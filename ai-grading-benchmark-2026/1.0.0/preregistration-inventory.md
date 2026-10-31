# Pre-registration inventory: ai-grading-benchmark-2026 1.0.0

Date 2026-10-28. Built by an agent (Claude Opus 5.5) from the sources, and corrected twice after independent audits
of its classifications; language CHANGE 3 added 2026-10-29. Source: the benchmark repository at
`bd3165f3d5bd1cd68c0a3f6115dbb2e3719b8107`.
Every study is one of the release's `analyses:` (`1.0.0.yaml`). Three analyses hold a second pre-registered design
in its own file, which the paper reports and which this inventory includes with its analysis: `fairness-ellipse/rep.py`
(the replication), `video/padding.py` (the length study) and `feedback-validity/lc_mrbench.py` (the Learning Commons
evaluators). Files with pre-registrations the paper does not report (`precision/run.py`, `discriminant/mtmm.py`,
`analyses/cluster_check.py`) are left out. Of the analyses, `board-fetch` and `public-data` are data
preparation, not studies, and `release-comparison` (`bench.py drift` on `out/lineage-2026-10-23/`) is exploratory,
with no pre-registration, threshold, verdict or planted-effect check. That leaves 30 studies.

## How each change is classified

Each numbered change is read from its own header and dated against the study's committed outputs where the header
does not say what had been read.

- **A**: made before any of that study's results had been read (design, implementation, budget, bug found before
  results).
- **F**: made after the study's own planted-effect check ran (usually failed), before any of its real results had
  been read.
- **P**: made after a pilot whose outputs were seen, before any of the study's runs.
- **R**: made after some of that study's own results had been read. Kinds: *coverage* (models or graders added,
  no rule changed), *arm* (a new arm or run added), *fix* (a bug fix), *statistic* (a reported or descriptive
  statistic added), *scoring* (what is scored, how a measure is read, or where results are shown changed).

## Inventory

"Thresholds and verdicts" says whether the pre-registration states a threshold and verdict wording before the study's
runs. "Planted-effect check" names the check that covers the study's statistics.

| study (release analysis) | pre-registration | thresholds and verdicts | planted-effect check | smoke or pilot before it | numbered changes |
|---|---|---|---|---|---|
| board (`leaderboard.py`, `floor.py`) | `leaderboard.py` battery; `floor.py` docstring | the probe battery and `floor.py`'s detection thresholds, yes; the disqualifying flags and the false-discovery correction, no: they were added after the board's first rows (`d04c148f`, `09ef6229`; see "The board's unnumbered changes") | `floor.py`: the paired probe statistics (gaming, label, surface, padding, blicket, null answers). Not the feedback columns, not the setups study's held-out note | `floor.py` CHANGE 4: "one smoke seed (5, not among the registered seeds)" disclosed | 5: C1 A ("committed before this version ran"); C2 F ("after the CHANGE 1 result, before any real run was read"); C3 R scoring (chimpanzee replaced by blicket after the first round's results; `docs/RESEARCH-LOG.md` "Second round": "The chimpanzee figures in the first-round tables above are kept as recorded ... re-sent for all 16 first-round runs"); C4 R scoring (three probes from the literature review, the null answers among them now a disqualifying flag, added in the "Third round" after rounds 1 and 2 were read); C5 R fix (a fake-grader bug, after the CHANGE 4 result, with the real rounds already read). The board's other changes to its scoring are not numbered: see "The board's unnumbered changes" below |
| standard-checks (`analyses/standard_checks.py`) | docstring | yes (ACT thresholds, PASS / FAIL / INDETERMINATE) | none (named exception) | no | 1: C1 R fix ("found when the article's draft compared these QWKs with the leaderboard's") |
| length-partial (`analyses/length_partial.py`) | docstring | yes | own ("FLOOR ... run before any submission is read") | no | 0 |
| trained-scorers (`baselines/baselines.py`) | docstring ("PRE-REGISTERED 2026-10-25") | **no** ("EXPECTED (written before scoring, to be checked, not a verdict)") | the board's `floor.py` covers its probe statistics; its agreement estimates have none | no | 4: C1 R arm (encoder-ridge, 2026-10-25 "before this baseline was scored", after the classic baselines' results, committed 2026-10-25 12:36); C2 R arm (DeBERTa, after the encoder baseline's result); C3 R scoring ("after every baseline result had been read": ranked on a scoring board); C4 R scoring (made unranked reference rows) |
| essays-finetune (`essays-finetune/study.py`) | docstring | yes | own (`out/floor.json`) | no | 1: C1 R arm ("written AFTER every result of arms 1-4 above was read"; adds Gemma and the board battery) |
| essays-genft (`essays-genft/study.py`) | docstring | yes | own; failed for M1, M4, M5 (code), M7, M8 (UNMEASURED) | no | 4: C1 A ("before any training run or model call"), C2 A (after the smoke test's assertion, "before any training of the real run, any model call or any grading"), C3 A (after the template check, before training), C4 F ("after the floor's 200-world run and before any real grading was read") |
| setups (`setups/study.py`) | docstring | yes | the board's `floor.py` for its gaming probes. **None** for the held-out vouched note: "The held-out vouched probe has no prior floor: it is read as a detector only if it shows a gain ... for at least three models under DEFAULT" (a usability rule on real data, not a planted-effect check); `floor.py` plants no vouched effect. The note is one of the FIXED verdict's conditions | no | 1: C1 A ("before any result was read"; Olmo added) |
| guard-retest (`guard-retest/study.py`) | docstring | yes | own | no | 2: C1 A (implementation, "before any run was read"); C2 R coverage ("AFTER the three hosted models' results were read"; Olmo added) |
| reasoning-effort (`reasoning/study.py`) | docstring | yes | own signal floor, for check 1 only; check 3's effort verdicts have none (the article does not report them) | no | 1: C1 R fix (2026-10-27 rounding fix; `out/runs.json` first committed 2026-10-25) |
| hosting (`hosting/study.py`) | docstring | yes | the board's gaming probes | no | 0 |
| precision-controlled (`precision-controlled/study.py`) | docstring | yes | own | no | 2: C1 F ("after the floor's first run and before any call"); C2 A ("no figure from any run had been computed or read") |
| paraphrase (`paraphrase/study.py`) | docstring | yes | own | no | 5: C1 F ("after the floor and before any call"); C2 F ("after CHANGE 1's floor and before any call"; verdict per model, 5% move); C3 A (implementation); C4 R coverage ("AFTER the first four models' results were read"; 18 models added); C5 R coverage ("AFTER the 20 models' results were read"; Astra, Fable) |
| prompt-ranking (`prompt-ranking/study.py`) | docstring | yes | own | no | 1: C1 R statistic ("AFTER the result was read"; descriptive rank range over re-asks) |
| pushback (`feedback-board/pushback.py`) | docstring | yes | own; the progressive / regressive split has none (named exception) | no | 1: C1 R statistic (2026-10-25, `not_ruled_out` beside null verdicts; `out/pushback.json` first committed 2026-10-24) |
| maths-working (`maths-process/process.py`) | docstring | yes | own | no | 2: C1 R coverage (Olmo added from its board grades, after the 21 graders' results); C2 R fix (half-up rounding; output unchanged) |
| feedback-validity (`feedback-validity/validate.py`; `feedback-validity/lc_mrbench.py`) | docstrings (`lc_mrbench.py`: "PRE-REGISTERED 2026-10-24, before any call") | yes (`lc_mrbench.py` uses validate.py's thresholds) | own (`validate.py --floor`; `lc_mrbench.py --floor`) | `lc_mrbench.py`: one smoke call (HTTP 400, no output), before its CHANGE 1 | 2: `validate.py` C1 F ("after the first --floor run": label strings); `lc_mrbench.py` C1 A ("after one smoke call, which returned HTTP 400 and no output": schema inlined) |
| feedback-board (`feedback-board/fb.py`) | docstring ("PRE-REGISTERED 2026-10-24") | **no** ("No verdict strings: these are leaderboard columns") | **none**: the halo and the gives-away share were not checked on simulated graders (`floor.py` covers neither) | no | 1: C1 R scoring ("after the results"; gives-away removed from the feedback strand's score) |
| feedback-discordant (`feedback-discordant/study.py`) | docstring | yes (S / W registered as descriptive) | own (S) | no | 3: C1 A ("before any call"); C2 A ("before any Fable call"; route); C3 R coverage ("after the 21 hosted results had been read"; Olmo added) |
| speech (`speech/PREREG.md`) | `PREREG.md` | **no** (probes and what a sound grader does; intervals only) | the board's `floor.py` covers its paired statistics (surface, padding, null answers); `media/floor.py` covers its recording-quality probes (noise, telephone channel) | yes: "One smoke run (2 cases, Gemini 3.8 Flash, 18 gradings)" | 1: C1 R coverage ("after the six graders' results were read") |
| language (`language/study.py`) | docstring | yes | own | no | 3: C1 A ("after the dry run and before any call"; cap); C2 R coverage ("after the other six models' results were read"; Gemini 3.5 Flash Lite); C3 R run ("after all seven models' results were read"; Voxtral's 112 transport failures retried once under the harness's rule) |
| handwriting (`images/PREREG.md`) | `PREREG.md` | **no** (probes and what a sound grader does) | **none** (named exception) | yes: "A 2-case smoke run (Gemini 3.5 Flash Lite)" | 1: C1 R coverage ("after the first five graders' results were read") |
| video (`video/PREREG.md`, `video/analyse.py`; the length study `video/padding.py`, `video/LENGTH.md`) | `PREREG.md`; `padding.py` docstring ("PRE-REGISTERED 2026-10-24, before any call of this design") | yes | WATCHES THE RECORDING: `out/video/floor-beyond-length.json`, three planted graders (stopwatch, watcher, weak), one world each, not a power and false-alarm study; the board's `floor.py` for the paired text-side statistics; `media/floor.py` for the recording-quality probes; the length study: its own floor (`out/video/padding-floor.json`, passed) | yes: "One smoke run ... three gradings" | 4: `PREREG.md` C1 R coverage ("after the first eleven runs' results were read"); `analyse.py` C1 R statistic (2026-10-25, `not_ruled_out`; results first committed 2026-10-24); `padding.py` C1 R statistic (2026-10-25, `not_ruled_out`; the length study's results committed 2026-10-25 01:26, before the 13:12 commit of the change); `padding.py` C2 R coverage ("after the first five graders' results were read") |
| media-floor (`media/floor.py`) | docstring | yes | it is the check for the speech and video recording-quality probes | no | 3: C1 F ("after step 1's first run, before any real quality-probe result was read"); C2 A (step 3 written "before any call of step 3", after step 2's real positive-control result, as the design said it would be; the strict reading would be R arm); C3 A (cap raised "before any step-3 result was read") |
| perception (`perception/study.py`) | docstring ("PRE-REGISTERED 2026-10-26, before any call of this design") | yes | own | no: the pre-registration came first; a one-model hosted pilot followed it, and CHANGE 1 changed the design after that pilot, before any call of the design run | 3: C1 P ("after a one-model pilot ... before any call of the design below"); C2 R scoring ("after reading only the first 12 test records of one model"; floor step 2 changed); C3 R scoring (after batch 1 had been graded and test records seen, "before any group comparison was read"; refusal and rating readings tightened) |
| fairness-ellipse (`fairness-ellipse/gap2.py`; the replication `fairness-ellipse/rep.py`) | docstrings (`rep.py`: "PRE-REGISTERED 2026-10-24, after gap2.py's result ... and before any grading for this design") | yes (`rep.py`: REPLICATES / DOES NOT REPLICATE / MIXED) | own (`gap2.py floor`; `rep.py floor`) | no | 7: `gap2.py` C1–C3 R coverage (graders added "after the ... results were read", "not because of any result"); `rep.py` C1 F ("The floor as written FAILED", "before any grading for this design"); `rep.py` C2 R coverage ("after the six graders' results were read"); `rep.py` C3, C4 R coverage ("after the earlier graders' results were read") |
| disability (`disability/gap.py`) | docstring | yes | own | no | 5: C1 A ("before the floor or any call ran"); C2 F (after "RESULT of CHANGE 1's floor ...: FLOOR FAILS", "before any real grading of this design was read"); C3–C5 R coverage (graders added after earlier graders' results were read) |
| disability-mechanism (`disability-mechanism/study.py`) | docstring | yes | own; Part A's failed (UNMEASURED) | no | 0 |
| drift-monitor (`drift/monitor.py`) | docstring | yes | own | no | 2: C1 F ("after the baseline month and before any comparison"; floor failed); C2 F (after "RESULT: the floor still FAILED", "before any comparison") |
| contamination (`contamination/search.py`) | docstring | yes | own | no | 1: C1 R fix ("after the first run", which "FAILED its floor"; the docstring says the first run's case counts "had been printed ... before the cause was found") |
| energy (`energy/energy.py`) | docstring | yes | own | no | 3: C1 A ("before any energy figure was read"); C2 R statistic ("after Llama 3.2 3B's figures were read"; the registered rule stands and descriptive readings were added); C3 R arm (a second run of the eight models, approved after the first run's figures were read) |

## Which reading of the board's early rounds

`floor.py` C3–C5 were made on 2026-10-23, while the board's first rounds ran in the research harness, before this
repository existed (it was created on 2026-10-24). `docs/RESEARCH-LOG.md` records those rounds' results ("First runs",
"Second round", "Third round", all 2026-10-23) before each of these changes, and the board is their continuation: the
blicket probe was re-sent for all 16 first-round runs and the first-round figures are kept as recorded. This inventory
therefore counts those rounds as the board's results, and C3–C5 as made after some of them had been read (the strict
reading). Under the other reading, which counts only results produced in this repository, C3 and C4 would be A and C5
F; the totals for that reading are given below too.

## The board's unnumbered changes

The board's scoring also changed after its results without a numbered change. Each is in the benchmark repository's
commit history (the commits below are ancestors of the pinned commit `bd3165f3`); where else it is recorded is said
for each.

| date | change | commit | also recorded in |
|---|---|---|---|
| 2026-10-24 | the whole-task (overall) score, its strand weights and rank intervals, and the disqualifying flags (gaming above 5% of the scale, any blank credit, refusals above 5%) with the rule that a flagged model ranks below every unflagged one, all added after the board's first rows (the research log had already summarised those rows with the same 5% cut) | `d04c148f` | nowhere else; `leaderboard.py`'s docstring still says "No overall score" |
| 2026-10-25 | the reading-the-working and pushback strands (weight 10 each) added to the whole-task score, after their results (maths working and pushback committed 2026-10-24) | `bef2041b` | nowhere else |
| 2026-10-25 | the false-discovery correction across probe intervals and the per-task scores added | `09ef6229` | `leaderboard.py` docstring, "(added 2026-10-25)" |
| 2026-10-27 | the feedback strand scores the halo's distance from 0 in either direction | `c23ba3aa` | `docs/CORRECTIONS.md`, "Feedback strand: how the halo is scored" |
| 2026-10-27 | the feedback strand scored from the wrong-grade test's S and W instead of the halo | `60a885c8` | `docs/CORRECTIONS.md`, "Feedback strand of the whole-task score: what is measured"; a comment in `leaderboard.py` `strand_scores` (`fb.py` CHANGE 1 still says "Halo alone is scored") |

`fb.py` CHANGE 1 (2026-10-24, gives-away left out of the feedback strand; also a row in `docs/CORRECTIONS.md`) and
the trained scorers' CHANGE 3 and 4 are numbered and counted below. The changes in this table are not counted in the
totals below, which count numbered changes only.

## Counts

- **Studies:** 30 analyses that are studies (plus one exploratory comparison with no pre-registration); three of them
  hold a second pre-registered design (above).
- **Thresholds and verdict wording stated in advance:** 26 of 30, counting the board for its probe battery and `floor.py`'s detection thresholds; its disqualifying flags were added after its first rows (`d04c148f`). Not: trained-scorers (expectations, not verdicts),
  feedback-board (leaderboard columns), speech and handwriting (probes and what a sound grader does).
- **Planted-effect check:** 27 of 30 have one covering their main statistics. None: standard-checks, feedback-board
  (the halo and the gives-away share) and handwriting. Not covered within studies that have one: the setups study's
  held-out vouched note (part of its FIXED verdict), the pushback progressive / regressive split, the trained scorers'
  agreement estimates, and reasoning-effort's effort verdicts (not reported in the article). The video verdict's check
  is three planted graders, one world each, not a power and false-alarm study.
- **Pre-registration location:** a script's docstring for 27; `PREREG.md` for speech, handwriting and video.
- **Smoke runs before the pre-registration:** speech, handwriting and video (two cases or three gradings, excluded
  from results); the board's floor disclosed one smoke seed. After the pre-registration: one smoke call before
  `lc_mrbench.py`'s CHANGE 1, and perception's pilot before its CHANGE 1.
- **Numbered changes:** 69 in 27 studies (three studies have none).

| class | strict reading (used) | other reading |
|---|---|---|
| A: before any of the study's results was read | 16 | 18 |
| F: after the study's own planted-effect check, before its results | 11 | 12 |
| P: after a pilot, before the study's runs | 1 | 1 |
| R: after some of the study's own results had been read | 41, in 21 studies | 38, in 20 studies |

The 41 R changes (strict reading) by kind:

| kind | count | which |
|---|---|---|
| coverage (models or graders added; no rule changed) | 19 | guard-retest C2; paraphrase C4, C5; maths-working C1; feedback-discordant C3; speech C1; language C2; handwriting C1; video `PREREG.md` C1, `padding.py` C2; fairness-ellipse `gap2.py` C1–C3, `rep.py` C2–C4; disability C3–C5 |
| arm or run added | 5 | trained-scorers C1, C2; essays-finetune C1; energy C3; language C3 |
| bug fix | 5 | standard-checks C1; reasoning-effort C1; maths-working C2; contamination C1; board `floor.py` C5 |
| reported statistic added | 5 | prompt-ranking C1; pushback C1; video `analyse.py` C1, `padding.py` C1; energy C2 |
| scoring or reading changed | 7 | feedback-board C1 (gives-away out of the feedback strand's score); trained-scorers C3, C4 (placement on the boards); perception C2, C3 (a floor step and two readings); board `floor.py` C3 (a probe replaced), C4 (three probes added, the null answers now a disqualifying flag) |

These counts depend on reading each change against its study's timeline and were corrected after independent
audits; the paper and the release therefore do not print them.
