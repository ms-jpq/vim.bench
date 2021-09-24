from asyncio import gather, run
from multiprocessing import cpu_count
from os.path import sep
from pathlib import Path, PurePosixPath
from sys import executable, exit
from typing import Optional
from urllib.parse import urlparse

from std2.asyncio.subprocess import call

_PACK_HOME = Path().home() / ".config" / "nvim" / "pack" / "modules"
_PACK_OPT = _PACK_HOME / "opt"
_PACK_START = _PACK_HOME / "start"
_DATA_LSP = Path(sep) / "data" / "lsp"


async def _git(cwd: Path, uri: str, branch: Optional[str] = None) -> None:
    location = cwd / PurePosixPath(urlparse(uri).path).name
    if location.exists():
        await call(
            "git",
            "pull",
            *(("origin", branch) if branch else ()),
            cwd=location,
            capture_stderr=False,
            capture_stdout=False,
        )
    else:
        await call(
            "git",
            "clone",
            "--jobs",
            str(cpu_count()),
            "--depth",
            "1",
            *(("--branch", branch) if branch else ()),
            "--",
            uri,
            cwd=cwd,
            capture_stderr=False,
            capture_stdout=False,
        )


async def _pack(uri: str, lazy: bool = False, branch: Optional[str] = None) -> None:
    cwd = _PACK_OPT if lazy else _PACK_START
    await _git(cwd, uri=uri, branch=branch)


async def _lsps() -> None:
    uri = "https://github.com/neovim/nvim-lspconfig"
    await gather(
        _pack(uri),
        call(
            "npm",
            "install",
            "--global",
            "--",
            "typescript",
            "typescript-language-server",
            "pyright",
            capture_stdout=False,
            capture_stderr=False,
        ),
    )


async def _coq() -> None:
    uri = "https://github.com/ms-jpq/coq_nvim"
    await _pack(uri)
    await call(
        Path(executable).resolve(),
        "-m",
        "coq",
        "deps",
        cwd=_PACK_START / "coq_nvim",
    )


async def _coc() -> None:
    uri = "https://github.com/neoclide/coc.nvim"
    await _pack(uri, lazy=True, branch="release")


async def _cmp() -> None:
    uris = {
        "https://github.com/hrsh7th/nvim-cmp",
        "https://github.com/hrsh7th/cmp-buffer",
        "https://github.com/hrsh7th/cmp-nvim-lsp",
        "https://github.com/hrsh7th/cmp-path",
    }
    await gather(*map(_pack, uris))


async def _repos() -> None:
    uris = {
        "https://github.com/nodejs/node",
        "https://github.com/python/mypy",
    }
    await gather(*(_git(_DATA_LSP, uri=uri) for uri in uris))


async def main() -> int:
    for path in (_PACK_OPT, _PACK_START, _DATA_LSP):
        path.mkdir(parents=True, exist_ok=True)

    await gather(_lsps(), _coq(), _coc(), _cmp(), _repos())

    return 0


if __name__ == "__main__":
    try:
        code = run(main())
    except KeyboardInterrupt:
        exit(130)
    else:
        exit(code)
