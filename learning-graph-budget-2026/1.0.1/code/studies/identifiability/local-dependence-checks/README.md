# Standard LD indexes and a bifactor re-scan beside the pairwise scan (Paper II, F6)

**Status: run 2026-10-07. The design was pre-registered at `018e286`, before any real number was read.
The synthetic floor was committed at `76dd563`. The real run is committed with this README.** The design,
thresholds and verdict strings are in the docstring of [`ld_checks.py`](ld_checks.py). Outputs:
[`out/ld-checks-synthetic.json`](out/ld-checks-synthetic.json) (no response data read) and
[`out/ld-checks.json`](out/ld-checks.json).

## What it asks

Paper II's F6 rests on two studies. [IITA-PAIRSCAN](../learning-structure/IITA-PAIRSCAN.md) found an
isolated pair with local dependence beyond one trait in 8 of 15 XES3G5M sets (12 unordered pairs).
[PAIRSCAN-CURRICULUM](../learning-structure/PAIRSCAN-CURRICULUM.md) found that those pairs are concentrated
in taxonomy-adjacent skills. The literature review (rank 6; entries 1.11 and 6.1-6.10) asked two
questions about this result:

- **(a)** Does the result depend on the scan's non-standard statistic? To find out, Chen-Thissen G² (and
  X²) and mean-centred Yen's Q3 (Christensen et al. 2017) are run under the *same* refitted parametric
  bootstrap, at the same unordered-pair grain, with the same max-T level (0.025) and isolation rule.
- **(b)** Is the result a unit-level factor or pair-specific dependence? To find out, a bifactor model
  with one group factor per XES3G5M taxonomy parent is fitted, and the scan statistic is rerun on what
  the model leaves.

## Result

**(a) Reading: PARTLY ANSWERABLE.** G² reproduces the set-level result exactly. Q3 fails its detection
floor, so it is UNANSWERABLE.

| statistic (XES3G5M, 15 sets) | PAIR floor (median per set) | fitted-model false positives | sets firing | binomial p | flagged pairs | overlap with the committed 12 | pooled Jaccard [95%, sets resampled] | per-set verdict agreement (kappa) | verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| pairscan (recomputed) | 1.00 | 0.000 | 8 | 1.8 × 10⁻⁷ | 12 | 12 | 1.00 | 15/15 (1.00) | PAIRWISE |
| **Chen-Thissen G²** | 1.00 | 0.000 | **8** | 1.8 × 10⁻⁷ | 12 | 10 | 0.71 [0.43, 1.00] | 13/15 (0.73) | **PAIRWISE** |
| X² (reported only) | 0.87 | 0.000 | 8 | 1.8 × 10⁻⁷ | 12 | 11 | 0.85 [0.56, 1.00] | 13/15 (0.73) | PAIRWISE |
| **Q3\*, mean-centred** | **0.60** | 0.000 | 6 | 5.3 × 10⁻⁵ | 10 | 9 | 0.69 [0.43, 0.89] | 13/15 (0.74) | **UNANSWERABLE** (floor fails) |

- **Reproduction check.** The replayed bootstrap matches the committed scan exactly: 15 of 15 scanned
  counts are the same, the largest critical-z difference is 0.0000, and the recomputed flags are the
  committed 12 pairs (Jaccard 1.00).
- **G².** G² fires in 8 sets, the same number as the scan, but not in the same sets. G² fires in set 6
  (2 pairs) and not in set 10. Ten of its 12 pairs are committed pairs. Three of its 12 flagged pairs are
  taxonomy-adjacent (within-set permutation p = 0.0013). The adjacency concentration therefore does not
  depend on the statistic either.
- **Q3.** Q3's floor is uneven across sets. PAIR detection is 0.53 to 1.00 in sets 0 to 9 and 0.07 to
  0.40 in sets 10 to 14, the last five sets the greedy construction built (n = 278 to 737). Mean-centred
  Q3 under this bootstrap cannot reliably see a single 0.9-strength plant in those sets. Its 6-of-15
  firing and its 9 overlapping pairs are descriptive only. G²'s per-set floor also drops in sets 10 to 14
  (0.20 to 0.73), but its median is 1.00.
- **ASSISTments 2012** (2 sets): every statistic is UNANSWERABLE because its floor fails (G² PAIR 0.50,
  Q3 0.50, pairscan 0.70), and there are fewer than 5 sets. No statistic flags an isolated pair there.

**(b) Verdict: MIXED.** In the testable class, 3 of 5 within-module pairs survive the module factors
(0.60). The scan still fires in more sets than chance. The adjacency concentration is no longer
significant, but it was not significant in the reference arm either.

| | 1D-PL (reference arm, no group factors) | BF-PL (module factors) |
| --- | ---: | ---: |
| sets firing (isolated pair), of 15 | 10 (binomial p = 2.3 × 10⁻¹⁰) | 5 (p = 0.00061, chance rate 0.05) |
| flagged pairs | 24 | 9 |
| adjacent (R1) among them | 3 (0.125 vs 0.039 expected, p = 0.054) | 1 (0.111 vs 0.019, p = 0.16) |

The 12 committed pairs, classed by the module (depth-2 route) groups:

| class | committed | kept by 1D-PL | of those, kept by BF-PL | survival [Clopper-Pearson 95%] |
| --- | ---: | ---: | ---: | --- |
| **WITHIN** (a factor group of ≥ 3 skills; the testable case) | 5 | 5 | **3** | **0.60 [0.15, 0.95]** |
| CROSS (no shared module; the churn control) | 5 | 5 | 4 | 0.80 [0.28, 0.99] |
| DOUBLET (a 2-skill module; untestable, Ip 2010) | 2 | 1 | 1 | — |

The pre-registered rule reads MIXED. UNIT-LEVEL needs within-module survival ≤ 0.25 with no BF
adjacency enrichment. Survival is 0.60. PAIR-SPECIFIC needs survival ≥ 0.50, BF adjacency p < 0.05 and a
positive BF scan. Survival and the scan pass, but adjacency p = 0.16 fails. In any case, PAIR-SPECIFIC
would have been downgraded to MIXED: in the group-free world, the BF scan's false-alarm rate was 0.15,
against a limit of 0.10 (see floor).

Of the three committed adjacent pairs, one is a doublet that the 1D-PL arm already lost. One is within a
module and survives. One is within a module and is lost. Within-module survival (0.60) is below the CROSS
churn rate (0.80), a difference of one pair out of five.

Two caveats on the comparison:
- **The reference arm differs from the committed scan.** The 1D-PL arm keeps 11 of the 12 committed pairs
  but flags 24 pairs in all. Twelve of those come from set 10 alone (n = 737), where the
  pairwise-likelihood estimator clearly behaves differently from the full-information fit. The
  1D-PL adjacency test is diluted by them, so the before/after adjacency contrast is weak. The
  pair-level survival table above, restricted to the committed pairs, is the cleaner reading.
- **Some bootstrap refits did not converge.** This happened in the small sets 9 and 11 (52 and 35 of
  500 refits under 1D-PL; 65 and 47 under BF-PL). Neither set holds a committed pair.

**Floor (b).**
- *Synthetic group world* (20 sets, module partitions of the real sets, a group factor and no pair
  dependence, R = 200 bootstrap draws). The BF scan's false-alarm rate is 0.05, against a limit of 0.10.
  The one-trait (1D-PL) scan fires in 0.25 of the same sets. Its 5 flagged pairs include 3 within-module
  pairs, and none of the 3 survives BF: where the truth is a unit factor, the re-scan makes the flags
  vanish. Pair plants placed inside this bifactor world are detected at a median per set of 1.00 both
  WITHIN and CROSS (pooled 0.93 and 0.97).
- *Real sets.* BF plant detection has a median per set of 1.00 both WITHIN and CROSS (pooled 0.88 and
  0.87). The BF fitted-model false-positive rate is 0.033.
- *Group-free world* (each grouped skill gets its own loading, so the one-loading model is
  misspecified). The BF false-alarm rate is 0.15, above 0.10. This triggers the pre-registered
  downgrade. It also means that some survivals on real data may reflect within-module loadings the
  constrained model cannot represent, rather than pair links.
- *Control size.* A plant changes a median of 58 cells. The bootstrap null differs from the observed
  matrix in a median of 2,623 cells.

## What it means for F6

- **The set-level claim does not rest on the scan's statistic.** Chen-Thissen G², under the same refitted
  bootstrap with a passing floor, fires in 8 of 15 sets. Ten of its 12 pairs are the scan's. Its flagged
  pairs are concentrated in adjacent skills (3 of 12, p = 0.0013). F6 may cite G² beside the scan. Pair
  lists should be cited with their overlap (pooled Jaccard 0.71 [0.43, 1.00]). Q3 cannot be cited as
  corroboration: its floor fails.
- **Unit-level against pair-specific is not settled.** Module factors remove most of the extra
  firing: 10 to 5 sets in the like-for-like comparison, and 24 to 9 flagged pairs. Even so, 5 of 15 sets
  still fire beyond module factors (p = 0.00061), and 3 of the 5 testable within-module committed pairs
  survive. The adjacency concentration does not survive as a significant enrichment: 1 of 9 flagged
  pairs is adjacent, p = 0.16. Under the registration, F6 keeps its current wording and states that a
  unit (module) factor was not excluded. Ip's (2010) equivalence applies to any surviving pair, and the
  group-free false-alarm rate shows that unequal within-module loadings can mimic survival.

## Decisions (all recorded in the docstring before the run)

- **Parent level.** The parent is the depth-2 route prefix: scheme root plus module. The immediate parent
  and the depth-3 topic were not used, because in these sets they form almost only one- and two-skill
  groups. A factor on two skills is the pair dependence itself, so finding that it absorbs the pair
  would be tautological.
- **Group factors.** Only groups of 3 or more skills get a factor, with one loading per group.
- **Estimation.** The bifactor model is fitted by pairwise (limited-information) likelihood, because
  full-information bifactor estimation with 500 refits per set was too slow for the shared machine.
  The comparison arm is therefore the same pairwise-likelihood code without group factors.
- **Bootstrap draws.** Synthetic worlds and the BF fitted-model check use R = 200 draws. The max-T level
  of 0.025 needs only R ≥ 40.

## Reproducing

```
python3 ld_checks.py --synthetic --workers 3   # out/ld-checks-synthetic.json (~35 min on a loaded machine)
python3 ld_checks.py --workers 3               # out/ld-checks.json; reads $XES_DIR, $ASSIST_DIR (~1 h)
```

Reads XES3G5M and ASSISTments 2012 through `shared.paths.data_path`. Only aggregates are written: skill
ids, counts and flags. No coded construct is involved: every flag is computed by rule from the responses.
