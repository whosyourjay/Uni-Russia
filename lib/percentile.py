"""Where an exam score stands in its year's cohort.

`cohort.py` builds the step table this reads. Every table that needs a
percentile comes through here, so the conversion has one definition.
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


def percentile(score, year):
    """The share of the year's exam participants a score stands above.

    Between two published steps the walk is linear in the score; outside them
    it holds at the nearest, because the table stops where the last admitted
    group does and says nothing about scores no university admitted on.
    """
    points = table().get(year)
    if not points or score is None:
        return None
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


def years():
    return sorted(table())
