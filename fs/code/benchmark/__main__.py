from argparse import ArgumentParser
from asyncio import run
from dataclasses import dataclass
from json import dumps
from locale import strxfrm
from os import environ
from os.path import sep
from pathlib import Path, PurePath
from statistics import NormalDist
from sys import exit
from typing import Optional, Sequence

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from std2.asyncio.subprocess import call
from std2.locale import pathsort_key
from std2.pickle import new_encoder

from .benchmarks import benchmarks as bench
from .types import Benchmark

_TOP_LEVEL = Path(__file__).resolve().parent
_DUMP = Path(sep) / "dump"


@dataclass(frozen=True)
class _Args:
    debug: Optional[str]
    samples: int
    wpm: int
    avg_word_len: int
    variance: float


@dataclass(frozen=True)
class _Norm:
    mu: float
    sigma: float


@dataclass(frozen=True)
class _Yaml:
    args: _Args
    feed_delay: _Norm
    benchmarks: Sequence[Benchmark]


def img_path(path: str) -> str:
    prefix = environ.get("PUBLISH_URL", "./")
    return prefix + PurePath(path).name


async def _dump(yaml: _Yaml) -> None:
    encode = new_encoder[_Yaml](_Yaml)
    j2 = Environment(
        enable_async=False,
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=StrictUndefined,
        loader=FileSystemLoader(_TOP_LEVEL, followlinks=True),
    )
    j2.filters = {**j2.filters, img_path.__qualname__: img_path}
    rendered = j2.get_template("README.md").render({"BENCHMARKS": yaml.benchmarks})

    encoded = encode(yaml)
    json = dumps(encoded, check_circular=False, ensure_ascii=False)
    await call(
        "sortd",
        "yaml",
        capture_stderr=False,
        capture_stdout=False,
        stdin=json.encode(),
    )
    (_DUMP / "README.md").write_text(rendered)


def _parse_args() -> _Args:
    parser = ArgumentParser()
    parser.add_argument("--debug")
    parser.add_argument("--samples", type=int, default=99)
    parser.add_argument("--wpm", type=int, default=20)
    parser.add_argument("--avg-word-len", type=int, default=9)
    parser.add_argument("--variance", type=float, default=0.15)
    ns = parser.parse_args()
    args = _Args(
        debug=ns.debug,
        samples=ns.samples,
        wpm=ns.wpm,
        avg_word_len=ns.avg_word_len,
        variance=ns.variance,
    )
    assert args.avg_word_len > 1
    assert args.wpm > 1
    assert args.variance > 0 and args.variance < 1
    return args


async def main() -> int:
    args = _parse_args()

    chars_per_minute = args.avg_word_len * args.wpm
    chars_per_second = chars_per_minute / 60

    mu = 1 / chars_per_second
    sigma = mu * args.variance
    norm = NormalDist(mu=mu, sigma=sigma)

    benchmarks = [
        benchmark
        async for benchmark in bench(
            args.debug, plot_dir=_DUMP, norm=norm, samples=args.samples
        )
    ]
    ordered = sorted(
        benchmarks,
        key=lambda b: (
            strxfrm(b.framework),
            pathsort_key(b.data_file),
        ),
    )

    yaml = _Yaml(
        args=args,
        feed_delay=_Norm(mu=mu * 1000, sigma=sigma * 1000),
        benchmarks=ordered,
    )
    await _dump(yaml)

    return 0


if __name__ == "__main__":
    try:
        code = run(main())
    except KeyboardInterrupt:
        exit(130)
    else:
        exit(code)
