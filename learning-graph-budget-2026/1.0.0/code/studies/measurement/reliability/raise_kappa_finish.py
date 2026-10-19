"""The two finishing modes of raise_kappa.py (`--rescore`, `--curve`). Design and verdicts are the
FINISHING section of raise_kappa.py's docstring; this file only holds the code, so the lever run in
raise_kappa.py stays as it was run.

    python3 raise_kappa.py --rescore
    python3 raise_kappa.py --curve [--corpus xes3g5m|ednet]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import raise_kappa as rk  # noqa: E402
from shared.stats import kappa  # noqa: E402


def rescore(path=HERE / "out/raise_kappa.json", out=HERE / "out/raise_kappa_rescored.json") -> None:
    """Re-apply the REGISTERED reject rule to the committed run. Nothing is recomputed."""
    d = json.loads(Path(path).read_text())
    k0, kd0 = d["baseline"], d["deranged_baseline"]
    base_eff = d["levers"]["baseline"]["effective"]
    rows, changed = {}, []
    for name, v in d["levers"].items():
        if name == "baseline":
            continue
        reg = rk.registered_manufactured(v["deranged"])
        rel = rk.relative_manufactured(v["kappa"], v["deranged"], k0, kd0)
        degenerate = bool(v.get("degenerate_real") or v.get("degenerate_deranged"))
        real = bool(v["gain"] >= rk.MIN_GAIN and not (reg or rel) and v["coverage"] >= rk.MIN_COVERAGE
                    and not degenerate)
        verdict = ("DEGENERATE" if degenerate else "MANUFACTURED" if (reg or rel) else "REAL" if real
                   else "thin coverage" if v["coverage"] < rk.MIN_COVERAGE else "no gain")
        old = ("DEGENERATE" if degenerate else "MANUFACTURED" if v["manufactured"] else "REAL" if v["real"]
               else "thin coverage" if v["coverage"] < rk.MIN_COVERAGE else "no gain")
        if verdict != old:
            changed.append(f"{name}: {old} -> {verdict}")
        rows[name] = dict(kappa=v["kappa"], deranged=v["deranged"], excess=v["excess"], gain=v["gain"],
                          coverage=v["coverage"], effective=v["effective"], registered_manufactured=reg,
                          relative_manufactured=rel, verdict_as_run=old, verdict_registered=verdict)
        print(f"  {name:14s} kappa {v['kappa']:+.3f} deranged {v['deranged']:+.3f} excess {v['excess']:+.3f} "
              f"gain {v['gain']:+.3f} cov {v['coverage']:4.0%}  as run: {old:13s} registered: {verdict}")
    real = [k for k, r in rows.items() if r["verdict_registered"] == "REAL"]
    best = max((rows[k] for k in real if rows[k]["effective"] > base_eff), key=lambda r: r["effective"], default=None)
    verdict = ("NO LEVER IS REAL UNDER THE REGISTERED RULE; KEEP LCB z = 1.0" if not real else
               f"REAL: {real}" + ("" if best else "; none beats the baseline's effective edge"))
    print("\nchanged by the registered rule:", changed or "none")
    print("VERDICT:", verdict)
    Path(out).write_text(json.dumps(dict(source=Path(path).name, max_deranged=rk.MAX_DERANGED,
                                         min_gain=rk.MIN_GAIN, min_coverage=rk.MIN_COVERAGE, baseline=k0,
                                         deranged_baseline=kd0, baseline_effective=base_eff, levers=rows,
                                         changed=changed, verdict=verdict), indent=2) + "\n")
    print(f"wrote {out}")


def curve(corpus="xes3g5m", items=90, min_cell=10, fracs=(0.15, 0.3, 0.5, 0.75, 1.0), subsamples=4,
          splits=4, der_splits=2, ednet_learners=60_000, out=None) -> None:
    """Baseline-rule kappa, its deranged arm and the EXCESS against learners per half."""
    import atlas
    import pairgrid as pg
    from scipy.optimize import curve_fit

    rng = np.random.default_rng(rk.SEED + 7)
    rows = (atlas.xes3g5m_rows(rk.SCRATCH / "xes3g5m") if corpus == "xes3g5m"
            else atlas.ednet_rows(limit_learners=ednet_learners))
    grid = pg.Grid(rows)
    print(f"{corpus}: {grid.shape[0]:,} learners, {grid.shape[1]} items; checked "
          f"{pg.check_against_classify(grid, 200)} pairs against positivity.classify", flush=True)
    grid.subset(grid.top_items(items))
    n_all = grid.shape[0]

    def kap(c, g1, g2):
        d1, s1, ok1 = pg.drops({k: v[g1] for k, v in c.items()}, min_cell)
        d2, s2, ok2 = pg.drops({k: v[g2] for k, v in c.items()}, min_cell)
        both = ok1 & ok2 & np.isfinite(s1) & np.isfinite(s2)
        np.fill_diagonal(both, False)
        if both.sum() < 100:
            return float("nan")
        return kappa((d1[both] - rk.BASE_Z * s1[both]) > rk.BAR, (d2[both] - rk.BASE_Z * s2[both]) > rk.BAR)

    def cells(FT, FP, Y, G, donor=None, start=None):
        res = [pg.column_cells(FT, FP, Y, b, G, donor=donor, start=start)["ALL"] for b in range(FT.shape[1])]
        return {s: np.stack([r[s] for r in res], axis=2) for s in ("nm", "sm", "nf", "sf")}

    pts = {}
    for frac in fracs:
        n = max(200, int(n_all * frac))
        reals, ders = [], []
        for _ in range(subsamples if frac < 1.0 else 1):
            sub = np.sort(rng.choice(n_all, n, replace=False))
            FT, FP, Y, st = grid.FT[sub], grid.FP[sub], grid.Y[sub], grid.start[sub]
            G = np.zeros((n, 2 * splits), np.float32)
            for s in range(splits):
                perm = rng.permutation(n)
                G[perm[: n // 2], 2 * s] = 1
                G[perm[n // 2:], 2 * s + 1] = 1
            c = cells(FT, FP, Y, G)
            reals += [kap(c, 2 * s, 2 * s + 1) for s in range(splits)]
            for _ in range(der_splits):
                perm = rng.permutation(n)
                h1, h2 = perm[: n // 2], perm[n // 2:]
                donor = pg.derangement(n, rng, blocks=[h1, h2])
                G2 = np.zeros((n, 2), np.float32)
                G2[h1, 0] = 1
                G2[h2, 1] = 1
                ders.append(kap(cells(FT, FP, Y, G2, donor=donor, start=st), 0, 1))
        r, d = np.array(reals), np.array(ders)
        ex = np.array([a - b for a in r for b in d])
        pts[frac] = dict(learners=n, per_half=n // 2, kappa=float(np.nanmean(r)), deranged=float(np.nanmean(d)),
                         excess=float(np.nanmean(r) - np.nanmean(d)),
                         excess_lo=float(np.nanpercentile(ex, 2.5)), excess_hi=float(np.nanpercentile(ex, 97.5)),
                         kappa_draws=r.tolist(), deranged_draws=d.tolist())
        p = pts[frac]
        print(f"   {frac:>5.0%} ({p['per_half']:,} per half): kappa {p['kappa']:+.3f}  deranged {p['deranged']:+.3f}  "
              f"EXCESS {p['excess']:+.3f} [{p['excess_lo']:+.3f}, {p['excess_hi']:+.3f}]", flush=True)

    target_file = Path(out or HERE / f"out/raise_kappa_curve_{corpus}.json")
    floor = None
    if corpus == "xes3g5m":
        k100 = pts[1.0]["kappa"]
        floor = dict(curve_100=k100, study_baseline=0.494, tol=rk.FLOOR_TOL,
                     passes=bool(abs(k100 - 0.494) <= rk.FLOOR_TOL))
        print(f"FLOOR: 100% kappa {k100:+.3f} vs this study's +0.494: {'PASSES' if floor['passes'] else 'FAILS'}")
        if not floor["passes"]:
            target_file.write_text(json.dumps(dict(floor=floor), indent=2) + "\n")
            raise SystemExit("floor failed; the curve is not read")

    f = lambda n, kmax, nh: kmax * n / (n + nh)
    xs = np.array([pts[q]["per_half"] for q in fracs], float)

    def fit(ys):
        try:
            (kmax, nh), _ = curve_fit(f, xs, ys, p0=(0.8, xs.mean()), bounds=([0, 1], [1.5, 1e8]), maxfev=20000)
            return kmax, nh
        except Exception:
            return float("nan"), float("nan")

    ys = np.array([pts[q]["excess"] for q in fracs])
    kmax, nh = fit(ys)
    drng = np.random.default_rng(1)
    fits = []
    for _ in range(500):
        yb = []
        for q in fracs:
            r = np.array(pts[q]["kappa_draws"])
            d = np.array(pts[q]["deranged_draws"])
            yb.append(np.nanmean(drng.choice(r, len(r))) - np.nanmean(drng.choice(d, len(d))))
        fits.append(fit(np.array(yb)))
    fits = np.array(fits)
    need = {}
    for target in (0.60, 0.70, 0.80):
        n_for = lambda km, h: h * target / (km - target) if km > target else float("inf")
        ns = np.array([n_for(km, h) for km, h in fits if np.isfinite(km)])
        lo, hi = np.percentile(ns, [2.5, 97.5]) if len(ns) else (float("nan"),) * 2
        need[str(target)] = dict(per_half=n_for(kmax, nh), lo=float(lo), hi=float(hi),
                                 unreachable=bool(np.nanpercentile(fits[:, 0], 97.5) < target))
    hi0 = pts[fracs[0]]["excess_hi"]
    lo1 = pts[fracs[-1]]["excess_lo"]
    rise = pts[fracs[-1]]["excess"] - pts[fracs[0]]["excess"]
    verdict = "SAMPLE IS THE CEILING" if (rise >= 0.05 and lo1 > hi0) else "FLAT"
    kci = [float(np.nanpercentile(fits[:, 0], 2.5)), float(np.nanpercentile(fits[:, 0], 97.5))]
    print(f"fit: k_max {kmax:+.3f} [{kci[0]:+.3f}, {kci[1]:+.3f}], n_half {nh:,.0f}; learners per half for excess "
          f"kappa 0.60 / 0.70 / 0.80: "
          + " / ".join(f"{v['per_half']:,.0f}" + (" (UNREACHABLE)" if v["unreachable"] else "") for v in need.values()))
    print(f"VERDICT ({corpus}): {verdict} -- excess rises {rise:+.3f} from {fracs[0]:.0%} to {fracs[-1]:.0%}")
    for p in pts.values():
        p.pop("kappa_draws")
        p.pop("deranged_draws")
    target_file.write_text(json.dumps(dict(
        corpus=corpus, items=items, min_cell=min_cell, base_z=rk.BASE_Z, bar=rk.BAR, learners=n_all, floor=floor,
        points={str(k): v for k, v in pts.items()}, fit=dict(k_max=kmax, n_half=nh, k_max_ci=kci),
        learners_per_half_needed=need, excess_rise=rise, verdict=verdict), indent=2, default=float) + "\n")
    print(f"wrote {target_file}")
