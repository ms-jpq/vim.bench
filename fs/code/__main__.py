from argparse import ArgumentParser, Namespace
from asyncio import run
from dataclasses import dataclass
from itertools import chain, islice, product
from os import linesep
from os.path import normcase, sep
from pathlib import Path, PurePath
from random import choice, sample, shuffle, uniform
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
    tot: int
    uniq: int
    gen: Iterator[str]


@dataclass(frozen=True)
class _Benched:
    framework: str
    method: str
    data: PurePath
    total_tokens: int
    unique_tokens: int
    times: Sequence[float]


_FRAMEWORKS = {"coq", "coc", "cmp"}
_TESTS = {
    "buf": {*_BUFFERS.iterdir()},
    "lsp": set(),
}


def _cartesian(reps: int) -> Iterator[Tuple[str, str, Path]]:
    assert reps > 0
    lhs = _FRAMEWORKS
    rhs = tuple((method, path) for method, paths in _TESTS.items() for path in paths)

    def cont() -> Iterator[Tuple[str, str, Path]]:
        for framework, (method, path) in product(lhs, sample(rhs, k=len(rhs))):
            yield framework, method, path

    for _ in range(reps):
        cartesian = [*cont()]
        shuffle(cartesian)
        yield from cartesian


def _naive_tokenize(path: Path) -> _Parsed:
    unifying = {"_"}
    text = path.read_text()
    lines = text.splitlines()
    tot = tuple(
        chain.from_iterable(
            token
            for line in lines
            for maybe_token in line.split()
            if (
                token := "".join(t for t in maybe_token if t.isalnum() or t in unifying)
            )
        )
    )
    uniq = {*tot}
    ws = " " * (len(tot) - len(lines)) + linesep * len(lines)
    gen = iter(lambda: choice(tot) + choice(ws), None)

    parsed = _Parsed(text=text, tot=len(tot), uniq=len(uniq), gen=gen)
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
    cartesian = _cartesian(args.reps)
    decode = new_decoder[Sequence[float]](Sequence[float])

    async def cont() -> _Benched:
        for framework, method, path in cartesian:
            parsed = _naive_tokenize(path)
            feed = islice(zip(time_gen, chain("goi", parsed.gen)), args.tokens)

            with NamedTemporaryFile(mode="w", delete=False) as fd_1, NamedTemporaryFile(
                mode="w", delete=False
            ) as fd_2:
                t_in, t_out = Path(fd_1.name), Path(fd_2.name)
                fd_1.write(parsed.text)

            env = {
                "TST_FRAMEWORK": framework,
                "TST_METHOD": method,
                "TST_INPUT": normcase(t_in),
                "TST_OUTPUT": normcase(t_out),
            }

            await tmux(Path(), env=env, document=t_in, feed=feed)
            json = t_out.read_text()
            times = decode(json)
            benched = _Benched(
                framework=framework,
                method=method,
                data=path,
                total_tokens=parsed.tot,
                unique_tokens=parsed.uniq,
                times=times,
            )
            yield benched

    return 0


if __name__ == "__main__":
    try:
        code = run(main())
    except KeyboardInterrupt:
        exit(130)
    else:
        exit(code)
