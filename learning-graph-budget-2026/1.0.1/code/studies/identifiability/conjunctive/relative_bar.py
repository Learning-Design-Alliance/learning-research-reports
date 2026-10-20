"""SETTLING THE BAR. Relative to each corpus's own background -- and the decision rule was wrong too.

`ednet_at_scale.py` left one question live: should an assertable effect be defined ABSOLUTELY or
RELATIVE to the corpus it is measured in? The programme's bar has been +0.10 throughout, and the
argument for going relative is stronger than it first looks: **+0.10 was never a constant.** It was
defined as "the background drop an arbitrary ordered pair already shows", which is XES3G5M's
background (+0.1073), hard-coded. EdNet's is +0.0491. Applying XES3G5M's number to EdNet asks it for
2x its own background, so the fixed bar is a XES3G5M-shaped ruler and always was. Going relative is
not a new rule; it is the original rule applied per corpus.

THE FAILURE MODE THAT DECIDES WHETHER IT IS SOUND, and it is measured here rather than assumed.
`stage1_floor.py` showed a conjunctive gate reads +0.083 PAIRWISE -- conjunctions CONTRIBUTE to the
pairwise drop that defines the background. So a corpus with more conjunctions gets a higher
background, hence a higher bar, hence fewer above-bar conjunctions. **A relative bar may be partly
self-cancelling against the very thing it measures.** Floor test (b) below plants conjunctions and
measures whether the background moves.

A SECOND DEFECT, IN THE DECISION RULE RATHER THAN THE BAR. Every verdict so far has asked whether the
above-bar SHARE exceeds FDR_Q = 0.05, on the reasoning that it must beat "the false-discovery
allowance". That reasoning is wrong. Benjamini-Hochberg at q = 0.05 bounds the false discovery
proportion AMONG REJECTIONS; under a global null it rejects approximately NOTHING, not 5% of tests.
Requiring share > 0.05 is an arbitrary and badly over-strict threshold, and it is why
`ednet_at_scale.py` returned NO STRUCTURE for a share of 0.078 -- and why XES3G5M READ AT ITS OWN
COARSE GRAIN fails the same rule (0.048). A rule that rejects the corpus the finding came from is not
measuring what it claims to.

The replacement is this programme's own idiom: compare against a MATCHED NULL, not a convention. The
WHOLE PIPELINE -- scoring, BH, the bar -- is re-run on learner-deranged data, and the observed
above-bar share must beat that null's 97.5th percentile. The derangement is the same control stage 3
validated its standard error against (a learner keeps their outcome and inherits another learner's
parent-state, no fixed points).

THREE SCOPES, because `studies/identifiability/assay-generality/local_background.py` already showed the background is local
WITHIN a corpus (52 XES3G5M families, +0.0517 to +0.1433) and `ednet_at_scale.py` showed it is local
BETWEEN corpora:

    global   the fixed +0.10. XES3G5M's background, applied everywhere.
    corpus   this corpus's own median ordered-pair drop. THE DECISION BEING SETTLED.
    family   the dependant's own source-family background. The fully consistent version, available
             only where a taxonomy exists -- XES3G5M has one, EdNet's 142 numeric tags do not, and
             that asymmetry is itself a finding about what a relative bar costs.

PRE-REGISTERED, before the run:

  the floor gates everything. Two tests, and if either fails the scope is not adopted:
    (a) SCALE INVARIANCE   a synthetic corpus and the SAME corpus with every effect multiplied by s
                           must return the same above-bar share under the relative bar, and must NOT
                           under the fixed bar. That is the whole claim for going relative, stated as
                           something that can fail.
    (b) SELF-CANCELLATION  planting conjunctions must not materially move the measured background.
                           Pre-registered tolerance: the background may rise by at most 20% OF THE
                           PLANTED CONJUNCTION'S SIZE. Beyond that the bar is eating its own signal
                           and the relative scope is reported as CONTAMINATED.

                           A DISCREPANCY BETWEEN THIS TEXT AND THE FIRST IMPLEMENTATION, RESOLVED IN
                           FAVOUR OF THIS TEXT AND REPORTED EITHER WAY. The first version computed
                           the shift as a fraction of the BACKGROUND rather than of the conjunction,
                           which is a different quantity and gave the opposite verdict on the same
                           numbers (31.2% "contaminated" against 4.0% "clean"). The text above was
                           written before any run and the code did not match it, so the code was
                           wrong; but choosing after seeing both numbers is exactly the move this
                           programme exists to avoid, so BOTH are reported and a THIRD, decisive
                           measure is added: the share cost -- how many above-bar triples are lost
                           by using the inflated background as the bar instead of the clean one.
                           That is the self-cancellation expressed in the only units that matter.

  then, per arm and scope:
    STRUCTURE      the above-bar share beats the deranged pipeline null's 97.5th percentile.
    NO STRUCTURE   it does not, and power at the bar is at least 50%. Real negative evidence.
    UNANSWERABLE   power at the bar is under 50%, or the analytic null fails validation. UNKNOWN.

Reads XES3G5M and EdNet. EdNet is CC BY-NC 4.0 -- non-commercial, no model training. Raw exports stay
in the session scratchpad; only aggregates are committed.

    python3 relative_bar.py --arm xes3g5m [--draws 1000] [--null-reps 200]
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "studies/identifiability/overlap"))

from atlas import xes3g5m_rows  # noqa: E402
from positivity import at_item, classify, states, timelines  # noqa: E402
from block_bootstrap import (FDR_Q, MIN_CELL, MIN_MEANINGFUL, _jsonable,  # noqa: E402
                             bh, block_bootstrap, design_effect, one_sided_p, pipeline, score_item)
from replicate import MIN_POWER, NULL_BAND, coarsen, planted_power  # noqa: E402
from ednet_at_scale import load_dense  # noqa: E402

sys.path.insert(0, str(HERE.parents[2]))
from shared.paths import data_path  # noqa: E402

SEED = 20260922
#: the background may rise by at most this fraction of a planted conjunction before the relative
#: scope is called CONTAMINATED -- the bar eating the signal it is supposed to measure
SELF_CANCEL_TOL = 0.20
#: GENERATOR SETTINGS, CALIBRATED AGAINST TARGETS FIXED BEFORE ANY FLOOR RESULT WAS READ, because
#: the floor's answer moved when the generator moved and that makes the generator the experiment.
#: The two targets are the real corpora's own numbers: a background in +0.05..+0.11 (XES3G5M +0.1073,
#: EdNet +0.0491) and an above-bar share in 0.05..0.11 (XES3G5M 0.108 fine / 0.048 coarse, EdNet
#: 0.078). A sweep over n_conj x conj picked the setting closest to both: background +0.0939, share
#: 0.0428. n_conj=60 gave a share of 0.008 (nothing to measure) and n_conj=400 tripled the background
#: (the conjunctions BECAME the background), and both of those are worlds we do not have.
BG, CONJ, N_CONJ = 0.085, 0.20, 250
#: how much larger the second world's effects are in the scale-invariance test. 1.8x is chosen to
#: bracket the real gap: XES3G5M's background is 2.2x EdNet's.
SCALE = 1.8
#: the relative bar is k x the scope's background. k = 1 reproduces the original definition of
#: +0.10 ("the drop an arbitrary ordered pair already shows"), which is why it is not a free knob.
BAR_K = 1.0


def derange(n, rng):
    d = rng.permutation(n)
    fx = np.flatnonzero(d == np.arange(n))
    if len(fx) > 1:
        d[fx] = d[np.roll(fx, 1)]
    return d


# ---------------------------------------------------------------- the pipeline null

def pipeline_null(dep, items, bar, rng, reps):
    """The whole pipeline -- scoring, BH, the bar -- re-run on deranged learners.

    This replaces `share > FDR_Q` as the decision rule. BH at q bounds the false discovery proportion
    AMONG REJECTIONS; under a global null it rejects almost nothing, so 0.05 was never the right
    reference. What the observed share has to beat is what THIS pipeline produces on data with the
    parent-outcome association destroyed, which is what a derangement destroys and nothing else.
    """
    shares, sups = [], []
    for _ in range(reps):
        inter, z = [], []
        for ok, H, pnames, c in dep:
            got = score_item(ok, H[derange(len(ok), rng)], pnames, c)
            if got is None:
                continue
            inter.append(got["interaction"])
            z.append(got["z"])
        if not inter:
            continue
        inter = np.concatenate(inter)
        pv = one_sided_p(np.concatenate(z))
        keep = bh(pv, FDR_Q)
        sup = keep & (inter > 0)
        shares.append(float((sup & (inter >= bar)).mean()))
        sups.append(float(sup.mean()))
    return np.array(shares), np.array(sups)


# ---------------------------------------------------------------- the floor

def synth(n, m, rng, *, bg, conj, n_conj=N_CONJ, scale=1.0):
    """A synthetic corpus with a tunable background AND planted conjunctions, in PROBABILITY space.

    THE FIRST VERSION OF THIS GENERATOR FAILED ITS OWN TEST AND THE GENERATOR WAS THE REASON. Built
    in logit space it produced a background of +0.242 -- against +0.05 to +0.11 on the real corpora --
    and a nominal 1.9x scaling arrived as 1.29x because the logistic saturated. A floor that fails on
    its generator tests nothing, which is the same trap `ability_control.py`'s first floor fell into.

    Rebuilt so the scaling is exact. What creates the background between two ARBITRARY items is not a
    prerequisite link -- most pairs have none -- it is shared learner ability, which is what
    `studies/identifiability/assay-generality/decompose.py` found on seven real datasets when source and target effects
    explained most of the statistic. So ability loading `bg` IS the background here, and `scale`
    multiplies the ability loading and the conjunction together: the same corpus, every effect twice
    as large.
    """
    theta = rng.normal(0, 1, n)
    mu = rng.uniform(0.34, 0.66, m)
    held = np.zeros((n, m), bool)
    triples = []
    for a, b, c in rng.choice(m, (n_conj, 3), replace=True):
        a, b, c = int(a), int(b), int(c)
        if len({a, b, c}) == 3 and c > max(a, b):
            triples.append((a, b, c))
    by_c = {}
    for a, b, c in triples:
        by_c.setdefault(c, []).append((a, b))
    for j in range(m):
        p = mu[j] + scale * bg * theta
        for a, b in by_c.get(j, []):
            p = p + scale * conj * (held[:, a] & held[:, b])
        held[:, j] = rng.random(n) < np.clip(p, 0.03, 0.97)
    return held, by_c


def synth_read(held, rng, bar_k=BAR_K):
    """Background, bar and above-bar share on a synthetic corpus, using the same cell arithmetic."""
    n, m = held.shape
    drops = []
    for a in range(m):
        for b in range(m):
            if a == b or held[:, a].sum() < MIN_CELL or (~held[:, a]).sum() < MIN_CELL:
                continue
            drops.append(float(held[held[:, a], b].mean() - held[~held[:, a], b].mean()))
    background = float(np.median(drops)) if drops else float("nan")
    inter = []
    for c in range(m):
        ok = held[:, c].astype(float)
        cols = [j for j in range(m) if j != c]
        got = score_item(ok, held[:, cols], [str(j) for j in cols], str(c))
        if got is not None:
            inter.append(np.stack([got["interaction"], got["z"]]))
    if not inter:
        return background, float("nan"), float("nan")
    allv = np.concatenate(inter, 1)
    keep = bh(one_sided_p(allv[1]), FDR_Q) & (allv[0] > 0)
    rel = float((keep & (allv[0] >= bar_k * background)).mean())
    fix = float((keep & (allv[0] >= MIN_MEANINGFUL)).mean())
    return background, rel, fix


def floor(rng, n=6000, m=26, reps=4):
    print("FLOOR -- two tests, and either one failing means the relative bar is not adopted\n")
    print("  (a) SCALE INVARIANCE: the same corpus with every effect multiplied, read both ways")
    rel1, rel2, fix1, fix2, bg1, bg2 = [], [], [], [], [], []
    for _ in range(reps):
        h1, _ = synth(n, m, rng, bg=BG, conj=CONJ, scale=1.0)
        h2, _ = synth(n, m, rng, bg=BG, conj=CONJ, scale=SCALE)
        b1, r1, f1 = synth_read(h1, rng)
        b2, r2, f2 = synth_read(h2, rng)
        bg1.append(b1); bg2.append(b2)
        rel1.append(r1); rel2.append(r2); fix1.append(f1); fix2.append(f2)
    B1, B2 = float(np.median(bg1)), float(np.median(bg2))
    R1, R2 = float(np.median(rel1)), float(np.median(rel2))
    F1, F2 = float(np.median(fix1)), float(np.median(fix2))
    print(f"      background   {B1:+.4f} -> {B2:+.4f}  (achieved scale {B2/max(B1,1e-9):.2f}x)")
    print(f"      RELATIVE bar share  {R1:.3f} -> {R2:.3f}   "
          f"(drift {abs(R2-R1)/max(R1,1e-9)*100:5.1f}%)")
    print(f"      FIXED  bar share    {F1:.3f} -> {F2:.3f}   "
          f"(drift {abs(F2-F1)/max(F1,1e-9)*100:5.1f}%)")
    rel_drift = abs(R2 - R1) / max(R1, 1e-9)
    fix_drift = abs(F2 - F1) / max(F1, 1e-9)
    inv = bool(rel_drift < fix_drift and rel_drift < 0.35)
    print(f"      -> {'SCALE INVARIANT' if inv else 'NOT SCALE INVARIANT'}: the relative bar "
          f"{'holds' if inv else 'does not hold'} its reading across a "
          f"{B2/max(B1,1e-9):.1f}x corpus while the fixed bar drifts {fix_drift*100:.0f}%")

    print("\n  (b) SELF-CANCELLATION: does planting conjunctions move the background itself?")
    b_off, b_on, cost_dirty, cost_clean = [], [], [], []
    for _ in range(reps):
        h0, _ = synth(n, m, rng, bg=BG, conj=0.0)
        h1, _ = synth(n, m, rng, bg=BG, conj=CONJ)
        B_off = synth_read(h0, rng)[0]
        B_on, share_own, _ = synth_read(h1, rng)
        # THE DECISIVE MEASURE: read the conjunction-bearing corpus against its OWN (inflated)
        # background, and against the background the same corpus would have had WITHOUT them
        _, share_clean, _ = synth_read(h1, rng, bar_k=BAR_K * B_off / max(B_on, 1e-9))
        b_off.append(B_off); b_on.append(B_on)
        cost_dirty.append(share_own); cost_clean.append(share_clean)
    B0, BC = float(np.median(b_off)), float(np.median(b_on))
    SD, SC = float(np.median(cost_dirty)), float(np.median(cost_clean))
    of_bg = (BC - B0) / max(B0, 1e-9)
    of_conj = (BC - B0) / max(CONJ, 1e-9)
    lost = (SC - SD) / max(SC, 1e-9)
    print(f"      background with conj=0.00 {B0:+.4f}")
    print(f"      background with conj={CONJ:.2f} {BC:+.4f}   "
          f"(a shift of {BC-B0:+.4f})")
    print(f"        as a fraction of the CONJUNCTION  {100*of_conj:+.1f}%   <- the pre-registered "
          f"measure, tolerance {100*SELF_CANCEL_TOL:.0f}%")
    print(f"        as a fraction of the BACKGROUND   {100*of_bg:+.1f}%   <- what the first "
          f"implementation computed; reported because it disagrees")
    print(f"      SHARE COST: reading the conjunction-bearing corpus against its own inflated "
          f"background gives {SD:.4f}; against the clean background {SC:.4f} "
          f"-> {100*lost:.1f}% of above-bar triples lost to self-inflation")
    clean = bool(abs(of_conj) <= SELF_CANCEL_TOL)
    print(f"      -> {'CLEAN' if clean else 'CONTAMINATED'} on the pre-registered measure")
    if not clean:
        print(f"      the bar rises with the signal it is meant to measure, so a relative bar "
              f"UNDERSTATES conjunctive structure in exactly the corpora that have most of it.")
    return dict(scale_invariant=inv, rel_drift=float(rel_drift), fix_drift=float(fix_drift),
                bg_low=B1, bg_high=B2, rel_low=R1, rel_high=R2, fix_low=F1, fix_high=F2,
                self_cancel_clean=clean, bg_no_conj=B0, bg_conj=BC,
                shift_of_conjunction=float(of_conj), shift_of_background=float(of_bg),
                share_own_bar=SD, share_clean_bar=SC, share_cost=float(lost))


# ---------------------------------------------------------------- arms

def arm(name, items_n=30, depth=3):
    """(per-dependant (ok, H, parent-names, c), item list, family-of-item or None)."""
    if name == "ednet":
        FT, OAT, FP, tags = load_dense()
        order = np.argsort(-np.isfinite(FT).sum(0))[:items_n]
        items = [tags[i] for i in order]
        dep = []
        for ci in order:
            sel = np.isfinite(FT[:, ci])
            pcols = [c for c in order if c != ci]
            dep.append((OAT[sel, ci].astype(float),
                        FP[np.ix_(sel, pcols)] < FT[sel, ci][:, None],
                        [tags[c] for c in pcols], tags[ci]))
        return dep, items, None, (FT, OAT, FP, list(order), tags)
    rows = list(xes3g5m_rows(data_path("XES_DIR")))
    fam = None
    if name == "xes3g5m-coarse":
        rows = list(coarsen(rows, depth))
    else:
        route = json.loads((data_path("XES_DIR") / "cid2route.json").read_text(encoding="utf-8"))
        fam = {f"k{int(k)}": " / ".join(v[:depth]) for k, v in route.items()
               if v and len(v) >= depth}
    by_learner = timelines(rows)
    ft, fp, oat = states(by_learner)
    idx = at_item(ft, oat)
    items = sorted(idx, key=lambda i: -len(idx[i]))[:items_n]
    dep = []
    for c in items:
        at_c = idx[c]
        learners = [l for l, _t, _y in at_c]
        tc = np.array([t for _l, t, _y in at_c])
        ok = np.array([float(y) for _l, _t, y in at_c])
        pnames = [p for p in items if p != c]
        H = np.zeros((len(at_c), len(pnames)), bool)
        for j, p in enumerate(pnames):
            for k, l in enumerate(learners):
                pp = fp[l].get(p)
                if pp is not None and pp < tc[k]:
                    H[k, j] = True
        dep.append((ok, H, pnames, c))
    return dep, items, fam, (ft, fp, oat, idx)


def backgrounds(name, items, extra, fam):
    """Corpus background, and per-family backgrounds where a taxonomy exists."""
    if name == "ednet":
        FT, OAT, FP, order, _tags = extra
        drops = []
        for a in order:
            for b in order:
                if a == b:
                    continue
                at_b = np.isfinite(FT[:, b])
                passed = FP[:, a] < FT[:, b]
                touched = FT[:, a] < FT[:, b]
                m, f = at_b & passed, at_b & touched & ~passed
                if m.sum() < MIN_CELL or f.sum() < MIN_CELL:
                    continue
                drops.append(float(OAT[m, b].mean() - OAT[f, b].mean()))
        return (float(np.median(drops)), len(drops)), None
    ft, fp, oat, idx = extra
    drops, fams = [], []
    for a in items:
        for b in items:
            if a == b:
                continue
            cl = classify((a, b), ft, fp, oat, idx)
            if len(cl["mastered"]) < MIN_CELL or len(cl["failed"]) < MIN_CELL:
                continue
            drops.append(float(np.mean(cl["mastered"]) - np.mean(cl["failed"])))
            fams.append(fam.get(b) if fam else None)
    drops = np.array(drops)
    per = None
    if fam:
        fa = np.array([f if f else "" for f in fams])
        per = {f: float(np.median(drops[fa == f])) for f in set(fa)
               if f and (fa == f).sum() >= 15}
    return (float(np.median(drops)), len(drops)), per


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default="xes3g5m",
                    choices=["xes3g5m", "xes3g5m-coarse", "ednet"])
    ap.add_argument("--items", type=int, default=30)
    ap.add_argument("--draws", type=int, default=1000)
    ap.add_argument("--null-reps", type=int, default=200)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    rng = np.random.default_rng(SEED)

    fl = floor(rng)
    print(f"\n{'='*78}\nARM: {args.arm}", flush=True)
    dep, items, fam, extra = arm(args.arm, args.items)
    (bg, npairs), per_fam = backgrounds(args.arm, items, extra, fam)
    print(f"  {len(dep)} dependants, corpus background {bg:+.4f} over {npairs:,} ordered pairs"
          + (f", {len(per_fam)} families with their own" if per_fam else
             " (no taxonomy -- family scope unavailable)"), flush=True)

    parts = [score_item(ok, H, pn, c) for ok, H, pn, c in dep]
    parts = [g for g in parts if g is not None]
    inter = np.concatenate([g["interaction"] for g in parts])
    z = np.concatenate([g["z"] for g in parts])
    base = np.concatenate([np.full(len(g["z"]), float(g["base"])) for g in parts])
    ncell = np.concatenate([g["ncell"] for g in parts])
    pos = {t: i for i, t in enumerate(items)}
    tri = np.stack([np.concatenate([[pos[x] for x in g[k]] for g in parts])
                    for k in ("c", "a", "b")], 1)
    pv = one_sided_p(z)
    T = len(z)
    dep_fam = np.concatenate([[fam.get(g["c"][0], "") if fam else ""] * len(g["z"])
                              for g in parts]) if fam else None

    out = dict(arm=args.arm, n_triples=T, background=bg, background_pairs=npairs,
               bar_k=BAR_K, floor=fl, scopes={})
    scopes = [("global", MIN_MEANINGFUL), ("corpus", BAR_K * bg)]
    if per_fam:
        scopes.append(("family", None))
    for label, b in scopes:
        if label == "family":
            bars = np.array([per_fam.get(f, bg) * BAR_K for f in dep_fam])
            above_mask = inter >= bars
            bshow = float(np.median(bars))
        else:
            above_mask = inter >= b
            bshow = b
        pw = planted_power(ncell, base, (round(bshow, 4),), rng)[round(bshow, 4)]["rate"]
        keep = bh(pv, FDR_Q) & (inter > 0)
        share = float((keep & above_mask).mean())
        nullshare, nullsup = pipeline_null(dep, items, bshow, rng, args.null_reps)
        nhi = float(np.percentile(nullshare, 97.5)) if len(nullshare) else float("nan")
        boot = block_bootstrap(items, tri, pv, inter, rng, args.draws, bar=bshow)
        d, vals = design_effect(boot, share, key="above_share", n=T)
        lo, hi = np.percentile(vals, [2.5, 97.5])
        verdict = ("UNANSWERABLE" if pw < MIN_POWER else
                   "STRUCTURE" if share > nhi else "NO STRUCTURE")
        print(f"\n  SCOPE = {label.upper()} (bar {bshow:+.4f}"
              + (", per-family median" if label == "family" else "") + ")")
        print(f"    above-bar share {share:.3f}, block CI [{lo:.3f}, {hi:.3f}], "
              f"power at bar {100*pw:.1f}%")
        print(f"    DERANGED PIPELINE NULL: share {np.median(nullshare):.4f}, "
              f"97.5th {nhi:.4f}  (the old rule compared against {FDR_Q:.2f})")
        print(f"    -> {verdict}")
        out["scopes"][label] = dict(bar=bshow, share=share, lo=float(lo), hi=float(hi),
                                    power=pw, design_effect=d, n_eff=float(T / d) if d else None,
                                    null_median=float(np.median(nullshare)), null_hi=nhi,
                                    null_reps=int(len(nullshare)), verdict=verdict,
                                    beats_old_rule=bool(share > FDR_Q))
    o = Path(args.out or f"out/relative_bar_{args.arm.replace('-', '_')}.json")
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(out, indent=2, default=_jsonable) + "\n")
    print(f"\nwrote {o}")


if __name__ == "__main__":
    main()
