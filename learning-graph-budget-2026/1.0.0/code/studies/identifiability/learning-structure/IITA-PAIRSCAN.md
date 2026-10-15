# Pair-level dependence beyond one trait: found on XES3G5M; ASSISTments unanswerable

**Status: run 2026-09-26 as pre-registered at 31ed282** (design, thresholds, verdict strings and the
eight changes the synthetic run forced are in the module docstring of
[`iita_pairscan.py`](iita_pairscan.py)). Output: [`out/iita-pairscan.json`](out/iita-pairscan.json).

## Result

| corpus | scored sets | floor (PAIR / GATE / CHAIN) | fitted-model false positives | sets firing (isolated) | binomial p | verdict |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| XES3G5M | 15 | 1.00 / 1.00 / 0.90 — passes | 0.00 | **8 of 15** | 1.8 × 10⁻⁷ | **PAIRWISE LOCAL DEPENDENCE BEYOND ONE TRAIT** |
| ASSISTments 2012 | 2 | 0.70 / 0.60 / 0.40 — fails | 0.00 | 0 of 2 | 1 | UNANSWERABLE (floor fails; also < 5 sets) |

**XES3G5M.** All 15 fits converge. The instrument is demonstrated on the corpus's own matrices: a
planted 0.9-strength prerequisite is flagged in a median 100% of placements, and data simulated from
each set's fitted one-trait model never fires (0 of 30). Against that, 8 of 15 real sets carry at least
one isolated pair with fewer counterexamples than one latent trait (ability, difficulty and
discrimination, with shared guess and slip) implies: 20 isolated ordered pairs in all, most of them
both orientations of the same skill pair (the statistic cannot orient a pair), z from −3.7 to −5.1.
One further set shows only clustered dependence (the multidimensional kind). The firing sets are mostly
the larger ones (8 of the 11 sets with 700 or more learners), which is what real but modest dependence
detected at the edge of power looks like.

**What it may and may not be called (fixed in advance).** This is pairwise local dependence beyond one
trait. It is not shown to be prerequisite structure: the statistic cannot orient a pair, and a second
trait shared by exactly two skills produces the same signal (the synthetic doublet world fired in 8 of
20 sets). These pairs are candidates for an experiment, not edges.

**For Paper 1 (fixed in advance):** the item-tree bullet must be narrowed. "No dependency beyond ability
and difficulty" holds only for IITA's count statistic on sparse MOOCCubeX item sets, a statistic this
programme has now shown cannot see a single planted prerequisite (IITA-DENSE.md). On dense skill data, a
pair-level test with a demonstrated floor finds pairwise dependence one trait does not explain.

## What it asks

[`iita_dense.py`](iita_dense.py) ([`IITA-DENSE.md`](IITA-DENSE.md)) could not detect one planted
prerequisite among 15 skills: the IITA implication count barely moves. A pair-level scan found the
plants, but against a fixed-margins null it also fired on every world with no dependency at all,
because that null holds only when all skills discriminate equally. This study keeps the pair-level
scan and swaps the null. Each 15-skill set gets a unidimensional 2PL fit (difficulty and
discrimination free, plus two shared guess and slip asymptotes), and a parametric bootstrap from
that fit, refitted on every draw, is what the observed counterexample counts are scored against. A
pair with fewer counterexamples than one latent trait implies is local dependence beyond that trait.
Each corpus (XES3G5M, ASSISTments 2012) gets one of: `UNANSWERABLE`,
`PAIRWISE LOCAL DEPENDENCE BEYOND ONE TRAIT`, `NO DEPENDENCE DETECTED`.

## What the synthetic run already says

`python3 iita_pairscan.py --synthetic` ([`out/iita-pairscan-synthetic.json`](out/iita-pairscan-synthetic.json))
covers six worlds of 20 sets each, shaped like the real sets (15 skills, 200–3000 learners). Four
were asked for: 2PL with no dependency, 2PL with planted prerequisites, two latent traits with no
prerequisite, and 3PL guessing with no prerequisite. Two were added: 5% misclassification, and a
second trait shared by exactly two skills.

| world | sets firing (isolated pair) | PAIR floor | fitted-model false positives | verdict |
| --- | --- | --- | --- | --- |
| 2PL, no dependency | 0 / 20 | 1.00 | 0.05 | NO DEPENDENCE DETECTED |
| 2PL + planted prerequisites | 19 / 20 | 0.90 | 0.075 | PAIRWISE LOCAL DEPENDENCE |
| two traits, no prerequisite | 1 / 20 (clustered in 19) | 0.97 | 0.025 | NO DEPENDENCE DETECTED |
| 3PL guessing | 2 / 20 | 1.00 | 0.00 | NO DEPENDENCE DETECTED |
| 5% misclassification | 0 / 20 | 1.00 | 0.00 | NO DEPENDENCE DETECTED |
| two-skill second trait | 8 / 20 | 1.00 | 0.00 | PAIRWISE LOCAL DEPENDENCE |

Unlike [`iita_dense.py`](iita_dense.py), this instrument finds single planted prerequisites: 89–99%
of placements, against 3–13% there. It stays quiet on unequal discrimination, guessing and
misclassification. Getting there took eight design changes, all made before any real data was read
and each recorded with its reason in the docstring. Three of them change what a positive result can
claim:

- **Orientation is not identified.** The asymmetry check the brief proposed (a prerequisite should
  depress one discordant cell and not the other) cannot work. Once both margins are fitted, a pair's
  2×2 table has one free cell, so a deficit in one discordant cell is the same count deficit in the
  other. Planted prerequisites came out asymmetric in 2–5% of placements.
- **Multidimensionality is screened by isolation instead.** A second trait over several skills
  leaves triangles of dependent pairs; a planted prerequisite leaves a single pair. The screen takes
  the two-trait world from 20 of 20 sets firing to 1 of 20. It cannot see a second trait shared by
  exactly two skills, which fires like a prerequisite.
- So the positive verdict is `PAIRWISE LOCAL DEPENDENCE BEYOND ONE TRAIT`, not "prerequisite-like".

The other changes are technical. The model gains two shared guess and slip asymptotes; without them
the misclassification world returned a false positive verdict. The fit moved from EM to L-BFGS-B.
Residuals are studentised before the bootstrap. Pairs are declared significant at 0.025.

The real run will not produce a verdict for ASSISTments: only 2 of its sets reach 15 skills, below
the 5-set minimum. A real set of 3000 learners costs at most about 6.5 minutes on one core, so 20
such sets fit in about 35 minutes per corpus on 4 workers.

## Reproducing

```
python3 iita_pairscan.py --synthetic --workers 2    # out/iita-pairscan-synthetic.json, no corpus read
python3 iita_pairscan.py --workers 4                # out/iita-pairscan.json; reads $XES_DIR, $ASSIST_DIR
```
