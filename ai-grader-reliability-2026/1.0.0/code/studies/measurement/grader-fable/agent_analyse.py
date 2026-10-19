"""
Amendment 1 analysis: Fable 5.1 as an agent (Claude Code subagents grading rendered batches).

The plan, estimand and verdicts are fable.py's, unchanged; the route and its differences are
Amendment 1 (fable.py docstring, README). This script never reads the corpus. It reads, from the
session scratchpad:
  <scratch>/fable-agent/batches/batch_NN.md, key.json   checked against out/agent-manifest.json first,
                                                        so the key cannot have changed since it was
                                                        committed
  <scratch>/fable-agent/results/batch_NN.json           what each agent returned (its final message,
                                                        saved verbatim by the orchestrator)
  <scratch>/fable/draw300.json                          the draw's per-answer metadata (ids, learner,
                                                        tail, teacher mark, the two labels)

PARSE RULE (pre-registered, Amendment 1). A results file is read as one JSON array after stripping
surrounding whitespace and AT MOST ONE enclosing Markdown code fence (```json ... ``` or ``` ... ```;
the count of fenced files is reported). If that fails, or the file is absent, all 10 of that batch's
items are missing. Within an array, an element counts only if it is an object whose `item_id` is one
of THIS batch's ids and appears once in the array, whose `score` is a JSON number (not a boolean or
string) within the schema's [0, 10], and whose `evaluation` is a string; extra fields are ignored.
Anything else, and any of the batch's ids not returned, is a missing item. An answer with either arm
missing is dropped (complete pairs only, as fable.py). If MORE THAN 20 OF THE 100 ANSWERS (20%) lack
a complete pair, the verdict is UNRESOLVED whatever the interval says; the missing-item and
dropped-pair counts are always reported.

OUTPUT. The per-case dump is rebuilt in the harness's attainment-swap dump format (stability.ts
runAttainmentSwap: model, runStamp, temperature, reasoning, arms, ids, run, rows of {id, questionId,
learnerId, tail, human, labelTrue, labelSwapped, control, trueLabel, swappedLabel}, rows in draw
order) and written to <scratch>/fable-agent/swap-fable-agent.json, so it can be hashed into the
release's per-case-dump record and stripped like every other dump; its sha256 is in the output. The
agents' evaluations go to a separate scratch file (the harness dump does not carry them). Statistics
are fable.py's `cluster_stats` (paired bootstrap resampling learners within tail, 4,000 replicates,
seed 20261006) and `verdict`, on the rebuilt rows. out/agent-results.json holds L, L per tail, the
mark under each label against the teacher's, the verdict, the parse counts and the model the
orchestrator recorded. The result is "Fable 5.1 as an agent" and is never pooled with an API run.

NULL RULE (Amendment 1). The floor fell short in the Q2 noise shape (79.5% vs 80%), so a
NOT-DETECTED-BOUNDED or UNRESOLVED verdict is reported as underpowered (`underpowered_null: true`),
whatever the observed d SD; deviation 1's d-SD > 0.6 flag is reported beside it.

SELF-TEST (`--selftest`). Synthetic agent outputs on the real key and draw (planted L = +0.3, 0 and
-0.3; one fenced file; malformed items; a run with 25 answers missing) must recover the planted sign,
count every malformed item, and return UNRESOLVED when > 20% of pairs are missing. Written and scored
by the same session: a smoke check of the plumbing, reported as one, not a detection floor.

Usage:
  python3 agent_analyse.py --scratch <scratch> --model-served "<what the session's fable alias served>" \
      [--opus <scratch>/breadth/swap-opus55.json] [--exclude-batches 3,7]
  (--exclude-batches: batches whose agent read anything under <scratch>/fable-agent/; Amendment 1.)
  python3 agent_analyse.py --scratch <scratch> --selftest
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
sys.path.insert(0, str(HERE))
import fable  # noqa: E402  (cluster_stats, verdict, SEED: unchanged)

N_ANSWERS = 100
MAX_MISSING_PAIRS = 20  # > 20 of 100 answers without a complete pair -> UNRESOLVED
SCORE_MIN, SCORE_MAX = 0.0, 10.0
FENCE = re.compile(r"\A```[A-Za-z]*\s*\n(.*?)\n?```\Z", re.S)


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check_manifest(bdir: Path) -> dict:
    man = json.loads((OUT / "agent-manifest.json").read_text())
    for name, h in man["sha256"]["batches"].items():
        assert sha256_file(bdir / name) == h, f"{name} differs from the committed manifest"
    assert sha256_file(bdir / "key.json") == man["sha256"]["key.json"], "key.json differs from the committed manifest"
    return man


def parse_file(p: Path) -> tuple[list | None, bool, str | None]:
    """(array or None, fenced?, error)."""
    if not p.exists():
        return None, False, "absent"
    text = p.read_text().strip()
    fenced = False
    m = FENCE.match(text)
    if m:
        text, fenced = m.group(1).strip(), True
    try:
        arr = json.loads(text)
    except json.JSONDecodeError as e:
        return None, fenced, f"not JSON: {str(e)[:80]}"
    if not isinstance(arr, list):
        return None, fenced, "not an array"
    return arr, fenced, None


def read_results(rdir: Path, key: dict, excluded: frozenset[int] = frozenset()) -> tuple[dict, dict, dict]:
    """scores[(case, arm)], evaluations[(case, arm)], parse report."""
    by_batch: dict[int, set[str]] = {}
    for iid, k in key.items():
        by_batch.setdefault(k["batch"], set()).add(iid)
    scores, evals = {}, {}
    rep = {"files_absent": [], "files_unparsed": {}, "files_fenced": [], "items_missing": 0,
           "missing_reasons": {}, "items_ok": 0}

    def miss(reason: str, n: int = 1) -> None:
        rep["items_missing"] += n
        rep["missing_reasons"][reason] = rep["missing_reasons"].get(reason, 0) + n

    for b, ids in sorted(by_batch.items()):
        f = rdir / f"batch_{b:02d}.json"
        if b in excluded:  # its agent read under fable-agent/ (key or prompts): Amendment 1 exclusion
            rep.setdefault("batches_excluded", []).append(f.name)
            miss("batch excluded (agent read under fable-agent/)", len(ids))
            continue
        arr, fenced, err = parse_file(f)
        if fenced:
            rep["files_fenced"].append(f.name)
        if arr is None:
            (rep["files_absent"].append(f.name) if err == "absent" else rep["files_unparsed"].__setitem__(f.name, err))
            miss(f"batch file {err if err == 'absent' else 'unparsed'}", len(ids))
            continue
        counts: dict[str, int] = {}
        for el in arr:
            if isinstance(el, dict) and isinstance(el.get("item_id"), str):
                counts[el["item_id"]] = counts.get(el["item_id"], 0) + 1
        got = set()
        for el in arr:
            if not isinstance(el, dict):
                miss("element not an object"); continue
            iid = el.get("item_id")
            if not isinstance(iid, str) or iid not in ids:
                miss("item_id not of this batch"); continue
            if counts[iid] > 1:
                continue  # counted once below as duplicated
            s = el.get("score")
            if isinstance(s, bool) or not isinstance(s, (int, float)) or not (SCORE_MIN <= s <= SCORE_MAX):
                miss("score not a number in [0, 10]"); got.add(iid); continue
            if not isinstance(el.get("evaluation"), str):
                miss("evaluation not a string"); got.add(iid); continue
            k = key[iid]
            scores[(k["case_id"], k["arm"])] = float(s)
            evals[(k["case_id"], k["arm"])] = el["evaluation"]
            got.add(iid)
            rep["items_ok"] += 1
        for iid in ids:
            if counts.get(iid, 0) > 1:
                miss("item_id duplicated")
            elif iid not in got:
                miss("item not returned")
    # elements with a wrong item_id are extra; missing items are those of the 200 without a score
    rep["items_missing"] = 200 - rep["items_ok"]
    return scores, evals, rep


def rebuild_dump(scratch: Path, scores: dict, model_served: str | None, man: dict, results: dict) -> dict:
    draw = json.loads((scratch / "fable/draw300.json").read_text())["rows"]
    ids = set(json.loads((OUT / "draw.json").read_text())["answer_ids"])
    rows = []
    for r in draw:  # draw order, as the harness writes it
        if str(r["id"]) not in ids:
            continue
        rows.append({"id": r["id"], "questionId": r["questionId"], "learnerId": r["learnerId"], "tail": r["tail"],
                     "human": r["human"], "labelTrue": r["labelTrue"], "labelSwapped": r["labelSwapped"],
                     "control": None, "trueLabel": scores.get((str(r["id"]), "true")),
                     "swappedLabel": scores.get((str(r["id"]), "swapped"))})
    assert len(rows) == N_ANSWERS
    return {
        "model": "claude-code-subagent:fable (Fable 5.1 as an agent; grader-fable Amendment 1)",
        "runStamp": f"agent route, analysed {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}Z",
        "temperature": "not recorded (agent route)",
        "reasoning": "not recorded (agent route)",
        "arms": ["true", "swapped"],
        "ids": N_ANSWERS,
        "run": {"calls": 200, "failures": sum(v is None for r in rows for v in (r["trueLabel"], r["swappedLabel"])),
                "reportedSpendUsd": None, "tokens": None,
                "served": {model_served or "not recorded": 20},
                "wire": {"claude-code-subagent": {"batches_sha256": man["sha256"]["batches"],
                                                   "key_sha256": man["sha256"]["key.json"],
                                                   "results_sha256": results}}},
        "rows": rows,
    }


def analyse(scratch: Path, rdir: Path, model_served: str | None, opus: Path | None, dump_out: Path,
            excluded: frozenset[int] = frozenset()) -> dict:
    bdir = scratch / "fable-agent/batches"
    man = check_manifest(bdir)
    key = json.loads((bdir / "key.json").read_text())
    scores, evals, rep = read_results(rdir, key, excluded)
    results_sha = {f.name: sha256_file(f) for f in sorted(rdir.glob("batch_*.json"))}
    dump = rebuild_dump(scratch, scores, model_served, man, results_sha)
    dump_out.parent.mkdir(parents=True, exist_ok=True)
    dump_out.write_text(json.dumps(dump, indent=2))  # the harness's own serialisation: indent 2, no trailing newline
    (dump_out.with_name(dump_out.stem + ".evaluations.json")).write_text(
        json.dumps({f"{c}__{a}": e for (c, a), e in sorted(evals.items())}, indent=2, ensure_ascii=False) + "\n")
    rows = [r for r in dump["rows"] if r["trueLabel"] is not None and r["swappedLabel"] is not None]
    dropped = N_ANSWERS - len(rows)
    out = {
        "result_label": "Fable 5.1 as an agent (Claude Code subagents; Amendment 1). Never pooled with the API runs.",
        "model_served_recorded_by_orchestrator": model_served,
        "parse": {**rep, "pairs_complete": len(rows), "pairs_dropped": dropped,
                  "rule": "> 20 of 100 answers without a complete pair -> UNRESOLVED"},
        "dump": {"path": str(dump_out), "sha256": sha256_file(dump_out)},
        "results_sha256": results_sha,
    }
    if len(rows) < 3:
        out.update({"verdict": "UNRESOLVED", "verdict_reason": "fewer than 3 complete pairs"})
        return out
    res = fable.cluster_stats(rows, np.random.default_rng(fable.SEED))
    v_ci = fable.verdict(res["L"]["ci95"])
    v = "UNRESOLVED" if dropped > MAX_MISSING_PAIRS else v_ci
    out.update({
        "verdict": v,
        "verdict_from_interval": v_ci,
        "verdict_reason": "missing rule: > 20% of pairs dropped" if v != v_ci else "interval rule",
        "verdict_rule": {"PERSISTS": "95% CI > 0", "PERSISTS-REVERSED": "95% CI < 0",
                         "NOT-DETECTED-BOUNDED": f"95% CI inside (-{fable.MARGIN}, +{fable.MARGIN})", "UNRESOLVED": "otherwise"},
        "tail_readings_reported_only": {k: fable.verdict(res[f"L_{k}"]["ci95"]) for k in ("high", "low")},
        "fable_agent": res,
        "underpowered_null": v in ("NOT-DETECTED-BOUNDED", "UNRESOLVED"),
        "deviation_1_dsd_flag": bool(v == "UNRESOLVED" and res["d_sd"] > fable.UNDERPOWERED_SD),
        "frontier_verdict_note": "an agent-route result is reported beside, not inside, the model-breadth frontier verdict",
    })
    if opus:
        op_all = {str(r["id"]): r for r in json.loads(Path(opus).read_text())["rows"]}
        op_rows = [op_all[str(r["id"])] for r in rows]
        o = fable.cluster_stats(op_rows, np.random.default_rng(fable.SEED))
        diff = fable.cluster_stats([{**f, "trueLabel": f["trueLabel"] - p["trueLabel"], "swappedLabel": f["swappedLabel"] - p["swappedLabel"]}
                                    for f, p in zip(rows, op_rows)], np.random.default_rng(fable.SEED))
        out["opus55_api_same_answers_reported_only"] = {k: o[k] for k in ("L", "L_high", "L_low", "n_pairs", "d_sd")}
        out["fable_agent_minus_opus55_api_dL_reported_only"] = {k: diff[k] for k in ("L", "L_high", "L_low")}
    return out


# ----------------------------------------------------------------------------- self-test

def selftest(scratch: Path) -> None:
    bdir = scratch / "fable-agent/batches"
    key = json.loads((bdir / "key.json").read_text())
    draw = {str(r["id"]): r for r in json.loads((scratch / "fable/draw300.json").read_text())["rows"]}
    base = scratch / "fable-agent/selftest"

    def world(name: str, L: float, drop_answers: int = 0, malform: bool = False) -> dict:
        rng = np.random.default_rng([fable.SEED, int(1000 * (L + 1)), drop_answers, int(malform)])
        rdir = base / name
        if rdir.exists():
            shutil.rmtree(rdir)
        rdir.mkdir(parents=True)
        case_eff = {c: rng.normal(0, 1.0) for c in {k["case_id"] for k in key.values()}}
        dropped_cases = set(sorted(case_eff)[:drop_answers])
        batches: dict[int, list] = {}
        for iid, k in sorted(key.items(), key=lambda kv: (kv[1]["batch"], kv[1]["position"])):
            r = draw[k["case_id"]]
            high_shown = (k["arm"] == "true") == (r["tail"] == "high")
            s = r["human"] + case_eff[k["case_id"]] + (L / 2 if high_shown else -L / 2) + rng.normal(0, 0.4)
            s = float(np.clip(np.round(s * 2) / 2, 0, 10))
            if k["case_id"] in dropped_cases and k["arm"] == "swapped":
                continue
            batches.setdefault(k["batch"], []).append({"item_id": iid, "score": s, "evaluation": "synthetic"})
        expect_missing = drop_answers
        for b, arr in batches.items():
            text = json.dumps(arr)
            if malform and b == 1:
                text = "```json\n" + text + "\n```"  # fenced: must still parse
            if malform and b == 2:
                arr[0]["score"] = "7"; arr[1]["score"] = 11; arr[2].pop("evaluation"); arr[3]["item_id"] = "ffffffff"
                arr.append(dict(arr[4]))  # duplicate id
                text = json.dumps(arr)
                expect_missing += 5
            if malform and b == 3:
                text = "Here are the grades: " + text  # whole batch unparsed
                expect_missing += 10
            (rdir / f"batch_{b:02d}.json").write_text(text)
        res = analyse(scratch, rdir, "selftest", None, rdir / "dump.json")
        return {"res": res, "expect_missing_items": expect_missing}

    checks = {}
    w = world("plus", 0.3)
    checks["plus: PERSISTS"] = w["res"]["verdict"] == "PERSISTS"
    checks["plus: L near +0.3"] = abs(w["res"]["fable_agent"]["L"]["est"] - 0.3) < 0.1
    checks["plus: 0 missing"] = w["res"]["parse"]["items_missing"] == 0
    w = world("minus", -0.3)
    checks["minus: PERSISTS-REVERSED"] = w["res"]["verdict"] == "PERSISTS-REVERSED"
    w = world("null", 0.0)
    checks["null: no signed call"] = w["res"]["verdict"] in ("NOT-DETECTED-BOUNDED", "UNRESOLVED")
    checks["null: underpowered_null set"] = w["res"]["underpowered_null"] is True
    w = world("malformed", 0.3, malform=True)
    p = w["res"]["parse"]
    checks["malformed: fenced file parsed"] = p["files_fenced"] == ["batch_01.json"] and not p["files_unparsed"].get("batch_01.json")
    checks["malformed: unparsed file counted"] = "batch_03.json" in p["files_unparsed"]
    checks[f"malformed: {w['expect_missing_items']} items missing"] = p["items_missing"] == w["expect_missing_items"]
    w = world("missing25", 0.3, drop_answers=25)
    checks["missing25: UNRESOLVED by missing rule"] = (w["res"]["verdict"] == "UNRESOLVED"
                                                      and w["res"]["verdict_from_interval"] == "PERSISTS"
                                                      and w["res"]["parse"]["pairs_dropped"] == 25)
    rdir = base / "plus"
    r = analyse(scratch, rdir, "selftest", None, rdir / "dump-excl.json", frozenset({4}))
    checks["exclusion: batch 4 -> 10 items missing"] = r["parse"]["items_missing"] == 10 and r["parse"]["pairs_dropped"] == 10
    w = world("missing20", 0.3, drop_answers=20)
    checks["missing20: rule not triggered at exactly 20%"] = w["res"]["verdict"] == "PERSISTS"
    # the rebuilt dump reads back through fable.py's own d (breadth.hl) with the planted sign
    d = json.loads((base / "plus/dump.json").read_text())
    assert set(d) >= {"model", "runStamp", "temperature", "reasoning", "arms", "ids", "run", "rows"}
    checks["dump: harness format, 100 rows in draw order"] = (len(d["rows"]) == 100 and
        [r["id"] for r in d["rows"]] == [str(r["id"]) for r in json.loads((scratch / "fable/draw300.json").read_text())["rows"]
                                          if str(r["id"]) in set(json.loads((OUT / "draw.json").read_text())["answer_ids"])])
    for k, ok in checks.items():
        print(f"  {'ok  ' if ok else 'FAIL'} {k}")
    shutil.rmtree(base)
    if not all(checks.values()):
        sys.exit("selftest FAILED")
    print("SELFTEST PASS (smoke check: synthetic outputs written and scored by the same session)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", type=Path, required=True)
    ap.add_argument("--results", type=Path)
    ap.add_argument("--model-served")
    ap.add_argument("--opus", type=Path)
    ap.add_argument("--exclude-batches", default="", help="comma-separated batch numbers whose agent read under fable-agent/")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest(a.scratch)
        return
    rdir = a.results or a.scratch / "fable-agent/results"
    excl = frozenset(int(x) for x in a.exclude_batches.split(",") if x.strip())
    res = analyse(a.scratch, rdir, a.model_served, a.opus, a.scratch / "fable-agent/swap-fable-agent.json", excl)
    (OUT / "agent-results.json").write_text(json.dumps(res, indent=2) + "\n")
    p = res["parse"]
    print(f"items missing {p['items_missing']}/200, pairs complete {p['pairs_complete']}/100, fenced {len(p['files_fenced'])}")
    if "fable_agent" in res:
        f = res["fable_agent"]
        g = lambda k: f"{f[k]['est']:+.2f} [{f[k]['ci95'][0]:+.2f}, {f[k]['ci95'][1]:+.2f}]"  # noqa: E731
        print(f"Fable 5.1 as an agent: L {g('L')}  high {g('L_high')}  low {g('L_low')}  d SD {f['d_sd']:.2f}")
    print(f"-> {res['verdict']} ({res['verdict_reason']})")


if __name__ == "__main__":
    main()
