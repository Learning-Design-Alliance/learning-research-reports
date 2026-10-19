"""Build the GitHub Pages site: an index of the published releases, over the release folders as they are.

    python3 scripts/build_site.py [--out _site]

The site is <out>/index.html plus a copy of every <release>/<version>/ folder, unchanged, so each
release's HTML report is served at <release>/<version>/report/index.html. Nothing here is committed:
the workflow in .github/workflows/pages.yml builds it from main on every push, after
check_releases.py has passed, so the site never shows a file the repository's checks have not.

For each version the index shows the title, authors, lift date and question from the release file,
links to the report, the article (rendered on GitHub), the release file, the code and the folder,
and the DOI once DOIS.json marks it published. A reserved DOI is not shown: it does not resolve.

Reads the release files with PyYAML; otherwise standard library only.
"""

from __future__ import annotations

import argparse
import html
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_URL = "https://github.com/Learning-Design-Alliance/learning-research-reports"

sys.path.insert(0, str(Path(__file__).parent))
import check_releases  # noqa: E402


def vkey(v: str) -> tuple:
    return tuple(int(x) for x in v.split("."))


def releases() -> list[dict]:
    import yaml
    dois = json.loads((ROOT / "DOIS.json").read_text(encoding="utf-8")) if (ROOT / "DOIS.json").is_file() else {}
    out = []
    for rdir in sorted(d for d in ROOT.iterdir() if d.is_dir() and d.name not in check_releases.NOT_RELEASES):
        versions = sorted((v for v in rdir.iterdir() if v.is_dir() and check_releases.SEMVER.match(v.name)),
                          key=lambda v: vkey(v.name), reverse=True)
        entries = []
        for vdir in versions:
            rec = yaml.safe_load((vdir / f"{vdir.name}.yaml").read_text(encoding="utf-8")) or {}
            lift = json.loads((vdir / "LIFT.json").read_text(encoding="utf-8"))
            r = rec.get("release") or {}
            prov = rec.get("provenance") or {}
            articles = sorted((vdir / "article").glob("*.md")) if (vdir / "article").is_dir() else []
            doi = dois.get(f"{rdir.name}/{vdir.name}") or {}
            entries.append({
                "release": rdir.name, "version": vdir.name,
                "title": " ".join(str(r.get("title") or rdir.name).split()),
                "question": " ".join(str(r.get("question") or "").split()),
                "authors": [a["name"] for a in prov.get("authors") or [] if isinstance(a, dict) and a.get("name")],
                "lifted_at": str(lift.get("lifted_at") or "")[:10],
                "doi": doi.get("doi") if doi.get("state") == "published" else None,
                "has_report": (vdir / "report" / "index.html").is_file(),
                "article": articles[0].relative_to(ROOT).as_posix() if articles else None,
                "has_code": (vdir / "code").is_dir(),
            })
        if entries:
            out.append({"release": rdir.name, "versions": entries})
    out.sort(key=lambda x: x["versions"][0]["lifted_at"], reverse=True)
    return out


def card(rel: dict) -> str:
    e = rel["versions"][0]
    esc = html.escape
    base = f"{e['release']}/{e['version']}"
    links = []
    if e["has_report"]:
        links.append(f'<a class="primary" href="{base}/report/index.html">Read the report</a>')
    if e["article"]:
        links.append(f'<a href="{REPO_URL}/blob/main/{e["article"]}">Article</a>')
    links.append(f'<a href="{REPO_URL}/blob/main/{base}/{e["version"]}.yaml">Release file</a>')
    if e["has_code"]:
        links.append(f'<a href="{REPO_URL}/tree/main/{base}/code">Code</a>')
    links.append(f'<a href="{REPO_URL}/tree/main/{base}">All files</a>')
    doi = (f'<a href="https://doi.org/{esc(e["doi"])}">doi:{esc(e["doi"])}</a>' if e["doi"]
           else '<span class="muted">DOI pending</span>')
    q = e["question"]
    if len(q) > 420:
        q = q[:420].rsplit(" ", 1)[0] + "…"
    older = ""
    if len(rel["versions"]) > 1:
        older = ('<p class="older">Earlier versions: ' + ", ".join(
            f'<a href="{v["release"]}/{v["version"]}/report/index.html">{esc(v["version"])}</a>'
            if v["has_report"] else esc(v["version"]) for v in rel["versions"][1:]) + "</p>")
    return f"""
  <article class="card">
    <h2><a href="{base}/report/index.html">{esc(e['title'])}</a></h2>
    <p class="meta">{esc(', '.join(e['authors']))} · version {esc(e['version'])} · published {esc(e['lifted_at'])} · {doi}</p>
    <p class="question">{esc(q)}</p>
    <p class="links">{' '.join(links)}</p>{older}
  </article>"""


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Learning Research Reports</title>
<meta name="description" content="Published research releases of the Learning Design Alliance's learning-engineering programme.">
<style>
:root {{ --bg:#fbfaf7; --fg:#1d1d1b; --muted:#66645e; --line:#e4e1d8; --card:#ffffff; --accent:#1f5f8b; --accent-fg:#ffffff; }}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{ --bg:#161614; --fg:#ecebe6; --muted:#a3a198; --line:#33322e; --card:#1f1f1c; --accent:#7fb7de; --accent-fg:#10202b; }}
}}
:root[data-theme="dark"] {{ --bg:#161614; --fg:#ecebe6; --muted:#a3a198; --line:#33322e; --card:#1f1f1c; --accent:#7fb7de; --accent-fg:#10202b; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--fg); font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif; }}
main {{ max-width:860px; margin:0 auto; padding:40px 16px 64px; }}
header h1 {{ font-size:1.9rem; margin:0 0 8px; letter-spacing:-0.01em; }}
header p {{ color:var(--muted); margin:0 0 6px; max-width:68ch; }}
a {{ color:var(--accent); }}
.card {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:20px 22px; margin:22px 0; }}
.card h2 {{ font-size:1.25rem; line-height:1.3; margin:0 0 6px; }}
.card h2 a {{ color:var(--fg); text-decoration:none; }}
.card h2 a:hover {{ text-decoration:underline; }}
.meta, .older, .muted {{ color:var(--muted); font-size:0.9rem; }}
.meta {{ margin:0 0 12px; }}
.question {{ margin:0 0 14px; }}
.links {{ display:flex; flex-wrap:wrap; gap:8px 16px; align-items:center; margin:0; font-size:0.95rem; }}
.links a.primary {{ background:var(--accent); color:var(--accent-fg); padding:6px 12px; border-radius:6px; text-decoration:none; font-weight:600; }}
footer {{ color:var(--muted); font-size:0.85rem; border-top:1px solid var(--line); margin-top:40px; padding-top:16px; }}
</style>
</head>
<body>
<main>
<header>
  <h1>Learning Research Reports</h1>
  <p>Published research releases of the Learning Design Alliance's learning-engineering programme. Each release
  is an article with everything needed to check it: the release file, the code, per-case outputs, re-run notebooks,
  and an HTML report in which every number links to the output it was computed from.</p>
  <p>Findings are also summarised as claim pages in <a href="https://github.com/Learning-Design-Alliance/learning-wiki">learning-wiki</a>.</p>
</header>
{cards}
<footer>
  {n} published release(s). Every file is listed with its SHA-256 in each version's LIFT.json; a published version
  is never changed. Code is MIT-licensed; text, figures, reports and data outputs are CC BY 4.0.
  Source: <a href="{repo}">{repo_short}</a>.
</footer>
</main>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "_site")
    a = ap.parse_args()
    out = a.out.resolve()
    if out == ROOT or out in ROOT.parents or (out.parent == ROOT and out.name != "_site"):
        sys.exit("--out must be _site at the repository root, or a folder outside the repository")
    rels = releases()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for rel in rels:
        for v in rel["versions"]:
            shutil.copytree(ROOT / v["release"] / v["version"], out / v["release"] / v["version"])
    (out / "index.html").write_text(PAGE.format(cards="".join(card(r) for r in rels), n=len(rels), repo=REPO_URL,
                                                repo_short=REPO_URL.removeprefix("https://github.com/")),
                                    encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")   # serve folders as they are, underscores included
    print(f"built {out}: {len(rels)} release(s), "
          + ", ".join(f"{r['release']} {r['versions'][0]['version']}" for r in rels))
    return 0


if __name__ == "__main__":
    sys.exit(main())
