"""
The five static figures of release checklist-grading-2026 (research/article/precise-checklists-and-an-ai-grader.md),
drawn from committed outputs only, numbered as the article places them:

  fig1  reliability: each model's test-retest r and the cross-model r, Likert against checklist, for the
        short answers and each programming dimension (../grader-boolean-rubrics/out/results.json, Table 1);
  fig2  agreement with the human raters: each model's r with the human mean, Likert against checklist, with the human raters'
        own agreement beside it (the same file, Table 2);
  fig3  each format's mean signed error against the human mean, by band of human score
        (out/results.json of this study, Table 3);
  fig4  the planted-defect contrasts: each format's mean change under a contradiction and under key-term
        stuffing, pooled and per model (../grader-boolean-rubrics/out/results.json, Table 4);
  fig5  the checklist's change under each planted defect split into its error checks (the registration's
        avoid checks) and presence checks
        (out/results.json of this study, Table 5).

ARTICLE holds the values the article prints. The script stops if any output, rounded the article's way,
gives something else, so the figures and the text cannot drift apart. Two runs give byte-identical PNGs
on one machine (metadata stripped, fixed fonts). Figures 1 and 2 are slope charts: one line per model
from its Likert value to its checklist value, so a falling line is a loss for the checklist.

    python3 figures.py            writes research/article/figures/checklist-fig{1..5}-*.png

Revised 2026-11-06 at the maintainer's request for more charts in the results: figures 1, 2 and 5 are
new, the band chart became a line chart, and the files were renumbered in the article's order (the old
checklist-fig1-planted-defects is fig4, checklist-fig2-error-by-band is fig3). On 2026-11-06 fig2 was renamed checklist-fig2-human-agreement and
"avoid checks" became "error checks" in fig5, following the article's terms.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
from shared import figstyle  # noqa: E402

PARENT = HERE.parent / "grader-boolean-rubrics" / "out" / "results.json"
OWN = HERE / "out" / "results.json"
FIGDIR = REPO / "research" / "article" / "figures"

DIMS = [("mohler", "Short answers"), ("Correctness", "Programs:\nCorrectness"),
        ("Code Elegance", "Programs:\nCode Elegance"), ("Readability", "Programs:\nReadability"),
        ("Documentation", "Programs:\nDocumentation")]

# Values printed in the article, checked against the outputs before drawing. Tables 1 and 2 print r
# unsigned to 3 decimals ("0.987", "−0.164"); the differences and Tables 3 to 5 are signed.
ARTICLE = {
    # Table 1: test-retest Likert / checklist per model, cross-model Likert / checklist, dR, dX
    "R mohler": ["0.987", "0.961", "0.962", "0.965", "0.885", "0.906", "-0.011", "+0.021"],
    "R Correctness": ["0.707", "0.596", "0.663", "0.426", "-0.164", "-0.159", "-0.174", "+0.006"],
    "R Code Elegance": ["0.830", "0.655", "0.673", "0.562", "0.577", "0.223", "-0.143", "-0.354"],
    "R Readability": ["0.832", "0.747", "0.745", "0.445", "0.586", "0.019", "-0.192", "-0.567"],
    "R Documentation": ["0.684", "0.650", "0.451", "0.285", "0.231", "0.212", "-0.100", "-0.019"],
    # Table 2: human agreement Likert / checklist per model, dH, human ceiling
    "V mohler": ["0.764", "0.688", "0.819", "0.682", "-0.106", "0.621"],
    "V Correctness": ["0.405", "0.433", "-0.173", "-0.054", "+0.073", "0.622"],
    "V Code Elegance": ["0.035", "0.017", "-0.182", "-0.137", "+0.013", "0.539"],
    "V Readability": ["0.039", "-0.007", "-0.235", "-0.011", "+0.089", "0.571"],
    "V Documentation": ["0.286", "0.079", "-0.284", "-0.125", "-0.024", "0.525"],
    # Table 4
    "contra D.likert": "-0.473", "contra D.boolean": "-0.172",
    "stuff D.likert": "+0.273", "stuff D.boolean": "+0.348",
    # Table 3
    "LOW e_likert": "-0.144", "LOW e_boolean": "-0.123",
    "MID e_likert": "-0.149", "MID e_boolean": "-0.327",
    "HIGH e_likert": "-0.049", "HIGH e_boolean": "-0.160",
    # Table 5: D, E, P (P not printed for the 77; the 43 have no error checks, so all of D is P)
    "contra_all": ["-0.172", "-0.109", "-0.063"],
    "contra_avoid": ["-0.224", "-0.170"],
    "contra_no_avoid": ["-0.079"],
    "stuff_all": ["+0.348", "+0.003", "+0.346"],
}

# Short verdict wording for the panel notes (the full strings are in Tables 1 and 2).
SHORT = {"LIKERT-MORE-RELIABLE": "Likert higher", "BOOLEAN-MORE-RELIABLE": "checklist higher",
         "LIKERT-MORE-VALID": "Likert higher", "BOOLEAN-MORE-VALID": "checklist higher",
         "EQUIVALENT": "equivalent", "UNRESOLVED": "too uncertain to call"}


def check(name: str, value: float) -> float:
    got = f"{value:+.3f}"
    if got != ARTICLE[name]:
        sys.exit(f"{name}: the output gives {got}, the article prints {ARTICLE[name]}")
    return value


def check_row(name: str, values: list[float], signed: list[bool]) -> list[float]:
    printed = ARTICLE[name]
    for i, (v, sg) in enumerate(zip(values, signed)):
        got = f"{v:+.3f}" if sg else f"{v:.3f}"
        if got != printed[i]:
            sys.exit(f"{name}[{i}]: the output gives {got}, the article prints {printed[i]}")
    return values


def save(fig, stem: str) -> None:
    FIGDIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGDIR / f"{stem}.png", dpi=200, bbox_inches="tight", metadata={"Software": None})


def slope(ax, a: float, b: float, style: str, label: str | None) -> None:
    """One line from the Likert value (x = 0) to the checklist value (x = 1), ends in the format colors."""
    ax.plot([0, 1], [a, b], color=figstyle.INK2, lw=1.4, ls=style, label=label, zorder=2)
    ax.scatter([0], [a], s=22, color=figstyle.S1, zorder=3, edgecolors=figstyle.SURF, linewidths=0.8)
    ax.scatter([1], [b], s=22, color=figstyle.S2, zorder=3, edgecolors=figstyle.SURF, linewidths=0.8)


def slope_axes(ax, lo: float, hi: float, first: bool, ylabel: str) -> None:
    ax.set_xlim(-0.35, 1.35)
    ax.set_ylim(lo, hi)
    ax.set_xticks([0, 1], ["Likert", "checklist"])
    for t, c in zip(ax.get_xticklabels(), (figstyle.S1, figstyle.S2)):
        t.set_color(c)
    ax.axhline(0, color=figstyle.AXIS, lw=0.6, zorder=1)
    ax.grid(axis="y")
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    if first:
        ax.set_ylabel(ylabel)
    else:
        ax.tick_params(axis="y", labelleft=False)


def note(ax, name: str, d: float, verdict: str, resolved: bool) -> None:
    """The pooled difference and its verdict, under the panel's format labels; bold when it resolves."""
    ax.text(0.5, -0.24, f"{name} {d:+.3f}".replace("-", "\u2212") + f"\n{SHORT[verdict]}",
            transform=ax.transAxes, ha="center", va="top", fontsize=7, linespacing=1.3,
            color=figstyle.INK if resolved else figstyle.MUTED, fontweight="bold" if resolved else "normal")


def fig1(parent: dict) -> None:
    import matplotlib.pyplot as plt
    rows = parent["paper_rows"]["reliability"]
    fig, axes = plt.subplots(2, 5, figsize=(7.2, 5.0))
    for j, (key, title) in enumerate(DIMS):
        r = rows[key]
        vals = [r["1"][0], r["1"][1], r["2"][0], r["2"][1], r["5"][0], r["5"][1], r["3"][0], r["6"][0]]
        check_row(f"R {key}", vals, [False] * 6 + [True, True])
        verdicts = (parent["mohler"] if key == "mohler" else parent["menagerie"][key])["verdicts"]
        ax = axes[0, j]
        slope(ax, r["1"][0], r["1"][1], "-", "Gemini 3.5 Flash Lite")
        slope(ax, r["2"][0], r["2"][1], "--", "GPT-5.4 mini")
        slope_axes(ax, 0.2, 1.02, j == 0, "test–retest r")
        ax.set_title(title, fontsize=8)
        note(ax, "dR", r["3"][0], verdicts["retest"], r["3"][1] > 0 or r["3"][2] < 0)
        ax = axes[1, j]
        slope(ax, r["5"][0], r["5"][1], "-", None)
        slope_axes(ax, -0.3, 1.02, j == 0, "cross-model r")
        note(ax, "dX", r["6"][0], verdicts["cross_model"], r["6"][1] > 0 or r["6"][2] < 0)
    fig.legend(*axes[0, 0].get_legend_handles_labels(), loc="upper left", bbox_to_anchor=(0.07, 1.0),
               ncol=2, fontsize=7, handlelength=2.4)
    fig.subplots_adjust(left=0.08, right=0.99, top=0.86, bottom=0.12, wspace=0.18, hspace=0.95)
    save(fig, "checklist-fig1-reliability")
    plt.close(fig)


def fig2(parent: dict) -> None:
    import matplotlib.pyplot as plt
    rows = parent["paper_rows"]["validity"]
    fig, axes = plt.subplots(1, 5, figsize=(7.2, 2.9))
    for j, (key, title) in enumerate(DIMS):
        r = rows[key]
        vals = [r["2"][0], r["2"][1], r["3"][0], r["3"][1], r["4"][0], r["6"][0]]
        check_row(f"V {key}", vals, [False] * 4 + [True, False])
        verdicts = (parent["mohler"] if key == "mohler" else parent["menagerie"][key])["verdicts"]
        ax = axes[j]
        ax.axhline(r["6"][0], color=figstyle.S3, lw=1.0, ls=":", zorder=1,
                   label="human raters' agreement" if j == 0 else None)
        slope(ax, r["2"][0], r["2"][1], "-", "Gemini 3.5 Flash Lite" if j == 0 else None)
        slope(ax, r["3"][0], r["3"][1], "--", "GPT-5.4 mini" if j == 0 else None)
        slope_axes(ax, -0.35, 0.9, j == 0, "r with the human mean")
        ax.set_title(title, fontsize=8)
        note(ax, "dH", r["4"][0], verdicts["validity"], r["4"][1] > 0 or r["4"][2] < 0)
    fig.legend(*axes[0].get_legend_handles_labels(), loc="upper left", bbox_to_anchor=(0.07, 1.0),
               ncol=3, fontsize=7, handlelength=2.4)
    fig.subplots_adjust(left=0.08, right=0.99, top=0.76, bottom=0.27, wspace=0.18)
    save(fig, "checklist-fig2-human-agreement")
    plt.close(fig)


def fig3(own: dict) -> None:
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(4.6, 2.7))
    bands = [("LOW", "≤ 2.5"), ("MID", "2.5 to 4.5"), ("HIGH", "≥ 4.5")]
    for k, (key, arm, c, dx) in enumerate((("e_likert", "Likert", figstyle.S1, -0.04),
                                           ("e_boolean", "checklist", figstyle.S2, 0.04))):
        est, lo, hi = [], [], []
        for b, _ in bands:
            e = own["bands"][b][key]
            check(f"{b} {key}", e["est"])
            est.append(e["est"]), lo.append(e["ci95"][0]), hi.append(e["ci95"][1])
        xs = [j + dx for j in range(3)]
        ax.fill_between(xs, lo, hi, color=c, alpha=0.12, lw=0)
        ax.plot(xs, est, color=c, lw=2, marker="o", ms=5, mec=figstyle.SURF, mew=0.8)
        ax.text(xs[-1] + 0.08, est[-1], arm, color=figstyle.INK2, va="center", fontsize=8)
    ax.axhline(0, color=figstyle.AXIS, lw=0.6)
    ax.set_xticks(range(3), [f"{b}\n(human {lab}; n={own['bands'][b]['n']})" for b, lab in bands])
    ax.set_xlim(-0.3, 2.6)
    ax.set_ylabel("score − human/5 (0–1 scale)")
    ax.set_title("Signed error against the human mean, by band of human score")
    ax.grid(axis="y")
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    save(fig, "checklist-fig3-error-by-band")
    plt.close(fig)


def fig4(parent: dict) -> None:
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.6), sharey=False)
    for ax, (key, title) in zip(axes, (("contra_manip_pass", "A false sentence appended to a good answer"),
                                        ("stuff_manip_pass", "Key terms appended to a weak answer"))):
        s = parent[key]["stats"]
        kind = "contra" if key.startswith("contra") else "stuff"
        rows = [("pooled", "D.likert", "D.boolean"), ("Gemini", "D.gemini.likert", "D.gemini.boolean"),
                ("GPT", "D.gpt.likert", "D.gpt.boolean")]
        for j, (lab, kl, kb) in enumerate(rows):
            for k, (col, arm, c) in enumerate(((kl, "Likert", figstyle.S1), (kb, "checklist", figstyle.S2))):
                v = s[col]
                if lab == "pooled":
                    check(f"{kind} {col}", v["est"])
                x = j + (k - 0.5) * 0.36
                ax.bar(x, v["est"], 0.34, color=c, label=arm if j == 0 else None)
                ax.errorbar(x, v["est"], yerr=[[v["est"] - v["ci95"][0]], [v["ci95"][1] - v["est"]]],
                            color=figstyle.INK, lw=0.8, capsize=2)
        ax.axhline(0, color=figstyle.AXIS, lw=0.6)
        ax.set_xticks(range(3), [r[0] for r in rows])
        ax.set_title(title)
        ax.set_ylabel("change in score (0–1 scale)")
    axes[0].legend(frameon=False, loc="lower left")
    fig.tight_layout()
    save(fig, "checklist-fig4-planted-defects")
    plt.close(fig)


def fig5(own: dict) -> None:
    import matplotlib.pyplot as plt
    rows = own["paper_rows"]["attribution"]
    a = check_row("contra_all", [rows["contra_all"][c][0] for c in "234"], [True] * 3)
    v = check_row("contra_avoid", [rows["contra_avoid"][c][0] for c in "23"], [True] * 2)
    n = check_row("contra_no_avoid", [rows["contra_no_avoid"]["2"][0]], [True])
    s = check_row("stuff_all", [rows["stuff_all"][c][0] for c in "234"], [True] * 3)
    # (label, error-check part, presence part, total D); the 77's presence part is D − E, computed unrounded
    bars = [("False sentence, all 120 answers", a[1], a[2], a[0]),
            ("False sentence, 77 with an error check", v[1], v[0] - v[1], v[0]),
            ("False sentence, 43 with no error check", 0.0, n[0], n[0]),
            ("Key terms, all 112 answers", s[1], s[2], s[0])]
    fig, ax = plt.subplots(figsize=(6.2, 2.5))
    for j, (lab, av, pr, tot) in enumerate(bars):
        y = len(bars) - 1 - j
        # stack away from zero in each direction: error checks first, presence beyond them
        left = 0.0
        for part, c, name in ((av, figstyle.S3, "error checks (E)"), (pr, figstyle.S4, "presence checks (P)")):
            if abs(part) < 1e-12:
                continue
            ax.barh(y, part, left=left, height=0.56, color=c, edgecolor=figstyle.SURF, linewidth=1.5,
                    label=name if j == 0 else None)
            left += part
        ax.text(tot + (0.012 if tot >= 0 else -0.012), y, f"D {tot:+.3f}".replace("-", "\u2212"), va="center",
                ha="left" if tot >= 0 else "right", fontsize=7, color=figstyle.INK2)
    ax.axvline(0, color=figstyle.AXIS, lw=0.8)
    ax.set_yticks(range(len(bars)), [b[0] for b in reversed(bars)])
    ax.set_xlim(-0.32, 0.45)
    ax.set_xlabel("checklist's change in score (0–1 scale)")
    ax.set_title("Which checks registered each planted defect")
    ax.grid(axis="x")
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(loc="upper right", fontsize=7)
    fig.tight_layout()
    save(fig, "checklist-fig5-check-types")
    plt.close(fig)


def main() -> None:
    import matplotlib
    matplotlib.use("Agg")
    figstyle.apply()
    parent = json.loads(PARENT.read_text())
    own = json.loads(OWN.read_text())
    fig1(parent)
    fig2(parent)
    fig3(own)
    fig4(parent)
    fig5(own)
    print("wrote", ", ".join(str(p.relative_to(REPO)) for p in sorted(FIGDIR.glob("checklist-fig*.png"))))


if __name__ == "__main__":
    main()
