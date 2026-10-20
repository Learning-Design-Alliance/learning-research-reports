"""ds1190 Study 2: the order manipulation this programme has been missing, with a delayed posttest.

`data/DATASETS.md` calls it Hole A -- edge existence needs order varied BETWEEN capabilities, and no
public dataset clearly supplies it. ds1190 Study 2 does. Two arms, both BLOCKED, differing only in
which capability comes first:

    AM   Pretest -> fraction ADDITION -> Midtest A -> fraction MULTIPLICATION -> Midtest B -> Posttest
    MA   Pretest -> fraction MULTIPLICATION -> Midtest A -> fraction ADDITION -> Midtest B -> Posttest

Same content, same blocking, opposite order. **30 learners per arm, zero overlap between them.** And
unlike ds1706 -- the same PI's Study 1, 79 learners over two days with no delayed measure -- this
carries a **DPosttest four to five days after** the session (2015-11-03/05 teaching, 2015-11-08/09
delayed test). That is the RETENTION readout `C1` requires and the reason `studies/outcomes/interleaving/README.md`
could not price `C2` from Study 1.

WHY 30 PER ARM IS ENOUGH TO BE WORTH RUNNING. `C2` is priced on an assumed sequencing effect of
d = 0.07-0.17 while Rohrer et al. (2020) report **d = 0.83** for blocked-versus-interleaved on an
unannounced test a month out. At 30 per arm the minimum detectable effect is
2.802 * sqrt(2/30) = **0.72**, so this study is blind to the low regime and roughly 88% powered for
the high one. It cannot confirm d = 0.07-0.17 and it CAN rule out d = 0.83 -- which is exactly the
question `C2`'s price turns on, and the opposite of the usual underpowered null.

THE SHARPEST TEST HERE IS WITHIN-LEARNER, NOT BETWEEN-ARM. The DPosttest contains both capabilities,
so each learner supplies a contrast between the one they practised LAST and the one they practised
FIRST. That removes learner variance, and the two accounts make different predictions:

    RECENCY          whatever you practised last is retained better, in BOTH arms. The within-learner
                     last-minus-first contrast is positive and the arms agree. Order matters, but
                     only as forgetting.
    ORDER MATTERS    one sequence beats the other overall. The BETWEEN-arm contrast on total
                     DPosttest accuracy is non-zero. This is the prerequisite claim.

They are separable, and conflating them is how a recency effect gets sold as a prerequisite.

A CONFOUND THAT ATE THREE QUARTERS OF ds1706'S HEADLINE, CHECKED HERE FIRST. The problem types are
not equally hard -- in Study 1, multiplication ran at 0.937 first-attempt accuracy against 0.827 for
addition with different denominators -- so any contrast that compares arms on DIFFERENT problem mixes
manufactures an effect. The DPosttest composition of each arm is reported before any outcome is, and
every contrast below is type-matched.

PRE-REGISTERED, before the run:

  HIGH REGIME SUPPORTED     between-arm |d| on the DPosttest >= 0.72 with a bootstrap interval
                            excluding zero. Order matters at a size that would reprice C2 to a
                            ~50-learner trial.
  HIGH REGIME RULED OUT     |d| < 0.72 AND the bootstrap upper bound excludes 0.83. At 88% power a
                            tight null is real evidence: a Rohrer-sized ORDER effect is not there,
                            and C2 must be priced for the low regime.
  UNINFORMATIVE             neither -- the interval is too wide to exclude 0.83 and too small to
                            support it.

  and separately, because it is a different claim:
  RECENCY PRESENT           the within-learner last-minus-first contrast excludes zero.

Reads ds1190 from DataShop. Research use, no redistribution: the raw export stays in the session
scratchpad and only aggregates are committed.

    python3 ds1190_order.py [--reps 10000]
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
sys.path.insert(0, str(HERE.parents[2] / "studies/identifiability/latent-shape"))

from build_matrix import SCRATCH  # noqa: E402

SEED = 20260922
MDE_D = 2.802 * np.sqrt(2 / 30)
#: the published blocked-vs-interleaved effect this study is powered to rule out
ROHRER_D = 0.83


#: test items carry a richer vocabulary than practice ones and this cost the first run its data.
#: PRACTICE problems are `AD 1_2_plus_2_3` / `M 1_3_times_4_9` -- addition and multiplication only.
#: TEST problems are `T AS 4_3_plus_1_3`, `T MD 11_7_times_2_3`, `T SS 3_7_minus_1_7`,
#: `T DD 3_5_div_2_11` -- four operations crossed with same/different denominators, sixteen items.
#: SUBTRACTION AND DIVISION WERE NEVER PRACTISED, so they are transfer items and are scored
#: separately; reading them as trained performance would mix a transfer question into an order one.
TRAINED = {"ADD", "MUL"}
_OPS = {"A": "ADD", "M": "MUL", "S": "SUB", "D": "DIV"}


def ptype(name: str) -> str:
    """The capability an item exercises. Handles both the practice and the test naming."""
    toks = name.strip().upper().split()
    if not toks:
        return "?"
    code = toks[1] if toks[0] == "T" and len(toks) > 1 else toks[0]
    if code == "M":
        return "MUL"
    if code in {"AD", "AS"}:
        return "ADD"
    return _OPS.get(code[0], "?") if len(code) == 2 and code[1] in "SD" else "?"


def pset(h: str) -> str:
    m = re.search(r"ProblemSet (.+?)\s*$", h or "")
    return m.group(1) if m else ""


def cohen_d(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    sp = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1))
                 / (len(a) + len(b) - 2))
    return float((a.mean() - b.mean()) / sp) if sp > 0 else float("nan")


def boot(fn, a, b, rng, reps):
    if len(a) < 2 or len(b) < 2:
        return float("nan"), float("nan")
    out = [fn(rng.choice(a, len(a), replace=True), rng.choice(b, len(b), replace=True))
           for _ in range(reps)]
    out = np.array([x for x in out if np.isfinite(x)])
    if not len(out):
        return float("nan"), float("nan")
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


def boot_mean(v, rng, reps):
    m = np.array([rng.choice(v, len(v), replace=True).mean() for _ in range(reps)])
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def load(path):
    per = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    with open(path, encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            t = ptype(r["Problem Name"])
            if t == "?":
                continue
            per[r["Anon Student Id"]][pset(r["Problem Hierarchy"])][t].append(
                1.0 if r["First Attempt"] == "correct" else 0.0)
    return per


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(SCRATCH / "ds1190"))
    ap.add_argument("--reps", type=int, default=10000)
    ap.add_argument("--out", default="out/ds1190_order.json")
    args = ap.parse_args()
    rng = np.random.default_rng(SEED)
    src = Path(args.src)

    arms = {}
    for tag, pat in (("AM", "S2_AM_Blocked"), ("MA", "S2_MA_Blocked")):
        f = next(p for p in src.iterdir() if pat in p.name)
        arms[tag] = load(f)
    print(f"ds1190 Study 2 -- AM {len(arms['AM'])} learners, MA {len(arms['MA'])} learners, "
          f"overlap {len(set(arms['AM']) & set(arms['MA']))}\n")

    # --- composition check, before any outcome
    print("DPOSTTEST COMPOSITION (the confound that ate three quarters of ds1706's headline)")
    comp = {}
    for tag in ("AM", "MA"):
        c = defaultdict(int)
        for st in arms[tag].values():
            for t, v in st.get("DPosttest", {}).items():
                c[t] += len(v)
        tot = sum(c.values()) or 1
        comp[tag] = {t: c[t] / tot for t in ("ADD", "MUL", "SUB", "DIV")}
        print(f"   {tag}   trained: ADD {100*comp[tag]['ADD']:.1f}%  MUL {100*comp[tag]['MUL']:.1f}%"
              f"   |  transfer: SUB {100*comp[tag]['SUB']:.1f}%  DIV {100*comp[tag]['DIV']:.1f}%"
              f"   ({tot:,} steps)")
    gap = abs(comp["AM"]["ADD"] - comp["MA"]["ADD"])
    print(f"   -> composition differs by {100*gap:.1f} points; "
          + ("contrasts below are type-matched regardless" if gap < 0.10 else
             "TOO FAR APART to compare raw, and the type-matched contrasts are the only readable ones"))

    res = dict(n_am=len(arms["AM"]), n_ma=len(arms["MA"]), mde_d=float(MDE_D),
               rohrer_d=ROHRER_D, composition=comp, composition_gap=float(gap))

    # --- 1. between-arm, type-matched: does one ORDER win on the delayed test?
    print(f"\n1. BETWEEN-ARM on the DPosttest, type-matched (MDE {MDE_D:.2f})")
    for t in ("ADD", "MUL", "SUB", "DIV"):
        a = np.array([np.mean(st["DPosttest"][t]) for st in arms["AM"].values()
                      if len(st.get("DPosttest", {}).get(t, [])) >= 3])
        b = np.array([np.mean(st["DPosttest"][t]) for st in arms["MA"].values()
                      if len(st.get("DPosttest", {}).get(t, [])) >= 3])
        d = cohen_d(a, b)
        lo, hi = boot(cohen_d, a, b, rng, args.reps)
        mark = "trained " if t in TRAINED else "TRANSFER"
        print(f"   {t} ({mark}):  AM {a.mean():.3f} (n={len(a)})   MA {b.mean():.3f} "
              f"(n={len(b)})   d = {d:+.2f}  [{lo:+.2f}, {hi:+.2f}]")
        res[f"between_{t}"] = dict(am=float(a.mean()), ma=float(b.mean()), n_am=len(a),
                                   n_ma=len(b), d=d, lo=lo, hi=hi)
    # pooled: each learner's whole DPosttest, which is type-matched only if composition allows
    pooled = {}
    for tag in ("AM", "MA"):
        v = []
        for st in arms[tag].values():
            dp = st.get("DPosttest", {})
            both = [np.mean(dp[t]) for t in ("ADD", "MUL") if len(dp.get(t, [])) >= 3]
            if len(both) == 2:
                v.append(float(np.mean(both)))
        pooled[tag] = np.array(v)
    d = cohen_d(pooled["AM"], pooled["MA"])
    lo, hi = boot(cohen_d, pooled["AM"], pooled["MA"], rng, args.reps)
    print(f"   BOTH (each learner's two type means averaged):  AM {pooled['AM'].mean():.3f} "
          f"(n={len(pooled['AM'])})   MA {pooled['MA'].mean():.3f} (n={len(pooled['MA'])})")
    print(f"        d = {d:+.2f}  95% bootstrap [{lo:+.2f}, {hi:+.2f}]")
    res["between_pooled"] = dict(am=float(pooled["AM"].mean()), ma=float(pooled["MA"].mean()),
                                 n_am=len(pooled["AM"]), n_ma=len(pooled["MA"]),
                                 d=d, lo=lo, hi=hi)

    # --- 2. within-learner recency: last-practised minus first-practised
    print(f"\n2. WITHIN-LEARNER RECENCY -- capability practised LAST minus the one practised FIRST")
    last = {"AM": "MUL", "MA": "ADD"}
    diffs = {}
    for tag in ("AM", "MA"):
        v = []
        for st in arms[tag].values():
            dp = st.get("DPosttest", {})
            L, F = last[tag], ("ADD" if last[tag] == "MUL" else "MUL")
            if len(dp.get(L, [])) >= 3 and len(dp.get(F, [])) >= 3:
                v.append(float(np.mean(dp[L]) - np.mean(dp[F])))
        diffs[tag] = np.array(v)
        lo, hi = boot_mean(diffs[tag], rng, args.reps)
        print(f"   {tag}  last={last[tag]:<4} mean {diffs[tag].mean():+.3f}  "
              f"[{lo:+.3f}, {hi:+.3f}]  (n={len(v)})")
        res[f"recency_{tag}"] = dict(last=last[tag], mean=float(diffs[tag].mean()),
                                     lo=lo, hi=hi, n=len(v))
    allv = np.concatenate([diffs["AM"], diffs["MA"]])
    rlo, rhi = boot_mean(allv, rng, args.reps)
    print(f"   BOTH ARMS POOLED  mean {allv.mean():+.3f}  [{rlo:+.3f}, {rhi:+.3f}]")
    res["recency_pooled"] = dict(mean=float(allv.mean()), lo=rlo, hi=rhi, n=len(allv))

    # --- verdicts
    bd, blo, bhi = res["between_pooled"]["d"], res["between_pooled"]["lo"], res["between_pooled"]["hi"]
    order_v = ("HIGH REGIME SUPPORTED" if abs(bd) >= MDE_D and (blo > 0 or bhi < 0) else
               "HIGH REGIME RULED OUT" if abs(bd) < MDE_D and bhi < ROHRER_D and blo > -ROHRER_D
               else "UNINFORMATIVE")
    rec_v = "RECENCY PRESENT" if (rlo > 0 or rhi < 0) else "NO RECENCY DETECTED"
    res["verdict_order"], res["verdict_recency"] = order_v, rec_v
    print(f"\nVERDICT (order): {order_v}")
    if order_v == "HIGH REGIME RULED OUT":
        print(f"   d = {bd:+.2f} with a 95% interval of [{blo:+.2f}, {bhi:+.2f}], which excludes "
              f"{ROHRER_D:+.2f} at roughly 88% power. A Rohrer-sized ORDER effect is not here. C2 "
              f"cannot be repriced downward on the strength of the interleaving literature, and its "
              f"1,087-6,410 stands until something else moves it.")
    elif order_v == "HIGH REGIME SUPPORTED":
        print(f"   d = {bd:+.2f} clears the MDE with an interval excluding zero, on a DELAYED test "
              f"with clean randomisation. C2 should be repriced and a ~50-learner trial designed.")
    else:
        print(f"   the interval [{blo:+.2f}, {bhi:+.2f}] neither excludes {ROHRER_D} nor clears "
              f"{MDE_D:.2f}. 30 per arm was not enough after all.")
    print(f"VERDICT (recency): {rec_v}")
    if rec_v == "RECENCY PRESENT":
        print(f"   the capability practised LAST is retained better by "
              f"{allv.mean():+.3f} across both arms. That is forgetting, not a prerequisite, and "
              f"anything that reads it as edge evidence is reading the calendar.")

    o = Path(args.out)
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(res, indent=2) + "\n")
    print(f"\nwrote {o}")


if __name__ == "__main__":
    main()
