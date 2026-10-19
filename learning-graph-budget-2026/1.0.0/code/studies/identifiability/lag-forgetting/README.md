# Lag decay: forgetting of A, or the edge weakening? (`lag_forgetting.py`, 2026-10-07)

**Asked.** Paper II's F1 says the prerequisite drop shrinks with the lag between A and B
(`studies/identifiability/overlap/lag_bands.py`: D = drop(≥ 7 d) − drop(< 1 d) is −0.062 on
ASSISTments, −0.033 on XES3G5M, −0.015 on EdNet and −0.048 on Eedi, verdict LAG-DEPENDENT). The literature
review (synthesis row 4, strand-2 analysis 1; entries 2.14 Cepeda et al. 2008 and 2.20 Matayoshi et al. 2025)
gives a second reading: the drop may shrink because A's own advantage fades, not because B depends less
on A. This study tries to separate the two by holding A's current state at B fixed, describes both arms'
absolute B accuracy by lag, and tests a rise-then-fall (Cepeda) profile.

**Came back.** Every registered verdict is **UNANSWERABLE**, because the synthetic floor failed. The
programme verdict is UNRESOLVED, with no corpus answerable. Positivity is also thin: XES3G5M has
too few learners who re-attempt A within a day of B at long lags (17 readable pairs, threshold 30). The
values computed on real data are reported below so the maintainer can judge whether to re-register,
but they come from an instrument that did not pass its floor, so they are not findings.

## Design record

The design was committed before any real corpus was read (`62fb970`). The first floor failed, and a dated
CHANGES entry in the docstring revised the design, still before any real read (`49206aa`). The second
floor failed on power, and the real run followed (`4c0017f`). The docstring is the full pre-registration.

**Definitions.** A learner-pair case is a learner who touched A before first touching B. Lag runs from the first A
attempt to the first B attempt, as in lag_bands. A *recent A attempt* is the last A attempt before B,
provided it falls within W = 1 day of B. In the EARLY band every case has one.

**Primary, as revised (Wald split).** The analysis uses cases with at least two A attempts before B, the last of them within a day.
The arm (MASTERED′ / FAILED′) is defined from the A attempts *before* that last one, so the last attempt's
outcome R is a fresh, equally noisy reading of A in both arms. Per band, the analysis computes the drop in B, the
arms' gap in current A accuracy (`gap`), and their ratio E = drop / gap, the drop per unit of current
A gap. Under pure forgetting E is constant across lag and the gap shrinks. Under a weakening edge E falls.
D_held = drop_LATE × gap_EARLY / gap_LATE − drop_EARLY. Share explained = (D_sub − D_held) / D_sub,
signed. Intervals are 95% from 2,000 cluster-bootstrap draws resampling B items. Verdict strings (MOSTLY-FORGETTING,
EDGE-WEAKENS, NO-DECAY-TO-SPLIT, UNRESOLVED-NO-A-GAP, UNRESOLVED) and thresholds are in the docstring.

## Floor (synthetic, 48-item gated chain, 3,000 learners, 3 seeds per world)

| world (planted) | v1 single-reading split | v2 Wald split | v2 shape | 9,000-learner diagnostic (gates nothing) |
| --- | --- | --- | --- | --- |
| FORGET: constant gate, A forgotten at 1/10 per day | EDGE-WEAKENS 3/3 (share +0.19, +0.12, +0.13) | MOSTLY-FORGETTING 3/3 (share +1.15, +1.45, +2.57) | never NON-MONOTONE | MOSTLY-FORGETTING 3/3 |
| EDGE: gate × exp(−lag/10 d), no forgetting | EDGE-WEAKENS 3/3 | EDGE-WEAKENS 2/3; third NO-DECAY-TO-SPLIT (D_sub −0.024 [−0.049, +0.001]) | never NON-MONOTONE | EDGE-WEAKENS 3/3 |
| NULL: constant gate, no forgetting | NO-DECAY-TO-SPLIT 3/3 | NO-DECAY-TO-SPLIT 3/3 | — | NO-DECAY-TO-SPLIT 3/3 |
| HUMP: gate peaks at 2 d | — | — | NON-MONOTONE 2/3 | NON-MONOTONE 3/3 |

- **v1 failed for a structural reason.** With a 0.20 guess rate, one correct recent A answer does not
  show that a past master still holds A, so the single-reading split read pure forgetting as an edge
  weakening.
- **v2 failed on power, not on direction.** No world ever returned another world's verdict. The
  identical floor at 9,000 learners passes both parts (`out/floor_diagnostic_9000.json`), but it was
  never registered as the gate.
- Outputs: `out/floor_v1_failed.json`, `out/floor.json`.

## Positivity (step 1)

Learner-pair cases are pooled over the 10,000 sampled pairs per corpus (lag_bands' sample). The table
shows how many have a recent A attempt and how many pairs are readable for the Wald split (≥ 5 cases per arm).

| corpus | LATE (≥ 7 d) cases | with a recent A attempt | of which FAILED | Wald-readable pairs EARLY / MID / LATE | held pairs (both EARLY and LATE) |
| --- | ---: | ---: | ---: | --- | ---: |
| ASSISTments 2012–13 | 578,841 | 40,412 (7.0%) | 2,060 | 323 / 30 / 121 | 59 |
| XES3G5M | 2,262,689 | 16,334 (0.7%) | 627 | 70 / 41 / 50 | **17: UNANSWERABLE** |
| EdNet KT1 (6,000 learners) | 876,113 | 140,772 (16.1%) | 6,296 | 2,757 / 1,432 / 856 | 632 |
| Eedi (latest answers only) | 10,133,623 | 633,398 (6.3%) | 58,791 | 3,636 / 563 / 3,018 | 2,692 |

The scarce cell is the long-lag non-master who comes back to A within a day of meeting B. On Eedi a
"recent A attempt" is the latest answer to *another* question of subject A, because Eedi keeps only each
learner's last answer to each question.

## As computed on real data. Not findings: the floor failed.

| corpus | held pairs | drop EARLY → LATE | A gap EARLY → LATE (change [CI]) | E EARLY → LATE | D_sub [CI] | D_held [CI] | share explained [CI] | would-be verdict |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- |
| ASSISTments | 59 | 0.153 → 0.143 | 0.492 → 0.403 (−0.088 [−0.153, −0.023]) | 0.31 → 0.35 | −0.011 [−0.104, +0.087] | +0.020 [−0.083, +0.133] | +2.86 [−8.90, +7.14] | NO-DECAY-TO-SPLIT |
| EdNet | 632 | 0.045 → 0.040 | 0.052 → 0.080 (+0.028 [+0.008, +0.047]) | 0.88 → 0.50 | −0.005 [−0.025, +0.014] | −0.019 [−0.036, −0.001] | −2.62 [−24.40, +16.52] | NO-DECAY-TO-SPLIT |
| Eedi | 2,692 | 0.163 → 0.124 | 0.237 → 0.179 (−0.058 [−0.066, −0.050]) | 0.686 → 0.694 | −0.038 [−0.047, −0.029] | +0.002 [−0.008, +0.013] | **+1.05 [+0.81, +1.43]** | MOSTLY-FORGETTING |

- **Eedi.** As computed, the whole decay tracks the shrinking A gap: the drop per unit of current A gap does not
  move (0.686 to 0.694). The gap does not shrink because past masters forget A. Their current A
  accuracy is flat (0.618 to 0.624), while the non-masters' rises (0.381 to 0.445). So the convergence is
  in A's state, but it comes from the disadvantaged arm catching up, not from Matayoshi-type forgetting
  by the advantaged arm. The pre-registered string "MOSTLY-FORGETTING" names that convergence; it does
  not show that anyone forgot.
- **ASSISTments and EdNet.** The decay vanishes once cases are restricted to learners with two or more
  A attempts and a recent one. On the same kind of subset, lag_bands' D is −0.062 and −0.013 over all
  cases. So there is nothing to apportion there, and selection into re-attempting A is itself a large
  part of the picture.
- **The v1 single-reading split** (failed floor) is in the JSON as `single_reading`. It is not interpreted.

## Both arms' absolute B accuracy (descriptive, lag_bands' arms and pairs)

| corpus | pairs | MASTERED < 1 d → ≥ 7 d (dM [CI]) | FAILED < 1 d → ≥ 7 d (dF [CI]) | D | label |
| --- | ---: | --- | --- | ---: | --- |
| ASSISTments | 644 | 0.625 → 0.649 (+0.024 [+0.011, +0.037]) | 0.467 → 0.553 (+0.086 [+0.064, +0.108]) | −0.062 | DISADVANTAGED-RISES |
| XES3G5M | 174 | 0.794 → 0.814 (+0.020 [+0.004, +0.038]) | 0.648 → 0.699 (+0.050 [+0.025, +0.079]) | −0.030 | DISADVANTAGED-RISES |
| EdNet | 6,168 | 0.646 → 0.640 (−0.006 [−0.014, +0.003]) | 0.589 → 0.596 (+0.007 [−0.002, +0.017]) | −0.013 | NEITHER-DOMINATES |
| Eedi | 4,643 | 0.633 → 0.652 (+0.019 [+0.014, +0.023]) | 0.478 → 0.540 (+0.063 [+0.057, +0.068]) | −0.044 | DISADVANTAGED-RISES |

- **In three of four corpora the gap closes because the disadvantaged arm rises.** The advantaged arm
  rises too, by less. This is the opposite of the forgetting signature: in the floor, the FORGET world
  read ADVANTAGED-FALLS in 3 of 3 seeds, and the EDGE world read DISADVANTAGED-RISES in 3 of 3.
- **This table is descriptive and was not registered as a verdict.** Learners who reach B weeks after A
  differ from same-day learners, and both arms are more accurate at long lags.
- **These numbers do not depend on the failed parts of the floor.**
- **Reproduction against lag_bands.** The pair counts reproduce lag_bands (644, 175, 6,170 and 4,643;
  this study reads 174 and 6,168). ASSISTments' D reproduces exactly (−0.0616 against −0.06158). The
  others differ slightly (XES3G5M −0.030 against −0.033, EdNet −0.013 against −0.015, Eedi −0.044
  against −0.048) because same-timestamp attempts are ordered differently. lag_bands sorts ties by
  (item, outcome), which puts a wrong answer first, while this study keeps the loader's order. Ties are
  0.01% of ASSISTments rows and 78% of XES3G5M rows (one question tagged with several KCs is one
  timestamp), and Eedi is at minute resolution. The sign and the verdict are unchanged in every corpus.

## Rise-then-fall (Cepeda). UNANSWERABLE (floor); as computed:

The drop by lag band (0–1 h, 1 h–1 d, 1–7 d, 7–30 d, 30 d+; mean over readable pairs):

| corpus | 0–1 h | 1 h–1 d | 1–7 d | 7–30 d | 30 d+ | change from 0–1 h to 30 d+ [CI] |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| ASSISTments | 0.159 | 0.127 | 0.108 | 0.095 | 0.082 | −0.075 [−0.099, −0.054] |
| XES3G5M | 0.180 | 0.112 | 0.104 | 0.108 | 0.088 | −0.072 [−0.115, −0.028] |
| EdNet | 0.064 | 0.049 | 0.041 | 0.048 | 0.041 | −0.018 [−0.028, −0.007] |
| Eedi | 0.155 | 0.133 | 0.125 | 0.124 | 0.103 | −0.047 [−0.052, −0.042] |

- **No corpus shows a rise from the first band.** The interior "rise" contrasts are all negative or
  inside their Bonferroni intervals, and the largest drop sits in the first hour everywhere. Under the
  registered rule each corpus would read MONOTONE-DECREASING.
- **The verdicts stay UNANSWERABLE** because the hump world was detected in only 2 of 3 seeds.

## What it means for Paper II's F1

1. **Keep both readings.** The literature review's instruction stands: "the drop shrinks with lag"
   describes the estimand and should not be worded as the edge weakening. This study could not separate
   the two readings with a registered instrument.
2. **Unverified hint 1: forgetting by past masters is not visible.** In ASSISTments, XES3G5M and Eedi
   the gap closes because non-masters do better at long lags. On Eedi, their current accuracy on A rises
   too, while past masters' does not fall.
3. **Unverified hint 2: the edge does not look weaker on Eedi.** Read through the Wald split, which
   failed its floor on power, the drop per unit of A difference is flat. If either hint is wanted in the
   paper, a re-registration with a power-matched floor comes first.
4. **Proposed next step.** Re-register with the floor at the real held-pair scale; the 9,000-learner
   diagnostic already passes. Positivity will not improve for XES3G5M, or for long-lag non-masters
   anywhere.

## Can and cannot say

- **Different learners in each band.** Learners in different lag bands differ, and re-attempting A is
  selected (on ASSISTments and EdNet the decay disappears on the re-attempt subset).
- **Exclusion assumption.** The Wald ratio assumes past mastery moves B only through A's current state
  plus a component that is constant across bands.
- **Dependence the bootstrap misses.** Pairs share A items, and the B-item bootstrap does not absorb
  that dependence.
- **Eedi's clock.** Eedi lags run between latest answers.
- **No coded constructs.** Every quantity is a count of logged outcomes.

## Data and outputs

- **Corpora**, read through lag_bands' adapters from `$LDA_SCRATCH_DIR`; no file is derived:
  - ASSISTments 2012–13 (`assist_rich.csv`)
  - XES3G5M (`attempts.tsv`)
  - EdNet KT1 (zip prefix of 6,000 learners)
  - Eedi NeurIPS 2020 (`answers.tsv`)
- **Bootstrap.** 2,000 draws resampling B items.
- **Outputs (aggregates only):**
  - `out/lag_forgetting.json`: per corpus, positivity by band and every statistic above
  - `out/floor.json`, `out/floor_v1_failed.json`, `out/floor_diagnostic_9000.json`
  - `out/history-entry.json`

Run with `python3 lag_forgetting.py floor`, `floor-diagnostic` or `real`.
