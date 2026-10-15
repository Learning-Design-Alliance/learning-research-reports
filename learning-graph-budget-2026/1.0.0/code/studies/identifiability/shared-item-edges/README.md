# Shared-item edges: why are co-tagged edges decided so much more often?

**Asked.** `studies/identifiability/qmatrix-positivity/` noted, as an exploratory observation that was
not pre-registered, that candidate edges A -> B whose two skills share at least one item are decided
by the positivity atlas far more often than other edges: 275 of 427 (64%) against 25.4% on Eedi, and
11 of 39 (28%) against 4.0% on XES3G5M. The maintainer asked whether this gap is **mechanical** or
**substantive**. Under the mechanical reading, a response to a shared item is one event on A and one
on B at the same instant, so it adds co-attempters, moves B's first touch, creates ties, and reads B's
outcome on an item that also needs A (the composition effect; Pardos et al. 2008, literature entry
2.13). Under the substantive reading, co-tagged skills are taught together, so learners really do meet
B without A at a different rate.

The design, controls, synthetic floor and signed verdict strings were committed before any real
number was read (`shared_item_edges.py` docstring, commit `26439c6`). Its CHANGES entry records four
iterations of the synthetic fixture and the caliper change (0.25 to 0.5 SD, with replacement). All
of them were made before that commit and before any real data was read.

**Came back.** The pre-registered verdicts are **MECHANICAL on Eedi** and **MIXED on XES3G5M**. On
XES3G5M a remainder of 2.4 points survives and has the same sign. On both corpora, matching on coverage
and difficulty closes nearly all of the gap: 99.0% on Eedi and 87.9% on XES3G5M. The shared responses
themselves account for very little of it. Excluding them moves the gap by 0.9 points on Eedi and by 2.8
points on XES3G5M. Co-tagged edges are decided more often because co-tagged skills are **co-practised**:
many more learners attempt both, mostly through items that are not shared. Once coverage and
difficulty are matched, a co-tagged edge is decided about as often as a non-shared edge into the same
dependant.

## Floor and reproduction

- **The synthetic floor passed** (`out/floor.json`, commit `2062f2e`).
  - Exactness: the per-edge engine equals qmatrix-positivity's validated atlas replica on all 39,600
    ordered pairs of the four discrimination worlds and on a small world, with 0 mismatches, and
    every state branch occurs. The exclusion rule equals the atlas's own `positivity` and
    `reachability` functions run on a row stream rebuilt without the shared responses, on 40 edges
    with 0 mismatches. The pool covariates computed by matrix product equal the per-edge ones on
    every pair.
  - Discrimination: W-MECH has conjunctive shared items and no positivity difference. Both seeds
    returned MECHANICAL: g0 = +55.8 and +57.5 points, gEM = 0.0 [−10.5, +10.8] and +3.6 [−5.6, +13.8].
  - W-SUBST has shared items that measure only general ability, and shared pairs taught together, with
    a failed skill remediated after its partner. Both seeds returned MIXED, which is a pass under the
    pre-registered rule: gEM = +11.8 [+3.4, +22.0] and +18.7 [+9.7, +27.2]. The lean check passed:
    W-MECH's raw lean is LEANS SUPPORTED.
- In the floor worlds, **exclusion** is what closes W-MECH's gap. There gE is about 0, while gM
  stays at +16.2 and +12.2 points. So the decomposition can tell "the shared response did it" apart
  from "coverage did it". No world planted a coverage-only gap, and that branch of the decomposition
  is read here, not floor-tested.
- **The atlas reproduced exactly** on both corpora. Recomputed on the atlas's 20,000-edge sample,
  learners, units, edges, readable, detect_20pt, supported, contradicted (before and after the gate)
  and unknown all equal `overlap/out/atlas.json`. XES3G5M: 736 supported, 69 contradicted, 19,195
  unknown. Eedi: 4,935, 138 and 14,927. The atlas-sample co-tagged subset also reproduces the
  observation: 11 of 39 decided on XES3G5M and 275 of 427 on Eedi.
- **ASSISTments 2012-13 is excluded.** Every problem carries exactly one skill, so the Q-matrix is a
  partition and no shared-item edge exists.

## Results

Treated: every co-tagged ordered pair in the census (1,528 on XES3G5M, 1,986 on Eedi). Baseline: the
atlas sample's non-shared edges (19,961 and 19,573). Controls: non-shared edges into the same dependant
B, matched 1:1 with replacement within 0.5 SD on log co-attempters, log attempts per co-attempter, and
first-touch correctness on B and on A. All gaps are differences in decided share, in percentage
points, with 95% percentile intervals from a 1,000-draw cluster bootstrap over dependants B. The
interval resamples dependants, not learners or items.

| | XES3G5M | Eedi |
|---|---:|---:|
| decided, co-tagged raw / non-shared baseline | 24.2% / 4.0% | 63.2% / 24.5% |
| **g0** raw gap | **+20.2** [+16.7, +23.6] | **+38.7** [+34.8, +42.0] |
| gE, shared responses excluded (EXCL), unmatched | +17.4 [+13.9, +20.9] | +37.8 [+33.9, +41.3] |
| gM, matched on raw coverage and difficulty | −1.0 [−4.1, +1.9] | −0.1 [−2.0, +1.5] |
| **gEM** EXCL and matched (primary) | **+2.4** [+0.2, +4.7] | **+0.4** [−1.2, +1.9] |
| gES, EXCL against matched controls with sized removal | +2.3 [−0.3, +4.8] | −0.6 [−2.5, +1.1] |
| share of g0 explained, 1 − gEM/g0 | 87.9% [77.6%, 99.0%] | 99.0% [95.1%, 103.1%] |
| treated edges matched (EM) | 1,474 of 1,528 (3.5% unmatched) | 1,901 of 1,986 (4.3% unmatched) |
| **verdict** | **MIXED** | **MECHANICAL** |
| verdict read from gES instead | MECHANICAL | MECHANICAL |

Balance after matching: every standardized mean difference is at most 0.044 on XES3G5M and at most
0.061 on Eedi. Before matching, co-tagged edges were 0.84 SD (XES3G5M) and 0.92 SD (Eedi) above the
pool in log co-attempters.

**The two estimators disagree on XES3G5M**, and the README is required to say so. gEM's interval
excludes 0 by 0.2 points, so the primary verdict is MIXED. gES's interval includes 0, so read from gES
the verdict would be MECHANICAL. The surviving remainder on XES3G5M is +2.4 points, small and only
just distinguishable from 0. Its sign agrees with the observation.

**Where the mechanical part sits.** These numbers are descriptive. The median share of B's events
removed by EXCL is 5.5% on XES3G5M and 0.7% on Eedi. On XES3G5M, 22.6% of co-attempters co-attempt
only through shared items, against 5.9% on Eedi. In the raw data, 10.5% (XES3G5M) and 2.7% (Eedi) of
B-reachers have their first B event on a shared item. Ties at B's first touch fall from 10.2% to 4.0%
of B-reachers on XES3G5M, and from 3.5% to 2.0% on Eedi. The rest of Eedi's ties come from its
minute-resolution, last-answer timestamps.

Attributing each shared response to one skill moves little. With TO_A the gap is +18.7 on XES3G5M and
+38.4 on Eedi. With TO_B it is +20.0 and +38.7, which equals g0 on Eedi, as the derivation in the
docstring predicts. Against matched controls with a removal sized to EXCL, the exclusion effect beyond
data loss is −3.3 points [−5.1, −1.6] on XES3G5M and +0.5 [−0.3, +1.3] on Eedi. The sized removals
came out larger than the treatment rather than smaller, because whole items are coarse: the median
control-to-treatment ratio is 1.07 on XES3G5M and 1.12 on Eedi, and the upper quartile is 2.5 on both.
They pass `shared/controls.check_control_scale` (1.73x and 1.55x at the median).

**Lean among decided edges** (signed: the supported share among decided co-tagged edges minus that
among controls).

| | XES3G5M | Eedi |
|---|---:|---:|
| raw, co-tagged vs baseline | +2.8 [−0.9, +6.4], NO DETECTED LEAN | +1.7 [+1.0, +2.5], LEANS SUPPORTED |
| EM, EXCL vs matched controls | −1.4 [−5.3, +2.2], NO DETECTED LEAN | +1.3 [+0.04, +2.8], LEANS SUPPORTED |

Both arms are almost all supported: 92–99% of decided edges. On Eedi, decided co-tagged edges lean
slightly toward supported, and the lean survives exclusion and matching, so it is not the composition
effect of the shared item. Almost all supported co-tagged edges survive EXCL: 303 of 349 on XES3G5M
and 1,216 of 1,243 on Eedi.

**Positivity diagnostic.** This is the failed-cell share of B-reachers, co-tagged EXCL against EM
controls. It is +0.25 points [+0.03, +0.47] on XES3G5M (2.37% vs 2.11%) and +0.35 [+0.22, +0.50] on
Eedi (3.32% vs 2.97%). Learners meet B having failed A slightly **more** often on co-tagged pairs. The
difference is real in sign, but on Eedi it is too small to move the decided share.

## What it means for Paper II F1

The pre-registered reading of MECHANICAL (Eedi) and MIXED (XES3G5M) applies, with one correction to
what "mechanical" turned out to mean.

- **The shared response is not what decides these edges.** Supported co-tagged edges are not
  supported by their shared item. Excluding it leaves 97.8% (Eedi) and 86.8% (XES3G5M) of them
  supported. F1's supported count needs no composition-effect footnote, and the concern
  qmatrix-positivity raised (that 270 supported Eedi edges might be carried by the shared item)
  does not hold.
- **The gap is coverage.** Co-tagged skills are attempted by far more of the same learners, and
  most of that co-attempting comes from items that are not shared. The brief counted coverage as
  mechanical, so the verdict is MECHANICAL on Eedi. But coverage of this kind is also the
  "taught together" pattern, acting through how many learners reach both skills rather than through
  which cell they fall into. F1 should say that co-tagged edges are decided more often because more
  learners attempt both skills, and that at equal coverage and difficulty they are decided at the
  same rate on Eedi and 2.4 points more often on XES3G5M.
- The co-tagged excess is not evidence that co-tagged edges are better identified or more often real.

## What this cannot say

Matching uses four observed covariates. Anything else that differs between co-tagged pairs and the
rest, such as content area or curriculum position, is part of XES3G5M's remainder. Matching on
coverage also absorbs any real "taught together" effect that works only through coverage. That is
the brief's choice, and it is the reason the verdict label MECHANICAL should not be read as
"artefact of the item map".

The floor did not plant a coverage-only world. The Q-matrices are the platforms' own tagging (TAL's
KC routes, Eedi's subject tree) and are not validated against an independent coder. Eedi's order is
last-answer order at minute resolution. The atlas's states are taken as defined. This study says
nothing about direction, conjunction between prerequisites, or lag.

## Files

- `shared_item_edges.py`: the pre-registration (docstring) and the code. Run `--floor`, then
  `--corpus xes3g5m` and `--corpus eedi`, then `--summary`.
- `out/floor.json`, `out/xes3g5m.json`, `out/eedi.json` (every gap with its interval, states by stage,
  matching balance, sized-control check, lean, mechanism descriptives, the 4 x 4 cell transition, and
  the reproduction check), `out/summary.json`, `out/history-entry.json`.
- Reads two licensed corpora, XES3G5M and Eedi NeurIPS 2020, through `shared.paths.data_path`.
  Only aggregates are written, and nothing is derived to disk.

## Follow-up: a coverage-only world (`--coverage-floor`, 2026-10-09)

**Asked** (maintainer, 2026-10-09). Paper II reads the gap as coverage: excluding the shared responses
leaves it, and matching on coverage and difficulty closes it. No floor world planted coverage alone, so
that reading was untested. The pass rule was written into the script's docstring and committed
(de01386) before the world ran, after the real decomposition above had been seen.

**Answer: COVERAGE FLOOR FAILED. Attributing the gap to coverage stays a reading of the decomposition.**

| world (seed) | g0 | gE (exclusion) | gM (matching) | primary verdict | shows the real shape |
| --- | --- | --- | --- | --- | --- |
| W-COVER (1) | +0.221 [+0.183, +0.260] | +0.021 [−0.043, +0.082] | +0.005 [−0.013, +0.025] | MECHANICAL | no: exclusion closes it |
| W-COVER (2) | +0.230 [+0.189, +0.273] | +0.035 [−0.031, +0.099] | +0.017 [−0.012, +0.053] | UNDERPOWERED | no: exclusion closes it |

In the coverage-only world, matching closes the gap as expected, but excluding the shared responses
closes it too, so the world does not reproduce the real pattern (exclusion leaves the gap: +37.8 of
+38.7 points on Eedi, +17.4 of +20.2 on XES3G5M). Neither W-MECH nor W-SUBST shows the real shape
either. The synthetic world decides about 75% of non-shared pairs, against 4% to 25% in the real
corpora, which is a likely reason the worlds differ; that is not tested. Full record:
`out/coverage-floor.json`.
