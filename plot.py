"""Draw what a school's median `ability` summarizes, and who skipped the exam.

The left panel gives every field group its own dot, budget places against paid
ones, so a university reads as the spread it is rather than the one number the
table prints. The right panel plots the olympiad share of a university's budget
intake against its ability: the students the monitoring scores at a nominal 100
sit almost entirely at the top of the scale.
"""

import collections

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from lib import admissions  # noqa: E402
from lib.paths import ranking_path  # noqa: E402
from lib.percentile import percentile  # noqa: E402
from lib.tsvio import read_rows  # noqa: E402

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
MUTED = "#52514e"
BUDGET = "#8a8a86"
PAID = "#eb6834"
MEAN = "#2a78d6"
GRID = "#e4e3df"

TARGET = ranking_path("ability-spread.png")
TOP = 18
# Dot area in points squared for a group admitting one student, and its cap.
DOT_SCALE = 0.7
DOT_MAX = 110
BIG = 400


def shorten(name, width=44):
    """Trim the middle, because these names differ in their last few words."""
    if len(name) <= width:
        return name
    head = (width - 3) * 2 // 3
    return f"{name[:head]}…{name[len(name) - (width - 3 - head):]}"


def universities(year):
    rows = [row for row in read_rows(ranking_path("ability-universities.tsv"))
            if int(row["year"]) == year and row["ability"]]
    rows.sort(key=lambda row: -float(row["ability"]))
    return rows


def groups(year, funding):
    by_university = collections.defaultdict(list)
    for row in admissions.cells("field", year, funding):
        if row["scored_mean"] is not None:
            by_university[row["university"]].append(row)
    return by_university


def spread(axes, year):
    rows = universities(year)[:TOP]
    budget, paid = groups(year, "budget"), groups(year, "paid")
    for place, row in enumerate(rows):
        name = row["school"]
        for source, color in ((budget, BUDGET), (paid, PAID)):
            for group in source.get(name, []):
                axes.scatter(percentile(group["scored_mean"], year), place,
                             s=min(DOT_MAX, DOT_SCALE * group["students"]),
                             color=color, alpha=0.5, linewidths=0)
        axes.scatter(float(row["ability"]), place, s=40, color=MEAN, zorder=3)
    axes.set_yticks(range(len(rows)))
    axes.set_yticklabels([shorten(row["school"]) for row in rows], fontsize=7)
    axes.invert_yaxis()
    axes.set_xlabel("percentile of the exam cohort", fontsize=8, color=MUTED)
    axes.set_title(f"{year}: route–field groups behind a school median",
                   fontsize=9, color=INK)
    axes.scatter([], [], s=30, color=BUDGET, label="бюджетное место")
    axes.scatter([], [], s=30, color=PAID, label="платное место")
    axes.scatter([], [], s=30, color=MEAN, label="weighted-median ability")
    axes.legend(fontsize=7, frameon=False, loc="upper left")


def olympiads(axes, year):
    for row in universities(year):
        seats = int(row["budget_seats"])
        if seats < 100:
            continue
        share = 100.0 * int(row["olympiad_seats"]) / seats
        axes.scatter(float(row["ability"]), share, s=min(BIG, seats / 12.0),
                     color=MEAN, alpha=0.35, linewidths=0)
    axes.set_xlabel("university ability, percentile of the exam cohort",
                    fontsize=8, color=MUTED)
    axes.set_ylabel("olympiad winners, % of budget places", fontsize=8,
                    color=MUTED)
    axes.set_title(f"{year}: admitted without sitting the exam", fontsize=9,
                   color=INK)


def main():
    year = max(admissions.years("field"))
    figure, (left, right) = plt.subplots(1, 2, figsize=(13, 5.6),
                                         facecolor=SURFACE,
                                         gridspec_kw={"wspace": 0.3})
    for axes in (left, right):
        axes.set_facecolor(SURFACE)
        axes.grid(color=GRID, linewidth=0.6)
        axes.set_axisbelow(True)
        for side in axes.spines.values():
            side.set_visible(False)
        axes.tick_params(colors=MUTED, labelsize=8, length=0)
    spread(left, year)
    olympiads(right, year)
    figure.subplots_adjust(left=0.22, right=0.97, top=0.92, bottom=0.1)
    figure.savefig(TARGET, dpi=150)
    print(f"wrote {TARGET}")


if __name__ == "__main__":
    main()
