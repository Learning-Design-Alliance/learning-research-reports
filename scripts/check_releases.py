"""Check that this repository holds only lifted, unaltered research releases.

Every release arrives as <release>/<version>/, exported from the programme's private research
repository by board/export_release.py after the maintainer has lifted it from embargo
(board/patent_gate.py --lift, which runs the patent and publication-readiness gates). This script,
run by CI on every pull request and on main, fails when:

  - any file carries the embargo marker (the string is assembled below so this file does not);
  - a version folder has no LIFT.json, or LIFT.json is not signed by a person (human:<name>), or
    names a different release or version than its folder;
  - a file in a version folder is not listed in LIFT.json, a listed file is missing, or a file's
    SHA-256 differs from the one recorded when it was lifted;
  - with --base <ref> (pull requests), the change edits, adds to or deletes from a version folder
    that already exists at <ref>. A published version is never changed: a correction is a new
    version folder whose release file says what it supersedes.

    python3 scripts/check_releases.py [--base origin/main]

Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = ("LDA-" + "EMBARGO").encode()
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
NOT_RELEASES = {".git", ".github", "scripts"}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def files_under(d: Path) -> list[Path]:
    return sorted(p for p in d.rglob("*") if p.is_file())


def check_tree() -> list[str]:
    bad = []
    for p in files_under(ROOT):
        if ".git" in p.relative_to(ROOT).parts:
            continue
        if MARKER in p.read_bytes():
            bad.append(f"{p.relative_to(ROOT)}: carries the embargo marker")
    for rdir in sorted(d for d in ROOT.iterdir() if d.is_dir() and d.name not in NOT_RELEASES):
        for x in sorted(rdir.iterdir()):
            if not (x.is_dir() and SEMVER.match(x.name)):
                bad.append(f"{x.relative_to(ROOT)}: a release folder holds only version folders (x.y.z)")
                continue
            bad += check_version(rdir.name, x)
    return bad


def check_version(release: str, vdir: Path) -> list[str]:
    where = vdir.relative_to(ROOT)
    lift_path = vdir / "LIFT.json"
    if not lift_path.is_file():
        return [f"{where}: no LIFT.json (export releases with board/export_release.py)"]
    try:
        lift = json.loads(lift_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"{where}/LIFT.json: not JSON ({e})"]
    bad = []
    by = str(lift.get("lifted_by") or "")
    if not by.startswith("human:") or len(by) <= len("human:"):
        bad.append(f"{where}/LIFT.json: lifted_by is {by!r}, not human:<name>")
    if lift.get("release") != release or str(lift.get("version")) != vdir.name:
        bad.append(f"{where}/LIFT.json: names {lift.get('release')} {lift.get('version')}")
    listed = {}
    for e in lift.get("files") or []:
        p = Path(e.get("path", ""))
        if p.is_absolute() or ".." in p.parts or not p.parts:
            bad.append(f"{where}/LIFT.json: bad path {e.get('path')!r}")
            continue
        listed[str(p)] = e.get("sha256")
    present = {str(p.relative_to(vdir)) for p in files_under(vdir)} - {"LIFT.json"}
    for x in sorted(present - set(listed)):
        bad.append(f"{where}/{x}: not listed in LIFT.json")
    for x in sorted(set(listed) - present):
        bad.append(f"{where}/{x}: listed in LIFT.json but missing")
    for x in sorted(present & set(listed)):
        if sha(vdir / x) != listed[x]:
            bad.append(f"{where}/{x}: SHA-256 differs from the one recorded at the lift")
    return bad


def check_published_unchanged(base: str) -> list[str]:
    def git(*args):
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    published = set()
    for line in git("ls-tree", "-r", "--name-only", base).splitlines():
        parts = Path(line).parts
        if len(parts) >= 3 and parts[0] not in NOT_RELEASES and SEMVER.match(parts[1]):
            published.add(parts[:2])
    bad = []
    for line in git("diff", "--name-status", "--no-renames", f"{base}...HEAD").splitlines():
        status, path = line.split("\t", 1)
        if Path(path).parts[:2] in published:
            bad.append(f"{path}: {status} in a published version folder; a correction is a new version")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", help="the ref a pull request merges into, e.g. origin/main")
    a = ap.parse_args()
    bad = check_tree()
    if a.base:
        bad += check_published_unchanged(a.base)
    n = sum(1 for r in ROOT.iterdir() if r.is_dir() and r.name not in NOT_RELEASES
            for v in r.iterdir() if v.is_dir() and SEMVER.match(v.name))
    if bad:
        print("\n".join(bad))
        print(f"{len(bad)} problem(s)")
        return 1
    print(f"{n} published version(s); every file lifted, listed and unaltered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
