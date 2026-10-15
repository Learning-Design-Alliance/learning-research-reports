# Does a surmise relation constrain the edge space, or assert into cells the corpus cannot read?

**What was asked.** Knowledge-space methods — IITA and its relatives — are usually placed *upstream*
of an assay, as a constraint generator: they narrow the space of admissible graphs before anything
is fitted. That is the hope this study tests, and it is testable cheaply, because IITA and the
positivity audit read **the same cell from opposite ends**.

IITA asserts `A precedes B` when few learners solved B without solving A — a **low counterexample
count**. `studies/identifiability/overlap/positivity.py` can decide whether A gates B only when many learners reached B
**without** holding A — a **large identifying cell**. Those are the same learners. A corpus where
nobody meets B without A gives IITA its strongest evidence for the edge and gives the audit nothing
at all.

**What came back.** Across three corpora IITA asserts hundreds of edges, and between **88.6% and
100%** of them land on pairs the corpus cannot decide either way. On Junyi it asserts 81% of all
ordered pairs, with **64% of unordered pairs asserted in both directions at once** — which is an
equivalence, not a prerequisite, and orients nothing. Surmise output is a **prior wearing a
constraint's clothes**. It may be carried downstream as a weighted hypothesis; it may not be used
to close the edge space.

## Pre-registered verdict

Written before any real number was read (`overlap_iita.py`, module docstring):

| asserted edges landing in UNKNOWN | verdict |
| --- | --- |
| ≥ 90% | prior, not a constraint |
| decided ≥ 25% | checkable claim on this corpus |
| between | mostly undecidable |

## The cross-tabulation

Both methods over the same items; the audit is run twice, once on IITA's complete-case learners
(like-for-like) and once on every learner who reached the item (the corpus at full strength, so an
UNKNOWN there is the corpus's and not the join's).

| corpus | items × sets | IITA asserts | unknown (same population) | unknown (every learner) | verdict |
| --- | --- | --- | --- | --- | --- |
| ds1190 | 8 × 2 | 40 of 112 (36%) | 100.0% | 100.0% | prior, not a constraint |
| Junyi | 8 × 2 | 91 of 112 (81%) | 100.0% | 100.0% | prior, not a constraint |
| ASSISTments | 16 × 2 | 237 of 480 (49%) | 100.0% | 88.6% | mostly undecidable |

ASSISTments at full strength decides 27 of the 237 asserted edges — 23 confirmed, 4 refuted. It is
**1.4 points short** of the pre-registered 90%, so the verdict is the weaker one. The threshold was
not moved.

## The relation before any data is joined to it

A relation can fail to constrain without ever being checked, and two numbers say so on their own:

| corpus | ordered pairs asserted | asserted in BOTH directions |
| --- | --- | --- |
| ds1190 | 36% | 3 of 56 (5%) |
| Junyi | **81%** | 36 of 56 (**64%**) |
| ASSISTments | 49% | 51 of 240 (21%) |

A quasi-order is permitted to contain `(i,j)` and `(j,i)` together — IITA is not misbehaving. But a
pair asserted both ways carries no ordering information, and on Junyi that is most of them. An
estimator that asserts four fifths of the ordered pairs has not narrowed the space it was brought in
to narrow.

## The detection floor, and what it took away

Two arms, 3,000 synthetic learners, 14 items, randomised order and a planted gate. The soft arm
plants a 0.30 drop — real, well above the 0.10 effect being claimed, but **not a quasi-order**. The
hard arm plants a 0.60 drop, nearly forbidding the dependant, which is IITA's own assumption.

The first version of this floor **passed while leaving a cell unreachable**. It confirmed the audit
decided every pair and that every IITA assertion resolved — and every one of them resolved to
CONTRADICTED, with **zero** in SUPPORTED. Nothing in that run established that `asserted & SUPPORTED`
could be reached at all, and a cross-tab with an unreachable cell would report "IITA confirms
nothing" on real data no matter what the data held. The hard arm was added to fill it, and it does.

One criterion then failed, and it was kept as a failure:

| | soft | hard | floor |
| --- | --- | --- | --- |
| pairs the audit decides | 100.0% | 72.0% | 50% |
| planted edges returned SUPPORTED | 31.8% | 35.0% | **50% — FAILS** |
| assertions landing in a decided cell | 100.0% | 100.0% | 50% |
| IITA precision vs planted truth | 62.5% | 82.4% | — |
| IITA recall vs planted truth | 22.7% | 35.0% | — |

**Why it fails, and it is not a bug.** A pairwise drop tests **one arm of a conjunctive gate**. When
a dependant needs four prerequisites, the learners who hold A are mostly missing something else B
needs, so both cells sit at the floor and the planted drop disappears:

| dependant's fan-in | planted edges | returned SUPPORTED | median observed drop |
| --- | --- | --- | --- |
| 1 prerequisite | 2 | 100% | +0.607 (planted 0.60) |
| 2–3 prerequisites | 6 | 83% | +0.111 |
| 4+ prerequisites | 32 | 22% | +0.018 |

So each floor check is tied in code to the reading it licenses, and a failed check **withdraws a
reading** rather than being argued away:

- **Reading 1 — prior vs constraint, from the UNKNOWN share: LICENSED.** The assertions resolve, and
  both the confirmed and the refuted cells are reachable.
- **Reading 2 — confirmed vs refuted as IITA's accuracy: WITHHELD.** CONTRADICTED beside an IITA edge
  does not establish the edge is wrong. The split is printed, because hiding it would be worse, but
  it does not enter the verdict.

This is a limit on `studies/identifiability/overlap/positivity.py` as much as on this study, and it is new: **the audit's
SUPPORTED state is a test of a single-prerequisite gate.** Conjunctive structure is close to
invisible to it, which is one more reason a non-SUPPORTED pair must never be read as a non-edge.

## Two design choices that could have produced the answer on their own

Both are controlled rather than argued:

- **Complete-case learners.** IITA reads "did not solve B" off a response pattern, and a learner
  never asked B is not a counterexample to anything, so both methods run on learners who touched
  every item in the set. But that restriction is mine and it destroys most of the corpus's power —
  on ASSISTments it takes 29,018 learners down to 224. So the audit is run a second time over
  everyone. That column is where ASSISTments moves from 100% unknown to 88.6%: **most of the
  like-for-like result was my restriction, and about an eighth of it was not.**
- **Item-set size.** Twenty items leaves 33 complete-case learners on Junyi, and a join over 33
  learners reports UNKNOWN for reasons that have nothing to do with the corpus. Size is therefore
  chosen as the largest that keeps 200+ complete-case learners — a decision made on learner counts
  alone, **before any state is computed**, so it cannot be tuned against the answer.

## What this changes

`studies/identifiability/learning-structure/SURMISE.md` already had the accuracy half of this: recovery precision 0.40, with
29.9 ± 9.1 spurious of 49 found. This is the other half, and it is the one that matters for the
assay's architecture. The distinction being drawn is between what is **permissible** and what is
**probable**, and surmise output does not belong on the permissible side:

- It may enter as a **prior over edges**, weighted, alongside the other proposers.
- It may **not** populate `required` in a graph sandwich, and it generates no `forbidden` at all —
  it has no machinery for absence.
- Anything that consumed an IITA relation as a hard constraint was consuming a prior with its label
  removed.

The corollary is the uncomfortable one. The constraint layer is supposed to cut the candidate space
before probability is applied. We now have **no validated empirical source of hard constraints** —
what remains is logical (acyclicity, part-of antisymmetry), which is real but cuts very little.

## Running it

```
python3 overlap_iita.py floor
python3 overlap_iita.py real junyi|assist|ds1190 [--sets 8] [--items N] [--out out/x.json]
```

Raw exports stay outside the repo (DataShop and ASSISTments both forbid redistribution); only the
aggregate counts in `out/` are committed.

## The reachability gate, added 2026-09-24 — and it changed a verdict

`CONTRADICTED` now requires a merge node that is both **readable** and **powered**
(`shared/edge_state.py`, `shared/reachability.py`). The gate runs inside `positivity_states()`, so
**both** readings this study reports are gated on their own learner set rather than one borrowed
from the other — which matters here, because the whole point of running it twice is that the
complete-case restriction is the author's choice and the every-learner reading is the corpus
answering with everything it has.

**Every contradiction on ASSISTments goes: 17 → 0.** Thirteen in the two population crosstabs, four
more in the per-set detail.

**This is the first study on the board whose verdict the gate actually moved**, and it moved it
*toward* the study's own thesis:

| | before | after |
|---|---|---|
| same population | `PRIOR, NOT A CONSTRAINT` (100.0% unknown) | unchanged |
| **every learner** | **`MOSTLY UNDECIDABLE`** — 88.6% unknown, 11.4% decided | **`PRIOR, NOT A CONSTRAINT`** — 90.3% of asserted edges undecidable |

The every-learner reading previously looked *partially* decidable: 4 of IITA's asserted edges came
back contradicted and 9 of the silent ones did. All 13 were flat results on powered **pairwise**
tests whose **conjunctive** counterpart was never powered. With them gone, the surmise relation
lands on pairs this corpus cannot decide either way in **both** readings, which is the cleaner
statement of what the study found.

The supported counts are untouched — 23 asserted, 26 silent — because falsifiability bears on the
negative branch alone. An edge the data confirms is confirmed whether or not a merge node exists.


**Reversed-arrow control (2026-09-24):** IITA's precision against the planted relation is 82.4% vs 0.0% reversed on the hard arm (CLAIMED), so its pairs join the audit the right way round. On real data it cannot orient anything: Junyi, ds1190 and ASSISTments' same-population reading are 0% SUPPORTED both ways (UNRESOLVED), and ASSISTments' every-learner reading is 9.7% SUPPORTED vs 10.5% for the reversed assertions (REVERSED, with unknown 90.3% vs 89.5% — the reversed relation would fall just under the 90% PRIOR line). **The rerun floor does not reproduce `out/floor.json` as committed:** that file predates the reachability gate inside `positivity_states()`, and with the gate the audit decides 11.5% / 61.5% of pairs and two floor checks fail, so READING 1 is WITHHELD by the current code (the rerun file is now in `out/floor.json`; with the gate disabled the old file reproduces exactly). The real-data outputs reproduced exactly.

## Post-hoc (2026-09-25): the gated floor failure is a power floor

With the reachability gate in place, the pre-registered floor fails at 3,000 learners and Reading 1
is WITHHELD by the code as it stands. `floor_scale.py` (post-hoc, labelled so in its docstring)
reruns the same two arms with the same seeds and thresholds, changing only the learner count
(`out/floor-scale.json`):

| learners | soft: decided / assertions decided | hard: decided / assertions decided / planted SUPPORTED | Reading-1 checks |
| ---: | --- | --- | --- |
| 3,000 | 11.5% / 37.5% | 61.5% / 70.6% / 35.0% | fail |
| 10,000 | 97.3% / 88.9% | 91.8% / 100.0% / 52.5% | pass |
| 30,000 | 100.0% / 100.0% | 98.4% / 100.0% / 90.0% | pass |

The gate asks for a powered merge node before it will call a contradiction, and 3,000 randomised
learners over 14 items cannot supply one for most pairs. At 10,000 every Reading-1 check passes,
and at 30,000 the accuracy check (Reading 2's floor) passes too.

What this licenses, and what it does not:

- **ASSISTments, every learner (29,018): readable.** It is at the scale where the floor passes, and
  90.3% of IITA's assertions are undecidable there. This is the one real reading that the floor
  supports.
- **Every same-population reading: not interpretable.** These run on 50–224 complete-case learners
  per set, far below any scale where the floor passes. Their 100% UNKNOWN is at least partly the
  audit's lack of power, not the corpus's silence. They are kept in the table as reported, not read.
- **The floor is still randomised-order.** The real corpora are not, so passing at 10,000 does not
  guarantee that a real corpus of that size can decide its pairs. It shows that the 3,000-learner
  failure is about sample size and not a defect in the join.

The pre-registered verdict for the study as a whole stays WITHHELD at the registered floor. The
statement Paper 1 carries is narrower: on the one corpus large enough for the floor to pass, about
nine in ten surmise assertions land where the data cannot decide them.
