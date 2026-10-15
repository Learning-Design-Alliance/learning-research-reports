# Is the cross-curricular core partly shared language?

**Status:** pre-registered 2026-10-08 at fb8cd9e; floor run at 41fe7a4 (calibration passed, power
failed); real run once. Script: [`language_split.py`](language_split.py). Its docstring holds the
design, the estimand, the reference distribution, the verdict strings and what each outcome means for
Paper II 5.5.

**Verdict: UNDERPOWERED.** The secondary pre-registered statement is **CROSS-LANGUAGE CORE HOLDS**.

## What was asked

[`../core-vs-culture/invariance.py`](../core-vs-culture/invariance.py) found **CORE AND CULTURAL**
across four corpora: pooled b_other +0.125 [+0.091, +0.158] and b_prox +0.363 [+0.326, +0.401]. The
four corpora form two language pairs:
- English: ASSISTments 2012-13 (US) and Eedi (UK).
- Chinese: XES3G5M (mainland China) and Junyi 2020 (Taiwan).

The literature sweep (`research/readiness/learning-graph-budget-2026/literature-sweep-2.md`, C.12,
Gökçe et al. 2021) reports that differential item functioning in TIMSS grows with linguistic and
cultural distance. If part of the "core" is shared language, b_other should be larger on the 4
same-language ordered corpus pairs than on the 8 cross-language ones.

**What had already been seen.** All 12 per-pair coefficients are printed in
`invariance-result.json`, and the author read them before writing the design. The point estimates
below are means of those coefficients and were not blind. The equivalence margin M = 0.0625 was set
knowing the point was near zero. The intervals, the floor and the verdict were new.

## Coder of the construct

Every unit's Common Core K-8 cluster was coded **by a language model from the unit's name**:
- openai/gpt-6-sol made the primary map, which bears the verdict.
- deepseek/deepseek-v4-pro made the second map, which is descriptive only.

Both maps are in `../core-vs-culture/out/unit-map.json`, and the prompt is `invariance.MAP_PROMPT`.

The blind human check (coder human:david-porcaro, 87 items, `human_codes.py`) returned MAP VALIDATED
narrowly, at **κ 0.606 [0.493, 0.709]** against a bar of 0.60. It was weakest on XES3G5M (0.464). No
second human coder has been run, so there is no human-human ceiling yet. No model was called here.

The mapper reads Chinese and English names. If its errors depend on the language, two same-language
corpora share mapping error. That is a threat specific to this question, and the second map is also
a model map, so it cannot control for it.

## Design (summary; the docstring is the record)

**Model.** invariance.py fits one OLS per ordered corpus pair and pools the 12 by their mean. The
language label belongs to a whole regression, so there is no pooled model to hold an interaction
term. The estimand is the split of that mean:
- b_same is the mean b_other over the 4 same-language ordered pairs.
- b_cross is the mean over the 8 cross-language pairs.
- DELTA = b_same − b_cross. A positive value means the core is larger within a language.

Each corpus appears once as the dependent and once as the source among the same-language
regressions. So additive corpus effects, such as one platform being noisier, cancel in DELTA.

**Interval.** As in invariance.py: 2,000 joint bootstraps of cluster pairs from the union of shared
pairs, with one draw serving all 12 regressions. Percentile 95% intervals. This resamples cluster
pairs conditional on the four corpora. Check R0 confirmed that the instrument reproduces the committed
invariance.py interval and null exactly.

**Reference distribution.** The label is assigned to corpora. There are exactly **3** ways to pair 4
corpora into two pairs, each giving 4 same and 8 cross ordered pairs:
- LANGUAGE: {XES3G5M, Junyi} and {ASSISTments, Eedi}.
- ALT-1: {XES3G5M, ASSISTments} and {Eedi, Junyi}.
- ALT-2: {XES3G5M, Eedi} and {ASSISTments, Junyi}.

The two alternatives are the reference. Three labellings cannot give a rank p-value below 1/3, so the
control is an interval contrast instead. SPEC = DELTA_LANGUAGE − max(DELTA_ALT), computed on the same
draws. A language reading requires the language pairing to beat both other pairings.

## Floor ([`out/language-split-synthetic.json`](out/language-split-synthetic.json))

The synthetic worlds used the real key structure: 12 ordered pairs, 273 to 1,134 shared pairs, and
1,891 in the union. They were generated as D = 0.40·core + bonus·language-shared + 0.42·P + noise, and
with no bonus they reproduce the real sizes (pooled b_other 0.124). Each world used 500 draws, and
each cell had 20 worlds.

| world | mean DELTA (language) | verdicts |
| --- | ---: | --- |
| no bonus | −0.005 | UNDERPOWERED 16, NO LANGUAGE DIFFERENCE 3, cross-language not specific 1 |
| bonus 0.42 on language | +0.110 | **WITHIN A LANGUAGE 15**, within not specific 4, UNDERPOWERED 1 |
| bonus 0.30 on language | +0.070 | WITHIN A LANGUAGE 7, within not specific 6, UNDERPOWERED 7 |
| bonus 0.42 on ALT-1 | −0.046 | cross-language not specific 8, UNDERPOWERED 11, NO LANGUAGE DIFFERENCE 1 |

- **Calibration passes.** No world without a language bonus produced a within-language verdict: 0 of
  20 with no bonus, and 0 of 20 with the bonus planted on another pairing.
- **Direction is right.** A bonus planted on ALT-1 drives the language DELTA negative.
- **Power fails.** A planted DELTA of 0.11 was found in 15 of 20 worlds, against a bar of 16. The
  instrument reached NO LANGUAGE DIFFERENCE in only 3 of 20 null worlds. By the pre-registered rule, a
  NO LANGUAGE DIFFERENCE would have read UNDERPOWERED.

## Result ([`out/language-split-result.json`](out/language-split-result.json)), primary map

| | estimate | 95% interval |
| --- | ---: | --- |
| b_same (4 same-language ordered pairs) | +0.121 | [+0.068, +0.176] |
| b_cross (8 cross-language ordered pairs) | +0.127 | [+0.088, +0.166] |
| permutation null for b_cross, 97.5th | +0.030 | |
| **DELTA = b_same − b_cross** | **−0.006** | **[−0.067, +0.055]** |
| DELTA / 3 as a share of the pooled core | −2% | [−18%, +16%] |
| SPEC = DELTA − max(alternatives) | −0.019 | [−0.138, +0.067] |

| pairing | same-pair mean | DELTA |
| --- | --- | --- |
| LANGUAGE | +0.121 [+0.068, +0.176] | −0.006 [−0.067, +0.055] |
| ALT-1 | +0.134 [+0.078, +0.191] | +0.013 [−0.058, +0.083] |
| ALT-2 | +0.120 [+0.066, +0.176] | −0.007 [−0.068, +0.055] |

Across the bootstrap draws, the language pairing ranked first of the three in 25% of draws, second in
36% and third in 39%.

- **Verdict: UNDERPOWERED.** The DELTA interval contains zero. Its upper end, +0.055, is inside the
  margin of 0.0625, but its lower end, −0.067, is just outside it. The pre-registered rule therefore
  reads UNDERPOWERED. The floor's power failure would have given the same reading for a NO LANGUAGE
  DIFFERENCE result. As pre-registered for Paper II 5.5, the design cannot tell, and 5.5 says so.
- **The direction C.12 predicts is not seen.** The point estimate is slightly negative. The
  language pairing does not stand out from the other two pairings (SPEC is negative and its interval
  is wide). This is a description of the interval, not a verdict: the 95% interval excludes a
  same-language excess above +0.055, which would be about 15% of the pooled core (0.055 / 3 / 0.125).
- **Cross-language core holds** (secondary, pre-registered). Using only the 8 cross-language pairs,
  b_cross is +0.127 [+0.088, +0.166], far above its null's 97.5th percentile of +0.030. The core does
  not need the same-language pairs.

Per unordered corpus pair (the mean of both directions; descriptive):

| pair | language | b_other |
| --- | --- | --- |
| Eedi–Junyi | cross | +0.195 [+0.146, +0.242] |
| ASSISTments–Eedi | same | +0.140 [+0.067, +0.216] |
| Eedi–XES3G5M | cross | +0.135 [+0.041, +0.224] |
| ASSISTments–Junyi | cross | +0.106 [+0.046, +0.164] |
| Junyi–XES3G5M | same | +0.102 [+0.028, +0.180] |
| ASSISTments–XES3G5M | cross | +0.073 [−0.035, +0.181] |

## Descriptive: second map (deepseek/deepseek-v4-pro)

This is not verdict-bearing. Here the cross-language pairs carry *more* than the same-language ones:
- b_same is +0.095 [+0.045, +0.146] and b_cross is +0.186 [+0.141, +0.232].
- DELTA is −0.091 [−0.156, −0.029].

The rule reads CROSS-LANGUAGE EXCESS, NOT SPECIFIC TO LANGUAGE. ALT-1 has the largest DELTA, +0.120
[+0.057, +0.186], driven by ASSISTments–XES3G5M at +0.302. The language pairing ranks last in 86% of
draws. The two Chinese corpora agree least under this map: Junyi–XES3G5M is +0.019 [−0.063, +0.101].

The two maps disagree about which corpus pairs carry the core, so pair-level affinities here are
sensitive to the map. Neither map shows the same-language excess C.12 predicts.

## What it cannot say

- Language is confounded with region and national tradition (US/UK against mainland China/Taiwan),
  and with the mapper's reading of each language.
- There are two language pairs, so this is one contrast on four corpora, not a gradient of linguistic
  distance.
- The bootstrap resamples cluster pairs, not corpora. The pairing contrast is the only corpus-level
  control, and three pairings are all there are.
- The construct is model-coded, with human κ 0.606 against one coder.

## Reproducing

```
python3 language_split.py --synthetic   # floor, about 6 min
python3 language_split.py analyse       # about 1 min; reads committed aggregates only
```

The script reads no corpus. It reads `../core-vs-culture/out/invariance-pairs.json` (primary map) and
`../core-vs-culture-linking/out/linking-pairs.json` (second map). core-vs-culture-linking's check R0
recomputed these statistics from the raw ASSISTments, Eedi, Junyi and XES3G5M exports and matched
them.
