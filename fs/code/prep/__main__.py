from asyncio import gather, run
from pathlib import Path
from sys import executable, exit
from typing import Optional

from std2.asyncio.subprocess import call

_PACK_HOME = Path().home() / ".config" / "nvim" / "pack" / "modules"
_PACK_OPT = _PACK_HOME / "opt"
_PACK_START = _PACK_HOME / "start"


async def _git(uri: str, lazy: bool = False, branch: Optional[str] = None) -> None:
    cwd = _PACK_OPT if lazy else _PACK_START

    await call(
        "git",
        "clone",
        "--depth",
        "1",
        *(("--branch", branch) if branch else ()),
        "--",
        uri,
        cwd=cwd,
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
        cwd=_PACK_START / "coq_nvim",
    )


async def _coc() -> None:
    uri = "https://github.com/neoclide/coc.nvim"
    await _git(uri, lazy=True, branch="release")


async def _cmp() -> None:
    uris = {
        "https://github.com/hrsh7th/nvim-cmp",
        "https://github.com/hrsh7th/cmp-buffer",
        "https://github.com/hrsh7th/cmp-nvim-lsp",
        "https://github.com/hrsh7th/cmp-path",
    }
    await gather(*map(_git, uris))


async def main() -> int:
    for path in (_PACK_OPT, _PACK_START):
        path.mkdir(parents=True, exist_ok=True)

    await gather(_coq(), _coc(), _cmp())

    return 0


if __name__ == "__main__":
    try:
        code = run(main())
    except KeyboardInterrupt:
        exit(130)
    else:
        exit(code)
