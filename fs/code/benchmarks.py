from dataclasses import dataclass
from functools import lru_cache
from itertools import chain, islice, product
from os import linesep
from os.path import normcase, sep
from pathlib import Path, PurePath
from random import choice, sample, shuffle, uniform
from tempfile import NamedTemporaryFile
from typing import AsyncIterator, Iterator, Sequence

from std2.pickle import new_decoder

from .stats import plot, stats
from .tmux import tmux
from .types import Benchmark


@dataclass(frozen=True)
class _Instruction:
    framework: str
    method: str
    cwd: PurePath
    test_file: Path


@dataclass(frozen=True)
class _Parsed:
    text: str
    tot: int
    uniq: int
    gen: Iterator[str]


_DATA = Path(sep) / "data"
_BUFFERS = _DATA / "buffers"

_FRAMEWORKS = {"coq", "coc", "cmp"}
_TESTS = {
    "buf": {*_BUFFERS.iterdir()},
    "lsp": set(),
}


def _cartesian() -> Iterator[_Instruction]:
    lhs = _FRAMEWORKS
    rhs = tuple((method, path) for method, paths in _TESTS.items() for path in paths)

    def cont() -> Iterator[_Instruction]:
        for framework, (method, path) in product(lhs, sample(rhs, k=len(rhs))):
            inst = _Instruction(
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
    cwd: PurePath, lo: float, hi: float, chars: int
) -> AsyncIterator[Benchmark]:
    time_gen = iter(lambda: uniform(lo, hi), None)
    cartesian = _cartesian()
    decode = new_decoder[Sequence[float]](Sequence[float])

    for inst in cartesian:
        parsed = _naive_tokenize(inst.test_file)
        feed = islice(zip(time_gen, parsed.gen), chars)

        with NamedTemporaryFile(mode="w", delete=False) as fd_1, NamedTemporaryFile(
            mode="w", delete=False
        ) as fd_2:
            t_in, t_out = Path(fd_1.name), Path(fd_2.name)
            fd_1.write(parsed.text)

        env = {
            "TST_FRAMEWORK": inst.framework,
            "TST_METHOD": inst.method,
            "TST_INPUT": normcase(t_in),
            "TST_OUTPUT": normcase(t_out),
        }

        await tmux(Path(), env=env, document=t_in, feed=feed)
        json = t_out.read_text()
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
            data=inst.test_file,
            total_tokens=parsed.tot,
            unique_tokens=parsed.uniq,
            stats=stat,
            plot=plotted,
        )
        yield benchmark
