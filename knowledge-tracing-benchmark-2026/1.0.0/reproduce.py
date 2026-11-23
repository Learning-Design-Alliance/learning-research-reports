#!/usr/bin/env python3
"""
reproduce.py: recompute the results of release knowledge-tracing-benchmark-2026 ("Published knowledge-tracing
models under one protocol on three tutor corpora") from what is published with it, and check each against the
published output.

Licence: MIT, Copyright (c) 2026 Learning Design Alliance (full text in code/LICENSE).

    python3 reproduce.py               every step
    python3 reproduce.py --list        the steps, the result each reproduces, and what it needs
    python3 reproduce.py --only tables

It copies the code package (code/) to a temporary folder, runs each analysis there exactly as the release file
(1.0.0.yaml, analyses:) records it, and compares every file the step writes, byte for byte, with the published
copy. It never changes code/. The benchmark's fits are not rerun: their harness is not published, and their
aggregates are the per-case outputs, from which every step here starts. See REPRODUCE.md.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODE = HERE / "code"
STUDY = "studies/models/state-estimator-benchmark/rivals"
FIG = "research/article/figures/knowledge-tracing-benchmark-2026"

STEPS = [
    dict(id="tables", rq="RQ1-RQ4", what="Tables 2 to 7 and the text's numbers, from the per-case outputs",
         cmd=["tables.py", "--per-case", str(HERE / "per-case-outputs.jsonl")],
         outs=[f"{STUDY}/out/tables.json"], needs=[]),
    dict(id="figures", rq="RQ3, RQ4", what="Figures 1 and 2, and the check of Tables 5 and 7 as printed",
         cmd=["figures.py"], outs=[f"{FIG}/fig1-main-auc.png", f"{FIG}/fig1-main-auc.svg",
                                   f"{FIG}/fig2-thinning.png", f"{FIG}/fig2-thinning.svg"], needs=["matplotlib"]),
]


def have(mod: str) -> bool:
    try:
        __import__(mod)
        return True
    except ImportError:
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--only", nargs="+")
    a = ap.parse_args()
    if a.list:
        for s in STEPS:
            print(f"{s['id']:10s} {s['rq']:9s} {s['what']}  needs: {', '.join(s['needs']) or 'the standard library'}")
        return 0
    steps = [s for s in STEPS if not a.only or s["id"] in a.only]
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "code"
        shutil.copytree(CODE, work)
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        for s in steps:
            missing = [m for m in s["needs"] if not have(m)]
            if missing:
                results.append((s["id"], f"SKIPPED (install {', '.join(missing)})"))
                continue
            for o in s["outs"]:
                (work / o).unlink(missing_ok=True)
            r = subprocess.run([sys.executable, *s["cmd"]], cwd=work / STUDY, env=env, capture_output=True, text=True)
            if r.returncode:
                results.append((s["id"], f"FAILED (exit {r.returncode}): {(r.stdout + r.stderr).strip()[-300:]}"))
                continue
            diff = [o for o in s["outs"] if not (work / o).is_file()
                    or (work / o).read_bytes() != (CODE / o).read_bytes()]
            results.append((s["id"], "MATCH" if not diff else f"DIFFERS: {', '.join(diff)}"))
    for sid, res in results:
        print(f"{sid:10s} {res}")
    return 0 if all(r.startswith(("MATCH", "SKIPPED")) for _, r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
