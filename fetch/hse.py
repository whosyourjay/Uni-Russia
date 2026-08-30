#!/usr/bin/env python3
"""Mirror the HSE admission-quality monitoring.

The site indexes every published table from its own sidebar, so the year and
report identifiers are read from the index rather than pinned here.
"""

import re
import sys

from lib import net
from lib.paths import source_path

INDEX = "https://ege.hse.ru/"
INDEX_PATH = source_path("hse", "index.html")

# The sidebar's two report families and the two kinds of place a student takes.
LEVELS = {"Данные по вузам": "university",
          "Данные по направлениям подготовки": "field"}
FUNDING = {"Бюджетный прием": "budget", "Платный прием": "paid"}

MARKER = re.compile(
    r'<span class="first_level">\s*([^<]+?)\s*</span>'
    r'|<a[^>]*href="([^"]*?/rating/\d{4}/[^"]+)"[^>]*>\s*([^<]+?)\s*</a>')


def reports(index):
    """(level, funding, year, url) for every table the sidebar publishes."""
    level = year = None
    for heading, url, label in MARKER.findall(index):
        if heading in LEVELS:
            level = LEVELS[heading]
        elif heading.isdigit():
            year = int(heading)
        elif url and label in FUNDING and level and year:
            yield level, FUNDING[label], year, urljoin(url)


def urljoin(url):
    """The sidebar mixes absolute and site-relative links, and points several
    years at a table already filtered to universities over a size. Dropping the
    query returns the full one."""
    url = url.split("?")[0]
    return url if url.startswith("http") else INDEX.rstrip("/") + url


def page_path(level, funding, year):
    return source_path("hse", f"{level}-{funding}-{year}.html")


def main(years=None, force=False):
    net.mirror(INDEX, INDEX_PATH, force=force)
    wanted = set(years or [])
    fetched = kept = 0
    for level, funding, year, url in reports(net.text(INDEX_PATH)):
        if wanted and year not in wanted:
            continue
        if net.mirror(url, page_path(level, funding, year), force=force):
            fetched += 1
        else:
            kept += 1
    print(f"mirrored {fetched} rating pages, {kept} already present")


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:] if a.isdigit()],
         force="--force" in sys.argv)
