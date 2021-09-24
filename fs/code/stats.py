from pathlib import PurePath
from statistics import fmean, stdev
from typing import Iterable, Iterator, Mapping, Sequence, Tuple

from seaborn import kdeplot

from .types import Stats


def _quantiles(data: Iterable[float], *quantiles: int) -> Mapping[int, float]:
    ordered = sorted(data)

    def cont() -> Iterator[Tuple[int, float]]:
        for quantile in quantiles:
            assert quantile >= 0 and quantile <= 100
            if ordered:
                idx = round((len(ordered) - 1) * quantile)
                yield quantile, ordered[idx]

    return {k: v for k, v in cont()}


def stats(sample: Sequence[float]) -> Stats:
    mean, std = fmean(sample), stdev(sample)
    quantiles = _quantiles(sample)
    stats = Stats(
        mean=mean,
        std=std,
        q0=quantiles[0],
        q50=quantiles[50],
        q95=quantiles[95],
        q100=quantiles[100],
    )
    return stats


def plot(
    cwd: PurePath, framework: str, method: str, sample: Sequence[float]
) -> PurePath:
    title = f"{framework} :: {method}"
    path = (cwd / title).with_suffix(".png")
    plot = kdeplot(data=sample)
    plot.set(title=title, xlabel="ms")
    plot.get_figure().savefig(path)
    return path
