# Does Paper VI's label effect persist on Claude Fable 5.1?

**Status: RUN under Amendment 1 (Fable 5.1 as an agent), 2026-10-06: `PERSISTS`, L = +0.31 [+0.19, +0.45]; see the end of this file.** The API route was BLOCKED 2026-10-06: no Fable 5.1 host is reachable under the account's
zero-data-retention setting, so no API grading was made and $0 was spent on it. Pre-registered at 7ccb528 (floor and deviation 1 at
cef3e95), before any paid call. The plan, thresholds and verdict strings below were fixed then; results
go below the line and the plan above it is not rewritten. Full record in the `fable.py` docstring.

**Amendment 1 (2026-10-06, committed before any agent grading):** the maintainer approved grading Fable 5.1
through Claude Code subagents instead of the blocked API. Route, every difference from the API
condition and the added rules are at the end of this file; not yet run.

## What is asked

`../grader-model-breadth/` ran Claude Opus 5.5 as Anthropic's frontier model (L +0.28 [+0.23, +0.32],
the smallest effect of any model) and left Fable 5.1, Anthropic's top tier, unrun for cost; the
maintainer then decided the top tiers stay unrun. The maintainer has since approved one low-cost test:
does the identical-work label effect persist on Fable 5.1? **Hard cap $30 total, pricing probe
included.**

## Design

| | |
| --- | --- |
| Draw | 100 answers from the Q2 attainment-swap draw (the one the Q2 and Opus 5.5 runs graded): 50 pair indices `k = sorted(numpy.random.default_rng(20261006).choice(150, 50, replace=False))`, and for each k the high-tail answer k and the low-tail answer k (the harness pairs them for the swap). 50 per tail; 17 of 19 high-tail and 13 of 14 low-tail learners; 32 questions (`out/draw.json`). |
| Arms | Two, on identical answers: true label and swapped (opposite tail's) label, so each answer is graded once under a high and once under a low label. **No control arm**, so the toward/away (prior vs bias) reading Q2 gives each model **is not available for Fable**. |
| Harness | `--mode attainment-swap --n 300 --ids <subset> --arms true,swapped` (`--ids` and `--arms` added here; labels and pairing are fixed on the full draw first, so each answer sees exactly the labels it saw in the 300-answer runs; unset, the mode behaves as before). Same prompt (vendor pin 277cd5085), harness and output-schema handling as Opus 5.5. |
| Fable configuration | `anthropic/claude-fable-5.1` via OpenRouter `/api/v1/responses`, host pinned to **Amazon Bedrock**, `allow_fallbacks: false` (as Opus 5.5; Fable's hosts on 2026-10-06: Azure, Anthropic, Amazon Bedrock, Google Vertex, all $10 / $50 per M tokens). Sent: `json_object` with the schema in a system message (the zero-retention route), `reasoning: {exclude: true}`, `max_tokens: 16384`, `usage: {include: true}`. **Not sent: temperature, top_p, seed.** Read back from the live request body in the dump. |
| Estimand | L = mean over answers of (mark under the high label − mark under the low label), out of 10. 95% interval: paired bootstrap resampling learners within tail (Q2's `cluster_index`), 4,000 replicates. Also L per tail. Answers with either arm failed are dropped and counted. |

## Pre-registered verdict (signed: positive = higher under the high label)

| verdict | rule |
| --- | --- |
| `PERSISTS` | L 95% interval above 0 |
| `PERSISTS-REVERSED` | L 95% interval below 0 |
| `NOT-DETECTED-BOUNDED` | otherwise, with the 95% interval inside ±0.10 |
| `UNRESOLVED` | otherwise |

For the model-breadth frontier verdict: `PERSISTS` keeps `PERSISTS-AT-FRONTIER` (Opus 5.5 and Fable
5.1); anything else makes it `MIXED-AT-FRONTIER`. Reported beside, not as, verdicts: L per tail; the mark
under each label against the teacher's, per tail; Opus 5.5's L on the same 100 answers (from its
existing dump, no new call) and the paired Fable − Opus difference.

## Detection floor

The Q2 / breadth floor was built at n = 300 with a control arm and does not transfer to 100 pairs, so a
synthetic floor runs on the real 100-answer subset (its learners, tails, questions), 400 replicates per
world, in two noise shapes: Q2's corpus-shaped synthetic grader (integer marks, d SD about 0.9;
conservative) and Opus 5.5's own per-answer d, centred, plus the planted effect (d SD 0.37). Worlds:
L = 0, +0.28 (Opus's effect, the smallest observed), −0.28 (direction), +0.10. **Pass** in both shapes:
a signed call under L = 0 in ≤ 10%; `PERSISTS` at +0.28 in ≥ 80% with no reversed call; `PERSISTS-REVERSED`
at −0.28 in ≥ 80%. The equivalence power (`NOT-DETECTED-BOUNDED` under L = 0) is reported, not required.
Synthetic graders written and scored by one session: a smoke check, reported as one. No paid call if it
fails.

### Floor result and deviation 1 (recorded before any paid call)

**Floor: FAIL, narrowly, in the conservative shape only** (`out/floor.json`, 400 replicates per world):

| shape (d SD) | signed call at L = 0 | `PERSISTS` at +0.28 | `PERSISTS-REVERSED` at −0.28 | `PERSISTS` at +0.10 | `NOT-DETECTED-BOUNDED` at L = 0 (equivalence power) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Q2 corpus-shaped (≈ 0.9) | 7.25% | **79.5%** (needed 80%) | **79.5%** | 21% | 0% |
| Opus 5.5-shaped (0.37) | 6.5% | 100% | 100% | 80% | 60% |

The pre-registered consequence was no paid call. **Deviation:** the run proceeds. The check that
protects a `PERSISTS` (or reversed) verdict, the false signed-call rate under no effect, passes in both
shapes (≤ 7.25%); what fails, by half a point of Monte Carlo noise (SE ≈ 2%), is power for a null in a
shape 2.4 times noisier than the closest model run. Rule fixed now, before any Fable number: an
`UNRESOLVED` is reported as "no Opus-sized effect excluded", and, if Fable's d SD exceeds 0.6, also as
"underpowered at the noise Fable showed"; a `NOT-DETECTED-BOUNDED` carries its 60% power (Opus shape).
`out/floor.json` keeps `pass: false`.

## Cost gate

10-answer pricing probe (`--mode schema-probe --n 10`, the seed-7 stratified sample, as every breadth
probe; only schema compliance, tokens and OpenRouter-reported cost read, no scores). Projection = probe
cost / 10 × 200 calls. **Run only if probe + 1.3 × projection ≤ $30**, else stop and report. The run
uses `--max-calls 220` and `--max-spend` = $30 − probe cost. Spend is OpenRouter's reported cost.
Prior estimate at Opus's token counts (2,163 in / 944 out per call) and Fable's list price: $0.069 per
grade, about $14 for 200.

## Data

JorGPT (`jorgpt-answers`), read only by the harness. Dumps stay in the session scratchpad; `out/*.json`
holds aggregates. The outcome is a grader's mark on fixed work (`not-a-learner-outcome`).

---

## Result: BLOCKED, because Fable 5.1 cannot be reached under the account's zero-data-retention setting

No verdict. **No grading was made and nothing was spent** ($0.00 OpenRouter-reported, against the $30
cap; `out/block.json`).

The pricing probe (10 answers, `--mode schema-probe`, pinned to Amazon Bedrock as Opus 5.5 was) failed
10 of 10 with the harness's class "PROVIDER: blocked by an account data/provider policy", 0 tokens
billed. One 16-token request to each host, pinned with fallbacks off, and one unpinned request all
returned the same refusal at OpenRouter's routing step, before any model ran:

> 0 endpoints out of 4 requested are available matching your guardrail restrictions and data policy
> ... ZDR violation (account settings): 4 endpoints excluded

(`failed_routing_step: "Filter by Guardrails"`, `reason: "zdr-violation-by-account"`.) Fable 5.1
(`anthropic/claude-fable-5.1`, listed as `claude-fable-5.1-20260831`) is served on OpenRouter by Azure,
Anthropic, Amazon Bedrock and Google Vertex, at $10 / $50 per million input / output tokens. **None of
the four is a zero-retention endpoint for this model**, while Opus 5.5 on Bedrock is. The
OpenRouter account's zero-retention setting is the protection over student work on that route that `provider.ts` documents (the direct Gemini and OpenAI routes run under the providers' data processing addenda without zero retention), so
it was not relaxed. Not tried, each the maintainer's decision: relaxing that setting for this test
(JorGPT is public, CC BY 4.0, so this corpus does not itself carry the student-work risk the setting
guards); a direct Anthropic key (none is set); direct AWS Bedrock with the environment's AWS credentials
(not a route this repo grades through, and OpenRouter's listing suggests Bedrock does not serve Fable
under zero retention either).

Everything else is ready: the draw (`out/draw.json`), the floor and deviation 1 (`out/floor.json`), the
harness options, and the run command (`--mode attainment-swap --n 300 --ids <ids.json> --arms
true,swapped --model openrouter:anthropic/claude-fable-5.1 --max-calls 220 --max-spend <30 − probe>`,
with `OPENROUTER_PROVIDER` set to a reachable host). If a route is approved, the probe and the cost gate
run first, unchanged, then `python3 fable.py --analyse <dump> --opus <Opus 5.5 dump> --probe-cost <usd>`.

**Cost per grade (a projection, not measured):** Opus 5.5's measured tokens per call on this draw
(2,162 in / 944 out) at Fable's list price give **$0.069 per grade**, about $550 per 8,000 grades and
$13.77 for the 200-call run (inside the cap with the 1.3 margin). The breadth table's earlier projection
($0.067, $530) is corrected to this.

## What this means for Paper VI

No headline number or verdict changes: `PERSISTS-AT-FRONTIER` rests on Opus 5.5 alone, as before, and
the reason Fable is absent changes from cost alone to cost and reachability. So
`cooling_off.last_headline_correction` in `research/readiness/ai-grader-reliability-2026/readiness.yaml`
was **not** set. The brief set it on the assumption that the frontier claim would change either way,
and it does not change when no run is made.

- **Model-breadth paragraph (methods, "Why these tiers").** Replace the last sentence, "Gemini 3.1 Pro
  and Claude Fable 5.1 were not run, for cost.", with:

  > Gemini 3.1 Pro was not run, for cost. Claude Fable 5.1, Anthropic's top tier, was approved for a
  > 100-answer test but could not be reached: none of the four hosts that serve it (Anthropic, Amazon
  > Bedrock, Google Vertex, Azure) offers it under the zero-data-retention setting the study's account
  > enforces over student work, and we did not relax that setting. At its list price it would cost about
  > $0.07 a grade, roughly 2.5 times Opus 5.5.

- **Configuration table row** (add after Opus 5.5):

  | model | where in Paper VI | code / SDK | endpoint | temperature, top_p, seed | output-token cap | reasoning sent | structured output sent | host |
  | --- | --- | --- | --- | --- | --- | --- | --- | --- |
  | Claude Fable 5.1 (attempted, not run) | — (grader-fable) | current harness | OpenRouter `/api/v1/responses` | not sent | `max_tokens: 16384` | `reasoning: {exclude: true}` | `json_object`, schema in a system message | none reachable: all four hosts excluded by the account's zero-data-retention setting |

- **Cost table row** (replaces the Fable row):

  | model | cost per grade | 8,000 grades (e.g. 200 students × 40 responses) | source |
  | --- | ---: | ---: | --- |
  | Claude Fable 5.1 | ~$0.069 | ~$550 | projection: Opus 5.5's measured tokens × Fable's list price; not reachable under zero data retention |

- **Abstract, "six models from five developers": unchanged.** Fable adds no model, so it is not counted.

- **Release 1.0.0 limitation and the breadth observation's `observability_notes`** (left for whoever
  re-cuts the article, so the records stay in step with it): "Gemini 3.1 Pro, Claude Fable 5.1 and
  GPT-5.5 were not run, a scope decision on cost per grade" becomes "Gemini 3.1 Pro and GPT-5.5 were
  not run, a scope decision on cost per grade; Claude Fable 5.1 was approved for a 100-answer test and
  could not be reached under the account's zero-data-retention setting (studies/measurement/grader-fable)".
  The article's cost-table row ($0.067 / $530) becomes the row above.

**Release record.** No per-case dump exists, so nothing is appended to
`grader-eval/analyses/per-case-dumps.sha256`, the published per-case file is not regenerated, and no
analysis or dataset entry is added to the release. Those steps belong to a run that happens.

---

## Amendment 1: Fable via Claude Code subagents

Committed **before any agent grading**; no Fable grade existed. Same text in the `fable.py` docstring.
Preparation `agent_prepare.py` (and `renderhook.mjs`), analysis `agent_analyse.py`, hashes
`out/agent-manifest.json`.

**Why.** The API route is blocked by the account's zero-data-retention setting (above), which stays. The
maintainer approved a different route: the orchestrating Claude Code session spawns subagents running
on Fable, each grading one batch of the exact prompts the harness would have sent.

**Route.**

1. *Render.* The unmodified harness runs the pre-registered API command (`--mode attainment-swap --n 300
   --ids <ids> --arms true,swapped --model openrouter:anthropic/claude-fable-5.1`, Bedrock pin) with
   `--concurrency 1` under `renderhook.mjs`: `fetch` is replaced, the harness's own provider wrapper builds
   each body exactly as for a live call (schema moved into a prepended system message, `json_object`,
   reasoning exclude, `max_tokens` 16384, usage, provider pin), the whole body is kept and nothing is
   sent. Each body is assigned to (answer, arm) by call order and checked against its content (the
   attainment line carries that arm's label).
2. *Identity with the Opus 5.5 API run* (the request `input` holds no model id, so it must be
   byte-identical; compared by the harness's own hash, sha256 of the serialised input):

   | check | result |
   | --- | --- |
   | Fable inputs = Opus 5.5 inputs for the same (answer, arm), both rendered on the current harness | 200 / 200 |
   | current harness = harness as committed with the breadth results (6265e5a), full Opus 5.5 run, 3 arms | 900 / 900 |
   | Opus 5.5 live dump's recorded wire input (sha256 `639d2116c9c9f0b5`) found among the re-rendered inputs | yes: answer 57, control arm (the only body that run recorded) |
   | the offline Opus 5.5 wire capture's first body = the re-render's first call | yes |
   | every Fable body's non-input fields = the Opus 5.5 live body's, except `model` | 200 / 200 |
   | true and swapped bodies of an answer differ only in the attainment line | 100 / 100 |

   The live run kept one body, so the byte-level match to what Opus was actually sent is direct for one
   (control-arm) prompt and, for the label arms, rests on the harness identity rows.
3. *Prompts.* `<scratch>/fable-agent/prompts/<case_id>__<arm>.json`: `{case_id, arm, label_value,
   messages, schema}` (+ `input_sha16`, and the body's other fields as `wire`).
4. *Batches.* 20 batches of 10, seed 20261007: 5 true-arm and 5 swapped-arm items per batch; 5 high and 5
   low labels shown per batch (tails 4/6 or 6/4); never both arms of one answer in a batch; random order
   within batch; opaque 8-hex item ids. Each `batch_NN.md` is the fixed preamble ("You are a grader. For
   each item below, read the instructions and the student's answer and return the JSON object the item
   asks for, exactly as specified, with no other text. Grade each item independently; do not compare
   items."), the items (`===== ITEM <id> =====`, each message verbatim under `----- message i (<role>)
   -----`, the output schema, `===== END ITEM <id> =====`) and the fixed closing line ("Return a single
   JSON array of objects {item_id, score, evaluation} in item order, and nothing else."). The wrapper text
   is checked to name nothing about the study, the label, arms or other items. `key.json` (item id →
   case, arm, label, batch, position) stays private. sha256 of every batch, the key and every prompt
   file: `out/agent-manifest.json`; `agent_analyse.py` refuses to read results if a batch or the key no
   longer matches it.
5. *Grading.* One fresh subagent per batch, handed the batch text and nothing else; its final message is
   saved verbatim to `<scratch>/fable-agent/results/batch_NN.json`. A batch whose agent returns no
   final message at all (an infrastructure failure) may be re-run once with a fresh agent; any returned
   message, parseable or not, is final. A batch whose agent read anything under `<scratch>/fable-agent/`
   (the key and prompt files reveal case and arm) is excluded (`--exclude-batches`): its items are
   missing.

**Differences from the API condition that this route cannot remove.**

| | API condition (pre-registered) | agent route |
| --- | --- | --- |
| Context before the item | the schema system message and the user message, nothing else | the agent harness's own system prompt, tool definitions and environment context, not controlled by the grader or the study |
| Message roles | API `system` and `user` roles | both messages as delimited text inside one user turn, after a fixed one-sentence preamble |
| Items per context | one | ten; within-batch order and carry-over (incl. the other items' labels) possible; balanced across arms and labels by design, not removed; an answer's two arms always in different agents |
| Structured output | `json_object` mode, schema in the system message, validated by the SDK | by instruction only; the closing line asks for `{item_id, score, evaluation}`, not the item schema's object (whose required `xapiStatements` the API model generated), and conflicts with the item's "single JSON object" instruction |
| Sampling / reasoning | no temperature, top_p or seed sent; `reasoning: {exclude: true}`, `max_tokens` 16384 | nothing known or recorded |
| Model | `anthropic/claude-fable-5.1`, Amazon Bedrock pinned, fallbacks off | whatever the session's "fable" alias serves, no host pin; recorded by the orchestrator from session metadata (e.g. `last_served_model`) as `--model-served`, or stated as not determinable |
| Accounting | tokens, served host and cost per call | none |
| Missingness | per call | correlated within a batch (one unparsed reply loses 10 items, 10 pairs) |

**Unchanged.** Draw, arms, estimand L, the paired bootstrap resampling learners within tail (4,000
replicates, seed 20261006), L per tail, and the verdicts and thresholds: `PERSISTS` (95% interval above
0), `PERSISTS-REVERSED` (below 0), `NOT-DETECTED-BOUNDED` (inside ±0.10), `UNRESOLVED` (otherwise).

**Added rules.**

- The result is reported as **"Fable 5.1 as an agent"** and is never pooled with the API runs. It is
  reported beside, not inside, the model-breadth frontier verdict, which stays on Opus 5.5 via the API.
- **Parse failures.** An item whose output does not parse, or whose `score` is not a number in [0, 10] or
  `evaluation` not a string, is missing (one enclosing code fence around the array is tolerated and
  counted; a duplicated or foreign item id is missing). The answer's pair is dropped. Missing items and
  dropped pairs are always reported. **More than 20 of the 100 answers without a complete pair →
  `UNRESOLVED`**, whatever the interval says.
- **Floor.** The floor fell just short (79.5% against 80% at Q2-shaped noise), so a
  `NOT-DETECTED-BOUNDED` or `UNRESOLVED` result is reported as **underpowered**; deviation 1's
  d SD > 0.6 flag is reported beside it.
- Opus 5.5's L on the same 100 answers (existing dump, no call) is reported beside, labelled API vs
  agent.

**Analysis self-test** (`agent_analyse.py --selftest`, synthetic agent outputs on the real key and
draw; written and scored by the same session, so a smoke check of the plumbing, not a detection floor):
planted +0.3 → `PERSISTS`, L within 0.1; −0.3 → `PERSISTS-REVERSED`; 0 → no signed call and
`underpowered_null`; a fenced reply parsed and counted; an unparsed reply, a string score, an
out-of-range score, a missing evaluation, a foreign id and a duplicated id each counted missing (15 of
15); an excluded batch → 10 pairs dropped; 25 answers missing → `UNRESOLVED` by the missing rule
(the interval alone said `PERSISTS`), 20 missing → rule not triggered; the rebuilt dump is in the
harness's attainment-swap format, rows in draw order. PASS.

Run: `python3 agent_analyse.py --scratch <scratch> --model-served "<model>" --opus
<scratch>/breadth/swap-opus55.json [--exclude-batches …]` → `out/agent-results.json`, the rebuilt dump
`<scratch>/fable-agent/swap-fable-agent.json` (its sha256 in the output, for the release's per-case-dump
record) and the agents' evaluations beside it.

---

## Result under Amendment 1 (2026-10-06): **PERSISTS**

**Fable 5.1 as an agent: L = +0.31 [+0.19, +0.45]** on 99 complete pairs, so the label effect is
present on Fable. Per tail, reported only: high +0.44 [+0.31, +0.57] (`PERSISTS`), low +0.19
[−0.06, +0.43] (`UNRESOLVED`). Per-answer d SD 0.66, between the floor's two noise shapes (0.37 and
about 0.9). Since the result is not a null, the floor shortfall does not bear on it
(`underpowered_null: false`). `out/agent-results.json`.

| | L [95%] | high tail | low tail |
| --- | --- | --- | --- |
| Fable 5.1 as an agent | **+0.31** [+0.19, +0.45] | **+0.44** [+0.31, +0.57] | +0.19 [−0.06, +0.43] |
| Opus 5.5 via the API, same 99 answers (existing dump, no call) | **+0.34** [+0.26, +0.43] | **+0.38** [+0.25, +0.51] | **+0.30** [+0.21, +0.42] |
| Fable (agent) − Opus (API), paired; route and model confounded | −0.03 [−0.19, +0.14] | +0.06 [−0.13, +0.26] | −0.11 [−0.42, +0.16] |

Mark against the teacher's, reported only. In the high tail it is −1.10 under a high label and
−1.54 under a low one. In the low tail it is −0.67 under a high label and −0.86 under a low one.
Fable marks below the teacher in both tails, as every model except Gemini does.

**Record of the run.**

- *Agents.* Twenty subagents with the `fable` model, one per batch, all spawned in one
  orchestrator turn. Each agent's own transcript records the served model as `claude-fable-5-1` for
  all 20; this was read from the transcripts, not inferred from the alias.
- *Exclusion check.* Every tool call of every agent was read from its transcript. Each agent read its
  own batch file twice, wrote its results file once and ended. Batch 03 also edited its own results
  file once. No agent read anything else, including the key, the prompts or another batch, so no
  batch is excluded.
- *Missingness.* One item of 200 was not returned (batch 13 returned 9 of 10), so 1 pair was dropped,
  leaving 99 complete. No reply was fenced, unparsed or out of range. This is far below the 20-pair
  `UNRESOLVED` rule.
- *Deviation 2, recorded after the run: how the batch reached the agent.* The amendment said
  each agent receives its batch. In fact, each agent was given the path of a copy of its batch file,
  `<scratch>/fable-blind/bNN/items.md`. The copy sat alone in its own directory, away from
  `<scratch>/fable-agent/`, which holds the key and prompts, so that a directory listing could not
  reveal them. The agent read that copy with its file tool. All 20 copies are byte-identical to the
  hashed `fable-agent/batches/batch_NN.md` in `out/agent-manifest.json`. The prompt text the model
  read is therefore the pre-registered text, but it arrived as a tool result rather than inline in the
  user turn. This adds one more difference from the API condition, of the same kind as the agent
  harness's own context (table above). It does not change the draw, the arms, the estimand or the
  verdict rule.
- *Dump.* `<scratch>/fable-agent/swap-fable-agent.json` is in the harness's attainment-swap
  format, with its sha256 in `agent-results.json` and in
  `../grader-eval/analyses/per-case-dumps.sha256`. It is published, stripped, as the 31st run
  of the release's `per-case-model-outputs.jsonl`. The agents' evaluation texts are kept privately
  beside it and are not published. `agent_analyse.py` now writes the dump in the harness's own
  serialisation (indent 2, no trailing newline), so `strip_dumps.py rebuild` reproduces it byte for
  byte. The first analysis run differed only by a trailing newline and was overwritten. Its numbers
  were identical.
- *Cost.* None was metered: the agents ran inside this session. The $30 cap was not used.

**What it means for Paper VI.** The identical-work label effect is present on Anthropic's top tier as
well as on Opus 5.5, at a similar size on the same answers. This is reported as "Fable 5.1 as an
agent", beside the cross-model table and outside its verdict. As pre-registered, the model-breadth
frontier verdict stays on Opus 5.5 via the API (`PERSISTS-AT-FRONTIER`). The low-tail reading is
unresolved on 50 answers. The toward/away reading is not available, because the run had no control
arm.
