from dataclasses import dataclass
from pathlib import Path, PurePath


@dataclass(frozen=True)
class Instruction:
    framework: str
    method: str
    cwd: PurePath
    test_file: Path


@dataclass(frozen=True)
class Stats:
    items: int
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
    data_file: PurePath
    total_tokens: int
    unique_tokens: int
    stats: Stats
    plot: PurePath
