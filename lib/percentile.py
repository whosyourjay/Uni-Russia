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
        year = int(row["year"])
        source_year = int(row.get("distribution_year") or year)
        entry = years.setdefault(year, {"points": [], "source_year": source_year})
        if entry["source_year"] != source_year:
            raise ValueError(f"year {year} mixes reference distributions")
        entry["points"].append((float(row["score"]), float(row["percentile"])))
    curves = {}
    for year, entry in years.items():
        carried = entry["source_year"] != year
        boundary = "hold" if carried else "missing"
        curves[year] = Curve(
            entry["points"], "linear", lower=boundary, upper=boundary,
            metadata={"distribution_year": entry["source_year"], "carried": carried},
        )
    return curves


def interpolate(points, score):
    """Linearly interpolate an ascending sequence of `(score, percentile)`."""
    curve = points if isinstance(points, Curve) else Curve(points)
    return curve.rank(score)


def percentile(score, year):
    """The empirical share at or below a score in the year's reference CDF.

    Between two points the CDF is linear. An exact-year curve rejects scores
    outside its support; a borrowed neighboring-year curve clamps and records
    that its endpoint handled the score.
    """
    points = table().get(year)
    if not points or score is None:
        return None
    return interpolate(points, score)


def years():
    return sorted(table())
