"""
Does a label-free calibration buy what the attainment label bought? Paper VI, re-tested (2026-10-06).

WHAT WAS ASKED. Paper VI (research/article/attainment-bias-in-llm-grading.md, release
ai-grader-reliability-2026) reports that a grader told a learner's attainment ("Current attainment for
this learner across this course: x/10, ...") raises QWK against the teacher on some graders, with no
resolved change in Pearson r, and says this gain is "consistent with moving marks toward where the
teacher puts them, which QWK rewards. That is the kind of gain a calibration that does not use the label
(one shift and one stretch fitted to everybody) is designed to produce, without telling the grader who
wrote the work; we did not test whether it produces this one." The maintainer asked to test it.
Identity (paper 4.6): QWK = 2 s_xy / (s_x^2 + s_y^2 + d^2) with chance from the marginals, so a linear
map that matches the teacher's mean and SD raises QWK toward (at most) r and leaves r unchanged.

CORRECTION TO THE BRIEF, RECORDED AS PART OF THE PRE-REGISTRATION. The brief named GPT-4.1-mini,
Qwen3-235B and Claude Opus 5.5 as the graders whose true label raised QWK. The coordinator corrected it
before anything here was pre-registered: the three runs where the true label raised QWK with a 95%
interval clear of zero are Claude Opus 5.5 (+0.029 [+0.013, +0.043], breadth/swap-opus55.json), Llama 4
Maverick (+0.046 [+0.010, +0.085], breadth/swap-llama4.json) and GPT-5-mini at MINIMAL reasoning
(+0.039 [+0.001, +0.074], breadth/swap-g5m-min.json). GPT-4.1-mini and Qwen showed no resolved gain
(+0.003, -0.010). (Source: the paper's accuracy table under RQ2 and grader-model-breadth/out/models.json.)
Those three are the SUMMARY SET for questions (b) and (c); every other run is reported with the same
rules but carries no summary weight.

PRIOR KNOWLEDGE, STATED. An exploratory, non-pre-registered look by the orchestrator has been seen:
leave-one-student-out mean/SD matching on the CONTROL arm only, integer-rounded and clipped, gave
Gemini 3.5 Flash Lite QWK 0.809 -> 0.817 (MAE 1.27 -> 1.25), GPT-4.1-mini 0.712 -> 0.808 (1.53 -> 1.23),
GPT-5-mini 0.748 -> 0.797, Qwen 0.718 -> 0.816 (1.59 -> 1.21), Opus 0.682 -> 0.814 (1.73 -> 1.24),
Llama 4 0.706 -> 0.755. That is question (a) almost exactly, and with the raw true-label QWK already in
the committed breadth table it nearly answers (b). So (a) and (b) are here for intervals and for the
record, not for discovery; the verdicts below do not depend on those numbers (margins come from the
paper and the floor, not from the look). The PRIMARY question is (c), which the look did not touch:
does the label add anything once BOTH arms are calibrated the same way?

THE DATA. JorGPT (Zenodo 18981627, CC BY 4.0; data/data-sources.json `jorgpt-answers`). This script
NEVER reads the corpus. It reads per-case dumps of the harness mode `attainment-swap`
(studies/measurement/grader-eval/harness/stability.ts) in the session scratchpad: per answer the entry
id, learner, question, tail, teacher mark (`human`) and three arms on identical work: `control` (no
label), `trueLabel`, `swappedLabel`. Each dump's sha256 is checked against
studies/measurement/grader-eval/analyses/per-case-dumps.sha256 (or .rebuilt.sha256) before it is read;
a mismatch stops the run. Nothing per-case is copied into the repo; out/ holds aggregates only.
Dumps: grader-vi/swap-{gemini,gpt41mini,gpt5mini,qwen}.json, breadth/swap-{opus55,llama4,g5m-min}.json.
The draw is Paper VI's attainment draw: 150 answers from 19 learners whose held-out mean is >= 6 and
150 from 14 learners with < 4 (a tails-only draw); GPT-5-mini minimal has 223 complete answers.
Transfer checks (reported only) also read grader-vi/history-gemini.json (control arm of the
grade-stratified seed-7 n=150 draw) and breadth/swap-lite-rerun.json (Gemini, same draw, second run).

THE CALIBRATION. Label-free, linear, one per grader and arm, fitted out of sample:
  MEANSD (primary)  y = mean_h + (sd_h / sd_x)(x - mean_x), moments from the training fold (pop. sd).
  LS (sensitivity)  y = mean_h + (cov_xh / var_x)(x - mean_x), least squares of teacher on grader.
Cross-fitting: LEAVE-ONE-STUDENT-OUT (primary: each learner's answers are marked with a map fitted on
the other 32 learners, both tails); LEAVE-ONE-QUESTION-OUT (secondary). Calibrated marks are rounded
half-up (JS Math.round, as harness/metrics.ts) and clipped to 0..10 BEFORE every metric; raw arms are
scored as the paper scores them (QWK rounds half-up; MAE and r on the mark as returned). QWK is the
paper's implementation (grader-attainment-prior/analyse.py `qwk`, = harness/metrics.ts; chance from
the observed marginals, quadratic weights over 0..10), copied here verbatim.

PRIMARY ESTIMANDS (signed, per model; positive QWK/r = better, negative MAE = better):
  (a) calibration gain     dQWK_a = QWK(cal control) - QWK(raw control); dMAE_a likewise.
  (b) calibration vs label dQWK_b = QWK(cal control) - QWK(raw true label); dMAE_b likewise.
  (c) label after both are calibrated (PRIMARY)
                           dQWK_c = QWK(cal true) - QWK(cal control); dMAE_c; dr_c = r(cal t) - r(cal c).
      Both arms go through the identical procedure, so the control is the size of the treatment by
      construction. If the label's raw gain was only "moving where marks land", dQWK_c ~ 0.
Intervals: 95% (and 90% for TOST) percentile, 4,000 replicates, LEARNER-CLUSTER bootstrap within tail
(the label is a property of the learner; resample learners with replacement within tail and take all
their answers), as Q2. THE CALIBRATION IS REFITTED INSIDE EVERY REPLICATE (the cross-fit is rerun on
the resampled data, holding out all copies of a learner together), so the interval includes fitting
noise. One shared learner draw per replicate is applied to every model, so a SUMMARY-SET MEAN (the mean
of the three models' deltas) has a joint interval.

PRE-REGISTERED MARGINS. m_QWK = 0.02 (the paper's resolution), m_MAE = 0.10 points (1% of the scale),
m_r = 0.02. Equivalence (TOST: 90% interval inside +/-m) is used only where the floor shows it is
reachable (rule below); otherwise the verdict string NO-ADD-BOUNDED / NO-GAIN-BOUNDED is not issued and
the result is read as an interval.

PRE-REGISTERED VERDICTS (per model and metric; signs are checked, never abs()):
  (a) CALIBRATION-GAIN        95% interval on the improving side of 0 (QWK lower > 0; MAE upper < 0)
      CALIBRATION-LOSS        95% interval on the worsening side of 0
      NO-GAIN-BOUNDED         neither, and 90% interval inside +/-m (only if reachable)
      UNRESOLVED              otherwise
  (b) CALIBRATION-AT-LEAST-MATCHES-LABEL  95% bound on the label's side does not pass -m
                              (QWK: lower95 > -m; MAE: upper95 < +m); flag `calibration_better` if
                              the 95% interval also clears 0 on calibration's side
      LABEL-BETTER            the label's arm is resolved better (QWK upper95 < 0; MAE lower95 > 0) and
                              calibration does not at least match
      UNRESOLVED              otherwise
  (c) LABEL-ADDS              95% interval on the improving side of 0; flag `within_margin` if the 90%
                              interval also lies inside +/-m (a resolved but small addition)
      LABEL-HURTS             95% interval on the worsening side of 0 (same flag)
      LABEL-ADDS-NOTHING-BOUNDED  neither, and 90% interval inside +/-m (only if reachable)
      UNRESOLVED              otherwise
  The headline metric for each question is QWK; MAE (and r for (c)) get the same strings, reported.
  ACROSS MODELS (summary set: Opus 5.5, Llama 4 Maverick, GPT-5-mini minimal), for (b) and (c):
      the common verdict if all three share it, else MIXED-ACROSS-MODELS with each; and the
      SUMMARY-SET MEAN delta with the same verdict rule (joint bootstrap). The mean's verdict is the
      across-model headline; the unanimity string is reported beside it.
  READING (fixed now): (c) LABEL-ADDS-NOTHING-BOUNDED or a within-margin result on the summary mean ->
      "the label's QWK gain is what a label-free shift and stretch buys"; LABEL-ADDS outside margin ->
      "the label carries information about the answer beyond where marks land"; LABEL-HURTS -> "once
      both are calibrated, the labelled arm is worse".

TRANSFER AND ROBUSTNESS (pre-registered as REPORTED, not verdicts):
  T1 cross-fit by question vs by student (all estimands, both procedures).
  T2 LS instead of MEANSD (all estimands).
  T3 tail transfer: the control's map fitted on one tail and applied to the other (each tail marked
     with the other tail's map); QWK, MAE and per-tail signed error, learner-cluster interval. This is
     a deliberately hostile check: the tails differ in mean by ~3 points.
  T4 the paper's concern that a calibration fixed on one draw overshoots on another: Gemini's control
     map fitted on the attainment draw (all 300) and applied to the grade-stratified history draw's
     control arm, and the reverse; and fitted on run 1 and applied to run 2 of the same draw
     (swap-lite-rerun). Point values, raw vs transferred vs in-draw cross-fit, and the overlap of the
     two draws' answers.

THE FLOOR (`--floor`, synthetic only, run and committed before any real estimand). Graders shaped like
the real ones from COMMITTED AGGREGATES ONLY (grader-model-breadth/out/models.json control bias per
tail and MAE; no arm of any dump was read to set them): on the real draw's teacher marks, learners,
tails and labels (draw.json, the dry-run draw with no model marks),
    latent = 5 + off + b (h - 5) + u_learner (sd 0.33) + e_answer (sd s_case);
    arm    = clip(round(latent [+ label effect] + call noise (sd 0.6)), 0..10).
  Shapes (off, b, s_case) fitted by grid to (bias_high, bias_low, MAE):
    OPUS  (-1.3, 0.75, 1.4)   LLAMA (-0.8, 0.80, 1.6)   G5MIN (0.0, 0.60, 1.5; run at n = 223)
    CALIBRATED (0, 1.0, 1.4) for the null of question (a).
  The learner sd 0.33 and call sd 0.6 are the Q2 floor's (deposit baseline). Every arm is one call:
  a continuous mark latent + call noise, then (for the label arm) the world's transform, then rounding.
  Worlds (what the label arm is), each run on every shape:
    NULL           a second call of the control's grader                       world (iii)
    SHIFT-STRETCH  the control's grader with its marks moved HALFWAY toward the teacher's mean and SD,
                   after the call noise: a pure shift and stretch, no information  world (i)
    INFO-STRONG    the grader's learner+answer error shrunk by 25% (K_STRONG): the label makes marks
                   track the teacher; sized so its raw QWK gain (~+0.04-0.06) is the size measured
                                                                                world (ii)
    INFO-MEASURED  latent + g (label - 5.1), g = L_measured / 3.72 (Opus 0.074, Llama 0.144, G5MIN
                   0.281): the measured label effect read as a label-keyed shift; REPORTED only
                   (what (c) would look like if all of the measured L were tail information)
    LABEL-WINS     INFO-STRONG's grader already on the teacher's mean and SD (the label both
                   calibrates and informs), for (b)'s LABEL-BETTER
  EXPECTED VERDICTS are fixed by each world's PLANTED value (mean over 40 synthetic draws, no bootstrap;
  `expected_from_planted`): (a) GAIN if planted dQWK_a >= 0.04, NO-GAIN-BOUNDED if |.| <= 0.01;
  (b) AT-LEAST-MATCHES if planted dQWK_b >= +0.045, LABEL-BETTER if <= -0.07; (c) NO-ADD-BOUNDED if
  |planted dQWK_c| <= 0.01, LABEL-ADDS if >= 0.05 (not for INFO-MEASURED); otherwise that estimand is
  reported for that world, not scored. (Probing before this was fixed showed some shapes make an
  estimand ambiguous: e.g. a G5MIN-shaped grader is near the teacher's mean and SD, so calibrating it
  buys ~0; such a world is not scored on (a). The (b) thresholds were widened from +0.03 / -0.05 after a
  10-replicate synthetic smoke run showed (b)'s per-model SE is ~0.02-0.025, so a world is scored only
  where its planted value is ~3 SE from the decision boundary. No real number had been read.)
  SUMMARY-SET FLOOR (`floor_summary`): the three harsh shapes simulated together on one shared learner
  bootstrap (G5MIN at n = 223), the mean of their deltas, the same rules: NULL and SHIFT-STRETCH ->
  NO-ADD-BOUNDED on (c) (reachability of the bounded string for the summary mean), INFO-STRONG ->
  LABEL-ADDS. Same pass rules.
  PASS RULES: for every scored (world, estimand), >= 80% of replicates return the expected verdict and
  <= 10% the opposite resolved sign (GAIN vs LOSS; LABEL-BETTER vs AT-LEAST; ADDS vs HURTS; for an
  expected equivalence, any resolved effect). EQUIVALENCE REACHABILITY: if every scored equivalence
  check for a shape hits >= 80%, the bounded string is REACHABLE for that shape and estimand; if not,
  that check passes on "<= 10% resolved" alone, the bounded string is withheld for the matching real
  model and its result is read as an interval. Real-model shape map: Opus -> OPUS, Llama -> LLAMA,
  GPT-5-mini minimal -> G5MIN (n = 223); GPT-4.1-mini, GPT-5-mini default, Qwen -> HARSH-ALL (bounded
  only if all three harsh shapes reached it); Gemini -> CALIBRATED.
  If any pass rule fails, no real number is read until the instrument is revised and the revision
  recorded here. A grader written and scored by this session is a smoke check of the instrument on
  worlds it was told about, not a validation; it is reported as one.

FLOOR RESULT (run 2026-10-06, before any real estimand; out/floor.json; 200 replicates x 400 bootstrap
per world). PASS on every scored check. Equivalence: (a) NO-GAIN-BOUNDED reachable only for the
CALIBRATED shape (200/200 in its worlds), so only Gemini can return it; (c) LABEL-ADDS-NOTHING-BOUNDED
is UNREACHABLE for every shape and for the summary-set mean (NULL 3/200 Opus, 9/200 Llama, 0/200 G5MIN,
92/200 calibrated; summary mean 72/200 NULL, 28/200 SHIFT-STRETCH). So, as pre-registered, the bounded
string is withheld everywhere and (c) is READ AS AN INTERVAL: "once both arms are calibrated the label
adds no more than X QWK", X = the 95% upper bound (`largest_addition_admitted`), beside any resolved
LABEL-ADDS / LABEL-HURTS. False resolved effects in no-information worlds: <= 6% per shape (NULL),
<= 7.5% (SHIFT-STRETCH, calibrated shape), 5% on the summary mean. Power: a label that tracks the
teacher (INFO-STRONG, planted dQWK_c +0.06 to +0.07) is called LABEL-ADDS in 200/200 (Opus, Llama),
189/200 (G5MIN, n = 223) and 200/200 on the summary mean. At the MEASURED label size read as pure
information (INFO-MEASURED, reported): planted dQWK_c +0.011 Opus, +0.021 Llama, +0.053 G5MIN, called
LABEL-ADDS 13%, 32%, 69%: a per-model null on Opus or Llama does not exclude information of the
measured size. (b) LABEL-BETTER where planted (LABEL-WINS) 200/200 on all three shapes; AT-LEAST on the
Opus shape 200/200. The (c) interval width per model is ~+/-0.04 (Opus, Llama).

DEVIATION 1 (recorded after the real run, before anything was written up). The primary filter keeps
rows with both a control and a true-label mark (the swapped arm is not used here), as the committed
code says; the docstring's "223 complete" for GPT-5-mini minimal counted rows complete in ALL THREE
arms. Rows actually used: Gemini 300, GPT-4.1-mini 300, GPT-5-mini default 298, Qwen 291, Opus 300,
Llama 300, GPT-5-mini minimal 242 (the floor's G5MIN shape at 223 is therefore slightly conservative).
The primary result stands as pre-registered; a sensitivity on the paper's basis (rows complete in all
three arms, `--all-arms`, out/results-all-arms.json, same seed and reps) is reported beside it.

THE GATE. `--run` refuses unless out/floor.json exists, its pass rules hold, and this script and
out/floor.json are committed unchanged (git diff against HEAD is empty), so the pre-registration and
floor are on record before any real estimand is computed.

Usage:
  python3 calibrate.py --floor  --draw <scratch>/grader-vi/draw.json
  python3 calibrate.py --run    --scratch <scratch>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
REPO = HERE.parents[2]
MANIFESTS = [REPO / "studies/measurement/grader-eval/analyses/per-case-dumps.sha256",
             REPO / "studies/measurement/grader-eval/analyses/per-case-dumps.rebuilt.sha256"]
REPS = 4000
FLOOR_REPS = 200
FLOOR_BOOT = 400
SCALE = (0, 10)
M = {"qwk": 0.02, "mae": 0.10, "r": 0.02}

DUMPS = {  # tag: (scratch path, floor shape, in summary set)
    "gemini-3.5-flash-lite": ("grader-vi/swap-gemini.json", "CALIBRATED", False),
    "gpt-4.1-mini": ("grader-vi/swap-gpt41mini.json", "HARSH-ALL", False),
    "gpt-5-mini (default)": ("grader-vi/swap-gpt5mini.json", "HARSH-ALL", False),
    "qwen3-235b": ("grader-vi/swap-qwen.json", "HARSH-ALL", False),
    "claude-opus-5.5": ("breadth/swap-opus55.json", "OPUS", True),
    "llama-4-maverick": ("breadth/swap-llama4.json", "LLAMA", True),
    "gpt-5-mini (minimal)": ("breadth/swap-g5m-min.json", "G5MIN", True),
}
SUMMARY = [k for k, v in DUMPS.items() if v[2]]


# ----------------------------------------------------------------------------- metrics

def round_half_up(x):
    """JS Math.round, which the harness's QWK uses; numpy's round is half-to-even."""
    return np.floor(np.asarray(x, float) + 0.5)


def qwk(h, m, lo: int = SCALE[0], hi: int = SCALE[1]) -> float:
    """Verbatim from grader-attainment-prior/analyse.py (= harness/metrics.ts)."""
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


def pearson(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    sa, sb = a.std(), b.std()
    return float(((a - a.mean()) * (b - b.mean())).mean() / (sa * sb)) if sa > 0 and sb > 0 else 0.0


def finish(y):
    return np.clip(round_half_up(y), *SCALE)


# ----------------------------------------------------------------------------- calibration

def crossfit(x, h, groups, method: str = "meansd"):
    """Out-of-sample linear map: each group's rows are mapped with moments from all OTHER groups.
    `groups` are original ids, so duplicated copies of a learner in a bootstrap are held out together."""
    _, g = np.unique(groups, return_inverse=True)
    G = g.max() + 1
    bc = lambda v: np.bincount(g, weights=v, minlength=G)  # noqa: E731
    n = np.bincount(g, minlength=G).astype(float)
    S = {k: bc(v) for k, v in (("x", x), ("h", h), ("xx", x * x), ("hh", h * h), ("xh", x * h))}
    N = n.sum() - n
    T = {k: v.sum() - v for k, v in S.items()}
    mx, mh = T["x"] / N, T["h"] / N
    vx = np.maximum(T["xx"] / N - mx ** 2, 1e-12)
    vh = np.maximum(T["hh"] / N - mh ** 2, 0.0)
    if method == "meansd":
        slope = np.sqrt(vh / vx)
    else:
        slope = (T["xh"] / N - mx * mh) / vx
    return finish(mh[g] + slope[g] * (x - mx[g]))


def fit_apply(x_fit, h_fit, x_new, method: str = "meansd"):
    mx, mh = x_fit.mean(), h_fit.mean()
    slope = h_fit.std() / x_fit.std() if method == "meansd" else np.cov(x_fit, h_fit, bias=True)[0, 1] / x_fit.var()
    return finish(mh + slope * (x_new - mx))


# ----------------------------------------------------------------------------- estimands

class Data:
    def __init__(self, rows: list[dict]):
        self.h = np.array([r["human"] for r in rows], float)
        self.c = np.array([r["control"] for r in rows], float)
        self.t = np.array([r["trueLabel"] for r in rows], float)
        self.hi = np.array([r["tail"] == "high" for r in rows])
        self.learner = np.array([str(r["learnerId"]) for r in rows])
        self.question = np.array([str(r["questionId"]) for r in rows])
        self.ids = [str(r["id"]) for r in rows]
        self.by_learner = {k: np.flatnonzero(self.learner == k) for k in np.unique(self.learner)}


def estimands(d: Data, idx, by: str = "learner", method: str = "meansd") -> dict[str, float]:
    h, c, t = d.h[idx], d.c[idx], d.t[idx]
    grp = (d.learner if by == "learner" else d.question)[idx]
    cc, ct = crossfit(c, h, grp, method), crossfit(t, h, grp, method)
    m = lambda x: float(np.abs(x - h).mean())  # noqa: E731
    o = {"qwk_raw_c": qwk(h, c), "qwk_raw_t": qwk(h, t), "qwk_cal_c": qwk(h, cc), "qwk_cal_t": qwk(h, ct),
         "mae_raw_c": m(c), "mae_raw_t": m(t), "mae_cal_c": m(cc), "mae_cal_t": m(ct),
         "r_raw_c": pearson(h, c), "r_raw_t": pearson(h, t), "r_cal_c": pearson(h, cc), "r_cal_t": pearson(h, ct),
         "bias_raw_c": float((c - h).mean()), "bias_cal_c": float((cc - h).mean()),
         "bias_raw_t": float((t - h).mean()), "bias_cal_t": float((ct - h).mean())}
    for k in ("qwk", "mae"):
        o[f"a_{k}"] = o[f"{k}_cal_c"] - o[f"{k}_raw_c"]
        o[f"b_{k}"] = o[f"{k}_cal_c"] - o[f"{k}_raw_t"]
    for k in ("qwk", "mae", "r"):
        o[f"c_{k}"] = o[f"{k}_cal_t"] - o[f"{k}_cal_c"]
    o["raw_label_qwk"] = o["qwk_raw_t"] - o["qwk_raw_c"]
    o["raw_label_r"] = o["r_raw_t"] - o["r_raw_c"]
    return o


def tail_transfer(d: Data, idx) -> dict[str, float]:
    """T3: each tail's control marks mapped with the OTHER tail's MEANSD map."""
    h, c, hi = d.h[idx], d.c[idx], d.hi[idx]
    y = np.empty_like(c)
    y[hi] = fit_apply(c[~hi], h[~hi], c[hi])
    y[~hi] = fit_apply(c[hi], h[hi], c[~hi])
    return {"qwk_tail_transfer": qwk(h, y), "mae_tail_transfer": float(np.abs(y - h).mean()),
            "bias_tail_transfer_high": float((y - h)[hi].mean()), "bias_tail_transfer_low": float((y - h)[~hi].mean())}


def learner_draw(ids_by_tail: dict[bool, np.ndarray], rng) -> list[str]:
    out = []
    for tail in (True, False):
        ids = ids_by_tail[tail]
        out.extend(rng.choice(ids, size=len(ids), replace=True))
    return out


def rows_for(d: Data, learners: list[str]) -> np.ndarray:
    parts = [d.by_learner[k] for k in learners if k in d.by_learner]
    return np.concatenate(parts)


def summarise(point: dict, draws: list[dict]) -> dict:
    res = {}
    for k, v in point.items():
        a = np.array([x[k] for x in draws])
        res[k] = {"est": v, "ci95": [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))],
                  "ci90": [float(np.percentile(a, 5)), float(np.percentile(a, 95))]}
    return res


# ----------------------------------------------------------------------------- verdicts

def better_sign(metric: str) -> int:
    return -1 if metric == "mae" else 1


def v_a(e: dict, metric: str, bounded_ok: bool) -> str:
    s = better_sign(metric)
    lo, hi = (e["ci95"][0], e["ci95"][1]) if s > 0 else (-e["ci95"][1], -e["ci95"][0])  # in 'better' units
    if lo > 0:
        return "CALIBRATION-GAIN"
    if hi < 0:
        return "CALIBRATION-LOSS"
    if bounded_ok and -M[metric] < e["ci90"][0] and e["ci90"][1] < M[metric]:
        return "NO-GAIN-BOUNDED"
    return "UNRESOLVED"


def v_b(e: dict, metric: str) -> dict:
    """e is cal control minus raw true label."""
    s = better_sign(metric)
    lo, hi = (e["ci95"][0], e["ci95"][1]) if s > 0 else (-e["ci95"][1], -e["ci95"][0])  # in 'better' units
    if lo > -M[metric]:
        return {"verdict": "CALIBRATION-AT-LEAST-MATCHES-LABEL", "calibration_better": bool(lo > 0)}
    if hi < 0:
        return {"verdict": "LABEL-BETTER", "calibration_better": False}
    return {"verdict": "UNRESOLVED", "calibration_better": False}


def v_c(e: dict, metric: str, bounded_ok: bool) -> dict:
    """e is cal true minus cal control."""
    s = better_sign(metric)
    lo, hi = (e["ci95"][0], e["ci95"][1]) if s > 0 else (-e["ci95"][1], -e["ci95"][0])
    inside = -M[metric] < e["ci90"][0] and e["ci90"][1] < M[metric]
    b = {"largest_addition_admitted": float(hi), "largest_harm_admitted": float(-lo)}  # 95%, 'better' units
    if lo > 0:
        return {"verdict": "LABEL-ADDS", "within_margin": bool(inside), **b}
    if hi < 0:
        return {"verdict": "LABEL-HURTS", "within_margin": bool(inside), **b}
    if bounded_ok and inside:
        return {"verdict": "LABEL-ADDS-NOTHING-BOUNDED", "within_margin": True, **b}
    return {"verdict": "UNRESOLVED", "within_margin": bool(inside), **b}


def verdicts(R: dict, bounded_a: bool, bounded_c: bool) -> dict:
    return {"a": {m: v_a(R[f"a_{m}"], m, bounded_a) for m in ("qwk", "mae")},
            "b": {m: v_b(R[f"b_{m}"], m) for m in ("qwk", "mae")},
            "c": {m: v_c(R[f"c_{m}"], m, bounded_c) for m in ("qwk", "mae", "r")}}


# ----------------------------------------------------------------------------- the floor

SHAPES = {"OPUS": (-1.3, 0.75, 1.4, 0.074, None), "LLAMA": (-0.8, 0.80, 1.6, 0.144, None),
          "G5MIN": (0.0, 0.60, 1.5, 0.281, 223), "CALIBRATED": (0.0, 1.0, 1.4, 0.0, None)}
LABEL_MEAN = 5.1          # ~ midpoint of the two tails' labels (6.96, 3.24) on the draw
K_STRONG = 0.25           # the label arm's answer+learner error shrunk by this fraction
WORLDS = ("NULL", "SHIFT-STRETCH", "INFO-STRONG", "INFO-MEASURED", "LABEL-WINS")


def expected_from_planted(world: str, p: dict) -> dict:
    """The verdict each world should return, fixed by its PLANTED value (40 synthetic draws, no
    bootstrap), so a world whose shape makes an estimand ambiguous is not scored on it."""
    e = {}
    if p["a_qwk"] >= 0.04:
        e["a"] = "CALIBRATION-GAIN"
    elif abs(p["a_qwk"]) <= 0.01:
        e["a"] = "NO-GAIN-BOUNDED"
    if p["b_qwk"] >= 0.045:
        e["b"] = "CALIBRATION-AT-LEAST-MATCHES-LABEL"
    elif p["b_qwk"] <= -0.07:
        e["b"] = "LABEL-BETTER"
    if world != "INFO-MEASURED":
        if abs(p["c_qwk"]) <= 0.01:
            e["c"] = "LABEL-ADDS-NOTHING-BOUNDED"
        elif p["c_qwk"] >= 0.05:
            e["c"] = "LABEL-ADDS"
    return e


OPPOSITE = {"CALIBRATION-GAIN": "CALIBRATION-LOSS", "CALIBRATION-LOSS": "CALIBRATION-GAIN",
            "NO-GAIN-BOUNDED": None,
            "CALIBRATION-AT-LEAST-MATCHES-LABEL": "LABEL-BETTER", "LABEL-BETTER": "CALIBRATION-AT-LEAST-MATCHES-LABEL",
            "LABEL-ADDS": "LABEL-HURTS", "LABEL-HURTS": "LABEL-ADDS", "LABEL-ADDS-NOTHING-BOUNDED": None}


def synth(draw: list[dict], shape: str, world: str, rng) -> list[dict]:
    off, b, sc, g_meas, _ = SHAPES[shape]
    learners = sorted({r["learnerId"] for r in draw})
    lv = dict(zip(learners, rng.normal(0, 0.33, len(learners))))
    h = np.array([r["human"] for r in draw], float)
    lab = np.array([r["labelTrue"] for r in draw], float)
    err = np.array([lv[r["learnerId"]] for r in draw]) + rng.normal(0, sc, len(h))
    latent = 5 + off + b * (h - 5) + err
    noisy = lambda x: x + rng.normal(0, 0.6, len(h))                     # one call's continuous mark  # noqa: E731
    fin = lambda x: np.clip(round_half_up(x), *SCALE)                      # noqa: E731
    xc = noisy(latent)
    if world == "NULL":
        xt = noisy(latent)
    elif world == "SHIFT-STRETCH":
        # the label arm is the control's grader with its marks moved HALFWAY toward the teacher's mean
        # and SD, applied after the call noise: a pure shift and stretch, no information
        x = noisy(latent)
        mu, sd = x.mean(), x.std()
        xt = mu + 0.5 * (h.mean() - mu) + (1 + 0.5 * (h.std() / sd - 1)) * (x - mu)
    elif world == "INFO-STRONG":
        xt = noisy(latent - K_STRONG * err)                                 # tracks the teacher better
    elif world == "INFO-MEASURED":
        xt = noisy(latent + g_meas * (lab - LABEL_MEAN))                    # measured L as a label-keyed shift
    elif world == "LABEL-WINS":
        x = noisy(latent - K_STRONG * err)                                  # INFO-STRONG, already on the
        xt = h.mean() + h.std() * (x - x.mean()) / x.std()                  # teacher's mean and SD
    else:
        raise ValueError(world)
    c, t = fin(xc), fin(xt)
    return [{**r, "control": float(c[i]), "trueLabel": float(t[i]), "swappedLabel": None} for i, r in enumerate(draw)]


def boot(d: Data, reps: int, rng) -> dict:
    point = estimands(d, np.arange(len(d.h)))
    ids = {t: np.unique(d.learner[d.hi == t]) for t in (True, False)}
    draws = [estimands(d, rows_for(d, learner_draw(ids, rng))) for _ in range(reps)]
    return summarise(point, draws)


def run_floor(draw_path: Path) -> dict:
    draw_all = json.loads(draw_path.read_text())["rows"]
    rng = np.random.default_rng(20261006)
    report = {}
    plan = [(s, w) for s in SHAPES for w in WORLDS]
    for shape, world in plan:
        n_keep = SHAPES[shape][4]
        sub = sorted(rng.choice(len(draw_all), n_keep, replace=False)) if n_keep else range(len(draw_all))
        draw = [draw_all[i] for i in sub]
        # planted values: 40 synthetic draws, point estimates, no bootstrap
        P = [estimands(Data(synth(draw, shape, world, rng)), np.arange(len(draw))) for _ in range(40)]
        planted = {k: float(np.mean([p[k] for p in P])) for k in ("a_qwk", "b_qwk", "c_qwk", "c_r", "c_mae",
                                                                    "raw_label_qwk", "qwk_raw_c", "qwk_cal_c")}
        got = {"a": [], "b": [], "c": []}
        for _ in range(FLOOR_REPS):
            R = boot(Data(synth(draw, shape, world, rng)), FLOOR_BOOT, rng)
            got["a"].append(v_a(R["a_qwk"], "qwk", True))
            got["b"].append(v_b(R["b_qwk"], "qwk")["verdict"])
            got["c"].append(v_c(R["c_qwk"], "qwk", True)["verdict"])
        expect = expected_from_planted(world, planted)
        rec = {"n": len(draw), "planted": planted, "checks": {}}
        for est, vs in got.items():
            counts = {v: vs.count(v) for v in sorted(set(vs))}
            e = expect.get(est)
            chk = {"expected": e, "verdicts": counts}
            if e:
                chk["hit_rate"] = vs.count(e) / len(vs)
                opp = OPPOSITE[e]
                if opp is None:   # equivalence expected: the wrong sign is any resolved effect
                    wrong = sum(v in ("LABEL-ADDS", "LABEL-HURTS", "CALIBRATION-GAIN", "CALIBRATION-LOSS") for v in vs)
                else:
                    wrong = vs.count(opp)
                chk["wrong_sign_rate"] = wrong / len(vs)
                chk["pass_strict"] = chk["hit_rate"] >= 0.8 and chk["wrong_sign_rate"] <= 0.10
                # equivalence fallback (pre-registered): bounded string unreachable -> pass if <=10% resolved
                chk["pass"] = chk["pass_strict"] or (opp is None and chk["wrong_sign_rate"] <= 0.10)
            rec["checks"][est] = chk
            print(f"  {shape:10s} {world:14s} ({est}) expect {str(e):36s} {counts}"
                  + (f"  {'PASS' if chk.get('pass') else 'FAIL'}{'' if chk.get('pass_strict', True) else ' (equivalence unreachable)'}" if e else ""),
                  flush=True)
        print(f"  {shape:10s} {world:14s} planted {json.dumps({k: round(v, 4) for k, v in planted.items()})}", flush=True)
        report[f"{shape}/{world}"] = rec
    def reachable(shape: str, est: str) -> bool:
        cs = [r["checks"][est] for k, r in report.items() if k.startswith(shape + "/")
              and r["checks"][est]["expected"] in ("NO-GAIN-BOUNDED", "LABEL-ADDS-NOTHING-BOUNDED")]
        return bool(cs) and all(c["pass_strict"] for c in cs)

    reach = {s: {e: reachable(s, e) for e in ("a", "c")} for s in SHAPES}
    reach["HARSH-ALL"] = {e: all(reach[s][e] for s in ("OPUS", "LLAMA", "G5MIN")) for e in ("a", "c")}
    summary = floor_summary(draw_all, rng)
    reach["SUMMARY-MEAN"] = {"c": all(summary[w]["pass_strict"] for w in ("NULL", "SHIFT-STRETCH"))}
    ok = all(c.get("pass", True) for r in report.values() for c in r["checks"].values())
    ok = ok and all(v["pass"] for v in summary.values())
    return {"pass": ok, "replicates": FLOOR_REPS, "bootstrap": FLOOR_BOOT, "equivalence_reachable": reach,
            "worlds": report, "summary_mean": summary, "margins": M,
            "note": "smoke check: synthetic graders written and scored by the same session; shapes from committed aggregates only"}


def floor_summary(draw_all: list[dict], rng) -> dict:
    shapes = ("OPUS", "LLAMA", "G5MIN")
    subs = {sh: (sorted(rng.choice(len(draw_all), SHAPES[sh][4], replace=False)) if SHAPES[sh][4]
                 else list(range(len(draw_all)))) for sh in shapes}
    out = {}
    for world, want in (("NULL", "LABEL-ADDS-NOTHING-BOUNDED"), ("SHIFT-STRETCH", "LABEL-ADDS-NOTHING-BOUNDED"),
                        ("INFO-STRONG", "LABEL-ADDS")):
        vs = []
        for _ in range(FLOOR_REPS):
            D = {sh: Data(synth([draw_all[i] for i in subs[sh]], sh, world, rng)) for sh in shapes}
            ref = D["OPUS"]
            ids = {t: np.unique(ref.learner[ref.hi == t]) for t in (True, False)}
            pt = float(np.mean([estimands(D[sh], np.arange(len(D[sh].h)))["c_qwk"] for sh in shapes]))
            dr = []
            for _ in range(FLOOR_BOOT):
                L = learner_draw(ids, rng)
                dr.append({"c_qwk": float(np.mean([estimands(D[sh], rows_for(D[sh], L))["c_qwk"] for sh in shapes]))})
            vs.append(v_c(summarise({"c_qwk": pt}, dr)["c_qwk"], "qwk", True)["verdict"])
        hit = vs.count(want) / len(vs)
        wrong = (sum(v in ("LABEL-ADDS", "LABEL-HURTS") for v in vs) if want != "LABEL-ADDS"
                 else vs.count("LABEL-HURTS")) / len(vs)
        strict = hit >= 0.8 and wrong <= 0.10
        out[world] = {"expected": want, "verdicts": {v: vs.count(v) for v in sorted(set(vs))}, "hit_rate": hit,
                      "wrong_sign_rate": wrong, "pass_strict": strict,
                      "pass": strict or (want != "LABEL-ADDS" and wrong <= 0.10)}
        print(f"  SUMMARY    {world:14s} (c) expect {want:36s} {out[world]['verdicts']}  "
              f"{'PASS' if out[world]['pass'] else 'FAIL'}", flush=True)
    return out


# ----------------------------------------------------------------------------- the real run

def manifest() -> dict[str, str]:
    out = {}
    for p in MANIFESTS:
        for line in p.read_text().splitlines():
            if line.strip():
                h, name = line.split()
                out.setdefault(name, set()).add(h)
    return out


def verified(scratch: Path, rel: str, man: dict) -> dict:
    p = scratch / rel
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    if digest not in man.get(rel, set()):
        sys.exit(f"sha256 mismatch for {rel}: {digest}; not read")
    return json.loads(p.read_text())


def gate() -> dict:
    fl = OUT / "floor.json"
    if not fl.exists():
        sys.exit("no floor; run --floor first")
    dirty = subprocess.run(["git", "status", "--porcelain", "--", str(Path(__file__)), str(fl)],
                           cwd=REPO, capture_output=True, text=True).stdout.strip()
    if dirty:
        sys.exit(f"pre-registration or floor not committed unchanged:\n{dirty}")
    f = json.loads(fl.read_text())
    if not f["pass"]:
        sys.exit("floor failed; no real number is read")
    return f


def run(scratch: Path, all_arms: bool = False) -> dict:
    floor = gate() if not all_arms else json.loads((OUT / "floor.json").read_text())
    reach = floor["equivalence_reachable"]
    man = manifest()
    data, meta = {}, {}
    for tag, (rel, shape, _) in DUMPS.items():
        blob = verified(scratch, rel, man)
        need = ("control", "trueLabel", "swappedLabel") if all_arms else ("control", "trueLabel")
        rows = [r for r in blob["rows"] if None not in tuple(r[k] for k in need)]
        data[tag] = Data(rows)
        meta[tag] = {"dump": rel, "model": blob["model"], "reasoning": blob.get("reasoning", "provider default"),
                     "run": blob.get("runStamp"), "n_rows": len(blob["rows"]), "n_complete": len(rows),
                     "learners": len(data[tag].by_learner), "shape": shape}
    # one shared learner population (all models ran the same draw)
    ref = data["gemini-3.5-flash-lite"]
    ids = {t: np.unique(ref.learner[ref.hi == t]) for t in (True, False)}
    schemes = {"student": ("learner", "meansd"), "question": ("question", "meansd"), "student_ls": ("learner", "ls")}
    rng = np.random.default_rng(1006)
    points = {tag: {s: estimands(d, np.arange(len(d.h)), *schemes[s]) for s in schemes} for tag, d in data.items()}
    for tag, d in data.items():
        points[tag]["student"].update(tail_transfer(d, np.arange(len(d.h))))
    draws = {tag: {s: [] for s in schemes} for tag in data}
    for _ in range(REPS):
        L = learner_draw(ids, rng)
        for tag, d in data.items():
            idx = rows_for(d, L)
            for s in schemes:
                e = estimands(d, idx, *schemes[s])
                if s == "student":
                    e.update(tail_transfer(d, idx))
                draws[tag][s].append(e)
    res = {"meta": meta, "margins": M, "bootstrap_reps": REPS, "summary_set": SUMMARY, "per_model": {}}
    for tag in data:
        shape = meta[tag]["shape"]
        R = {s: summarise(points[tag][s], draws[tag][s]) for s in schemes}
        # direction check: the calibrated control's mean error must be closer to 0 than the raw one's,
        # on the side the map was meant to move it (signed, not abs of a difference)
        braw, bcal = R["student"]["bias_raw_c"]["est"], R["student"]["bias_cal_c"]["est"]
        assert abs(bcal) < abs(braw) or abs(braw) < 0.1, (tag, braw, bcal)
        res["per_model"][tag] = {
            "verdicts": verdicts(R["student"], reach[shape]["a"], reach[shape]["c"]),
            "bounded_strings_available": reach[shape],
            "student": R["student"], "sensitivity_question_crossfit": R["question"],
            "sensitivity_least_squares": R["student_ls"],
            "verdicts_question_crossfit_reported": verdicts(R["question"], reach[shape]["a"], reach[shape]["c"]),
            "verdicts_least_squares_reported": verdicts(R["student_ls"], reach[shape]["a"], reach[shape]["c"]),
        }
    # summary-set mean, joint bootstrap
    summ = {}
    bounded_c = reach["SUMMARY-MEAN"]["c"]
    for s in schemes:
        keys = ("b_qwk", "b_mae", "c_qwk", "c_mae", "c_r", "a_qwk", "a_mae", "raw_label_qwk")
        pt = {k: float(np.mean([points[t][s][k] for t in SUMMARY])) for k in keys}
        dr = [{k: float(np.mean([draws[t][s][i][k] for t in SUMMARY])) for k in keys} for i in range(REPS)]
        Rm = summarise(pt, dr)
        summ[s] = {"stats": Rm,
                   "b": {m: v_b(Rm[f"b_{m}"], m) for m in ("qwk", "mae")},
                   "c": {m: v_c(Rm[f"c_{m}"], m, bounded_c) for m in ("qwk", "mae", "r")}}
    uni = {}
    for q in ("b", "c"):
        vs = {t: res["per_model"][t]["verdicts"][q]["qwk"]["verdict"] for t in SUMMARY}
        uni[q] = next(iter(vs.values())) if len(set(vs.values())) == 1 else {"MIXED-ACROSS-MODELS": vs}
    res["summary"] = {"mean_student": summ["student"], "mean_question_crossfit": summ["question"],
                      "mean_least_squares": summ["student_ls"], "unanimity_qwk": uni}
    res["transfer_cross_draw"] = cross_draw(scratch, man, data["gemini-3.5-flash-lite"])
    return res


def cross_draw(scratch: Path, man: dict, att: Data) -> dict:
    """T4, Gemini only: maps fixed on one draw/run applied to another. Point values."""
    hist = verified(scratch, "grader-vi/history-gemini.json", man)
    arm = hist["arms"][0]
    hr = [r for r in hist["rows"] if r[arm] is not None]
    hh = np.array([r["human"] for r in hr], float)
    hc = np.array([r[arm] for r in hr], float)
    hl = np.array([str(r["learnerId"]) for r in hr])
    rer = verified(scratch, "breadth/swap-lite-rerun.json", man)
    rr = [r for r in rer["rows"] if r["control"] is not None]
    rh = np.array([r["human"] for r in rr], float)
    rc = np.array([r["control"] for r in rr], float)
    m = lambda h, x: {"qwk": qwk(h, x), "mae": float(np.abs(x - h).mean()), "bias": float((x - h).mean())}  # noqa: E731
    overlap = len({str(r["id"]) for r in hr} & set(att.ids))
    return {
        "history_arm": arm,
        "attainment_to_history": {"n": len(hr), "raw": m(hh, hc), "transferred": m(hh, fit_apply(att.c, att.h, hc)),
                                  "in_draw_loso": m(hh, crossfit(hc, hh, hl))},
        "history_to_attainment": {"n": len(att.h), "raw": m(att.h, att.c),
                                  "transferred": m(att.h, fit_apply(hc, hh, att.c)),
                                  "in_draw_loso": m(att.h, crossfit(att.c, att.h, att.learner))},
        "run1_to_run2_same_draw": {"n": len(rr), "raw": m(rh, rc), "transferred": m(rh, fit_apply(att.c, att.h, rc)),
                                   "in_draw_loso": m(rh, crossfit(rc, rh, np.array([str(r["learnerId"]) for r in rr])))},
        "answers_in_both_draws": overlap,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--floor", action="store_true")
    ap.add_argument("--draw", type=Path)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--scratch", type=Path)
    ap.add_argument("--all-arms", action="store_true",
                    help="DEVIATION 1 sensitivity: only rows complete in all three arms (the paper's basis)")
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    if a.floor:
        res = run_floor(a.draw)
        (OUT / "floor.json").write_text(json.dumps(res, indent=2) + "\n")
        print("FLOOR", "PASS" if res["pass"] else "FAIL", json.dumps(res["equivalence_reachable"]))
        sys.exit(0 if res["pass"] else 1)
    if a.run:
        res = run(a.scratch, a.all_arms)
        name = "results-all-arms.json" if a.all_arms else "results.json"
        (OUT / name).write_text(json.dumps(res, indent=2) + "\n")
        report(res)


def report(res: dict) -> None:
    f = lambda e: f"{e['est']:+.3f} [{e['ci95'][0]:+.3f}, {e['ci95'][1]:+.3f}]"  # noqa: E731
    for tag, v in res["per_model"].items():
        S = v["student"]
        print(f"\n{tag}  n={res['meta'][tag]['n_complete']}  QWK raw c {S['qwk_raw_c']['est']:.3f} raw t {S['qwk_raw_t']['est']:.3f}"
              f" cal c {S['qwk_cal_c']['est']:.3f} cal t {S['qwk_cal_t']['est']:.3f}")
        for k in ("a_qwk", "a_mae", "b_qwk", "b_mae", "c_qwk", "c_mae", "c_r", "raw_label_qwk", "qwk_tail_transfer"):
            print(f"  {k:18s} {f(S[k])}   q-xfit {f(v['sensitivity_question_crossfit'][k]) if k in v['sensitivity_question_crossfit'] else ''}"
                  f"   LS {f(v['sensitivity_least_squares'][k]) if k in v['sensitivity_least_squares'] else ''}")
        print("  verdicts", json.dumps(v["verdicts"]))
    s = res["summary"]["mean_student"]
    print("\nSUMMARY MEAN", {k: f(s["stats"][k]) for k in ("b_qwk", "c_qwk", "c_mae", "c_r")})
    print("  b", s["b"], " c", s["c"], " unanimity", res["summary"]["unanimity_qwk"])
    print("\nCROSS-DRAW", json.dumps(res["transfer_cross_draw"], indent=1))


if __name__ == "__main__":
    main()
