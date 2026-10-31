# Reproducing release ai-grading-benchmark-2026

The code of this release is the AI grading benchmark repository
(https://github.com/Learning-Design-Alliance/ai-grading-benchmark) at commit
`bd3165f3d5bd1cd68c0a3f6115dbb2e3719b8107`, named in every analysis of the release file (`1.0.0.yaml`). Its paths
are the paper's `code/<path>`. There are three ways to check a result, from quickest to most complete.

## 1. The report and the notebooks

The paper's HTML report recomputes, when it is built, every number it links from the committed output it names, and
shows the file and field beside the number. The notebooks in `notebooks/` (one per research question) recompute each
question's answer from the committed outputs and assert the printed values. They need a clone of the benchmark
repository at the pinned commit; set `GBENCH_DIR` to it, or put it beside the notebook.

## 2. reproduce.py

```
git clone https://github.com/Learning-Design-Alliance/ai-grading-benchmark
python3 reproduce.py --repo ai-grading-benchmark          # about 30 minutes; --quick skips the slow steps
python3 reproduce.py --repo ai-grading-benchmark --list   # the steps and what each reproduces
```

It works on a copy checked out at the pinned commit and never changes your clone. It needs Python 3.11 or later and
pyarrow; the `baselines` step also needs scikit-learn and sentence-transformers. No model is called and no key is
needed. The steps:

| step | reproduces | needs |
|---|---|---|
| `verify` | every committed output (submissions/, out/, each study's out/) against `manifests/benchmark-outputs.sha256` | the clone |
| `fetch` | the board's four corpora, hash-checked against `fetch_data.py` (4.2) | network |
| `board` | the board: agreement, probes and flags (5.1 Table 5.1; 5.2 Table 5.2) | the corpora |
| `overall` | the whole-task order and the feedback strand (4.5; the order of every model table) | the clone |
| `scoring` | the marking-only order with the trained scorers (5.1) | the clone |
| `standard-checks` | standardized mean differences (5.1) and the pushback split (5.3) | the corpora |
| `length` | length beside agreement (5.1) | the corpora |
| `baselines` | the CPU trained scorers (5.1); the DeBERTa rows, trained on a GPU, are kept | the corpora |
| `public` | the public files the report reads (`out/public/`) | the clone |

JSON outputs are compared without the two fields that record when and from which code a file was built (`built`,
`code_sha256`); every result field must match. `out/baselines.json` is compared row by row, because the script
rewrites the CPU scorers' rows after the kept DeBERTa rows; `out/public/baselines.json`, built from it, is compared as
a multiset of rows for the same reason. The manifest also covers `docs/energy.json`.

## 3. Each study from its script

Every analysis in the release file gives its exact invocation. Those marked `rerun: offline` are the steps above.
Those marked `api` or `gpu` graded with hosted models (zero data retention, with the exceptions stated in each entry of the release file) or with models served on a rented GPU;
their replies are not published, because they quote the student work, so the analysis step cannot be re-run from the
release. Each study's script records its pre-registration, its planted-effect check and every later change, and its
committed `out/` files are what the paper's numbers are computed from. Grading again needs the corpora (sources and
hashes in the release file's `datasets:`) and a provider for each model, and can give different grades, because
hosted models change.

## The corpora

None is redistributed. Each is fetched from its source with the sha256 the release file records. Three are checked
as several files, listed in `manifests/` (`sha256sum -c` from the folder that holds them): ELLIPSE
(`manifests/ellipse.sha256`) and the 18 FLEURS languages (`manifests/fleurs-dev-18.sha256`, paths as in the
Hugging Face repository); `manifests/benchmark-outputs.sha256` lists the benchmark's committed outputs. Casual
Conversations v2 is available only under Meta's license, through personal links.
