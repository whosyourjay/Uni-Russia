#!/usr/bin/env python3
"""Build an annual score CDF from FIPI's single-subject distributions.

An annual reference is the equal-weight mean of every subject CDF recovered for
that year. Admission years without observations use the nearest empirical year.
This is a reference for the HSE per-subject score, not an observed distribution
of applicants' three- or four-subject averages.
"""

from lib import admissions
from lib.paths import data_path, path
from lib.percentile import interpolate
from lib.tsvio import number, read_rows, write_rows

NATIONAL = data_path("ege-national.tsv")
DISTRIBUTIONS = data_path("ege-score-distributions.tsv")
STEPS = data_path("cohort-steps.tsv")
MODEL = data_path("cohort-model.tsv")
POOL = path("assessment-pool.tsv")


def exam_cohort():
    """Compulsory Russian-paper participants where FIPI publishes the count."""
    return {int(row["year"]): number(row["participants"])
            for row in read_rows(NATIONAL)}


def empirical_cdfs():
    """Ascending `(score, percentile)` points by exam year and subject."""
    found = {}
    for row in read_rows(DISTRIBUTIONS):
        key = int(row["year"]), row["subject"]
        found.setdefault(key, {"points": [], "method": row["method"]})
        found[key]["points"].append((float(row["score"]),
                                      float(row["percentile"])))
    return found


def nearest_year(year, available):
    """Closest observation, preferring the earlier one on a tie."""
    return min(available, key=lambda candidate: (abs(candidate - year),
                                                  candidate > year, candidate))


def annual_reference(year, cdfs):
    """The year used and its subject distributions."""
    available = sorted({exam_year for exam_year, _ in cdfs})
    source_year = nearest_year(year, available)
    subjects = {subject: value for (exam_year, subject), value in cdfs.items()
                if exam_year == source_year}
    return source_year, subjects


def steps(year, source_year, subjects):
    """Mean subject CDF at every integer score on the common test scale."""
    names = ",".join(sorted(subjects))
    for score in range(101):
        values = [interpolate(value["points"], score)
                  for value in subjects.values()]
        yield {"year": year, "score": score,
               "percentile": round(sum(values) / len(values), 4),
               "distribution_year": source_year, "subjects": names}


def model_row(year, source_year, subjects, cohorts):
    """Audit which empirical distributions support one admission year."""
    methods = [value["method"] for value in subjects.values()]
    return {"year": year, "distribution_year": source_year,
            "carried": "no" if year == source_year else "yes",
            "subject_distributions": len(subjects),
            "subjects": ",".join(sorted(subjects)),
            "vector_curves": methods.count("digitized vector curve"),
            "band_tables": methods.count("published 20-point bands"),
            "exam_cohort": int(cohorts[year]) if year in cohorts else ""}


def pool_row(year, base):
    """The one line `compare/` reads to place this scale on a population."""
    return {"year": year, "percentile_counts": "ЕГЭ", "B": int(base),
            "B_display": f"{round(base / 1000):,}k", "cohort_scaled": "no",
            "source": "Russian-language EGE participants in the main period, "
                      "the compulsory paper every school leaver sits"}


def main():
    cohorts, cdfs = exam_cohort(), empirical_cdfs()
    table, model = [], []
    for year in admissions.years("field"):
        source_year, subjects = annual_reference(year, cdfs)
        table.extend(steps(year, source_year, subjects))
        model.append(model_row(year, source_year, subjects, cohorts))
    print(f"wrote {write_rows(STEPS, table):,} CDF points to {STEPS}")
    print(f"wrote {write_rows(MODEL, model):,} years to {MODEL}")
    latest = max(set(admissions.years("field")) & set(cohorts))
    write_rows(POOL, [pool_row(latest, cohorts[latest])])
    print(f"wrote the {latest} assessment pool to {POOL}")


if __name__ == "__main__":
    main()
