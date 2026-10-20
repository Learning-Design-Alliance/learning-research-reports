"""Merge-node reachability: was a pairwise null ever falsifiable?

WHY THIS EXISTS. A7 and A17 were both re-scored UNMET on 2026-09-23 against the same gap, so the
computation lives here once rather than twice. docs/specs/SPAN.md states it: two concepts can be genuinely
independent until a third node where they fuse -- `ne`/`ci` and `futuro anteriore` do not gate each
other until `i verbi pronominali`, where the clitics fuse onto the verb and a learner needs both at
once. The pairwise null between them is CORRECT. The dependency is conjunctive, `(A and B) -> C`,
and it exists nowhere in the curriculum before C.

So a corpus whose syllabus stops before C contains NO EVIDENCE that A and B are related, and that
absence is a fact about the corpus rather than about the domain. Every pairwise null this programme
reports is therefore silently indexed to a node set nobody has ever stated:

    "no relation between A and B"  really means
    "no relation between A and B AMONG THE DOWNSTREAM NODES THIS CORPUS HAPPENS TO CONTAIN."

THE TEST, IN TWO PARTS, BECAUSE READABILITY IS NOT POWER. A pair (A, B) needs at least one node C,
reached after both, carrying enough learners in EACH of the four strata

        passed A x passed B        passed A x failed B
        failed A x passed B        failed A x failed B

for a conjunctive gate at C to have shown itself. "Enough" is two conditions and the second was
missing until 2026-09-24:

    READABLE   at least `min_cell` learners in each stratum -- the cells exist to be compared.
    POWERED    the comparison between the both-passed stratum and the weakest other one could
               DETECT the claimed effect: mde(n_both, n_weakest, p_both) <= `claimed`.

Only the first was implemented, which left this module making exactly the mistake
shared/edge_state.py exists to prevent one level down -- treating "I could read the cells" as "I
could have seen the effect". A7's open question was which cell floor to use, 5 or 10, and the
honest answer is that a bare floor is the wrong instrument for the question: 5 learners per stratum
can never resolve a 10-point gate, and no choice of floor makes a readability test into a power
test. The programme already owns the right rule and applies it to single edges; this lifts it one
level up rather than picking a threshold.

Where no qualifying C exists, the pair's null is UNFALSIFIABLE and must be reported UNKNOWN rather
than CONTRADICTED.

DOWNSTREAM IS READ FROM THE LEARNER'S OWN TIMELINE, not from the published curriculum. The
testability condition is that learners actually held states on A and B before meeting C; a C the
curriculum places later but that no learner reached after both is not a testable merge node. Where a
published position is supplied, how many qualifying C are ALSO curriculum-downstream is reported
beside it, since a merge node the curriculum agrees is downstream is the stronger case.

This module counts what could have been seen. It does not score conjunctions -- that is
studies/identifiability/conjunctive/, criterion A17.
"""
import collections
import itertools
import math
import random

#: 80% power, two-sided 0.05 -- the convention studies/identifiability/overlap/positivity.py already reports MDEs under
Z_ALPHA, Z_BETA = 1.959964, 0.8416212


def build_timelines(cells, pass_threshold=0.5):
    """cells: iterable of (learner, skill, time, mean_outcome).

    Returns learner -> {skill: (first_time, passed)}, first occurrence only, because a learner's
    later practice on A must not decide whether they had passed A before reaching C."""
    per = collections.defaultdict(dict)
    for learner, skill, t, m in cells:
        cur = per[learner].get(skill)
        if cur is None or t < cur[0]:
            per[learner][skill] = (t, m >= pass_threshold)
    return per


def _index(timelines):
    """skill -> {learner: (time, passed)}, for cheap membership tests."""
    idx = collections.defaultdict(dict)
    for learner, skills in timelines.items():
        for s, (t, p) in skills.items():
            idx[s][learner] = (t, p)
    return idx


def _mde(n_control, n_treat, p_control):
    """Smallest drop an 80%-powered two-proportion test could detect. Same solve as
    studies/identifiability/overlap/positivity.py's, kept here so this module does not import an experiment."""
    if n_control < 1 or n_treat < 1 or p_control <= 0.01 or p_control >= 0.99:
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


def reachability(timelines, pairs, min_cell=10, position=None, claimed=None):
    """For each unordered pair, find the merge nodes that would have made a conjunction visible.

    `claimed` turns on the POWER half of the test: a node qualifies only if the comparison between
    its both-passed stratum and its weakest other stratum could detect a drop of that size. Left
    None it is readability alone, which is what every caller did before 2026-09-24 and is kept so
    an old result can still be reproduced.

    Returns pair -> {"status", "merge_nodes", "best", "best_cells", "best_mde",
    "curriculum_downstream", "readable_nodes"}.
    """
    idx = _index(timelines)
    out = {}
    for (a, b) in pairs:
        la, lb = idx.get(a, {}), idx.get(b, {})
        both = la.keys() & lb.keys()
        if not both:
            out[(a, b)] = {"status": "UNFALSIFIABLE", "merge_nodes": 0, "best": None,
                           "best_cells": None, "best_mde": None, "readable_nodes": 0,
                           "curriculum_downstream": 0, "learners_with_both": 0}
            continue
        # cells[C][stratum] over learners who met C after BOTH a and b, and how many of them
        # passed C -- the pass counts are what the power half needs
        cells = collections.defaultdict(lambda: [0, 0, 0, 0])
        passes = collections.defaultdict(lambda: [0, 0, 0, 0])
        for learner in both:
            ta, pa = la[learner]
            tb, pb = lb[learner]
            after = max(ta, tb)
            stratum = (0 if pa else 2) + (0 if pb else 1)
            for c, (tc, pc) in timelines[learner].items():
                if c != a and c != b and tc > after:
                    cells[c][stratum] += 1
                    if pc:
                        passes[c][stratum] += 1
        readable = [(c, v) for c, v in cells.items() if min(v) >= min_cell]
        good = readable
        if claimed is not None:
            powered = []
            for c, v in readable:
                # the gate's own comparison: both-passed against the weakest other stratum
                n_both, p_both = v[0], (passes[c][0] / v[0] if v[0] else 0.0)
                m = _mde(n_both, min(v[1:]), p_both)
                if m is not None and m <= claimed:
                    powered.append((c, v, m))
            powered.sort(key=lambda t: t[2])
            good = [(c, v) for c, v, _m in powered]
            best_mde = powered[0][2] if powered else None
        else:
            best_mde = None
        good.sort(key=lambda kv: -min(kv[1]))
        cd = 0
        if position is not None and good:
            for c, _ in good:
                pa_, pb_, pc_ = position.get(a), position.get(b), position.get(c)
                if None in (pa_, pb_, pc_):
                    continue
                if pa_[:2] == pc_[:2] == pb_[:2] and pc_[2] > pa_[2] and pc_[2] > pb_[2]:
                    cd += 1
        out[(a, b)] = {
            "status": "FALSIFIABLE" if good else "UNFALSIFIABLE",
            "merge_nodes": len(good),
            "readable_nodes": len(readable),
            "best": good[0][0] if good else None,
            "best_cells": good[0][1] if good else None,
            "best_mde": best_mde,
            "curriculum_downstream": cd,
            "learners_with_both": len(both),
        }
    return out


def summarise(result):
    n = len(result)
    f = sum(1 for v in result.values() if v["status"] == "FALSIFIABLE")
    cd = sum(1 for v in result.values() if v["curriculum_downstream"] > 0)
    nodes = [v["merge_nodes"] for v in result.values() if v["merge_nodes"]]
    nodes.sort()
    return {
        "pairs": n,
        "falsifiable": f,
        "unfalsifiable": n - f,
        "share_falsifiable": f / n if n else float("nan"),
        "with_curriculum_downstream_node": cd,
        "median_merge_nodes_when_any": nodes[len(nodes) // 2] if nodes else 0,
        "max_merge_nodes": nodes[-1] if nodes else 0,
    }


# ---------------------------------------------------------------- floor

def planted_corpus(n_learners=4000, n_skills=12, reach=0.6, seed=0):
    """A synthetic corpus whose answer is known by construction.

    Skills 0..n_skills-1 are met in index order. Every learner meets an initial run of them, so a
    pair (i, j) has an observable merge node exactly when learners get far enough past max(i, j) --
    which makes LATE pairs unfalsifiable and EARLY pairs falsifiable, by construction and with
    nothing to do with any dependency. An instrument that cannot reproduce that gradient is not
    measuring reachability.
    """
    rng = random.Random(seed)
    cells = []
    for u in range(n_learners):
        depth = 2 + int(rng.random() ** (1 / max(reach, 1e-9)) * (n_skills - 2))
        for s in range(depth):
            cells.append((u, "S%02d" % s, float(s), 1.0 if rng.random() < 0.5 else 0.0))
    return cells


def floor(min_cell=10, log=print, claimed=None):
    """The planted gradient must come back: early pairs falsifiable, late pairs not.

    Run with `claimed` set, the POWER half must be STRICTLY NARROWER than readability alone --
    adding a condition can only remove nodes. A power test that certified a pair readability had
    refused would mean the two are not nested, which would be a bug rather than a finding."""
    cells = planted_corpus()
    tl = build_timelines(cells)
    skills = sorted({s for _, s, _, _ in cells})
    pairs = list(itertools.combinations(skills, 2))
    res = reachability(tl, pairs, min_cell=min_cell, claimed=claimed)
    early = [(p, v) for p, v in res.items() if max(int(p[0][1:]), int(p[1][1:])) <= 3]
    late = [(p, v) for p, v in res.items() if max(int(p[0][1:]), int(p[1][1:])) >= 10]
    e = sum(1 for _, v in early if v["status"] == "FALSIFIABLE") / max(1, len(early))
    l = sum(1 for _, v in late if v["status"] == "FALSIFIABLE") / max(1, len(late))
    log("  FLOOR -- planted reachability gradient%s"
        % ("" if claimed is None else ", powered to %.2f" % claimed))
    log("    early pairs (max index <= 3)   falsifiable %.0f%%  of %d" % (100 * e, len(early)))
    log("    late  pairs (max index >= 10)  falsifiable %.0f%%  of %d" % (100 * l, len(late)))
    ok = e > 0.9 and l < 0.1
    if claimed is not None:
        bare = reachability(tl, pairs, min_cell=min_cell)
        nested = all(not (v["status"] == "FALSIFIABLE" and bare[k]["status"] != "FALSIFIABLE")
                     for k, v in res.items())
        kept = sum(1 for v in res.values() if v["status"] == "FALSIFIABLE")
        had = sum(1 for v in bare.values() if v["status"] == "FALSIFIABLE")
        log("    powered keeps %d of readability's %d, nested %s" % (kept, had, nested))
        ok = ok and nested
    log("    -> %s" % ("instrument reproduces the gradient" if ok else "FLOOR FAILURE"))
    return ok, e, l
