# Build a skill graph blind on XES3G5M, then check every stage

**Status: run 2026-09-26 as pre-registered (bbc3339); build frozen before learner data was read (af63b35); results below.** The design, verdict strings and thresholds are the module
docstring of [`e2e.py`](e2e.py), committed before any build call and before any statistic of this
design was computed on XES3G5M. Eight build changes were forced along the way, all before learner data was read; they are listed under CHANGES there.

## What it asks

The north-star process ([`docs/specs/NORTH-STAR-PROCESS.md`](../../../docs/specs/NORTH-STAR-PROCESS.md))
says how to build a skill graph with levels where no curriculum exists to check it. Each stage has
been studied alone. This runs the whole process once on a domain where every stage can be checked:

| stage | built from (blind to taxonomy and learner data) | checked against | board |
| --- | --- | --- | --- |
| scope | a fixed scope record read by every prompt | — | B1 (not scored) |
| nodes | six model families, each given a different sample of 120 questions, with the tacit-skill probe; merged by the calibrated judge | XES3G5M's KC taxonomy at depth 3, by the judge and by question overlap | B3 |
| levels | three levels per node; each question keyed to a level | item difficulty within node | B4 |
| edges | two proposer families (OpenAI, Mistral) plus a critic (Moonshot) | whether prerequisite history improves prediction beyond a shuffled graph | B11 |
| time | minutes per node | observed time on task | B7 |
| load | load rating per node | load × prior-knowledge interaction on accuracy | B8 |
| usefulness | the whole graph | knowledge tracing on held-out learners against difficulty only, no graph, and the expert taxonomy | B11 |

The builders never see the KC taxonomy, KC tags or any response. The build is committed to
[`build/`](build/) before the analysis reads learner data. The analyst is not blind: earlier studies
in this repo read XES3G5M's taxonomy and learner data.

## Reproducing

```
python3 e2e.py --synthetic   # the detection floor; no corpus, no model call
python3 e2e.py build         # stages 1-3 and tagging (OpenRouter; about $5, capped at $30)
python3 e2e.py analyse       # after build/ is committed
python3 figure_build.py      # Paper II Figure 2 from the committed build and result; no corpus
```

Needs `XES_DIR` (see `data/data-sources.json`) and `OPENROUTER_API_KEY` in the environment or the
repo's gitignored `.env`.

## Result

Output: [`out/result.json`](out/result.json); the frozen build in [`build/`](build/). Spend $21.88 (build
$20.12, coverage judge $1.76). 4,391,076 training and 1,101,162 held-out attempts; 3,630 held-out
learners.

**The build.** Six families answered (z-ai could not return a parseable list and Mistral, the reserve,
replaced it). The judge merged 582 proposals into 401 nodes, 65 flagged terminal. The pool never
saturates: distinct nodes rise 95, 169, 234, 293, 349, 401 as families are added, so "stop when new
families add little" was never reached. The edge panel proposed 1,467 edges (235 by both proposers);
the critic kept 802; 636 remain after cycle removal and transitive reduction. Every question was
tagged, 67% with two or three nodes; 28 nodes tag no question.

**B11, usefulness on held-out learners: USEFUL, NOT WORSE THAN THE EXPERT TAXONOMY.**

| model | AUC |
| --- | ---: |
| M0 difficulty only | 0.7298 |
| M1 no graph (overall history) | 0.7919 |
| M2 expert taxonomy, leaf KCs | 0.7965 |
| M2c expert taxonomy, depth 3 | 0.7976 |
| M3 built nodes | 0.7989 |
| M4 built nodes and edges | 0.7991 |
| M4s built nodes, shuffled edges | 0.7989 |
| M4r built nodes, reversed edges | 0.7991 |

M4 beats M0 by +0.069 [+0.066, +0.072] and M1 by +0.0072 [+0.0068, +0.0076], and it is above the
expert taxonomy, not merely non-inferior: +0.0026 [+0.0023, +0.0028] over leaf KCs.

**Edges: EDGES ADD NOTHING.** M4 - M3 is +0.0002 [+0.0001, +0.0002] and M4 - M4s the same, both below
the pre-registered +0.001 bar, although the synthetic floor showed the pipeline detects a planted
prerequisite effect at +0.007 to +0.010. The reversed-arrow control ties (M4r - M4 +0.00005). Built
edges also do not follow the platform's order: learners meet the prerequisite first on a median 0.52
of edges, against 0.63 for shuffled edges.

**The usefulness is in the nodes.** Built nodes alone beat the expert taxonomy by +0.0024 [+0.0022,
+0.0027]. 67% of questions carry two or three built nodes against 13% for the expert tags, so the
follow-up below separates node boundaries from tag count.

**B3, node coverage: NOT MET.** Against the 187 depth-3 taxonomy nodes (`reference_depth3` in `out/result.json`; 172 in an earlier version of this README) the judge finds some
overlapping built node for 0.963 but an equivalent one for only 0.139; 4 of 55 judge chunks were
unparsed and counted as no match. These are from the judge's rerun as its own step
(`e2e.py judge`, CHANGES 9, 2026-10-08; build/coverage-judge.json). The first run, made inside
`analyse` and no longer cached, gave 0.957 and 0.080 with 6 of 55 chunks unparsed; no other value in
`out/result.json` changed, and B3 is NOT MET either way. By question overlap, 40 of 83 eligible depth-3 nodes (0.48) and 51
of 239 leaf KCs (0.21) are covered. A terminal node is present. The built graph cuts the domain
differently from the taxonomy, and still predicts better.

**B4, levels: LEVELS NOT ORDERED.** Across 138 nodes, pooled within-node Spearman between keyed level
and error rate is +0.039 [-0.0004, +0.080]; 55% of nodes positive. The tagger keyed 82% of questions
to level 2, which leaves little to order.

**B7, time: TIME NOT PREDICTED.** Panel minutes vs each learner's total time on the node: rho -0.04
(179 nodes); train error rate does no better (+0.06). Total time is exposure the platform assigns.
Secondary: panel minutes correlate with median time per attempt, rho +0.30.

**B8, load: LOAD HURTS LOW-PRIOR LEARNERS MORE.** Load x low prior accuracy -0.040 [-0.055, -0.028] on
the log-odds of a correct answer, beyond question difficulty, over 1,083,012 held-out attempts.
Consistent with the expertise-reversal account; a logit-scale floor effect is an alternative the
design does not separate.

**What this licenses.** A graph built from question text alone, blind to the taxonomy and to learner
data, gives a Q-matrix that tracks held-out learners better than the platform's expert one. Its edges
add nothing measurable to prediction, its levels are not ordered, its time estimates do not track
exposure, and its load ratings carry a small, correctly signed interaction. Prediction is not
learning: whether sequencing by this graph helps learners, or which way its edges point, still needs
an experiment.

## Follow-up: boundaries or tag count? (primary_tag.py)

Pre-registered at dfeff84 after the result above was read; no model call. Output:
[`out/primary-tag-result.json`](out/primary-tag-result.json).

| Q-matrix | tags per question | AUC |
| --- | ---: | ---: |
| expert, first KC only | 1.00 | 0.7963 |
| expert, all KCs | 1.16 | 0.7965 |
| built, primary node only | 1.00 | 0.7971 |
| built, primary + random secondary nodes | 1.74 | 0.7959 |
| built, all nodes the tagger gave | 1.74 | 0.7989 |

**V1, boundaries at one tag each: NO DIFFERENCE AT ONE TAG.** Built primary minus expert first KC is
+0.0008 [+0.0006, +0.0010]: above zero but under the +0.001 bar set for "beats".

**V2, the extra tags: SECONDARY TAGS CARRY CONTENT.** The tagger's secondary nodes beat random ones
of the same count by +0.0030 [+0.0028, +0.0032]; random secondaries are worse than none (-0.0012). So
the gain is not generic pooling of more history.

**Reading.** Of the built graph's +0.0024 over the expert taxonomy, about a third is node boundaries
(small, under the bar) and the rest is multi-skill tagging: marking every skill a question draws on
(+0.0019 over the primary tag alone), where the expert tags mostly name one (+0.0003 for their
extra tags). The transferable finding is less "models find better skills" than "models tag each
question with all the skills it uses".

## Follow-up: multi-skill tags on the expert's own nodes (expert_tags.py)

Pre-registered at a5e5485; tags frozen at 994fc1a before learner data was read; $2.17. The same
tagger named 1-3 of the 866 expert KCs per question from its text alone. Output:
[`out/expert-tags-result.json`](out/expert-tags-result.json).

| Q-matrix | tags per question | AUC |
| --- | ---: | ---: |
| expert, original tags | 1.16 | 0.7965 |
| expert, tagger's primary KC only | 1.00 | 0.7962 |
| expert, tagger's KCs | 1.66 | 0.7975 |
| expert, original + random extra KCs | 2.18 | 0.7953 |
| expert, original + tagger's extra KCs | 2.18 | 0.7984 |
| built nodes, all tags | 1.74 | 0.7989 |

**V1: TAGGING ADDS CONTENT TO EXPERT NODES.** Adding the tagger's extra KCs to the original tags gains
+0.0019 [+0.0017, +0.0021], and beats the same number of random extra KCs by +0.0031.

**V2: EXPERT NODES WITH MULTI-SKILL TAGS MATCH THE BUILT GRAPH.** The best expert arm trails the built
graph by -0.0005 [-0.0007, -0.0003], inside the pre-set -0.001 margin. Multi-skill tagging closes
about 80% of the original +0.0024 gap.

The tagger's single best KC agrees with the experts' first tag on 48% of questions and predicts
slightly worse than it (-0.0003): the experts choose the main skill a little better; the tagger's
value is in naming the others.

**Reading across the three analyses.** The built graph beat the expert taxonomy mainly because every
question was tagged with all the skills it draws on. The same tagging applied to the expert's nodes
recovers most of that. A good node set matters less than complete item tagging, and a model can do
the tagging from question text alone.

## Follow-up: what an AUC gain buys in practice (practice_value.py)

Pre-registered at 8608b36; no model call. Before each test attempt the model decides whether the
learner is ready to move on. Each model's threshold is set so that 20% of wrong answers come from
learners it had judged ready (matched risk). At that risk, unneeded practice is a correct answer
from a learner it judged not ready. Output:
[`out/practice-value-result.json`](out/practice-value-result.json).

Unneeded practice, as a share of correct answers: difficulty only 48.7%, no skills 37.6%, expert
skills 36.7%, built skills 36.3%, expert skills with the tagger's extra tags 36.3%.

| comparison (risk 0.20) | AUC gain | items saved per 1,000 attempts | per learner (282 attempts) | a year at 50 items/week | 10,000 learners, a year |
| --- | ---: | ---: | ---: | ---: | ---: |
| no skills vs difficulty only | +0.062 | +88.0 [+82.7, +93.8] | 25 items, 88 min | 565 min | 94,000 h |
| built skills vs no skills | +0.007 | +10.5 [+9.4, +11.9] | 3 items, 10 min | 67 min | 11,200 h |
| built vs expert skills | +0.0024 | +3.4 [+2.5, +4.2] | 1 item, 3.5 min | 22 min | 3,700 h |
| expert + tagger's tags vs expert | +0.0019 | +3.2 [+2.3, +3.8] | 1 item, 3 min | 20 min | 3,400 h |

**VERDICT: SAVES PRACTICE.** Results at risks 0.10 and 0.30 fall within about 1 item of these. The
median correct attempt takes 214 s, measured from the start of one attempt to the start of the next
and capped at 600 s. These are word problems, so that figure includes reading time.

**Reading.** On the decision scale, the AUC gains grow by roughly a factor of 1,500. A gain of 0.0024
(built vs expert skills) saves about one item in 300. That is negligible for one learner in one
session. It comes to about 20 minutes per learner per year at a moderate practice load, and to
thousands of hours across a platform. The ordering matches the AUC ordering: learner history does
most of the work, skills are next, and the choice between skill sets is a small refinement on top.
The yearly and cohort figures are arithmetic that assumes the per-attempt rate stays constant; no
learner was followed for a year.

## Follow-up: how much of difficulty is tangled skills? (difficulty.py)

Pre-registered at 8608b36; no model call. This covers 5,264 items with at least 60 training attempts.
Item difficulty is the logit of the error rate. The ceiling is the reliable share of difficulty
variance: split-half r 0.946, which the Spearman-Brown correction raises to 0.972. Output:
[`out/difficulty-result.json`](out/difficulty-result.json).

| difficulty = sum of … | out-of-fold R² | share of reliable difficulty |
| --- | ---: | ---: |
| expert KCs | 0.048 | 5% |
| expert KCs + tagger's extra KCs | 0.053 | 6% |
| built primary node | 0.098 | 10% |
| built nodes, all tags | 0.096 | 10% |
| + number of skills | 0.096 | 10% |
| + panel load and keyed level | 0.097 | 10% |

**D1: MOSTLY NOT DECOMPOSABLE.** The skills an item is tagged with account for about 10% of its
reliable difficulty; 90% of what makes an item reliably harder than another is not in its skill
labels.

**D2: COMBINING IS ADDITIVE.** On average, items with more skills are harder:

- 1 skill: −1.59 logits
- 2 skills: −1.46
- 3 skills: −1.28

Once the model accounts for which skills an item carries, each extra skill adds +0.005 logits
[−0.020, +0.032]. An item that combines skills is about as hard as the skills themselves predict,
with no measurable cost for combining them.

**Reading.** There are two findings, and they have different uses.

- **Combining is additive.** A hard multi-skill item is hard because of the particular skills it
  contains, not because they are combined. Splitting it would leave each skill's difficulty where it
  was. Designers can identify which component skill is the hard one and target that skill.
- **Skill labels explain little.** Most of the reliable difference between items lies somewhere
  else: numbers, wording, format, the number of steps, position in the sequence, or skills that no
  one tagged. That is where a finer decomposition would have to look. Candidates are features read
  from the item text, or tagging steps rather than whole items.

**Limits.** The indicator models are sparse. There are 866 expert KCs against about 400 built nodes,
and many KCs have only a few items, so some of the gap between the expert and built vocabularies
comes from estimation noise, not from which carving is better. None of the models explains much. An
LLTM-style fit on skill labels alone is a lower bound on how decomposable difficulty is, not a
measure of it.
