"""
Does a surmise relation constrain the edge space, or does it assert into cells the corpus cannot
read?

The claim that put this study on the board: knowledge-space methods -- IITA and its relatives --
narrow the space of admissible graphs, so they belong upstream of the assay as a constraint
generator. That is a real hope. It is also testable, and the test is cheap, because IITA and the
positivity audit read THE SAME CELL from opposite ends:

    IITA asserts "A precedes B" when few learners solved B without solving A -- a LOW
    COUNTEREXAMPLE COUNT.

    positivity.py can decide "A gates B" only when enough learners reached B WITHOUT holding A --
    a LARGE IDENTIFYING CELL.

Those are the same learners. A corpus where nobody meets B without A gives IITA its strongest
evidence for the edge and gives the audit nothing to read at all. Where a tutor gates, the
counterexample count is structurally near zero for EVERY pair, so IITA asserts edges everywhere
and the audit can decide none of them.

So: run both over the same items and the same learners, and cross-tabulate IITA's assertion against
the edge state (`shared/edge_state.py`). Three outcomes matter, and they are pre-registered below:

    asserted & SUPPORTED      IITA found an edge the corpus independently confirms -- a constraint
    asserted & CONTRADICTED   IITA found an edge the corpus refutes on a powered test -- worse than
                              no constraint, it is a wrong one
    asserted & UNKNOWN        IITA found an edge the corpus cannot speak to either way -- the
                              assertion is a PRIOR, not a constraint derived from this data

PRE-REGISTERED VERDICT, written before any real number was read:

    >= 90% of IITA-asserted edges landing in UNKNOWN
        "surmise output is a prior wearing a constraint's clothes" -- it must be labelled as a
        prior downstream, and may not be used to close the edge space
    >= 25% of asserted edges decided (SUPPORTED or CONTRADICTED)
        "surmise output is a checkable claim on this corpus" -- the data can speak to it
    anything between
        "mostly undecidable" -- reported as such, no rescue

WHAT THE FLOOR TOOK AWAY. It licensed the first reading and withheld a second one this study was
originally going to make. The audit returns only ~35% of planted edges as SUPPORTED when the
dependant has several prerequisites, because a pairwise drop tests ONE arm of a conjunctive gate:
the learners who hold A are mostly missing something else B needs, so both cells sit at the floor
and the drop disappears (100% recovered at fan-in 1, 22% at fan-in 4+). So CONTRADICTED beside an
IITA edge does NOT mean IITA is wrong, and the confirmed/refuted split is printed but excluded from
the verdict. Only the UNKNOWN share is read.

DETECTION FLOOR (`floor` mode, and it runs first). The cross-tab is only readable if it CAN show
agreement. So the same join runs on synthetic data with a planted gate, randomised item order and
enough learners: there the audit must decide most pairs and return the planted edges as SUPPORTED,
and IITA's assertions must land mostly in decided cells. A cross-tab that cannot show agreement
where agreement was planted says nothing about a corpus where it shows none.

Both sides are restricted to the SAME learners -- those who touched every item in the set -- because
otherwise IITA's "did not solve B" silently includes "was never asked B", which is the mistake
`mooccubex_concept_iita.py` was built to avoid, and the two methods would not be reading the same
population.

    python3 overlap_iita.py floor
    python3 overlap_iita.py real junyi|assist|ds1190 [--sets 8] [--items N] [--out out/x.json]

Raw exports stay outside the repo (DataShop and ASSISTments both forbid redistribution); only the
aggregate counts printed here are ever committed.

DIRECTION: a -> b means a is a prerequisite of b: IITA's pair (i, j) is asserted when few learners
solved j without i (counterexamples b[i][j], studies/identifiability/learning-structure/iita.py, the
DAKS convention), and positivity.classify((a, b)) reads b's outcome split by what the learner held in
a. The join is only meaningful if the two agree, which the floor checks against the planted relation
(this file's own generator: an unmet prerequisite a lowers b).

Reversed-arrow control added 2026-09-24. On the floor's hard arm, IITA's precision against the planted
relation must beat its reverse (require_claimed: otherwise IITA's pairs are joined to the audit's
states backwards). On real data the share of asserted edges the audit SUPPORTS, pooled over sets, is
scored against the reversed assertions and reported beside the UNKNOWN share the verdict reads.
"""

from __future__ import annotations

import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "studies/identifiability/overlap"))
sys.path.insert(0, str(HERE.parents[2] / "studies/identifiability/learning-structure"))
sys.path.insert(0, str(HERE.parents[2]))

from iita import corrected_iita  # noqa: E402
from positivity import MIN_CELL, at_item, classify, mde, states, timelines  # noqa: E402
from shared.edge_state import (CLAIMED_EFFECT, CONTRADICTED, SUPPORTED,  # noqa: E402
                               UNKNOWN, classify_edge)
from shared.direction import require_claimed, reversed_arrow  # noqa: E402
from shared.reachability import reachability  # noqa: E402
from shared.seeds import arm_seed  # noqa: E402

try:
    from build_matrix import LOADERS
except ImportError:  # only needed in `real` mode
    sys.path.insert(0, str(HERE.parents[2] / "studies/identifiability/latent-shape"))
    from build_matrix import LOADERS  # noqa: E402

SEED = 20260921

#: the floor's two planted gates. The soft one costs the dependant 0.30 -- well above
#: CLAIMED_EFFECT, so a powered corpus has to see it, but NOT a quasi-order: a learner without the
#: prerequisite still passes most of the time. The hard one nearly forbids the dependant, which is
#: the deterministic structure IITA is built for. Both arms are needed and they check different
#: things: see `floor()`.
PLANT_SOFT = 0.30
PLANT_HARD = 0.60

#: floor thresholds, fixed before the floor was run
FLOOR_MIN_DECIDED = 0.50      # share of ordered pairs the audit must decide on planted data
FLOOR_MIN_PLANTED_SUPPORTED = 0.50   # share of planted edges coming back SUPPORTED (hard arm)
FLOOR_MIN_ASSERTED_DECIDED = 0.50    # share of IITA assertions landing in a decided cell

#: verdict thresholds, likewise pre-registered
PRIOR_SHARE = 0.90
CONSTRAINT_SHARE = 0.25


# --------------------------------------------------------------------------- the join

def mastery_patterns(items: list[str], learners: list[str], first_pass) -> list[set[int]]:
    """IITA's input: for each learner, the set of item indices they ever got right."""
    idx = {it: i for i, it in enumerate(items)}
    return [{idx[it] for it in first_pass[u] if it in idx} for u in learners]


def positivity_states(items, learners, by_learner):
    """The audit's per-ordered-pair state, over exactly these learners and items.

    `learners` is passed explicitly because the study reads it two ways and the difference is the
    point. Restricted to IITA's complete-case learners, both methods read one population -- but the
    restriction is MY choice and it destroys most of the corpus's power, so an UNKNOWN there could
    be my doing rather than the corpus's. Run again over every learner who reached the item, it is
    the corpus answering with everything it has. Both are reported.
    """
    keep = set(items)
    sub = {u: [r for r in by_learner[u] if r[1] in keep] for u in learners}
    first_touch, first_pass, outcome_at_touch = states(sub)
    idx = at_item(first_touch, outcome_at_touch)
    out = {}
    for a in items:
        for b in items:
            if a == b:
                continue
            c = classify((a, b), first_touch, first_pass, outcome_at_touch, idx)
            n_m, n_f = len(c["mastered"]), len(c["failed"])
            p_m = float(np.mean(c["mastered"])) if n_m else float("nan")
            p_f = float(np.mean(c["failed"])) if n_f else float("nan")
            m = mde(n_m, n_f, p_m) if n_m and not math.isnan(p_m) else None
            obs = (p_m - p_f) if not (math.isnan(p_m) or math.isnan(p_f)) else None
            state, _why = classify_edge(m, obs)      # provisional; the gate below may move it
            out[(a, b)] = dict(state=state, mde=m, observed=obs, n_mastered=n_m, n_failed=n_f)

    # A null is negative evidence only where this learner set could have falsified it, and a merge
    # node has to be READABLE and POWERED for that. Run over the would-be contradictions alone --
    # falsifiability bears on no other branch, and reachability is O(pairs x learners x units).
    # It runs inside this function so BOTH readings the study reports (complete-case learners and
    # every learner) are gated on their own learner set rather than on one borrowed from the other.
    contra = [k for k, v in out.items() if v["state"] == CONTRADICTED]
    if contra:
        tl = {learner: {u: ((fp[u], True) if u in fp else (t, False))
                        for u, t in first_touch[learner].items()}
              for learner, fp in first_pass.items()}
        reach_of = reachability(tl, contra, min_cell=MIN_CELL, claimed=CLAIMED_EFFECT)
        for k in contra:
            ok = reach_of[k]["status"] == "FALSIFIABLE"
            rec = out[k]
            rec["falsifiable"] = ok
            rec["readable_merge_nodes"] = reach_of[k]["readable_nodes"]
            rec["state"] = classify_edge(rec["mde"], rec["observed"], falsifiable=ok)[0]
    return out


def shape(items, asserted: set[tuple[str, str]]) -> dict:
    """What the asserted relation LOOKS like, before anything is joined to it.

    Two numbers, because a relation can fail to constrain without ever being checked against data.
    `density` is the share of ordered pairs asserted: a relation covering most of them has not
    narrowed the edge space it was supposed to narrow. `bidirectional` is the share of unordered
    pairs where BOTH directions are asserted -- IITA estimates a quasi-order, which is allowed to
    contain (i,j) and (j,i) together, but a pair asserted both ways is an equivalence, not a
    prerequisite claim, and cannot orient anything downstream.
    """
    n = len(items)
    ordered = n * (n - 1)
    both = sum(1 for i in range(n) for j in range(i + 1, n)
               if (items[i], items[j]) in asserted and (items[j], items[i]) in asserted)
    return dict(ordered=ordered, asserted=len(asserted),
                density=len(asserted) / ordered if ordered else 0.0,
                bidirectional=both, unordered=n * (n - 1) // 2)


def crosstab(items, asserted: set[tuple[str, str]], st: dict) -> dict:
    """asserted x state, over every ordered pair of the item set."""
    tab = {True: {SUPPORTED: 0, CONTRADICTED: 0, UNKNOWN: 0},
           False: {SUPPORTED: 0, CONTRADICTED: 0, UNKNOWN: 0}}
    for pair, row in st.items():
        tab[pair in asserted][row["state"]] += 1
    return tab


def merge(tabs: list[dict]) -> dict:
    out = {True: {SUPPORTED: 0, CONTRADICTED: 0, UNKNOWN: 0},
           False: {SUPPORTED: 0, CONTRADICTED: 0, UNKNOWN: 0}}
    for t in tabs:
        for k in (True, False):
            for s in out[k]:
                out[k][s] += t[k][s]
    return out


def print_tab(tab: dict) -> None:
    tot = {k: sum(tab[k].values()) for k in (True, False)}
    print(f"\n   {'':<22}{'supported':>11}{'contradicted':>14}{'unknown':>10}{'all':>9}")
    for k, label in ((True, "IITA asserts edge"), (False, "IITA is silent")):
        r = tab[k]
        print(f"   {label:<22}{r[SUPPORTED]:>11,}{r[CONTRADICTED]:>14,}"
              f"{r[UNKNOWN]:>10,}{tot[k]:>9,}")
    if tot[True]:
        r = tab[True]
        dec = r[SUPPORTED] + r[CONTRADICTED]
        print(f"\n   of the {tot[True]:,} edges IITA asserts:")
        print(f"      unknown to the corpus   {r[UNKNOWN]:>7,}  ({r[UNKNOWN] / tot[True]:>6.1%})")
        print(f"      decided                 {dec:>7,}  ({dec / tot[True]:>6.1%})")
        if dec:
            print(f"         confirmed            {r[SUPPORTED]:>7,}  "
                  f"({r[SUPPORTED] / dec:>6.1%} of the decided)")
            print(f"         refuted              {r[CONTRADICTED]:>7,}  "
                  f"({r[CONTRADICTED] / dec:>6.1%} of the decided)")


def verdict(tab: dict) -> str:
    """The pre-registered verdict, on the one reading the floor licensed.

    The floor withheld the accuracy reading -- the audit recovers only a third of planted edges
    into multi-prerequisite dependants, so a CONTRADICTED beside an IITA edge does not establish
    that the edge is wrong. The confirmed/refuted split is still printed, because hiding it would
    be worse, but it does not enter the verdict.
    """
    tot = sum(tab[True].values())
    if not tot:
        return "IITA asserted nothing here -- no verdict"
    r = tab[True]
    unknown = r[UNKNOWN] / tot
    decided = (r[SUPPORTED] + r[CONTRADICTED]) / tot
    if unknown >= PRIOR_SHARE:
        return (f"PRIOR, NOT A CONSTRAINT: {unknown:.1%} of asserted edges land on pairs this "
                f"corpus cannot decide either way")
    if decided >= CONSTRAINT_SHARE:
        return (f"DECIDABLE: the corpus can speak to {decided:.1%} of the asserted edges, so they "
                f"are checkable claims here rather than a prior")
    return (f"MOSTLY UNDECIDABLE: {unknown:.1%} unknown, {decided:.1%} decided -- short of the "
            f"{PRIOR_SHARE:.0%} that would settle it, and short of the {CONSTRAINT_SHARE:.0%} "
            f"a usable constraint needs")


# --------------------------------------------------------------------------- the floor

def planted_corpus(rng: random.Random, n_learners: int, items: int, gate: float):
    """An event log with a known prerequisite relation and NO curriculum gating.

    Order is randomised per learner, which is the whole point: it populates the identifying cell the
    audit needs and, at the same time, gives IITA the counterexamples it uses. A gated corpus would
    starve one and feed the other, which is the asymmetry the real run is looking for.
    """
    rel = set()
    for j in range(items):
        for i in range(j):
            if rng.random() < 0.15:
                rel.add((i, j))
    # transitive closure -- IITA estimates a quasi-order, so the truth has to be one
    for _ in range(items):
        grown = rel | {(a, d) for a, b in rel for c, d in rel if b == c and a != d}
        if grown == rel:
            break
        rel = grown
    prereqs = defaultdict(set)
    for a, b in rel:
        prereqs[b].add(a)

    base = [0.55 + 0.25 * rng.random() for _ in range(items)]
    rows, t = [], 0
    for u in range(n_learners):
        learner = f"L{u:05d}"
        ability = rng.gauss(0, 0.08)
        passed = set()
        for it in rng.sample(range(items), items):
            t += 1
            p = base[it] + ability - (gate if prereqs[it] - passed else 0.0)
            ok = rng.random() < min(max(p, 0.02), 0.98)
            rows.append((learner, f"i{it:02d}", ok, f"{t:09d}", False, False))
            if ok:
                passed.add(it)
    names = [f"i{it:02d}" for it in range(items)]
    truth = {(names[a], names[b]) for a, b in rel}
    return rows, names, truth


def floor_arm(label: str, gate: float, note: str) -> dict:
    rng = random.Random(arm_seed(SEED, label))
    rows, items, truth = planted_corpus(rng, 3000, 14, gate)
    print(f"\n   -- {label} arm, gate {gate:.2f}: {note}")
    print(f"      3,000 learners, {len(items)} items, randomised order, "
          f"{len(truth)} true edges of {len(items) * (len(items) - 1)} ordered pairs")

    by_learner = timelines(rows)
    learners = sorted(by_learner)
    st = positivity_states(items, learners, by_learner)
    _ft, first_pass, _oat = states({u: by_learner[u] for u in learners})
    rel, _diff, _err = corrected_iita(mastery_patterns(items, learners, first_pass), len(items))
    asserted = {(items[i], items[j]) for i, j in rel}

    tab = crosstab(items, asserted, st)
    print_tab(tab)

    hit = len(asserted & truth)
    flip = reversed_arrow(lambda t: len(asserted & t) / len(asserted) if asserted else 0.0, truth)
    print(f"      reversed-arrow control: IITA precision vs planted {flip['claimed']:.1%}, "
          f"vs its reverse {flip['reversed']:.1%} -> {flip['verdict']}")
    # Fan-in diagnostic. A pairwise comparison tests ONE arm of what may be a conjunctive gate: for
    # a dependant needing four prerequisites, the learners who hold A are mostly missing something
    # else, so both cells sit at the floor and the drop the audit measures is not the drop that was
    # planted. This is the reason the recall criterion below fails, and it is a property of the
    # instrument rather than of this join.
    fan = defaultdict(int)
    for a, b in truth:
        fan[b] += 1
    by_fan = {}
    for lo, hi, key in ((1, 1, "1"), (2, 3, "2-3"), (4, 99, "4+")):
        grp = [pr for pr in truth if lo <= fan[pr[1]] <= hi]
        if grp:
            drops = [st[pr]["observed"] for pr in grp if st[pr]["observed"] is not None]
            by_fan[key] = dict(
                edges=len(grp),
                supported=sum(1 for pr in grp if st[pr]["state"] == SUPPORTED) / len(grp),
                median_drop=float(np.median(drops)) if drops else None)
    print("      planted edges recovered, by how many prerequisites the dependant has:")
    for key, row in by_fan.items():
        d = "  --  " if row["median_drop"] is None else f"{row['median_drop']:+.3f}"
        print(f"         {key:<4} {row['edges']:>3} edges   {row['supported']:>6.1%} SUPPORTED"
              f"   median observed drop {d}")

    return dict(
        by_fan=by_fan,
        label=label, gate=gate, truth=len(truth), asserted=len(asserted),
        # IITA against the planted relation, reported separately from the join: a join that works
        # and an estimator that is accurate are two different claims and must not be read off one
        # number.
        precision=hit / len(asserted) if asserted else 0.0,
        recall=hit / len(truth) if truth else 0.0,
        decided=sum(1 for r in st.values() if r["state"] != UNKNOWN) / len(st),
        planted_supported=(sum(1 for p in truth if st[p]["state"] == SUPPORTED) / len(truth)
                           if truth else 0.0),
        asserted_decided=((sum(1 for p in asserted if st[p]["state"] != UNKNOWN) / len(asserted))
                          if asserted else 0.0),
        asserted_supported=tab[True][SUPPORTED],
        asserted_contradicted=tab[True][CONTRADICTED],
        reversed_arrow=flip,
    )


def floor() -> int:
    """Two arms, because the first version of this floor passed while leaving a cell unreachable.

    It planted a 0.30 gate, confirmed the audit decided every pair and that IITA's assertions all
    landed in decided cells, and called that enough. But every assertion landed in CONTRADICTED and
    none in SUPPORTED -- so nothing in that run established that `asserted & SUPPORTED` can be
    reached AT ALL. A cross-tab with an unreachable cell would report "IITA confirms nothing" on
    real data no matter what the data held, and that reading would be an artefact.

    A 0.30 gate is not a quasi-order: a learner without the prerequisite still passes most of the
    time, so counterexamples stay common and IITA ranks pairs by difficulty instead. The hard arm
    plants a gate that nearly forbids the dependant -- IITA's own assumption -- and requires the
    confirmed cell to fill there. The soft arm keeps the earlier check that assertions resolve.
    """
    print("DETECTION FLOOR -- can this cross-tab show agreement where agreement was planted?")
    soft = floor_arm("soft", PLANT_SOFT,
                     "a real but probabilistic gate -- not the structure IITA assumes")
    hard = floor_arm("hard", PLANT_HARD,
                     "a near-deterministic gate -- IITA's own home ground")

    print(f"\n   {'':<34}{'soft':>9}{'hard':>9}   floor")
    for key, name, lo in (
            ("decided", "pairs the audit decides", FLOOR_MIN_DECIDED),
            ("planted_supported", "planted edges SUPPORTED", FLOOR_MIN_PLANTED_SUPPORTED),
            ("asserted_decided", "assertions in a decided cell", FLOOR_MIN_ASSERTED_DECIDED)):
        print(f"   {name:<34}{soft[key]:>8.1%}{hard[key]:>9.1%}   {lo:.0%}")
    print(f"   {'IITA precision vs planted truth':<34}{soft['precision']:>8.1%}"
          f"{hard['precision']:>9.1%}   --")
    print(f"   {'IITA recall vs planted truth':<34}{soft['recall']:>8.1%}"
          f"{hard['recall']:>9.1%}   --")
    print(f"   {'asserted & SUPPORTED (must be >0)':<34}{soft['asserted_supported']:>8,}"
          f"{hard['asserted_supported']:>9,}   >0 on hard")

    # Each check is tied to the reading it licenses, so a failed check withdraws a reading rather
    # than being argued away. The thresholds were fixed before the floor ran and none moved after.
    checks = [
        ("audit decides most pairs, both arms", "sanity",
         soft["decided"] >= FLOOR_MIN_DECIDED and hard["decided"] >= FLOOR_MIN_DECIDED),
        ("assertions resolve to a state, both arms", "unknown-share",
         soft["asserted_decided"] >= FLOOR_MIN_ASSERTED_DECIDED
         and hard["asserted_decided"] >= FLOOR_MIN_ASSERTED_DECIDED),
        ("the confirmed cell is reachable", "unknown-share",
         hard["asserted_supported"] > 0),
        ("the refuted cell is reachable", "unknown-share",
         soft["asserted_contradicted"] > 0 or hard["asserted_contradicted"] > 0),
        ("planted edges come back SUPPORTED on the hard arm", "accuracy",
         hard["planted_supported"] >= FLOOR_MIN_PLANTED_SUPPORTED),
    ]
    print()
    for name, reading, ok in checks:
        print(f"   [{'ok' if ok else 'FAIL'}] {name:<52} licenses: {reading}")

    require_claimed(hard["reversed_arrow"], "IITA orientation against the planted relation (hard arm)")
    unknown_ok = all(ok for _n, r, ok in checks if r == "unknown-share")
    accuracy_ok = all(ok for _n, r, ok in checks if r == "accuracy")
    print(f"\n   READING 1 -- prior vs constraint, from the UNKNOWN share: "
          f"{'LICENSED' if unknown_ok else 'WITHHELD'}")
    print(f"   READING 2 -- confirmed vs refuted as IITA's accuracy: "
          f"{'LICENSED' if accuracy_ok else 'WITHHELD'}")
    if not accuracy_ok:
        print("      withheld because the audit recovers only "
              f"{hard['planted_supported']:.0%} of planted edges when the dependant has several")
        print("      prerequisites: a pairwise drop tests one arm of a conjunctive gate and both")
        print("      cells sit at the floor. So on real data CONTRADICTED against an IITA edge")
        print("      cannot be read as 'IITA is wrong' -- only the UNKNOWN share is safe to read.")
    Path("out/floor.json").write_text(json.dumps(
        dict(soft=soft, hard=hard, reading_unknown_share=unknown_ok,
             reading_accuracy=accuracy_ok), indent=1))
    return 0 if unknown_ok else 1


# --------------------------------------------------------------------------- the real run

def item_sets(by_learner, n_sets: int, size: int, pool: int = 60):
    """Sets of `size` items chosen to keep as many complete-case learners as possible.

    Complete case, because IITA reads "did not solve B" off the response pattern and a learner who
    was never asked B is not a counterexample to anything. Greedy: start from the most-attempted
    item left in the pool, then add whichever item costs the fewest learners.
    """
    touched = defaultdict(set)
    for u, rows in by_learner.items():
        for _t, item, _ok in rows:
            touched[item].add(u)
    ranked = sorted(touched, key=lambda i: -len(touched[i]))[:pool]
    used, out = set(), []
    for _ in range(n_sets):
        left = [i for i in ranked if i not in used]
        if len(left) < size:
            break
        chosen = [left[0]]
        cur = set(touched[left[0]])
        while len(chosen) < size:
            best, best_cur = None, None
            for cand in left:
                if cand in chosen:
                    continue
                nxt = cur & touched[cand]
                if best_cur is None or len(nxt) > len(best_cur):
                    best, best_cur = cand, nxt
            if best is None:
                break
            chosen.append(best)
            cur = best_cur
        used |= set(chosen)
        out.append((sorted(chosen), sorted(cur)))
    return out


#: a set needs at least this many complete-case learners to be worth running IITA over
MIN_COMPLETE = 200


def choose_size(by_learner, n_sets: int, sizes=(20, 16, 12, 10, 8)):
    """Largest item-set size whose first set still holds MIN_COMPLETE complete-case learners.

    Set size is a power decision, made here on learner counts alone and BEFORE any state is
    computed, so it cannot be tuned against the answer. It has to be made somehow: 20 items leaves
    33 complete-case learners on Junyi, and a join over 33 learners reports UNKNOWN everywhere for
    reasons that have nothing to do with the corpus.
    """
    for size in sizes:
        sets = item_sets(by_learner, n_sets, size)
        if sets and len(sets[0][1]) >= MIN_COMPLETE:
            return size, sets
    return sizes[-1], item_sets(by_learner, n_sets, sizes[-1])


def real(name: str, n_sets: int, size: int | None, out_path: Path | None) -> int:
    print(f"IITA against the positivity state: {name}")
    by_learner = timelines(LOADERS[name]())
    print(f"   {len(by_learner):,} learners")

    if size is None:
        size, sets = choose_size(by_learner, n_sets)
        print(f"   item-set size {size}, the largest holding {MIN_COMPLETE}+ complete-case learners")
    else:
        sets = item_sets(by_learner, n_sets, size)
    if not sets:
        print("   no item set of this size has complete-case learners -- nothing to join")
        return 1

    everyone = sorted(by_learner)
    tabs_same, tabs_all, per_set, shapes = [], [], [], []
    # pooled for the reversed-arrow control; item sets are disjoint, so pairs never collide
    all_asserted, pooled_same, pooled_all = set(), {}, {}
    for k, (items, learners) in enumerate(sets):
        if len(learners) < 50:
            print(f"   set {k}: only {len(learners)} complete-case learners -- skipped")
            continue
        _ft, first_pass, _oat = states({u: by_learner[u] for u in learners})
        pats = mastery_patterns(items, learners, first_pass)
        rel, _diff, _err = corrected_iita(pats, len(items))
        asserted = {(items[i], items[j]) for i, j in rel}

        sh = shape(items, asserted)
        shapes.append(sh)
        st_same = positivity_states(items, learners, by_learner)
        st_all = positivity_states(items, everyone, by_learner)
        t_same, t_all = crosstab(items, asserted, st_same), crosstab(items, asserted, st_all)
        all_asserted |= asserted
        pooled_same.update(st_same)
        pooled_all.update(st_all)
        tabs_same.append(t_same)
        tabs_all.append(t_all)
        per_set.append(dict(items=len(items), complete_case=len(learners),
                            asserted=len(asserted), shape=sh,
                            same_population={k2: t_same[True][k2]
                                             for k2 in (SUPPORTED, CONTRADICTED, UNKNOWN)},
                            all_learners={k2: t_all[True][k2]
                                          for k2 in (SUPPORTED, CONTRADICTED, UNKNOWN)}))
        print(f"   set {k}: {len(items)} items, {len(learners):,} complete-case learners, "
              f"IITA asserts {len(asserted):,} of {sh['ordered']:,} ordered pairs "
              f"({sh['density']:.0%}), both directions on {sh['bidirectional']}"
              f"/{sh['unordered']} unordered pairs")

    if not tabs_same:
        print("   no usable set")
        return 1

    same, allpop = merge(tabs_same), merge(tabs_all)
    tot_ordered = sum(x["ordered"] for x in shapes)
    tot_asserted = sum(x["asserted"] for x in shapes)
    tot_bi = sum(x["bidirectional"] for x in shapes)
    tot_un = sum(x["unordered"] for x in shapes)
    print(f"\n   THE RELATION ITSELF, before any join")
    print(f"      ordered pairs asserted      {tot_asserted:,} of {tot_ordered:,} "
          f"({tot_asserted / max(tot_ordered, 1):.0%})")
    print(f"      asserted in BOTH directions {tot_bi:,} of {tot_un:,} unordered pairs "
          f"({tot_bi / max(tot_un, 1):.0%})   -- an equivalence, not a prerequisite")
    out = {}
    for label, tab, note in (
            ("same population", same,
             "both methods on IITA's complete-case learners -- the like-for-like join"),
            ("every learner", allpop,
             "the audit on everyone who reached the item -- the corpus at full strength, "
             "so an UNKNOWN here is the corpus's and not the join's")):
        print(f"\n   POOLED over {len(tabs_same)} item sets, {label.upper()}")
        print(f"   ({note})")
        print_tab(tab)
        v = verdict(tab)
        print(f"\n   VERDICT ({label}): {v}")
        out[label] = dict(crosstab={"asserted": tab[True], "silent": tab[False]}, verdict=v)

    def share(st, state):
        return lambda es: (sum(1 for p in es if st[p]["state"] == state) / len(es)) if es else 0.0

    flip = {}
    for label, st in (("same population", pooled_same), ("every learner", pooled_all)):
        f = reversed_arrow(share(st, SUPPORTED), all_asserted)
        f["unknown_claimed"] = share(st, UNKNOWN)(all_asserted)
        f["unknown_reversed"] = share(st, UNKNOWN)({(b, a) for a, b in all_asserted})
        flip[label] = f
        print(f"\n   reversed-arrow control ({label}): SUPPORTED share of asserted edges "
              f"{f['claimed']:.1%}, of their reverses {f['reversed']:.1%} -> {f['verdict']}; "
              f"unknown {f['unknown_claimed']:.1%} vs {f['unknown_reversed']:.1%}")

    if out_path:
        out_path.write_text(json.dumps(dict(
            dataset=name, sets=len(tabs_same), item_set_size=size,
            claimed_effect=CLAIMED_EFFECT, populations=out, reversed_arrow=flip,
            relation=dict(ordered=tot_ordered, asserted=tot_asserted,
                          density=tot_asserted / max(tot_ordered, 1),
                          bidirectional=tot_bi, unordered=tot_un),
            per_set=per_set), indent=1))
        print(f"\n   -> {out_path}")
    return 0


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "floor"
    if mode == "floor":
        return floor()
    name = sys.argv[2]
    n_sets = int(sys.argv[sys.argv.index("--sets") + 1]) if "--sets" in sys.argv else 8
    size = int(sys.argv[sys.argv.index("--items") + 1]) if "--items" in sys.argv else None
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else None
    return real(name, n_sets, size, out)


if __name__ == "__main__":
    raise SystemExit(main())
