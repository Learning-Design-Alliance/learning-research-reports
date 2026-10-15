"""STANDARDISE BY RELIABILITY. And the decision rule that made the replication fail was broken.

`relative_bar.py` settled two things and this file acts on both.

FIRST, THE RELATIVE BAR FAILED ITS FLOOR and is not adopted: it was no more scale-invariant than the
fixed bar (63.6% drift against 60.2%) and it was CONTAMINATED -- planting conjunctions moved the
measured background by 27.1% of the conjunction's own size, because a conjunctive gate reads +0.083
PAIRWISE (`stage1_floor.py`) and is therefore INSIDE the background that would define the bar. A
yardstick partly made of the thing being measured cannot be the yardstick.

SECOND, THE DECISION RULE WAS WRONG BY ABOUT 500x. Every verdict in this line asked whether the
above-bar share beat FDR_Q = 0.05. Benjamini-Hochberg at q bounds the false discovery proportion
AMONG REJECTIONS; under a global null it rejects almost nothing. Re-running the WHOLE pipeline on
learner-deranged data puts the null share at 0.0000 (97.5th percentile 0.0001), not 0.05. Under the
corrected rule EdNet shows STRUCTURE at BOTH bars -- 0.016 [0.003, 0.035] at the fixed +0.10 with
100% power, and 0.078 [0.036, 0.130] at its own. **`replicate.py`'s FAILS verdict was produced by a
broken rule.** Both corpora carry conjunctive structure; they differ in HOW MUCH, by about 7x at the
fixed bar.

THIS FILE ASKS WHETHER THAT REMAINING GAP IS THE INSTRUMENT. Reliability is the right standardiser
precisely where the background was the wrong one: it is measured on LEARNERS, from repeated attempts,
and is therefore independent of the conjunctive statistic rather than made out of it. XES3G5M's
split-half is 0.572 against EdNet's 0.315, a ratio of 1.82, while their backgrounds sit at 2.19 --
close enough that attenuation is the obvious candidate.

THE MECHANISM, AND WHY IT PREDICTS SOMETHING SHARP. Noise in the OUTCOME does not bias a difference
of means; it inflates the variance only, and in any case our estimand is observable performance at c,
so outcome noise is part of the estimand rather than a nuisance. Noise in the PREDICTOR is different:
"held A" is a noisy indicator of mastering A, and a mismeasured predictor attenuates the coefficient
it carries. An interaction rides on TWO mismeasured indicators, so it should attenuate by roughly the
SQUARE of what a main effect suffers:

    observed_main        ~  r^1  x  true_main
    observed_interaction ~  r^2  x  true_interaction

That is falsifiable, and floor (a) measures the exponents rather than assuming them. If it does not
recover them on planted data, no correction is applied.

MEASURING r, the new measurement this file adds. For each item, learners with at least two attempts
have their attempts split ODD / EVEN, giving two independent verdicts on whether they ever passed it.
The phi correlation between those two verdicts across learners, Spearman-Brown corrected to full
length, is the reliability of "held this item" AS AN INDICATOR -- which is the quantity the
attenuation argument needs, and is not the same as `split_half.py`'s reliability of the edge
STATISTIC.

PRE-REGISTERED, before the run:

  floor (a) EXPONENTS RECOVERABLE   on planted data with indicators corrupted to known reliability,
            the fitted exponents must land near 1 for the main effect and near 2 for the interaction
            (pre-registered window 0.6-1.5 and 1.4-2.8). Outside that, the attenuation model is
            wrong for this statistic and NO CORRECTION IS APPLIED -- the run stops and says so.
  floor (b) CORRECTION RESTORES     disattenuating a corrupted corpus must return its above-bar share
            to within 25% of the uncorrupted corpus's. A correction that does not recover a known
            answer is not a correction.

  then, on the corrected scale and at the SINGLE fixed +0.10 bar, because standardising is what makes
  an absolute bar meaningful again:
    REPLICATES    the two corpora's block CIs on the corrected above-bar share OVERLAP.
    DOES NOT      they do not. The gap is real and is not the instrument.

Decision rule throughout is the deranged pipeline null, never FDR_Q.

Reads XES3G5M and EdNet. EdNet is CC BY-NC 4.0 -- non-commercial, no model training. Raw exports stay
in the session scratchpad; only aggregates are committed.

    python3 reliability_bar.py [--items 30] [--draws 1000]
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "studies/identifiability/overlap"))

from atlas import ednet_rows, xes3g5m_rows  # noqa: E402
sys.path.insert(0, str(HERE.parents[2]))
from shared.corpus import KT1_RESTORED, ednet_questions, kt1_members  # noqa: E402
from positivity import SCRATCH, at_item, states, timelines  # noqa: E402
from block_bootstrap import (FDR_Q, MIN_CELL, MIN_MEANINGFUL, _jsonable,  # noqa: E402
                             bh, block_bootstrap, design_effect, one_sided_p, score_item)
from replicate import coarsen  # noqa: E402
from relative_bar import derange, pipeline_null, synth, synth_read  # noqa: E402

SEED = 20260922
#: pre-registered windows the fitted attenuation exponents must land in, or no correction is applied
MAIN_WINDOW, INTER_WINDOW = (0.6, 1.5), (1.4, 2.8)
#: disattenuation must return a corrupted corpus to within this of the clean one
RESTORE_TOL = 0.25
#: a learner needs at least this many attempts at an item to contribute to its reliability
MIN_ATTEMPTS = 2
#: an item needs at least this many such learners for its reliability to be read
MIN_REL_LEARNERS = 60


def phi_sb(x, y):
    """Split-half correlation of two binary verdicts, Spearman-Brown corrected to full length."""
    if len(x) < MIN_REL_LEARNERS or x.std() == 0 or y.std() == 0:
        return None
    r = float(np.corrcoef(x, y)[0, 1])
    if not np.isfinite(r) or r <= -1:
        return None
    return float(max(0.0, min(0.999, (2 * r) / (1 + r))))


def indicator_reliability(attempts):
    """Per item: split a learner's attempts ODD / EVEN and correlate the two 'ever passed' verdicts.

    This is the reliability of the PREDICTOR -- "did this learner hold the item" -- which is what the
    attenuation argument needs. `studies/measurement/reliability/split_half.py` measures something different: the
    reliability of the edge STATISTIC across halves of the learner pool.
    """
    out = {}
    for item, seq in attempts.items():
        odd, even = [], []
        for outcomes in seq:
            if len(outcomes) < MIN_ATTEMPTS:
                continue
            odd.append(int(any(outcomes[0::2])))
            even.append(int(any(outcomes[1::2])))
        r = phi_sb(np.array(odd, float), np.array(even, float)) if odd else None
        if r is not None:
            out[item] = dict(r=r, n=len(odd))
    return out


# ---------------------------------------------------------------- the floor

def corrupt(held, flip, rng):
    """Flip an indicator with probability `flip` -- misclassification of 'held this item'."""
    return held ^ (rng.random(held.shape) < flip)


def measure_r(held, flip, rng):
    """The reliability an odd/even split would report for an indicator corrupted at this rate."""
    a = corrupt(held, flip, rng)
    b = corrupt(held, flip, rng)
    rs = [phi_sb(a[:, j].astype(float), b[:, j].astype(float)) for j in range(held.shape[1])]
    rs = [x for x in rs if x is not None]
    return float(np.median(rs)) if rs else float("nan")


def planted_interaction(held_out, held_pred, by_c):
    """Mean interaction over exactly the triples a conjunction was PLANTED in.

    The denominator problem the previous two versions had. Selecting on significance gave a winner's
    curse; averaging over ALL triples gave a baseline of almost zero, because the signal is sparse,
    so the ratio exploded and changed sign. The planted set is known by construction, is not selected
    on any outcome, and has a real non-zero baseline -- which is what an attenuation exponent has to
    be fitted against.
    """
    vals = []
    for c, pairs in by_c.items():
        ok = held_out[:, c].astype(float)
        for a, b in pairs:
            ha, hb = held_pred[:, a], held_pred[:, b]
            sel = [ha & hb, ha & ~hb, ~ha & hb, ~ha & ~hb]
            n = [int(x.sum()) for x in sel]
            if min(n) < MIN_CELL:
                continue
            m = [float(ok[x].mean()) for x in sel]
            vals.append((m[0] - m[1]) - (m[2] - m[3]))
    return float(np.mean(vals)) if vals else float("nan")


def stats_of(held_out, held_pred):
    """Median main effect and MEAN interaction over ALL triples, plus the raw array.

    THE INTERACTION SUMMARY IS DELIBERATELY UNSELECTED, and the first version of this floor got that
    wrong. It used the median of the BH-SIGNIFICANT interactions, which is a selected quantity: as
    the predictor gets noisier fewer triples survive selection and the survivors are the largest, so
    the median of survivors does not fall. The fitted exponent came out at 0.16 with ratios bouncing
    between -0.05 and 1.00 -- a winner's curse in the measurement, not a fact about attenuation. The
    main effect was already unselected, which is why it behaved (1.24, against an expected 1). Both
    statistics are now summarised the same unselected way.
    """
    n, m = held_out.shape
    drops, inter = [], []
    for c in range(m):
        ok = held_out[:, c].astype(float)
        cols = [j for j in range(m) if j != c]
        for a in cols:
            ha = held_pred[:, a]
            if ha.sum() < MIN_CELL or (~ha).sum() < MIN_CELL:
                continue
            drops.append(float(ok[ha].mean() - ok[~ha].mean()))
        got = score_item(ok, held_pred[:, cols], [str(j) for j in cols], str(c))
        if got is not None:
            inter.append(np.stack([got["interaction"], got["z"]]))
    if not inter:
        return float("nan"), float("nan"), np.zeros((2, 0))
    allv = np.concatenate(inter, 1)
    return (float(np.median(drops)) if drops else float("nan"),
            float(np.mean(allv[0])), allv)


def floor(rng, n=8000, m=26, reps=3):
    print("FLOOR -- the attenuation model has to earn the correction\n")
    print("  (a) EXPONENTS: corrupt the PREDICTOR to known reliability, watch both statistics fall")
    flips = (0.0, 0.05, 0.12, 0.22)
    rows = []
    for _ in range(reps):
        held, by_c = synth(n, m, rng, bg=0.085, conj=0.20)
        base_main, _, _ = stats_of(held, held)
        base_int = planted_interaction(held, held, by_c)
        for f in flips:
            r = 1.0 if f == 0 else measure_r(held, f, rng)
            noisy = corrupt(held, f, rng)
            mn, _, _ = stats_of(held, noisy)
            it = planted_interaction(held, noisy, by_c)
            rows.append((r, mn / base_main, it / base_int))
    arr = np.array([x for x in rows if np.isfinite(x).all() and x[0] > 0.05])
    ok_rows = arr[arr[:, 0] < 0.999]
    k_main = float(np.median(np.log(np.clip(ok_rows[:, 1], 1e-6, None)) / np.log(ok_rows[:, 0])))
    k_int = float(np.median(np.log(np.clip(ok_rows[:, 2], 1e-6, None)) / np.log(ok_rows[:, 0])))
    for r, mn, it in arr[np.argsort(-arr[:, 0])][:8]:
        print(f"      r = {r:.3f}   main x{mn:.3f}   interaction x{it:.3f}")
    print(f"      fitted exponents:  main {k_main:.2f} (expected ~1, window {MAIN_WINDOW})   "
          f"interaction {k_int:.2f} (expected ~2, window {INTER_WINDOW})")
    good = bool(MAIN_WINDOW[0] <= k_main <= MAIN_WINDOW[1]
                and INTER_WINDOW[0] <= k_int <= INTER_WINDOW[1])
    print(f"      -> {'RECOVERED' if good else 'NOT RECOVERED'}: the attenuation model "
          f"{'holds' if good else 'does NOT hold'} for this statistic")
    if not good:
        return dict(exponents_recovered=False, k_main=k_main, k_interaction=k_int)

    print("\n  (b) RESTORATION: does dividing by r^k bring a corrupted corpus back?")
    clean_s, dirty_s, fixed_s = [], [], []
    for _ in range(reps):
        held, by_c = synth(n, m, rng, bg=0.085, conj=0.20)
        _, _, a0 = stats_of(held, held)
        r = measure_r(held, 0.12, rng)
        _, _, a1 = stats_of(held, corrupt(held, 0.12, rng))
        for arrv, bucket, div in ((a0, clean_s, 1.0), (a1, dirty_s, 1.0),
                                  (a1, fixed_s, r ** k_int)):
            keep = bh(one_sided_p(arrv[1]), FDR_Q) & (arrv[0] > 0)
            bucket.append(float((keep & (arrv[0] / div >= MIN_MEANINGFUL)).mean()))
    C, D, F = (float(np.median(clean_s)), float(np.median(dirty_s)), float(np.median(fixed_s)))
    err = abs(F - C) / max(C, 1e-9)
    print(f"      clean corpus share      {C:.4f}")
    print(f"      corrupted, uncorrected  {D:.4f}   ({100*(D-C)/max(C,1e-9):+.0f}%)")
    print(f"      corrupted, CORRECTED    {F:.4f}   ({100*(F-C)/max(C,1e-9):+.0f}%)")
    rest = bool(err <= RESTORE_TOL)
    print(f"      -> {'RESTORES' if rest else 'DOES NOT RESTORE'}: correction lands within "
          f"{100*err:.0f}% of the clean answer, tolerance {100*RESTORE_TOL:.0f}%")
    return dict(exponents_recovered=True, restores=rest, k_main=k_main, k_interaction=k_int,
                clean=C, corrupted=D, corrected=F, restore_error=float(err))


# ---------------------------------------------------------------- arms

def ednet_dense(root: Path, items_n):
    """One streaming pass: first-touch/first-pass per tag, PLUS the odd/even split reliability needs.

    `positivity.timelines` holds every event as a Python tuple and 60,308 EdNet learners is ~75M of
    them, which does not fit. Everything needed here is a handful of numbers per learner per tag, so
    they are accumulated in dicts per learner and written into dense arrays one row at a time.
    """
    # leading tag per question, via the shared parse: the `-1` sentinel is not a KC, so its 797
    # questions are skipped (until 2026-09-24 they formed a unit "-1")
    answer, tagof = {}, {}
    for q, (key, tags) in ednet_questions(root / "contents").items():
        if tags:
            answer[q] = key
            tagof[q] = tags[0]
    tags = sorted(set(tagof.values()))
    tix = {t: i for i, t in enumerate(tags)}
    # The zip, not the extracted directory: the learner set is the first KT1_RESTORED namelist
    # members, a function of the archive alone (shared/corpus.kt1_members; re-issued 2026-09-24).
    zf, files = kt1_members(root.parent / "ednet-kt1.zip", KT1_RESTORED)
    n, m = len(files), len(tags)
    FT = np.full((n, m), np.nan)
    FP = np.full((n, m), np.nan)
    OAT = np.zeros((n, m), np.int8)
    ODD = np.zeros((n, m), np.int8)
    EVEN = np.zeros((n, m), np.int8)
    NATT = np.zeros((n, m), np.int16)
    for r, f in enumerate(files):
        ft, fp, oat, cnt, od, ev = {}, {}, {}, {}, {}, {}
        with io.TextIOWrapper(zf.open(f), encoding="utf-8", errors="replace") as fh:
            next(fh, None)
            for line in fh:
                col = line.split(",")
                if len(col) < 4:
                    continue
                t = tagof.get(col[2])
                if t is None:
                    continue
                j = tix[t]
                ts = float(col[0])
                ok = col[3] == answer[col[2]]
                k = cnt.get(j, 0)
                cnt[j] = k + 1
                if ok:
                    (od if k % 2 == 0 else ev)[j] = 1
                if j not in ft or ts < ft[j]:
                    ft[j] = ts
                    oat[j] = ok
                if ok and (j not in fp or ts < fp[j]):
                    fp[j] = ts
        if ft:
            kk = list(ft)
            FT[r, kk] = [ft[i] for i in kk]
            OAT[r, kk] = [oat[i] for i in kk]
        if fp:
            kk = list(fp)
            FP[r, kk] = [fp[i] for i in kk]
        if cnt:
            kk = list(cnt)
            NATT[r, kk] = [cnt[i] for i in kk]
            ODD[r, kk] = [od.get(i, 0) for i in kk]
            EVEN[r, kk] = [ev.get(i, 0) for i in kk]
        if (r + 1) % 20000 == 0:
            print(f"    {r+1:,}/{n:,} learners", flush=True)
    order = np.argsort(-np.isfinite(FT).sum(0))[:items_n]
    items = [tags[i] for i in order]
    dep = []
    for ci in order:
        sel = np.isfinite(FT[:, ci])
        pcols = [c for c in order if c != ci]
        dep.append((OAT[sel, ci].astype(float),
                    FP[np.ix_(sel, pcols)] < FT[sel, ci][:, None],
                    [tags[c] for c in pcols], tags[ci]))
    rel = {}
    for ci in order:
        m2 = NATT[:, ci] >= MIN_ATTEMPTS
        r = phi_sb(ODD[m2, ci].astype(float), EVEN[m2, ci].astype(float))
        if r is not None:
            rel[tags[ci]] = dict(r=r, n=int(m2.sum()))
    return dep, items, rel, n


def arm(name, items_n):
    """Per-dependant (ok, H, names, c), item list, and per-item attempt outcome sequences."""
    if name == "ednet":
        return ednet_dense(SCRATCH / "ednet", items_n)
    rows = xes3g5m_rows(SCRATCH / "xes3g5m")
    if name == "xes3g5m-coarse":
        rows = coarsen(list(rows))
    rows = list(rows)
    by_learner = timelines(rows)
    ft, fp, oat = states(by_learner)
    idx = at_item(ft, oat)
    items = sorted(idx, key=lambda i: -len(idx[i]))[:items_n]
    keep = set(items)
    attempts = {i: [] for i in items}
    for learner, seq in by_learner.items():
        per = {}
        for _t, item, ok in seq:
            if item in keep:
                per.setdefault(item, []).append(bool(ok))
        for item, o in per.items():
            attempts[item].append(o)
    dep = []
    for c in items:
        at_c = idx[c]
        learners = [l for l, _t, _y in at_c]
        tc = np.array([t for _l, t, _y in at_c])
        ok = np.array([float(y) for _l, _t, y in at_c])
        pn = [p for p in items if p != c]
        H = np.zeros((len(at_c), len(pn)), bool)
        for j, p in enumerate(pn):
            for k, l in enumerate(learners):
                pp = fp[l].get(p)
                if pp is not None and pp < tc[k]:
                    H[k, j] = True
        dep.append((ok, H, pn, c))
    return dep, items, indicator_reliability(attempts), len(by_learner)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", type=int, default=30)
    ap.add_argument("--draws", type=int, default=1000)
    ap.add_argument("--null-reps", type=int, default=120)
    ap.add_argument("--arms", default="xes3g5m,xes3g5m-coarse,ednet")
    ap.add_argument("--out", default="out/reliability_bar.json")
    args = ap.parse_args()
    rng = np.random.default_rng(SEED)

    fl = floor(rng)
    out = dict(seed=SEED, floor=fl, bar=MIN_MEANINGFUL, arms={})
    if not fl.get("exponents_recovered"):
        print("\nSTOPPING -- the attenuation model does not hold for this statistic.")
        Path(args.out).write_text(json.dumps(out, indent=2, default=_jsonable) + "\n")
        return
    apply_fix = bool(fl.get("restores"))
    if not apply_fix:
        print("\nTHE CORRECTION IS NOT APPLIED TO ANY VERDICT: floor (b) failed. Disattenuation "
              "restores EFFECT SIZE but not POWER -- BH selection runs on the raw z, which the "
              "rescaling does not touch, so triples that lost significance to noise cannot be "
              "resurrected by multiplying the survivors. Reliabilities and the corrected numbers "
              "below are DIAGNOSTIC ONLY.")
    out["correction_applied"] = apply_fix
    k = fl["k_interaction"]

    for name in args.arms.split(","):
        print(f"\n{'='*78}\nARM: {name}", flush=True)
        dep, items, rel, nlearn = arm(name, args.items)
        rs = np.array([v["r"] for v in rel.values()])
        r_corpus = float(np.median(rs)) if len(rs) else float("nan")
        print(f"  {nlearn:,} learners, {len(dep)} dependants; INDICATOR RELIABILITY "
              f"median {r_corpus:.3f} over {len(rs)} items "
              f"(p10 {np.percentile(rs,10):.3f}, p90 {np.percentile(rs,90):.3f})", flush=True)

        parts = [score_item(ok, H, pn, c) for ok, H, pn, c in dep]
        parts = [g for g in parts if g is not None]
        inter = np.concatenate([g["interaction"] for g in parts])
        z = np.concatenate([g["z"] for g in parts])
        pos = {t: i for i, t in enumerate(items)}
        tri = np.stack([np.concatenate([[pos[x] for x in g[kk]] for g in parts])
                        for kk in ("c", "a", "b")], 1)
        pv = one_sided_p(z)
        T = len(z)
        # the per-triple correction uses the two PARENTS' own reliabilities, not the corpus median
        ra = np.array([rel.get(a, {"r": r_corpus})["r"]
                       for a in np.concatenate([g["a"] for g in parts])])
        rb = np.array([rel.get(b, {"r": r_corpus})["r"]
                       for b in np.concatenate([g["b"] for g in parts])])
        lam = np.clip(np.sqrt(ra * rb) ** k, 0.05, 1.0)
        corrected = inter / lam

        for label, vals in (("raw", inter), ("corrected", corrected)):
            keep = bh(pv, FDR_Q) & (inter > 0)
            share = float((keep & (vals >= MIN_MEANINGFUL)).mean())
            boot = block_bootstrap(items, tri, pv, vals, rng, args.draws, bar=MIN_MEANINGFUL)
            d, bv = design_effect(boot, share, key="above_share", n=T)
            lo, hi = np.percentile(bv, [2.5, 97.5])
            ns, _ = pipeline_null(dep, items, MIN_MEANINGFUL, rng,
                                  args.null_reps if label == "raw" else 0)
            nhi = float(np.percentile(ns, 97.5)) if len(ns) else out["arms"].get(
                name, {}).get("raw", {}).get("null_hi", 0.0)
            print(f"    {label:<10} above-bar share {share:.3f}  block CI [{lo:.3f}, {hi:.3f}]"
                  + (f"   deranged null 97.5th {nhi:.4f}" if label == "raw" else
                     f"   (median attenuation factor {np.median(lam):.3f})"))
            out["arms"].setdefault(name, {})[label] = dict(
                share=share, lo=float(lo), hi=float(hi), design_effect=d,
                n_eff=float(T / d) if d else None, null_hi=nhi,
                median_lambda=float(np.median(lam)), n_triples=T,
                indicator_reliability=r_corpus, learners=nlearn)

    out["verdict_scope"] = ("corrected scale" if apply_fix else
                            "raw scale -- the correction did not earn its floor")
    a = out["arms"].get("xes3g5m", {}).get("corrected")
    b = out["arms"].get("ednet", {}).get("corrected")
    if a and b:
        overlap = not (b["hi"] < a["lo"] or a["hi"] < b["lo"])
        raw_a = out["arms"]["xes3g5m"]["raw"]
        raw_b = out["arms"]["ednet"]["raw"]
        raw_ov = not (raw_b["hi"] < raw_a["lo"] or raw_a["hi"] < raw_b["lo"])
        # THE VERDICT IS TAKEN ON WHICHEVER SCALE THE FLOOR LICENSED, and the first version of this
        # block took it on the corrected scale unconditionally -- reporting REPLICATES off numbers
        # the floor had just refused. If floor (b) failed, the raw scale decides.
        out["verdict"] = (("REPLICATES" if overlap else "DOES NOT REPLICATE") if apply_fix else
                          ("REPLICATES" if raw_ov else "DOES NOT REPLICATE"))
        print(f"\n{'='*78}\nAT THE FIXED {MIN_MEANINGFUL:+.2f} BAR, ON THE CORRECTED SCALE")
        print(f"  XES3G5M  raw {raw_a['share']:.3f} [{raw_a['lo']:.3f}, {raw_a['hi']:.3f}]"
              f"   corrected {a['share']:.3f} [{a['lo']:.3f}, {a['hi']:.3f}]")
        print(f"  EdNet    raw {raw_b['share']:.3f} [{raw_b['lo']:.3f}, {raw_b['hi']:.3f}]"
              f"   corrected {b['share']:.3f} [{b['lo']:.3f}, {b['hi']:.3f}]")
        print(f"  intervals overlap: raw {raw_ov}, corrected {overlap}")
        print(f"\nVERDICT: {out['verdict']}")
        out["raw_overlap"] = raw_ov
    Path(args.out).write_text(json.dumps(out, indent=2, default=_jsonable) + "\n")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
