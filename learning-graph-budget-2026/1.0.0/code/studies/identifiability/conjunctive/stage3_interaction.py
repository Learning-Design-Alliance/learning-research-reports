"""STAGE 3. Is there conjunctive structure in XES3G5M -- properly nulled, powered and corrected?

`chunking.py` found the interaction near zero in both expertise strata (-0.0049 and +0.0052) against
stage 1's PLANTED conjunctions of +0.19 to +0.40. But that study nulled the GAP BETWEEN STRATA, not
the INTERACTION LEVEL, so it could not say whether conjunctive structure is absent or merely
unmeasured. This does the missing test.

    interaction = (m1 - m2) - (m3 - m4)

with m1 = held both parents, m2 = held A only, m3 = held B only, m4 = held neither, among learners
who then reached the dependant. A conjunctive gate makes this large; two independent single-parent
gates make it zero, which stage 1 confirmed on planted data (0 of 12 additive arms fired).

THE THREE THINGS chunking.py SAID WERE MISSING, ALL PRESENT HERE.

  1. A NULL ON THE INTERACTION ITSELF. Under the hypothesis that a learner's parent-state is
     independent of their outcome, the interaction has variance p(1-p) * (1/n1 + 1/n2 + 1/n3 + 1/n4).
     That analytic null is used for all triples AND VALIDATED against an explicit learner-deranged
     null on a random subset -- if the two disagree the analytic form is wrong and the run says so.
     The derangement is the same control the rest of this programme uses: a learner keeps their
     outcome and inherits another learner's parent-state, with no fixed points.

  2. PER-TRIPLE MDE. `stage2_census.py` showed the limiting cell is `neither` -- as small as 20-29
     against a `both` cell of 8,000+ -- and power is set by the smallest cell, so most triples cannot
     see a moderate conjunction at all. Every triple carries its own MDE and a triple whose MDE
     exceeds the smallest conjunction worth asserting is returned UNKNOWN, never "null".

  3. MULTIPLE-COMPARISON CORRECTION. Thousands of triples are scored. Benjamini-Hochberg FDR at
     q = 0.05, applied once across all of them, exactly as antimatroid/study_verdict() does.

THE THREE-STATE EDGE, and CONTRADICTED requires the power to say so:

  SUPPORTED     interaction > 0 and significant after FDR correction.
  CONTRADICTED  the upper 95% bound falls BELOW the smallest conjunction worth asserting, so a
                conjunction of that size is ruled out for this triple.
  UNKNOWN       neither -- the triple is underpowered, which stage 2 predicts for most of them.

MIN_MEANINGFUL is pre-registered at +0.10, the background drop an arbitrary ordered pair already
shows. A conjunction smaller than the background is not worth asserting in this programme.

THE FLOOR IS SEMI-SYNTHETIC AND USES THE REAL CELL SIZES. Planting into idealised data would report
power we do not have. Instead the observed (n1, n2, n3, n4) of each real triple is kept and only the
OUTCOMES are simulated, under a known conjunction. That answers the question that matters: at
XES3G5M's actual cell sizes, what fraction of triples could detect a conjunction of a given strength?

Reads XES3G5M. Raw exports stay in the session scratchpad; only aggregates are committed.

    python3 stage3_interaction.py [--items 30] [--check-null 200]
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "studies/identifiability/overlap"))

from atlas import xes3g5m_rows  # noqa: E402
from positivity import SCRATCH, at_item, states, timelines  # noqa: E402

SEED = 20260922
#: every cell must hold this many learners. 20, not positivity.py's 5: an interaction is a
#: difference of differences and needs roughly four times the sample of a main effect.
MIN_CELL = 20
#: the smallest conjunction worth asserting -- the background drop an arbitrary ordered pair already
#: shows. PRE-REGISTERED, and the bar CONTRADICTED has to clear.
MIN_MEANINGFUL = 0.10
#: Benjamini-Hochberg false discovery rate, applied once across every scored triple. This is a
#: CORRECT use of q -- it controls the false discovery proportion among rejections. It is NOT the
#: threshold a share of tests has to beat; see PIPELINE_NULL_97_5.
FDR_Q = 0.05
#: The 97.5th percentile of the above-bar share when this entire pipeline is re-run on
#: learner-deranged data, measured in `relative_bar.py` over 200 replicates on this same corpus and
#: item set. It is the reference a share must beat, and it is ~500x smaller than FDR_Q, which the
#: verdict below used to use. Recorded as a constant rather than recomputed because it costs a
#: 200-replicate rescoring and does not depend on anything this run varies.
PIPELINE_NULL_97_5 = 0.0001


def cells_of(ok, ha, hb):
    """The four parent cells; None if any is too thin to read."""
    sel = [ha & hb, ha & ~hb, ~ha & hb, ~ha & ~hb]
    n = [int(s.sum()) for s in sel]
    if min(n) < MIN_CELL:
        return None
    m = [float(ok[s].mean()) for s in sel]
    return m, n


def score(ok, ha, hb):
    """Interaction, its analytic standard error, z, and the MDE this triple can actually see."""
    got = cells_of(ok, ha, hb)
    if got is None:
        return None
    m, n = got
    inter = (m[0] - m[1]) - (m[2] - m[3])
    p = float(ok.mean())
    var = p * (1 - p) * sum(1.0 / k for k in n)
    se = float(np.sqrt(var)) if var > 0 else float("nan")
    if not np.isfinite(se) or se <= 0:
        return None
    return dict(interaction=float(inter), se=se, z=float(inter / se),
                # two-sided 80%-power MDE: (z_{0.975} + z_{0.80}) * se
                mde=float(2.802 * se),
                n_cells=n, n_min=min(n), base=p)


def _derange(n, rng):
    p = rng.permutation(n)
    while True:
        fixed = np.flatnonzero(p == np.arange(n))
        if not len(fixed):
            return p
        if len(fixed) == 1:
            o = rng.integers(0, n - 1); o += o >= fixed[0]
            p[[fixed[0], o]] = p[[o, fixed[0]]]
        else:
            p[fixed] = p[np.roll(fixed, 1)]


def empirical_null(ok, ha, hb, rng, draws=200):
    """The learner-deranged null, run explicitly. Used to VALIDATE the analytic standard error."""
    vals = []
    for _ in range(draws):
        d = _derange(len(ok), rng)
        got = score(ok, ha[d], hb[d])
        if got:
            vals.append(got["interaction"])
    if len(vals) < draws // 3:
        return None
    return dict(null_mean=float(np.mean(vals)), null_sd=float(np.std(vals, ddof=1)), draws=len(vals))


def bh(pvals, q=FDR_Q):
    """Benjamini-Hochberg: returns a boolean array of which hypotheses are rejected at FDR q."""
    p = np.asarray(pvals, float)
    n = len(p)
    order = np.argsort(p)
    thresh = q * (np.arange(1, n + 1) / n)
    passed = p[order] <= thresh
    keep = np.zeros(n, bool)
    if passed.any():
        cut = np.max(np.flatnonzero(passed))
        keep[order[: cut + 1]] = True
    return keep


def norm_sf(z):
    """One-sided upper tail of the standard normal, without scipy."""
    from math import erfc, sqrt
    return 0.5 * erfc(np.asarray(z, float) / sqrt(2)) if np.ndim(z) else 0.5 * erfc(z / sqrt(2))


# ---------------------------------------------------------------- the semi-synthetic floor

def planted_power(rows, strengths, rng, reps=3):
    """At the REAL cell sizes, what fraction of triples could detect a conjunction of each strength?

    The observed (n1, n2, n3, n4) and base rate of each real triple are kept, and only the OUTCOMES
    are simulated: cell 1 (held both parents) gets base + strength, the other three get base. This
    reports the power we actually have rather than the power an idealised corpus would have.
    """
    out = {}
    for s in strengths:
        hits = 0
        tot = 0
        for r in rows:
            n = r["n_cells"]
            base = min(max(r["base"] - s * (1 - 0.0), 0.02), 0.98)
            for _ in range(reps):
                ok_parts, ha_parts, hb_parts = [], [], []
                for k, (nk, (a, b)) in enumerate(zip(n, ((1, 1), (1, 0), (0, 1), (0, 0)))):
                    p = min(base + s, 0.99) if k == 0 else base
                    ok_parts.append((rng.random(nk) < p).astype(float))
                    ha_parts.append(np.full(nk, bool(a)))
                    hb_parts.append(np.full(nk, bool(b)))
                got = score(np.concatenate(ok_parts), np.concatenate(ha_parts),
                            np.concatenate(hb_parts))
                tot += 1
                if got and got["interaction"] > got["mde"]:
                    hits += 1
        out[s] = dict(detected=hits, of=tot, rate=hits / max(tot, 1))
        print(f"  planted conjunction {s:+.2f}: detectable in {hits:,} of {tot:,} "
              f"triple-draws ({100*hits/max(tot,1):.1f}%)")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", type=int, default=30)
    ap.add_argument("--check-null", type=int, default=150)
    ap.add_argument("--out", default="out/stage3.json")
    args = ap.parse_args()
    rng = np.random.default_rng(SEED)

    rows_raw = list(xes3g5m_rows(SCRATCH / "xes3g5m"))
    by_learner = timelines(rows_raw)
    ft, fp, oat = states(by_learner)
    idx = at_item(ft, oat)
    items = sorted(idx, key=lambda i: -len(idx[i]))[:args.items]
    print(f"xes3g5m: {len(by_learner):,} learners, top {len(items)} items, "
          f"cell floor {MIN_CELL}, FDR q={FDR_Q}, smallest conjunction worth asserting "
          f"{MIN_MEANINGFUL:+.2f}\n", flush=True)

    scored, unreadable = [], 0
    check = []
    for c in items:
        at_c = idx[c]
        learners = [l for l, _t, _y in at_c]
        tc = np.array([t for _l, t, _y in at_c])
        ok = np.array([float(y) for _l, _t, y in at_c])
        parents = [p for p in items if p != c]
        held = {}
        for p in parents:
            h = np.zeros(len(at_c), bool)
            for k, l in enumerate(learners):
                pp = fp[l].get(p)
                if pp is not None and pp < tc[k]:
                    h[k] = True
            held[p] = h
        for a, b in itertools.combinations(parents, 2):
            got = score(ok, held[a], held[b])
            if got is None:
                unreadable += 1
                continue
            got.update(c=c, a=a, b=b)
            scored.append(got)
            if len(check) < args.check_null and rng.random() < 0.05:
                emp = empirical_null(ok, held[a], held[b], rng, draws=120)
                if emp:
                    emp.update(analytic_se=got["se"], c=c, a=a, b=b)
                    check.append(emp)
        print(f"   {c}: {len(scored):,} readable, {unreadable:,} below the cell floor", flush=True)

    if not scored:
        print("no triple cleared the cell floor")
        return

    # --- 1. is the analytic null right? compare its SE against the explicit deranged one
    ratios = [e["null_sd"] / e["analytic_se"] for e in check if e["analytic_se"] > 0]
    ratio = float(np.median(ratios)) if ratios else float("nan")
    null_ok = bool(0.85 <= ratio <= 1.18) if ratios else False
    print(f"\nNULL VALIDATION: explicit learner-deranged SD / analytic SE = {ratio:.3f} "
          f"across {len(ratios)} triples -> {'analytic null accepted' if null_ok else 'ANALYTIC NULL REJECTED'}")
    if ratios:
        print(f"  deranged null mean interaction: {np.median([e['null_mean'] for e in check]):+.5f} "
              f"(should be ~0)")
    if not null_ok:
        print("  the analytic form does not match the derangement; stopping rather than "
              "reporting corrected p-values built on it.")
        return

    # --- 2. power at the real cell sizes, before any real number is interpreted
    print(f"\nPOWER AT THE REAL CELL SIZES ({len(scored):,} triples, outcomes simulated, "
          f"cell sizes kept):")
    sample = [scored[i] for i in rng.choice(len(scored), min(400, len(scored)), replace=False)]
    power = planted_power(sample, (0.10, 0.20, 0.40), rng)

    # --- 3. the real reading, FDR-corrected
    z = np.array([r["z"] for r in scored])
    p_one = np.array([norm_sf(v) for v in z])
    keep = bh(p_one, FDR_Q)
    hi95 = np.array([r["interaction"] + 1.96 * r["se"] for r in scored])
    for i, r in enumerate(scored):
        r["p_one_sided"] = float(p_one[i])
        r["ci_hi"] = float(hi95[i])
        r["verdict"] = ("SUPPORTED" if keep[i] and r["interaction"] > 0
                        else "CONTRADICTED" if hi95[i] < MIN_MEANINGFUL
                        else "UNKNOWN")
    from collections import Counter
    tally = Counter(r["verdict"] for r in scored)
    # magnitude, not just significance: a triple can be statistically significant AND far below the
    # smallest conjunction worth asserting. Both numbers are reported.
    sup = [r for r in scored if r["verdict"] == "SUPPORTED"]
    above = [r for r in sup if r["interaction"] >= MIN_MEANINGFUL]
    sup_i = np.array([r["interaction"] for r in sup]) if sup else np.array([0.0])
    med_mde = float(np.median([r["mde"] for r in scored]))
    print(f"\n{len(scored):,} triples scored, {unreadable:,} below the cell floor")
    print(f"  median interaction {np.median([r['interaction'] for r in scored]):+.5f}, "
          f"median MDE {med_mde:+.4f}, median smallest cell "
          f"{int(np.median([r['n_min'] for r in scored]))}")
    for k in ("SUPPORTED", "CONTRADICTED", "UNKNOWN"):
        print(f"  {k:<13} {tally.get(k,0):>7,}  ({100*tally.get(k,0)/len(scored):.1f}%)")
    exp_false = FDR_Q * max(tally.get("SUPPORTED", 0), 0)
    print(f"  at FDR q={FDR_Q}, about {exp_false:.0f} of the {tally.get('SUPPORTED',0):,} "
          f"SUPPORTED are expected false")
    if sup:
        print(f"  SUPPORTED interaction: median {np.median(sup_i):+.4f}, "
              f"p90 {np.percentile(sup_i, 90):+.4f}, max {sup_i.max():+.4f}")
        print(f"  SUPPORTED AND >= the pre-registered bar of {MIN_MEANINGFUL:+.2f}: "
              f"{len(above):,} ({100*len(above)/len(scored):.1f}% of all scored triples)")

    share = tally.get("SUPPORTED", 0) / len(scored)
    big = len(above) / len(scored)
    # CORRECTED 2026-09-22. This compared `share > FDR_Q`, on the reasoning that the share had to
    # beat "the false-discovery allowance". It does not: Benjamini-Hochberg at q bounds the false
    # discovery proportion AMONG REJECTIONS, and under a global null it rejects approximately
    # nothing. Re-running the WHOLE pipeline -- scoring, BH and the bar -- on learner-deranged data
    # puts the null share at 0.0000 with a 97.5th percentile of 0.0001 (studies/identifiability/conjunctive/BAR.md), so the
    # old rule was over-strict by about 500x. It did NOT change this study's answer, whose share of
    # 0.216 and above-bar share of 0.108 clear either reference -- stage 3 was right for the wrong
    # reason -- but it manufactured a replication failure downstream that took three studies to
    # undo. The threshold is now the measured null, not the significance level.
    null_hi = PIPELINE_NULL_97_5
    verdict = ("UNDERPOWERED" if tally.get("UNKNOWN", 0) > len(scored) / 2 else
               "CONJUNCTIVE STRUCTURE" if share > null_hi and big > null_hi else
               "CONJUNCTIVE STRUCTURE BELOW THE BAR" if share > null_hi else
               "NO CONJUNCTIVE STRUCTURE")
    print(f"\nVERDICT: {verdict}")
    if verdict == "UNDERPOWERED":
        print("  most triples cannot see a conjunction worth asserting. This is NOT a null: "
              "per this programme's first rule, an instrument that cannot see a planted gate "
              "reports UNKNOWN, not absence.")
    elif verdict == "CONJUNCTIVE STRUCTURE BELOW THE BAR":
        print("  the interactions are statistically real and SMALLER than the background drop an "
              "arbitrary ordered pair already shows. Significant is not the same as worth asserting.")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(seed=SEED, min_cell=MIN_CELL, min_meaningful=MIN_MEANINGFUL,
                                   fdr_q=FDR_Q, items=args.items, verdict=verdict,
                                   null_ratio=ratio, null_accepted=null_ok,
                                   power_at_real_cells={str(k): v for k, v in power.items()},
                                   n_scored=len(scored), n_unreadable=unreadable,
                                   tally=dict(tally), median_mde=med_mde,
                                   supported_above_bar=len(above),
                                   supported_interaction={
                                       "median": float(np.median(sup_i)) if sup else None,
                                       "p90": float(np.percentile(sup_i, 90)) if sup else None,
                                       "max": float(sup_i.max()) if sup else None},
                                   all_interaction={
                                       "median": float(np.median([r["interaction"] for r in scored])),
                                       "p90": float(np.percentile([r["interaction"] for r in scored], 90)),
                                       "max": float(max(r["interaction"] for r in scored))},
                                   # a RANDOM sample: scored[] is ordered by item coverage, so the
                                   # first N over-represent the best-powered triples
                                   rows=[scored[i] for i in sorted(rng.choice(
                                       len(scored), min(400, len(scored)), replace=False))]),
                              indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
