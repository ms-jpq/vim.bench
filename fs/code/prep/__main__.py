from asyncio import gather, run
from multiprocessing import cpu_count
from pathlib import Path
from sys import executable, exit
from typing import Optional

from std2.asyncio.subprocess import call

_TOP_LEVEL = Path(__file__).resolve().parent
_PACK_HOME = Path().home() / ".config" / "nvim" / "pack" / "modules"
_PACK_OPT = _PACK_HOME / "opt"


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


async def _pack(uri: str, branch: Optional[str] = None) -> None:
    await _git(_PACK_OPT, uri=uri, branch=branch)


async def _lsps() -> None:
    lsp_init = _TOP_LEVEL.parent / "lsp" / "build.sh"
    await call(
        lsp_init,
        capture_stdout=False,
        capture_stderr=False,
    )


async def _coq() -> None:
    uri = "https://github.com/ms-jpq/coq_nvim"
    await _pack(uri)
    await call(
        Path(executable).resolve(),
        "-m",
        "coq",
        "deps",
        cwd=_PACK_OPT / "coq_nvim",
    )


async def _coc() -> None:
    uri = "https://github.com/neoclide/coc.nvim"
    await _pack(uri, branch="release")


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
    await gather(*map(_pack, uris))


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


async def main() -> int:
    _PACK_OPT.mkdir(parents=True, exist_ok=True)
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
