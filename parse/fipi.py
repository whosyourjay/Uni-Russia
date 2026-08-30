#!/usr/bin/env python3
"""Read the national exam figures out of the FIPI Russian-language reports.

Russian is compulsory for the school-leaving certificate, so the count its
report gives is the size of the exam cohort the admission scores rank inside.
"""

import glob
import os
import re

from fetch.fipi import report_path
from lib.paths import data_path, source_path
from lib.pdf import pdf_text
from lib.tsvio import write_rows

TARGET = data_path("ege-national.tsv")

PARTICIPANTS = re.compile(
    r"приняли\s+участие\s+(более\s+)?([\d  ]+?)\s*(тыс\.)?\s*человек")
MEAN = re.compile(
    r"[Сс]редний\s+тестовый\s+балл.{0,60}?(?:составил|–|—)\s*(\d{2}(?:[,.]\d+)?)")


def clean(text):
    """Reports break a long line and space their thousands."""
    return " ".join(text.split())


def participants(text):
    """(count, whether the report rounded it) from the opening paragraph."""
    found = PARTICIPANTS.search(text)
    if not found:
        return None, ""
    approximate, digits, thousands = found.groups()
    count = int(digits.replace(" ", "").replace(" ", ""))
    if thousands:
        count *= 1000
    return count, "yes" if approximate or thousands else "no"


def mean_score(text):
    found = MEAN.search(text)
    return float(found.group(1).replace(",", ".")) if found else ""


def years():
    found = glob.glob(source_path("fipi", "*", "russian.pdf"))
    return sorted(int(os.path.basename(os.path.dirname(p))) for p in found)


def rows():
    for year in years():
        text = clean(pdf_text(report_path(year, "russian")))
        count, rounded = participants(text)
        if count is None:
            continue
        yield {"year": year, "participants": count, "rounded": rounded,
               "mean_test_score": mean_score(text),
               "source": f"sources/fipi/{year}/russian.pdf"}


def main():
    found = list(rows())
    print(f"wrote {write_rows(TARGET, found):,} years to {TARGET}")


if __name__ == "__main__":
    main()
