from dataclasses import dataclass
from pathlib import PurePath
from typing import Sequence


@dataclass(frozen=True)
class Stats:
    sample: Sequence[float]


@dataclass(frozen=True)
class Benchmark:
    framework: str
    method: str
    data: PurePath
    total_tokens: int
    unique_tokens: int
    stats: Stats
