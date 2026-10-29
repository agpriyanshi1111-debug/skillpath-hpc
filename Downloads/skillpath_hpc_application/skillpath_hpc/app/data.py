"""Editable starter career-to-skill knowledge base.

This is a small hand-authored demonstration dataset, not an official industry dataset.
Proficiency levels: Beginner=1, Intermediate=2, Advanced=3.
"""
from copy import deepcopy

CAREER_DATA = [
    {
        "career": "AI/ML Engineer", "skill": "Python Programming", "category": "Programming",
        "importance": 5, "target_level": 3, "estimated_hours": 35, "prerequisites": [],
        "tags": ["python", "programming", "ai", "machine learning"],
        "objective": "Write readable Python programs using functions, collections, modules, and basic testing.",
        "activity": "Build a small command-line data cleaning tool.",
        "resource_name": "Python official tutorial", "resource_url": "https://docs.python.org/3/tutorial/"
    },
    {
        "career": "AI/ML Engineer", "skill": "Mathematics for ML", "category": "Mathematics",
        "importance": 4, "target_level": 2, "estimated_hours": 28, "prerequisites": [],
        "tags": ["math", "statistics", "linear algebra", "ai"],
        "objective": "Understand vectors, matrices, probability, derivatives, and descriptive statistics.",
        "activity": "Explain a simple linear regression example using a small dataset.",
        "resource_name": "Khan Academy mathematics", "resource_url": "https://www.khanacademy.org/math"
    },
    {
        "career": "AI/ML Engineer", "skill": "Data Analysis with Pandas", "category": "Data",
        "importance": 4, "target_level": 2, "estimated_hours": 18, "prerequisites": ["Python Programming"],
        "tags": ["python", "data", "analysis", "pandas"],
        "objective": "Load, clean, transform, and summarize tabular datasets.",
        "activity": "Analyze a public CSV and document three findings.",
        "resource_name": "pandas getting started", "resource_url": "https://pandas.pydata.org/docs/getting_started/"
    },
    {
        "career": "AI/ML Engineer", "skill": "Machine Learning Fundamentals", "category": "AI",
        "importance": 5, "target_level": 3, "estimated_hours": 40, "prerequisites": ["Python Programming", "Mathematics for ML", "Data Analysis with Pandas"],
        "tags": ["ai", "machine learning", "ml", "data science"],
        "objective": "Understand supervised learning, train/test splits, overfitting, and evaluation metrics.",
        "activity": "Train and evaluate a classification model on a small dataset.",
        "resource_name": "scikit-learn user guide", "resource_url": "https://scikit-learn.org/stable/user_guide.html"
    },
    {
        "career": "AI/ML Engineer", "skill": "Model Evaluation", "category": "AI",
        "importance": 4, "target_level": 2, "estimated_hours": 16, "prerequisites": ["Machine Learning Fundamentals"],
        "tags": ["ai", "machine learning", "metrics", "evaluation"],
        "objective": "Select suitable metrics and interpret confusion matrices and validation results.",
        "activity": "Compare precision, recall, and F1 on a sample classifier.",
        "resource_name": "scikit-learn model evaluation", "resource_url": "https://scikit-learn.org/stable/modules/model_evaluation.html"
    },
    {
        "career": "AI/ML Engineer", "skill": "SQL and Data Storage", "category": "Data",
        "importance": 3, "target_level": 2, "estimated_hours": 15, "prerequisites": [],
        "tags": ["sql", "database", "data"],
        "objective": "Query relational data using SELECT, JOIN, GROUP BY, and filtering.",
        "activity": "Create a small database and answer five questions with SQL.",
        "resource_name": "SQLBolt interactive lessons", "resource_url": "https://sqlbolt.com/"
    },
    {
        "career": "AI/ML Engineer", "skill": "Communication", "category": "Soft skill",
        "importance": 3, "target_level": 2, "estimated_hours": 8, "prerequisites": [],
        "tags": ["communication", "presentation", "teamwork"],
        "objective": "Explain technical work clearly to a non-specialist audience.",
        "activity": "Give a three-minute explanation of a mini-project.",
        "resource_name": "Suggested search: technical communication", "resource_url": "https://www.google.com/search?q=technical+communication+for+students"
    },
    {
        "career": "Data Scientist", "skill": "Python Programming", "category": "Programming",
        "importance": 5, "target_level": 3, "estimated_hours": 35, "prerequisites": [],
        "tags": ["python", "programming", "data science"],
        "objective": "Use Python functions, data structures, files, and modules to solve data tasks.",
        "activity": "Write a script that validates and summarizes a CSV file.",
        "resource_name": "Python official tutorial", "resource_url": "https://docs.python.org/3/tutorial/"
    },
    {
        "career": "Data Scientist", "skill": "Statistics and Probability", "category": "Mathematics",
        "importance": 5, "target_level": 3, "estimated_hours": 30, "prerequisites": [],
        "tags": ["statistics", "probability", "math", "data science"],
        "objective": "Interpret distributions, sampling, confidence intervals, and basic hypothesis tests.",
        "activity": "Summarize a dataset and explain its variability.",
        "resource_name": "Khan Academy statistics", "resource_url": "https://www.khanacademy.org/math/statistics-probability"
    },
    {
        "career": "Data Scientist", "skill": "Data Cleaning and Visualization", "category": "Data",
        "importance": 5, "target_level": 3, "estimated_hours": 24, "prerequisites": ["Python Programming"],
        "tags": ["data", "visualization", "python", "analysis"],
        "objective": "Clean missing or inconsistent values and choose clear visual encodings.",
        "activity": "Create a small report with three charts and data-quality notes.",
        "resource_name": "pandas getting started", "resource_url": "https://pandas.pydata.org/docs/getting_started/"
    },
    {
        "career": "Data Scientist", "skill": "Machine Learning Fundamentals", "category": "AI",
        "importance": 4, "target_level": 2, "estimated_hours": 32, "prerequisites": ["Python Programming", "Statistics and Probability"],
        "tags": ["ai", "machine learning", "ml", "data science"],
        "objective": "Understand common regression and classification methods and how to validate them.",
        "activity": "Compare a baseline model with one alternative model.",
        "resource_name": "scikit-learn user guide", "resource_url": "https://scikit-learn.org/stable/user_guide.html"
    },
    {
        "career": "Data Scientist", "skill": "SQL and Data Storage", "category": "Data",
        "importance": 4, "target_level": 2, "estimated_hours": 15, "prerequisites": [],
        "tags": ["sql", "database", "data"],
        "objective": "Extract useful information from relational datasets with joins and aggregates.",
        "activity": "Write queries for a small student-performance database.",
        "resource_name": "SQLBolt interactive lessons", "resource_url": "https://sqlbolt.com/"
    },
    {
        "career": "Data Analyst", "skill": "Spreadsheet Analysis", "category": "Data",
        "importance": 4, "target_level": 2, "estimated_hours": 12, "prerequisites": [],
        "tags": ["excel", "spreadsheets", "data", "analysis"],
        "objective": "Use formulas, filters, pivot tables, and basic data validation.",
        "activity": "Create a summary sheet from a sample sales dataset.",
        "resource_name": "Suggested search: spreadsheet analysis", "resource_url": "https://www.google.com/search?q=spreadsheet+analysis+tutorial"
    },
    {
        "career": "Data Analyst", "skill": "SQL and Data Storage", "category": "Data",
        "importance": 5, "target_level": 3, "estimated_hours": 22, "prerequisites": [],
        "tags": ["sql", "database", "data"],
        "objective": "Retrieve and aggregate data from relational databases.",
        "activity": "Answer business questions with joins and grouped queries.",
        "resource_name": "SQLBolt interactive lessons", "resource_url": "https://sqlbolt.com/"
    },
    {
        "career": "Data Analyst", "skill": "Data Visualization", "category": "Analytics",
        "importance": 5, "target_level": 3, "estimated_hours": 20, "prerequisites": ["Spreadsheet Analysis"],
        "tags": ["visualization", "charts", "analytics", "data"],
        "objective": "Select appropriate charts and communicate insights accurately.",
        "activity": "Build a one-page dashboard with three key findings.",
        "resource_name": "Suggested search: data visualization", "resource_url": "https://www.google.com/search?q=data+visualization+best+practices"
    },
    {
        "career": "Data Analyst", "skill": "Statistics Basics", "category": "Mathematics",
        "importance": 4, "target_level": 2, "estimated_hours": 16, "prerequisites": [],
        "tags": ["statistics", "math", "analytics"],
        "objective": "Understand mean, median, spread, outliers, and correlation.",
        "activity": "Describe the distribution of a real-world dataset.",
        "resource_name": "Khan Academy statistics", "resource_url": "https://www.khanacademy.org/math/statistics-probability"
    },
    {
        "career": "Data Analyst", "skill": "Communication", "category": "Soft skill",
        "importance": 4, "target_level": 2, "estimated_hours": 8, "prerequisites": [],
        "tags": ["communication", "presentation", "storytelling"],
        "objective": "Translate analytical results into concise, actionable explanations.",
        "activity": "Present three findings and one limitation from a chart.",
        "resource_name": "Suggested search: data storytelling", "resource_url": "https://www.google.com/search?q=data+storytelling+for+analysts"
    },
    {
        "career": "Software Developer", "skill": "Programming Fundamentals", "category": "Programming",
        "importance": 5, "target_level": 3, "estimated_hours": 35, "prerequisites": [],
        "tags": ["programming", "algorithms", "coding"],
        "objective": "Use control flow, functions, collections, and modular problem solving.",
        "activity": "Solve ten small problems and write tests for edge cases.",
        "resource_name": "Python official tutorial", "resource_url": "https://docs.python.org/3/tutorial/"
    },
    {
        "career": "Software Developer", "skill": "Data Structures and Algorithms", "category": "Computer science",
        "importance": 5, "target_level": 3, "estimated_hours": 40, "prerequisites": ["Programming Fundamentals"],
        "tags": ["dsa", "algorithms", "data structures", "programming"],
        "objective": "Choose suitable arrays, maps, stacks, queues, trees, and algorithmic patterns.",
        "activity": "Implement and analyze five common data-structure problems.",
        "resource_name": "VisuAlgo", "resource_url": "https://visualgo.net/en"
    },
    {
        "career": "Software Developer", "skill": "Git and Version Control", "category": "Tools",
        "importance": 4, "target_level": 2, "estimated_hours": 8, "prerequisites": [],
        "tags": ["git", "github", "tools", "software"],
        "objective": "Commit changes, branch safely, and resolve simple merge conflicts.",
        "activity": "Publish a small project with a clear README and commit history.",
        "resource_name": "Git book", "resource_url": "https://git-scm.com/book/en/v2"
    },
    {
        "career": "Software Developer", "skill": "Testing and Debugging", "category": "Engineering",
        "importance": 4, "target_level": 2, "estimated_hours": 18, "prerequisites": ["Programming Fundamentals"],
        "tags": ["testing", "debugging", "software quality"],
        "objective": "Write basic unit tests and diagnose common runtime errors.",
        "activity": "Add unit tests and reproduce/fix one intentional bug.",
        "resource_name": "pytest documentation", "resource_url": "https://docs.pytest.org/"
    },
    {
        "career": "Software Developer", "skill": "Communication", "category": "Soft skill",
        "importance": 3, "target_level": 2, "estimated_hours": 8, "prerequisites": [],
        "tags": ["communication", "teamwork", "documentation"],
        "objective": "Explain decisions, collaborate, and document technical work.",
        "activity": "Write a project README and present the design in two minutes.",
        "resource_name": "Suggested search: software documentation", "resource_url": "https://www.google.com/search?q=software+documentation+best+practices"
    },
    {
        "career": "Web Developer", "skill": "HTML and CSS", "category": "Web",
        "importance": 5, "target_level": 3, "estimated_hours": 25, "prerequisites": [],
        "tags": ["html", "css", "web", "frontend"],
        "objective": "Build semantic responsive pages with accessible styling.",
        "activity": "Create a responsive personal portfolio page.",
        "resource_name": "MDN web docs", "resource_url": "https://developer.mozilla.org/en-US/docs/Learn"
    },
    {
        "career": "Web Developer", "skill": "JavaScript", "category": "Programming",
        "importance": 5, "target_level": 3, "estimated_hours": 35, "prerequisites": ["HTML and CSS"],
        "tags": ["javascript", "web", "frontend", "programming"],
        "objective": "Use functions, arrays, objects, DOM events, and asynchronous requests.",
        "activity": "Build a form-driven application that consumes a public API.",
        "resource_name": "MDN JavaScript guide", "resource_url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide"
    },
    {
        "career": "Web Developer", "skill": "API and HTTP Fundamentals", "category": "Backend",
        "importance": 4, "target_level": 2, "estimated_hours": 16, "prerequisites": ["JavaScript"],
        "tags": ["api", "http", "backend", "web"],
        "objective": "Understand HTTP methods, status codes, JSON, and API requests.",
        "activity": "Connect a small frontend to a simple REST API.",
        "resource_name": "MDN HTTP overview", "resource_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview"
    },
    {
        "career": "Cybersecurity Analyst", "skill": "Networking Fundamentals", "category": "Networking",
        "importance": 5, "target_level": 3, "estimated_hours": 28, "prerequisites": [],
        "tags": ["networking", "tcp", "ip", "security"],
        "objective": "Explain IP addressing, DNS, TCP/UDP, ports, and common network flows.",
        "activity": "Draw and explain a safe lab network diagram.",
        "resource_name": "Cisco Networking Academy", "resource_url": "https://www.netacad.com/"
    },
    {
        "career": "Cybersecurity Analyst", "skill": "Operating System Fundamentals", "category": "Systems",
        "importance": 4, "target_level": 2, "estimated_hours": 20, "prerequisites": [],
        "tags": ["operating systems", "linux", "systems", "security"],
        "objective": "Understand processes, permissions, filesystems, and basic system logs.",
        "activity": "Review sample logs in a local lab and document observations.",
        "resource_name": "Linux command line guide", "resource_url": "https://ubuntu.com/tutorials/command-line-for-beginners"
    },
    {
        "career": "Cybersecurity Analyst", "skill": "Security Principles", "category": "Security",
        "importance": 5, "target_level": 3, "estimated_hours": 30, "prerequisites": ["Networking Fundamentals", "Operating System Fundamentals"],
        "tags": ["cybersecurity", "security", "risk", "privacy"],
        "objective": "Understand least privilege, defense in depth, threat modeling, and safe incident handling.",
        "activity": "Create a threat model for a fictional student portal.",
        "resource_name": "OWASP Top 10", "resource_url": "https://owasp.org/www-project-top-ten/"
    },
    {
        "career": "Cloud Engineer", "skill": "Linux Fundamentals", "category": "Systems",
        "importance": 4, "target_level": 2, "estimated_hours": 18, "prerequisites": [],
        "tags": ["linux", "systems", "cloud"],
        "objective": "Use the shell, permissions, processes, and basic service logs.",
        "activity": "Set up a local Linux environment and document five commands.",
        "resource_name": "Ubuntu command line tutorial", "resource_url": "https://ubuntu.com/tutorials/command-line-for-beginners"
    },
    {
        "career": "Cloud Engineer", "skill": "Networking Fundamentals", "category": "Networking",
        "importance": 4, "target_level": 2, "estimated_hours": 20, "prerequisites": [],
        "tags": ["networking", "cloud", "tcp", "ip"],
        "objective": "Understand subnets, DNS, ports, and basic network security groups.",
        "activity": "Sketch a simple two-tier cloud architecture.",
        "resource_name": "Cisco Networking Academy", "resource_url": "https://www.netacad.com/"
    },
    {
        "career": "Cloud Engineer", "skill": "Cloud Concepts", "category": "Cloud",
        "importance": 5, "target_level": 3, "estimated_hours": 25, "prerequisites": ["Linux Fundamentals", "Networking Fundamentals"],
        "tags": ["cloud", "aws", "azure", "gcp"],
        "objective": "Compare compute, storage, networking, identity, and shared-responsibility concepts.",
        "activity": "Design a simple deployment diagram and estimate its components.",
        "resource_name": "AWS cloud practitioner resources", "resource_url": "https://aws.amazon.com/training/learn-about/cloud-practitioner/"
    },
    {
        "career": "Cloud Engineer", "skill": "Automation and Scripting", "category": "Automation",
        "importance": 4, "target_level": 2, "estimated_hours": 18, "prerequisites": ["Linux Fundamentals"],
        "tags": ["automation", "scripting", "python", "cloud"],
        "objective": "Automate repeatable tasks with scripts and clear error handling.",
        "activity": "Write a script that checks and reports local file sizes.",
        "resource_name": "Python official tutorial", "resource_url": "https://docs.python.org/3/tutorial/"
    },
    {
        "career": "DevOps Engineer", "skill": "Linux Fundamentals", "category": "Systems",
        "importance": 5, "target_level": 3, "estimated_hours": 20, "prerequisites": [],
        "tags": ["linux", "systems", "devops"],
        "objective": "Operate shell commands, permissions, processes, and services.",
        "activity": "Document a local service's startup and log inspection steps.",
        "resource_name": "Ubuntu command line tutorial", "resource_url": "https://ubuntu.com/tutorials/command-line-for-beginners"
    },
    {
        "career": "DevOps Engineer", "skill": "Git and Version Control", "category": "Tools",
        "importance": 4, "target_level": 2, "estimated_hours": 8, "prerequisites": [],
        "tags": ["git", "github", "devops"],
        "objective": "Use branches, pull requests, tags, and collaborative workflows.",
        "activity": "Practice a feature branch and merge in a demo repository.",
        "resource_name": "Git book", "resource_url": "https://git-scm.com/book/en/v2"
    },
    {
        "career": "DevOps Engineer", "skill": "CI/CD Fundamentals", "category": "Automation",
        "importance": 5, "target_level": 3, "estimated_hours": 24, "prerequisites": ["Git and Version Control"],
        "tags": ["ci/cd", "automation", "devops", "testing"],
        "objective": "Explain automated build, test, and deployment stages.",
        "activity": "Create a basic CI workflow that runs tests on commits.",
        "resource_name": "GitHub Actions documentation", "resource_url": "https://docs.github.com/en/actions"
    },
    {
        "career": "DevOps Engineer", "skill": "Containers", "category": "Infrastructure",
        "importance": 4, "target_level": 2, "estimated_hours": 20, "prerequisites": ["Linux Fundamentals"],
        "tags": ["docker", "containers", "devops"],
        "objective": "Understand images, containers, ports, volumes, and environment variables.",
        "activity": "Containerize a small demo application.",
        "resource_name": "Docker getting started", "resource_url": "https://docs.docker.com/get-started/"
    },
    {
        "career": "UI/UX Designer", "skill": "User Research", "category": "Design",
        "importance": 5, "target_level": 3, "estimated_hours": 18, "prerequisites": [],
        "tags": ["ux", "research", "design", "users"],
        "objective": "Plan interviews, synthesize findings, and identify user needs.",
        "activity": "Interview two volunteers about a simple task and summarize findings.",
        "resource_name": "Nielsen Norman Group articles", "resource_url": "https://www.nngroup.com/articles/"
    },
    {
        "career": "UI/UX Designer", "skill": "Wireframing and Prototyping", "category": "Design",
        "importance": 5, "target_level": 3, "estimated_hours": 24, "prerequisites": ["User Research"],
        "tags": ["ux", "ui", "figma", "design", "prototyping"],
        "objective": "Translate user needs into low- and high-fidelity interface flows.",
        "activity": "Prototype a mobile onboarding flow and test it with a peer.",
        "resource_name": "Figma learning resources", "resource_url": "https://help.figma.com/hc/en-us"
    },
    {
        "career": "UI/UX Designer", "skill": "Accessibility and Usability", "category": "Design",
        "importance": 4, "target_level": 2, "estimated_hours": 16, "prerequisites": ["Wireframing and Prototyping"],
        "tags": ["accessibility", "usability", "ux", "design"],
        "objective": "Apply readable contrast, keyboard access, clear labels, and usability checks.",
        "activity": "Audit a simple page for keyboard navigation and contrast.",
        "resource_name": "W3C WAI resources", "resource_url": "https://www.w3.org/WAI/fundamentals/"
    },
]

CAREERS = sorted({row["career"] for row in CAREER_DATA})

def get_career_data(career: str | None = None):
    rows = CAREER_DATA if not career else [r for r in CAREER_DATA if r["career"].lower() == career.lower()]
    return deepcopy(rows)

def validate_dataset():
    seen = set()
    for row in CAREER_DATA:
        key = (row["career"].casefold(), row["skill"].casefold())
        if key in seen:
            raise ValueError(f"Duplicate career-skill row: {key}")
        seen.add(key)
        if not 1 <= row["target_level"] <= 3:
            raise ValueError(f"Invalid target level for {key}")
        if not 1 <= row["importance"] <= 5:
            raise ValueError(f"Invalid importance for {key}")
        if row["estimated_hours"] <= 0:
            raise ValueError(f"Invalid estimated hours for {key}")
    return True
