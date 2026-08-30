#!/usr/bin/env python3
"""Read national exam figures and distribution coverage from FIPI reports.

Russian is compulsory for the school-leaving certificate, so the count its
report gives is the size of the exam cohort the admission scores rank inside.
"""

import glob
import os
import re

from lib.paths import data_path, source_path
from lib.pdf import clean_text, pdf_text
from lib.tsvio import write_rows
from parse.fipi_distributions import write_distributions

TARGET = data_path("ege-national.tsv")
COVERAGE = data_path("ege-report-coverage.tsv")

PARTICIPANTS = re.compile(
    r"приняли\s+участие\s+(более\s+)?([\d  ]+?)\s*(тыс\.)?\s*человек")
MEAN = re.compile(
    r"[Сс]редний\s+тестовый\s+балл.{0,60}?(?:составил|–|—)\s*(\d{2}(?:[,.]\d+)?)")
DISTRIBUTIONS = {
    "distribution_pages": re.compile(
        r"(?:крив\w+\s+)?распредел\w*.{0,160}(?:участник\w*\s+экзамен|"
        r"результат\w*\s+участник|балл\w*\s+участник)", re.I | re.S),
    "primary_distribution_pages": re.compile(
        r"распредел\w*.{0,100}первичн\w*\s+балл", re.I | re.S),
    "test_distribution_pages": re.compile(
        r"распредел\w*.{0,100}тестов\w*\s+балл", re.I | re.S),
    "score_band_pages": re.compile(
        r"(?:диапазон\w*\s+тестов\w*\s+балл|"
        r"распредел\w*.{0,100}(?:групп|диапазон)\w*\s+балл)", re.I | re.S),
}


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


def reports(subject="*"):
    for path in sorted(glob.glob(source_path("fipi", "*", f"{subject}.pdf"))):
        yield int(os.path.basename(os.path.dirname(path))), os.path.splitext(
            os.path.basename(path))[0], path


def national_rows():
    for year, _, path in reports("russian"):
        text = clean_text(pdf_text(path))
        count, rounded = participants(text)
        if count is None:
            continue
        yield {"year": year, "participants": count, "rounded": rounded,
               "mean_test_score": mean_score(text),
               "source": f"sources/fipi/{year}/russian.pdf"}


def matching_pages(text, pattern):
    return ",".join(str(number) for number, page in enumerate(text.split("\f"), 1)
                    if number <= 15 and pattern.search(page))


def coverage_rows():
    for year, subject, path in reports():
        text = pdf_text(path)
        normalized = clean_text(text)
        count, rounded = participants(normalized)
        yield {"year": year, "subject": subject,
               "participants": count or "", "rounded": rounded,
               "mean_test_score": mean_score(normalized),
               **{column: matching_pages(text, pattern)
                  for column, pattern in DISTRIBUTIONS.items()},
               "source": f"sources/fipi/{year}/{subject}.pdf"}


def main():
    national = list(national_rows())
    coverage = list(coverage_rows())
    print(f"wrote {write_rows(TARGET, national):,} years to {TARGET}")
    print(f"wrote {write_rows(COVERAGE, coverage):,} reports to {COVERAGE}")
    write_distributions()


if __name__ == "__main__":
    main()
