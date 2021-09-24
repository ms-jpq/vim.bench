from dataclasses import dataclass
from functools import lru_cache
from itertools import chain, product
from json import loads
from os import linesep
from os.path import sep
from pathlib import Path, PurePath
from random import choice, sample, shuffle
from statistics import NormalDist
from typing import AsyncIterator, Iterator, Sequence

from std2.pickle import new_decoder

from .stats import plot, stats
from .tmux import tmux
from .types import Benchmark, Instruction


@dataclass(frozen=True)
class _Parsed:
    text: str
    tot: int
    uniq: int
    gen: Iterator[str]


_DATA = Path(sep) / "data"
_BUFFERS = _DATA / "buffers"
_LSP = _DATA / "lsp"

_FRAMEWORKS = {"coq", "cmp"}
_TESTS = {
    "buf": tuple(zip((_BUFFERS,), _BUFFERS.iterdir())),
    "lsp": (
        (_LSP / "node", _LSP / "node" / "lib" / "rep.js"),
        (_LSP / "mypy", _LSP / "mypy" / "mypy" / "checkstrformat.js"),
    ),
}


def _cartesian() -> Iterator[Instruction]:
    lhs = _FRAMEWORKS
    rhs = tuple((method, path) for method, paths in _TESTS.items() for path in paths)

    def cont() -> Iterator[Instruction]:
        for framework, (method, path) in product(lhs, sample(rhs, k=len(rhs))):
            inst = Instruction(
                framework=framework,
                method=method,
                cwd=PurePath(),
                test_file=path,
            )
            yield inst

    cartesian = [*cont()]
    shuffle(cartesian)
    yield from cartesian


@lru_cache(maxsize=None)
def _naive_tokenize(path: Path) -> _Parsed:
    unifying = {"_"}
    text = path.read_text()
    lines = text.splitlines()
    tot = tuple(
        token
        for line in lines
        for maybe_token in line.split()
        if (token := "".join(t for t in maybe_token if t.isalnum() or t in unifying))
    )
    uniq = {*tot}
    ws = " " * (len(tot) - len(lines)) + linesep * len(lines)
    gen = chain.from_iterable(iter(lambda: choice(tot) + choice(ws), None))

    parsed = _Parsed(text=text, tot=len(tot), uniq=len(uniq), gen=gen)
    return parsed


async def benchmarks(
    cwd: PurePath, norm: NormalDist, samples: int
) -> AsyncIterator[Benchmark]:
    cartesian = _cartesian()
    decode = new_decoder[Sequence[float]](Sequence[float])

    for inst in cartesian:
        parsed = _naive_tokenize(inst.test_file)
        feed = zip(norm.samples(samples), parsed.gen)

        out = await tmux(inst, feed=feed)
        json = loads(out.read_text())
        sample = decode(json)

        stat = stats(sample)
        plotted = plot(
            cwd=cwd,
            framework=inst.framework,
            method=inst.method,
            sample=sample,
        )

        benchmark = Benchmark(
            framework=inst.framework,
            method=inst.method,
            data_file=inst.test_file,
            total_tokens=parsed.tot,
            unique_tokens=parsed.uniq,
            stats=stat,
            plot=plotted,
        )
        yield benchmark
