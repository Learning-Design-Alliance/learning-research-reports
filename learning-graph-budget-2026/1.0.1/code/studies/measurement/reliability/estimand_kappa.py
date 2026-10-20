"""Is an ORDER claim more reliable than a DROP claim, on the same pairs, at the same grain?

studies/outcomes/ope/c3_readiness.py made A5 the binding constraint on the north star, because a graph-derived
policy acts on the assay's output and C3's sample scales as 1/kappa^2. The cheapest imaginable way
to raise kappa is not a better estimator or more learners -- it is to CLAIM SOMETHING ELSE. A drop
says "meeting A first is worth +0.11 on B". An order statistic says only "A comes before B". The
second is a weaker claim, and weaker claims are easier to make reliably.

There is already an apparent answer on the board and IT IS NOT A VALID COMPARISON. course_grain.py
reads decision kappa +0.859 on an ORDER statistic, against tail.py's +0.438 on the DROP. Quoting
those two against each other was wrong and this script exists to replace that comparison, because
they differ on three things at once:

    corpus      MOOCCubeX against XES3G5M
    grain       course against knowledge-component
    estimand    order asymmetry against prerequisite drop

Only the third is the question. A reliability coefficient is a variance ratio, so it rises with the
SPREAD of whatever is ranked as well as with the precision of the instrument -- that is why A5's
own criterion text now names its estimand -- and an order share spreads across [0,1] where a drop
has sd about 0.07. Comparing across all three axes at once cannot separate any of them.

So both estimands are computed HERE on the same corpus, the same pairs, the same learners and the
same splits. Only the estimand changes.

    drop(a, b)   mean outcome at b among learners who passed a first,
                 minus mean outcome at b among learners who touched a and failed it
    order(a, b)  share of learners who touched BOTH of a and b who touched a first

THE CONTROL THAT DECIDES IT. Kappa is chance-corrected but it is NOT base-rate free: it depends on
how often the rule says yes. The drop asserts about 56% of pairs; an order statistic at its own
conventional bar asserts a quite different share, and comparing the two at their own bars would
confound estimand with assert rate. So each estimand's bar is TUNED to hit a matched assert rate,
and the comparison is made at several matched rates. A difference that survives matched assert
rates is about the estimand. One that does not was about the threshold.

Both estimands also run on LEARNER-DERANGED data -- a learner keeps their outcome and inherits
another learner's parent state -- because an estimand that scores high on deranged data is
measuring exposure, not structure. THAT RISK IS REAL AND SPECIFIC HERE: order asymmetry can be
carried entirely by what the platform made available when, which is why course_grain.py had to
regress it on release dates. At KC grain there is no release schedule to regress on, so the
derangement is the control that remains.

PRE-REGISTERED, before the run:

    floor      the drop's kappa must reproduce tail.py's reading at this cell floor, allowing for
               this script's half-splits against tail.py's third-splits.
    verdict    ORDER IS MORE RELIABLE      order beats drop by >= 0.05 at matched assert rates,
                                           with deranged order below 0.05
               NO ESTIMAND ADVANTAGE       it does not
               ORDER IS CONFOUNDED         deranged order exceeds 0.05, whatever the real number
    and       whichever way it goes, report the 1/kappa^2 consequence for C3.

DATA. XES3G5M from the session scratchpad. Only aggregates are written to out/.
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
DROP_BAR = 0.10
#: assert rates at which the two estimands are compared. The first is roughly what the drop does
#: at its own bar, so the comparison includes the operating point actually in use.
MATCHED_RATES = (0.55, 0.40, 0.25, 0.10)
MAX_DERANGED = 0.05
MIN_GAIN = 0.05


def stats_for(pairs, ft, fp, oat, idx, min_cell):
    """Both estimands for every readable pair, from one pass over the same learners."""
    out = {}
    for a, b in pairs:
        c = classify((a, b), ft, fp, oat, idx)
        m, f = np.asarray(c["mastered"], float), np.asarray(c["failed"], float)
        if len(m) < min_cell or len(f) < min_cell:
            continue
        drop = float(m.mean() - f.mean())
        # order: among learners who touched BOTH, the share who touched a first
        first, both = 0, 0
        for learner, tb, _y in idx[b]:
            ta = ft[learner].get(a)
            if ta is None:
                continue
            both += 1
            if ta < tb:
                first += 1
        if both < min_cell:
            continue
        out[(a, b)] = (drop, first / both)
    return out


def derange_history(ft, fp, rng):
    """Cross one learner's parent state onto another's dependant outcome. No fixed points.

    Remapping whole learner records is a NO-OP for an aggregate statistic -- it only relabels
    learners -- and it cost this study a wasted run before the floor caught it. What must break is
    the link classify() reads: `idx` keeps the learner's own outcome and touch time, while
    first_touch/first_pass come from someone else.
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
    return {k: ft[donor[k]] for k in keys}, {k: fp[donor[k]] for k in keys}


def one_split(pairs, by_learner, learners, min_cell, rng, derange=False):
    perm = rng.permutation(len(learners))
    half = len(perm) // 2
    parts = []
    for lo, hi in ((0, half), (half, len(perm))):
        side = {learners[i] for i in perm[lo:hi]}
        sub = {k: v for k, v in by_learner.items() if k in side}
        ft, fp, oat = states(sub)
        idx = at_item(ft, oat)
        if derange:
            ft, fp = derange_history(ft, fp, rng)
        parts.append(stats_for(pairs, ft, fp, oat, idx, min_cell))
    A, B = parts
    common = sorted(set(A) & set(B))
    if len(common) < 100:
        return None
    return (np.array([[A[p][0] for p in common], [A[p][1] for p in common]]),
            np.array([[B[p][0] for p in common], [B[p][1] for p in common]]))


def score_at_rate(splits, row, target, two_sided):
    """Kappa when each half's bar is set to assert `target` of its own pairs.

    Tuning the bar per half rather than globally is deliberate: a bar fixed on one half and applied
    to the other would import that half's noise into the other's decision and inflate agreement.
    """
    ks, rates = [], []
    for A, B in splits:
        dec = []
        for side in (A, B):
            v = side[row]
            s = np.abs(2 * v - 1) if two_sided else v
            if not np.isfinite(s).any():
                break
            thr = float(np.quantile(s, 1 - target))
            dec.append(s > thr)
        if len(dec) != 2:
            continue
        k = kappa(dec[0], dec[1])
        if np.isfinite(k):
            ks.append(k)
            rates.append(float(dec[0].mean()))
    if not ks:
        return float("nan"), float("nan")
    return float(np.mean(ks)), float(np.mean(rates))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", type=int, default=60)
    ap.add_argument("--splits", type=int, default=6)
    ap.add_argument("--min-cell", type=int, default=10)
    ap.add_argument("--tail-kappa", type=float, default=0.422)
    ap.add_argument("--out", default="out/estimand_kappa.json")
    a = ap.parse_args()
    rng = np.random.default_rng(SEED)

    rows = list(xes3g5m_rows(SCRATCH / "xes3g5m"))
    by_learner = timelines(rows)
    learners = sorted(by_learner)
    ft0, _fp0, oat0 = states(by_learner)
    idx0 = at_item(ft0, oat0)
    items = sorted(idx0, key=lambda i: -len(idx0[i]))[:a.items]
    pairs = [(x, y) for x in items for y in items if x != y]
    print(f"XES3G5M: {len(learners):,} learners, {len(items)} items, {len(pairs):,} ordered pairs, "
          f"cell floor {a.min_cell}, {a.splits} splits")
    print("both estimands from the SAME pairs, learners and splits -- only the estimand changes")

    real = [s for s in (one_split(pairs, by_learner, learners, a.min_cell, rng)
                        for _ in range(a.splits)) if s]
    print(f"\n  {len(real)} real splits, {real[0][0].shape[1]:,} common pairs each", flush=True)
    der = [s for s in (one_split(pairs, by_learner, learners, a.min_cell, rng, derange=True)
                       for _ in range(a.splits)) if s]
    print(f"  {len(der)} deranged splits", flush=True)

    # ---- FLOOR: the drop at its own fixed bar -----------------------------
    print()
    print("FLOOR -- does the DROP reproduce tail.py's kappa at its own fixed bar?")
    ks, ars = [], []
    for A, B in real:
        dec = [side[0] > DROP_BAR for side in (A, B)]
        k = kappa(dec[0], dec[1])
        if np.isfinite(k):
            ks.append(k); ars.append(float(dec[0].mean()))
    k_fixed, ar_fixed = float(np.mean(ks)), float(np.mean(ars))
    print(f"      drop at {DROP_BAR:+.2f}: kappa {k_fixed:+.3f}, assert rate {ar_fixed:.0%}")
    print(f"      tail.py at this cell floor: {a.tail_kappa:+.3f} (on THIRD-splits; this uses")
    print(f"      HALF-splits, so a higher reading here is expected, not a discrepancy)")

    # ---- the comparison, at matched assert rates --------------------------
    print()
    print("=" * 78)
    print("DROP AGAINST ORDER, AT MATCHED ASSERT RATES")
    print()
    print(f"  {'assert rate':>12} {'drop kappa':>11} {'order kappa':>12} {'gain':>8} "
          f"{'drop deranged':>14} {'order deranged':>15}")
    table = {}
    for target in MATCHED_RATES:
        kd, _ = score_at_rate(real, 0, target, two_sided=False)
        ko, _ = score_at_rate(real, 1, target, two_sided=True)
        kdd, _ = score_at_rate(der, 0, target, two_sided=False)
        kod, _ = score_at_rate(der, 1, target, two_sided=True)
        table[target] = dict(drop=kd, order=ko, gain=ko - kd,
                             drop_deranged=kdd, order_deranged=kod)
        print(f"  {target:>11.0%} {kd:>+11.3f} {ko:>+12.3f} {ko - kd:>+8.3f} "
              f"{kdd:>+14.3f} {kod:>+15.3f}")

    gains = [v["gain"] for v in table.values() if np.isfinite(v["gain"])]
    order_der = [v["order_deranged"] for v in table.values() if np.isfinite(v["order_deranged"])]
    mean_gain = float(np.mean(gains)) if gains else float("nan")
    worst_der = float(np.max(order_der)) if order_der else float("nan")
    confounded = bool(np.isfinite(worst_der) and worst_der > MAX_DERANGED)
    better = bool(np.isfinite(mean_gain) and mean_gain >= MIN_GAIN and not confounded)

    print()
    print("=" * 78)
    print("VERDICT")
    print()
    if confounded:
        print(f"  ORDER IS CONFOUNDED. Its deranged kappa reaches {worst_der:+.3f}, above the "
              f"{MAX_DERANGED:.2f} ceiling.")
        print(f"  Deranged data has no prerequisite structure left, so whatever order is agreeing")
        print(f"  about is EXPOSURE -- which items learners happen to meet first -- not dependency.")
        print(f"  course_grain.py had to regress course order on release dates for exactly this")
        print(f"  reason; at KC grain there is no release schedule to regress on, so this reading")
        print(f"  cannot be cleaned up the same way.")
    elif better:
        print(f"  ORDER IS MORE RELIABLE, by {mean_gain:+.3f} averaged over matched assert rates,")
        print(f"  with deranged order at most {worst_der:+.3f}.")
    else:
        print(f"  NO ESTIMAND ADVANTAGE at matched assert rates: mean gain {mean_gain:+.3f}.")
        print(f"  The +0.859-against-+0.438 gap on the board is therefore NOT the estimand. It is")
        print(f"  the corpus and the grain, which were varying at the same time.")
    print()
    best_d = max((v["drop"] for v in table.values() if np.isfinite(v["drop"])), default=float("nan"))
    best_o = max((v["order"] for v in table.values() if np.isfinite(v["order"])), default=float("nan"))
    print(f"  FOR C3, AT 1/kappa^2:")
    print(f"      best drop kappa  {best_d:+.3f}")
    print(f"      best order kappa {best_o:+.3f}"
          + ("   (CONFOUNDED -- not available)" if confounded else ""))
    if not confounded and np.isfinite(best_d) and np.isfinite(best_o) and best_d > 0:
        print(f"      switching estimand changes C3's sample by {(best_d / best_o) ** 2:.2f}x")
    print(f"      the assert rate that maximises the drop's kappa is worth noting on its own:")
    bestrate = max(table, key=lambda t: table[t]["drop"] if np.isfinite(table[t]["drop"]) else -9)
    print(f"      {bestrate:.0%} gives {table[bestrate]['drop']:+.3f} against {k_fixed:+.3f} at the "
          f"fixed +0.10 bar ({ar_fixed:.0%} assert)")

    out = dict(seed=SEED, items=a.items, splits=a.splits, min_cell=a.min_cell,
               drop_fixed_bar=dict(bar=DROP_BAR, kappa=k_fixed, assert_rate=ar_fixed),
               matched=table, mean_gain=mean_gain, worst_order_deranged=worst_der,
               order_confounded=confounded, order_better=better)
    (HERE / "out").mkdir(exist_ok=True)
    Path(a.out).write_text(json.dumps(out, indent=2, default=float))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
