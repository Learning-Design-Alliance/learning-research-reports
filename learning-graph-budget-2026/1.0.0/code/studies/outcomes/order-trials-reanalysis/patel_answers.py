"""REGISTERED AMENDMENT (2026-10-08), NOT BLIND: Patel, Liu & Koedinger (2016) Study 2 on ds1190,
scored on the answer the learner typed.

WHY AN AMENDMENT. `patel_order.py` (registered at 901d14b, run unchanged at c5b4d91) fails on the
data. Each `T ...` test problem is logged as eight steps: five pre-filled givens (num1, den1,
operation1, num2, den2; 100% "correct", 0 s), the answer's num3 and den3 (the only responses), and an
ungraded ConfidenceRating (100% "incorrect"). Its step, problem and final-step scorings therefore do
not measure answers, and its delay counted in-test ComDen/Equiv rows as practice
(`patel_artefacts.py`, `out/patel_artefacts.json`, README section 2). This script scores the answer
only and measures the delay from the last practice-set row. Everything below is fixed before any
answer-level contrast between arms is computed. It is committed before the floor is run, and the
floor is committed before the real run.

WHAT IS NOT BLIND (stated here, in the README and in the history entry). This registration is made
  (a) after the logging artefact was found;
  (b) after the registered analysis's step-level per-arm outputs were seen (`out/patel_order.json`:
      e.g. DPosttest trained step accuracy AM 0.858, MA 0.863) and after the earlier
      `studies/outcomes/interleaving/ds1190_order.py` step-level estimate (d -0.43, MA better);
  (c) after rough arithmetic on committed aggregates (step accuracy = given share + answer share x
      answer accuracy, solved for answer accuracy) suggested answer accuracy near AM 0.70 / MA 0.78
      on the DPosttest and 0.68 / 0.78 on the Posttest (README section 2, point 5).
So the direction and rough size of the primary contrast were anticipated from the arithmetic. The
result is a REGISTERED BUT NON-BLIND re-analysis. The registration fixes the scoring, the tests, the
inference and the verdict strings so that they cannot be chosen after the exact numbers are seen; it
does not make the outcome a prediction. The reproduction check below is in particular not an
independent confirmation: the arithmetic already pointed at it.

DATA. DataShop ds1190 (research use, no redistribution; registry entry `datashop`, All Data MD5
e4d2ba2d7ba06be4fe080a7671f34e18). Reads the per-sample exports S2_AM_Blocked and S2_MA_Blocked under
scratch_root()/ds1190, which `patel_artefacts.py` ties row for row to the checksummed All Data file
(34,738 rows, 60 learners). Raw data stays in scratch; only aggregates go to out/. The loader is
`patel_order.load_arm`, unchanged; the re-randomisation is `patel_order.rerand_p`, unchanged.

SCORING (the only change of outcome).
  * A test problem is a learner x `T ...` problem within one test problem set. Its response is read
    from the earliest Problem View of that problem that logs a num3 or den3 row.
  * PRIMARY, answer correct: the problem is correct when BOTH num3 and den3 have First Attempt ==
    "correct" in that view. A missing num3 or den3 row in that view counts as not correct.
  * A problem presented (any row logged) but with no num3/den3 row in any view is UNANSWERED and
    scored 0 in the primary analysis. Sensitivity (reported, not used for verdicts): unanswered
    problems dropped.
  * SECONDARY, per-step answer score: mean over the problem's two answer fields of First Attempt ==
    "correct" (missing field = 0), i.e. 1, 0.5 or 0 per problem.
  * Givens and ConfidenceRating rows are never scored.
  * Item classes: TRAINED = addition and multiplication items (`T A.`, `T M.`; 8 per Pre/Post/
    DPosttest, 4 per Midtest); TRANSFER = subtraction and division (`T S.`, `T D.`; 4 per Pre/Post/
    DPosttest, 2 per Midtest), never practised. ALL = both, used only for the reproduction check
    and reported as secondary.
  * A learner's score on a test x class is the mean over the problems presented. A learner enters a
    test x class cell only with at least half that cell's items presented (4 of 8, 2 of 4, 1 of 2).
  * Arm mean = mean of learner scores. Contrast = mean(MA) - mean(AM), signed: positive means
    multiplication first is better.

PRIMARY CONTRAST (one). DPosttest, TRAINED items, primary answer scoring, MA - AM.
SECONDARY (reported with their own p; no verdict multiplicity correction; none can replace the
primary): Posttest trained; DPosttest and Posttest transfer; DPosttest and Posttest all items; the
per-step answer score for each of those; the unanswered-dropped sensitivity of the primary; the
delay contrast (within-learner DPosttest - Posttest change on trained items, MA - AM); a
pretest-adjusted primary (outcome minus b x Pretest trained score, b the pooled OLS slope fitted
without arm labels; learners lacking a Pretest dropped). Midtests A and B are reported descriptively
only: at Midtest A the two arms had practised different operations, so it is an exposure contrast,
not an order contrast. Pretest trained MA - AM is reported as a balance check.

DELAY. Per learner, from the last row in a practice problem set ("Fraction Arithmetic Blocked 1/2")
to the first row of each test, in days (as `patel_artefacts.py` measures it; the DPosttest median is
already known to be 3.98 days, range 3.97-4.97). Reported per test and per arm; descriptive.

INFERENCE.
  * Test: re-randomisation of arm labels across learners (the learner was the unit assigned; the
    export has no class column, so no strata), 10,000 relabellings keeping arm sizes, the observed
    labelling excluded, two-sided p (`patel_order.rerand_p`).
  * Interval: learner bootstrap within arm (resample learners with replacement inside AM and inside
    MA separately, arm sizes kept), 10,000 resamples, percentile 95% interval of MA - AM in
    proportion units; Cohen's d (pooled SD) with its bootstrap percentile interval alongside.
  * Seed 20261008.

DETECTION FLOOR (`--floor`, run and committed before the real run). Synthetic worlds shaped like this
experiment at the answer level, one floor per verdict cell (DPosttest and Posttest x TRAINED and
TRANSFER):
  * learners per arm as they appear in that cell of the real data (a count, not an outcome: the
    DPosttest has 27 AM + 29 MA test-takers, the Posttest 29 + 28), items per class as above;
  * answer correct ~ Bernoulli(logistic(c + theta_learner - b_item)), theta ~ N(0, sd_a), b_item ~
    N(0, 0.8) redrawn each world; c and sd_a calibrated on a grid so that the per-learner proportion
    correct has the POOLED mean and SD of that real cell. The pooled values are computed with arm
    labels discarded (both arms concatenated); they contain any true arm difference, which inflates
    the pooled SD by a negligible amount at the effects considered;
  * per-step score: a correct problem scores 1; an incorrect one scores 0 with probability q (both
    fields wrong) else 0.5, q the pooled share of incorrect answered problems with both fields
    wrong (arm labels discarded);
  * planted MA - AM = 0, +0.08 (the authors' printed 8 points) and +0.16, applied as a logit shift
    for MA solved so the expected difference in proportion equals the planted value;
  * 1,000 worlds per planted value, each tested with 2,000 relabellings (the same rerand_p) on the
    primary scoring and on the per-step score;
  * power = share of worlds with p < 0.05 AND MA - AM > 0 (right sign); wrong-sign rate = share with
    p < 0.05 AND MA - AM < 0.
  * PASS RULE per cell: false-positive rate at 0 <= 0.07, right-sign power at +0.16 >= 0.80, and
    wrong-sign rate <= 0.01 at +0.08 and +0.16. A cell that fails reads FLOOR FAILED (NO READING)
    whatever its p.
  The analytic MDE at 80% power for 27 + 29 learners is 2.802 x sqrt(1/27 + 1/29) = 0.75 SD.

VERDICTS (per verdict cell; the primary cell's is THE verdict; strings fixed here):
  * FLOOR FAILED (NO READING)               the cell's floor failed its pass rule.
  * MULTIPLICATION FIRST BETTER ON ANSWERS  MA - AM > 0 and p < 0.05.
  * ADDITION FIRST BETTER ON ANSWERS        MA - AM < 0 and p < 0.05.
      Either directional verdict gets the suffix " (UNDERPOWERED: ESTIMATE LIKELY INFLATED)" when the
      cell's floor power at +0.08 is below 0.80, and " (INTERVAL INCLUDES ZERO)" when the bootstrap
      interval contains 0.
  * UNINFORMATIVE (BELOW FLOOR)             p >= 0.05 and the floor's right-sign power at +0.08 < 0.80.
  * NOT DISTINGUISHED                       p >= 0.05 and that power >= 0.80.
  The direction is read from the signed MA - AM and is printed beside every verdict; abs() is never
  used to choose a verdict.

REPRODUCTION CHECK (pre-stated; not blind, see (c)). Over the four cells {Posttest, DPosttest} x
{TRAINED, ALL} on the primary scoring: REPRODUCES ON <test, class> for each cell with AM within 0.02
of 0.70 AND MA within 0.02 of 0.78; DOES NOT REPRODUCE if none. It is a search over four cells and
is reported as one; the cells that match are named. The printed B, SE, t, p are not re-derived: the
paper's model is not known, and `patel_order.py` part 1 showed they are mutually inconsistent.

WHAT CARRIES OVER FROM 901d14b. The printed-statistics check, the arm coding (MA minus AM), the
learner as the re-randomised unit, the 10,000 relabellings, the reproduction tolerance 0.02, the
0.80 power gate and the 8-point effect it is evaluated at. What changes: the scoring, the delay, the
floor (answer-level, per cell, at the real cell sizes), the bootstrap interval, the
UNDERPOWERED/INTERVAL suffixes and the FLOOR FAILED verdict.

    LDA_SCRATCH_DIR=<scratch> python3 patel_answers.py --floor   # writes out/patel_answers_floor.json
    LDA_SCRATCH_DIR=<scratch> python3 patel_answers.py           # needs the floor; writes out/patel_answers.json
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
from shared.paths import scratch_root  # noqa: E402
from patel_order import PRINTED, load_arm, pset, rerand_p  # noqa: E402

OUT = HERE / "out"
SEED = 20261008
REPS = 10000
BOOT = 10000
TESTS = ("Pretest", "Midtest A", "Midtest B", "Posttest", "DPosttest")
VERDICT_TESTS = ("DPosttest", "Posttest")
PRIMARY = ("DPosttest", "trained")
CLASSES = {"trained": ("ADD", "MUL"), "transfer": ("SUB", "DIV"), "all": ("ADD", "MUL", "SUB", "DIV")}
ITEMS = {("Pretest", "trained"): 8, ("Posttest", "trained"): 8, ("DPosttest", "trained"): 8,
         ("Midtest A", "trained"): 4, ("Midtest B", "trained"): 4,
         ("Pretest", "transfer"): 4, ("Posttest", "transfer"): 4, ("DPosttest", "transfer"): 4,
         ("Midtest A", "transfer"): 2, ("Midtest B", "transfer"): 2}
PLANT = (0.0, 0.08, 0.16)
ITEM_SD = 0.8


# ------------------------------------------------------------------ scoring
def problem_scores(probs, cls, drop_unanswered=False):
    """Per-problem (primary, per-step) scores for one learner on one test, for one item class.

    `probs` is patel_order.load_arm's {(problem, view): [(step, correct, op, ts), ...]}.
    """
    by_problem = defaultdict(dict)
    for (pname, view), rows in probs.items():
        by_problem[pname][int(view) if str(view).isdigit() else 99] = rows
    out = []
    for pname, views in by_problem.items():
        op = next(iter(views.values()))[0][2]
        if op not in CLASSES[cls]:
            continue
        chosen = None
        for v in sorted(views):
            ans = {r[0].split(" ")[0]: r[1] for r in views[v] if r[0].split(" ")[0] in ("num3", "den3")}
            if ans:
                chosen = ans
                break
        if chosen is None:
            if drop_unanswered:
                continue
            out.append((0.0, 0.0, True))
            continue
        n3, d3 = chosen.get("num3", False), chosen.get("den3", False)
        out.append((float(n3 and d3), (float(n3) + float(d3)) / 2, False))
    return out


def learner_scores(tests_arm, test, cls, which="primary", drop_unanswered=False):
    need = math.ceil(ITEMS[(test, cls)] / 2) if cls != "all" else \
        math.ceil((ITEMS[(test, "trained")] + ITEMS[(test, "transfer")]) / 2)
    res = {}
    for sid, probs in tests_arm.get(test, {}).items():
        ps = problem_scores(probs, cls, drop_unanswered)
        n_presented = len(problem_scores(probs, cls, False))
        if n_presented < need or not ps:
            continue
        k = 0 if which == "primary" else 1
        res[sid] = float(np.mean([p[k] for p in ps]))
    return res


# ------------------------------------------------------------------ data
def load():
    src = scratch_root() / "ds1190"
    arms = {}
    for tag, pat in (("AM", "S2_AM_Blocked"), ("MA", "S2_MA_Blocked")):
        f = next(p for p in src.iterdir() if pat in p.name)
        tests, _, _, _ = load_arm(f)             # patel_order's loader, unchanged
        arms[tag] = dict(tests=tests, file=f)
    return arms


def delays(arms):
    """Days from each learner's last practice-set row to the first row of each test (patel_artefacts)."""
    out = {}
    for tag, a in arms.items():
        last_prac, first = {}, defaultdict(dict)
        with open(a["file"], encoding="utf-8", errors="replace") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                sid, s, t = r["Anon Student Id"], pset(r["Problem Hierarchy"]), r["Step Start Time"]
                if not t:
                    continue
                if s.startswith("Fraction Arithmetic Blocked") and (sid not in last_prac or t > last_prac[sid]):
                    last_prac[sid] = t
                if s in TESTS and (s not in first[sid] or t < first[sid][s]):
                    first[sid][s] = t
        out[tag] = {s: [(datetime.fromisoformat(first[sid][s][:19]) - datetime.fromisoformat(last_prac[sid][:19]))
                         .total_seconds() / 86400 for sid in first if s in first[sid] and sid in last_prac]
                    for s in TESTS}
    return {s: {tag: dict(median=float(np.median(out[tag][s])), min=float(np.min(out[tag][s])),
                          max=float(np.max(out[tag][s])), n=len(out[tag][s])) for tag in out}
            for s in TESTS}


# ------------------------------------------------------------------ floor
def pooled_calibration(arms):
    """Arm-blind: both arms' learners are concatenated and the arm label is discarded."""
    cal = {}
    pooled_tests = defaultdict(dict)
    for tag in ("AM", "MA"):
        for s, d in arms[tag]["tests"].items():
            for sid, probs in d.items():
                pooled_tests[s][f"{sid}"] = probs
    for test in VERDICT_TESTS:
        for cls in ("trained", "transfer"):
            ys = list(learner_scores(pooled_tests, test, cls).values())
            n = {tag: len(learner_scores(arms[tag]["tests"], test, cls)) for tag in ("AM", "MA")}
            cal[f"{test}|{cls}"] = dict(pooled_mean=float(np.mean(ys)), pooled_sd=float(np.std(ys, ddof=1)),
                                        n_pooled=len(ys), n_am=n["AM"], n_ma=n["MA"], items=ITEMS[(test, cls)])
    wrong, both = 0, 0
    for s in VERDICT_TESTS:
        for sid, probs in pooled_tests[s].items():
            for prim, step, unans in problem_scores(probs, "all"):
                if not unans and prim == 0:
                    wrong += 1
                    both += step == 0
    cal["q_both_fields_wrong_given_incorrect"] = both / wrong
    return cal


def _fit(mean, sd, k, rng):
    best = None
    for sd_a in np.linspace(0.2, 3.0, 57):
        th = rng.normal(0, sd_a, 3000)
        for c in np.linspace(-0.5, 3.0, 71):
            b = rng.normal(0, ITEM_SD, (3000, k))
            pr = 1 / (1 + np.exp(-(c + th[:, None] - b)))
            props = (rng.random(pr.shape) < pr).mean(1)
            err = abs(props.mean() - mean) + abs(props.std(ddof=1) - sd)
            if best is None or err < best[0]:
                best = (err, float(sd_a), float(c), float(props.mean()), float(props.std(ddof=1)))
    return best


def _shift_for(eff, sd_a, c, k, rng):
    """Logit shift for MA whose expected gain in proportion correct equals eff."""
    if eff == 0:
        return 0.0
    th = rng.normal(0, sd_a, 20000)
    b = rng.normal(0, ITEM_SD, (20000, k))
    base = (1 / (1 + np.exp(-(c + th[:, None] - b)))).mean()
    lo, hi = 0.0, 5.0
    for _ in range(50):
        mid = (lo + hi) / 2
        m = (1 / (1 + np.exp(-(c + mid + th[:, None] - b)))).mean()
        lo, hi = (mid, hi) if m - base < eff else (lo, mid)
    return (lo + hi) / 2


def floor(arms, rng, worlds=1000, reps=2000):
    cal = pooled_calibration(arms)
    q = cal["q_both_fields_wrong_given_incorrect"]
    cells = {}
    for test in VERDICT_TESTS:
        for cls in ("trained", "transfer"):
            cc = cal[f"{test}|{cls}"]
            k, na, nm = cc["items"], cc["n_am"], cc["n_ma"]
            err, sd_a, c, m_fit, s_fit = _fit(cc["pooled_mean"], cc["pooled_sd"], k, rng)
            res = dict(calibration=dict(ability_sd=sd_a, intercept=c, fitted_mean=m_fit, fitted_sd=s_fit,
                                        target_mean=cc["pooled_mean"], target_sd=cc["pooled_sd"],
                                        n_am=na, n_ma=nm, items=k, item_sd=ITEM_SD, q=q),
                       planted={})
            for eff in PLANT:
                sh = _shift_for(eff, sd_a, c, k, rng)
                tally = {"primary": [0, 0, 0], "step": [0, 0, 0]}        # reject, right sign, wrong sign
                diffs = []
                for _ in range(worlds):
                    b = rng.normal(0, ITEM_SD, k)
                    pa = 1 / (1 + np.exp(-(c + rng.normal(0, sd_a, na)[:, None] - b)))
                    pm = 1 / (1 + np.exp(-(c + sh + rng.normal(0, sd_a, nm)[:, None] - b)))
                    ya, ym = rng.random(pa.shape) < pa, rng.random(pm.shape) < pm
                    sa = np.where(ya, 1.0, np.where(rng.random(ya.shape) < q, 0.0, 0.5))
                    sm = np.where(ym, 1.0, np.where(rng.random(ym.shape) < q, 0.0, 0.5))
                    for key, (A, M) in (("primary", (ya.mean(1), ym.mean(1))), ("step", (sa.mean(1), sm.mean(1)))):
                        p, d = rerand_p(A, M, rng, reps)                  # d = mean(MA) - mean(AM)
                        if key == "primary":
                            diffs.append(d)
                        if p < 0.05:
                            tally[key][0] += 1
                            tally[key][1 if d > 0 else 2] += 1
                res["planted"][f"{eff:.2f}"] = dict(
                    planted=eff, logit_shift=sh, mean_estimate=float(np.mean(diffs)),
                    **{f"{key}_{nm_}": v / worlds for key, t in tally.items()
                       for nm_, v in zip(("reject", "power_right_sign", "wrong_sign"), t)})
                print(f"  {test:9s} {cls:8s} planted {eff:+.2f}: mean est {np.mean(diffs):+.3f}  "
                      f"primary reject {tally['primary'][0] / worlds:.3f} right {tally['primary'][1] / worlds:.3f} "
                      f"wrong {tally['primary'][2] / worlds:.3f} | step right {tally['step'][1] / worlds:.3f}",
                      flush=True)
            pl = res["planted"]
            for key in ("primary", "step"):
                res[f"{key}_pass"] = bool(pl["0.00"][f"{key}_reject"] <= 0.07
                                          and pl["0.16"][f"{key}_power_right_sign"] >= 0.80
                                          and pl["0.08"][f"{key}_wrong_sign"] <= 0.01
                                          and pl["0.16"][f"{key}_wrong_sign"] <= 0.01)
                res[f"{key}_power_at_0.08"] = pl["0.08"][f"{key}_power_right_sign"]
            cells[f"{test}|{cls}"] = res
    return dict(calibration_pooled=cal, worlds=worlds, reps=reps, plant=PLANT, cells=cells,
                mde_d_analytic_dpost=2.802 * math.sqrt(1 / cal["DPosttest|trained"]["n_am"]
                                                       + 1 / cal["DPosttest|trained"]["n_ma"]))


# ------------------------------------------------------------------ real run
def boot(a, b, rng, n=BOOT):
    a, b = np.asarray(a), np.asarray(b)
    ia = rng.integers(0, len(a), (n, len(a)))
    ib = rng.integers(0, len(b), (n, len(b)))
    A, B = a[ia], b[ib]
    diff = B.mean(1) - A.mean(1)
    sp = np.sqrt(((len(a) - 1) * A.var(1, ddof=1) + (len(b) - 1) * B.var(1, ddof=1)) / (len(a) + len(b) - 2))
    d = np.where(sp > 0, diff / np.where(sp > 0, sp, 1), np.nan)
    return [float(x) for x in np.percentile(diff, [2.5, 97.5])], [float(x) for x in np.nanpercentile(d, [2.5, 97.5])]


def contrast(ya, ym, rng):
    a, b = list(ya.values()), list(ym.values())
    p, diff = rerand_p(a, b, rng, REPS)
    assert abs(diff - (np.mean(b) - np.mean(a))) < 1e-12           # sign check: MA minus AM
    sp = math.sqrt(((len(a) - 1) * np.var(a, ddof=1) + (len(b) - 1) * np.var(b, ddof=1)) / (len(a) + len(b) - 2))
    ci, dci = boot(a, b, rng)
    return dict(am=float(np.mean(a)), ma=float(np.mean(b)), n_am=len(a), n_ma=len(b), ma_minus_am=diff,
                direction="MA higher" if diff > 0 else "AM higher" if diff < 0 else "equal",
                d=diff / sp if sp > 0 else float("nan"), ci95_ma_minus_am=ci, ci95_d=dci, p=p)


def verdict(c, fl_cell, key="primary"):
    if not fl_cell[f"{key}_pass"]:
        return "FLOOR FAILED (NO READING)"
    pw = fl_cell[f"{key}_power_at_0.08"]
    if c["p"] < 0.05:
        v = "MULTIPLICATION FIRST BETTER ON ANSWERS" if c["ma_minus_am"] > 0 else "ADDITION FIRST BETTER ON ANSWERS"
        if pw < 0.80:
            v += " (UNDERPOWERED: ESTIMATE LIKELY INFLATED)"
        if c["ci95_ma_minus_am"][0] <= 0 <= c["ci95_ma_minus_am"][1]:
            v += " (INTERVAL INCLUDES ZERO)"
        return v
    return "UNINFORMATIVE (BELOW FLOOR)" if pw < 0.80 else "NOT DISTINGUISHED"


def run(arms, fl, rng):
    T = {tag: arms[tag]["tests"] for tag in ("AM", "MA")}
    res = dict(primary_cell=list(PRIMARY), per_test={})
    for test in TESTS:
        res["per_test"][test] = {}
        for cls in ("trained", "transfer", "all"):
            for which in ("primary", "step"):
                ya = learner_scores(T["AM"], test, cls, which)
                ym = learner_scores(T["MA"], test, cls, which)
                c = contrast(ya, ym, rng)
                cell = f"{test}|{cls}"
                if test in VERDICT_TESTS and cls != "all":
                    c["floor_power_at_0.08"] = fl["cells"][cell][f"{which}_power_at_0.08"]
                    c["verdict"] = verdict(c, fl["cells"][cell], which)
                else:
                    c["verdict"] = "descriptive" if test != "Pretest" else "balance check (descriptive)"
                res["per_test"][test][f"{cls}_{which}"] = c
                print(f"  {test:9s} {cls:8s} {which:7s} AM {c['am']:.3f} (n {c['n_am']})  MA {c['ma']:.3f} "
                      f"(n {c['n_ma']})  MA-AM {c['ma_minus_am']:+.3f} [{c['ci95_ma_minus_am'][0]:+.3f}, "
                      f"{c['ci95_ma_minus_am'][1]:+.3f}]  d {c['d']:+.2f}  p {c['p']:.4f}  -> {c['verdict']}",
                      flush=True)
    pc = res["per_test"][PRIMARY[0]][f"{PRIMARY[1]}_primary"]
    res["primary"] = dict(cell="DPosttest, trained items, answer correct (num3 and den3), MA - AM", **pc)
    # sensitivity: unanswered dropped
    ya = learner_scores(T["AM"], *PRIMARY, "primary", drop_unanswered=True)
    ym = learner_scores(T["MA"], *PRIMARY, "primary", drop_unanswered=True)
    res["sensitivity_unanswered_dropped"] = contrast(ya, ym, rng)
    unans = {tag: sum(p[2] for sid, pr in T[tag]["DPosttest"].items() for p in problem_scores(pr, "trained"))
             for tag in T}
    res["unanswered_trained_problems_dpost"] = unans
    # delay contrast
    ch = {}
    for tag in ("AM", "MA"):
        po = learner_scores(T[tag], "Posttest", "trained")
        dp = learner_scores(T[tag], "DPosttest", "trained")
        ch[tag] = {k: dp[k] - po[k] for k in dp if k in po}
    dc = contrast(ch["AM"], ch["MA"], rng)
    res["delay_contrast_trained"] = dict(note="within-learner DPosttest - Posttest change; MA - AM", **dc)
    # pretest-adjusted primary, slope fitted without arm labels
    pre = {tag: learner_scores(T[tag], "Pretest", "trained") for tag in T}
    out = {tag: learner_scores(T[tag], *PRIMARY) for tag in T}
    xs = [pre[t][k] for t in T for k in out[t] if k in pre[t]]
    ys = [out[t][k] for t in T for k in out[t] if k in pre[t]]
    slope = float(np.polyfit(xs, ys, 1)[0])
    adj = {t: {k: out[t][k] - slope * pre[t][k] for k in out[t] if k in pre[t]} for t in T}
    res["pretest_adjusted_primary"] = dict(pooled_slope=slope, **contrast(adj["AM"], adj["MA"], rng))
    # reproduction check
    hits = []
    cells = {}
    for test in ("Posttest", "DPosttest"):
        for cls in ("trained", "all"):
            c = res["per_test"][test][f"{cls}_primary"]
            ok = abs(c["am"] - PRINTED["am"]) <= 0.02 and abs(c["ma"] - PRINTED["ma"]) <= 0.02
            cells[f"{test}|{cls}"] = dict(am=c["am"], ma=c["ma"], within_0_02=ok)
            if ok:
                hits.append(f"{test}, {cls}")
    res["reproduction"] = dict(printed=dict(am=PRINTED["am"], ma=PRINTED["ma"]), tolerance=0.02, cells=cells,
                               verdict=("REPRODUCES ON " + "; ".join(hits)) if hits else "DOES NOT REPRODUCE",
                               note="search over 4 cells; not blind (arithmetic on committed aggregates had "
                                    "already suggested 0.70/0.78)")
    res["delay_days_from_last_practice_set_row"] = delays(arms)
    res["verdict"] = pc["verdict"]
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--floor", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    rng = np.random.default_rng(SEED)
    arms = load()
    if a.floor:
        print("DETECTION FLOOR (answer level, calibrated on pooled data with arm labels discarded)")
        fl = floor(arms, rng)
        for cell, r in fl["cells"].items():
            print(f"  {cell}: primary {'PASS' if r['primary_pass'] else 'FAIL'} (power@0.08 "
                  f"{r['primary_power_at_0.08']:.3f}); step {'PASS' if r['step_pass'] else 'FAIL'} "
                  f"(power@0.08 {r['step_power_at_0.08']:.3f})")
        (OUT / "patel_answers_floor.json").write_text(json.dumps(fl, indent=1))
        return
    fpath = OUT / "patel_answers_floor.json"
    if not fpath.exists():
        sys.exit("run --floor first (and commit it) -- the floor precedes any real number")
    fl = json.loads(fpath.read_text())
    rng = np.random.default_rng(SEED + 1)
    print("RE-ANALYSIS, answer level (registered amendment; not blind)")
    res = run(arms, fl, rng)
    res["not_blind"] = ("Registered after the logging artefact was found, after the registered analysis's "
                        "step-level per-arm outputs were seen, and after arithmetic on committed aggregates "
                        "suggested answer accuracy near 0.70/0.78 on the DPosttest. Registered but non-blind.")
    print(f"\nPRIMARY {res['primary']['cell']}: MA-AM {res['primary']['ma_minus_am']:+.4f} "
          f"CI {res['primary']['ci95_ma_minus_am']} p {res['primary']['p']:.4f} -> {res['verdict']}")
    print(f"REPRODUCTION: {res['reproduction']['verdict']}")
    (OUT / "patel_answers.json").write_text(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
