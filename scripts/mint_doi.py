"""A Zenodo DOI for a published research release: reserved first, recorded, then published.

Ported from learning-wiki's scripts/mint_release_doi.py (2026-10-15), for this repository's layout.
A version folder is immutable once merged, so the DOI is not written into the release file. It is
recorded in DOIS.json at the repository root, keyed by "<release>/<version>", with the Zenodo
deposition that holds it and its state (reserved, then published).

    python3 scripts/mint_doi.py --release <r> --version <v> --metadata
        # the deposit metadata, offline: read this first

    python3 scripts/mint_doi.py --release <r> --version <v> --reserve [--sandbox]
        # creates an unpublished Zenodo deposition with a reserved DOI and records it in DOIS.json
        # (state: reserved). Reversible: an unpublished deposition can be deleted on Zenodo.
        # Commit DOIS.json through a pull request.

    python3 scripts/mint_doi.py --release <r> --version <v> --publish --by human:<name> --yes [--sandbox]
        # uploads the version folder as one zip, publishes the deposition, and marks the entry
        # published. IRREVERSIBLE: a published Zenodo record cannot be deleted, and the DOI resolves
        # from then on. Commit DOIS.json through a pull request.

Token: a Zenodo personal access token with scopes deposit:write and deposit:actions, never passed
on the command line. Either set ZENODO_TOKEN (or ZENODO_SANDBOX_TOKEN with --sandbox) in the
environment, or, in a Claude Code cloud environment, store it as a network secret that the proxy
adds as an Authorization header for zenodo.org (or sandbox.zenodo.org): the script then sends no
header of its own and never sees the token. Try the whole flow on the sandbox first: sandbox DOIs
never resolve.

What it refuses, each for a reason:
- a version folder that fails scripts/check_releases.py: only a complete, unaltered, lifted release
  gets a DOI;
- reserving a second DOI for a version: one version, one DOI;
- publishing a version that is not yet on origin/main: the DOI must resolve to what this repository
  publishes;
- publishing a deposition whose reserved DOI is not the one DOIS.json records;
- publishing without a human:<name> actor and --yes. Anyone may prepare a deposit; making a work
  public under a permanent identifier is a person's decision.

Standard library only.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import io
import json
import os
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOIS = ROOT / "DOIS.json"
ZENODO = "https://zenodo.org/api"
ZENODO_SANDBOX = "https://sandbox.zenodo.org/api"
REPO_URL = "https://github.com/Learning-Design-Alliance/learning-research-reports"

sys.path.insert(0, str(Path(__file__).parent))
import check_releases  # noqa: E402


class Refusal(Exception):
    pass


def load_dois() -> dict:
    return json.loads(DOIS.read_text(encoding="utf-8")) if DOIS.is_file() else {}


def save_dois(d: dict) -> None:
    DOIS.write_text(json.dumps(dict(sorted(d.items())), indent=1) + "\n", encoding="utf-8")


def version_dir(release: str, version: str) -> Path:
    vdir = ROOT / release / version
    if not (vdir / "LIFT.json").is_file():
        raise Refusal(f"no published release at {release}/{version} (no LIFT.json)")
    bad = check_releases.check_version(release, vdir)
    if bad:
        raise Refusal("the version folder fails check_releases.py:\n  " + "\n  ".join(bad[:10]))
    return vdir


def release_record(vdir: Path, version: str) -> dict:
    """The release file (YAML). The one dependency outside the standard library: PyYAML."""
    try:
        import yaml
        return yaml.safe_load((vdir / f"{version}.yaml").read_text(encoding="utf-8"))
    except ImportError:
        raise Refusal("PyYAML is needed to read the release file (pip install pyyaml)")


def deposit_metadata(vdir: Path, release: str, version: str) -> dict:
    """Zenodo deposition metadata, built only from what the release and its LIFT.json state."""
    rec = release_record(vdir, version)
    lift = json.loads((vdir / "LIFT.json").read_text(encoding="utf-8"))
    r = rec.get("release") or {}
    prov = rec.get("provenance") or {}

    def para(s):
        return " ".join(str(s or "").split())

    creators = []
    for a in prov.get("authors") or []:
        if not (isinstance(a, dict) and a.get("name")):
            raise Refusal("every provenance.authors entry needs a name: a DOI record names its creators")
        c = {"name": a["name"]}
        for k in ("affiliation", "orcid"):
            if a.get(k):
                c[k] = a[k]
        creators.append(c)
    if not creators:
        raise Refusal("the release names no authors")
    contributors = [{"name": c["name"], "type": "Other"} for c in prov.get("contributors") or []
                    if isinstance(c, dict) and c.get("name")]

    description = (f"<p><b>Question.</b> {para(r.get('question'))}</p>"
                   f"<p><b>Interpretation.</b> {para(rec.get('interpretation'))}</p>"
                   "<p><b>Limitations.</b></p><ul>"
                   + "".join(f"<li>{para(x)}</li>" for x in rec.get("limitations") or [])
                   + f"</ul><p>Learning Design Alliance research release {release} {version}. The deposit "
                   f"is the release folder as published at {REPO_URL}/tree/main/{release}/{version}: the "
                   f"release file, article, HTML report, code package, notebooks and readiness records. "
                   f"LIFT.json inside it lists the SHA-256 of every file.</p>")
    related = [{"identifier": f"{REPO_URL}/tree/main/{release}/{version}", "relation": "isIdenticalTo",
                "scheme": "url"}]
    for d in rec.get("datasets") or []:
        loc = (d or {}).get("location") or {}
        ref = {"identifier": loc.get("ref"), "relation": "references", "scheme": "doi"}
        if loc.get("kind") == "doi" and loc.get("ref") and ref not in related:   # one corpus, several datasets
            related.append(ref)
    prev = r.get("supersedes")
    if prev and (load_dois().get(f"{release}/{prev}") or {}).get("doi"):
        related.append({"identifier": load_dois()[f"{release}/{prev}"]["doi"], "relation": "isNewVersionOf",
                        "scheme": "doi"})
    meta = {
        "title": para(r.get("title")),
        "upload_type": "publication",
        "publication_type": "report",
        "description": description,
        "creators": creators,
        "publication_date": str(lift.get("lifted_at", ""))[:10],
        "version": version,
        "access_right": "open",
        "license": "cc-by-4.0",
        "related_identifiers": related,
        "notes": f"Funding: {para(rec.get('funding'))} Conflicts: {para(rec.get('conflicts'))}",
    }
    if contributors:
        meta["contributors"] = contributors
    return meta


def bundle(vdir: Path, release: str, version: str) -> bytes:
    """The version folder as one zip, byte-for-byte reproducible (sorted names, fixed timestamps)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(x for x in vdir.rglob("*") if x.is_file()):
            info = zipfile.ZipInfo(f"{release}/{version}/{p.relative_to(vdir)}", (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, p.read_bytes())
    return buf.getvalue()


class Zenodo:
    """The calls this script makes, behind one small surface (tests pass a fake)."""

    def __init__(self, sandbox: bool):
        self.base = ZENODO_SANDBOX if sandbox else ZENODO
        var = "ZENODO_SANDBOX_TOKEN" if sandbox else "ZENODO_TOKEN"
        self.var = var
        self.token = os.environ.get(var)   # unset: the proxy adds the header (a network secret)

    def _call(self, method, url, body=None, raw=None):
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        data = None
        if body is not None:
            data, headers["Content-Type"] = json.dumps(body).encode(), "application/json"
        elif raw is not None:
            data, headers["Content-Type"] = raw, "application/octet-stream"
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        for attempt in (1, 2):
            try:
                with urllib.request.urlopen(req, timeout=600) as resp:
                    text = resp.read()
                break
            except urllib.error.HTTPError as e:
                hint = ""
                if e.code in (401, 403):
                    hint = (f"\n  no token was accepted (Zenodo answers 403 to a wrong token as to none): set "
                            f"{self.var}, or store the token as a network secret for "
                            f"{urllib.parse.urlsplit(url).hostname}; a network secret for that host replaces "
                            f"the header this script sends, so keep only one of the two")
                raise Refusal(f"Zenodo {method} {url} -> {e.code}: {e.read()[:300]!r}{hint}")
            except urllib.error.URLError as e:
                # A TLS handshake that fails fails before the request is sent, so one retry cannot
                # create a second deposition. Seen once through the cloud sessions' proxy, 2026-10-19.
                if attempt == 2 or not isinstance(e.reason, ssl.SSLError):
                    raise Refusal(f"Zenodo {method} {url}: {e.reason}")
                time.sleep(3)
        return json.loads(text) if text else {}

    def reserve(self, meta: dict) -> tuple[int, str]:
        dep = self._call("POST", f"{self.base}/deposit/depositions",
                         body={"metadata": {**meta, "prereserve_doi": True}})
        doi = ((dep.get("metadata") or {}).get("prereserve_doi") or {}).get("doi")
        if not doi:
            raise Refusal(f"Zenodo created deposition {dep.get('id')} but reserved no DOI")
        return dep["id"], doi

    def get(self, dep_id: int) -> dict:
        return self._call("GET", f"{self.base}/deposit/depositions/{dep_id}")

    def update(self, dep_id: int, meta: dict) -> None:
        self._call("PUT", f"{self.base}/deposit/depositions/{dep_id}", body={"metadata": meta})

    def upload(self, dep: dict, name: str, data: bytes) -> None:
        bucket = (dep.get("links") or {}).get("bucket")
        if not bucket:
            raise Refusal("the deposition has no file bucket")
        self._call("PUT", f"{bucket}/{name}", raw=data)

    def publish(self, dep_id: int) -> dict:
        return self._call("POST", f"{self.base}/deposit/depositions/{dep_id}/actions/publish")


def on_main(release: str, version: str) -> bool:
    try:
        subprocess.run(["git", "fetch", "-q", "origin", "main"], cwd=ROOT, check=True, capture_output=True)
        subprocess.run(["git", "cat-file", "-e", f"origin/main:{release}/{version}/LIFT.json"], cwd=ROOT,
                       check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def main(argv=None, client=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--release", required=True)
    ap.add_argument("--version", required=True)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--metadata", action="store_true")
    mode.add_argument("--reserve", action="store_true")
    mode.add_argument("--publish", action="store_true")
    ap.add_argument("--by")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--sandbox", action="store_true")
    a = ap.parse_args(argv)
    key = f"{a.release}/{a.version}"
    try:
        vdir = version_dir(a.release, a.version)
        meta = deposit_metadata(vdir, a.release, a.version)
        if a.metadata:
            print(json.dumps(meta, indent=2, ensure_ascii=False))
            return 0
        dois = load_dois()
        if a.reserve:
            if key in dois and not a.sandbox:
                raise Refusal(f"{key} already has {dois[key]['doi']} ({dois[key]['state']}): one version, one DOI")
            z = client or Zenodo(a.sandbox)
            dep_id, doi = z.reserve(meta)
            if a.sandbox:
                print(f"Sandbox: reserved {doi} on deposition {dep_id}. DOIS.json is not changed for the sandbox.")
                return 0
            dois[key] = {"doi": doi, "registrar": "zenodo", "deposition": dep_id, "state": "reserved",
                         "reserved_at": datetime.date.today().isoformat()}
            save_dois(dois)
            print(f"Reserved {doi} on deposition {dep_id} (unpublished, so still deletable). Recorded in "
                  f"DOIS.json: commit it through a pull request. Publish later with --publish --by "
                  f"human:<name> --yes, once {key} is on main.")
            return 0
        # publish
        if not (a.by or "").startswith("human:") or len(a.by) <= len("human:"):
            raise Refusal("publishing needs --by human:<name>: a permanent identifier is a person's decision")
        if not a.yes:
            raise Refusal("publishing is irreversible (a published Zenodo record cannot be deleted); pass --yes")
        z = client or Zenodo(a.sandbox)
        if a.sandbox:
            dep_id, doi = z.reserve(meta)
        else:
            entry = dois.get(key)
            if not entry or entry.get("state") != "reserved":
                raise Refusal(f"{key} has no reserved DOI in DOIS.json: run --reserve first")
            if not on_main(a.release, a.version):
                raise Refusal(f"{key} is not on origin/main yet: merge its pull request first")
            dep_id, doi = entry["deposition"], entry["doi"]
        dep = z.get(dep_id)
        reserved = ((dep.get("metadata") or {}).get("prereserve_doi") or {}).get("doi")
        if reserved != doi:
            raise Refusal(f"deposition {dep_id} reserved {reserved!r}, but DOIS.json says {doi!r}")
        z.update(dep_id, {**meta, "prereserve_doi": True})
        data = bundle(vdir, a.release, a.version)
        z.upload(dep, f"{a.release}-{a.version}.zip", data)
        out = z.publish(dep_id)
        if not a.sandbox:
            dois[key] |= {"state": "published", "published_at": datetime.date.today().isoformat(),
                          "published_by": a.by, "zip_sha256": hashlib.sha256(data).hexdigest()}
            save_dois(dois)
        print(f"Published {out.get('doi') or doi} ({a.by}): {(out.get('links') or {}).get('record_html') or ''}"
              + ("" if a.sandbox else "\nDOIS.json updated: commit it through a pull request."))
        return 0
    except Refusal as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
