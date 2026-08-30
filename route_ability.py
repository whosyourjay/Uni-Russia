#!/usr/bin/env python3
"""Expose the routes a Russian university admits through, with their seats."""

from lib import admissions
from lib.paths import ranking_path
from lib.percentile import percentile
from lib.tsvio import write_rows

TARGET = ranking_path("route_ability.tsv")
# `compare/viz/routes.py` names the families; funding is a separate dimension.
EXAM = "Exam score"
OLYMPIAD = ("Talent and other", "Без вступительных испытаний")
COMPETITION = "ЕГЭ / внутренние испытания (не разделены)"
FUNDING = {"budget": "Бюджетные места", "paid": "Платные места"}


def rows(year=None):
    """One allocation per admitted group, with olympiad winners split out.

    A БВИ student is admitted on an olympiad result and never sits the subjects,
    so the monitoring writes 100 in place of a score. Here they keep their own
    route with no numeric ability instead of lifting a programme's estimate.
    """
    year = year or max(admissions.years("field"))
    for row in admissions.cells("field", year):
        if row["scored_mean"] is None:
            continue
        non_bvi = row["students"] - row["bvi"]
        if non_bvi > 0:
            yield {"family": EXAM, "route": COMPETITION,
                   "funding": FUNDING[row["funding"]],
                   "ability": percentile(row["scored_mean"], year),
                   "top": "", "seats": non_bvi,
                   "observed_score_seats": ""}
        if row["bvi"]:
            yield {"family": OLYMPIAD[0], "route": OLYMPIAD[1],
                   "funding": FUNDING[row["funding"]], "ability": None,
                   "top": "yes", "seats": row["bvi"],
                   "observed_score_seats": 0}


def main():
    found = list(rows())
    print(f"wrote {write_rows(TARGET, found):,} allocations to {TARGET}")


if __name__ == "__main__":
    main()
