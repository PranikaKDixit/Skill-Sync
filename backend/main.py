"""
SkillSync Backend — FastAPI server.
Handles resume upload, JD matching (baseline + enhanced).
"""
import os
from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ml.matching_engine import calculate_match
from pdf_parsing.pdf_parser import extract_text_from_pdf

app = FastAPI(title="SkillSync API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


@app.post("/match-single")
async def match_single(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...),
    mode: str = Query("baseline"),
):
    # Validate file size
    content = await resume_file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 5MB)")

    # Validate PDF magic bytes
    if not content[:5].startswith(b"%PDF"):
        raise HTTPException(400, "Not a valid PDF file")

    # Parse PDF (now returns sections too)
    parsed = extract_text_from_pdf(content)

    if parsed["status"] == "error":
        raise HTTPException(500, f"PDF parsing failed: {parsed['error']}")

    if parsed["status"] == "empty":
        return {
            "score": 0,
            "breakdown": {},
            "matched_skills": [],
            "missing_skills": [],
            "mode": mode,
            "warning": parsed["error"],
        }

    # Calculate match (pass sections for enhanced mode)
    result = calculate_match(
        resume_text=parsed["text"],
        jd_text=job_description,
        mode=mode,
        resume_sections=parsed.get("sections"),
    )

    return result


@app.post("/match-bulk")
async def match_bulk(
    resume_files: list[UploadFile] = File(...),
    job_description: str = Form(...),
    mode: str = Form("baseline"),
):
    results = []
    for rf in resume_files:
        content = await rf.read()
        if len(content) > MAX_FILE_SIZE:
            results.append({
                "filename": rf.filename,
                "score": 0,
                "error": "File too large",
            })
            continue

        if not content[:5].startswith(b"%PDF"):
            results.append({
                "filename": rf.filename,
                "score": 0,
                "error": "Not a valid PDF",
            })
            continue

        parsed = extract_text_from_pdf(content)

        if parsed["status"] == "error":
            results.append({
                "filename": rf.filename,
                "score": 0,
                "error": parsed["error"],
            })
            continue

        if parsed["status"] == "empty":
            results.append({
                "filename": rf.filename,
                "score": 0,
                "warning": parsed["error"],
                "breakdown": {},
                "matched_skills": [],
                "missing_skills": [],
            })
            continue

        match_result = calculate_match(
            resume_text=parsed["text"],
            jd_text=job_description,
            mode=mode,
            resume_sections=parsed.get("sections"),
        )
        match_result["filename"] = rf.filename
        results.append(match_result)

    return {"results": results}

from ml.recommendations import generate_recommendations


@app.post("/analyze")
async def analyze(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...),
    mode: str = Query("enhanced"),
):
    """
    Full analysis endpoint for the dashboard.
    Returns match result + recommendations + chart-ready data.
    """
    content = await resume_file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 5MB)")
    if not content[:5].startswith(b"%PDF"):
        raise HTTPException(400, "Not a valid PDF file")

    parsed = extract_text_from_pdf(content)
    if parsed["status"] == "error":
        raise HTTPException(500, f"PDF parsing failed: {parsed['error']}")
    if parsed["status"] == "empty":
        return {
            "score": 0, "breakdown": {}, "matched_skills": [],
            "missing_skills": [], "mode": mode,
            "warning": parsed["error"], "recommendations": [],
        }

    # Force enhanced mode for full analysis
    result = calculate_match(
        resume_text=parsed["text"],
        jd_text=job_description,
        mode="enhanced",
        resume_sections=parsed.get("sections"),
    )

    # Generate recommendations
    recs = generate_recommendations(result, parsed["text"], job_description)
    result["recommendations"] = recs

    # Add section data for charts
    result["sections_detected"] = list(parsed.get("sections", {}).keys())

    return result