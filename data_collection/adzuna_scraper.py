"""
Adzuna Scraper
--------------
Pulls private sector job postings from Adzuna API.
Covers: Google, Meta, startups, finance, consulting, etc.
Complements USAJobs which is government-only.

Docs: https://developer.adzuna.com/docs/search
"""

import os, time, requests
from datetime import datetime
from dotenv import load_dotenv
from data_collection.career_keywords import search_terms

load_dotenv()

APP_ID  = os.getenv("ADZUNA_APP_ID", "")
APP_KEY = os.getenv("ADZUNA_APP_KEY", "")
BASE_URL = "https://api.adzuna.com/v1/api/jobs/us/search"

# All career search terms (tech + non-tech), from the shared source of truth.
TARGET_KEYWORDS = search_terms()

def fetch_page(keyword: str, page: int = 1, per_page: int = 50) -> list:
    url = f"{BASE_URL}/{page}"
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "what": keyword,
        "results_per_page": per_page,
        "content-type": "application/json",
        "sort_by": "date",
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json().get("results", [])

def parse_job(item: dict) -> dict:
    # Extract salary
    sal_min = item.get("salary_min")
    sal_max = item.get("salary_max")

    # Parse date
    created = item.get("created", "")
    try:
        posted_at = datetime.fromisoformat(created[:10]) if created else None
    except:
        posted_at = None

    # Company name
    company = item.get("company", {}).get("display_name", "") if isinstance(item.get("company"), dict) else ""

    # Location
    loc = item.get("location", {})
    location = loc.get("display_name", "") if isinstance(loc, dict) else ""

    return {
        "external_id": f"adzuna_{item.get('id', '')}",
        "title": item.get("title", ""),
        "company": company,
        "location": location,
        "salary_min": int(sal_min) if sal_min else None,
        "salary_max": int(sal_max) if sal_max else None,
        "description": item.get("description", ""),
        "url": item.get("redirect_url", ""),
        "posted_at": posted_at,
        "source": "adzuna",
    }

def scrape(max_pages: int = 4) -> list:
    all_jobs, seen = [], set()

    for kw in TARGET_KEYWORDS:
        print(f"  🔍 '{kw}'", end="", flush=True)
        for page in range(1, max_pages + 1):
            try:
                items = fetch_page(kw, page)
                if not items:
                    break

                new = []
                for item in items:
                    job = parse_job(item)
                    if job["external_id"] not in seen and job["title"]:
                        seen.add(job["external_id"])
                        new.append(job)

                all_jobs.extend(new)
                print(f" {len(all_jobs)}", end="", flush=True)
                time.sleep(0.3)

            except requests.HTTPError as e:
                print(f" [HTTP {e.response.status_code}]", end="")
                break
            except Exception as e:
                print(f" [err: {e}]", end="")
                break
        print()

    print(f"✅ Adzuna scrape complete. Total unique jobs: {len(all_jobs)}")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape(max_pages=2)
    if jobs:
        import json
        print("\nSample job:")
        j = jobs[0].copy()
        j["description"] = j["description"][:200] + "..."
        print(json.dumps(j, indent=2, default=str))
