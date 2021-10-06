from os.path import sep
from pathlib import Path

from std2.pickle.decoder import new_decoder
from yaml import safe_load

from .types import Specs

_SPECS = Path(sep) / "data" / "specs.yml"


def specs() -> Specs:
    decode = new_decoder[Specs](Specs)
    txt = _SPECS.read_text()
    yaml = safe_load(txt)
    specs = decode(yaml)
    return specs
