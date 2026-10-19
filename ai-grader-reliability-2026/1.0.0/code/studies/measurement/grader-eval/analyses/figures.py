"""The six figures of Paper VI (research/article/attainment-bias-in-llm-grading.md), from committed outputs.

Release ai-grader-reliability-2026, analysis `figures`. No model call and no corpus is read: every number
plotted comes from an aggregate JSON already committed under studies/measurement/*/out/, except figure 5,
whose trajectories are a re-run of the committed simulation (grader-label-compounding/compounding.py, its
own functions, its committed out/params.json, the primary configuration and the seeds `evaluate` uses).

  fig1  label effect L across models (forest)      grader-model-breadth/out/models.json (six API models),
                                                    grader-fable/out/agent-results.json (Fable, agent route)
  fig2  toward or away from the teacher (dumbbell) grader-model-breadth/out/models.json
  fig3  label value: A shift d by label-gap tercile grader-label-dose/out/posthoc.json (terciles),
                                                    grader-label-dose/out/results.json (pooled rho)
        B Qwen's ASAP 2.0 mean mark by label value  grader-label-dose/out/results.json (asap block)
  fig4  graded examples, shown level vs bias        grader-exemplar-marks/out/results.json; the per-arm
                                                    shown-level offsets (+1.49, -1.43 per example) are the
                                                    study's docstring figures, checked against the shown
                                                    shift it records (2.92)
  fig5  recovery from a false low record (re-run)  grader-label-compounding/compounding.py, out/params.json;
                                                    medians asserted equal to out/results.json
  fig6  group gap at equal true quality by rho     grader-matching-artefact/out/results.json (grid),
                                                    out/reliability-known.json (0.75 and 0.857)

THE CHECKS. Every value the article prints for a plotted quantity is written below (ARTICLE_*) as the
article prints it, and the script stops if the committed output, rounded the same way, does not give
it. Figure 5 also stops unless the re-run's median recovery items equal the committed `recovery`
medians and the article's (23->25, 19->20, 21->23, 19->22).

Design (the dataviz method): one axis per panel, thin marks, hairline recessive grid, text in ink
colours never series colours, categorical slots 1-3 (#2a78d6, #eb6834, #1baf7a) in fixed order, model
identity on the axis, a legend wherever two or more series appear. Light mode only (print).

    python3 studies/measurement/grader-eval/analyses/figures.py
writes research/article/figures/fig{1..6}-*.svg and .png (300 dpi). matplotlib 3.11.2, numpy 2.4.6
(requirements.txt beside this file).
"""
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
M = ROOT / "studies" / "measurement"
OUT = ROOT / "research" / "article" / "figures"

# ------------------------------------------------------------------ palette (dataviz reference, light)
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"     # categorical slots 1-3
S1_LIGHT = "#86b6ef"                             # blue step 250, the second shade of a dumbbell
SURF = "#fcfcfb"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS = "#e1e0d9", "#c3c2b7"
WASH = "#f0efec"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Liberation Sans", "Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 8,
    "axes.titlesize": 8.5,
    "axes.titleweight": "bold",
    "axes.titlecolor": INK,
    "axes.titlelocation": "left",
    "axes.labelsize": 8,
    "axes.labelcolor": INK2,
    "axes.edgecolor": AXIS,
    "axes.linewidth": 0.6,
    "axes.facecolor": SURF,
    "figure.facecolor": SURF,
    "savefig.facecolor": SURF,
    "xtick.color": AXIS,
    "ytick.color": AXIS,
    "xtick.labelcolor": INK2,
    "ytick.labelcolor": INK2,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.size": 3,
    "ytick.major.size": 0,
    "legend.fontsize": 7.5,
    "legend.frameon": False,
    "legend.labelcolor": INK2,
    "lines.solid_capstyle": "round",
    "lines.solid_joinstyle": "round",
    "svg.hashsalt": "paper-vi-figures",
    "svg.fonttype": "path",
})


def load(rel: str) -> dict:
    return json.loads((M / rel).read_text())


def f2(x: float) -> str:
    """The article's two-decimal signed format (minus as U+2212)."""
    s = f"{x:+.2f}"
    return s.replace("-", "−")


KNOWN_DISCREPANCIES = {
    # Empty. The one entry this held (the RQ6 table's GPT-4.1-mini economic gap at reliability 0.75,
    # printed -0.10 against the committed -0.0946) was corrected in the article and the study README.
}


def check(name: str, got: str, want: str) -> None:
    if name in KNOWN_DISCREPANCIES and got == KNOWN_DISCREPANCIES[name]:
        print(f"KNOWN DISCREPANCY {name}: committed output gives {got}, article prints {want}")
        return
    if got != want:
        raise SystemExit(f"MISMATCH {name}: committed output gives {got}, article prints {want}")


def style(ax, grid_axis="x"):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.6, linestyle="-")
    ax.set_axisbelow(True)


def zero_line(ax, vertical=True):
    if vertical:
        ax.axvline(0, color=AXIS, linewidth=0.9, zorder=1)
    else:
        ax.axhline(0, color=AXIS, linewidth=0.9, zorder=1)


def save(fig, stem: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{stem}.svg", metadata={"Date": None, "Creator": None})
    fig.savefig(OUT / f"{stem}.png", dpi=300, metadata={"Software": None})
    plt.close(fig)
    print("wrote", OUT.relative_to(ROOT) / f"{stem}.svg", "and .png")


def dot(ax, x, y, color, marker="o", size=5.5, z=4, **kw):
    """A filled marker with a 2px-equivalent surface ring."""
    ax.plot(x, y, marker=marker, markersize=size, color=color, markeredgecolor=SURF,
            markeredgewidth=1.1, linestyle="none", zorder=z, **kw)


# ------------------------------------------------------------------ the article's values

MODELS = [  # paper order, models.json key, axis label
    ("google:gemini-3.5-flash-lite", "Gemini 3.5 Flash Lite"),
    ("openai:gpt-4.1-mini", "GPT-4.1-mini"),
    ("openai:gpt-5-mini", "GPT-5-mini"),
    ("openrouter:qwen/qwen3-235b-a22b-2507", "Qwen3-235B"),
    ("openrouter:anthropic/claude-opus-5.5", "Claude Opus 5.5"),
    ("openrouter:meta-llama/llama-4-maverick", "Llama 4 Maverick"),
]
# Cross-model table under RQ2: L [95%]; L high / low; bias control high / low; bias true label high / low
ARTICLE_RQ2 = {
    "Gemini 3.5 Flash Lite": ("+0.37", "+0.30", "+0.44", "+0.42", "+0.32", "+0.20", "+0.49", "+0.44", "+0.27"),
    "GPT-4.1-mini": ("+0.38", "+0.30", "+0.46", "+0.50", "+0.26", "−1.30", "−0.46", "−1.22", "−0.72"),
    "GPT-5-mini": ("+0.52", "+0.43", "+0.61", "+0.57", "+0.47", "−0.98", "+0.08", "−0.97", "−0.44"),
    "Qwen3-235B": ("+0.75", "+0.69", "+0.82", "+0.79", "+0.72", "−1.52", "−0.41", "−1.29", "−0.75"),
    "Claude Opus 5.5": ("+0.28", "+0.23", "+0.32", "+0.30", "+0.25", "−1.79", "−0.83", "−1.63", "−0.94"),
    "Llama 4 Maverick": ("+0.54", "+0.42", "+0.65", "+0.51", "+0.56", "−1.19", "−0.40", "−0.66", "−0.42"),
}
ARTICLE_TOWARD = {  # "Toward or away (high, low)" column
    "Gemini 3.5 Flash Lite": ("unresolved", "toward"), "GPT-4.1-mini": ("toward", "away"),
    "GPT-5-mini": ("no move", "unresolved"), "Qwen3-235B": ("toward", "away"),
    "Claude Opus 5.5": ("toward", "away"), "Llama 4 Maverick": ("toward", "no move"),
}
ARTICLE_FABLE = ("+0.31", "+0.19", "+0.45", "+0.44", "+0.19")      # L [95%], L high, L low (RQ5)


def rq2_rows():
    pm = load("grader-model-breadth/out/models.json")["per_model"]
    rows = []
    for key, name in MODELS:
        lc = pm[key]["learner_cluster"]
        r = {k: lc[k]["est"] for k in ("L", "L_high", "L_low", "bias_control_high", "bias_control_low",
                                       "bias_true_high", "bias_true_low")}
        r["L_ci"] = lc["L"]["ci95"]
        r["name"] = name
        q2 = pm[key]["q2"]
        r["call"] = tuple({"FLAT": "no move"}.get(q2[t], q2[t].lower()) for t in ("high_tail", "low_tail"))
        got = (f2(r["L"]), f2(r["L_ci"][0]), f2(r["L_ci"][1]), f2(r["L_high"]), f2(r["L_low"]),
               f2(r["bias_control_high"]), f2(r["bias_control_low"]), f2(r["bias_true_high"]),
               f2(r["bias_true_low"]))
        for i, (g, w) in enumerate(zip(got, ARTICLE_RQ2[name])):
            check(f"RQ2 {name} col {i}", g, w)
        check(f"RQ2 {name} toward/away", str(r["call"]), str(ARTICLE_TOWARD[name]))
        rows.append(r)
    return rows


# ------------------------------------------------------------------ figure 1

def fig1():
    rows = rq2_rows()
    fa = load("grader-fable/out/agent-results.json")["fable_agent"]
    got = (f2(fa["L"]["est"]), f2(fa["L"]["ci95"][0]), f2(fa["L"]["ci95"][1]), f2(fa["L_high"]["est"]),
           f2(fa["L_low"]["est"]))
    for i, (g, w) in enumerate(zip(got, ARTICLE_FABLE)):
        check(f"Fable col {i}", g, w)

    fig, ax = plt.subplots(figsize=(6.5, 3.15))
    fig.subplots_adjust(left=0.22, right=0.80, top=0.86, bottom=0.15)
    n = len(rows)
    ys = list(range(n + 1, 1, -1))           # API models at n+1..2, Fable at 0
    y_f = 0
    entries = [(y, r["name"], r["L"], r["L_ci"], r["L_high"], r["L_low"]) for y, r in zip(ys, rows)]
    entries.append((y_f, "Claude Fable 5.1", fa["L"]["est"], fa["L"]["ci95"], fa["L_high"]["est"],
                    fa["L_low"]["est"]))
    zero_line(ax)
    for y, name, L, ci, lh, ll in entries:
        ax.plot(ci, [y, y], color=S1, linewidth=2, zorder=3)
        dot(ax, lh, y + 0.26, S2, marker="^", size=5, z=5)
        dot(ax, ll, y - 0.26, S3, marker="v", size=5, z=5)
        dot(ax, L, y, S1, size=7, z=6)
        txt = f"{f2(L)} [{f2(ci[0])}, {f2(ci[1])}]"
        ax.text(1.02, y, txt, transform=ax.get_yaxis_transform(), va="center", ha="left",
                fontsize=7.5, color=INK2)
    ax.axhline(1.0, color=AXIS, linewidth=0.6, xmin=-0.33, clip_on=False)
    ax.set_yticks([e[0] for e in entries])
    ax.set_yticklabels([e[1] for e in entries], color=INK)
    ax.text(-0.012, y_f - 0.42, "run in Claude Code sessions,\nnot the API; not pooled",
            transform=ax.get_yaxis_transform(), ha="right", va="top", fontsize=6.5, color=MUTED)
    ax.text(1.02, n + 2.15, "L [95%]", transform=ax.get_yaxis_transform(), ha="left", va="center",
            fontsize=7.5, color=INK, fontweight="bold")
    ax.set_ylim(-1.15, n + 2.6)
    ax.set_xlim(-0.05, 1.0)
    ax.set_xticks(np.arange(0, 1.01, 0.2))
    ax.set_xlabel("Mark under the high label minus mark under the low label, same answer (points of 10)")
    style(ax, "x")
    ax.spines["left"].set_visible(False)
    handles = [
        Line2D([], [], color=S1, linewidth=2, marker="o", markersize=6, markeredgewidth=0,
               label="L, both tails, with 95% interval"),
        Line2D([], [], color=S2, linestyle="none", marker="^", markersize=5.5, markeredgecolor=SURF,
               label="L in the high tail"),
        Line2D([], [], color=S3, linestyle="none", marker="v", markersize=5.5, markeredgecolor=SURF,
               label="L in the low tail"),
    ]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.21, 0.995), ncol=3,
               handlelength=1.6, columnspacing=1.4)
    save(fig, "fig1-label-effect-across-models")


# ------------------------------------------------------------------ figure 2

def fig2():
    rows = rq2_rows()
    fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.95), sharey=True)
    fig.subplots_adjust(left=0.165, right=0.90, top=0.79, bottom=0.17, wspace=0.30)
    n = len(rows)
    ys = list(range(n - 1, -1, -1))
    for ax, tail, title in ((axes[0], "high", "High tail (attainment 6 or more)"),
                            (axes[1], "low", "Low tail (attainment below 4)")):
        zero_line(ax)
        ax.text(0, n - 0.42, "teacher", ha="center", va="bottom", fontsize=6.5, color=MUTED,
                bbox=dict(boxstyle="square,pad=0.15", facecolor=SURF, edgecolor="none"), zorder=6)
        for y, r in zip(ys, rows):
            c, t = r[f"bias_control_{tail}"], r[f"bias_true_{tail}"]
            if abs(t - c) >= 0.05:
                ax.annotate("", xy=(t, y), xytext=(c, y), zorder=3,
                            arrowprops=dict(arrowstyle="-|>,head_length=0.4,head_width=0.2", color=S1,
                                            linewidth=1.5, shrinkA=2.5, shrinkB=3.0))
            dot(ax, c, y, S1_LIGHT, size=6)
            dot(ax, t, y, S1, size=6, z=5)
            call = r["call"][0 if tail == "high" else 1]
            strong = call in ("toward", "away")
            ax.text(1.03, y, call, transform=ax.get_yaxis_transform(), ha="left", va="center",
                    fontsize=6.8, color=INK if strong else MUTED, fontweight="bold" if strong else "normal")
        ax.set_title(title, pad=10)
        ax.set_xlim(-2.0, 0.75)
        ax.set_xticks([-2, -1.5, -1, -0.5, 0, 0.5])
        ax.set_xticklabels(["\u22122.0", "\u22121.5", "\u22121.0", "\u22120.5", "0", "+0.5"])
        ax.set_ylim(-0.6, n - 0.1)
        style(ax, "x")
        ax.spines["left"].set_visible(False)
        ax.set_xlabel("Bias: grader minus teacher (points of 10)")
    axes[0].set_yticks(ys)
    axes[0].set_yticklabels([r["name"] for r in rows], color=INK)
    handles = [
        Line2D([], [], color=S1_LIGHT, linestyle="none", marker="o", markersize=6, markeredgewidth=0,
               label="no label (control)"),
        Line2D([], [], color=S1, linestyle="none", marker="o", markersize=6, markeredgewidth=0,
               label="the student's true label"),
    ]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.165, 1.0), ncol=2,
               columnspacing=1.6, handletextpad=0.3)
    fig.text(0.985, 0.955, "words at right: the pre-registered\ncall for each model and tail",
             ha="right", va="center", fontsize=6.5, color=MUTED)
    save(fig, "fig2-toward-or-away")


# ------------------------------------------------------------------ figure 3

ARTICLE_DOSE = {"rho": ("+0.84", "+0.38", "+1.36"), "per_point_low_to_mid": "0.28",
                "per_point_mid_to_high": "0.13", "high_minus_none": ("−0.01", "−0.03", "+0.00")}
DOSE_ORDER = [("gemini", "Gemini 3.5 Flash Lite"), ("gpt41mini", "GPT-4.1-mini"), ("gpt5mini", "GPT-5-mini"),
              ("qwen", "Qwen3-235B"), ("opus55", "Claude Opus 5.5"), ("llama4", "Llama 4 Maverick")]


def fig3():
    res = load("grader-label-dose/out/results.json")
    post = load("grader-label-dose/out/posthoc.json")
    pooled, asap = res["pooled"], res["asap"]
    check("pooled rho", (f2(pooled["rho"]), f2(pooled["rho_ci"][0]), f2(pooled["rho_ci"][1])).__repr__(),
          ARTICLE_DOSE["rho"].__repr__())
    check("asap low->mid", f"{asap['point']['per_point_low_to_mid']:.2f}", ARTICLE_DOSE["per_point_low_to_mid"])
    check("asap mid->high", f"{asap['point']['per_point_mid_to_high']:.2f}", ARTICLE_DOSE["per_point_mid_to_high"])
    hmn = (f2(asap["point"]["high_minus_none"]), f2(asap["ci"]["high_minus_none"][0]),
           f2(asap["ci"]["high_minus_none"][1]))
    check("asap high-none", repr(hmn), repr(ARTICLE_DOSE["high_minus_none"]))
    for k, _ in DOSE_ORDER:   # the tercile table in posthoc.json is the one results.json carries
        assert post["terciles"][k] == res["models"][k]["d_by_g_tercile"], k

    fig, (a, b) = plt.subplots(1, 2, figsize=(6.5, 2.9), gridspec_kw={"width_ratios": [1.1, 1]})
    fig.subplots_adjust(left=0.08, right=0.975, top=0.80, bottom=0.17, wspace=0.42)

    # Panel A: each model's mean shift by gap tercile, and their unweighted mean
    gs, ds = [], []
    ends = []
    for k, name in DOSE_ORDER:
        t = post["terciles"][k]
        g = [x["g_mean"] for x in t]
        d = [x["d_mean"] for x in t]
        gs.append(g)
        ds.append(d)
        a.plot(g, d, color=AXIS, linewidth=1.0, zorder=2)
        ends.append((d[-1], g[-1], name))
    gm, dm = np.mean(gs, axis=0), np.mean(ds, axis=0)
    a.plot(gm, dm, color=S1, linewidth=2, zorder=4)
    dot(a, gm, dm, S1, size=6, z=5)
    for d_end, g_end, name in ends:
        a.text(g_end + 0.08, d_end, name, va="center", ha="left", fontsize=6.5, color=INK2)
    a.set_xlim(2.4, 6.15)
    a.set_xticks([3, 4, 5])
    a.set_ylim(0, 1.0)
    a.set_yticks(np.arange(0, 1.01, 0.2))
    a.set_xlabel("Gap between the two labels, tercile mean (points of 10)")
    a.set_ylabel("Shift d on the same answer (points of 10)")
    a.set_title("A  Shift by label gap, six models (Corpus A)", pad=16)
    a.text(0.0, 1.025, f"pooled relative slope ρ = {f2(pooled['rho'])} [{f2(pooled['rho_ci'][0])}, "
           f"{f2(pooled['rho_ci'][1])}]; 1 = proportional, 0 = step", transform=a.transAxes,
           fontsize=6.5, color=MUTED, va="bottom")
    style(a, "y")
    a.tick_params(axis="y", length=0)
    a.legend(handles=[Line2D([], [], color=AXIS, linewidth=1, label="each model"),
                      Line2D([], [], color=S1, linewidth=2, marker="o", markersize=5, markeredgewidth=0,
                             label="mean of the six")],
             loc="upper left", handlelength=1.6)

    # Panel B: Qwen on ASAP 2.0, mean mark under each label value; no label as a reference
    m = asap["means"]
    xv = [1.9, 3.0, 4.2]
    yv = [m["low"], m["mid"], m["high"]]
    b.axhline(m["none"], color=MUTED, linewidth=0.9, zorder=1)
    b.text(1.62, m["none"] + 0.012, f"no label {m['none']:.2f}", fontsize=6.8, color=INK2, va="bottom")
    b.plot(xv, yv, color=S1, linewidth=2, zorder=3)
    dot(b, xv, yv, S1, size=6.5, z=4)
    for x, y, dx, ha in zip(xv, yv, (0.1, -0.1, 0.0), ("left", "right", "center")):
        b.text(x + dx, y if dx else y - 0.035, f"{y:.2f}", ha=ha, va="center" if dx else "top",
               fontsize=6.8, color=INK2)
    pp, ci = asap["point"], asap["ci"]
    b.text(4.5, 2.62,
           "per label point, paired 95%:\n"
           f"low to mid   +{pp['per_point_low_to_mid']:.2f} [{ci['per_point_low_to_mid'][0]:.2f}, "
           f"{ci['per_point_low_to_mid'][1]:.2f}]\n"
           f"mid to high  +{pp['per_point_mid_to_high']:.2f} [{ci['per_point_mid_to_high'][0]:.2f}, "
           f"{ci['per_point_mid_to_high'][1]:.2f}]",
           ha="right", va="top", fontsize=6.5, color=INK2, linespacing=1.45,
           bbox=dict(boxstyle="square,pad=0.2", facecolor=SURF, edgecolor="none"))
    b.text(4.2, m["none"] + 0.075, f"high \u2212 no label {hmn[0]} [{hmn[1]}, {hmn[2]}]", ha="right",
           va="bottom", fontsize=6.5, color=INK2)
    b.set_xlim(1.5, 4.5)
    b.set_xticks(xv)
    b.set_xticklabels(["low\n1.9", "mid\n3.0", "high\n4.2"])
    b.set_ylim(2.4, 3.15)
    b.set_yticks([2.4, 2.6, 2.8, 3.0])
    b.set_xlabel("Label shown (attainment out of 6)")
    b.set_ylabel("Mean mark, same 2,996 essays (1–6)")
    b.set_title("B  Qwen3-235B on ASAP 2.0, by label value", pad=16)
    b.text(0.0, 1.025, "intervals are for the paired differences (essay bootstrap)", transform=b.transAxes,
           fontsize=6.5, color=MUTED, va="bottom")
    style(b, "y")
    b.tick_params(axis="y", length=0)
    save(fig, "fig3-label-value")


# ------------------------------------------------------------------ figure 4

ARTICLE_EX = {"control": ("+0.19", "−0.01", "+0.41"), "ungraded": ("+0.61", "+0.43", "+0.79"),
              "correct": ("−0.15", "−0.34", "+0.06"), "shuffled": ("+0.06", "−0.11", "+0.26"),
              "shiftUp": ("+0.33", "+0.15", "+0.52"), "shiftDown": ("−0.80", "−1.00", "−0.57")}
SHOWN_OFFSET = {"shiftDown": -1.43, "correct": 0.0, "shiftUp": +1.49}   # analyse.py docstring, per example


def fig4():
    g = load("grader-exemplar-marks/out/results.json")["models"][0]
    assert g["model"] == "google:gemini-3.5-flash-lite" and g["n_complete"] == 600
    q = g["intervals"]["question"]
    arms = q["arms"]
    for k, want in ARTICLE_EX.items():
        b = arms[k]["bias"]
        check(f"exemplar {k}", repr((f2(b["est"]), f2(b["ci95"][0]), f2(b["ci95"][1]))), repr(want))
    check("shown shift", f"{q['shown_shift']:.2f}", "2.92")
    check("docstring offsets", f"{SHOWN_OFFSET['shiftUp'] - SHOWN_OFFSET['shiftDown']:.2f}",
          f"{q['shown_shift']:.2f}")
    kap = q["kappa"]
    check("kappa", f"{kap['est']:.2f} [{kap['ci95'][0]:.2f}, {kap['ci95'][1]:.2f}]", "0.39 [0.35, 0.42]")

    fig, ax = plt.subplots(figsize=(5.2, 3.1))
    fig.subplots_adjust(left=0.13, right=0.70, top=0.86, bottom=0.2)
    zero_line(ax, vertical=False)
    ax.text(2.02, 0, "teacher", va="center", ha="left", fontsize=6.8, color=MUTED)
    for k, lab in (("control", "control, no examples"), ("ungraded", "examples without marks")):
        v = arms[k]["bias"]["est"]
        ax.axhline(v, color=MUTED, linewidth=0.9, zorder=1)
        ax.text(2.02, v, f"{lab} {f2(v)}", va="center", ha="left", fontsize=6.8, color=INK2)
    xs = [SHOWN_OFFSET[k] for k in ("shiftDown", "correct", "shiftUp")]
    ys = [arms[k]["bias"]["est"] for k in ("shiftDown", "correct", "shiftUp")]
    for k, x in zip(("shiftDown", "correct", "shiftUp"), xs):
        lo, hi = arms[k]["bias"]["ci95"]
        ax.plot([x, x], [lo, hi], color=S1, linewidth=1.2, zorder=3)
    ax.plot(xs, ys, color=S1, linewidth=2, zorder=3)
    dot(ax, xs, ys, S1, size=6.5, z=5)
    sx = 0.28
    lo, hi = arms["shuffled"]["bias"]["ci95"]
    ax.plot([sx, sx], [lo, hi], color=S2, linewidth=1.2, zorder=3)
    dot(ax, sx, arms["shuffled"]["bias"]["est"], S2, marker="D", size=5.5, z=5)
    for x, y, side in zip(xs, ys, (-1, -1, 1)):
        ax.text(x + side * 0.11, y, f2(y), ha="right" if side < 0 else "left", va="center", fontsize=6.8,
                color=INK2)
    ax.text(sx, hi + 0.03, f2(arms["shuffled"]["bias"]["est"]), ha="center", va="bottom", fontsize=6.8,
            color=INK2)
    ax.text(-1.88, 0.78, f"slope {kap['est']:.2f} points of grade per point of\nshown level "
            f"[{kap['ci95'][0]:.2f}, {kap['ci95'][1]:.2f}] (1.13 over 2.92)", fontsize=6.5, color=INK2,
            va="center")
    ax.set_xlim(-1.95, 1.95)
    ax.set_xticks(xs)
    ax.set_xticklabels(["shifted down 2\n−1.43", "correct\n0", "shifted up 2\n+1.49"])
    ax.set_xlabel("Marks shown on the three examples: mean offset from the teacher's (points)")
    ax.set_ylim(-1.1, 1.0)
    ax.set_yticks([-1.0, -0.5, 0, 0.5, 1.0])
    ax.set_yticklabels(["−1.0", "−0.5", "0", "+0.5", "+1.0"])
    ax.set_ylabel("Bias: grader minus teacher (points of 10)")
    style(ax, "y")
    ax.tick_params(axis="y", length=0)
    handles = [
        Line2D([], [], color=S1, linewidth=2, marker="o", markersize=5.5, markeredgewidth=0,
               label="examples with the teacher's marks, shifted or not"),
        Line2D([], [], color=S2, linestyle="none", marker="D", markersize=5, markeredgecolor=SURF,
               label="the same marks shuffled among the examples"),
    ]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.13, 1.0), ncol=1, handlelength=1.8)
    save(fig, "fig4-graded-examples")


# ------------------------------------------------------------------ figure 5

ARTICLE_RECOVERY = {"google:gemini-3.5-flash-lite": (23, 25), "openai:gpt-4.1-mini": (19, 20),
                    "openai:gpt-5-mini": (21, 23), "openrouter:qwen/qwen3-235b-a22b-2507": (19, 22)}
SIM_NAMES = {"google:gemini-3.5-flash-lite": "Gemini 3.5 Flash Lite", "openai:gpt-4.1-mini": "GPT-4.1-mini",
             "openai:gpt-5-mini": "GPT-5-mini", "openrouter:qwen/qwen3-235b-a22b-2507": "Qwen3-235B"}


def recovery_trajectories():
    """Re-run recovery_estimands' own steps, keeping the four belief trajectories it discards."""
    d = M / "grader-label-compounding"
    spec = importlib.util.spec_from_file_location("compounding", d / "compounding.py")
    C = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(C)
    prm = json.loads((d / "out" / "params.json").read_text())
    committed = json.loads((d / "out" / "results.json").read_text())["per_model"]
    cohort, lab = prm["cohort"], prm["tail_labels"]
    cfg = C.CONFIGS["primary"]
    T = cohort["T"]
    out = {}
    for mname, mv in prm["models"].items():
        P = mv["fit"]
        c2 = dict(cohort)                                          # as _run_model builds it
        a, b = (0.0, 1.0) if cfg.get("calibrated") else (P["a"], P["b"])
        mg = np.clip((a + b * cohort["mu_theta"]) / 10.0, 0.02, 0.98)
        c2["mu_logit"] = float(math.log(mg / (1 - mg)))
        seed = C.arm_seed(C.SEED, f"{mname}-primary") + 7          # evaluate(): recovery seed = seed + 7
        rng = np.random.default_rng(seed)
        theta = np.full(C.N_REC, 7.0)
        theta, h, e, u = C.draw_cohort(C.N_REC, T, c2, P, cfg, rng, theta=theta)
        rec = {}
        for nm, edge in (("noedge", False), ("edge", True)):
            dflt = C.run_engine(theta, h, e, u, P, cfg, edge, c2, lab)
            shock = C.run_engine(theta, h, e, u, P, cfg, edge, c2, lab, shock=True)
            far = np.abs(shock - dflt) >= C.REC_TOL
            idx = np.where(far.any(1), T - np.argmax(far[:, ::-1], axis=1), 0)
            r = np.where(far[:, -1], T + 1, idx + 1)
            rec[nm] = {"default": dflt.mean(0), "shock": shock.mean(0), "median": float(np.median(r))}
        want_c = committed[mname]["primary"]["recovery"]["point"]
        got = (rec["noedge"]["median"], rec["edge"]["median"])
        if got != (want_c["rec_median_noedge"], want_c["rec_median_edge"]):
            raise SystemExit(f"fig5: {mname} re-run medians {got} differ from committed results.json "
                             f"({want_c['rec_median_noedge']}, {want_c['rec_median_edge']})")
        if got != tuple(float(x) for x in ARTICLE_RECOVERY[mname]):
            raise SystemExit(f"fig5: {mname} re-run medians {got} differ from the article {ARTICLE_RECOVERY[mname]}")
        out[mname] = rec
    return out, C.REC_TOL


def fig5():
    traj, tol = recovery_trajectories()
    print("fig5: re-run median recovery items equal committed and article values:",
          {SIM_NAMES[m]: (int(r["noedge"]["median"]), int(r["edge"]["median"])) for m, r in traj.items()})
    fig, axes = plt.subplots(2, 2, figsize=(6.5, 4.6), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.09, right=0.985, top=0.86, bottom=0.11, hspace=0.32, wspace=0.08)
    items = np.arange(1, 41)
    for ax, (mname, rec) in zip(axes.flat, traj.items()):
        for nm, col in (("noedge", S1), ("edge", S2)):
            ax.plot(items, rec[nm]["default"], color=col, linewidth=1.0, alpha=0.75, zorder=2)
            ax.plot(items, rec[nm]["shock"], color=col, linewidth=2, zorder=3)
            md = int(rec[nm]["median"])
            dot(ax, md, rec[nm]["shock"][md - 1], col, size=6, z=5)
        n0, n1 = int(rec["noedge"]["median"]), int(rec["edge"]["median"])
        ax.text(0.98, 0.06, f"median recovery item: {n0} without the edge, {n1} with it", transform=ax.transAxes, ha="right",
                va="bottom", fontsize=6.8, color=INK2)
        ax.set_title(SIM_NAMES[mname], pad=4)
        style(ax, "y")
        ax.tick_params(axis="y", length=0)
        ax.set_xlim(0, 41)
        ax.set_xticks([1, 10, 20, 30, 40])
        ax.set_ylim(0.25, 0.75)
        ax.set_yticks([0.3, 0.4, 0.5, 0.6, 0.7])
    for ax in axes[1]:
        ax.set_xlabel("Graded item over the term")
    for ax in axes[:, 0]:
        ax.set_ylabel("Mean belief (0–1), θ = 7")
    handles = [
        Line2D([], [], color=S1, linewidth=2, label="no label edge, false low start"),
        Line2D([], [], color=S2, linewidth=2, label="label edge, false low start"),
        Line2D([], [], color=S1, linewidth=1, alpha=0.75, label="no label edge, correct start"),
        Line2D([], [], color=S2, linewidth=1, alpha=0.75, label="label edge, correct start"),
        Line2D([], [], color=INK2, linestyle="none", marker="o", markersize=5.5, markeredgecolor=SURF,
               label="median recovery item"),
    ]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.09, 1.0), ncol=3, handlelength=1.8,
               columnspacing=1.2)
    save(fig, "fig5-loop-recovery")


# ------------------------------------------------------------------ figure 6

AXES6 = [("ell", "English learners", S1), ("economic", "economically disadvantaged", S2),
         ("disability", "disability-identified", S3)]
MODELS6 = [("openai:gpt-4.1-mini", "GPT-4.1-mini"), ("openrouter:qwen/qwen3-235b-a22b-2507", "Qwen3-235B")]
ARTICLE_RQ6 = {  # rows "reliability 0.75" and "reliability 0.86": ELL / economic / disability
    ("GPT-4.1-mini", 0.75): ("−0.15", "−0.09", "−0.21"), ("Qwen3-235B", 0.75): ("−0.17", "−0.12", "−0.22"),
    ("GPT-4.1-mini", 0.86): ("−0.18", "−0.12", "−0.25"), ("Qwen3-235B", 0.86): ("−0.21", "−0.15", "−0.27"),
}


def fig6():
    res = load("grader-matching-artefact/out/results.json")["per_model"]
    rk = load("grader-matching-artefact/out/reliability-known.json")["per_model"]
    rho_best = load("grader-matching-artefact/out/reliability-known.json")["rhos"]["best_estimate_spearman_brown"]
    bes = []
    for mk, mname in MODELS6:
        for rho, key in ((0.75, "lower_bound_one_rater"), (0.86, "best_estimate_spearman_brown")):
            got = tuple(f2(rk[mk][ax][key]["C"]) for ax, _, _ in AXES6)
            check(f"RQ6 {mname} {rho}", repr(got), repr(ARTICLE_RQ6[(mname, rho)]))
        for ax, _, _ in AXES6:   # the grid point at 0.75 is the known-reliability reading
            assert abs(res[mk]["axes"][ax]["by_rho"]["0.75"]["C"] - rk[mk][ax]["lower_bound_one_rater"]["C"]) < 1e-12
            bes.append(res[mk]["axes"][ax]["break_even_rho"])
    check("break-even range", f"{min(bes):.2f}–{max(bes):.2f}", "0.49–0.52")

    fig, axs = plt.subplots(1, 2, figsize=(6.5, 3.0), sharey=True)
    fig.subplots_adjust(left=0.09, right=0.985, top=0.80, bottom=0.16, wspace=0.08)
    for a, (mk, mname) in zip(axs, MODELS6):
        a.axvspan(0.75, rho_best, color=WASH, zorder=0, linewidth=0)
        a.text((0.75 + rho_best) / 2, 0.205, "raters'\nagreement", ha="center", va="top", fontsize=6.5,
               color=INK2)
        be_m = [res[mk]["axes"][ax]["break_even_rho"] for ax, _, _ in AXES6]
        a.axvspan(min(be_m), max(be_m), color=WASH, zorder=0, linewidth=0)
        a.text((min(be_m) + max(be_m)) / 2, 0.205, "break-\neven", ha="center", va="top", fontsize=6.5,
               color=INK2)
        zero_line(a, vertical=False)
        for ax, lab, col in AXES6:
            A = res[mk]["axes"][ax]
            low = A["low_rho_points"]
            grid = A["by_rho"]
            rl = [float(r) for r in low if float(r) >= 0.45]
            rg = sorted(float(r) for r in grid)
            xs = rl + rg
            ys = [low[f"{r:g}"]["C"] for r in rl] + [grid[f"{r:g}"]["C"] for r in rg]
            lo = [grid[f"{r:g}"]["C_ci"][0] for r in rg]
            hi = [grid[f"{r:g}"]["C_ci"][1] for r in rg]
            a.fill_between(rg, lo, hi, color=col, alpha=0.10, linewidth=0, zorder=1)
            a.plot(xs, ys, color=col, linewidth=2, zorder=3)
            for key in ("lower_bound_one_rater", "best_estimate_spearman_brown"):
                k = rk[mk][ax][key]
                dot(a, k["rho"], k["C"], col, size=5.5, z=5)
        a.set_title(mname, pad=4)
        a.set_xlim(0.44, 0.96)
        a.set_xticks([0.5, 0.6, 0.7, 0.75, 0.8, 0.86, 0.9])
        a.set_xticklabels(["0.5", "0.6", "0.7", ".75", "0.8", ".86", "0.9"])
        a.set_ylim(-0.42, 0.22)
        a.set_yticks([-0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2])
        a.set_yticklabels(["−0.4", "−0.3", "−0.2", "−0.1", "0", "+0.1", "+0.2"])
        a.set_xlabel("Assumed reliability of the human score")
        style(a, "y")
        a.tick_params(axis="y", length=0)
    axs[0].set_ylabel("Gap at equal true quality\n(grader − human, focal − peers; levels of 1–6)")
    handles = [Line2D([], [], color=col, linewidth=2, label=lab) for _, lab, col in AXES6]
    handles.append(Line2D([], [], color=INK2, linestyle="none", marker="o", markersize=5, markeredgecolor=SURF,
                          label="the table's rows (0.75, 0.86)"))
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.09, 1.0), ncol=4, handlelength=1.6,
               columnspacing=1.2)
    fig.text(0.09, 0.875, "bands: 95% bootstrap interval with reliability fixed (computed from 0.60 up)",
             fontsize=6.5, color=MUTED, ha="left", va="center")
    save(fig, "fig6-group-gap-by-reliability")


if __name__ == "__main__":
    import sys
    ALL = {"1": fig1, "2": fig2, "3": fig3, "4": fig4, "5": fig5, "6": fig6}
    for k in (sys.argv[1:] or list(ALL)):   # e.g. `figures.py 3 5` redraws figures 3 and 5 only
        ALL[k]()
