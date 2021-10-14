from base64 import b64encode
from dataclasses import dataclass
from io import BytesIO
from statistics import StatisticsError, fmean, stdev
from typing import Sequence, Tuple

from matplotlib.pyplot import figure
from seaborn import kdeplot
from std2.statistics import quantiles


@dataclass(frozen=True)
class Stats:
    items: int
    mean: float
    std: float
    q0: float
    q50: float
    q95: float
    q100: float


def stats(sample: Sequence[float]) -> Stats:
    try:
        mean, std = round(fmean(sample)), round(stdev(sample))
    except StatisticsError:
        mean, std = 0, 0
    quads = {key: round(val) for key, val in quantiles(sample, 0, 50, 95, 100).items()}

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


def b64_plots(title: str, sample: Sequence[float]) -> Tuple[str, str]:
    pdf_title, cdf_title = f"pdf -- {title}", f"cdf -- {title}"
    pdf_io, cdf_io = BytesIO(), BytesIO()

    figure()
    pdf_plot = kdeplot(data=sample, cumulative=False)
    pdf_plot.set(xlabel="ms", title=pdf_title)
    pdf_plot.get_figure().savefig(pdf_io, format="png")

    figure()
    cdf_plot = kdeplot(data=sample, cumulative=True)
    cdf_plot.set(xlabel="ms", title=cdf_title)
    cdf_plot.get_figure().savefig(cdf_io, format="png")

    pdf_io.seek(0)
    cdf_io.seek(0)

    pdf = b64encode(pdf_io.read())
    cdf = b64encode(cdf_io.read())
    return pdf.decode(), cdf.decode()
