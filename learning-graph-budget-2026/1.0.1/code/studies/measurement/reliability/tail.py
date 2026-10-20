"""A5 on the ASSERTED TAIL: do the edges we would actually claim replicate?

`split_half.py` measures the assay's reliability across EVERY readable pair -- XES3G5M reaches
Spearman-Brown 0.510 / 0.563 / 0.643 at cell floors 5 / 10 / 20, EdNet 0.287 / 0.320 / 0.337, against
a 0.80 gate and a seven-rater human panel's 0.857.

THOSE FIGURES ARE DOMINATED BY THE BULK, AND THE BULK IS EMPTY. Two studies in this programme now
show the signal is sparse: `studies/identifiability/conjunctive/stage3_interaction.py` reads a median interaction of +0.00092
across 11,203 XES3G5M triples while 2,425 fire and the SUPPORTED median is +0.100; `studies/identifiability/within-task/
conjunctive.py` reads a median of exactly +0.0000 across 1,444 triples while 26 fire against 9.8 by
chance. A graph is a sparse object -- O(n) edges among O(n^2) pairs -- so a population-wide
correlation is mostly measuring noise against noise, and the number it returns is not the number the
assay is judged on.

THE QUESTION THE ASSAY ACTUALLY FACES IS NARROWER: of the edges we WOULD ASSERT, how many hold up?

SELECTION MUST BE INDEPENDENT OF MEASUREMENT OR THE ANSWER IS GUARANTEED WRONG. Picking the top
pairs by their drop in half A and then correlating A with B measures regression to the mean and
reports it as unreliability. So learners are split THREE ways:

    S   selection    -- the pairs that clear the assertion bar are chosen here, and only here
    A   measurement  -- one half of the held-out data
    B   measurement  -- the other

Nothing selected in S is measured in S. Two readings come out of that:

  REPLICATION RATE   of the pairs S would assert, what fraction still clear the bar in A+B? This is
                     the interpretable one -- precision of assertion, out of sample.
  TAIL RELIABILITY   Spearman between A and B restricted to the selected pairs, Spearman-Brown
                     corrected exactly as split_half.py does.

TWO CONTROLS, BECAUSE A CORRELATION ON A SUBSET IS NOT COMPARABLE TO ONE ON EVERYTHING.

  SIZE-MATCHED RANDOM   k pairs drawn at random, same k. Handles the sample-size effect.
  RANGE RESTRICTION     selecting on a high drop narrows the spread of the truth among the selected,
                        which LOWERS a correlation for reasons that have nothing to do with the
                        assay. The observed spread in A is reported beside every figure so a fall
                        can be attributed rather than assumed, and this is the confound the study
                        cannot fully remove -- it is stated, not solved.

PRE-REGISTERED VERDICTS, written before the run:

  TAIL IS MORE RELIABLE   tail Spearman-Brown exceeds the population figure AND the size-matched
                          random control. The bulk was dragging the assay's number down and A5 has
                          been understated.
  TAIL IS LESS RELIABLE   it falls below the size-matched random control. The pairs we asserted are
                          exactly the ones that do not hold up, which is a worse result than 0.643
                          and the more serious finding.
  NO DIFFERENCE           within the control band. Sparsity does not change what A5 measures.

Reads XES3G5M and EdNet. EdNet is CC BY-NC 4.0 -- non-commercial, no model training. Raw exports stay
in the session scratchpad; only aggregates are committed.

    python3 tail.py [--splits 24] [--top 0.05]
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
from split_half import CELLS, MIN_PAIRS, SEED, drops, spearman  # noqa: E402
from atlas import ednet_rows, xes3g5m_rows  # noqa: E402
from positivity import SCRATCH, at_item, states, timelines  # noqa: E402

#: the assertion bar: the background drop an arbitrary ordered pair already shows. A pair below this
#: is not something this programme would claim, so it is not part of what A5 should be judged on.
BAR = 0.10
#: a tail needs this many pairs before a correlation on it means anything
MIN_TAIL = 25


def brown(r):
    """Spearman-Brown, exactly as split_half.py applies it: halves -> full-length estimate."""
    return (2 * r) / (1 + r) if r > -1 else float("nan")


def one_split(pairs, by_learner, learners, min_cell, rng, top_frac):
    """Three-way split: select in S, measure in A and B. Nothing selected in S is measured in S."""
    perm = rng.permutation(len(learners))
    third = len(perm) // 3
    parts = []
    for lo, hi in ((0, third), (third, 2 * third), (2 * third, len(perm))):
        side = {learners[i] for i in perm[lo:hi]}
        sub = {k: v for k, v in by_learner.items() if k in side}
        ft, fp, oat = states(sub)
        parts.append(drops(pairs, ft, fp, oat, at_item(ft, oat), min_cell))
    S, A, B = parts
    common = sorted(set(S) & set(A) & set(B))
    if len(common) < MIN_PAIRS:
        return None

    dS = np.array([S[p][0] for p in common])
    dA = np.array([A[p][0] for p in common])
    dB = np.array([B[p][0] for p in common])

    # --- selection, in S only
    asserted = dS > BAR
    k = int(asserted.sum())
    if k < MIN_TAIL:
        # fall back to a fixed top fraction so the study still reports at thin cell floors
        k = max(MIN_TAIL, int(len(common) * top_frac))
        if k > len(common):
            return None
        asserted = np.zeros(len(common), bool)
        asserted[np.argsort(dS)[::-1][:k]] = True
        bar_used = "top-fraction"
    else:
        bar_used = "bar"

    r_all = spearman(dA, dB)
    r_tail = spearman(dA[asserted], dB[asserted])
    # size-matched random control: same k, drawn independently of any drop
    rnd = []
    for _ in range(40):
        sel = rng.choice(len(common), k, replace=False)
        rnd.append(spearman(dA[sel], dB[sel]))
    # replication: of the pairs S asserts, how many clear the bar out of sample?
    held = (dA + dB) / 2.0
    rep = float(np.mean(held[asserted] > BAR)) if k else float("nan")
    base = float(np.mean(held > BAR))
    # DECISION KAPPA on the drop: does the assay assert the same edges in two independent halves?
    decA, decB = dA > BAR, dB > BAR
    kap = kappa(decA, decB)
    kap_tail = kappa(decA[asserted], decB[asserted]) if k >= MIN_TAIL else float("nan")
    return dict(pairs=len(common), k=k, bar_used=bar_used,
                kappa=kap, kappa_tail=kap_tail,
                assert_rate_A=float(decA.mean()), assert_rate_B=float(decB.mean()),
                r_all=r_all, r_tail=r_tail, r_random=float(np.nanmedian(rnd)),
                sb_all=brown(r_all), sb_tail=brown(r_tail),
                sb_random=brown(float(np.nanmedian(rnd))),
                replication=rep, base_rate=base,
                sd_all=float(np.std(dA)), sd_tail=float(np.std(dA[asserted])))


def run(name, rows, splits, rng, top_frac, max_items=90):
    by_learner = timelines(rows)
    learners = sorted(by_learner)
    ft, fp, oat = states(by_learner)
    idx = at_item(ft, oat)
    items = sorted(idx, key=lambda i: -len(idx[i]))[:max_items]
    pairs = [(a, b) for a in items for b in items if a != b]
    print(f"\n{name}: {len(learners):,} learners, {len(items)} items", flush=True)

    out = []
    for min_cell in CELLS:
        acc = [g for g in (one_split(pairs, by_learner, learners, min_cell, rng, top_frac)
                           for _ in range(splits)) if g]
        if not acc:
            print(f"  cell floor {min_cell:>2}: unreadable")
            continue
        m = lambda k: float(np.nanmedian([x[k] for x in acc]))  # noqa: E731
        row = dict(corpus=name, min_cell=min_cell, splits=len(acc),
                   pairs=int(np.median([x["pairs"] for x in acc])),
                   k=int(np.median([x["k"] for x in acc])),
                   **{k: m(k) for k in ("r_all", "r_tail", "r_random", "sb_all", "sb_tail",
                                        "sb_random", "replication", "base_rate",
                                        "sd_all", "sd_tail", "kappa", "kappa_tail",
                                        "assert_rate_A", "assert_rate_B")})
        row["verdict"] = ("TAIL IS MORE RELIABLE" if row["sb_tail"] > max(row["sb_all"], row["sb_random"])
                          else "TAIL IS LESS RELIABLE" if row["sb_tail"] < row["sb_random"]
                          else "NO DIFFERENCE")
        out.append(row)
        print(f"  cell floor {min_cell:>2}: {row['pairs']:>5} pairs, tail k={row['k']:<4} "
              f"SB all {row['sb_all']:+.3f} | tail {row['sb_tail']:+.3f} | "
              f"size-matched random {row['sb_random']:+.3f}   -> {row['verdict']}")
        print(f"                 replication of asserted pairs out of sample "
              f"{row['replication']:.1%}  (base rate {row['base_rate']:.1%})   "
              f"spread sd {row['sd_all']:.3f} -> {row['sd_tail']:.3f} on the tail")
        print(f"                 DECISION KAPPA on the drop {row['kappa']:+.3f}   "
              f"(assert rate {row['assert_rate_A']:.1%} / {row['assert_rate_B']:.1%}; "
              f"course-grain ORDER statistic reads +0.859 at full depth, +0.524 at cell 40)")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--splits", type=int, default=12)
    ap.add_argument("--items", type=int, default=90)
    ap.add_argument("--top", type=float, default=0.05)
    ap.add_argument("--out", default="out/tail.json")
    args = ap.parse_args()
    rng = np.random.default_rng(SEED)

    print("A5 ON THE ASSERTED TAIL -- do the edges we would claim replicate?")
    print(f"  three-way learner split: select in S (drop > {BAR:+.2f}), measure in A and B")
    print(f"  split_half.py for reference: XES3G5M 0.510 / 0.563 / 0.643, EdNet 0.287 / 0.320 / 0.337")

    rows = []
    for name, rd in (("xes3g5m", lambda: xes3g5m_rows(SCRATCH / "xes3g5m")),
                     ("ednet", lambda: ednet_rows(SCRATCH / "ednet"))):
        rows += run(name, list(rd()), args.splits, rng, args.top, args.items)

    print()
    for r in rows:
        print(f"{r['corpus']:8s} floor {r['min_cell']:>2}: {r['verdict']}")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(seed=SEED, bar=BAR, splits=args.splits, rows=rows),
                              indent=2) + "\n")
    print(f"\nwrote {out}")
    print("RANGE RESTRICTION IS NOT REMOVED: selecting on a high drop narrows the spread among the")
    print("selected (reported above as sd_all -> sd_tail), which lowers a correlation for reasons")
    print("that have nothing to do with the assay. Read any fall against that, not past it.")


if __name__ == "__main__":
    main()
