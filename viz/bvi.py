"""Show how БВИ placeholder 100s move published university averages."""

from lib import admissions
from lib.english import english_names
from lib.percentile import percentile
from viz import common

NAME = "bvi-placeholder-shift.png"
SHOW = 18
MINIMUM_INTAKE = 100


def points(year):
    """Budget cohorts with both БВИ and non-БВИ students."""
    source = admissions.cells("university", year, "budget")
    english = english_names({row["university"] for row in source})
    found = []
    for row in source:
        non_bvi = row["students"] - row["bvi"]
        if (row["students"] < MINIMUM_INTAKE or row["bvi"] <= 0
                or non_bvi <= 0 or row["mean_ege"] is None
                or row["scored_mean"] is None):
            continue
        published = percentile(row["mean_ege"], year)
        proxy = percentile(row["scored_mean"], year)
        if published is None or proxy is None:
            continue
        found.append({"school": english.get(row["university"], row["university"]),
                      "published": published, "proxy": proxy,
                      "shift": published - proxy, "bvi": row["bvi"],
                      "students": row["students"]})
    return sorted(found, key=lambda row: row["shift"], reverse=True)[:SHOW]


def draw(axis, rows):
    """One leftward correction per institution."""
    rows = list(reversed(rows))
    for position, row in enumerate(rows):
        share = 100 * row["bvi"] / row["students"]
        axis.plot([row["proxy"], row["published"]], [position, position],
                  color=common.BROWN, linewidth=2.2, alpha=0.72, zorder=2)
        axis.scatter(row["published"], position, s=50, facecolor=common.SURFACE,
                     edgecolor=common.BROWN, linewidth=1.7, zorder=3)
        axis.scatter(row["proxy"], position, s=56, color=common.BLUE,
                     edgecolor=common.SURFACE, linewidth=0.7, zorder=4)
        axis.text(row["published"] + 0.7, position,
                  f"−{row['shift']:.1f} pts · {common.compact(row['bvi'])} БВИ"
                  f" ({share:.0f}%)", va="center", fontsize=8,
                  color=common.MUTED)
    axis.set_yticks(range(len(rows)))
    axis.set_yticklabels([common.shorten(row["school"]) for row in rows],
                         fontsize=8.2, color=common.INK)
    axis.axvspan(90, 100, color=common.BLUE, alpha=0.055, zorder=0)
    axis.axvline(90, color=common.BLUE, linewidth=0.9, alpha=0.35)
    axis.grid(axis="x", color=common.GRID, linewidth=0.7)
    axis.set_axisbelow(True)
    left = min(row["proxy"] for row in rows)
    axis.set_xlim(max(0, left - 3), 111)
    axis.set_xlabel("percentile of the ЕГЭ reference cohort", color=common.MUTED)
    axis.scatter([], [], s=50, facecolor=common.SURFACE,
                 edgecolor=common.BROWN, linewidth=1.7,
                 label="published mean, including placeholder 100s")
    axis.scatter([], [], s=56, color=common.BLUE,
                 label="proxy after removing the placeholders")
    axis.legend(loc="lower left", frameon=False, fontsize=8)


def main():
    year = max(admissions.years("university"))
    rows = points(year)
    figure, axis = common.start((12.8, 7.2))
    draw(axis, rows)
    total = sum(row["bvi"] for row in admissions.cells("university", year,
                                                       "budget"))
    common.finish(
        figure, NAME, "How БВИ placeholder 100s bend the leaderboard",
        f"{year} budget intake · {total:,} olympiad admits entered without exams",
        "Shown are the largest percentile shifts among institutions admitting at "
        "least 100 budget students. The blue endpoint is an algebraic group proxy, "
        "not an observed ЕГЭ-only mean: HSE does not separately count university-test "
        "admits.")


if __name__ == "__main__":
    main()
