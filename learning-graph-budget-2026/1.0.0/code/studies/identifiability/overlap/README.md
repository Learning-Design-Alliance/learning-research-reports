# Positivity: can the dataset answer the question at all?

Every structural null this programme has reported rests on an assumption nobody tested: that the
data contains learners who attempted the dependant **without** holding the prerequisite. A gate is a
claim about what happens in that cell. A mastery-learning tutor exists to keep the cell empty.

So the null and the tutor's success are the same observation, and we have been reporting one as
evidence about the other.

This is a **positivity (overlap) violation**. No estimator repairs it — there is nothing to
estimate — which is why it belongs before the model as a gate, not after it as a caveat.

## What is measured

For each candidate edge `A -> B`, the learners who reached B, split by what they held in A at the
moment of their first B attempt:

| cell | meaning |
| --- | --- |
| `MASTERED` | at least one correct A attempt beforehand — the control |
| `FAILED` | A attempted beforehand, never once correct — **the identifying cell** |
| `NEVER` | no A attempt at all — an order violation, but silent about whether they hold A |

From the two cell sizes, the **minimum detectable effect**: the smallest drop in B success an
80%-powered two-proportion test could see. An edge whose MDE exceeds any effect anyone claims is
unanswerable in that dataset, whatever a model reports about it.

A fourth cell recovers some of `NEVER`. Most of those learners meet A later, and skills are acquired
rather than lost — the monotone-accumulation assumption the cancer-progression and phylogenetic
literatures both run on — so a learner whose *later* first attempt at A fails almost certainly did
not hold A when they reached B. Weaker than watching someone fail A and be sent onward, and
confounded by ability on both sides, so it is reported separately and never pooled.

## Result

| | Junyi (authored edges) | ds1190 (all pairs) | ASSISTments (40k sampled pairs) |
| --- | --- | --- | --- |
| edges with any learner at B | 775 | 1,482 | 40,000 |
| median learners reaching B | 12 | 80 | 405 |
| **median in the identifying cell** | **0** | **0** | **0** |
| median reaching B with no A at all | 5 | 75 | 380 |
| both cells clear 5 learners | 2 (0.3%) | 205 (13.8%) | 9,495 (23.7%) |
| median MDE, readable edges | 0.463 | 0.344 | 0.296 |
| **edges able to detect a 10-point drop** | **0** | 18 (1.2%) | 158 (0.4%) |
| edges able to detect a 20-point drop | 0 | 42 (2.8%) | 2,103 (5.3%) |
| retrospective cell readable | 12 (1.5%) | 285 (19.2%) | 12,564 (31.4%) |
| retrospective median MDE | 0.565 | 0.273 | 0.248 |

**The median identifying cell is empty in all three datasets.**

On Junyi, 2 of 775 authored prerequisite edges have enough learners on both sides to read at all,
and **not one** could detect a twenty-point drop in success. Junyi is the dataset this programme's
edge-recovery work was built on. Its nulls are not findings about Junyi's graph; they are the
absence of a measurement.

**Correction (2026-09-24): ds1275 read once, authored edges deduplicated.** The Junyi column came
from `build_matrix.py`'s loader, which globbed both DataShop samples on disk ('All Data' and
'All Data1', the same 359,804 transactions rolled up two ways) and so read every event twice; it
now reads one sample through `shared.corpus.ds1275_export`. The authored-edge list also held the
exercise table's duplicate rows (988 entries, 981 edges); it now comes from `shared/junyi_graph.py`.
Rerun: 775 edges, median identifying cell 0, 2 readable, median MDE 0.463, 0 able to see a 10- or
20-point drop, all 775 UNKNOWN -- unchanged. Only the retrospective observed drop moved, median
+0.004 -> -0.007. The retrospective rows in the table above (12, 1.5%, MDE 0.565) were already stale
before this fix: they come from an older `out/positivity-junyi.json` that the committed code did not
reproduce (it gives 10, 1.3%, 0.548, as `out/positivity-junyi-states.json` recorded); both files now
hold the corrected run. No verdict changed.

ASSISTments is the best of the three and still only 5.3% of its pairs could see a twenty-point gate.
The typical readable edge can resolve a ~30-point drop — far larger than any effect the field
reports.

## What this changes

1. **Retro-actively.** Every "structure adds nothing" result in this programme was computed on data
   where the identifying cell was empty. They remain true statements about *prediction*; they are
   not evidence about gates. Where a null was read as "the gate is not there", it should be read as
   "the dataset cannot say".
2. **Prospectively.** `positivity.py` runs before any fit. A dataset whose MDE exceeds the effect
   being chased is reported as unanswerable rather than null. This pairs with
   `studies/identifiability/latent-shape/power.py`: power says what the *estimator* can resolve at a given size, positivity
   says whether the *data* contains the contrast at all. Both have to pass.
3. **On dataset choice.** "High-quality ITS data" selects precisely for the censoring. The inclusion
   criterion should be inverted: prefer domains where a real dependency exists but instruction does
   not enforce it, and measure the identifying cell before committing to a corpus.

The observed drops are reported unadjusted and are **not** causal: learners who failed A differ from
those who passed it in every other way too. They are printed only to show the size of the thing the
cell counts say we could or could not have seen.

## Reproduce

```
python3 positivity.py ds1190 --pairs all      --out out/positivity-ds1190.json
python3 positivity.py junyi  --pairs authored --out out/positivity-junyi.json
python3 positivity.py assist --pairs all      --out out/positivity-assist.json
python3 random_order.py                              # out/random_order.json
python3 figure_atlas.py                              # Paper II Figure 1 (no corpus)
```

`figure_atlas.py` draws the atlas's rules as Paper II's Figure 1. It reads them from
`shared/edge_state.py`, `positivity.py` and `shared/reachability.py`, and it stops if
`classify_edge` disagrees with any branch of the drawn decision flow, or if the article's Section 4.2
prints a rule differently.

`random_order.py` is the check that ASSISTments 2012-13's random-order sections do not randomise
skill order: 3,838 co-seen skill pairs, largest minority arm 15 (`data/DATASETS.md`). Corpus paths
come from each corpus's environment variable in `data/data-sources.json` (`shared/paths.data_path`).

Raw DataShop and ASSISTments exports stay outside the repo under their redistribution terms; only
the aggregate JSON here is committed.
