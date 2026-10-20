# Order-variation estimator: can the order learners met two skills orient an edge beyond difficulty?

Script: `order_variation.py`. Its docstring is the pre-registration. Outputs: `out/sim.json` (part 1),
`out/sim-posthoc.json` (post-hoc diagnostics, which gate nothing), `out/positivity.json` (part 2, no
outcome read) and `out/real.json` (part 3). Commits, in order: design `9c7a756` (before any number),
simulation `0de51f6`, CHANGES after the simulation `47c6e60` (before any real row), positivity
`ceed51a`, then the real reading.

## What was asked

Paper II (5.1, Answer to RQ1) shows that the atlas's orientation statistic is identically a sort
from the easier skill to the harder one. It narrows its claim: the identity "does not rule out an
estimator that uses variation in the order learners met the skills together with a later outcome".
Doroudi, Holstein, Aleven & Brunskill (EDM 2016, SCOVA; literature-sweep-2 A.4) found a data-preferred
order that ran against difficulty. This study builds such an estimator, floors it in the
orientation-sortability worlds under random and ability-driven order, and reads it on corpora that
have order variation.

**Estimator (ORDER-ADJ).** For a pair {u, v}, learners fall into a u-first arm or a v-first arm by
which skill they attempted first. The outcome is Y = Y_u + Y_v, where Y_x is accuracy on the
learner's first 3 attempts at x. Each skill is indexed by its own attempt count, so both arms are
compared at equal practice. The u-first advantage on this sum is exactly D_v − D_u: what meeting u
first does to v, minus what meeting v first does to u. It is positive for a true edge u → v. The
advantage is estimated by OLS, pair by pair, adjusted for prior ability: the learner's mean residual
first-attempt correctness (correct minus that unit's mean) on units met before both skills, plus
log(1 + the number of those units). The residual is the difficulty adjustment. The call is the sign
of the advantage, and it is compared with DIFFSORT, which orients from higher to lower first-attempt
accuracy. Variants: ORDER-RAW (no covariates); SCOVA-NEXT (pairwise SCOVA, with the outcome being
residual accuracy on the next 20 attempts after both skills are met); SCOVA-POST (simulation only:
a final assessment over all skills, since no held corpus has a common posttest).

## What came back

### Simulation (detection floor and confounding check)

Pre-registered headline for ORDER-ADJ: **`FLOOR FAILED; ABILITY-DRIVEN ORDER FOOLS IT`**.

The setup uses sortability.py's worlds (15 per cell, 30 nodes, 3,000 learners) with a dynamic
generator. Learners meet skills in an order. A prerequisite not yet mastered blocks acquisition
(hardness 1.0). Each meeting gives 3 attempts, followed by a review pass and a posttest. Accuracy is
the share of true edges oriented correctly. Intervals resample worlds (2,000 draws). D =
acc(ORDER-ADJ) − acc(DIFFSORT) on the same edges.

| cell (mechanism / regime / order) | ORDER-ADJ | DIFFSORT | D | reading |
| --- | --- | --- | --- | --- |
| AND / ALIGNED / RANDOM | 0.565 [0.516, 0.615] | 0.960 | −0.396 [−0.446, −0.344] | CEILING / ORIENTS |
| AND / INDEPENDENT / RANDOM | 0.537 [0.501, 0.582] | 0.956 | −0.419 [−0.451, −0.379] | CEILING / ORIENTS |
| AND / INVERTED / RANDOM | 0.571 [0.528, 0.609] | 0.945 | −0.374 [−0.413, −0.340] | **WORSE** / ORIENTS |
| OR / ALIGNED / RANDOM | 0.700 [0.656, 0.745] | 0.910 | −0.210 [−0.260, −0.167] | WORSE / ORIENTS |
| OR / INDEPENDENT / RANDOM | 0.848 [0.822, 0.872] | 0.771 | +0.077 [+0.026, +0.126] | **ADDS** / ORIENTS |
| OR / INVERTED / RANDOM | 0.942 [0.921, 0.963] | 0.721 | +0.221 [+0.188, +0.251] | **ADDS** / ORIENTS |
| NULL / ALIGNED / RANDOM | 0.438 [0.388, 0.490] | 0.979 | | REVERSED (registered: CHANCE) |
| NULL / INDEPENDENT / RANDOM | 0.456 [0.416, 0.493] | 0.492 | | REVERSED (registered: CHANCE) |
| NULL / INVERTED / RANDOM | 0.496 [0.448, 0.552] | 0.019 | | CHANCE |

The floor failed on two of its three parts.

- **Part (i) failed.** Under AND with random order, the dynamic gate blocks a dependent whenever it
  is met before its prerequisites. The gate therefore makes dependents look hard, so the difficulty
  sort sits at 0.945 to 0.960 even where latent difficulty falls with depth. The order effect left
  over is small: a dependent with several parents is acquired only when all of them were met first
  and mastered. Under OR, the estimator beats the sort where difficulty does not rise with depth
  (+0.077 INDEPENDENT, +0.221 INVERTED).
- **Part (iii) failed.** Two NULL cells, where the prerequisite is inert, read REVERSED at the edge
  of their intervals. The post-hoc diagnostic on 60 further worlds reads CHANCE in all three NULL
  regimes: 0.510 [0.487, 0.532], 0.509 [0.485, 0.534] and 0.483 [0.458, 0.508]. So this failure
  comes from a 15-world interval that is too narrow, not from a bias. It is reported, and it does
  not change the registered outcome.
- **AND at hardness 0.5 (post-hoc).** With a softer gate, ORDER-ADJ reads ADDS under INVERTED:
  0.733 against DIFFSORT 0.153, D +0.580 [+0.530, +0.633]. INDEPENDENT reads UNDECIDED (+0.056
  [−0.008, +0.118]).

**Confounding: ability-driven order fools it, adjustment included.** Under ABILITY order (abler
learners take the harder skill first) and NULL edges, ORDER-ADJ orients inert edges from the harder
skill to the easier. It scores 0.054 [0.025, 0.086] where difficulty rises with depth and 0.956
[0.936, 0.976] where it falls. In effect it becomes an anti-difficulty sort. Under SKIP (abler
learners deviate from the curriculum more often), it orients inert edges against the curriculum:
0.019, 0.044 and 0.019. It reverses true AND edges in INDEPENDENT (0.429) and INVERTED (0.354), and
true edges in AND/ALIGNED and OR/ALIGNED under ABILITY (0.346, 0.408). In these regimes the median
|SMD| of prior ability between arms is 0.41 to 0.79, against 0.03 under random order. The prior
adjustment is a noisy measure, so it removes only part of the ability gap. ORDER-RAW is fooled
further, for example 0.163 against 0.354 for AND/INVERTED/SKIP. CURRICULUM order (ability-free
deviations) does not fool it: 0.78 to 0.95 on true edges, and CHANCE on all NULL cells. SCOVA-NEXT
and SCOVA-POST are near chance on true edges under random order (0.49 to 0.59) and swing with the confound under
ABILITY and SKIP (0.01 to 0.08, or 0.97 to 0.98 under ABILITY/INVERTED). They are the most confoundable variants.

This bears directly on the Doroudi et al. reading. **In this generator, an order "preferred by the
data" against the difficulty order is exactly what ability-driven order choice produces on an inert
edge.**

### Positivity (no outcome read)

An eligible pair has at least 30 learners in each arm, counting only learners who met at least 3
other units before the earlier of the two skills.

| corpus | learners | eligible pairs | median minority arm (eligible) | reference pairs eligible | read? |
| --- | --- | --- | --- | --- | --- |
| EdNet KT1 (first 20,000 members, first tag) | 20,000 | 9,485 of 9,870 | 440 | none held | **yes** |
| ASSISTments 2012-13 | 28,998 | 6,449 of 19,673 | 118 | 1,669 of 6,988 CCSS cross-grade pairs | **yes** |
| Junyi 2015, ds1275 | 2,059 | 98 of 114,119 | 38 | **1** of 774 authored edges | no: UNANSWERABLE |
| Eedi NeurIPS 2020 | 118,971 | 28,676 of 43,222 (last-answer order) | 805 | none held | no: first-meeting order not recorded |

EdNet was chosen over Eedi. Eedi has the larger positivity count, but its time is the latest answer
to each question, so the treatment (which skill came first) is not recorded. That exclusion was
registered before the count. Eedi was counted with a memory-light counter (CHANGES 4); it matched
the full builder exactly on Junyi and ASSISTments.

### Real data

Every registered verdict is **UNANSWERABLE**, because the simulation floor failed. The registered
rule's own reading was computed descriptively (CHANGES 3) and is not a verdict.

Two intervals are reported. The LEARNER interval comes from Poisson bootstrap weights on the unit
the order is assigned to: learners for EdNet, the cohort proxy (class) for ASSISTments. Each of its
200 draws recomputes every pair's estimate and every unit's difficulty. The SKILL interval resamples
units and rebuilds the pairs (2,000 draws). The deranged control deranges arm labels within (pair,
prior-ability quintile), 20 times, so it is the treatment's size.

**ASSISTments 2012-13: descriptive reading `CONFOUNDED BY ORDER CHOICE`.** The reading before the
confounding rule is WORSE THAN DIFFICULTY. On the 1,669 eligible CCSS reference pairs:

- ORDER-ADJ agrees with grade order on 0.501 of pairs (cohort [0.477, 0.527], skill [0.448,
  0.554]). DIFFSORT agrees on 0.648 (cohort [0.619, 0.665], skill [0.562, 0.730]).
- D = −0.146, with cohort interval [−0.180, −0.110] and skill interval [−0.243, −0.050].
- On the 826 discordant pairs, ORDER-ADJ follows grade order on 0.352.
- The deranged control agrees with grade order on 0.502 (range 0.485 to 0.516 over 20 runs). On
  the reference, the estimator therefore does no better than order labels shuffled within ability
  strata.
- Balance (median |SMD| of prior between arms) is 0.206, above the registered 0.10. Order on
  ASSISTments is tied to ability, in a regime the simulation showed the adjustment cannot handle.
- The estimator does carry order signal: mean z² is 6.70 against at most 1.05 under the control. That
  control is at learner level while order is set per class, so this line is descriptive, as
  registered.
- The real-shaped floor passed: a planted 0.05 was recovered and read ORIENTS BEYOND DIFFICULTY in
  20 of 20 reps, and with nothing planted the interval excluded 0.5 in 0 of 20.

**EdNet KT1: descriptive reading `ORDER ORIENTATION INDEPENDENT OF DIFFICULTY (ORDER SIGNAL
PRESENT)`.** On 9,485 eligible pairs:

- ORDER-ADJ agrees with DIFFSORT on 0.489 (learner [0.479, 0.522], skill [0.445, 0.532]). The
  control gives 0.501.
- Signal: mean z² is 3.39 against at most 1.05 for the 20 derangements.
- Balance is 0.096: under the registered 0.10, so the confounding rule does not fire, but three
  times the 0.03 seen under random order in the simulation.
- The real-shaped floor passed (minimum detectable 0.05).
- With no authored order held for EdNet, departing from difficulty is not evidence of being right.
- SCOVA-NEXT agrees with difficulty on only 0.368. That is the practice and window confound
  registered as its weakness, and it is not read further.

## What it means for Paper II's RQ1 caveat and for Paper VII

The narrowed sentence stands as written, and it gains a condition. An order-variation estimator
does beat the difficulty sort, but only where order is random with respect to ability and difficulty
does not rise along the edges (OR, and AND with a soft gate, under random order). Even then, under
a hard AND gate, the gate itself makes the sort near-perfect. When abler learners choose or are given
harder or later skills first, the estimator, prior adjustment included, orients inert edges
confidently, from harder to easier or against the curriculum. A data-preferred order against
difficulty, the Doroudi et al. pattern, is therefore also what ability-driven order choice produces,
and it needs randomised order to be read causally. On the held corpora:

- ASSISTments' order is ability-tied, and its order-based calls agree with CCSS grade at chance,
  below the difficulty sort.
- EdNet's calls carry signal but sit at chance relative to difficulty, with no reference to say
  which is right.
- Junyi's authored graph cannot be read: 1 eligible edge.
- Eedi does not record first-meeting order.

No verdict here is a finding about real edge direction.

## Cannot say

- The direction of any real edge.
- Anything about generators outside this family.
- Whether the 20,000-learner EdNet prefix represents KT1.
- Anything about ASSISTments as a graph: CCSS grade is an order, and most cross-grade pairs are not
  prerequisites.

Every number is descriptive under a failed simulation floor.

    python3 order_variation.py sim            # ~1 min -> out/sim.json
    python3 order_variation.py sim-posthoc    # -> out/sim-posthoc.json (gates nothing)
    LDA_SCRATCH_DIR=... python3 order_variation.py positivity --corpora junyi,assist,ednet
    LDA_SCRATCH_DIR=... python3 order_variation.py positivity --light --corpora eedi
    LDA_SCRATCH_DIR=... python3 order_variation.py real   # ~40 min (EdNet ~33)

Data: EdNet KT1 (CC BY-NC 4.0), Eedi (research use; positivity only), ASSISTments 2012-13 (analysis
only) and DataShop ds1275 / Junyi 2015 (research use). All are read from the scratchpad through
`shared.paths.data_path`. Only aggregates are committed.
