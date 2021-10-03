from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import AbstractSet, Optional, Sequence


@dataclass(frozen=True)
class _Test:
    src: PurePath
    tokens: PurePath


@dataclass(frozen=True)
class _TestSpec:
    cwd: Path
    files: AbstractSet[_Test]


@dataclass(frozen=True)
class _Repo:
    uri: str
    sh: Optional[Sequence[str]] = None


@dataclass(frozen=True)
class Specs:
    repos: Sequence[_Repo]
    frameworks: AbstractSet[str]
    tests: Sequence[_TestSpec]
