from asyncio import create_subprocess_exec, sleep
from itertools import chain, repeat
from os import environ
from pathlib import Path, PurePath
from subprocess import CalledProcessError
from tempfile import TemporaryDirectory
from typing import Iterable, Mapping, Tuple
from uuid import uuid4

from std2.asyncio.subprocess import call

_SHORT = 0.1
_LONG = 0.6


async def tmux(
    cwd: PurePath,
    env: Mapping[str, str],
    document: PurePath,
    feed: Iterable[Tuple[float, str]],
) -> None:

    with TemporaryDirectory() as temp:
        sock = Path(temp) / str(uuid4())
        args = ("tmux", "-S", sock, "--", "new-session", "nvim", "--", document)
        proc = await create_subprocess_exec(*args, cwd=cwd, env={**environ, **env})

        await sleep(_LONG)
        while True:
            if sock.exists():
                break
            else:
                await sleep(0)

        for delay, chars in chain(zip(repeat(_SHORT), "Goi"), feed):
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
            await sleep(delay)
            await call(
                "tmux",
                "-S",
                sock,
                "--",
                "paste-buffer",
                capture_stderr=False,
                capture_stdout=False,
            )

        await call(
            "tmux",
            "-S",
            sock,
            "--",
            "send-keys",
            "Escape",
            ":qa!",
            "Enter",
            capture_stderr=False,
            capture_stdout=False,
        )

        if (code := await proc.wait()) != 0:
            raise CalledProcessError(returncode=code, cmd=args)
