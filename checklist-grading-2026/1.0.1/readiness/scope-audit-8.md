# Scope audit 8: checklist-grading-2026 1.0.0, verification of the scope-audit-7 corrections

**Independence.** I am an agent with no part in the analyses, the draft, the release file, any
correction pass, the earlier scope audits or the reproductions. No model was called.

**Commit audited.** `ebae337166d123fcbf5803fd934d4d7dbe9742b2` (branch `claude/blissful-fermat-jeqm05`),
checked out and confirmed as HEAD before starting.

**Scope.** Narrow: `git diff be685db ebae337 -- research/article
research/wiki/research/releases/checklist-grading-2026/1.0.0.yaml`, three changed sentences, read
against F3 and notes A and B of `scope-audit-7.md` and the "Scope audit 7" section of `corrections-6.md`.
Sources: §4.6 and Appendix A.2 of `research/article/precise-checklists-and-an-ai-grader.md`; the
docstring floor record and `run_floor` (worlds, gated checks, `reported_not_gated`) in
`studies/measurement/grader-boolean-rubrics/boolean.py`; that study's `out/floor.json` (revision 1) and
`out/results.json` (unrounded). The rest of the paper was not re-audited.

**What counts as open.** Text that is wrong, unsupported or misleading against the outputs or the
registered design. Wording that is correct but could be clearer is a note.

---

## 1. F3 (§7.4): resolved

New text: "The detection floor confirmed that the verdict rules find most of the planted effects it
tested (not differences of 0.10 in human agreement on programs; §4.6) and, when both formats share a
scale, rarely find effects that are not there (§4.6 gives the exception for different scales)".

- **Is "most" true, and is the exception the only one?** The floor's planted-effect worlds in revision 1
  (`out/floor.json`) and their target verdicts: Mohler V+ 97%, V− 95%, R+ 97%; Menagerie V+0.15 87.5%,
  V−0.15 83.5%; CONTRA 100%; BLIND (LIKERT-ALSO-BLIND) 96.5%; STUFF 98%; Menagerie V+0.10 58%,
  V−0.10 56%. Every world clears the 80% bar except the two ±0.10 human-agreement worlds on programs
  (54.5% / 56% in revision 0, `floor-rev0.json`; 58% / 56% in revision 1, listed under
  `reported_not_gated`). So "most" is correct and the parenthetical names exactly the worlds that fell
  short. Wrong-sign rates are 0% in all four Menagerie validity worlds, so the parenthetical does not
  need to qualify direction.
- **Numbers and wording.** "Differences of 0.10" covers both planted signs (±0.10), matching the
  docstring ("Menagerie V+/-0.10") and A.2 ("+0.10 and of −0.10"). "Human agreement" is the paper's name
  for the registered validity measure (§4.6, "Differences between formats"), and "programs" is the
  Menagerie corpus, as elsewhere in the paper.
- **Section reference.** §4.6 ("The detection floor", second limit) says a difference of 0.10 on programs
  "is found only 56–58% of the time", which is what the parenthetical points to. A.2 carries the full
  record and is consistent with it (54.5% / 56% at revision 0; 56–58% against 83.5–87.5% for ±0.15 at
  revision 1).
- **Meaning of the paragraph.** The first clause no longer reads as a full confirmation. The second
  clause (null worlds on a shared scale) is unchanged and still true: revision 1 signed false rates
  (both signs summed) are 4.0–8.0% across the NULL worlds' validity, retest and cross-model verdicts,
  against a 10% bar. The following sentence ("a difference in human
  agreement smaller than about 0.15 could go undetected") now follows from the parenthetical rather than
  correcting it. The same-session caveat is kept. Nothing is overclaimed: the sentence does not say the
  floor tested every verdict (it did not plant a cross-model difference or a Menagerie retest
  difference) and it does not need to, since it is limited to the effects "it tested".

This is the first of the two fixes scope audit 7 suggested, taken nearly verbatim.

## 2. Notes of scope audit 7

| note | status | check |
| --- | --- | --- |
| A | resolved | Table 6, RQ2 Mohler row: "the 95% interval's upper end, −0.048, is just inside it". `results.json` `mohler/stats/dV/ci95/1` = −0.0475046, rounded once to −0.048, and \|−0.0475\| < 0.05, so "just inside" is true of the 95% interval. The 90% interval is [−0.1549, −0.0565], wholly beyond the margin, which is consistent with held "no". The point estimate −0.10616 → −0.106 is unchanged. The cell now names the interval and cannot be read against §4.6's 90% rule. |
| B | resolved | Release `interpretation`: "an appended false sentence lowered it by 0.172 of its scale against 0.473 for Likert". The preposition is restored, and the numbers are unchanged from be685db, which scope audit 7 checked. |

## 3. New findings

None. The change touches three sentences, changes no number, and introduces no new claim beyond what
§4.6, A.2 and the floor record state.

## 4. Notes (non-blocking)

- **C. §7.4 now cites §4.6 twice in one sentence.** "(…; §4.6)" and "(§4.6 gives the exception for
  different scales)" sit a clause apart. Correct, but one reference would do, for example by moving both
  qualifications into a single closing parenthesis or pointing the first at Appendix A.2, which carries
  the 0.10 record in full.
- **D. Source line length.** The edited line in §7.4 was not re-wrapped (about 140 characters). It
  renders identically; this is cosmetic in the Markdown source only.

## 5. Other checks

- The committed HTML report (`research/reports/checklist-grading-2026/index.html`) carries both new
  article sentences. `python3 board/readiness.py --release checklist-grading-2026` at this commit lists
  only scope_audit (scope audit 7's open finding), explain_back and the article's draft status as open;
  it does not report the committed report as stale.
- `corrections-6.md` describes the three changes accurately and records `numbers_changed: 0`, which
  matches the diff.
- No other sentence in the article or the release file paraphrases the §7.4 claim (searched for
  "planted effects", "sizes tested" and "detection floor").

## 6. Summary

- HEAD `ebae337166d123fcbf5803fd934d4d7dbe9742b2`.
- F3 resolved; notes A and B resolved.
- Open findings: 0.
- Notes: 2, non-blocking (C: two §4.6 references in one §7.4 sentence; D: unwrapped source line).

```yaml
scope_audit: {date: 2026-11-06, by: agent, report: scope-audit-8.md, open_findings: 0, audited_commit: ebae337166d123fcbf5803fd934d4d7dbe9742b2}
```
