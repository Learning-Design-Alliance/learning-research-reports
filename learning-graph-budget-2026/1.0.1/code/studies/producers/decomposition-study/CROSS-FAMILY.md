# Do different model families agree on a domain's capabilities? More diverse, but completeness stays matching-limited

**Status: run 2026-09-25/26 as pre-registered (14d516b); results under Result below.** The design,
matchers, estimand, predictions, verdict strings and what each would mean for Paper 1 are the module
docstring of [`cross_family.py`](cross_family.py), written before any proposal call of this study.

## What it asks

Paper 1 argues that capture–recapture over repeated runs of one model over-certifies completeness.
On this domain, eight runs of one model named 9 of the 11 reference capabilities and missed the same two
every time, which Chao2 cannot see. The paper's remedy is independent contributors. The human version
of that remedy is [`PROTOCOL.md`](PROTOCOL.md), which is waiting for lists. This study tests the
model-only version:

- One proposal from each of 10 model families, plus two same-model repeats, all on the frozen prompt
  and topic used for `model-runs/M1–M8`.
- Every list matched to the 11-capability reference and to each other list. Two matchers do the
  matching, and both are calibrated on the 2,811 labelled CTA pairs before use.
- Chao2 over reference-matched proposals, compared with the share of the 11 the pool actually
  recovers. This is done for the cross-family pool, for M1–M8, and for all same-size subsets of each,
  with the calibrated matching error carried through as an interval.

## Pre-registered verdicts

| | strings |
| --- | --- |
| V1 calibration (each pool) | `CROSS-FAMILY POOL CALIBRATED` / `STILL OVER-CERTIFIES` / `UNDER-CERTIFIES` / `MATCHING-LIMITED` (same bands for M1–M8, ±0.15) |
| V2 comparison at k = 8 | `PREDICTION CONFIRMED` / `REFUTED` / `INCONCLUSIVE` (predicted: M1–M8 over-certify more) |
| V3 independence | `CROSS-FAMILY MORE DIVERSE` / `LESS DIVERSE` / `NO FAMILY EFFECT DETECTED` (Sørensen, list bootstrap) |
| V4 blind spots | `CROSS-FAMILY RECOVERS WHAT ONE MODEL MISSES` / `PARTIAL RECOVERY` / `SHARED BLIND SPOT` |
| gates | `MATCHER NOT CALIBRATED`, `POOL TOO SMALL` |

## What phase 1 ran

- `python3 cross_family.py --synthetic` ([`out/cross-family-synthetic.json`](out/cross-family-synthetic.json)),
  no model call:
  - **Detection floor cleared.** On 11 items, Chao2 separates independent from same-model-like pools:
    within ±0.15 in 98% of independent worlds, and above +0.15 in 87% of correlated ones.
  - **Shared blind spots also cause over-certification.** A low-κ pool whose members share a blind spot
    over-certifies too, by +0.18.
  - **The matching-error interval covers but is wide.** It contains the true error in 83–97% of planted
    worlds. It is 0.35–0.56 wide under a noisy judge, so `MATCHING-LIMITED` is the expected verdict
    unless the judge's miss rate is near 0.10.
  - **Detection limit for V3.** The list bootstrap detects a Sørensen difference of 0.12 or more.
  - **A first design was replaced.** It drew each pair's truth independently and under-covered in
    correlated worlds, so it was replaced before any real call.
- `python3 cross_family.py --dry-run` ([`out/cross-family-dryrun.json`](out/cross-family-dryrun.json)):
  - **Roster.** The slugs and prices were checked against OpenRouter's public listing, and the cost
    estimate came out at $1.9 expected and $6.6 worst case, against a $15 cap.
  - **Probe 1, the judge:** a chat call to the judge model passed the account's data-policy guardrail.
    Its slug, served model, provider, generation id, request and cost were logged.
  - **Probe 2, the embedder:** an embedding call to the first-choice embedder was refused by that
    guardrail. That embedder is dropped, and the guardrail is not routed around.

## Reproducing

```
python3 cross_family.py --synthetic   # no model call
python3 cross_family.py --dry-run     # roster, cost estimate, two routing probes
python3 cross_family.py run           # phase 2 (after this file and the script are committed)
python3 cross_family.py analyse       # re-analyse committed outputs, no model call
```

## Result (run 2026-09-25/26 as pre-registered at 14d516b; spend $2.48)

Output: [`out/cross-family-result.json`](out/cross-family-result.json); raw proposals with model slug,
served model, provider, request and timestamp in [`cross-family-runs/`](cross-family-runs/); every judge
reply in [`cross-family-judgements/`](cross-family-judgements/).

**Pool.** Ten families answered: Google, OpenAI, Anthropic, Meta, Mistral, DeepSeek, Z-AI (GLM),
Moonshot (Kimi), Cohere, Xiaomi, plus within-family repeats for Google and DeepSeek. Qwen and xAI were
refused by the account's data-policy guardrail (not routed around); the reserve families filled the pool.

**Matchers.** The judge (`minimax/minimax-m3`, outside the pool) passed calibration on the 2,811
labelled CTA pairs: κ 0.856 strict, 0.896 lenient, synonym-miss 0.20, false merge 0.00. The embedding
matcher (`perplexity/pplx-embed-v1-4b`) passed too: held-out κ 0.732 strict, synonym-miss 0.17, but it
promotes 26% of OVERLAPPING pairs to SAME. Both are calibrated against one model family's labels, not
ground truth. 2 of 91 judge replies could not be parsed and are reported missing; the analysis's
bootstrap was fixed to skip them as its point estimates already did (disclosed in the script).

| | judged matcher | embedding matcher |
| --- | --- | --- |
| Sørensen, cross-family vs same-model (M1–M8) | 0.283 vs 0.642 | 0.386 vs 0.787 |
| Chao2 error, cross-family pool (claimed − actual, interval) | +0.27 [+0.18, +0.74] | +0.13 [+0.09, +0.60] |
| Chao2 error, same-model runs | +0.09 [−0.12, +0.56] | +0.45 [+0.55, +1.30] |
| reference capabilities no family names | 3 of 11 | 2 of 11 |

Pre-registered verdicts: V3 **CROSS-FAMILY MORE DIVERSE** under both matchers (the Sørensen difference
interval excludes zero in both). V1 cross-family: STILL OVER-CERTIFIES (judged) / MATCHING-LIMITED
(embedding); same-model: MATCHING-LIMITED (judged) / STILL OVER-CERTIFY (embedding). V2 at k = 8:
INCONCLUSIVE (judged) / PREDICTION CONFIRMED (embedding). V4: SHARED BLIND SPOT (judged) / PARTIAL
RECOVERY (embedding). V5: **MATCHERS DISAGREE**.

**Reading.**
- What holds under both matchers: different model families agree far less than repeated runs of one
  model (Sørensen roughly halves), so family diversity does what the edge results predicted.
- Every point estimate is positive: Chao2 over-states completeness for every pool under every matcher.
  But which pool errs more depends on the matcher, and the intervals are wide, so no pool yields a
  completeness estimate that can be trusted. That is the matching limit completeness_nodes.py predicted,
  now measured on real proposals.
- No family, and no same-model run, names the terminal capability "subtract whole numbers of any size";
  under the judged matcher no family names single borrowing in any column either. A shared blind spot
  across families is possible, and a diverse pool is not a remedy for it.
- Per-proposer recall of the 11 reference capabilities is low (0–7 strict), so the reference anchor
  rests on few recovered items.

**For Paper 1 (as fixed in advance):** proposer diversity is necessary (model family matters) but not
sufficient: node-level capture–recapture on real proposals is matching-limited, over-states completeness
at every point estimate, and cannot see a blind spot every proposer shares.
