# Reproduction: learning-graph-budget-2026 1.0.0 (Paper II), 2026-10-14, follow-up

**Status: complete.** 28 steps reported (the scope below, plus two prerequisites and one check). The run
took about 3.5 hours (2026-10-14 11:24 to 14:52 UTC). This file was written as the run proceeded and
committed after each group of steps.

This is a follow-up of `reproduction-2026-10-13.md` (which reproduced `b40b0e9`), narrow by design: it
reruns every step whose code, invocation, inputs or published output changed between `b40b0e9` and the
audited commit, and every step that reproduction found mismatched or could not run for a packaging reason.

## Independence

The reproducer is an agent with no part in the analyses, the draft, the release, any correction pass, or
the earlier audits and reproductions. It worked from a copy of the release directory alone
(`research/wiki/research/releases/learning-graph-budget-2026/`: `1.0.0.yaml`, `REPRODUCE.md`,
`reproduce.py`, `code/`), copied to its scratch folder, not from the studies' working copies, and wrote
only this file.

- **Date:** 2026-10-14 (run started 11:24 UTC).
- **Commit reproduced:** `0db370283f6cbc4ccf34745007753f2edae2aadd` (HEAD of `origin/main` after
  `git fetch origin main`; this file is on branch `audit/repro-2026-10-14`, made from it).
- **Ancestry:** `readiness.yaml` gives `cooling_off.last_headline_correction: 2026-10-14` and
  `last_headline_correction_commit: 5e74d15b4bac1b617be1a0ee56ed8b44c7713435`;
  `git merge-base --is-ancestor 5e74d15b… 0db3702…` holds (exit 0).
- **Machine:** 4-core cloud container shared with other jobs, 15 GB RAM, no GPU; at most two processes
  were run at once.
- **Environment:** Python 3.11.15; numpy 2.4.6 (scipy-openblas 0.3.31, DYNAMIC_ARCH, Haswell), scipy
  1.17.1, pandas 3.0.6; PyYAML and markdown-it-py for the release file and the report build. No thread
  variable was set except where a step declares one, and for the filter re-check steps (below).

## How it was run

`reproduce.py` was not run as a single invocation. A small wrapper in the reproducer's scratch folder (not
part of the release) imports the copied `reproduce.py` and uses each step's command, working directory,
environment, clean list, compare mode and `same()` unchanged. It differs from `reproduce.py`'s own loop
only in that it (1) makes the working copy of `code/` once and keeps it; (2) records each outcome as soon
as the step ends; (3) refuses to compare a declared output whose modification time did not change
(NOT-REWRITTEN), since the working copy starts with the published file; (4) lets two lanes share the
working copy, each step claimed by one lane; and (5) applies, only where this file says so, an extra
environment setting or a dropped need. Before the run, every file of the copied `code/` was checked
against `code/SHA256SUMS`: 400 match as they are and 59 (`.md`, `.txt`) match once the embargo-marker
line is removed, which is how `package_code.py` says the sums are taken; none differs.

Corpora were read through symlinks from a scratch folder laid out as the registry lays out
`$LDA_SCRATCH_DIR` (`xes3g5m/`, `eedi/`, `ednet/contents`, `datashop/prod/`, `ds1275`, `ds576`, `junyi`,
the ASSISTments files at its root), so that every folder a step writes into is the reproducer's own:
`EDMCUP_DIR` (into which `rq3-edmcup-prep` writes `cells.tsv`) held symlinks to the seven official CSVs
and no `cells.tsv`; the reverse-reinforcement cache (`$LDA_SCRATCH_DIR/../reverse-reinforcement-related`)
and `s2-tmp/` landed in scratch. Variables: `LDA_SCRATCH_DIR`, `XES_DIR`, `ASSIST_DIR`, `EDMCUP_DIR`,
`EDNET_ZIP`, `EDNET_CONTENTS`, `EEDI_ZIP`, `EEDI_ANSWERS`, `DATASHOP_DIR`, `DS1275_DIR`, `DS576_DIR`,
`JUNYI_DIR`. Not set, because the corpus is not on this machine: `SLAM_DIR` (Duolingo SLAM was deleted),
`JUNYI2020_DIR`, `MOOCCUBEX_DIR`, `ECPE_DIR`, `LT_C6_XLSX`.

## Input hashes

Every input the steps below read was hashed (SHA-256 and MD5) before use and compared with `1.0.0.yaml`
(`datasets:`: the top-level `sha256` and the hashes its notes give).

| Corpus | Files | Result |
| --- | --- | --- |
| ASSISTments 2012–13 | `assist2012.zip`, `assist_slim.csv`, `assist_rich.csv`, `assist_skill_names.csv` | SHA-256 match the release (`7bb18f93…`, `f767f919…`, `ba01682f…`, `8bea8bad…`); MD5s match the notes |
| EDM Cup 2023 | `assignment_details.csv`, `assignment_relationships.csv`, `unit_test_scores.csv`, `problem_details.csv` | SHA-256 match the release (`2285c714…`, `155adb03…`, `227f248f…`, `4f45daf2…`) |
| | `sequence_details.csv`, `sequence_relationships.csv`, `explanation_details.csv` | no SHA-256 in the release (its note defers to the registry); MD5 `f9adb10c…`, `74b5fb6d…`, `76c5a0cf…` recorded here |
| | `cells.tsv`, rebuilt by `rq3-edmcup-prep` from the files above | SHA-256 `c98a1a0d…65e4`, MD5 `a579b4d8a46fed1028c2aa963fb14bba`: equal to the release note |
| EdNet KT1 | `ednet-kt1.zip`, `ednet-content.zip`, `contents/questions.csv` | SHA-256 match the release (`0d13933f…`, `aa910a04…`, `137d2936…`) |
| XES3G5M | `XES3G5M.tar.gz`, `attempts.tsv`, `cid2route.json`, `metadata/questions.json` | SHA-256 match the release (`62d145bd…`, `46ff6268…`, `e928d81b…`, `57a3a63e…`) |
| Eedi | `data.zip`, `answers.tsv` | SHA-256 match the release (`c7f01672…`, `24442463…`) |
| DataShop | ds580, ds671, ds649, ds669, ds1530, ds1531, ds1706, ds495, ds576, ds1190, ds1275 'All Data' exports | SHA-256 match the release (11 of 11) |
| Junyi 2015 | exercise table, problem-log sample | SHA-256 match the release (`13292cc2…`, `e8bea912…`) |
| Coherence Map | `code/studies/producers/pipeline/data/coherence-map.json` (now in the package) | SHA-256 `49fa041e…`: equal to the release's `coherence-map` dataset |
| Duolingo SLAM 2018 | — | **absent** (deleted from this machine) |
| XES3G5M interactivity ratings | `code/studies/measurement/difficulty-sources/build/ratings.json` (now in the package) | SHA-256 `a06407f6…`, the file the 2026-10-13 reproducer supplied; still not declared in `datasets:` |

No file under `external/` was written by this run. Two changed during it, neither written by any step
here: `pisa2022/` (another session's download) and `.data-access.json` (a registry-aware access log;
the code package ships no registry, so its `shared/fetch.touch_env` cannot write it, and the corpora
were read here through the reproducer's own symlink folder).

## Scope

`git diff b40b0e9 0db3702 --stat -- studies/ research/wiki/research/releases/learning-graph-budget-2026/`
lists, besides `1.0.0.yaml` (the Z7 removals, the `--floor-reps 30` record and the planning analysis
note), `REPRODUCE.md`, `code-manifest.txt` and `code/SHA256SUMS`: `coarse.py` and `coarse.json`
(+ `coarse-single-draw.json`, new); `assist2012-direction/out/direction.json`;
`order-swap-remnant/planning_abs.py`, `planning-abs.json` and its README (new); `empty-cell/README.md`
(text only); and two packaged inputs, `coherence-map.json` and `ratings.json`. `reproduce.py` moves
`rq3-edmcup-prep` first, records `--floor-reps 30` for `rq1-conjunctive-ability` and adds
`rq3-planning-abs`. Steps run, so: every step whose code, invocation, inputs or published output changed
(`rq3-edmcup-prep`, `rq3-planning-abs`, `rq2-coarse`, `rq1-conjunctive-ability`, `rq3-assist-direction`,
the six `rq1-revrel-*`, the eight filter re-check steps that read `ratings.json` or were found stale);
every step the 2026-10-13 run found mismatched (the same, plus `rq4-filter-compare`); every step that
reads EDM Cup's `cells.tsv` (`rq1-atlas`, `rq1-empty-cell*`, `rq1-lag-bands`; and `rq3-edmcup-direction`
as a check); and `rq1-reverse-skeleton`, which the `rq1-revrel-*` steps turn out to need (below). Not in
scope and not rerun: the other 2026-10-13 MISMATCH steps, which `corrections-8.md` leaves as recorded and
whose code and outputs did not change: `rq5-holon-floor-*` (they read MOOCCubeX, absent here) and
`rq2-raise-kappa` / `-rescore`. Their explained mismatches stand as recorded on 2026-10-13.

## Steps

Verdicts: MATCH (byte for byte, or under the step's declared compare mode); ROUNDING (the file differs,
but only in floating-point digits, run-time fields, field order or added fields, so that no reported
value and no printed number changes); MISMATCH (a real difference, with its cause); NOT RUN (absent
corpus). Every step ran with the step's own command and environment; the filter re-check steps also
ran with `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`, as the study's README and the
docstring's CHANGE 1 say they were run ("the same machine and thread count (1)"); `reproduce.py` does not
set it for them.

| Step | RQ | Reproduces (`--list`) | Verdict | Detail |
| --- | --- | --- | --- | --- |
| `rq3-edmcup-prep` | RQ3 | EDM Cup: rebuild cells.tsv from the official files (writes to EDMCUP_DIR) | MATCH | Now the first step. Declares no output; exit 0, 17 s. The rebuilt `cells.tsv` has SHA-256 `c98a1a0d…65e4` and MD5 `a579b4d8…`, equal to the release note; it was in place before every RQ1 step below |
| `rq3-planning-abs` | RQ3 | Table 16: planning values at a drop of 0.10 in accuracy (derived from power.json) | MATCH | New step. 1 file identical under `bytes`; exit 0 (its assertion that the 0.10 SD values equal the stored ones held) |
| `rq1-conjunctive-ability` | RQ1 | the XES3G5M interactions stratified by ability (PARTIAL) | MATCH | Now declared with `--floor-reps 30`. 1 file identical under `bytes`; exit 0, 103 s. The 2026-10-13 mismatch is resolved |
| `rq1-empty-cell-floor` | RQ1 | where pairs go undecided: the floor (ten worlds) | MATCH | 1 file identical under `bytes`; exit 0, 16 s |
| `rq1-empty-cell-junyi` | RQ1 | Table 1: Junyi at its exercises | MATCH | 2 files identical under `bytes`; exit 0, 3 s |
| `rq2-coarse` | RQ2 | groups of skills against random groupings | MATCH | `coarse.py` CHANGE 1. 1 file identical under `bytes`; exit 0, 638 s, under this process's own (unfixed) string-hash seed. By reading: the group sizes are now taken in sorted label order, and the other set iterations (`set(ga) & set(gb)`) only pair values that a rank correlation treats symmetrically, so no hash-seed dependence remains. The 2026-10-13 mismatch is resolved |
| `rq1-atlas` | RQ1 | Table 1: the positivity atlas, every corpus but ASSISTments and SLAM | MATCH | 1 file identical under `rows`; exit 0, 875 s, reading the rebuilt `cells.tsv` (EDM Cup row identical). Rows come out in discovery order, as `REPRODUCE.md` says; put in the published order they are byte-identical to the published file but for its final newline |
| `rq1-empty-cell` | RQ1 | Table 1: the labels per corpus (the funnel step below compares the file) | NOT RUN (absent corpus: SLAM) | Needs `SLAM_DIR`, so `reproduce.py` skips it here. Run as a diagnostic with `SLAM_DIR` pointed at an empty folder: exit 0, 1,121 s; the three SLAM courses are recorded as skipped (`generator raised StopIteration`), every other corpus is read. Its output is compared through the funnel step |
| `rq1-empty-cell-funnel` | RQ1 | Table 1: the verdict funnel and the ability check | NOT RUN (absent corpus: SLAM) | Same diagnostic: exit 0, 577 s. Against the published `result.json`: every non-SLAM corpus entry (13 corpora, funnel included) and `grades` are identical; the differences are only the three SLAM entries (skipped here) and the cross-corpus fields that include them (`C1`, `C1_table1` lists, `C3`, `V2`). With the three published SLAM entries put back and the cross-corpus fields recomputed by `real()`'s own rules, the file is byte-identical to the published one. So the EDM Cup row, which the 2026-10-13 notes showed could silently go missing, reproduces once `cells.tsv` is built first; the SLAM row could not be checked here |
| `rq1-lag-bands` | RQ1 | Table 2: the drop by lag band (LAG-DEPENDENT) | MATCH | 1 file identical under `bytes`; exit 0, 500 s, reading the rebuilt `cells.tsv` |
| `rq1-reverse-skeleton` | RQ1 | reverse reinforcement: pairs, controls and cases (outcomes sealed) | MATCH | Not in scope by diff; run because the `rq1-revrel-*` steps read its cache (below). 1 file identical under `bytes`; exit 0, 391 s |
| `rq1-revrel-skeleton` | RQ1 | related pairs: sets, controls and cases (outcomes sealed) | MATCH | With the coherence map now in `code/`, no file had to be supplied. **First attempt FAILED** (exit 1 after 442 s, `FileNotFoundError: …/reverse-reinforcement/skeleton_R.npz`): its reproduction check loads the parent study's sealed skeleton from the parent's cache (`$LDA_SCRATCH_DIR/../reverse-reinforcement`), which only `rq1-reverse-skeleton` writes, and the step does not list it. `reproduce.py`'s full order runs the parent first, so a full run is unaffected; a narrow `--only rq1-revrel` run fails. After `rq1-reverse-skeleton`: 1 file identical under `bytes`; exit 0, 332 s |
| `rq1-revrel-positivity` | RQ1 | related pairs: positivity and control size | MATCH | 1 file identical; exit 0, 1 s (first attempt failed with the skeleton) |
| `rq1-revrel-floor-l1` | RQ1 | related pairs: floor, same strand | MATCH | Declares no output; exit 0, 520 s. The five floor parts it writes (`out/floor_parts/L1/*.json`) were rewritten and are identical to the published ones |
| `rq1-revrel-floor-cm` | RQ1 | related pairs: floor, Common Core progressions | MATCH | Declares no output; exit 0, 457 s; the five `out/floor_parts/CM/*.json` rewritten and identical |
| `rq1-revrel-assemble` | RQ1 | related pairs: floor assembled | MATCH | 1 file identical; exit 0, 1 s. (`1.0.0.yaml` writes the invocation `assemble --set S`, `S` standing for a set name; `reproduce.py` runs `--set L1`) |
| `rq1-revrel` | RQ1 | related pairs: same strand NOT B-SPECIFIC; progressions NO REVERSE EFFECT | MATCH | 1 file identical; exit 0, 28 s. The 2026-10-13 packaging failure (coherence map missing) is resolved |
| `rq3-assist-direction` | RQ3 | Table 8: Common Core grade order on ASSISTments (NOT RECOVERED) | MISMATCH | `out/direction.json` is **byte-identical** to the republished file (exit 0, 6,268 s): the corrections-8 rerun on the hashed extract reproduces, and the hand-added note is gone. `out/skill_ccss_map.json` differs in three fields only: `assistments_name` of skills 40, 92 and 365 carries a trailing space in the published file ("Circumference ", "Pattern Finding ", "Interpreting Coordinate Graphs ") and none here. Cause, established: the hashed `assist_skill_names.csv` (`8bea8bad…`) has no trailing space on those rows (checked); the published map was last written at `dcb4b9c` from an older names file, as the 2026-10-13 run found, and was not republished with `direction.json`. Every CCSS code and every number is identical; nothing printed depends on the name field |
| `rq3-edmcup-direction` | RQ3 | Table 8: EDM Cup grade, module and lesson order | MATCH | Check only (code unchanged; reads `cells.tsv`). 1 file identical; exit 0, 43 s |
| `rq4-filter-gs-xes` | RQ4 | filter re-check: graph-state on xes with moment matching | MATCH | One BLAS thread: 1 file identical under `bytes`; exit 0, 3,062 s. The published record (with `R2_passes` false, as it reads) is exactly what the declared code writes at one thread. The 2026-10-13 mismatch (run at the machine's default thread count) is explained by the thread count, as `corrections-8.md` records |
| `rq4-filter-gs-assist` | RQ4 | filter re-check: graph-state on assist with moment matching | MISMATCH | One BLAS thread; exit 0, 1,047 s. Every number identical, `R1_C0_logloss_diff` 2.83e-5 and `R2_passes` false included. Two fields differ: the rerun adds `reproduction.R1_CLIM_logloss_diff` (0.0) and sets `R1_passes` true; the published record lacks the first and has `R1_passes` false. Cause, established: the published record was written before CHANGE 1 redefined R1 (counts and CLIM's log loss, not C0's); the packaged script writes the new R1, and `filter_recheck.py compare` recomputes CHANGE 1's R1 for records written before it ("recomputed for records written before it"), getting the same true and 0.0. No printed number or verdict changes |
| `rq4-filter-gs-lap-xes` | RQ4 | filter re-check: gs-lap on xes | MATCH | One BLAS thread: 1 file identical; exit 0, 3,486 s |
| `rq4-filter-gs-lap-assist` | RQ4 | filter re-check: gs-lap on assist | MATCH | One BLAS thread: 1 file identical; exit 0, 979 s |
| `rq4-filter-s2-xes` | RQ4 | filter re-check: s2 on xes | MATCH | One BLAS thread, reading the now-packaged `ratings.json` (no file supplied): 1 file identical; exit 0, 710 s |
| `rq4-filter-s2-assist` | RQ4 | filter re-check: s2 on assist | MISMATCH | One BLAS thread; exit 0, 791 s. Same two fields and the same cause as `rq4-filter-gs-assist`: rerun adds `R1_CLIM_logloss_diff` 0.0 and `R1_passes` true; published lacks the first and has false (record written before CHANGE 1). Every number identical (`R1_C0_logloss_diff` 2.8308482114103306e-05 included), as the 2026-10-13 run's one-thread diagnostic found |
| `rq4-filter-s2-lap-xes` | RQ4 | filter re-check: s2-lap on xes | MATCH | One BLAS thread, `ratings.json` from the package: 1 file identical; exit 0, 569 s |
| `rq4-filter-s2-lap-assist` | RQ4 | filter re-check: s2-lap on assist | MATCH | One BLAS thread: 1 file identical; exit 0, 589 s |
| `rq4-filter-compare` | RQ4 | filter re-check: every headline and its rule (reads committed outputs) | ROUNDING | Recomputed from the twelve records (eight regenerated here, the four Eedi ones as published). Every value identical (0 differing fields); the bytes differ only in the order of two keys in `reproduction.gs-assist` and `reproduction.s2-assist` (`R1_CLIM_logloss_diff` before `R1_passes`), because those two regenerated records already carry the field that `compare` otherwise appends. Follows from the two records above; no separate cause |

Tally over the 28 steps: 22 MATCH (including the `rq1-reverse-skeleton` prerequisite and the
`rq3-edmcup-direction` check), 1 ROUNDING, 3 MISMATCH (all explained), 2 NOT RUN (SLAM absent; run as
diagnostics, every non-SLAM output reproduced).

## Headline numbers

**Method.** `board/render_report.py --no-notebooks` was run in a scratch tree: copies of `board/`,
`research/`, `docs/` and `data/` at `0db3702`, with `studies/` and `shared/` pointing at the regenerated
working copy of `code/`. Steps not rerun here leave their published outputs in place. Three changes were
made in that scratch tree only: (1) the renderer records every mismatch instead of stopping at the first,
and writes each check (printed text, what the source gives, file and field) and each block's heading with
its linked and unlinked numbers to a JSON dump; (2) the regenerated `atlas.json` rows, equal to the
published rows as a set, were put in the published order, since provenance indexes them by position;
(3) `empty-cell/out/result.json` is the regenerated file with the three published SLAM entries put back
(above), since SLAM cannot be read here. The committed report was not touched. The same instrumented
build on the published outputs gives the same result (1,686 checks, 0 mismatches), so the instrument
reads both.

**Result.** 1,686 provenance-linked numbers were recomputed (1,624 of the 1,749 decimal numbers the
renderer counts in the Abstract, the results and the Conclusion). All 1,686 give the printed value with
its sign. Integer cells, which the provenance files do not link, were checked by a separate script
against the regenerated outputs.

| Part of the paper | Numbers checked | Result |
| --- | --- | --- |
| Abstract | 22 linked numbers; 0.10 and 0.001 by hand (`shared/edge_state.CLAIMED_EFFECT` = 0.10; `e2e.BEATS` = 0.001, the margin `kc_tree.py` uses) | all reproduce with sign, the Common Core excess +0.0117 included |
| Answers to RQ1–RQ5 | 62 linked numbers; 0.10 and 0.001 by hand. Not checked: section numbers (2.4, 6.5), the 5% and 1% of RQ5, and RQ2's 90 skills, 20 worlds and 500 to 32,000 learners, which come from steps outside this scope | all reproduce with sign |
| Table 1 | 13 linked decimals (decided shares, background drops); by script, all 56 integer cells and the seven "surviving ability" cells against regenerated `atlas.json`, `positivity-assist.json` (unchanged), `empty-cell/out/result.json` and `junyi-exercise.json` | all reproduce. The SLAM row is checked against published `atlas-slam.json` and the published SLAM entries only, so it is not a reproduction here |
| Table 8 | 22 linked numbers (excesses, intervals, noise, planted gate, verdict words); the five "Pairs" integers by script (1,426, 472, 5, 54, 71) | all reproduce with sign, from the byte-identical regenerated `direction.json` files |
| Table 16 | not linked; every cell by script against regenerated `planning-abs.json` (291 to 385, 1,570; 241 to 319, 1,301; 49 to 64, 260; 42 to 55, 222; 129 to 170, 693; 495 to 655 and 99 to 131, 2,673 and 535); the caption's 0.20 to 0.23 SD from its `d_sd` fields; the ICCs 0.096 and 0.395 from `power.json` and `icc-power.json` | all reproduce |
| Section 5.2, the coarse paragraph | 24 linked numbers (0.478; 0.455, 0.530, 0.564; random means 0.436, 0.442, 0.477; the 2.5–97.5 percentile ranges; gaps +0.020, +0.089, +0.088; 100% and 98% of draws; 547 against 454 and 153 against 79 group pairs; 0.80); by hand 8 splits, cell floor 5, 53 and 425 groups, 50 draws | all reproduce with sign from the regenerated `coarse.json`. The gaps are computed from unrounded values (0.530148 − 0.441505 = +0.0886, printed +0.089, not 0.530 − 0.442) |
| Conclusion | 1 linked number (0.075) | reproduces |

No headline number moves. Abstract and Section 5.3's +0.0117 [+0.0054, +0.0181] (`corrections-8.md`)
and Section 5.2's 50-draw control reproduce from the release.

## Notes on the run

- **The filter re-check needs one BLAS thread, and `reproduce.py` does not say so.** At one thread, six
  of the eight XES3G5M and ASSISTments records are byte-identical to the published ones and the other two
  differ only in the R1 flag (above). The 2026-10-13 run, at the machine's default thread count, found
  all eight to differ in numbers. The release file's `filter-recheck` environment and the eight steps in
  `reproduce.py` declare no thread setting; the study's docstring and README do. Fix: add
  `env={"OMP_NUM_THREADS": "1"}` (and the OpenBLAS and MKL variables) to those steps, as `rq3-remnant`
  has, and say so in `1.0.0.yaml`. The published records' own `R2_passes` false (graph-state's records
  were written at another thread count) is as CHANGE 1 describes: R2 is reported, not gated.
- **`rq1-revrel-skeleton` depends on `rq1-reverse-skeleton`'s cache**, which neither its `needs` nor
  `REPRODUCE.md` say. A full `reproduce.py` run is unaffected (the parent comes first); `--only rq1-revrel`
  fails at once. Fix: say so in the step, or have the related study fail with a message naming the
  parent step.
- **`ratings.json` is now packaged but not declared** in `datasets:` (the 2026-10-13 fix asked for both).
  The coherence map is packaged and its hash matches its declared dataset.
- **`skill_ccss_map.json` was not republished** with `direction.json`: three skill names keep the trailing
  space of an older names file. Cosmetic (no code reads the name), but the declared invocation does not
  regenerate the published file byte for byte.
- **SLAM.** The SLAM rows of Table 1 and SLAM's entries in `empty-cell/out/result.json` could not be
  reproduced on this machine. Run without SLAM, `empty_cell.py` exits 0 and records the three courses as
  skipped, the same silent-skip behaviour the 2026-10-13 run reported for EDM Cup; `reproduce.py` itself
  skips both steps when `SLAM_DIR` is unset, so a reader is not misled.
- **A reader's note on the coarse control.** `coarse.json` has two "random" values per level: the RANDOM
  grain rows (Spearman-Brown of the split-half correlations averaged over draws and splits: 0.436, 0.442,
  0.478) and the comparison rows (mean of the draws' Spearman-Brown: 0.436, 0.442, 0.477). The verdict
  rule and the paper use the second, as CHANGE 1 says; at L4 the two round differently (0.478 against
  0.477). Not a reproduction finding.

## Summary

- **28 steps:** 22 MATCH (including the `rq3-edmcup-direction` check and the `rq1-reverse-skeleton`
  prerequisite), 1 ROUNDING (`rq4-filter-compare`, key order only), 3 MISMATCH, 2 NOT RUN (SLAM absent:
  `rq1-empty-cell`, `rq1-empty-cell-funnel`; run as diagnostics, every non-SLAM output identical and the
  file byte-identical once the published SLAM entries are restored).
- **Resolved since 2026-10-13:** `rq2-coarse` (now deterministic), `rq1-conjunctive-ability` (invocation),
  the six `rq1-revrel-*` (coherence map packaged), `rq4-filter-s2-xes` / `-s2-lap-xes` (`ratings.json`
  packaged), the EDM Cup step order, `rq3-assist-direction`'s `direction.json` (republished on the hashed
  extract), and six of the eight stale filter records, which match at one thread.
- **Unexplained mismatches: 0.** The three mismatches have established causes and change no printed
  number or verdict: `rq3-assist-direction`'s `skill_ccss_map.json` (three trailing spaces from an older
  names file; the map was not republished) and `rq4-filter-gs-assist` / `rq4-filter-s2-assist` (records
  written before CHANGE 1 redefined R1; every number identical).
- **Headline check:** every number in the Abstract, the RQ answers, Tables 1, 8 and 16, Section 5.2's
  coarse paragraph and the Conclusion recomputes from the regenerated outputs with its sign, except Table
  1's SLAM row, which could not be regenerated here.

```yaml
reproduction: {date: 2026-10-14, by: agent, report: reproduction-2026-10-14.md, unexplained_mismatches: 0, audited_commit: 0db370283f6cbc4ccf34745007753f2edae2aadd, scope: follow-up of reproduction-2026-10-13.md}
```
