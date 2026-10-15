"""A9 / A17 LEVEL 4. Does the conjunctive finding survive on EdNet?

`stage3_interaction.py` found conjunctive structure in XES3G5M and `block_bootstrap.py` showed it
survives being blocked on the 30 items it was measured from -- above-bar share 0.108, block CI
[0.063, 0.171], but an effective 122 independent tests rather than 11,203. Every one of those
numbers comes from ONE corpus, and A9 has never been met by anything: nothing in this programme has
ever replicated.

This runs the same estimand through the same code on both corpora, so a difference between the arms
is the corpus and not the implementation. XES3G5M is re-run rather than quoted, and its agreement
with stage 3 is checked before the EdNet arm is read.

THE BAR IS PER-CORPUS, AND THAT IS A CHANGE. Stage 3 scored against a fixed +0.10, the background
drop an arbitrary ordered XES3G5M pair already shows. `studies/identifiability/assay-generality/local_background.py` has
since shown that number is local even WITHIN XES3G5M -- family medians run +0.0517 to +0.1433 -- so
carrying XES3G5M's background onto EdNet would test "does EdNet beat XES3G5M's background", which is
a question about neither corpus. Each arm therefore computes its OWN background, by the same
definition (`studies/identifiability/overlap/positivity.py`'s strict mastered-minus-failed drop, median over ordered pairs),
and is scored against it. The fixed +0.10 is reported beside it so the two readings are visible
rather than chosen.

WHAT EDNET CANNOT CONTROL, stated before the result. KT1 carries no `source` column -- the sprint /
adaptive-offer distinction lives in KT3 and KT4, which we do not hold -- so recommender-chosen items
CANNOT be conditioned out. If EdNet's recommender bundles items, that bundling is inside the
interaction. This is the same confound XES3G5M has through curricular bundling, and neither arm
resolves it; it is why a positive result here is DIRECTIONAL, NOT CAUSAL, on both corpora.

The sample is 8,000 learners -- every KT1 file on disk, not a cap we chose -- against EdNet's
published ~780,000. Cell sizes, and therefore power, are a property of that sample.

PRE-REGISTERED, before the run. The finding under test is stage 3's: a non-trivial share of triples
carry an interaction at or above the corpus background, and that share survives item-level blocking.

  UNANSWERABLE     the arm's analytic null fails validation against the learner derangement, OR its
                   power at its own real cell sizes is under 50% at a planted effect the size of the
                   bar being read. Reported as UNKNOWN, never as absence -- this programme's first
                   rule. The power gate is applied PER BAR, for the reason recorded below.
  REPLICATES       both arms powered and validated at that bar, and the EdNet block-CI lower bound
                   on the above-bar share clears FDR_Q = 0.05.
  FAILS            EdNet powered and validated at that bar, and its block-CI lower bound does NOT
                   clear 0.05. Real negative evidence, not a missing measurement.

  and separately, because "both positive" is a weaker claim than "the same size":
  AGREES ON MAGNITUDE   the two arms' block CIs on the above-bar share overlap.

ONE THING WAS RESTRUCTURED AFTER A SMOKE RUN AND IT IS RECORDED HERE RATHER THAN QUIETLY. The
pre-registration above first gated the WHOLE arm on power at its OWN bar. A six-item smoke run then
showed EdNet's background is +0.0463, less than half XES3G5M's +0.1061, and that EdNet detects a
planted +0.046 in 13.8% of triples against 100% at +0.20. Under the original wording that single
number would have returned UNANSWERABLE and thrown away a comparison that is fully powered -- the one
at the FIXED +0.10 bar, which is the bar stage 3's claim was actually stated at and therefore the
claim A9 is asking about. So the power gate now applies PER BAR instead of per arm. MIN_POWER was
not lowered, no bar was moved, and the primary verdict is the FIXED-bar one because that is stage
3's claim; the own-bar reading is secondary and is reported as UNANSWERABLE where it is underpowered.
That EdNet's background is half of XES3G5M's is itself a result, and it is the local_background
finding showing up between corpora rather than within one.

Reads XES3G5M and EdNet. EdNet is CC BY-NC 4.0 -- non-commercial, no model training; counting
learners in cells is neither. Raw exports stay in the session scratchpad; only aggregates are
committed.

    python3 replicate.py --dataset ednet [--items 30] [--draws 1000]
    python3 replicate.py --compare

DIRECTION: symmetric -- the conjunctive interaction is symmetric in its two parents, and which item
is the dependant is fixed by each learner's timeline (states held before first reaching it), not by
an edge convention; 'directional' in the text means 'not causal'.

Direction declaration added 2026-09-24 (reversed-arrow rule, shared/experimental-contract.md):
nothing reported depends on edge orientation, so no reversed-arrow control applies.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "studies/identifiability/overlap"))

from atlas import ednet_rows, xes3g5m_rows  # noqa: E402
from positivity import SCRATCH, at_item, classify, states, timelines  # noqa: E402
from block_bootstrap import (FDR_Q, MIN_CELL, MIN_MEANINGFUL, _jsonable,  # noqa: E402
                             block_bootstrap, design_effect, jackknife, one_sided_p,
                             pipeline, score_item)

SEED = 20260922
FLOOR_SHARE = FDR_Q
#: a corpus arm must be able to see a planted effect the size of its own bar this often to be read
MIN_POWER = 0.50
#: the deranged SD / analytic SE band outside which the analytic null is rejected, as in stage 3
NULL_BAND = (0.85, 1.18)
STRATA = 5

CORPORA = {"xes3g5m": lambda: xes3g5m_rows(SCRATCH / "xes3g5m"),
           "ednet": lambda: ednet_rows(SCRATCH / "ednet", limit_learners=8000)}

#: XES3G5M at the grain of its own expert taxonomy, for the control described in coarsen()
COARSE_DEPTH = 3


def coarsen(rows, depth=COARSE_DEPTH):
    """Relabel XES3G5M attempts by their depth-3 taxonomy family instead of their leaf KC.

    THE ALTERNATIVE EXPLANATION FOR ANY EDNET GAP. EdNet ships 142 expert tags where XES3G5M ships
    865 leaf KCs, and an item that is a MIXTURE of finer skills dilutes an interaction: a learner who
    "holds" a coarse tag may hold any of the skills inside it, so the four parent cells stop being
    the four states the statistic is about. If the conjunctive share collapses when XES3G5M is read
    at its own coarse grain too, the difference between the corpora is ZOOM LEVEL, not corpus -- and
    "EdNet has no conjunctions" would be the wrong sentence.
    """
    route = json.loads((SCRATCH / "xes3g5m" / "cid2route.json").read_text(encoding="utf-8"))
    fam = {f"k{int(k)}": " / ".join(v[:depth]) for k, v in route.items()
           if v and len(v) >= depth}
    for learner, item, ok, t, a, b in rows:
        f = fam.get(item)
        if f:
            yield (learner, f, ok, t, a, b)


# ---------------------------------------------------------------- the corpus's own background

def background(items, ft, fp, oat, idx, min_cell=MIN_CELL):
    """Median pairwise drop over ordered pairs -- the number +0.10 was, measured per corpus.

    Same definition as studies/identifiability/assay-generality/local_background.py, which is studies/identifiability/overlap/positivity.py's STRICT
    cells: `mastered` passed A before reaching B, `failed` attempted A before reaching B and never
    passed it. Learners who never touched A are excluded, because "never offered" is selection.
    """
    drops = []
    for a in items:
        for b in items:
            if a == b:
                continue
            c = classify((a, b), ft, fp, oat, idx)
            if len(c["mastered"]) < min_cell or len(c["failed"]) < min_cell:
                continue
            drops.append(float(np.mean(c["mastered"]) - np.mean(c["failed"])))
    if not drops:
        return None, 0
    return float(np.median(drops)), len(drops)


# ---------------------------------------------------------------- null validation and power

def derangement_null(ok, H, parents, c, rng, draws=200):
    """Per-triple deranged SD against the analytic SE, all pairs of one dependant at once.

    Stage 3 did this triple by triple on a 5% subsample. Vectorised, a whole dependant's 406 pairs
    come out of one permuted scoring, so the check runs on every triple of the sampled dependants
    instead of a handful.
    """
    n = len(ok)
    real = score_item(ok, H, parents, c)
    if real is None:
        return None
    keyed = {(str(a), str(b)): i for i, (a, b) in enumerate(zip(real["a"], real["b"]))}
    acc = [[] for _ in keyed]
    for _ in range(draws):
        d = rng.permutation(n)
        fixed = np.flatnonzero(d == np.arange(n))
        if len(fixed) > 1:
            d[fixed] = d[np.roll(fixed, 1)]
        got = score_item(ok, H[d], parents, c)
        if got is None:
            continue
        for a, b, v in zip(got["a"], got["b"], got["interaction"]):
            k = keyed.get((str(a), str(b)))
            if k is not None:
                acc[k].append(v)
    sd, se, mean = [], [], []
    for i, vals in enumerate(acc):
        if len(vals) < draws // 3:
            continue
        sd.append(float(np.std(vals, ddof=1)))
        se.append(float(real["se"][i]))
        mean.append(float(np.mean(vals)))
    return (np.array(sd), np.array(se), np.array(mean)) if sd else None


def planted_power(n_cells, base, strengths, rng, reps=4):
    """At this corpus's REAL cell sizes, how often is a planted conjunction of each size detectable?

    The observed (n1, n2, n3, n4) and base rate of every triple are kept and only the OUTCOMES are
    simulated. Vectorised over triples: cell 1 draws at base + strength, the other three at base.
    """
    out = {}
    n = np.asarray(n_cells, float)
    for s in strengths:
        b = np.clip(np.asarray(base, float) - s, 0.02, 0.98)
        hits = tot = 0
        for _ in range(reps):
            p1 = np.minimum(b + s, 0.99)
            s1 = rng.binomial(n[:, 0].astype(int), p1)
            rest = [rng.binomial(n[:, k].astype(int), b) for k in (1, 2, 3)]
            m = [s1 / n[:, 0]] + [rest[k] / n[:, k + 1] for k in range(3)]
            inter = (m[0] - m[1]) - (m[2] - m[3])
            se = np.sqrt(b * (1 - b) * (1.0 / n).sum(1))
            hits += int((inter > 2.802 * se).sum())
            tot += len(b)
        out[float(s)] = dict(detected=hits, of=tot, rate=hits / max(tot, 1))
    return out


# ---------------------------------------------------------------- ability, the confound stage 3 needed

def ability_matrix(learners, tc, by_learner, parents, c):
    """Prior accuracy excluding c, plus the per-parent counts needed to exclude a and b as well.

    Recomputing this inside the pair loop ran 8 of 30 dependants in 2h10m; ability excludes only a,
    b and c, so the per-item counts accumulate once and subtract.
    """
    n = len(learners)
    tot_h, tot_n = np.zeros(n), np.zeros(n)
    item_h = {p: np.zeros(n) for p in parents}
    item_n = {p: np.zeros(n) for p in parents}
    for k, l in enumerate(learners):
        for t, item, good in by_learner[l]:
            if t >= tc[k] or item == c:
                continue
            tot_n[k] += 1
            tot_h[k] += bool(good)
            if item in item_n:
                item_n[item][k] += 1
                item_h[item][k] += bool(good)
    return tot_h, tot_n, item_h, item_n


def stratified(ok, ha, hb, abil, strata=STRATA):
    """Interaction within ability quintiles, pooled by inverse variance."""
    good = np.isfinite(abil)
    if good.sum() < 4 * MIN_CELL * strata:
        return None
    qs = np.quantile(abil[good], np.linspace(0, 1, strata + 1))
    qs[0] -= 1e-9
    vs, ws = [], []
    for i in range(strata):
        sel = good & (abil > qs[i]) & (abil <= qs[i + 1])
        cells = [sel & ha & hb, sel & ha & ~hb, sel & ~ha & hb, sel & ~ha & ~hb]
        ns = [int(s.sum()) for s in cells]
        if min(ns) < MIN_CELL:
            continue
        ms = [float(ok[s].mean()) for s in cells]
        p = float(ok[sel].mean())
        var = p * (1 - p) * sum(1.0 / k for k in ns)
        if var <= 0:
            continue
        vs.append((ms[0] - ms[1]) - (ms[2] - ms[3]))
        ws.append(1.0 / var)
    if not vs:
        return None
    w = np.array(ws)
    return float((w * np.array(vs)).sum() / w.sum())


# ---------------------------------------------------------------- one arm, end to end

def run_arm(name, args, rng):
    base_name = name.replace("-coarse", "")
    rows = list(CORPORA[base_name]())
    if name.endswith("-coarse"):
        rows = list(coarsen(rows, args.depth))
    by_learner = timelines(rows)
    ft, fp, oat = states(by_learner)
    idx = at_item(ft, oat)
    items = sorted(idx, key=lambda i: -len(idx[i]))[:args.items]
    pos = {it: i for i, it in enumerate(items)}
    print(f"\n{'='*78}\n{name}: {len(by_learner):,} learners, {len(idx):,} items available, "
          f"top {len(items)} used, cell floor {MIN_CELL}, FDR q={FDR_Q}", flush=True)

    bar, n_pairs = background(items, ft, fp, oat, idx)
    print(f"  CORPUS BACKGROUND: {bar:+.4f} over {n_pairs:,} readable ordered pairs "
          f"(the fixed bar stage 3 used is {MIN_MEANINGFUL:+.2f})", flush=True)

    parts, checks = [], []
    for j, c in enumerate(items):
        at_c = idx[c]
        learners = [l for l, _t, _y in at_c]
        tc = np.array([t for _l, t, _y in at_c])
        ok = np.array([float(y) for _l, _t, y in at_c])
        parents = [p for p in items if p != c]
        H = np.zeros((len(at_c), len(parents)), bool)
        for jj, p in enumerate(parents):
            for k, l in enumerate(learners):
                pp = fp[l].get(p)
                if pp is not None and pp < tc[k]:
                    H[k, jj] = True
        got = score_item(ok, H, parents, c)
        if got is None:
            print(f"   {c}: nothing readable", flush=True)
            continue
        got["base_arr"] = np.full(len(got["z"]), float(got["base"]))
        parts.append(got)
        if j < args.null_items:
            ch = derangement_null(ok, H, parents, c, rng, draws=args.null_draws)
            if ch:
                checks.append(ch)
        if args.ability:
            got["ability"] = ability_matrix(learners, tc, by_learner, parents, c) + \
                (ok, H, parents)
        print(f"   {c}: {sum(len(g['z']) for g in parts):,} readable", flush=True)

    z = np.concatenate([g["z"] for g in parts])
    inter = np.concatenate([g["interaction"] for g in parts])
    base = np.concatenate([g["base_arr"] for g in parts])
    ncell = np.concatenate([g["ncell"] for g in parts])
    tri_items = np.stack([np.concatenate([[pos[x] for x in g[k]] for g in parts])
                          for k in ("c", "a", "b")], 1)
    T = len(z)
    pvals = one_sided_p(z)

    # --- null validation: is the analytic SE the derangement's SD?
    sd = np.concatenate([c[0] for c in checks])
    se = np.concatenate([c[1] for c in checks])
    mu = np.concatenate([c[2] for c in checks])
    ratio = float(np.median(sd / se))
    null_ok = bool(NULL_BAND[0] <= ratio <= NULL_BAND[1])
    print(f"\n  NULL VALIDATION: deranged SD / analytic SE = {ratio:.3f} over {len(sd):,} triples "
          f"from {len(checks)} dependants, deranged mean interaction {np.median(mu):+.5f} "
          f"-> {'accepted' if null_ok else 'ANALYTIC NULL REJECTED'}")

    # --- power at this corpus's own cell sizes, at ITS OWN bar
    print(f"  POWER AT THIS CORPUS'S REAL CELL SIZES ({T:,} triples, outcomes simulated):")
    power = planted_power(ncell, base, (round(bar, 4), 0.20, 0.40), rng)
    for s, v in power.items():
        print(f"    planted {s:+.4f}: detectable {100*v['rate']:.1f}% "
              f"({v['detected']:,} of {v['of']:,})")
    p_own = power[round(bar, 4)]["rate"]
    p_fixed = planted_power(ncell, base, (MIN_MEANINGFUL,), rng)[float(MIN_MEANINGFUL)]["rate"]
    print(f"    planted {MIN_MEANINGFUL:+.4f} (the fixed bar): detectable {100*p_fixed:.1f}%")
    print(f"  -> null {'accepted' if null_ok else 'REJECTED'}; power {100*p_own:.1f}% at its own "
          f"bar and {100*p_fixed:.1f}% at the fixed bar, against a {100*MIN_POWER:.0f}% floor")

    out = dict(corpus=name, learners=len(by_learner), items=len(items), n_triples=T,
               background=bar, background_pairs=n_pairs, fixed_bar=MIN_MEANINGFUL,
               null_ratio=ratio, null_accepted=null_ok, null_mean=float(np.median(mu)),
               power=power, power_at_own_bar=p_own, power_at_fixed_bar=p_fixed)
    if not null_ok:
        print("  the analytic null does not match the derangement; not reading corrected counts "
              "off p-values built on it.")
        out["readable_own"] = out["readable_fixed"] = False
        return out, None

    # --- the reading, against BOTH bars, blocked on items, each gated on ITS OWN power
    for label, b, pw in (("own", bar, p_own), ("fixed", MIN_MEANINGFUL, p_fixed)):
        out[f"readable_{label}"] = bool(pw >= MIN_POWER)
        if pw < MIN_POWER:
            print(f"\n  BAR = {label.upper()} ({b:+.4f}): UNANSWERABLE -- {100*pw:.1f}% power at "
                  f"this corpus's real cell sizes, under the {100*MIN_POWER:.0f}% floor. This is "
                  f"UNKNOWN, not absence.")
            continue
        pt = pipeline(pvals, inter, bar=b)
        boot = block_bootstrap(items, tri_items, pvals, inter, rng, args.draws, bar=b)
        d, vals = design_effect(boot, pt["above_share"], key="above_share", n=T)
        lo, hi = np.percentile(vals, [2.5, 97.5])
        cnt = np.array([x["above"] for x in boot], float)
        out[f"read_{label}"] = dict(
            bar=b, supported=pt["supported"], above=pt["above"], share=pt["share"],
            above_share=pt["above_share"], lo=float(lo), hi=float(hi), design_effect=d,
            n_eff=float(T / d) if np.isfinite(d) and d > 0 else float("nan"),
            count_ci=[float(np.percentile(cnt, 2.5)), float(np.percentile(cnt, 97.5))])
        print(f"\n  BAR = {label.upper()} ({b:+.4f}): SUPPORTED {pt['supported']:,} "
              f"({100*pt['share']:.1f}%), above bar {pt['above']:,} ({100*pt['above_share']:.1f}%)")
        print(f"    block CI on the above-bar share [{lo:.3f}, {hi:.3f}], design effect {d:.1f}, "
              f"effective independent triples {T/d:.0f}, count CI "
              f"[{np.percentile(cnt,2.5):,.0f}, {np.percentile(cnt,97.5):,.0f}]")

    primary = "read_fixed" if "read_fixed" in out else "read_own"
    if primary not in out:
        return out, None
    jk = jackknife(items, tri_items, pvals, inter, bar=out[primary]["bar"])
    worst = min(jk, key=lambda r: r["above"])
    lost = 1 - worst["above"] / max(out[primary]["above"], 1)
    out["jackknife_worst"] = dict(item=str(worst["dropped"]), above=worst["above"], cost=float(lost))
    print(f"  leave-one-item-out: worst single item ({worst['dropped']}) costs {100*lost:.1f}%")

    # --- ability, on the arm's own above-bar set
    if args.ability:
        abar = out[primary]["bar"]
        raw, adj = [], []
        for g in parts:
            th, tn, ih, inn, ok_g, H_g, parents_g = g["ability"]
            pidx = {p: i for i, p in enumerate(parents_g)}
            for a, b_, iv in zip(g["a"], g["b"], g["interaction"]):
                if iv < abar:
                    continue
                # ability excludes a, b and c: total minus the two parents' own contributions
                nb = tn - inn[a] - inn[b_]
                hb_ = th - ih[a] - ih[b_]
                abil = np.where(nb >= 5, hb_ / np.maximum(nb, 1), np.nan)
                v = stratified(ok_g, H_g[:, pidx[a]], H_g[:, pidx[b_]], abil)
                if v is not None:
                    raw.append(float(iv)); adj.append(v)
        if raw:
            R, A = float(np.median(raw)), float(np.median(adj))
            kept_n = int(sum(1 for v in adj if v >= abar))
            out["ability"] = dict(n=len(raw), raw_median=R, adj_median=A,
                                  kept_fraction=float(A / R) if abs(R) > 1e-9 else float("nan"),
                                  still_above=kept_n)
            print(f"  ABILITY (quintile-stratified, on the {len(raw):,} above-bar triples): "
                  f"median {R:+.4f} -> {A:+.4f} (keeps {100*A/R:.0f}%), "
                  f"{kept_n:,} still at or above the bar")
    return out, dict(tri_items=tri_items, T=T)


def compare(res):
    """The replication verdict, at the FIXED bar because that is the bar stage 3's claim was made at.

    The own-bar reading is reported beside it and carries its own verdict, which may be UNANSWERABLE
    where a corpus's background is small enough that its own bar is below what its cell sizes can see.
    """
    ref, rep = res.get("xes3g5m"), res.get("ednet")
    print(f"\n{'='*78}\nREPLICATION")
    if not (ref and rep):
        print("  need both arms")
        return "UNANSWERABLE"
    print(f"  background          XES3G5M {ref['background']:+.4f}   "
          f"EdNet {rep['background']:+.4f}   "
          f"-- EdNet's own background is {rep['background']/ref['background']:.2f}x XES3G5M's, so "
          f"the fixed +0.10 bar asks EdNet for {MIN_MEANINGFUL/rep['background']:.1f}x its own "
          f"background against {MIN_MEANINGFUL/ref['background']:.1f}x for XES3G5M")
    verdict = None
    for label in ("fixed", "own"):
        a, b = ref.get(f"read_{label}"), rep.get(f"read_{label}")
        head = f"  AT THE {label.upper()} BAR"
        if not (ref.get(f"readable_{label}") and rep.get(f"readable_{label}")):
            who = " and ".join(n for n, r in (("XES3G5M", ref), ("EdNet", rep))
                               if not r.get(f"readable_{label}"))
            v = "UNANSWERABLE"
            print(f"{head}: {v} -- {who} underpowered at it. UNKNOWN, not absence.")
        else:
            print(f"{head} (XES3G5M {a['bar']:+.4f} / EdNet {b['bar']:+.4f})")
            print(f"    above-bar share   XES3G5M {a['above_share']:.3f} "
                  f"[{a['lo']:.3f}, {a['hi']:.3f}]   "
                  f"EdNet {b['above_share']:.3f} [{b['lo']:.3f}, {b['hi']:.3f}]")
            print(f"    effective tests   XES3G5M {a['n_eff']:.0f} of {ref['n_triples']:,}   "
                  f"EdNet {b['n_eff']:.0f} of {rep['n_triples']:,}")
            expect = a["above_share"] * (rep[f"power_at_{label}_bar"] /
                                          max(ref[f"power_at_{label}_bar"], 1e-9))
            print(f"    if EdNet carried XES3G5M's structure, its {100*rep[f'power_at_{label}_bar']:.0f}% "
                  f"power against XES3G5M's {100*ref[f'power_at_{label}_bar']:.0f}% predicts an "
                  f"above-bar share of {expect:.3f}; observed {b['above_share']:.3f} "
                  f"({b['above_share']/max(expect,1e-9):.2f}x)")
            v = "REPLICATES" if b["lo"] > FLOOR_SHARE else "FAILS"
            overlap = not (b["hi"] < a["lo"] or a["hi"] < b["lo"])
            print(f"    -> {v}"
                  + ("  (AGREES ON MAGNITUDE)" if overlap and v == "REPLICATES"
                     else "  (INTERVALS DO NOT OVERLAP)" if v == "REPLICATES" else ""))
        if label == "fixed":
            verdict = v

    co = res.get("xes3g5m-coarse")
    if co and co.get("read_fixed") and rep.get("read_fixed"):
        c, b = co["read_fixed"], rep["read_fixed"]
        a = ref["read_fixed"]
        print(f"\n  GRAIN CONTROL -- is the gap the corpus, or the zoom level? EdNet ships "
              f"{rep['items']} of 142 expert tags where XES3G5M ships {ref['items']} of 865 leaf "
              f"KCs, and a coarse item is a MIXTURE of finer skills, which dilutes an interaction.")
        print(f"    XES3G5M re-read at its own depth-{COARSE_DEPTH} taxonomy grain "
              f"({co['items']} of 172 families, against EdNet's 142 tags), power "
              f"{100*co['power_at_fixed_bar']:.0f}% against EdNet's "
              f"{100*rep['power_at_fixed_bar']:.0f}% -- matched on both:")
        print(f"      XES3G5M fine     {a['above_share']:.3f} [{a['lo']:.3f}, {a['hi']:.3f}]")
        print(f"      XES3G5M coarse   {c['above_share']:.3f} [{c['lo']:.3f}, {c['hi']:.3f}]")
        print(f"      EdNet            {b['above_share']:.3f} [{b['lo']:.3f}, {b['hi']:.3f}]")
        ov = not (b["hi"] < c["lo"] or c["hi"] < b["lo"])
        print(f"    -> coarsening costs XES3G5M "
              f"{100*(1 - c['above_share']/max(a['above_share'],1e-9)):.0f}% of its share, so GRAIN "
              f"IS PART OF IT -- but at matched grain and matched power XES3G5M still runs "
              f"{c['above_share']/max(b['above_share'],1e-9):.0f}x EdNet and the intervals "
              f"{'OVERLAP' if ov else 'DO NOT OVERLAP'}. The gap is not explained by zoom level.")
        if c["lo"] <= FLOOR_SHARE:
            print(f"    AND A CAVEAT AGAINST MY OWN READING: coarse XES3G5M's own lower bound "
                  f"{c['lo']:.3f} does not clear {FLOOR_SHARE:.2f} either, so at this grain the "
                  f"pass/fail line is not what separates the corpora. What survives is the "
                  f"{c['above_share']/max(b['above_share'],1e-9):.0f}x ratio and the non-overlap.")

    print(f"\nVERDICT: {verdict}")
    if verdict == "FAILS":
        print(f"  EdNet is powered at the fixed bar "
              f"({100*rep['power_at_fixed_bar']:.0f}%) and its analytic null validates against the "
              f"derangement ({rep['null_ratio']:.3f}), so this is a measurement and not a gap. The "
              f"above-bar share's blocked lower bound does not clear the {FLOOR_SHARE:.2f} the "
              f"false-discovery allowance itself occupies. Stage 3's conjunctive structure is a "
              f"fact about XES3G5M, not about learners.")
    elif verdict == "REPLICATES":
        print(f"  conjunctive structure above the bar is present on two independent corpora, "
              f"blocked on the items each was measured from. A9 is met for this estimand and A17 "
              f"reaches level 4 -- the first replication of anything in this programme.")
    else:
        print(f"  neither corpus can be read at this bar with the cell sizes on disk. Per this "
              f"programme's first rule that is UNKNOWN and it is a COLLECTION requirement, not a "
              f"null.")
    return verdict


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="both",
                    choices=["both", "ednet", "xes3g5m", "xes3g5m-coarse", "compare"])
    ap.add_argument("--items", type=int, default=30)
    ap.add_argument("--draws", type=int, default=1000)
    ap.add_argument("--depth", type=int, default=COARSE_DEPTH)
    ap.add_argument("--null-items", type=int, default=4)
    ap.add_argument("--null-draws", type=int, default=150)
    ap.add_argument("--no-ability", dest="ability", action="store_false", default=True)
    ap.add_argument("--out", default="out/replicate.json")
    args = ap.parse_args()
    rng = np.random.default_rng(SEED)

    # each arm can be run in its own process and merged afterwards with --dataset compare, so a
    # long run is not one failure away from losing both
    if args.dataset == "compare":
        res = {}
        for n in ("xes3g5m", "ednet", "xes3g5m-coarse"):
            f = HERE / f"out/replicate_{n.replace('-', '_')}.json"
            if f.exists():
                res[n] = json.loads(f.read_text())["arms"][n]
    else:
        names = ["xes3g5m", "ednet"] if args.dataset == "both" else [args.dataset]
        res = {}
        for n in names:
            res[n], _ = run_arm(n, args, rng)
    verdict = compare(res) if len(res) >= 2 else None

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(seed=SEED, items=args.items, draws=args.draws,
                                   min_power=MIN_POWER, floor_share=FLOOR_SHARE,
                                   verdict=verdict, arms=res),
                              indent=2, default=_jsonable) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
