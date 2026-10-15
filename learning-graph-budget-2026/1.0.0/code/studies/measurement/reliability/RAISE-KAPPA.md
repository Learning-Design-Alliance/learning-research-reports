# How to raise decision kappa: four levers, and the one that turned out to be a mirage

`raise_kappa.py`. `studies/outcomes/ope/c3_readiness.py` made A5 the binding constraint on the north star, so
"raise kappa" became the highest-value work on the board.

**This run re-baselines on the adopted rule.** LCB at z = 1.0 is no longer a candidate lever, it is
the BASELINE, and every other lever is composed with that margin. So the question is not "what beats
a plain bar" — the programme no longer uses a plain bar — but **"what ADDS to the rule we have."**

Corpus: XES3G5M, 18,066 learners, **90 items, 8,010 ordered pairs, cell floor 10, 8 splits**,
6,978 common pairs per split.

> An earlier pass ran at 60 items / 3,540 pairs / 6 splits and is **superseded**. Its numbers are not
> comparable to these and should not be quoted.

## The scoring rule, which is the point

The deranged baseline is **not zero** — it is **+0.008** here. Crossing one learner's parent state
onto another's dependant outcome destroys learner-level dependency but leaves **item-level** structure
standing: cell composition still tracks parent difficulty, the dependant's outcome still tracks
dependant difficulty, and both halves see that and agree about it.

**So every lever is scored on its EXCESS over its own deranged value, not on raw kappa.** A lever that
lifts both arms together has bought nothing, and raw kappa cannot tell the difference.

Floor check: the baseline rule reproduces `tail.py` (+0.494 here against +0.422 there). The gap is
expected — this script splits learners in HALF where `tail.py` splits in THIRDS, so there are more
learners per half. That difference is itself the sample-size lever, quantified at the bottom.

## Results

| lever | raw κ | deranged | **excess** | vs base | coverage | assert | verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **baseline — LCB z=1.0** | +0.494 | +0.008 | **+0.486** | — | 100% | 35% | |
| LCB z=0.25 | +0.486 | +0.081 | +0.404 | −0.082 | 100% | 51% | no gain |
| LCB z=0.5 | +0.491 | +0.068 | +0.423 | −0.064 | 100% | 45% | no gain |
| LCB z=1.5 | +0.506 | −0.001 | +0.507 | +0.021 | 100% | 25% | no gain |
| LCB z=2.0 | +0.512 | −0.000 | +0.513 | +0.026 | 100% | 18% | **DEGENERATE** |
| shrink 0.5 → 4.0 | +0.543 → +0.614 | *undefined* | — | — | 100% | 29% → 19% | **DEGENERATE** |
| abstain z=0.25 | +0.588 | **+0.092** | +0.497 | +0.010 | 80% | 51% | **MANUFACTURED** |
| abstain z=0.5 | +0.694 | +0.088 | +0.606 | +0.120 | **64%** | 45% | REAL |
| abstain z=1.0 | +0.872 | +0.012 | +0.860 | +0.374 | **41%** | 35% | thin coverage |
| abstain z=1.5 | +0.966 | −0.000 | +0.966 | +0.480 | **27%** | 25% | **DEGENERATE** |
| bar 0.05 | +0.472 | +0.049 | +0.423 | −0.063 | 100% | 65% | no gain |
| bar 0.15 | +0.441 | −0.000 | +0.441 | −0.045 | 100% | 13% | no gain |
| bar 0.20 | +0.335 | −0.000 | +0.335 | −0.151 | 100% | 4% | **DEGENERATE** |
| bar 0.25 | +0.193 | −0.000 | +0.193 | −0.293 | 100% | 1% | **DEGENERATE** |

**Loosening the margin below z = 1.0 re-admits the exposure it was adopted to remove.** At z = 0.25
and z = 0.5 the *deranged* arm climbs to +0.081 and +0.068 — agreement about item difficulty, on data
with no learner-level dependency left in it. Raw kappa barely moves (+0.486, +0.491), so on raw kappa
these look harmless. On excess they are the two worst LCB settings on the board. **z = 1.0 is a knee,
not a preference.**

**Tightening past it buys precision by asserting almost nothing.** z = 1.5 and 2.0 raise excess, but
the assert rate falls to 25% and 18%, and on the deranged arm nothing clears `bar + z·se`, so every
decision collapses to the same value and kappa there is undefined rather than zero.

**Shrinkage failed exactly as predicted.** It is the only lever that raises raw kappa monotonically —
+0.543 to +0.614 — and its deranged arm is *undefined* at every setting. When between-pair variance
net of measurement error collapses, every pair shrinks to the same mean and every decision becomes
identical. Kappa there is not perfect, it is meaningless. **Scored on raw kappa without a deranged
arm, shrinkage would have looked like the answer.**

**The bar is also already at its knee.** Every move away from 0.10 loses excess, in both directions.

## Abstention does not survive contact with what a policy is for

1/κ² prices the sample needed to *detect* a gain; it says nothing about how many edges the policy
still acts on. **A policy that abstains on 36% of edges does not act on them** — it falls back to
difficulty ordering and earns zero incremental value there. The comparable quantity is the
**effective edge**, coverage × excess:

| lever | excess | coverage | **effective** | C3 sample |
| --- | ---: | ---: | ---: | ---: |
| LCB z=2.0 | +0.513 | 100% | +0.512 | 0.90× *(DEGENERATE)* |
| LCB z=1.5 | +0.507 | 100% | +0.507 | 0.92× *(no gain)* |
| **baseline — LCB z=1.0** | +0.486 | 100% | **+0.486** | **1.00×** |
| bar 0.15 | +0.441 | 100% | +0.441 | 1.21× |
| abstain z=0.25 | +0.497 | 80% | +0.397 | 1.50× *(MANUFACTURED)* |
| **abstain z=0.5** | +0.606 | 64% | +0.388 | **1.57×** |
| abstain z=1.0 | +0.860 | 41% | +0.350 | 1.93× |
| abstain z=1.5 | +0.966 | 27% | +0.258 | 3.56× |

**Abstention at z = 0.5 is the only lever scored REAL, and it is near the bottom of this table.** It
would cost **57% more learners**, because it raises kappa by removing exactly the cases the policy
most needs to decide. Every further abstention setting is worse than the last.

**One caveat this metric does not capture.** LCB z=1.5 and z=2.0 top the ranking, and both are
disqualified elsewhere. **Coverage counts DECISIONS, not ASSERTIONS** — at z = 2.0 the rule decides
every edge while asserting only 18%, so its effective edge overstates what the policy delivers. The
`DEGENERATE` flag is what catches that; the ranking alone would not. Any future use of effective edge
must be read beside the assert rate.

Abstention is not dismissed on arithmetic alone, because the linear model assumes a wrong decision
merely fails to help. If a wrong decision actively *harms*, declining has insurance value. Whether
sequencing errors are that costly is a domain question this programme has not measured.

## The sample is a ceiling, and it has not been reached

| learners per half | 1,354 | 2,709 | 4,516 | 6,774 | 9,033 |
| --- | ---: | ---: | ---: | ---: | ---: |
| kappa | +0.177 | +0.302 | +0.395 | +0.456 | +0.500 |

**+0.323 across a 7× change, still climbing at 100% of XES3G5M.** More learners help. EdNet has
60,308 unused.

## Verdict

**Keep LCB at z = 1.0. Do not adopt abstention. Do not move the bar. Then get more learners.**

The decision rule is not what is holding kappa down. Every rule that raises structure-attributable
agreement does it by declining edges, and it declines more value than the extra precision returns.

## A bug in this file's own scoring, recorded because it nearly went unnoticed

The effective-edge ranking was added to `raise_kappa.py` after an earlier reading of this study
recommended abstention off 1/κ² alone. The first version of that patch read `results["baseline"]["excess"]`
— but **the baseline row stores no `excess` of its own**; its excess is `kappa − deranged`, held
separately. The lookup returned NaN, which printed `+nan` for the baseline, turned every "C3 sample"
cell into `nanx`, and forced the no-lever-wins branch *regardless of the numbers*. The verdict it
printed was correct by accident. Fixed, with an assertion that the baseline's effective edge is
finite, so the comparison can never again be made against NaN.

---

# Finishing the study (2026-10-05)

Pre-registered in the FINISHING section of `raise_kappa.py`'s docstring (commit `c472cc2` on branch
`study/structure-ii-tests`) before either new mode ran. Code: `raise_kappa_finish.py`, through
`pairgrid.py` (the matrix form of `positivity.classify`, asserted equal to it on 200 pairs per corpus).

## 1. The registered reject rule, applied (`--rescore`, `out/raise_kappa_rescored.json`)

The docstring fixed in advance that a lever whose deranged kappa exceeds 0.05 is MANUFACTURING
AGREEMENT. `MAX_DERANGED` was defined and never read; the run used a relative rule instead. Re-read
under the registered rule, with nothing recomputed:

| lever | deranged | as run | registered |
| --- | ---: | --- | --- |
| LCB z = 0.25 | +0.081 | no gain | MANUFACTURED |
| LCB z = 0.5 | +0.068 | no gain | MANUFACTURED |
| **abstain z = 0.5** | **+0.088** | **REAL** | **MANUFACTURED** |

Every other row is unchanged. **No lever is REAL.** The sentence above, "Abstention at z = 0.5 is
the only lever scored REAL", is withdrawn: under the rule written before the run it is manufacturing
agreement about item difficulty. The verdict (keep LCB z = 1.0, do not adopt abstention, do not move
the bar) is unchanged and now rests on the registered rule. `raise_kappa.py`'s main path applies the
registered rule from now on.

## 2. Kappa against learners, on EXCESS over deranged (`--curve`)

Baseline rule (LCB z = 1.0, bar 0.10, cell floor 10, 90 best-covered items, halves). Floor: the 100%
point reads +0.504 against this study's +0.494 (tolerance 0.05): PASSES.

| corpus | learners per half | raw kappa | deranged | **excess [95%]** |
| --- | ---: | ---: | ---: | --- |
| XES3G5M | 1,354 | +0.210 | +0.009 | +0.202 [+0.163, +0.231] |
| | 2,709 | +0.306 | +0.014 | +0.291 [+0.226, +0.338] |
| | 4,516 | +0.376 | +0.009 | +0.367 [+0.309, +0.403] |
| | 6,774 | +0.456 | +0.005 | +0.451 [+0.396, +0.473] |
| | 9,033 | +0.504 | +0.030 | +0.474 [+0.437, +0.508] |
| EdNet (60,000 learners) | 4,500 | +0.071 | +0.016 | +0.055 [+0.028, +0.086] |
| | 9,000 | +0.154 | +0.013 | +0.140 [+0.096, +0.175] |
| | 15,000 | +0.234 | +0.013 | +0.220 [+0.157, +0.284] |
| | 22,500 | +0.325 | +0.015 | +0.310 [+0.241, +0.355] |
| | 30,000 | +0.400 | −0.004 | +0.403 [+0.383, +0.414] |

**Verdict on both corpora: SAMPLE IS THE CEILING** (excess rises +0.272 on XES3G5M and +0.348 on
EdNet, intervals at the ends disjoint). The raw curve's conclusion survives on excess: the deranged
arm stays near zero at every size, so the rise is not exposure the derangement removes.

## 3. How many learners? (`kappa(n) = k_max · n / (n + n_half)`)

- **XES3G5M saturates.** k_max +0.644 [+0.584, +0.722], n_half 3,171. Excess kappa 0.60 needs about
  43,000 learners per half (lower bound 20,000; upper unbounded). **0.80 is UNREACHABLE BY SAMPLE SIZE
  ALONE**; 0.70 is reachable only at the top of k_max's interval.
- **EdNet does not yet bend.** Its excess rises almost linearly to 30,000 per half, so the fit puts
  k_max at its upper bound (1.5) and saturation is not identified. The fitted 57,000 / 74,000 /
  97,000 learners per half for 0.60 / 0.70 / 0.80 are a linear extrapolation, not an estimate, and
  their narrow intervals mean nothing. What is measured: at 60,000 learners EdNet's excess kappa is
  +0.403, three times the +0.13 its 6,000-learner prefix gave.

## What this does not show (read with `kappa_bar.py`)

The deranged arm crosses one learner's parent history onto another's dependant outcome. That removes
item-level exposure and **also removes learner-ability confounding**, so "excess over deranged" is not
"agreement about prerequisite structure". `kappa_bar.py`'s floor world makes the point concretely: a
graph whose asserted edges are 93% false (ability-driven) reached split-half kappa +0.646, all of it
excess over deranged, and Spearman–Brown +0.899. Rising kappa with more learners is the assay
becoming more repeatable; it is not shown to be the assay becoming more right.

## Board

A5 does not move: no decision rule raises structure-attributable agreement, and the sample route
saturates below 0.80 on XES3G5M. A5's "last cheap route" is closed.
