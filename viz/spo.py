"""Relate СПО application pressure to the certificate-grade gate."""

import statistics

from fetch.spo import DEFAULT_YEAR, index_path, institutions
from lib import net
from lib.paths import data_path
from lib.tsvio import number, read_rows
from viz import common
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

NAME = "spo-demand-gpa.png"
BINS = (1, 1.5, 2, 3, 5, 8, 13, 21, 34, 68)


def rows():
    """Schools with both budget entrant GPA and application pressure."""
    found = []
    for row in read_rows(data_path("spo-institutions.tsv")):
        budget = number(row["budget_admitted_gpa"])
        paid = number(row["paid_admitted_gpa"])
        applications = number(row["applications_per_100_budget_places"])
        if budget is None or applications is None or applications <= 0:
            continue
        found.append({"school": row["school"], "gpa": budget,
                      "applications": applications / 100,
                      "gap": None if paid is None else budget - paid})
    return found


def medians(found):
    """Median budget GPA in fixed log-spaced demand bands."""
    out = []
    for lower, upper in zip(BINS, BINS[1:]):
        values = [row["gpa"] for row in found
                  if lower <= row["applications"] < upper]
        if values:
            out.append(((lower * upper) ** 0.5, statistics.median(values)))
    return out


def label_outliers(axis, found):
    """Name the highest-pressure schools without turning labels into a thicket."""
    leaders = sorted(found, key=lambda row: row["applications"], reverse=True)[:2]
    offsets = ((-7, -18), (-7, 10))
    for row, offset in zip(leaders, offsets):
        axis.scatter(row["applications"], row["gpa"], s=36,
                     facecolor=common.SURFACE, edgecolor=common.INK,
                     linewidth=1.0, zorder=5)
        axis.annotate(common.shorten(row["school"], 38),
                      (row["applications"], row["gpa"]), xytext=offset,
                      textcoords="offset points", ha="right",
                      va="bottom" if offset[1] > 0 else "top", fontsize=7.1,
                      color=common.INK, arrowprops={"arrowstyle": "-",
                                                   "color": common.MUTED,
                                                   "linewidth": 0.6})


def draw(figure, axis, found):
    unpaired = [row for row in found if row["gap"] is None]
    paired = [row for row in found if row["gap"] is not None]
    axis.scatter([row["applications"] for row in unpaired],
                 [row["gpa"] for row in unpaired], s=11, color="#c9c6be",
                 alpha=0.38, linewidths=0, label="paid GPA unavailable")
    colour = LinearSegmentedColormap.from_list(
        "funding_gap", [common.ORANGE, common.SURFACE, common.BLUE])
    points = axis.scatter([row["applications"] for row in paired],
                          [row["gpa"] for row in paired],
                          c=[row["gap"] for row in paired], s=15, alpha=0.55,
                          cmap=colour,
                          norm=TwoSlopeNorm(vmin=-0.75, vcenter=0, vmax=0.75),
                          linewidths=0)
    trend = medians(found)
    axis.plot([point[0] for point in trend], [point[1] for point in trend],
              color=common.INK, linewidth=2.4, zorder=4,
              label="median within demand band")
    axis.scatter([point[0] for point in trend], [point[1] for point in trend],
                 s=25, color=common.INK, edgecolor=common.SURFACE,
                 linewidth=0.8, zorder=4)
    axis.axhline(4, color=common.MUTED, linewidth=0.8, linestyle="--", alpha=0.6)
    axis.text(1.03, 4.025, "4.0 certificate average", fontsize=7.5,
              color=common.MUTED, va="bottom")
    label_outliers(axis, found)
    axis.set_xscale("log")
    axis.set_xlim(0.9, 85)
    axis.set_ylim(2.65, 5.05)
    axis.set_xticks((1, 2, 5, 10, 20, 50), ("1", "2", "5", "10", "20", "50"))
    axis.grid(color=common.GRID, linewidth=0.65)
    axis.set_axisbelow(True)
    axis.set_xlabel("applications per budget place · log scale", color=common.MUTED)
    axis.set_ylabel("mean certificate GPA of budget entrants", color=common.MUTED)
    axis.legend(loc="lower right", frameon=False, fontsize=8)
    bar = figure.colorbar(points, ax=axis, pad=0.025, shrink=0.8)
    bar.set_label("budget GPA minus paid GPA", color=common.MUTED, fontsize=8)
    bar.ax.tick_params(colors=common.MUTED, labelsize=7, length=0)


def main():
    found = rows()
    paired = [row for row in found if row["gap"] is not None]
    budget_higher = sum(row["gap"] > 0 for row in paired)
    indexed = len(institutions(net.text(index_path(DEFAULT_YEAR)), DEFAULT_YEAR))
    downloaded = sum(1 for _ in read_rows(data_path("spo-institutions.tsv")))
    figure, axis = common.start((11.2, 7.4))
    draw(figure, axis, found)
    common.finish(
        figure, NAME, "Demand and the СПО gate",
        f"{DEFAULT_YEAR} retained pages · {len(found):,} schools plotted from "
        f"{downloaded:,}/{indexed:,} indexed institutions",
        f"Each point is a school, not a seat. Among {len(paired):,} schools with "
        f"both funding averages, budget GPA is higher in "
        f"{100 * budget_higher / len(paired):.0f}%. The retained pages are an "
        "incomplete download, so the figure describes this collection rather than "
        "a national sample; current enrollment is not used as admission volume.")


if __name__ == "__main__":
    main()
