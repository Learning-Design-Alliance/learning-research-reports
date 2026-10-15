# IITA on real learner responses — and a retraction

The surmise/IITA pipeline had only ever been validated against DAKS's own generative model. This is
its first contact with real learners: **133,384,333 attempt records** from MOOCCubeX, filtered to the
69,546 on concept-linked problems.

> ## Retraction
>
> An earlier version of this page reported **6 of 20 item sets carrying structure beyond item
> difficulty, binomial p = 3.3 × 10⁻⁴**, and called it evidence that IITA recovers dependency
> structure from real behaviour.
>
> **That was wrong.** It survived only because the control had a blind spot. Adding a null that
> holds learner ability fixed as well as item difficulty, the result collapses to **1 of 20** —
> exactly what chance predicts (p = 0.64).
>
> The same correction applies at the concept level, where 9 of 11 sets became **0 of 11**.
>
> **A second correction, to the test itself.** Both runs asked whether IITA's relation was *larger*
> than the null produces. That is the wrong tail — genuine dependency yields *fewer* implications
> than ability alone, because a failed gate breaks orderings a Guttman scale would not. Re-scored
> against the lower tail: **1 of 20 below the null's 5th percentile, 1.0 expected by chance.** The
> conclusion is unchanged and has now been tested in both directions. See
> [`IDENTIFIABILITY.md`](IDENTIFIABILITY.md).

## Narrowed wording for Paper II (2026-10-05): a headline correction

Paper 1 (`research/article/limits-of-inferring-prerequisite-structure.md`, Abstract and §5.1), which
Paper II inherits, states the result as **"On 20 MOOCCubeX item sets, item-tree analysis finds no
dependency beyond ability and difficulty"** and adds that this "is a property of these data, not of
the method". Two later studies, both pre-registered, say that wording over-states it:

- [`IITA-DENSE.md`](IITA-DENSE.md): the same implication-count test, run on 15 dense XES3G5M skill
  sets with a detection floor on the corpus's own matrices, detects a single planted prerequisite in
  7% of placements and a conjunctive gate in 27% (pass mark 80%). The verdict is `UNANSWERABLE`, and
  the study fixed in advance that a null from this statistic, MOOCCubeX's 1 of 20 included, "is not
  evidence of absence". So the result is a property of the count statistic at least as much as of
  the data, and the sentence "a property of these data, not of the method" is withdrawn.
- [`IITA-PAIRSCAN.md`](IITA-PAIRSCAN.md) and [`PAIRSCAN-CURRICULUM.md`](PAIRSCAN-CURRICULUM.md): a
  pair-level test against a fitted one-trait (2PL) null, whose floor is demonstrated on the same
  matrices, finds pairwise local dependence beyond one trait in 8 of 15 XES3G5M sets, and the flagged
  pairs are curriculum-linked. IITA-PAIRSCAN fixed in advance that "the item-tree bullet must be
  narrowed".

**The wording Paper II should use** (the article itself is not edited here; it is being re-cut):

> *Abstract bullet.* **IITA's implication count finds nothing beyond ability and difficulty on 20
> sparse MOOCCubeX item sets, but that count cannot see a single prerequisite; a pair-level test that
> can finds pairwise dependence one trait does not explain on dense skill data.**
> - MOOCCubeX: against a null that holds ability and difficulty fixed, 1 of 20 sets (3–6 items) survives,
>   which is chance (p = 0.64), and 11 of the 20 nulls are degenerate. This is a null from an
>   instrument with no demonstrated floor, not evidence that no dependency exists.
> - On 15 dense XES3G5M skill sets the same count detects a planted prerequisite in 7% of placements
>   (gate 27%; pass mark 80%), so it cannot answer the question there either.
> - A pair-level test against a fitted one-trait model, which detects a planted prerequisite in 100%
>   of placements and never fires on data simulated from the fitted model (0 of 30), flags isolated
>   pairwise dependence in 8 of 15 XES3G5M sets (binomial p = 1.8 × 10⁻⁷). The flagged pairs sit closer
>   in the expert taxonomy than other pairs of their sets (3 of 12 adjacent against 0.024 expected;
>   p = 0.0275 with difficulty gap and co-attempts controlled). The test cannot orient a pair or tell a
>   prerequisite from a trait two skills share, so these are candidates for an experiment, not edges.
>   ASSISTments is unanswerable (2 sets; floor fails).

> *§5.1 heading and first bullets.* **An item-tree count finds no dependency beyond ability and
> difficulty in these sets, and cannot see one where it exists.** On MOOCCubeX attempt records, 6 of
> 20 item sets (3–6 items, 77–700 complete-case learners) carried structure beyond item difficulty;
> against the fixed-margins null that also holds learner ability, 1 of 20 survives (p = 0.64), and on
> the lower tail 1 of 20 against 1.0 expected. In simulation the procedure recovers diamond and
> two-chain structures from 200 learners, but it cannot see a single chain, its null is degenerate in
> 11 of the 20 sets, and on 15 dense XES3G5M skill sets it detects a single planted prerequisite in 7%
> of placements (`IITA-DENSE.md`). The null is therefore uninformative about single edges. The
> pair-level result above is reported beside it as the population-level dependence that *is*
> identified.

What changes and what does not: the MOOCCubeX numbers (1 of 20, p = 0.64; 6 of 20; 9 of 11 → 0 of
11) are unchanged and reproduce (reproduction #13, #14). What changes is the claim they carry, from
"no dependency" to "this statistic sees none and could not have seen one". That is a change of verdict
on a headline, so it is recorded as a headline correction in
`research/readiness/learning-graph-budget-2026/readiness.yaml` (`cooling_off.last_headline_correction`).
The record count "133,384,333" is re-checked in reproduction #16.

## The control that was missing, and why it matters most here

The difficulty control resamples each item as an independent Bernoulli at its observed solve rate.
That removes dependencies — but it also removes **learner ability**, because independent resampling
gives every learner the same expected score.

And ability alone produces exactly the pattern IITA reads as implication. A strong learner solves
the hard item *and* the easy one; a weak learner solves neither. Counterexamples — solved the hard
one, missed the easy one — are then rare with no dependency present at all. The difficulty null has
no ability factor to reproduce, so a relation made entirely of ability sails straight through it.

The fix is a null holding **both margins fixed**: row sums (items solved per learner — ability) and
column sums (learners solving each item — difficulty). Checkerboard swaps on a `[[1,0],[0,1]]`
submatrix change neither. What remains is the association between *specific* items, which is the
only thing a prerequisite claim can be about.

## Item level: 1 of 20, which is chance

| concept | N | implications | difficulty p95 | ability p95 | verdict |
| --- | --- | --- | --- | --- | --- |
| 信息化战争 (information warfare) | 700 | 14 | 7 | 16 | dies: ability |
| 触点 (contact) | 227 | 12 | 16 | — | dies: difficulty |
| 梯形图 (ladder diagram) | 225 | 20 | 30 | — | dies: difficulty |
| 微血栓 (microthrombus) | 145 | 6 | 5 | 7 | dies: ability |
| D (Chinese linguistics) | 131 | 11 | 8 | 13 | dies: ability |
| **硬链接 (hard link)** | 110 | 4 | 3 | 3 | **survives** |
| 符号链接 (symbolic link) | 110 | 6 | 4 | 6 | dies: ability |
| 登录 (login) | 81 | 9 | 8 | 14 | dies: ability |

(Twelve further sets die at the difficulty control and are not re-tested.)

Six sets cleared difficulty. Five of those six died against ability. The survivor clears by 4
against a 95th percentile of 3 — one implication of margin, in one set out of twenty, which is what
chance produces.

## Concept level: 0 of 11

The item-level run answers a question nobody asked: problems are not capabilities. The bridge is the
Q-matrix — ECD's evidence model, CbKST's skill function — so `mooccubex_concept_iita.py` derives a
learner's *concept* state from their item outcomes and runs IITA over concepts.

Three controls, beyond the two above:

- **The mastery rule is a choice.** Deriving "mastered concept X" from the items tagged X has no
  single right answer: `all` is DINA's conjunctive assumption, `any` its disjunctive opposite,
  `majority` between. All three are always reported, because a relation appearing under one and not
  the others is a property of the rule.
- **The Q-matrix manufactures dependency.** Two concepts tagged on one problem have states computed
  from overlapping evidence and are dependent by construction. So concept sets are required to have
  **disjoint problem sets** — removing the confound at source rather than modelling it.
- **Coverage is at the concept level.** A learner counts only if they attempted an item for every
  concept in the set.

| field | concepts | learners | survives difficulty | survives both |
| --- | --- | --- | --- | --- |
| 军事思想及军事历史 (military history) | 4 | 646 | 2/3 rules | **0/3** |
| 控制科学与工程 (control engineering) | 8 | 219 | 1/3 | **0/3** |
| 临床医学 (clinical medicine) | 8 | 217 | 3/3 | **0/3** |
| 物理学 (physics) | 8 | 198 | 3/3 | **0/3** |
| 中国语言文学 (Chinese literature) | 8 | 91 | 2/3 | **0/3** |
| 历史学 · 建筑学 · 体育学 | 8 each | 76, 75, 53 | 3/3 each | **0/3 each** |

Under the difficulty control alone this read as 9 of 11 sets surviving under at least one rule and
5 of 11 under all three — binomial p = 9.8 × 10⁻¹¹, which is the kind of number that ends an
investigation. Against the ability control, **every one of them dies.**

## What this actually establishes

**The pipeline works.** It ingests 133M real records, applies the coverage guard, runs IITA, and
returns a clean negative under an honest control. That is what the machinery was built to do.

**On this data, there is no concept-specific dependency structure to find.** Learner ability and
item difficulty account for everything IITA reports. Not "the effect is small" — the observed counts
sit inside the null's 95th percentile.

**One reading, now that the test is powered.** These concepts have no prerequisite structure
recoverable from these responses beyond a difficulty ordering. The simulation settles the
alternative that was open when this was first written — near-ceiling mastery does not erase the
signal, it *sharpens* it (diamond detects at 1.00 at 90% mastery and 0.53 at 30%), so the high
mastery rates here are not an excuse. The one structure that would still hide is a chain, and for a
set of problems inside a single exercise that is a live possibility.

## Why: the null is real, and the test had the power to say so

Running the detector against worlds with known structure settles which of the two readings above is
right. With the statistic corrected to the lower tail, it detects structure at **1.00 from 200
learners upward**, at realistic slip and guess, with a false-positive rate never above 0.10. The
MOOCCubeX sets had 77–700 complete responders — squarely inside that region.

So this is a **powered** negative: the test could have found structure and did not. These response
patterns are what learner ability and item difficulty alone produce.

The one genuine blind spot is a chain, which is a Guttman scale and therefore observationally
equivalent to unidimensional ability with ordered difficulties. Nothing reading who-solved-what can
recover one, at any sample size.

IITA itself is blameless throughout: recall 1.00 and precision 1.00 against known truth, and 15
implications on data with no structure at all.

Full table, and the conditions under which induction does work, in
[`IDENTIFIABILITY.md`](IDENTIFIABILITY.md).

## What this says about the programme

The ceiling argument now cuts both ways. Reconstruction against expert opinion is bounded by κ ≈
0.31, which is why induction from behaviour looked like the escape. But induction has its own
precondition — **evidence that separates learners on the specific capability**, not on general
ability — and a MOOC's exercise logs do not supply it.

That is a constraint on the observation strategy, not a detail. It applies to DataShop and to
Lazuli's `goal_evidence` equally: a course whose checks nearly everyone passes will produce the same
null however many learners it has. Which is an argument for the evidence-role field in
[`docs/specs/TYPED-COMPETENCY-SPEC.md`](../../../docs/specs/TYPED-COMPETENCY-SPEC.md) — a `demonstrates` check is where
discrimination has to live, and marking which checks those are is what would make this analysis
answerable on our own data.

## The guard that was right

MOOCCubeX ships attempt **logs**, not test results. A learner who worked items 1–3 and stopped has
no record for 4–10; read as "incorrect", they look exactly like someone who cannot do them, and IITA
would infer that 1–3 are prerequisites of everything purely from dropout order.

Only learners who attempted every item are used — 4,264 with any attempt become 700 for the largest
set, 81 for the smallest. That guard was correct and stays.

## Reproducing

```
curl -s -L https://lfs.aminer.cn/misc/moocdata/data/mooccube2/relations/user-problem.json \
  | python3 data/ingest/mooccubex/stream_attempts.py $MOOCCUBEX_DIR/concept-problem.txt \
      $MOOCCUBEX_DIR/attempts.tsv               # 69,546 kept of 133M rows; 21 GB never stored
python3 mooccubex_iita.py --top-n 20            # out/iita-real-result.json
python3 mooccubex_concept_iita.py               # out/iita-concept-result.json
python3 reanalyse_lower_tail.py                 # out/lower-tail-reanalysis.json
```

`--top-n 20` gives the twenty item sets above; the default of 12 reads 1 of 12. Inputs default to
`$MOOCCUBEX_DIR/attempts.tsv` and `$MOOCCUBEX_DIR/concept-problem.txt`.

Until 2026-09-25 the item sets depended on Python's hash seed: `pick_item_sets` took each concept's
problems from a set of ids and ties in attempt count kept that set's order, so the lower-tail count
read 1 of 20 at seeds 1 and 2 and 0 of 20 at seed 0. Ties are now broken by id (the concept script
likewise), and all three outputs are byte-identical at seeds 0, 1 and 2: 6 of 20 pass the
difficulty null, 1 of 20 both nulls, 1 of 20 on the lower tail, 0 of 11 concept sets.
