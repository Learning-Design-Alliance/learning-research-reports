# Lag decay, forgetting of A or the edge weakening: a re-registration with matched floors (`lag_forgetting_v2.py`, 2026-10-07)

**Asked.** `studies/identifiability/lag-forgetting/` (v1) asked whether Paper II's lag decay of the
prerequisite drop (F1: the drop shrinks with the time between the two skills) is forgetting of A or the
edge weakening. Its revised estimand, the Wald split, reads A's state at B on its own. The edge is the drop
per unit of the arms' current A-accuracy gap. In v1's floor that estimand never confused the planted worlds, but
it failed the registered rule on power (EDGE detected in 2 of 3 seeds, rule 3 of 3), so every v1 verdict
was UNANSWERABLE. This study keeps v1's estimand, verdict strings, thresholds and programme rule, all
imported unchanged. Only the gate is replaced: a synthetic floor per corpus, sized cell by cell to that
corpus's real usable pairs, with 40 seeds per world and a stated pass rule and false-call bound.

**This is a re-registration after seeing estimates.** v1's real-data numbers had already been computed and
read when this design was written (the docstring says so first). The re-run uses the same code, pairs and
bootstrap seed, and it reproduces v1's numbers exactly (largest absolute difference 0.0 on every
statistic). **No real number here is new data.** What is new is which of those numbers an instrument
with a passing floor stands behind. Confirming any of them needs data not yet read.

**Came back.** Under the matched floors, **Eedi reads MOSTLY-FORGETTING** and **EdNet reads
NO-DECAY-TO-SPLIT**. ASSISTments is UNANSWERABLE because its floor fails. XES3G5M is UNANSWERABLE on positivity.
The **programme verdict is UNRESOLVED**, because v1's rule needs two corpora with the same directional verdict.
- **Eedi.** On 2,692 held pairs the decay on the Wald subset is D_sub = −0.038 [−0.047, −0.029]. Scaled to
  the EARLY A gap, it is D_held = +0.002 [−0.008, +0.013], so the share explained is **+1.05 [+0.81, +1.43]**.
  The drop per unit of current A gap does not move (E 0.686 → 0.694).
- **What the string names on Eedi.** The A gap narrows because the non-masters' current A accuracy rises
  (+0.064 [+0.056, +0.071]). The masters' does not fall (+0.006 [−0.000, +0.012]). That is convergence in
  A's state by catching up, not Matayoshi-type forgetting by past masters.
- **EdNet.** On 632 held pairs there is no decay on the re-attempt subset to split: D_sub −0.005
  [−0.025, +0.014].

## Design record

| step | commit | what |
| --- | --- | --- |
| design | `94ece18` | pre-registration: estimand imported from v1, matched-floor rule, pass rule, scope; before sizing, floor or any real read |
| calibration and CHANGES | `c8a9901` | case generator checked against v1's agent floor; a unit bug and A's own parent gate fixed; before the floor or any real outcome |
| sizing, ASSISTments and EdNet floors | `82e68e1` | outcome-free counts; floors; the floor made resumable after the Eedi run hit the session's 2-hour limit (implementation only) |
| results | the one after `82e68e1` | Eedi floor (re-run per world), real re-run, README, history entry |

**The matched floor.** v1's 10,000 pairs are re-drawn for each corpus. Each pair's four Wald cells (MASTERED′ and
FAILED′ in EARLY < 1 d and LATE ≥ 7 d) are counted without reading y or R. Every pair with ≥ 5 cases
in each cell is kept. Each synthetic copy has exactly those pairs and those four cell sizes, and keeps
each pair's real B item, so the B-item bootstrap resamples the real cluster structure. Cases are drawn
from v1's planted worlds, unchanged (slip 0.10, guess 0.20, learning 0.3, ability N(0, 0.5), gate 0.30,
τ = 10 d, v1's session clock), by a case-level version of v1's agent simulation:
- FORGET: held A is lost at rate 1/10 per day, and the gate is constant.
- EDGE: the gate shrinks as exp(−lag/10 d), and nothing is forgotten.
- NULL: neither.

**Pass rule (per corpus, 40 seeds per world).** All five must hold:
- FORGET → MOSTLY-FORGETTING in ≥ 32 of 40 seeds.
- EDGE → EDGE-WEAKENS in ≥ 32 of 40.
- FORGET → EDGE-WEAKENS in ≤ 2 of 40.
- EDGE → MOSTLY-FORGETTING in ≤ 2 of 40.
- NULL → either directional verdict in ≤ 4 of 40.

A corpus that fails is UNANSWERABLE. Corpora are not pooled, because no pooled floor was registered.

## Calibration of the case generator against v1's agent floor (synthetic; gates nothing)

At v1's own floor counts (3,000 agent learners, seeds 200–202), the means of the case generator are
compared with the agent's (`out/calibration.json`; first attempt in `out/calibration_v1_departs.json`):

| world | drop EARLY (agent / case) | drop LATE | A gap EARLY | A gap LATE | within 0.02 |
| --- | --- | --- | --- | --- | --- |
| FORGET | 0.058 / 0.060 | 0.017 / 0.016 | 0.247 / 0.237 | 0.051 / 0.053 | yes |
| EDGE | 0.062 / 0.054 | 0.032 / 0.035 | 0.238 / 0.216 | 0.259 / 0.259 | no (A gap EARLY −0.022) |
| NULL | 0.063 / 0.065 | 0.060 / 0.064 | 0.246 / 0.231 | 0.263 / 0.265 | yes |

The first calibration departed in every world. It exposed a units bug (the recency window compared days
with seconds) and a missing mechanism (v1's agent gates A's own first attempt on A's parent). Both were
fixed in a dated CHANGES entry before the floor ran, and the effect sizes were not touched. EDGE still
departs, by −0.022 on the EARLY A gap against a 0.02 tolerance. As registered, the floor then runs on the
generator as it stands. The departure makes EDGE harder to detect, not easier: at v1's counts the case
generator reads EDGE-WEAKENS in 2 of 10 seeds, against the agent's 2 of 3.

## Positivity and sizing (outcome-free; `out/sizing.json`)

| corpus | learners | count-readable pairs (v1 held pairs) | distinct B items | learners in their Wald cells | median cell sizes M′E / F′E / M′L / F′L |
| --- | ---: | ---: | ---: | ---: | --- |
| ASSISTments 2012–13 | 29,018 | 62 (59) | 43 | 8,377 | 72.5 / 16 / 69 / 7 |
| EdNet KT1 (6,000-learner prefix) | 6,000 | 650 (632) | 104 | 2,440 | 20 / 11 / 24 / 7 |
| Eedi (latest answers only) | 118,971 | 2,700 (2,692) | 219 | 99,580 | 81 / 25 / 94 / 20 |
| XES3G5M | — | not re-read (v1: 17 held pairs) | — | — | UNANSWERABLE on positivity |

The scarce cell everywhere is the long-lag non-master who comes back to A within a day of B (median 7 on
ASSISTments and EdNet).

## Matched floors (`out/floor.json`)

Counts of 40 seeds, with the Clopper–Pearson 95% interval of each rate:

| corpus | pairs | FORGET → MOSTLY-FORGETTING | EDGE → EDGE-WEAKENS | wrong-world calls (F→E / E→F) | NULL false calls | floor |
| --- | ---: | --- | --- | --- | --- | --- |
| ASSISTments | 62 | 2 [0.006, 0.169] | 5 [0.042, 0.268] | 0 / 0 | 2 [0.006, 0.169] | **FAILS** |
| EdNet | 650 | 40 [0.912, 1.000] | 36 [0.763, 0.972] | 0 / 0 | 0 [0.000, 0.088] | **PASSES** |
| Eedi | 2,700 | 40 [0.912, 1.000] | 40 [0.912, 1.000] | 0 / 0 | 0 [0.000, 0.088] | **PASSES** |

- **ASSISTments fails on power, not on direction.** No world returned the other world's verdict. At 62
  pairs with a median of 7 long-lag non-masters per pair, FORGET mostly reads UNRESOLVED-NO-A-GAP (16)
  or NO-DECAY-TO-SPLIT (14): the LATE A gap of about 0.05 cannot be told from zero. EDGE reads
  NO-DECAY-TO-SPLIT in 35 of 40.
- **EdNet's EDGE detection** (36 of 40, 0.90) clears the 0.80 bar. Its interval reaches down to 0.76.
- **NULL never produced a directional verdict on EdNet or Eedi.** On ASSISTments it read EDGE-WEAKENS
  twice, within the bound of 4.
- **The Eedi floor process was stopped** at the session's 2-hour limit during its NULL world. The floor
  was made resumable and its three worlds were re-run separately (implementation-only CHANGES entry).
  The re-run FORGET and EDGE tallies match the stopped run's printed tallies (40 and 40).

## Real data (`out/lag_forgetting_v2.json`)

Held pairs as in v1. Intervals are 95%, from 2,000 cluster-bootstrap draws that resample B items (the unit each
pair's outcome is measured on; bootstrap seed 0, as v1). Every value reproduces v1's
`out/lag_forgetting.json` exactly.

| corpus | held pairs | floor | drop EARLY → LATE | A gap EARLY → LATE (change [CI]) | E EARLY → LATE | D_sub [CI] | D_held [CI] | Delta [CI] | share explained [CI] | verdict |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ASSISTments | 59 | fails | 0.153 → 0.143 | 0.492 → 0.403 (−0.088 [−0.153, −0.023]) | 0.31 → 0.35 | −0.011 [−0.104, +0.087] | +0.020 [−0.083, +0.133] | +0.031 [+0.007, +0.064] | +2.86 [−8.90, +7.14] | **UNANSWERABLE** (as computed NO-DECAY-TO-SPLIT) |
| EdNet | 632 | passes | 0.045 → 0.040 | 0.052 → 0.080 (+0.028 [+0.008, +0.047]) | 0.88 → 0.50 | −0.005 [−0.025, +0.014] | −0.019 [−0.036, −0.001] | −0.014 [−0.025, −0.004] | −2.62 [−24.40, +16.52] | **NO-DECAY-TO-SPLIT** |
| Eedi | 2,692 | passes | 0.163 → 0.124 | 0.237 → 0.179 (−0.058 [−0.066, −0.050]) | 0.686 → 0.694 | −0.038 [−0.047, −0.029] | +0.002 [−0.008, +0.013] | +0.040 [+0.034, +0.047] | +1.05 [+0.81, +1.43] | **MOSTLY-FORGETTING** (D_held residual includes 0) |
| XES3G5M | 17 (v1) | — | — | — | — | — | — | — | — | **UNANSWERABLE** (positivity) |

Programme verdict (v1's rule): **UNRESOLVED**. One corpus is MOSTLY-FORGETTING, none is EDGE-WEAKENS, and the
rule needs two.

**Each arm's change, EARLY → LATE, on the held pairs (secondary, descriptive, same draws).**

| corpus | B, MASTERED′ (pM) | B, FAILED′ (pF) | current A, MASTERED′ (rM) | current A, FAILED′ (rF) |
| --- | --- | --- | --- | --- |
| ASSISTments (floor fails) | 0.617 → 0.611 (−0.006 [−0.045, +0.035]) | 0.463 → 0.468 (+0.005 [−0.085, +0.093]) | 0.794 → 0.738 (−0.056 [−0.095, −0.018]) | 0.302 → 0.335 (+0.032 [−0.034, +0.097]) |
| EdNet | 0.614 → 0.623 (+0.008 [−0.010, +0.026]) | 0.569 → 0.583 (+0.014 [−0.007, +0.035]) | 0.618 → 0.662 (+0.045 [+0.031, +0.058]) | 0.566 → 0.583 (+0.017 [−0.001, +0.035]) |
| Eedi | 0.611 → 0.610 (−0.000 [−0.007, +0.007]) | 0.448 → 0.486 (+0.038 [+0.029, +0.047]) | 0.618 → 0.624 (+0.006 [−0.000, +0.012]) | 0.381 → 0.445 (+0.064 [+0.056, +0.071]) |

- **Eedi: the decay is in the disadvantaged arm, in both A and B.** From EARLY to LATE, the non-masters'
  B accuracy rises by 0.038 and their current A accuracy by 0.064. The past masters' B and A accuracy are
  flat. The ratio of the two rises is close to E (0.038 / 0.064 = 0.60, against E of about 0.69), which
  is what the Wald split's MOSTLY-FORGETTING reading says: the drop shrinks in step with the A gap. But
  the A gap does not shrink because past masters forget A. Learners who never passed A before a long
  gap and then come back to it within a day of B answer A better than same-day non-masters do. That
  could be learning of A elsewhere during the gap, or selection of who comes back. This instrument
  cannot tell the two apart.
- **EdNet: nothing to apportion.** The registered verdict is now NO-DECAY-TO-SPLIT. On the re-attempt
  subset the drop barely moves (0.045 → 0.040), while the A gap widens (+0.028 [+0.008, +0.047]),
  because past masters' current A accuracy rises. The floor certifies detection of a planted decay of
  about −0.03 on this subset. The real interval reaches −0.025, and lag_bands' full-data EdNet decay is
  only −0.015, so a decay of the size lag_bands saw is not excluded.
- **ASSISTments is UNANSWERABLE.** Its values are as v1 computed them and are not findings. A matched
  floor at 62 pairs detects neither planted world.

## What it means for Paper II's F1

1. **F1's wording stands as v1 advised.** "The drop shrinks with lag" describes the estimand and should
   not be read as the edge weakening. With a floor that passes, the one corpus with a decay to split
   (Eedi) shows no sign of the edge weakening: E is flat, and D_held is +0.002 [−0.008, +0.013]. The decay
   tracks the narrowing of the arms' current A gap.
2. **It is not Matayoshi-type forgetting either.** On Eedi, past masters' current A accuracy does not
   fall over the lag (+0.006 [−0.000, +0.012]). The gap closes because long-lag non-masters do better on
   A. A sentence the data support: "on Eedi the lag decay tracks non-masters' current accuracy on the
   prerequisite rising, not past masters forgetting it, and the drop per unit of current prerequisite
   difference does not change with lag". It needs the qualifiers below.
3. **One corpus, a re-registration, numbers already seen.** v1's programme rule needs two corpora. EdNet
   has no decay on the re-attempt subset, and ASSISTments and XES3G5M cannot be read. The programme
   verdict is UNRESOLVED. If Paper II uses the Eedi reading, it should say it comes from one corpus,
   re-gated after the estimate was seen.
4. **What would confirm it.** Eedi has no unread sample in this format. EdNet beyond v1's
   6,000-learner prefix is unread and would raise its pair count. That would not create a decay where the
   subset shows none, but it would narrow EdNet's interval.

## Can and cannot say

- **Re-registration after seeing estimates.** The floor and pass rule were fixed before the floor ran and
  do not depend on v1's estimates. The planted worlds are v1's, and the sizes come from counts that never
  read an outcome. But the decision to re-register was taken after v1's estimates were seen, and the real
  numbers are the same numbers. A verdict here certifies the instrument, not a fresh test of the data.
- **The floor certifies power for v1's planted effects, not for the effects in the data.** The planted
  A gap is about 0.23. EdNet's real A gap is about 0.05. lag_bands' full-data decay on EdNet (−0.015) is
  smaller than the planted decay on the Wald subset (about −0.03).
- **The synthetic pairs are kinder than the real ones.** They are homogeneous gated pairs with
  independent cases, whereas real pairs are arbitrary, heterogeneous, and share learners and A items.
  The synthetic B-item bootstrap is therefore better calibrated than the real one, and a pass is
  necessary but not sufficient.
- **v1's caveats stand.** Learners differ across lag bands, and re-attempting A within a day of B is
  selected. The Wald ratio assumes that past mastery reaches B only through A's current state, plus a
  component constant across bands. Eedi keeps only each learner's latest answer per question.
- **Scope.** Only the primary split is re-registered. v1's rise-then-fall shape test would need its own
  matched floor, and its descriptive arms table needed none.
- **No coded constructs.** Every quantity is a count of logged outcomes.

## Data and outputs

- **Corpora**, read through v1's loaders (lag_bands' adapters) from `$LDA_SCRATCH_DIR`; no file is derived:
  - ASSISTments 2012–13 (`assist_rich.csv`)
  - EdNet KT1 (`ednet-kt1.zip`, prefix of 6,000 learners)
  - Eedi NeurIPS 2020 (`answers.tsv`)
- **Outputs (aggregates only; B items as integer codes):**
  - `out/sizing.json`
  - `out/calibration.json`, `out/calibration_v1_departs.json`
  - `out/floor.json`, `out/floor_parts/`
  - `out/lag_forgetting_v2.json`
  - `out/history-entry.json`

Run with `python3 lag_forgetting_v2.py sizing | calibrate | floor [--worlds W] | real`.
