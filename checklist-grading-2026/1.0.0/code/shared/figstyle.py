"""The Learning Design Alliance chart style for a paper's static figures (matplotlib).

A release's figure script imports this instead of carrying its own palette, so the printed figures
match the report they sit in (board/report/brand.css) and the LDA site:

    from shared import figstyle
    figstyle.apply()                      # rcParams: cream surface, ink text, hairline axes
    ax.plot(x, y, color=figstyle.S1)      # categorical slots in fixed order: S1, S2, S3, S4

The categorical slots pass the dataviz validator (scripts/validate_palette.js in the dataviz skill)
against the cream surface: lightness band, chroma floor, colour-blind and normal-vision separation,
and 3:1 contrast. S4 (gold) is under 3:1 against cream, so a figure that uses it labels those marks
directly. Assign slots in order and keep a series' colour when a filter drops others; a fifth series
folds into "other" or a small multiple, never a new hue. S1_LIGHT is the second shade of a dumbbell.

Fonts: DM Sans when it is installed, then the fallbacks Paper VI used. A figure's bytes depend on the
font found, so a release's figures are rebuilt on one machine.
"""

from __future__ import annotations

S1, S2, S3, S4 = "#3554dc", "#e8682a", "#14a38a", "#c99a00"   # lapis, orange, teal, gold
S1_LIGHT = "#a7b4f2"
SURF = "#fffbf5"                       # cream, the LDA ground
INK, INK2, MUTED = "#0e1240", "#353a6e", "#676b93"
LAPIS = "#122fb2"                      # titles and accents, never a data series
GRID, AXIS = "#e6e2ef", "#bdbad6"
WASH = "#f3efe6"


def apply() -> None:
    """Set matplotlib's rcParams to the LDA style. Call once, before drawing."""
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DM Sans", "Liberation Sans", "Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 8,
        "axes.titlesize": 9,
        "axes.titleweight": "normal",
        "axes.titlecolor": LAPIS,
        "axes.titlelocation": "left",
        "axes.labelsize": 8,
        "axes.labelcolor": INK2,
        "axes.edgecolor": AXIS,
        "axes.linewidth": 0.6,
        "axes.facecolor": SURF,
        "axes.prop_cycle": plt.cycler(color=[S1, S2, S3, S4]),
        "figure.facecolor": SURF,
        "savefig.facecolor": SURF,
        "xtick.color": AXIS,
        "ytick.color": AXIS,
        "xtick.labelcolor": INK2,
        "ytick.labelcolor": INK2,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "legend.frameon": False,
        "legend.labelcolor": INK2,
        "lines.linewidth": 2,
        "svg.hashsalt": "lda",
    })
