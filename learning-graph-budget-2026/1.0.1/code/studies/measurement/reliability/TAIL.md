# A5 on the asserted tail: the edges we would claim are the *least* reliable part of the instrument

`split_half.py` measures the assay's reliability across **every readable pair** and reaches
Spearman-Brown 0.510 / 0.563 / 0.643 on XES3G5M against a 0.80 gate. The hypothesis behind this study
was that those figures are **dominated by the bulk, and the bulk is empty** — a graph is sparse,
O(n) edges among O(n²) pairs, so a population-wide correlation is largely noise against noise, and
A5 might simply have been understated.

**That hypothesis was wrong, and the opposite is true.**

## Design

Selection must be independent of measurement or the answer is guaranteed. Learners are split **three
ways**: `S` selects which pairs clear the +0.10 bar, `A` and `B` measure them. Nothing selected in
`S` is measured in `S`. Two controls: a **size-matched random** subset of the same *k* (for the
sample-size effect) and the observed spread reported beside every figure (for range restriction,
which this study states rather than solves).

## Result — `TAIL IS LESS RELIABLE` on XES3G5M at every floor, and on EdNet only at floor 5

> **EdNet's rows were re-issued on 2026-09-24 and two of its three verdicts flipped.** The original
> figures came from an extracted KT1 subset that was deleted to reclaim disk and cannot be
> re-derived (`studies/identifiability/a7-readjudication/`, `studies/identifiability/overlap/ATLAS.md`). Both tables below are from the same run;
> **XES3G5M's is identical to the original to every digit**, which is what isolates the change to
> EdNet's reader rather than to anything this study does.

**XES3G5M**, 18,066 learners, 90 items, 12 splits:

| cell floor | pairs | k asserted | SB all | **SB tail** | SB size-matched random | replication out of sample | base rate | spread sd all → tail |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 5 | 7,036 | 3,925 | +0.689 | **+0.607** | +0.689 | **76.2%** | 55.9% | 0.082 → 0.078 |
| 10 | 6,798 | 3,768 | +0.712 | **+0.622** | +0.711 | **77.5%** | 56.3% | 0.076 → 0.071 |
| 20 | 6,434 | 3,550 | +0.743 | **+0.654** | +0.744 | **78.3%** | 56.0% | 0.072 → 0.066 |

**EdNet**, 6,000 learners:

| cell floor | pairs | k asserted | SB all | **SB tail** | SB random | replication | base rate | sd all → tail |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 5 | 7,686 | 2,540 | +0.125 | **+0.120** | +0.128 | **33.8%** | 28.6% | 0.126 → **0.129** |
| 10 | 6,879 | 2,266 | +0.136 | **+0.139** | +0.136 | **32.6%** | 27.3% | 0.117 → **0.120** |
| 20 | 4,115 | 1,226 | +0.181 | **+0.218** | +0.181 | **32.6%** | 24.8% | 0.102 → **0.105** |

*(Superseded, for the record: the unreproducible read gave +0.387/+0.391/+0.403 all-pairs and
+0.366/+0.360/+0.374 on the tail, with k of 1,131/1,100/1,048.)*

**What changed and what it means.** EdNet's reliability on a reproducible read is **a third of what
was recorded** — 0.125–0.181 against 0.387–0.403. The asserted tail roughly doubles in size (k 1,131
→ 2,540 at floor 5) because the drop distribution is different, and the spread more than doubles
(sd 0.056 → 0.126), which is the mechanical reason a correlation computed on it behaves differently.

**Two verdicts flip, and the honest reading is that they are near-ties at a much lower level.** At
floor 10 the tail reads +0.139 against an all-pairs +0.136 and a size-matched random +0.136 — a
three-thousandth, which is nothing. At floor 20 it reads **+0.218 against +0.181**, and *that* one
is a real gap against its own size-matched control, so on a reproducible EdNet read the tail is
genuinely the more reliable part at the highest cell floor.

**This does not reopen the tail route.** 0.218 is against a 0.80 gate. What it does is retire the
sentence this study was written to support: *"the tail is less reliable at every cell floor on both
corpora"* was true of the corpus read we had, and is **not** true of the corpus. It holds on
XES3G5M — where every figure is unchanged — and fails on EdNet at two floors of three.

## What the controls settle

**It is not a sample-size effect.** The size-matched random control reproduces the population figure
almost exactly — +0.689 against +0.689, +0.711 against +0.712, +0.744 against +0.743. A random subset
of the same size keeps full reliability. **The fall is specific to selecting on a high drop.**

**On EdNet it is not range restriction either, and that is the cleaner case.** Selecting on a high
drop is supposed to *narrow* the spread among the selected, which lowers a correlation for reasons
that have nothing to do with the assay. On XES3G5M the spread does narrow, by 5–8% — real, and
smaller than the ~12% fall in Spearman-Brown, but not nothing. **On EdNet the spread *widens* on the
tail** (0.126 → 0.129 at floor 5, re-issued; was 0.056 → 0.062), so range restriction cannot be lowering the correlation there at all. The
tail is genuinely noisier.

## But the interpretable number is the replication rate, and it is not bad

Reliability is a correlation and it inherits every problem a correlation has on a selected subset.
**The question the assay actually faces is precision of assertion out of sample**, and there the
answer is clearer:

- **XES3G5M: 76.2% / 77.5% / 78.3%** of asserted pairs still clear the bar in held-out learners,
  against a base rate of **~56%**. A lift of about 21 points, or 1.40×.
- **EdNet (re-issued): 32.6–33.8%** against a base rate of **24.8–28.6%** — a lift of 1.2–1.3×, and an
  absolute precision so low that two assertions in three do not hold. (The unreproducible read gave
  ~19% against ~8.6%.)

The XES3G5M base rate of 56% is itself worth staring at: **more than half of all readable ordered
pairs already clear +0.10**, which is the background finding (`studies/identifiability/assay-generality/`) restated as a
precision ceiling. Asserting an edge is not a rare event in this corpus, so the lift from asserting
is bounded before the instrument is even considered.

## Verdict for the criterion

**`A5` stays unmet, and the tail reading makes it harder rather than easier.** The best tail figure
is **+0.654** against the 0.80 gate and a seven-rater human panel's 0.857 (`studies/measurement/expert-agreement/`). The
route of "restrict to what we would actually claim and the number improves" is now closed by
measurement.

**This agrees with the other two things measured today.** `studies/identifiability/conjunctive/block_bootstrap.py` found the
conjunctive claim's effective precision is 122 independent tests rather than 11,203, and this finds
the asserted pairwise edges are the least reliable part of the instrument. Both say the same thing:
**the confident end of this assay is thinner than its headline counts suggest.**

```
python3 tail.py --splits 12 --items 90
```

Reads XES3G5M and EdNet. EdNet is CC BY-NC 4.0 — non-commercial, no model training. Raw exports stay
in the session scratchpad; only aggregates are committed.

**Do not compare these all-pairs figures with `split_half.py`'s directly** — this run uses 90 items
and 12 splits and reaches +0.689/+0.712/+0.743 where `split_half.py` reports +0.510/+0.563/+0.643 on
its own configuration. The comparison that matters here is tail against its own population and its
own size-matched control, all measured in the same run.
