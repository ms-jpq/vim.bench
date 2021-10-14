from dataclasses import dataclass
from functools import lru_cache
from itertools import chain, product
from json import dump, loads
from os import linesep
from pathlib import Path, PurePath
from random import Random
from shutil import copy2
from statistics import NormalDist
from tempfile import NamedTemporaryFile
from typing import AsyncIterator, Iterator, MutableSequence, Sequence, Tuple
from uuid import uuid4

from std2.pickle.decoder import new_decoder
from std2.pickle.encoder import new_encoder

from .consts import DATA
from .specs import specs
from .tmux import tmux


@dataclass(frozen=True)
class _Tokenized:
    text: str
    tot: Sequence[str]
    ws: Sequence[str]


@dataclass(frozen=True)
class _LSProw:
    delay: float
    words: Sequence[str]


_LSPFeed = Sequence[_LSProw]


@dataclass(frozen=True)
class _Instruction:
    framework: str
    method: str
    file: PurePath
    tokens: Iterator[Tuple[float, str]]
    lsp_cache: bool
    lsp_feed: _LSPFeed


@dataclass(frozen=True)
class Benchmark:
    framework: str
    method: str
    file: PurePath
    sample: Sequence[float]


@lru_cache(maxsize=None)
def _naive_tokenize(path: Path) -> _Tokenized:
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
    parsed = _Tokenized(text=text, tot=tot, ws=ws)
    return parsed


def _token_stream(
    seed: bytes, norm: NormalDist, samples: int, tokenized: _Tokenized
) -> Iterator[Tuple[float, str]]:
    rand = Random(seed)
    gen = chain.from_iterable(
        iter(lambda: rand.choice(tokenized.tot) + rand.choice(tokenized.ws), None)
    )
    feed = zip(norm.samples(samples, seed=seed), gen)
    return feed


def _cartesian(
    debug: bool, seed: bytes, norm: NormalDist, samples: int
) -> Iterator[_Instruction]:
    n = 999
    variance = norm.stdev / norm.mean
    spec = specs()
    txts = DATA.glob("*.txt")

    if not debug:
        for framework, txt in product(spec.frameworks, txts):
            method = "buf"
            tokens = _naive_tokenize(txt)
            stream = _token_stream(seed, norm=norm, samples=samples, tokenized=tokens)

            inst = _Instruction(
                framework=framework,
                method=method,
                file=txt,
                tokens=stream,
                lsp_cache=False,
                lsp_feed=(),
            )
            yield inst

    for framework, profile, txt in product(
        spec.frameworks, spec.tests.lsp.profiles, txts
    ):
        method = f"lsp delay={profile.delay} rows={profile.rows}"
        tokens = _naive_tokenize(txt)
        stream = _token_stream(seed, norm=norm, samples=samples, tokenized=tokens)

        with NamedTemporaryFile(mode="w", suffix=".cljc", delete=False) as fd:
            cljc = PurePath(fd.name)
        copy2(txt, cljc)

        def cont() -> Iterator[_LSProw]:
            rand = Random(seed)
            norm_delay = NormalDist(mu=profile.delay, sigma=profile.delay * variance)
            norm_samples = NormalDist(mu=profile.rows, sigma=profile.rows * variance)

            for delay, wcount in zip(
                norm_delay.samples(n, seed=seed),
                map(round, norm_samples.samples(n, seed=seed)),
            ):
                k = min(len(tokens.tot), wcount)
                words = rand.sample(tokens.tot, k=k)
                row = _LSProw(delay=delay, words=words)
                yield row

        inst = _Instruction(
            framework=framework,
            method=method,
            file=cljc,
            tokens=stream,
            lsp_cache=profile.cache,
            lsp_feed=tuple(cont()),
        )
        yield inst


async def benchmarks(
    debug: bool, norm: NormalDist, samples: int
) -> AsyncIterator[Benchmark]:
    decode = new_decoder[Sequence[float]](Sequence[float])
    encode = new_encoder[_LSPFeed](_LSPFeed)

    seed = uuid4().bytes
    for inst in _cartesian(debug, seed=seed, norm=norm, samples=samples):
        json = encode(inst.lsp_feed)

        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as fd:
            lsp_input = PurePath(fd.name)
            dump(
                json,
                fd,
                check_circular=False,
                ensure_ascii=False,
                allow_nan=False,
                indent=2,
            )

        out = await tmux(
            debug,
            framework=inst.framework,
            test_input=inst.file,
            lsp_cache=inst.lsp_cache,
            lsp_input=lsp_input,
            feed=inst.tokens,
        )

        json = loads(out.read_text())
        sample = decode(json)

        benchmark = Benchmark(
            framework=inst.framework,
            method=inst.method,
            file=inst.file,
            sample=sample,
        )
        yield benchmark
