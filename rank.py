#!/usr/bin/env python3
"""Write comparable school and school-major ability tables."""

from lib import admissions
from lib.english import english_names
from lib.paths import ranking_path
from lib.percentile import percentile
from lib.tsvio import write_rows

UNIVERSITIES = ranking_path("ability-universities.tsv")
MAJORS = ranking_path("ability-majors.tsv")


def rounded(place):
    """A percentile, or nothing for a year with no CDF behind it."""
    return "" if place is None else round(place, 3)


def labels(rows):
    """Every institution and field name needed by a ranking build."""
    return {row[column] for row in rows
            for column in ("university", "field") if row[column]}


def weighted_median(groups):
    """The ordinary median after expanding integer `(center, seats)` groups."""
    ordered = sorted(groups)
    total = sum(seats for _, seats in ordered)
    targets = ((total - 1) // 2, total // 2)
    values = []
    seen = 0
    for center, seats in ordered:
        while len(values) < 2 and targets[len(values)] < seen + seats:
            values.append(center)
        seen += seats
        if len(values) == 2:
            break
    return sum(values) / len(values)


def ability(level, year, english=None):
    """One row per school or school-major from route-by-field centers.

    Each published exam-taker subgroup mean stands in for its median. BVI
    olympiad seats remain a separate count because they have no EGE score.
    """
    source = admissions.cells("field", year)
    if english is None:
        english = english_names(labels(source))
    totals = {}
    for row in source:
        seats, school = row["students"], row["university"]
        major = row["field"] if level == "field" else None
        key = (school, major)
        blank = {"seats": 0, "scored_seats": 0, "groups": [], "bvi": 0,
                 "budget_seats": 0, "region": row["region"]}
        entry = totals.setdefault(key, blank)
        entry["seats"] += seats
        entry["bvi"] += row["bvi"]
        examined = seats - row["bvi"]
        if examined > 0 and row["scored_mean"] is not None:
            entry["groups"].append((row["scored_mean"], examined))
            entry["scored_seats"] += examined
        if row["funding"] == "budget":
            entry["budget_seats"] += seats
    rows = []
    for (school, major), entry in totals.items():
        if not entry["groups"]:
            continue
        score = weighted_median(entry["groups"])
        row = {"school": school, "school_en": english.get(school, "")}
        if major is not None:
            row.update({"major": major, "major_en": english.get(major, "")})
        row.update({"ability": rounded(percentile(score, year)),
                    "seats": entry["seats"],
                    "scored_seats": entry["scored_seats"], "year": year,
                    "budget_seats": entry["budget_seats"],
                    "olympiad_seats": entry["bvi"], "region": entry["region"]})
        rows.append(row)
    rows.sort(key=lambda row: -row["ability"])
    for place, row in enumerate(rows, start=1):
        row["rank"] = place
        row = {"rank": row.pop("rank"), **row}
        rows[place - 1] = row
    return rows


def main():
    latest = max(admissions.years("university"))
    english = english_names(labels(admissions.cells("field", latest)))
    for level, target in (("university", UNIVERSITIES), ("field", MAJORS)):
        rows = ability(level, latest, english)
        print(f"wrote {write_rows(target, rows):,} {level} rows to {target}")


if __name__ == "__main__":
    main()
