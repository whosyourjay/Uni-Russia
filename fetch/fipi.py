#!/usr/bin/env python3
"""Download the FIPI reports that carry national subject-score distributions.

File names change spelling from year to year, so the reports are discovered
from the index page instead of being constructed.
"""

import argparse
import re

from lib import net
from lib.paths import source_path

INDEX = "https://fipi.ru/ege/analiticheskie-i-metodicheskie-materialy"
INDEX_PATH = source_path("fipi", "index.html")

# Russian is compulsory, so its report counts the whole exam cohort. The
# others are the subjects a competitive admission most often asks for. The
# index names a subject beside its link, but declines the noun differently
# from one year's layout to the next, so each entry is matched on its stem.
SUBJECTS = {"русск": "russian", "математик": "mathematics", "физик": "physics",
            "хими": "chemistry", "биологи": "biology", "истори": "history",
            "географи": "geography", "обществознани": "social-studies",
            "литератур": "literature", "информатик": "informatics",
            "иностранн": "foreign-language", "английск": "english",
            "немецк": "german", "французск": "french", "испанск": "spanish",
            "китайск": "chinese"}
REPORT = re.compile(
    r'<a\b[^>]*?href="(https?://[^"]*?/analiticheskie-i-metodicheskie-materialy/'
    r'(\d{4})/[^"]+\.pdf)"[^>]*>(.*?)</a>', re.S)


def named(text):
    """The subject a fragment names, by the last stem it mentions."""
    lowered = text.lower()
    found = [(lowered.rfind(stem), name)
             for stem, name in SUBJECTS.items() if stem in lowered]
    return max(found)[1] if found else None


def reports(index):
    """(year, subject, url) for every subject report the index links.

    Through 2024 the link's own text names the subject. The 2025 block puts a
    download button under a heading instead, so an unnamed link takes the last
    subject named before it.
    """
    for match in REPORT.finditer(index):
        url, year, label = match.group(1), int(match.group(2)), match.group(3)
        subject = named(label) or named(index[:match.start()])
        if subject:
            yield year, subject, url.replace("http://", "https://")


def report_path(year, subject):
    return source_path("fipi", str(year), f"{subject}.pdf")


def main(subjects=(), years=(), force=False):
    net.download(INDEX, INDEX_PATH, force=force)
    wanted = set(subjects)
    wanted_years = set(years)
    fetched = kept = 0
    for year, subject, url in reports(net.text(INDEX_PATH)):
        if wanted and subject not in wanted:
            continue
        if wanted_years and year not in wanted_years:
            continue
        if net.download(url, report_path(year, subject), force=force):
            fetched += 1
            print(f"downloaded {year} {subject}")
        else:
            kept += 1
    print(f"downloaded {fetched} subject reports, {kept} already present")


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("subjects", nargs="*", choices=sorted(set(SUBJECTS.values())))
    parser.add_argument("--year", action="append", type=int, default=[])
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = arguments()
    main(args.subjects, args.year, args.force)
