"""Fetch a registered corpus when an analysis asks for it, and keep scratch disk under a budget.

Scratch disk is small and most corpora are read a few times a month. A corpus that can be
re-downloaded from its recorded route (data/data-sources.json `fetch`, checked against its recorded
MD5) need not sit on disk between uses: shared.paths.data_path() calls ensure() when a path is
missing, and evict() removes the least recently used of those corpora until the scratch footprint
fits a budget. Measured 2026-09-27 through the session proxy: 5-16 MB/s, so a 1.6 GB corpus costs
2-5 minutes to bring back.

Never evicted:
  - a source with no `env` variable: only data_path() fetches automatically, so a corpus read
    through scratch_root() directly would simply be missing;
  - a source with a `manual` step (a licence click, a sign-up, an emailed request): it cannot come
    back without a person;
  - a source read by PIN_USERS or more study scripts (data_sources.used_by), whose re-download would
    be paid every few runs;
  - anything outside scratch_root(), any derived file whose generator is not committed, and any
    source whose directories hold a file no recorded route recreates (a fetch file, a derived
    file, a git-fetched tree or a member of a fetched archive) -- a hand-made extract, say.
Derived files are rebuilt by their registry `by` command when it is an archive extraction or a
committed data/ingest script; any other derived file makes its source unevictable.

    python3 data/data_sources.py --footprint
    python3 data/data_sources.py --evict 8 [--apply]      # budget in GB; dry run without --apply

LDA_NO_AUTOFETCH=1 turns the automatic fetch in data_path() off.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from shared.paths import REGISTRY, REPO, scratch_root

PIN_USERS = 10
ACCESS_FILE = ".data-access.json"
_GENERATORS = ("unzip ", "tar ", "python3 data/ingest/")


def _registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def _ds():
    sys.path.insert(0, str(REPO / "data"))
    import data_sources
    return data_sources


def source_for_env(env_var: str, reg: dict | None = None) -> dict | None:
    for s in (reg or _registry())["sources"]:
        if env_var in (s.get("env") or {}):
            return s
    return None


def _expand(p: str) -> Path:
    return Path(p.replace("$SCRATCH", str(scratch_root())))


def _command(by: str) -> str | None:
    cmd = by.split("  (")[0].strip()
    return cmd if cmd.startswith(_GENERATORS) else None


def touch(source_id: str) -> None:
    """Record that a source was just read; best effort, never raises."""
    try:
        f = scratch_root() / ACCESS_FILE
        log = json.loads(f.read_text()) if f.exists() else {}
        log[source_id] = time.time()
        tmp = f.with_suffix(".tmp")
        tmp.write_text(json.dumps(log, indent=0))
        tmp.replace(f)
    except (OSError, ValueError):
        pass


_ENV_IDS: dict | None = None


def touch_env(env_var: str) -> None:
    global _ENV_IDS
    try:
        if _ENV_IDS is None:
            _ENV_IDS = {v: s["id"] for s in _registry()["sources"] for v in (s.get("env") or {})}
        if env_var in _ENV_IDS:
            touch(_ENV_IDS[env_var])
    except (OSError, ValueError):
        pass


def ensure(env_var: str) -> bool:
    """Bring back the source behind `env_var` if it can be fetched without a person. True when every
    fetch record and rebuildable derived file is present afterwards."""
    s = source_for_env(env_var)
    if s is None or s.get("manual") or not s.get("fetch"):
        return False
    ds = _ds()
    print(f"[fetch] {s['id']} is not on disk; fetching from its recorded route", file=sys.stderr)
    ok = all(ds.fetch_one(rec) for rec in s["fetch"] if not rec["file"].startswith("/"))
    for d in s.get("derived", []):
        if _expand("$SCRATCH/" + d["file"]).exists():
            continue
        cmd = _command(d.get("by") or "")
        if not cmd:
            ok = False
            continue
        cmd = cmd.replace("$SCRATCH", str(scratch_root()))
        ok &= subprocess.run(cmd, shell=True, cwd=REPO).returncode == 0
    if ok:
        touch(s["id"])
    return ok


def _paths(s: dict) -> list[Path]:
    """Every path under scratch_root() the source puts there: fetch files, derived files, env targets."""
    root = scratch_root().resolve()
    ps = [scratch_root() / f["file"] for f in s.get("fetch", []) if not f["file"].startswith("/")]
    ps += [_expand("$SCRATCH/" + d["file"]) for d in s.get("derived", [])]
    ps += [_expand(v) for v in (s.get("env") or {}).values() if v.startswith("$SCRATCH/")]
    out = []
    for p in ps:
        try:
            rp = p.resolve()
        except OSError:
            continue
        if rp != root and root in rp.parents and rp not in out:
            out.append(rp)
    return [p for p in out if not any(q in p.parents for q in out)]


def _uncovered(s: dict, paths: list[Path]) -> list[Path]:
    """Files the source's paths hold that no recorded route recreates: not a fetch file, not a
    derived file, not inside a git-fetched tree, not a member of a fetched archive."""
    import tarfile
    import zipfile
    fetched = {(scratch_root() / f["file"]).resolve() for f in s.get("fetch", []) if not f["file"].startswith("/")}
    derived = {_expand("$SCRATCH/" + d["file"]).resolve() for d in s.get("derived", [])}
    gits = {(scratch_root() / f["file"]).resolve() for f in s.get("fetch", []) if "git" in f}
    members = set()
    for a in fetched:
        try:
            if a.suffix == ".zip" and a.exists():
                members |= {Path(n).name for n in zipfile.ZipFile(a).namelist()}
            elif a.name.endswith((".tar.gz", ".tgz")) and a.exists():
                members |= {Path(n).name for n in tarfile.open(a).getnames()}
        except (OSError, zipfile.BadZipFile, tarfile.TarError):
            pass
    out = []
    for p in paths:
        files = [p] if p.is_file() else [f for f in p.rglob("*") if f.is_file()] if p.exists() else []
        for f in files:
            if (f in fetched or f in derived or any(g == f or g in f.parents for g in gits)
                    or any(d == f or d in f.parents for d in derived) or f.name in members):
                continue
            out.append(f)
    return out


def _bytes(p: Path) -> int:
    if not p.exists():
        return 0
    if p.is_file():
        return p.stat().st_size
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())


def footprint(reg: dict | None = None, used: dict | None = None) -> list[dict]:
    reg = reg or _registry()
    used = used if used is not None else _ds().used_by(reg)
    log = {}
    f = scratch_root() / ACCESS_FILE
    if f.exists():
        try:
            log = json.loads(f.read_text())
        except ValueError:
            pass
    rows = []
    for s in reg["sources"]:
        paths = _paths(s)
        size = sum(_bytes(p) for p in paths)
        if not size:
            continue
        rebuildable = all(_command(d.get("by") or "") for d in s.get("derived", []))
        why = ("manual step" if s.get("manual") else "no fetch route" if not s.get("fetch") else
               "no env var, so data_path() cannot fetch it back" if not s.get("env") else
               f"read by {len(used.get(s['id'], []))} scripts" if len(used.get(s["id"], [])) >= PIN_USERS else
               "derived file without a committed generator" if not rebuildable else "")
        if not why:
            loose = _uncovered(s, paths)
            if loose:
                why = f"holds {len(loose)} file(s) no recorded route recreates, e.g. {loose[0].name}"
        rows.append({"id": s["id"], "bytes": size, "paths": [str(p) for p in paths], "last_access": log.get(s["id"]),
                     "evictable": not why, "kept_because": why or None})
    return rows


def evict(budget_gb: float, apply: bool = False) -> list[dict]:
    """Remove least-recently-read evictable sources until the registered footprint fits the budget."""
    rows = footprint()
    total = sum(r["bytes"] for r in rows)
    goal = budget_gb * 2 ** 30
    out = []
    for r in sorted((r for r in rows if r["evictable"]), key=lambda r: r["last_access"] or 0):
        if total <= goal:
            break
        out.append(r)
        total -= r["bytes"]
        if apply:
            for p in map(Path, r["paths"]):
                shutil.rmtree(p) if p.is_dir() else p.unlink(missing_ok=True)
    return out


def autofetch_enabled() -> bool:
    return os.environ.get("LDA_NO_AUTOFETCH") != "1"
