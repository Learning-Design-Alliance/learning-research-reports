"""
A prerequisite whose direction we KNOW, inside real learner data.

Everything in this programme has tested prerequisite structure between KCs, where nobody is certain
the dependency exists and nobody can check the arrow. Inside a single fraction-addition problem
there is a dependency that is not in doubt:

    5/3 + 2/5   ->   den3, den4   the common denominator      (KC commonDenominator)
                     num3, num4   the converted numerators    (KC equivalentFractions)
                     num5, den5   the answer

You cannot compute a converted numerator without the common denominator. The arrow is procedural,
authored into the interface, and the same for every learner. It is exactly the hard conjunctive gate
`studies/identifiability/latent-shape/recover.py` plants synthetically -- except this one is real, and there are thousands of
observations of it.

So this asks three questions the synthetic work could only ask of made-up data:

  GATE      does failing the prerequisite step actually crush the dependent step? If the gate is not
            visible even here, the programme has been hunting something that does not exist in the
            data at all
  DIRECTION can the arrow be recovered? `latent-shape` found direction unrecoverable between KCs at
            realistic noise. Here the truth is known, so a failure is decisive and a success bounds
            the earlier claim to KC-level structure
  RESCUE    the tutor hints until the learner gets the prerequisite right, so by the time they reach
            the dependent step it has been REPAIRED. Does that repair carry? This is the mechanism
            behind "how could practising something you lack the prerequisite for possibly help" --
            if scaffolding supplies the prerequisite in place, it can

Observations are (learner, problem instance) pairs and learners contribute many, so every interval
is bootstrapped over LEARNERS.

    python3 steps_ds1190.py <all_data_export.txt> [--out result.json]
"""

from __future__ import annotations

import collections
import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from shared.stats import bootstrap  # noqa: E402

#: the authored order inside an addition-with-different-denominators problem. Left depends on right.
DEPENDS = [("num3", "den3"), ("num4", "den4"), ("num5", "num3"), ("num5", "num4"),
           ("den5", "den3")]
#: pairs with no authored dependency either way, as the discriminant control -- the two branches of
#: the conversion are computed independently of each other
INDEPENDENT = [("den3", "den4"), ("num3", "num4")]
CORRECT = {"CORRECT", "OK"}
SEED = 20260919
REPS = 2000


def field(step: str) -> str:
    return step.split()[0] if step else ""


def load(path: Path):
    """learner -> list of problem attempts, each a dict of field -> (first-attempt ok, hints)."""
    by = collections.defaultdict(dict)
    with path.open(newline="", encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            h = r["Problem Hierarchy"]
            if any(f"ProblemSet {p}" in h for p in ("Pretest", "Posttest", "Midtest", "DPosttest")):
                continue
            if not r["Problem Name"].startswith("AD"):
                continue
            key = (r["Anon Student Id"], r["Problem Name"], r["Problem View"])
            f = field(r["Step Name"])
            if f:
                by[key][f] = ((r.get("First Attempt") or "").strip().upper() in CORRECT,
                              int(r.get("Hints") or 0))
    out = collections.defaultdict(list)
    for (learner, _, _), fields in by.items():
        out[learner].append(fields)
    return out


def conditional(attempts, dependant: str, prereq: str):
    """P(dependant right | prereq right) and P(dependant right | prereq wrong), plus the counts."""
    got = [0, 0]
    tot = [0, 0]
    for a in attempts:
        if dependant not in a or prereq not in a:
            continue
        side = 1 if a[prereq][0] else 0
        tot[side] += 1
        got[side] += a[dependant][0]
    return got, tot


def rate_gap(learners, data, dependant, prereq):
    got = [0, 0]
    tot = [0, 0]
    for s in learners:
        g, t = conditional(data[s], dependant, prereq)
        got[0] += g[0]; got[1] += g[1]; tot[0] += t[0]; tot[1] += t[1]
    if min(tot) < 20:
        return float("nan")
    return got[1] / tot[1] - got[0] / tot[0]


def main() -> None:
    path = Path(sys.argv[1])
    data = load(path)
    learners = sorted(data)
    n_att = sum(len(v) for v in data.values())
    print(f"{len(learners)} learners, {n_att:,} attempts at addition-with-different-denominators "
          f"problems\n")

    rng = np.random.default_rng(SEED)
    out = {"n_learners": len(learners), "n_attempts": n_att, "pairs": []}

    print("GATE -- how much does the dependent step suffer when its prerequisite is failed?")
    print(f"{'':<16}{'P(dep | pre ok)':>17}{'P(dep | pre wrong)':>20}{'gap':>9}"
          f"{'95% interval':>20}")
    for dep, pre in DEPENDS + INDEPENDENT:
        got = [0, 0]; tot = [0, 0]
        for s in learners:
            g, t = conditional(data[s], dep, pre)
            got[0] += g[0]; got[1] += g[1]; tot[0] += t[0]; tot[1] += t[1]
        if min(tot) < 20:
            print(f"{dep} <- {pre:<8}  too few")
            continue

        def stat(idx, dep=dep, pre=pre):
            return rate_gap([learners[i] for i in idx], data, dep, pre)

        g, lo, hi = bootstrap(stat, len(learners), rng, reps=REPS)
        tag = "" if (dep, pre) in DEPENDS else "   (no authored dependency)"
        print(f"{dep} <- {pre:<8}{got[1] / tot[1]:>17.3f}{got[0] / tot[0]:>20.3f}"
              f"{g:>+9.3f}   [{lo:+.3f}, {hi:+.3f}]{tag}")
        out["pairs"].append(dict(dependant=dep, prereq=pre, authored=(dep, pre) in DEPENDS,
                                 p_given_ok=got[1] / tot[1], p_given_wrong=got[0] / tot[0],
                                 gap=g, lo=lo, hi=hi, n_ok=tot[1], n_wrong=tot[0]))

    print("\nDIRECTION -- the same pairs measured backwards. The arrow is known, so a symmetric")
    print("             reading means the direction is not in the data, however real it is.")
    print(f"{'':<16}{'forward':>10}{'backward':>11}{'forward - backward':>22}{'95% interval':>20}")
    out["direction"] = []
    for dep, pre in DEPENDS:
        def diff(idx, dep=dep, pre=pre):
            sel = [learners[i] for i in idx]
            f, b = rate_gap(sel, data, dep, pre), rate_gap(sel, data, pre, dep)
            return f - b

        fwd = rate_gap(learners, data, dep, pre)
        bwd = rate_gap(learners, data, pre, dep)
        d, lo, hi = bootstrap(diff, len(learners), rng, reps=REPS)
        verdict = "asymmetric" if (hi < 0 or lo > 0) else "SYMMETRIC -- no arrow in the data"
        print(f"{dep} <- {pre:<8}{fwd:>+10.3f}{bwd:>+11.3f}{d:>+22.3f}   [{lo:+.3f}, {hi:+.3f}]"
              f"  {verdict}")
        out["direction"].append(dict(dependant=dep, prereq=pre, forward=fwd, backward=bwd,
                                     diff=d, lo=lo, hi=hi))

    print("\nRESCUE -- the tutor hints until the prerequisite is right, so it is REPAIRED before the")
    print("          dependent step is reached. Split the failures by whether help was taken.")
    print(f"{'':<16}{'pre ok':>9}{'pre wrong, hinted':>19}{'pre wrong, no hint':>20}")
    out["rescue"] = []
    for dep, pre in DEPENDS:
        cells = {"ok": [0, 0], "hinted": [0, 0], "unhinted": [0, 0]}
        for s in learners:
            for a in data[s]:
                if dep not in a or pre not in a:
                    continue
                ok, hints = a[pre]
                k = "ok" if ok else ("hinted" if hints > 0 else "unhinted")
                cells[k][0] += a[dep][0]
                cells[k][1] += 1
        row = {k: (v[0] / v[1] if v[1] >= 20 else None) for k, v in cells.items()}
        fmt = {k: (f"{v:.3f}" if v is not None else "  --  ") for k, v in row.items()}
        print(f"{dep} <- {pre:<8}{fmt['ok']:>9}{fmt['hinted']:>19}{fmt['unhinted']:>20}")
        out["rescue"].append(dict(dependant=dep, prereq=pre, counts={k: v[1] for k, v in
                                                                     cells.items()}, **row))

    if "--out" in sys.argv:
        q = Path(sys.argv[sys.argv.index("--out") + 1])
        q.write_text(json.dumps(out, indent=1, allow_nan=False, default=lambda x: None))
        print(f"\n-> {q}")


if __name__ == "__main__":
    main()
