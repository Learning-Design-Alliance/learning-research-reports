"""PRE-REGISTERED: what do small AUC gains buy in practice items and minutes?

The end-to-end study measured skill structure in AUC: difficulty only 0.730, no skills 0.792, expert
taxonomy 0.797, blind-built skills 0.799. Gains of 0.002-0.007 look negligible on that scale. This
translates them into a decision a platform makes on every item: is this learner ready to move on?
Written 2026-09-27 after those AUCs were read; no statistic below has been computed.

Reads the frozen build and, through shared.paths.data_path("XES_DIR"), attempts.tsv. No model call.
Split, features and fits are e2e.py's (imported): models M0 (difficulty), M1 (no skills), M2 (expert
leaf KCs), M3 (built skills, all tags), M6 (expert tags + tagger's extra KCs, from
build/expert-tags.json), fitted on TRAIN learners, scored on TEST attempts.

DECISION. Before each TEST attempt a model predicts p. The learner is judged READY if p >= tau.
  premature advance: judged ready, then answers wrong.
  unneeded practice: judged not ready, then answers right (an item given to a learner who could
  already do it).
MATCHED RISK. For each model, tau is set so that premature advance is the same share of wrong
answers for every model: RISK = 0.20 (primary), 0.10 and 0.30 (reported). At matched risk, the
difference in unneeded practice is what the better model saves, the practice counterpart of an AUC
gain.
UNITS. Unneeded practice per 1,000 attempts; items saved per learner over the learner's observed
attempts (median TEST learner); minutes saved using the median duration of a correct attempt
(next start - this start, same learner, 0 < d <= 600 s).
BUILD-UP (arithmetic on the above, reported): minutes per learner per year at 20, 50 and 100
practice items a week over 36 weeks; the same for a cohort of 10,000 learners.
BOOTSTRAP: 200 learner resamples, tau re-set within each draw, for every difference.

VERDICT (primary risk 0.20, built skills M3 vs expert M2)
  SAVES PRACTICE: the lower 95% bound of items saved per 1,000 attempts is above 0.
  COSTS PRACTICE: the upper bound is below 0.   NO DIFFERENCE IN PRACTICE: otherwise.
Reported the same way: M3 vs M1 (skills vs none), M1 vs M0, M6 vs M2.

DIRECTION: symmetric -- no edge enters any model.

    python3 practice_value.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import e2e  # noqa: E402

OUT = HERE / "out"
RISKS = (0.20, 0.10, 0.30)
SEED = e2e.SEED + 23
WEEKLY = (20, 50, 100)
WEEKS = 36
COHORT = 10_000


def unneeded(p, y, risk):
    """Share of correct attempts judged not ready, at the tau giving `risk` premature advances."""
    wrong = np.sort(p[y == 0])
    if len(wrong) == 0:
        return float("nan")
    tau = wrong[min(len(wrong) - 1, int(np.floor((1 - risk) * len(wrong))))]
    return float((p[y == 1] < tau).mean())


def main() -> None:
    rt = e2e.routes()
    built = {q: t["nodes"] for q, t in json.loads((HERE / "build/tags.json").read_text())["tags"].items()}
    tagger = json.loads((HERE / "build/expert-tags.json").read_text())["tags"]
    print("reading attempts")
    rows = e2e.load_attempts()
    uids = [r[0] for r in rows]
    y = np.array([r[5] for r in rows], np.int8)
    ul = {u: i for i, u in enumerate(dict.fromkeys(uids))}
    learner = np.array([ul[u] for u in uids])
    train = np.array([int(hashlib.sha256(u.encode()).hexdigest()[:8], 16) % 5 != 0 for u in uids])
    qlist = sorted({r[3] for r in rows}, key=int)
    qi = {q: i for i, q in enumerate(qlist)}
    qidx = np.array([qi[r[3]] for r in rows])
    E1 = {}
    for r in rows:
        if r[3] not in E1:
            E1[r[3]] = [k for k in r[4].split("_") if k in rt]
    E6 = {q: E1[q] + [k for k in tagger.get(q, []) if k not in E1[q]] for q in E1}
    seq = [(r[0], r[3], r[5]) for r in rows]
    off, _, _ = e2e.difficulty(qidx, y, train)
    blocks = {"off": off[:, None]}
    blocks.update(e2e.features(seq, {"expert": E1, "built": built, "expert6": E6}, {}))
    specs = {"M0": ["off"], "M1": ["off", "U"], "M2": ["off", "U", "K:expert"],
             "M3": ["off", "U", "K:built"], "M6": ["off", "U", "K:expert6"]}
    test = ~train
    yt = y[test].astype(int)
    lt = np.unique(learner[test], return_inverse=True)[1]
    nl = lt.max() + 1
    probs = {}
    for m, bl in specs.items():
        X = np.column_stack([blocks[b] for b in bl]).astype(np.float64)
        beta = e2e.fit_logistic(X[train], y[train].astype(float))
        probs[m] = 1 / (1 + np.exp(-e2e.predict(beta, X[test])))
        print("fitted", m)
    # durations and attempts per learner
    dur = []
    idx_test = np.nonzero(test)[0]
    for r in idx_test:
        if r + 1 < len(rows) and rows[r + 1][0] == rows[r][0] and rows[r][5]:
            d = (rows[r + 1][1] - rows[r][1]) / 1000
            if 0 < d <= 600:
                dur.append(d)
    sec_correct = float(np.median(dur))
    attempts_per_learner = float(np.median(np.bincount(lt)))
    per = {}
    rng = np.random.default_rng(SEED)
    comps = [("M3", "M2"), ("M3", "M1"), ("M1", "M0"), ("M6", "M2")]
    for risk in RISKS:
        point = {m: unneeded(p, yt, risk) for m, p in probs.items()}
        draws = {f"{a}-{b}": [] for a, b in comps}
        for _ in range(200):
            w = np.bincount(rng.integers(0, nl, nl), minlength=nl)
            rep = np.repeat(np.arange(len(yt)), w[lt])
            u = {m: unneeded(probs[m][rep], yt[rep], risk) for m in probs}
            for a, b in comps:
                draws[f"{a}-{b}"].append((u[b] - u[a]))
        share_correct = float(yt.mean())
        res = {"unneeded_share_of_correct": point}
        for a, b in comps:
            k = f"{a}-{b}"
            saved = (point[b] - point[a]) * share_correct * 1000
            d = np.array(draws[k]) * share_correct * 1000
            res[k] = {"items_saved_per_1000_attempts": saved,
                      "lo": float(np.percentile(d, 2.5)), "hi": float(np.percentile(d, 97.5)),
                      "items_saved_per_learner": saved / 1000 * attempts_per_learner,
                      "minutes_saved_per_learner": saved / 1000 * attempts_per_learner * sec_correct / 60,
                      "build_up_minutes_per_year": {str(wk): saved / 1000 * wk * WEEKS * sec_correct / 60 for wk in WEEKLY},
                      "build_up_cohort_hours_per_year": {str(wk): saved / 1000 * wk * WEEKS * sec_correct / 3600 * COHORT
                                                          for wk in WEEKLY}}
        per[str(risk)] = res
    prim = per["0.2"]["M3-M2"]
    verdict = ("SAVES PRACTICE" if prim["lo"] > 0 else "COSTS PRACTICE" if prim["hi"] < 0 else "NO DIFFERENCE IN PRACTICE")
    out = {"median_seconds_per_correct_attempt": sec_correct, "median_test_attempts_per_learner": attempts_per_learner,
           "by_risk": per, "verdict_M3_vs_M2": verdict}
    OUT.mkdir(exist_ok=True)
    (OUT / "practice-value-result.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"median {sec_correct:.1f} s per correct attempt; {attempts_per_learner:.0f} test attempts per learner")
    for risk, res in per.items():
        print(f"risk {risk}: unneeded share of correct {({m: round(v, 4) for m, v in res['unneeded_share_of_correct'].items()})}")
        for a, b in comps:
            r = res[f"{a}-{b}"]
            print(f"   {a} vs {b}: {r['items_saved_per_1000_attempts']:+.1f} items /1000 [{r['lo']:+.1f}, {r['hi']:+.1f}]; "
                  f"{r['minutes_saved_per_learner']:+.1f} min per learner; year at 50/wk {r['build_up_minutes_per_year']['50']:+.0f} min")
    print("VERDICT:", verdict)


if __name__ == "__main__":
    main()
