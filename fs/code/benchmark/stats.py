from hashlib import md5
from pathlib import PurePath
from posixpath import normcase
from statistics import fmean, stdev
from typing import Sequence

from seaborn import kdeplot
from std2.statistics import quantiles

from .types import Instruction, Stats


def stats(sample: Sequence[float]) -> Stats:
    mean, std = fmean(sample), stdev(sample)
    quads = quantiles(sample, 0, 50, 95, 100)
    stats = Stats(
        items=len(sample),
        mean=mean,
        std=std,
        q0=quads[0],
        q50=quads[50],
        q95=quads[95],
        q100=quads[100],
    )
    return stats


def plot(dump_into: PurePath, inst: Instruction, sample: Sequence[float]) -> PurePath:
    title = f"{inst.framework} :: {normcase(inst.test_file)}"
    path = (dump_into / md5(title.encode()).hexdigest()).with_suffix(".png")
    plot = kdeplot(data=sample)
    plot.set(title=title, xlabel="ms")
    plot.get_figure().savefig(path)
    return path
