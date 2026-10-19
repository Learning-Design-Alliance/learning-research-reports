# Is there a structure under the skill graph, or only a culture?

**Status: pre-registered 2026-09-27 (0d7def1); all three run; map frozen before learner data at d4acbb0.** Each script's docstring holds its design,
verdict strings and thresholds, committed before any statistic of that design was computed.

## What it asks

The end-to-end study found real structure (content-specific skill tags predict learners; random tags
do not) but not a unique one: differently cut skill sets fit about equally well, experts agree poorly,
and the order seen in learner data follows the curriculum. One reading: a sparse core of dependencies
that hold across cultures (logical, physical, cognitive), inside a large layer of grain, grouping and
order that each curriculum chooses. Three tests on data already held:

| script | question | data |
| --- | --- | --- |
| [`rashomon.py`](rashomon.py) | how many different carvings fit learners equally well, and does content beat a difficulty-only carving? | XES3G5M |
| [`invariance.py`](invariance.py) | does the dependence between two skills follow the local curriculum, or carry across curricula? | XES3G5M (China), ASSISTments (US), Eedi (UK), Junyi (Taiwan) |
| [`order_swap.py`](order_swap.py) | when topics with no logical dependency are taught in random orders, does order matter? | ASSISTments PSABANRN (mean, median, range, mode; four orders) |

Prior work: [`docs/literature/CORE-VS-CULTURE.md`](../../../docs/literature/CORE-VS-CULTURE.md). No
source found states this synthesis for skill structure, and the cross-curriculum test has not been
run in this form. The nearest precedents are Sarama and Clements' hierarchic interactionalism and
Pienemann's teachability hypothesis in second-language learning.

## What it cannot say

The invariance test separates dependence tied to one curriculum from dependence that carries across
four. It cannot separate a cognitive core from a mathematics-education culture the four countries
share. The order test covers one set of topics on one platform, with problems to mastery, not a
delayed test, as the outcome.

## Reproducing

```
python3 rashomon.py
python3 order_swap.py
python3 invariance.py --synthetic
python3 invariance.py map          # about $3 of model calls; commit out/unit-map.json
python3 invariance.py analyse
```

## Result: rashomon.py — NON-UNIQUE CARVING, CONTENT MATTERS

Output: [`out/rashomon-result.json`](out/rashomon-result.json). XES3G5M, 3,630 held-out learners.

| carving | tags per question | AUC |
| --- | ---: | ---: |
| C3 built nodes, all tags | 1.74 | 0.7989 |
| C6 expert tags + tagger's extra KCs | 2.18 | 0.7984 |
| C2 expert, depth 3 | 1.11 | 0.7976 |
| C5 tagger's expert KCs | 1.66 | 0.7975 |
| C4 built primary node | 1.00 | 0.7971 |
| C1 expert leaf KCs | 1.16 | 0.7965 |
| C7 difficulty bins (341) | 1.00 | 0.7921 |
| C8 random partition | 1.00 | 0.7920 |
| no skills (M1) | — | 0.7919 |

- **Non-unique.** The two carvings within 0.001 AUC of the best (C3, C6) group questions differently:
  adjusted Rand index 0.36 between their primary partitions. At 0.002, five carvings qualify, with
  pairwise agreement as low as 0.21.
- **Content matters.** Every carving in the set beats the difficulty-only and random carvings (C3 vs
  C7 +0.0068 [+0.0064, +0.0072]); difficulty bins and random groups add almost nothing over no skills
  (+0.0002, +0.0001).
- **A small shared core.** Of question pairs grouped together by either of the two best carvings,
  22% are grouped together by both; across the five within 0.002, 4%.

Reading: the structure is real, since content-based groupings predict and content-free ones do not,
but its description is not unique, and what the equally good descriptions share is a small fraction
of what each asserts.

## Result: order_swap.py — ORDER MATTERS (for efficiency, not for completion)

Output: [`out/order-swap-result.json`](out/order-swap-result.json). 1,192 students randomised to four
orders of mean, median, range and mode (ASSISTments PSABANRN). Prior correctness balanced (0.59-0.62).

| arm | n | completed | problems to mastery | correct rate |
| --- | ---: | ---: | ---: | ---: |
| T1 | 320 | 0.772 | 6.51 | 0.586 |
| T2 | 314 | 0.780 | 7.16 | 0.629 |
| T3 | 266 | 0.774 | 8.01 | 0.610 |
| T4 | 292 | 0.801 | 6.93 | 0.625 |

- **Completion does not depend on order** (omnibus p 0.82; pairwise differences within about 0.085).
- **Problems to mastery does** (omnibus p 0.003): T3 needs 1.5 more problems than T1 [0.8, 2.2] and
  1.1 more than T4, about 23% more practice. By the pre-registered rule the verdict is ORDER MATTERS.
- The release does not say which treatment is which order, so the better orders cannot be named.

Reading: topics with no logical dependency were not interchangeable in cost. Learners reach mastery
in any order, but some orders take more practice, plausibly through transfer or interference between
related measures. The chosen layer is not free; its choices change efficiency even where they do not
change attainment. One topic set, one platform, and problems to mastery rather than a delayed test.

## Result: invariance.py — CORE AND CULTURAL

Output: [`out/invariance-result.json`](out/invariance-result.json), per-pair statistics in
[`out/invariance-pairs.json`](out/invariance-pairs.json). Unit names were mapped to 92 Common Core K-8
clusters ($2.10); about 75% of units mapped; the two mapping models agree on 61% of units. Cluster
pairs per corpus: XES3G5M 930, ASSISTments 972, Eedi 1,531, Junyi 2,604; shared pairs per corpus pair
273 to 1,134, so power is high (synthetic: >= 0.9 at 300 shared pairs for an effect of 0.3).

| | primary map | second map |
| --- | --- | --- |
| dependence carried from another country's platform (b_other) | +0.125 [+0.091, +0.158] | +0.155 [+0.120, +0.194] |
| local teaching proximity (b_prox) | +0.363 [+0.326, +0.401] | +0.360 [+0.308, +0.404] |
| permutation null for b_other, 97.5th | +0.022 | +0.025 |

- **A core carries across curricula.** How strongly two skills depend on each other on one country's
  platform predicts it on another's, beyond how close the two are taught locally. All 12 corpus pairs
  are positive under the primary map (+0.06 to +0.23).
- **The local layer is larger.** Skills taught close together locally depend on each other about three
  times as strongly as the cross-country carry-over (standardised coefficients 0.36 vs 0.13).
- **It mostly survives where local orders disagree.** On cluster pairs one platform teaches in one
  order and another in the reverse (1,326 corpus-pair cases), cross-country agreement in dependence is
  similar to agreement on concordant pairs under the primary map (mean Spearman 0.16 vs 0.17) and
  lower under the second (0.12 vs 0.22; one corpus pair negative).

What this cannot separate: a cognitive core from a mathematics-education culture the four countries
share. The order-discordant pairs are the closest it comes, and there the carried-over dependence
largely holds. Name-only mapping is noisy, which biases b_other toward zero.

## Result: human_codes.py — MAP VALIDATED (narrowly)

Pre-registered at a528af0 and 4c8e603 (second coder), before any code was returned. Coder:
human:david-porcaro, blind to both model maps, working from names alone (Chinese names with a
literal machine translation). Outputs: `out/human-codes.json` (item, corpus, unit id, code; no names),
`out/human-agreement.json`.

| | n | κ, human vs primary map (gpt-6-sol) | κ, human vs second map (deepseek) | κ, map vs map, same items | raw agreement, same domain |
| --- | ---: | ---: | ---: | ---: | ---: |
| All coded items | 87 | **0.606 [0.493, 0.709]** | 0.560 | 0.710 | 0.759 |
| ASSISTments 2012-13 | 25 | 0.620 | 0.582 | 0.706 | 0.80 |
| Eedi | 24 | 0.668 | 0.563 | 0.702 | 0.75 |
| Junyi 2020 | 20 | 0.525 | 0.520 | 0.581 | 0.75 |
| XES3G5M | 18 | 0.464 | 0.445 | 0.825 | 0.72 |
| English-named (ASSISTments, Eedi) | 49 | 0.656 | | | |

The interval is a 2,000-draw bootstrap of items within corpus. The pre-registered verdict is **MAP
VALIDATED** (κ ≥ 0.60 with lower bound ≥ 0.40), passing the point bar by 0.006. 13 of 100 items were
left blank and excluded, as registered: 7 XES3G5M, 5 Junyi, 1 Eedi. Read with the human coder's
cluster agreement with the primary map at domain grain, 0.759, and at grade.domain, 0.667.

Descriptive, not registered:
- Reading the 13 blanks as NONE gives κ 0.549 over 100 items, below the bar. The verdict rests on
  the registered rule, which excludes blanks; the paper reports both.
- The two models agree with each other (κ 0.710) more than either agrees with the human, most
  sharply on XES3G5M (0.825 against 0.464). Agreement between two models is not evidence that the
  map is right; it is what correlated errors would also produce.
- Items the coder marked unsure (22) agree less (κ 0.532) than the rest (65, κ 0.624).
- The coder's account (2026-10-07): ASSISTments skills were the clearest, because the platform
  aligned them to Common Core; Eedi's (UK) were close but sometimes covered content outside the
  Common Core; XES3G5M's were "nearly impossible" because names were unclear or a unit spanned
  several standards. A unit that spans several clusters has no single right code, so part of the
  XES3G5M disagreement is the construct, not the coder or the model.

For comparison (literature review, strand 6): trained raters aligning full test items reached κ
0.55-0.58 across 57 topics and 0.71-0.74 across 10 categories (Herman, Webb & Zuniga 2007). A
second human coder on the same 100 items (registered, not yet run) would give this study's own
human-human ceiling.

## Across the three tests

The structure is real (content predicts; difficulty-only and random carvings do not), its
description is not unique (equally good carvings share 4-22% of their groupings), part of it carries
across four national curricula, and a larger part follows local teaching. Order among topics with no
logical dependency still changes how much practice learners need, though not whether they master.

## Follow-ups (pre-registered at b24bb02)

The three scripts were started about a minute before that commit (a lint failure blocked the first
commit); no output had been read.

**core_producer.py — PRODUCER FINDS THE CORE; CRITIC ADDS NOTHING.** A two-family panel, blind to
learner data, rated 811 cluster pairs for dependence "because of the mathematics itself". Its ratings
correlate with the empirical core (dependence shared across countries after local proximity is
removed) at Spearman 0.31 [0.25, 0.38], above the best simple cue (same domain, 0.21; panel minus cue
lower bound +0.02). The panel also correlates 0.28 with local proximity, so it partly mistakes the
local layer for the core. A critic's kept pairs score +0.16 higher on the core than its rejected
ones, but the interval spans zero ([-0.04, +0.36], 162 pairs). $1.33.

**prior_split.py — LOCAL LAYER LARGER FOR LOW-PRIOR LEARNERS; core no different.** Within each corpus,
learners below the median of overall accuracy lean more on local teaching proximity (b_prox 0.35)
than learners above it (0.27; difference -0.09 [-0.14, -0.03]). The carried-over core does not differ
(0.11 vs 0.08, interval spans zero). Learners with gaps depend more on how things are taught together.

**language.py — CORE AND CULTURAL, dominated by the core.** English grammar across Duolingo's courses
for Spanish, Portuguese and Italian speakers (31,735 / 8,637 / 3,436 learners): dependence between
grammatical forms carries across courses at b_other +0.63 [+0.55, +0.69]; review proximity +0.05.
The ratio (11 to 1, against mathematics' 1 to 3) is not a fair comparison: the three courses share
one company's design, and proximity here is review scheduling, not first teaching. What it does show
is that the dependence structure among grammatical forms is nearly the same for speakers of three
first languages, as Pienemann's developmental-sequence account predicts.

## Other domains

**Writing ([WRITING.md](WRITING.md), pre-registered at 558c80e).**
- PERSUADE argumentative essays. Whether one element of an argument is well written goes with whether
  another is, and that link is largely the same across prompts (invariance share 0.86 [0.56, 1.35]),
  tasks (0.90) and grade bands (0.80): INVARIANT. The ELL comparison is uninformative.
- The order of elements is shared across every prompt. Of the 9 orders with enough violators to test,
  2 cost holistic score: MOSTLY CONVENTIONAL (share 0.22).
- Raters' trait structures differ (ELLIPSE, share 0.41), which is a property of raters, not learners.

**Procedures ([`../../procedures/core-vs-culture/`](../../procedures/core-vs-culture/README.md),
pre-registered at ed793f6).**
- Assembly101: skipping a consensus step raises failure of the later step from 10% to 22%: CORE
  PRESENT. About a third of testable orders look necessary (0.32 [0.00, 0.45]).
- Ego-Exo4D site-invariant orders: UNDERPOWERED.

**Reading across domains.** Mathematics, grammar, writing and assembly all show a shared dependence
structure together with a large conventional layer of order. Where order has a cost, it is where the
task makes one step's product the next step's input: physical parts in assembly, the position an
argument's evidence must support. The core share of order is modest everywhere measured (about 0.2-0.3).
