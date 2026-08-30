#!/usr/bin/env python3
"""Turn the admitted population into a score-to-percentile table.

Russia publishes no national distribution of exam scores in machine-readable
form: the FIPI subject reports draw it as a picture, and the statistical
services that hold the numbers refuse automated requests. What is published is
every admitted group's average and headcount, and the size of the exam cohort.
Walking the groups from the highest average down gives a rank for each score,
the same shape as a Chinese 一分一段 table, on two assumptions: an admitted
student ranks where the group's average ranks, and every one of them sat this
year's exam.
"""

from lib import admissions
from lib.paths import data_path, path
from lib.tsvio import number, read_rows, write_rows

NATIONAL = data_path("ege-national.tsv")
STEPS = data_path("cohort-steps.tsv")
MODEL = data_path("cohort-model.tsv")
POOL = path("assessment-pool.tsv")


def exam_cohort():
    """Exam participants per year, from the compulsory Russian paper."""
    return {int(row["year"]): number(row["participants"])
            for row in read_rows(NATIONAL)}


def admitted(year):
    """Every admitted group of the year, at the finest level published."""
    return [row for row in admissions.cells("field", year)
            if row["scored_mean"] is not None]


def steps(year, base):
    """One row per distinct score, carrying the rank that score reaches."""
    totals = {}
    for row in admitted(year):
        score = round(row["scored_mean"], 1)
        totals[score] = totals.get(score, 0) + row["students"]
    above = 0
    for score in sorted(totals, reverse=True):
        above += totals[score]
        yield {"year": year, "score": score, "admits_at_or_above": above,
               "percentile": round(100.0 * (1.0 - above / base), 4)}


def pool_row(year, base):
    """The one line `compare/` reads to place this scale on a population."""
    return {"year": year, "percentile_counts": "ЕГЭ", "B": int(base),
            "B_display": f"{round(base / 1000):,}k", "cohort_scaled": "no",
            "source": "Russian-language EGE participants in the main period, "
                      "the compulsory paper every school leaver sits"}


def whole_intake(year):
    """Scored admits counted at the university level, which the field tables
    fall short of because a small group gets no field row of its own."""
    return sum(row["students"] for row in admissions.cells("university", year)
               if row["scored_mean"] is not None)


def main():
    base = exam_cohort()
    table, model = [], []
    for year in sorted(set(admissions.years("field")) & set(base)):
        rows = list(steps(year, base[year]))
        walked, intake = rows[-1]["admits_at_or_above"], whole_intake(year)
        table.extend(rows)
        model.append({"year": year, "exam_cohort": int(base[year]),
                      "scored_admits": walked, "whole_intake": intake,
                      "field_coverage": round(walked / intake, 4),
                      "admitted_share": round(walked / base[year], 4),
                      "lowest_percentile": rows[-1]["percentile"]})
    print(f"wrote {write_rows(STEPS, table):,} score steps to {STEPS}")
    print(f"wrote {write_rows(MODEL, model):,} years to {MODEL}")
    latest = model[-1]["year"]
    write_rows(POOL, [pool_row(latest, base[latest])])
    print(f"wrote the {latest} assessment pool to {POOL}")


if __name__ == "__main__":
    main()
