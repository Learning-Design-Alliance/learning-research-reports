# Settling the bar: neither standardiser works, and the rule that made it urgent was broken

> **Re-issued 2026-09-24 ([`docs/notes/EDNET-REISSUE.md`](/docs/notes/EDNET-REISSUE.md)):** on a reproducible EdNet learner set, `relative_bar.py`'s corpus scope is **UNANSWERABLE** (was STRUCTURE) and `reliability_bar.py` **REPLICATES** (was DOES NOT REPLICATE).

`ednet_at_scale.py` left a specification question: should an assertable effect be defined
**absolutely** or **relative to the corpus it is measured in**? Two candidate standardisers were
tested against pre-registered floors. **Both failed.** A third thing — a defect in the decision rule
they were all judged by — turned out to matter more than either.

## 0. The decision rule was wrong by about 500×, and it manufactured a replication failure

Every verdict in this line asked whether the above-bar share beat `FDR_Q = 0.05`, reasoning it had to
beat "the false-discovery allowance". **That reasoning is wrong.** Benjamini-Hochberg at q bounds the
false discovery proportion *among rejections*; under a global null it rejects approximately nothing,
not 5% of tests.

The replacement is this programme's own idiom — a matched null rather than a convention. The **whole
pipeline**, scoring and BH and the bar, is re-run on learner-deranged data:

> **deranged pipeline null: share 0.0000, 97.5th percentile 0.0001.**

Re-adjudicated against that:

| arm | bar | share | 95% block CI | power | verdict |
| --- | ---: | ---: | --- | ---: | --- |
| XES3G5M | +0.100 | 0.108 | [0.062, 0.170] | 75.0% | **STRUCTURE** |
| XES3G5M | own +0.1073 | 0.097 | [0.054, 0.159] | 78.1% | **STRUCTURE** |
| XES3G5M | family +0.1139 | 0.086 | [0.046, 0.139] | 80.3% | **STRUCTURE** |
| EdNet | +0.100 | 0.016 | [0.003, 0.035] | 100% | **STRUCTURE** |
| EdNet | own +0.0491 | 0.078 | [0.036, 0.130] | 92.2% | **STRUCTURE** |

**`replicate.py`'s `FAILS` verdict was an artefact of the broken rule.** EdNet carries conjunctive
structure at the same +0.10 bar XES3G5M's claim was stated at, at 100% power, against a null of zero.
Both corpora carry it. They differ in **how much** — about 7× at the fixed bar, 1.4× at each corpus's
own — and the rest of this file is about whether that difference is the instrument.

## 1. Relative to the corpus's own background — `NOT ADOPTED`

The argument for it was strong: +0.10 was never a constant, it was *defined* as the background an
arbitrary ordered pair already shows, which is XES3G5M's +0.1073 hard-coded. EdNet's is +0.0491.

Both pre-registered gates failed.

**(a) Scale invariance — the entire case — does not hold.** Two synthetic corpora, identical except
every effect multiplied:

| | share at 1× | at 2.0× | drift |
| --- | ---: | ---: | ---: |
| relative bar | 0.034 | 0.013 | **63.6%** |
| fixed bar | 0.031 | 0.049 | 60.2% |

**(b) `CONTAMINATED`.** Planting conjunctions moved the measured background from +0.0302 to +0.0843
— **+27.1% of the planted conjunction's own size**, against a 20% tolerance — costing 8.4% of the
above-bar triples. The mechanism is `stage1_floor.py`'s blind spot seen from the other side: a
conjunctive gate reads **+0.083 pairwise**, so conjunctions are *inside* the background that would
define the bar. **A yardstick partly made of the thing being measured cannot be the yardstick.**

## 2. Standardise by reliability — `NOT ADOPTED`, for two independent reasons

Reliability looked like the right standardiser precisely where the background was wrong: measured on
learners from repeated attempts, so independent of the conjunctive statistic rather than made of it.

**The attenuation model is real, and this is the finding worth keeping.** Noise in the *outcome* does
not bias a difference of means. Noise in the *predictor* does — "held A" is a noisy indicator of
mastering A — and an interaction rides on **two** such indicators, so it should attenuate by roughly
the square. Measured on planted data with indicators corrupted to known reliability:

| r | main effect | interaction |
| ---: | ---: | ---: |
| 0.890 | ×0.891 | ×0.761 |
| 0.883 | ×0.805 | ×0.633 |
| 0.722 | ×0.734 | ×0.473 |
| 0.711 | ×0.663 | ×0.431 |

> **main effects attenuate by r^1.17, interactions by r^2.34.**

That is a general statement about why conjunctive structure is systematically harder to see than
pairwise structure in any noisy corpus, and it holds independently of everything below.

**Reason one it cannot be used as a bar: disattenuation restores effect size, not power.** Correcting
a corrupted corpus moved its share from 0.0069 to 0.0126 against a clean 0.0349 — still **64% short**
of the right answer, against a 25% tolerance. BH selection runs on the raw z, which rescaling does
not touch, so triples that *lost significance* to noise cannot be resurrected by multiplying up the
survivors.

**Reason two, and it is fatal to the motivation: there is nothing to standardise.**

| arm | indicator reliability (odd/even attempt split, Spearman-Brown) |
| --- | ---: |
| XES3G5M | 0.419 |
| XES3G5M coarse | 0.440 |
| **EdNet** | **0.406** (re-issued: **0.481**) |

**Ratio 1.03** (re-issued 2026-09-24: 0.481 against 0.419, ratio about 1.15, so EdNet's indicator is now slightly *more* reliable). The corpora are about equally reliable *at the indicator level*. EdNet is not a noisier
instrument, and attenuation cannot explain a 7× gap between corpora that differ by 3% in reliability.

**My argument for trying this was wrong, and specifically wrong.** I motivated it with
`split_half.py`'s 0.572 against 0.315, a ratio of 1.82 close to the background ratio of 2.19. But
`split_half.py` measures the reliability of the **edge statistic** across halves of the learner pool,
not the reliability of the **indicator**. They are different quantities and only the second is what
the attenuation argument needs. Measured properly, the ratio is 1.03 and the argument evaporates.

**A bug in this study's own verdict logic, found and fixed.** Applying the correction anyway moves
XES3G5M 0.108 → 0.216 and EdNet 0.016 → 0.159, whose intervals *do* overlap, and the first version
printed `REPLICATES` off those numbers — on a scale its own floor had just refused. It also would
have been an artefact: the two attenuation factors are near-identical (0.114, 0.120), so the
correction is close to a uniform rescale, and it changes the *share* by 2.0× for XES3G5M and 9.9× for
EdNet only because EdNet's distribution sat just below the bar. The verdict now takes whichever scale
the floor licensed.

## The settled answer

**Keep the absolute bar. Fix the decision rule. The corpora genuinely differ.**

- The bar stays at a fixed +0.10, not because it is principled but because **both alternatives are
  worse**: the background is contaminated by the signal, and reliability is equal across corpora so
  standardising by it is a no-op that only rescales.
- The decision rule becomes the **deranged pipeline null** (0.0000), never `FDR_Q`. Every verdict in
  this line judged against 0.05 needs re-reading, and three of them flip.
- The 7× gap between XES3G5M and EdNet is **not** the instrument. Equal indicator reliability rules
  out attenuation; equal power at the bar (100% on EdNet) rules out detection. It is a real
  difference between a curated expert KC hierarchy and a set of 142 platform tags.

**What does not follow.** A relative bar is not wrong *in principle* — it failed at the conjunction
density our corpora actually show, and the floor's answer moved with that density, which is recorded
in `relative_bar.py` rather than smoothed over. And "equal reliability" is measured on the 30
best-covered items of each corpus; it is not a claim about either corpus as a whole.

```
python3 relative_bar.py --arm xes3g5m|xes3g5m-coarse|ednet
python3 reliability_bar.py --items 30 --draws 1000
```

Reads XES3G5M and EdNet. EdNet is CC BY-NC 4.0 — non-commercial, no model training. Raw exports stay
in the session scratchpad; only aggregates are committed.
