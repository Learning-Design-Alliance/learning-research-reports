# Orientation sortability: does F2 say more than "sort by difficulty"?

Script: `sortability.py` (its docstring is the pre-registration). Outputs: `out/sim.json` (parts a
and b, synthetic only) and `out/real.json` (part c). Design commit `21f88cf`, made before any number
was computed. Literature: review rank 3, strand 2 entries 2.1-2.3 (Verma & Pearl 1990; Reisach et al.
2021, 2023).

## What was asked

1. In each mechanism x difficulty regime of the existing orientation sweep
   (`studies/simulation/learner-sim/orientation_soft.py`, the source of Paper II's F2), how accurately
   do two sorting baselines orient the true edges: "sort by difficulty" (DIFFSORT) and "sort by R² from
   the other skills" (R2SORT)? Does the signed marginal asymmetry beat them? The seeds, graphs and
   learners are the same as the sweep's.
2. What happens under a disjunctive (OR, DINO-type) prerequisite, both for orientation and for the
   conjunctive-interaction reading of `studies/identifiability/conjunctive/stage1_floor.py`?
3. Where do the held authored structures sit on the difficulty-depth axis?

## What came back

**Verdict (a): `F2 REDUCES TO DIFFICULTY SORTABILITY`.** In all 30 cells (15 conjunctive/soft, 15
OR), the asymmetry statistic and the difficulty sort orient every scored edge the same way. D = 0.000,
and the world-bootstrap interval is [0.000, 0.000] in every cell (477-480 edges per cell, 15 worlds).
This is an identity, not a simulation result. Write f_x = P(fail x) and j = P(fail a and fail b).
Then s(a, b) = j/f_a − j/f_b = j(f_b − f_a)/(f_a·f_b), so whenever j > 0 the sign of s is the sign of
f_b − f_a. **The signed marginal asymmetry is "orient from the easier skill to the harder one."** The
difficulty-matched subset applies the same sort to pairs whose failure rates are within 0.05 of each
other, so on that subset too the two agree exactly.

| Conjunctive/soft arm (F2) | asymmetry = difficulty sort | world-bootstrap 95% interval |
| --- | --- | --- |
| ALIGNED, hardness 1.0 to 0.0 | 0.998 to 1.000 | CEILING (sort ≥ 0.95) |
| INDEPENDENT, hardness 1.0 | 0.883 | [0.854, 0.910] |
| INDEPENDENT, hardness 0.0 | 0.773 | [0.736, 0.809] |
| INVERTED, hardness 1.0 | 0.772 | [0.721, 0.814] |
| INVERTED, hardness 0.0 | 0.520 | [0.462, 0.580] |

So the mechanism-by-regime grid maps how sortable each generator is. The gate itself makes dependents
fail more often, so in the INDEPENDENT regime the observed Spearman(depth, failure rate) is +0.47 to
+0.65, although the latent difficulty is unrelated to depth (latent Spearman −0.05). In INVERTED worlds
the gate pulls the observed order back toward the true one (+0.39 at hardness 1.0, −0.15 at 0.0)
against a latent −0.93. That is why orientation "depends on mechanism and difficulty regime." The
"difficulty-matched control discards signal" reading becomes: the matched subset keeps only the pairs
with small difficulty gaps, where the sort is noisier.

**Floor (a):** passed. PLANT-SORT (the sort itself, ties broken at random) read NO BETTER in 1.00 of
50 reps in every non-ceiling cell. PLANT-ADD detected a planted increment of 0.05 with minimum power
1.00 (conjunctive) and 0.98 (OR), so the minimum detectable increment is 0.05. The asymmetry
accuracies reproduce `orientation-soft-result.json` exactly (maximum absolute difference 0).

**R2SORT: not validated.** On the linear-Gaussian check it oriented 0.665 of 480 edges, below the
pre-registered 0.70; the accuracy was identical on standardized data. The pre-registered secondary
verdict, "ADDS BEYOND R2 SORTABILITY", therefore carries "(R2SORT NOT VALIDATED)". In the binary sweep,
R2SORT points backward: 0.088 to 0.223 in the conjunctive arm and 0.280 to 0.415 in the OR arm, with
a deeper skill less predictable from the others. That is a property of this generator. It is not
evidence for the asymmetry statistic.

**(b1) OR arm: `OR ARM REDUCES TO DIFFICULTY SORTABILITY`** (the same identity applies). A disjunctive
prerequisite hardly makes the dependent fail more often, so orientation collapses wherever the latent
difficulty does not already rise with depth:

| OR arm | all edges | edges into fan-in ≥ 2 | conjunctive arm, fan-in ≥ 2 |
| --- | --- | --- | --- |
| ALIGNED | 0.969 to 0.975 | 0.957 to 0.966 | 1.000 |
| INDEPENDENT | 0.551 to 0.558 (lower bounds 0.495 to 0.501) | 0.484 to 0.504 | 0.821 to 0.949 |
| INVERTED | 0.069 to 0.098 | 0.009 to 0.020 | 0.633 to 0.966 |

Under OR with difficulty falling with depth, the statistic confidently orients edges the wrong way:
about 98% to 99% of edges into multi-parent nodes are reversed.

**(b2) Conjunctive census on OR: descriptive only, because the census floor failed.** The wrapper
reproduced stage 1's conjunctive detection (12 of 12 gated arms fired), but 1 of 16 control arms fired
(additive, co-parent 0.6, gate 0: interaction +0.0415 against a null 97.5th percentile of +0.0305).
Under the pre-registered rule, the OR numbers are therefore not a census reading. Descriptively, all 12
gated OR arms gave a negative interaction (−0.20 to −0.40), below the null's 2.5th percentile; none
was misread as a conjunction. The pairwise A-drop fell under the 0.10 background in 4 of 12 arms, and
these were the arms where the co-parent is common (prevalence 0.6 at gate 0.5, and 0.8 at gates 0,
0.25 and 0.5). This is the opposite corner from the conjunctive blind spot. The one-sided census
records a disjunction as "no conjunction." The floor failure suggests that stage 1's rule (the median
of 20 reps against the 97.5th percentile of 20 deranged nulls) has a false-fire rate above zero. Stage
1's own seed had 0 of 12 additive arms firing.

**(c) Regime placement.** Difficulty is 1 − the share correct on each learner's first attempt. Units
need at least 20 learners.

| Corpus | n | S (share of pairs where the dependent is harder) | Spearman(depth, difficulty) | Floor | Verdict |
| --- | --- | --- | --- | --- | --- |
| ASSISTments 2012-13, CCSS grade, all matched skills | 131 skills, 8 grades, 6,871 cross-grade pairs | 0.576 [0.503, 0.647] | +0.187 [+0.001, +0.364] | pass (0.93 / 0.88 correct sign, 0.07 wrong sign at r = 0) | **DIFFICULTY RISES WITH DEPTH (ALIGNED SIDE)** |
| ASSISTments, exact-name tier | 66 skills, 6 grades, 1,577 pairs | 0.590 [0.490, 0.688] | +0.210 [−0.025, +0.438] | fail (0.67 / 0.63) | UNDERPOWERED |
| Junyi 2015, authored graph (981 edges), ds1275 log | 236 exercises, 48 depths, 233 eligible edges | 0.579 [0.515, 0.639] | +0.476 [+0.388, +0.551] (node-resampled +0.335 [+0.207, +0.447]) | **fail** (0.01 / 0.07 correct sign; 0.01 wrong sign at r = 0) | **DIFFICULTY RISES WITH DEPTH (ALIGNED SIDE)**, floor failed (see below) |
| Junyi 2015, public 999-row sample (superseded) | 2 of 238 logged exercises reach 20 learners; 0 eligible edges | — | — | — | UNANSWERABLE |
| Eedi | — | — | — | — | NOT HELD (no authored prerequisite graph) |

The ASSISTments intervals resample skills (2,000 draws; the pairs are rebuilt from the resampled
skills). ASSISTments has no authored prerequisite graph on hand, so depth is the CCSS grade of the
name-matched code. Its weak alignment (S 0.576) is closest to the sweep cell CONJUNCTIVE/INVERTED/0.25
(0.603). Because of the identity, the asymmetry statistic would agree with grade order there about as
often as the difficulty sort does, and no more.

**Junyi 2015 on ds1275 (run 2026-10-08).** Junyi's public log sample (`junyi_ProblemLog_for_PSLC.txt`,
642 learners) was too thin, so the loader was changed to read the DataShop ds1275 student-step export
(CHANGES 2026-10-08 in the docstring, committed `1a1570f` before this study read any ds1275 row; the
file is `ds1275_student_step_All_Data_2872_2026_0916_191215.txt`, sample 'All Data', and its MD5
`edbbcaf83211085be980ab02ff186127` matched `data/data-sources.json` before the run). Mapping: learner =
`Anon Student Id`, exercise = `KC (Exercise)`, time = `Step Start Time`, outcome = `First Attempt`
(correct/incorrect; steps whose first action was a hint, 53,604 of 303,720, are skipped as the public
loader skipped HINT rows; 110 rows with no KC or time). All 631 logged exercises match a name in the
authored exercise table, so the authored graph joins exactly. 236 exercises reach 20 learners, and 233
of the 981 authored edges have both ends eligible, spanning 48 depths.

The pre-registered placement is **DIFFICULTY RISES WITH DEPTH (ALIGNED SIDE)**: the dependent is harder
than its prerequisite on S = 0.579 [0.515, 0.639] of the 233 eligible authored edges (interval
resamples edges), and Spearman(depth, difficulty) is +0.476 [+0.388, +0.551] over the resampled edges'
endpoints (+0.335 [+0.207, +0.447] when nodes are resampled, the stated sensitivity). 2,000 draws,
percentile. **The floor failed, and the verdict is read with that beside it.** On this edge set and
these learner counts a planted latent r = +0.3 (−0.3) was placed with the correct sign in only 0.01
(0.07) of 100 reps, so the instrument cannot see a difficulty-depth relation of that size. Its other
half held: at r = 0 a wrong-signed placement occurred in 0.01 of reps (bar 0.10). Under the
pre-registered rule the floor only separates "NO ORDER RESOLVED" from "UNDERPOWERED"; it does not
withhold a placement both intervals resolve, so the verdict string stands as computed. What the failed
floor means: a null here would have been uninformative, and the real relation is much stronger than
the planted one. (Why the planted 0.3 is invisible was not measured; the likely reason is that
authored edges join nearby depths, so a depth-level correlation of 0.3 barely changes the difficulty
gap along one edge, and S cannot leave 0.5.) S is closest to the sweep cell CONJUNCTIVE/INVERTED/0.25
(DIFFSORT 0.603), where the asymmetry statistic reads NO BETTER than the sort: by the identity, on
Junyi it would agree with the authored direction on about 58% of eligible edges, as the difficulty sort
does, and no more.

ds1275 is not Junyi's full log. Its own README titles it "Partial Samples" (1/120 of users, 2,063
students); the full log is an extra file of DataShop ds1198, not held. The ASSISTments rows and the
rater descriptive reproduced the committed `out/real.json` exactly on this run (the Junyi branch now
draws from its own stream, so the shared stream is unchanged).

As a descriptive count only, the Junyi 2015 crowd raters, averaged (coder: the raters of Chang, Hsu &
Chen 2015; no independent reference was computed, so this gates nothing), rated the dependent harder
than its prerequisite on 0.715 [0.681, 0.748] of 652 rated authored pairs. The mean was +0.62 [+0.52,
+0.72] on the 1-9 scale relative to "equal" (5). The intervals resample pairs.

## What it means for Paper II

F2 should be stated as an instance of sortability (Reisach et al. 2021, 2023). The signed marginal
asymmetry is algebraically a difficulty sort, so its success in simulation measures how far observed
difficulty rises along the true edges. The gate mechanism matters because it adds to that rise. AND
gates add a lot, OR gates almost nothing. The paper should not say that the statistic reads direction
from dependency beyond difficulty.

On real data the same identity applies wherever the statistic was computed as `signed_marginal` on a
single population. The 0.464 agreement on ASSISTments cited in `orientation_difficulty.py` is then a
difficulty-order agreement. This was not re-checked here, and `shared/direction_contrast.py`'s
within-pair delta is a different statistic that this identity does not cover.

## Cannot say

Nothing here concerns real orientation truth or other generator families. ASSISTments is placed only
as a grade order, not as a graph. Junyi is placed on 233 of its 981 authored edges (the eligible ones,
from a 1/120 user sample) with a failed power floor, so the size of its alignment is not established,
only its sign. Eedi is not placed.

    python3 sortability.py sim     # ~25 min on one core
    LDA_SCRATCH_DIR=... DS1275_DIR=... JUNYI_DIR=... python3 sortability.py real   # --junyi-log public for the 999-row sample
