"""Writes the corpus: each case's store snapshot, as JSON, to conformance/python3/<case>.json.

    uv run python -m mbse.Architecture.Systems.Conformance.write
"""

from __future__ import annotations

from pathlib import Path

from mbse.Schemas.Framework import Builders, JSON

from .Corpus import CASES

FOLDER = Path(__file__).resolve().parents[5] / "conformance" / "python3"


def snapshot(case: str) -> str:
    """The JSON snapshot of a store holding one case."""
    store = Builders.Store()
    CASES[case](store)
    return JSON.ToJSON(store).Snapshot() + "\n"


if __name__ == "__main__":
    FOLDER.mkdir(parents=True, exist_ok=True)
    for case in CASES:
        (FOLDER / f"{case}.json").write_text(snapshot(case))
        print(f"wrote {case}.json")
