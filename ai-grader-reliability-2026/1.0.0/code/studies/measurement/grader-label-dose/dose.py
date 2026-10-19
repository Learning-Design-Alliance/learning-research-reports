"""
Does the attainment label's effect scale with the label's VALUE, or is it a step? (Paper VI, 2026-10-06)

WHAT IS ASKED. Paper VI (research/article/attainment-bias-in-llm-grading.md, release
ai-grader-reliability-2026) shows an LLM grader "Current attainment for this learner across this course:
x/10, from n prior graded responses." In the swapped-label arm every answer is graded twice, under its own
student's held-out attainment and under the label of a paired student from the opposite tail (high tail
>= 6, low tail < 4). L = mark under the high label - mark under the low label, on the same answer, is
positive on every model (+0.28 to +0.75 of 10). Kapetanovic et al. (2026) found an LLM judge's response to
a prior score "threshold-like": that a score is present mattered more than its value. A reviewer will ask
the same of Paper VI. Two readings:
  JorGPT  The gap g = high label - low label that an answer saw varies across answers (2.0 to 7.7 points).
          Does the per-answer shift d = mark|high label - mark|low label grow with g?
  ASAP    On ASAP 2.0, Qwen3-235B graded the same 2,996 essays under a low (1.9/6), a mid (3.0/6) and a
          high (4.2/6) label (and none): a direct three-point dose curve. The presence-of-a-label effect
          is already reported (grader-attainment-groups); this reports the dose curve only.

THE DATA. No model call; per-case dumps only, all in the session scratchpad and each checked against
studies/measurement/grader-eval/analyses/per-case-dumps.sha256 before it is read (`verify`):
  grader-vi/swap-{gemini,gpt41mini,gpt5mini,qwen}.json   Paper VI Q2 runs (grader-attainment-prior)
  breadth/swap-{opus55,llama4}.json                      grader-model-breadth, default configuration
  breadth/swap-lite-rerun.json                           Gemini lite default re-run: reported beside only
  fable-agent/swap-fable-agent.json                      Fable 5.1 via the agent route, 100 answers:
                                                         reported beside, labelled, never pooled
  grader-vi-groups/run-qwen.json                         ASAP 2.0 attainment-groups, Qwen, four arms
JorGPT (Zenodo 18981627, CC BY 4.0; data/data-sources.json `jorgpt-answers`) and ASAP 2.0 (Kaggle
lburleigh/asap-2-0, CC BY 4.0; `asap2`) are not read; the dumps hold ids, the teacher's / human score, the
labels shown and the grader's marks. The ASAP group fields are in the dump and are not used. Only
aggregates in out/ are committed. The six primary models are the six default-configuration API models:
Gemini 3.5 Flash Lite, GPT-4.1-mini, GPT-5-mini, Qwen3-235B-A22B-2507, Claude Opus 5.5, Llama 4 Maverick.

THE STRUCTURE OF g (read from the labels only, before anything else; same 300-answer draw on every model).
The harness (`runAttainmentSwap`, grader-eval/harness/stability.ts) pairs BY CASE INDEX, not by student:
high-tail case i and low-tail case i swap labels, so both cases of a pair see the same (high, low) labels
and the same g. A student's cases are paired with different partners, so g varies WITHIN a student.
  g: 2.0 to 7.7 points, mean 3.72, SD 0.99, 10th-90th percentile 2.5 to 5.1.
  high tail (150 answers, 19 learners): own label 6.0-8.5 (SD 0.76); partner (low) label 0.6-4.0 (SD
    0.65), within-learner SD of the partner label 0.53.
  low tail (150 answers, 14 learners): own label 0.6-4.0 (SD 0.65); partner (high) label 6.0-8.5 (SD
    0.76), within-learner SD 0.71.
  corr(own label, partner label) = +0.02 in each tail; corr(partner label, teacher mark) -0.07 (high
  tail), +0.02 (low tail); corr(own label, teacher mark) +0.39 (high), +0.19 (low).

THE CONFOUND AND THE DESIGN. g = own - partner in the high tail and partner - own in the low tail. The
own-label half of g is a property of the student: it predicts the teacher's mark (r = 0.39 in the high
tail) and so the answer's room to move (a 10/10 answer cannot be lifted). A raw slope of d on g would
mix "the grader responds to the label's value" with "strong students' answers respond differently".
The partner-label half is set by the draw's index pairing, unrelated to the answer being graded.
  PRIMARY ESTIMAND b: OLS of d on g with tail-specific intercepts, tail-specific slopes on the student's
  own label and tail-specific slopes on the answer's teacher mark:
      d ~ 1 + low + g + own:high + own:low + teacher:high + teacher:low
  With own controlled within tail, b is identified only from the partner label: b = -dd/d(low label) in
  the high tail and +dd/d(high label) in the low tail, pooled. Units: points of d per point of g.
  IDENTIFYING ASSUMPTION: given tail, own label and teacher mark, the partner's label is unrelated to how
  the grader would move this answer under any label. The pairing is deterministic (corpus order after a
  fixed-step take), not randomised; it could correlate with question order. The measured correlations
  above are near zero. WEAKNESSES: (1) b is linear and pooled across the two tails, which identify it on
  different label ranges (low labels 0.6-4.0 in the high tail; high labels 6.0-8.5 in the low tail);
  per-tail slopes are reported. (2) The label sentence also carries n (prior responses), which moves with
  the partner and is not in the dump; b is the slope on the label's value with whatever n came with it.
  (3) The identifying variation is the partner label, SD 0.65-0.76 within tail, not g's full SD of 0.99:
  that is the range that matters for power, and the floor is run on it.
  SENSITIVITY (reported, not the verdict): learner fixed effects + teacher mark by tail (b from within-
  learner partner variation only); per-tail slopes.
  INTERVALS: learner-cluster bootstrap within tail (the label is the learner's), 4,000 replicates,
  percentile, implemented as multiplicity weights (identical to resampling for OLS and for the fixed-
  effects estimator, since duplicated learners carry identical data).

RELATIVE SLOPE rho = b * mean(g) / L: the share of the effect at the mean gap that is graded. rho = 1 when
the effect is fully proportional to the gap (d = k g), 0 for a pure step (d = L whatever the gap).
"Proportional slope" b_prop = L / mean(g) (about 0.08 to 0.20 points per point here).

PRE-REGISTERED VERDICTS (written, and the floor run and committed, before the real slope is computed; see
the git log). Per model, on b's 95% learner-cluster interval:
  UNANSWERABLE-FLOOR  the model's floor fails (below): the estimate is reported, the question is not
                      answered on that model.
  GRADED              lower bound > 0: "the label's effect on this model grows with the gap between the
                      labels: +b points per point of label".
  INVERSE             upper bound < 0: "the effect shrinks as the labels move apart".
  STEP-BOUNDED        L > 0 (its interval excludes 0), the interval lies inside +/- m, m = k * b_prop,
                      k the smallest of {0.25, 0.5} at which the floor's pure-step world is called
                      STEP-BOUNDED in >= 80% of replicates (if neither, STEP-BOUNDED is unreachable on
                      that model and is never returned): "the effect is a step: at most k of it is graded
                      by the label's value".
  UNRESOLVED          otherwise.
  Checked in that order (UNANSWERABLE-FLOOR first; GRADED and INVERSE cannot both hold).
ACROSS MODELS, on the six primary models jointly (same learner resample for every model, answers complete
on all six): pooled rho = mean over models of rho_m, 95% interval.
  UNANSWERABLE-FLOOR-POOLED  the pooled floor fails.
  GRADED-ACROSS-MODELS       rho lower bound > 0.
  INVERSE-ACROSS-MODELS      rho upper bound < 0.
  STEP-BOUNDED-ACROSS-MODELS rho interval inside +/- k_pool (k_pool chosen as k above, on rho), and every
                             model's L > 0.
  UNRESOLVED-ACROSS-MODELS   otherwise.
  Reported beside: the tally of per-model verdicts.

THE FLOOR (`--floor`), before the real slope. Synthetic d on the REAL structure of each model's dump: real
g, tails, learners, own labels and teacher marks; real noise shape: d_sim = f(g) + tail offset + a learner
effect + a residual, where the learner effects are the real learner means of d minus the tail mean,
shuffled across learners within tail each replicate, and the residuals are the real d minus its learner
mean, permuted within learner each replicate (keeps the discreteness and the within-learner spread; any
real slope left in them inflates the noise, so the floor is conservative). L is the model's real mean d
(already published). The floor never fits d on g in the real data. Worlds, each holding mean d at L:
  STEP   f = L                               expected: no signed call; STEP-BOUNDED rate reported
  PROP   f = L g / mean(g)       (b = b_prop) expected: GRADED
  HALF   f = L/2 + L g / (2 mean(g))         GRADED rate reported
  NEG    f = L - L (g - mean(g)) / mean(g)   INVERSE rate reported (the direction check)
PASS per model: GRADED in >= 80% of PROP replicates AND a signed call (GRADED or INVERSE) in <= 10% of
STEP replicates. The pooled floor runs the same worlds on all six models at once, with the SAME
permutation in every model (so answer-level noise shared across models stays shared), on pooled rho; pass
on the same two rates. 500 replicates per world, 1,000 bootstrap replicates inside each.
A floor written and scored by this session is a check of the instrument on worlds it was told about, not a
validation of the construct; it is reported as one.

ASAP DOSE CURVE (Qwen3-235B, 0-6 scale, arms low 1.9, mid 3.0, high 4.2; essays complete on all four
arms). Paired per-essay contrasts: A = mid - low, B = high - mid, S = high - low; per label point
a = A/1.1, b2 = B/1.2; curvature C = b2 - a. Essay bootstrap (one essay per student, the unit the label
was assigned to), 4,000 replicates, unweighted (the draw's oversampling of ELL and disability cells is not
reweighted; the dose shape is a within-essay contrast). NOT BLIND: the four arm means (2.98 / 2.51 / 2.97
/ 2.81) were published in grader-attainment-groups before this was written; what is new is the paired
intervals and the shape. Pre-registered, margin M = 0.05 levels (1% of the 1-6 range):
  NON-MONOTONE        A or B has its 95% upper bound < 0.
  MONOTONE-DOSE       A and B both have 95% lower bound > 0.
  STEP-LOW-TO-MID     A lower > 0 and B's 95% interval inside +/- M (plateau above mid).
  STEP-MID-TO-HIGH    B lower > 0 and A's interval inside +/- M.
  UNRESOLVED          otherwise.
  Shape, appended: LINEAR-IN-VALUE if C's interval includes 0, else CONCAVE (C upper < 0) or CONVEX.
ASAP floor: latent = the real none-arm mark + U(-0.5, 0.5); each arm = clip(round(latent + effect + N(0,
s)), 1, 6), s calibrated so the null sd of (low - none) matches the real one. Worlds with a 0.48 latent
spread low to high: LINEAR (in label value) -> MONOTONE-DOSE; STEP at low->mid -> STEP-LOW-TO-MID; STEP at
mid->high -> STEP-MID-TO-HIGH. Pass: >= 80% each. 200 replicates, 500 bootstrap.

FAILURES THAT SHAPED THIS. (1) The brief described g as "fixed by the student pairing"; the harness pairs
by case index, so g varies within a student (read from the code and the labels before anything else),
which is what makes a within-student design possible. (2) The scratch-path default of shared.paths points
at an earlier session; pass --dump-dir.

Usage:
  python3 dose.py --verify --dump-dir D
  python3 dose.py --floor  --dump-dir D     writes out/floor.json (no real slope computed)
  python3 dose.py --run    --dump-dir D     writes out/results.json (requires out/floor.json)
  python3 dose.py --posthoc --dump-dir D    added after the run, reported only: out/posthoc.json
  D holds grader-vi/, breadth/, fable-agent/, grader-vi-groups/; else $GRADER_DUMP_DIR; else
  shared.paths.scratch_root().
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
OUT = HERE / "out"
SHA_LIST = ROOT / "studies/measurement/grader-eval/analyses/per-case-dumps.sha256"

PRIMARY = [
    ("gemini", "Gemini 3.5 Flash Lite", "grader-vi/swap-gemini.json"),
    ("gpt41mini", "GPT-4.1-mini", "grader-vi/swap-gpt41mini.json"),
    ("gpt5mini", "GPT-5-mini", "grader-vi/swap-gpt5mini.json"),
    ("qwen", "Qwen3-235B-A22B-2507", "grader-vi/swap-qwen.json"),
    ("opus55", "Claude Opus 5.5", "breadth/swap-opus55.json"),
    ("llama4", "Llama 4 Maverick", "breadth/swap-llama4.json"),
]
BESIDE = [
    ("gemini-rerun", "Gemini 3.5 Flash Lite, default re-run (beside)", "breadth/swap-lite-rerun.json"),
    ("fable-agent", "Fable 5.1, agent route, 100 answers (beside, never pooled)", "fable-agent/swap-fable-agent.json"),
]
ASAP = "grader-vi-groups/run-qwen.json"
ASAP_LABELS = {"low": 1.9, "mid": 3.0, "high": 4.2}

REPS = 4000
FLOOR_REPS = 500
FLOOR_BOOT = 1000
ASAP_FLOOR_REPS = 200
ASAP_FLOOR_BOOT = 500
K_GRID = (0.25, 0.5)
PASS_RECOVERY = 0.80
PASS_FALSE = 0.10
ASAP_MARGIN = 0.05
SEED = 20261006


# ----------------------------------------------------------------------------- data

def dump_dir(arg: str | None) -> Path:
    if arg:
        return Path(arg)
    if os.environ.get("GRADER_DUMP_DIR"):
        return Path(os.environ["GRADER_DUMP_DIR"])
    from shared.paths import scratch_root
    return scratch_root()


def verify(root: Path) -> dict[str, bool]:
    # Each dump must match either its original hash or, for the two ASAP 2.0 runs whose published copy
    # drops the `resumedFrom` header, the deterministic hash of the copy `strip_dumps.py rebuild` writes
    # (per-case-dumps.rebuilt.sha256; added after reproduction-5 found the declared command could not run
    # on rebuilt dumps). Either way the bytes read are pinned.
    want: dict[str, set[str]] = {}
    for lst in (SHA_LIST, SHA_LIST.with_name("per-case-dumps.rebuilt.sha256")):
        for line in lst.read_text().splitlines() if lst.exists() else []:
            if line.strip():
                h, f = line.split()
                want.setdefault(f, set()).add(h)
    res = {}
    for f in [p for _, _, p in PRIMARY + BESIDE] + [ASAP]:
        got = hashlib.sha256((root / f).read_bytes()).hexdigest()
        if got not in want.get(f, set()):
            raise SystemExit(f"{f}: sha256 {got} matches neither per-case-dumps.sha256 nor its rebuilt list")
        res[f] = True
    return res


class Swap:
    """Complete rows of one swapped-label dump. d = mark|high label - mark|low label, same answer."""

    def __init__(self, rows: list[dict]):
        rows = [r for r in rows if r.get("trueLabel") is not None and r.get("swappedLabel") is not None]
        self.ids = np.array([str(r["id"]) for r in rows])
        self.hi = np.array([r["tail"] == "high" for r in rows])
        self.own = np.array([r["labelTrue"] for r in rows], float)
        self.partner = np.array([r["labelSwapped"] for r in rows], float)
        lab_hi = np.where(self.hi, self.own, self.partner)
        lab_lo = np.where(self.hi, self.partner, self.own)
        self.g = lab_hi - lab_lo
        t = np.array([r["trueLabel"] for r in rows], float)
        s = np.array([r["swappedLabel"] for r in rows], float)
        self.d = np.where(self.hi, t - s, s - t)
        self.teacher = np.array([r["human"] for r in rows], float)
        self.learner = np.array([("H|" if h else "L|") + str(r["learnerId"]) for r, h in zip(rows, self.hi)])

    def subset(self, keep: np.ndarray) -> "Swap":
        new = object.__new__(Swap)
        for k, v in self.__dict__.items():
            new.__dict__[k] = v[keep]
        return new


def load_swap(root: Path, path: str) -> Swap:
    return Swap(json.loads((root / path).read_text())["rows"])


# ----------------------------------------------------------------------------- the instrument

def design(s: Swap, fe: bool = False) -> tuple[np.ndarray, int]:
    """Design matrix and the column index of g."""
    hi = s.hi.astype(float)
    lo = 1 - hi
    if not fe:
        X = np.column_stack([np.ones_like(hi), lo, s.g, s.own * hi, s.own * lo, s.teacher * hi, s.teacher * lo])
        return X, 2
    learners = sorted(set(s.learner))
    D = (s.learner[:, None] == np.array(learners)[None, :]).astype(float)
    X = np.column_stack([s.g, s.teacher * hi, s.teacher * lo, D])
    return X, 0


def cluster_weights(s: Swap, B: int, rng: np.random.Generator) -> np.ndarray:
    """B x n multiplicity weights: resample learners with replacement within tail."""
    W = np.zeros((B, len(s.d)))
    for tail in (True, False):
        ls = np.array(sorted(set(s.learner[s.hi == tail])))
        member = (s.learner[:, None] == ls[None, :])           # n x k
        draws = rng.integers(0, len(ls), size=(B, len(ls)))
        counts = np.zeros((B, len(ls)))
        np.add.at(counts, (np.repeat(np.arange(B), len(ls)), draws.ravel()), 1)
        W += counts @ member.T.astype(float)
    return W


def slope_operator(X: np.ndarray, col: int, W: np.ndarray) -> np.ndarray:
    """G (B x n) with G @ y = the weighted-OLS coefficient on column `col` in each replicate."""
    out = []
    for start in range(0, len(W), 250):                      # chunked: the FE design is ~36 columns
        XtW = np.einsum("np,bn->bpn", X, W[start:start + 250])
        A = np.linalg.pinv(XtW @ X) @ XtW                    # b x p x n
        out.append(A[:, col, :])
    return np.concatenate(out)


def point_slope(X: np.ndarray, col: int, y: np.ndarray) -> float:
    return float(np.linalg.lstsq(X, y, rcond=None)[0][col])


def ci(x: np.ndarray) -> list[float]:
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]


def verdict_model(b_ci, L_ci, m: float | None, floor_pass: bool) -> str:
    if not floor_pass:
        return "UNANSWERABLE-FLOOR"
    if b_ci[0] > 0:
        return "GRADED"
    if b_ci[1] < 0:
        return "INVERSE"
    if m is not None and L_ci[0] > 0 and -m < b_ci[0] and b_ci[1] < m:
        return "STEP-BOUNDED"
    return "UNRESOLVED"


def verdict_pooled(r_ci, k: float | None, all_L_pos: bool, floor_pass: bool) -> str:
    if not floor_pass:
        return "UNANSWERABLE-FLOOR-POOLED"
    if r_ci[0] > 0:
        return "GRADED-ACROSS-MODELS"
    if r_ci[1] < 0:
        return "INVERSE-ACROSS-MODELS"
    if k is not None and all_L_pos and -k < r_ci[0] and r_ci[1] < k:
        return "STEP-BOUNDED-ACROSS-MODELS"
    return "UNRESOLVED-ACROSS-MODELS"


# ----------------------------------------------------------------------------- floor

WORLDS = ("STEP", "PROP", "HALF", "NEG")


def planted(world: str, g: np.ndarray, L: float, gbar: float) -> np.ndarray:
    if world == "STEP":
        return np.full_like(g, L)
    if world == "PROP":
        return L * g / gbar
    if world == "HALF":
        return L / 2 + L * g / (2 * gbar)
    if world == "NEG":
        return L - L * (g - gbar) / gbar
    raise ValueError(world)


class Noise:
    """Real noise shape of d: tail offsets, learner effects, within-learner residuals. No g is used."""

    def __init__(self, s: Swap):
        self.s = s
        self.mu = s.d.mean()
        self.tail_off = np.where(s.hi, s.d[s.hi].mean(), s.d[~s.hi].mean()) - self.mu
        self.lmean = {l: s.d[s.learner == l].mean() for l in set(s.learner)}
        lm = np.array([self.lmean[l] for l in s.learner])
        self.resid = s.d - lm
        self.groups = {l: np.flatnonzero(s.learner == l) for l in sorted(set(s.learner))}
        self.tails = {t: sorted({l for l in self.groups if s.hi[self.groups[l][0]] == t}) for t in (True, False)}
        self.ueff = {l: self.lmean[l] - (s.d[s.hi].mean() if s.hi[self.groups[l][0]] else s.d[~s.hi].mean())
                     for l in self.groups}

    def draw(self, perm_l: dict, perm_r: dict) -> np.ndarray:
        out = self.tail_off.copy()
        for l, idx in self.groups.items():
            out[idx] += self.ueff[perm_l[l]] + self.resid[idx[perm_r[l]]]
        return out


def draw_perms(noise: Noise, rng: np.random.Generator) -> tuple[dict, dict]:
    perm_l = {}
    for t, ls in noise.tails.items():
        sh = list(rng.permutation(ls))
        perm_l.update(dict(zip(ls, sh)))
    perm_r = {l: rng.permutation(len(idx)) for l, idx in noise.groups.items()}
    return perm_l, perm_r


def floor_model(s: Swap, rng: np.random.Generator) -> dict:
    X, col = design(s)
    W = cluster_weights(s, FLOOR_BOOT, rng)
    G = slope_operator(X, col, W)
    noise = Noise(s)
    L = float(s.d.mean())
    gbar = float(s.g.mean())
    bprop = L / gbar
    res = {"n": int(len(s.d)), "L": L, "gbar": gbar, "b_prop": bprop, "worlds": {}}
    for w in WORLDS:
        f = planted(w, s.g, L, gbar)
        cnt = {"GRADED": 0, "INVERSE": 0, **{f"STEP-BOUNDED@{k}": 0 for k in K_GRID}}
        slopes = []
        for _ in range(FLOOR_REPS):
            y = f + noise.draw(*draw_perms(noise, rng))
            bb = G @ y
            lo, hi = np.percentile(bb, [2.5, 97.5])
            slopes.append(point_slope(X, col, y))
            cnt["GRADED"] += lo > 0
            cnt["INVERSE"] += hi < 0
            for k in K_GRID:
                cnt[f"STEP-BOUNDED@{k}"] += (-k * bprop < lo) and (hi < k * bprop)
        res["worlds"][w] = {**{c: v / FLOOR_REPS for c, v in cnt.items()},
                            "mean_slope": float(np.mean(slopes)), "planted_slope":
                            {"STEP": 0.0, "PROP": bprop, "HALF": bprop / 2, "NEG": -bprop}[w]}
    W_ = res["worlds"]
    res["pass"] = bool(W_["PROP"]["GRADED"] >= PASS_RECOVERY and
                       W_["STEP"]["GRADED"] + W_["STEP"]["INVERSE"] <= PASS_FALSE)
    ks = [k for k in K_GRID if W_["STEP"][f"STEP-BOUNDED@{k}"] >= PASS_RECOVERY]
    res["k"] = ks[0] if ks else None
    res["m"] = res["k"] * bprop if ks else None
    return res


def pooled_parts(models: list[Swap]) -> tuple[list[Swap], np.ndarray]:
    common = set(models[0].ids)
    for s in models[1:]:
        common &= set(s.ids)
    out = []
    for s in models:
        keep = np.isin(s.ids, sorted(common))
        sub = s.subset(keep)
        order = np.argsort(sub.ids)
        out.append(sub.subset(order))
    return out, out[0].ids


def rho_boot(parts: list[Swap], Gs: list[np.ndarray], W: np.ndarray, ys: list[np.ndarray]) -> np.ndarray:
    """B-vector of pooled rho = mean_m b_m * gbar_w / L_m,w."""
    g = parts[0].g
    gbar = (W @ g) / W.sum(1)
    rhos = []
    for G, y in zip(Gs, ys):
        Lw = (W @ y) / W.sum(1)
        rhos.append((G @ y) * gbar / Lw)
    return np.mean(rhos, axis=0)


def floor_pooled(models: list[Swap], rng: np.random.Generator) -> dict:
    parts, _ = pooled_parts(models)
    ref = parts[0]
    X, col = design(ref)
    W = cluster_weights(ref, FLOOR_BOOT, rng)
    G = slope_operator(X, col, W)
    noises = [Noise(p) for p in parts]
    Ls = [float(p.d.mean()) for p in parts]
    gbar = float(ref.g.mean())
    res = {"n_common": int(len(ref.d)), "worlds": {}}
    for w in WORLDS:
        cnt = {"GRADED": 0, "INVERSE": 0, **{f"STEP-BOUNDED@{k}": 0 for k in K_GRID}}
        for _ in range(FLOOR_REPS):
            perm_l, perm_r = draw_perms(noises[0], rng)      # one permutation shared by every model
            ys = [planted(w, ref.g, L, gbar) + nz.draw(perm_l, perm_r) for L, nz in zip(Ls, noises)]
            r = rho_boot(parts, [G] * len(parts), W, ys)
            lo, hi = np.percentile(r, [2.5, 97.5])
            cnt["GRADED"] += lo > 0
            cnt["INVERSE"] += hi < 0
            for k in K_GRID:
                cnt[f"STEP-BOUNDED@{k}"] += (-k < lo) and (hi < k)
        res["worlds"][w] = {c: v / FLOOR_REPS for c, v in cnt.items()}
    W_ = res["worlds"]
    res["pass"] = bool(W_["PROP"]["GRADED"] >= PASS_RECOVERY and
                       W_["STEP"]["GRADED"] + W_["STEP"]["INVERSE"] <= PASS_FALSE)
    ks = [k for k in K_GRID if W_["STEP"][f"STEP-BOUNDED@{k}"] >= PASS_RECOVERY]
    res["k"] = ks[0] if ks else None
    return res


# ----------------------------------------------------------------------------- ASAP

def load_asap(root: Path) -> dict[str, np.ndarray]:
    rows = json.loads((root / ASAP).read_text())["rows"]
    rows = [r for r in rows if all(r.get(a) is not None for a in ("none", "low", "mid", "high"))]
    return {a: np.array([r[a] for r in rows], float) for a in ("none", "low", "mid", "high")}


def asap_stats(arms: dict[str, np.ndarray], idx: np.ndarray | None = None,
               full: bool = True) -> dict[str, np.ndarray]:
    """Vectorised over a B x n index matrix (or the full sample if idx is None)."""
    take = (lambda x: x[idx].mean(-1)) if idx is not None else (lambda x: x.mean())
    A = take(arms["mid"] - arms["low"])
    B = take(arms["high"] - arms["mid"])
    a = A / (ASAP_LABELS["mid"] - ASAP_LABELS["low"])
    b = B / (ASAP_LABELS["high"] - ASAP_LABELS["mid"])
    out = {"A_mid_minus_low": A, "B_high_minus_mid": B, "curvature": b - a}
    if full:
        out.update({"S_high_minus_low": take(arms["high"] - arms["low"]),
                    "per_point_low_to_mid": a, "per_point_mid_to_high": b,
                    "mid_minus_none": take(arms["mid"] - arms["none"]),
                    "low_minus_none": take(arms["low"] - arms["none"]),
                    "high_minus_none": take(arms["high"] - arms["none"])})
    return out


def asap_verdict(c: dict[str, list[float]]) -> str:
    A, B, C = c["A_mid_minus_low"], c["B_high_minus_mid"], c["curvature"]
    M = ASAP_MARGIN
    if A[1] < 0 or B[1] < 0:
        v = "NON-MONOTONE"
    elif A[0] > 0 and B[0] > 0:
        v = "MONOTONE-DOSE"
    elif A[0] > 0 and -M < B[0] and B[1] < M:
        v = "STEP-LOW-TO-MID"
    elif B[0] > 0 and -M < A[0] and A[1] < M:
        v = "STEP-MID-TO-HIGH"
    else:
        v = "UNRESOLVED"
    shape = "LINEAR-IN-VALUE" if C[0] <= 0 <= C[1] else ("CONCAVE" if C[1] < 0 else "CONVEX")
    return f"{v} / {shape}"


def asap_boot(arms, B: int, rng, full: bool = True) -> dict[str, list[float]]:
    n = len(arms["none"])
    out: dict[str, list[np.ndarray]] = {}
    for start in range(0, B, 500):
        idx = rng.integers(0, n, size=(min(500, B - start), n))
        for k, v in asap_stats(arms, idx, full).items():
            out.setdefault(k, []).append(v)
    return {k: ci(np.concatenate(v)) for k, v in out.items()}


def asap_floor(arms: dict[str, np.ndarray], rng) -> dict:
    base = arms["none"]
    n = len(base)
    target = float(np.std(arms["low"] - arms["none"]))

    def sim(eff: dict[str, float], s: float, r) -> dict[str, np.ndarray]:
        lat = base + r.uniform(-0.5, 0.5, n)
        return {a: np.clip(np.floor(lat + eff.get(a, 0.0) + r.normal(0, s, n) + 0.5), 1, 6)
                for a in ("none", "low", "mid", "high")}

    grid = np.round(np.arange(0.2, 1.21, 0.05), 2)
    sds = [float(np.mean([np.std((x := sim({}, s, rng))["low"] - x["none"]) for _ in range(5)])) for s in grid]
    s = float(grid[int(np.argmin(np.abs(np.array(sds) - target)))])
    spread = 0.48
    lin = {a: spread * (v - ASAP_LABELS["low"]) / (ASAP_LABELS["high"] - ASAP_LABELS["low"]) - spread / 2
           for a, v in ASAP_LABELS.items()}
    worlds = {"LINEAR": (lin, "MONOTONE-DOSE"),
              "STEP-LOW-TO-MID": ({"low": -spread / 2, "mid": spread / 2, "high": spread / 2}, "STEP-LOW-TO-MID"),
              "STEP-MID-TO-HIGH": ({"low": -spread / 2, "mid": -spread / 2, "high": spread / 2}, "STEP-MID-TO-HIGH")}
    res = {"target_sd_low_minus_none": target, "sigma": s, "worlds": {}}
    for w, (eff, want) in worlds.items():
        hits = 0
        calls: dict[str, int] = {}
        for _ in range(ASAP_FLOOR_REPS):
            x = sim(eff, s, rng)
            v = asap_verdict(asap_boot(x, ASAP_FLOOR_BOOT, rng, full=False)).split(" / ")[0]
            calls[v] = calls.get(v, 0) + 1
            hits += v == want
        res["worlds"][w] = {"expected": want, "rate": hits / ASAP_FLOOR_REPS, "calls": calls}
    res["pass"] = all(w["rate"] >= PASS_RECOVERY for w in res["worlds"].values())
    return res


# ----------------------------------------------------------------------------- main modes

def g_structure(s: Swap) -> dict:
    out = {"n": int(len(s.g)), "g_min": float(s.g.min()), "g_max": float(s.g.max()),
           "g_mean": float(s.g.mean()), "g_sd": float(s.g.std()),
           "g_p10_p90": [float(x) for x in np.percentile(s.g, [10, 90])]}
    for name, m in (("high", s.hi), ("low", ~s.hi)):
        within = [float(np.std(s.partner[(s.learner == l)])) for l in set(s.learner[m])
                  if (s.learner == l).sum() > 1]
        out[name] = {"n": int(m.sum()), "learners": int(len(set(s.learner[m]))),
                     "partner_label_range": [float(s.partner[m].min()), float(s.partner[m].max())],
                     "partner_label_sd": float(s.partner[m].std()),
                     "partner_label_within_learner_sd": float(np.mean(within)),
                     "corr_partner_teacher": float(np.corrcoef(s.partner[m], s.teacher[m])[0, 1]),
                     "corr_own_teacher": float(np.corrcoef(s.own[m], s.teacher[m])[0, 1])}
    return out


def run_floor(root: Path) -> None:
    verify(root)
    rng = np.random.default_rng(SEED)
    models = [load_swap(root, p) for _, _, p in PRIMARY]
    out = {"seed": SEED, "floor_reps": FLOOR_REPS, "floor_boot": FLOOR_BOOT, "k_grid": list(K_GRID),
           "pass_rule": {"PROP_GRADED_min": PASS_RECOVERY, "STEP_signed_max": PASS_FALSE},
           "models": {}, "beside": {}}
    for (key, label, _), s in zip(PRIMARY, models):
        r = floor_model(s, rng)
        out["models"][key] = {"label": label, "g": g_structure(s), **r}
        print(f"{label:28s} n {r['n']}  L {r['L']:+.2f}  b_prop {r['b_prop']:.3f}  "
              + "  ".join(f"{w}: G {v['GRADED']:.2f} I {v['INVERSE']:.2f} SB.25 {v['STEP-BOUNDED@0.25']:.2f} "
                          f"SB.5 {v['STEP-BOUNDED@0.5']:.2f}" for w, v in r["worlds"].items())
              + f"  PASS {r['pass']} k {r['k']}", flush=True)
    for key, label, p in BESIDE:
        s = load_swap(root, p)
        r = floor_model(s, rng)
        out["beside"][key] = {"label": label, "g": g_structure(s), **r}
        print(f"{label:28s} n {r['n']}  PROP G {r['worlds']['PROP']['GRADED']:.2f}  STEP signed "
              f"{r['worlds']['STEP']['GRADED'] + r['worlds']['STEP']['INVERSE']:.2f}  PASS {r['pass']} k {r['k']}",
              flush=True)
    out["pooled"] = floor_pooled(models, rng)
    print("pooled", json.dumps(out["pooled"]), flush=True)
    arms = load_asap(root)
    out["asap"] = {"n_complete": int(len(arms["none"])), **asap_floor(arms, rng)}
    print("asap", json.dumps(out["asap"]), flush=True)
    OUT.mkdir(exist_ok=True)
    (OUT / "floor.json").write_text(json.dumps(out, indent=1) + "\n")


def analyse_model(s: Swap, fl: dict, rng) -> dict:
    X, col = design(s)
    W = cluster_weights(s, REPS, rng)
    G = slope_operator(X, col, W)
    b = point_slope(X, col, s.d)
    b_bt = G @ s.d
    L = float(s.d.mean())
    L_bt = (W @ s.d) / W.sum(1)
    gbar_bt = (W @ s.g) / W.sum(1)
    rho_bt = b_bt * gbar_bt / L_bt
    res = {"n": int(len(s.d)), "L": L, "L_ci": ci(L_bt), "b": b, "b_ci": ci(b_bt),
           "b_prop": L / float(s.g.mean()), "rho": b * float(s.g.mean()) / L, "rho_ci": ci(rho_bt),
           "m": fl["m"], "floor_pass": fl["pass"]}
    res["verdict"] = verdict_model(res["b_ci"], res["L_ci"], fl["m"], fl["pass"])
    # sensitivity: learner fixed effects
    Xf, cf = design(s, fe=True)
    Gf = slope_operator(Xf, cf, W)
    res["b_fe"] = point_slope(Xf, cf, s.d)
    res["b_fe_ci"] = ci(Gf @ s.d)
    # sensitivity: per tail (d ~ 1 + g + own + teacher within tail); the bootstrap draws of the other tail
    # do not enter
    for name, m in (("high", s.hi), ("low", ~s.hi)):
        Xt = np.column_stack([np.ones(m.sum()), s.g[m], s.own[m], s.teacher[m]])
        Gt = slope_operator(Xt, 1, W[:, m])
        res[f"b_{name}"] = point_slope(Xt, 1, s.d[m])
        res[f"b_{name}_ci"] = ci(Gt @ s.d[m])
    # descriptive: raw (unadjusted) slope and d by g tercile
    Xr = np.column_stack([np.ones_like(s.g), s.g])
    res["b_raw_unadjusted"] = point_slope(Xr, 1, s.d)
    cuts = np.percentile(s.g, [100 / 3, 200 / 3])
    bins = np.digitize(s.g, cuts)
    res["d_by_g_tercile"] = [{"g_mean": float(s.g[bins == i].mean()), "d_mean": float(s.d[bins == i].mean()),
                              "n": int((bins == i).sum())} for i in range(3)]
    return res


def run_real(root: Path) -> None:
    verify(root)
    fl = json.loads((OUT / "floor.json").read_text())
    rng = np.random.default_rng(SEED + 1)
    models = [load_swap(root, p) for _, _, p in PRIMARY]
    out = {"reps": REPS, "models": {}, "beside": {}}
    for (key, label, _), s in zip(PRIMARY, models):
        r = analyse_model(s, fl["models"][key], rng)
        out["models"][key] = {"label": label, **r}
        print(f"{label:28s} L {r['L']:+.2f} [{r['L_ci'][0]:+.2f},{r['L_ci'][1]:+.2f}]  b {r['b']:+.3f} "
              f"[{r['b_ci'][0]:+.3f},{r['b_ci'][1]:+.3f}]  rho {r['rho']:+.2f} [{r['rho_ci'][0]:+.2f},"
              f"{r['rho_ci'][1]:+.2f}]  m {r['m']}  {r['verdict']}  | FE {r['b_fe']:+.3f} "
              f"[{r['b_fe_ci'][0]:+.3f},{r['b_fe_ci'][1]:+.3f}]  hi {r['b_high']:+.3f} "
              f"[{r['b_high_ci'][0]:+.3f},{r['b_high_ci'][1]:+.3f}]  lo {r['b_low']:+.3f} "
              f"[{r['b_low_ci'][0]:+.3f},{r['b_low_ci'][1]:+.3f}]  raw {r['b_raw_unadjusted']:+.3f}", flush=True)
    for key, label, p in BESIDE:
        r = analyse_model(load_swap(root, p), fl["beside"][key], rng)
        out["beside"][key] = {"label": label, **r}
        print(f"{label:28s} L {r['L']:+.2f}  b {r['b']:+.3f} [{r['b_ci'][0]:+.3f},{r['b_ci'][1]:+.3f}]  "
              f"{r['verdict']}", flush=True)
    # pooled
    parts, _ = pooled_parts(models)
    ref = parts[0]
    X, col = design(ref)
    W = cluster_weights(ref, REPS, rng)
    G = slope_operator(X, col, W)
    r_bt = rho_boot(parts, [G] * len(parts), W, [p.d for p in parts])
    gbar = float(ref.g.mean())
    rho = float(np.mean([point_slope(X, col, p.d) * gbar / p.d.mean() for p in parts]))
    pf = fl["pooled"]
    all_L_pos = all(out["models"][k]["L_ci"][0] > 0 for k, _, _ in PRIMARY)
    out["pooled"] = {"n_common": int(len(ref.d)), "rho": rho, "rho_ci": ci(r_bt), "k": pf["k"],
                     "floor_pass": pf["pass"], "all_L_positive": all_L_pos,
                     "verdict": verdict_pooled(ci(r_bt), pf["k"], all_L_pos, pf["pass"]),
                     "tally": {}}
    for k, _, _ in PRIMARY:
        v = out["models"][k]["verdict"]
        out["pooled"]["tally"][v] = out["pooled"]["tally"].get(v, 0) + 1
    print("pooled", json.dumps(out["pooled"]), flush=True)
    # ASAP
    arms = load_asap(root)
    pt = {k: float(v) for k, v in asap_stats(arms).items()}
    cis = asap_boot(arms, REPS, rng)
    out["asap"] = {"n_complete": int(len(arms["none"])), "means": {a: float(v.mean()) for a, v in arms.items()},
                   "point": pt, "ci": cis, "floor_pass": fl["asap"]["pass"],
                   "verdict": asap_verdict(cis) if fl["asap"]["pass"] else "UNANSWERABLE-FLOOR"}
    print("asap", json.dumps(out["asap"]), flush=True)
    (OUT / "results.json").write_text(json.dumps(out, indent=1) + "\n")


def run_posthoc(root: Path) -> None:
    """ADDED AFTER THE RUN, reported only, never a verdict: leave-one-model-out pooled rho (is the pooled
    GRADED one model's doing?) and each model's d by g tercile."""
    verify(root)
    rng = np.random.default_rng(SEED + 2)
    models = [load_swap(root, p) for _, _, p in PRIMARY]
    parts, _ = pooled_parts(models)
    ref = parts[0]
    X, col = design(ref)
    W = cluster_weights(ref, REPS, rng)
    G = slope_operator(X, col, W)
    gbar = float(ref.g.mean())
    out = {"leave_one_out": {}, "terciles": {}}
    for i, (key, label, _) in enumerate(PRIMARY):
        keep = [p for j, p in enumerate(parts) if j != i]
        r_bt = rho_boot(keep, [G] * len(keep), W, [p.d for p in keep])
        rho = float(np.mean([point_slope(X, col, p.d) * gbar / p.d.mean() for p in keep]))
        out["leave_one_out"][key] = {"rho": rho, "rho_ci": ci(r_bt)}
        print(f"without {label:24s} rho {rho:+.2f} [{ci(r_bt)[0]:+.2f}, {ci(r_bt)[1]:+.2f}]")
    res = json.loads((OUT / "results.json").read_text())
    for key, v in res["models"].items():
        out["terciles"][key] = v["d_by_g_tercile"]
        print(key, " ".join(f"g {t['g_mean']:.2f}: d {t['d_mean']:+.2f} (n {t['n']})" for t in v["d_by_g_tercile"]))
    (OUT / "posthoc.json").write_text(json.dumps(out, indent=1) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--floor", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--posthoc", action="store_true")
    ap.add_argument("--dump-dir")
    a = ap.parse_args()
    root = dump_dir(a.dump_dir)
    if a.verify:
        print(json.dumps(verify(root), indent=1))
    if a.floor:
        run_floor(root)
    if a.run:
        run_real(root)
    if a.posthoc:
        run_posthoc(root)


if __name__ == "__main__":
    main()
