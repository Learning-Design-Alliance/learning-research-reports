# Reproduction 4: knowledge-tracing-benchmark-2026 1.0.0

Independent reproduction by an agent with no part in the analyses, the draft, the release, any correction pass,
any audit, or reproductions 1 to 3. Date 2026-11-21. Audited commit
`0bf31a1cef185d4dfdc9b42e052d193b0a18e004` (`origin/main`, checked out in a worktree). The last headline
correction `a76e058468245255a0803ca2f1bd4f8d7ce585dc` and reproduction 3's audited commit `319c3bd97` are both
ancestors of it (`git merge-base --is-ancestor`, exit 0 for each).

The reader steps worked from `git archive` of
`research/wiki/research/releases/knowledge-tracing-benchmark-2026/` at the audited commit, extracted to scratch
(23 files), and nothing else from the repository, except the article text (which step 7 checks numbers against)
and the steps marked "repository". Python 3.13.18, matplotlib 3.11.2. Scratch peaked under 5 MB and was deleted.

## Results

| step | check | result |
|---|---|---|
| 1 | `cd code && sha256sum -c SHA256SUMS` on the extracted release | 12 of 12 OK, exit 0 |
| 1 | `per-case-outputs.jsonl` against the release file | SHA-256 `3436512d...1c61`, 966,074 bytes, 2,731 lines: as recorded. Unchanged since `319c3bd97` (no diff) |
| 2 | rebuild of the per-case file | the release says it is rebuilt only in the repository (`per-case` analysis). Repository: from `studies/models/state-estimator-benchmark/rivals/`, `python3 collect.py verify --out ../../../../research/wiki/research/releases/knowledge-tracing-benchmark-2026/per-case-outputs.jsonl` as recorded: `verify: IDENTICAL`, exit 0 |
| 3 | `python3 reproduce.py --list`; `python3 reproduce.py` | `tables MATCH`, `figures MATCH`, exit 0 |
| 3 | `tables`, as recorded, from a copy of the release: from `code/studies/models/state-estimator-benchmark/rivals/`, `python3 tables.py --per-case ../../../../../per-case-outputs.jsonl`, after deleting `out/tables.json` | exit 0; `out/tables.json` byte-identical to the published copy |
| 3 | `figures`, as recorded: `python3 figures.py`, after deleting the four figure files | exit 0; prints "printed values match: Table 5 (13 models), Table 7 (38 rows)"; `fig1-main-auc.png`, `fig1-main-auc.svg`, `fig2-thinning.png`, `fig2-thinning.svg` byte-identical |
| 3 | `diff -r` of the run copy's `code/` against the published `code/` | identical except `shared/__pycache__/` left by the figure run (bytecode, not an output) |
| 3 | `benchmark-fits` | SKIPPED: the harness is not in the package and the corpora (KDD Cup 2010, EDM Cup 2023) are not on this machine |
| 4 | the commit the `tables` and `figures` analyses name, `4aa7c512e36a7f57355e0c2e209bdb7dc24e8b07`: `git archive` of `studies/models/state-estimator-benchmark/rivals`, `shared` and the figure folder, to scratch | `tables.py`, `figures.py`, `collect.py`, `shared/figstyle.py`, `out/tables.json` and the figures at that commit have the same SHA-256 as the packaged files |
| 4 | run at `4aa7c512e`: `tables.py --per-case <release per-case file>` and `figures.py`, after deleting their outputs | exit 0 both; `out/tables.json` and all four figure files byte-identical to the copies in `code/`. So the named commit is the code that produced the committed outputs |
| 4 | repository: `python3 board/package_code.py --release knowledge-tracing-benchmark-2026 --check` | "current (12 files)" |
| 5 (M1) | reproduction 1's M1, re-run: `sha256sum -c` on the shipped `code/` (README carries the embargo marker) | 12 of 12 OK, including `rivals/README.md`; also 12 of 12 OK on the code/ inside the report's zip. M1 does not recur |
| 5 (M2) | reproduction 1's M2, re-run: the report's "Download the release" zip (`knowledge-tracing-benchmark-2026-reproduce.zip`, 338,113 bytes, decoded from `research/reports/knowledge-tracing-benchmark-2026/index.html`) | 23 files; `diff -r` against the release directory finds no difference, `code-manifest.txt` and the current `1.0.0.yaml` included. `python3 board/render_report.py --release knowledge-tracing-benchmark-2026 --check` (repository): "report ... is current". M2 does not recur |
| 5 | the report's other downloads | `per-case-outputs.jsonl.gz` decompresses to bytes identical to the release's file; the four notebook downloads are byte-identical to the release's `notebooks/` |
| 6 | each downloaded notebook in its own empty folder with only `per-case-outputs.jsonl`, `RELEASE_DIR` unset, executed with nbclient | rq1-gates (4 code cells), rq2-floor, rq3-prediction, rq4-thinning (3 each): all run to the end, every assertion holding |
| 6 | rq2-floor in an empty folder with only `per-case-outputs.jsonl.gz` | runs to the end (it unpacked the file beside itself) |
| 6 | rq1-gates in an empty folder with no data file | stops at the first data cell with `FileNotFoundError: Could not find per-case-outputs.jsonl (or per-case-outputs.jsonl.gz)`, saying where to get it and naming `RELEASE_DIR` |
| 7 | independent recomputation (below) | 853 checks, 0 mismatches; no value at a rounding half-boundary |
| 8 | unexplained mismatches | 0 |

## Step 7: the numbers changed since `319c3bd97`

What changed between `319c3bd97` and the audited commit (`git diff`): the article (subtitle, abstract, sections
4.2, 4.5, 5.2 to 5.4, 6, 7.2, 7.4, 8, 9, references), the release file (analysis commits, `research_design`,
`interpretation`, `limitations`), `tables.py` (PFA, BKT and the running proportion read FLOOR DESCRIPTIVE),
`figures.py` (a label and the docstring), `out/tables.json` (eight status values, PASS to FLOOR DESCRIPTIVE), both
figures, both READMEs and three notebooks. The per-case file did not change, so no measured value changed: what
changed is which numbers count, and the counts built on that.

A script of my own (standard library; it imports nothing from `code/`) read the per-case file, parsed Tables 4 to 7
out of the article's Markdown, recomputed every cell from unrounded values, rounded once, and compared the strings
(U+2212 minus, `+` sign and bold included). It derived each model's status independently: IRT the reference; PFA,
BKT and the running proportion "floor descriptive" wherever a 25% floor record exists for them (the maintainer's
rule, R0597); otherwise "pass" or "not read" from the 25% floor record, or "no floor run" without one.

- **Table 4.** All 34 floor cells (value and interval), "not run"/"not fitted" exactly where no record is, the bold
  on exactly the three cells failing the stated rule, each record's PASS/MISS agreeing with the rule, G_N's interval
  below zero in every cell, and "(descriptive)" on exactly the PFA, BKT and running-proportion rows.
- **Counts and their signs.** Models with a floor: the six deep models, plus PFA, BKT and the running proportion
  on the KDD corpora only (none on EDM Cup; none for the Best-LR models; no 2% floor on bridge06, as section 7.4
  says). "Five of the six deep models" pass at 25% on every corpus where run: DKT, AKT, simpleKT, IEKT, LPKT;
  HawkesKT misses on both KDD corpora (−0.0481, −0.0460, negative, against bars 0.0063 and 0.0085) and passes on
  EDM Cup; DKT misses at 2% on half A (−0.0008, interval covering zero); every other 2% floor passes. PFA's, BKT's
  and the running proportion's floor statistics lie above the bar with intervals above zero on both KDD corpora
  (section 5.2's new sentence). Nine gated models, all passing; thirteen models. Subtitle, abstract, Answer to RQ2,
  section 6 ("every other deep model"), conclusion and the release's `interpretation` state these counts and agree.
- **Table 5.** All 38 cells (mean, lowest and highest fold), bold on AKT on each corpus, and the status column
  for all 13 rows against my derived statuses and against `tables.json` (all 38 statuses equal).
- **Section 5.3's changed sentence.** Leaving out IRT and HawkesKT, the lowest means on both KDD corpora are the
  running proportion's, 0.7306 and 0.7356; IRT 0.7261, 0.7438, 0.7438.
- **Table 6.** All 38 log losses (unchanged, rechecked).
- **Table 7.** All 190 changes, from unrounded means, with 5 fits per cell (25 for 10% and 2%); "(not read)" on
  exactly HawkesKT's two KDD rows; "not read (floor)" on DKT's half A 2% cell, whose 2% floor missed. The caption's
  list of counted 2% cells (AKT, simpleKT, IEKT, LPKT on half A; DKT, AKT, simpleKT, IEKT, HawkesKT on EDM Cup)
  equals the set with a passing 2% floor and a counted model.
- **"Most of these numbers have no floor at that size"** (subtitle, abstract, section 5.4, 6, conclusion,
  interpretation): of the 21 cells the abstract's 2% sentence reads (recurrent, logistic and attention models on the
  two KDD corpora, BKT on all three), 4 have a counting 2% floor; of all 38 2% cells, 9. True on either reading.
- **2% and 20-answer ranges, with signs** (abstract, 5.4, RQ4 answer, conclusion): recurrent 0.138 to 0.184,
  logistic 0.063 to 0.100, attention 0.083 to 0.095, BKT 0.030 to 0.057 and least on every corpus (all losses,
  i.e. negative changes); every recurrent 2% loss on the KDD corpora larger than every logistic and attention loss.
  With 20 answers: logistic 0.126 to 0.186, recurrent 0.148 to 0.205, attention 0.106 to 0.114, BKT 0.047 and
  0.059; on each KDD corpus every logistic loss is larger than every attention and BKT loss.
- **Section 5.4's changed EDM Cup sentence** ("every model fitted there except HawkesKT lost less from the cut than
  on either KDD corpus"): holds for every learning model fitted on EDM Cup other than HawkesKT, at both 20 and 50
  answers; HawkesKT lost more on EDM Cup (0.065) than on half A (0.046), which is why it is excepted. The eleven
  learning models fitted there lost 0.017 to 0.067.
- **Unchanged numbers inside changed sentences**: PFA +0.0161 against 0.741; bars 0.0063, 0.0085, 0.0065.

## Skipped

- `benchmark-fits`: the harness is not published and the corpora are not on this machine. Skipped, not failed.
- The SHA-256 of the corpus files: no corpus is on this machine.

## Mismatches

None. One discrepancy arose in my own script (it expected Table 5's status column for LPKT, fitted on two corpora,
as "pass" rather than the printed "pass; pass"); the value is the same on both corpora, so it was a formatting
assumption of the script, fixed before the count above.

## Note for the scope audit (not a mismatch)

- Section 5.4: "On EDM Cup, every model fitted there except HawkesKT lost less from the cut than on either KDD
  corpus". The running proportion is fitted there and its change is exactly 0.000 on every corpus (Table 7), so it
  did not lose less. The sentence after it ("the eleven models fitted there") excludes it, and the 319c3bd97 wording
  ("whose KDD numbers are read") already included it; no printed number is affected. Adding "that learns" (or
  "except HawkesKT and the running proportion") would make it exact.

reproduction: {date: 2026-11-21, by: agent, report: reproduction-4.md, unexplained_mismatches: 0, audited_commit: 0bf31a1cef185d4dfdc9b42e052d193b0a18e004}
