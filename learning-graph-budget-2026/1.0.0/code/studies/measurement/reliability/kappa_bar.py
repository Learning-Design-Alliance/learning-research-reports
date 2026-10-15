"""A calibrated bar: at what decision kappa does a graph-driven sequencing decision stop costing more
than it saves? (Paper 2 placeholder 3; Paper II; A5)

A5's gate is Spearman-Brown >= 0.80. Paper 2 section 7 says no study ever sized that bar against the
effect it protects; it is a convention [Nunnally 1978]. The board's A5 entry says the calibration "is
still outstanding and must not inherit 0.80 from the correlation gate". This sizes it.

THE DECISION, AND THE MACHINERY, ARE studies/end-to-end/xes3g5m-build/practice_value.py's. Before each
attempt a readiness model gives p; the learner is judged READY if p >= tau. A premature advance is
"judged ready, then wrong"; unneeded practice is "judged not ready, then right". tau is re-set for
every rule so premature advance is the same share of wrong answers (RISK 0.20 primary; 0.10, 0.30
reported). At matched risk, the difference in unneeded practice is what a rule saves, in items per
1,000 attempts. 200 learner resamples give the interval.

A GRAPH-DRIVEN SEQUENCING DECISION is the graph used as a rule, which is how a graph sequences:

  HARD (primary)   not ready for B while any asserted parent A is FAILED (attempted, not yet
                   passed) -- the cell the assay's drop is estimated on.
  HARD-NOTPASSED   not ready for B while any asserted parent is not yet passed, attempted or not
                   (a curriculum gate). Reported.
  SOFT             the count of FAILED asserted parents added to the readiness model as a fitted
                   feature. Reported: a fitted feature can be down-weighted, so it cannot cost
                   much; the hard rule is where a wrong edge costs practice.

against the same readiness model without a graph (practice_value's M1: item difficulty and the
learner's running accuracy). "Stops costing more than it saves" is items saved = 0.

WHY SIMULATION. Calibration needs the true graph, which no corpus has. So the curve is drawn in
planted worlds shaped like XES3G5M, where the assay is run exactly as on real data -- the drop,
cell floor 10, the adopted rule (assert when drop - 1.0 se > 0.10), split-half kappa between random
halves of the training learners -- and the graph it asserts is deployed as a sequencing rule on
held-out learners. The training sample is swept (500 ... 32,000 learners), which moves the assay's
kappa from low to high the way more learners do on real data (RAISE-KAPPA.md: +0.177 at 1,354 per
half to +0.500 at 9,033). Each sample gives one point (kappa, items saved). Then the real XES3G5M
graph is placed on the same axes.

PRE-REGISTERED 2026-10-05, committed before any items-saved figure is computed.

  worlds    60 items in a hidden order; a gate a -> b (a before b) planted with probability
            DENSITY in {0.02, 0.05, 0.10}, size U(0.05, 0.35); success p = logistic(mu + theta -
            beta_b) - sum of gates whose parent the learner does not hold; a learner holds A if
            they passed it earlier or held it on arrival (probability logistic(theta - beta_a)).
            Each learner attempts a random 60% of items in random order, 1-3 attempts each.
            Two seeds per density. 4,000 held-out learners per world.
  shape     theta sd and mu are tuned ONCE, at density 0.05, to XES3G5M's first-attempt accuracy
            and median ALL-lag drop (top 200 KCs, cell floor 10), from the grid below; nothing
            about items saved is read while tuning. beta sd 0.8.
  sweep     training learners N in {500, 1000, 2000, 4000, 8000, 16000, 32000}; split-half kappa,
            Spearman-Brown and their deranged arms on 6 splits (deranged: 2) of each N.
  controls  ORACLE graph (the planted gates; the most a graph can save in that world) and a
            RANDOM graph with as many edges as the estimated one (size-matched; no information).
  break-even  kappa0 = the split-half kappa at which HARD items saved crosses 0 from below,
            linear interpolation between sweep points; interval from the 200 bootstrap draws.
            Reported in kappa, in excess-over-deranged kappa and in Spearman-Brown (A5's unit).
  per world   BREAK-EVEN AT kappa0 [lo, hi]
              PAYS ACROSS THE SWEEP (kappa0 below the smallest kappa reached)
              NEVER PAYS IN THE SWEEP (oracle pays; every estimated graph costs)
              NO GRAPH PAYS (the oracle's own interval is below 0: a hard gate costs practice
                             even when every edge is true)
  the bar   over the worlds where a break-even exists, take the LARGEST kappa0 (the bar that
            makes a hard gate pay in every such world) with its interval, in SB units too:
              0.80 TOO STRICT   interval entirely below 0.80
              0.80 TOO LAX      interval entirely above 0.80
              0.80 CONSISTENT   interval contains 0.80
              NO BAR JUSTIFIES A HARD GATE   if any world returns NO GRAPH PAYS, said beside the
                             above, because then the answer depends on the world, not the bar.
  real      XES3G5M, top 200 KCs, e2e.py's learner split (sha256(uid) % 5 != 0 is TRAIN): graph
            asserted on TRAIN with the adopted rule, gate evaluated on TEST KC-rows at matched
            risk, its split-half kappa on TRAIN, beside a size-matched RANDOM graph.

  FLOOR (run first; if it fails nothing is read): at density 0.10, seed 1, the ORACLE hard gate
            saves items with its lower bound above 0, and the RANDOM graph at N = 32,000 does not
            (its upper bound <= the oracle's lower bound); kappa at N = 32,000 exceeds kappa at
            N = 500. If the oracle cannot be seen saving where gates are dense, a null from this
            instrument is not a finding.

WHAT IT ASSUMES, stated before the numbers: gates are subtractive and hold for every learner;
success needs no hidden second skill; edges do not interact (conjunctive attenuation is Paper II's
own result, so real gates are softer than these). The break-even is a property of these worlds;
the real XES3G5M point says where the real graph sits on the same axes.

CHANGES (each recorded before any items-saved figure was computed)
  1. 2026-10-05 tuning grid. The registered grid (theta sd 0.5-1.4, mu 0.5-1.5) did not bracket
     XES3G5M's first-attempt accuracy 0.763 (best 0.66); moved to sd 0.5-0.8, mu 1.5-2.5. Same
     loss, same targets (accuracy 0.763, median drop 0.102 at cell floor 10, top 200 KCs).
     Chosen: theta sd 0.8, mu 2.0 (accuracy 0.729, median drop 0.109, assert rate 0.37 vs 0.32).

FLOOR RESULT (2026-10-05): FAILS. At density 0.10, seed 1, the ORACLE hard gate COSTS practice:
-4.2 [-5.5, -3.0] items per 1,000 attempts. The estimated graph costs far more (-80.7 at N = 500,
-172.9 at N = 32,000; random graph of the same size -125.8 / -261.0); SOFT use is ~0 (-1.8, -0.1).
By the rule above, `sim` and `real` are not run and no break-even is read. Two things the floor run
shows anyway, reported as descriptive, not as verdicts:
  - at N = 32,000 the assay's split-half kappa is +0.646 (excess over deranged +0.646) and its
    Spearman-Brown +0.899 -- above A5's 0.80 -- while 2,507 of 3,540 pairs are asserted with
    precision 0.07 against the planted graph. The deranged arm does not remove LEARNER-ABILITY
    exposure (crossing learners destroys it along with the dependency), so a graph made almost
    entirely of ability-driven false edges is highly reliable.
  - in this world shape, a hard gate does not pay even when every edge is true.
CHANGE 2 (post hoc, labelled): `diagnostic` re-runs the floor world with gates U(0.5, 0.8) to see
whether the machinery can register a gate's value at all, and adds a LATENT-STATE gate (block exactly
the attempts where the learner truly lacks a true parent, penalty >= 0.25), which no observable rule
can know. Result: latent gate +39.0 [+36.5, +41.3] items per 1,000 (blocks 62%); ORACLE observable
hard gate still -4.8 [-5.7, -3.9]; estimated graph -163.1 at kappa +0.719 / SB +0.937 (precision
0.07). So the machinery sees a gate's value; what fails is the OBSERVABLE rule: "attempted A and not
yet passed" is a poor proxy for "lacks A" when learners arrive holding things and pass on retries.
No graph accuracy makes that rule pay in these worlds, so no kappa bar can be sized from it.

DATA. XES3G5M (licence unstated; research use, non-redistributable) through shared.paths `XES_DIR`.
Only aggregates are written to out/.

    python3 kappa_bar.py tune      # the shape targets and the tuned theta sd / mu (no items saved)
    python3 kappa_bar.py floor
    python3 kappa_bar.py sim
    python3 kappa_bar.py real
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pairgrid as pg  # noqa: E402

sys.path.insert(0, str(HERE.parents[2]))
from shared.stats import kappa, spearman  # noqa: E402

SEED = 20261006
K_ITEMS = 60
SUBSET = 0.6
BETA_SD = 0.8
DENSITIES = (0.02, 0.05, 0.10)
SEEDS = (1, 2)
NS = (500, 1000, 2000, 4000, 8000, 16000, 32000)
N_TEST = 4000
SPLITS, DER_SPLITS = 6, 2
MIN_CELL, BAR, Z = 10, 0.10, 1.0
RISKS = (0.20, 0.10, 0.30)
BOOT = 200
XES_TOP = 200
OUT = HERE / "out"
TUNE_FILE = OUT / "kappa_bar_tune.json"
#: CHANGE 1 (2026-10-05, before any items-saved figure): the registered grid sd {0.5, 0.8, 1.1, 1.4} x
#: mu {0.5, 1.0, 1.5} did not bracket XES3G5M (best: accuracy 0.66 vs 0.76, drop 0.135 vs 0.102); the
#: grid is moved to bracket it. Same loss, same targets, same single tuning world.
TUNE_SD = (0.5, 0.6, 0.7, 0.8)
TUNE_MU = (1.5, 2.0, 2.5)


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


# ---------------------------------------------------------------- world

class World:
    def __init__(self, density, seed, theta_sd, mu, gate_range=(0.05, 0.35)):
        rng = np.random.default_rng([seed, int(density * 1000)])
        self.K = K_ITEMS
        self.beta = rng.normal(0, BETA_SD, self.K)
        G = np.zeros((self.K, self.K))
        for a in range(self.K):
            for b in range(a + 1, self.K):
                if rng.random() < density:
                    G[a, b] = rng.uniform(*gate_range)
        self.G = G
        self.theta_sd, self.mu = theta_sd, mu
        self.rng = rng

    def learners(self, n):
        """Simulate n learners; returns FT, FP, Y (first-touch outcome) and the attempt table."""
        rng, K = self.rng, self.K
        theta = rng.normal(0, self.theta_sd, n)
        prior = rng.random((n, K)) < sigmoid(theta[:, None] - self.beta[None, :])
        held = prior.copy()
        m = int(round(SUBSET * K))
        order = np.argsort(rng.random((n, K)), axis=1)[:, :m]
        reps = rng.integers(1, 4, (n, m))
        FT = np.full((n, K), np.inf)
        FP = np.full((n, K), np.inf)
        Y = np.zeros((n, K), np.float32)
        t = np.zeros(n)
        rows_l, rows_i, rows_t, rows_y, rows_p = [], [], [], [], []
        GT = self.G.T
        ar = np.arange(n)
        for j in range(m):
            b = order[:, j]
            for r in range(3):
                act = reps[:, j] > r
                if not act.any():
                    continue
                L = ar[act]
                bb = b[act]
                pen = (GT[bb] * (~held[L])).sum(1)
                p = np.clip(sigmoid(self.mu + theta[L] - self.beta[bb]) - pen, 0.02, 0.98)
                y = rng.random(len(L)) < p
                tt = t[L]
                first = ~np.isfinite(FT[L, bb])
                FT[L[first], bb[first]] = tt[first]
                Y[L[first], bb[first]] = y[first]
                newpass = y & ~np.isfinite(FP[L, bb])
                FP[L[newpass], bb[newpass]] = tt[newpass]
                held[L[y], bb[y]] = True
                rows_l.append(L); rows_i.append(bb); rows_t.append(tt); rows_y.append(y); rows_p.append(pen)
                t[L] += 1
        att = dict(l=np.concatenate(rows_l), i=np.concatenate(rows_i), t=np.concatenate(rows_t),
                   y=np.concatenate(rows_y).astype(np.int8), pen=np.concatenate(rows_p))
        return FT, FP, Y, att


# ---------------------------------------------------------------- assay

def cells_all(FT, FP, Y, groups):
    """ALL-lag cells for every pair, per group: (G, K_A, K_B)."""
    K = FT.shape[1]
    res = [pg.column_cells(FT, FP, Y, b, groups, bands=("ALL",), lag_scale=1.0)["ALL"] for b in range(K)]
    return {s: np.stack([r[s] for r in res], axis=2) for s in ("nm", "sm", "nf", "sf")}


def assert_graph(c, g=0):
    d, se, ok = pg.drops({k: v[g] for k, v in c.items()}, MIN_CELL)
    A = ok & np.isfinite(se) & ((d - Z * se) > BAR)
    np.fill_diagonal(A, False)
    return A, d, ok


def split_reliability(FT, FP, Y, rng, splits=SPLITS, der_splits=DER_SPLITS, start=None):
    """Mean split-half kappa (adopted rule), Spearman-Brown, and both on a deranged arm."""
    n = FT.shape[0]
    G = np.zeros((n, 2 * splits), np.float32)
    for s in range(splits):
        perm = rng.permutation(n)
        G[perm[: n // 2], 2 * s] = 1
        G[perm[n // 2:], 2 * s + 1] = 1
    c = cells_all(FT, FP, Y, G)

    def agree(c, g1, g2):
        d1, s1, ok1 = pg.drops({k: v[g1] for k, v in c.items()}, MIN_CELL)
        d2, s2, ok2 = pg.drops({k: v[g2] for k, v in c.items()}, MIN_CELL)
        both = ok1 & ok2 & np.isfinite(s1) & np.isfinite(s2)
        np.fill_diagonal(both, False)
        if both.sum() < 30:
            return float("nan"), float("nan"), int(both.sum())
        a1 = (d1[both] - Z * s1[both]) > BAR
        a2 = (d2[both] - Z * s2[both]) > BAR
        return kappa(a1, a2), spearman(d1[both], d2[both]), int(both.sum())

    ks, rs, ns = zip(*[agree(c, 2 * s, 2 * s + 1) for s in range(splits)])
    dks, drs = [], []
    for _ in range(der_splits):
        perm = rng.permutation(n)
        h1, h2 = perm[: n // 2], perm[n // 2:]
        donor = pg.derangement(n, rng, blocks=[h1, h2])
        g2 = np.zeros((n, 2), np.float32)
        g2[h1, 0] = 1
        g2[h2, 1] = 1
        K = FT.shape[1]
        res = [pg.column_cells(FT, FP, Y, b, g2, bands=("ALL",), lag_scale=1.0, donor=donor,
                               start=start)["ALL"] for b in range(K)]
        cd = {s: np.stack([r[s] for r in res], axis=2) for s in ("nm", "sm", "nf", "sf")}
        k, r, _ = agree(cd, 0, 1)
        dks.append(k)
        drs.append(r)
    r = float(np.nanmean(rs))
    dr = float(np.nanmean(drs))
    sbf = lambda x: 2 * x / (1 + x) if np.isfinite(x) and x > -1 else float("nan")
    return dict(kappa=float(np.nanmean(ks)), sb=sbf(r), pairs=int(np.median(ns)),
                deranged_kappa=float(np.nanmean(dks)), deranged_sb=sbf(dr),
                excess_kappa=float(np.nanmean(ks)) - float(np.nanmean(dks)))


# ---------------------------------------------------------------- readiness

def fit_logistic(X, y, iters=25):
    X = np.column_stack([np.ones(len(X)), X])
    w = np.zeros(X.shape[1])
    for _ in range(iters):
        p = sigmoid(X @ w)
        g = X.T @ (y - p)
        H = (X * (p * (1 - p))[:, None]).T @ X + 1e-6 * np.eye(X.shape[1])
        w += np.linalg.solve(H, g)
    return w


def predict(w, X):
    return sigmoid(np.column_stack([np.ones(len(X)), X]) @ w)


def running_logit(l, y):
    """Logit of each learner's running accuracy BEFORE each attempt (rows in time order per learner)."""
    order = np.lexsort((np.arange(len(l)), l))
    ls, ys = l[order], y[order].astype(float)
    start = np.r_[True, ls[1:] != ls[:-1]]
    grp = np.cumsum(start) - 1
    csum = np.cumsum(ys)
    first_idx = np.nonzero(start)[0]
    before = csum - ys - (csum[first_idx] - ys[first_idx])[grp]
    cnt = np.arange(len(ls)) - first_idx[grp]
    out = np.empty(len(l))
    out[order] = np.log((before + 1) / (cnt - before + 1))
    return out


def failed_parents(A, FT, FP, l, i, t, mode="failed"):
    """Per attempt: number of asserted parents of item i that are FAILED (or not passed) at t."""
    out = np.zeros(len(l))
    for b in np.unique(i):
        rows = np.nonzero(i == b)[0]
        par = np.nonzero(A[:, b])[0]
        if len(par) == 0:
            continue
        tt = t[rows][:, None]
        ft = FT[l[rows]][:, par]
        fp = FP[l[rows]][:, par]
        if mode == "failed":
            bad = (ft < tt) & ~(fp < tt)
        else:
            bad = ~(fp < tt)
        out[rows] = bad.sum(1)
    return out


def unneeded(p, y, risk, blocked=None):
    """Share of correct attempts judged not ready, with tau set so `risk` of wrong attempts are
    judged ready. Blocked attempts are never ready. practice_value.unneeded, plus the block."""
    if blocked is None:
        blocked = np.zeros(len(p), bool)
    wrong_open = np.sort(p[(y == 0) & ~blocked])[::-1]
    allow = int(np.floor(risk * int((y == 0).sum())))
    if allow >= len(wrong_open):
        tau = -np.inf
    elif allow == 0:
        tau = np.inf
    else:
        tau = wrong_open[allow - 1]
    ready = (~blocked) & (p >= tau)
    return float((~ready[y == 1]).mean())


def saved(p_base, p_rule, y, risk, blocked, learner, rng, boot=BOOT):
    """Items saved per 1,000 attempts by (p_rule, blocked) over p_base, with a learner bootstrap."""
    sc = float(y.mean())
    point = (unneeded(p_base, y, risk) - unneeded(p_rule, y, risk, blocked)) * sc * 1000
    ul, inv = np.unique(learner, return_inverse=True)
    nl = len(ul)
    draws = []
    for _ in range(boot):
        w = np.bincount(rng.integers(0, nl, nl), minlength=nl)
        rep = np.repeat(np.arange(len(y)), w[inv])
        draws.append((unneeded(p_base[rep], y[rep], risk) - unneeded(p_rule[rep], y[rep], risk, blocked[rep]))
                     * float(y[rep].mean()) * 1000)
    return point, np.array(draws)


def evaluate(graphs, FT, FP, att, base_model, rng, risks=RISKS):
    """For each named graph: HARD, HARD-NOTPASSED and SOFT items saved over the no-graph model."""
    l, i, t, y = att["l"], att["i"], att["t"], att["y"]
    Xb, wb, soft_fit = base_model
    p0 = predict(wb, Xb)
    res = {}
    for name, A in graphs.items():
        fpar = failed_parents(A, FT, FP, l, i, t, "failed")
        npar = failed_parents(A, FT, FP, l, i, t, "notpassed")
        ws = soft_fit(A)
        ps = predict(ws, np.column_stack([Xb, fpar]))
        r = dict(edges=int(A.sum()), blocked_share=float((fpar > 0).mean()),
                 blocked_share_notpassed=float((npar > 0).mean()))
        for risk in risks:
            for rule, prule, blk in (("hard", p0, fpar > 0), ("hard_notpassed", p0, npar > 0),
                                     ("soft", ps, np.zeros(len(y), bool))):
                main = risk == 0.20 and rule == "hard"
                pt, dr = saved(p0, prule, y, risk, blk, l, rng, boot=BOOT if main else 30)
                r[f"{rule}@{risk}"] = dict(saved=pt, lo=float(np.percentile(dr, 2.5)),
                                           hi=float(np.percentile(dr, 97.5)),
                                           draws=dr.tolist() if (risk == 0.20 and rule == "hard") else None)
        res[name] = r
    return res


def base_model_factory(FT_tr, FP_tr, att_tr, att_te, n_items):
    """practice_value's M1 (item difficulty offset + running accuracy) fitted on TRAIN attempts;
    soft_fit(A) refits it with the failed-parent count as a third feature."""
    acc = np.bincount(att_tr["i"], weights=att_tr["y"], minlength=n_items) + 1
    cnt = np.bincount(att_tr["i"], minlength=n_items) + 2
    off = np.log(acc / (cnt - acc))
    Xtr = np.column_stack([off[att_tr["i"]], running_logit(att_tr["l"], att_tr["y"])])
    Xte = np.column_stack([off[att_te["i"]], running_logit(att_te["l"], att_te["y"])])
    ytr = att_tr["y"].astype(float)
    sub = np.random.default_rng(0).choice(len(ytr), min(len(ytr), 400_000), replace=False)
    w = fit_logistic(Xtr[sub], ytr[sub])

    def soft_fit(A):
        f = failed_parents(A, FT_tr, FP_tr, att_tr["l"][sub], att_tr["i"][sub], att_tr["t"][sub], "failed")
        return fit_logistic(np.column_stack([Xtr[sub], f]), ytr[sub])

    return Xte, w, soft_fit


def random_graph(n_edges, K, rng):
    A = np.zeros((K, K), bool)
    off = np.array([(a, b) for a in range(K) for b in range(K) if a != b])
    pick = off[rng.choice(len(off), min(n_edges, len(off)), replace=False)]
    A[pick[:, 0], pick[:, 1]] = True
    return A


def breakeven(points, key="kappa"):
    """kappa0: first crossing of items saved from <= 0 to > 0 along increasing kappa."""
    pts = sorted(points, key=lambda p: p[key])
    xs = [p[key] for p in pts]
    ys = [p["hard@0.2"]["saved"] for p in pts]
    draws = np.array([p["hard@0.2"]["draws"] for p in pts])  # (n_points, BOOT)

    def cross(yv):
        if yv[0] > 0:
            return -np.inf
        for j in range(1, len(yv)):
            if yv[j - 1] <= 0 < yv[j]:
                return xs[j - 1] + (xs[j] - xs[j - 1]) * (0 - yv[j - 1]) / (yv[j] - yv[j - 1])
        return np.inf

    k0 = cross(ys)
    bs = np.array([cross(draws[:, b]) for b in range(draws.shape[1])])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return float(k0), float(lo), float(hi), xs, ys


# ---------------------------------------------------------------- modes

def xes_grid():
    import atlas
    grid = pg.Grid(atlas.xes3g5m_rows())
    return grid.subset(grid.top_items(XES_TOP))


def shape_stats(FT, FP, Y):
    touched = np.isfinite(FT)
    acc = float(Y[touched].mean())
    c = cells_all(FT, FP, Y, np.ones((FT.shape[0], 1), np.float32))
    A, d, ok = assert_graph(c)
    np.fill_diagonal(ok, False)
    return dict(first_attempt_accuracy=acc, median_drop=float(np.nanmedian(d[ok])), readable=float(ok.mean()),
                assert_rate=float(A[ok].mean()))


def run_tune():
    grid = xes_grid()
    target = shape_stats(grid.FT, grid.FP, grid.Y)
    print("XES3G5M target (top 200 KCs, all learners):", target, flush=True)
    best = None
    rows = []
    for sd in TUNE_SD:
        for mu in TUNE_MU:
            w = World(0.05, 99, sd, mu)
            FT, FP, Y, _ = w.learners(18000)
            st = shape_stats(FT, FP, Y)
            loss = ((st["first_attempt_accuracy"] - target["first_attempt_accuracy"]) / 0.05) ** 2 + \
                   ((st["median_drop"] - target["median_drop"]) / 0.02) ** 2
            rows.append(dict(theta_sd=sd, mu=mu, loss=loss, **st))
            print(f"  theta sd {sd} mu {mu}: {st} loss {loss:.2f}", flush=True)
            if best is None or loss < best["loss"]:
                best = rows[-1]
    OUT.mkdir(exist_ok=True)
    TUNE_FILE.write_text(json.dumps(dict(target=target, grid=rows, chosen=best), indent=1) + "\n")
    print("chosen:", best)


def tuned():
    t = json.loads(TUNE_FILE.read_text())["chosen"]
    return t["theta_sd"], t["mu"]


def run_world(density, seed, ns=NS, verbose=True, gate_range=(0.05, 0.35)):
    sd, mu = tuned()
    w = World(density, seed, sd, mu, gate_range)
    rng = np.random.default_rng([SEED, seed, int(density * 1000)])
    FTp, FPp, Yp, attp = w.learners(max(ns))
    FTt, FPt, Ytt, attt = w.learners(N_TEST)
    oracle = w.G > 0
    pts = []
    for n in ns:
        keep = attp["l"] < n
        att_tr = {k: v[keep] for k, v in attp.items()}
        FT, FP, Y = FTp[:n], FPp[:n], Yp[:n]
        rel = split_reliability(FT, FP, Y, rng, start=np.zeros(n))
        A, _, _ = assert_graph(cells_all(FT, FP, Y, np.ones((n, 1), np.float32)))
        tp = int((A & oracle).sum())
        base = base_model_factory(FT, FP, att_tr, attt, w.K)
        graphs = {"estimated": A, "random": random_graph(int(A.sum()), w.K, rng)}
        if n == max(ns):
            graphs["oracle"] = oracle
        ev = evaluate(graphs, FTt, FPt, attt, base, rng)
        latent = None
        if n == max(ns):
            # machinery check: block exactly the attempts where the learner truly lacks a true parent
            # (latent penalty >= 0.25), which no observable rule can know
            p0 = predict(base[1], base[0])
            lp, ld = saved(p0, p0, attt["y"], 0.20, attt["pen"] >= 0.25, attt["l"], rng, boot=50)
            latent = dict(saved=lp, lo=float(np.percentile(ld, 2.5)), hi=float(np.percentile(ld, 97.5)),
                          blocked_share=float((attt["pen"] >= 0.25).mean()))
            print(f"  latent-state gate (pen >= 0.25): saved {lp:+.1f} [{latent['lo']:+.1f}, {latent['hi']:+.1f}], "
                  f"blocks {latent['blocked_share']:.1%}", flush=True)
        pt = dict(latent_gate=latent, n=n, **rel, edges=int(A.sum()), true_edges=int(oracle.sum()),
                  precision=tp / max(int(A.sum()), 1), recall=tp / max(int(oracle.sum()), 1),
                  **{k: v for k, v in ev["estimated"].items() if k != "edges"}, random=ev["random"],
                  oracle=ev.get("oracle"))
        pts.append(pt)
        if verbose:
            h = pt["hard@0.2"]
            print(f"  density {density} seed {seed} N {n:6,d}: kappa {rel['kappa']:+.3f} (excess "
                  f"{rel['excess_kappa']:+.3f}) SB {rel['sb']:+.3f} | edges {pt['edges']} prec {pt['precision']:.2f} "
                  f"rec {pt['recall']:.2f} | HARD saved {h['saved']:+.1f} [{h['lo']:+.1f}, {h['hi']:+.1f}] "
                  f"random {pt['random']['hard@0.2']['saved']:+.1f} soft {pt['soft@0.2']['saved']:+.1f}"
                  + (f" | ORACLE {pt['oracle']['hard@0.2']['saved']:+.1f} [{pt['oracle']['hard@0.2']['lo']:+.1f}, "
                     f"{pt['oracle']['hard@0.2']['hi']:+.1f}]" if pt["oracle"] else ""), flush=True)
    return pts


def strip(pts):
    for p in pts:
        for k in list(p):
            if isinstance(p[k], dict) and "draws" in p[k]:
                p[k] = {kk: vv for kk, vv in p[k].items() if kk != "draws"}
        for sub in ("random", "oracle"):
            if p.get(sub):
                for k in list(p[sub]):
                    if isinstance(p[sub][k], dict):
                        p[sub][k].pop("draws", None)
    return pts


def run_floor():
    pts = run_world(0.10, 1, ns=(500, 32000))
    big = pts[-1]
    o = big["oracle"]["hard@0.2"]
    r = big["random"]["hard@0.2"]
    ok = (o["lo"] > 0) and (r["hi"] <= o["lo"]) and (big["kappa"] > pts[0]["kappa"])
    print(f"FLOOR {'PASSES' if ok else 'FAILS'}: oracle {o['saved']:+.1f} [{o['lo']:+.1f}, {o['hi']:+.1f}], "
          f"random {r['saved']:+.1f} [{r['lo']:+.1f}, {r['hi']:+.1f}], kappa {pts[0]['kappa']:+.3f} -> {big['kappa']:+.3f}")
    OUT.mkdir(exist_ok=True)
    (OUT / "kappa_bar_floor.json").write_text(json.dumps(dict(passes=bool(ok), points=strip(pts)), indent=1,
                                                         default=float) + "\n")
    return ok


def run_diagnostic():
    """CHANGE 2 (post hoc; labelled): is the floor failure the machinery or the world? Same world
    shape, density 0.10, seed 1, but gates U(0.5, 0.8): if the oracle hard gate saves practice here,
    the machinery can see a gate's value and the registered floor failed because gates of the
    registered size do not pay as hard blocks."""
    pts = run_world(0.10, 1, ns=(32000,), gate_range=(0.5, 0.8))
    o = pts[-1]["oracle"]["hard@0.2"]
    print(f"DIAGNOSTIC: oracle with gates U(0.5, 0.8) saves {o['saved']:+.1f} [{o['lo']:+.1f}, {o['hi']:+.1f}]")
    (OUT / "kappa_bar_diagnostic.json").write_text(json.dumps(dict(post_hoc=True, gate_range=[0.5, 0.8],
                                                                   points=strip(pts)), indent=1, default=float) + "\n")


def world_verdict(pts):
    k0, lo, hi, xs, ys = breakeven(pts, "kappa")
    o = pts[-1]["oracle"]["hard@0.2"]
    if o["hi"] < 0:
        v = "NO GRAPH PAYS"
    elif k0 == -np.inf:
        v = "PAYS ACROSS THE SWEEP"
    elif k0 == np.inf:
        v = "NEVER PAYS IN THE SWEEP"
    else:
        v = "BREAK-EVEN"
    # same crossing in SB and excess-kappa units
    sbk = breakeven(pts, "sb")
    exk = breakeven(pts, "excess_kappa")
    return dict(verdict=v, kappa0=[k0, lo, hi], sb0=list(sbk[:3]), excess_kappa0=list(exk[:3]),
                oracle_hard=o)


def run_sim():
    if not json.loads((OUT / "kappa_bar_floor.json").read_text()).get("passes"):
        raise SystemExit("floor has not passed; nothing is read")
    worlds = {}
    for dens in DENSITIES:
        for seed in SEEDS:
            pts = run_world(dens, seed)
            v = world_verdict(pts)
            print(f"  => density {dens} seed {seed}: {v['verdict']} kappa0 {v['kappa0']} SB0 {v['sb0']}", flush=True)
            worlds[f"{dens}/{seed}"] = dict(density=dens, seed=seed, points=strip(pts), **v)
            (OUT / "kappa_bar.json").write_text(json.dumps(dict(worlds=worlds), indent=1, default=float) + "\n")
    finite = [w for w in worlds.values() if w["verdict"] == "BREAK-EVEN"]
    nopay = [k for k, w in worlds.items() if w["verdict"] == "NO GRAPH PAYS"]
    bar = None
    if finite:
        top = max(finite, key=lambda w: w["kappa0"][0])
        bar = dict(world=f"{top['density']}/{top['seed']}", kappa0=top["kappa0"], sb0=top["sb0"],
                   excess_kappa0=top["excess_kappa0"])
        lo, hi = top["sb0"][1], top["sb0"][2]
        judge = ("0.80 TOO STRICT" if hi < 0.80 else "0.80 TOO LAX" if lo > 0.80 else "0.80 CONSISTENT")
    else:
        judge = "NO FINITE BREAK-EVEN IN ANY WORLD"
    if nopay:
        judge += f"; NO BAR JUSTIFIES A HARD GATE in {nopay}"
    print(f"\nBAR: {bar}\nVERDICT ON A5's 0.80: {judge}")
    (OUT / "kappa_bar.json").write_text(json.dumps(dict(worlds=worlds, bar=bar, verdict=judge), indent=1,
                                                   default=float) + "\n")


def run_real():
    import atlas
    grid = xes_grid()
    cols = {it: j for j, it in enumerate(grid.items)}
    lrow = {u: r for r, u in enumerate(grid.learners)}
    train_l = np.array([int(hashlib.sha256(u.encode()).hexdigest()[:8], 16) % 5 != 0 for u in grid.learners])
    ls, is_, ts, ys = [], [], [], []
    for u, it, ok, t, _h1, _h2 in atlas.xes3g5m_rows():
        j = cols.get(it)
        if j is None:
            continue
        ls.append(lrow[u]); is_.append(j); ts.append(float(t) / 1000.0 if float(t) > 1e11 else float(t)); ys.append(ok)
    att = dict(l=np.array(ls), i=np.array(is_), t=np.array(ts), y=np.array(ys, np.int8))
    order = np.lexsort((att["t"], att["l"]))
    att = {k: v[order] for k, v in att.items()}
    tr_rows = train_l[att["l"]]
    att_tr = {k: v[tr_rows] for k, v in att.items()}
    att_te = {k: v[~tr_rows] for k, v in att.items()}
    rng = np.random.default_rng(SEED)
    tr = np.nonzero(train_l)[0]
    FTtr, FPtr, Ytr = grid.FT[tr], grid.FP[tr], grid.Y[tr]
    rel = split_reliability(FTtr, FPtr, Ytr, rng, start=grid.start[tr])
    A, _, _ = assert_graph(cells_all(FTtr, FPtr, Ytr, np.ones((len(tr), 1), np.float32)))
    # TRAIN attempts are indexed by full-grid learner rows; FT/FP passed in full so rows line up
    base = base_model_factory(grid.FT, grid.FP, att_tr, att_te, grid.shape[1])
    ev = evaluate({"xes3g5m": A, "random": random_graph(int(A.sum()), grid.shape[1], rng)},
                  grid.FT, grid.FP, att_te, base, rng)
    for g in ev.values():
        for k in g:
            if isinstance(g[k], dict):
                g[k].pop("draws", None)
    out = dict(train_learners=int(train_l.sum()), test_learners=int((~train_l).sum()), items=grid.shape[1],
               test_attempts=int(len(att_te["y"])), reliability=rel, edges=int(A.sum()), evaluation=ev)
    h, r = ev["xes3g5m"]["hard@0.2"], ev["random"]["hard@0.2"]
    print(f"XES3G5M: kappa {rel['kappa']:+.3f} (deranged {rel['deranged_kappa']:+.3f}) SB {rel['sb']:+.3f}; "
          f"{A.sum()} edges; HARD saved {h['saved']:+.1f} [{h['lo']:+.1f}, {h['hi']:+.1f}] per 1,000; "
          f"random {r['saved']:+.1f} [{r['lo']:+.1f}, {r['hi']:+.1f}]; soft {ev['xes3g5m']['soft@0.2']['saved']:+.1f}")
    (OUT / "kappa_bar_real.json").write_text(json.dumps(out, indent=1, default=float) + "\n")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "floor"
    {"tune": run_tune, "floor": lambda: sys.exit(0 if run_floor() else 1), "sim": run_sim, "real": run_real,
     "diagnostic": run_diagnostic}[mode]()
