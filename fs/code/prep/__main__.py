from asyncio import gather, run
from pathlib import Path
from sys import executable, exit
from typing import Optional

from std2.asyncio.subprocess import call

_PACK = Path().home() / ".config" / "nvim" / "pack" / "modules" / "start"


async def _git(uri: str, branch: Optional[str] = None) -> None:
    await call(
        "git",
        "clone",
        "--depth",
        "1",
        *(("--branch", branch) if branch else ()),
        "--",
        uri,
        cwd=_PACK,
        capture_stderr=False,
        capture_stdout=False,
    )


async def _coq() -> None:
    uri = "https://github.com/ms-jpq/coq_nvim"
    await _git(uri)
    await call(
        Path(executable).resolve(),
        "-m",
        "coq",
        "deps",
        cwd=_PACK / "coq_nvim",
    )


async def _coc() -> None:
    uri = "https://github.com/neoclide/coc.nvim"
    await _git(uri, branch="release")


async def _cmp() -> None:
    uris = {
        "https://github.com/hrsh7th/nvim-cmp",
        "https://github.com/hrsh7th/cmp-buffer",
        "https://github.com/hrsh7th/cmp-nvim-lsp",
        "https://github.com/hrsh7th/cmp-path",
    }
    await gather(*map(_git, uris))


async def main() -> int:
    _PACK.mkdir(parents=True, exist_ok=True)
    await gather(_coq(), _coc(), _cmp())

    return 0


if __name__ == "__main__":
    try:
        code = run(main())
    except KeyboardInterrupt:
        exit(130)
    else:
        exit(code)
