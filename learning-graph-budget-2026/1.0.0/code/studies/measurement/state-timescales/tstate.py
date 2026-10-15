"""Machinery for the state-timescales study. state_timescales.py holds the pre-registration; the
definitions here are the ones it states.

  Struct        sessions, submissions, steps and the per-attempt structure the features need
  features      the control stack's offsets (H1 previous outcome, H2 previous action, H3 memory and
                selection), strictly from earlier attempts
  fit_offset    gamma for an offset layer, by penalised Fisher scoring over a fixed predictive state
  Comps         the extra scalar components (AR fast state, static per-learner slope) and their
                decoupled extended-Kalman step, vectorised over a parameter grid
  resid_filter  the components alone over a fixed base predictive state (the grid fit of rho, tau, ...)
  run_joint     gstate.run_gauss plus offsets and components; records the general-factor posterior
                (Part A's g-tracker) and the next-session forecasts (B-M2)
  run_beta_A    the engine's Beta with a learner-informed prior (Part A)
  run_beta_M    the engine's Beta with the AR fast state (the engine reading of Part B)
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy.special import polygamma

import engine as E
import gstate as S

SESSION_GAP = 1800.0
RAPID_MS = 5000.0


def sigmoid(z):
    return E.sigmoid(z)


def probit_P(a, b, c, d, m, v):
    kap = np.sqrt(1 + math.pi * a * a * np.maximum(v, 0) / 8)
    return c + (d - c) * sigmoid(a * (m - b) / kap)


def score_info(a, b, c, d, Sm, y):
    """Score and Fisher information of a response in the linear predictor S at the point Sm."""
    L0 = sigmoid(a * (Sm - b))
    P0 = np.clip(c + (d - c) * L0, 1e-9, 1 - 1e-9)
    dP = (d - c) * a * L0 * (1 - L0)
    g = np.where(y == 1, dP / P0, -dP / (1 - P0))
    J = dP * dP / (P0 * (1 - P0)) + 1e-12
    return g, J


# ---------------------------------------------------------------- structure

class Struct:
    """Per-attempt structure for an S.Attempts (sorted by learner, time, order).

    quiz: per attempt (Eedi) or None; batch: XES3G5M's submission rule (identical timestamps)."""

    def __init__(self, at: S.Attempts, quiz=None, batch=False):
        n = at.n
        l, t = at.l, at.t
        self.n = n
        first = at.step == 0
        dt = np.r_[np.inf, t[1:] - t[:-1]]
        dt[first] = np.inf
        brk = first | (dt > SESSION_GAP)
        if quiz is not None:
            qz = np.asarray(quiz)
            brk |= np.r_[True, qz[1:] != qz[:-1]]
        self.learner_first = first
        self.sess_start = brk
        self.sess = np.cumsum(brk) - 1
        idx = np.arange(n)
        s0 = np.maximum.accumulate(np.where(brk, idx, 0))
        self.pos = idx - s0
        self.sess_len = np.bincount(self.sess)[self.sess]
        if batch:
            new = brk | (dt != 0)
        else:
            new = np.ones(n, bool)
        self.new_step = new
        self.sub = np.cumsum(new) - 1
        self.batch = batch
        sub0 = np.maximum.accumulate(np.where(new, idx, 0))       # first attempt of the current step
        self.prev = np.where(brk, -1, idx - 1)                     # previous attempt in the session
        prevstep_last = sub0 - 1                                   # last attempt of the previous step
        self.prevstep = np.where(brk | (sub0 == s0) , -1, prevstep_last)
        self.same_sub_prev = (self.prev >= 0) & ~new
        self.dt_prev = np.where(self.prev >= 0, dt, 0.0)
        self.next_first = brk & ~first
        # skills shared with the previous attempt / with any attempt of the previous step
        Sk, M = at.S, at.M
        K1 = int(Sk.max()) + 2
        p = np.maximum(self.prev, 0)
        ov = (Sk[:, :, None] == Sk[p][:, None, :]) & M[:, :, None] & M[p][:, None, :]
        self.prev_same_skill = ov.any((1, 2)) & (self.prev >= 0)
        rows, cols = np.nonzero(M)
        key_sub = self.sub[rows].astype(np.int64) * K1 + Sk[rows, cols]
        pss = np.maximum(self.prevstep, 0)
        q = self.sub[pss].astype(np.int64)[rows] * K1 + Sk[rows, cols]
        hit = np.isin(q, key_sub)
        any_hit = np.zeros(n, bool)
        np.logical_or.at(any_hit, rows, hit)
        self.prevstep_same_skill = any_hit & (self.prevstep >= 0)
        key_ss = self.sess[rows].astype(np.int64) * K1 + Sk[rows, cols]
        hit2 = np.isin((self.sess[rows].astype(np.int64) - 1) * K1 + Sk[rows, cols], key_ss)
        any2 = np.zeros(n, bool)
        np.logical_or.at(any2, rows, hit2)
        self.prev_sess_same_skill = any2 & self.next_first
        # item memory
        key = l.astype(np.int64) * (int(at.i.max()) + 1) + at.i
        o = np.lexsort((idx, key))
        ks = key[o]
        st = np.r_[True, ks[1:] != ks[:-1]]
        cnt = np.empty(n, np.int64)
        cnt[o] = np.arange(n) - np.maximum.accumulate(np.where(st, np.arange(n), 0))
        prv = np.full(n, -1, np.int64)
        prv[o[~st]] = o[np.nonzero(~st)[0] - 1]
        self.item_count = cnt
        self.item_prev = prv
        self.item_hours = np.where(prv >= 0, (t - t[np.maximum(prv, 0)]) / 3600.0, 0.0)
        # same-skill memory: per slot rank R and gap (seconds since the pair's previous row)
        Rm = np.where(M, at.R, 0)
        self.skill_seen = (Rm > 0).any(1)
        gmin = np.nanmin(np.where(M & (at.R > 0), at.gap, np.inf), 1)
        self.skill_minutes = np.where(np.isfinite(gmin), gmin / 60.0, 0.0)
        sk_key = self.sess[rows].astype(np.int64) * K1 + Sk[rows, cols]
        oo = np.lexsort((rows, sk_key))
        kk = sk_key[oo]
        st2 = np.r_[True, kk[1:] != kk[:-1]]
        c2 = np.empty(len(rows), np.int64)
        c2[oo] = np.arange(len(rows)) - np.maximum.accumulate(np.where(st2, np.arange(len(rows)), 0))
        sc = np.zeros(n, np.int64)
        np.maximum.at(sc, rows, c2)
        self.skill_sess_count = sc
        self.restricted = (self.prevstep >= 0) & ~self.prevstep_same_skill & (self.item_count == 0)
        self.within = ~brk

    def assignment(self, at, assign, ytrue):
        """ASSISTments: position within the assignment and the run of consecutive correct answers in it
        before the current problem."""
        n = self.n
        key = at.l.astype(np.int64) * (int(np.max(assign)) + 2) + (np.asarray(assign) + 1)
        idx = np.arange(n)
        o = np.lexsort((idx, key))
        ks = key[o]
        st = np.r_[True, ks[1:] != ks[:-1]]
        pos = np.empty(n, np.int64)
        pos[o] = np.arange(n) - np.maximum.accumulate(np.where(st, np.arange(n), 0))
        ys = ytrue[o]
        streak = np.zeros(n, np.int64)
        run = 0
        out = np.zeros(n, np.int64)
        for j in range(n):          # sequential by construction (resets on a wrong answer)
            if st[j]:
                run = 0
            out[j] = run
            run = run + 1 if ys[j] == 1 else 0
        streak[o] = out
        return pos, streak


def l1p(x):
    return np.log1p(np.maximum(x, 0))


def features(st: Struct, at: S.Attempts, extra: dict, kind: str):
    """Named offset columns per layer (H1, H2, H3mem, H3sel); constant columns dropped.

    extra (per attempt, aligned with at): hint, bottom, multi, rt_ms (ASSISTments-like), assign, mastery,
    demand (XES3G5M-like)."""
    n = at.n
    y = at.y
    pv = st.prev
    has = pv >= 0
    pp = np.maximum(pv, 0)
    yprev = np.where(has, y[pp], 0.0)
    cols = {"H1": {}, "H2": {}, "H3mem": {}, "H3sel": {}}
    cols["H1"]["prev_present"] = has.astype(float)
    cols["H1"]["prev_y"] = yprev
    cols["H1"]["prev_same_skill"] = st.prev_same_skill.astype(float)
    cols["H1"]["prev_y_x_same_skill"] = yprev * st.prev_same_skill
    if st.batch:
        cols["H1"]["prev_same_sub"] = st.same_sub_prev.astype(float)
        cols["H1"]["prev_y_x_same_sub"] = yprev * st.same_sub_prev
    if "hint" in extra:
        h = np.asarray(extra["hint"], float)
        cols["H2"]["prev_hint"] = np.where(has, h[pp], 0.0)
        cols["H2"]["prev_hint_x_prev_y"] = cols["H2"]["prev_hint"] * yprev       # CHANGE 5
        for nm in ("bottom", "multi"):
            if nm in extra:
                v = np.asarray(extra[nm], float)
                cols["H2"][f"prev_{nm}"] = np.where(has, v[pp], 0.0)
        if "rt_ms" in extra:
            rt = np.asarray(extra["rt_ms"], float)
            ok = has & np.isfinite(rt[pp]) & (rt[pp] > 0)
            cols["H2"]["prev_log_rt"] = np.where(ok, np.log1p(np.where(ok, rt[pp], 0) / 1000.0), 0.0)
            cols["H2"]["prev_rapid"] = (ok & (rt[pp] < RAPID_MS)).astype(float)
    seen = st.item_count > 0
    cols["H3mem"]["item_seen"] = seen.astype(float)
    cols["H3mem"]["item_log_count"] = l1p(st.item_count)
    cols["H3mem"]["item_log_hours"] = np.where(seen, l1p(st.item_hours), 0.0)
    cols["H3mem"]["item_prev_resid"] = np.zeros(n)          # filled from H0 (set_item_resid)
    cols["H3mem"]["skill_seen"] = st.skill_seen.astype(float)
    cols["H3mem"]["skill_log_minutes"] = np.where(st.skill_seen, l1p(st.skill_minutes), 0.0)
    cols["H3mem"]["skill_sess_log_count"] = l1p(st.skill_sess_count)
    cols["H3sel"]["sess_log_pos"] = l1p(st.pos)
    cols["H3sel"]["log_secs_prev"] = l1p(st.dt_prev)
    if "assign" in extra:
        pos, streak = st.assignment(at, extra["assign"], y)
        ms = np.asarray(extra.get("mastery", np.zeros(n)), float)
        sel = {"assign_log_pos": l1p(pos), "assign_first": (pos == 0).astype(float),
               "streak1": (streak == 1).astype(float), "streak2": (streak == 2).astype(float),
               "streak3p": (streak >= 3).astype(float)}
        for k_, v_ in list(sel.items()):
            cols["H3sel"][k_] = v_
            cols["H3sel"][k_ + "_x_mastery"] = v_ * ms
    if "demand" in extra:
        dem = np.asarray(extra["demand"], float)
        cols["H3sel"]["sess_log_pos_x_demand"] = l1p(st.pos) * dem
    for lay in cols:
        for k_ in list(cols[lay]):
            v_ = cols[lay][k_]
            if k_ != "item_prev_resid" and np.nanstd(v_) == 0:
                del cols[lay][k_]
    return cols


def set_item_resid(cols, st: Struct, y, P0):
    """The learner's last residual on this item under H0 (a stable learner x item proxy)."""
    pr = st.item_prev
    cols["H3mem"]["item_prev_resid"] = np.where(pr >= 0, y[np.maximum(pr, 0)] - P0[np.maximum(pr, 0)], 0.0)


def matrix(cols, layers):
    names, mats = [], []
    for lay in layers:
        for k_, v_ in cols[lay].items():
            names.append(f"{lay}:{k_}")
            mats.append(np.asarray(v_, np.float64))
    if not mats:
        return np.zeros((len(next(iter(cols["H1"].values()))), 0)), names
    return np.column_stack(mats), names


def fit_offset(F, base_S, v, a, b, c, d, y, ridge=1.0, iters=20, mask=None):
    """gamma maximising sum log P(y), P = probit 4PL at base_S + F gamma (penalty gamma ~ N(0, 1/ridge))."""
    p = F.shape[1]
    if p == 0:
        return np.zeros(0)
    if mask is not None:
        F, base_S, v, a, b, c, d, y = (x[mask] for x in (F, base_S, v, a, b, c, d, y))
    gam = np.zeros(p)
    kap = np.sqrt(1 + math.pi * a * a * v / 8)
    for _ in range(iters):
        z = a * (base_S + F @ gam - b) / kap
        L = sigmoid(z)
        P = np.clip(c + (d - c) * L, 1e-9, 1 - 1e-9)
        dz = (d - c) * L * (1 - L) * a / kap
        w = dz * dz / (P * (1 - P))
        gr = F.T @ ((y - P) / (P * (1 - P)) * dz) - ridge * gam
        H = (F * w[:, None]).T @ F + ridge * np.eye(p)
        step = np.linalg.solve(H, gr)
        step = np.clip(step, -1, 1)
        gam = gam + step
        if np.abs(step).max() < 1e-6:
            break
    return gam


# ---------------------------------------------------------------- the extra components

class Comps:
    """Scalar components over a grid of G parameter sets, per learner.

    spec: list of dicts, kind 'ar' (rho, tau: (G,); scale: None, an (n,) array, or (demand (n,), kappa
    (G,)); carry: None (reset at a session start) or (G,) rho_b) or kind 'static' (sig: (G,); loading:
    (n,) array). AR components of a batch-blind Struct accumulate a step's evidence and apply it when
    the next step starts."""

    def __init__(self, spec, nl, st: Struct, rep=None):
        """rep: with replicated learners (virtual learner = l * rep + j), parameter arrays have length rep
        and virtual learner v uses entry v % rep; the state then has one column."""
        self.spec, self.st, self.rep = spec, st, rep
        G = 1 if rep else max(len(np.atleast_1d(c.get("rho", c.get("sig")))) for c in spec)
        self.G = G
        self.mu, self.V, self.aA, self.aB = [], [], [], []
        for c in spec:
            self.mu.append(np.zeros((nl, G)))
            self.V.append(np.ones((nl, G)))
            self.aA.append(np.zeros((nl, G)))
            self.aB.append(np.zeros((nl, G)))

    def _p(self, c, k, l):
        if self.rep:
            return np.broadcast_to(np.asarray(c[k], float), (self.rep,))[l % self.rep][:, None]
        return np.broadcast_to(np.asarray(c[k], float), (self.G,))[None, :]

    @staticmethod
    def _sub(x, m):
        return x if x.shape[0] == 1 else x[m]

    def pre(self, idx, l, record=False):
        """Transition before the attempts idx (one per learner). With record, returns per component the
        (mu, V) a carried state would hold at session starts (end of the previous session)."""
        st = self.st
        first = st.learner_first[idx]
        ss = st.sess_start[idx] & ~first
        ns = st.new_step[idx] & ~st.sess_start[idx]
        rec = []
        sb = self._sub
        for j, c in enumerate(self.spec):
            if c["kind"] != "ar":
                if first.any():
                    lf = l[first]
                    self.mu[j][lf] = 0.0
                    self.V[j][lf] = np.broadcast_to(sb(self._p(c, "sig", l), first) ** 2, (len(lf), self.G))
                rec.append(None)
                continue
            mu, V, aA, aB = self.mu[j], self.V[j], self.aA[j], self.aB[j]
            fl = st.new_step[idx] & ~first
            if fl.any():                       # apply the previous step's accumulated evidence
                lf = l[fl]
                Vn = V[lf] / (1.0 + V[lf] * aA[lf])
                mu[lf] = mu[lf] + Vn * aB[lf]
                V[lf] = Vn
                aA[lf] = 0.0
                aB[lf] = 0.0
            rho, tau = self._p(c, "rho", l), self._p(c, "tau", l)
            if record:
                rec.append((mu[l].copy(), V[l].copy()))
            if ns.any():
                ln = l[ns]
                r_, t_ = sb(rho, ns), sb(tau, ns)
                mu[ln] = r_ * mu[ln]
                V[ln] = r_ * r_ * V[ln] + t_ * t_ * (1 - r_ * r_)
            if ss.any():
                ls_ = l[ss]
                t_ = sb(tau, ss)
                if c.get("carry") is None:
                    mu[ls_] = 0.0
                    V[ls_] = np.broadcast_to(t_ * t_, (len(ls_), self.G))
                else:
                    rb = sb(self._p(c, "carry", l), ss)
                    mu[ls_] = rb * mu[ls_]
                    V[ls_] = rb * rb * V[ls_] + t_ * t_ * (1 - rb * rb)
            if first.any():
                lf = l[first]
                t_ = sb(tau, first)
                mu[lf] = 0.0
                V[lf] = np.broadcast_to(t_ * t_, (len(lf), self.G))
                aA[lf] = 0.0
                aB[lf] = 0.0
        return rec

    def loads(self, idx, l=None):
        out = []
        for c in self.spec:
            if c["kind"] == "static":
                out.append(np.asarray(c["loading"], float)[idx][:, None])
            elif c.get("scale") is None:
                out.append(np.ones((len(idx), 1)))
            elif isinstance(c["scale"], tuple):
                dem, kap = c["scale"]
                kk = (np.broadcast_to(np.asarray(kap, float), (self.rep,))[l % self.rep][:, None] if self.rep
                      else np.atleast_1d(np.asarray(kap, float))[None, :])
                out.append(np.exp(np.asarray(dem, float)[idx][:, None] * kk))
            else:
                out.append(np.asarray(c["scale"], float)[idx][:, None])
        return out

    def moments(self, l, ells, mus=None, Vs=None):
        mus = [m[l] for m in self.mu] if mus is None else mus
        Vs = [v[l] for v in self.V] if Vs is None else Vs
        mean = sum(e * m for e, m in zip(ells, mus))
        var = sum(e * e * v for e, v in zip(ells, Vs))
        return mean, var


def resid_filter(at: S.Attempts, st: Struct, S0, v0, items_row, spec, masks):
    """The components alone over a fixed predictive state: S = S0 + sum l_c c, variance v0 + ...
    items_row = (a, b, c, d) per attempt. Returns, per mask, the per-learner log likelihood (nl, G)."""
    a, b, c, d = items_row
    comp = Comps(spec, at.nl, st)
    LL = [np.zeros((at.nl, comp.G)) for _ in masks]
    y = at.y
    for idx in at.steps:
        l = at.l[idx]
        comp.pre(idx, l)
        ells = comp.loads(idx, l)
        em, ev = comp.moments(l, ells)
        Sm = S0[idx][:, None] + em
        Sv = v0[idx][:, None] + 0 * ev       # components enter the forecast as a point shift (CHANGE 2)
        ai, bi, ci, di = (x[idx][:, None] for x in (a, b, c, d))
        P = np.clip(probit_P(ai, bi, ci, di, Sm, Sv), 1e-9, 1 - 1e-9)
        yy = y[idx][:, None]
        ll = yy * np.log(P) + (1 - yy) * np.log1p(-P)
        for k_, mk in enumerate(masks):
            sel = mk[idx]
            if sel.any():
                LL[k_][l[sel]] += ll[sel]
        g, J = score_info(ai, bi, ci, di, Sm, yy)
        _update_grid(comp, idx, l, ells, g, J, v0[idx])
    return LL


def _update_grid(comp: Comps, idx, l, ells, g, J, vbase):
    """Comps.update with g, J of shape (n_idx, G)."""
    tot = sum(e * e * v[l] for e, v in zip(ells, comp.V))
    gj = g / J
    for j, c in enumerate(comp.spec):
        e = ells[j]
        Vj = comp.V[j][l]
        noise = 1.0 / J + vbase[:, None] + tot - e * e * Vj
        if c["kind"] == "ar" and comp.st.batch:
            comp.aA[j][l] += e * e / noise
            comp.aB[j][l] += e * gj / noise
        else:
            K = e * Vj / (e * e * Vj + noise)
            comp.mu[j][l] = comp.mu[j][l] + K * gj
            comp.V[j][l] = Vj - K * e * Vj


def resid_predict(at, st, S0, v0, items_row, spec):
    """resid_filter for one parameter set: per attempt P and the components' mean and variance (n,)."""
    a, b, c, d = items_row
    comp = Comps(spec, at.nl, st)
    P, EM, EV = np.empty(at.n), np.empty(at.n), np.empty(at.n)
    for idx in at.steps:
        l = at.l[idx]
        comp.pre(idx, l)
        ells = comp.loads(idx, l)
        em, ev = comp.moments(l, ells)
        Sm = S0[idx] + em[:, 0]
        Sv = v0[idx] + 0 * ev[:, 0]
        ai, bi, ci, di = (x[idx] for x in (a, b, c, d))
        P[idx] = probit_P(ai, bi, ci, di, Sm, Sv)
        EM[idx], EV[idx] = em[:, 0], ev[:, 0]
        g, J = score_info(ai, bi, ci, di, Sm, at.y[idx])
        _update_grid(comp, idx, l, ells, g[:, None], J[:, None], v0[idx])
    return P, EM, EV


# ---------------------------------------------------------------- the joint filter

def run_joint(at: S.Attempts, pr: S.Prior, items, K, st: Struct | None = None, h=None, spec=(),
              record_g=False, record_ns=False, rep=None, masks=None):
    """gstate.run_gauss (dense prior) plus an offset h in the linear predictor and the components of
    `spec` (one parameter set). Returns P, m, v (the skills' part), the components' mean contribution
    per attempt, and on request the general factor's posterior before each attempt (r = 1: mean, variance,
    and per skill slot with that skill's own evidence removed) and, at next-session first attempts, the
    forecast with the previous session's end state carried (P_abs) and the end state (dend).

    rep: every learner is replicated rep times (virtual learner l * rep + j uses parameter entry j of
    each component's arrays), and the run returns only the per-learner log likelihood (nl, rep) on
    each of `masks`: the joint filter's own likelihood over a parameter grid in one pass."""
    R_ = rep or 1
    a, b, c, d, beta = items
    n, nl0 = at.n, at.nl
    nl = nl0 * R_
    q = np.zeros((nl, K))
    s = np.zeros((nl, K))
    tl = np.full((nl, K), np.nan)
    r = pr.W.shape[1]
    A = np.broadcast_to(np.eye(r), (nl, r, r)).copy()
    eta = np.zeros((nl, r))
    comp = Comps(list(spec), nl, st, rep=rep) if spec else None
    if rep:
        LLm = [np.zeros(nl) for _ in masks]
        jj = np.arange(R_)
    Pout, mout, vout, cm, cvv = np.empty(n), np.empty(n), np.empty(n), np.zeros(n), np.zeros(n)
    rec = {}
    if record_g:
        rec["g"] = np.empty(n)
        rec["gv"] = np.empty(n)
        rec["g_loo"] = np.full(at.S.shape, np.nan)
    if record_ns:
        rec["P_abs"] = np.full(n, np.nan)
        rec["dend"] = np.full(n, np.nan)
        rec["Vend"] = np.full(n, np.nan)
    hh = np.zeros(n) if h is None else h
    for idx0 in at.steps:
        if rep:
            idx = np.repeat(idx0, R_)
            l = (at.l[idx0][:, None] * R_ + jj[None]).ravel()
        else:
            idx, l = idx0, at.l[idx0]
        M = at.M[idx]
        Sc = np.where(M, at.S[idx], 0)
        Mf = M.astype(float)
        L2 = np.broadcast_to(l[:, None], Sc.shape)
        qk, sk = q[L2, Sc] * Mf, s[L2, Sc] * Mf
        Dk, muk = pr.D[Sc], pr.mu[Sc]
        den = 1 + Dk * qk
        rho = Dk * qk / den
        Pz = np.linalg.inv(A[l])
        mz = np.einsum("nij,nj->ni", Pz, eta[l])
        WS = pr.W[Sc] * Mf[..., None]
        base = muk + np.einsum("nsr,nr->ns", WS, mz)
        Cz = np.einsum("nsr,nrt,nut->nsu", WS, Pz, WS)
        if record_g and r == 1:
            rec["g"][idx] = mz[:, 0]
            rec["gv"][idx] = Pz[:, 0, 0]
            phk = qk / den
            psk = (sk - muk * qk) / den
            w = pr.W[Sc][..., 0]
            A_ = A[l][:, 0, 0][:, None] - phk * w * w
            e_ = eta[l][:, 0][:, None] - psk * w
            rec["g_loo"][idx] = np.where(M, e_ / A_, np.nan)
        mk = (1 - rho) * base + Dk * sk / den
        one_r = (1 - rho) * Mf
        cov = one_r[:, :, None] * one_r[:, None, :] * Cz
        cov += np.eye(Sc.shape[1])[None] * (Dk / den * Mf)[:, :, None]
        nS = at.nS[idx].astype(float)
        m = (mk * Mf).sum(1) / nS
        v = cov.sum((1, 2)) / nS ** 2
        it = at.i[idx]
        ai, bi, ci, di = a[it], b[it], c[it], d[it]
        off = beta * at.x[idx] + hh[idx]
        if comp is not None:
            rc = comp.pre(idx, l, record=record_ns)
            ells = comp.loads(idx, l)
            em, ev = comp.moments(l, ells)
            em, ev = em[:, 0], ev[:, 0]
            if record_ns:
                nf = st.next_first[idx]
                if nf.any():
                    mus = [x[0] if x is not None else cmu[l] for x, cmu in zip(rc, comp.mu)]
                    Vs = [x[1] if x is not None else cV[l] for x, cV in zip(rc, comp.V)]
                    am, av = comp.moments(l, ells, mus, Vs)
                    Pa = probit_P(ai, bi, ci, di, m + off + am[:, 0], v)
                    rec["P_abs"][idx[nf]] = Pa[nf]
                    j0 = [k_ for k_, x in enumerate(rc) if x is not None]
                    if j0:
                        rec["dend"][idx[nf]] = rc[j0[0]][0][nf, 0]
                        rec["Vend"][idx[nf]] = rc[j0[0]][1][nf, 0]
        else:
            em = ev = 0.0
        Sm = m + off + em
        y = at.y[idx]
        if rep:
            Pp = np.clip(probit_P(ai, bi, ci, di, Sm, v), 1e-9, 1 - 1e-9)
            ll = y * np.log(Pp) + (1 - y) * np.log1p(-Pp)
            for k_, mk_ in enumerate(masks):
                sel = mk_[idx]
                LLm[k_][l[sel]] += ll[sel]
        else:
            Pout[idx], mout[idx], vout[idx] = probit_P(ai, bi, ci, di, Sm, v), m, v
            cm[idx] = em
            cvv[idx] = ev
        g, J = score_info(ai, bi, ci, di, Sm, y)
        Jt = 1.0 / (1.0 / J + ev) if comp is not None else J
        if comp is not None:
            _update_grid(comp, idx, l, ells, g[:, None], J[:, None], v)
        rr = S.retention(at.t[idx][:, None] - tl[L2, Sc])
        qn = (qk * rr + (Jt / nS)[:, None]) * Mf
        sn = (sk * rr + ((Jt[:, None] * mk + (Jt * g / J)[:, None]) / nS[:, None])) * Mf
        dphi = (qn / (1 + Dk * qn) - qk / den) * Mf
        dpsi = ((sn - muk * qn) / (1 + Dk * qn) - (sk - muk * qk) / den) * Mf
        rows, cols = np.nonzero(M)
        lr, kr = l[rows], at.S[idx][rows, cols]
        q[lr, kr], s[lr, kr], tl[lr, kr] = qn[rows, cols], sn[rows, cols], at.t[idx][rows]
        A[l] += np.einsum("ns,nsr,nst->nrt", dphi, WS, WS)
        eta[l] += np.einsum("ns,nsr->nr", dpsi, WS)
    if rep:
        return [x.reshape(nl0, R_) for x in LLm]
    if record_g and r == 1:
        rec["g_final"] = (eta[:, 0] / A[:, 0, 0])
    return {"P": Pout, "m": mout, "v": vout, "cm": cm, "cv": cvv, **rec}


# ---------------------------------------------------------------- the engine's Beta, Part A

def run_beta_A(at: S.Attempts, prm: E.Params, K: int, P0=None, n0=1.0, record=False):
    """The engine's update (gstate.run_beta without propagation) with the pair's Beta held as a prior
    part n0 (p0, 1 - p0) plus the evidence part (alpha_e, beta_e), decayed toward 0 by the engine's curve.
    P0 (n, smax): p0 for each attempt's skill slots (A1: the value at the pair's first attempt; A2: the
    current one); None = 0.5. At n0 = 1, p0 = 0.5 this is the engine exactly."""
    Ae = np.zeros((at.nl, K))
    Be = np.zeros((at.nl, K))
    T = np.full((at.nl, K), np.nan)
    P_own = np.empty(at.n)
    rec_a, rec_b = (np.empty(at.n), np.empty(at.n)) if record else (None, None)
    a_i, b_i, c_i, d_i = prm.a[at.i], prm.b[at.i], prm.c[at.i], prm.d[at.i]
    watt = E.LAMBDA ** np.maximum(0, at.att - 1)
    for idx in at.steps:
        l = at.l[idx]
        Sk, M = at.S[idx], at.M[idx]
        Sc = np.where(M, Sk, 0)
        L2 = np.broadcast_to(l[:, None], Sk.shape)
        p0 = 0.5 if P0 is None else P0[idx]
        p0 = np.where(M, p0, 0.5)
        a0 = n0 * p0 + Ae[L2, Sc]
        b0 = n0 * (1 - p0) + Be[L2, Sc]
        ai, bi, ci, di = (x[idx][:, None] for x in (a_i, b_i, c_i, d_i))
        _, Lk, Pp, info = E.item_model(a0, b0, ai, bi, ci, di, prm.mode)
        Mass = E.K * watt[idx][:, None] * (E.MASS_FLOOR + info)
        y = at.y[idx][:, None]
        if prm.mode == "raw":
            s_ = np.broadcast_to(y, Pp.shape)
        else:
            s_ = np.where(y == 1, di * Lk / np.maximum(Pp, E.EPS), (1 - di) * Lk / np.maximum(1 - Pp, E.EPS))
        s_ = np.clip(s_, 0.0, 1.0)
        da, db = Mass * s_, Mass * (1 - s_)
        tot = da + db
        sc = np.where(tot > E.MAX_EVIDENCE_MASS, E.MAX_EVIDENCE_MASS / np.maximum(tot, E.EPS), 1.0)
        da, db = da * sc, db * sc
        P_own[idx] = (Pp * M).sum(1) / at.nS[idx]
        if record:
            rec_a[idx], rec_b[idx] = a0[:, 0], b0[:, 0]
        t = at.t[idx]
        for j in range(Sk.shape[1]):
            v_ = M[:, j]
            if not v_.any():
                continue
            lv, kv, tv = l[v_], Sk[v_, j], t[v_]
            dt = np.nan_to_num(tv - T[lv, kv], nan=0.0)
            rr = np.where(dt > 0, (1.0 + prm.v * np.maximum(dt, 0) / E.DAY) ** (-prm.dd), 1.0) if prm.v > 0 else 1.0
            Ae[lv, kv] = Ae[lv, kv] * rr + da[v_, j]
            Be[lv, kv] = Be[lv, kv] * rr + db[v_, j]
            T[lv, kv] = tv
    return {"P": P_own, "alpha": rec_a, "beta": rec_b}


# ---------------------------------------------------------------- the engine's Beta with the AR state

def logit_beta_var(al, be):
    return polygamma(1, al) + polygamma(1, be)


def run_beta_M(at: S.Attempts, prm: E.Params, K: int, st: Struct, spec=(), filtered=False):
    """C0 plus the components of `spec` (the engine reading). Each skill slot's item model is shifted by
    the components' mean and integrated over their variance (probit); the engine's Beta is updated as
    shipped (ABSORBED) or, with filtered, with each mass multiplied by 1 / (1 + J sum l^2 V) and the
    direction from the shifted item model (FILTERED). Returns P and the attempt-level equivalent linear
    predictor and variance of the engine state (for resid_filter)."""
    A = np.full((at.nl, K), E.PRIOR)
    B = np.full((at.nl, K), E.PRIOR)
    T = np.full((at.nl, K), np.nan)
    comp = Comps(list(spec), at.nl, st) if spec else None
    P_out, S_eq, V_eq = np.empty(at.n), np.empty(at.n), np.empty(at.n)
    a_i, b_i, c_i, d_i = prm.a[at.i], prm.b[at.i], prm.c[at.i], prm.d[at.i]
    watt = E.LAMBDA ** np.maximum(0, at.att - 1)
    for idx in at.steps:
        l = at.l[idx]
        Sk, M = at.S[idx], at.M[idx]
        Sc = np.where(M, Sk, 0)
        L2 = np.broadcast_to(l[:, None], Sk.shape)
        a0, b0 = A[L2, Sc], B[L2, Sc]
        ai, bi, ci, di = (x[idx][:, None] for x in (a_i, b_i, c_i, d_i))
        th, Lk, Pp, info = E.item_model(a0, b0, ai, bi, ci, di, prm.mode)
        vb = logit_beta_var(a0, b0)
        nS = at.nS[idx]
        Patt = (Pp * M).sum(1) / nS
        S_eq[idx] = bi[:, 0] + np.log(np.clip((Patt - ci[:, 0]) / (di[:, 0] - ci[:, 0]), 1e-6, 1 - 1e-6)
                                      / (1 - np.clip((Patt - ci[:, 0]) / (di[:, 0] - ci[:, 0]), 1e-6, 1 - 1e-6))) / ai[:, 0]
        V_eq[idx] = (vb * M).sum(1) / nS
        if comp is not None:
            comp.pre(idx, l)
            ells = comp.loads(idx, l)
            em, ev = comp.moments(l, ells)
            em, ev = em[:, 0], ev[:, 0]
            Psh = probit_P(ai, bi, ci, di, th + em[:, None], 0 * th)
            P_out[idx] = (Psh * M).sum(1) / nS
            g, J = score_info(ai[:, 0], bi[:, 0], ci[:, 0], di[:, 0], S_eq[idx] + em, at.y[idx])
            _update_grid(comp, idx, l, ells, g[:, None], J[:, None], V_eq[idx])
        else:
            P_out[idx] = Patt
        Mass = E.K * watt[idx][:, None] * (E.MASS_FLOOR + info)
        if filtered and comp is not None:
            Lk = sigmoid(ai * (th + em[:, None] - bi))
            Pp = ci + (di - ci) * Lk
            Mass = Mass / (1 + J * ev)[:, None]
        y = at.y[idx][:, None]
        s_ = np.where(y == 1, di * Lk / np.maximum(Pp, E.EPS), (1 - di) * Lk / np.maximum(1 - Pp, E.EPS))
        s_ = np.clip(s_, 0.0, 1.0)
        da, db = Mass * s_, Mass * (1 - s_)
        tot = da + db
        sc = np.where(tot > E.MAX_EVIDENCE_MASS, E.MAX_EVIDENCE_MASS / np.maximum(tot, E.EPS), 1.0)
        da, db = da * sc, db * sc
        t = at.t[idx]
        for j in range(Sk.shape[1]):
            v_ = M[:, j]
            if not v_.any():
                continue
            S._write(A, B, T, l[v_], Sk[v_, j], t[v_], da[v_, j], db[v_, j], prm)
    return {"P": P_out, "S_eq": S_eq, "V_eq": V_eq}
