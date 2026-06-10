"""
compute_weights.py
------------------
Reads your job database and computes REAL skill weights per career path
based on actual job posting frequencies.

Replaces the hand-crafted weights in career_paths.py with data-derived ones.

Run this after collect_jobs.py has populated your database:
    python compute_weights.py

Output:
    - Prints a report of computed weights
    - Writes computed_weights.json (used by the matching engine)
    - Shows which skills appear most in each career
"""

import json, sys, os, re
sys.path.append(os.path.dirname(__file__))

from database.db import get_connection

# Title→career matching uses the SAME shared list the scrapers use,
# so search keywords and weight-computation can never drift apart.
from data_collection.career_keywords import get_career_for_title

def compute_weights() -> dict:
    """
    For each career path:
    1. Find all jobs in the DB with matching titles
    2. Count how often each skill appears across those jobs
    3. Convert to frequency (skill_count / total_jobs)
    4. Assign weight tier: required (>60%), important (30-60%), nice (<30%)
    """
    print("📊 Computing real skill weights from job database...\n")

    conn = get_connection()
    try:
        cur = conn.cursor()
        # Get all jobs with their skills
        cur.execute("""
            SELECT j.title, s.name as skill
            FROM jobs j
            JOIN job_skills js ON js.job_id = j.id
            JOIN skills s ON s.id = js.skill_id
            WHERE j.title IS NOT NULL
        """)
        rows = cur.fetchall()

        # Get total jobs per career (for denominator)
        cur.execute("SELECT title FROM jobs WHERE title IS NOT NULL")
        all_titles = [r["title"] for r in cur.fetchall()]
    finally:
        conn.close()

    if not rows:
        print("❌ No data found. Run collect_jobs.py first to populate the database.")
        return {}

    # Group by career
    career_skill_counts = {}   # career -> {skill: count}
    career_job_counts = {}     # career -> total jobs

    # Count jobs per career
    for title in all_titles:
        career = get_career_for_title(title)
        if career:
            career_job_counts[career] = career_job_counts.get(career, 0) + 1

    # Count skill occurrences per career
    for row in rows:
        career = get_career_for_title(row["title"])
        if not career:
            continue
        if career not in career_skill_counts:
            career_skill_counts[career] = {}
        skill = row["skill"]
        career_skill_counts[career][skill] = career_skill_counts[career].get(skill, 0) + 1

    # Compute frequencies and assign tiers
    computed = {}
    for career, skill_counts in career_skill_counts.items():
        total_jobs = career_job_counts.get(career, 1)
        print(f"  📁 {career}: {total_jobs} jobs found")

        skills_with_freq = []
        for skill, count in skill_counts.items():
            freq = count / total_jobs
            skills_with_freq.append((skill, freq, count))

        skills_with_freq.sort(key=lambda x: x[1], reverse=True)

        # RANK-BASED tiering (not threshold-based).
        # Real job descriptions are sparse and inconsistent — many postings are
        # vague marketing blurbs with no real skills listed. So we use a low flat
        # floor: a skill that appears in at least 3 postings is a real signal,
        # even if most postings for that career are uninformative.
        min_count = 3
        ranked = [(s, f, c) for s, f, c in skills_with_freq if c >= min_count]

        required     = [s for s, _, _ in ranked[:5]]
        important    = [s for s, _, _ in ranked[5:12]]
        nice_to_have = [s for s, _, _ in ranked[12:20]]

        # Print top skills
        print(f"     Top skills: {', '.join(s for s,_,_ in ranked[:6])}")
        print(f"     Required: {required}")
        print(f"     Important: {important[:5]}")
        print()

        computed[career] = {
            "required":     required,
            "important":    important,
            "nice_to_have": nice_to_have,
            "total_jobs_analyzed": total_jobs,
            "skill_frequencies": {s: round(f, 3) for s, f, _ in skills_with_freq},
        }

    return computed


def save_weights(weights: dict):
    path = os.path.join(os.path.dirname(__file__), "matching_engine", "computed_weights.json")
    with open(path, "w") as f:
        json.dump(weights, f, indent=2)
    print(f"✅ Weights saved to {path}")
    print("   The matching engine will automatically use these on next run.")


def print_summary(weights: dict):
    print("\n" + "="*55)
    print("  COMPUTED WEIGHTS SUMMARY")
    print("="*55)
    for career, data in weights.items():
        jobs = data["total_jobs_analyzed"]
        req  = len(data["required"])
        imp  = len(data["important"])
        print(f"\n  {career} ({jobs} jobs)")
        print(f"    Required ({req}):  {', '.join(data['required'][:4])}")
        print(f"    Important ({imp}): {', '.join(data['important'][:4])}")


if __name__ == "__main__":
    weights = compute_weights()
    if weights:
        save_weights(weights)
        print_summary(weights)
        print("\n✅ Done! Your career match scores are now data-driven.")
    else:
        print("\n⚠️  Could not compute weights. Make sure you have job data in the DB.")
        print("   Run: python collect_jobs.py --pages 20")
