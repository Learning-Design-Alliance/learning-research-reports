# Stage 3: is there conjunctive structure in XES3G5M?

**Verdict: `CONJUNCTIVE STRUCTURE`.** 11,203 triples scored, top 30 items, cell floor 20, FDR q=0.05.

`chunking.py` found the interaction near zero in both expertise strata and could not say whether
conjunctive structure was *absent* or merely *unmeasured* — it nulled the gap between strata, not the
interaction level. This supplies the three things it was missing.

## 1. The null on the interaction itself, validated

Under independence the interaction has variance `p(1−p)·Σ(1/nᵢ)`. That analytic null is used for all
triples and **checked against an explicit learner-deranged null** on 150 of them:

> explicit deranged SD / analytic SE = **0.997**; deranged null mean interaction **−0.00032**.

The analytic form is right. Had it disagreed the run was pre-registered to stop rather than report
corrected p-values built on it.

## 2. Power at the *real* cell sizes

Planting into idealised data would report power we don't have, so the observed (n₁,n₂,n₃,n₄) of each
real triple is kept and only the **outcomes** are simulated:

| planted conjunction | detectable |
| --- | ---: |
| +0.10 | **79.2%** |
| +0.20 | 94.0% |
| +0.40 | 99.8% |

Median MDE **+0.0612**, median smallest cell **658**. This corrects an expectation I set from
Stage 2's examples — the `neither` cell there ran 20–29, but that census used all 40 items at floor 5;
restricting to the top 30 at floor 20 leaves genuinely powered triples. **We are powered to see a
conjunction at the pre-registered bar.**

## 3. Multiple-comparison correction, and magnitude reported beside significance

| verdict | count | share |
| --- | ---: | ---: |
| **SUPPORTED** | 2,425 | 21.6% |
| **CONTRADICTED** | 7,706 | 68.8% |
| UNKNOWN | 1,072 | 9.6% |

At FDR q=0.05 about **121** of the 2,425 SUPPORTED are expected false. And the effects are not
trivial:

> SUPPORTED interaction: median **+0.1000**, p90 **+0.1934**, max **+0.4710**.
> **SUPPORTED *and* ≥ the pre-registered +0.10 bar: 1,212 triples (10.8% of all scored).**

For scale, Stage 1's *planted* conjunctions read +0.19 to +0.40. The top of this distribution is in
that range.

## What this changes

`chunking.py`'s incidental reading — "the interaction is flat" — was **an artefact of aggregation**.
The median across all triples is +0.00092, which is what that study saw. But the distribution is not
centred noise: **one triple in ten carries a conjunction at or above the background drop**, and
68.8% can rule one out. The structure is real, sparse, and concentrated.

That also settles Stage 1's question in the affirmative direction: our pairwise instruments are blind
to conjunctions, conjunctions exist here at detectable size, so **some fraction of this programme's
accumulated pairwise nulls are conjunctions we could not see.**

## Caveats

- **Directional, not causal.** A large positive interaction says the two parents' effects are
  super-additive. Co-teaching, shared item format and curricular bundling all produce that.
- **Top 30 items only** — the best-trafficked KCs, which is where the power is and also where
  curricular bundling is strongest.
- **SUPPORTED includes 1,213 triples below the +0.10 bar**: statistically real, smaller than the
  background an arbitrary ordered pair already shows. Significant is not the same as worth asserting.
- Two bugs were fixed before this was reportable: the saved rows were the *first* 400 rather than a
  random sample (and `scored` is ordered by item coverage, so that slice over-represented
  well-powered triples), and the verdict was decided on significance alone with no magnitude term.

```
python3 stage3_interaction.py --items 30
```
