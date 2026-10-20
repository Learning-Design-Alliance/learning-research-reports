"""Seeds that survive a restart.

Two studies seeded their arms with `SEED + ... + hash(name) % 1000`, where `name` is an arm label.
Python randomises `hash` of a string per process, so that offset was a different number on every
launch. Three consequences, all of them silent:

* the disk cache in `shared/llm.py` never hit on a relaunch, because the cache key includes the
  seed. Its whole reason for existing is that "a run that dies at call 60 of 480 should not repay
  for the first 60", and the container restarts that killed runs repeatedly this programme did
  exactly that -- repaid, and redrew.
* neither study was reproducible. Re-running `studies/producers/claim-critic/design_instinct.py` or
  `studies/producers/claim-critic/replicate_both.py` samples a different set of seeds, so the numbers move and
  nothing says why.
* a relaunch mid-run mixed seeds within one arm, which is a confound rather than a nuisance: the
  arms are compared to each other, and only one of them gets re-drawn.

`arm_seed` is the fix. It is a digest, not `hash`, so it is the same integer in every process, on
every machine, forever. Integers hash to themselves in CPython, so a seed built only from ints was
never affected -- it is specifically string and tuple-of-string keys that move.
"""

from __future__ import annotations

import hashlib

__all__ = ["stable_hash", "arm_seed"]


def stable_hash(key: object, *, mod: int = 2 ** 32) -> int:
    """A deterministic non-negative digest of `key`'s repr, replacing `hash` where it is persisted.

    `repr` rather than `str` so that `("a", "b")` and `"('a', 'b')"` do not collide, and so tuples
    of mixed types work without the caller flattening them first."""
    d = hashlib.sha256(repr(key).encode("utf-8")).hexdigest()
    return int(d, 16) % mod


def arm_seed(base: int, arm: str, *offsets: int, spread: int = 1000) -> int:
    """The seed for one arm of one draw: `base`, the per-draw offsets, and a stable arm offset."""
    return base + sum(offsets) + stable_hash(arm, mod=spread)
