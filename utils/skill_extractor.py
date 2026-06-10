"""
Skill Extractor — CareerIQ
---------------------------
Extracts skills from text using exact + alias + multi-word matching.
Works on both job descriptions AND resumes.

IMPORTANT distinction:
  - On a RESUME, a word like "communication" is a deliberately listed skill.
  - In a JOB DESCRIPTION, words like "communication", "research", "organization"
    are just ordinary prose and don't signal a real required skill.

So when extracting from job postings we pass exclude_generic=True to skip a
set of weak/ambiguous terms. This keeps computed weights focused on real,
distinguishing skills (Python, SQL, Docker) instead of filler.
"""

import re
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.skills_taxonomy import SKILL_LOOKUP, CATEGORY_LOOKUP

# Generic terms that are real skills on a resume but noise in a job description.
# These are common English words or vague descriptors that appear in nearly
# every posting regardless of role, so they don't help distinguish careers.
GENERIC_IN_JOB_POSTINGS = {
    "communication", "teamwork", "leadership", "problem solving",
    "critical thinking", "time management", "organization", "adaptability",
    "creativity", "collaboration", "attention to detail", "public speaking",
    "writing", "research", "training", "assessment", "strategy",
    "presentation", "documentation", "reporting", "planning",
    "consulting", "testing", "communication protocols", "design systems",
    "architecture", "security", "analytics", "marketing", "operations management",
    "storytelling", "automation", "optimization", "scriptwriting",
    "content optimization", "youtube optimization", "process improvement",
    "compliance", "construction", "manufacturing", "logistics",
    "monitoring", "regulatory compliance", "report writing",
    "classification", "remediation", "industry expertise",
}


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s\+\#\/\-\.]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_skills(text: str, exclude_generic: bool = False) -> list:
    """
    Extract all recognized skills from a block of text.

    Args:
        text: the text to scan
        exclude_generic: if True, skip generic filler terms (use this for
                         job-description parsing; leave False for resumes)

    Returns:
        List of dicts: [{"skill": "python", "category": "programming"}, ...]
    """
    if not text:
        return []

    normalized_text = normalize(text)
    found = {}

    # Sort by length descending so multi-word skills match first
    sorted_skills = sorted(SKILL_LOOKUP.keys(), key=len, reverse=True)

    for skill_phrase in sorted_skills:
        pattern = r"(?<!\w)" + re.escape(skill_phrase) + r"(?!\w)"
        if re.search(pattern, normalized_text):
            canonical = SKILL_LOOKUP[skill_phrase]
            if exclude_generic and canonical in GENERIC_IN_JOB_POSTINGS:
                continue
            if canonical not in found:
                category = CATEGORY_LOOKUP.get(canonical, "other")
                found[canonical] = {"skill": canonical, "category": category}

    return list(found.values())


def extract_skill_names(text: str, exclude_generic: bool = False) -> list:
    """Convenience: just return a list of skill name strings."""
    return [s["skill"] for s in extract_skills(text, exclude_generic=exclude_generic)]


def skills_by_category(text: str, exclude_generic: bool = False) -> dict:
    """
    Extract skills and group them by their taxonomy category.
    Returns: {category_name: [skill, skill, ...], ...}
    """
    skills = extract_skills(text, exclude_generic=exclude_generic)
    grouped = {}
    for s in skills:
        grouped.setdefault(s["category"], []).append(s["skill"])
    return grouped
