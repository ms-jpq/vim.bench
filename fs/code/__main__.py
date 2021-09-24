from argparse import ArgumentParser, Namespace
from asyncio import run
from dataclasses import dataclass
from itertools import chain, islice, product
from os import linesep
from os.path import normcase, sep
from pathlib import Path
from random import choice, uniform
from sys import exit
from tempfile import NamedTemporaryFile
from typing import Iterator, Sequence, Tuple

from std2.pickle import new_decoder

from .tmux import tmux

_DATA = Path(sep) / "data"
_BUFFERS = _DATA / "buffers"


@dataclass(frozen=True)
class _Parsed:
    text: str
    total: int
    unique: int
    gen: Iterator[str]


_FRAMEWORKS = {"coq", "coc", "cmp"}
_TESTS = {*_BUFFERS.iterdir()}


def _tokenize(path: Path) -> _Parsed:
    text = path.read_text()
    lines = text.splitlines()
    tot = tuple(chain.from_iterable(line.split() for line in lines))
    uniq = {*tot}
    ws = " " * (len(tot) - len(lines)) + linesep * len(lines)
    gen = iter(lambda: choice(tot) + choice(ws), None)

    parsed = _Parsed(text=text, total=len(tot), unique=len(uniq), gen=gen)
    return parsed


def _parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--lo", type=float, required=True)
    parser.add_argument("--hi", type=float, required=True)
    parser.add_argument("--tokens", type=int, required=True)
    parser.add_argument("--reps", type=int, required=True)

    return parser.parse_args()


async def main() -> int:
    args = _parse_args()
    time_gen = iter(lambda: uniform(args.lo, args.hi), None)
    decode = new_decoder[Sequence[float]](Sequence[float])

    async def cont() -> Tuple[_Parsed, Sequence[float]]:
        for framework, path in product(_FRAMEWORKS, _TESTS):
            with NamedTemporaryFile(mode="w", delete=False) as fd:
                tmp = Path(fd.name)
                parsed = _tokenize(path)
                fd.write(parsed.text)

            feed = islice(zip(time_gen, chain("goi", parsed.gen)), args.tokens)
            env = {
                "COMPLETION_FRAMEWORK": framework,
                "JSON_OUTPUT": normcase(tmp),
            }
            await tmux(Path(), env=env, document=tmp, feed=feed)
            json = tmp.read_text()
            decoded = decode(json)
            yield parsed, decoded

    return 0


if __name__ == "__main__":
    try:
        code = run(main())
    except KeyboardInterrupt:
        exit(130)
    else:
        exit(code)
