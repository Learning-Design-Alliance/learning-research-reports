"""PRE-REGISTERED: how much of an item's difficulty is the skills it combines, and how much is left over?

"Difficulty" predicts most of what learners get right, but explains little: it mixes the skills an item
demands, how many it tangles together, its wording and format, and when learners meet it. If a hard
item is hard because it combines several skills, it can be broken into smaller, more digestible
pieces; if its difficulty is not explained by its skills, something is hidden (an untagged skill, a
format effect) or it is idiosyncratic. Written 2026-09-27; no statistic below has been computed.

Reads the frozen builds (build/tags.json, build/expert-tags.json, build/attributes.json) and, through
shared.paths.data_path("XES_DIR"), attempts.tsv and cid2route.json. No model call.

ITEMS: questions with >= 60 TRAIN attempts. DIFFICULTY: logit of the TRAIN error rate, shrunk as in
e2e.py. RELIABILITY CEILING: TRAIN learners split in two by sha256(uid) parity; difficulty from each
half; Spearman-Brown corrected Pearson correlation between halves = the share of difficulty variance
that is reliable, so the most any item description could explain.

DECOMPOSITION (ridge regression, lambda = 1.0 on 0/1 skill indicators, 5-fold cross-validation over
items, seeded; out-of-fold R^2 against the item difficulties):
  A_expert   additive in expert leaf KCs (difficulty = sum of the item's skill effects)
  A_built1   additive in the primary built node only
  A_built    additive in all built nodes the tagger gave
  A_mixed    additive in expert KCs + tagger's extra expert KCs (e2e's E3)
  +count     A_built + number of built skills on the item (integration cost of combining skills)
  +attrs     +count + mean panel load and keyed level of the item's primary node
DECOMPOSABLE SHARE = out-of-fold R^2 of A_built divided by the reliability ceiling.
INTEGRATION COST = the coefficient on skill count in +count (difficulty logits per extra skill),
interval by 2,000 bootstraps over items (refit on each draw, in-sample).

VERDICTS
  D1 decomposability (A_built): LARGELY DECOMPOSABLE if the decomposable share >= 0.5; PARTLY
     DECOMPOSABLE if 0.2-0.5; MOSTLY NOT DECOMPOSABLE if < 0.2.
  D2 combining: INTEGRATION COST if the skill-count coefficient's 95% interval is above 0; COMBINING IS
     ADDITIVE if it spans 0; COMBINING IS EASIER THAN ITS PARTS if below 0.
  Reported: every model's out-of-fold R^2 and share of the ceiling; mean difficulty by number of
  built skills (1, 2, 3); the share of reliable difficulty left unexplained by the best model.

DIRECTION: symmetric -- no edge enters.

    python3 difficulty.py
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
SEED = e2e.SEED + 29
MIN_ATTEMPTS = 60
LAMBDA = 1.0


def shrunk_logit(c, n, g):
    p = (c + 5 * g) / (n + 5)
    return np.log((1 - p) / p)            # difficulty = logit of error


def design(items, tagsets, extra=None):
    vocab = sorted({t for q in items for t in tagsets.get(q, [])})
    ix = {t: i for i, t in enumerate(vocab)}
    X = np.zeros((len(items), len(vocab) + (extra.shape[1] if extra is not None else 0)))
    for r, q in enumerate(items):
        for t in tagsets.get(q, []):
            X[r, ix[t]] = 1.0
    if extra is not None:
        X[:, len(vocab):] = extra
    return X


def ridge(X, y, lam):
    mu = y.mean()
    A = X.T @ X + lam * np.eye(X.shape[1])
    return np.linalg.solve(A, X.T @ (y - mu)), mu


def cv_r2(X, y, rng):
    folds = rng.permutation(len(y)) % 5
    pred = np.zeros(len(y))
    for f in range(5):
        tr, te = folds != f, folds == f
        b, mu = ridge(X[tr], y[tr], LAMBDA)
        pred[te] = mu + X[te] @ b
    return float(1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum())


def main() -> None:
    rt = e2e.routes()
    built = {q: t["nodes"] for q, t in json.loads((HERE / "build/tags.json").read_text())["tags"].items()}
    tagger = json.loads((HERE / "build/expert-tags.json").read_text())["tags"]
    att = json.loads((HERE / "build/attributes.json").read_text())
    level = {q: t["level"] for q, t in json.loads((HERE / "build/tags.json").read_text())["tags"].items()}
    print("reading attempts")
    rows = e2e.load_attempts()
    n = {}; c = {}; nh = [{}, {}]; ch = [{}, {}]; expert = {}
    for u, t, k, q, cs, ok in rows:
        if int(hashlib.sha256(u.encode()).hexdigest()[:8], 16) % 5 == 0:
            continue                                        # TEST learners never enter
        h = int(hashlib.sha256(u.encode()).hexdigest()[8:16], 16) % 2
        n[q] = n.get(q, 0) + 1; c[q] = c.get(q, 0) + ok
        nh[h][q] = nh[h].get(q, 0) + 1; ch[h][q] = ch[h].get(q, 0) + ok
        if q not in expert:
            expert[q] = [x for x in cs.split("_") if x in rt]
    items = sorted([q for q in n if n[q] >= MIN_ATTEMPTS and built.get(q)], key=int)
    g = sum(c.values()) / sum(n.values())
    y = shrunk_logit(np.array([c[q] for q in items], float), np.array([n[q] for q in items], float), g)
    halves = [shrunk_logit(np.array([ch[h].get(q, 0) for q in items], float),
                           np.array([nh[h].get(q, 0) for q in items], float), g) for h in (0, 1)]
    r = float(np.corrcoef(halves[0], halves[1])[0, 1])
    ceiling = 2 * r / (1 + r)
    mixed = {q: expert[q] + [k for k in tagger.get(q, []) if k not in expert[q]] for q in items}
    count = np.array([[len(built[q])] for q in items], float)
    load = np.array([np.mean([att.get(x, {}).get("load") or 3.0 for x in built[q][:1]]) for q in items])
    lev = np.array([level.get(q) or 2 for q in items], float)
    rng = np.random.default_rng(SEED)
    models = {"A_expert": design(items, expert), "A_built1": design(items, {q: built[q][:1] for q in items}),
              "A_built": design(items, built), "A_mixed": design(items, mixed),
              "+count": design(items, built, count),
              "+attrs": design(items, built, np.column_stack([count[:, 0], load, lev]))}
    r2 = {m: cv_r2(X, y, np.random.default_rng(SEED)) for m, X in models.items()}
    share = {m: v / ceiling for m, v in r2.items()}
    # integration cost: coefficient on skill count, in-sample, bootstrap over items
    Xc = models["+count"]
    b, _ = ridge(Xc, y, LAMBDA)
    coef = float(b[-1])
    boots = []
    for _ in range(2000):
        i = rng.integers(0, len(y), len(y))
        bb, _ = ridge(Xc[i], y[i], LAMBDA)
        boots.append(bb[-1])
    lo, hi = float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))
    dshare = share["A_built"]
    d1 = ("LARGELY DECOMPOSABLE" if dshare >= 0.5 else "PARTLY DECOMPOSABLE" if dshare >= 0.2 else "MOSTLY NOT DECOMPOSABLE")
    d2 = ("INTEGRATION COST" if lo > 0 else "COMBINING IS EASIER THAN ITS PARTS" if hi < 0 else "COMBINING IS ADDITIVE")
    by_count = {int(k): float(y[count[:, 0] == k].mean()) for k in (1, 2, 3) if (count[:, 0] == k).any()}
    best = max(r2, key=r2.get)
    res = {"items": len(items), "reliability_ceiling": ceiling, "split_half_r": r, "oof_r2": r2, "share_of_ceiling": share,
           "skill_count_coef_logits": coef, "skill_count_ci": [lo, hi], "mean_difficulty_by_skill_count": by_count,
           "best_model": best, "unexplained_reliable_share": 1 - share[best], "D1": d1, "D2": d2}
    OUT.mkdir(exist_ok=True)
    (OUT / "difficulty-result.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
