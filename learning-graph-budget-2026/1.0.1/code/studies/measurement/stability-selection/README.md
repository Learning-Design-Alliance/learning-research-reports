# Stability selection for data-derived edges, and the edge estimator's error curve (`stability.py`)

Paper II, F3. Literature review rank 4; strand 3 entries 3.8, 3.10 and 3.11, and strand-3 analyses 1
and 2. The design was pre-registered at `50bef7e` before any real number was computed. The docstring of
`stability.py` holds the full design, the floors and the verdict strings.

## What was asked

F3 says that split-half reliability does not certify edges. In `kappa_bar.py`'s calibrated simulation,
a graph estimated from 32,000 learners reaches Spearman-Brown +0.899 while its precision is 0.075. This
study asks three questions:

1. Stability selection (Meinshausen & Bühlmann 2010, with complementary pairs per Shah & Samworth 2013)
   gives per-edge selection probabilities and a bound on expected false selections,
   E[V] ≤ q²/((2τ−1)p). Does that bound hold on this estimator?
2. In particular, does the bound hold when noise is independent of curriculum order and fail when
   noise follows it, which is what entry 3.10 predicts?
3. What are the sensitivity, specificity and precision of the estimator as a function of learner
   count? The answer replaces the single 93% false-edge figure.

**Setup.** The estimator is the reliability study's drop at cell floor 10. Each draw splits the learners
into halves; there are 50 complementary pairs, so 100 half-samples. Each half-sample selects the top q
edges, with q set so that the bound at τ = 0.75 equals 1. τ = 0.75 is the primary threshold; 0.60 and
0.90 are reported.

**Simulation.** It uses `kappa_bar.World` as tuned. It reproduces kappa_bar's floor world exactly:
2,507 edges at precision 0.0750. There are four world types:

| World | Attempt order | Session state | Notes |
| --- | --- | --- | --- |
| I0 | random | none | kappa_bar's world |
| I | random | AR(1) on the logit, sd 0.6, ρ 0.9 | noise independent of curriculum order |
| C | catalogue order (jitter sd 3) | same as I | noise that follows curriculum order |
| C0 | catalogue order | none | reported, to separate the order from the session state |

Replication: 20 replicate worlds at density 0.10 (the primary density) and 10 at density 0.05. Each
replicate world is a new graph, new item difficulties and new learners. Intervals resample replicate
worlds.

## Floors

Both floors pass.

- **Reproduction.** kappa_bar world (0.10, seed 1) at 32,000 learners: 2,507 edges at precision 0.0750.
  This matches the reference exactly.
- **F1, recovery.** Sparse graph (density 0.05), no ability confound, N = 32,000, 10 worlds, τ = 0.75:
  - precision of the selected set 0.971 (replicate range 0.915–1.000);
  - recall 0.273 (0.186–0.368), against a ceiling of about 0.5 set by q = 42;
  - realised false selections V = 0.7 [0.2, 1.2] against a bound of 0.997.
  - This passes the pre-registered criteria (precision ≥ 0.90, recall ≥ 0.25, V ≤ bound). The recall
    criterion passed with little margin.
- **F2, a violation is visible.** The same world with 20 decoy pairs that share a learner factor but
  carry no gate. The violation is detected at the smallest decoy sd on the ladder (sd 1):
  V = 4.8 [3.1, 6.3] against a bound of 0.997. At sd 2 and sd 3, V is 27.3 and 31.8.
- **Classify check.** Both real grids match `positivity.classify` on 300 pairs. The fast cell routine
  matches `pairgrid.column_cells` exactly in every replicate and on both corpora.

## (2) Is the bound honest? Pre-registered verdict: **NOT SUPPORTED: THE BOUND HOLDS UNDER CURRICULUM ORDER**

Results at N = 32,000, density 0.10 and τ = 0.75. "Mean V" is the mean realised false selections over
20 worlds, with a bootstrap 95% interval over worlds.

| world | mean V | bound | V − bound | verdict | selected | precision of selected | sensitivity |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| I0 (Paper II's world) | 1.20 [0.70, 1.75] | 0.997 | +0.20 | VIOLATED (marginal) | 28.1 | 0.956 | 0.150 |
| I (independent) | 0.90 [0.45, 1.45] | 0.997 | −0.10 | HONEST (marginal) | 29.3 | 0.969 | 0.159 |
| C (curriculum-ordered) | 0.95 [0.55, 1.35] | 0.986 | −0.04 | HONEST (marginal) | 15.3 | 0.943 | 0.080 |
| C0 (order only) | 0.70 [0.35, 1.10] | 0.986 | −0.29 | HONEST (marginal) | 17.7 | 0.962 | 0.094 |

The verdict rule required I to be HONEST and C to be VIOLATED. C is not violated at the primary
threshold, so by the pre-registered rule the catalogue-order prediction is not supported. Every world
sits within about 0.3 false edges of its bound. Three secondary readings point the way entry 3.10
predicts, but none of them reverses the verdict:

- **At τ = 0.60, C violates decisively and I does not.** C: V = 3.45 [2.85, 4.05] against a bound of
  2.46. I: 1.60 [0.90, 2.35] against 2.49, which is honest. C0: 2.00 against 2.47, also honest. The
  combination of order and session state drives this, not order alone.
- **Curriculum order makes false edges more stable.** The mean selection probability of the ten most
  stable false edges is 0.548 in C, against 0.339 in I. C0 is 0.491 and I0 is 0.393.
- **Curriculum order lowers the true edges' stability.** The mean selection probability of a true edge
  is 0.106 in C, against 0.208 in I.

At density 0.05, all four worlds give the same verdicts at τ = 0.75 (I0 VIOLATED marginal 1.40 against
0.997; I, C and C0 HONEST), and C again violates at τ = 0.60 (3.30 against 2.50).

**The deranged null cannot see either mechanism.** In simulation, on 5 worlds per type, the deranged
arm selects 0 edges in every world type, while the real arm's V on the same worlds is 0.2 to 1.2. A
deranged-null check on real data therefore tests only exposure. It cannot detect false edges that come
from ability or a session state.

## (3) The error curve, replacing "93% false"

The adopted rule asserts an edge when drop − 1.0 se > 0.10, at cell floor 10. These are results for
world I0 at density 0.10: means, with the 2.5–97.5 percentiles over 20 worlds in brackets.

| learners | sensitivity | specificity | precision | edges asserted |
| ---: | --- | --- | --- | ---: |
| 500 | 0.372 [0.257, 0.456] | 0.784 [0.723, 0.833] | 0.085 [0.067, 0.110] | 792 |
| 1,000 | 0.562 [0.466, 0.650] | 0.710 [0.626, 0.783] | 0.095 [0.082, 0.116] | 1,076 |
| 2,000 | 0.696 [0.605, 0.802] | 0.633 [0.542, 0.699] | 0.093 [0.081, 0.105] | 1,359 |
| 4,000 | 0.803 [0.712, 0.871] | 0.556 [0.443, 0.639] | 0.089 [0.080, 0.099] | 1,635 |
| 8,000 | 0.873 [0.818, 0.911] | 0.488 [0.367, 0.564] | 0.084 [0.078, 0.092] | 1,876 |
| 16,000 | 0.921 [0.880, 0.953] | 0.418 [0.311, 0.489] | 0.078 [0.071, 0.085] | 2,122 |
| 32,000 | 0.949 [0.912, 0.974] | 0.365 [0.262, 0.447] | 0.074 [0.066, 0.082] | 2,304 |

Registered readings: SENSITIVITY RISES, SPECIFICITY FALLS and PRECISION FLAT with learners (I0, I).
In C and C0, PRECISION FALLS: C goes from 0.166 [0.135, 0.193] at 500 learners to 0.100 [0.087, 0.108]
at 32,000. **More learners do not make the adopted rule more accurate.** Its precision stays between
0.07 and 0.10 at every sample size from 500 to 32,000. Additional learners let it assert more of the
ability-driven non-edges, so specificity falls as fast as sensitivity rises. At density 0.05 the curve
has the same shape, with precision 0.054 at 32,000 (I0).

The stability-selected set (τ = 0.75) gives a different curve:

- precision is above 0.94 at every N from 8,000 upward, in every world;
- specificity is 1.000 throughout;
- sensitivity rises from 0.003 at 500 learners to 0.150 at 32,000 (I0, density 0.10).

It trades almost all recall for precision. At density 0.10 it never recovers more than about 16% of the
true edges.

## (1) Real data

The control column is the deranged arm's median smaller cell relative to the real arm's. Deranged runs
were done once per corpus; real runs twice.

| corpus | learners | items | readable pairs p | q | bound (τ 0.75) | selected at 0.60 / 0.75 / 0.90 (run 1; run 2) | deranged selected at 0.75 | control |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | --- |
| XES3G5M (top 200 KCs) | 18,066 | 200 | 32,362 of 39,800 | 127 | 0.997 | 24 / 10 / 3; 25 / 9 / 2 | 0 | 1.04× |
| EdNet KT1 (6,000-learner prefix) | 6,000 | 141 | 15,138 of 19,740 | 87 | 1.000 | 1 / 0 / 0; 2 / 0 / 0 | 0 | **0.43×** |

Pre-registered verdict on both corpora: **BOUND HONEST UNDER THE DERANGED NULL** (0 deranged selections
against a bound of about 1).

**What the real-data verdict supports.** The verdict is weak. The simulation shows that the deranged
null cannot see the ability or session mechanisms. On EdNet the deranged arm's cells are 0.43× the
real arm's, below the 0.5× control-scale floor (`shared/controls.check_control_scale`), so the EdNet
control is too small for the thing it controls.

**Corpus findings.**

- XES3G5M yields 9 to 10 stably selected edges out of 32,362 candidates. None has its reverse also
  selected. In simulation such a set was about 95% true. On real data no truth exists, and this set
  is not certified as prerequisites.
- EdNet yields no edge stable at τ = 0.75. This matches its split-half Spearman-Brown of 0.10 to 0.14.
- On both corpora, almost all of the per-half top-q edges change from one half-sample to the next.
  On XES3G5M, 32,037 of 32,362 candidates have π < 0.1. Of the 127 edges selected in each half,
  only 10 (7.9%) reach π ≥ 0.75 in run 1.

## What it means for Paper II (F3)

- **"Repeatability does not certify edges" holds for aggregate reliability, but stability selection is
  close to honest.** The split-half coefficient and the adopted rule certify nothing: precision is
  0.07–0.10 at every learner count, at SB +0.90. By contrast, per-edge stability selection with
  Meinshausen–Bühlmann control yields a small set that is about 95% true, and it exceeds its bound by
  at most 0.4 false edges at the primary threshold (+0.20 at density 0.10, +0.40 at 0.05, both in I0).
- **Curriculum order is a mechanism that loosens the bound.** It makes false edges more stable, and it
  breaks the bound decisively at τ = 0.60. At τ = 0.75 the bound held. Paper II can say the bound
  "becomes optimistic under curriculum order at lenient thresholds", not that it fails under curriculum
  order.
- **Replace the 93% figure with the curve.** The adopted rule's precision is 0.085 [0.067, 0.110] at
  500 learners and 0.074 [0.066, 0.082] at 32,000. Sensitivity rises from 0.37 to 0.95 while specificity
  falls from 0.78 to 0.37, so more learners do not buy accuracy. The point sits on Isvoranu & Epskamp's
  discovery/caution trade-off. Stability selection sits at the other end: precision about 0.95 and
  sensitivity 0.08–0.16 at 32,000.

## Limits

- The session state and the catalogue jitter are one mechanism by which noise could follow curriculum
  order. They were chosen by the agent, set before the run and not tuned.
- I, C and C0 were not re-tuned to XES3G5M. At density 0.10 their first-attempt accuracy is 0.61–0.68,
  against a target of 0.76.
- The bound's honesty is judged on means over 20 worlds. Most per-world verdicts are "marginal".
- q was set from the bound target, which caps stability selection's sensitivity. A larger q would
  raise both sensitivity and the bound.
- The MB bound is the conservative one. The tighter bounds of Shah & Samworth would be violated sooner.
- The real-data check is against exposure only.

## Coders

None. No construct is coded; every quantity is computed from attempt records or from simulation.

## Files

- `out/floor.json`: reproduction, F1 and F2.
- `out/sim.json`: per world type and density, the bound at every N and τ, the error curves and the
  deranged arm.
- `out/real.json`: per corpus, p, q, bounds, selection counts, the π histograms, the deranged arm and
  the control scale.
- `out/history-entry.json`.

Aggregates only. The data are XES3G5M (research use, non-redistributable) and EdNet KT1 (CC BY-NC 4.0).

```
python3 stability.py floor   # ~5 min
python3 stability.py sim     # ~70 min on a loaded 4-core machine
python3 stability.py real    # ~15 min
```
