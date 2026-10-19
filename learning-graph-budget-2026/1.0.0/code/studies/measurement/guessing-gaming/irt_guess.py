"""PRE-REGISTERED: how much of a single answer is a lucky guess or a slip? (G1)

variance.py (studies/measurement/variance-sources/) left 54-60% of single-answer variance
unexplained. Guessing and slipping are two named parts of that residual. The four-parameter logistic
item model (4PL; Barton & Lord 1981) makes both explicit:

    P(correct) = c + (d - c) P*,   P* = sigmoid(a (theta - b))

c is the lower asymptote (a learner far below the item still succeeds with probability c: guessing),
1 - d = s the upper one (a learner far above it still fails with probability s: slipping). The 3PL
fixes s = 0, the 2PL also c = 0. Read as a latent-state model: with probability P* the learner can
do the item; if so she answers correctly with probability d, if not with probability c. Written
2026-09-27; no statistic below has been computed on real data.

DATA (raw data never enters the repo; only aggregates are written to out/)
  Eedi NeurIPS 2020 tasks 1-2 through shared.paths.data_path("EEDI_ANSWERS") (the slim TSV:
    UserId, QuestionId, IsCorrect; train plus both task-1 test splits). Every question has 4 options.
    One answer per (learner, question), the latest. Learners with sha256("g1" + UserId) first 8 hex
    digits mod 3 == 0 (about a third), to keep memory under 3 GB.
  XES3G5M through data_path("XES_DIR"): attempts.tsv (uid, question, concepts, correct, epoch ms)
    and XES3G5M/metadata/questions.json (type: 单选 = multiple choice, 填空 = fill-in; the number
    of options k = len(options)). Only each learner's FIRST attempt at each question is used (local
    independence; later attempts follow feedback). All learners.

MODEL AND ESTIMATION. Joint maximum a posteriori over learner abilities and item parameters, one
  L-BFGS problem per fit, gradients accumulated with np.bincount (no per-item loops). Priors:
    theta ~ N(0, 1)  (fixes the scale);  b ~ N(0, 2^2);  log a ~ N(0, 0.6^2);
    c = 0.5 u, u ~ Beta(1.2, 4);  s = 1 - d = 0.5 v, v ~ Beta(1.2, 4).
  So c and s live in (0, 0.5), with prior mean 0.115 and mode 0.03: the same prior for every item
  in every format, so any difference between formats comes from the data. 2PL is fitted first from
  logit starts; 3PL and 4PL start from it. Fit set: 80% of answers (numpy default_rng(SEED) uniform
  < 0.8); the other 20% are held out.

OUTPUTS PER CORPUS (4PL unless stated; items reported only with >= 150 fit answers)
  1. c and s distributions by format (Eedi: all 4-option MC; XES: MC by k, and fill-in): mean,
     median, 10/25/75/90th percentiles, share of items with c > 0.15; median with a 95% item
     bootstrap (1,000 draws). Mean c by k against 1/k.
  2. GUESS SHARE OF CORRECT ANSWERS: sum over correct answers of c (1 - P*) / P, divided by the
     number of correct answers (posterior probability that a correct answer was a guess). Also the
     expected form sum c (1 - P*) / sum P.
  3. SLIP SHARE OF INCORRECT ANSWERS: sum over incorrect answers of s P* / (1 - P), over their count.
  4. VARIANCE. Per answer P (1 - P) = P* d (1 - d) [slip noise] + (1 - P*) c (1 - c) [guess noise]
     + P* (1 - P*) (d - c)^2 [knowledge-state noise]; total answer variance Pbar (1 - Pbar) =
     var(P) [explained by learner and item] + mean P (1 - P). Reported: guess and slip noise as
     shares of the total and of the unexplained part mean P (1 - P). This is the observed 0/1
     scale; variance.py's 54-60% is on the latent logit scale, so the two are compared as shares of
     "unexplained", not number for number.
  Intervals: 95% learner-cluster Poisson bootstrap (400 draws) of 2-4 holding the fitted parameters
  fixed; parameter uncertainty is shown by refitting 4PL on each half of learners (hash parity) and by
  two alternative priors on u and v: Beta(1, 1) (flat) and Beta(5, 5) (centred on c = 0.25).
  5. Held-out log loss per answer of 2PL, 3PL, 4PL on the 20%.

VERDICTS (decided in advance)
  V1 IDENTIFICATION (XES3G5M, where both formats exist): IDENTIFIED if the median c of 4-option MC
     items exceeds that of fill-in items by more than 0.05 with the 95% bootstrap interval of the
     difference above 0, and the fill-in median c is below 0.05; NOT IDENTIFIED otherwise. (If MC
     and fill-in come out alike, c is not separating guessing from content and verdicts V2-V3 are
     read as model quantities, not guessing.)
  V2 FLOOR LEVEL (Eedi; XES 4-option MC): median c AT CHANCE if within 0.15-0.35 (1/k = 0.25 +/- 0.10);
     BELOW CHANCE if < 0.15 (distractors draw weak learners away from the key); ABOVE CHANCE if > 0.35.
  V3 SIZE (per corpus): guess share of correct answers SMALL < 0.05, MODERATE 0.05-0.15, LARGE > 0.15
     (point estimate); the same bands for the slip share of incorrect answers.
  V4 AGAINST THE ROUGH BOUND (Eedi): guess noise as a share of total answer variance, against the
     synthesis's rough bound of about 0.24: BELOW THE BOUND if the interval's upper end < 0.24; AT
     THE BOUND if it covers 0.24; ABOVE if its lower end > 0.24.
  V5 MODEL (per corpus): 4PL FITS BETTER if its held-out log loss is at least 0.001 nats per answer
     below the 2PL's; NO GAIN otherwise. 3PL reported alongside.

CONTROLS. Fill-in items are the negative control for guessing (a guess at a free number is almost
  never right); 1/k for the MC items is the reference. 2PL (c = s = 0) is the model without either
  asymptote.

SYNTHETIC FLOOR (before any real statistic): 3 seeds of a sparse world shaped like the real ones:
  6,000 learners, 400 items (half "MC" with c ~ U(0.15, 0.35), half "fill-in" with c = 0.01),
  s ~ U(0, 0.15), a ~ logN(0.2, 0.3), b ~ N(0, 1), theta ~ N(0, 1), each learner answering 60 items
  drawn with lognormal item popularity (so exposure is uneven). Truth: the same functionals as
  outputs 2-4 evaluated at the planted parameters. PASS (all 3 seeds) requires: mean estimated c on
  MC items and on fill-in items (>= 150 answers) each within 0.04 of planted; guess share of correct
  and slip share of incorrect each within 0.03 of truth; guess and slip noise shares of total
  variance within 0.02. A null world (c = s = 0 for every item) must give guess share of correct
  < 0.04 and slip share of incorrect < 0.04. Otherwise every verdict is UNCALIBRATED. Per-item
  Spearman of estimated against planted c is reported.

LIMITS stated in advance: a static ability ignores learning between answers (XES answers span
  months; Eedi keeps only the latest answer, biased toward correct); c and s are weakly identified
  for items few weak (strong) learners meet, where the prior carries them; Eedi's distractors are
  written to attract misconceptions, so c there is "success among those who cannot do it", which can
  sit below 1/k without meaning no guessing; guessing and slipping are the 4PL's reading of the
  asymptotes -- any process that keeps weak learners above zero (partial knowledge, elimination of
  options) counts as "guess" here.

DIRECTION: symmetric -- no edge enters.

CHANGES (after the first synthetic floor, before any real statistic)
  1. The first floor FAILED in 3 of 3 seeds with the joint MAP estimator. Planted MC c averaged 0.24-0.25
     and came back 0.06-0.07; the guess share of correct answers came back 0.048-0.056 for a true
     0.110-0.129; guess and slip noise shares were halved. Fill-in c (0.02 for 0.01), the slip share of
     incorrect answers (within 0.03) and the null world (0.02 for 0) passed. Reason: with about 60 answers
     per learner, the N(0, 1) prior on each learner's theta pulls weak learners toward the mean, and
     their lucky successes are absorbed into ability instead of c. Replaced by marginal maximum
     likelihood (Bock & Aitkin 1981): theta is integrated over 21 quadrature nodes on [-4, 4] with
     N(0, 1) weights; EM alternates an E-step (each learner's posterior over the nodes, accumulated
     with np.bincount) with an M-step (the item parameters under the same priors, L-BFGS on the
     item x node expected counts, 40 iterations per round), until the marginal log-likelihood
     changes by less than 1e-7 relatively (at most 300 rounds). Every per-answer share is now
     integrated over the learner's posterior over the nodes rather than read at a point theta.
     Held-out answers are predicted from the posterior built on the fit answers. Nothing else in the
     design changes.
  2. The second floor (marginal ML) still FAILED: MC c came back 0.093-0.096 for a planted 0.24-0.25,
     and the guess share of correct answers 0.065-0.075 for a true 0.110-0.129. EM run for 200 rounds
     on seed 0 left c at 0.0956, so the estimator had converged. The cause is the registered prior:
     Beta(1.2, 4) on u = 2c pulls every c toward its mode 0.03, against the few answers each item gets
     from learners far below it. Replaced as the primary prior by a format-group empirical-Bayes
     prior: u ~ Beta(1 + 8 mu_G, 1 + 8 (1 - mu_G)), with mode mu_G. mu_G is re-estimated after
     every EM round as the mean u of the items in group G (start 0.1). Groups are the item formats as
     recorded: Eedi, one group (4-option MC); XES3G5M, fill-in and MC by number of options. The same
     applies to s. The data, not the prior, set each group's centre, and items borrow strength only
     from items of their own recorded format; with no information both groups stay at the common
     start. Tried on floor seed 0 before this floor: MC c 0.235 (planted 0.245), fill-in 0.025
     (0.01), guess share of correct 0.128 (0.125), slip share of incorrect 0.071 (0.072); the flat
     Beta(1, 1) gave 0.238, 0.059, 0.142 and 0.095. The registered Beta(1.2, 4) stays as a
     sensitivity, alongside flat and centred-0.25 (Beta(5, 5)).

RESULTS (synthetic floor 3, out/irt-synthetic.json): FLOOR PASSES. MC c recovered 0.231-0.241 for a
  planted 0.241-0.247; fill-in c 0.022-0.025 for 0.01; guess share of correct within 0.003 of truth;
  slip share of incorrect within 0.012; noise shares within 0.019. Null world (truth 0): guess share
  of correct 0.015-0.019, slip share 0.016-0.018, guess noise 0.028-0.038 of variance. That is the
  estimator's own floor: figures near it are upper bounds. Per-item Spearman of estimated against planted MC c 0.43-0.52: the group means
  are recovered, single items only roughly.

RESULTS (out/irt-eedi.json, out/irt-xes.json). Items reported with >= 150 fit answers. Intervals are
  learner bootstraps with the parameters held fixed; halves and priors show parameter uncertainty.
  Eedi: 6,611,183 answers, 39,624 learners (a third), 11,027 reported items; base rate 0.643.
  XES3G5M: 5,308,394 first attempts, 18,066 learners, 4,049 reported items; base rate 0.791.
                                          Eedi                   XES3G5M
    median c, 4-option MC                 0.204 [0.204, 0.205]   0.308 [0.306, 0.310]
    mean c by options k=2, 3, 4, 5        -                      0.44, 0.38, 0.30, 0.17 (1/k: 0.50, 0.33, 0.25, 0.20)
    median c, fill-in                     -                      0.062 [0.062, 0.063]
    median slip s                         0.008                  0.007 MC, 0.015 fill-in
    guess share of correct answers        0.145 [0.144, 0.147]   0.045 [0.044, 0.045] (MC 0.112, fill-in 0.017)
    slip share of incorrect answers       0.019 [0.019, 0.020]   0.057 [0.056, 0.058]
    guess noise / total answer variance   0.317 [0.316, 0.318]   0.156 [0.155, 0.157] (MC 0.386, fill-in 0.074)
    slip noise / total answer variance    0.029                  0.069
    unexplained (mean P(1-P)) / total     0.736                  0.764
    guess noise / unexplained             0.431                  0.204
    held-out log loss 2PL, 3PL, 4PL       0.5167, 0.5147, 0.5146 0.4019, 0.4016, 0.4016
    halves: guess share of correct        0.130, 0.131           0.041, 0.040
    priors (registered, flat, centred):
      guess share of correct              0.066, 0.156, 0.149    0.023, 0.078, 0.062
      held-out log loss (EB: best)        0.5157, 0.5169, 0.5186 0.4018, 0.4019, 0.4033
  VERDICTS
    V1 (XES3G5M) NOT IDENTIFIED, on the letter of the rule: the MC-minus-fill-in median c is +0.245
       [+0.244, +0.248], far above 0.05, but fill-in's median c is 0.062, not below 0.05. In spirit
       the asymptote does separate guessing from content: MC c falls with the number of options
       roughly as 1/k (0.44, 0.38, 0.30, 0.17 against 0.50, 0.33, 0.25, 0.20), which the prior cannot
       produce, since each k is its own group started at the same value.
    V2 AT CHANCE on both: Eedi 0.204, XES3G5M 0.308 for 4 options.
    V3 Eedi: guessing MODERATE (0.145, at the band's top edge), slipping SMALL (0.019). XES3G5M:
       guessing SMALL (0.045), slipping MODERATE (0.057).
    V4 (Eedi) ABOVE THE BOUND: guess noise is 0.317 [0.316, 0.318] of total answer variance on the
       0/1 scale (halves 0.291 and 0.292; flat prior 0.312). The rough bound was about 0.24.
    V5 Eedi 4PL FITS BETTER (+0.0020 nats per held-out answer over 2PL); XES3G5M NO GAIN (+0.0003).
  The registered Beta(1.2, 4) prior, which failed the floor, roughly halves every guessing figure
  (Eedi 0.066, XES3G5M 0.023) and predicts held-out answers worse than the group prior.

    python3 irt_guess.py synthetic | eedi | xes
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
from scipy.special import expit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from shared.paths import data_path  # noqa: E402

OUT = HERE / "out"
SEED = 20260927 + 71
PRIOR = "EB"
KAPPA = 8.0
ALT_PRIORS = {"registered Beta(1.2, 4)": (1.2, 4.0), "flat": (1.0, 1.0), "centred_0.25": (5.0, 5.0)}
MIN_ITEM = 150
BOOT = 400
BOUND = 0.24
EM_MAX, EM_TOL = 300, 1e-7


def h(u, mod: int, salt: str = "") -> int:
    return int(hashlib.sha256((salt + str(u)).encode()).hexdigest()[:8], 16) % mod


# ---------------------------------------------------------------- the model

NODES = np.linspace(-4, 4, 21)
LOGW = -0.5 * NODES ** 2 - np.log(np.exp(-0.5 * NODES ** 2).sum())


class IRT:
    """Marginal-ML 2PL / 3PL / 4PL (Bock-Aitkin EM over quadrature nodes; see CHANGES 1).
    Item parameters w = [b, log a, gamma, delta] (I each; gamma, delta only for 3PL/4PL);
    c = 0.5 sigmoid(gamma), s = 0.5 sigmoid(delta)."""

    def __init__(self, li, it, y, L, I):
        self.li, self.it, self.y = li.astype(np.int64), it.astype(np.int64), y.astype(float)
        self.L, self.I = L, I

    def split(self, w, model):
        I = self.I
        b, la = w[:I], w[I:2 * I]
        g = w[2 * I:3 * I] if model in ("3PL", "4PL") else None
        dl = w[3 * I:4 * I] if model == "4PL" else None
        c = 0.5 * expit(g) if g is not None else np.zeros(I)
        s = 0.5 * expit(dl) if dl is not None else np.zeros(I)
        return b, la, g, dl, c, s

    def size(self, model):
        return self.I * {"2PL": 2, "3PL": 3, "4PL": 4}[model]

    def node_P(self, w, model, rows, q):
        b, la, _, _, c, s = self.split(w, model)
        it = self.it[rows]
        ps = expit(np.exp(la)[it] * (NODES[q] - b[it]))
        P = np.clip(c[it] + (1 - s[it] - c[it]) * ps, 1e-9, 1 - 1e-9)
        return ps, P, c[it], s[it]

    def estep(self, w, model, rows):
        li, y = self.li[rows], self.y[rows]
        LL = np.tile(LOGW, (self.L, 1))
        for q in range(len(NODES)):
            _, P, _, _ = self.node_P(w, model, rows, q)
            LL[:, q] += np.bincount(li, y * np.log(P) + (1 - y) * np.log1p(-P), self.L)
        m = LL.max(1, keepdims=True)
        post = np.exp(LL - m)
        Z = post.sum(1, keepdims=True)
        return post / Z, float((m + np.log(Z)).sum())

    def counts(self, post, rows):
        li, it, y = self.li[rows], self.it[rows], self.y[rows]
        Q = len(NODES)
        n, r = np.zeros((self.I, Q)), np.zeros((self.I, Q))
        for q in range(Q):
            wq = post[li, q]
            n[:, q] = np.bincount(it, wq, self.I)
            r[:, q] = np.bincount(it, wq * y, self.I)
        return n, r

    def mobj(self, w, model, n, r, prior):
        b, la, g, dl, c, s = self.split(w, model)
        a = np.exp(la)[:, None]
        dx = NODES[None, :] - b[:, None]
        ps = expit(a * dx)
        span = (1 - s - c)[:, None]
        P = np.clip(c[:, None] + span * ps, 1e-9, 1 - 1e-9)
        ll = (r * np.log(P) + (n - r) * np.log1p(-P)).sum()
        dP = (r - n * P) / (P * (1 - P))
        gp = dP * span * ps * (1 - ps)
        grads = [-(gp * a).sum(1) - b / 4, (gp * a * dx).sum(1) - la / 0.36]
        lp = -(b @ b) / 8 - (la @ la) / 0.72
        al, be, als, bes = prior
        if g is not None:
            u = 2 * c
            grads.append((dP * (1 - ps)).sum(1) * c * (1 - 2 * c) + (al - 1) * (1 - u) - (be - 1) * u)
            lp += ((al - 1) * np.log(u) + (be - 1) * np.log1p(-u)).sum()
        if dl is not None:
            v = 2 * s
            grads.append(-(dP * ps).sum(1) * s * (1 - 2 * s) + (als - 1) * (1 - v) - (bes - 1) * v)
            lp += ((als - 1) * np.log(v) + (bes - 1) * np.log1p(-v)).sum()
        return -(ll + lp), -np.concatenate(grads)

    def start(self, rows):
        y, it = self.y[rows], self.it[rows]
        pi = (np.bincount(it, y, self.I) + 1) / (np.bincount(it, None, self.I) + 2)
        return np.concatenate([-np.log(pi / (1 - pi)), np.zeros(self.I)])

    def prior_arrays(self, prior, mu_c, mu_s, groups):
        """Fixed (alpha, beta) for every item, or "EB": Beta(1 + K mu_G, 1 + K (1 - mu_G)) on u = 2c
        (and v = 2s), mode mu_G, with mu_G the current mean of u (v) over the items of group G."""
        if prior == "EB":
            mc, ms = mu_c[groups], mu_s[groups]
            return 1 + KAPPA * mc, 1 + KAPPA * (1 - mc), 1 + KAPPA * ms, 1 + KAPPA * (1 - ms)
        al, be = prior
        return (np.full(self.I, al), np.full(self.I, be), np.full(self.I, al), np.full(self.I, be))

    def fit(self, model, rows, prior=PRIOR, w0=None, maxiter=EM_MAX, tol=EM_TOL, groups=None):
        w = self.start(rows) if w0 is None else w0.copy()
        need = self.size(model) - len(w)
        if need > 0:        # extend a 2PL/3PL start: c = s = 0.05 (u = v = 0.1)
            w = np.concatenate([w, np.full(need, math.log(0.1 / 0.9))])
        groups = np.zeros(self.I, int) if groups is None else np.asarray(groups)
        G = int(groups.max()) + 1
        seen = np.bincount(self.it[rows], None, self.I) > 0
        mu_c, mu_s = np.full(G, 0.1), np.full(G, 0.1)
        prev = -np.inf
        for k in range(maxiter):
            post, ll = self.estep(w, model, rows)
            n, r = self.counts(post, rows)
            pa = self.prior_arrays(prior, mu_c, mu_s, groups)
            res = minimize(self.mobj, w, args=(model, n, r, pa), jac=True, method="L-BFGS-B",
                           options={"maxiter": 40})
            w = res.x
            if prior == "EB":
                c, s = self.split(w, model)[4:]
                cnt = np.maximum(np.bincount(groups[seen], None, G), 1)
                mu_c = np.clip(np.bincount(groups[seen], 2 * c[seen], G) / cnt, 0.005, 0.995)
                mu_s = np.clip(np.bincount(groups[seen], 2 * s[seen], G) / cnt, 0.005, 0.995)
            if abs(ll - prev) < tol * abs(ll):
                break
            prev = ll
        self.mu = {"c": (mu_c / 2).tolist(), "s": (mu_s / 2).tolist()}
        print(f"   {model} prior {prior}: {k + 1} EM rounds, marginal loglik {ll:.1f}", flush=True)
        post, _ = self.estep(w, model, rows)
        return w, post

    def parts(self, w, model, post, rows):
        """Per-answer numerators of every share, integrated over the learner's posterior."""
        li, y = self.li[rows], self.y[rows]
        keys = ("P", "guess_post", "guess_exp", "slip_post", "resid", "guess_noise", "slip_noise", "state_noise")
        acc = {k: np.zeros(len(y)) for k in keys}
        for q in range(len(NODES)):
            wq = post[li, q]
            ps, P, c, s = self.node_P(w, model, rows, q)
            d = 1 - s
            acc["P"] += wq * P
            acc["guess_post"] += wq * y * c * (1 - ps) / P
            acc["guess_exp"] += wq * c * (1 - ps)
            acc["slip_post"] += wq * (1 - y) * ps * s / (1 - P)
            acc["resid"] += wq * P * (1 - P)
            acc["guess_noise"] += wq * (1 - ps) * c * (1 - c)
            acc["slip_noise"] += wq * ps * d * (1 - d)
            acc["state_noise"] += wq * ps * (1 - ps) * (d - c) ** 2
        acc["y"], acc["n"], acc["wrong"] = y, np.ones_like(y), 1 - y
        return acc


def logloss(P, y):
    return float(-(y * np.log(P) + (1 - y) * np.log1p(-P)).mean())


def share_parts(ps, c, s, P, y):
    """Per-answer numerators; every reported share is a ratio of sums of these (bootstrap-friendly)."""
    d = 1 - s
    return {"y": y, "n": np.ones_like(y), "P": P,
            "guess_post": y * c * (1 - ps) / P, "guess_exp": c * (1 - ps),
            "slip_post": (1 - y) * ps * s / (1 - P), "wrong": 1 - y,
            "resid": P * (1 - P), "guess_noise": (1 - ps) * c * (1 - c), "slip_noise": ps * d * (1 - d),
            "state_noise": ps * (1 - ps) * (d - c) ** 2}


def shares_from(S):
    n, pbar = S["n"], S["P"] / S["n"]
    tot = pbar * (1 - pbar)
    return {"guess_share_of_correct": S["guess_post"] / S["y"],
            "guess_share_of_correct_expected": S["guess_exp"] / S["P"],
            "slip_share_of_incorrect": S["slip_post"] / S["wrong"],
            "guess_noise_share_of_variance": S["guess_noise"] / n / tot,
            "slip_noise_share_of_variance": S["slip_noise"] / n / tot,
            "state_noise_share_of_variance": S["state_noise"] / n / tot,
            "unexplained_share_of_variance": S["resid"] / n / tot,
            "guess_noise_share_of_unexplained": S["guess_noise"] / S["resid"],
            "slip_noise_share_of_unexplained": S["slip_noise"] / S["resid"]}


def shares(parts, groups=None, boot=0, seed=0):
    tot = {k: float(v.sum()) for k, v in parts.items()}
    point = shares_from(tot)
    if not boot:
        return {k: float(v) for k, v in point.items()}
    G = int(groups.max()) + 1
    per = {k: np.bincount(groups, v, G) for k, v in parts.items()}
    rng = np.random.default_rng(SEED + 7 + seed)
    draws = {k: [] for k in point}
    for _ in range(boot):
        wt = rng.poisson(1.0, G)
        sh = shares_from({k: float(wt @ v) for k, v in per.items()})
        for k in draws:
            draws[k].append(sh[k])
    out = {}
    for k in point:
        lo, hi = np.percentile(draws[k], [2.5, 97.5])
        out[k] = {"est": float(point[k]), "lo": float(min(lo, point[k])), "hi": float(max(hi, point[k]))}
    return out


def dist(v, rng, boot=1000):
    v = np.asarray(v, float)
    if len(v) == 0:
        return {"items": 0}
    q = np.percentile(v, [10, 25, 50, 75, 90])
    meds = np.median(rng.choice(v, (boot, len(v))), axis=1)
    return {"items": int(len(v)), "mean": float(v.mean()), "p10": float(q[0]), "p25": float(q[1]),
            "median": float(q[2]), "p75": float(q[3]), "p90": float(q[4]),
            "median_lo": float(np.percentile(meds, 2.5)), "median_hi": float(np.percentile(meds, 97.5)),
            "share_above_0.15": float((v > 0.15).mean())}


def median_diff(a, b, rng, boot=1000):
    a, b = np.asarray(a, float), np.asarray(b, float)
    est = float(np.median(a) - np.median(b))
    d = [np.median(rng.choice(a, len(a))) - np.median(rng.choice(b, len(b))) for _ in range(boot)]
    lo, hi = np.percentile(d, [2.5, 97.5])
    return {"est": est, "lo": float(min(lo, est)), "hi": float(max(hi, est))}


# ---------------------------------------------------------------- synthetic floor

def world(seed, null=False):
    rng = np.random.default_rng(SEED + seed)
    L, I, per = 6000, 400, 60
    th = rng.normal(0, 1, L)
    mc = np.arange(I) < I // 2
    c = np.where(mc, rng.uniform(0.15, 0.35, I), 0.01)
    s = rng.uniform(0, 0.15, I)
    if null:
        c[:], s[:] = 0.0, 0.0
    a = np.exp(rng.normal(0.2, 0.3, I))
    b = rng.normal(0, 1, I)
    pop = np.exp(rng.normal(0, 0.8, I))
    pop /= pop.sum()
    li = np.repeat(np.arange(L), per)
    it = np.concatenate([rng.choice(I, per, replace=False, p=pop) for _ in range(L)])
    ps = expit(a[it] * (th[li] - b[it]))
    P = c[it] + (1 - s[it] - c[it]) * ps
    y = (rng.random(len(li)) < P).astype(float)
    truth = shares(share_parts(ps, c[it], s[it], P, y))
    return li, it, y, L, I, mc, c, s, truth


def synthetic():
    from shared.stats import spearman
    out = {"seeds": [], "null": [], "passes": True}
    for sd in range(3):
        li, it, y, L, I, mc, c, s, truth = world(sd)
        m = IRT(li, it, y, L, I)
        allm = np.ones(len(y), bool)
        w2, _ = m.fit("2PL", allm)
        w, post = m.fit("4PL", allm, w0=w2, groups=mc.astype(int))
        c_i, s_i = m.split(w, "4PL")[4:]
        est = shares(m.parts(w, "4PL", post, allm))
        nitem = np.bincount(it, None, I)
        ok_items = nitem >= MIN_ITEM
        mcm, fim = mc & ok_items, ~mc & ok_items
        chk = {"c_mc": abs(c_i[mcm].mean() - c[mcm].mean()) <= 0.04,
               "c_fill": abs(c_i[fim].mean() - c[fim].mean()) <= 0.04,
               "guess_share_of_correct": abs(est["guess_share_of_correct"] - truth["guess_share_of_correct"]) <= 0.03,
               "slip_share_of_incorrect": abs(est["slip_share_of_incorrect"] - truth["slip_share_of_incorrect"]) <= 0.03,
               "guess_noise": abs(est["guess_noise_share_of_variance"] - truth["guess_noise_share_of_variance"]) <= 0.02,
               "slip_noise": abs(est["slip_noise_share_of_variance"] - truth["slip_noise_share_of_variance"]) <= 0.02}
        rec = {"truth": truth, "estimated": est, "checks": chk,
               "c_mc": [float(c[mcm].mean()), float(c_i[mcm].mean())], "c_fill": [float(c[fim].mean()), float(c_i[fim].mean())],
               "s_mean": [float(s[ok_items].mean()), float(s_i[ok_items].mean())],
               "spearman_c_mc": spearman(c[mcm], c_i[mcm]), "spearman_s": spearman(s[ok_items], s_i[ok_items]),
               "items_reported": int(ok_items.sum())}
        rec["checks"] = {k: bool(v) for k, v in chk.items()}
        out["seeds"].append(rec)
        out["passes"] &= all(chk.values())
        print(f"seed {sd}: " + ", ".join(f"{k} {'ok' if v else 'FAIL'}" for k, v in chk.items()), flush=True)
        print("   truth " + json.dumps({k: round(v, 4) for k, v in truth.items()}))
        print("   est   " + json.dumps({k: round(v, 4) for k, v in est.items()}))
        print(f"   c MC {rec['c_mc']}, fill {rec['c_fill']}, s {rec['s_mean']}, rho_c {rec['spearman_c_mc']:.2f}")
    for sd in range(2):
        li, it, y, L, I, mc, c, s, truth = world(10 + sd, null=True)
        m = IRT(li, it, y, L, I)
        allm = np.ones(len(y), bool)
        w, post = m.fit("4PL", allm, w0=m.fit("2PL", allm)[0], groups=mc.astype(int))
        est = shares(m.parts(w, "4PL", post, allm))
        ok = est["guess_share_of_correct"] < 0.04 and est["slip_share_of_incorrect"] < 0.04
        out["null"].append({"estimated": est, "passes": bool(ok)})
        out["passes"] &= bool(ok)
        print(f"null {sd}: guess {est['guess_share_of_correct']:.4f} slip {est['slip_share_of_incorrect']:.4f} {'ok' if ok else 'FAIL'}")
    OUT.mkdir(exist_ok=True)
    (OUT / "irt-synthetic.json").write_text(json.dumps(out, indent=1) + "\n")
    print("FLOOR", "PASSES" if out["passes"] else "FAILS")


# ---------------------------------------------------------------- real corpora

def analyse(name, li, it, y, learner_ids, fmt, k_opt):
    """fmt: per item label ('MC' / 'fill'); k_opt: per item options (0 for fill-in)."""
    L, I = int(li.max()) + 1, int(it.max()) + 1
    m = IRT(li, it, y, L, I)
    rng = np.random.default_rng(SEED)
    fitm = rng.random(len(y)) < 0.8
    ho = ~fitm
    print(f"{name}: {len(y):,} answers, {L:,} learners, {I:,} items; fit {fitm.sum():,}", flush=True)
    res = {"answers": int(len(y)), "learners": L, "items": I, "base_rate": float(y.mean()), "models": {}}
    grp_lab, grp = np.unique([f"{f}|{k}" for f, k in zip(fmt, k_opt)], return_inverse=True)
    ws, posts = {}, {}
    ws["2PL"], posts["2PL"] = m.fit("2PL", fitm)
    ws["3PL"], posts["3PL"] = m.fit("3PL", fitm, w0=ws["2PL"], groups=grp)
    ws["4PL"], posts["4PL"] = m.fit("4PL", fitm, w0=ws["3PL"], groups=grp)
    res["eb_prior_modes"] = {"groups": grp_lab.tolist(), **m.mu}
    for mod, w in ws.items():
        Pho = m.parts(w, mod, posts[mod], ho)["P"]
        Pfit = m.parts(w, mod, posts[mod], fitm)
        res["models"][mod] = {"heldout_logloss": logloss(np.clip(Pho, 1e-9, 1 - 1e-9), y[ho]),
                              "fit_logloss": logloss(np.clip(Pfit["P"], 1e-9, 1 - 1e-9), y[fitm])}
        if mod != "2PL":
            res["models"][mod]["shares"] = shares(Pfit, li[fitm], boot=BOOT)
    c_i, s_i = m.split(ws["4PL"], "4PL")[4:]
    nitem = np.bincount(it[fitm], None, I)
    rep = nitem >= MIN_ITEM
    drng = np.random.default_rng(SEED + 3)
    fmt, k_opt = np.asarray(fmt), np.asarray(k_opt)
    res["c"], res["s"] = {}, {}
    groups = {"all MC": (fmt == "MC") & (k_opt >= 2), "fill-in": fmt == "fill"}
    for k in sorted(set(k_opt[(fmt == "MC")].tolist())):
        groups[f"MC k={k}"] = (fmt == "MC") & (k_opt == k)
    for g, sel in groups.items():
        sel = sel & rep
        if sel.sum() == 0:
            continue
        res["c"][g] = dist(c_i[sel], drng)
        res["s"][g] = dist(s_i[sel], drng)
    res["mean_c_by_k"] = {str(k): {"items": int(((k_opt == k) & (fmt == "MC") & rep).sum()),
                                   "mean_c": float(c_i[(k_opt == k) & (fmt == "MC") & rep].mean()), "chance": 1 / k}
                          for k in sorted(set(k_opt[fmt == "MC"].tolist())) if k >= 2 and ((k_opt == k) & (fmt == "MC") & rep).any()}
    res["shares_by_format"] = {}
    for g, sel in (("MC", fmt == "MC"), ("fill-in", fmt == "fill")):
        rows = fitm & sel[it]
        if rows.sum() and rows.sum() < fitm.sum():
            res["shares_by_format"][g] = shares(m.parts(ws["4PL"], "4PL", posts["4PL"], rows), li[rows], boot=BOOT, seed=1)
    parity = np.array([h(u, 2, "half") for u in learner_ids])[li]
    res["halves"] = {}
    for hv in (0, 1):
        mk = fitm & (parity == hv)
        wh, ph = m.fit("4PL", mk, w0=ws["4PL"], groups=grp)
        res["halves"][str(hv)] = shares(m.parts(wh, "4PL", ph, mk))
        ch = m.split(wh, "4PL")[4]
        res["halves"][str(hv)]["median_c"] = {g: float(np.median(ch[sel & rep])) for g, sel in groups.items() if (sel & rep).any()}
    res["priors"] = {}
    for pn, pr in ALT_PRIORS.items():
        wp, pp = m.fit("4PL", fitm, prior=pr, w0=ws["4PL"])
        res["priors"][pn] = shares(m.parts(wp, "4PL", pp, fitm))
        cp = m.split(wp, "4PL")[4]
        res["priors"][pn]["median_c"] = {g: float(np.median(cp[sel & rep])) for g, sel in groups.items() if (sel & rep).any()}
        res["priors"][pn]["heldout_logloss"] = logloss(np.clip(m.parts(wp, "4PL", pp, ho)["P"], 1e-9, 1 - 1e-9), y[ho])
    # verdicts
    sh = res["models"]["4PL"]["shares"]
    v = {}
    g = sh["guess_share_of_correct"]["est"]
    v["V3_guess"] = "SMALL" if g < 0.05 else "MODERATE" if g <= 0.15 else "LARGE"
    sl = sh["slip_share_of_incorrect"]["est"]
    v["V3_slip"] = "SMALL" if sl < 0.05 else "MODERATE" if sl <= 0.15 else "LARGE"
    gain = res["models"]["2PL"]["heldout_logloss"] - res["models"]["4PL"]["heldout_logloss"]
    v["V5"] = "4PL FITS BETTER" if gain >= 0.001 else "NO GAIN"
    res["heldout_gain_4PL_over_2PL"] = gain
    four = "MC k=4" if "MC k=4" in res["c"] else None
    if four:
        mc4 = res["c"][four]["median"]
        v["V2"] = "AT CHANCE" if 0.15 <= mc4 <= 0.35 else "BELOW CHANCE" if mc4 < 0.15 else "ABOVE CHANCE"
    if "fill-in" in res["c"] and four:
        sel4 = (fmt == "MC") & (k_opt == 4) & rep
        self_ = (fmt == "fill") & rep
        dd = median_diff(c_i[sel4], c_i[self_], drng)
        res["median_c_mc4_minus_fill"] = dd
        v["V1"] = ("IDENTIFIED" if dd["est"] > 0.05 and dd["lo"] > 0 and res["c"]["fill-in"]["median"] < 0.05
                   else "NOT IDENTIFIED")
    if name == "eedi":
        gv = sh["guess_noise_share_of_variance"]
        v["V4"] = "BELOW THE BOUND" if gv["hi"] < BOUND else "ABOVE THE BOUND" if gv["lo"] > BOUND else "AT THE BOUND"
    syn = json.loads((OUT / "irt-synthetic.json").read_text()) if (OUT / "irt-synthetic.json").exists() else {"passes": False}
    if not syn["passes"]:
        v = {k: x + " (UNCALIBRATED)" for k, x in v.items()}
    res["verdicts"] = v
    OUT.mkdir(exist_ok=True)
    (OUT / f"irt-{name}.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({"verdicts": v, "shares": sh, "c": res["c"]}, indent=1))


def eedi():
    a = pd.read_csv(data_path("EEDI_ANSWERS"), sep="\t", usecols=["UserId", "QuestionId", "IsCorrect"],
                    dtype={"UserId": np.int64, "QuestionId": np.int64, "IsCorrect": np.int8})
    users = a.UserId.unique()
    keep = {u for u in users if h(u, 3, "g1") == 0}
    a = a[a.UserId.isin(keep)].reset_index(drop=True)
    li, uids = pd.factorize(a.UserId)
    it, _ = pd.factorize(a.QuestionId)
    I = int(it.max()) + 1
    analyse("eedi", li, it, a.IsCorrect.to_numpy().astype(float), np.asarray(uids), ["MC"] * I, [4] * I)


def xes():
    d = data_path("XES_DIR")
    a = pd.read_csv(d / "attempts.tsv", sep="\t", header=None, names=["uid", "q", "c", "res", "t"],
                    usecols=["uid", "q", "res", "t"], dtype={"uid": str, "q": str})
    a = a.reset_index().sort_values(["uid", "t", "index"]).drop_duplicates(["uid", "q"]).reset_index(drop=True)
    qs = json.loads((d / "XES3G5M/metadata/questions.json").read_text())
    li, uids = pd.factorize(a.uid)
    it, qids = pd.factorize(a.q)
    fmt = ["MC" if qs.get(q, {}).get("type") == "单选" else "fill" for q in qids]
    kopt = [len(qs[q]["options"]) if f == "MC" and isinstance(qs[q].get("options"), dict) else 0 for q, f in zip(qids, fmt)]
    analyse("xes", li, it, a.res.to_numpy().astype(float), np.asarray(uids), fmt, kopt)


if __name__ == "__main__":
    {"synthetic": synthetic, "eedi": eedi, "xes": xes}[sys.argv[1]]()
