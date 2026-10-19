# EdNet at its own bar: the negative holds, but "EdNet has no conjunctions" was the wrong sentence

> **Re-issued 2026-09-24 ([`docs/notes/EDNET-REISSUE.md`](/docs/notes/EDNET-REISSUE.md)):** the verdict is now **UNANSWERABLE**, not NO STRUCTURE (power at own bar 0.92 → 0.34 on a reproducible learner set). The headline above is superseded.

`replicate.py` left one reading open. At the fixed +0.10 bar EdNet was a **powered negative** (0.005,
60.2% power). At its **own** bar — +0.0565, barely half XES3G5M's — it had 15.1% power and the honest
output was `UNANSWERABLE`: UNKNOWN, not absence.

That was a sample-size problem and nothing else. The whole EdNet KT1 archive was already on disk;
only 8,000 of its 784,309 learner files had been extracted. This closes it with **60,308**.

## The extraction, and a selection that was already there and undeclared

The original 8,000 were **never a uniform sample**: mean file size 38.8 KB against a corpus mean of
3.9 KB and a corpus **median of 390 bytes**. `replicate.py` ran on unusually active learners without
saying so. The median EdNet learner has a handful of events and **cannot enter a four-way cell at any
sample size**, so a uniform draw would add rows and no power.

This takes every learner file at or above 10 KB: **60,308 learners, mean ~41 KB — the same activity
profile as the original 8,000 and 7.5× as many.** That is selection on *analysability*, the same
restriction positivity already imposes, but it is selection and it bounds the claim: **this is a
result about active EdNet learners, not about EdNet learners.**

## Result

> **SUPERSEDED IN PART — see `BAR.md`.** The `FAILS` verdict below was produced by comparing
> the above-bar share against `FDR_Q = 0.05`. That rule is wrong: BH at q bounds the false
> discovery proportion *among rejections*, and under a global null it rejects almost nothing.
> Against a deranged **pipeline** null of 0.0000, EdNet shows **STRUCTURE** at this same
> +0.10 bar (0.016 [0.003, 0.035], 100% power). Existence replicates; magnitude (7×) does not.

Null validates at **1.002** (deranged mean interaction +0.00007). Background **+0.0491** over 870
readable ordered pairs, against +0.0565 on 8,000.

| | bar | power at bar | above-bar share | 95% block CI | n_eff |
| --- | ---: | ---: | ---: | --- | ---: |
| EdNet, 8,000 (`replicate.py`) | +0.100 | 60.2% | 0.005 | [0.000, 0.021] | 152 |
| **EdNet, 60,308** | **+0.100** | **100%** | **0.016** | **[0.003, 0.035]** | 225 |
| **EdNet, 60,308** | **own +0.0491** | **92.1%** | **0.078** | **[0.033, 0.131]** | 119 |
| XES3G5M fine | +0.100 | 74.6% | 0.108 | [0.059, 0.171] | 118 |
| XES3G5M coarse | +0.100 | 61.9% | 0.056 | [0.035, 0.082] | 368 |
| XES3G5M coarse | own +0.110 | 66.6% | 0.048 | [0.027, 0.075] | 314 |

**Verdict at its own bar: `NO STRUCTURE`** — 0.078 [0.033, 0.131], and 0.033 does not clear the 0.05
the false-discovery allowance occupies.

## What this actually settles, and what it overturns

**The fixed-bar negative was real, not underpowered.** Going from 8,000 to 60,308 learners took power
at +0.10 from 60.2% to **100%** and moved the share only from 0.005 to **0.016**. Against XES3G5M's
0.108 fine and 0.056 coarse, that is a 7–3× gap that more data did not close. **`A9` stays unmet.**

**But "XES3G5M has conjunctive structure and EdNet has none" is now the wrong sentence.** Read at its
own scale EdNet shows **7.8%**, and that interval **overlaps XES3G5M's at both grains**. Everything
in EdNet is about half the size — background +0.049 against +0.107, split-half reliability 0.29–0.34
against 0.51–0.64 (`studies/measurement/reliability/split_half.py`). The conjunctions scale with the rest of it. The
corpora differ in the **size of every effect**, not in whether conjunctive structure is present.

**A defect in my own pre-registration, recorded rather than quietly dropped.** The 0.05 lower-bound
rule was meant to separate "carries conjunctive structure" from "does not". It does not do that here:
**XES3G5M read at its own coarse grain fails it too** (0.048 [0.027, 0.075]). A threshold that
rejects the corpus the finding came from, merely re-read at a different zoom level, is not
discriminating what it was built to discriminate. It is behaving as a joint test of effect size and
power, which is not what it was pre-registered as. **The fixed-bar comparison is the one that carries
the replication verdict; the own-bar verdict string should be read as a measurement, not a ruling.**

Note also that relative-scale reasoning is **post-hoc**. The pre-registered comparison was at the
fixed bar and it failed. The proportionality observation is a hypothesis this run generated, not one
it tested.

## Where that leaves the conjunctive line

> Conjunctive structure at or above **+0.10** is a fact about XES3G5M (10.8% fine, 5.6% coarse) and
> not about EdNet (1.6% at 100% power). At **each corpus's own background scale** the two are not
> distinguishable (7.8% against 4.8–10.8%, intervals overlapping), and **neither clears the 0.05
> rule** at coarse or own grain.

The unresolved question is no longer "does it replicate" — it does not, at the stated bar — but
**whether a bar should be absolute or relative to a corpus's own background**, which
`studies/identifiability/assay-generality/local_background.py` already showed is local *within* a corpus and this shows is
local *between* them. That is a specification question about the assay, and it is now the live one.

```
python3 ednet_at_scale.py --items 30 --draws 1000
```

Reads EdNet. CC BY-NC 4.0 — non-commercial, no model training; counting learners in cells is neither.
Raw exports stay in the session scratchpad; only aggregates are committed.
