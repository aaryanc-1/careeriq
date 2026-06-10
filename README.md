# Career Opportunity Intelligence Platform

An AI-powered platform that analyzes your background, compares it against real labor market data, and generates a personalized career roadmap.

## What It Does
- Parses your resume and extracts 100+ skills
- Scores you against 10 career paths with weighted matching
- Identifies exact skill gaps (required vs. important vs. nice-to-have)
- Generates a month-by-month learning roadmap with real resources
- Shows market intelligence: skill demand, salary data, growth trends

## Architecture
```
career-platform/
├── database/           # PostgreSQL schema + connection manager
├── data_collection/    # USAJobs scraper + job storage
├── resume_engine/      # PDF/text resume parser
├── matching_engine/    # Career matching + gap analysis
├── roadmap_engine/     # Learning roadmap generator
├── utils/              # Skill taxonomy + extractor (shared)
├── dashboard/          # Interactive HTML dashboard
├── platform.py         # Main orchestrator API
└── collect_jobs.py     # Job data collection runner
```

## Quick Start

### 1. Set up database
```bash
docker-compose up -d          # starts PostgreSQL
cp .env.example .env
pip install -r requirements.txt
python database/db.py         # creates tables
```

### 2. Collect job data
Get a free API key at https://developer.usajobs.gov/apirequest/
```bash
python collect_jobs.py --pages 10   # ~2,500 jobs
```

### 3. Open the dashboard
Open `dashboard/index.html` in a browser — paste any resume and get your full analysis instantly.

### 4. Use the Python API directly
```python
from platform import analyze_resume, print_report

result = analyze_resume("path/to/resume.pdf")
print_report(result)
```

## Tech Stack
- **NLP**: Custom regex + keyword extractor (skills_taxonomy.py) — no model download needed
- **Database**: PostgreSQL with psycopg2
- **Resume Parsing**: pdfplumber for PDF text extraction
- **Frontend**: Vanilla HTML/CSS/JS — zero dependencies
- **Job Data**: USAJobs.gov public API
