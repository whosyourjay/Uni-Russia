"""Where an exam score stands in its year's empirical reference CDF.

`cohort.py` builds the table this reads from FIPI subject distributions. Every
table that needs a percentile comes through here, so interpolation has one
definition.
"""

import functools

from uniability import Curve

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
    return {year: Curve(points, "linear", lower="missing", upper="missing")
            for year, points in years.items()}


def interpolate(points, score):
    """Linearly interpolate an ascending sequence of `(score, percentile)`."""
    curve = points if isinstance(points, Curve) else Curve(points)
    return curve.rank(score)


def percentile(score, year):
    """The empirical share at or below a score in the year's reference CDF.

    Between two points the CDF is linear; scores outside the measured curve are
    missing rather than being promoted to an extreme percentile.
    """
    points = table().get(year)
    if not points or score is None:
        return None
    return interpolate(points, score)


def years():
    return sorted(table())
