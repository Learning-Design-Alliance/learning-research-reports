"""Per-case outputs of the knowledge-tracing benchmark's published rivals and baselines (release
knowledge-tracing-benchmark-2026). Written 20 Nov 2026.

WHAT. One JSON line per scored job of the models this release reports, built from the benchmark's
committed per-job aggregates and gate records and from nothing else:

  record "fit"    one per scored fit: model, corpus, regime (main, seed1, quarter, tenth, fiftieth,
                  history-twenty, history-fifty), draw (the 10% and 2% subsets are drawn five times),
                  fold, device, the fold's test learners and rows, and the scorer's AUC, log loss
                  (nats per answer) and saturated share, unrounded;
  record "floor"  one per prediction-floor (F1) score: model, corpus, regime (quarter = 25% of the
                  training learners, fiftieth = 2%), the oracle's effect-minus-null difference O and
                  its SE, G_E, G_N with its 95% interval, G_E - G_N with its 95% interval, and the
                  scorer's reading (PASS or MISS);
  record "sizing" one per corpus: the F1 effect size b its sizing job chose from the grid {0.3, 0.45, 0.6,
                  0.9} (the smallest at which O is at least 6 times its SE over five twin pairs);
  record "gate"   one per gate reproduction of a published number: model, corpus, target and its
                  source, the benchmark's value, and for the pyKT rivals pyKT's own loop and the
                  differences the gate reads; HawkesKT's and LPKT's failed first attempts are kept
                  beside their counted gates (`attempt`);
  record "prep"   one: EDM Cup 2023's preprocessing report, as the registered prep job wrote it (counts
                  only: action lines, problem logs, those whose file order disagrees with time order,
                  duplicates dropped, multi-code and no-code problems, rows, learners);
  record "device_band" one per model with fits on a GPU: the pre-registered device control (Amendment 3),
                  each sampled cell's GPU-minus-CPU AUC difference and the band (their largest absolute
                  value); a verdict involving the model whose margin is within twice the band is reported
                  as device-sensitive. Added 20 Nov 2026 (corrections-2).

A fit is an aggregate over one fold's test learners. No learner, row, prediction or identifier is
written, and no corpus is read, so this script needs none. Floats are the committed values, unrounded.

THE REPORTED MODELS are the list REPORTED below and only those: an aggregate whose model is not on it
is never opened. The list is the release's scope (R0553, R0554).

WHICH COPY COUNTS (the rules of the benchmark's own per-rival table, R0380, R0396, R0437, R0439):
  - a job counts when an aggregate with status "done" was pushed for it;
  - HawkesKT's half A, bridge06 and EDM Cup fits and floors (blocks d, f, g) count only from the lanes
    run under Amendment 4 (lane name carries "-a4"); its earlier lanes ran a loop that failed its gate;
  - fits come from the registered stages' blocks (FIT_BLOCKS); the floor lanes (block "rr") contribute
    their F1 scores only;
  - where several lanes pushed the same job, the copy committed first counts; a later copy that differs
    is reported by `build` on stderr (none differed on 20 Nov 2026).
The gate records are read from the files named in GATES.

    python3 collect.py build  --out <path>   write the file (run from the repository, which holds the
                                             aggregates; the published release holds only the result)
    python3 collect.py verify --out <path>   rebuild in memory and compare byte for byte; exit 1 if different
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
REPO = HERE.parents[3]
OUT = STUDY / "out"

REPORTED = ["IRT", "PFA", "Best-LR", "Best-LR-iter1000", "Best-LR+", "BKT", "running-proportion",
            "DKT", "AKT", "simpleKT", "IEKT", "HawkesKT", "LPKT"]
SID_MODEL = {m.replace("+", "plus"): m for m in REPORTED}        # pushed job ids spell Best-LR+ "Best-LRplus"
CORPORA = {"algebra0607": "kddcup2010-algebra0607:halfA", "bridge06": "kddcup2010-bridge06",
           "edmcup2023": "edmcup2023", "edmcup": "edmcup2023"}     # the non-deep EDM Cup lanes write "edmcup"
FIT_BLOCKS = {"a", "d", "e", "f", "g", "h", "d2", "f2"}          # the registered stages' fits (the per-rival table's)
SID = re.compile(r"^(?P<block>[a-z0-9]+)_(?P<corpus>algebra0607|bridge06|edmcup2023|edmcup)_(?P<model>.+?)_"
                 r"(?P<rest>main_f\d|seed1_f\d|quarter_f\d|(tenth|fiftieth)_d\d_f\d|history-(twenty|fifty)_f\d|"
                 r"F1-(quarter|fiftieth)_score)$")

# gate records: (model, file, how to read it)
GATES = [
    ("IRT", "out/optionA/b/push/b_bridge06_IRT_gate_score/b_bridge06_IRT_gate_score-0.json", "gervet", .749),
    ("PFA", "out/optionA/b/push/b_bridge06_PFA_gate_score/b_bridge06_PFA_gate_score-0.json", "gervet", .741),
    ("PFA", "out/plan2/rr-b-PFA-gate/push/b_bridge06_PFA_gate_score/b_bridge06_PFA_gate_score-0.json",
     "gervet-amended", .761),
    ("Best-LR", "out/optionA/b/push/b_bridge06_Best-LR_gate_score/b_bridge06_Best-LR_gate_score-0.json",
     "gervet", .803),
    ("DKT", "out/optionA/b/push/b_bridge06_DKT_gate_score/b_bridge06_DKT_gate_score-0.json", "gervet", .790),
    ("AKT", "out/plan2/c-AKT/state.json", "pykt-state", None),
    ("simpleKT", "out/plan2/c-simpleKT/state.json", "pykt-state", None),
    ("IEKT", "out/plan2/c-IEKT/state.json", "pykt-state", None),
    ("HawkesKT", "out/hawkeskt-gate-amend4-r1-2026-11-13.json", "pykt-file", None),
    ("LPKT", "rivals/out/lpkt-gate-bridge06-r1.json", "pykt-flat", None),
]
# first attempts that failed (recorded, not counted): HawkesKT before Amendment 4, LPKT before its tuning
GATES_FIRST = [
    ("HawkesKT", "out/plan2/c-HawkesKT/state.json", "pykt-state"),
    ("LPKT", "out/lpkt-gate-bridge06-2026-11-13.json", "pykt-file"),
]
# the F1 effect size b chosen per corpus by the floor's sizing job (the grid of bench_floors.B_GRID)
B_GRID = (0.3, 0.45, 0.6, 0.9)
SIZING = [("kddcup2010-algebra0607:halfA", "out/plan2/d-size/state.json", "d:algebra0607:size"),
          ("kddcup2010-bridge06", "out/plan2/f2-size/state.json", "f2:bridge06:size"),
          ("edmcup2023", "out/plan2/g-AKT-gpu4-f0-F1q/state.json", "g:edmcup2023:size")]
GERVET_SRC = {"gervet": "Gervet et al. (2020), Table 4, bridge06 (pooled AUC over five folds)",
              "gervet-amended": "Gervet et al. (2020), Table 13, bridge06 (mean of five fold AUCs; Amendment 1)"}
PYKT_KEYS = ["target", "target_source", "pykt_primary_auc", "pykt_loop_auc", "bench_auc", "bench_auc_ci_lo",
             "bench_auc_ci_hi", "repro_diff", "repro_reading", "loop_diff", "loop_reading", "gate_reading",
             "n_test_learners", "n_test_rows"]

# the EDM Cup prep job's report (one registered prep job; every lane's copy of it is identical)
PREP = ("edmcup2023", "out/plan2/g-AKT-gpu4-f0-F1q/state.json", "g:edmcup:prep")
# the device control's records (Amendment 3): (model, file, key in "governing" or None for a flat record)
DEVICE = [("IEKT", "out/plan2/gpu-device-calibration-2026-11-13.json", "g IEKT"),
          ("AKT", "out/plan2/gpu-device-calibration-2026-11-13.json", "g AKT"),
          ("simpleKT", "out/plan2/gpu-device-calibration-2026-11-13.json", "h simpleKT"),
          ("LPKT", "out/plan2/lpkt-device-band-2026-11-15.json", None)]
# a gate record's target_source cut short where it was written (N4, scope audit 1)
SOURCE_FIX = {"LefoKT Table 3, BD2006 (third-party target); pyKT's LPKT at 4db3fbe6 reads no an":
              "LefoKT Table 3, BD2006 (third-party target); pyKT's LPKT at 4db3fbe6 reads no answer time"}

_ADDED: dict[str, str] = {}


def first_commit(p: Path) -> str:
    """The time of the commit that added a pushed aggregate (the first copy counts)."""
    if not _ADDED:
        r = subprocess.run(["git", "-C", str(REPO), "log", "--diff-filter=A", "--name-only", "--format=@%cI", "--",
                            str((OUT / "plan2").relative_to(REPO)), str((OUT / "optionA").relative_to(REPO))],
                           capture_output=True, text=True, check=True)
        t = None
        for ln in r.stdout.splitlines():
            if ln.startswith("@"):
                t = ln[1:]
            elif ln.strip():
                _ADDED[ln.strip()] = t       # newest first: the last time seen is the first add
    return _ADDED.get(str(p.relative_to(REPO)), "9999")


def eligible(lane: str, model: str, block: str) -> bool:
    if model == "HawkesKT" and block in ("d", "f", "g"):
        return "-a4" in lane
    return True


def job_records() -> list[dict]:
    cands: dict[str, list[tuple[str, str, Path]]] = {}
    for f in sorted(glob.glob(str(OUT / "plan2/*/push/*/*.json")) + glob.glob(str(OUT / "optionA/*/push/*/*.json"))):
        p = Path(f)
        sid, lane = p.parent.name, p.parent.parent.parent.name
        m = SID.match(sid)
        if not m or m["model"] not in SID_MODEL:
            continue                                   # not a reported model's fit or floor: never opened
        model = SID_MODEL[m["model"]]
        if not eligible(lane, model, m["block"]):
            continue
        if not m["rest"].startswith("F1-") and m["block"] not in FIT_BLOCKS:
            continue                                   # the floor lanes' own re-fits ("rr") are not stage fits
        cands.setdefault(sid, []).append((first_commit(p), lane, p))
    out = []
    for sid in sorted(cands):
        copies = sorted(cands[sid])
        recs = [json.loads(p.read_text()) for _, _, p in copies]
        recs_done = [(c, r) for c, r in zip(copies, recs) if r.get("status") == "done"]
        if not recs_done:
            continue
        (t, lane, p), rec = recs_done[0]
        for (_, l2, _), r2 in recs_done[1:]:
            if r2["metrics"] != rec["metrics"]:
                print(f"copies differ: {sid} {lane} vs {l2}", file=sys.stderr)
        m = SID.match(sid)
        model, corpus = SID_MODEL[m["model"]], CORPORA[m["corpus"]]
        rest = m["rest"]
        met = {x["name"]: x for x in rec["metrics"]}
        any_m = rec["metrics"][0]
        assert any_m["model"] == model and any_m["corpus"] == corpus, sid
        if rest.startswith("F1-"):
            o, gn, ge, d = met["f1_oracle_gain"], met["f1_gn"], met["f1_ge"], met["f1_ge_minus_gn"]
            out.append({"record": "floor", "model": model, "corpus": corpus, "block": m["block"],
                        "regime": rest.split("_")[0][3:], "device": any_m.get("device"),
                        "n_test_learners": any_m["n_learners"], "n_test_rows": any_m["n_rows"],
                        "O": o["value"], "O_se": o.get("se"), "G_E": ge["value"], "G_N": gn["value"],
                        "G_N_ci95": gn.get("ci"), "G_E_minus_G_N": d["value"], "G_E_minus_G_N_ci95": d.get("ci"),
                        "reading": d.get("reading"), "lane": lane, "job": sid})
            continue
        parts = rest.split("_")
        regime = parts[0]
        draw = int(parts[1][1:]) if regime in ("tenth", "fiftieth") else None
        fold = int(parts[-1][1:])
        out.append({"record": "fit", "model": model, "corpus": corpus, "block": m["block"], "regime": regime,
                    "draw": draw, "fold": fold, "device": any_m.get("device"),
                    "n_test_learners": any_m["n_learners"], "n_test_rows": any_m["n_rows"],
                    "auc": met["auc"]["value"], "log_loss": met["log_loss"]["value"],
                    "saturated_share": met["saturated_share"]["value"], "lane": lane, "job": sid})
    return out


def gate_records() -> list[dict]:
    out = []
    for model, rel, kind, target in GATES + [(m, r, k, None) for m, r, k in GATES_FIRST]:
        p = STUDY / rel
        d = json.loads(p.read_text())
        r = {"record": "gate", "model": model, "corpus": "kddcup2010-bridge06", "source_file": rel}
        if kind.startswith("gervet"):
            g = d["metrics"][0]
            assert g["model"] == model
            r.update({"kind": kind, "target": target, "target_source": GERVET_SRC[kind], "bench_auc": g["value"],
                      "bench_auc_ci95": g.get("ci"), "diff": g["value"] - target, "n_learners": g["n_learners"],
                      "n_rows": g["n_rows"],
                      "reading": "PASS" if abs(g["value"] - target) <= .010 else "HARNESS_FAIL",
                      "scorer_reading": g.get("reading")})
        else:
            if kind == "pykt-state":
                (job,) = d["jobs"].values()
                g = job["rented"]["gate"]
            elif kind == "pykt-file":
                g = d["gate"]
            else:
                g = d
            assert g["model"] == model
            r.update({"kind": "pykt"}, **{k: g.get(k) for k in PYKT_KEYS})
            r["target_source"] = SOURCE_FIX.get(r["target_source"], r["target_source"])
            r["reading"] = g["gate_reading"]
        r["attempt"] = "first (failed; not counted)" if (model, rel, kind) in GATES_FIRST else "counted"
        out.append(r)
    return out


def sizing_records() -> list[dict]:
    out = []
    for corpus, rel, key in SIZING:
        j = json.loads((STUDY / rel).read_text())["jobs"][key]
        out.append({"record": "sizing", "corpus": corpus, "reading": j["reading"], "b_index": j["b_index"],
                    "b": B_GRID[j["b_index"]], "b_grid": list(B_GRID), "source_file": rel})
    return out


def prep_records() -> list[dict]:
    corpus, rel, key = PREP
    rep = json.loads((STUDY / rel).read_text())["jobs"][key]["rented"]["prep"]["report"]
    return [{"record": "prep", "corpus": corpus, **rep, "source_file": rel}]


def device_records() -> list[dict]:
    out = []
    for model, rel, key in DEVICE:
        d = json.loads((STUDY / rel).read_text())
        if key:
            g = d["governing"][key]
            cells = [{"cell": c["cell"], "gpu_minus_cpu": c["signed_gpu_minus_cpu"]}
                     for c in g["calibration"]["cells"] if c["signed_gpu_minus_cpu"] is not None]
            gpu, band, how = g["gpu"], g["calibration"]["band"], "committed CPU fits re-run once on the GPU"
        else:
            cells = [{"cell": c["cell"], "gpu_minus_cpu": -c["signed_cpu_minus_gpu"]} for c in d["cells"]]
            gpu, band, how = d["cells"][0]["gpu_type"], d["band"], "counted GPU fits re-run once on a CPU"
        assert band == max(abs(c["gpu_minus_cpu"]) for c in cells), model
        out.append({"record": "device_band", "model": model, "gpu": gpu, "how": how, "n_cells": len(cells),
                    "cells": cells, "band": band, "source_file": rel})
    return out


def lines() -> list[str]:
    return [json.dumps(x, sort_keys=True) for x in sizing_records() + gate_records() + prep_records()
            + device_records() + job_records()]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["build", "verify"])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    text = "\n".join(lines()) + "\n"
    out = Path(a.out)
    if a.mode == "build":
        out.write_text(text)
        print(f"wrote {out} ({text.count(chr(10))} records)")
    else:
        same = out.exists() and out.read_text() == text
        print("verify:", "IDENTICAL" if same else "DIFFERENT")
        sys.exit(0 if same else 1)


if __name__ == "__main__":
    main()
