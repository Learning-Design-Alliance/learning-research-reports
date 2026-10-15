"""Machinery for the filter re-check. filter_recheck.py holds the pre-registration; the definitions here
are the ones it states.

  step        the per-response update quantities (score g, information J) of the Gaussian filters:
              LAPLACE (graph-state's extended-Kalman step at the point, gstate.run_gauss and
              tstate.score_info verbatim) or MOMENT MATCHING (grey-box's assumed-density step, the
              adf branch of gbox.run_grey at nu = 1 with no extra components)
  run_gauss   gstate.run_gauss with the step selectable (adf) and, for the exact-filter check only,
              evidence decay switchable off (decay)
  run_joint   tstate.run_joint without extra components (Part A of state-timescales uses none), with
              the step selectable

With adf=False and decay=True both are gstate.run_gauss and tstate.run_joint exactly (checked to 1e-9 in
the synthetic record). Nothing else in either filter differs: the predictive mean and variance, the
forecast P, the hyperedge spread (J / nS at value m_k + g / J), the lazy decay and the information-form
bookkeeping are copied unchanged.
"""

from __future__ import annotations

import math

import numpy as np

import gstate as S
import tstate as T


def sigmoid(z):
    return S.sigmoid(z)


def step(ai, bi, ci, di, Sm, v, y, adf):
    """(g, J): the pseudo-measurement of the linear predictor is precision J at value Sm + g / J.

    Laplace: score and Fisher information of the plain 4PL at the point Sm.
    Moment matching: score g_o and observed information J_o of the probit-integrated likelihood
    P = c + (d - c) sigmoid(a (Sm - b) / kappa), kappa = sqrt(1 + pi a^2 v / 8), in the predictive mean;
    J = J_o / (1 - v J_o) and g = g_o J / J_o, so the posterior of S is the moment-matched Gaussian
    (mean Sm + v g_o, variance v - v^2 J_o) and the value stays at Sm + g_o / J_o."""
    if not adf:
        L0 = sigmoid(ai * (Sm - bi))
        P0 = np.clip(ci + (di - ci) * L0, 1e-9, 1 - 1e-9)
        dP = (di - ci) * ai * L0 * (1 - L0)
        g = np.where(y == 1, dP / P0, -dP / (1 - P0))
        J = dP * dP / (P0 * (1 - P0)) + 1e-12
        return g, J
    kap = np.sqrt(1 + math.pi * ai * ai * np.maximum(v, 0) / 8)
    kk = ai / kap
    L = sigmoid(ai * (Sm - bi) / kap)
    P = np.clip(ci + (di - ci) * L, 1e-9, 1 - 1e-9)
    dPdS = (di - ci) * L * (1 - L) * kk
    d2P = (di - ci) * L * (1 - L) * ((1 - L) - L) * kk * kk
    g_o = (y - P) / (P * (1 - P)) * dPdS
    Jo = dPdS * dPdS * (y / P ** 2 + (1 - y) / (1 - P) ** 2) - d2P * (y / P - (1 - y) / (1 - P))
    vv = np.maximum(v, 1e-12)
    Jo = np.clip(Jo, 1e-12, 0.95 / vv)
    J = Jo / (1 - vv * Jo)
    return g_o * J / Jo, J


def run_gauss(at, pr, items, K, adf=True, decay=True):
    """gstate.run_gauss with the update step selectable. Returns per attempt P, m, v."""
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
            ar_ = np.arange(len(l))[:, None]
            ug, dg, egg = ul[ar_, gS], dll[ar_, gS], egl[ar_, gS]
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
        Pout[idx], mout[idx], vout[idx] = S._probit_P(ai, bi, ci, di, m + off, v), m, v
        g, J = step(ai, bi, ci, di, m + off, v, at.y[idx], adf)
        rr = S.retention(at.t[idx][:, None] - tl[L2, Sc]) if decay else 1.0
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


_ORIG_RUN_JOINT = T.run_joint


def run_joint(at, pr, items, K, st=None, h=None, spec=(), record_g=False, record_ns=False, rep=None, masks=None,
              adf=True):
    """tstate.run_joint without extra components, with the update step selectable. With components the
    original tstate.run_joint (its Laplace step) is called, and only with adf=False."""
    if spec:
        assert not adf, "moment matching with extra components is not defined in this re-check"
        return _ORIG_RUN_JOINT(at, pr, items, K, st=st, h=h, spec=spec, record_g=record_g, record_ns=record_ns,
                               rep=rep, masks=masks)
    assert rep is None and not record_ns
    a, b, c, d, beta = items
    n, nl = at.n, at.nl
    q = np.zeros((nl, K))
    s = np.zeros((nl, K))
    tl = np.full((nl, K), np.nan)
    r = pr.W.shape[1]
    A = np.broadcast_to(np.eye(r), (nl, r, r)).copy()
    eta = np.zeros((nl, r))
    Pout, mout, vout, cm, cvv = np.empty(n), np.empty(n), np.empty(n), np.zeros(n), np.zeros(n)
    rec = {}
    if record_g:
        rec["g"] = np.empty(n)
        rec["gv"] = np.empty(n)
        rec["g_loo"] = np.full(at.S.shape, np.nan)
    hh = np.zeros(n) if h is None else h
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
        Sm = m + beta * at.x[idx] + hh[idx]
        Pout[idx], mout[idx], vout[idx] = T.probit_P(ai, bi, ci, di, Sm, v), m, v
        g, J = step(ai, bi, ci, di, Sm, v, at.y[idx], adf)
        rr = S.retention(at.t[idx][:, None] - tl[L2, Sc])
        qn = (qk * rr + (J / nS)[:, None]) * Mf
        sn = (sk * rr + ((J[:, None] * mk + g[:, None]) / nS[:, None])) * Mf
        dphi = (qn / (1 + Dk * qn) - qk / den) * Mf
        dpsi = ((sn - muk * qn) / (1 + Dk * qn) - (sk - muk * qk) / den) * Mf
        rows, cols = np.nonzero(M)
        lr, kr = l[rows], at.S[idx][rows, cols]
        q[lr, kr], s[lr, kr], tl[lr, kr] = qn[rows, cols], sn[rows, cols], at.t[idx][rows]
        A[l] += np.einsum("ns,nsr,nst->nrt", dphi, WS, WS)
        eta[l] += np.einsum("ns,nsr->nr", dpsi, WS)
    if record_g and r == 1:
        rec["g_final"] = (eta[:, 0] / A[:, 0, 0])
    return {"P": Pout, "m": mout, "v": vout, "cm": cm, "cv": cvv, **rec}
