"""POST-HOC (written 2026-09-25, after the gated floor was seen to fail): is the failure a power floor?

With the reachability gate inside `positivity_states()`, the pre-registered detection floor
(`overlap_iita.py floor`, 3,000 learners) fails one unknown-share check: on the soft arm only 37.5%
of IITA's assertions land in a decided cell against a 50% floor, so READING 1 (prior vs constraint,
from the UNKNOWN share) is WITHHELD. This reruns the same two arms, same seeds and thresholds,
changing only the learner count, to see whether the gated audit recovers with sample size.

It is a sensitivity analysis. It cannot relicense Reading 1 on any corpus: the floor's learners
meet items in randomised order and the real corpora do not. It says whether 3,000 was simply too
few for the gate's merge-node power requirement, and so at what scale the floor would be read.

DIRECTION: inherited from `overlap_iita.floor_arm`, which runs the reversed-arrow control on the
planted relation (`reversed_arrow` is recorded per arm below).

    python3 floor_scale.py [--n 3000,10000,30000] [--out out/floor-scale.json]
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import overlap_iita as OI  # noqa: E402

KEYS = ("decided", "asserted_decided", "planted_supported", "asserted_supported",
        "asserted_contradicted", "precision", "recall")


def arms_at(n: int) -> dict:
    orig = OI.planted_corpus
    OI.planted_corpus = lambda rng, _n, items, gate: orig(rng, n, items, gate)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            soft = OI.floor_arm("soft", OI.PLANT_SOFT, "")
            hard = OI.floor_arm("hard", OI.PLANT_HARD, "")
    finally:
        OI.planted_corpus = orig
    lo = OI.FLOOR_MIN_ASSERTED_DECIDED
    reading1 = (soft["asserted_decided"] >= lo and hard["asserted_decided"] >= lo
                and hard["asserted_supported"] > 0
                and (soft["asserted_contradicted"] > 0 or hard["asserted_contradicted"] > 0))
    return dict(soft={k: soft[k] for k in KEYS} | {"reversed_arrow": soft["reversed_arrow"]["verdict"]},
                hard={k: hard[k] for k in KEYS} | {"reversed_arrow": hard["reversed_arrow"]["verdict"]},
                reading1_checks_pass=reading1)


def main() -> None:
    ns = [int(x) for x in sys.argv[sys.argv.index("--n") + 1].split(",")] if "--n" in sys.argv \
        else [3000, 10000, 30000]
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv \
        else HERE / "out/floor-scale.json"
    res = {}
    print(f"{'learners':>9}  {'arm':<5}{'decided':>9}{'assert dec':>12}{'planted sup':>13}"
          f"{'a&S':>5}{'a&C':>5}   reading-1 checks")
    for n in ns:
        r = arms_at(n)
        res[str(n)] = r
        for arm in ("soft", "hard"):
            a = r[arm]
            print(f"{n:>9,}  {arm:<5}{a['decided']:>9.1%}{a['asserted_decided']:>12.1%}"
                  f"{a['planted_supported']:>13.1%}{a['asserted_supported']:>5}"
                  f"{a['asserted_contradicted']:>5}   "
                  f"{('PASS' if r['reading1_checks_pass'] else 'fail') if arm == 'hard' else ''}",
                  flush=True)
    out.write_text(json.dumps(dict(post_hoc=True, floor_min_asserted_decided=OI.FLOOR_MIN_ASSERTED_DECIDED,
                                   by_learners=res), indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
