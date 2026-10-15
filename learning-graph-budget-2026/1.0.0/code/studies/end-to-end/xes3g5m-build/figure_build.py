"""Figure 2 of Paper II (research/article/what-learner-records-can-say-about-a-prerequisite-edge.md):
the graph language models built for RQ4 and the arms that test it. Section 4.6 drawn as a diagram.

Release learning-graph-budget-2026, analysis `figure-build`. No model call and no corpus is read. The
figure is a schematic of the design, not a plot of results: it shows no AUC and no difference. The
quantities it does print are read from committed files, never typed in:

  families, nodes, edges, questions tagged   build/nodes.json, build/edges.json, build/tags.json
  questions sampled per family (120)         e2e.py SAMPLE_N
  held-out learners and attempts             out/result.json split
  the bars (+0.001 to beat, -0.005 for       e2e.py BEATS, NONINF, and the bootstrap draws BOOT
  "not worse than the expert taxonomy")

e2e.py is read for its constants with `ast`, not imported, so drawing the figure runs none of the build.

THE CHECKS. The script stops (1) if the committed files disagree with each other (the result's build
summary against the build files, every question tagged), (2) if Section 4.6 of the article does not
print each quantity as the figure does (checked in the research repository; the release's code package
does not ship the article, so there it is skipped), and (3) if the arms drawn in panel B are not the
arms the result file scored, in the order Table 10 gives.

Design (the dataviz method, light mode, print): text in ink; the parts an arm adds in fixed washes
(built nodes blue, their prerequisites green, the expert taxonomy orange, the shared terms grey) with
each part named on its box, so no part is read from colour alone; the two controls drawn dashed.

    python3 studies/end-to-end/xes3g5m-build/figure_build.py
writes research/article/figures/learning-graph-budget-2026/fig2-build-and-arms.svg and .png (300 dpi),
byte-identical on re-run. matplotlib 3.11.2.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTICLE = ROOT / "research" / "article" / "what-learner-records-can-say-about-a-prerequisite-edge.md"
OUT = ROOT / "research" / "article" / "figures" / "learning-graph-budget-2026"
STEM = "fig2-build-and-arms"

# ------------------------------------------------------------------ palette (dataviz reference, light)
SURF = "#fcfcfb"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"
FILL = {"step": "#e6effa", "plain": SURF, "shared": "#efeeea", "built": "#e6effa", "edges": "#e2f4ec",
        "expert": "#fce9df", "control": SURF}
EDGE = {"step": S1, "plain": INK2, "shared": MUTED, "built": S1, "edges": S3, "expert": S2,
        "control": MUTED}

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Liberation Sans", "Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 7.5,
    "figure.facecolor": SURF,
    "savefig.facecolor": SURF,
    "svg.hashsalt": "paper-ii-figures",
    "svg.fonttype": "path",
})

ARMS = ["M0", "M1", "M2", "M2c", "M3", "M4", "M4s", "M4r"]   # panel B's rows: Table 10's arms, in its order


# ------------------------------------------------------------------ the quantities, from committed files
def constants() -> dict:
    """SAMPLE_N, BEATS, NONINF and BOOT from e2e.py, read without running it."""
    want = {"SAMPLE_N", "BEATS", "NONINF", "BOOT"}
    got = {}
    for node in ast.parse((HERE / "e2e.py").read_text()).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in want:
                got[node.targets[0].id] = ast.literal_eval(node.value)
    if set(got) != want:
        raise SystemExit(f"MISMATCH e2e.py: constants {sorted(want - set(got))} not found")
    return got


def quantities() -> dict:
    nodes = json.loads((HERE / "build" / "nodes.json").read_text())
    edges = json.loads((HERE / "build" / "edges.json").read_text())
    tags = json.loads((HERE / "build" / "tags.json").read_text())
    res = json.loads((HERE / "out" / "result.json").read_text())
    q = dict(families=len(nodes["families"]), nodes=len(nodes["nodes"]), edges=len(edges["edges"]),
             questions=len(tags["tags"]), untagged=tags["untagged"],
             held_learners=res["split"]["test_learners"], held_attempts=res["split"]["test_attempts"],
             arms=list(res["B11"]["auc"]), **constants())
    b = res["build"]
    for k_res, k in (("nodes", "nodes"), ("edges", "edges"), ("tagged_questions", "questions")):
        if b[k_res] != q[k]:
            raise SystemExit(f"MISMATCH build: result.json says {k_res} {b[k_res]}, the build files {q[k]}")
    if b["families"] != nodes["families"] or q["untagged"] not in (0, []):
        raise SystemExit("MISMATCH build: families differ between result.json and nodes.json, or a "
                         "question is untagged")
    missing = [a for a in ARMS if a not in q["arms"]]
    if missing:
        raise SystemExit(f"MISMATCH arms: result.json scored no {missing}")
    order = [a for a in q["arms"] if a in ARMS]
    if order != ARMS:
        raise SystemExit(f"MISMATCH arms: result.json orders them {order}, the figure {ARMS}")
    q["seen"] = q["families"] * q["SAMPLE_N"]
    return q


def signed(x: float) -> str:
    return f"{x:+.3f}".replace("-", "−")


def check_article(printed: dict[str, str]) -> None:
    if not ARTICLE.exists():   # the release's code package does not ship the article
        print("article not present: Section 4.6 not checked (the files are still checked against each other)")
        return
    text = ARTICLE.read_text()
    a = text.index("### 4.6 ")
    sec = " ".join(text[a:text.index("### 4.7 ", a)].split())
    for name, phrase in printed.items():
        if phrase not in sec:
            raise SystemExit(f"MISMATCH article: Section 4.6 does not print '{phrase}' ({name})")


# ------------------------------------------------------------------ drawing helpers
def box(ax, x, y, w, h, kind, title, sub=(), size=7.3, dashed=False, step=2.45):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.9",
                                facecolor=FILL[kind], edgecolor=EDGE[kind], linewidth=0.9,
                                linestyle=(0, (3, 2)) if dashed else "-"))
    lines = [title, *sub] if title else list(sub)
    top = y + h / 2 + step * (len(lines) - 1) / 2
    for i, s in enumerate(lines):
        bold = bool(title) and i == 0
        ax.text(x + w / 2, top - i * step, s, ha="center", va="center", color=INK,
                fontsize=size if bold else size - 0.9, fontweight="bold" if bold else "normal")


def arrow(ax, pts, label=None, at=None, ha="center", head=True):
    xs, ys = zip(*pts)
    ax.plot(xs[:-1] if head else xs, ys[:-1] if head else ys, color=INK2, linewidth=0.8)
    if head:
        ax.annotate("", xy=pts[-1], xytext=pts[-2],
                    arrowprops=dict(arrowstyle="-|>", color=INK2, linewidth=0.8, mutation_scale=7,
                                    shrinkA=0, shrinkB=0))
    if label:
        ax.text(*at, label, ha=ha, va="center", color=MUTED, fontsize=6.6)


def panel_title(ax, y, letter, text):
    ax.text(0, y, letter, ha="left", va="center", color=INK, fontsize=9, fontweight="bold")
    ax.text(3.2, y, text, ha="left", va="center", color=INK, fontsize=8.5, fontweight="bold")


# ------------------------------------------------------------------ the figure
def draw(q: dict):
    fig = plt.figure(figsize=(7.2, 8.41))
    ax = fig.add_axes((0.02, 0.01, 0.96, 0.98))
    ax.set_xlim(0, 100)
    ax.set_ylim(-5.9, 110.8)
    ax.set_aspect("equal")
    ax.axis("off")

    # A ---------------------------------------------------------------- the build
    panel_title(ax, 108.6, "A", "The build, from question text alone, frozen before any learner record was read")
    w, gap, y0, h = 17.6, 2.75, 92, 13
    xs = [0.5 + i * (w + gap) for i in range(5)]
    steps = [("Question text", [f"{q['questions']:,} questions", "with answers and", "worked solutions"]),
             ("Propose nodes", [f"{q['families']} model families,", f"{q['SAMPLE_N']} questions each",
                                f"({q['seen']} seen in all)"]),
             ("Merge", ["a judge model joins", "matching proposals:", f"{q['nodes']} nodes"]),
             ("Propose edges", ["2 models name each", "node's direct", "prerequisites"]),
             ("Check and reduce", ["a critic keeps or rejects;", "cycles skipped, then", f"reduced: {q['edges']} edges"])]
    for x, (t, sub) in zip(xs, steps):
        box(ax, x, y0, w, h, "plain" if t == "Question text" else "step", t, sub)
    for i in range(4):
        arrow(ax, [(xs[i] + w, y0 + h / 2), (xs[i + 1], y0 + h / 2)])
    ax.text(xs[0] + w / 2, 87.6, "never the KC taxonomy,", ha="center", color=MUTED, fontsize=6.6)
    ax.text(xs[0] + w / 2, 85.2, "its tags or a learner", ha="center", color=MUTED, fontsize=6.6)
    ax.text(xs[0] + w / 2, 82.8, "response", ha="center", color=MUTED, fontsize=6.6)
    # the tagger hangs off the merged nodes
    box(ax, xs[2], 78.5, w, 8, "step", "Tag questions", ["1 to 3 nodes each"])
    arrow(ax, [(xs[2] + w / 2, y0), (xs[2] + w / 2, 86.5)])
    # the build's output runs down to the analysis, crossing the freeze
    xo = xs[4] + w / 2
    ax.plot([xs[2] + w, xo], [82.5, 82.5], color=INK2, linewidth=0.8)
    arrow(ax, [(xo, y0), (xo, 65.5)])
    ax.text(xo + 1.2, 78.8, "nodes, edges", ha="left", va="center", color=MUTED, fontsize=6.6)
    ax.text(xo + 1.2, 76.6, "and tags", ha="left", va="center", color=MUTED, fontsize=6.6)
    ax.plot([0.5, 99.5], [73.5, 73.5], color=MUTED, linewidth=0.8, linestyle=(0, (3, 3)))
    ax.text(42, 74.9, "frozen and committed here: no learner response read above this line",
            ha="center", va="bottom", color=INK2, fontsize=6.8)
    # the learner side
    box(ax, 0.5, 55, 23, 10.5, "plain", "XES3G5M learner", ["records"])
    box(ax, 29, 55, 33, 10.5, "step", "Split by a hash of the learner", ["1 learner in 5 held out:",
        f"{q['held_learners']:,} learners, {q['held_attempts']:,} attempts"])
    box(ax, 68, 55, 31.5, 10.5, "step", "Fit each arm on training", ["learners; score AUC on", "held-out learners (panel B)"])
    arrow(ax, [(23.5, 60.25), (29, 60.25)])
    arrow(ax, [(62, 60.25), (68, 60.25)])

    # B ---------------------------------------------------------------- the arms
    panel_title(ax, 50, "B", "The arms: each adds one part, and each difference from M4 asks one question")
    cols = [(9, "per-question", "difficulty"), (22.5, "history on", "every question"),
            (36, "history on the", "question's units"), (49.5, "history on", "its prerequisites")]
    cw = 12.8
    for x, l1, l2 in cols:
        ax.text(x + cw / 2, 45.6, l1, ha="center", color=MUTED, fontsize=6.4)
        ax.text(x + cw / 2, 43.4, l2, ha="center", color=MUTED, fontsize=6.4)
    ax.text(64.5, 45.6, "the difference from M4 asks", ha="left", color=MUTED, fontsize=6.4)
    ax.text(64.5, 43.4, f"(paired bootstrap over held-out learners, {q['BOOT']} draws)", ha="left",
            color=MUTED, fontsize=6.4)
    beat, noninf = signed(q["BEATS"]), signed(q["NONINF"])
    rows = {  # arm: parts beyond the two shared ones, question, rule
        "M0": ([], "Does the graph help at all?", "useful only if M4 beats M0 and M1"),
        "M1": ([], "Does it help beyond overall history?", f"beats: lower bound above {beat}"),
        "M2": ([("expert", "expert leaf KCs")], "Is it as good as the expert taxonomy?",
               f"not worse: lower bound above {noninf}"),
        "M2c": ([("expert", "expert KCs,|cut at depth 3")], "reported beside M2; no contrast registered", ""),
        "M3": ([("built", "built nodes")], "What do the edges add to the nodes?",
               "edges add nothing unless M4 beats M3"),
        "M4": ([("built", "built nodes"), ("edges", "prerequisites")], "the reference arm", ""),
        "M4s": ([("built", "built nodes"), ("control", "same edges,|nodes at random")],
                "Do the edges beat a random placement?", f"beats: lower bound above {beat}"),
        "M4r": ([("built", "built nodes"), ("control", "dependents|(edges reversed)")],
                "Does direction matter?", "reported only: the platform's order confounds it"),
    }
    y, rh, step = 36.6, 4.9, 5.75
    for arm in ARMS:
        parts, question, rule = rows[arm]
        ax.text(1, y + rh / 2, arm, ha="left", va="center", color=INK, fontweight="bold", fontsize=7.5)
        segs = [("shared", "difficulty offset")]
        if arm != "M0":
            segs.append(("shared", "all questions"))
        segs += parts
        for (kind, label), (x, _, _) in zip(segs, cols):
            sub = label.split("|")
            box(ax, x, y, cw, rh, kind, None, sub, size=7.3, dashed=kind == "control", step=1.95)
        if not rule:
            ax.text(64.5, y + rh / 2, question, ha="left", va="center", color=MUTED, fontsize=6.8,
                    style="italic")
        else:
            ax.text(64.5, y + rh / 2 + 1.1, question, ha="left", va="center", color=INK, fontsize=6.8)
            ax.text(64.5, y + rh / 2 - 1.2, rule, ha="left", va="center", color=INK2, fontsize=6.4)
        y -= step
    return fig


def main() -> None:
    q = quantities()
    check_article({
        "questions per family": f"sample of {q['SAMPLE_N']} questions",
        "seen": f"saw {q['seen']} of the {q['questions']:,} questions",
        "nodes": f"merge gave {q['nodes']} nodes",
        "edges": f"leaving {q['edges']} edges",
        "families": "proposed by six model families" if q["families"] == 6 else f"{q['families']} model families",
        "held out": f"{q['held_learners']:,} learners and {q['held_attempts']:,} attempts",
        "beat bar": f"exceeds {signed(q['BEATS'])}",
        "non-inferiority bar": f"exceeds {signed(q['NONINF'])}",
        "bootstrap": f"{q['BOOT']} draws",
        "tags per question": "one to three nodes",
    })
    fig = draw(q)
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{STEM}.svg", metadata={"Date": None, "Creator": None})
    fig.savefig(OUT / f"{STEM}.png", dpi=300, metadata={"Software": None})
    plt.close(fig)
    print("wrote", (OUT / STEM).relative_to(ROOT), ".svg and .png; every quantity checked against the "
          "committed files and Section 4.6")


if __name__ == "__main__":
    main()
