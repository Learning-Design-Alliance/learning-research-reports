# Order, reversed: the first randomised test of sequence on this board

**Asked.** Three Clements/Sarama learning-trajectory trials looked like the causal version of the
programme's question: does following a prerequisite order produce more learning than the same
instruction out of order?

**Answer. On the one trial whose data is actually deposited: ORDER MATTERS, FRAGILELY.** Same ten
12-minute activities, same dose, randomised within 16 kindergarten classrooms; only the order
differs. Trajectory order beats reverse order by **+0.317 logits [+0.067, +0.566]** in the authors'
own model, about **0.28 posttest SD**, and survives re-randomisation inside classes (**p = 0.032**).
But a third of it sits in seven children — all seven top-5% posttests are in the trajectory arm —
and dropping them leaves **+0.191**, with the class-cluster bootstrap just touching zero.

## What was deposited is not what the titles say

| ICPSR package | title | actually contains |
| --- | --- | --- |
| 151741 | length measurement, LT vs reverse vs BAU (n = 187) | ✅ that study: `C6 Analysis File.xlsx` + the authors' R syntax |
| 168361 | early arithmetic, LT vs teach-to-target (n = 291) | ❌ **length again**: a 133-column item-level version of the same C6 file, codebook, BMLM models |
| 168846 | shape composition, LT vs skip levels (n = 145) | ❌ **a different arithmetic study**: 26 gifted kindergartners, one class per arm |

The 291-child arithmetic RCT and the shape-composition trial are not in either package. The
26-child arithmetic pilot randomised **one class to each arm**, so it has two clusters and cannot
carry a causal contrast; it is not analysed.

## Result (`length_order.py`)

| | LT − REV |
| --- | --- |
| authors' model: posttest ~ condition + scale(pre) + gender + private + (1\|class) | **+0.317 [+0.067, +0.566]** |
| class fixed effects | +0.301 (+0.28 pooled SD) |
| **within-class permutation** — the randomisation the design used | **p = 0.032** |
| class-cluster bootstrap | [−0.009, +0.508] |
| median regression | +0.395 [+0.041, +0.750] |
| rank outcome | +0.104 of the distribution |
| drop the top 5% of posttests (7 children, all LT) | +0.191 |

Floor: the authors' model reproduces the abstract's direction and significance (LT − BAU +0.582,
REV − BAU +0.265, LT − REV +0.317). The paper's Table 9 figures were not available here to compare
digit by digit.

## What it means for the board

- **C2 gains its first anchor where the SEQUENCE is what was randomised.** Every earlier anchor
  randomises something else. ~0.28 SD from 120 minutes of reordered instruction sits far above the
  d ≈ 0.05 prior `studies/outcomes/ope/j6esa_power.py` measured for assorted ASSISTments interventions — but it is
  one study, 16 classrooms, a tail-carried effect, and published, so the selection j6esa exposed
  applies to it too.
- **A4 material, not yet used.** The 133-column file tags all 26 items to the trajectory's seven
  levels, pre and post. The POSTTEST gave every child all 26 items; the pretest stopped after three
  consecutive errors in trajectory order, so any order read from the pretest is partly the stop
  rule and it must not be used for recovery.

Terms: AERA/ICPSR open data — statistical analysis only, no re-identification. Data stay in the
scratchpad; race, language-proficiency and assessor columns are never read.

## Class ICC for the edge-release power statement (`icc.py`)

**Asked** (handover 2026-10-09, Task 3; literature review strand 4, "Analyses" items 2 and 7). What
class ICC do the trajectory trials' own data imply, and does it replace the borrowed classroom planning
values (Hedges & Hedberg 0.15-0.25, school level) in `studies/outcomes/order-swap-remnant/out/power.json`?
Can the trajectory trials be pooled?

**Pre-registration.** The `icc.py` docstring sets the estimator, the outcome for each deposit, the
minimum class count, the floor, the verdict strings, the feed into the power table and the pooling rule.
It was committed with the floor (`out/icc-floor.json`) in 2ae3e25, before any outcome value was read. The
first registered interval, a percentile class bootstrap, failed the synthetic floor: coverage was
0.767-0.790 at planted rho 0.20-0.30 against the 0.80 required. One replacement was registered before
the run, BCa over the same class draws, and it passed. The docstring records both.

**Answer. The length trial's class ICC is about 0.39: higher than either value power.json uses, and
too imprecise to replace them. PLANNING VALUES STAND, and the trial's upper bound is the conservative
case.**

| | |
| --- | --- |
| class ICC, posttest theta, arm-centred (151741) | **0.395, 90% BCa [0.226, 0.582]**, 2,000 draws resampling the 16 classes |
| the v1 percentile interval on the same draws (failed the floor; shown only for comparison) | [0.180, 0.527] |
| clustering test, class labels permuted within arm (2,000) | p = 0.0005, the smallest value 2,000 permutations can give |
| classes / children | 16 / 187. Class sizes 4, 5, 6, 7, 8, 8, 10, 11, 13, 14, 16, 16, 16, 17, 18, 18 (median 12). No posttest is missing. |
| after the pretest (OLS on arm + PreTheta, slope 0.570) | conditional ICC 0.341; eta_B 0.690, eta_W 0.870 |
| ceiling: posttest reliability 1 - mean(SE^2)/Var | 0.813. The implied true-score ICC is 0.486, so the observed 0.395 is the one a trial measured the same way would face. |
| scoring sensitivity: raw sum score TotalPostCorrect (168361, same children) | 0.348 [0.231, 0.453] |
| verdict | **CLASS ICC ESTIMATED; OVERLAPS H&H RANGE; ABOVE ASSISTMENTS; TOO IMPRECISE TO REPLACE** |

The interval is 0.357 wide, against the 0.20 the replacement rule allows. Its lower bound lies above
ASSISTMENTS' 0.096, so the classroom clustering in this trial is not the platform's. The upper bound
lies above H&H's 0.25, so by the rule the hi90 row is the conservative case.

**Implied sample, edge release randomised by class** (`out/icc-power.json`). Same formula as
`remnant.py`: two arms, two-sided 0.05, power 0.80, normal approximation, with no t correction for
few classes. Each cell is classes per arm.

| d (SD) | this ICC 0.395, m = 13 / 20 / 12 | lo90 0.226 (m = 13) | hi90 0.582 (m = 13) | 0.395 with pretest (m = 13) | power.json H&H 0.15 / 0.25 (m = 13) | power.json ASSISTments 0.096 (m = 13) |
| --- | --- | --- | --- | --- | --- | --- |
| 0.05 | 2,772 / 2,670 / 2,797 | 1,791 | 3,858 | 1,967 | 1,353 / 1,933 | 1,040 |
| **0.10** | **693 / 668 / 700** | 448 | 965 | 492 | 339 / 484 | 260 |
| 0.30 | 77 / 75 / 78 | 50 | 108 | 55 | 38 / 54 | 29 |

At 0.10 SD and the length trial's ICC, a class-randomised edge-release trial needs about 700 classes
per arm (693 at 13 children per class), or 492 with a pretest. The H&H planning range gives 339-484.
Class size barely matters at this ICC: at m = 20 the figure is still 668, because the class term
dominates.

**Floor** (`out/icc-floor.json`): synthetic data built on 151741's 16 classes, using its class sizes
and its arm-by-class counts. Planted rho was 0, 0.05, 0.10, 0.20 and 0.30, under two shapes: NORMAL,
and TAIL (t5 errors, with the arm SD ratio from `length_order.json`). Each setting ran 300 replicates.
**PASS.**

- BCa coverage was 0.800-0.873, against 0.80 required.
- |bias| was at most 0.015, against 0.05 allowed.
- Under the null, the permutation test rejected in 0.047-0.050 of replicates, against at most 0.10
  allowed.
- At planted 0.10, the interval's lower bound cleared 0 in 0.70-0.76 of replicates.

A post-hoc check (`out/icc-floor-posthoc.json`, added after the run, changes no verdict) was run
because the estimate lay above the registered planted range. At planted 0.40 and 0.50, coverage was
0.777-0.853 and the mean estimate was 0.391-0.486. The nominal 90% interval therefore behaves like
roughly an 80% interval near this estimate. Read [0.226, 0.582] that way. The power-table arithmetic
reproduces every classroom cell of power.json before printing a new one.

**Other deposits.**

- **168361: NOT A SEPARATE TRIAL.** It holds the same 187 SIDs as 151741, with the same class and arm
  for each child, and posttest theta identical to 151741 (max |diff| 0). Its codebook's description of
  Total_Post copies PRE_TotalR's figures (0-20). The column's observed range is 0-26.
- **168846: UNANSWERABLE: CLASS CONFOUNDED WITH ARM.** It has 2 classes of 13, and class equals arm.
  The floor fails by construction: the arm-centred class means are fixed at 0, so the estimate is
  always -0.083 whatever is planted. Its outcome was never opened.

**Pooling: NOTHING TO POOL.** Only one independent trial reaches an estimate. The ICC pooling rule
requires two or more independent trials. Item 7's pooling of the order effects needs the patterning,
shape and arithmetic trials' learner data, and none of it is in these deposits.

**Post hoc, descriptive, not registered.** Point ICCs within arm subsets were BAU 0.494, REV 0.531,
LT 0.427, and REV+BAU 0.471. So the clustering is not the LT arm's tail. Each arm has only 3-5
children per class, which makes these noisy.

**What it can and cannot say.** It is one trial with 16 classes. The trial randomised children
within class to pull-out instruction, so the class component also carries school differences: 6
schools, private and public. That makes the classroom ICC comparable to H&H's school-level values
rather than smaller than them. The result says the classroom planning values in power.json are not
conservative for this kind of outcome, because the trial's own ICC is above them. It does not pin the
ICC down well enough to replace them. Paper II section 6 is for the drafting session to update; this
study does not edit it.

**Coders.** None. Every construct is a deposit's own score (Rasch theta, raw sum), the deposit's class
and arm labels, or arithmetic on them. No person or model coded anything.

**Run record (2026-10-08).** The data are the three unpacked ICPSR deposits under
`$LDA_SCRATCH_DIR/lt-trials/`. The maintainer's uploaded outer zips match the registry's byte sizes
but not its MD5s, because the upload re-wrapped each deposit in a new zip. This is not an error: the
deposit contents are what was read, and 168361's SIDs, classes, arms and posttest theta match
151741's exactly. Race, ethnicity, date of birth, language-proficiency and assessor columns were never
read. The loaders select columns by header before building any table. Commands:
`python3 icc.py --floor`, `--run`, `--floor-posthoc`.

## Does the order effect vary across classes? (`effect_variation.py`)

**Asked** (literature sweep 2, B.16, Weiss et al. 2017; Paper II 5.3). Children were randomised within
class, so a class-resampling interval is governed by how much the LT − REV effect varies across classes
(tau), not by the outcome ICC. How large is tau, and can 16 classes estimate it?

**Pre-registration.** The `effect_variation.py` docstring fixes the estimand, estimator, interval, test,
floor and verdicts. It was committed in aee86b2 before any per-class effect or effect variance was
computed; what had already been seen is listed there (length_order.json, icc.json). The floor was
committed in c1dc98a before the run.

- **Estimand:** tau, the between-class SD of the pretest-adjusted LT − REV effect on posttest theta.
- **Estimator:** DerSimonian-Laird over 15 per-class effects. Class 7 has no REV child and enters only
  the pooled pretest slope. Each per-class sampling variance uses arm-specific within-class variances
  POOLED over classes, so a class with one child per arm (class 5) still gets one, and the LT arm's
  spread enters every LT mean.
- **Interval:** 95% Q-profile. It resamples nothing; it inverts Q against chi-square(14).
- **Test of tau > 0:** within-class permutation of the LT/REV labels under the sharp null of a COMMON
  effect (impute y − δ·arm, permute, add δ back, refit everything). Berger-Boos over the δ 99.9%
  interval; 2,000 permutations per grid point.

**Answer. CANNOT ESTIMATE (floor): 16 CLASSES TOO FEW TO SEE tau 0.4.**

| | |
| --- | --- |
| common effect, class FE (LT/REV children, 130) | +0.301 (as length_order.py) |
| **tau, DL** | **0.418 logits, 95% Q-profile [0, 1.141]** |
| tau, REML on the same per-class effects | 0.317 |
| Q / df | 24.1 / 14 |
| **p, tau > 0** (Berger-Boos; plug-in δ) | **0.445** (0.288) |
| classes with a positive per-class effect | 11 of 15 |
| sensitivity: classes with ≥ 2 per arm (14) | tau 0.421 [0, 1.184] |
| sensitivity: drop the top 5% (7 children, all LT) | δ +0.191, tau 0.446 [0, 1.126] |
| sensitivity: child-level random-slope mixed model (homoscedastic) | arm +0.246, slope SD 0.432 |
| class bootstrap of δ, re-run (2,000) | [−0.027, +0.509], SD 0.135 |
| SE of the common effect at tau 0 / tau 0.418 / tau 1.141 | 0.126 / 0.170 / 0.326 |

The point estimate of tau is larger than the effect itself, and the interval runs from 0 to almost
four times the effect. The data neither show variation nor rule out variation large enough to reverse
the effect in some classes.

**Floor** (`out/effect-variation-floor.json`). The worlds were synthetic, on the real LT/REV class
structure, with a common effect of 0.30 and the raw arm SDs. There were 500 replicates per world.
**PASS.**

- Under tau 0 the verdict test rejected in 0.014-0.020 of replicates, against at most 0.10 allowed.
  The worlds were normal, heteroscedastic, a one-arm mixture tail (1 LT child in 10 jumps 3.29 logits,
  LT SD 1.24), and one-arm t3. So a tail confined to one arm is not mistaken for class variation.
- Q-profile coverage was 0.930-0.944 at planted tau 0.2 and 0.4, against 0.85 required.
- **Power was low.** At tau 0.4 it was 0.144 with the tail and 0.250 normal. At tau 0.2 it was
  0.048-0.056.
- The median upper bound under tau 0 was 0.68-0.88.

**Post hoc, changes no verdict.**

- **Power at the trial's own noise** (`out/effect-variation-floor-posthoc.json`). The run's residual
  SDs after the pretest are 0.877 (LT) and 0.478 (REV), smaller than the raw SDs the floor used.
  Re-run at that noise, power with the tail is 0.058 at tau 0.2, 0.316 at tau 0.4 and 0.672 at
  tau 0.6. Even at the trial's real noise, 16 classes see a between-class SD of 0.4 less than a third
  of the time.
- **Why Q 24.1 is not significant** (`out/effect-variation-posthoc.json`). Against chi-square(14), Q
  would give p 0.044. The within-class permutation null of Q is centred at 22.6 (median 22.0, 95th
  percentile 30.4), not at 14. One class with 2 LT and 2 REV children (per-class effect −2.42) carries
  62% of Q. Q is high whichever way that class's labels fall, so it reflects a class whose children
  differ a lot. It is not evidence that the effect differs. The synthetic worlds had equal
  within-class variance in every class, so they did not show this. The Q-profile interval rests on the
  same chi-square reference, so read [0, 1.141] as indicative. Its lower bound of 0 and its width
  stand either way.

**What it means for the class bootstrap in Paper II 5.3.** The bootstrap touching zero cannot be read
as "the effect depends on the class". Variation was not detected, and the design cannot detect
moderate variation.

- Its SD (0.135) is close to the inverse-variance SE of a common effect with no variation (0.126). It
  is not the 0.170 that the estimated tau would imply.
- In the registered tail world, a true common effect of 0.30 with tau 0 gives a class-bootstrap lower
  bound ≤ 0 in 0.58 of replicates. At the trial's own noise the post-hoc share is 0.30.
- So the touch is what this design gives a common effect of this size.

The sentence the paper can carry: 16 classes cannot estimate how much the order effect varies across
classes. The between-class SD is 0.42 logits, with a 95% interval from 0 to 1.14. A common effect and
one that changes sign between classes are both consistent with the data. Section 5.3 is for the
drafting session; this study does not edit it.

**Coders.** None. Run 2026-10-08: `python3 effect_variation.py --floor`, `--run`, then post hoc
`--posthoc` and `--floor-posthoc`. Only Student ID, Class, Condition, PreTheta_1pl and Theta_post_1pl
are kept from the analysis file. Per-class effects are written only for classes with ≥ 2 children in
each arm.
