# Brief: Telling an AI grader about the student changes the grade

*Source: release ai-grader-reliability-2026, version 1.0.1, 2026-10-19; DOI [10.5281/zenodo.23488287](https://doi.org/10.5281/zenodo.23488287) (reserved; 1.0.0 is [10.5281/zenodo.23480844](https://doi.org/10.5281/zenodo.23480844)).*

## The answer

Told how well a student has done before, a grader built on a large language model (LLM) gives the same answer a different mark, on every model tested. That information was not shown to improve its judgment, and the usual check, agreement with a teacher's marks, did not catch it.

## What we found

**1. The same answer gets a different mark depending on what the grader is told about the student.** Each answer was graded under a high and a low "label" (one prompt sentence giving the student's attainment as a number). On short answers, six models from five developers gave the same answer 0.28 to 0.75 points more on a ten-point scale under the high label; a false low label cost a strong student 0.30 to 0.79 points. Whether that moved marks toward or away from the teacher's depended on the model.
*Confidence: shown on six models, and on a seventh (Claude Fable 5.1) on a 100-answer subset.*
Evidence: [the label on identical work](https://reports.learningdesignalliance.org/ai-grader-reliability-2026/1.0.1/report/index.html#the-label-on-identical-work)

**2. The label was not shown to make the grader a better judge, though agreement scores can make it look like one.** On three model configurations the label raised QWK (quadratic-weighted kappa, a chance-corrected agreement score) by 0.029 to 0.046, consistent with shifting where marks land, not better judgment. Rescaling marks without student information beat the raw labeled marks by 0.038 QWK on average.
*Confidence: not shown to help; once both are rescaled, a gain above 0.035 QWK is ruled out.*
Evidence: [effect of the label on accuracy](https://reports.learningdesignalliance.org/ai-grader-reliability-2026/1.0.1/report/index.html#effect-of-the-label-on-accuracy)

**3. A low mark on an earlier attempt drags the new grade down; a high one does not lift it.** A previous attempt shown with a low mark lowered the grade on identical work by 0.44 points; the same attempt without its mark did not.
*Confidence: shown on one model (Gemini 3.5 Flash Lite) only.*
Evidence: [a previous attempt and its mark](https://reports.learningdesignalliance.org/ai-grader-reliability-2026/1.0.1/report/index.html#52-rq1-a-previous-attempt-and-its-mark)

**4. Over a course the effect grows modestly, and costs most to students wrongly recorded as weak.** In a simulated course where grades update the learner model (the platform's estimate of what each student knows), which supplies the label, the effect is amplified by a factor of 1.066 to 1.167 over a term, yet stays stable. Strong students whose record starts wrongly low take 1 to 3 more items to recover.
*Confidence: a simulation driven by four of the measured models, not an observed course.*
Evidence: [the loop over a course](https://reports.learningdesignalliance.org/ai-grader-reliability-2026/1.0.1/report/index.html#55-rq4-the-loop-over-a-course)

**5. Leaving the label out does not make the grader mark every group alike.** On 3,000 school essays graded by two models, the label's effect was not larger for any group tested. With no label, both models marked English learners' and disability-identified students' essays below their peers' at equal human score, and 68 to 87% of that gap remains after correcting for noise in the human scores.
*Confidence: shown on two models and one corpus; whether the human raters marked every group alike is untested.*
Evidence: [demographic groups](https://reports.learningdesignalliance.org/ai-grader-reliability-2026/1.0.1/report/index.html#57-rq6-demographic-groups)

## What this means for you

**Administrators** approving an AI grader can require that the student's record stay out of it, a rule that costs little and is easiest to set when a platform is designed. Grades for a group where a difference is found warrant human review before they inform decisions about students.

**Learning designers** should give the grader the question, the rubric and the answer, and nothing about the student, not even a neutral sentence. Graded example answers do not reliably fix a grader that marks too high or too low; they shifted marks by a fixed amount instead.

**Product managers** deciding whether to pass the learner model's estimate to the grader have the paper's argument against it: the grader gains no information the system lacks, and a grade that partly reflects the estimate is a weaker test of it. Switching models is no substitute: none tested, including the most expensive, was free of the effect.

**Data scientists** should add four checks to agreement with human scores, each with a threshold set in advance. These are Pearson r, which separates better ranking from shifted marks; signed error for weaker and stronger work; marks on identical answers with and without each piece of student information, which needs no human scores; and a repeated run.

**Researchers** should not report agreement with a human reference alone, and should state its reliability. Comparisons within the same answer (a true against a swapped label, and a same-length neutral sentence) carried this result.

## What this does not show

- It measures the mark, not the written feedback.
- The short-answer and program corpora are undergraduate computer science in English, and the learner-context tests rest on one of them, with 79 students; nothing was tested on a Lazuli course.
- The label is one fixed sentence standing in for a learner model's estimate; vaguer or implied wording may move marks more.
- The grader is formative only; grades of record were not studied.
- Higher-cost model tiers such as GPT-5.5 were not run as graders.
- The design shows the label changes the mark on the same answer, not why.
- The harness and production prompt are held back: results can be recomputed from the published outputs, but prompts cannot be re-sent.

## Read more

- [Full report](https://reports.learningdesignalliance.org/ai-grader-reliability-2026/1.0.1/report/index.html)
- [Article](https://github.com/Learning-Design-Alliance/learning-research-reports/blob/main/ai-grader-reliability-2026/1.0.1/article/attainment-bias-in-llm-grading.md)
- DOI: [10.5281/zenodo.23488287](https://doi.org/10.5281/zenodo.23488287) (1.0.1, reserved); [10.5281/zenodo.23480844](https://doi.org/10.5281/zenodo.23480844) (1.0.0)
- Wiki claims:
  [Showing an LLM grader a learner's prior performance biases the grade](https://wiki.learningdesignalliance.org/claims/showing-a-grader-a-learners-prior-performance-biases-the-grade/);
  [Graded exemplars shift an LLM grader by the level they are marked at](https://wiki.learningdesignalliance.org/claims/graded-exemplars-shift-an-llm-grader-by-the-level-they-are-marked-at/);
  [Human graders agree less than single-grade ground truth implies](https://wiki.learningdesignalliance.org/claims/human-graders-agree-less-than-single-grade-ground-truth-implies/);
  [LLM short-answer graders and human rater agreement](https://wiki.learningdesignalliance.org/claims/llm-short-answer-graders-can-reach-human-rater-agreement/);
  [Pooling repeated LLM grades does not improve agreement](https://wiki.learningdesignalliance.org/claims/pooling-repeated-llm-grades-does-not-improve-agreement/);
  [Surface formatting changes shift LLM grades](https://wiki.learningdesignalliance.org/claims/surface-formatting-changes-shift-llm-grades-without-penalising-them/);
  [Course context helps terse answers and dilutes long ones](https://wiki.learningdesignalliance.org/claims/course-context-helps-sparse-items-and-dilutes-rich-ones/);
  [Delimiting untrusted learner text blocks authority-claim injection](https://wiki.learningdesignalliance.org/claims/delimiting-untrusted-learner-text-defeats-authority-claim-injection/)
