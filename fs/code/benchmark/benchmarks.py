from dataclasses import dataclass
from functools import lru_cache
from itertools import chain, product
from json import loads
from os import linesep
from os.path import sep
from pathlib import Path, PurePath
from random import Random
from statistics import NormalDist
from tempfile import NamedTemporaryFile
from typing import (
    AbstractSet,
    AsyncIterator,
    Iterator,
    MutableSequence,
    Optional,
    Sequence,
)
from uuid import uuid4

from std2.pickle.decoder import new_decoder
from yaml import safe_load

from .stats import plot, stats
from .tmux import tmux
from .types import Benchmark, Instruction


@dataclass(frozen=True)
class _Test:
    src: PurePath
    tokens: PurePath


@dataclass(frozen=True)
class _TestSpec:
    cwd: Path
    files: AbstractSet[_Test]


@dataclass(frozen=True)
class _Specs:
    frameworks: AbstractSet[str]
    tests: Sequence[_TestSpec]


@dataclass(frozen=True)
class _Parsed:
    text: str
    tot: Sequence[str]
    ws: Sequence[str]


_SPECS = Path(sep) / "data" / "specs.yml"


def _specs() -> _Specs:
    decode = new_decoder[_Specs](_Specs)
    txt = _SPECS.read_text()
    yaml = safe_load(txt)
    specs = decode(yaml)
    return specs


def _cartesian(debug: Optional[str]) -> Iterator[Instruction]:
    if debug:
        with NamedTemporaryFile(delete=False) as fd:
            tmp = Path(fd.name)
        inst = Instruction(
            debug=True, framework=debug, cwd=PurePath(), test_file=tmp, token_file=tmp
        )
        yield inst
    else:
        spec = _specs()
        for framework, test in product(spec.frameworks, spec.tests):
            for tst in test.files:
                inst = Instruction(
                    debug=False,
                    framework=framework,
                    cwd=test.cwd,
                    test_file=test.cwd / tst.src,
                    token_file=test.cwd / tst.tokens,
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
    debug: Optional[str], plot_dir: PurePath, norm: NormalDist, samples: int
) -> AsyncIterator[Benchmark]:
    cartesian = _cartesian(debug)
    decode = new_decoder[Sequence[float]](Sequence[float])

    seed = uuid4().bytes
    for inst in cartesian:
        parsed = _naive_tokenize(inst.token_file)

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
