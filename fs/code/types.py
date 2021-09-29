from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import AbstractSet, Optional, Sequence


@dataclass(frozen=True)
class _TestSpec:
    cwd: Path
    files: AbstractSet[PurePath]


@dataclass(frozen=True)
class _Repo:
    uri: str
    sh: Optional[Sequence[str]]


@dataclass(frozen=True)
class Specs:
    repos: AbstractSet[_Repo]
    frameworks: AbstractSet[str]
    tests: Sequence[_TestSpec]
