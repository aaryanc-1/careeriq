"""
Level Detection — CareerIQ
----------------------------
Infers a seniority level from job-posting text OR resume text.

Four levels: "internship", "entry", "mid", "senior".

This is INFERENCE from keywords, not a labeled field — postings rarely
state their level explicitly. It's roughly right most of the time, which
is plenty for a filter, but it is intentionally honest: the UI labels
job levels as "estimated".

detect_job_level(title, description) -> one of the 4 levels
detect_resume_level(resume_text)    -> one of the 4 levels
"""

import re

# Signals are checked in priority order. Most specific / highest-confidence first.
# Each entry: (level, [keywords]). We check senior and internship before entry/mid
# because those have the clearest, least-ambiguous signals.

SENIOR_SIGNALS = [
    "senior", "sr.", "sr ", "lead ", "principal", "staff ", "director",
    "head of", "vp ", "vice president", "manager", "architect",
    "iii", "iv", " v ", "10+ years", "8+ years", "7+ years",
    "6+ years", "5+ years", "expert", "chief",
]

INTERNSHIP_SIGNALS = [
    "intern", "internship", "co-op", "coop", "co op", "trainee",
    "apprentice", "summer analyst", "work study", "practicum",
]

ENTRY_SIGNALS = [
    "entry level", "entry-level", "junior", "jr.", "jr ", "associate",
    "graduate", "grad ", "new grad", "early career", "level i", " i ",
    "0-2 years", "0-1 years", "1-2 years", "no experience", "trainee",
    "assistant",
]

MID_SIGNALS = [
    "mid level", "mid-level", "intermediate", "level ii", " ii ",
    "3-5 years", "2-4 years", "3+ years", "4+ years", "2+ years",
]


def _contains_any(text: str, signals) -> bool:
    return any(s in text for s in signals)


def detect_job_level(title: str, description: str = "") -> str:
    """
    Infer a job's seniority level. Title is weighted most heavily
    (it's the clearest signal); description is a fallback.
    """
    t = f" {(title or '').lower()} "
    d = (description or "").lower()

    # 1) Internship is the most distinct signal — check first, title or desc.
    if _contains_any(t, INTERNSHIP_SIGNALS) or _contains_any(d, INTERNSHIP_SIGNALS):
        return "internship"

    # 2) Senior signals in the TITLE are high-confidence.
    if _contains_any(t, SENIOR_SIGNALS):
        return "senior"

    # 3) Entry signals in the title.
    if _contains_any(t, ENTRY_SIGNALS):
        return "entry"

    # 4) Mid signals in the title.
    if _contains_any(t, MID_SIGNALS):
        return "mid"

    # 5) Fall back to description-based experience hints.
    if _contains_any(d, SENIOR_SIGNALS):
        return "senior"
    if _contains_any(d, ENTRY_SIGNALS):
        return "entry"
    if _contains_any(d, MID_SIGNALS):
        return "mid"

    # 6) No clear signal → default to "mid" (the safest neutral bucket,
    #    since most untitled-level professional postings sit here).
    return "mid"


def detect_resume_level(resume_text: str) -> str:
    """
    Infer the candidate's own level from their resume.

    Heuristics, in order:
    - Mentions of being a student / current studies / expected grad → internship/entry
    - Years of experience stated → map to a level
    - Senior/leadership titles held → senior
    - Otherwise default to entry (safest for an early-career audience)
    """
    if not resume_text:
        return "entry"
    text = resume_text.lower()

    # Strong student / new-grad signals → internship-seeking
    student_signals = [
        "student", "currently pursuing", "currently studying", "expected graduation",
        "expected grad", "candidate for", "b.s. expected", "anticipated graduation",
        "sophomore", "freshman", "junior year", "senior year", "undergraduate",
        "pursuing a bachelor", "pursuing a master", "class of 20",
    ]
    if _contains_any(text, student_signals):
        return "internship"

    # Senior/leadership signals → senior
    senior_self = [
        "senior ", "lead ", "principal ", "manager", "director", "head of",
        "vp of", "vice president", "10+ years", "12 years", "15 years",
        "managed a team", "led a team", "team of", "p&l",
    ]
    if _contains_any(text, senior_self):
        return "senior"

    # Try to find an explicit "N years of experience"
    m = re.search(r"(\d{1,2})\+?\s*years?(?:\s+of)?\s+(?:experience|exp)", text)
    if m:
        years = int(m.group(1))
        if years <= 1:
            return "entry"
        if years <= 4:
            return "mid"
        return "senior"

    # Internship-only history → still entry/intern level
    if "intern" in text and "full-time" not in text:
        return "internship"

    # Default for an early-career-leaning tool
    return "entry"


# Human-friendly labels for the UI
LEVEL_LABELS = {
    "internship": "Internship",
    "entry": "Entry-Level",
    "mid": "Mid-Level",
    "senior": "Senior+",
}
LEVEL_ORDER = ["internship", "entry", "mid", "senior"]
