# Is the core-versus-culture split a property of the data, or of the linking?

**Status: pre-registered 2026-10-07 (57af02d); floor passed; run on real data.** Script:
[`linking.py`](linking.py). Its docstring holds the design, controls, thresholds and verdict strings,
and they were committed before any real number was read.

## What it asks

[`../core-vs-culture/invariance.py`](../core-vs-culture/invariance.py) found **CORE AND CULTURAL**
across XES3G5M (China), ASSISTments 2012-13 (US), Eedi (UK) and Junyi 2020 (Taiwan). Dependence
between two Common Core clusters on one platform predicts it on another (pooled b_other +0.125
[+0.091, +0.158]). Local teaching proximity predicts it more strongly (b_prox +0.363 [+0.326, +0.401]).
Paper II reads this as a core plus a larger local layer. The Paper II literature review (strand 6,
"Analyses" rank 7) raised two objections:

1. **Linking** (Oliveri & von Davier 2014; Kreiner & Christensen 2014; Robitzsch & Lüdtke 2023;
   Rutkowski & Svetina 2014). A shared/local split is defined relative to the linking. How far does the
   split move under other reasonable linkings?
2. **Opportunity to learn** (Muthén, Kao & Burstein 1991; Naumann et al. 2014; Huang, Wilson & Wang
   2016; Schmidt, Zoido & Cogan 2014). If the local layer is opportunity to learn, a direct exposure
   term should take over part of what proximity carries, and the core should hold.

**Provisional construct.** Every unit's cluster comes from `../core-vs-culture/out/unit-map.json`.
That map was coded from unit names alone by a language model: openai/gpt-6-sol made the primary map
and deepseek/deepseek-v4-pro the second map. Its human check (`human_codes.py`) is pre-registered but
has not been returned. The map is unchanged here, so this is a robustness analysis of a provisional
construct. Nothing below lifts the bound that the pending check places on the core-and-culture result.

## Reproduction check

The script recomputed all cluster-pair statistics from the raw corpora, streaming Junyi's 3 GB
`Log_Problem.csv` from its zip, and they matched `invariance-pairs.json`: the same pairs, the same n
and P, and D within 8.4e-14. Its re-implementation of the joint bootstrap and permutation (invariance.py
CHANGE 1) reproduced the committed `invariance-result.json` exactly: the points, both intervals and
the null's 97.5th percentile. The L1 and L2 alternatives therefore use the same 2,000 draws as the
baseline, and their changes are paired.

## Floor ([`out/linking-synthetic.json`](out/linking-synthetic.json))

Synthetic only, with no corpus. The floor used 500 draws per world rather than 2,000, because it runs
more than 100 worlds with three estimators each.

- **Re-implementation.** `cross_multi` equals `invariance.cross` on a synthetic world.
- **Huber estimator.** It is within 0.010 of OLS on clean data. With 10% leverage outliers, its mean
  absolute error is 0.167, against 0.390 for OLS.
- **F1 calibration** (invariance.py's worlds, 60 shared pairs). Each estimator claims a false core in
  1 of 40 core-free worlds, so all **pass** (the bar is ≤ 4). Planted core found: OLS 35/40, rank
  34/40, Huber 35/40. Power at core 0.3 is 0.2-0.3 at 60 pairs and 0.9-1.0 at 300 pairs. Real corpus
  pairs share 273-1,134 cluster pairs, and 197-535 at grade.domain.
- **F2 exposure** (300 pairs, E correlated 0.6 with P). **Pass.**
  - Exposure driving the local layer was read as ABSORBS in 20/20 worlds (the bar is ≥ 16).
  - Inert exposure was read as ABSORBS in 1/20 (the bar is ≤ 2).
  - A false CORE HOLDS appeared in 0/20 core-free worlds (the bar is ≤ 2).
  - The CORE HOLDS read on the six-regression subset has modest power at core 0.3: it held in 12/20
    and 13/20 of the core worlds.

## Result 1: linking sensitivity, **LINKING-ROBUST** ([`out/linking-result.json`](out/linking-result.json))

Primary map. Each pooled coefficient is the mean over 12 ordered corpus pairs. Intervals are
percentile 95% intervals from 2,000 joint bootstraps of cluster pairs, and the null is 2,000 joint
permutations (CHANGE 1). R is the ratio b_other / b_prox.

| linking | b_other | b_prox | R | R change from L0 | verdict |
| --- | --- | --- | --- | --- | --- |
| L0 committed: OLS, standardized D, cluster | +0.125 [+0.091, +0.158] | +0.363 [+0.326, +0.401] | 0.344 [0.244, 0.457] | — | CORE AND CULTURAL |
| L1 rank (Spearman-scaled) | +0.130 [+0.093, +0.164] | +0.280 [+0.244, +0.311] | 0.464 [0.326, 0.614] | +0.120 [+0.028, +0.222] (paired) | CORE AND CULTURAL |
| L2 Huber M-estimator | +0.114 [+0.084, +0.145] | +0.358 [+0.318, +0.396] | 0.319 [0.230, 0.422] | −0.026 [−0.065, +0.010] (paired) | CORE AND CULTURAL |
| L3 grade.domain map (43 units) | +0.126 [+0.075, +0.177] | +0.374 [+0.315, +0.428] | 0.337 [0.190, 0.521] | −0.007 (pairs differ, unpaired) | CORE AND CULTURAL |

Cluster pairs per corpus: XES3G5M 930, ASSISTments 972, Eedi 1,531 and Junyi 2,604 at cluster grain;
470, 314, 591 and 735 at grade.domain. The null's 97.5th percentile for b_other was +0.020 to +0.031
under every linking.

- **The verdict string does not change** under any linking. Every R stays inside the pre-registered
  band [0.172, 0.516] (0.5 to 1.5 times R0) and below 1.
- **Rank linking moves the ratio most, upward** (+0.120, paired interval excluding 0). It leaves b_other
  almost unchanged and shrinks b_prox from 0.363 to 0.280. On ranks, part of the proximity coefficient
  goes away: it rested on the shape of the proximity scale, not only on its order. The core is then
  about half the size of the local layer rather than a third.
- Huber and the coarser map leave the split where it was (−0.026 and −0.007).
- **Second map** (descriptive). Every linking also gives CORE AND CULTURAL: R is 0.432 under OLS, 0.695
  under rank (0.501-0.922), 0.421 under Huber and 0.263 at grade.domain. Rank linking again moves R
  the most, and here it comes closest to 1.
- **Median pooling over corpus pairs** (descriptive): R is 0.355 at L0, 0.427 under L1 and 0.320
  under L2.

**Reading.** In this data, the core/culture split does not depend on which of these linkings is used.
The core term is the most stable quantity across linkings (b_other +0.114 to +0.130). The local term
depends on the scale proximity is read on, so the ratio is best stated as a range: the core is about a
third to a half of the local layer (0.32 to 0.46 across linkings under the primary map). It is not a
single linking-free number. That is the literature's point, and it is now quantified here.

## Result 2: exposure term, **EXPOSURE ABSORBS PART OF THE LOCAL LAYER; CORE HOLDS** ([`out/exposure-result.json`](out/exposure-result.json))

**Where co-assignment is recorded.**
- ASSISTments: `assignment_id` in `assist_rich.csv`.
- Eedi: `QuizId` in `answers.tsv`. `GroupId`, the class, is also kept but not used.
- XES3G5M: not recorded. The release has learner, question, concepts, response and time, with no
  exam, class or assignment id.
- Junyi 2020: not recorded. `Log_Problem.csv` has no assignment field, and `Info_UserData.csv` has
  only counts.

The term therefore enters the six regressions whose dependent corpus is ASSISTments or Eedi.

E is defined for each cluster pair: it is the share of that pair's learners (the same learners
`pair_stats` counts; the denominator is asserted equal to n) who answered both clusters within one
assignment or quiz.
- ASSISTments: 931 pairs enter the regressions. Mean E is 0.232; 893 pairs have E > 0, and
  corr(E, P) is +0.575.
- Eedi: 1,313 pairs. Mean E is 0.232; 1,310 pairs have E > 0, and corr(E, P) is +0.745.

Both corpora pass positivity, which uses the median-split rule and |corr| ≤ 0.9.

Pooled over the six regressions (same 2,000 draws, with and without E on the same pairs):

| | without E | with E | change |
| --- | --- | --- | --- |
| b_prox | +0.425 [+0.365, +0.482] | +0.253 [+0.183, +0.325] | **−0.172 [−0.222, −0.120]** |
| b_other | +0.120 [+0.082, +0.161] | +0.114 [+0.076, +0.153] | −0.007 [−0.014, +0.000] |
| b_exp | — | +0.241 [+0.169, +0.308] | |

The null's 97.5th percentile for b_other with E is +0.030.

- **The control is family-matched and deranged.** E was deranged within deciles of P (a Sattolo
  cycle per decile, 200 times), which keeps E's distribution and most of its tie to proximity. Its
  mean |corr(E~, P)| is 0.553, against 0.557 and 0.749 for the real E (0.85 times the real value,
  which passes `check_control_scale`). It moves b_prox by only −0.007 on average (2.5th percentile
  −0.031). The real −0.172 lies far beyond that, so the shrinkage is pair-specific exposure, not
  collinearity with proximity.
- **About 40% of the local layer is taken over by recorded co-assignment** (share absorbed 0.404). The
  carried-over core does not move: its change is −0.007 and its interval reaches 0.
- **Per corpus**, the same verdict holds in each:
  - ASSISTments: b_prox changes by −0.109 [−0.179, −0.039] (control 2.5th percentile −0.042);
    b_exp is +0.172 [+0.064, +0.273]; b_other is +0.102 with E.
  - Eedi: b_prox changes by −0.235 [−0.308, −0.159] (control −0.051); b_exp is +0.309
    [+0.210, +0.404]; b_other is +0.126 with E.

**Reading.** This is the opportunity-to-learn mechanism that Muthén et al. and Huang et al. describe,
seen in skill dependence. Being set two clusters in the same assignment makes learners' performance
on them go together, beyond how close in time they were met. That accounts for a substantial part of
what invariance.py called the local layer. Co-assignment does not account for the cross-country core.
If co-assignment were only a proxy for content relatedness that every country shares, it should have
taken some of b_other, and it took none.

## What it cannot say

- There is no linking-free split, and this study does not supply one. It shows the verdict is stable
  across three reasonable linkings and that the ratio ranges from about 0.32 to 0.46.
- It cannot separate a cognitive core from a mathematics-education culture shared by the four
  countries; that is invariance.py's limit.
- Co-assignment is one opportunity-to-learn channel, and it is recorded on only two of the four
  platforms. Teaching that the platforms do not log is not covered.
- Assignments are also authored. The share of b_prox that E absorbs may partly be the authors'
  judgment of relatedness, not exposure as such.
- Eedi's time is the latest answer, not the first (see the adapter), so its P and E both partly
  reflect quiz scheduling.
- The cluster map is model-coded and its human check is pending.

## Reproducing

```
python3 linking.py --synthetic   # floor, about 1.5 h on a shared 4-core machine
python3 linking.py read          # streams the four corpora into $LDA_SCRATCH_DIR/derived-core-vs-culture-linking/
python3 linking.py analyse       # about 30 min
python3 linking.py clean         # deletes the derived cache (done after this run)
```

`out/linking-pairs.json` holds aggregate cluster-pair statistics for the second map and both
grade.domain maps, plus E for each pair (primary map, cluster grain). The primary-map cluster
statistics are `../core-vs-culture/out/invariance-pairs.json`.
