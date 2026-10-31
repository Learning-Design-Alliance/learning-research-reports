# Scope audit 29: ai-grading-benchmark-2026 1.0.0 (the benchmark paper), corrections-28

Date 2026-10-30. Independent verification audit by an agent (Claude Opus 5.5) with no part in the analyses, the draft,
the release, any correction pass or the earlier audits. Narrow scope: corrections-28 (W1, the abstract's short-answer
sentence; D1, the maintainer's AI use section and the placeholder count).

## Setup

- Fresh clone of `Learning-Design-Alliance/Learning-engineering-research`, branch `ccr-cc446611-ss4v9y`, in an empty
  scratch directory. HEAD `e5fe22252e74cfcb585b3f78eaadf7627c945434` (the expected e5fe2225; no later commits).
- `git merge-base --is-ancestor 9555bbdf HEAD` succeeds.
- Python run with `python3 -I` from inside the clone.
- Source for the interval check: `out/leaderboard.json` of the AI grading benchmark repository (the release's
  `code/out/leaderboard.json`), read from a local working copy at commit 8219436, rows `task == "mohler"`, 22 models.

## What was checked

1. `research/readiness/ai-grading-benchmark-2026/corrections-28.md` and
   `git diff e5fe2225~1 e5fe2225 -- research/article/ai-grading-benchmark.md`, plain and with `--word-diff=plain`.
   The commit also touches `readiness.yaml` (disclosure `present: true`) and the rebuilt report; both consistent with D1.
2. The reworded abstract sentence against Table 5.1, the §5.1 text and the source:
   - Point estimates above 100% of the short-answer ceiling, Table 5.1: 18 (all but Gemini 3.5 Flash Lite 96%,
     Ministral 8B 99%, Gemma 3 4B 91%, Llama 3.2 3B 66%). Source: 18 with `share_of_ceiling.estimate > 1`.
   - Share-of-ceiling intervals wholly above 100%: source, 0 of 22 (highest lower bound 0.990, Claude Opus 5.5).
     §5.1: "no model's interval lies wholly above 100%, because the raters' agreement on 100 answers is itself
     uncertain". The abstract matches.
   - Alternative reading (the model's raw QWK interval against the fixed 0.573): every lower bound is below 0.573
     (highest 0.571, Claude Opus 5.5), so the sentence is also true under that reading; it cannot mislead on the
     fact stated. See N1.
   - Fit with the rest of the sentence: "On short answers ... but for none does the whole interval lie above it; on
     code four models are shown to agree ... ; and on essays no point estimate reaches ... and 18 of the 22 are shown
     to fall below it, while a fine-tuned scorer (QWK 0.809) ...". Grammatical; "it" refers to the raters' agreement;
     the three clauses stay parallel (point estimate versus interval, then "shown"). Consistent with the Answer to
     RQ1 ("none is shown to exceed them"), which was left unchanged.
3. AI use section: the placeholder line `PLACEHOLDER (AI use): to be written by the maintainer.` is replaced by three
   paragraphs of the maintainer's text (content not judged). `grep -i placeholder` on the article finds only the
   front-matter key, which reads `placeholders: 0`; no `TODO`, `TBD` or "to be written" remains. The rebuilt report
   holds no `PLACEHOLDER` and contains the new section.
4. Other changes: the word diff of the abstract shows only the W1 sentence changed; the rest is rewrapping (including
   the line break before "Six of seven audio models"). The only other article hunks are the front-matter count and
   the AI use section. No number changed.

## Findings

| id | status | where | what | suggested fix |
|---|---|---|---|---|
| N1 | note | abstract, short-answer clause | "the whole interval" does not say whose interval (the share of the raters' agreement, which also carries the raters' uncertainty). Both readings, share interval above 100% and raw QWK interval above 0.573, are true for none of the 22, so the text is not wrong or misleading. | Optional: "but for none does its interval lie wholly above it". |
| N2 | note | §5.1 | The brief describes the share interval as resampling answers and recomputing the raters' agreement; §5.1 says this only implicitly ("because the raters' agreement on 100 answers is itself uncertain"; §5 intro, bootstrap over items). Adequate for the abstract claim. | None required. |

No OPEN findings.

```yaml
scope_audit: {date: 2026-10-30, by: agent, report: scope-audit-29.md, open_findings: 0, audited_commit: e5fe22252e74cfcb585b3f78eaadf7627c945434}
```
