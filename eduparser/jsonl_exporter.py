"""Export records to JSON Lines format."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Dict


def export_to_jsonl(records: Iterable[Dict], path: str | Path) -> None:
    """Write *records* to *path* in JSON Lines format."""
    p = Path(path)
    with p.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
