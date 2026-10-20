# IITA on dense 15-skill sets: UNANSWERABLE on XES3G5M, no verdict on ASSISTments

**Status: run 2026-09-25 on real data, as pre-registered at 09b53ca** (design, thresholds and verdict
strings in the module docstring of [`iita_dense.py`](iita_dense.py)). Output:
[`out/iita-dense.json`](out/iita-dense.json).

## Result

| corpus | 15-skill sets | degenerate | pair / gate / chain detection | beyond null | verdict |
| --- | ---: | ---: | --- | ---: | --- |
| XES3G5M | 15 (5 short, excluded) | 0 | 0.07 / 0.27 / 0.20 | 0 of 15 | `UNANSWERABLE` (floor fails) |
| ASSISTments 2012 | 2 (8 short) | — | — | — | no verdict: mixing check failed |

**XES3G5M.** The instrument works as built: mixing passes, no set is degenerate, and IITA's relation
holds 668 planted arrows the right way round against 39 reversed. But the floor fails on the real
matrices as it did on synthetic ones: a single planted prerequisite is detected in 7% of placements
and a conjunctive gate in 27%, against a pass mark of 80%. So the observed 0 of 15 sets beyond the
null is not evidence of no structure; the implication count cannot see one dependency among 15 skills.
The plants lean to the lower tail (22 lower / 17 upper for pairs), consistent with the direction
RESULTS-IITA-REAL argues, but weakly.

**ASSISTments.** Only 2 of 10 sets reached 15 skills with 200 complete responders, and the sampler's
mixing check failed (Hamming ratio 0.958 against 0.98), so by the pre-registration the corpus gets no
verdict. With 2 sets it would have been `UNANSWERABLE` anyway (fewer than 5 scored).

**For Paper 1 (as fixed in advance):** an `UNANSWERABLE` corpus neither supports nor challenges the
item-tree bullet, and may not be cited as corroboration. The finding that carries is methodological:
the standard IITA implication-count test cannot detect a single planted prerequisite on 15-skill sets
of real data, so a null from it (including MOOCCubeX's 1 of 20) is not evidence of absence. A redesign
with a pair-level statistic against a fitted 2PL null is pre-registered separately (`iita_pairscan.py`).

## What it asks

Paper 1's item-tree bullet rests on 20 MOOCCubeX item sets where IITA finds nothing beyond ability
and difficulty (1 of 20 beats a fixed-margins null; [`RESULTS-IITA-REAL.md`](RESULTS-IITA-REAL.md)).
Those sets hold 3–6 items, 11 of the 20 have a degenerate null, and the test was one-tailed with the
tail itself in dispute. This study asks the same question per corpus (XES3G5M, ASSISTments 2012) on
15-skill sets built as [`surmise_graphs.py`](../../measurement/graph-typology/surmise_graphs.py)
builds them. It runs a two-sided fixed-margins test and measures a detection floor on each corpus's
own matrices before that corpus's verdict is read. Each corpus gets one of: `UNANSWERABLE`,
`STRUCTURE BEYOND ABILITY`, `NO STRUCTURE DETECTED`.

## What the synthetic run already says

`python3 iita_dense.py --synthetic` ([`out/iita-dense-synthetic.json`](out/iita-dense-synthetic.json))
covers two worlds of 10 sets each, one with a planted dependency and one without. The instrument
itself works: the null is never degenerate at 15 skills, mixing passes, and IITA's relation holds
every planted arrow the right way round. **The floor fails in both worlds**, though. Median per-set
detection is 0.03–0.13 for single pairwise and gate plants, and the plants split evenly between the
tails. A single dependency among 15 skills does not move the implication count beyond how far the
count swings between null draws. Both synthetic worlds return `UNANSWERABLE`. Unless the real
matrices behave very differently, the real run will return `UNANSWERABLE` on both corpora.

## Reproducing

```
python3 iita_dense.py --synthetic                 # out/iita-dense-synthetic.json, no corpus read
python3 iita_dense.py                             # out/iita-dense.json; reads $XES_DIR, $ASSIST_DIR
```
