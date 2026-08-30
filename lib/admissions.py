"""The parsed monitoring rows, and the score proxy every table ranks on.

The monitoring gives a student admitted without entrance exams — an olympiad
winner, БВИ — a nominal 100 in every subject. That is a placeholder rather
than a measurement, so the proxy used here algebraically takes those students
back out while leaving them in the headcount. Current tables do not separately
count university-test admits, so this is not an observed ЕГЭ-only mean.
"""

import functools

from lib.paths import data_path
from lib.tsvio import number, read_rows

LEVELS = {"university": "admissions-universities.tsv",
          "field": "admissions-fields.tsv"}


@functools.lru_cache(maxsize=len(LEVELS))
def _table(level):
    rows = []
    for row in read_rows(data_path(LEVELS[level])):
        row["year"] = int(row["year"])
        row["students"] = int(row["students"])
        row["bvi"] = int(row["bvi"]) if row["bvi"] else 0
        row["mean_ege"] = number(row["mean_ege"])
        row["scored_mean"] = mean_excluding_bvi(row)
        rows.append(row)
    return rows


def mean_excluding_bvi(row):
    """De-placeholder the group under a declared non-БВИ denominator proxy."""
    non_bvi = row["students"] - row["bvi"]
    if non_bvi <= 0 or row["mean_ege"] is None:
        return row["mean_ege"]
    total = row["mean_ege"] * row["students"] - 100.0 * row["bvi"]
    return round(total / non_bvi, 4)


def cells(level, year=None, funding=None):
    """Admitted groups at one level, filtered to a year or a kind of place."""
    return [row for row in _table(level)
            if (year is None or row["year"] == year)
            and (funding is None or row["funding"] == funding)]


def years(level="university"):
    return sorted({row["year"] for row in _table(level)})
