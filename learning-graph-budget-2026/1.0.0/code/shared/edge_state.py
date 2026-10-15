"""Three states for an edge, because a zero in an adjacency matrix is two different claims.

`studies/identifiability/overlap/ATLAS.md` is the reason this file exists. The identifying cell -- learners who met the
dependant having failed the prerequisite -- is **empty** for most pairs in every corpus on disk, and
the best one answers 15.5% of them. A mastery tutor erases that cell on purpose: it is built to stop
exactly the learners who would identify the claim.

So for most pairs we have no evidence either way, and an adjacency matrix has nowhere to say so. It
offers 1 and 0, and 0 gets used for both *"we looked and there is no edge"* and *"we could not
look"*. Those are opposite claims and collapsing them is how an empty cell becomes a confident
non-edge.

    SUPPORTED     the cell was readable and the effect is there
    CONTRADICTED  the cell was readable, the test had the power to see the effect, and it is not
                  there. Real negative evidence
    UNKNOWN       the cell was not readable, or was readable but underpowered. NOT a non-edge

## CONTRADICTED requires power, and that is the whole point

An edge is only contradicted when the test **could have seen** the effect and did not. Without that,
a null result is `UNKNOWN`. This is the same rule `studies/identifiability/latent-shape/power.py` enforces for the
programme's own findings -- *a null from an instrument that cannot see a planted gate is not a
finding* -- applied to the graph itself.

It also means positivity is the only route this programme has to legitimate negative evidence about
an edge. Nothing else generates `CONTRADICTED`, because nothing else establishes the power to.

## A null is only negative evidence if it was falsifiable, and that is a THIRD condition

Power is necessary and it is not sufficient. `studies/identifiability/a7-readjudication/` measured the gap: of XES3G5M's
410 `CONTRADICTED` verdicts, **337 keep an observed merge node and 73 do not** -- about one in six
was granted on a pair the corpus could never have falsified. `docs/specs/SPAN.md` states why this is not a
technicality. Two capabilities can be genuinely independent until a third node where they fuse, so
the pairwise null between them is *correct* and the dependency is conjunctive; a corpus whose
syllabus stops before that node holds no evidence the two are related, and that absence is a fact
about the corpus rather than the domain.

So `classify_edge` takes an optional `falsifiable`, from `shared/reachability.py`, and refuses the
`CONTRADICTED` branch without it. It is deliberately a THREE-VALUED argument:

    True   a merge node was observed with adequate cells -- the null can stand as evidence
    False  none was -- the null is UNFALSIFIABLE and reads UNKNOWN however powered it was
    None   the gate was not run. The state is unchanged, and the REASON says the check is
           missing, so a CONTRADICTED that never met the gate stays visible as one rather
           than passing for an adjudicated verdict.

`None` preserving the old behaviour is a compatibility choice with a cost, and the cost is paid in
the reason string rather than hidden: every caller that has not been wired up yet is labelled.

Falsifiability bears on the negative branch only. A pair with no observed merge node that
nonetheless shows the drop is still `SUPPORTED` -- the merge-node argument is about what an ABSENCE
can mean, never about discarding a positive.

## Why the states are not probabilities

A probability per edge would be tidier and would smuggle the same error back in: an edge nobody
could measure and an edge measured at 50/50 would both come out near 0.5. The point of the
trichotomy is that unmeasured and measured-as-uncertain are different kinds of thing, and the
schema should be unable to confuse them. Weights belong on top of a state, not instead of one.
"""

from __future__ import annotations

__all__ = ["SUPPORTED", "CONTRADICTED", "UNKNOWN", "STATES", "classify_edge",
           "IDENTIFIED", "PROJECTED", "EdgeClaim", "claim", "project"]

SUPPORTED = "supported"
CONTRADICTED = "contradicted"
UNKNOWN = "unknown"
STATES = (SUPPORTED, CONTRADICTED, UNKNOWN)

#: The smallest drop in dependant success anyone claims for a prerequisite. An edge whose MDE
#: exceeds this cannot be contradicted by this dataset however flat the observed difference is --
#: the test simply could not have seen a real effect of the size being claimed.
CLAIMED_EFFECT = 0.10


def classify_edge(mde: float | None, observed: float | None, *,
                  claimed: float = CLAIMED_EFFECT,
                  falsifiable: bool | None = None) -> tuple[str, str]:
    """The edge's state and the one-line reason, from the test's power, what it saw, and whether
    the corpus could ever have falsified it.

    `mde` is the minimum detectable effect for this edge's cells, or None when the cells could not
    be read at all -- too small, or a control arm at the ceiling. `observed` is the drop in
    dependant success between the control cell and the identifying cell, or None when there is
    nothing to compare. `falsifiable` is `shared/reachability.py`'s answer for this pair: True, or
    False, or None where the gate was not run (see the module docstring).

    The order of the checks is the argument. Power is examined BEFORE the observation, so that a
    flat result from an underpowered test can never reach the `CONTRADICTED` branch -- and
    falsifiability is examined INSIDE that branch, so an unfalsifiable pair that shows the drop is
    still SUPPORTED. Only the negative verdict needs a corpus that could have produced a positive.
    """
    if mde is None:
        return UNKNOWN, "the identifying cell is not readable, so nothing was measured"
    if mde > claimed:
        return UNKNOWN, (f"the cell is readable but underpowered: MDE {mde:.3f} exceeds the "
                         f"{claimed:.2f} effect being claimed, so a real edge would not show")
    if observed is None:
        return UNKNOWN, "no comparison available"
    if observed >= mde:
        return SUPPORTED, f"drop of {observed:.3f} at or above an MDE of {mde:.3f}"
    if falsifiable is False:
        return UNKNOWN, (f"drop of {observed:.3f} below an MDE of {mde:.3f} on a powered test, but "
                         f"no observed merge node: this corpus could not have falsified the pair, "
                         f"so the absence is not evidence")
    tail = ("" if falsifiable else
            " (REACHABILITY GATE NOT RUN -- falsifiability unchecked for this pair)")
    return CONTRADICTED, (f"drop of {observed:.3f} below an MDE of {mde:.3f}, on a test powered "
                          f"to see the {claimed:.2f} effect claimed{tail}")


# ---------------------------------------------------------------- levels and projection
#
# A claim about an edge is made at a level of detail: between items, skills, units, courses. The
# programme keeps finding that claims are identified at one level and unknown at another (individual
# skill edges fail where course-level comparisons have learners; one experiment says nothing where a
# pooled portfolio says something). An adjacency matrix has to pick one level for everything, so
# `EdgeClaim` records the level a claim was made at, and whether it was IDENTIFIED there or
# PROJECTED up from a finer level. Those are different claims: a projected course edge says "some
# skill edge between these courses is supported", not "the course comparison identifies an edge".
# studies/identifiability/holon-projection/ tests whether the two agree.
#
# Levels are free labels, deliberately not a fixed item < skill < unit < course ladder: model-made
# decompositions tie node type to depth (the goal-graph work), and a schema that fixes types by level
# would build that artefact in instead of testing it.
#
# The projection rule is transitive REDUCTION. studies/workforce/graphex/zoom.py, on the standards'
# four-level hierarchy, found that projecting by transitive closure inflates the edge set by up to 18%, by
# reduction 0-1%.

from dataclasses import dataclass  # noqa: E402

IDENTIFIED = "identified"
PROJECTED = "projected"


@dataclass(frozen=True)
class EdgeClaim:
    src: str
    dst: str
    state: str          # one of STATES
    reason: str
    level: str = "skill"
    basis: str = IDENTIFIED


def claim(src: str, dst: str, mde: float | None, observed: float | None, *, level: str = "skill",
          claimed: float = CLAIMED_EFFECT, falsifiable: bool | None = None) -> EdgeClaim:
    """`classify_edge`, recorded with the level the claim was made at. The default, skill, is the
    level every existing caller works at."""
    state, reason = classify_edge(mde, observed, claimed=claimed, falsifiable=falsifiable)
    return EdgeClaim(src, dst, state, reason, level, IDENTIFIED)


def project(claims, parent_of: dict[str, str], level: str) -> list[EdgeClaim]:
    """Project finer-level claims to the level of their parents, then reduce transitively.

    Between two parents P and Q (P != Q), over the child claims with src in P and dst in Q:
      SUPPORTED     if any child claim is supported;
      CONTRADICTED  only if every one of the |P| x |Q| child pairs has a claim and all are
                    contradicted (a negative at the coarser level needs every finer test negative);
      UNKNOWN       otherwise.
    Children with no parent in `parent_of`, and claims within one parent, do not project.
    Then every SUPPORTED projected edge P -> R implied by a path of other SUPPORTED projected edges
    is dropped (transitive reduction). With a cycle among supported edges the reduction is not
    unique, so nothing on the cycle is dropped and the reason says so.
    """
    members: dict[str, set] = {}
    for child, parent in parent_of.items():
        members.setdefault(parent, set()).add(child)
    grouped: dict[tuple, list] = {}
    for c in claims:
        p, q = parent_of.get(c.src), parent_of.get(c.dst)
        if p is None or q is None or p == q:
            continue
        grouped.setdefault((p, q), []).append(c)
    out = {}
    for (p, q), cs in grouped.items():
        n = len(cs)
        if any(c.state == SUPPORTED for c in cs):
            k = sum(c.state == SUPPORTED for c in cs)
            out[(p, q)] = EdgeClaim(p, q, SUPPORTED, f"{k} of {n} finer claims supported", level, PROJECTED)
        elif (n == len(members[p]) * len(members[q]) and len({(c.src, c.dst) for c in cs}) == n
              and all(c.state == CONTRADICTED for c in cs)):
            out[(p, q)] = EdgeClaim(p, q, CONTRADICTED, f"all {n} finer pairs contradicted", level, PROJECTED)
        else:
            out[(p, q)] = EdgeClaim(p, q, UNKNOWN, f"no finer claim supported; {n} of "
                                    f"{len(members[p]) * len(members[q])} pairs claimed", level, PROJECTED)
    succ: dict[str, set] = {}
    for (p, q), c in out.items():
        if c.state == SUPPORTED:
            succ.setdefault(p, set()).add(q)

    def reaches(a, b, skip):
        seen, stack = set(), [n for n in succ.get(a, ()) if (a, n) != skip]
        while stack:
            n = stack.pop()
            if n == b:
                return True
            if n not in seen:
                seen.add(n)
                stack.extend(succ.get(n, ()))
        return False
    for (p, q), c in list(out.items()):
        if c.state != SUPPORTED:
            continue
        if reaches(q, p, None):
            out[(p, q)] = EdgeClaim(p, q, SUPPORTED, c.reason + "; on a cycle, kept (reduction not unique)",
                                    level, PROJECTED)
        elif reaches(p, q, (p, q)):
            del out[(p, q)]
    return sorted(out.values(), key=lambda c: (c.src, c.dst))


def _selftest() -> None:
    """The invariants, not the happy path. `python3 edge_state.py` runs them.

    Kept here rather than in a second test file because the rule and its check should not be able
    to drift apart, and because `shared/test_stats.py` is the stats module's."""
    powered, flat, drop = 0.05, 0.01, 0.20

    # the three states still come out of the same three inputs they always did
    assert classify_edge(None, drop)[0] == UNKNOWN
    assert classify_edge(0.30, flat)[0] == UNKNOWN          # underpowered beats any observation
    assert classify_edge(powered, None)[0] == UNKNOWN
    assert classify_edge(powered, drop)[0] == SUPPORTED
    assert classify_edge(powered, flat)[0] == CONTRADICTED

    # falsifiability bites on the negative branch and only there
    assert classify_edge(powered, flat, falsifiable=False)[0] == UNKNOWN
    assert classify_edge(powered, flat, falsifiable=True)[0] == CONTRADICTED
    assert classify_edge(powered, drop, falsifiable=False)[0] == SUPPORTED, \
        "an unfalsifiable pair that SHOWS the drop is still supported"

    # power is checked before falsifiability, so a reachable pair cannot be contradicted on an
    # underpowered test just because its merge node exists
    assert classify_edge(0.30, flat, falsifiable=True)[0] == UNKNOWN

    # an unwired caller is labelled rather than silently passing for an adjudicated verdict
    assert "GATE NOT RUN" in classify_edge(powered, flat)[1]
    assert "GATE NOT RUN" not in classify_edge(powered, flat, falsifiable=True)[1]

    # a claim records its level; the default is the level every existing caller works at
    c = claim("a", "b", powered, drop)
    assert (c.state, c.level, c.basis) == (SUPPORTED, "skill", IDENTIFIED)

    # projection: courses X = {a, b}, Y = {c}, Z = {d}
    parent = {"a": "X", "b": "X", "c": "Y", "d": "Z"}
    sk = lambda s, d, st: EdgeClaim(s, d, st, "", "skill")
    # one supported child edge is enough for a supported projected edge
    pr = project([sk("a", "c", SUPPORTED), sk("b", "c", UNKNOWN)], parent, "course")
    assert [(p.src, p.dst, p.state, p.basis) for p in pr] == [("X", "Y", SUPPORTED, PROJECTED)]
    # a projected negative needs every finer pair claimed and contradicted
    assert project([sk("a", "c", CONTRADICTED)], parent, "course")[0].state == UNKNOWN
    assert project([sk("a", "c", CONTRADICTED), sk("b", "c", CONTRADICTED)], parent,
                   "course")[0].state == CONTRADICTED
    # transitive reduction drops the implied X -> Z, keeps X -> Y -> Z
    pr = project([sk("a", "c", SUPPORTED), sk("c", "d", SUPPORTED), sk("b", "d", SUPPORTED)],
                 parent, "course")
    assert {(p.src, p.dst) for p in pr} == {("X", "Y"), ("Y", "Z")}
    # a cycle is kept whole, not reduced arbitrarily
    pr = project([sk("a", "c", SUPPORTED), sk("c", "b", SUPPORTED)], parent, "course")
    assert {(p.src, p.dst) for p in pr} == {("X", "Y"), ("Y", "X")}
    # claims inside one parent do not project
    assert project([sk("a", "b", SUPPORTED)], parent, "course") == []
    print("edge_state: %d states, all invariants hold" % len(STATES))


if __name__ == "__main__":
    _selftest()
