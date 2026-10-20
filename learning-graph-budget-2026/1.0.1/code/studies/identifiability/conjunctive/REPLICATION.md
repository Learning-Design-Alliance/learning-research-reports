# It does not replicate. EdNet had the power to say so, and said no.

> **Re-issued 2026-09-24 ([`docs/notes/EDNET-REISSUE.md`](/docs/notes/EDNET-REISSUE.md)):** the EdNet arm is now **UNANSWERABLE**, not FAILS (power at the fixed bar 0.60 → 0.12 on a reproducible learner set). A9 stays met: at the reliability bar the two corpora now replicate, and their intervals overlap at +0.10. The headline above is superseded.

`stage3_interaction.py` found conjunctive structure in XES3G5M and `block_bootstrap.py` showed it
survives being blocked on the 30 items it came from. Every number in both came from one corpus, and
`A9` — *does a positive finding survive on a second independent dataset?* — has never been met by
anything in this programme.

`replicate.py` runs the same estimand through the same code on both corpora, so a difference between
the arms is the corpus and not the implementation. XES3G5M is **re-run rather than quoted**.

## The three arms

| | learners | items | triples | background | null ratio | power at +0.10 | **above-bar share** | 95% block CI |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| XES3G5M (fine, 30 of 865 KCs) | 18,066 | 30 | 11,203 | +0.1073 | 0.993 | 74.6% | **0.108** | [0.059, 0.171] |
| XES3G5M (coarse, 30 of 172 families) | 18,066 | 30 | 11,203 | +0.1102 | 0.999 | 61.9% | **0.056** | [0.035, 0.082] |
| **EdNet** (30 of 142 tags) | 8,000 | 30 | 12,180 | **+0.0565** | 1.003 | 60.2% | **0.005** | **[0.000, 0.021]** |

Every arm's analytic null validates against an explicit learner derangement (0.993 / 0.999 / 1.003,
deranged mean interaction within 0.0012 of zero). Nothing below rests on an unchecked standard error.

## Verdict: `FAILS`

> **SUPERSEDED IN PART — see `BAR.md`.** The `FAILS` verdict below was produced by comparing
> the above-bar share against `FDR_Q = 0.05`. That rule is wrong: BH at q bounds the false
> discovery proportion *among rejections*, and under a global null it rejects almost nothing.
> Against a deranged **pipeline** null of 0.0000, EdNet shows **STRUCTURE** at this same
> +0.10 bar (0.016 [0.003, 0.035], 100% power). Existence replicates; magnitude (7×) does not.

> **Followed up in `EDNET-AT-SCALE.md`.** EdNet was re-run on **60,308**
> learners (the 8,000 used here were an undeclared high-activity sample). Power at this bar went
> from 60.2% to **100%** and the share moved only 0.005 → **0.016**, so this negative is real
> rather than underpowered. But at EdNet's **own** bar it shows 0.078 [0.033, 0.131], overlapping
> XES3G5M at both grains — the corpora differ in the *size* of every effect, not in whether
> conjunctive structure exists. The 0.05 rule used below also rejects XES3G5M read at its own
> coarse grain, which is a defect in it.

EdNet is **powered** at the bar the claim was made at — 60.2% against a pre-registered 50% floor —
and its null validates. This is a measurement, not a gap.

If EdNet carried XES3G5M's structure, its 60% power against XES3G5M's 75% predicts an above-bar
share of **0.087**. Observed: **0.005**, or **0.06×** what replication would produce. The blocked
lower bound, 0.000, does not clear the 0.05 the false-discovery allowance itself occupies.

## Is it grain rather than corpus?

EdNet ships **142 expert tags** where XES3G5M ships **865 leaf KCs**. A coarse item is a *mixture* of
finer skills, so a learner who "holds" a coarse tag may hold any of the skills inside it and the four
parent cells stop being the four states the statistic is about. That dilution is a complete
alternative explanation and it had to be tested, not asserted.

XES3G5M re-read at its own depth-3 taxonomy grain — **172 families against EdNet's 142 tags, power
61.9% against EdNet's 60.2%, matched on both**:

- Coarsening costs XES3G5M **48%** of its above-bar share (0.108 → 0.056). **Grain is real and it is
  half the story.**
- At matched grain and matched power, XES3G5M still runs **11× EdNet**, and the intervals
  **do not overlap** ([0.035, 0.082] against [0.000, 0.021]).

**A caveat that cuts against my own reading.** Coarse XES3G5M's own lower bound, 0.035, does not
clear 0.05 either. So at this grain the pass/fail line is not what separates the corpora. What
survives is the **11× ratio and the non-overlap**, and those are what the negative rests on.

## What is NOT answered

**EdNet at its own background scale.** EdNet's background is **+0.0565, 0.53× XES3G5M's**, so the
fixed +0.10 bar asks EdNet for **1.8× its own background** against 0.9× for XES3G5M. Read at its own
bar, EdNet has **15.1% power** — far under the floor — so that reading is **`UNANSWERABLE`: UNKNOWN,
not absence**, per this programme's first rule.

Closing it is a **download, not a collection**: power scales with √n, so reaching 50% at +0.0565
needs roughly **5× the learners**, and we hold **8,000 of EdNet's ~780,000**. That is the single
cheapest open question on this board.

## One structural change, recorded rather than buried

The pre-registration first gated the whole arm on power at its **own** bar. A six-item smoke run then
showed EdNet's background is +0.046 and that EdNet sees a planted +0.046 in 13.8% of triples against
100% at +0.20. Under the original wording that one number would have returned `UNANSWERABLE` and
thrown away the comparison that *is* fully powered — the one at the fixed +0.10 bar, which is the bar
stage 3's claim was stated at and therefore the claim A9 asks about.

So the power gate now applies **per bar** instead of per arm. `MIN_POWER` was not lowered, no bar was
moved, and the primary verdict is the fixed-bar one. The own-bar reading is secondary and reports
`UNANSWERABLE` where it is underpowered.

## What EdNet cannot control, stated before the result

KT1 carries no `source` column — the sprint / adaptive-offer distinction lives in KT3 and KT4, which
we do not hold — so **recommender-chosen items cannot be conditioned out**. If EdNet's recommender
bundles items, that bundling is inside the interaction. XES3G5M has the same confound through
curricular bundling. Neither arm resolves it, which is why a positive result on either is
**directional, not causal**.

## Where this leaves the conjunctive line

The honest sentence is narrower than stage 3's and wider than "it was noise":

> Conjunctive structure at or above +0.10 is present in XES3G5M at fine grain (10.8%), roughly halved
> by coarsening (5.6%), and **absent in EdNet at the same bar with the power to detect it** (0.5%).
> Whether EdNet carries conjunctions at *its own* smaller scale is unmeasured.

Ability adjustment behaves consistently across all three arms — 78% / 81% / 60% of the magnitude
retained under quintile stratification — so the difference is not the ability confound either.

Concentration differs sharply and is worth carrying: the worst single item costs XES3G5M **29.9%**
fine and **17.4%** coarse, but costs EdNet **71.0%**. What little EdNet has sits in one tag.

```
python3 replicate.py --dataset xes3g5m       --items 30 --draws 1000
python3 replicate.py --dataset ednet         --items 30 --draws 1000
python3 replicate.py --dataset xes3g5m-coarse --items 30 --draws 1000
python3 replicate.py --dataset compare
```

Reads XES3G5M and EdNet. EdNet is CC BY-NC 4.0 — non-commercial, no model training; counting
learners in cells is neither. Raw exports stay in the session scratchpad; only aggregates are
committed.
