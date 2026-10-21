# API Documentation

Base URL: `http://localhost:8000`  
Interactive API reference: `http://localhost:8000/docs` (Swagger UI)

All matching endpoints accept PDF files and a job description as
`multipart/form-data`. The maximum resume size is 5 MB. Files must start with
the PDF signature (`%PDF`).

Supported matching modes for `/match-single` and `/match-bulk`:

- `baseline` (default): keyword, skill overlap, and TF-IDF scoring.
- `enhanced`: skill inference, credibility, semantic similarity, and
  section-aware scoring.
- `learned`: uses the trained scorer when available; otherwise falls back to
  enhanced scoring and includes a `warning`.

## `GET /health`

Health check.

**Response (`200`):**

```json
{
  "status": "ok",
  "version": "2.0.0"
}
```

## `POST /match-single`

Compare one resume with a job description.

**Form fields:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `resume_file` | PDF file | Yes | — | Resume to analyze; maximum 5 MB |
| `job_description` | string | Yes | — | Job description text |
| `mode` | string | No | `baseline` | `baseline`, `enhanced`, or `learned` |

**Example:**

```bash
curl -X POST http://localhost:8000/match-single \
  -F "resume_file=@resume.pdf" \
  -F "job_description=Python developer with Django experience" \
  -F "mode=enhanced"
```

**Successful response (`200`):** A match result containing `score` (0–100),
`breakdown`, `matched_skills`, `missing_skills`, and `mode`. Enhanced and
learned responses also include inference, credibility, category, and section
similarity details. If the PDF contains no extractable text, the response
contains a `warning` and empty skill lists.

**Errors:** `400` for a file over 5 MB or an invalid PDF signature; `500` if
PDF parsing fails; `422` if required form fields are missing or invalid.

## `POST /match-bulk`

Compare multiple resumes with the same job description.

**Form fields:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `resume_files` | PDF files | Yes | — | One or more resumes; each maximum 5 MB |
| `job_description` | string | Yes | — | Job description text used for every resume |
| `mode` | string | No | `baseline` | `baseline`, `enhanced`, or `learned` |

**Example:**

```bash
curl -X POST http://localhost:8000/match-bulk \
  -F "resume_files=@resume-1.pdf" \
  -F "resume_files=@resume-2.pdf" \
  -F "job_description=Python developer with Django experience" \
  -F "mode=enhanced"
```

**Successful response (`200`):**

```json
{
  "results": [
    {
      "filename": "resume-1.pdf",
      "score": 74.2,
      "breakdown": {},
      "matched_skills": ["django", "python"],
      "missing_skills": [],
      "mode": "enhanced"
    }
  ]
}
```

The breakdown and additional fields depend on the selected mode. A resume
that fails validation or parsing is returned in the `results` array with a
`filename`, `score: 0`, and an `error` (or `warning` for a PDF with no
extractable text); it does not fail the entire bulk request.

**Errors:** `422` if required form fields are missing or invalid.

## `POST /analyze`

Run full dashboard analysis for one resume. This endpoint always uses
`enhanced` matching, regardless of the optional `mode` form value.

**Form fields:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `resume_file` | PDF file | Yes | — | Resume to analyze; maximum 5 MB |
| `job_description` | string | Yes | — | Job description text |
| `mode` | string | No | `enhanced` | Accepted for compatibility; analysis always uses enhanced mode |

**Example:**

```bash
curl -X POST http://localhost:8000/analyze \
  -F "resume_file=@resume.pdf" \
  -F "job_description=Python developer with Django experience"
```

**Successful response (`200`):** An enhanced match result plus:

- `recommendations`: up to six actionable suggestions. Each has `title`,
  `description`, `priority`, `resource_name`, and `resource_url`.
- `sections_detected`: names of the sections extracted from the resume.

If the PDF contains no extractable text, the endpoint returns a zero score,
empty skill lists and recommendations, and a `warning`.

**Errors:** `400` for a file over 5 MB or an invalid PDF signature; `500` if
PDF parsing fails; `422` if required form fields are missing or invalid.
