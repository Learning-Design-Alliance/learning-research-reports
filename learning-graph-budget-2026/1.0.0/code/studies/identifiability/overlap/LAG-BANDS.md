# Positivity by lag band (`lag_bands.py`, pre-registered 2026-09-24)

Does the atlas's estimand, the drop in first-attempt B accuracy between learners who had passed A and
those who had only failed it, depend on how long before B they first tried A? Verdict rules and a
synthetic floor were committed before any corpus was read (commit `7203f86`). Floor: a lag-decaying
planted gate returned DECAYS in 3 of 3 worlds, and a constant gate returned neither DECAYS nor GROWS.

Primary estimand: within-pair D = drop(lag ≥ 7 days) − drop(lag < 1 day), over pairs readable in
both bands, 10,000 sampled pairs per corpus, B-item cluster bootstrap.

| corpus | pairs readable in both | drop, < 1 day | drop, ≥ 7 days | D [95% CI] | verdict | SUPPORTED pairs only |
| --- | ---: | ---: | ---: | --- | --- | --- |
| ASSISTments 2012–13 | 644 | +0.158 | +0.096 | −0.062 [−0.080, −0.043] | DECAYS | UNANSWERABLE (14) |
| XES3G5M | 175 | +0.153 | +0.120 | −0.033 [−0.060, −0.007] | DECAYS | DECAYS (83) |
| EdNet (re-issued; no-tag rows dropped 2026-09-25) | 6,170 | +0.058 | +0.043 | −0.015 [−0.022, −0.007] | DECAYS | UNRESOLVED (72) |
| Eedi | 4,643 | +0.166 | +0.118 | −0.048 [−0.052, −0.043] | DECAYS | DECAYS (2,504) |
| EDM Cup | 0 | — | — | — | UNANSWERABLE | — |

**Programme verdict: LAG-DEPENDENT** (4 of 4 answerable corpora DECAY). The drop is largest when B
follows A within a day and is 24–39% smaller after a week or more. EDM Cup has no pair readable at
short lags: its learners meet one skill per assignment.

**What it does and does not mean.** Learners who reach B the same day differ from those who return
weeks later, so D compares different learners across bands; it shows the estimand moves with lag, not
a forgetting curve for any edge. It does mean every positivity figure read without a lag band mixes
estimands, and the within-day band carries the largest share of any "SUPPORTED" signal. Where the
edge-like (SUPPORTED) subset is large enough to test it (XES3G5M, Eedi), it decays too. Pairs share
items, and the B-item bootstrap does not absorb A-item dependence, so intervals may be narrow.
Output: `out/lag_bands.json`.

**Limitation (2026-09-24): Eedi's lags are between last answers.** Eedi keeps only each learner's
**latest** answer to a question (Wang et al. 2020, s2.1: "when a student has multiple answer records
to the same question, we keep the latest answer record"), at minute resolution. So first touch,
outcome at first touch, first pass and A-before-B order are all read from last answers: a question a
learner re-answered moves later and carries its re-answer outcome, which leans correct. Earlier
attempts are not in the release and nothing can restore them, so this is recorded rather than fixed
(`shared/corpus.Eedi`). The Eedi row (D -0.048 [-0.052, -0.043], DECAYS; DECAYS on 2,504 supported
pairs) therefore measures lag between the latest answers to A and B, with outcome at the latest
answer, not lag from first exposure; it is one of the four DECAYS behind LAG-DEPENDENT, and without
it the verdict still rests on three answerable corpora that all decay (ASSISTments, XES3G5M, EdNet).

**Rerun (2026-09-25): ASSISTments and EdNet after the loader fixes.** ASSISTments now scores partial
credit as incorrect instead of dropping it, and EdNet drops questions tagged `-1` (no KC). ASSISTments
reproduces exactly. For EdNet: 141 items (was 142) and 6,170 both-readable pairs (was 6,108). D moves
from −0.014 [−0.022, −0.006] to −0.015 [−0.022, −0.007], still DECAYS. The supported subset goes from
50 pairs to 72, still UNRESOLVED. The verdict stays LAG-DEPENDENT.
