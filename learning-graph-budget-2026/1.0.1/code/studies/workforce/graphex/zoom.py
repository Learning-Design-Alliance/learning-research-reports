"""
Is the graph zoomable? Test the claim [`STRUCTURE.md`](STRUCTURE.md) makes, on the real graph.

That note argues a graph meant to be zoomed must **store the reachability closure and render the
reduction**, never the other way round, because:

  A. reachability SURVIVES node contraction - the quotient's reachability is exactly the projection
     of the fine graph's reachability; and
  B. the immediate-prerequisite relation DOES NOT - contracting `b` out of `a -> b -> c` makes `a`
     immediate to `c`, which nobody asserted.

**A is false, and this script is what showed it.** Contraction never DESTROYS reachability, but it
freely MANUFACTURES it: glue `a` and `b` into one node and everything reaching `a` now reaches
everything `b` reached, whether or not any path existed. The note asserted preservation where only
monotonicity holds. So the two claims are not "one survives, one does not" - both directions leak,
and the only question worth asking is **how much**, which is a measurement rather than a theorem.

    python3 zoom.py

## The hierarchy is the standards' own

CCSS codes nest: `5.NF.A.2` sits under `5.NF.A`, under `5.NF`, under grade `5`. That gives four
genuine zoom levels over 408 of the 626 nodes without inventing a clustering, which matters - a
contraction chosen to make the result come out is not a test. Nodes outside that scheme (learner
variables, capabilities, occupations) are carried through unchanged at every level, so the only
thing varying is standard granularity.
"""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from shared.paths import HERE  # noqa: E402

LEVELS = {4: "standard (5.NF.A.2)", 3: "cluster (5.NF.A)", 2: "domain (5.NF)", 1: "grade (5)"}


def coarsen(node_id: str, level: int) -> str:
    """Map a node to its representative at `level`. Non-standard nodes are their own class."""
    if not node_id.startswith("std:"):
        return node_id
    code = node_id[4:]
    # 'HS.G-CO.A.1' keeps HS as one token so it coarsens to 'HS.G-CO' rather than to 'HS'.
    parts = code.split(".")
    if parts[0] == "HS" and len(parts) > 1:
        parts = [f"HS.{parts[1]}"] + parts[2:]
    return "std:" + ".".join(parts[:level])


def reachability(nodes: list[str], edges: list[tuple[str, str]]) -> set[tuple[str, str]]:
    """All ordered pairs (u, v), u != v, with a directed path u -> v. Cycles are fine."""
    adj: dict[str, list[str]] = collections.defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
    out: set[tuple[str, str]] = set()
    for s in nodes:
        seen = {s}
        stack = list(adj[s])
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            stack.extend(adj[x])
        for t in seen:
            if t != s:
                out.add((s, t))
    return out


def reduction(pairs: set[tuple[str, str]]) -> set[tuple[str, str]]:
    """Edges of the closure that no two-step path already gives - the immediate relation.

    Mutually-reachable pairs (a->b and b->a) are excluded rather than reduced: inside an equivalence
    class 'immediate' has no meaning, and including them would let class size drive the comparison.
    """
    succ: dict[str, set[str]] = collections.defaultdict(set)
    for u, v in pairs:
        succ[u].add(v)
    mutual = {(u, v) for (u, v) in pairs if (v, u) in pairs}
    out = set()
    for u, v in pairs - mutual:
        if not any(v in succ[m] for m in succ[u] if m != v and (v, m) not in pairs):
            out.add((u, v))
    return out


def main() -> int:
    g = json.loads((HERE(__file__) / "graphex.json").read_text())
    nodes = [n["id"] for n in g["nodes"]]
    edges = [(e["from"], e["to"]) for e in g["edges"]]
    fine_reach = reachability(nodes, edges)
    fine_red = reduction(fine_reach)
    print(f"   fine graph: {len(nodes)} nodes, {len(edges)} edges, "
          f"{len(fine_reach)} reachable pairs, {len(fine_red)} immediate\n")

    rows = []
    for level in sorted(LEVELS, reverse=True):
        phi = {n: coarsen(n, level) for n in nodes}
        cnodes = sorted(set(phi.values()))
        cedges = {(phi[u], phi[v]) for u, v in edges if phi[u] != phi[v]}

        quotient_reach = reachability(cnodes, sorted(cedges))
        projected_reach = {(phi[u], phi[v]) for u, v in fine_reach if phi[u] != phi[v]}
        # Never lost (monotonicity), sometimes invented (gluing). Both are measured, because
        # asserting one of them was the mistake this script exists to catch.
        lost_reach = projected_reach - quotient_reach
        made_reach = quotient_reach - projected_reach

        quotient_red = reduction(quotient_reach)
        projected_red = {(phi[u], phi[v]) for u, v in fine_red if phi[u] != phi[v]}
        made_red = quotient_red - projected_red

        rows.append({"level": level, "name": LEVELS[level], "nodes": len(cnodes),
                     "edges": len(cedges), "reachable_pairs": len(quotient_reach),
                     "immediate": len(quotient_red),
                     "reach_lost": len(lost_reach), "reach_manufactured": len(made_reach),
                     "reach_manufactured_share": (len(made_reach) / len(quotient_reach)
                                                  if quotient_reach else 0.0),
                     "immediate_manufactured": len(made_red),
                     "immediate_manufactured_share": (len(made_red) / len(quotient_red)
                                                      if quotient_red else 0.0)})
        print(f"   L{level} {LEVELS[level]:22} {len(cnodes):4d} nodes {len(cedges):5d} edges | "
              f"reach {len(quotient_reach):6d} (lost {len(lost_reach)}, invented "
              f"{len(made_reach):5d} = {(len(made_reach) / len(quotient_reach) if quotient_reach else 0):4.0%}) | "
              f"immediate {len(quotient_red):4d} (invented {len(made_red):3d} = "
              f"{(len(made_red) / len(quotient_red) if quotient_red else 0):3.0%})")

    print()
    never_lost = all(r["reach_lost"] == 0 for r in rows)
    wr = max(rows, key=lambda r: r["reach_manufactured_share"])
    wi = max(rows, key=lambda r: r["immediate_manufactured_share"])
    print(f"   Reachability is never destroyed by contraction: {'confirmed' if never_lost else 'VIOLATED'}"
          " - so a zoomed-out view never hides a dependency.")
    print(f"   It is freely invented: at {wr['name']} {wr['reach_manufactured_share']:.0%} of the "
          f"reachable pairs a zoomed view shows have no path underneath them.")
    print(f"   The immediate relation fares better here: worst is {wi['name']} at "
          f"{wi['immediate_manufactured_share']:.0%}.")

    (HERE(__file__) / "zoom-result.json").write_text(json.dumps(
        {"source": "graphex.json - all layers in one weighted network",
         "fine": {"nodes": len(nodes), "edges": len(edges),
                  "reachable_pairs": len(fine_reach), "immediate": len(fine_red)},
         "reachability_never_lost": never_lost,
         "levels": rows}, indent=2))
    print("\n   wrote zoom-result.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
