#!/usr/bin/env python3
"""Write comparable school and school-major ability tables."""

import re

from lib import admissions
from lib.paths import ranking_path
from lib.percentile import percentile
from lib.tsvio import write_rows

UNIVERSITIES = ranking_path("ability-universities.tsv")
MAJORS = ranking_path("ability-majors.tsv")

TRANSLITERATION = str.maketrans({
    **dict(zip("абвгдеёжзийклмнопрстуфхцчшщыэюя",
               ("a", "b", "v", "g", "d", "e", "yo", "zh", "z", "i", "y", "k",
                "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "kh",
                "ts", "ch", "sh", "shch", "y", "e", "yu", "ya"))),
    "ь": "", "ъ": "",
})
TRANSLITERATION.update({ord(char.upper()): value.capitalize()
                        for char, value in zip(
                            "абвгдеёжзийклмнопрстуфхцчшщыэюя",
                            ("a", "b", "v", "g", "d", "e", "yo", "zh", "z", "i", "y", "k",
                             "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "kh",
                             "ts", "ch", "sh", "shch", "y", "e", "yu", "ya"))})
ENGLISH_TERMS = (("Моск.", "Moscow"), ("С.-Петербург", "Saint Petersburg"),
                 ("гос.", "State"), ("ун-т.", "University"),
                 ("ин-т.", "Institute"), ("университет", "University"),
                 ("академия", "Academy"), ("федеральный", "Federal"),
                 ("национальный", "National"),
                 ("исследовательский", "Research"),
                 ("технический", "Technical"),
                 ("медицинский", "Medical"),
                 ("педагогический", "Pedagogical"),
                 ("физико-техн.", "Physics and Technology"))


def rounded(place):
    """A percentile, or nothing for a year with no step table behind it."""
    return "" if place is None else round(place, 3)


def englishish(name):
    """A cheap readable label: common terms translated, the rest romanized."""
    for russian, english in ENGLISH_TERMS:
        name = re.sub(re.escape(russian), english, name, flags=re.IGNORECASE)
    return " ".join(name.translate(TRANSLITERATION).split())


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


def ability(level, year):
    """One row per school or school-major from route-by-field centers.

    Each published subgroup mean stands in for that subgroup's median. BVI
    olympiad seats are their own group at the top of the score scale.
    """
    totals = {}
    for row in admissions.cells("field", year):
        seats, school = row["students"], row["university"]
        major = row["field"] if level == "field" else None
        key = (school, major)
        blank = {"seats": 0, "groups": [], "bvi": 0, "budget_seats": 0,
                 "region": row["region"]}
        entry = totals.setdefault(key, blank)
        entry["seats"] += seats
        entry["bvi"] += row["bvi"]
        examined = seats - row["bvi"]
        if examined > 0 and row["scored_mean"] is not None:
            entry["groups"].append((row["scored_mean"], examined))
        if row["bvi"]:
            entry["groups"].append((100.0, row["bvi"]))
        if row["funding"] == "budget":
            entry["budget_seats"] += seats
    rows = []
    for (school, major), entry in totals.items():
        if not entry["groups"]:
            continue
        score = weighted_median(entry["groups"])
        row = {"school": school, "school_en": englishish(school)}
        if major is not None:
            row.update({"major": major, "major_en": englishish(major)})
        row.update({"ability": rounded(percentile(score, year)),
                    "seats": entry["seats"], "year": year,
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
    for level, target in (("university", UNIVERSITIES), ("field", MAJORS)):
        rows = ability(level, latest)
        print(f"wrote {write_rows(target, rows):,} {level} rows to {target}")


if __name__ == "__main__":
    main()
