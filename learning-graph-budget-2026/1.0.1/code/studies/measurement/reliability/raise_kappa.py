"""How do we raise decision kappa? Four levers, measured against the control that catches the cheat.

studies/outcomes/ope/c3_readiness.py made A5 the binding constraint on the north star: a graph-derived policy acts
on the assay's output, realised gain tracks the assay's decision kappa, and sample size therefore
scales as 1/kappa^2. At XES3G5M's +0.438 that is a 4.7x penalty on C3; moving to 0.80 would cut
C3's sample by 3.3x, more than any trial-design change available. So "raise kappa" is now the
highest-value piece of work on the board, and this script asks how.

WHAT KAPPA IS MEASURING HERE. studies/measurement/reliability/tail.py splits learners three ways, computes the
prerequisite drop in each part, and asks whether two independent parts ASSERT THE SAME EDGES at
drop > 0.10. Kappa is chance-corrected agreement on that binary decision. It reads +0.411 / +0.422
/ +0.438 on XES3G5M across cell floors 5 / 10 / 20, and +0.130 / +0.131 / +0.131 on EdNet.

THE FOUR LEVERS, and why each might work:

  LCB          decide on `drop - z*se > bar` instead of `drop > bar`. The current rule treats a
               drop of +0.11 from a cell of 12 learners exactly like one from a cell of 900. A
               pair whose estimate is mostly noise flips between halves by construction, and a
               precision-aware rule stops asserting it. Costs coverage.
  SHRINK       empirical Bayes: pull each pair's drop toward the corpus mean by se^2/(se^2+tau^2),
               with tau^2 the between-pair variance net of measurement error, then apply the bar.
               Standard for exactly this problem.
  ABSTAIN      three-way output -- assert, deny, or decline to say -- and score kappa only where
               both halves committed. This is the assay admitting it does not know.
  BAR          move the threshold. Kappa depends on where the bar sits in the density of true
               drops: XES3G5M asserts ~55% of pairs, which means the bar sits near the mode, which
               is the worst possible place for stability. This lever changes WHAT THE ASSAY CLAIMS,
               so it is measured but is not free.

THE CONTROL THAT MATTERS, AND THE REASON THIS SCRIPT EXISTS RATHER THAN A ONE-LINE PATCH.
**Three of these four levers can raise kappa without the assay getting any better, and SHRINK is
the worst offender.** Shrinking every pair toward a common mean moves both halves' estimates
toward the SAME number; past a certain strength the two halves agree because they have both been
pulled to the corpus mean, not because they found the same structure. In the limit every pair is
shrunk to the mean, every decision is identical, and kappa is undefined or perfect for no reason
at all. Abstention does the same thing by a different route: discard everything uncertain and what
remains agrees trivially. Raising the bar can too, by driving the assert rate toward zero.

So every lever is run TWICE: on the real corpus and on LEARNER-DERANGED data, where a learner
keeps their outcome and inherits another learner's parent-state, so no true prerequisite structure
survives. A lever that raises kappa on the deranged corpus is manufacturing agreement, and is
rejected however good it looks on the real one.

PRE-REGISTERED, before the run:

    floor      the baseline rule must reproduce tail.py's kappa to within 0.05 at the same cell
               floor. If this script cannot reproduce the number it is trying to improve, nothing
               below means anything.
    accept     a lever counts as REAL if it raises kappa by at least 0.05 over baseline on the
               real corpus, AND its deranged kappa stays below 0.05, AND it still decides at
               least 50% of readable pairs (coverage).
    reject     any lever whose deranged kappa exceeds 0.05 is MANUFACTURING AGREEMENT and is
               reported as such regardless of its real-corpus number.
    report     coverage beside every kappa, always. A kappa on 5% of pairs is a different assay,
               not a better one.

Also measured, because it bounds everything: KAPPA AGAINST LEARNER COUNT. Each half currently uses
a third of the corpus. If kappa rises steeply with learners then the ceiling is sample size and no
decision rule will fix it; if it is flat then the rule is the problem and more data will not help.

DATA. XES3G5M from the session scratchpad. Only aggregates are written to out/.

FINISHING (pre-registered 2026-10-05, committed before either new mode is run). Three things this
study promised and did not deliver, found by reading it against its own docstring:

  1. THE REJECT RULE ABOVE WAS NEVER APPLIED. `MAX_DERANGED` is defined and never read; the run
     scored "manufactured" by a different, relative rule (deranged rise > half the real rise), so
     abstention at z = 0.5 -- deranged +0.088, above the registered 0.05 -- was scored REAL. The
     main path now applies the registered rule (deranged > MAX_DERANGED is MANUFACTURING, and a
     lever can only be REAL with deranged <= MAX_DERANGED), keeping the relative rule as a second
     flag. `--rescore` re-applies it to the committed out/raise_kappa.json without recomputing
     anything, so the corrected table is the same run read by the rule written before it.
  2. THE LEARNER CURVE WAS RAW. Every lever is scored on excess over its deranged arm, but kappa
     against learners was not, so "more learners help" was never shown on the quantity that
     matters. `--curve` re-measures it on EXCESS: the baseline rule (LCB z = 1.0, bar 0.10, cell
     floor 10, 90 best-covered items, learners split in half), at learner fractions 0.15 / 0.3 /
     0.5 / 0.75 / 1.0, 4 random subsamples per fraction (1 at 100%), 4 real splits and 2 deranged
     splits per subsample, with a 95% interval over real x deranged split combinations. Through
     pairgrid.py (the matrix form of positivity.classify, asserted equal to it before use).
       floor   the curve's 100% point must reproduce this study's baseline +0.494 within FLOOR_TOL
               (0.05). If not, the curve is not read.
  3. "GET MORE LEARNERS" WAS NOT SIZED. A curve kappa(n) = k_max * n / (n + n_half) (n learners per
     half) is fitted to the EXCESS points by least squares; reported: k_max, n_half, and the
     learners per half at which excess kappa would reach 0.60, 0.70 and 0.80, with intervals from
     refitting over split draws. If k_max's upper bound is below a target, the target is
     UNREACHABLE BY SAMPLE SIZE ALONE. EdNet (the atlas reader, first 60,000 learners, 90
     best-covered items) is run the same way at fractions of 60,000, because it is the corpus with
     the unused learners RAISE-KAPPA.md points at.
  verdicts  per corpus: SAMPLE IS THE CEILING if excess kappa rises by >= 0.05 between the smallest
            and largest fraction with the two intervals disjoint; FLAT otherwise.

    python3 raise_kappa.py --rescore            # registered rule on the committed run
    python3 raise_kappa.py --curve [--corpus xes3g5m|ednet]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2]))
sys.path.insert(0, str(HERE.parents[2] / "studies/identifiability/overlap"))

from shared.stats import kappa  # noqa: E402
from atlas import xes3g5m_rows  # noqa: E402
from positivity import SCRATCH, at_item, classify, states, timelines  # noqa: E402

SEED = 20260923
BAR = 0.10
#: THE BASELINE IS NOW THE ADOPTED RULE, NOT THE OLD ONE. The first pass of this study took the
#: plain `drop > BAR` as its reference and found LCB the one clean improvement on it. `drop > BAR`
#: is therefore no longer the rule in use, and measuring against it would keep re-proving a
#: decision already taken. Every lever below is now scored against AND COMPOSED WITH LCB at this z,
#: so the question changes from "does anything beat the plain rule" to "does anything ADD to the
#: rule we adopted". Pass --base-z 0 to recover the original comparison.
BASE_Z = 1.0
#: a lever must beat baseline by this much to be worth adopting
MIN_GAIN = 0.05
#: and must leave the deranged corpus below this, or it is manufacturing agreement
MAX_DERANGED = 0.05
#: and must still decide this share of readable pairs
MIN_COVERAGE = 0.50
#: reproduce tail.py's reading to within this before anything else is believed
FLOOR_TOL = 0.05


def drops_se(pairs, ft, fp, oat, idx, min_cell):
    """Per-pair drop WITH its standard error -- the quantity the current rule throws away.

    split_half.drops returns the drop and the pair's reach but no precision, so `drop > bar`
    cannot tell a well-measured +0.11 from a noisy one. se is the usual difference-of-means
    standard error on the two cells.
    """
    out = {}
    for a, b in pairs:
        c = classify((a, b), ft, fp, oat, idx)
        m, f = np.asarray(c["mastered"], float), np.asarray(c["failed"], float)
        nm, nf = len(m), len(f)
        if nm < min_cell or nf < min_cell:
            continue
        se = float(np.sqrt(m.var(ddof=1) / nm + f.var(ddof=1) / nf))
        out[(a, b)] = (float(m.mean() - f.mean()), se if np.isfinite(se) and se > 0 else np.nan)
    return out


def derange_history(ft, fp, rng):
    """A learner keeps their OUTCOME at the dependant and inherits another learner's PARENT STATE.

    THE OBVIOUS IMPLEMENTATION IS A NO-OP AND THIS SCRIPT'S FLOOR CAUGHT IT. Remapping whole
    learner records -- {learner_i: record_of_learner_j} -- only RELABELS learners. The drop is an
    aggregate over learners, so the multiset of records is unchanged and every statistic is
    identical; the deranged arm came back at kappa +0.475 against a real +0.480, which is not a
    weak control, it is the same data wearing a different name.

    What has to be broken is the LINK classify() reads: a learner's outcome at the dependant comes
    from `idx`, and their state on the parent comes from first_touch/first_pass. Deranging only the
    history dicts, and leaving `idx` built from the ORIGINAL first-touch and outcomes, crosses one
    learner's parent-state with another's dependant outcome. Both marginals survive exactly; only
    the dependence between them dies, which is the thing under test.

    A derangement, not a permutation: no fixed points. An ordinary permutation leaves 1/n of the
    real evidence in place, which was enough to score a spurious p = 0.006 elsewhere here.
    """
    keys = sorted(ft)
    n = len(keys)
    if n < 2:
        return ft, fp
    while True:
        perm = rng.permutation(n)
        if not np.any(perm == np.arange(n)):
            break
    donor = {keys[i]: keys[perm[i]] for i in range(n)}
    return ({k: ft[donor[k]] for k in keys}, {k: fp[donor[k]] for k in keys})


def tau2(d, se):
    """Between-pair variance net of measurement error -- the empirical-Bayes prior width."""
    v = float(np.nanvar(d, ddof=1) - np.nanmean(se ** 2))
    return max(v, 1e-6)


def decisions(d, se, lever, param, bar=BAR):
    """Return (assert, committed) boolean arrays for a lever, COMPOSED WITH the adopted LCB margin.

    Each lever now CARRIES the BASE_Z precision margin rather than replacing it, because LCB is the
    rule in use: `shrink` shrinks and THEN applies the margin, `bar` moves the threshold while
    keeping it, and `baseline` IS the margin. Only `lcb` varies the margin itself, so its sweep
    answers whether the adopted z is the right one. `abstain` already works in units of se, so it is
    precision-aware by construction and its param is its own margin.
    """
    ok = np.isfinite(d) & np.isfinite(se)
    committed = ok.copy()
    if lever == "baseline":
        a = (d - BASE_Z * se) > bar
    elif lever == "lcb":
        a = (d - param * se) > bar
    elif lever == "shrink":
        t2 = tau2(d[ok], se[ok])
        mu = float(np.nanmean(d[ok]))
        w = t2 / (t2 + param * se ** 2)
        a = (mu + w * (d - mu) - BASE_Z * se) > bar
    elif lever == "abstain":
        hi, lo = d - param * se, d + param * se
        a = hi > bar
        committed = ok & ((hi > bar) | (lo < bar))
    elif lever == "bar":
        a = (d - BASE_Z * se) > param
    else:
        raise ValueError(lever)
    return np.where(ok, a, False), committed


def one_split(pairs, by_learner, learners, min_cell, rng, derange=False):
    """Two independent halves of learners, each scored; returns aligned drop/se arrays.

    With `derange`, each half's parent-state is crossed onto another learner's dependant outcome
    AFTER `idx` is built, so the dependant side is untouched and only the dependence is destroyed.
    """
    perm = rng.permutation(len(learners))
    half = len(perm) // 2
    parts = []
    for lo, hi in ((0, half), (half, len(perm))):
        side = {learners[i] for i in perm[lo:hi]}
        sub = {k: v for k, v in by_learner.items() if k in side}
        ft, fp, oat = states(sub)
        idx = at_item(ft, oat)          # built from the ORIGINAL touch times and outcomes
        if derange:
            ft, fp = derange_history(ft, fp, rng)
        parts.append(drops_se(pairs, ft, fp, oat, idx, min_cell))
    A, B = parts
    common = sorted(set(A) & set(B))
    if len(common) < 100:
        return None
    dA = np.array([A[p][0] for p in common]); sA = np.array([A[p][1] for p in common])
    dB = np.array([B[p][0] for p in common]); sB = np.array([B[p][1] for p in common])
    return dA, sA, dB, sB


def score(splits_data, lever, param):
    """Mean kappa and coverage across splits for one lever setting.

    A lever can make every decision identical, at which point kappa is undefined rather than
    perfect -- there is no variation to agree about. That is not a missing number, it is the
    FLATTENING failure mode this study was built to catch: shrinkage toward a common mean does it
    whenever the between-pair variance net of measurement error collapses, which is exactly what
    happens on deranged data. It is counted and reported rather than averaged away as NaN.
    """
    ks, cov = [], []
    degenerate = 0
    for dA, sA, dB, sB in splits_data:
        aA, cA = decisions(dA, sA, lever, param)
        aB, cB = decisions(dB, sB, lever, param)
        both = cA & cB
        if both.sum() < 50:
            continue
        if aA[both].all() or not aA[both].any() or aB[both].all() or not aB[both].any():
            degenerate += 1
            continue
        k = kappa(aA[both], aB[both])
        if np.isfinite(k):
            ks.append(k)
            cov.append(float(both.mean()))
    ar = float(np.mean([(decisions(d, s, lever, param)[0]).mean()
                        for d, s, _, _ in splits_data]))
    if not ks:
        return float("nan"), float("nan"), ar, degenerate
    return float(np.mean(ks)), float(np.mean(cov)), ar, degenerate


def registered_manufactured(kd) -> bool:
    """The rule written in the docstring before the first run: deranged kappa above MAX_DERANGED."""
    return bool(np.isfinite(kd) and kd > MAX_DERANGED)


def relative_manufactured(k, kd, k0, kd0) -> bool:
    """The rule the first run actually applied: the deranged arm rose by more than half the real rise."""
    return bool(np.isfinite(kd) and np.isfinite(k) and (kd - kd0) > 0.5 * max(k - k0, 1e-9) and k > k0)


def main() -> None:
    global BASE_Z
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", type=int, default=90)
    ap.add_argument("--splits", type=int, default=8)
    ap.add_argument("--min-cell", type=int, default=10)
    ap.add_argument("--base-z", type=float, default=BASE_Z,
                    help="precision margin of the BASELINE rule, in standard errors. Default is "
                         "the adopted LCB z; 0 recovers the original plain-bar comparison.")
    ap.add_argument("--tail-kappa", type=float, default=0.422,
                    help="tail.py's reading at this cell floor, for the reproduction floor")
    ap.add_argument("--out", default="out/raise_kappa.json")
    a = ap.parse_args()
    rng = np.random.default_rng(SEED)
    BASE_Z = a.base_z

    rows = list(xes3g5m_rows(SCRATCH / "xes3g5m"))
    by_learner = timelines(rows)
    learners = sorted(by_learner)
    ft0, fp0, oat0 = states(by_learner)
    idx0 = at_item(ft0, oat0)
    items = sorted(idx0, key=lambda i: -len(idx0[i]))[:a.items]
    pairs = [(x, y) for x in items for y in items if x != y]
    print(f"XES3G5M: {len(learners):,} learners, {len(items)} items, {len(pairs):,} ordered pairs, "
          f"cell floor {a.min_cell}, {a.splits} splits")
    print(f"BASELINE IS LCB AT z = {BASE_Z}: assert when drop - {BASE_Z} x se > {BAR}. Every lever is")
    print(f"composed with that margin, so this asks what ADDS to the adopted rule, not what beats")
    print(f"the plain bar the programme no longer uses.")

    print("\nscoring real splits", flush=True)
    real = [s for s in (one_split(pairs, by_learner, learners, a.min_cell, rng)
                        for _ in range(a.splits)) if s]
    print(f"  {len(real)} usable splits, {len(real[0][0]):,} common pairs each")

    print("scoring DERANGED splits (the control)", flush=True)
    der = [s for s in (one_split(pairs, by_learner, learners, a.min_cell, rng, derange=True)
                       for _ in range(a.splits)) if s]
    print(f"  {len(der)} usable splits")

    # ---- FLOOR ------------------------------------------------------------
    print()
    print("FLOOR -- does the baseline rule reproduce tail.py's kappa?")
    k0, c0, ar0, _dg0 = score(real, "baseline", None)
    kd0, _, _, dgd0 = score(der, "baseline", None)
    print(f"      baseline kappa {k0:+.3f} (coverage {c0:.0%}, assert rate {ar0:.0%})")
    print(f"      tail.py at cell floor {a.min_cell}: {a.tail_kappa:+.3f}")
    print(f"      deranged baseline kappa {kd0:+.3f}  (must be ~0, and is the control's own check)")
    if abs(k0 - a.tail_kappa) > FLOOR_TOL:
        print(f"      NOTE: differs by {abs(k0 - a.tail_kappa):.3f}. This script splits learners in")
        print(f"      HALF where tail.py splits in THIRDS (it needs a third for unbiased selection,")
        print(f"      which this study does not), so more learners per half and a higher kappa is")
        print(f"      EXPECTED. That difference is itself the sample-size lever, quantified below.")
    print()
    print(f"      THE DERANGED BASELINE IS NOT ZERO, AND THAT IS A RESULT, NOT A BROKEN CONTROL.")
    print(f"      Crossing one learner's parent state onto another's dependant outcome destroys the")
    print(f"      learner-level dependency a prerequisite claim asserts, but it leaves ITEM-LEVEL")
    print(f"      structure standing: cell composition still tracks how hard the parent is, and the")
    print(f"      dependant's outcome still tracks how hard the dependant is. Both halves see that,")
    print(f"      so they agree about it. {kd0:+.3f} of the drop's {k0:+.3f} is exposure, not dependency.")
    print(f"      EVERY LEVER IS THEREFORE SCORED ON ITS EXCESS OVER ITS OWN DERANGED VALUE, not on")
    print(f"      raw kappa. A lever that lifts real and deranged together has bought nothing, and")
    print(f"      raw kappa cannot tell the difference.")
    print(f"      structure-attributable baseline: {k0 - kd0:+.3f}")

    # ---- the levers -------------------------------------------------------
    grid = {
        "lcb":     [0.25, 0.5, 1.0, 1.5, 2.0],
        "shrink":  [0.5, 1.0, 2.0, 4.0],
        "abstain": [0.25, 0.5, 1.0, 1.5],
        "bar":     [0.05, 0.10, 0.15, 0.20, 0.25],
    }
    print()
    print("=" * 78)
    print("THE LEVERS -- real corpus, deranged control, and coverage")
    print()
    print(f"  {'lever':<10} {'param':>6} {'kappa':>8} {'deranged':>9} {'EXCESS':>8} "
          f"{'vs base':>8} {'coverage':>9} {'assert':>7}  verdict")
    base_excess = k0 - kd0
    print(f"  {'baseline':<10} {'--':>6} {k0:+8.3f} {kd0:+9.3f} {base_excess:+8.3f} "
          f"{0.0:+8.3f} {c0:9.0%} {ar0:7.0%}")
    results = {"baseline": dict(param=None, kappa=k0, deranged=kd0, coverage=c0, assert_rate=ar0)}
    for lever, params in grid.items():
        for p in params:
            k, c, ar, dg = score(real, lever, p)
            kd, _, _, dgd = score(der, lever, p)
            excess = k - kd
            gain = excess - base_excess          # gain in STRUCTURE-ATTRIBUTABLE agreement
            # a lever that lifts the deranged arm as much as the real one has bought nothing
            # the REGISTERED rule (deranged above MAX_DERANGED), which the first run never applied,
            # and the relative rule it applied instead; either one rejects
            manufactured = registered_manufactured(kd) or relative_manufactured(k, kd, k0, kd0)
            real_gain = bool(gain >= MIN_GAIN and not manufactured and c >= MIN_COVERAGE)
            v = ("DEGENERATE" if dgd or dg else
                 "MANUFACTURED" if manufactured else
                 "REAL" if real_gain else
                 "thin coverage" if c < MIN_COVERAGE else "no gain")
            if dgd or dg:
                real_gain = False
            print(f"  {lever:<10} {p:>6.2f} {k:+8.3f} {kd:+9.3f} {excess:+8.3f} "
                  f"{gain:+8.3f} {c:9.0%} {ar:7.0%}  {v}")
            results[f"{lever}@{p}"] = dict(lever=lever, param=p, kappa=k, deranged=kd,
                                           excess=excess, coverage=c, assert_rate=ar, gain=gain,
                                           manufactured=manufactured, real=real_gain,
                                           degenerate_real=dg, degenerate_deranged=dgd)

    # ---- is it the rule, or the sample? -----------------------------------
    print()
    print("=" * 78)
    print("IS THE CEILING THE RULE OR THE SAMPLE? kappa against learners per half")
    curve = {}
    for frac in (0.15, 0.3, 0.5, 0.75, 1.0):
        n = max(200, int(len(learners) * frac))
        sub_keys = set(rng.choice(learners, min(n, len(learners)), replace=False))
        sub = {k: v for k, v in by_learner.items() if k in sub_keys}
        sub_learners = sorted(sub)
        sp = [s for s in (one_split(pairs, sub, sub_learners, a.min_cell, rng)
                          for _ in range(max(3, a.splits // 2))) if s]
        if not sp:
            continue
        k, c, _, _ = score(sp, "baseline", None)
        curve[frac] = dict(learners=len(sub_learners), per_half=len(sub_learners) // 2,
                           kappa=k, coverage=c)
        print(f"      {frac:>5.0%} of learners ({len(sub_learners) // 2:,} per half)  "
              f"kappa {k:+.3f}   coverage {c:.0%}")
    ks = [v["kappa"] for v in curve.values() if np.isfinite(v["kappa"])]
    slope = (ks[-1] - ks[0]) if len(ks) > 1 else float("nan")
    print(f"      -> kappa moves {slope:+.3f} across a {1 / 0.15:.0f}x change in learners")

    # ---- verdict ----------------------------------------------------------
    # RANK ON THE EFFECTIVE EDGE, NOT ON EXCESS. 1/kappa^2 prices the sample needed to DETECT a
    # gain and says nothing about how many edges the policy still acts on. A rule that abstains on
    # 35% of edges earns zero incremental value there, so ranking by excess alone crowns whichever
    # lever declines the most -- which is how an earlier reading of this study recommended
    # abstention. The comparable quantity is coverage x excess (see studies/outcomes/ope/abstention_value.py).
    for v in results.values():
        # The baseline row stores no "excess" of its own -- its excess IS kappa minus its deranged
        # arm, held separately. Reading v["excess"] blind made base_eff nan, which silently turned
        # every "C3 sample" cell into nanx and forced the no-lever-wins branch regardless of the
        # numbers. The verdict happened to be right; the arithmetic behind it was not.
        exc = v.get("excess")
        if exc is None and "kappa" in v and "deranged" in v:
            exc = v["kappa"] - v["deranged"]
        # STORED BACK, not just used. The first version of this fix computed the baseline's excess
        # locally and left the key absent, which was harmless only while base_eff was nan and the
        # baseline row was skipped by the isfinite filter below. Fixing base_eff made the row
        # reachable and the print raised KeyError on v["excess"] -- a crash the fix itself created,
        # after an hour of compute. A derived value the table prints belongs in the record.
        v["excess"] = exc
        v["effective"] = (v["coverage"] * exc
                          if exc is not None and np.isfinite(exc) else float("nan"))
    base_eff = results["baseline"]["effective"]
    assert np.isfinite(base_eff), "baseline effective edge must be finite to rank against"
    best = max((v for k, v in results.items() if k != "baseline" and v.get("real")
                and np.isfinite(v["effective"]) and v["effective"] > base_eff),
               key=lambda v: v["effective"], default=None)
    print()
    print("  EFFECTIVE EDGE (coverage x excess) -- what the policy actually acts on")
    for k, v in sorted(results.items(), key=lambda kv: -(kv[1].get("effective") or -9)):
        if not np.isfinite(v.get("effective", float("nan"))):
            continue
        print("    %-16s excess %+.3f  coverage %3.0f%%  effective %+.3f  C3 sample %s"
              % (k, v["excess"] if v["excess"] is not None else float("nan"),
                 100 * v["coverage"], v["effective"],
                 ("%.2fx" % (base_eff / v["effective"]) ** 2) if v["effective"] > 0 else "--"))
    print()
    print("=" * 78)
    print("VERDICT -- how do we raise kappa?")
    print()
    if best:
        print(f"  BEST REAL LEVER: {best['lever']} at {best['param']}. Structure-attributable")
        print(f"  agreement {best['excess']:+.3f} against a baseline {base_excess:+.3f} "
              f"({best['gain']:+.3f}), raw kappa {best['kappa']:+.3f},")
        print(f"  deranged {best['deranged']:+.3f}, coverage {best['coverage']:.0%}, EFFECTIVE EDGE")
        print(f"  {best['effective']:+.3f} against the baseline's {base_eff:+.3f}. At 1/kappa^2 on the")
        print(f"  EFFECTIVE figure that is a "
              f"{(base_eff / best['effective']) ** 2 if best['effective'] else float('nan'):.2f}x change in C3's sample.")
    else:
        print(f"  NO LEVER BEATS THE BASELINE ON THE EFFECTIVE EDGE ({base_eff:+.3f}). Every rule that")
        print(f"  raises STRUCTURE-ATTRIBUTABLE agreement does it by declining edges, and it declines")
        print(f"  more value than the extra precision returns. The decision rule is not what is")
        print(f"  holding kappa down -- abstention included, which is the lever that looks best on")
        print(f"  raw excess and loses once the edges it walks away from are counted.")
    manu = [k for k, v in results.items() if v.get("manufactured")]
    if manu:
        print()
        print(f"  MANUFACTURING AGREEMENT ({len(manu)} settings): {', '.join(sorted(manu)[:6])}")
        print(f"  These raise kappa on DERANGED data, where there is no structure to agree about.")
        print(f"  Without the deranged arm they would have looked like the answer.")
    print()
    if np.isfinite(slope):
        print(f"  AND THE SAMPLE IS {'NOT ' if abs(slope) < 0.05 else ''}THE CEILING: kappa moves "
              f"{slope:+.3f} across a 7x change in learners.")
        if abs(slope) < 0.05:
            print(f"  More learners will not fix this. The decision rule and the estimand are what")
            print(f"  is left, and C3's 1/kappa^2 penalty has to be paid or designed around.")

    out = dict(seed=SEED, items=a.items, splits=a.splits, min_cell=a.min_cell,
               bar=BAR, baseline=k0, deranged_baseline=kd0,
               levers=results, learner_curve=curve, learner_slope=slope,
               accept=dict(min_gain=MIN_GAIN, max_deranged=MAX_DERANGED,
                           min_coverage=MIN_COVERAGE))
    (HERE / "out").mkdir(exist_ok=True)
    Path(a.out).write_text(json.dumps(out, indent=2, default=float))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    if "--rescore" in sys.argv:
        from raise_kappa_finish import rescore
        rescore()
    elif "--curve" in sys.argv:
        from raise_kappa_finish import curve
        curve(corpus=sys.argv[sys.argv.index("--corpus") + 1] if "--corpus" in sys.argv else "xes3g5m")
    else:
        main()
