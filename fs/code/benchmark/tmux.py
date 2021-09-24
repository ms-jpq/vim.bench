from asyncio import create_subprocess_exec, sleep
from itertools import chain, repeat
from os import environ
from os.path import normcase
from pathlib import Path
from subprocess import CalledProcessError
from tempfile import mkdtemp
from typing import Iterable, Tuple
from uuid import uuid4

from std2.asyncio.subprocess import call
from std2.timeit import timeit

from .types import Instruction

_SHORT = 0.1
_LONG = 1


async def tmux(inst: Instruction, feed: Iterable[Tuple[float, str]]) -> Path:
    tmp = Path(mkdtemp())
    sock, t_out = tmp / str(uuid4()), tmp / str(uuid4())

    env = {
        "TST_FRAMEWORK": inst.framework,
        "TST_METHOD": inst.method,
        "TST_OUTPUT": normcase(t_out),
    }
    args = (
        "tmux",
        "-S",
        sock,
        "--",
        "new-session",
        "nvim",
        "--",
        normcase(inst.test_file),
    )
    proc = await create_subprocess_exec(*args, cwd=inst.cwd, env={**environ, **env})

    await sleep(_LONG)
    while True:
        if sock.exists():
            break
        else:
            await sleep(0)

    t0 = 0
    for delay, chars in chain(zip(repeat(_SHORT), "Goi"), feed):
        with timeit() as t:
            await call(
                "tmux",
                "-S",
                sock,
                "--",
                "load-buffer",
                "-",
                capture_stderr=False,
                capture_stdout=False,
                stdin=chars.encode(),
            )
        await sleep(delay - t0 - t())
        with timeit() as t:
            await call(
                "tmux",
                "-S",
                sock,
                "--",
                "paste-buffer",
                capture_stderr=False,
                capture_stdout=False,
            )
        t0 = t()

    await call(
        "tmux",
        "-S",
        sock,
        "--",
        "send-keys",
        "Escape",
        "Escape",
        "Escape",
        ":qa!",
        "Enter",
        capture_stderr=False,
        capture_stdout=False,
    )

    if (code := await proc.wait()) != 0:
        raise CalledProcessError(returncode=code, cmd=args)
    else:
        return t_out
