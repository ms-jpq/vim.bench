from pathlib import Path
from typing import Iterable

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .benchmarks import Benchmark
from .consts import DUMP

_TOP_LEVEL = Path(__file__).resolve().parent


async def dump(benchmarks: Iterable[Benchmark]) -> None:
    j2 = Environment(
        enable_async=False,
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=StrictUndefined,
        loader=FileSystemLoader(_TOP_LEVEL, followlinks=True),
    )
    tpl = j2.get_template("index.html")
    rendered = tpl.render({"BENCHMARKS": benchmarks})

    (DUMP / "index.html").write_text(rendered)
