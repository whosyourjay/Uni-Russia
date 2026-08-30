"""Compare budget and paid selectivity within matched university fields."""

import math

from lib import admissions
from lib.english import english_names
from lib.percentile import percentile
from viz import common
from matplotlib.colors import LinearSegmentedColormap, LogNorm

NAME = "budget-paid-gap.png"
MINIMUM_LABEL_SEATS = 120
LABELS_PER_SIDE = (2, 1)


def pairs(year):
    """Matched budget and paid rows for the same university and broad field."""
    source = admissions.cells("field", year)
    english = english_names({row[column] for row in source
                             for column in ("university", "field")})
    grouped = {}
    for row in source:
        if row["scored_mean"] is not None:
            grouped.setdefault((row["university"], row["field"]), {})[
                row["funding"]] = row
    found = []
    for (school, field), rows in grouped.items():
        if not {"budget", "paid"} <= rows.keys():
            continue
        budget, paid = rows["budget"], rows["paid"]
        budget_place = percentile(budget["scored_mean"], year)
        paid_place = percentile(paid["scored_mean"], year)
        if budget_place is None or paid_place is None:
            continue
        seats = budget["students"] + paid["students"]
        found.append({"school": english.get(school, school),
                      "field": english.get(field, field),
                      "budget": budget_place, "paid": paid_place,
                      "gap": budget_place - paid_place, "seats": seats})
    return found


def material_outliers(rows):
    """Large, consequential gaps, with no school labeled twice."""
    eligible = [row for row in rows if row["seats"] >= MINIMUM_LABEL_SEATS]
    score = lambda row: abs(row["gap"]) * math.sqrt(row["seats"])
    sides = (sorted((row for row in eligible if row["gap"] >= 0),
                    key=score, reverse=True),
             sorted((row for row in eligible if row["gap"] < 0),
                    key=score, reverse=True))
    found, schools = [], set()
    for side, limit in zip(sides, LABELS_PER_SIDE):
        taken = 0
        for row in side:
            if row["school"] in schools:
                continue
            found.append(row)
            schools.add(row["school"])
            taken += 1
            if taken == limit:
                break
    return found


def annotate(axis, rows):
    offsets = ((7, 12), (-7, 12), (7, -20))
    for row, offset in zip(material_outliers(rows), offsets):
        align = "left" if offset[0] > 0 else "right"
        axis.scatter(row["paid"], row["budget"], s=36,
                     facecolor=common.SURFACE, edgecolor=common.INK,
                     linewidth=1.0, zorder=5)
        axis.annotate(common.shorten(row["school"], 30),
                      (row["paid"], row["budget"]), xytext=offset,
                      textcoords="offset points", ha=align,
                      va="bottom" if offset[1] > 0 else "top", fontsize=7.3,
                      color=common.INK, arrowprops={"arrowstyle": "-",
                                                   "color": common.MUTED,
                                                   "linewidth": 0.6})


def draw(figure, axis, rows):
    """Seat-mass hexagons around the equal-selectivity diagonal."""
    x = [row["paid"] for row in rows]
    y = [row["budget"] for row in rows]
    weights = [row["seats"] for row in rows]
    colour = LinearSegmentedColormap.from_list(
        "seat_mass", [common.SURFACE, "#a9c9d9", common.BLUE, "#123d5a"])
    mesh = axis.hexbin(x, y, C=weights, reduce_C_function=sum, gridsize=35,
                       mincnt=1, cmap=colour, norm=LogNorm(), linewidths=0.25,
                       edgecolors=common.SURFACE)
    axis.plot([0, 100], [0, 100], color=common.MUTED, linewidth=1.0,
              linestyle="--", zorder=2)
    axis.text(37, 39, "same selectivity", color=common.MUTED, fontsize=8,
              rotation=45, ha="center", va="bottom")
    axis.fill_between([0, 100], [0, 100], [100, 100], color=common.BLUE,
                      alpha=0.035, zorder=0)
    axis.fill_between([0, 100], [0, 0], [0, 100], color=common.ORANGE,
                      alpha=0.035, zorder=0)
    axis.text(4, 95, "budget list higher", color=common.BLUE, fontsize=9)
    axis.text(96, 4, "paid list higher", color=common.ORANGE, fontsize=9,
              ha="right")
    annotate(axis, rows)
    axis.set_xlim(0, 100)
    axis.set_ylim(0, 100)
    axis.set_aspect("equal", adjustable="box")
    axis.grid(color=common.GRID, linewidth=0.6)
    axis.set_axisbelow(True)
    axis.set_xlabel("paid-list ability percentile", color=common.MUTED)
    axis.set_ylabel("budget-list ability percentile", color=common.MUTED)
    bar = figure.colorbar(mesh, ax=axis, pad=0.025, shrink=0.8)
    bar.set_label("seats in matched cohorts", color=common.MUTED, fontsize=8)
    bar.ax.tick_params(colors=common.MUTED, labelsize=7, length=0)


def main():
    year = max(admissions.years("field"))
    rows = pairs(year)
    higher = sum(row["budget"] > row["paid"] for row in rows)
    gaps = sorted(row["gap"] for row in rows)
    median = gaps[len(gaps) // 2]
    figure, axis = common.start((10.4, 8.2))
    draw(figure, axis, rows)
    common.finish(
        figure, NAME, "Same exams, separate lists",
        f"{year} · {len(rows):,} matched university–field cohorts · budget is "
        f"higher in {100 * higher / len(rows):.0f}% · median gap {median:+.1f} points",
        "Each hexagon sums budget and paid seats for matched HSE broad-field rows. "
        "A broad field may pool exact programmes with different subject sets; values "
        "are de-placeholdered group proxies, and university-test admits remain "
        "unseparated.")


if __name__ == "__main__":
    main()
