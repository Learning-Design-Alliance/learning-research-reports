# XES3G5M's expert KC-route tree against deranged trees of the same shape

**Status: run 2026-10-07 as pre-registered.** The design, controls, floor and verdict strings are the
module docstring of [`kc_tree.py`](kc_tree.py), committed at dfc8545 before any learner data was
read. No design change followed. Outputs: [`out/synthetic.json`](out/synthetic.json) and
[`out/result.json`](out/result.json).

## What it asks

The XES3G5M dataset paper (Liu et al., NeurIPS 2023; entry 5.9 of the Paper II literature review)
reports that adding the dataset's KC routes to knowledge-tracing models adds nothing, or slightly hurts,
once question content is in. The authors describe the route tree as encoding prerequisite relations. Their
null has no control. Paper II's F5 ([`../xes3g5m-build/`](../xes3g5m-build/), `e2e.py`) found that
LLM-built edges add no more than shuffled or reversed edges. This study asks the same question of the
platform's own expert tree, in e2e.py's framework. That framework fixes the TRAIN/TEST learner split,
the per-question difficulty offset in every arm, the IRLS logistic model, AUC on held-out learners, the
paired learner bootstrap (B = 200) and the +0.001 bar.

| arm | P block (prior history on...) | size |
| --- | --- | --- |
| M2 | none; difficulty offset, overall history, expert leaf-KC history (e2e.py's M2) | — |
| T, real tree | each KC's KC parent: the nearest KC above it on its route | 559 links, 555 child KCs |
| Td0–Td4, deranged | the same forest with every child moved to another parent, matched by route depth of child and parent | 559 links each, same out-degrees |
| Tr, reversed | each KC's KC children | 559 links |
| F, route family (secondary) | KCs under the KC's parent route node, outside its own subtree | mean 8.3 KCs |
| Fd0–Fd2, deranged route tree | families recomputed after every route node of depth ≥ 2 is moved to another parent of the same depth | mean 7.7–10.6 KCs |

No deranged tree keeps a real parent link, and none contains a real link reversed. In 0 to 4 of the 559
edges the parent depth changed; these are edges whose depth group could not be deranged.

**Not replicated:** the authors' early-fusion deep models (simpleKT and AKT with text embeddings). They
need a PyTorch GPU run. This machine has four shared CPU cores and no torch, so e2e.py's model is used
throughout.

## Detection floor (synthetic, no corpus)

Each simulated world has 30 KCs under 3 module nodes and 3,000 learners. Mastery affects accuracy
through the KC parent (planted-parent), through the route family (planted-family), or through neither
(null).

| worlds | T − Td-bar | T beats Td-bar | F − Fd-bar | F beats Fd-bar |
| --- | --- | ---: | --- | ---: |
| planted-parent (5) | +0.0098 to +0.0137 | 5/5 | +0.0024 to +0.0045 | 5/5 |
| planted-family (5) | +0.0041 to +0.0070 | 5/5 | +0.0043 to +0.0079 | 5/5 |
| null (10) | −0.0001 to +0.0000 | 0/10 | −0.0002 to +0.0000 | 0/10 |

**TREE FLOOR PASSES; FAMILY FLOOR PASSES.** M2 beats M1 in every planted world. Every null interval
for T − Td-bar lies within [−0.00017, +0.00007]. The floors are not specific to their own mechanism:
each arm also detects the other's planted effect. The lean feature code equals e2e.features exactly
on a synthetic world. Random synthetic trees in which one hub held most of the child slots could not
be deranged; they were redrawn, 0 to 20 times per world (counts in `synthetic.json`). The planted
effects (about +0.01 AUC) are much larger than the bar. The floor shows that the instrument works,
and the null worlds show its noise, about ±0.0002. It does not map the smallest effect the
instrument can detect.

## Result (4,391,076 TRAIN and 1,101,162 TEST attempts; 3,630 TEST learners)

The run first reproduced e2e.py's published M1 (0.791880) and M2 (0.796524) AUCs exactly.

| model | AUC | cold start |
| --- | ---: | ---: |
| M1 no skills | 0.791880 | 0.78861 |
| M2 expert KCs | 0.796524 | 0.78887 |
| T real tree | 0.796575 | 0.78897 |
| Td-bar deranged trees (mean of 5) | 0.796538 | 0.78888 |
| Tr reversed tree | 0.796554 | 0.78893 |
| F route family | 0.797254 | 0.79011 |
| Fd-bar deranged route trees (mean of 3) | 0.796530 | 0.78886 |

Cold start means the TEST attempts with no prior attempt on any of the question's KCs (408,283
attempts).

All differences are paired learner-bootstrap 95% intervals: the bootstrap resamples the 3,630 TEST
learners.

| contrast | all TEST attempts | cold start |
| --- | --- | --- |
| **T − Td-bar** (V1) | **+0.000037 [+0.000010, +0.000063]** | +0.000084 [+0.000049, +0.000120] |
| T − M2 (V2) | +0.000051 [+0.000025, +0.000080] | +0.000096 [+0.000062, +0.000135] |
| T − Tr (direction) | +0.000021 [−0.000005, +0.000055] | — |
| Td-bar − M2 | +0.000014 [+0.000007, +0.000020] | — |
| **F − Fd-bar** (V3) | **+0.000724 [+0.000638, +0.000816]** | **+0.001245 [+0.001118, +0.001372]** |
| F − M2 | +0.000731 [+0.000643, +0.000824] | +0.001238 [+0.001106, +0.001364] |
| M2 − M1 | +0.004644 [+0.004302, +0.004962] | +0.000263 [+0.000161, +0.000385] |

T beats each of the five derangements by +0.000025 to +0.000043. F beats each of the three by +0.000723
to +0.000725.

**V1: TREE EQUIVALENT TO ITS DERANGEMENT.** The whole interval for the real tree minus its derangements
lies inside ±0.001. Its upper bound, +0.000063, is about one sixteenth of the bar. **V2: TREE ADDS
NOTHING** over expert KCs alone. **Direction:** CLAIMED by +0.00002, and the interval includes 0.
This is reported only.

**V3: FAMILY EQUIVALENT TO ITS DERANGEMENT** under the pre-registered rule, because the interval lies
inside ±0.001. The difference is positive, however, and the interval excludes 0: the real route family
adds a small signal that is specific to it, +0.0007. At cold start the gap is +0.0012 [+0.0011,
+0.0014]. That is above the +0.001 bar, but it is a descriptive result, not a verdict.

**Control size.** Size is measured as the share of TEST attempts whose P set holds prior history. The
deranged trees reach 0.70 to 0.92 times T's share (T: 0.074), and the deranged route families reach
0.52 to 0.61 times F's share (F: 0.519). Both pass the 0.5 check in `shared/controls.py`. The real
families have prior history more often because the platform presents sibling KCs close together.
Part of F's advantage may therefore be curriculum order, not structure. The design cannot separate
the two.

## What it means for Paper II

- **The XES3G5M authors' unexplained null becomes a controlled null, in this model.** The expert tree's
  parent links predict no better than a same-shape tree with every real link destroyed. This matches
  F5's finding for LLM-built edges: neither the expert edges nor the built edges carry
  edge-specific signal at e2e.py's bar. The edge null is therefore not a failure of LLM building.
  The platform's own prerequisite tree, used the same way, does no better.
- **What the tree does carry is grouping, not direction.** Pooling history over a KC's route family
  gives +0.0007 overall and +0.0012 at cold start. Both are specific to the real tree. This fits
  the literature review's note that the hierarchy's value is concentrated at cold start (entry 5.9
  against F5's sibling-group result). It is also a second instance of F5's "nodes and grouping, not
  edges".
- **Limits.** The model is a logistic model with additive history features, not the authors'
  early-fusion deep models. A direction-aware or embedding-based architecture could still use the
  tree differently. Prediction is not learning. Platform order makes parent history more often
  present than child history, which is why the reversed arm is not verdict-bearing.

## Reproducing

```
python3 kc_tree.py --synthetic   # the floor; no corpus (about 15 minutes)
python3 kc_tree.py               # needs XES_DIR (data/data-sources.json); about 10 minutes, 2.7 GB peak
```

`figure_usefulness.py` draws Paper II's Figure 3 (this study's same-shape controls beside the coupled
state's retained-share rule) from `out/result.json`, `kc_tree.py`'s constants and
`studies/measurement/graph-state/coupling.py`; it reads no corpus.
