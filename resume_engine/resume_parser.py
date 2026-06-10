"""
Resume Parser
-------------
Extracts structured data from a PDF resume:
- Skills (using the shared skill extractor)
- Education (degree + institution)
- Experience (years of work experience)
- Projects (project names/descriptions)
- Contact info

Usage:
    from resume_engine.resume_parser import parse_resume
    profile = parse_resume("path/to/resume.pdf")
"""

import re
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.skill_extractor import extract_skills, skills_by_category

try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False


# ── Text Extraction ───────────────────────────────────────────────────────────

def extract_text_from_pdf(path: str) -> str:
    if not PDF_SUPPORT:
        raise ImportError("pdfplumber not installed. Run: pip install pdfplumber")
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_text_from_string(text: str) -> str:
    """For when resume text is already extracted (e.g. from a web form)."""
    return text


# ── Section Detectors ─────────────────────────────────────────────────────────

EDUCATION_KEYWORDS = [
    "bachelor", "master", "phd", "ph.d", "b.s.", "m.s.", "b.a.", "m.a.",
    "degree", "university", "college", "institute", "school of",
    "computer science", "information technology", "engineering", "mathematics",
    "statistics", "data science", "mba", "associate"
]

DEGREE_PATTERNS = [
    r"(bachelor(?:'s)?(?:\s+of\s+[\w\s]+)?)",
    r"(master(?:'s)?(?:\s+of\s+[\w\s]+)?)",
    r"(ph\.?d\.?(?:\s+in\s+[\w\s]+)?)",
    r"(b\.?s\.?(?:\s+in\s+[\w\s]+)?)",
    r"(m\.?s\.?(?:\s+in\s+[\w\s]+)?)",
    r"(associate(?:'s)?(?:\s+of\s+[\w\s]+)?)",
    r"(mba)",
]

SCHOOL_PATTERNS = [
    r"((?:university|college|institute|school)\s+of\s+[\w\s]+)",
    r"([\w\s]+\s+university)",
    r"([\w\s]+\s+college)",
    r"([\w\s]+\s+institute(?:\s+of\s+technology)?)",
    r"(njit|mit|nyu|cuny|rutgers|columbia|cornell|stanford|harvard|princeton)",
]

def extract_education(text: str) -> dict:
    lower = text.lower()
    degree = None
    school = None

    for pattern in DEGREE_PATTERNS:
        m = re.search(pattern, lower)
        if m:
            degree = m.group(1).strip().title()
            break

    for pattern in SCHOOL_PATTERNS:
        m = re.search(pattern, lower)
        if m:
            school = m.group(1).strip().title()
            break

    # Try to find major
    major_match = re.search(
        r"(?:in|of)\s+(computer science|data science|information technology|"
        r"mathematics|statistics|electrical engineering|software engineering|"
        r"information systems|business administration|finance|economics)",
        lower
    )
    major = major_match.group(1).title() if major_match else None

    return {
        "degree": degree,
        "school": school,
        "major": major,
        "raw": _extract_education_section(text)
    }


def _extract_education_section(text: str) -> str:
    """Pull out the education section lines."""
    lines = text.split("\n")
    edu_lines = []
    in_section = False
    for line in lines:
        low = line.lower()
        if any(k in low for k in ["education", "academic"]):
            in_section = True
        elif in_section and any(k in low for k in
            ["experience", "skills", "projects", "certifications", "awards"]):
            break
        if in_section:
            edu_lines.append(line)
    return " ".join(edu_lines[:8])


def extract_experience_years(text: str) -> int:
    """Estimate years of experience from date ranges in resume."""
    # Look for year ranges like "2021 - 2023" or "2022 – Present"
    ranges = re.findall(r"(20\d{2})\s*[-–]\s*(20\d{2}|present|current)", text.lower())
    total = 0
    import datetime
    current_year = datetime.datetime.now().year
    for start, end in ranges:
        s = int(start)
        e = current_year if end in ("present", "current") else int(end)
        total += max(0, e - s)
    return min(total, 25)  # cap at 25 to avoid noise


def extract_contact(text: str) -> dict:
    email = None
    phone = None
    linkedin = None
    github = None

    email_m = re.search(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", text.lower())
    if email_m:
        email = email_m.group()

    phone_m = re.search(r"(\+?1?\s?)?(\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4})", text)
    if phone_m:
        phone = phone_m.group()

    linkedin_m = re.search(r"linkedin\.com/in/([\w-]+)", text.lower())
    if linkedin_m:
        linkedin = f"linkedin.com/in/{linkedin_m.group(1)}"

    github_m = re.search(r"github\.com/([\w-]+)", text.lower())
    if github_m:
        github = f"github.com/{github_m.group(1)}"

    return {"email": email, "phone": phone, "linkedin": linkedin, "github": github}


def extract_name(text: str) -> str | None:
    """Try to extract name from first 2 lines."""
    lines = [l.strip() for l in text.split("\n") if l.strip()][:3]
    for line in lines:
        # Name is typically all caps or Title Case, short, no numbers
        if re.match(r"^[A-Za-z\s\-\.]{3,40}$", line) and len(line.split()) <= 4:
            return line.title()
    return None


# ── Main Parse Function ───────────────────────────────────────────────────────

def parse_resume(source, is_text: bool = False) -> dict:
    """
    Parse a resume from a PDF file path or raw text.

    Args:
        source: file path (str) or raw text string
        is_text: if True, treat source as raw text instead of file path

    Returns:
        dict with keys: name, contact, skills, skills_by_category,
                        education, experience_years, raw_text
    """
    if is_text:
        raw_text = source
    else:
        raw_text = extract_text_from_pdf(source)

    skills = extract_skills(raw_text)
    grouped = skills_by_category(raw_text)

    return {
        "name": extract_name(raw_text),
        "contact": extract_contact(raw_text),
        "skills": [s["skill"] for s in skills],
        "skills_by_category": grouped,
        "skill_count": len(skills),
        "education": extract_education(raw_text),
        "experience_years": extract_experience_years(raw_text),
        "raw_text": raw_text,
    }


# ── Test ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample_resume = """
    Alex Johnson
    alex.johnson@email.com | (555) 123-4567 | linkedin.com/in/alexjohnson | github.com/alexj

    EDUCATION
    Bachelor's in Computer Science
    New Jersey Institute of Technology (NJIT), 2021 - 2024

    EXPERIENCE
    Data Analyst Intern — TechCorp, 2023 - 2024
    - Built dashboards using Power BI and Tableau
    - Wrote complex SQL queries for reporting
    - Analyzed marketing data using Python and pandas

    Junior Developer — StartupXYZ, 2022 - 2023
    - Developed REST APIs using Python/FastAPI
    - Maintained PostgreSQL database

    SKILLS
    Python, Java, SQL, Excel, Git, Tableau, Power BI, Machine Learning basics

    PROJECTS
    - Stock Price Predictor: Built a machine learning model using scikit-learn
    - Sales Dashboard: Created interactive Tableau visualizations
    """

    import json
    profile = parse_resume(sample_resume, is_text=True)
    print(json.dumps({k: v for k, v in profile.items() if k != "raw_text"}, indent=2))
