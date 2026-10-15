"""
Does the positivity estimand depend on the lag between attempting A and attempting B?

The atlas reads B accuracy at first attempt, split by what a learner held in A at that moment
(`positivity.classify`): MASTERED (a correct A attempt before B) against FAILED (A attempted before B,
never correct). It ignores how long before B the A attempts happened. The release penalty in
`studies/identifiability/rdd/LAG.md` moved with lag (+0.044 within a fortnight, +0.013 at 41-81 days, +0.024 at 137-363),
and the programme's outcome-timing rule says every estimand states its lag. This reads the drop
(p_mastered - p_failed) by band of lag = t(first B attempt) - t(first A attempt), a definition that
is the same for both cells and does not condition on A's outcome timing.

PRE-REGISTERED (written and committed before any real corpus is read)

  bands (days)   EARLY [0, 1)   MID [1, 7)   LATE [7, inf)   (LATE pools 7-30 and 30+; reported
                 separately too)
  pair sample    up to 10,000 ordered pairs per corpus, atlas's name-keyed seed (corpus_rng)
  band-readable  both cells >= MIN_CELL (5) learners in that band, control rate inside (0.01, 0.99)
  PRIMARY        within-pair contrast D = drop(LATE) - drop(EARLY), over pairs band-readable in both;
                 mean D with a 95% cluster bootstrap resampling B items (2,000 draws)
  per corpus     UNANSWERABLE  fewer than 30 pairs readable in both EARLY and LATE
                 DECAYS        CI entirely below 0
                 GROWS         CI entirely above 0
                 FLAT          CI inside [-0.02, +0.02]
                 UNRESOLVED    otherwise
  programme      LAG-DEPENDENT if at least two answerable corpora return DECAYS or GROWS in the same
                 direction; LAG-INVARIANT if every answerable corpus is FLAT; MIXED otherwise
  SECONDARY      the same contrast on pairs whose all-lag state is SUPPORTED (edge-like pairs), and
                 the share of readable pairs by band (descriptive)

  FLOOR (run first, on synthetic learners): a planted gate whose drop decays with lag must return
  DECAYS; the same gate with a constant drop must NOT return DECAYS or GROWS. If either fails, no
  real number is read.

WHAT IT CANNOT SEPARATE. Learners who reach B soon after A differ from those who come back weeks
later (engagement, ability, practice in between), so D compares different learners across bands.
Over arbitrary pairs, D measures how the estimand itself moves with lag, whatever the cause; it is
not a forgetting curve for any edge. Pairs share items, and the B-item bootstrap does not absorb
A-item dependence, so intervals may be narrow.

    python3 lag_bands.py floor
    python3 lag_bands.py real [--corpora assist,xes3g5m,ednet,edmcup,eedi] [--out out/lag_bands.json]

DIRECTION: symmetric -- arbitrary ordered pairs take their roles from each learner's timeline (A
attempted before B), and D = drop(LATE) - drop(EARLY) is a within-pair contrast of lag bands;
'direction' means the sign of D.

Direction declaration added 2026-09-24 (reversed-arrow rule, shared/experimental-contract.md):
nothing reported depends on edge orientation, so no reversed-arrow control applies.
"""

from __future__ import annotations

import json
import math
import random
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "studies/identifiability/latent-shape"))
sys.path.insert(0, str(HERE.parents[2]))

from positivity import MIN_CELL, at_item, states, timelines  # noqa: E402
from shared.edge_state import SUPPORTED, classify_edge  # noqa: E402
from positivity import mde  # noqa: E402

BANDS = [("EARLY", 0.0, 1.0), ("MID", 1.0, 7.0), ("LATE_7_30", 7.0, 30.0), ("LATE_30P", 30.0, math.inf)]
LATE = ("LATE_7_30", "LATE_30P")
MAX_PAIRS, MIN_BOTH, BOOT, FLAT_BAND = 10_000, 30, 2000, 0.02
DAY = 86400.0


def to_seconds(t) -> float:
    """Every corpus's clock on one scale. Numbers above 1e11 are epoch milliseconds."""
    if isinstance(t, (int, float)):
        v = float(t)
    else:
        s = str(t)
        try:
            v = float(s)
        except ValueError:
            for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
                try:
                    return datetime.strptime(s, fmt).timestamp()
                except ValueError:
                    continue
            raise ValueError(f"unparsed time {s!r}")
    return v / 1000.0 if v > 1e11 else v


def band_of(lag_days: float) -> str:
    for name, lo, hi in BANDS:
        if lo <= lag_days < hi:
            return name
    return BANDS[-1][0]


def pair_cells(a, b, first_touch, first_pass, idx):
    """Per band: outcomes of MASTERED and FAILED learners, with lag measured from A's first touch."""
    out = defaultdict(lambda: {"m": [], "f": []})
    allc = {"m": [], "f": []}
    for learner, tb, y in idx[b]:
        ta = first_touch[learner].get(a)
        if ta is None or ta >= tb:
            continue
        pa = first_pass[learner].get(a)
        cell = "m" if (pa is not None and pa < tb) else "f"
        bnd = band_of((tb - ta) / DAY)
        out[bnd][cell].append(y)
        allc[cell].append(y)
        if bnd in LATE:
            out["LATE"][cell].append(y)
    return out, allc


def drop(cells):
    m, f = cells["m"], cells["f"]
    if len(m) < MIN_CELL or len(f) < MIN_CELL:
        return None
    pm = float(np.mean(m))
    if pm <= 0.01 or pm >= 0.99:
        return None
    return pm - float(np.mean(f))


def analyse(first_touch, first_pass, idx, pairs, rng_seed=0):
    rows = []
    for a, b in pairs:
        by_band, allc = pair_cells(a, b, first_touch, first_pass, idx)
        d = {k: drop(by_band[k]) for k in [n for n, _, _ in BANDS] + ["LATE"]}
        # all-lag state, as the atlas would read it before the reachability gate
        n_m, n_f = len(allc["m"]), len(allc["f"])
        state = None
        if n_m >= MIN_CELL and n_f >= MIN_CELL:
            pm = float(np.mean(allc["m"]))
            m = mde(n_m, n_f, pm)
            state, _ = classify_edge(m, pm - float(np.mean(allc["f"])))
        rows.append(dict(a=a, b=b, drops=d, state=state))
    return rows


def contrast(rows, seed=0):
    both = [r for r in rows if r["drops"]["EARLY"] is not None and r["drops"]["LATE"] is not None]
    res = dict(pairs_both=len(both))
    if len(both) < MIN_BOTH:
        res.update(verdict="UNANSWERABLE")
        return res
    diffs = np.array([r["drops"]["LATE"] - r["drops"]["EARLY"] for r in both])
    by_b = defaultdict(list)
    for i, r in enumerate(both):
        by_b[r["b"]].append(i)
    groups = list(by_b.values())
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(BOOT):
        pick = rng.integers(0, len(groups), len(groups))
        idxs = [i for g in pick for i in groups[g]]
        boots.append(float(diffs[idxs].mean()))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    mean = float(diffs.mean())
    if hi < 0:
        v = "DECAYS"
    elif lo > 0:
        v = "GROWS"
    elif lo >= -FLAT_BAND and hi <= FLAT_BAND:
        v = "FLAT"
    else:
        v = "UNRESOLVED"
    res.update(mean_D=mean, ci=[float(lo), float(hi)], verdict=v,
               early_mean=float(np.mean([r["drops"]["EARLY"] for r in both])),
               late_mean=float(np.mean([r["drops"]["LATE"] for r in both])))
    return res


def band_summary(rows):
    out = {}
    for name, _, _ in BANDS:
        ds = [r["drops"][name] for r in rows if r["drops"][name] is not None]
        out[name] = dict(readable_pairs=len(ds), median_drop=float(np.median(ds)) if ds else None)
    return out


# ------------------------------------------------------------------ floor

def synth(decay: bool, seed: int, learners=3000, items=48, gate=0.25, tau_days=5.0):
    """Learners meet items in random order at random gaps; items form a chain of planted gates.
    A learner who has not passed the parent when they first try the child loses `gate`, times
    exp(-lag/tau) in the decay world (constant in the flat world). The loss decays because a learner
    who failed the parent long ago has had time to learn it elsewhere."""
    rnd = random.Random(seed)
    rows = []
    parent = {f"i{k}": f"i{k-1}" for k in range(1, items)}
    for u in range(learners):
        ability = rnd.gauss(0, 1)
        t = rnd.uniform(0, 30) * DAY
        seen_pass, first_t = {}, {}
        order = [f"i{k}" for k in range(items)]
        rnd.shuffle(order)
        for it in order:
            for _ in range(rnd.randint(1, 3)):
                # sessions: most attempts follow within minutes, some after a break of days
                t += (rnd.expovariate(1 / 0.01) if rnd.random() < 0.8 else rnd.expovariate(1 / 5.0)) * DAY
                p = 1 / (1 + math.exp(-(0.3 + ability)))
                par = parent.get(it)
                if par is not None and it not in first_t and par in first_t and par not in seen_pass:
                    lag = (t - first_t[par]) / DAY
                    p -= gate * (math.exp(-lag / tau_days) if decay else 1.0)
                ok = rnd.random() < max(0.02, min(0.98, p))
                first_t.setdefault(it, t)
                if ok:
                    seen_pass.setdefault(it, t)
                rows.append((f"u{u}", it, ok, t, False, False))
    return rows, list(parent.items())


def run_floor():
    results = {}
    for world, decay in (("decay", True), ("flat", False)):
        verdicts = []
        for s in range(3):
            rows, gate_pairs = synth(decay, seed=100 + s)
            ft, fp, oat = states(timelines(rows))
            idx = at_item(ft, oat)
            pairs = [(a, b) for b, a in gate_pairs]
            verdicts.append(contrast(analyse(ft, fp, idx, pairs), seed=s))
        results[world] = verdicts
        print(f"   {world:6s} " + "  ".join(v["verdict"] + " (D " + format(v.get("mean_D", float("nan")), "+.3f")
                                          + ", pairs " + str(v["pairs_both"]) + ")" for v in verdicts))
    ok = (all(v["verdict"] == "DECAYS" for v in results["decay"])
          and not any(v["verdict"] in ("DECAYS", "GROWS") for v in results["flat"]))
    print(f"   FLOOR {'PASSES' if ok else 'FAILS'}")
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / "lag_bands_floor.json").write_text(json.dumps(dict(passes=ok, results=results), indent=1))
    return ok


# ------------------------------------------------------------------ real

def loaders():
    import atlas
    from build_matrix import LOADERS
    return {"assist": lambda: LOADERS["assist"](),
            "xes3g5m": lambda: atlas.xes3g5m_rows(),
            "ednet": lambda: atlas.ednet_rows(),
            "edmcup": lambda: atlas.edmcup_rows(),
            "eedi": lambda: atlas.eedi_rows()}


def run_real(names, out):
    import atlas
    floor = json.loads((HERE / "out" / "lag_bands_floor.json").read_text())
    if not floor.get("passes"):
        raise SystemExit("floor has not passed; no real number is read")
    L = loaders()
    res = {}
    for name in names:
        rows = ((u, i, ok, to_seconds(t), h1, h2) for u, i, ok, t, h1, h2 in L[name]())
        tl = timelines(rows)
        ft, fp, oat = states(tl)
        idx = at_item(ft, oat)
        items = sorted(idx)
        pairs = [(a, b) for a in items for b in items if a != b]
        rng = atlas.corpus_rng(name)
        if len(pairs) > MAX_PAIRS:
            pairs = [pairs[i] for i in rng.choice(len(pairs), MAX_PAIRS, replace=False)]
        prs = analyse(ft, fp, idx, pairs)
        primary = contrast(prs)
        secondary = contrast([r for r in prs if r["state"] == SUPPORTED])
        bands = band_summary(prs)
        res[name] = dict(learners=len(tl), items=len(items), pairs=len(pairs), primary=primary,
                         secondary_supported=secondary, bands=bands)
        p = primary
        print(f"  {name:8s} learners {len(tl):7,d}  pairs {len(pairs):6,d}  both-readable {p['pairs_both']:5d}  "
              + (f"early {p['early_mean']:+.3f}  late {p['late_mean']:+.3f}  D {p['mean_D']:+.4f} "
                 f"[{p['ci'][0]:+.4f}, {p['ci'][1]:+.4f}]  " if "mean_D" in p else "")
              + f"{p['verdict']}   | supported pairs: {secondary['verdict']} ({secondary['pairs_both']})")
        parts = []
        for k, v in bands.items():
            md = v["median_drop"]
            parts.append(f"{k} {v['readable_pairs']}" + (f" (median drop {md:+.3f})" if md is not None else ""))
        print("           readable pairs by band: " + ", ".join(parts), flush=True)
    answerable = [v["primary"]["verdict"] for v in res.values() if v["primary"]["verdict"] != "UNANSWERABLE"]
    if answerable and all(v == "FLAT" for v in answerable):
        overall = "LAG-INVARIANT"
    elif answerable.count("DECAYS") >= 2 or answerable.count("GROWS") >= 2:
        overall = "LAG-DEPENDENT"
    else:
        overall = "MIXED"
    summary = ", ".join(k + ": " + v["primary"]["verdict"] for k, v in res.items())
    print(f"\nPROGRAMME VERDICT: {overall}  ({summary})")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(bands_days=[b[1:] for b in BANDS], min_cell=MIN_CELL, max_pairs=MAX_PAIRS,
                                   verdict=overall, corpora=res), indent=1, default=str) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "floor"
    if mode == "floor":
        sys.exit(0 if run_floor() else 1)
    names = (sys.argv[sys.argv.index("--corpora") + 1].split(",") if "--corpora" in sys.argv
             else ["assist", "xes3g5m", "ednet", "edmcup", "eedi"])
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else HERE / "out" / "lag_bands.json"
    run_real(names, out)
