#!/usr/bin/env python3
"""
reproduce.py: recompute every result of release checklist-grading-2026 from what is published with it,
and check each output against the published copy.

    python3 reproduce.py             every step
    python3 reproduce.py --list      the steps, and which result each reproduces
    python3 reproduce.py --only rq12-analyse figures
    python3 reproduce.py --quick     skip the two floors (about 4 minutes together on a 4-CPU machine)

WHAT IT DOES. It copies the code package (code/) to a temporary working folder, runs each analysis there
exactly as the release file records it, reading only per-case-model-outputs.jsonl beside this script, and
compares every output, byte for byte, with the published copy in code/. It never changes code/. It prints
one line per step: MATCH, DIFFERS (with the file) or FAILED.

WHAT IT NEEDS. Python 3.9 or later with numpy, and matplotlib for the figures step. No corpus is read and
no model is called: the model calls (boolean.py --build, --perturb, --run) need the corpora and API keys,
and the checklists and planted sentences they used paraphrase the corpus text, which the release does
not publish.

TWO NOTES. The parent study's floor records its own runtime in a `seconds` field, which is ignored in
the comparison. The figures' bytes depend on the fonts matplotlib finds; on a machine with other fonts
the figures step can report DIFFERS while every value drawn is the same (the figure script checks each
value against the article's printed text before drawing, and fails if one disagrees).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = HERE / "per-case-model-outputs.jsonl"
P = "studies/measurement/grader-boolean-rubrics"
D = "studies/measurement/grader-checklist-defects"

STEPS = [
    ("rq12-analyse", "RQ1 and RQ2 (Tables 1, 2) and RQ3's planted-defect contrasts (Table 4)",
     [f"{P}/boolean.py", "--analyse", "--cases", "{cases}"], [f"{P}/out/results.json"], False),
    ("floor", "the registered study's detection floor (section 4.6, Appendix A.2)",
     [f"{P}/boolean.py", "--floor", "--cases", "{cases}"], [f"{P}/out/floor.json"], True),
    ("rq23-mechanism", "RQ2's bands (Table 3) and RQ3's per-check attribution (Table 5)",
     [f"{D}/defects.py", "--cases", "{cases}"], [f"{D}/out/results.json"], False),
    ("mechanism-floor", "the follow-up study's detection floor",
     [f"{D}/defects.py", "--floor", "--cases", "{cases}"], [f"{D}/out/floor.json"], True),
    ("figures", "Figures 1 to 5",
     [f"{D}/figures.py"], [f"research/article/figures/checklist-fig{n}.png" for n in
                           ("1-reliability", "2-human-agreement", "3-error-by-band", "4-planted-defects", "5-check-types")],
     False),
]


def same(a: Path, b: Path) -> bool:
    if a.suffix == ".json" and a.name == "floor.json" and "grader-boolean-rubrics" in str(a):
        ja, jb = json.loads(a.read_text()), json.loads(b.read_text())
        ja.pop("seconds", None), jb.pop("seconds", None)
        return ja == jb
    return a.read_bytes() == b.read_bytes()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--only", nargs="+")
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    if a.list:
        for sid, what, cmd, outs, slow in STEPS:
            print(f"{sid:16s} {what}{'  (slow)' if slow else ''}\n{'':16s} python3 {' '.join(cmd)}")
        return 0
    if not CASES.is_file():
        print(f"missing {CASES.name}: it ships beside this script")
        return 1
    code = HERE / "code"
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "code"
        shutil.copytree(code, work)
        for sid, what, cmd, outs, slow in STEPS:
            if (a.only and sid not in a.only) or (a.quick and slow):
                continue
            argv = [sys.executable, "-B"] + [c.replace("{cases}", str(CASES)) for c in cmd]
            r = subprocess.run(argv, cwd=work, capture_output=True, text=True)
            if r.returncode != 0:
                print(f"FAILED   {sid}: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else r.returncode}")
                bad += 1
                continue
            diff = [o for o in outs if not same(work / o, code / o)]
            if diff:
                print(f"DIFFERS  {sid}: {', '.join(diff)}")
                bad += 1
            else:
                print(f"MATCH    {sid} ({what})")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
