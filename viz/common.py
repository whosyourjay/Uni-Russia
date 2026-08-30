"""Shared editorial style for the Russia figures."""

import os
import tempfile
import textwrap

os.environ.setdefault("MPLCONFIGDIR",
                      os.path.join(tempfile.gettempdir(), "uni-russia-mpl"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from lib.paths import ranking_path  # noqa: E402

SURFACE = "#faf8f3"
INK = "#17212b"
MUTED = "#65717d"
GRID = "#dedbd2"
BLUE = "#2474a6"
ORANGE = "#ec6b35"
BROWN = "#9b6846"
GREEN = "#3d9078"
FONTS = ["Avenir Next", "Helvetica Neue", "Arial Unicode MS", "DejaVu Sans"]
DPI = 170


def start(figsize):
    """A single clean panel on the project's warm paper background."""
    plt.rcParams["font.family"] = FONTS
    plt.rcParams["axes.unicode_minus"] = False
    figure, axis = plt.subplots(figsize=figsize, facecolor=SURFACE)
    axis.set_facecolor(SURFACE)
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.tick_params(colors=MUTED, labelsize=9, length=0)
    return figure, axis


def finish(figure, name, title, subtitle="", note="", layout=True):
    """Title, note and save a figure into rankings."""
    figure.suptitle(title, x=0.06, y=0.97, ha="left", fontsize=17,
                    fontweight="semibold", color=INK)
    if subtitle:
        figure.text(0.06, 0.925, subtitle, ha="left", va="top", fontsize=10,
                    color=MUTED)
    bottom = 0.05
    if note:
        width = max(80, int(figure.get_figwidth() * 15))
        lines = textwrap.wrap(note, width)
        figure.text(0.06, 0.025, "\n".join(lines), ha="left", va="bottom",
                    fontsize=7.5, color=MUTED, linespacing=1.35)
        bottom = 0.055 + 0.015 * len(lines)
    if layout:
        figure.tight_layout(rect=(0.04, bottom, 0.98, 0.89))
    target = ranking_path(name)
    figure.savefig(target, dpi=DPI, facecolor=SURFACE)
    plt.close(figure)
    print(f"wrote {target}")
    return target


def compact(value):
    """A seat count compact enough to sit beside a mark."""
    if value >= 1000:
        return f"{value / 1000:,.1f}k"
    return f"{value:,.0f}"


def shorten(text, width=48):
    """Keep the distinctive beginning and end of a long school name."""
    if len(text) <= width:
        return text
    left = (width - 1) * 2 // 3
    return f"{text[:left]}…{text[-(width - left - 1):]}"
