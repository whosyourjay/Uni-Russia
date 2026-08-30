#!/usr/bin/env python3
"""Digitize national test-score distributions in the FIPI PDF reports."""

import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from lib.paths import data_path, path
from lib.pdf import clean_text, pdf_text
from lib.tsvio import read_rows, write_rows

COVERAGE = data_path("ege-report-coverage.tsv")
TARGET = data_path("ege-score-distributions.tsv")
POINT = re.compile(r"[ML]\s*(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)")
DASH = r"\s*[–—-]\s*"
BAND_HEADER = re.compile(DASH.join(("0", r"20\s+21", r"40\s+41", r"60\s+61",
                                    r"80\s+81", "100")))
PERCENT = r"(\d{1,3}(?:[,.]\d+)?)%"
BAND_ROW = re.compile(r"\b(20\d{2})\s+(?:\d{2}(?:[,.]\d+)?\s+)?" +
                      r"\s+".join((PERCENT,) * 5))
BAND_SCORES = (0, 20, 40, 60, 80, 100)
# Full test-score curves which remain vector data in the downloaded PDF.
VECTOR_CURVES = {(2023, "russian"): (5, 68.65)}


def reports():
    """One row per downloaded report, as recorded by the coverage pass."""
    for row in read_rows(COVERAGE):
        yield int(row["year"]), row["subject"], path(row["source"]), row["source"]


def cdf_rows(year, subject, points, report_year, method, source):
    """Attach provenance to ascending `(score, percentile)` points."""
    for score, percentile in points:
        yield {"year": year, "subject": subject, "score": round(score, 3),
               "percentile": round(percentile, 4), "report_year": report_year,
               "method": method, "source": source}


def band_points(shares):
    """CDF endpoints from the five published 20-point score bands."""
    scale = 100.0 / sum(shares)
    cumulative = 0.0
    points = [(0, 0.0)]
    for score, share in zip(BAND_SCORES[1:], shares):
        cumulative += share * scale
        points.append((score, cumulative))
    return points


def band_tables():
    """Best source for every subject-year five-band distribution."""
    chosen = {}
    for report_year, subject, pdf, source in reports():
        text = clean_text(pdf_text(pdf))
        for header in BAND_HEADER.finditer(text):
            block = text[header.end():header.end() + 1200]
            for found in BAND_ROW.finditer(block):
                exam_year = int(found.group(1))
                shares = [float(value.replace(",", "."))
                          for value in found.groups()[1:]]
                if not 99.0 <= sum(shares) <= 101.0:
                    continue
                key = exam_year, subject
                candidate = (abs(report_year - exam_year), report_year,
                             shares, source)
                if key not in chosen or candidate[:2] < chosen[key][:2]:
                    chosen[key] = candidate
    return chosen


def svg_elements(pdf, page):
    """Vector elements on one PDF page, rendered losslessly by Poppler."""
    with tempfile.TemporaryDirectory() as directory:
        target = f"{directory}/page.svg"
        subprocess.run(["pdftocairo", "-f", str(page), "-l", str(page),
                        "-svg", pdf, target], check=True)
        yield from ET.parse(target).iter()


def coordinates(element):
    """M/L coordinates from an SVG path."""
    return [(float(x), float(y)) for x, y in POINT.findall(element.get("d", ""))]


def plotted_line(pdf, page):
    """The longest non-grid line spanning a chart."""
    candidates = []
    for element in svg_elements(pdf, page):
        points = coordinates(element)
        if element.get("fill") != "none" or len(points) < 20:
            continue
        xs, ys = zip(*points)
        if max(xs) - min(xs) > 300 and max(ys) - min(ys) > 20:
            candidates.append(points)
    return max(candidates, key=len)


def curve_points(pdf, page, expected_mean):
    """CDF points recovered from a vector line's plotted marker centers."""
    plotted = sorted(plotted_line(pdf, page))
    low_x, high_x = plotted[0][0], plotted[-1][0]
    baseline = min(y for _, y in plotted)
    masses = [(round(100 * (x - low_x) / (high_x - low_x)), y - baseline)
              for x, y in plotted]
    total = sum(mass for _, mass in masses)
    mean = sum(score * mass for score, mass in masses) / total
    if abs(mean - expected_mean) > 1.0:
        raise ValueError(f"digitized mean {mean:.2f}, expected {expected_mean:.2f}")
    cumulative, points = 0.0, []
    for score, mass in masses:
        cumulative += 100.0 * mass / total
        points.append((score, cumulative))
    return points


def distribution_rows():
    """Published band tables, superseded where a full vector curve exists."""
    report_index = {(year, subject): (pdf, source)
                    for year, subject, pdf, source in reports()}
    curves = set(VECTOR_CURVES)
    for (year, subject), (_, report_year, shares, source) in band_tables().items():
        if (year, subject) not in curves:
            yield from cdf_rows(year, subject, band_points(shares), report_year,
                                "published 20-point bands", source)
    for key, (page, expected_mean) in VECTOR_CURVES.items():
        pdf, source = report_index[key]
        points = curve_points(pdf, page, expected_mean)
        yield from cdf_rows(*key, points, key[0], "digitized vector curve", source)


def write_distributions():
    rows = sorted(distribution_rows(), key=lambda row: (row["year"],
                                                         row["subject"],
                                                         row["score"]))
    print(f"wrote {write_rows(TARGET, rows):,} CDF points to {TARGET}")


if __name__ == "__main__":
    write_distributions()
