"""
Career Keywords — CareerIQ
----------------------------
THE single source of truth that maps job-search keywords to career names.

Both the scrapers (what to search for on USAJobs/Adzuna) AND
compute_weights.py (how to file a scraped job under a career) import this,
so they can never drift out of sync.

ORDER MATTERS for title matching: more specific phrases must come before
more generic ones, so "machine learning engineer" is claimed by ML Engineer
before the generic "engineer"/"software engineer" rule can grab it. The
matcher walks this list top-to-bottom and takes the first keyword that
appears in a job title.

Each entry: (search_keyword, career_name)
The search_keyword is what we send to the job APIs; if a title contains it,
that job is filed under career_name.
"""

CAREER_KEYWORDS = [
    # ── Machine Learning & AI (most specific engineer titles first) ──
    ("machine learning engineer", "ML Engineer"),
    ("ml engineer",               "ML Engineer"),
    ("deep learning engineer",    "ML Engineer"),
    ("ai engineer",               "AI Engineer"),
    ("artificial intelligence",   "AI Engineer"),
    ("nlp engineer",              "NLP Engineer"),
    ("natural language",          "NLP Engineer"),
    ("computer vision",           "Computer Vision Engineer"),
    ("research scientist",        "Research Scientist (AI)"),

    # ── Data & Analytics ──
    ("analytics engineer",        "Analytics Engineer"),
    ("data scientist",            "Data Scientist"),
    ("data engineer",             "Data Engineer"),
    ("data architect",            "Data Engineer"),
    ("clinical data analyst",     "Clinical Data Analyst"),
    ("business intelligence",     "Business Intelligence Developer"),
    ("bi developer",              "Business Intelligence Developer"),
    ("product analyst",           "Product Analyst"),
    ("data analyst",              "Data Analyst"),
    ("quantitative analyst",      "Quantitative Analyst"),
    ("quantitative",              "Quantitative Analyst"),
    ("statistician",              "Data Scientist"),

    # ── Software Engineering (specific roles before generic) ──
    ("frontend engineer",         "Frontend Engineer"),
    ("front end engineer",        "Frontend Engineer"),
    ("front-end developer",       "Frontend Engineer"),
    ("backend engineer",          "Backend Engineer"),
    ("back end engineer",         "Backend Engineer"),
    ("back-end developer",        "Backend Engineer"),
    ("full stack",                "Full Stack Engineer"),
    ("full-stack",                "Full Stack Engineer"),
    ("mobile engineer",           "Mobile Engineer"),
    ("ios developer",             "Mobile Engineer"),
    ("android developer",         "Mobile Engineer"),
    ("devops engineer",           "DevOps Engineer"),
    ("devops",                    "DevOps Engineer"),
    ("site reliability",          "Site Reliability Engineer"),
    ("sre",                       "Site Reliability Engineer"),
    ("cybersecurity",             "Cybersecurity Engineer"),
    ("security engineer",         "Cybersecurity Engineer"),
    ("information security",      "Cybersecurity Engineer"),
    ("cloud architect",           "Cloud Architect"),
    ("solutions architect",       "Cloud Architect"),
    ("embedded systems",          "Embedded Systems Engineer"),
    ("embedded software",         "Embedded Systems Engineer"),
    ("blockchain",                "Blockchain Developer"),
    ("software engineer",         "Software Engineer"),
    ("software developer",        "Software Engineer"),

    # ── Business & Finance ──
    ("investment banker",         "Investment Banker"),
    ("investment banking",        "Investment Banker"),
    ("buy-side analyst",          "Investment Analyst (Buy-Side)"),
    ("equity research",           "Investment Analyst (Buy-Side)"),
    ("financial analyst",         "Financial Analyst"),
    ("corporate finance",         "Corporate Finance Manager"),
    ("finance manager",           "Corporate Finance Manager"),
    ("accountant",                "Accountant"),
    ("accounting",                "Accountant"),
    ("risk analyst",              "Risk Analyst"),
    ("actuary",                   "Actuary"),
    ("actuarial",                 "Actuary"),
    ("management consultant",     "Management Consultant"),
    ("consultant",                "Management Consultant"),
    ("supply chain",              "Supply Chain Manager"),
    ("operations manager",        "Operations Manager"),
    ("product manager",           "Product Manager"),
    ("business analyst",          "Business Analyst"),

    # ── Healthcare ──
    ("registered nurse",          "Registered Nurse"),
    ("nurse",                     "Registered Nurse"),
    ("physician assistant",       "Physician Assistant"),
    ("physical therapist",        "Physical Therapist"),
    ("healthcare administrator",  "Healthcare Administrator"),
    ("health services manager",   "Healthcare Administrator"),
    ("pharmacist",                "Pharmacist"),
    ("mental health counselor",   "Mental Health Counselor"),
    ("counselor",                 "Mental Health Counselor"),
    ("biomedical engineer",       "Biomedical Engineer"),

    # ── Law & Policy ──
    ("attorney",                  "Attorney"),
    ("lawyer",                    "Attorney"),
    ("paralegal",                 "Paralegal"),
    ("compliance officer",        "Compliance Officer"),
    ("policy analyst",            "Policy Analyst"),
    ("contract manager",          "Contract Manager"),

    # ── Creative & Marketing ──
    ("ux designer",               "UX Designer"),
    ("ux/ui",                     "UX Designer"),
    ("product designer",          "UX Designer"),
    ("graphic designer",          "Graphic Designer"),
    ("content strategist",        "Content Strategist"),
    ("digital marketing",         "Digital Marketing Manager"),
    ("marketing manager",         "Digital Marketing Manager"),
    ("brand manager",             "Brand Manager"),
    ("seo specialist",            "SEO Specialist"),
    ("copywriter",                "Copywriter"),
    ("public relations",          "Public Relations Manager"),
    ("video producer",            "Video Producer"),

    # ── Traditional Engineering ──
    ("mechanical engineer",       "Mechanical Engineer"),
    ("civil engineer",            "Civil Engineer"),
    ("electrical engineer",       "Electrical Engineer"),
    ("chemical engineer",         "Chemical Engineer"),
    ("aerospace engineer",        "Aerospace Engineer"),
    ("environmental engineer",    "Environmental Engineer"),
    ("manufacturing engineer",    "Manufacturing Engineer"),
    ("structural engineer",       "Structural Engineer"),

    # ── Education ──
    ("teacher",                   "K-12 Teacher"),
    ("professor",                 "University Professor"),
    ("instructional designer",    "Instructional Designer"),
    ("corporate trainer",         "Corporate Trainer"),
    ("education technology",      "Education Technology Specialist"),

    # ── Operations & HR ──
    ("human resources",           "Human Resources Manager"),
    ("hr manager",                "Human Resources Manager"),
    ("recruiter",                 "Recruiter"),
    ("project manager",           "Project Manager"),
    ("logistics manager",         "Logistics Manager"),
]


def get_career_for_title(title: str):
    """Return the career a job title belongs to, or None. First match wins."""
    t = title.lower()
    for keyword, career in CAREER_KEYWORDS:
        if keyword in t:
            return career
    return None


# The distinct search terms to send to the job APIs (deduplicated, order kept).
def search_terms():
    seen = set()
    terms = []
    for keyword, _career in CAREER_KEYWORDS:
        if keyword not in seen:
            seen.add(keyword)
            terms.append(keyword)
    return terms
