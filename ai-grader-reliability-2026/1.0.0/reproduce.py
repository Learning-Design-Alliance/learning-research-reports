#!/usr/bin/env python3
"""
reproduce.py: recompute the results of release ai-grader-reliability-2026 (Paper VI) from what is
published with it, and check each against the published output. Every result is covered except the
original single runs, which left no per-case output, and the two analyses that draw samples through
the held-back harness, all listed at the end of this docstring.

    python3 reproduce.py                 everything that the available data allow
    python3 reproduce.py --list          the steps, which result each reproduces, and what it needs
    python3 reproduce.py --only rq2 rq4  just the steps for some research questions
    python3 reproduce.py --quick         skip the two slow steps (rq4-loop and rq6-matching; together about
                                         8 minutes on a 4-CPU machine, more on a slower one)

WHAT IT DOES. It copies the code package (code/) to a working folder, rebuilds the per-case model
outputs from per-case-model-outputs.jsonl, runs each analysis exactly as the release file records it,
and compares every file it writes, byte for byte, with the published copy in code/. It never changes
code/. At the end it prints one line per step: MATCH, DIFFERS (with the file), SKIPPED (with what is
missing) or FAILED.

WHAT IT NEEDS. Python 3.9 or later with the packages in code/studies/measurement/grader-eval/analyses/
requirements.txt (pip install -r that file). No model is called. Most steps need only the published
per-case file. A few also read a public corpus, which you download yourself (the release publishes no
corpus text); point the environment variable at its folder, or the step is skipped:

    ASAP2_DIR      ASAP 2.0 (label dose, RQ6) kaggle.com/datasets/lburleigh/asap-2-0, file ASAP2_train_sourcetexts.csv
    JORGPT_DIR     JorGPT (offsets, RQ4)      doi:10.5281/zenodo.18981627, file dataset_en.csv
    MOHLER_DIR     Mohler (Corpus B ceiling)  huggingface.co/datasets/nkazi/MohlerASAG -> mohler_en.csv (see REPRODUCE.md)
    MENAGERIE_DIR  Menagerie (Corpus C)       osf.io/q8jbt, file grades.csv
    HARMOGEN_DIR   HARMOGEN-R (5.1 ceiling)   doi:10.5281/zenodo.19534458, file harmogenr_dataset_v2.zip (zipped or extracted)

The release file gives each corpus file's SHA-256. What cannot be reproduced from the release: the
model calls themselves (the evaluation harness is not published); the two small analyses that draw
samples through the harness (sampling_sd.ts, mohler_ceiling_draw.mts; their outputs are published);
the Fable 5.1 agent bookkeeping (its statistics are recomputed by the RQ5 notebook from the per-case
file); and the original single runs, which left no per-case output: the baseline table and the grader
against each Corpus B rater (paper 5.1), the first attempt-history run (5.2), the original attainment
contrast (5.3), the original exemplar table (5.4), the three passes behind the paper's resolution
(4.8) and the corpus baselines' first spread ratios (5.1), reported from the observation records
lazuli-grader-jorgpt-2026 and lazuli-grader-mohler-2026; and likewise every other figure from a run whose
output was not kept (the design-history runs, the pricing and reasoning-token probes and the unseeded
0.795 draw), which the paper labels where it appears and reports from the records its section 9 names.
No step here regenerates any of them.
"""
from __future__ import annotations

import argparse
import os
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODE = HERE / "code"
M = "studies/measurement"
G, B = "{D}/grader-vi", "{D}/breadth"

# id, research question, what it reproduces, command (run from the working copy of code/),
# files it writes (relative to code/), corpora it needs, single-threaded BLAS, slow
STEPS = [
    ("rq1-history", "RQ1", "5.2 table: drift of each previous-attempt arm",
     f"{M}/grader-attainment-prior/analyse.py --history {G}/history-gemini.json",
     [f"{M}/grader-attainment-prior/out/history-q4.json"], [], False, False),
    ("rq2-label", "RQ2", "5.3 cross-model table: L, toward or away, penalty and reward (four original models)",
     f"{M}/grader-attainment-prior/analyse.py --dumps {G}/swap-gemini.json {G}/swap-gpt41mini.json "
     f"{G}/swap-gpt5mini.json {G}/swap-qwen.json",
     [f"{M}/grader-attainment-prior/out/results.json"], [], False, False),
    ("rq2-pooling", "RQ2", "pooling re-run (Pearson r, short answers)",
     f"{M}/grader-attainment-prior/pooling.py --dump {G}/pool-gemini.json",
     [f"{M}/grader-attainment-prior/out/pooling.json"], [], False, False),
    ("rq2-models", "RQ2, RQ5", "5.3 cross-model table and accuracy table (all six models and settings); Figures 1 and 2",
     f"{M}/grader-model-breadth/breadth.py --models {G}/swap-gemini.json {G}/swap-gpt41mini.json "
     f"{G}/swap-gpt5mini.json {G}/swap-qwen.json {B}/swap-opus55.json {B}/swap-llama4.json "
     f"{B}/swap-lite-rerun.json {B}/swap-lite-high.json {B}/swap-g5m-min.json {B}/swap-g5m-high.json "
     f"--frontier openrouter:anthropic/claude-opus-5.5",
     [f"{M}/grader-model-breadth/out/models.json"], [], False, False),
    ("rq2-learners", "RQ2", "the label effect by student",
     f"{M}/grader-model-breadth/breadth.py --learners {G}/swap-gemini.json {G}/swap-gpt41mini.json "
     f"{G}/swap-gpt5mini.json {G}/swap-qwen.json {B}/swap-opus55.json {B}/swap-llama4.json "
     f"{B}/swap-lite-rerun.json {B}/swap-lite-high.json {B}/swap-g5m-min.json {B}/swap-g5m-high.json",
     [f"{M}/grader-model-breadth/out/learners.json"], [], False, False),
    ("rq2-r-check", "RQ2", "accuracy: the change in Pearson r",
     f"{M}/grader-model-breadth/r_check.py {G}/swap-gemini.json {G}/swap-gpt41mini.json {G}/swap-gpt5mini.json "
     f"{G}/swap-qwen.json {B}/swap-opus55.json {B}/swap-llama4.json {B}/swap-lite-high.json "
     f"{B}/swap-g5m-min.json {B}/swap-g5m-high.json",
     [f"{M}/grader-model-breadth/out/r_check.json"], [], False, False),
    ("rq2-dose", "RQ2", "label dose (rho) and Qwen's label curve on ASAP 2.0; Figure 3",
     f"{M}/grader-label-dose/dose.py --run --dump-dir {{D}}",
     [f"{M}/grader-label-dose/out/results.json"], ["ASAP2_DIR"], False, False),
    ("rq2-dose-posthoc", "RQ2", "label dose, leave one model out",
     f"{M}/grader-label-dose/dose.py --posthoc --dump-dir {{D}}",
     [f"{M}/grader-label-dose/out/posthoc.json"], ["ASAP2_DIR"], False, False),
    ("rq2-neutral", "RQ2", "the neutral-sentence control",
     f"{M}/grader-neutral-control/neutral.py --dump {{D}}/neutral/swap-neutral-lite.json",
     [f"{M}/grader-neutral-control/out/results.json"], [], False, False),
    ("rq2-calibration", "RQ2", "the label-free calibration table",
     f"{M}/grader-calibration-vs-label/calibrate.py --run --scratch {{D}}",
     [f"{M}/grader-calibration-vs-label/out/results.json"], [], False, False),
    ("rq2-calibration-arms", "RQ2", "the calibration with all three arms",
     f"{M}/grader-calibration-vs-label/calibrate.py --run --all-arms --scratch {{D}}",
     [f"{M}/grader-calibration-vs-label/out/results-all-arms.json"], [], False, False),
    ("rq3-examples", "RQ3", "5.4 graded-examples table, the shuffled share and the slope; Figure 4",
     f"{M}/grader-exemplar-marks/analyse.py --dumps {{D}}/exmarks/lite.json {{D}}/exmarks/gpt41mini.json",
     [f"{M}/grader-exemplar-marks/out/results.json"], [], False, False),
    ("rq4-params", "RQ4", "the loop's fitted parameters",
     f"{M}/grader-label-compounding/compounding.py params --dumps {G}/swap-gemini.json {G}/swap-gpt41mini.json "
     f"{G}/swap-gpt5mini.json {G}/swap-qwen.json",
     [f"{M}/grader-label-compounding/out/params.json"], ["JORGPT_DIR"], False, False),
    ("rq4-loop", "RQ4", "5.5 loop table: multipliers, eigenvalues, recovery; Figure 5",
     f"{M}/grader-label-compounding/compounding.py run",
     [f"{M}/grader-label-compounding/out/results.json"], [], False, True),
    ("rq5-reasoning", "RQ5", "5.6 reasoning table",
     f"{M}/grader-model-breadth/breadth.py --reasoning "
     f"{B}/swap-g5m-min.json:{B}/swap-g5m-high.json:gpt5mini-minimal-vs-high "
     f"{B}/swap-g5m-min.json:{G}/swap-gpt5mini.json:gpt5mini-minimal-vs-default "
     f"{G}/swap-gpt5mini.json:{B}/swap-g5m-high.json:gpt5mini-default-vs-high "
     f"{B}/swap-lite-rerun.json:{B}/swap-lite-high.json:gemini-lite-minimal-vs-high "
     f"{G}/swap-gemini.json:{B}/swap-lite-rerun.json:RERUN-gemini-lite-default",
     [f"{M}/grader-model-breadth/out/reasoning.json"], [], False, False),
    ("rq5-items", "RQ5", "5.6 item types and scales (s)",
     f"{M}/grader-label-stability/analyse.py --run --dump-dir {{D}}",
     [f"{M}/grader-label-stability/out/results.json"], [], False, False),
    ("rq6-groups", "RQ6", "5.7 label effect by group",
     f"{M}/grader-attainment-groups/analyse.py --dumps {{D}}/grader-vi-groups/run-qwen.json "
     f"{{D}}/grader-vi-groups/run-gpt41mini.json",
     [f"{M}/grader-attainment-groups/out/results.json"], ["ASAP2_DIR"], False, False),
    ("rq6-matching", "RQ6", "5.7 the group gap corrected for a noisy human score; Figure 6",
     f"{M}/grader-matching-artefact/artefact.py --run --dumps {{D}}/grader-vi-groups/run-qwen.json "
     f"{{D}}/grader-vi-groups/run-gpt41mini.json",
     [f"{M}/grader-matching-artefact/out/results.json"], ["ASAP2_DIR"], True, True),
    ("rq6-label-check", "RQ6", "5.7 the label contrasts at a known reliability",
     f"{M}/grader-matching-artefact/artefact.py --label-check --dumps {{D}}/grader-vi-groups/run-qwen.json "
     f"{{D}}/grader-vi-groups/run-gpt41mini.json",
     [f"{M}/grader-matching-artefact/out/label-check.json"], ["ASAP2_DIR"], True, False),
    ("rq6-reliability", "RQ6", "5.7 RQ6 table rows at reliability 0.75 and 0.86",
     f"{M}/grader-matching-artefact/reliability_known.py --subsets --dumps {{D}}/grader-vi-groups/run-qwen.json "
     f"{{D}}/grader-vi-groups/run-gpt41mini.json",
     [f"{M}/grader-matching-artefact/out/reliability-known.json"], ["ASAP2_DIR"], True, False),
    ("ref-offset", "5.1", "the QWK offset arithmetic (Corpus A)",
     f"{M}/grader-eval/analyses/qwk_offset.py {G}/pool-gemini.json",
     [f"{M}/grader-eval/analyses/out/qwk-offset.json"], ["JORGPT_DIR"], False, False),
    ("ref-removed-rows", "5.1", "Corpus B agreement on the rows the consistency filter removed",
     f"{M}/grader-eval/analyses/mohler_removed_rows.py {{MOHLER_DIR}}/mohler_en.csv",
     [f"{M}/grader-eval/analyses/out/mohler-removed-rows.json"], ["MOHLER_DIR"], False, False),
    ("ref-ceilings", "5.1", "the human ceilings under QWK and AC2, by rater agreement",
     f"{M}/grader-ceiling-robustness/robustness.py --run --dump-dir {{D}}",
     [f"{M}/grader-ceiling-robustness/out/results.json"], ["MOHLER_DIR", "MENAGERIE_DIR"], True, False),
    ("ref-ceilings-posthoc", "5.1", "the constant-grader readings",
     f"{M}/grader-ceiling-robustness/robustness.py --posthoc --dump-dir {{D}}",
     [f"{M}/grader-ceiling-robustness/out/posthoc.json"], ["MOHLER_DIR", "MENAGERIE_DIR"], True, False),
    ("ref-harmogen", "5.1", "the HARMOGEN-R instructor ceiling (pooled, multiple-choice half, open half)",
     f"{M}/grader-harmogen-ceiling/harmogen.py --root {{HARMOGEN_DIR}}",
     [f"{M}/grader-harmogen-ceiling/out/results.json"], ["HARMOGEN_DIR"], False, False),
    ("figures", "all", "Figures 1-6 (after the steps above)",
     f"{M}/grader-eval/analyses/figures.py",
     [f"research/article/figures/{n}.{e}" for n in
      ("fig1-label-effect-across-models", "fig2-toward-or-away", "fig3-label-value", "fig4-graded-examples",
       "fig5-loop-recovery", "fig6-group-gap-by-reliability") for e in ("png", "svg")], [], False, False),
]


def unmarked(path: Path) -> bytes:
    """The published text files carry an embargo line while the release is embargoed; compare without it."""
    data = path.read_bytes()
    if path.suffix in (".md", ".txt", ".yaml", ".yml"):
        data = b"".join(ln for ln in data.splitlines(keepends=True) if b"LDA-" + b"EMBARGO" not in ln)
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[1], formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--only", nargs="*", help="step ids, or rq1 ... rq6, ref, figures")
    ap.add_argument("--quick", action="store_true", help="skip the slow steps")
    ap.add_argument("--work", type=Path, default=HERE / "reproduction", help="working folder (default ./reproduction)")
    a = ap.parse_args()

    if a.list:
        print(f"{'step':22s} {'RQ':9s} needs                     reproduces")
        for sid, rq, what, _, _, needs, _, slow in STEPS:
            print(f"{sid:22s} {rq:9s} {(', '.join(needs) or 'published data only') + (' (slow)' if slow else ''):25s} {what}")
        return 0

    steps = [s for s in STEPS if not a.only or s[0] in a.only or any(s[0].startswith(o) for o in a.only)]
    if a.quick:
        steps = [s for s in steps if not s[7]]
    work, dumps = a.work / "code", a.work / "per-case"
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(CODE, work, ignore=shutil.ignore_patterns("__pycache__"))
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    have = {v: bool(os.environ.get(v)) and Path(os.environ[v]).exists() for v in
            ("ASAP2_DIR", "JORGPT_DIR", "MOHLER_DIR", "MENAGERIE_DIR", "HARMOGEN_DIR")}

    print("Rebuilding the per-case model outputs from per-case-model-outputs.jsonl ...")
    cmd = [sys.executable, f"{M}/grader-eval/analyses/strip_dumps.py", "rebuild", "--data", str(HERE),
           "--out", str(dumps), "--skip-missing-corpus"]
    if have["ASAP2_DIR"]:
        cmd += ["--asap2", str(Path(os.environ["ASAP2_DIR"]) / "ASAP2_train_sourcetexts.csv")]
    r = subprocess.run(cmd, cwd=work, env=env)
    if r.returncode:
        print("The rebuild failed; nothing else can run.")
        return 1

    # Corpus B ships as parquet; its analyses read a CSV made from it deterministically (mohler_to_csv.py).
    if have["MOHLER_DIR"] and not (Path(os.environ["MOHLER_DIR"]) / "mohler_en.csv").exists():
        parquet = Path(os.environ["MOHLER_DIR"]) / "cleaned-oe-00001.parquet"
        if parquet.exists():
            made = a.work / "mohler"
            made.mkdir(parents=True, exist_ok=True)
            print("Deriving mohler_en.csv from the published parquet ...")
            subprocess.run([sys.executable, f"{M}/grader-eval/analyses/mohler_to_csv.py", str(parquet),
                            str(made / "mohler_en.csv")], cwd=work, env=env, check=True)
            os.environ["MOHLER_DIR"] = env["MOHLER_DIR"] = str(made)

    results = []
    for sid, rq, what, command, outs, needs, single, slow in steps:
        missing = [v for v in needs if not have[v]]
        if missing:
            results.append((sid, rq, "SKIPPED", f"needs {', '.join(missing)} (a public corpus; see the top of this file)"))
            continue
        # Split the recorded command into arguments first, then fill in the paths, so that a path
        # containing a space (the working folder or a corpus folder) stays one argument.
        args = []
        for tok in shlex.split(command):
            tok = tok.replace("{D}", str(dumps))
            for v in ("MOHLER_DIR", "HARMOGEN_DIR"):
                tok = tok.replace("{" + v + "}", os.environ.get(v, ""))
            args.append(tok)
        step_env = {**env, "OPENBLAS_NUM_THREADS": "1"} if single else env
        t0 = time.time()
        print(f"\n[{sid}] {what}\n  python3 {command.replace('{D}', '<per-case>')}")
        r = subprocess.run([sys.executable] + args, cwd=work, env=step_env)
        took = time.time() - t0
        if r.returncode:
            results.append((sid, rq, "FAILED", f"exit {r.returncode} after {took:.0f} s"))
            continue
        diff = [o for o in outs if not (work / o).exists() or unmarked(work / o) != unmarked(CODE / o)]
        results.append((sid, rq, "DIFFERS" if diff else "MATCH",
                        ", ".join(diff) if diff else f"{len(outs)} file(s) byte-identical, {took:.0f} s"))

    print("\n" + "=" * 100)
    print(f"{'step':22s} {'RQ':9s} {'result':8s} detail")
    for sid, rq, status, detail in results:
        print(f"{sid:22s} {rq:9s} {status:8s} {detail}")
    n = {s: sum(r[2] == s for r in results) for s in ("MATCH", "DIFFERS", "SKIPPED", "FAILED")}
    print(f"\n{n['MATCH']} match, {n['DIFFERS']} differ, {n['SKIPPED']} skipped, {n['FAILED']} failed.")
    return 1 if n["DIFFERS"] or n["FAILED"] else 0


if __name__ == "__main__":
    sys.exit(main())
