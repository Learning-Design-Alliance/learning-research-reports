# Reproduction 4: checklist-grading-2026 1.0.0, after corrections-4 and corrections-5

**Independence.** Reproducer: an agent with no part in the analyses, the draft, the release, any
corrections round, or the earlier reproductions and scope audits of release `checklist-grading-2026`. No
model was called. Nothing in the article, the release, the code package, the studies or
`readiness.yaml` was edited; this file is the only one written.

- **Date:** 2026-11-06.
- **Audited commit:** `98e9e1d3b0e395bf626e5a8698d96cdd909c4b27` (branch `claude/blissful-fermat-jeqm05`).
  The worktree branch was reset to that commit before any check; `git rev-parse HEAD` printed it, and the
  tree was clean. It contains every corrections-5 commit (`d638061` … `7c35805`) and the AI-use commit.
- **Environment:** Linux 6.18.44, Python 3.13.17, numpy 2.5.3, matplotlib 3.11.2, `jupyter execute`.
- **Scratch:** only `research/wiki/research/releases/checklist-grading-2026/` was copied, twice, to a
  scratch folder outside the repository: one copy for `reproduce.py`, one for the invocations as
  written (compared against the untouched release directory in the worktree). The notebooks ran in
  three further folders, each holding only the notebook and the per-case file. All scratch was deleted
  at the end. No tracked file was changed by any step (`git status` clean before the commit).
- **Read first:** `CLAUDE.md`, `.claude/skills/release-pipeline/SKILL.md`, `reproduction-3.md` (at
  `c1b5bdb`, 0 unexplained), `corrections-5.md`.

## 1. Data record

| check | release file (`datasets[per-case-model-outputs]`) | measured | result |
| --- | --- | --- | --- |
| SHA-256 | `b4051c6c…77775f26c` | `b4051c6c18f2b84e822cd38eedae7e349e6e18599f2b9043dbe7cca77775f26c` | MATCH |
| lines (`rows`) | 12000 | 12000 | MATCH |
| `size_bytes` | 3471904 | 3471904 | MATCH |

The line composition matches the data dictionary: 1 study, 66 question, 957 item and 10,976 grade lines.

## 2. Steps

### 2.1 `reproduce.py` (all five steps, both floors)

`python3 reproduce.py` in the copied release folder, exit 0, 4 min 8 s wall time:

| step | reproduces | result |
| --- | --- | --- |
| `rq12-analyse` | Tables 1, 2, 4; Figures 1, 2, 4 values | MATCH |
| `floor` | registered floor (§4.6, A.2) | MATCH (`seconds` ignored, as documented) |
| `rq23-mechanism` | Tables 3, 5; Figures 3, 5 values | MATCH |
| `mechanism-floor` | follow-up floor | MATCH |
| `figures` | Figures 1–5 | MATCH (byte-identical PNGs on this machine) |

### 2.2 The release file's `analyses[].code.invocation`, exactly as written

Each was run verbatim (`cd code && python3 …`) from the root of a second copy of the release
directory, and every declared output was compared byte for byte with the published copy:

| analysis id | output | result |
| --- | --- | --- |
| `grader-boolean-rubrics` (`--analyse`) | `out/results.json` | MATCH (byte-identical), exit 0 |
| `grader-boolean-rubrics-floor` (`--floor`) | `out/floor.json` | MATCH: the only differing line is `"seconds": 206` against the published `198`, the runtime field the release file and `REPRODUCE.md` declare and exclude; exit 0 |
| `grader-checklist-defects` | `out/results.json` | MATCH (byte-identical), exit 0 |
| `grader-checklist-defects-floor` (`--floor`) | `out/floor.json` | MATCH (byte-identical), exit 0 |
| `figures` | `checklist-fig1-reliability.png` … `checklist-fig5-check-types.png` | MATCH (all five byte-identical), exit 0 |

`diff -rq` of the whole copied `code/` against the published one found no other changed file.

### 2.3 Code package and report

- `python3 board/package_code.py --release checklist-grading-2026 --check`: "code package for
  checklist-grading-2026 is current (21 files)", exit 0. MATCH.
- `python3 board/render_report.py --release checklist-grading-2026 --out /tmp/claude-0/repro-report`,
  exit 0. Summary line: **"270 numbers checked and linked (270 of 299 in abstract, results and
  conclusion); 3 notebooks executed; 0 interactive figures; 0 reviews requested; Readiness fails (2
  open)"**. The build recomputes every provenance-linked number from its source and fails on a
  mismatch, so all 270 linked numbers recompute. The sidebar breaks coverage down as abstract 10 of 11,
  results 260 of 288, conclusion 0 of 0; I checked the 29 unlinked numbers by hand below. The rebuilt
  `index.html` is byte-identical to the committed `research/reports/checklist-grading-2026/index.html`,
  so the committed report is current. "Readiness fails (2 open)" is the readiness gate's status at this
  commit, not a reproduction mismatch (the gate still waits for this record and the scope audit of
  corrections-5).
- Notebooks: `rq1-reliability`, `rq2-validity` and `rq3-defects` from `notebooks/`, each run with
  `jupyter execute` in an empty folder holding only it and the per-case file: all exit 0 (their asserts
  of the printed point estimates pass). Without the data file, `rq1-reliability` stops with a clear
  `FileNotFoundError` naming the file and `RELEASE_DIR`. MATCH.

### 2.4 Independent recomputation

To check that the published scripts compute what the article says they compute (and not only that
they reproduce themselves), I wrote a separate script reading only the per-case file. It recomputed,
from the definitions in §4.6 and Appendix A.1: the four Mohler H and R values, dH (−0.1062), dR
(−0.0113), the cross-model X (0.8849 / 0.9058), the raters' r (0.6212); the three band rows of Table 3
(e.g. MID n 145, G −0.1778); Table 4's D and C for both defects; and Table 5's E and P for all 120
false-sentence answers (−0.1091, −0.0626) and the 112 key-term answers (+0.0029, +0.3456), with D = E + P.
Every value agrees with `results.json` to the fourth decimal. From the per-case file I also confirmed:
10,976 gradings, 0 errors, 5,488 per model each served by the requested model; 46 of 544 GPT-5.4 mini
checklist calls on programs unparsed, on 45 submissions, plus 1 Gemini Likert call, so 46 submissions
dropped and 226 kept; 0 unparsed short-answer calls; 62 questions, 284 checks, 3–7 per question, 8
no-error checks, all also error checks; program checklists 12/12/10/10 (= 44); 620 answers over 62
questions in the main draw; 73 of 272 programs truncated; 3 or 4 raters per program dimension; 120
high (h ≥ 4.5) and 120 low (h ≤ 2.5) answers, at most 3 per question; 120/120 and 112/120 manipulation
passes; neutral/treatment length ratio per pair 0.84–1.12 (false) and 0.81–1.18 (key terms), all inside
0.75–1.33, and ratio of mean lengths 0.963 and 0.968.

## 3. Printed numbers

Each printed number was checked against the regenerated (byte-identical) outputs, rounded once from
the unrounded value, with its sign. Sources: P = `grader-boolean-rubrics/out/results.json`, F = its
`floor.json` (and `floor-rev0.json` for revision 0), M = `grader-checklist-defects/out/results.json`,
K = `checklists.json`, T = `perturb.json`, C = the per-case file (§2.4).

### Abstract

| printed | source | unrounded | result |
| --- | --- | --- | --- |
| 620 short answers; 272 assignments (226 usable); three or four graders | C, P | 620; 272; 226; 3–4 | MATCH |
| consistency 0.96–0.99 | P `mohler.stats.R.*` | 0.9614–0.9871 | MATCH |
| checklist r 0.68 and 0.69 | P `V.gpt.boolean`, `V.gemini.boolean` | 0.6820, 0.6883 | MATCH |
| Likert r 0.76 and 0.82 | P `V.gemini.likert`, `V.gpt.likert` | 0.7638, 0.8189 | MATCH |
| false sentence: 47% Likert, 17% checklist | P `contra_manip_pass.stats.D` | −0.4733, −0.1717 | MATCH (signs stated in words: "lowered") |
| key terms: 35% checklist, 27% Likert | P `stuff_manip_pass.stats.D` | +0.3485, +0.2732 | MATCH ("raised") |
| three of the four dimensions | P Table 2 | CE, Readability, Documentation weak or negative | MATCH |

### §4 Method

| printed | source | unrounded | result |
| --- | --- | --- | --- |
| §4.2 1,721 answers to 62 questions | dataset note; `boolean.py` docstring | not recomputable from the release (needs the corpus) | not checked (no release output) |
| §4.2 620 over 62; r 0.621 [0.546, 0.689] | P `mohler.ceiling.r_rater1_rater2` | 0.6212 [0.5464, 0.6890] | MATCH |
| §4.2 272 submissions; 73 shortened | C; P `menagerie.truncated` | 272; 73 | MATCH |
| §4.3 284 checks over 62 questions (3–7); 10–12 per dimension | K; C | 284; 3–7; 10–12 | MATCH |
| §4.3 eight no-error checks, all error checks | K `with_no_error_check`; C | 8; subset true | MATCH |
| §4.4 10,976 gradings, none failed | P `calls`, `failed` | 10976, 0 | MATCH |
| §4.4 46 of 544 (8.5%), 45 submissions; 1 Gemini Likert; 226 of 272 | C; P `unparsed` 47 | 46/544 = 0.0846; 45; 1; 226 | MATCH |
| §4.5 120 high (≥ 4.5), 120 low (≤ 2.5), ≤ 3 per question | C | as printed | MATCH |
| §4.5 0.963 and 0.968; within 0.75–1.33 | T `mean_ratio`; C | 0.9630, 0.9684; 0.81–1.18 | MATCH |
| §4.5 120/120 and 112/120 passed | T `manip_pass` | 120, 112 | MATCH |
| §4.6 margins ±0.05, ±0.03 | `boolean.py` docstring | as printed | MATCH |
| §4.6 22.5% and 23.5% | F `reported_not_gated … GRID retest` | 0.225, 0.235 | MATCH |
| §4.6 ±0.10 found 56–58%; up to about 0.15 | F `menagerie V±0.10` | 0.56, 0.58 | MATCH |
| §4.6 0.08 found 95–97% | F `mohler_Vplus/Vminus.validity` | 0.97, 0.95 | MATCH |

### §5.1 and Table 1 (all 50 cells)

| row | printed | unrounded (P) | result |
| --- | --- | --- | --- |
| Mohler | 0.987 / 0.961; 0.962 / 0.965; −0.011 [−0.023, −0.001] LIKERT-MORE-RELIABLE; 0.885 / 0.906; +0.021 [−0.022, +0.067] UNRESOLVED | 0.98711/0.96137; 0.96159/0.96474; −0.01129 [−0.02346, −0.00116]; 0.88495/0.90582; +0.02087 [−0.02189, +0.06669] | MATCH |
| Correctness | 0.707 / 0.596; 0.663 / 0.426; −0.174 [−0.280, −0.063] LIKERT-MORE-RELIABLE; −0.164 / −0.159; +0.006 [−0.163, +0.143] UNRESOLVED | 0.70718/0.59572; 0.66315/0.42625; −0.17418 [−0.28033, −0.06280]; −0.16423/−0.15863; +0.00560 [−0.16304, +0.14296] | MATCH |
| Code Elegance | 0.830 / 0.655; 0.673 / 0.562; −0.143 [−0.364, +0.016] UNRESOLVED; 0.577 / 0.223; −0.354 [−0.486, −0.200] LIKERT-MORE-RELIABLE | 0.82977/0.65486; 0.67343/0.56204; −0.14315 [−0.36403, +0.01644]; 0.57741/0.22304; −0.35437 [−0.48647, −0.19987] | MATCH |
| Readability | 0.832 / 0.747; 0.745 / 0.445; −0.192 [−0.429, −0.076] LIKERT-MORE-RELIABLE; 0.586 / 0.019; −0.567 [−0.675, −0.428] LIKERT-MORE-RELIABLE | 0.83233/0.74732; 0.74463/0.44479; −0.19243 [−0.42895, −0.07614]; 0.58569/0.01870; −0.56699 [−0.67545, −0.42802] | MATCH |
| Documentation | 0.684 / 0.650; 0.451 / 0.285; −0.100 [−0.224, +0.017] UNRESOLVED; 0.231 / 0.212; −0.019 [−0.187, +0.152] UNRESOLVED | 0.68383/0.64979; 0.45050/0.28477; −0.09989 [−0.22409, +0.01711]; 0.23057/0.21203; −0.01854 [−0.18714, +0.15167] | MATCH |
| caption n | 620, 226 | P `n` | MATCH |

§5.1 prose: 0.96 to 0.99; lower by 0.011; inside ±0.03; Gemini −0.026 LIKERT-MORE-RELIABLE (−0.02574);
GPT +0.003 EQUIVALENT (+0.00316); 0.885, 0.906, +0.021; programs 0.17 to 0.57 (the four clear
differences −0.174, −0.192, −0.354, −0.567); GPT −0.237 (−0.23690) and −0.300 (−0.29984); Gemini
checklist means 0.990 and 0.994, SDs 0.05 and 0.03 over all 272 (`post_hoc_all_parsed.gemini.boolean`:
0.99004/0.04908, 0.99449/0.03072, n 272); ICC 0.803, 0.889, 0.865 (0.80253, 0.88900, 0.86458); 27% and
5% (0.2711, 0.0528). All MATCH.

### §5.2 and Table 2 (all 35 cells)

| row | printed | unrounded (P) | result |
| --- | --- | --- | --- |
| Mohler | 620; 0.764 / 0.688; 0.819 / 0.682; −0.106 [−0.165, −0.048] LIKERT-MORE-VALID; 0.621 | 0.76376/0.68834; 0.81894/0.68204; −0.10616 [−0.16515, −0.04750]; 0.62124 | MATCH |
| Correctness | 226; 0.405 / 0.433; −0.173 / −0.054; +0.073 [−0.008, +0.150] UNRESOLVED; 0.622 | 0.40531/0.43344; −0.17253/−0.05409; +0.07328 [−0.00846, +0.15042]; 0.62217 | MATCH |
| Code Elegance | 0.035 / 0.017; −0.182 / −0.137; +0.013 [−0.075, +0.092] UNRESOLVED; 0.539 | 0.03461/0.01659; −0.18176/−0.13739; +0.01317 [−0.07537, +0.09216]; 0.53854 | MATCH |
| Readability | 0.039 / −0.007; −0.235 / −0.011; +0.089 [−0.043, +0.189] UNRESOLVED; 0.571 | 0.03944/−0.00748; −0.23506/−0.01073; +0.08870 [−0.04306, +0.18887]; 0.57107 | MATCH |
| Documentation | 0.286 / 0.079; −0.284 / −0.125; −0.024 [−0.109, +0.050] UNRESOLVED; 0.525 | 0.28587/0.07874; −0.28377/−0.12516; −0.02426 [−0.10876, +0.05016]; 0.52531 | MATCH |

The rename dV → dH did not move any number: every dH cell is `stats.dV` of the same corpus/dimension,
and the "human ceiling" column is `ceiling.r_rater1_rater2` / `r_one_rater_vs_mean_of_others`, as
before; the verdict strings are `verdicts.validity`.

§5.2 prose: by 0.075 (Gemini, −0.07543) and 0.137 (GPT, −0.13690); one rater at a time Likert 0.594 to
0.819 (0.5944, 0.7532, 0.6198, 0.8187), above 0.621 in two of four, level at 0.620 (0.6198); checklist
0.526 to 0.675 (0.5264 … 0.6754); repeated at 0.96 or above; Gemini −0.007 to 0.286 on the three
dimensions, only the 0.286 interval excludes zero (0.190 to 0.368; Gemini's other five intervals include
zero); GPT negative on every dimension in both formats, significant only for Likert on Readability
(−0.235, −0.408 to −0.004) and Documentation (−0.284, −0.453 to −0.045); Gemini 0.405 and 0.433 on
Correctness; GPT Readability +0.224 (+0.078 to +0.340, verdict BOOLEAN-MORE-VALID); Gemini Documentation
−0.207 (−0.319 to −0.069, LIKERT-MORE-VALID); raters' r with length 0.40 to 0.53 (0.3961 … 0.5292); GPT
−0.14 to −0.50 (−0.1398 … −0.4988). All MATCH.

### Table 3 and §5.2 band prose (all 15 cells)

| band | printed | unrounded (M `bands`) | result |
| --- | --- | --- | --- |
| LOW | 65; −0.144 [−0.216, −0.065]; −0.123 [−0.215, −0.023]; +0.022 [−0.071, +0.120] UNRESOLVED | −0.14423 [−0.21585, −0.06507]; −0.12255 [−0.21462, −0.02306]; +0.02168 [−0.07071, +0.12006] | MATCH |
| MID | 145; −0.149 [−0.210, −0.091]; −0.327 [−0.386, −0.265]; −0.178 [−0.234, −0.120] CHECKLIST-LOWER | −0.14914 [−0.20968, −0.09126]; −0.32698 [−0.38592, −0.26520]; −0.17784 [−0.23402, −0.11986] | MATCH |
| HIGH | 410; −0.049 [−0.065, −0.034]; −0.160 [−0.194, −0.127]; −0.111 [−0.143, −0.081] CHECKLIST-LOWER | −0.04872 [−0.06519, −0.03398]; −0.16003 [−0.19428, −0.12695]; −0.11131 [−0.14329, −0.08057] | MATCH |

Prose: +0.022, over-credit up to 0.12, 0.178 more (MID), 0.111 more (HIGH), "largest in the middle band".
MATCH.

### §5.3, Table 4 and Table 5

| printed | unrounded | result |
| --- | --- | --- |
| Table 4 false: 120; −0.473 [−0.514, −0.431]; −0.172 [−0.223, −0.124]; +0.302 [+0.255, +0.348] CHECKLIST-BLIND-TO-CONTRADICTION | P `contra_manip_pass`: −0.47333 [−0.51411, −0.43101]; −0.17169 [−0.22300, −0.12381]; +0.30165 [+0.25522, +0.34808] | MATCH |
| Table 4 key terms: 112; +0.273 [+0.220, +0.325]; +0.348 [+0.283, +0.410]; +0.075 [+0.014, +0.136] CHECKLIST-REWARDS-STUFFING | P `stuff_manip_pass`: +0.27321 [+0.21990, +0.32521]; +0.34845 [+0.28297, +0.40994]; +0.07524 [+0.01442, +0.13596] | MATCH |
| 0.473 Likert, 0.172 checklist; 0.361 (Gemini), 0.243 (GPT) smaller | C.gemini +0.36055, C.gpt +0.24275 | MATCH |
| 0.273, 0.348; GPT +0.031 (−0.028 to +0.089); clear pooled and for Gemini | C.gpt +0.03075 [−0.02797, +0.08926]; by_model gemini CHECKLIST-REWARDS-STUFFING, gpt NO-DIFFERENCE-RESOLVED | MATCH |
| no-error split: 13 answers 0.300 vs 0.535; other 107 0.156 vs 0.466 | P `split_by_no_error_check`: −0.30032/−0.53462; −0.15606/−0.46589 | MATCH |
| Table 5 all 120: −0.172 [−0.220, −0.123]; E −0.109 [−0.152, −0.072]; P −0.063 [−0.090, −0.033]; PRESENCE-CHECKS-REGISTER-CONTRADICTION | M `contra.all`: D −0.17169 [−0.22039, −0.12260]; A −0.10910 [−0.15211, −0.07221]; P −0.06259 [−0.09032, −0.03271]; E1 | MATCH |
| Table 5 the 77: −0.224 [−0.288, −0.157]; E −0.170 [−0.223, −0.122]; S 0.760 [0.639, 0.915] AVOID-CHECKS-CARRY-THE-LOSS | M `contra.with_avoid`: −0.22370 [−0.28832, −0.15730]; −0.17002 [−0.22347, −0.12206]; 0.76004 [0.63865, 0.91516]; E2_share | MATCH |
| Table 5 the 43: −0.079 [−0.125, −0.026] | M `contra.without_avoid.D`: −0.07854 [−0.12476, −0.02609] | MATCH |
| Table 5 key terms 112: +0.348 [+0.283, +0.411]; +0.003 [−0.010, +0.015]; +0.346 [+0.286, +0.404]; PRESENCE-CHECKS-REWARD-KEY-TERMS | M `stuff.all`: +0.34845 [+0.28324, +0.41075]; +0.00286 [−0.00975, +0.01547]; +0.34559 [+0.28552, +0.40379]; E3 | MATCH |
| 76% of its loss | S 0.76004 | MATCH |
| 0.095 instead of 0.224; +0.129 (+0.084 to +0.177); 58% less | `D_pres` −0.09464; K +0.12906 [+0.08391, +0.17716]; 0.12906/0.22370 = 0.577 | MATCH |
| presence checks −0.063 | P −0.06259 | MATCH |
| error checks YES→NO 49.1%; presence 10.5%; call-to-call 4.0% | `contra.noise.yes_to_no.avoid` 0.49074, `.presence` 0.10526, `rep_disagree_neutral.presence` 0.04005 | MATCH |
| key terms NO→YES 45.9%, call-to-call 2.5%; error checks +0.003 | `stuff.noise.no_to_yes.presence` 0.45853, `rep_disagree_neutral.presence` 0.02488; A +0.00286 | MATCH |
| Answer to RQ3: 0.36 times; 0.079 vs Likert 0.442 on the 43 | 0.17169/0.47333 = 0.3627; −0.07854 and `post_hoc_split_by_avoid_check.without.D.likert` −0.44186 | MATCH |

The rename "avoid" → "error check", A → E: every E cell in Table 5 and Figure 5 is the `A` field of
`defects.py` (checks matching `\bavoid`), and P is the `P` field, as before. No number changed meaning.

### §5.4, Table 6

Each prediction was checked against the registration (`boolean.py` docstring, PREDICTIONS; `defects.py`
docstring, PREDICTIONS) and its outcome against `predictions` in P and M:

| prediction | recorded outcome | Table 6 | result |
| --- | --- | --- | --- |
| P1 Mohler dR > 0 | False (dR −0.011, LIKERT-MORE-RELIABLE) | no | MATCH |
| P1 Mohler dX > 0 | True (+0.021, UNRESOLVED) | direction only | MATCH |
| P1b per-tuple ICC > response-level | False (0.803 < 0.889) | no | MATCH |
| P2 Mohler dH ≥ −0.05 | False (−0.106) | no | MATCH |
| P2 Documentation and Readability dH ≥ −0.05 | True, True (−0.024, +0.089) | yes, on the point estimates | MATCH |
| P2 Code Elegance dH < 0 | False (+0.013) | no ("slightly more") | MATCH |
| E4 LOW: checklist higher | False (UNRESOLVED) | no | MATCH |
| E4 HIGH: checklist lower | True (CHECKLIST-LOWER) | yes | MATCH |
| P3 CHECKLIST-BLIND-TO-CONTRADICTION, attenuated with a no-error check | True; C with 0.235 (0.535 − 0.300) < C without 0.310 | yes | MATCH |
| P4 CHECKLIST-REWARDS-STUFFING | True | yes | MATCH |
| E1 PRESENCE-CHECKS-REGISTER-CONTRADICTION | True | yes | MATCH |
| E2 SHARED or AVOID-CHECKS-CARRY-THE-LOSS; AVOID-CHECKS-ADD-SENSITIVITY | True; True | yes | MATCH |
| E3 PRESENCE-CHECKS-REWARD-KEY-TERMS | True | yes | MATCH |

Caption margin ±0.05 r: MATCH.

### §6–§8, Appendix A, release file

| printed | source | result |
| --- | --- | --- |
| §6.1 8.5% of checklist calls; 44 checks (12 + 12 + 10 + 10) | C | MATCH |
| §6.2 "less consistent wherever the data clearly showed a difference" | Table 1 verdicts | MATCH |
| §7.1 0.621; 0.525 to 0.622 | P ceilings | MATCH |
| §7.2 46 programs (45 for miscounts); 226 | C | MATCH |
| §7.4 about 0.15; +0.014; −0.001 | F; P `stuff…C.ci95[0]` +0.01442; `dR.ci95[1]` −0.00116 | MATCH |
| §8 near ceiling; less reliable wherever clear | Tables 1–3 | MATCH |
| A.1 4,000 replicates; margins 0.05, 0.03, ±0.02; S against one half | `BOOT = 4000`; `defects.py` | MATCH |
| A.2 200 simulations; 10% and 80% bars; first version failed three gated checks | F `replicates`/docstring; `floor-rev0.json` `checks` (3 False) | MATCH |
| A.2 11 and 7 possible scores | 0–5 by 0.5; six checks → 0/6…6/6 | MATCH |
| A.2 20.5% (revision 0) | `floor-rev0.json` `mohler_NULL.retest=LIKERT-MORE-RELIABLE` 0.205 | MATCH |
| A.2 22.5% and 23.5% | F | MATCH |
| A.2 54.5% and 56% (revision 0) | `floor-rev0.json` `menagerie_Vplus/Vminus.validity` 0.545, 0.56 | MATCH |
| A.2 56–58%, 83.5–87.5% for ±0.15 | F 0.56, 0.58; 0.835, 0.875 | MATCH |
| A.2 ±0.08 detected 95–97% | F 0.95, 0.97 | MATCH |
| release `interpretation`: 0.96–0.99, 0.011, 0.03, dH −0.106 [−0.165, −0.048], 0.172, 0.473, +0.348, +0.273 | P | MATCH |
| release `limitations`: 46 submissions (45) | C | MATCH |

## 4. Figures

The `figures` step reproduces all five PNGs byte for byte. `figures.py` reads each plotted value from
the output named in its caption and stops unless it rounds to the article's printed value (its
`ARTICLE` table was checked against the article: every entry agrees with Tables 1–5). I also viewed each
figure:

| figure | caption says | plotted (from `figures.py` and the image) | result |
| --- | --- | --- | --- |
| 1 | Table 1 as slope charts; test–retest per model (solid Gemini, dashed GPT), cross-model one line; pooled dR/dX and verdict under each panel, bold where clear; source P | `paper_rows.reliability` cells 1, 2 (per-model R), 5 (X), 3 (dR), 6 (dX); `verdicts.retest`/`cross_model`; bold iff the 95% CI excludes 0 (Mohler dR, Correctness dR, Readability dR, CE dX, Readability dX) | MATCH |
| 2 | Table 2 as slope charts; dotted line the raters' agreement; pooled dH and verdict | `paper_rows.validity` cells 2, 3 (H per model), 4 (dH), 6 (ceiling); `verdicts.validity`; only Mohler bold | MATCH |
| 3 | signed error by band, both formats pooled, shaded 95% intervals; source M | `bands.*.e_likert/e_boolean` est and ci95; n 65/145/410 in the labels | MATCH |
| 4 | change under each defect, each format, pooled and per model; whiskers 95%; source P | `contra_manip_pass`/`stuff_manip_pass` `stats.D.*` (pooled checked against Table 4; per-model bars match P: −0.557/−0.196, −0.390/−0.147; +0.249/+0.368, +0.298/+0.329) | MATCH |
| 5 | Table 5 split into E and P; full bar D; for the 77, P = D − E unrounded; the 43 all P; key-terms E too small to see; source M | `paper_rows.attribution` D, A (=E), P; 77: P = −0.22370 − (−0.17002) = −0.05368; bar labels D −0.172, −0.224, −0.079, +0.348 | MATCH |

## 5. Notes (not mismatches)

1. Figures 1 and 2 label the verdict UNRESOLVED as "unresolved" under each panel, while the corrections-5
   sweep turned prose "unresolved" into "too uncertain to call". The captions call it "its verdict", and
   UNRESOLVED is a registered verdict string that §4.6 keeps and glosses, so this is consistent, but a
   reader may notice the two wordings.
2. The release file's `interpretation` still says "an appended false sentence cost it 0.172 of its
   scale"; corrections-5 swept "cost" in the article only. Wording, not a number.
3. The abstract lists the checklist correlations as "0.68 and 0.69" (GPT, Gemini) and the Likert ones as
   "0.76 and 0.82" (Gemini, GPT). No model is named, so nothing is misattributed; each pair is ascending.
4. §4.2's 1,721 answers (corpus E01–E10) cannot be recomputed from the release alone, which holds only
   the 685 drawn answers; it is stated in the dataset record and the script's docstring.
5. The 29 numbers the report does not link to provenance were all among those checked by hand above.

## 6. Mismatches

None. Every step MATCH; every printed number checked agrees with the regenerated outputs, sign
included, rounded once from the unrounded value. The renames (validity → agreement with the human
raters, dV → dH; avoid → error check, A → E; Table 5 rows; figure renumbering) did not change which
number belongs to which quantity.

Unexplained mismatches: **0**.

```yaml
reproduction: {date: 2026-11-06, by: agent, report: reproduction-4.md, unexplained_mismatches: 0, audited_commit: 98e9e1d3b0e395bf626e5a8698d96cdd909c4b27}
```
