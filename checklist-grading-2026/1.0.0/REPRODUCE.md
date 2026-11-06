# Reproducing release `checklist-grading-2026`

Every result in the article recomputes from the per-case file published beside the release file
(`per-case-model-outputs.jsonl`). No corpus download and no model call are needed.

There are three ways in:

- **One command.** `python3 reproduce.py` copies `code/` to a temporary folder and runs each analysis
  there exactly as the release file records it. It then compares every output, byte for byte, with the
  published copy, and prints MATCH, DIFFERS or FAILED per step. `--list` shows the steps, and `--quick`
  skips the two detection floors. It needs Python 3.9+ with numpy, and matplotlib for the figures.
- **The notebooks.** The report's "re-run this finding" notebooks (also in `notebooks/` once the report
  is built) recompute the printed numbers of each research question from the per-case file, with only
  numpy.
- **The code.** Each analysis is a single script under `code/studies/measurement/`. Its docstring is the
  study's full record: question, design, registered verdicts, the detection floor and its revisions.

| step | reproduces | command (run from `code/`) |
| --- | --- | --- |
| `rq12-analyse` | Tables 1, 2 and 4, and the values of Figures 1, 2 and 4 | `python3 studies/measurement/grader-boolean-rubrics/boolean.py --analyse --cases ../per-case-model-outputs.jsonl` |
| `floor` | the registered study's detection floor | `python3 studies/measurement/grader-boolean-rubrics/boolean.py --floor --cases ../per-case-model-outputs.jsonl` |
| `rq23-mechanism` | Tables 3 and 5, and the values of Figures 3 and 5 | `python3 studies/measurement/grader-checklist-defects/defects.py --cases ../per-case-model-outputs.jsonl` |
| `mechanism-floor` | the follow-up's detection floor | `python3 studies/measurement/grader-checklist-defects/defects.py --floor --cases ../per-case-model-outputs.jsonl` |
| `figures` | Figures 1 to 5 | `python3 studies/measurement/grader-checklist-defects/figures.py` |

**What cannot be reproduced from the release.** The model calls cannot be re-sent: `boolean.py --build`,
`--perturb` and `--run` are packaged as the record of how the outputs were made. They need the two
public corpora and API keys, and the checklists and planted sentences they used paraphrase the
corpus text, which the release does not publish (their SHA-256 values are in
`code/studies/measurement/grader-boolean-rubrics/out/checklists.json` and `perturb.json`). The parent
floor's `seconds` field records its runtime and is ignored in the comparison. The figures' bytes depend
on the fonts matplotlib finds, so on another machine that step can report DIFFERS while every value
drawn is the same; the figure script checks each value against the article before drawing.
