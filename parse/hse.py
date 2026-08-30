#!/usr/bin/env python3
"""Turn the downloaded monitoring pages into one row per admitted group.

Fifteen years of tables reword their captions freely — the average score is a
"средний балл" until 2015 and a "качество приема" after it, and each year
attaches its own suffix — so a column is found by the role its caption
describes rather than by its text.
"""

import glob
import os
import re

from fetch.hse import page_path
from lib import html, net
from lib.paths import data_path, source_path
from lib.tsvio import number, write_rows

UNIVERSITIES = data_path("admissions-universities.tsv")
FIELDS = data_path("admissions-fields.tsv")

PLACES = {"budget": "бюджет", "paid": "платн"}
COUNTED = ("количество", "кол-во", "зачислено", "численность", "сколько",
           "всего", "принято", "число")
AVERAGE = ("средний балл", "ср.балл", "ср. балл")


def rules(funding):
    """Caption rules per role, best first, as (prefixes, contains, forbidden).

    An average that keeps the achievement points in, a minimum, and the score
    of the weakest admitted student all sit beside the one the ranking wants.
    """
    place = PLACES[funding]
    return {
        "mean_ege": [
            (("качество приема",), (), ()),
            (AVERAGE, (place,), ("без вычета",)),
            (("средний балл зачисленных по результатам егэ",), (), ()),
            (("средний балл егэ",), (), ("min", "слаб", "конкурсу")),
        ],
        "students": [(COUNTED, (place,), ("балл",)),
                     (COUNTED, (), ("балл", "стоимость", *PLACES.values()))],
        "bvi": [((), ("олимпиад",), ()), ((), ("без экзаменов",), ()),
                ((), ("бви",), ())],
        "field": [(("укрупн",), (), ())],
        "region": [(("регион",), (), ())],
        "profile": [(("профиль",), (), ())],
        "tuition": [((), ("стоимость",), ())],
        "id_deducted": [((), ("и.д.?",), ())],
    }


def matches(headers, rule):
    prefixes, contains, forbidden = rule
    found = []
    for header in headers:
        text = header.lower()
        if prefixes and not text.startswith(prefixes):
            continue
        if any(word not in text for word in contains):
            continue
        if any(word in text for word in forbidden):
            continue
        found.append(header)
    return found


REQUIRED = ("mean_ege", "students")


def columns(headers, funding):
    """Map each caption this page uses onto the role the ranking needs. A rule
    that leaves two candidates has not identified the column, so the next one
    decides instead."""
    roles = {"university": "Вуз"}
    for role, ordered in rules(funding).items():
        for rule in ordered:
            found = matches(headers, rule)
            if len(found) == 1:
                roles[role] = found[0]
                break
    missing = [role for role in REQUIRED if role not in roles]
    if missing:
        raise ValueError(f"no {missing} column among {headers}")
    return roles


def tuition_rubles(published):
    """The field tables print thousands of roubles under a caption that says
    roubles; no annual fee is under 10,000 ₽ or over 10,000 thousand ₽."""
    if published in ("", None):
        return ""
    return published * 1000 if published < 10000 else published


def value(record, roles, role, default=""):
    return record[roles[role]].strip() if role in roles else default


def read(level, funding, year):
    """One downloaded page as ranking rows, dropping groups with no score."""
    path = page_path(level, funding, year)
    if not os.path.exists(path):
        return
    records = html.records(net.text(path))
    if not records:
        return
    headers = list(records[0])
    roles = columns(headers, funding)
    for record in records:
        students = number(record[roles["students"]])
        mean = number(record[roles["mean_ege"]])
        if not students or mean is None:
            continue
        yield {"year": year, "funding": funding,
               "university": record[roles["university"]].strip(),
               "field": value(record, roles, "field"),
               "region": value(record, roles, "region"),
               "profile": value(record, roles, "profile"),
               "mean_ege": mean, "students": int(students),
               "bvi": int(number(value(record, roles, "bvi"), 0)),
               "tuition": tuition_rubles(number(value(record, roles, "tuition"),
                                                "")),
               "id_deducted": value(record, roles, "id_deducted").lower()}


def downloaded_years(level):
    """Every year whose page for this level is on disk."""
    found = glob.glob(source_path("hse", f"{level}-*-*.html"))
    return sorted({int(re.search(r"(\d{4})\.html$", p).group(1)) for p in found})


def table(level):
    for year in downloaded_years(level):
        for funding in PLACES:
            yield from read(level, funding, year)


def main():
    for level, target in (("university", UNIVERSITIES), ("field", FIELDS)):
        rows = list(table(level))
        print(f"wrote {write_rows(target, rows):,} rows to {target}")


if __name__ == "__main__":
    main()
