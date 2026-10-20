"""PRE-REGISTERED: is the local (curricular) layer larger for learners with less prior knowledge?

invariance.py found a cross-curricular core (b_other +0.125) inside a larger local layer (b_prox
+0.363). One reading: learners with gaps lean on how things are taught together, while learners who
know more carry structure that holds anywhere. The opposite is also plausible: learners who know more
have absorbed their own curriculum's grouping. Written 2026-09-27 after invariance.py's result was
read; no statistic below has been computed.

Same corpora, primary map (out/unit-map.json), cells and pair statistics as invariance.py, imported.
Learners are split within each corpus at the median of their overall accuracy on mapped attempts
(learners with >= 20 mapped attempts): LOW and HIGH. pair_stats and cross() run on each half
separately. Differences between halves use the two halves' bootstrap draws (independent learners).

DIRECTION: symmetric -- as invariance.py.

VERDICTS (95% interval of the HIGH minus LOW difference)
  local layer: LOCAL LAYER LARGER FOR LOW-PRIOR LEARNERS if b_prox(high) - b_prox(low) < 0 throughout;
     LARGER FOR HIGH-PRIOR LEARNERS if > 0 throughout; NO DIFFERENCE BY PRIOR KNOWLEDGE otherwise.
  core: CORE STRONGER FOR HIGH-PRIOR LEARNERS / FOR LOW-PRIOR LEARNERS / NO DIFFERENCE, the same way
     on b_other.
  Caveat stated in advance: splitting on accuracy restricts its range within each half, which shrinks
  partial correlations; coefficients are standardised within each regression, so the comparison is
  of relative weights, not raw dependence.

    python3 prior_split.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import invariance as inv  # noqa: E402

OUT = HERE / "out"
MIN_ATTEMPTS = 20


def main() -> None:
    umap = json.loads(inv.MAP.read_text())["maps"][inv.MAPPER]
    halves = {"low": {}, "high": {}}
    for corpus in inv.CORPORA:
        print("reading", corpus)
        by = inv.cells(corpus, umap.get(corpus, {}))
        acc = {}
        for l, cs in by.items():
            n = sum(v[0] for v in cs.values())
            if n >= MIN_ATTEMPTS:
                acc[l] = sum(v[1] for v in cs.values()) / n
        med = float(np.median(list(acc.values())))
        for name, keep in (("low", lambda a: a < med), ("high", lambda a: a >= med)):
            sub = {l: by[l] for l, a in acc.items() if keep(a)}
            halves[name][corpus] = inv.pair_stats(sub)
            print(f"   {name}: {len(sub)} learners, {len(halves[name][corpus])} pairs")
    res = {}
    for name in ("low", "high"):
        res[name] = inv.cross(halves[name], np.random.default_rng(inv.SEED + (0 if name == "low" else 1)))
    out = {}
    for coef, key in (("b_prox", "_boot_prox"), ("b_other", "_boot_other")):
        lo_d, hi_d = np.array(res["low"][key]), np.array(res["high"][key])
        d = hi_d - lo_d
        out[coef] = {"low": res["low"]["pooled_" + coef], "high": res["high"]["pooled_" + coef],
                     "high_minus_low": float(res["high"]["pooled_" + coef] - res["low"]["pooled_" + coef]),
                     "ci": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]}
    bp, bo = out["b_prox"]["ci"], out["b_other"]["ci"]
    v_local = ("LOCAL LAYER LARGER FOR LOW-PRIOR LEARNERS" if bp[1] < 0 else
               "LOCAL LAYER LARGER FOR HIGH-PRIOR LEARNERS" if bp[0] > 0 else "NO DIFFERENCE BY PRIOR KNOWLEDGE")
    v_core = ("CORE STRONGER FOR LOW-PRIOR LEARNERS" if bo[1] < 0 else
              "CORE STRONGER FOR HIGH-PRIOR LEARNERS" if bo[0] > 0 else "NO DIFFERENCE BY PRIOR KNOWLEDGE")
    result = {"coefficients": out, "verdict_local": v_local, "verdict_core": v_core,
              "verdict_by_half": {h: res[h]["verdict"] for h in res},
              "per_pair": {h: res[h]["per_pair"] for h in res}}
    (OUT / "prior-split-result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "per_pair"}, indent=1))


if __name__ == "__main__":
    main()
