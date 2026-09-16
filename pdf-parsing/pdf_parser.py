# import os
# import re
# import unicodedata

# import pdfplumber
# from PyPDF2 import PdfReader


# def clean_text(text):
#     """
#     Clean and normalize extracted PDF text.

#     Args:
#         text (str): Raw text extracted from PDF.

#     Returns:
#         str: Cleaned text.
#     """

#     if not text:
#         return ""

#     # Normalize Unicode characters
#     text = unicodedata.normalize("NFKC", text)

#     # Replace common bullet characters with "-"
#     bullet_chars = [
#         "●",
#         "•",
#         "▪",
#         "◦",
#         "■",
#         "○",
#         "◆",
#         "►",
#         "➢"
#     ]

#     for bullet in bullet_chars:
#         text = text.replace(bullet, "-")

#     # Replace tabs with spaces
#     text = text.replace("\t", " ")

#     # Remove unwanted control characters
#     text = "".join(
#         char
#         for char in text
#         if char == "\n"
#         or char == "\t"
#         or not unicodedata.category(char).startswith("C")
#     )

#     # Replace multiple spaces with one space
#     text = re.sub(r"[ ]{2,}", " ", text)

#     # Remove spaces before newline
#     text = re.sub(r"[ \t]+\n", "\n", text)

#     # Remove spaces after newline
#     text = re.sub(r"\n[ \t]+", "\n", text)

#     # Replace 3 or more consecutive newlines with 2
#     text = re.sub(r"\n{3,}", "\n\n", text)

#     # Remove leading/trailing whitespace
#     return text.strip()


# def extract_text_from_pdf(file_path):
#     """
#     Extract all text from a PDF resume.

#     pdfplumber is used as the primary parser.
#     PyPDF2 is used as a fallback.

#     Args:
#         file_path (str): Path to the PDF file.

#     Returns:
#         str: Extracted and cleaned text.

#     Raises:
#         FileNotFoundError: If the file does not exist.
#         ValueError: If the file is not a PDF.
#     """

#     # --------------------------------------------------
#     # 1. Check whether file exists
#     # --------------------------------------------------

#     if not os.path.isfile(file_path):
#         raise FileNotFoundError(
#             f"File not found: {file_path}"
#         )

#     # --------------------------------------------------
#     # 2. Check PDF extension
#     # --------------------------------------------------

#     if not file_path.lower().endswith(".pdf"):
#         raise ValueError(
#             "File is not a valid PDF"
#         )

#     # --------------------------------------------------
#     # 3. Try pdfplumber first
#     # --------------------------------------------------

#     try:
#         extracted_pages = []

#         with pdfplumber.open(file_path) as pdf:

#             # Extract text from ALL pages
#             for page in pdf.pages:

#                 page_text = page.extract_text()

#                 if page_text:
#                     extracted_pages.append(page_text)

#         # Combine all pages
#         text = "\n".join(extracted_pages)

#         # Clean text
#         text = clean_text(text)

#         # If text was successfully extracted,
#         # return it.
#         if text:
#             return text

#     except Exception as error:
#         print(f"pdfplumber extraction failed: {error}")

#     # --------------------------------------------------
#     # 4. PyPDF2 fallback
#     # --------------------------------------------------

#     try:
#         reader = PdfReader(
#             file_path,
#             strict=False
#         )

#         # Check password protection
#         if reader.is_encrypted:

#             try:
#                 reader.decrypt("")

#             except Exception:
#                 raise ValueError(
#                     "PDF is password protected and cannot be read"
#                 )

#         extracted_pages = []

#         # Extract text from ALL pages
#         for page in reader.pages:

#             page_text = page.extract_text()

#             if page_text:
#                 extracted_pages.append(page_text)

#         # Combine pages
#         text = "\n".join(extracted_pages)

#         # Clean text
#         text = clean_text(text)

#         return text

#     except ValueError:
#         raise

#     except Exception as error:

#         print(f"PyPDF2 extraction failed: {error}")

#         # If both libraries fail,
#         # return empty string.
#         return ""


# # ======================================================
# # TESTING
# # ======================================================

# if __name__ == "__main__":

#     # Change this filename if your test PDF has
#     # a different name.
#     pdf_path = "uploads/resume_test.pdf"

#     try:

#         # Call the main function
#         resume_text = extract_text_from_pdf(
#             pdf_path
#         )

#         # Check whether text was extracted
#         if resume_text:

#             print("\n" + "=" * 60)
#             print("PDF TEXT EXTRACTION SUCCESSFUL")
#             print("=" * 60)

#             print("\nExtracted Resume Text:\n")

#             print(resume_text)

#             print("\n" + "=" * 60)

#         else:

#             print(
#                 "\nNo text could be extracted from the PDF."
#             )

#             print(
#                 "The PDF may be scanned/image-only, "
#                 "corrupted, or may not contain a text layer."
#             )

#     except FileNotFoundError as error:

#         print(f"\nERROR: {error}")

#     except ValueError as error:

#         print(f"\nERROR: {error}")

#     except Exception as error:

#         print(f"\nERROR: {error}")
import os
import re
import unicodedata

import pdfplumber
from PyPDF2 import PdfReader


def clean_text(text):
    """
    Clean and normalize text extracted from a PDF.

    Args:
        text (str): Raw text extracted from the PDF.

    Returns:
        str: Cleaned readable text.
    """

    if not text:
        return ""

    # --------------------------------------------------
    # 1. Normalize Unicode characters
    # --------------------------------------------------
    text = unicodedata.normalize("NFKC", text)

    # --------------------------------------------------
    # 2. Remove PDF encoding artifacts
    # Example: (cid:131), (cid:239)
    # --------------------------------------------------
    text = re.sub(r"\(cid:\d+\)", "", text)

    # --------------------------------------------------
    # 3. Replace common bullet characters with "-"
    # --------------------------------------------------
    bullet_chars = [
        "●",
        "•",
        "▪",
        "◦",
        "■",
        "○",
        "◆",
        "►",
        "➢",
        "❖",
    ]

    for bullet in bullet_chars:
        text = text.replace(bullet, "-")

    # --------------------------------------------------
    # 4. Replace tabs with spaces
    # --------------------------------------------------
    text = text.replace("\t", " ")

    # --------------------------------------------------
    # 5. Remove unwanted control characters
    # Keep newline characters
    # --------------------------------------------------
    text = "".join(
        char
        for char in text
        if char == "\n"
        or char == "\t"
        or not unicodedata.category(char).startswith("C")
    )

    # --------------------------------------------------
    # 6. Remove spaces before newline
    # --------------------------------------------------
    text = re.sub(r"[ \t]+\n", "\n", text)

    # --------------------------------------------------
    # 7. Remove spaces after newline
    # --------------------------------------------------
    text = re.sub(r"\n[ \t]+", "\n", text)

    # --------------------------------------------------
    # 8. Replace multiple spaces with one space
    # --------------------------------------------------
    text = re.sub(r"[ ]{2,}", " ", text)

    # --------------------------------------------------
    # 9. Reduce excessive blank lines
    # --------------------------------------------------
    text = re.sub(r"\n{3,}", "\n\n", text)

    # --------------------------------------------------
    # 10. Remove leading/trailing whitespace
    # --------------------------------------------------
    return text.strip()


def extract_text_from_pdf(file_path):
    """
    Extract all text from a PDF resume.

    pdfplumber is used as the primary extraction library.
    PyPDF2 is used as a fallback.

    Args:
        file_path (str):
            Path to the PDF file.

            Example:
            "uploads/resume.pdf"

    Returns:
        str:
            Extracted and cleaned resume text.

            Example:
            "John Doe
            Software Engineer
            Python, Java, React..."

    Raises:
        FileNotFoundError:
            If the PDF file does not exist.

        ValueError:
            If the file is not a PDF or is password protected.
    """

    # ==================================================
    # STEP 1: Check if file exists
    # ==================================================

    if not os.path.isfile(file_path):
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    # ==================================================
    # STEP 2: Check file extension
    # ==================================================

    if not file_path.lower().endswith(".pdf"):
        raise ValueError(
            "File is not a valid PDF"
        )

    # ==================================================
    # STEP 3: Try pdfplumber
    # ==================================================

    try:

        extracted_pages = []

        with pdfplumber.open(file_path) as pdf:

            # Process every page
            for page in pdf.pages:

                page_text = page.extract_text(
                    x_tolerance=2,
                    y_tolerance=3
                )

                if page_text:
                    extracted_pages.append(page_text)

        # Combine all pages
        text = "\n".join(extracted_pages)

        # Clean the text
        text = clean_text(text)

        # If text was found, return it
        if text:
            return text

    except Exception as error:

        print(
            f"pdfplumber extraction failed: {error}"
        )

    # ==================================================
    # STEP 4: PyPDF2 FALLBACK
    # ==================================================

    try:

        reader = PdfReader(
            file_path,
            strict=False
        )

        # --------------------------------------------------
        # Check if PDF is encrypted/password protected
        # --------------------------------------------------

        if reader.is_encrypted:

            try:

                result = reader.decrypt("")

                if result == 0:
                    raise ValueError(
                        "PDF is password protected"
                    )

            except Exception:
                raise ValueError(
                    "PDF is password protected"
                )

        extracted_pages = []

        # Process every page
        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                extracted_pages.append(page_text)

        # Combine pages
        text = "\n".join(extracted_pages)

        # Clean text
        text = clean_text(text)

        return text

    except ValueError:
        raise

    except Exception as error:

        print(
            f"PyPDF2 extraction failed: {error}"
        )

        # Both libraries failed.
        # Return empty string instead of crashing.
        return ""


# ======================================================
# TESTING
# ======================================================

if __name__ == "__main__":

    # --------------------------------------------------
    # PDF file used for testing
    # --------------------------------------------------

    pdf_path = "uploads/resume_test.pdf"

    print("\n" + "=" * 60)
    print("PDF RESUME PARSER")
    print("=" * 60)

    print(f"\nFile: {pdf_path}")

    try:

        # Call the main function
        resume_text = extract_text_from_pdf(
            pdf_path
        )

        # --------------------------------------------------
        # Check extraction result
        # --------------------------------------------------

        if resume_text:

            print("\n" + "=" * 60)
            print("PDF TEXT EXTRACTION SUCCESSFUL")
            print("=" * 60)

            print("\nExtracted Resume Text:\n")

            print(resume_text)

            print("\n" + "=" * 60)

        else:

            print("\n" + "=" * 60)
            print("NO TEXT FOUND")
            print("=" * 60)

            print(
                "\nNo text could be extracted from the PDF."
            )

            print(
                "The PDF may be:"
            )

            print(
                "- Scanned/image-only PDF"
            )

            print(
                "- Corrupted PDF"
            )

            print(
                "- PDF without a text layer"
            )

    except FileNotFoundError as error:

        print("\nERROR:")
        print(error)

    except ValueError as error:

        print("\nERROR:")
        print(error)

    except Exception as error:

        print("\nUNEXPECTED ERROR:")
        print(error)