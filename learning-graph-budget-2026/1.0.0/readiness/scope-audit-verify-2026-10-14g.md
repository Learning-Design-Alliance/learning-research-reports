# Scope audit, verification: learning-graph-budget-2026 1.0.0 (Paper II), 2026-10-14 (seventh)

- **Audited commit.** `322a8635324ea6d28535765efa675099e5cd630f` (HEAD of `origin/main` after `git fetch origin main`).
- **Auditor.** An agent with no part in the analyses, the draft, the release, any correction pass or the earlier audits.
- **Scope.** (1) EE1 of `scope-audit-verify-2026-10-14f.md` (audited d3b5d4d), answered by `corrections-14.md`, and
  that audit's note on the held-record topics; (2) every change in `git diff d3b5d4d 322a863 -- research/README.md
  research/holding/`. Nothing earlier audits settled is re-audited.
- **Headline-correction commit.** `readiness.yaml` `cooling_off.last_headline_correction_commit:
  5e74d15b4bac1b617be1a0ee56ed8b44c7713435` (`last_headline_correction: 2026-10-14`). `git merge-base --is-ancestor
  5e74d15 322a863` succeeds: the audited commit contains it. The diff d3b5d4d..322a863 touches only the two READMEs,
  `corrections-14.md` and the previous audit file. No article, provenance, notebook, figure or headline number changes.

A finding is OPEN only where text is wrong, unsupported or misleading. Wording preferences are recorded as notes.

---

## 1. Verification of EE1

| Finding | Status | Text at 322a863 |
| --- | --- | --- |
| EE1 | RESOLVED | `research/README.md`, "## Paper": "Its HTML report, which recomputes each number its provenance files link (1,624 of the 1,751 numbers in the abstract, results and conclusion at the last build) from its source, is `reports/learning-graph-budget-2026/` (embargoed, internal)." |

**Checks.**
- The committed report `research/reports/learning-graph-budget-2026/index.html` was last changed at d3b5d4d. The article
  has not changed since, and `render_report.py --check` reports the report current. It prints "1624 of 1751 numbers
  in the abstract, results and conclusion link to their source". The README's 1,624 of 1,751 matches.
- "Recomputes … from its source": the `board/render_report.py` docstring says "Every number a provenance file covers
  is recomputed from its source at build and linked to it … A printed number that no longer matches its source FAILS
  THE BUILD", and `provenance_tables()` and `provenance_text()` call `prov.check()` on each linked number. Supported.
- "At the last build": the count is a property of the build, and the README says so. Accurate.

---

## 2. Every change in the diff, checked

**`research/README.md`, held records.** The topic list now reads "completeness and decompositions, motifs, error costs,
facilitation, budget, load, help-seeking and the work probe". The destinations read "Paper V for completeness,
decompositions and motifs; Paper VII for error costs, facilitation, budget and load; help-seeking and the work probe
not yet assigned". Checked against `research/holding/paper-1/`:
- There are eight claim pages under `claims/` and ten observations in the two `*.moved.yaml` files. Both counts are correct.
- Every topic has a record:
  - completeness: `graph-shape-carries-no-completeness-signal`, `capture-recapture-misreads-proposer-diversity`
  - decompositions: the completeness claim's "independent human decompositions" paragraph
  - motifs: `motif-shares-sit-inside-the-random-null`, linked to the completeness claim
  - error costs: `node-and-edge-error-costs-are-not-a-fixed-ratio`, `ten-to-one-is-not-a-constant`,
    `error-cost-ordering-survives-the-load-exponent`
  - facilitation: `pruning-not-repair-is-what-facilitation-contributes`,
    `a-capability-map-and-an-expert-facilitator-are-substitutes`, and their observations
  - budget: `extraneous-capabilities-dominate-an-instructional-budget`, `extraneous-capabilities-dominate`
  - load: `element-interactivity-is-far-weaker-than-load-models-assume`, `no-detectable-load-effect-on-bundle-time`
  - help-seeking: `a-learners-choice-to-seek-help-cannot-be-used-to-measure-scaffolding`,
    `help-seeking-cannot-measure-scaffolding`
  - work probe: `a-work-probe-predicts-time-to-outcome-better-than-prior-knowledge`, `work-probe-beats-prior-knowledge`

  Every record falls under a listed topic.
- Every listed topic now has a destination, and the list agrees with the destinations. Motifs go with completeness
  to Paper V. That fits the motif observation's link to the completeness claim and `reproduction.md` ("The paper plan
  moves completeness and capture–recapture out of Paper II, to Paper V"). This answers the 14f note.

**`research/holding/paper-1/README.md`.** The destinations clause now uses the same wording as the research README.
Correct.

**`research/README.md`, Paper.** This is EE1, resolved.

### Notes (not findings)
- The report carries 1,686 provenance links in all, and 62 of them sit outside the abstract, results and conclusion.
  The README's parenthetical counts only those three parts and says so, so it is not misleading.

---

## 3. Commands at 322a863

| Command | Outcome |
| --- | --- |
| `python3 board/render_report.py --release learning-graph-budget-2026 --check` | exit 0, "report for learning-graph-budget-2026 is current" |
| `python3 board/readiness.py --release learning-graph-budget-2026` | exit 1, "READINESS FAILS (2 open)": explain_back is not signed by the maintainer; cooling_off: `scope_audit` (2026-09-25) predates the last headline correction (2026-10-14). Eight specialist reviews are listed as post-publication. |

The `scope_audit` cooling-off item is the `readiness.yaml` record, which this audit may not edit.

---

## 4. Summary

- EE1 is RESOLVED, and the 14f note on the held-record topics is answered.
- The diff has no open findings.

```yaml
scope_audit: {date: 2026-10-14, by: agent, report: scope-audit-verify-2026-10-14g.md, open_findings: 0, audited_commit: 322a8635324ea6d28535765efa675099e5cd630f, scope: verification of corrections-14; chain scope-audit-2026-10-14b.md -> verify c, d, e, f, g}
```
