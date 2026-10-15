# Is the edge matrix node effects, or is there pairwise structure to pool?

> **Re-issued 2026-09-24 ([`docs/notes/EDNET-REISSUE.md`](/docs/notes/EDNET-REISSUE.md)):** on a reproducible EdNet learner set, the pairwise residual after removing the multiplicative margin (`k=1`) is **+0.022** (was +0.054); the earlier '+0.435' headline used the retracted truncation measure; the antisymmetry verdict BOTH stands. EdNet figures below are superseded.

**What was asked.** Every pooling method — graphon estimation, USVT, stochastic block models, matrix
completion, and the GNN family that sits on top of them — makes the same bet: that the edge matrix is
a smooth low-rank object plus noise, so borrowing strength across pairs recovers signal that any
single cell is too thin to show. This tests the bet directly, and it is the fair representative of
the whole family. Decompose the edge matrix into node-level effects plus a residual, and ask whether
the **residual replicates across independent halves of the learners** above a margin-matched null.
If it does not, no amount of smoothing recovers structure that is not there.

`M[a,b]` is the outcome gap on *b* between learners who mastered *a* and learners who failed it —
the same quantity `studies/identifiability/overlap/` gates for positivity. Eight learner splits, cell floor 5, items with
fewer than 8 observed cells dropped.

## The correction that changed the answer

**The first version of this study tested the wrong thing, and its headline was wrong by a factor of
eight.** It measured the rank-*r* **truncation** of the residual: keep the top *r* singular
components and correlate those across halves. Rank 1 replicated at **+0.435** on EdNet against a null
of −0.003, and the run reported PAIRWISE STRUCTURE.

But **a rank-1 term `u_i · v_j` is a multiplicative node effect** — a source score times a target
score, which is another margin, not a pairwise interaction. Removing the additive margins
`mu + a_i + b_j` and then *keeping* the leading multiplicative one measures margins twice over and
calls the result structure. The arms were not independent either: "rank 2" was a truncation
*including* rank 1, so each arm contained the ones below it.

The corrected test **deflates** rather than truncates. After the additive margins, the top *k*
singular components are **removed**, and what survives is correlated across halves. `k = 0` is
additive-only; `k = 1` also removes the multiplicative margin; `k ≥ 2` removes progressively more
node-level structure. **Only what survives `k ≥ 1` can be called pairwise.**

## Result

**Verdict: PAIRWISE STRUCTURE — 6 of 6 `(corpus, deflation ≥ 1)` arms beat their margin-matched
null.**

| | XES3G5M | EdNet |
| --- | ---: | ---: |
| learners / items / cells | 18,066 / 160 / 21,601 | 6,000 / 139 / 12,956 |
| raw split-half (no decomposition) | +0.522 | +0.061 |
| **additive margins alone** | **+0.849** | **+0.276** |
| residual, additive removed (`k=0`) | +0.376 *(null +0.002)* | +0.026 *(null −0.002)* |
| **residual, + multiplicative removed (`k=1`)** | **+0.318** *(null −0.001)* | **+0.022** *(null −0.001)* |
| residual, `k=2` | +0.293 *(null +0.002)* | +0.020 *(null +0.002)* |
| residual, `k=3` | +0.265 *(null +0.002)* | +0.016 *(null −0.002)* |

EdNet column: re-issued on a reproducible learner set (6,000 learners, 12,956 cells; `docs/notes/EDNET-REISSUE.md`). XES3G5M column: as in the committed `out/lowrank.json` (21,601 cells), which a later rerun changed in the third decimal from the first issue (21,610 cells, k=1 +0.319); corrected 2026-10-08 to match the file.
| *what the first version measured (top-1 kept)* | *+0.713* | *+0.435* |

Three things to read off it.

**1. XES3G5M holds real pairwise structure, and it is substantial.** +0.318 after both kinds of
margin are gone, against a null of −0.001, and it decays slowly — +0.293 and +0.265 as more
node-level structure is stripped. It does not collapse the moment the multiplicative margin goes,
which is what a margin artefact would do. This is the strongest positive the pooling family has
produced in this programme.

**2. The margins are most of the matrix, and that is the corrected story.** The additive margins
alone replicate at **+0.849** on XES3G5M and **+0.276** on EdNet (re-issued; +0.601 in the first issue) — far above the residual in both
cases. An edge matrix is overwhelmingly "some items are harder, some learners' mastery of anything
predicts everything", and the pairwise part is the minority of what replicates. The original +0.435
on EdNet was **88% multiplicative margin**: deflating rank 1 takes it to +0.054.

**3. The corpus that reads more edges holds less structure.** EdNet is readable on 81.5% of pairs and
lands at +0.022; XES3G5M on 24.3% and lands at +0.318 — a **14× gap** (re-issued), in the same direction as `A5`,
where EdNet reaches split-half 0.337 and XES3G5M 0.643. EdNet's background drop is the smallest on
the board (+0.048, re-issued), so its edges are a longer list of smaller differences and there is less to pool.
**Readability and structure trade off**, which is a third instrument saying what `studies/measurement/reliability/` said:
reliability is bought by discarding pairs.

## What this does NOT establish

`M` is directional by **construction**, but a quantity being directional in its definition is not the
same as its **signal** being directional. Two items on the same topic will show a mutual gap in both
directions for reasons that have nothing to do with order. So +0.319 is pairwise; whether it is
**prerequisite** is a separate question, and this study does not answer it.

Two independent measurements in this repo predict it is **not**. `studies/identifiability/taxonomy-order/` found XES3G5M's
expert hierarchy inert for ordering (ancestor − descendant = −0.0128) while still carrying magnitude
(sibling − cross-root = +0.0161 [+0.0109, +0.0218]). `studies/producers/direction-benchmark/` found a text proposer
recovers **generality**, not prerequisite, and fails to beat a content-free degree rule on the honest
direction subset.

`antisymmetry.py` puts that to the test: split the residual into its symmetric part `(R + Rᵀ)/2`
(relatedness) and antisymmetric part `(R − Rᵀ)/2` (the only place a prerequisite claim can live), and
ask which replicates. **That study's floor already produced a result worth recording on its own** —
see below.

## A by-product of the floor: a prerequisite that is a pure skill difference is unrecoverable

The first antisymmetry floor planted `A[i,j] = s_i − s_j` from a latent score per item. It read
**+0.004 against a null of −0.008** — nothing. The generator was wrong, and *why* it was wrong is a
statement about the estimand, not the instrument: `s_i − s_j` is exactly `a_i + b_j` with `a_i = s_i`
and `b_j = −s_j`, so it **is an additive margin** and `additive()` removes it before the
decomposition ever sees it.

**A prerequisite that acts as a pure skill difference is indistinguishable from node effects by
construction, and no amount of pooling will recover it.** Only an order that is *not* a total ranking
— one with genuinely incomparable pairs — leaves an antisymmetric residue behind the margins. The
corrected generator plants a sparse random DAG and recovers it at **+0.822** against a null of +0.003,
with a purely symmetric world leaking **−0.000** into the antisymmetric arm.

## Pre-registered verdict

Revised before any corrected number was read:

| verdict | condition |
| --- | --- |
| `PAIRWISE STRUCTURE` | the **deflated** residual at `k ≥ 1` replicates above its margin-matched null |
| `MARGINS ONLY` | it does not — the edge matrix is node-level effects, additive and multiplicative, and there is nothing to recover by pooling |

## Licence

EdNet is CC BY-NC 4.0 — non-commercial, **no model training**; fitting two scalars per learner to
test whether one suffices is analysis, not training. XES3G5M is handled as research use. Raw exports
stay in the session scratchpad; only the aggregate is committed.

```
python3 lowrank.py --splits 8
python3 antisymmetry.py --floor-only
python3 antisymmetry.py --splits 8
```
