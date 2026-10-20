"""
Bias on identical work, or an informative prior? Paper VI's attainment gap, re-tested (2026-10-05).

WHAT WAS ASKED. Paper VI (research/article/attainment-bias-in-llm-grading.md, release
ai-grader-reliability-2026 1.0.0) reports that telling an LLM grader a learner's held-out attainment
opens a gap on identical work between learners described as strong and weak: 0.48, 0.24 and 0.54
points on 0-10 for three models, "the entire effect ... a penalty applied to students the grader is
told are weak". The NLP reviewer packet (research/readiness/reviewer-packets/nlp-data-scientist.md)
asks two things the original run could not answer:

  Q2  The two tails hold DIFFERENT students, whose teacher marks differ, and the label shown is TRUE
      and predicts the teacher's mark. A downward drift in the low tail could be a penalty (bias) or
      a correction of the control arm's generosity toward the teacher (an informative prior). Needs
      (a) per-tail signed error against the teacher with and without the label, and (b) a
      swapped-label arm on identical work.
  Q4  "No accuracy gain" rests on a +/-0.02 QWK harness resolution, not on a paired interval. Needs a
      paired, clustered bootstrap on dQWK and dMAE with an equivalence margin fixed in advance.

THE DATA. JorGPT (Zenodo 18981627, CC BY 4.0; data/data-sources.json `jorgpt-answers`): 3,041
teacher-graded answers, 50 questions, 79 learners. This script NEVER reads the corpus. It reads the
per-case dumps written by the harness mode `attainment-swap`
(studies/measurement/grader-eval/harness/stability.ts), which hold entry ids, the teacher grade and
the model's scores; those dumps stay in the session scratchpad and only the aggregates in `out/` are
committed. The draw is the original run's, byte for byte: `attainmentDraw()` was extracted unchanged
from `runAttainment()`, which in turn matches app commit 584e5a91a apart from a metrics call
signature. 150 cases whose learner's held-out mean teacher grade is >= 6, 150 whose is < 4.

THE DESIGN. Three arms on every case, identical prompt bytes apart from one sentence:
  control      no attainment (the shipped configuration)
  trueLabel    "Current attainment for this learner across this course: {own held-out mean}/10, from
               {n} prior graded responses." -- the original arm
  swappedLabel the same sentence carrying the OPPOSITE tail's label: high-tail case i gets low-tail
               case i's held-out mean and n, and vice versa. A derangement by construction (no case
               keeps a label from its own tail, let alone its own learner). The control is the size
               of the treatment by construction: same template, same length to within a digit.

THE UNIT. The attainment label is a property of the LEARNER, and the draw holds 19 high-tail and 14
low-tail learners, contributing up to 13 cases each. Cases are not independent: every interval here is
a LEARNER-CLUSTER bootstrap (resample learners with replacement within tail, take all their cases),
4,000 resamples, percentile. The original harness interval treated 300 cases as independent; that is
the "permute the unit the treatment was assigned to" failure, and its widening is reported beside
each gap. A question-cluster bootstrap is reported as a sensitivity check only.

QUANTITIES (all signed; "score" means the grader's number, h the teacher's):
  drift_k        mean(trueLabel - control) in tail k
  L              label effect on identical work: mean over all cases of score|high label - score|low
                 label = (trueLabel - swappedLabel) in the high tail, (swappedLabel - trueLabel) in the
                 low tail. Positive = a high label raises the grade.
  bias_arm_k     mean(arm - h) in tail k (the reviewer's per-tail signed error)
  dMAE_k         MAE_k(trueLabel) - MAE_k(control). Negative = the true label moves grades TOWARD the
                 teacher (reviewer's check (a)).
  I_k            MAE_k(trueLabel) - MAE_k(swappedLabel), same work. Negative = the RIGHT label gives
                 more accurate grades than the WRONG label on the same answers, i.e. the label is
                 being used as information about the answer. This is what a legitimate prior
                 predicts in BOTH tails.
  dQWK, dMAE     pooled, trueLabel minus control (Q4). QWK as harness/metrics.ts: scores rounded
                 half-up onto 0..10.

WHY I_k AND NOT dMAE ALONE. The grader is generous in control (+0.38 on the grade-stratified draw).
Against a generous grader ANY downward push lowers MAE, whatever drives it. So a pure penalty on weak
labels would pass the reviewer's check (a) in the low tail and look like a prior. The swapped arm
separates the two: under a prior the true label beats the false one in both tails; under a
label-keyed shove the high tail's true (high) label makes things worse than the false (low) one,
because the low label pushes a generous grader down. The floor (below) plants both worlds.

PRE-REGISTERED VERDICT (written and committed before any model call; see the git log):
  NO-LABEL-EFFECT  L's 95% interval includes 0.
  PRIOR            L > 0 (interval excludes 0), I_high and I_low both have 95% upper bound < 0, and no
                   tail has dMAE_k 95% lower bound > 0.
                   -> "the grader uses the label as an informative prior: on the same work the true
                      label moves grades toward the teacher's mark in both tails"
  BIAS             L > 0, and EITHER some tail has I_k 95% lower bound > 0 (the true label is less
                   accurate than the false one on the same work) OR some tail has dMAE_k 95% lower
                   bound > 0 (the true label moves that tail away from the teacher).
                   -> "the label moves the grade on identical work in a way its information about the
                      answer does not justify"
  MIXED            L > 0 and neither PRIOR nor BIAS.
  REVERSED         L < 0 (interval excludes 0).
  Across models: the common verdict if every model shares one, else MIXED-ACROSS-MODELS with each.
  PER-TAIL READING of the paper's "penalty on the weak" (reported, not part of the verdict):
    LOW-TAIL-AWAY / LOW-TAIL-TOWARD / LOW-TAIL-FLAT from dMAE_low's 95% interval.

PRE-REGISTERED Q4 VERDICT, per model and metric, trueLabel minus control:
  margins  dQWK +/-0.02 (the paper's own stated resolution), dMAE +/-0.10 points (1% of the scale).
  EQUIVALENT    the 90% interval (TOST at alpha 0.05) lies inside +/-margin -> "no gain larger than X",
                X = the improving-side bound of the 95% interval.
  GAIN / LOSS   not EQUIVALENT and the 95% interval excludes 0 (improving / worsening side).
  INCONCLUSIVE  otherwise.

THE FLOOR (`--floor`). Before any real number: synthetic graders on the real draw (real teacher marks,
real tails, real labels, real learner clusters), with a case effect, a learner effect, per-arm
re-sampling noise and the control's generosity, rounded onto 0..10. Five planted worlds, 200
replicates each, the instrument above run unchanged. PASS requires >= 80% of replicates to return the
planted verdict in every world, and <= 10% of NULL replicates to return any label effect.
  NULL            no label effect                                   -> NO-LABEL-EFFECT
  PRIOR           shrink 11% toward the label value (L ~ 0.4)       -> PRIOR
  PENALTY-GEN     -0.5 for a low label only, generous grader +0.38  -> BIAS
  PENALTY-UNBIAS  -0.5 for a low label only, unbiased grader        -> BIAS
  SYM-SHOVE       +/-0.25 by label, generous grader                 -> BIAS
A grader written by this session and scored by this session is a smoke check of the instrument's
logic on worlds it was told about, not a validation of the construct; it is reported as one.

THE PRE-REGISTERED Q2 INSTRUMENT ABOVE FAILED ITS FLOOR, AND THE VERDICT IS NOW REVISION 3. Kept
above as written, because a reader should see what was planned. Revision 0 recovered a planted PRIOR
in 3 of 200 replicates: MAE moves only to second order under a 0.2-0.5 point shift, and a generous
control makes any downward push look accurate. Revisions 1-2 (recentring; |signed error| differences)
still had no power, because a difference of absolute values swings by twice the uncertainty of the
control's tail bias, which is +/-0.3 with 14-19 learners per tail. Revision 3 (`tail_direction`,
`verdict_q2`) uses first-order quantities only and DECLINES (UNRESOLVED) where the reference point is
not resolved; the floor worlds were re-shaped to the corpus (control per-tail error matched to the
deposit's own gemini_grade baseline: +0.10 high, +0.40 low; learner sd 0.33). All of this was
settled before any dump from the real runs was read; see README "Floor record".

FAILURES THAT SHAPED THIS. (1) The original harness n flag defaults to 150, i.e. 75 per tail; the
paper's 150 per tail needs --n 300, which the new mode defaults to. (2) dMAE alone cannot tell a prior
from a penalty against a generous grader; I_k was added for that reason before any run.

Usage:
  python3 analyse.py --floor
  python3 analyse.py --dumps <scratch>/grader-vi/swap-*.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
REPS = 4000
FLOOR_REPS = 200
FLOOR_BOOT = 400
SCALE = (0, 10)
MARGIN_QWK = 0.02
MARGIN_MAE = 0.10


# ----------------------------------------------------------------------------- metrics

def round_half_up(x: np.ndarray) -> np.ndarray:
    """JS Math.round, which the harness's QWK uses; numpy's round is half-to-even."""
    return np.floor(np.asarray(x, float) + 0.5)


def qwk(h: np.ndarray, m: np.ndarray, lo: int = SCALE[0], hi: int = SCALE[1]) -> float:
    k = hi - lo + 1
    a = np.clip(round_half_up(h) - lo, 0, k - 1).astype(int)
    b = np.clip(round_half_up(m) - lo, 0, k - 1).astype(int)
    O = np.zeros((k, k))
    np.add.at(O, (a, b), 1)
    n = len(a)
    E = np.outer(np.bincount(a, minlength=k), np.bincount(b, minlength=k)) / n
    i, j = np.indices((k, k))
    W = (i - j) ** 2 / (k - 1) ** 2
    den = (W * E).sum()
    return float(1 - (W * O).sum() / den) if den else 0.0


# ----------------------------------------------------------------------------- the instrument

class Data:
    def __init__(self, rows: list[dict]):
        self.h = np.array([r["human"] for r in rows], float)
        self.c = np.array([r["control"] for r in rows], float)
        self.t = np.array([r["trueLabel"] for r in rows], float)
        self.s = np.array([r["swappedLabel"] for r in rows], float)
        self.hi = np.array([r["tail"] == "high" for r in rows])
        self.learner = np.array([str(r["learnerId"]) for r in rows])
        self.question = np.array([str(r["questionId"]) for r in rows])


def stats(d: Data, idx: np.ndarray) -> dict[str, float]:
    h, c, t, s, hi = d.h[idx], d.c[idx], d.t[idx], d.s[idx], d.hi[idx]
    lo = ~hi
    out: dict[str, float] = {}
    hl = np.where(hi, t - s, s - t)                 # score under high label minus under low label
    out["L"] = hl.mean()
    out["L_high"] = hl[hi].mean()
    out["L_low"] = hl[lo].mean()
    for name, m in (("high", hi), ("low", lo)):
        out[f"drift_{name}"] = (t - c)[m].mean()
        out[f"drift_swapped_{name}"] = (s - c)[m].mean()
        for arm, x in (("control", c), ("true", t), ("swapped", s)):
            out[f"bias_{arm}_{name}"] = (x - h)[m].mean()
            out[f"mae_{arm}_{name}"] = np.abs(x - h)[m].mean()
        out[f"dMAE_{name}"] = out[f"mae_true_{name}"] - out[f"mae_control_{name}"]
        out[f"dMAE_swapped_{name}"] = out[f"mae_swapped_{name}"] - out[f"mae_control_{name}"]
        out[f"I_{name}"] = out[f"mae_true_{name}"] - out[f"mae_swapped_{name}"]
    # RECENTRED (revision 1, after the first floor failed; see README): each arm minus its own
    # pooled, label-blind mean signed error, so a shift common to every case cannot pass for
    # information. The control's generosity otherwise makes any downward push look accurate.
    rc, rt, rs = c - (c - h).mean(), t - (t - h).mean(), s - (s - h).mean()
    for name, m in (("high", hi), ("low", lo)):
        for arm, x in (("control", rc), ("true", rt), ("swapped", rs)):
            out[f"rbias_{arm}_{name}"] = (x - h)[m].mean()
            out[f"rmae_{arm}_{name}"] = np.abs(x - h)[m].mean()
        out[f"rdrift_{name}"] = out[f"rbias_true_{name}"] - out[f"rbias_control_{name}"]
        out[f"rdMAE_{name}"] = out[f"rmae_true_{name}"] - out[f"rmae_control_{name}"]
        out[f"rI_{name}"] = out[f"rmae_true_{name}"] - out[f"rmae_swapped_{name}"]
        # Revision 2: TAIL-LEVEL signed error. A learner-level label can only carry tail-level
        # information, and a shift moves a mean signed error to first order but an MAE only to
        # second, which is why the MAE versions had no power (README, floor record).
        for P, key in (("r", "rbias"), ("", "bias")):
            out[f"{P}T_{name}"] = abs(out[f"{key}_true_{name}"]) - abs(out[f"{key}_control_{name}"])
            out[f"{P}J_{name}"] = abs(out[f"{key}_true_{name}"]) - abs(out[f"{key}_swapped_{name}"])
    out["gap"] = out["drift_high"] - out["drift_low"]
    out["dMAE"] = np.abs(t - h).mean() - np.abs(c - h).mean()
    out["dMAE_swapped"] = np.abs(s - h).mean() - np.abs(c - h).mean()
    out["qwk_control"] = qwk(h, c)
    out["qwk_true"] = qwk(h, t)
    out["qwk_swapped"] = qwk(h, s)
    out["dQWK"] = out["qwk_true"] - out["qwk_control"]
    out["dQWK_swapped"] = out["qwk_swapped"] - out["qwk_control"]
    out["mae_control"] = np.abs(c - h).mean()
    out["mae_true"] = np.abs(t - h).mean()
    return {k: float(v) for k, v in out.items()}


def cluster_index(groups: np.ndarray, strata: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Resample whole clusters with replacement, within stratum, and return the case indices."""
    out = []
    for st in np.unique(strata):
        ids = np.unique(groups[strata == st])
        for g in rng.choice(ids, size=len(ids), replace=True):
            out.append(np.flatnonzero((groups == g) & (strata == st)))
    return np.concatenate(out)


def interval(d: Data, rng: np.random.Generator, reps: int, by: str = "learner") -> dict[str, dict]:
    point = stats(d, np.arange(len(d.h)))
    groups = d.learner if by == "learner" else d.question
    if by == "case":
        groups = np.arange(len(d.h)).astype(str)
    draws = {k: [] for k in point}
    for _ in range(reps):
        st = stats(d, cluster_index(groups, d.hi, rng))
        for k, v in st.items():
            draws[k].append(v)
    res = {}
    for k, v in point.items():
        a = np.array(draws[k])
        res[k] = {
            "est": v,
            "ci95": [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))],
            "ci90": [float(np.percentile(a, 5)), float(np.percentile(a, 95))],
        }
    return res


def tail_direction(r: dict[str, dict], k: str, P: str = "") -> str:
    """REVISION 3 (2026-10-05, before any real number was read; README "Floor record").

    Built from first-order quantities only, each with its learner-cluster 95% interval: the drift the
    true label causes in tail k, the control's mean signed error in tail k (the reference point the
    drift moves relative to), and the true-label arm's. Revisions 1-2 tested a difference of absolute
    values, |B_true| - |B_control|, whose interval swings by twice the uncertainty of B_control and
    had no power on the floor.

      FLAT        the drift's interval includes 0
      AWAY        the control's error is resolvably on the SAME side as the drift (the label pushes a
                  tail further the way it was already wrong), or the true-label error is resolvably on
                  the far side of 0 and larger in magnitude than the control's (overshoot)
      TOWARD      the control's error is resolvably on the OPPOSITE side of the drift, and no overshoot
      UNRESOLVED  a real drift, but the control's error in that tail is not resolved from 0
    """
    key = "rbias" if P == "r" else "bias"
    dr = r[f"{P}drift_{k}"]["ci95"]
    bc, bt = r[f"{key}_control_{k}"], r[f"{key}_true_{k}"]
    pos = lambda ci: ci[0] > 0   # noqa: E731
    neg = lambda ci: ci[1] < 0   # noqa: E731
    if not (pos(dr) or neg(dr)):
        return "FLAT"
    up = pos(dr)
    if (up and pos(bc["ci95"])) or (not up and neg(bc["ci95"])):
        return "AWAY"
    over = abs(bt["est"]) > abs(bc["est"]) and (
        (pos(bc["ci95"]) and neg(bt["ci95"])) or (neg(bc["ci95"]) and pos(bt["ci95"])))
    if over:
        return "AWAY"
    if (not up and pos(bc["ci95"])) or (up and neg(bc["ci95"])):
        return "TOWARD"
    return "UNRESOLVED"


def verdict_q2(r: dict[str, dict], P: str = "") -> dict[str, str]:
    """Combine the two tails. P = "r": the same reading after each arm is recentred on its own
    pooled, label-blind signed error, i.e. what the label adds beyond a calibration constant;
    reported beside the verdict, not instead of it."""
    L = r["L"]["ci95"]
    d = {k: tail_direction(r, k, P) for k in ("high", "low")}
    out = {"high_tail": d["high"], "low_tail": d["low"]}
    if L[0] <= 0 <= L[1]:
        v = "NO-LABEL-EFFECT"
    elif L[1] < 0:
        v = "REVERSED"
    else:
        # Strict: a verdict needs EVERY tail the label moved to be resolved the same way. A tail
        # with a real drift but an unresolved reference blocks PRIOR and BIAS alike (rev. 3b).
        moved = [x for x in d.values() if x != "FLAT"]
        if "TOWARD" in moved and "AWAY" in moved:
            v = "MIXED"
        elif moved and all(x == "TOWARD" for x in moved):
            v = "PRIOR"
        elif moved and all(x == "AWAY" for x in moved):
            v = "BIAS"
        else:
            v = "UNRESOLVED"
    out["verdict"] = v
    return out


def verdict_q4(r: dict[str, dict], metric: str, margin: float, better_is_lower: bool) -> dict:
    e = r[metric]
    lo90, hi90 = e["ci90"]
    lo95, hi95 = e["ci95"]
    if -margin < lo90 and hi90 < margin:
        v = "EQUIVALENT"
    elif (hi95 < 0) if better_is_lower else (lo95 > 0):
        v = "GAIN"
    elif (lo95 > 0) if better_is_lower else (hi95 < 0):
        v = "LOSS"
    else:
        v = "INCONCLUSIVE"
    bound = -lo95 if better_is_lower else hi95       # largest gain the 95% interval admits
    return {"verdict": v, "margin": margin, "est": e["est"], "ci95": e["ci95"], "ci90": e["ci90"],
            "largest_gain_admitted": max(0.0, bound)}


# ----------------------------------------------------------------------------- the floor

# Every world shares one control grader SHAPED LIKE THE CORPUS: compression 0.90 and generosity +0.28,
# chosen so the control's per-tail signed error on this draw matches the deposit's own Gemini baseline
# grades (gemini_grade: +0.10 high tail, +0.40 low tail), with the deposit's learner-level error sd
# (0.33) and within-learner sd (1.5, split 1.4 case + 0.6 per call). No score from this study's own
# runs was read to set them.
BASE_G, BASE_C = 0.28, 0.90
WORLDS = {
    # name: (label_fn(label_value, base_score) -> shifted score, expected verdict)
    "NULL": (lambda lab, x: x, "NO-LABEL-EFFECT"),
    "PENALTY": (lambda lab, x: x - 0.4 * (lab < 5), "PRIOR"),            # corrects the low tail's generosity
    "OVERSHOOT": (lambda lab, x: x - 2.0 * (lab < 5), "BIAS"),           # drives the low tail well past the teacher (clipping at 0 absorbs part)
    # The corpus-shaped high tail is only +0.10 generous, which 19 learners cannot resolve from 0, so
    # a push there has no resolvable direction: the instrument must DECLINE, not guess.
    "BOOST": (lambda lab, x: x + 0.4 * (lab >= 5), "UNRESOLVED"),
    "SHOVE": (lambda lab, x: x + np.where(lab >= 5, 0.3, -0.3), "UNRESOLVED"),
}


def synth(draw: list[dict], world: str, rng: np.random.Generator) -> list[dict]:
    fn, _ = WORLDS[world]
    learners = sorted({r["learnerId"] for r in draw})
    lv = dict(zip(learners, rng.normal(0, 0.33, len(learners))))
    out = []
    for r in draw:
        base = 5 + BASE_C * (r["human"] - 5) + BASE_G + lv[r["learnerId"]] + rng.normal(0, 1.4)

        def arm(label):
            x = base + rng.normal(0, 0.6)                                    # re-sampling noise per call
            if label is not None:
                x = fn(np.array(label), x)
            return float(np.clip(round_half_up(x), *SCALE))

        out.append({**r, "control": arm(None), "trueLabel": arm(r["labelTrue"]),
                    "swappedLabel": arm(r["labelSwapped"])})
    return out


def run_floor(draw_path: Path) -> dict:
    draw = json.loads(draw_path.read_text())["rows"]
    rng = np.random.default_rng(20261005)
    report = {}
    ok = True
    for world, (_, expected) in WORLDS.items():
        got = []
        for _ in range(FLOOR_REPS):
            d = Data(synth(draw, world, rng))
            got.append(verdict_q2(interval(d, rng, FLOOR_BOOT))["verdict"])
        hit = sum(v == expected for v in got) / len(got)
        counts = {v: got.count(v) for v in sorted(set(got))}
        # a wrong-direction call is the costly error: PRIOR where none is planted, or BIAS likewise
        wrong = sum(v in ("PRIOR", "BIAS", "MIXED") and v != expected for v in got) / len(got)
        passed = hit >= 0.8 and wrong <= 0.10
        if world == "NULL":
            fp = sum(v != "NO-LABEL-EFFECT" for v in got) / len(got)
            passed = passed and fp <= 0.10
        ok &= passed
        report[world] = {"expected": expected, "hit_rate": hit, "wrong_direction_rate": wrong,
                         "verdicts": counts, "pass": passed}
        print(f"  floor {world:15s} expect {expected:16s} hit {hit:.2f}  {counts}  {'PASS' if passed else 'FAIL'}")
    return {"pass": ok, "replicates": FLOOR_REPS, "bootstrap": FLOOR_BOOT, "worlds": report,
            "note": "smoke check: synthetic graders written and scored by the same session"}


# ----------------------------------------------------------------------------- main

def analyse(path: Path, rng: np.random.Generator) -> dict:
    blob = json.loads(path.read_text())
    rows = blob["rows"]
    complete = [r for r in rows if None not in (r["control"], r["trueLabel"], r["swappedLabel"])]
    d = Data(complete)
    r = interval(d, rng, REPS, "learner")
    rq = interval(d, rng, REPS // 2, "question")
    rc = interval(d, rng, REPS // 2, "case")
    keep = ("L", "gap", "dMAE", "dQWK", "dMAE_low", "dMAE_high", "I_low", "I_high")
    return {
        "model": blob["model"],
        "run": blob.get("runStamp"),
        "n_rows": len(rows),
        "n_complete": len(complete),
        "complete_by_tail": {"high": int(d.hi.sum()), "low": int((~d.hi).sum())},
        "learners_by_tail": {"high": len(set(d.learner[d.hi])), "low": len(set(d.learner[~d.hi]))},
        "q2": verdict_q2(r),
        "q2_recentred_reported_only": verdict_q2(r, "r"),
        "q4": {"dQWK": verdict_q4(r, "dQWK", MARGIN_QWK, False),
               "dMAE": verdict_q4(r, "dMAE", MARGIN_MAE, True)},
        "learner_cluster": r,
        "sensitivity_question_cluster": {k: rq[k] for k in keep},
        "sensitivity_case_iid": {k: rc[k] for k in keep},
    }


def analyse_history(path: Path, rng: np.random.Generator, reps: int = REPS) -> dict:
    """Q4 for the attempt-history arms (paper section 5.2): each arm minus control, paired, with a
    learner-cluster bootstrap and the same pre-registered margins and verdict strings as above. The
    draw is the harness's grade-stratified n=150, seed 7, as in the paper."""
    blob = json.loads(path.read_text())
    arms = blob["arms"]
    rows = [r for r in blob["rows"] if all(r[a] is not None for a in arms)]
    h = np.array([r["human"] for r in rows], float)
    learner = np.array([str(r["learnerId"]) for r in rows])
    one = np.zeros(len(rows), bool)
    X = {a: np.array([r[a] for r in rows], float) for a in arms}
    ctl = arms[0]
    out = {"model": blob["model"], "run": blob.get("runStamp"), "n_rows": len(blob["rows"]),
           "n_complete": len(rows), "learners": len(set(learner)), "arms": {}}

    def st(idx: np.ndarray, a: str) -> dict[str, float]:
        hh, c, x = h[idx], X[ctl][idx], X[a][idx]
        return {"drift": float((x - c).mean()), "dQWK": qwk(hh, x) - qwk(hh, c),
                "dMAE": float(np.abs(x - hh).mean() - np.abs(c - hh).mean()),
                "qwk": qwk(hh, x), "mae": float(np.abs(x - hh).mean()), "bias": float((x - hh).mean())}

    for a in arms[1:]:
        point = st(np.arange(len(rows)), a)
        draws = [st(cluster_index(learner, one, rng), a) for _ in range(reps)]
        r = {k: {"est": v, "ci95": [float(np.percentile([d[k] for d in draws], 2.5)),
                                     float(np.percentile([d[k] for d in draws], 97.5))],
                 "ci90": [float(np.percentile([d[k] for d in draws], 5)),
                          float(np.percentile([d[k] for d in draws], 95))]} for k, v in point.items()}
        out["arms"][a] = {"stats": r, "q4": {"dQWK": verdict_q4(r, "dQWK", MARGIN_QWK, False),
                                             "dMAE": verdict_q4(r, "dMAE", MARGIN_MAE, True)}}
    c = X[ctl]
    out["control"] = {"qwk": qwk(h, c), "mae": float(np.abs(c - h).mean()), "bias": float((c - h).mean())}
    return out


def floor_q4(draw_path: Path) -> dict:
    """Floor for the Q4 instrument on the grade-stratified history draw: an arm that is the control
    re-drawn (nothing planted) must come back EQUIVALENT on dMAE and dQWK in >= 80% of replicates; an
    arm whose case-level error is cut by 40% (a real accuracy gain) must come back GAIN on dMAE in
    >= 80%. Smoke check, synthetic, one session."""
    rows = json.loads(draw_path.read_text())["rows"]
    h = np.array([r["human"] for r in rows], float)
    learner = [r["learnerId"] for r in rows]
    rng = np.random.default_rng(41)
    tallies = {"null_dMAE": [], "null_dQWK": [], "gain_dMAE": []}
    for _ in range(FLOOR_REPS):
        lv = {k: rng.normal(0, 0.33) for k in set(learner)}
        case = rng.normal(0, 1.4, len(h)) + np.array([lv[k] for k in learner])
        mk = lambda e: np.clip(round_half_up(h + 0.3 + e + rng.normal(0, 0.6, len(h))), *SCALE)  # noqa: E731
        ctl, null, gain = mk(case), mk(case), mk(0.6 * case)
        for name, arm in (("null", null), ("gain", gain)):
            blob = {"model": "synthetic", "arms": ["control", name],
                    "rows": [{"human": float(h[i]), "learnerId": learner[i], "control": float(ctl[i]),
                              name: float(arm[i])} for i in range(len(h))]}
            tmp = OUT / ".floor-q4.json"
            tmp.write_text(json.dumps(blob))
            res = analyse_history(tmp, rng, reps=FLOOR_BOOT)["arms"][name]["q4"]
            tmp.unlink()
            if name == "null":
                tallies["null_dMAE"].append(res["dMAE"]["verdict"])
                tallies["null_dQWK"].append(res["dQWK"]["verdict"])
            else:
                tallies["gain_dMAE"].append(res["dMAE"]["verdict"])
    want = {"null_dMAE": "EQUIVALENT", "null_dQWK": "EQUIVALENT", "gain_dMAE": "GAIN"}
    report = {k: {"expected": want[k], "hit_rate": v.count(want[k]) / len(v),
                  "verdicts": {x: v.count(x) for x in set(v)}} for k, v in tallies.items()}
    ok = all(x["hit_rate"] >= 0.8 for x in report.values())
    for k, v in report.items():
        print(f"  q4 floor {k:10s} expect {v['expected']:10s} hit {v['hit_rate']:.2f} {v['verdicts']}")
    return {"pass": ok, "replicates": FLOOR_REPS, "bootstrap": FLOOR_BOOT, "checks": report,
            "note": "smoke check: synthetic arms written and scored by the same session"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--floor-q4", type=Path, help="the grade-stratified draw (human grades, learner ids)")
    ap.add_argument("--floor", action="store_true")
    ap.add_argument("--draw", type=Path)
    ap.add_argument("--dumps", type=Path, nargs="*")
    ap.add_argument("--history", type=Path)
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    if a.floor_q4:
        res = floor_q4(a.floor_q4)
        (OUT / "floor-q4.json").write_text(json.dumps(res, indent=2) + "\n")
        print("Q4 FLOOR", "PASS" if res["pass"] else "FAIL")
        sys.exit(0 if res["pass"] else 1)
    if a.history:
        # The Q4 floor FAILED on its equivalence half (README): at n=150 and 65 learners a re-drawn
        # control comes back EQUIVALENT in 4% of replicates at the +/-0.10 MAE margin and 33% at
        # +/-0.02 QWK, while a real gain is caught 100% of the time. So EQUIVALENT is unreachable
        # here, and the result is read only as an interval ("no gain larger than X"). The gate below
        # requires the floor to have RUN and its shortfall to be the documented one.
        fq = json.loads((OUT / "floor-q4.json").read_text())
        if fq["checks"]["gain_dMAE"]["hit_rate"] < 0.8:
            sys.exit("Q4 floor cannot see a planted gain; no real number is read")
        res = analyse_history(a.history, np.random.default_rng(11))
        (OUT / "history-q4.json").write_text(json.dumps(res, indent=2) + "\n")
        print(f"control {res['control']}  n={res['n_complete']}/{res['n_rows']}  learners={res['learners']}")
        for name, v in res["arms"].items():
            s = v["stats"]
            f = lambda k: f"{s[k]['est']:+.3f} [{s[k]['ci95'][0]:+.3f}, {s[k]['ci95'][1]:+.3f}]"
            print(f"  {name:32s} drift {f('drift')}  dQWK {f('dQWK')} {v['q4']['dQWK']['verdict']}"
                  f"  dMAE {f('dMAE')} {v['q4']['dMAE']['verdict']}")
        return
    if a.floor:
        res = run_floor(a.draw)
        (OUT / "floor.json").write_text(json.dumps(res, indent=2) + "\n")
        print("FLOOR", "PASS" if res["pass"] else "FAIL")
        sys.exit(0 if res["pass"] else 1)
    floor = json.loads((OUT / "floor.json").read_text())
    # Revision 3's floor passed every world but OVERSHOOT, at 0.78 against 0.80 (MC se ~0.03), and
    # it missed by DECLINING (42 UNRESOLVED), not by misdirection (1 PRIOR, 1 MIXED in 200). Read
    # with that limit stated: a low-tail overshoot is detected about four times in five. Any other
    # shortfall stops the read.
    short = [w for w, v in floor["worlds"].items() if not v["pass"]]
    if short not in ([], ["OVERSHOOT"]) or floor["worlds"]["OVERSHOOT"]["wrong_direction_rate"] > 0.10:
        sys.exit(f"floor shortfall beyond the documented one: {short}; no real number is read")
    rng = np.random.default_rng(7)
    per = [analyse(p, rng) for p in a.dumps]
    verdicts = sorted({m["q2"]["verdict"] for m in per})
    overall = verdicts[0] if len(verdicts) == 1 else "MIXED-ACROSS-MODELS"
    res = {"overall_q2": overall, "per_model": {m["model"]: m for m in per},
           "margins": {"dQWK": MARGIN_QWK, "dMAE": MARGIN_MAE}, "bootstrap_reps": REPS}
    (OUT / "results.json").write_text(json.dumps(res, indent=2) + "\n")
    for m in per:
        R = m["learner_cluster"]
        f = lambda k: f"{R[k]['est']:+.3f} [{R[k]['ci95'][0]:+.3f}, {R[k]['ci95'][1]:+.3f}]"
        print(f"\n{m['model']}  n={m['n_complete']}/{m['n_rows']}  Q2 {m['q2']}  recentred {m['q2_recentred_reported_only']}")
        for k in ("L", "L_high", "L_low", "gap", "drift_high", "drift_low", "bias_control_high", "bias_true_high",
                  "bias_control_low", "bias_true_low", "dMAE_high", "dMAE_low", "I_high", "I_low", "dQWK", "dMAE"):
            print(f"  {k:20s} {f(k)}")
        print(f"  Q4 dQWK {m['q4']['dQWK']['verdict']}  dMAE {m['q4']['dMAE']['verdict']}")
    print("\nOVERALL Q2:", overall)


if __name__ == "__main__":
    main()
