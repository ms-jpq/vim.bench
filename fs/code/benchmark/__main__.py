from argparse import ArgumentParser, Namespace
from asyncio import run
from os import getcwd
from pathlib import PurePath
from statistics import NormalDist
from sys import exit

from .benchmarks import benchmarks as bench


def _parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--samples", type=int, default=666)
    parser.add_argument("--wpm", type=int, default=99)
    parser.add_argument("--avg-word-len", type=int, default=9)
    parser.add_argument("--variance", type=float, default=0.15)
    return parser.parse_args()


async def main() -> int:
    args = _parse_args()
    assert args.avg_word_len > 1
    assert args.wpm > 1
    assert args.variance > 0 and args.variance < 1

    cwd = PurePath(getcwd())

    chars_per_minute = args.avg_word_len * args.wpm
    chars_per_second = chars_per_minute / 60

    mu = 1 / chars_per_second
    sigma = mu * args.variance
    norm = NormalDist(mu=mu, sigma=sigma)

    benchmarks = [
        benchmark async for benchmark in bench(cwd, norm=norm, samples=args.samples)
    ]

    return 0


if __name__ == "__main__":
    try:
        code = run(main())
    except KeyboardInterrupt:
        exit(130)
    else:
        exit(code)
