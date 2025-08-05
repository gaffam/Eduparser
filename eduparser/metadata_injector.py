"""Attach metadata to text chunks."""
from __future__ import annotations

import uuid
from typing import Dict, Iterable, List


def inject_metadata(
    chunks: Iterable[str], metadata: Dict[str, str], *, id_strategy: str = "simple"
) -> List[Dict[str, str]]:
    """Combine *chunks* with *metadata* and assign record IDs.

    ``id_strategy`` controls how ``id`` fields are generated:

    - ``"simple"``: sequential IDs based on the course name.
    - ``"uuid"``: random UUID4 values.
    """

    results: list[dict[str, str]] = []
    for idx, chunk in enumerate(chunks, start=1):
        if id_strategy == "uuid":
            rec_id = str(uuid.uuid4())
        else:
            rec_id = f"{metadata.get('ders', 'doc')}_{idx}"

        item = {"id": rec_id, "content": chunk}
        item.update(metadata)
        results.append(item)
    return results
