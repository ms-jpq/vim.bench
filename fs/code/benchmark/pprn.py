from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .consts import DUMP

_TOP_LEVEL = Path(__file__).resolve().parent


async def dump() -> None:
    j2 = Environment(
        enable_async=False,
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=StrictUndefined,
        loader=FileSystemLoader(_TOP_LEVEL, followlinks=True),
    )
    tpl = j2.get_template("index.html")
    rendered = tpl.render({"BENCHMARKS": yaml.benchmarks})

    (DUMP / "index.html").write_text(rendered)
