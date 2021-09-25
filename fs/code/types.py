from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import AbstractSet


@dataclass(frozen=True)
class _TestSpec:
    cwd: PurePath
    files: AbstractSet[Path]


@dataclass(frozen=True)
class Specs:
    repos: AbstractSet[str]
    frameworks: AbstractSet[str]
    tests: AbstractSet[_TestSpec]
