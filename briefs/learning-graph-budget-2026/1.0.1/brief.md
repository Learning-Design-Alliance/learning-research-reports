# Brief: Learner records rarely show that one skill must come before another

*Source: release learning-graph-budget-2026, version 1.0.1, 2026-10-19; DOI [10.5281/zenodo.23488368](https://doi.org/10.5281/zenodo.23488368) (published; 1.0.0 is [10.5281/zenodo.23480842](https://doi.org/10.5281/zenodo.23480842)).*

## The answer

A prerequisite edge is the claim, in a map of skills, that one skill must be learned before another; adaptive platforms use such edges to decide what a learner may do next. On most platforms, learners' records cannot say whether a given edge exists, and the statistic that seems to give its direction only sorts skills by difficulty. What the records can say is which skills belong together.

## What we found

**1. Testing an edge needs hundreds of learners who met a skill before passing its prerequisite, and few platforms have them.** An edge from skill *a* to skill *b* is tested by comparing learners who reached *b* after trying *a* without passing it with learners who reached *b* after passing *a*; a prerequisite is taken to lower first-attempt accuracy on *b* by 0.10. Most pairs of skills share few learners: the median pair had none in common on EDM Cup and 4 on ASSISTments. A test of that drop needs between 277 and 379 learners in each group, and only Eedi, with 118,971 learners, could test more than a quarter of its pairs.
*Confidence: measured on each corpus the atlas read; none randomized the order of skills, and a platform with many more learners per pair could hold tests these lack.*
Evidence: [existence and direction](https://reports.learningdesignalliance.org/learning-graph-budget-2026/1.0.1/report/index.html#51-rq1-existence-and-direction)

**2. Most edges the records do support could be general ability instead.** Learners who have not passed one skill tend to score lower on others, so almost any two skills look related. In the four corpora with enough supported edges to check, at most 27.6% still held once each learner's accuracy on other skills was taken out.
*Confidence: the adjustment is partial and may also remove real dependence, so an edge that fails it is unknown, not absent.*
Evidence: [few edges can be tested](https://reports.learningdesignalliance.org/learning-graph-budget-2026/1.0.1/report/index.html#61-few-edges-can-be-tested-and-most-supported-edges-do-not-s)

**3. The statistic that seems to orient an edge points from the easier skill to the harder.** It compares how often learners who failed each skill also failed the other, and its sign is set by which skill more learners fail. It is right only as far as difficulty rises along the true edges; in a simulated world where any one of a skill's prerequisites suffices and later skills are easier, it pointed most edges the wrong way.
*Confidence: an algebraic identity for this statistic, not an estimate; an estimator of another kind, which uses the order learners met skills in, was fooled in simulation when abler learners chose that order.*
Evidence: [the orientation statistic](https://reports.learningdesignalliance.org/learning-graph-budget-2026/1.0.1/report/index.html#62-the-orientation-statistic-read-from-learner-records-is-th)

**4. Edges did not repeat to the standard set, and repeating or matching a curriculum would not confirm them.** Split-half reliability (the correlation between rankings of pairs from two random halves of the learners) reached 0.643 on XES3G5M and 0.136 on EdNet, against a bar of 0.80, and in simulation a ranking above 0.80 had only 0.075 of its asserted edges true. On ASSISTments, Common Core grade order, assigned to skills by a name-matching rule no person checked, was not recovered: the excess over a deranged control (one in which no unit keeps its own pairing) was +0.0117, against a bar of 0.02.
*Confidence: validity is untested rather than shown or refuted; no independent order confirmed or contradicted the edges.*
Evidence: [reliability](https://reports.learningdesignalliance.org/learning-graph-budget-2026/1.0.1/report/index.html#52-rq2-reliability); [validity](https://reports.learningdesignalliance.org/learning-graph-budget-2026/1.0.1/report/index.html#53-rq3-validity)

**5. Edges added almost nothing to predicting learners' next attempts; the skills did the work.** On XES3G5M, a graph that language models built from question text helped prediction through its skills. Its edges raised AUC (the chance that a correct response is ranked above an incorrect one) by +0.000161, below the pre-registered bar of +0.001, though the test detected a planted edge effect as small as +0.0072. The dataset's own expert tree was equivalent to scrambled copies of itself, within the pre-registered margin of 0.001.
*Confidence: one corpus and simple statistical models; the outcome is the next attempt, not learning.*
Evidence: [usefulness](https://reports.learningdesignalliance.org/learning-graph-budget-2026/1.0.1/report/index.html#54-rq4-usefulness)

**6. What the records do identify is dependence between skills.** In 8 of 15 sets of XES3G5M skills, some pairs stayed related after a one-trait model (one general ability per learner) had accounted for each learner's ability; those pairs sit close together in the expert taxonomy. Across four national curricula, part of the dependence carried from one country's platform to another's (a regression coefficient of +0.125), and a larger part followed local teaching (+0.363).
*Confidence: the pair-level test cannot orient a pair or tell a prerequisite from a trait two skills share; the cross-curricular result rests on a map coded by a model and checked by one person, at a kappa (agreement corrected for chance) of 0.606.*
Evidence: [what is identified](https://reports.learningdesignalliance.org/learning-graph-budget-2026/1.0.1/report/index.html#55-rq5-what-is-identified)

## What this means for you

**Administrators** approving a platform that holds learners back until a prerequisite is mastered should treat each such rule as an instructional decision, not a finding about learners, until the edge has been tested at random. Enforcing prerequisites has a measured cost and a benefit not yet isolated: requiring every mapped remediation lowered completion in one randomized trial, though that arm also carried more work.

**Learning designers** can use learner records to decide which skills to group into a unit, which to tag on a question, and which earlier skills to draw on when forecasting a first attempt at a new one. A mined graph that agrees with the curriculum is not thereby confirmed, because its learners followed that curriculum.

**Product managers** should expect a graph mined from usage to describe how the platform's learners met and grouped skills. An edge can be tested by randomized edge release: withhold the gate from a random part of learners and compare the groups on the dependent skill. Randomizing learners, a drop of 0.10 in accuracy needs 291 to 385 per arm to detect, with workload equal between arms.

**Data scientists** should count, before fitting anything, the learners who met each dependent skill without its prerequisite, adjust supported edges for general ability, compare a graph with shuffled, deranged and reversed copies of itself rather than only with no graph, and measure how far difficulty rises along edges before reading a direction.

**Researchers** should report a mined graph as a measurement: how many pairs could be tested, how many supported edges survive the ability adjustment, its excess over a deranged control rather than its raw reliability, the reliability of any reference, and the time between attempts at which it was read.

## What this does not show

- It reads one outcome, first-attempt accuracy, against one size of effect; a smaller effect, or one on later attempts, speed or retention, would leave its pairs unknown, not contradicted.
- An untestable pair is unknown, not shown to have no edge. Randomized trials show order can matter, by +0.317 logits in one, but none tested an edge the records had decided.
- Predicting the next attempt is not learning; sequencing, retention and transfer were not measured.
- The corpora are those their providers released, mostly mathematics, and the usefulness of edges was tested on one.
- Some references were coded by a rule set or a model: the Common Core grades by an unchecked rule, the curriculum map checked by one person.
- Results from simulation hold for the worlds simulated.
- No record from the author's organization's own platform was read. Raw records are not published, under the providers' terms; a reader with the same access can reproduce every input.

## Read more

- [Full report](https://reports.learningdesignalliance.org/learning-graph-budget-2026/1.0.1/report/index.html)
- [Article](https://github.com/Learning-Design-Alliance/learning-research-reports/blob/main/learning-graph-budget-2026/1.0.1/article/what-learner-records-can-say-about-a-prerequisite-edge.md)
- DOI: [10.5281/zenodo.23488368](https://doi.org/10.5281/zenodo.23488368) (1.0.1, published); [10.5281/zenodo.23480842](https://doi.org/10.5281/zenodo.23480842) (1.0.0)
- Wiki claims:
  [Learner records rarely establish that a prerequisite edge exists](https://wiki.learningdesignalliance.org/claims/observation-cannot-establish-a-prerequisite-edge/);
  [The orientation statistic read from learner records is a difficulty sort](https://wiki.learningdesignalliance.org/claims/observation-orients-edges-only-where-prerequisites-gate/)
