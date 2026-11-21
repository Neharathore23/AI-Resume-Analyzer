"""Module 1 & 2 - resume upload validation and text extraction (PDF / DOCX).
Files are read from memory only; nothing is written to disk."""
import io
import os
from pypdf import PdfReader
from docx import Document

ALLOWED = {".pdf", ".docx"}
MAX_MB = float(os.getenv("MAX_FILE_SIZE_MB", 5))


class ResumeError(Exception):
    pass


def validate(filename: str, size_bytes: int) -> None:
    """Validate resume format and file size limits."""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED:
        raise ResumeError("Unsupported file type. Please upload a PDF or DOCX resume.")
    if size_bytes > MAX_MB * 1024 * 1024:
        raise ResumeError(f"File too large. Maximum size is {MAX_MB:g} MB.")


def _pdf_text(data: bytes) -> str:
    """Extract raw text from PDF bytes using pypdf."""
    reader = PdfReader(io.BytesIO(data))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def _docx_text(data: bytes) -> str:
    """Extract raw text from DOCX bytes including paragraphs and table contents."""
    doc = Document(io.BytesIO(data))
    parts = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            parts.extend(cell.text for cell in row.cells)
    return "\n".join(parts)


def extract_text(filename: str, data: bytes) -> str:
    """
    Validate and extract text from in-memory resume bytes.
    Ensures safe in-memory execution without touching the local disk.
    """
    validate(filename, len(data))
    try:
        text = _pdf_text(data) if filename.lower().endswith(".pdf") else _docx_text(data)
    except Exception as exc:  # corrupt / encrypted files
        raise ResumeError(f"Could not read the file: {exc}") from exc
    if len(text.strip()) < 30:
        raise ResumeError("No readable text found (scanned image PDFs need OCR, which is not included).")
    return text


def get_resume_metadata(filename: str, data: bytes = b"", text: str = "") -> dict:
    """Extract document statistics for dashboard presentation."""
    words = text.split() if text else []
    word_count = len(words)
    char_count = len(text) if text else 0
    reading_time_min = max(1, round(word_count / 200)) if word_count else 0
    size_kb = round(len(data) / 1024, 1) if data else 0.0
    ext = os.path.splitext(filename)[1].upper().replace(".", "") if filename else "UNKNOWN"
    return {
        "filename": filename or "Unknown",
        "extension": ext,
        "size_kb": size_kb,
        "word_count": word_count,
        "char_count": char_count,
        "reading_time_min": reading_time_min,
    }


__all__ = [
    "ALLOWED",
    "MAX_MB",
    "ResumeError",
    "validate",
    "extract_text",
    "get_resume_metadata",
]
