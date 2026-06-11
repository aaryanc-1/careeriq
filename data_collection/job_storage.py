"""
Job Storage — CareerIQ (SQLite version)
----------------------------------------
Saves scraped jobs to the SQLite database (database/careeriq.db).
Auto-extracts skills from each job description on insert.
"""

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from database.db import get_connection
from utils.skill_extractor import extract_skills


def upsert_company(cur, name: str) -> int:
    # Insert the company if new; either way return its id.
    cur.execute("INSERT OR IGNORE INTO companies (name) VALUES (?)", (name,))
    cur.execute("SELECT id FROM companies WHERE name = ?", (name,))
    return cur.fetchone()["id"]


def upsert_skill(cur, skill: str, category: str) -> int:
    cur.execute("INSERT OR IGNORE INTO skills (name, category) VALUES (?, ?)", (skill, category))
    cur.execute("SELECT id FROM skills WHERE name = ?", (skill,))
    return cur.fetchone()["id"]


def insert_job(cur, job: dict):
    """Insert a job. Returns the new job id, or None if it already existed."""
    company_id = upsert_company(cur, job["company"]) if job.get("company") else None
    cur.execute("""
        INSERT OR IGNORE INTO jobs
            (external_id, title, company_id, location, salary_min, salary_max,
             description, url, posted_at, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        job.get("external_id"), job.get("title"), company_id, job.get("location"),
        job.get("salary_min"), job.get("salary_max"), job.get("description"),
        job.get("url"), job.get("posted_at"), job.get("source"),
    ))
    if cur.rowcount == 0:
        return None                      # was a duplicate, INSERT OR IGNORE skipped it
    return cur.lastrowid


def link_skills_to_job(cur, job_id: int, text: str):
    # exclude_generic=True: job postings are full of prose like "communication"
    # and "research" that aren't real distinguishing skills — skip them here.
    skills = extract_skills(text or "", exclude_generic=True)
    for s in skills:
        skill_id = upsert_skill(cur, s["skill"], s["category"])
        cur.execute(
            "INSERT OR IGNORE INTO job_skills (job_id, skill_id) VALUES (?, ?)",
            (job_id, skill_id)
        )


def save_jobs(jobs: list) -> dict:
    inserted = skipped = 0
    conn = get_connection()
    try:
        cur = conn.cursor()
        for job in jobs:
            job_id = insert_job(cur, job)
            if job_id:
                link_skills_to_job(cur, job_id, job.get("description", ""))
                inserted += 1
            else:
                skipped += 1
        conn.commit()
    finally:
        conn.close()
    print(f"  Inserted {inserted} new jobs, skipped {skipped} duplicates.")
    return {"inserted": inserted, "skipped": skipped}


def get_job_count() -> int:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS c FROM jobs")
        return cur.fetchone()["c"]
    finally:
        conn.close()


def get_recent_jobs_by_career(limit_per_career: int = 25) -> dict:
    """
    Read jobs from the DB and group them under careers using the SAME
    specific-first title matching the rest of the pipeline uses (so a job
    lands in the right career — this also addresses the mis-filing issue).

    Returns: { career_name: [ {title, company, location, salary_min,
               salary_max, url, posted_at}, ... ] }
    Jobs are newest-first; capped at limit_per_career each.
    """
    # Import here to avoid a circular import at module load time.
    from data_collection.career_keywords import get_career_for_title

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT j.title, c.name AS company, j.location,
                   j.salary_min, j.salary_max, j.url, j.posted_at
            FROM jobs j
            LEFT JOIN companies c ON c.id = j.company_id
            WHERE j.title IS NOT NULL
            ORDER BY j.posted_at DESC
        """)
        rows = cur.fetchall()
    finally:
        conn.close()

    grouped = {}
    for r in rows:
        career = get_career_for_title(r["title"])
        if not career:
            continue
        bucket = grouped.setdefault(career, [])
        if len(bucket) >= limit_per_career:
            continue
        bucket.append({
            "title": r["title"],
            "company": r["company"] or "",
            "location": r["location"] or "",
            "salary_min": r["salary_min"],
            "salary_max": r["salary_max"],
            "url": r["url"] or "",
            "posted_at": r["posted_at"],
        })
    return grouped
