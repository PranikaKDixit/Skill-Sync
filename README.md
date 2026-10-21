# SkillSync: Intelligent Resume–Job Matching System

An intelligent resume–job matching system with ontology-based skill inference,
semantic similarity, and evidence-weighted credibility scoring.

**B.Tech Major Project** — Computer Science & Engineering

## What It Does

SkillSync takes a resume (PDF) and a job description, then produces a
**similarity score (0–100)** with a full explanation of *why* that score
was assigned.

Unlike simple keyword matchers, SkillSync:

- **Infers implicit skills** — a resume listing Django, Pandas, and
  scikit-learn is recognized as having Python experience, even if the
  word "Python" never appears
- **Understands meaning** — "machine learning pipelines" matches
  "ML model development" using Sentence-BERT embeddings
- **Weighs evidence** — a skill mentioned once in a job title scores
  lower than one demonstrated across multiple projects with specific metrics
- **Learns from data** — a GradientBoosting model trained on 100 labeled
  pairs discovers the optimal combination of matching signals

## What It Does NOT Do

To be clear and honest:

- It does **not** predict hiring outcomes or candidate quality
- It does **not** use large language models (no GPT, no LLM API calls)
- It does **not** claim novel ML contributions — it applies established
  techniques (SBERT, TF-IDF, gradient boosting) in a well-engineered pipeline
- It does **not** replace human judgment in hiring

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML, CSS, JavaScript, Chart.js |
| Backend | FastAPI (Python) |
| ML/NLP | scikit-learn, Sentence-BERT (all-MiniLM-L6-v2), PyTorch (CPU) |
| PDF Parsing | pypdf |
| Containerization | Docker, Docker Compose, Nginx |

## Quick Start

### Prerequisites
- Docker Desktop installed and running
- 4GB+ free RAM (for SBERT model)
- Internet connection (first run downloads ~220MB of ML models)

### Run

```bash
# Clone and start
git clone <your-repo-url>
cd skillsync
docker compose up --build

# First-time setup (inside container)
docker compose exec -w /app backend python data/generate_dataset.py
docker compose exec -w /app backend python -m ml.train