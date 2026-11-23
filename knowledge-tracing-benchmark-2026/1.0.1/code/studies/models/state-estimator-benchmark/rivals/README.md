# Knowledge-tracing benchmark: the published models and baselines (release knowledge-tracing-benchmark-2026)

**Asked** (maintainer, 20 Nov 2026). Publish a report of the benchmark covering the published
knowledge-tracing models and baselines it scored, and only those.

**What this folder holds.** The release's analysis code, run on the benchmark's committed per-job aggregates
(no corpus is read here):

- `collect.py` writes the per-case outputs (one record per scored fit, prediction floor, gate and floor sizing,
  with EDM Cup 2023's preprocessing report and the device control's bands) from the aggregates of the thirteen
  reported models, read by an allowlist; `collect.py verify` rebuilds the file
  byte for byte in the research repository.
- `tables.py` computes every table and every number of the article from the per-case outputs, into
  `out/tables.json`.
- `figures.py` draws Figures 1 and 2 from `out/tables.json`, after checking every value Tables 5 and 7 print.
- `out/lpkt-gate-bridge06-r1.json` is LPKT's passing gate record (an aggregate: AUCs, epochs, seconds, memory).

**What came back** (the article, `research/article/knowledge-tracing-models-under-one-protocol.md`, has the full
account):

- All nine gated models reproduced their published targets within the registered band: IRT, PFA (against Gervet
  et al.'s Table 13 value, under Amendment 1), Best-LR and DKT on Gervet et al.'s Table 4 targets; AKT, simpleKT,
  IEKT, HawkesKT (after Amendment 4) and LPKT (after tuning on the gate split) on pyKT's.
- The prediction floor F1 passed at 25% of the training learners for every deep model except HawkesKT on both
  KDD corpora; at 2%, DKT missed on half A. No floor was run for the Best-LR models. The floors of PFA, BKT and the
  running proportion were added after the registered fits, outside the registered stage lists, and are reported as
  descriptive only (`tables.py` gives those models the status FLOOR DESCRIPTIVE).
- With all training learners, AKT and simpleKT had the highest mean test AUC on all three corpora (half A 0.8148
  and 0.8128; bridge06 0.8149 and 0.8148; EDM Cup 0.8381 and 0.8364). Descriptive: no paired interval between
  models exists, because per-row predictions were not kept. On EDM Cup the order of AKT, simpleKT and IEKT, all
  fitted on GPUs, is device-sensitive under the registered rule (margins within twice the device bands), and on
  half A so is the lead of AKT, simpleKT and Best-LR with time windows (`Best-LR+` in the
  per-case outputs and the code) over IEKT, whose fits there ran on a GPU.
- With 2% of the training learners, on the two KDD corpora, the recurrent deep models (DKT, IEKT, LPKT) lost 0.138
  to 0.184 AUC, more than the logistic models (0.063 to 0.100); the attention models lost 0.083 to 0.095, about as
  much as the Best-LR models (0.083 to 0.100); of the models that fit anything, BKT lost least on every corpus
  (0.030 to 0.057); most of these 2% numbers have no floor at that size. With training
  histories cut to 20 answers the logistic models lost more than the attention models and BKT on the KDD
  corpora, and the logistic models' and BKT's numbers are descriptive only; the recurrent deep models' losses (0.148 to 0.205) overlapped the logistic models' (0.126 to 0.186).

    python3 collect.py build --out ../../../../research/wiki/research/releases/knowledge-tracing-benchmark-2026/per-case-outputs.jsonl
    python3 tables.py
    python3 figures.py
