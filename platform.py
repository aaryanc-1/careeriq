"""
Career Platform — Core API
--------------------------
The main entry point that orchestrates all modules.
Input: resume text or file path
Output: complete analysis (matches, gaps, roadmap, market data)
"""

import sys, os, json
sys.path.append(os.path.dirname(__file__))

from resume_engine.resume_parser import parse_resume
from matching_engine.matcher import match_all_careers, get_gap_analysis
from roadmap_engine.roadmap_generator import generate_roadmap
from utils.skill_extractor import extract_skills


def analyze_resume(resume_source, is_text: bool = False, target_career: str = None) -> dict:
    """
    Full platform analysis pipeline.

    Args:
        resume_source: PDF file path or raw resume text
        is_text: True if resume_source is raw text
        target_career: optional specific career to deep-dive (e.g. "Data Scientist")

    Returns:
        Complete analysis dict with profile, matches, gap analysis, and roadmap
    """

    # 1. Parse resume
    print("📄 Parsing resume...")
    profile = parse_resume(resume_source, is_text=is_text)
    user_skills = profile["skills"]
    print(f"   Found {len(user_skills)} skills: {', '.join(user_skills[:6])}{'...' if len(user_skills) > 6 else ''}")

    # 2. Match against all careers
    print("🎯 Matching against career paths...")
    matches = match_all_careers(user_skills)
    top_match = matches[0]["career"] if matches else "Data Analyst"
    target = target_career or top_match
    print(f"   Top match: {top_match} ({matches[0]['score']}%)")

    # 3. Gap analysis for top career (or specified)
    print(f"🔍 Running gap analysis for: {target}...")
    gap = get_gap_analysis(user_skills, target)

    # 4. Generate roadmap
    print(f"🗺️  Generating roadmap...")
    roadmap = generate_roadmap(user_skills, target)

    # 5. Market insights (skill demand from taxonomy)
    market_insights = build_market_insights(user_skills, matches)

    return {
        "profile": {
            "name": profile.get("name"),
            "contact": profile.get("contact"),
            "education": profile.get("education"),
            "experience_years": profile.get("experience_years"),
            "skills": user_skills,
            "skills_by_category": profile.get("skills_by_category"),
            "skill_count": profile.get("skill_count"),
        },
        "career_matches": matches[:7],         # Top 7 matches
        "gap_analysis": gap,
        "roadmap": roadmap,
        "market_insights": market_insights,
        "target_career": target,
    }


def build_market_insights(user_skills: list, matches: list) -> dict:
    """Generate market context and skill demand data."""
    from matching_engine.career_paths import CAREER_PATHS

    # Most in-demand skills across all careers
    skill_demand = {}
    for career_data in CAREER_PATHS.values():
        for skill in career_data.get("required", []):
            skill_demand[skill] = skill_demand.get(skill, 0) + 3
        for skill in career_data.get("important", []):
            skill_demand[skill] = skill_demand.get(skill, 0) + 2
        for skill in career_data.get("nice_to_have", []):
            skill_demand[skill] = skill_demand.get(skill, 0) + 1

    top_skills = sorted(skill_demand.items(), key=lambda x: x[1], reverse=True)[:15]

    # Which of user's skills are most valuable
    your_valuable_skills = [
        {"skill": skill, "demand_score": skill_demand.get(skill, 0)}
        for skill in user_skills
        if skill in skill_demand
    ]
    your_valuable_skills.sort(key=lambda x: x["demand_score"], reverse=True)

    # Salary potential across top matches
    salary_data = [
        {"career": m["career"], "avg_salary": m["avg_salary"], "growth": m["growth"]}
        for m in matches[:5]
    ]

    # High-growth careers
    high_growth = sorted(
        [{"career": k, "growth": v["growth"], "avg_salary": v["avg_salary"]}
         for k, v in CAREER_PATHS.items()],
        key=lambda x: float(x["growth"].replace("%", "").replace("+", "")),
        reverse=True
    )[:5]

    return {
        "top_market_skills": [{"skill": s, "demand_score": d} for s, d in top_skills],
        "your_valuable_skills": your_valuable_skills[:5],
        "salary_by_career": salary_data,
        "highest_growth_careers": high_growth,
    }


def print_report(analysis: dict):
    """Pretty-print the full analysis to terminal."""
    p = analysis["profile"]
    print("\n" + "="*60)
    print(f"  CAREER INTELLIGENCE REPORT")
    if p.get("name"):
        print(f"  Candidate: {p['name']}")
    print("="*60)

    print(f"\n📋 PROFILE SUMMARY")
    print(f"   Skills found: {p['skill_count']}")
    edu = p.get("education", {})
    if edu.get("major"):
        print(f"   Education:   {edu.get('degree', '')} in {edu['major']}")
    if p.get("experience_years"):
        print(f"   Experience:  ~{p['experience_years']} years")

    print(f"\n🎯 CAREER COMPATIBILITY")
    for m in analysis["career_matches"][:5]:
        bar = "█" * (m["score"] // 10) + "░" * (10 - m["score"] // 10)
        print(f"   {m['score']:>3}%  {bar}  {m['career']:<22}  ${m['avg_salary']:,}")

    gap = analysis["gap_analysis"]
    target = analysis["target_career"]
    print(f"\n🔍 GAP ANALYSIS — {target}")
    print(f"   Match score: {gap['match_score']}%  |  Avg salary: ${gap['avg_salary']:,}  |  Growth: {gap['growth']}")
    print(f"   ✅ You have:   {', '.join(gap['you_have'][:6]) or 'None yet'}")
    if gap.get("missing_required"):
        print(f"   🔴 Required:  {', '.join(gap['missing_required'])}")
    if gap.get("missing_important"):
        print(f"   🟡 Important: {', '.join(gap['missing_important'][:4])}")

    roadmap = analysis["roadmap"]
    print(f"\n🗺️  PERSONALIZED ROADMAP  (~{roadmap.get('total_months', 0)} months)")
    for step in roadmap.get("steps", []):
        if step.get("is_project_month"):
            print(f"   {step['label']}: 🚀 BUILD PROJECTS")
            for proj in step.get("projects", [])[:2]:
                print(f"          → {proj}")
        else:
            print(f"   {step['label']}: Learn {', '.join(step['skills'])}")

    mi = analysis["market_insights"]
    print(f"\n📈 MARKET INSIGHTS — Fastest Growing Careers")
    for c in mi["highest_growth_careers"][:3]:
        print(f"   {c['growth']:>5}  {c['career']:<25}  ${c['avg_salary']:,}")

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    sample_resume = """
    Jordan Lee
    jordan.lee@gmail.com | linkedin.com/in/jordanlee | github.com/jordanlee

    EDUCATION
    Bachelor's in Computer Science — NJIT, 2021 - 2024

    EXPERIENCE
    Software Intern — FinTech Corp, 2023 - 2024
    - Built REST APIs in Python/FastAPI
    - Wrote SQL queries and maintained PostgreSQL databases
    - Used Git for version control

    SKILLS
    Python, Java, SQL, Git, Excel, HTML, CSS

    PROJECTS
    - Budget Tracker App (Python + SQLite)
    - Simple Web Scraper (Python + BeautifulSoup)
    """

    result = analyze_resume(sample_resume, is_text=True, target_career="Data Scientist")
    print_report(result)
