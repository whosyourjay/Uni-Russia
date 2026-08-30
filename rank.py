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


def scored(level, year=None, funding=None):
    """Admitted groups that carry a usable average."""
    return [row for row in admissions.cells(level, year, funding)
            if row["scored_mean"] is not None]


def englishish(name):
    """A cheap readable label: common terms translated, the rest romanized."""
    for russian, english in ENGLISH_TERMS:
        name = re.sub(re.escape(russian), english, name, flags=re.IGNORECASE)
    return " ".join(name.translate(TRANSLITERATION).split())


def ability(level, year):
    """One row per school or school-major: the middle of both funding routes.

    Budget and paid places go to different people, so a university's intake is
    the two together and its score is their weighted average.
    """
    totals = {}
    for row in scored(level, year):
        seats, school = row["students"], row["university"]
        major = row["field"] if level == "field" else None
        key = (school, major)
        blank = {"seats": 0, "weighted": 0.0, "bvi": 0, "budget_seats": 0,
                 "region": row["region"]}
        entry = totals.setdefault(key, blank)
        entry["seats"] += seats
        entry["weighted"] += seats * row["scored_mean"]
        entry["bvi"] += row["bvi"]
        if row["funding"] == "budget":
            entry["budget_seats"] += seats
    rows = []
    for (school, major), entry in totals.items():
        score = entry["weighted"] / entry["seats"]
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
