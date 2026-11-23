# Scope audit 6: knowledge-tracing-benchmark-2026 1.0.0

Date 2026-11-21. Independent verification auditor (Claude Opus 5.5, agent), with no part in the analyses, the draft,
the release, any correction pass or the earlier audits. Audited commit: 0bf31a1cef185d4dfdc9b42e052d193b0a18e004
(origin/main at the time of the audit), which contains the last headline correction
a76e058468245255a0803ca2f1bd4f8d7ce585dc (`git merge-base --is-ancestor`: yes; `readiness.yaml`
`last_headline_correction_commit` names it). Scope, as briefed: (1) every finding and note of scope audit 5 against
corrections-6; (2) the diff 044355d7b..0bf31a1ce on the article, the release file, the rivals README and the report;
(3) the headline places in full; (4) the commits the release file's tables and figures analyses name. Out of scope:
the AI-use section, the conflict-of-interest section, the registration-extract question and the masking of models this release does not report.

## What was checked, and how

- **The diff.** `git diff --stat 044355d7b 0bf31a1ce` restricted to `research/`, `studies/models/`, `board/` and
  `shared/` touches nine files: the article (18 lines), corrections-6, `readiness.yaml`, scope audit 5, the report,
  the release file (19 lines), the code package's `SHA256SUMS` and its copy of the rivals README, and the rivals
  README. No analysis code, provenance file, notebook, figure, per-case file or `out/tables.json` changed. Every
  changed sentence was read in its paragraph against `out/tables.json` (`regimes`, `status`, `summary`) and Tables 4,
  5 and 7.
- **Numbers.** No printed number changed in corrections-6; the new qualifiers carry only "2%" and "20". The numbers
  standing in the touched sentences were recomputed from unrounded `tables.json` values, rounded once, signs
  checked (losses are −`minus_main`): logistic 20-answer KDD 0.126079–0.186005 (0.126 to 0.186), recurrent
  0.147594–0.205273 (0.148 to 0.205), attention 0.106341–0.113886 (0.106 to 0.114), BKT 0.047124 and 0.059219
  (0.047, 0.059), IRT 0.180362 and 0.181693 (0.180, 0.182); EDM Cup 20-answer over 11 models 0.016586–0.067168
  (0.017 to 0.067); HawkesKT 0.065276 on EDM Cup and 0.045517 on half A (0.065, 0.046). All match.
- **Report and package.** `python3 board/render_report.py --release knowledge-tracing-benchmark-2026 --check`: the
  committed report is current. `python3 board/package_code.py --release knowledge-tracing-benchmark-2026 --check`:
  current (12 files). The report's diff carries exactly the article's changed sentences (plus the input digests); the
  embedded per-case download decompresses to the same SHA-256 before and after (3436512d…, equal to the published
  per-case file).
- **Commits the analyses name (item 4).** `git archive` of 4aa7c512e36a7f57355e0c2e209bdb7dc24e8b07 (the rivals
  folder, `shared/`, and the per-case file) into scratch, laid out as the release directory (`code/` beside
  `per-case-outputs.jsonl`); the archived per-case file is byte-identical to the one at the audited commit. Running
  the recorded invocations from `code/studies/models/state-estimator-benchmark/rivals/`: `python3 tables.py
  --per-case ../../../../../per-case-outputs.jsonl` wrote an `out/tables.json` byte-identical (cmp) to the committed
  `studies/.../rivals/out/tables.json` and to the code package's copy; `python3 figures.py` ("printed values match:
  Table 5 (13 models), Table 7 (38 rows)") wrote `fig1-main-auc.png/.svg` and `fig2-thinning.png/.svg`, each
  byte-identical to the committed figures under `research/article/figures/` and to the package's copies. No commit
  after 4aa7c512e touches `tables.py`, `figures.py`, `shared/figstyle.py` (last changed at 01254e553, an ancestor of
  4aa7c512e) or the per-case file. The per-case analysis still names 903826eb9; `collect.py` last changed at
  3ea0b9c2c, so the header comment's account ("the collector has not changed since corrections-2") is true, as are
  its statements that corrections-3 and -4 changed no analysis code and that corrections-5 changed `tables.py` and
  `figures.py` (`git log` on each file: tables 750ec39f1, 3ea0b9c2c, 4aa7c512e; figures 750ec39f1, 4aa7c512e).
- **Descriptive floors counted as passes.** None in the headline places, the RQ answers, section 5.2, Table 4's
  caption, the discussion, section 7.4, the release `interpretation` or the rivals README. The only "PASS" beside
  PFA in the article is its gate row (Table 3), which is a gate, not a floor.
- **Product mentions.** A case-insensitive search for the product's name across the article and its provenance,
  notebooks and report directory, the release folder (release file, code package, per-case README) and the rivals
  folder: no match.
- **Precedence.** Corrections-6 added no comparative claim about the literature; the hedges noted by scope audit 5
  ("cited here", "found here") are unchanged. No overclaim.

## Scope audit 5's findings and notes against corrections-6

| id | corrections-6 says | verified | new error? |
|---|---|---|---|
| F1 | Qualifier "the logistic models' and BKT's numbers are descriptive only" added to the conclusion, discussion, section 5.4, release `interpretation` and rivals README; conclusion scoped "on the two Cognitive Tutor corpora" | Present in all five places. `status`: PFA and BKT `FLOOR DESCRIPTIVE` on both KDD corpora, the three Best-LR models `NO FLOOR RUN`; attention and recurrent models `PASS` there, so the qualifier reaches only descriptive numbers. The added scope is needed and correct: on EDM Cup PFA lost 0.037181 at 20 answers against AKT 0.051151 and simpleKT 0.067168, so the unscoped sentence was false there. On KDD the smallest logistic loss (0.126) exceeds the largest attention loss (0.114) and BKT's (0.059). Fixed. | None. The discussion's added scope "on the KDD corpora" also covers the recurrent models, which is required (on EDM Cup DKT 0.050561 and IEKT 0.051111 against AKT 0.051151); the recurrent minimum on KDD (0.148) exceeds the attention maximum (0.114). |
| F2 | `analyses[tables]` and `analyses[figures]` name 4aa7c512e; header comment rewritten | Both name 4aa7c512e36a7f57355e0c2e209bdb7dc24e8b07; recorded invocations at that commit reproduce `out/tables.json` and all four figure files byte for byte (above). Header comment true. Fixed. | None. |
| N1 | Section 7.4 names the six models | "every number of the three Best-LR models, PFA, BKT and the running proportion is therefore descriptive only"; matches the paragraph's first sentence and `status`. Fixed. | None. |
| N2 | Subtitle "six with a planted-effect floor that counts" | The six deep models; HawkesKT's floor counts and missed. Consistent with abstract ("The six deep models were given a floor"), RQ2 answer, conclusion and `interpretation`. Fixed. | None. |
| N3 | No change; PDF title kept | Accepted. | n/a |
| N4 | Discussion "a condition of counting any model's numbers" | Present; true under section 4.5's rule. Fixed. | None. |
| N5 | Section 5.4 "every model fitted there except HawkesKT lost less from the cut than on either KDD corpus" | Checked per model (EDM Cup against half A and bridge06): IRT 0.060 v 0.182/0.180; PFA 0.037 v 0.141/0.126; Best-LR 0.066 v 0.171/0.186; Best-LR (1,000 iterations) 0.065 v 0.170/0.185; Best-LR with time windows 0.065 v 0.171/0.173; BKT 0.017 v 0.047/0.059; DKT 0.051 v 0.158/0.160; AKT 0.051 v 0.110/0.114; simpleKT 0.067 v 0.106/0.107; IEKT 0.051 v 0.148/0.156. HawkesKT 0.065 against 0.046 on half A is the exception. The running proportion (zero change everywhere) fits nothing and is outside "the eleven models fitted there". Fixed. | None. |
| N6 | 2% qualifier "most of these numbers have no floor at that size" in subtitle, conclusion, `interpretation`, discussion, README | Present in all five. Count against `status` `f1_2`: of the 18 KDD 2% cells of the recurrent, logistic and attention models, 4 have a passed 2% floor (IEKT, LPKT, AKT, simpleKT on half A), 1 missed (DKT on half A), 13 have none; adding BKT's three cells (none) keeps "most" true for the conclusion and `interpretation`. Fixed. | None (see note N1 below on placement). |

## Headline places (item 3)

Subtitle, abstract, the four RQ answers, the conclusion and the release `interpretation` were read in full and
against each other and Tables 3 to 7. They agree on: nine gated models all reproduced (three after a correction);
six deep models given a counted floor, HawkesKT missing on both KDD corpora at 25% and DKT on half A at 2%; AKT then
simpleKT highest on every corpus (half A 0.8148, 0.8128; bridge06 0.8149, 0.8148; EDM Cup 0.8381, 0.8364), with the
lead over IEKT device-sensitive on half A and EDM Cup; at 2% on the KDD corpora recurrent (0.138 to 0.184) above
logistic (0.063 to 0.100) and attention (0.083 to 0.095), BKT least on every corpus (0.030 to 0.057), with most of
those numbers unfloored; at 20 answers logistic above attention and BKT on the KDD corpora, the logistic and BKT
numbers descriptive. No descriptive floor is counted as a pass and no product is named.

## Findings

| id | location | what | status |
|---|---|---|---|
| N1 | Discussion, end of the paragraph on published tables | "most of the 2% numbers have no floor at that size" follows the 20-answer sentence, one sentence after the 2% comparison it qualifies. The referent is clear from "2%", but placing it after "... about as much as the Best-LR models" (as in the conclusion) would read more directly. | note |
| N2 | Release `interpretation` | Says the five-of-six floor result "at 25% of the training learners" and that PFA's, BKT's and the running proportion's floors are descriptive, but not that the Best-LR models had no floor or that DKT missed at 2% on half A (both in the abstract). Every statement made is true and scoped; the closing qualifier "the logistic models' and BKT's numbers are descriptive only" is supported by section 7.4 rather than by anything earlier in the `interpretation`. Pre-existing apart from the qualifier. | note |

Open findings: 0. Notes: 2. Overclaims of precedence: 0.

## Closing lines for readiness.yaml

```yaml
scope_audit: {date: 2026-11-21, by: agent, report: scope-audit-6.md, open_findings: 0, audited_commit: 0bf31a1cef185d4dfdc9b42e052d193b0a18e004}
precedence: {date: 2026-11-21, by: agent, report: scope-audit-6.md, overclaimed_open: 0, audited_commit: 0bf31a1cef185d4dfdc9b42e052d193b0a18e004}
```
