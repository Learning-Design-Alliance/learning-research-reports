"""Reversed-arrow control for any analysis whose answer depends on which way an edge points.

Every directional result is scored twice: under the orientation the study claims and under its
reverse. If the reverse scores as well or better, the orientation is unproven or backwards, and the
result is not reported as directional. This is the control that would have caught the Junyi
rating-direction error (strict AUC 0.598 claimed; the reverse gave 0.752), the way a deranged arm
catches a result that the data's shape alone produces.

A script that uses this declares its convention in its docstring on a line of the form

    DIRECTION: <what "a -> b" means here>, per <source of the convention, quoted in the codebook>

or `DIRECTION: symmetric` if nothing it reports depends on orientation. `board/direction_audit.py`
enforces both.

    from shared.direction import reversed_arrow
    res = reversed_arrow(lambda edges: auc(scores, [e in edges for e in pairs]), authored)
"""

from __future__ import annotations

from typing import Callable, Hashable, Iterable

Edge = tuple[Hashable, Hashable]

#: the claimed orientation must beat its reverse by at least this much to be called directional;
#: a tie is not evidence of direction
MARGIN = 0.0


def reverse(edges: Iterable[Edge]) -> set[Edge]:
    return {(b, a) for a, b in edges}


def reversed_arrow(score: Callable[[set[Edge]], float], edges: Iterable[Edge],
                   higher_is_better: bool = True) -> dict:
    """Score `edges` as claimed and reversed. `score` takes a set of (tail, head) edges.

    Returns claimed, reversed, their difference (in the better direction) and a verdict:
      CLAIMED      the claimed orientation scores better than its reverse
      REVERSED     the reverse scores better: the convention is probably backwards
      UNRESOLVED   they tie
    """
    e = set(edges)
    c, r = float(score(e)), float(score(reverse(e)))
    d = (c - r) if higher_is_better else (r - c)
    verdict = "CLAIMED" if d > MARGIN else "REVERSED" if d < -MARGIN else "UNRESOLVED"
    return dict(claimed=c, reversed=r, margin=d, verdict=verdict)


def require_claimed(res: dict, what: str) -> None:
    """Refuse to continue when the reverse wins: a backwards convention is a bug, not a finding."""
    if res["verdict"] != "CLAIMED":
        raise SystemExit(f"{what}: reversed-arrow control reads {res['verdict']} "
                         f"(claimed {res['claimed']:.3f}, reversed {res['reversed']:.3f}). "
                         f"Check the direction convention against the source before reporting.")
