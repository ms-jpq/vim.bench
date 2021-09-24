from dataclasses import dataclass
from pathlib import PurePath


@dataclass(frozen=True)
class Stats:
    mean: float
    std: float
    q0: float
    q50: float
    q95: float
    q100: float


@dataclass(frozen=True)
class Benchmark:
    framework: str
    method: str
    data: PurePath
    total_tokens: int
    unique_tokens: int
    stats: Stats
    plot: PurePath
