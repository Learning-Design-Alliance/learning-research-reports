# Reverse reinforcement on related pairs, Eedi (`reverse_reinforcement_related.py`, 2026-10-08)

**Asked.** The parent study (`../reverse-reinforcement/`) found NO REVERSE EFFECT on Eedi. Meeting b
between two attempts at a did not raise a non-master's next a answer: Delta −0.012 [−0.016, −0.007],
S −0.007 [−0.014, −0.002], margin 0.02. Its 2,700 pairs were a random sample of subject pairs, and b
shared a's top-level strand in only 30% of them. Backward transfer (Cosyn et al. 2021; Hohensee et al.
2025) is plausibly confined to closely related skills. The question here is whether the same contrast,
restricted to related pairs, shows it.

**This is observational.** Nobody assigned b or c. The verdicts describe how the data behave against the
confounds the synthetic floor plants. They are not causal estimates.

**Came back: no reverse effect on related pairs either. Where the data move at all, meeting a related b
goes with a slightly *lower* next a answer.**

| set | pairs | verdict | Delta (b − c) | S (b − deranged b') |
| --- | ---: | --- | --- | --- |
| L1, same level-1 strand | 799 | **NOT B-SPECIFIC** (negative) | −0.013 [−0.023, −0.006] | −0.002 [−0.012, +0.007] |
| L2, same level-2 group | 73 / 728 | **UNANSWERABLE** (control size) | — | — |
| CM, Coherence-Map curated (model-mapped) | 700 | **NO REVERSE EFFECT** | −0.007 [−0.018, −0.000] | +0.010 [−0.004, +0.018] |

All intervals are 95% percentile intervals from 1,000 draws that **resample learners**.

- **L1, NOT B-SPECIFIC, and negative.** Meeting a same-strand b instead of a matched skill from another
  strand goes with a lower next a answer. The interval excludes zero on the negative side, and its lower
  end (−0.023) passes the −0.02 margin. Meeting another related pair's b' (Delta_der −0.011
  [−0.019, −0.004]) does the same, so the dip is not specific to b. Under CHANGE 1, b' can share a's
  strand, so NOT B-SPECIFIC is also the shape a strand-wide effect would take, and here that effect is
  negative. Neither reading supports backward transfer.
- **CM, NO REVERSE EFFECT.** Both intervals sit inside ±0.02. S's point is positive (+0.010), and its
  upper end (+0.018) is just inside the margin. No direction is claimed. This set inherits the mapper's
  error (below), which biases any real effect toward zero.
- **L2 cannot be answered with this instrument.** A deranged b' of matched difficulty that is outside a's
  level-2 group sits in a non-master's a-interval far less often than a same-group b. The deranged control
  holds only 0.38× (73 pairs) and 0.36× (728 pairs) of the treatment's matched cases. The bound is 0.5×.
- **Registered summary line:** `L1: NOT B-SPECIFIC; L2: UNANSWERABLE; CM: NO REVERSE EFFECT`. No set reads
  PRACTISING B RAISES A.

## Design record

| step | commit | what |
| --- | --- | --- |
| design | `ade77d4` | pre-registration: sets, controls, derangement within set, size bounds, verdicts, floor, what was not blind |
| skeleton and positivity | `cd2e62f` | outcome-free under the registered derangement: every set failed the deranged-control size bound |
| CHANGE 1 | `378cb77` | derangement reverts to the parent's level-2 rule (before any floor or outcome) |
| positivity | `cf55e42` | under CHANGE 1: L1 and CM answerable; L2 still fails the size bound |
| floor | `a0e65bb` | L1 and CM floors pass |
| real | the commit after `a0e65bb` | sealed outcomes opened; this README; history entry |

**CHANGE 1** was made after an outcome-free result and before any floor or outcome. The registered
derangement put b' outside a's **level-1** strand. On every set that left the deranged control too small:
its matched T was 0.48× (L1), 0.21× (L2r), 0.24× (L2x) and 0.40× (CM) the treatment's, against a bound of
≥ 0.5×. Eedi quizzes are topic-blocked, so a non-master's interval rarely holds another strand. The
derangement reverted to the parent's rule: b' outside a's **level-2** group, not linked to a by the parent's
pair set or the Coherence Map, and drawn from the related set's own b-difficulty deciles. b' now shares a's
level-1 strand in 38% (L1) and 28% (CM) of pairs. The strict-rule positivity is kept in
`out/positivity.json` under `registered_strict_derangement`. Under the design as first registered, every
set was UNANSWERABLE.

## The sets

- **L1:** the parent's pairs where b shares a's level-1 strand. That is 799 of 2,700, all in the
  parent's set. Positivity passed without the registered extension, so L1x was never built.
- **L2:** b shares a's level-2 group (62 groups over 308 subjects).
  - L2r is the parent's 73 such pairs.
  - L2x is every count-readable same-group ordered pair: 728 of 1,682 candidates.
  - Both fail the control-size bound, which no extension can fix.
- **CM:** pairs (a, b) where the Achieve the Core Coherence Map links a's Common Core cluster as a
  prerequisite of b's.
  - Edges: the Coherence Map's direct cluster edges, 193 of them between distinct K-8 clusters.
    They come from the committed `studies/producers/pipeline/data/coherence-map.json`, registry id
    `coherence-map`. Its edge direction was asserted: all 454 graded edges run forward in grade.
  - Pairs: every count-readable ordered Eedi subject pair whose mapped clusters are so linked, 700 of
    1,429 candidates. Only 84 of them are in the parent's set.
  - Overlap with the strand sets: 62% of CM pairs share a's level-1 strand, so CM and L1 overlap. They
    are two operationalisations of "related", not independent tests.
- **Coder of the curated set (model-coded construct).** Each Eedi subject's cluster comes from
  `core-vs-culture/out/unit-map.json`, coded by **openai/gpt-6-sol from the subject's name alone**.
  101 of 308 subjects are mapped NONE. Against a blind human coder (human:david-porcaro), agreement is
  κ = 0.606 [0.493, 0.709] over 87 items from four corpora. On the Eedi items alone it is 0.668 (n = 24),
  with raw agreement 0.71. The edges themselves are authored by Achieve the Core. The curation is
  model-mapped and inherits the map's error: roughly three in ten subjects may sit in the wrong cluster.
  That adds unrelated pairs to CM and biases any real effect toward zero.
- **Count-readable** is the parent's population filter: v2's `wald_counts` ≥ 5 in each cell. It reads
  timing and a's prior mastery, not this study's outcome.

## Controls and their size (outcome-free; `out/positivity.json`)

- **Control set C(a, b):** five subjects. Each is closest to b in difficulty (mean gap 0.003), in a
  different level-1 strand from a, and linked to a neither by the parent's pair set nor by the Coherence
  Map.
- **Derangement:** within the related set (CHANGE 1 above).
- **Machinery:** strata, proxy adjustment, estimator and verdict function are the parent's, imported
  unchanged.
- **Case builder:** a copy of the parent's loop. On every parent pair whose control set is unchanged, it
  reproduces the parent's per-pair T counts exactly: 706 pairs for L1, 65 for CM, 0 mismatches.

| set | matched T / K | usable pairs | coverage | learners | K dose / T | K log-length − T | b' dose / b | b' matched T / b |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| L1 | 118,858 / 167,380 | 740 | 0.74 | 34,832 | 1.05 | +0.05 | 1.08 | 0.70 |
| L2r | 16,547 / 13,970 | 69 | 0.55 | 15,129 | 1.04 | +0.14 | 1.13 | **0.38** |
| L2x | 180,011 / 160,492 | 660 | 0.62 | 42,965 | 1.03 | +0.09 | 1.15 | **0.36** |
| CM | 133,172 / 167,470 | 664 | 0.74 | 35,949 | 1.03 | +0.06 | 1.04 | 0.57 |

Bounds: K dose / T within [0.8, 1.25]; log-length difference ≤ 0.25; b' dose within [0.5, 2]; b' matched
T ≥ 0.5. `shared.controls.check_control_scale` was applied to each set as well.

## Synthetic floor (`out/floor.json`)

The floor runs on each set's real outcome-free skeleton. Worlds are the parent's, from `rr.synth_world`.
Each world has 40 seeds with 200 learner-resampling draws per seed.

| world | L1 verdicts | L1 mean Delta | CM verdicts | CM mean Delta |
| --- | --- | ---: | --- | ---: |
| NULL | NO REVERSE EFFECT 38, UNRESOLVED 2 | −0.000 | NO REVERSE EFFECT 39, UNRESOLVED 1 | +0.000 |
| REV (+0.15 logit) | RAISES 40 | +0.032 | RAISES 40 | +0.032 |
| NEG (−0.15 logit) | LOWERS 40 | −0.031 | LOWERS 40 | −0.031 |
| ABILITY-B | NO REVERSE EFFECT 38, NOT B-SPECIFIC 1, RAISES 1 | +0.002 (unadj. +0.007) | NO REVERSE EFFECT 39, NOT B-SPECIFIC 1 | +0.003 (unadj. +0.009) |
| ABILITY-ALL | NO REVERSE EFFECT 38, UNRESOLVED 2 | +0.002 | NO REVERSE EFFECT 38, RAISES 1, UNRESOLVED 1 | +0.003 |

- **Both floors pass every rule.**
  - Planted effects of about ±0.032 are found in 40 of 40 seeds, in the right direction.
  - NULL gives no directional string.
  - False RAISES under ability selection is 1 of 40, against an allowed 2.
- **Interval width.** The mean Delta interval is about 0.013–0.014 wide on these subsets. The parent's
  was 0.008.
- **What the floor does not plant.** The floor does not plant selection the proxy cannot see. On related
  pairs that is more plausible than on random ones: b and a are taught together, so a class that meets b
  may be one about to revisit a. A pass is necessary, not sufficient.

## Real data (`out/related.json`)

| | L1 | CM |
| --- | --- | --- |
| Delta, adjusted | −0.013 [−0.023, −0.006] | −0.007 [−0.018, −0.000] |
| Delta, strata only | −0.013 [−0.022, −0.005] | −0.006 [−0.017, +0.000] |
| Delta_der (deranged b') | −0.011 [−0.019, −0.004] | −0.016 [−0.023, −0.007] |
| S = Delta − Delta_der | −0.002 [−0.012, +0.007] | +0.010 [−0.004, +0.018] |
| next-a accuracy, T / K weighted to T's strata | 0.435 / 0.448 | 0.446 / 0.452 |
| proxy slope β | 0.77 | 0.67 |
| verdict | **NOT B-SPECIFIC** | **NO REVERSE EFFECT** |

**Secondary, descriptive (no floor of its own; it gates nothing):** the first-meeting subset.

| set | verdict string | Delta | S |
| --- | --- | --- | --- |
| L1 | UNRESOLVED | −0.009 [−0.022, +0.002] | +0.003 [−0.014, +0.016] |
| CM | NO REVERSE EFFECT | +0.001 [−0.012, +0.013] | +0.001 [−0.016, +0.015] |

- **Direction.**
  - Every primary Delta point is negative, as in the parent (−0.012).
  - L1's Delta (−0.013) is the same size as the parent's whole-set Delta. CM's (−0.007) is about half
    of it.
  - Restricting to related pairs did not turn the sign. Neither set's Delta interval reaches zero
    (upper ends −0.006 and −0.000).
- **CM's positive S comes from its deranged arm.** S is +0.010 only because Delta_der is more negative
  (−0.016) than Delta. Its interval includes zero. It is not a positive effect of meeting b.
- **The proxy adjustment barely moves either estimate** (L1: −0.0131 adjusted, −0.0125 strata only).
  That matches the parent.

## What it means for Paper II 5.1

1. **Backward transfer from a related b does not show on Eedi either.** On same-strand pairs and on
   Coherence-Map-linked pairs, meeting b between two a attempts does not raise the next a answer relative
   to a matched unrelated skill. The parent's qualifier, that the sample was mostly unrelated pairs, is
   now answered for strand-level and progression-level relatedness. It is not answered for the finest
   level (level-2 group), which this instrument cannot reach.
2. **If anything, related b goes with slightly lower next-a accuracy** (L1 −0.013). The derangement shows
   it is not specific to b. It is about a fifth of v2's +0.064 catch-up in magnitude and opposite in
   sign. No interference is claimed: there is no floor for selection the proxy cannot see.
3. **Qualifiers.**
   - One corpus, observational, latest answers only.
   - CM is model-mapped (κ 0.606).
   - L1's S cannot isolate the strand relation under CHANGE 1.
   - The design changed once, after an outcome-free size failure.

## What was not blind

- **The parent's result was known** when this was designed: its overall NO REVERSE EFFECT and negative
  sign, and its secondary subsets (first meeting, interval bands).
- **The parent's committed `out/` held no subset estimates.** It was searched for same-strand or
  curated-subset estimates and holds none. The only strand-related values in it are structural shares in
  `out/skeleton.json` (b_same_level1_as_a 0.30, b_same_level2_as_a 0.027). Its estimates cover only the
  whole set, first meeting and interval bands, and `floor_parts` is synthetic.
- **L1 was weakly constrained by the parent's aggregate.** L1's pairs are 799 of the parent's 2,700, so
  its cases are a subset of a pool whose aggregate (−0.012) was known. That constrains L1 weakly. It does
  not reveal L1's value. No per-case sealed file of the parent was opened for any subset.
- **Structural pool counts were computed before the design was written:** 799, 73, 1,682, 1,429, 84, 829
  and 62 groups. No case, case count or outcome of these sets had been computed.
- **CHANGE 1 followed an outcome-free result.** It came after outcome-free case counts of these sets were
  seen, and before any floor or outcome.
- **The maintainer's expected direction was known:** backward transfer on related pairs.

## Data and outputs

- **Corpus.** Eedi NeurIPS 2020, tasks 1–2 (research use, no redistribution). It is read through
  `lag_forgetting_v2.load("eedi")` from `$LDA_SCRATCH_DIR` (`EEDI_ANSWERS`, `EEDI_ZIP`). Per-case arrays
  and sealed outcomes stay in `$RRR_CACHE` (scratchpad).
- **Coherence Map.** `studies/producers/pipeline/data/coherence-map.json` (registry `coherence-map`).
- **Unit map.** `studies/identifiability/core-vs-culture/out/unit-map.json` (openai/gpt-6-sol).
- **Outputs (aggregates only; subjects as integer codes):**
  - `out/skeleton.json`: pools, per-set pairs, controls and b' as codes, plus counts; the
    strict-derangement sets are kept too;
  - `out/positivity.json`;
  - `out/floor.json` and `out/floor_parts/`;
  - `out/related.json`;
  - `out/history-entry.json`.

Run with `python3 reverse_reinforcement_related.py skeleton | positivity | floor --set L1|CM [--worlds W] |
assemble --set S | real`.
