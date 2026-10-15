# HOLON-1: is the course graph the projection of the concept graph?

**Verdict: UNANSWERABLE.** The binding detection floor failed, so this instrument cannot tell a course
order that is the projection of the concept graph from a catalogue order on MOOCCubeX. The failure
has a clear cause, which is the main result: once course order is controlled for the catalogue,
a course order that every learner shares is gone, because it has become part of each course's
enrolment timing, which is exactly what the catalogue control keeps. The verdict is also bound as
descriptive under CLAUDE.md, because the concept-to-course map is model-extracted and has no human
reference.

Proposed by the maintainer on 2026-10-07. The script is `holon.py`, and its docstring holds the
pre-registration and the CHANGES entry. Commits: design `9ed765e` (before any learner data);
CHANGES and floor results `50ac955` (before any real-data statistic).

## What was asked

A holonic graph would let an edge be asserted at course level while the concept edges inside the
two courses stay unknown, with a projection rule that summarizes the lower level upward. Per
`studies/workforce/graphex/zoom.py`, that rule is to take the closure and render the transitive
reduction. The question is whether the course graph that learners identify equals that projection
(PROJECTION HOLDS), shares only its direction (PROJECTION PARTIAL, a verdict added to the brief's
four), is unrelated to it (LEVELS INDEPENDENT), or cannot be told from the catalogue (CATALOGUE ONLY).

## Data (MOOCCubeX; research use, no redistribution)

- **Concept graph.** `prerequisites/{cs,psy,math}.json`, with positives only: 725, 831 and 761
  respectively. Coder: human annotators, labelling candidate pairs that a model had ranked, and the
  model's graph component used within-course video order.
- **Concept-to-course map.** `relations/concept-course.txt` (19 MB). Coder: a model (NER over
  captions, then an unstated refinement), with no human reference. Concepts were joined by name
  within their own field. 483, 632 and 240 positive pairs have both concepts placed in a course.
- **Learner course order.** `entities/user.json` (807 MB), streamed through
  `data/ingest/mooccubex/stream_user.py`, which drops all demographic fields. 211,063 learners
  enrolled in at least 2 of the 166 courses the projection touches.
- **General factor.** `relations/user-problem.json` (22.45 GB) was streamed through
  `ability_ingest.py` and never stored: 133,384,333 rows, 1,290,530 learners, and the stream exited
  with code 0. Only 41,441 of the 211,063 order learners have any problem rows, and only 22,013
  (10.4%) have at least 20. The ids share the `U_` format, so this is genuine sparsity, not a failed
  join. That is under the registered 20% bar, so the **general factor was dropped** from the family
  key, as pre-registered. The conditioning that remains is on breadth and the week of first
  enrolment.
- The derived files are under `$LDA_SCRATCH_DIR/derived-holon-projection/`; their generators are
  given in the docstring.

## The projection (metadata; `out/projection.json`)

The literal rule (X → Y if some concept in X is a prerequisite of some concept in Y) gives 5,485
course edges over 166 courses. Its closure has 12,698 ordered pairs, and most of them are mutual.
In cs, 5,151 unordered closure pairs are mutual and 938 run one way. The transitive reduction has **510
edges, all in cs**. Psychology and mathematics reduce to nothing, because each domain's courses form
a single strongly connected class. This is zoom.py's "contraction manufactures reachability" at full
strength. Because concept membership is many-to-many, almost every course reaches almost every other. Under the literal rule, the projection is defined in
one domain only. A majority-flow variant (P_net: 3,040 edges; its reduction P_netred: 842) is
reported as secondary.

## The detection floor (binding: real marginals; `out/floor-real.json`)

The synthetic worlds were built on the real projection and the real enrolment marginals. In W_proj,
30% of learners take their courses in P_red order. In W_cat, course opening dates follow P_red order
and no learner orders anything. In W_ind, learners follow a relabelled P_red.

| world | seeds HOLDS | D by seed |
| --- | ---: | --- |
| W_proj (β 0.3) | **0 / 3** | −0.0040, +0.0054, +0.0088 (null p 0.60, 0.41, 0.30) |
| W_cat | 0 / 3 (all CATALOGUE ONLY) | −0.0024, −0.0002, +0.0032 |
| W_ind | 0 / 3 (all LEVELS INDEPENDENT) | −0.0116, +0.0096, +0.0001 |

At β 0.1 and 0.2 the result is also LEVELS INDEPENDENT. The instrument rejects the catalogue world,
which was the trap it had to avoid, but it **cannot see a planted projection**. The floor fails.

**Why** (`floor_diagnosis.py`, `out/floor-diagnosis.json`; the floor's synthetic learners on real
marginals, run before any real-data statistic). In W_proj with β 1.0, where every learner follows
the projection, the raw order statistic on P_red edges is +0.979. The derangement-only excess is
+0.089, and after the catalogue residualization it is −0.020. At β 0.3 the same three numbers are
+0.396, +0.011 and −0.012.

An order that the whole population follows changes each course's enrolment-date distribution. The
donor derangement keeps that distribution by design, and the catalogue-gap residualization removes
whatever it predicts. This is the same mechanism as `course_order_derangement.py`'s EXPOSURE
verdict, seen from the other side. On free-enrolment data, "learners take X before Y" and "X is
generally taken earlier" are the same observation. Projection-shaped course order is not
identifiable from enrolment order with a catalogue control.

Earlier floors: `out/floor-synthetic-v1.json` failed (W_cat's D was "significant" in 3 of 3 seeds,
from a start-date leak). That led to the single registered CHANGES entry: weekly cohorts and the
catalogue residualization. `out/floor-synthetic.json` failed again after it, on synthetic marginals.

## Real-data numbers (descriptive only; not findings; `out/holon.json`)

The verdicts are forced to UNANSWERABLE, and the pre-floor readings are kept as
`verdict_before_floor`. A floor that failed means these numbers cannot carry a verdict.

- 3,666 course pairs were read (at least 30 learners in the real cell and in both deranged cells).
  The split-half reliability of the catalogue-controlled excess E is 0.885 (mean Spearman over 6
  learner splits), and the median |E| is 0.125. Learner order beyond the catalogue is reproducible.
  What the floor shows is that its relation to a projection cannot be scored.
- **P_red** (133 of 510 edges read): D +0.0449. The learner bootstrap interval (95%, 30 draws) is
  [+0.0323, +0.0585]. The deranged-projection null has mean −0.0101 and SD 0.0619, giving
  p = 0.19. Concordance is 0.62 over 100 decided edges. Three-class κ is 0.0014, against a null 95th
  percentile of 0.018. The pre-floor reading was LEVELS INDEPENDENT.
- **P_clo** (252 read): D +0.0701 [+0.0557, +0.0788], p = 0.044, concordance 0.68 over 213 decided
  edges. The pre-floor reading was PARTIAL.
- **P_net** (847 read): D −0.0124 [−0.0160, −0.0080], p_lower = 0.12.
- **P_netred** (175 read): D +0.0257 [+0.0097, +0.0345], p = 0.27.
- The bootstrap interval resamples learners with the edge set held fixed. The null relabels courses.
  An interval can exclude zero while p is large, because the variation between edges, not sampling
  error, is what limits D.
- With the conditioning removed (weekly cohort only), D on P_red is +0.0527.
- Raw order with no catalogue control gives D +0.039 on P_red (p 0.38).

## What this means

This study cannot say whether course-level claims may sit on the projection of concept claims. Two
things are established:

1. On MOOCCubeX, the literal holonic projection degenerates: the reduction exists only in cs.
2. On free-enrolment data, catalogue-controlled course order is structurally blind to a
   population-wide course order, so it cannot test the projection at all.

For Paper II, this extends F3. The course-grain catalogue trap does more than inflate reliability: a
catalogue control strong enough to remove the trap also removes any shared prerequisite order. A
holonic test needs a course-grain outcome (performance in Y given X, conditioned on a general
factor). On this corpus the general factor exists for only 10.4% of the learners in the order data,
and the problem-to-course link was not built.

## Moves nothing

See `out/history-entry.json`.
