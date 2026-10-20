"""PRE-REGISTERED: is the "core" that carries across national curricula partly shared language?

WHY. invariance.py (studies/identifiability/core-vs-culture/) found CORE AND CULTURAL on four corpora:
pooled b_other +0.12488 [+0.09098, +0.15834], pooled b_prox +0.36290 [+0.32627, +0.40110], null 97.5th
for b_other +0.02232 (Paper II 5.5). The four corpora form two language pairs: English (ASSISTments
2012-13, US; Eedi, UK) and Chinese (XES3G5M, mainland China; Junyi 2020, Taiwan). The literature sweep
(research/readiness/learning-graph-budget-2026/literature-sweep-2.md, C.12: Gokce, Berberoglu, Wells &
Sireci 2021, TIMSS 2015) found differential item functioning growing with linguistic and cultural
distance, smallest where the language is the same and the country differs, which is exactly the
contrast these four corpora allow. If part of the "core" is shared language (and the culture that comes
with it), b_other should be larger on the 4 same-language ordered corpus pairs than on the 8
cross-language ones. Written 2026-10-08.

WHAT HAS ALREADY BEEN SEEN, AND WHAT IS NEW. Each of invariance.py's 12 per-ordered-pair OLS
coefficients depends only on the two corpora in that pair, and all 12 are printed, for both maps, in
../core-vs-culture/out/invariance-result.json. The author of this design printed and read them while
reading invariance.py's outputs, before writing this design, and so knew in advance, approximately,
the point estimates below: under the primary map the same-language mean is about +0.121 and the
cross-language mean about +0.127, so the point contrast is near zero, slightly negative, and the
language pairing's same-pair mean is the middle one of the three pairings (one of the alternatives is
higher, one lower). The point estimate is therefore NOT blind, and the equivalence margin M below was
chosen knowing it (M is half the pooled core; the reason for that number is given with it). What is
new and not yet computed: the joint bootstrap intervals of every quantity below, the specificity
contrast's interval, the cross-language core's interval and null, the floor, and the second map's
intervals. The brief asked for the design to be committed before the real split was read; the split's
point values cannot be unread, so the verdict rests on the intervals, which have not been computed.

CONSTRUCT. Unchanged from invariance.py: every unit's Common Core K-8 cluster was coded from the unit's
name by a language model (openai/gpt-6-sol primary; deepseek/deepseek-v4-pro second) under
invariance.MAP_PROMPT (out/unit-map.json). Blind human check (human_codes.py; coder human:david-porcaro,
87 items): MAP VALIDATED narrowly, kappa 0.606 [0.493, 0.709] against the bar 0.60. No second human
coder (human-human ceiling) has been run. No model is called here.
  A threat specific to this question: the mapper reads names in two languages. If its errors are
  language-specific (Chinese names mis-mapped in a consistent way, English names in another), two
  same-language corpora share mapping error, which can raise or lower their agreement in D. A
  same-language excess here could be the mapper's language, not the learners'. The second map is
  reported for that reason, but both are model maps, so it is not a control for it.

DATA. This script reads no corpus. It reads committed aggregates only, as no_xes.py does:
  - ../core-vs-culture/out/invariance-pairs.json: per corpus, per cluster pair, n, D, P, O under the
    primary map. core-vs-culture-linking (linking.py, check R0) recomputed these from the raw corpora
    (ASSISTments 2012-13, Eedi NeurIPS 2020, Junyi 2020, XES3G5M) and matched them (same pairs, same n
    and P, D within 8.4e-14); that check is what licenses using the committed file rather than a
    multi-hour re-stream of four licensed corpora.
  - ../core-vs-culture-linking/out/linking-pairs.json, key "deepseek/deepseek-v4-pro | cluster": the
    same statistics under the second map (descriptive only).
Imported, not modified: invariance.py (cross, CORPORA, SEED, MAPPER, MAPPER2) and linking.py
(_regressions, fit). The joint scheme is invariance.py's CHANGE 1, re-implemented in draws() so that
each ordered pair's b_other is kept per draw; draws() consumes the random stream exactly as
invariance.cross and linking.cross_multi do (one integers() draw over the union, then one
permutation per corpus, per draw), so its pooled-over-12 b_other must reproduce invariance.cross.
That is check F0 (synthetic) and R0 (real: the committed invariance-result.json interval).

MODEL AND ESTIMAND. invariance.py fits one OLS per ordered corpus pair (c <- c'):
  z(D_c) ~ b_other z(D_c') + b_prox z(P_c), over the cluster pairs the two corpora share,
and pools by the unweighted mean over the 12 ordered pairs. There is no pooled regression in which an
interaction term could sit; the language label is a property of the ordered corpus pair, i.e. of a
whole regression. So the estimand is the split of that same mean:
  b_same  = mean b_other over the 4 same-language ordered pairs
            (xes3g5m<->junyi2020, assistments2012<->eedi, both directions);
  b_cross = mean b_other over the 8 cross-language ordered pairs;
  DELTA   = b_same - b_cross (signed; positive = the core is larger within a language).
Since pooled b_other = (4 b_same + 8 b_cross) / 12 = b_cross + DELTA / 3, the share of the pooled
core attributable to a same-language excess is (DELTA / 3) / pooled, reported.
CORPUS MAIN EFFECTS CANCEL. Each pairing's 4 same-pair regressions contain every corpus once as the
dependent and once as the source, so any additive effect of a corpus (one platform's D being noisier,
or one being a better predictor of all others) contributes equally to b_same and to b_cross. DELTA
measures only a pair-specific affinity between corpora.

THE REFERENCE DISTRIBUTION (the control). The language label is assigned to corpora, so the unit to
permute is the corpus, not the cluster pair. A relabelling that keeps the design (two pairs of two
corpora; 4 same vs 8 cross ordered pairs) is a partition of the 4 corpora into 2 unordered pairs.
There are exactly 3 such partitions (4! / (2! 2! 2!) = 3):
  LANGUAGE  {xes3g5m, junyi2020} {assistments2012, eedi}
  ALT-1     {xes3g5m, assistments2012} {eedi, junyi2020}
  ALT-2     {xes3g5m, eedi} {assistments2012, junyi2020}
So the reference distribution is these two alternative pairings, each the same size as the treatment
(4 vs 8 ordered pairs, every corpus in one pair). Writing s_i for pairing i's same-pair mean and m for
the mean of all 12, DELTA_i = 1.5 (s_i - m), so the three DELTAs sum to zero and rank as the s_i do.
With 3 labellings, a rank test alone can never reach p < 1/3; the reference is used as an interval
contrast instead:
  SPEC = DELTA_LANGUAGE - max(DELTA_ALT-1, DELTA_ALT-2)    (for a positive reading)
  SPEC- = DELTA_LANGUAGE - min(DELTA_ALT-1, DELTA_ALT-2)   (for a negative reading)
computed per bootstrap draw. A language reading needs the language pairing to beat both alternative
pairings, not just zero: otherwise "same language" is one of several corpus affinities of the same
size. Note what it cannot do: language is confounded with region and culture (East Asia vs US/UK), and
with only two pairs per pairing, any pairwise affinity of that size would score the same.

INTERVAL AND RESAMPLING UNIT. As invariance.py: 2,000 joint bootstraps, seed invariance.SEED; one draw
of cluster pairs (with replacement) from the union of all 12 regressions' shared cluster pairs serves
every regression; each regression's b_other is refitted on its resampled shared pairs; b_same, b_cross,
DELTA, the alternatives' DELTAs, SPEC and SPEC- are computed from the same draw. Percentile 95%
intervals. This resamples cluster pairs conditional on the four corpora; it does not resample corpora
(there are four), which is why the pairing contrast, not the bootstrap, carries the corpus-level control.

PRE-REGISTERED VERDICT (primary map; signed throughout, never on abs()). M = 0.0625, half of the pooled
core (+0.125): a same-language excess below M changes the pooled core by less than M/3 = 0.021, about
a sixth of it, which would not change any sentence of Paper II 5.5.
  CORE IS LARGER WITHIN A LANGUAGE: DELTA lower 95% > 0 and SPEC lower 95% > 0.
  WITHIN-LANGUAGE EXCESS, NOT SPECIFIC TO LANGUAGE: DELTA lower 95% > 0 and SPEC lower 95% <= 0.
  CORE IS LARGER ACROSS LANGUAGES: DELTA upper 95% < 0 and SPEC- upper 95% < 0.
  CROSS-LANGUAGE EXCESS, NOT SPECIFIC TO LANGUAGE: DELTA upper 95% < 0 and SPEC- upper 95% >= 0.
  NO LANGUAGE DIFFERENCE: the DELTA interval lies inside [-M, +M] (and none of the above).
  UNDERPOWERED: the DELTA interval contains 0 and reaches beyond -M or +M.
  Floor rules: if the floor's calibration (F1, F3) fails, the verdict is UNANSWERABLE (the read it
  would have been is recorded). If its power check (F2) fails, a NO LANGUAGE DIFFERENCE reads
  UNDERPOWERED, since an instrument that cannot see a planted bonus cannot bound one.
  SECONDARY (pre-registered statement, not the verdict): CROSS-LANGUAGE CORE HOLDS if b_cross lower
  95% > 0 and b_cross > the 97.5th percentile of its permutation null (the same joint null as
  invariance.py: each corpus's D shuffled once per draw over all its own pairs, for every regression
  it enters; b_cross recomputed on the 8 cross-language regressions); else CROSS-LANGUAGE CORE NOT SHOWN.
  WHAT EACH OUTCOME MEANS FOR PAPER II 5.5 (fixed now):
    WITHIN A LANGUAGE: part of the "core" is shared language and culture; 5.5 states b_cross as the
      cross-language core beside the pooled figure, and Threats names language.
    NOT SPECIFIC TO LANGUAGE (either sign): corpus pairs differ in affinity, but language does not
      stand out from other pairings; 5.5 reports DELTA and the alternatives, and draws no language
      conclusion.
    ACROSS LANGUAGES: the opposite of the C.12 prediction; reported as such, with the mapper threat.
    NO LANGUAGE DIFFERENCE: a same-language excess larger than M is excluded; 5.5 can say the core is
      not explained by shared language between these two pairs, bounded by the interval.
    UNDERPOWERED: the design cannot tell; 5.5 says so.
  Reported beside it (descriptive): b_same, b_cross, DELTA, share of pooled core, each with interval;
  the three pairings' s_i and DELTA_i with intervals; the bootstrap share of draws in which the
  language pairing ranks first, second and third; per unordered corpus pair, the mean of its two
  directions with interval; the same under the second map; check R0.

FLOOR (--synthetic; no corpus values. It reads only which cluster-pair keys each corpus holds and
  whether P is defined, from invariance-pairs.json, so the worlds have the real design's exact overlap
  (12 ordered pairs, 273 to 1,134 shared); no D, P or n value is read.)
  World: per cluster pair in the union, truth t ~ N(0,1); per language group g, u_g ~ N(0,1) per
  cluster pair; per corpus P ~ N(0,1), e ~ N(0,1);
    D_c = CORE t + BONUS u_{g(c)} + CULT P_c + e,  CORE 0.40, CULT 0.42,
  chosen so that with no bonus pooled b_other is about 0.12 and b_prox about 0.36, the real sizes.
  The groups g are the LANGUAGE pairing unless stated. BONUS 0.30 plants DELTA of about 0.06 (= M);
  BONUS 0.42 plants DELTA of about 0.12 (a same-language core twice the cross-language one). The
  realised mean DELTA per world type is reported.
  F0: draws() pooled over 12 equals invariance.cross on one synthetic world (point exactly, interval
      to 1e-9), so the instrument is invariance.py's.
  F1 CALIBRATION, no bonus (20 worlds): a WITHIN-family verdict (either WITHIN string) in <= 2 of 20.
      NO LANGUAGE DIFFERENCE rate reported (equivalence power).
  F2 POWER, BONUS 0.42 on the language pairing (20 worlds): CORE IS LARGER WITHIN A LANGUAGE in
      >= 16 of 20. BONUS 0.30 (20 worlds): reported, not governing.
  F3 SPECIFICITY AND DIRECTION, BONUS 0.42 planted on ALT-1 (20 worlds): the language pairing then
      carries none of the bonus and its DELTA should be negative. CORE IS LARGER WITHIN A LANGUAGE in
      <= 2 of 20 (governing); the share reading NOT SPECIFIC or ACROSS is reported.
  FLOOR PASSES if F0, F1 and F3 hold (calibration); F2 is the power check (see the floor rules).
  Floor draws: 500 per world (not 2,000), as no_xes.py and linking.py. The real run uses 2,000.

WHAT IT CAN AND CANNOT SAY. It says whether b_other is larger between the two corpora that share a
language than across languages, and whether that pairing stands out from the two other ways of pairing
four corpora. Language here is confounded with region and national tradition (US/UK, mainland
China/Taiwan), and with the mapper's reading of each language; there are two language pairs, so it is
one contrast on four corpora, not a dose-response over linguistic distance.

RUN RECORD (2026-10-08; design committed at fb8cd9e, nothing changed after it). The floor ran first
(41fe7a4): F0 true; calibration passes (a within-language verdict in 0 of 20 bonus-free worlds and 0
of 20 worlds with the bonus on ALT-1); power fails, 15 of 20 at a planted DELTA of about 0.11 against
the bar of 16, and NO LANGUAGE DIFFERENCE was reached in only 3 of 20 bonus-free worlds. Then
`analyse` ran once; R0 reproduced the committed invariance interval. Results: README.md and
out/language-split-result.json.

    python3 language_split.py --synthetic   # floor -> out/language-split-synthetic.json
    python3 language_split.py analyse       # needs the floor; -> out/language-split-result.json
"""

from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies" / "identifiability" / "core-vs-culture"))
sys.path.insert(0, str(ROOT / "studies" / "identifiability" / "core-vs-culture-linking"))
import invariance as inv  # noqa: E402
import linking  # noqa: E402

OUT = HERE / "out"
INV_OUT = ROOT / "studies" / "identifiability" / "core-vs-culture" / "out"
LINK_OUT = ROOT / "studies" / "identifiability" / "core-vs-culture-linking" / "out"
DRAWS, FLOOR_DRAWS, FLOOR_WORLDS = 2000, 500, 20
M = 0.0625
CORE, CULT = 0.40, 0.42
PAIRINGS = {
    "LANGUAGE": (("xes3g5m", "junyi2020"), ("assistments2012", "eedi")),
    "ALT-1": (("xes3g5m", "assistments2012"), ("eedi", "junyi2020")),
    "ALT-2": (("xes3g5m", "eedi"), ("assistments2012", "junyi2020")),
}
WITHIN = ("CORE IS LARGER WITHIN A LANGUAGE", "WITHIN-LANGUAGE EXCESS, NOT SPECIFIC TO LANGUAGE")


def group_of(pairing):
    return {c: i for i, pr in enumerate(PAIRINGS[pairing]) for c in pr}


def is_same(reg, pairing):
    c, c2 = reg.split("<-")
    g = group_of(pairing)
    return g[c] == g[c2]


# ---------------------------------------------------------------- instrument

def draws(stats, rng, n=DRAWS):
    """invariance.py's joint bootstrap and permutation (CHANGE 1), keeping each ordered pair's b_other
    per draw. Consumes rng exactly as invariance.cross / linking.cross_multi do."""
    per = linking._regressions(stats)
    regs = list(per)
    union = sorted(set().union(*per.values()))
    uidx = {k: i for i, k in enumerate(union)}
    corp_keys = {c: list(stats[c]) for c in stats}
    corp_vals = {c: [stats[c][x]["D"] for x in corp_keys[c]] for c in stats}
    corp_pos = {c: {k: i for i, k in enumerate(corp_keys[c])} for c in stats}
    R = {}
    for k in regs:
        c, c2 = k.split("<-")
        keys = per[k]
        R[k] = {"c2": c2, "u": np.array([uidx[x] for x in keys]),
                "y": np.array([stats[c][x]["D"] for x in keys]),
                "x1": np.array([stats[c2][x]["D"] for x in keys]),
                "x2": np.array([stats[c][x]["P"] for x in keys]),
                "pos2": np.array([corp_pos[c2][x] for x in keys])}
    point = np.array([linking.fit("ols", R[k]["y"], R[k]["x1"], R[k]["x2"]) for k in regs])  # (12, 2)
    B = np.full((n, len(regs)), np.nan)
    BP = np.full((n, len(regs)), np.nan)
    N = np.full((n, len(regs)), np.nan)
    for d in range(n):
        cnt = np.bincount(rng.integers(0, len(union), len(union)), minlength=len(union))
        for j, k in enumerate(regs):
            w = cnt[R[k]["u"]]
            if w.sum() >= 3:
                idx = np.repeat(np.arange(len(w)), w)
                b = linking.fit("ols", R[k]["y"][idx], R[k]["x1"][idx], R[k]["x2"][idx])
                B[d, j], BP[d, j] = b
        perm = {c: rng.permutation(corp_vals[c]) for c in stats}
        for j, k in enumerate(regs):
            x1 = perm[R[k]["c2"]][R[k]["pos2"]]
            N[d, j] = linking.fit("ols", R[k]["y"], x1, R[k]["x2"])[0]
    return {"regs": regs, "n_shared": {k: len(per[k]) for k in regs}, "union": len(union),
            "point": point, "B": B, "BP": BP, "N": N}


def ci(v):
    v = np.asarray(v, float)
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def split(dr, pairing):
    regs = dr["regs"]
    same = np.array([is_same(k, pairing) for k in regs])
    p = dr["point"][:, 0]
    s, x = float(p[same].mean()), float(p[~same].mean())
    Bs, Bx = np.nanmean(dr["B"][:, same], axis=1), np.nanmean(dr["B"][:, ~same], axis=1)
    return {"same_pairs": [k for k in regs if is_same(k, pairing)], "b_same": s, "b_cross": x, "delta": s - x,
            "_Bs": Bs, "_Bx": Bx, "_Bd": Bs - Bx, "_mask": same}


def summarise(dr):
    sp = {name: split(dr, name) for name in PAIRINGS}
    L = sp["LANGUAGE"]
    alt_d = np.column_stack([sp["ALT-1"]["_Bd"], sp["ALT-2"]["_Bd"]])
    spec = L["_Bd"] - alt_d.max(axis=1)
    spec_neg = L["_Bd"] - alt_d.min(axis=1)
    p_alt = [sp["ALT-1"]["delta"], sp["ALT-2"]["delta"]]
    pooled_draw = np.nanmean(dr["B"], axis=1)
    pooled = float(dr["point"][:, 0].mean())
    null_cross = dr["N"][:, ~L["_mask"]].mean(axis=1)
    allD = np.column_stack([sp[n]["_Bd"] for n in PAIRINGS])
    rank_lang = (allD > allD[:, [0]]).sum(axis=1)  # 0 = language pairing largest
    out = {
        "pooled_b_other": pooled, "pooled_b_other_ci": ci(pooled_draw),
        "b_same": L["b_same"], "b_same_ci": ci(L["_Bs"]),
        "b_cross": L["b_cross"], "b_cross_ci": ci(L["_Bx"]),
        "b_cross_null_975": float(np.percentile(null_cross, 97.5)),
        "delta": L["delta"], "delta_ci": ci(L["_Bd"]),
        "share_of_pooled_core": L["delta"] / 3 / pooled, "share_of_pooled_core_ci": ci(L["_Bd"] / 3 / pooled_draw),
        "spec": L["delta"] - max(p_alt), "spec_ci": ci(spec),
        "spec_neg": L["delta"] - min(p_alt), "spec_neg_ci": ci(spec_neg),
        "language_rank_share": {"first": float(np.mean(rank_lang == 0)), "second": float(np.mean(rank_lang == 1)),
                                "third": float(np.mean(rank_lang == 2))},
        "pairings": {n: {"pairs": [list(p) for p in PAIRINGS[n]], "same_ordered_pairs": sp[n]["same_pairs"],
                         "b_same": sp[n]["b_same"], "b_same_ci": ci(sp[n]["_Bs"]),
                         "b_cross": sp[n]["b_cross"], "delta": sp[n]["delta"], "delta_ci": ci(sp[n]["_Bd"])}
                     for n in PAIRINGS},
    }
    regs = dr["regs"]
    per = {}
    for i, k in enumerate(regs):
        per[k] = {"n_shared": dr["n_shared"][k], "b_other": float(dr["point"][i, 0]), "b_prox": float(dr["point"][i, 1]),
                  "b_other_ci": ci(dr["B"][:, i]), "same_language": bool(L["_mask"][i])}
    out["per_ordered_pair"] = per
    unordered = {}
    for i, k in enumerate(regs):
        c, c2 = k.split("<-")
        u = "|".join(sorted((c, c2)))
        if u in unordered:
            continue
        j = regs.index(f"{c2}<-{c}")
        unordered[u] = {"mean_b_other": float((dr["point"][i, 0] + dr["point"][j, 0]) / 2),
                        "ci": ci((dr["B"][:, i] + dr["B"][:, j]) / 2), "same_language": bool(L["_mask"][i])}
    out["per_unordered_pair"] = unordered
    out["verdict_rule_output"] = verdict(out)
    out["cross_language_core"] = ("CROSS-LANGUAGE CORE HOLDS" if out["b_cross_ci"][0] > 0 and
                                  out["b_cross"] > out["b_cross_null_975"] else "CROSS-LANGUAGE CORE NOT SHOWN")
    return out


def verdict(o):
    lo, hi = o["delta_ci"]
    if lo > 0:
        return WITHIN[0] if o["spec_ci"][0] > 0 else WITHIN[1]
    if hi < 0:
        return ("CORE IS LARGER ACROSS LANGUAGES" if o["spec_neg_ci"][1] < 0
                else "CROSS-LANGUAGE EXCESS, NOT SPECIFIC TO LANGUAGE")
    if lo >= -M and hi <= M:
        return "NO LANGUAGE DIFFERENCE"
    return "UNDERPOWERED"


def strip(d):
    if isinstance(d, dict):
        return {k: strip(v) for k, v in d.items() if not k.startswith("_")}
    return d


# ---------------------------------------------------------------- floor

def key_structure():
    """Which cluster-pair keys each corpus holds, and whether P is defined. No values."""
    st = json.loads((INV_OUT / "invariance-pairs.json").read_text())
    return {c: {k: (v["P"] is not None) for k, v in st[c].items()} for c in inv.CORPORA}


def world(rng, ks, bonus, pairing="LANGUAGE", core=CORE, cult=CULT):
    union = sorted(set().union(*[set(v) for v in ks.values()]))
    truth = rng.normal(size=len(union))
    u = rng.normal(size=(2, len(union)))
    pos = {k: i for i, k in enumerate(union)}
    g = group_of(pairing)
    stats = {}
    for c in inv.CORPORA:
        names = sorted(ks[c])
        ix = np.array([pos[k] for k in names])
        P = rng.normal(size=len(names))
        D = core * truth[ix] + bonus * u[g[c], ix] + cult * P + rng.normal(size=len(names))
        stats[c] = {k: {"n": 500, "D": float(D[i]), "P": float(P[i]) if ks[c][k] else None, "O": 0.5}
                    for i, k in enumerate(names)}
    return stats


def synthetic():
    rng = np.random.default_rng(inv.SEED + 47)
    out = {"draws_per_world": FLOOR_DRAWS, "worlds_per_cell": FLOOR_WORLDS, "core": CORE, "culture": CULT, "M": M}
    t0 = time.time()
    ks = key_structure()
    # F0: draws() pooled over all regressions is invariance.cross.
    w = world(rng, ks, 0.3)
    a = inv.cross(w, np.random.default_rng(11))
    dr = draws(w, np.random.default_rng(11), n=2000)
    pd_ = np.nanmean(dr["B"], axis=1)
    f0 = (abs(a["pooled_b_other"] - dr["point"][:, 0].mean()) < 1e-12 and
          max(abs(x - y) for x, y in zip(a["b_other_ci"], ci(pd_))) < 1e-9 and
          abs(a["null_b_other_975"] - float(np.percentile(dr["N"].mean(axis=1), 97.5))) < 1e-9)
    out["F0_draws_equals_invariance_cross"] = bool(f0)
    out["structure"] = {"ordered_pairs": len(dr["regs"]), "n_shared": dr["n_shared"], "union": dr["union"]}
    print("F0:", f0, f"({time.time() - t0:.0f}s)", flush=True)
    cells = {"F1 no bonus": (0.0, "LANGUAGE"), "F2 bonus 0.42 on language": (0.42, "LANGUAGE"),
             "F2 bonus 0.30 on language": (0.30, "LANGUAGE"), "F3 bonus 0.42 on ALT-1": (0.42, "ALT-1")}
    res = {}
    for name, (bonus, pairing) in cells.items():
        vs, deltas, bcross, pooled = Counter(), [], [], []
        for _ in range(FLOOR_WORLDS):
            s = summarise(draws(world(rng, ks, bonus, pairing), np.random.default_rng(rng.integers(1 << 30)), n=FLOOR_DRAWS))
            vs[s["verdict_rule_output"]] += 1
            deltas.append(s["delta"])
            bcross.append(s["b_cross"])
            pooled.append(s["pooled_b_other"])
        res[name] = {"verdicts": dict(vs), "mean_delta_language": float(np.mean(deltas)),
                     "mean_b_cross": float(np.mean(bcross)), "mean_pooled_b_other": float(np.mean(pooled))}
        print(f"  {name:<28} {dict(vs)} mean DELTA {np.mean(deltas):+.3f} pooled {np.mean(pooled):+.3f} "
              f"({time.time() - t0:.0f}s)", flush=True)
    out["worlds"] = res
    n_within = lambda cell: sum(v for k, v in res[cell]["verdicts"].items() if k in WITHIN)
    f1 = n_within("F1 no bonus") <= 2
    f3 = res["F3 bonus 0.42 on ALT-1"]["verdicts"].get(WITHIN[0], 0) <= 2
    f2 = res["F2 bonus 0.42 on language"]["verdicts"].get(WITHIN[0], 0) >= 16
    out["F1"] = {"within_family_of_20": n_within("F1 no bonus"), "passes": f1,
                 "no_language_difference_of_20": res["F1 no bonus"]["verdicts"].get("NO LANGUAGE DIFFERENCE", 0)}
    out["F2"] = {"found_of_20_at_0.42": res["F2 bonus 0.42 on language"]["verdicts"].get(WITHIN[0], 0),
                 "found_of_20_at_0.30": res["F2 bonus 0.30 on language"]["verdicts"].get(WITHIN[0], 0), "passes": f2}
    out["F3"] = {"false_within_language_of_20": res["F3 bonus 0.42 on ALT-1"]["verdicts"].get(WITHIN[0], 0),
                 "any_within_family_of_20": n_within("F3 bonus 0.42 on ALT-1"), "passes": f3}
    out["calibration_passes"] = bool(f0 and f1 and f3)
    out["power_passes"] = bool(f2)
    OUT.mkdir(exist_ok=True)
    (OUT / "language-split-synthetic.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"FLOOR calibration {'PASSES' if out['calibration_passes'] else 'FAILS'}; power "
          f"{'PASSES' if f2 else 'FAILS'} ({time.time() - t0:.0f}s)")


# ---------------------------------------------------------------- real run

def analyse():
    fpath = OUT / "language-split-synthetic.json"
    if not fpath.exists():
        raise SystemExit("run --synthetic first: the floor governs the verdict")
    floor = json.loads(fpath.read_text())
    committed = json.loads((INV_OUT / "invariance-result.json").read_text())
    st = json.loads((INV_OUT / "invariance-pairs.json").read_text())
    t0 = time.time()
    dr = draws(st, np.random.default_rng(inv.SEED))
    prim = summarise(dr)
    cc = committed[inv.MAPPER]["cross"]
    r0 = (abs(prim["pooled_b_other"] - cc["pooled_b_other"]) < 1e-12 and
          max(abs(x - y) for x, y in zip(prim["pooled_b_other_ci"], cc["b_other_ci"])) < 1e-9 and
          abs(float(np.percentile(dr["N"].mean(axis=1), 97.5)) - cc["null_b_other_975"]) < 1e-9)
    print(f"primary ({time.time() - t0:.0f}s); R0 reproduces invariance-result.json: {r0}", flush=True)
    read = prim["verdict_rule_output"]
    v = read
    if not floor["calibration_passes"] or not r0:
        v = f"UNANSWERABLE (floor or R0 failed; read would have been: {read})"
    elif not floor["power_passes"] and read == "NO LANGUAGE DIFFERENCE":
        v = "UNDERPOWERED"
    prim["verdict"] = v
    st2 = json.loads((LINK_OUT / "linking-pairs.json").read_text())[f"{inv.MAPPER2} | cluster"]
    sec = summarise(draws(st2, np.random.default_rng(inv.SEED)))
    res = {"verdict": v, "floor": {"calibration_passes": floor["calibration_passes"], "power_passes": floor["power_passes"]},
           "R0_reproduces_invariance": bool(r0), "M": M, "primary_map": strip(prim),
           "second_map_descriptive": strip(sec),
           "four_corpus_committed": {k: cc[k] for k in ("verdict", "pooled_b_other", "b_other_ci", "null_b_other_975")},
           "map_status": ("model-coded from names (openai/gpt-6-sol primary; deepseek/deepseek-v4-pro second); blind "
                          "human check MAP VALIDATED narrowly, kappa 0.606 [0.493, 0.709], 87 items, coder "
                          "human:david-porcaro"),
           "point_estimate_blind": False}
    OUT.mkdir(exist_ok=True)
    (OUT / "language-split-result.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
    for nm, s in (("primary", prim), ("second", sec)):
        print(nm, s["verdict_rule_output"], json.dumps({k: s[k] for k in (
            "b_same", "b_same_ci", "b_cross", "b_cross_ci", "b_cross_null_975", "delta", "delta_ci", "spec", "spec_ci",
            "spec_neg", "spec_neg_ci", "language_rank_share", "cross_language_core")}))
        for n, p in s["pairings"].items():
            print(f"   {n:<9} s {p['b_same']:+.4f} {p['b_same_ci']} DELTA {p['delta']:+.4f} {p['delta_ci']}")
    print("VERDICT:", v)


if __name__ == "__main__":
    {"--synthetic": synthetic, "analyse": analyse}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
