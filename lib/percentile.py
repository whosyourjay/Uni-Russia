"""Where an exam score stands in its year's empirical reference CDF.

`cohort.py` builds the table this reads from FIPI subject distributions. Every
table that needs a percentile comes through here, so interpolation has one
definition.
"""

import bisect
import functools

from lib.paths import data_path
from lib.tsvio import read_rows

STEPS = data_path("cohort-steps.tsv")


@functools.lru_cache(maxsize=1)
def table():
    """Ascending (score, percentile) points per year."""
    years = {}
    for row in read_rows(STEPS):
        years.setdefault(int(row["year"]), []).append(
            (float(row["score"]), float(row["percentile"])))
    return {year: sorted(points) for year, points in years.items()}


def interpolate(points, score):
    """Linearly interpolate an ascending sequence of `(score, percentile)`."""
    scores = [point[0] for point in points]
    place = bisect.bisect_left(scores, score)
    if place == 0:
        return points[0][1]
    if place >= len(points):
        return points[-1][1]
    (low, below), (high, above) = points[place - 1], points[place]
    if high == low:
        return above
    return below + (above - below) * (score - low) / (high - low)


def percentile(score, year):
    """The empirical share at or below a score in the year's reference CDF.

    Between two points the CDF is linear; outside them it holds at the nearest.
    """
    points = table().get(year)
    if not points or score is None:
        return None
    return interpolate(points, score)


def years():
    return sorted(table())
