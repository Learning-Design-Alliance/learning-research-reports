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
    version folder whose release file says what it supersedes;
  - with --base <ref>, a file added in a new version folder or brief states an embargo in words (an
    `embargo:` front-matter field, "EMBARGOED", "not for circulation", "awaiting the lift", "staged in
    learning-engineering-research"). Only the marker comes off at the lift, so such a notice would be
    published as written; it was, in five releases, before 2026-11-24. The patterns match NOTICE in the
    research repository's board/patent_gate.py, which refuses the lift first; keep the two in step;
  - an erratum (errata/<release>/<version>.json) is for a version folder that does not exist, is not
    approved by a person (approved_by human:<name>), declares that it changes a finding, is of a kind not
    listed in ERRATA_KINDS, or quotes a published line that is not in the published file at the line it
    names; or, with --base, an erratum that exists at <ref> is changed or removed. An erratum corrects
    wording that changes no finding, number, verdict, data or code, without a new version or DOI
    (maintainer, 2026-11-25); anything else is a new version;
  - DOIS.json (written by scripts/mint_doi.py) names a version folder that does not exist, has an
    entry that is not a well-formed reserved or published DOI, or, with --base, changes or removes
    an entry that was already published at <ref> (a reserved entry may only become published);
  - a brief, briefs/<release>/<version>/ (exported by board/export_release.py --brief after the
    maintainer has lifted it with board/patent_gate.py --lift-brief), fails the checks a version
    folder does against its own LIFT.json, or is for a version that has no folder here; or, with
    --base, a brief that exists at <ref> is replaced by a different lifted brief. A brief may be
    re-exported from the same lift, which is how its DOI's state is brought up to date.

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
MARKER = "-".join(["LDA", "EMBARGO"]).encode()   # joined at run time: a constant would be folded into the .pyc
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
NOT_RELEASES = {".git", ".github", "scripts", "site", "_site", "briefs", "errata"}   # _site: the Pages build, never committed
BRIEFS = ROOT / "briefs"
ERRATA = ROOT / "errata"
DOIS = ROOT / "DOIS.json"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def files_under(d: Path) -> list[Path]:
    return sorted(p for p in d.rglob("*") if p.is_file())


def check_tree() -> list[str]:
    bad = []
    for p in files_under(ROOT):
        if {".git", "__pycache__"} & set(p.relative_to(ROOT).parts):
            continue
        if MARKER in p.read_bytes():
            bad.append(f"{p.relative_to(ROOT)}: carries the embargo marker")
    for rdir in sorted(d for d in ROOT.iterdir() if d.is_dir() and d.name not in NOT_RELEASES):
        for x in sorted(rdir.iterdir()):
            if not (x.is_dir() and SEMVER.match(x.name)):
                bad.append(f"{x.relative_to(ROOT)}: a release folder holds only version folders (x.y.z)")
                continue
            bad += check_version(rdir.name, x)
    bad += check_briefs()
    return bad


def check_briefs() -> list[str]:
    bad = []
    if not BRIEFS.is_dir():
        return bad
    for x in sorted(BRIEFS.glob("*/*")):
        if not (x.is_dir() and SEMVER.match(x.name)):
            bad.append(f"{x.relative_to(ROOT)}: briefs/ holds only <release>/<version>/ folders")
            continue
        bad += check_version(x.parent.name, x)
        if not (ROOT / x.parent.name / x.name / "LIFT.json").is_file():
            bad.append(f"{x.relative_to(ROOT)}: a brief for a version that is not published here")
    return bad


def check_briefs_unchanged(base: str) -> list[str]:
    def git(*args):
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    bad = []
    for path in git("ls-tree", "-r", "--name-only", base, "--", "briefs").stdout.splitlines():
        if Path(path).name != "LIFT.json":
            continue
        old = json.loads(git("show", f"{base}:{path}").stdout or "{}")
        new_p = ROOT / path
        new = json.loads(new_p.read_text(encoding="utf-8")) if new_p.is_file() else {}
        if (old.get("source_sha256"), old.get("lifted_by")) != (new.get("source_sha256"), new.get("lifted_by")):
            bad.append(f"{path}: a published brief may only be re-exported from the same lift")
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


ERRATA_KINDS = {"embargo-notice", "typo", "broken-link", "metadata"}
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def check_errata() -> list[str]:
    """Each errata file names a published version, and each location quotes that version's file exactly."""
    bad = []
    if not ERRATA.is_dir():
        return bad
    for f in sorted(ERRATA.rglob("*")):
        if not f.is_file():
            continue
        where = f.relative_to(ROOT)
        rel = f.parent.name
        ver = f.stem
        if f.parent.parent != ERRATA or f.suffix != ".json" or not SEMVER.match(ver):
            bad.append(f"{where}: errata/ holds only <release>/<version>.json")
            continue
        vdir = ROOT / rel / ver
        if not (vdir / "LIFT.json").is_file():
            bad.append(f"{where}: an erratum for a version that is not published here")
            continue
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            bad.append(f"{where}: not JSON ({e})")
            continue
        if (doc.get("release"), doc.get("version")) != (rel, ver):
            bad.append(f"{where}: names {doc.get('release')} {doc.get('version')}")
        ids = []
        for e in doc.get("errata") or []:
            tag = f"{where} erratum {e.get('id')}"
            ids.append(e.get("id"))
            by = str(e.get("approved_by") or "")
            if not by.startswith("human:") or len(by) <= len("human:"):
                bad.append(f"{tag}: approved_by is {by!r}, not human:<name> (an erratum is a person's decision)")
            if e.get("changes_findings") is not False:
                bad.append(f"{tag}: changes_findings must be false; a correction that changes a finding is a new version")
            if e.get("kind") not in ERRATA_KINDS:
                bad.append(f"{tag}: kind {e.get('kind')!r} is not one of {sorted(ERRATA_KINDS)}")
            if not ISO_DATE.match(str(e.get("date") or "")):
                bad.append(f"{tag}: date {e.get('date')!r} is not YYYY-MM-DD")
            if not (e.get("summary") and e.get("note")):
                bad.append(f"{tag}: needs a summary and a note")
            if not e.get("locations"):
                bad.append(f"{tag}: names no location")
            for loc in e.get("locations") or []:
                p, n, pub = Path(str(loc.get("path", ""))), loc.get("line"), loc.get("published")
                if p.is_absolute() or ".." in p.parts or not (vdir / p).is_file():
                    bad.append(f"{tag}: {p} is not a file of {rel}/{ver}")
                    continue
                if not isinstance(n, int) or n < 1 or not isinstance(pub, str) or not pub or "reads" not in loc:
                    bad.append(f"{tag}: {p} needs line (>= 1), published and reads")
                    continue
                have = (vdir / p).read_text(encoding="utf-8", errors="replace").splitlines()
                want = pub.split("\n")
                if len(want) > 1:
                    ok = have[n - 1:n - 1 + len(want)] == want
                else:
                    ok = n <= len(have) and pub in have[n - 1]
                if not ok:
                    bad.append(f"{tag}: {p}:{n} does not read as the erratum quotes it")
        if ids != list(range(1, len(ids) + 1)):
            bad.append(f"{where}: errata ids must run 1, 2, 3 ... in order")
    return bad


def check_errata_unchanged(base: str) -> list[str]:
    """Errata are added to, never changed or removed."""
    def git(*args):
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    bad = []
    for path in git("ls-tree", "-r", "--name-only", base, "--", "errata").stdout.splitlines():
        try:
            old = json.loads(git("show", f"{base}:{path}").stdout or "{}").get("errata") or []
        except json.JSONDecodeError:
            continue
        new_p = ROOT / path
        try:
            new = json.loads(new_p.read_text(encoding="utf-8")).get("errata") or [] if new_p.is_file() else []
        except json.JSONDecodeError:
            new = []
        if new[:len(old)] != old:
            bad.append(f"{path}: an erratum published at {base} was changed or removed; add a new one instead")
    return bad


DOI = re.compile(r"^10\.\d{4,9}/\S+$")


def check_dois(text: str | None, where: str = "DOIS.json") -> tuple[list[str], dict]:
    if text is None:
        return [], {}
    try:
        d = json.loads(text)
    except json.JSONDecodeError as e:
        return [f"{where}: not JSON ({e})"], {}
    bad = []
    for key, e in d.items():
        parts = key.split("/")
        if len(parts) != 2 or not SEMVER.match(parts[1]):
            bad.append(f"{where}: key {key!r} is not <release>/<version>")
            continue
        if where == "DOIS.json" and not (ROOT / key / "LIFT.json").is_file():
            bad.append(f"{where}: {key} has no published version folder")
        if not DOI.match(str(e.get("doi", ""))) or e.get("state") not in ("reserved", "published") \
                or not isinstance(e.get("deposition"), int):
            bad.append(f"{where}: {key} needs a doi (10.x/...), a state (reserved or published) and a deposition id")
        if e.get("state") == "published" and not str(e.get("published_by", "")).startswith("human:"):
            bad.append(f"{where}: {key} is published but not by a person (published_by: human:<name>)")
    return bad, d


def check_dois_unchanged(base: str) -> list[str]:
    r = subprocess.run(["git", "show", f"{base}:DOIS.json"], cwd=ROOT, capture_output=True, text=True)
    _bad, old = check_dois(r.stdout if r.returncode == 0 else None, f"{base}:DOIS.json")
    _bad, new = check_dois(DOIS.read_text(encoding="utf-8") if DOIS.is_file() else None)
    out = []
    for key, e in old.items():
        n = new.get(key)
        if e.get("state") == "published" and n != e:
            out.append(f"DOIS.json: {key} was published at {base}; its entry may not change")
        elif e.get("state") == "reserved" and (not n or n.get("doi") != e.get("doi")
                                              or n.get("deposition") != e.get("deposition")):
            out.append(f"DOIS.json: {key}'s reserved DOI may only become published, not change or go")
    return out


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


# Kept in step with NOTICE in the research repository's board/patent_gate.py (2026-11-24).
NOTICE = re.compile(
    r"\bEMBARGOED\b|\bNOT PUBLISHED\b|\bNOT in learning-wiki\b"
    r"|(?i:^\s*#?\s*embargo\s*:)"
    r"|(?i:awaiting the lift|\bat embargo lift|not for circulation)"
    r"|(?i:staged in learning-engineering-research|staged under research/wiki)",
    re.M)
TEXT = {".md", ".yaml", ".yml", ".txt", ".html", ".py", ".json", ".jsonl", ".csv", ".svg", ".ipynb", ".R", ".r"}


def check_new_notices(base: str) -> list[str]:
    """Files added by this change, in a version folder or brief, that state an embargo in words.
    Published folders are left alone: they are never edited, and a correction is a new version."""
    out = subprocess.run(["git", "diff", "--name-status", "--no-renames", "--diff-filter=A", f"{base}...HEAD"],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    bad = []
    for line in out.splitlines():
        path = Path(line.split("\t", 1)[1])
        f = ROOT / path
        if path.suffix not in TEXT or not f.is_file() or path.parts[0] in NOT_RELEASES - {"briefs"}:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for n, ln in enumerate(text.splitlines(), 1):
            if MARKER.decode() not in ln and NOTICE.search(ln):
                bad.append(f"{path}:{n}: states an embargo in words; reword it in the research repository, "
                           f"re-lift and re-export: {ln.strip()[:100]}")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", help="the ref a pull request merges into, e.g. origin/main")
    a = ap.parse_args()
    bad = check_tree()
    bad += check_dois(DOIS.read_text(encoding="utf-8") if DOIS.is_file() else None)[0]
    bad += check_errata()
    if a.base:
        bad += check_published_unchanged(a.base)
        bad += check_dois_unchanged(a.base)
        bad += check_briefs_unchanged(a.base)
        bad += check_new_notices(a.base)
        bad += check_errata_unchanged(a.base)
    n = sum(1 for r in ROOT.iterdir() if r.is_dir() and r.name not in NOT_RELEASES
            for v in r.iterdir() if v.is_dir() and SEMVER.match(v.name))
    if bad:
        print("\n".join(bad))
        print(f"{len(bad)} problem(s)")
        return 1
    nb = sum(1 for x in BRIEFS.glob("*/*") if x.is_dir()) if BRIEFS.is_dir() else 0
    print(f"{n} published version(s) and {nb} brief(s); every file lifted, listed and unaltered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
