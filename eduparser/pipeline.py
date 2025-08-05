"""High level orchestration for the EduParser toolkit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, Optional

from .pdf_extractor import extract_text
from .content_cleaner import clean_text
from .chunk_generator import generate_chunks
from .metadata_injector import inject_metadata
from .jsonl_exporter import export_to_jsonl
from .faiss_indexer import build_faiss_index, DEFAULT_MODEL


@dataclass
class EduParserConfig:
    """Configuration for :func:`run_pipeline`."""

    source_path: str | Path
    out_path: str | Path
    metadata: Dict[str, str]
    max_tokens: int = 300
    tokenizer: str = "simple"
    split_headings: bool = False
    id_strategy: str = "simple"
    index_path: str | Path | None = None
    model_name: str = DEFAULT_MODEL


def run_pipeline(
    config: EduParserConfig,
    *,
    text: Optional[str] = None,
    extract_fn: Callable[[str | Path], str] = extract_text,
    clean_fn: Callable[[str], str] = clean_text,
    progress_cb: Optional[Callable[[int, int], None]] = None,
) -> Iterable[Dict[str, str]]:
    """Execute the full extraction pipeline.

    ``text`` may be provided to skip the extraction/cleaning stages. If
    ``progress_cb`` is supplied it will be called with ``(step, total_steps)``
    after each stage.
    """

    total_steps = 5 + (1 if config.index_path else 0)
    if text is not None:
        total_steps -= 2

    step = 0

    def update_progress() -> None:
        nonlocal step
        step += 1
        if progress_cb:
            progress_cb(step, total_steps)

    if text is None:
        text = extract_fn(config.source_path)
        update_progress()
        text = clean_fn(text)
        update_progress()

    chunks = generate_chunks(
        text,
        max_tokens=config.max_tokens,
        tokenizer=config.tokenizer,
        respect_headings=config.split_headings,
    )
    update_progress()

    records = inject_metadata(
        chunks, config.metadata, id_strategy=config.id_strategy
    )
    update_progress()

    export_to_jsonl(records, config.out_path)
    update_progress()

    if config.index_path:
        build_faiss_index(
            config.out_path, config.index_path, model_name=config.model_name
        )
        update_progress()

    return records
