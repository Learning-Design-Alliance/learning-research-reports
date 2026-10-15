"""
Can this dataset answer a prerequisite question at all -- before anything is fitted to it?

Every structural null this programme has reported shares an untested assumption: that the data
contains learners who attempted the dependant WITHOUT holding the prerequisite. A gate is a claim
about what happens in that cell. A mastery-learning tutor is built to keep the cell empty. If it
succeeded, the null is not evidence about the gate; it is evidence that the tutor works, and the
question was never asked.

This is a positivity (overlap) violation. No estimator repairs it -- there is nothing to estimate --
so it belongs BEFORE the model, as a gate, not after it as a caveat.

For each candidate edge A -> B we sort the learners who reached B by what they held when they got
there, at the moment of their first B attempt:

    MASTERED  at least one correct A attempt beforehand      -- the control cell
    FAILED    A attempted beforehand, never once correct     -- THE IDENTIFYING CELL
    NEVER     no A attempt beforehand at all                 -- order violation, weaker evidence:
              silent about whether they hold A from elsewhere

FAILED is the cell the gate lives or dies in, and the one a tutor erases. From its size and the
control's we report the minimum detectable effect: the smallest drop in B success an 80%-powered
test could see here. An edge whose MDE exceeds the effect anyone claims is unanswerable in this
dataset, whatever a model reports.

Every edge therefore leaves here carrying a STATE rather than a number alone (`shared/edge_state.py`):

    SUPPORTED     readable cell, powered test, the drop is there
    CONTRADICTED  readable cell, powered test, the drop is NOT there -- real negative evidence
    UNKNOWN       the cell could not be read, or could be read but not powered to the effect
                  claimed. This is most of them, and it is NOT a non-edge

A LIMIT ON SUPPORTED, measured in `studies/identifiability/surmise-vs-positivity/`: this comparison tests ONE ARM of what
may be a conjunctive gate. If B needs four prerequisites, the learners who hold A are mostly missing
something else B needs, both cells sit at the floor and the drop vanishes -- on synthetic data with
a planted 0.60 gate, 100% of edges into a single-prerequisite dependant come back SUPPORTED against
22% at fan-in four. So SUPPORTED here means "a single-prerequisite gate is visible", and the absence
of it says even less about the edge than the three states already imply.

That distinction is the entire point of the audit. An adjacency matrix has one symbol for "we
looked and found nothing" and "we could not look", and this programme's own result is that the
second case dominates: the best corpus on disk answers 15.5% of its pairs. Writing UNKNOWN is how
that stops being invisible downstream.

    python3 positivity.py junyi|assist|ds1190 [--out result.json] [--pairs all|authored]

Raw exports stay outside the repo (DataShop and ASSISTments both forbid redistribution); only the
aggregate counts printed here are ever committed.
"""

from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "studies/identifiability/latent-shape"))

from build_matrix import LOADERS, SCRATCH  # noqa: E402,F401  (SCRATCH: re-exported for conjunctive/)

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from shared.edge_state import (CLAIMED_EFFECT, CONTRADICTED, SUPPORTED,  # noqa: E402
                               UNKNOWN, classify_edge)
from shared.reachability import reachability  # noqa: E402

#: 80% power, two-sided 0.05 -- the convention the effects we are chasing are reported under
Z_ALPHA, Z_BETA = 1.959964, 0.8416212

#: an edge with fewer than this many learners on EITHER side cannot be read at all; reported
#: separately from "read it and found nothing" because the two mean opposite things
MIN_CELL = 5


def timelines(rows) -> dict[str, list[tuple[str, str, bool]]]:
    """Per learner, every attempt in time order as (time, item, correct).

    Takes an iterable of raw rows rather than a dataset name so the atlas can feed corpora that
    have no entry in LOADERS. One implementation, any corpus.
    """
    by_learner: dict[str, list[tuple[str, str, bool]]] = defaultdict(list)
    for learner, item, ok, t, _helped, _hinted in rows:
        by_learner[learner].append((t, item, bool(ok)))
    for rows in by_learner.values():
        rows.sort()
    return by_learner


def states(by_learner):
    """For each learner: first-touch time per item, and the time they first got each item right.

    Both are needed and they are not the same instant. Holding A is about having succeeded at it;
    reaching B is about having touched it.
    """
    first_touch, first_pass, outcome_at_touch = {}, {}, {}
    for learner, rows in by_learner.items():
        ft, fp, oat = {}, {}, {}
        for t, item, ok in rows:
            if item not in ft:
                ft[item] = t
                oat[item] = ok
            if ok and item not in fp:
                fp[item] = t
        first_touch[learner] = ft
        first_pass[learner] = fp
        outcome_at_touch[learner] = oat
    return first_touch, first_pass, outcome_at_touch


def at_item(first_touch, outcome_at_touch):
    """Learner lists keyed by item, so the pair loop never touches learners who did not reach B.

    The outer-loop form (scan every learner for every pair) is 29,000 x 40,000 lookups on
    ASSISTments and does not finish.
    """
    idx = defaultdict(list)
    for learner, ft in first_touch.items():
        oat = outcome_at_touch[learner]
        for item, t in ft.items():
            idx[item].append((learner, t, oat[item]))
    return idx


def classify(pair, first_touch, first_pass, outcome_at_touch, idx):
    """Split the learners who reached B by what they held in A when they got there."""
    a, b = pair
    cells = {"mastered": [], "failed": [], "never": []}
    for learner, tb, y in idx[b]:
        ta = first_touch[learner].get(a)
        if ta is None or ta >= tb:
            cells["never"].append(y)
        elif (pa := first_pass[learner].get(a)) is not None and pa < tb:
            cells["mastered"].append(y)
        else:
            cells["failed"].append(y)
    return cells



def retrospective(pair, first_touch, first_pass, outcome_at_touch, idx):
    """Recover an identifying cell from the learners who reached B having never touched A.

    Those learners are the bulk of the overlap in every dataset here, and on their own they say
    nothing: not having attempted A is not the same as not holding it. But most of them meet A
    later, and skills are acquired rather than lost -- the monotone-accumulation assumption the
    cancer-progression and phylogenetic literatures both run on. So a learner whose LATER first
    attempt at A fails almost certainly did not hold A when they reached B, and one whose later
    first attempt succeeds probably did.

    That is a weaker instrument than watching someone fail A and be sent to B anyway: "probably"
    is doing real work, and ability confounds both sides. It is reported as a separate cell for
    that reason, never pooled with the strict one.
    """
    a, b = pair
    held, lacked = [], []
    for learner, tb, y in idx[b]:
        ta = first_touch[learner].get(a)
        if ta is None or ta < tb:
            continue  # not a "never" learner: no A at all, or A came first
        (held if outcome_at_touch[learner][a] else lacked).append(y)
    return held, lacked


def mde(n_control: int, n_treat: int, p_control: float) -> float | None:
    """Smallest drop in B success an 80%-powered two-proportion test could detect here.

    Solved numerically rather than in closed form because the treated-arm variance depends on the
    effect being solved for -- the closed form that ignores this understates the MDE on small cells,
    which are exactly the cells at issue.
    """
    if n_control < MIN_CELL or n_treat < MIN_CELL:
        return None
    # A control arm pinned at 0 or 1 has no variance, and the binary search below then returns an
    # MDE of ~0 -- which reads as infinite power and is the opposite of the truth. It is a ceiling
    # effect: everyone who held the prerequisite got the dependant right, so the comparison has no
    # room to move. Two DataShop sets reported "sees a 20-point gate on 89% of pairs" this way.
    if p_control <= 0.01 or p_control >= 0.99:
        return None
    lo, hi = 0.0, p_control
    for _ in range(60):
        d = (lo + hi) / 2
        pt = p_control - d
        se = math.sqrt(p_control * (1 - p_control) / n_control + pt * (1 - pt) / n_treat)
        if d >= (Z_ALPHA + Z_BETA) * se:
            hi = d
        else:
            lo = d
    return hi


def authored_junyi() -> list[tuple[str, str]]:
    """Each authored edge once. Until 2026-09-24 this kept a list of every listed prerequisite, so
    the file's two duplicated rows (each listing its prerequisite twice) and one row listing a
    prerequisite twice put 988 entries, 981 edges, into the candidate set."""
    from shared.junyi_graph import authored_edges
    from shared.paths import data_path
    return authored_edges(data_path("JUNYI_DIR"), known_only=False)


#: ds1190's within-problem step dependencies -- the one ground truth in this programme that is
#: procedurally true rather than authored (a fifth-grade fraction sum needs both denominators
#: before the common one, and both numerators before the sum).
#:
#: ORIENTATION: (prerequisite, dependant), the convention of candidate_pairs(), of authored_junyi()
#: (which returns (p, name)) and of every reader of this list, including evpi.py. The edge list
#: itself lives in ONE place, steps_ds1190.DEPENDS, which is written the other way round ("left
#: depends on right", i.e. (dependant, prerequisite)), so it is imported and flipped here rather
#: than restated. It used to be a copy "kept identical" to DEPENDS, which read every authored
#: ds1190 pair backwards here (found 2026-09-24; no committed output used it -- see the README).
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "outcomes/datashop"))
from steps_ds1190 import DEPENDS as _DS1190_DEPENDS  # noqa: E402

DS1190_PAIRS = [(prereq, dependant) for dependant, prereq in _DS1190_DEPENDS]


def candidate_pairs(name: str, items: list[str], mode: str) -> list[tuple[str, str]]:
    if mode == "authored" and name == "junyi":
        held = set(items)
        return [(a, b) for a, b in authored_junyi() if a in held and b in held]
    if mode == "authored" and name == "ds1190":
        held = set(items)
        return [(a, b) for a, b in DS1190_PAIRS if a in held and b in held]
    # every ordered pair, for datasets with no authored graph -- the question is then about the
    # dataset's capacity rather than about any particular edge
    return [(a, b) for a in items for b in items if a != b]


def main() -> None:
    name = sys.argv[1]
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else None
    mode = sys.argv[sys.argv.index("--pairs") + 1] if "--pairs" in sys.argv else (
        "authored" if name in ("junyi", "ds1190") else "all")

    print(f"positivity audit: {name} ({mode} pairs)")
    by_learner = timelines(LOADERS[name]())
    first_touch, first_pass, outcome_at_touch = states(by_learner)
    idx = at_item(first_touch, outcome_at_touch)
    items = sorted(idx)
    print(f"   {len(by_learner):,} learners, {len(items):,} items")

    pairs = candidate_pairs(name, items, mode)
    if len(pairs) > 40000:
        rng = np.random.default_rng(0)
        pairs = [pairs[i] for i in rng.choice(len(pairs), 40000, replace=False)]
        print(f"   sampling 40,000 of the ordered pairs")
    print(f"   {len(pairs):,} candidate edges")

    rows = []
    for a, b in pairs:
        c = classify((a, b), first_touch, first_pass, outcome_at_touch, idx)
        n_m, n_f, n_n = len(c["mastered"]), len(c["failed"]), len(c["never"])
        if n_m + n_f + n_n == 0:
            continue
        p_m = float(np.mean(c["mastered"])) if n_m else float("nan")
        p_f = float(np.mean(c["failed"])) if n_f else float("nan")
        held, lacked = retrospective((a, b), first_touch, first_pass,
                                     outcome_at_touch, idx)
        p_h = float(np.mean(held)) if held else float("nan")
        m = mde(n_m, n_f, p_m) if n_m and not math.isnan(p_m) else None
        # the drop the gate predicts: control cell minus identifying cell
        obs = (p_m - p_f) if not (math.isnan(p_m) or math.isnan(p_f)) else None
        state, why = classify_edge(m, obs)      # provisional; the gate below may move it
        rows.append(dict(a=a, b=b, n_mastered=n_m, n_failed=n_f, n_never=n_n,
                         p_mastered=p_m, p_failed=p_f,
                         mde=m, observed=obs, state=state, state_reason=why,
                         n_held=len(held), n_lacked=len(lacked),
                         p_held=p_h, p_lacked=float(np.mean(lacked)) if lacked else float("nan"),
                         mde_retro=(mde(len(held), len(lacked), p_h)
                                    if held and not math.isnan(p_h) else None)))

    # THE REACHABILITY GATE, OVER THE WOULD-BE CONTRADICTIONS ONLY. A null is negative evidence
    # only where the corpus could have falsified it -- shared/edge_state.py holds the rule and this
    # supplies it the figure. Running it on every pair would dominate the audit; running it on the
    # negative verdicts costs nothing, and falsifiability bears on no other branch. The node must
    # be READABLE and POWERED, the same two-part rule classify_edge applies to a single edge.
    contra = [r for r in rows if r["state"] == CONTRADICTED]
    if contra:
        tl = {learner: {u: ((fp[u], True) if u in fp else (t, False))
                        for u, t in first_touch[learner].items()}
              for learner, fp in first_pass.items()}
        reach_of = reachability(tl, [(r["a"], r["b"]) for r in contra], min_cell=MIN_CELL,
                                claimed=CLAIMED_EFFECT)
        moved = unpowered = 0
        for r in contra:
            ok = reach_of[(r["a"], r["b"])]["status"] == "FALSIFIABLE"
            r["falsifiable"] = ok
            r["state"], r["state_reason"] = classify_edge(r["mde"], r["observed"], falsifiable=ok)
            if r["state"] != CONTRADICTED:
                moved += 1
                unpowered += reach_of[(r["a"], r["b"])]["readable_nodes"] > 0
        print(f"   reachability gate: {moved:,} of {len(contra):,} contradictions read UNKNOWN "
              f"({unpowered:,} had a readable merge node that was underpowered, "
              f"{moved - unpowered:,} had none at all)")

    report(name, mode, rows, out)


def report(name, mode, rows, out) -> None:
    n = len(rows)
    reach = np.array([r["n_mastered"] + r["n_failed"] + r["n_never"] for r in rows], float)
    failed = np.array([r["n_failed"] for r in rows], float)
    never = np.array([r["n_never"] for r in rows], float)
    frac = np.divide(failed, reach, out=np.zeros_like(failed), where=reach > 0)

    readable = [r for r in rows if r["mde"] is not None]
    mdes = np.array([r["mde"] for r in readable]) if readable else np.array([])

    print(f"\n   edges with any learner at B          {n:,}")
    print(f"   median learners reaching B           {np.median(reach):.0f}")
    print(f"   median in the IDENTIFYING cell       {np.median(failed):.0f}"
          f"   ({np.median(frac):.1%} of those who reached B)")
    print(f"   median reaching B with no A at all   {np.median(never):.0f}")
    print(f"   edges where BOTH cells clear {MIN_CELL:<2}      "
          f"{len(readable):,}  ({len(readable) / max(n, 1):.1%})")

    # The headline the atlas could not state before: how many edges does this corpus actually
    # decide, in either direction, and how many does it leave undecided? An adjacency matrix would
    # write a zero for every one of the UNKNOWN rows.
    counts = {k: sum(1 for r in rows if r["state"] == k) for k in (SUPPORTED, CONTRADICTED, UNKNOWN)}
    print(f"\n   EDGE STATE, at the {CLAIMED_EFFECT:.2f} effect being claimed")
    for k in (SUPPORTED, CONTRADICTED, UNKNOWN):
        print(f"      {k:<14}{counts[k]:>8,}  ({counts[k] / max(n, 1):>6.1%})")
    decided = counts[SUPPORTED] + counts[CONTRADICTED]
    print(f"      {'decided':<14}{decided:>8,}  ({decided / max(n, 1):>6.1%})"
          f"   -- the rest would be a zero in an adjacency matrix")
    if len(mdes):
        print(f"\n   minimum detectable drop in B success, over the readable edges")
        for q in (10, 25, 50, 75, 90):
            print(f"      p{q:<3} {np.percentile(mdes, q):.3f}")
        for thresh in (0.05, 0.10, 0.20):
            k = int((mdes <= thresh).sum())
            print(f"   edges able to detect a {thresh:.0%} drop   {k:,}"
                  f"  ({k / max(n, 1):.1%} of all edges)")

    # the observed drop, where it is readable at all. This is not a causal estimate -- learners who
    # failed A differ from those who passed it in every other way too -- it is the size of the thing
    # the cell counts above say we could or could not have seen.
    both = [r for r in readable if not math.isnan(r["p_failed"])]
    if both:
        d = np.array([r["p_mastered"] - r["p_failed"] for r in both])
        beats = sum(1 for r, dd in zip(both, d) if dd > r["mde"])
        print(f"\n   observed drop (unadjusted, NOT causal), {len(both):,} readable edges")
        print(f"      median {np.median(d):+.3f}   mean {d.mean():+.3f}")
        print(f"      exceeding their own MDE  {beats:,}  ({beats / len(both):.1%})")

    retro = [r for r in rows if r["mde_retro"] is not None
             and not math.isnan(r["p_lacked"])]
    if retro:
        dr = np.array([r["p_held"] - r["p_lacked"] for r in retro])
        mr = np.array([r["mde_retro"] for r in retro])
        print(f"\n   RETROSPECTIVE cell -- reached B before A, split by how A later went")
        print(f"      readable edges  {len(retro):,}  ({len(retro) / max(n, 1):.1%} of all edges)")
        print(f"      median MDE      {np.median(mr):.3f}")
        print(f"      observed drop   median {np.median(dr):+.3f}   mean {dr.mean():+.3f}")
        print(f"      exceeding MDE   {int((dr > mr).sum()):,}  ({(dr > mr).mean():.1%})")

    summary = dict(
        dataset=name, pairs=mode, edges=n,
        median_reach=float(np.median(reach)), median_identifying=float(np.median(failed)),
        median_identifying_frac=float(np.median(frac)), median_never=float(np.median(never)),
        readable=len(readable), readable_frac=len(readable) / max(n, 1),
        mde_median=float(np.median(mdes)) if len(mdes) else None,
        edge_state={k: sum(1 for r in rows if r["state"] == k)
                    for k in (SUPPORTED, CONTRADICTED, UNKNOWN)},
        claimed_effect=CLAIMED_EFFECT,
        detect_10pt=int((mdes <= 0.10).sum()) if len(mdes) else 0,
        detect_20pt=int((mdes <= 0.20).sum()) if len(mdes) else 0,
        retro_readable=len(retro), retro_readable_frac=len(retro) / max(n, 1),
        retro_mde_median=float(np.median(mr)) if retro else None,
        retro_drop_median=float(np.median(dr)) if retro else None,
        retro_beats_mde=float((dr > mr).mean()) if retro else None,
    )
    if out:
        out.write_text(json.dumps(dict(summary=summary, edges=rows[:2000]), indent=1))
        print(f"\n   -> {out}")


if __name__ == "__main__":
    main()
