"""Figure 3 of Paper II (research/article/what-learner-records-can-say-about-a-prerequisite-edge.md): the
expert hierarchy's two tests in Section 5.4, drawn as a diagram; Figure 2 draws the built graph's arms
(Table 10). Panel A is the expert tree against trees of the same shape and uses Table 11's names for its
arms and contrasts; panel B is the coupled state and uses the terms of the text that reports it.

Release learning-graph-budget-2026, analysis `figure-usefulness`. No model call and no corpus is read. The
figure is a schematic of the design, not a plot of results: it shows no AUC, gain or share. What it does
print is read from committed files and code, never typed in:

  866 KCs, 559 parent links into 555 KCs   out/result.json tree (kcs, contracted_parent_links,
                                           kcs_with_kc_parent)
  5 deranged trees, 3 deranged route trees kc_tree.py N_DER, N_FDER (and result.json's own arms)
  the bar, +0.001                          kc_tree.py EQUIV
  the coupled state's rule, one half       studies/measurement/graph-state/coupling.py, the line that
                                           assigns GRAPH CARRIES THE COUPLING

Panel A's six-KC tree is an illustration of the derangement rule, and the script checks that it obeys
the rule it illustrates: every child moved to another parent at the same depth, every parent keeping its
number of children, and no real link surviving, either as it was or reversed.

THE CHECKS. The script stops (1) if any quantity above differs between its sources, (2) if the drawn
derangement breaks the rule, and (3) if Section 5.4 of the article does not print each quantity as the
figure does (checked in the research repository; the release's code package does not ship the article,
so there it is skipped).

Design (the dataviz method, light mode, print): text in ink; real links in grey ink, deranged links in
slot 2 orange, reversed links in slot 1 blue, each named on the drawing so no arm is read from colour
alone; covariance cells in one sequential blue.

    python3 studies/end-to-end/xes3g5m-kc-tree-control/figure_usefulness.py
writes research/article/figures/learning-graph-budget-2026/fig3-expert-hierarchy.svg and .png (300 dpi),
byte-identical on re-run. matplotlib 3.11.2.
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTICLE = ROOT / "research" / "article" / "what-learner-records-can-say-about-a-prerequisite-edge.md"
COUPLING = ROOT / "studies" / "measurement" / "graph-state" / "coupling.py"
OUT = ROOT / "research" / "article" / "figures" / "learning-graph-budget-2026"
STEM = "fig3-expert-hierarchy"

SURF = "#fcfcfb"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
S1, S2 = "#2a78d6", "#eb6834"
WASH = "#e6effa"
BLUES = ["#e6effa", "#b9d3f3", "#86b6ef", "#4f93e0", "#2a78d6"]

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Liberation Sans", "Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 7.5,
    "figure.facecolor": SURF,
    "savefig.facecolor": SURF,
    "svg.hashsalt": "paper-ii-figures",
    "svg.fonttype": "path",
})

# Panel A's illustrative tree: two parents, four child KCs
REAL = {"P1": ["k1", "k2"], "P2": ["k3", "k4"]}
DERANGED = {"P1": ["k3", "k4"], "P2": ["k1", "k2"]}


# ------------------------------------------------------------------ the quantities
def constants(path: Path, names: set[str]) -> dict:
    got = {}
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in names:
                got[node.targets[0].id] = ast.literal_eval(node.value)
    if set(got) != names:
        raise SystemExit(f"MISMATCH {path.name}: constants {sorted(names - set(got))} not found")
    return got


def quantities() -> dict:
    res = json.loads((HERE / "out" / "result.json").read_text())
    c = constants(HERE / "kc_tree.py", {"N_DER", "N_FDER", "EQUIV"})
    t = res["tree"]
    q = dict(kcs=t["kcs"], links=t["contracted_parent_links"], children=t["kcs_with_kc_parent"], **c)
    n_td = sum(1 for k in res["auc"] if re.fullmatch(r"Td\d+", k))
    n_fd = sum(1 for k in res["auc"] if re.fullmatch(r"Fd\d+", k))
    if (n_td, n_fd) != (c["N_DER"], c["N_FDER"]):
        raise SystemExit(f"MISMATCH arms: result.json scored {n_td} deranged trees and {n_fd} deranged route "
                         f"trees, kc_tree.py says {c['N_DER']} and {c['N_FDER']}")
    m = re.search(r'"GRAPH CARRIES THE COUPLING" if rt\["est"\] >= ([0-9.]+) else "EMPIRICAL COVARIANCE ONLY"',
                  COUPLING.read_text())
    if not m:
        raise SystemExit("MISMATCH coupling.py: the rule that assigns GRAPH CARRIES THE COUPLING was not found")
    q["share_rule"] = float(m.group(1))
    if "retention is (C3 - C2-diag) / (C2 - C2-diag)" not in " ".join(COUPLING.read_text().split()):
        raise SystemExit("MISMATCH coupling.py: the retained share is no longer (C3 - C2-diag) / (C2 - C2-diag)")
    for corpus in ("xes", "eedi"):
        r = json.loads((COUPLING.parent / "out" / f"{corpus}.json").read_text())
        for key in ("C2_over_C2diag_M1", "C3_over_C2diag_M1", "C3g_over_C2g_M1", "graph_retention"):
            if key not in r:
                raise SystemExit(f"MISMATCH graph-state: out/{corpus}.json has no {key}, an arm the figure draws")
    return q


def check_derangement() -> None:
    real = {(p, k) for p, ks in REAL.items() for k in ks}
    der = {(p, k) for p, ks in DERANGED.items() for k in ks}
    if {p: len(v) for p, v in REAL.items()} != {p: len(v) for p, v in DERANGED.items()}:
        raise SystemExit("MISMATCH drawing: a parent's number of children changed")
    if sorted(k for v in REAL.values() for k in v) != sorted(k for v in DERANGED.values() for k in v):
        raise SystemExit("MISMATCH drawing: the deranged tree does not hold the same children")
    if real & der or {(k, p) for p, k in real} & der:
        raise SystemExit("MISMATCH drawing: a real link survives the derangement")


def words(n: int) -> str:
    return {3: "three", 5: "five"}.get(n, str(n))


def check_article(printed: dict[str, str]) -> None:
    if not ARTICLE.exists():   # the release's code package does not ship the article
        print("article not present: Section 5.4 not checked (the sources are still checked against each other)")
        return
    text = ARTICLE.read_text()
    a = text.index("### 5.4 ")
    sec = " ".join(text[a:text.index("### 5.5 ", a)].split())
    for name, phrase in printed.items():
        if phrase not in sec:
            raise SystemExit(f"MISMATCH article: Section 5.4 does not print '{phrase}' ({name})")


# ------------------------------------------------------------------ drawing helpers
def node(ax, x, y, label, kind):
    w, h = (7, 4.2) if kind == "parent" else (5.4, 4.2)
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0,rounding_size=0.8",
                                facecolor=WASH if kind == "parent" else SURF,
                                edgecolor=S1 if kind == "parent" else INK2, linewidth=0.9, zorder=3))
    ax.text(x, y, label, ha="center", va="center", color=INK, fontsize=7, zorder=4,
            fontweight="bold" if kind == "parent" else "normal")


def link(ax, a, b, color, style="-"):
    ax.annotate("", xy=b, xytext=a, zorder=2,
                arrowprops=dict(arrowstyle="-|>", color=color, linewidth=1.0, mutation_scale=7,
                                linestyle=style, shrinkA=0, shrinkB=0))


def panel_title(ax, y, letter, text):
    ax.text(0, y, letter, ha="left", va="center", color=INK, fontsize=9, fontweight="bold")
    ax.text(3.2, y, text, ha="left", va="center", color=INK, fontsize=8.5, fontweight="bold")


FILLS = {"shared": ("#efeeea", MUTED), "expert": ("#fce9df", S2), "tree": ("#e2f4ec", "#1baf7a"),
         "control": (SURF, MUTED)}


def block(ax, x, y, w, h, kind, lines, step=1.95):
    face, edge = FILLS[kind]
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.8", facecolor=face,
                                edgecolor=edge, linewidth=0.9, linestyle=(0, (3, 2)) if kind == "control" else "-"))
    top = y + h / 2 + step * (len(lines) - 1) / 2
    for k, t in enumerate(lines):
        ax.text(x + w / 2, top - k * step, t, ha="center", va="center", color=INK, fontsize=6.6)


def tree(ax, x0, ytop, title, edges, color, reverse=False, note=()):
    px = {"P1": x0 + 8, "P2": x0 + 22}
    kx = {"k1": x0 + 2.5, "k2": x0 + 11, "k3": x0 + 19, "k4": x0 + 27.5}
    py, ky = ytop - 6, ytop - 17
    ax.text(x0 + 15, ytop, title, ha="center", va="center", color=INK, fontsize=7.8, fontweight="bold")
    for p, x in px.items():
        node(ax, x, py, p, "parent")
    for k, x in kx.items():
        node(ax, x, ky, k, "child")
    for p, ks in edges.items():
        for k in ks:
            a, b = (px[p], py - 2.1), (kx[k], ky + 2.1)     # box edges, so the heads show
            link(ax, b if reverse else a, a if reverse else b, color)
    for i, t in enumerate(note):
        ax.text(x0 + 15, ky - 4.6 - i * 2.4, t, ha="center", va="center", color=INK2, fontsize=6.6)


def matrix(ax, x0, y0, M, cell=1.25):
    n = len(M)
    for i in range(n):
        for j in range(n):
            v = M[i][j]
            ax.add_patch(Rectangle((x0 + j * cell, y0 + (n - 1 - i) * cell), cell, cell,
                                   facecolor=BLUES[min(v, 4)] if v else SURF, edgecolor="#d9d8d2", linewidth=0.3))


def ladder_rows(ax, y, rows, step=5.9, xq=64.5):
    for label, left, question, rule in rows:
        ax.text(1, y + 2.4, label, ha="left", va="center", color=INK, fontweight="bold", fontsize=7.3)
        left(y)
        if rule:
            parts = rule.split("|")
            y0 = y + 2.4 + 1.1 * len(parts)
            ax.text(xq, y0, question, ha="left", va="center", color=INK, fontsize=6.8)
            for k, r in enumerate(parts):
                ax.text(xq, y0 - 2.2 * (k + 1), r, ha="left", va="center", color=INK2, fontsize=6.4)
        else:
            ax.text(xq, y + 2.4, question, ha="left", va="center", color=MUTED, fontsize=6.8, style="italic")
        y -= step
    return y


# ------------------------------------------------------------------ the figures
def canvas(H):
    fig = plt.figure(figsize=(7.2, 7.2 * H / 100 * 0.985))
    ax = fig.add_axes((0.02, 0.01, 0.96, 0.98))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, H)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def draw_tree(ax, q: dict, top: float):
    """Panel A: Table 11's arms, named as the table names them."""
    bar = f"{q['EQUIV']:+.3f}".replace("-", "−")
    eq = f"{q['EQUIV']:.3f}"
    tree(ax, 1, top, "Real tree", REAL, INK2, note=("each KC's parent on its route",))
    tree(ax, 35, top, f"Deranged tree (one of {words(q['N_DER'])})", DERANGED, S2,
         note=("children moved at the same depth;", "parents keep their counts; no real link"))
    tree(ax, 69, top, "Reversed tree", REAL, S1, reverse=True, note=("each KC's children instead",))
    ax.text(50, top - 28.5, f"{q['kcs']:,} KCs; {q['links']:,} parent links into {q['children']:,} KCs. "
            "The six-KC tree is an illustration.", ha="center", va="center", color=INK2, fontsize=6.7)
    yh = top - 34
    cols = [(17, "per-question", "difficulty"), (28, "history on", "every question"),
            (39, "history on the", "expert leaf KCs"), (50, "history the", "tree adds")]
    widths = (10.2, 10.2, 10.2, 13.2)
    for (x, l1, l2), w in zip(cols, widths):
        ax.text(x + w / 2, yh, l1, ha="center", color=MUTED, fontsize=6.3)
        ax.text(x + w / 2, yh - 2.1, l2, ha="center", color=MUTED, fontsize=6.3)
    ax.text(65.5, yh, "contrast in Table 11 (paired bootstrap", ha="left", color=MUTED, fontsize=6.3)
    ax.text(65.5, yh - 2.1, "over held-out learners)", ha="left", color=MUTED, fontsize=6.3)
    rh = 4.9

    def arm(kind, lines):
        def f(y):
            for (x, _, _), w, (k, ls) in zip(cols, widths, [("shared", ["difficulty"]), ("shared", ["all questions"]),
                                                            ("expert", ["expert leaf KCs"])]):
                block(ax, x, y, w, rh, k, ls)
            if kind:
                block(ax, cols[3][0], y, widths[3], rh, kind, lines)
        return f

    rows = [
        ("expert KCs alone", arm(None, []), "the reference: M2 of Table 10", ""),
        ("real tree", arm("tree", ["KC parents"]), "Real tree minus expert KCs alone",
         f"beats: lower bound above {bar}"),
        ("deranged trees", arm("control", ["parents in a", "deranged tree"]), "Real tree minus deranged trees",
         f"beats: lower bound above {bar}; equivalent:|interval within ±{eq} (mean of {words(q['N_DER'])} trees)"),
        ("reversed tree", arm("control", ["KC children"]), "Real tree minus reversed tree", "reported only"),
        ("route family", arm("tree", ["route family"]), "its sibling KCs and the KCs beneath them", ""),
        ("deranged", arm("control", ["family in a", "deranged route tree"]),
         "Route family minus deranged route trees",
         f"as for the trees (mean of {words(q['N_FDER'])})"),
    ]
    y = yh - 8
    for label, left, question, rule in rows:
        sub = "route trees" if label == "deranged" else ""
        ax.text(1, y + 2.4 + (1.1 if sub else 0), label, ha="left", va="center", color=INK, fontweight="bold",
                fontsize=7)
        if sub:
            ax.text(1, y + 1.3, sub, ha="left", va="center", color=INK, fontweight="bold", fontsize=7)
        left(y)
        if rule:
            parts = rule.split("|")
            y0 = y + 2.4 + 1.1 * len(parts)
            ax.text(65.5, y0, question, ha="left", va="center", color=INK, fontsize=6.8)
            for k, r in enumerate(parts):
                ax.text(65.5, y0 - 2.2 * (k + 1), r, ha="left", va="center", color=INK2, fontsize=6.4)
        else:
            ax.text(65.5, y + 2.4, question, ha="left", va="center", color=MUTED, fontsize=6.8, style="italic")
        y -= 6.2


def draw_coupling(ax, q: dict, top: float):
    """Panel B: the coupled state, in the terms of the text that reports it."""
    n = 6
    sib = [0, 0, 0, 1, 1, 1]
    full = [[5 if i == j else 1 + ((i * 7 + j * 3) % 4) for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(i):
            full[i][j] = full[j][i]
    diag = [[full[i][j] if i == j else 0 for j in range(n)] for i in range(n)]
    sibm = [[full[i][j] if sib[i] == sib[j] else 0 for j in range(n)] for i in range(n)]
    gen = [[5 if i == j else 1 for j in range(n)] for i in range(n)]
    gsib = [[5 if i == j else 3 if sib[i] == sib[j] else 1 for j in range(n)] for i in range(n)]
    share = f"{q['share_rule']:g}"
    ax.text(1, top, "the filter's covariance between skills", ha="left", color=MUTED, fontsize=6.3)
    ax.text(50, top, "what each comparison measures, at a learner's first", ha="left", color=MUTED, fontsize=6.3)
    ax.text(50, top - 2.1, "attempt at a skill they had never attempted", ha="left", color=MUTED, fontsize=6.3)

    def mrow(M, text):
        def f(y):
            matrix(ax, 1, y - 1.2, M)
            ax.text(11, y + 2.4, text, ha="left", va="center", color=INK, fontsize=6.9, fontweight="bold")
        return f

    rows = [
        ("", mrow(diag, "no covariance"), "the reference", ""),
        ("", mrow(full, "covariance fitted on training learners"), "coupling gain",
         "log loss with no covariance minus log loss with it"),
        ("", mrow(sibm, "sibling groups only (skills sharing a parent)"), "retained share",
         f"the sibling groups' gain divided by the coupling gain;|at least {share}: GRAPH CARRIES THE COUPLING;"
         f"|under {share}: EMPIRICAL COVARIANCE ONLY"),
        ("", mrow(gen, "a general factor only"), "the reference for the next row", ""),
        ("", mrow(gsib, "a general factor plus sibling groups"), "what sibling groups add to a general factor",
         "reported, with its interval"),
    ]
    ladder_rows(ax, top - 12, rows, step=8.6, xq=50)


def draw(q: dict):
    """Figure 3: the expert hierarchy's two tests, one panel each."""
    H = 141
    fig, ax = canvas(H)
    panel_title(ax, H - 2.5, "A", "The expert tree against trees of the same shape (Table 11)")
    draw_tree(ax, q, H - 9)
    panel_title(ax, H - 89, "B", "Does the hierarchy describe how skills co-vary? (the coupled state)")
    draw_coupling(ax, q, H - 95)
    return fig


def main() -> None:
    q = quantities()
    check_derangement()
    check_article({
        "kcs": f"{q['kcs']:,} KCs",
        "links": f"{q['links']:,} parent links into {q['children']:,} child KCs",
        "deranged trees": f"{words(q['N_DER'])} deranged trees",
        "deranged route trees": f"{words(q['N_FDER'])} route trees deranged",
        "share rule": "keeps at least half the gain" if q["share_rule"] == 0.5 else f"at least {q['share_rule']}",
    })
    OUT.mkdir(parents=True, exist_ok=True)
    fig = draw(q)
    fig.savefig(OUT / f"{STEM}.svg", metadata={"Date": None, "Creator": None})
    fig.savefig(OUT / f"{STEM}.png", dpi=300, metadata={"Software": None})
    plt.close(fig)
    print("wrote", (OUT / STEM).relative_to(ROOT), ".svg and .png")
    print("every quantity checked against its sources and Section 5.4")


if __name__ == "__main__":
    main()
