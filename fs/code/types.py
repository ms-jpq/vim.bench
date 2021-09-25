from dataclasses import dataclass
from pathlib import PurePath
from typing import AbstractSet


@dataclass(frozen=True)
class _SourceSpecs:
    cwd: PurePath
    files: AbstractSet[PurePath]


@dataclass(frozen=True)
class Specs:
    repos: AbstractSet[str]
    frameworks: AbstractSet[str]
    buf: _SourceSpecs
    lsp: _SourceSpecs
