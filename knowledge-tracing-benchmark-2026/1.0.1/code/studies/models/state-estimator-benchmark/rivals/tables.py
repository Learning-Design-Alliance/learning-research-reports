"""The release's summary tables, computed from the per-case outputs (release knowledge-tracing-benchmark-2026).
Written 20 Nov 2026. DATA: reads no corpus; reads only per-case-outputs.jsonl (collect.py).

WHAT IT COMPUTES (every value unrounded; the article rounds once, from these):
  corpora   per corpus: learners and test rows summed over the five folds' test sets of the main fits
            (every model is scored on the same test rows, which the script checks), and the regimes run;
  main      per model and corpus: the main fits' test AUC (mean over the five folds, its minimum and maximum),
            log loss in nats per answer (mean over folds), the largest saturated share, the second training
            seed's fold-0 AUC minus the first seed's (deep models only), and the device;
  regimes   per model, corpus and regime: mean test AUC over the regime's fits (5 folds, or 5 draws x 5 folds
            at 10% and 2%), its minimum and maximum, and its difference from the main fits' mean;
  floors    per model, corpus and regime: the F1 record as written by the scorer, and the status the release
            prints beside each model's numbers (PASS at 25%, MISS at 25%, NOT RUN; IRT is the reference and
            exempt, DESIGN 7);
  gates     the gate records as collected, with each difference from its target;
  sizing    per corpus, the F1 effect size b chosen by the floor's sizing job, and (floor_O) the oracle's
            effect-minus-null difference O, its SE, O/2 and O/SE;
  fold_leads per corpus and ordered pair of models, the number of the five folds on which the first model's
            AUC is above the second's (both are scored on the same test learners);
  summary   the ranges of AUC loss the article's text states, by family and regime (RQ4), and the spread of
            the three highest means on half A (RQ3);
  ranks     per corpus, the models ordered by main mean AUC (descriptive: no comparison between two models
            is tested; the benchmark kept no per-row predictions, so no paired interval can be computed);
  prep      EDM Cup 2023's preprocessing report (the prep record), including the share of problem logs whose
            file order disagrees with time order (added 20 Nov 2026, corrections-2);
  device    per model with GPU fits, the pre-registered device band (Amendment 3) and twice it; and, per
            corpus, every pair of main means in which at least one model's fits ran on a GPU, with the margin,
            twice the larger band involved and whether the margin lies within it (the registered rule's
            "device-sensitive"; added 20 Nov 2026, corrections-2).

THE STATUS RULE (registered, DESIGN 7 and REGISTRATION "Pass rules"): a model's numbers on a corpus count only
when its F1 floor passes at 25% on that corpus; a model whose floor missed reads NOT READ (floor) there, and
one with no floor run reads NO FLOOR RUN. A model counts at the 2% regime only when its F1 passes at 2%.
The release prints every model's numbers with this status beside them. The floors of PFA, BKT and the running
proportion (run 16 Nov 2026 outside the registered stage lists, under no amendment) are descriptive only
(maintainer, R0597, 21 Nov 2026): whatever their reading, they read FLOOR DESCRIPTIVE, and those models' numbers
count no more than a model's with no floor run.

    python3 tables.py [--per-case <path>] [--out out/tables.json]
The per-case file is found at --per-case, else beside the release file (the published layout: this script
sits at code/studies/models/state-estimator-benchmark/rivals/), else in the repository's release folder.
"""
from __future__ import annotations

import argparse
import collections
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RELEASE = "knowledge-tracing-benchmark-2026"
CANDIDATES = [HERE.parents[4] / "per-case-outputs.jsonl",                         # published: <release>/code/...
              HERE.parents[3] / f"research/wiki/research/releases/{RELEASE}/per-case-outputs.jsonl"]   # repository
ORDER = ["IRT", "PFA", "Best-LR", "Best-LR-iter1000", "Best-LR+", "BKT", "running-proportion",
         "DKT", "AKT", "simpleKT", "IEKT", "HawkesKT", "LPKT"]
DEEP = {"DKT", "AKT", "simpleKT", "IEKT", "HawkesKT", "LPKT"}
UNREGISTERED_FLOOR = {"PFA", "BKT", "running-proportion"}     # floors outside the registered stage lists (R0597)
CORPORA = ["kddcup2010-algebra0607:halfA", "kddcup2010-bridge06", "edmcup2023"]
SHORT = {"kddcup2010-algebra0607:halfA": "half A", "kddcup2010-bridge06": "bridge06", "edmcup2023": "EDM Cup"}
REGIMES = ["main", "quarter", "tenth", "fiftieth", "history-fifty", "history-twenty"]


def find(path: str | None) -> Path:
    for p in ([Path(path)] if path else CANDIDATES):
        if p.is_file():
            return p
    sys.exit("per-case-outputs.jsonl not found; pass --per-case")


def build(recs: list[dict]) -> dict:
    fits = [r for r in recs if r["record"] == "fit"]
    by = collections.defaultdict(list)
    for r in fits:
        by[(r["model"], r["corpus"], r["regime"])].append(r)
    out = {"release": RELEASE, "what": __doc__.split("\n")[0], "corpora": {}, "main": {}, "regimes": {},
           "floors": {}, "gates": [], "ranks": {}}
    for c in CORPORA:
        tests = {}
        for m in ORDER:
            rows = sorted(by.get((m, c, "main"), []), key=lambda r: r["fold"])
            if rows:
                tests[m] = [(r["fold"], r["n_test_learners"], r["n_test_rows"]) for r in rows]
        sets = {tuple(v) for v in tests.values()}
        assert len(sets) == 1, f"{c}: models scored on different test sets"
        (t,) = sets
        out["corpora"][c] = {"learners": sum(x[1] for x in t), "test_rows": sum(x[2] for x in t),
                             "folds": len(t), "models": [m for m in ORDER if m in tests]}
    for m in ORDER:
        for c in CORPORA:
            main = sorted(by.get((m, c, "main"), []), key=lambda r: r["fold"])
            if not main:
                continue
            assert [r["fold"] for r in main] == [0, 1, 2, 3, 4], (m, c)
            aucs = [r["auc"] for r in main]
            rec = {"auc_mean": statistics.fmean(aucs), "auc_min": min(aucs), "auc_max": max(aucs),
                   "auc_folds": aucs, "log_loss_mean": statistics.fmean(r["log_loss"] for r in main),
                   "saturated_share_max": max(r["saturated_share"] for r in main),
                   "saturated_share_min": min(r["saturated_share"] for r in main),
                   "devices": sorted({r["device"] for r in by[(m, c, "main")]})}
            s1 = by.get((m, c, "seed1"), [])
            if s1:
                (s,) = s1
                rec["seed1_f0_auc"] = s["auc"]
                rec["seed1_minus_seed0_f0"] = s["auc"] - aucs[0]
            out["main"].setdefault(m, {})[c] = rec
            for g in REGIMES:
                rs = by.get((m, c, g), [])
                if not rs:
                    continue
                a = [r["auc"] for r in rs]
                out["regimes"].setdefault(m, {}).setdefault(c, {})[g] = {
                    "n_fits": len(a), "auc_mean": statistics.fmean(a), "auc_min": min(a), "auc_max": max(a),
                    "minus_main": statistics.fmean(a) - rec["auc_mean"]}
    for r in recs:
        if r["record"] == "floor":
            out["floors"].setdefault(r["model"], {}).setdefault(r["corpus"], {})[r["regime"]] = {
                k: r[k] for k in ("O", "O_se", "G_E", "G_N", "G_N_ci95", "G_E_minus_G_N", "G_E_minus_G_N_ci95",
                                  "reading", "n_test_learners", "n_test_rows")}
    status = {}
    for m in ORDER:
        for c in CORPORA:
            if m not in out["main"] or c not in out["main"][m]:
                continue
            f = out["floors"].get(m, {}).get(c, {})
            q, s = f.get("quarter", {}).get("reading"), f.get("fiftieth", {}).get("reading")
            if m == "IRT":
                st = "REFERENCE (exempt)"
            elif m in UNREGISTERED_FLOOR and q is not None:
                st = "FLOOR DESCRIPTIVE"
            elif q == "PASS":
                st = "PASS"
            elif q is None:
                st = "NO FLOOR RUN"
            else:
                st = "NOT READ (floor)"
            status.setdefault(m, {})[c] = {"status": st, "f1_25": q or "NOT RUN", "f1_2": s or "NOT RUN"}
    out["status"] = status
    for r in recs:
        if r["record"] == "gate":
            g = dict(r)
            if g.get("kind") == "pykt":
                g["diff"] = g["repro_diff"]
            (out["gates"] if g["attempt"] == "counted" else out.setdefault("gates_first", [])).append(g)
    for c in CORPORA:
        ms = [m for m in ORDER if c in out["main"].get(m, {})]
        out["ranks"][c] = sorted(ms, key=lambda m: -out["main"][m][c]["auc_mean"])
    # per corpus and ordered pair of models: on how many of the five folds (the same test learners for both)
    # the first model's AUC is above the second's. Descriptive: a count, not a test.
    out["fold_leads"] = {c: {a: {b: sum(x > y for x, y in zip(out["main"][a][c]["auc_folds"],
                                                              out["main"][b][c]["auc_folds"]))
                                 for b in ORDER if c in out["main"].get(b, {}) and b != a}
                             for a in ORDER if c in out["main"].get(a, {})} for c in CORPORA}
    # flat views for the article's long tables: "<model> / <corpus short name>"
    out["by_row"] = {f"{m} / {SHORT[c]}": {"main": out["main"][m][c], "regimes": out["regimes"][m][c],
                                           **out["status"][m][c]}
                     for m in ORDER for c in CORPORA if c in out["main"].get(m, {})}
    out["sizing"] = {r["corpus"]: r for r in recs if r["record"] == "sizing"}
    out["floor_O"] = {}
    for m, cs in out["floors"].items():
        for c, rs in cs.items():
            for g, r in rs.items():
                o = out["floor_O"].setdefault(c, {"O": r["O"], "O_se": r["O_se"], "half_O": r["O"] / 2,
                                                  "O_over_se": r["O"] / r["O_se"]})
                assert o["O"] == r["O"], (m, c, g)      # one effect world per corpus, the same for every model
    seeds = [(abs(out["main"][m][c]["seed1_minus_seed0_f0"]), m, c) for m in DEEP for c in CORPORA
             if "seed1_minus_seed0_f0" in out["main"].get(m, {}).get(c, {})]
    out["seed_max_abs"] = {"value": max(seeds)[0], "model": max(seeds)[1], "corpus": max(seeds)[2],
                           "n": len(seeds)}
    out["summary"] = summary(out)
    (prep,) = [r for r in recs if r["record"] == "prep"]
    out["prep"] = prep
    out["device"] = device(out, [r for r in recs if r["record"] == "device_band"])
    return out


def device(out: dict, bands: list[dict]) -> dict:
    """The registered device-sensitivity rule (Amendment 3), applied to the main means."""
    b = {r["model"]: {"band": r["band"], "two_x_band": 2 * r["band"], "gpu": r["gpu"], "n_cells": r["n_cells"]}
         for r in bands}
    pairs = {}
    for c in CORPORA:
        gpu = [m for m in ORDER if c in out["main"].get(m, {}) and "cuda" in out["main"][m][c]["devices"]]
        assert set(gpu) <= set(b), (c, gpu)
        ms = [m for m in ORDER if c in out["main"].get(m, {})]
        for i, x in enumerate(ms):
            for y in ms[i + 1:]:
                inv = [m for m in (x, y) if m in gpu]
                if not inv:
                    continue
                margin = abs(out["main"][x][c]["auc_mean"] - out["main"][y][c]["auc_mean"])
                lim = max(b[m]["two_x_band"] for m in inv)
                pairs.setdefault(c, {})[f"{x} | {y}"] = {"margin": margin, "two_x_band": lim,
                                                        "device_sensitive": margin <= lim, "gpu_models": inv}
    return {"bands": b, "pairs": pairs}


LOGISTIC = ["PFA", "Best-LR", "Best-LR-iter1000", "Best-LR+"]
ATTENTION = ["AKT", "simpleKT"]
RECURRENT_KDD = ["DKT", "IEKT", "LPKT"]
KDD = CORPORA[:2]


def summary(out: dict) -> dict:
    """The ranges the article's text states (RQ3, RQ4), from the unrounded values."""
    def loss(m, c, g):
        return -out["regimes"][m][c][g]["minus_main"]

    def rng(cells):
        v = [loss(m, c, g) for m, c, g in cells]
        return {"min": min(v), "max": max(v), "n": len(v)}
    read = lambda m, c: out["status"][m][c]["status"] != "NOT READ (floor)"
    deep2 = [(m, c, "fiftieth") for m in sorted(DEEP) for c in CORPORA if c in out["main"].get(m, {}) and read(m, c)]
    s = {"deep_2pct": rng(deep2),
         "logistic_2pct": rng([(m, c, "fiftieth") for m in LOGISTIC for c in CORPORA]),
         "bkt_2pct": rng([("BKT", c, "fiftieth") for c in CORPORA]),
         "irt_2pct": rng([("IRT", c, "fiftieth") for c in CORPORA]),
         "attention_2pct_kdd": rng([(m, c, "fiftieth") for m in ATTENTION for c in KDD]),
         "recurrent_2pct_kdd": rng([(m, c, "fiftieth") for m in RECURRENT_KDD for c in KDD]),
         "logistic_h20_kdd": rng([(m, c, "history-twenty") for m in LOGISTIC for c in KDD]),
         "attention_h20_kdd": rng([(m, c, "history-twenty") for m in ATTENTION for c in KDD]),
         "bkt_h20_kdd": rng([("BKT", c, "history-twenty") for c in KDD]),
         "logistic_2pct_kdd": rng([(m, c, "fiftieth") for m in LOGISTIC for c in KDD]),
         "bestlr_2pct_kdd": rng([(m, c, "fiftieth") for m in LOGISTIC[1:] for c in KDD]),
         "logistic_2pct_edm": rng([(m, "edmcup2023", "fiftieth") for m in LOGISTIC]),
         "deep_2pct_edm": rng([(m, "edmcup2023", "fiftieth") for m in sorted(DEEP) if "edmcup2023" in out["main"][m]]),
         "irt_h20_kdd": rng([("IRT", c, "history-twenty") for c in KDD]),
         "recurrent_h20_kdd": rng([(m, c, "history-twenty") for m in RECURRENT_KDD for c in KDD]),
         "all_h20_edm": rng([(m, "edmcup2023", "history-twenty") for m in ORDER
                             if m != "running-proportion" and "edmcup2023" in out["main"].get(m, {})])}
    h = "kddcup2010-algebra0607:halfA"
    top3 = out["ranks"][h][:3]
    s["halfA_top3"] = {"models": top3, "spread": out["main"][top3[0]][h]["auc_mean"] - out["main"][top3[2]][h]["auc_mean"]}
    return s


def crosscheck(out: dict) -> None:
    """Repository only: the main means agree with the benchmark's own per-rival table (R0439)."""
    p = HERE.parent / "out/plan2/rival-table-2026-11-15.json"
    if not p.exists():
        return
    n = 0
    for row in json.loads(p.read_text())["rows"]:
        m, c = row["model"], row["corpus"]
        if m in out["main"] and c in out["main"][m]:
            assert abs(out["main"][m][c]["auc_mean"] - row["main_auc_mean"]) < 1e-12, (m, c)
            n += 1
    print(f"crosscheck: {n} main means equal the per-rival table's")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-case")
    ap.add_argument("--out", default=str(HERE / "out/tables.json"))
    a = ap.parse_args()
    p = find(a.per_case)
    recs = [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
    out = build(recs)
    crosscheck(out)
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
