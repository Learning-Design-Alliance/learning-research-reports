"""EdNet AT ITS OWN BAR. The one reading `replicate.py` returned UNANSWERABLE rather than negative.

`replicate.py` found EdNet fails to replicate XES3G5M's conjunctive structure at the FIXED +0.10 bar,
with 60.2% power and a validated null -- a powered negative. But EdNet's own background is +0.0565,
0.53x XES3G5M's, so that bar asks EdNet for 1.8x its own background. Read at its OWN bar EdNet had
15.1% power, far under the 50% floor, and the correct output was UNANSWERABLE: UNKNOWN, not absence.

Power scales with sqrt(n), so that reading is a sample-size problem and nothing else. It is closed
here by using 7.5x the learners.

WHERE THE LEARNERS CAME FROM, AND THE SELECTION THAT IS NOW EXPLICIT. The whole EdNet KT1 archive was
already on disk; only 8,000 of its 784,309 learner files had been extracted. Those 8,000 were never a
uniform sample -- mean file size 38.8 KB against a corpus mean of 3.9 KB and a corpus MEDIAN of 390
bytes, so `replicate.py` ran on unusually active learners without saying so. The corpus median
learner has a handful of events and CANNOT enter a four-way cell at any sample size, so a uniform
draw would add rows and no power.

This extracts every learner file at or above 10 KB -- 60,308 learners, mean ~41 KB, the SAME activity
profile as the original 8,000 and 7.5x as many of them. That is selection on ANALYSABILITY rather
than on outcome, which is the same restriction positivity already imposes, but it is selection and it
bounds the claim: this is a result about ACTIVE EdNet learners, not about EdNet learners.

WHY THIS FILE EXISTS RATHER THAN A FLAG ON replicate.py. 60,308 learners is ~75M events, and
`positivity.timelines/states` hold every event as a Python tuple keyed per learner, which does not
fit. Everything the interaction needs is three numbers per learner per tag -- first-touch time,
outcome at that touch, first-pass time -- so the loader here produces three dense (learners x tags)
arrays in one streaming pass and never materialises the event log. Scoring, the derangement null,
the power curve, BH and the item block bootstrap are all IMPORTED from the files that already
validated them; nothing statistical is re-implemented.

ONE THING IS WEAKER THAN replicate.py AND IS NOT HIDDEN. The ability control there used every
attempt a learner made before reaching the dependant. Dense arrays carry first touches only, so
ability here is FIRST-ATTEMPT accuracy over the tags a learner had already touched, excluding a, b
and c. Same spirit, coarser instrument, and reported as such.

PRE-REGISTERED, and identical to replicate.py's so this cannot be read as a moved goalpost:

  UNANSWERABLE   the analytic null fails validation against the learner derangement, OR power at
                 the corpus's own bar is under 50% at its own real cell sizes. Still UNKNOWN.
  STRUCTURE      powered and validated, and the block-CI lower bound on the above-bar share clears
                 FDR_Q = 0.05.
  NO STRUCTURE   powered and validated, and it does not. Real negative evidence.

Reads EdNet. CC BY-NC 4.0 -- non-commercial, no model training; counting learners in cells is
neither. Raw exports stay in the session scratchpad; only aggregates are committed.

    python3 ednet_at_scale.py [--items 30] [--draws 1000] [--max-learners 0]
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "studies/identifiability/overlap"))

sys.path.insert(0, str(HERE.parents[2]))
from shared.corpus import KT1_RESTORED, ednet_questions, kt1_members  # noqa: E402
from positivity import SCRATCH  # noqa: E402
from shared.paths import data_path  # noqa: E402
from block_bootstrap import (FDR_Q, MIN_CELL, MIN_MEANINGFUL, _jsonable,  # noqa: E402
                             block_bootstrap, design_effect, jackknife, one_sided_p, pipeline,
                             score_item)
from replicate import MIN_POWER, NULL_BAND, STRATA, planted_power  # noqa: E402

SEED = 20260922
FLOOR_SHARE = FDR_Q


# ---------------------------------------------------------------- the dense loader

def load_dense(root: Path | None = None, max_learners: int = 0):
    """One streaming pass -> first-touch time, outcome at that touch, and first-pass time per tag.

    Returns FT, OAT, FP as (learners x tags) arrays. NaN means the learner never touched (FT) or
    never passed (FP) that tag. Nothing else about the event log is kept, which is what makes 60,308
    learners fit where `positivity.timelines` would not.

    `root` holds contents/ beside ../ednet-kt1.zip; without it, $EDNET_CONTENTS and $EDNET_ZIP.
    """
    if root is None:
        contents, zip_path = data_path("EDNET_CONTENTS"), data_path("EDNET_ZIP")
    else:
        contents, zip_path = root / "contents", root.parent / "ednet-kt1.zip"
    # leading tag per question, via the shared parse: the `-1` sentinel is not a KC, so its 797
    # questions are skipped (until 2026-09-24 they formed a unit "-1")
    answer, tagof = {}, {}
    for q, (key, tags) in ednet_questions(contents).items():
        if tags:
            answer[q] = key
            tagof[q] = tags[0]
    tags = sorted(set(tagof.values()))
    tix = {t: i for i, t in enumerate(tags)}
    # The zip, not the extracted directory: the learner set is the first KT1_RESTORED namelist
    # members, a function of the archive alone (shared/corpus.kt1_members; re-issued 2026-09-24).
    zf, files = kt1_members(zip_path, KT1_RESTORED)
    if max_learners and len(files) > max_learners:
        pick = np.random.default_rng(SEED).choice(len(files), max_learners, replace=False)
        files = [files[i] for i in sorted(pick)]

    n, m = len(files), len(tags)
    FT = np.full((n, m), np.nan)
    FP = np.full((n, m), np.nan)
    OAT = np.zeros((n, m), np.int8)
    for r, f in enumerate(files):
        # accumulate in plain dicts and write the row once: per-element numpy scalar assignment is
        # roughly two orders of magnitude slower, and this loop runs ~75M times
        ft, fp, oat = {}, {}, {}
        with io.TextIOWrapper(zf.open(f), encoding="utf-8", errors="replace") as fh:
            next(fh, None)
            for line in fh:
                col = line.split(",")
                if len(col) < 4:
                    continue
                t = tagof.get(col[2])
                if t is None:
                    continue
                j = tix[t]
                ts = float(col[0])
                ok = col[3] == answer[col[2]]
                if j not in ft or ts < ft[j]:
                    ft[j] = ts
                    oat[j] = ok
                if ok and (j not in fp or ts < fp[j]):
                    fp[j] = ts
        if ft:
            k = list(ft)
            FT[r, k] = [ft[i] for i in k]
            OAT[r, k] = [oat[i] for i in k]
        if fp:
            k = list(fp)
            FP[r, k] = [fp[i] for i in k]
        if (r + 1) % 10000 == 0:
            print(f"    {r+1:,}/{n:,} learners", flush=True)
    return FT, OAT, FP, tags


def background(FT, OAT, FP, cols, min_cell=MIN_CELL):
    """Median STRICT pairwise drop -- the number the fixed +0.10 bar is, measured on this corpus.

    Same cells as studies/identifiability/overlap/positivity.py: `mastered` passed A before first touching B, `failed`
    touched A before B and had not passed it. Learners who never touched A are excluded, because
    "never offered" is selection rather than evidence.
    """
    drops = []
    for a in cols:
        for b in cols:
            if a == b:
                continue
            at_b = np.isfinite(FT[:, b])
            passed_a = FP[:, a] < FT[:, b]
            touched_a = FT[:, a] < FT[:, b]
            mast = at_b & passed_a
            fail = at_b & touched_a & ~passed_a
            if mast.sum() < min_cell or fail.sum() < min_cell:
                continue
            drops.append(float(OAT[mast, b].mean() - OAT[fail, b].mean()))
    return (float(np.median(drops)), len(drops)) if drops else (None, 0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", type=int, default=30)
    ap.add_argument("--draws", type=int, default=1000)
    ap.add_argument("--max-learners", type=int, default=0)
    ap.add_argument("--null-items", type=int, default=4)
    ap.add_argument("--null-draws", type=int, default=150)
    ap.add_argument("--out", default="out/ednet_at_scale.json")
    args = ap.parse_args()
    rng = np.random.default_rng(SEED)

    print("loading EdNet KT1 (dense, one pass)", flush=True)
    FT, OAT, FP, tags = load_dense(SCRATCH / "ednet", args.max_learners)
    cover = np.isfinite(FT).sum(0)
    order = np.argsort(-cover)[:args.items]
    items = [tags[i] for i in order]
    print(f"\nednet: {FT.shape[0]:,} learners, {len(tags)} tags, top {len(items)} used "
          f"(coverage {cover[order].max():,} down to {cover[order].min():,}), "
          f"cell floor {MIN_CELL}, FDR q={FDR_Q}", flush=True)

    bar, npairs = background(FT, OAT, FP, list(order))
    print(f"  CORPUS BACKGROUND: {bar:+.4f} over {npairs:,} readable ordered pairs "
          f"(replicate.py got {0.0565:+.4f} on 8,000 learners)", flush=True)

    parts, checks = [], []
    for jj, ci in enumerate(order):
        sel = np.isfinite(FT[:, ci])
        ok = OAT[sel, ci].astype(float)
        tc = FT[sel, ci][:, None]
        pcols = [c for c in order if c != ci]
        H = FP[np.ix_(sel, pcols)] < tc
        got = score_item(ok, H, [tags[c] for c in pcols], tags[ci])
        if got is None:
            continue
        got["base_arr"] = np.full(len(got["z"]), float(got["base"]))
        parts.append(got)
        if jj < args.null_items:
            real = got["interaction"]
            keyed = {(str(a), str(b)): i for i, (a, b) in enumerate(zip(got["a"], got["b"]))}
            acc = [[] for _ in keyed]
            for _ in range(args.null_draws):
                d = rng.permutation(len(ok))
                fx = np.flatnonzero(d == np.arange(len(ok)))
                if len(fx) > 1:
                    d[fx] = d[np.roll(fx, 1)]
                g2 = score_item(ok, H[d], [tags[c] for c in pcols], tags[ci])
                if g2 is None:
                    continue
                for a, b, v in zip(g2["a"], g2["b"], g2["interaction"]):
                    k = keyed.get((str(a), str(b)))
                    if k is not None:
                        acc[k].append(v)
            for i, vals in enumerate(acc):
                if len(vals) >= args.null_draws // 3:
                    checks.append((np.std(vals, ddof=1), got["se"][i], np.mean(vals)))
        print(f"   {tags[ci]}: {sum(len(g['z']) for g in parts):,} readable", flush=True)

    z = np.concatenate([g["z"] for g in parts])
    inter = np.concatenate([g["interaction"] for g in parts])
    base = np.concatenate([g["base_arr"] for g in parts])
    ncell = np.concatenate([g["ncell"] for g in parts])
    pos = {t: i for i, t in enumerate(items)}
    tri = np.stack([np.concatenate([[pos[x] for x in g[k]] for g in parts])
                    for k in ("c", "a", "b")], 1)
    T = len(z)
    pv = one_sided_p(z)

    sd = np.array([c[0] for c in checks]); se = np.array([c[1] for c in checks])
    ratio = float(np.median(sd / se))
    null_ok = bool(NULL_BAND[0] <= ratio <= NULL_BAND[1])
    print(f"\n  NULL VALIDATION: deranged SD / analytic SE = {ratio:.3f} over {len(sd):,} triples, "
          f"deranged mean interaction {np.median([c[2] for c in checks]):+.5f} "
          f"-> {'accepted' if null_ok else 'ANALYTIC NULL REJECTED'}")

    print(f"  POWER AT THE REAL CELL SIZES ({T:,} triples, outcomes simulated):")
    power = planted_power(ncell, base, (round(bar, 4), MIN_MEANINGFUL, 0.20), rng)
    for s, v in power.items():
        print(f"    planted {s:+.4f}: detectable {100*v['rate']:.1f}%")
    p_own = power[round(bar, 4)]["rate"]
    powered = bool(p_own >= MIN_POWER)
    print(f"  -> power at its own bar {100*p_own:.1f}% against a {100*MIN_POWER:.0f}% floor "
          f"(replicate.py had 15.1% on 8,000 learners)")

    out = dict(corpus="ednet-at-scale", learners=int(FT.shape[0]), items=len(items), n_triples=T,
               background=bar, background_pairs=npairs, null_ratio=ratio, null_accepted=null_ok,
               power=power, power_at_own_bar=p_own, powered=powered)
    if not (null_ok and powered):
        print(f"\nVERDICT: UNANSWERABLE -- still UNKNOWN, not absence.")
        out["verdict"] = "UNANSWERABLE"
    else:
        # BOTH bars, because the question this file exists to settle needs both. replicate.py's
        # negative was at the FIXED +0.10 with 60.2% power on 8,000 learners; at 60,308 that bar is
        # at 100% power, so reading it again says whether that negative was the BAR or the POWER.
        for label, b in (("own", bar), ("fixed", MIN_MEANINGFUL)):
            pt = pipeline(pv, inter, bar=b)
            boot = block_bootstrap(items, tri, pv, inter, rng, args.draws, bar=b)
            d, vals = design_effect(boot, pt["above_share"], key="above_share", n=T)
            lo, hi = np.percentile(vals, [2.5, 97.5])
            cnt = np.array([x["above"] for x in boot], float)
            print(f"\n  BAR = {label.upper()} ({b:+.4f}): SUPPORTED {pt['supported']:,} "
                  f"({100*pt['share']:.1f}%), above bar {pt['above']:,} "
                  f"({100*pt['above_share']:.1f}%)")
            print(f"    block CI on the above-bar share [{lo:.3f}, {hi:.3f}], design effect "
                  f"{d:.1f}, effective independent triples {T/d:.0f}, count CI "
                  f"[{np.percentile(cnt,2.5):,.0f}, {np.percentile(cnt,97.5):,.0f}]")
            out[f"read_{label}"] = dict(bar=b, supported=pt["supported"], above=pt["above"],
                                        share=pt["share"], above_share=pt["above_share"],
                                        lo=float(lo), hi=float(hi), design_effect=d,
                                        n_eff=float(T / d),
                                        count_ci=[float(np.percentile(cnt, 2.5)),
                                                  float(np.percentile(cnt, 97.5))])
        jk = jackknife(items, tri, pv, inter, bar=bar)
        worst = min(jk, key=lambda r: r["above"])
        lost = 1 - worst["above"] / max(out["read_own"]["above"], 1)
        print(f"  leave-one-item-out at the own bar: worst single item ({worst['dropped']}) "
              f"costs {100*lost:.1f}%")
        out["jackknife_worst"] = dict(item=str(worst["dropped"]), cost=float(lost))
        lo_own = out["read_own"]["lo"]
        out["verdict"] = "STRUCTURE" if lo_own > FLOOR_SHARE else "NO STRUCTURE"
        print(f"\nVERDICT (at its own bar): {out['verdict']}")
        print(f"  EdNet is now powered at its own bar ({100*p_own:.0f}%, against 15.1% on 8,000 "
              f"learners) with a null validating at {ratio:.3f}. Its above-bar share is "
              f"{out['read_own']['above_share']:.3f} [{lo_own:.3f}, {out['read_own']['hi']:.3f}], "
              f"which {'clears' if lo_own > FLOOR_SHARE else 'does not clear'} the "
              f"{FLOOR_SHARE:.2f} the false-discovery allowance occupies.")
        print(f"  READ THE FIXED BAR BESIDE IT: {out['read_fixed']['above_share']:.3f} "
              f"[{out['read_fixed']['lo']:.3f}, {out['read_fixed']['hi']:.3f}] at "
              f"{100*power[float(MIN_MEANINGFUL)]['rate']:.0f}% power, against replicate.py's "
              f"0.005 [0.000, 0.021] at 60.2% power on 8,000 learners.")

    o = Path(args.out)
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(out, indent=2, default=_jsonable) + "\n")
    print(f"wrote {o}")


if __name__ == "__main__":
    main()
