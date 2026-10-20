# Which effect-size regime is C2 in? ds1706 cannot say, and that is worth knowing precisely

`C2` — *do we have data large enough to answer the outcome question?* — is priced at **1,087–6,410
randomised learners** on an assumed sequencing effect of **d = 0.07–0.17**.

The closest published trial of the same estimand disagrees by a factor of five. Rohrer, Dedrick,
Hartwig & Cheung (2020), *J. Educ. Psych.* 112(1) 40–52, ran a preregistered **cluster-randomised**
blocked-versus-interleaved trial in 54 seventh-grade classes over four months and reported, on an
**unannounced test one month later**, 61% against 38%, **d = 0.83**.

**At d = 0.83 a two-arm individually-randomised trial needs about 46 learners. At d = 0.07 it needs
6,410.** C2's price turns on an assumption nobody in this programme has tested, and the two regimes
differ by a factor of 140.

## Why ds1706 is the right dataset to ask and still cannot answer

ds1706 (Patel 2016, [DOI 10.60710/DATASET-1706](https://doi.org/10.60710/DATASET-1706)) is **the only
corpus on this board that randomises order between capabilities**. Blocked learners meet all fraction
addition before any multiplication; interleaved learners meet them mixed. It passes the test Junyi
failed — **1 learner of 79 carries two condition labels (1.3%)** against Junyi's 48% — so the
assignment records what learners were *assigned*, not what they did.

What it cannot do, stated before any result: the whole dataset is **two days**, both arms see the
**same 48 problems reordered**, and **there is no delayed post-test**. The retention outcome `C1`
requires — the one on which the prerequisite deficit decays from +0.0440 at a fortnight to +0.0134 by
eleven weeks — is not measurable here at all.

And its **minimum detectable effect is d = 0.63** (40 per arm, two-sided 0.05, 80% power). ds1706 can
just about see Rohrer's 0.83 and is **completely blind to 0.07–0.17**. It is informative in one
direction only, which is why the pre-registration says so.

## Result

**1. The manipulation is unambiguously in the data.** Share of consecutive steps that change problem
type: blocked **0.009**, interleaved **0.125**, d = **+15.83**.

**2. Interleaving costs accuracy during practice**, the sign desirable-difficulty theory predicts:
0.856 against 0.893, d = **−0.31** [−0.70, +0.13].

**3 and 4. The late-window comparison was confounded, and finding it is the main methodological
yield.**

| | blocked | interleaved | d | 95% bootstrap |
| --- | ---: | ---: | ---: | --- |
| final 25%, raw | 0.952 | 0.890 | **−0.50** | [−0.90, −0.10] |
| final 25%, **multiplication only** | 0.945 | 0.926 | **−0.13** | [−0.59, +0.29] |

The three problem types are not equally hard — **multiplication 0.937, addition same denominator
0.921, addition different denominator 0.827** — and the design puts them in different places. A
blocked learner's final quarter is **96.3% multiplication**, because Blocked set 2 is nothing else;
an interleaved learner's is **47.6% AD / 13.7% AS / 38.7% M**. The raw contrast was therefore
blocked-on-the-easiest-problems against interleaved-on-a-mix, and it manufactured **−0.50** where the
type-matched contrast gives **−0.13**. Roughly three-quarters of the apparent late deficit was the
problem mix.

## Verdict: `UNINFORMATIVE`, and that is the useful answer

|d| = 0.13 against an MDE of 0.63. **At 40 per arm this is the expected result under both regimes** —
Rohrer's 0.83 would have been seen, 0.07–0.17 never could — so it discriminates neither. **It is not
evidence that ordering does not matter.**

What it does establish:

- the randomisation is clean and the manipulation took, so ds1706 is a **valid template** for the
  trial C2 needs — it is 14×–81× too small, not wrongly designed;
- the acquisition-phase cost of interleaving is visible and small once type-matched, which is
  consistent with the theory that the benefit appears only on a **delayed** test;
- **C2's price remains unresolved**, and resolving it is the cheapest high-value action on the board.

## What would resolve it

1. **Patel study 2.** ds1706's own README says *"the blocked and interleaved condition data from
   study 1"*, so a second study exists. Worth requesting.
2. **The IES systematic replication** — WestEd, PI Bryan Matlen, 2022–2027 — exists precisely because
   the field wants to know whether d = 0.83 survives "a larger, more heterogeneous sample". The
   effect size is contested, not settled, and that is the number C2 is priced on.
3. **Any DataShop dataset with `Has Study Data: Yes`, n > 500, and a delayed post-test.** The Junyi
   test takes minutes per dataset.

**One caution against the optimistic reading.** Rohrer's manipulation is *interleaving* — whether
consecutive problems share a strategy — not *prerequisite ordering*. And `studies/identifiability/conjunctive/BAR.md` measured
that interactions attenuate by r^2.34 where main effects attenuate by r^1.17, so a conjunctive gate
seen through noisy indicators shows a smaller d than its underlying size. Both push against assuming
0.83 transfers.

```
python3 ds1706.py --late 0.25 --reps 10000
```

Reads ds1706 from DataShop. Research use, no redistribution: the raw export stays in the session
scratchpad and only the aggregates above are committed.

---

# ds1190 Study 2: the order manipulation itself, with a delayed test — and it needs 170 learners

`ds1706` above is the same PI's Study 1. **ds1190 Study 2 is the study `data/DATASETS.md`'s Hole A has
been describing.** Two arms, both blocked, differing only in which capability comes first:

    AM   Pretest → fraction ADDITION → Midtest A → fraction MULTIPLICATION → Midtest B → Posttest
    MA   Pretest → fraction MULTIPLICATION → Midtest A → fraction ADDITION → Midtest B → Posttest

Same content, same blocking, **opposite order**. 30 learners per arm, **zero overlap**. Taught
2015-11-03/05 with a **DPosttest on 2015-11-08/09** — a genuine delayed test, which is the retention
readout `C1` requires and the thing Study 1 entirely lacked.

**The test items go beyond what was practised.** Practice covers addition and multiplication only;
the 16 test items cross four operations with same/different denominators, so **subtraction and
division are transfer items**. Reading them as trained performance would mix a transfer question
into an order one, so they are scored separately.

> **2026-10-08: the score below is not answer accuracy.** The pre-registered re-analysis
> (`studies/outcomes/order-trials-reanalysis/patel_order.py`, registered at `901d14b`) ran on this
> export on 2026-10-08. Its diagnostic (`patel_artefacts.py` there) shows that each `T ...` test problem
> logs eight steps. Five are the problem as posed (num1, den1, operation1, num2, den2): 100% "correct",
> 0 s. One is a confidence rating that is always logged "incorrect". Only num3 and den3 (the answer)
> are responses, at about 0.72. The step-level accuracy this script reads (0.852 vs 0.862) is therefore
> about two-thirds givens and up to a tenth ratings. Those shares differ by arm: on the DPosttest the
> givens are 0.671 of AM's steps and 0.651 of MA's, larger than the 1-point gap being tested.
> **The printed d −0.43 [−0.93, +0.10] (learner bootstrap; d is AM − MA) does not stand as an estimate
> of the order effect on answers.** The registered re-randomisation test cannot replace it, because its
> scorings share the defect and it fails on the data. Arithmetic on the committed aggregates puts
> answer-field accuracy near AM 0.70 and MA 0.78, the paper's printed figures. That is an
> approximation, not a computed result. At that 8-point gap the design has 0.37 power, so
> "UNINFORMATIVE" probably survives as a verdict word, but the d, its interval and the 170-learner
> price below do not. The delayed test follows the last practice by a median of 3.98 days (range
> 3.97–4.97), not "3–6". The within-learner recency contrast below uses the same scoring and carries
> the same caveat. See `studies/outcomes/order-trials-reanalysis/README.md`, section 2.
>
> **2026-10-08, later: the answer-level estimate (registered, not blind).** An amendment,
> `order-trials-reanalysis/patel_answers.py`, scores a problem correct when num3 and den3 are both
> right on first attempt. It was registered at `1e8b885`, its floor committed at `469cf62`, and it ran
> at `b4d36c2`. The registration came after the artefact, the step-level outputs and the 0.70 / 0.78
> arithmetic were all known, so it is not blind.
>
> - **Primary result.** DPosttest trained items: AM 0.683 (26) vs MA 0.772 (29), MA − AM +0.089,
>   learner-bootstrap 95% [−0.025, +0.203], d **+0.41 [−0.12, +1.02]** (MA − AM, so MA better, as
>   before), re-randomisation p 0.144. Verdict **UNINFORMATIVE (BELOW FLOOR)**: answer-level floor
>   power at 8 points is 0.30.
> - **Reproduction.** The paper's 70% / 78% reproduce on that cell, within 0.02.
> - **Immediate Posttest** (secondary): +0.136, p 0.013, MULTIPLICATION FIRST BETTER ON ANSWERS
>   (UNDERPOWERED: ESTIMATE LIKELY INFLATED).
> - **Transfer items:** FLOOR FAILED on four items.
>
> The size of d is close to the step-level 0.43 by coincidence. In the regime table below, Patel's
> anchor should read d 0.41 (MA better) [−0.12, +1.02] on answers. On the point estimate a two-arm
> trial would need about 92 per arm, roughly 184 learners rather than 170. On the interval endpoint
> nearest zero it is still infeasible. The table and `regime.py` have not been rerun.

## Composition is clean — the ds1706 confound is absent

| | ADD | MUL | SUB *(transfer)* | DIV *(transfer)* |
| --- | ---: | ---: | ---: | ---: |
| AM | 33.5% | 33.7% | 16.4% | 16.4% |
| MA | 33.0% | 33.6% | 16.7% | 16.6% |

**0.5 points apart.** Unlike Study 1 — where blocked learners' final quarter was 96.3%
multiplication and the raw contrast manufactured d = −0.50 — there is nothing here to correct for.

## Result: no detectable order effect, and a consistent direction the study cannot resolve

| DPosttest item type | AM | MA | d | 95% bootstrap |
| --- | ---: | ---: | ---: | --- |
| ADD *(trained)* | 0.848 | 0.854 | −0.14 | [−0.74, +0.38] |
| MUL *(trained)* | 0.863 | 0.871 | −0.41 | [−0.82, +0.09] |
| SUB *(transfer)* | 0.841 | 0.846 | −0.14 | [−0.66, +0.42] |
| DIV *(transfer)* | 0.786 | 0.815 | −0.45 | [−1.05, +0.08] |
| **pooled** | **0.852** | **0.862** | **−0.43** | **[−0.93, +0.10]** |

**Verdict: `UNINFORMATIVE`.** The interval neither clears the MDE of 0.72 nor excludes a
Rohrer-sized 0.83 on the low side. At 30 per arm this study is ~88% powered for d = 0.83 and blind
to anything smaller.

**But all four item types point the same way.** Every contrast favours **MA — multiplication
first** — including both transfer types. Four of four is not significant by a sign test (p ≈ 0.125
one-tailed, and the types share learners so it is weaker still), but the point estimate of −0.43 is a
moderate effect sitting just under what 30 per arm can resolve. **This is the shape of a real effect
the study was too small to see**, and it is the opposite of a clean null.

## No recency — and the within-learner contrast proves it is sensitive enough to say so

The DPosttest contains both capabilities, so each learner supplies a last-practised-minus-first
contrast. The two arms come out with **opposite signs of near-equal size**:

| arm | practised last | last − first |
| --- | --- | ---: |
| AM | MUL | **+0.021** [+0.006, +0.037] |
| MA | ADD | **−0.017** [−0.031, −0.005] |
| pooled | — | **+0.001** [−0.010, +0.012] |

Re-expressed, both arms say **MUL − ADD ≈ +0.02**. That is not recency, it is multiplication being
slightly easier than addition, identically in both arms. The pooled contrast — which is what isolates
recency — is **+0.001**.

**This matters because it calibrates the instrument.** The within-learner contrast detects a
two-percentage-point capability difficulty difference with intervals excluding zero, and finds
*nothing* for recency. The measurement is sensitive; the recency effect is absent. Anything that
reads "whatever came last is retained better" out of this data is reading the calendar.

## What it costs to finish

To detect the observed **d = 0.43** at 80% power: **85 per arm, 170 learners total.** To detect 0.50:
126 total.

That is a very different ask from C2's standing 1,087–6,410, and it is for a design that **already
exists, is already validated, and already has the delayed outcome** — Patel's Study 2, run at 3× the
sample. It is the most concrete route to `C2` this programme has found.

```
python3 ds1190_order.py --reps 10000
```

Reads ds1190 from DataShop. Research use, no redistribution: the raw export stays in the session
scratchpad and only aggregates are committed.

---

# Rohrer's d = 0.83 reproduces exactly, and carries a design effect of 4.30

`rohrer_osf.py` recomputes the headline from the authors' own item-level data
([osf.io/pfeg4](https://osf.io/pfeg4)) rather than from the paper. 787 students with complete
scores, 16 items, 54 classes, 5 schools.

**It reproduces: interleaved 0.607 against blocked 0.376, d = +0.828 against a published +0.83.**
That settles the transcription question — the number this programme has been pricing against is
real and correctly read.

## The clustering the headline does not carry

The trial randomised **classes**, not students, and the published d is computed across students as
though they were independent.

| | |
| --- | ---: |
| class-level ICC | **0.243** |
| mean class size | 14.6 |
| design effect `1 + (m−1)ρ` | **4.30** |
| 787 students are worth about | **183** independent ones |
| cluster bootstrap on d, classes resampled whole | **[+0.58, +1.10]** |

**Power on the lower bound.** A point estimate from a clustered design is how a replication ends up
underpowered while believing itself generous. On +0.83 a two-arm trial needs 46 learners; on +0.58
it needs **94**. The second number is the honest planning input.

## It is not uniform across skills

| skill | d |
| --- | ---: |
| graph | **+0.86** |
| inequality | +0.63 |
| expression | +0.40 |
| circle | **+0.34** |

Spread **0.240** against a label-permutation null 97.5th of **0.123** → **CONCENTRATED**. Interleaving
did not lift four skills equally. That concentration is structure, and it is the north star's
question asked inside someone else's trial.

---

# The regime question, settled on three anchors: `regime.py`

C2's price turned on an effect size nobody here had measured. Three anchors now exist, and the
important thing about them is that **they are not three attempts at one number.**

| anchor | d | randomised by | dose | outcome delay | n |
| --- | ---: | --- | --- | --- | ---: |
| Rohrer 2020 (recomputed) | **+0.83** [+0.58, +1.10] | **class** (deff 4.30) | 4 months | 1 month, unannounced | 787 |
| Ostrow 2015 (published) | **+0.22** | **student** | 1 homework, 12 problems | 2–5 days | 146 |
| Patel ds1190 (recomputed) | **−0.43** [−0.93, +0.10] | **student** | order of two capabilities | 4 days | 60 |

Ostrow, Heffernan, Heffernan & Peterson (2015), *AIED 2015*, LNAI 9112 338–347
([ERIC ED656930](https://files.eric.ed.gov/fulltext/ED656930.pdf)) is the anchor that matters most
for design, because of three properties no other has together: assignment is at the **student**
level — the authors say explicitly it was done that way "rather than the class level to control for
potential teacher and class effects" — the outcome is a **delayed** posttest, and the dose is a
**single session**. Its materials link (`tiny.cc/AIED-2015-Interleaving`) is dead, so these are the
published numbers, not a reanalysis.

**Its headline does not reach significance: g = 0.22, F(1,143) = 2.69, p = 0.103.**

### What a two-arm trial costs at each anchor

| anchor | d | on the point | on the lower bound |
| --- | ---: | ---: | ---: |
| Rohrer 2020 | +0.83 | 46 | **94** |
| Ostrow 2015 | +0.22 | **649** | — (no interval published) |
| Patel ds1190 | −0.43 | 170 | infeasible (CI contains zero) |
| *C2's standing assumption* | +0.17 | *1,087* | |
| *C2's standing assumption* | +0.07 | *6,408* | |

Two implementation notes, both of which changed a number:

- **The floor caught a real discrepancy and it was mine, not the paper's.** Ostrow's g = 0.22 does
  not follow from F = 2.69, which implies 0.27. Both are right: the F is from an **ANCOVA** with
  skill level as a covariate, which strips variance from the error term, while 0.22 is the raw-means
  g. They are different estimands. The check now reads each row against the statistic that matches
  its model, and the two plain-ANOVA rows reproduce to two decimals from both directions.
- **"Lower bound" must mean the interval endpoint nearest zero.** Taking the endpoint furthest from
  zero priced ds1190's [−0.93, +0.10] at **37 learners** off −0.93 — the optimistic bound wearing an
  interval's clothes. An interval containing zero places no lower bound on the effect at all, and
  the honest entry is *infeasible*.

### The regime depends on the dose

Rohrer interleaves for **four months** and tests a month later. Ostrow interleaves for **one
homework** and tests three days later. Reading +0.83 as the planning input for a single-session
trial is precisely how a study gets powered at 46 when it needs six hundred.

**C2's standing 1,087–6,410 is too high, but not by the factor 0.83 suggests.**

---

# Sana & Yan: the within-subject anchor, and the concept confound that eats its headline

`sana_yan.py`, on [osf.io/aqng6](https://osf.io/aqng6) — *Interleaved Retrieval Practice Promotes
Science Learning*. 2,480 concept-level observations, **155 high-school students**, 8 classrooms,
5 teachers, 6 course-grades, 95 concepts, four weeks of real science classes.

Every anchor in `regime.py` is **between** learners, and between-learner variance is the dominant
term in all three prices. This is the one that tests whether it has to be paid. Blocked,
interleaved and unpractised control all run **within each student**.

## The design is exactly as balanced as it claims

Every one of the 155 students contributes 4 blocked, 4 interleaved and 8 control concepts, and all
24 course-grade × week cells are balanced on schedule. **155/155 and 24/24.** The learner
differences away exactly, with no weighting. This is a better-built trial than anything else on
this board.

## The confound, found before fitting anything

Of 47 practiced concepts, **only 17 appear under both schedules**, and they live entirely in two of
the six course-grades:

| course-grade | concepts | under both | |
| --- | ---: | ---: | --- |
| Biology11 | 8 | 8 | counterbalanced |
| Science9 | 8 | 8 | counterbalanced |
| Chemistry12 | 8 | **0** | **CONFOUNDED** |
| Physics11 | 8 | **0** | **CONFOUNDED** |
| Physics12 | 8 | **0** | **CONFOUNDED** |
| Science10 | 8 | **0** | **CONFOUNDED** |

In those four courses every concept appears under exactly one schedule, so interleaved-minus-blocked
there is inseparable from *which concepts happened to get which schedule*. A crossed random effect
for concept shrinks this but cannot remove it — there is no within-concept contrast to estimate from.
**610 of 1,240 practiced rows (49.2%) sit on a counterbalanced concept.**

This is the ds1706 failure exactly, and the control is the same one: read the contrast where, and
only where, the same material appears on both sides.

## Result

| contrast | | | diff | 95% CI | d_z |
| --- | ---: | ---: | ---: | --- | ---: |
| interleaved − blocked, **all rows** | 0.634 | 0.540 | **+0.094** | [+0.039, +0.147] | +0.271 |
| interleaved − blocked, **counterbalanced only** | 0.583 | 0.510 | **+0.073** | **[−0.017, +0.156]** | +0.194 |
| interleaved − control | 0.634 | 0.470 | +0.164 | [+0.120, +0.207] | +0.590 |
| blocked − control | 0.540 | 0.470 | +0.070 | [+0.023, +0.119] | +0.226 |

**The interleaving advantage does not survive the concept control.** The point estimate falls only
from +0.094 to +0.073, but on the 72 students who carry the same concepts on both sides the
interval contains zero. What *does* survive is **retrieval practice itself** — both practiced
conditions beat unpractised control comfortably, and that contrast is not exposed to this confound.

**It is not concentrated across concepts**: spread 0.151 against a within-student permutation null
97.5th of 0.219. The null shuffles the schedule label *within* a student, which is the unit the
schedule varied on. Unlike Rohrer across skills and Ostrow across learners, this effect is flat —
which is itself worth having, because it means the two concentration findings are not an artefact
of the concentration test.

## The classroom bootstrap is not usable here, and saying so is the finding

Resampling classrooms whole returns **[+0.046, +0.103]** on the counterbalanced contrast — *narrower*
than the student-level interval, which is a giveaway rather than a result. Only **4** classrooms
contribute a paired student, so the between-cluster variance rests on 3 degrees of freedom, and the
four room means (+0.045, +0.047, +0.092, +0.117) sit closer together than the within-room noise
alone would predict. A percentile cluster bootstrap on 4 clusters under-covers; this is an unstable
estimate that landed narrow, not a tighter one. **It does not rescue the counterbalanced contrast.**
The binding interval stays the student-level one, which contains zero. The script now refuses to
read a cluster interval below a pre-set floor of 10 clusters.

Two bugs were fixed to get there, both of the resampling-unit kind this repo keeps re-learning:
a classroom drawn twice **collapsed into one student** because the per-student aggregation keys by
ID, so the "bootstrap" only varied which rooms were present; and drawing all 8 rooms when only some
contribute duplicated the contributors and inflated the effective *n*.

## What it buys C2

On the counterbalanced contrast, **d_z = +0.194 within** against **d = +0.253 between**:

- within-subject, two conditions per learner: **210 learners**
- the same effect run between learners: **491 learners**
- → **2.3× cheaper for the same effect**

**This is a design saving, not a bigger effect.** d_z is larger than d because the learner's own
level is differenced away, not because interleaving did more. Quoting a within-subject d_z beside
a between-subject d without saying so is how a cheaper design gets reported as a stronger finding.

## Verdict

**`CONFOUNDED HEADLINE, USABLE DESIGN.`** The interleaving contrast does not survive its concept
control. The retrieval-practice contrast does, comfortably. And the design itself is the most
transferable thing here: a within-subject schedule manipulation inside real classes, fully
balanced, at a 2.3× discount — which is the lever C2 had not priced.
