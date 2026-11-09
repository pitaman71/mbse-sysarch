"""The corpus's cases: each a name and a function that builds its architecture in a store."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from mbse.Architecture.Systems.Examples import Pipeline

CASES: dict[str, Callable[[Any], Any]] = {
    "pipeline": Pipeline.build,
}
