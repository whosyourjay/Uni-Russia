#!/usr/bin/env python3
"""Parse public СПО institution monitoring pages without inventing seats."""

import glob
import gzip
import re

from fetch.spo import DEFAULT_YEAR
from lib import html
from lib.paths import data_path, source_path
from lib.tsvio import number, write_rows

INSTITUTIONS = data_path("spo-institutions.tsv")
FIELDS = data_path("spo-fields.tsv")
NAME = re.compile(r"<div id=['\"]inst_name['\"][^>]*>(.*?)</div>", re.S)
REGION = re.compile(r"material\.php\?type=2&id=\d+['\"][^>]*>(.*?)</a>", re.S)
INDICATOR = re.compile(r"<tr[^>]*\bN=['\"]([^'\"]+)['\"][^>]*>(.*?)</tr>", re.S)
FIELD_TABLE = re.compile(r"<table[^>]*class=['\"][^'\"]*table_ugs[^'\"]*['\"][^>]*>.*?</table>", re.S)
FIELD = re.compile(r"^(\d{2}\.00\.00)\s*-\s*(.+)$")


def downloaded(year):
    pattern = source_path("spo", str(year), "*.html.gz")
    for path in sorted(glob.glob(pattern)):
        yield re.search(r"(\d+)\.html\.gz$", path).group(1), path


def read(path):
    with gzip.open(path, "rt", encoding="utf-8") as source:
        return source.read()


def indicators(page):
    """Indicator caption to organization value; regional/RF values are last."""
    found = []
    for code, markup in INDICATOR.findall(page):
        cells = [html.strip(cell) for cell in html.CELL.findall(markup)]
        if len(cells) >= 4:
            found.append((code, cells[0], number(cells[-3])))
    return found


def metric(rows, required, forbidden=(), valid=lambda value: True):
    candidates = []
    for code, caption, value in rows:
        lower = caption.lower()
        if value is None or any(term not in lower for term in required):
            continue
        if any(term in lower for term in forbidden) or not valid(value):
            continue
        candidates.append((len(caption), code, value))
    return min(candidates)[2] if candidates else ""


def fields(page):
    match = FIELD_TABLE.search(page)
    if not match:
        return []
    found = []
    for row in html.rows(match.group()):
        parsed = FIELD.match(row[0]) if row else None
        if parsed:
            found.append((parsed.group(1), parsed.group(2)))
    return found


def parse_page(page, year, institution_id):
    rows = indicators(page)
    school = html.strip(NAME.search(page).group(1))
    region_match = REGION.search(page)
    base = {"year": year, "institution_id": institution_id,
            "school": school,
            "region": html.strip(region_match.group(1)) if region_match else ""}
    gpa_terms = ("средний балл аттестата", "студентов, принятых")
    gpa_bad = ("интегрирован", "за счет средств", "по договорам")
    gpa_valid = lambda value: 2 <= value <= 5
    base.update({
        "admitted_gpa": metric(rows, gpa_terms, gpa_bad, gpa_valid),
        "budget_admitted_gpa": metric(rows, gpa_terms + ("за счет средств",),
                                      ("интегрирован",), gpa_valid),
        "paid_admitted_gpa": metric(rows, gpa_terms + ("по договорам",),
                                    ("интегрирован",), gpa_valid),
        "admitted_gpa_ge_4_pct": metric(rows, ("не менее 4-х баллов",)),
        "applications_per_100_budget_places": metric(
            rows, ("в расчете на 100 бюджетных мест",)),
        "current_students": metric(rows, ("общая численность студентов", "чел.")),
        "current_full_time_pct": metric(
            rows, ("удельный вес", "по очной форме", "общей численности")),
        "current_budget_pct": metric(
            rows, ("удельный вес", "за счет средств", "общей численности")),
        "admitted_students": "",
        "budget_admitted_students": "",
        "paid_admitted_students": "",
    })
    return base


def tables(year=DEFAULT_YEAR):
    schools, school_fields = [], []
    for institution_id, path in downloaded(year):
        page = read(path)
        school = parse_page(page, year, institution_id)
        schools.append(school)
        for code, field in fields(page):
            school_fields.append({"year": year, "institution_id": institution_id,
                                  "school": school["school"], "field_code": code,
                                  "field": field, "admitted_gpa": "",
                                  "admitted_students": ""})
    return schools, school_fields


def main(year=DEFAULT_YEAR):
    schools, school_fields = tables(year)
    if not schools:
        raise SystemExit(f"no downloaded СПО institution pages for {year}")
    print(f"wrote {write_rows(INSTITUTIONS, schools):,} institutions")
    print(f"wrote {write_rows(FIELDS, school_fields):,} institution-fields")


if __name__ == "__main__":
    main()
