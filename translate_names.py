#!/usr/bin/env python3
"""Refresh automatic English labels for every HSE institution and field."""

from lib import admissions
from lib.english import CACHE, english_names, load_cache


def names():
    return {row[column] for row in admissions.cells("field")
            for column in ("university", "field") if row[column]}


def main():
    found = names()
    before = len(load_cache())
    translated = english_names(found, translate_missing=True)
    print(f"{len(found)} labels, {len(translated) - before} newly translated")
    print(f"cache holds {len(translated)} labels at {CACHE}")


if __name__ == "__main__":
    main()
