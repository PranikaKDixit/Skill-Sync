from typing import Annotated
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

import os
import sys
import uuid
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import from actual modules (no copies!)
from ml.matching_engine import calculate_match
from pdf_parsing.pdf_parser import extract_text_from_pdf


app = FastAPI(
    title="SkillSync Resume Matching API",
    description="API for matching multiple resumes against a job description",
    version="1.0.0"
)

# ... rest of the file stays the same
app.openapi_version = "3.0.3"

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Fix Swagger UI file upload schema
    try:
        body_schema = openapi_schema["components"]["schemas"][
            "Body_match_bulk_match_bulk_post"
        ]

        body_schema["properties"]["resume_files"]["items"] = {
            "type": "string",
            "format": "binary"
        }

    except KeyError:
        pass

    openapi_schema["openapi"] = "3.0.3"

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# -------------------------
# CORS
# -------------------------

app.add_middleware(
    CORSMiddleware,

    # Vite usually runs on 5173
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000"
    ],

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# Upload folder
# -------------------------

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


# -------------------------
# Root route
# -------------------------

@app.get("/")
def root():

    return {
        "message": "SkillSync Resume Matching Backend is running"
    }


# -------------------------
# MATCH BULK
# -------------------------

@app.post("/match-bulk")
async def match_bulk(
    resume_files: Annotated[list[UploadFile], File(...)],
    job_description: Annotated[str, Form(...)]
):

    # -------------------------
    # 1. Validate files
    # -------------------------

    if not resume_files:

        raise HTTPException(
            status_code=400,
            detail="No resume files uploaded"
        )


    # -------------------------
    # 2. Validate JD
    # -------------------------

    if not job_description.strip():

        raise HTTPException(
            status_code=400,
            detail="Job description is required"
        )


    results = []


    # -------------------------
    # 3. Process every resume
    # -------------------------

    for file in resume_files:

        # -------------------------
        # Check file type
        # -------------------------

        if file.content_type != "application/pdf":

            results.append({
                "filename": file.filename,
                "status": "failed",
                "error": "File must be a PDF"
            })

            continue


        # -------------------------
        # Generate unique filename
        # -------------------------

        unique_name = f"{uuid.uuid4()}_{file.filename}"

        file_path = os.path.join(
            UPLOAD_DIR,
            unique_name
        )


        try:

            # -------------------------
            # 4. Save PDF temporarily
            # -------------------------

            file_content = await file.read()

            with open(file_path, "wb") as buffer:

                buffer.write(file_content)


            # -------------------------
            # 5. Extract resume text
            # -------------------------

            resume_text = extract_text_from_pdf(
                file_path
            )


            if not resume_text:

                raise Exception(
                    "Could not extract text from PDF"
                )


            # -------------------------
            # 6. Calculate match
            # -------------------------

            match_result = calculate_match(
                resume_text,
                job_description
            )


            # -------------------------
            # 7. Store result
            # -------------------------

            results.append({

                "filename": file.filename,

                "score": match_result["score"],

                "matched_skills":
                    match_result["matched_skills"],

                "missing_skills":
                    match_result["missing_skills"],

                "status": "success"
            })


        except Exception as e:

            print(
                f"Error processing {file.filename}: {e}"
            )

            results.append({

                "filename": file.filename,

                "status": "failed",

                "error": str(e)
            })


        finally:

            # -------------------------
            # 8. Delete temporary PDF
            # -------------------------

            if os.path.exists(file_path):

                os.remove(file_path)


    # -------------------------
    # 9. Sort successful results
    # -------------------------

    results.sort(
        key=lambda x: x.get("score", -1),
        reverse=True
    )


    # -------------------------
    # 10. Add ranking
    # -------------------------

    rank = 1

    for result in results:

        if result["status"] == "success":

            result["rank"] = rank

            rank += 1


    # -------------------------
    # 11. Return response
    # -------------------------

    return {

        "total_resumes": len(resume_files),

        "processed": len([
            r for r in results
            if r["status"] == "success"
        ]),

        "failed": len([
            r for r in results
            if r["status"] == "failed"
        ]),

        "results": results
    }

# -------------------------
# MATCH SINGLE (For Student Portal)
# -------------------------

@app.post("/match-single")
async def match_single(
    resume_file: Annotated[UploadFile, File(...)],
    job_description: Annotated[str, Form(...)]
):
    """
    Match a single resume against a job description.
    Used by the Student Portal.
    """

    # -------------------------
    # 1. Validate file
    # -------------------------

    if not resume_file:
        raise HTTPException(
            status_code=400,
            detail="No resume file uploaded"
        )

    # -------------------------
    # 2. Check file type
    # -------------------------

    if resume_file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="File must be a PDF"
        )

    # -------------------------
    # 3. Validate JD
    # -------------------------

    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description is required"
        )

    # -------------------------
    # 4. Generate unique filename
    # -------------------------

    unique_name = f"{uuid.uuid4()}_{resume_file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    try:
        # -------------------------
        # 5. Save PDF temporarily
        # -------------------------

        file_content = await resume_file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)

        # -------------------------
        # 6. Extract resume text
        # -------------------------

        resume_text = extract_text_from_pdf(file_path)

        if not resume_text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF"
            )

        # -------------------------
        # 7. Calculate match
        # -------------------------

        match_result = calculate_match(resume_text, job_description)

        # -------------------------
        # 8. Return result
        # -------------------------

        return {
            "match_score": match_result["score"],
            "matched_skills": match_result["matched_skills"],
            "missing_skills": match_result["missing_skills"]
        }

    except HTTPException:
        raise

    except Exception as e:
        print(f"Error processing {resume_file.filename}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing resume: {str(e)}"
        )

    finally:
        # -------------------------
        # 9. Delete temporary PDF
        # -------------------------

        if os.path.exists(file_path):
            os.remove(file_path)