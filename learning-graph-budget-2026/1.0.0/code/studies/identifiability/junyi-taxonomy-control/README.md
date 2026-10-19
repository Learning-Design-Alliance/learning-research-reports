# Junyi rater validity against a taxonomy-distance-matched control

Script: `taxonomy_control.py`. Its docstring is the pre-registration (committed in `2f701b1` before any
real number was computed). Outputs: `out/floor.json`, `out/floor.log`, `out/taxonomy-control.json`,
`out/run.log`, `out/history-entry.json` (the two logs are gitignored).

## What was asked

Paper II's F4 rests partly on `studies/identifiability/junyi/expert_vs_data.py`, section 3. It reports a
Spearman correlation of +0.299 [−0.017, +0.571] between Junyi crowd raters' mean Prerequisite rating
and a learner-order gap, over 47 rated pairs. The literature review (strand 1, entry 1.15; ranked
analysis 5) notes that in VISL on Eedi, raters' "sensibility" judgments track topic proximity. If Junyi
raters favor same-topic pairs, and learner gaps are also larger for same-topic pairs, the correlation
could come from taxonomy distance and not from pair-specific dependence. The question: does the
rater-learner association survive conditioning on taxonomy distance?

Taxonomy distance comes from the exercise table: 0 means same topic, 1 means same area but a different
topic, and 2 means a different area. The pre-registered tests are:

- a partial Spearman correlation given distance;
- a within-treatment derangement within distance level;
- an external control: unrated pairs matched on distance, the dependent's area and learner coverage,
  drawn without replacement and the same size as the treatment, with a bootstrap over pairs.

The verdict strings and thresholds are in the docstring.

## What came back

### Learner side: run on ds1275, 2026-10-08

**Verdict: EXPLAINED BY TAXONOMY DISTANCE (UNDERPOWERED: floor F2 failed).**

Earlier (2026-10-07) this section read BLOCKED: ds1275 was not on disk, and the 999-row public sample
gave 0 rated pairs against the committed 47. On 2026-10-08 the script ran unchanged on DataShop ds1275,
'All Data' sample (`ds1275_student_step_All_Data_2872_2026_0916_191215.txt`). Its MD5,
`edbbcaf83211085be980ab02ff186127`, matches `data/data-sources.json`. No design, threshold or verdict
string was changed. The held sections below came out identical to the 2026-10-07 run (same seed).

**Reproduction check: passed.** 47 rated pairs reach 15 learners in each order, and the positional
Spearman is +0.29914, equal to the committed value.

Treatment pairs (n = 47; distance 0 / 1 / 2: 18 / 26 / 3; median coverage 84 learners):

| quantity | value | what it is |
| --- | --- | --- |
| ρ_T | +0.297 | Spearman(rating, gap), tie-averaged ranks |
| ρ_p given distance | +0.127 | partial Spearman; below 0.5·ρ_T = 0.149 |
| ρ_p given map distance (sensitivity) | +0.195 | |
| C1 mean | +0.179 (SD 0.100), one-sided p = 0.12 | 2,000 derangements of the gaps within distance level; 0 pairs dropped |
| C2 mean ρ_C2 | +0.231 (SD 0.127 over assignments) | 2,000 matched-control assignments; at least 0.5·ρ_T |
| Δ = ρ_T − ρ_C2 | +0.066 [−0.308, +0.434] | 2,000 bootstrap replicates over treatment pairs, each redrawing the control assignment |
| Spearman(rating, distance), treatment | −0.635 | |
| Spearman(gap, distance), treatment | −0.322 | |
| Spearman(gap, map distance), treatment | −0.268 | |

The C2 pool holds 1,394 unrated ordered pairs with at least 15 learners in each order. 0.3% of them are
authored edges. Their Spearman(gap, distance) is −0.089, and the mean gap is +0.017 / +0.001 / −0.024
at distance 0 / 1 / 2. All 47 treatment pairs matched under the strict rule (P2 met). The control has
47 pairs (1.00×) and median coverage 114 against 84 (1.36×).

Direction check: both signs the confound needs are negative. Raters rate nearer pairs higher (−0.635),
and nearer pairs show the larger prerequisite-first gap (−0.322 in the treatment, −0.089 in the pool).
This is the configuration in which distance can produce a positive ρ_T. Both pre-registered criteria
fire: the matched control reproduces 78% of ρ_T (0.231 / 0.297), and partialling distance leaves 43%
(0.127 / 0.297). Hence EXPLAINED.

The F2 suffix is pre-registered: with the floor's power check failed, any verdict other than SURVIVES
"is not a finding about the raters". Read with the floor beside it: at the observed size of about 0.30
the instrument reaches SURVIVES in only 31.4% of synthetic datasets (80% MDE 0.50). So this run cannot
establish that the raters carry no pair-specific signal. It can say that the 47-pair association is
mostly reproduced by distance alone.

Post-hoc, not part of the verdict:

- In the floor, a genuine pair-specific effect planted at 0.30 (S1) was called EXPLAINED in 0% of
  datasets and MIXED in 2.4%. A distance-only confound (S2) was called EXPLAINED in 87%.
- The floor drew distance levels from all rated rows (54% / 21% / 25%). The treatment's are 38% / 55% /
  6%, with only 3 pairs at distance 2. The floor was not re-shaped or re-run.

### Detection floor (synthetic, 500 datasets per scenario)

Run 2026-10-07, before the learner data; not re-run.

The synthetic datasets have 47 pairs. Distance levels follow the rated rows (0.542 / 0.211 / 0.247).
Each matched-control pool is 10 times the treatment size. Each dataset uses 200 control assignments
and 400 bootstrap replicates; these are fewer than the real run's 2,000, to fit the shared machine.

| scenario | mean ρ_T | SURVIVES | EXPLAINED | MIXED |
| --- | --- | --- | --- | --- |
| S0 null | +0.003 | 0.6% | 5.2% | 18.0% |
| S2 distance only | +0.303 | 0.0% | 87.0% | 10.0% |
| S1 specific, planted 0.30 | +0.312 | 31.4% | 0% | 2.4% |
| S1 specific, planted 0.50 | +0.506 | 84.0% | 0% | 0.4% |

- **F1 PASS** (confound recognized): when distance alone produces ρ ≈ 0.30, the instrument never
  calls SURVIVES, and calls EXPLAINED or MIXED in 97.0% of datasets.
- **F3 PASS** (size): S0 reaches SURVIVES in 0.6% of datasets.
- **F2 FAIL** (power): at the observed size of 0.30, SURVIVES is reached in only 31.4% of datasets.
  The 80% minimum detectable effect is 0.50.

The script that defines this floor also scores it, so it is a smoke check, not an independent
validation.

If ds1275 becomes available, the instrument can tell a distance artifact from a dependence signal. At
n = 47, however, it cannot establish a true pair-specific effect as small as the observed one.
Therefore, with ds1275, the most likely outcome for a genuine effect is "SURVIVES IN POINT, NOT
ESTABLISHED (UNDERPOWERED)". The outcomes most informative for F4 are EXPLAINED and MIXED.

### Held data: raters follow taxonomy distance strongly

This uses all 1,954 rated rows. The bootstrap resamples 1,638 unordered pairs, 2,000 replicates.

- Spearman(rating, distance) = **−0.740 [−0.759, −0.720]**. The sign is negative: raters rate nearer
  pairs as better prerequisites.
- Mean rating is 5.96 at distance 0 (n 1,060), 3.71 at distance 1 (n 412) and 2.32 at distance 2
  (n 482).
- Using knowledge-map Euclidean distance instead gives −0.672 [−0.696, −0.647].

So one of the two conditions the confound needs holds, and strongly. The other condition, that learner
gaps also fall with distance, could not be measured.

### Auxiliary: authored map against raters, distance-matched

This is section 2 of `expert_vs_data.py`. Authored rows are rated above other rated rows with
d = **0.955 [0.842, 1.065]**.

80% of authored rated rows are same-topic (311 of 387), against 48% of the other rows (749 of 1,567).
Comparing authored rows with other rows only at the same distance gives d_strat = **0.442 [0.363,
0.523]**, standardized by the overall SD as pre-registered. That is below half of d_raw, with the
interval above 0. The pre-registered verdict is **MAP-RATER AGREEMENT ATTENUATED BY DISTANCE**.

Post-hoc, not part of the verdict:

- Authored rows are rated higher at every level, by +1.03, +0.68 and +0.41 on the 1–9 scale at
  distances 0, 1 and 2.
- Standardized by within-level SDs, d is 0.622, which is above half of d_raw.

The attenuated/survives boundary therefore depends on the choice of SD. The robust reading: about half
of the map-rater agreement is carried by distance, and a clear within-distance remainder is left. This
compares catalogue with catalogue, since the same authors made the map and the taxonomy. In addition,
the rated pairs were chosen from the knowledge tree.

## What it means for F4

The finding stays at "points the right way, not established", and the reason is now measured, not
hypothesised. Taxonomy distance explains a large share of rater judgments (ρ = −0.740 over all rows).
On the 47 pairs, distance also carries most of the rater-learner association. A distance-matched
control reproduces +0.231 of the +0.297, and partialling distance leaves +0.127. Paper II should not
present the +0.299 as evidence of rater validity. Because floor F2 failed (31% power at 0.30), it also
should not state that the raters lack a pair-specific signal.

## Coders

Prerequisite ratings come from Chang, Hsu and Chen's (EDM 2015) crowd raters: 3–15 per row, on a 1–9
scale. Split-half agreement is in `expert_vs_data.py` section 1. No model coded anything here.
Taxonomy distance is a rule applied to the release's own `topic` and `area` columns.

## Runs

- 2026-10-07: floor; held sections; learner side BLOCKED (ds1275 not on disk).
- 2026-10-08: learner side on ds1275 'All Data' (MD5 matched), unchanged script and seed:
  `DS1275_DIR=<dir> python3 taxonomy_control.py`. The log (`out/run.log`) is
  gitignored.
