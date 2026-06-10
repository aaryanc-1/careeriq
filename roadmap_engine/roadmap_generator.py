"""
Roadmap Generator — CareerIQ
------------------------------
Converts a skill gap into a concrete, month-by-month learning roadmap.
Covers 80+ careers across all industries.
"""

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from matching_engine.matcher import get_gap_analysis

# ── LEARNING RESOURCES ────────────────────────────────────────────────────────
# Format: [(type, title, url), ...]
SKILL_RESOURCES = {
    # Programming
    "python":               [("course", "Python for Everybody – Coursera (free audit)", "https://coursera.org/specializations/python"),
                              ("practice", "LeetCode Python track", "https://leetcode.com")],
    "r":                    [("book", "R for Data Science – Free online", "https://r4ds.had.co.nz"),
                              ("course", "Statistics with R – Coursera", "https://coursera.org/specializations/statistics")],
    "javascript":           [("course", "The Odin Project – Free full curriculum", "https://theodinproject.com"),
                              ("docs", "MDN JavaScript Guide", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide")],
    "typescript":           [("docs", "TypeScript Handbook – Official", "https://typescriptlang.org/docs"),
                              ("course", "Understanding TypeScript – Udemy", "https://udemy.com")],
    "java":                 [("course", "Java Programming Masterclass – Udemy", "https://udemy.com"),
                              ("practice", "Exercism Java Track – Free", "https://exercism.org/tracks/java")],
    "c++":                  [("course", "C++ Nanodegree – Udacity", "https://udacity.com/course/c-plus-plus-nanodegree--nd213"),
                              ("book", "A Tour of C++ – Bjarne Stroustrup", "https://stroustrup.com/tour3.html")],
    "c":                    [("book", "The C Programming Language – K&R", "https://amazon.com"),
                              ("course", "CS50 – Harvard (free)", "https://cs50.harvard.edu")],
    "scala":                [("course", "Functional Programming in Scala – Coursera", "https://coursera.org/specializations/scala"),
                              ("docs", "Scala Documentation", "https://docs.scala-lang.org")],
    "go":                   [("docs", "Tour of Go – Official", "https://go.dev/tour"),
                              ("course", "Go: The Complete Developer's Guide – Udemy", "https://udemy.com")],
    "swift":                [("docs", "Swift.org – Official Tutorials", "https://swift.org/getting-started"),
                              ("course", "iOS & Swift Bootcamp – Udemy", "https://udemy.com")],
    "kotlin":               [("docs", "Kotlin Official Docs", "https://kotlinlang.org/docs"),
                              ("course", "Android with Kotlin – Google Codelabs", "https://developer.android.com/codelabs")],
    "solidity":             [("course", "CryptoZombies – Free Solidity course", "https://cryptozombies.io"),
                              ("docs", "Solidity Documentation", "https://docs.soliditylang.org")],
    # Data
    "sql":                  [("course", "Mode SQL Tutorial – Free", "https://mode.com/sql-tutorial"),
                              ("practice", "SQLZoo – Interactive exercises", "https://sqlzoo.net")],
    "pandas":               [("docs", "Pandas Official Tutorials", "https://pandas.pydata.org/docs/getting_started"),
                              ("course", "Kaggle Pandas – Free", "https://kaggle.com/learn/pandas")],
    "numpy":                [("docs", "NumPy Quickstart", "https://numpy.org/doc/stable/user/quickstart"),
                              ("course", "Kaggle Intro to ML – Free", "https://kaggle.com/learn/intro-to-machine-learning")],
    "excel":                [("course", "Excel Skills for Business – Coursera (free audit)", "https://coursera.org/specializations/excel"),
                              ("practice", "Exceljet formulas reference", "https://exceljet.net")],
    "tableau":              [("course", "Tableau Training – Free on Tableau Public", "https://public.tableau.com/learn/training"),
                              ("practice", "Build 3 dashboards on Tableau Public", "https://public.tableau.com")],
    "power bi":             [("course", "Microsoft Power BI – Microsoft Learn (free)", "https://learn.microsoft.com/training/powerbi"),
                              ("practice", "Build a report using a public dataset", "https://powerbi.microsoft.com")],
    "data visualization":   [("course", "Data Viz with Python – Coursera", "https://coursera.org/learn/python-for-data-visualization"),
                              ("practice", "Kaggle Data Visualization – Free", "https://kaggle.com/learn/data-visualization")],
    "dbt":                  [("course", "dbt Fundamentals – Free", "https://courses.getdbt.com/courses/fundamentals"),
                              ("docs", "dbt Official Docs", "https://docs.getdbt.com")],
    "snowflake":            [("course", "Snowflake Essentials – Free", "https://learn.snowflake.com"),
                              ("cert", "Snowflake SnowPro Core Certification", "https://learn.snowflake.com/en/certifications")],
    "spark":                [("course", "Apache Spark with Python – Udemy", "https://udemy.com"),
                              ("docs", "PySpark Quick Start", "https://spark.apache.org/docs/latest/quick-start")],
    "airflow":              [("docs", "Apache Airflow Docs", "https://airflow.apache.org/docs"),
                              ("course", "Data Engineering with Apache Airflow – Udemy", "https://udemy.com")],
    "etl":                  [("course", "Data Engineering – DataCamp", "https://datacamp.com"),
                              ("project", "Build an ETL pipeline: API → transform → PostgreSQL", "")],
    # ML & AI
    "machine learning":     [("course", "Andrew Ng ML Specialization – Coursera", "https://coursera.org/specializations/machine-learning-introduction"),
                              ("book", "Hands-On ML with Scikit-Learn – O'Reilly", "https://oreilly.com")],
    "deep learning":        [("course", "Deep Learning Specialization – Coursera", "https://coursera.org/specializations/deep-learning"),
                              ("practice", "Fast.ai Practical Deep Learning – Free", "https://fast.ai")],
    "scikit-learn":         [("docs", "Scikit-learn User Guide", "https://scikit-learn.org/stable/user_guide"),
                              ("course", "Kaggle Intermediate ML – Free", "https://kaggle.com/learn/intermediate-machine-learning")],
    "tensorflow":           [("course", "TensorFlow Developer Certificate – Coursera", "https://coursera.org/professional-certificates/tensorflow-in-practice"),
                              ("docs", "TensorFlow Tutorials", "https://tensorflow.org/tutorials")],
    "pytorch":              [("course", "PyTorch for Deep Learning – Udemy", "https://udemy.com"),
                              ("docs", "Official PyTorch Tutorials", "https://pytorch.org/tutorials")],
    "large language models":[("course", "LLM Bootcamp – Full Stack Deep Learning", "https://fullstackdeeplearning.com/llm-bootcamp"),
                              ("practice", "Build a RAG app with LangChain", "https://python.langchain.com")],
    "prompt engineering":   [("course", "ChatGPT Prompt Engineering – DeepLearning.AI (free)", "https://deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers"),
                              ("practice", "PromptingGuide.ai", "https://promptingguide.ai")],
    "nlp":                  [("course", "NLP Specialization – Coursera", "https://coursera.org/specializations/natural-language-processing"),
                              ("practice", "Hugging Face NLP Course – Free", "https://huggingface.co/course")],
    "computer vision":      [("course", "Computer Vision – Coursera", "https://coursera.org/learn/deep-neural-networks-with-pytorch"),
                              ("practice", "Roboflow tutorials – Free", "https://blog.roboflow.com/tutorials")],
    "statistics":           [("course", "Statistics with Python – Coursera", "https://coursera.org/specializations/statistics-with-python"),
                              ("book", "Think Stats – Free", "https://greenteapress.com/thinkstats2")],
    "a/b testing":          [("course", "A/B Testing – Udacity (free)", "https://udacity.com/course/ab-testing--ud257"),
                              ("article", "A/B Testing Guide – Optimizely", "https://optimizely.com/optimization-glossary/ab-testing")],
    "time series":          [("course", "Practical Time Series Analysis – Coursera", "https://coursera.org/learn/practical-time-series-analysis"),
                              ("practice", "Kaggle Time Series Competition", "https://kaggle.com/competitions")],
    # Cloud & DevOps
    "aws":                  [("cert", "AWS Cloud Practitioner – Free exam prep", "https://aws.amazon.com/certification/certified-cloud-practitioner"),
                              ("course", "AWS for Beginners – freeCodeCamp YouTube", "https://youtube.com/freecodecamp")],
    "docker":               [("docs", "Docker Getting Started Guide", "https://docs.docker.com/get-started"),
                              ("course", "Docker & Kubernetes – Udemy", "https://udemy.com")],
    "kubernetes":           [("course", "Kubernetes for Beginners – KodeKloud (free tier)", "https://kodekloud.com"),
                              ("docs", "Kubernetes Official Tutorials", "https://kubernetes.io/docs/tutorials")],
    "git":                  [("course", "Git & GitHub Crash Course – freeCodeCamp", "https://youtube.com/freecodecamp"),
                              ("practice", "GitHub Skills – Interactive labs", "https://skills.github.com")],
    "linux":                [("course", "The Linux Command Line – Free book", "https://linuxcommand.org/tlcl.php"),
                              ("practice", "OverTheWire Bandit – Linux challenges", "https://overthewire.org/wargames/bandit")],
    "ci/cd":                [("course", "GitHub Actions – Official docs", "https://docs.github.com/actions"),
                              ("course", "CI/CD with Jenkins – Udemy", "https://udemy.com")],
    "terraform":            [("course", "HashiCorp Terraform Associate – Free study guide", "https://developer.hashicorp.com/terraform/tutorials"),
                              ("docs", "Terraform Official Docs", "https://developer.hashicorp.com/terraform/docs")],
    # Web
    "react":                [("course", "React – Official Tutorial", "https://react.dev/learn"),
                              ("course", "Full Stack Open – Free university course", "https://fullstackopen.com")],
    "html":                 [("course", "freeCodeCamp Responsive Web Design – Free", "https://freecodecamp.org/learn/2022/responsive-web-design"),
                              ("docs", "MDN HTML Guide", "https://developer.mozilla.org/docs/Web/HTML")],
    "css":                  [("course", "CSS – The Complete Guide – Udemy", "https://udemy.com"),
                              ("practice", "CSS Grid Garden – Free game", "https://cssgridgarden.com")],
    # Finance
    "financial modeling":   [("course", "Financial Modeling & Valuation – Wall Street Prep", "https://wallstreetprep.com"),
                              ("course", "Excel Crash Course – CFI (free)", "https://corporatefinanceinstitute.com/courses")],
    "accounting":           [("course", "Financial Accounting – Coursera (free audit)", "https://coursera.org/learn/financial-accounting"),
                              ("book", "Accounting Made Simple – Mike Piper", "https://amazon.com")],
    "valuation":            [("course", "Business Valuation – Coursera", "https://coursera.org/learn/valuation-for-startups"),
                              ("book", "Investment Valuation – Aswath Damodaran (free PDFs)", "https://pages.stern.nyu.edu/~adamodar")],
    "quantitative analysis":[("course", "Quantitative Finance – Coursera", "https://coursera.org/learn/quantitative-methods"),
                              ("book", "Paul Wilmott on Quantitative Finance", "https://amazon.com")],
    # Design
    "ux design":            [("course", "Google UX Design Certificate – Coursera", "https://coursera.org/professional-certificates/google-ux-design"),
                              ("practice", "Build 3 case studies for your portfolio", "https://uxfol.io")],
    "figma":                [("course", "Figma Essentials – YouTube (free)", "https://youtube.com/c/DesignCourse"),
                              ("docs", "Figma Official Tutorials", "https://help.figma.com/hc/en-us/categories/360002042553")],
    "graphic design":       [("course", "Graphic Design Specialization – Coursera", "https://coursera.org/specializations/graphic-design"),
                              ("practice", "Daily UI challenge", "https://dailyui.co")],
    "adobe photoshop":      [("course", "Adobe Photoshop CC – Udemy", "https://udemy.com"),
                              ("docs", "Adobe Photoshop Tutorials – Official", "https://helpx.adobe.com/photoshop/tutorials.html")],
    # Marketing
    "digital marketing":    [("cert", "Google Digital Marketing Certificate – Free", "https://learndigital.withgoogle.com/digitalgarage"),
                              ("course", "Digital Marketing Specialization – Coursera", "https://coursera.org/specializations/digital-marketing")],
    "seo":                  [("course", "SEO Fundamentals – Semrush Academy (free)", "https://semrush.com/academy"),
                              ("guide", "Moz Beginner's Guide to SEO", "https://moz.com/beginners-guide-to-seo")],
    "content marketing":    [("course", "Content Marketing Certification – HubSpot (free)", "https://academy.hubspot.com/courses/content-marketing"),
                              ("book", "Content Inc. – Joe Pulizzi", "https://amazon.com")],
    "google analytics":     [("cert", "Google Analytics Certification – Free", "https://skillshop.exceedlms.com"),
                              ("course", "Google Analytics 4 – Analytics Mania (free)", "https://analyticsmania.com/courses")],
    # Engineering
    "cad":                  [("course", "AutoCAD Fundamentals – Autodesk Learning", "https://learn.autodesk.com"),
                              ("course", "AutoCAD 2024 – Udemy", "https://udemy.com")],
    "solidworks":           [("course", "SolidWorks for Beginners – Udemy", "https://udemy.com"),
                              ("docs", "SolidWorks Official Tutorials", "https://my.solidworks.com/training")],
    "matlab":               [("course", "MATLAB Onramp – MathWorks (free)", "https://matlabacademy.mathworks.com"),
                              ("docs", "MATLAB Official Documentation", "https://mathworks.com/help/matlab")],
    "project management":   [("cert", "Google Project Management Certificate – Coursera", "https://coursera.org/professional-certificates/google-project-management"),
                              ("cert", "PMP Exam Prep – PMI", "https://pmi.org/certifications/project-management-pmp")],
    # Healthcare
    "nursing":              [("resource", "NCLEX Study Guide – Nurseslabs", "https://nurseslabs.com/nclex"),
                              ("resource", "Nursing Pharmacology – Nurseslabs", "https://nurseslabs.com/pharmacology")],
    "clinical research":    [("course", "Clinical Trials – Coursera (free audit)", "https://coursera.org/learn/clinical-trials"),
                              ("cert", "CITI Program Research Ethics – Free tier", "https://citiprogram.org")],
    # Legal
    "legal research":       [("course", "Legal Research & Writing – Coursera", "https://coursera.org/learn/legal-research-writing-and-analysis"),
                              ("resource", "Westlaw Training – Thomson Reuters", "https://legal.thomsonreuters.com/en/products/westlaw/training")],
    "contract drafting":    [("course", "Contract Drafting – Coursera (free audit)", "https://coursera.org/learn/contract-drafting"),
                              ("resource", "IACCM Contract Templates", "https://iaccm.com")],
    # Education
    "instructional design": [("cert", "Instructional Design Certificate – ATD", "https://td.org/certification"),
                              ("course", "Instructional Design – Coursera", "https://coursera.org/learn/instructional-design-foundations-applications")],
    "curriculum development":[("course", "Curriculum Design – Coursera", "https://coursera.org/learn/curriculum-design"),
                               ("book", "Understanding by Design – Wiggins & McTighe", "https://amazon.com")],
    # Cybersecurity
    "cybersecurity":        [("cert", "CompTIA Security+ – Study guide", "https://comptia.org/certifications/security"),
                              ("course", "Google Cybersecurity Certificate – Coursera", "https://coursera.org/professional-certificates/google-cybersecurity")],
    "network security":     [("cert", "CompTIA Network+ – Study guide", "https://comptia.org/certifications/network"),
                              ("course", "Network Security – Cybrary (free)", "https://cybrary.it")],
}

# ── SKILL DURATION IN WEEKS ───────────────────────────────────────────────────
SKILL_DURATION_WEEKS = {
    # Programming
    "python": 6, "r": 4, "javascript": 6, "typescript": 3, "java": 6,
    "c++": 8, "c": 6, "scala": 5, "go": 4, "swift": 5, "kotlin": 4,
    "solidity": 5, "node.js": 3,
    # Data
    "sql": 4, "pandas": 2, "numpy": 2, "excel": 3, "tableau": 3,
    "power bi": 3, "data visualization": 3, "dbt": 2, "snowflake": 2,
    "spark": 4, "airflow": 3, "etl": 3, "data analysis": 3,
    "data warehouse": 3, "data pipeline": 3,
    # ML/AI
    "machine learning": 8, "deep learning": 8, "scikit-learn": 3,
    "tensorflow": 6, "pytorch": 6, "large language models": 4,
    "prompt engineering": 2, "nlp": 5, "computer vision": 5,
    "a/b testing": 2, "time series": 3, "statistics": 5,
    # Cloud
    "aws": 4, "docker": 2, "kubernetes": 4, "git": 1, "linux": 3,
    "ci/cd": 2, "terraform": 3, "cloud computing": 4,
    # Web
    "react": 4, "html": 3, "css": 3, "typescript": 3, "vue": 4,
    # Finance
    "financial modeling": 4, "accounting": 5, "valuation": 4,
    "quantitative analysis": 5, "financial analysis": 4,
    # Design
    "ux design": 5, "figma": 2, "graphic design": 5,
    "adobe photoshop": 3, "wireframing": 2, "prototyping": 2,
    # Marketing
    "digital marketing": 4, "seo": 3, "content marketing": 3,
    "google analytics": 2, "copywriting": 4,
    # Engineering
    "cad": 4, "solidworks": 4, "matlab": 3, "project management": 4,
    "mechanical engineering": 12, "civil engineering": 12,
    # Healthcare
    "nursing": 16, "clinical research": 4,
    # Legal
    "legal research": 4, "contract drafting": 3,
    # Soft/universal
    "communication": 2, "leadership": 4,
}
DEFAULT_WEEKS = 3

# ── PROJECT SUGGESTIONS ───────────────────────────────────────────────────────
PROJECT_SUGGESTIONS = {
    # Data & Analytics
    "Data Analyst":             ["Analyze a Kaggle public dataset, write an insights report",
                                 "Build a sales or marketing dashboard in Tableau/Power BI",
                                 "Create a SQL-based reporting pipeline on public data"],
    "Business Analyst":         ["Write a business case analysis for a real company problem",
                                 "Build a process flow diagram and improvement proposal",
                                 "Create a mock requirements document for a fictional app"],
    "Data Scientist":           ["Enter a Kaggle beginner competition and publish a notebook",
                                 "Build an end-to-end ML model (data → train → evaluate → visualize)",
                                 "Predict housing prices or churn using scikit-learn"],
    "Data Engineer":            ["Build an ETL pipeline: public API → transform → PostgreSQL",
                                 "Create a dbt project on a public dataset",
                                 "Set up Airflow to schedule a data pipeline locally"],
    "Analytics Engineer":       ["Build a full dbt project with staging + mart layers",
                                 "Design a data warehouse schema from scratch",
                                 "Set up a Snowflake + dbt + Metabase stack (free tiers)"],
    "Product Analyst":          ["Analyze a public product funnel dataset and write insights",
                                 "Design and analyze a mock A/B test",
                                 "Build a user retention dashboard"],
    "Business Intelligence Developer": ["Build 3 connected dashboards from a single dataset",
                                 "Design and document a BI reporting layer",
                                 "Automate a weekly KPI report in Power BI"],
    # ML & AI
    "ML Engineer":              ["Deploy a trained ML model as a REST API with FastAPI + Docker",
                                 "Build an MLOps pipeline with experiment tracking (MLflow)",
                                 "Fine-tune a small open-source LLM for a specific task"],
    "AI Engineer":              ["Build a RAG chatbot with LangChain + a vector DB",
                                 "Create an AI-powered tool using the OpenAI or Anthropic API",
                                 "Deploy an LLM app with Streamlit or FastAPI"],
    "NLP Engineer":             ["Build a text classifier on a public dataset",
                                 "Fine-tune a Hugging Face model for sentiment analysis",
                                 "Build a simple search engine with semantic embeddings"],
    "Computer Vision Engineer": ["Train an image classifier on CIFAR-10 or a custom dataset",
                                 "Build an object detection app with YOLO",
                                 "Create a real-time webcam detection demo"],
    "Quantitative Analyst":     ["Build a stock backtesting script in Python",
                                 "Monte Carlo simulation for portfolio risk",
                                 "Implement a simple pairs trading strategy"],
    "Research Scientist (AI)":  ["Reproduce a paper's results from scratch",
                                 "Write a technical blog post on a recent AI paper",
                                 "Contribute to an open-source ML library"],
    # Software Engineering
    "Software Engineer":        ["Build and deploy a REST API with authentication",
                                 "Contribute to an open-source project on GitHub",
                                 "Build a full-stack app with a frontend + backend"],
    "Frontend Engineer":        ["Build a responsive portfolio site from scratch",
                                 "Clone a popular app's UI (Twitter, Airbnb, etc.)",
                                 "Build a React app that consumes a public API"],
    "Backend Engineer":         ["Build a RESTful API with authentication and a database",
                                 "Design and implement a database schema for a real-world use case",
                                 "Build a background job processing system"],
    "Full Stack Engineer":      ["Build a full-stack task manager or social app",
                                 "Deploy an app on AWS or Render with CI/CD",
                                 "Build a SaaS landing page with a working backend"],
    "Mobile Engineer":          ["Build and publish a simple iOS or Android app",
                                 "Build a cross-platform app with React Native",
                                 "Integrate a REST API into a mobile app"],
    "DevOps Engineer":          ["Set up a CI/CD pipeline for a GitHub project",
                                 "Deploy an app on Kubernetes locally with minikube",
                                 "Write Terraform to provision a cloud resource"],
    "Site Reliability Engineer":["Set up Prometheus + Grafana monitoring on a local app",
                                 "Write a runbook for a common incident scenario",
                                 "Simulate chaos engineering on a local cluster"],
    "Cybersecurity Engineer":   ["Set up a home lab and run vulnerability scans (legal targets only)",
                                 "Complete TryHackMe or HackTheBox beginner rooms",
                                 "Write a threat model for a fictional application"],
    "Cloud Architect":          ["Design a 3-tier architecture diagram in AWS",
                                 "Deploy a serverless app with Lambda + API Gateway",
                                 "Write a cost optimization report for a hypothetical workload"],
    "Embedded Systems Engineer":["Build a blinking LED project then expand to sensor reading",
                                 "Write a device driver for a simple peripheral",
                                 "Implement a small RTOS project on an Arduino or Raspberry Pi"],
    "Blockchain Developer":     ["Deploy a simple ERC-20 token on a testnet",
                                 "Build a basic NFT smart contract",
                                 "Create a simple DeFi liquidity pool clone"],
    # Business & Finance
    "Financial Analyst":        ["Build a 3-statement financial model for a public company",
                                 "Write an equity research report on a stock you follow",
                                 "Create a budget vs actuals dashboard in Excel"],
    "Investment Banker":        ["Build a DCF and comparable company analysis",
                                 "Model an LBO for a fictional buyout scenario",
                                 "Write a pitch deck for a mock M&A transaction"],
    "Investment Analyst (Buy-Side)": ["Build a stock screening model in Python",
                                 "Write a 2-page investment thesis on a public company",
                                 "Build a portfolio tracker with Python + Yahoo Finance"],
    "Accountant":               ["Prepare a mock set of financial statements",
                                 "Model a tax return scenario in Excel",
                                 "Build a budget tracking tool in Excel or Google Sheets"],
    "Corporate Finance Manager":["Build a company budget model with variance analysis",
                                 "Create a rolling 12-month cash flow forecast",
                                 "Present a capital allocation recommendation (mock board deck)"],
    "Risk Analyst":             ["Build a credit scoring model on public data",
                                 "Create a risk register for a fictional project",
                                 "Run a Monte Carlo simulation to model financial risk"],
    "Actuary":                  ["Model a life insurance premium calculation",
                                 "Sit for and pass Exam P or Exam FM (Society of Actuaries)",
                                 "Build a claims frequency model on public insurance data"],
    "Management Consultant":    ["Write a consulting case study with problem, analysis, recommendation",
                                 "Practice 30 case interviews (Case in Point framework)",
                                 "Build a benchmarking analysis comparing 3 companies"],
    "Supply Chain Manager":     ["Map a full supply chain for a real product you use",
                                 "Build a demand forecast model in Excel",
                                 "Design an inventory optimization model"],
    "Operations Manager":       ["Map and optimize a business process using lean principles",
                                 "Build a KPI dashboard for an operations team",
                                 "Write an SOP (standard operating procedure) for a workflow"],
    "Product Manager":          ["Write a full PRD (product requirements doc) for an app idea",
                                 "Run a user research session and synthesize findings",
                                 "Build a product roadmap in Notion or Jira"],
    "Entrepreneur / Startup Founder": ["Build an MVP of your idea (no-code or coded)",
                                 "Write a 1-page business plan and pitch deck",
                                 "Interview 20 potential customers about the problem"],
    # Healthcare
    "Registered Nurse":         ["Complete a clinical simulation or skills lab",
                                 "Write a patient care plan for a case study",
                                 "Obtain a specialty certification (wound care, oncology, etc.)"],
    "Physician Assistant":      ["Shadow a PA for 40+ hours across specialties",
                                 "Write a SOAP note for 5 mock patient cases",
                                 "Complete a clinical rotation in a new specialty"],
    "Physical Therapist":       ["Document a full treatment plan for a mock case",
                                 "Learn and practice 2 new manual therapy techniques",
                                 "Complete a continuing education course in a specialty"],
    "Healthcare Administrator": ["Write a quality improvement proposal for a real healthcare issue",
                                 "Build a staffing model for a clinical department",
                                 "Analyze CMS public data and write a policy brief"],
    "Clinical Data Analyst":    ["Analyze a public clinical trial dataset and write findings",
                                 "Build a patient outcomes dashboard in Tableau",
                                 "Complete CITI training and analyze de-identified EHR data"],
    "Mental Health Counselor":  ["Complete supervised clinical hours (required for licensure)",
                                 "Write a treatment plan using CBT framework for a mock case",
                                 "Present a case at a peer consultation group"],
    "Biomedical Engineer":      ["Design a simple medical device prototype (CAD model)",
                                 "Write a 510(k) pathway summary for a fictional device",
                                 "Analyze biosignal data (ECG, EEG) with Python"],
    # Law & Policy
    "Attorney":                 ["Write a legal memo analyzing both sides of a real case",
                                 "Draft a simple contract (NDA, freelance agreement)",
                                 "Participate in a moot court or mock negotiation"],
    "Paralegal":                ["Draft a demand letter or complaint for a mock case",
                                 "Complete a Westlaw legal research exercise",
                                 "Organize and index a fictional case file"],
    "Compliance Officer":       ["Write a compliance policy for a fictional company",
                                 "Conduct a mock risk assessment and write the report",
                                 "Map a regulatory requirement to internal controls"],
    "Policy Analyst":           ["Write a 3-page policy brief on a current issue",
                                 "Analyze public government data and derive recommendations",
                                 "Build a stakeholder map for a policy proposal"],
    # Creative
    "UX Designer":              ["Complete a full case study: research → wireframes → prototype → test",
                                 "Redesign an existing app's worst UX flow",
                                 "Build a design system with components in Figma"],
    "Graphic Designer":         ["Build a brand identity (logo, color palette, typography)",
                                 "Design a 3-piece marketing campaign (social, email, banner)",
                                 "Redesign a real company's outdated logo"],
    "Digital Marketing Manager":["Run a real Google Ads or Meta Ads campaign (even $10 budget)",
                                 "Build a 90-day content calendar for a fictional brand",
                                 "Write a performance report analyzing campaign data"],
    "Content Strategist":       ["Write 10 SEO-optimized blog posts on a topic you know well",
                                 "Build a content audit for a real company's website",
                                 "Create a full editorial calendar with distribution strategy"],
    "SEO Specialist":           ["Conduct a technical SEO audit on a real or fictional site",
                                 "Build a keyword map for a niche topic",
                                 "Write 5 optimized blog posts and track rankings over 90 days"],
    "Copywriter":               ["Write 3 landing pages for fictional products",
                                 "Write an email sequence (5 emails) for a product launch",
                                 "Rewrite a real company's homepage to improve conversion"],
    "Video Producer":           ["Produce a 2-minute documentary-style video on any topic",
                                 "Create a YouTube channel and publish 5 videos",
                                 "Edit a raw interview into a polished 90-second cut"],
    # Traditional Engineering
    "Mechanical Engineer":      ["Design a mechanical part in SolidWorks and run a stress analysis",
                                 "Build a physical prototype (even with cardboard/3D printing)",
                                 "Write an engineering report for a design decision"],
    "Civil Engineer":           ["Design a small structural element (beam, column) with calculations",
                                 "Create a site plan drawing in AutoCAD",
                                 "Write a geotechnical investigation summary"],
    "Electrical Engineer":      ["Design a simple circuit and simulate it in LTspice",
                                 "Build an Arduino project with sensor + actuator",
                                 "Write a power system load flow analysis report"],
    "Chemical Engineer":        ["Model a process unit (distillation column, reactor) in Aspen",
                                 "Write a process safety review for a fictional chemical plant",
                                 "Run a material and energy balance on a simple process"],
    "Environmental Engineer":   ["Conduct a desktop environmental impact assessment",
                                 "Analyze EPA or state water quality data with Python",
                                 "Write a remediation plan for a fictional contaminated site"],
    "Manufacturing Engineer":   ["Map a production line and identify waste using lean principles",
                                 "Run a measurement system analysis (MSA) on mock data",
                                 "Design a process FMEA for a simple product"],
    # Education
    "K-12 Teacher":             ["Design a full unit plan for a topic you'd teach",
                                 "Record and self-critique a 10-minute practice lesson",
                                 "Build a student assessment rubric aligned to standards"],
    "Instructional Designer":   ["Build a full eLearning module in Articulate Storyline",
                                 "Create a learning needs analysis document",
                                 "Design a blended learning curriculum for a real topic"],
    "Corporate Trainer":        ["Facilitate a 30-minute training session and collect feedback",
                                 "Build a full training program deck with activities",
                                 "Create a pre/post assessment to measure learning"],
    # HR & Operations
    "Human Resources Manager":  ["Write a full performance review template",
                                 "Design a 90-day onboarding plan for a new hire",
                                 "Analyze employee survey data and write recommendations"],
    "Recruiter":                ["Source 20 candidates for a mock role and write outreach messages",
                                 "Build a talent pipeline for a hard-to-fill position",
                                 "Write a job description that improves on a real one"],
    "Project Manager":          ["Plan a fictional project end-to-end with WBS, timeline, budget",
                                 "Run a mock sprint with a team (even friends/colleagues)",
                                 "Write a project post-mortem for a past experience"],
    "Logistics Manager":        ["Map a supply chain and identify 3 optimization opportunities",
                                 "Build a transportation cost model in Excel",
                                 "Write an RFP for a fictional 3PL provider selection"],
}


def generate_roadmap(user_skills: list, career_title: str) -> dict:
    gap = get_gap_analysis(user_skills, career_title)
    if "error" in gap:
        return gap

    priority_gaps = gap["priority_gaps"]
    if not priority_gaps:
        return {
            "career": career_title,
            "message": "🎉 You already have all the key skills for this role! Focus on building projects.",
            "projects": PROJECT_SUGGESTIONS.get(career_title, ["Build a portfolio project showcasing your skills"]),
            "steps": [],
            "total_weeks": 0,
        }

    steps = []
    month = 1
    current_month_skills = []
    current_month_weeks = 0

    def flush_month():
        nonlocal month, current_month_skills, current_month_weeks
        if current_month_skills:
            steps.append({
                "month": month,
                "label": f"Month {month}",
                "skills": list(current_month_skills),
                "duration_weeks": current_month_weeks,
                "milestone": f"Complete {', '.join(current_month_skills[:2])} fundamentals",
            })
            month += 1
            current_month_skills = []
            current_month_weeks = 0

    for skill in priority_gaps:
        weeks = SKILL_DURATION_WEEKS.get(skill, DEFAULT_WEEKS)
        if current_month_weeks + weeks > 5 and current_month_skills:
            flush_month()
        current_month_skills.append(skill)
        current_month_weeks += weeks

    flush_month()

    projects = PROJECT_SUGGESTIONS.get(career_title, ["Build a portfolio project showcasing your new skills"])
    steps.append({
        "month": month,
        "label": f"Month {month}",
        "skills": [],
        "is_project_month": True,
        "milestone": "Build portfolio projects",
        "projects": projects[:2],
    })

    resources = {}
    for skill in priority_gaps:
        if skill in SKILL_RESOURCES:
            resources[skill] = SKILL_RESOURCES[skill]

    total_weeks = sum(SKILL_DURATION_WEEKS.get(s, DEFAULT_WEEKS) for s in priority_gaps)

    return {
        "career": career_title,
        "current_score": gap["match_score"],
        "target_salary": gap["avg_salary"],
        "market_growth": gap["growth"],
        "skills_you_have": gap["you_have"],
        "total_gaps": gap["total_gaps"],
        "steps": steps,
        "total_months": month,
        "estimated_weeks": total_weeks,
        "resources": resources,
        "portfolio_projects": projects,
    }


if __name__ == "__main__":
    import json
    user_skills = ["excel", "writing", "communication", "project management"]
    roadmap = generate_roadmap(user_skills, "Digital Marketing Manager")
    print(json.dumps(roadmap, indent=2))
