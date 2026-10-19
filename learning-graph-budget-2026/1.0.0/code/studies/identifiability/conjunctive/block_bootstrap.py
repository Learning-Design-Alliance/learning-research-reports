"""Stage 3's FDR treated 11,203 triples as independent. They are 30 items. Re-run it blocked.

`studies/identifiability/sparse-signal/empirical_null.py` fitted Efron's empirical null to stage 3's z-scores and got
N(+0.038, 2.753) -- a null nearly three times too wide, which at face value would erase most of the
2,425 SUPPORTED. That reading cannot be taken at face value, because stage 3's standard error was
NOT unchecked: it was validated per-triple against an explicit learner derangement at a ratio of
0.997. An SE that is right for one test and a cross-test spread of 2.75 are not in conflict. They
are the two halves of the same fact: THE TESTS ARE NOT INDEPENDENT.

11,203 triples were built from 30 items. Every triple is a (dependant, parent, parent) draw from
that set, so each item appears in roughly 2,240 of them, and two triples sharing an item share
learners, share that item's base rate and share whatever real structure the item carries. Widening
every SE to 2.75x, as an empirical null does, pays for that correlation by destroying the one thing
that was measured correctly. The right correction resamples the unit the dependence lives in.

THE UNIT IS THE ITEM. This is the same rule the rest of the programme follows for permutation --
"permute the unit the treatment was assigned to" -- applied to resampling instead. A triple is a
3-way draw from the item set, so the multiway cluster bootstrap weights each triple by the PRODUCT
of its three items' draw counts (Davezies/D'Haultfoeuille/Guyonvarch; the pigeonhole bootstrap).
An item drawn twice doubles the weight of every triple it appears in, and an item not drawn at all
removes its ~2,240 triples entirely.

WHAT IS RESAMPLED AND WHAT IS NOT. The learner-level evidence inside a triple is left alone: its
interaction, its SE and its z are stage 3's, recomputed here and checked against stage 3's own saved
rows. Only the SET OF TRIPLES is resampled, and the WHOLE pipeline -- Benjamini-Hochberg included --
is re-run inside each replicate, because it is the pipeline's output that is being given an interval,
not its input.

THE FLOOR, and it is the reason this file has two synthetic worlds. A bootstrap always returns an
interval; that is not evidence it found anything. Two 30-item, 11,203-triple worlds are built with
the SAME triple geometry and a planted signal of the same size, differing only in where the signal
is attached:

    UNCLUSTERED  the non-null triples are chosen at random across triples
    CLUSTERED    the non-null triples are exactly those touching a few planted items

If the item bootstrap cannot separate those two, its design effect on the real data means nothing.
The unclustered world also supplies the reference the real design effect has to beat: a 3-way
product bootstrap over 30 clusters has variance above the iid value even with no correlation at all,
so "design effect > 1" is not by itself a finding.

PRE-REGISTERED, before the run:

  bar                 the claim under test is stage 3's headline, 1,212 triples (10.8%) SUPPORTED
                      and at or above the pre-registered +0.10. Its share is what gets an interval.
  INFLATED            the bootstrap 2.5th percentile of the above-bar share falls below FDR_Q=0.05.
                      Stage 3's count did not survive being told how many items it came from.
  CONCENTRATED        the interval clears 0.05, but dropping a single item (leave-one-item-out)
                      costs more than half the above-bar triples. Real, and it is one item's claim.
  SURVIVES            the interval clears 0.05 and no single item carries more than half.

Reads XES3G5M. Raw exports stay in the session scratchpad; only aggregates are committed.

    python3 block_bootstrap.py [--items 30] [--draws 1000]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.special import erfc

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "studies/identifiability/overlap"))

from atlas import xes3g5m_rows  # noqa: E402
from positivity import SCRATCH, at_item, states, timelines  # noqa: E402
from stage3_interaction import FDR_Q, MIN_CELL, MIN_MEANINGFUL, bh  # noqa: E402

SEED = 20260922
#: the share a claim has to clear to be more than the false-discovery allowance itself
FLOOR_SHARE = FDR_Q
#: how large a planted signal the floor worlds carry, and over how many items when clustered
PLANT_SHARE, PLANT_SHIFT, PLANT_ITEMS = 0.11, 3.0, 4


# ---------------------------------------------------------------- scoring, vectorised over pairs

def score_item(ok, H, items, c):
    """Every (c, a, b) interaction for one dependant at once.

    The four cell counts of every parent pair come out of two 29x29 products rather than 406 passes
    over the learner array: H'H is the "held both" count and (H*ok)'H the successes inside it.
    Everything else is a margin minus that. Same arithmetic as stage3_interaction.score(), checked
    against its saved rows in main().
    """
    n = len(ok)
    Hf = H.astype(np.float64)
    n_both = Hf.T @ Hf
    s_both = (Hf * ok[:, None]).T @ Hf
    n_a = Hf.sum(0)
    s_a = ok @ Hf
    S = float(ok.sum())
    p = S / n
    ia, ib = np.triu_indices(len(items), k=1)

    n1 = n_both[ia, ib]
    n2 = n_a[ia] - n1
    n3 = n_a[ib] - n1
    n4 = n - n_a[ia] - n_a[ib] + n1
    s1 = s_both[ia, ib]
    s2 = s_a[ia] - s1
    s3 = s_a[ib] - s1
    s4 = S - s_a[ia] - s_a[ib] + s1

    ns = np.stack([n1, n2, n3, n4])
    keep = ns.min(0) >= MIN_CELL
    if not keep.any():
        return None
    ns = ns[:, keep]
    ms = np.stack([s1, s2, s3, s4])[:, keep] / ns
    inter = (ms[0] - ms[1]) - (ms[2] - ms[3])
    se = np.sqrt(p * (1 - p) * (1.0 / ns).sum(0))
    good = np.isfinite(se) & (se > 0)
    return dict(c=np.full(good.sum(), c), a=np.asarray(items)[ia[keep][good]],
                b=np.asarray(items)[ib[keep][good]], interaction=inter[good], se=se[good],
                z=(inter / se)[good], n_min=ns.min(0)[good], ncell=ns[:, good].T, base=p)


# ---------------------------------------------------------------- the pipeline being bootstrapped

def one_sided_p(z):
    """Upper-tail normal p, vectorised. Computed once: resampling repeats triples, it does not
    change any triple's evidence."""
    return 0.5 * erfc(np.asarray(z, float) / np.sqrt(2.0))


def pipeline(p, inter, weight=None, bar=MIN_MEANINGFUL):
    """Stage 3's verdicts, end to end, on whatever set of triples it is handed.

    `weight` repeats a triple that many times, which is how the multiway cluster bootstrap makes an
    item drawn twice count twice. BH is re-run on the expanded set, not inherited: the correction is
    part of what is being given an interval.
    """
    if weight is not None:
        idx = np.repeat(np.arange(len(p)), weight)
        p, inter = p[idx], inter[idx]
    if not len(p):
        return dict(n=0, supported=0, above=0, share=float("nan"), above_share=float("nan"),
                    median_supported=float("nan"))
    keep = bh(p, FDR_Q)
    sup = keep & (inter > 0)
    above = sup & (inter >= bar)
    return dict(n=int(len(p)), supported=int(sup.sum()), above=int(above.sum()),
                share=float(sup.mean()), above_share=float(above.mean()),
                median_supported=float(np.median(inter[sup])) if sup.any() else float("nan"))


def block_bootstrap(items, tri_items, p, inter, rng, draws, bar=MIN_MEANINGFUL):
    """Resample ITEMS with replacement; a triple's weight is the product of its three items' counts.

    tri_items is (T, 3) of item indices. Drawing an item twice doubles the weight of every triple it
    sits in; not drawing it removes them. That is the dependence structure, resampled directly,
    rather than an SE widened until it covers it.
    """
    k = len(items)
    out = []
    for _ in range(draws):
        mult = np.bincount(rng.integers(0, k, k), minlength=k)
        w = mult[tri_items[:, 0]] * mult[tri_items[:, 1]] * mult[tri_items[:, 2]]
        out.append(pipeline(p, inter, weight=w, bar=bar))
    return out


def jackknife(items, tri_items, p, inter, bar=MIN_MEANINGFUL):
    """Drop one item and everything it touches. The concentration test A14 made necessary."""
    out = []
    for i in range(len(items)):
        keep = (tri_items != i).all(1)
        r = pipeline(p[keep], inter[keep], bar=bar)
        r["dropped"] = items[i]
        r["n_triples_dropped"] = int((~keep).sum())
        out.append(r)
    return out


# ---------------------------------------------------------------- the floor: two synthetic worlds

def synth_world(tri_items, k, clustered, rng):
    """Same triple geometry, same amount of planted signal, attached differently.

    UNCLUSTERED puts the shift on randomly chosen triples; CLUSTERED puts it on every triple touching
    a few chosen items. Both carry the same expected number of non-null triples, so any difference
    the bootstrap reports is about WHERE the signal sits, not how much there is.
    """
    t = len(tri_items)
    z = rng.standard_normal(t)
    if clustered:
        hot = rng.choice(k, PLANT_ITEMS, replace=False)
        nz = np.isin(tri_items, hot).any(1)
        # match the unclustered world's count so the two differ only in arrangement
        idx = np.flatnonzero(nz)
        want = int(round(PLANT_SHARE * t))
        if len(idx) > want:
            idx = rng.choice(idx, want, replace=False)
        nz = np.zeros(t, bool)
        nz[idx] = True
    else:
        nz = np.zeros(t, bool)
        nz[rng.choice(t, int(round(PLANT_SHARE * t)), replace=False)] = True
    z = z + nz * PLANT_SHIFT
    se = np.full(t, 0.05)
    return one_sided_p(z), z * se


def _jsonable(o):
    """numpy scalars do not serialise; every number here is a plain float or bool underneath."""
    if isinstance(o, (np.bool_, bool)):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(f"not serialisable: {type(o).__name__}")


def design_effect(boot, point, key="above_share", n=None):
    """bootstrap variance over the variance an independent binomial of the same size would have."""
    vals = np.array([b[key] for b in boot], float)
    vals = vals[np.isfinite(vals)]
    if len(vals) < 2 or n is None or not np.isfinite(point) or point <= 0 or point >= 1:
        return float("nan"), vals
    return float(vals.var(ddof=1) / (point * (1 - point) / n)), vals


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", type=int, default=30)
    ap.add_argument("--draws", type=int, default=1000)
    ap.add_argument("--out", default="out/block_bootstrap.json")
    args = ap.parse_args()
    rng = np.random.default_rng(SEED)

    rows_raw = list(xes3g5m_rows(SCRATCH / "xes3g5m"))
    by_learner = timelines(rows_raw)
    ft, fp, oat = states(by_learner)
    idx = at_item(ft, oat)
    items = sorted(idx, key=lambda i: -len(idx[i]))[:args.items]
    pos = {it: i for i, it in enumerate(items)}
    print(f"xes3g5m: {len(by_learner):,} learners, {len(items)} items, cell floor {MIN_CELL}, "
          f"FDR q={FDR_Q}, bar {MIN_MEANINGFUL:+.2f}\n", flush=True)

    parts = []
    for c in items:
        at_c = idx[c]
        learners = [l for l, _t, _y in at_c]
        tc = np.array([t for _l, t, _y in at_c])
        ok = np.array([float(y) for _l, _t, y in at_c])
        parents = [p for p in items if p != c]
        H = np.zeros((len(at_c), len(parents)), bool)
        for j, p in enumerate(parents):
            for k, l in enumerate(learners):
                pp = fp[l].get(p)
                if pp is not None and pp < tc[k]:
                    H[k, j] = True
        got = score_item(ok, H, parents, c)
        if got:
            parts.append(got)
        print(f"   {c}: {sum(len(g['z']) for g in parts):,} readable", flush=True)

    z = np.concatenate([g["z"] for g in parts])
    inter = np.concatenate([g["interaction"] for g in parts])
    se = np.concatenate([g["se"] for g in parts])
    tri_items = np.stack([np.concatenate([[pos[x] for x in g[k]] for g in parts])
                          for k in ("c", "a", "b")], 1)
    T = len(z)

    # --- 0. does this reproduce stage 3? if not, nothing below is about stage 3
    pvals = one_sided_p(z)
    point = pipeline(pvals, inter)
    ref = json.loads((HERE / "out/stage3.json").read_text())
    key = {(r["c"], r["a"], r["b"]): r for r in ref["rows"]}
    mine = {(str(cc), str(aa), str(bb)): i for i, (cc, aa, bb) in
            enumerate(zip(np.concatenate([g["c"] for g in parts]),
                          np.concatenate([g["a"] for g in parts]),
                          np.concatenate([g["b"] for g in parts])))}
    diffs = [abs(inter[mine[k]] - v["interaction"]) for k, v in key.items() if k in mine]
    print(f"\nREPRODUCTION CHECK against stage3.json: {T:,} triples here vs {ref['n_scored']:,} "
          f"there; {len(diffs)} of {len(key)} saved rows matched, "
          f"max |interaction difference| {max(diffs) if diffs else float('nan'):.2e}")
    agrees = bool(T == ref["n_scored"] and diffs and max(diffs) < 1e-9)
    print(f"  SUPPORTED {point['supported']:,} vs {ref['tally']['SUPPORTED']:,}; "
          f"above bar {point['above']:,} vs {ref['supported_above_bar']:,} "
          f"-> {'reproduced' if agrees else 'DOES NOT REPRODUCE'}")
    if not agrees:
        print("  refusing to report a corrected count for a pipeline that is not stage 3's.")
        return

    # --- 1. the floor, before any real interval is read
    print(f"\nFLOOR -- the same {T:,} triples over {len(items)} items, "
          f"{PLANT_SHARE:.0%} non-null at z+{PLANT_SHIFT:.1f}, placed two ways "
          f"({args.draws // 4} bootstrap draws each, 6 repetitions):")
    floor = {}
    for name, clustered in (("unclustered", False), ("clustered", True)):
        des = []
        for _ in range(6):
            pp, ii = synth_world(tri_items, len(items), clustered, rng)
            pt = pipeline(pp, ii)
            bo = block_bootstrap(items, tri_items, pp, ii, rng, args.draws // 4)
            d, _ = design_effect(bo, pt["above_share"], n=T)
            des.append(d)
        floor[name] = dict(design_effect_median=float(np.median(des)),
                           design_effect_hi=float(np.max(des)), reps=[float(x) for x in des])
        print(f"  {name:<12} design effect median {np.median(des):6.1f}  "
              f"(max over reps {np.max(des):6.1f})")
    sep = floor["clustered"]["design_effect_median"] > floor["unclustered"]["design_effect_hi"]
    print(f"  -> the item bootstrap {'SEPARATES' if sep else 'DOES NOT SEPARATE'} the two worlds; "
          f"the unclustered world's worst design effect, {floor['unclustered']['design_effect_hi']:.1f}, "
          f"is the reference the real data has to beat")
    if not sep:
        print("  an instrument that cannot tell clustered signal from scattered signal cannot be "
              "used to say stage 3's count was item-driven. Stopping.")
        return

    # --- 2. the real interval
    print(f"\nBLOCK BOOTSTRAP over {len(items)} items, {args.draws:,} draws "
          f"(triple weight = product of its three items' draw counts):")
    boot = block_bootstrap(items, tri_items, pvals, inter, rng, args.draws)
    res = {}
    for k, label in (("share", "SUPPORTED share"), ("above_share", "above-bar share")):
        d, vals = design_effect(boot, point[k], key=k, n=T)
        lo, hi = np.percentile(vals, [2.5, 97.5])
        res[k] = dict(point=point[k], lo=float(lo), hi=float(hi), design_effect=d,
                      n_eff=float(T / d) if np.isfinite(d) and d > 0 else float("nan"))
        print(f"  {label:<18} point {point[k]:.3f}   95% block CI [{lo:.3f}, {hi:.3f}]   "
              f"design effect {d:6.1f}   effective independent triples {T/d:8.0f}")
    counts = np.array([b["above"] for b in boot], float)
    print(f"  above-bar COUNT: point {point['above']:,}, block CI "
          f"[{np.percentile(counts, 2.5):,.0f}, {np.percentile(counts, 97.5):,.0f}] "
          f"(replicate sets average {np.mean([b['n'] for b in boot]):,.0f} triples)")

    # --- 3. is one item carrying it?
    jk = jackknife(items, tri_items, pvals, inter)
    worst = min(jk, key=lambda r: r["above"])
    lost = 1 - worst["above"] / max(point["above"], 1)
    print(f"\nLEAVE ONE ITEM OUT ({len(items)} items):")
    for r in sorted(jk, key=lambda r: r["above"])[:3]:
        print(f"  drop {r['dropped']:<6} -> above-bar {r['above']:,} "
              f"({100*(1 - r['above']/max(point['above'],1)):+.1f}% vs {point['above']:,}), "
              f"{r['n_triples_dropped']:,} triples removed")
    print(f"  worst single item costs {100*lost:.1f}% of the above-bar triples")

    verdict = ("INFLATED" if res["above_share"]["lo"] < FLOOR_SHARE else
               "CONCENTRATED" if lost > 0.5 else "SURVIVES")
    print(f"\nVERDICT: {verdict}")
    if verdict == "INFLATED":
        print(f"  stage 3's {point['above']:,} above-bar triples are not {point['above']:,} pieces "
              f"of evidence. Blocked on the {len(items)} items they came from, the share can fall "
              f"to {res['above_share']['lo']:.3f}, below the {FLOOR_SHARE:.2f} the false-discovery "
              f"allowance itself occupies. The conjunctive reading stands or falls on which items "
              f"were drawn, and 30 is too few to say which.")
    elif verdict == "CONCENTRATED":
        print(f"  the structure is real under blocking but {worst['dropped']} carries "
              f"{100*lost:.0f}% of it -- the same shape A14 found, where 2 of 38 tasks held the "
              f"whole excess. A finding about one item, not about the corpus.")
    else:
        print(f"  the share survives resampling the items it was measured on, and no single item "
              f"carries more than half. The effective number of independent triples is "
              f"{res['above_share']['n_eff']:,.0f}, not {T:,} -- the claim is the same, its "
              f"precision is not.")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(
        seed=SEED, items=len(items), draws=args.draws, n_triples=T, fdr_q=FDR_Q,
        min_meaningful=MIN_MEANINGFUL, floor_share=FLOOR_SHARE, verdict=verdict,
        reproduced_stage3=agrees, point=point, floor=floor, floor_separates=bool(sep),
        bootstrap=res,
        above_count_ci=[float(np.percentile(counts, 2.5)), float(np.percentile(counts, 97.5))],
        jackknife=[{k: v for k, v in r.items()} for r in jk],
        worst_item=worst["dropped"], worst_item_cost=float(lost)),
        indent=2, default=_jsonable) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
