# Precise boolean checklists against Likert rubrics: what the reliability gain is made of, and what it costs

**Status: PRE-REGISTERED 2026-10-28 at 758e58f, before any model call; instruments frozen at c5b8ed3,
before any grading call. Floor revision 0 failed and revision 1 passed, both before any call. RUN
2026-10-28; results below the line.** Design, thresholds, predictions and verdict strings are fixed in the
docstring of `boolean.py`, which is the full record. Results go below the line; the plan above it is
not rewritten.

The outcome is a grader's mark on fixed work (`not-a-learner-outcome`).

## What is asked

Google's *A Scalable Framework for Evaluating Health Language Models* (Mallinar et al., npj Digital
Medicine 2026; arXiv 2503.23339) splits each Likert criterion into many precise yes/no questions and
reports higher inter-rater ICC in about half the rating time. The maintainer asked whether the
reliability costs validity:

- can some constructs not be captured as booleans;
- can a decomposition miss critical children;
- does this work beyond procedural assessment?

There are three reasons to doubt the headline:

- **The ICC unit.** The paper computes ICC per (query, response, question) tuple, so differences in
  base rate between questions raise it.
- **Binarised Likert lost.** It did worse than both formats, so what helped was precise wording.
- **A near-circular validity test.** The questions are templated on the very data the test removes.

## Design

- **Two arms on identical inputs.** LIKERT is the corpus's own rubric. BOOLEAN is a checklist
  authored from the same criterion text by a third model (gpt-5.5), scored as the share of YES.
- **Two corpora on the procedural–judgement axis.**
  - Mohler ASAG: short answers with a reference answer and two human raters, 620 answers over 62
    questions. The construct is "contains the right ideas".
  - Menagerie: 272 CS1 Java submissions, 3–4 human raters, four dimensions with the deposit's
    six-band rubric. Documentation and Readability read like checklists; Code Elegance is a judgement
    of the whole design; Correctness is not predicted, because neither arm sees the specification.
- **Two graders, each called twice.** gemini-3.5-flash-lite (Google direct) and gpt-5.4-mini (OpenAI
  direct), giving test–retest and cross-model reliability at the response level.
- **Planted defects: the missing-child test.** 120 good answers each get, separately, a false
  sentence contradicting the reference (CONTRA) and a size-matched neutral sentence. 120 weak answers
  get a key-terms-without-understanding sentence (STUFF) and a neutral one. A different model
  (gemini-3.1-pro-preview) checks the manipulation. The size rule is enforced by
  `shared/controls.check_control_scale`.
- **Statistic.** Pearson *r* throughout, because the boolean arm's coarser scale cannot buy it, with
  a cluster bootstrap by question or submission.

## Verdicts (fixed before any call)

| Question | Verdicts |
| --- | --- |
| validity, per corpus × dimension, margin 0.05 | BOOLEAN-MORE-VALID / LIKERT-MORE-VALID / EQUIVALENT / UNRESOLVED |
| test–retest and cross-model reliability, margin 0.03 | BOOLEAN-MORE-RELIABLE / LIKERT-MORE-RELIABLE / EQUIVALENT / UNRESOLVED |
| contradiction (good answers) | LIKERT-ALSO-BLIND (positive control failed) / CHECKLIST-BLIND-TO-CONTRADICTION / CHECKLIST-MORE-SENSITIVE / NO-DIFFERENCE-RESOLVED |
| stuffing (weak answers) | CHECKLIST-REWARDS-STUFFING / LIKERT-REWARDS-STUFFING-MORE / NO-DIFFERENCE-RESOLVED |

**Predictions:**

- **P1, reliability.** Boolean is more reliable on Mohler, by less than the per-tuple ICC suggests.
- **P2, validity.** The checklist is no worse than −0.05 on Mohler, Documentation and Readability,
  and worse on Code Elegance.
- **P3.** CHECKLIST-BLIND-TO-CONTRADICTION.
- **P4.** CHECKLIST-REWARDS-STUFFING.

Incremental validity (partial *r*) is reported descriptively only. Two measures of one construct with
independent errors each add to the other, so it cannot detect missing children.

## The floor (synthetic, before any call)

Revision 0 failed two checks:

- **The Mohler null wasn't null.** The arms' different output grids alone made Likert look more
  reliable on test–retest in 20.5% of null replicates, because a coarser grid loses test–retest *r*.
  The null now holds the grid fixed. GRID worlds report the cost of the grid alone: 22.5% (Mohler)
  and 23.5% (Menagerie). **A test–retest verdict for Likert is therefore read as possibly the grid
  alone.**
- **Menagerie is underpowered at ±0.10.** That difference is detected in only 54.5–58% of replicates.
  ±0.15 is detected in 87.5% / 83.5%, with the wrong sign in 0%, so a Menagerie UNRESOLVED does not
  rule out differences up to about 0.15.

Revision 1 passes every gated check. The planted-defect tests detect at 98–100%, with false rates of
1.5–2.5%. Figures are in `out/floor.json`, and revision 0 is in `out/floor-rev0.json`.

---

## Results

**The run.** 10,976 gradings: 8,800 Mohler and 2,176 Menagerie. None failed. The served models were
`gemini-3.5-flash-lite` and `gpt-5.4-mini-2026-03-17` on every call. Tokens: Gemini 24.3M in /
0.23M out; GPT 20.8M in / 0.96M out. Instruments: 66 gpt-5.5 calls for the checklists, 240 for the
perturbations, and 240 gemini-3.1-pro-preview manipulation checks.

- **Checklists.** Mohler has 284 checks over 62 questions (3–7 per question). The Menagerie
  dimensions have 10–12 checks each.
- **Perturbations.** 120/120 pairs kept in each kind, with a neutral-to-treatment length ratio of
  0.963 (contradiction) and 0.968 (stuffing). The manipulation check passes 120/120 and 112/120.
- **A failure the format introduces.** gpt-5.4-mini returned 12 answers for Readability's 10 checks
  in 46 of 544 Menagerie boolean calls (8.5%), on 45 submissions; one Gemini Likert call on a program
  also did not parse. By the pre-registered rule those 46 submissions leave every Menagerie table,
  which keeps 226 of 272. (Corrected 2026-10-28 per reproduction 1: this line first said all 46 were
  checklist miscounts.) The Likert arm has no counterpart, since a letter
  either parses or not.

### Validity (r with the human mean)

| table | n | Likert / boolean (gemini) | Likert / boolean (gpt) | dV [95%] | verdict | human ceiling |
| --- | ---: | --- | --- | --- | --- | --- |
| Mohler | 620 | 0.764 / 0.688 | 0.819 / 0.682 | −0.106 [−0.165, −0.048] | **LIKERT-MORE-VALID** | 0.621 (rater 1 vs 2) |
| Menagerie Correctness | 226 | 0.405 / 0.433 | −0.173 / −0.054 | +0.073 [−0.008, +0.150] | UNRESOLVED | 0.622 (one rater vs rest) |
| Menagerie Code Elegance | 226 | 0.035 / 0.017 | −0.182 / −0.137 | +0.013 [−0.075, +0.092] | UNRESOLVED | 0.539 |
| Menagerie Readability | 226 | 0.039 / −0.007 | −0.235 / −0.011 | +0.089 [−0.043, +0.189] | UNRESOLVED | 0.571 |
| Menagerie Documentation | 226 | 0.286 / 0.079 | −0.284 / −0.125 | −0.024 [−0.109, +0.050] | UNRESOLVED | 0.525 |

**On Mohler, the corpus a checklist was predicted to suit, the checklist is less valid** for both
graders (dV −0.075 Gemini, −0.137 GPT; consistent). Against one rater at a time, the fair comparison
with the human ceiling (0.621), the Likert arm reaches 0.594–0.819 and is above the humans in three
of four model × rater pairs. The boolean arm reaches 0.526–0.675.

**Menagerie cannot answer the validity question.** On Code Elegance, Readability and Documentation
neither grader tracks the raters in either format. Gemini reaches −0.01 to 0.29, and gpt-5.4-mini is
negative in every dimension and both arms. That is not a coding error: Gemini runs through the same
pipeline and reaches +0.51 on untruncated Correctness. The pre-registered verdicts stand as
UNRESOLVED.

The post hoc reading, recorded in `out/results.json` under `post_hoc_all_parsed` and labelled post
hoc in the script: the format contrast there is between two instruments that do not see the
construct. The raters give longer submissions higher grades (r +0.40 to +0.53 with code length).
gpt-5.4-mini gives them lower ones (−0.14 to −0.50), with or without truncation. Gemini's checklist
answers YES to nearly everything on Code Elegance and Readability: mean score 0.990 and 0.994, SD
0.05 and 0.03. That is the no-discrimination signature (`grader-eval/findings/rubric-and-goal-graph.md`
§4a), produced by the format.

### Reliability

| table | retest L / B (gemini) | retest L / B (gpt) | dR [95%] | verdict | cross-model L / B | dX [95%] | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Mohler | 0.987 / 0.961 | 0.962 / 0.965 | −0.011 [−0.023, −0.001] | LIKERT-MORE-RELIABLE | 0.885 / 0.906 | +0.021 [−0.022, +0.067] | UNRESOLVED |
| Menagerie Correctness | 0.707 / 0.596 | 0.663 / 0.426 | −0.174 [−0.280, −0.063] | LIKERT-MORE-RELIABLE | −0.164 / −0.159 | +0.006 [−0.163, +0.143] | UNRESOLVED |
| Menagerie Code Elegance | 0.830 / 0.655 | 0.673 / 0.562 | −0.143 [−0.364, +0.016] | UNRESOLVED | 0.577 / 0.223 | −0.354 [−0.486, −0.200] | LIKERT-MORE-RELIABLE |
| Menagerie Readability | 0.832 / 0.747 | 0.745 / 0.445 | −0.192 [−0.429, −0.076] | LIKERT-MORE-RELIABLE | 0.586 / 0.019 | −0.567 [−0.675, −0.428] | LIKERT-MORE-RELIABLE |
| Menagerie Documentation | 0.684 / 0.650 | 0.451 / 0.285 | −0.100 [−0.224, +0.017] | UNRESOLVED | 0.231 / 0.212 | −0.019 [−0.187, +0.152] | UNRESOLVED |

**The checklist bought no reliability anywhere.**

- **Mohler.** Both formats are near the top of the scale (test–retest 0.96–0.99). The Likert verdict
  there is 0.011 r. The floor showed that a coarser grid alone produces that verdict in about 23% of
  null replicates, so it is read as possibly the grid.
- **Menagerie.** The Likert format is more reliable by 0.14–0.57 wherever a verdict resolves. Some of
  that is a checklist answering YES to everything, which has no variance to be reliable with.

**The per-tuple unit did not inflate agreement here (P1b failed).** Between the two models, ICC(3,1)
per (answer, check) tuple is 0.803, below the boolean arm's response-level 0.889 and Likert's 0.865.
Only 27% of checks are answered YES at least 90% of the time, so the between-check variance that
would inflate a per-tuple ICC is small on these checklists. The critique of the paper's unit is not
supported by this data, at least for two model raters.

### Planted defects: the missing-child test

| test | n | D Likert | D boolean | C (boolean − Likert) | verdict |
| --- | ---: | --- | --- | --- | --- |
| contradiction (all 120 pass the manipulation check) | 120 | −0.473 [−0.514, −0.431] | −0.172 [−0.223, −0.124] | +0.302 [+0.255, +0.348] | **CHECKLIST-BLIND-TO-CONTRADICTION** (both models) |
| stuffing (manipulation pass) | 112 | +0.273 [+0.220, +0.325] | +0.348 [+0.283, +0.410] | +0.075 [+0.014, +0.136] | **CHECKLIST-REWARDS-STUFFING** (Gemini resolved; GPT +0.031 [−0.028, +0.089]) |
| stuffing (all) | 120 | +0.287 [+0.236, +0.338] | +0.367 [+0.303, +0.428] | +0.080 [+0.020, +0.138] | CHECKLIST-REWARDS-STUFFING |

D is on a 0–1 scale, against the size-matched neutral sentence on the same answer.

**Contradiction.** Appending one false sentence that contradicts the key point costs a good answer
47% of the Likert scale and 17% of the checklist score. The checklist loses about a third as much.
The checklist still records the answer's correct content as present, and its presence checks have
no child that asks whether what is present is also true.

**The children explain the gap.** Below, the pre-registered split ("no incorrect claim"
checks) sits beside the post hoc one (any check phrased "avoid …", which is how the author wrote its
targeted misconception checks). The post hoc split was added after reading the checklists and before
any grading call.

| split | n | D Likert | D boolean |
| --- | ---: | --- | --- |
| contradiction: checklist has a no-error check (pre-registered; all are also avoid checks) | 13 | −0.535 | −0.300 |
| contradiction: no no-error check | 107 | −0.466 | −0.156 |
| contradiction: checklist has an "avoid …" check (post hoc) | 77 | −0.491 | −0.224 |
| contradiction: no "avoid …" check | 43 | −0.442 | **−0.079** |
| stuffing: checklist has an "avoid …" check (post hoc) | 63 | +0.313 | +0.295 |
| stuffing: no "avoid …" check | 49 | +0.222 | **+0.417** |

Without a child that checks for errors, the checklist nearly ignores a contradiction (−0.08 against
Likert's −0.44). It also pays almost twice what Likert pays for key terms listed without
understanding (+0.42 against +0.22). With such a child, the stuffing gap closes, and the checklist's
loss to a contradiction nearly triples (−0.22 against −0.08), though it is still under half of
Likert's. These splits are descriptive, with no interval.

Both formats reward stuffing substantially. Likert adds 0.27 of the scale for a sentence that names
the right terms and states nothing correct, so key-term matching is not a checklist-only failure.

### Predictions

| prediction | outcome |
| --- | --- |
| P1 Mohler dR > 0 | **no** (−0.011) |
| P1 Mohler dX > 0 | yes in sign (+0.021), unresolved |
| P1b per-tuple ICC > response-level | **no** (0.803 vs 0.889) |
| P2 Mohler dV ≥ −0.05 | **no** (−0.106) |
| P2 Documentation, Readability dV ≥ −0.05 | yes (−0.024, +0.089), with neither arm valid |
| P2 Code Elegance dV < 0 | no (+0.013), with neither arm valid |
| P3 contradiction blindness | **yes** |
| P4 stuffing reward | **yes** (one model resolved) |

### Descriptive only

Partial r on Mohler, which by the docstring's argument is not a missing-children test:

- r(human, Likert | boolean) is 0.514 (Gemini) and 0.637 (GPT);
- r(human, boolean | Likert) is 0.265 and 0.186;
- r(Likert, boolean) is 0.754 and 0.746.

### What this says

1. **For an LLM grader, precise booleans did not buy reliability, and on the short-answer corpus
   they cost validity.** A model grader is already near the top of the test–retest scale with a
   Likert prompt, so there is little reliability left to buy. The paper's gain was measured with
   human raters, which this study does not test.
2. **A checklist built from a reference answer checks presence, not truth.** Unless it carries
   children that look for errors, it nearly ignores a contradicting claim and over-pays for
   keywords. The model author added such children unprompted for 77 of the 120 contradiction answers
   (64%, post hoc). They nearly tripled the checklist's response to a contradiction and closed the
   stuffing gap, but left it at under half of Likert's response.
3. **On judgement constructs the checklist can collapse to YES** (Gemini, Code Elegance and
   Readability). The format comparison there is uninformative, because neither format measures the
   construct with these graders.

### Limits

- Two graders, both small tiers, and one checklist author.
- The checklists are model-written with no human review. The manipulation check is a model, not a
  person.
- Menagerie's graders see no coursework specification (as in every earlier run). The boolean
  miscount drop is non-random (8.5% of one model's calls).
- Human raters, the population the paper measured, are not tested. Nothing here says booleans fail
  to help people.
