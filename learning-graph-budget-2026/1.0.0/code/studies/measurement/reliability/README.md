# A5: run the assay twice on split data — does it say the same thing?

**Asked:** A5 has stood at **0.523** against a 0.80 gate, measured on ASSISTments skill builders' retention estimand (`studies/identifiability/rdd/`; earlier text said Junyi) over
690 edges. That figure was obtained where the identifying cell is largely **empty** — you cannot rank
edges reliably when most of them cannot be read at all — so it has never been clear whether 0.523 is
a fact about the assay or a fact about the corpora it was measured on.

Two corpora now settle that. XES3G5M reads 24.3% of arbitrary ordered pairs and EdNet 81.5%: the only
two on disk where the identifying cell survives, because both are practice platforms where learners
choose rather than tutors that gate.

**Came back: it is a fact about the assay.** Readable data did not make the edge ranking reliable.

## Result

Split the learners at random into halves, score every pair independently on each half, Spearman across
pairs, Spearman–Brown back to the full sample. 12 splits. Method unchanged from
`studies/identifiability/junyi/assay_controls.py` so the numbers are comparable.

| corpus | min cell | pairs | split-half | **Spearman–Brown** | reach-partialled | predictor ceiling |
|---|---:|---:|---:|---:|---:|---:|
| XES3G5M | 5 | 1,261 | +0.342 | **0.510** | 0.507 | 0.714 |
| XES3G5M | 10 | 1,036 | +0.392 | **0.563** | 0.560 | 0.750 |
| XES3G5M | 20 | 812 | +0.474 | **0.643** | 0.640 | 0.802 |
| EdNet | 5 | 4,340 | +0.065 | **0.122** | 0.120 | 0.349 |
| EdNet | 10 | 3,563 | +0.073 | **0.135** | 0.135 | 0.368 |
| EdNet | 20 | 2,364 | +0.100 | **0.182** | 0.175 | 0.426 |

EdNet re-issued 2026-09-24 through the reproducible zip-prefix reader (`shared/corpus.EdNet`); the
earlier rows (0.287 / 0.320 / 0.337) came from an extracted subset that cannot be re-derived. Re-run at
the same 12 splits, **XES3G5M's three rows are identical to every digit**, so the whole change is
EdNet's reader. EdNet's reliability fell to between a third and a half of what was recorded, the same
direction and size as `TAIL.md`'s re-issue.

The standing figure was 0.523. The best cell here is **0.643**, and that is on the *smallest*
sub-sample of pairs. **A5 remains unmet, and the corpus explanation is gone.**

## Three things the table says

**1. The corpus that reads the most edges ranks them the least reliably.** EdNet is readable on 81.5%
of pairs and reaches 0.182; XES3G5M is readable on 24.3% and reaches 0.643 (readable shares from the
re-issued `studies/identifiability/overlap/out/atlas.json`). That inversion is not a
paradox — EdNet's background drop is +0.048, among the smallest of any corpus, so its edge estimates are
mostly noise around a small effect, and there are simply more marginal pairs in the ranking. **More
readable pairs means a longer ranking of smaller differences.**

**2. Reliability is bought by discarding pairs, not by the assay agreeing with itself.** On XES3G5M,
raising the cell floor from 5 to 20 moves Spearman–Brown 0.510 → 0.643 while the pair count falls
1,261 → 812. Any reliability figure quoted without its cell floor and pair count is unreadable, and
this is why the whole sweep is reported rather than the best row.

**3. It is not a ranking of reach.** The obvious alternative — that the assay is really ordering pairs
by how many learners reach them, which would replicate beautifully and mean nothing — is dead. The
reach-partialled figures are within 0.013 of the raw ones everywhere.

## The ceiling this puts on everything downstream

If the assay correlates with itself at *r*, no predictor can correlate with it above roughly √*r* for
reasons having nothing to do with the predictor. At the **best** cell on the **best** corpus that
ceiling is **0.802**; on EdNet it is **0.426** (re-issued; was 0.536).

Every elicitation and critic number in this repo sits under it. The panel-elicitation ceiling, the
cheap-proxy correlation, the critic's agreement — none of them can exceed this, and a disattenuated
figure must be reported beside the raw one or the comparison is meaningless.

## What this points at, and it is a design question rather than a data one

A per-edge readout that replicates at 0.51–0.64 **cannot support edge-level claims**. The assay's
output unit may simply be wrong: a ranking this unstable might still be stable in aggregate — over a
module, a topic, a subgraph — and the programme has never tested a coarser readout because it
inherited the edge as the unit from the literature it was arguing with.

That is the next thing to measure, and it is measurable on the same data with no new permissions.

## Provenance

XES3G5M and EdNet (CC BY-NC 4.0 — non-commercial, no model training; counting cells is neither).
Exports stay in the scratchpad; only the aggregate row per corpus and cell floor is committed.

## Run

```
python3 split_half.py --splits 12
```

---

# Is the edge the wrong output unit? (`coarse.py`)

**Asked:** a per-edge ranking replicating at 0.51–0.64 cannot support edge-level claims. The programme
inherited the edge as its output unit from the literature it argues with. Does a coarser readout —
group pairs rather than item pairs — replicate well enough to be usable?

**Came back: no.** Coarsening does not rescue reliability.

> **CHANGE 1 (2026-10-14, post hoc, maintainer's decision).** The release reproduction found the single
> matched random grouping depended on Python's string-hash seed, and the L3 verdict flipped under one seed.
> The control is now the mean of 50 matched random groupings drawn from their own generator. That also
> redrew seven of the eight learner splits, so the edge and taxonomy rows moved as well. Verdict rule and
> margin unchanged; the verdicts are the ones first published. The single-draw output is kept as
> `out/coarse-single-draw.json`. Every number below is CHANGE 1's (`out/coarse.json`).

| grain | groups | group pairs | split-half | **Spearman–Brown** |
|---|---:|---:|---:|---:|
| **edge (per item pair)** | 865 | 30,000 | 0.314 | **0.478** |
| taxonomy L2 | 53 | 337 | 0.295 | 0.455 |
| taxonomy L3 | 187 | 547 | 0.361 | 0.530 |
| taxonomy L4 | 425 | 153 | 0.393 | **0.564** |

Nothing approaches the 0.80 gate. **The design fix this study was built to test does not work**, and
"report at module grain instead of edge grain" is not an available answer.

## The control was the whole point, and it did not go as predicted

Aggregation raises reliability mechanically, since averaging *k* noisy estimates cuts noise by √*k*, so
every taxonomic grain ran beside matched random groupings: same number of groups, same group-size
distribution, same splits, same edge scores.

| level | taxonomy | matched random, mean of 50 [2.5th, 97.5th] | gap | taxonomy above | |
|---|---:|---:|---:|---:|---|
| L2 | 0.455 | 0.436 [0.393, 0.484] | +0.020 | 80% of draws | aggregation only |
| L3 | 0.530 | 0.442 [0.406, 0.467] | **+0.089** | 100% | taxonomy beats random |
| L4 | 0.564 | 0.477 [0.412, 0.554] | **+0.088** | 98% | taxonomy beats random |

**The pre-registered prediction was that taxonomy would match random**, on the grounds that
`studies/identifiability/taxonomy-order/` found this same hierarchy inert for ordering. That prediction was **wrong at L3 and
L4**.

### The confound, checked rather than assumed

`MIN_EDGES_PER_GROUP_PAIR = 3` bites differently on the two arms: taxonomic groups concentrate edges
because KCs in a module co-occur, so more group pairs clear the filter. The taxonomy's advantage could
therefore be that its group means are simply better estimated.

**It is not.** Edges per scored group pair are *identical* at every level — median 7.0 / 7.0 at L2,
4.0 / 4.0 at L3, 3.0 / 3.0 at L4, with means within 1.1.

**What remains unexcluded:** the taxonomic arm scores *more* group pairs (547 against 454 at L3, 153
against 79 at L4, CHANGE 1's medians), so it may sample a wider spread of true values, which would raise
a rank correlation without the grouping being meaningful. The gaps have a spread over random draws but
no interval over learner splits. (The edges-per-group-pair check above was made on the single-draw run.)

## Why this is coherent with taxonomy-order rather than contradicting it

`studies/identifiability/taxonomy-order/` measured the same hierarchy as **inert for ordering**: same module buys +0.0161 over
an arbitrary pair, non-monotone in distance, ancestor-vs-descendant at −0.0128 with the wrong sign.
Here the hierarchy carries something about **magnitude** — how strongly two regions relate, which is
what a rank correlation reads — while carrying nothing about **which comes first**.

Containment predicts *relatedness*, not *sequence*. That is the third study to land on the same
distinction: `studies/producers/direction-benchmark/` found a text model recovers **generality, not prerequisite**, and
`studies/identifiability/taxonomy-order/` found containment carries no order. A curricular hierarchy is a similarity
structure that has been drawn as a tree.

## Board

Does not move A5: nothing reaches the gate at any grain, so the reliability problem is not solved by
changing the output unit. It removes a candidate answer, which is what it was run to do.

---

# Is the ESTIMAND the lever? (`retention.py`)

> **Re-issued 2026-09-24 ([`docs/notes/EDNET-REISSUE.md`](/docs/notes/EDNET-REISSUE.md)):** EdNet retention split-half (SB) is 0.117 (was 0.183) and the gain −0.057 (was −0.140); the gate still fails and the conclusion stands. **Rerun 2026-09-25** with EdNet's `-1` (no-KC) questions dropped and tie-averaged ranks: EdNet first attempt 0.174 → 0.154, retention 0.117 → 0.080, gain −0.057 → −0.074; XES3G5M moves in the fourth decimal. Same conclusion, a little stronger.

**Asked:** `coarse.py` showed the output unit is not the lever. The remaining candidate was the
estimand, with prior evidence behind it: on ASSISTments skill builders (`studies/identifiability/rdd/`) the concentration test scored **0.523** on retention
against **0.458** on first-attempt correctness, and `studies/identifiability/rdd/lag.py` showed first-attempt correctness is
the wrong outcome in principle — the prerequisite deficit *decays* on it (+0.0440 at a fortnight,
+0.0134 by eleven weeks) while the durability deficit does not (+0.0312 at equal initial success).

**Came back: retention is substantially WORSE.** The pre-registered prediction — "improved but still
short", expecting roughly +0.065 — was wrong in direction.

Both estimands scored on **the same pairs, the same splits, the same learners**: a pair counts only if
both are readable on both halves, so the difference is the outcome and not the sample.

| corpus | pairs | first attempt | **retention** | gain |
|---|---:|---:|---:|---:|
| EdNet (re-issued; no-tag questions dropped) | 3,252 | 0.154 | **0.080** | **−0.074** |
| XES3G5M | 531 | 0.641 | **0.336** | **−0.305** |

## Two explanations tested and refuted, one supported

**Refuted — single-binary noise.** `MIN_LATER = 1` lets a retention score be the mean of one later
attempt, with none of the noise reduction the estimand is supposed to buy. XES3G5M's median is 2
attempts per learner-item, so this looked likely. It is wrong: on EdNet the gain is **−0.140 / −0.134
/ −0.146** at MIN_LATER 1 / 3 / 5. Flat.

**Refuted — restriction of range.** Conditioning on first-time success selects a more homogeneous,
higher-performing subgroup, which would attenuate any correlation. Also wrong: the between-pair SD is
0.0520 for retention against 0.0570 for first attempt, a ratio of **0.911**. The signal is nearly all
still there.

**Supported — it is sample size.** The median smaller cell is **122** for retention against **264** for
first attempt, a ratio of **0.459**. Retention keeps 91% of the between-pair signal with 46% of the
sample behind each estimate; halving *n* raises the standard error by about 41% while the signal stays
flat, and reliability falls exactly as observed.

**Retention is not a less noisy outcome. It is a smaller one.** Conditioning on first-time success
costs more in sample than it gains in precision.

## The two estimands rank edges almost independently

**r = +0.126** across 5,552 pairs scored on both. `A10` already records that the gate and hook readings
disagree — *"Both are now measured on the same data and they disagree, which is the point"* — and this
puts a number on it. They are not two views of one quantity, and an edge ranking is not a property of
the data alone: it is a property of the data *and* the outcome chosen.

## On the Junyi precedent, which is not strictly contradicted

The 0.523 came from `studies/identifiability/rdd/retention_edges.py`: a **concentration** test on downstream skills after a
mastery exit, on a platform with an explicit release-without-mastery rule. That is a different
statistic on a different design. What failed here is **my assumption that it would transfer to a
pairwise drop** — the number itself stands where it was measured.

## What this settles for A5

Neither the output unit nor the estimand rescues reliability. `studies/identifiability/rdd/retention_edges.py` wrote the
conclusion in advance: *"If the edge ranking is still unreliable on the better estimand, that is a fact
about how much structure is there to find, not about the choice of outcome."*

Two levers have now been tried and neither moved it. **The unreliability is about how much structure
is there.**

**Correction (2026-09-25): EdNet's `-1` tag is not a KC.** 797 of EdNet's 13,169 questions carry only the undocumented tag `-1`, which the reader had turned into a unit; it is now dropped (`shared.corpus.ednet_questions`). Rerun: EdNet split-half Spearman–Brown at cell floors 5 / 10 / 20 is **0.098 / 0.125 / 0.136** (was 0.122 / 0.135 / 0.182; pairs 4,382 / 3,569 / 2,343), reach-partialled 0.096 / 0.122 / 0.127, predictor ceiling at floor 20 **0.369** (was 0.426). XES3G5M is unchanged. No verdict changes: every EdNet row stays far below the 0.80 bar, and the paradox in point 1 is sharper. The tables above keep the pre-correction figures.

**Ties (2026-09-25).** `split_half.py` ranked with `np.argsort(np.argsort(...))`, which breaks ties
by position; it now uses `shared.stats.rank`. Rerun at the committed 12 splits: every figure moves
in the fifth decimal or less (XES3G5M 0.510 / 0.563 / 0.643, EdNet 0.098 / 0.125 / 0.136 unchanged).

---

# A calibrated bar? (`kappa_bar.py`, Paper 2 placeholder 3)

**Asked:** at what decision kappa does a graph-driven sequencing decision stop costing more than it
saves? A5's 0.80 is a convention; the board said the calibration was outstanding. The machinery is
`studies/end-to-end/xes3g5m-build/practice_value.py`'s: unneeded practice at matched premature-advance
risk (0.20), in items per 1,000 attempts, against a readiness model with no graph. The graph is used
as a sequencing rule: not ready for B while an asserted parent A is FAILED (attempted, not yet
passed). Pre-registered (`a5b29f3`) with planted worlds shaped like XES3G5M (tuned once to its
first-attempt accuracy and median drop: theta sd 0.8, mu 2.0 gives 0.729 / 0.109 against 0.763 /
0.102; the first tuning grid did not bracket the target and was moved before any items-saved number,
CHANGE 1).

**Came back: no bar can be sized this way, because the observable sequencing rule never pays, not
even with the true graph.** The pre-registered floor FAILED, so the sweep and the real XES3G5M arm
were not run and no break-even kappa is read.

| world (density 0.10, seed 1) | split-half kappa | SB | edges (precision) | HARD rule saves, items / 1,000 |
| --- | ---: | ---: | --- | --- |
| estimated graph, 500 learners | +0.080 | +0.262 | 828 (0.08) | −80.7 [−83.6, −77.5] |
| estimated graph, 32,000 learners | +0.646 | **+0.899** | 2,507 (**0.07**) | −172.9 [−176.5, −168.9] |
| random graph, same size | — | — | 2,507 | −261.0 |
| **true graph (oracle)** | — | — | 194 (1.00) | **−4.2 [−5.5, −3.0]** |
| graph as a fitted feature (soft) | | | | −0.1 to −1.8 |

A post hoc diagnostic (CHANGE 2, labelled) separates the instrument from the world. With much stronger
gates, U(0.5, 0.8), the oracle hard rule still costs −4.8 [−5.7, −3.9], but a rule that blocks exactly
the attempts where the learner truly lacks a true parent saves **+39.0 [+36.5, +41.3]**. So the
machinery sees a gate's value. What fails is the observable proxy: "attempted A and not yet passed" is
not "lacks A" when learners arrive already holding some skills and pass on retries.

**Three things follow.**

1. **The 0.80 bar is neither justified nor refuted by sequencing value.** In these worlds the
   decision a graph drives costs practice at every graph accuracy, so the kappa at which it "stops
   costing more than it saves" does not exist. Verdict on the registered scale: NO BAR JUSTIFIES A
   HARD GATE (floor world; the other worlds were not read).
2. **As a validity guarantee, 0.80 is far too lax.** At 32,000 learners the assay clears A5's bar
   (SB +0.899, kappa +0.646, all of it excess over deranged) while 93% of the edges it asserts are
   false. The false edges are ability-driven: learners who pass A are abler, so they also do better
   on B. The deranged arm removes that confound along with the dependency, so excess-over-deranged
   does not catch it. Reliability measures whether the assay repeats itself; it cannot say the
   repeated answer is a prerequisite.
3. **What would calibrate a bar** is a decision whose value depends on edge accuracy: a randomised
   edge release (Paper VII), or a soft use whose value is measured. The soft use here is worth about
   nothing at any accuracy.

**Assumptions** (stated before the run): subtractive gates for every learner, no hidden second skill,
no interaction between edges, prior holding at logistic(theta − beta). Real gates are softer
(conjunctive attenuation, Paper II), which makes a hard rule worse, not better.

Outputs: `out/kappa_bar_tune.json`, `out/kappa_bar_floor.json`, `out/kappa_bar_diagnostic.json`.

**For Paper II (placeholder 3):** replace the placeholder with: "No reliability bar can be calibrated
from sequencing value on these data shapes. A hard prerequisite rule driven by observed failure costs
practice even with the true graph (−4 to −5 items per 1,000 attempts at matched risk). An assay can
also clear 0.80 split-half reliability while 93% of its edges are false. A reliability bar is a
repeatability floor, not a validity bar; edges need an experimental check (randomised edge release)."

---

# Reliability by lag band (`lag_band_reliability.py`, Paper 2 placeholder 2)

**Asked:** the drop shrinks with the lag between first trying A and first trying B (LAG-BANDS.md), so
a reliability pooled over lags pools estimands. How reliable is the drop *within* a band? Pre-registered
at `2ec0b52` with its floor (synthetic: FLAT band-minus-thinned within ±0.05; DECAY EARLY +0.15 / +0.21,
LATE −0.07 / −0.12: PASSES). `pairgrid.py` (matrix form of `positivity.classify`) was asserted equal to
it on 200 pairs of each corpus before anything was read.

**Came back: no band reaches 0.80, so lag banding does not rescue A5. But the same-day band is more
reliable than its sample size implies, on XES3G5M.**

XES3G5M, 200 best-covered KCs (39,800 ordered pairs), 18,066 learners, 20 splits:

| floor | band | pairs | Spearman–Brown | kappa | deranged SB | size-matched (thinned) SB | band − thinned [central 95% of splits] |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 10 | EARLY (< 1 day) | 3,289 | +0.610 | +0.364 | +0.034 | +0.520 | **+0.089 [+0.062, +0.114] LAG RAISES RELIABILITY** |
| 10 | MID (1–7 days) | 4,642 | +0.549 | +0.315 | +0.018 | +0.484 | +0.065 [+0.038, +0.081] LAG RAISES RELIABILITY |
| 10 | LATE (≥ 7 days) | 28,654 | +0.675 | +0.415 | +0.055 | +0.683 | −0.008 [−0.012, −0.003] LAG LOWERS (by less than 0.01) |
| 10 | ALL | 30,266 | +0.699 | +0.442 | +0.059 | — | — |
| 20 | EARLY | 2,200 | +0.717 | +0.429 | +0.107 | +0.642 | +0.074 [+0.060, +0.103] |
| 20 | LATE | 26,563 | +0.717 | +0.431 | +0.062 | +0.723 | −0.006 [−0.009, −0.003] |
| 20 | ALL | 28,248 | **+0.736** | +0.458 | +0.065 | — | — |

EdNet, atlas prefix (6,000 learners, 141 items, 19,740 pairs): every band is far below the bar (floor
10: EARLY +0.120, MID +0.020, LATE +0.093, ALL +0.146), and band − thinned is SIZE ONLY or UNRESOLVED
at every floor. EdNet cannot say whether lag matters for reliability.

Control scale (`shared/controls.check_control_scale`): the thinned arm's median cell is 0.95–1.14×
the band's on both corpora, so the size control is the size of the thing it controls. Where it is
larger (EARLY, 1.14×) it favours the control, so the EARLY advantage is conservative.

**What it means.**

1. **A5 is not rescued.** The best band at the primary floor is XES3G5M LATE at +0.675; the best at
   any floor is ALL at floor 20, +0.736, on the 200 best-covered KCs (A5's standing 0.643 is the
   all-865-KC random-pair reading). Programme verdict: LAG BANDING DOES NOT RESCUE A5.
2. **Same-day pairs carry more signal per learner.** On XES3G5M, a same-day band is +0.09 more
   reliable than a lag-blind sample of the same size, and the 1–7-day band +0.06. The week-plus band
   is no better than its size. This fits LAG-BANDS.md: the drop is largest within a day, so a
   same-day reading is a cleaner, larger estimand. It is still a different population (learners
   who reach B the same day), which the size control does not remove.
3. **The pooled figure is mostly the LATE band.** 95% of XES3G5M's readable pairs are readable at
   lag ≥ 7 days and only 11% within a day. So the "A5 reliability" the programme quotes is mostly a
   week-plus estimand.
4. **Deranged arms are small** (SB +0.00 to +0.11), and kappa's deranged arm is ≤ +0.04 at floor 10.
   As `kappa_bar.py` shows, though, the deranged arm does not remove learner-ability confounding, so
   excess over deranged is a repeatability figure, not a structure figure.

Output: `out/lag_band_reliability.json`, `out/lag_band_reliability_floor.json`.

**For Paper II (placeholder 2):** "Split-half reliability of the drop by lag band (XES3G5M, 200
best-covered KCs, cell floor 10): same day +0.61, 1–7 days +0.55, a week or more +0.68, all lags
+0.70; no band reaches 0.80, and EdNet's bands are all below 0.15. Against a lag-blind sample of the
same size, the same-day band is +0.09 [+0.06, +0.11] more reliable and the week-plus band no
different (−0.01). A reliability should therefore be reported with its lag band. The pooled figure
is dominated by week-plus pairs."
