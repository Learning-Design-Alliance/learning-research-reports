"""PRE-REGISTERED: is the core-versus-culture split a property of the data or of the linking, and does
recorded co-assignment explain the local layer?

WHY. invariance.py (studies/identifiability/core-vs-culture/) found CORE AND CULTURAL: dependence between
two Common Core clusters on one country's platform predicts it on another's (pooled b_other +0.12488
[+0.09098, +0.15834]), and local teaching proximity predicts it more strongly (b_prox +0.36290
[+0.32627, +0.40110]); ratio b_other/b_prox 0.344. Paper II reads that as "a core plus a larger local
layer" (F6). The Paper II literature review (research/readiness/learning-graph-budget-2026/literature.md,
strand 6, and "Analyses" rank 7) raises two objections:
  - 6.13 Oliveri & von Davier (2014), Kreiner & Christensen (2014); 6.14 Robitzsch & Ludtke (2023),
    Rutkowski & Svetina (2014): in measurement invariance, what counts as shared and what as local is
    defined relative to a linking. The split here rests on three linking choices: standardized D in an
    OLS regression of one platform on another, and a cluster-grain shared vocabulary. It is not
    identified independently of them, so how far it moves under other reasonable linkings is the
    quantity to report.
  - 6.11 Muthen, Kao & Burstein (1991); Naumann, Hochweber & Hartig (2014); 6.12 Huang, Wilson & Wang
    (2016); 6.15 Schmidt, Zoido & Cogan (2014): opportunity to learn acts directly on items and makes
    item groups dependent. If the local layer is OTL, a direct exposure term (were A and B set in the
    same assignment?) should take over part of what proximity in time carries, and the core should hold.
  6.16 Wu et al. (2020) is the cross-national precedent; it is not re-tested here. Written 2026-10-07;
no statistic of this design has been computed on real data.

PROVISIONAL CONSTRUCT. Every unit's cluster comes from out/unit-map.json of core-vs-culture, coded by a
language model (openai/gpt-6-sol, MAPPER; deepseek/deepseek-v4-pro, MAPPER2) from the unit's name
alone, under invariance.py's MAP_PROMPT. Its human check (human_codes.py; coder David S. Porcaro, 100
units, MAP VALIDATED at kappa >= 0.60) is pre-registered and NOT YET RETURNED. The map is unchanged
here. This is therefore a robustness analysis of a provisional construct: whatever it finds, the
core-and-culture result stays bounded by that pending check (CLAUDE.md, model-coded constructs).

DATA (reads four licensed corpora; raw data never enters the repo; only aggregates are written).
  XES3G5M (XES_DIR, shared.corpus adapter); ASSISTments 2012-13 (ASSIST_DIR: assist_slim.csv through
  the adapter for responses, assist_rich.csv for assignment_id); Eedi NeurIPS 2020 (EEDI_ANSWERS,
  EEDI_ZIP: the adapter's level-3 leaves, answers.tsv read directly so QuizId is kept); Junyi 2020
  (JUNYI2020_DIR: Log_Problem.csv STREAMED FROM junyi2020.zip with zipfile, no extraction, with the
  adapter's filter and fields copied exactly). All paths via shared.paths.data_path.
  DERIVED CACHE: learner x unit cells (learner index, unit index, attempts, correct, first time) and
  (learner, assignment, unit) triples are cached as npz under
  $LDA_SCRATCH_DIR/derived-core-vs-culture-linking/ by `python3 linking.py read`, so a crash does
  not cost a re-read; `python3 linking.py clean` deletes it, and it is deleted when the study is done.

WHAT IS REUSED (imported from invariance.py, not modified): pair_stats (cells, D, P, O, all filters),
zs, to_seconds, MIN_SHARED, CORPORA, SEED, MAPPER, MAPPER2. The cross-corpus bootstrap and
permutation scheme (invariance.py CHANGE 1: one draw of cluster pairs from the union serves every corpus
pair; the null shuffles each corpus's D once per draw across every regression it enters) is
re-implemented in cross_multi() so several estimators share the same draws; it consumes the random
stream in the same order as invariance.cross, so with OLS it must reproduce the committed
invariance-result.json (point exactly, interval to 1e-9). That reproduction is check R0 below.

PART 1. LINKING SENSITIVITY (primary map; second map reported, not verdict-bearing)
  Baseline L0 = invariance.py as committed (OLS on standardized D_c, D_c', P_c; cluster grain).
  L1 RANK: each of D_c, D_c', P_c replaced by its tie-averaged rank within the (resampled) shared pairs,
     then standardized (a Spearman-scaled linking: only the order of dependence carries over).
  L2 HUBER: the same standardized variables, fitted by a Huber M-estimator (c = 1.345, scale by MAD,
     re-estimated each IRLS step) instead of OLS: a few corpus pairs' extreme D no longer drive the fit.
  L3 COARSE: the map collapsed to grade.domain (4.NF.B -> 4.NF; 92 clusters -> 43 grade.domains), all
     cells, D, P and pairs recomputed with invariance.pair_stats at that grain; OLS as L0.
  Descriptive only: L1 and L2 at the coarse grain; pooling by the median over corpus pairs instead of
  the mean; all of it under MAPPER2.
  Every linking: pooled b_other, pooled b_prox, ratio R = b_other / b_prox (signed, per draw from the
  same draws), the same verdict rule as invariance.py (CORE: b_other lower 95% > 0 and above its
  permutation null's 97.5th; CULTURAL: b_prox lower 95% > 0; CORE AND CULTURAL: both; NEITHER). For L1
  and L2 the change in R from L0 is PAIRED (same draws); L3's pairs differ, so only its own interval
  is given. 2,000 draws as in invariance.py.
  LINKING VERDICT (on L1, L2, L3 under the primary map, among those whose estimator passed its floor):
    LINKING-ROBUST: every one gives CORE AND CULTURAL, and every R is in [0.5 R0, 1.5 R0] and < 1.
    VERDICT ROBUST, RATIO SENSITIVE: every one gives CORE AND CULTURAL, but some R falls outside that
      band or reaches 1 (the core no longer smaller than the local layer).
    LINKING-SENSITIVE: at least one gives a different verdict string (named in the output).
    UNANSWERABLE: fewer than two of L1-L3 passed their floor or had a qualifying corpus pair.
  Direction: R and both coefficients are reported signed; a negative b_other or b_prox is a different
  verdict string by the rule, never absorbed by abs().

PART 2. EXPOSURE (OPPORTUNITY TO LEARN), primary map, cluster grain
  Where recorded. ASSISTments 2012-13: assignment_id on every row of assist_rich.csv (a class's
  assignment of a problem set). Eedi: QuizId on every answer (a quiz a teacher set to a class; GroupId is
  the class). NOT recorded: XES3G5M (attempts.tsv is learner, question, concepts, response, time; the
  release holds no exam, class or assignment id) and Junyi 2020 (Log_Problem.csv has no assignment
  field; Info_UserData.csv has only counts such as belongs_to_class_cnt, no ids). So the exposure term
  enters only regressions whose dependent corpus c is ASSISTments or Eedi (6 of the 12 ordered pairs).
  E_c(A, B) = share of the learners that enter pair_stats for (A, B) in corpus c (same filters, so the
  denominator must equal that pair's n; asserted) who answered a unit of A and a unit of B within one
  assignment (ASSISTments) or one quiz (Eedi). It is opportunity to learn A and B together, recorded by
  the platform, not inferred from time.
  POSITIVITY. In each exposure corpus, over the pairs that enter its regressions: >= 30 pairs with
  E > 0, >= 30 with E = 0 or below its median (whichever applies; both counts reported), and
  |corr(E, P)| <= 0.9 (else exposure and proximity cannot be separated). A corpus failing any of these
  is dropped from Part 2; if both fail, Part 2 is UNANSWERABLE.
  Model: D_c ~ b_other D_c' + b_prox P_c + b_exp E_c (all standardized, OLS), against the same model
  without E_c on the same pairs and the same draws. Pooled over the exposure regressions (mean).
  Estimands: delta_prox = b_prox(with E) - b_prox(without), delta_other likewise, b_exp; share of the
  local layer absorbed = -delta_prox / b_prox(without). Intervals: the same 2,000 joint draws.
  Null for b_other with E: the same per-draw shuffle of each corpus's D.
  CONTROL (family-matched, deranged, sized like the treatment). E_c deranged within deciles of P_c
  across that corpus's pairs (a Sattolo cycle in each decile, so no pair keeps its own E). It keeps E's
  distribution and most of its correlation with proximity, so it can absorb what collinearity alone would
  absorb, but carries no pair-specific exposure. 200 derangements, point estimates only. Its size is its
  |corr(E~, P)| against the real |corr(E, P)|; shared/controls.check_control_scale must pass at 0.5x.
  EXPOSURE VERDICT
    EXPOSURE ABSORBS PART OF THE LOCAL LAYER: b_exp lower 95% > 0, delta_prox upper 95% < 0, and
      delta_prox below the 2.5th percentile of the deranged control's delta_prox.
    EXPOSURE ADDS NOTHING BEYOND PROXIMITY: not the above, and the b_exp interval contains 0.
    EXPOSURE CARRIES DEPENDENCE, NOT PROXIMITY'S: b_exp lower 95% > 0 but delta_prox is not below the
      control or its interval reaches 0 (exposure adds its own dependence without taking proximity's).
    EXPOSURE SIGN OPPOSITE: b_exp upper 95% < 0 (co-assignment goes with LESS dependence).
    Suffixed "; CORE HOLDS" when b_other with E (pooled over the exposure regressions) has lower 95% > 0
      and exceeds its null's 97.5th, else "; CORE DOES NOT HOLD".
    UNANSWERABLE: no exposure corpus passes positivity.
  Descriptive: the same per exposure corpus.

SYNTHETIC FLOOR (`--synthetic`, no corpus; written before any real number is read).
  R0-s: cross_multi with OLS equals invariance.cross on one synthetic world (point exactly, intervals
     to 1e-9, null 97.5th to 1e-9) -- the re-implementation is the same instrument.
  H: the Huber fit is within 0.02 of OLS on clean data and closer to the truth than OLS when 10% of
     points are leverage outliers (implementation check, reported).
  F1 (linking estimators): invariance.py's worlds (four corpora, a shared truth, D = core * truth +
     culture * P + noise), 20 each of core+culture, culture only, core only, neither, at 60 shared pairs;
     for RANK and HUBER (and OLS for reference). An estimator PASSES if it claims a core falsely in
     <= 4 of 40 core-free worlds (invariance.py CHANGE 2's calibration bar). Power at 60 and 300 pairs for
     core 0.3 (10 worlds each) reported. An estimator that fails is UNANSWERABLE in Part 1.
  F2 (exposure): four corpora, 300 shared pairs, exposure recorded in two (c1, c2), E correlated 0.6 with
     P. Worlds (20 each): W1 exposure drives the local layer (D = 0.3 truth + 0.5 E + noise, P has no
     direct effect); W2 exposure inert (D = 0.3 truth + 0.5 P + noise); W3 no core (D = 0.5 E + noise);
     W4 mixed (0.3 truth + 0.3 P + 0.3 E), reported. Corpora without exposure: 0.3 truth + 0.5 P (W3: 0.5 P).
     PASSES if W1 is read EXPOSURE ABSORBS in >= 16/20, W2 is read EXPOSURE ABSORBS in <= 2/20, and W3
     is read CORE HOLDS in <= 2/20. If it fails, Part 2's real verdict is UNANSWERABLE.
  Floor draws: 500 bootstrap/permutation draws per world (not 2,000) and 50 derangements, because the
  floor runs 100+ worlds with three estimators each; at the 2.5/97.5th percentiles 500 draws leave a
  Monte Carlo error small beside the calibration margin. Real data uses 2,000 and 200.

WHAT IT CAN AND CANNOT SAY. It says how far the core/culture split moves under three other reasonable
linkings of the same four corpora, and whether recorded co-assignment takes over part of the local
layer in the two corpora that record it. It cannot supply a linking-free split (the literature says
none exists); it cannot separate a cognitive core from a shared mathematics-education culture
(invariance.py's limit); and co-assignment is one OTL channel (being set A and B together), not taught
content, so a null for exposure does not rule out OTL acting through teaching the platform does not log.
The map's human check is pending.

RUN RECORD (2026-10-07, after the design commit 57af02d; no design change)
  The floor ran first. Because it ran slowly on a shared machine, `analyse` was started while F1 was
  still running, with one added line that makes the verdict step wait for out/linking-synthetic.json;
  pair statistics and bootstrap draws were computed in the meantime, but no verdict, coefficient or
  interval was printed or read before the floor had passed (R0, H, F1 rank and Huber, F2 all pass).
  Nothing was tuned. The derived cache was deleted after the run.

    python3 linking.py --synthetic     # floor (no corpus)
    python3 linking.py read            # stream the four corpora once into the derived cache
    python3 linking.py analyse         # Parts 1 and 2 -> out/linking-result.json, out/exposure-result.json
    python3 linking.py clean           # delete the derived cache
"""

from __future__ import annotations

import array
import csv
import io
import json
import math
import os
import sys
import zipfile
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402
from scipy.stats import rankdata  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies" / "identifiability" / "core-vs-culture"))
import invariance as inv  # noqa: E402
from shared.controls import check_control_scale  # noqa: E402
from shared.paths import data_path, scratch_root  # noqa: E402

OUT = HERE / "out"
INV_OUT = ROOT / "studies" / "identifiability" / "core-vs-culture" / "out"
MAP = INV_OUT / "unit-map.json"
DERIVED = scratch_root() / "derived-core-vs-culture-linking"
DRAWS, DERANGE = 2000, 200
FLOOR_DRAWS, FLOOR_DERANGE = 500, 50
EXPOSURE_CORPORA = ("assistments2012", "eedi")
HUBER_C = 1.345


# ---------------------------------------------------------------- estimators

def _ols(X, y):
    return np.linalg.lstsq(X, y, rcond=None)[0]


def huber(X, y, c=HUBER_C, it=50):
    b = _ols(X, y)
    for _ in range(it):
        r = y - X @ b
        s = np.median(np.abs(r - np.median(r))) / 0.6745
        if s <= 0:
            break
        u = np.abs(r / s)
        w = np.sqrt(np.where(u <= c, 1.0, c / np.maximum(u, 1e-12)))
        nb = _ols(X * w[:, None], y * w)
        if np.max(np.abs(nb - b)) < 1e-8:
            b = nb
            break
        b = nb
    return b


def _design(cols, rank):
    if rank:
        cols = [rankdata(c, method="average") for c in cols]
    return [inv.zs(c) for c in cols]


def fit(est, y, *xs):
    """Standardized coefficients (excluding intercept) of y on xs under estimator est."""
    cols = _design([y, *xs], est == "rank")
    X = np.column_stack([np.ones(len(y)), *cols[1:]])
    b = huber(X, cols[0]) if est == "huber" else _ols(X, cols[0])
    return b[1:]


# ---------------------------------------------------------------- the joint scheme

def _regressions(stats):
    per = {}
    for c in stats:
        for c2 in stats:
            if c == c2:
                continue
            shared = sorted(k for k in stats[c] if k in stats[c2] and stats[c][k]["P"] is not None)
            if len(shared) >= inv.MIN_SHARED:
                per[f"{c}<-{c2}"] = shared
    return per


def verdict(lo_o, point_o, null975, lo_p):
    core = lo_o > 0 and point_o > null975
    cult = lo_p > 0
    return "CORE AND CULTURAL" if core and cult else "CORE" if core else "CULTURAL" if cult else "NEITHER"


def cross_multi(stats, rng, ests=("ols", "rank", "huber"), draws=DRAWS, exposure=None, derange=0):
    """invariance.cross's joint bootstrap and permutation, for several estimators on the same draws.

    exposure: {corpus: {pair key: E}}; adds, for regressions whose dependent corpus is in it, OLS fits
    with and without E on the same draws, and `derange` decile-matched derangement controls.
    Consumes rng exactly as invariance.cross does (integers, then one permutation per corpus, per draw);
    derangement controls use a separate generator so the main stream is unchanged."""
    per = _regressions(stats)
    if not per:
        return {"verdicts": {e: "UNANSWERABLE" for e in ests}, "per_pair": {}}
    union = sorted(set().union(*per.values()))
    uidx = {k: i for i, k in enumerate(union)}
    corp_keys = {c: list(stats[c]) for c in stats}
    corp_vals = {c: [stats[c][x]["D"] for x in corp_keys[c]] for c in stats}
    corp_pos = {c: {k: i for i, k in enumerate(corp_keys[c])} for c in stats}
    R = {}
    for k, keys in per.items():
        c, c2 = k.split("<-")
        R[k] = {"c": c, "c2": c2, "keys": keys, "u": np.array([uidx[x] for x in keys]),
                "y": np.array([stats[c][x]["D"] for x in keys]),
                "x1": np.array([stats[c2][x]["D"] for x in keys]),
                "x2": np.array([stats[c][x]["P"] for x in keys]),
                "pos2": np.array([corp_pos[c2][x] for x in keys])}
        if exposure and c in exposure:
            R[k]["e"] = np.array([exposure[c][x] for x in keys])
    exk = [k for k in per if "e" in R[k]]

    def fits(r, idx=None, x1=None):
        y, a, p = r["y"], r["x1"] if x1 is None else x1, r["x2"]
        if idx is not None:
            y, a, p = y[idx], a[idx], p[idx]
        out = {e: fit(e, y, a, p) for e in ests}
        if "e" in r:
            ee = r["e"] if idx is None else r["e"][idx]
            out["exp_without"] = fit("ols", y, a, p)
            out["exp_with"] = fit("ols", y, a, p, ee)
        return out

    point = {k: fits(R[k]) for k in per}
    names = list(ests) + (["exp_without", "exp_with"] if exk else [])
    keys_for = {n: (exk if n.startswith("exp_") else list(per)) for n in names}
    boot = {n: [] for n in names}
    null = {n: [] for n in names}
    for _ in range(draws):
        cnt = np.bincount(rng.integers(0, len(union), len(union)), minlength=len(union))
        bd = {}
        for k in per:
            w = cnt[R[k]["u"]]
            if w.sum() >= 3:
                bd[k] = fits(R[k], np.repeat(np.arange(len(w)), w))
        for n in names:
            vs = [bd[k][n] for k in keys_for[n] if k in bd]
            boot[n].append(np.mean(vs, axis=0))
        perm = {c: rng.permutation(corp_vals[c]) for c in stats}
        nd = {k: fits(R[k], x1=perm[R[k]["c2"]][R[k]["pos2"]]) for k in per}
        for n in names:
            null[n].append(np.mean([nd[k][n][0] for k in keys_for[n]]))
    res = {"n_regressions": len(per), "estimators": {}}
    for n in names:
        pts = np.array([point[k][n] for k in keys_for[n]])
        pooled, med = pts.mean(axis=0), np.median(pts, axis=0)
        B = np.array(boot[n])
        lo, hi = np.percentile(B, 2.5, axis=0), np.percentile(B, 97.5, axis=0)
        n975 = float(np.percentile(null[n], 97.5))
        ratio_draws = B[:, 0] / B[:, 1]
        rec = {"pooled_b_other": float(pooled[0]), "pooled_b_prox": float(pooled[1]),
               "b_other_ci": [float(lo[0]), float(hi[0])], "b_prox_ci": [float(lo[1]), float(hi[1])],
               "null_b_other_975": n975,
               "ratio": float(pooled[0] / pooled[1]),
               "ratio_ci": [float(np.percentile(ratio_draws, 2.5)), float(np.percentile(ratio_draws, 97.5))],
               "median_pooled_b_other": float(med[0]), "median_pooled_b_prox": float(med[1]),
               "median_pooled_ratio": float(med[0] / med[1]),
               "verdict": verdict(float(lo[0]), float(pooled[0]), n975, float(lo[1])),
               "per_pair": {k: {"n_shared": len(per[k]), "b_other": float(point[k][n][0]),
                                "b_prox": float(point[k][n][1])} for k in keys_for[n]},
               "_boot": B}
        if pts.shape[1] > 2:
            rec["pooled_b_exp"] = float(pooled[2])
            rec["b_exp_ci"] = [float(lo[2]), float(hi[2])]
            for k in keys_for[n]:
                rec["per_pair"][k]["b_exp"] = float(point[k][n][2])
        res["estimators"][n] = rec
    for n in names:
        if n != "ols" and n in ests and "ols" in ests:
            d = res["estimators"][n]["_boot"][:, 0] / res["estimators"][n]["_boot"][:, 1] - \
                res["estimators"]["ols"]["_boot"][:, 0] / res["estimators"]["ols"]["_boot"][:, 1]
            res["estimators"][n]["ratio_change_vs_ols"] = res["estimators"][n]["ratio"] - res["estimators"]["ols"]["ratio"]
            res["estimators"][n]["ratio_change_ci_paired"] = [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]
    if exk:
        res["exposure"] = _exposure_summary(res, stats, R, exk, exposure, derange)
    for n in names:
        res["estimators"][n].pop("_boot")
    return res


def sattolo(n, rng):
    p = np.arange(n)
    for i in range(n - 1, 0, -1):
        j = int(rng.integers(0, i))
        p[i], p[j] = p[j], p[i]
    return p


def derange_in_deciles(keys, P, E, rng):
    """E deranged within deciles of P: each pair takes another pair's E from its own proximity decile."""
    order = np.argsort(P, kind="mergesort")
    bins = np.array_split(order, 10)
    out = E.copy()
    for b in bins:
        if len(b) >= 2:
            out[b] = E[b[sattolo(len(b), rng)]]
    return dict(zip(keys, out))


def _exposure_summary(res, stats, R, exk, exposure, derange):
    wo, wi = res["estimators"]["exp_without"], res["estimators"]["exp_with"]
    Bw, Bo = wi["_boot"], wo["_boot"]
    dprox = Bw[:, 1] - Bo[:, 1]
    doth = Bw[:, 0] - Bo[:, 0]
    out = {"regressions": exk,
           "delta_prox": wi["pooled_b_prox"] - wo["pooled_b_prox"],
           "delta_prox_ci": [float(np.percentile(dprox, 2.5)), float(np.percentile(dprox, 97.5))],
           "delta_other": wi["pooled_b_other"] - wo["pooled_b_other"],
           "delta_other_ci": [float(np.percentile(doth, 2.5)), float(np.percentile(doth, 97.5))],
           "share_absorbed": -(wi["pooled_b_prox"] - wo["pooled_b_prox"]) / wo["pooled_b_prox"]}
    # Control: E deranged within proximity deciles, over each exposure corpus's own pairs.
    crng = np.random.default_rng(inv.SEED + 7)
    ctrl, ctrl_corr = [], []
    real_corr = {c: float(np.corrcoef([exposure[c][k] for k in stats[c] if stats[c][k]["P"] is not None],
                                      [stats[c][k]["P"] for k in stats[c] if stats[c][k]["P"] is not None])[0, 1])
                 for c in exposure}
    for _ in range(derange):
        dm = {}
        for c in exposure:
            ks = [k for k in stats[c] if stats[c][k]["P"] is not None]
            P = np.array([stats[c][k]["P"] for k in ks])
            E = np.array([exposure[c][k] for k in ks])
            dm[c] = derange_in_deciles(ks, P, E, crng)
            ctrl_corr.append(abs(float(np.corrcoef([dm[c][k] for k in ks], P)[0, 1])))
        dp = []
        for k in exk:
            r = R[k]
            ee = np.array([dm[r["c"]][x] for x in r["keys"]])
            dp.append(fit("ols", r["y"], r["x1"], r["x2"], ee)[1] - fit("ols", r["y"], r["x1"], r["x2"])[1])
        ctrl.append(float(np.mean(dp)))
    out["control_delta_prox_mean"] = float(np.mean(ctrl)) if ctrl else None
    out["control_delta_prox_p025"] = float(np.percentile(ctrl, 2.5)) if ctrl else None
    out["control_abs_corr_with_P_mean"] = float(np.mean(ctrl_corr)) if ctrl_corr else None
    out["real_corr_E_P"] = real_corr
    if ctrl:
        sizes = {"exposure": float(np.mean([abs(v) for v in real_corr.values()])),
                 "deranged": out["control_abs_corr_with_P_mean"]}
        out["control_scale"] = check_control_scale(sizes, ["deranged"], strict=False)
    absorbs = (wi["b_exp_ci"][0] > 0 and out["delta_prox_ci"][1] < 0 and ctrl and
               out["delta_prox"] < out["control_delta_prox_p025"])
    if wi["b_exp_ci"][1] < 0:
        v = "EXPOSURE SIGN OPPOSITE"
    elif absorbs:
        v = "EXPOSURE ABSORBS PART OF THE LOCAL LAYER"
    elif wi["b_exp_ci"][0] > 0:
        v = "EXPOSURE CARRIES DEPENDENCE, NOT PROXIMITY'S"
    else:
        v = "EXPOSURE ADDS NOTHING BEYOND PROXIMITY"
    core = wi["b_other_ci"][0] > 0 and wi["pooled_b_other"] > wi["null_b_other_975"]
    out["core_holds"] = bool(core)
    out["verdict"] = v + ("; CORE HOLDS" if core else "; CORE DOES NOT HOLD")
    return out


# ---------------------------------------------------------------- reading the corpora

def _parse_time_memo():
    memo = {}

    def f(t):
        v = memo.get(t)
        if v is None:
            s = inv.to_seconds(t)
            v = math.nan if s is None else s
            if len(memo) < 2_000_000:
                memo[t] = v
        return v
    return f


def _events(corpus):
    """(learner, unit, time, y, assignment-or-None) for each attempt, as invariance.cells reads it."""
    from shared import corpus as C
    if corpus == "xes3g5m":
        for l, u, t, y in C.Xes3g5m(data_path("XES_DIR")).events():
            yield l, u, t, y, None
    elif corpus == "assistments2012":
        for l, u, t, y in C.Assistments2012(data_path("ASSIST_DIR")).events():
            yield l, u, t, y, None
    elif corpus == "eedi":
        src = C.Eedi(data_path("EEDI_ANSWERS"), data_path("EEDI_ZIP"))
        with open(data_path("EEDI_ANSWERS"), encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                for unit in src.leaves.get(r["QuestionId"], ()):
                    yield r["UserId"], unit, r["DateAnswered"], float(r["IsCorrect"]), r["QuizId"]
    elif corpus == "junyi2020":
        z = zipfile.ZipFile(data_path("JUNYI2020_DIR") / "junyi2020.zip")
        with z.open("Log_Problem.csv") as raw:
            for r in csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig")):
                ok = (r.get("is_correct") or "").strip().lower()
                if ok not in ("true", "false"):
                    continue
                yield r["uuid"], r["ucid"], r["timestamp_TW"], 1.0 if ok == "true" else 0.0, None


def _assist_assignments():
    with open(data_path("ASSIST_DIR") / "assist_rich.csv") as f:
        for r in csv.DictReader(f):
            if r.get("skill_id") and r.get("assignment_id") and r.get("user_id"):
                yield r["user_id"], r["skill_id"], r["assignment_id"]


def read(corpus):
    """Stream one corpus into learner x unit cells and (learner, assignment, unit) triples; cache them."""
    DERIVED.mkdir(parents=True, exist_ok=True)
    path = DERIVED / f"{corpus}.npz"
    if path.exists():
        return
    maps = json.loads(MAP.read_text())["maps"]
    units = sorted(set(maps[inv.MAPPER].get(corpus, {})) | set(maps[inv.MAPPER2].get(corpus, {})))
    uix = {u: i for i, u in enumerate(units)}
    lix = {}
    L, U, T, Y = array.array("i"), array.array("i"), array.array("d"), array.array("f")
    ax, aL, aA, aU = {}, array.array("i"), array.array("i"), array.array("i")
    pt = _parse_time_memo()
    n = 0
    for l, u, t, y, a in _events(corpus):
        ui = uix.get(u)
        if ui is None:
            continue
        li = lix.setdefault(l, len(lix))
        L.append(li); U.append(ui); T.append(pt(t)); Y.append(y)
        if a is not None:
            aL.append(li); aA.append(ax.setdefault(a, len(ax))); aU.append(ui)
        n += 1
        if n % 2_000_000 == 0:
            print(f"   {corpus}: {n:,} events", flush=True)
    if corpus == "assistments2012":
        for l, u, a in _assist_assignments():
            ui, li = uix.get(u), lix.get(l)
            if ui is None or li is None:
                continue
            aL.append(li); aA.append(ax.setdefault(a, len(ax))); aU.append(ui)
    L, U, T, Y = (np.frombuffer(x, dtype=d).copy() for x, d in ((L, np.int32), (U, np.int32), (T, np.float64), (Y, np.float32)))
    key = L.astype(np.int64) * len(units) + U
    uk, invk = np.unique(key, return_inverse=True)
    cn = np.bincount(invk).astype(np.int64)
    cs = np.bincount(invk, weights=Y.astype(np.float64))
    tmin = np.full(len(uk), np.inf)
    np.minimum.at(tmin, invk, np.where(np.isnan(T), np.inf, T))
    del L, U, T, Y, key, invk
    tri = np.zeros((0, 3), dtype=np.int64)
    if len(aL):
        tri = np.unique(np.column_stack([np.frombuffer(aL, dtype=np.int32), np.frombuffer(aA, dtype=np.int32),
                                         np.frombuffer(aU, dtype=np.int32)]).astype(np.int64), axis=0)
    np.savez(path, cl=(uk // len(units)).astype(np.int32), cu=(uk % len(units)).astype(np.int32), cn=cn, cs=cs,
             ct=tmin, tri=tri, n_learners=len(lix), n_events=n, n_assignments=len(ax))
    (DERIVED / f"{corpus}.units.json").write_text(json.dumps(units))
    print(f"   {corpus}: {n:,} events, {len(lix):,} learners, {len(uk):,} learner-unit cells, "
          f"{len(tri):,} assignment triples", flush=True)


def load(corpus):
    z = np.load(DERIVED / f"{corpus}.npz")
    units = json.loads((DERIVED / f"{corpus}.units.json").read_text())
    return z, units


def coarse(cl):
    return cl if cl == "NONE" else cl.rsplit(".", 1)[0]


def by_from_cells(z, units, umap):
    """learner -> {cluster: (n, s, first time)} -- invariance.cells' output, from the cached unit cells."""
    lab = [umap.get(u) for u in units]
    names = sorted({x for x in lab if x and x != "NONE"})
    cix = {c: i for i, c in enumerate(names)}
    uc = np.array([cix.get(x, -1) if x and x != "NONE" else -1 for x in lab])
    c = uc[z["cu"]]
    keep = c >= 0
    l, c, n, s, t = z["cl"][keep].astype(np.int64), c[keep], z["cn"][keep], z["cs"][keep], z["ct"][keep]
    key = l * len(names) + c
    uk, ik = np.unique(key, return_inverse=True)
    N, S = np.bincount(ik, weights=n), np.bincount(ik, weights=s)
    Tm = np.full(len(uk), np.inf)
    np.minimum.at(Tm, ik, t)
    by = defaultdict(dict)
    for k, a, b, tt in zip(uk.tolist(), N.tolist(), S.tolist(), Tm.tolist()):
        by[k // len(names)][names[k % len(names)]] = (int(a), float(b), tt)
    return by


def coassigned(z, units, umap):
    """learner -> set of 'A|B' cluster pairs answered within one assignment / quiz."""
    tri = z["tri"]
    co = defaultdict(set)
    if not len(tri):
        return co
    lab = [umap.get(u) for u in units]
    names = sorted({x for x in lab if x and x != "NONE"})
    cix = {c: i for i, c in enumerate(names)}
    uc = np.array([cix.get(x, -1) if x and x != "NONE" else -1 for x in lab])
    c = uc[tri[:, 2]]
    keep = c >= 0
    g = np.unique(np.column_stack([tri[keep, 0], tri[keep, 1], c[keep]]), axis=0)
    brk = np.flatnonzero(np.any(np.diff(g[:, :2], axis=0) != 0, axis=1)) + 1
    for grp in np.split(g, brk):
        if len(grp) < 2:
            continue
        cs = sorted(names[i] for i in grp[:, 2].tolist())
        co[int(grp[0, 0])].update(f"{a}|{b}" for a, b in combinations(cs, 2))
    return co


def exposure_share(by, co, stats):
    """E per pair key: share of the learners pair_stats counted for that pair who were co-assigned."""
    num, den = Counter(), Counter()
    for l, cs in by.items():
        N = sum(v[0] for v in cs.values())
        ok = sorted(c for c, v in cs.items() if v[0] >= inv.MIN_CELL)
        mine = co.get(l, ())
        for i in range(len(ok)):
            for j in range(i + 1, len(ok)):
                a, b = ok[i], ok[j]
                if N - cs[a][0] - cs[b][0] < inv.MIN_REST:
                    continue
                k = f"{a}|{b}"
                if k in stats:
                    den[k] += 1
                    if k in mine:
                        num[k] += 1
    for k in stats:
        assert den[k] == stats[k]["n"], (k, den[k], stats[k]["n"])
    return {k: num[k] / den[k] for k in stats}


# ---------------------------------------------------------------- real-data run

def strip(d):
    return {k: v for k, v in d.items() if not k.startswith("_")}


def analyse():
    maps = json.loads(MAP.read_text())["maps"]
    committed = json.loads((INV_OUT / "invariance-result.json").read_text())
    committed_pairs = json.loads((INV_OUT / "invariance-pairs.json").read_text())
    stats = {}   # (map, grain) -> corpus -> pair stats
    exposure = {}
    for corpus in inv.CORPORA:
        read(corpus)
        z, units = load(corpus)
        for model in (inv.MAPPER, inv.MAPPER2):
            um = maps[model].get(corpus, {})
            for grain, m in (("cluster", um), ("grade.domain", {u: coarse(c) for u, c in um.items()})):
                print(f"{corpus} {model} {grain}", flush=True)
                by = by_from_cells(z, units, m)
                st = inv.pair_stats(by)
                stats.setdefault((model, grain), {})[corpus] = st
                if model == inv.MAPPER and grain == "cluster" and corpus in EXPOSURE_CORPORA:
                    exposure[corpus] = exposure_share(by, coassigned(z, units, m), st)
                del by
    # R0: the recomputed primary cluster stats equal the committed ones; then use the committed order.
    r0 = {}
    for corpus in inv.CORPORA:
        a, b = stats[(inv.MAPPER, "cluster")][corpus], committed_pairs[corpus]
        same_keys = set(a) == set(b)
        dmax = max((abs(a[k]["D"] - b[k]["D"]) for k in b if k in a), default=None)
        nsame = all(a[k]["n"] == b[k]["n"] and a[k]["P"] == b[k]["P"] for k in b if k in a)
        r0[corpus] = {"same_pairs": same_keys, "max_abs_D_diff": dmax, "n_and_P_equal": nsame,
                      "pairs_recomputed": len(a), "pairs_committed": len(b)}
    r0_ok = all(v["same_pairs"] and v["n_and_P_equal"] and v["max_abs_D_diff"] < 1e-9 for v in r0.values())
    print("R0 recomputed stats match committed:", r0_ok, json.dumps(r0), flush=True)
    if r0_ok:
        stats[(inv.MAPPER, "cluster")] = {c: committed_pairs[c] for c in inv.CORPORA}

    results = {"r0_pair_stats_match": r0, "r0_ok": r0_ok, "runs": {}}
    for (model, grain), st in stats.items():
        ex = exposure if (model == inv.MAPPER and grain == "cluster") else None
        print(f"cross_multi {model} {grain}", flush=True)
        res = cross_multi(st, np.random.default_rng(inv.SEED), exposure=ex, derange=DERANGE if ex else 0)
        res["pairs_per_corpus"] = {c: len(s) for c, s in st.items()}
        results["runs"][f"{model} | {grain}"] = res
    base = results["runs"][f"{inv.MAPPER} | cluster"]["estimators"]["ols"]
    cm = committed[inv.MAPPER]["cross"]
    results["r0_reproduces_committed"] = {
        "pooled_b_other": [base["pooled_b_other"], cm["pooled_b_other"]],
        "pooled_b_prox": [base["pooled_b_prox"], cm["pooled_b_prox"]],
        "b_other_ci": [base["b_other_ci"], cm["b_other_ci"]],
        "b_prox_ci": [base["b_prox_ci"], cm["b_prox_ci"]],
        "null_b_other_975": [base["null_b_other_975"], cm["null_b_other_975"]],
        "exact": bool(abs(base["pooled_b_other"] - cm["pooled_b_other"]) < 1e-9 and
                      abs(base["b_other_ci"][0] - cm["b_other_ci"][0]) < 1e-9 and
                      abs(base["null_b_other_975"] - cm["null_b_other_975"]) < 1e-9)}

    import time
    while not (OUT / "linking-synthetic.json").exists():   # the floor may still be running
        time.sleep(60)
    floor = json.loads((OUT / "linking-synthetic.json").read_text())
    passed = {e: floor["F1"][e]["passes"] for e in ("rank", "huber")}
    R0 = base["ratio"]
    prim = results["runs"][f"{inv.MAPPER} | cluster"]["estimators"]
    coarse_ols = results["runs"][f"{inv.MAPPER} | grade.domain"]["estimators"]["ols"]
    alts = {"L1 rank": prim["rank"] if passed["rank"] else None,
            "L2 huber": prim["huber"] if passed["huber"] else None,
            "L3 grade.domain": coarse_ols if results["runs"][f"{inv.MAPPER} | grade.domain"]["n_regressions"] else None}
    usable = {k: v for k, v in alts.items() if v is not None}
    table = {k: {"verdict": v["verdict"], "b_other": v["pooled_b_other"], "b_other_ci": v["b_other_ci"],
                 "b_prox": v["pooled_b_prox"], "b_prox_ci": v["b_prox_ci"], "ratio": v["ratio"],
                 "ratio_ci": v["ratio_ci"], "ratio_change": v["ratio"] - R0,
                 "ratio_change_ci_paired": v.get("ratio_change_ci_paired"),
                 "null_b_other_975": v["null_b_other_975"]} for k, v in usable.items()}
    if len(usable) < 2:
        lv = "UNANSWERABLE"
    elif any(v["verdict"] != "CORE AND CULTURAL" for v in usable.values()):
        lv = "LINKING-SENSITIVE (" + ", ".join(f"{k}: {v['verdict']}" for k, v in usable.items()
                                                if v["verdict"] != "CORE AND CULTURAL") + ")"
    elif all(0.5 * R0 <= v["ratio"] <= 1.5 * R0 and v["ratio"] < 1 for v in usable.values()):
        lv = "LINKING-ROBUST"
    else:
        lv = "VERDICT ROBUST, RATIO SENSITIVE"
    link = {"baseline_L0": {"b_other": base["pooled_b_other"], "b_other_ci": base["b_other_ci"],
                            "b_prox": base["pooled_b_prox"], "b_prox_ci": base["b_prox_ci"], "ratio": R0,
                            "ratio_ci": base["ratio_ci"], "verdict": base["verdict"]},
            "alternatives": table, "excluded_for_floor": [k for k, v in alts.items() if v is None],
            "ratio_band": [0.5 * R0, 1.5 * R0], "verdict": lv,
            "map_status": "model-coded (openai/gpt-6-sol primary, deepseek/deepseek-v4-pro second), name only; human check pending"}
    results["linking"] = link
    OUT.mkdir(exist_ok=True)
    (OUT / "linking-result.json").write_text(json.dumps(results, indent=1, default=float) + "\n")

    # Part 2.
    pr = results["runs"][f"{inv.MAPPER} | cluster"]
    pos = {}
    for c in EXPOSURE_CORPORA:
        ks = sorted({x for k in pr["exposure"]["regressions"] if k.startswith(c + "<-")
                     for x in _regressions(stats[(inv.MAPPER, "cluster")])[k]})
        E = np.array([exposure[c][k] for k in ks])
        P = np.array([stats[(inv.MAPPER, "cluster")][c][k]["P"] for k in ks])
        pos[c] = {"pairs": len(ks), "pairs_E_pos": int((E > 0).sum()), "pairs_E_zero": int((E == 0).sum()),
                  "pairs_E_at_or_below_median": int((E <= np.median(E)).sum()),
                  "E_mean": float(E.mean()), "E_median": float(np.median(E)), "E_max": float(E.max()),
                  "corr_E_P": float(np.corrcoef(E, P)[0, 1]) if E.std() > 0 else None}
        low = pos[c]["pairs_E_zero"] if pos[c]["pairs_E_zero"] >= 30 else pos[c]["pairs_E_at_or_below_median"]
        pos[c]["passes"] = bool(pos[c]["pairs_E_pos"] >= 30 and low >= 30 and pos[c]["corr_E_P"] is not None
                                and abs(pos[c]["corr_E_P"]) <= 0.9)
    ok = [c for c in EXPOSURE_CORPORA if pos[c]["passes"]]
    expo = {"positivity": pos, "recorded": {"assistments2012": "assignment_id (assist_rich.csv)",
                                            "eedi": "QuizId (answers.tsv); GroupId is the class",
                                            "xes3g5m": "not recorded", "junyi2020": "not recorded"}}
    if not ok:
        expo["verdict"] = "UNANSWERABLE"
    else:
        if set(ok) != set(EXPOSURE_CORPORA):
            pr = cross_multi(stats[(inv.MAPPER, "cluster")], np.random.default_rng(inv.SEED), ests=("ols",),
                             exposure={c: exposure[c] for c in ok}, derange=DERANGE)
        expo["pooled"] = {k: v for k, v in pr["exposure"].items()}
        expo["with_E"] = strip(pr["estimators"]["exp_with"])
        expo["without_E"] = strip(pr["estimators"]["exp_without"])
        expo["verdict"] = pr["exposure"]["verdict"]
        if not floor["F2"]["passes"]:
            expo["verdict"] = "UNANSWERABLE (floor failed; read would have been: " + expo["verdict"] + ")"
        expo["per_corpus"] = {}
        for c in ok:
            sub = cross_multi(stats[(inv.MAPPER, "cluster")], np.random.default_rng(inv.SEED), ests=("ols",),
                              exposure={c: exposure[c]}, derange=DERANGE)
            expo["per_corpus"][c] = {"exposure": sub["exposure"],
                                     "with_E": strip(sub["estimators"]["exp_with"]),
                                     "without_E": strip(sub["estimators"]["exp_without"])}
    (OUT / "exposure-result.json").write_text(json.dumps(expo, indent=1, default=float) + "\n")
    pairs_out = {f"{m} | {g}": st for (m, g), st in stats.items() if not (m == inv.MAPPER and g == "cluster")}
    pairs_out["exposure_share_primary_cluster"] = exposure
    (OUT / "linking-pairs.json").write_text(json.dumps(pairs_out) + "\n")
    print("LINKING VERDICT:", lv)
    print("EXPOSURE VERDICT:", expo["verdict"])


# ---------------------------------------------------------------- synthetic floor

def _world(rng, core, culture, npairs=60):
    truth = rng.normal(size=npairs)
    stats = {}
    for c in ("c1", "c2", "c3", "c4"):
        P = rng.normal(size=npairs)
        D = core * truth + culture * P + rng.normal(size=npairs)
        stats[c] = {f"p{i}": {"n": 500, "D": float(D[i]), "P": float(P[i]), "O": 0.5} for i in range(npairs)}
    return stats


def _exposure_world(rng, kind, npairs=300):
    truth = rng.normal(size=npairs)
    stats, ex = {}, {}
    for c in ("c1", "c2", "c3", "c4"):
        P = rng.normal(size=npairs)
        E = 0.6 * P + 0.8 * rng.normal(size=npairs)
        noise = rng.normal(size=npairs)
        if c in ("c1", "c2"):
            D = {"W1": 0.3 * truth + 0.5 * E, "W2": 0.3 * truth + 0.5 * P, "W3": 0.5 * E,
                 "W4": 0.3 * truth + 0.3 * P + 0.3 * E}[kind] + noise
            ex[c] = {f"p{i}": float(E[i]) for i in range(npairs)}
        else:
            D = (0.5 * P if kind == "W3" else 0.3 * truth + 0.5 * P) + noise
        stats[c] = {f"p{i}": {"n": 500, "D": float(D[i]), "P": float(P[i]), "O": 0.5} for i in range(npairs)}
    return stats, ex


def synthetic():
    rng = np.random.default_rng(inv.SEED)
    out = {}
    # R0-s: same instrument as invariance.cross.
    w = _world(rng, 0.3, 0.5, 80)
    a = inv.cross(w, np.random.default_rng(11))
    b = cross_multi(w, np.random.default_rng(11), ests=("ols",))["estimators"]["ols"]
    r0 = {"point": [a["pooled_b_other"], b["pooled_b_other"]], "ci": [a["b_other_ci"], b["b_other_ci"]],
          "prox_ci": [a["b_prox_ci"], b["b_prox_ci"]], "null": [a["null_b_other_975"], b["null_b_other_975"]]}
    r0["equal"] = bool(abs(a["pooled_b_other"] - b["pooled_b_other"]) < 1e-12 and
                       max(abs(x - y) for x, y in zip(a["b_other_ci"] + a["b_prox_ci"], b["b_other_ci"] + b["b_prox_ci"])) < 1e-9
                       and abs(a["null_b_other_975"] - b["null_b_other_975"]) < 1e-9)
    print("R0-s cross_multi == invariance.cross:", r0["equal"], flush=True)
    out["R0"] = r0
    # H: Huber implementation.
    hr = []
    for _ in range(20):
        x = rng.normal(size=400)
        y = 0.5 * x + rng.normal(size=400)
        X = np.column_stack([np.ones(400), x])
        clean = (huber(X, y)[1], _ols(X, y)[1])
        bad = rng.random(400) < 0.10
        y2 = y.copy()
        y2[bad] = -3 * x[bad]
        cont = (huber(X, y2)[1], _ols(X, y2)[1])
        hr.append((abs(clean[0] - clean[1]), abs(cont[0] - 0.5), abs(cont[1] - 0.5)))
    hr = np.array(hr)
    out["H"] = {"mean_abs_huber_minus_ols_clean": float(hr[:, 0].mean()),
                "mean_abs_err_contaminated_huber": float(hr[:, 1].mean()),
                "mean_abs_err_contaminated_ols": float(hr[:, 2].mean())}
    out["H"]["passes"] = bool(out["H"]["mean_abs_huber_minus_ols_clean"] < 0.02 and
                              out["H"]["mean_abs_err_contaminated_huber"] < out["H"]["mean_abs_err_contaminated_ols"])
    print("H:", out["H"], flush=True)
    # F1: calibration of each estimator on invariance.py's worlds.
    ests = ("ols", "rank", "huber")
    tally = {e: defaultdict(Counter) for e in ests}
    for name, core, culture in (("core+culture", 0.5, 0.5), ("culture only", 0.0, 0.5),
                                ("core only", 0.5, 0.0), ("neither", 0.0, 0.0)):
        for _ in range(20):
            r = cross_multi(_world(rng, core, culture), np.random.default_rng(rng.integers(1 << 30)), ests=ests,
                            draws=FLOOR_DRAWS)
            for e in ests:
                tally[e][name][r["estimators"][e]["verdict"]] += 1
        print("  F1", name, {e: dict(tally[e][name]) for e in ests}, flush=True)
    F1 = {}
    for e in ests:
        t = tally[e]
        false_core = sum(v for wn in ("culture only", "neither") for k, v in t[wn].items() if "CORE" in k)
        hits = sum(v for wn in ("core+culture", "core only") for k, v in t[wn].items() if "CORE" in k)
        false_cult = sum(v for wn in ("core only", "neither") for k, v in t[wn].items() if "CULTURAL" in k)
        F1[e] = {"worlds": {k: dict(v) for k, v in t.items()}, "false_core_of_40": false_core,
                 "core_found_of_40_at_60_pairs": hits, "false_culture_of_40": false_cult,
                 "passes": false_core <= 4, "power_core_0.3": {}}
    for npairs in (60, 300):
        hits = Counter()
        for _ in range(10):
            r = cross_multi(_world(rng, 0.3, 0.5, npairs), np.random.default_rng(rng.integers(1 << 30)), ests=ests,
                            draws=FLOOR_DRAWS)
            for e in ests:
                hits[e] += "CORE" in r["estimators"][e]["verdict"]
        for e in ests:
            F1[e]["power_core_0.3"][f"{npairs} pairs"] = hits[e] / 10
        print(f"  F1 power core 0.3 at {npairs} pairs:", dict(hits), flush=True)
    out["F1"] = F1
    # F2: exposure.
    F2 = {}
    for kind in ("W1", "W2", "W3", "W4"):
        vs = Counter()
        for _ in range(20):
            st, ex = _exposure_world(rng, kind)
            r = cross_multi(st, np.random.default_rng(rng.integers(1 << 30)), ests=("ols",), draws=FLOOR_DRAWS,
                            exposure=ex, derange=FLOOR_DERANGE)
            vs[r["exposure"]["verdict"]] += 1
        F2[kind] = dict(vs)
        print("  F2", kind, dict(vs), flush=True)
    absorbs = lambda k: sum(v for s, v in F2[k].items() if s.startswith("EXPOSURE ABSORBS"))
    holds = lambda k: sum(v for s, v in F2[k].items() if s.endswith("; CORE HOLDS"))
    F2["W1_absorbs"], F2["W2_false_absorbs"], F2["W3_false_core"] = absorbs("W1"), absorbs("W2"), holds("W3")
    F2["passes"] = bool(F2["W1_absorbs"] >= 16 and F2["W2_false_absorbs"] <= 2 and F2["W3_false_core"] <= 2)
    out["F2"] = F2
    out["passes"] = {"R0": r0["equal"], "H": out["H"]["passes"], "F1_rank": F1["rank"]["passes"],
                     "F1_huber": F1["huber"]["passes"], "F2": F2["passes"]}
    out["draws"] = {"bootstrap_and_permutation": FLOOR_DRAWS, "derangements": FLOOR_DERANGE}
    OUT.mkdir(exist_ok=True)
    (OUT / "linking-synthetic.json").write_text(json.dumps(out, indent=1) + "\n")
    print("FLOOR:", out["passes"])


def clean():
    import shutil
    if DERIVED.exists():
        shutil.rmtree(DERIVED)
        print("removed", DERIVED)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "read":
        for c in (sys.argv[2:] or inv.CORPORA):
            read(c)
    else:
        {"--synthetic": synthetic, "analyse": analyse, "clean": clean}.get(cmd, lambda: print(__doc__))()
