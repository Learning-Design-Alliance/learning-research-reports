# A5 at course grain: the number clears the gate, and the gate does not mean what it meant

`TAIL.md` closed two of A5's three explanations. The corpus explanation went when XES3G5M and EdNet
were both measured; the sparsity explanation went when the asserted tail came back **less** reliable
than the bulk (+0.654 against +0.743). The one route left was A5's own `moves_next`: **aggregate the
unit.** `studies/identifiability/coarse-grain/register_order.py` showed course grain carries cells three orders of magnitude
deeper than KC grain, and bigger cells mean less sampling noise.

**That route has now been walked, and it is not where the gain comes from.**

## The estimand changes, and nothing makes it not change

At KC grain the edge statistic is a **drop** — does holding A raise success at B. MOOCCubeX has no
usable outcomes at course grain: streaming its 21 GB user-problem log kept **33,856 records from
133,384,333 rows**, because the problem-to-course map covers only 10,509 problems. So what is
measurable here is **order, not performance**:

    asym(A, B) = share of learners enrolled in BOTH who enrolled in A first

That is an edge statistic and it does rank edges, so A5's question is askable of it. But it is not
the same question.

## Result

541,452 learners across the 60 most-enrolled courses, 1,770 unordered pairs, all readable at a floor
of 30 co-enrollers. Median cell **1,494** learners (p10 568, max 32,922) against KC grain's hundreds.

| | Spearman | **Spearman-Brown** |
| --- | ---: | ---: |
| raw | +0.985 | **+0.992** |
| open-date residual | +0.984 | **+0.992** |

**It is not the catalogue.** `register_order.py` flagged that order asymmetry carries a
course-availability confound — if A was published before B, everyone takes A first whatever the
relation — and a release schedule is stable, so a statistic driven by it would be almost perfectly
reliable and entirely invalid. Regressing the asymmetry on the sign and size of each pair's open-date
gap, **the schedule explains R² = 0.001**, and reliability on the residual is unchanged at +0.992.
The confound the study was built to catch is simply not there.

**The asserted tail replicates well too.** Of 770 pairs selected as ordered in a held-out third
(|2p−1| ≥ 0.30), **91.6%** still clear the bar out of sample against a base rate of 42.9% — a 2.14×
lift, against KC grain's 1.40×.

## But the cell ladder says it is not A5's route

A reliability coefficient is a **variance ratio** — true variance over true plus error — so it rises
when the error shrinks *and* when the true spread grows. Those are different claims and only the
first is A5's. The same measurement on learner subsamples:

| learners | median cell | pairs | Spearman-Brown |
| ---: | ---: | ---: | ---: |
| 5,414 | **40** | 55 | **+0.943** |
| 16,243 | 61 | 549 | +0.924 |
| 54,145 | 154 | 1,554 | +0.950 |
| 178,679 | 495 | 1,747 | +0.979 |
| 541,452 | 1,494 | 1,768 | +0.992 |

**At a KC-grain cell depth of 40, this statistic already reads +0.943.** Aggregation buys the last
0.05; the estimand buys everything from KC grain's +0.654 to +0.943. An order share spreads across
the whole [0,1] interval where a KC drop has a standard deviation of 0.07 — more true variance, same
error, higher coefficient, no better instrument.

## The proposed replacement was tested here, and it discriminates

`A5`'s `moves_next` proposes replacing the rank correlation with **chance-corrected agreement
(Cohen's kappa) on the assertion decision** — assert this edge or not — on the grounds that a
correlation rewards spread *anywhere* in the range, including far above the bar where it changes no
decision, while the assay's output is a decision. The decisive test is cheap: run it on the very
statistic that gamed the old gate.

| median cell | Spearman-Brown | **decision kappa** |
| ---: | ---: | ---: |
| 40 | +0.943 | **+0.524** |
| 61 | +0.924 | **+0.437** |
| 154 | +0.950 | **+0.576** |
| 495 | +0.979 | **+0.738** |
| 1,494 | +0.992 | **+0.859** |

**This is what a portable metric looks like next to one that is not.** Across a 37× change in cell
depth the correlation moves 0.943 → 0.992 — it is nearly flat, because it is reporting the estimand's
spread and not the instrument's precision. Kappa moves 0.524 → 0.859, tracking precision the way A5's
gate was always supposed to. At a KC-grain cell depth of 40 the order statistic reads **+0.943 by
correlation and +0.524 by kappa**: under a kappa gate it does not walk through on spread.

**Two caveats.** The ladder is not monotone (+0.437 at cell 61 against +0.524 at cell 40) — the first
rung has only 55 readable pairs and that is sampling noise, not a reversal. And kappa depends on the
assertion bar (0.30 here) and on the base rate it corrects against, so **a 0.80 kappa threshold would
be a new constant and would need calibrating rather than inheriting**, which is precisely the mistake
this file exists to document.

## Verdict: `RELIABLE AND NOT THE CATALOGUE` — and A5 stays unmet

A5's `met_when` reads "split-half reliability of the edge ranking is 0.80 or better", and +0.992
clears it on the letter. **Marking A5 met on this would be the exact mistake this repository spent
the day correcting**: applying a constant where it does not mean the same thing. A reliability gate
is a variance ratio, so it is **not portable across estimands**, and 0.80 was set for a drop.

**This is a judgement, and it is the conservative one.** The criterion needs re-specifying to name
the estimand it gates before any number can meet it.

## The through-line

Three constants were found non-portable in one day, all the same defect class:

| constant | not portable across | where |
| --- | --- | --- |
| the **+0.10** assertion bar | corpora | `studies/identifiability/conjunctive/BAR.md` |
| the **0.05** decision rule | null structures | `board/VERDICT-AUDIT.md` |
| the **0.80** reliability gate | **estimands** | here |

Each was defined once, in one setting, and then carried somewhere it silently meant something else.
`VERDICT-AUDIT.md` counted up to 41 of 75 verdicts in this programme decided against a constant. This
is what that risk looks like when it lands.

```
python3 course_grain.py --top 60 --splits 12
```

Reads MOOCCubeX enrolment order. **Privacy:** the ingest discarded `name`, `gender`,
`year_of_birth` and `school` at the door; only pseudonymous id, course sequence and enrolment times
were ever kept. Raw exports stay in the session scratchpad; only aggregates are committed.

---

# Audit: the +0.859 is the catalogue. 93% of it survives crossing learners.

`course_order_derangement.py`. This criterion's text already declined to count the course-grain
reading because it is measured on a different estimand from A5's gate. That refusal turns out to
have been generous.

## Why the audit was run

`estimand_kappa.py` put both estimands on XES3G5M at KC grain — same pairs, same learners, same
splits, compared at matched assert rates — and found the order statistic reaching kappa **+0.98**
while scoring **+0.97 on deranged data**, where every learner's parent state has been crossed onto
another learner's dependant outcome. At KC grain the order statistic is almost pure presentation
order.

That did not transfer automatically. XES3G5M's KC order is set by a curriculum; MOOCCubeX
enrolment is **chosen by the learner** — `register_order.py` established free enrolment and
course-grain positivity holds on 3,532 of 3,540 pairs. So the control was run here rather than the
conclusion carried across.

## The derangement

For a pair (A, B) the real statistic asks, of learners enrolled in both, what share met A first.
The deranged statistic compares a **donor's** enrolment time for A against the learner's **own**
time for B, under a derangement with no fixed points.

- **It destroys** within-learner sequencing — the thing "learners take A before B" asserts.
- **It preserves** every course's own enrolment-time distribution *exactly*, because a derangement
  permutes a column rather than altering it.

## Result

Floor first: the real arm reproduces the published reading to three decimals.

| | real | deranged | excess |
| --- | ---: | ---: | ---: |
| Spearman-Brown | **+0.992** (published +0.992) | **+0.982** | **+0.010** |
| decision kappa | **+0.857** (published +0.859) | **+0.800** | **+0.057** |

541,452 learners, 60 courses, 1,768 pairs per split, median cell 748.

## Verdict: `EXPOSURE`

**Crossing learners costs the statistic 0.057 of kappa out of 0.857.** Roughly 93% of the agreement
is about *when each course is generally taken* — when it opened, when it is popular, where it sits
in a programme — and not about any order the learners impose.

The open-date regression that cleared this result (R² = 0.001) ruled out **one** exposure channel,
the release schedule. The general channel went unmeasured, and it is almost the whole thing.

**The course-grain route to A5 is shut, for the same reason the KC-grain order estimand is: both
are reading the catalogue.** Two different corpora, two different grains, one mechanism.

For C3, where sample scales as 1/kappa²: quoting the raw +0.857 rather than the
structure-attributable +0.057 **understates the required sample by 227×**.

## What this costs and what it leaves

It removes the cheapest imaginable route to raising kappa — claim something weaker and get
reliability for free. That route is now closed on measurement, not opinion. What survives is the
drop at KC grain, whose own deranged floor is **+0.099** against a real **+0.480**: about +0.38 of
structure-attributable agreement, which is a far worse headline number and the only honest one.
