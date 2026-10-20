"""How reliable is the prerequisite drop WITHIN a lag band? (Paper 2 placeholder 2; Paper II)

`studies/identifiability/overlap/lag_bands.py` showed the drop depends on the lag between a learner's
first try at A and their first try at B: it is 24-39% smaller after a week than within a day, in every
corpus where both are readable (LAG-BANDS.md). A5's reliability figures (`split_half.py`, `tail.py`,
`raise_kappa.py`) pool every lag, so they pool estimands. Paper 2 section 7 says a reliability pooled
over lags pools estimands and leaves the banded reliability as a placeholder. This fills it.

PRE-REGISTERED 2026-10-05, committed before any real corpus is read by this script.

  corpora    XES3G5M (the 200 KCs the most learners reached; 39,800 ordered pairs) and EdNet (the
             atlas reader's 6,000-learner prefix, every item). XES3G5M is primary: it carries A5's
             standing best reading (0.643).
  bands      lag_bands.py's: EARLY [0, 1) day, MID [1, 7) days, LATE [7, inf) days, and ALL (no lag
             restriction; the estimand A5 has always read).
  estimand   positivity.py's drop, unchanged: first-attempt B outcome, MASTERED minus FAILED, with A
             first touched before B. In a band, only encounters whose lag falls in the band count.
  method     split_half.py's: random halves of learners, drop scored on each half, Spearman across
             pairs readable in BOTH halves, mean over splits, Spearman-Brown to the full sample.
             20 splits. Cell floors 5 / 10 / 20; PRIMARY floor 10. Decision kappa beside it
             (raise_kappa.py's adopted rule: assert when drop - 1.0 se > 0.10), because Paper 2
             proposes kappa as the reported figure.
  controls   SIZE-MATCHED (the control that matters): a band has smaller cells than ALL, and a
             smaller cell is less reliable whatever its lag. For each band, ALL-lag encounters are
             thinned at random, per pair, to that band's share of the pair's encounters (share
             from the full corpus), so the thinned arm has the band's expected cell size and no lag
             information. band minus thinned = what the lag itself does to reliability. Scale is
             asserted with shared/controls.check_control_scale (thinned cell size against band).
             DERANGED (the board's rule: every reliability is reported as excess over its own
             deranged arm): a learner's A-side history is replaced by another learner's of the
             same half, re-anchored to the recipient's start time, B side untouched; 4 splits.
             A derangement, not a permutation (no fixed points).
  check      the matrix implementation (pairgrid.py) must equal positivity.classify cell for cell on
             200 random pairs of each corpus before anything is read.

  VERDICTS (primary floor 10)
    per band   MEETS A5 if Spearman-Brown >= 0.80 on >= 100 median pairs; BELOW otherwise;
               NOT ESTIMABLE if fewer than 30 pairs are readable on both halves in any split.
    lag effect for each of EARLY, MID, LATE, the per-split difference band - thinned:
               LAG RAISES RELIABILITY   central 95% of splits above 0
               LAG LOWERS RELIABILITY   central 95% of splits below 0
               SIZE ONLY                central 95% inside [-0.05, +0.05]
               UNRESOLVED               otherwise
    programme  LAG BANDING RESCUES A5 if any band MEETS on XES3G5M or EdNet; otherwise
               LAG BANDING DOES NOT RESCUE A5. Reported with each band's excess over deranged.

  FLOOR (run first; synthetic learners; if it fails no real number is read)
    worlds     40 items, gates planted on 20% of item pairs with sizes U(0.05, 0.35); learners meet
               items in random order with lag_bands.synth's session timing. DECAY: the gate shrinks
               as exp(-lag / 2 days). FLAT: the gate is constant. Two seeds each, 4,000 learners.
    pass if    FLAT: |band - thinned| <= 0.10 for EARLY and LATE (lag carries no reliability of its
               own when the gate does not depend on lag), and ALL Spearman-Brown >= 0.30 (the
               machinery sees the planted gates at all);
               DECAY: EARLY - thinned >= +0.05 and LATE - thinned <= -0.05 (a band where the
               planted gate lives is more reliable than its size, one where it has faded is less).

WHAT IT CANNOT SEPARATE (lag_bands.py's caveat carries over): learners who reach B within a day are
not the learners who come back weeks later, so a band is a different population as well as a
different lag. The size-matched control removes cell size, not population.

DATA. XES3G5M (licence unstated; research use, non-redistributable) and EdNet KT1 (CC BY-NC 4.0; no
commercial use, no model training -- counting cells is neither), read from the scratch directory via
shared.paths (`XES_DIR`, `EDNET_ZIP`). Only aggregates are written to out/.

    python3 lag_band_reliability.py floor
    python3 lag_band_reliability.py real [--corpora xes3g5m,ednet] [--splits 20]
"""

from __future__ import annotations

import json
import math
import random
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pairgrid as pg  # noqa: E402

sys.path.insert(0, str(HERE.parents[2]))
from shared.controls import check_control_scale  # noqa: E402
from shared.stats import kappa, spearman  # noqa: E402

SEED = 20261005
SPLITS = 20
DERANGED_SPLITS = 4
CELLS = (5, 10, 20)
PRIMARY_CELL = 10
GATE = 0.80
MIN_PAIRS = 30
MIN_MEDIAN_PAIRS = 100
SIZE_ONLY = 0.05
BAR, Z = 0.10, 1.0
BANDS = ("EARLY", "MID", "LATE", "ALL")
LAG_BANDS = ("EARLY", "MID", "LATE")
XES_TOP = 200
WORKERS = 2
OUT = HERE / "out"

# ---------------------------------------------------------------- pass machinery

_G = {}


def _init(FT, FP, Y, kw):
    _G.update(FT=FT, FP=FP, Y=Y, kw=kw)


def _col(b):
    kw = dict(_G["kw"])
    if "seed" in kw:
        kw["rng"] = np.random.default_rng(kw.pop("seed") * 100_003 + b)
    return b, pg.column_cells(_G["FT"], _G["FP"], _G["Y"], b, **kw)


def run_pass(FT, FP, Y, groups, bands, workers=WORKERS, **kw):
    """Every B column; returns band -> stat -> (G, K_A, K_B)."""
    K = FT.shape[1]
    kw = dict(kw, groups=groups, bands=bands)
    if workers > 1:
        with Pool(workers, initializer=_init, initargs=(FT, FP, Y, kw)) as p:
            res = dict(p.imap_unordered(_col, range(K), chunksize=4))
    else:
        _init(FT, FP, Y, kw)
        res = dict(_col(b) for b in range(K))
    names = list(res[0])
    out = {}
    for bd in names:
        out[bd] = {s: np.stack([res[b][bd][s] for b in range(K)], axis=2) for s in ("nm", "sm", "nf", "sf")}
    return out


def halves_matrix(n, splits, rng):
    """(n, 2*splits) membership; column 2s and 2s+1 are the two halves of split s."""
    G = np.zeros((n, 2 * splits), np.float32)
    for s in range(splits):
        perm = rng.permutation(n)
        G[perm[: n // 2], 2 * s] = 1
        G[perm[n // 2:], 2 * s + 1] = 1
    return G


def score_split(cells, g1, g2, min_cell):
    """Spearman, kappa and pair count between two groups of one band's cells."""
    pick = lambda c, g: {k: v[g] for k, v in c.items()}
    d1, s1, ok1 = pg.drops(pick(cells, g1), min_cell)
    d2, s2, ok2 = pg.drops(pick(cells, g2), min_cell)
    both = ok1 & ok2 & np.isfinite(s1) & np.isfinite(s2)
    np.fill_diagonal(both, False)
    n = int(both.sum())
    if n < MIN_PAIRS:
        return dict(pairs=n, r=float("nan"), kappa=float("nan"), assert_rate=float("nan"))
    x, y = d1[both], d2[both]
    a1 = (x - Z * s1[both]) > BAR
    a2 = (y - Z * s2[both]) > BAR
    return dict(pairs=n, r=spearman(x, y), kappa=kappa(a1, a2), assert_rate=float((a1.mean() + a2.mean()) / 2),
                cell_median=float(np.median((cells["nm"][g1] + cells["nf"][g1])[both])))


def sb(r):
    return 2 * r / (1 + r) if np.isfinite(r) and r > -1 else float("nan")


def summarise(per_split):
    rs = [p["r"] for p in per_split if np.isfinite(p["r"])]
    ks = [p["kappa"] for p in per_split if np.isfinite(p["kappa"])]
    if not rs:
        return dict(splits=0, estimable=False)
    r = float(np.mean(rs))
    return dict(splits=len(rs), estimable=True, pairs_median=int(np.median([p["pairs"] for p in per_split])),
                split_half=r, spearman_brown=sb(r), kappa=float(np.mean(ks)) if ks else float("nan"),
                assert_rate=float(np.nanmean([p["assert_rate"] for p in per_split])),
                cell_median=float(np.nanmedian([p.get("cell_median", np.nan) for p in per_split])),
                sb_by_split=[sb(x) for x in rs])


def lag_verdict(diffs):
    d = np.asarray([x for x in diffs if np.isfinite(x)])
    if len(d) < 3:
        return "NOT ESTIMABLE", None
    lo, hi = np.percentile(d, [2.5, 97.5])
    if lo > 0:
        v = "LAG RAISES RELIABILITY"
    elif hi < 0:
        v = "LAG LOWERS RELIABILITY"
    elif lo >= -SIZE_ONLY and hi <= SIZE_ONLY:
        v = "SIZE ONLY"
    else:
        v = "UNRESOLVED"
    return v, [float(d.mean()), float(lo), float(hi)]


def analyse(FT, FP, Y, start, splits, rng, cells=CELLS, deranged_splits=DERANGED_SPLITS, lag_scale=pg.DAY,
            workers=WORKERS, verbose=True):
    n, K = FT.shape
    G = halves_matrix(n, splits, rng)
    full = np.ones((n, 1), np.float32)
    groups = np.hstack([full, G])
    real = run_pass(FT, FP, Y, groups, BANDS, workers=workers, lag_scale=lag_scale)
    # shares: band encounters / ALL encounters, per pair, on the full corpus (group 0)
    tot = real["ALL"]["nm"][0] + real["ALL"]["nf"][0]
    keep = {}
    for bd in LAG_BANDS:
        nb = real[bd]["nm"][0] + real[bd]["nf"][0]
        with np.errstate(invalid="ignore", divide="ignore"):
            share = np.where(tot > 0, nb / np.maximum(tot, 1), 0.0)
        keep[bd] = share
    # the thinned control needs a per-(A, B) keep probability; column_cells takes a (K,) vector per
    # B column, so the pass is run with a per-column lookup
    thin = run_pass_thin(FT, FP, Y, G, keep, workers=workers, lag_scale=lag_scale, seed=int(rng.integers(1 << 30)))
    # deranged: a dedicated split per pass, donors within each half
    der = []
    for _ in range(deranged_splits):
        perm = rng.permutation(n)
        h1, h2 = perm[: n // 2], perm[n // 2:]
        donor = pg.derangement(n, rng, blocks=[h1, h2])
        g2 = np.zeros((n, 2), np.float32)
        g2[h1, 0] = 1
        g2[h2, 1] = 1
        der.append(run_pass(FT, FP, Y, g2, BANDS, workers=workers, donor=donor, start=start, lag_scale=lag_scale))

    out = {}
    for mc in cells:
        row = {}
        for bd in BANDS:
            ps = [score_split(real[bd], 1 + 2 * s, 2 + 2 * s, mc) for s in range(splits)]
            r = summarise(ps)
            dps = [score_split(dd[bd], 0, 1, mc) for dd in der]
            dr = summarise(dps)
            r["deranged"] = {k: dr.get(k) for k in ("spearman_brown", "kappa", "pairs_median", "splits")}
            if r.get("estimable") and dr.get("estimable"):
                r["excess_sb"] = r["spearman_brown"] - dr["spearman_brown"]
                r["excess_kappa"] = r["kappa"] - dr["kappa"]
            if bd in LAG_BANDS:
                tps = [score_split(thin["THIN_" + bd], 2 * s, 2 * s + 1, mc) for s in range(splits)]
                t = summarise(tps)
                r["thinned"] = {k: t.get(k) for k in ("spearman_brown", "kappa", "pairs_median", "cell_median")}
                diffs = [sb(a["r"]) - sb(b["r"]) for a, b in zip(ps, tps)]
                r["lag_effect"], r["lag_effect_mean_lo_hi"] = lag_verdict(diffs)
                if r.get("estimable") and t.get("estimable"):
                    chk = check_control_scale({bd: r["cell_median"], "thinned": t["cell_median"]}, ["thinned"],
                                              strict=False)
                    r["control_scale"] = dict(ok=chk["ok"], ratio=chk["ratios"]["thinned"])
            if not r.get("estimable"):
                r["verdict"] = "NOT ESTIMABLE"
            else:
                r["verdict"] = ("MEETS A5" if r["spearman_brown"] >= GATE and r["pairs_median"] >= MIN_MEDIAN_PAIRS
                                else "BELOW")
            r.pop("sb_by_split", None)
            row[bd] = r
            if verbose:
                pr = (f"  floor {mc:2d} {bd:5s} " + (f"pairs {r['pairs_median']:6,d} SB {r['spearman_brown']:+.3f} "
                      f"kappa {r['kappa']:+.3f} | deranged SB {r['deranged'].get('spearman_brown') or float('nan'):+.3f} "
                      f"kappa {r['deranged'].get('kappa') or float('nan'):+.3f}" if r.get("estimable") else "NOT ESTIMABLE"))
                if bd in LAG_BANDS and r.get("estimable"):
                    t = r["thinned"]
                    pr += (f" | thinned SB {t.get('spearman_brown') or float('nan'):+.3f} -> {r['lag_effect']}"
                           f" {r['lag_effect_mean_lo_hi']}")
                print(pr, flush=True)
        out[str(mc)] = row
    return out


def _col_thin(b):
    kw = dict(_G["kw"])
    rng = np.random.default_rng(kw.pop("seed") * 100_003 + b)
    keep = kw.pop("keep")
    return b, pg.column_cells(_G["FT"], _G["FP"], _G["Y"], b, rng=rng,
                              thinned_all={bd: v[:, b].astype(np.float32) for bd, v in keep.items()}, **kw)


def run_pass_thin(FT, FP, Y, groups, keep, workers=WORKERS, **kw):
    K = FT.shape[1]
    kw = dict(kw, groups=groups, bands=(), keep=keep)
    if workers > 1:
        with Pool(workers, initializer=_init, initargs=(FT, FP, Y, kw)) as p:
            res = dict(p.imap_unordered(_col_thin, range(K), chunksize=4))
    else:
        _init(FT, FP, Y, kw)
        res = dict(_col_thin(b) for b in range(K))
    out = {}
    for bd in res[0]:
        out[bd] = {s: np.stack([res[b][bd][s] for b in range(K)], axis=2) for s in ("nm", "sm", "nf", "sf")}
    return out


# ---------------------------------------------------------------- floor

def synth(decay: bool, seed: int, learners=4000, items=40, density=0.20, tau_days=2.0):
    """Learners meet items in random order at lag_bands.synth's session timing; planted gates of
    varying size on `density` of item pairs (a -> b with a < b in a hidden order)."""
    rnd = random.Random(seed)
    names = [f"i{k}" for k in range(items)]
    gates = {}
    for a in range(items):
        for b in range(a + 1, items):
            if rnd.random() < density:
                gates.setdefault(b, []).append((a, rnd.uniform(0.05, 0.35)))
    rows = []
    for u in range(learners):
        ability = rnd.gauss(0, 1)
        t = rnd.uniform(0, 30) * pg.DAY
        first_t, passed = {}, set()
        order = list(range(items))
        rnd.shuffle(order)
        for it in order:
            for _ in range(rnd.randint(1, 3)):
                t += (rnd.expovariate(1 / 0.01) if rnd.random() < 0.8 else rnd.expovariate(1 / 5.0)) * pg.DAY
                p = 1 / (1 + math.exp(-(0.3 + ability)))
                if it not in first_t:
                    for a, g in gates.get(it, []):
                        if a in first_t and a not in passed:
                            lag = (t - first_t[a]) / pg.DAY
                            p -= g * (math.exp(-lag / tau_days) if decay else 1.0)
                ok = rnd.random() < max(0.02, min(0.98, p))
                first_t.setdefault(it, t)
                if ok:
                    passed.add(it)
                rows.append((f"u{u}", names[it], ok, t, False, False))
    return rows


def run_floor(splits=8):
    rng = np.random.default_rng(SEED)
    res, ok = {}, True
    for world, decay in (("flat", False), ("decay", True)):
        res[world] = []
        for seed in (1, 2):
            grid = pg.Grid(synth(decay, seed), timed=False)
            print(f"{world} seed {seed}: {grid.shape}", flush=True)
            r = analyse(grid.FT, grid.FP, grid.Y, grid.start, splits, rng, cells=(PRIMARY_CELL,),
                        deranged_splits=1, verbose=True)[str(PRIMARY_CELL)]
            e = {bd: (r[bd].get("lag_effect_mean_lo_hi") or [float("nan")])[0] for bd in LAG_BANDS}
            allsb = r["ALL"].get("spearman_brown", float("nan"))
            if decay:
                passed = e["EARLY"] >= 0.05 and e["LATE"] <= -0.05
            else:
                passed = abs(e["EARLY"]) <= 0.10 and abs(e["LATE"]) <= 0.10 and allsb >= 0.30
            ok &= bool(passed)
            res[world].append(dict(seed=seed, band_minus_thinned=e, all_sb=allsb, passes=bool(passed), rows=r))
            print(f"   -> band - thinned {e}; ALL SB {allsb:+.3f}; {'PASS' if passed else 'FAIL'}", flush=True)
    print(f"FLOOR {'PASSES' if ok else 'FAILS'}")
    OUT.mkdir(exist_ok=True)
    (OUT / "lag_band_reliability_floor.json").write_text(json.dumps(dict(passes=ok, results=res), indent=1,
                                                                        default=float) + "\n")
    return ok


# ---------------------------------------------------------------- real

def load(name):
    import atlas
    if name == "xes3g5m":
        grid = pg.Grid(atlas.xes3g5m_rows())
        print(f"xes3g5m: {grid.shape[0]:,} learners, {grid.shape[1]} KCs; checked "
              f"{pg.check_against_classify(grid, 200)} pairs against positivity.classify", flush=True)
        return grid.subset(grid.top_items(XES_TOP))
    if name == "ednet":
        grid = pg.Grid(atlas.ednet_rows())
        print(f"ednet: {grid.shape[0]:,} learners, {grid.shape[1]} items; checked "
              f"{pg.check_against_classify(grid, 200)} pairs against positivity.classify", flush=True)
        return grid
    raise SystemExit(f"unknown corpus {name}")


def run_real(names, splits):
    floor = json.loads((OUT / "lag_band_reliability_floor.json").read_text())
    if not floor.get("passes"):
        raise SystemExit("floor has not passed; no real number is read")
    rng = np.random.default_rng(SEED)
    res = {}
    for name in names:
        grid = load(name)
        print(f"{name}: scoring {grid.shape[1]} items, {grid.shape[1] * (grid.shape[1] - 1):,} ordered pairs, "
              f"{splits} splits", flush=True)
        res[name] = dict(learners=grid.shape[0], items=grid.shape[1],
                         floors=analyse(grid.FT, grid.FP, grid.Y, grid.start, splits, rng))
        (OUT / "lag_band_reliability.json").write_text(json.dumps(dict(seed=SEED, splits=splits, bar=BAR, z=Z,
                                                                       gate=GATE, corpora=res), indent=1,
                                                                  default=float) + "\n")
    meets = [(c, bd) for c, v in res.items() for bd, r in v["floors"][str(PRIMARY_CELL)].items()
             if r.get("verdict") == "MEETS A5"]
    verdict = "LAG BANDING RESCUES A5" if meets else "LAG BANDING DOES NOT RESCUE A5"
    print(f"\nPROGRAMME VERDICT: {verdict}" + (f" ({meets})" if meets else ""))
    (OUT / "lag_band_reliability.json").write_text(json.dumps(dict(seed=SEED, splits=splits, bar=BAR, z=Z, gate=GATE,
                                                                   verdict=verdict, corpora=res), indent=1,
                                                              default=float) + "\n")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "floor"
    if mode == "floor":
        sys.exit(0 if run_floor() else 1)
    corp = sys.argv[sys.argv.index("--corpora") + 1].split(",") if "--corpora" in sys.argv else ["xes3g5m", "ednet"]
    spl = int(sys.argv[sys.argv.index("--splits") + 1]) if "--splits" in sys.argv else SPLITS
    run_real(corp, spl)
