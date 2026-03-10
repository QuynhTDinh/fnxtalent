"""
File Parser Utility — Extract text from PDF and DOCX files.

Supported formats:
    - PDF (.pdf) → via PyPDF2
    - DOCX (.docx) → via python-docx
"""

import io
from typing import Optional


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract plaintext from uploaded file bytes.

    Args:
        file_bytes: Raw binary content of the file
        filename: Original filename (used to detect format)

    Returns:
        Extracted text as a single string

    Raises:
        ValueError: If file format is not supported
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext == "pdf":
        return _extract_pdf(file_bytes)
    elif ext in ("docx", "doc"):
        return _extract_docx(file_bytes)
    else:
        raise ValueError(
            f"Unsupported file format: .{ext}. "
            "Supported: .pdf, .docx"
        )


def _extract_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using PyPDF2."""
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        raise ImportError("PyPDF2 is required for PDF parsing. Install: pip install PyPDF2")

    reader = PdfReader(io.BytesIO(file_bytes))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text.strip())

    return "\n\n".join(pages)


def _extract_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX using python-docx."""
    try:
        from docx import Document
    except ImportError:
        raise ImportError("python-docx is required for DOCX parsing. Install: pip install python-docx")

    doc = Document(io.BytesIO(file_bytes))
    paragraphs = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            paragraphs.append(text)

    return "\n\n".join(paragraphs)
