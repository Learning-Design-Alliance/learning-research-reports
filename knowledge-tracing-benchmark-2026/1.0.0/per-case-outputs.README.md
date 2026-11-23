# Per-case outputs of release knowledge-tracing-benchmark-2026

`per-case-outputs.jsonl` holds one JSON object per line, 2,731 lines, written by
`code/studies/models/state-estimator-benchmark/rivals/collect.py` from the benchmark's per-job aggregates.
Every `fit`, `floor` and `gate` value is an aggregate over one fold's test learners (at least 127 learners and
157,260 rows), or a published or gate statistic; the `prep` record holds counts over the whole EDM Cup corpus,
before folds, and the `device_band` records hold AUC differences between two fits of one cell. No learner, row,
prediction or identifier is in it. Floats are unrounded.

Corpora: `kddcup2010-algebra0607:halfA` (half A of KDD Cup 2010 Algebra I 2006-07), `kddcup2010-bridge06`
(KDD Cup 2010 Bridge to Algebra 2006-07), `edmcup2023` (EDM Cup 2023).

## `record: "fit"` (2,677 records)

One scored fit: a model trained on one fold's training learners (or a regime's subset of them) and scored on
that fold's test rows.

| field | meaning |
|---|---|
| `model` | one of IRT, PFA, Best-LR, Best-LR-iter1000 (solver limit 1,000), Best-LR+ (the article's Best-LR with time windows; `Best-LRplus` in `job`), BKT, running-proportion, DKT, AKT, simpleKT, IEKT, HawkesKT, LPKT |
| `corpus` | as above |
| `block` | the benchmark stage that ran the fit (a: non-deep KDD; d, e, f, d2, f2: deep KDD; g, h: EDM Cup) |
| `regime` | `main` (all training learners), `seed1` (second training seed, fold 0, deep models), `quarter` (25%), `tenth` (10%), `fiftieth` (2%), `history-fifty`, `history-twenty` (training histories cut to their first 50 or 20 answers) |
| `draw` | the subset draw, 0 to 4, for `tenth` and `fiftieth`; otherwise null |
| `fold` | the learner-level fold, 0 to 4 |
| `device` | `cpu` or `cuda` |
| `n_test_learners`, `n_test_rows` | the fold's test learners and scored rows (each learner's first row is not scored) |
| `auc` | AUC over the fold's test rows |
| `log_loss` | mean log loss, nats per answer, probabilities clipped to [1e-12, 1 - 1e-12] |
| `saturated_share` | share of test rows predicted within 1e-12 of 0 or 1 |
| `lane`, `job` | the benchmark's lane and job id that pushed the aggregate (provenance) |

## `record: "floor"` (34 records)

The prediction floor F1 for one model, corpus and regime (`quarter` = 25% or `fiftieth` = 2% of the training
learners), on fold 0's test rows of five synthetic twin pairs built on the corpus's structure.

| field | meaning |
|---|---|
| `O`, `O_se` | the oracle's effect-minus-null AUC difference and its standard error |
| `G_E` | the model's AUC minus the AUC of the world's ability-and-difficulty probabilities, effect world |
| `G_N`, `G_N_ci95` | the model's AUC minus the oracle's in the null twin, with its 95% learner-bootstrap interval |
| `G_E_minus_G_N`, `G_E_minus_G_N_ci95` | the floor statistic and its 95% interval (2,000 resamples) |
| `reading` | `PASS` (G_N's interval not above 0; G_E - G_N's interval above 0 and its point at least O/2) or `MISS`. The floors of PFA, BKT and running-proportion were run outside the registered stage lists; the release reports them as descriptive only, whatever their reading |

## `record: "gate"` (12 records)

A reproduction of a published number on bridge06. `kind` is `gervet` (pooled AUC over five folds on Gervet et
al.'s rows, against their Table 4), `gervet-amended` (PFA, mean of five fold AUCs, against their Table 13) or
`pykt` (fold 0 of pyKT's split: `pykt_primary_auc` is pyKT's own loop against `target`, `repro_diff` their
difference; `bench_auc` minus `pykt_loop_auc` is `loop_diff`). `reading` is the gate's; `attempt` marks the two
failed first attempts (HawkesKT before Amendment 4, LPKT before its tuning), kept beside the counted gates.
"LefoKT Table 3" in `target_source` is Bai et al. (2025), Table 3, the paper that proposed LefoKT.

## `record: "sizing"` (3 records)

The floor's effect size `b` per corpus: the smallest value of `b_grid` at which O was at least six times its
standard error over five twin pairs.

## `record: "prep"` (1 record)

EDM Cup 2023's preprocessing report, as the registered preparation job wrote it: counts over the whole corpus,
before folds. The preparation is shared by every EDM Cup job, and each lane keeps an identical copy of its report;
`source_file` names the copy read, which is one floor lane's. `action_lines` (lines of action_logs.csv read), `duplicate_action_lines_dropped` (exact duplicate
lines), `problem_logs`, `out_of_order_logs` and `out_of_order_share` (problem logs whose file order disagrees with
time order; ties in time are broken by file order), `drop_out_of_order` (false: the sensitivity run that drops them
was not made), `multi_code_problems` (problems carrying more than one skill code), `no_code_problems` (problems with
none, which take one "no skill code" concept), `items`, `kc_combinations`, `rows`, `learners`,
`learners_dropped_under_10`, `help_first_rows` (rows whose first action is a help request, scored as incorrect),
`u_after_video_or_tutor` (rows whose first response comes after a video or live-tutor request and no hint,
answer or explanation request: they count as unassisted under the registration's three request types, and are
scored incorrect because a help action came first), and the problem logs excluded before scoring (`excluded_open_response_first`,
`excluded_open_after_help`, `excluded_no_attempt`, `excluded_unknown_learner`).

## `record: "device_band"` (4 records)

The pre-registered device control for each model whose counted fits ran on a GPU (IEKT, AKT, simpleKT, LPKT).
`cells` lists each sampled cell (a fit named by stage, corpus, model, regime and fold) with its GPU-minus-CPU AUC
difference; for IEKT, AKT and simpleKT, fits already scored on a CPU were re-run once on the GPU, and for LPKT,
counted GPU fits were re-run once on a CPU (`how`). `band` is the largest absolute difference. The registered rule:
a verdict involving the model whose margin is within twice its band is reported as device-sensitive.
