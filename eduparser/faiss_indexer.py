"""Build a FAISS vector index from JSONL records."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List


# Default embedding model used for indexing.
DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def build_faiss_index(
    jsonl_path: str | Path,
    index_path: str | Path,
    model_name: str = DEFAULT_MODEL,
) -> None:
    """Create a FAISS index from a JSONL file.

    Each line in *jsonl_path* must be a JSON object with at least ``id`` and
    ``content`` fields. Embeddings are created using a SentenceTransformer
    model and stored in a simple ``IndexFlatL2`` FAISS index. The index is
    written to *index_path* and an accompanying ``.ids`` JSON file stores the
    document ids in order.
    """
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
        import faiss  # type: ignore
    except Exception as exc:  # pragma: no cover - import error informative
        raise ImportError("sentence-transformers and faiss are required for indexing") from exc

    jsonl_path = Path(jsonl_path)
    index_path = Path(index_path)

    texts: List[str] = []
    ids: List[str] = []
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            texts.append(obj["content"])
            ids.append(obj["id"])

    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    faiss.write_index(index, str(index_path))

    with (index_path.with_suffix(index_path.suffix + ".ids")).open("w", encoding="utf-8") as f:
        json.dump(ids, f, ensure_ascii=False)
