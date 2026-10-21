"""
Skill Ontology — Prerequisite Knowledge Graph and Category Taxonomy.

This module defines the knowledge structures that enable skill inference:
    - PREREQUISITE_GRAPH: child skill → primary parent skill
    - ADDITIONAL_PREREQUISITES: child skill → other valid parent skills
    - SKILL_CATEGORIES:   skill → category name
    - CATEGORY_SKILLS:    category → list of skills

Example:
    If a resume mentions Django, Pandas, and scikit-learn, but never "Python",
    the inference engine will walk this graph and infer Python with high
    confidence because 3 Python-prerequisite skills are present.
"""

# ---------------------------------------------------------------------------
# PREREQUISITE GRAPH
# Child skill → primary parent skill (knowing the child implies knowing the parent)
# ---------------------------------------------------------------------------

PREREQUISITE_GRAPH = {
    # ---- Python ecosystem ----
    "django": "python",
    "flask": "python",
    "fastapi": "python",
    "pandas": "python",
    "numpy": "python",
    "scipy": "python",
    "scikit-learn": "python",
    "tensorflow": "python",
    "pytorch": "python",
    "keras": "python",
    "xgboost": "python",
    "lightgbm": "python",
    "catboost": "python",
    "pytest": "python",
    "celery": "python",
    "streamlit": "python",
    "gradio": "python",
    "langchain": "python",
    "transformers": "python",
    "huggingface": "python",
    "mlflow": "python",
    "airflow": "python",

    # ---- JavaScript ecosystem ----
    "react": "javascript",
    "angular": "javascript",
    "vue": "javascript",
    "svelte": "javascript",
    "node.js": "javascript",
    "next.js": "javascript",
    "nuxt.js": "javascript",
    "nest.js": "javascript",
    "express": "javascript",
    "redux": "javascript",
    "mobx": "javascript",
    "jquery": "javascript",
    "jest": "javascript",
    "mocha": "javascript",
    "cypress": "javascript",
    "webpack": "javascript",
    "babel": "javascript",

    # ---- TypeScript ecosystem ----
    # Note: TypeScript is a superset of JavaScript, so TS implies JS
    "typescript": "javascript",

    # ---- Java ecosystem ----
    "spring": "java",
    "spring boot": "java",
    "hibernate": "java",
    "junit": "java",
    "testng": "java",
    "maven": "java",
    "gradle": "java",

    # ---- Ruby ecosystem ----
    "rails": "ruby",
    "ruby on rails": "ruby",

    # ---- PHP ecosystem ----
    "laravel": "php",
    "symfony": "php",

    # ---- C# ecosystem ----
    "asp.net": "c#",
    ".net": "c#",

    # ---- Mobile ----
    "swiftui": "swift",
    "react native": "javascript",
    "flutter": "dart",

    # ---- Container orchestration ----
    "kubernetes": "docker",
    "openshift": "kubernetes",
    "helm": "kubernetes",
    "argocd": "kubernetes",
    "rancher": "kubernetes",

    # ---- Cloud ----
    "ec2": "aws",
    "s3": "aws",
    "lambda": "aws",
    "rds": "aws",
    "dynamodb": "aws",
    "cloudformation": "aws",
    "cloudfront": "aws",
    "route53": "aws",
    "eks": "aws",
    "ecs": "aws",
    "fargate": "aws",

    # ---- Infrastructure as Code ----
    "terraform": "cloud computing",
    "ansible": "devops",
    "chef": "devops",
    "puppet": "devops",

    # ---- CI/CD ----
    "jenkins": "ci/cd",
    "github actions": "ci/cd",
    "gitlab": "ci/cd",
    "circleci": "ci/cd",
    "travis ci": "ci/cd",
    "tekton": "ci/cd",

    # ---- Monitoring ----
    "prometheus": "monitoring",
    "grafana": "monitoring",
    "datadog": "monitoring",
    "new relic": "monitoring",
    "sentry": "monitoring",
    "elk": "monitoring",
    "kibana": "elk",
    "logstash": "elk",

    # ---- Databases (specific → general concept) ----
    "mysql": "sql",
    "postgresql": "sql",
    "sqlite": "sql",
    "oracle": "sql",
    "sql server": "sql",
    "mariadb": "sql",

    "mongodb": "nosql",
    "redis": "nosql",
    "cassandra": "nosql",
    "couchdb": "nosql",
    "neo4j": "nosql",
    "firestore": "nosql",

    # ---- Big Data ----
    "spark": "big data",
    "hadoop": "big data",
    "kafka": "big data",
    "hive": "big data",
    "pig": "big data",
    "presto": "big data",
    "databricks": "big data",
    "flink": "big data",

    # ---- Testing concepts ----
    "selenium": "integration testing",

    # ---- Methodologies ----
    "scrum": "agile",
    "kanban": "agile",

    # ---- Shell / OS ----
    "bash": "linux",
    "shell scripting": "linux",
    "powershell": "windows",

    # ---- API concepts ----
    "rest": "api",
    "graphql": "api",
    "grpc": "api",
    "soap": "api",
    "websocket": "api",
    "swagger": "api",
    "openapi": "api",

    # ---- Architecture ----
    "microservices": "system design",
    "serverless": "system design",
    "event-driven": "system design",
    "cqrs": "system design",
    "ddd": "system design",
    "domain-driven design": "system design",
}

ADDITIONAL_PREREQUISITES = {
    "tensorflow": ("deep learning",),
    "pytorch": ("deep learning",),
    "keras": ("deep learning",),
    "scikit-learn": ("machine learning",),
    "xgboost": ("machine learning",),
    "lightgbm": ("machine learning",),
    "catboost": ("machine learning",),
    "pandas": ("data science",),
    "numpy": ("data science",),
    "scipy": ("data science",),
    "pytest": ("unit testing",),
    "jest": ("unit testing",),
    "mocha": ("unit testing",),
    "cypress": ("integration testing",),
    "junit": ("unit testing",),
    "argocd": ("ci/cd",),
    "dynamodb": ("nosql",),
}


# ---------------------------------------------------------------------------
# SKILL CATEGORIES
# Each skill is tagged with ONE primary category for taxonomy purposes
# ---------------------------------------------------------------------------

SKILL_CATEGORIES = {
    # Programming Languages
    "python": "Programming Languages",
    "java": "Programming Languages",
    "javascript": "Programming Languages",
    "typescript": "Programming Languages",
    "c++": "Programming Languages",
    "c#": "Programming Languages",
    "c": "Programming Languages",
    "go": "Programming Languages",
    "rust": "Programming Languages",
    "ruby": "Programming Languages",
    "php": "Programming Languages",
    "swift": "Programming Languages",
    "kotlin": "Programming Languages",
    "scala": "Programming Languages",
    "r": "Programming Languages",
    "dart": "Programming Languages",
    "perl": "Programming Languages",

    # Web Frameworks (Frontend)
    "react": "Web Frameworks",
    "angular": "Web Frameworks",
    "vue": "Web Frameworks",
    "svelte": "Web Frameworks",
    "next.js": "Web Frameworks",
    "nuxt.js": "Web Frameworks",
    "jquery": "Web Frameworks",
    "redux": "Web Frameworks",
    "mobx": "Web Frameworks",
    "html": "Web Frameworks",
    "css": "Web Frameworks",
    "sass": "Web Frameworks",
    "scss": "Web Frameworks",
    "tailwind": "Web Frameworks",
    "bootstrap": "Web Frameworks",

    # Web Frameworks (Backend)
    "django": "Web Frameworks",
    "flask": "Web Frameworks",
    "fastapi": "Web Frameworks",
    "express": "Web Frameworks",
    "spring": "Web Frameworks",
    "spring boot": "Web Frameworks",
    "rails": "Web Frameworks",
    "laravel": "Web Frameworks",
    "symfony": "Web Frameworks",
    "asp.net": "Web Frameworks",
    "node.js": "Web Frameworks",
    "nest.js": "Web Frameworks",

    # Mobile
    "react native": "Mobile",
    "flutter": "Mobile",
    "android": "Mobile",
    "ios": "Mobile",
    "xamarin": "Mobile",
    "ionic": "Mobile",
    "swiftui": "Mobile",

    # Data Science & ML
    "pandas": "Data Science",
    "numpy": "Data Science",
    "scipy": "Data Science",
    "data science": "Data Science",
    "statistics": "Data Science",
    "machine learning": "ML/DL",
    "scikit-learn": "ML/DL",
    "xgboost": "ML/DL",
    "lightgbm": "ML/DL",
    "catboost": "ML/DL",
    "deep learning": "ML/DL",
    "tensorflow": "ML/DL",
    "pytorch": "ML/DL",
    "keras": "ML/DL",
    "neural networks": "ML/DL",
    "nlp": "ML/DL",
    "computer vision": "ML/DL",
    "transformers": "ML/DL",
    "huggingface": "ML/DL",
    "langchain": "ML/DL",
    "mlflow": "ML/DL",

    # Cloud
    "aws": "Cloud",
    "azure": "Cloud",
    "gcp": "Cloud",
    "google cloud": "Cloud",
    "heroku": "Cloud",
    "digitalocean": "Cloud",
    "cloudflare": "Cloud",
    "vercel": "Cloud",
    "netlify": "Cloud",
    "cloud computing": "Cloud",
    "ec2": "Cloud",
    "s3": "Cloud",
    "lambda": "Cloud",
    "rds": "Cloud",
    "eks": "Cloud",
    "ecs": "Cloud",
    "fargate": "Cloud",

    # DevOps
    "docker": "DevOps",
    "kubernetes": "DevOps",
    "jenkins": "DevOps",
    "ansible": "DevOps",
    "terraform": "DevOps",
    "chef": "DevOps",
    "puppet": "DevOps",
    "helm": "DevOps",
    "argocd": "DevOps",
    "github actions": "DevOps",
    "circleci": "DevOps",
    "travis ci": "DevOps",
    "ci/cd": "DevOps",
    "devops": "DevOps",
    "openshift": "DevOps",
    "rancher": "DevOps",

    # Databases
    "sql": "Databases",
    "mysql": "Databases",
    "postgresql": "Databases",
    "sqlite": "Databases",
    "oracle": "Databases",
    "sql server": "Databases",
    "mariadb": "Databases",
    "nosql": "Databases",
    "mongodb": "Databases",
    "redis": "Databases",
    "cassandra": "Databases",
    "couchdb": "Databases",
    "neo4j": "Databases",
    "dynamodb": "Databases",
    "firestore": "Databases",

    # Big Data
    "spark": "Big Data",
    "hadoop": "Big Data",
    "kafka": "Big Data",
    "airflow": "Big Data",
    "hive": "Big Data",
    "databricks": "Big Data",
    "big data": "Big Data",

    # Testing
    "pytest": "Testing",
    "unittest": "Testing",
    "jest": "Testing",
    "mocha": "Testing",
    "selenium": "Testing",
    "cypress": "Testing",
    "junit": "Testing",
    "testng": "Testing",
    "unit testing": "Testing",
    "integration testing": "Testing",
    "tdd": "Testing",
    "bdd": "Testing",

    # APIs
    "rest": "APIs",
    "graphql": "APIs",
    "grpc": "APIs",
    "soap": "APIs",
    "websocket": "APIs",
    "api": "APIs",
    "swagger": "APIs",
    "openapi": "APIs",

    # OS / Scripting
    "linux": "OS/Scripting",
    "unix": "OS/Scripting",
    "ubuntu": "OS/Scripting",
    "windows": "OS/Scripting",
    "macos": "OS/Scripting",
    "bash": "OS/Scripting",
    "powershell": "OS/Scripting",
    "shell scripting": "OS/Scripting",

    # Monitoring
    "prometheus": "Monitoring",
    "grafana": "Monitoring",
    "datadog": "Monitoring",
    "new relic": "Monitoring",
    "sentry": "Monitoring",
    "elk": "Monitoring",
    "kibana": "Monitoring",
    "logstash": "Monitoring",
    "splunk": "Monitoring",
    "monitoring": "Monitoring",

    # Security
    "oauth": "Security",
    "jwt": "Security",
    "saml": "Security",
    "ssl": "Security",
    "tls": "Security",
    "encryption": "Security",
    "security": "Security",
    "cybersecurity": "Security",

    # Version Control
    "git": "Version Control",
    "github": "Version Control",
    "gitlab": "Version Control",
    "bitbucket": "Version Control",

    # Methodologies
    "agile": "Methodologies",
    "scrum": "Methodologies",
    "kanban": "Methodologies",
    "waterfall": "Methodologies",
    "system design": "Methodologies",
    "microservices": "Methodologies",
    "serverless": "Methodologies",
}


# ---------------------------------------------------------------------------
# CATEGORY → SKILLS (reverse mapping, built automatically)
# ---------------------------------------------------------------------------

def _build_category_skills():
    """Build reverse mapping from category to list of skills."""
    result = {}
    for skill, category in SKILL_CATEGORIES.items():
        result.setdefault(category, []).append(skill)
    return result


CATEGORY_SKILLS = _build_category_skills()


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def get_parent(skill):
    """Return the primary parent skill, or None if the skill is unknown."""
    return PREREQUISITE_GRAPH.get(skill)


def get_parents(skill):
    """Return the primary and additional parent skills for a skill."""
    primary_parent = get_parent(skill)
    if primary_parent is None:
        return ()
    return (primary_parent, *ADDITIONAL_PREREQUISITES.get(skill, ()))


def get_children(parent_skill):
    """Return all skills that have the given prerequisite parent."""
    return [
        child for child in PREREQUISITE_GRAPH
        if parent_skill in get_parents(child)
    ]


def get_category(skill):
    """Return the category of a skill, or 'Other' if not categorized."""
    return SKILL_CATEGORIES.get(skill, "Other")


def get_all_categories():
    """Return list of all defined categories."""
    return sorted(set(SKILL_CATEGORIES.values()))


def get_all_parents():
    """Return all parent skills (skills that have at least one child in the graph)."""
    return sorted({
        parent
        for skill in PREREQUISITE_GRAPH
        for parent in get_parents(skill)
    })