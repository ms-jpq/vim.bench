from dataclasses import dataclass
from functools import lru_cache
from itertools import chain, product
from json import loads
from os import linesep
from pathlib import Path, PurePath
from random import Random
from statistics import NormalDist
from tempfile import NamedTemporaryFile
from typing import AsyncIterator, Iterator, MutableSequence, Sequence
from uuid import uuid4

from std2.pickle import new_decoder

from ..parse import specs
from .stats import plot, stats
from .tmux import tmux
from .types import Benchmark, Instruction


@dataclass(frozen=True)
class _Parsed:
    text: str
    tot: Sequence[str]
    ws: Sequence[str]


def _cartesian(debug: bool) -> Iterator[Instruction]:
    if debug:
        with NamedTemporaryFile(delete=False) as fd:
            test_file = Path(fd.name)
        inst = Instruction(
            debug=debug,
            framework="noop",
            cwd=PurePath(),
            test_file=test_file,
        )
        yield inst
    else:
        spec = specs()
        for framework, test in product(spec.frameworks, spec.tests):
            for path in test.files:
                file = test.cwd / path
                inst = Instruction(
                    debug=debug,
                    framework=framework,
                    cwd=test.cwd,
                    test_file=file,
                )
                yield inst


@lru_cache(maxsize=None)
def _naive_tokenize(path: Path) -> _Parsed:
    unifying = {"_"}
    text = path.read_text()
    lines = text.splitlines()

    def cont() -> Iterator[str]:
        for line in lines:
            for section in line.split():
                acc: MutableSequence[str] = []
                for char in section:
                    if char.isalnum() or char in unifying:
                        acc.append(char)
                    else:
                        if acc:
                            yield "".join(acc)
                            acc.clear()
                if acc:
                    yield "".join(acc)
                    acc.clear()

    tot = tuple(cont())
    ws = " " * (len(tot) - len(lines)) + linesep * len(lines)
    parsed = _Parsed(text=text, tot=tot, ws=ws)
    return parsed


async def benchmarks(
    debug: bool, plot_dir: PurePath, norm: NormalDist, samples: int
) -> AsyncIterator[Benchmark]:
    cartesian = _cartesian(debug)
    decode = new_decoder[Sequence[float]](Sequence[float])

    seed = uuid4().bytes
    for inst in cartesian:
        parsed = _naive_tokenize(inst.test_file)

        rand = Random(seed)
        gen = chain.from_iterable(
            iter(lambda: rand.choice(parsed.tot) + rand.choice(parsed.ws), None)
        )
        feed = zip(norm.samples(samples, seed=seed), gen)

        out = await tmux(inst, feed=feed)
        json = loads(out.read_text())
        sample = decode(json)

        stat = stats(sample)
        plotted = plot(
            dump_into=plot_dir,
            inst=inst,
            sample=sample,
        )
        benchmark = Benchmark(
            framework=inst.framework,
            data_file=inst.test_file,
            tokens=len(parsed.tot),
            stats=stat,
            plot=plotted,
        )
        yield benchmark
