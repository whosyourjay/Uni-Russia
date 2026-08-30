#!/usr/bin/env python3
"""Rank universities and fields of study by the exam score they admit on."""

from lib import admissions
from lib.paths import ranking_path
from lib.percentile import percentile
from lib.tsvio import write_rows

UNIVERSITIES = ranking_path("rank-universities.tsv")
FIELDS = ranking_path("rank-fields.tsv")
ABILITY = ranking_path("ability-universities.tsv")


def rounded(place):
    """A percentile, or nothing for a year with no step table behind it."""
    return "" if place is None else round(place, 3)


def scored(level, year=None, funding=None):
    """Admitted groups that carry a usable average."""
    return [row for row in admissions.cells(level, year, funding)
            if row["scored_mean"] is not None]


def ranked(level):
    """Every group, ranked against the other groups of its year and route."""
    out = []
    for year in admissions.years(level):
        for funding in ("budget", "paid"):
            rows = sorted(scored(level, year, funding),
                          key=lambda row: -row["scored_mean"])
            for place, row in enumerate(rows, start=1):
                entry = {"year": year, "funding": funding, "rank": place,
                         "university": row["university"]}
                if level == "field":
                    entry["field"] = row["field"]
                entry.update({
                    "mean_ege": row["mean_ege"],
                    "scored_mean": row["scored_mean"],
                    "ability": rounded(percentile(row["scored_mean"], year)),
                    "students": row["students"], "bvi": row["bvi"],
                    "region": row["region"]})
                out.append(entry)
    return out


def ability(year):
    """One row per university: the seat-weighted middle of both routes.

    Budget and paid places go to different people, so a university's intake is
    the two together and its score is their weighted average.
    """
    totals = {}
    for row in scored("university", year):
        seats, name = row["students"], row["university"]
        blank = {"seats": 0, "weighted": 0.0, "bvi": 0, "budget_seats": 0,
                 "region": row["region"]}
        entry = totals.setdefault(name, blank)
        entry["seats"] += seats
        entry["weighted"] += seats * row["scored_mean"]
        entry["bvi"] += row["bvi"]
        if row["funding"] == "budget":
            entry["budget_seats"] += seats
    rows = []
    for name, entry in totals.items():
        score = entry["weighted"] / entry["seats"]
        rows.append({"year": year, "university": name, "region": entry["region"],
                     "scored_mean": round(score, 2),
                     "ability": rounded(percentile(score, year)),
                     "seats": entry["seats"],
                     "budget_seats": entry["budget_seats"], "bvi": entry["bvi"]})
    rows.sort(key=lambda row: -row["scored_mean"])
    for place, row in enumerate(rows, start=1):
        row["rank"] = place
    return rows


def main():
    for level, target in (("university", UNIVERSITIES), ("field", FIELDS)):
        rows = ranked(level)
        print(f"wrote {write_rows(target, rows):,} rows to {target}")
    latest = max(admissions.years("university"))
    rows = ability(latest)
    print(f"wrote {write_rows(ABILITY, rows):,} universities to {ABILITY}")


if __name__ == "__main__":
    main()
