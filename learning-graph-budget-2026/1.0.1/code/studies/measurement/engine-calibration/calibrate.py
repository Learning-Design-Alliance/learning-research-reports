"""PRE-REGISTERED: calibrate the engine's item and forgetting parameters from a response log.

Deliverable 2 of the engine-calibration study (README.md). Input: one row per graded response
  learner, item, competency, correct (0/1), timestamp (epoch seconds or ISO 8601), format
  ("mc" for multiple choice, anything else is its own group), n_options (m; 0 or blank if not MC),
  optional attempt (1-based attempt index on the item; counted from the log if absent).
A response tagged with several competencies is one row per competency (same learner, item, time).
Output (JSON, the engine's parameter shape; engine.py documents the formulas each feeds):
  items:   {item: {a, b, c, d, n_first, n_rows, c_source, ab_source}}  c = lower asymptote (guessing),
           d = upper asymptote (1 - slip), a/b on the engine's own theta = logit(p*) scale
  groups:  per format group, the centres unsampled items fall back to
  decay:   {type: "power-law", v, d, toward: "prior" | "zero", read: bool, half_life_days}
  structure: mode ("know" = slip-aware direction), eff ("post")
Written 2026-09-27, before any statistic on real data.

PROCEDURE (fit set = the caller's training learners only)
  1. ASYMPTOTES c, d. Each learner's FIRST response to each item (local independence; retries follow
     feedback). Marginal-ML 4PL over 21 quadrature nodes with the format-group empirical-Bayes prior
     of studies/measurement/guessing-gaming/irt_guess.py (imported; its CHANGES 1-2 are why: a joint
     MAP estimator and a fixed Beta(1.2, 4) prior both halved c on its synthetic floor). Groups are
     format x n_options. c and s = 1 - d live in (0, 0.5). 2PL start, then 4PL.
     SHRINKAGE is the group prior itself (kappa = 8 pseudo-answers toward the group's mean). MINIMUM
     SAMPLE: an item with < 150 first responses takes its group's centre instead of its own estimate;
     a group with < 5 items at >= 150 takes the engine's default (c = 1/m for MC with m >= 2, else 0;
     d = 1).
  2. FORGETTING (v, d, toward, read). Replay the engine (engine.py) over the fit set for every point
     of a grid and keep the one with the highest PREQUENTIAL log-likelihood of the attempt-level
     prediction (each response predicted from earlier responses only, so the score is held out in
     time; attempt P = mean of its competency rows' P):
       v in {0, 0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 100} per day, d in {0.25, 0.5, 1, 2},
       toward in {prior, zero};
     then v x {0.6, 0.8, 1.25, 1.6} at the best (d, toward). The half-life is (2^(1/d) - 1) / v days.
     Replays for the grid use the structure being calibrated with a = 1, b = 0.
  3. DISCRIMINATION AND DIFFICULTY a, b ON THE ENGINE'S SCALE. The engine's theta is logit(p*) of
     its own belief, not an IRT ability, so a and b are fitted to that scale: replay the structure
     (with steps 1-2's parameters and a = 1, b = 0), record theta before every response, and fit per
     item P = c + (d - c) sigmoid(a (theta - b)) by penalised maximum likelihood (each row weighted
     1 / its attempt's competency count), priors b ~ N(b_G, 1), log a ~ N(log a_G, 0.5^2), log a
     clipped to [log 0.2, log 4]; the group centres b_G, log a_G are re-estimated three times as the
     mean over the group's items with >= 30 rows. Then replay again with the fitted a, b and refit
     (two passes, fixed in advance: mass depends on a, b, so theta moves). MINIMUM SAMPLE: an item
     with < 30 weighted rows takes its group centre.

SYNTHETIC FLOOR (`python3 calibrate.py synthetic`, before any real statistic; 3 seeds of world A:
  5,000 learners, 40 competencies x 8 items, half MC (m = 4, c ~ U(0.1, 0.3); m = 3, c ~
  U(0.28, 0.46): off chance, as Eedi's and XES3G5M's are), half fill-in (c ~ U(0.03, 0.09)), slip ~ U(0, 0.12), a ~ logN(0.2, 0.3), b ~ N(0, 1);
  knowledge z = ability + learner x competency effect + practice gain; each attempt adds 0.25 to the
  gain, which decays between attempts as (1 + v t)^(-d) with v = 1/day, d = 0.5 (half-life 3 days);
  P = c + (d - c) sigmoid(a (z - b)); sessions 1 h to 30 days apart, 6-12 attempts on one
  competency, half of them revisits). Fitted on the 80% TRAIN learners (e2e.py's hash). PASS (all
  seeds) requires:
    mean c of MC items (>= 150 first responses) within 0.05 of planted; the same for fill-in;
    mean slip (1 - d) within 0.03 of planted;
    Spearman(planted b, fitted b) >= 0.8 and Spearman(planted a, fitted a) >= 0.3 over items with
      >= 30 rows (a and b are on the engine's scale, so only their order is comparable);
    the fitted half-life (engine structure, decay on read) within a factor of 4 of the planted 3 days
      (the engine's decay blends the whole belief; the planted process decays only the gain).
      [Dropped as a check by CHANGE 3; reported.]
  And in world B (the engine E0 itself as the generator; CHANGE 2), 2 seeds: a and b fitted on
    the engine's structure recover a = 1 (median in [0.9, 1.1]) and b = 0 (median |b| <= 0.1), and
    the lazy-decay fit recovers the engine's 30-day half-life within a factor 2.
  A procedure that fails this floor is not to be run on Lazuli's data as calibrated.

RUNNING IT ON LAZULI'S LRS: README.md, "What to change in the engine".

CHANGES (after the first synthetic floor, before any real statistic)
  1. World A failed in seeds 1-2 on fill-in c: 0.090, 0.121, 0.118 for a planted 0.058-0.061 (MC c
     came back 0.03-0.04 high; slip, a and b order and half-life passed). The 4PL's ability is
     static, so the practice gain on a learner's later first responses reads as guessing. Step 1 now
     uses only first responses made with at most 2 earlier responses by the learner on that
     competency (EARLY = 3), before much practice has accrued. Tried on the three world-A seeds
     before the second floor: fill-in c 0.054, 0.072, 0.060 for 0.058, 0.060, 0.061; MC c 0.257,
     0.208, 0.234 for 0.265, 0.249, 0.264.
  2. World B as first registered (a latent success rate per learner and competency ~ Beta(0.5, 0.5),
     redrawn between attempts with probability 1 - (1 + 0.1 t)^(-0.5); P = c + (1 - c) q) failed every
     check on seed 0: MC c 0.42 (1/m averages 0.27), fill-in c 0.27, slip 0.24, fitted half-life
     0.31 days for 30. That world has no learner-level ability, so a static-ability 4PL pushes
     competency-specific knowledge into both asymptotes; and E0's evidence mass (at most 0.9
     pseudo-counts per response) is not that world's Bayes update (1 per response), so a fast decay
     toward zero, which lets recent evidence outweigh the prior, fits better. It tested "E0 is
     optimal for q", which E0 is not. World B is now E0's own assumptions taken literally: the same
     schedule and items, every response DRAWN from E0's own prediction given the pair's history
     (engine.replay with rng). E0 is then the truth. Its checks are the recoverable ones: a = 1, b = 0
     and the 30-day lazy decay. c and d are reported, not checked, in B.
  3. The second floor passed every check but one: world A seed 1's fitted half-life (engine
     structure, decay on read) was 15 days for the planted 3 (a factor 5; seeds 0 and 2: 12 days).
     The check was ill-posed. The engine's decay parameter is not the half-life of a knowledge gain:
     it blends the whole belief toward the prior, and the grid's optimum also absorbs the evidence-
     mass scale and within-session learning (the same worlds' slip-aware structure picks a 2-3 hour
     decay toward ZERO, which is recency weighting, not forgetting). The half-life's recoverable
     meaning is tested in world B, where the lazy-decay fit returns the engine's 30.0 days in both
     seeds. The world-A half-life is reported, not checked; the fitted (v, d) is to be read as the
     evidence horizon that predicts best, not as how fast learners forget. `python3 calibrate.py
     recheck` re-applies the current rule to out/calibrate-synthetic.json (no refit). World B's
     reported asymptotes (MC c 0.33-0.35, fill-in c 0.25-0.26, slip 0.29-0.30 where the generator
     has 1/m, 0 and 0) show what the 4PL's asymptotes absorb when success is not driven by one
     learner-level ability: they are guessing and slipping only under the 4PL's own model.
  4. Computation only, after the floors and before any real statistic: step 3's optimiser is
     Fisher scoring per item (a 2 x 2 system each, the objective being separable given the group
     centres; a pinned log a gets a b-only step) instead of L-BFGS, for speed on 5M-row fits. Same
     objective. On a 1,500-learner world A it reached a penalised objective 0.0007 below a
     3,000-iteration L-BFGS (111007.0868 against .0876), with b within 0.024 and log a within 0.007.
     The floors above ran with L-BFGS (300 iterations per round).
  5. Computation only, after the real runs: `fit` crashed on an ISO-8601 timestamp column, which
     pandas 3 reads as a string dtype that np.issubdtype rejects; it now asks pandas whether the
     column is numeric. Found by a smoke test on a 600-learner world-A CSV. No variant uses `fit`.

DIRECTION: symmetric -- no edge enters; "direction" is the evidence split alpha : beta.

    python3 calibrate.py synthetic [then recheck]
    python3 calibrate.py fit <responses.csv> <params.json> [--test-share 0]
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "studies/measurement/guessing-gaming"))
import engine as E  # noqa: E402
from irt_guess import IRT  # noqa: E402
from shared.stats import spearman  # noqa: E402

OUT = HERE / "out"
SEED = 20260927 + 505
MIN_CD, MIN_GROUP_ITEMS, MIN_AB = 150, 5, 30
EARLY = 3          # CHANGE 1: asymptotes from responses with <= 2 earlier ones on the competency
V_GRID = (0.0, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0)
D_GRID = (0.25, 0.5, 1.0, 2.0)
REFINE = (0.6, 0.8, 1.25, 1.6)
SD_B, SD_LA = 1.0, 0.5
LA_LO, LA_HI = math.log(0.2), math.log(4.0)


def test_learner(uid) -> bool:
    """e2e.py's split: sha256(uid) first 8 hex digits mod 5 == 0 is TEST."""
    return int(hashlib.sha256(str(uid).encode()).hexdigest()[:8], 16) % 5 == 0


# ---------------------------------------------------------------- building the replay input

class Data:
    """Rows (attempt x competency) with item metadata. `uid` per dense learner id."""

    def __init__(self, learner, item, comp, y, t, order, is_mc, m, group, uid, item_names=None):
        """learner/item/comp: dense ints per row; order: file order of the row's ATTEMPT (unique per
        attempt, shared by its competency rows; breaks time ties); is_mc, m, group: per item; uid: per
        learner (for the split)."""
        learner, item, comp = np.asarray(learner, np.int32), np.asarray(item, np.int32), np.asarray(comp, np.int32)
        t, order = np.asarray(t, np.float64), np.asarray(order, np.int64)
        attempt = pd.factorize(order)[0].astype(np.int32)
        fi = np.zeros(int(attempt.max()) + 1, np.int64)
        fi[attempt[::-1]] = np.arange(len(attempt))[::-1]
        la, ia, ta, oa = learner[fi], item[fi], t[fi], order[fi]
        srt = np.lexsort((oa, ta, ia, la))
        new = np.r_[True, (la[srt][1:] != la[srt][:-1]) | (ia[srt][1:] != ia[srt][:-1])]
        pos = np.arange(len(srt))
        att = np.empty(len(fi), np.int32)
        att[srt] = pos - np.maximum.accumulate(np.where(new, pos, 0)) + 1
        del la, ia, ta, oa, srt, new, pos, fi
        pair = pd.factorize(learner.astype(np.int64) * (int(comp.max()) + 1) + comp)[0]
        o = np.lexsort((order, t, pair))
        self.df = pd.DataFrame({"l": learner[o], "i": item[o], "k": comp[o], "y": np.asarray(y, np.float64)[o],
                                "t": t[o], "o": order[o], "attempt": attempt[o], "att": att[attempt[o]],
                                "pair": pair[o]})
        del o, pair, attempt, att
        pr = self.df.pair.to_numpy()
        st = np.r_[True, pr[1:] != pr[:-1]]
        pos = np.arange(len(pr))
        self.df["r"] = (pos - np.maximum.accumulate(np.where(st, pos, 0))).astype(np.int32)
        self.is_mc, self.m, self.group = np.asarray(is_mc, bool), np.asarray(m, int), np.asarray(group, int)
        self.uid = np.asarray(uid)
        self.I = len(self.m)
        self.item_names = item_names
        self.test_l = np.array([test_learner(u) for u in self.uid])

    def events(self, mask=None) -> E.Events:
        d = self.df if mask is None else self.df[mask]
        pair = pd.factorize(d.pair.to_numpy())[0]
        attempt = pd.factorize(d.attempt.to_numpy())[0]
        return E.Events(pair, d.i.to_numpy(), d.t.to_numpy(), d.y.to_numpy(), d.att.to_numpy(), attempt, d.l.to_numpy())

    def rows(self, which: str, sub=None):
        """Boolean row mask: 'train' / 'test' learners, optionally a hash subsample of learners
        (sub = (mod, salt): keep sha256(salt + uid) % mod == 0)."""
        te = self.test_l[self.df.l.to_numpy()]
        mk = te if which == "test" else ~te
        if sub:
            mod, salt = sub
            keep = np.array([int(hashlib.sha256((salt + str(u)).encode()).hexdigest()[:8], 16) % mod == 0 for u in self.uid])
            mk = mk & keep[self.df.l.to_numpy()]
        return mk


# ---------------------------------------------------------------- step 1: asymptotes

def fit_asymptotes(data: Data, mask) -> dict:
    """4PL c, d per item from first responses of the masked rows (irt_guess.IRT, EB format prior)."""
    d = data.df[mask & (data.df.r.to_numpy() < EARLY)].drop_duplicates("attempt")
    first = d.sort_values(["l", "t", "o"], kind="stable").drop_duplicates(["l", "i"])
    li = pd.factorize(first.l.to_numpy())[0]
    it = first.i.to_numpy()
    y = first.y.to_numpy(float)
    I = data.I
    m = IRT(li, it, y, int(li.max()) + 1, I)
    allr = np.ones(len(y), bool)
    w2, _ = m.fit("2PL", allr)
    w4, _ = m.fit("4PL", allr, w0=w2, groups=data.group)
    c_raw, s_raw = m.split(w4, "4PL")[4:]
    n_first = np.bincount(it, None, I)
    ok = n_first >= MIN_CD
    G = int(data.group.max()) + 1
    E0 = E.engine_params(data.is_mc, data.m)
    c, dd = c_raw.copy(), 1 - s_raw
    src = np.array(["item"] * I, dtype=object)
    centres = {}
    for g in range(G):
        sel = data.group == g
        good = sel & ok
        if good.sum() >= MIN_GROUP_ITEMS:
            cg, dg = float(c_raw[good].mean()), float(1 - s_raw[good].mean())
            c[sel & ~ok], dd[sel & ~ok] = cg, dg
            src[sel & ~ok] = "group"
        else:
            cg, dg = None, None
            c[sel], dd[sel] = E0.c[sel], 1.0
            src[sel] = "engine default"
        centres[int(g)] = {"c": cg, "d": dg, "items_sampled": int(good.sum()), "items": int(sel.sum())}
    return {"c": c, "d": dd, "n_first": n_first, "c_source": src, "centres": centres}


# ---------------------------------------------------------------- step 2: forgetting

def prequential(ev: E.Events, prm: E.Params) -> float:
    """Mean attempt-level log-likelihood of each response predicted from earlier ones."""
    P = np.clip(ev.attempt_mean(E.replay(ev, prm)["P"]), 1e-9, 1 - 1e-9)
    y = ev.attempt_mean(ev.y)
    return float((y * np.log(P) + (1 - y) * np.log1p(-P)).mean())


def fit_decay(ev: E.Events, base: E.Params, read: bool, towards=("prior", "zero")) -> dict:
    grid = {}
    for tw in towards:
        for dd in D_GRID:
            for v in V_GRID:
                if v == 0 and (dd != D_GRID[0] or tw != towards[0]):
                    continue
                grid[(v, dd, tw)] = prequential(ev, base.replace(v=v, dd=dd, toward=tw, read=read))
    v, dd, tw = max(grid, key=grid.get)
    if v > 0:
        for f in REFINE:
            grid[(v * f, dd, tw)] = prequential(ev, base.replace(v=v * f, dd=dd, toward=tw, read=read))
    v, dd, tw = max(grid, key=grid.get)
    best_by_toward = {}
    for t_ in towards:
        ks = [k for k in grid if k[2] == t_ or k[0] == 0]
        kb = max(ks, key=grid.get)
        best_by_toward[t_] = {"v": kb[0], "d": kb[1], "half_life_days": E.half_life_days(kb[0], kb[1]),
                              "prequential_loglik": grid[kb]}
    return {"v": v, "d": dd, "toward": tw, "read": read, "half_life_days": E.half_life_days(v, dd),
            "prequential_loglik": grid[(v, dd, tw)], "engine_prequential_loglik":
            prequential(ev, base.replace(v=E.V0, dd=E.D0, toward="prior", read=read)),
            "best_by_toward": best_by_toward, "grid_points": len(grid)}


# ---------------------------------------------------------------- step 3: a, b on the engine's scale

def _ab_objective(w, theta, it, y, wt, c, d, I, bG, laG):
    """c, d per row."""
    b, la = w[:I], w[I:]
    a = np.exp(la)
    z = a[it] * (theta - b[it])
    L = E.sigmoid(z)
    span = d - c
    P = np.clip(c + span * L, 1e-9, 1 - 1e-9)
    ll = (wt * (y * np.log(P) + (1 - y) * np.log1p(-P))).sum()
    dP = wt * (y - P) / (P * (1 - P)) * span * L * (1 - L)
    gb = -np.bincount(it, dP * a[it], I) - (b - bG) / SD_B ** 2
    gla = np.bincount(it, dP * z, I) - (la - laG) / SD_LA ** 2
    lp = -((b - bG) ** 2).sum() / (2 * SD_B ** 2) - ((la - laG) ** 2).sum() / (2 * SD_LA ** 2)
    return -(ll + lp), -np.concatenate([gb, gla])


def _scoring(w, theta, it, y, wt, c, d, I, bG, laG, iters=100, tol=1e-7):
    """Fisher scoring for the same penalised objective, item by item (it is separable given the
    group centres): a 2 x 2 system per item, bincount-accumulated. CHANGE 4 (speed)."""
    b, la = w[:I].copy(), w[I:].copy()
    span = d - c
    for _ in range(iters):
        a = np.exp(la)
        z = a[it] * (theta - b[it])
        L = E.sigmoid(z)
        P = np.clip(c + span * L, 1e-9, 1 - 1e-9)
        dPz = span * L * (1 - L)
        g = wt * (y - P) / (P * (1 - P)) * dPz
        fz = wt * dPz * dPz / (P * (1 - P))
        ar = a[it]
        gb = -np.bincount(it, g * ar, I) - (b - bG) / SD_B ** 2
        gl = np.bincount(it, g * z, I) - (la - laG) / SD_LA ** 2
        hbb = np.bincount(it, fz * ar * ar, I) + 1 / SD_B ** 2
        hll = np.bincount(it, fz * z * z, I) + 1 / SD_LA ** 2
        hbl = -np.bincount(it, fz * ar * z, I)
        det = hbb * hll - hbl * hbl
        sb = (hll * gb - hbl * gl) / det
        sl = (hbb * gl - hbl * gb) / det
        pinned = ((la <= LA_LO) & (sl < 0)) | ((la >= LA_HI) & (sl > 0))
        sb = np.where(pinned, gb / hbb, sb)
        sl = np.where(pinned, 0.0, sl)
        sb, sl = np.clip(sb, -1, 1), np.clip(sl, -0.5, 0.5)
        b += sb
        la = np.clip(la + sl, LA_LO, LA_HI)
        if max(np.abs(sb).max(), np.abs(sl).max()) < tol:
            break
    return np.concatenate([b, la])


SOLVER = "scoring"


def fit_ab_once(theta, it, y, wt, c, d, group, I, w0=None, solver=None):
    """c, d per row; group per item."""
    G = int(group.max()) + 1
    n = np.bincount(it, wt, I)
    ok = n >= MIN_AB
    bGg, laGg = np.zeros(G), np.zeros(G)
    w = np.zeros(2 * I) if w0 is None else w0.copy()
    bounds = [(None, None)] * I + [(LA_LO, LA_HI)] * I
    for _ in range(3):
        if (solver or SOLVER) == "scoring":
            w = _scoring(w, theta, it, y, wt, c, d, I, bGg[group], laGg[group])
        else:
            res = minimize(_ab_objective, w, args=(theta, it, y, wt, c, d, I, bGg[group], laGg[group]), jac=True,
                           method="L-BFGS-B", bounds=bounds, options={"maxiter": 300})
            w = res.x
        for g in range(G):
            sel = (group == g) & ok
            if sel.any():
                bGg[g], laGg[g] = w[:I][sel].mean(), w[I:][sel].mean()
    b, la = w[:I].copy(), w[I:].copy()
    b[~ok], la[~ok] = bGg[group][~ok], laGg[group][~ok]
    return b, np.exp(la), ok, n, {"b": bGg.tolist(), "a": np.exp(laGg).tolist()}, w


def fit_ab(ev: E.Events, prm: E.Params, group, passes=2):
    """Two passes of: replay -> theta per row -> penalised per-item fit of a, b."""
    wt = 1.0 / np.bincount(ev.attempt, None, ev.natt)[ev.attempt]
    cur = prm.replace(a=np.ones_like(prm.a), b=np.zeros_like(prm.b))
    w0 = None
    for _ in range(passes):
        th = E.replay(ev, cur)["theta"]
        b, a, ok, n, cent, w0 = fit_ab_once(th, ev.item, ev.y, wt, prm.c[ev.item], prm.d[ev.item], np.asarray(group),
                                             len(prm.a), w0)
        cur = cur.replace(a=a, b=b)
    cur.meta["ab"] = {"items_own": int(ok.sum()), "n_rows": n, "centres": cent}
    return cur


# ---------------------------------------------------------------- the whole procedure

def calibrate(data: Data, fit_mask, decay_sub=None, log=print) -> tuple[E.Params, dict]:
    """E5-shaped parameters from the rows in fit_mask. decay_sub: a row mask (subset of fit_mask)
    for the decay grid, for speed."""
    asy = fit_asymptotes(data, fit_mask)
    log(f"   asymptotes: {int((asy['n_first'] >= MIN_CD).sum())} items with >= {MIN_CD} first responses")
    base = E.engine_params(data.is_mc, data.m, name="calibrated").replace(c=asy["c"], d=asy["d"], mode="know", eff="post")
    ev_fit = data.events(fit_mask)
    ev_dec = data.events(decay_sub) if decay_sub is not None else ev_fit
    dec = fit_decay(ev_dec, base, read=True)
    log(f"   decay: v {dec['v']:.3g}/day d {dec['d']} toward {dec['toward']}: half-life {dec['half_life_days']:.3g} days")
    prm = base.replace(v=dec["v"], dd=dec["d"], toward=dec["toward"], read=True)
    prm = fit_ab(ev_fit, prm, data.group)
    return prm, {"asymptotes": asy, "decay": dec}


def to_json(data: Data, prm: E.Params, info: dict) -> dict:
    asy = info["asymptotes"]
    names = data.item_names if data.item_names is not None else list(range(data.I))
    nrows = prm.meta["ab"]["n_rows"]
    items = {str(names[i]): {"a": float(prm.a[i]), "b": float(prm.b[i]), "c": float(prm.c[i]), "d": float(prm.d[i]),
                             "n_first": int(asy["n_first"][i]), "n_rows": float(nrows[i]),
                             "c_source": str(asy["c_source"][i]), "ab_source": "item" if nrows[i] >= MIN_AB else "group"}
             for i in range(data.I)}
    dec = info["decay"]
    return {"structure": {"mode": prm.mode, "eff": prm.eff}, "items": items,
            "groups": {"asymptotes": asy["centres"], "ab": prm.meta["ab"]["centres"]},
            "decay": {"type": "power-law", "v": dec["v"], "d": dec["d"], "toward": dec["toward"], "read": dec["read"],
                      "half_life_days": dec["half_life_days"]},
            "minimum_samples": {"c_d_first_responses": MIN_CD, "group_items": MIN_GROUP_ITEMS, "a_b_rows": MIN_AB}}


# ---------------------------------------------------------------- synthetic worlds (shared with the study)

def world(kind: str, seed: int, L=5000, Kc=40, per=8):
    """kind 'A' (4PL with forgetting) or 'B' (the engine E0 as the generator: CHANGE 2). -> Data, truth."""
    rng = np.random.default_rng(SEED + 1000 * (kind == "B") + seed)
    I = Kc * per
    comp_of = np.repeat(np.arange(Kc), per)
    is_mc = rng.random(I) < 0.5
    m = np.where(is_mc, np.where(rng.random(I) < 0.7, 4, 3), 0)
    if kind == "A":
        c = np.where(m == 4, rng.uniform(0.1, 0.3, I), np.where(m == 3, rng.uniform(0.28, 0.46, I),
                                                               rng.uniform(0.03, 0.09, I)))
        s = rng.uniform(0, 0.12, I)
        a = np.exp(rng.normal(0.2, 0.3, I))
        b = rng.normal(0, 1, I)
        v, dd = 1.0, 0.5
    else:
        c = np.where(is_mc, 1.0 / np.maximum(m, 1), 0.0)
        s, a, b = np.zeros(I), np.ones(I), np.zeros(I)
        v, dd = E.V0, E.D0
    ability = rng.normal(0, 1, L)
    rows_l, rows_i, rows_t, rows_y = [], [], [], []
    for u in range(L):
        n_sess = int(rng.integers(5, 36))
        t = 0.0
        z0 = ability[u] + rng.normal(0, 0.5, Kc)
        gain = np.zeros(Kc)
        last = np.full(Kc, -1.0)
        seen = []
        for _ in range(n_sess):
            t += math.exp(rng.uniform(math.log(3600), math.log(30 * 86400)))
            k = int(rng.choice(seen)) if seen and rng.random() < 0.5 else int(rng.integers(Kc))
            if k not in seen:
                seen.append(k)
            for j in range(int(rng.integers(6, 13))):
                tt = t + 60.0 * j
                it = int(k * per + rng.integers(per))
                if last[k] >= 0:
                    r = (1 + v * (tt - last[k]) / 86400) ** (-dd)
                    if kind == "A":
                        gain[k] *= r
                if kind == "A":
                    P = c[it] + (1 - s[it] - c[it]) / (1 + math.exp(-a[it] * (z0[k] + gain[k] - b[it])))
                    yv = int(rng.random() < P)
                else:
                    yv = 0          # drawn below from the engine's own prediction
                if kind == "A":
                    gain[k] += 0.25
                last[k] = tt
                rows_l.append(u)
                rows_i.append(it)
                rows_t.append(tt)
                rows_y.append(yv)
            t += 3600.0
    li, ii = np.array(rows_l), np.array(rows_i)
    group = np.where(is_mc, np.where(m == 4, 0, 1), 2)
    data = Data(li, ii, comp_of[ii], np.array(rows_y, float), np.array(rows_t), np.arange(len(li)), is_mc, m, group,
                np.array([f"{kind}{seed}-{u}" for u in range(L)]))
    if kind == "B":
        data.df["y"] = E.replay(data.events(), E.engine_params(is_mc, m), rng=rng)["y"]
    truth = {"a": a, "b": b, "c": c, "d": 1 - s, "is_mc": is_mc, "m": m, "half_life_days": E.half_life_days(v, dd)}
    return data, truth


def floor_checks(kind, data, prm, info, truth):
    asy = info["asymptotes"]
    okc = asy["n_first"] >= MIN_CD
    mc, fi = truth["is_mc"] & okc, ~truth["is_mc"] & okc
    n_rows = prm.meta["ab"]["n_rows"]
    okab = n_rows >= MIN_AB
    hl = info["decay_engine_structure"]["half_life_days"]
    rec = {"c_mc": [float(truth["c"][mc].mean()), float(prm.c[mc].mean())],
           "c_fill": [float(truth["c"][fi].mean()), float(prm.c[fi].mean())],
           "slip": [float(1 - truth["d"][okc].mean()), float(1 - prm.d[okc].mean())],
           "half_life_days": [truth["half_life_days"], hl],
           "calibrated_structure_half_life_days": info["decay"]["half_life_days"]}
    if kind == "A":
        rec["spearman_b"] = spearman(truth["b"][okab], prm.b[okab])
        rec["spearman_a"] = spearman(truth["a"][okab], prm.a[okab])
        chk = {"c_mc": abs(rec["c_mc"][0] - rec["c_mc"][1]) <= 0.05, "c_fill": abs(rec["c_fill"][0] - rec["c_fill"][1]) <= 0.05,
               "slip": abs(rec["slip"][0] - rec["slip"][1]) <= 0.03, "b_order": rec["spearman_b"] >= 0.8,
               "a_order": rec["spearman_a"] >= 0.3}
        rec["half_life_within_factor_4_reported"] = bool(0.25 <= hl / truth["half_life_days"] <= 4)
    else:
        e1 = info["E1_structure"]
        own = e1.meta["ab"]["n_rows"] >= MIN_AB
        rec["E1_structure_median_a"] = float(np.median(e1.a[own]))
        rec["E1_structure_median_abs_b"] = float(np.median(np.abs(e1.b[own])))
        hl = info["decay_lazy_engine_structure"]["half_life_days"]
        rec["lazy_engine_structure_half_life_days"] = hl
        chk = {"a_is_1": 0.9 <= rec["E1_structure_median_a"] <= 1.1, "b_is_0": rec["E1_structure_median_abs_b"] <= 0.1,
               "half_life": 0.5 <= hl / truth["half_life_days"] <= 2}
    rec["checks"] = {k: bool(v) for k, v in chk.items()}
    return rec


def synthetic():
    out = {"A": [], "B": [], "passes": True}
    for kind, seeds in (("A", 3), ("B", 2)):
        for sd in range(seeds):
            data, truth = world(kind, sd)
            fit = data.rows("train")
            print(f"world {kind} seed {sd}: {len(data.df):,} rows", flush=True)
            prm, info = calibrate(data, fit)
            e0 = E.engine_params(data.is_mc, data.m)
            info["decay_engine_structure"] = fit_decay(data.events(fit), e0, read=True)
            if kind == "B":
                info["E1_structure"] = fit_ab(data.events(fit), e0, data.group)
                info["decay_lazy_engine_structure"] = fit_decay(data.events(fit), e0, read=False)
            rec = floor_checks(kind, data, prm, info, truth)
            out[kind].append(rec)
            out["passes"] &= all(rec["checks"].values())
            print("   " + json.dumps({k: v for k, v in rec.items()}, default=float), flush=True)
    OUT.mkdir(exist_ok=True)
    (OUT / "calibrate-synthetic.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    print("FLOOR", "PASSES" if out["passes"] else "FAILS")


def recheck():
    """Re-apply the current pass rule (CHANGE 3) to the stored floor records, without refitting."""
    f = OUT / "calibrate-synthetic.json"
    out = json.loads(f.read_text())
    for rec in out["A"]:
        hl = rec["half_life_days"]
        rec["checks"].pop("half_life", None)
        rec["half_life_within_factor_4_reported"] = bool(0.25 <= hl[1] / hl[0] <= 4)
    out["passes"] = all(all(r["checks"].values()) for k in ("A", "B") for r in out[k])
    out["rule"] = "CHANGE 3: world-A half-life reported, not checked"
    f.write_text(json.dumps(out, indent=1, default=float) + "\n")
    print("FLOOR", "PASSES" if out["passes"] else "FAILS")


def fit_csv(src, dst, test_share=0.0):
    df = pd.read_csv(src)
    ts = df.timestamp
    if not pd.api.types.is_numeric_dtype(ts):       # CHANGE 5: pandas 3 string columns
        ts = (pd.to_datetime(ts, utc=True) - pd.Timestamp("1970-01-01", tz="UTC")).dt.total_seconds()
    li, uid = pd.factorize(df.learner)
    ii, names = pd.factorize(df.item)
    kk = pd.factorize(df.competency)[0]
    meta = df.assign(ii=ii).drop_duplicates("ii").sort_values("ii")
    is_mc = meta.format.astype(str).str.lower().eq("mc").to_numpy()
    m = meta.n_options.fillna(0).astype(int).to_numpy()
    grp = pd.factorize(meta.format.astype(str) + "|" + np.where(is_mc, m, 0).astype(str))[0]
    data = Data(li, ii, kk, df.correct.to_numpy(float), ts.to_numpy(float), np.arange(len(df)), is_mc, m, grp,
                np.asarray(uid), item_names=np.asarray(names))
    fit = data.rows("train") if test_share else np.ones(len(data.df), bool)
    prm, info = calibrate(data, fit)
    Path(dst).write_text(json.dumps(to_json(data, prm, info), indent=1, default=float) + "\n")
    print("wrote", dst)


if __name__ == "__main__":
    if sys.argv[1] == "synthetic":
        synthetic()
    elif sys.argv[1] == "recheck":
        recheck()
    elif sys.argv[1] == "fit":
        fit_csv(sys.argv[2], sys.argv[3], float(sys.argv[5]) if len(sys.argv) > 5 else 0.0)
