from asyncio import gather, run
from pathlib import Path
from sys import exit

from std2.asyncio.subprocess import call

_PACK = Path().home() / ".config" / "nvim" / "pack" / "modules" / "start"


_REPOS = {
    "https://github.com/ms-jpq/coq_nvim.git",
}


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


async def main() -> int:
    _PACK.mkdir(parents=True, exist_ok=True)
    await gather(*map(_git, _REPOS))

    return 0


if __name__ == "__main__":
    try:
        code = run(main())
    except KeyboardInterrupt:
        exit(130)
    else:
        exit(code)
