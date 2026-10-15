# The tutor's own stopping rule fills the cell the tutor is built to keep empty

The [positivity audit](../overlap/README.md) shows why every structural null in this programme is
uninterpretable: a mastery tutor almost never lets a learner reach B without A, so the cell that
identifies a gate is empty. On Junyi, 2 of 775 authored edges have enough learners in it to read.

ASSISTments skill builders have a second exit. A learner leaves when they get three right in a row
— **or** when they run out of problems and are released anyway. The second exit is a learner the
system passed forward without mastery, and there are **28,608** of them. That is overlap,
manufactured by the same mechanism that destroys it everywhere else.

| | |
| --- | ---: |
| skill-builder runs of 5+ problems on one skill | 134,701 |
| exited with mastery | 106,093 |
| **released without it** | **28,608** |
| learners | 20,815 |
| (exit, downstream skill) observations | 1,283,084 |

## The design

Exit status alone proves nothing: learners who fail to master a skill are weaker learners and would
do worse on everything downstream for that reason. The test is the **contrast across downstream
skills**. Ability is one number per learner; a prerequisite is a claim about particular pairs. So:
is the penalty concentrated on some downstream skills and absent on others, beyond a null that
permutes exit status within ability strata?

The permuted unit is the **exit**, not the row. A learner leaves skill A once and carries that
status into every downstream skill they meet, so shuffling rows independently hands the same learner
both statuses at once and shrinks the null until anything looks significant. Row-level shuffling put
this at p = 0.0000; exit-level shuffling puts it at p = 0.0020.

## Result

| | |
| --- | ---: |
| raw gap, mastered − released | +0.0438 |
| ability-stratified gap | +0.0254 |
| readable edges (≥30 learners each side) | 1,644 |
| edge gap sd, observed | 0.1043 |
| edge gap sd, null | 0.0973 ± 0.0023 |
| **p, concentrated vs flat** | **0.0020** |
| **edge-specific component, sd** | **0.0373** |
| **split-half over learners, r** | **0.297** |
| full-sample reliability (Spearman–Brown) | 0.458 |

**The penalty is concentrated — the structure is real.** This is the first positive structural
result in the programme that does not depend on a model choosing its own shape, and it comes from a
near-experiment rather than a fit.

**It is also small and barely reliable.** The edge-specific component is 3.7 percentage points
against a flat ability gap of 2.5 — so most of the downstream penalty is the learner, not the pair,
and the part that is the pair is at the edge of what this much data can resolve. Split-half
correlation over learners is 0.297, giving a full-sample reliability of 0.458.

**The listed top edges are not findings.** At r = 0.297 the ranking is mostly noise; the result is
about the *variance* being non-null, not about which pairs are at the top. Anyone reading the
largest-penalty list as a discovered graph is reading sampling error.

For scale: a seven-rater human panel judging the same kind of claim reaches ICC 0.857
([expert-agreement](../../measurement/expert-agreement/README.md)). This detector, on 1.3 million observations,
reaches 0.458. **The cheapest reliable prerequisite instrument currently available is a room of
people, by a factor of about two.** That is not an argument against the data-driven route; it is the
bar it has to clear, stated in the same units for the first time.

## What to do with it

Scale is the obvious lever and the arithmetic is unkind: reliability grows like n, so matching a
seven-rater panel from this design needs roughly an order of magnitude more exits. The better lever
is the design — more overlap per learner rather than more learners. Every mechanism that releases a
learner without mastery is an instrument, and the skill-builder limit is only the most common one.

## Reproduce

```
python3 mastery_exit.py --out out/mastery-exit.json
```

Raw ASSISTments exports stay outside the repo under their redistribution terms; only the aggregates
here are committed.
