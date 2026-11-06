# Brief: A yes/no checklist did not make an AI grader more consistent, and it missed errors

*Source: release checklist-grading-2026, version 1.0.1, 2026-11-06; DOI [10.5281/zenodo.24023968](https://doi.org/10.5281/zenodo.24023968) (published; 1.0.0 is [10.5281/zenodo.24023788](https://doi.org/10.5281/zenodo.24023788)).*

## The answer

Replacing a rating-scale rubric with a list of precise yes/no questions, as researchers at Google proposed for evaluating AI answers to health questions, did not make two AI graders of student work more consistent. On short answers the checklist agreed less with human graders, gave too little credit to good and partly good answers, and largely let a false statement in an answer go unnoticed.

## What we found

**1. The checklist was not shown to make grading more consistent.** Graded twice, both models gave nearly the same scores on short answers in either format (correlation 0.96 to 0.99), so a checklist had almost no room to help. On first-year Java programs, where the models were far less consistent, the rating scale was the more consistent format wherever the data clearly showed a difference.
*Confidence: two small, inexpensive models (Gemini 3.5 Flash Lite and GPT-5.4 mini); 620 short answers and 226 programs.*
Evidence: [reliability](https://reports.learningdesignalliance.org/checklist-grading-2026/1.0.1/report/index.html#51-reliability-rq1)

**2. On short answers the checklist agreed less with human graders.** Its scores correlated 0.69 and 0.68 with the human graders' average for the two models, against 0.76 and 0.82 for the rating scale. The checklist gave answers the graders judged partly correct 0.178 less credit than the rating scale did, and fully correct ones 0.111 less, which is consistent with its lower agreement. It was not shown to give wrong answers too much credit.
*Confidence: shown for both models on one course's short answers.*
Evidence: [agreement with the human raters](https://reports.learningdesignalliance.org/checklist-grading-2026/1.0.1/report/index.html#52-agreement-with-the-human-raters-rq2)

**3. The checklist mostly checked whether the expected ideas were present, not whether the answer was right.** A false sentence added to a good answer lowered the rating-scale score by 47% of the scale, but the checklist score by only 17%. A sentence that merely named the right technical terms raised the checklist score by 35% of the scale, against 27% for the rating scale. What the checklist did catch of a false statement came mainly from questions written to look for a particular mistake: where a checklist had them, they carried 76% of its drop.
*Confidence: false statements were clear contradictions planted by a model; subtler errors were not tested.*
Evidence: [planted errors](https://reports.learningdesignalliance.org/checklist-grading-2026/1.0.1/report/index.html#53-planted-defects-rq3)

**4. On the programming assignments the formats could not be compared.** On three of the four rubric dimensions the models tracked the human graders weakly or not at all, and on the fourth the difference between formats was too uncertain to call.
*Confidence: one corpus of first-year Java programs; with 226 programs, differences of up to about 0.15 in correlation could go undetected.*
Evidence: [agreement with the human raters](https://reports.learningdesignalliance.org/checklist-grading-2026/1.0.1/report/index.html#52-agreement-with-the-human-raters-rq2)

## What this means for you

**Administrators** asked to approve an AI grader built on a yes/no checklist should not accept "more consistent" as the reason. Ask for evidence that it agrees with independent human graders and that it catches a planted error.

**Learning designers** writing a checklist for an AI grader should add questions that look for the specific mistakes and misconceptions that matter, because little else in a checklist notices a wrong statement. A checklist score runs low for good work, so a pass mark set for a rating scale will not carry over.

**Product managers** weighing a switch from a rating scale to a checklist should expect no gain in consistency where the grader is already consistent, and a grader that rewards students for naming the right terms.

**Data scientists** evaluating a change of rubric format should report reliability and agreement with human graders separately, check where in the range of answers the formats part, and test each format with planted errors against a matched harmless sentence.

**Researchers** should not read a gain in agreement between raters as a gain in validity. A rubric format's effect on reliability depends on where agreement starts, and on how many different scores the format can give.

## What this does not show

- Two small models were tested; larger models may follow long checklists better.
- The short answers come from one data-structures course; longer or more open questions may favor or disfavor checklists differently.
- The checklists, the planted sentences and their checks were each made by a model, with no human review.
- No human grader used either format, so nothing here bears on checklists for human graders, the setting of the Google framework.
- The planted errors were clear contradictions; subtler mistakes may be caught less often by either format.

## Read more

- [Full report](https://reports.learningdesignalliance.org/checklist-grading-2026/1.0.1/report/index.html)
- [Article](https://github.com/Learning-Design-Alliance/learning-research-reports/blob/main/checklist-grading-2026/1.0.1/article/precise-checklists-and-an-ai-grader.md)
- DOI: [10.5281/zenodo.24023968](https://doi.org/10.5281/zenodo.24023968) (1.0.1, published); [10.5281/zenodo.24023788](https://doi.org/10.5281/zenodo.24023788) (1.0.0)
- Wiki claims:
  [Precise yes/no checklists were not shown to make LLM grading more reliable](https://wiki.learningdesignalliance.org/claims/precise-yes-no-checklists-do-not-make-llm-grading-more-reliable/);
  [A model-written yes/no checklist agrees less with human raters on short answers](https://wiki.learningdesignalliance.org/claims/a-model-written-checklist-agrees-less-with-human-raters-on-short-answers/);
  [Checklists written from a reference answer miss false claims and reward key terms](https://wiki.learningdesignalliance.org/claims/reference-answer-checklists-miss-false-claims-and-reward-key-terms/)
