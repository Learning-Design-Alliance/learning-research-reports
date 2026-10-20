# Junyi: expert judgement, an authored map, and learner behaviour, on one set of exercises

The programme's central question needs three things at once, and until now nothing had them: an
authored prerequisite graph, expert ratings of individual pairs with every rater's raw score, and
learner data whose order was not dictated by a scheduler. Junyi Academy has all three.

| | |
|---|---|
| `junyi_Exercise_table.csv` | 837 exercises, **981 authored prerequisite edges** (the knowledge map) |
| `relationship_annotation_*.csv` | **1,954 rows** (1,638 unordered pairs) rated 1–9 for prerequisite strength, 3–15 raters each, every rater's score kept. Row (A, B) rates **B as a prerequisite of A** (Chang, Hsu & Chen, EDM 2015); read through `shared/junyi_ratings.py` |
| DataShop ds1275 | **2,063 learners** over 631 of those exercises, learner-chosen order |

Source: base.ustc.edu.cn/data/tests/junyi. Acknowledgement: Koedinger et al. (2010), datashop.org.

## 1. Individual experts agree moderately; a panel of them agrees well

Splitting each pair's raters in half and correlating the halves:

| | |
|---|---:|
| split-half correlation (two ~4.6-rater panels) | **+0.783** |
| **single-rater reliability** (Spearman-Brown inverted) | **+0.441** |
| full-panel reliability (9–15 raters; older split-half estimate, superseded by `studies/measurement/expert-agreement/`: ICC(1,k) 0.857 at an effective ~7 raters, k₀ 6.90, over 1,954 pairs rated by 3–15 people) | **+0.879** |

The middle figure is the one comparable to our own corpora, which put expert agreement on graph
structure at **κ ≈ 0.31**. At 0.441 on 1,954 pairs this is an **independent replication at roughly ten
times the scale**, in a different domain, by a different research group, using a different
instrument. Individual expert judgement about prerequisites is only moderately reliable, and that is
now a robust finding rather than a quirk of our corpora.

The panel figure is the other half of the same story. **Pooling nine to fifteen raters takes
reliability from 0.44 to 0.88.** This is the strongest evidence yet for the programme's advice to pool
authors rather than push them toward consensus — the disagreement is signal-bearing noise, and
averaging it away is what makes the measurement good.

## 2. The raters clearly endorse the published knowledge map

Prerequisite ratings for rows whose rated direction the knowledge map asserts, against rows it does
not:

| | mean | sd | n |
|---|---:|---:|---:|
| edges the map asserts, rated in their direction | 6.12 | 1.92 | 387 |
| rows it does not assert | 4.21 | 2.02 | 1,567 |

**Cohen's d = 0.96** (pooled sd). A large effect: two *human* sources on the same 1,954 rows, with no
learners involved, agree substantially about what a prerequisite is. The 265 rows that rate an
authored edge backwards score 5.17 — between the two — so the raters also track which way the edge
runs. Measured against another panel the map is still imperfect (AUC 0.752 against a panel
split-half of 0.891, `studies/measurement/expert-agreement/`), but it is not a lightly endorsed
object.

## 3. Expert rating tracks the order effect in learner data — positively, and the test is weak

For each rated edge P -> D, learners who met the prerequisite P first were compared against those who
met D first, on first-attempt accuracy at D, adjusted for each learner's overall accuracy:

    Spearman(expert prerequisite rating, prereq-first advantage) = +0.299   95% CI [-0.017, +0.571]
    n = 47 pairs with >=15 learners in each order

    mean prereq-first advantage, all pairs            +0.0382
    mean prereq-first advantage, top-quartile ratings  +0.1059

**Positive, in the pre-registered H1 direction, with an interval that just touches zero.** Only 47
of 1,954 rated rows had enough learners in both orders, because the pairs were selected for
annotation rather than for coverage. The top-rated quartile shows nearly three times the mean
advantage. This is suggestive evidence that expert judgement tracks something in behaviour, not a
demonstration.

**And it is observational.** Learners chose their own order, so someone who takes P before D may
differ from someone who does the reverse in ways that also affect performance at D. Adjusting for
overall accuracy removes the crude version of that confound and not the subtle one.

## What this changes

- **Pool authors; do not seek consensus.** Now replicated independently at scale. Four to five raters
  is not a nicety — it is what takes an unreliable judgement to a reliable one.
- **Do not treat a published map as ground truth**, including the Coherence Map and including ours.
  Expert raters endorse Junyi's asserted edges strongly (d 0.96), but the map still sits well below
  a second panel's agreement.
- **The link from expert judgement to learner behaviour is suggested, not established.** rho +0.299
  on 47 pairs, interval touching zero: the thesis question leans positive and remains open.

## Correction (2026-09-24): rating direction

Sections 2 and 3 read each rated row (Exercise_A, Exercise_B) as A -> B. Chang, Hsu & Chen (EDM 2015)
asked "after students learned to correctly answer exercise B, how appropriate is utilizing exercise
A to deepen the students' knowledge", so the row rates **B -> A**; on the 231 authored pairs rated
both ways the correctly oriented row scores 1.09 points higher. Section 2 compared ratings on the
*reverse* of the authored arrows: 5.17 vs 4.50 (n 265, d 0.35 as reported, 0.32 pooled) is **6.12 vs
4.21 (n 387, d 0.96)**, and the verdict flips from "only weakly endorsed" to "clearly endorsed".
Section 3 measured the order effect for the wrong prerequisite: rho −0.059 [−0.382, +0.267] n 50 is
**+0.299 [−0.017, +0.571] n 47**, from a null to a positive, still-inconclusive result. Section 1 is
orientation-free and unchanged. The other analyses below carried the same error; each has its own
correction note.

---

## Other analyses on this dataset

Sections 1–3 above come from `expert_vs_data.py`. The authored map and the ds1275 logs support four
further analyses, each with its own write-up:

| | |
|---|---|
| [`HOP-DECAY.md`](HOP-DECAY.md) | how far a prerequisite's effect carries — and why weighting the edges reverses the answer (`hop_decay.py`, `weighted_paths.py`) |
| [`GATING-GRAIN.md`](GATING-GRAIN.md) | what a coarse prerequisite overcharges: 18.5× at topic grain, 69.8× at area grain, 0 of 96 needing the whole group (`gating_grain.py`) |
| [`GATE-OR-WEIGHT.md`](GATE-OR-WEIGHT.md) | whether prerequisites gate or merely load — 80% of testable edges beat a permutation null for a threshold over a slope (`gate_or_weight.py`) |
| [`CURRICULAR-COMPLEXITY.md`](CURRICULAR-COMPLEXITY.md) | blocking factor crossed with overcharge: 86% of blocking unwarranted, and 13 topic pairs that require each other (`curricular_complexity.py`) |

**Reversed-arrow control (2026-09-24), every edge flipped:** authored-vs-rated d 0.96 vs 0.32; rating-vs-learner-order rho +0.299 vs −0.059; gate-or-weight median excess +0.195 vs +0.065 and rho(excess, rating) +0.432 vs +0.151; hop-decay direct-edge signal +2.59 vs +1.63; weighted-paths rho +0.799 (n 356) vs +0.333 (n 16) — all CLAIMED, all original figures reproduced.
