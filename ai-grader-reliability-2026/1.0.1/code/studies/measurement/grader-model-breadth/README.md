# Paper VI's model coverage: frontier models, reasoning on/off, the configuration record, learners

**Status: RUN 2026-10-05.** Pre-registered at 5f3ceca before any model call; floor and pricing at c999185 before any real run. Plan, thresholds and verdict strings
below were fixed in 5f3ceca; results are below the line and the plan above it is not rewritten.

## What is asked

Maintainer review 1 of Paper VI (`research/readiness/ai-grader-reliability-2026/maintainer-review-1.md`):

- "across 3 LLM models from 2 providers" — *do we want to expand the main findings across more models?*
- *why didn't you use something like opus 5.5? or fable* / *what about thinking/reasoning vs non
  reasoning models*
- "Each model runs in its own default configuration." — *what is included in that configuration? I'm
  sure people will ask about temperature or top-p, etc.*
- "no people are assigned" — *Would it make any difference if we compared findings by individual?*

## Base

`../grader-attainment-prior/` (Q2): JorGPT, the original attainment draw (150 answers from learners
whose held-out mean is ≥ 6, 150 from < 4; 19 and 14 learners), three arms on identical work (control,
true label, the opposite tail's label), `--mode attainment-swap --n 300`, the shipped prompt (vendor
pin 277cd5085). Four models there: Gemini 3.5 Flash Lite, GPT-4.1-mini, GPT-5-mini, Qwen3-235B.
Every new run uses the same draw, arms, prompt and analysis code, so it pools into Q2's table.

## Design (full record in the `breadth.py` docstring)

**Part 1, model breadth.** In priority order (the cap rule below decides how far down the list runs):

| priority | model | route | why |
| --- | --- | --- | --- |
| 1 | Claude Opus 5.5 (`anthropic/claude-opus-5.5`) | OpenRouter, pinned to Amazon Bedrock, fallbacks off (`shared/llm.py`'s pin for the Opus line: this key's routing drops Anthropic's own endpoint) | Anthropic frontier; no Anthropic key is set |
| 4 | Llama 4 Maverick (`meta-llama/llama-4-maverick`) | OpenRouter, pinned to one host, fallbacks off | a second open-weights family (Q2's pre-registered fallback) |
| 5 | Gemini 3.1 Pro (`gemini-3.1-pro-preview`) | Google direct, as every Gemini run | Google's frontier tier; its thinking cannot be turned off |
| 6 | Claude Fable 5.1 (`anthropic/claude-fable-5.1`) or GPT-5.5 (`gpt-5.5`, OpenAI direct) | as above | only if the budget left exceeds 1.3 × its probed cost |

Each runs at its own defaults as every Paper VI model did: no temperature, top-p or token limit set by
the harness except OpenRouter's required `max_tokens` 16,384, OpenRouter's `reasoning: {exclude: true}`,
and the Anthropic routes' JSON mode with the schema in the prompt (`provider.ts`, the ZDR note). Those
are recorded per run, not equalised.

**Part 2, reasoning contrast** (priorities 2 and 3). Same model, draw, prompt, arms; only the
reasoning setting changes (new harness flag `--reasoning`; unset leaves every request as before):

- GPT-5-mini, `reasoningEffort` **minimal** vs **high** (OpenAI direct). Q2's run at the API default
  (medium) is reported between them.
- Gemini 3.5 Flash Lite, `thinkingLevel` **high** vs its default **minimal**, and the default
  **re-run**: default-vs-default across two runs is the null for a contrast made across runs.

dL = L(more reasoning) − L(less), paired on answers, learner-cluster bootstrap 95% / 90%. Whether the
setting took effect is read off billed reasoning tokens, which the harness now records per run.

**Part 3, configuration record.** For every model configuration in Paper VI and its re-tests: the wire
body each tree's own pinned SDK builds (`wirehook.mjs`: fetch replaced, nothing sent, prompt and schema
hashed), from the frozen snapshots `vendor/934478716/` and `vendor/584e5a91a/` and the current
harness; and for runs made here, the bodies, billed tokens and serving host recorded in each dump. No
model call. Output: a methods-section table.

**Part 4, per learner** (no new calls). On the four Q2 dumps (and new dumps once they exist):
per-learner label sensitivity L_j, its spread, and a heterogeneity test (between/within-learner
F within tail) against a **family-matched, deranged** null (learner ids re-assigned among answers to
the same question in the same tail, nobody keeping their own), plus the maintainer's suggested control
(labels flipped at random within learner: the null L_j = 0).

## Pre-registered verdicts

| part | verdict | rule |
| --- | --- | --- |
| 1, per model | Q2's, unchanged | `PRIOR` / `BIAS` / `MIXED` / `UNRESOLVED` / `NO-LABEL-EFFECT` / `REVERSED` (`../grader-attainment-prior/README.md`, revision 3) |
| 1, all models | `<shared>` or `MIXED-ACROSS-MODELS` | as Q2 |
| 1, frontier (Opus 5.5, Gemini 3.1 Pro, Fable 5.1, GPT-5.5: whichever ran) | `PERSISTS-AT-FRONTIER` | every frontier model's L 95% interval > 0 |
| | `ABSENT-AT-FRONTIER` | every frontier model's L 90% interval inside ±0.15 |
| | `MIXED-AT-FRONTIER` | otherwise |
| 2, per model | `REASONING-RAISES` / `REASONING-LOWERS` | dL 95% interval above / below 0 (signed: raises = more label-dependent) |
| | `NO-REASONING-EFFECT` | otherwise, with dL 90% interval inside ±0.15 |
| | `INCONCLUSIVE` | otherwise |
| | `NOT-A-CONTRAST` | the two runs bill the same reasoning tokens per call (within 1), whatever dL says |
| 4, per model | `HETEROGENEOUS` / `NO-DETECTABLE-HETEROGENEITY` | deranged-null p < 0.05 / otherwise, the latter always stated with the floor's minimum detectable τ |
| 4, across models | `<shared>` or `MIXED` | |

Margin 0.15 marks ≈ 40% of the smallest Q2 L (0.37). Reported beside, not as, verdicts: per-tail L,
per-tail drift and control signed error under each reasoning setting; per-learner L_j quantiles, share
negative against the null, correlation with held-out attainment, agreement of L_j across models.

## Detection floor (before any real number)

- **Reused:** Q2's floor for the per-model verdict (`../grader-attainment-prior/out/floor.json`,
  revision 3: every world passes except OVERSHOOT at 0.78, which misses by declining). Valid because
  draw, arms and instrument are identical; it was shaped to Gemini's calibration, and a harsher grader
  resolves its reference points more easily.
- **New, dL:** synthetic graders on the real draw with Q2's corpus-shaped base, 200 replicates per
  world. NULL (L 0.45 in both runs): a signed call in ≤ 10%, and NO-REASONING-EFFECT in ≥ 80% for the
  equivalence verdict to be reachable; if that half fails, dL is read only as an interval ("no change
  larger than X"), as Q2 read Q4. RAISE (0.45 → 0.75) and LOWER (0.45 → 0.15): the planted sign in ≥ 80%.
- **New, heterogeneity:** τ = 0 and τ = 0 with question-level heterogeneity (sd 0.3) must each give
  p < 0.05 in ≤ 10% (the second is the family matching's job); detection reported at τ = 0.2, 0.3, 0.5,
  and the smallest detected in ≥ 80% is the stated minimum detectable τ.

All are smoke checks written and scored by one session, and are reported as such.

## Cost and the cap

Cap **$60 total**, counted as OpenRouter's reported cost plus billed tokens × list price for direct
OpenAI and Google calls (the harness now records tokens). Before each full run, a 10-answer pricing
probe (`--mode schema-probe`, the seed-7 stratified draw, prints only schema compliance and tokens, no
scores) projects its cost. Prior estimate from Q2's Qwen tokens (~2.5k in, ~0.4k out per call; 900
calls a run): Opus 5.5 ≈ $17; GPT-5-mini minimal ≈ $1.5, high ≈ $7; Gemini lite high ≈ $5 and the
re-run ≈ $1.5; Llama ≈ $1; Gemini 3.1 Pro ≈ $20; Fable 5.1 ≈ $42; GPT-5.5 ≈ $50. A run starts only if
spend so far + its projection × 1.3 ≤ $60, in priority order; a skipped run is reported as skipped by
the cap. A run that trips the harness's 35% failure guard is reported as failed, not replaced.

## Data

JorGPT (`jorgpt-answers` in `data/data-sources.json`), read only by the harness. Dumps and wire
captures stay in the session scratchpad; only `out/*.json` aggregates are committed. The outcome is a
grader's mark on fixed work (outcome-timing tag `not-a-learner-outcome`).

## Floor and pricing record (before any real run)

**Floor: PASS** (`out/floor.json`, 200 replicates per world). dL: RAISE and LOWER called with the
planted sign in 96% each; under NULL a signed call in 6.5% (13/200). **The equivalence half fails**
(NO-REASONING-EFFECT in 36% under NULL), so, as pre-registered, `NO-REASONING-EFFECT` is unreachable
and dL is read as an interval: "no change larger than X". Heterogeneity: false positives 4% at τ = 0
and 6% with question-level heterogeneity sd 0.3 (the family matching holds); detection 36% at
τ = 0.2, 67% at τ = 0.3, 100% at τ = 0.5. **Minimum detectable τ: 0.5** marks (between-learner SD of
the label effect); a `NO-DETECTABLE-HETEROGENEITY` says only that τ is probably below about 0.3–0.5.

**Pricing probes** (10 answers each, seed-7 stratified draw, no scores read; list prices):

| run | tokens per call in / out (reasoning) | projected 900 calls |
| --- | --- | --- |
| Opus 5.5, Bedrock pin | 2,261 / 944 (0) | $25 (OpenRouter-reported $0.28 for 10) |
| GPT-5-mini, effort minimal | 1,335 / 658 (0); 1 of 10 failed schema | $1.5 |
| GPT-5-mini, effort high | 1,335 / 5,393 (4,474) | $10 |
| Gemini 3.5 Flash Lite, thinking high | 1,046 / 1,875 (1,642) | $4.5 |
| Gemini 3.5 Flash Lite, default (minimal), re-run | 1,046 / 291 (0) | $0.9 |
| Llama 4 Maverick, Parasail pin | 1,016 / 312 (0) | $1 |
| Gemini 3.1 Pro preview | 1,046 / 1,546 (1,184) | $19 |

Probes cost about $0.5. Priorities 1–4 project to ≈ $43. Gemini 3.1 Pro would then need
$43 + 1.3 × $19 = $67 > $60, so **by the pre-registered rule it is skipped by the cap**, as are Fable
5.1 (~$60 alone at Opus's token counts × 2.5) and GPT-5.5. If the first four come in under projection
the rule is re-applied to Gemini 3.1 Pro with the actual spend.

---

## Results

Six new runs of `--mode attainment-swap --n 300` on the Q2 draw: Opus 5.5 (0 of 900 gradings
failed), Llama 4 Maverick (0), Gemini 3.5 Flash Lite thinking high (0) and default re-run (0),
GPT-5-mini effort minimal (92 of 900 failed schema validation, **223 of 300 answers complete in all
three arms**; failures spread evenly over arms and tails, 14–17 per arm and tail, one learner lost),
GPT-5-mini effort high (3 timeouts, 297 complete). Actual spend came in at the projection, so the
rule re-applied left Gemini 3.1 Pro, Fable 5.1 and GPT-5.5 **skipped by the cap**. **Spend: $42.68**
of $60 (`out/spend.json`, `spend.py`): Opus $24.78 (OpenRouter-reported), GPT-5-mini high $9.82,
Gemini high $4.41, GPT-5-mini minimal $1.44, Gemini re-run $0.94 (tokens × list price), Llama $0.56,
probes $0.73. Aggregates: `out/models.json`, `out/reasoning.json`, `out/learners.json`,
`out/config.json`, `out/r_check.json`. All intervals are learner-cluster bootstrap 95%.

**Checked, not assumed.** The Gemini re-run reproduces Q2's Gemini L to 0.01 (+0.36 against +0.37;
dL −0.01 [−0.07, +0.05]), so a contrast made across two runs on this draw carries about ±0.07 of
run-to-run noise. The reasoning settings took effect by the bills: GPT-5-mini 0 reasoning tokens per
call at minimal, ~813 at the API default (10-call probe), 4,424 at high; Gemini lite 0 at minimal,
1,591 at high. Opus billed 12 reasoning tokens per call on average (10,549 over 900) with nothing
asked for. Every live request body matched its offline wire capture. A first pass of the part 1 table
silently merged the Gemini Q2 run and its re-run under one key (same model id); caught on reading,
fixed (`[re-run, <file>]` tags) before anything was written.

### Part 1 — model breadth: `PERSISTS-AT-FRONTIER`; across all models `MIXED-ACROSS-MODELS`

| model (configuration) | L: high − low label, same work | L high / low tail | control signed error, high / low | with true label, high / low | low-tail ΔMAE | Q2 verdict (high, low) |
| --- | --- | --- | --- | --- | --- | --- |
| Gemini 3.5 Flash Lite (Q2) | +0.37 [+0.30, +0.44] | +0.42 / +0.32 | +0.20 / **+0.49** | +0.44 / +0.27 | −0.03 | UNRESOLVED (unresolved, TOWARD) |
| Gemini 3.5 Flash Lite, re-run | +0.36 [+0.29, +0.43] | +0.35 / +0.37 | +0.19 / **+0.47** | +0.40 / +0.21 | −0.02 | UNRESOLVED (unresolved, TOWARD) |
| GPT-4.1-mini (Q2) | +0.38 [+0.30, +0.46] | +0.50 / +0.26 | **−1.30** / **−0.46** | −1.22 / −0.72 | **+0.16** | MIXED (TOWARD, AWAY) |
| GPT-5-mini, default effort (Q2) | +0.52 [+0.43, +0.61] | +0.57 / +0.47 | **−0.98** / +0.08 | −0.97 / −0.44 | +0.10 | UNRESOLVED (flat, unresolved) |
| Qwen3-235B (Q2, open weights) | +0.75 [+0.69, +0.82] | +0.79 / +0.72 | **−1.52** / **−0.41** | −1.29 / −0.75 | **+0.21** | MIXED (TOWARD, AWAY) |
| **Claude Opus 5.5** (frontier) | **+0.28 [+0.23, +0.32]** | +0.30 / +0.25 | **−1.79** / **−0.83** | −1.63 / −0.94 | **+0.07** [+0.03, +0.11] | MIXED (TOWARD, AWAY) |
| **Llama 4 Maverick** (open weights) | **+0.54 [+0.42, +0.65]** | +0.51 / +0.56 | **−1.19** / **−0.40** | −0.66 / −0.42 | +0.01 | PRIOR (TOWARD, flat) |

(The reasoning configurations of GPT-5-mini and Gemini are in Part 2; with them the run count is ten.)

1. **The label moves the grade on identical work on every model tried: six models, four vendors,
   five families, frontier included.** Opus 5.5 shows the smallest effect (+0.28; a false low label
   costs strong work 0.30 points), with the tightest interval of any model. Llama 4 Maverick, a second
   open-weights family, sits mid-range (+0.54). The effect is not a small-model artefact and not a
   property of one post-training lineage.
2. **Opus is the harshest grader in the set** (−1.79 on strong work, −0.83 on weak; control QWK
   0.682, MAE 1.73 against 0.706–0.809 and 1.27–1.59 for the others) and, like GPT-4.1-mini and Qwen,
   its low label pushes weak work further from the teacher (low-tail MAE +0.07). Llama is the first
   default-configuration model to read PRIOR: the label pulls its harsh high tail up toward the
   teacher and leaves the low tail flat. Direction relative to the teacher remains a property of each
   model's own calibration, as Q2 found.

### Part 2 — reasoning: on GPT-5-mini `REASONING-LOWERS` (reasoning halves the effect); on Gemini lite no signed effect

| contrast (everything else fixed) | reasoning tokens per call | L less → more | dL [95%] | verdict |
| --- | --- | --- | --- | --- |
| GPT-5-mini, minimal → high (n = 220 paired) | 0 → 4,424 | +1.05 → +0.54 | **−0.51 [−0.62, −0.39]** | `REASONING-LOWERS` |
| GPT-5-mini, minimal → default/medium (n = 222) | 0 → ~813 | +1.04 → +0.53 | **−0.51 [−0.65, −0.37]** | `REASONING-LOWERS` |
| GPT-5-mini, default → high (n = 294) | ~813 → 4,424 | +0.53 → +0.52 | −0.01 [−0.10, +0.10] | no signed effect; no change larger than 0.10 |
| Gemini 3.5 Flash Lite, minimal → high (n = 300) | 0 → 1,591 | +0.36 → +0.41 | +0.05 [−0.06, +0.14] | no signed effect; no change larger than 0.14 |
| null: Gemini lite default, Q2 run → re-run | 0 → 0 | +0.37 → +0.36 | −0.01 [−0.07, +0.05] | no signed effect (the across-run null) |

(`NO-REASONING-EFFECT` was unreachable by the floor, so unsigned results are read as intervals, as
pre-registered. The ~813 is from a 10-call probe; Q2's dump predates the usage record.)

Signed: **turning GPT-5-mini's reasoning off doubles its label sensitivity** (+1.04, the largest of
any configuration here; a false low label costs strong work 1.16 points), in both tails (dL −0.52
high, −0.50 low). Any reasoning buys the reduction; more than the default buys nothing further. On
Gemini lite, thinking changes the grader's calibration (control signed error −0.33 in the high tail,
−0.18 in the low) but not its dependence on the label. So reasoning is not a fix in general: on one
model it halves the effect, on the other it does nothing, and the reasoning-on GPT-5-mini still moves
identical work by half a point. GPT-5-mini at minimal also reads PRIOR (TOWARD in both tails): at that
setting it is generous to weak work (+0.52) and the label pulls it back, the calibration point again.

| configuration | L [95%] | control signed error, high / low | with true label, high / low | Q2 verdict |
| --- | --- | --- | --- | --- |
| GPT-5-mini, minimal | +1.04 [+0.90, +1.18] | −0.68 / +0.52 | −0.41 / −0.20 | PRIOR (TOWARD, TOWARD) |
| GPT-5-mini, high | +0.52 [+0.44, +0.61] | −1.12 / −0.04 | −1.10 / −0.53 | UNRESOLVED (flat, unresolved) |
| Gemini lite, thinking high | +0.41 [+0.31, +0.50] | −0.14 / +0.29 | +0.03 / −0.03 | UNRESOLVED (unresolved, TOWARD) |

**Accuracy (Q4's instrument, reported beside L; not a pre-registered verdict of this study).** Three
runs show a QWK gain from the true label whose 95% interval excludes 0: Opus +0.029 [+0.013,
+0.043], Llama +0.046 [+0.010, +0.085], GPT-5-mini minimal +0.039 [+0.001, +0.074]; GPT-5-mini high
shows an MAE loss (+0.10 [+0.03, +0.19]). Pearson r moves on none of the nine runs checked (Δr from
−0.015 to +0.014, every interval spanning 0; `r_check.py`): the label moves where marks land, which on
a harsh, compressed grader partly corrects calibration, not what the grader perceives.

### Part 3 — what "its own default configuration" sent (`out/config.json`)

Captured from each tree's own pinned SDK (`wirehook.mjs`, nothing sent; `capture_config.py`) and,
for this study's runs, from the live request bodies the harness now records, which matched. **No run
in Paper VI or its re-tests sent a temperature, a top_p, a seed or, on a direct API, an output-token
limit**: each provider's defaults applied. For the methods section:

| model | where in Paper VI | code / SDK | endpoint | temperature, top_p, seed | output-token cap | reasoning sent | structured output sent | host |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Gemini 3.5 Flash Lite ("LITE") | every ablation arm, history, attainment, pooling | 934478716, 584e5a91a (ai 6.0.233, @ai-sdk/google 3.0.98); re-tests: current harness (ai 5.0.261, google 2.0.97) | Gemini API `generateContent` (v1beta) | not sent | not sent | `thinkingLevel: "minimal"`, `includeThoughts: false` (0 thought tokens billed) | `responseMimeType: application/json` + `responseSchema` (same schema hash in every tree) | Google, direct |
| Gemini 3.7 Flash ("STANDARD") | tier comparison, pooling's standard pass | 934478716 | same | not sent | not sent | **none sent**: the model's default thinking | same | Google, direct |
| GPT-4.1-mini | attainment (original) | 584e5a91a (ai 6.0.233, @ai-sdk/openai 3.0.86) | OpenAI Responses `/v1/responses` | not sent | not sent | not applicable | `json_schema`, **`strict: true`** | OpenAI, direct |
| GPT-4.1-mini | Q2 re-test | current harness (@ai-sdk/openai 2.0.127) | same | not sent | not sent | — | `json_schema`, **`strict: false`** | OpenAI, direct |
| GPT-5-mini | attainment (original) | 584e5a91a | same | not sent | not sent | **none sent**: API default effort (medium; ~813 reasoning tokens per call measured) | `json_schema`, `strict: true` | OpenAI, direct |
| GPT-5-mini | Q2 re-test; this study (minimal, high) | current harness | same | not sent | not sent | none / `reasoning.effort: "minimal"` / `"high"` | `json_schema`, `strict: false` | OpenAI, direct |
| Qwen3-235B-A22B-2507 | Q2 re-test | current harness | OpenRouter `/api/v1/responses` | not sent | `max_tokens: 16384` | `reasoning: {exclude: true}` | `json_schema`, `strict: false` | DeepInfra (fp8), pinned, `allow_fallbacks: false` |
| Claude Opus 5.5 | this study | current harness | OpenRouter `/api/v1/responses` | not sent | `max_tokens: 16384` | `reasoning: {exclude: true}`; 12 reasoning tokens per call billed | **`json_object`, schema in a system message** (the zero-retention route refuses strict schemas, `provider.ts`) | Amazon Bedrock, pinned, no fallbacks |
| Llama 4 Maverick | this study | current harness | same | not sent | `max_tokens: 16384` | `reasoning: {exclude: true}` | `json_schema`, `strict: false` | Parasail (fp8), pinned, no fallbacks |
| Gemini 3.1 Pro (captured, not run) | — | current harness | Gemini API | not sent | not sent | none sent (cannot be disabled; ~1,184 thought tokens per call in the probe) | as LITE | Google, direct |

**A configuration difference the earlier re-test record missed.** The original OpenAI runs
(584e5a91a, ai 6 / @ai-sdk/openai 3.0.86) sent `strict: true`; the Q2 re-tests from the current
harness (ai 5 / @ai-sdk/openai 2.0.127) sent `strict: false`, with identical prompt text (same input
hash) and a differently serialised schema. `vendor/runtime/README.md` described the schema difference
as key order only. Non-strict decoding is the likely source of the 2–3 schema failures in the GPT
re-tests and of the 10% at minimal effort. The re-tests reproduced the original gaps (Q2: 0.35 against
0.24 for GPT-4.1-mini, 0.53 against 0.54 for GPT-5-mini), so no verdict moves, but the methods must
not call the re-test configuration identical.

Notes: the grader prompt is one user message; the only system message any route adds is the
Anthropic route's schema instruction. OpenRouter's Responses API did not echo the serving host, so
the host is guaranteed by the pin with fallbacks off (a request the pinned host cannot serve fails
rather than moving), not read back.

### Part 4 — by learner: `MIXED` (heterogeneous on 3 of 10 runs, none after Holm)

| run | learners | F (between / within) | τ̂ (between-learner SD of L) | deranged-null p | verdict | L_j range | learners above / below the sign-flip null |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Gemini lite (Q2) | 33 | 1.05 | 0.04 | 0.26 | NO-DETECTABLE | 0.00 to +0.83 | 5 / 0 |
| Gemini lite re-run | 33 | 0.98 | 0.00 | 0.49 | NO-DETECTABLE | −0.25 to +0.75 | 3 / 0 |
| Gemini lite, thinking high | 33 | 1.14 | 0.10 | 0.16 | NO-DETECTABLE | −0.14 to +1.00 | 6 / 0 |
| GPT-4.1-mini | 33 | 1.62 | 0.15 | **0.012** | HETEROGENEOUS | −1.00 to +0.91 | 7 / 0 |
| GPT-5-mini (default) | 33 | 1.07 | 0.06 | 0.41 | NO-DETECTABLE | 0.00 to +1.00 | 9 / 0 |
| GPT-5-mini, minimal | 32 | 1.70 | 0.26 | **0.008** | HETEROGENEOUS | 0.00 to +1.83 | 18 / 0 |
| GPT-5-mini, high | 33 | 1.38 | 0.14 | 0.13 | NO-DETECTABLE | 0.00 to +2.00 | 8 / 0 |
| Qwen3-235B | 33 | 0.86 | 0.00 | 0.61 | NO-DETECTABLE | +0.40 to +1.08 | 23 / 0 |
| Opus 5.5 | 33 | 1.28 | 0.06 | 0.20 | NO-DETECTABLE | 0.00 to +1.00 | 9 / 0 |
| Llama 4 Maverick | 33 | 1.78 | 0.26 | **0.013** | HETEROGENEOUS | −1.50 to +1.77 | 13 / 0 |

Holm across the ten runs leaves none below 0.05 (smallest 0.080). The floor's minimum detectable τ is
0.5 (67% power at 0.3), so a NO-DETECTABLE row says τ is probably below about 0.3, not that it is 0.

What this says about "no people are assigned":

1. **Nobody is helped by a low label beyond chance.** Under the maintainer's control (labels flipped
   within learner), no learner on any run has an effect resolvably below zero, while 3–23 of 33
   learners per run are individually above it. Learners with a negative point estimate are 0–12%, at
   or just above what the homogeneous-effect null produces (0–12%); the most negative values come from
   one-answer learners (e.g. −1.00 on a single answer for GPT-4.1-mini).
2. **The size varies modestly by learner on some graders.** Where heterogeneity is detected
   (GPT-4.1-mini, Llama, GPT-5-mini without reasoning) its SD is 0.15–0.26 marks against mean effects
   of 0.38–1.04, under the family-matched control that keeps each learner's questions, so it is not
   question mix. The pooled figure does not hide a group moved the other way.
3. **Part of that spread is the size of the label, not the learner.** Within tail, L_j rises with
   how extreme the learner's own label is: Spearman with held-out attainment +0.40 to +0.68 in the high
   tail and −0.25 to −0.58 in the low tail on every default-configuration model except Opus (−0.21 /
   −0.07). The swap pairs each answer with the other tail's label, so a more extreme learner's answers
   face a larger label gap: a dose response, consistent with the per-label-point slope
   `../grader-label-compounding/` fitted.
4. **What is repeatable is the answer more than the learner.** Re-running Gemini gives per-learner
   L_j that correlate 0.61–0.67 with the first run while the between-learner test finds nothing on that
   model: some answers are reliably more label-sensitive than others, and that averages out within
   learner. Across different models L_j agree weakly and unevenly (question-residualised Spearman
   −0.34 to +0.61; Opus agrees with no other model).

Revision recorded (reported-only statistic): cross-model agreement was first computed against a
learner permutation within tail; a question-matched derangement null was tried next and dropped
because its null sat below zero (median −0.20 on one pair: in strata of two or three answers a
derangement hands a learner's own deviation to the others). The reading uses d residualised on
(tail, question) with the learner-permutation null; raw and residualised are both in
`out/learners.json`.

## What this means for Paper VI

- **"Across 3 LLM models from 2 providers" becomes six models from four vendors and five families,
  including Anthropic's frontier model and two open-weights families, plus three reasoning
  configurations**, and the identical-work label effect holds on every one (L +0.28 to +0.75 at
  defaults; +1.04 with GPT-5-mini's reasoning off). Suggested sentence: *the label effect was present
  on every model tried, from small fast models to a frontier one; the frontier model showed the
  smallest effect (+0.28 points), not none.* Direction relative to the teacher stays model-dependent
  (`MIXED-ACROSS-MODELS`).
- **Opus 5.5 / Fable.** Opus 5.5 was run. Fable 5.1 and Gemini 3.1 Pro were not, by the pre-registered
  $60 cap; the paper should say so rather than imply coverage.
- **Reasoning.** *On GPT-5-mini, turning reasoning off doubled the label effect (+0.52 → +1.04) and
  any reasoning restored it; on Gemini 3.5 Flash Lite, thinking changed the grader's calibration but
  not its label effect.* Reasoning is not a remedy: reasoning-on configurations still move identical
  work by 0.4–0.5 points.
- **"No accuracy gain" needs a further restatement (headline correction).** On three new runs the
  true label raises QWK by 0.03–0.05 with intervals clear of zero (Opus, Llama, GPT-5-mini at
  minimal), while Pearson r moves on none. So: *the label does not improve what the grader perceives
  (r unchanged on every model), but on harsh graders it shifts marks toward the teacher's and can buy
  a small QWK gain, which a label-blind calibration would also buy.* The architectural argument
  stands; "no accuracy is bought" does not hold as written on every model.
  `cooling_off.last_headline_correction` is set in this commit.
- **Methods: replace "each model runs in its own default configuration"** with the configuration
  table above, and disclose that the OpenAI re-tests used non-strict structured output where the
  originals were strict. Draft text:

  > **Models and configuration.** Each grader received the production grading prompt as a single
  > user message with no sampling parameters: no temperature, top-p, seed or output-token limit was
  > set, so each provider's defaults applied. Gemini 3.5 Flash Lite (LITE) ran with thinking at its
  > minimum ("minimal"; no thought tokens billed), the setting the product uses for high-volume
  > grading; Gemini 3.7 Flash (STANDARD) and GPT-5-mini ran at their default reasoning. Output was
  > constrained by each API's structured-output mode: a response schema (Gemini), a JSON schema
  > (OpenAI; strict in the original runs, non-strict in the re-tests), and JSON mode with the schema
  > given in a system message for Claude, whose zero-retention route refuses strict schemas. Models
  > reached through OpenRouter (Qwen3-235B-A22B-2507, Llama 4 Maverick, Claude Opus 5.5) were pinned
  > to one serving host with fallbacks disabled (DeepInfra fp8, Parasail fp8, Amazon Bedrock) and
  > given the 16,384-token output cap the router requires. We did not equalise settings across vendors,
  > since there is no common scale for "effort" and defaults are what a platform deploys; instead we
  > varied the one setting most likely to matter, reasoning, within a model (GPT-5-mini at minimal,
  > default and high effort; Gemini 3.5 Flash Lite at minimal and high thinking), everything else
  > fixed. **Why these tiers.** The original arms used the small tiers a product calls at grading
  > volume. The re-tests added a third vendor's frontier model (Claude Opus 5.5) and two open-weights
  > families (Qwen3, Llama 4), so that the label effect could not be put down to model size, vendor or
  > one post-training lineage. Gemini 3.1 Pro and Claude Fable 5.1 were not run, for cost.

- **"No people are assigned"** is defensible and does not hide a reversal: no learner is helped by a
  low label beyond chance on any model; where the effect's size varies by learner its SD is 0.15–0.26
  marks, and part of it is the size of the label gap. One sentence and a pointer to Part 4 suffice.

## Decision (2026-10-05): the top frontier tiers stay unrun, and the paper says why

The maintainer decided not to run Gemini 3.1 Pro, Fable 5.1 or GPT-5.5. Their cost per grade is out of
reach for anyone applying these results to routine grading, which is the setting the paper is about,
and Opus 5.5 already represents the frontier (`PERSISTS-AT-FRONTIER`). Paper VI states this as a scope
decision with the arithmetic, not as a gap. Cost per grade, from this study's measured spend (900
gradings a run) or, where not run, its pricing probe or projection:

| model | cost per grade | 8,000 grades (e.g. 200 students × 40 responses) | source |
| --- | ---: | ---: | --- |
| Llama 4 Maverick | $0.0006 | $5 | measured |
| Gemini 3.5 Flash Lite (LITE, the shipped tier) | $0.0010 | $8 | measured |
| GPT-5-mini, reasoning minimal | $0.0016 | $13 | measured |
| Claude Opus 5.5 | $0.028 | $220 | measured |
| Gemini 3.1 Pro | ~$0.021 | ~$170 | 10-answer pricing probe |
| GPT-5.5 | ~$0.055 | ~$440 | projection, not probed |
| Claude Fable 5.1 | ~$0.069 | ~$550 | projection (Opus 5.5's measured tokens × Fable's list price, corrected 2026-10-06 from $0.067 / $530); not reachable under zero data retention (`../grader-fable/`) |

List prices on 2026-10-05; projections exclude the reasoning-token variance that made GPT-5-mini at
high effort cost about 7× its minimal setting.

**Update (2026-10-06): the Fable 5.1 test was approved and is blocked.** The maintainer then approved
one low-cost test of Fable 5.1 (100 answers, true and swapped labels, $30 cap; pre-registered in
`../grader-fable/`). It could not run: all four OpenRouter hosts that serve Fable 5.1 (Anthropic, Amazon
Bedrock, Google Vertex, Azure) are excluded by the account's zero-data-retention setting
(`zdr-violation-by-account`), and that setting was not relaxed. No grading was made and nothing was
spent. Gemini 3.1 Pro and GPT-5.5 stay unrun by the decision above; Fable 5.1 stays unrun for cost and
reachability. `PERSISTS-AT-FRONTIER` rests on Opus 5.5 alone, unchanged.
