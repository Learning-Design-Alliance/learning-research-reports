"""
Is the attainment-label effect on identical work stable across item length and score scale?
Paper VI placeholder 3 (2026-10-05).

WHAT WAS ASKED. Paper VI (research/article/attainment-bias-in-llm-grading.md, release
ai-grader-reliability-2026 1.0.0), section 5.3, placeholder 3: "What remains open is whether the gap is
stable across items of different length and scale, which this draw does not vary." The Q2 study
(studies/measurement/grader-attainment-prior/) measured the label's effect on identical work with a
swapped-label arm on ONE corpus, JorGPT (short open answers, 0-10): high label minus low label on the
same answer is +0.37 / +0.38 / +0.52 / +0.75 points on Gemini 3.5 Flash Lite, GPT-4.1-mini, GPT-5-mini
and Qwen3-235B-A22B-2507. This study asks whether that effect, put on a common scale, changes with the
length of the work or the scale it is marked on.

THE CELLS (corpora already registered in data/data-sources.json):
  jorgpt10   JorGPT, 0-10, the Q2 draw (300 cases, 33 learners, 150 per attainment tail). The Q2
             per-case dumps ARE this cell: no new calls. high/low = trueLabel/swappedLabel by tail.
  jorgpt5    the SAME 300 answers, the SAME label pairs rescaled by 5/10, graded out of 5. Identical
             items and label positions: the only thing that moves against jorgpt10 is the scale (and
             the run date). New calls.
  mohler     Mohler ASAG (mohler-asag), 0-5, two raters averaged; 300 answers stratified on the grade
             (seed 7), 62 questions; median 81 characters against JorGPT's 486. New calls.
  menagerie  Menagerie CS1 Java programs (menagerie-grades, original source trees from the deposit's
             "Anonymised Assignments" archives), 60 submissions drawn as `menagerie-grade` draws them,
             x 4 rubric dimensions, the deposit's six-band rubric, graded out of 13 (A++..F). Source
             truncated at 60,000 characters (55 of 60 hit it): ~120x JorGPT's length. New calls.
  The label pairs in EVERY cell are the Q2 draw's 150 (high, low) pairs of held-out attainment,
  rescaled by max/10, in the same sentence ("Current attainment for this learner across this course:
  x/max, from n prior graded responses."). jorgpt keeps each case's own pair; Mohler case k takes pair
  k mod 150; Menagerie submission j takes pair j for all four of its dimensions (a submission plays the
  learner). The label gap is 0.372 of the range in the JorGPT and Mohler cells and 0.361 in Menagerie
  (pairs 0-59 only); the pass-through reading below divides it out.

THE ESTIMAND. Per case S_i = score | high label - score | low label (signed: positive = a high label
raises the mark). Per cell:
  s      = mean S_i / range                  PRIMARY: fraction of the score range
  s_sd   = mean S_i / SD(human reference)    secondary: SD of the cell's own human scores
           (JorGPT teacher grade; Mohler rater mean; Menagerie rater mean, 0-13), fixed on the draw
  pt     = mean S_i / mean label gap          reported only: the share of the label gap passed through
UNIT. Labels are assigned to the case, and cases cluster by learner (JorGPT), question (Mohler: no
learner id) and submission (Menagerie). Every interval is a cluster bootstrap (JorGPT: learners resampled
within tail, as Q2), 4,000 resamples, percentile. Cells sharing cases (jorgpt5 vs jorgpt10) are
resampled jointly; different corpora independently.

CONTRASTS (all signed, on s; the same contrasts on s_sd are reported as the SD reading):
  C1 LEN-JORGPT    within-tail slope of s on log10(characters), adjusted for the human score level
                   (one indicator per tenth of the range), read as the predicted difference between the
                   median lengths of the long and short thirds (cut within tail, because the high tail
                   writes longer answers: median 680 vs 293 chars). On jorgpt10 (the Q2 dumps, all four
                   models); jorgpt5 reported as replication; the unadjusted thirds difference reported.
  C2 LEN-MOHLER    the same within Mohler (one stratum).
  C3 SCALE         s(jorgpt5) - s(jorgpt10): same answers, same label positions, 0-5 vs 0-10.
  C4 SHORT-CORPUS  s(mohler) - s(jorgpt5): same scale, shorter answers, different items.
  C5 LONG-CORPUS   s(menagerie) - s(jorgpt10): whole programs vs short answers (0-13 vs 0-10;
                   also a different task and a rubric dimension rather than a model answer).

PRE-REGISTERED CLASSIFICATION of each contrast (tolerance delta = 0.02 of the score range, i.e. 0.2
points on 0-10, 0.1 on 0-5, 0.26 on 0-13; the Q2 effects are 0.037-0.075 of the range, so delta is
about a third to a half of the effect. SD reading: delta_sd = 0.07 SD, the same 0.2 points on JorGPT):
  EQUIVALENT  the 90% interval lies inside +/-delta (TOST, alpha 0.05)
  LARGER      not EQUIVALENT and the 99% interval lies above 0  (99%: Bonferroni over five contrasts)
  SMALLER     not EQUIVALENT and the 99% interval lies below 0
  UNRESOLVED  otherwise
DIRECTION of each cell: POSITIVE if s's 95% interval is above 0, NEGATIVE if below, else UNRESOLVED.

PRE-REGISTERED VERDICT per model (verdict labels joined with " + "):
  STABLE                 every ANSWERABLE contrast is EQUIVALENT (see the floor rule below)
  GROWS-WITH-LENGTH      some length contrast says the effect grows with length, none says it shrinks.
                         Length contrasts: C1, C2 (within corpus, tagged [within]) and C4, C5 (across
                         corpora, tagged [across-corpora: confounded with task]); C4 SMALLER and C5
                         LARGER point to growth. The tag names which kind carried it.
  SHRINKS-WITH-LENGTH    the mirror image.
  LENGTH-INCONSISTENT    resolved length contrasts point both ways.
  SCALE-DEPENDENT        C3 LARGER (-> "larger on 0-5") or SMALLER (-> "smaller on 0-5").
  UNDERPOWERED           none of the above and not STABLE: no difference resolved, but some answerable
                         contrast did not reach equivalence.
  Across models: the shared verdict, else MIXED-ACROSS-MODELS with each, over the models that have
  every cell. GPT-5-mini is not re-run (its reasoning tokens cost ~10x the others); its Q2 JorGPT
  cell gives C1 only and is reported beside the verdict, not in it.
  Separately: DIRECTION-STABLE if every cell on every model is POSITIVE; DIRECTION-REVERSES if any cell
  is NEGATIVE; else DIRECTION-UNRESOLVED naming the cells.
What each verdict would mean for the paper was written before the run (README).

THE FLOOR (`--floor`), before any real number. Synthetic graders on the real draws (real lengths, real
clusters and tails, real label pairs, real human scores and ranges): latent = human + item effect
(sd 0.10 of range); each arm's mark = clip(round(latent + b_i * (label - range/2) + e)), e ~ N(0,
sigma * range); b_i = k * (1 + cluster slope, sd 0.3), k set so the cell's mean S equals the planted
s * range. sigma = 0.05 of range gives a per-case S sd of about 0.06 of range, the spread of the Q2
dumps' per-case S (0.58-0.72 points on 0-10; read from the pooled Q2 dumps, which were already
analysed in pooled form, never by length). Integer rounding everywhere, the pessimistic case (three of
the four models return integers 78-99% of the time). 200 replicates per world, 2,000 bootstrap resamples
each:
  CONST         s = 0.05 everywhere                    -> no LARGER/SMALLER anywhere in >= 90%
  CONST-NOISY   CONST, sigma x1.5, cluster sd 0.5       -> the same
  GROWS         s = 0.05 (chars/500)^0.2 (Mohler 0.035, JorGPT ~0.05, Menagerie 0.13)
                                                        -> GROWS-WITH-LENGTH >= 80%, SHRINKS <= 5%
  SHRINKS       exponent -0.2                           -> SHRINKS-WITH-LENGTH >= 80%, GROWS <= 5%
  SCALE         s = 0.09 on the 0-5 cells, 0.05 elsewhere (twice the tolerance), no length term
                                                        -> SCALE-DEPENDENT (larger on 0-5) >= 80%,
                                                           any length verdict <= 10%
FLOOR RULE FOR "ANSWERABLE" (fixed before any real number): a contrast is answerable if it returns
EQUIVALENT in >= 50% of CONST replicates. A contrast that cannot reach equivalence under a constant
effect can only ever report a difference or UNRESOLVED, and STABLE is then stated over the answerable
contrasts only, naming the others. A grader written and scored by this session is a smoke check of the
instrument's logic on the worlds it was told about, not a validation, and is reported as one.

FLOOR RECORD (all before the pre-registration commit and before any model call of this study):
  rev 0  C1/C2 as unadjusted long-minus-short thirds; SCALE world at 0.075 vs 0.05; 400 bootstrap
         resamples per replicate. FAILED: CONST returned a difference in 10.5% (C1 LARGER 3.5%:
         compression at the ends of the scale, since longer answers score higher), SCALE detected 57%.
  rev 1  C1/C2 as the level-adjusted slope (quadratic in h, then fifths, then tenths of the range).
         CONST still 10.5-11%: every contrast over-rejected ~3x, which was the floor's own 400
         resamples putting the 0.5th percentile at the 2nd order statistic, not the instrument.
  rev 2  (this) 2,000 resamples per floor replicate; the SCALE world planted at twice the tolerance
         (0.09 vs 0.05), the smallest scale difference the verdict is meant to call. PASSED: CONST
         93.5% and CONST-NOISY 90.5% no difference; GROWS 100%, SHRINKS 95.5%, SCALE 93%; SCALE
         falsely called a length trend 4%. ANSWERABLE (equivalence reachable under CONST in >= 50%):
         C3 (62%) and C5 (68%) only; C1 41%, C4 46%, C2 2%. The planted length trend is found through
         the cross-corpus contrast C5 (100%), within corpus only 13.5% of the time: within JorGPT and
         Mohler the instrument cannot see a length trend of this size, and a GROWS/SHRINKS verdict
         will rest on corpora that differ in task as well as length.

FAILURES THAT SHAPED THIS. (1) The high tail writes 2.3x longer answers than the low tail, so a
pooled length split in JorGPT would carry the tail difference the Q2 study found (L 0.42 vs 0.32 on
Gemini): the slope is estimated within tail. Longer answers also score higher, so it is adjusted
for the score level (floor rev 0). (2) A fixed label on Mohler/Menagerie would differ in distribution
from JorGPT's per-learner labels, so the Q2 pairs themselves are reused everywhere. (3) Five contrasts
at 95% would give about one false difference in five null runs: differences need the 99% interval.

DATA. This script reads no corpus. It reads the harness dumps (`--mode label-stability` and the Q2
`--mode attainment-swap` dumps), which hold ids, character counts, human scores and the model's marks;
the dumps stay in the session scratchpad and only out/*.json aggregates are committed.

RESULT (2026-10-05; README for the tables). MIXED-ACROSS-MODELS, DIRECTION-STABLE (13/13 cells
positive). Scale on identical answers: EQUIVALENT on Gemini (-0.006) and GPT-4.1-mini (+0.000), SMALLER
on 0-5 on Qwen (-0.016, its 0-10 cell from the earlier Q2 run). Programs vs short answers: Gemini
SMALLER (0.015 vs 0.037), GPT-4.1-mini LARGER (0.105 vs 0.038), Qwen LARGER (0.179 vs 0.076); tagged
across-corpora, confounded with task. No within-corpus length trend resolved. The per-level reading
(`post_hoc_level`) was added after the run and is reported only.

Usage:
  python3 analyse.py --floor [--dump-dir <dir>]
  python3 analyse.py --run [--dump-dir <dir>]

  <dir> holds the two dump folders, grader-vi/ (swap-<model>.json) and grader-label-stability/
  (draw-<corpus>.json, <corpus>-<model>.json). It is --dump-dir if given, else $GRADER_DUMP_DIR, else
  shared.paths.scratch_root() (LDA_SCRATCH_DIR, or the registry's default scratch root). Corrected
  2026-10-06 (Paper VI corrections-1): this used to be a hard-coded session-scratchpad literal, which
  the reproduction (research/readiness/ai-grader-reliability-2026/reproduction.md, gap 3) could only
  get past by editing the source. No computation changed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
ROOT = HERE.parents[2]
DUMP_ENV = "GRADER_DUMP_DIR"
Q2: Path | None = None      # <dump dir>/grader-vi, set by set_dump_dir()
DUMPS: Path | None = None   # <dump dir>/grader-label-stability


def set_dump_dir(override: str | None = None) -> Path:
    """Point Q2 and DUMPS at the folder holding the per-case harness dumps (never committed)."""
    global Q2, DUMPS
    import os
    raw = override or os.environ.get(DUMP_ENV)
    if raw:
        root = Path(raw).expanduser()
    else:
        sys.path.insert(0, str(ROOT))
        from shared.paths import scratch_root
        root = scratch_root()
    Q2, DUMPS = root / "grader-vi", root / "grader-label-stability"
    if not DUMPS.is_dir():
        raise SystemExit(
            f"per-case dumps not found under {root}.\n"
            f"  Pass --dump-dir <dir> or set {DUMP_ENV} (or LDA_SCRATCH_DIR) to the directory holding\n"
            f"  grader-label-stability/ (and, for --run, grader-vi/). The dumps are not committed.")
    return root
REPS = 4000
FLOOR_REPS = 200
FLOOR_BOOT = 2000  # 400 put the 0.5th percentile at the 2nd order statistic and under-covered the 99% interval
DELTA = 0.02
DELTA_SD = 0.07
CONTRASTS = ["C1", "C2", "C3", "C4", "C5"]
MODELS = {  # tag -> (Q2 dump tag, label)
    "gemini": ("gemini", "Gemini 3.5 Flash Lite"),
    "gpt41mini": ("gpt41mini", "GPT-4.1-mini"),
    "gpt5mini": ("gpt5mini", "GPT-5-mini"),
    "qwen": ("qwen", "Qwen3-235B-A22B-2507"),
}


# ---------------------------------------------------------------- cells

class Cell:
    """One corpus x scale x model: per-case S, cluster ids, strata, lengths."""

    def __init__(self, name, rows, max_, sd_human):
        self.name = name
        self.max = max_
        self.sd = sd_human
        self.ids = np.array([r["id"] for r in rows])
        self.S = np.array([r["high"] - r["low"] for r in rows], float)
        self.gap = np.array([r["labelHigh"] - r["labelLow"] for r in rows], float)
        self.chars = np.array([r["chars"] for r in rows], float)
        self.h = np.array([r["human"] for r in rows], float) / max_   # human level, fraction of range
        self.tail = np.array([r.get("tail") or "all" for r in rows])
        cl = [f'{r.get("tail") or "all"}|{r["cluster"]}' for r in rows]
        self.cluster_names = sorted(set(cl))
        idx = {c: i for i, c in enumerate(self.cluster_names)}
        self.cl = np.array([idx[c] for c in cl])
        self.cl_stratum = np.array([c.split("|")[0] for c in self.cluster_names])

    def subset(self, keep):
        new = object.__new__(Cell)
        new.__dict__.update(self.__dict__)
        for k in ("ids", "S", "gap", "chars", "h", "tail", "cl"):
            setattr(new, k, getattr(self, k)[keep])
        return new


def boot_weights(cell, B, rng):
    """Cluster multinomial weights, stratified by tail where the cell has tails. B x n_clusters."""
    C = len(cell.cluster_names)
    W = np.zeros((B, C))
    for st in np.unique(cell.cl_stratum):
        cols = np.where(cell.cl_stratum == st)[0]
        draws = rng.integers(0, len(cols), size=(B, len(cols)))
        for j in range(len(cols)):
            np.add.at(W, (np.arange(B), cols[draws[:, j]]), 1)
    return W


def wmean(cell, values, mask, W):
    """Bootstrap means of values[mask] with cluster weights W (B x C); also the point estimate."""
    C = len(cell.cluster_names)
    sums = np.bincount(cell.cl[mask], weights=values[mask], minlength=C)
    cnts = np.bincount(cell.cl[mask], minlength=C).astype(float)
    point = sums.sum() / cnts.sum()
    with np.errstate(invalid="ignore", divide="ignore"):
        bs = (W @ sums) / (W @ cnts)
    return point, bs


def s_of(cell, W, unit="range"):
    v = cell.S / (cell.max if unit == "range" else cell.sd)
    return wmean(cell, v, np.ones(len(v), bool), W)


def length_contrast(cell, W, unit="range"):
    """PRIMARY C1/C2: the within-tail slope of s on log10(chars), adjusted for the human score level.

    Regression s_i ~ tail + log10(chars) + level (h = human score / range, one indicator per tenth of the range), cluster-weighted, so the
    slope is estimated within tail and net of the score level. Without the level terms, compression at
    the ends of the scale (a near-full-marks answer cannot rise further) shows up as a length effect,
    because longer answers score higher: the first floor returned a false C1 difference in 3.5% of
    constant-effect worlds for exactly that reason. Reported as the predicted difference in s between
    the median lengths of the long and short thirds (cut within tail), so it reads like a thirds contrast.
    """
    v = cell.S / (cell.max if unit == "range" else cell.sd)
    tails = np.unique(cell.tail)
    x = np.log10(cell.chars)
    bins = np.round(cell.h * 10).astype(int)                   # human level in tenths of the range
    levels = [(bins == k).astype(float) for k in sorted(set(bins))[1:] if (bins == k).sum() >= 5]
    cols = [np.ones(len(v))] + [(cell.tail == t).astype(float) for t in tails[1:]] + [x] + levels
    X = np.column_stack(cols)
    j = 1 + len(tails) - 1                       # index of the log10(chars) column
    span = []
    for t in tails:
        m = cell.tail == t
        lo_cut, hi_cut = np.percentile(cell.chars[m], [100 / 3, 200 / 3])
        span.append(np.log10(np.median(cell.chars[m & (cell.chars > hi_cut)])) -
                    np.log10(np.median(cell.chars[m & (cell.chars <= lo_cut)])))
    span = float(np.mean(span))
    beta = np.linalg.lstsq(X, v, rcond=None)[0][j]
    w = W[:, cell.cl]                                           # B x n case weights
    XtWX = np.einsum("bi,ij,ik->bjk", w, X, X)
    XtWy = np.einsum("bi,ij,i->bj", w, X, v)
    sol = np.linalg.solve(XtWX + 1e-9 * np.eye(X.shape[1]), XtWy[..., None])[..., 0]
    return float(beta * span), sol[:, j] * span


def thirds_contrast(cell, W, unit="range"):
    """Long third minus short third, cut within each tail, averaged over tails."""
    v = cell.S / (cell.max if unit == "range" else cell.sd)
    pts, bss = [], []
    for t in np.unique(cell.tail):
        m = cell.tail == t
        lo_cut, hi_cut = np.percentile(cell.chars[m], [100 / 3, 200 / 3])
        p_long, b_long = wmean(cell, v, m & (cell.chars > hi_cut), W)
        p_short, b_short = wmean(cell, v, m & (cell.chars <= lo_cut), W)
        pts.append(p_long - p_short)
        bss.append(b_long - b_short)
    return float(np.mean(pts)), np.mean(bss, axis=0)


def classify(point, bs, delta):
    bs = bs[np.isfinite(bs)]
    lo90, hi90 = np.percentile(bs, [5, 95])
    lo99, hi99 = np.percentile(bs, [0.5, 99.5])
    lo95, hi95 = np.percentile(bs, [2.5, 97.5])
    if lo90 > -delta and hi90 < delta:
        v = "EQUIVALENT"
    elif lo99 > 0:
        v = "LARGER"
    elif hi99 < 0:
        v = "SMALLER"
    else:
        v = "UNRESOLVED"
    return {"point": round(float(point), 4), "ci95": [round(float(lo95), 4), round(float(hi95), 4)],
            "ci90": [round(float(lo90), 4), round(float(hi90), 4)],
            "ci99": [round(float(lo99), 4), round(float(hi99), 4)], "class": v}


def direction(point, bs):
    lo, hi = np.percentile(bs[np.isfinite(bs)], [2.5, 97.5])
    return {"point": round(float(point), 4), "ci95": [round(float(lo), 4), round(float(hi), 4)],
            "direction": "POSITIVE" if lo > 0 else "NEGATIVE" if hi < 0 else "UNRESOLVED"}


def contrasts(cells, B, rng, unit="range"):
    """cells: dict jorgpt10, jorgpt5, mohler, menagerie (any may be absent).

    C1/C5 use all of jorgpt10. C3 pairs jorgpt5 with jorgpt10 on the cases complete in both, under ONE
    set of learner weights (the same learners resampled for both scales). Returns (contrasts, cells),
    each value a (point, bootstrap array) pair.
    """
    out, cw = {}, {}
    j10, j5, mo, me = (cells.get(k) for k in ("jorgpt10", "jorgpt5", "mohler", "menagerie"))
    if j10 is not None:
        Wj = boot_weights(j10, B, rng)
        out["C1"] = length_contrast(j10, Wj, unit)
        out["C1_thirds_unadjusted"] = thirds_contrast(j10, Wj, unit)
        cw["jorgpt10"] = s_of(j10, Wj, unit)
    if j5 is not None:
        common = np.intersect1d(j5.ids, j10.ids)
        a = j5.subset(np.isin(j5.ids, common))
        b = j10.subset(np.isin(j10.ids, common))
        assert a.cluster_names == b.cluster_names
        order_a, order_b = np.argsort(a.ids), np.argsort(b.ids)
        assert (a.ids[order_a] == b.ids[order_b]).all()
        Wp = boot_weights(a, B, rng)
        sa, sb = s_of(a, Wp, unit), s_of(b, Wp, unit)
        out["C3"] = (sa[0] - sb[0], sa[1] - sb[1])
        out["C1_rep_jorgpt5"] = length_contrast(a, Wp, unit)
        cw["jorgpt5"] = s_of(j5, boot_weights(j5, B, rng), unit)
    if mo is not None:
        Wm = boot_weights(mo, B, rng)
        out["C2"] = length_contrast(mo, Wm, unit)
        out["C2_thirds_unadjusted"] = thirds_contrast(mo, Wm, unit)
        cw["mohler"] = s_of(mo, Wm, unit)
        if j5 is not None:
            out["C4"] = (cw["mohler"][0] - cw["jorgpt5"][0], cw["mohler"][1] - cw["jorgpt5"][1])
    if me is not None:
        cw["menagerie"] = s_of(me, boot_weights(me, B, rng), unit)
        if j10 is not None:
            out["C5"] = (cw["menagerie"][0] - cw["jorgpt10"][0], cw["menagerie"][1] - cw["jorgpt10"][1])
    return out, cw


def model_verdict(cls, answerable):
    """cls: contrast -> class string. Returns the verdict string."""
    labels = []
    grows, shrinks = [], []
    for c, up in (("C1", "LARGER"), ("C2", "LARGER"), ("C5", "LARGER"), ("C4", "SMALLER")):
        k = cls.get(c)
        if k is None or k in ("EQUIVALENT", "UNRESOLVED"):
            continue
        tag = "within" if c in ("C1", "C2") else "across-corpora: confounded with task"
        (grows if k == up else shrinks).append((c, tag))
    if grows and shrinks:
        labels.append("LENGTH-INCONSISTENT")
    elif grows or shrinks:
        tags = sorted({t for _, t in (grows or shrinks)})
        labels.append(("GROWS-WITH-LENGTH" if grows else "SHRINKS-WITH-LENGTH") + "[" + "; ".join(tags) + "]")
    if cls.get("C3") == "LARGER":
        labels.append("SCALE-DEPENDENT (larger on 0-5)")
    elif cls.get("C3") == "SMALLER":
        labels.append("SCALE-DEPENDENT (smaller on 0-5)")
    if labels:
        return " + ".join(labels)
    ans = [c for c in CONTRASTS if c in cls and c in answerable]
    if ans and all(cls[c] == "EQUIVALENT" for c in ans):
        rest = [c for c in CONTRASTS if c in cls and c not in answerable]
        return "STABLE" + (f" (over {', '.join(ans)}; not answerable: {', '.join(rest)})" if rest else "")
    return "UNDERPOWERED"


# ---------------------------------------------------------------- floor

def load_draw(name):
    """The dry-run draw. JorGPT's human grade is 0-10 whatever scale the cell grades on; it is put on
    the cell's own scale here, so a jorgpt5 world and the jorgpt5 SD are on 0-5."""
    d = json.load(open(DUMPS / f"draw-{name}.json"))
    rows = d["rows"]
    if name.startswith("jorgpt") and d["max"] != 10:
        rows = [{**r, "human": r["human"] * d["max"] / 10} for r in rows]
    return rows, d["max"]


def synth_cell(name, rows, max_, s_fn, sigma, cl_sd, rng):
    """A synthetic grader on a real draw. s_fn(chars, max) -> planted s per case."""
    rows = [dict(r) for r in rows]
    human = np.array([r["human"] for r in rows], float)
    chars = np.array([r["chars"] for r in rows], float)
    hi = np.array([r["labelHigh"] for r in rows], float)
    lo = np.array([r["labelLow"] for r in rows], float)
    clusters = sorted(set(r["cluster"] for r in rows))
    ci = {c: i for i, c in enumerate(clusters)}
    slope_noise = rng.normal(0, cl_sd, len(clusters))[[ci[r["cluster"]] for r in rows]]
    latent = human + rng.normal(0, 0.10 * max_, len(rows))
    s = s_fn(chars, max_)
    k = s * max_ / np.mean(hi - lo)          # pass-through giving mean S = s * max
    b = k * (1 + slope_noise)
    mid = max_ / 2
    sh = np.clip(np.round(latent + b * (hi - mid) + rng.normal(0, sigma * max_, len(rows))), 0, max_)
    sl = np.clip(np.round(latent + b * (lo - mid) + rng.normal(0, sigma * max_, len(rows))), 0, max_)
    for r, a, z in zip(rows, sh, sl):
        r["high"], r["low"] = float(a), float(z)
    return Cell(name, rows, max_, float(np.std(human)))


WORLDS = {
    "CONST": dict(s=lambda c, m: np.full(len(c), 0.05), sigma=0.05, cl=0.3),
    "CONST-NOISY": dict(s=lambda c, m: np.full(len(c), 0.05), sigma=0.075, cl=0.5),
    "GROWS": dict(s=lambda c, m: 0.05 * (c / 500) ** 0.2, sigma=0.05, cl=0.3),
    "SHRINKS": dict(s=lambda c, m: 0.05 * (c / 500) ** -0.2, sigma=0.05, cl=0.3),
    "SCALE": dict(s=lambda c, m: np.full(len(c), 0.09 if m == 5 else 0.05), sigma=0.05, cl=0.3),
}


def run_floor():
    draws = {n: load_draw(n) for n in ("jorgpt10", "jorgpt5", "mohler", "menagerie")}
    rng = np.random.default_rng(20261005)
    res = {}
    equiv_const = {c: 0 for c in CONTRASTS}
    for wname, w in WORLDS.items():
        tallies = {"verdicts": {}, "classes": {c: {} for c in CONTRASTS}}
        for rep in range(FLOOR_REPS):
            cells = {n: synth_cell(n, rows, m, w["s"], w["sigma"], w["cl"], rng) for n, (rows, m) in draws.items()}
            # jorgpt5 shares cases and clusters with jorgpt10, so it is paired in the bootstrap.
            raw, _ = contrasts(cells, FLOOR_BOOT, rng)
            cls = {c: classify(*raw[c], DELTA)["class"] for c in CONTRASTS}
            for c in CONTRASTS:
                tallies["classes"][c][cls[c]] = tallies["classes"][c].get(cls[c], 0) + 1
            if wname == "CONST":
                for c in CONTRASTS:
                    equiv_const[c] += cls[c] == "EQUIVALENT"
            v = model_verdict(cls, set(CONTRASTS))
            tallies["verdicts"][v] = tallies["verdicts"].get(v, 0) + 1
        res[wname] = tallies
        print(wname, json.dumps(tallies["classes"]), file=sys.stderr)
    answerable = sorted(c for c in CONTRASTS if equiv_const[c] / FLOOR_REPS >= 0.5)
    # Re-score the verdicts with the answerable set now fixed (only STABLE/UNDERPOWERED depend on it).
    n = FLOOR_REPS

    def share(world, pred):
        return sum(k for v, k in res[world]["verdicts"].items() if pred(v)) / n

    any_diff = lambda v: any(t in v for t in ("GROWS", "SHRINKS", "SCALE-DEP", "INCONSISTENT"))
    checks = {
        "CONST: no difference in >= 90%": share("CONST", lambda v: not any_diff(v)) >= 0.90,
        "CONST-NOISY: no difference in >= 90%": share("CONST-NOISY", lambda v: not any_diff(v)) >= 0.90,
        "GROWS: GROWS-WITH-LENGTH >= 80%": share("GROWS", lambda v: "GROWS-WITH-LENGTH" in v) >= 0.80,
        "GROWS: SHRINKS <= 5%": share("GROWS", lambda v: "SHRINKS" in v) <= 0.05,
        "SHRINKS: SHRINKS-WITH-LENGTH >= 80%": share("SHRINKS", lambda v: "SHRINKS-WITH-LENGTH" in v) >= 0.80,
        "SHRINKS: GROWS <= 5%": share("SHRINKS", lambda v: "GROWS" in v) <= 0.05,
        "SCALE: SCALE-DEPENDENT (larger on 0-5) >= 80%": share("SCALE", lambda v: "larger on 0-5" in v) >= 0.80,
        "SCALE: any length verdict <= 10%": share("SCALE", lambda v: "LENGTH" in v) <= 0.10,
    }
    shares = {
        "CONST no-difference": share("CONST", lambda v: not any_diff(v)),
        "CONST-NOISY no-difference": share("CONST-NOISY", lambda v: not any_diff(v)),
        "GROWS detected": share("GROWS", lambda v: "GROWS-WITH-LENGTH" in v),
        "GROWS detected [within]": share("GROWS", lambda v: "GROWS-WITH-LENGTH" in v and "within" in v),
        "SHRINKS detected": share("SHRINKS", lambda v: "SHRINKS-WITH-LENGTH" in v),
        "SCALE detected": share("SCALE", lambda v: "larger on 0-5" in v),
        "SCALE false length": share("SCALE", lambda v: "LENGTH" in v),
    }
    out = {
        "what": "detection floor for the label-stability instrument: synthetic graders on the real draws",
        "smoke_check": "written and scored by one session; checks the instrument's logic on worlds it was told about",
        "reps": FLOOR_REPS, "boot": FLOOR_BOOT, "delta": DELTA,
        "worlds": {k: {"sigma": v["sigma"], "cluster_sd": v["cl"]} for k, v in WORLDS.items()},
        "answerable": answerable,
        "const_equivalence_rate": {c: equiv_const[c] / n for c in CONTRASTS},
        "shares": shares, "checks": checks, "passed": all(checks.values()), "tallies": res,
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "floor.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("answerable", "const_equivalence_rate", "shares", "checks", "passed")}, indent=1))
    return out


# ---------------------------------------------------------------- real run

def q2_rows(tag, draw10):
    d = json.load(open(Q2 / f"swap-{tag}.json"))
    by = {r["id"]: r for r in draw10}
    rows = []
    for r in d["rows"]:
        if r["trueLabel"] is None or r["swappedLabel"] is None:
            continue
        hi_s, lo_s = (r["trueLabel"], r["swappedLabel"]) if r["tail"] == "high" else (r["swappedLabel"], r["trueLabel"])
        base = dict(by[r["id"]])
        assert base["tail"] == r["tail"] and base["human"] == r["human"], r["id"]
        base.update(high=hi_s, low=lo_s)
        rows.append(base)
    return rows, d["model"]


def new_rows(corpus, tag):
    p = DUMPS / f"{corpus}-{tag}.json"
    if not p.exists():
        return None, None
    d = json.load(open(p))
    assert not d.get("dryRun"), p
    return [r for r in d["rows"] if r["high"] is not None and r["low"] is not None], d


def sentence(label, max_, n=39):
    return f"Current attainment for this learner across this course: {label:.1f}/{max_}, from {n} prior graded responses."


def control_size():
    """Each arm is the other's control: the low-label sentence must be the size of the high-label one."""
    sys.path.insert(0, str(ROOT))
    from shared.controls import check_control_scale
    out = {}
    for n in ("jorgpt10", "jorgpt5", "mohler", "menagerie"):
        rows, m = load_draw(n)
        sizes = {"high label": float(np.mean([len(sentence(r["labelHigh"], m)) for r in rows])),
                 "low label": float(np.mean([len(sentence(r["labelLow"], m)) for r in rows]))}
        rep = check_control_scale(sizes, ["low label"])
        out[n] = {"sizes": sizes, "report": rep["report"]}
    return out


def run_real():
    floor = json.load(open(OUT / "floor.json"))
    if not floor.get("passed"):
        sys.exit("floor has not passed; refusing to read any dump")
    answerable = set(floor["answerable"])
    draw10, _ = load_draw("jorgpt10")
    sd_by = {}
    for n in ("jorgpt10", "jorgpt5", "mohler", "menagerie"):
        rows, _ = load_draw(n)
        sd_by[n] = float(np.std([r["human"] for r in rows]))
    rng = np.random.default_rng(7)
    results = {"delta": DELTA, "delta_sd": DELTA_SD, "answerable": sorted(answerable),
               "control_size": control_size(), "models": {}}
    verdicts = {}
    for tag, (q2tag, label) in MODELS.items():
        cells, meta = {}, {}
        rows, spec = q2_rows(q2tag, draw10)
        cells["jorgpt10"] = Cell("jorgpt10", rows, 10, sd_by["jorgpt10"])
        meta["jorgpt10"] = {"source": f"Q2 dump swap-{q2tag}.json", "model": spec, "n": len(rows), "of": 300}
        for corpus, max_ in (("jorgpt5", 5), ("mohler", 5), ("menagerie", 13)):
            rws, d = new_rows(corpus, tag)
            if rws is None:
                continue
            assert d["max"] == max_, (corpus, d["max"])
            cells[corpus] = Cell(corpus, rws, max_, sd_by[corpus])
            meta[corpus] = {"model": d["model"], "runStamp": d.get("runStamp"), "n": len(rws), "of": len(d["rows"])}
        entry = {"label": label, "cells": meta}
        for unit, delta in (("range", DELTA), ("sd", DELTA_SD)):
            raw, cw = contrasts(cells, REPS, rng, unit)
            cls = {c: classify(*raw[c], delta) for c in raw}
            entry[unit] = {
                "cells": {k: direction(*v) for k, v in cw.items()},
                "contrasts": cls,
                "verdict": model_verdict({c: cls[c]["class"] for c in CONTRASTS if c in cls}, answerable),
            }
        # Pass-through and raw points, reported only.
        entry["raw"] = {k: {"S_points": round(float(c.S.mean()), 3), "max": c.max,
                            "pass_through": round(float(c.S.mean() / c.gap.mean()), 3),
                            "median_chars": float(np.median(c.chars)), "sd_human": round(c.sd, 3),
                            "share_S_zero": round(float(np.mean(c.S == 0)), 3)}
                        for k, c in cells.items()}
        # ADDED AFTER THE RUN, reported only (not part of any verdict): s within thirds of the human
        # score level (a pre-treatment split), to read how much of a cell's s depends on room at the
        # ends of the scale.
        entry["post_hoc_level"] = {}
        for k, c in cells.items():
            cuts = np.percentile(c.h, [100 / 3, 200 / 3])
            band = np.digitize(c.h, cuts)
            entry["post_hoc_level"][k] = {
                "s_by_human_third": [round(float((c.S[band == b] / c.max).mean()), 4) for b in range(3)],
                "human_third_cuts_frac": [round(float(x), 3) for x in cuts],
            }
        # Secondary, reported only: slope of s on log10(chars) within each cell.
        entry["slope_per_decade"] = {}
        for k, c in cells.items():
            if np.ptp(np.log10(c.chars)) < 0.3:
                continue
            x = np.log10(c.chars)
            entry["slope_per_decade"][k] = round(float(np.polyfit(x, c.S / c.max, 1)[0]), 4)
        results["models"][tag] = entry
        verdicts[tag] = entry["range"]["verdict"]
        print(label, entry["range"]["verdict"], "| SD reading:", entry["sd"]["verdict"], file=sys.stderr)
    # Across models: only models with every cell (GPT-5-mini has the Q2 JorGPT cell alone: C1 only).
    full = [t for t, m in results["models"].items() if all(c in m["range"]["contrasts"] for c in CONTRASTS)]
    results["models_in_verdict"] = full
    vs = {verdicts[t] for t in full}
    results["verdict"] = vs.pop() if len(vs) == 1 else "MIXED-ACROSS-MODELS"
    vs_sd = {results["models"][t]["sd"]["verdict"] for t in full}
    results["verdict_sd_reading"] = vs_sd.pop() if len(vs_sd) == 1 else "MIXED-ACROSS-MODELS"
    dirs = {(t, k): c["direction"] for t, m in results["models"].items() for k, c in m["range"]["cells"].items()}
    neg = [f"{t}/{k}" for (t, k), v in dirs.items() if v == "NEGATIVE"]
    unr = [f"{t}/{k}" for (t, k), v in dirs.items() if v == "UNRESOLVED"]
    results["direction"] = ("DIRECTION-REVERSES: " + ", ".join(neg)) if neg else (
        ("DIRECTION-UNRESOLVED: " + ", ".join(unr)) if unr else "DIRECTION-STABLE")
    (OUT / "results.json").write_text(json.dumps(results, indent=1) + "\n")
    print(json.dumps({"verdict": results["verdict"], "sd": results["verdict_sd_reading"],
                      "direction": results["direction"]}, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--floor", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--dump-dir", default=None,
                    help=f"folder holding grader-vi/ and grader-label-stability/ (else ${DUMP_ENV}, "
                         "else shared.paths.scratch_root())")
    a = ap.parse_args()
    if a.floor or a.run:
        set_dump_dir(a.dump_dir)
    if a.floor:
        run_floor()
    if a.run:
        run_real()
