# A4 positive control on EDM Cup 2023

**Asked.** Build the A4 positive control: does the assay recover a structure known
independently of the data *from real human responses, direction included*?

**Answer.** Not on this corpus. The structure is real, the timeline is real, the instrument
demonstrably works — and the measurement still lands inside its own noise. A4 is **not met**.
The useful output is a price: ~500 both-order skill pairs would settle it, against 128 in hand.

## What the corpus supplies

EDM Cup 2023 ([osf.io/7stjh](https://osf.io/7stjh)), an ASSISTments release. Analysis only, no
redistribution — raw CSVs stayed in the scratchpad, only the aggregates here are committed.

| | |
|---|---|
| learners with graded, skill-tagged responses | 34,580 |
| classes | 2,705 |
| (learner, skill, time) cells | 192,971 |
| problems carrying a CCSS code | 131,918 of 132,738 (99.4%), 541 distinct standards |
| ordered skill pairs | 9,428 |
| **pairs seen in BOTH orders** | **1,250** |

That last row is the whole study. Everything else is abundant.

## The sentinel that nearly killed it

`assignment_start_time` on a unit-test assignment is not a time. It is the literal string
`REMOVED_FOR_EVALUATION` — the competition redacted the clock on exactly the 53,615 rows whose
scores were the prediction target. Parsed naively that sentinel is one constant value, so every
learner appears to hold exactly one timestamp, no skill pair is ever ordered, and the corpus
reads as structurally incapable of any directional test. The first probe here reported exactly
that, and it was wrong.

It is a redaction marker, not a property of the corpus. All **9,266,061** non-test assignments
keep real epoch times, and **none** of the 638,528 in-unit practice assignments is redacted. So
the timeline is rebuilt from the practice side: `assignment_relationships` links each unit test
to the practice beneath it, already per learner, and a test is anchored at the *last* practice
start time below it. All 53,615 tests anchor; none is lost. The anchor uses practice timing
only — never the CCSS codes or the curriculum order the study is trying to recover.

No `action_logs.csv` download was needed.

## Design

The repo's drop is positive for essentially any ordered pair, because learners who pass A are
abler; the house background is about +0.10. A single drop therefore cannot show direction. The
readout is the **within-pair directional contrast**, computed only on pairs seen both ways:

```
delta(A,B) = drop(A->B) - drop(B->A),   A before B in the published document
```

The same two skills carry both terms, so pair difficulty cancels and general ability cancels to
the extent it acts equally in both orders. Outcomes are additionally residualised against each
learner's own mean over their other cells, excluding both A and B; raw figures are reported
beside the residualised ones so the residualisation can be audited.

Three independently-published structures, none induced from the responses:

| | structure | grain |
|---|---|---|
| **S1** | CCSS grade, parsed from the code (`5.NBT.A.4` before `6.RP.A.2`) | across grades |
| **S2** | publisher's scope and sequence — module 2 before module 3 | within a course |
| **S3** | the same document read finer — module 1 lesson 4 before lesson 5 | within a module |

S3 was added after S1 and S2 came back underpowered. It is a finer reading of the same published
document, not a different hypothesis; the bar and the verdict rule were not touched.

Pre-registered before the run: bar `delta_excess > 0.02`; 95% cluster bootstrap over **class**
must exclude 0; ≥10 learners in each of a pair's four cells; <20 surviving pairs ⇒ UNANSWERABLE.

## Result

| structure | pairs | obs | excess | instrument noise (2sd) | verdict |
|---|---|---|---|---|---|
| S1 CCSS grade | 5 | — | — | — | UNANSWERABLE |
| S2 module order | 54 | 13,124 | **−0.0291** | 0.0305 | UNDERPOWERED AT THE BAR |
| S3 lesson order | 71 | 19,475 | **+0.0103** | 0.0251 | UNDERPOWERED AT THE BAR |

The two curriculum grains disagree in sign. Neither clears its own noise. The direction-label
null — randomising which end of each pair is "first" — sits at −0.011 ± 0.030 and −0.002 ± 0.019,
which is to say indistinguishable from the real labelling. The full positivity sweep (cells ≥ 5,
10, 20, 30) is in `out/direction.log`; every setting is reported. One setting reads NOT RECOVERED: module order at cells ≥ 5 (96 pairs, −0.0326 against noise 0.0244); every other setting is UNDERPOWERED or UNANSWERABLE (corrected 2026-09-24).

**The bar is below the instrument's noise floor.** That is the finding. A null at 0.02 from an
instrument whose own unplanted arm scatters by ±0.025–0.031 says nothing about curriculum and
everything about sample size, which is why the verdict is *underpowered*, not *not recovered*.

## Controls, and the two they caught

- **Floor.** Synthetic learners shaped like the real selection, a +0.150 gate planted on the
  forward direction only. Recovered **+0.1487 to +0.1558**, unplanted arm centred on zero. The
  instrument works.
- **Deranged arm.** Pass/fail labels deranged within each (pair, direction) stratum — a
  derangement, not a permutation. Everything reported as excess over its own deranged arm.
- **Direction-label null.** The direction labels themselves randomised across pairs.
- **Clustering.** Intervals resample whole classes, each drawn copy getting its own learner
  namespace.

Two defects the controls caught, both already written in this repo's rules and both re-committed
here anyway:

1. **A single synthetic draw is not a floor.** The first version scored **+0.0222** on an
   *unplanted* arm — over the 0.02 bar, from noise alone — and would have been read as a
   detection. Both floor arms now average over 25 draws.
2. **A single derangement is not a control.** Reading the excess off one deranged arm moved the
   S2 headline from −0.0188 to −0.0052 between two runs differing only in RNG consumption. Both
   deranged arms now average over 25 derangements, and each sweep cell is seeded from its own
   identity so the sweep row and the headline are the same number.

## What would settle it

Instrument noise falls as `0.224 / sqrt(pairs)`.

| | pairs |
|---|---|
| in hand, best setting | 128 |
| to resolve the bar | ~126 (i.e. we are *at* the limit — measured noise at that setting is 0.0270, so the fit is optimistic) |
| to resolve half the bar | **~504** |

The scarce ingredient is not learners. It is learners who meet a **later** skill **before** an
earlier one. Only 128 of 1,250 both-order pairs survive direction and positivity, because
cohorts marched through one publisher's sequence in that publisher's order. A corpus recruits
that cell by holding learners on **different curricular sequences** — several publishers, or
transfer students, or an out-of-order intervention — not by holding more learners on the same one.

That is the exact ask, and it is a property to check *before* acquiring a corpus for A4, not after.

## Files

- `prep.py` — distils the 966 MB assignment log into one cell table (scratchpad only)
- `direction.py` — the study, with floor, derangement, direction-label null and class clustering
- `out/direction.json`, `out/direction.log`

Reproduce with `EDMCUP_DIR=<scratchpad>/edmcup python3 prep.py && ... python3 direction.py`.

**Reversed-arrow control (2026-09-24):** the within-pair delta is antisymmetric, so the control reads each structure's sign: S1 grade −0.1425 (5 pairs, UNANSWERABLE) and S2 module −0.0328 read REVERSED, S3 lesson +0.0063 CLAIMED — the same sign disagreement already reported, all inside the instrument's noise. Reproduced exactly.

## Official release swapped in (2026-09-25)

`assignment_details.csv` now comes from the official release (osf.io/yrwuh, file q946d, md5
bb1b3328c8ce8d178223c71d5e593304) instead of the osf.io/7stjh mirror, which masked start and end
times on the 53,615 unit-test rows. `prep.py` rebuilt `cells.tsv` from it byte-identical (md5
a579b4d8a46fed1028c2aa963fb14bba), because unit tests are anchored on their in-unit practice times
and no practice row was masked. Every result that reads `cells.tsv` is therefore unchanged: this
study, the positivity atlas and lag bands, window-depth and conjunctive-reachability. All four
`data/invariants.py` checks for this source pass on the new copy.
