from asyncio import gather, run
from multiprocessing import cpu_count
from os import sep
from pathlib import Path
from sys import executable, exit
from typing import Optional

from std2.asyncio.subprocess import call

_TOP_LEVEL = Path(__file__).resolve().parent
_PACK_HOME = Path().home() / ".config" / "nvim" / "pack" / "modules"
_PACK_START = _PACK_HOME / "start"
_PACK_OPT = Path(sep) / "srv"


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


async def _pack(cwd: Path, uri: str, branch: Optional[str] = None) -> None:
    cwd.mkdir(parents=True, exist_ok=True)

    await _git(cwd, uri=uri, branch=branch)


async def _lsps() -> None:
    _PACK_START.mkdir(parents=True, exist_ok=True)
    uri = "https://github.com/neovim/nvim-lspconfig"
    lsp_init = _TOP_LEVEL.parent / "lsp" / "build.sh"
    await gather(
        _git(_PACK_START, uri=uri),
        call(
            lsp_init,
            capture_stdout=False,
            capture_stderr=False,
        ),
    )


async def _coq() -> None:
    uri = "https://github.com/ms-jpq/coq_nvim"
    cwd = _PACK_OPT / "coq"

    await _pack(cwd, uri=uri)
    await call(
        Path(executable).resolve(strict=True),
        "-m",
        "coq",
        "deps",
        cwd=cwd / "coq_nvim",
    )


async def _coc() -> None:
    uri = "https://github.com/neoclide/coc.nvim"
    cwd = _PACK_OPT / "coc"

    await _pack(cwd, uri, branch="release")


async def _cmp() -> None:
    uris = {
        "https://github.com/hrsh7th/nvim-cmp",
        "https://github.com/hrsh7th/cmp-buffer",
        "https://github.com/hrsh7th/cmp-nvim-lsp",
        "https://github.com/hrsh7th/cmp-path",
    }
    cwd = _PACK_OPT / "cmp"

    await gather(*(_pack(cwd, uri=uri) for uri in uris))


async def _compe() -> None:
    uri = "https://github.com/hrsh7th/nvim-compe"
    cwd = _PACK_OPT / "compe"

    await _pack(cwd, uri=uri)


async def _comp_nvim() -> None:
    uris = {
        "https://github.com/nvim-lua/completion-nvim",
        "https://github.com/steelsojka/completion-buffers",
    }
    cwd = _PACK_OPT / "comp_nvim"

    await gather(*(_pack(cwd, uri=uri) for uri in uris))


async def _ddc() -> None:
    uris = {
        "https://github.com/vim-denops/denops.vim",
        "https://github.com/Shougo/ddc.vim",
        "https://github.com/Shougo/ddc-around",
        "https://github.com/Shougo/ddc-matcher_head",
        "https://github.com/Shougo/ddc-sorter_rank",
    }
    cwd = _PACK_OPT / "ddc"

    await gather(*(_pack(cwd, uri=uri) for uri in uris))


async def _ncm() -> None:
    uris = {
        "https://github.com/roxma/nvim-yarp",
        "https://github.com/ncm2/ncm2",
        "https://github.com/ncm2/ncm2-bufword",
        "https://github.com/ncm2/ncm2-path",
    }
    cwd = _PACK_OPT / "ncm"

    await gather(
        call(executable, "-m", "pip", "install", "--", "pynvim"),
        *(_pack(cwd, uri=uri) for uri in uris),
    )


async def main() -> int:
    await gather(
        _lsps(),
        _coq(),
        _coc(),
        _cmp(),
        _compe(),
        _comp_nvim(),
        _ddc(),
        _ncm(),
    )

    return 0


if __name__ == "__main__":
    try:
        code = run(main())
    except KeyboardInterrupt:
        exit(130)
    else:
        exit(code)
