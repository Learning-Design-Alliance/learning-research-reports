# Attainment gap: bias on identical work, or an informative prior? (Paper VI, reviewer Q2 and Q4)

**Status: RUN 2026-10-05.** Pre-registered at d44fd28, before any model call; floor record and the
Q2 instrument's revision committed at 50434ad, before any dump was read. Results are below the line;
the plan above is not rewritten.

## What is asked

Paper VI (`research/article/attainment-bias-in-llm-grading.md`, release
`ai-grader-reliability-2026` 1.0.0) says that showing an LLM grader a learner's held-out attainment
opens a gap on identical work between learners described as strong and weak (0.48 / 0.24 / 0.54 on
three models) and that the effect is "a penalty applied to students the grader is told are weak",
with "no accuracy gain". The NLP reviewer packet
(`research/readiness/reviewer-packets/nlp-data-scientist.md`) asks:

- **Q2.** The tails hold different students with different teacher marks, and the label is true. Does
  the drift move grades *toward* the teacher's mark (an informative prior) or *away* from it (bias)?
  Needs per-tail signed error with and without the label, and a swapped-label arm on identical work.
- **Q4.** Is "no accuracy gain" licensed by a ±0.02 QWK harness resolution, or does it need a paired
  interval on ΔQWK and ΔMAE with an equivalence margin fixed in advance?

Three further items ride along: an open-weights model on the attainment arm (paper placeholder 6),
paired intervals for the attempt-history arms (the abstract's "neither manipulation"), and a re-run
of JorGPT pooling read in Pearson *r* to reconcile the staged pooling claim with the 2026-09-16
Menagerie finding that QWK hid a gain.

## Design (full record in the `analyse.py` and `pooling.py` docstrings)

- **Draw.** The original attainment draw, unchanged: `attainmentDraw()` was extracted verbatim from
  `runAttainment()` in `studies/measurement/grader-eval/harness/stability.ts`, which matches app
  commit 584e5a91a. 150 cases with held-out learner mean ≥ 6, 150 with < 4 (`--n 300`; the mode's old
  default of 150 gives 75 per tail). 19 high-tail and 14 low-tail learners.
- **Arms** (`--mode attainment-swap`): control; true label (the original arm); swapped label (each
  high-tail case shown the paired low-tail case's label and vice versa). Same template, same length.
- **Prompt.** The vendored shipped prompt (`vendor/`, app 277cd5085). Diffed on 2026-10-05 against
  `prompt.ts` at 584e5a91a: with `hardened` and `nonce` off (as in every learner-context arm), and the
  harness passing an explicit string for the context, the rendered prompt text is identical. The
  response schema differs by one optional xAPI extension field (`attempt_index`) added after
  584e5a91a. Recorded, not corrected.
- **Unit.** The label is a learner property, so every interval is a learner-cluster bootstrap (4,000
  resamples, within tail). Question-cluster and case-iid intervals are reported as sensitivity only.
- **Models.** `google:gemini-3.5-flash-lite` (thinking off), `openai:gpt-4.1-mini`,
  `openai:gpt-5-mini`, each at its own defaults as in the paper; open weights:
  `openrouter:qwen/qwen3-235b-a22b-2507` pinned to the DeepInfra fp8 endpoint with fallbacks off
  (`OPENROUTER_PROVIDER=DeepInfra`). If Qwen trips the harness's failure-rate guard (35%), the
  pre-registered fallback is `openrouter:meta-llama/llama-4-maverick`, and the switch is reported.
- **History arms (Q4).** `--mode history --n 150 --seed 7` on Gemini 3.5 Flash Lite, as the paper,
  now with a per-case dump; each arm minus control with the same margins and verdict strings.
- **Pooling.** `--mode pool --n 150 --seed 7 --repeats 9` on Gemini 3.5 Flash Lite.

## Pre-registered verdicts

**Q2, per model** (learner-cluster 95% intervals). L = label effect on identical work (score under the
high label minus under the low label); dMAE_k = MAE(true label) − MAE(control) in tail k;
I_k = MAE(true label) − MAE(swapped label) in tail k, on the same answers.

| verdict | rule |
| --- | --- |
| `NO-LABEL-EFFECT` | L's interval includes 0 |
| `PRIOR` | L > 0, I_high and I_low both < 0, and no tail has dMAE_k > 0 |
| `BIAS` | L > 0, and some tail has I_k > 0 (true label less accurate than the false one on the same work) or dMAE_k > 0 (true label moves that tail away from the teacher) |
| `MIXED` | L > 0 and neither of the above |
| `REVERSED` | L < 0 |

Across models: the shared verdict, else `MIXED-ACROSS-MODELS`. The paper's "penalty on the weak" is
read separately as `LOW-TAIL-AWAY` / `LOW-TAIL-TOWARD` / `LOW-TAIL-FLAT` from dMAE_low.

Why I_k: the control grader is generous, so *any* downward push lowers MAE. A pure penalty would pass
the reviewer's check (a) in the low tail. Only the swapped arm separates a label used as information
(the true label beats the false one in both tails) from a label-keyed shove.

**Q4, per model and arm**, true label (or history arm) minus control. Margins: ΔQWK ±0.02 (the
paper's own stated resolution), ΔMAE ±0.10 points. `EQUIVALENT` if the 90% interval lies inside the
margin (TOST, α 0.05), reported as "no gain larger than X" with X the improving-side 95% bound;
otherwise `GAIN` / `LOSS` if the 95% interval excludes 0; else `INCONCLUSIVE`.

**Pooling** (JorGPT, k = 9 passes): `R-GAIN` / `R-EQUIVALENT` (90% interval inside ±0.01) / `R-LOSS` /
`R-INCONCLUSIVE` on Δr; the same strings on ΔQWK with ±0.02. `R-GAIN` with `QWK-EQUIVALENT` means
"QWK hid it" replicates on the claim's own corpus and the claim's title is wrong as written;
`R-EQUIVALENT` means the claim stands for short answers and needs scoping, not reversal.

## Detection floor

Synthetic graders on the real draws (real teacher marks, tails, labels and learner clusters; case
effect, learner effect, per-call noise and generosity, rounded onto 0–10). Attainment: five planted
worlds × 200 replicates; pass needs ≥ 80% correct verdicts in each and ≤ 10% false label effects under
NULL. Pooling: R-GAIN in ≥ 80% with per-pass noise sd 0.6, R-EQUIVALENT in ≥ 80% with none. These are
smoke checks written and scored by one session, and are reported as such.

## Budget

Estimated before any call: about 3,600 gradings in all; roughly $0.5 Gemini, $1.5 GPT-4.1-mini,
$5 GPT-5-mini (reasoning tokens), $0.5 Qwen, $1 for history and pooling: about $9, against a $40
ceiling. The harness's spend, call and failure guards stay on.

## Data

JorGPT (`jorgpt-answers` in `data/data-sources.json`, registered in this study's first commit),
read only by the harness. Per-case dumps stay in the session scratchpad; only `out/*.json` aggregates
are committed.

## Floor record: the pre-registered Q2 instrument failed its floor, and was revised before any real number was read

Model calls began after the pre-registration commit (d44fd28); their outputs sat unread on disk while
the floor ran, and `analyse.py` refuses to read a dump until `out/floor.json` passes. What happened:

- **Revision 0 (as pre-registered): FAILED.** NULL passed (193/200 correct, 3.5% false label
  effects), but PRIOR was recovered in 3 of 200 replicates (189 MIXED). Two faults. (i) It judged
  direction by MAE, which a shift of 0.2–0.5 points moves only to second order against case noise of
  ~1.5, so it had no power in any world. (ii) Against a generous control, a "prior" pulling toward a
  label below the grader's mean is indistinguishable from a downward shove by I_k.
- **Revisions 1–2**: recentring each arm on its own label-blind bias, then a tail-level
  |signed error| difference. Exploratory scans (30 replicates per world) still failed: a difference
  of absolute values swings by twice the uncertainty of the control's own tail bias, and with 14–19
  learners per tail that uncertainty is ±0.3.
- **Revision 3 (the verdict now)**: first-order quantities only, each with its learner-cluster 95%
  interval. In each tail: the drift the true label causes; the control's mean signed error (the
  reference point); the true-label arm's. **TOWARD** if the control's error is resolvably on the
  opposite side of the drift and there is no resolvable overshoot; **AWAY** if resolvably on the same
  side, or the label drives the tail resolvably past the teacher; **FLAT** if no drift;
  **UNRESOLVED** if a real drift meets a reference not resolved from 0. Model verdict: PRIOR if every
  moved tail is TOWARD, BIAS if every moved tail is AWAY, MIXED if one of each, UNRESOLVED otherwise;
  NO-LABEL-EFFECT / REVERSED from L as before. The worlds were also re-shaped to the corpus: the
  control's per-tail signed error matches the deposit's own `gemini_grade` baseline on this draw
  (+0.10 high tail, +0.40 low tail), with the deposit's learner-level error sd 0.33. Nothing from
  this study's runs was read to set them.
- **What the floor says before any real number**: on this draw the HIGH tail's direction is not
  resolvable at all — a corpus-shaped grader is only ~0.1 generous there, which 19 learners cannot
  separate from 0 — so the instrument is required to DECLINE (UNRESOLVED) on any world that moves the
  high tail, and the floor checks that it does. Only the LOW tail, where the paper's "penalty on the
  weak" claim sits, is answerable. Pass criteria: ≥ 80% of 200 replicates return the planted verdict,
  and ≤ 10% return a wrong-direction verdict.

- **Revision 3's floor result** (`out/floor.json`): every world passed except OVERSHOOT, a low-tail
  overshoot recovered in 156 of 200 replicates (0.78 against the required 0.80; Monte Carlo se about
  0.03; wrong direction 1%). `analyse.py` accepts exactly that shortfall with the limit stated: a
  low-tail overshoot is detected about four times in five. (Recorded here 2026-10-06 after
  reproduction-8; previously stated only in `analyse.py`.)

The recentred reading (what the label adds beyond a label-blind calibration constant) and the
original MAE quantities are reported beside the verdict, not as it.

---

## Results

Runs: `--mode attainment-swap --n 300` on four models (900 gradings each; failures 0, 2, 3 and 10 of
900), `--mode history --n 150 --seed 7` and `--mode pool --n 150 --seed 7 --repeats 9` on Gemini 3.5
Flash Lite. OpenAI was called directly (Node needs `NODE_USE_ENV_PROXY=1` in this sandbox; the first
GPT-4.1-mini attempt failed 30/30 on egress and was stopped by the guard before any score existed).
Qwen ran through OpenRouter pinned to DeepInfra (spend reported $0.37). Aggregates: `out/results.json`,
`out/history-q4.json`, `out/pooling.json`; floors in `out/floor*.json`. All intervals are
learner-cluster bootstrap 95%.

**Reproduction first.** The original attainment arm reproduces on the identical draw: gap 0.47 / 0.35 /
0.53 against the paper's 0.48 / 0.24 / 0.54 (drifts +0.24/−0.22, +0.08/−0.27, +0.01/−0.52 against
+0.21/−0.27, +0.03/−0.21, −0.00/−0.54). GPT-4.1-mini's gap is a little larger than published. The
attempt-history arms reproduce too: drift −0.44 (low mark), −0.16 (high mark), +0.14 and −0.24 (marks
removed), against −0.59, −0.10, +0.15, −0.20.

### Q2 — bias or prior: `MIXED-ACROSS-MODELS`

| model | L: high label − low label, same work | L in high / low tail | control signed error, high / low tail | with true label, high / low | low-tail ΔMAE | verdict (high, low) |
| --- | --- | --- | --- | --- | --- | --- |
| Gemini 3.5 Flash Lite | **+0.37** [+0.30, +0.44] | +0.42 / +0.32 | +0.20 [−0.02, +0.44] / **+0.49** | +0.44 / +0.27 | −0.03 [−0.13, +0.06] | UNRESOLVED (unresolved, **TOWARD**) |
| GPT-4.1-mini | **+0.38** [+0.30, +0.46] | +0.50 / +0.26 | **−1.30** / **−0.46** | −1.22 / −0.72 | **+0.16** [+0.07, +0.25] | MIXED (TOWARD, **AWAY**) |
| GPT-5-mini | **+0.52** [+0.43, +0.61] | +0.57 / +0.47 | **−0.98** / +0.08 [−0.16, +0.31] | −0.97 / −0.44 | +0.10 [−0.03, +0.24] | UNRESOLVED (flat, unresolved) |
| Qwen3-235B-A22B-2507 (open weights) | **+0.75** [+0.69, +0.82] | +0.79 / +0.72 | **−1.52** / **−0.41** | −1.29 / −0.75 | **+0.21** [+0.09, +0.32] | MIXED (TOWARD, **AWAY**) |

(2026-10-06, reproduction-5: GPT-4.1-mini's −0.72 and +0.25 were printed −0.73 and +0.26, rounded twice; the values are −0.7248 and +0.2547.)

What this says:

1. **The label moves the grade on identical work, in both populations, on all four models.** The
   swapped arm removes the reviewer's confound: the same answer gets +0.37 to +0.75 more under a high
   label than a low one, inside the high tail and inside the low tail separately (every interval clears
   zero; question-clustered and case-level intervals agree). A false low label costs strong students'
   identical work 0.42–0.79 points. The open-weights model shows the largest effect, so it is not a
   commercial post-training convention (placeholder 6).
2. **Whether the movement is toward or away from the teacher depends on the model's own calibration,
   not on the label.** Gemini is generous to weak work (+0.49) and the low label pulls it toward the
   teacher (TOWARD; the reviewer's suspicion is right for that model). GPT-4.1-mini and Qwen are
   already harsh on weak work (−0.46, −0.41) and the low label makes them harsher (AWAY; low-tail MAE
   worsens by 0.16 and 0.21). GPT-5-mini is unbiased on weak work (+0.08) and the label takes it to
   −0.44: away on the point estimate, UNRESOLVED by the pre-set rule because the reference is not
   resolved from 0. The pre-registered verdict is therefore `MIXED-ACROSS-MODELS`.
3. **Read after removing each arm's own label-blind calibration constant** (reported only), three of
   four models read PRIOR: these graders compress (much harsher on strong work than on weak), and the
   label's differential pushes each tail the way the compression is wrong. So the label does carry
   tail-level information the graders lack. Whether a label-blind affine calibration (shift and
   stretch, which the programme already uses) removes the same compression without the label was not
   tested here.
4. **No accuracy is bought** (Q4 below), and a wrong label is costly: on GPT-4.1-mini, GPT-5-mini and
   Qwen, high-tail work is 0.42–0.58 MAE points worse under a false low label than under its true one.

### Q4 — paired intervals instead of a resolution band

Change from control; margins fixed before the run: QWK ±0.02, MAE ±0.10. "No gain larger than" is the
improving-side bound of the 95% interval.

| arm | ΔQWK [95%] | verdict | ΔMAE [95%] | verdict | no gain larger than |
| --- | --- | --- | --- | --- | --- |
| attainment, Gemini 3.5 Flash Lite | +0.003 [−0.010, +0.017] | EQUIVALENT | −0.010 [−0.087, +0.063] | EQUIVALENT | QWK +0.017, MAE 0.09 |
| attainment, GPT-4.1-mini | +0.003 [−0.021, +0.027] | INCONCLUSIVE | +0.034 [−0.030, +0.101] | EQUIVALENT | QWK +0.027, MAE 0.03 |
| attainment, GPT-5-mini | −0.001 [−0.027, +0.018] | INCONCLUSIVE | +0.064 [−0.015, +0.147] | INCONCLUSIVE | QWK +0.018, MAE 0.02 |
| attainment, Qwen3-235B | −0.010 [−0.047, +0.023] | INCONCLUSIVE | +0.066 [−0.019, +0.150] | INCONCLUSIVE | QWK +0.023, MAE 0.02 |
| history, prior low mark | −0.011 [−0.049, +0.024] | INCONCLUSIVE | +0.063 [−0.107, +0.240] | INCONCLUSIVE | QWK +0.024, MAE 0.11 |
| history, prior high mark | +0.019 [−0.012, +0.056] | INCONCLUSIVE | −0.017 [−0.169, +0.128] | INCONCLUSIVE | QWK +0.056, MAE 0.17 |
| history, low, mark removed | −0.015 [−0.038, +0.007] | INCONCLUSIVE | +0.093 [−0.011, +0.202] | INCONCLUSIVE | QWK +0.007, MAE 0.01 |
| history, high, mark removed | +0.014 [−0.013, +0.044] | INCONCLUSIVE | −0.030 [−0.163, +0.103] | INCONCLUSIVE | QWK +0.044, MAE 0.16 |

No arm shows a gain (no interval excludes zero on the improving side). Equivalence is established only
for the attainment arm on Gemini (both metrics) and GPT-4.1-mini (MAE). The floor said this in advance:
at n = 150 a null arm reaches EQUIVALENT at ±0.10 MAE 4% of the time. The ±0.02 "resolution" is not a
licence for "no gain": the history arms admit QWK gains up to +0.056.

### Pooling read in Pearson r (staged-claim reconciliation): `R-EQUIVALENT`, `QWK-EQUIVALENT`

Nine Gemini 3.5 Flash Lite passes on the stratified 150 (65 learners): Δr +0.0035 [+0.0026, +0.0048]
at k = 9 (+0.0025 at k = 3), ΔQWK +0.007 [−0.001, +0.016], ΔMAE 0.0000; single-pass r 0.855. Checked
rather than trusted: the MAE change is exactly zero because no answer's nine passes straddle the
teacher's mark (per-answer pass sd 0.18; 49% of answers vary at all), so averaging cannot change any
absolute error. **On short answers QWK hid nothing material**; the Menagerie gain (+0.021 r, whole
programs, per-item sd ~0.6 on 14 levels) belongs to noisier items. Both are right on their own corpus.
The staged claim `pooling-repeated-llm-grades-does-not-improve-agreement` was scoped to short answers
in place with both measurements in it, and the release limitation and the `pooling-agreement`
observation were corrected in place (release unpublished, 1.0.0).

### Placeholder 7 — what §9 should say (hashes recomputed 2026-10-05 from fresh downloads)

| corpus | location | file | bytes | sha256 | md5 |
| --- | --- | --- | --- | --- | --- |
| A, JorGPT | doi:10.5281/zenodo.18981627 (CC BY 4.0) | `dataset_en.csv` | 14,558,120 | `1d5deb07247a415181f1999e66763c29a2a4df9130d0ad6e9bc813f64343653c` | `196825ce723a632b1b117efc187b0147` (matches Zenodo) |
| B, Mohler | huggingface.co/datasets/nkazi/MohlerASAG @ `dac06732b42d01a5169f543f6d272f1476cced3e` (CC BY 4.0) | `data/cleaned-oe-00001.parquet` | 153,016 | `f2aff37d7a3c6e6a7267afe0ab29ca4ebfbf90285b8eea77b08da9e1217376b0` | — |
| B, analysed CSV | `studies/measurement/grader-eval/analyses/mohler_to_csv.py` over the parquet | `mohler_en.csv` | 702,489 | `7c64b6e1eb9ef95121cb912e273b208130ec4f79c5cf1ea888970026fd605901` | `5d579caa0bfc71e108dcbbaf2d9dbd43` |
| C, Menagerie | osf.io/q8jbt (CC BY 4.0) | `grades.csv` | 460,833 | `2a63ccf4b60ea93b4ae8b11d594cbb870aa6a0ba41c81a1acdead09058d1cf7b` | `54ff4ef967c83e92813e3d146d38fc9f` |

All four match the release file exactly. JorGPT: 3,041 rows, every `teacher_corrected` True, 79
learners, 50 questions; the loader keeps 3,031 (ten empty answers). §9 should say, in substance:

> **Data.** Corpus A is JorGPT (Cisneros-González and Sánchez-Soriano 2026), Zenodo
> doi:10.5281/zenodo.18981627, file dataset_en.csv, SHA-256 1d5deb07…3653c. Corpus B is the Mohler
> ASAG corpus as mirrored at huggingface.co/datasets/nkazi/MohlerASAG, revision dac06732, file
> data/cleaned-oe-00001.parquet, SHA-256 f2aff37d…376b0; the analysed CSV is a deterministic export of
> it (SHA-256 7c64b6e1…05901). Corpus C is Menagerie (Messer et al. 2024), osf.io/q8jbt, file
> grades.csv, SHA-256 2a63ccf4…cf7b. All three are CC BY 4.0. **Code.** All code is in the research
> repository (Learning-Design-Alliance/Learning-engineering-research) at commit [the merge that brings
> the vendored harness in]. The original runs were made inside the product's private repository; the
> harness and every product file it imports at each commit those runs used are vendored byte for
> byte under studies/measurement/grader-eval/vendor/: 934478716/ (the model arms other than learner
> context), 584e5a91a/ (attempt history and attainment) and 8474722e9/ (the Menagerie ceiling), each
> with a per-file SHA-256 and git object id, and a lockfile pinning the SDK versions the runs
> resolved. Re-rendering every prompt from the vendored code reproduces, request for request, the
> prompts the product repository renders at those commits and at the two commits the learner-context
> runs were made at (vendor/runtime/render.py). The re-tests (swapped label, open-weights model,
> paired intervals, pooling in r) ran from the current harness in the same directory, with the
> grading prompt pinned to the product's 277cd5085, whose rendered prompts for the repeated arms are
> identical to the originals. **Release.** ai-grader-reliability-2026 v1.0.0, DOI [assigned at
> publication].

(Revised 2026-10-05 after the code was vendored. The earlier draft named product-repository commits
only, which a reader cannot check out; the release's `code:` blocks now point at the vendored paths
in this repository and keep the product commits as `upstream:` provenance. One thing still waits on
the merge: the research-repository commit, which exists only once the vendor branch is merged.)

## What this means for Paper VI

- **The headline (abstract, §5.3, §6.1) needs restating.** Still true: attainment context changes the
  grade on identical work, now shown causally with a swapped label, on four models including an open
  one, with no accuracy bought. Not supported as written: "bias" as a uniform harm, and "the damage is
  one-sided … a penalty applied to students the grader is told are weak" as damage. The low label
  pulls Gemini's generous grades *toward* the teacher and pushes the two harsh graders (GPT-4.1-mini,
  Qwen) away. A defensible restatement: *the mark depends on the label, not only on the work; whether
  that helps or harms a given learner depends on the grader's own calibration, which the label knows
  nothing about.* The architectural argument (§6.2) does not depend on the sign and stands; a false
  label costing strong work 0.4–0.8 points is its sharpest support.
- **"No accuracy gain" becomes an interval statement**: no QWK gain larger than +0.017 to +0.027 on the
  attainment arm and +0.007 to +0.056 on the history arms; equivalence within the paper's own ±0.02
  holds only for Gemini. "A decision, not a trade-off" survives only as "no detectable gain, and gains
  above those bounds excluded".
- **Placeholder 6 is resolved** (Qwen3-235B-A22B-2507, open weights, largest effect of the four), and
  **placeholder 7** can be filled from the table above.
- §5.3's "on both OpenAI models a high signal buys essentially nothing" still holds for drift; but the
  label effect is present in both tails on every model (L in the high tail 0.42–0.79).
