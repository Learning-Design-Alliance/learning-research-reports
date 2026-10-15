"""PRE-REGISTERED: when topics with no logical dependency are taught in a random order, does order matter?

The core-versus-culture reading of the programme's results says order among topics that do not
depend on each other is a curricular choice: any order should serve learners about equally. ASSISTments
experiment PSABANRN (osf.io/59shv, E-TRIALS) randomised students to four orders of mean, median, range
and mode within one skill builder. None of the four needs another (mode needs counting, median
ordering, range the extremes, mean adding and dividing), so the reading predicts no order effect.
Transfer between measures of centre could still make some orders easier; that would count against
interchangeability here. Written 2026-09-27; no statistic of PSABANRN has been computed by this
programme (studies/outcomes/ope/ read other experiments from the same release, not this one).

Reads $SCRATCH/osf-59shv/exp.zip (PSABANRN.zip: exp_alogs.csv, one row per student assignment, and
priors.csv), resolved through shared.paths.scratch_root(). Raw files stay outside the repo; only
per-arm aggregates are written.

DIRECTION: symmetric -- no edge is asserted; arms are compared without an assumed order.

PRE-REGISTRATION
  Units: students with assigned_condition in Treatment 1-4 ("Not Assigned" dropped); if a student
  has several rows, the first by start_time. The release does not say which treatment is which
  order; the test does not need it.
  Outcomes
    completion (primary): end_time present (the skill builder was finished, i.e. mastery reached).
    problems to mastery: condition_problem_count, among completers.
    correct rate: condition_total_correct / condition_problem_count, among students with >= 1 problem.
  Tests, for each outcome
    omnibus: between-arm variance of arm means, permutation p over 10,000 relabellings of arm.
    pairwise: all six arm differences with 90% bootstrap intervals (5,000 student resamples).
  Equivalence margins: completion +-0.08, problems to mastery +-1.0 problem, correct rate +-0.05.
  VERDICT
    ORDER MATTERS if the omnibus p < 0.05 for completion or problems to mastery.
    ORDER INTERCHANGEABLE if not, and every pairwise 90% interval lies inside its margin for
    completion and problems to mastery (two one-sided tests at 0.05).
    INCONCLUSIVE otherwise.
  Reported: arm sizes and means; prior average correctness by arm (a randomisation check); the same
  tests within the lower and upper halves of prior correctness (exploratory).

    python3 order_swap.py
"""

from __future__ import annotations

import csv
import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from shared.paths import scratch_root  # noqa: E402

OUT = HERE / "out"
SEED = 20260927
ARMS = ["Treatment 1", "Treatment 2", "Treatment 3", "Treatment 4"]
MARGIN = {"completion": 0.08, "problems_to_mastery": 1.0, "correct_rate": 0.05}


def load():
    z = zipfile.ZipFile(scratch_root() / "osf-59shv/exp.zip")
    inner = zipfile.ZipFile(io.BytesIO(z.read("PSABANRN.zip")))
    rows = list(csv.DictReader(io.TextIOWrapper(inner.open("exp_alogs.csv"), encoding="utf-8")))
    priors = {r["student_id"]: r for r in csv.DictReader(io.TextIOWrapper(inner.open("priors.csv"), encoding="utf-8"))}
    first = {}
    for r in sorted(rows, key=lambda r: (r["student_id"], r["start_time"] or "~")):
        if r["assigned_condition"] in ARMS and r["student_id"] not in first:
            first[r["student_id"]] = r
    return list(first.values()), priors


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def outcomes(rows):
    out = {"completion": [], "problems_to_mastery": [], "correct_rate": []}
    for r in rows:
        arm = ARMS.index(r["assigned_condition"])
        done = bool((r["end_time"] or "").strip())
        out["completion"].append((arm, 1.0 if done else 0.0))
        n, c = fnum(r["condition_problem_count"]), fnum(r["condition_total_correct"])
        if done and n is not None:
            out["problems_to_mastery"].append((arm, n))
        if n and c is not None:
            out["correct_rate"].append((arm, c / n))
    return {k: (np.array([a for a, _ in v]), np.array([x for _, x in v])) for k, v in out.items()}


def test(arm, x, rng):
    means = np.array([x[arm == a].mean() if (arm == a).any() else np.nan for a in range(4)])
    stat = np.nanvar(means)
    perm = np.empty(10000)
    for i in range(10000):
        pa = rng.permutation(arm)
        pm = np.array([x[pa == a].mean() for a in range(4)])
        perm[i] = np.var(pm)
    p = float((1 + (perm >= stat).sum()) / (1 + len(perm)))
    idx = [np.nonzero(arm == a)[0] for a in range(4)]
    pairs = {}
    for a in range(4):
        for b in range(a + 1, 4):
            d = []
            for _ in range(5000):
                ma = x[rng.choice(idx[a], len(idx[a]))].mean()
                mb = x[rng.choice(idx[b], len(idx[b]))].mean()
                d.append(ma - mb)
            pairs[f"T{a + 1}-T{b + 1}"] = {"diff": float(means[a] - means[b]),
                                           "lo90": float(np.percentile(d, 5)), "hi90": float(np.percentile(d, 95))}
    return {"n": [int((arm == a).sum()) for a in range(4)], "means": means.tolist(), "omnibus_p": p, "pairs": pairs}


def verdict(res):
    matters = res["completion"]["omnibus_p"] < 0.05 or res["problems_to_mastery"]["omnibus_p"] < 0.05
    inside = all(abs(v["lo90"]) <= MARGIN[k] and abs(v["hi90"]) <= MARGIN[k]
                 for k in ("completion", "problems_to_mastery") for v in res[k]["pairs"].values())
    return "ORDER MATTERS" if matters else "ORDER INTERCHANGEABLE" if inside else "INCONCLUSIVE"


def main() -> None:
    rng = np.random.default_rng(SEED)
    rows, priors = load()
    res = {"students": len(rows)}
    oc = outcomes(rows)
    for k, (arm, x) in oc.items():
        res[k] = test(arm, x, rng)
    res["verdict"] = verdict(res)
    pc = [(ARMS.index(r["assigned_condition"]), fnum(priors.get(r["student_id"], {}).get("student_prior_average_correctness")))
          for r in rows]
    res["prior_correctness_by_arm"] = [float(np.nanmean([v for a, v in pc if a == i and v is not None] or [np.nan]))
                                       for i in range(4)]
    vals = [v for _, v in pc if v is not None]
    med = float(np.median(vals)) if vals else None
    res["by_prior_half"] = {}
    if med is not None:
        for half, keep in (("lower", lambda v: v is not None and v < med), ("upper", lambda v: v is not None and v >= med)):
            sub = [r for r, (_, v) in zip(rows, pc) if keep(v)]
            o = outcomes(sub)
            res["by_prior_half"][half] = {k: test(a, x, rng) for k, (a, x) in o.items()}
    OUT.mkdir(exist_ok=True)
    (OUT / "order-swap-result.json").write_text(json.dumps(res, indent=1) + "\n")
    print("students", res["students"])
    for k in MARGIN:
        r = res[k]
        print(f"{k}: n {r['n']} means {[round(m, 3) for m in r['means']]} omnibus p {r['omnibus_p']:.3f}")
        for pk, v in r["pairs"].items():
            print(f"   {pk} {v['diff']:+.3f} [{v['lo90']:+.3f}, {v['hi90']:+.3f}]")
    print("prior correctness by arm", [round(v, 3) for v in res["prior_correctness_by_arm"]])
    print("VERDICT:", res["verdict"])


if __name__ == "__main__":
    main()
