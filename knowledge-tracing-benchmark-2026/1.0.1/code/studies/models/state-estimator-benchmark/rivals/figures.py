"""Figures 1 and 2 of release knowledge-tracing-benchmark-2026, from the release's summary tables only
(out/tables.json, written by tables.py from the per-case outputs). Written 20 Nov 2026. Reads no corpus.

Figure 1: test AUC with all training learners, per model and corpus: the mean over five folds (dot) and the lowest
to highest fold (line). Hollow dots: numbers that are descriptive only under the registered rule (no floor run, the
floor not passed, or a floor run outside the registered stage lists, R0597; IRT, the reference, is drawn filled).

Figure 2: change in mean test AUC from the fits with all training learners, with 2% of the training learners
(circles) and with every training learner's history cut to its first 20 answers (squares), per model and corpus.
Hollow marks: descriptive only (for 2%, no floor passed at 2%; for the history cut, the model's floor status).
IRT, the reference, is drawn filled throughout.

Colours follow shared/figstyle.py's slots in order, one per family: item response and logistic (S1), Bayesian
and count (S2), recurrent and time-aware deep (S3), attention (S4, labelled directly by the axis).

Before drawing, the script checks every value Tables 5 and 7 of the article print, rounded the article's way, against
the summary tables, and stops if one differs: a printed value that does not match is a paper error.

    python3 figures.py     writes research/article/figures/knowledge-tracing-benchmark-2026/fig1-main-auc.{png,svg}
                           and fig2-thinning.{png,svg}
Two runs give byte-identical files on one machine (fonts decide the bytes).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
from shared import figstyle  # noqa: E402

TABLES = HERE / "out/tables.json"
OUT = ROOT / "research/article/figures/knowledge-tracing-benchmark-2026"
ORDER = ["IRT", "PFA", "Best-LR", "Best-LR-iter1000", "Best-LR+", "BKT", "running-proportion",
         "DKT", "IEKT", "HawkesKT", "LPKT", "AKT", "simpleKT"]
LABEL = {"Best-LR-iter1000": "Best-LR (1,000 it.)", "Best-LR+": "Best-LR with time windows",
         "running-proportion": "running proportion"}
FAMILY = {"IRT": "S1", "PFA": "S1", "Best-LR": "S1", "Best-LR-iter1000": "S1", "Best-LR+": "S1",
          "BKT": "S2", "running-proportion": "S2", "DKT": "S3", "IEKT": "S3", "HawkesKT": "S3", "LPKT": "S3",
          "AKT": "S4", "simpleKT": "S4"}
CORPORA = [("kddcup2010-algebra0607:halfA", "half A"), ("kddcup2010-bridge06", "bridge06"), ("edmcup2023", "EDM Cup")]

# Values the article prints. Table 5: per model, (mean, lowest, highest) for half A, bridge06, EDM Cup in turn.
# Table 7: per "model / corpus", the change at 25%, 10%, 2%, first 50 and first 20 answers.
PRINTED_T5 = {
 "IRT": [
  "0.7261",
  "0.7198",
  "0.7371",
  "0.7438",
  "0.7392",
  "0.7477",
  "0.7438",
  "0.7402",
  "0.7478"
 ],
 "PFA": [
  "0.7514",
  "0.7478",
  "0.7563",
  "0.7569",
  "0.7546",
  "0.7593",
  "0.7327",
  "0.7283",
  "0.7365"
 ],
 "Best-LR": [
  "0.8053",
  "0.8022",
  "0.8086",
  "0.8040",
  "0.8014",
  "0.8052",
  "0.8211",
  "0.8173",
  "0.8244"
 ],
 "Best-LR-iter1000": [
  "0.8040",
  "0.8005",
  "0.8074",
  "0.8030",
  "0.8002",
  "0.8047",
  "0.8204",
  "0.8166",
  "0.8236"
 ],
 "Best-LR+": [
  "0.8122",
  "0.8092",
  "0.8163",
  "0.8090",
  "0.8069",
  "0.8103",
  "0.8287",
  "0.8256",
  "0.8325"
 ],
 "BKT": [
  "0.7520",
  "0.7485",
  "0.7554",
  "0.7534",
  "0.7501",
  "0.7555",
  "0.7254",
  "0.7215",
  "0.7295"
 ],
 "running-proportion": [
  "0.7306",
  "0.7258",
  "0.7373",
  "0.7356",
  "0.7330",
  "0.7374",
  "0.7288",
  "0.7250",
  "0.7326"
 ],
 "DKT": [
  "0.7920",
  "0.7880",
  "0.7981",
  "0.7966",
  "0.7937",
  "0.7992",
  "0.8291",
  "0.8260",
  "0.8327"
 ],
 "AKT": [
  "0.8148",
  "0.8111",
  "0.8207",
  "0.8149",
  "0.8133",
  "0.8165",
  "0.8381",
  "0.8354",
  "0.8423"
 ],
 "simpleKT": [
  "0.8128",
  "0.8092",
  "0.8166",
  "0.8148",
  "0.8122",
  "0.8165",
  "0.8364",
  "0.8336",
  "0.8405"
 ],
 "IEKT": [
  "0.8040",
  "0.7997",
  "0.8085",
  "0.8036",
  "0.8014",
  "0.8054",
  "0.8353",
  "0.8320",
  "0.8399"
 ],
 "HawkesKT": [
  "0.6999",
  "0.6910",
  "0.7075",
  "0.7559",
  "0.7535",
  "0.7582",
  "0.8035",
  "0.7997",
  "0.8074"
 ],
 "LPKT": [
  "0.8035",
  "0.7991",
  "0.8080",
  "0.8080",
  "0.8055",
  "0.8098"
 ]
}
PRINTED_T7 = {
 "IRT / half A": [
  "-0.036",
  "-0.069",
  "-0.144",
  "-0.151",
  "-0.182"
 ],
 "IRT / bridge06": [
  "-0.037",
  "-0.071",
  "-0.139",
  "-0.146",
  "-0.180"
 ],
 "IRT / EDM Cup": [
  "-0.014",
  "-0.034",
  "-0.096",
  "-0.029",
  "-0.060"
 ],
 "PFA / half A": [
  "-0.007",
  "-0.017",
  "-0.064",
  "-0.080",
  "-0.141"
 ],
 "PFA / bridge06": [
  "-0.005",
  "-0.013",
  "-0.063",
  "-0.099",
  "-0.126"
 ],
 "PFA / EDM Cup": [
  "-0.002",
  "-0.006",
  "-0.038",
  "-0.016",
  "-0.037"
 ],
 "Best-LR / half A": [
  "-0.017",
  "-0.034",
  "-0.089",
  "-0.113",
  "-0.171"
 ],
 "Best-LR / bridge06": [
  "-0.017",
  "-0.033",
  "-0.084",
  "-0.134",
  "-0.186"
 ],
 "Best-LR / EDM Cup": [
  "-0.010",
  "-0.025",
  "-0.071",
  "-0.029",
  "-0.066"
 ],
 "Best-LR-iter1000 / half A": [
  "-0.015",
  "-0.033",
  "-0.088",
  "-0.111",
  "-0.170"
 ],
 "Best-LR-iter1000 / bridge06": [
  "-0.017",
  "-0.032",
  "-0.083",
  "-0.133",
  "-0.185"
 ],
 "Best-LR-iter1000 / EDM Cup": [
  "-0.010",
  "-0.024",
  "-0.070",
  "-0.028",
  "-0.065"
 ],
 "Best-LR+ / half A": [
  "-0.018",
  "-0.037",
  "-0.100",
  "-0.132",
  "-0.171"
 ],
 "Best-LR+ / bridge06": [
  "-0.018",
  "-0.036",
  "-0.095",
  "-0.136",
  "-0.173"
 ],
 "Best-LR+ / EDM Cup": [
  "-0.011",
  "-0.026",
  "-0.077",
  "-0.027",
  "-0.065"
 ],
 "BKT / half A": [
  "-0.010",
  "-0.023",
  "-0.039",
  "-0.035",
  "-0.047"
 ],
 "BKT / bridge06": [
  "-0.009",
  "-0.020",
  "-0.057",
  "-0.051",
  "-0.059"
 ],
 "BKT / EDM Cup": [
  "-0.002",
  "-0.008",
  "-0.030",
  "-0.009",
  "-0.017"
 ],
 "running-proportion / half A": [
  "0.000",
  "0.000",
  "0.000",
  "0.000",
  "0.000"
 ],
 "running-proportion / bridge06": [
  "0.000",
  "0.000",
  "0.000",
  "0.000",
  "0.000"
 ],
 "running-proportion / EDM Cup": [
  "0.000",
  "0.000",
  "0.000",
  "0.000",
  "0.000"
 ],
 "DKT / half A": [
  "-0.042",
  "-0.072",
  "-0.167",
  "-0.132",
  "-0.158"
 ],
 "DKT / bridge06": [
  "-0.038",
  "-0.074",
  "-0.166",
  "-0.135",
  "-0.160"
 ],
 "DKT / EDM Cup": [
  "-0.030",
  "-0.055",
  "-0.089",
  "-0.027",
  "-0.051"
 ],
 "AKT / half A": [
  "-0.026",
  "-0.050",
  "-0.093",
  "-0.091",
  "-0.110"
 ],
 "AKT / bridge06": [
  "-0.024",
  "-0.048",
  "-0.093",
  "-0.088",
  "-0.114"
 ],
 "AKT / EDM Cup": [
  "-0.015",
  "-0.042",
  "-0.079",
  "-0.025",
  "-0.051"
 ],
 "simpleKT / half A": [
  "-0.027",
  "-0.047",
  "-0.083",
  "-0.089",
  "-0.106"
 ],
 "simpleKT / bridge06": [
  "-0.021",
  "-0.046",
  "-0.095",
  "-0.087",
  "-0.107"
 ],
 "simpleKT / EDM Cup": [
  "-0.017",
  "-0.047",
  "-0.080",
  "-0.040",
  "-0.067"
 ],
 "IEKT / half A": [
  "-0.038",
  "-0.067",
  "-0.148",
  "-0.117",
  "-0.148"
 ],
 "IEKT / bridge06": [
  "-0.029",
  "-0.055",
  "-0.138",
  "-0.116",
  "-0.156"
 ],
 "IEKT / EDM Cup": [
  "-0.014",
  "-0.030",
  "-0.067",
  "-0.023",
  "-0.051"
 ],
 "HawkesKT / half A": [
  "-0.006",
  "-0.018",
  "-0.085",
  "-0.046",
  "-0.046"
 ],
 "HawkesKT / bridge06": [
  "-0.112",
  "-0.135",
  "-0.187",
  "-0.159",
  "-0.154"
 ],
 "HawkesKT / EDM Cup": [
  "-0.031",
  "-0.050",
  "-0.136",
  "-0.035",
  "-0.065"
 ],
 "LPKT / half A": [
  "-0.168",
  "-0.175",
  "-0.179",
  "-0.192",
  "-0.205"
 ],
 "LPKT / bridge06": [
  "-0.023",
  "-0.058",
  "-0.184",
  "-0.197",
  "-0.202"
 ]
}


def check(t: dict) -> None:
    bad = []
    for m, want in PRINTED_T5.items():
        got = []
        for c, _ in CORPORA:
            r = t["main"][m].get(c)
            if r:
                got += [f"{r['auc_mean']:.4f}", f"{r['auc_min']:.4f}", f"{r['auc_max']:.4f}"]
        if got != want:
            bad.append(("Table 5", m, got, want))
    short = {s: c for c, s in CORPORA}
    for key, want in PRINTED_T7.items():
        m, s = key.split(" / ")
        rg = t["regimes"][m][short[s]]
        got = []
        for g in ("quarter", "tenth", "fiftieth", "history-fifty", "history-twenty"):
            x = rg[g]["minus_main"]
            got.append("0.000" if abs(x) < 5e-4 and m == "running-proportion" else f"{x:+.3f}")
        if got != want:
            bad.append(("Table 7", key, got, want))
    if bad:
        for b in bad:
            print("MISMATCH", *b)
        sys.exit("a printed value does not match its source: fix the article")
    print(f"printed values match: Table 5 ({len(PRINTED_T5)} models), Table 7 ({len(PRINTED_T7)} rows)")


def color(m):
    return getattr(figstyle, FAMILY[m])


def counted(t, m, c, regime="main"):
    st = t["status"][m][c]
    if st["status"] == "REFERENCE (exempt)":
        return True
    if regime == "fiftieth":
        return st["f1_2"] == "PASS" and st["status"] == "PASS"
    return st["status"] in ("PASS", "REFERENCE (exempt)")


def fig1(t, plt):
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 3.6), sharey=True)
    ys = {m: i for i, m in enumerate(reversed(ORDER))}
    for ax, (c, name) in zip(axes, CORPORA):
        for m in ORDER:
            r = t["main"][m].get(c)
            if not r:
                continue
            y, col = ys[m], color(m)
            ax.plot([r["auc_min"], r["auc_max"]], [y, y], color=col, lw=1.2, solid_capstyle="butt")
            full = counted(t, m, c)
            ax.plot(r["auc_mean"], y, "o", ms=4.5, mec=col, mfc=col if full else figstyle.SURF, mew=1.1)
        ax.set_title(name)
        ax.set_xlim(0.68, 0.85)
        ax.grid(axis="x", color=figstyle.GRID, lw=0.5)
        ax.set_xlabel("test AUC")
    axes[0].set_yticks(list(ys.values()))
    axes[0].set_yticklabels([LABEL.get(m, m) for m in ys])
    fig.tight_layout()
    return fig


def fig2(t, plt):
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 3.6), sharey=True)
    ys = {m: i for i, m in enumerate(reversed(ORDER))}
    for ax, (c, name) in zip(axes, CORPORA):
        ax.axvline(0, color=figstyle.AXIS, lw=0.6)
        for m in ORDER:
            rg = t["regimes"][m].get(c)
            if not rg:
                continue
            y, col = ys[m], color(m)
            for g, mk, dy in (("fiftieth", "o", 0.15), ("history-twenty", "s", -0.15)):
                full = counted(t, m, c, g)
                ax.plot(rg[g]["minus_main"], y + dy, mk, ms=4, mec=col, mfc=col if full else figstyle.SURF, mew=1.0)
        ax.set_title(name)
        ax.set_xlim(-0.22, 0.01)
        ax.grid(axis="x", color=figstyle.GRID, lw=0.5)
        ax.set_xlabel("change in test AUC")
    axes[0].set_yticks(list(ys.values()))
    axes[0].set_yticklabels([LABEL.get(m, m) for m in ys])
    h = [plt.Line2D([], [], ls="", marker="o", ms=4, mec=figstyle.INK2, mfc=figstyle.INK2, label="2% of training learners"),
         plt.Line2D([], [], ls="", marker="s", ms=4, mec=figstyle.INK2, mfc=figstyle.INK2, label="first 20 answers")]
    fig.legend(handles=h, loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.01))
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    return fig


def main() -> None:
    t = json.loads(TABLES.read_text())
    check(t)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    figstyle.apply()
    plt.rcParams["svg.hashsalt"] = "knowledge-tracing-benchmark-2026"
    plt.rcParams["svg.fonttype"] = "none"
    OUT.mkdir(parents=True, exist_ok=True)
    for stem, f in (("fig1-main-auc", fig1), ("fig2-thinning", fig2)):
        fig = f(t, plt)
        fig.savefig(OUT / f"{stem}.png", dpi=200, metadata={"Software": None})
        fig.savefig(OUT / f"{stem}.svg", metadata={"Date": None, "Creator": None})
        plt.close(fig)
        print("wrote", OUT / f"{stem}.png")


if __name__ == "__main__":
    main()
