#!/usr/bin/env python3
"""
Do graded exemplars calibrate the grader by carrying CORRECT marks, or only by showing the SCALE?
Paper VI section 5.4, re-tested (2026-10-05).

WHAT WAS ASKED. Paper VI (research/article/attainment-bias-in-llm-grading.md, release
ai-grader-reliability-2026 1.0.0, evidence record lazuli-grader-jorgpt-2026/exemplar-calibration)
reports, on JorGPT with Gemini 3.5 Flash Lite (Model.LITE, thinking off), n = 150 stratified, seed 7:

    control (no exemplars)      QWK 0.840  MAE 1.24  bias +0.38
    3 graded anchors            QWK 0.840  MAE 1.22  bias +0.06   drift -0.32
    3 anchors, marks removed    QWK 0.821  MAE 1.26  bias +0.63   drift +0.26

and reads it as "the gain comes from the marks -- from information about where this rubric places a
3 and where it places an 8". The literature review for the release
(research/readiness/ai-grader-reliability-2026/literature.md: Min et al. 2022, with the rebuttals
Yoo et al. 2022 and Wei et al. 2023) raises the rival: in-context demonstrations can work by showing
the label SPACE and FORMAT, with the correctness of the labels mattering little. Here that means the
marks may calibrate by showing a 0-to-10 scale in use, not by pairing each answer with its right
mark. The original design cannot tell these apart: its only contrast is marks versus no marks.

THE DATA. JorGPT (Zenodo 18981627, CC BY 4.0; data/data-sources.json `jorgpt-answers`). This script
NEVER reads the corpus. It reads the per-case dumps written by the harness mode `exemplar-marks`
(studies/measurement/grader-eval/harness/stability.ts), which hold entry ids, question and learner
ids, the teacher grade, the three anchors' teacher marks, the marks each arm showed, and the model's
score per arm. Dumps stay in the session scratchpad; only aggregates in `out/` are committed.

THE DRAW. `stratifiedSample(all, 600, seed 7)`: 600 teacher-corrected answers, 54-55 per grade
level 0..10, 50 questions, 79 learners. The sampler is prefix-stable, so its first 150 cases are the
original run's 150 exactly (and the replication model's). Anchors are the original's: from the same
question, excluding the answer being graded, the lowest, median and highest by teacher grade, in that
order. Every drawn case has three. `render_check.py` shows (out/render-check.json) that the mode at
n 300 sends every one of the original run's 450 prompts byte for byte (vendor/934478716, `--mode
exemplars --n 150`) plus 1,350 new ones.

MODELS, SIZES AND THE STOP RULE (fixed here, before any call):
  primary      google:gemini-3.5-flash-lite (Model.LITE, thinking off; the model the release names
               for this arm), n = 600, 3,600 gradings, run first, --max-calls 3700.
  replication  openai:gpt-4.1-mini at its defaults, n = 150 (the original 150 cases), 900 gradings,
               --max-calls 950. Runs ONLY IF the Gemini run's measured cost (its dump's provider
               token counts x list price) plus GPT-4.1-mini's projected cost (900 calls x Gemini's
               measured mean input and output tokens per call x GPT-4.1-mini's list price) is at most
               $10. Otherwise n = 100 (the first 100) if that fits, else it is not run and the README
               says so. The rule reads token counts only, never a score.
  List prices, USD per million tokens in / out, as grader-attainment-groups read them on 2026-10-05:
  Gemini 3.5 Flash Lite 0.30 / 2.50, GPT-4.1-mini 0.40 / 1.60. Planning estimate from the dry-run
  prompts (6,100 characters, about 2,100 tokens with the schema) and 600 output tokens: $7.6 Gemini,
  $1.6 GPT-4.1-mini.
Why these sizes: the floor (below) was run before any call at n 150, 300, 450, 600 and 900. With the
planning noise (per-arm call sd 0.6) the equivalence verdicts (SCALE IS ENOUGH, IGNORES SHOWN LEVEL)
come back in 20-26% of planted-true replicates at 150, 57-66% at 300, 80-87% at 450 (one world at
the edge, FAIL), 84-92% at 600 (PASS) and 94-98% at 900. Directional verdicts pass at every n down to
150 (92-100%). With the pessimistic noise (sd 0.8) n 600 gives 70-80% on the equivalence verdicts
(floor-600-sd0.8.json, FAIL) and n 900 passes. So: an equivalence verdict that comes back is a valid
TOST whatever the power; an INCONCLUSIVE on an equivalence question is "underpowered", most of all
for GPT-4.1-mini at 150, and is never read as disagreement. The measured within-case sd of each
contrast is reported beside the verdicts so the reader can see which floor applies.

THE ARMS (identical work, identical exemplar texts in identical order, identical closing instruction
in every graded arm; only the digits beside each anchor change):
  control     no exemplars
  ungraded    the three anchors, no marks (the original third arm)
  correct     the teacher's marks (the original graded arm)
  shuffled    the same three marks deranged across the three anchors: a cyclic rotation (the only
              derangements of three positions), direction fixed per case by hash. Same set of
              numbers on the same scale; every anchor's pairing wrong unless two anchors tie. On this
              draw the mean |shown - teacher| per anchor is 6.1 points and the mean signed
              displacement is exactly 0, so the shown LEVEL is unchanged and only the PAIRING moves.
  shiftUp     teacher's marks + 2, clamped to 0..10: ranking kept, shown level raised (mean +1.49 per
              anchor after the clamp; most questions' top anchor is already 9 or 10)
  shiftDown   teacher's marks - 2, clamped: mean -1.43 per anchor (most bottom anchors are 0)
Jobs are interleaved in a hash order, so no arm runs on its own stretch of the provider's day.

ONE CONFOUND THE ORIGINAL DESIGN CARRIES, RECORDED NOT FIXED: every graded block ends with "Grade the
learner's response on the same scale these examples were graded on."; the ungraded block does not.
So "correct vs ungraded" is marks plus an instruction. The contrasts this study pre-registers
(correct vs shuffled, shiftUp vs shiftDown) all hold that sentence fixed.

ESTIMANDS (signed; "score" is the grader's number, h the teacher's; all on the same answers):
  B(arm)    bias = mean(score - h). Positive = generous.
  MAE(arm), QWK(arm)  QWK as harness/metrics.ts: scores rounded half-up onto 0..10.
  dCorr     B(correct) - B(control)      the original calibration effect (was -0.32)
  dUngr     B(ungraded) - B(control)     the original "worse than nothing" (was +0.26)
  R         B(shuffled) - B(correct)     PAIRING: what wrong pairings cost, scale held fixed
  S         B(shiftUp) - B(shiftDown)    ANCHORING: does the grader follow the level it is shown
  U, D      B(shiftUp) - B(correct), B(shiftDown) - B(correct)   the two legs of S
  rho       (B(shuffled) - B(control)) / dCorr   share of the calibration the wrong pairing keeps
  kappa     S / (mean shown(shiftUp) - mean shown(shiftDown))     pass-through of the shown level
  plus dMAE and dQWK for every contrast.

INTERVALS. Paired cluster bootstrap, 4,000 resamples, percentile. Every arm grades every answer, so
the difference is within-answer; the dependence is through the QUESTION (the three anchors are a
property of the question, shared by every case of it) and the LEARNER. Both are run; a verdict needs
its condition to hold under BOTH clusterings (the more conservative reading), otherwise it falls to
the next rule. Case-iid intervals are reported as sensitivity only.

PRE-REGISTERED VERDICTS (written and committed before any model call; see the git log). Margin
m = 0.15 points of bias (half the original calibration effect of 0.32, 1.5% of the scale).

  Replication, from dCorr:  GRADED-CALIBRATES  95% upper < 0
                            GRADED-MISCALIBRATES 95% lower > 0
                            NOT-REPLICATED     otherwise
  Ungraded, from dUngr:     UNGRADED-WORSE     95% lower > 0   (more generous than no exemplars)
                            UNGRADED-BETTER    95% upper < 0
                            UNGRADED-NO-SHIFT  otherwise
  Q1 PAIRING, from R (applied in this order):
    SCALE IS ENOUGH         90% interval of R inside (-m, +m) (TOST at alpha 0.05)
                            -> "shuffled marks on the right scale calibrate as well as the correct
                               marks, to within 0.15 points: the calibration does not need correct
                               marks"
    CORRECT MARKS MATTER    95% lower bound of R > 0: wrong pairings give back the generosity
                            -> "the calibration needs the correct pairing of answer and mark"
    SHUFFLED MARKS OVERCORRECT  95% upper bound of R < 0: wrong pairings make the grader HARSHER
                            than correct marks do (marks matter, but not as calibration retained)
    PAIRING INCONCLUSIVE    otherwise
  Q2 ANCHORING, from S, U, D (in this order):
    ANCHORS TO SHOWN LEVEL  95% lower of U > 0 AND 95% upper of D < 0: both legs follow the shift's
                            sign -> "the grader adopts the level the marks show, right or wrong"
    ANCHORS UP ONLY / ANCHORS DOWN ONLY   95% lower of S > 0 and only that leg resolved with its sign
    ANCHORS, LEGS UNRESOLVED  95% lower of S > 0, neither leg resolved alone
    IGNORES SHOWN LEVEL     90% interval of S inside (-m, +m)
    ANCHORS AGAINST SHOWN LEVEL  95% upper of S < 0 (a contrast effect)
    ANCHORING INCONCLUSIVE  otherwise
  Across models: the shared verdict, else DIFFERS-ACROSS-MODELS with each model's.
  Secondary, per contrast and metric: EQUIVALENT (90% inside +/-0.02 QWK or +/-0.10 MAE), else
  BETTER / WORSE (95% excludes 0, on the improving / worsening side), else INCONCLUSIVE.

WHAT EACH OUTCOME MEANS FOR PAPER VI (also pre-registered):
  CORRECT MARKS MATTER        section 5.4's reading stands: the marks carry rubric information.
  SCALE IS ENOUGH             section 5.4's reading is wrong as worded: the calibration comes from
                              seeing the scale used, not from correct marks. "Exemplars must carry
                              their marks" survives; "information about where this rubric places a 3"
                              does not.
  ANCHORS TO SHOWN LEVEL      whatever Q1 says, the shown marks set the grader's level, so a set of
                              exemplars marked by a severe or lenient teacher transfers that
                              severity; the "same correction as the better tier" claim depends on the
                              exemplars' marks being on the reference's level.
  NOT-REPLICATED              the section's headline (+0.38 -> +0.06) does not reproduce and Q1/Q2
                              are read as descriptive only.

THE FLOOR (`--floor`), run and committed before any model call. Synthetic graders on the real draw
(real teacher marks, real question and learner clusters, the real marks each arm shows): score =
clamp(round(h + question effect (sd 0.5) + learner effect (sd 0.3) + case effect (sd 1.2) + arm
offset + per-arm call noise (sd 0.6; 0.8 pessimistic))). None of these sizes comes from this study's
runs. The stable part is set so the control's MAE is near the paper's 1.24. The per-arm noise is the
grader's case x prompt interaction, i.e. how far a changed prompt moves one answer's mark: re-grading
an IDENTICAL prompt barely moves LITE (sd 0.18 over nine passes, grader-attainment-prior/out/
pooling.json), while layout-only rewrites of the answer move it by a mean |delta| of 0.22-0.42
(grader-eval findings, n 30), i.e. a per-arm sd of about 0.2-0.4; a 1,900-character context block is
a bigger change, so 0.6 plans and 0.8 (the paper's test-retest r 0.937) is the pessimistic case. Arm offsets: control +0.38,
ungraded +0.63, correct +0.06, then per world:
  SCALE         shuffled = correct, no anchoring              -> SCALE IS ENOUGH, IGNORES SHOWN LEVEL
  PAIRING       shuffled = control (+0.38), no anchoring       -> CORRECT MARKS MATTER, IGNORES
  ANCHOR        shuffled = correct, pass-through 0.5 of the shown displacement
                                                               -> SCALE IS ENOUGH, ANCHORS TO SHOWN LEVEL
  PAIR+ANCHOR   shuffled = control, pass-through 0.5           -> CORRECT MARKS MATTER, ANCHORS
  OVERCORRECT   shuffled = correct - 0.40                      -> SHUFFLED MARKS OVERCORRECT, IGNORES
  NULL          every arm +0.38 (exemplars do nothing)         -> NOT-REPLICATED, SCALE IS ENOUGH,
                                                                  IGNORES SHOWN LEVEL
A question x arm offset (sd 0.15) is added to every exemplar arm, because the anchors are a property
of the question and an arm's effect may differ by question.
PASS: in every world >= 80% of 200 replicates return the planted Q1 and Q2 verdicts (and the
replication verdict), and <= 10% return a false finding (the opposite sign, or any directional
verdict where a null was planted). Written to out/floor-<n>.json; the primary run is not read unless
floor-900.json passes. A power sweep over rho and kappa
is reported beside it as the instrument's resolution. A grader written by this session and scored by
this session is a smoke check of the instrument's logic on worlds it was told about, not a validation
of the construct, and is reported as one.

RESULTS (2026-10-05, after the pre-registration commit 8807506; README "Results" has the tables).
Gemini 3.5 Flash Lite, n 600, 0 failures, $4.19. The original 150 reproduce: control +0.32, correct
0.00, ungraded +0.67. GRADED-CALIBRATES (dCorr -0.34 [-0.48, -0.21] q). UNGRADED-WORSE (+0.42).
CORRECT MARKS MATTER (R +0.22, q [+0.12, +0.31], l [+0.16, +0.27]; shuffled keeps rho 0.37 of the
shift). ANCHORS TO SHOWN LEVEL (S +1.13 over 2.92 points shown, kappa 0.39; U +0.48, D -0.65). On the
full draw the control is only +0.19, so correct marks overshoot to -0.15: a shift, not a calibration.
GPT-4.1-mini, n 146 of 150, $1.10: NOT-REPLICATED (dCorr -0.06 [-0.17, +0.04]), UNGRADED-WORSE (+0.19,
toward the teacher for this harsh grader, control -0.77), PAIRING INCONCLUSIVE (R +0.08 [-0.02,
+0.17], underpowered at 150), ANCHORS TO SHOWN LEVEL (S +0.47, kappa 0.16). Within-case sd of the
Gemini contrasts 0.70-0.99, so the planning floor (floor-600.json, PASS) applies.

Usage:
  python3 analyse.py --floor <draw.json>          # dry-run dump: the draw and shown marks, no scores
  python3 analyse.py --dumps <lite.json> [<gpt41mini.json> ...]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
ARMS = ["control", "ungraded", "correct", "shuffled", "shiftUp", "shiftDown"]
SCALE = (0, 10)
M_BIAS = 0.15
M_QWK = 0.02
M_MAE = 0.10
REPS = 4000
PRIMARY_N = 600  # Gemini 3.5 Flash Lite; GPT-4.1-mini runs the first 150 of the same draw
FLOOR_REPS = 200
FLOOR_BOOT = 2000
CALL_SD = float(__import__("os").environ.get("FLOOR_CALL_SD", "0.6"))


def seed_of(key: str) -> int:
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:4], "little")


def round_half_up(x: np.ndarray) -> np.ndarray:
    """JavaScript's Math.round, as harness/metrics.ts uses it (Python's round is banker's)."""
    return np.floor(np.asarray(x, dtype=float) + 0.5)


class Data:
    """Per-case arrays for one model: teacher grade, score per arm, cluster ids."""

    def __init__(self, rows: list[dict]):
        self.rows = rows
        self.h = np.array([r["human"] for r in rows], dtype=float)
        self.s = {a: np.array([r["scores"][a] for r in rows], dtype=float) for a in ARMS}
        self.shown_mean = {a: np.array([np.mean(r["shown"][a]) if r["shown"][a] else np.nan for r in rows])
                           for a in ARMS}
        self.true_mean = np.array([np.mean(r["trueMarks"]) for r in rows])
        self.q = np.unique([r["questionId"] for r in rows], return_inverse=True)[1]
        self.l = np.unique([str(r["learnerId"]) for r in rows], return_inverse=True)[1]
        self.n = len(rows)


def weights(groups: np.ndarray, reps: int, rng: np.random.Generator) -> np.ndarray:
    """(reps+1) x n case weights for a cluster bootstrap; row 0 is the sample itself."""
    G = groups.max() + 1
    draw = rng.integers(0, G, size=(reps, G))
    counts = np.zeros((reps, G))
    np.add.at(counts, (np.repeat(np.arange(reps), G), draw.ravel()), 1)
    return np.vstack([np.ones(len(groups)), counts[:, groups]])


def arm_stats(d: Data, W: np.ndarray) -> dict[str, dict[str, np.ndarray]]:
    """Bias, MAE and QWK per arm, for every weight row at once.

    QWK in closed form: with integer levels and weighted histograms H (teacher) and M (grader) of
    total N, sum_ij (i-j)^2 H_i M_j / N = S2h + S2m - 2 S1h S1m / N, so QWK = 1 - sum w (h-m)^2 /
    (S2h + S2m - 2 S1h S1m / N). Identical to harness/metrics.ts (checked in `self_check`).
    """
    N = W.sum(1)
    hi = np.clip(round_half_up(d.h), *SCALE)
    out = {}
    for a in ARMS:
        s = d.s[a]
        mi = np.clip(round_half_up(s), *SCALE)
        num = W @ (hi - mi) ** 2
        den = W @ hi ** 2 + W @ mi ** 2 - 2 * (W @ hi) * (W @ mi) / N
        out[a] = {"bias": W @ (s - d.h) / N, "mae": W @ np.abs(s - d.h) / N,
                  "qwk": np.where(den > 0, 1 - num / np.where(den > 0, den, 1), 0.0)}
    out["_shown"] = {a: W @ np.nan_to_num(d.shown_mean[a]) / N for a in ("shiftUp", "shiftDown")}
    return out


def qwk_direct(h: np.ndarray, m: np.ndarray) -> float:
    """harness/metrics.ts quadraticWeightedKappa, line for line, for the self-check."""
    L = SCALE[1] - SCALE[0] + 1
    hi = np.clip(round_half_up(h), *SCALE).astype(int)
    mi = np.clip(round_half_up(m), *SCALE).astype(int)
    O = np.zeros((L, L))
    np.add.at(O, (hi, mi), 1)
    Hh, Mh = O.sum(1), O.sum(0)
    w = (np.arange(L)[:, None] - np.arange(L)[None, :]) ** 2 / (L - 1) ** 2
    den = (w * np.outer(Hh, Mh) / len(h)).sum()
    return 0.0 if den == 0 else 1 - (w * O).sum() / den


CONTRASTS = {
    "dCorr": ("correct", "control"),
    "dUngr": ("ungraded", "control"),
    "dShuf": ("shuffled", "control"),
    "R": ("shuffled", "correct"),
    "S": ("shiftUp", "shiftDown"),
    "U": ("shiftUp", "correct"),
    "D": ("shiftDown", "correct"),
}


def summarise(v: np.ndarray) -> dict:
    """v[0] is the point estimate; v[1:] the bootstrap replicates."""
    b = v[1:][~np.isnan(v[1:])]
    p = lambda q: float(np.percentile(b, q))
    return {"est": float(v[0]), "ci95": [p(2.5), p(97.5)], "ci90": [p(5), p(95)]}


def intervals(d: Data, rng: np.random.Generator, reps: int, by: str) -> dict:
    groups = {"question": d.q, "learner": d.l, "case": np.arange(d.n)}[by]
    st = arm_stats(d, weights(groups, reps, rng))
    out: dict = {"arms": {a: {k: summarise(st[a][k]) for k in ("bias", "mae", "qwk")} for a in ARMS}}
    for name, (a, b) in CONTRASTS.items():
        out[name] = {k: summarise(st[a][k] - st[b][k]) for k in ("bias", "mae", "qwk")}
    with np.errstate(divide="ignore", invalid="ignore"):
        shown = st["_shown"]["shiftUp"] - st["_shown"]["shiftDown"]
        out["kappa"] = summarise((st["shiftUp"]["bias"] - st["shiftDown"]["bias"]) / shown)
        out["rho"] = summarise((st["shuffled"]["bias"] - st["control"]["bias"])
                               / (st["correct"]["bias"] - st["control"]["bias"]))
        out["shown_shift"] = float(shown[0])
    return out


# ----------------------------------------------------------------------------------------------
# Verdicts. `r` maps clustering -> intervals(); a condition must hold under every clustering in it.

def _all(r: dict, f) -> bool:
    return all(f(x) for x in r.values())


def lo95(x):
    return x["ci95"][0]


def hi95(x):
    return x["ci95"][1]


def inside90(x, m):
    return -m < x["ci90"][0] and x["ci90"][1] < m


def verdict_replication(r: dict) -> str:
    if _all(r, lambda x: hi95(x["dCorr"]["bias"]) < 0):
        return "GRADED-CALIBRATES"
    if _all(r, lambda x: lo95(x["dCorr"]["bias"]) > 0):
        return "GRADED-MISCALIBRATES"
    return "NOT-REPLICATED"


def verdict_ungraded(r: dict) -> str:
    if _all(r, lambda x: lo95(x["dUngr"]["bias"]) > 0):
        return "UNGRADED-WORSE"
    if _all(r, lambda x: hi95(x["dUngr"]["bias"]) < 0):
        return "UNGRADED-BETTER"
    return "UNGRADED-NO-SHIFT"


def verdict_q1(r: dict) -> str:
    if _all(r, lambda x: inside90(x["R"]["bias"], M_BIAS)):
        return "SCALE IS ENOUGH"
    if _all(r, lambda x: lo95(x["R"]["bias"]) > 0):
        return "CORRECT MARKS MATTER"
    if _all(r, lambda x: hi95(x["R"]["bias"]) < 0):
        return "SHUFFLED MARKS OVERCORRECT"
    return "PAIRING INCONCLUSIVE"


def verdict_q2(r: dict) -> str:
    up = _all(r, lambda x: lo95(x["U"]["bias"]) > 0)
    down = _all(r, lambda x: hi95(x["D"]["bias"]) < 0)
    s_pos = _all(r, lambda x: lo95(x["S"]["bias"]) > 0)
    if up and down:
        return "ANCHORS TO SHOWN LEVEL"
    if s_pos and up:
        return "ANCHORS UP ONLY"
    if s_pos and down:
        return "ANCHORS DOWN ONLY"
    if s_pos:
        return "ANCHORS, LEGS UNRESOLVED"
    if _all(r, lambda x: inside90(x["S"]["bias"], M_BIAS)):
        return "IGNORES SHOWN LEVEL"
    if _all(r, lambda x: hi95(x["S"]["bias"]) < 0):
        return "ANCHORS AGAINST SHOWN LEVEL"
    return "ANCHORING INCONCLUSIVE"


def verdict_secondary(r: dict, contrast: str, metric: str) -> str:
    m = M_QWK if metric == "qwk" else M_MAE
    better_low = metric == "mae"
    if _all(r, lambda x: inside90(x[contrast][metric], m)):
        return "EQUIVALENT"
    below = _all(r, lambda x: hi95(x[contrast][metric]) < 0)
    above = _all(r, lambda x: lo95(x[contrast][metric]) > 0)
    if (below and better_low) or (above and not better_low):
        return "BETTER"
    if (above and better_low) or (below and not better_low):
        return "WORSE"
    return "INCONCLUSIVE"


# A verdict that would be a false finding when the planted one is true: the opposite sign, or, for
# a planted null (SCALE IS ENOUGH, IGNORES SHOWN LEVEL, NOT-REPLICATED), any directional verdict.
WRONG = {
    "SCALE IS ENOUGH": {"CORRECT MARKS MATTER", "SHUFFLED MARKS OVERCORRECT"},
    "CORRECT MARKS MATTER": {"SHUFFLED MARKS OVERCORRECT", "SCALE IS ENOUGH"},
    "SHUFFLED MARKS OVERCORRECT": {"CORRECT MARKS MATTER", "SCALE IS ENOUGH"},
    "IGNORES SHOWN LEVEL": {"ANCHORS TO SHOWN LEVEL", "ANCHORS UP ONLY", "ANCHORS DOWN ONLY",
                            "ANCHORS, LEGS UNRESOLVED", "ANCHORS AGAINST SHOWN LEVEL"},
    "ANCHORS TO SHOWN LEVEL": {"ANCHORS AGAINST SHOWN LEVEL", "IGNORES SHOWN LEVEL"},
    "GRADED-CALIBRATES": {"GRADED-MISCALIBRATES"},
    "NOT-REPLICATED": {"GRADED-CALIBRATES", "GRADED-MISCALIBRATES"},
}


# ----------------------------------------------------------------------------------------------
# The floor.

WORLDS = {
    #             shuffled offset            anchoring pass-through  exemplars act
    "SCALE":       {"shuf": "correct", "k": 0.0, "act": True,
                    "expect": ("GRADED-CALIBRATES", "SCALE IS ENOUGH", "IGNORES SHOWN LEVEL")},
    "PAIRING":     {"shuf": "control", "k": 0.0, "act": True,
                    "expect": ("GRADED-CALIBRATES", "CORRECT MARKS MATTER", "IGNORES SHOWN LEVEL")},
    "ANCHOR":      {"shuf": "correct", "k": 0.5, "act": True,
                    "expect": ("GRADED-CALIBRATES", "SCALE IS ENOUGH", "ANCHORS TO SHOWN LEVEL")},
    "PAIR+ANCHOR": {"shuf": "control", "k": 0.5, "act": True,
                    "expect": ("GRADED-CALIBRATES", "CORRECT MARKS MATTER", "ANCHORS TO SHOWN LEVEL")},
    "OVERCORRECT": {"shuf": "over", "k": 0.0, "act": True,
                    "expect": ("GRADED-CALIBRATES", "SHUFFLED MARKS OVERCORRECT", "IGNORES SHOWN LEVEL")},
    "NULL":        {"shuf": "control", "k": 0.0, "act": False,
                    "expect": ("NOT-REPLICATED", "SCALE IS ENOUGH", "IGNORES SHOWN LEVEL")},
}
OFF = {"control": 0.38, "ungraded": 0.63, "correct": 0.06}


def synth(draw: list[dict], shuf: str | float, k: float, act: bool, rng: np.random.Generator) -> list[dict]:
    h = np.array([r["human"] for r in draw], dtype=float)
    qi = np.unique([r["questionId"] for r in draw], return_inverse=True)[1]
    li = np.unique([str(r["learnerId"]) for r in draw], return_inverse=True)[1]
    stable = h + rng.normal(0, 0.5, qi.max() + 1)[qi] + rng.normal(0, 0.3, li.max() + 1)[li] + rng.normal(0, 1.2, len(h))
    true_m = np.array([np.mean(r["trueMarks"]) for r in draw])
    disp = {a: np.array([np.mean(r["shown"][a]) for r in draw]) - true_m for a in ("shiftUp", "shiftDown")}
    if not act:
        off = {a: np.full(len(h), 0.38) for a in ARMS}
    else:
        c = OFF["correct"]
        s_off = (OFF["control"] if shuf == "control" else c - 0.40 if shuf == "over"
                 else c if shuf == "correct" else OFF["control"] - float(shuf) * (OFF["control"] - c))
        off = {"control": np.full(len(h), OFF["control"]), "ungraded": np.full(len(h), OFF["ungraded"]),
               "correct": np.full(len(h), c), "shuffled": np.full(len(h), s_off),
               "shiftUp": c + k * disp["shiftUp"], "shiftDown": c + k * disp["shiftDown"]}
    # The anchors are a property of the question, so an arm's effect can differ by question: a
    # question x arm offset (sd 0.15) for every exemplar arm, which the question-cluster bootstrap
    # must absorb. Without it the floor would be easier than any real grader.
    het = {a: (rng.normal(0, 0.15, qi.max() + 1)[qi] if a != "control" else 0.0) for a in ARMS}
    rows = []
    sc = {a: np.clip(round_half_up(stable + off[a] + het[a] + rng.normal(0, CALL_SD, len(h))), *SCALE) for a in ARMS}
    for i, r in enumerate(draw):
        rows.append({**r, "scores": {a: float(sc[a][i]) for a in ARMS}})
    return rows


def verdicts_for(d: Data, rng: np.random.Generator, reps: int) -> tuple[dict, dict]:
    r = {by: intervals(d, rng, reps, by) for by in ("question", "learner")}
    v = {"replication": verdict_replication(r), "ungraded": verdict_ungraded(r),
         "q1": verdict_q1(r), "q2": verdict_q2(r)}
    return v, r


def self_check(draw: list[dict]) -> dict:
    rng = np.random.default_rng(1)
    d = Data(synth(draw, "control", 0.3, True, rng))
    st = arm_stats(d, np.ones((1, d.n)))
    diffs = [abs(float(st[a]["qwk"][0]) - qwk_direct(d.h, d.s[a])) for a in ARMS]
    assert max(diffs) < 1e-9, f"closed-form QWK disagrees with metrics.ts's form: {diffs}"
    return {"qwk_closed_form_max_abs_diff": max(diffs)}


def run_floor(draw_path: Path) -> dict:
    draw = json.loads(draw_path.read_text())["rows"]
    out: dict = {"self_check": self_check(draw), "n": len(draw), "call_sd": CALL_SD, "question_arm_sd": 0.15,
                 "replicates": FLOOR_REPS,
                 "bootstrap": FLOOR_BOOT, "worlds": {}}
    ok = True
    for w, spec in WORLDS.items():
        rng = np.random.default_rng(seed_of(f"floor|{w}"))
        counts: dict[str, dict[str, int]] = {"replication": {}, "q1": {}, "q2": {}}
        for _ in range(FLOOR_REPS):
            d = Data(synth(draw, spec["shuf"], spec["k"], spec["act"], rng))
            v, _ = verdicts_for(d, rng, FLOOR_BOOT)
            for key in counts:
                counts[key][v[key]] = counts[key].get(v[key], 0) + 1
        res = {}
        for key, want in zip(("replication", "q1", "q2"), spec["expect"]):
            hit = counts[key].get(want, 0) / FLOOR_REPS
            wrong = sum(counts[key].get(x, 0) for x in WRONG[want]) / FLOOR_REPS
            passed = hit >= 0.80 and wrong <= 0.10
            ok &= passed
            res[key] = {"planted": want, "hit_rate": hit, "false_finding_rate": wrong, "pass": passed,
                        "all": counts[key]}
        out["worlds"][w] = res
        print(f"  {w:12s} " + "  ".join(f"{k}: {v['planted']} {v['hit_rate']:.0%}{'' if v['pass'] else ' FAIL'}"
                                       for k, v in res.items()), flush=True)
    # Resolution: how small a pairing loss and how weak an anchoring the instrument can see.
    sweep = {"rho_retained": {}, "kappa_pass_through": {}}
    for rho in (0.0, 0.25, 0.5, 0.75, 1.0):
        rng = np.random.default_rng(seed_of(f"sweep-rho|{rho}"))
        c = {}
        for _ in range(60):
            v, _ = verdicts_for(Data(synth(draw, rho, 0.0, True, rng)), rng, FLOOR_BOOT)
            c[v["q1"]] = c.get(v["q1"], 0) + 1
        sweep["rho_retained"][str(rho)] = c
    for k in (0.05, 0.1, 0.2, 0.3):
        rng = np.random.default_rng(seed_of(f"sweep-kappa|{k}"))
        c = {}
        for _ in range(60):
            v, _ = verdicts_for(Data(synth(draw, "correct", k, True, rng)), rng, FLOOR_BOOT)
            c[v["q2"]] = c.get(v["q2"], 0) + 1
        sweep["kappa_pass_through"][str(k)] = c
    out["sweep_60_replicates"] = sweep
    out["PASS"] = bool(ok)
    return out


# ----------------------------------------------------------------------------------------------
# The real runs.

def analyse(path: Path, reps: int = REPS, smoke: bool = False) -> dict:
    dump = json.loads(path.read_text())
    if dump.get("dryRun"):
        raise SystemExit(f"{path} is a dry-run dump (no scores)")
    if str(dump.get("model", "")).startswith("fake:") and not smoke:
        raise SystemExit(f"{path} was graded by the fake model; it exercises the code path and is never a result")
    rows = dump["rows"]
    floor_path = OUT / f"floor-{len(rows)}.json"
    if not floor_path.exists():
        raise SystemExit(f"{floor_path.name} missing: no real number is read before the floor for this n has run")
    floor = json.loads(floor_path.read_text())
    if len(rows) == PRIMARY_N and not floor.get("PASS"):
        raise SystemExit(f"{floor_path.name} has not passed; the primary run is not read until it does")
    complete = [r for r in rows if all(r["scores"][a] is not None for a in ARMS)]
    failed = {a: sum(r["scores"][a] is None for r in rows) for a in ARMS}
    d = Data(complete)
    rng = np.random.default_rng(seed_of(f"real|{dump['model']}"))
    v, r = verdicts_for(d, rng, reps)
    r["case"] = intervals(d, rng, reps, "case")
    secondary = {c: {m: verdict_secondary({k: r[k] for k in ("question", "learner")}, c, m) for m in ("mae", "qwk")}
                 for c in ("dCorr", "dUngr", "R", "S", "U", "D")}
    within_sd = {c: float(np.std(d.s[a] - d.s[b], ddof=1)) for c, (a, b) in CONTRASTS.items()}
    first150 = [x for x in complete if x["id"] in {y["id"] for y in rows[:150]}]
    d150 = Data(first150)
    st150 = arm_stats(d150, np.ones((1, d150.n)))
    return {
        "model": dump["model"], "runStamp": dump.get("runStamp"), "temperature": dump.get("temperature"),
        "tokenUsage": dump.get("tokenUsage"),
        "n_drawn": len(rows), "n_complete": len(complete), "failed_by_arm": failed,
        "questions": int(d.q.max() + 1), "learners": int(d.l.max() + 1),
        "verdicts": v, "secondary": secondary,
        "within_case_sd": within_sd,
        "floor_planning_within_sd": "about 0.9 for a contrast of two arms at call sd 0.6 (1.2 at 0.8), after rounding",
        "cost_usd": cost_of(dump),
        "floor": {"file": floor_path.name, "PASS": floor.get("PASS"),
                  "hit_rates": {w: {k: x["hit_rate"] for k, x in r.items()} for w, r in floor["worlds"].items()}},
        "intervals": r,
        "original_150_point_estimates": {a: {k: float(st150[a][k][0]) for k in ("bias", "mae", "qwk")} for a in ARMS},
        "original_150_n_complete": len(first150),
    }


PRICES = {"google:gemini-3.5-flash-lite": (0.30, 2.50), "openai:gpt-4.1-mini": (0.40, 1.60)}


def cost_of(dump: dict) -> float | None:
    u, p = dump.get("tokenUsage"), PRICES.get(dump.get("model", ""))
    if not u or not p:
        return None
    return (u["input"] * p[0] + u["output"] * p[1]) / 1e6


def stop_rule(gemini_dump: Path, cap: float = 10.0) -> dict:
    """The pre-registered GPT-4.1-mini size, from token counts only (never a score)."""
    d = json.loads(gemini_dump.read_text())
    u = d["tokenUsage"]
    spent = cost_of(d)
    per_in, per_out = u["input"] / u["calls"], u["output"] / u["calls"]
    gp = PRICES["openai:gpt-4.1-mini"]
    proj = {n: 6 * n * (per_in * gp[0] + per_out * gp[1]) / 1e6 for n in (150, 100)}
    n = next((k for k in (150, 100) if spent + proj[k] <= cap), None)
    return {"gemini_cost": spent, "tokens_per_call": [per_in, per_out], "gpt_projection": proj, "gpt_n": n}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--floor", type=Path)
    ap.add_argument("--dumps", type=Path, nargs="*")
    ap.add_argument("--stop-rule", type=Path, help="Gemini dump: print the pre-registered GPT-4.1-mini n")
    ap.add_argument("--smoke", type=Path, help="fake-model dump: run the analysis end to end, write nothing to out/")
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    if a.floor:
        res = run_floor(a.floor)
        name = f"floor-{res['n']}.json" if CALL_SD == 0.6 else f"floor-{res['n']}-sd{CALL_SD}.json"
        (OUT / name).write_text(json.dumps(res, indent=1) + "\n")
        print("FLOOR", "PASS" if res["PASS"] else "FAIL")
        sys.exit(0 if res["PASS"] else 1)
    if a.stop_rule:
        print(json.dumps(stop_rule(a.stop_rule), indent=1))
        return
    if a.smoke:
        res = analyse(a.smoke, reps=500, smoke=True)
        print(json.dumps({"model": res["model"], "n": res["n_complete"], "verdicts": res["verdicts"],
                          "secondary": res["secondary"]}, indent=1))
        return
    results = [analyse(p) for p in a.dumps or []]
    across = {}
    for key in ("replication", "ungraded", "q1", "q2"):
        vs = {x["model"]: x["verdicts"][key] for x in results}
        across[key] = next(iter(vs.values())) if len(set(vs.values())) == 1 else \
            "DIFFERS-ACROSS-MODELS: " + "; ".join(f"{m} {v}" for m, v in vs.items())
    out = {"models": results, "across_models": across}
    (OUT / "results.json").write_text(json.dumps(out, indent=1) + "\n")
    for x in results:
        print(f"\n== {x['model']}  n={x['n_complete']}/{x['n_drawn']}  failed {x['failed_by_arm']}")
        q = x["intervals"]["question"]
        for arm in ARMS:
            s = q["arms"][arm]
            print(f"  {arm:10s} bias {s['bias']['est']:+.2f} {s['bias']['ci95']}  MAE {s['mae']['est']:.2f}  QWK {s['qwk']['est']:.3f}")
        for c in CONTRASTS:
            print(f"  {c:6s} dBias {q[c]['bias']['est']:+.3f} q{[round(v, 3) for v in q[c]['bias']['ci95']]}"
                  f" l{[round(v, 3) for v in x['intervals']['learner'][c]['bias']['ci95']]}"
                  f"  dMAE {q[c]['mae']['est']:+.3f}  dQWK {q[c]['qwk']['est']:+.3f}")
        print("  verdicts:", x["verdicts"])
    print("\nacross models:", across)


if __name__ == "__main__":
    main()
