# Reproducing Paper VI

Everything needed to recompute the paper's results, apart from the original single runs and the two
harness analyses listed under "What cannot be reproduced", is published with this release: the per-case model outputs
(`per-case-model-outputs.jsonl`), the analysis code (`code/`), and one script that runs it all
(`reproduce.py`). No model is called; the results are recomputed from the model outputs the study
recorded. There are three ways in, from quickest to most thorough.

## 1. Check one finding (a minute)

Each research question has a notebook that recomputes its headline numbers from the per-case file and
checks them against the paper. In the HTML report, open the green **Re-run this finding** panel under
the result, download the notebook and the data file into one folder, and run all cells (Python 3.9 or
later with numpy).

| Research question | Notebook | Also needs |
| --- | --- | --- |
| RQ1, a previous attempt and its mark | `rq1-history-arms.ipynb` | nothing else |
| RQ2, the attainment label | `rq2-label-effect.ipynb` | nothing else |
| RQ3, graded example answers | `rq3-graded-examples.ipynb` | nothing else |
| RQ4, the loop over a course | `rq4-loop.ipynb` | the `code/` folder beside it |
| RQ5, generality across models, settings and items | `rq5-generality.ipynb` | nothing else |
| RQ6, demographic groups | `rq6-groups.ipynb` | the ASAP 2.0 corpus (below) |

## 2. Reproduce everything (about 17 minutes on a 4-CPU machine)

```bash
pip install -r code/studies/measurement/grader-eval/analyses/requirements.txt
python3 reproduce.py            # or --quick to skip the slow steps, --only rq2 for one question
```

It copies `code/` to a working folder, rebuilds the per-case files, runs every analysis exactly as the
release file records it, and compares each output byte for byte with the published one. It never
changes `code/`. It ends with one line per step: **MATCH**, **DIFFERS**, **SKIPPED** (with what is
missing) or **FAILED**. `python3 reproduce.py --list` shows every step and the result it reproduces:

| Step | Reproduces | Needs |
| --- | --- | --- |
| `rq1-history` | 5.2 table, previous-attempt arms | published data only |
| `rq2-label`, `rq2-models`, `rq2-learners`, `rq2-r-check`, `rq2-pooling` | 5.3 cross-model and accuracy tables; Figures 1 and 2 | published data only |
| `rq2-dose`, `rq2-dose-posthoc` | label dose; Figure 3 | ASAP 2.0 (both steps) |
| `rq2-neutral` | the neutral-sentence control | published data only |
| `rq2-calibration`, `rq2-calibration-arms` | the label-free calibration table | published data only |
| `rq3-examples` | 5.4 graded-examples table; Figure 4 | published data only |
| `rq4-params`, `rq4-loop` | 5.5 loop table; Figure 5 | JorGPT for `rq4-params`, which reads it for the cohort's shape; `rq4-loop` needs published data only and takes about a minute and a half |
| `rq5-reasoning`, `rq5-items` | 5.6 reasoning and item-type tables | published data only |
| `rq6-groups`, `rq6-matching`, `rq6-label-check`, `rq6-reliability` | 5.7 tables; Figure 6 | ASAP 2.0 (`rq6-matching` takes about seven minutes) |
| `ref-offset`, `ref-removed-rows`, `ref-ceilings`, `ref-ceilings-posthoc` | 5.1 reference and human ceilings | JorGPT, Mohler, Menagerie |
| `ref-harmogen` | 5.1 the HARMOGEN-R instructor ceiling (0.981 pooled, 1.000 and 0.942 on the two halves) | HARMOGEN-R |
| `figures` | Figures 1–6, compared with the published images | published data only |

**Public corpora.** A few steps also read a public corpus, which the release does not redistribute: it
publishes no corpus text. Download it, then set the environment variable to its folder; without it those steps
are skipped and the rest still run. The release file (`1.0.0.yaml`, `datasets:`) gives each file's
SHA-256.

| Variable | Corpus | Where | File the steps read |
| --- | --- | --- | --- |
| `ASAP2_DIR` | ASAP 2.0 | kaggle.com/datasets/lburleigh/asap-2-0 (version 8) | `ASAP2_train_sourcetexts.csv` |
| `JORGPT_DIR` | JorGPT | doi:10.5281/zenodo.18981627 | `dataset_en.csv` |
| `MOHLER_DIR` | Mohler ASAG | huggingface.co/datasets/nkazi/MohlerASAG, revision dac06732 | `data/cleaned-oe-00001.parquet` (the script makes `mohler_en.csv` from it) |
| `MENAGERIE_DIR` | Menagerie | osf.io/q8jbt | `grades.csv` |
| `HARMOGEN_DIR` | HARMOGEN-R | doi:10.5281/zenodo.19534458 | `harmogenr_dataset_v2.zip`, zipped or extracted (the step reads three of its `csv/tables/` files) |

## 3. Read the code

`code/` keeps the layout of the repository the work was done in, so every path the paper gives resolves inside it.
Each study is a folder under `code/studies/measurement/`: its script's opening docstring is the
primary record of the design, the controls and the pre-registered verdicts; its `README.md` says what
was asked and what came back; `out/` holds the published outputs. The paper's section 9 maps each study
to its research question. `code/SHA256SUMS` hashes every file.

## What cannot be reproduced from this release

- **The model calls.** The evaluation harness that sent the prompts, and the production grading prompt
  it imports, are not published. Every result except the original single runs and the two harness
  analyses (below) can be recomputed from the recorded outputs and the public corpora; the prompts
  cannot be re-sent.
- **The Fable 5.1 agent bookkeeping** (batches and keys). Its statistics are recomputed from the
  per-case file by the RQ5 notebook and by `fable.cluster_stats` in `code/`.
- **Two small analyses that draw samples through the harness** (`sampling_sd.ts`,
  `mohler_ceiling_draw.mts`). Their outputs are published under `code/studies/measurement/grader-eval/analyses/out/`,
  but they cannot be regenerated from this release.
- **The original single runs.** The baseline table and the grader against each Corpus B rater (paper
  5.1), the first attempt-history run (5.2), the original attainment contrast (5.3), the original
  exemplar table (5.4), the three passes of one configuration behind the paper's resolution of ±0.02
  QWK (4.8) and the corpus baselines' spread ratios on a smaller first run (5.1) left no per-case output.
  Their figures are reported from the observation records `lazuli-grader-jorgpt-2026` and
  `lazuli-grader-mohler-2026`. The same holds for every other figure from a run whose output was not
  kept, which the paper labels where it appears: the preliminary runs of the design history (4.9), the
  pricing and reasoning-token probes (4.3 and 5.6) and the unseeded draw of 0.795 (4.8); section 9 of
  the paper names the record each is reported from. None can be recomputed from this release, and no
  step of `reproduce.py` regenerates them.

## Notes

- Thread count matters for byte-identical output in four steps: `rq6-matching`, `rq6-label-check` and
  `rq6-reliability` run single-threaded, and `rq6-groups` runs at the default (`reproduce.py` sets
  this). `ref-ceilings` and `ref-ceilings-posthoc` also run single-threaded, as their outputs were
  regenerated from the published file, although the default thread count gives the same bytes.
- The times above are from one run on a 4-CPU machine and depend on the machine; `--quick` skips the
  two slow steps, `rq4-loop` and `rq6-matching`.
- While the release is under embargo, its Markdown and `.txt` files carry one embargo line (the first
  line, or the first after a file's front matter), removed at publication. `SHA256SUMS` hashes the
  files without it, and `reproduce.py` compares outputs without it.
