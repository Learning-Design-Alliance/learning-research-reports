"""Is the EDGE the wrong output unit? Split-half reliability at coarser grains.

`split_half.py` established that the assay's per-edge ranking replicates at Spearman-Brown 0.510 to
0.643 on the best corpus available, against a 0.80 gate -- and that the standing 0.523 was a fact
about the assay rather than about unreadable data. A ranking that unstable cannot support edge-level
claims.

But the programme inherited the EDGE as its output unit from the literature it argues with, and has
never asked whether a coarser readout is stable. This asks that: group the knowledge components, score
GROUP PAIRS rather than item pairs, and measure the same split-half reliability.

THE CONTROL IS THE ENTIRE STUDY, BECAUSE AGGREGATION RAISES RELIABILITY MECHANICALLY. Averaging k
noisy estimates cuts their noise by sqrt(k), so ANY grouping improves replication, including a
meaningless one. Reporting "coarser is more reliable" without a matched random grouping would be
restating the Spearman-Brown formula and calling it a finding.

So every taxonomic grain is run beside a RANDOM grouping with the same number of groups and the same
group-size distribution, on the same split, from the same edge scores.

  TAXONOMY BEATS RANDOM   the authored grouping is doing work: the groups are real.
  AGGREGATION ONLY        they match. Reliability at grain g is available, but the taxonomy is not
                          what supplies it, and no claim about the groups' meaning is supported.

PRE-REGISTERED PREDICTION, written before the run: `studies/identifiability/taxonomy-order/` found the same hierarchy INERT
for ordering -- same module buys +0.0161 over an arbitrary pair, non-monotone in distance, no
ancestor/descendant direction. So taxonomic and random grouping are expected to MATCH, and the
expected finding is AGGREGATION ONLY.

    python3 coarse.py [--splits 8] [--pairs 30000] [--out out/coarse.json]

XES3G5M only: it is the one positivity-passing corpus with an authored hierarchy to group by. Export
stays in the scratchpad; only the aggregate row per grain is committed.

DIRECTION: symmetric -- split-half reliability of group-pair drops is unchanged by reversing every
pair in both halves; the taxonomy groups nodes and orients nothing.

Direction declaration added 2026-09-24 (reversed-arrow rule, shared/experimental-contract.md):
nothing reported depends on edge orientation, so no reversed-arrow control applies.

CHANGE 1 (2026-10-14, after the published result and after the release's reproduction had been read;
post hoc, decided by the maintainer). The reproduction found that the matched random grouping depended
on Python's per-process string-hash seed: `matched_random` took the group sizes in the iteration order of
a set of strings, so which random group received which size changed from process to process although the
numpy seed was fixed. Across four processes the random rows ran 0.402 to 0.519, and under one seed the
L3 verdict read AGGREGATION ONLY instead of the published TAXONOMY BEATS RANDOM: the published verdicts
rested on one draw. Two changes, nothing else:
  (a) group sizes are taken in sorted order of the group labels, so a draw no longer depends on the hash
      seed;
  (b) the control is the mean over R_DRAWS = 50 matched random groupings per level and split, drawn from
      their own generator (SEED + 1). (Written before the run as "so that the learner splits are the
      same as before"; that was wrong. The published single draws used the splits' generator, so moving
      them changes splits 2 to 8, and the edge and taxonomy rows move with them: the edge row from 0.475
      to 0.478, the taxonomy rows from 0.447 / 0.495 / 0.574 to 0.455 / 0.530 / 0.564. Corrected after the
      run, 2026-10-14; the verdicts are the published ones.) Each draw's
      Spearman-Brown is computed from its split-half correlations averaged over the splits, as the
      taxonomy's is.
The verdict rule and its margin are unchanged: TAXONOMY BEATS RANDOM when the taxonomy's Spearman-Brown
exceeds the MEAN random Spearman-Brown by more than 0.05, AGGREGATION ONLY otherwise. Reported beside it,
not used by the rule: the 2.5th and 97.5th percentiles of the 50 draws and the share of draws the
taxonomy exceeds. The edge row uses the tie-averaged ranks of shared/stats.rank (the published file was
written with positional ranks; it moves in the seventh digit). The superseded single-draw file is kept as
out/coarse-single-draw.json.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "studies/identifiability/overlap"))

from atlas import xes3g5m_rows  # noqa: E402
from positivity import SCRATCH, at_item, classify, states, timelines  # noqa: E402
from split_half import spearman  # noqa: E402

SEED = 20260922
SPLITS, N_PAIRS = 8, 30000
#: CHANGE 1: matched random groupings per level and split
R_DRAWS = 50
MIN_CELL = 5
#: a group pair needs at least this many readable edges on BOTH halves to be scored
MIN_EDGES_PER_GROUP_PAIR = 3
MIN_GROUP_PAIRS = 30
GATE = 0.80
#: taxonomy prefix lengths to group by. Level 1 gives 9 groups, which is too few to rank.
LEVELS = (2, 3, 4)


def edge_scores(pairs, by_learner, side):
    sub = {k: v for k, v in by_learner.items() if k in side}
    ft, fp, oat = states(sub)
    idx = at_item(ft, oat)
    out = {}
    for a, b in pairs:
        c = classify((a, b), ft, fp, oat, idx)
        nm, nf = len(c["mastered"]), len(c["failed"])
        if nm < MIN_CELL or nf < MIN_CELL:
            continue
        out[(a, b)] = float(np.mean(c["mastered"])) - float(np.mean(c["failed"]))
    return out


def group_reliability(sa, sb, group):
    """Spearman between halves on GROUP-PAIR mean drops, and how many group pairs were scored."""
    ga, gb = defaultdict(list), defaultdict(list)
    for (a, b), v in sa.items():
        ga[(group[a], group[b])].append(v)
    for (a, b), v in sb.items():
        gb[(group[a], group[b])].append(v)
    keys = [k for k in set(ga) & set(gb)
            if k[0] != k[1]
            and len(ga[k]) >= MIN_EDGES_PER_GROUP_PAIR and len(gb[k]) >= MIN_EDGES_PER_GROUP_PAIR]
    if len(keys) < MIN_GROUP_PAIRS:
        return None, len(keys)
    x = [float(np.mean(ga[k])) for k in keys]
    y = [float(np.mean(gb[k])) for k in keys]
    return spearman(x, y), len(keys)


def matched_random(group, rng):
    """A random grouping with the same number of groups and the same group-size distribution."""
    items = list(group)
    sizes = [sum(1 for i in group if group[i] == g) for g in sorted(set(group.values()))]
    rng.shuffle(items)
    out, k = {}, 0
    for gi, n in enumerate(sizes):
        for it in items[k:k + n]:
            out[it] = f"r{gi}"
        k += n
    for it in items[k:]:
        out[it] = f"r{len(sizes) - 1}"
    return out


def main() -> None:
    argv = sys.argv
    splits = int(argv[argv.index("--splits") + 1]) if "--splits" in argv else SPLITS
    n_pairs = int(argv[argv.index("--pairs") + 1]) if "--pairs" in argv else N_PAIRS
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else HERE / "out/coarse.json"
    rng = np.random.default_rng(SEED)
    rng_r = np.random.default_rng(SEED + 1)

    root = SCRATCH / "xes3g5m"
    route = {int(k): tuple(v) for k, v in
             json.loads((root / "cid2route.json").read_text(encoding="utf-8")).items()}
    by_learner = timelines(xes3g5m_rows(root))
    learners = sorted(by_learner)
    ft, fp, oat = states(by_learner)
    items = sorted(at_item(ft, oat))
    all_pairs = [(a, b) for a in items for b in items if a != b]
    pairs = [all_pairs[i] for i in rng.choice(len(all_pairs), min(n_pairs, len(all_pairs)),
                                              replace=False)]
    print(f"xes3g5m: {len(learners):,} learners, {len(items)} KCs, {len(pairs):,} pairs, "
          f"{splits} splits")

    groupings = {}
    for lvl in LEVELS:
        g = {int(k.split("k")[-1]) if isinstance(k, str) else k: None for k in []}
        g = {}
        for it in items:
            kc = int(it[1:]) if isinstance(it, str) and it.startswith("k") else int(it)
            r = route.get(kc, ())
            g[it] = "/".join(r[:lvl]) if len(r) >= lvl else "/".join(r) or "?"
        groupings[f"taxonomy L{lvl}"] = g
        print(f"   taxonomy L{lvl}: {len(set(g.values()))} groups")

    acc = defaultdict(list)
    draws = {name: [[] for _ in range(R_DRAWS)] for name in groupings}
    edge_rs = []
    for s in range(splits):
        perm = rng.permutation(len(learners))
        A = {learners[i] for i in perm[:len(perm) // 2]}
        B = {learners[i] for i in perm[len(perm) // 2:]}
        sa, sb = edge_scores(pairs, by_learner, A), edge_scores(pairs, by_learner, B)
        both = sorted(set(sa) & set(sb))
        if len(both) >= 30:
            edge_rs.append(spearman([sa[k] for k in both], [sb[k] for k in both]))
        for name, g in groupings.items():
            r, n = group_reliability(sa, sb, g)
            if r is not None:
                acc[name].append((r, n))
            for d in range(R_DRAWS):
                rg = matched_random(g, rng_r)
                r2, n2 = group_reliability(sa, sb, rg)
                if r2 is not None:
                    acc[f"{name} RANDOM"].append((r2, n2))
                    draws[name][d].append(r2)
        print(f"   split {s+1}/{splits} done ({len(both):,} edges readable on both)", flush=True)

    def sb_of(rs):
        r = float(np.nanmean([x[0] for x in rs]))
        return r, (2 * r / (1 + r) if r > -1 else float("nan")), int(np.median([x[1] for x in rs]))

    rows = []
    r_edge, sb_edge, _ = sb_of([(x, 0) for x in edge_rs]) if edge_rs else (float("nan"),) * 3
    print(f"\n{'grain':24s}{'groups':>8s}{'pairs':>9s}{'split-half':>12s}{'S-B':>8s}")
    print(f"{'EDGE (per item pair)':24s}{len(items):>8d}{len(pairs):>9,d}"
          f"{r_edge:>12.3f}{sb_edge:>8.3f}")
    rows.append(dict(grain="edge", groups=len(items), pairs=len(pairs),
                     split_half=r_edge, spearman_brown=sb_edge, meets_gate=bool(sb_edge >= GATE)))
    for name in list(groupings) + [f"{n} RANDOM" for n in groupings]:
        if name not in acc:
            continue
        r, sb, n = sb_of(acc[name])
        ng = len(set(groupings[name.replace(" RANDOM", "")].values()))
        print(f"{name:24s}{ng:>8d}{n:>9,d}{r:>12.3f}{sb:>8.3f}"
              f"{'  MEETS GATE' if sb >= GATE else ''}")
        rows.append(dict(grain=name, groups=ng, pairs=n, split_half=r, spearman_brown=sb,
                         meets_gate=bool(sb >= GATE)))

    print()
    for lvl in LEVELS:
        t, r_ = f"taxonomy L{lvl}", f"taxonomy L{lvl} RANDOM"
        if t in acc and r_ in acc:
            st = sb_of(acc[t])[1]
            sbs = []
            for rs in draws[t]:
                if rs:
                    r = float(np.mean(rs))
                    sbs.append(2 * r / (1 + r))
            sbs = np.array(sbs)
            sr = float(sbs.mean())
            lo, hi = (float(x) for x in np.percentile(sbs, [2.5, 97.5]))
            beats = float(np.mean(st > sbs))
            verdict = "TAXONOMY BEATS RANDOM" if st - sr > 0.05 else "AGGREGATION ONLY"
            print(f"L{lvl}: taxonomy {st:+.3f} vs matched random mean {sr:+.3f} "
                  f"[{lo:+.3f}, {hi:+.3f}] over {len(sbs)} draws (gap {st - sr:+.3f}; "
                  f"taxonomy above {beats:.0%} of draws) -> {verdict}")
            rows.append(dict(comparison=f"L{lvl}", taxonomy=st, random=sr, gap=st - sr,
                             random_draws=len(sbs), random_p2_5=lo, random_p97_5=hi,
                             share_of_draws_below_taxonomy=beats, verdict=verdict))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(seed=SEED, random_seed=SEED + 1, random_draws=R_DRAWS,
                                   change="CHANGE 1 (2026-10-14): mean of matched random draws",
                                   splits=splits, pairs=len(pairs), gate=GATE,
                                   min_cell=MIN_CELL,
                                   min_edges_per_group_pair=MIN_EDGES_PER_GROUP_PAIR,
                                   rows=rows), indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
