# Paper VI's human ceilings: two robustness checks (stratified agreement; Gwet's AC2)

**Status: RUN 2026-10-06.** Pre-registered at b1b954d, before any grader mark was read. No model calls. Design, thresholds, verdict strings and the
detection floor are in `robustness.py`'s docstring, which is the primary record. The floor
(`out/floor.json`, rev 1) and the AC2 self-test (`out/selftest.json`) passed before this commit and
before any grader mark was read. Results go below a line; nothing above it will be rewritten.

## What is asked

The Paper VI literature review (`research/readiness/ai-grader-reliability-2026/literature.md`, 5a.6
and 5b.3) suggested two optional checks for release `ai-grader-reliability-2026` 1.0.0
(`research/article/attainment-bias-in-llm-grading.md`):

1. **Agreement stratified by whether the humans agreed** (Elangovan et al. 2025). Paper VI §1.2
   argues that "a substantial share of the residual disagreement between a grader and a single human
   reference is noise in the reference", so agreement is "a blunt instrument". Does the grader look
   better where the humans agree, and does the argument survive?
2. **Gwet's AC2 beside each kappa** (Albatarni & Elsayed 2026). Kappa takes chance agreement from the
   marginals; AC2 is less sensitive to skewed marginals. Do the human ceilings (Mohler 0.519;
   Menagerie 0.465 on 5 levels, 0.424 on 14, per-pair 0.035–0.730) and the grader-vs-human
   comparisons survive the change of statistic?

## Data

Registered corpora `mohler-asag` (the analysed `mohler_en.csv`, 1,727 rows) and `menagerie-grades`
(`grades.csv`), for per-rater grades; grader marks from the `grader-label-stability` per-case dumps
(verified against `grader-eval/analyses/per-case-dumps.sha256`): Mohler 300 answers / 62 questions
and Menagerie 60 programs × 4 dimensions, each graded by Gemini 3.5 Flash Lite, GPT-4.1-mini and
Qwen3-235B under a high and a low attainment label. Those are labelled marks; the labels were
assigned independently of rater agreement, so they balance across the strata. The 150-answer run
behind the paper's 0.549 / 0.798 / 0.711 kept no per-case dump, and its draw does not re-derive from
the current harness (re-derived rater-vs-rater 0.478, not 0.608), so those three figures are not
re-scored here. No new derived input; nothing is added to `data/data-sources.json`.

## Pre-registered design (summary; the docstring governs)

**Strata.** Mohler: the two raters gave the same mark (121 of 300 agree). Menagerie: all raters
within a range of 3 fine levels on the 14-level scale (86 of 240 agree). "All within one level"
leaves 18 items and fails positivity; range ≤ 3 matches Mohler's agree share (36% vs 40%).
Ranges ≤ 2 and ≤ 4 reported as sensitivity.

**T1 verdicts** (clusters: Mohler questions, Menagerie submissions; 4,000 resamples):

- **P1** D = level-standardised MAE where humans disagree minus where they agree, grader against a
  single human, as a share of the range. `GRADER-BETTER-WHERE-HUMANS-AGREE` (95% interval > 0),
  `GRADER-WORSE-WHERE-HUMANS-AGREE` (< 0), `NO-DIFFERENCE` (90% interval within ±0.03 of the range),
  else `UNRESOLVED`. Control: stratum labels deranged within level bin (same sizes, same level mix).
- **P2** ρ = (MSE human–human / 2) / MSE grader–human: the share of the grader's squared error against
  one human that is that human's own noise. `SHARE-SUBSTANTIAL` (95% interval > 0.25),
  `SHARE-MINOR` (< 0.25), else `SHARE-UNRESOLVED`.
- **P3** (reported only after floor rev 0): Menagerie leave-two-out decomposition of the grader's own
  error across strata.
- **Reference swing** (Mohler): QWK(g, rater 2) − QWK(g, rater 1), against the 0.05 that bounds every
  intervention's movement of agreement in Paper VI.
- **Overall**: `BLUNT-INSTRUMENT-SUPPORTED` if P1 BETTER in ≥ 4 of 6 model × corpus cells, P2
  SUBSTANTIAL in ≥ 4 of 6, and the swing exceeds 0.05 on ≥ 2 of 3 models;
  `BLUNT-INSTRUMENT-WEAKENED` if P1 BETTER in ≤ 2, or P2 MINOR in ≥ 4, or the swing exceeds on none;
  else `BLUNT-INSTRUMENT-PARTLY`.

**T2 verdict.** AC2 (quadratic weights over the scale's levels) beside each QWK, with a bootstrap over
items. A ceiling's level is `STATISTIC-DEPENDENT` if the 95% interval of AC2 − QWK lies wholly
beyond ±0.10, `ROBUST` if inside. An ordering (grader–human vs human–human; the reference swing)
`FLIPS` if the AC2 difference's interval excludes 0 on the side opposite the QWK difference. The
per-pair spread is `ROBUST` if the AC2 range is at least half the QWK range. `CEILING-ROBUST` if
every level is ROBUST, nothing flips and the spread is ROBUST; `CEILING-STATISTIC-DEPENDENT (…)`
naming what moved if any level is STATISTIC-DEPENDENT, any ordering flips or the spread is not
robust; else `CEILING-UNRESOLVED`.

**What each verdict would mean for Paper VI (written before the run):**

- `BLUNT-INSTRUMENT-SUPPORTED` → §1.2's reference-noise sentence has a direct measurement behind it
  on both two-rater corpora and can cite this study; §5.1 can report the stratified table.
- `BLUNT-INSTRUMENT-PARTLY` → the paper keeps the argument but states which leg (stratified gradient,
  noise share, or reference swing) the data on disk support and which they do not.
- `BLUNT-INSTRUMENT-WEAKENED` → §1.2's premise ("a substantial share … is noise in the reference")
  must be softened or withdrawn; the bias-first design still stands on its own grounds (an offset
  barely moves QWK, §4.6), which this study does not test.
- `CEILING-ROBUST` → AC2 goes beside each kappa in §5.1 as a one-line robustness note.
- `CEILING-STATISTIC-DEPENDENT` on level only → the comparisons survive, but "humans agree at 0.52"
  is a kappa figure, not a fact about agreement: §5.1 must give AC2 beside it and say the level
  depends on the statistic. On an ordering flip → the comparison that flipped cannot be stated
  without naming the statistic, and §5.1's reading of it must change.

## Detection floor (passed before this commit)

Synthetic two-rater (Mohler) and four-rater (Menagerie) data on the real draws' clusters and level
mix, integer marks, 200 replicates × 2,000 resamples. Rev 0 failed on P3's power and on
answerability of a Mohler null (record in the docstring); rev 1 demotes those to reported. See
`out/floor.json`. Rev 1 (passed):

| world | planted | Mohler | Menagerie |
| --- | --- | --- | --- |
| W0 | no reference noise; strata at random | P1 BETTER 3% (NO-DIFFERENCE 45%) | BETTER 5% (NO-DIFF 65.5%) |
| W1 | independent rater noise | P1 BETTER 88%; ρ 0.452 vs planted 0.452, coverage 97.5% | BETTER 90.5%; ρ 0.481 vs 0.480, coverage 100% |
| W2 | ambiguous items (rater noise ×2.5 on a third) | BETTER 98% | BETTER 100% |
| W3 | W2 and the grader ×2 on the same items | BETTER 98.5% | BETTER 100% |
| RHO10 / RHO50 | planted ρ 0.10 / 0.50 | MINOR 97.5% / SUBSTANTIAL 100% | MINOR 100% / SUBSTANTIAL 100% |

What the floor says about reading P1: it finds planted reference noise, and it does not find it where
there is none (3–5%). It cannot tell reference noise on the disagree items (W2) from items that are also
harder for the grader (W3); P3, built to separate them, had 0–23.5% power, so that question stays open.
A Mohler null would read UNRESOLVED about half the time. These graders were written and scored by this
session: a smoke check of the instrument, not a validation of the real graders.

## AC2 self-test (passed before this commit)

The implementation reproduces the published worked examples of Gwet's irrCAC package exactly:
`cont3x3abstractors` quadratic κ 0.8921569 and AC2 0.9402369; `cac.raw4raters` quadratic pa 0.9753788,
pe 0.7137044, AC2 0.914; unweighted pe 0.1903212, AC1 0.77544. The two-rater and many-rater forms agree;
a planted kappa paradox moves QWK (−0.11) and not AC2 (`out/selftest.json`).

## Reproduce

    export LDA_SCRATCH_DIR=<dir holding mohler/ and menagerie/>   # or MOHLER_DIR, MENAGERIE_DIR
    python3 robustness.py --selftest
    python3 robustness.py --floor --dump-dir <dir holding grader-label-stability/>
    python3 robustness.py --run   --dump-dir <dir holding grader-label-stability/>

---

## Results

Run 2026-10-06, `out/results.json` (`--run`); post-hoc readings in `out/posthoc.json` (`--posthoc`,
added after the run, reported only). Reproduction first: Mohler rater 1 vs rater 2 QWK 0.519 (1,727
rows), Menagerie pooled 0.465 (5 levels) and 0.424 (14), per-pair min / median / max 0.035 / 0.410 /
0.730: the paper's figures, recomputed independently of the harness.

### T1. Stratified by whether the humans agreed — `BLUNT-INSTRUMENT-SUPPORTED`

Grader against a single human, mean absolute error per stratum. D is the level-standardised
difference (disagree minus agree) as a share of the score range; positive means the grader looks
better where the humans agreed. ρ is the share of the grader's squared error against one human that
is that human's own noise. Clustered 95% intervals.

| Corpus, model | MAE agree → disagree | D (primary) | D raw | D vs rater mean | P1 | ρ (P2) |
| --- | --- | --- | --- | --- | --- | --- |
| Mohler (121 / 179), Gemini 3.5 Flash Lite | 0.68 → 1.44 pts | +0.014 [−0.037, +0.072] | +0.153 [+0.100, +0.209] | −0.020 [−0.072, +0.037] | UNRESOLVED | 0.53 [0.44, 0.63] |
| Mohler, GPT-4.1-mini | 1.16 → 1.38 | +0.043 [−0.008, +0.093] | +0.043 [+0.009, +0.080] | −0.004 [−0.053, +0.044] | UNRESOLVED | 0.55 [0.45, 0.66] |
| Mohler, Qwen3-235B | 1.22 → 1.48 | +0.055 [+0.015, +0.088] | +0.052 [+0.020, +0.087] | +0.009 [−0.030, +0.043] | **BETTER** | 0.50 [0.41, 0.61] |
| Menagerie (86 / 154), Gemini | 2.11 → 2.54 levels | +0.045 [+0.029, +0.062] | +0.033 [−0.030, +0.088] | +0.007 [−0.013, +0.027] | **BETTER** | 0.50 [0.37, 0.66] |
| Menagerie, GPT-4.1-mini | 2.37 → 2.43 | +0.057 [+0.045, +0.069] | +0.004 [−0.088, +0.078] | +0.007 [−0.006, +0.020] | **BETTER** | 0.50 [0.32, 0.75] |
| Menagerie, Qwen3-235B | 2.86 → 2.84 | +0.037 [+0.014, +0.060] | −0.002 [−0.049, +0.042] | −0.011 [−0.036, +0.015] | **BETTER** | 0.45 [0.35, 0.57] |

- **P1: 4 of 6 cells BETTER**, exactly the pre-registered bar. Mohler is MIXED (only Qwen resolved);
  Menagerie is BETTER on all three. The deranged control (stratum labels moved to other cases of the
  same level, all 300 / 240 relabelled, 200 derangements) sits at −0.002 to +0.001, with its 95% range
  within ±0.045: the difference is not level mix or composition. Menagerie sensitivity: range ≤ 2 and
  ≤ 4 are BETTER on every model too.
- **Level matters, in opposite directions.** On Mohler the humans agree mostly at 0 and 5, where the
  graders are also right, so the raw gradient (up to 0.15 of the range, on Gemini) shrinks once the
  level is held fixed. On Menagerie the agreed items include whole-F programs that the graders mark
  well above F (Gemini's bias is +1.74 levels where the raters agree), so the raw gradient is near
  zero and the standardised one is positive.
- **Against the rater mean no gradient is resolved** (all six point estimates within ±0.02 of the range, every interval spanning zero, but reaching −0.07 to +0.04 on Mohler and −0.04 to +0.03 on Menagerie, so a gradient the size seen against one human is not excluded; reworded 2026-10-06, scope-audit-6 S2). Against one human it is there. That is what a single rater's own noise would
  produce, but it does not prove it (see P3 below).
- **P2: SHARE-SUBSTANTIAL in all six cells**, ρ 0.45–0.55: about half of each grader's squared error
  against one human is that human's disagreement with the other humans. The independence assumption
  fails in a known direction on Mohler. Rater 1 marks 0.89 points above rater 2 on this draw (0.47 on
  all 1,727 rows), every grader sits below the mean (bias −0.4 to −1.2), and ρ is 0.38–0.41 against
  rater 1 alone and 0.73–0.82 against rater 2 alone. "About half" is the average over the two
  references, not a property of either one.
- **The reference swing replicates on three more models**: QWK(grader, rater 2) − QWK(grader,
  rater 1) = +0.270 [+0.170, +0.378] (Gemini), +0.242 [+0.166, +0.319] (GPT-4.1-mini), +0.231
  [+0.165, +0.292] (Qwen); AC2 +0.28 / +0.25 / +0.25. All three exceed the 0.05 bound on
  interventions. The paper's 0.25 came from one run on another draw that cannot be recovered; this is
  the same size on 300 other answers.
- **P3 (reported only)**: the leave-two-out decomposition is UNRESOLVED on every model (dSG +1.0,
  +1.3, +2.3 squared levels, every interval spanning zero), as the floor said it would be at 60
  programs. **This study does not answer whether the disagree items have a noisy reference or are
  also hard for the grader.** The Elangovan reading (grader–human MAE minus human–human MAE, on held-out
  raters) is about the same in both strata: −0.62 / −0.59 (Gemini), −0.70 / −0.62 (GPT-4.1-mini) and
  −0.12 / +0.11 (Qwen) levels, agree / disagree. On MAE the grader sits nearer each human than the
  humans sit to each other, in both strata; on QWK it is far below them (T2). These data do not show
  Elangovan's pattern.
- QWK and AC2 per stratum are in `out/results.json` (`by_stratum_grader_vs_single_rater`). They are
  not compared across strata, because the agree strata have a wider spread of human marks (SD 1.92
  vs 1.44 points on Mohler), which raises kappa by itself.

Overall: P1 BETTER in 4 of 6 cells, P2 SUBSTANTIAL in 6 of 6, swing above 0.05 on 3 of 3 models →
**BLUNT-INSTRUMENT-SUPPORTED**. P1 sits exactly at its bar, and P2's assumption is visibly strained
on Mohler.

### T2. Gwet's AC2 beside each kappa — `CEILING-STATISTIC-DEPENDENT (level: Mohler, Menagerie 5- and 14-level; spread)`

| Ceiling | QWK | AC2 (quadratic) | AC2 − QWK | Level |
| --- | --- | --- | --- | --- |
| Mohler r1 vs r2, 1,727 answers | 0.519 [0.474, 0.560] | **0.858** [0.839, 0.875] | +0.338 [+0.303, +0.376] (question-clustered [+0.275, +0.405]) | STATISTIC-DEPENDENT |
| Mohler r1 vs r2, the 300-answer draw (stratified on grade) | 0.531 [0.450, 0.610] | 0.562 [0.479, 0.644] | +0.031 [−0.013, +0.088] | ROBUST |
| Menagerie pooled pairs, 5 levels (6,600) | 0.465 [0.311, 0.577] | **0.887** [0.867, 0.906] | +0.422 [+0.311, +0.575] | STATISTIC-DEPENDENT |
| Menagerie pooled pairs, 14 levels | 0.424 [0.295, 0.529] | **0.749** [0.717, 0.778] | +0.324 [+0.225, +0.455] | STATISTIC-DEPENDENT |
| Menagerie many-rater AC2 (1,116 items), 5 / 14 levels | | 0.886 / 0.747 | | |
| Menagerie per pair (42, 14 levels): min / median / max | 0.035 / 0.410 / 0.730 | 0.609 / 0.782 / 0.916 | range 0.695 → 0.307 (0.44×) | spread STATISTIC-DEPENDENT |

The bootstrap is over items (Mohler answers, Menagerie submissions). The intervals on the per-pair
minimum and maximum are percentile intervals on an extreme order statistic, and those are biased (the
QWK minimum's [−0.221, +0.028] does not cover its own point). They are in the JSON and are not used
here. AC2 restricted to the observed categories is identical to three decimals on every ceiling.

**Why the levels move.** It is the kappa paradox. On the full Mohler corpus the marks bunch at the
top (rater means 4.40 and 3.93 out of 5), so kappa's chance agreement is high and its value low. On
the 300-answer draw, stratified to flatten the grade distribution, QWK and AC2 agree (0.531 vs
0.562). The raters and the scale are the same, so the level of "the human ceiling" belongs to the
statistic and the sample's marginals, not only to the humans.

**Orderings: none flips.** Per model, grader–human minus human–human on the same rows:

| | Gemini QWK → AC2 | GPT-4.1-mini | Qwen3-235B |
| --- | --- | --- | --- |
| O1 Mohler g–r1 minus r1–r2 | −0.059 → −0.122 (holds) | −0.143 → −0.088 (lost) | −0.165 → −0.093 (lost) |
| O2 Mohler g–r2 minus r1–r2 | +0.210 → +0.161 (holds) | +0.099 → +0.165 (gained) | +0.066 → +0.160 (gained) |
| O3 swing g–r2 minus g–r1 | +0.270 → +0.283 (holds) | +0.242 → +0.253 (holds) | +0.231 → +0.253 (holds) |
| O4 Menagerie 14 levels, g–h minus h–h | −0.205 → +0.053 (lost) | −0.379 → +0.039 (lost) | −0.272 → −0.036 (lost) |
| O5 Menagerie 5 levels | −0.277 → +0.031 (lost) | −0.462 → +0.002 (lost) | −0.354 → −0.059 (holds) |

"Lost" means the QWK interval excluded zero and the AC2 interval does not. On Mohler, the reading
"one rater above the human–human level, the other below it" keeps its sign everywhere. On Menagerie,
QWK says every grader agrees with the humans far less than the humans agree with each other
(grader–human 0.06–0.23 against human–human 0.44 on 14 levels), while AC2 says they are
indistinguishable.

**AC2 is not the better instrument for these data (post hoc, reported only).** A grader that gives
every Menagerie item A− scores AC2 **0.854** against the human raters (14 levels; 0.865 on 5). That is
above the raters' 0.706 with each other on the same items and above every real grader (0.67–0.76). A
grader that gives every Mohler answer a 5 scores AC2 **0.926** against rater 1 on the full corpus,
above the human–human 0.858. QWK gives both 0. AC2 is less sensitive to the marginals because its
chance term ignores them, and the same property lets it credit marks that ignore the work. Albatarni
& Elsayed made their recommendation for essay-scoring models evaluated against a reference; on these
corpora it would rank a constant grader above the humans.

## What this means for Paper VI

No number in the paper changes and no headline moves. Every QWK the paper reports reproduces, the
abstract does not cite the ceilings, and the readiness record's `cooling_off` is not touched. Three
things change in what the paper may say.

1. **§1.2's premise is now measured, with a caveat.** The premise is that "a substantial share of the
   residual disagreement between a grader and a single human reference is noise in the reference".
   The share is about half (ρ 0.45–0.55, six cells, every interval above 0.25). The grader looks better
   where the humans agree in 4 of 6 cells, and the reference swing is 0.23–0.27 on three further
   models. What this study cannot say is whether the items humans disagree on are noisy references or
   hard items (P3 is unresolved). On Mohler the noise is partly a systematic offset between the raters
   (rater 1 is +0.89 points on the draw).
2. **"Humans agree at 0.52 / 0.47" is a kappa statement.** Under AC2 the same raters are at 0.86 /
   0.89. §5.1 should put AC2 beside the ceilings, say that the level depends on the statistic and the
   marginals, and say why the paper keeps QWK. The comparisons the paper builds on the ceiling (the
   reference swing; one rater above the human–human level, one below) survive the change of statistic.
3. **§4.6's mention of Albatarni & Elsayed should not read as an endorsement of AC2 for graders.** On
   these data AC2 credits a constant grader above the humans.

Nothing here supports Elangovan et al.'s specific pattern (the grader comparable to humans only where
humans disagree): on MAE the grader-minus-human gap is similar in the two strata on Gemini and GPT-4.1-mini (−0.62 / −0.59, −0.70 / −0.62 levels) and changes sign on Qwen (−0.12 / +0.11), with no interval computed (reworded 2026-10-06, scope-audit-6 S2). §5.1's citation
of Elangovan for the 0.798 should stay a caution ("can"), not a finding about these data.

### Proposed text (the article is not edited here)

**§5.1, after the human-ceiling table (an addition; it replaces nothing):**

> **The ceilings depend on the statistic; the comparisons do not.** Gwet's AC2 (§4.6) puts the same
> raters much higher: Corpus B 0.858 [0.839, 0.875] against QWK 0.519; Corpus C 0.887 on five levels
> (QWK 0.465) and 0.749 on fourteen (0.424); per grader pair 0.61 to 0.92 against QWK's 0.04 to 0.73.
> The gap is the kappa paradox. Corpus B's marks bunch at the top (rater means 4.40 and 3.93 out of
> 5), and on a 300-answer draw stratified to flatten them the two statistics agree (0.531 and 0.562).
> So "trained raters agree at about 0.5" is a statement about kappa, and we do not quote the level
> without its statistic. What the paper uses the ceiling for survives: no grader-versus-human
> comparison reverses under AC2, and the choice of reference moves agreement by 0.23–0.27 in QWK
> (0.25–0.28 in AC2) on three further models grading 300 Corpus B answers, against at most 0.05 from
> any intervention here. On Corpus C the two statistics disagree about the grader: QWK puts every
> model far below the humans (0.06–0.23 against 0.44 on fourteen levels), AC2 level with them. We
> keep QWK, because AC2 would score a grader that ignores the work above the humans (§4.6)
> (`studies/measurement/grader-ceiling-robustness/`).
>
> **Where the humans agree.** We split Corpus B by whether its two raters gave the same mark (121 of
> 300 answers) and Corpus C by whether all its raters fell within three of the fourteen levels (86 of
> 240). After standardising for the level of the work, each grader's error against a single human is
> larger where the humans disagreed: by 0.04–0.06 of the score range on all three models on Corpus C,
> and by 0.01–0.06 on Corpus B, where only one model's interval excludes zero. Against the mean of the
> raters the difference disappears (within ±0.02 of the range for all six). About half of each
> grader's squared error against one human (0.45–0.55; every interval above 0.25) is that human's
> own disagreement with the others, if the grader's errors are independent of the raters'. On Corpus
> B they are not quite: rater 1 marks 0.89 points above rater 2 on these answers, and every grader
> sits nearer rater 2. Neither split can say whether the items humans disagree on are noisy for the
> reference or also hard for the grader. A leave-two-out decomposition on Corpus C's four raters,
> built to separate the two, could not resolve it on 60 programs. Elangovan et al. (2025) report
> that machine–human agreement falls well below human–human where humans agree; on Corpus C the gap
> between the grader and the humans is the same in both strata.

**§4.6, after the QWK paragraph:**

> **Gwet's AC2 (a robustness check on the ceilings only).** AC2 is a chance-corrected agreement
> coefficient, here with the same quadratic weights over the same levels, whose chance term does not
> come from the observed marginals (Gwet 2008). It therefore does not fall when marks bunch at one end
> of the scale, as kappa does (the "kappa paradox"; Feinstein & Cicchetti 1990). Albatarni & Elsayed
> (2026) recommend it over QWK; we report it beside each human–human ceiling. *Cons:* the same
> property lets it credit marks that ignore the work. A grader that gave every Corpus C item A− would
> score AC2 0.85 against the human raters, above the raters' 0.71 with each other on the same items;
> one that gave every Corpus B answer full marks would score 0.93 against rater 1. So we do not use it
> to score a grader. Our implementation reproduces the worked examples published with Gwet's irrCAC
> package.

**§1.2, after "…is noise in the reference" (optional):**

> — on the two corpora with independent raters, about half of a grader's squared error against one
> human is that human's own disagreement with the others (§5.1) —

**References, if the text above is used:** Gwet (2008) is not yet in Paper VI's list. Gwet, K. L.
(2008). Computing inter-rater reliability and its variance in the presence of high agreement.
*British Journal of Mathematical and Statistical Psychology*, 61(1), 29–48.
https://doi.org/10.1348/000711006X126600. Feinstein & Cicchetti (1990) and Albatarni & Elsayed (2026)
are already cited.

Scope of every figure above: the 300 Mohler answers and 60 × 4 Menagerie programs of
`grader-label-stability`, graded by three models under an attainment label (balanced across strata).
The paper's own 0.549 / 0.798 / 0.711 run cannot be re-scored: it has no per-case dump, and its draw
does not re-derive.

## Erratum (2026-10-06, Paper VI corrections-4)

The statement in "Data" and in the scope note above that the 150-answer run's draw "does not re-derive
from the current harness (re-derived rater-vs-rater 0.478, not 0.608)" is wrong, and so is "another draw
that cannot be recovered" under the reference swing. The 0.478 is the `--mode taxonomy` draw,
`stratifiedSample(eligible, 150, 7)` over the 1,609 answers with four sibling questions. The paper's figures
come from `--mode ceiling`, which draws `stratifiedSample(all 1,727, 150, 7)`; that draw rebuilds with no
model call to rater-vs-rater QWK 0.6077 (MAE 1.147) in both the frozen `vendor/934478716` snapshot and the
current harness (`studies/measurement/grader-eval/analyses/mohler_ceiling_draw.mts`,
`analyses/out/mohler-ceiling-draw.json`). The grader marks behind 0.549 / 0.798 / 0.711 were not kept per
case, so those three still cannot be re-scored here. No number or verdict of this study changes. The
proposed text above was applied to Paper VI in corrections-4.
