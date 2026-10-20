# Which corpora can answer a prerequisite question at all?

The [positivity gate](README.md) found the identifying cell — learners who attempted the dependant
having failed the prerequisite — empty on Junyi, ds1190 and ASSISTments. That is either a fact about
three datasets or a fact about the kind of data this field collects.

So: run the gate over every corpus on disk. No new collection, no permissions beyond those already
held.

| dataset | learners | items | median cell | readable | median MDE | 20pt | supported | contradicted | **unknown** | **decided** |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ds580 | 104 | 107 | 0 | 0.9% | 0.349 | **15.5%** | 0 | 3 | 11,339 | 0.03% |
| ds1275 (Junyi) | 2,063 | 8 | 4 | 41.1% | 0.325 | 13.0% | 0 | 2 | 54 | **3.57%** |
| ds1190 | 431 | 39 | 0 | 10.3% | 0.334 | 15.1% | 2 | 0 | 1,480 | 0.13% |
| ds1706 | 79 | 16 | 4 | 40.4% | 0.399 | 2.1% | 0 | 0 | 240 | 0.00% |
| ds671 | 77 | 16 | 1 | 27.1% | 0.341 | 0.0% | 0 | 0 | 240 | 0.00% |
| ds649 | 74 | 19 | 0 | 16.4% | 0.348 | 0.0% | 0 | 0 | 342 | 0.00% |
| ds1530 | 78 | 16 | 12 | 0.0% | — | 0.0% | 0 | 0 | 240 | 0.00% |
| ds1531 | 78 | 16 | 12 | 0.0% | — | 0.0% | 0 | 0 | 240 | 0.00% |

The last four columns are new and they are the ones to read. `decided` is supported plus
contradicted, at the 0.10 effect the field claims for a prerequisite; everything else is `unknown`,
which an adjacency matrix would have written as a zero.

**Across all eight corpora: 1 edge supported, 5 contradicted, 13,114 unknown.** Four of the eight
decide nothing at all.

### "Readable" was already too generous a word

The `readable` and `decided` columns disagree by two orders of magnitude, and the gap is the point.
ds1706 is **40.4% readable and decides 0.00%**. ds1275 is 41.1% readable and decides 3.57%.

Readable means both cells clear five learners. It does not mean the test could see anything: the
median MDE across these corpora runs **0.32 to 0.40**, three to four times the effect anyone claims.
So a pair can be perfectly readable and still be incapable of distinguishing a real ten-point
prerequisite effect from nothing.

This table has been quoting `readable` as its headline since it was written. It overstates what
these corpora can do by roughly a hundredfold, and only adding the third state made that visible —
because "readable but decided nothing" and "readable and decided against" were the same cell before.

Nine further corpora were too small to read at all (under 40 learners or under 8 items).

**The best corpus available can answer the question on 15.5% of its pairs.** Three of the eight have
a completely empty median identifying cell. This is not a property of three unlucky datasets.

## The trap in ds1530 and ds1531

On the first pass those two reported an MDE of **0.000** and "sees a 20-point gate on 89% of pairs"
— by far the best numbers in the table, and entirely false.

Both are at ceiling: nearly every learner who held the prerequisite got the dependant right. A
control arm with no variance makes the standard error vanish, so the minimum-detectable-effect
search returns ~0, which reads as infinite power and means the exact opposite — there is no room
left for an effect to show up in.

`mde()` now returns "unreadable" when the control rate is within 1% of 0 or 1. Those two are the
least informative corpora here, not the most.

## Which KC model

DataShop ships several KC models per dataset and they are different models of the same learning, so
the numbers here depend on which is picked. This takes the first KC column in each export and
records its name in `out/atlas.json`. Any corpus-level claim has to name the model it was computed
under. (Until 2026-09-25 this section blamed the KC model for ds1190's 161 learners against the
canonical 431. Both use `KC (Default)`; the cause was the sample, see the correction below.)

## What this is for

A published floor per dataset is the yardstick the field does not have. Every automated-prerequisite
result is reported as an accuracy against a reference; none is reported against the detection limit
of the corpus it was computed on. With this table, a reader can tell whether a reported gain on
ds649 could have been real — it could not; that corpus cannot see a twenty-point gate on any pair.

A dataset failing here is not bad data. ITS logs are excellent for the job they were collected for,
and the tutor's own success at sequencing is precisely what empties the cell. They cannot support a
**causal** prerequisite claim, which is a different thing.

## Reproduce

```
python3 atlas.py --out out/atlas.json
```

Raw DataShop exports stay in the scratchpad under the provider's redistribution terms; only the
aggregate row per dataset is committed.

---

## How many edges does a corpus actually decide?

The table above says how many pairs are *readable*. It does not say what a reader should write down
for the rest, and until now the honest answer had nowhere to go: an adjacency matrix offers 1 and 0,
and 0 gets used both for *"we looked and there is no edge"* and for *"we could not look"*. Those are
opposite claims.

[`shared/edge_state.py`](../../../shared/edge_state.py) gives the third symbol, and `positivity.py` now
writes it for every pair:

```
SUPPORTED     readable cell, test powered to the claimed effect, the drop is there
CONTRADICTED  readable cell, powered test, the drop is NOT there   -- real negative evidence
UNKNOWN       cell unreadable, or readable but underpowered        -- NOT a non-edge
```

At the 0.10 effect the field claims for a prerequisite:

| corpus | learners | supported | contradicted | **unknown** | decided |
| --- | ---: | ---: | ---: | ---: | ---: |
| Junyi (authored pairs) | 2,063 | 0 | 0 | **775 (100.0%)** | 0.0% |
| ds1190 (all pairs) | 431 | 2 | 0 | **1,480 (99.9%)** | 0.1% |
| ASSISTments (all pairs) | 29,018 | 87 | 46 | **39,867 (99.7%)** | 0.3% |

**On the largest corpus in the programme, 0.3% of edges are decided.** Twenty-nine thousand
learners, and 99.7% of the pairs would have been written down as zeros.

Junyi's authored graph is the sharpest case: **every single one of the 757 edges its own authors
asserted comes back UNKNOWN.** Not contradicted — unknown. The corpus cannot speak to any of them
at the effect size anyone claims, and a matrix would have recorded 775 confident zeros.

### CONTRADICTED is new, and it is the only place negative evidence comes from

ASSISTments yields **46 edges the data argues against** — a readable cell, a test with the power to
see a ten-point drop, and no drop there. That is the first genuine negative evidence about an edge
this programme has produced, and positivity is the only route to it: nothing else establishes the
power that makes an absence mean something.

The rule is `classify_edge`'s ordering. Power is checked **before** the observation, so a flat result
from an underpowered test can never reach the contradicted branch. Without that, 39,867 flat
underpowered pairs would all have read as evidence against.

### What it changes downstream

Anything consuming this now has to carry three states, and the ones that matter are the two that
used to be one symbol. A graph built from these corpora is not sparse — **it is almost entirely
unmeasured**, and that is a different object with different uses. It also means the `forbidden` half
of a partial-specification scheme is nearly empty: we can populate `unknown` in bulk and
`contradicted` in the dozens, which bounds what any constraint-based completion has to work with.

---

## 2026-09-23: the two practice corpora, a reachability gate, and a row that did not reproduce

The table above is the eight DataShop exports. EdNet and XES3G5M joined the atlas afterwards, and
this run adds a third condition to the state rule and corrects one of the two rows.

| dataset | learners | items | median cell | readable | median MDE | 20pt | supported | contradicted | *(downgraded)* | **unknown** | **decided** |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| xes3g5m | 18,066 | 865 | 0 | 24.3% | 0.203 | **49.4%** | 736 | 69 | *343* | 19,195 | **4.03%** |
| ednet | 6,000 | 142 | 32 | 81.5% | 0.229 | 36.8% | 119 | 9 | *110* | 19,872 | 0.64% |
| **edmcup** | **34,580** | **351** | **0** | **2.5%** | **0.342** | **19.4%** | **3** | **0** | ***3*** | **19,997** | **0.01%** |
| ds580 | 104 | 107 | 0 | 0.9% | 0.349 | 15.5% | 0 | 0 | *3* | 11,342 | 0.00% |
| ds1275 (Junyi) | 2,063 | 8 | 4 | 41.1% | 0.325 | 13.0% | 0 | 0 | *2* | 56 | 0.00% |
| ds1190 | 431 | 39 | 0 | 10.3% | 0.334 | 15.1% | 2 | 0 | *0* | 1,480 | 0.13% |

**The best corpus on disk decides 4.03% of its pairs.** That is the headline this document has
carried in three different forms; it is still under six percent.

### EDM Cup is the largest corpus here and answers least

34,580 learners, 351 skills, **2.5% readable and 0.02% decided** — three supported edges and one
contradicted, out of 20,000 pairs (before the reachability gate; after it, 3 and 0, 0.015%). It had never been in the atlas, which is why the programme held
no positivity states for it at all, and it arrives now through the loader contract
(`shared/corpus.EdmCup`) rather than a bespoke reader.

It is worth having precisely because it is the extreme case, and it lands where
`studies/identifiability/conjunctive-reachability/` said it would: EDM Cup put only **5.2%** of its pairs inside an observed
merge node, the lowest of seven corpora, and **two of its three contradictions were downgraded** —
a 67% rate against XES3G5M's 4.6%. Its cell grain is a unit-test sitting, one row per
(learner, skill), so "passed" is that sitting's mean at or above 0.5.

More learners did not help. EDM Cup has **five times XES3G5M's learners and answers a quarter as
many of its pairs**, because the learners are spread across a published curriculum that gates who
meets what. That is the positivity argument in its cleanest form: overlap is a property of how a
platform assigns work, not of how much work it records.

### A null is only negative evidence if the corpus could have falsified it — and that takes power

`CONTRADICTED` now requires a third thing beside a readable cell and a powered test: an **observed
merge node** — some node reached after both units, carrying adequate cells in each of the four
(A-pass × B-pass) strata. Without one, a conjunctive dependency could never have shown itself, so
the flat result is not evidence and the pair reads `UNKNOWN`. `docs/specs/SPAN.md` argues the case;
`shared/reachability.py` computes it; `shared/edge_state.py` holds the rule.

The gate runs in a **second pass over the would-be contradictions only**. Falsifiability bears on
that branch alone — a pair with no merge node that nonetheless shows the drop is still `SUPPORTED` —
and reachability is O(pairs × learners-holding-both × units-per-learner), ruinous over 20,000 pairs
and trivial over the few hundred that are live. The cell floor is positivity's own `MIN_CELL`, the
same threshold that decides whether a cell is readable at all.

**The floor was the wrong instrument, and the measurement says so.** The first version of this gate
asked only whether a merge node was READABLE — at least `MIN_CELL` learners in each stratum — and
A7's open question was whether that floor should be 5 or 10. But five learners per stratum can never
resolve a ten-point gate, and no choice of floor turns a readability test into a power test. Since
2026-09-24 a node must be **readable AND powered**: the comparison between its both-passed stratum
and its weakest other stratum must be able to detect the claimed effect, `mde(n_both, n_weakest,
p_both) ≤ 0.10`. That is the same two-part rule `classify_edge` applies one level down, lifted up.

The floor question turns out to be immaterial, which is the cleanest possible answer to it:

| | candidates | survive | downgraded | *of those, readable but **underpowered*** |
| --- | ---: | ---: | ---: | ---: |
| xes3g5m | 412 | 69 | 343 | *324* |
| ednet | 119 | 9 | 110 | *106* |
| edmcup | 3 | 0 | 3 | *1* |
| ds580 | 3 | 0 | 3 | *1* |
| ds1275 (Junyi) | 2 | 0 | 2 | *0* |
| **total** | **539** | **78** | **461** | ***432 — 93.7%*** |

**93.7% of the downgrades are nodes that exist and cannot see.** The merge node is there, the four
strata are populated past the floor, and the comparison still could not have resolved the effect
being claimed. Moving the floor between 5 and 10 was never going to touch those.

**Across the whole atlas, 78 of 539 contradictions survive — 14.5%.** The rest were flat results on
powered *pairwise* tests whose *conjunctive* counterpart was never powered at all. ds1275's two and
EDM Cup's three go to zero; XES3G5M keeps 69 and EdNet 9.

A conjunctive gate is simply a more expensive thing to see than a pairwise one — it splits the same
learners four ways before comparing — so a corpus can be comfortably powered for the pairwise
question and hopeless for the conjunctive one. That is not a defect of the gate. It is the price of
the question `docs/specs/SPAN.md` says we should have been asking all along.

**ASSISTments, audited separately through `positivity.py`, goes to zero: 46 of 46.** Twenty-eight
had a readable merge node that was underpowered; eighteen had none at all. Those 46 were, by this
programme's own record, the **first genuine negative evidence about an edge it ever produced**, and
none of them survives a conjunctive test.

So **the atlas's** negative evidence about edges is now **78 edges, from two practice-platform
corpora** — XES3G5M's 69 and EdNet's 9. Every other corpus audited here, ASSISTments included,
contributes none.

**That is the atlas's count and not the programme's.** Two other studies hold `CONTRADICTED`
verdicts computed before the gate existed: `studies/identifiability/taxonomy-order/` (1,482, on XES3G5M) and
`studies/identifiability/surmise-vs-positivity/` (17, on ASSISTments). Both call `classify_edge` without the reachability
figure, so every one of those verdicts now carries `REACHABILITY GATE NOT RUN` in its own reason
string — visible rather than silent, which is why the three-valued argument was worth the extra
branch. **They have not been re-adjudicated, and the atlas's 78 should not be quoted as a
programme-wide total until they are.** ASSISTments' own re-audit suggests where that lands: its 46
went to zero.

Under **readability alone** the downgrade rate tracked merge-node reach, which is what made the gate
a per-corpus fact rather than a blanket discount — ds1275 100%, ds580 67%, EDM Cup 67%, ASSISTments
39%, XES3G5M 4.6%, EdNet 3.4%. Under the **powered** rule the long-history corpora lose that
protection, because reach was never the binding constraint for them: XES3G5M goes to 83% downgraded
and EdNet to 92%. Short-history corpora were already losing everything.

So the two halves of the gate bite on different corpora. Reach removes nulls from corpora that stop
too early; power removes them from corpora that observe the node and cannot resolve it. Only the
second is fixable by collecting more of the same data.

### EdNet's row was re-issued, and it fell by a factor of forty-five

| | published | re-issued |
| --- | ---: | ---: |
| median identifying cell | 242 | **32** |
| readable | 97.2% | 81.5% |
| median MDE | 0.095 | **0.229** |
| supported / contradicted | 1,744 / 8,995 | **119 / 115** |
| decided | **53.70%** | **1.17%** |

The old reader drew a deterministic random sample from whatever `KT1/*.csv` happened to be
**extracted on disk** — a guard against an early-cohort bias the archive does not actually have,
over a pool that is whatever the last run left behind. KT1 is 784,309 files allocating ~31 GB, so
the extraction backing the published row was deleted to reclaim space and cannot be rebuilt: its
restore note reconstructs a *file count*, not a sample.

The corpus now arrives through `shared/corpus.EdNet`, which streams members out of the zip and takes
a documented **prefix of the namelist**. The namelist is not in id order, so a prefix is already an
arbitrary slice, and unlike a random draw over a mutable directory it is regenerable from the archive
alone.

**Two independent reads agree and the published row is the outlier.** `studies/identifiability/a7-readjudication/` sampled
6,000 learners at random from the extracted files and got 110 contradictions; this prefix read gets
115. The published row has 8,995. The median EdNet learner has 11 interactions and cannot populate
an identifying cell, which is why the re-issued numbers look the way they do.

**XES3G5M reproduced exactly** — every field identical to the published row apart from the
reachability columns — so the atlas is stable where it should be and moved only where intended.

The claim this corrects is a load-bearing one. A7 recorded EdNet as deciding 53.7% of its pairs and
supplying "roughly 200x" ASSISTments' 46 contradictions; `studies/identifiability/identifiability/` built its
positivity-versus-identifiability trade-off on the same figure. Both are corrected in place. What
survives is the direction, not the size: practice platforms where learners choose do have better
overlap than mastery tutors that gate — 5.86% against 0.22% — but nothing on disk decides more than
a small fraction of its pairs.

### Each corpus now draws its own random stream, and only one row moved

The atlas used to draw every corpus's pair sample from **one rng advanced across corpora in
`discover()` order**. So a row depended on what else happened to be on disk that day and in what
order it was found; adding a corpus silently moved every later corpus's sample, and no row could be
re-derived on its own. That is the wall `studies/identifiability/a7-readjudication/` hit trying to reproduce the EdNet row.
Each corpus now gets a stream keyed by its own name.

This is a deliberate one-time re-sample, and **what moved is itself the check**:

| | before | after |
| --- | ---: | ---: |
| every DataShop corpus | — | **identical** |
| ednet | 119 / 115 | **identical** |
| xes3g5m | 775 / 397, 5.86% decided | 736 / 393, **5.64% decided** |

Only XES3G5M moved, and it is the only corpus whose sample is a real subsample: 20,000 pairs drawn
from **747,360**. EdNet's 20,000 come from 20,022 and every DataShop corpus has fewer pairs than the
cap, so their samples are effectively complete and cannot move. A 5% relative shift in supported
edges on a 2.7% sample is sampling error, which is the answer one wants — **the rows are stable
under re-sampling, and now each is independently re-derivable.**

## 2026-09-24: Duolingo, kept out of the table above, and why that turned out not to matter

Run through `atlas.audit()` itself — same states, same MDE, same readable-and-powered gate — one
learning language at a time, at lemma grain, via `shared/corpus.Duolingo`. Source: Duolingo's own
Harvard Dataverse release of the Settles & Meeder (2016) spaced-repetition traces
(doi:10.7910/DVN/N8XJME), **CC BY-NC 4.0**, checked against its published MD5 — not the third-party
Kaggle mirror. Output: `out/atlas-duolingo.json`, deliberately **not** `atlas.json`.

**Why it is quarantined.** Every corpus above is read in the order learners *met* things. In this
release **not one of 12,854,226 rows is a first exposure**: `history_seen` is positive on every row,
because the 11.9-day window opens after every word was introduced. What is observable is review
order, chosen by a spaced-repetition scheduler, so the "identifying cell" here is learners who
failed a *review* of A and then reviewed B — a retention correlation between two words already
learned, not a test of whether A gates B. Left-censoring at 100%.

The worry was that free review scheduling would produce exactly the overlap a mastery tutor
destroys, and the rows would look more answerable than anything above. **They do not:**

| language | learners | lemmas | median reach | median identifying cell | readable | median MDE | at ceiling | decided |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| en | 43,805 | 1,373 | 252 | 1 | 11.3% | 0.509 | 83.9% | 0.01% |
| es | 31,155 | 1,729 | 69 | 0 | 6.3% | 0.500 | 84.4% | 0.00% |
| fr | 19,947 | 1,698 | 8 | 0 | 1.2% | 0.435 | 81.6% | 0.00% |
| de | 14,383 | 1,808 | 13 | 0 | 1.3% | 0.508 | 84.1% | 0.00% |
| **it** | **6,498** | **753** | **19** | **0** | **2.4%** | **0.495** | **85.9%** | **0.00%** |
| pt | 2,709 | 655 | 11 | 0 | 1.2% | 0.548 | 85.9% | 0.00% |

**One supported edge in 120,000 pairs, and zero contradictions** — English's seven were all taken
back by the powered gate.

Two things hold it there, and neither is the censoring:

- **Ceiling.** 82–86% of review sessions recall the word at 98% or better. The identifying cell
  needs learners who *failed* A, and on a scheduler built to review words just before they are
  forgotten, almost nobody does — the median identifying cell is 0 or 1 in every language, and
  `mde()` refuses a control arm pinned near 100%.
- **Sparsity.** The median learner reviews 14–20 lemmas in the window against a vocabulary of
  650–1,800, so two given words rarely share a learner — median reach is 8–19 learners outside the
  two largest languages. That is under 2% coverage, the low side of the transition
  `studies/identifiability/conjunctive-reachability/` measured across seven corpora.

So the quarantine was right for the wrong-looking reason: these rows would not have inflated the
table, but they answer a different question, and on that question too they are silent. **For the
Italian work specifically, Duolingo is not a substitute for instrumented data** — 6,498 Italian
learners decide nothing here, and `platform/italian-instrumentation/`'s randomised hold-out remains the route
that buys falsifiability by design.


## 2026-09-24: Eedi, the largest decided share on the board, and the reason not to celebrate it

Eedi NeurIPS 2020, tasks 1–2 (research use confirmed with Eedi): 19,834,813 answers from 118,971
learners on UK diagnostic maths questions, 2018–2020, read at the leaf of Eedi's own subject tree
(308 units). `data/ingest/eedi/slim.py` builds the slim file and never opens `student_metadata`.
Added with `atlas.py --only eedi --out out/atlas.json`, which replaces one row in place; the other
17 rows came back bit-identical, as the name-keyed rng promises.

| | learners | units | median identifying cell | readable | median MDE | supported | contradicted | −unfals | decided | background |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **eedi** | 118,971 | 308 | **34** | **65.6%** | **0.114** | **4,935** | 138 | 724 | **25.36%** | **+0.125** |
| xes3g5m | 18,066 | 865 | 0 | 24.3% | 0.203 | 736 | 69 | — | 4.03% | +0.087 |
| ednet | 6,000 | 142 | 32 | 81.5% | 0.229 | 119 | 9 | — | 0.64% | +0.048 |

**Six times XES3G5M's decided share, and the first corpus whose median MDE approaches the claimed
effect.** Size is the reason: 119k learners at 9.4% coverage put a median of 9,683 learners on every
pair.

**But the background drop is +0.125, above the 0.10 claimed effect** (background share 1.25; EdNet
0.48, XES3G5M 0.87). An arbitrary ordered pair on Eedi already shows a bigger drop than the gate the
assay is trying to detect, so most of those 4,935 SUPPORTED edges are indistinguishable from
general ability: a learner who passes anything passes more. A single-drop SUPPORTED verdict is
weakest exactly where it is most plentiful. What Eedi buys is not verdicts but **power for the
contrasts that subtract the background** — the within-pair direction contrast and deranged-arm
excess — which is where it should go next.

The reachability gate took back 724 of 862 would-be contradictions (84%), 723 of them readable but
underpowered.

**The prediction logged before the result held.** `studies/identifiability/conjunctive-reachability/any_corpus.py`, run
unmodified through the new adapter (the O1 demonstration on a corpus none of the code was written
for), puts Eedi at **100.0% falsifiable at cell floors 5 and 10, 99.8% at 20**, median 88 merge
nodes per pair. The coverage curve predicted 93–100% from 29/308 = 9.4% before any number was read.

**Limitation (2026-09-24): Eedi order is last-answer order.** Eedi keeps only each learner's
**latest** answer to a question (Wang et al. 2020, s2.1: "when a student has multiple answer records
to the same question, we keep the latest answer record"), at minute resolution. So first touch,
outcome at first touch, first pass and A-before-B order are all read from last answers: a question a
learner re-answered moves later and carries its re-answer outcome, which leans correct. Earlier
attempts are not in the release and nothing can restore them, so this is recorded rather than fixed
(`shared/corpus.Eedi`). Every figure in the Eedi row -- median identifying cell 34, readable 65.6%,
median MDE 0.114, 4,935 supported / 138 contradicted / 724 taken back, 25.36% decided, background
+0.125 -- rests on first-attempt semantics and should be read as a statement about last answers. The
reachability figure (100.0% at floors 5 and 10) depends on it less: it uses only the order of those
last answers and a pass decided on their mean.

## 2026-09-24: Duolingo SLAM 2018 — first exposures on the record, and still almost nothing decided

The half-life release above read review order. SLAM (Settles et al. 2018, CC BY-NC 4.0, Dataverse
guestbook) opens at every learner's first session and runs 30 days, token-scored, so learning order
is observed and the estimand matches this table. `slam_atlas.py` writes `out/atlas-slam.json`: three
courses × two grains (UD part of speech + morphology as a "construct"; the lowercased word).

| course | grain | learners | units | readable | MDE | median cell | supp | contra | −unfals | decided |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| en_es | construct | 2,593 | 204 | 25.0% | 0.323 | 0 | 19 | 0 | 106 | 0.10% |
| en_es | word | 2,593 | 2,093 | 12.7% | 0.377 | 0 | 11 | 2 | 41 | 0.07% |
| es_en | construct | 2,643 | 358 | 13.5% | 0.371 | 0 | 15 | 0 | 39 | 0.07% |
| es_en | word | 2,643 | 2,866 | 6.6% | 0.407 | 0 | 0 | 0 | 7 | 0.00% |
| fr_en | construct | 1,213 | 236 | 10.2% | 0.341 | 0 | 15 | 0 | 41 | 0.07% |
| fr_en | word | 1,213 | 2,156 | 4.2% | 0.431 | 0 | 1 | 0 | 4 | 0.01% |

**Scored against the prediction written before the run:** MDE (predicted 0.35–0.50) and decided
share (predicted under 1%) held. **Readability did not, and on the pre-stated test the prediction is
wrong on mechanism for two of three courses:** construct grain came back at 13.5% and 10.2%, under
the 20% line set in advance, with the median identifying cell 0 everywhere. Coverage of 20–35% did not
fill the failed-A cell. The likely reason is the course itself: Duolingo's skill tree fixes the
order constructions are introduced, so few learners meet B having failed A — positivity is spent by
the curriculum, as in a mastery tutor, even though coverage is high. **Coverage predicts
reachability; it does not predict positivity when the platform fixes the order**, which is a caveat
the acquisition test in data/DATASETS.md now needs.

## Correction (2026-09-24): EdNet's `-1` tag is not a KC

797 of EdNet's 13,169 questions carry only the tag `-1`, a sentinel the release never documents, and
`shared/corpus.EdNet` made it a unit `t-1`. It is now dropped as "no KC" (`shared.corpus.ednet_questions`),
so those questions contribute no events. The EdNet row was rerun with `atlas.py --only ednet`
(the committed row reproduced exactly at HEAD first): items 142 -> 141, and because 141 x 140 =
19,740 ordered pairs is under the 20,000 cap the row is now the complete pair set rather than a
sample of 20,022. Median identifying cell 32 -> 33, readable 81.5% -> 82.1%, median MDE 0.229 ->
0.230, can see a 20-point gate 36.8% -> 36.5%, supported 119 and contradicted 9 unchanged, taken
back by the reachability gate 110 -> 108, unknown 19,872 -> 19,612, decided 0.64% -> 0.65%,
background +0.048 -> +0.048 (share 0.482 -> 0.484). No verdict changes; the tables above keep the
pre-correction figures.

**ASSISTments row rerun (2026-09-25)** on the corrected extract (main problems only, partial credit
scored 0): `out/positivity-assist.json` is byte-identical. The row stands at 29,018 learners, 87
supported, 0 contradicted after the gate, 0.22% decided.

## Correction (2026-09-25): every DataShop row reads the 'All Data' sample; QA-server sets dropped

`discover()` took the first student-step file in sorted order. A DataShop download holds one file
per sample, and for ds1190 the first was '2016 data', one term's subset (161 learners); for ds1275
and ds649 it was 'All Data1', the same transactions rolled up differently. Every DataShop reader now
goes through `shared/corpus.datashop_export`, which returns the 'All Data' sample, and
`shared/check_idioms.py` refuses any other way of picking an export.

Rerun, all eleven public DataShop rows: only ds1190 moves, to 431 learners, 39 KCs under the same
`KC (Default)`, 10.3% readable, 2 SUPPORTED and 0.13% decided (was 13.3% and 0.24%). ds1275 and
ds649 reproduce exactly. The highest-deciding mastery tutor is now ASSISTments at 0.22%.

ds827, ds839 and ds941 were downloaded from DataShop's QA server (their TERMS.html points at
qa.datashop.org), whose ids name different production datasets. They are not public, each had too
few learners to read (14, 15 and 0), and no result rested on them. `discover()` now skips QA
exports and their rows are removed from `out/atlas.json`.
