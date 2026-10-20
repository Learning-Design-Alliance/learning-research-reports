# Does the core-versus-culture result survive without XES3G5M?

**Status:** pre-registered 2026-10-07 at 9cc4075, before any statistic of this design was computed. The
floor passed and the study was run on real data. Script: [`no_xes.py`](no_xes.py). Its docstring holds
the design, the verdict strings, what each outcome means for Paper II, and a note on what had already
been seen.

## What was asked

[`../core-vs-culture/invariance.py`](../core-vs-culture/invariance.py) found **CORE AND CULTURAL**
across four corpora: XES3G5M, ASSISTments 2012-13, Eedi and Junyi 2020.
- Pooled b_other was +0.125 [+0.091, +0.158].
- Pooled b_prox was +0.363 [+0.326, +0.401].

Every unit's Common Core cluster was coded from its name by a language model (openai/gpt-6-sol). The
blind human check of that map (human:david-porcaro, 87 items) passed narrowly, at κ 0.606
[0.493, 0.709] against a bar of 0.60. XES3G5M was its weakest corpus, at κ 0.464, and there the two
models agree with each other most (0.825). The maintainer asked whether the headline depends on the
leg that the map handles worst.

**What had already been seen.** The six per-corpus-pair coefficients without XES3G5M are already
printed in `invariance-result.json`, so the new pooled point estimate is their mean and was not
blind. The bootstrap interval, the permutation null and the verdict were new, and so was everything
below.

## Data

The script reads no corpus. It uses committed aggregates:
- `../core-vs-culture/out/invariance-pairs.json` for the primary map. `core-vs-culture-linking`
  recomputed these pair statistics from the raw ASSISTments, Eedi, Junyi and XES3G5M exports and matched
  them exactly.
- `../core-vs-culture-linking/out/linking-pairs.json` for the second map.
- `unit-map.json` and `human-codes.json`.

Pair statistics are computed separately for each corpus, so dropping XES3G5M changes no other
corpus's numbers.

## Floor ([`out/no-xes-synthetic.json`](out/no-xes-synthetic.json))

The floor used synthetic values on the reduced design's real cluster-pair key structure: 1,460 pairs
in the union and 6 ordered corpus pairs. It used 500 draws per world.

- **F0.** The faster instrument (`linking.cross_multi`) equals `invariance.cross`.
- **F1 calibration: passes.** A core was falsely claimed in 1 of 40 core-free worlds (the bar is ≤ 4).
  A planted core of 0.5 was found in 40 of 40 worlds. Culture was falsely claimed in 2 of 40.
- **F2 power at three corpora** (20 worlds per cell, core effect 0.3):
  - 0.10 at 60 shared pairs, 0.20 at 150 and 0.80 at 300.
  - At core 0.5: 0.60, 0.90 and 1.00 at the same counts.
  - On the real key structure at 0.3: 1.00.
  - The power bar is therefore 300 shared pairs, the same as the committed four-corpus table.

## Result (1), primary: **CORE AND CULTURAL** ([`out/no-xes-result.json`](out/no-xes-result.json))

The run used ASSISTments, Eedi and Junyi 2020 under the primary map. Each pooled coefficient is the
mean over 6 ordered corpus pairs. Intervals are percentile 95% intervals from 2,000 joint bootstraps
that resample cluster pairs from the union of shared pairs. The null comes from 2,000 joint
permutations of each corpus's D (invariance.py CHANGE 1, seed as committed).

| | without XES3G5M | four corpora (committed) |
| --- | --- | --- |
| b_other (carried from another country) | **+0.147 [+0.108, +0.186]** | +0.125 [+0.091, +0.158] |
| b_prox (local teaching proximity) | **+0.351 [+0.307, +0.392]** | +0.363 [+0.326, +0.401] |
| null 97.5th for b_other | +0.027 | +0.022 |
| ratio b_other / b_prox | 0.418 [0.299, 0.564] | 0.344 |
| verdict | CORE AND CULTURAL | CORE AND CULTURAL |

- **The core does not rest on XES3G5M.** Without it, b_other is slightly larger (+0.022, unpaired; the
  unions differ, so no paired interval is claimed). Its lower bound, +0.108, is far above the null's
  97.5th percentile of +0.027. All six corpus pairs are positive, from +0.097 (ASSISTments ← Junyi) to
  +0.228 (Junyi ← Eedi).
- **The local layer is also unchanged:** b_prox moves by −0.012.
- **Pre-registered meaning for Paper II.** The headline does not depend on the leg the map handles
  worst. The paper states the four-corpus result as before and adds that it holds without XES3G5M,
  with these numbers.
- **Order-discordant pairs** (descriptive). There are 518 corpus-pair cases. Cross-country agreement
  in dependence on them averages Spearman 0.142, against 0.215 on concordant pairs. With all four
  corpora it was 0.16 against 0.17, and XES3G5M's pairs had contributed some of the highest
  discordant agreement. Without XES3G5M, the carried-over dependence is weaker where local orders
  disagree, though still positive in all six corpus pairs (0.061 to 0.202).

## Result (3), design size: powered

- **Design.** There are 6 ordered corpus pairs, against 12 with all four corpora. Their shared
  cluster-pair counts are 760 (ASSISTments–Eedi), 768 (ASSISTments–Junyi) and 1,134 (Eedi–Junyi).
- **Power.** The median, 768, is well above the 300-pair bar, so the reduced design is powered. The
  UNDERPOWERED rule did not apply, because the verdict was not NEITHER.

## Result (2), secondary: human confirmation (descriptive; it cannot be a verdict)

A cluster counts as *confirmed* if at least one of the 87 coded units has a human code equal to its
primary-map code, and that code is not NONE. 40 items meet this: XES3G5M 4, ASSISTments 16, Eedi 11 and
Junyi 9. They confirm 28 distinct clusters.

The table covers each corpus's shared cluster pairs. Those are the reduced design for the three
remaining corpora, and the four-corpus design for XES3G5M, which is included for reference.

| corpus | shared pairs | distinct clusters (confirmed anywhere) | both clusters confirmed anywhere | at least one | both confirmed in this corpus | at least one, in this corpus |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ASSISTments | 927 | 48 (25) | 0.311 | 0.818 | 0.069 | 0.483 |
| Eedi | 1,293 | 57 (26) | 0.220 | 0.727 | 0.036 | 0.343 |
| Junyi 2020 | 1,301 | 59 (26) | 0.194 | 0.704 | 0.022 | 0.309 |
| XES3G5M (ref.) | 848 | 48 (20) | 0.184 | 0.689 | 0.004 | 0.142 |

- **How much of the design touches a checked cluster.** About 70% to 82% of the pairs the verdict
  rests on involve at least one cluster that a person independently produced somewhere. Only 19% to
  31% involve two.
- **Within-corpus confirmation is thin.** It is thinnest for XES3G5M, where 3 clusters are confirmed
  by its own units.
- **Unconfirmed is not the same as wrong.** The sample is 25 units per corpus, drawn uniformly over
  units, so most clusters were never shown to the coder. These shares describe how much of the design
  a human has touched. They are not an estimate of how much of it is right, and no re-weighting was
  attempted.

## Descriptive: second map, and dropping each corpus in turn

- **Second map** (deepseek/deepseek-v4-pro), without XES3G5M: CORE AND CULTURAL. b_other is +0.161
  [+0.121, +0.203], b_prox +0.359 [+0.316, +0.398], the null +0.024, and the ratio 0.448. The median
  shared count is 734.
- **Leave one corpus out** (primary map). Every one of the four reduced designs gives CORE AND
  CULTURAL:

| dropped | median shared | b_other | b_prox | ratio |
| --- | ---: | --- | --- | --- |
| XES3G5M | 768 | +0.147 [+0.108, +0.186] | +0.351 [+0.307, +0.392] | 0.418 |
| ASSISTments | 804 | +0.144 [+0.102, +0.189] | +0.385 [+0.345, +0.424] | 0.373 |
| Eedi | 768 | +0.093 [+0.048, +0.140] | +0.300 [+0.246, +0.349] | 0.312 |
| Junyi 2020 | 395 | +0.116 [+0.065, +0.169] | +0.416 [+0.359, +0.466] | 0.278 |

  Dropping XES3G5M is not special. It raises b_other slightly, and dropping Eedi lowers it the most.
  No single corpus carries the verdict.

## What it cannot say

- It does not show that the three remaining corpora are mapped correctly. Their κ against one human
  coder is 0.525 to 0.668, and Junyi's is also below the 0.60 bar.
- No second human coder has yet given a human-human ceiling.
- It cannot separate a cognitive core from a mathematics-education culture the countries share, which
  is invariance.py's limit.
- With three corpora, the pooled estimate rests on three unordered corpus pairs.

## Reproducing

```
python3 no_xes.py --synthetic   # floor, about 3 min
python3 no_xes.py analyse       # about 2 min; reads committed aggregates only
```
