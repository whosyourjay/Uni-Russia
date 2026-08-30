"""Read the monitoring's result tables off its pages.

The pages carry one filter table and one result table, both plain grids without
merged cells, so a row is its cells in order.
"""

import html as entities
import re

TABLE = re.compile(r"<table[^>]*>.*?</table>", re.S)
ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S)


def strip(markup):
    """One cell's text, with its tags and entities resolved away."""
    plain = re.sub(r"<[^>]+>", " ", markup)
    return " ".join(entities.unescape(plain).replace("\xa0", " ").split())


def rows(markup):
    """Every row of a table as a list of cell strings."""
    return [[strip(cell) for cell in CELL.findall(row)]
            for row in ROW.findall(markup)]


def result_table(page):
    """The monitoring's data table, which carries the id its script sorts on."""
    for table in TABLE.findall(page):
        if 'id="transparence_t"' in table[:200]:
            return table
    raise ValueError("no result table on the page")


def records(page):
    """Header-keyed dictionaries for one downloaded rating page."""
    grid = [row for row in rows(result_table(page)) if row]
    header, body = grid[0], grid[1:]
    return [dict(zip(header, row)) for row in body if len(row) == len(header)]


def links(page):
    """Every (href, text) pair on a page, in document order."""
    pattern = re.compile(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.S)
    return [(entities.unescape(href), strip(label))
            for href, label in pattern.findall(page)]
