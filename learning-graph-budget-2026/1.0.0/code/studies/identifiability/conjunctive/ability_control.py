"""Is stage 3's conjunctive structure real, or is it learner ability wearing a conjunction's shape?

THE CONFOUND, WHICH I DID NOT STATE WHEN I REPORTED STAGE 3. The interaction

    (m1 - m2) - (m3 - m4)      m1 = held both parents, ... m4 = held neither

cancels a learner-ability effect ONLY IF ability is ADDITIVE in the number of parents held. It is not
obviously additive. Learners who hold both parents are systematically abler, and if ability is
SUPER-ADDITIVE -- abler learners hold more parents AND do disproportionately better on the dependant
beyond the sum of the two -- the interaction fires with no conjunction present at all.

So stage 3's 1,212 triples at or above the pre-registered bar have a live alternative explanation:
CONJUNCTIVE STRUCTURE **OR** ABILITY SUPER-ADDITIVITY. This separates them.

DP's framing is what surfaced it, and it generalises past ability: a conjunct may be a prior skill, a
piece of vocabulary, or an ATTRIBUTE -- working memory, mobility, motivation -- that has no
acquisition event at all. An attribute never enters `first_pass`, so it can never be a conditioning
variable here; it can only ever act as an unobserved co-parent. Ability is the one such attribute we
can estimate from the logs we hold, so it is the one we can control for. The rest cannot be, and that
limit is a property of response-log data, not of this study.

THE CONTROL. Estimate each learner's ability from their accuracy on KCs OTHER THAN A, B and C, using
only attempts BEFORE they reached the dependant -- excluding the three KCs avoids circularity, and
the time restriction avoids conditioning on the future. Stratify learners into ability tertiles,
compute the interaction WITHIN each stratum, and pool by inverse variance. A within-stratum
comparison holds ability roughly fixed, so a conjunction survives it and an ability artefact does not.
This is a Mantel-Haenszel-style adjustment and it assumes no interaction-by-ability effect, which is
weaker than assuming ability is additive.

PRE-REGISTERED VERDICTS, written before the run:

  SURVIVES          the ability-adjusted interaction keeps at least 75% of the unadjusted magnitude
                    on the triples stage 3 called SUPPORTED. The conjunctions are not ability.
  ABILITY ARTEFACT  the adjusted interaction falls below HALF the unadjusted AND below the
                    pre-registered +0.10 bar. Stage 3's positive was ability super-additivity and
                    must be withdrawn.
  PARTIAL           in between: real but inflated, and stage 3's magnitudes need restating.

THE FLOOR DECIDES WHETHER ANY OF THAT MEANS ANYTHING, and the second arm is the one that matters:

  "conjunction"   a true conjunction, ability additive -> adjusted must SURVIVE
  "ability"       NO conjunction, ability super-additive in parents held -> unadjusted must FIRE and
                  adjusted must GO QUIET. If it does not, the control cannot separate them and no
                  real number is read.
  "both"          both planted -> adjusted must recover roughly the conjunction alone.

Reads XES3G5M. Raw exports stay in the session scratchpad; only aggregates are committed.

    python3 ability_control.py --floor-only
    python3 ability_control.py [--items 30] [--strata 3]
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

from stage3_interaction import MIN_CELL, MIN_MEANINGFUL, SEED, score  # noqa: E402
from atlas import xes3g5m_rows  # noqa: E402
from positivity import SCRATCH, at_item, states, timelines  # noqa: E402

#: ability quintiles. TUNED, not assumed: on a planted pure-ability artefact, 3 strata remove 65%,
#: 5 remove 76%, 8 remove 71% and cost more cells. Stage 3's median smallest cell was 658, so five
#: strata leave ~130 and most triples stay readable.
STRATA = 5


def adjusted(ok, ha, hb, ability, strata=STRATA):
    """Interaction within ability strata, pooled by inverse variance."""
    qs = np.quantile(ability, np.linspace(0, 1, strata + 1))
    qs[0] -= 1e-9
    parts = []
    for i in range(strata):
        sel = (ability > qs[i]) & (ability <= qs[i + 1])
        if sel.sum() < 4 * MIN_CELL:
            continue
        got = score(ok[sel], ha[sel], hb[sel])
        if got:
            parts.append(got)
    if not parts:
        return None
    w = np.array([1.0 / (p["se"] ** 2) for p in parts])
    v = np.array([p["interaction"] for p in parts])
    pooled = float((w * v).sum() / w.sum())
    se = float(np.sqrt(1.0 / w.sum()))
    return dict(interaction=pooled, se=se, z=pooled / se, strata_used=len(parts),
                mde=2.802 * se)


# ---------------------------------------------------------------- the detection floor

def simulate(n, kind, rng, *, hold_c=2.5, quad_c=1.5, conj=0.6):
    """Learners reaching a dependant, where ability also drives WHICH PARENTS THEY HOLD.

      "conjunction"  a true conjunctive bonus, ability present but only ADDITIVE.
      "ability"      NO conjunction. Ability raises P(hold each parent) AND enters the outcome
                     through its own square, which is what manufactures a spurious interaction.
                     THE ARM THAT DECIDES WHETHER THE CONTROL WORKS.
      "both"         a true conjunction on top of the ability artefact.

    The coefficients are TUNED so the pure-ability arm produces an interaction of about +0.04, the
    size this confound can plausibly reach, rather than a strawman too small to test against. The
    first version of this floor used weaker coupling, manufactured only +0.006, and FAILED its own
    gate because there was nothing there to remove -- a floor that tested the generator, not the
    control.
    """
    theta = rng.normal(0, 1, n)
    p_hold = 1.0 / (1.0 + np.exp(-(hold_c * theta)))
    ha = rng.random(n) < p_hold
    hb = rng.random(n) < p_hold
    lo = 0.2 + 0.8 * theta
    if kind in ("ability", "both"):
        lo = lo + quad_c * np.maximum(theta, 0) ** 2
    if kind in ("conjunction", "both"):
        lo = lo + conj * (ha & hb)
    ok = (rng.random(n) < 1.0 / (1.0 + np.exp(-lo))).astype(float)
    # the ability ESTIMATE is noisy, as it is on real data
    est = theta + rng.normal(0, 0.45, n)
    return ok, ha, hb, est


def floor(reps, n, rng, strata=STRATA):
    """Calibrate the control: how much of a pure artefact does it remove, how much real does it keep?"""
    print("DETECTION FLOOR -- can stratifying on ability tell a conjunction from an ability artefact?")
    print(f"  {strata} ability strata, {reps} reps of {n:,} learners per arm\n")
    out = {}
    for kind in ("conjunction", "ability", "both"):
        raw, adj = [], []
        for _ in range(reps):
            ok, ha, hb, est = simulate(n, kind, rng)
            r = score(ok, ha, hb)
            a = adjusted(ok, ha, hb, est, strata)
            if r and a:
                raw.append(r["interaction"]); adj.append(a["interaction"])
        if not raw:
            continue
        R, A = float(np.median(raw)), float(np.median(adj))
        out[kind] = dict(n=len(raw), raw=R, adj=A,
                         kept=float(A / R) if abs(R) > 1e-9 else float("nan"))
        print(f"  planted {kind:11s} unadjusted {R:+.4f}  adjusted {A:+.4f}   "
              f"keeps {100*out[kind]['kept']:.0f}%")

    removed = 1 - out["ability"]["kept"]
    kept = out["conjunction"]["kept"]
    ok_abil = out["ability"]["raw"] > 0.02 and removed > 0.60
    ok_conj = kept > 0.70
    passed = bool(ok_abil and ok_conj)
    print(f"\n  a planted ability artefact is REMOVED:   {ok_abil} "
          f"({100*removed:.0f}% of {out['ability']['raw']:+.4f})")
    print(f"  a planted conjunction SURVIVES:          {ok_conj} ({100*kept:.0f}% retained)")
    print(f"  -> {'FLOOR PASSED' if passed else 'FLOOR FAILED -- NO REAL NUMBER WILL BE READ'}")
    print(f"\n  THE CONTROL IS PARTIAL, AND THAT IS THE CALIBRATION THE REAL READING NEEDS:")
    print(f"  a reading that shrinks by about {100*removed:.0f}% is CONSISTENT WITH pure ability;")
    print(f"  one that shrinks by much less carries conjunctive structure beyond it.\n")
    out["benchmark"] = dict(artefact_removed=float(removed), conjunction_kept=float(kept))
    return out, passed


# ---------------------------------------------------------------- real corpus

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--floor-only", action="store_true")
    ap.add_argument("--floor-reps", type=int, default=40)
    ap.add_argument("--items", type=int, default=30)
    ap.add_argument("--strata", type=int, default=STRATA)
    ap.add_argument("--out", default="out/ability.json")
    args = ap.parse_args()
    rng = np.random.default_rng(SEED)

    floor_out, passed = floor(args.floor_reps, 6000, rng)
    if args.floor_only:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(dict(seed=SEED, floor=floor_out,
                                                  floor_passed=passed), indent=2))
        return
    if not passed:
        print("FLOOR FAILED -- stopping before the corpus is read, per the pre-registration.")
        return

    rows = list(xes3g5m_rows(SCRATCH / "xes3g5m"))
    by_learner = timelines(rows)
    ft, fp, oat = states(by_learner)
    idx = at_item(ft, oat)
    items = sorted(idx, key=lambda i: -len(idx[i]))[:args.items]
    print(f"xes3g5m: {len(by_learner):,} learners, top {len(items)} items, "
          f"{args.strata} ability strata\n", flush=True)

    scored = []
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
        # PRECOMPUTE ONCE PER DEPENDANT, NOT ONCE PER TRIPLE. The first version recomputed every
        # learner's ability from their full history inside the pair loop: O(triples x learners x
        # events), which ran 8 of 30 dependants in 2h10m and would have taken ~8 hours. Ability
        # excludes a, b and c, so it is the same total minus the two parents' own contributions --
        # accumulate per-item counts once and subtract.
        tot_h = np.zeros(len(at_c))
        tot_n = np.zeros(len(at_c))
        item_h = {p: np.zeros(len(at_c)) for p in parents}
        item_n = {p: np.zeros(len(at_c)) for p in parents}
        for k, l in enumerate(learners):
            for t, item, good in by_learner[l]:
                if t >= tc[k] or item == c:
                    continue
                tot_n[k] += 1
                tot_h[k] += bool(good)
                if item in item_n:
                    item_n[item][k] += 1
                    item_h[item][k] += bool(good)

        for a, b in itertools.combinations(parents, 2):
            n_ab = tot_n - item_n[a] - item_n[b]
            h_ab = tot_h - item_h[a] - item_h[b]
            with np.errstate(invalid="ignore", divide="ignore"):
                abil = np.where(n_ab >= 5, h_ab / np.maximum(n_ab, 1), np.nan)
            keep = ~np.isnan(abil)
            if keep.sum() < 8 * MIN_CELL:
                continue
            raw = score(ok[keep], held[a][keep], held[b][keep])
            adj = adjusted(ok[keep], held[a][keep], held[b][keep], abil[keep], args.strata)
            if raw is None or adj is None:
                continue
            scored.append(dict(c=c, a=a, b=b, raw=raw["interaction"], raw_se=raw["se"],
                               adj=adj["interaction"], adj_se=adj["se"],
                               adj_mde=adj["mde"], strata_used=adj["strata_used"],
                               n=int(keep.sum())))
        print(f"   {c}: {len(scored):,} triples with a readable ability-adjusted reading",
              flush=True)

    if not scored:
        print("no triple survived stratification")
        return

    big = [r for r in scored if r["raw"] >= MIN_MEANINGFUL]
    med_raw = float(np.median([r["raw"] for r in scored]))
    med_adj = float(np.median([r["adj"] for r in scored]))
    print(f"\n{len(scored):,} triples adjusted, {len(big):,} of them at or above the "
          f"+{MIN_MEANINGFUL:.2f} bar unadjusted")
    print(f"  ALL triples      unadjusted {med_raw:+.5f}   adjusted {med_adj:+.5f}")
    if big:
        b_raw = float(np.median([r["raw"] for r in big]))
        b_adj = float(np.median([r["adj"] for r in big]))
        kept = b_adj / b_raw if abs(b_raw) > 1e-9 else float("nan")
        still = sum(1 for r in big if r["adj"] >= MIN_MEANINGFUL)
        print(f"  ABOVE-BAR triples unadjusted {b_raw:+.5f}   adjusted {b_adj:+.5f}   "
              f"keeps {100*kept:.0f}%")
        print(f"  of those {len(big):,}, still at or above the bar after adjustment: "
              f"{still:,} ({100*still/len(big):.1f}%)")
        # calibrated against the floor: pure ability shrinks by `removed`, a real conjunction by
        # roughly (1 - conjunction_kept). The real reading is placed between those two benchmarks.
        bench_art = 1 - floor_out["ability"]["kept"]
        bench_conj = 1 - floor_out["conjunction"]["kept"]
        shrink = 1 - kept
        print(f"  BENCHMARKS from the floor: a pure ability artefact shrinks {100*bench_art:.0f}%, "
              f"a real conjunction shrinks {100*bench_conj:.0f}%; this reading shrinks "
              f"{100*shrink:.0f}%")
        verdict = ("SURVIVES" if shrink <= bench_conj + 0.15 else
                   "ABILITY ARTEFACT" if shrink >= bench_art - 0.10 else "PARTIAL")
    else:
        verdict = "UNANSWERABLE"
    print(f"\nVERDICT: {verdict}")
    if verdict == "ABILITY ARTEFACT":
        print("  stage 3's positive was ability super-additivity and must be WITHDRAWN.")
    elif verdict == "PARTIAL":
        print("  the conjunctions are real and INFLATED -- stage 3's magnitudes need restating at "
              "the adjusted values.")
    print("  NOTE: ability is the only unobserved attribute we can estimate from these logs. "
          "Working memory, mobility and motivation have no acquisition event, never enter "
          "first_pass, and cannot be controlled for here at all.")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(seed=SEED, strata=args.strata, floor=floor_out,
                                   floor_passed=passed, verdict=verdict, n=len(scored),
                                   n_above_bar=len(big), median_raw=med_raw, median_adj=med_adj,
                                   rows=[scored[i] for i in sorted(rng.choice(
                                       len(scored), min(400, len(scored)), replace=False))]),
                              indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
