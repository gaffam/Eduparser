"""Utilities for cleaning extracted text.

The :func:`clean_text` function removes excessive whitespace, line numbers
and trivial artefacts that commonly appear in OCR or PDF sourced text.
"""
from __future__ import annotations

import re


_LINE_NUM_RE = re.compile(r"^\s*\d+[\.)]?\s*")

# Preset patterns for common PDF artefacts that should be removed entirely.
_ARTEFACT_PATTERNS = [
    re.compile(r"^sayfa\s*\d+", re.IGNORECASE),
    re.compile(r"\bEBA\b"),
    re.compile(r"\bMEB\b"),
]


def _strip_line_numbers(lines: list[str]) -> list[str]:
    return [_LINE_NUM_RE.sub("", ln).strip() for ln in lines]


def clean_text(text: str) -> str:
    """Return a normalised version of *text*.

    The function performs several lightweight cleanups:

    * Remove leading line numbers (e.g. "1. Foo")
    * Drop common PDF artefacts such as "sayfa" headers or "EBA" markers
    * Collapse multiple whitespace characters
    * Drop empty lines
    """
    lines = text.splitlines()
    lines = _strip_line_numbers(lines)
    filtered = [ln for ln in lines if not any(p.search(ln) for p in _ARTEFACT_PATTERNS)]
    cleaned = [re.sub(r"\s+", " ", ln).strip() for ln in filtered if ln.strip()]
    return "\n".join(cleaned)
