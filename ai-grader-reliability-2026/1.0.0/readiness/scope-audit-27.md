# Scope audit 27: ai-grader-reliability-2026 1.0.0 (Paper VI), verification of corrections-26

Auditor: an agent with no part in the analyses, the draft, the release, its records, any correction
pass, or the earlier audits and reproductions. Date: 2026-10-16. No model was called and nothing was
sent to an external service. Nothing in the article, the release, the protocol, the observations, the
claim pages, the studies, `board/` or `readiness.yaml` was edited. This file is the only change. Scratch
work was two log files in the session scratchpad (`--release` and `--stamps` output) and read-only
one-liners: a search for "847" over every file `publish_set()` returns for the release, and a print of
`grader-eval/analyses/out/sampling-sd.json`.

**Text audited.** I fast-forwarded the worktree to `origin/claude/bold-ptolemy-6odavp`. HEAD is
`443188e2dae3f728550dafaea3b67720dc634ad6`. `git merge-base --is-ancestor d05bd6e HEAD` succeeds, so the
audit contains the last headline correction (`cooling_off.last_headline_correction_commit: d05bd6e`).
`ca15f03`, the commit scope-audit-26 audited, is an ancestor.

**Scope.** This is a narrow verification of `git diff ca15f03..443188e`, restricted to what the brief names.
The window changes one sentence of 4.9 (L747–749) and one of §9 (L2204–2206), one limitation of the
release file (`1.0.0.yaml` L1689–1693), records scope-audit-26 and corrections-26, adds the `readiness.yaml`
line and a `cooling_off` comment, and rebuilds the report. Line numbers are the article's at HEAD unless
another file is named. "The working record" is `studies/measurement/grader-eval/findings/grader-evaluation.md`;
"the JorGPT record" is `research/wiki/observations/lazuli-grader-jorgpt-2026.yaml`.

---

## 1. The 4.9 sentence and the 0.847 (corrections-26, finding 1)

**The text at HEAD** (L747–749): "At 40 answers the low-prior-mark arm read QWK 0.930 against a 0.886
control, an apparent gain of 0.044 that was nearly reported. At 120 the two were level."
Release file L1690–1692: "at n=120 the two were level."

**Support.** JorGPT record L1056–1058: "At n=40 an earlier version of this experiment showed the low-prior
arm at QWK 0.930 against a 0.886 control; at n=120 the two were level." The sentence now says exactly
what the record says and nothing more. **Supported.**

**Any 0.847 left for that run.** `patent_gate.py --release` reports 172 files to be published (160 text
files scanned). I searched every file `publish_set()` returns for "847":

| file | line | what it is | for the n = 120 run? |
| --- | --- | --- | --- |
| article, release file, claim pages, other observation records | — | no hit | — |
| report `index.html` | one hit | provenance pop-up of a printed 0.848, source value 0.847634 (`exemplar-marks`) | no |
| JorGPT record | L683 | pooling arm "cross-model pool of 3 LITE + 1 STANDARD, 0.847" | no |
| working record | L64 | "attempt history 0.847 across all three arms" (no sample size) | not stated (note BB) |
| working record | L169, L779 | pooling table; SAS-Bench History subject | no |
| code package JSON outputs (`grader-calibration-vs-label`, `grader-exemplar-marks`, `grader-label-compounding`) and the calibration README L144 | various | unrounded values of other analyses | no |
| `readiness.yaml` L162 | — | `cooling_off` comment: "an unsourced 0.847 removed from 4.9 and the release file" | no (records the removal) |
| `scope-audit-26.md` | L43–178 | quotes the withdrawn sentence as audit history | quoted, not asserted (note BB) |

No published file now states 0.847 as the n = 120 figure. A search for "n=120 / at 120" over the article,
`research/wiki` and the findings logs finds only the JorGPT record, the release file and the article for
this run (the other hits are the n = 120 feedback and vendor runs of other logs). **True.**

## 2. Corrections-26's statements

| item | statement | holds? |
| --- | --- | --- |
| Finding 1 | "The JorGPT record supports 'level' but gives no value" | **Yes.** L1057–1058, quoted above. |
| Finding 1 | "no record gives 0.847 for a 120-answer run" | **Yes.** Section 1. |
| Finding 1 | corrections-25's L64 identification "was wrong (that line gives no sample size …)" | **Yes.** Working record L64 has no size; it sits under a table headed "size at stratified n=150" (L46). |
| Finding 1 | "the record's only sized history run, n = 150, reads 0.849, 0.848 and 0.829" | **Yes**, for the three original arms (L262 heading "`--mode history`, n=150, LITE"; L269–271). The run has five arms; the two no-mark arms read 0.833 and 0.838 (L272–273), and none of the five is 0.847. Elliptical, not wrong (note BA). |
| Finding 1 | changed in "article 4.9; release file limitations" | **Yes.** Both diffs remove "at 0.847" and nothing else. |
| Finding 2 | 0.831 and 0.800 (L55) "are not roundings of the committed `sampling-sd.json` values 0.83256 and 0.79925" | **Yes.** `stratified_seed7` 0.8325591 and `corpus_all_rows.qwk` 0.7992468 round to 0.833 and 0.799. |
| Finding 2 | "figures from an earlier computation in the record's dated text" | **Yes.** `git log -L55,56` dates L55 to 2026-09-21 (`54104af`); `sampling-sd.json` was first committed on 2026-10-06 (`c80fc59`). The record (header `updated: 2026-09-16`) does not identify the computation, and corrections-26 does not claim it does. |
| Finding 2 | "the paper prints the committed values, rounded once (0.833 and 0.799)" | **Yes**, as scope-audit-26 section 3 established; no paper text changed here. |
| Note AY | "the preliminary runs of the design history" is now "the design-history runs" | **Yes.** §9 L2204. |
| Note AZ | the working record "is now identified as the release's `working-record` artifact" | **Yes.** §9 L2205–2206; see section 3. |
| Header | "No headline or verdict changed" | **Yes.** Only a withdrawn unsourced figure; `cooling_off.last_headline_correction` stays 2026-10-06 / d05bd6e, with a dated comment. |
| Footer | "Report rebuilt; `--stamps` passes" | **Yes.** Section 4. |

## 3. The §9 wording

"… the design-history runs (4.9), from the findings logs that section cites, the observation record
`lazuli-grader-jorgpt-2026` and the working record (the release's `working-record` artifact); …"
(L2204–2206)

- **The artifact.** `1.0.0.yaml` has a top-level `artifacts:` list (L1439) with an entry `id: working-record`
  (L1460), `kind: reference`, title "Grader evaluation: the working record, with every table and
  correction", `location.ref: studies/measurement/grader-eval/findings/grader-evaluation.md`. **Exists, under
  that id, in a list named `artifacts`.**
- **The records against 4.9's unkept-output figures, now that 0.847 is gone.** 0.930 / 0.886 and "level":
  the JorGPT record (L1056–1058). 0.044: the working record (L71) and the JorGPT difference. The
  grade-stratified −0.07 / 0.826 / 0.838: the working record and the JorGPT record (as scope-audit-26
  section 1). The ASAP 2.0 figures: the two logs 4.9 cites by path (article L812–819;
  `2026-09-16-asap2-and-the-ell-gap.md`, `2026-09-16-the-ell-gap-is-the-halo.md`). Every such figure is in
  one of the three records named, and each named record supplies at least one. **Accurate.**
- "The working record" at L2208 (the 0.795 draw) now reads back to the same identification three lines up.

## 4. Checks run

- `python3 board/render_report.py --release ai-grader-reliability-2026 --check`: "report for
  ai-grader-reliability-2026 is current", exit 0. The report's 4.9 text (L986–987) reads "were level."
- `python3 board/package_code.py --release ai-grader-reliability-2026 --check`: current (120 files), exit 0.
- `python3 board/patent_gate.py --release ai-grader-reliability-2026`: 172 files, no registered candidate
  matched, **GATE PASSES**.
- `python3 board/patent_gate.py --stamps`: exit 0, 306 of 306 `research/` files stamped before this file.
  **No "CHANGED AFTER LIFT" line.** It prints the four permitted "changed after lift (a wiki record or the
  readiness record …)" lines for `learning-graph-budget-2026` records, as at scope-audit-26; the window did
  not touch them.
- `python3 board/readiness.py --release ai-grader-reliability-2026`, as it stands: **READINESS FAILS (1
  open)**, which is `scope_audit: 2 open findings` (scope-audit-26's count, recorded in `readiness.yaml`). No
  other check fails. Four specialist reviews are listed as post-publication.

---

## Open findings

None.

## Notes (not findings, not counted)

Scope-audit-26's findings and notes:

| id | status | evidence |
| --- | --- | --- |
| Finding 1 | **CLOSED** | Sections 1 and 2. The figure was withdrawn rather than sourced; no number in a headline depended on it. |
| Finding 2 | **CLOSED** | Section 2. |
| AY | **CLOSED** | Section 2. |
| AZ | **CLOSED** | Sections 2 and 3. |
| AU, AW | **Left**, as scope-audit-26 recorded | Not touched in the window. |
| AO, AK, AL, AM, AN, R, AB | **Unchanged** | Not touched in the window. |

New notes:

- **BA. Corrections-26 gives three of the n = 150 history run's five arms.** "reads 0.849, 0.848 and 0.829"
  are the control and the two marked-prior arms; the no-mark arms (0.833, 0.838) are omitted. The point it
  makes (no arm reads 0.847) holds for all five. Wording only, in a readiness record.
- **BB. An unsized 0.847 remains in the published working record, and the withdrawn sentence is quoted in
  the audit trail.** Working record L64 ("attempt history 0.847 across all three arms") still ships as the
  `working-record` artifact. The paper no longer prints it and no record ties it to a run, so it misleads
  only a reader who already has the withdrawn sentence. `scope-audit-26.md` (published while
  `readiness.yaml` cites it) and this file quote "At 120 the two were level at 0.847" as audit history, each
  saying it is unsupported. A dated correction note at L64, like the record's 2026-10-15 notes, would close
  the loop. Outside the diff.

## Summary

**Counts.**
- Item 1: the 4.9 sentence and the release file now say what the JorGPT record says (L1057–1058); no
  published file prints 0.847 as the n = 120 figure.
- Item 2: every statement in corrections-26 on findings 1 and 2 and notes AY and AZ is true (BA: one is
  elliptical).
- Item 3: the §9 wording is accurate, and `artifacts:` holds `id: working-record` (L1460).
- Item 4: the report and package are current; GATE PASSES; `--stamps` passes with no CHANGED AFTER LIFT;
  `readiness.py` fails only on the recorded scope-audit count.
- New notes: BA, BB; none counted.
- Open findings: 0.

scope_audit: {date: 2026-10-16, by: agent, report: scope-audit-27.md, open_findings: 0, audited_commit: 443188e2dae3f728550dafaea3b67720dc634ad6}
