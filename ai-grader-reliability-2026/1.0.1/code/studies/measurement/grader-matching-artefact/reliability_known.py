"""
Reading the registered H15 grid at the human score's now-known reliability (amendment 3; no re-run).

RESULT (2026-10-06). rho = 0.75 (one rater, lower bound) / 0.857 (two-read Spearman-Brown, best estimate):
  corrected gap at equal true score, Qwen / GPT-4.1-mini
    ell         -0.173 / -0.149  ->  -0.210 / -0.179   PARTLY-ARTEFACT at 0.75, NOT-ARTEFACT at 0.857
    disability  -0.217 / -0.212  ->  -0.268 / -0.253   PARTLY-ARTEFACT at 0.75, NOT-ARTEFACT at 0.857
    economic    -0.120 / -0.095  ->  -0.147 / -0.117   NOT-ARTEFACT at both
  artefact share 27-32% at 0.75, 13-16% at 0.857; break-even 0.49-0.52 is excluded by r = .75.
  Integer-composite sensitivity rho 0.805: disability PARTLY-ARTEFACT, ell and economic NOT-ARTEFACT.
  Label-by-group corrected z (0.75 / 0.857): Qwen D_low ell 2.24 / 2.73, disability 3.01 / 3.62; GPT
  D_low economic 2.53 / 2.61; Qwen D_lowmid ell -2.63 / -2.98, disability -1.72 / -2.17, economic
  -2.49 / -2.72 (Bonferroni bar 2.576). The triad bound 0.30-0.37 sits far below 0.75 because the two
  LLMs correlate 0.76 against ~0.33-0.38 for independent errors: shared non-human-score variance.
  Of the 3,000-essay draw, 278 are identifiably PERSUADE 2.0 (numeric ids); 2,722 cannot be attributed;
  both subsets report r = .750, so rho does not depend on the subset.

WHAT IS ASKED. artefact.py corrected the grader's no-label group gap on ASAP 2.0 for matching on a
noisy human score, and because the data paper could not be read it reported every verdict at fixed
reliabilities rho in a pre-registered grid (0.60-0.95). The maintainer has since supplied the paper:
Crossley, Baffour, Burleigh & King (2025), Assessing Writing 65, 100954, doi:10.1016/j.asw.2025.100954,
section 3, p. 3 -- double-blind expert rating followed by 100 percent adjudication; inter-rater
reliability before adjudication weighted kappa .745, r .750 (PERSUADE 2.0 subset, ~13,000 essays)
and weighted kappa .659, r .750 (~12,000 new essays). What do the registered verdicts say at the
reliability those figures imply?

THE RELIABILITY OF THE RELEASED SCORE.
  One rater. For parallel raters the inter-rater correlation is each rating's reliability: 0.750.
  Both subsets report the same r, so the subsets do not need to be read separately for rho.
  Two reads. The released score is a composite of two reads plus adjudication. If it is at least as
  good as the mean of two parallel ratings, its reliability is Spearman-Brown 2(.75)/(1 + .75) =
  0.857. It cannot be below one rating's 0.75 unless adjudication adds error, so 0.75 is the lower
  bound and 0.857 the best estimate. Both are read here.
  Why kappa and r differ. Quadratic-weighted kappa is 2 cov / (var1 + var2 + (m1 - m2)^2), so it falls
  below r when the two rating slots differ in mean or spread; r ignores both. kappa .659 against r .750
  on the new essays says their two reads differ systematically in level or scale (with equal spreads,
  a mean gap of about half a standard deviation). A difference that is the same for every essay does not
  reorder essays, and the correction here calibrates the grader's mean on the analysed essays, so the
  classical-test-theory quantity is the correlation. Rater leniency that varies from essay to essay
  lowers r as well, so it is already counted.
  The integer caveat (SENSITIVITY, not a verdict). The paper calls the released column "the average
  human assigned score", but the file holds integers 1-6 with no half points, so it is not the raw mean
  of two reads. A synthetic check (`integer_composites`) uses a normal true score and two integer
  raters tuned to r = .750 on the corpus's spread. It gives the reliability of integer composites:
  the raw mean, the mean rounded half up, the mean rounded at random, and a third read on
  disagreement. The registered grid is also read at the round-half-up value, labelled as a
  sensitivity. The check is a model with no data in it; adjudication by a senior reader that is better
  than any one rater would sit above it.

THE READING (amendment 3, committed at 454f28a before any number here was written into the README).
  At rho = 0.75, a grid point: the committed point estimate, 95% fixed-rho bootstrap interval and
  verdict from out/results.json.
  At rho = 0.857 and at the sensitivity value: linear interpolation of the committed neighbours'
  point estimates and interval endpoints. 0.857 lies between 0.85 and 0.90. The verdict is
  artefact.verdict() on the interpolated interval, which equals the neighbours' verdict when they
  agree: the rule is linear inequalities on the endpoints, and a convex combination preserves them.
  The interpolation error is bounded by the grid's own curvature, reported as `interp_check`: the
  committed value at each interior grid point against the interpolation of its two neighbours.
  Label-by-group (item 5): the implied matching bias of each within-essay contrast is evaluated exactly
  at each rho with the committed analytic formula, (slope / rho_w)(1 - rho_w)(mu_f - mu_r), from the
  committed slopes (out/label-check.json) and corpus model (out/results.json). The script asserts that
  it reproduces the committed values at 0.65, 0.75 and 0.90. Corrected z = (measured - bias) / sd, with
  sd the bootstrap SD from grader-attainment-groups/out/results.json, which is the denominator its
  binary_verdict uses. That rule's label (Bonferroni z* 2.576) is applied to the corrected value
  post hoc, as in the README's item 5; the registered verdicts of grader-attainment-groups are not
  re-cut.
  Subset check (`--subsets`, optional). It reads the corpus's essay_id, prompt_name and blank
  economic/disability fields ($ASAP2_DIR, data/data-sources.json `asap2`), plus the two
  grader-attainment-groups dumps' essay ids (--dumps, session scratchpad). It counts the draw's
  essays that are identifiably PERSUADE 2.0. Only counts are written.

DATA. No model call. With --subsets it reads the ASAP 2.0 corpus (CC BY 4.0; the raw file stays in the
scratchpad). Otherwise it reads only committed outputs. It writes out/reliability-known.json.

    python3 reliability_known.py [--subsets --dumps run-qwen.json run-gpt41mini.json]
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OUT = HERE / "out"
sys.path.insert(0, str(REPO))

_spec = importlib.util.spec_from_file_location("artefact", HERE / "artefact.py")
ART = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ART)

R_INTER = 0.750                                   # both subsets, p. 3
KAPPA = {"persuade_2_0": 0.745, "new_essays": 0.659}
RHO_LOW = 0.75
RHO_SB = 2 * R_INTER / (1 + R_INTER)             # 0.857142...
AXES = ("ell", "disability", "economic", "gender")
CONTRASTS = ("D_low", "D_lowmid", "D_high", "D_spread")


def kappa_gap():
    """With equal spreads s, QWK = r s^2 / (s^2 + dm^2 / 2), so dm / s = sqrt(2 (r / kappa - 1))."""
    return {k: {"kappa": v, "r": R_INTER, "kappa_over_r": v / R_INTER,
                "implied_mean_gap_sd_if_equal_spread": float(np.sqrt(2 * (R_INTER / v - 1)))}
            for k, v in KAPPA.items()}


def integer_composites(sd_rating: float, n: int = 400_000, seed: int = 20261006) -> dict:
    """SENSITIVITY: reliability of integer composites of two integer raters whose r is 0.750."""
    rng = np.random.default_rng(seed)
    mu = 2.93

    def rate(T, sde):
        return np.clip(np.rint(T + rng.normal(0, sde, T.shape)), 1, 6)

    def world(sde, sdt):
        T = rng.normal(mu, sdt, n)
        r = [rate(T, sde) for _ in range(6)]
        c = lambda a, b: float(np.corrcoef(a, b)[0, 1])
        m1, m2 = (r[0] + r[1]) / 2, (r[2] + r[3]) / 2
        u = rng.random((2, n)) < 0.5
        return {"single": c(r[0], r[1]), "mean_of_two": c(m1, m2),
                "mean_round_half_up": c(np.floor(m1 + 0.5), np.floor(m2 + 0.5)),
                "mean_round_random": c(np.where(u[0], np.floor(m1), np.ceil(m1)),
                                       np.where(u[1], np.floor(m2), np.ceil(m2))),
                "third_read_on_disagreement": c(np.where(r[0] == r[1], r[0], r[4]),
                                                np.where(r[2] == r[3], r[2], r[5])),
                "exact_agreement": float(np.mean(r[0] == r[1])), "sd_rating": float(r[0].std())}

    # total spread fixed near the corpus's; bisect the error sd so one rater's r is 0.750
    lo, hi = 0.2, 0.8
    for _ in range(18):
        sde = (lo + hi) / 2
        sdt = float(np.sqrt(max(sd_rating ** 2 - sde ** 2 - 1 / 12, 0.05)))
        w = world(sde, sdt)
        if w["single"] > R_INTER:
            lo = sde
        else:
            hi = sde
    w["error_sd"], w["true_sd"] = sde, sdt
    w["spearman_brown_of_single"] = 2 * w["single"] / (1 + w["single"])
    return w


def interp(by: dict, rho: float, key):
    pts = sorted(float(r) for r in by)
    lo = max(p for p in pts if p <= rho + 1e-12)
    hi = min(p for p in pts if p >= rho - 1e-12)
    f = lambda p: np.asarray(key(by[str(p) if str(p) in by else f"{p:.2f}"]), dtype=float)
    if hi == lo:
        return f(lo), (lo, hi)
    t = (rho - lo) / (hi - lo)
    return (1 - t) * f(lo) + t * f(hi), (lo, hi)


def read_axis(a: dict, rho: float) -> dict:
    by = {k: v for k, v in a["by_rho"].items()}
    G = a["G_obs"]
    C, nb = interp(by, rho, lambda b: b["C"])
    A, _ = interp(by, rho, lambda b: b["A"])
    ci, _ = interp(by, rho, lambda b: b["C_ci"])
    out = {"rho": rho, "neighbours": list(nb), "interpolated": nb[0] != nb[1], "A": float(A), "C": float(C),
           "C_ci": [float(ci[0]), float(ci[1])], "share_artefact": float(A / G),
           "verdict": ART.verdict(G, float(ci[0]), float(ci[1])),
           "neighbour_verdicts": [by[f"{p:.2f}" if f"{p:.2f}" in by else str(p)]["verdict"] for p in nb]}
    for meth in ("kelley_reg", "eiv"):
        mci, _ = interp(by, rho, lambda b: b[f"{meth}_ci"])
        out[f"verdict_{meth}"] = ART.verdict(G, float(mci[0]), float(mci[1]))
    return out


def interp_check(by: dict) -> float:
    """Largest gap between a committed interior grid C and the linear interpolation of its neighbours."""
    rs = sorted(float(r) for r in by)
    key = lambda p: by[f"{p:.2f}" if f"{p:.2f}" in by else str(p)]["C"]
    return float(max(abs(key(rs[i]) - (key(rs[i - 1]) + key(rs[i + 1])) / 2) for i in range(1, len(rs) - 1)))


def label_bias(slope, rho, cm, ax):
    rw = 1 - (1 - rho) * cm["var_H"] / cm["s_w2"]
    dmu = cm["group_means"][ax][0] - cm["group_means"][ax][1]
    return slope / rw * (1 - rw) * dmu


def subsets(dumps: list[Path]) -> dict:
    from shared.paths import data_path
    p = data_path("ASAP2_DIR") / "ASAP2_train_sourcetexts.csv"
    csv.field_size_limit(10 ** 9)
    numeric, n, num_blank, by_prompt = set(), 0, 0, {}
    with open(p, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            n += 1
            eid = row["essay_id"]
            if eid.split("_")[0].isdigit():
                numeric.add(eid)
                num_blank += (row["economically_disadvantaged"] in ("", "NA") and row["student_disability_status"] in ("", "NA"))
                by_prompt[row["prompt_name"]] = by_prompt.get(row["prompt_name"], 0) + 1
    out = {"corpus_rows": n, "numeric_id_rows": len(numeric), "numeric_id_with_blank_economic_and_disability": num_blank,
           "numeric_id_prompts": by_prompt, "paper_persuade_without_economic_disability": 4005,
           "paper_persuade_total": 12871, "paper_new_total": 11829, "draw": {}}
    for d in dumps:
        dd = json.loads(Path(d).read_text())
        rows = next(v for v in dd.values() if isinstance(v, list) and len(v) > 100 and isinstance(v[0], dict))
        ids = [r["id"] for r in rows]
        k = sum(i in numeric for i in ids)
        out["draw"][Path(d).name] = {"n": len(ids), "identifiably_persuade": k, "unattributable": len(ids) - k}
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subsets", action="store_true")
    ap.add_argument("--dumps", type=Path, nargs="*", default=[])
    a = ap.parse_args()
    res = json.loads((OUT / "results.json").read_text())
    lab = json.loads((OUT / "label-check.json").read_text())
    prev = json.loads((REPO / "studies/measurement/grader-attainment-groups/out/results.json").read_text())
    cm = res["corpus_model"]

    comp = integer_composites(float(np.sqrt(cm["var_H"])))
    rho_sens = round(comp["mean_round_half_up"], 3)
    rhos = {"lower_bound_one_rater": RHO_LOW, "best_estimate_spearman_brown": RHO_SB,
            "sensitivity_integer_round_half_up": rho_sens}

    out = {"source": "Crossley, Baffour, Burleigh & King (2025), Assessing Writing 65, 100954, section 3, p. 3",
           "rhos": rhos, "kappa_vs_r": kappa_gap(), "integer_composites_sensitivity": comp, "per_model": {},
           "across": {}, "label_by_group": {}}
    for model, m in res["per_model"].items():
        rec = {}
        for ax in AXES:
            ax_rec = m["axes"][ax]
            rec[ax] = {"G_obs": ax_rec["G_obs"], "registered_verdict": ax_rec["verdict"],
                       "interp_check_max": interp_check(ax_rec["by_rho"]),
                       # linear interpolation over one 0.05 step at fraction t errs by t(1 - t) times the
                       # midpoint-over-two-steps error that interp_check measures (same curvature)
                       "interp_error_bound_best": interp_check(ax_rec["by_rho"]) * ((RHO_SB - 0.85) / 0.05)
                       * (1 - (RHO_SB - 0.85) / 0.05),
                       **{name: read_axis(ax_rec, r) for name, r in rhos.items()}}
        out["per_model"][model] = rec
    for ax in AXES:
        out["across"][ax] = {}
        for name in rhos:
            vs = [out["per_model"][mm][ax][name]["verdict"] for mm in res["per_model"]]
            out["across"][ax][name] = vs[0] if len(set(vs)) == 1 else " / ".join(vs)

    for model, cs in lab["post_hoc_contrast_slopes"].items():
        lrec = {}
        for cname, c in cs.items():
            for ax, v in c["by_axis"].items():
                for r0, b0 in v["implied_bias"].items():      # reproduce the committed analytic values
                    assert abs(label_bias(c["slope_on_H"], float(r0), cm, ax) - b0) < 1e-9, (model, cname, ax, r0)
                meas = prev["per_model"][model]["axes"][cname][ax]
                sd = meas["sd"]          # the bootstrap SD the registered binary_verdict divides by
                rr = {}
                for name, r in rhos.items():
                    b = label_bias(c["slope_on_H"], r, cm, ax)
                    rr[name] = {"rho": r, "bias": b, "corrected": meas["diff"] - b, "z_corrected": (meas["diff"] - b) / sd,
                                "rule_label": ART.AG.binary_verdict(meas["diff"] - b, sd, meas["coverage"])}
                lrec.setdefault(cname, {})[ax] = {"measured": meas["diff"], "sd": sd, "z_measured": meas["diff"] / sd,
                                                  "measured_verdict": meas["verdict"], **rr}
        out["label_by_group"][model] = lrec

    if a.subsets:
        out["subsets"] = subsets(a.dumps)
    (OUT / "reliability-known.json").write_text(json.dumps(out, indent=1, default=float))

    print(f"rho: one rater {RHO_LOW}, Spearman-Brown {RHO_SB:.4f}, integer round-half-up sensitivity {rho_sens}")
    print("integer composites:", {k: round(v, 3) for k, v in comp.items()})
    for model, rec in out["per_model"].items():
        for ax, r in rec.items():
            s = " | ".join(f"{name.split('_')[0]} {r[name]['rho']:.3f}: A {r[name]['A']:+.3f} C {r[name]['C']:+.3f} "
                           f"[{r[name]['C_ci'][0]:+.3f}, {r[name]['C_ci'][1]:+.3f}] {r[name]['verdict']}"
                           for name in rhos)
            print(f"{model.split(':')[1][:14]:14s} {ax:10s} G {r['G_obs']:+.3f} | {s} | interp<= {r['interp_check_max']:.4f}")
    print(json.dumps(out["across"], indent=1))
    for model, lrec in out["label_by_group"].items():
        for cname in ("D_low", "D_lowmid"):
            for ax, v in lrec.get(cname, {}).items():
                print(f"{model.split(':')[1][:14]:14s} {cname:8s} {ax:10s} {v['measured']:+.3f} z {v['z_measured']:+.2f} -> "
                      + " / ".join(f"{v[n]['z_corrected']:+.2f} {v[n]['rule_label']}" for n in rhos))
    if a.subsets:
        print(json.dumps(out["subsets"], indent=1))


if __name__ == "__main__":
    main()
