#!/usr/bin/env python3
"""Expose the routes a Russian university admits through, with their seats."""

from lib import admissions
from lib.paths import ranking_path
from lib.percentile import percentile
from lib.tsvio import write_rows

TARGET = ranking_path("route_ability.tsv")
# `compare/viz/routes.py` names the families; the route keeps the Russian name.
EXAM = "Exam score"
OLYMPIAD = ("Talent and other", "Без вступительных испытаний")
ROUTES = {"budget": "Бюджетные места", "paid": "Платные места"}


def rows(year=None):
    """One allocation per admitted group, with olympiad winners split out.

    A БВИ student is admitted on an olympiad result and never sits the subjects,
    so the monitoring writes 100 in place of a score. Here they keep their own
    route at the top of the scale instead of lifting their programme's average.
    """
    year = year or max(admissions.years("field"))
    top = percentile(100.0, year)
    for row in admissions.cells("field", year):
        if row["scored_mean"] is None:
            continue
        examined = row["students"] - row["bvi"]
        if examined > 0:
            yield {"family": EXAM, "route": ROUTES[row["funding"]],
                   "ability": percentile(row["scored_mean"], year),
                   "seats": examined}
        if row["bvi"]:
            yield {"family": OLYMPIAD[0], "route": OLYMPIAD[1], "ability": top,
                   "seats": row["bvi"]}


def main():
    found = list(rows())
    print(f"wrote {write_rows(TARGET, found):,} allocations to {TARGET}")


if __name__ == "__main__":
    main()
