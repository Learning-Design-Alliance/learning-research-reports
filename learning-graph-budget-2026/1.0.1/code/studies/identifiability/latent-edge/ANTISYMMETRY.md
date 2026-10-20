# Is the pairwise structure directional, or only relatedness?

**Verdict: `BOTH` — and I predicted `RELATEDNESS ONLY`. I was wrong.**

| corpus | pairs | symmetric | null | **antisymmetric** | null |
| --- | ---: | ---: | ---: | ---: | ---: |
| **XES3G5M** | 8,892 | **+0.295** | −0.006 | **+0.266** | −0.000 |
| EdNet | 8,928 | +0.072 | +0.006 | +0.020 | −0.003 |

After the additive margins **and** the leading multiplicative one are removed, XES3G5M's residual
holds antisymmetric structure replicating across independent learner halves at **+0.266 against a
null of −0.000**. The symmetric and antisymmetric parts are **comparable in magnitude** (+0.295 vs
+0.266). This is not "mostly relatedness with a trace of order".

## Why I expected otherwise, and what survives

`studies/identifiability/taxonomy-order/` found XES3G5M's expert hierarchy inert for ordering (ancestor − descendant =
−0.0128) while carrying magnitude. `studies/producers/direction-benchmark/` found a text proposer recovers generality,
not prerequisite. I read both as predicting the residual would be symmetric. They do not conflict
with this result — they are about **the expert taxonomy** and **a text model**, and this is about
**learner trajectories**. The honest synthesis: *there is directional structure in the data that
neither the authored hierarchy nor a language model recovers.*

## The finding this sharpens

`lowrank.py`'s floor established that a prerequisite acting as a pure skill difference,
`A[i,j] = sᵢ − sⱼ`, **is** an additive margin `aᵢ + bⱼ` and is removed before the decomposition sees
it. So whatever survives here **cannot be a total ranking**. It is order with genuinely incomparable
pairs — branching structure, not a difficulty ladder.

That is the first direct evidence in this programme for a partial order in learner data that is not
reducible to difficulty.

## What the floor proves, and one diagnostic that came back uninformative

Floor (30 reps, 60 items): planted DAG recovers at **anti +0.822** vs null +0.002 with symmetric
−0.002; planted relatedness recovers at **sym +0.376** and leaks **anti −0.004**; the empty world
reads +0.016. So the arms separate and relatedness does not manufacture antisymmetry.

**The energy share is uninformative and should not be quoted.** Both corpora report ~49% of residual
energy in the antisymmetric part — but the *no-structure* floor arm also reports 0.50, because a
random matrix splits its energy evenly between the two components. The run log prints this number;
it carries no information and only the replication correlations do.

## Caveats

- **EdNet is weak** — anti +0.020 against a null of −0.003. Technically `BOTH`, practically almost
  nothing, consistent with everything else: EdNet reads more edges and holds less structure.
- **Directional ≠ prerequisite.** Antisymmetry says A affects B more than B affects A. Reciprocal
  teaching order, curricular sequencing and exposure asymmetry all live here too.
- One instrument, two corpora, 8 splits. It wants replication on a third corpus.

```
python3 antisymmetry.py --floor-only
python3 antisymmetry.py --splits 8
```
