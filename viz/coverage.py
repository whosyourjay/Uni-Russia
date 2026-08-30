"""Calendar of the national ЕГЭ distributions behind the ability model."""

from lib.paths import data_path
from lib.tsvio import read_rows
from viz import common
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch, Rectangle

NAME = "ege-distribution-calendar.png"
YEARS = tuple(range(2017, 2026))
SUBJECTS = (
    ("russian", "Russian"),
    ("mathematics", "Mathematics"),
    ("physics", "Physics"),
    ("chemistry", "Chemistry"),
    ("biology", "Biology"),
    ("informatics", "Informatics"),
    ("history", "History"),
    ("social-studies", "Social studies"),
    ("geography", "Geography"),
    ("literature", "Literature"),
    ("foreign-language", "Foreign languages"),
    ("chinese", "Chinese"),
)
ALIASES = {name: "foreign-language" for name in
           ("english", "french", "german", "spanish")}
COLOURS = (common.SURFACE, "#d9d7d0", "#e1bd96", "#72a9c5", "#174d70")
LABELS = ("No usable distribution", "Mean only", "Chart in report",
          "Recovered 20-point bands", "Recovered full score curve")


def key(subject):
    return ALIASES.get(subject, subject)


def cells():
    """Highest available evidence class for every subject-year."""
    found = {}
    for row in read_rows(data_path("ege-report-coverage.tsv")):
        year, subject = int(row["year"]), key(row["subject"])
        if year not in YEARS:
            continue
        charts = any(row[column] for column in
                     ("distribution_pages", "primary_distribution_pages",
                      "test_distribution_pages", "score_band_pages"))
        level = 2 if charts else (1 if row["mean_test_score"] else 0)
        found[(year, subject)] = max(level, found.get((year, subject), 0))
    for row in read_rows(data_path("ege-score-distributions.tsv")):
        year, subject = int(row["year"]), key(row["subject"])
        if year in YEARS:
            level = 4 if "vector curve" in row["method"] else 3
            found[(year, subject)] = max(level, found.get((year, subject), 0))
    return found


def model():
    return {int(row["year"]): row for row in
            read_rows(data_path("cohort-model.tsv"))}


def draw_matrix(axis, evidence):
    matrix = [[evidence.get((year, subject), 0) for year in YEARS]
              for subject, _ in SUBJECTS]
    axis.imshow(matrix, cmap=ListedColormap(COLOURS), vmin=-0.5, vmax=4.5,
                interpolation="nearest", aspect="auto")
    axis.set_xticks(range(len(YEARS)), YEARS)
    axis.xaxis.tick_top()
    axis.tick_params(axis="x", pad=8)
    axis.set_yticks(range(len(SUBJECTS)), [label for _, label in SUBJECTS])
    axis.set_xticks([value - 0.5 for value in range(1, len(YEARS))], minor=True)
    axis.set_yticks([value - 0.5 for value in range(1, len(SUBJECTS))], minor=True)
    axis.grid(which="minor", color=common.SURFACE, linewidth=2.2)
    axis.tick_params(which="minor", bottom=False, left=False)
    axis.spines[:].set_visible(False)
    for row, values in enumerate(matrix):
        for column, level in enumerate(values):
            if level == 1:
                axis.text(column, row, "•", ha="center", va="center",
                          color=common.MUTED, fontsize=11)
            elif level == 4:
                axis.text(column, row, "curve", ha="center", va="center",
                          color="white", fontsize=7, fontweight="semibold")


def draw_model(axis, rows):
    axis.set_xlim(-0.5, len(YEARS) - 0.5)
    axis.set_ylim(0, 1.35)
    axis.axis("off")
    axis.text(-0.58, 0.48, "CDF used", ha="right", va="center", fontsize=8,
              color=common.MUTED)
    for column, year in enumerate(YEARS):
        row = rows[year]
        carried = row["carried"] == "yes"
        colour = common.BROWN if carried else common.GREEN
        axis.add_patch(Rectangle((column - 0.38, 0.2), 0.76, 0.56,
                                 facecolor=colour, alpha=0.16,
                                 edgecolor=colour, linewidth=1.2))
        label = (f"← {row['distribution_year']}" if carried else
                 f"{row['subject_distributions']} subj.")
        axis.text(column, 0.48, label, ha="center", va="center", fontsize=7.4,
                  color=colour, fontweight="semibold")
    axis.text(-0.47, 1.08, "2011–16 also carry → 2017", ha="left", va="center",
              fontsize=7.5, color=common.BROWN)


def main():
    figure, (matrix_axis, model_axis) = common.plt.subplots(
        2, 1, figsize=(11.7, 7.2), facecolor=common.SURFACE,
        gridspec_kw={"height_ratios": (11, 1.5), "hspace": 0.16})
    matrix_axis.set_facecolor(common.SURFACE)
    model_axis.set_facecolor(common.SURFACE)
    draw_matrix(matrix_axis, cells())
    draw_model(model_axis, model())
    handles = [Patch(facecolor=COLOURS[level], edgecolor=common.GRID,
                     label=LABELS[level]) for level in range(1, 5)]
    figure.legend(handles=handles, loc="upper right", bbox_to_anchor=(0.965, 0.88),
                  frameon=False, ncol=4, fontsize=7.5)
    figure.subplots_adjust(left=0.14, right=0.97, top=0.79, bottom=0.13,
                           hspace=0.16)
    common.finish(
        figure, NAME, "Where the Russian ability curve actually comes from",
        "Recovered national ЕГЭ distributions by observation year",
        "Only blue cells feed the empirical CDF. Tan cells mark a distribution "
        "chart in that year's FIPI report that did not yield a recovered test-score "
        "CDF; grey dots are means without a distribution. The model averages the "
        "available subjects and carries the nearest observed year where necessary.",
        layout=False)


if __name__ == "__main__":
    main()
