"""
collect_jobs.py
---------------
Runs both scrapers (USAJobs + Adzuna) and stores everything in PostgreSQL.

Usage:
    python collect_jobs.py               # default: 4 pages each (~2,000 jobs)
    python collect_jobs.py --pages 20    # ~10,000 jobs
    python collect_jobs.py --source usajobs   # only USAJobs
    python collect_jobs.py --source adzuna    # only Adzuna
"""

import argparse, sys, os
sys.path.append(os.path.dirname(__file__))

from data_collection.job_storage import save_jobs, get_job_count

parser = argparse.ArgumentParser()
parser.add_argument("--pages",  type=int, default=4)
parser.add_argument("--source", type=str, default="both", choices=["both","usajobs","adzuna"])
args = parser.parse_args()

print("=" * 55)
print("  CareerIQ — Job Data Collector")
print("=" * 55)
print(f"\nJobs in DB before run: {get_job_count()}")

all_jobs = []

if args.source in ("both", "usajobs"):
    print(f"\n📡 USAJobs (government sector) — {args.pages} pages per keyword")
    from data_collection.usajobs_scraper import scrape as scrape_usa
    all_jobs += scrape_usa(max_pages=args.pages)

if args.source in ("both", "adzuna"):
    print(f"\n📡 Adzuna (private sector) — {args.pages} pages per keyword")
    from data_collection.adzuna_scraper import scrape as scrape_adzuna
    all_jobs += scrape_adzuna(max_pages=args.pages)

if not all_jobs:
    print("\n⚠️  No jobs scraped. Check your API keys in .env")
    sys.exit(1)

print(f"\n💾 Saving {len(all_jobs)} jobs to database...")
result = save_jobs(all_jobs)

print(f"\nJobs in DB after run: {get_job_count()}")
print("\n✅ Done! Run `python compute_weights.py` to update career match scores.")
