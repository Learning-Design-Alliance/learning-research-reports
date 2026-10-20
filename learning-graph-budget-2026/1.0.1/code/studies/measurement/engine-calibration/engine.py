"""PRE-REGISTERED (as a definition, not a test): Lazuli's mastery inference engine, replayed.

The engine as implemented in the product repo on 2026-09-27, read-only from:
  knowledge/areas/learning-records/mastery-and-inference.md   (the contract)
  services/lazuli-app/src/lib/mastery/beta-mass.ts            (MCQ evidence mass)
  services/lazuli-app/src/lib/ai/assessMultipleChoice.ts      (what state the mass is sized from)
  services/lazuli-fastapi/src/actions/inference_lib.py        (prior, bound, decay, update)

E0, THE ENGINE. A Beta(alpha, beta) belief per (learner, competency), starting at the Jeffreys prior
(0.5, 0.5). For a graded response (s = 1 correct, 0 wrong) on an item with m options:
  c = 1/m if the item is multiple choice and m >= 2, else 0;   a = 1, b = 0 (fixed placeholders)
  p = alpha / max(alpha + beta, EPS);   p* = clamp((p - c) / max(1 - c, EPS), EPS, 1 - EPS)
  theta = logit(p*);   L = sigmoid(a (theta - b));   P = c + (1 - c) L
  info = a^2 L (1 - L) ((1 - c) L / max(P, EPS))
  M = K lambda^max(0, attempt - 1) clamp(sourceWeight, 0.4, 2) (MASS_FLOOR + info),
      K = 3, lambda = 0.8, MASS_FLOOR = 0.05, sourceWeight = 1, EPS = 1e-6
  delta alpha = M s, delta beta = M (1 - s)
The mass is sized from the STORED belief (assessMultipleChoice reads the agent profile the engine
last wrote; it is not decayed). The engine then bounds the evidence (mass > 3 is rescaled to 3,
direction kept -- never binds for these masses unless a calibrated a exceeds ~2), decays the stored
state by the elapsed time since its timestamp, t in days:
  r = (1 + v t)^(-d), v = 0.1/day, d = 0.5;  alpha' = max(1e-9, r alpha + (1 - r) 0.5), same for beta
(no decay when t <= 0, including the first response, whose prior carries the time of the call),
and adds: alpha = max(1e-9, alpha' + delta alpha). Decay is lazy: nothing moves between responses and
nothing is decayed on read. The engine's prediction for a response is the mass model's own P from
the stored state (`finalItemResponseTheoryPrediction` in the diagnostics it stamps).

Parent propagation (`generate_parent_assertions`) hands each parent the child's increment times an
edge weight. It never writes back to the child, so a replay of leaf competencies is exact without
it; parents are not evaluated here.

GENERALISATIONS (the variants' knobs; every one reduces to E0 at its default):
  item arrays a, b, c, d (d = 1 - slip, the 4PL upper asymptote); with d = 1 exactly the formulas
    above are used verbatim, otherwise P = c + (d - c) L, p* = (p - c) / (d - c) and the 4PL
    information a^2 L^2 (1 - L)^2 (d - c)^2 / (P (1 - P)), which equals the engine's at d = 1;
  mode "raw" (the engine: the belief counts correct answers) or "know" (the belief counts evidence
    of knowing: p* = p, and the direction is s_eff below);
  eff "post": s_eff = P(know | response) = d L / P if correct, (1 - d) L / (1 - P) if wrong;
      "lr":   s_eff = d / (c + d) if correct, (1 - d) / (2 - c - d) if wrong (the same at L = 1/2);
  decay (v, d, toward "prior" | "zero"), read = True decays to the response time BEFORE sizing and
    predicting (decay on read) instead of after.

CHECK (run by `python3 engine.py`): the vectorised replay equals a line-by-line scalar transcription
of the TypeScript and Python above to 1e-12 on 2,000 random sequences (MC and fill-in, retries, gaps
from seconds to a year), and the retention table pinned by the product's test_retention_table is
reproduced (1 h 99.8%, 1 d 95.3%, 1 wk 76.7%, 30 d 50.0%, 1 yr 16.3%).

DIRECTION: symmetric -- no edge enters; "direction" here is the evidence split alpha : beta.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

K = 3.0
LAMBDA = 0.8
MASS_FLOOR = 0.05
EPS = 1e-6
MAX_EVIDENCE_MASS = 3.0
PRIOR = 0.5
DAY = 86_400.0
V0, D0 = 0.1, 0.5


def half_life_days(v: float, d: float) -> float:
    return float("inf") if v <= 0 else (2 ** (1 / d) - 1) / v


@dataclass
class Params:
    a: np.ndarray
    b: np.ndarray
    c: np.ndarray
    d: np.ndarray
    mode: str = "raw"
    eff: str = "post"
    v: float = V0
    dd: float = D0
    toward: str = "prior"
    read: bool = False
    name: str = "E0"
    meta: dict = field(default_factory=dict)

    def replace(self, **kw) -> "Params":
        out = Params(**{**self.__dict__, **kw})
        out.meta = dict(self.meta)
        return out


def engine_params(is_mc: np.ndarray, m: np.ndarray, name="E0") -> Params:
    """E0: c = 1/m for multiple choice with m >= 2, else 0; a = 1, b = 0, d = 1."""
    I = len(m)
    c = np.where(is_mc & (m >= 2), 1.0 / np.maximum(m, 1), 0.0)
    return Params(np.ones(I), np.zeros(I), c, np.ones(I), name=name)


def sigmoid(z):
    z = np.asarray(z, float)
    out = np.empty_like(z)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    ez = np.exp(z[~pos])
    out[~pos] = ez / (1.0 + ez)
    return out


def item_model(A, B, a, b, c, d, mode):
    """-> theta, L, P, info, exactly as beta-mass.ts when d == 1 and mode == 'raw'."""
    p = A / np.maximum(A + B, EPS)
    if mode == "raw":
        p_star = np.clip((p - c) / np.maximum(d - c, EPS), EPS, 1 - EPS)
    else:
        p_star = np.clip(p, EPS, 1 - EPS)
    theta = np.log(p_star / (1 - p_star))
    L = sigmoid(a * (theta - b))
    P = c + (d - c) * L
    three = a * a * L * (1 - L) * (((1 - c) * L) / np.maximum(P, EPS))
    four = a * a * L * L * (1 - L) ** 2 * (d - c) ** 2 / np.maximum(P * (1 - P), EPS)
    info = np.where(d == 1.0, three, four)
    return theta, L, P, info


def decay(A, B, dt, v, dd, toward):
    if v <= 0 or dd <= 0:
        return A, B
    pos = dt > 0
    r = np.where(pos, (1.0 + v * np.maximum(dt, 0) / DAY) ** (-dd), 1.0)
    if toward == "prior":
        return np.maximum(1e-9, A * r + PRIOR * (1 - r)), np.maximum(1e-9, B * r + PRIOR * (1 - r))
    return np.maximum(1e-9, A * r), np.maximum(1e-9, B * r)


class Events:
    """Rows = (attempt, competency), sorted by pair then time then file order.
    pair: dense (learner, competency) id; item: dense item id; t: seconds; y: 0/1; att: attempt index
    on the item (1-based); attempt: dense attempt id (rows of one attempt share it)."""

    def __init__(self, pair, item, t, y, att, attempt, learner):
        self.pair, self.item = pair.astype(np.int64), item.astype(np.int64)
        self.t, self.y = t.astype(np.float64), y.astype(np.float64)
        self.att, self.attempt, self.learner = att.astype(np.int64), attempt.astype(np.int64), learner.astype(np.int64)
        n = len(pair)
        assert np.all(np.diff(self.pair) >= 0), "rows must be sorted by pair"
        start = np.r_[True, self.pair[1:] != self.pair[:-1]]
        first = np.maximum.accumulate(np.where(start, np.arange(n), 0))
        self.rank = np.arange(n) - first
        self.gap = np.where(start, 0.0, self.t - np.r_[self.t[:1], self.t[:-1]])
        self.first = start
        self.npair = int(self.pair.max()) + 1 if n else 0
        order = np.argsort(self.rank, kind="stable")
        cnt = np.bincount(self.rank)
        self.steps = np.split(order, np.cumsum(cnt)[:-1])
        self.natt = int(self.attempt.max()) + 1 if n else 0

    def subset(self, mask):
        """Rows of whole pairs (mask must be constant within a pair), re-indexed."""
        idx = np.nonzero(mask)[0]
        pair = np.unique(self.pair[idx], return_inverse=True)[1]
        attempt = np.unique(self.attempt[idx], return_inverse=True)[1]
        return Events(pair, self.item[idx], self.t[idx], self.y[idx], self.att[idx], attempt, self.learner[idx])

    def attempt_mean(self, x):
        return np.bincount(self.attempt, x, self.natt) / np.bincount(self.attempt, None, self.natt)


def replay(ev: Events, prm: Params, rng=None):
    """-> dict(P, theta, s, M, y per row; A, B final per pair). With rng, each response is DRAWN from the
    variant's own P instead of read from ev.y (the variant as a generative model)."""
    n = len(ev.pair)
    P, TH, S, MM, Y = np.empty(n), np.empty(n), np.empty(n), np.empty(n), np.empty(n)
    A = np.full(ev.npair, PRIOR)
    B = np.full(ev.npair, PRIOR)
    a_i, b_i, c_i, d_i = prm.a[ev.item], prm.b[ev.item], prm.c[ev.item], prm.d[ev.item]
    watt = LAMBDA ** np.maximum(0, ev.att - 1)
    for idx in ev.steps:
        pr = ev.pair[idx]
        a0, b0 = A[pr], B[pr]
        gap = ev.gap[idx]
        if prm.read:
            a0, b0 = decay(a0, b0, gap, prm.v, prm.dd, prm.toward)
        a, b, c, d = a_i[idx], b_i[idx], c_i[idx], d_i[idx]
        theta, L, Pp, info = item_model(a0, b0, a, b, c, d, prm.mode)
        M = K * watt[idx] * 1.0 * (MASS_FLOOR + info)
        y = ev.y[idx] if rng is None else (rng.random(len(idx)) < Pp).astype(float)
        if prm.mode == "raw":
            s = y
        elif prm.eff == "post":
            s = np.where(y == 1, d * L / np.maximum(Pp, EPS), (1 - d) * L / np.maximum(1 - Pp, EPS))
        else:
            s = np.where(y == 1, d / (c + d), (1 - d) / np.maximum(2 - c - d, EPS))
        s = np.clip(s, 0.0, 1.0)
        da, db = M * s, M * (1 - s)
        tot = da + db
        sc = np.where(tot > MAX_EVIDENCE_MASS, MAX_EVIDENCE_MASS / np.maximum(tot, EPS), 1.0)
        da, db = da * sc, db * sc
        if not prm.read:
            a0, b0 = decay(a0, b0, gap, prm.v, prm.dd, prm.toward)
        A[pr] = np.maximum(1e-9, a0 + da)
        B[pr] = np.maximum(1e-9, b0 + db)
        P[idx], TH[idx], S[idx], MM[idx], Y[idx] = Pp, theta, s, M, y
    return {"P": P, "theta": TH, "s": S, "M": MM, "y": Y, "A": A, "B": B}


# ---------------------------------------------------------------- the exactness check

def _ts_update(alpha, beta_, is_mc, m, a, b, attempt, s):
    """beta-mass.ts updateBetaMassWeighted, line by line (sourceWeight 1, evidence {s})."""
    c = 1.0 / m if (is_mc and m and m >= 2) else 0.0
    p = alpha / max(alpha + beta_, EPS)
    p_star = max(EPS, min((p - c) / max(1.0 - c, EPS), 1.0 - EPS))
    theta = math.log(p_star / (1.0 - p_star))
    z = a * (theta - b)
    L = 1.0 / (1.0 + math.exp(-z)) if z >= 0 else math.exp(z) / (1.0 + math.exp(z))
    P = c + (1.0 - c) * L
    info = a * a * L * (1.0 - L) * (((1.0 - c) * L) / max(P, EPS))
    w_att = LAMBDA ** max(0, attempt - 1)
    w_src = max(0.4, min(1.0, 2.0))
    M = K * w_att * w_src * (MASS_FLOOR + info)
    s = max(0.0, min(s, 1.0))
    return M * s, M * (1.0 - s), P


def _py_update(prior_alpha, prior_beta, elapsed, pos, neg):
    """inference_lib.py: _bound_evidence, _apply_decay (power-law, toward the prior), add."""
    pos = pos if math.isfinite(pos) and pos > 0 else 0.0
    neg = neg if math.isfinite(neg) and neg > 0 else 0.0
    mass = pos + neg
    if mass > MAX_EVIDENCE_MASS:
        sc = MAX_EVIDENCE_MASS / mass
        pos, neg = pos * sc, neg * sc
    if elapsed > 0:
        retained = (1.0 + V0 * (elapsed / DAY)) ** (-D0)
        faded = 1.0 - retained
        prior_alpha = max(1e-9, prior_alpha * retained + 0.5 * faded)
        prior_beta = max(1e-9, prior_beta * retained + 0.5 * faded)
    return max(1e-9, prior_alpha + pos), max(1e-9, prior_beta + neg)


def check(n_seq=2000, seed=7):
    rng = np.random.default_rng(seed)
    rows = []
    item_mc, item_m = [], []
    for it in range(60):
        mc = it % 3 != 0
        item_mc.append(mc)
        item_m.append(int(rng.integers(1, 6)) if mc else 0)
    item_mc, item_m = np.array(item_mc), np.array(item_m)
    for q in range(n_seq):
        n = int(rng.integers(1, 25))
        t = np.cumsum(np.exp(rng.uniform(0, math.log(3e7), n)) * (rng.random(n) < 0.8))
        for k in range(n):
            rows.append((q, int(rng.integers(60)), float(t[k]), int(rng.random() < 0.6), int(rng.integers(1, 5))))
    pair = np.array([r[0] for r in rows])
    item = np.array([r[1] for r in rows])
    t = np.array([r[2] for r in rows])
    y = np.array([r[3] for r in rows])
    att = np.array([r[4] for r in rows])
    ev = Events(pair, item, t, y, att, np.arange(len(rows)), pair)
    out = replay(ev, engine_params(item_mc, item_m))
    exp_P = np.empty(len(rows))
    fa = {}
    for j, (q, it, tt, yy, at) in enumerate(rows):
        if q in fa:
            al, be, last = fa[q]
        else:
            al, be, last = 0.5, 0.5, None
        da, db, P = _ts_update(al, be, bool(item_mc[it]), int(item_m[it]), 1.0, 0.0, at, float(yy))
        exp_P[j] = P
        al, be = _py_update(al, be, 0.0 if last is None else tt - last, da, db)
        fa[q] = (al, be, tt)
    fin = np.array([[fa[q][0], fa[q][1]] for q in range(n_seq)])
    err = max(np.abs(exp_P - out["P"]).max(), np.abs(fin[:, 0] - out["A"]).max(), np.abs(fin[:, 1] - out["B"]).max())
    table = {h: (1 + V0 * h / 24) ** (-D0) for h in (1, 24, 168, 720, 8760)}
    want = {1: 0.998, 24: 0.953, 168: 0.767, 720: 0.500, 8760: 0.163}
    tab_ok = all(abs(table[h] - want[h]) < 0.0006 for h in want)
    ok = err < 1e-12 and tab_ok
    print(f"engine replay vs scalar transcription: max abs diff {err:.2e} over {len(rows):,} responses; "
          f"retention table {'ok' if tab_ok else 'FAIL'}; {'PASS' if ok else 'FAIL'}")
    return ok, err


if __name__ == "__main__":
    raise SystemExit(0 if check()[0] else 1)
