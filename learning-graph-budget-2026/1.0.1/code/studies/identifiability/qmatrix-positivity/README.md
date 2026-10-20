# Per-edge Q-matrix positivity: is the design or the learner order the limit on F1?

**Asked.** Gu & Xu (2024, *Statistica Sinica*, doi:10.5705/ss.202021.0350, Proposition 1;
literature review entry 1.1, ranked analysis 2) show that the latent cell "B mastered without A" is
unidentified **by design** when no item measures B without A, whatever the learners did. Paper II's
F1 measures the **empirical** decided share in the positivity atlas (`studies/identifiability/overlap/`).
For every candidate edge A -> B the atlas scores on XES3G5M, ASSISTments 2012-13 and Eedi, this study
asks whether the corpus's Q-matrix has an item measuring B without A, and crosses that design state
with the atlas's empirical state for the same edge. The design, thresholds and verdict strings were
committed before any real number (`qmatrix_positivity.py` docstring, commit `cbc0f5d`; CHANGES
entries `ba778db` and `435417b` changed only how timestamps are ordered, before any number was read).

**Came back.** On all three corpora the pre-registered primary verdict is **LEARNER-ORDER-LIMITED**:
the item design isolates B from A for all but 0 to 3 of the atlas's undecided edges. The
design-level and learner-level limits fall on **different edges**. Each design-unidentified edge
is also undecided (verdict "DESIGN NESTED IN LEARNER LIMIT"), but these edges are a vanishing part
of the undecided set. F1's low decided shares are not explained by Gu & Xu's design condition: the
limit is who reached B having failed A, not which items exist. Under the strict reading (an item
measuring B *alone*), the design does bind on part of the undecided set: 16.7% on XES3G5M and
8.2% on Eedi (verdict MIXED there).

## Floor and reproduction

- **Synthetic floor passed** (`out/floor.json`). The pairwise counter equals a brute-force loop
  exactly on all 39,800 ordered pairs of a planted 200-unit Q-matrix. All 40 planted unidentified
  edges and all 40 planted isolating items were recovered. Gu & Xu's toy ({A}, {A,B}, {A,B}) comes
  back with A -> B unidentified and B -> A identified. The Q builder rebuilds the planted Q from a
  shuffled row stream. On a 6,000-learner synthetic corpus, the dense per-edge replica of the
  atlas matches the atlas's own `positivity.classify`, `mde`, `classify_edge` and `reachability`
  on every one of 210 ordered pairs, with every branch exercised (supported, would-be
  contradicted, 18 falsifiable). The timestamp key orders mixed-width strings exactly as Python's
  string comparison does.
- **The atlas reproduced exactly** on all three corpora. Recomputed per edge, the counts of
  learners, units, edges, readable edges, edges powered for a 20-point drop, supported,
  contradicted (before and after the merge-node gate) and unknown equal the committed rows
  (`overlap/out/atlas.json` for XES3G5M and Eedi, `overlap/out/positivity-assist.json` for
  ASSISTments). XES3G5M 736 supported / 69 contradicted / 19,195 unknown. Eedi
  4,935 / 138 / 14,927. ASSISTments 87 / 0 / 39,913. The cross-tabulations below are therefore
  against the committed atlas.
- Artefacts found on the way. XES3G5M has 7 timestamps of 12 digits among 6,350,435 unit-events,
  and ASSISTments `start_time` mixes fractional-second widths (19 to 26 characters). The atlas
  compares both as strings, and this replica does the same. Whether string order is the right
  order for those few rows is a question about the atlas. It is reported here, not repaired.

## Results (U = no item measures B without A)

Census values cover every ordered pair of units (the whole population, so they carry no interval).
f is the share of the atlas's undecided edges that are in U. Its interval is the wider of the Wilson
95% interval, which resamples edges, and a 1,000-draw cluster bootstrap over dependants B; neither
resamples learners.

| corpus | units | items | units/item | census U | sampled edges | U in sample | undecided | **f** (95%) | verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| XES3G5M | 865 | 7,651 | 1.16 | 151 of 747,360 (0.020%) | 20,000 | 2 | 19,195 | **0.010%** [0, 0.038%] | LEARNER-ORDER-LIMITED |
| ASSISTments 2012-13 | 265 | 53,091 | 1.00 | 0 of 69,960 | 40,000 | 0 | 39,913 | **0%** [0, 0.0096%] | LEARNER-ORDER-LIMITED (vacuous: Q is a partition) |
| Eedi | 308 | 27,523 | 1.10 | 18 of 94,556 (0.019%) | 20,000 | 3 | 14,927 | **0.020%** [0, 0.059%] | LEARNER-ORDER-LIMITED |

**Cross-tabulation, design state by atlas state (sampled edges).**

| corpus | design | unreadable | unpowered | supported | contradicted | unfalsifiable |
|---|---|---:|---:|---:|---:|---:|
| XES3G5M | U | 2 | 0 | 0 | 0 | 0 |
| | not U | 15,147 | 3,703 | 736 | 69 | 343 |
| ASSISTments | U | 0 | 0 | 0 | 0 | 0 |
| | not U | 30,650 | 9,217 | 87 | 0 | 46 |
| Eedi | U | 2 | 1 | 0 | 0 | 0 |
| | not U | 6,878 | 7,322 | 4,935 | 138 | 724 |

**Same edges or different?** These are signed counts: U and undecided / U and decided / not U and
undecided / not U and decided.
- XES3G5M: 2 / 0 / 19,193 / 805, Jaccard 0.0001.
- Eedi: 3 / 0 / 14,924 / 5,073, Jaccard 0.0002.
- ASSISTments: 0 / 0 / 39,913 / 87.

No design-unidentified edge is decided, and so none is supported. The pre-registered
supported-by-construction flag therefore does not fire, because the share of supported edges in U
is 0 on all three corpora. The decided rate is lower in U than outside it: 0% against 4.0% on
XES3G5M (d = −4.0 points) and 0% against 25.4% on Eedi (d = −25.4 points). The direction agrees
with the design limit, but it rests on 2 and 3 edges.

**The derangement null is degenerate here, and the direction test is not informative.**
This was found after the run and does not change any threshold. The pre-registered null deranges
U labels among edges that share a dependant. Its standard deviation came back at about 0 for U on
both corpora. That happens only when every sampled edge into those dependants is undecided, so
the few U edges sit under dependants the learners never decide for any A. Under the strict
reading U_pure is a property of B alone, so a within-B derangement cannot move it at all. The
reported verdict "NO DETECTED ASSOCIATION beyond the dependant" (p = 1.0) therefore reflects the
construction of the test, not a finding about the data. Read the sign of d as descriptive only.

### Secondary: either cell, the strict (pure-item) reading, and co-tagged pairs

| corpus | U_either (sample) | census U_pure | **f, U_pure** (95%) | decided, U_pure vs not | supported in U_pure |
|---|---:|---:|---:|---:|---:|
| XES3G5M | 6 (f 0.031%) | 124,416 of 747,360 (16.6%); 144 of 865 units have no item measuring them alone | **16.7%** [14.3%, 19.1%], MIXED | 1.4% vs 4.5% | 40 of 736 (5.4%): flag fires |
| ASSISTments | 0 | 0 | 0%, LEARNER-ORDER-LIMITED | n/a | 0 |
| Eedi | 6 (f 0.040%) | 5,833 of 94,556 (6.2%); 19 of 308 units | **8.2%** [4.8%, 12.0%], MIXED | 0.6% vs 27.0% | 7 of 4,935 (0.1%) |

Under Gu & Xu's strict condition, which requires an identity row for B over all attributes, a
dependant with no item measuring it alone leaves every edge into it unidentified. Under that
reading the design does bind on a real part of F1's undecided set. On XES3G5M, 40 of the 736
supported edges point into such dependants. The supported-count flag (≥ 0.05) fires only here. It
fires on the strict reading only. Whether those 40 edges share an item with their prerequisite,
which is the conjunction-by-item mechanism, was not computed.

U is concentrated where the design question has bite. Among pairs whose skills share at least one
item, U is 151 of 1,528 on XES3G5M (9.9%) and 18 of 1,986 on Eedi (0.9%).

**Exploratory, not pre-registered.** Co-tagged edges are decided far more often than the rest:
11 of 39 (28%) against 4.0% on XES3G5M, and 275 of 427 (64%) against 25.4% on Eedi. On Eedi, 270
of the 4,935 supported edges (5.5%) share an item with their prerequisite, and part of their drop
may come from the shared item rather than the edge. This was not a pre-registered verdict and
needs its own study before anything rests on it.

## What it means for F1

The pre-registered reading for LEARNER-ORDER-LIMITED on all three corpora is that Gu & Xu's
condition holds pairwise on these designs, so the design does not explain F1's low decided shares.
F1's measurement is a distinct, learner-level limit. Gu & Xu should be credited for the argument
(literature synthesis row 1), but they are not the cause of the numbers. Two qualifications go with
it. First, on ASSISTments the result is vacuous: each problem carries one skill, so the pairwise
condition holds trivially. Second, under the strict reading, F1 should say that on XES3G5M (16.7%)
and Eedi (8.2%) part of the undecided set also lacks an item measuring the dependant alone.

## What this cannot say

A design-identified edge is not thereby identified. Gu & Xu's Theorem 1 needs more than a pairwise
isolating item, and learners must still take those items, which is exactly what the atlas
measures. The Q-matrices are the platforms' own tagging (TAL's KC routes, the ASSISTments skill
tags, Eedi's subject tree). This study did not validate any of them against an independent coder.
Eedi's order is last-answer order, a limitation carried over from the atlas. This study says
nothing about direction, conjunction or lag.

## Files

- `qmatrix_positivity.py`: the pre-registration (docstring) and the code. Run
  `--floor`, then `--corpus xes3g5m|assist|eedi`, then `--summary`.
- `out/floor.json`, `out/{xes3g5m,assist,eedi}.json` (census, cross-tabs, intervals, reproduction
  check, qmatrix.py's C1–C4 conditions), `out/summary.json`, `out/history-entry.json`.
- Reads three licensed corpora, XES3G5M, ASSISTments 2012-13 and Eedi NeurIPS 2020, via
  `shared.paths.data_path`. Only aggregates are written, and nothing is derived to disk.
