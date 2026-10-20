"""
One learner model, so results from different experiments mean the same thing.

An audit of nine experiments found **five** different learner models in use:

    time_to_outcome.py        binary held/not-held, conjunctive hard gate
    levers.py, tolerance.py   binary, soft prerequisite penalty
    chunking.py               strength, element-count load, penalty
    fading.py                 strength, element-count load
    world_model.py            strength, elements, environment, fixed budget
    orientation_difficulty.py conjunctive gate with slip and guess
    nodes.py, conflation_detect.py   binary

Each file is internally consistent, which is exactly why the drift was invisible: nothing ever
failed. But a number produced under a hard conjunctive gate and a number produced under soft
prerequisites are not comparable, and several load-bearing results — the 10:1 node-to-edge cost
ratio above all — were measured under assumptions the model has since replaced.

This is that model in one place, parameterised so the OLD behaviour is a setting rather than a
different file. `Model.legacy_binary()` reproduces the original conjunctive world, so a past result
can be re-derived and only then re-run under current assumptions. A difference then means the
assumptions moved the result, rather than that two scripts disagreed.

## The model

    elements(c)      = 1 + SUM over prerequisites p of (1 - s_p)     chunking; an automated
                                                                     prerequisite stops being a
                                                                     separate element
    hours_needed(c)  = BASE × exp(λ(diff_c - θ)) × elements(c) ** γ
    s_c              = 1 - exp(-hours_spent / hours_needed)          Carroll: degree of learning is
                                                                     time spent over time needed
    scaffold p while s_p < 1 - κ                                     expertise reversal as a
                                                                     threshold

Binary mastery is the limit of this as strength is thresholded, and the hard conjunctive gate is
the limit as γ grows without bound. Both are reachable from the same code.

## What is measured and what is assumed

Assumed, and flagged as such at every use: κ, γ, the element-count form itself, and the repair and
prune rates. `studies/simulation/validate/` holds the attempt to estimate the ones real data can reach and the
argument for why the facilitation parameters cannot be reached from public archives.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

BASE_HOURS = 1.0
LAMBDA = 0.55
NOISE_SD = 0.30


@dataclass
class Model:
    """The knobs, with their defaults and their provenance.

    gamma:   load exponent on element count. ASSUMED. 0 recovers a model where prerequisites do not
             affect difficulty at all, which is the null worth keeping reachable.
    kappa:   scaffold attention cost, so a scaffold is worth using while strength < 1 - kappa.
             ASSUMED; `studies/simulation/validate/scaffold_threshold.py` is the attempt to estimate it.
    binary:  threshold strength into held/not-held at `mastery`, reproducing the older experiments.
    gate:    refuse to teach a capability whose prerequisites are not held. The original conjunctive
             assumption. Under it, remediation depth has no optimum because deeper is always better.
    """
    gamma: float = 1.0
    kappa: float = 0.35
    mastery: float = 0.8
    binary: bool = False
    gate: bool = False
    lam: float = LAMBDA
    noise_sd: float = NOISE_SD

    @classmethod
    def legacy_binary(cls) -> "Model":
        """The world every pre-strength result was measured in. Kept so those numbers can be
        reproduced before being re-run, rather than merely contradicted."""
        return cls(gamma=0.0, binary=True, gate=True)

    def elements(self, c, parents, strength, scaffolded=()) -> float:
        total = 1.0
        for p in parents:
            total += self.kappa if p in scaffolded else (1.0 - self.held(strength, p))
        return total

    def held(self, strength, c) -> float:
        """Strength, or its thresholded shadow when reproducing a binary experiment."""
        s = strength.get(c, 0.0)
        return (1.0 if s >= self.mastery else 0.0) if self.binary else s

    def scaffold_set(self, parents, strength, in_slice=None):
        """Which prerequisites a scaffold is worth building for. A scaffold can only exist for a
        capability the author knew about, so `in_slice` bounds it."""
        return {p for p in parents
                if (in_slice is None or p in in_slice)
                and self.held(strength, p) < 1 - self.kappa}

    def hours_needed(self, c, ability, diff, parents, strength, scaffolded=(), rng=None) -> float:
        if self.gate and any(self.held(strength, p) < self.mastery for p in parents):
            return math.inf                  # conjunctive: cannot be taught yet
        load = self.elements(c, parents, strength, scaffolded) ** self.gamma
        noise = math.exp(rng.gauss(0, self.noise_sd)) if rng else 1.0
        return BASE_HOURS * math.exp(self.lam * (diff[c] - ability)) * load * noise

    def strength_after(self, hours, needed) -> float:
        """Carroll. Binary mode masters the capability exactly when the time spent covers the time
        needed, which is the older experiments' rule: one slot, mastered iff ability beats
        difficulty. Thresholding the continuous curve instead would demand hours >= 1.61 x needed
        and reproduce nothing — the LEGACY arm of `nodes_remodel.py` caught that."""
        if needed == math.inf or needed <= 0:
            return 0.0
        if self.binary:
            return self.mastery if hours >= needed else 0.0
        return 1 - math.exp(-hours / needed)


def selftest() -> None:
    """The properties that make the legacy setting a real reproduction rather than a label."""
    fails = []
    rng = random.Random(0)
    diff = {0: 0.0, 1: 0.5}

    m = Model()
    s = {0: 0.0}
    a = m.hours_needed(1, 0.0, diff, [0], s, rng=None)
    s2 = {0: 1.0}
    b = m.hours_needed(1, 0.0, diff, [0], s2, rng=None)
    if not b < a:
        fails.append("an automated prerequisite should make a capability cheaper")

    # gamma 0 removes the prerequisite effect entirely -- the null must be reachable.
    m0 = Model(gamma=0.0)
    if abs(m0.hours_needed(1, 0.0, diff, [0], s) - m0.hours_needed(1, 0.0, diff, [0], s2)) > 1e-9:
        fails.append("gamma 0 should make prerequisite strength irrelevant")

    # The gate is the hard conjunctive world.
    mg = Model.legacy_binary()
    if mg.hours_needed(1, 0.0, diff, [0], {0: 0.0}) != math.inf:
        fails.append("legacy gate should refuse a capability with unheld prerequisites")
    if mg.hours_needed(1, 0.0, diff, [0], {0: 1.0}) == math.inf:
        fails.append("legacy gate should allow one whose prerequisites are held")

    # Binary mode must quantise strength AND fire exactly where the older experiments did:
    # one slot of instruction masters a capability iff ability beats difficulty.
    got = mg.strength_after(100.0, 1.0)
    if got not in (0.0, mg.mastery):
        fails.append(f"binary strength should be 0 or mastery, got {got}")
    for th, dd, want in ((0.29, 0.3, False), (0.31, 0.3, True), (1.0, 0.3, True)):
        need = mg.hours_needed(0, th, {0: dd}, [], {})
        if (mg.strength_after(1.0, need) > 0) != want:
            fails.append(f"legacy: ability {th} vs difficulty {dd} should be mastered={want}")

    # The scaffold threshold must sit where the algebra says.
    m = Model(kappa=0.3)
    if m.scaffold_set([0], {0: 0.69}) != {0} or m.scaffold_set([0], {0: 0.71}) != set():
        fails.append("scaffold set should switch at 1 - kappa")
    if m.scaffold_set([0], {0: 0.0}, in_slice=set()) != set():
        fails.append("a capability outside the slice cannot be scaffolded")

    for f in fails:
        print("FAIL", f)
    print(f"{'FAILED' if fails else 'passed'}: {len(fails)} failures")
    raise SystemExit(1 if fails else 0)


if __name__ == "__main__":
    selftest()
