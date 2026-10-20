"""Power arithmetic behind Paper 1's "about 30 learners per arm is a readability floor, not power".

Paper 1 (`research/article/limits-of-inferring-prerequisite-structure.md`, Abstract and section 6.1)
says that at 30 learners per arm the minimum detectable difference in first-encounter accuracy is
"about 0.33 (p 0.5-0.8, 80% power, normal approximation)" and that detecting a 0.10 difference needs
"about 300-380 per arm on a single edge". The reproduction audit (#46) found no committed analysis
behind either figure; its hand arithmetic agreed. This is that arithmetic, committed.

Two-sided alpha 0.05, power 0.80, normal approximation for two independent proportions, unpooled
variance: n per arm = (z_{1-a/2} + z_{1-b})^2 [p1(1-p1) + p2(1-p2)] / (p1 - p2)^2, p2 = p1 - delta.
p1 is the higher arm's accuracy, swept 0.5-0.8 as the paper states. The MDE at n is solved for
delta numerically because p2 depends on it (as positivity.mde does). No data are read.

    python3 arm_power.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from scipy.stats import norm

HERE = Path(__file__).resolve().parent
Z = norm.ppf(0.975) + norm.ppf(0.80)


def n_per_arm(p1: float, delta: float) -> float:
    p2 = p1 - delta
    return Z ** 2 * (p1 * (1 - p1) + p2 * (1 - p2)) / delta ** 2


def mde(n: int, p1: float) -> float:
    lo, hi = 0.0, p1
    for _ in range(80):
        d = (lo + hi) / 2
        p2 = p1 - d
        if d >= Z * math.sqrt((p1 * (1 - p1) + p2 * (1 - p2)) / n):
            hi = d
        else:
            lo = d
    return hi


def main() -> None:
    ps = [0.5, 0.6, 0.7, 0.8]
    out = dict(alpha=0.05, power=0.80,
               mde_at_30={str(p): mde(30, p) for p in ps},
               n_per_arm_for_0_10={str(p): math.ceil(n_per_arm(p, 0.10)) for p in ps})
    for p in ps:
        print(f"p1 {p:.1f}: MDE at 30 per arm {out['mde_at_30'][str(p)]:.3f}; "
              f"n per arm for 0.10: {out['n_per_arm_for_0_10'][str(p)]}")
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / "arm_power.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
