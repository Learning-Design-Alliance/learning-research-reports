"""Does the edge matrix have structure beyond its own margins?

A5 found the per-edge ranking replicates at 0.475-0.643. Two levers were tried and neither moved it:
the OUTPUT UNIT (`studies/measurement/reliability/coarse.py` -- grouping by the authored taxonomy is no better than the
edge, and the coarsest grain is worse) and the ESTIMAND (`studies/measurement/reliability/retention.py` -- retention is
worse, because it keeps 91% of the signal with 46% of the sample).

Neither tried the thing Borgs & Chayes (arXiv:1706.01143) §4 is actually about: POOLING ACROSS NODES
WITH SIMILAR CONNECTION PROFILES, learned from the data rather than imposed. `coarse.py` pooled using
a grouping someone authored; this learns one.

THE QUESTION, PUT SO IT CAN FAIL. Decompose the edge matrix into

    M[i,j]  ~  mu + a_i + b_j   +   R[i,j]

The additive part is the MARGINS: a source effect and a target effect, which is reach and difficulty.
`studies/measurement/reliability/split_half.py` already established that a ranking of reach is worthless -- partialling it
out moved reliability by less than 0.013, so the assay is not secretly ranking reach, but equally a
margin-only structure would tell us nothing about prerequisites. So the real question is whether the
RESIDUAL -- genuine pairwise structure, what a graphon would call the interesting part of W -- carries
anything that replicates.

THE CONTROL IS THE WHOLE STUDY, AND IT IS THE LESSON FROM coarse.py. ANY smoother raises split-half
correlation by shrinking towards a common mean, so a denoised matrix will replicate better than a raw
one whether or not there is structure. Every arm therefore runs identically on a MARGIN-MATCHED NULL:
a matrix with the same row and column effects and the residual permuted, which destroys pairwise
structure and keeps everything else. A rank that does not beat its own null is measuring the smoother.

DIRECTEDNESS IS KEPT. Graphon estimators assume a symmetric W, and symmetrising would destroy the
direction question this programme exists to ask. The matrix is treated as BIPARTITE -- rows are the
source, columns the target -- which is the form Borgs & Chayes actually develop for collaborative
filtering, and it leaves M[i,j] and M[j,i] as distinct entries.

CORRECTED 2026-09-22 -- THE FIRST VERSION TESTED THE WRONG THING. It measured the rank-r TRUNCATION
of the residual: keep the top r singular components and correlate those across halves. Rank 1
replicated at +0.416 against a null of -0.003 and the run reported PAIRWISE STRUCTURE.

But **a rank-1 term u_i v_j is a MULTIPLICATIVE NODE EFFECT** -- a source score times a target score,
which is another margin, not a pairwise interaction. Removing the ADDITIVE margins mu + a_i + b_j and
then keeping the leading multiplicative one measures margins twice over and calls the result
structure. The arms were not independent either: "rank 2" was a truncation INCLUDING rank 1, so each
arm contained the ones below it.

The corrected test DEFLATES rather than truncates. After the additive margins, the top k singular
components are REMOVED, and what survives is correlated across halves. k = 0 is additive-only; k = 1
also removes the multiplicative margin; k >= 2 removes progressively more node-level structure. Only
what survives k >= 1 can be called pairwise.

PRE-REGISTERED VERDICT, revised before any corrected number was read:

  PAIRWISE STRUCTURE     the DEFLATED residual at k >= 1 replicates above its margin-matched null.
  MARGINS ONLY           it does not. The edge matrix is node-level effects -- additive and
                         multiplicative -- and there is no pairwise structure to recover by pooling.

    python3 lowrank.py [--splits 8] [--out out/lowrank.json]

Exports stay in the scratchpad; only aggregate rows are committed.

DIRECTION: symmetric -- split-half replication of the residual is unchanged by transposing both
halves (the additive margins and the SVD deflation are transpose-equivariant), and M[a, b] comes
from each learner's timeline.

Direction declaration added 2026-09-24 (reversed-arrow rule, shared/experimental-contract.md):
nothing reported depends on edge orientation, so no reversed-arrow control applies.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "studies/identifiability/overlap"))
sys.path.insert(0, str(HERE.parents[2] / "studies/measurement/reliability"))

from atlas import ednet_rows, xes3g5m_rows  # noqa: E402
from positivity import SCRATCH, at_item, classify, states, timelines  # noqa: E402
from split_half import spearman  # noqa: E402

SEED = 20260922
SPLITS = 8
MIN_CELL = 5
MIN_PAIRS = 100
#: components to DEFLATE (remove). 0 = additive margins only; 1 also removes the
#: multiplicative margin; higher removes more node-level structure.
DEFLATE = (0, 1, 2, 3)
#: items with fewer observed cells than this are dropped: a row with two entries cannot inform a
#: latent position, and keeping it lets the SVD fit noise
MIN_PER_ITEM = 8


def edge_matrix(pairs, by_learner, side, items):
    sub = {k: v for k, v in by_learner.items() if k in side}
    ft, fp, oat = states(sub)
    idx = at_item(ft, oat)
    pos = {it: i for i, it in enumerate(items)}
    M = np.full((len(items), len(items)), np.nan)
    for a, b in pairs:
        c = classify((a, b), ft, fp, oat, idx)
        nm, nf = len(c["mastered"]), len(c["failed"])
        if nm < MIN_CELL or nf < MIN_CELL:
            continue
        M[pos[a], pos[b]] = float(np.mean(c["mastered"])) - float(np.mean(c["failed"]))
    return M


def additive(M, iters=60):
    """mu + a_i + b_j fitted on observed cells only, by alternating means."""
    obs = ~np.isnan(M)
    mu = np.nanmean(M)
    a = np.zeros(M.shape[0])
    b = np.zeros(M.shape[1])
    for _ in range(iters):
        R = M - mu - b[None, :]
        a = np.where(obs.any(1), np.nanmean(np.where(obs, R, np.nan), axis=1), 0.0)
        a = np.nan_to_num(a)
        R = M - mu - a[:, None]
        b = np.where(obs.any(0), np.nanmean(np.where(obs, R, np.nan), axis=0), 0.0)
        b = np.nan_to_num(b)
    return mu + a[:, None] + b[None, :]


def truncate(R, rank):
    """Top-`rank` components KEPT. Reported only to show what the first version was measuring."""
    X = np.nan_to_num(R)
    U, s, Vt = np.linalg.svd(X, full_matrices=False)
    k = min(rank, len(s))
    return (U[:, :k] * s[:k]) @ Vt[:k]


def deflate(R, k):
    """Top-k components REMOVED. k=0 leaves the additive residual; k>=1 strips the multiplicative
    margin too, so what remains cannot be written as a score per source times a score per target."""
    X = np.nan_to_num(R)
    if k <= 0:
        return X
    U, s, Vt = np.linalg.svd(X, full_matrices=False)
    kk = min(k, len(s))
    return X - (U[:, :kk] * s[:kk]) @ Vt[:kk]


def margin_matched_null(M, rng):
    """Same additive structure, residuals permuted among observed cells: pairwise structure gone."""
    fit = additive(M)
    R = M - fit
    obs = ~np.isnan(M)
    vals = R[obs]
    rng.shuffle(vals)
    out = np.full_like(M, np.nan)
    out[obs] = fit[obs] + vals
    return out


def compare(MA, MB, k, rng):
    """Split-half Spearman of the residual with the top-k components REMOVED, against its null."""
    both = (~np.isnan(MA)) & (~np.isnan(MB))
    if both.sum() < MIN_PAIRS:
        return None
    def defl(M):
        return deflate(M - additive(M), k)
    ra, rb = defl(MA), defl(MB)
    real = spearman(ra[both], rb[both])
    na, nb = defl(margin_matched_null(MA, rng)), defl(margin_matched_null(MB, rng))
    null = spearman(na[both], nb[both])
    fa, fb = additive(MA), additive(MB)
    add = spearman(fa[both], fb[both])
    raw = spearman(MA[both], MB[both])
    # what the FIRST version measured, kept so the correction is visible rather than silent
    ka = truncate(MA - additive(MA), max(k, 1))
    kb = truncate(MB - additive(MB), max(k, 1))
    keep = spearman(ka[both], kb[both])
    return dict(cells=int(both.sum()), raw=raw, additive=add, residual=real, residual_null=null,
                excess=real - null, truncation_kept=keep)


def run(name, rows, splits, rng, max_items=None):
    by_learner = timelines(rows)
    learners = sorted(by_learner)
    ft, fp, oat = states(by_learner)
    idx = at_item(ft, oat)
    items = sorted(idx, key=lambda i: -len(idx[i]))
    if max_items:
        items = sorted(items[:max_items])
    pairs = [(a, b) for a in items for b in items if a != b]
    print(f"{name}: {len(learners):,} learners, {len(items)} items, {len(pairs):,} cells")
    print(f"   additive margins are removed first; then the top-k singular components, because a "
          f"rank-1 term is a MULTIPLICATIVE margin, not pairwise structure")

    acc = {r: [] for r in DEFLATE}
    for s in range(splits):
        perm = rng.permutation(len(learners))
        A = {learners[i] for i in perm[:len(perm) // 2]}
        B = {learners[i] for i in perm[len(perm) // 2:]}
        MA, MB = (edge_matrix(pairs, by_learner, side, items) for side in (A, B))
        keep = ((~np.isnan(MA)).sum(1) >= MIN_PER_ITEM) & ((~np.isnan(MB)).sum(1) >= MIN_PER_ITEM)
        MA, MB = MA[np.ix_(keep, keep)], MB[np.ix_(keep, keep)]
        for r in DEFLATE:
            got = compare(MA, MB, r, rng)
            if got:
                acc[r].append(got)
        print(f"   split {s+1}/{splits}: {int(keep.sum())} items kept, "
              f"{int(((~np.isnan(MA)) & (~np.isnan(MB))).sum()):,} cells on both", flush=True)

    out = []
    for r in DEFLATE:
        if not acc[r]:
            continue
        g = lambda k: float(np.nanmean([x[k] for x in acc[r]]))  # noqa: E731
        row = dict(corpus=name, deflated=r, cells=int(np.median([x["cells"] for x in acc[r]])),
                   raw=g("raw"), additive=g("additive"), residual=g("residual"),
                   residual_null=g("residual_null"), excess=g("excess"),
                   truncation_kept=g("truncation_kept"),
                   beats_null=bool(g("residual") > g("residual_null")))
        out.append(row)
        label = "additive only" if r == 0 else f"additive + top-{r} removed"
        print(f"   {label:24s} residual {row['residual']:+.3f} vs null "
              f"{row['residual_null']:+.3f} (excess {row['excess']:+.3f}) "
              f"-> {'STRUCTURE' if row['beats_null'] else 'null'}"
              + (f"   [truncation kept top-{max(r,1)}: {row['truncation_kept']:+.3f}]" if r <= 1 else ""))
    return out


def main() -> None:
    argv = sys.argv
    splits = int(argv[argv.index("--splits") + 1]) if "--splits" in argv else SPLITS
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else HERE / "out/lowrank.json"
    rng = np.random.default_rng(SEED)
    rows = []
    rows += run("ednet", ednet_rows(SCRATCH / "ednet"), splits, rng)
    rows += run("xes3g5m", xes3g5m_rows(SCRATCH / "xes3g5m"), splits, rng, max_items=160)
    # only k >= 1 can be called pairwise: k = 0 still contains the multiplicative margin
    any_structure = [r for r in rows if r["beats_null"] and r["deflated"] >= 1]
    print(f"\nVERDICT: {'PAIRWISE STRUCTURE' if any_structure else 'MARGINS ONLY'} -- "
          f"{len(any_structure)} of {len([r for r in rows if r['deflated'] >= 1])} "
          f"(corpus, deflation>=1) arms beat their margin-matched null")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(seed=SEED, splits=splits, deflate=DEFLATE, min_cell=MIN_CELL,
                                   min_per_item=MIN_PER_ITEM, rows=rows), indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
