"""
PDF text extraction with section detection.

Returns full text + detected sections (SKILLS, EXPERIENCE, etc.).
"""
import io
from typing import Dict, Any

from pypdf import PdfReader

# Import section detector (same package)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pdf_parsing.section_detector import detect_sections


def extract_text_from_pdf(file_bytes: bytes) -> Dict[str, Any]:
    """
    Extract text and sections from a PDF resume.

    Returns:
        {
            "text": "full resume text...",
            "sections": {"skills": "...", "experience": "...", ...},
            "page_count": 2,
            "status": "ok" | "empty" | "error",
            "error": None | "error message"
        }
    """
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        pages = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                pages.append(page_text)

        full_text = "\n".join(pages).strip()

        if len(full_text) < 50:
            return {
                "text": full_text,
                "sections": {"other": full_text},
                "page_count": len(reader.pages),
                "status": "empty",
                "error": "PDF appears to contain very little text (possibly scanned image)",
            }

        # Detect sections
        sections = detect_sections(full_text)

        return {
            "text": full_text,
            "sections": sections,
            "page_count": len(reader.pages),
            "status": "ok",
            "error": None,
        }

    except Exception as e:
        return {
            "text": "",
            "sections": {},
            "page_count": 0,
            "status": "error",
            "error": str(e),
        }