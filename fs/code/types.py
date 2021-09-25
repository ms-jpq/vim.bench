from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import AbstractSet, Sequence


@dataclass(frozen=True)
class _TestSpec:
    cwd: Path
    files: AbstractSet[PurePath]


@dataclass(frozen=True)
class Specs:
    repos: AbstractSet[str]
    frameworks: AbstractSet[str]
    tests: Sequence[_TestSpec]
