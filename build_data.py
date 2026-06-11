"""
build_data.py — CareerIQ (Plan 2: static site)
------------------------------------------------
This is the script that REPLACES a live backend server.

Instead of running FastAPI on Render answering requests, you run this
ONCE on your laptop. It bundles everything the dashboard needs —
career definitions, real computed weights (where available), and the
skills taxonomy — into a single file: dashboard/data.json

Then you push that file to GitHub and the site is live. No server.

Run it like this:
    python build_data.py

What it produces:
    dashboard/data.json   <- the dashboard reads this directly in the browser

Every career is tagged with "data_driven": true/false so the dashboard
can show the honesty badge ("Based on N live job postings" vs
"Curated estimate"). Tech/data careers become data-driven once you've
run collect_jobs.py + compute_weights.py; everything else stays an
honest curated estimate until more data sources are added.
"""

import json
import os
import sys
from datetime import datetime, timezone

sys.path.append(os.path.dirname(__file__))

from matching_engine.career_paths import CAREER_PATHS
from utils.skills_taxonomy import SKILLS_TAXONOMY, SKILL_LOOKUP, CATEGORY_LOOKUP

HERE = os.path.dirname(__file__)
COMPUTED_PATH = os.path.join(HERE, "matching_engine", "computed_weights.json")
OUTPUT_PATH = os.path.join(HERE, "dashboard", "data.json")


def load_computed_weights() -> dict:
    """Load data-derived weights if compute_weights.py has been run."""
    if os.path.exists(COMPUTED_PATH):
        try:
            with open(COMPUTED_PATH, encoding="utf-8") as f:
                data = json.load(f)
            print(f"  Found computed weights for {len(data)} career(s) — these will be tagged 'live data'.")
            return data
        except (json.JSONDecodeError, OSError) as e:
            print(f"  Could not read computed_weights.json ({e}); treating all careers as estimates.")
    else:
        print("  No computed_weights.json yet — every career will be a 'curated estimate'.")
        print("  (Run collect_jobs.py then compute_weights.py to make tech careers data-driven.)")
    return {}


def build_careers(computed: dict) -> list:
    """
    Merge hand-crafted definitions with computed weights.
    For any career that has computed data, use the real weights and
    mark it data_driven=True. Otherwise keep the curated estimate.
    """
    careers = []
    for name, base in CAREER_PATHS.items():
        entry = {
            "name": name,
            "industry": base.get("industry", "Other"),
            "description": base["description"],
            "avg_salary": base["avg_salary"],
            "growth": base["growth"],
            "required": base["required"],
            "important": base["important"],
            "nice_to_have": base["nice_to_have"],
            "data_driven": False,
            "jobs_analyzed": 0,
        }

        if name in computed:
            c = computed[name]
            # Only override if the computed data actually has skills
            if c.get("required") or c.get("important"):
                entry["required"] = c["required"]
                entry["important"] = c["important"]
                entry["nice_to_have"] = c["nice_to_have"]
                entry["data_driven"] = True
                entry["jobs_analyzed"] = c.get("total_jobs_analyzed", 0)
                entry["skill_frequencies"] = c.get("skill_frequencies", {})

        careers.append(entry)

    return careers


def build_data() -> dict:
    print("Building static data file for the dashboard...\n")
    computed = load_computed_weights()
    careers = build_careers(computed)

    # Attach recent real job listings per career (the "Recent Openings" feature).
    # Reads from the DB if it exists; degrades gracefully to none if not.
    jobs_by_career = {}
    try:
        from data_collection.job_storage import get_recent_jobs_by_career
        jobs_by_career = get_recent_jobs_by_career(limit_per_career=25)
        total_listed = sum(len(v) for v in jobs_by_career.values())
        print(f"  Attached {total_listed} recent job listings across {len(jobs_by_career)} careers.")
    except Exception as e:
        print(f"  No job listings attached ({e}). Careers will show an empty openings state.")

    for c in careers:
        listings = jobs_by_career.get(c["name"], [])
        # posted_at may be a datetime/date/string; store as ISO date string or None
        clean = []
        for j in listings:
            pa = j.get("posted_at")
            if hasattr(pa, "isoformat"):
                pa = pa.isoformat()[:10]
            elif isinstance(pa, str) and pa:
                pa = pa[:10]
            else:
                pa = None
            clean.append({**j, "posted_at": pa})
        c["recent_jobs"] = clean

    data_driven_count = sum(1 for c in careers if c["data_driven"])
    total_jobs = sum(c["jobs_analyzed"] for c in careers)

    # The dashboard needs the skill vocabulary to parse resumes in-browser.
    # SKILL_LOOKUP maps every term + alias -> canonical name.
    # CATEGORY_LOOKUP maps canonical name -> category.
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stats": {
            "total_careers": len(careers),
            "data_driven_careers": data_driven_count,
            "estimate_careers": len(careers) - data_driven_count,
            "total_jobs_analyzed": total_jobs,
            "total_skills": len(set(SKILL_LOOKUP.values())),
            "industries": sorted({c["industry"] for c in careers}),
        },
        "careers": careers,
        "skill_lookup": SKILL_LOOKUP,
        "category_lookup": CATEGORY_LOOKUP,
        "taxonomy": SKILLS_TAXONOMY,
    }
    return payload


def main():
    payload = build_data()

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    s = payload["stats"]
    size_kb = os.path.getsize(OUTPUT_PATH) / 1024

    print()
    print("=" * 55)
    print("  DATA FILE BUILT")
    print("=" * 55)
    print(f"  Output:            dashboard/data.json  ({size_kb:.0f} KB)")
    print(f"  Total careers:     {s['total_careers']}  across {len(s['industries'])} industries")
    print(f"  Live data:         {s['data_driven_careers']} careers ({s['total_jobs_analyzed']} job postings analyzed)")
    print(f"  Curated estimates: {s['estimate_careers']} careers")
    print(f"  Skills recognized: {s['total_skills']}")
    print()
    if s["data_driven_careers"] == 0:
        print("  Note: 0 careers are data-driven yet. That's expected before you")
        print("  run the scrapers. The site will work — every career just shows")
        print("  the 'curated estimate' badge. Run collect_jobs.py + compute_weights.py")
        print("  then re-run this script to light up the tech careers with real data.")
    else:
        print("  Next: push dashboard/data.json to GitHub and your site is live.")
    print()


if __name__ == "__main__":
    main()
