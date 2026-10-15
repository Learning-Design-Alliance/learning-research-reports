"""Is the pairwise structure `lowrank.py` found DIRECTIONAL, or only relatedness?

`lowrank.py` established that XES3G5M's edge matrix holds replicable pairwise structure: after the
additive margins AND the leading multiplicative one are removed, the residual still replicates
across learner halves at +0.319 against a margin-matched null of -0.005. That is a real finding and
it answers the pooling family's question -- there IS something beyond node effects to recover.

It does NOT say the something is a prerequisite. The edge matrix is directional by CONSTRUCTION --
M[a,b] is the outcome gap on b between learners who mastered a and learners who failed it -- but a
quantity being directional in its definition is not the same as its SIGNAL being directional. Two
items on the same topic will show a mutual gap in both directions for reasons that have nothing to
do with order.

So split the residual into the only two parts it can have:

    S = (R + R^T) / 2     SYMMETRIC     -- a and b are related. Relatedness, similarity, co-teaching.
    A = (R - R^T) / 2     ANTISYMMETRIC -- a helps b MORE than b helps a. This, and only this, is
                                           the part a prerequisite claim can live in.

and ask which of them replicates across learner halves. The decomposition is exhaustive and
orthogonal: R = S + A always, and no pairwise signal can hide outside the two.

WHY THE ANSWER IS NOT OBVIOUS IN ADVANCE, AND WHY THIS PROGRAMME EXPECTS SYMMETRY. Two independent
measurements here already point the same way. `studies/identifiability/taxonomy-order/` found XES3G5M's expert hierarchy
INERT for ordering -- ancestor-minus-descendant -0.0128, so containment carries no direction -- while
still carrying magnitude, with siblings dropping more than cross-root pairs by +0.0161
[+0.0109, +0.0218]. `studies/producers/direction-benchmark/` found a text proposer recovers GENERALITY rather than
prerequisite, and fails to beat a content-free degree rule on the honest direction subset. If the
+0.319 is relatedness, both of those are the same fact seen from a third angle.

THE FLOOR COMES FIRST. A planted antisymmetric component must be recovered, and a purely symmetric
matrix must NOT produce an antisymmetric replication, or the arms are not separable and no real
number is read.

PRE-REGISTERED VERDICTS, written before any real number was read:

  DIRECTIONAL          the ANTISYMMETRIC part replicates above its margin-matched null. Prerequisite
                       structure is present in the residual and the pooling family can reach it.
  RELATEDNESS ONLY     the symmetric part replicates and the antisymmetric part does not. The
                       structure lowrank.py found is real and is NOT about order, which also
                       explains taxonomy-order and direction-benchmark without either being wrong.
  BOTH                 both replicate. Then the antisymmetric share is the number that matters and
                       is reported as the fraction of residual variance carrying direction.
  NEITHER              the decomposition destroys the signal, which would mean the +0.319 lives in
                       cells whose transpose is unobserved -- a coverage artefact, not structure.

Reads EdNet (CC BY-NC 4.0 -- non-commercial, no model training) and XES3G5M, exactly as lowrank.py
does. Raw exports stay in the session scratchpad; only the aggregate is committed.

    python3 antisymmetry.py --floor-only
    python3 antisymmetry.py [--splits 8]

DIRECTION: symmetric -- split-half replication of the antisymmetric part is unchanged by transposing
both halves (A becomes -A in each), and M[a, b] is defined from each learner's timeline, not from an
authored arrow.

Direction declaration added 2026-09-24 (reversed-arrow rule, shared/experimental-contract.md):
nothing reported depends on edge orientation, so no reversed-arrow control applies.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "studies/identifiability/overlap"))
sys.path.insert(0, str(HERE.parents[2] / "studies/measurement/reliability"))

from lowrank import (MIN_PER_ITEM, SEED, additive, deflate, edge_matrix,  # noqa: E402
                     margin_matched_null)
from atlas import ednet_rows, xes3g5m_rows  # noqa: E402
from positivity import SCRATCH, at_item, states, timelines  # noqa: E402
from split_half import spearman  # noqa: E402

#: the residual is read after the additive margins AND the multiplicative one are gone, which is the
#: arm lowrank.py reports as the honest pairwise number
DEFLATE_K = 1
#: a pair enters only when ALL FOUR of MA[i,j], MA[j,i], MB[i,j], MB[j,i] are observed -- the
#: decomposition is undefined on a half-observed pair, and filling the transpose with zero would
#: manufacture antisymmetry out of missingness
MIN_PAIRS = 60


def sym_anti(R, both):
    """The symmetric and antisymmetric parts, on cells whose transpose is also observed."""
    X = np.where(both, R, 0.0)
    return (X + X.T) / 2.0, (X - X.T) / 2.0


def compare(MA, MB, rng):
    """Split-half replication of each part, against the same margin-matched null lowrank.py uses."""
    obs = (~np.isnan(MA)) & (~np.isnan(MB))
    both = obs & obs.T                      # the pair AND its transpose, in both halves
    iu = np.triu(np.ones_like(both, bool), 1) & both
    if iu.sum() < MIN_PAIRS:
        return None

    def parts(M):
        return sym_anti(deflate(M - additive(M), DEFLATE_K), both)

    SA, AA = parts(MA)
    SB, AB = parts(MB)
    nSA, nAA = parts(margin_matched_null(MA, rng))
    nSB, nAB = parts(margin_matched_null(MB, rng))

    # how the residual's energy divides, averaged over the two halves
    share = []
    for S, A in ((SA, AA), (SB, AB)):
        es, ea = float((S[iu] ** 2).sum()), float((A[iu] ** 2).sum())
        share.append(ea / (es + ea) if (es + ea) > 0 else np.nan)

    return dict(pairs=int(iu.sum()),
                sym=spearman(SA[iu], SB[iu]), sym_null=spearman(nSA[iu], nSB[iu]),
                anti=spearman(AA[iu], AB[iu]), anti_null=spearman(nAA[iu], nAB[iu]),
                anti_share=float(np.nanmean(share)))


# ---------------------------------------------------------------- the detection floor

def planted(n, kind, rng, *, noise=0.35, strength=1.0, miss=0.15):
    """Two halves of a matrix built from a KNOWN structure, with node margins on top.

    `kind` is what is planted under the margins:
      "anti"   an antisymmetric component from a random DAG: A[i,j] = +1 where i precedes j, -1
               where j precedes i, 0 for incomparable pairs.

               THE FIRST VERSION OF THIS GENERATOR WAS WRONG AND THE FLOOR CAUGHT IT. It planted
               A[i,j] = s_i - s_j from a latent score per item, which LOOKS antisymmetric but is
               exactly a_i + b_j with a_i = s_i and b_j = -s_j -- an ADDITIVE MARGIN. `additive()`
               removed it before the decomposition ever saw it, and the planted arm read +0.004
               against a null of -0.008. That is not a weak instrument, it is a true statement about
               the estimand, and it is worth keeping in view: A PREREQUISITE THAT ACTS AS A PURE
               SKILL-DIFFERENCE IS INDISTINGUISHABLE FROM NODE EFFECTS BY CONSTRUCTION, and no
               amount of pooling recovers it. Only an order that is NOT a total ranking -- one with
               incomparable pairs -- leaves an antisymmetric residue behind the margins.
      "sym"    a symmetric component from latent positions: S[i,j] = -|z_i - z_j|. Relatedness.
      "none"   margins only, so neither part should replicate.
    Both halves see the SAME planted structure and INDEPENDENT noise, which is exactly what a
    split-half asks of real data.
    """
    a, b = rng.normal(0, 0.4, n), rng.normal(0, 0.4, n)
    base = a[:, None] + b[None, :]
    if kind == "anti":
        # a random DAG on a shuffled order, sparse enough to leave incomparable pairs
        order = rng.permutation(n)
        rank = np.empty(n, int)
        rank[order] = np.arange(n)
        before = rank[:, None] < rank[None, :]
        linked = rng.random((n, n)) < 0.25
        linked = linked | linked.T
        core = strength * np.where(before & linked, 1.0, 0.0)
        core = core - core.T
    elif kind == "sym":
        z = rng.normal(0, 1.0, n)
        core = -strength * np.abs(z[:, None] - z[None, :])
    else:
        core = np.zeros((n, n))
    out = []
    for _ in range(2):
        M = base + core + rng.normal(0, noise, (n, n))
        np.fill_diagonal(M, np.nan)
        M[rng.random((n, n)) < miss] = np.nan
        out.append(M)
    return out


def floor(reps, n, rng):
    print("DETECTION FLOOR -- can the decomposition tell a planted direction from a planted "
          "relatedness?\n")
    out = {}
    for kind in ("anti", "sym", "none"):
        acc = []
        for _ in range(reps):
            MA, MB = planted(n, kind, rng)
            got = compare(MA, MB, rng)
            if got:
                acc.append(got)
        if not acc:
            continue
        g = lambda k: float(np.nanmean([x[k] for x in acc]))  # noqa: E731
        out[kind] = dict(n=len(acc), sym=g("sym"), sym_null=g("sym_null"),
                         anti=g("anti"), anti_null=g("anti_null"), anti_share=g("anti_share"))
        print(f"  planted {kind:5s}  symmetric {g('sym'):+.3f} (null {g('sym_null'):+.3f})   "
              f"antisymmetric {g('anti'):+.3f} (null {g('anti_null'):+.3f})   "
              f"anti share of energy {g('anti_share'):.2f}")

    #: a bare ">" is not a floor -- the first generator passed that way at +0.004 while recovering
    #: nothing. The planted arm must clear its null BY A MARGIN and must beat the empty world too.
    MIN_RECOVERY, MIN_SEPARATION = 0.15, 0.10
    ok_anti = (out["anti"]["anti"] - out["anti"]["anti_null"] > MIN_RECOVERY
               and out["anti"]["anti"] - out["none"]["anti"] > MIN_SEPARATION)
    ok_sym = out["sym"]["sym"] - out["sym"]["sym_null"] > MIN_RECOVERY
    #: the arm that matters: a purely SYMMETRIC world must not manufacture antisymmetric replication
    ok_sep = out["sym"]["anti"] <= max(out["none"]["anti"], 0.0) + 0.05
    passed = bool(ok_anti and ok_sym and ok_sep)
    print(f"\n  planted direction is recovered:              {ok_anti}")
    print(f"  planted relatedness is recovered:            {ok_sym}")
    print(f"  relatedness does NOT leak into antisymmetry: {ok_sep} "
          f"(symmetric world reads {out['sym']['anti']:+.3f} antisymmetric)")
    print(f"  -> {'FLOOR PASSED' if passed else 'FLOOR FAILED -- NO REAL NUMBER WILL BE READ'}\n")
    return out, passed


# ---------------------------------------------------------------- real corpora

def run(name, rows, splits, rng, max_items=None):
    by_learner = timelines(rows)
    learners = sorted(by_learner)
    ft, fp, oat = states(by_learner)
    idx = at_item(ft, oat)
    items = sorted(idx, key=lambda i: -len(idx[i]))
    # the SAME cap lowrank.py applies, so the two studies read the same matrix and their numbers
    # are comparable rather than merely adjacent
    if max_items:
        items = sorted(items[:max_items])
    pairs = [(a, b) for a in items for b in items if a != b]
    print(f"\n{name}: {len(learners):,} learners, {len(items)} items", flush=True)
    acc = []
    for s in range(splits):
        perm = rng.permutation(len(learners))
        A = {learners[i] for i in perm[:len(perm) // 2]}
        B = {learners[i] for i in perm[len(perm) // 2:]}
        MA, MB = (edge_matrix(pairs, by_learner, side, items) for side in (A, B))
        keep = ((~np.isnan(MA)).sum(1) >= MIN_PER_ITEM) & ((~np.isnan(MB)).sum(1) >= MIN_PER_ITEM)
        MA, MB = MA[np.ix_(keep, keep)], MB[np.ix_(keep, keep)]
        got = compare(MA, MB, rng)
        if got:
            acc.append(got)
        print(f"   split {s+1}/{splits}: {int(keep.sum())} items, "
              f"{got['pairs'] if got else 0:,} pairs with both directions observed", flush=True)
    if not acc:
        return None
    g = lambda k: float(np.nanmean([x[k] for x in acc]))  # noqa: E731
    row = dict(corpus=name, pairs=int(np.median([x["pairs"] for x in acc])),
               sym=g("sym"), sym_null=g("sym_null"), anti=g("anti"), anti_null=g("anti_null"),
               anti_share=g("anti_share"),
               sym_beats=bool(g("sym") > g("sym_null")), anti_beats=bool(g("anti") > g("anti_null")))
    row["verdict"] = ("BOTH" if row["sym_beats"] and row["anti_beats"]
                      else "DIRECTIONAL" if row["anti_beats"]
                      else "RELATEDNESS ONLY" if row["sym_beats"] else "NEITHER")
    print(f"   symmetric     {row['sym']:+.3f} vs null {row['sym_null']:+.3f}")
    print(f"   antisymmetric {row['anti']:+.3f} vs null {row['anti_null']:+.3f}")
    print(f"   antisymmetric share of residual energy {row['anti_share']:.3f}")
    print(f"   -> {row['verdict']}")
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--floor-only", action="store_true")
    ap.add_argument("--floor-reps", type=int, default=30)
    ap.add_argument("--splits", type=int, default=8)
    ap.add_argument("--out", default="out/antisymmetry.json")
    args = ap.parse_args()
    rng = np.random.default_rng(SEED)

    floor_out, passed = floor(args.floor_reps, 60, rng)
    if args.floor_only:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(dict(seed=SEED, floor=floor_out,
                                                  floor_passed=passed), indent=2))
        return
    if not passed:
        print("FLOOR FAILED -- stopping before any real corpus is read, per the pre-registration.")
        return

    rows = []
    for name, rd, cap in (("xes3g5m", lambda: xes3g5m_rows(SCRATCH / "xes3g5m"), 160),
                          ("ednet", lambda: ednet_rows(SCRATCH / "ednet"), None)):
        got = run(name, list(rd()), args.splits, rng, max_items=cap)
        if got:
            rows.append(got)

    print()
    for r in rows:
        print(f"{r['corpus']}: {r['verdict']} -- symmetric {r['sym']:+.3f}, "
              f"antisymmetric {r['anti']:+.3f}, direction carries {r['anti_share']:.1%} of "
              f"the residual's energy")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(seed=SEED, deflate_k=DEFLATE_K, splits=args.splits,
                                   floor=floor_out, floor_passed=passed, rows=rows), indent=2))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
