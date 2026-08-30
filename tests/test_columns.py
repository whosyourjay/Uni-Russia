"""Tests for picking the right column out of fifteen years of captions.

Every year the monitoring reprints its average beside two decoys: the same
average with the achievement points left in, and the score of the weakest
admitted student. Reading either one silently shifts a whole year's ranking,
so the captions are checked against every page on disk.
"""

import os
import unittest

from fetch.hse import page_path
from lib import html, net
from parse import hse

DECOYS = ("без вычета", "min ", "самого слабого", "самогослабого", "конкурсу")


def downloaded():
    for level in ("university", "field"):
        for year in hse.downloaded_years(level):
            for funding in hse.PLACES:
                path = page_path(level, funding, year)
                if os.path.exists(path):
                    yield level, funding, year, path


class TestColumns(unittest.TestCase):
    def test_every_downloaded_page_resolves_its_required_columns(self):
        pages = list(downloaded())
        self.assertTrue(pages, "no monitoring pages are downloaded")
        for level, funding, year, path in pages:
            records = html.records(net.text(path))
            if not records:
                continue
            with self.subTest(level=level, funding=funding, year=year):
                roles = hse.columns(list(records[0]), funding)
                for role in hse.REQUIRED:
                    self.assertIn(role, roles)

    def test_the_average_column_is_never_one_of_its_decoys(self):
        for level, funding, year, path in downloaded():
            records = html.records(net.text(path))
            if not records:
                continue
            caption = hse.columns(list(records[0]), funding)["mean_ege"].lower()
            with self.subTest(level=level, funding=funding, year=year):
                for decoy in DECOYS:
                    self.assertNotIn(decoy, caption)

    def test_the_headcount_column_never_counts_the_other_kind_of_place(self):
        # A few early field tables head their only headcount "Зачислено
        # человек" and leave the kind of place to the page, so the caption is
        # allowed to name this kind or neither — never the other one.
        for level, funding, year, path in downloaded():
            records = html.records(net.text(path))
            if not records:
                continue
            caption = hse.columns(list(records[0]), funding)["students"].lower()
            other = hse.PLACES["paid" if funding == "budget" else "budget"]
            with self.subTest(level=level, funding=funding, year=year):
                self.assertNotIn(other, caption)


if __name__ == "__main__":
    unittest.main()
