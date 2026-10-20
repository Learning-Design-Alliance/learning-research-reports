"""STAGE 1. Is this programme's pairwise instrument blind to a conjunctive gate?

Nearly every instrument here is PAIRWISE -- overlap/positivity's drop, the background drop, IITA,
latent-edge's edge matrix, within-task, taxonomy-order, eprism-floor's LePPED. If the real constraint
is (A AND B) -> C, the single-parent contrast for A averages over learners who held B and learners
who did not, so it reports a DILUTED effect. The question this study answers is how diluted, and
whether the dilution is enough to drop it under the background an arbitrary ordered pair already
shows -- which is the threshold every real reading in this programme is judged against.

THE PRECISE CLAIM, STATED BEFORE THE RUN AND NARROWER THAN "INVISIBLE". A conjunctive gate is NOT
literally invisible to a pairwise contrast: among learners who mastered A, the ones who also hold B
can pass C, so the A-drop stays positive. It is ATTENUATED, roughly in proportion to how many
learners hold the co-parent. The claim is therefore quantitative: there is a region of (conjunction
strength, co-parent prevalence) where the pairwise reading falls below the background drop and is
recorded as null, while the INTERACTION statistic still fires. If that region exists and is not
exotic, then this programme's accumulated nulls are CONSISTENT WITH conjunctive structure rather
than with the absence of structure, and that is true whatever any corpus says.

THE TWO STATISTICS, ON THE SAME PLANTED DATA.

  PAIRWISE (what we already run)   drop(A->C) = mean outcome on C among learners who had mastered A
                                   when they reached it, minus those who had not.

  INTERACTION (the new one)        with m1 = held both, m2 = held A only, m3 = held B only,
                                   m4 = held neither,
                                        interaction = (m1 - m2) - (m3 - m4)
                                   the effect of B given A, minus the effect of B given not-A. A
                                   conjunctive gate makes this large. TWO INDEPENDENT SINGLE-PARENT
                                   GATES MAKE IT ZERO, which is what stops it being a relabelled
                                   main effect -- and the `additive` arm below tests exactly that.

PRE-REGISTERED VERDICTS, written before the run:

  BLIND SPOT CONFIRMED   the interaction statistic recovers the planted conjunctive gate above its
                         family-matched deranged null, AND there is a region of the sweep where the
                         pairwise drop falls below the background drop while it does so.
  PAIRWISE SUFFICES      the pairwise drop clears the background everywhere the interaction fires,
                         so conjunctive structure is not hidden from what we already run and A17 is
                         a lower priority than it looks.
  FLOOR FAILED           the interaction statistic cannot see its own planted gate, or it fires on
                         the ADDITIVE control where two independent single-parent gates are planted
                         and no conjunction exists. Either way no real corpus is read.

Synthetic only. No corpus is read by this file.

    python3 stage1_floor.py [--reps 30]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

SEED = 20260922
#: shaped like XES3G5M's readable core: thousands of learners, free choice of what to attempt
N_LEARNERS = 4000
#: a cell must hold this many learners to be read, exactly as studies/identifiability/overlap/positivity.py requires
MIN_CELL = 5
#: the background an ARBITRARY ordered pair already shows. Every real reading in this programme is
#: judged against this, not against zero: +0.1016 on ASSISTments, +0.1465 on ds1190. The midpoint is
#: the bar a pairwise reading has to clear to be recorded as anything at all.
BACKGROUND = 0.10
#: how many learners hold the co-parent B -- the axis the dilution runs along
CO_PARENT = (0.2, 0.4, 0.6, 0.8)
#: how hard the gate is. 0.0 = C is unreachable without both parents; 1.0 = no gate at all.
GATE = (0.0, 0.25, 0.5, 1.0)


def simulate(n, p_a, p_b, gate, kind, rng, *, base=0.55, ability=0.22):
    """Learners arriving at C having already held some combination of A and B.

    `kind` is what is planted:
      "conjunctive"  C is gated by A AND B together: the penalty applies unless BOTH are held.
      "additive"     A and B each help independently and there is no conjunction. THE CONTROL that
                     stops the interaction statistic being a relabelled main effect.
      "none"         neither parent matters.
    A learner-level ability term is included because without it the cells differ only by the gate,
    which is a world no real corpus resembles and which would flatter both statistics.
    """
    theta = rng.normal(0, ability, n)
    held_a = rng.random(n) < p_a
    held_b = rng.random(n) < p_b
    p = np.full(n, base) + theta
    if kind == "conjunctive":
        both = held_a & held_b
        p = np.where(both, p, p - (1 - gate) * 0.45)
    elif kind == "additive":
        # each parent contributes on its own, no interaction term at all
        p = p - (1 - gate) * 0.225 * (~held_a) - (1 - gate) * 0.225 * (~held_b)
    ok = (rng.random(n) < np.clip(p, 0.01, 0.99)).astype(float)
    return held_a, held_b, ok


def cells(held_a, held_b, ok):
    m = {}
    for name, sel in (("both", held_a & held_b), ("a_only", held_a & ~held_b),
                      ("b_only", ~held_a & held_b), ("neither", ~held_a & ~held_b)):
        m[name] = ok[sel] if sel.sum() >= MIN_CELL else None
    return m


def statistics(held_a, held_b, ok):
    """The pairwise drop we already run, and the interaction statistic, from the same data."""
    c = cells(held_a, held_b, ok)
    if any(v is None for v in c.values()):
        return None
    m1, m2 = float(np.mean(c["both"])), float(np.mean(c["a_only"]))
    m3, m4 = float(np.mean(c["b_only"])), float(np.mean(c["neither"]))
    pair_a = float(np.mean(ok[held_a]) - np.mean(ok[~held_a]))
    pair_b = float(np.mean(ok[held_b]) - np.mean(ok[~held_b]))
    return dict(pairwise_a=pair_a, pairwise_b=pair_b,
                interaction=(m1 - m2) - (m3 - m4),
                m_both=m1, m_a_only=m2, m_b_only=m3, m_neither=m4,
                n_min=int(min(len(v) for v in c.values())))


def deranged_null(held_a, held_b, ok, rng):
    """The treatment is assigned per LEARNER, so the learner is the unit shuffled.

    Each learner keeps their own outcome and inherits another learner's (A, B) state, by a
    derangement rather than a permutation -- a permutation leaves 1/n of learners holding their own
    pair, which scored a spurious p = 0.006 elsewhere in this programme.
    """
    n = len(ok)
    p = rng.permutation(n)
    while True:
        fixed = np.flatnonzero(p == np.arange(n))
        if not len(fixed):
            break
        if len(fixed) == 1:
            o = rng.integers(0, n - 1); o += o >= fixed[0]
            p[[fixed[0], o]] = p[[o, fixed[0]]]
        else:
            p[fixed] = p[np.roll(fixed, 1)]
    return statistics(held_a[p], held_b[p], ok)


def arm(kind, p_b, gate, reps, rng):
    acc, nulls = [], []
    for _ in range(reps):
        ha, hb, ok = simulate(N_LEARNERS, 0.5, p_b, gate, kind, rng)
        got = statistics(ha, hb, ok)
        if got:
            acc.append(got)
            nb = deranged_null(ha, hb, ok, rng)
            if nb:
                nulls.append(nb["interaction"])
    if not acc:
        return None
    g = lambda k: float(np.median([x[k] for x in acc]))  # noqa: E731
    return dict(kind=kind, co_parent=p_b, gate=gate, reps=len(acc),
                pairwise_a=g("pairwise_a"), pairwise_b=g("pairwise_b"),
                interaction=g("interaction"),
                interaction_null=float(np.median(nulls)) if nulls else float("nan"),
                interaction_null_hi=float(np.percentile(nulls, 97.5)) if nulls else float("nan"),
                n_min=int(np.median([x["n_min"] for x in acc])))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--out", default="out/stage1.json")
    args = ap.parse_args()
    rng = np.random.default_rng(SEED)

    print("STAGE 1 -- is the pairwise instrument blind to a conjunctive gate?")
    print(f"  {N_LEARNERS:,} learners per rep, {args.reps} reps per arm, cell floor {MIN_CELL}")
    print(f"  a pairwise drop is recorded as a finding only above the BACKGROUND an arbitrary "
          f"ordered pair already shows: {BACKGROUND:+.3f}\n")

    rows = []
    print(f"{'planted':<12} {'P(B)':>5} {'gate':>5} {'pair A':>9} {'pair B':>9} "
          f"{'interaction':>12} {'null hi':>9}   reading")
    for kind in ("conjunctive", "additive", "none"):
        for p_b in CO_PARENT:
            for gate in GATE:
                if kind == "none" and gate != 0.0:
                    continue
                r = arm(kind, p_b, gate, args.reps, rng)
                if not r:
                    continue
                r["pairwise_reads_null"] = bool(abs(r["pairwise_a"]) < BACKGROUND)
                r["interaction_fires"] = bool(r["interaction"] > r["interaction_null_hi"])
                rows.append(r)
                tag = ("PAIRWISE NULL, INTERACTION FIRES" if r["pairwise_reads_null"] and r["interaction_fires"]
                       else "both fire" if r["interaction_fires"]
                       else "pairwise only" if not r["pairwise_reads_null"]
                       else "neither")
                print(f"{kind:<12} {p_b:>5.1f} {gate:>5.2f} {r['pairwise_a']:>+9.4f} "
                      f"{r['pairwise_b']:>+9.4f} {r['interaction']:>+12.4f} "
                      f"{r['interaction_null_hi']:>+9.4f}   {tag}")

    conj = [r for r in rows if r["kind"] == "conjunctive" and r["gate"] < 1.0]
    add = [r for r in rows if r["kind"] == "additive" and r["gate"] < 1.0]
    none = [r for r in rows if r["kind"] == "none"]

    recovers = any(r["interaction_fires"] for r in conj)
    #: the control that stops this being a relabelled main effect: two INDEPENDENT single-parent
    #: gates must NOT produce an interaction
    clean = not any(r["interaction_fires"] for r in add) and not any(r["interaction_fires"] for r in none)
    blind = [r for r in conj if r["pairwise_reads_null"] and r["interaction_fires"]]

    print(f"\n  interaction recovers a planted conjunction:        {recovers}")
    print(f"  interaction stays silent on ADDITIVE and NONE:     {clean} "
          f"({sum(r['interaction_fires'] for r in add)} of {len(add)} additive arms fired, "
          f"{sum(r['interaction_fires'] for r in none)} of {len(none)} none arms)")
    print(f"  arms where PAIRWISE reads null but INTERACTION fires: {len(blind)} of {len(conj)}")

    if not (recovers and clean):
        verdict = "FLOOR FAILED"
    elif blind:
        verdict = "BLIND SPOT CONFIRMED"
    else:
        verdict = "PAIRWISE SUFFICES"
    print(f"\nVERDICT: {verdict}")
    if blind:
        print("  the region where a real conjunction would be recorded as a null by this programme's"
              " existing instruments:")
        for r in sorted(blind, key=lambda z: (z["gate"], z["co_parent"])):
            print(f"    gate {r['gate']:.2f}, co-parent prevalence {r['co_parent']:.1f}: "
                  f"pairwise {r['pairwise_a']:+.4f} (under {BACKGROUND:+.3f}), "
                  f"interaction {r['interaction']:+.4f} vs null hi {r['interaction_null_hi']:+.4f}")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(seed=SEED, n_learners=N_LEARNERS, reps=args.reps,
                                   min_cell=MIN_CELL, background=BACKGROUND,
                                   verdict=verdict, rows=rows), indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
