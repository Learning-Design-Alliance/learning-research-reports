"""Machinery for the graph-state study. coupling.py holds the pre-registration; the definitions here
are the ones it states, and the sections below name the step of it each implements.

  Attempts          the replay input: one row per attempt, learners' time order, skills as a padded row
  run_beta          C0 / C1: the engine's Beta state per node, sequential in each learner's time, with
                    the engine's parent propagation optional; checked equal to engine.replay without it
  static_items      Stage 1: a static 4PL calibration on TRAIN (learner ability, per-item a and b)
  cells             Stage 1: per (learner, skill) Gaussian pseudo-measurements of logit mastery
  fit_dense/_arrow  Stage 2: the population prior theta = mu + W z + e by EM (heteroscedastic factor
                    analysis with missing cells); `arrow` = a general factor plus one factor per group
  run_gauss         the coupled filter (C2 family): Laplace / extended-Kalman step per response
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

import engine as E

DAY = E.DAY
TAU_W = 0.5            # loadings ~ N(mean loading, TAU_W^2)
D_PSEUDO = 10.0        # pseudo-cells pulling each D_k toward the median D
MIN_CELLS = 20         # a skill with fewer TRAIN cells keeps the prior (mean loading, median D)
MIN_J = 0.02           # a cell with less likelihood information is dropped
EM_ITERS = 40
D_LO, D_HI = 0.01, 25.0


def sigmoid(z):
    return E.sigmoid(z)


def retention(dt):
    """The engine's curve (1 + v t)^(-d), t in days; 1 where dt <= 0 or unknown (nan)."""
    dt = np.nan_to_num(dt, nan=0.0)
    return np.where(dt > 0, (1.0 + E.V0 * np.maximum(dt, 0) / DAY) ** (-E.D0), 1.0)


# ---------------------------------------------------------------- the replay input

class Attempts:
    """Attempts of the rows in `mask` of a calibrate.Data, sorted by learner, time, file order.

    S (n, smax): the attempt's skills (competency ids), -1 padding; R (n, smax): each skill row's rank
    within its (learner, skill) pair (0 = the learner's first attempt on that skill); gap (n, smax):
    seconds since the pair's previous row (nan for R == 0). gid: calibrate.Data's attempt id."""

    def __init__(self, data, mask):
        d = data.df[mask]
        k = d.k.to_numpy()
        a_id = d.attempt.to_numpy()
        r = d.r.to_numpy()
        t = d.t.to_numpy()
        pr = d.pair.to_numpy()
        prev_same = np.r_[False, pr[1:] == pr[:-1]]
        gap = np.where(prev_same, t - np.r_[t[:1], t[:-1]], np.nan)
        assert np.all(prev_same == (r > 0)), "rows must be sorted by pair then time (calibrate.Data)"
        o = np.lexsort((k, a_id))
        a_s = a_id[o]
        start = np.r_[True, a_s[1:] != a_s[:-1]]
        n = int(start.sum())
        aidx = np.cumsum(start) - 1
        pos = np.arange(len(o)) - np.maximum.accumulate(np.where(start, np.arange(len(o)), 0))
        smax = int(pos.max()) + 1
        S = np.full((n, smax), -1, np.int64)
        R = np.full((n, smax), -1, np.int64)
        G = np.full((n, smax), np.nan)
        S[aidx, pos], R[aidx, pos], G[aidx, pos] = k[o], r[o], gap[o]
        first = o[start]
        l, i, y = d.l.to_numpy()[first], d.i.to_numpy()[first], d.y.to_numpy()[first]
        ta, oa, att = t[first], d.o.to_numpy()[first], d.att.to_numpy()[first]
        perm = np.lexsort((oa, ta, l))
        self.S, self.R, self.gap = S[perm], R[perm], G[perm]
        self.l_global = l[perm]
        self.i, self.y, self.t, self.o, self.att = i[perm], y[perm].astype(float), ta[perm], oa[perm], att[perm]
        self.gid = a_s[start][perm]
        self.l, self.learners = pd.factorize(self.l_global, sort=True)
        self.nl = len(self.learners)
        self.n = n
        self.M = self.S >= 0
        self.nS = self.M.sum(1)
        st = np.r_[True, self.l[1:] != self.l[:-1]]
        self.step = np.arange(n) - np.maximum.accumulate(np.where(st, np.arange(n), 0))
        order = np.argsort(self.step, kind="stable")
        self.steps = np.split(order, np.cumsum(np.bincount(self.step))[:-1])
        Rm = np.where(self.M, self.R, 0)
        self.cold = np.all(np.where(self.M, Rm == 0, True), 1) & (self.step > 0)
        self.warm = np.all(np.where(self.M, Rm > 0, True), 1)
        self.x = (np.log1p(Rm) * self.M).sum(1) / self.nS      # practice: mean log(1 + earlier attempts)
        self.gap_min = np.nanmin(np.where(self.M & (self.R > 0), self.gap, np.inf), 1)
        self.gap_min[~self.warm] = np.nan


# ---------------------------------------------------------------- C0 / C1: the engine's Beta state

def run_beta(at: Attempts, prm: E.Params, K: int, chain=None, record=False):
    """The engine's update over nodes 0..N-1 (competencies are 0..K-1), sequential per learner.

    chain (N, depth): each node's ancestors nearest first, -1 padding, or None (no propagation). With a
    chain every applied increment (delta alpha, delta beta, after the engine's bound) is handed to each
    ancestor, which decays by its own elapsed time and adds it, as generate_parent_assertions does.
    Returns per attempt: P_own (the mean over the attempt's skills of the item model at each skill's own
    stored state: C0 without a chain, C1-engine with one) and P_read (a skill with no evidence of its
    own reads the nearest ancestor holding evidence: C1). With record, the stored alpha, beta of the
    first skill before each attempt."""
    N = K if chain is None else chain.shape[0]
    A = np.full((at.nl, N), E.PRIOR)
    B = np.full((at.nl, N), E.PRIOR)
    T = np.full((at.nl, N), np.nan)
    P_own, P_read = np.empty(at.n), np.empty(at.n)
    rec_a, rec_b = (np.empty(at.n), np.empty(at.n)) if record else (None, None)
    a_i, b_i, c_i, d_i = prm.a[at.i], prm.b[at.i], prm.c[at.i], prm.d[at.i]
    watt = E.LAMBDA ** np.maximum(0, at.att - 1)
    for idx in at.steps:
        l = at.l[idx]
        S, M = at.S[idx], at.M[idx]
        Sc = np.where(M, S, 0)
        L2 = np.broadcast_to(l[:, None], S.shape)
        a0, b0 = A[L2, Sc], B[L2, Sc]
        ai, bi, ci, di = (x[idx][:, None] for x in (a_i, b_i, c_i, d_i))
        _, Lk, Pp, info = E.item_model(a0, b0, ai, bi, ci, di, prm.mode)
        Mass = E.K * watt[idx][:, None] * (E.MASS_FLOOR + info)
        y = at.y[idx][:, None]
        if prm.mode == "raw":
            s = np.broadcast_to(y, Pp.shape)
        else:
            s = np.where(y == 1, di * Lk / np.maximum(Pp, E.EPS), (1 - di) * Lk / np.maximum(1 - Pp, E.EPS))
        s = np.clip(s, 0.0, 1.0)
        da, db = Mass * s, Mass * (1 - s)
        tot = da + db
        sc = np.where(tot > E.MAX_EVIDENCE_MASS, E.MAX_EVIDENCE_MASS / np.maximum(tot, E.EPS), 1.0)
        da, db = da * sc, db * sc
        nS = at.nS[idx]
        P_own[idx] = (Pp * M).sum(1) / nS
        if chain is not None:
            touched = ~np.isnan(T[L2, Sc])
            ra, rb = a0.copy(), b0.copy()
            need = M & ~touched
            for h in range(chain.shape[1]):
                if not need.any():
                    break
                anc = chain[Sc, h]
                ok = need & (anc >= 0)
                ancc = np.where(ok, anc, 0)
                has = ok & ~np.isnan(T[L2, ancc])
                ra = np.where(has, A[L2, ancc], ra)
                rb = np.where(has, B[L2, ancc], rb)
                need = need & ~has
            _, _, Pr, _ = E.item_model(ra, rb, ai, bi, ci, di, prm.mode)
            P_read[idx] = (Pr * M).sum(1) / nS
        else:
            P_read[idx] = P_own[idx]
        if record:
            rec_a[idx], rec_b[idx] = a0[:, 0], b0[:, 0]
        t = at.t[idx]
        for j in range(S.shape[1]):
            v = M[:, j]
            if not v.any():
                continue
            lv, nv, tv = l[v], S[v, j], t[v]
            _write(A, B, T, lv, nv, tv, da[v, j], db[v, j], prm)
            if chain is not None:
                for h in range(chain.shape[1]):
                    an = chain[nv, h]
                    ok = an >= 0
                    if not ok.any():
                        break
                    _write(A, B, T, lv[ok], an[ok], tv[ok], da[v, j][ok], db[v, j][ok], prm)
    return {"P_own": P_own, "P_read": P_read, "alpha": rec_a, "beta": rec_b}


def _write(A, B, T, l, node, t, da, db, prm):
    dt = t - T[l, node]
    a0, b0 = E.decay(A[l, node], B[l, node], np.nan_to_num(dt, nan=0.0), prm.v, prm.dd, prm.toward)
    A[l, node] = np.maximum(1e-9, a0 + da)
    B[l, node] = np.maximum(1e-9, b0 + db)
    T[l, node] = t


def beta_check(data, at: Attempts, prm: E.Params, mask) -> float:
    """max |run_beta(no chain) - engine.replay| over the attempt-level P (the exactness check)."""
    ev = data.events(mask)
    rp = E.replay(ev, prm)["P"]
    d = data.df[mask]
    att_glob = d.attempt.to_numpy()
    ref = np.bincount(att_glob, rp, int(att_glob.max()) + 1) / np.maximum(np.bincount(att_glob, None, int(att_glob.max()) + 1), 1)
    mine = run_beta(at, prm, int(data.df.k.max()) + 1)["P_own"]
    return float(np.abs(ref[at.gid] - mine).max())


# ---------------------------------------------------------------- Stage 1: static items and cells

def _logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def static_items(at: Attempts, c, d, group, I, rounds=4, log=print):
    """JML on TRAIN attempts: linear predictor a (theta_l + beta x - b), x the attempt's practice feature.
    theta_l ~ N(0, 2^2) per learner (then standardised: the scale anchor), one global practice slope
    beta, then per item a, b by calibrate's penalised fit (fit_ab_once), alternated `rounds` times. c, d
    fixed (E5's asymptotes). Unidimensional: the item sees the learner's ability, not the skill's."""
    import calibrate as C
    it, y, l = at.i, at.y, at.l
    ci, di = c[it], d[it]
    p = (np.bincount(it, y, I) + 5 * y.mean()) / (np.bincount(it, None, I) + 5)
    a = np.ones(I)
    b = -_logit(np.clip((p - c) / np.maximum(d - c, 1e-3), 0.02, 0.98))
    th = np.zeros(at.nl)
    x = at.x
    beta = 0.0
    w0 = None
    for rd in range(rounds):
        for _ in range(6):
            z = a[it] * (th[l] + beta * x - b[it])
            L = sigmoid(z)
            P = np.clip(ci + (di - ci) * L, 1e-9, 1 - 1e-9)
            dP = (di - ci) * a[it] * L * (1 - L)
            g = np.bincount(l, (y - P) / (P * (1 - P)) * dP, at.nl) - th / 4.0
            h = np.bincount(l, dP * dP / (P * (1 - P)), at.nl) + 1 / 4.0
            th = th + np.clip(g / h, -2, 2)
        sd = max(th.std(), 1e-6)
        th, beta = (th - th.mean()) / sd, beta / sd       # anchors the scale (JML drifts otherwise)
        for _ in range(4):
            z = a[it] * (th[l] + beta * x - b[it])
            L = sigmoid(z)
            P = np.clip(ci + (di - ci) * L, 1e-9, 1 - 1e-9)
            dP = (di - ci) * a[it] * L * (1 - L) * x
            beta += float(((y - P) / (P * (1 - P)) * dP).sum() / max((dP * dP / (P * (1 - P))).sum(), 1e-9))
        b, a, ok, n, cent, w0 = C.fit_ab_once(th[l] + beta * x, it, y, np.ones(len(y)), ci, di, np.asarray(group), I, w0)
        log(f"   stage 1 round {rd + 1}: practice beta {beta:.3f}; items with own a, b {int(ok.sum()):,}; "
            f"median a {np.median(a[ok]) if ok.any() else float('nan'):.3f}")
    return a, b, th, beta


def cells(at: Attempts, th, a, b, c, d, K, beta=0.0):
    """Per (learner, skill) cell of TRAIN attempts: a Gaussian pseudo-measurement (value y, precision J)
    of the cell's logit mastery theta_lk -- the cell's likelihood linearised at the learner's ability
    theta_l, as the filter linearises at its predictive mean: J = the Fisher information and
    y = theta_l + score / J, both at theta_l. A row of an attempt with nS skills has linear predictor
    a ((theta_lk + (nS - 1) theta_l) / nS - b): the other skills held at theta_l (the compensatory rule,
    slope a / nS). Cells with J < MIN_J are dropped."""
    M = at.M
    rows = np.nonzero(M.ravel())[0]
    ai = np.repeat(np.arange(at.n), M.shape[1])[rows]
    k = at.S.ravel()[rows]
    l = at.l[ai]
    nS = at.nS[ai]
    it = at.i[ai]
    y = at.y[ai]
    cid, cl = pd.factorize(l.astype(np.int64) * K + k)
    nc = len(cl)
    lc, kc = (cl // K).astype(np.int64), (cl % K).astype(np.int64)
    slope = a[it] / nS
    ci, di = c[it], d[it]
    L = sigmoid(a[it] * (th[l] + beta * at.x[ai] - b[it]))
    P = np.clip(ci + (di - ci) * L, 1e-9, 1 - 1e-9)
    dP = (di - ci) * L * (1 - L) * slope
    g = np.bincount(cid, (y - P) / (P * (1 - P)) * dP, nc)
    J = np.bincount(cid, dP * dP / (P * (1 - P)), nc)
    ok = J >= MIN_J
    yv = th[lc] + g / np.maximum(J, 1e-12)
    first_t = np.full(nc, np.inf)
    np.minimum.at(first_t, cid, at.t[ai])
    return {"l": lc[ok], "k": kc[ok], "y": yv[ok], "J": J[ok], "first_t": first_t[ok], "nl": at.nl, "K": K,
            "dropped": int((~ok).sum()), "n": int(ok.sum())}


# ---------------------------------------------------------------- Stage 2: the population prior

class Prior:
    """theta = mu + W z + e (kind 'dense', W: K x r) or theta = mu + lam0 z0 + lam z_grp + e ('arrow');
    z ~ N(0, I), e_k ~ N(0, D_k)."""

    def __init__(self, kind, mu, D, W=None, lam0=None, lam=None, grp=None, G=0, name=""):
        self.kind, self.mu, self.D, self.W = kind, mu, D, W
        self.lam0, self.lam, self.grp, self.G, self.name = lam0, lam, grp, G, name

    def diag(self):
        if self.kind == "dense":
            return self.D + (self.W ** 2).sum(1)
        return self.D + self.lam0 ** 2 + self.lam ** 2

    def as_dense(self):
        if self.kind == "dense":
            return self
        K = len(self.mu)
        W = np.zeros((K, 1 + self.G))
        W[:, 0] = self.lam0
        W[np.arange(K), 1 + self.grp] = self.lam
        return Prior("dense", self.mu, self.D, W=W, name=self.name)

    def cov(self, j, k):
        """Sigma entries for index arrays j, k."""
        if self.kind == "dense":
            return (self.W[j] * self.W[k]).sum(-1) + np.where(j == k, self.D[j], 0.0)
        return (self.lam0[j] * self.lam0[k] + np.where(self.grp[j] == self.grp[k], self.lam[j] * self.lam[k], 0.0)
                + np.where(j == k, self.D[j], 0.0))


def _estep_dense(cl, W, D, mu):
    """Per-learner factor posterior given the cells: A = I + sum phi w w^T, eta = sum psi w."""
    r = W.shape[1]
    nl = cl["nl"]
    v = 1.0 / cl["J"]
    phi = 1.0 / (D[cl["k"]] + v)
    res = cl["y"] - mu[cl["k"]]
    Wc = W[cl["k"]]
    A = np.zeros((nl, r, r))
    for a_ in range(r):
        for b_ in range(a_, r):
            s = np.bincount(cl["l"], phi * Wc[:, a_] * Wc[:, b_], nl)
            A[:, a_, b_] = s
            A[:, b_, a_] = s
    A += np.eye(r)
    eta = np.stack([np.bincount(cl["l"], phi * res * Wc[:, a_], nl) for a_ in range(r)], 1) if r else np.zeros((nl, 0))
    P = np.linalg.inv(A) if r else np.zeros((nl, 0, 0))
    m = np.einsum("nij,nj->ni", P, eta) if r else np.zeros((nl, 0))
    ll = -0.5 * (np.bincount(cl["l"], np.log(2 * np.pi / phi) + phi * res * res, nl)
                 + (np.linalg.slogdet(A)[1] if r else 0.0) - (np.einsum("ni,ni->n", eta, m) if r else 0.0))
    return m, P, float(ll.sum())


def quad(Wc, P, l):
    """w_c^T P_l w_c per cell without materialising P[l] (cells x r x r)."""
    out = np.zeros(len(l))
    r = Wc.shape[1]
    for a_ in range(r):
        for b_ in range(r):
            out += Wc[:, a_] * Wc[:, b_] * P[l, a_, b_]
    return out


def fit_dense(cl, r, iters=EM_ITERS, seed=0, log=None):
    """MAP-EM for mu, W (K x r), D from the cells; heteroscedastic noise 1 / J per cell."""
    K, k = cl["K"], cl["k"]
    rng = np.random.default_rng(seed)
    n_k = np.bincount(k, None, K)
    thin = n_k < MIN_CELLS
    wv = cl["J"] / (1 + cl["J"])
    mu = np.bincount(k, wv * cl["y"], K) / np.maximum(np.bincount(k, wv, K), 1e-9)
    var_tot = np.bincount(k, wv * (cl["y"] - mu[k]) ** 2, K) / np.maximum(np.bincount(k, wv, K), 1e-9)
    D = np.clip(np.full(K, np.median(var_tot[~thin]) if (~thin).any() else 1.0) * (0.5 if r else 1.0), D_LO, D_HI)
    W = np.zeros((K, r))
    if r:
        W[:, 0] = 0.7
        W[:, 1:] = rng.normal(0, 0.1, (K, r - 1))
    trace = []
    for itn in range(iters):
        m, P, ll = _estep_dense(cl, W, D, mu)
        trace.append(ll)
        mc = m[cl["l"]]
        # (mu_k, w_k): weighted least squares with E[x x^T], x = [1, z]
        v = 1.0 / cl["J"]
        om = 1.0 / (D[k] + v)
        q = r + 1
        Gm = np.zeros((K, q, q))
        h = np.zeros((K, q))
        Gm[:, 0, 0] = np.bincount(k, om, K)
        h[:, 0] = np.bincount(k, om * cl["y"], K)
        for a_ in range(r):
            s = np.bincount(k, om * mc[:, a_], K)
            Gm[:, 0, 1 + a_] = s
            Gm[:, 1 + a_, 0] = s
            h[:, 1 + a_] = np.bincount(k, om * cl["y"] * mc[:, a_], K)
            for b_ in range(a_, r):
                s = np.bincount(k, om * (mc[:, a_] * mc[:, b_] + P[cl["l"], a_, b_]), K)
                Gm[:, 1 + a_, 1 + b_] = s
                Gm[:, 1 + b_, 1 + a_] = s
        wbar = W[~thin].mean(0) if r and (~thin).any() else np.zeros(r)
        for a_ in range(r):
            Gm[:, 1 + a_, 1 + a_] += 1 / TAU_W ** 2
            h[:, 1 + a_] += wbar[a_] / TAU_W ** 2
        Gm[:, 0, 0] += 1e-6
        sol = np.linalg.solve(Gm, h[..., None])[..., 0]
        mu, W = sol[:, 0], sol[:, 1:]
        # D_k: Newton steps on log D with pseudo-cells at the median
        e2 = (cl["y"] - mu[k] - (W[k] * mc).sum(1)) ** 2 + quad(W[k], P, cl["l"])
        D = _update_D(D, k, v, e2, K, thin)
        if r:
            W[thin] = W[~thin].mean(0) if (~thin).any() else 0.0
        mu[thin] = np.median(mu[~thin]) if (~thin).any() else 0.0
        if log and (itn % 10 == 9 or itn == iters - 1):
            log(f"      EM r={r} iter {itn + 1}: marginal loglik {ll:,.1f}")
    return Prior("dense", mu, D, W=W, name=f"dense r={r}"), trace


def _update_D(D, k, v, e2, K, thin, steps=4):
    Dm = float(np.median(D[~thin])) if (~thin).any() else float(np.median(D))
    for _ in range(steps):
        s = D[k] + v
        g = np.bincount(k, -1 / s + e2 / s ** 2, K) + D_PSEUDO * (-1 / D + Dm / D ** 2)
        hh = np.bincount(k, 1 / s ** 2 - 2 * e2 / s ** 3, K) + D_PSEUDO * (1 / D ** 2 - 2 * Dm / D ** 3)
        gt = D * g
        ht = D * g + D * D * hh
        step = np.where(ht < 0, -gt / ht, np.sign(gt) * 0.5)
        D = np.clip(D * np.exp(np.clip(step, -1, 1)), D_LO, D_HI)
    D[thin] = Dm
    return D


def _estep_arrow(cl, pr: Prior):
    """Arrow-shaped factor posterior per learner: z0 (general) and one z_g per group."""
    nl, G = cl["nl"], pr.G
    k = cl["k"]
    g = pr.grp[k]
    v = 1.0 / cl["J"]
    phi = 1.0 / (pr.D[k] + v)
    res = cl["y"] - pr.mu[k]
    l0, lg = pr.lam0[k], pr.lam[k]
    a00 = 1 + np.bincount(cl["l"], phi * l0 * l0, nl)
    eta0 = np.bincount(cl["l"], phi * res * l0, nl)
    lgk = cl["l"] * G + g
    u = np.bincount(lgk, phi * l0 * lg, nl * G).reshape(nl, G)
    dl = 1 + np.bincount(lgk, phi * lg * lg, nl * G).reshape(nl, G)
    eg = np.bincount(lgk, phi * res * lg, nl * G).reshape(nl, G)
    sch = a00 - (u * u / dl).sum(1)
    m0 = (eta0 - (u * eg / dl).sum(1)) / sch
    mg = (eg - u * m0[:, None]) / dl
    ll = -0.5 * (np.bincount(cl["l"], np.log(2 * np.pi / phi) + phi * res * res, nl)
                 + np.log(sch) + np.log(dl).sum(1) - (eta0 * m0 + (eg * mg).sum(1)))
    return {"m0": m0, "mg": mg, "sch": sch, "u": u, "dl": dl}, float(ll.sum())


def fit_arrow(cl, grp, G, general=True, groups=True, iters=EM_ITERS, log=None, name=""):
    """MAP-EM for the arrow prior. A group with fewer than 2 skills holding MIN_CELLS cells has lam = 0."""
    K, k = cl["K"], cl["k"]
    n_k = np.bincount(k, None, K)
    thin = n_k < MIN_CELLS
    grp = np.asarray(grp, np.int64)
    gsize = np.bincount(grp[~thin], None, G)
    grouped = groups & (gsize[grp] >= 2)
    wv = cl["J"] / (1 + cl["J"])
    mu = np.bincount(k, wv * cl["y"], K) / np.maximum(np.bincount(k, wv, K), 1e-9)
    var_tot = np.bincount(k, wv * (cl["y"] - mu[k]) ** 2, K) / np.maximum(np.bincount(k, wv, K), 1e-9)
    D = np.full(K, np.clip(np.median(var_tot[~thin]) * 0.5, D_LO, D_HI))
    lam0 = np.full(K, 0.7 if general else 0.0)
    lam = np.where(grouped, 0.5, 0.0)
    pr = Prior("arrow", mu, D, lam0=lam0, lam=lam, grp=grp, G=G, name=name)
    trace = []
    for itn in range(iters):
        st, ll = _estep_arrow(cl, pr)
        trace.append(ll)
        lc = cl["l"]
        gk = grp[k]
        m0 = st["m0"][lc]
        mg = st["mg"][lc, gk]
        sch, u, dl = st["sch"][lc], st["u"][lc, gk], st["dl"][lc, gk]
        P00 = 1 / sch
        P0g = -u / (dl * sch)
        Pgg = 1 / dl + u * u / (dl * dl * sch)
        v = 1.0 / cl["J"]
        om = 1.0 / (pr.D[k] + v)
        yy = cl["y"]
        # x = [1, z0, zg]; unused factors are dropped from the system per variant
        X = [np.ones_like(m0), m0, mg]
        C = {(1, 1): P00, (1, 2): P0g, (2, 2): Pgg}
        use = [0] + ([1] if general else []) + ([2] if groups else [])
        q = len(use)
        Gm = np.zeros((K, q, q))
        h = np.zeros((K, q))
        for ia, a_ in enumerate(use):
            h[:, ia] = np.bincount(k, om * yy * X[a_], K)
            for ib, b_ in enumerate(use):
                if ib < ia:
                    continue
                s = X[a_] * X[b_] + C.get((min(a_, b_), max(a_, b_)), 0.0)
                val = np.bincount(k, om * s, K)
                Gm[:, ia, ib] = val
                Gm[:, ib, ia] = val
        prior_mean = {}
        if general:
            prior_mean[1] = pr.lam0[~thin].mean()
        if groups:
            prior_mean[2] = pr.lam[grouped & ~thin].mean() if (grouped & ~thin).any() else 0.0
        for ia, a_ in enumerate(use):
            if a_ > 0:
                Gm[:, ia, ia] += 1 / TAU_W ** 2
                h[:, ia] += prior_mean[a_] / TAU_W ** 2
        if groups:
            ig = use.index(2)
            Gm[~grouped, ig, :] = 0
            Gm[~grouped, :, ig] = 0
            Gm[~grouped, ig, ig] = 1
            h[~grouped, ig] = 0
        Gm[:, 0, 0] += 1e-6
        sol = np.linalg.solve(Gm, h[..., None])[..., 0]
        mu = sol[:, 0]
        lam0 = sol[:, use.index(1)] if general else np.zeros(K)
        lam = sol[:, use.index(2)] if groups else np.zeros(K)
        lam = np.where(grouped, lam, 0.0)
        pred = mu[k] + lam0[k] * m0 + lam[k] * mg
        e2 = (yy - pred) ** 2 + lam0[k] ** 2 * P00 + 2 * lam0[k] * lam[k] * P0g + lam[k] ** 2 * Pgg
        D = _update_D(pr.D, k, v, e2, K, thin)
        if general:
            lam0[thin] = lam0[~thin].mean()
        if groups:
            lam[thin & grouped] = lam[~thin & grouped].mean() if (~thin & grouped).any() else 0.0
        mu[thin] = np.median(mu[~thin]) if (~thin).any() else 0.0
        pr = Prior("arrow", mu, D, lam0=lam0, lam=lam, grp=grp, G=G, name=name)
        if log and (itn % 10 == 9 or itn == iters - 1):
            log(f"      EM {name} iter {itn + 1}: marginal loglik {ll:,.1f}")
    return pr, trace


def heldout_density(cl_fit, cl_val, pr: Prior) -> float:
    """Mean predictive log density of each validation learner's later half of cells (by first-encounter
    time) from the earlier half: the rank-selection score."""
    order = np.lexsort((cl_val["first_t"], cl_val["l"]))
    l = cl_val["l"][order]
    st = np.r_[True, l[1:] != l[:-1]]
    pos = np.arange(len(l)) - np.maximum.accumulate(np.where(st, np.arange(len(l)), 0))
    cnt = np.bincount(l, None, cl_val["nl"])[l]
    early = pos < cnt // 2
    idx_e, idx_t = order[early], order[~early]
    sub = {kk: (vv[idx_e] if isinstance(vv, np.ndarray) else vv) for kk, vv in cl_val.items()}
    dp = pr.as_dense()
    m, P, _ = _estep_dense(sub, dp.W, dp.D, dp.mu)
    lt, kt = cl_val["l"][idx_t], cl_val["k"][idx_t]
    mean = dp.mu[kt] + (dp.W[kt] * m[lt]).sum(1)
    var = quad(dp.W[kt], P, lt) + dp.D[kt] + 1.0 / cl_val["J"][idx_t]
    yt = cl_val["y"][idx_t]
    return float(np.mean(-0.5 * (np.log(2 * np.pi * var) + (yt - mean) ** 2 / var)))


# ---------------------------------------------------------------- the coupled filter

def _probit_P(a, b, c, d, m, v):
    kap = np.sqrt(1 + math.pi * a * a * v / 8)
    return c + (d - c) * sigmoid(a * (m - b) / kap)


def run_gauss(at: Attempts, pr: Prior, items, K):
    """The C2-family filter. Per learner, evidence on skill k is held as a Gaussian pseudo-measurement
    of theta_k (precision q_k, information s_k); the state is the prior conditioned on all of them.

    Before each attempt: the skills' predictive means and covariance; theta_eff = their mean; P = the
    4PL integrated over theta_eff ~ N(m, v) (probit approximation). Then one Laplace (EKF) step at m:
    score g and Fisher information J of the response in theta_eff. Evidence spreads evenly over the
    item's nS skills (compensatory): each skill's pseudo-measurement gains precision J / nS at value
    m_k + g / J. Before adding, q_k and s_k of each touched skill decay by the engine's retention over the
    time since that skill's last evidence (lazy, as the engine). items = (a, b, c, d, beta): the 4PL and
    the practice slope (the linear predictor is a (theta_eff + beta x - b)). Returns per attempt P, m, v."""
    a, b, c, d, beta = items
    n, nl = at.n, at.nl
    q = np.zeros((nl, K))
    s = np.zeros((nl, K))
    tl = np.full((nl, K), np.nan)
    dense = pr.kind == "dense"
    if dense:
        r = pr.W.shape[1]
        A = np.broadcast_to(np.eye(r), (nl, r, r)).copy()
        eta = np.zeros((nl, r))
    else:
        G = pr.G
        a00 = np.ones(nl)
        eta0 = np.zeros(nl)
        u = np.zeros((nl, G))
        dl = np.ones((nl, G))
        eg = np.zeros((nl, G))
    Pout, mout, vout = np.empty(n), np.empty(n), np.empty(n)
    for idx in at.steps:
        l = at.l[idx]
        M = at.M[idx]
        Sc = np.where(M, at.S[idx], 0)
        Mf = M.astype(float)
        L2 = np.broadcast_to(l[:, None], Sc.shape)
        qk, sk = q[L2, Sc] * Mf, s[L2, Sc] * Mf
        Dk, muk = pr.D[Sc], pr.mu[Sc]
        den = 1 + Dk * qk
        rho = Dk * qk / den
        if dense:
            Pz = np.linalg.inv(A[l])
            mz = np.einsum("nij,nj->ni", Pz, eta[l])
            WS = pr.W[Sc] * Mf[..., None]
            base = muk + np.einsum("nsr,nr->ns", WS, mz)
            Cz = np.einsum("nsr,nrt,nut->nsu", WS, Pz, WS)
        else:
            gS = pr.grp[Sc]
            l0, lg = pr.lam0[Sc] * Mf, pr.lam[Sc] * Mf
            ul, dll, egl = u[l], dl[l], eg[l]
            sch = a00[l] - (ul * ul / dll).sum(1)
            m0 = (eta0[l] - (ul * egl / dll).sum(1)) / sch
            ug, dg, egg = ul[np.arange(len(l))[:, None], gS], dll[np.arange(len(l))[:, None], gS], egl[np.arange(len(l))[:, None], gS]
            mg = (egg - ug * m0[:, None]) / dg
            base = muk + l0 * m0[:, None] + lg * mg
            P00 = (1 / sch)[:, None, None]
            P0g = -ug / (dg * sch[:, None])
            same = gS[:, :, None] == gS[:, None, :]
            Pgg = same / dg[:, :, None] + ug[:, :, None] * ug[:, None, :] / (dg[:, :, None] * dg[:, None, :] * sch[:, None, None])
            Cz = (l0[:, :, None] * l0[:, None, :] * P00 + l0[:, :, None] * lg[:, None, :] * P0g[:, None, :]
                  + lg[:, :, None] * l0[:, None, :] * P0g[:, :, None] + lg[:, :, None] * lg[:, None, :] * Pgg)
        mk = (1 - rho) * base + Dk * sk / den
        one_r = (1 - rho) * Mf
        cov = one_r[:, :, None] * one_r[:, None, :] * Cz
        cov += np.eye(Sc.shape[1])[None] * (Dk / den * Mf)[:, :, None]
        nS = at.nS[idx].astype(float)
        m = (mk * Mf).sum(1) / nS
        v = cov.sum((1, 2)) / nS ** 2
        it = at.i[idx]
        ai, bi, ci, di = a[it], b[it], c[it], d[it]
        off = beta * at.x[idx]
        Pout[idx], mout[idx], vout[idx] = _probit_P(ai, bi, ci, di, m + off, v), m, v
        L0 = sigmoid(ai * (m + off - bi))
        P0 = np.clip(ci + (di - ci) * L0, 1e-9, 1 - 1e-9)
        dP = (di - ci) * ai * L0 * (1 - L0)
        y = at.y[idx]
        g = np.where(y == 1, dP / P0, -dP / (1 - P0))
        J = dP * dP / (P0 * (1 - P0)) + 1e-12
        rr = retention(at.t[idx][:, None] - tl[L2, Sc])
        qn = (qk * rr + (J / nS)[:, None]) * Mf
        sn = (sk * rr + ((J[:, None] * mk + g[:, None]) / nS[:, None])) * Mf
        dphi = (qn / (1 + Dk * qn) - qk / den) * Mf
        dpsi = ((sn - muk * qn) / (1 + Dk * qn) - (sk - muk * qk) / den) * Mf
        rows, cols = np.nonzero(M)
        lr, kr = l[rows], at.S[idx][rows, cols]
        q[lr, kr], s[lr, kr], tl[lr, kr] = qn[rows, cols], sn[rows, cols], at.t[idx][rows]
        if dense:
            A[l] += np.einsum("ns,nsr,nst->nrt", dphi, WS, WS)
            eta[l] += np.einsum("ns,nsr->nr", dpsi, WS)
        else:
            a00[l] += (dphi * l0 * l0).sum(1)
            eta0[l] += (dpsi * l0).sum(1)
            gr = gS[rows, cols]
            np.add.at(u, (lr, gr), (dphi * l0 * lg)[rows, cols])
            np.add.at(dl, (lr, gr), (dphi * lg * lg)[rows, cols])
            np.add.at(eg, (lr, gr), (dpsi * lg)[rows, cols])
    return {"P": Pout, "m": mout, "v": vout}


# ---------------------------------------------------------------- items on the filter's own state

def fit_items_filter(m, v, x, it, y, wt, c, d, group, I, a0, b0, beta, iters=60, tol=1e-7):
    """Per-item a, b for P = c + (d - c) sigmoid(a (m - b) / kappa), kappa = sqrt(1 + pi a^2 v / 8), given
    the filter's predictive m, v per attempt (m shifted by the practice term beta x, beta refitted by a
    Fisher step per sweep): calibrate step 3's penalised objective (b ~ N(b_G, 1),
    log a ~ N(log a_G, 0.5^2), log a in [log 0.2, log 4], group centres re-estimated three times, items with
    < 30 weighted rows at their group centre), solved by Fisher scoring. dz/db = -a / kappa and
    dz/da = (m - b) / kappa^3."""
    import calibrate as C
    group = np.asarray(group)
    G = int(group.max()) + 1
    n = np.bincount(it, wt, I)
    ok = n >= C.MIN_AB
    b, la = b0.copy(), np.log(np.clip(a0, 0.2, 4.0))
    bG, laG = np.zeros(G), np.zeros(G)
    ci, di = c[it], d[it]
    span = di - ci
    for _ in range(4):
        for _ in range(iters):
            a = np.exp(la)
            ar, br = a[it], b[it]
            kap = np.sqrt(1 + math.pi * ar * ar * v / 8)
            mm = m + beta * x
            z = ar * (mm - br) / kap
            L = sigmoid(z)
            P = np.clip(ci + span * L, 1e-9, 1 - 1e-9)
            dPz = span * L * (1 - L)
            gz = wt * (y - P) / (P * (1 - P)) * dPz
            fz = wt * dPz * dPz / (P * (1 - P))
            zb = -ar / kap
            zl = ar * (mm - br) / kap ** 3
            gb = np.bincount(it, gz * zb, I) - (b - bG[group]) / C.SD_B ** 2
            gl = np.bincount(it, gz * zl, I) - (la - laG[group]) / C.SD_LA ** 2
            hbb = np.bincount(it, fz * zb * zb, I) + 1 / C.SD_B ** 2
            hll = np.bincount(it, fz * zl * zl, I) + 1 / C.SD_LA ** 2
            hbl = np.bincount(it, fz * zb * zl, I)
            det = hbb * hll - hbl * hbl
            sb = (hll * gb - hbl * gl) / det
            sl = (hbb * gl - hbl * gb) / det
            pinned = ((la <= C.LA_LO) & (sl < 0)) | ((la >= C.LA_HI) & (sl > 0))
            sb = np.where(pinned, gb / hbb, sb)
            sl = np.where(pinned, 0.0, sl)
            sb, sl = np.clip(sb, -1, 1), np.clip(sl, -0.5, 0.5)
            b = b + sb
            la = np.clip(la + sl, C.LA_LO, C.LA_HI)
            if max(np.abs(sb).max(), np.abs(sl).max()) < tol:
                break
        for _ in range(5):      # the practice slope, items held (a joint step overshoots: beta x and b trade off)
            a = np.exp(la)
            ar, br = a[it], b[it]
            kap = np.sqrt(1 + math.pi * ar * ar * v / 8)
            L = sigmoid(ar * (m + beta * x - br) / kap)
            P = np.clip(ci + span * L, 1e-9, 1 - 1e-9)
            dPz = span * L * (1 - L)
            zx = ar * x / kap
            beta += float(np.clip((wt * (y - P) / (P * (1 - P)) * dPz * zx).sum()
                                  / max((wt * dPz * dPz / (P * (1 - P)) * zx * zx).sum(), 1e-9), -0.5, 0.5))
        for g in range(G):
            sel = (group == g) & ok
            if sel.any():
                bG[g], laG[g] = b[sel].mean(), la[sel].mean()
    b[~ok], la[~ok] = bG[group][~ok], laG[group][~ok]
    return np.exp(la), b, beta, ok


def refit_items(at: Attempts, pr, items, K, group, I, passes=2):
    """Two passes: run the filter with the current items, refit a, b and the practice slope on the filter's
    own predictive state. items = (a, b, c, d, beta)."""
    a, b, c, d, beta = items
    for _ in range(passes):
        o = run_gauss(at, pr, (a, b, c, d, beta), K)
        a, b, beta, ok = fit_items_filter(o["m"], o["v"], at.x, at.i, at.y, np.ones(at.n), c, d, group, I, a, b, beta)
    return a, b, c, d, beta
