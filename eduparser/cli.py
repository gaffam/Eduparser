"""Command line interface for the EduParser toolkit."""
from __future__ import annotations

import argparse
import logging

from .pipeline import EduParserConfig, run_pipeline
from .faiss_indexer import DEFAULT_MODEL


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert educational materials into JSONL chunks")
    parser.add_argument("source", help="Input document (PDF, DOCX, HTML, TXT)")
    parser.add_argument("--sınıf", required=True, help="Grade level")
    parser.add_argument("--ders", required=True, help="Course name")
    parser.add_argument("--konu", required=True, help="Topic")
    parser.add_argument("--out", default="output.jsonl", help="Output JSONL file")
    parser.add_argument("--max_tokens", type=int, default=300, help="Approximate tokens per chunk")
    parser.add_argument(
        "--tokenizer",
        choices=["simple", "openai"],
        default="simple",
        help="Token counting method",
    )
    parser.add_argument(
        "--split_headings",
        action="store_true",
        help="Start new chunks at heading markers",
    )
    parser.add_argument(
        "--id_strategy",
        choices=["simple", "uuid"],
        default="simple",
        help="Record ID generation method",
    )
    parser.add_argument("--index", help="Optional path to build a FAISS index")
    parser.add_argument(
        "--model_name",
        default=DEFAULT_MODEL,
        help="Embedding model used when building the FAISS index",
    )
    return parser


def main(args: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("eduparser")

    parser = build_arg_parser()
    ns = parser.parse_args(args=args)

    metadata = {"sınıf": ns.sınıf, "ders": ns.ders, "konu": ns.konu}
    config = EduParserConfig(
        source_path=ns.source,
        out_path=ns.out,
        metadata=metadata,
        max_tokens=ns.max_tokens,
        tokenizer=ns.tokenizer,
        split_headings=ns.split_headings,
        id_strategy=ns.id_strategy,
        index_path=ns.index,
        model_name=ns.model_name,
    )

    records = run_pipeline(config)
    logger.info("Wrote %d records to %s", len(records), ns.out)

    if ns.index:
        logger.info("Built FAISS index at %s", ns.index)

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
