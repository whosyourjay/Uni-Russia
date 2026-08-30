"""Build the self-contained Russian admissions visual report."""

import json
from pathlib import Path

from fetch.spo import DEFAULT_YEAR, index_path, institutions
from lib import admissions, net
from lib.paths import data_path
from lib.tsvio import read_rows
from viz import bvi, coverage, funding, spo

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUTPUT = ROOT / "rankings" / "ability-report.html"


def bvi_data():
    year = max(admissions.years("university"))
    rows = bvi.points(year)
    total = sum(row["bvi"] for row in
                admissions.cells("university", year, "budget"))
    return {"year": year, "total": total, "rows": rows,
            "largestShift": max(row["shift"] for row in rows)}


def funding_data():
    year = max(admissions.years("field"))
    rows = funding.pairs(year)
    gaps = sorted(row["gap"] for row in rows)
    higher = sum(row["gap"] > 0 for row in rows)
    return {"year": year, "rows": rows,
            "higherPercent": 100 * higher / len(rows),
            "medianGap": gaps[len(gaps) // 2],
            "seats": sum(row["seats"] for row in rows),
            "labels": funding.material_outliers(rows)}


def coverage_data():
    evidence = coverage.cells()
    model = coverage.model()
    matrix = [[evidence.get((year, subject), 0) for year in coverage.YEARS]
              for subject, _ in coverage.SUBJECTS]
    model_rows = [{"year": year,
                   "distributionYear": int(model[year]["distribution_year"]),
                   "carried": model[year]["carried"] == "yes",
                   "subjects": int(model[year]["subject_distributions"])}
                  for year in coverage.YEARS]
    return {"years": coverage.YEARS, "subjects": coverage.SUBJECTS,
            "labels": coverage.LABELS, "matrix": matrix, "model": model_rows,
            "recovered": sum(level >= 3 for row in matrix for level in row),
            "curves": sum(level == 4 for row in matrix for level in row),
            "carriedYears": sum(row["carried"] for row in model_rows)}


def spo_data():
    found = spo.rows()
    paired = [row for row in found if row["gap"] is not None]
    higher = sum(row["gap"] > 0 for row in paired)
    downloaded = sum(1 for _ in read_rows(data_path("spo-institutions.tsv")))
    indexed = len(institutions(net.text(index_path(DEFAULT_YEAR)), DEFAULT_YEAR))
    return {"year": DEFAULT_YEAR, "rows": found, "trend": spo.medians(found),
            "paired": len(paired), "higherPercent": 100 * higher / len(paired),
            "downloaded": downloaded, "indexed": indexed}


def page_data():
    return {"bvi": bvi_data(), "funding": funding_data(),
            "coverage": coverage_data(), "spo": spo_data()}


def render(data, output=OUTPUT):
    page = (HERE / "report.html").read_text(encoding="utf-8")
    for marker, filename in (("__CSS__", "report.css"),
                             ("__JS__", "report.js")):
        page = page.replace(marker, (HERE / filename).read_text(encoding="utf-8"))
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    page = page.replace("__DATA__", payload.replace("</", "<\\/"))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding="utf-8")
    print(f"wrote {output} ({len(page.encode('utf-8')) / 1e6:.1f} MB)")
    return output


def main():
    render(page_data())


if __name__ == "__main__":
    main()
