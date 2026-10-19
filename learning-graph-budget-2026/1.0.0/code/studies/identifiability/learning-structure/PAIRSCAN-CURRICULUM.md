# Are the flagged XES3G5M pairs curriculum-linked? Yes

**Status: run 2026-09-26 as pre-registered at 314fcce; see Result.** The design, thresholds, verdict strings, minimum detectable
effects and synthetic validation are in the module docstring of
[`pairscan_curriculum.py`](pairscan_curriculum.py). Synthetic output:
[`out/pairscan-curriculum-synthetic.json`](out/pairscan-curriculum-synthetic.json). The comparison
itself has not been computed.

## What it asks

[`iita_pairscan.py`](iita_pairscan.py) ([`IITA-PAIRSCAN.md`](IITA-PAIRSCAN.md)) found 12 skill pairs
in 8 of 15 XES3G5M sets with pairwise local dependence beyond one trait. That statistic cannot orient
a pair, and it cannot tell a prerequisite from a trait shared by two skills. This study asks whether
the flagged pairs sit closer together in XES3G5M's expert KC taxonomy than the unflagged pairs of the
same sets. It uses three relations: adjacent (siblings or parent and child), routed before (ancestor
and descendant) and tree distance. Flags are permuted within each set, and the verdict-bearing
control stratifies by difficulty gap and co-attempt count.

Verdicts: `CURRICULUM-LINKED`, `NOT CURRICULUM-LINKED`, `UNDERPOWERED`.

## Known before the run

- **"Routed before" cannot be asked.** No set that holds a flagged pair contains an
  ancestor-descendant pair of skills. The taxonomy has no order among these skills.
- **A null result will read `UNDERPOWERED`, not `NOT CURRICULUM-LINKED`.** With 12 flagged pairs,
  the smallest effect the test detects (80% power, difficulty and co-practice control) is +0.32 in
  adjacency rate, against an expected 0.024, or −0.26 in distance rank. Both are well above the
  +0.10 / −0.10 fixed as meaningful. A reading therefore needs 3 or more of the 12 pairs to be
  adjacent, or the flagged pairs to sit at or below about the 34th distance percentile.
- **The permutation test is calibrated.** On random labels it rejects at 0.026 for adjacency (a
  discrete, conservative count) and 0.053 for distance. It detects planted links, and the control
  removes most of a strong synthetic confound. In the real sets, a flag driven by difficulty gap
  cannot fake a link, because distance is nearly independent of difficulty gap there.

## Reproducing

```
python3 pairscan_curriculum.py --validate   # phase 1, never reads which pairs were flagged
python3 pairscan_curriculum.py              # phase 2, the comparison and verdict
```

## Result

Output: [`out/pairscan-curriculum.json`](out/pairscan-curriculum.json). Verdict: **CURRICULUM-LINKED**
(R1 and R3 enriched in the Holm family, surviving the difficulty-gap × co-attempt control).

| relation | flagged pairs | expected (within-set permutation) | p, plain | p, control |
| --- | ---: | ---: | ---: | ---: |
| R1 adjacent in the taxonomy (same KC, siblings, parent–child) | 0.250 (3 of 12) | 0.024 (control 0.063) | 0.0013 | 0.0275 |
| R3 tree distance, normalised rank within set (lower = closer) | 0.201 | 0.499 (control 0.443) | 0.0002 | 0.0007 |
| R2 ancestor–descendant | 0 of 12 | 0 | — | — |

- The 12 pairs the pair-level test flagged sit much closer together in XES3G5M's expert taxonomy than
  the other pairs in the same sets, and not because they are closer in difficulty or co-attempted by
  more learners (the stratified control holds both).
- R2 cannot speak: the taxonomy is a containment tree with no order among siblings, and no flagged pair
  is ancestor–descendant. So this check says the pairs are curriculum-related, not which comes first.

**What it licenses (fixed in advance, with one caveat).** The flagged pairs are prerequisite-like
candidates consistent with the expert curriculum, not arbitrary artefacts of the fit. Caveat: taxonomy
closeness is also what a topic-specific second trait would produce (two neighbouring skills sharing a
sub-ability), so this result makes "shared trait between unrelated skills" unlikely but does not by
itself separate a prerequisite from a shared topical ability. That separation, and direction, still
need an experiment or an ordered source.
