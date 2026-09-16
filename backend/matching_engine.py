import re


# Skills that our system can recognize
SKILLS = [
    "python",
    "java",
    "c++",
    "c#",
    "javascript",
    "typescript",
    "react",
    "angular",
    "vue",
    "node.js",
    "express",
    "html",
    "css",
    "bootstrap",
    "tailwind",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "redis",
    "git",
    "github",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "machine learning",
    "deep learning",
    "tensorflow",
    "pytorch",
    "pandas",
    "numpy",
    "scikit-learn",
    "data analysis",
    "rest api",
    "fastapi",
    "django",
    "flask",
    "spring boot",
]


def normalize_text(text):
    """
    Convert text into a cleaner lowercase form.
    """
    text = text.lower()

    # Replace multiple spaces/newlines with one space
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_skills(text):
    """
    Find known skills present in the given text.
    """

    text = normalize_text(text)

    found_skills = []

    for skill in SKILLS:

        # Escape special characters such as C++
        pattern = r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)"

        if re.search(pattern, text):
            found_skills.append(skill)

    return found_skills


def calculate_match(resume_text, job_description):
    """
    Calculate how well a resume matches a job description.

    Score =
        matched required skills
        ----------------------- × 100
        total required skills
    """

    resume_skills = set(extract_skills(resume_text))
    required_skills = set(extract_skills(job_description))

    # If JD contains no recognizable skills
    if not required_skills:
        return {
            "score": 0,
            "matched_skills": [],
            "missing_skills": [],
        }

    matched_skills = resume_skills.intersection(required_skills)
    missing_skills = required_skills - resume_skills

    score = (len(matched_skills) / len(required_skills)) * 100

    return {
        "score": round(score, 2),
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
    }