from asyncio import create_subprocess_exec, sleep
from os import environ
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable, Mapping, Tuple
from uuid import uuid4

from std2.asyncio.subprocess import call
from std2.pathlib import AnyPath


async def tmux(
    cwd: AnyPath,
    env: Mapping[str, str],
    feed: Iterable[Tuple[float, str]],
) -> int:

    with TemporaryDirectory() as temp:
        sock = Path(temp) / str(uuid4())
        args = ("tmux", "-S", sock, "--", "new-session", "nvim")
        proc = await create_subprocess_exec(*args, cwd=cwd, env={**environ, **env})

        while True:
            await sleep(0)
            if sock.exists():
                break

        for delay, chars in feed:
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

        await proc.wait()
        return proc.returncode or -2
