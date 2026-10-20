# Order trials, re-analysed: Kremer et al. (Nigeria) and Patel et al. (ds1190)

**Asked.** This programme had cited two order-trial claims only as their authors printed them
(`studies/outcomes/order-trials/PUBLISHED-FINDINGS.md`). This study re-analyses both:

1. **Kremer, Gray-Lobe, de Laat & van der Haar (NBER 31853).** A year of interleaved maths practice in
   59 Nigerian schools: +0.28 SD on termly tests, +0.03 at year end. (a) Does that reproduce? (b) Does
   the year-end fade depend on baseline attainment? (c) Does it depend on how long ago the tested
   material was taught?
2. **Patel, Liu & Koedinger (CogSci 2016), DataShop ds1190.** The only prerequisite-order swap we hold
   (fraction addition first vs multiplication first). Its printed statistics are inconsistent, and its
   delayed test comes four to five days after the last practice (log timestamps; the paper says three).

The pre-registration (verdict strings, thresholds and floors) is in the docstrings of
`kremer_fade.py` and `patel_order.py`, committed at `901d14b` before either script read a real
outcome. The floors were committed at `92b2821`, before the real Kremer run. The Patel answer-level
amendment (`patel_answers.py`) was registered at `1e8b885` after the registered run failed on the
data. It is registered but **not blind** (section 2b).

## Answer

| | Verdict | Numbers |
| --- | --- | --- |
| Kremer (a), reproduction | **REPRODUCES** | posttest index **+0.281** (school-clustered SE 0.119), n 661; cumulative **+0.028** (0.159), n 516; 58 schools |
| Kremer (a), fade | **UNINFORMATIVE (BELOW FLOOR)** | fade +0.252, **randomisation p 0.053** (the paper's SUR test gave p 0.02); floor power at 0.28 is 0.53 |
| Kremer (b), fade by baseline | **UNINFORMATIVE (BELOW FLOOR)** | fade slope −0.142 per baseline SD (lower-baseline pupils fade more), p 0.26; floor power at 0.19 is 0.35 |
| Kremer (c), fade by delay | **OLDER MATERIAL FADES**, with three caveats (below) | same material: **+0.270 at about 38 days, −0.118 at about 124–244 days**; difference +0.388, p 0.032; floor power at 0.28 is 0.28 |
| Patel, printed statistics | **PRINTED STATISTICS INCONSISTENT** | B/SE = 0.07/0.04 gives t 1.75 (p 0.086); t 3.57 gives p 0.0007; p 0.04 needs t 2.10. Each pair of the three disagrees |
| Patel, floor | detection floor fails at the printed effect | power **0.37** at the printed 8 points; 0.86 at 16 points; MDE d 0.73 (about 11 points at the printed SE) |
| Patel, re-analysis of ds1190 (run 2026-10-08) | **FAILS ON THE DATA**: the run completed, but the registered scorings do not measure answers (below) | mechanical outputs: **DOES NOT REPRODUCE**; 29 of 30 test cells UNINFORMATIVE (BELOW FLOOR), one ADDITION FIRST BETTER (Midtest A, trained, step scoring, p 0.040). None is a valid reading: 5 of the 8 logged steps per test problem are pre-filled givens (100% "correct", 0 s), and the 8th is an ungraded confidence rating (100% "incorrect") |
| Patel, answer-level amendment (`patel_answers.py`, registered 2026-10-08, **not blind**) | **UNINFORMATIVE (BELOW FLOOR)** on the primary; reproduction **REPRODUCES ON DPosttest, trained** | DPosttest trained answers AM **0.683** (26) vs MA **0.772** (29), MA − AM **+0.089** [−0.025, +0.203] (learner bootstrap within arm), re-randomisation **p 0.144**, d +0.41; floor power at 8 points **0.30**. Secondary Posttest trained +0.136 [+0.033, +0.241], p 0.013 (section 2b) |

## 1. Kremer et al.: `kremer_fade.py`

**Data.** The authors' replication package, Harvard Dataverse
[doi:10.7910/DVN/BBS0SH](https://doi.org/10.7910/DVN/BBS0SH), CC0. It is registered as `kremer-bbs0sh` in
`data/data-sources.json` (MD5, fetch URL and codebook) and is read in place from the zip. The sample
is the authors' own (`fx-math.do`): 683 eligible pupils in 59 schools and 10 strata, 27 schools
interleaved. The pupil-level outcomes match the package's own `po`/`cu` columns exactly.

**Inference.** The school is the unit of randomisation. Every p-value here comes from 5,000 re-draws
of the school labels within strata, keeping each stratum's treated count, with the observed
assignment excluded. A re-draw leaves on average 51% of schools with their real label; with two arms
that cannot be avoided. Pupils are never shuffled.

### (a) The headline reproduces, and so does the paper's real clustering

Both coefficients match to the third decimal. **The printed SEs (0.12, 0.16) are school-clustered.**
Strata clustering gives 0.107 and 0.189. Table 3's note says "Standard errors are clustered at the
strata level", but the text and `fx-math.do` both say school, and school is what reproduces the
printed numbers. Per term: +0.272 (PO1), +0.268 (PO2), +0.325 (PO3, paper 0.31 on its unfiltered
sample). Baseline subgroups reproduce too: posttest +0.54 / +0.35 / +0.16 at −1 / 0 / +1 SD, and
cumulative +0.07 / +0.02 / −0.02.

**The fade is weaker than printed.** The paper tests posttest = cumulative by SUR with
school-clustered SEs and gets p 0.02. Design-based inference at the randomised unit gives
**p 0.053**. That figure barely moves with the common effect imposed under the null (0.052–0.055 for
τ0 from 0 to b_post). At the paper's own effect size this instrument detects a fade 53% of the time,
so the pre-registered verdict is UNINFORMATIVE (BELOW FLOOR), not "no fade". On randomisation
inference the year-end fade is suggestive, not established at 0.05. The posttest effect itself
survives (p 0.037; the paper's wild bootstrap gave 0.04).

### (b) Whether the fade depends on baseline cannot be decided here

Baseline exists in only 43 of 59 schools. Six strata hold both arms with baseline, so the
interaction is identified but thin. The fade's slope on baseline is **−0.142** per SD, the direction in
which lower-baseline pupils lose more of their larger posttest gain. But p is 0.26, and the floor
detects a slope of the paper's size (0.19) only 35% of the time. The low achievers' posttest
advantage (+0.54) is mostly gone at year end (+0.07). So is the high achievers' smaller one (+0.16
to −0.02). The data cannot say whether the two fades differ.

### (c) Fade by delay: the clearest result, built on an assumption

No item-level data were recorded (paper, s.2.6), so delay can be indexed only at test level. The
cumulative test (26 June 2019) mirrors PO1 (30% of items), PO2 (37%) and PO3 (33%). Term-1 material is
about 244 days old by then, term-2 material about 124 days, term-3 material about 34. PO3 came five
days before the cumulative test. Following the paper's s.4.4, the effect on terms-1–2 material at
year end is **d_old = (b_cum − 0.33 · b_PO3) / 0.67 = −0.118**. The same material's effect at its own
posttests, about 38 days after teaching, is **d_short = mean(b_PO1, b_PO2) = +0.270**. Delay-matched
fade on the same material: **+0.388, p 0.032**. The pre-registered verdict is OLDER MATERIAL FADES.
d_old is not distinguishable from zero (p 0.55): the data say the advantage is gone, not that it
reversed.

Three caveats belong with this verdict wherever it is quoted:

1. **It rests on the decomposition.** The decomposition assumes the cumulative score is the
   item-share-weighted sum of per-term effects on one SD scale, and that PO3 measures the term-3
   component. The paper names two ways this fails: PO3 itself teaches, and shared skills across
   terms make PO3 a bad control.
2. **It comes from an underpowered instrument, so its size is inflated.** Floor power at a true 0.28
   is 0.28. In an exploratory check added after the run (`--type-m`, `out/kremer_typem.json`, not
   pre-registered), significant estimates averaged 0.51 when the truth was 0.28 (1.8x) and 0.54 when
   it was 0.39 (1.4x). The observed 0.39 is consistent with a true delay fade anywhere from about 0.2
   to 0.4.
3. **It is one of three pre-registered verdicts.** It would not survive a Bonferroni correction
   across (a), (b) and (c) (0.032 > 0.017).

### What the Kremer re-analysis means

- The cross-cutting delay rule in `research/WRITEUP-MAP.md` cites "+0.28 SD on termly tests, +0.03 at
  year end". Both numbers are now our own reproduction, not a transcription. The **p 0.02 for the
  difference is not**: at the randomised unit it is p 0.053. Cite the fade as "the termly effect
  (+0.28, p 0.04) is not detectable at year end (+0.03, CI about ±0.31); the difference is p 0.05 by
  randomisation inference".
- On a delay-matched comparison, which is the comparison the delay rule asks for, the effect on the
  same material falls from +0.27 at about five weeks to about −0.12 at four to eight months. That is
  the delay rule's own example, measured rather than quoted. Two qualifiers travel with it: it
  depends on the decomposition, and it is likely inflated.
- This is a **practice-order** trial (interleaved vs blocked), not a prerequisite-order trial.

## 2. Patel et al.: `patel_order.py`

**Printed statistics (no data needed).** For MA vs AM the paper prints 78% vs 70%,
"B = 0.07 (0.04), t = 3.57, p = 0.04", with 29 + 30 learners. The three are pairwise inconsistent.
B/SE gives t 1.75 and p 0.086. t 3.57 gives p 0.0007 and needs SE 0.020. p 0.04 needs t 2.10 and SE
0.033. Each pair implies a different learner SD: 0.15, 0.08 or 0.13. At most one figure can be right,
and the published significance of the reversed-order advantage cannot be read from the paper. The
interleaved-vs-AM contrast (B 0.10, SE 0.03, p < .01) is consistent: t 3.33, p ≈ 0.001. These are
transcriptions from `PUBLISHED-FINDINGS.md`. The paper's hosts (escholarship.org,
cogsci.mindmodeling.org, semanticscholar.org) are blocked by this session's egress proxy, so the
full text could not be re-opened today.

**Detection floor (synthetic, shaped like ds1190 Study 2).** The synthetic data use 29 + 30 learners
and 16 test items. They are calibrated to AM ≈ 0.70 and to the learner SD the printed B/SE implies
(0.15). Learner labels are re-randomised 2,000 times with arm sizes kept, since the learner is the
assigned unit. False positives run at 0.053. Power at the printed +8 points is **0.37**; it is 0.65 at
+12 and 0.86 at +16. The MDE is d = 0.73, about 11 points at the printed SE. **Even a clean
re-analysis of ds1190 would read UNINFORMATIVE at the printed effect size.** Only an effect twice the
printed one would be detectable.

**Re-analysis: run on 2026-10-08, and it fails on the data.** Until then this part was BLOCKED (ds1190
was not on the machine). The export is DataShop ds1190, "Fraction Addition and Multiplication",
project "Blocked vs Interleaved Instruction" (PI Rony Patel). The All Data file's MD5
`e4d2ba2d7ba06be4fe080a7671f34e18` matches `data/data-sources.json`. The script reads the per-sample
exports `S2_AM_Blocked` (MD5 `355e10b9…4da`) and `S2_MA_Blocked` (`c243341b…abe`), which the registry
does not checksum. `patel_artefacts.py` ties them to the checksummed file: all 34,738 rows of the 60
learners appear in the All Data file, with every learner's row count equal, under the assignments
"AM Day 1" and "MA Day 1". `patel_order.py` was run unchanged
(`LDA_SCRATCH_DIR=<scratch> python3 patel_order.py`; output `out/patel_order.json`, commit `c5b4d91`).

*What it printed.* Parts 1 and 2 reproduced their committed values exactly (same seed). Part 3 found
30 + 30 learners, five test sets in time order (Pretest, Midtest A, Midtest B, Posttest, DPosttest),
and no class column, so learners were relabelled across the study (10,000 relabellings). The
registered verdicts are:

- **reproduction: DOES NOT REPRODUCE.** No scoring of any test gives AM within 0.02 of 0.70 and MA
  within 0.02 of 0.78.
- **order:** UNINFORMATIVE (BELOW FLOOR) in 29 of 30 test × scoring cells (floor power at 8 points is
  0.37). The exception is **ADDITION FIRST BETTER** on Midtest A, trained items, step scoring:
  MA − AM −0.022, d −0.56, p 0.040, one of 30 cells.
- **delay contrast** (Posttest → DPosttest change, MA − AM): −0.011 to +0.000, p 0.62 to 0.98.
- **delay:** median "days after last practice" of −5.0, −4.0, −4.0, −4.0 and −0.004 for the five
  tests.

*Why none of these is a reading.* The values parsed cleanly, but they do not mean what the
registration says. `patel_artefacts.py` (written after the run, not pre-registered, and computing no
between-arm outcome contrast) shows what each logged step is. It pools both arms over all five tests
(`out/patel_artefacts.json`):

| step of a `T ...` test problem | rows | first attempt correct | median duration |
| --- | ---: | ---: | ---: |
| num1, den1, operation1, num2, den2 (the problem as posed) | 2,740 each | **1.000** | **0 s** |
| num3 (answer numerator) | 2,713 | 0.715 | 8 s |
| den3 (answer denominator) | 2,703 | 0.733 | 5 s |
| ConfidenceRating (radio button) | 1,799 | **0.000** (all "incorrect") | 2 s |

Five of the eight logged steps are pre-filled givens and one is an ungraded rating, so:

1. **Step scoring** is about two-thirds givens. Its arm difference is driven largely by how many
   steps of each kind were logged, and that differs by arm. On the DPosttest the givens are 0.671 of
   AM's steps and 0.651 of MA's, and the ratings 0.078 and 0.092. A 2-point composition gap is
   larger than the 0.5- to 2-point accuracy gaps being tested. The one directional verdict (Midtest
   A) has the composition gap in its own direction: givens 0.677 (AM) vs 0.653 (MA). It is not
   evidence that addition first is better.
2. **Problem scoring** ("every step correct") is false whenever a rating was logged, which is why it
   reads 0.01–0.04.
3. **Final-step scoring** reads the rating whenever one was logged, so it reads 0.05–0.16.
4. **The delay** takes the learner's latest non-`T` row as "last practice". The test sets also hold
   non-`T` items (ComDen, Equiv), so for the DPosttest that row is inside the test itself (−0.004
   days). Measured from the last row in a practice set ("Fraction Arithmetic Blocked 1/2"), the
   Posttest follows practice within minutes (median 0.0002 days). The **DPosttest follows it by a
   median of 3.98 days (range 3.97–4.97, 55 learners)**: four to five days, not three, and not six.
5. **The reproduction search** is over these three scorings only, so DOES NOT REPRODUCE says
   nothing about whether the printed 70/78 are in the data. One piece of arithmetic on the committed
   aggregates suggests they are. Since givens score 1 and ratings 0, step accuracy ≈ given share +
   answer share × answer accuracy. Solving for answer accuracy on the DPosttest gives AM
   (0.846 − 0.671) / 0.251 ≈ 0.70 and MA (0.853 − 0.651) / 0.257 ≈ 0.78. On the Posttest it gives
   0.68 and 0.78. This approximation ignores the covariance between a learner's share and accuracy.
   It was **not computed from the data and is not a registered result**. It says the printed
   figures are probably answer-field accuracy, on one of the two posttests.

Under the handover's rule (a script that fails on the data is recorded, not tuned), the analysis
stops here. An answer-field scoring (num3, den3 only, givens and ratings dropped) and a delay
measured from the last practice-set row would need a dated amendment committed before it is run.
The registered thresholds, floor and verdict strings would carry over. With an 8-point effect and the
floor's 0.37 power, such a run would most likely still read UNINFORMATIVE (BELOW FLOOR) unless p fell
below 0.05. That amendment was registered and run the same day, with its own answer-level floor
(section 2b).

**Already on the board, from the earlier session that held the data.** `studies/outcomes/interleaving/ds1190_order.py`
read the delayed posttest (DPosttest) as step-level first-attempt accuracy over every logged step of
the ADD and MUL items. It found AM 0.852 vs MA 0.862, **d −0.43 [−0.93, +0.10]** (d is AM − MA, so MA
better, the paper's direction; the interval is a learner bootstrap), UNINFORMATIVE. That score has
the same defect as the step scoring above. About two-thirds of it is pre-filled givens and up to a
tenth is always-wrong ratings, in shares that differ by arm. The README's guess that "the paper scored
something else, probably whole problems" is replaced by the finding above: the paper's figures are
most likely answer-field accuracy, and the 0.85 level is the givens. **The printed estimate does not
stand as an estimate of the order effect on answers.** It is neither confirmed nor replaced by the
registered test, because that test's scorings share the defect. Its verdict word (UNINFORMATIVE)
probably survives: the arithmetic above puts the answer-field gap near the printed 8 points, where
this design has 0.37 power. That is a reading of the floor, not a result. The answer-level amendment
(section 2b) now replaces it: on the delayed test, trained items, MA − AM is +0.089, d +0.41
[−0.12, +1.02], p 0.14, UNINFORMATIVE (BELOW FLOOR).

**MacLellan (2025) exclusions: not run, cannot be reconstructed.** The literature review (strand 4,
"Analyses" item 4) asks for a sensitivity run with MacLellan's exclusions (78 tutor and 71 posttest
students). The arXiv full text (2502.02456, read 2026-10-08) says only that "seven students had
corrupted posttest data and one additional student had corrupted tutor and posttest data". It gives
no definition of "corrupted", no student identifiers and no code or data link (the only links are the
DataShop pages for ds1190 and ds1123). The exclusions are also for a different contrast: Study 1's 79
students, blocked (add-same → add-different → multiply) vs fully interleaved, with an 8-item
posttest. They are not for Study 2's 30 + 30 AM-vs-MA order swap that `patel_order.py` analyses. Any
exclusion list built here would be a guess at an undefined criterion applied to the wrong sample, so
the sensitivity run was skipped.

**ds1706** is Study 1 (interleaved vs blocked add-then-multiply, two days, no delayed test). It has no
MA arm, so it carries no order swap and is not re-analysed here.

## 2b. Patel et al., amended: answer-level scoring (`patel_answers.py`)

**Asked.** On the answer the learner typed, with givens and ratings dropped, does fraction
multiplication first (MA) beat addition first (AM)? And are the paper's printed 70% / 78% in the data?

**This is a registered but non-blind re-analysis.** The amendment's docstring is its registration. It
was committed at `1e8b885` before any answer-level contrast between arms was computed. The floor was
committed at `469cf62`, and the real run at `b4d36c2`. Four things were known before the
registration:

- the logging artefact (section 2);
- the registered analysis's step-level per-arm outputs (`out/patel_order.json`);
- the earlier step-level estimate in `studies/outcomes/interleaving/` (d −0.43, MA better);
- arithmetic on those committed aggregates, which suggested answer accuracy near AM 0.70 / MA 0.78 on
  the DPosttest (section 2, point 5).

The direction and rough size of the result were therefore anticipated. The registration fixes the
scoring, the tests, the inference and the verdict strings so they could not be chosen after the exact
numbers were seen. It does not make the result a prediction, and the reproduction check below is not
an independent confirmation.

**Design (as registered).** A test problem is correct when both num3 and den3 are correct on first
attempt. The response is read from the earliest Problem View that logs an answer field, and a missing
field counts as wrong. A presented problem with no answer row is scored 0; dropping it instead is
reported as a sensitivity check. The secondary per-step answer score averages num3 and den3 (1, 0.5
or 0 per problem). Trained items are addition and multiplication (8 per post-test); transfer items
are subtraction and division (4). A learner enters a cell with at least half its items presented.

- **Primary:** DPosttest, trained items, MA − AM.
- **Inference:** 10,000 re-randomisations of arm labels across learners. The learner is the assigned
  unit and the export has no class column. The interval resamples learners with replacement within
  each arm (10,000 resamples, percentile 95%).
- **Delay:** measured from the last practice-set row.

**Floor (synthetic, answer level, at the real cell sizes).** Learner ability and item difficulty are
calibrated to the pooled per-learner answer accuracy, with arm labels discarded. On the DPosttest
trained items that is mean 0.730 and learner SD 0.218 over 26 + 29 learners and 8 items. Effects of
0, +0.08 and +0.16 are planted as a logit shift. Each value has 1,000 worlds, each tested with 2,000
relabellings.

| cell | false positives | right-sign power at +0.08 | at +0.16 | wrong sign at +0.08 / +0.16 | pass |
| --- | ---: | ---: | ---: | ---: | --- |
| DPosttest trained | 0.049 | **0.304** | 0.912 | 0.000 / 0.000 | PASS |
| Posttest trained | 0.033 | 0.310 | 0.910 | 0.001 / 0.000 | PASS |
| DPosttest transfer | 0.043 | 0.179 | 0.539 | 0.001 / 0.000 | **FAIL** |
| Posttest transfer | 0.047 | 0.158 | 0.565 | 0.000 / 0.000 | **FAIL** |

The answer-level learner SD (0.22) is larger than the 0.15 the paper's printed SE implies. Power at
the printed 8 points is therefore 0.30, lower than `patel_order.py`'s 0.37. The instrument sees a
16-point effect 91% of the time on eight trained items. On four transfer items it sees one only
54–57% of the time, so transfer reads FLOOR FAILED.

**Result.**

| test, items (answer correct) | AM (n) | MA (n) | MA − AM [95% learner bootstrap] | d | p | verdict |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| **DPosttest, trained (primary)** | **0.683** (26) | **0.772** (29) | **+0.089 [−0.025, +0.203]** | +0.41 [−0.12, +1.02] | **0.144** | **UNINFORMATIVE (BELOW FLOOR)** |
| Posttest, trained | 0.661 (28) | 0.796 (28) | +0.136 [+0.033, +0.241] | +0.68 | 0.013 | MULTIPLICATION FIRST BETTER ON ANSWERS (UNDERPOWERED: ESTIMATE LIKELY INFLATED) |
| DPosttest, transfer | 0.481 (26) | 0.595 (29) | +0.114 [−0.034, +0.262] | +0.40 | 0.163 | FLOOR FAILED (NO READING) |
| Posttest, transfer | 0.491 (28) | 0.545 (28) | +0.054 [−0.089, +0.196] | +0.19 | 0.555 | FLOOR FAILED (NO READING) |
| Pretest, trained (balance) | 0.672 (29) | 0.662 (30) | −0.010 [−0.118, +0.100] | −0.05 | 0.88 | descriptive |

- **Direction:** MA is higher in every post-test cell, which is the paper's direction. On the primary
  the bootstrap interval includes zero, and so does the d interval.
- **Per-step answer score** (secondary). DPosttest trained: AM 0.776 vs MA 0.851, +0.075, p 0.100,
  UNINFORMATIVE (BELOW FLOOR). Posttest trained: +0.106, p 0.014, MULTIPLICATION FIRST BETTER ON
  ANSWERS (UNDERPOWERED).
- **All items** (secondary, descriptive). DPosttest +0.097, p 0.108. Posttest +0.106, p 0.055.
- **Sensitivity:** dropping unanswered problems changes nothing. One AM trained DPosttest problem
  was unanswered, and the contrast stays +0.089, p 0.146.
- **Pretest-adjusted primary** (secondary; pooled slope 0.40, fitted without arm labels): +0.093
  [−0.008, +0.197], p 0.084.
- **Delay contrast** (secondary; within-learner DPosttest − Posttest change on trained items):
  AM +0.020, MA −0.030, MA − AM −0.050 [−0.143, +0.044], p 0.33. MA's advantage is smaller at the
  delay (+0.089 against +0.136). The data cannot distinguish that shrinkage from no change.
- **Midtests** (descriptive). Midtest A is an exposure contrast, because the arms had practised
  different operations by then: trained −0.025, p 0.75. Midtest B trained: +0.107, p 0.11.
- **Delay.** The Posttest follows the last practice row by a median of about 20 s in both arms. The
  DPosttest follows it by 3.99 days (AM, range 3.97–4.00) and 3.98 days (MA, range 3.97–4.97). The
  medians before the Posttest are negative, because practice continues after the earlier tests; they
  are not delays.
- **Cell sizes.** The DPosttest has 26 AM learners here against 27 in `patel_order.py`, because one
  AM learner was shown only one trained item (the half-items rule).

**Reproduction check: REPRODUCES ON DPosttest, trained.** AM 0.683 and MA 0.772 are within 0.02 of
the printed 0.70 and 0.78. None of the other three cells matches: Posttest trained 0.661 / 0.796,
Posttest all 0.604 / 0.710, DPosttest all 0.615 / 0.713. So the printed percentages are most likely
answer accuracy on the trained items of the delayed test. This was a search over four cells, and the
rough arithmetic had already pointed at this cell. The printed B, SE, t and p were not re-derived,
because the paper's model is not known.

**What it means.**

- **The paper's means are in the data, but its significance is not.** On the delayed test, the
  answers favour multiplication first by about 9 points. That is the printed size and direction. At
  the learner unit, though, p is 0.14, and the interval runs from about −2 to +20 points. The
  registered verdict is UNINFORMATIVE (BELOW FLOOR): at 26 + 29 learners this design detects an
  8-point effect 30% of the time. Design-based inference does not reproduce the printed "p = 0.04".
  The paper's model may differ: it may have pooled problems or adjusted for pretest. Even with the
  pretest adjustment, p is 0.08.
- **The immediate Posttest clears 0.05:** +13.6 points, p 0.013. It is a secondary outcome, and it
  comes from an instrument with 31% power at 8 points. A significant result from such an instrument
  overstates the effect: at these cell sizes an estimate must reach about +0.11 to clear 0.05. Read
  it as "the direction is probably right; the size is not known".
- **This replaces the step-level d −0.43** in `studies/outcomes/interleaving/` as the ds1190 order
  estimate. In this section's orientation, that estimate put MA ahead by 0.43 SD. On answers, the
  delayed test gives d +0.41 [−0.12, +1.02] (MA − AM). The size is close by coincidence, and the
  interval is wider.

## A second randomised order result already exists

`studies/identifiability/core-vs-culture/order_swap.py` (ASSISTments PSABANRN, osf.io/59shv) randomised
**1,192 students to four orders** of mean, median, range and mode. Verdict: **ORDER MATTERS** for
problems to mastery (omnibus permutation p 0.0035; arm means 6.5–8.0 problems) but not for
completion (p 0.82) or correct rate (p 0.29). Together with the Clements/Sarama length trajectory
(`studies/outcomes/lt-trials/`), that makes **at least two randomised order trials we hold and have
analysed**, plus ds1190 (section 2b: UNINFORMATIVE on its primary). Papers II and VII (and the Paper 1 sentence "In
the one randomised order trial we hold", `research/article/limits-of-inferring-prerequisite-structure.md`)
should stop saying "the one randomised order trial we hold" (PAPER-PLAN corrections table).

## What this means for Paper VII (and III)

- **VII (does structure move learning).** VII's motivation ("unfiltered effects are small and fade by
  the delayed test") can now cite a reproduction instead of a transcription. Kremer's termly effect
  reproduces exactly (+0.28), and the year-end effect is +0.03. On delay-matched material the effect
  falls from +0.27 at about five weeks to about −0.12 at four to eight months (p 0.03, likely
  inflated, decomposition-dependent). The printed "p 0.02" for the overall fade should not be
  repeated: it is p 0.05 at the randomised unit. **For VII's design:** at 59 schools this trial had
  53% power for a fade of its own size. A co-primary delayed test needs to be powered for the
  *difference* between delays, not only for the immediate effect. Patel's prerequisite-order swap
  adds a direction but no established effect. Its printed means reproduce on answer accuracy (delayed
  test, trained items: 0.683 vs 0.772). Its printed significance is internally inconsistent, and at
  the learner unit the delayed contrast has p 0.14, with 30% power for an effect of its printed size.
  The immediate posttest gives p 0.013, but that is a secondary outcome from an underpowered
  instrument (section 2b, registered but not blind). VII should cite it as "a small study whose
  printed means reproduce but whose delayed effect is not distinguishable from zero at the learner
  unit". It should cite `order_swap` as the randomised order result (efficiency, not attainment).
- **III (learner state).** The moderation question (does the fade depend on baseline) is unanswerable
  on this trial. The direction (lower-baseline pupils gain more and lose more) matches the paper, but
  p is 0.26 at 35% power. III should not cite Kremer as evidence that the right order depends on
  prior attainment. It may cite it as motivation, labelled as unestablished.

## Files

- `kremer_fade.py`: pre-registered reproduction and fade analyses; `--floor` for the detection floor;
  `--type-m` (exploratory, added after the run).
- `patel_order.py`: printed-statistics check, synthetic floor, and the data-gated ds1190 re-analysis
  (pre-registered; run unchanged on 2026-10-08).
- `patel_artefacts.py`: not pre-registered; written after that run to show from the data why its
  scorings and delay do not mean what they say. Computes no between-arm outcome contrast.
- `patel_answers.py`: the answer-level amendment. Registered (not blind) at `1e8b885`; `--floor`
  committed at `469cf62`; real run at `b4d36c2`. Reuses `patel_order.py`'s loader and
  re-randomisation.
- `out/kremer_floor.json`, `out/kremer_fade.json`, `out/kremer_typem.json`, `out/patel_order.json`,
  `out/patel_artefacts.json`, `out/patel_answers_floor.json`, `out/patel_answers.json`: aggregates only.
- `out/history-entry.json`: the board entry for the 2026-10-08 answer-level amendment, for the
  maintainer to append. The previous entry (the failed registered run) is already in `board/history.json`.

```
LDA_SCRATCH_DIR=<scratch> python3 data/data_sources.py --fetch kremer-bbs0sh
LDA_SCRATCH_DIR=<scratch> python3 kremer_fade.py --floor && python3 kremer_fade.py
LDA_SCRATCH_DIR=<scratch> python3 patel_order.py && python3 patel_artefacts.py   # ds1190 under <scratch>/ds1190
LDA_SCRATCH_DIR=<scratch> python3 patel_answers.py --floor && python3 patel_answers.py
```
