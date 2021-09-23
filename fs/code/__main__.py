from argparse import ArgumentParser, Namespace
from asyncio import run
from itertools import chain, islice
from pathlib import Path
from posixpath import normcase
from random import choice, uniform
from string import printable
from sys import exit

from .tmux import tmux

_POOL = printable + " " * 10


def _parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--lo", type=float, required=True)
    parser.add_argument("--hi", type=float, required=True)
    parser.add_argument("--reps", type=int, required=True)
    parser.add_argument("--json", type=Path)

    return parser.parse_args()


async def main() -> int:
    args = _parse_args()
    gen = zip(
        iter(lambda: uniform(args.lo, args.hi), None),
        chain("i", iter(lambda: choice(_POOL), None)),
    )
    feed = islice(gen, args.reps)
    env = {"JSON_OUTPUT": normcase(args.json)}

    code = await tmux(Path(), env=env, feed=feed)
    return code


if __name__ == "__main__":
    try:
        code = run(main())
    except KeyboardInterrupt:
        exit(130)
    else:
        exit(code)
