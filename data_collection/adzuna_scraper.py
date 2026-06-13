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
from data_collection.countries import COUNTRIES, meta

load_dotenv()

APP_ID  = os.getenv("ADZUNA_APP_ID", "")
APP_KEY = os.getenv("ADZUNA_APP_KEY", "")
BASE = "https://api.adzuna.com/v1/api/jobs"  # /{country}/search/{page}

# All career search terms (tech + non-tech), from the shared source of truth.
TARGET_KEYWORDS = search_terms()

def fetch_page(country: str, keyword: str, page: int = 1, per_page: int = 50) -> list:
    url = f"{BASE}/{country}/search/{page}"
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

def parse_job(item: dict, country_code: str) -> dict:
    sal_min = item.get("salary_min")
    sal_max = item.get("salary_max")

    created = item.get("created", "")
    try:
        posted_at = datetime.fromisoformat(created[:10]) if created else None
    except:
        posted_at = None

    company = item.get("company", {}).get("display_name", "") if isinstance(item.get("company"), dict) else ""
    loc = item.get("location", {})
    location = loc.get("display_name", "") if isinstance(loc, dict) else ""

    cm = meta(country_code)
    return {
        "external_id": f"adzuna_{country_code}_{item.get('id', '')}",
        "title": item.get("title", ""),
        "company": company,
        "location": location,
        "salary_min": int(sal_min) if sal_min else None,
        "salary_max": int(sal_max) if sal_max else None,
        "description": item.get("description", ""),
        "url": item.get("redirect_url", ""),
        "posted_at": posted_at,
        "source": "adzuna",
        "country": country_code,
        "currency": cm["currency"],
        "currency_symbol": cm["symbol"],
    }

def scrape(max_pages: int = 2) -> list:
    all_jobs, seen = [], set()

    for country in COUNTRIES:
        cc = country["code"]
        print(f"\n🌍 {country['flag']} {country['name']} ({cc})")
        for kw in TARGET_KEYWORDS:
            for page in range(1, max_pages + 1):
                try:
                    items = fetch_page(cc, kw, page)
                    if not items:
                        break
                    new = []
                    for item in items:
                        job = parse_job(item, cc)
                        if job["external_id"] not in seen and job["title"]:
                            seen.add(job["external_id"])
                            new.append(job)
                    all_jobs.extend(new)
                    time.sleep(0.3)
                except requests.HTTPError as e:
                    print(f"  [{kw}: HTTP {e.response.status_code}]", end="")
                    break
                except Exception as e:
                    print(f"  [{kw}: err {e}]", end="")
                    break
        print(f"  → running total: {len(all_jobs)}")

    print(f"\n✅ Adzuna multi-country scrape complete. Total unique jobs: {len(all_jobs)}")
    return all_jobs


if __name__ == "__main__":
    jobs = scrape(max_pages=1)
    if jobs:
        import json
        print("\nSample job:")
        j = jobs[0].copy()
        j["description"] = j["description"][:150] + "..."
        print(json.dumps(j, indent=2, default=str))
