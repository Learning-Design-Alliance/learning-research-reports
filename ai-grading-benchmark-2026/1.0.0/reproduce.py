#!/usr/bin/env python3
"""
reproduce.py: recompute what release ai-grading-benchmark-2026 can recompute from what is published with it, and
check each result against the published output.

    python3 reproduce.py --repo DIR              a clone of the benchmark repository (it is checked out at the
                                                 pinned commit in a copy; your clone is not changed)
    python3 reproduce.py --repo DIR --list       the steps, what each reproduces, what it needs
    python3 reproduce.py --repo DIR --only verify board
    python3 reproduce.py --repo DIR --data DATA  reuse corpora already fetched into DATA (default: a temporary
                                                 folder inside the working copy)

WHAT IT DOES. It copies the repository to a working folder, checks out the commit the release file names, and:
  1. checks every committed output (submissions/, out/, <study>/out/) against manifests/benchmark-outputs.sha256;
  2. fetches the board's four corpora and checks them against the hashes pinned in fetch_data.py;
  3. runs each offline analysis exactly as the release file records it, and compares each file it writes with the
     committed copy. JSON files are compared with the build-time fields `built` and `code_sha256` removed (they
     record when and from which code a file was built, not a result); everything else must match exactly.
At the end it prints one line per step: MATCH, DIFFERS (with the file), SKIPPED (with what is missing) or FAILED.

WHAT IT NEEDS. Python 3.11 or later, pyarrow (Mohler's parquet), and for the `baselines` step scikit-learn and
sentence-transformers (it downloads all-MiniLM-L6-v2 at the revision the script pins). No model is called, no key is
needed. About 30 minutes on a 4-CPU machine, most of it the board's bootstrap and the standard checks.

WHAT IT CANNOT REPRODUCE. Every analysis the release file marks `rerun: api` or `rerun: gpu`: their grading calls
went to hosted or self-hosted models whose replies are not published, because they quote the student work. Their
aggregate outputs are published and checked in step 1, and the paper's report recomputes every number it links from
them. The DeBERTa rows of the trained scorers were trained on a GPU; the `baselines` step keeps them and recomputes
the CPU scorers only. Grading again with the same models can give different grades: hosted models change.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMMIT = "bd3165f3d5bd1cd68c0a3f6115dbb2e3719b8107"
MANIFEST = HERE / "manifests" / "benchmark-outputs.sha256"
VOLATILE = {"built", "code_sha256"}

# id, what it reproduces (article section), command (run in the working copy; {DATA} is the corpora folder),
# files it writes and compares, slow
STEPS = [
    ("verify", "every published output (5.1 to 5.6)", None, [], False),
    ("fetch", "4.2: the board's corpora, hash-checked", "python3 fetch_data.py --dir {DATA}", [], False),
    ("board", "5.1 Table 5.1; 5.2 Table 5.2 and flags; the order of every model table",
     "python3 leaderboard.py build submissions/ --cases-dir {DATA} --out out/leaderboard.json",
     ["out/leaderboard.json"], True),
    ("overall", "the whole-task order and the feedback strand (4.5)",
     "python3 leaderboard.py overall out/leaderboard.json --feedback feedback-board/out/feedback-board.json "
     "--discordant feedback-discordant/out/discordant.json --extra essays-genft/out/board_rows.json --out out/overall.json",
     ["out/overall.json"], False),
    ("scoring", "the marking-only order with the trained scorers (5.1)",
     "python3 leaderboard.py scoring out/leaderboard.json --extra out/baselines.json out/finetune_extra.json "
     "essays-genft/out/board_rows.json",
     ["out/scoring.json"], False),
    ("standard-checks", "5.1 standardized mean differences; 5.3 the pushback split",
     "python3 analyses/standard_checks.py --cases-dir {DATA} --out out/standard_checks.json",
     ["out/standard_checks.json"], True),
    ("length", "5.1 length beside agreement",
     "python3 analyses/length_partial.py --cases-dir {DATA} --out out/length_partial.json",
     ["out/length_partial.json"], False),
    ("baselines", "5.1 trained scorers (length, word features, reference similarity, sentence embeddings)",
     "python3 baselines/baselines.py --cases-dir {DATA} --out out/baselines.json "
     "--kinds length tfidf-ridge reference-similarity encoder-ridge",
     ["out/baselines.json"], True),
    ("public", "the public files the report reads (out/public/)",
     "python3 public_data.py out/public", ["out/public"], False),
]
# `board` rebuilds out/leaderboard.json and compares it with the committed copy; overall, scoring and public read
# whichever copy is in the working tree (the rebuilt one when board ran first).
ORDER = [s[0] for s in STEPS]


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def norm(path: Path):
    if path.suffix == ".json":
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            return path.read_bytes()
        if isinstance(d, dict):
            for k in VOLATILE:
                d.pop(k, None)
        return d
    return path.read_bytes()


def compare(work: Path, ref: Path, rel: str) -> list[str]:
    a, b = work / rel, ref / rel
    if b.is_dir() or a.is_dir():
        out = []
        for f in sorted(p for p in b.rglob("*") if p.is_file()):
            r = str(f.relative_to(ref))
            out += compare(work, ref, r)
        return out
    if not b.exists():  # not tracked in the repository (a generated file): nothing to compare it with
        return [] if a.exists() else [f"{rel} not written"]
    if not a.exists():
        return [f"{rel} not written"]
    if rel == "out/baselines.json":  # see BASELINES below
        return [] if rows_match(a, b) else [rel]
    if rel == "out/public/baselines.json":  # built from out/baselines.json, so in its row order: compare as a multiset
        key = lambda rows: sorted(json.dumps(r, sort_keys=True) for r in rows)
        return [] if key(json.loads(a.read_text())) == key(json.loads(b.read_text())) else [rel]
    return [] if norm(a) == norm(b) else [rel]


# BASELINES. `--kinds` rewrites the CPU scorers' rows after the kept DeBERTa rows, so the row order changes, and the
# script at the pinned commit adds a `prompts_tried` field that the committed file, built before that field existed,
# lacks. The comparison is therefore row by row, keyed by (model, task), on every field the committed row has.
# out/public/baselines.json follows out/baselines.json's row order, so it is compared as a multiset of rows.
def rows_match(new: Path, old: Path) -> bool:
    a = {(r["model"], r["task"]): r for r in json.loads(new.read_text())["rows"]}
    b = {(r["model"], r["task"]): r for r in json.loads(old.read_text())["rows"]}
    return a.keys() == b.keys() and all(a[k].get(f) == v for k, r in b.items() for f, v in r.items())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--repo", required=True, help="a clone of the ai-grading-benchmark repository")
    ap.add_argument("--data", help="folder for the corpora (default: inside the working copy)")
    ap.add_argument("--only", nargs="+", choices=ORDER)
    ap.add_argument("--quick", action="store_true", help="skip the slow steps")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--keep", action="store_true", help="keep the working copy")
    a = ap.parse_args()
    if a.list:
        for sid, what, cmd, outs, slow in STEPS:
            print(f"{sid:16s} {what}{'  [slow]' if slow else ''}\n{'':16s} {cmd or 'sha256 of every committed output'}")
        return 0
    tmp = Path(tempfile.mkdtemp(prefix="agb-reproduce-"))
    work, ref = tmp / "work", tmp / "ref"
    for d in (work, ref):
        subprocess.run(["git", "clone", "-q", a.repo, str(d)], check=True)
        subprocess.run(["git", "-C", str(d), "checkout", "-q", COMMIT], check=True)
    data = Path(a.data).resolve() if a.data else work / "data"
    data.mkdir(parents=True, exist_ok=True)
    want = a.only or ORDER
    results = []
    for sid, what, cmd, outs, slow in STEPS:
        if sid not in want:
            continue
        if a.quick and slow:
            results.append((sid, "SKIPPED", "slow (--quick)"))
            continue
        if sid == "verify":
            bad = []
            for line in MANIFEST.read_text().splitlines():
                h, rel = line.split("  ", 1)
                p = ref / rel
                if not p.exists() or sha(p) != h:
                    bad.append(rel)
            results.append((sid, "MATCH" if not bad else "DIFFERS", f"{len(bad)} of the manifest's files" if bad else ""))
            continue
        print(f"[{sid}] {cmd.format(DATA=data)}", flush=True)
        p = subprocess.run(cmd.format(DATA=data), shell=True, cwd=work, capture_output=True, text=True)
        if p.returncode != 0:
            tail = (p.stderr or p.stdout).strip().splitlines()[-1:] or ["(no output)"]
            results.append((sid, "FAILED", tail[0][:200]))
            continue
        diffs = [d for o in outs for d in compare(work, ref, o)]
        untracked = [o for o in outs if not (ref / o).exists()]
        note = ", ".join(diffs[:5]) if diffs else (
            f"written; {', '.join(untracked)} is not tracked, so it is checked through the steps that read it"
            if untracked else "")
        results.append((sid, "MATCH" if not diffs else "DIFFERS", note))
    print()
    for sid, verdict, note in results:
        print(f"{sid:16s} {verdict:8s} {note}")
    if not a.keep:
        shutil.rmtree(tmp, ignore_errors=True)
    else:
        print(f"working copy kept at {tmp}")
    return 0 if all(v in ("MATCH", "SKIPPED") for _, v, _ in results) else 1


if __name__ == "__main__":
    sys.exit(main())
