from asyncio import gather, run
from pathlib import Path
from sys import executable, exit

from std2.asyncio.subprocess import call

_PACK = Path().home() / ".config" / "nvim" / "pack" / "modules" / "start"


async def _git(uri: str) -> None:
    await call(
        "git",
        "clone",
        "--depth",
        "1",
        "--",
        uri,
        cwd=_PACK,
        capture_stderr=False,
        capture_stdout=False,
    )


async def _coq() -> None:
    uri = "https://github.com/ms-jpq/coq_nvim.git"
    await _git(uri)
    await call(
        Path(executable).resolve(),
        "-m",
        "coq",
        "deps",
        cwd=_PACK / "coq_nvim",
    )


async def _coc() -> None:
    pass


async def _cmp() -> None:
    pass


async def main() -> int:
    _PACK.mkdir(parents=True, exist_ok=True)
    await gather(_coq())

    return 0


if __name__ == "__main__":
    try:
        code = run(main())
    except KeyboardInterrupt:
        exit(130)
    else:
        exit(code)
