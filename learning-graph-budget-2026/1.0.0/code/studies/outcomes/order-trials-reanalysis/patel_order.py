"""PRE-REGISTERED: Patel, Liu & Koedinger (2016, CogSci), the only held prerequisite-order swap.

Study 2 of "When to Block versus Interleave Practice? Evidence Against Teaching Fraction Addition
before Fraction Multiplication" randomised sixth graders to blocked fraction ADDITION then
MULTIPLICATION (AM, 29) or the reverse (MA, 30), plus an interleaved arm (59). The paper prints
(as transcribed in studies/outcomes/order-trials/PUBLISHED-FINDINGS.md from the full text, 2026-09-24;
the full text could not be re-opened from this session, its hosts are blocked by the egress proxy):

    MA 78% vs AM 70%, "B = 0.07 (0.04), t = 3.57, p = 0.04"        delay stated as 3 days
    interleaved 79% vs AM 70%, "B = 0.10 (0.03), p < .01"

Data: DataShop ds1190, Study 2 sample files S2_AM_Blocked and S2_MA_Blocked (student-step export).
ds1706 is the same PI's Study 1 (interleaved vs blocked add-then-mult over two days); it has no MA arm
and no delayed test, so it carries no order swap and is not re-analysed here
(studies/outcomes/interleaving/ds1706.py already reads it). DataShop terms: research use, no
redistribution; the raw export stays in scratch and only aggregates are committed. Reads
scratch_root()/ds1190 as studies/measurement/transfer/transfer.py and
studies/outcomes/interleaving/ds1190_order.py do.

THREE PARTS, the first two need no learner data:

  1. PRINTED-STATISTICS CHECK. With 29 + 30 learners (df 57 for a two-group linear contrast), the
     three printed numbers B/SE, t and p each imply the other two. Report every implied value. Verdict
     PRINTED STATISTICS CONSISTENT if all three agree to rounding (|t_implied - t_printed| <= 0.15 and
     p within a factor 1.5), otherwise PRINTED STATISTICS INCONSISTENT, naming which pairs disagree.
  2. DETECTION FLOOR (synthetic, run before any real number). 29 + 30 learners x 16 test items
     (ds1190's test form: 4 operations x same/different denominators, 2 each), learner ability
     N(0, sd_a) and item difficulty N(0, 0.8) on the logit scale, sd_a set so the per-learner
     proportion-correct SD is ~0.15 (the SD the printed B and SE imply: 0.04 / sqrt(1/29 + 1/30)).
     Plant MA - AM = 0, 4, 8, 12, 16 points; 1,000 worlds each; re-randomisation test of the
     difference in arm means with 2,000 relabellings that keep arm sizes (the learner is the unit
     assigned). Power = share with p < 0.05 AND the planted sign. The analytic MDE at 80% power and
     two-sided 0.05 is 2.802 * sqrt(1/29 + 1/30) = 0.73 SD.
  3. RE-ANALYSIS (needs ds1190 on disk). For every test-form problem set (items named "T ..."), in
     time order, each learner's proportion correct under three scorings (step first-attempt; problem
     correct = every step correct on first attempt; final step correct), on all items and on trained
     items (addition, multiplication) only. Per test: arm means, MA - AM, Cohen's d, re-randomisation
     p over 10,000 relabellings of learners (within class when a class column holds both arms in at
     least two classes, else across the study), and the delay from the learner's last practice step to
     the test. The DELAY CONTRAST is the within-learner change from the immediate posttest to the
     delayed posttest, compared between arms with the same test.
     REPRODUCTION: REPRODUCES if some scoring of some posttest gives AM within 0.02 of 0.70 and MA
     within 0.02 of 0.78 (the scoring is named; this is a search over 2 x 3 x test-count cells and is
     reported as one); otherwise DOES NOT REPRODUCE.
     ORDER VERDICT, per test: MULTIPLICATION FIRST BETTER if MA - AM > 0 and p < 0.05; ADDITION
     FIRST BETTER if < 0 and p < 0.05; else NOT DISTINGUISHED, or UNINFORMATIVE (BELOW FLOOR) if the
     floor's power at 8 points (the printed effect) is below 0.80.
     Without ds1190 on disk part 3 prints BLOCKED and writes that into the result.

DIRECTION: symmetric -- arms are compared as MA minus AM; no edge orientation is inferred.

    python3 patel_order.py            # parts 1-2 always; part 3 when scratch_root()/ds1190 exists
"""

from __future__ import annotations

import csv
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats as sps

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from shared.paths import scratch_root  # noqa: E402

OUT = HERE / "out"
SEED = 20261005
N_AM, N_MA = 29, 30
PRINTED = dict(am=0.70, ma=0.78, B=0.07, SE=0.04, t=3.57, p=0.04, delay_days=3)
PLANT = [0.0, 0.04, 0.08, 0.12, 0.16]


# ------------------------------------------------------------------ 1. printed statistics
def printed_check():
    df = N_AM + N_MA - 2
    B, SE, t, p = PRINTED["B"], PRINTED["SE"], PRINTED["t"], PRINTED["p"]
    t_from_bse = B / SE
    p_from_bse = 2 * sps.t.sf(t_from_bse, df)
    p_from_t = 2 * sps.t.sf(t, df)
    t_from_p = sps.t.isf(p / 2, df)
    se_from_t = B / t
    se_from_p = B / t_from_p
    diff_means = PRINTED["ma"] - PRINTED["am"]
    pairs = {
        "B/SE vs t": abs(t_from_bse - t) <= 0.15,
        "t vs p": 0.667 <= p_from_t / p <= 1.5,
        "B/SE vs p": 0.667 <= p_from_bse / p <= 1.5,
    }
    bad = [k for k, ok in pairs.items() if not ok]
    sd_implied = SE / math.sqrt(1 / N_AM + 1 / N_MA)
    return dict(df=df, t_from_B_SE=t_from_bse, p_from_B_SE=p_from_bse, p_from_t=p_from_t,
                t_from_p=t_from_p, SE_from_t=se_from_t, SE_from_p=se_from_p,
                difference_of_printed_means=diff_means, pair_agrees=pairs,
                implied_learner_sd={"from_SE_0.04": sd_implied,
                                    "from_t_3.57": se_from_t / math.sqrt(1 / N_AM + 1 / N_MA),
                                    "from_p_0.04": se_from_p / math.sqrt(1 / N_AM + 1 / N_MA)},
                verdict="PRINTED STATISTICS CONSISTENT" if not bad else
                "PRINTED STATISTICS INCONSISTENT (" + "; ".join(bad) + ")")


# ------------------------------------------------------------------ re-randomisation test
def rerand_p(a, b, rng, reps, strata=None):
    """Two-sided p of mean(b) - mean(a) under relabelling of learners (within strata if given)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    y = np.concatenate([a, b])
    lab = np.r_[np.zeros(len(a)), np.ones(len(b))]
    obs = b.mean() - a.mean()
    if strata is None:
        strata = np.zeros(len(y), int)
    strata = np.asarray(strata)
    L = np.tile(lab, (reps, 1))
    for s in np.unique(strata):
        idx = np.flatnonzero(strata == s)
        L[:, idx] = rng.permuted(L[:, idx], axis=1)
    same = (L == lab).all(1)                       # derangement rule: never score the real labelling
    L = L[~same]
    m1 = (L * y).sum(1) / L.sum(1)
    m0 = ((1 - L) * y).sum(1) / (1 - L).sum(1)
    null = m1 - m0
    return float((1 + np.sum(np.abs(null) >= abs(obs) - 1e-12)) / (len(null) + 1)), float(obs)


# ------------------------------------------------------------------ 2. floor
def floor(rng, worlds=1000, reps=2000):
    n_items = 16
    target_sd = PRINTED["SE"] / math.sqrt(1 / N_AM + 1 / N_MA)
    diff = rng.normal(0, 0.8, n_items)
    # calibrate ability SD and intercept so AM mean ~0.70 and learner SD ~ target
    best = None
    for sd_a in np.linspace(0.3, 2.5, 45):
        th = rng.normal(0, sd_a, 4000)
        for c in np.linspace(0.3, 1.8, 31):
            pr = 1 / (1 + np.exp(-(c + th[:, None] - diff[None, :])))
            props = pr.mean(1)
            err = abs(props.mean() - PRINTED["am"]) + abs(props.std() - target_sd)
            if best is None or err < best[0]:
                best = (err, sd_a, c, props.mean(), props.std())
    _, sd_a, c, m_cal, s_cal = best
    out = {}
    for eff in PLANT:
        hits = 0
        rej = 0
        for _ in range(worlds):
            ta = rng.normal(0, sd_a, N_AM)
            tb = rng.normal(0, sd_a, N_MA)
            pa = 1 / (1 + np.exp(-(c + ta[:, None] - diff[None, :])))
            pb = 1 / (1 + np.exp(-(c + tb[:, None] - diff[None, :])))
            pb = np.clip(pb + eff, 0, 1)
            ya = (rng.random(pa.shape) < pa).mean(1)
            yb = (rng.random(pb.shape) < pb).mean(1)
            p, d = rerand_p(ya, yb, rng, reps)
            rej += p < 0.05
            hits += (p < 0.05) and (eff == 0 or d > 0)
        out[f"{eff:.2f}"] = dict(planted=eff, reject_rate=rej / worlds,
                                 power_right_sign=(hits / worlds) if eff else None)
        print(f"  planted MA-AM {eff:+.2f}: reject {rej / worlds:.3f}"
              + (f"  power(right sign) {hits / worlds:.3f}" if eff else "  (false-positive rate)"), flush=True)
    return dict(calibration=dict(ability_sd=float(sd_a), intercept=float(c), am_mean=float(m_cal),
                                 learner_sd=float(s_cal), target_learner_sd=float(target_sd)),
                worlds=worlds, reps=reps, cells=out,
                mde_d_analytic=2.802 * math.sqrt(1 / N_AM + 1 / N_MA),
                mde_points_at_printed_SE=2.802 * PRINTED["SE"])


# ------------------------------------------------------------------ 3. re-analysis
_OP = {"A": "ADD", "M": "MUL", "S": "SUB", "D": "DIV"}


def item_op(name):
    toks = name.strip().upper().split()
    if len(toks) < 2 or toks[0] != "T":
        return None
    return _OP.get(toks[1][0], "?")


def pset(h):
    m = re.search(r"ProblemSet (.+?)\s*$", h or "")
    return m.group(1) if m else ""


def load_arm(path):
    tests = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))   # set -> learner -> (problem,view) -> rows
    last_practice = {}
    times = defaultdict(list)
    klass = {}
    with open(path, encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            sid = r["Anon Student Id"]
            ts = r.get("Step Start Time") or r.get("First Transaction Time") or ""
            klass.setdefault(sid, r.get("Class", "") or "")
            op = item_op(r["Problem Name"])
            if op is None:
                if ts and (sid not in last_practice or ts > last_practice[sid]):
                    last_practice[sid] = ts
                continue
            s = pset(r["Problem Hierarchy"])
            tests[s][sid][(r["Problem Name"], r.get("Problem View", ""))].append(
                (r.get("Step Name", ""), r["First Attempt"] == "correct", op, ts))
            if ts:
                times[s].append(ts)
    return tests, last_practice, times, klass


def score(probs, scoring, trained_only):
    vals = []
    for rows in probs.values():
        op = rows[0][2]
        if trained_only and op not in ("ADD", "MUL"):
            continue
        rows = sorted(rows, key=lambda x: x[3])
        if scoring == "step":
            vals += [float(c) for _, c, _, _ in rows]
        elif scoring == "problem":
            vals.append(float(all(c for _, c, _, _ in rows)))
        else:
            vals.append(float(rows[-1][1]))
    return float(np.mean(vals)) if vals else float("nan")


def reanalyse(src, rng, floor_res, reps=10000):
    from datetime import datetime
    arms = {}
    for tag, pat in (("AM", "S2_AM_Blocked"), ("MA", "S2_MA_Blocked")):
        f = next(p for p in src.iterdir() if pat in p.name)
        arms[tag] = load_arm(f)
    sets = sorted(set(arms["AM"][0]) & set(arms["MA"][0]),
                  key=lambda s: np.median([datetime.fromisoformat(t[:19]).timestamp()
                                           for t in arms["AM"][2][s] + arms["MA"][2][s]]))
    pw8 = floor_res["cells"]["0.08"]["power_right_sign"]
    res = dict(n_am=len(arms["AM"][3]), n_ma=len(arms["MA"][3]), tests=sets, per_test={})
    kl = {**{("AM", k): v for k, v in arms["AM"][3].items()}, **{("MA", k): v for k, v in arms["MA"][3].items()}}
    classes = defaultdict(set)
    for (a, _), c in kl.items():
        classes[c].add(a)
    within = sum(len(v) == 2 for c, v in classes.items() if c) >= 2
    per_learner = {}
    for s in sets:
        res["per_test"][s] = {}
        for trained in (False, True):
            for sc in ("step", "problem", "final"):
                ys, cl = {}, {}
                for a in ("AM", "MA"):
                    d = arms[a][0][s]
                    ys[a] = {sid: score(pr, sc, trained) for sid, pr in d.items()}
                    ys[a] = {k: v for k, v in ys[a].items() if not math.isnan(v)}
                    cl[a] = [kl[(a, k)] for k in ys[a]]
                    per_learner[(s, trained, sc, a)] = ys[a]
                a_, b_ = list(ys["AM"].values()), list(ys["MA"].values())
                strata = (np.r_[cl["AM"], cl["MA"]] if within else None)
                p, d = rerand_p(a_, b_, rng, reps, strata)
                sp = math.sqrt(((len(a_) - 1) * np.var(a_, ddof=1) + (len(b_) - 1) * np.var(b_, ddof=1))
                               / (len(a_) + len(b_) - 2))
                cd = d / sp if sp > 0 else float("nan")
                v = ("MULTIPLICATION FIRST BETTER" if d > 0 else "ADDITION FIRST BETTER") if p < 0.05 else \
                    ("UNINFORMATIVE (BELOW FLOOR)" if pw8 < 0.80 else "NOT DISTINGUISHED")
                res["per_test"][s][f"{'trained' if trained else 'all'}_{sc}"] = dict(
                    am=float(np.mean(a_)), ma=float(np.mean(b_)), n_am=len(a_), n_ma=len(b_),
                    ma_minus_am=d, d=cd, p=p, verdict=v)
        # delay from last practice step to this test, in days, median over learners
        gaps = []
        for a in ("AM", "MA"):
            lp = arms[a][1]
            for sid, pr in arms[a][0][s].items():
                ts = min(r[3] for rows in pr.values() for r in rows if r[3])
                if sid in lp and ts:
                    gaps.append((datetime.fromisoformat(ts[:19]) - datetime.fromisoformat(lp[sid][:19])).total_seconds() / 86400)
        res["per_test"][s]["median_days_after_last_practice"] = float(np.median(gaps)) if gaps else None
    hits = [(s, k) for s, v in res["per_test"].items() for k, c in v.items()
            if isinstance(c, dict) and abs(c["am"] - PRINTED["am"]) <= 0.02 and abs(c["ma"] - PRINTED["ma"]) <= 0.02]
    res["reproduction"] = dict(matches=hits, verdict="REPRODUCES" if hits else "DOES NOT REPRODUCE")
    post = [s for s in sets if "post" in s.lower()]
    if len(post) >= 2:
        imm, dly = post[0], post[-1]
        out = {}
        for trained in (False, True):
            for sc in ("step", "problem", "final"):
                ch = {}
                for a in ("AM", "MA"):
                    i, dl = per_learner[(imm, trained, sc, a)], per_learner[(dly, trained, sc, a)]
                    ch[a] = [dl[k] - i[k] for k in i if k in dl]
                p, d = rerand_p(ch["AM"], ch["MA"], rng, reps)
                out[f"{'trained' if trained else 'all'}_{sc}"] = dict(change_am=float(np.mean(ch["AM"])),
                                                                     change_ma=float(np.mean(ch["MA"])),
                                                                     ma_minus_am=d, p=p)
        res["delay_contrast"] = dict(immediate=imm, delayed=dly, by_scoring=out)
    res["permuted_within_class"] = within
    return res


def main() -> None:
    OUT.mkdir(exist_ok=True)
    rng = np.random.default_rng(SEED)
    print("1. PRINTED STATISTICS (Patel et al. 2016, Study 2, MA vs AM)")
    pc = printed_check()
    for k in ("t_from_B_SE", "p_from_B_SE", "p_from_t", "t_from_p", "SE_from_t", "SE_from_p"):
        print(f"   {k:12s} {pc[k]:.4f}")
    print(f"   implied learner SD: {pc['implied_learner_sd']}")
    print(f"   -> {pc['verdict']}")

    print("\n2. DETECTION FLOOR (synthetic, shaped like ds1190 Study 2)")
    fl = floor(rng)
    print(f"   analytic MDE d = {fl['mde_d_analytic']:.2f}; at the printed SE, {100 * fl['mde_points_at_printed_SE']:.1f} points")

    src = scratch_root() / "ds1190"
    have = src.is_dir() and any("S2_AM_Blocked" in p.name for p in src.iterdir())
    if have:
        print(f"\n3. RE-ANALYSIS of {src}")
        ra = reanalyse(src, rng, fl)
        print(json.dumps(ra, indent=1)[:6000])
    else:
        ra = dict(status="BLOCKED", reason=(
            "ds1190 is not on this machine (scratch_root()/ds1190 absent). DataShop exports are login-gated; the "
            "registry entry 'datashop' (kind upload) records that ds1190 was exported by hand and "
            "attached to an earlier session. No DATASHOP_API_TOKEN / DATASHOP_API_SECRET is set in "
            "this environment, so the web-services route is also closed. A person must log in, export "
            "ds1190 Student-Step (all samples) and attach it; then re-run this script unchanged."))
        print(f"\n3. RE-ANALYSIS: BLOCKED -- {ra['reason']}")
    (OUT / "patel_order.json").write_text(json.dumps(dict(
        printed=PRINTED, printed_check=pc, floor=fl, reanalysis=ra), indent=1, default=float))


if __name__ == "__main__":
    main()
