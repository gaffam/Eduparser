"""Split cleaned text into manageable pieces."""
from __future__ import annotations

import re
from typing import List

try:  # Optional tiktoken import for accurate token counting
    import tiktoken
except Exception:  # pragma: no cover - optional dependency
    tiktoken = None


def _count_tokens(text: str, tokenizer: str) -> int:
    if tokenizer == "simple":
        return len(text.split())
    if tokenizer == "openai":
        if tiktoken is None:
            raise RuntimeError("tiktoken is required for tokenizer='openai'")
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    raise ValueError(f"Unknown tokenizer: {tokenizer}")


def generate_chunks(
    text: str,
    max_tokens: int = 300,
    *,
    tokenizer: str = "simple",
    respect_headings: bool = False,
    heading_pattern: str = r"^(#+\s+|Bölüm\b)",
) -> List[str]:
    """Yield chunks of approximately *max_tokens* tokens.

    Splits the text on paragraph boundaries (double newlines) and groups
    paragraphs until the token count would exceed ``max_tokens``. Token
    counting can use a simple whitespace method or ``tiktoken`` when
    ``tokenizer='openai'``. If ``respect_headings`` is ``True``, paragraphs
    matching ``heading_pattern`` will start a new chunk.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    heading_re = re.compile(heading_pattern, re.IGNORECASE)
    chunks: list[str] = []
    current: list[str] = []
    token_count = 0

    for para in paragraphs:
        if respect_headings and heading_re.match(para) and current:
            chunks.append("\n\n".join(current))
            current = []
            token_count = 0

        tokens = _count_tokens(para, tokenizer)
        if token_count + tokens > max_tokens and current:
            chunks.append("\n\n".join(current))
            current = []
            token_count = 0

        current.append(para)
        token_count += tokens

    if current:
        chunks.append("\n\n".join(current))

    return chunks
