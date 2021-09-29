from asyncio import gather, run
from multiprocessing import cpu_count
from os.path import sep
from pathlib import Path
from sys import executable, exit
from typing import Optional

from std2.asyncio.subprocess import call

from ..parse import specs

_PACK_HOME = Path().home() / ".config" / "nvim" / "pack" / "modules"
_PACK_OPT = _PACK_HOME / "opt"
_PACK_START = _PACK_HOME / "start"
_DATA_LSP = Path(sep) / "data" / "lsp"


async def _git(cwd: Path, uri: str, branch: Optional[str] = None) -> None:
    await call(
        "git",
        "clone",
        f"--jobs={cpu_count()}",
        "--depth=1",
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


async def _compe() -> None:
    uri = "https://github.com/hrsh7th/nvim-compe"
    await _pack(uri)


async def _comp_nvim() -> None:
    uris = {
        "https://github.com/nvim-lua/completion-nvim",
        "https://github.com/steelsojka/completion-buffers",
    }
    await gather(*map(_pack, uris))


async def _ddc() -> None:
    uris = {
        "https://github.com/vim-denops/denops.vim",
        "https://github.com/Shougo/ddc.vim",
        "https://github.com/Shougo/ddc-around",
        "https://github.com/Shougo/ddc-matcher_head",
        "https://github.com/Shougo/ddc-sorter_rank",
    }
    # await gather(*map(_pack, uris))


async def _ncm() -> None:
    uris = {
        "https://github.com/roxma/nvim-yarp",
        "https://github.com/ncm2/ncm2",
        "https://github.com/ncm2/ncm2-bufword",
        "https://github.com/ncm2/ncm2-path",
    }
    await gather(
        call("python3", "-m", "pip", "install", "--", "pynvim"),
        *map(_pack, uris),
    )


async def _repos() -> None:
    uris = specs().repos
    await gather(*(_git(_DATA_LSP, uri=uri) for uri in uris))


async def main() -> int:
    for path in (_PACK_OPT, _PACK_START, _DATA_LSP):
        path.mkdir(parents=True, exist_ok=True)

    await gather(
        _lsps(),
        _coq(),
        _coc(),
        _cmp(),
        _compe(),
        _comp_nvim(),
        _ddc(),
        _ncm(),
        _repos(),
    )

    return 0


if __name__ == "__main__":
    try:
        code = run(main())
    except KeyboardInterrupt:
        exit(130)
    else:
        exit(code)
