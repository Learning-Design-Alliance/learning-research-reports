# Scope audit 35: corrections-19 (Paper II) and corrections-34 (Paper VI), 1.0.1

This is an independent scope audit, made on 2026-10-20 by an agent with no part in the work. It
audits commit `779fb65cf8984497e0a58417c8f9cc50e4a1e065` (head of `claude/bold-ptolemy-6odavp`) and
covers both releases: learning-graph-budget-2026 (II) and ai-grader-reliability-2026 (VI).

Method:
- Read scope-audit-34, corrections-19 (II) and corrections-34 (VI), and the whole of
  `git diff ddb1efc 779fb65`.
- Parsed both 1.0.1 release files and VI's `readiness.yaml` with `yaml.safe_load`.
- Checked the dates that replaced the record names against `corrections-1.md` and
  `corrections-4.md`. Each record's own date line and its git add commit were both used.
- Checked the named environment variables against `order_variation.py`, both at HEAD and at the
  release's pinned commit `ceed51a`.
- Diffed both HTML reports between ddb1efc and 779fb65. Base64 runs of 400 or more characters were
  stripped and entities unescaped before the diff. The embedded payloads were compared by hash, and
  the files inside II's reproduce bundle were compared one by one.
- Re-ran scope-audit-34's scan over every text file in `publish_set(release, "1.0.1")`. The scan
  excluded code/, readiness/, protocol/, artifacts/ and the embargo marker line. The report was
  included, so the readiness.yaml text it renders was scanned too. Every repository-path hit was
  resolved against the publish set's sources, its destinations and its `code/` paths.

## Scope-audit-34's open findings

1. CLOSED. Paper VI, the specialist-review claims. `readiness.yaml:59-61` and the rebuilt
   `research/reports/ai-grader-reliability-2026/index.html` ("Specialist reviews requested") now read:
   - "'with Pearson r flat' restated 2026-10-06"
   - "with Gwet AC2 0.858 / 0.887 beside them since a correction of 2026-10-06"
   - "Restated 2026-10-06, and again the same day at the known reliability"

   The dates are right:
   - corrections-1 is dated 2026-10-06 (git add 2558e65, 2026-10-06). Its H9 row is the "Pearson
     r flat" restatement, and its H13 and H15 rows restate the fairness claim.
   - corrections-4 is dated 2026-10-06 (git add d210462, 2026-10-06, later the same day). It added
     AC2 0.858 / 0.887 (line 32 and its §4.6 and §5.1 rows) and the known-reliability fairness
     wording (rows 2 to 20). "Again the same day" is therefore true.

   The fourth change, "adjudicated (established in a correction of 2026-10-06)" at :61, is in a
   `note:` field. The report does not render that field, and none of the note text appears in it.

   No "corrections-N" is left in the report outside the "Audits, reproductions and corrections"
   table, which is an accepted exclusion. readiness.yaml:54 still says "(corrections-19,
   scope-audit-20 note AA)", but it sits in `pending_links.then`, which the report does not render.

   The report's text diff is these three list items plus the records-table rows. All 16 embedded
   base64 payloads, the per-case download among them, are byte-identical.

2. CLOSED. Paper II, `1.0.1.yaml:2922-2924`. order-variation-estimator now reads "Environment
   variables: EDNET_ZIP, EDNET_CONTENTS, ASSIST_DIR, EEDI_ANSWERS, EEDI_ZIP, DS1275_DIR, JUNYI_DIR."
   These are exactly the `data_path(...)` variables that `order_variation.py` reads:
   - EDNET_ZIP and EDNET_CONTENTS at :704
   - EEDI_ANSWERS and EEDI_ZIP at :708
   - ASSIST_DIR at :712
   - DS1275_DIR at :717
   - JUNYI_DIR at :736

   The list is the same at the release's pinned commit `ceed51a`. No other variable is read apart
   from thread-count settings (:260-261). The header comment at :1486-1488 is now true of this
   analysis. The YAML parses.

## New findings

1. NOTE. `git diff ddb1efc 779fb65` changed nothing else of substance. Outside the two fixes above,
   the diff touches only the following:
   - corrections-18 and -33: the tally now reads "nine DataShop notes ... two more", which closes
     scope-audit-34 note 4.
   - The new corrections-19 (II) and corrections-34 (VI). They have the same content.
   - scope-audit-34 itself.
   - II's report. Its only changes are `report-inputs-sha256` and the reproduce bundle, and the only
     file that changed inside the bundle is `learning-graph-budget-2026/1.0.1.yaml`.
   - The records-table rows in both reports.

   No number, hash, date, commit or verdict changed. The two edits replace only record names, with
   dates that are correct.

2. NOTE. Both reports, "Audits, reproductions and corrections" table: VI line 4954 (inside the
   single long line) and II line 6770. The newest rows, "Corrections 34" (VI) and "Corrections 19"
   (II), again sort first with an empty Added cell, because each record was rendered in the same
   commit that added it. Scope-audit-34 note 4 explains this, and the rows fix themselves at the next
   rebuild. Corrections 33 (VI) and 18 (II) now show 2026-10-20 in date order. The table is otherwise
   the accepted exclusion of scope-audit-34 note 3.

3. NOTE. VI, `readiness.yaml:60` (rendered in the report). The text "Restated 2026-10-06; was: no
   accuracy gain; 'with Pearson r flat' restated 2026-10-06" states the same date twice. It is
   true but redundant, and is cosmetic only.

4. NOTE. Regression sweep. No new pointer to an unpublished file or internal record was found in
   either publish set. Every record-name hit (corrections-N, scope-audit-N, reproduction-N,
   records-N) is inside the records table. The only "recorded there" is II's article :1144 and the
   same text in the report, which scope-audit-34 note 6 accepted (it refers to the release file named
   at :1141). The repository-path hits that do not resolve to a shipped file are all on scope-audit-34
   note 6's accepted list:
   - the held-back VI `code:`/`lockfile:` paths (:377 to :659, :1192 to :1201)
   - the figure output paths (II :1220, :2271, :2300; VI :1231)
   - VI's per-case `ref` (:322)
   - deposit-internal paths (`src/18~19.zip` to `src/21~22.zip`, `data/cleaned-oe-00001.parquet`,
     `data/metadata/subject_metadata.csv`, `src/contrib/Archive/CDM/`)
   - `module.attribute` references to shipped modules
   - `learning-research-reports scripts/mint_doi.py` (VI :1783, :1787)
   - the notebooks' `studies/.../out/result.json` placeholder

   One hit was not on that list: II `notebooks/rq2-reliability.ipynb:217` (and the same text in the
   report), `studies/measurement/reliability/out/raise_kappa_curve_{c}.json`. This is an f-string, and
   both files it expands to (`_xes3g5m`, `_ednet`) are in `code-manifest.txt`. The changed text since
   ddb1efc contains no new "there".

5. NOTE. Mechanical checks, all with exit 0 checked directly:
   - Both 1.0.1 release files and VI's readiness.yaml parse with `yaml.safe_load`.
   - `python3 board/patent_gate.py --stamps`: 331 of 331 stamped before this file was added.
   - `python3 board/package_code.py --release learning-graph-budget-2026 --check`: current (459
     files).
   - `--release ai-grader-reliability-2026 --check`: current (120 files).
   - `python3 board/render_report.py --release <r> --check`: both current at 779fb65.

   Adding this record to VI's readiness folder may make VI's report stale, because its records table
   lists the folder. If so, the next rebuild is the drafting agent's to make, not this audit's.

Open findings: 0
