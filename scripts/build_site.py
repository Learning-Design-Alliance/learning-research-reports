"""Build the GitHub Pages site: an index of the published releases, over the release folders as they are.

    python3 scripts/build_site.py [--out _site]

The site is <out>/index.html, the brand assets in site/ (served as assets/), plus a copy of every <release>/<version>/ folder, unchanged, so each
release's HTML report is served at <release>/<version>/report/index.html, with a breadcrumb bar back to
the index and the current review form (site/review/) in the served copy only (the repository's file, which LIFT.json hashes, is unchanged). Nothing here is committed:
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
import re
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


# The bar the site adds above each report it serves. Only the served copy carries it: the repository's
# file, which LIFT.json hashes and the DOI deposit holds, is not changed.
NAV = """<div class="lda-crumbs" role="navigation" aria-label="Breadcrumb"><style>
.lda-crumbs{{background:#0e1240;color:#f8fafc;border-bottom:2px solid #e3b455;font:500 14px/1.4 "DM Sans",system-ui,-apple-system,"Segoe UI",sans-serif}}
.lda-crumbs .in{{display:flex;align-items:center;gap:10px;padding:9px 16px;min-width:0}}
.lda-crumbs a{{color:#f8fafc;text-decoration:none}}
.lda-crumbs a:hover{{text-decoration:underline;text-decoration-color:#e3b455;text-underline-offset:3px}}
.lda-crumbs img{{height:22px;width:22px;display:block}}
.lda-crumbs .home{{display:flex;align-items:center;gap:8px;white-space:nowrap;flex:none}}
.lda-crumbs .sep{{color:#8f95c4;flex:none}}
.lda-crumbs .here{{color:#c9cde6;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:0;flex:1}}
.lda-crumbs .doi{{flex:none;white-space:nowrap;color:#c9cde6}}
@media (max-width:560px){{.lda-crumbs .doi{{display:none}}}}
@media print{{.lda-crumbs{{display:none}}}}
</style><div class="in"><a class="home" href="../../../index.html"><img src="../../../assets/lda-monogram-white.svg" alt="">Research Reports</a><span class="sep" aria-hidden="true">›</span><span class="here" aria-current="page">{title} · v{version}</span>{doi}</div></div>"""


REVIEW_DIALOG = re.compile(r'<dialog id="review-dialog".*?</dialog>', re.S)
REVIEW_JS = re.compile(r'// Review drafting: a "Review" action on every paragraph.*?p\.appendChild\(b\);\}\);', re.S)


def update_review_form(report: Path) -> None:
    """Swap the report's review form for the current one in site/review/, in the served copy only.

    Reports published before 2026-10-19 carry a form whose Close button could not close an empty form
    and whose labels were the review schema's own terms. The new form builds the same record."""
    s = report.read_text(encoding="utf-8")
    dialog = (ROOT / "site" / "review" / "dialog.html").read_text(encoding="utf-8").strip()
    js = (ROOT / "site" / "review" / "review.js").read_text(encoding="utf-8").strip()
    s, n1 = REVIEW_DIALOG.subn(lambda m: dialog, s, count=1)
    s, n2 = REVIEW_JS.subn(lambda m: js, s, count=1)
    if (n1, n2) != (1, 1):
        sys.exit(f"{report}: review form not found (dialog {n1}, script {n2}); update REVIEW_DIALOG/REVIEW_JS")
    report.write_text(s, encoding="utf-8")


def add_nav(report: Path, e: dict) -> None:
    """Insert NAV right after <body> in the served copy of a report."""
    s = report.read_text(encoding="utf-8")
    doi = (f'<a class="doi" href="https://doi.org/{html.escape(e["doi"])}">doi:{html.escape(e["doi"])}</a>'
           if e["doi"] else "")
    nav = NAV.format(title=html.escape(e["title"]), version=html.escape(e["version"]), doi=doi)
    m = re.search(r"<body[^>]*>", s)
    if not m:
        sys.exit(f"{report}: no <body> tag to put the navigation after")
    report.write_text(s[:m.end()] + nav + s[m.end():], encoding="utf-8")


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Learning Research Reports</title>
<meta name="description" content="Published research releases of the Learning Design Alliance's learning-engineering programme.">
<link rel="icon" type="image/svg+xml" href="assets/lda-monogram-lapis.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&family=Instrument+Serif&display=swap" rel="stylesheet">
<style>
/* Learning Design Alliance: ink #0E1240, lapis #122FB2, pyrite #E3B455 on a cool gesso white. */
:root {{ --bg:#f6f7fb; --fg:#0e1240; --muted:#4f5475; --line:#dde0ec; --card:#ffffff; --band:#0e1240; --band-fg:#f8fafc;
         --accent:#122fb2; --accent-fg:#ffffff; --pyrite:#e3b455; }}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{ --bg:#0a0d2e; --fg:#eef0fa; --muted:#a9aecb; --line:#262b55; --card:#11163d;
         --band:#070a24; --band-fg:#f8fafc; --accent:#8fa2ff; --accent-fg:#0a0d2e; }}
}}
:root[data-theme="dark"] {{ --bg:#0a0d2e; --fg:#eef0fa; --muted:#a9aecb; --line:#262b55; --card:#11163d;
         --band:#070a24; --band-fg:#f8fafc; --accent:#8fa2ff; --accent-fg:#0a0d2e; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--fg); font:16px/1.6 "DM Sans",system-ui,-apple-system,"Segoe UI",sans-serif; }}
a {{ color:var(--accent); text-underline-offset:3px; }}
.band {{ background:var(--band); color:var(--band-fg); border-bottom:3px solid var(--pyrite); }}
.band-inner {{ max-width:880px; margin:0 auto; padding:28px 16px 34px; }}
.brand {{ display:inline-block; line-height:0; }}
.brand img {{ height:58px; width:auto; }}
.band h1 {{ font:400 clamp(2.2rem,6vw,3.1rem)/1.05 "Instrument Serif",Georgia,serif; margin:26px 0 12px; letter-spacing:-0.01em; text-wrap:balance; }}
.band p {{ margin:0 0 8px; max-width:66ch; color:#c9cde6; text-wrap:pretty; }}
.band a {{ color:#ffffff; text-decoration-color:var(--pyrite); }}
main {{ max-width:880px; margin:0 auto; padding:12px 16px 64px; }}
.card {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:22px 24px; margin:24px 0;
         box-shadow:0 1px 2px rgba(14,18,64,0.05); }}
.card h2 {{ font:400 1.6rem/1.2 "Instrument Serif",Georgia,serif; margin:0 0 8px; text-wrap:balance; }}
.card h2 a {{ color:var(--fg); text-decoration:none; }}
.card h2 a:hover {{ color:var(--accent); }}
.meta, .older, .muted {{ color:var(--muted); font-size:0.9rem; }}
.meta {{ margin:0 0 12px; }}
.question {{ margin:0 0 16px; text-wrap:pretty; }}
.links {{ display:flex; flex-wrap:wrap; gap:8px 18px; align-items:center; margin:0; font-size:0.95rem; font-weight:500; }}
.links a.primary {{ background:var(--accent); color:var(--accent-fg); padding:7px 14px; border-radius:8px; text-decoration:none; font-weight:600; }}
.links a.primary:hover {{ filter:brightness(1.12); }}
footer {{ color:var(--muted); font-size:0.85rem; border-top:1px solid var(--line); margin-top:40px; padding-top:16px; }}
</style>
</head>
<body>
<header class="band">
  <div class="band-inner">
    <a class="brand" href="https://learningdesignalliance.org"><img src="assets/lda-wordmark-white.svg" alt="Learning Design Alliance"></a>
    <h1>Research Reports</h1>
    <p>Published research releases of the Learning Design Alliance's learning-engineering programme. Each release
    is an article with everything needed to check it: the release file, the code, per-case outputs, re-run notebooks,
    and an HTML report in which every number links to the output it was computed from.</p>
    <p>Findings are also summarised as claim pages in <a href="https://wiki.learningdesignalliance.org">learning-wiki</a>.</p>
  </div>
</header>
<main>
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
            if v["has_report"]:
                update_review_form(out / v["release"] / v["version"] / "report" / "index.html")
                add_nav(out / v["release"] / v["version"] / "report" / "index.html", v)
    (out / "index.html").write_text(PAGE.format(cards="".join(card(r) for r in rels), n=len(rels), repo=REPO_URL,
                                                repo_short=REPO_URL.removeprefix("https://github.com/")),
                                    encoding="utf-8")
    shutil.copytree(ROOT / "site", out / "assets", ignore=shutil.ignore_patterns("review"))   # the LDA logos
    (out / ".nojekyll").write_text("", encoding="utf-8")   # serve folders as they are, underscores included
    print(f"built {out}: {len(rels)} release(s), "
          + ", ".join(f"{r['release']} {r['versions'][0]['version']}" for r in rels))
    return 0


if __name__ == "__main__":
    sys.exit(main())
