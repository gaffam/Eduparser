"""Module for extracting text from various document formats.

Supports PDF, DOCX, HTML and plain text files. For PDF parsing the
`pdfplumber` library is used. DOCX files are handled via `python-docx`
while HTML files rely on `BeautifulSoup` from `bs4`.

The main entrypoint is :func:`extract_text` which returns the textual
content of the given document as a single string.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable


def _read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_pdf(path: Path) -> str:
    try:
        import pdfplumber  # type: ignore
    except Exception as exc:  # pragma: no cover - import error is informative
        raise ImportError("pdfplumber is required for PDF extraction") from exc

    text_parts: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts)


def _read_docx(path: Path) -> str:
    try:
        import docx  # type: ignore
    except Exception as exc:
        raise ImportError("python-docx is required for DOCX extraction") from exc

    document = docx.Document(str(path))
    paragraphs = [p.text for p in document.paragraphs]
    return "\n".join(paragraphs)


def _read_html(path: Path) -> str:
    try:
        from bs4 import BeautifulSoup  # type: ignore
    except Exception as exc:
        raise ImportError("beautifulsoup4 is required for HTML extraction") from exc

    html = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n")


_READERS = {
    ".pdf": _read_pdf,
    ".txt": _read_txt,
    ".docx": _read_docx,
    ".html": _read_html,
    ".htm": _read_html,
}


def extract_text(path: str | Path) -> str:
    """Extract text from *path*.

    Parameters
    ----------
    path:
        Path to the document to read.

    Returns
    -------
    str
        All textual content found in the document.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(p)

    reader = _READERS.get(p.suffix.lower())
    if reader is None:
        raise ValueError(f"Unsupported file type: {p.suffix}")

    return reader(p)
