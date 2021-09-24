from .types import Stats


def stats(sample: Sequence[float]) -> Stats:
    ordered = sorted(sample)
    stats = Stats(
        sample=sample,
    )
    return stats
