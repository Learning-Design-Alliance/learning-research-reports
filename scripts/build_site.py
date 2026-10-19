"""Build the GitHub Pages site: an index of the published releases, over the release folders as they are.

    python3 scripts/build_site.py [--out _site]

The site is <out>/index.html, the brand assets in site/ (served as assets/), plus a copy of every <release>/<version>/ folder, unchanged, so each
release's HTML report is served at <release>/<version>/report/index.html, with a breadcrumb bar back to
the index, the current review form (site/review/) and the LDA brand and footer (site/report/) in the
served copy only (the repository's file, which LIFT.json hashes, is unchanged). Nothing here is committed:
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
        links.append(f'<a class="pill primary" href="{base}/report/index.html">Read the report</a>')
    if e["article"]:
        links.append(f'<a class="pill" href="{REPO_URL}/blob/main/{e["article"]}">Article <span aria-hidden="true">↗</span></a>')
    links.append(f'<a class="pill" href="{REPO_URL}/blob/main/{base}/{e["version"]}.yaml">Release file <span aria-hidden="true">↗</span></a>')
    if e["has_code"]:
        links.append(f'<a class="pill" href="{REPO_URL}/tree/main/{base}/code">Code <span aria-hidden="true">↗</span></a>')
    links.append(f'<a class="pill" href="{REPO_URL}/tree/main/{base}">All files <span aria-hidden="true">↗</span></a>')
    doi = (f'<a href="https://doi.org/{esc(e["doi"])}">doi:{esc(e["doi"])}</a>' if e["doi"]
           else '<span>DOI pending</span>')
    q = e["question"]
    if len(q) > 420:
        q = q[:420].rsplit(" ", 1)[0] + "…"
    older = ""
    if len(rel["versions"]) > 1:
        older = ('<p class="label older">Earlier versions: ' + ", ".join(
            f'<a href="{v["release"]}/{v["version"]}/report/index.html">{esc(v["version"])}</a>'
            if v["has_report"] else esc(v["version"]) for v in rel["versions"][1:]) + "</p>")
    return f"""
  <article class="release">
    <p class="label">{esc(e['release'])} · v{esc(e['version'])} · published {esc(e['lifted_at'])} · {doi}</p>
    <h2><a href="{base}/report/index.html">{esc(e['title'])}</a></h2>
    <p class="byline">{esc(', '.join(e['authors']))}</p>
    <p class="question">{esc(q)}</p>
    <p class="links">{' '.join(links)}</p>{older}
  </article>"""


# The bar the site adds above each report it serves. Only the served copy carries it: the repository's
# file, which LIFT.json hashes and the DOI deposit holds, is not changed.
NAV = """<div class="lda-crumbs" role="navigation" aria-label="Breadcrumb"><style>
.lda-crumbs{{background:#fffbf5;color:#122fb2;border-bottom:1px solid #122fb2;font:400 12.5px/1.4 "DM Mono",ui-monospace,Menlo,monospace;letter-spacing:.06em;text-transform:uppercase}}
.lda-crumbs .in{{display:flex;align-items:center;gap:12px;padding:10px 16px;min-width:0}}
.lda-crumbs a{{color:#122fb2;text-decoration:none}}
.lda-crumbs a:hover{{text-decoration:underline;text-underline-offset:3px}}
.lda-crumbs img{{height:16px;width:auto;display:block}}
.lda-crumbs .home{{display:flex;align-items:center;gap:10px;white-space:nowrap;flex:none}}
.lda-crumbs .sep{{opacity:.5;flex:none}}
.lda-crumbs .here{{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:0;flex:1;opacity:.8}}
.lda-crumbs .doi{{flex:none;white-space:nowrap}}
@media (max-width:560px){{.lda-crumbs .doi{{display:none}}}}
@media print{{.lda-crumbs{{display:none}}}}
</style><div class="in"><a class="home" href="../../../index.html"><img src="../../../assets/lda-monogram.svg" alt="Learning Design Alliance">Research reports</a><span class="sep" aria-hidden="true">/</span><span class="here" aria-current="page">{title} · v{version}</span>{doi}</div></div>"""


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


def add_brand(report: Path) -> None:
    """Give a served report the LDA brand: the stylesheet, favicon and fonts in site/report/ (kept in step
    with the report renderer's board/report/), and the LDA footer. Reports rendered before 2026-10-19
    have none of these; a report that already has them is left alone."""
    s = report.read_text(encoding="utf-8")
    if 'class="lda-foot"' in s:
        return
    d = ROOT / "site" / "report"
    head = (d / "head.html").read_text(encoding="utf-8") + "<style>" + (d / "brand.css").read_text(encoding="utf-8") + "</style>"
    if s.count("</head>") < 1 or s.count("</article></main>") != 1:
        sys.exit(f"{report}: no </head> or </article></main> to put the LDA brand around")
    s = s.replace("</head>", head + "</head>", 1)
    s = s.replace("</article></main>", "</article>" + (d / "footer.html").read_text(encoding="utf-8") + "</main>", 1)
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
<title>Research Reports · Learning Design Alliance</title>
<meta name="description" content="Published research releases of the Learning Design Alliance's learning-engineering programme.">
<link rel="icon" type="image/png" sizes="32x32" href="assets/lda-favicon.png">
<link rel="icon" type="image/svg+xml" href="assets/lda-monogram-lapis.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Baskervville:ital@0;1&family=DM+Mono&family=DM+Sans:opsz,wght@9..40,400;9..40,500&display=swap" rel="stylesheet">
<style>
/* After learningdesignalliance.org and the LDA templates' palette: cream ground, lapis type, Baskervville display, DM Mono labels,
   DM Sans text, pill buttons, hairline lapis rules, a lavender-to-peach glow. */
:root {{ --cream:#fffbf5; --lapis:#122fb2; --ink:#0e1240; --lavender:#e1dbff; --pink:#f7cbcb; --orange:#f37434; --butter:#fffad9;
         --bg:var(--cream); --fg:var(--lapis); --text:var(--ink); --rule:rgba(18,47,178,.85); --faint:rgba(18,47,178,.12); }}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{ --bg:#0b0e33; --fg:#c9c2ff; --text:#ece9ff; --rule:rgba(201,194,255,.6);
         --faint:rgba(201,194,255,.10); --butter:#2a2f6b; --lavender:#2b2470; --pink:#4a2340; --orange:#5a2a1c; }}
}}
:root[data-theme="dark"] {{ --bg:#0b0e33; --fg:#c9c2ff; --text:#ece9ff; --rule:rgba(201,194,255,.6);
         --faint:rgba(201,194,255,.10); --butter:#2a2f6b; --lavender:#2b2470; --pink:#4a2340; --orange:#5a2a1c; }}
* {{ box-sizing:border-box; }}
html {{ background:var(--bg); }}
body {{ margin:0; min-height:100vh; color:var(--text); font:16px/1.6 "DM Sans",system-ui,-apple-system,"Segoe UI",sans-serif; position:relative; }}
body::before {{ content:""; position:fixed; inset:0; z-index:-1; pointer-events:none;
  background:
    radial-gradient(60vw 50vh at 100% 0%, var(--lavender), transparent 70%),
    radial-gradient(55vw 55vh at 0% 100%, var(--pink), transparent 70%),
    radial-gradient(30vw 30vh at 0% 100%, color-mix(in srgb, var(--orange) 35%, transparent), transparent 70%),
    var(--bg); }}
a {{ color:var(--fg); text-underline-offset:3px; }}
.label, nav.top {{ font:400 12.5px/1.5 "DM Mono",ui-monospace,Menlo,monospace; letter-spacing:.07em; text-transform:uppercase; color:var(--fg); }}
nav.top {{ display:grid; grid-template-columns:1fr auto 1fr; align-items:center; gap:16px; padding:22px 24px; border-bottom:1px solid var(--rule); }}
nav.top a {{ text-decoration:none; }}
nav.top a:hover {{ text-decoration:underline; }}
nav.top .r {{ justify-self:end; display:flex; gap:28px; }}
nav.top .mark svg {{ height:28px; width:auto; display:block; color:var(--fg); }}
main {{ max-width:920px; margin:0 auto; padding:0 20px 72px; }}
.hero {{ padding:72px 0 40px; }}
h1 {{ font:400 clamp(3rem,9vw,5.6rem)/1 "Baskervville",Georgia,serif; letter-spacing:-.02em; color:var(--fg); margin:14px 0 26px; }}
h1 em {{ font-style:italic; }}
.hero p {{ max-width:60ch; margin:0 0 10px; color:var(--fg); text-wrap:pretty; }}
.release {{ border-top:1px solid var(--rule); padding:30px 0 34px; }}
.release h2 {{ font:400 clamp(1.7rem,4vw,2.3rem)/1.15 "Baskervville",Georgia,serif; letter-spacing:-.01em; margin:10px 0 6px; text-wrap:balance; }}
.release h2 a {{ color:var(--fg); text-decoration:none; }}
.release h2 a:hover {{ text-decoration:underline; text-decoration-thickness:1px; }}
.byline {{ font-family:"Baskervville",Georgia,serif; font-style:italic; font-size:1.05rem; color:var(--fg); margin:0 0 14px; }}
.question {{ margin:0 0 20px; max-width:70ch; text-wrap:pretty; }}
.links {{ display:flex; flex-wrap:wrap; gap:10px; margin:0; }}
.pill {{ display:inline-flex; align-items:center; gap:8px; padding:9px 18px; border:1px solid var(--rule); border-radius:999px;
  font:400 12.5px/1 "DM Mono",ui-monospace,Menlo,monospace; letter-spacing:.07em; text-transform:uppercase; text-decoration:none; color:var(--fg); }}
.pill:hover {{ background:var(--faint); }}
.pill.primary {{ background:var(--butter); }}
.pill.primary:hover {{ filter:brightness(.97); }}
.older {{ margin-top:14px; }}
footer {{ border-top:1px solid var(--rule); padding-top:18px; margin-top:8px; color:var(--fg); }}
footer p {{ margin:0 0 8px; max-width:80ch; }}
.lda-links {{ display:flex; flex-wrap:wrap; gap:8px 22px; margin-bottom:14px !important; }}
.lda-links a {{ text-decoration:none; }} .lda-links a:hover {{ text-decoration:underline; }}
@media (max-width:600px) {{ nav.top {{ grid-template-columns:1fr auto; }} nav.top .l {{ display:none; }} nav.top .r {{ gap:16px; }} .hero {{ padding-top:44px; }} }}
</style>
</head>
<body>
<nav class="top" aria-label="Site">
  <span class="l"><a href="./">Research reports</a></span>
  <a class="mark" href="https://www.learningdesignalliance.org" aria-label="Learning Design Alliance">{mark}</a>
  <span class="r"><a href="https://wiki.learningdesignalliance.org">Wiki <span aria-hidden="true">↗</span></a><a href="https://www.learningdesignalliance.org">LDA <span aria-hidden="true">↗</span></a></span>
</nav>
<main>
<section class="hero">
  <p class="label">Learning Design Alliance · published research</p>
  <h1>research, <em>in the open</em></h1>
  <p>Research releases from the Learning Design Alliance's learning-engineering programme. Each release is an article with
  everything needed to check it: the release file, the code, per-case outputs, re-run notebooks, and an HTML report in which
  every number links to the output it was computed from.</p>
  <p>The findings are also summarised as claim pages in <a href="https://wiki.learningdesignalliance.org">learning-wiki</a>.</p>
</section>
{cards}
<footer class="label">
  <p class="lda-links"><a href="https://www.learningdesignalliance.org">Learning Design Alliance</a> <a href="https://reports.learningdesignalliance.org">Research reports</a> <a href="https://wiki.learningdesignalliance.org">Wiki</a> <a href="https://lazuli.design">Lazuli</a></p>
  <p>{n} published release(s) · every file is listed with its SHA-256 in each version's LIFT.json, and a published version is never changed</p>
  <p>Code MIT · text, figures, reports and data outputs CC BY 4.0 · source <a href="{repo}">{repo_short}</a></p>
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
                add_brand(out / v["release"] / v["version"] / "report" / "index.html")
                add_nav(out / v["release"] / v["version"] / "report" / "index.html", v)
    # The mark is inlined so it takes the page's colour (lapis, or lavender in dark mode).
    mark = re.sub(r'fill="#[0-9A-Fa-f]{6}"', 'fill="currentColor"',
                  (ROOT / "site" / "lda-monogram.svg").read_text(encoding="utf-8").strip())
    mark = mark.replace("<svg ", '<svg aria-hidden="true" focusable="false" ', 1)
    (out / "index.html").write_text(PAGE.format(cards="".join(card(r) for r in rels), n=len(rels), repo=REPO_URL, mark=mark,
                                                repo_short=REPO_URL.removeprefix("https://github.com/")),
                                    encoding="utf-8")
    shutil.copytree(ROOT / "site", out / "assets", ignore=shutil.ignore_patterns("review", "report"))   # the LDA logos
    shutil.copyfile(ROOT / "site" / "lda-favicon.png", out / "favicon.ico")   # browsers that ask for /favicon.ico take a PNG
    (out / ".nojekyll").write_text("", encoding="utf-8")   # serve folders as they are, underscores included
    print(f"built {out}: {len(rels)} release(s), "
          + ", ".join(f"{r['release']} {r['versions'][0]['version']}" for r in rels))
    return 0


if __name__ == "__main__":
    sys.exit(main())
