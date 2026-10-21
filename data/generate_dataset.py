"""
Generate 100 labeled resume-JD pairs for training and evaluation.
Each pair gets a human-like score (0-100) based on domain match
and skill overlap, with Gaussian noise to simulate annotator variance.

Run: python data/generate_dataset.py
Output: data/evaluation_dataset.csv
"""
import csv
import random
import os

random.seed(42)

RESUMES = {
    "python_backend": {
        "text": (
            "SKILLS\nPython, Django, Flask, PostgreSQL, Redis, Docker, Git, REST API, Linux\n"
            "EXPERIENCE\nBackend Developer at TechCorp (2021-2024)\n"
            "- Built RESTful APIs using Django REST Framework serving 1M+ requests daily\n"
            "- Designed PostgreSQL database schemas and optimized slow queries\n"
            "- Deployed microservices using Docker and CI/CD pipelines\n"
            "EDUCATION\nB.Tech Computer Science, NIT Trichy (2017-2021)"
        ),
        "domain": "backend",
    },
    "react_frontend": {
        "text": (
            "SKILLS\nJavaScript, React, TypeScript, HTML, CSS, Redux, Webpack, Jest, Figma\n"
            "EXPERIENCE\nFrontend Developer at DesignHub (2022-2024)\n"
            "- Built responsive SPAs using React and TypeScript\n"
            "- Implemented state management with Redux Toolkit\n"
            "- Improved Lighthouse performance score from 45 to 92\n"
            "EDUCATION\nB.Tech IT, VIT Vellore (2018-2022)"
        ),
        "domain": "frontend",
    },
    "data_scientist": {
        "text": (
            "SKILLS\nPython, Pandas, NumPy, scikit-learn, TensorFlow, SQL, Matplotlib, Jupyter, Statistics\n"
            "EXPERIENCE\nData Scientist at AnalyticsCo (2021-2024)\n"
            "- Built customer churn prediction model with 94% accuracy using scikit-learn\n"
            "- Developed ETL pipelines processing 10M+ records daily with Pandas\n"
            "- Created interactive dashboards for stakeholder reporting\n"
            "EDUCATION\nM.Tech Data Science, IIT Hyderabad (2019-2021)"
        ),
        "domain": "data",
    },
    "devops_engineer": {
        "text": (
            "SKILLS\nDocker, Kubernetes, AWS, Terraform, Jenkins, Linux, Bash, Prometheus, Grafana\n"
            "EXPERIENCE\nDevOps Engineer at CloudFirst (2020-2024)\n"
            "- Managed Kubernetes clusters with 200+ pods on AWS EKS\n"
            "- Automated infrastructure provisioning using Terraform\n"
            "- Set up CI/CD pipelines with Jenkins reducing deployment time by 60%\n"
            "EDUCATION\nB.Tech Computer Science, BITS Pilani (2016-2020)"
        ),
        "domain": "devops",
    },
    "java_enterprise": {
        "text": (
            "SKILLS\nJava, Spring Boot, Hibernate, MySQL, Maven, JUnit, Kafka, Microservices\n"
            "EXPERIENCE\nSoftware Engineer at BankTech (2020-2024)\n"
            "- Developed microservices architecture using Spring Boot and Kafka\n"
            "- Implemented event-driven processing handling 500K transactions daily\n"
            "- Wrote comprehensive unit tests with JUnit achieving 90% coverage\n"
            "EDUCATION\nB.Tech Computer Science, DTU Delhi (2016-2020)"
        ),
        "domain": "backend",
    },
    "mobile_developer": {
        "text": (
            "SKILLS\nFlutter, Dart, React Native, Firebase, REST API, Git, Android, iOS\n"
            "EXPERIENCE\nMobile Developer at AppWorks (2022-2024)\n"
            "- Built cross-platform mobile apps using Flutter with 100K+ downloads\n"
            "- Integrated Firebase for authentication, push notifications, and analytics\n"
            "- Published 5 apps on both Google Play Store and Apple App Store\n"
            "EDUCATION\nB.Tech ECE, SRM Chennai (2018-2022)"
        ),
        "domain": "mobile",
    },
    "fullstack_mern": {
        "text": (
            "SKILLS\nJavaScript, React, Node.js, Express, MongoDB, TypeScript, Docker, GraphQL\n"
            "EXPERIENCE\nFull Stack Developer at StartupXYZ (2021-2024)\n"
            "- Built end-to-end SaaS platform using MERN stack serving 50K users\n"
            "- Designed GraphQL API layer reducing frontend data fetching by 40%\n"
            "- Implemented real-time features using WebSockets and Redis\n"
            "EDUCATION\nB.Tech Computer Science, IIIT Bangalore (2017-2021)"
        ),
        "domain": "fullstack",
    },
    "ml_engineer": {
        "text": (
            "SKILLS\nPython, PyTorch, TensorFlow, scikit-learn, MLflow, Docker, AWS SageMaker, NLP\n"
            "EXPERIENCE\nML Engineer at DeepTech (2021-2024)\n"
            "- Trained and deployed NLP models for sentiment analysis using PyTorch\n"
            "- Built ML pipeline with MLflow for experiment tracking and model versioning\n"
            "- Deployed models on AWS SageMaker serving 10K predictions per minute\n"
            "EDUCATION\nM.Tech AI, IISc Bangalore (2019-2021)"
        ),
        "domain": "ml",
    },
    "cloud_architect": {
        "text": (
            "SKILLS\nAWS, Azure, GCP, Terraform, Kubernetes, Docker, Python, Networking, Security\n"
            "EXPERIENCE\nCloud Architect at InfraScale (2019-2024)\n"
            "- Designed multi-cloud architecture across AWS, Azure, and GCP\n"
            "- Migrated legacy monolith to microservices on Kubernetes\n"
            "- Reduced cloud infrastructure costs by 35% through optimization\n"
            "EDUCATION\nB.Tech Computer Science, IIT Roorkee (2015-2019)"
        ),
        "domain": "cloud",
    },
    "fresh_graduate": {
        "text": (
            "SKILLS\nC, C++, Python, HTML, CSS, JavaScript, SQL, Git, Data Structures\n"
            "EXPERIENCE\nIntern at WebDev Solutions (Summer 2023)\n"
            "- Built a student management portal using HTML, CSS, and JavaScript\n"
            "- Created REST API endpoints using Python Flask\n"
            "PROJECTS\nLibrary Management System using C++ and file handling\n"
            "EDUCATION\nB.Tech Computer Science, ABC University (2020-2024) CGPA: 7.8"
        ),
        "domain": "general",
    },
}

JDS = {
    "senior_python": {
        "text": (
            "Senior Python Developer needed with 4+ years of experience.\n"
            "Required: Python, Django, PostgreSQL, Docker, REST APIs, Git.\n"
            "Preferred: AWS, Redis, Celery, CI/CD.\n"
            "You will build scalable backend services and mentor junior developers."
        ),
        "domain": "backend",
    },
    "frontend_engineer": {
        "text": (
            "Frontend Engineer to build modern web interfaces.\n"
            "Required: JavaScript, React, TypeScript, HTML, CSS.\n"
            "Preferred: Redux, Webpack, Jest, Figma, accessibility.\n"
            "You will work closely with designers to implement pixel-perfect UIs."
        ),
        "domain": "frontend",
    },
    "data_scientist_jd": {
        "text": (
            "Data Scientist to drive data-driven decision making.\n"
            "Required: Python, Pandas, scikit-learn, SQL, Statistics.\n"
            "Preferred: TensorFlow, deep learning, A/B testing, Tableau.\n"
            "You will build predictive models and present insights to leadership."
        ),
        "domain": "data",
    },
    "devops_sre": {
        "text": (
            "DevOps/SRE Engineer to maintain cloud infrastructure.\n"
            "Required: Docker, Kubernetes, AWS, Linux, CI/CD.\n"
            "Preferred: Terraform, Prometheus, Grafana, Python scripting.\n"
            "You will ensure 99.99% uptime and automate deployment pipelines."
        ),
        "domain": "devops",
    },
    "java_backend": {
        "text": (
            "Java Backend Developer for enterprise applications.\n"
            "Required: Java, Spring Boot, MySQL, Hibernate, REST APIs.\n"
            "Preferred: Kafka, microservices, JUnit, Maven, Docker.\n"
            "You will build high-throughput transaction processing systems."
        ),
        "domain": "backend",
    },
    "mobile_dev_jd": {
        "text": (
            "Mobile App Developer for cross-platform applications.\n"
            "Required: Flutter or React Native, REST APIs, Git.\n"
            "Preferred: Firebase, Android, iOS, app store deployment.\n"
            "You will build consumer-facing mobile apps with millions of users."
        ),
        "domain": "mobile",
    },
    "fullstack_jd": {
        "text": (
            "Full Stack Developer for SaaS product.\n"
            "Required: JavaScript, React, Node.js, MongoDB, REST APIs.\n"
            "Preferred: TypeScript, Docker, GraphQL, AWS.\n"
            "You will own features end-to-end from database to UI."
        ),
        "domain": "fullstack",
    },
    "ml_engineer_jd": {
        "text": (
            "ML Engineer to build and deploy production ML systems.\n"
            "Required: Python, PyTorch or TensorFlow, scikit-learn, Docker.\n"
            "Preferred: MLflow, AWS SageMaker, NLP, computer vision.\n"
            "You will take models from research to production at scale."
        ),
        "domain": "ml",
    },
    "cloud_engineer": {
        "text": (
            "Cloud Engineer to design and manage cloud infrastructure.\n"
            "Required: AWS, Docker, Kubernetes, Terraform, Linux.\n"
            "Preferred: Azure, GCP, Python, networking, security.\n"
            "You will build scalable, secure, and cost-effective cloud solutions."
        ),
        "domain": "cloud",
    },
    "intern_jd": {
        "text": (
            "Software Engineering Intern (6 months).\n"
            "Required: Python or Java, basic data structures, Git.\n"
            "Preferred: HTML, CSS, SQL, any web framework.\n"
            "You will work on real projects with mentorship from senior engineers."
        ),
        "domain": "general",
    },
}

DOMAIN_AFFINITY = {
    ("backend", "backend"): 1.0, ("backend", "fullstack"): 0.7,
    ("backend", "general"): 0.5, ("frontend", "frontend"): 1.0,
    ("frontend", "fullstack"): 0.7, ("frontend", "general"): 0.4,
    ("data", "data"): 1.0, ("data", "ml"): 0.8, ("data", "general"): 0.4,
    ("devops", "devops"): 1.0, ("devops", "cloud"): 0.8,
    ("devops", "general"): 0.3, ("mobile", "mobile"): 1.0,
    ("mobile", "general"): 0.3, ("fullstack", "fullstack"): 1.0,
    ("fullstack", "frontend"): 0.7, ("fullstack", "backend"): 0.7,
    ("fullstack", "general"): 0.5, ("ml", "ml"): 1.0,
    ("ml", "data"): 0.8, ("ml", "general"): 0.3,
    ("cloud", "cloud"): 1.0, ("cloud", "devops"): 0.8,
    ("cloud", "general"): 0.3, ("general", "general"): 0.7,
    ("general", "backend"): 0.3, ("general", "frontend"): 0.3,
}


def compute_score(resume, jd):
    r_domain, j_domain = resume["domain"], jd["domain"]
    domain_score = DOMAIN_AFFINITY.get(
        (r_domain, j_domain),
        DOMAIN_AFFINITY.get((j_domain, r_domain), 0.2),
    )
    stop = {"the", "a", "an", "and", "or", "of", "to", "in", "for",
            "with", "you", "will", "on", "at", "by", "from", "as", "is"}
    r_words = set(resume["text"].lower().split()) - stop
    j_words = set(jd["text"].lower().split()) - stop
    overlap = len(r_words & j_words) / max(len(j_words), 1)
    overlap_score = min(1.0, overlap * 3)
    raw = 0.55 * domain_score + 0.45 * overlap_score
    score = raw * 100 + random.gauss(0, 8)
    return round(max(0, min(100, score)), 1)


def main():
    output_path = os.path.join(os.path.dirname(__file__), "evaluation_dataset.csv")
    rows = []
    pair_id = 1
    for r_name, resume in RESUMES.items():
        for j_name, jd in JDS.items():
            rows.append({
                "id": pair_id,
                "resume_profile": r_name,
                "jd_profile": j_name,
                "resume_text": resume["text"],
                "jd_text": jd["text"],
                "human_score": compute_score(resume, jd),
            })
            pair_id += 1

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "resume_profile", "jd_profile",
            "resume_text", "jd_text", "human_score"
        ])
        writer.writeheader()
        writer.writerows(rows)

    scores = [r["human_score"] for r in rows]
    print(f"Generated {len(rows)} pairs -> {output_path}")
    print(f"Score range: {min(scores):.1f} - {max(scores):.1f}, "
          f"mean: {sum(scores)/len(scores):.1f}")


if __name__ == "__main__":
    main()