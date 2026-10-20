# Do the real KC routes beat deranged routes in the XES3G5M authors' deep models?

**Asked** (maintainer, 2026-10-12). Paper II, Section 5.4, reported that the deep-model version of the
KC-tree control had not been run. Liu et al. (2023) fused route-text embeddings into simpleKT and AKT
and found nothing gained over content alone, with no control. `kc_tree.py` gave the control inside a
logistic model. This study runs the control in the authors' two deep models: real route text against
route text from three deranged route trees of the same shape (`kc_tree.py`'s Fd trees), on the authors'
folds and test set.

**Status: DONE (2026-10-13). Both floors fail; both models read UNANSWERABLE, and neither real run was started.** The design, arms, gate, floor and verdict strings are in the
docstring of `dkt_routes.py`, committed before any model saw an XES3G5M response. The fusion is in
`fusion.py`. The run code and the decisions it fixed (CHANGES 1-3) were committed before the run
started; `python3 dkt_routes.py --smoke` checks it end to end on fake data, on a CPU.

**Data handling.** Approved by the maintainer on 2026-10-12: the run happens on a private RunPod pod
(secure cloud, no network volume), which is deleted when the run ends; only the aggregates in `out/`
come back. Route names are embedded on the pod by a public encoder. No text goes to any model API.

## Cost check (`timing.py`, synthetic data, `out/timing.json`, `out/cost.json`)

One fold (26,718 training rows of 200 KC attempts, 6,679 validation rows) on one RTX 4090, secure cloud,
billed at $0.89 an hour. Three epochs per model and arm; the first includes warm-up.

| model | seconds per epoch (route arm) | peak GPU memory |
| --- | ---: | ---: |
| simpleKT | 12.2 | 3.1 GB |
| AKT | 32.4 | 10.1 GB |

The content-only arm runs at the same speed. Adding route text does not change the cost.

The unknown is how many epochs each model needs before pyKT's rule stops it (10 epochs with no gain on
validation, at most 200). AKT trains at a learning rate of 1e-5, so it is likely to run long. There are
35 trainings per model: 25 for the real run (5 arms by 5 folds) and 10 for the floor (2 worlds by 5 arms,
fold 0). The projection adds 10% for loading, test scoring and the encoder.

| scenario | simpleKT epochs | AKT epochs | GPU-hours | cost |
| --- | ---: | ---: | ---: | ---: |
| fast | 30 | 60 | 25 | $22 |
| middle | 60 | 120 | 49 | $44 |
| slow | 120 | 200 | 85 | $75 |

AKT accounts for most of the cost in every scenario. Up to two AKT trainings fit on one 24 GB card at
once, so wall-clock time can be cut by running several pods, at the same total cost. The timing check
cost about $0.25.

## What came back

**Both floors fail, so both verdicts read UNANSWERABLE (floor fails), and no model was trained on real
XES3G5M responses.** In the synthetic world with a planted route-family effect (gamma 2), every arm
scored the same test AUC to within 0.0005, the content-only arm included:

| model | world | C | R | Rd0 | Rd1 | Rd2 | R - Rd-bar [95%] | V1 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| simpleKT | planted | 0.8063 | 0.8061 | 0.8060 | 0.8061 | 0.8061 | +0.0001 [+0.0001, +0.0001] | equivalent |
| simpleKT | null | 0.7986 | 0.7988 | 0.7982 | 0.7983 | 0.7982 | +0.0006 [+0.0005, +0.0007] | equivalent |
| AKT | planted | 0.8022 | 0.8024 | 0.8021 | 0.8020 | 0.8019 | +0.0004 [+0.0003, +0.0004] | equivalent |
| AKT | null | 0.7943 | 0.7945 | 0.7941 | 0.7945 | 0.7943 | +0.0002 [+0.0002, +0.0003] | equivalent |

(`out/floor_simplekt.json`, `out/floor_akt.json`; fold 0 only, 1,000 bootstrap draws over the 3,613 test
learners. The intervals are narrow because the arms' predictions are paired and nearly identical.)
The floor needed ROUTES BEAT THEIR DERANGEMENT in the planted world; both models read ROUTES
EQUIVALENT TO THEIR DERANGEMENT in both worlds. Route text added nothing over content alone in either
world (V2: ROUTES EQUIVALENT TO CONTENT ALONE, all four rows).

**What the failure means.** Fusing route text into these models does not let them use a planted
route-family effect, so a null on the real data would not have been evidence about the routes. There
is a second reading, which this floor cannot separate from the first: the generator sends each learner
through a family in blocks of ten attempts, so a learner's recent history already is the family, and a
sequence model can learn the family effect from recency and its own KC embeddings without any tree.
The content-only arm doing as well as the route arms in the planted world fits that reading. Either
way the instrument, as built, cannot answer the question. A generator that interleaves families (so
that only the tree says which earlier attempts belong to the current family) would be a new
pre-registration, not a change to this one.

**Checks that passed on the pods.** The tarball's MD5, the rebuilt `cid2route.json` and all four route
trees matched the values computed here before the run (`out/prep_*.json`). The encoder resolved to
`hfl/chinese-roberta-wwm-ext` revision `5c58d0b8ec1d9014354d691c538661bf00bfdb44`. The control-size
check passed: the mean cosine distance between a KC's real and deranged route vectors is 0.058, against
0.100 between two random KCs' real route vectors (0.58 of a full shuffle; the floor in
`shared/controls.py` is 0.5).

**What it cost.** $12.96 in all (`out/cost.json`): the timing check, three aborted launches that touched
only synthetic floor data (CHANGES 4 and 5), 0.20 hours of simpleKT on 2 RTX 4090s and 2.68 hours of
AKT on 4 L40S. The AKT floor trainings ran about 150 epochs before pyKT's stopping rule ended them;
simpleKT's ran about 20.

**For Paper II.** Section 5.4's statement that the deep-model control was not run should become: it was
run, and its floor failed for both of the authors' models, so the authors' null (Liu et al. 2023) still
has no control that could have detected the routes.
