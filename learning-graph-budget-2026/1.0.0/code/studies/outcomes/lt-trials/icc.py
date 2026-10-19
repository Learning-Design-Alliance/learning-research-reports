"""
Class ICC of the Clements-Sarama learning-trajectory trials, for the edge-release power statement.

Handover 2026-10-09 (docs/handover/2026-10-09-restricted-datasets.md), Task 3; literature review strand
4, "Analyses" items 2 and 7 (research/readiness/learning-graph-budget-2026/literature.md). Paper II's
edge-release sample size (studies/outcomes/order-swap-remnant/out/power.json) uses a class ICC of 0.096
[0.057, 0.136] from one ASSISTments experiment and, for classrooms, Hedges & Hedberg's SCHOOL-level
planning values rho 0.15-0.25, because these trials were not on disk. This study estimates the class
ICC the trials' own data imply and says, by a rule fixed here, whether it replaces those borrowed values.

PRE-REGISTRATION. Written 2026-10-08, before any outcome value of any of the three deposits was read
in this session. What had been read before writing it: the codebooks (READ ME FIRST.docx of 151741 and
168846; Unit 6 Length Codebook and the Variables tab of 168361), the header row and row count of every
sheet, and nothing else. One disclosure: length_order.py (2026-09-24) already fitted 151741's posttest,
and out/length_order.json publishes its arm SDs (LT 1.239, REV 0.752, BAU 0.724) and the arm effects.
That study never computed or printed a class variance component or an ICC. Its arm SDs and the
heavy LT tail it reported shape the detection floor below; they are the only outcome-derived facts used
before the run.

WHAT THE THREE DEPOSITS ARE (codebooks and headers; studies/outcomes/lt-trials/README.md)
  151741  length measurement, LT vs REV vs BAU, 187 kindergartners, 16 classrooms, randomised to arm
          WITHIN class at pre-assessment. File: C6 Analysis File.xlsx, sheet 'Analysis File'.
  168361  the SAME length trial: a 133-column version of the C6 file (SID, Class, Condition, item
          responses, total scores, Rasch scores; also race, language and assessor columns, never read).
          Codebook says 187 children, 16 classrooms, LT 71 / REV 59 / BAU 57, as 151741.
  168846  a 26-child arithmetic pilot, LT vs SKIP (teach to target), "two classes: the intervention (LT)
          class (n = 13), teaching to the target (SKIP) class (n = 13). Class 1 was randomly assigned
          to the LT treatment." Class IS arm: one cluster per arm.

OUTCOME PER TRIAL (each deposit's own posttest score, chosen from the codebooks)
  151741  Theta_post_1pl: "STATA 15.1 generated theta score with one parameter Rasch model", the outcome
          of the authors' own model (C6 Analysis Syntax.R). Read through length_order.load (reused).
  168361  TotalPostCorrect (codebook name Total_Post, "Total correct score for each student"): the
          deposit's raw posttest sum over the 26 items. The codebook's description of it repeats
          PRE_TotalR's statistics verbatim ("range from 0 to 20, mean 6.95, S.D. 3.3"), so the run
          prints its observed range and does not trust the codebook's. PostTheta_1pl is also read, only
          for the identity check below.
  168846  Post-Assessment_Mastery_Level. NOT READ: the trial is unanswerable by design (below), so its
          outcome is never opened. Its Race, Ethnicity and DoB columns are never read either.

UNITS AND INDEPENDENCE (decided before the run)
  168361 is not an independent trial unless its children differ from 151741's. Identity check (no
  outcomes): SID, Class and Condition of every child, matched on SID. If every SID matches with the same
  Class and Condition, 168361 is the SAME TRIAL: verdict "NOT A SEPARATE TRIAL"; its TotalPostCorrect
  ICC is reported only as a scoring sensitivity (Rasch theta vs raw sum on the same children) and never
  pooled with 151741. If the identity check fails it is analysed as its own trial under the same rules.
  At run time the posttest scores are also compared (PostTheta_1pl vs 151741's Theta_post_1pl,
  max |difference| on matched SIDs), reported, not used for any verdict.

ICC ESTIMATOR (one per trial, fixed)
  Outcome centred by arm (each child's posttest minus its arm mean), so the class component is net of
  the randomised treatment. Arms are randomised within class, so class and arm are not confounded.
  One-way random-effects ANOVA ICC over Class, unbalanced form (n0 = (N - sum n_j^2 / N) / (k - 1)),
  rho = (MSB - MSW) / (MSB + (n0 - 1) MSW); the same function as order-swap-remnant (remnant.py
  icc_oneway), copied so this study is self-contained. Signed: a negative estimate is reported as
  negative and floored at 0 only where it enters a sample-size formula (as remnant.py does).
  Interval: 90% interval over 2,000 bootstrap draws that resample CLASSES with replacement (each drawn
  class keeps all its children, relabelled so a class drawn twice is two classes). 90% matches
  power.json's intervals. The class is the unit; children are never resampled singly.
    v1 (as first registered): the PERCENTILE interval. It FAILED the synthetic floor on 151741's
       structure: coverage 0.777 (NORMAL) and 0.767 / 0.790 (NORMAL / TAIL) at planted rho 0.20 and
       0.30, against the 0.80 required (first --floor run, 2026-10-08, before any outcome was read; the
       percentile results are kept in out/icc-floor.json beside v2's).
    v2 (registered after that synthetic failure, before any outcome was read; FINAL): BCa over the
       same class-bootstrap draws (bias correction z0 from the share of draws below the estimate;
       acceleration from the leave-one-CLASS-out jackknife). Chosen on principle, not by trying
       several: the percentile interval's undercoverage with 16 clusters comes from the ANOVA ICC's
       skewed, bias-prone sampling distribution, which is what BCa corrects. No v3: if v2 fails the
       floor, the trial is UNANSWERABLE: FLOOR FAILED. The floor's thresholds are unchanged.
  Children with a missing posttest are dropped (arm means computed after dropping).
  Clustering test: one-sided permutation p for ICC > 0, permuting children's class labels WITHIN ARM
  (arm-by-class counts kept), 2,000 permutations. Children are the units whose class membership the
  null says is exchangeable; arm is held fixed because it was assigned.
  With pretest (for H&H's eta_B, eta_W): residual of OLS posttest ~ arm + PreTheta_1pl (pooled slope),
  same ANOVA on the residual, on children with both scores. eta_B = sigma2_B(cond) / sigma2_B(uncond)
  and eta_W = sigma2_W(cond) / sigma2_W(uncond), both components from the same complete-case set.
  If sigma2_B(uncond) <= 0, eta_B is undefined and set to 1 (no class-level gain assumed).
  Ceiling: posttest reliability = 1 - mean(SE^2) / Var(theta) with Theta_SE_post_1pl (151741), printed
  beside the ICC with the implied true-score ICC = rho / reliability. Measurement error inflates the
  within-class variance only, so the observed ICC is the one a trial measured the same way would face;
  the power table uses the observed ICC.

MINIMUM CLASSES. A trial with fewer than 10 classes, or whose classes are confounded with arm (any class
  holding one arm only while arm is assigned by class, so the arm-centred class means are fixed at zero),
  is UNANSWERABLE. 10: below it the between-class mean square has fewer than 9 df and an ANOVA ICC's
  sampling SD exceeds the 0.10-0.25 range being planned for. 168846 (2 classes, class = arm) is
  UNANSWERABLE on both counts before any outcome is read; its floor is still run, to show it.

DETECTION FLOOR (part 1; synthetic only, runs and is committed before the run)
  Per trial, synthetic data with that trial's class count, class sizes and arm-by-class counts (read
  from SID/Class/Condition only). y = arm effect + u_class + e, u ~ N(0, rho), e scaled to within
  variance 1 - rho, planted rho in {0, 0.05, 0.10, 0.20, 0.30}. Two shapes: NORMAL (homoscedastic
  normal e) and TAIL (e from t with 5 df, scaled to unit variance, with arm-specific SDs in the ratio
  length_order.json reports, LT 1.239 : REV 0.752 : BAU 0.724, normalised so the child-weighted mean
  within variance is 1 - rho). Arm effects LT +0.58, REV +0.27, BAU 0 (length_order.json) are planted
  and must be removed by the arm-centring. 300 replicates per setting, 1,000 class-bootstrap draws each
  (the real run uses 2,000), 300 within-arm permutations for the null rejection rate.
  PASS for a trial iff, in BOTH shapes:
    coverage    the 90% class-bootstrap interval contains the planted rho in >= 0.80 of replicates at
                every planted rho in {0.05, 0.10, 0.20, 0.30} (at 0 the truth is on the boundary of the
                parameter space and coverage is reported, not required);
    bias        |mean estimate - planted rho| <= 0.05 at every planted rho;
    null        the permutation test rejects at 0.05 in <= 0.10 of replicates at rho = 0.
  Also reported, not required: mean interval width per rho and the share of replicates whose lower
  bound exceeds 0 (the power to see clustering).
  A trial that fails the floor is UNANSWERABLE: FLOOR FAILED, and its real ICC is not read.
  Arithmetic floor: the sample-size formula below must reproduce power.json's committed numbers
  (e.g. H&H rho 0.15, m = 13, d = 0.10 -> 339 classes per arm) before any new number is printed.

VERDICTS (per trial; strings fixed)
  "UNANSWERABLE: CLASS CONFOUNDED WITH ARM" | "UNANSWERABLE: FEWER THAN 10 CLASSES" |
  "UNANSWERABLE: FLOOR FAILED" | "NOT A SEPARATE TRIAL" | "CLASS ICC ESTIMATED", the last qualified by:
    vs Hedges & Hedberg 0.15-0.25: "BELOW H&H RANGE" if hi90 < 0.15; "ABOVE H&H RANGE" if lo90 > 0.25;
       else "OVERLAPS H&H RANGE";
    vs ASSISTments 0.096: "BELOW ASSISTMENTS" if hi90 < 0.096; "ABOVE ASSISTMENTS" if lo90 > 0.096;
       else "CONSISTENT WITH ASSISTMENTS";
    precision: "PRECISE ENOUGH TO REPLACE" if hi90 - lo90 <= 0.20, else "TOO IMPRECISE TO REPLACE".
  All comparisons signed (hi90 < x, lo90 > x), never on abs().

HOW IT FEEDS THE POWER TABLE (order-swap-remnant/out/power.json; its files are not touched)
  Same formula as remnant.py: two arms, equal allocation, two-sided alpha 0.05, power 0.80, normal
  approximation, Z = z_.975 + z_.80; classes per arm J = 2 Z^2 / d^2 * [rho eta_B + (1 - rho) eta_W / m],
  d in {0.05, 0.10, 0.30} outcome SD, m in {13 (power.json's median participant class), 20, this
  trial's median class size}. Rows: this trial's rho at the point estimate, lo90 and hi90 (each floored
  at 0) without a pretest (eta_B = eta_W = 1), and at the point estimate with the pretest (realized
  eta_B, eta_W). Written to THIS study's out/icc-power.json, beside power.json's own rows for comparison.
  Replacement rule: if the length trial's verdict is CLASS ICC ESTIMATED and PRECISE ENOUGH TO REPLACE,
  its point estimate replaces H&H 0.15-0.25 as the classroom planning value ("REPLACES PLANNING
  VALUES"). Otherwise "PLANNING VALUES STAND": H&H 0.15-0.25 remain the classroom basis; this trial's
  rows are printed as a sensitivity, and if its hi90 exceeds 0.25 the hi90 row is named the
  conservative case. Either way the ASSISTments 0.096 rows are unchanged (a different population and
  outcome).

POOLING (literature strand 4, items 2 and 7)
  Rule: pool only INDEPENDENT trials (no shared children) that each reach CLASS ICC ESTIMATED, have the
  class as the cluster, and a posttest on the trained trajectory. Pool on the ICC scale by
  DerSimonian-Laird random effects with each trial's class-bootstrap variance. Fewer than two eligible
  trials -> "NOTHING TO POOL". Item 7's pooling of ORDER EFFECTS (patterning n = 16 and 48, shape
  n = 152, arithmetic n = 291 with the length trial) needs those trials' learner data, none of which
  is in these deposits; 168846 is LT vs skip (not a same-activity order contrast) with one class per
  arm and is excluded from both poolings by this rule. Recorded, not run.

    python3 icc.py --floor      # design stage: structure only, writes out/icc-floor.json
    python3 icc.py --run        # reads outcomes; refuses unless out/icc-floor.json exists
    python3 icc.py --floor-posthoc   # added after the run, see stage_floor_posthoc; changes no verdict

Data: $LDA_SCRATCH_DIR/lt-trials/ (registry id clements-sarama-lt; or --dir). AERA/ICPSR open data --
statistical analysis only, no re-identification. Raw files stay in the scratchpad; only aggregates are
written. Race, ethnicity, date of birth, language-proficiency and assessor columns are never read:
loaders select columns by header name before building any table. Nothing here is coded by a person or
a model; every construct is a deposit's own score.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import openpyxl
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
from shared.paths import scratch_root  # noqa: E402

OUT = HERE / "out"
SEED = 20261008
Z = float(norm.ppf(0.975) + norm.ppf(0.80))
RHOS = (0.0, 0.05, 0.10, 0.20, 0.30)
MIN_CLASSES = 10
ARM_EFFECT = {"LT": 0.58, "REV": 0.27, "BAU": 0.0, "SKIP": 0.0}
ARM_SD = {"LT": 1.239, "REV": 0.752, "BAU": 0.724}          # length_order.json post_sd_by_arm
FLOOR = {"coverage": 0.80, "bias": 0.05, "null_reject": 0.10}
HH = (0.15, 0.25)
ASSIST = 0.096
WIDTH_TO_REPLACE = 0.20
METHODS = ("percentile", "bca")
INTERVAL = "bca"            # v2; v1 (percentile) failed the synthetic floor, see the docstring

P151 = ("ICPSR_151741-V1.1", "AERA Open Depository", "C6 Analysis File.xlsx")
P168361 = ("ICPSR_168361-V2.1", "ICPSR Submission Materials", "LTS Combined C6 Analysis File -Aug2020.xlsx")
P168846 = ("ICPSR_168846-V1.1", "Collection 3 Unit 1 and Unit 2 Arithmetic Data Repository",
           "Pre and Post Assessment Mastery LT Level.xlsx")


# ------------------------------------------------------------------ loaders (named columns only)
def read_columns(path: Path, sheet: str, want: dict[str, str], key: str) -> list[dict]:
    """Rows of `sheet` holding only the columns named in `want` ({header: name}); others never kept."""
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    it = wb[sheet].iter_rows(values_only=True)
    hdr = [str(h).strip() if h is not None else "" for h in next(it)]
    idx = {name: hdr.index(h) for h, name in want.items()}
    rows = []
    for r in it:
        rec = {name: r[i] for name, i in idx.items()}
        if rec[key] is not None:
            rows.append(rec)
    return rows


def structure_151741(d: Path) -> list[dict]:
    return read_columns(d.joinpath(*P151), "Analysis File",
                        {"Student ID Number": "sid", "Class": "cls", "Condition": "arm"}, "sid")


def structure_168361(d: Path) -> list[dict]:
    return read_columns(d.joinpath(*P168361), "Analysis File",
                        {"SID": "sid", "Class": "cls", "Condition": "arm"}, "sid")


def structure_168846(d: Path) -> list[dict]:
    """ChildID and the sheet (= arm = class) only; the outcome column is not read."""
    rows = []
    for sheet in ("LT", "SKIP"):
        for r in read_columns(d.joinpath(*P168846), sheet, {"ChildID": "sid"}, "sid"):
            rows.append({"sid": r["sid"], "cls": sheet, "arm": sheet})
    return rows


# ------------------------------------------------------------------ estimator
def icc_oneway(y, g):
    """ANOVA ICC for unbalanced groups (groups of size 1 dropped). Same as order-swap-remnant."""
    labs, inv, cnt = np.unique(g, return_inverse=True, return_counts=True)
    keep = cnt[inv] >= 2
    y, inv = y[keep], inv[keep]
    labs, inv, cnt = np.unique(inv, return_inverse=True, return_counts=True)
    k, N = len(labs), len(y)
    means = np.bincount(inv, y) / cnt
    ssb = (cnt * (means - y.mean()) ** 2).sum()
    ssw = ((y - means[inv]) ** 2).sum()
    msb, msw = ssb / (k - 1), ssw / (N - k)
    n0 = (N - (cnt ** 2).sum() / N) / (k - 1)
    rho = (msb - msw) / (msb + (n0 - 1) * msw) if msb + (n0 - 1) * msw > 0 else float("nan")
    return float(rho), k, N, float((msb - msw) / n0), float(msw)


def arm_centre(y, arm):
    out = y.astype(float).copy()
    for a in np.unique(arm):
        m = arm == a
        out[m] = y[m] - y[m].mean()
    return out


def boot_icc(y, g, rng, draws):
    """90% percentile interval, resampling classes with replacement.

    Vectorised from per-class sufficient statistics (n_j, sum_j, within-SS_j); identical to calling
    icc_oneway on the stacked resampled children with each drawn class relabelled (classes of size 1
    are dropped first, as icc_oneway drops them)."""
    labs, inv, cnt = np.unique(g, return_inverse=True, return_counts=True)
    s = np.bincount(inv, y)
    ss = np.bincount(inv, y * y)
    keep = cnt >= 2
    n, s, ss = cnt[keep].astype(float), s[keep], ss[keep]
    sw = ss - s * s / n
    k = len(n)
    pick = rng.integers(0, k, (draws, k))
    N = n[pick].sum(1)
    S = s[pick].sum(1)
    ssb = (s[pick] ** 2 / n[pick]).sum(1) - S ** 2 / N
    ssw = sw[pick].sum(1)
    msb, msw = ssb / (k - 1), ssw / (N - k)
    n0 = (N - (n[pick] ** 2).sum(1) / N) / (k - 1)
    with np.errstate(invalid="ignore", divide="ignore"):
        vals = (msb - msw) / (msb + (n0 - 1) * msw)
    return vals[np.isfinite(vals)]


def jackknife_icc(y, g):
    """ICC with each class left out in turn (for the BCa acceleration)."""
    labs = np.unique(g)
    return np.array([icc_oneway(y[g != l], g[g != l])[0] for l in labs])


def interval(vals, est, jack, method):
    """90% interval from class-bootstrap draws: 'percentile' (v1) or 'bca' (v2, registered)."""
    if method == "percentile":
        return float(np.percentile(vals, 5)), float(np.percentile(vals, 95))
    share = np.clip((vals < est).mean() + 0.5 * (vals == est).mean(), 1e-6, 1 - 1e-6)
    z0 = norm.ppf(share)
    jack = jack[np.isfinite(jack)]
    dv = jack.mean() - jack
    den = 6 * (dv ** 2).sum() ** 1.5
    acc = (dv ** 3).sum() / den if den > 0 else 0.0
    qs = []
    for za in (norm.ppf(0.05), norm.ppf(0.95)):
        qs.append(100 * norm.cdf(z0 + (z0 + za) / (1 - acc * (z0 + za))))
    return float(np.percentile(vals, qs[0])), float(np.percentile(vals, qs[1]))


def perm_p(y, g, arm, rng, perms):
    """One-sided p for ICC > 0, class labels permuted among children within arm."""
    obs = icc_oneway(y, g)[0]
    blocks = [np.nonzero(arm == a)[0] for a in np.unique(arm)]
    hits = 0
    gp = g.copy()
    for _ in range(perms):
        for ix in blocks:
            gp[ix] = g[rng.permutation(ix)]
        hits += icc_oneway(y, gp)[0] >= obs
    return (hits + 1) / (perms + 1)


def estimate(y, g, arm, rng, draws=2000, perms=2000):
    yc = arm_centre(y, arm)
    rho, k, N, sb, sw = icc_oneway(yc, g)
    vals = boot_icc(yc, g, rng, draws)
    lo, hi = interval(vals, rho, jackknife_icc(yc, g), INTERVAL)
    plo, phi = interval(vals, rho, None, "percentile")
    return {"icc": rho, "lo90": lo, "hi90": hi, "interval": INTERVAL, "percentile_lo90_hi90_v1": [plo, phi],
            "classes": k, "children": N,
            "sigma2_between": sb, "sigma2_within": sw, "perm_p_icc_gt_0": perm_p(yc, g, arm, rng, perms)}


# ------------------------------------------------------------------ structure checks
def describe(rows):
    g = np.array([str(r["cls"]) for r in rows])
    arm = np.array([str(r["arm"]).strip() for r in rows])
    labs, cnt = np.unique(g, return_counts=True)
    arms_per_class = {l: sorted(set(arm[g == l])) for l in labs}
    confounded = all(len(v) == 1 for v in arms_per_class.values())
    return {"classes": len(labs), "class_sizes": sorted(int(c) for c in cnt),
            "median_class_size": float(np.median(cnt)),
            "arm_by_class": {l: {a: int(((g == l) & (arm == a)).sum()) for a in arms_per_class[l]}
                             for l in labs},
            "class_confounded_with_arm": confounded}, g, arm


def structural_verdict(desc):
    if desc["class_confounded_with_arm"]:
        return "UNANSWERABLE: CLASS CONFOUNDED WITH ARM"
    if desc["classes"] < MIN_CLASSES:
        return "UNANSWERABLE: FEWER THAN 10 CLASSES"
    return None


# ------------------------------------------------------------------ detection floor
def simulate(g, arm, rho, shape, rng):
    labs, inv = np.unique(g, return_inverse=True)
    u = rng.normal(0, math.sqrt(rho), len(labs))[inv]
    if shape == "NORMAL":
        e = rng.normal(0, 1, len(g))
        s = np.ones(len(g))
    else:
        e = rng.standard_t(5, len(g)) / math.sqrt(5 / 3)
        s = np.array([ARM_SD.get(a, 1.0) for a in arm])
        s = s / math.sqrt((s ** 2).mean())
    return np.array([ARM_EFFECT.get(a, 0.0) for a in arm]) + u + e * s * math.sqrt(1 - rho)


def run_floor(g, arm, rng, reps=300, draws=1000, perms=300, rhos=RHOS):
    res = {}
    for shape in ("NORMAL", "TAIL"):
        res[shape] = {}
        for rho in rhos:
            est, rej = [], 0
            cov = {m: 0 for m in METHODS}
            lo_pos = {m: 0 for m in METHODS}
            width = {m: [] for m in METHODS}
            for _ in range(reps):
                y = simulate(g, arm, rho, shape, rng)
                yc = arm_centre(y, arm)
                r = icc_oneway(yc, g)[0]
                vals = boot_icc(yc, g, rng, draws)
                jack = jackknife_icc(yc, g)
                est.append(r)
                for m in METHODS:
                    lo, hi = interval(vals, r, jack, m)
                    cov[m] += lo <= rho <= hi
                    lo_pos[m] += lo > 0
                    width[m].append(hi - lo)
                if rho == 0.0:
                    rej += perm_p(y, g, arm, rng, perms) < 0.05
            est = np.array(est, dtype=float)
            res[shape][str(rho)] = {"mean_estimate": float(np.nanmean(est)),
                                    "bias": float(np.nanmean(est) - rho),
                                    **{f"{m}": {"coverage90": cov[m] / reps, "share_lo90_above_0": lo_pos[m] / reps,
                                                "mean_width90": float(np.mean(width[m]))} for m in METHODS},
                                    **({"null_reject_rate": rej / reps} if rho == 0.0 else {})}
            print(f"   {shape:6s} rho {rho:.2f}: mean {np.nanmean(est):+.3f}  "
                  + "  ".join(f"{m}: cov {cov[m] / reps:.3f} width {np.mean(width[m]):.3f} lo>0 {lo_pos[m] / reps:.3f}"
                              for m in METHODS)
                  + (f"  null reject {rej / reps:.3f}" if rho == 0.0 else ""), flush=True)
    fails, fails_v1 = [], []
    for shape, rr in res.items():
        for rho, v in rr.items():
            if float(rho) > 0 and v[INTERVAL]["coverage90"] < FLOOR["coverage"]:
                fails.append(f"{shape} rho {rho}: coverage {v[INTERVAL]['coverage90']:.3f}")
            if float(rho) > 0 and v["percentile"]["coverage90"] < FLOOR["coverage"]:
                fails_v1.append(f"{shape} rho {rho}: percentile coverage {v['percentile']['coverage90']:.3f}")
            if not abs(v["bias"]) <= FLOOR["bias"]:
                fails.append(f"{shape} rho {rho}: bias {v['bias']:+.3f}")
        if "0.0" in rr and rr["0.0"]["null_reject_rate"] > FLOOR["null_reject"]:
            fails.append(f"{shape}: null rejection {rr['0.0']['null_reject_rate']:.3f}")
    return {"settings": res, "interval_registered": INTERVAL, "fails": fails, "pass": not fails,
            "v1_percentile_fails": fails_v1}


# ------------------------------------------------------------------ power arithmetic
def classes_per_arm(d, rho, m, eta_b=1.0, eta_w=1.0):
    rho = max(rho, 0.0)
    return math.ceil(2 * Z ** 2 / d ** 2 * (rho * eta_b + (1 - rho) * eta_w / m))


def arithmetic_floor():
    pw = json.loads((ROOT / "studies/outcomes/order-swap-remnant/out/power.json").read_text())
    checks = []
    for d in ("0.05", "0.1", "0.3"):
        for src, rho, eb, ew in (("hedges_hedberg_rho_0.15", 0.15, 1, 1), ("hedges_hedberg_rho_0.25", 0.25, 1, 1),
                                 ("hedges_hedberg_rho_0.239_pretest_etaB_0.210_etaW_0.360", 0.239, 0.210, 0.360),
                                 ("this_experiment_ptm_rho", pw["icc"]["problems_to_mastery_class"]["icc"], 1, 1)):
            for m in (13, 20):
                want = pw["sample_sizes"][d]["per_class"][src][f"m={m}"]["classes_per_arm"]
                got = classes_per_arm(float(d), rho, m, eb, ew)
                checks.append({"d": d, "source": src, "m": m, "power_json": want, "recomputed": got})
    ok = all(c["power_json"] == c["recomputed"] for c in checks)
    return {"pass": ok, "checks": checks}


# ------------------------------------------------------------------ stages
def data_dir(a) -> Path:
    return Path(a.dir) if a.dir else scratch_root() / "lt-trials"


def stage_floor(a):
    d = data_dir(a)
    rng = np.random.default_rng(SEED)
    out = {"date": "2026-10-08", "floor_rule": FLOOR, "planted_rhos": RHOS, "reps": 300,
           "boot_draws": 1000, "perms": 300, "trials": {}}
    s151, s168 = structure_151741(d), structure_168361(d)
    m151 = {int(r["sid"]): (str(r["cls"]), str(r["arm"]).strip()) for r in s151}
    m168 = {int(r["sid"]): (str(r["cls"]), str(r["arm"]).strip()) for r in s168}
    same = m151 == m168
    out["identity_168361_vs_151741"] = {
        "children_151741": len(m151), "children_168361": len(m168),
        "sids_in_both": len(set(m151) & set(m168)),
        "same_class_and_arm_for_every_sid": same}
    print(f"identity 168361 vs 151741 on SID/Class/Condition: {out['identity_168361_vs_151741']}")
    for name, rows in (("151741", s151), ("168361", s168), ("168846", structure_168846(d))):
        desc, g, arm = describe(rows)
        sv = structural_verdict(desc)
        print(f"\n{name}: {desc['classes']} classes, sizes {desc['class_sizes']}, confounded "
              f"{desc['class_confounded_with_arm']}  -> {sv or 'structure OK'}")
        if name == "168361" and same:
            out["trials"][name] = {**desc, "floor": "shared with 151741 (same children, classes and arms)",
                                   "structural_verdict": "NOT A SEPARATE TRIAL"}
            continue
        fl = run_floor(g, arm, rng)
        print(f"   FLOOR {'PASS' if fl['pass'] else 'FAIL'} {fl['fails']}")
        out["trials"][name] = {**desc, "floor": fl, "structural_verdict": sv}
    out["arithmetic_floor"] = arithmetic_floor()
    print(f"\narithmetic floor (power.json reproduced): {'PASS' if out['arithmetic_floor']['pass'] else 'FAIL'}")
    OUT.mkdir(exist_ok=True)
    (OUT / "icc-floor.json").write_text(json.dumps(out, indent=1) + "\n")


def with_pretest(y, pre, g, arm):
    """eta_B, eta_W: class and child variance components after posttest ~ arm + pretest, over before."""
    ok = np.isfinite(y) & np.isfinite(pre)
    y, pre, g, arm = y[ok], pre[ok], g[ok], arm[ok]
    X = np.column_stack([(arm == a).astype(float) for a in np.unique(arm)] + [pre])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ beta
    _, _, n, sb_u, sw_u = icc_oneway(arm_centre(y, arm), g)
    rho_c, _, _, sb_c, sw_c = icc_oneway(res, g)
    return {"children": int(n), "pretest_slope": float(beta[-1]), "icc_conditional": rho_c,
            "sigma2_between_uncond": sb_u, "sigma2_between_cond": sb_c,
            "sigma2_within_uncond": sw_u, "sigma2_within_cond": sw_c,
            "eta_B": float(sb_c / sb_u) if sb_u > 0 else 1.0, "eta_B_defined": bool(sb_u > 0),
            "eta_W": float(sw_c / sw_u)}


def trial_verdict(e):
    v = ["CLASS ICC ESTIMATED"]
    v.append("BELOW H&H RANGE" if e["hi90"] < HH[0] else "ABOVE H&H RANGE" if e["lo90"] > HH[1]
             else "OVERLAPS H&H RANGE")
    v.append("BELOW ASSISTMENTS" if e["hi90"] < ASSIST else "ABOVE ASSISTMENTS" if e["lo90"] > ASSIST
             else "CONSISTENT WITH ASSISTMENTS")
    v.append("PRECISE ENOUGH TO REPLACE" if e["hi90"] - e["lo90"] <= WIDTH_TO_REPLACE
             else "TOO IMPRECISE TO REPLACE")
    return v


def stage_run(a):
    import pandas as pd
    from length_order import load                     # the loader length_order.py uses, reused
    fl_path = OUT / "icc-floor.json"
    if not fl_path.is_file():
        raise SystemExit("out/icc-floor.json missing: run --floor and commit it first.")
    fl = json.loads(fl_path.read_text())
    d = data_dir(a)
    rng = np.random.default_rng(SEED + 1)
    out = {"date": "2026-10-08", "interval": f"90% {INTERVAL} over 2,000 class-bootstrap draws",
           "resamples": "classes (with replacement; children kept with their class)", "trials": {}}

    # ---- 151741: the length trial
    t = fl["trials"]["151741"]
    rec = {"classes": t["classes"], "class_sizes_all_children": t["class_sizes"],
           "median_class_size": t["median_class_size"], "floor_pass": t["floor"]["pass"]}
    sv = t["structural_verdict"] or (None if t["floor"]["pass"] else "UNANSWERABLE: FLOOR FAILED")
    D = load(d.joinpath(*P151)).dropna(subset=["Theta_post_1pl"])
    y = D.Theta_post_1pl.to_numpy(float)
    g = D.Class.astype(str).to_numpy()
    arm = D.Condition.astype(str).str.strip().to_numpy()
    if sv:
        rec["verdict"] = [sv]
    else:
        e = estimate(y, g, arm, rng)
        rec["outcome"] = "Theta_post_1pl (Rasch posttest theta, logits)"
        rec["estimate"] = e
        rec["class_sizes_with_posttest"] = sorted(int(c) for c in np.unique(g, return_counts=True)[1])
        rec["with_pretest"] = with_pretest(y, D.PreTheta_1pl.to_numpy(float), g, arm)
        se = pd.to_numeric(D.Theta_SE_post_1pl, errors="coerce").to_numpy(float)
        ok = np.isfinite(se)
        rel = float(1 - np.mean(se[ok] ** 2) / np.var(y[ok], ddof=1))
        rec["ceiling"] = {"posttest_reliability": rel, "true_score_icc": e["icc"] / rel,
                          "note": "1 - mean(SE^2)/Var(theta); measurement error inflates within-class variance only"}
        rec["verdict"] = trial_verdict(e)
        # direction check: the arm-centred class means must sum to ~0 within arm and the ICC is signed
        rec["sign_check"] = {"icc_signed": e["icc"], "sigma2_between_signed": e["sigma2_between"]}
        # POST HOC, descriptive, not registered: point ICC within arm subsets (the LT arm carries the tail)
        rec["post_hoc_descriptive_point_icc"] = {
            lab: icc_oneway(arm_centre(y[m], arm[m]), g[m])[0]
            for lab, m in (("BAU only", arm == "BAU"), ("REV only", arm == "REV"), ("LT only", arm == "LT"),
                           ("REV+BAU (LT dropped)", arm != "LT"))}
    out["trials"]["151741"] = rec
    print(json.dumps(rec, indent=1))

    # ---- 168361: same children? scoring sensitivity
    r68 = read_columns(d.joinpath(*P168361), "Analysis File",
                       {"SID": "sid", "Class": "cls", "Condition": "arm", "TotalPostCorrect": "tot",
                        "PostTheta_1pl": "theta"}, "sid")
    full = load(d.joinpath(*P151))
    m151 = dict(zip(full["Student ID Number"].astype(int), full.Theta_post_1pl))
    diffs = [abs(float(r["theta"]) - m151[int(r["sid"])]) for r in r68
             if r["theta"] not in (None, "") and int(r["sid"]) in m151 and np.isfinite(m151[int(r["sid"])])]
    tot = np.array([float(r["tot"]) if r["tot"] not in (None, "", "NA") else np.nan for r in r68])
    g68 = np.array([str(r["cls"]) for r in r68])
    a68 = np.array([str(r["arm"]).strip() for r in r68])
    okt = np.isfinite(tot)
    sens = estimate(tot[okt], g68[okt], a68[okt], rng)
    out["trials"]["168361"] = {
        "verdict": [fl["trials"]["168361"]["structural_verdict"]],
        "identity": {**fl["identity_168361_vs_151741"], "posttheta_matched": len(diffs),
                     "max_abs_diff_posttheta_vs_151741": float(max(diffs)) if diffs else None},
        "scoring_sensitivity_TotalPostCorrect": {**sens, "observed_range": [float(np.nanmin(tot)), float(np.nanmax(tot))],
                                                  "codebook_range_claimed": [0, 20]}}
    print(json.dumps(out["trials"]["168361"], indent=1))

    # ---- 168846: unanswerable by design; outcome never read
    t46 = fl["trials"]["168846"]
    out["trials"]["168846"] = {"classes": t46["classes"], "class_sizes": t46["class_sizes"],
                               "floor_pass": t46["floor"]["pass"], "verdict": [t46["structural_verdict"]],
                               "outcome_read": False}

    # ---- pooling
    eligible = [k for k, v in out["trials"].items() if v["verdict"][0] == "CLASS ICC ESTIMATED"]
    out["pooling"] = {"eligible_independent_trials": eligible,
                      "verdict": "NOTHING TO POOL" if len(eligible) < 2 else "POOLED",
                      "order_effect_pooling_item_7": "not run: the patterning, shape and arithmetic order "
                      "trials' learner data are not in these deposits"}
    (OUT / "icc.json").write_text(json.dumps(out, indent=1) + "\n")

    # ---- power feed
    if "estimate" not in rec:
        print("no estimate: power table not written")
        return
    e, wp = rec["estimate"], rec["with_pretest"]
    m_trial = float(np.median(np.unique(g, return_counts=True)[1]))
    ms = (13, 20, m_trial)
    pw = json.loads((ROOT / "studies/outcomes/order-swap-remnant/out/power.json").read_text())
    rows = {"length_trial_icc_point": (e["icc"], 1, 1), "length_trial_icc_lo90": (e["lo90"], 1, 1),
            "length_trial_icc_hi90": (e["hi90"], 1, 1),
            "length_trial_icc_point_with_pretest": (e["icc"], wp["eta_B"], wp["eta_W"])}
    table = {}
    for dd in (0.05, 0.10, 0.30):
        table[str(dd)] = {name: {f"m={m:g}": classes_per_arm(dd, rho, m, eb, ew) for m in ms}
                          for name, (rho, eb, ew) in rows.items()}
        table[str(dd)]["power_json_classroom_rows_m13_m20"] = {
            src: {k: v["classes_per_arm"] for k, v in vv.items()}
            for src, vv in pw["sample_sizes"][str(dd) if dd != 0.10 else "0.1"]["per_class"].items()}
    replaces = rec["verdict"][0] == "CLASS ICC ESTIMATED" and "PRECISE ENOUGH TO REPLACE" in rec["verdict"]
    power = {"formula": "J = 2 Z^2 / d^2 [rho eta_B + (1 - rho) eta_W / m]; two arms, alpha 0.05 two-sided, "
                        "power 0.80, normal approximation (as order-swap-remnant/remnant.py)",
             "Z": Z, "m_values": list(ms), "trial_median_class_size": m_trial,
             "rho_used": {k: max(v[0], 0.0) for k, v in rows.items()},
             "eta_B": wp["eta_B"], "eta_W": wp["eta_W"], "classes_per_arm": table,
             "replacement_rule_verdict": "REPLACES PLANNING VALUES" if replaces else "PLANNING VALUES STAND",
             "conservative_case": ("length_trial_icc_hi90" if (not replaces and e["hi90"] > HH[1]) else None),
             "source_not_modified": "studies/outcomes/order-swap-remnant/out/power.json"}
    (OUT / "icc-power.json").write_text(json.dumps(power, indent=1) + "\n")
    print(json.dumps(power, indent=1))


def stage_floor_posthoc(a):
    """POST HOC (added after --run): the estimate lay above the registered planted range (max 0.30).
    Same floor, same structure, planted rho 0.40 and 0.50. Reported beside the result; it changes no
    verdict, because the verdict rules were fixed before the run."""
    desc, g, arm = describe(structure_151741(data_dir(a)))
    fl = run_floor(g, arm, np.random.default_rng(SEED + 2), rhos=(0.40, 0.50))
    (OUT / "icc-floor-posthoc.json").write_text(json.dumps(
        {"post_hoc": True, "why": "real estimate 0.395 above the registered planted range (0-0.30)",
         "trial": "151741", **fl}, indent=1) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--floor", action="store_true")
    ap.add_argument("--floor-posthoc", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--dir", help="folder holding the unpacked ICPSR deposits (default $LDA_SCRATCH_DIR/lt-trials)")
    a = ap.parse_args()
    if a.floor:
        stage_floor(a)
    elif a.run:
        stage_run(a)
    elif a.floor_posthoc:
        stage_floor_posthoc(a)
    else:
        ap.error("--floor or --run")


if __name__ == "__main__":
    main()
