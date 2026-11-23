# Reproducing release knowledge-tracing-benchmark-2026

This folder holds everything the article cites: the release file (`1.0.0.yaml`), the per-case outputs
(`per-case-outputs.jsonl` and its data dictionary), the code package (`code/`, listed in `code-manifest.txt`,
hashed in `code/SHA256SUMS`), the executed notebooks (`notebooks/`) and `reproduce.py`.

## What can be rerun, and what cannot

Every number in the article is computed from the per-case outputs: one record per scored fit, prediction floor,
gate and floor sizing, with EDM Cup 2023's preprocessing report and the device control's bands. `reproduce.py` reruns those computations and compares each output, byte for byte, with the
published copy:

    python3 reproduce.py          # tables (standard library) and figures (needs matplotlib)
    python3 reproduce.py --list

The fits themselves cannot be rerun from this folder. The benchmark's fitting harness (model adapters, the
rented-machine runner and the stage lists) is not published, and the corpora may not be redistributed: the KDD Cup
2010 files come from the PSLC DataShop (<https://pslcdatashop.web.cmu.edu/KDDCup/>) and EDM Cup 2023 from OSF
(<https://doi.org/10.17605/OSF.IO/YRWUH>), each under its depositor's terms. The release file records the
SHA-256 of every file read. The per-case outputs were collected from the harness's per-job aggregates by
`code/studies/models/state-estimator-benchmark/rivals/collect.py`, which runs only where those aggregates are.

The release file's `analyses:` name each analysis's repository and commit. That repository is private, so those
commits cannot be opened from outside it; every file the article cites is in `code/`, and its SHA-256 is in
`code/SHA256SUMS`.

## The notebooks

Each research question has a "re-run this finding" notebook that recomputes its printed numbers from
`per-case-outputs.jsonl` alone and asserts them. Run one from this folder or its `notebooks/` folder (or set
`RELEASE_DIR` to this folder).

| result | notebook | `reproduce.py` step |
|---|---|---|
| Tables 2 and 3 (RQ1) | `rq1-gates` | `tables` |
| Table 4 (RQ2) | `rq2-floor` | `tables` |
| Tables 5 and 6, Figure 1 (RQ3) | `rq3-prediction` | `tables`, `figures` |
| Table 7, Figure 2 (RQ4) | `rq4-thinning` | `tables`, `figures` |

Figures depend on the fonts installed; two runs on one machine give identical files, and a run elsewhere may
differ in bytes while drawing the same values.
