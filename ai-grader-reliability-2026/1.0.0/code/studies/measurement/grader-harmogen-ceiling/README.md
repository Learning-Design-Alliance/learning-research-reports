# HARMOGEN-R re-analysed: the instructors' ceiling, in Python

The docstring of `harmogen.py` is the primary record (question, design, input, how it was ported).

## What was asked

Paper VI (release `ai-grader-reliability-2026`) prints four HARMOGEN-R figures in section 5.1 (23,100
instructor pairs; QWK 0.981 pooled, 1.000 on the multiple-choice half, 0.942 on the open half), and the
release's observation record `lazuli-grader-harmogen-2026` prints many more. They came from
`stability.ts --mode harmogen` (`harness/harmogen.ts`) in the evaluation harness, which the release does
not publish, and no aggregate output was committed. Scope-audit-20 (finding 2) found that a reader could
not recompute them from the release. The maintainer chose to port the re-analysis to Python and ship it
(corrections-20, 2026-10-15).

The question the analysis answers is unchanged: how far do four instructors who scored the same
responses agree with each other, measured with the same pairwise construction and the same QWK as the
release's other human ceilings, and how does that depend on how open the items are? The port is a
translation, not a redesign. It is not pre-specified.

## Data

The release file's `harmogen-r` dataset entry (`1.0.0.yaml`, `datasets:`) gives the location (Zenodo,
doi:10.5281/zenodo.19534458, CC BY 4.0) and the SHA-256 of `harmogenr_dataset_v2.zip`
(md5 `68a8a970e4b5f2e833fd5f8c686d5a89`); the script reads it from `HARMOGEN_DIR`. The script reads three tables
(`questions.csv`, `student_responses.csv`, `evaluations.csv`) from an extracted copy or from the zip.
Only counts and agreement statistics are committed (`out/results.json`). No model is called.

## Reproduce

Download `harmogenr_dataset_v2.zip` from the location in the release file's `harmogen-r` dataset entry
and check its SHA-256 there (`REPRODUCE.md`, "Public corpora", lists the same route), then, from `code/`:

```bash
python3 studies/measurement/grader-harmogen-ceiling/harmogen.py --root "$HARMOGEN_DIR"
```

`reproduce.py --only ref-harmogen` beside the release file runs the same command and compares the output
with the published one.

About ten seconds; standard library only. Two runs give a byte-identical `out/results.json`, whether
the tables are read from the zip or from an extracted copy.

## Checked against the original

The unmodified TypeScript (`harmogen.ts`, `menagerie.ts`, `metrics.ts`) was run under Node 22.22 on the
same tables, with a short driver that mirrors `runHarmogen` and prints unrounded values. All 538 values
(both binnings, every block, construction and statistic, the unanimity and extreme-mark shares) are
bit-identical to the port's. A first draft of the port differed in the last bit of two QWK values,
because it multiplied the weight before dividing by n; the original divides first, and the port now does.

## What came back

At 21 levels (a 5-point grid), unrounded values in `out/results.json` under `by_levels.21.blocks`:

| Cells | n (instructor pairs) | Instructor vs instructor QWK | LLM vs instructor QWK | Cells all four instructors identical |
| --- | --- | --- | --- | --- |
| All 3,850 | 23,100 | 0.98085 | 0.96846 | 69.8% |
| Bare option letter, 1,925 | 11,550 | 1.00000 | 1.00000 | 100% |
| Open, 1,925 | 11,550 | 0.94250 (0.9424986) | 0.90481 | 39.5% |
| Open text, 1,155 | 6,930 | 0.94911 | 0.94387 | 48.0% |
| Open code, 770 | 4,620 | 0.93130 | 0.83681 | 26.9% |

At 11 levels the pooled ceiling is 0.98007. The LLM's mean bias against the instructors is −0.40503
levels pooled and −2.17908 on the code questions (negative: the LLM marks below the instructor). On the
unbinned 0–100 scores, over the same 138,600 LLM–instructor pairs, the pooled bias is −2.02002 points
(`descriptives.unbinned_machine_human_bias`, an addition described below).

## Every printed HARMOGEN-R number, recomputed

Each number the paper, the release file, the claim pages and the observation records print was
recomputed from `out/results.json` and rounded once, half up, from the unrounded value. All 61 that
corrections-20 counted now match, with their signs, and so do the three that corrections-21 added to the
record (the unbinned bias −2.02, and 0.95 and 0.93 for the open text and open code questions). They include, in the paper, 23,100, 0.981, 1.000 and 0.942. The observation record adds
0.980 at 11 levels, 0.949, 0.931, 0.968, 0.978, −0.41, 0.985, 0.905, 96%, 0.980 and 0.988 for the
aggregate, 0.986 and 0.988 for all text cells, 0.837, −2.18, 0.944, 0.005, 0.094, 99%, 70%, 40%, 27%,
80%, 385 of 770, nine questions at 62–98%, 3,850, 15,400, 34,650 and 138,600, and the binned pooled
bias, −0.405 levels, which converts to −2.03 points on the 5-point grid (−0.40503 × 5 = −2.0251).

The record first printed −2.05 for that conversion, the rounded −0.41 multiplied by 5, a double rounding;
it was corrected to −2.03 (2026-10-15). Its sentence "bias matches to two decimal places", against the data
paper's −2.02%, then no longer held for the binned figure. The record now prints the unbinned pooled bias,
−2.02 points (−2.02002), which does match the data paper's −2.02% to two decimal places, beside the binned
−0.405 levels (corrections-21). The paper does not print either number.

Three figures in the record are not computed by the TypeScript mode, and the port reports them under
`descriptives`, each labelled as an addition. They are the corpus counts; the three constructions by
question type over all cells (text: 0.98618 for the LLM, 0.98765 for the instructors, 80.5% unanimous);
and `unbinned_machine_human_bias` (n 138,600; −2.02002 points), the mean of LLM minus instructor over the
same machine–instructor pairs on the normalised 0–100 scores before binning. They use the same cells and
the same pair order as the ported code, and adding the last left every other value in `out/results.json`
byte-identical.

## What this means for Paper VI

The HARMOGEN-R figures in section 5.1 now come from a committed analysis whose code, output and
`reproduce.py` step ship with the release. No printed number in the paper changed.
