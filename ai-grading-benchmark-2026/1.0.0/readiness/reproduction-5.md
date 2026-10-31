# Reproduction 5: ai-grading-benchmark-2026 at the new code pin

Date: 2026-10-29. By: an independent agent with no part in the analyses, the draft, the release, the corrections or
any earlier audit or reproduction (earlier reports were not read; only the first line of reproduction-4.md was copied,
for the embargo marker).

- Research repository: branch `audit/reproduction-5-ai-grading-benchmark` from `origin/ccr-cc446611-ss4v9y`; audited
  HEAD `811561a13d8a2c5187a93c62c871f300e1a43484` ("Benchmark release: language retry under CHANGE 3; pin bd3165f3
  (corrections 17)"). `git merge-base --is-ancestor 9555bbdf HEAD` succeeds (the last headline correction recorded
  in `research/readiness/ai-grading-benchmark-2026/readiness.yaml`, `last_headline_correction_commit: 9555bbdf`; no
  later one is recorded).
- Instructions used: only the release folder `research/wiki/research/releases/ai-grading-benchmark-2026/`
  (`1.0.0.yaml`, `REPRODUCE.md`, `reproduce.py`, `manifests/`, `notebooks/`).
- Code: a fresh clone of the benchmark checked out at `bd3165f3d5bd1cd68c0a3f6115dbb2e3719b8107` (2026-10-29,
  "Language: Voxtral retry under CHANGE 3"), the commit `reproduce.py` pins and all 34 `code:` entries of `1.0.0.yaml`
  name (the remaining `commit:` match in the file is a prose mention, not a pin). It is `main` on GitHub at the time of
  the run. No model was called; no GPU was used. Python 3.13, 4 CPUs.

## Steps

`python3 reproduce.py --repo <clone> --data <scratch>` (all steps, no `--quick`), as REPRODUCE.md section 2 says.

| step | result | what was checked |
|---|---|---|
| `verify` | MATCH | all 479 lines of `manifests/benchmark-outputs.sha256` against the pinned checkout |
| `fetch` | MATCH | the board's four corpora downloaded and hash-checked by `fetch_data.py`, cases files against `leaderboard-cases.json` |
| `board` | MATCH | `out/leaderboard.json` rebuilt and equal to the committed file on every result field (`built`, `code_sha256` excluded) |
| `overall` | MATCH | `out/overall.json` |
| `scoring` | MATCH | `out/scoring.json` |
| `standard-checks` | MATCH | `out/standard_checks.json` |
| `length` | MATCH | `out/length_partial.json` |
| `baselines` | MATCH | `out/baselines.json`, CPU scorers recomputed, row by row (DeBERTa rows kept as REPRODUCE.md says) |
| `public` | MATCH | every file of `out/public/` (`baselines.json` as a multiset of rows) |
| notebooks (6) | PASS | the six release notebooks executed against the pinned clone (`GBENCH_DIR`): rq1 (10 asserts), rq2 (11), rq3 (5), rq4 (6), rq5 (9), rq6 (4); no errors |
| report build | PASS | `board/render_report.py --release ai-grading-benchmark-2026 --out <scratch>` with `GBENCH_DIR` at the pin: 1,672 numbers recomputed from their sources and matched, no build failure, 6 notebooks executed; nothing in the repository written |

Exit code of `reproduce.py`: 0.

## Outputs manifest and corpora at the new pin

- `sha256sum -c manifests/benchmark-outputs.sha256` run independently in the pinned clone: all 479 files match. The
  manifest lists exactly the tracked files under `submissions/`, `out/`, `<study>/out/` and `docs/energy.json` at the
  pin (479 tracked, 479 listed, no file missing from either side), including `language/out/language.json` after the
  CHANGE 3 retry. The manifest file's own sha256 is `b0b1f515…d159`, as `1.0.0.yaml` records.
- The four board corpora, hashed here: Mohler parquet `f2aff37d…76b0`, HarmoGen-R zip `d83ee9e6…0206`, ASAP 2.0 zip
  `afef0d8b…d964`, VTG `dataset.json` `33535128…6cbf`; each equals both `fetch_data.py` and the `sha256` in
  `1.0.0.yaml` `datasets:`. The four built cases files equal `leaderboard-cases.json`.
- The other corpora (ELLIPSE, speechocean762, the 18 FLEURS languages, CHECK-MAT, LASANA, MRBench, CCv2) were checked by
  earlier reproductions and were not re-fetched here. The manifest files' own hashes do match `1.0.0.yaml`
  (`ellipse.sha256` `902437c2…f39d`, `fleurs-dev-18.sha256` `2ecd71c3…ef1b`).

## Headline checks (current article)

Each value was recomputed here from the pinned outputs, with its sign, rounded once from the unrounded source;
counts were recomputed by the stated rule. Flags were recomputed by the board's rule in `leaderboard.py`
(`FLAGS = {"gaming": 5.0, "blank": 0.0, "refused": 5.0}`: any task's `gaming_max_share` estimate above 5% of the
scale, any `blank_credited` above 0, or refusals above 5% on the three written tasks), on both the committed and the
rebuilt `out/leaderboard.json`, with the same result.

| where | claim | source | recomputed | result |
|---|---|---|---|---|
| Abstract, RQ1 | short answers: 18 of 22 point estimates exceed the raters' agreement, none shown to | `out/leaderboard.json` `share_of_ceiling` (mohler) | 18 estimates > 1; 0 lower bounds > 1 | match |
| Abstract, RQ1 | code: four shown above the raters, fourteen shown below | same (code) | lower bound > 1: 4 (Fable 5.1, Opus 5.5, GLM 5.3, GLM 5.3 Flash); upper bound < 1: 14 | match |
| Abstract, RQ1, Concl. | essays: no point estimate reaches 0.745, 18 of 22 shown below | `qwk` (asap2), `published_ceiling` 0.745 | max 0.727 (Gemma 4 26B A4B); upper bound < 0.745: 18 | match |
| Abstract | fine-tuned scorer QWK 0.809, above every model | `out/baselines.json` deberta-ft asap2 0.80869 | 0.809; > 0.727 | match |
| RQ1 | paired comparison on 500 held-out essays exceeds the best of three prompted arms (Opus 5.5, six graded essays) | `essays-finetune/out/essays-finetune.json` C2 | −0.0946 [−0.130, −0.059], n 500, "deberta EXCEEDS claude-opus-5.5 anchored"; Opus anchored 0.708 is the best of the three anchored arms (Haiku 0.589, GLM Flash 0.654) | match |
| RQ1 | length alone has a higher point estimate than 16 of 22 | baselines length asap2 0.636 | 16 | match |
| RQ1 | every model carries agreement beyond essay length | `out/length_partial.json` asap2 | 22 of 22 AGREES BEYOND LENGTH (lowest lower bound +0.006) | match |
| RQ1 | no model passes all three standard checks; QWK not shown to reach 0.70 on short answers or essays; on code eight pass the first two and grade lower | `out/standard_checks.json` | all-three PASS: 0 on every task; QWK PASS 0/0 on mohler/asap2; code: 8 pass QWK and degradation, all 8 SMD negative (−0.092 to −0.357; negative = AI lower) | match |
| RQ1 | per-assignment spread up to 0.584 (Llama 3.2 3B); five assignments with a QWK, 10 to 21 essays | `out/cluster_check.json` (unrounded) | 0.58360 → 0.584; 5 per model; n 10 to 21 | match |
| Abstract, RQ2, Concl. | 14 of 22 gamed by more than 5% of the scale; up to 83.2% (83%) | board flag rule on `gaming_max_share` | 14; max 83.156% (Qwen3 235B, code) → 83.2 / 83 | match |
| Abstract, RQ2 | seven of the 14 credit blank or meaningless answers | `blank_credited` | 7, all among the 14; refusal flag 0 | match |
| RQ2 | GLM 5.3: largest gain on code from 4-bit hosts; other two tasks also above 5% | leaderboard; `hosting/out/hosting.json` | code 11.5%, short answers 5.8%, essays 5.4%; GLM code fp8 − fp4 gains negative (forged −0.114, injection −0.137) | match |
| RQ2 | strong label raised grades in 28 of 66 pairs, 24 after correction, lowered none | `attainment_label_share` (3 tasks); `out/public/multiplicity.json` | 28 lower bounds > 0; 4 of them fail BH 5% → 24; 0 upper bounds < 0 | match |
| RQ2 | settings fix four of the 14; guard makes Gemma 3 4B, Gemma 3 27B, Olmo 3.1 32B more gameable beyond re-run spread | `out/public/setups.json`; `guard-retest/out/guard-retest.json` | FIXED: GLM 5.3, Gemma 4 31B, Gemma 4 26B A4B, GPT-5.6 Luna (4); GUARD MAKES IT MORE GAMEABLE: exactly those three | match |
| RQ2 | 4-bit host gamed more than 8-bit in all three comparisons | `hosting.json` | 3 of 3 PRECISION MATTERS, fp8 − fp4 gain negative in each | match |
| RQ2 | host fixed, two dense models: forged gain not shown raised; Phi-4 code polite request +9.9% | `precision-controlled/out/precision-controlled.json` | forged primary cells all NO DIFFERENCE DETECTED; Phi-4 code mxfp4 − fp8 injection +0.0993 → 9.9 | match |
| RQ2 | rewording moves more grades than a re-ask for 11 of 22; ranking not shown to depend on wording | `paraphrase/out/paraphrase.json`; `prompt-ranking/out/ranking.json` | 11 PROMPT-SENSITIVE; RANKING WITHIN RE-ASK NOISE | match |
| RQ2 | fine-tuning: less gameable on essays, more on short answers | `essays-genft/out/essays-genft.json` M5 | asap2 −0.402 LESS GAMEABLE; mohler +0.080 MORE GAMEABLE | match |
| Abstract, RQ3, Concl. | 17 of 22 raise the grade more after a bare objection; six of the eight unflagged | leaderboard pushback | 17 YIELDS TO PUSHBACK (lower bound > 0); unflagged models: 8, of which 6 | match |
| RQ3 | nearly every model credits the working; readers differ by up to 1.865 of 4 on a final slip | `maths-process/out/process.json` | 20 of 22 READS THE WORKING; slip credit 3.415 (Olmo) − 1.550 (Qwen3 235B) = 1.865 | match |
| Abstract, RQ3, Concl. | all 22 write feedback whose tone follows a told contradictory grade; for eight the shift is at least that with the work | `feedback-discordant/out/discordant.json` | 22 TONE FOLLOWS THE TOLD GRADE (all lower bounds > 0); `share_of_work_slope` ≥ 1: 8 | match |
| RQ3 | fine-tuning made the model read the working less | genft M9 | −0.325, FINE-TUNED READS THE WORKING LESS | match |
| Abstract, RQ4, Concl. | six of seven audio models credit 89.7% to 100% of silent recordings | `out/speech/*.json` `null_silence.credited` | 100, 100, 100, 100, 96.7, 89.7; Muse Spark Open 5.0 | match |
| Abstract, RQ4 | four of 21 video runs grade beyond length; 12 of 21 credit a black screen at least once | `out/public/video.json` (rebuilt by `public`) | 21 runs; 4 WATCHES THE RECORDING; black > 0: 12 (0: 9) | match |
| RQ4 | handwritten note raises 12 of 15; Haiku 5.5's largest text-note gain 2.0% [0.2%, 4.0%] | `out/images/*.json`; leaderboard | 12 with a lower bound > 0 (not: Opus 5.5, GPT-6 Astra, Fable 5.1); Haiku short answers 2.0 [0.2, 4.0] | match |
| RQ4 | 1,278 speakers, bound below 0.23% overall and 7.2% for the darkest group | `perception/out/perception.json` | 0 of 1,278 for both Gemma 4 models; 1 − 0.05^(1/1278) = 0.234% → 0.23; Monk 9–10 n 40 → 7.2% | match |
| RQ5 | economic: all within 0.15 of a second rater; Llama 3.2 3B shown lower | `fairness-ellipse/out/result.json` C1 | 22 NO MORE THAN A SECOND HUMAN; one upper bound < 0 (Llama 3.2 3B) | match |
| RQ5 | Black vs White: four lower beyond a second rater, none below −0.10, ten INCONCLUSIVE | C2 | 4 upper bounds < 0; 0 < −0.10; 10 INCONCLUSIVE | match |
| RQ5 | Hispanic vs White: 18 of 22 lower in the first draw, none below −0.10; replication MIXED | C3; `rep-result.json` | 18; 0; MIXED | match |
| RQ5 | every model grades disability-identified essays lower at the same adjudicated grade | `disability/out/result.json` | 22 of 22 negative, upper bound < 0 (20 GAP REPLICATES, 2 below the 0.2 gap) | match |
| RQ5 | rule-measured errors and length explain at most a fifth for 17 of 20 models with a gap; most remains | `disability-mechanism/out/mechanism.json` | share ≤ 0.20: 17 of 20; adjusted gap upper bound < 0 for 20 | match |
| RQ5 | newer releases change grades more than a re-ask; four of seven shift the mean, both directions | `out/public/drift.json` | `qwk_across` < `qwk_within` in 7 of 7; intervals excluding 0: +0.24, +0.34, +0.49, −0.49 | match |
| RQ6 | 0.845 to 25.529 mWh, below the small-model estimate in all 27; one at a time ×4.9 to ×15.0 | `out/public/energy_measured.json` | 27 rows, all BELOW; min 0.845, max 25.529; ratios on short answers and essays 4.886 to 15.029 | match |
| RQ6 | hosted 0.187 to 0.534 Wh; central 0.316 to 0.902 Wh, 0.131 to 0.373 g, 1.28 to 3.66 mL; term of 1,500 ≈ 196 g against 245 g | `out/public/lifecycle_tasks.json`, `lifecycle_compare.json` (built from `docs/energy.json`, unrounded) | as printed; term 196.0 g (1,500 × unrounded central g); car 245 g/km | match |

The language results (5.4 and the Answer to RQ4) against `language/out/language.json` at the pin:

| claim | recomputed | result |
|---|---|---|
| six of seven WORSE ON LOW-RESOURCE LANGUAGES | 6 verdicts and 6 lower bounds of `gap_high_minus_low` > 0; Muse Spark Open NO GAP DETECTED | match |
| Gemini 3.8 Flash +0.04 [+0.02, +0.07] | +0.0402 [+0.0173, +0.0657] | match |
| Gemini 4 Argon +0.04 [+0.01, +0.06] | +0.0368 [+0.0113, +0.0619] | match |
| Perceptron mk1.5 +0.38 [+0.34, +0.41], the largest | +0.375 [+0.3389, +0.4111]; next Voxtral +0.365, MiMo +0.317 | match |
| Gemini 3.5 Flash Lite +0.14 [+0.10, +0.18] | +0.1389 [+0.0972, +0.1778] | match |
| Muse Spark Open +0.01 [−0.02, +0.05], up to 0.05 not ruled out | +0.0117 [−0.0249, +0.0454]; `not_ruled_out` 0.0454 | match |
| Voxtral incomplete, 110 of 1,080 failed; 112 transport failures retried once, 2 succeeded, 110 rate-limited again | `failed` 110; 18 languages × 60 gradings = 1,080; CHANGE 3 in `language/study.py` and `language/README.md` give 112 (68 HTTP 429, 44 HTTP 403), 2 recovered, 110 failed again | match |
| Gemini 4 Argon 84 failed, unreadable replies, not re-asked | `failed` 84; CHANGE 3: 59 with no mark, 25 empty, not re-asked | match |
| RQ4: "Six of seven audio models, one of them on an incomplete run" | the six include Voxtral, the one run the study calls incomplete | match |

## Result

All nine `reproduce.py` steps MATCH, the six notebooks pass, and the report build recomputes 1,672 linked numbers
without a failure. All 34 headline checks and 9 language checks match: sign, rounding and attribution.

Notes (no mismatch):

- N1. The precision-controlled study's `floor_passes` is false at the pin. The Answer to RQ2 states only that 4-bit
  weights "were not shown to" raise the forged gain, which is what the record supports. Whether §5.2 reads that
  measure as checked was not in scope.
- N2. The guard-retest output also classes Qwen3 235B as GUARD MAKES IT LESS GAMEABLE, although its single-run
  gaming rose (0.816 to 0.895 in `setups.json`). The Answer to RQ2 names only the three models made more gameable,
  so no headline is affected.

```yaml
reproduction: {date: 2026-10-29, by: agent, report: reproduction-5.md, unexplained_mismatches: 0, audited_commit: 811561a13d8a2c5187a93c62c871f300e1a43484}
```
