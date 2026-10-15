# Is a prerequisite a gate or a hook?

[`mastery_exit.py`](mastery_exit.py) found that release without mastery costs something downstream,
measured at the learner's **first encounter** with each downstream skill. That is the right
measurement for one theory of what a prerequisite is and the wrong one for the other.

> **Gate** — you cannot do B without A. The penalty is there immediately and does not grow.
>
> **Hook** — B does not *stick* without A. Learning is expansion: new material attaches to what is
> already held, so a learner with nothing to attach to can still answer B correctly today by
> matching the surface of the problem set, and has nothing holding it later.

Two arms on the same 1.28M observations.

## Arm 1 — does the deficit persist? No, it decays.

| lag (days) | n | released % | gap | 95% interval |
| --- | ---: | ---: | ---: | --- |
| 0.0 – 13.9 | 256,617 | 17.3% | **+0.0440** | [+0.0392, +0.0489] |
| 13.9 – 41.4 | 256,617 | 16.7% | +0.0254 | [+0.0204, +0.0304] |
| 41.4 – 80.9 | 256,616 | 16.9% | **+0.0134** | [+0.0086, +0.0180] |
| 80.9 – 137.0 | 256,617 | 18.9% | +0.0195 | [+0.0148, +0.0243] |
| 137.0 – 363.1 | 256,617 | 19.7% | +0.0240 | [+0.0198, +0.0284] |

The released share is stable across buckets (17.3% → 19.7%), so this is not differential attrition.

Holding the pair fixed — same (A, B) measured early and late, so skill composition cannot move the
answer — the late-minus-early gap is **−0.0181 [−0.0481, +0.0132]**: undecided, and the point
estimate points at narrowing. That arm could only have detected a widening of ±0.031, so it is not
strong evidence either way.

**The penalty for lacking A fades as time passes.** That is the gate's prediction, and the likely
mechanism is mundane: the learner picks A up somewhere else.

## Arm 2 — does what they learned stay? No, and that is the hook

Restricted to learners who got the downstream skill **right at first encounter** — both groups have
demonstrated they could do it once, so the only question left is whether it stayed.

| | mastered A | released without A |
| --- | ---: | ---: |
| first-time successes with a later attempt | \- | 626,850 across 11,303 learners |
| later attempts per success | 7.26 | 7.75 |
| **later accuracy** | **0.8431** | **0.8057** |

**Ability-stratified gap +0.0312 [+0.0277, +0.0344]**, learner-clustered bootstrap.

**Same initial success, worse retention without the prerequisite.**

Two things make this conservative rather than optimistic:

- **The selection runs the wrong way for the result.** Conditioning on first-time success positively
  selects the released group — lacking the prerequisite, they needed more ability or more luck to
  succeed at all. That collider should make them look *better* afterwards. They look worse.
- **They get more practice, not less** (7.75 later attempts against 7.26), which should help them.

The interval is learner-clustered because it has to be: one learner contributes hundreds of rows
carrying the same exit status, and an observation bootstrap returned ±0.002 on 627,000 rows, which
no 11,000-learner sample can justify.

## What it does not distinguish

"Acquired it and it did not stick" and "never acquired it, got lucky once" produce the same data
here. Both are the absence of a hook, and for an instructional decision they may not differ — but
they are different mechanisms and this design cannot separate them. Separating them needs a measure
of *how* the first success was obtained (response time, hint use, attempt count), which the log
carries and this arm does not yet use.

## Why the two arms disagree, and why that is the point

The immediate deficit decays; the durability deficit does not. Those are consistent: a learner who
lacked A can catch up on *performing* B, while what they built the first time still had nothing to
attach to.

It also means **every outcome measure in this programme has been the one that fades.** First-attempt
correctness minutes later is the moment the hook effect is guaranteed to be smallest. The
readout should be retention.

## Reproduce

```
python3 lag.py --out out/lag.json
```

---

# Is the retention penalty pair-specific?

The aggregate retention deficit is solid. The question that decides whether it is *structure* is
whether it concentrates on particular (A, B) pairs, as `mastery_exit.py` asked of the first-attempt
outcome. Two reasons to expect the retention estimand to do better, stated before the numbers:
conditioning on first-time success starts both groups from equal demonstrated capability rather than
equal estimated ability, and the outcome is a mean over ~7 attempts rather than one binary.

| | first attempt | retention |
| --- | ---: | ---: |
| flat ability-stratified gap | +0.0254 | +0.0312 |
| median edge gap | +0.0341 | +0.0274 |
| readable edges | 1,644 | 695 |
| observed edge-gap sd | 0.1043 | 0.0551 |
| null spread | 0.0973 | **0.0589** |
| p, concentrated | 0.0020 | **0.8440** |
| **split-half r** | 0.297 | **0.354** |
| **full-sample reliability** | 0.458 | **0.523** |

## Two readings, and the honest one is "unresolved"

Taken at face value, p = 0.844 says the retention penalty is flat — a general durability deficit
rather than a prerequisite-structure effect.

**But the null is overdispersed here and that reverses the test's meaning.** On the first-attempt
outcome the null spread sat *below* the observed (0.0973 against 0.1043), which is what a
well-calibrated null does. On retention it sits *above* it (0.0589 against 0.0551) — permuting exit
status is generating more between-edge variance than the real data contains. A null that overshoots
cannot distinguish "flat" from "concentrated"; it just fails to reject anything.

The split-half does not depend on the null's calibration, and it is **positive and higher than the
first-attempt version**: r = 0.354 across 690 edges. Pure noise would give ~0. So there is
reproducible between-edge variation that the permutation test is not able to see.

**Reported as inconclusive rather than negative.** Fixing it means a null that preserves each
learner's own retention level — the ability strata evidently do not, for this outcome.

## What it does move

Reliability goes from **0.458 to 0.523** on the better-identified estimand. That is real progress on
the criterion that decides whether any of this is usable, and it is still well short of the 0.80 bar
and of the 0.857 a seven-rater human panel reaches.

## Reproduce

```
python3 retention_edges.py --out out/retention-edges.json
```
