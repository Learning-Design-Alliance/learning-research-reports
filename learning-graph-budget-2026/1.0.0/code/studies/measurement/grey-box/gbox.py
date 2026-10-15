"""Machinery for the grey-box study. grey_box.py holds the pre-registration; the definitions here are the
ones it states.

  run_grey      the Gaussian grey-box filter: gstate.run_gauss at rank <= 1 plus read-decay, g drift,
                offsets (learning, item memory, traces), the extra components of tstate.Comps (answer
                noise, session shift, per-learner gain and forgetting), a session shift on the slip
                asymptote, the combination rule, the power-logistic link, a no-update (frozen) mask, and
                the replicated-learner grid mode
  run_beta_F    the engine's Beta (C0) and S2's A1 prior on it, with the frozen mask
  Feats         the offset columns, the component loadings and the frozen-pass trace means
  cut_mask      the 30-day horizon: per-learner cut, no-update mask and scored attempts
  g_halves      the descriptive within-learner drift of g against experience volume
  grid_filter   the exact grid filter under world W3's generative model (the approximation check)
"""

from __future__ import annotations

import math

import numpy as np

import engine as E
import gstate as S
import tstate as T

DAY = 86400.0


def sigmoid(z):
    return E.sigmoid(z)


def _row(x, jr):
    """A scalar parameter, or one value per replica indexed by jr (virtual learner % R)."""
    if np.ndim(x) == 0:
        return float(x)
    return np.asarray(x, float)[jr]


def _any(x):
    return np.any(np.asarray(x) != 0)


def lam_of(pr):
    return pr.W[:, 0].copy() if pr.W.shape[1] else np.zeros(len(pr.mu))


def run_grey(at, pr, items, K, st=None, h=None, F=None, coef=None, spec=(), q_g=0.0, comb="comp", s_comb=0.0,
             nu=1.0, shift=0.0, slip_tau=None, upd=None, read_decay=True, rep=None, masks=None, record=False, adf=True):
    """One pass over `at` (learners in parallel, attempts in time order). pr: a dense Prior of rank 0 or 1.

    Per attempt: the skills' predictive means and covariance (graph-state's exact Gaussian conditional for
    theta = mu + lambda z + e), read-decayed; theta_eff = sum w_k m_k (w = 1/nS compensatory, softmax(-/+ s m)
    conjunctive / disjunctive); S = theta_eff + beta x + h + F coef + components; P = c + (d' - c)
    sigmoid(a (S + shift - b) / kappa)^nu, kappa the probit factor of the skills' variance, d' = d or
    sigmoid(logit d + delta_d) with the slip-asymptote session shift. Then (unless upd is False) one
    Laplace step at the point: the skills' pseudo-measurements gain precision Jt w_k with Jt = 1 / (1/J +
    the components' variance) (S2's decoupled step), the components their extended-Kalman updates.
    g drift: before each attempt the general factor's variance grows by q_g x days since the learner's
    previous attempt; every stored contribution is discounted by the same factor (log-weights per skill).

    rep: learners replicated R times (virtual learner l * R + j uses entry j of every per-replica array:
    q_g, s_comb, nu, shift, slip_tau, the rows of coef, the components' parameter arrays); returns the
    per-learner log likelihood (nl, R) on each of masks."""
    R = rep or 1
    a, b, c, d, beta = items
    n, nl0 = at.n, at.nl
    nl = nl0 * R
    lam, mu, Dv = lam_of(pr), pr.mu, pr.D
    has_g = bool(np.any(lam != 0))
    q = np.zeros((nl, K))
    s = np.zeros((nl, K))
    tl = np.full((nl, K), np.nan)
    A = np.ones(nl)
    eta = np.zeros(nl)
    drift = _any(q_g) and has_g
    if drift:
        lw = np.zeros((nl, K))          # log of the discount weight at which each contribution was stored
        lom = np.zeros(nl)              # the learner's current log discount
        tlast = np.full(nl, np.nan)
    comp = T.Comps(list(spec), nl, st, rep=rep) if spec else None
    slip = slip_tau is not None
    if slip:
        mud, Vd, aAd, aBd = np.zeros(nl), np.ones(nl), np.zeros(nl), np.zeros(nl)
    hh = np.zeros(n) if h is None else np.asarray(h, float)
    if F is not None:
        F = np.asarray(F, float)
        coef = np.asarray(coef, float)
    if rep:
        LLm = [np.zeros(nl) for _ in masks]
        jj = np.arange(R)
    else:
        out = {k_: np.empty(n) for k_ in ("P", "m", "v", "off", "em", "ev")}
        if record:
            out["g"] = np.full(n, np.nan)
            out["gv"] = np.full(n, np.nan)
    for idx0 in at.steps:
        if rep:
            idx = np.repeat(idx0, R)
            l = (at.l[idx0][:, None] * R + jj[None]).ravel()
            jr = l % R
        else:
            idx, l = idx0, at.l[idx0]
            jr = None
        tt = at.t[idx]
        Sk = at.S[idx]
        M = at.M[idx]
        Sc = np.where(M, Sk, 0)
        Mf = M.astype(float)
        L2 = np.broadcast_to(l[:, None], Sc.shape)
        if drift:
            dtd = np.where(np.isnan(tlast[l]), 0.0, np.maximum(tt - tlast[l], 0) / DAY)
            r_ = 1.0 / (1.0 + _row(q_g, jr) * dtd * A[l])
            A[l] = A[l] * r_
            eta[l] = eta[l] * r_
            lom[l] = lom[l] + np.log(r_)
            tlast[l] = tt
            wrel = np.exp(lom[l][:, None] - lw[L2, Sc]) * Mf
        else:
            wrel = Mf
        qk, sk = q[L2, Sc] * Mf, s[L2, Sc] * Mf
        Dk, muk, lk = Dv[Sc], mu[Sc], lam[Sc] * Mf
        rr = S.retention(tt[:, None] - tl[L2, Sc])
        den0 = 1 + Dk * qk
        phi0 = qk / den0 * wrel
        psi0 = (sk - muk * qk) / den0 * wrel
        if read_decay:
            qr, sr = qk * rr, sk * rr
            denr = 1 + Dk * qr
            Ar = A[l] + (lk * lk * (qr / denr - phi0)).sum(1)
            er = eta[l] + (lk * ((sr - muk * qr) / denr - psi0)).sum(1)
        else:
            qr, sr, denr = qk, sk, den0
            Ar, er = A[l], eta[l]
        mz = er / Ar
        Pz = 1.0 / Ar
        base = muk + lk * mz[:, None]
        rho = Dk * qr / denr
        mk = (1 - rho) * base + Dk * sr / denr
        one_r = (1 - rho) * Mf
        cov = (one_r * lk)[:, :, None] * (one_r * lk)[:, None, :] * Pz[:, None, None]
        cov += np.eye(Sc.shape[1])[None] * (Dk / denr * Mf)[:, :, None]
        nS = at.nS[idx].astype(float)
        if comb == "comp":
            w = Mf / nS[:, None]
        else:
            sg = -1.0 if comb == "conj" else 1.0
            sc_ = _row(s_comb, jr)
            sc_ = sc_[:, None] if np.ndim(sc_) else sc_
            z_ = np.where(M, sg * sc_ * mk, -np.inf)
            z_ = z_ - z_.max(1, keepdims=True)
            w = np.exp(z_) * Mf
            w = w / w.sum(1, keepdims=True)
        m = (w * mk).sum(1)
        v = np.einsum("ns,nst,nt->n", w, cov, w)
        it = at.i[idx]
        ai, bi, ci, di = a[it], b[it], c[it], d[it]
        off = beta * at.x[idx] + hh[idx]
        if F is not None:
            off = off + ((F[idx] * coef[jr]).sum(1) if rep else F[idx] @ coef)
        if comp is not None:
            comp.pre(idx, l)
            ells = comp.loads(idx, l)
            em, ev = comp.moments(l, ells)
            em, ev = em[:, 0], ev[:, 0]
        else:
            em = ev = 0.0
        if slip:
            first = at.step[idx] == 0
            ss = st.sess_start[idx]
            if st.batch:
                fl = st.new_step[idx] & ~first
                if fl.any():
                    lf = l[fl]
                    Vn = Vd[lf] / (1.0 + Vd[lf] * aAd[lf])
                    mud[lf] = mud[lf] + Vn * aBd[lf]
                    Vd[lf] = Vn
                    aAd[lf] = 0.0
                    aBd[lf] = 0.0
            if ss.any():
                ls_ = l[ss]
                tau_d = _row(slip_tau, jr)
                mud[ls_] = 0.0
                Vd[ls_] = (tau_d[ss] if np.ndim(tau_d) else tau_d) ** 2
                aAd[ls_] = 0.0
                aBd[ls_] = 0.0
            dlt = np.log(di / (1 - di))
            dprime = sigmoid(dlt + mud[l])
        else:
            dprime = di
        nu_r, sh_r = _row(nu, jr), _row(shift, jr)
        Sm = m + off + em
        kap = np.sqrt(1 + math.pi * ai * ai * np.maximum(v, 0) / 8)
        Lp = sigmoid(ai * (Sm + sh_r - bi) / kap)
        P = ci + (dprime - ci) * (Lp if np.ndim(nu_r) == 0 and nu_r == 1.0 else Lp ** nu_r)
        P = np.clip(P, 1e-9, 1 - 1e-9)
        y = at.y[idx]
        if rep:
            ll = y * np.log(P) + (1 - y) * np.log1p(-P)
            for k_, mk_ in enumerate(masks):
                sel = mk_[idx]
                LLm[k_][l[sel]] += ll[sel]
        else:
            out["P"][idx], out["m"][idx], out["v"][idx] = P, m, v
            out["off"][idx], out["em"][idx], out["ev"][idx] = off, em, ev
            if record:
                out["g"][idx], out["gv"][idx] = mz, Pz
        uu = np.ones(len(idx), bool) if upd is None else upd[idx]
        if not uu.any():
            continue
        if adf:
            # moment matching (assumed-density filtering): score and observed information of the
            # probit-integrated likelihood in the predictive mean; pseudo-measurement precision J / (1 - v J)
            kk = ai / kap
            L0 = Lp
            Ln = L0 if np.ndim(nu_r) == 0 and nu_r == 1.0 else L0 ** nu_r
            P0 = P
            dPdS = (dprime - ci) * nu_r * Ln * (1 - L0) * kk
            d2P = (dprime - ci) * nu_r * Ln * (1 - L0) * (nu_r * (1 - L0) - L0) * kk * kk
            rs = (y - P0) / (P0 * (1 - P0))
            g = rs * dPdS
            Jo = dPdS * dPdS * (y / P0 ** 2 + (1 - y) / (1 - P0) ** 2) - d2P * (y / P0 - (1 - y) / (1 - P0))
            vv = np.maximum(v, 1e-12)
            Jo = np.clip(Jo, 1e-12, 0.95 / vv)
            J = Jo / (1 - vv * Jo)
            g = g * J / Jo                       # keeps the pseudo-measurement's value at Sm + g_o / J_o
        else:
            L0 = sigmoid(ai * (Sm + sh_r - bi))
            Ln = L0 if np.ndim(nu_r) == 0 and nu_r == 1.0 else L0 ** nu_r
            P0 = np.clip(ci + (dprime - ci) * Ln, 1e-9, 1 - 1e-9)
            dPdS = (dprime - ci) * nu_r * Ln * (1 - L0) * ai
            rs = (y - P0) / (P0 * (1 - P0))
            g = rs * dPdS
            J = dPdS * dPdS / (P0 * (1 - P0)) + 1e-12
        evt = ev
        if slip:
            dPdd = Ln * dprime * (1 - dprime)
            gd = rs * dPdd
            Jd = dPdd * dPdd / (P0 * (1 - P0)) + 1e-12
            ratio2 = np.minimum((dPdd / np.maximum(dPdS, 1e-12)) ** 2, 1e6)
            evt = ev + Vd[l] * ratio2
        if comp is not None:
            iu = np.nonzero(uu)[0]
            T._update_grid(comp, idx[iu], l[iu], [e[iu] for e in ells], g[iu][:, None], J[iu][:, None], v[iu])
        if slip:
            noise = 1.0 / Jd + (v + ev) / np.maximum(ratio2, 1e-12)
            lu = l[uu]
            if st.batch:
                aAd[lu] += 1.0 / noise[uu]
                aBd[lu] += (gd / Jd / noise)[uu]
            else:
                Kd = Vd[lu] / (Vd[lu] + noise[uu])
                mud[lu] = mud[lu] + Kd * (gd / Jd)[uu]
                Vd[lu] = Vd[lu] * (1 - Kd)
        Jt = 1.0 / (1.0 / J + evt)
        qn = qr + Jt[:, None] * w
        sn = sr + w * (Jt[:, None] * mk + (Jt * g / J)[:, None])
        if not read_decay:
            qn = qk * rr + Jt[:, None] * w
            sn = sk * rr + w * (Jt[:, None] * mk + (Jt * g / J)[:, None])
        qn, sn = qn * Mf, sn * Mf
        dphi = (qn / (1 + Dk * qn) - phi0) * Mf
        dpsi = ((sn - muk * qn) / (1 + Dk * qn) - psi0) * Mf
        Mu = M & uu[:, None]
        rows, cols = np.nonzero(Mu)
        lr, kr = l[rows], Sk[rows, cols]
        q[lr, kr], s[lr, kr], tl[lr, kr] = qn[rows, cols], sn[rows, cols], tt[rows]
        if drift:
            lw[lr, kr] = lom[lr]
        if has_g:
            ufl = uu.astype(float)
            A[l] += (lk * lk * dphi).sum(1) * ufl
            eta[l] += (lk * dpsi).sum(1) * ufl
    if rep:
        return [x.reshape(nl0, R) for x in LLm]
    return out


# ---------------------------------------------------------------- the engine's Beta with the frozen mask

def run_beta_F(at, prm: E.Params, K: int, P0=None, n0=1.0, upd=None):
    """tstate.run_beta_A (the engine's update; with P0 and n0 the A1 prior part) with no writes where upd
    is False. Returns P and the stored alpha, beta of the first skill before each attempt."""
    Ae = np.zeros((at.nl, K))
    Be = np.zeros((at.nl, K))
    Tt = np.full((at.nl, K), np.nan)
    P_own, rec_a, rec_b = np.empty(at.n), np.empty(at.n), np.empty(at.n)
    a_i, b_i, c_i, d_i = prm.a[at.i], prm.b[at.i], prm.c[at.i], prm.d[at.i]
    watt = E.LAMBDA ** np.maximum(0, at.att - 1)
    for idx in at.steps:
        l = at.l[idx]
        Sk, M = at.S[idx], at.M[idx]
        Sc = np.where(M, Sk, 0)
        L2 = np.broadcast_to(l[:, None], Sk.shape)
        p0 = 0.5 if P0 is None else np.where(M, P0[idx], 0.5)
        a0 = n0 * p0 + Ae[L2, Sc]
        b0 = n0 * (1 - p0) + Be[L2, Sc]
        ai, bi, ci, di = (x[idx][:, None] for x in (a_i, b_i, c_i, d_i))
        _, Lk, Pp, info = E.item_model(a0, b0, ai, bi, ci, di, prm.mode)
        P_own[idx] = (Pp * M).sum(1) / at.nS[idx]
        rec_a[idx], rec_b[idx] = a0[:, 0], b0[:, 0]
        uu = np.ones(len(idx), bool) if upd is None else upd[idx]
        if not uu.any():
            continue
        Mass = E.K * watt[idx][:, None] * (E.MASS_FLOOR + info)
        y = at.y[idx][:, None]
        s_ = np.where(y == 1, di * Lk / np.maximum(Pp, E.EPS), (1 - di) * Lk / np.maximum(1 - Pp, E.EPS))
        s_ = np.clip(s_, 0.0, 1.0)
        da, db = Mass * s_, Mass * (1 - s_)
        tot = da + db
        sc = np.where(tot > E.MAX_EVIDENCE_MASS, E.MAX_EVIDENCE_MASS / np.maximum(tot, E.EPS), 1.0)
        da, db = da * sc, db * sc
        t = at.t[idx]
        for j in range(Sk.shape[1]):
            v_ = M[:, j] & uu
            if not v_.any():
                continue
            lv, kv, tv = l[v_], Sk[v_, j], t[v_]
            dt = np.nan_to_num(tv - Tt[lv, kv], nan=0.0)
            rr = np.where(dt > 0, (1.0 + prm.v * np.maximum(dt, 0) / E.DAY) ** (-prm.dd), 1.0) if prm.v > 0 else 1.0
            Ae[lv, kv] = Ae[lv, kv] * rr + da[v_, j]
            Be[lv, kv] = Be[lv, kv] * rr + db[v_, j]
            Tt[lv, kv] = tv
    return {"P": P_own, "alpha": rec_a, "beta": rec_b}


# ---------------------------------------------------------------- horizons

def cut_mask(at, min_att=20, lead_days=30.0):
    """H3: each learner with >= min_att attempts is cut at their median attempt (the first n // 2 attempts
    update); scored = attempts after the cut at least lead_days after the last updating attempt."""
    n_l = np.bincount(at.l, None, at.nl).astype(int)
    cut = np.where(n_l >= min_att, n_l // 2, n_l)
    upd = at.step < cut[at.l]
    start = np.r_[0, np.cumsum(n_l)[:-1]]
    last_upd = start + np.maximum(cut - 1, 0)
    t_cut = at.t[last_upd]
    scored = (~upd) & (at.t - t_cut[at.l] >= lead_days * DAY)
    return upd, scored


# ---------------------------------------------------------------- features

class Feats:
    """Offset columns and loadings for one Attempts (+ its Struct and extras), computed on demand."""

    def __init__(self, at, st, ext, lam, wmap=None, m6_cols=None):
        self.at, self.st, self.ext, self.lam = at, st, ext, lam
        self.wmap = wmap
        self.m6_cols = m6_cols
        self.cache = {}

    def lam_bar(self):
        if "lb" not in self.cache:
            at = self.at
            self.cache["lb"] = (np.where(at.M, self.lam[np.where(at.M, at.S, 0)], 0.0).sum(1) / at.nS)
        return self.cache["lb"]

    def col(self, key):
        if key in self.cache:
            return self.cache[key]
        at, st = self.at, self.st
        kind = key[0]
        if kind == "learn":
            lb = self.lam_bar()
            N = at.step.astype(float)
            form = key[1]
            if form == "lin":
                f = N / 100.0
            elif form == "log":
                f = np.log1p(N)
            else:
                lbn = lb / max(float(np.mean(self.lam[self.lam != 0])) if np.any(self.lam != 0) else 1.0, 1e-9)
                cs = np.cumsum(lbn)
                st0 = np.r_[True, at.l[1:] != at.l[:-1]]
                first = np.maximum.accumulate(np.where(st0, np.arange(at.n), 0))
                before = np.where(first > 0, cs[np.maximum(first - 1, 0)], 0.0)
                f = (cs - lbn - before) / 100.0          # earlier attempts of this learner only
            v = f * lb
        elif kind == "mem":
            seen = st.item_count > 0
            v = np.where(seen, np.exp(-st.item_hours / key[1]), 0.0)
        elif kind == "wmem":
            hrs = self.wrong_hours()
            v = np.where(np.isfinite(hrs), np.exp(-np.nan_to_num(hrs, nan=0.0) / key[1]), 0.0)
        elif kind == "ms":
            v = (at.nS > 1).astype(float)
        elif kind == "m6":
            v = self.m6_cols[key[1]]
        else:
            raise KeyError(key)
        self.cache[key] = v
        return v

    def wrong_hours(self):
        """Hours since the learner's last exposure to item wmap[i] (the deranged same-skill item); inf if
        never."""
        if "wh" in self.cache:
            return self.cache["wh"]
        at = self.at
        I = int(max(at.i.max(), self.wmap.max())) + 1
        key_exp = at.l.astype(np.int64) * I + at.i
        idx = np.arange(at.n, dtype=np.int64)
        comb = key_exp * at.n + idx
        o = np.argsort(comb)
        cs = comb[o]
        qk = at.l.astype(np.int64) * I + self.wmap[at.i]
        qq = qk * at.n + idx
        pos = np.searchsorted(cs, qq, side="left") - 1
        ok = pos >= 0
        cand = o[np.maximum(pos, 0)]
        ok &= key_exp[cand] == qk
        hrs = np.where(ok, (at.t - at.t[cand]) / 3600.0, np.inf)
        self.cache["wh"] = hrs
        return hrs

    def x(self):
        return self.at.x

    def forget(self):
        if "fg" not in self.cache:
            at = self.at
            gm = np.where(at.warm & np.isfinite(at.gap_min), at.gap_min, 0.0)
            self.cache["fg"] = np.log1p(np.maximum(gm, 0) / DAY)
        return self.cache["fg"]


def derange_items(item_skill, rng):
    """Each item mapped to another item with the same first skill (no fixed point); items alone in their
    skill keep themselves (they then never fire)."""
    perm = np.arange(len(item_skill))
    for k in np.unique(item_skill):
        ids = np.nonzero(item_skill == k)[0]
        if len(ids) < 2:
            continue
        while True:
            p = rng.permutation(len(ids))
            if np.all(p != np.arange(len(ids))):
                break
        perm[ids] = ids[p]
    return perm


# ---------------------------------------------------------------- descriptive drift of g

def g_halves(at, pr, items, min_cold=10, iters=12):
    """MAP g (N(0, 1) prior) from first attempts on new skills in each half of each learner's attempts:
    P = c + (d - c) sigmoid(a (mean mu + mean lambda g + beta x - b) / kappa), kappa from the skills' local
    variance. Returns per learner (g1, g2, n_attempts) for learners with >= min_cold such attempts per half."""
    a, b, c, d, beta = items
    lam = lam_of(pr)
    M = at.M
    Sc = np.where(M, at.S, 0)
    first = np.all(np.where(M, at.R == 0, True), 1)
    n_l = np.bincount(at.l, None, at.nl)
    half = (at.step >= (n_l[at.l] // 2)).astype(int)
    nS = at.nS.astype(float)
    mub = np.where(M, pr.mu[Sc], 0).sum(1) / nS
    lb = np.where(M, lam[Sc], 0).sum(1) / nS
    vb = np.where(M, pr.D[Sc], 0).sum(1) / nS ** 2
    sel = first
    grp = (at.l * 2 + half)[sel]
    G = at.nl * 2
    it = at.i[sel]
    ai, bi, ci, di = a[it], b[it], c[it], d[it]
    kap = np.sqrt(1 + math.pi * ai * ai * vb[sel] / 8)
    y = at.y[sel]
    base = mub[sel] + beta * at.x[sel] - bi
    lbs = lb[sel]
    z = np.zeros(G)
    for _ in range(iters):
        L = sigmoid(ai * (base + lbs * z[grp]) / kap)
        P = np.clip(ci + (di - ci) * L, 1e-9, 1 - 1e-9)
        dP = (di - ci) * L * (1 - L) * ai * lbs / kap
        gr = np.bincount(grp, (y - P) / (P * (1 - P)) * dP, G) - z
        hs = np.bincount(grp, dP * dP / (P * (1 - P)), G) + 1
        z = z + np.clip(gr / hs, -2, 2)
    cnt = np.bincount(grp, None, G).reshape(at.nl, 2)
    ok = (cnt >= min_cold).all(1)
    zz = z.reshape(at.nl, 2)
    return zz[ok, 0], zz[ok, 1], n_l[ok], np.nonzero(ok)[0]


# ---------------------------------------------------------------- the approximation check (world W3)

def grid_filter(at, truth, ng=41, nu_=21):
    """Exact posterior predictive under W3's generative model (g ~ N(0,1), u_k ~ N(0, 0.48), the known
    homogeneous practice gain rate log(1 + earlier attempts on the skill), true items), by quadrature: a g grid and, per
    g point and skill, a u grid (the u_k are independent given g). Returns per-attempt P."""
    lam, a, b, c, d = truth["lam"], truth["a"], truth["b"], truth["c"], truth["d"]
    rate, K = truth["rate"], len(lam)
    gx, gw = np.polynomial.hermite_e.hermegauss(ng)
    gw = gw / gw.sum()
    ux, uw = np.polynomial.hermite_e.hermegauss(nu_)
    uw = uw / uw.sum()
    ux = ux * math.sqrt(truth["Du"])
    nl = at.nl
    logwg = np.tile(np.log(gw), (nl, 1))                       # (nl, ng) log posterior weight of g (unnormalised)
    # per learner, skill, g point: log posterior over the u grid, and that skill's log marginal so far
    logpu = np.tile(np.log(uw), (nl, K, ng, 1))
    nk = np.zeros((nl, K))
    Pout = np.empty(at.n)
    for idx in at.steps:
        l = at.l[idx]
        k = at.S[idx, 0]
        i = at.i[idx]
        gnow = rate * np.log1p(nk[l, k])
        th = lam[k][:, None, None] * gx[None, :, None] + ux[None, None, :] + gnow[:, None, None]
        Pg = c[i][:, None, None] + (d[i] - c[i])[:, None, None] * sigmoid(a[i][:, None, None] * (th - b[i][:, None, None]))
        lp = logpu[l, k]                                        # (n, ng, nu)
        mx = lp.max(2, keepdims=True)
        wu = np.exp(lp - mx)
        wu = wu / wu.sum(2, keepdims=True)
        Pgk = (wu * Pg).sum(2)                                  # P given g
        lg = logwg[l]
        wg = np.exp(lg - lg.max(1, keepdims=True))
        wg = wg / wg.sum(1, keepdims=True)
        P = (wg * Pgk).sum(1)
        Pout[idx] = P
        y = at.y[idx]
        lik = np.where(y[:, None, None] == 1, Pg, 1 - Pg)
        logpu[l, k] = lp + np.log(np.clip(lik, 1e-12, 1))
        # the g weights: multiply by P(y | g) integrated over this skill's u
        lik_g = np.where(y[:, None] == 1, Pgk, 1 - Pgk)
        logwg[l] = lg + np.log(np.clip(lik_g, 1e-12, 1))
        nk[l, k] += 1
    return Pout
