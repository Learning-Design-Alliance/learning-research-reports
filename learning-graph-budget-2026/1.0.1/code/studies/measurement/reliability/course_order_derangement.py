"""Is MOOCCubeX's course-order reliability structure, or is it exposure?

course_grain.py reads Spearman-Brown +0.992 and decision kappa +0.859 on an ORDER statistic at
course grain -- the share of learners enrolled in both A and B who enrolled in A first. Those are
the best reliability numbers this programme has produced by a wide margin, and A5's criterion text
already refuses to count them because they are measured on a different estimand from the gate.

studies/measurement/reliability/estimand_kappa.py has now made that refusal look generous rather than pedantic. Run on
XES3G5M at KC grain, with both estimands on the same pairs, learners and splits and compared at
matched assert rates, the order statistic reaches kappa +0.98 -- AND REACHES +0.97 ON DERANGED
DATA, where every learner's parent state has been crossed onto another learner's dependant outcome
so no learner-level dependency survives. Essentially all of its reliability is item-level
presentation order. It agrees with itself about the curriculum, not about prerequisite structure.

THAT RESULT DOES NOT TRANSFER AUTOMATICALLY, WHICH IS WHY THIS SCRIPT EXISTS. XES3G5M's KC order is
set by a curriculum; MOOCCubeX enrolment is CHOSEN by the learner -- studies/identifiability/coarse-grain/register_order.py
established free enrolment and course-grain positivity holds on 3,532 of 3,540 pairs. A statistic
that is pure exposure where the platform dictates order may be something else where the learner
picks. So the same control is run here rather than the conclusion being carried across.

THE DERANGEMENT, AND WHAT IT DOES AND DOES NOT DESTROY. For a pair (A, B) the real statistic asks,
of learners enrolled in both, what share met A first. The deranged statistic compares a DONOR's
enrolment time for A against the learner's OWN enrolment time for B, under a derangement of
learners with no fixed points.

    it destroys   within-learner sequencing -- the thing "learners take A before B" asserts
    it preserves  every course's own enrolment-time distribution, exactly, because a derangement
                  permutes a column rather than altering it

So if the asymmetry survives, what it was measuring was WHEN EACH COURSE IS GENERALLY TAKEN -- when
it opened, when it is popular, where it sits in a programme -- and not any ordering the learners
themselves impose. course_grain.py already regressed the asymmetry on open-date gaps and found
R^2 = 0.001, but the release schedule is only ONE channel of exposure. This closes the general one.

PRE-REGISTERED, before the run:

    floor      the real arm must reproduce course_grain.py's published reading -- Spearman-Brown
               about +0.99 and decision kappa about +0.86 -- or this script is not measuring the
               thing it is auditing.
    verdict    EXPOSURE       deranged kappa stays within 0.10 of the real kappa. The statistic
                              agrees with itself about course timing; the learner-level ordering
                              contributes almost nothing, and the +0.859 on the board should not
                              be read as evidence about prerequisite structure.
               STRUCTURE      deranged kappa falls at least 0.30 below the real one, and the
                              remainder is learner-imposed ordering.
               PARTIAL        in between; report the structure-attributable excess and treat that,
                              not the raw figure, as what the estimand is worth.

    and in every case the number that matters downstream is the EXCESS, real minus deranged, since
    studies/outcomes/ope/c3_readiness.py showed C3's sample scales as 1/kappa^2 on whatever part of the agreement is
    actually about structure.

DATA. MOOCCubeX enrolment order from the session scratchpad. `user.json` was filtered at ingest --
name, gender, year_of_birth and school discarded at the door, leaving a pseudonymous id, the course
sequence and enrolment times. Only aggregates are written to out/.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2]))
sys.path.insert(0, str(HERE.parents[2] / "studies/identifiability/coarse-grain"))

from shared.stats import kappa  # noqa: E402
from register_order import SCRATCH, load  # noqa: E402
from course_grain import ASSERT_BAR, MIN_CELL, brown, spearman, time_matrix  # noqa: E402

SEED = 20260923
#: course_grain.py's published readings, for the reproduction floor
PUB_SB, PUB_KAPPA = 0.992, 0.859
FLOOR_TOL = 0.06
#: deranged within this of real -> the statistic is exposure
EXPOSURE_BAND = 0.10
#: deranged at least this far below real -> there is real structure in it
STRUCTURE_DROP = 0.30


def derange_rows(n, rng):
    """A permutation with no fixed points. An ordinary permutation leaves 1/n of the real
    pairing in place, which was enough to score a spurious p = 0.006 elsewhere in this
    programme."""
    if n < 2:
        return np.arange(n)
    while True:
        p = rng.permutation(n)
        if not np.any(p == np.arange(n)):
            return p


def asym_two(TA, TB, col, pairs, min_cell):
    """A-first share where A's time is read from TA and B's from TB.

    With TA is TB this is exactly course_grain.asym_of. With TA a deranged copy, it crosses a
    donor's enrolment time for A onto the learner's own for B.
    """
    out = {}
    for a, b in pairs:
        ta, tb = TA[:, col[a]], TB[:, col[b]]
        both = np.isfinite(ta) & np.isfinite(tb)
        if int(both.sum()) < min_cell:
            continue
        x, y = ta[both], tb[both]
        af, bf = int((x < y).sum()), int((x > y).sum())
        if af + bf >= min_cell:
            out[(a, b)] = (af / (af + bf), af + bf)
    return out


def split_arm(T, col, pairs, rng, splits, min_cell, derange=False):
    """Split-half Spearman / kappa, optionally with the donor derangement inside each half."""
    rs, ks, ns, cells = [], [], [], []
    for _ in range(splits):
        idx = rng.permutation(T.shape[0])
        h = T.shape[0] // 2
        sides = []
        for part in (idx[:h], idx[h:]):
            Th = T[part]
            TA = Th[derange_rows(Th.shape[0], rng)] if derange else Th
            sides.append(asym_two(TA, Th, col, pairs, min_cell))
        A, B = sides
        both = sorted(set(A) & set(B))
        if len(both) < 10:
            continue
        xa = np.array([A[p][0] for p in both])
        xb = np.array([B[p][0] for p in both])
        rs.append(spearman(xa, xb))
        ks.append(kappa(np.abs(2 * xa - 1) >= ASSERT_BAR, np.abs(2 * xb - 1) >= ASSERT_BAR))
        ns.append(len(both))
        cells.append(float(np.median([A[p][1] for p in both])))
    rs = [r for r in rs if np.isfinite(r)]
    ks = [k for k in ks if np.isfinite(k)]
    r = float(np.mean(rs)) if rs else float("nan")
    return dict(spearman=r, sb=brown(r),
                kappa=float(np.mean(ks)) if ks else float("nan"),
                pairs=int(np.median(ns)) if ns else 0,
                median_cell=float(np.median(cells)) if cells else float("nan"),
                assert_rate=float(np.mean([np.mean(np.abs(2 * np.array([A[p][0] for p in both]) - 1)
                                                   >= ASSERT_BAR)])) if ns else float("nan"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=60)
    ap.add_argument("--splits", type=int, default=8)
    ap.add_argument("--min-cell", type=int, default=MIN_CELL)
    ap.add_argument("--src", default=str(SCRATCH / "user-order.jsonl"))
    ap.add_argument("--out", default="out/course_order_derangement.json")
    a = ap.parse_args()
    rng = np.random.default_rng(SEED)

    print("IS COURSE-ORDER RELIABILITY STRUCTURE, OR EXPOSURE?\n", flush=True)
    seqs, keep, _pop, _first = load(a.src, a.top)
    items = sorted(keep)
    pairs = [(x, y) for x, y in itertools.combinations(items, 2)]
    print(f"mooccubex: {len(seqs):,} learners, {len(items)} courses, {len(pairs):,} unordered pairs",
          flush=True)
    T, col = time_matrix(seqs, items)
    print(f"  time matrix {T.shape[0]:,} x {T.shape[1]}", flush=True)

    # ---- FLOOR: reproduce the published reading ---------------------------
    print("\nFLOOR -- does the real arm reproduce course_grain.py?", flush=True)
    real = split_arm(T, col, pairs, rng, a.splits, a.min_cell, derange=False)
    print(f"      Spearman-Brown {real['sb']:+.3f}   (published {PUB_SB:+.3f})")
    print(f"      decision kappa {real['kappa']:+.3f}   (published {PUB_KAPPA:+.3f})")
    print(f"      {real['pairs']:,} pairs per split, median cell {real['median_cell']:,.0f}")
    ok = (abs(real["sb"] - PUB_SB) <= FLOOR_TOL and abs(real["kappa"] - PUB_KAPPA) <= FLOOR_TOL)
    if not ok:
        raise SystemExit(f"FLOOR FAILED: this does not reproduce the reading it is auditing "
                         f"(SB {real['sb']:+.3f} vs {PUB_SB}, kappa {real['kappa']:+.3f} vs "
                         f"{PUB_KAPPA}). Fix that before reading the deranged arm.")
    print("      -> REPRODUCED")

    # ---- the control ------------------------------------------------------
    print("\nDERANGED ARM -- donor's enrolment time for A against the learner's own for B",
          flush=True)
    der = split_arm(T, col, pairs, rng, a.splits, a.min_cell, derange=True)
    print(f"      Spearman-Brown {der['sb']:+.3f}")
    print(f"      decision kappa {der['kappa']:+.3f}")
    print(f"      {der['pairs']:,} pairs per split, median cell {der['median_cell']:,.0f}")

    gap_k = real["kappa"] - der["kappa"]
    gap_r = real["sb"] - der["sb"]
    print()
    print("=" * 78)
    print(f"  {'':<22}{'real':>10}{'deranged':>11}{'excess':>10}")
    print(f"  {'Spearman-Brown':<22}{real['sb']:>+10.3f}{der['sb']:>+11.3f}{gap_r:>+10.3f}")
    print(f"  {'decision kappa':<22}{real['kappa']:>+10.3f}{der['kappa']:>+11.3f}{gap_k:>+10.3f}")

    if np.isfinite(gap_k) and gap_k <= EXPOSURE_BAND:
        verdict = "EXPOSURE"
    elif np.isfinite(gap_k) and gap_k >= STRUCTURE_DROP:
        verdict = "STRUCTURE"
    else:
        verdict = "PARTIAL"

    print()
    print("VERDICT:", verdict)
    print()
    if verdict == "EXPOSURE":
        print(f"  Crossing learners costs the statistic almost nothing ({gap_k:+.3f} of kappa), so what")
        print(f"  it agrees about is WHEN EACH COURSE IS GENERALLY TAKEN, not any order the learners")
        print(f"  impose. The +{PUB_KAPPA:.3f} on the board is not evidence about prerequisite structure,")
        print(f"  and the open-date regression that cleared it (R^2 = 0.001) ruled out one exposure")
        print(f"  channel while the general one went unmeasured. THE COURSE-GRAIN ROUTE TO A5 IS SHUT")
        print(f"  for the same reason the KC-grain order estimand is: both are reading the catalogue.")
    elif verdict == "STRUCTURE":
        print(f"  Crossing learners costs {gap_k:+.3f} of kappa, so most of the agreement IS learner-imposed")
        print(f"  ordering rather than course timing. Unlike XES3G5M at KC grain -- where the same")
        print(f"  control left the order statistic at +0.97 on deranged data -- free enrolment makes")
        print(f"  this estimand carry something real. Structure-attributable kappa {gap_k:+.3f}.")
    else:
        print(f"  Part of it survives crossing learners and part does not. The structure-attributable")
        print(f"  figure is {gap_k:+.3f}, not {real['kappa']:+.3f}, and that is what any downstream use has to quote.")
    print()
    print(f"  FOR C3, AT 1/kappa^2 ON THE STRUCTURE-ATTRIBUTABLE FIGURE:")
    print(f"      raw course-grain kappa    {real['kappa']:+.3f}")
    print(f"      structure-attributable    {gap_k:+.3f}")
    if np.isfinite(gap_k) and gap_k > 0:
        print(f"      reading the raw figure understates C3's sample by "
              f"{(real['kappa'] / gap_k) ** 2:.1f}x")

    out = dict(seed=SEED, top=a.top, splits=a.splits, min_cell=a.min_cell,
               learners=len(seqs), courses=len(items),
               real=real, deranged=der, kappa_excess=gap_k, sb_excess=gap_r,
               verdict=verdict, published=dict(sb=PUB_SB, kappa=PUB_KAPPA))
    (HERE / "out").mkdir(exist_ok=True)
    Path(a.out).write_text(json.dumps(out, indent=2, default=float))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
