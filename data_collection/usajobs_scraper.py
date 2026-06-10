"""
USAJobs Scraper
---------------
Pulls real job postings from the official USAJobs.gov public API.

Free API key: https://developer.usajobs.gov/apirequest/
Set in .env:
    USAJOBS_API_KEY=your_key
    USAJOBS_EMAIL=your_email@example.com
"""

import os, time, requests
from datetime import datetime
from dotenv import load_dotenv
from data_collection.career_keywords import search_terms

load_dotenv()

BASE_URL = "https://data.usajobs.gov/api/search"
HEADERS = {
    "Host": "data.usajobs.gov",
    "User-Agent": os.getenv("USAJOBS_EMAIL", "user@example.com"),
    "Authorization-Key": os.getenv("USAJOBS_API_KEY", ""),
}

# All career search terms (tech + non-tech), from the shared source of truth.
TARGET_KEYWORDS = search_terms()

def fetch_page(keyword: str, page: int = 1, per_page: int = 25) -> list:
    params = {"Keyword": keyword, "ResultsPerPage": per_page, "Page": page,
              "SortField": "OpenDate", "SortDirection": "Desc"}
    r = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json().get("SearchResult", {}).get("SearchResultItems", [])

def parse_job(item: dict) -> dict:
    d = item.get("MatchedObjectDescriptor", {})
    sal = d.get("PositionRemuneration", [{}])[0]
    def to_int(v):
        try: return int(float(v))
        except: return None
    def to_date(v):
        try: return datetime.fromisoformat(v[:10]) if v else None
        except: return None
    return {
        "external_id": d.get("PositionID", ""),
        "title": d.get("PositionTitle", ""),
        "company": d.get("OrganizationName", ""),
        "location": d.get("PositionLocationDisplay", ""),
        "salary_min": to_int(sal.get("MinimumRange")),
        "salary_max": to_int(sal.get("MaximumRange")),
        "description": d.get("QualificationSummary", ""),
        "url": d.get("PositionURI", ""),
        "posted_at": to_date(d.get("PublicationStartDate")),
        "source": "usajobs",
    }

def scrape(max_pages: int = 4) -> list:
    all_jobs, seen = [], set()
    for kw in TARGET_KEYWORDS:
        print(f"  🔍 '{kw}'", end="", flush=True)
        for page in range(1, max_pages + 1):
            try:
                items = fetch_page(kw, page)
                if not items: break
                new = [parse_job(i) for i in items
                       if parse_job(i)["external_id"] not in seen]
                for j in new: seen.add(j["external_id"])
                all_jobs.extend(new)
                print(f" {len(all_jobs)}", end="", flush=True)
                time.sleep(0.4)
            except Exception as e:
                print(f" [err: {e}]", end="")
                break
        print()
    print(f"✅ Scraped {len(all_jobs)} unique jobs.")
    return all_jobs
