"""
Two robustness checks on Paper VI's human ceilings (no model calls; the grader runs already on disk).

WHAT WAS ASKED (2026-10-06). The Paper VI literature review (research/readiness/ai-grader-reliability-2026/
literature.md, 5a.6 and 5b.3; release ai-grader-reliability-2026 1.0.0, article
research/article/attainment-bias-in-llm-grading.md, sections 1.2, 4.6, 5.1) suggested two optional checks:

  T1  Elangovan et al. 2025: grader-human agreement stratified by whether the HUMANS agreed. Paper VI
      argues (1.2) that "a substantial share of the residual disagreement between a grader and a single
      human reference is noise in the reference", and so that "agreement is a blunt instrument". Does the
      grader look better where humans agree, how much of its single-reference error is reference noise,
      and does the argument survive?
  T2  Albatarni & Elsayed 2026: Gwet's AC2 (quadratic weights) beside each kappa. Kappa-type statistics
      take chance agreement from the marginals (the "kappa paradox": skewed marginals depress kappa at
      fixed raw agreement); AC2 is less sensitive. Are the ceilings (Mohler 0.519; Menagerie pooled 0.465
      on 5 levels, 0.424 on 14, per-pair 0.035-0.730) and the grader-vs-human comparisons robust to it?

DATA. Reads two registered corpora (data/data-sources.json): `mohler-asag` (MOHLER_DIR, the analysed CSV
mohler_en.csv, generator studies/measurement/grader-eval/analyses/mohler_to_csv.py; CC BY 4.0) and
`menagerie-grades` (MENAGERIE_DIR, grades.csv; CC BY 4.0). Per-rater grades come from these. Grader marks
come from the per-case harness dumps of studies/measurement/grader-label-stability/ (verified against
studies/measurement/grader-eval/analyses/per-case-dumps.sha256 before use: `--verify` in this script),
held in the session scratchpad and never committed:
  grader-label-stability/draw-mohler.json, mohler-{gemini,gpt41mini,qwen}.json     300 answers, 62 questions
  grader-label-stability/draw-menagerie.json, menagerie-{...}.json                 60 programs x 4 dimensions
Each case was graded twice, under a high and a low attainment label (that study's manipulation). Labels
were assigned to cases independently of rater agreement, so they are balanced across this study's
strata; both arms are used, each case weighted once (per-case quantities average over the arms present).
The marks are therefore LABELLED marks, not an unlabelled control pass; no unlabelled pass exists on these
corpora. THE 150-ANSWER RUN behind the paper's 0.549 / 0.798 / 0.711 (`--mode taxonomy`) kept no per-case
dump, and its draw cannot be re-derived from the current harness (re-deriving `stratifiedSample(eligible,
150, 7)` gives rater-vs-rater 0.478, not the reported 0.608): those three figures cannot be re-scored and
are not. Only aggregates are committed (out/*.json).

COMMON CONVENTIONS. Marks are rounded half up (JavaScript Math.round, as the harness) and clipped onto the
scale for QWK and AC2; MAE, MSE and bias use the marks as returned. QWK is the harness's Cohen
quadratic-weighted kappa over the scale's own levels (studies/measurement/grader-eval/harness/metrics.ts),
re-implemented here and checked to reproduce 0.519, 0.465, 0.424 and the per-pair 0.035 / 0.410 / 0.730.
Scales: Mohler 0-5 (6 levels); Menagerie 0-13 (F..A++, 14 levels) and its bare-letter collapse (5 levels).
Clusters for every interval: Mohler questions (no learner id), Menagerie submissions (four dimensions share
the work and the raters). T2's human-human ceilings use the bootstrap OVER ITEMS that was asked for
(Mohler answers; Menagerie submissions) and report the question-clustered Mohler interval beside it.
4,000 resamples, percentile intervals. Every difference is signed and its direction stated.

================================================================== T1: STRATIFIED BY HUMAN AGREEMENT

STRATA (pre-registered).
  Mohler     AGREE = the two raters gave the same mark (|r1 - r2| = 0). Draw: 121 agree, 179 disagree.
  Menagerie  AGREE = all raters of the item within a span of 3 fine levels (range <= 3 on the 14-level
             scale). Draw: 86 agree, 154 disagree. "All within one level" (range <= 1) leaves 18 of 240
             items: positivity fails, so that rule cannot be used. Range <= 3 is the rule whose agree share
             on the draw (36%) is closest to Mohler's exact-agreement share on its draw (40%), and it is
             the widest span that keeps four raters inside one letter band plus one step (a letter is 3
             fine levels). Sensitivity (reported, no verdict): range <= 2 and <= 4.

QUANTITIES. Per case i, over the arms present and the item's raters k:
  e1_i = mean |g - r_k|           error against a SINGLE human reference (the paper's subject); integer
                                  against integer, so a split pair's half-point mean cannot inflate it
  em_i = mean |g - mean(r)|       error against the rater mean (the dump's `human`)
  b_i  = mean (g - mean(r))       signed bias against the rater mean (+ = grader above the humans)
  QWK / AC2 per stratum: grader vs every single rater, pooled rows (case x arm x rater).
LEVEL STANDARDISATION. Humans agree most at the ends of the scale, where clipping also shrinks any
grader's error, so a raw stratum difference carries the level mix. Each stratum's MAE is standardised to
the pooled distribution over six level bins (bin = round-half-up(mean(r) / range * 5)), using bins with
>= 3 cases in each stratum on the full sample (fixed outside the bootstrap). Raw differences reported.

P1 (primary)  D = std MAE_disagree(e1) - std MAE_agree(e1), as a FRACTION OF THE SCORE RANGE.
              Signed: D > 0 means the grader's single-reference error is larger where the humans disagree,
              i.e. the grader looks better where humans agree.
   GRADER-BETTER-WHERE-HUMANS-AGREE   95% interval of D above 0
   GRADER-WORSE-WHERE-HUMANS-AGREE    95% interval of D below 0
   NO-DIFFERENCE                      90% interval inside +/-0.03 of the range (0.15 points on 0-5,
                                      0.39 levels on 0-13; TOST, alpha 0.05)
   UNRESOLVED                         otherwise
   CONTROL (the size of the treatment): the same D with the stratum labels deranged within level bin
   (every case takes another case's label; same stratum sizes, same level mix; 200 derangements, mean
   and 95% range reported). It must sit near 0: a D the control also produces is composition, not
   human agreement.
P2 (primary)  rho = (MSE(h,h) / 2) / MSE(g,h): the share of the grader's mean squared error against a
              single human that is that human's own noise. With T the average rater's mark and errors
              independent, MSE(g,h_k) = E(g-T)^2 + E(r_k-T)^2 and MSE(h,h) = 2 E(r-T)^2. Unstratified;
              per case, MSE(h,h) over rater pairs and MSE(g,h) over arms x raters, ratio of means.
              Assumes the grader's errors are independent of each rater's (a grader that shares one
              rater's reading makes rho too high against the other and too low against that one; the
              two Mohler raters are also reported separately as rho_r1, rho_r2 with MSE(h,h)/2 as the
              noise of each, reported only).
   SHARE-SUBSTANTIAL   95% interval above 0.25 ("a substantial share", the paper's words, fixed at a quarter)
   SHARE-MINOR         95% interval below 0.25
   SHARE-UNRESOLVED    otherwise
P3 (REPORTED ONLY since floor rev 1; Menagerie only: needs four raters)  LEAVE-TWO-OUT. Stratifying on the same raters that form
              the reference makes the human-human comparison mechanical (agreeing raters agree). On items
              with four raters, each of the three splits {a,b}|{c,d} stratifies on |r_a - r_b| <= 1
              ("within one level") and measures on c and d only: hh = (r_c - r_d)^2, gh = mean over arms
              and {c,d} of (g - r)^2. Under independence MSE(gh) = s_g^2 + s_h^2 and MSE(hh) = 2 s_h^2, so
              the grader's own error in a stratum is sg2 = MSE(gh) - MSE(hh)/2, and
              dSG = sg2_disagree - sg2_agree (level-standardised as above, squared fine levels):
   (rev 0 rules, kept as labels; the floor showed they cannot be reached on 60 submissions, so P3 carries
   no verdict and the labels are printed only as a description of the interval)
   GRADIENT-IS-REFERENCE-NOISE                    90% interval of dSG inside +/-1.0 squared level
   GRADER-ALSO-WORSE-WHERE-HUMANS-DISAGREE         95% interval above 0
   GRADER-BETTER-WHERE-HUMANS-DISAGREE             95% interval below 0
   UNRESOLVED                                      otherwise
              Reported beside it: dMSE(gh), dMSE(hh), the share of dMSE(gh) that is reference noise
              (dMSE(hh)/2 / dMSE(gh)), and the Elangovan reading, the gap MAE(gh) - MAE(hh) per stratum.
Across models, per corpus: the shared verdict, else MIXED with each.

REFERENCE SWING (reported, feeds the overall verdict). Mohler: QWK(g, rater 2) - QWK(g, rater 1), signed,
per model (the paper's 0.25 is from the unrecoverable 150-answer run). Compared with the largest movement
of agreement by any intervention in Paper VI, 0.05 (section 1.2): SWING-EXCEEDS-INTERVENTIONS if the 95%
interval of |swing| lies above 0.05 (interval of the signed swing excludes [-0.05, 0.05]).

OVERALL T1 VERDICT on the paper's argument (six model x corpus cells for P1 and P2; three for the swing):
   BLUNT-INSTRUMENT-SUPPORTED   P1 BETTER in >= 4 of 6, P2 SUBSTANTIAL in >= 4 of 6, swing exceeds in >= 2 of 3
   BLUNT-INSTRUMENT-WEAKENED    P1 BETTER in <= 2 of 6, or P2 MINOR in >= 4 of 6, or swing exceeds in 0 of 3
   BLUNT-INSTRUMENT-PARTLY      otherwise
   P1 cannot tell reference noise on the disagree items (W2) from items that are also harder for the
   grader (W3): the floor shows both read BETTER. P3 was meant to separate them and cannot at this n
   (floor rev 0), so that question is left open and said so.

T1 FLOOR (`--floor`, before any real number). Synthetic two-rater (Mohler) and four-rater (Menagerie)
data on the real draws' clusters and level mix: truth T_i = the real rater mean + U(-0.5, 0.5) (continuous),
clipped; raters r = clip(round(T + N(0, s_h))), graders g = clip(round(T + N(0, s_g))), two arms each. s_g:
0.9 points (Mohler), 2.5 levels (Menagerie), fixed without reading any grader error. s_h is set so the
world's agree share matches the draw's. 200 replicates x 2,000 resamples per world:
  W0  NO-REFERENCE-NOISE  raters = round(T) exactly; strata assigned at random in level bin with the
                          real sizes (a "disagreement" that says nothing about the reference)
                          -> P1 BETTER <= 5%; P2 rho = 0. P1 NO-DIFFERENCE share reported (answerability)
  W1  REFERENCE-NOISE     independent homoscedastic rater noise -> P1 BETTER >= 80%; P2 recovers the
                          planted share (s_h^2 / (s_h^2 + s_g^2) before rounding; reported, with coverage)
  W2  AMBIGUOUS-ITEMS     rater noise x2.5 on a third of items (heteroscedastic), grader homoscedastic
                          -> P1 BETTER >= 80%; P3 rates reported
  W3  GRADER-HARD         as W2, and the grader's noise x2 on the same items
                          -> P1 BETTER >= 80% (P1 cannot tell W3 from W2: stated); P3 rates reported
  P2 SHARE worlds         W1 with s_h set for planted rho 0.10 and 0.50 -> MINOR / SUBSTANTIAL >= 80%
FLOOR RECORD (all before the pre-registration commit and before any grader mark was read):
  rev 0  as above, with P3 a primary verdict and "W0 P1 NO-DIFFERENCE >= 50%", "W2 P3
         GRADIENT-IS-REFERENCE-NOISE >= 50%", "W2 P3 GRADER-ALSO-WORSE <= 5%", "W3 P3 GRADER-ALSO-WORSE >= 80%"
         as pass conditions. P1 and P2 detected what was planted (W1 BETTER 88% / 90.5%, W2-W3 98-100%,
         W0 false BETTER 3% / 5%; P2 recovered the planted share, coverage 97-100%). FAILED on: Mohler W0
         NO-DIFFERENCE 45% (a null P1 on Mohler reads UNRESOLVED about half the time); P3 power: W2
         GRADIENT-IS-REFERENCE-NOISE 0%, W3 GRADER-ALSO-WORSE 23.5% (squared errors on 60 submissions are
         too noisy); and a crash on the Menagerie RHO10 world (no level bin populated in both strata).
  rev 1  (this) P3 demoted to reported-only; the NO-DIFFERENCE share is reported as answerability, not a
         pass condition; an empty standardisation returns UNRESOLVED. Nothing else changed.
A grader written and scored by this session is a smoke check of the instrument on the worlds it was told
about, not a validation of the real graders, and is reported as one.

================================================================== T2: GWET'S AC2 BESIDE EACH KAPPA

AC2 (Gwet 2008; Handbook 4th ed. ch. 3), quadratic weights w_kl = 1 - (k-l)^2/(q-1)^2 over the scale's q
levels (6, 14, 5: the same levels the QWK uses; AC2 on observed categories only is reported for the
ceilings as a sensitivity). Two raters: pa = sum w_kl p_kl, pi_k = (p_k. + p_.k)/2,
pe = sum(w) / (q(q-1)) * sum pi_k (1 - pi_k), AC2 = (pa - pe)/(1 - pe). Many raters with missing ratings
(Gwet's raw-ratings form, irrCAC gwet.ac1.raw): pa over items with >= 2 ratings,
pa_i = sum_k r_ik (r*_ik - 1) / (r_i (r_i - 1)), r*_ik = sum_l w_kl r_il; pi_k = mean_i r_ik / r_i.
TESTED before use (`--selftest`) on the published worked examples of Gwet's irrCAC package (vignettes
"overview" and "weighting", read 2026-10-06): cont3x3abstractors, quadratic: Cohen's kappa 0.8921569,
AC2 0.9402369; cac.raw4raters, quadratic: pa 0.9753788, pe 0.7137044, AC2 0.914; unweighted: pe 0.1903212,
AC1 0.77544. Plus: the two-rater and multi-rater forms agree on two-rater data, and a planted kappa paradox
(identical rater process, balanced vs skewed truth) must move QWK more than AC2.

COMPARISONS, each with QWK and AC2 and the paired difference AC2 - QWK:
  ceilings  Mohler r1 vs r2, 1,727 answers; Mohler r1 vs r2 on the 300-answer draw; Menagerie pooled pairs
            on 5 and 14 levels (6,600 pairs) and multi-rater AC2; Menagerie per rater pair (14 levels,
            n >= 30): min / q1 / median / q3 / max and the range max - min.
  grader    per model: Mohler g vs r1, g vs r2, g vs round(mean), on the draw; Menagerie g vs every rater
            (pooled) on the draw, 14 and 5 levels; and the human-human figures on the same rows.
  orderings O1 g-r1 minus r1-r2; O2 g-r2 minus r1-r2; O3 the swing (g-r2 minus g-r1); O4/O5 Menagerie
            g-h minus h-h on 14 and 5 levels: each per model, QWK difference and AC2 difference.
PRE-REGISTERED T2 RULES.
  LEVEL   a ceiling's level is STATISTIC-DEPENDENT if the 95% interval of AC2 - QWK lies wholly beyond
          +/-0.10 (above +0.10 or below -0.10); ROBUST if it lies inside +/-0.10; else UNRESOLVED.
  ORDER   an ordering FLIPS if the AC2 difference's 95% interval excludes 0 on the side opposite the QWK
          difference's sign; it is LOST if the QWK interval excludes 0 and the AC2 interval does not;
          GAINED the reverse; else HOLDS.
  SPREAD  the per-pair spread is ROBUST if the AC2 range is >= 0.5 x the QWK range, else STATISTIC-DEPENDENT.
  VERDICT CEILING-ROBUST if every ceiling level is ROBUST, no ordering FLIPS and the spread is ROBUST;
          CEILING-STATISTIC-DEPENDENT if any level is STATISTIC-DEPENDENT, any ordering FLIPS or the spread is
          STATISTIC-DEPENDENT (naming which); else CEILING-UNRESOLVED. Components are reported separately:
          a level that moves while every ordering holds means the comparisons survive and the stated
          numbers do not transfer between statistics.

RESULT (2026-10-06; pre-registered at b1b954d; README for the tables). T1 BLUNT-INSTRUMENT-SUPPORTED:
P1 BETTER in 4/6 cells (Menagerie all three, D +0.037 to +0.057 of the range; Mohler only Qwen, +0.055;
Gemini and GPT-4.1-mini UNRESOLVED once level is held fixed); P2 SHARE-SUBSTANTIAL 6/6 (rho 0.45-0.55),
with the independence assumption strained on Mohler (rater 1 +0.89 points on the draw; rho 0.38-0.41
against rater 1, 0.73-0.82 against rater 2); swing +0.23 to +0.27 on all three models. Against the rater
mean the gradient is nil. P3 UNRESOLVED on every model, as the floor predicted. T2
CEILING-STATISTIC-DEPENDENT (level: Mohler 1,727 0.519 -> AC2 0.858; Menagerie 0.465 -> 0.887 and
0.424 -> 0.749; spread: per-pair range 0.695 -> 0.307), no ordering flips; on the grade-stratified
Mohler draw the two agree (0.531 / 0.562). Post hoc (posthoc(), reported only): a constant grader scores
AC2 0.85 (Menagerie, always A-) and 0.93 (Mohler, always 5 vs rater 1), above the humans.

Usage:
  python3 robustness.py --verify   [--dump-dir D]   check the dumps against per-case-dumps.sha256
  python3 robustness.py --selftest                  AC2/QWK on the published worked examples
  python3 robustness.py --floor    [--dump-dir D]   T1 detection floor (no grader marks read)
  python3 robustness.py --run      [--dump-dir D]   T1 and T2 on the real data
  python3 robustness.py --posthoc  [--dump-dir D]   added after the run, reported only (see posthoc())
  D holds grader-label-stability/; else $GRADER_DUMP_DIR; else shared.paths.scratch_root().
  Corpora: MOHLER_DIR, MENAGERIE_DIR (or LDA_SCRATCH_DIR), as data/data-sources.json records.

ERRATUM (2026-10-06, Paper VI corrections-4; appended, nothing above is rewritten). The statement near the
top that the 150-answer draw "cannot be re-derived from the current harness" is wrong. That rebuild used the
`--mode taxonomy` draw, stratifiedSample(eligible, 150, 7) over the 1,609 answers whose module has four
sibling questions, which is a different 150 (rater-vs-rater 0.478). The paper's 0.608 / 0.549 / 0.798 /
0.711 come from `--mode ceiling`, whose draw is stratifiedSample(all 1,727, 150, 7); it rebuilds with no
model call to rater-vs-rater 0.6077 in the frozen vendor/934478716 snapshot and in the current harness
(studies/measurement/grader-eval/analyses/mohler_ceiling_draw.mts). The grader's own marks on that draw
were not kept per case, so 0.549 / 0.798 / 0.711 still cannot be re-scored here without a model call.
No number or verdict of this study changes.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
OUT = HERE / "out"
SHA_LIST = ROOT / "studies/measurement/grader-eval/analyses/per-case-dumps.sha256"
MODELS = {"gemini": "Gemini 3.5 Flash Lite", "gpt41mini": "GPT-4.1-mini", "qwen": "Qwen3-235B-A22B-2507"}
REPS = 4000
FLOOR_REPS = 200
FLOOR_BOOT = 2000
DELTA_P1 = 0.03       # of the range
RHO_BAR = 0.25
DELTA_P3 = 1.0        # squared fine levels
SWING_BAR = 0.05
LEVEL_BAR = 0.10
SPREAD_FRAC = 0.5
MEN_SCALE = ["F", "D-", "D", "D+", "C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+", "A++"]
LETTERS = ["F", "D", "C", "B", "A"]
COARSE = np.array([LETTERS.index(g[0]) for g in MEN_SCALE])


# ----------------------------------------------------------------------------- statistics

def rnd(x):
    """JavaScript Math.round for these scales: half up."""
    return np.floor(np.asarray(x, dtype=float) + 0.5)


def to_idx(x, lo, hi):
    return np.clip(rnd(x), lo, hi).astype(int) - lo


def qw(q):
    k = np.arange(q)
    return 1.0 - (k[:, None] - k[None, :]) ** 2 / (q - 1) ** 2


def tables(a, b, q, W=None):
    """Joint count tables of integer category indices a, b (0..q-1); W (B x n) gives B weighted tables."""
    flat = a * q + b
    if W is None:
        return np.bincount(flat, minlength=q * q).reshape(q, q).astype(float)
    onehot = np.zeros((len(a), q * q))
    onehot[np.arange(len(a)), flat] = 1.0
    return (W @ onehot).reshape(-1, q, q)


def qwk_t(T):
    """Cohen quadratic-weighted kappa (harness definition) from table(s) [..., q, q]."""
    q = T.shape[-1]
    d = 1.0 - qw(q)
    n = T.sum(axis=(-1, -2))
    r, c = T.sum(axis=-1), T.sum(axis=-2)
    num = (T * d).sum(axis=(-1, -2))
    exp = np.einsum("...i,...j->...ij", r, c) / n[..., None, None]
    den = (exp * d).sum(axis=(-1, -2))
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(den == 0, 0.0, 1.0 - num / den)


def ac2_t(T, q_eff=None):
    """Gwet AC2, quadratic weights, two raters, from table(s). q_eff: restrict to observed categories."""
    q = T.shape[-1]
    w = qw(q)
    n = T.sum(axis=(-1, -2))
    p = T / n[..., None, None]
    pa = (p * w).sum(axis=(-1, -2))
    pi = (p.sum(axis=-1) + p.sum(axis=-2)) / 2
    pe = w.sum() / (q * (q - 1)) * (pi * (1 - pi)).sum(axis=-1)
    return (pa - pe) / (1 - pe), pa, pe


def ac2_counts(C, w, item_w=None):
    """Gwet AC2 from per-item category counts C (n x q) and weight matrix w; item_w (B x n) for bootstrap."""
    q = C.shape[1]
    r = C.sum(axis=1)
    star = C @ w.T
    two = r >= 2
    pa_i = np.zeros(len(C))
    pa_i[two] = (C[two] * (star[two] - 1)).sum(axis=1) / (r[two] * (r[two] - 1))
    pi_i = np.where(r[:, None] > 0, C / np.maximum(r, 1)[:, None], 0.0)
    if item_w is None:
        item_w = np.ones((1, len(C)))
        single = True
    else:
        single = False
    pa = (item_w * (pa_i * two)).sum(axis=1) / (item_w * two).sum(axis=1)
    pi = (item_w @ pi_i) / item_w.sum(axis=1)[:, None]
    pe = w.sum() / (q * (q - 1)) * (pi * (1 - pi)).sum(axis=1)
    ac = (pa - pe) / (1 - pe)
    return (float(ac[0]), float(pa[0]), float(pe[0])) if single else (ac, pa, pe)


def cluster_weights(clusters, B, rng):
    """B x n item weights from resampling clusters with replacement (row 0 is NOT the identity)."""
    labels, inv = np.unique(np.asarray(clusters), return_inverse=True)
    C = len(labels)
    draws = rng.integers(0, C, size=(B, C))
    counts = np.zeros((B, C))
    np.add.at(counts, (np.repeat(np.arange(B), C), draws.ravel()), 1.0)
    return counts[:, inv]


def ci(vals, point, alpha=0.05):
    v = np.asarray(vals, dtype=float)
    v = v[~np.isnan(v)]
    if not len(v):
        return {"est": float(point), "lo": float("nan"), "hi": float("nan")}
    lo, hi = np.percentile(v, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return {"est": float(point), "lo": float(lo), "hi": float(hi)}


def ci90(vals):
    v = np.asarray(vals, dtype=float)
    v = v[~np.isnan(v)]
    if not len(v):
        return [float("nan"), float("nan")]
    return [float(x) for x in np.percentile(v, [5, 95])]


# ----------------------------------------------------------------------------- data

def dump_root(override):
    raw = override or os.environ.get("GRADER_DUMP_DIR")
    if raw:
        return Path(raw).expanduser()
    from shared.paths import scratch_root
    return scratch_root()


def verify(root):
    want = {}
    for line in SHA_LIST.read_text().splitlines():
        h, f = line.split()
        want[f] = h
    used = [f"grader-label-stability/{c}-{m}.json" for c in ("mohler", "menagerie") for m in MODELS] + \
           ["grader-label-stability/draw-mohler.json", "grader-label-stability/draw-menagerie.json"]
    res = {}
    for f in used:
        got = hashlib.sha256((root / f).read_bytes()).hexdigest()
        res[f] = got == want[f]
        if got != want[f]:
            raise SystemExit(f"{f}: sha256 {got} does not match per-case-dumps.sha256 ({want[f]})")
    return res


def load_mohler_raters():
    from shared.paths import data_path
    path = data_path("MOHLER_DIR") / "mohler_en.csv"
    out = {}
    for r in csv.DictReader(open(path, encoding="utf-8")):
        try:
            a, b, m = float(r["score_grader_1"]), float(r["score_grader_2"]), float(r["score_avg"])
        except (TypeError, ValueError):
            continue
        if not (0 <= a <= 5 and 0 <= b <= 5) or abs((a + b) / 2 - m) > 1e-9:
            continue
        if not (r["student_answer"] or "").strip() or not (r["question"] or "").strip():
            continue
        out[r["id"]] = (a, b)
    return out


def load_menagerie_raters():
    from shared.paths import data_path
    path = data_path("MENAGERIE_DIR") / "grades.csv"
    idx = {g: i for i, g in enumerate(MEN_SCALE)}
    items = {}
    for r in csv.DictReader(open(path, encoding="utf-8", newline="")):
        p = idx.get(r["grade"])
        if p is None:
            continue
        a = re.sub(r"\.0+$", "", (r["assignment_number"] or "").strip())
        items.setdefault(f"{a}|{r['skill']}", {})[r["participant_id"]] = p
    return {k: v for k, v in items.items() if len(v) >= 2}


def load_cases(root, corpus, raters):
    """Per case: id, cluster, rater marks (list), grader marks per model (list over arms present)."""
    draw = json.load(open(root / f"grader-label-stability/draw-{corpus}.json"))["rows"]
    cases = []
    for r in draw:
        rr = raters[r["id"]]
        rv = list(rr) if corpus == "mohler" else [rr[k] for k in sorted(rr)]
        cases.append({"id": r["id"], "cluster": r["cluster"], "raters": [float(x) for x in rv],
                      "human": float(r["human"])})
        if abs(np.mean(rv) - r["human"]) > 1e-9:
            raise SystemExit(f"{corpus} {r['id']}: rater mean {np.mean(rv)} != dump human {r['human']}")
    return cases


def attach_marks(root, corpus, cases):
    out = {}
    for m in MODELS:
        rows = {r["id"]: r for r in json.load(open(root / f"grader-label-stability/{corpus}-{m}.json"))["rows"]}
        out[m] = [[float(x) for x in (rows[c["id"]]["high"], rows[c["id"]]["low"]) if x is not None]
                  for c in cases]
    return out


# ----------------------------------------------------------------------------- T1 quantities

def level_bins(means, rng_max):
    return rnd(np.asarray(means) / rng_max * 5).astype(int)


def usable_bins(bins, strat, min_n=3):
    return [b for b in np.unique(bins) if (strat[bins == b] == 0).sum() >= min_n and (strat[bins == b] == 1).sum() >= min_n]


def std_diff(W, e, strat, bins, ub, absval=False):
    """Level-standardised mean(e | disagree) - mean(e | agree), per weight row; NaN where a bin empties."""
    if not len(ub):   # no level bin populated in both strata: the standardised contrast does not exist
        nan = np.full(W.shape[0], np.nan)
        return nan, nan, nan
    num = {0: [], 1: []}
    den = {0: [], 1: []}
    for s in (0, 1):
        for b in ub:
            m = (strat == s) & (bins == b)
            num[s].append(W @ (e * m))
            den[s].append(W @ m.astype(float))
    N0, N1 = np.array(den[0]), np.array(den[1])
    with np.errstate(invalid="ignore", divide="ignore"):
        share = (N0 + N1) / (N0 + N1).sum(axis=0)
        m0 = (share * np.array(num[0]) / N0).sum(axis=0)
        m1 = (share * np.array(num[1]) / N1).sum(axis=0)
        bad = (N0 == 0).any(axis=0) | (N1 == 0).any(axis=0)
    d = m1 - m0
    d[bad] = np.nan
    return d, m0, m1


def raw_diff(W, e, strat):
    with np.errstate(invalid="ignore", divide="ignore"):
        m1 = (W @ (e * (strat == 1))) / (W @ (strat == 1).astype(float))
        m0 = (W @ (e * (strat == 0))) / (W @ (strat == 0).astype(float))
    return m1 - m0, m0, m1


def per_case(cases, marks):
    """e1 (single-rater abs), em (vs mean abs), bias, se1 (single-rater sq), shh (rater-pair sq) per case."""
    e1, em, bias, se1, shh = [], [], [], [], []
    for c, g in zip(cases, marks):
        r = np.array(c["raters"])
        g = np.array(g)
        e1.append(np.abs(g[:, None] - r[None, :]).mean() if len(g) else np.nan)
        em.append(np.abs(g - r.mean()).mean() if len(g) else np.nan)
        bias.append((g - r.mean()).mean() if len(g) else np.nan)
        se1.append(((g[:, None] - r[None, :]) ** 2).mean() if len(g) else np.nan)
        shh.append(np.mean([(a - b) ** 2 for a, b in combinations(r, 2)]))
    return {k: np.array(v) for k, v in dict(e1=e1, em=em, bias=bias, se1=se1, shh=shh).items()}


def strata(cases, corpus, span=3):
    if corpus == "mohler":
        return np.array([int(c["raters"][0] != c["raters"][1]) for c in cases])
    return np.array([int(max(c["raters"]) - min(c["raters"]) > span) for c in cases])


def p1_verdict(d, lo, hi, l90, h90):
    if np.isnan(d):
        return "UNRESOLVED"
    if lo > 0:
        return "GRADER-BETTER-WHERE-HUMANS-AGREE"
    if hi < 0:
        return "GRADER-WORSE-WHERE-HUMANS-AGREE"
    if -DELTA_P1 < l90 and h90 < DELTA_P1:
        return "NO-DIFFERENCE"
    return "UNRESOLVED"


def p2_verdict(lo, hi):
    if lo > RHO_BAR:
        return "SHARE-SUBSTANTIAL"
    if hi < RHO_BAR:
        return "SHARE-MINOR"
    return "SHARE-UNRESOLVED"


def p3_verdict(lo, hi, l90, h90):
    if -DELTA_P3 < l90 and h90 < DELTA_P3:
        return "GRADIENT-IS-REFERENCE-NOISE"
    if lo > 0:
        return "GRADER-ALSO-WORSE-WHERE-HUMANS-DISAGREE"
    if hi < 0:
        return "GRADER-BETTER-WHERE-HUMANS-DISAGREE"
    return "UNRESOLVED"


def t1_p1(cases, marks, corpus, W, rng_max, span=3, with_control=False, rng=None, detail=True):
    pc = per_case(cases, marks)
    keep = ~np.isnan(pc["e1"])
    strat = strata(cases, corpus, span)
    bins = level_bins([c["human"] for c in cases], rng_max)
    sub = lambda a: a[keep]
    st, bn, Wk = strat[keep], bins[keep], W[:, keep]
    ub = usable_bins(bn, st)
    e = sub(pc["e1"]) / rng_max
    I = np.ones((1, len(e)))
    d0, a0, b0 = std_diff(I, e, st, bn, ub)
    dB, _, _ = std_diff(Wk, e, st, bn, ub)
    res = {"D": ci(dB, d0[0]), "D_90": ci90(dB), "verdict": None,
           "n_agree": int((st == 0).sum()), "n_disagree": int((st == 1).sum()), "bins_used": [int(b) for b in ub]}
    res["verdict"] = p1_verdict(d0[0], res["D"]["lo"], res["D"]["hi"], *res["D_90"])
    if not detail:
        return res
    res["std_mae_agree_frac"], res["std_mae_disagree_frac"] = float(a0[0]), float(b0[0])
    rd0, ra, rb = raw_diff(I, e, st)
    rdB, _, _ = raw_diff(Wk, e, st)
    res["D_raw"] = ci(rdB, rd0[0])
    res["mae_single_points"] = {"agree": float(ra[0] * rng_max), "disagree": float(rb[0] * rng_max)}
    em = sub(pc["em"]) / rng_max
    dm0, ma, mb = std_diff(I, em, st, bn, ub)
    dmB, _, _ = std_diff(Wk, em, st, bn, ub)
    res["D_vs_mean"] = ci(dmB, dm0[0])
    res["mae_vs_mean_points"] = {"agree": float(ma[0] * rng_max), "disagree": float(mb[0] * rng_max)}
    bi = sub(pc["bias"])
    for s, name in ((0, "agree"), (1, "disagree")):
        m = (st == s).astype(float)
        with np.errstate(invalid="ignore", divide="ignore"):
            bb = (Wk @ (bi * m)) / (Wk @ m)
        res.setdefault("bias_vs_mean_points", {})[name] = ci(bb, (bi * m).sum() / m.sum())
    if with_control:
        ctrl = []
        idx = np.arange(len(st))
        for _ in range(200):
            lab = st.copy()
            for b in np.unique(bn):
                pos = idx[bn == b]
                if len(pos) < 2:
                    continue
                perm = derange(len(pos), rng)
                lab[pos] = st[pos[perm]]
            ub_c = usable_bins(bn, lab)
            dc, _, _ = std_diff(I, e, lab, bn, ub_c)
            ctrl.append(dc[0])
        ctrl = np.array(ctrl)
        res["control_deranged_D"] = {"mean": float(np.nanmean(ctrl)),
                                     "p2.5": float(np.nanpercentile(ctrl, 2.5)),
                                     "p97.5": float(np.nanpercentile(ctrl, 97.5)), "n": 200,
                                     "relabelled_per_derangement": int(len(st))}
    return res


def derange(n, rng):
    while True:
        p = rng.permutation(n)
        if not (p == np.arange(n)).any():
            return p


def t1_p2(cases, marks, W):
    pc = per_case(cases, marks)
    keep = ~np.isnan(pc["se1"])
    se, hh = pc["se1"][keep], pc["shh"][keep]
    Wk = W[:, keep]
    point = (hh.mean() / 2) / se.mean()
    boot = (Wk @ hh / 2) / (Wk @ se)
    out = {"rho": ci(boot, point), "mse_gh": float(se.mean()), "mse_hh": float(hh.mean())}
    out["verdict"] = p2_verdict(out["rho"]["lo"], out["rho"]["hi"])
    return out


def t1_p2_per_rater(cases, marks):
    """Mohler only: rho against each rater separately (reported only)."""
    res = {}
    for k in (0, 1):
        se, hh = [], []
        for c, g in zip(cases, marks):
            if not g:
                continue
            r = c["raters"]
            se.append(np.mean([(x - r[k]) ** 2 for x in g]))
            hh.append((r[0] - r[1]) ** 2)
        res[f"rho_r{k + 1}"] = float((np.mean(hh) / 2) / np.mean(se))
        res[f"mse_g_r{k + 1}"] = float(np.mean(se))
    return res


def p3_rows(cases, marks):
    """Leave-two-out rows: (cluster, level, stratum, gh, hh, gh_abs, hh_abs) for items with 4 raters."""
    rows = []
    for ci_, (c, g) in enumerate(zip(cases, marks)):
        r = c["raters"]
        if len(r) != 4 or not g:
            continue
        g = np.array(g)
        for a, b in ((0, 1), (0, 2), (0, 3)):
            cd = [k for k in range(4) if k not in (a, b)]
            rc, rd = r[cd[0]], r[cd[1]]
            rows.append((c["cluster"], c["human"], int(abs(r[a] - r[b]) > 1),
                         float(np.mean([(g - rc) ** 2, (g - rd) ** 2])), (rc - rd) ** 2,
                         float(np.mean([np.abs(g - rc), np.abs(g - rd)])), abs(rc - rd), ci_))
    return rows


def t1_p3(cases, marks, rng_max, B, rng, clusters_all=None, W=None):
    rows = p3_rows(cases, marks)
    cl = np.array([r[0] for r in rows])
    lev = level_bins([r[1] for r in rows], rng_max)
    st = np.array([r[2] for r in rows])
    gh, hh = np.array([r[3] for r in rows]), np.array([r[4] for r in rows])
    gha, hha = np.array([r[5] for r in rows]), np.array([r[6] for r in rows])
    if W is None:
        W = cluster_weights(cl, B, rng)
    else:
        case_idx = np.array([r[7] for r in rows])
        W = W[:, case_idx]
    ub = usable_bins(lev, st)
    I = np.ones((1, len(rows)))
    sg = gh - hh / 2
    d0, sa, sd = std_diff(I, sg, st, lev, ub)
    dB, _, _ = std_diff(W, sg, st, lev, ub)
    out = {"dSG": ci(dB, d0[0]), "dSG_90": ci90(dB), "sg2_agree": float(sa[0]), "sg2_disagree": float(sd[0]),
           "rows": len(rows), "rows_agree": int((st == 0).sum()), "rows_disagree": int((st == 1).sum())}
    out["verdict"] = p3_verdict(out["dSG"]["lo"], out["dSG"]["hi"], *out["dSG_90"])
    g0, ga, gd = std_diff(I, gh, st, lev, ub)
    h0, ha, hd = std_diff(I, hh, st, lev, ub)
    out["dMSE_gh"], out["dMSE_hh"] = float(g0[0]), float(h0[0])
    out["mse_gh"] = {"agree": float(ga[0]), "disagree": float(gd[0])}
    out["mse_hh"] = {"agree": float(ha[0]), "disagree": float(hd[0])}
    out["ref_noise_share_of_gradient"] = float((h0[0] / 2) / g0[0]) if g0[0] != 0 else None
    ea = std_diff(I, gha, st, lev, ub)
    eh = std_diff(I, hha, st, lev, ub)
    out["elangovan_gap_mae"] = {"agree": float(ea[1][0] - eh[1][0]), "disagree": float(ea[2][0] - eh[2][0]),
                                "note": "MAE(grader, human) - MAE(human, human) on the held-out pair; "
                                        "positive = grader further from humans than humans are from each other"}
    return out


# ----------------------------------------------------------------------------- floor

def synth(cases, n_raters, rng_max, s_h, s_g, rng, world, amb=None):
    T = np.clip(np.array([c["human"] for c in cases]) + rng.uniform(-0.5, 0.5, len(cases)), 0, rng_max)
    n = len(T)
    sh = np.full(n, s_h)
    sgv = np.full(n, s_g)
    if world in ("W2", "W3"):
        sh = np.where(amb, s_h * 2.5, s_h)
        if world == "W3":
            sgv = np.where(amb, s_g * 2, s_g)
    if world == "W0":
        R = np.repeat(np.clip(rnd(T), 0, rng_max)[:, None], n_raters, axis=1)
    else:
        R = np.clip(rnd(T[:, None] + rng.normal(0, 1, (n, n_raters)) * sh[:, None]), 0, rng_max)
    G = np.clip(rnd(T[:, None] + rng.normal(0, 1, (n, 2)) * sgv[:, None]), 0, rng_max)
    out = []
    for i, c in enumerate(cases):
        out.append({"id": c["id"], "cluster": c["cluster"], "raters": list(R[i]), "human": float(R[i].mean())})
    synth.last = float(((R - T[:, None]) ** 2).mean() / (((R - T[:, None]) ** 2).mean() + ((G - T[:, None]) ** 2).mean()))
    return out, [list(G[i]) for i in range(n)]


def agree_share(cases, corpus, span=3):
    return float((strata(cases, corpus, span) == 0).mean())


def calibrate_sh(cases, corpus, n_raters, rng_max, target, rng, amb=None, world="W1"):
    best = None
    for s in np.linspace(0.1, 4.0, 79):
        sh_ = []
        for _ in range(6):
            sc, _ = synth(cases, n_raters, rng_max, s, 1.0, rng, world, amb)
            sh_.append(agree_share(sc, corpus))
        a = np.mean(sh_)
        if best is None or abs(a - target) < abs(best[1] - target):
            best = (float(s), float(a))
    return best


def run_floor(root):
    rng = np.random.default_rng(20261006)
    mo_r, me_r = load_mohler_raters(), load_menagerie_raters()
    out = {"note": "synthetic graders on the real draws' clusters and level mix; no grader mark read",
           "reps": FLOOR_REPS, "boot": FLOOR_BOOT}
    for corpus, raters, nr, rmax, s_g in (("mohler", mo_r, 2, 5, 0.9), ("menagerie", me_r, 4, 13, 2.5)):
        cases = load_cases(root, corpus, raters)
        real_strat = strata(cases, corpus)
        target = 1 - real_strat.mean()
        amb = rng.random(len(cases)) < 1 / 3
        cal = {w: calibrate_sh(cases, corpus, nr, rmax, target, rng, amb, w) for w in ("W1", "W2")}
        res = {"agree_share_target": float(target), "s_g": s_g, "calibrated_s_h": cal}
        bins_real = level_bins([c["human"] for c in cases], rmax)
        worlds = ["W0", "W1", "W2", "W3"]
        # planted-share worlds for P2: s_h for rho = 0.10 and 0.50 (before rounding)
        rho_worlds = {"RHO10": s_g * np.sqrt(0.10 / 0.90), "RHO50": s_g}
        for w in worlds + list(rho_worlds):
            tally = {}
            rhos, covers, planted_l = [], 0, []
            for rep in range(FLOOR_REPS):
                if w in rho_worlds:
                    s_h, ww = rho_worlds[w], "W1"
                else:
                    s_h, ww = (cal["W2"][0] if w in ("W2", "W3") else cal["W1"][0]), w
                sc, G = synth(cases, nr, rmax, s_h, s_g, rng, ww, amb)
                if ww == "W0":
                    # strata assigned at random within level bin with the real sizes
                    lab = real_strat.copy()
                    for b in np.unique(bins_real):
                        pos = np.where(bins_real == b)[0]
                        lab[pos] = lab[pos[rng.permutation(len(pos))]]
                    sc = [dict(c, _lab=int(l)) for c, l in zip(sc, lab)]
                W = cluster_weights([c["cluster"] for c in sc], FLOOR_BOOT, rng)
                if ww == "W0":
                    p1 = t1_p1_given(sc, G, rmax, W, np.array([c["_lab"] for c in sc]))
                else:
                    p1 = t1_p1(sc, G, corpus, W, rmax, detail=False)
                tally["P1:" + p1["verdict"]] = tally.get("P1:" + p1["verdict"], 0) + 1
                p2 = t1_p2(sc, G, W)
                tally["P2:" + p2["verdict"]] = tally.get("P2:" + p2["verdict"], 0) + 1
                rhos.append(p2["rho"]["est"])
                planted = synth.last if ww == "W1" else None   # in-sample share, after rounding and clipping
                if planted is not None:
                    planted_l.append(planted)
                    covers += int(p2["rho"]["lo"] <= planted <= p2["rho"]["hi"])
                if corpus == "menagerie" and w in ("W1", "W2", "W3"):
                    p3 = t1_p3(sc, G, rmax, FLOOR_BOOT, rng)
                    tally["P3:" + p3["verdict"]] = tally.get("P3:" + p3["verdict"], 0) + 1
            entry = {k: v / FLOOR_REPS for k, v in sorted(tally.items())}
            entry["rho_mean"] = float(np.mean(rhos))
            if w in ("W1",) or w in rho_worlds:
                entry["rho_planted_before_rounding"] = float(s_h ** 2 / (s_h ** 2 + s_g ** 2))
                entry["rho_planted_in_sample_mean"] = float(np.mean(planted_l))
                entry["rho_coverage_of_in_sample"] = covers / FLOOR_REPS
            res[w] = entry
            print(corpus, w, json.dumps(entry), flush=True)
        out[corpus] = res
    out["criteria"] = floor_criteria(out)
    return out


def t1_p1_given(cases, marks, rng_max, W, strat):
    """P1 with strata supplied (floor W0)."""
    pc = per_case(cases, marks)
    bins = level_bins([c["human"] for c in cases], rng_max)
    ub = usable_bins(bins, strat)
    e = pc["e1"] / rng_max
    d0, _, _ = std_diff(np.ones((1, len(e))), e, strat, bins, ub)
    dB, _, _ = std_diff(W, e, strat, bins, ub)
    c = ci(dB, d0[0])
    return {"verdict": p1_verdict(d0[0], c["lo"], c["hi"], *ci90(dB))}


def floor_criteria(fl):
    """Rev 1 (see the docstring's FLOOR RECORD): pass conditions, and answerability reported only."""
    crit, rep = {}, {}
    for corpus in ("mohler", "menagerie"):
        f = fl[corpus]
        g = lambda w, k: f[w].get(k, 0.0)
        crit[corpus] = {
            "W0 P1 BETTER <= 5%": g("W0", "P1:GRADER-BETTER-WHERE-HUMANS-AGREE") <= 0.05,
            "W1 P1 BETTER >= 80%": g("W1", "P1:GRADER-BETTER-WHERE-HUMANS-AGREE") >= 0.80,
            "W2 P1 BETTER >= 80%": g("W2", "P1:GRADER-BETTER-WHERE-HUMANS-AGREE") >= 0.80,
            "W3 P1 BETTER >= 80%": g("W3", "P1:GRADER-BETTER-WHERE-HUMANS-AGREE") >= 0.80,
            "RHO10 P2 MINOR >= 80%": g("RHO10", "P2:SHARE-MINOR") >= 0.80,
            "RHO50 P2 SUBSTANTIAL >= 80%": g("RHO50", "P2:SHARE-SUBSTANTIAL") >= 0.80,
        }
        rep[corpus] = {"W0 P1 NO-DIFFERENCE (answerability; >= 50% would make a null reachable)":
                       g("W0", "P1:NO-DIFFERENCE")}
        if corpus == "menagerie":
            rep[corpus].update({
                "W2 P3 GRADIENT-IS-REFERENCE-NOISE": g("W2", "P3:GRADIENT-IS-REFERENCE-NOISE"),
                "W2 P3 GRADER-ALSO-WORSE (false)": g("W2", "P3:GRADER-ALSO-WORSE-WHERE-HUMANS-DISAGREE"),
                "W3 P3 GRADER-ALSO-WORSE (power)": g("W3", "P3:GRADER-ALSO-WORSE-WHERE-HUMANS-DISAGREE"),
            })
    crit["all_passed"] = all(v for c in ("mohler", "menagerie") for v in crit[c].values())
    crit["reported_only"] = rep
    return crit


# ----------------------------------------------------------------------------- self-test (T2 instrument)

RAW4 = [[1, 1, None, 1], [2, 2, 3, 2], [3, 3, 3, 3], [3, 3, 3, 3], [2, 2, 2, 2], [1, 2, 3, 4], [4, 4, 4, 4],
        [1, 1, 2, 1], [2, 2, 2, 2], [None, 5, 5, 5], [None, None, 1, 1], [None, None, 3, None]]


def counts_from_raw(raw, cats):
    C = np.zeros((len(raw), len(cats)))
    for i, row in enumerate(raw):
        for x in row:
            if x is not None:
                C[i, cats.index(x)] += 1
    return C


def selftest():
    res = {}
    T = np.array([[13, 0, 0], [0, 20, 7], [0, 4, 56]], dtype=float)
    k = float(qwk_t(T))
    a, pa, pe = ac2_t(T)
    res["cont3x3abstractors"] = {"qwk": k, "qwk_published": 0.8921569, "ac2": float(a), "ac2_published": 0.9402369}
    C = counts_from_raw(RAW4, [1, 2, 3, 4, 5])
    a2, pa2, pe2 = ac2_counts(C, qw(5))
    a1, pa1, pe1 = ac2_counts(C, np.eye(5))
    res["cac.raw4raters_quadratic"] = {"ac2": a2, "pa": pa2, "pe": pe2, "published": {"ac2": 0.914, "pa": 0.9753788, "pe": 0.7137044}}
    res["cac.raw4raters_identity"] = {"ac1": a1, "pa": pa1, "pe": pe1, "published": {"ac1": 0.77544, "pa": 0.8181818, "pe": 0.1903212}}
    ok = (abs(k - 0.8921569) < 5e-7 and abs(float(a) - 0.9402369) < 5e-7 and abs(a2 - 0.914) < 5e-4
          and abs(pa2 - 0.9753788) < 5e-7 and abs(pe2 - 0.7137044) < 5e-7 and abs(a1 - 0.77544) < 5e-6
          and abs(pe1 - 0.1903212) < 5e-7)
    # two-rater vs multi-rater form on the same two-rater data
    rng = np.random.default_rng(3)
    x = rng.integers(0, 6, 400)
    y = np.clip(x + rng.integers(-1, 2, 400), 0, 5)
    Cxy = np.zeros((400, 6))
    Cxy[np.arange(400), x] += 1
    Cxy[np.arange(400), y] += 1
    two = float(ac2_t(tables(x, y, 6))[0])
    multi = ac2_counts(Cxy, qw(6))[0]
    res["two_vs_multi_form"] = {"two_rater": two, "multi_rater": multi}
    ok = ok and abs(two - multi) < 1e-12
    # planted kappa paradox: identical rater process, balanced vs skewed truth
    para = {}
    for name, p in (("balanced", np.ones(6) / 6), ("skewed", np.array([.02, .02, .03, .05, .13, .75]))):
        qs, acs = [], []
        for _ in range(200):
            t = rng.choice(6, 1000, p=p)
            r1 = np.where(rng.random(1000) < 0.7, t, np.clip(t + rng.choice([-2, -1, 1, 2], 1000), 0, 5))
            r2 = np.where(rng.random(1000) < 0.7, t, np.clip(t + rng.choice([-2, -1, 1, 2], 1000), 0, 5))
            TT = tables(r1, r2, 6)
            qs.append(float(qwk_t(TT)))
            acs.append(float(ac2_t(TT)[0]))
        para[name] = {"qwk": float(np.mean(qs)), "ac2": float(np.mean(acs))}
    para["qwk_drop"] = para["balanced"]["qwk"] - para["skewed"]["qwk"]
    para["ac2_drop"] = para["balanced"]["ac2"] - para["skewed"]["ac2"]
    res["planted_kappa_paradox"] = para
    ok = ok and para["qwk_drop"] > para["ac2_drop"]
    res["passed"] = bool(ok)
    return res


# ----------------------------------------------------------------------------- T2

def pair_stats(a, b, q, W):
    """QWK, AC2 and AC2 - QWK with bootstrap over the supplied weights."""
    T0 = tables(a, b, q)
    TB = tables(a, b, q, W)
    k0, kB = float(qwk_t(T0)), qwk_t(TB)
    a0, aB = float(ac2_t(T0)[0]), ac2_t(TB)[0]
    obs = sorted(set(a.tolist()) | set(b.tolist()))
    sub = T0[np.ix_(obs, obs)]
    return {"n": int(len(a)), "qwk": ci(kB, k0), "ac2": ci(aB, a0), "ac2_minus_qwk": ci(aB - kB, a0 - k0),
            "ac2_observed_categories_only": float(ac2_t(sub)[0]),
            "pa_weighted": float(ac2_t(T0)[1]), "pe_ac2": float(ac2_t(T0)[2]), "_kB": kB, "_aB": aB}


def level_rule(c):
    lo, hi = c["lo"], c["hi"]
    if lo > LEVEL_BAR or hi < -LEVEL_BAR:
        return "STATISTIC-DEPENDENT"
    if -LEVEL_BAR < lo and hi < LEVEL_BAR:
        return "ROBUST"
    return "UNRESOLVED"


def order_rule(dq, da):
    """dq, da: dicts est/lo/hi of the QWK and AC2 differences."""
    sgn = np.sign(dq["est"])
    if (sgn > 0 and da["hi"] < 0) or (sgn < 0 and da["lo"] > 0):
        return "FLIPS"
    q_res = dq["lo"] > 0 or dq["hi"] < 0
    a_res = da["lo"] > 0 or da["hi"] < 0
    if q_res and not a_res:
        return "LOST"
    if a_res and not q_res:
        return "GAINED"
    return "HOLDS"


def strip(d):
    if isinstance(d, dict):
        return {k: strip(v) for k, v in d.items() if not k.startswith("_")}
    if isinstance(d, list):
        return [strip(v) for v in d]
    return d


def run_t2(root, mo_r, me_r, mo_cases, me_cases, mo_marks, me_marks, rng):
    out = {"ceilings": {}, "grader": {}, "orderings": {}}
    # ---- Mohler full ceiling: bootstrap over answers (asked) and over questions (sensitivity)
    ids = sorted(mo_r)
    a = np.array([int(mo_r[i][0]) for i in ids])
    b = np.array([int(mo_r[i][1]) for i in ids])
    q_of = [".".join(i.split(".")[:2]) for i in ids]
    W_item = cluster_weights(ids, REPS, rng)
    W_q = cluster_weights(q_of, REPS, rng)
    m_full = pair_stats(a, b, 6, W_item)
    m_full["question_clustered"] = strip({k: v for k, v in pair_stats(a, b, 6, W_q).items()
                                          if k in ("qwk", "ac2", "ac2_minus_qwk")})
    out["ceilings"]["mohler_r1_r2_1727"] = m_full
    # ---- Mohler draw (300): human-human on the grader rows
    da = np.array([int(c["raters"][0]) for c in mo_cases])
    db = np.array([int(c["raters"][1]) for c in mo_cases])
    Wd_item = cluster_weights([c["id"] for c in mo_cases], REPS, rng)
    out["ceilings"]["mohler_r1_r2_draw300"] = pair_stats(da, db, 6, Wd_item)
    # ---- Menagerie pooled pairs (6,600), bootstrap over submissions
    items = sorted(me_r)
    pa_, pb_, pcl, pkey = [], [], [], []
    for it in items:
        rs = sorted(me_r[it])
        for i, j in combinations(rs, 2):
            pa_.append(me_r[it][i]); pb_.append(me_r[it][j]); pcl.append(it.split("|")[0]); pkey.append(f"{i}|{j}")
    pa_, pb_ = np.array(pa_), np.array(pb_)
    sub_of_item = [it.split("|")[0] for it in items]
    subs = sorted(set(sub_of_item))
    rng_sub = rng.integers(0, len(subs), size=(REPS, len(subs)))
    cnt = np.zeros((REPS, len(subs)))
    np.add.at(cnt, (np.repeat(np.arange(REPS), len(subs)), rng_sub.ravel()), 1.0)
    s_index = {s: k for k, s in enumerate(subs)}
    W_pairs = cnt[:, [s_index[s] for s in pcl]]
    W_items = cnt[:, [s_index[s] for s in sub_of_item]]
    out["ceilings"]["menagerie_pooled_5level"] = pair_stats(COARSE[pa_], COARSE[pb_], 5, W_pairs)
    out["ceilings"]["menagerie_pooled_14level"] = pair_stats(pa_, pb_, 14, W_pairs)
    for lvl, q, mp in (("14level", 14, lambda x: x), ("5level", 5, lambda x: COARSE[x])):
        C = np.zeros((len(items), q))
        for i, it in enumerate(items):
            for v in me_r[it].values():
                C[i, mp(np.array(v))] += 1
        a0, pa0, pe0 = ac2_counts(C, qw(q))
        aB, _, _ = ac2_counts(C, qw(q), W_items)
        out["ceilings"][f"menagerie_multirater_ac2_{lvl}"] = {"ac2": ci(aB, a0), "pa": pa0, "pe": pe0,
                                                              "items": len(items)}
    # ---- Menagerie per rater pair (14 levels, n >= 30)
    keys = sorted(set(pkey))
    pkey = np.array(pkey)
    per = []
    for kk in keys:
        m = pkey == kk
        if m.sum() < 30:
            continue
        T0 = tables(pa_[m], pb_[m], 14)
        TB = tables(pa_[m], pb_[m], 14, W_pairs[:, m])
        per.append((kk, int(m.sum()), float(qwk_t(T0)), float(ac2_t(T0)[0]), qwk_t(TB), ac2_t(TB)[0]))
    qk = np.array([p[2] for p in per]); ak = np.array([p[3] for p in per])
    qB = np.array([p[4] for p in per]); aB = np.array([p[5] for p in per])

    def at(v, qq):
        s = np.sort(v)
        return float(s[min(len(s) - 1, int(np.floor(qq * len(s))))])

    def summ(vec, boot):
        o = {}
        for name, fn in (("min", lambda v: np.min(v, axis=0)),
                         ("median", lambda v: np.sort(v, axis=0)[len(v) // 2]),   # the harness's at(0.5)
                         ("max", lambda v: np.max(v, axis=0)),
                         ("range", lambda v: np.max(v, axis=0) - np.min(v, axis=0))):
            o[name] = ci(fn(boot), float(fn(vec)))
        o["q1"], o["q3"] = at(vec, 0.25), at(vec, 0.75)
        return o
    out["ceilings"]["menagerie_per_pair_14level"] = {
        "pairs": len(per), "qwk": summ(qk, qB), "ac2": summ(ak, aB),
        "spearman_qwk_ac2_across_pairs": float(np.corrcoef(np.argsort(np.argsort(qk)), np.argsort(np.argsort(ak)))[0, 1]),
        "pairs_detail": [{"pair": p[0], "n": p[1], "qwk": p[2], "ac2": p[3]} for p in per]}
    # ---- grader vs human on the draws
    Wm = cluster_weights([c["cluster"] for c in mo_cases], REPS, rng)
    Wn = cluster_weights([c["cluster"] for c in me_cases], REPS, rng)
    # human-human on the same rows, clustered
    hh_m = pair_stats(da, db, 6, Wm)
    # Menagerie draw human pooled pairs
    hp_a, hp_b, hp_case = [], [], []
    for ci_, c in enumerate(me_cases):
        for x, y in combinations(c["raters"], 2):
            hp_a.append(int(x)); hp_b.append(int(y)); hp_case.append(ci_)
    hp_a, hp_b = np.array(hp_a), np.array(hp_b)
    hh_n14 = pair_stats(hp_a, hp_b, 14, Wn[:, hp_case])
    hh_n5 = pair_stats(COARSE[hp_a], COARSE[hp_b], 5, Wn[:, hp_case])
    out["grader"]["human_human_same_rows"] = {"mohler_r1_r2": strip(hh_m), "menagerie_14": strip(hh_n14),
                                              "menagerie_5": strip(hh_n5)}
    for m in MODELS:
        g_rows = [(ci_, x) for ci_, gs in enumerate(mo_marks[m]) for x in gs]
        cidx = np.array([r[0] for r in g_rows])
        gi = to_idx([r[1] for r in g_rows], 0, 5)
        r1 = da[cidx]; r2 = db[cidx]
        mean_i = to_idx([mo_cases[i]["human"] for i in cidx], 0, 5)
        Wg = Wm[:, cidx]
        s1 = pair_stats(r1, gi, 6, Wg)
        s2 = pair_stats(r2, gi, 6, Wg)
        sm = pair_stats(mean_i, gi, 6, Wg)
        # Menagerie: grader vs every rater pooled
        n_rows = [(ci_, x, r) for ci_, gs in enumerate(me_marks[m]) for x in gs for r in me_cases[ci_]["raters"]]
        nidx = np.array([r[0] for r in n_rows])
        ng = to_idx([r[1] for r in n_rows], 0, 13)
        nr = np.array([int(r[2]) for r in n_rows])
        Wng = Wn[:, nidx]
        g14 = pair_stats(nr, ng, 14, Wng)
        g5 = pair_stats(COARSE[nr], COARSE[ng], 5, Wng)
        out["grader"][m] = {"mohler_g_r1": strip(s1), "mohler_g_r2": strip(s2), "mohler_g_mean_rounded": strip(sm),
                            "menagerie_g_h_14": strip(g14), "menagerie_g_h_5": strip(g5)}

        def diff(x, y, stat):
            # x - y; x and y were bootstrapped on the same cluster weights row by row
            key = "_kB" if stat == "qwk" else "_aB"
            return ci(x[key] - y[key], x[stat]["est"] - y[stat]["est"])
        ords = {}
        for name, x, y in (("O1_g_r1_minus_r1_r2", s1, hh_m), ("O2_g_r2_minus_r1_r2", s2, hh_m),
                           ("O3_swing_g_r2_minus_g_r1", s2, s1), ("O4_menagerie14_g_h_minus_h_h", g14, hh_n14),
                           ("O5_menagerie5_g_h_minus_h_h", g5, hh_n5)):
            dq, dA = diff(x, y, "qwk"), diff(x, y, "ac2")
            ords[name] = {"qwk_diff": dq, "ac2_diff": dA, "rule": order_rule(dq, dA)}
        out["orderings"][m] = ords
    # ---- verdict
    lv = {k: level_rule(out["ceilings"][k]["ac2_minus_qwk"]) for k in
          ("mohler_r1_r2_1727", "mohler_r1_r2_draw300", "menagerie_pooled_5level", "menagerie_pooled_14level")}
    pp = out["ceilings"]["menagerie_per_pair_14level"]
    spread = "ROBUST" if pp["ac2"]["range"]["est"] >= SPREAD_FRAC * pp["qwk"]["range"]["est"] else "STATISTIC-DEPENDENT"
    flips = [f"{m}:{k}" for m in MODELS for k, v in out["orderings"][m].items() if v["rule"] == "FLIPS"]
    lost = [f"{m}:{k}" for m in MODELS for k, v in out["orderings"][m].items() if v["rule"] == "LOST"]
    gained = [f"{m}:{k}" for m in MODELS for k, v in out["orderings"][m].items() if v["rule"] == "GAINED"]
    dep = [k for k, v in lv.items() if v == "STATISTIC-DEPENDENT"]
    if not dep and not flips and spread == "ROBUST" and all(v == "ROBUST" for v in lv.values()):
        verdict = "CEILING-ROBUST"
    elif dep or flips or spread != "ROBUST":
        why = [f"level:{k}" for k in dep] + [f"flip:{f}" for f in flips] + ([] if spread == "ROBUST" else ["spread"])
        verdict = "CEILING-STATISTIC-DEPENDENT (" + ", ".join(why) + ")"
    else:
        verdict = "CEILING-UNRESOLVED"
    out["verdict"] = {"verdict": verdict, "levels": lv, "spread": spread, "orderings_flipped": flips,
                      "orderings_lost": lost, "orderings_gained": gained}
    return strip(out)


# ----------------------------------------------------------------------------- run

def run(root):
    rng = np.random.default_rng(20261006)
    mo_r, me_r = load_mohler_raters(), load_menagerie_raters()
    mo_cases, me_cases = load_cases(root, "mohler", mo_r), load_cases(root, "menagerie", me_r)
    mo_marks, me_marks = attach_marks(root, "mohler", mo_cases), attach_marks(root, "menagerie", me_cases)
    # reproduction checks of the paper's figures
    ids = sorted(mo_r)
    repro = {"mohler_1727_qwk": float(qwk_t(tables(np.array([int(mo_r[i][0]) for i in ids]),
                                                   np.array([int(mo_r[i][1]) for i in ids]), 6))),
             "mohler_rows": len(ids), "menagerie_items": len(me_r)}
    t1 = {}
    for corpus, cases, marks, rmax in (("mohler", mo_cases, mo_marks, 5), ("menagerie", me_cases, me_marks, 13)):
        W = cluster_weights([c["cluster"] for c in cases], REPS, rng)
        cres = {"strata": {"agree": int((strata(cases, corpus) == 0).sum()),
                           "disagree": int((strata(cases, corpus) == 1).sum())}}
        for m in MODELS:
            mres = {"P1": t1_p1(cases, marks[m], corpus, W, rmax, with_control=True, rng=rng),
                    "P2": t1_p2(cases, marks[m], W)}
            if corpus == "mohler":
                mres["P2"]["per_rater"] = t1_p2_per_rater(cases, marks[m])
            else:
                mres["P3"] = t1_p3(cases, marks[m], rmax, REPS, rng, W=W)
                mres["P1_sensitivity"] = {f"range<={s}": {k: v for k, v in t1_p1(cases, marks[m], corpus, W, rmax, span=s).items()
                                                          if k in ("D", "verdict", "n_agree", "n_disagree")}
                                          for s in (2, 4)}
            mres["missing_marks"] = int(sum(2 - len(g) for g in marks[m]))
            cres[m] = mres
        for P in ("P1", "P2") + (("P3",) if corpus == "menagerie" else ()):
            vs = {cres[m][P]["verdict"] for m in MODELS}
            cres[f"{P}_across_models"] = vs.pop() if len(vs) == 1 else "MIXED (" + ", ".join(
                f"{MODELS[m]}: {cres[m][P]['verdict']}" for m in MODELS) + ")"
        t1[corpus] = cres
    # QWK by stratum (reported): grader vs every single rater, pooled rows
    for corpus, cases, marks, q, lo, hi in (("mohler", mo_cases, mo_marks, 6, 0, 5), ("menagerie", me_cases, me_marks, 14, 0, 13)):
        st = strata(cases, corpus)
        W = cluster_weights([c["cluster"] for c in cases], REPS, rng)
        for m in MODELS:
            byst = {}
            for s, name in ((0, "agree"), (1, "disagree")):
                rows = [(i, x, r) for i, gs in enumerate(marks[m]) if st[i] == s for x in gs for r in cases[i]["raters"]]
                idx = np.array([r[0] for r in rows])
                ps = pair_stats(np.array([int(r[2]) for r in rows]), to_idx([r[1] for r in rows], lo, hi), q, W[:, idx])
                byst[name] = {"qwk": ps["qwk"], "ac2": ps["ac2"], "rows": ps["n"],
                              "sd_reference": float(np.std([r[2] for r in rows]))}
            t1[corpus][m]["by_stratum_grader_vs_single_rater"] = byst
    # swing
    swing = {}
    t2 = run_t2(root, mo_r, me_r, mo_cases, me_cases, mo_marks, me_marks, rng)
    for m in MODELS:
        s = t2["orderings"][m]["O3_swing_g_r2_minus_g_r1"]["qwk_diff"]
        exceeds = s["lo"] > SWING_BAR or s["hi"] < -SWING_BAR
        swing[m] = {"swing_qwk": s, "swing_ac2": t2["orderings"][m]["O3_swing_g_r2_minus_g_r1"]["ac2_diff"],
                    "rule": "SWING-EXCEEDS-INTERVENTIONS" if exceeds else "SWING-NOT-RESOLVED-ABOVE-0.05"}
    t1["reference_swing_mohler"] = swing
    cells = [(c, m) for c in ("mohler", "menagerie") for m in MODELS]
    better = sum(t1[c][m]["P1"]["verdict"] == "GRADER-BETTER-WHERE-HUMANS-AGREE" for c, m in cells)
    subst = sum(t1[c][m]["P2"]["verdict"] == "SHARE-SUBSTANTIAL" for c, m in cells)
    minor = sum(t1[c][m]["P2"]["verdict"] == "SHARE-MINOR" for c, m in cells)
    sw = sum(v["rule"] == "SWING-EXCEEDS-INTERVENTIONS" for v in swing.values())
    if better >= 4 and subst >= 4 and sw >= 2:
        ov = "BLUNT-INSTRUMENT-SUPPORTED"
    elif better <= 2 or minor >= 4 or sw == 0:
        ov = "BLUNT-INSTRUMENT-WEAKENED"
    else:
        ov = "BLUNT-INSTRUMENT-PARTLY"
    t1["overall"] = {"verdict": ov, "P1_better_cells": better, "P2_substantial_cells": subst,
                     "P2_minor_cells": minor, "swing_exceeds_models": sw}
    return {"reproduction": repro, "T1": t1, "T2": t2}


def posthoc(root):
    """ADDED AFTER THE RUN (2026-10-06), reported only, no verdict. Two readings the results raised:
    (1) what AC2 and QWK give a grader that ignores the work (every item the pooled modal human mark, or
    the pooled median), on the same rows as the real comparisons, since AC2 put GPT-4.1-mini at 0.745 on
    Menagerie where its QWK is 0.058; (2) the two Mohler raters' means, since every grader sits much closer
    to rater 2 (P2 per rater), which breaks P2's independence assumption in a known direction."""
    mo_r, me_r = load_mohler_raters(), load_menagerie_raters()
    mo_cases, me_cases = load_cases(root, "mohler", mo_r), load_cases(root, "menagerie", me_r)
    out = {"note": posthoc.__doc__}
    ids = sorted(mo_r)
    r1 = np.array([mo_r[i][0] for i in ids]); r2 = np.array([mo_r[i][1] for i in ids])
    d1 = np.array([c["raters"][0] for c in mo_cases]); d2 = np.array([c["raters"][1] for c in mo_cases])
    out["mohler_rater_means"] = {"full_1727": {"r1": float(r1.mean()), "r2": float(r2.mean()),
                                               "r1_minus_r2": float((r1 - r2).mean())},
                                 "draw_300": {"r1": float(d1.mean()), "r2": float(d2.mean()),
                                              "r1_minus_r2": float((d1 - d2).mean())}}
    cons = {}
    allm = np.concatenate([r1, r2]).astype(int)
    for name, val in (("mode", int(np.bincount(allm).argmax())), ("median", int(np.median(allm)))):
        for lab, hum in (("full_1727_vs_r1", r1), ("full_1727_vs_r2", r2), ("draw_300_vs_r1", d1), ("draw_300_vs_r2", d2)):
            T = tables(hum.astype(int), np.full(len(hum), val), 6)
            cons[f"mohler_constant_{name}_{val}_{lab}"] = {"qwk": float(qwk_t(T)), "ac2": float(ac2_t(T)[0])}
    men = np.array([v for c in me_cases for v in c["raters"]]).astype(int)
    for name, val in (("mode", int(np.bincount(men).argmax())), ("median", int(np.median(men)))):
        for lvl, q, mp in (("14", 14, lambda x: x), ("5", 5, lambda x: COARSE[x])):
            T = tables(mp(men), mp(np.full(len(men), val)), q)
            cons[f"menagerie_constant_{name}_{MEN_SCALE[val]}_vs_every_rater_{lvl}level"] = {
                "qwk": float(qwk_t(T)), "ac2": float(ac2_t(T)[0])}
    out["constant_grader"] = cons
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--floor", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--posthoc", action="store_true")
    ap.add_argument("--dump-dir")
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    if a.selftest:
        r = selftest()
        (OUT / "selftest.json").write_text(json.dumps(r, indent=1) + "\n")
        print(json.dumps(r, indent=1))
        if not r["passed"]:
            raise SystemExit("SELFTEST FAILED")
        return
    root = dump_root(a.dump_dir)
    if a.posthoc:
        r = posthoc(root)
        (OUT / "posthoc.json").write_text(json.dumps(r, indent=1) + "\n")
        print(json.dumps(r, indent=1))
        return
    if a.verify or a.floor or a.run:
        v = verify(root)
        print(f"dumps verified against per-case-dumps.sha256: {sum(v.values())}/{len(v)}")
    if a.floor:
        r = run_floor(root)
        (OUT / "floor.json").write_text(json.dumps(r, indent=1) + "\n")
        print(json.dumps(r["criteria"], indent=1))
    if a.run:
        r = run(root)
        (OUT / "results.json").write_text(json.dumps(r, indent=1) + "\n")
        print(json.dumps({"T1": {k: (v if k in ("overall",) else {kk: vv for kk, vv in v.items() if "across" in kk})
                                 for k, v in r["T1"].items() if k != "reference_swing_mohler"},
                          "swing": {m: v["rule"] for m, v in r["T1"]["reference_swing_mohler"].items()},
                          "T2": r["T2"]["verdict"]}, indent=1))


if __name__ == "__main__":
    main()
