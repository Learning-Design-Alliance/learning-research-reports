"""Figure 1 of Paper II (research/article/what-learner-records-can-say-about-a-prerequisite-edge.md):
how the positivity atlas gives each ordered pair (a, b) its state. Section 4.2 drawn as a diagram.

Release learning-graph-budget-2026, analysis `figure-atlas`. No model call and no corpus is read. The
figure is a schematic, not a plot: it carries no estimate. What it does carry are the atlas's rules,
and those are taken from the code that applies them, never typed in:

  the claimed effect (0.10)          shared/edge_state.py CLAIMED_EFFECT
  the cell floor (5 learners)        positivity.py MIN_CELL, also the merge-node stratum floor, because
                                     atlas.py passes min_cell=MIN_CELL to shared/reachability.py
  the readability band (0.01-0.99)   probed from positivity.mde(), which returns None outside it
  80% power, two-sided 5% level      shared/reachability.py and positivity.py Z_ALPHA, Z_BETA

THE CHECKS. The script stops (1) if any of those values differs from what the figure draws, (2) if
Section 4.2 of the article does not print each of them as the figure does (checked in the research
repository; the release's code package does not ship the article, so there it is skipped), and (3) unless
shared/edge_state.classify_edge, run on one constructed case per branch, returns the state the
decision panel shows for that branch, in the panel's order: an unreadable cell is unknown before power
is looked at, an underpowered cell is unknown before the drop is looked at, a drop that reaches the MDE
is supported whether or not the pair is falsifiable, and a powered null is contradicted only when it
is falsifiable. A change to the rules therefore cannot leave a stale figure in the paper.

Design (the dataviz method, light mode, print): text in ink, never in a series colour; the three states
in fixed slots (supported #1baf7a, contradicted #eb6834, unknown grey) with their names written on
every box, so no state is read from colour alone; decisions in a blue wash.

    python3 studies/identifiability/overlap/figure_atlas.py
writes research/article/figures/learning-graph-budget-2026/fig1-positivity-atlas.svg and .png (300 dpi),
byte-identical on re-run. matplotlib 3.11.2.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from statistics import NormalDist

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyBboxPatch  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

import positivity  # noqa: E402
import shared.reachability as reach  # noqa: E402
from shared.edge_state import (CLAIMED_EFFECT, CONTRADICTED, SUPPORTED,  # noqa: E402
                               UNKNOWN, classify_edge)

ARTICLE = ROOT / "research" / "article" / "what-learner-records-can-say-about-a-prerequisite-edge.md"
OUT = ROOT / "research" / "article" / "figures" / "learning-graph-budget-2026"
STEM = "fig1-positivity-atlas"

# ------------------------------------------------------------------ palette (dataviz reference, light)
SURF = "#fcfcfb"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
LINE = "#c3c2b7"
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"
FILL = {"decision": "#e6effa", "supported": "#e2f4ec", "contradicted": "#fce9df", "unknown": "#efeeea",
        "plain": SURF}
EDGE = {"decision": S1, "supported": S3, "contradicted": S2, "unknown": MUTED, "plain": INK2}

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Liberation Sans", "Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 7.5,
    "figure.facecolor": SURF,
    "savefig.facecolor": SURF,
    "svg.hashsalt": "paper-ii-figures",
    "svg.fonttype": "path",
})


# ------------------------------------------------------------------ the rules, from the code
def readability_band() -> tuple[float, float]:
    """The mastered-cell accuracies at which positivity.mde() refuses to read a cell."""
    n = 50
    lo, hi = 0.01, 0.99
    if positivity.mde(n, n, lo) is not None or positivity.mde(n, n, hi) is not None:
        raise SystemExit(f"MISMATCH readability: mde() reads a cell at {lo} or {hi}")
    if positivity.mde(n, n, lo + 1e-4) is None or positivity.mde(n, n, hi - 1e-4) is None:
        raise SystemExit(f"MISMATCH readability: mde() refuses a cell just inside ({lo}, {hi})")
    return lo, hi


def power_convention() -> tuple[int, int]:
    """(power %, two-sided level %) implied by the z values both modules use."""
    out = set()
    for mod in (positivity, reach):
        level = 2 * (1 - NormalDist().cdf(mod.Z_ALPHA))
        power = NormalDist().cdf(mod.Z_BETA)
        out.add((round(power * 100), round(level * 100)))
    if len(out) != 1:
        raise SystemExit(f"MISMATCH power: the two modules use different conventions {out}")
    return out.pop()


def check_branches() -> None:
    """Each branch of the decision panel, run through classify_edge."""
    c = CLAIMED_EFFECT
    cases = [  # (panel branch, mde, observed drop, falsifiable, state the panel shows)
        ("not readable", None, None, True, UNKNOWN),
        ("readable, not powered", c + 0.02, c + 0.05, True, UNKNOWN),
        ("powered, drop shows, falsifiable", c - 0.02, c - 0.01, True, SUPPORTED),
        ("powered, drop shows, no merge node", c - 0.02, c - 0.01, False, SUPPORTED),
        ("powered, no drop, falsifiable", c - 0.02, 0.0, True, CONTRADICTED),
        ("powered, no drop, no merge node", c - 0.02, 0.0, False, UNKNOWN),
    ]
    for name, m, obs, fals, want in cases:
        got, _why = classify_edge(m, obs, falsifiable=fals)
        if got != want:
            raise SystemExit(f"MISMATCH branch '{name}': classify_edge gives {got}, the figure shows {want}")


def check_article(printed: dict[str, str]) -> None:
    if not ARTICLE.exists():   # the release's code package does not ship the article
        print("article not present: Section 4.2 not checked (the rules are still checked against the code)")
        return
    text = ARTICLE.read_text()
    a = text.index("### 4.2 ")
    sec = " ".join(text[a:text.index("### 4.3 ", a)].split())
    for name, phrase in printed.items():
        if phrase not in sec:
            raise SystemExit(f"MISMATCH article: Section 4.2 does not print '{phrase}' ({name})")
    if not re.search(r"min_cell=MIN_CELL", (HERE / "atlas.py").read_text()):
        raise SystemExit("MISMATCH merge-node floor: atlas.py no longer passes MIN_CELL to reachability")


# ------------------------------------------------------------------ drawing helpers
def box(ax, x, y, w, h, kind, title, sub=(), size=7.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.0",
                                facecolor=FILL[kind], edgecolor=EDGE[kind], linewidth=0.9))
    lines = [title, *sub]
    step = 2.5
    top = y + h / 2 + step * (len(lines) - 1) / 2
    for i, s in enumerate(lines):
        ax.text(x + w / 2, top - i * step, s, ha="center", va="center", color=INK,
                fontsize=size if i == 0 else size - 1, fontweight="bold" if i == 0 else "normal")


def arrow(ax, pts, label=None, at=None, ha="center"):
    xs, ys = zip(*pts)
    ax.plot(xs[:-1], ys[:-1], color=INK2, linewidth=0.8)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="-|>", color=INK2, linewidth=0.8, mutation_scale=7,
                                shrinkA=0, shrinkB=0))
    if label:
        ax.text(*at, label, ha=ha, va="center", color=MUTED, fontsize=6.8)


def panel_title(ax, y, letter, text):
    ax.text(0, y, letter, ha="left", va="center", color=INK, fontsize=9, fontweight="bold")
    ax.text(3.2, y, text, ha="left", va="center", color=INK, fontsize=8.5, fontweight="bold")


# ------------------------------------------------------------------ the figure
def draw(claim: str, floor: int, lo: float, hi: float, power: int, level: int):
    fig = plt.figure(figsize=(7.2, 8.9))
    ax = fig.add_axes((0.02, 0.01, 0.96, 0.98))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 123.6)
    ax.set_aspect("equal")
    ax.axis("off")

    # A ---------------------------------------------------------------- placing a learner
    panel_title(ax, 121, "A", "Placing a learner: what they held in a at their first attempt at b")
    ax.plot([60, 60], [88.5, 115], color=MUTED, linewidth=0.8, linestyle=(0, (3, 3)))
    ax.text(60, 116.8, "first attempt at b: the learner is placed here", ha="center", color=MUTED,
            fontsize=6.8)
    rows = [  # y, name, attempts at a (x, right?), faint later attempt, cell
        (110, "Learner 1", [(22, False), (35, True)], None, ("supported", "Mastered cell",
                                                            "passed a at least once")),
        (101, "Learner 2", [(22, False), (42, False)], (68, True), ("contradicted", "Identifying cell",
                                                                    "tried a, never passed it")),
        (92, "Learner 3", [], None, ("unknown", "Neither cell", "may hold a off the record")),
    ]
    for y, name, attempts, later, (kind, cell, sub) in rows:
        ax.text(1, y, name, ha="left", va="center", color=INK, fontweight="bold")
        ax.plot([13, 74], [y, y], color=LINE, linewidth=1.2, zorder=1)
        for x, right in attempts:
            ax.add_patch(Circle((x, y), 1.6, facecolor=FILL["supported" if right else "plain"],
                                edgecolor=S3 if right else INK2, linewidth=0.9, zorder=2))
            ax.text(x, y, "a", ha="center", va="center", color=INK, fontsize=6.8, zorder=3)
            ax.text(x, y - 3.1, "right" if right else "wrong", ha="center", va="center",
                    color=INK2, fontsize=6.5)
        if later:
            x, _ = later
            ax.add_patch(Circle((x, y), 1.6, facecolor=SURF, edgecolor=LINE, linewidth=0.9, zorder=2))
            ax.text(x, y, "a", ha="center", va="center", color=MUTED, fontsize=6.8, zorder=3)
            ax.text(x, y - 3.1, "right, too late", ha="center", va="center", color=MUTED, fontsize=6.5)
        if not attempts:
            ax.text(35, y + 1.6, "no attempt at a", ha="center", color=MUTED, fontsize=6.8)
        ax.add_patch(FancyBboxPatch((58.4, y - 1.6), 3.2, 3.2, boxstyle="round,pad=0,rounding_size=0.5",
                                    facecolor=FILL["decision"], edgecolor=S1, linewidth=0.9, zorder=2))
        ax.text(60, y, "b", ha="center", va="center", color=INK, fontsize=6.8, fontweight="bold",
                zorder=3)
        box(ax, 77, y - 3.3, 22, 6.6, kind, cell, (sub,), size=7.2)
    ax.text(20, 86.8, "time  →", ha="center", color=MUTED, fontsize=6.8)
    ax.text(62, 86.8, "drop = accuracy on b in the mastered cell − accuracy on b in the identifying cell",
            ha="center", color=INK, fontsize=6.8)

    # B ---------------------------------------------------------------- three states
    panel_title(ax, 81, "B", f"From two cells to one of three states, against a claimed drop of {claim}")
    dy, dh = 65.5, 10
    dec = [(1, 21, "Readable?", [f"≥ {floor} learners in each cell;",
                                   f"mastered accuracy {lo:.2f}–{hi:.2f}"]),
           (25.5, 21, "Powered?", [f"MDE ≤ {claim}", f"({power}% power, {level}% level)"]),
           (50, 21, "Drop shows?", ["observed drop ≥ MDE"]),
           (74.5, 24.5, "Falsifiable?", ["a readable, powered", "merge node (panel C)"])]
    for x, w, t, sub in dec:
        box(ax, x, dy, w, dh, "decision", t, sub)
    yc = dy + dh / 2
    for x0, x1, lab in [(22, 25.5, "yes"), (46.5, 50, "yes"), (71, 74.5, "no")]:
        arrow(ax, [(x0, yc), (x1, yc)], lab, ((x0 + x1) / 2, yc + 1.6))
    oy, oh = 48.5, 8
    outs = [(2, 19, "unknown", "Unknown", "cells cannot be compared"),
            (26.5, 19, "unknown", "Unknown", f"a {claim} drop could not show"),
            (51, 19, "supported", "Supported", "the drop from a is visible"),
            (75, 13, "contradicted", "Contradicted", "a powered null"),
            (89, 10.5, "unknown", "Unknown", "unfalsifiable")]
    for x, w, kind, t, s in outs:
        box(ax, x, oy, w, oh, kind, t, (s,))
    for x, lab in [(11.5, "no"), (36, "no"), (60.5, "yes")]:
        arrow(ax, [(x, dy), (x, oy + oh)], lab, (x + 1.2, (dy + oy + oh) / 2), ha="left")
    arrow(ax, [(81.5, dy), (81.5, oy + oh)], "yes", (80.6, 61.6), ha="right")
    arrow(ax, [(92, dy), (92, 60), (94.25, 60), (94.25, oy + oh)], "no", (95.2, 61.6), ha="left")
    ax.plot([51, 51, 88, 88], [47, 45.4, 45.4, 47], color=INK2, linewidth=0.8)
    ax.text(69.5, 43.4, "decided", ha="center", va="center", color=INK, fontweight="bold")

    # C ---------------------------------------------------------------- reachability gate
    panel_title(ax, 38.5, "C", "The reachability gate: could a null on (a, b) ever have been falsified?")
    for (x, y), lab in [((8, 28), "a"), ((8, 10), "b")]:
        ax.add_patch(Circle((x, y), 3, facecolor=SURF, edgecolor=INK2, linewidth=0.9))
        ax.text(x, y, lab, ha="center", va="center", color=INK, fontsize=8.5, fontweight="bold")
    ax.add_patch(Circle((32, 19), 3.4, facecolor=FILL["decision"], edgecolor=S1, linewidth=0.9))
    ax.text(32, 19, "c", ha="center", va="center", color=INK, fontsize=8.5, fontweight="bold")
    arrow(ax, [(10.9, 27.0), (28.8, 20.4)])
    arrow(ax, [(10.9, 11.0), (28.8, 17.6)])
    ax.text(25.2, 19, "and", ha="center", va="center", color=INK, fontweight="bold", fontsize=7)
    ax.plot([8, 8], [13.4, 24.6], color=MUTED, linewidth=0.8, linestyle=(0, (3, 3)))
    ax.text(9.6, 20.2, "no pairwise", ha="left", va="center", color=MUTED, fontsize=6.6)
    ax.text(9.6, 17.8, "dependence", ha="left", va="center", color=MUTED, fontsize=6.6)
    for i, s in enumerate(["merge node: reached after", "first attempts at both a and b,",
                           "on each learner's own timeline"]):
        ax.text(32, 12.4 - i * 2.4, s, ha="center", va="center", color=INK2, fontsize=6.6)
    arrow(ax, [(37.5, 19), (48, 19)], "split c's learners", (42.75, 21))
    ax.text(68.5, 35.2, "passed b", ha="center", color=INK, fontweight="bold", fontsize=7)
    ax.text(84.5, 35.2, "did not pass b", ha="center", color=INK, fontweight="bold", fontsize=7)
    ax.text(59, 27.5, "passed a", ha="right", va="center", color=INK, fontweight="bold", fontsize=7)
    ax.text(59, 16.7, "did not", ha="right", va="center", color=INK, fontweight="bold", fontsize=7)
    ax.text(59, 14.5, "pass a", ha="right", va="center", color=INK, fontweight="bold", fontsize=7)
    for x, y, kind, t in [(61, 23, "supported", "both"), (77, 23, "unknown", "a only"),
                          (61, 11.2, "unknown", "b only"), (77, 11.2, "unknown", "neither")]:
        box(ax, x, y, 15, 9.6, kind, t, (f"≥ {floor} learners",))
    for i, s in enumerate([f"Readable: each of the four strata holds ≥ {floor} learners.",
                           f"Powered: “both” against the weakest other stratum has MDE ≤ {claim}.",
                           "With no such c, a powered null returns to unknown."]):
        ax.text(77, 7.6 - i * 2.6, s, ha="center", va="center", color=INK, fontsize=6.8)
    return fig


def main() -> None:
    claim = f"{CLAIMED_EFFECT:.2f}"
    floor = positivity.MIN_CELL
    lo, hi = readability_band()
    power, level = power_convention()
    check_branches()
    check_article({
        "claimed effect": f"drop of {claim} in first-attempt accuracy",
        "cell floor": f"{floor} learners in each",
        "lower bound": f"at or below {lo:.2f}",
        "upper bound": f"at or above {hi:.2f}",
        "power": f"{power}% power",
        "level": f"at the {level}% level",
        "merge floor": f"holds at least {floor} learners",
        "merge power": f"MDE of {claim} or less",
    })
    fig = draw(claim, floor, lo, hi, power, level)
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{STEM}.svg", metadata={"Date": None, "Creator": None})
    fig.savefig(OUT / f"{STEM}.png", dpi=300, metadata={"Software": None})
    plt.close(fig)
    print("wrote", (OUT / STEM).relative_to(ROOT), ".svg and .png; every rule checked against the code "
          "and Section 4.2")


if __name__ == "__main__":
    main()
