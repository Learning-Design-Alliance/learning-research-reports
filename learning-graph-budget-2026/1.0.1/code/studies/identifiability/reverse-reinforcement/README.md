# Reverse reinforcement on Eedi: does meeting b raise a non-master's next answer on a? (`reverse_reinforcement.py`, 2026-10-08)

**Asked.** `lag-forgetting-v2` found that on Eedi the lag decay of the prerequisite drop tracks non-masters
of a catching up on a: their current A accuracy rises by +0.064 [+0.056, +0.071] from EARLY to LATE. Paper
II 5.1 names two readings, learning a elsewhere and selection of who returns. The second literature sweep
(strand A: A.16 Cosyn et al. 2021; A.17 Hohensee et al. 2025) adds a third: working on b exercises a. This
study tests the third reading. Among learners who had not yet passed a, does answering b questions between
two attempts at a raise the next a answer? The comparison is matched non-masters of a who, in a comparable
interval, answered questions on an unrelated skill c of b's difficulty.

**This is observational.** Nobody assigned b or c; teachers set quizzes. The verdict says how the data
behave against the confounds the synthetic floor plants. It is not a causal estimate.

**Came back: NO REVERSE EFFECT (at the 0.02 margin), and the small effect that is there points the other
way.**
- **Delta**, the ATT of meeting b instead of c on the next a answer, is **−0.012 [−0.016, −0.007]**.
- **Delta_der**, the same with another pair's b (deranged), is −0.005 [−0.009, +0.000].
- **S = Delta − Delta_der**, the part specific to the a–b link, is **−0.007 [−0.014, −0.002]**.
- Every interval sits inside ±0.02, so the registered string is NO REVERSE EFFECT. That check was placed
  first, before any data were read.
- Both Delta and S exclude zero **on the negative side**. Read naively, meeting b slightly *lowers* the
  next a answer. Their size (about 1 percentage point) is around the floor's selection-bias scale and
  well inside the margin, so no direction is claimed.
- The +0.064 catch-up in `lag-forgetting-v2` is not explained by meeting b. The whole interval for
  meeting b is below zero (upper end −0.007), so no positive effect is left to explain it. Of the three readings,
  this study tests only one: learning a elsewhere and selection of who returns are left open.

## Design record

| step | commit | what |
| --- | --- | --- |
| design | `75b04e4` | pre-registration: pair set, arms, control set, strata, estimand, derangement, verdicts, floor and pass rule; before any Eedi read |
| skeleton and positivity | `09f4ddc` | outcome-free: pair set reproduced, cases built with y sealed in the scratchpad, positivity and control-size assertions |
| floor | `d0e934f` | synthetic floor on the real skeleton, five worlds × 40 seeds; passes |
| real | the one after `d0e934f` | sealed outcomes opened; this README; history entry |

The design was revised once, before it was committed, after a smoke test of the floor code on **fake**
data. Under ABILITY-B, a noisy ability proxy left about +0.009 of selection bias. On ~10^5 learners an
interval narrower than that would turn residual selection into a finding. Two rules were added before
commit:
- a case's proxy must rest on ≥ 30 answers;
- the equivalence check (NO REVERSE EFFECT) is tested before the directional strings.

The docstring says so. No Eedi value had been read.

## What was compared

- **Pairs.** lag-forgetting-v2's 2,700 count-readable Eedi pairs, regenerated and checked against v2's
  `out/sizing.json`: the count and every B code match. These are v1's random sample of ordered subject
  pairs, kept for readability. They are **not a curated prerequisite graph**. b and a share a level-1
  strand in 30% of pairs and a level-2 group in 2.7%. "b is a's dependent" means only that (a, b) is in
  this set.
- **Case.** One non-master interval: two consecutive a answers by a learner with no correct a answer yet.
  The outcome is the second one.
- **Arms.**
  - T: ≥ 1 b answer strictly inside the interval, and no C answer.
  - K: ≥ 1 answer at C(a, b) strictly inside the interval, and no b answer.
- **Control set C(a, b).** The 5 subjects closest to b in difficulty (mean correctness), drawn from a
  different level-1 strand than a, and not paired with a either way. The mean |difficulty gap| to b is
  0.002, and the largest is 0.039.
- **Matching.** Exact strata within pair, on:
  - interval length (5 bands);
  - attempt index (3);
  - dose (number of target answers in the interval, 3);
  - other activity in the interval (2);
  - ability-proxy quintile (accuracy on everything but a, b, C).

  On top of the strata, a linear adjustment for the proxy (β = 0.75).
- **Interval.** 95% percentile interval from 1,000 draws that **resample learners** (multinomial over the
  learners in either set). Real and deranged estimates share each draw, which gives S its joint interval.
- **Derangement.** Each pair's b is replaced by another pair's b from the same b-difficulty decile. The
  replacement is not a, not in C, not in a's level-2 group, and not paired with a. Everything else is
  unchanged, and all 2,700 pairs got a b'. b' shares a's level-1 strand in 30% of pairs, as b does.
- **Latest answers only.** Eedi keeps only each learner's latest answer per question, at minute
  resolution, so "between" is in latest-answer order.

## Positivity and control size (outcome-free; `out/positivity.json`)

| set | T cases | K cases | matched T / K | usable pairs | coverage of T | learners |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| real (b) | 351,048 | 1,080,086 | 273,655 / 539,883 | 2,486 | 0.78 | 43,713 |
| deranged (b') | 353,099 | 1,097,564 | 280,861 / 549,866 | 2,385 | 0.80 | 43,696 |

- **Answerable on the fine strata.** The pre-registered fallback was not needed.
- **Proxy rule.** 26 real and 20 deranged cases were dropped for a proxy resting on fewer than 30 answers.
- **The control is the size of the treatment** (asserted):
  - Weighted to T's strata, K's mean dose is 1.06× T's (bound [0.8, 1.25]).
  - K's mean log interval length differs from T's by +0.026 (bound 0.25).
  - The deranged treatment's dose is 1.04× the real one's, and its matched-T count is 1.03×.
  - `shared.controls.check_control_scale` passes all three.

## Synthetic floor (`out/floor.json`)

The floor is the real outcome-free skeleton, with synthetic ability, proxy and outcomes:
- ability θ ~ N(0, 0.8) per learner;
- the proxy is drawn from each learner's real answer count;
- the outcome slope on ability varies by pair;
- catching up grows with interval length.

40 seeds per world, with 200 learner-resampling draws each:

| world | planted | verdicts (of 40) | mean Delta | mean S | mean unadjusted Delta |
| --- | --- | --- | ---: | ---: | ---: |
| NULL | nothing | NO REVERSE EFFECT 40 | −0.0003 | −0.0001 | −0.0003 |
| REV | +0.15 logit when b is in the interval | RAISES 40 | +0.032 | +0.034 | +0.032 |
| NEG | −0.15 logit | LOWERS 40 | −0.031 | −0.034 | −0.031 |
| ABILITY-B | meeting b selected on ability (OR 1.65/SD), no effect | NO REVERSE EFFECT 40 | +0.002 | +0.002 | +0.008 |
| ABILITY-ALL | the same selection, real and deranged | NO REVERSE EFFECT 40 | +0.003 | −0.000 | +0.009 |

- **Every pass condition holds** (≥ 32/40 detection, ≤ 2/40 false RAISES). The Clopper–Pearson
  interval on each 40/40 is [0.91, 1.00].
- **Stratification and the proxy adjustment remove most of the planted selection** (+0.008 → +0.002), but
  not all of it. About +0.002 to +0.003 remains, and single seeds' upper limits reached +0.012. That is
  the instrument's resolution against selection of this strength. It is why a sub-margin interval is not
  read as a direction.
- **What the floor does not plant.** Selection the proxy cannot see, for example a teacher who sets b to
  a class about to revisit a. Nor does it plant learners sharing a items across pairs beyond their shared
  ability. A pass is necessary, not sufficient.

## Real data (`out/reverse_reinforcement.json`)

| estimate | value [95% CI, learners resampled] |
| --- | --- |
| Delta (meeting b − meeting c, adjusted) | **−0.012 [−0.016, −0.007]** |
| Delta unadjusted (strata only) | −0.012 [−0.017, −0.007] |
| Delta_der (another pair's b − c) | −0.005 [−0.009, +0.000] |
| S = Delta − Delta_der | **−0.007 [−0.014, −0.002]** |
| next-a accuracy, T / K weighted to T's strata | 0.431 / 0.444 |
| verdict | **NO REVERSE EFFECT** |

- **The proxy adjustment barely moves Delta** (−0.0122 adjusted, −0.0124 unadjusted). On the observed
  data, ability selection into b versus c is small after the strata.
- **The real Delta is negative.** A selection artefact like the floor's would most plausibly push it the
  other way, upward. A naive reading is a slight interference: a non-master who meets b before returning
  to a does about 1 point worse than one who met an unrelated skill of the same difficulty, and about
  0.7 point of that is specific to the a–b link. It is below the registered margin and not claimed.
- **Mean intervals.** The bootstrap intervals of the T and K means are skewed relative to their points,
  because strata that lose an arm in a draw are dropped. They are descriptive.

**Secondary, descriptive (no floor of their own; they gate nothing):**

| subset | verdict string | Delta | S |
| --- | --- | --- | --- |
| first meeting of b (or of the c met) inside the interval | NO REVERSE EFFECT | −0.003 [−0.010, +0.004] | +0.005 [−0.005, +0.012] |
| interval < 1 h / 1 h–1 d / 1–7 d | UNANSWERABLE (coverage 0.49 / 0.08 / 0.44) | — | — |
| interval 7–30 d | NO REVERSE EFFECT | −0.011 [−0.016, −0.003] | −0.005 [−0.011, +0.003] |
| interval ≥ 30 d | (LOWERS A) | −0.016 [−0.025, −0.008] | −0.013 [−0.023, −0.004] |

- **Most non-master intervals that hold b or c are a week or longer.** Eedi quizzes are topic-blocked, so
  a short interval rarely holds another topic.
- **The ≥ 30 d band's directional string is not a finding.** It has no floor at that size, it was one of
  six descriptive subsets, and its effect is below the margin. It is listed because it points the same
  way as the primary.
- **The first-meeting subset is the closest to "meeting b" in the literal sense.** It shows nothing in
  either direction.

## What it means for Paper II 5.1

1. **The third reading (backward transfer from b) does not account for the catch-up on Eedi.** Meeting b
   between two attempts at a does not raise the next a answer relative to meeting a matched unrelated
   skill: the primary interval's upper end is −0.007. The rise v2 found is +0.064. If
   anything the sign is negative, and it is small.
2. **The two readings Paper II already names remain open.** Learning a elsewhere and selection of who
   returns were not tested.
3. **Qualifiers a sentence should carry.**
   - It is one corpus, observational, and in latest-answer order.
   - The pairs are a random sample of subject pairs, mostly unrelated (b shares a's level-1 strand in 30%
     of pairs), not prerequisite edges. Backward transfer is plausibly confined to genuinely related pairs.
     A test on curated edges, or on the same-strand subset, would be the follow-up. It is not registered
     here and was not run.

## Can and cannot say

- **Observational.** Exact strata and a proxy adjustment, checked against planted selection, but with no
  assignment.
- **Margin-bound.** The verdict excludes effects of ±0.02 or more on the next answer, not smaller ones.
- **Ability proxy.** It uses answers before and after the interval. If meeting b raised accuracy
  elsewhere, the adjustment would pull toward zero. The adjustment moved Delta by +0.0002, so this does
  not bear on the result.
- **Eedi limits.** Only the latest answer per question is kept, at minute resolution, and multi-leaf
  questions count on each leaf. "Strictly inside the interval" excludes questions tagged with both a and
  b.
- **No coded constructs.** Every quantity is a count or mean of logged answers.

## Data and outputs

- **Corpus.** Eedi NeurIPS 2020, tasks 1–2 (research use, no redistribution). It is read through
  `atlas.eedi_rows` via `lag_forgetting_v2.load` from `$LDA_SCRATCH_DIR` (`EEDI_ANSWERS`, `EEDI_ZIP`). The
  subject tree comes from `data.zip`. Per-case arrays and the sealed outcomes stay in the scratchpad
  (`$RR_CACHE`).
- **Outputs (aggregates only; subjects as integer codes):**
  - `out/skeleton.json`: pairs, control sets and b' as codes, plus counts;
  - `out/positivity.json`;
  - `out/floor.json` and `out/floor_parts/`;
  - `out/reverse_reinforcement.json`;
  - `out/history-entry.json`.

Run with `python3 reverse_reinforcement.py skeleton | positivity | floor [--worlds W] | assemble | real`.
