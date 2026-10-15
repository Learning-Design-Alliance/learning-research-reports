# What empties the identifying cell in each corpus, measured from its records?

**Asked** (maintainer, 2026-10-13), after the scope audit's finding F1: Paper II sorts corpora by how
their order is documented to be set, and the records do not follow that label (EDM Cup and Eedi are both
teacher-assigned; Junyi is learner-chosen and decides nothing).

**Status: DONE (2026-10-13). Floor passed on its third run (CHANGES 4); real reading under CHANGES 5.** The design, the decomposition (identifying cell = coverage x order x
pass-through, read separately in the curriculum's direction and against it), the labels, the documentation's predictions, the claims C1-C3 for the paper and the floor are
in the docstring of `empty_cell.py`, committed before any corpus is read.

## Floor (`out/floor.json`)

All twelve labels came out as planted, and N x O x P1 x P2 equalled the atlas's identifying cell on every
one of the 1,560 ordered pairs in each of the six worlds.

| world | planted | forward | backward | W |
| --- | --- | --- | --- | ---: |
| fixed | one global order, no gating | CELL FILLS | ORDER-LIMITED | 0.00 |
| gated | random order, move on only after a pass | RETRY-LIMITED | RETRY-LIMITED | 1.00 |
| curriculum | one global order, gated | RETRY-LIMITED | ORDER-LIMITED | 0.00 |
| sparse | 2 skills per learner | COVERAGE-LIMITED | COVERAGE-LIMITED | (7 pairs) |
| free | random order, no gating | CELL FILLS | CELL FILLS | 1.00 |
| easy | one attempt, pass probability 0.995 | EASE-LIMITED | EASE-LIMITED | 1.00 |

Two margins worth knowing. In the sparse world COVERAGE bound 66% of the empty forward pairs, not all:
pairs with 5 to 9 learners often have fewer than 5 who met a first, and those count as ORDER. W there rests
on 7 unordered pairs and means nothing. In the easy world 82% and 78% of pairs were empty, above the half
rule.

## Floors 2 and 3 (`out/floor-changes3.json`, `out/floor.json`)

CHANGES 3 replaced counts with binomial evidence for order and ease. Its floor failed: the easy world read
COVERAGE-LIMITED, because ease was judged against the corpus's own median miss rate, and in a world of
easy skills nothing is easier than usual; the marginal world, given 3 attempts per skill, really did
contain retrying (14% of its empty forward pairs). CHANGES 4 judged ease against a fixed 1-in-5 miss rate
and gave marginal one attempt per skill. The third floor passes: all sixteen labels as planted, the
identity exact, too-few-learners binding 99.9% / 98.7% of empty pairs in sparse and 100% / 95.1% in
marginal; every label is the same at the 1-in-10 and 3-in-10 ease standards. The first table above is
floor 1's, under CHANGES 1-2.

## What came back (`out/result.json`)

Sixteen corpus readings were made: the 12 rows of atlas.json the atlas did not skip (eight DataShop exports,
EDM Cup, EdNet, XES3G5M, Eedi), ASSISTments 2012-13 and the three SLAM courses at the construct grain.
(Correction, 2026-10-13: an earlier version of this README said eighteen.) The identity (cell = N x O x P1 x P2) held on every sampled
pair of every corpus.

**C1: ORDER VARIATION DOES NOT SEPARATE THE CORPORA** (all four versions: every corpus, those with
coverage, and both over Table 1's seven rows). The three corpora deciding more than 0.22% of their pairs
have W of 0.371 (XES3G5M), 0.896 (Eedi) and 0.973 (EdNet); corpora deciding at most 0.22% reach W 0.857
(ds1275, at the area grain), 0.674 (ASSISTments) and 0.598 (SLAM en_es). XES3G5M, where on the median pair only 0.2% of learners met the two skills in the less common order
(median minority share 0.002; EDM Cup's is 0.0), decides the second most. (Corrected 2026-10-13: an
earlier version called XES3G5M's order the most uniform of any large corpus.)

**V2: DOCUMENTATION DISAGREES** on 13 of the predicted labels. No prediction of ORDER-LIMITED backward for
ASSISTments, EDM Cup or SLAM came true at the corpus level: each reads COVERAGE-LIMITED.

**What empties the cell** (forward / backward label; Table 1's rows):

| corpus | decided | median N | W | forward | backward |
| --- | ---: | ---: | ---: | --- | --- |
| ASSISTments 2012-13 | 0.22% | 4 | 0.674 | CELL FILLS | COVERAGE-LIMITED |
| EDM Cup 2023 | 0.015% | 0 | 0.132 | COVERAGE-LIMITED | COVERAGE-LIMITED |
| Junyi ds1275 (8 areas) | 0.00% | 38.5 | 0.857 | RETRY-LIMITED | COVERAGE-LIMITED |
| SLAM en_es constructs | 0.10% | 25 | 0.598 | COVERAGE-LIMITED | COVERAGE-LIMITED |
| EdNet KT1 | 0.65% | 415 | 0.973 | CELL FILLS | CELL FILLS |
| XES3G5M | 4.03% | 12 | 0.371 | CELL FILLS | COVERAGE-LIMITED |
| Eedi | 25.36% | 420 | 0.896 | CELL FILLS | CELL FILLS |

Read by coverage band, order does what the floor said it would. Among well-covered pairs, the backward
direction reads ORDER-LIMITED on ASSISTments (N 5-99), EDM Cup (N 5-99), SLAM en_es (N 5 and over),
XES3G5M (N 5 and over) and the DataShop tutors, while the forward direction fills on ASSISTments, EDM Cup
(N 20 and over), SLAM (N 100 and over), XES3G5M and most tutors.

Three readings follow, for the paper to weigh:
1. **Coverage, not order, is what most often empties the cell** in the corpora with few decisions: most
   sampled pairs of skills are attempted by fewer than 5 learners in common (median N 0 on EDM Cup, 4 on
   ASSISTments).
2. **Where pairs are covered, a uniform order empties only the reverse direction.** The curriculum's own
   direction usually fills, as the fixed world of the floor planted.
3. **A filled cell is not a decision.** The DataShop tutors ds671, ds1530, ds1531 and ds1706 fill their
   forward cells and decide none of their pairs, and ASSISTments fills forward and decides 0.22%: what
   stops a verdict there lies after positivity (the size of the drop against the bar, and power).

Difficulty (descriptive, CHANGES 3): on Eedi, EASE-limited forward pairs had a median P1 of 0.031 but an
all-learner miss rate of 0.335 on the same skill, so "easy" there meant easy for the learners who met a
first, not easy for everyone. Common Core grade against all-learner miss rate: Spearman +0.269 over 259
skills on EDM Cup, +0.167 over 132 on ASSISTments.

The atlas reads Junyi ds1275 at its first KC column, KC (Area): 8 areas, 56 ordered pairs (found by
studies/measurement/difficulty-validation/, CHANGES 2). Its row here is at that grain, like Table 1's.

## The verdict funnel (CHANGES 6; `funnel` in `out/result.json`)

Floor: passed on its third run (two failed runs kept, `out/floor-changes6a.json` and
`floor-changes6b.json`; both failures were in the prereq world's construction). In a world with planted
prerequisites and no ability spread, 40 of 55 SUPPORTED verdicts survived the ability adjustment; in a
world with ability spread and no prerequisites, 16 of 380 did.

On the real corpora the pre-gate SUPPORTED and would-be CONTRADICTED counts equal the atlas's on every
corpus that records them. Pairs reaching each stage, and passing it:

| corpus | sampled | covered | cell >= 5 | readable | powered | decided (atlas) | binding stage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| ASSISTments | 40,000 | 19,699 | 9,940 | 9,350 | 133 | 87 | POWER |
| EDM Cup | 20,000 | 2,032 | 648 | 509 | 6 | 3 | POWER |
| Junyi ds1275 (areas) | 56 | 46 | 26 | 23 | 2 | 0 | GATE (2 powered pairs, both withdrawn) |
| SLAM en_es | 20,000 | 13,684 | 5,253 | 5,000 | 125 | 19 | POWER |
| EdNet | 19,740 | 19,734 | 16,202 | 16,201 | 236 | 128 | POWER |
| XES3G5M | 20,000 | 10,926 | 5,073 | 4,851 | 1,148 | 805 | POWER |
| Eedi | 20,000 | 17,111 | 13,243 | 13,120 | 5,797 | 5,073 | POWER |

**POWER binds in every large corpus.** Among readable pairs the median identifying cell is 21 learners on
ASSISTments, 19 on EDM Cup and SLAM en_es, 43 on EdNet, 50 on XES3G5M and 178 on Eedi, against 277 to 379
per group that a test needs to see the claimed 0.10 drop at each corpus's median control accuracy. Only
Eedi's cells approach that size, and it is the only corpus where more than a quarter of readable pairs
are powered (44.2%). The DataShop tutors ds1530 and ds1531 stop at READABILITY: every control arm sits at
the ceiling.

**The verdicts that exist are mostly general ability.** Of the SUPPORTED pairs, the share whose drop still
reaches its MDE after each learner's general accuracy is taken out is 13.5% (99 of 736) on XES3G5M, 9.2%
(11 of 119) on EdNet, 13.9% (684 of 4,935) on Eedi and 27.6% (24 of 87) on ASSISTments: VERDICTS ARE MOSTLY
ABILITY on all four. EDM Cup, SLAM and the tutors have too few verdicts to test.

So the funnel's answer to "why do some corpora reach verdicts" is scale, and its answer to "what are those
verdicts" is mostly that learners who fail one skill are weaker learners in general.

## Junyi at the exercise grain (CHANGES 7; `out/junyi-exercise.json`, `out/junyi-exercise-atlas.json`)

Read at KC (Exercise), ds1275 has 2,063 learners over 631 exercises. Through atlas.audit unchanged: 20,000
pairs scored, median identifying cell 0, 0.09% readable (18 pairs), none supported or contradicted, decided 0.00%,
background drop +0.204. Both directions read COVERAGE-LIMITED: the median pair of exercises has 1 learner
in common (W 0.521 over the pairs with enough learners to judge). In the funnel, 2,905 pairs are covered,
38 have an identifying cell of 5 or more, 18 are readable and none is powered: the readable cells hold a
median of 7.5 learners against the 336 per group a test of the 0.10 drop needs.
