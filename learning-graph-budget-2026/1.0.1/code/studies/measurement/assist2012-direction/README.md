# A4 positive control on ASSISTments 2012–13

**Asked.** Run the A4 positive control on a corpus that can actually answer it: is a structure known
independently of the data — CCSS grade order — recovered in real human responses, *direction
included*?

**Answer. NOT RECOVERED, and this time that is a real answer.** The bar is resolvable here (0.020
against an instrument noise of 0.0033), so unlike `studies/measurement/edmcup-direction/` this is an adjudicated null
rather than a shrug. A directional signal over all mapped skills exists, +0.0117 [+0.0054, +0.0181],
**but it is smaller than the pre-registered bar, and it comes only through the skills matched to
Common Core by approximate names**: over exact names alone the excess is −0.0022 [−0.0099, +0.0094].

> **Re-run 2026-10-14 on the extract the release hashes.** The release's reproduction found the published
> output had been computed from the ASSISTments extract as it was before 2026-09-24 (that day's change drops
> 88,189 scaffolding and 773 open-response rows and scores 211 partial-credit rows). On the hashed extract:
> 27,181 learners, 4,176 both-order pairs; S1 +0.0118 → +0.0117 [+0.0054, +0.0181] over 1,426 pairs; S1E
> −0.0015 → −0.0022 over 472. **No verdict moved.** Every number below is the re-run's. The earlier re-issue
> (2026-09-24) had moved S1 from +0.0144 to +0.0118 and fed `studies/outcomes/prospective-verdict/PREREGISTRATION.md`;
> the noise constant is now 0.134 and the pairs needed to resolve the bar 45.

## Why this corpus

`studies/measurement/edmcup-direction/` came back UNDERPOWERED AT THE BAR. The contrast lives entirely on pairs seen in
BOTH orders; EDM Cup yields 128, and its 0.02 bar fell *below* the instrument's own 0.025–0.031
scatter. That study priced the ask at ~504 both-order pairs and named the mechanism that recruits
them: **learners on different curricular sequences, not more learners on the same one.**

ASSISTments 2012–13 is that corpus, and it was already on disk. Skill builders are **teacher-assigned**,
so classes meet skills in different orders and the both-order cell is abundant rather than scarce.

| | EDM Cup 2023 | **ASSISTments 2012–13** |
|---|---:|---:|
| both-order pairs | 1,250 | **4,176** |
| surviving direction + positivity | 5 | **1,426** |
| instrument noise (2 sd) | 0.025–0.031 | **0.0033** |
| bar resolvable? | no | **yes** |

Both-order pairs here are among the 135 CCSS-mapped skills (`both_order_pairs` in `out/direction.json`). The 14,485 in the script docstring is the count over all 245 named skills, made before the map restricted the set.

## What unlocked it: EDM Cup as a curriculum dictionary

The missing piece was never learners, it was a curriculum map — and EDM Cup supplied one.
`problem_details.csv` publishes **541 CCSS codes each with a description**, which makes it in effect
a published ASSISTments skill-name → CCSS dictionary. Matched against the 245 named 2012 skills:

- **135 mapped** (67 exact name matches, 68 strong at Jaccard ≥ 0.5)
- **132 carry a parseable grade**, spanning grades 1–8
  (`[(1,1),(2,3),(3,6),(4,15),(5,20),(6,42),(7,23),(8,22)]`)
- 27,181 learners touching a mapped skill

The derived map is committed at `out/skill_ccss_map.json`.

**Name matching is not construct identity**, so the exact-name subset is run as a structure of its
own (**S1E**). If the fuzzy tail is driving anything, the two must disagree — and they do. That is
the single most informative thing in this study.

## Design

The statistic, controls and verdict rule live in `shared/direction_contrast.py` (read that docstring
first). In brief: a single drop is positive for nearly any ordered pair because passers are abler, so
the readout is the within-pair contrast on pairs seen both ways,

```
delta(A,B) = drop(A→B) − drop(B→A),   A before B in the published structure
```

scored as **excess over a family-matched deranged arm**, with outcomes residualised against each
learner's own mean over their other skills.

Two corpus-specific choices, both named rather than assumed:

- **Passing A is measured only on A-attempts that precede the first B-attempt.** The claim is
  "passed A *before* reaching B", and on this corpus a learner's A attempts often straddle B, so
  letting later practice count would leak the future into the conditioning variable.
- **`assignment_id` is the class proxy.** `assist_slim` carries no `class_id`; an ASSISTments
  assignment is given to a class, so learners are clustered by the assignment they were first seen
  on. 6,630 cohorts, 84.6% of learners in cohorts of ≥5, 6.8% singletons. **A proxy, not a class.**

Pre-registered before the run: bar `excess > 0.02`; 95% cluster bootstrap over cohort must exclude 0;
≥10 learners in each of a pair's four cells; <20 surviving pairs → UNANSWERABLE.

## Result

| | **S1** all 135 mapped | **S1E** exact names only |
|---|---:|---:|
| pairs surviving | 1,426 | 472 |
| ordered observations | 1,163,968 | 320,269 |
| planted +0.150 recovered | +0.1502 | +0.1495 |
| unplanted arm | −0.0001 ± 0.0016 | −0.0011 ± 0.0034 |
| **instrument noise (2 sd)** | **0.0033** | **0.0069** |
| delta, residualised | +0.0122 | −0.0011 |
| deranged | +0.0005 | +0.0011 |
| **excess** | **+0.0117** | **−0.0022** |
| direction labels shuffled | −0.0003 ± 0.0029 | +0.0002 ± 0.0048 |
| 95% cluster CI | [+0.0054, +0.0181] | [−0.0099, +0.0094] |
| **verdict** | **NOT RECOVERED** | **NOT RECOVERED** |

The split between the two structures holds at every cell floor tried:

| cells ≥ | 5 | 10 | 20 | 30 |
|---|---:|---:|---:|---:|
| S1 pairs | 1,754 | 1,426 | 1,035 | 809 |
| **S1 excess** | **+0.0133** | **+0.0117** | **+0.0126** | **+0.0137** |
| S1 noise | 0.0041 | 0.0033 | 0.0033 | 0.0034 |
| S1E pairs | 559 | 472 | 339 | 256 |
| **S1E excess** | **+0.0007** | **−0.0022** | **−0.0032** | **−0.0049** |
| S1E noise | 0.0057 | 0.0069 | 0.0080 | 0.0069 |

S1 is positive at every floor. S1E stays within its own noise of zero at every floor (+0.0007 at the
loosest, negative at the other three).

## Power is closed, and by a wide margin

Instrument noise falls as **0.134 / √pairs** here, fitted on all eight sweep points:

| | pairs |
|---|---:|
| in hand, best setting | **1,754** |
| to resolve the bar | 45 |
| to resolve half the bar | 180 |

Whatever is now blocking A4, it is not sample size.

## What the two numbers mean together

**1. Pre-registration earned its keep.** S1's +0.0117 is several times the instrument's noise, with an
interval that excludes zero. It is also **below the 0.020 bar written down before the run**, so it does
not count, and it is the number that would have been reported as a success had the threshold been chosen
afterwards.

**2. The signal lies in the approximate matches.** S1's pairs are a superset of S1E's. The exact-name
subset returns −0.0022, not shown to differ from zero; the union returns +0.0117. So the pairs reached
through approximate matches carry more than +0.0117 on their own. This design cannot tell whether that
reflects mislabeled skills or a grade order the exact-name subset is too small to show; the map was made
by a name-matching rule no person checked.

## The distance profile — first read on the distal-prerequisite hazard

`docs/specs/SPAN.md` argues that a real prerequisite can sit further back than the corpus observes, in which case
near and far pairs should not behave alike. The strata are the first empirical test, and **they do not
confirm it**:

| excess by grade gap | 1 | 2 | 3 | 4+ |
|---|---:|---:|---:|---:|
| **S1** | +0.0085 (581) | +0.0160 (470) | +0.0293 (216) | +0.0266 (159) |
| **S1E** | −0.0168 (227) | +0.0322 (153) | +0.0186 (62) | −0.0498 (30) |

S1 rises with distance up to three grades. S1E does not: it is non-monotonic and negative at gap 1 and
at gap 4+. Recorded as **not evidence either way**; the strata have no intervals.

## Controls

- **Floor.** A +0.150 gate planted on the forward direction only, recovered at **+0.1502**, with the
  unplanted arm centred on zero (−0.0001 ± 0.0016), averaged over 25 draws.
- **Deranged arm.** Pass/fail labels deranged within each (pair, direction) stratum — a derangement,
  not a permutation — averaged over 25 derangements (spread ±0.0018 on S1).
- **Direction-label null.** −0.0003 ± 0.0029 on S1: randomising which end is "first" is
  indistinguishable from the published labelling once the excess is taken.
- **Clustering.** Whole cohorts resampled, each drawn copy getting its own learner namespace.

## What this does and does not move

A4 **stays unmet**. What changes is the quality of the evidence: for the first time the criterion has
been tested on a corpus where the instrument could have resolved the bar, so "not recovered" now
carries information. The remaining obstacle is no longer power — it is the **reference**. This corpus
has no published instructional sequence for its own skill vocabulary, only CCSS grade borrowed
through a name match, and the name match is where the one positive signal lives.

The next A4 attempt should use a corpus whose structure is known **by construction** rather than by
string matching — the procedural-corpus route, or the Prolific artificial-domain study, both of which
supply the reverse direction without depending on a curriculum vocabulary being alignable across
releases.

## Files

- `direction.py` — the study
- `out/direction.json` (run logs are not committed)
- `out/skill_ccss_map.json` — the derived 135-skill ASSISTments → CCSS map

Reproduce with `ASSIST_DIR=<scratchpad> EDMCUP_DIR=<scratchpad>/edmcup python3 direction.py`.

ASSISTments is analysis-only, no redistribution: raw CSVs stay in the scratchpad, only the aggregates
and the derived map are committed.

**Reversed-arrow control (2026-09-24):** the within-pair delta is antisymmetric, so the control reads each structure's sign: S1 (all mapped) +0.0122 vs −0.0122 reversed (CLAIMED), S1E (exact names) −0.0011 vs +0.0011 (REVERSED, inside the noise): on the exact-name subset the CCSS grade order does not beat its reverse (re-run values, 2026-10-14).
