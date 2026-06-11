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


def _has_word(text: str, signals) -> bool:
    """
    True if any signal appears as a WHOLE word/phrase in text.
    This prevents 'intern' from matching inside 'internal'/'international',
    or 'lead' inside 'leader/leading' when we don't want it to.
    """
    for s in signals:
        s = s.strip()
        if not s:
            continue
        # \b = word boundary. Escape the signal so '+' etc. are literal.
        if re.search(r"\b" + re.escape(s) + r"\b", text):
            return True
    return False


def _max_years(text: str) -> int:
    """Largest 'N years' figure mentioned, or 0 if none."""
    yrs = [int(n) for n in re.findall(r"(\d{1,2})\+?\s*years?", text)]
    return max(yrs) if yrs else 0


def _max_salary(salary_min, salary_max) -> float:
    vals = [v for v in (salary_min, salary_max) if v]
    return max(vals) if vals else 0


def detect_job_level(title: str, description: str = "",
                     salary_min=None, salary_max=None) -> str:
    """
    Infer a job's seniority level — TITLE-FIRST with contextual guards.

    Order of confidence:
      1. Title keywords (highest confidence)
      2. Contextual guards (salary, years-of-experience) to veto bad guesses
      3. Description keywords (only as a weak fallback, whole-word)
    """
    t = (title or "").lower()
    d = (description or "").lower()
    years = _max_years(t + " " + d)
    top_salary = _max_salary(salary_min, salary_max)

    title_has = lambda sig: _has_word(t, sig)

    # ── Guards: things that strongly mean "NOT an internship/entry" ──
    senior_title_words = ["developer", "engineer", "manager", "director",
                          "lead", "principal", "senior", "architect", "head"]
    looks_professional = (
        top_salary >= 80000 or years >= 3 or _has_word(t, senior_title_words)
    )

    # 1) INTERNSHIP — only trust the TITLE (whole word), and never if it
    #    clearly looks like a professional role by salary/experience/title.
    intern_title = ["intern", "internship", "co-op", "coop", "trainee",
                    "apprentice", "summer analyst", "practicum"]
    if title_has(intern_title) and not looks_professional:
        return "internship"

    # 2) SENIOR — strong title signals, or high experience/salary.
    senior_sig = ["senior", "sr", "lead", "principal", "staff", "director",
                  "head", "vp", "vice president", "manager", "architect",
                  "chief", "iii", "iv", "expert"]
    if title_has(senior_sig) or years >= 6 or top_salary >= 150000:
        return "senior"

    # 3) ENTRY — junior/entry/grad signals in the TITLE.
    entry_sig = ["entry", "junior", "jr", "associate", "graduate", "grad",
                 "trainee", "assistant", "i"]  # 'i' as a standalone level token
    if title_has(["entry level", "entry-level", "junior", "jr", "associate",
                  "graduate", "grad", "new grad", "early career"]):
        return "entry"
    if years and years <= 1:
        return "entry"

    # 4) MID — explicit mid signals or 2–5 years.
    if title_has(["mid level", "mid-level", "intermediate", "ii"]) or (2 <= years <= 5):
        return "mid"

    # 5) Weak description fallback for internships (whole word, guarded).
    if _has_word(d, ["internship", "intern position", "summer intern"]) and not looks_professional:
        return "internship"

    # 6) Default — neutral professional bucket.
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
