from argparse import ArgumentParser, Namespace
from asyncio import run
from os import getcwd
from pathlib import PurePath
from sys import exit

from .benchmarks import benchmarks as bench


def _parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--lo", type=float, required=True)
    parser.add_argument("--hi", type=float, required=True)
    parser.add_argument("--chars", type=int, required=True)
    return parser.parse_args()


async def main() -> int:
    args = _parse_args()
    cwd = PurePath(getcwd())

    benchmarks = [
        benchmark
        async for benchmark in bench(cwd, lo=args.lo, hi=args.hi, chars=args.chars)
    ]

    return 0


if __name__ == "__main__":
    try:
        code = run(main())
    except KeyboardInterrupt:
        exit(130)
    else:
        exit(code)
