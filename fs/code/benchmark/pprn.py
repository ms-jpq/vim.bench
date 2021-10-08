from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from locale import strxfrm
from pathlib import Path
from typing import Iterable, Sequence, Tuple

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from std2.itertools import fst, group_by

from .benchmarks import Benchmark
from .consts import DUMP
from .stats import Stats, b64_plots, stats


@dataclass(frozen=True)
class _Benched:
    stats: Stats
    title: str
    b64_pdf: str
    b64_cdf: str
    details: Sequence[_Benched]


_TOP_LEVEL = Path(__file__).resolve().parent


def _consolidate(
    benchmarks: Iterable[Benchmark],
) -> Sequence[Tuple[str, Sequence[Benchmark]]]:
    marks = group_by(benchmarks, key=lambda b: b.framework, val=lambda x: x)
    consolidated = sorted(
        ((key, val) for key, val in marks.items()),
        key=lambda x: strxfrm(fst(x)),
    )
    return consolidated


def _trans(benchmarks: Sequence[Benchmark]) -> _Benched:
    samples = tuple(chain.from_iterable(mark.sample for mark in benchmarks))
    stat = stats(samples)
    title = ""
    b64_pdf, b64_cdf = b64_plots(title, sample=samples)

    benched = _Benched(
        stats=stat,
        title=title,
        b64_pdf=b64_pdf,
        b64_cdf=b64_cdf,
        details=(),
    )
    return benched


async def dump(benchmarks: Iterable[Benchmark]) -> None:
    j2 = Environment(
        enable_async=True,
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=StrictUndefined,
        loader=FileSystemLoader(_TOP_LEVEL, followlinks=True),
    )
    tpl = j2.get_template("index.html")

    benched = {
        framework: _trans(marks) for framework, marks in _consolidate(benchmarks)
    }
    rendered = await tpl.render_async({"BENCHMARKS": benched})

    (DUMP / "index.html").write_text(rendered)
