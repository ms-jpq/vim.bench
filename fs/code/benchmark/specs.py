from dataclasses import dataclass
from functools import lru_cache
from pathlib import PurePath
from typing import AbstractSet

from std2.pickle.decoder import new_decoder
from yaml import safe_load

from .consts import DATA


@dataclass(frozen=True)
class _Typist:
    samples: int
    wpm: int
    avg_word_len: int
    variance: float


@dataclass(frozen=True)
class _Profile:
    cache: bool
    delay: float
    rows: int


@dataclass(frozen=True)
class _Lsp:
    profiles: AbstractSet[_Profile]
    cljc: PurePath
    files: AbstractSet[PurePath]


@dataclass(frozen=True)
class _Tests:
    buffers: AbstractSet[PurePath]
    lsp: _Lsp


@dataclass(frozen=True)
class _Specs:
    typist: _Typist
    frameworks: AbstractSet[str]
    tests: _Tests


_SPECS = DATA / "specs.yml"


@lru_cache(maxsize=None)
def specs() -> _Specs:
    yml = safe_load(_SPECS.read_text())
    specs = new_decoder[_Specs](_Specs)(yml)
    return specs
