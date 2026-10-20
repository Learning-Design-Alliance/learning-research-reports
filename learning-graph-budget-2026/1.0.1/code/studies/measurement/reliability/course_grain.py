"""A5 AT COURSE GRAIN -- and the estimand changes, which is the first thing to say.

`TAIL.md` closed two explanations for A5's failure. The corpus explanation went when XES3G5M and
EdNet were both measured; the sparsity explanation went when the asserted tail came back LESS
reliable than the bulk (+0.654 against +0.743). A5's remaining route was to AGGREGATE THE UNIT:
reliability is a property of the edge statistic, and `studies/identifiability/coarse-grain/register_order.py` showed course
grain carries a median identifying cell of 18,783 learners against KC-grain cells in the hundreds.
Bigger cells, less sampling noise, better reliability -- that is the hypothesis.

THE ESTIMAND IS NOT THE SAME ONE, AND NO AMOUNT OF CARE MAKES IT THE SAME. At KC grain the edge
statistic is a DROP -- does holding A raise success at B. MOOCCubeX has no usable outcomes at course
grain: streaming its 21 GB user-problem log kept 33,856 records from 133,384,333 rows, because the
problem-to-course map covers only 10,509 problems. So what can be measured here is ORDER, not
performance:

    asym(A, B) = share of learners enrolled in BOTH who enrolled in A first

That is an edge statistic and it does rank edges, so A5's question -- "run it twice on split data,
does it say the same thing" -- is askable of it. But a reliability computed on an ORDER statistic is
not interchangeable with one computed on a DROP, and A5's 0.80 gate was set for the latter. Every
number below carries that.

WHY HIGH RELIABILITY HERE WOULD BE THE EASIEST KIND TO MISREAD. `register_order.py` already flagged
that order asymmetry carries a COURSE-AVAILABILITY confound: if A was published before B, every
learner takes A first whatever the relation between them. A release schedule is extremely STABLE, so
a statistic driven by it would be almost perfectly RELIABLE and entirely INVALID. Reliability is not
validity, and at this grain the two come apart in the most flattering possible direction. The
open-date control below exists for exactly that, and it is the reading that matters.

    OPEN-DATE CONTROL   each course's first observed enrolment stands in for its availability. The
                        asymmetry is regressed on the sign and size of the pair's open-date gap, and
                        the RESIDUAL is put through the same split-half machinery. If reliability
                        survives on the residual, something other than the catalogue is being
                        measured; if it collapses, the catalogue is the whole of it.

A SECOND CONTROL, ADDED BEFORE THE FULL RUN BECAUSE A SMOKE TEST RETURNED SPEARMAN-BROWN 0.996 AND A
NUMBER THAT GOOD IS A REASON TO LOOK HARDER, NOT TO STOP. A reliability coefficient is a variance
ratio -- true variance over true plus error -- so it rises when the ERROR shrinks AND when the TRUE
SPREAD grows, and those are different claims. A5's route was the first: aggregate the unit, get cells
of thousands instead of hundreds, shrink the error. But this estimand also has far more between-pair
spread than a drop does: course-order asymmetry ranges across the whole [0,1] interval while a KC
drop has a standard deviation of 0.07 (`TAIL.md`). A high number here could be the cells or it could
be the spread, and only one of those is A5's hypothesis.

    CELL LADDER   the same measurement on learner subsamples chosen to put the median cell at
                  roughly 30, 100, 300, 1,000 and the full depth. If reliability holds up at
                  KC-grain cell sizes, the gain is the estimand's spread and NOT the aggregation,
                  and A5's route has not actually been walked.

PRE-REGISTERED VERDICTS, written before the run:

  RELIABLE AND NOT THE CATALOGUE   Spearman-Brown >= 0.80 raw AND >= 0.80 on the open-date residual.
                                   Aggregating the unit rescues A5, and the estimand swap is then
                                   the thing to argue about rather than the number.
  RELIABLE BUT IT IS THE CATALOGUE raw >= 0.80, residual below it. The instrument is measuring
                                   XuetangX's release schedule, reliably. This is the outcome the
                                   confound predicts and it is not a pass.
  NOT RELIABLE                     raw < 0.80. Bigger cells did not do it, and the unit-aggregation
                                   route out of A5 is closed like the other two.

Reads MOOCCubeX enrolment order. PRIVACY: the ingest discarded `name`, `gender`, `year_of_birth` and
`school` at the door; only pseudonymous id, course sequence and enrolment times were ever kept. Raw
exports stay in the session scratchpad; only aggregates are committed.

    python3 course_grain.py [--top 60] [--splits 12] [--min-cell 30]

DIRECTION: symmetric -- reversing every pair maps the A-first share p to 1 - p in both halves and
flips the open-date gap with it, so the split-half Spearman and the open-date residual's reliability
are unchanged.

Direction declaration added 2026-09-24 (reversed-arrow rule, shared/experimental-contract.md):
nothing reported depends on edge orientation, so no reversed-arrow control applies.
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

from shared.stats import kappa, rank  # noqa: E402
from register_order import SCRATCH, load  # noqa: E402

SEED = 20260922
#: A5's gate, carried over unchanged so the comparison is visible even though the estimand is not
GATE = 0.80
#: co-enrollers needed in EACH half before a pair is read
MIN_CELL = 30
#: |2p-1| above this and the pair would be asserted as ordered -- the tail, as in tail.py
ASSERT_BAR = 0.30


def spearman(x, y):
    """Tie-safe Spearman. `shared.stats.rank` rather than argsort-of-argsort, which ranks ties by
    array position and is the idiom `shared/check_idioms.py` exists to stop."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3:
        return float("nan")
    rx, ry = rank(x), rank(y)
    if rx.std() == 0 or ry.std() == 0:
        return float("nan")
    return float(np.corrcoef(rx, ry)[0, 1])


def brown(r):
    return (2 * r) / (1 + r) if np.isfinite(r) and r > -1 else float("nan")


def time_matrix(seqs, items):
    """(learners x courses) of first enrolment time in days, NaN where the learner never enrolled.

    THE PAIR LOOP HAS TO BE A MATRIX OR THIS DOES NOT FINISH. The first version walked every learner
    and every pair in Python: 541,452 x 1,770 is 958 million iterations for ONE reading, and a
    split-half over 12 splits needs 24 of them plus a ladder. Built once as an array, a pair is two
    column comparisons and the whole thing is seconds.
    """
    col = {c: j for j, c in enumerate(items)}
    epoch = np.datetime64("2015-01-01T00:00:00")
    T = np.full((len(seqs), len(items)), np.nan)
    for i, pr in enumerate(seqs):
        for c, t in pr:
            j = col.get(c)
            if j is None:
                continue
            try:
                d = float((np.datetime64(str(t).replace(" ", "T")) - epoch)
                          / np.timedelta64(1, "D"))
            except Exception:
                continue
            if np.isnan(T[i, j]) or d < T[i, j]:
                T[i, j] = d
    return T, col


def asym_of(T, col, pairs, min_cell):
    """A-first share per ordered pair, over the learner rows present in T.

    ONE ORIENTATION PER UNORDERED PAIR. `register_order.py` reported a median A-first share of
    exactly 0.500 before this was fixed: every unordered pair appeared twice with complementary
    shares, so the median was pinned at 0.5 by construction whatever the data said.
    """
    out = {}
    for a, b in pairs:
        ta, tb = T[:, col[a]], T[:, col[b]]
        both = np.isfinite(ta) & np.isfinite(tb)
        if int(both.sum()) < min_cell:
            continue
        x, y = ta[both], tb[both]
        af = int((x < y).sum())
        bf = int((x > y).sum())
        if af + bf >= min_cell:
            out[(a, b)] = (af / (af + bf), af + bf)
    return out


def split_reliability(T, col, pairs, rng, splits, min_cell, adjust=None):
    """Spearman-Brown of the pair statistic across random halves of the LEARNERS.

    `adjust` optionally maps pair -> a value to subtract, which is how the open-date residual is put
    through the identical machinery rather than a parallel one.
    """
    rs, ns, ks = [], [], []
    for _ in range(splits):
        idx = rng.permutation(T.shape[0])
        h = T.shape[0] // 2
        A = asym_of(T[idx[:h]], col, pairs, min_cell)
        B = asym_of(T[idx[h:]], col, pairs, min_cell)
        both = sorted(set(A) & set(B))
        if len(both) < 10:
            continue
        xa = np.array([A[p][0] for p in both])
        xb = np.array([B[p][0] for p in both])
        if adjust is not None:
            adj = np.array([adjust.get(p, 0.0) for p in both])
            xa, xb = xa - adj, xb - adj
        rs.append(spearman(xa, xb))
        ks.append(kappa(np.abs(2 * xa - 1) >= ASSERT_BAR, np.abs(2 * xb - 1) >= ASSERT_BAR))
        ns.append(len(both))
    rs = [r for r in rs if np.isfinite(r)]
    ks = [k for k in ks if np.isfinite(k)]
    if not rs:
        return float("nan"), float("nan"), 0, float("nan")
    r = float(np.mean(rs))
    return r, brown(r), int(np.median(ns)), (float(np.mean(ks)) if ks else float("nan"))


def opendate_fit(asym, first_seen):
    """Least-squares fit of the asymmetry on the pair's open-date gap; returns the fitted values.

    The catalogue's prediction for a pair is "whichever course opened first is taken first", and its
    strength should grow with the gap. Both the sign and the size are given to the fit, so the
    residual is what remains after the schedule has been allowed to explain as much as it can.
    """
    ps = sorted(asym)
    gaps = []
    for a, b in ps:
        ta, tb = first_seen.get(a), first_seen.get(b)
        if ta is None or tb is None:
            gaps.append(0.0)
            continue
        d = (np.datetime64(tb.replace(" ", "T")) - np.datetime64(ta.replace(" ", "T")))
        gaps.append(float(d / np.timedelta64(1, "D")))
    g = np.array(gaps)
    y = np.array([asym[p][0] for p in ps])
    X = np.stack([np.ones_like(g), np.sign(g), np.clip(g, -400, 400) / 400.0], 1)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    fit = X @ beta
    ss = float(1 - ((y - fit) ** 2).sum() / max(((y - y.mean()) ** 2).sum(), 1e-12))
    return {p: float(f - beta[0]) for p, f in zip(ps, fit)}, ss, g, y


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=60)
    ap.add_argument("--splits", type=int, default=12)
    ap.add_argument("--min-cell", type=int, default=MIN_CELL)
    ap.add_argument("--src", default=str(SCRATCH / "user-order.jsonl"))
    ap.add_argument("--out", default="out/course_grain.json")
    args = ap.parse_args()
    rng = np.random.default_rng(SEED)

    print("A5 AT COURSE GRAIN -- bigger cells, and a different estimand\n", flush=True)
    seqs, keep, pop, first_seen = load(args.src, args.top)
    items = sorted(keep)
    pairs = [(a, b) for a, b in itertools.combinations(items, 2)]
    print(f"mooccubex: {len(seqs):,} learners with at least one of the top {len(items)} courses, "
          f"{len(pairs):,} unordered pairs", flush=True)

    T, col = time_matrix(seqs, items)
    full = asym_of(T, col, pairs, args.min_cell)
    ns = np.array([n for _, n in full.values()])
    print(f"  {len(full):,} pairs readable at a floor of {args.min_cell} co-enrollers; "
          f"median cell {int(np.median(ns)):,}, p10 {int(np.percentile(ns,10)):,}, "
          f"max {int(ns.max()):,}", flush=True)
    print(f"  (KC grain for comparison: reliability/TAIL.md reads cells in the hundreds)")

    readable = sorted(full)
    raw_r, raw_sb, npairs, raw_k = split_reliability(T, col, readable, rng, args.splits,
                                                     args.min_cell)
    print(f"\n  RAW        Spearman {raw_r:+.3f}  ->  Spearman-Brown {raw_sb:+.3f}  "
          f"over {npairs:,} pairs per split")
    print(f"             DECISION KAPPA {raw_k:+.3f}  (the proposed A5 replacement, on the "
          f"assert/do-not decision at |2p-1| >= {ASSERT_BAR})")

    fit, ss, gaps, ys = opendate_fit(full, first_seen)
    print(f"\n  OPEN-DATE CONTROL: the release schedule explains R^2 = {ss:.3f} of the asymmetry "
          f"across {len(full):,} pairs")
    res_r, res_sb, nres, res_k = split_reliability(T, col, readable, rng, args.splits,
                                                   args.min_cell, adjust=fit)
    print(f"  RESIDUAL   Spearman {res_r:+.3f}  ->  Spearman-Brown {res_sb:+.3f}")

    # the asserted tail, same three-way logic as tail.py: select in S, measure in A and B
    idx = rng.permutation(T.shape[0])
    third = T.shape[0] // 3
    S, AB = T[idx[:third]], T[idx[third:]]
    selA = asym_of(S, col, readable, args.min_cell)
    tail = [p for p, (v, _n) in selA.items() if abs(2 * v - 1) >= ASSERT_BAR]
    held = asym_of(AB, col, tail, args.min_cell) if tail else {}
    repl = (sum(1 for p in held if abs(2 * held[p][0] - 1) >= ASSERT_BAR) / len(held)) if held else float("nan")
    base = (sum(1 for p, (v, _n) in full.items() if abs(2 * v - 1) >= ASSERT_BAR) / len(full)) if full else float("nan")
    print(f"\n  ASSERTED TAIL (|2p-1| >= {ASSERT_BAR}): {len(tail):,} pairs selected in S, "
          f"{len(held):,} readable out of sample")
    print(f"    replication {repl:.1%}  against a base rate of {base:.1%}"
          + (f"  ({repl/base:.2f}x)" if np.isfinite(repl) and base > 0 else ""))

    # --- cell ladder: is this bigger cells, or a wider-spread statistic?
    print(f"\n  CELL LADDER -- reliability against cell depth, to separate the two explanations:")
    ladder = []
    for frac in (0.01, 0.03, 0.10, 0.33, 1.00):
        n_sub = max(int(T.shape[0] * frac), 400)
        sub = T[rng.choice(T.shape[0], min(n_sub, T.shape[0]), replace=False)]
        got = asym_of(sub, col, readable, args.min_cell)
        if len(got) < 10:
            continue
        med = int(np.median([n for _, n in got.values()]))
        r_, sb_, np_, k_ = split_reliability(sub, col, sorted(got), rng, max(args.splits // 2, 3),
                                             args.min_cell)
        ladder.append(dict(learners=int(sub.shape[0]), median_cell=med, pairs=np_,
                           spearman=r_, sb=sb_, kappa=k_))
        print(f"    {sub.shape[0]:>7,} learners   median cell {med:>6,}   {np_:>5,} pairs   "
              f"Spearman-Brown {sb_:+.3f}   decision kappa {k_:+.3f}")
    small = [x for x in ladder if x["median_cell"] <= 400]
    cells_explain = bool(small and small[0]["sb"] < GATE)
    if small:
        print(f"    -> at a KC-grain cell depth of {small[0]['median_cell']:,} this statistic reads "
              f"{small[0]['sb']:+.3f}, so the headline is "
              f"{'THE AGGREGATION' if cells_explain else 'THE ESTIMAND, NOT THE AGGREGATION'}")

    print(f"\n  DOES THE PROPOSED REPLACEMENT DISCRIMINATE? The rank correlation reads "
          f"{raw_sb:+.3f} on this statistic and {0.654:+.3f} on a KC-grain drop. Decision kappa "
          f"reads {raw_k:+.3f} here.")
    print(f"    -> " + ("kappa is ALSO near-perfect, so it does not separate the two and the "
                        "replacement fixes nothing" if raw_k >= 0.90 else
                        "kappa is materially lower than the correlation, so it is NOT simply "
                        "rewarding the estimand's spread -- the replacement is worth measuring "
                        "at KC grain"))

    verdict = ("NOT RELIABLE" if not (raw_sb >= GATE) else
               "RELIABLE AND NOT THE CATALOGUE" if res_sb >= GATE else
               "RELIABLE BUT IT IS THE CATALOGUE")
    print(f"\nVERDICT: {verdict}")
    if verdict == "RELIABLE BUT IT IS THE CATALOGUE":
        print(f"  the raw {raw_sb:.3f} clears the {GATE:.2f} gate and the residual {res_sb:.3f} does "
              f"not. A release schedule is stable, so a statistic driven by it replicates almost "
              f"perfectly and means almost nothing. This is the outcome the confound predicts.")
    elif verdict == "NOT RELIABLE":
        print(f"  {raw_sb:.3f} against a {GATE:.2f} gate. Aggregating the unit gave cells "
              f"{int(np.median(ns)):,} learners deep and did not rescue A5, so that route closes "
              f"alongside the corpus and sparsity explanations.")
    else:
        print(f"  raw {raw_sb:.3f} and residual {res_sb:.3f} both clear {GATE:.2f}, and the "
              f"release schedule explains only R^2 = {ss:.3f}, so this is not the catalogue.")
        if small and not cells_explain:
            print(f"  BUT THE CELL LADDER SAYS IT IS NOT A5'S ROUTE EITHER: at a KC-grain cell "
                  f"depth of {small[0]['median_cell']:,} the same statistic still reads "
                  f"{small[0]['sb']:+.3f}. The gain is the ESTIMAND -- an order share spreads across "
                  f"[0,1] where a drop has sd 0.07 -- not the aggregation A5 was pointed at.")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(
        seed=SEED, top=args.top, splits=args.splits, min_cell=args.min_cell, gate=GATE,
        learners=len(seqs), pairs_total=len(pairs), pairs_readable=len(full),
        cell_median=int(np.median(ns)), cell_p10=int(np.percentile(ns, 10)), cell_max=int(ns.max()),
        raw_spearman=raw_r, raw_sb=raw_sb, raw_kappa=raw_k, opendate_r2=ss,
        residual_spearman=res_r, residual_sb=res_sb,
        assert_bar=ASSERT_BAR, tail_selected=len(tail), tail_readable=len(held),
        tail_replication=repl, base_rate=base, ladder=ladder,
        cells_explain=cells_explain, verdict=verdict,
        kappa_discriminates=bool(np.isfinite(raw_k) and raw_k < 0.90)), indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
