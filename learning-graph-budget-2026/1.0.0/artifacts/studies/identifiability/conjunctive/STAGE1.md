# Stage 1: the pairwise instrument is blind in a region that is not exotic

**Verdict: `BLIND SPOT CONFIRMED`.**

## The claim, stated narrowly

A conjunctive gate is *not* literally invisible to a pairwise contrast — among learners who mastered
A, the ones who also hold B can pass C, so the A-drop stays positive. It is **attenuated**, roughly
in proportion to how many learners hold the co-parent. The testable claim is therefore quantitative:
**is there a region where the pairwise reading falls below the background drop — the threshold every
real reading in this programme is judged against — while the interaction statistic still fires?**

There is.

| planted | P(B) | gate | pairwise A | interaction | null hi | reading |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| conjunctive | 0.2 | 0.00 | **+0.0834** | +0.3955 | +0.0467 | **pairwise null, interaction fires** |
| conjunctive | 0.2 | 0.25 | **+0.0624** | +0.3099 | +0.0531 | **pairwise null, interaction fires** |
| conjunctive | 0.2 | 0.50 | **+0.0407** | +0.2027 | +0.0584 | **pairwise null, interaction fires** |
| conjunctive | 0.4 | 0.50 | **+0.0862** | +0.1937 | +0.0567 | **pairwise null, interaction fires** |
| conjunctive | 0.8 | 0.00 | +0.3212 | +0.3925 | +0.0598 | both fire |

**4 of 12 conjunctive arms** sit in the blind region. The worst case is the one that matters: a
**hard** gate (γ = 0.00 — C is unreachable without both parents) whose co-parent is held by 20% of
learners reads **+0.083 pairwise**, under the **+0.10** background an arbitrary ordered pair already
shows on ASSISTments. This programme would record that as a null. The interaction statistic reads
**+0.396** against a null ceiling of **+0.047** on the same data.

## The control that makes it mean something

The interaction statistic would be worthless if it were a relabelled main effect. It is not:

- **`additive` arms** — two *independent* single-parent gates, no conjunction — **0 of 12 fired.**
  Pairwise fires on all of them (+0.10 to +0.21); interaction stays at −0.004 to +0.043, inside its
  null.
- **`none` arms** — neither parent matters — **0 of 4 fired.**

So the statistic separates *conjunction* from *two main effects*, which is the whole question.

## What this establishes, and what it does not

**Establishes:** this programme's accumulated nulls are **consistent with conjunctive structure**
rather than with the absence of structure, over a parameter region that is ordinary rather than
contrived. That is true independent of any corpus, and it is the finding.

**Does not establish:** that real learning is conjunctive. That needs Stage 3 on a corpus Stage 2 may
say does not exist. The honest framing is *"our nulls are consistent with X"*, never *"X is true"*.

## Method

`interaction = (m₁ − m₂) − (m₃ − m₄)` where m₁ = held both, m₂ = held A only, m₃ = held B only,
m₄ = held neither — the effect of B given A, minus the effect of B given not-A. 4,000 learners per
rep, 20 reps per arm, cell floor 5, learner-level ability term included so the cells differ by more
than the gate. Null is a **learner derangement**: each learner keeps their outcome and inherits
another learner's (A, B) state, since the treatment is assigned per learner.

Synthetic only — no corpus is read by `stage1_floor.py`.

```
python3 stage1_floor.py --reps 20
```
