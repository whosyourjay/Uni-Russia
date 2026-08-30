#!/usr/bin/env python3
"""What each mirrored monitoring page publishes, year by year.

The ranking reads four columns. The pages carry more than that in some years —
the quota a seat came through, the score of the weakest admitted student, the
average over the general competition alone — and drop them again in others.
This writes down which year offers what, so a question about coverage is
answered from the pages rather than from memory.
"""

import os

from fetch.hse import page_path
from lib import html, net
from lib.paths import data_path
from lib.tsvio import number, write_rows
from parse import hse

TARGET = data_path("source-coverage.tsv")

# Roles beyond the ones the ranking needs, as (prefixes, contains, forbidden).
EXTRA = {
    "general_mean": (hse.AVERAGE, ("конкурсу",), ()),
    "general_count": (("из них", "кол-во", "число"), ("конкурсу",), ("балл",)),
    "scored_count": ((), ("известна сумма баллов",), ()),
    "benefit_count": (("из них",), ("льготник",), ()),
    "quota_count": (("из них",), ("квоте",), ()),
    "target_count": (("из них",), ("целев",), ()),
    "crimea_count": (("из них",), ("крым",), ()),
    "weakest_score": ((), ("слабог",), ()),
    "floor_score": (("min",), (), ()),
}
COLUMNS = ("mean_ege", "students", "bvi", "id_deducted", "region", "profile",
           "tuition", *EXTRA)


def published(headers, funding):
    """Every role this page's captions offer, whether the ranking reads it or not."""
    found = set(hse.columns(headers, funding))
    found |= {role for role, rule in EXTRA.items() if hse.matches(headers, rule)}
    return found


def rows():
    for level in ("university", "field"):
        for year in hse.mirrored_years(level):
            for funding in hse.PLACES:
                path = page_path(level, funding, year)
                if not os.path.exists(path):
                    continue
                records = html.records(net.text(path))
                if not records:
                    continue
                counts = hse.columns(list(records[0]), funding)["students"]
                offers = published(list(records[0]), funding)
                yield {"level": level, "funding": funding, "year": year,
                       "groups": len(records),
                       "admitted": sum(int(number(r[counts], 0)) for r in records),
                       **{role: "yes" if role in offers else "" for role in COLUMNS}}


def main():
    found = sorted(rows(), key=lambda row: (row["level"], row["funding"],
                                            row["year"]))
    print(f"wrote {write_rows(TARGET, found):,} pages to {TARGET}")


if __name__ == "__main__":
    main()
