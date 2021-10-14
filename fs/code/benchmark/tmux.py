from asyncio import create_subprocess_exec, sleep
from itertools import chain, repeat
from os import environ, sep
from os.path import normcase
from pathlib import Path, PurePath
from subprocess import CalledProcessError
from tempfile import mkdtemp
from typing import Iterable, Tuple
from uuid import uuid4

from std2.asyncio.subprocess import call
from std2.timeit import timeit

_SRV = Path(sep) / "srv"
_PACK = Path.home() / ".config" / "nvim" / "pack" / "frameworks" / "start"

_SHORT = 0.1
_LONG = 1


async def tmux(
    debug: bool,
    framework: str,
    test_input: PurePath,
    lsp_cache: bool,
    lsp_input: PurePath,
    feed: Iterable[Tuple[float, str]],
) -> Path:
    tmp = Path(mkdtemp())
    sock, t_out = tmp / str(uuid4()), tmp / str(uuid4())
    _PACK.symlink_to(_SRV / framework)

    env = {
        "TST_FRAMEWORK": framework,
        "TST_INPUT": normcase(test_input),
        "TST_LSP_CACHE": str(int(lsp_cache)),
        "TST_LSP_INPUT": normcase(lsp_input),
        "TST_OUTPUT": normcase(t_out),
    }
    args = ("tmux", "-S", sock, "--", "new-session", "nvim")
    proc = await create_subprocess_exec(*args, env={**environ, **env})

    await sleep(_LONG)
    while True:
        if sock.exists():
            break
        else:
            await sleep(0)

    if not debug:
        t0 = 0.0
        for delay, chars in chain(zip(repeat(_SHORT), "Go"), feed):
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
        _PACK.unlink()
        return t_out
