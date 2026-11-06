# Per-case model outputs: data dictionary

The data file `per-case-model-outputs.jsonl` ships beside the release file `1.0.0.yaml` of research
release `checklist-grading-2026`. That record declares it as dataset `per-case-model-outputs`, with its
SHA-256, line count and size.

The file holds, for every grading made in the study, the item's ids and human scores, its draw, its
checklist's structure and its perturbation flags, and the model's score and per-check answers.
**It holds no answer text, program, checklist text, planted sentence, prompt or model rationale.**

It was written by `python3 boolean.py --strip`, in `code/studies/measurement/grader-boolean-rubrics/`,
from the study's private per-call dumps, the two corpora and the frozen checklists and perturbations.
The script is deterministic: the same inputs always give the same bytes. Every analysis in the release
runs from this file alone (`REPRODUCE.md`).

## Format

The format is JSON Lines, UTF-8, one object per line, with keys sorted. Every object has a `record`
key. The 12,000 lines are, in this order:

- **1 `study` line.** The release id, the two graders (`gemini`: Google, `gemini-3.5-flash-lite`;
  `gpt`: OpenAI, `gpt-5.4-mini`), the SHA-256 of the frozen checklists and of the frozen perturbations,
  and the draw seed.
- **66 `question` lines.** One per Mohler question (62) and one per Menagerie dimension (4).
- **957 `item` lines.** One per Mohler answer in any draw (685) and one per Menagerie submission (272).
- **10,976 `grade` lines.** One per model call.

### `question` lines

| key | meaning |
| --- | --- |
| `corpus` | `mohler` or `menagerie` |
| `q` | Mohler question id as the corpus publishes it (`E<exercise>.Q<question>`), or the Menagerie dimension |
| `n_checks` | number of checks in that checklist |
| `avoid_check`, `avoid_by_check` | (Mohler) whether any check, and which checks in order, match the rule `\bavoid`: the article's *error checks* |
| `no_error_check`, `no_error_by_check` | (Mohler) the same for the pre-registered no-error rule (all 8 matching checks are also avoid checks) |

### `item` lines

| key | meaning |
| --- | --- |
| `corpus`, `id` | Mohler answer id as published (`E01.Q01.A00`), or Menagerie `assignment_number` |
| `q` | the bootstrap cluster: the Mohler question, or the Menagerie submission itself |
| `draws` | Mohler: any of `main` (the 620-answer draw), `high`, `low` (the planted-defect draws); Menagerie: `main` |
| `g1`, `g2`, `h` | (Mohler) the two raters' scores and their mean, 0–5, as the corpus publishes them |
| `raters` | (Menagerie) each dimension's grades from its raters, on the 14-level scale mapped to 0–13 (F = 0 … A++ = 13) |
| `h` | (Menagerie) each dimension's mean grade, 0–13 |
| `chars` | length in characters of the graded answer, or of the concatenated program as graded (after truncation) |
| `truncated` | (Menagerie) whether the program was cut at 90,000 characters |
| `contra`, `stuff` | (Mohler, planted-defect draws) `ok` (a length-matched pair was produced), `manip_pass` (the manipulation check passed), `manip` (the checker's four YES/NO answers), `chars_treatment`, `chars_neutral` |

### `grade` lines

| key | meaning |
| --- | --- |
| `corpus`, `id` | the item graded |
| `form` | `orig`, or for a planted-defect answer `contra-treat`, `contra-neutral`, `stuff-treat`, `stuff-neutral` |
| `model` | `gemini` or `gpt` |
| `arm` | `likert` or `boolean` (the checklist) |
| `rep` | 0 or 1: the first or second independent call |
| `served` | the model string the provider reported for the call |
| `error` | null, or the error text of a failed call (none failed) |
| `score` | (Mohler) the score on 0–1: Likert score / 5, or the checklist's share of YES; null if the reply did not parse |
| `scores` | (Menagerie) each dimension's score on 0–1: letter grade index / 13, or share of YES; null if the reply did not parse |
| `checks` | the checklist's YES/NO answers in check order (`true` = YES); per dimension for Menagerie; null for Likert |
| `tokens_in`, `tokens_out` | billed input and output tokens (output includes reasoning tokens) |

## Reading it

`pandas.read_json(path, lines=True)` reads the file. Filter on `record` to separate the four kinds.

## Sources and licences

The human scores are those published by the corpora, under their licences:

- **Mohler ASAG** (Mohler, Bunescu & Mihalcea 2011), from the Hugging Face mirror `nkazi/MohlerASAG`
  at revision `dac06732`, CC BY 4.0.
- **Menagerie** (Messer, Brown, Kölling & Shi 2024), OSF `q8jbt`, CC BY 4.0.
