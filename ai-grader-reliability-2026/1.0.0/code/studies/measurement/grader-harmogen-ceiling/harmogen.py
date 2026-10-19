"""HARMOGEN-R re-analysed: four instructors' agreement with each other, and the deposit's LLMs' with them.

Paper VI (release ai-grader-reliability-2026, article research/article/attainment-bias-in-llm-grading.md),
section 5.1, "The human ceiling": the row "Four instructors, pooled pairs (HARMOGEN-R, half multiple
choice)" (23,100 pairs, QWK 0.981) and the sentence after the table (0.981 pooled, exactly 1.000 on the
multiple-choice half, 0.942 on the open half). Release analysis `harmogen-reanalysis`; observation record
`lazuli-grader-harmogen-2026` (both of its observations).

THE QUESTION. HARMOGEN-R (Mendonca, Quintal, Mendonca and Baras 2026, doi:10.5281/zenodo.19534458,
CC BY 4.0) has 770 student responses from a university data-structures course, each evaluated by four
instructors and by three LLMs (three iterations each) under five rubric variants. Its data paper reports a
Spearman rho of 0.991 between LLM and teacher scores, and no agreement between the instructors, although
four instructors scored every item. How far do the instructors agree with each other, measured with the
same pairwise construction and the same quadratic-weighted kappa (QWK) as the release's other human
ceilings (Mohler, Menagerie), and how does that ceiling depend on how open the items are?

THE DESIGN (as the TypeScript original; no model is called anywhere, it is arithmetic over the
depositors' published evaluations).
  - A cell is one (student response, rubric variant). Every active evaluation with a score is
    normalised to 0-100 per question by the deposit's own formula (score / Q_max x 100, Q_max the
    question's `score` in questions.csv), and binned onto an ordinal scale of L levels:
    level = round-half-up(normalised / (100 / (L - 1))), clipped to 0..L-1. L = 21 (a 5-point grid)
    and L = 11 (a 10-point grid) are both reported, because the binning is a choice that moves the number.
  - Three pair constructions per set of cells (cells with fewer than two instructors are skipped):
      machine_human   one pair per (LLM evaluation, instructor) on the cell; the instructor is the reference
      human_human     one pair per pair of instructors on the cell (instructor i before k, in file order)
      aggregate       the deposit's own construction: the binned mean of the instructors' normalised
                      scores against the binned mean of the LLM evaluations' (cells with any LLM evaluation)
    Each gets the harness's `agreement()` (n, QWK over 0..L-1 with chance from the observed marginals,
    MAE, RMSE, Pearson r, spread ratio sd(model)/sd(human), mean bias model - human: NEGATIVE means the
    LLM marks below the instructor) and Spearman rho with midranks.
  - The sets: all cells; the "bare option" cells (the response is a bare option letter, regular
    expression ^\\s*[A-Ea-e]\\s*[).]?\\s*$); the open cells (the rest); the open cells by question type
    (`text`, `code`); and each rubric variant.
  - "How much disagreement the items admit": the share of cells where every instructor's binned score
    is identical, and the share of instructor marks at 0 or full (normalised <= 0.01 or >= 99.99), for
    all cells, the bare-option cells, the open cells and the open cells by type.

INPUT. The registered corpus `harmogen-r` (data/data-sources.json; env HARMOGEN_DIR; the Zenodo file
harmogenr_dataset_v2.zip, md5 68a8a970e4b5f2e833fd5f8c686d5a89, sha256 d83ee9e6...0206; CC BY 4.0). It
reads csv/tables/questions.csv, student_responses.csv and evaluations.csv, from an extracted copy
(`--root` is the extracted harmogenr_dataset_v2/ folder, or a folder holding it) or, if none is
extracted, straight from the zip in that folder. Corpus text never enters the repository or the output:
only counts and agreement statistics are written, to out/results.json. Python standard library only.

    python3 studies/measurement/grader-harmogen-ceiling/harmogen.py --root <HARMOGEN_DIR>

HOW IT WAS PORTED (2026-10-15, Paper VI corrections-20; scope-audit-20 finding 2). The original is
TypeScript in the evaluation harness, which the release does not publish:
studies/measurement/grader-eval/harness/harmogen.ts (`loadHarmogen`, `harmogenPairs`, `toLevel`,
`spearman`), its caller `runHarmogen` in harness/stability.ts (`--mode harmogen`), the CSV parser `parse`
in harness/menagerie.ts and `agreement` / `quadraticWeightedKappa` / `pearson` in harness/metrics.ts, at
the commit the release declares (21487fe; the HARMOGEN-R code is unchanged from there to the port). Each
function is translated line for line, keeping the JavaScript semantics that can move a value:
  - Math.round rounds halves up (toward +infinity); Python's round() rounds them to even. Ported as
    floor(x + 0.5).
  - Number() of a string: "" and whitespace give 0, anything not a decimal number gives NaN. The original
    drops an evaluation whose score is "" before converting, and drops one whose normalised score is not
    finite; a question whose maximum is not > 0 is skipped. Ported as such.
  - The CSV parser is the harness's own, not Python's csv module: a double quote anywhere opens a quoted
    section, "" inside one is a literal quote, a carriage return outside quotes is dropped, and any row
    whose cell count differs from the header's is dropped. The byte-order mark at the start of each file
    is removed first, as the original does.
  - JavaScript's \\s (including U+FEFF) and its $ (end of string only, unlike Python's $, which also
    matches before a final newline) in the bare-option expression.
  - Sums are accumulated left to right in the original's order, so the floating-point results match.
The original prints a text table; the port writes the same quantities, unrounded, to JSON. Nothing was
re-designed. Three additions are reported separately under `descriptives`, because records that ship
with the release print them and the TypeScript mode does not compute them: the counts that describe the
corpus (cells, responses, variants, evaluations, bare-option responses and their share per question,
response lengths); the same three constructions by question type over ALL cells, bare-option ones
included (the observation record's "text 0.986 / 0.988" and "text 80% unanimous"); and
`unbinned_machine_human_bias` (added 2026-10-15, Paper VI corrections-21; scope-audit-21 finding 2). The
last is the mean of LLM minus instructor over the same machine-human pairs, on the normalised 0-100
scores BEFORE binning, in points: the figure comparable with the data paper's reported -2.02%. The binned
mean_bias in `by_levels` is unchanged; it converts to points only through the bin width (x 5 at 21
levels). The additions use the same cells and the same pair order as the ported code.

CHECKED AGAINST THE ORIGINAL. Before the output was committed, the original TypeScript (harmogen.ts,
menagerie.ts and metrics.ts, unmodified apart from the import's file extension) was run under Node 22.22
on the same extracted tables, with a ten-line driver that mirrors `runHarmogen` and prints the unrounded
values instead of its text table. All 538 values it produces (both binnings: every block, construction
and statistic, and the unanimity and extreme-mark shares) are bit-identical to this port's. The port reads
the tables from the zip or from an extracted copy; both give a byte-identical out/results.json.

PRE-SPECIFIED: no. This is a port of an analysis first run on 2026-09-15 (findings/grader-evaluation.md,
"A third corpus, and it breaks the generalisation"); its numbers were printed before the port existed and
the port was checked against them, not the other way round.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEVELS = (21, 11)  # HARMOGEN_LEVELS in harmogen.ts
TABLES = ("questions.csv", "student_responses.csv", "evaluations.csv")

# JavaScript's \s: ECMAScript WhiteSpace and LineTerminator, which include U+FEFF.
_JS_WS = "\t\n\v\f\r \u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000\ufeff"
BARE_OPTION = re.compile(rf"^[{_JS_WS}]*[A-Ea-e][{_JS_WS}]*[).]?[{_JS_WS}]*\Z")
_JS_DECIMAL = re.compile(r"^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$")
_JS_STRIP = re.compile(rf"^[{_JS_WS}]+|[{_JS_WS}]+$")


def js_number(s: str) -> float:
    """JavaScript Number(string) for the forms a CSV cell can take."""
    t = _JS_STRIP.sub("", s)
    if t == "":
        return 0.0
    if t in ("Infinity", "+Infinity"):
        return math.inf
    if t == "-Infinity":
        return -math.inf
    return float(t) if _JS_DECIMAL.match(t) else math.nan


def js_round(x: float) -> int:
    """Math.round: halves toward +infinity."""
    return math.floor(x + 0.5)


def js_mean(xs: list[float]) -> float:
    """xs.reduce((a, b) => a + b, 0) / xs.length (NaN for an empty list, as in JavaScript)."""
    s = 0.0
    for x in xs:
        s += x
    return s / len(xs) if xs else math.nan


def parse(text: str) -> list[dict[str, str]]:
    """menagerie.ts parse(): the harness's CSV reader, character for character."""
    rows: list[list[str]] = []
    row: list[str] = []
    cell: list[str] = []
    quoted = False
    i, n = 0, len(text)
    special = re.compile(r'["\n\r,]')
    while i < n:
        if quoted:
            j = text.find('"', i)
            if j < 0:
                cell.append(text[i:])
                break
            cell.append(text[i:j])
            if j + 1 < n and text[j + 1] == '"':
                cell.append('"')
                i = j + 2
            else:
                quoted = False
                i = j + 1
            continue
        m = special.search(text, i)
        if not m:
            cell.append(text[i:])
            break
        j = m.start()
        cell.append(text[i:j])
        ch = text[j]
        if ch == '"':
            quoted = True
        elif ch == ",":
            row.append("".join(cell))
            cell = []
        elif ch == "\n":
            row.append("".join(cell))
            rows.append(row)
            row, cell = [], []
        # "\r" outside quotes is dropped
        i = j + 1
    tail = "".join(cell)
    if tail or row:
        row.append(tail)
        rows.append(row)
    header = rows.pop(0) if rows else []
    return [dict(zip(header, r)) for r in rows if len(r) == len(header)]


def to_level(normalised: float, levels: int) -> int:
    step = 100 / (levels - 1)
    return min(levels - 1, max(0, js_round(normalised / step)))


# ------------------------------------------------------------------ metrics.ts

def _sd(xs: list[float]) -> float:
    m = js_mean(xs)
    return math.sqrt(js_mean([(x - m) ** 2 for x in xs]))


def pearson(a: list[float], b: list[float]) -> float:
    ma, mb = js_mean(a), js_mean(b)
    num = da = db = 0.0
    for x, y in zip(a, b):
        num += (x - ma) * (y - mb)
        da += (x - ma) ** 2
        db += (y - mb) ** 2
    den = math.sqrt(da * db)
    return 0.0 if den == 0 else num / den


def qwk(human: list[float], model: list[float], lo: int, hi: int) -> float:
    levels = hi - lo + 1
    if levels < 2 or not human:
        return 0.0
    ix = lambda x: min(levels - 1, max(0, js_round(x) - lo))  # noqa: E731
    obs = [[0] * levels for _ in range(levels)]
    hh, mh = [0] * levels, [0] * levels
    for h, m in zip(human, model):
        i, j = ix(h), ix(m)
        obs[i][j] += 1
        hh[i] += 1
        mh[j] += 1
    n = len(human)
    num = den = 0.0
    for i in range(levels):
        for j in range(levels):
            w = (i - j) ** 2 / (levels - 1) ** 2
            num += w * obs[i][j]
            den += w * ((hh[i] * mh[j]) / n)  # the original's `expected`, then the weight
    return 0.0 if den == 0 else 1 - num / den


def agreement(human: list[float], model: list[float], lo: int, hi: int) -> dict:
    errors = [m - h for h, m in zip(human, model)]
    sdh = _sd(human)
    return {
        "n": len(human),
        "qwk": qwk(human, model, lo, hi),
        "mae": js_mean([abs(e) for e in errors]),
        "rmse": math.sqrt(js_mean([e ** 2 for e in errors])),
        "pearson": pearson(human, model),
        "spread_ratio": 0.0 if sdh == 0 else _sd(model) / sdh,
        "mean_bias": js_mean(errors),
    }


def spearman(a: list[float], b: list[float]) -> float:
    """harmogen.ts spearman(): Pearson on midranks."""
    def rank(xs):
        order = sorted(range(len(xs)), key=lambda k: xs[k])
        out = [0.0] * len(xs)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
                j += 1
            r = (i + j) / 2 + 1
            for k in range(i, j + 1):
                out[order[k]] = r
            i = j + 1
        return out
    return pearson(rank(a), rank(b))


# ------------------------------------------------------------------ harmogen.ts

def find_tables(root: Path) -> dict[str, str]:
    """The three tables as text, BOM removed: from an extracted deposit, or from the zip."""
    for base in (root, root / "harmogenr_dataset_v2"):
        t = base / "csv" / "tables"
        if all((t / n).is_file() for n in TABLES):
            return {n: (t / n).read_bytes().decode("utf-8") for n in TABLES}
    z = root / "harmogenr_dataset_v2.zip" if root.is_dir() else root
    if z.is_file():
        with zipfile.ZipFile(z) as zf:
            return {n: zf.read(f"harmogenr_dataset_v2/csv/tables/{n}").decode("utf-8") for n in TABLES}
    sys.exit(f"no csv/tables/{{{','.join(TABLES)}}} and no harmogenr_dataset_v2.zip under {root}")


def load(texts: dict[str, str]):
    """loadHarmogen(): one item per (response, rubric variant), with every rating anyone gave it."""
    read = lambda n: parse(re.sub("^\ufeff", "", texts[n]))  # noqa: E731
    questions = {}
    for q in read("questions.csv"):
        questions[q["id"]] = {"type": q["type"], "max": js_number(q["score"]),
                              "assignment": q["assignment_id"]}  # the last is for `descriptives` only
    response_question, bare, responses = {}, {}, {}
    for r in read("student_responses.csv"):
        response_question[r["id"]] = r["question_id"]
        bare[r["id"]] = bool(BARE_OPTION.match(r["response"]))
        responses[r["id"]] = r
    items: dict[str, dict] = {}
    for e in read("evaluations.csv"):
        if e["is_active"] != "1" or e["score"] == "":
            continue
        qid = response_question.get(e["student_response_id"])
        q = questions.get(qid) if qid is not None else None
        if q is None or not (q["max"] > 0):
            continue
        key = f"{e['student_response_id']}|{e['source_question_criteria']}"
        it = items.get(key)
        if it is None:
            it = items[key] = {
                "response_id": e["student_response_id"], "rubric": e["source_question_criteria"],
                "question_id": qid, "question_type": q["type"],
                "bare_option": bare.get(e["student_response_id"], False), "q_max": q["max"],
                "teachers": [], "llms": [],
            }
        normalised = (js_number(e["score"]) / q["max"]) * 100
        if not math.isfinite(normalised):
            continue
        if e["evaluator_type"] == "teacher":
            it["teachers"].append(normalised)
        else:
            it["llms"].append((e["evaluator_id"], normalised))
    return list(items.values()), questions, responses


def pairs(items: list[dict], levels: int):
    """harmogenPairs()."""
    mh, hh, ag = ([], []), ([], []), ([], [])
    L = lambda x: to_level(x, levels)  # noqa: E731
    for it in items:
        t = it["teachers"]
        if len(t) < 2:
            continue
        for i in range(len(t)):
            for k in range(i + 1, len(t)):
                hh[0].append(L(t[i]))
                hh[1].append(L(t[k]))
        for _, s in it["llms"]:
            for x in t:
                mh[0].append(L(x))
                mh[1].append(L(s))
        if it["llms"]:
            ag[0].append(L(js_mean(t)))
            ag[1].append(L(js_mean([s for _, s in it["llms"]])))
    return {"machine_human": mh, "human_human": hh, "aggregate": ag}


def block(sel: list[dict], levels: int) -> dict | None:
    """runHarmogen()'s `block`: the three constructions, each with agreement() and rho."""
    if not sel:
        return None
    out = {"cells": len(sel)}
    for name, (h, m) in pairs(sel, levels).items():
        if h:
            out[name] = {**agreement(h, m, 0, levels - 1), "rho": spearman(h, m)}
    return out


def unanimous(sel, levels):
    return sum(1 for i in sel if len({to_level(t, levels) for t in i["teachers"]}) == 1) / len(sel)


def extreme(sel):
    marks = [t for i in sel for t in i["teachers"]]
    return sum(1 for x in marks if x <= 0.01 or x >= 99.99) / len(marks)


def analyse(items: list[dict], levels: int) -> dict:
    types = sorted({i["question_type"] for i in items})
    rubrics = sorted({i["rubric"] for i in items})
    open_ = [i for i in items if not i["bare_option"]]
    admit = {"all": items, "bare_option": [i for i in items if i["bare_option"]], "open": open_}
    admit.update({f"open_{t}": [i for i in open_ if i["question_type"] == t] for t in types})
    blocks = {"all": block(items, levels),
              "bare_option": block([i for i in items if i["bare_option"]], levels),
              "open": block(open_, levels)}
    blocks.update({f"open_{t}": block([i for i in open_ if i["question_type"] == t], levels) for t in types})
    blocks.update({f"rubric_{r}": block([i for i in items if i["rubric"] == r], levels) for r in rubrics})
    return {
        "levels": levels,
        "cells": len(items),
        "responses": len({i["response_id"] for i in items}),
        "rubric_variants": rubrics,
        "instructors_per_cell": sorted({len(i["teachers"]) for i in items}),
        "disagreement_admitted": {k: {"cells": len(v), "unanimous_share": unanimous(v, levels),
                                      "marks_at_0_or_full_share": extreme(v)} for k, v in admit.items() if v},
        "blocks": {k: v for k, v in blocks.items() if v},
    }


def descriptives(items: list[dict], questions: dict, responses: dict) -> dict:
    """Corpus counts the records print, and the constructions by question type over all cells."""
    rids = {i["response_id"] for i in items}
    resp = [responses[r] for r in sorted(rids, key=int)]
    bare = [r for r in resp if BARE_OPTION.match(r["response"])]
    per_q = {}
    for r in resp:
        d = per_q.setdefault(r["question_id"], {"type": questions[r["question_id"]]["type"], "responses": 0,
                                                "bare_option": 0})
        d["responses"] += 1
        d["bare_option"] += bool(BARE_OPTION.match(r["response"]))
    for d in per_q.values():
        d["bare_option_share"] = d["bare_option"] / d["responses"]

    def median(xs):
        xs = sorted(xs)
        k = len(xs)
        return (xs[(k - 1) // 2] + xs[k // 2]) / 2 if k else None

    text_q = [q for q, d in per_q.items() if d["type"] == "text"]
    mostly_bare = [q for q in text_q if per_q[q]["bare_option"] > 0]
    llm_models = sorted({m for i in items for m, _ in i["llms"]}, key=lambda s: (len(s), s))
    # ADDITION (corrections-21), not part of the ported TypeScript: the machine-human pairs of
    # harmogenPairs() (cells with at least two instructors; each LLM evaluation against each
    # instructor, in that order), on the unbinned normalised 0-100 scores, LLM minus instructor.
    unbinned = [s - x for it in items if len(it["teachers"]) >= 2 for _, s in it["llms"] for x in it["teachers"]]
    by_type_all = {}
    for lv in LEVELS:
        by_type_all[str(lv)] = {}
        for t in sorted({i["question_type"] for i in items}):
            sel = [i for i in items if i["question_type"] == t]
            b = block(sel, lv)
            b["unanimous_share"] = unanimous(sel, lv)
            by_type_all[str(lv)][t] = b
    return {
        "responses": len(rids),
        "questions": {t: sum(1 for d in per_q.values() if d["type"] == t) for t in ("text", "code")},
        "assignments": len({questions[q]["assignment"] for q in per_q}),
        "instructor_evaluations": sum(len(i["teachers"]) for i in items),
        "llm_evaluations": sum(len(i["llms"]) for i in items),
        "llm_evaluator_ids": llm_models,
        "llm_evaluations_per_cell": sorted({len(i["llms"]) for i in items}),
        "bare_option_responses": len(bare),
        "bare_option_cells": sum(1 for i in items if i["bare_option"]),
        "open_cells": sum(1 for i in items if not i["bare_option"]),
        "median_length_bare_option_responses": median([len(r["response"]) for r in bare]),
        "text_questions_with_bare_options": len(mostly_bare),
        "bare_option_share_range_on_those": [min(per_q[q]["bare_option_share"] for q in mostly_bare),
                                             max(per_q[q]["bare_option_share"] for q in mostly_bare)]
        if mostly_bare else None,
        "per_question": dict(sorted(per_q.items(), key=lambda kv: int(kv[0]))),
        "by_question_type_all_cells": by_type_all,
        "unbinned_machine_human_bias": {
            "note": "ADDITION, not in the TypeScript mode: mean of LLM minus instructor over the "
                    "machine_human pairs, on normalised 0-100 scores before binning; points, negative means "
                    "the LLM marks below the instructor",
            "n": len(unbinned),
            "mean_bias_points": js_mean(unbinned),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", type=Path, required=True,
                    help="HARMOGEN_DIR: the extracted harmogenr_dataset_v2/, a folder holding it, or the zip's folder")
    ap.add_argument("--out", type=Path, default=HERE / "out" / "results.json")
    a = ap.parse_args()
    texts = find_tables(a.root)
    items, questions, responses = load(texts)
    result = {
        "analysis": "harmogen-reanalysis (release ai-grader-reliability-2026); a Python port of "
                    "grader-eval/harness/harmogen.ts and stability.ts --mode harmogen",
        "input": {n: {"md5": hashlib.md5(texts[n].encode("utf-8")).hexdigest(),
                      "characters": len(texts[n])} for n in TABLES},
        "note": "Unrounded. QWK, MAE, RMSE and bias are in binned levels (0..levels-1); mean_bias is "
                "model - human (negative: the LLM marks below the instructor). Human-human pairs put the "
                "earlier instructor in file order in the human slot.",
        "by_levels": {str(lv): analyse(items, lv) for lv in LEVELS},
        "descriptives": descriptives(items, questions, responses),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    r = result["by_levels"]["21"]["blocks"]
    print(f"{result['by_levels']['21']['cells']} cells; instructor ceiling, 21 levels: "
          f"all {r['all']['human_human']['qwk']:.3f} (n {r['all']['human_human']['n']}), "
          f"bare option {r['bare_option']['human_human']['qwk']:.3f}, open {r['open']['human_human']['qwk']:.3f}")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
