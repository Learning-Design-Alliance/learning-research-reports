# ECPE positive control: a latent hierarchy test against the programme's instruments

Script: `ecpe_control.py` (its docstring is the pre-registration, with one dated change). Outputs:
`out/fit.json` (fitted parameters), `out/floor.json` (synthetic floor), `out/result.json` (real
readings and verdicts). Literature review for Paper II, rank 11; strand 2 entries 2.7 and 2.9 and
"Analyses" item 4; strand 3 entries 3.14 to 3.17 and "Analyses" item 6.

## What was asked

This study asks whether a likelihood-based latent test finds the attribute hierarchy that Templin and
Bradshaw (2014) reported on the ECPE grammar data, and whether the programme's own instruments find
it on the same responses. The instruments are IITA against the fixed-margins null, the IITA-PAIRSCAN
statistic and the conjunctive interaction test. If the latent test finds the hierarchy and an
instrument does not, that is a detection-floor statement about the instrument, on real data with a
known reference.

**Data.** ECPE (data id `ecpe`): 2,922 examinees, 28 items, and a Q-matrix over 3 skills (skill1
morphosyntactic, skill2 cohesive, skill3 lexical). Templin and Hoffman (2013), as shipped in the CDM R
package 8.3-14. The data are for research use only, with no redistribution, and only aggregates are
committed.

**The hierarchy tested.** H_PUB is the linear chain skill3 (lexical) -> skill2 (cohesive) -> skill1
(morphosyntactic). Its permissible profiles (skill1, skill2, skill3) are 000, 001, 011 and 111.
Templin and Bradshaw's abstract says that a "suspected attribute hierarchy" fits these data better
than a crossed structure, but the abstract does not name the order, and the full text could not be
reached from here. The order comes from a secondary source that reports their result on these data
(Frontiers in Psychology 2018, 9:1875). That is a limit of this study.

## What came back

| | Verdict | Headline |
|---|---|---|
| Reference (latent test) | **HIERARCHY FOUND** | H_PUB not rejected: LR 25.51, bootstrap p = 0.068 (B = 500). H_REV rejected: LR 426.60, p = 0.002 |
| IITA (skill grain) | **UNANSWERABLE** | floor fails: recovers the planted hierarchy in 0.02 of replicates |
| IITA-PAIRSCAN (item grain) | **UNANSWERABLE** | floor fails: 0.25 |
| Interaction test (skill grain) | **UNANSWERABLE** | floor fails: 0.245, and 0.24 in the reversed world |
| Control | **INFORMATIVE** | |

The control is informative. None of the programme's three cross-sectional instruments can see a
latent linear hierarchy of ECPE's shape, even when it is planted. The likelihood-based test can, and
on the real responses it does not reject the published hierarchy, while it rejects the reverse chain
and the other four orders.

### The reference

The model is a saturated diagnostic classification model, equivalent to the saturated LCDM or
saturated G-DINA, fitted by EM in numpy without monotonicity constraints (4 fitted violations). The
hierarchical version gives the four forbidden profiles zero probability. Each test is a
parametric-bootstrap likelihood-ratio test (Ma and Xu 2021): 500 samples of n = 2,922 drawn from the
fitted hierarchical model, with both models refitted on each.

| Chain (bottom -> top) | LR | p (B = 500) | Bootstrap 95th pct |
|---|---|---|---|
| skill3 -> skill2 -> skill1 (H_PUB) | 25.51 | 0.068 | 26.24 |
| skill1 -> skill2 -> skill3 (H_REV) | 426.60 | 0.002 | 24.72 |
| skill3 -> skill1 -> skill2 | 119.89 | 0.002 | 24.11 |
| skill2 -> skill1 -> skill3 | 413.48 | 0.002 | 24.54 |
| skill2 -> skill3 -> skill1 | 94.13 | 0.002 | 25.19 |
| skill1 -> skill3 -> skill2 | 411.18 | 0.002 | 24.33 |

A p of 0.002 is the smallest the bootstrap can give (1/501): none of the 500 bootstrap LRs reached
the observed one.

**The non-rejection is narrow.** 33 of the 500 bootstrap LRs reached the observed 25.51. The
Clopper-Pearson 95% interval on that exceedance probability is [0.046, 0.091], which straddles 0.05.
So "not rejected at 0.05" is inside Monte Carlo error, and a rerun with another seed could reject.
The pre-registered verdict reads the observed p and is HIERARCHY FOUND. The accurate summary is that
the published chain is the only one of the six linear orders the data do not clearly reject. All five
others give LRs 3.7 to 17.3 times their bootstrap 95th percentile; H_PUB's LR sits at its own.

The fitted H_PUB class proportions are 0.320 (000), 0.144 (001), 0.185 (011) and 0.351 (111). Under
the saturated fit, the mass on the four forbidden profiles is 0.041, with a 95% percentile interval of
[0.017, 0.091] from 200 nonparametric bootstrap resamples of examinees. This interval is not a test.
The saturated estimate of a boundary quantity is positive even when the true mass is zero.

### The floor

The floor uses ECPE-shaped synthetic data: the same Q-matrix, n = 2,922, and item parameters from the
real saturated fit, projected to be monotone. The worlds differ only in the profile distribution:

- **PUB:** H_PUB planted.
- **REV:** the mirror chain.
- **ONE:** one continuous trait with thresholds; same margins; forbidden mass 0.10.
- **MIX:** a mixture with independent skills; same margins; forbidden mass 0.10 or 0.05.

**Latent test, which passes.**

- Size: H_PUB rejected in 0 of 60 PUB replicates.
- Power against forbidden mass 0.10: 40 of 40 (MIX 0.10) and 40 of 40 (ONE).
- Power against forbidden mass 0.05: 30 of 30.
- Direction: H_REV rejected in 60 of 60 PUB replicates.
- Each replicate used B = 49 (CHANGE 1).

**Programme instruments, all of which fail.** Each needed a rate of AGREES (recovering the planted
hierarchy in the published direction) of at least 0.80 in PUB, and at most 0.10 in ONE and in REV.

| Instrument | AGREES in PUB | AGREES in ONE | AGREES in REV | Replicates per world |
|---|---|---|---|---|
| IITA, skill grain | 0.02 | 0.01 | 0.00 | 200 |
| IITA-PAIRSCAN, item grain | 0.25 | 0.10 | 0.00 (REVERSED 1.00) | 20 |
| Interaction, skill grain | 0.245 | 0.04 | 0.24 | 200 |

What each failure looks like:

- **IITA.** The relation IITA selects points the published way in every PUB replicate (d > 0 in
  1.00), but the implication count leaves the fixed-margins band in only 0.02 of them. The band is
  degenerate in 0.32. Ability and difficulty already produce the chain, which is the same blindness
  F6 reports.
- **Pairscan.** It fires in only 0.35 of PUB replicates (any significant pair: 0.65). In REV it fires
  in all 20 and reads the reversed direction correctly in all 20. This study did not investigate why PUB and
  REV differ. In ONE, a significant pair appears in every
  replicate (0.95 of them in the published direction), but only 0.10 are ISOLATED.
  - Shared and own calibrations agreed on all 3 replicates checked.
- **Interaction.** The published triple was unscored in 0.29 of PUB replicates and 0.685 of ONE
  replicates, because the cell "cohesive held, lexical not" fell below 20 learners. That cell is the
  one a hierarchy empties. AGREES is as common in REV as in PUB, so the reading is not
  direction-specific.

### The instruments on the real responses (descriptive; every floor failed)

Skill grain: a skill counts as held when at least half of its single-skill items are correct (5, 4
and 10 items). Held rates: skill1 0.693, skill2 0.943, skill3 0.930.

- **IITA, skill grain.** 3 implications, inside the fixed-margins band [2, 3] (R = 500). The relation
  is cohesive -> morphosyntactic, lexical -> morphosyntactic and cohesive -> lexical. The last pair is
  backwards relative to H_PUB, and it follows difficulty: the 4 cohesive items are the easiest. Score
  d = +1; the reversed-arrow control reads CLAIMED (2 against 1). Reading: MISSES.
- **IITA, item grain** (reported only). 160 implications, above the fixed-margins band [97.0, 133.0]
  (R = 200). Of the 109 cross-level implications, 0.826 run low -> high level. That is below the
  null's own band [0.835, 0.880]: beyond ability and difficulty, the extra implications lean against
  the published direction.
- **IITA-PAIRSCAN, item grain** (R = 200).
  - Minimum standardised residual -5.55, max-T p = 0.005. One significant isolated pair, E19-E28,
    both lexical-only items at the same level. No cross-level pair. Reading: MISSES.
  - Its own floor on this matrix: planted PAIR, GATE and CHAIN arrows detected at 1.00, 1.00 and 1.00
    (ISOLATED 1.00, 1.00 and 0.90).
  - Fitted-model false positives: 0 of 2.
  - The scan sees an arbitrary planted 0.9-strength pair here; it does not see the hierarchy.
- **Interaction test, skill grain.**

  | Dependant | Interaction | SE | Verdict |
  |---|---|---|---|
  | skill1 (published triple) | -0.016 | 0.097 | UNKNOWN (MDE 0.271; smallest cell 33) |
  | skill3 (reversed triple) | -0.107 | 0.041 | CONTRADICTED |
  | skill2 | -0.083 | 0.034 | CONTRADICTED |

  The analytic SE agrees with the learner-deranged null (ratios 1.02 to 1.04). Reading: MISSES.

**Not run.** The pairwise drop, the lag profile and the mastery-release contrast need the order and
timing of attempts. ECPE is one cross-sectional administration without timestamps, so this study
says nothing about those instruments.

## What it means for Paper II

These consequences were fixed before the run.

- **F6, IITA.** On real data with an established hierarchy, IITA against fixed margins could not
  have seen it: its floor recovers a planted copy in 0.02 of replicates. This confirms F6's "could not
  have", now against a latent-level positive control.
- **F6, pairscan.** The scan's positives (8 of 15 sets) are local dependence beyond one trait, not
  hierarchy detection. Its nulls do not exclude a hierarchy. A linear hierarchy over three skills is
  close to one ordered trait. On the real attribute correlation, a one-trait threshold model matching
  it has lambda at its 0.999 cap and forbidden mass 2e-14, so the two are not separable here.
- **F1, AND result.** The interaction test has no latent-level positive control on ECPE. Its floor
  fails and its reading is not direction-specific. F1's AND result rests on its planted floor alone,
  and the paper should say so.
- **Synthesis row 6.** Hierarchies are tested at the latent level, and on ECPE such a test sees what
  the programme's pairwise and count statistics cannot. Paper II should present its instruments as
  blind to latent linear hierarchies at assessment scale, and cite Templin and Bradshaw (2014) and Ma
  and Xu (2021) as the method that is not.

## Limits

- The hierarchy's order comes from a secondary source.
- The non-rejection of H_PUB is within Monte Carlo error of 0.05.
- The latent floor used B = 49 per replicate.
- The skill grain uses only single-skill items, so mastery is misclassified at an unestimated rate.
- Pairscan used R = 200 on the real data and R = 100 in the floor (iita_pairscan used 500).
- ECPE is an assessment, not a platform log.
- The floor's per-world median interaction for the published triple was computed as NaN. Unscored
  replicates entered the median: a reporting defect, and no verdict reads it.

Coder of constructs: no coded construct. Skills come from the published Q-matrix, and "held" is a
rule (at least half of single-skill items correct).

Run: `ECPE_DIR=... python3 ecpe_control.py --phase fit|floor|real` (about 1.4 h for the floor and
19 min for the real phase on 3 workers).
