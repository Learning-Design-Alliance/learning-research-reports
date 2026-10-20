# Reproduction 13: ai-grader-reliability-2026 1.0.0 (Paper VI), from the release directory alone

Reproducer: an agent with no part in the analyses, the draft, the release, any correction pass, or
the earlier audits and reproductions. Date: 2026-10-15.
- Audited HEAD `de01e5f807c632fe46492333fcda27bdc19030e0`, the head of `claude/bold-ptolemy-6odavp`,
  reached by `git merge --ff-only origin/claude/bold-ptolemy-6odavp` on the worktree branch.
- `git merge-base --is-ancestor d05bd6e HEAD` succeeds, so the latest headline correction is included.
- **No model was called.** Nothing in the article, the release, the code package, the studies or
  `readiness.yaml` was edited. No agent transcript was read.

**Scope.** A full reproduction through the release's new `reproduce.py`, plus:
1. every regenerated output compared byte for byte with the published one, independently of
   `reproduce.py`'s own comparison;
2. the six re-run notebooks in `notebooks/`, run from the copied release folder;
3. the five values of `corrections-18.md`, and every number changed in `git diff 4a5c0f8..HEAD` on the
   article and the release folder (4a5c0f8 is reproduction-12's audited commit), checked with sign;
4. the code package: `board/package_code.py --check` and `code/SHA256SUMS` against the copied files;
5. the release-stated invocations that `reproduce.py` does not run.

## Method

- **Release directory only.** `git archive HEAD research/wiki/research/releases/ai-grader-reliability-2026 |
  tar -x -C <A>`, `<A>` = a scratch folder outside the repository (no parent folder is a repository
  checkout, so the notebooks' data search cannot fall back to the repository). `diff -rq` against the
  worktree's release folder: identical. Before any run, `code/` was copied to `<A>/committed-code/`.
- **reproduce.py.** Run once with no flags, from the copied release folder, with `ASAP2_DIR`,
  `JORGPT_DIR`, `MOHLER_DIR`, `MENAGERIE_DIR` set to the corpus folders in the session scratchpad
  (`MOHLER_DIR` holding only the published parquet, so the script derived `mohler_en.csv` itself).
  Thread settings are the script's own: it sets `OPENBLAS_NUM_THREADS=1` for the three steps the
  release records as single-threaded (`rq6-matching`, `rq6-label-check`, `rq6-reliability`) and nothing
  otherwise. Wall time 20:20:12 to 20:36:47, 16.6 minutes on 4 CPUs.
- **Independent byte check.** For every file of every step: its mtime in the work copy (each is after
  the run started, so each was rewritten; `copytree` keeps the source mtime, so an unwritten file would
  show the old one), and plain `filecmp.cmp(shallow=False)` against the copied release's `code/`.
- **Hashes.** `per-case-model-outputs.jsonl` sha256 `4b0bd3e8…0586346d`. Corpora, read in place:
  JorGPT `dataset_en.csv` `1d5deb07…4343653c`; Mohler `cleaned-oe-00001.parquet` `f2aff37d…217376b0`,
  derived `mohler_en.csv` `7c64b6e1…fd605901`; Menagerie `grades.csv` `2a63ccf4…8d1cf7b` and the four
  archives `07a1ca90…6191d6`, `0c618cfc…5487d7`, `b1764a02…22502d`, `abecfef1…c8ddd`; ASAP 2.0
  `asap2.zip` `afef0d8b…5cd964`, member `ASAP2_train_sourcetexts.csv` `df6b816d…34a3dea`. Every value
  equals the release file's. HARMOGEN-R is not on this machine.
- **Environment.** Python 3.11.15; numpy 2.4.6, pandas 3.0.6, scipy 1.17.1, matplotlib 3.11.2.
- `<D>` = the rebuilt per-case folder (`reproduction/per-case`). Rounding half up.

## 1. Package checks and rebuilding the dumps

| # | Check | Result | Class |
| --- | --- | --- | --- |
| P1 | `python3 board/package_code.py --release ai-grader-reliability-2026 --check` (repository) | "code package … is current (117 files)", exit 0 | MATCH |
| P2 | `sha256sum -c SHA256SUMS` in the copied `code/` | 117 entries, 117 files besides SHA256SUMS. 102 OK; 15 text files fail, each carrying the embargo marker (13 on line 1, the two findings-log `.md` files on line 6, after the front matter). With the marker line removed all 15 hash to the listed value | EXPLAINED (embargo stamping; REPRODUCE.md now says "the first line, or the first after a file's front matter", which resolves reproduction-12 J2) |
| R1 | `strip_dumps.py rebuild --data . --out <D> --skip-missing-corpus --asap2 …` (run by `reproduce.py`) | "rebuilt 32 of 32 dumps" | — |
| R2 | `sha256sum -c per-case-dumps.sha256` in `<D>` | 30 OK; the two `grader-vi-groups/` files differ, as the release documents (they lose `resumedFrom`) | EXPLAINED (documented) |
| R3 | `sha256sum -c per-case-dumps.rebuilt.sha256` in `<D>` | 2/2 OK | MATCH |
| R4 | `strip_dumps.py verify --dump-dir <D> --data <release> --asap2 …` | stops at `grader-vi-groups/run-qwen.json`: its hash is not the original's. Same cause as R2: `verify` checks against the original dumps' hashes, and the release says the two ASAP 2.0 dumps cannot regain them | EXPLAINED (documented; see note O3) |

## 2. reproduce.py, every step

All 25 steps ran; none was skipped, none failed. `reproduce.py` printed "25 match, 0 differ,
0 skipped, 0 failed." and exited 0. The independent check agrees on every file.

| # | Step | Reproduces | Output(s) | Rewritten | Byte-identical (independent cmp) |
| --- | --- | --- | --- | --- | --- |
| S1 | `rq1-history` | 5.2 history arms | grader-attainment-prior/out/history-q4.json | yes (20:20:27) | **yes** |
| S2 | `rq2-label` | 5.3, four original models | grader-attainment-prior/out/results.json | yes (20:21:14) | **yes** |
| S3 | `rq2-pooling` | pooling re-run | grader-attainment-prior/out/pooling.json | yes | **yes** |
| S4 | `rq2-models` | 5.3 tables, Figures 1–2 | grader-model-breadth/out/models.json | yes (20:23:22) | **yes** |
| S5 | `rq2-learners` | label effect by student | grader-model-breadth/out/learners.json | yes | **yes** |
| S6 | `rq2-r-check` | change in Pearson r | grader-model-breadth/out/r_check.json | yes | **yes** |
| S7 | `rq2-dose` | label dose, Figure 3 (ASAP 2.0) | grader-label-dose/out/results.json | yes | **yes** |
| S8 | `rq2-dose-posthoc` | leave one model out | grader-label-dose/out/posthoc.json | yes | **yes** |
| S9 | `rq2-neutral` | neutral-sentence control | grader-neutral-control/out/results.json | yes | **yes** |
| S10 | `rq2-calibration` | label-free calibration | grader-calibration-vs-label/out/results.json | yes (20:26:00) | **yes** |
| S11 | `rq2-calibration-arms` | calibration, three arms | out/results-all-arms.json | yes (20:27:17) | **yes** |
| S12 | `rq3-examples` | 5.4, Figure 4 | grader-exemplar-marks/out/results.json | yes | **yes** |
| S13 | `rq4-params` | loop parameters | grader-label-compounding/out/params.json | yes | **yes** |
| S14 | `rq4-loop` | 5.5 loop table, Figure 5 | grader-label-compounding/out/results.json | yes (20:28:59) | **yes** |
| S15 | `rq5-reasoning` | 5.6 reasoning table | grader-model-breadth/out/reasoning.json | yes | **yes** |
| S16 | `rq5-items` | 5.6 item types | grader-label-stability/out/results.json | yes | **yes** |
| S17 | `rq6-groups` | 5.7 label by group (default threads) | grader-attainment-groups/out/results.json | yes | **yes** |
| S18 | `rq6-matching` | 5.7 corrected gap, Figure 6 (single-threaded) | grader-matching-artefact/out/results.json | yes (20:36:24; 406 s) | **yes** |
| S19 | `rq6-label-check` | label contrasts at known reliability | out/label-check.json | yes | **yes** |
| S20 | `rq6-reliability` | RQ6 rows at 0.75 and 0.86 | out/reliability-known.json | yes | **yes** |
| S21 | `ref-offset` | QWK offset (JorGPT) | grader-eval/analyses/out/qwk-offset.json | yes | **yes** |
| S22 | `ref-removed-rows` | Mohler removed rows | out/mohler-removed-rows.json | yes | **yes** |
| S23 | `ref-ceilings` | human ceilings, QWK and AC2 | grader-ceiling-robustness/out/results.json | yes | **yes** |
| S24 | `ref-ceilings-posthoc` | constant-grader readings | out/posthoc.json | yes | **yes** |
| S25 | `figures` | Figures 1–6 | 6 PNG + 6 SVG | yes (all 12) | **yes, 12/12**; also equal to the repository's `research/article/figures/` (12/12). fig5's re-run medians equal the committed and printed ones (23→25, 19→20, 21→23, 19→22) |

`diff -rq` of the copied `code/` against `<A>/committed-code/` after all runs shows only two
`__pycache__/` folders (note O1); no published file changed.

## 3. Release-stated invocations that reproduce.py does not run

Run in the work copy of `code/`, from it, as the release file states them.

| # | Command | Result | Class |
| --- | --- | --- | --- |
| X1 | `robustness.py --selftest`, `OPENBLAS_NUM_THREADS=1` | exit 0; out/selftest.json byte-identical | MATCH |
| X2 | `robustness.py --floor --dump-dir <D>`, single-threaded | exit 0; out/floor.json byte-identical | MATCH |
| X3 | `robustness.py --run --dump-dir <D>`, single-threaded as the release states (S23 ran it at default) | out/results.json byte-identical | MATCH (both thread settings give the same bytes; note O4) |
| X4 | `analyse.py --history <D>/reproduction-rerun/history-gemini.json` (the spot re-run) | overwrites history-q4.json, as expected; "high, NO mark" dMAE −0.143 [−0.267, −0.023] GAIN, as the release states | EXPLAINED (expected overwrite) |
| X5 | `analyse.py --history <D>/grader-vi/history-gemini.json` | restores history-q4.json byte for byte | MATCH |
| X6 | `asap2-label-by-group` single-threaded | one value differs, `coef` 0.04245702600813837 → 0.042457026008138374 (one ulp); the release says this analysis is byte-identical only at default threading, and REPRODUCE.md now says `rq6-groups` runs at the default | EXPLAINED (documented; reproduction-12 J1 resolved) |
| X7 | the same at default threading | byte-identical | MATCH |

## 4. The notebooks

All six were executed with `nbclient`, working directory the copied release's `notebooks/`, so each
found `per-case-model-outputs.jsonl` and `code/` in the folder above it; `ASAP2_DIR` was set for RQ6.
Each raises on any printed value that its recomputation does not give.

| Notebook | Result | What it reports |
| --- | --- | --- |
| `rq1-history-arms.ipynb` | PASS, no error cell | "All 19 printed point values and the derived figures match the paper." |
| `rq2-label-effect.ipynb` | PASS | "All 18 point estimates match the paper." |
| `rq3-graded-examples.ipynb` | PASS | "All 18 table values and 12 values in the text match the paper." |
| `rq4-loop.ipynb` | PASS (34 s) | fitted effects, r, w, γ* and the four fitted-effect multiples; "All 28 simulated point values in the table and text match the paper". Its assertions hold the corrected 12.6×, 11.8× and the range 5.9 to 12.6 |
| `rq5-generality.ipynb` | PASS (46 s) | 15 table values and the minimal-reasoning figures (including 0.38 SD), 12 values of s, the five Fable figures |
| `rq6-groups.ipynb` | PASS | "All 18 printed point values of the measured rows, and the spread and mid-label figures, match the paper." |

## 5. Numbers changed since 4a5c0f8, against the regenerated outputs

`git diff 4a5c0f8..HEAD` changes 160 lines of the article. Most are not numbers: links around DOIs and
URLs, the AI-use statement and byline note, the authorship, the section 9 table (result → study →
step → notebook, every step and notebook it names exists), and the removal of the list of claims
awaiting specialist review. Every number that is new or moved, recomputed from the outputs regenerated
in section 2:

| # | Where (line at HEAD) | Article | Regenerated source and value | Class |
| --- | --- | --- | --- | --- |
| C1 | 5.5 loop table, Gemini (L1511) | 12.6× measured | `grader-label-compounding/out/results.json` primary `analytic_latent_gamma`: γ* / (loop_gain / w) = 1.29289 / 0.10282 = 12.575 → 12.6 | MATCH (corrections-18) |
| C2 | 5.5 loop table, GPT-4.1-mini (L1512) | 11.8× | 1.29289 / 0.11000 = 11.754 → 11.8 | MATCH (corrections-18) |
| C3 | 5.5 text (L1536) and the Answer to RQ4 (L1564) | 5.9 to 12.6 | min Qwen 5.877 → 5.9, max Gemini 12.575 → 12.6; GPT-5-mini 8.374 → 8.4 unchanged | MATCH (corrections-18) |
| C4 | 5.6 (L1611) and discussion (L1894) | 0.38 SD (SD 2.78) | `models.json` GPT-5-mini minimal `learner_cluster.L` +1.04439 / `grader-label-stability` `sd_human` 2.784 = 0.37514 → 0.38; positive (an upward shift toward the label); 1.04439 / 2.78 = 0.3757 gives the same | MATCH (corrections-18) |
| C5 | 5.7 (L1770) | inflated by at most 0.03 at 0.75 and 0.014 at 0.86 | `reliability-known.json` `label_by_group`, low-label contrasts (D_low, D_lowmid) over both models and four groups: largest bias at 0.857 +0.01435 (Qwen, disability, D_low) → 0.014; at 0.75 +0.02964 → 0.03. Signs: D_low biases positive (inflating the favoring differences), D_lowmid biases negative (inflating the against-the-group readings, largest −0.0215 at 0.75, −0.0104 at 0.857), as the text says | MATCH (corrections-18) |
| C6 | 5.3 accuracy table, new row "Gemini 3.5 Flash Lite, thinking high" (L1302) | MAE −0.005 [−0.087, +0.072]; QWK +0.013 [−0.006, +0.031]; equivalent; inconclusive; no gain larger than +0.031 | `models.json` `[reasoning high]` `q4`: dMAE −0.00500 [−0.08689, +0.07245] EQUIVALENT; dQWK +0.01251 [−0.00581, +0.03126] INCONCLUSIVE, `largest_gain_admitted` 0.03126 | MATCH (sign checked; resolves reproduction-12 note O1) |

Further checks on the same diff:
- **No stale value remains.** `grep` for 12.5, 11.7×, "0.37 SD" and "0.015 at" finds nothing in the
  article, the release file or the two packaged study READMEs (`grader-label-compounding`,
  `grader-matching-artefact`), which now print 12.6×, 11.8× and ≤ 0.014 / 0.014 as the paper does.
- **Text around the new row.** "On three of the later runs the true label raised QWK by 0.029 to 0.046"
  still holds with the row added (its QWK interval spans 0); "Equivalence … is established only for
  Gemini" refers to the first four models and holds.
- **Release file diff** (`1.0.0.yaml`): wording on HARMOGEN-R (now "in this release", four instructors
  at QWK 0.981, and 0.942 on the open half) agrees with the article's 5.1 (L937, L944); the provenance
  block's authors and contributors. No invocation changed. The 0.981 and 0.942 cannot be recomputed
  here (HARMOGEN-R not on disk; its analysis is in the unpublished harness), and were not changed in
  the article since 4a5c0f8.
- **Code package diff**: `strip_dumps.py` gains `--skip-missing-corpus` (used by R1); the two READMEs
  above; `SHA256SUMS` lists their new hashes, and P2 confirms them.

## 6. Skipped, and why

- **Nothing in `reproduce.py` was skipped**: all four public corpora were on disk and hashed as the
  release states.
- **Model calls**: none sent; the harness is not published (REPRODUCE.md says so).
- **Analyses that run in the unpublished TypeScript harness** (e.g. `harmogen-reanalysis`,
  `jorgpt-agreement`, `sampling_sd.ts`, `mohler_ceiling_draw.mts`): not runnable from the release; their
  published outputs were not regenerated. HARMOGEN-R is also not on this machine.
- **Fable 5.1 agent bookkeeping**: not published; its statistics were recomputed by the RQ5 notebook.

## 7. Notes, not counted as mismatches

- **O1. The notebooks write bytecode into `code/`.** After the notebooks ran, the copied `code/` held
  `shared/__pycache__/seeds.cpython-311.pyc` and
  `studies/measurement/grader-label-compounding/__pycache__/compounding.cpython-311.pyc` (timestamps
  match the notebook run; `reproduce.py` itself sets `PYTHONDONTWRITEBYTECODE` and works on a copy). No
  listed file changes and `sha256sum -c` is unaffected, but a reader's `diff` against a fresh package
  would show them. Fix I would make: have the preamble's import helper set
  `sys.dont_write_bytecode = True` before importing from `code_dir()`.
- **O2. Timing and the `--quick` wording.** REPRODUCE.md says "about ten minutes" and `rq6-matching`
  "about six minutes"; here the full run took 16.6 minutes and `rq6-matching` 406 s on 4 CPUs.
  `reproduce.py`'s docstring says `--quick` skips "the three slow steps (about 8 minutes between
  them)", but only two steps are flagged slow (`rq4-loop`, `rq6-matching`; 502 s here). Fix: "the two
  slow steps", and quote the times as machine-dependent.
- **O3. `strip_dumps.py verify` on rebuilt dumps** fails on the first ASAP 2.0 file rather than
  accepting `per-case-dumps.rebuilt.sha256` as `label-dose` does. It is documented behaviour and no
  output depends on it; accepting the rebuilt hashes in `verify` would make it usable on a reader's
  rebuild.
- **O4. Thread setting for `ref-ceilings`.** The release says to run `robustness.py` single-threaded
  "as elsewhere"; `reproduce.py` runs it at default. Both give identical bytes (S23, X3), so nothing
  is wrong; aligning the two texts would remove a question a reader might ask.
- **O5. Section 9 table** names one or two steps per row rather than every step (`rq2-pooling`,
  `rq2-learners`, `rq2-dose-posthoc`, `rq2-calibration-arms`, `rq6-label-check`, `ref-ceilings-posthoc`
  are not named there). REPRODUCE.md's step table names them all. A wording matter, not an error.

## 8. Summary

- **reproduce.py**: 25 of 25 steps MATCH, byte for byte, confirmed independently file by file
  (24 JSON outputs, one per analysis step, plus 12 figures); 0 skipped, 0 failed.
- **Release-stated invocations not in reproduce.py**: selftest, floor, single-threaded ceilings, the
  history restore and the default-thread group analysis all byte-identical; the spot re-run gives the
  release's −0.143 [−0.267, −0.023]; the single-threaded group analysis differs by the documented ulp.
- **Notebooks**: 6 of 6 pass.
- **corrections-18**: all five values (12.6×, 11.8×, 5.9 to 12.6, 0.38 SD, 0.014) recomputed from the
  regenerated outputs with sign, MATCH; the new accuracy-table row MATCH.
- **Package**: `--check` current (117 files); `SHA256SUMS` matches all 117 files, 15 only after their
  embargo line is removed, as REPRODUCE.md states.
- **Count.**
  - **Reproduced: 44** rows classed MATCH: section 1, 2 (P1, R3); section 2, 25 (S1–S25); section 3,
    5 (X1–X3, X5, X7); section 4, 6 notebooks; section 5, 6 (C1–C6).
  - **Explained: 5** (P2, R2, R4, X4, X6).
  - **Unexplained mismatches: 0.**
  - Notes: 5 (O1–O5), none affecting a published number.

```yaml
reproduction: {date: 2026-10-15, by: agent, report: reproduction-13.md, unexplained_mismatches: 0, audited_commit: de01e5f807c632fe46492333fcda27bdc19030e0}
```
