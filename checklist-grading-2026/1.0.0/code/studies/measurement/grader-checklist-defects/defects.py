"""
Which checks move when a checklist meets a planted defect, and where on the human scale a checklist
grader parts from a Likert one (2026-10-28). A follow-up to studies/measurement/grader-boolean-rubrics/.

WHAT WAS ASKED. The parent study found that a model-written yes/no checklist loses 0.17 of its scale to
an appended false sentence where a Likert score loses 0.47 (CHECKLIST-BLIND-TO-CONTRADICTION), and gains
more from a key-terms sentence (CHECKLIST-REWARDS-STUFFING). A post hoc split, made after reading the
checklists, put checklists that carry an "avoid ..." check at -0.22 and those without at -0.08. That
split is observational: which questions got avoid checks was not assigned. The release's literature
review (research/readiness/checklist-grading-2026/literature.md, analyses 1 and 4) proposed turning the
score gap into a mechanism from the per-check answers already recorded. The maintainer chose this one
(2026-10-28). No model is called.

THE DATA. Only the published per-case file of release checklist-grading-2026
(research/wiki/research/releases/checklist-grading-2026/per-case-model-outputs.jsonl), written by the
parent's `boolean.py --strip`: each Mohler item's human scores, draw and perturbation flags; each
question's checklist length and, per check, whether it is an avoid check (AVOID_PATTERN of the parent,
`\\bavoid`) or a generic no-error check (the parent's pre-registered NO_ERROR_PATTERN); every grading's
score and per-check YES/NO. The corpora (Mohler ASAG, CC BY 4.0) are not read.

UNITS. An answer's checks are answered by each model twice per form (treated, neutral). For check j of
answer i under model m, y = mean over the two reps of YES (0, 0.5 or 1). The change is
d_ij = y(treated) - y(neutral). The checklist score is the mean over the question's n checks, so the
answer's checklist change is D_i = (1/n) sum_j d_ij, and it splits exactly into an avoid-check part
A_i = (1/n) sum_{j avoid} d_ij and a presence part P_i = (1/n) sum_{j not avoid} d_ij. Every estimate is
pooled over the two models (their mean on the same resample), signed, on the 0-1 scale, with a 95%
cluster bootstrap over questions (4,000 replicates, multinomial weights). The primary sets are the
parent's manipulation-pass sets: 120 CONTRA answers, 112 STUFF answers.

ESTIMANDS AND PRE-REGISTERED VERDICTS (written before this script read any grade).

  E1 Contradiction, all 120 answers: A and P (means of A_i, P_i).
     PRESENCE-CHECKS-REGISTER-CONTRADICTION   P's 95% interval lies below 0;
     PRESENCE-CHECKS-BLIND                    P's 90% interval inside +/-0.02;
     PRESENCE-UNRESOLVED                      otherwise.
  E2 Contradiction, the answers whose checklist has >= 1 avoid check: the avoid share of the loss,
     S = mean(A_i) / mean(D_i).
     AVOID-CHECKS-CARRY-THE-LOSS     S's 95% interval lies above 0.5;
     PRESENCE-CHECKS-CARRY-THE-LOSS  S's 95% interval lies below 0.5;
     SHARED                          otherwise.
     And the within-answer counterfactual: the same answers re-scored on their presence checks only,
     D_pres_i = mean over presence checks of d_ij, against D_i. K = mean(D_pres_i) - mean(D_i).
     AVOID-CHECKS-ADD-SENSITIVITY    K's 95% interval lies above 0 (dropping them blunts the score);
     AVOID-CHECKS-ADD-NOTHING        K's 90% interval inside +/-0.02;
     UNRESOLVED                      otherwise.
  E3 Key-term stuffing, 112 answers: A and P as in E1.
     PRESENCE-CHECKS-REWARD-KEY-TERMS P's 95% interval lies above 0;
     PRESENCE-CHECKS-UNMOVED          P's 90% interval inside +/-0.02;
     PRESENCE-UNRESOLVED              otherwise.
     And the avoid part: AVOID-CHECKS-PENALIZE-STUFFING if A's 95% interval lies below 0.
  E4 Where the formats part, the parent's 620-answer main draw (no perturbation): the signed error
     e = score - human/5 per format (score = mean of the two reps, pooled over models), by band of the
     human mean: LOW h <= 2.5, MID 2.5 < h < 4.5, HIGH h >= 4.5. Per band, G = mean(e_checklist) -
     mean(e_likert):
       CHECKLIST-HIGHER   G's 95% interval above 0 (the checklist credits that band more);
       CHECKLIST-LOWER    below 0;
       UNRESOLVED         otherwise.
     Mean signed error per format per band is reported beside it.
  Noise floor (descriptive). Per check, the rep-to-rep disagreement rate on the neutral form, and the
  rate at which a check's two-rep majority changes between neutral and treated forms, by check type.
  A change rate inside the rep disagreement rate is not read as evidence.

PREDICTIONS (not verdicts): E1 PRESENCE-CHECKS-REGISTER-CONTRADICTION, small (presence checks such as
"states the elements are processed left to right" can be contradicted directly); E2 SHARED or
AVOID-CHECKS-CARRY-THE-LOSS, and AVOID-CHECKS-ADD-SENSITIVITY; E3 PRESENCE-CHECKS-REWARD-KEY-TERMS; E4
CHECKLIST-HIGHER in LOW (presence credit for wrong answers) and CHECKLIST-LOWER in HIGH (terse correct
answers miss enumerated checks; Hodges et al. 1999).

THE FLOOR (--floor), before any grade is read for an estimate. It reads only the checklist lengths and
check types, the draws and the human scores; the synthetic checks are drawn, not taken from the run.
Each synthetic answer has a neutral YES rate per check of 0.8 (CONTRA, good answers) or 0.4 (STUFF,
weak answers), rep noise flipping each answer with probability 0.06 (a guess, held fixed), and a
planted change per check type. 200 replicates per world:
  C-PRES   presence checks flip YES->NO w.p. 0.12, avoid w.p. 0: E1 REGISTER >= 80%, and E2
           PRESENCE-CARRY >= 80%.
  C-NULL   no planted change: E1 REGISTER <= 10%, E2 ADD-SENSITIVITY <= 10%.
  C-AVOID  avoid checks flip YES->NO w.p. 0.7, presence w.p. 0.03: E2 AVOID-CARRY >= 80%,
           ADD-SENSITIVITY >= 80%.
  S-PRES   presence checks flip NO->YES w.p. 0.15: E3 REWARD >= 80%; S-NULL: <= 10%.
  B-LOW    the main draw: Likert e ~ N(0, 0.15) per answer; checklist e the same plus +0.06 in LOW:
           E4 CHECKLIST-HIGHER in LOW >= 80%, and a signed verdict in MID or HIGH <= 10%.
  B-NULL   no difference: a signed verdict in any band <= 10% each.
A world that misses its bar makes its verdict unreachable: reported as an interval only. The floor is a
smoke check of this script's logic, written and scored by the same session.

FLOOR RECORD: REVISION 0 PASSED, BEFORE ANY ESTIMATE (out/floor.json; 200 replicates per world).
C-PRES: E1 REGISTER 100%, E2 PRESENCE-CARRY 99%. C-NULL: E1 REGISTER 1%, E2 ADD-SENSITIVITY 4.5%.
C-AVOID: AVOID-CARRY 100%, ADD-SENSITIVITY 100%. S-PRES REWARD 100%; S-NULL 2.5%. B-LOW: LOW HIGHER
100%, MID signed 2%, HIGH signed 6%. B-NULL signed LOW 7%, MID 6%, HIGH 3%.

    python3 defects.py --floor     synthetic worlds -> out/floor.json
    python3 defects.py             -> out/results.json
    --cases PATH                   the per-case file (default: the release's)
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from shared.seeds import stable_hash  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
CASES = REPO / "research/wiki/research/releases/checklist-grading-2026/per-case-model-outputs.jsonl"
SEED = 20261029
BOOT = 4000
MODELS = ("gemini", "gpt")
REPS = (0, 1)
MARGIN = 0.02
BANDS = (("LOW", lambda h: h <= 2.5), ("MID", lambda h: 2.5 < h < 4.5), ("HIGH", lambda h: h >= 4.5))


def load(path: Path) -> dict:
    C = dict(items={}, q={}, grades={})
    for ln in open(path, encoding="utf-8"):
        r = json.loads(ln)
        if r["record"] == "question" and r["corpus"] == "mohler":
            C["q"][r["q"]] = r
        elif r["record"] == "item" and r["corpus"] == "mohler":
            C["items"][r["id"]] = r
        elif r["record"] == "grade" and r["corpus"] == "mohler":
            C["grades"][(r["id"], r["form"], r["model"], r["arm"], r["rep"])] = r
    return C


def weights(groups, rng, B=BOOT):
    _, g = np.unique(groups, return_inverse=True)
    G = g.max() + 1
    cw = rng.multinomial(G, np.full(G, 1 / G), size=B).astype(float)
    return np.vstack([np.ones(len(g)), cw[:, g]])


def wmean(W, x):
    return W @ x / W.sum(1)


def summ(v):
    b = v[1:][~np.isnan(v[1:])]
    p = lambda q: float(np.percentile(b, q))
    return dict(est=float(v[0]), ci95=[p(2.5), p(97.5)], ci90=[p(5), p(95)])


def below(s, x=0.0):
    return s["ci95"][1] < x


def above(s, x=0.0):
    return s["ci95"][0] > x


def inside(s, m=MARGIN):
    return -m < s["ci90"][0] and s["ci90"][1] < m


# ---------------------------------------------------------------- per-answer decompositions

def decompose(dY: np.ndarray, avoid: np.ndarray) -> tuple[float, float, float, float]:
    """dY: per-check change (treated - neutral) for one answer and model. Returns D, A, P, D_pres."""
    n = len(dY)
    A = dY[avoid].sum() / n
    P = dY[~avoid].sum() / n
    D_pres = dY[~avoid].mean() if (~avoid).any() else np.nan
    return A + P, A, P, D_pres


def defect_arrays(C: dict, kind: str):
    """Per answer (pooled over models): D, A, P, D_pres, has_avoid, question; plus noise stats."""
    ids = sorted((i for i, it in C["items"].items() if kind in it and it[kind]["ok"] and it[kind]["manip_pass"]),
                 key=lambda i: stable_hash((SEED, "p", i)))
    rows, noise = [], defaultdict(list)
    for i in ids:
        it = C["items"][i]
        qf = C["q"][it["q"]]
        avoid = np.array(qf["avoid_by_check"], bool)
        per_m = []
        for m in MODELS:
            ys = {}
            for f in ("treat", "neutral"):
                reps = [C["grades"][(i, f"{kind}-{f}", m, "boolean", k)]["checks"] for k in REPS]
                if any(r is None for r in reps):
                    break
                ys[f] = np.array(reps, float)
            else:
                dY = ys["treat"].mean(0) - ys["neutral"].mean(0)
                per_m.append(decompose(dY, avoid))
                # noise: rep disagreement on the neutral form; majority change between forms
                for t, lab in ((avoid, "avoid"), (~avoid, "presence")):
                    if t.any():
                        noise[f"rep_disagree_neutral.{lab}"] += list((ys["neutral"][0] != ys["neutral"][1])[t])
                        maj_n = ys["neutral"].mean(0) >= 0.5
                        maj_t = ys["treat"].mean(0) >= 0.5
                        noise[f"majority_change.{lab}"] += list((maj_n != maj_t)[t])
                        noise[f"yes_to_no.{lab}"] += list((maj_n & ~maj_t)[t])
                        noise[f"no_to_yes.{lab}"] += list((~maj_n & maj_t)[t])
        if len(per_m) != len(MODELS):
            continue
        a = np.array(per_m)
        rows.append(dict(id=i, q=it["q"], has_avoid=bool(avoid.any()), D=a[:, 0].mean(), A=a[:, 1].mean(),
                         P=a[:, 2].mean(), D_pres=np.nanmean(a[:, 3]) if not np.isnan(a[:, 3]).all() else np.nan,
                         **{f"D.{m}": a[j, 0] for j, m in enumerate(MODELS)},
                         **{f"A.{m}": a[j, 1] for j, m in enumerate(MODELS)},
                         **{f"P.{m}": a[j, 2] for j, m in enumerate(MODELS)}))
    return rows, {k: dict(rate=float(np.mean(v)), n=len(v)) for k, v in sorted(noise.items())}


def defect_estimates(rows, rng, kind):
    q = np.array([r["q"] for r in rows])
    W = weights(q, rng)
    col = lambda k, mask=None: np.array([r[k] for r in rows], float) if mask is None else np.array([r[k] for r in rows], float)[mask]
    out = dict(n=len(rows), questions=len(set(q)))
    s = {k: summ(wmean(W, col(k))) for k in ("D", "A", "P") + tuple(f"{x}.{m}" for x in "DAP" for m in MODELS)}
    out["all"] = s
    if kind == "contra":
        P = s["P"]
        out["E1"] = ("PRESENCE-CHECKS-REGISTER-CONTRADICTION" if below(P) else
                     "PRESENCE-CHECKS-BLIND" if inside(P) else "PRESENCE-UNRESOLVED")
        mask = np.array([r["has_avoid"] for r in rows])
        Wa = W[:, mask]
        A, D, Dp = col("A")[mask], col("D")[mask], col("D_pres")[mask]
        with np.errstate(invalid="ignore", divide="ignore"):
            S = wmean(Wa, A) / wmean(Wa, D)
        K = wmean(Wa, Dp) - wmean(Wa, D)
        sS, sK = summ(S), summ(K)
        out["with_avoid"] = dict(n=int(mask.sum()), questions=len(set(q[mask])), S=sS, K=sK,
                                 D=summ(wmean(Wa, D)), A=summ(wmean(Wa, A)), D_pres=summ(wmean(Wa, Dp)))
        out["E2_share"] = ("AVOID-CHECKS-CARRY-THE-LOSS" if above(sS, 0.5) else
                           "PRESENCE-CHECKS-CARRY-THE-LOSS" if below(sS, 0.5) else "SHARED")
        out["E2_counterfactual"] = ("AVOID-CHECKS-ADD-SENSITIVITY" if above(sK) else
                                    "AVOID-CHECKS-ADD-NOTHING" if inside(sK) else "UNRESOLVED")
        nm = ~mask
        if nm.sum():
            Wn = W[:, nm]
            out["without_avoid"] = dict(n=int(nm.sum()), D=summ(wmean(Wn, col("D")[nm])), P=summ(wmean(Wn, col("P")[nm])))
    else:
        P, A = s["P"], s["A"]
        out["E3"] = ("PRESENCE-CHECKS-REWARD-KEY-TERMS" if above(P) else
                     "PRESENCE-CHECKS-UNMOVED" if inside(P) else "PRESENCE-UNRESOLVED")
        out["E3_avoid"] = "AVOID-CHECKS-PENALIZE-STUFFING" if below(A) else "NOT-SHOWN"
    return out


def band_arrays(C: dict):
    main = sorted((it for it in C["items"].values() if "main" in it["draws"]), key=lambda it: it["id"])
    rows = []
    for it in main:
        sc = {}
        for a in ("likert", "boolean"):
            v = [C["grades"][(it["id"], "orig", m, a, k)]["score"] for m in MODELS for k in REPS]
            if any(x is None for x in v):
                break
            sc[a] = float(np.mean(v))
        else:
            rows.append(dict(id=it["id"], q=it["q"], h=it["h"], eL=sc["likert"] - it["h"] / 5,
                             eB=sc["boolean"] - it["h"] / 5))
    return rows


def band_estimates(rows, rng):
    q = np.array([r["q"] for r in rows])
    h = np.array([r["h"] for r in rows])
    eL = np.array([r["eL"] for r in rows])
    eB = np.array([r["eB"] for r in rows])
    W = weights(q, rng)
    out = {}
    for name, f in BANDS:
        mask = np.array([f(x) for x in h])
        Wb = W[:, mask]
        G = summ(wmean(Wb, eB[mask]) - wmean(Wb, eL[mask]))
        out[name] = dict(n=int(mask.sum()), G=G, e_likert=summ(wmean(Wb, eL[mask])), e_boolean=summ(wmean(Wb, eB[mask])),
                         verdict="CHECKLIST-HIGHER" if above(G) else "CHECKLIST-LOWER" if below(G) else "UNRESOLVED")
    return out


# ---------------------------------------------------------------- floor

def synth_defect_rows(C, kind, rng, p_pres, p_avoid, base, noise=0.06):
    """Synthetic per-check answers on the real draw and real checklist structure."""
    ids = [i for i, it in C["items"].items() if kind in it and it[kind]["ok"] and it[kind]["manip_pass"]]
    rows = []
    for i in ids:
        it = C["items"][i]
        avoid = np.array(C["q"][it["q"]]["avoid_by_check"], bool)
        n = len(avoid)
        per_m = []
        for _ in MODELS:
            latent = rng.random(n) < base
            p = np.where(avoid, p_avoid, p_pres)
            if kind == "contra":
                treated_latent = latent & ~(rng.random(n) < p)
            else:
                treated_latent = latent | (rng.random(n) < p)
            ys = {}
            for f, lat in (("neutral", latent), ("treat", treated_latent)):
                ys[f] = np.array([lat ^ (rng.random(n) < noise) for _ in REPS], float)
            per_m.append(decompose(ys["treat"].mean(0) - ys["neutral"].mean(0), avoid))
        a = np.array(per_m)
        rows.append(dict(id=i, q=it["q"], has_avoid=bool(avoid.any()), D=a[:, 0].mean(), A=a[:, 1].mean(), P=a[:, 2].mean(),
                         D_pres=np.nanmean(a[:, 3]) if not np.isnan(a[:, 3]).all() else np.nan,
                         **{f"{x}.{m}": a[j, "DAP".index(x)] for j, m in enumerate(MODELS) for x in "DAP"}))
    return rows


def synth_band_rows(C, rng, low_shift):
    rows = []
    for it in sorted((it for it in C["items"].values() if "main" in it["draws"]), key=lambda it: it["id"]):
        e = rng.normal(0, 0.15)
        rows.append(dict(id=it["id"], q=it["q"], h=it["h"], eL=e + rng.normal(0, 0.05),
                         eB=e + rng.normal(0, 0.05) + (low_shift if it["h"] <= 2.5 else 0.0)))
    return rows


def run_floor(C, reps=200):
    rng = np.random.default_rng(SEED)
    from collections import Counter
    worlds = {
        "C-PRES": ("contra", 0.12, 0.0, 0.8), "C-NULL": ("contra", 0.0, 0.0, 0.8),
        "C-AVOID": ("contra", 0.03, 0.7, 0.8),
        "S-PRES": ("stuff", 0.15, 0.0, 0.4), "S-NULL": ("stuff", 0.0, 0.0, 0.4),
    }
    res = {}
    for w, (kind, pp, pa, base) in worlds.items():
        cnt = Counter()
        for _ in range(reps):
            e = defect_estimates(synth_defect_rows(C, kind, rng, pp, pa, base), rng, kind)
            for k in ("E1", "E2_share", "E2_counterfactual", "E3", "E3_avoid"):
                if k in e:
                    cnt[f"{k}={e[k]}"] += 1
        res[w] = {k: v / reps for k, v in sorted(cnt.items())}
    for w, shift in (("B-LOW", 0.06), ("B-NULL", 0.0)):
        cnt = Counter()
        for _ in range(reps):
            b = band_estimates(synth_band_rows(C, rng, shift), rng)
            for name in b:
                cnt[f"{name}={b[name]['verdict']}"] += 1
        res[w] = {k: v / reps for k, v in sorted(cnt.items())}
    g = lambda w, k: res[w].get(k, 0.0)
    signed = lambda w, band: g(w, f"{band}=CHECKLIST-HIGHER") + g(w, f"{band}=CHECKLIST-LOWER")
    checks = {
        "C-PRES E1 REGISTER >= 0.80": g("C-PRES", "E1=PRESENCE-CHECKS-REGISTER-CONTRADICTION") >= 0.80,
        "C-NULL E1 REGISTER <= 0.10": g("C-NULL", "E1=PRESENCE-CHECKS-REGISTER-CONTRADICTION") <= 0.10,
        "C-NULL E2 ADD-SENSITIVITY <= 0.10": g("C-NULL", "E2_counterfactual=AVOID-CHECKS-ADD-SENSITIVITY") <= 0.10,
        "C-AVOID E2 AVOID-CARRY >= 0.80": g("C-AVOID", "E2_share=AVOID-CHECKS-CARRY-THE-LOSS") >= 0.80,
        "C-AVOID E2 ADD-SENSITIVITY >= 0.80": g("C-AVOID", "E2_counterfactual=AVOID-CHECKS-ADD-SENSITIVITY") >= 0.80,
        "C-PRES E2 PRESENCE-CARRY >= 0.80": g("C-PRES", "E2_share=PRESENCE-CHECKS-CARRY-THE-LOSS") >= 0.80,
        "S-PRES E3 REWARD >= 0.80": g("S-PRES", "E3=PRESENCE-CHECKS-REWARD-KEY-TERMS") >= 0.80,
        "S-NULL E3 REWARD <= 0.10": g("S-NULL", "E3=PRESENCE-CHECKS-REWARD-KEY-TERMS") <= 0.10,
        "B-LOW LOW HIGHER >= 0.80": g("B-LOW", "LOW=CHECKLIST-HIGHER") >= 0.80,
        "B-LOW MID/HIGH signed <= 0.10": max(signed("B-LOW", "MID"), signed("B-LOW", "HIGH")) <= 0.10,
        "B-NULL signed <= 0.10 each": max(signed("B-NULL", b) for b, _ in BANDS) <= 0.10,
    }
    out = dict(worlds=res, checks=checks, passed=all(checks.values()), replicates=reps)
    OUT.mkdir(exist_ok=True)
    (OUT / "floor.json").write_text(json.dumps(out, indent=1))
    for k, v in checks.items():
        print(("PASS " if v else "FAIL ") + k)
    print(json.dumps(res, indent=1))
    print("FLOOR", "PASSED" if out["passed"] else "FAILED")


def run(C):
    rng = np.random.default_rng(SEED + 1)
    res = {}
    for kind in ("contra", "stuff"):
        rows, noise = defect_arrays(C, kind)
        res[kind] = defect_estimates(rows, rng, kind)
        res[kind]["noise"] = noise
    res["bands"] = band_estimates(band_arrays(C), rng)
    res["predictions"] = {
        "E1 REGISTER": res["contra"]["E1"] == "PRESENCE-CHECKS-REGISTER-CONTRADICTION",
        "E2 SHARED or AVOID-CARRY": res["contra"]["E2_share"] in ("SHARED", "AVOID-CHECKS-CARRY-THE-LOSS"),
        "E2 ADD-SENSITIVITY": res["contra"]["E2_counterfactual"] == "AVOID-CHECKS-ADD-SENSITIVITY",
        "E3 REWARD": res["stuff"]["E3"] == "PRESENCE-CHECKS-REWARD-KEY-TERMS",
        "E4 LOW HIGHER": res["bands"]["LOW"]["verdict"] == "CHECKLIST-HIGHER",
        "E4 HIGH LOWER": res["bands"]["HIGH"]["verdict"] == "CHECKLIST-LOWER",
    }
    ci = lambda s: [s["est"], s["ci95"][0], s["ci95"][1]]
    c, st = res["contra"], res["stuff"]
    res["paper_rows"] = {
        "bands": {b: {"2": ci(v["e_likert"]), "3": ci(v["e_boolean"]), "4": ci(v["G"])} for b, v in res["bands"].items()},
        "attribution": {
            "contra_all": {"2": ci(c["all"]["D"]), "3": ci(c["all"]["A"]), "4": ci(c["all"]["P"])},
            "contra_avoid": {"2": ci(c["with_avoid"]["D"]), "3": ci(c["with_avoid"]["A"]), "5": ci(c["with_avoid"]["S"])},
            "contra_no_avoid": {"2": ci(c["without_avoid"]["D"])},
            "stuff_all": {"2": ci(st["all"]["D"]), "3": ci(st["all"]["A"]), "4": ci(st["all"]["P"])},
        },
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(res, indent=1))
    f = lambda s: f"{s['est']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]"
    c, s_ = res["contra"], res["stuff"]
    print(f"CONTRA n={c['n']}: D {f(c['all']['D'])} A {f(c['all']['A'])} P {f(c['all']['P'])} -> {c['E1']}")
    w = c["with_avoid"]
    print(f"  with avoid n={w['n']}: D {f(w['D'])} A {f(w['A'])} S {f(w['S'])} -> {c['E2_share']}; "
          f"D_pres {f(w['D_pres'])} K {f(w['K'])} -> {c['E2_counterfactual']}")
    if "without_avoid" in c:
        print(f"  without avoid n={c['without_avoid']['n']}: D {f(c['without_avoid']['D'])}")
    print(f"STUFF n={s_['n']}: D {f(s_['all']['D'])} A {f(s_['all']['A'])} P {f(s_['all']['P'])} -> {s_['E3']}, {s_['E3_avoid']}")
    for b, v in res["bands"].items():
        print(f"{b} n={v['n']}: e_L {f(v['e_likert'])} e_B {f(v['e_boolean'])} G {f(v['G'])} -> {v['verdict']}")
    print("noise contra", json.dumps(c["noise"]))
    print("noise stuff", json.dumps(s_["noise"]))
    print("predictions", res["predictions"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--floor", action="store_true")
    ap.add_argument("--cases", type=Path, default=CASES)
    a = ap.parse_args()
    C = load(a.cases)
    if a.floor:
        run_floor(C)
    else:
        run(C)
