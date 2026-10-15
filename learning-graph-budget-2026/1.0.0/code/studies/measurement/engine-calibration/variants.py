"""PRE-REGISTERED: should Lazuli's mastery engine move to a calibrated 4PL evidence model, and which
parts matter -- item difficulty and discrimination, the guessing floor, slip, the forgetting curve?

The engine (engine.py, replicated exactly and checked against a scalar transcription of the product
code) keeps a Beta belief per (learner, competency), sizes each multiple-choice response's evidence
with a 3PL item model whose parameters are placeholders (a = 1, b = 0, c = 1/m, no slip) and decays
the belief toward the prior on a 30-day half-life. This study replays it and its calibrated variants
over three open corpora and asks which changes predict held-out learners better. Written 2026-09-27;
no statistic below has been computed on real data. The engine's own LRS is not reachable from here,
so these are open-corpus answers about the engine's formulas, not about Lazuli's items.

DATA (raw data never enters the repo; out/ holds aggregates only)
  XES3G5M through data_path("XES_DIR"): attempts.tsv (uid, question, expert KC ids joined by "_",
    correct, epoch ms) and XES3G5M/metadata/questions.json (type 单选 = multiple choice, m =
    len(options); 填空 = fill-in). Every attempt kept, all learners. Competency = each leaf KC the
    attempt lists (a multi-KC attempt updates each). Attempt index = 1 + the learner's earlier
    attempts at the question. PRIMARY corpus: it alone has both formats, retries and real times.
  Eedi NeurIPS 2020 tasks 1-2 through data_path("EEDI_ANSWERS") and data_path("EEDI_ZIP") (level-3
    subjects, shared.corpus.Eedi's leaves): every question 4-option MC; one answer per (learner,
    question), the LATEST, so attempt index is always 1 and time is last-answer order at minute
    resolution (ties in file order). Learners with sha256("ec" + UserId)[:8] % 6 == 0 (memory).
  ASSISTments 2012-13 raw export streamed from its zip (guessing-gaming/assist_raw.py; nothing
    extracted): main problems (original == 1) with a skill_id, excluding open_response; correct = 1 if
    correct == 1 else 0; competency = skill_id; time = start_time. Format = problem_type; choose_1 is
    multiple choice with m = 4 ASSUMED (the export does not record options; Lazuli records m); every
    other type has c = 0 in E0. Learners with sha256("ec" + user_id)[:8] % 3 == 0 (memory).
  SPLIT (all corpora): e2e.py's learner hash, sha256(uid)[:8] % 5 == 0 is TEST. Every fitted quantity
  (item parameters, decay, the baselines' coefficients) comes from TRAIN learners; every metric is on
  TEST learners. The decay grid runs on TRAIN learners with sha256("decay" + uid)[:8] % 4 == 0 (speed).

VARIANTS (formulas in engine.py; fitting procedure in calibrate.py, whose steps are cited)
  E0   the engine as implemented.
  E1   E0 + a, b per item fitted on the engine's own theta scale (calibrate step 3), c = 1/m, d = 1.
  E2   E0 with c per item = the 4PL lower asymptote (calibrate step 1), fill-in included; d = 1.
  E3   E2 + d per item = the 4PL upper asymptote AND the slip-aware direction: the belief counts
       evidence of knowing (mode "know"), s_eff = P(know | response) = d L / P if correct,
       (1 - d) L / (1 - P) if wrong, with L = sigmoid(a (logit(p) - b)) from the stored belief;
       delta alpha = M s_eff, delta beta = M (1 - s_eff); P = c + (d - c) L.
  E4   E0 + forgetting fitted (calibrate step 2) with decay applied on read (the belief is decayed to
       the response time before sizing and predicting, which the engine does not do today).
  E5   all: E3's c, d and direction + forgetting fitted on that structure (decay on read) + a, b
       fitted on it.
  Secondary, reported: E1g (one global a, b for all items: separates item calibration from a
  rescaling of the engine's own scale), E3lr (s_eff = d / (c + d) if correct, (1 - d) / (2 - c - d)
  if wrong: the direction without the learner's prior), E4n (forgetting fitted, lazy decay as
  today), E4r (engine constants, decay on read), E4z (best decay toward ZERO, pre-LDA-1250, on read,
  against E4's best toward the prior), and leave-one-out from E5: E5-ab (a = 1, b = 0), E5-c
  (c = 1/m, a/b refitted), E5-slip (d = 1, raw direction, a/b refitted), E5-decay (engine decay,
  lazy, a/b refitted).
  Reference baselines (not engine variants): PFA-lite, e2e.py's M2 specification (off = shrunk logit
  of the item's TRAIN success rate; U = log1p prior successes and failures on all items; K = mean
  over the attempt's competencies of log1p prior successes and failures on each; IRLS on TRAIN);
  RUNNING PROPORTION per (learner, competency), (successes + 0.5) / (attempts + 1) before the
  response, averaged over the attempt's competencies.

METRICS (TEST learners; a variant's prediction is the engine's own P before the response; an
attempt's P is the mean over its competency rows)
  NEXT ATTEMPT  AUC (e2e.AUC), log loss, calibration error ECE = sum over 10 equal-count bins of P
                |mean P - mean y| x share of attempts (bin edges fixed at the point estimate).
  DELAYED       rows that are a learner's first response on a competency after a gap >= 1 day and
                >= 7 days since the previous one: log loss and AUC.
  DECISION      practice_value.py's matched-risk metric: tau set so premature advances (judged
                ready, then wrong) are 20% of wrong answers (10%, 30% reported); unneeded practice
                = correct answers judged not ready, per 1,000 attempts. Items saved = E0's minus
                the variant's.
  RELIABILITY   TEST (learner, competency) pairs with >= 10 rows: rows split by alternating position,
                each half replayed as its own sequence; Pearson r of the two halves' final mastery
                (alpha / (alpha + beta)) across pairs, Spearman-Brown 2r / (1 + r).
  BOOTSTRAP     B = 200 multinomial resamples of TEST learners, the same draws for every variant;
                percentile 95% intervals of every difference (tau re-set inside each draw).

VERDICTS (per corpus; gain = log loss(base) - log loss(variant), attempt level, TEST)
  Component contrasts: a/b = E1 vs E0; guessing floor c = E2 vs E0; slip = E3 vs E2; forgetting =
  E4 vs E0. CALIBRATION WORSE if the 95% interval of ECE(variant) - ECE(base) lies above +0.005.
    IMPROVES   gain's lower bound > 0 and calibration not worse;
    WORSENS    gain's upper bound < 0, or calibration worse with the gain's lower bound <= 0;
    NO GAIN    otherwise (a better log loss with worse calibration is NO GAIN).
  OVERALL (primary corpus XES3G5M): UPDATE RECOMMENDED if E5 IMPROVES over E0, or failing that any
    single component does ("UPDATE RECOMMENDED (subset: ...)"), and the recommended variant does
    not WORSEN on either replication corpus; NOT RECOMMENDED otherwise. REPLICATES if Eedi and
    ASSISTments give the same verdict string.
  WHICH COMPONENTS CARRY THE GAIN: component X CARRIES it if E5 beats E5-X (gain of E5 over E5-X
    with lower bound > 0). The decision, delayed and reliability metrics are reported beside the
    verdicts, not in them.

CONTROLS. E0 is the reference for everything. E1g sizes the part of E1's gain that any rescaling of
  the engine's scale would give. Fill-in items are the guessing negative control (their c should sit
  near 0). The running proportion is the model with no item model and no decay; PFA-lite is the
  logistic benchmark e2e.py uses.

SYNTHETIC FLOOR (before any real statistic; `python3 variants.py synthetic`). calibrate.py's worlds:
  world A (the truth is a 4PL with forgetting: c off chance -- 4 options U(0.1, 0.3), 3 options
  U(0.28, 0.46), fill-in U(0.03, 0.09) --, slip U(0, 0.12), item a and b, practice gains that
  decay with a 3-day half-life), 3 seeds; world B (E0 as the generator: every response drawn from
  E0's own prediction; CHANGE 2), 3 seeds;
  5,000 learners each, 80/20 split by the same hash. PASS requires:
    world A: E5 IMPROVES over E0 in 3/3 seeds, and E1, E2 and E4 each IMPROVE over E0 in >= 2/3;
    world B: no variant among E1, E2, E3, E4, E5 IMPROVES over E0 in any seed.
  The slip contrast's floor result is reported: if E3 does not IMPROVE over E2 in >= 2/3 world-A
  seeds, the real slip verdict carries "(not detected at the floor)". If the floor fails, every real
  verdict carries "(UNCALIBRATED)".

LIMITS stated in advance: open corpora are not Lazuli's items, learners or formats (Lazuli's MCQ path
  sends evidence only for questions tagged with exactly one skill; multi-KC attempts here update
  each); Eedi's latest-answer-only record removes retries and distorts time; ASSISTments' option
  counts are assumed; the item parameters are fitted on the same corpora the variants are evaluated
  on (different learners); parents and propagation are not evaluated; the decay grid is coarse
  (factor ~3 in v, refined by 0.6-1.6 at the best point); the variants change the prediction as
  well as the mass, so a gain may come from either.

CHANGES (after the first synthetic floor, before any real statistic)
  1. The asymptotes (E2, E3, E5 and their leave-one-outs) come from first responses made with at most
     2 earlier responses on the competency: calibrate.py CHANGE 1.
  2. World B is the engine as the generator: calibrate.py CHANGE 2. With E0 the truth, any IMPROVES
     in world B is a false positive of the fitting or of the bootstrap. The first run of this floor
     was stopped in world A seed 0, before any verdict was printed, when calibrate.py's floor showed
     1-2.
  3. Computation only: the matched-risk metric's sorts are cached per variant (the same value;
     asserted against the uncached form under random weights); XES3G5M is read with categorical
     columns and calibrate.Data builds its arrays in place (memory). These edits went into commit
     c137d4a by accident of another session's `git commit -a`; they were made before any real-data
     statistic (the loaders were run for structural counts only: rows, learners, items, pair lengths).

  4. Computation only: calibrate.py CHANGE 4 (Fisher scoring for a, b) after the floor below, which
     ran with L-BFGS; and calibrate.py CHANGE 3 (its own floor's half-life check), which does not
     enter any variant.

RESULTS (synthetic floor 2, out/synthetic.json): FLOOR PASSES. World A (TEST log-loss gain over E0,
  3 seeds): E1 +0.072-0.073 (E1g, one global a and b, +0.040-0.042), E2 +0.0001/+0.0012/+0.0007
  (IMPROVES 2/3), E3 over E2 +0.005-0.011 (IMPROVES 2/3; seed 1 NO GAIN on calibration), E4
  +0.0017-0.0022, E5 +0.077-0.079, every lower bound above 0 but E2's in seed 0. Fitted half-lives
  12-15 days (engine structure) against a planted 3-day gain half-life; the slip-aware structure
  picks 2-3 hours toward zero. World B (E0 generates the data): every variant WORSENS or ties; E1
  -0.0005, E2 -0.007 to -0.009, E3 -0.08, E4 -0.0002, E5 -0.060; the lazy decay refits to 30 days.
  So a gain on real data is not an artefact of fitting on TRAIN and scoring on TEST.
  Note for reading E2: at a = 1, b = 0 the engine's prediction is P = max(p, c) (p* undoes the floor
  that P adds back), so c moves only the clamp and the mass; E2's gain is small by construction.

DIRECTION: symmetric -- no edge enters; "direction" is the evidence split alpha : beta.

    python3 variants.py synthetic | xes | eedi | assist
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "studies/end-to-end/xes3g5m-build"))
import calibrate as C  # noqa: E402
import engine as E  # noqa: E402
import e2e  # noqa: E402
from practice_value import unneeded  # noqa: E402
from shared.paths import data_path  # noqa: E402

OUT = HERE / "out"
SEED = C.SEED + 17
BOOT = 200
RISKS = (0.20, 0.10, 0.30)
ECE_MARGIN = 0.005
MIN_REL = 10
T0 = time.time()


def log(*a):
    print(f"[{time.time() - T0:7.0f}s]", *a, flush=True)


def hsh(u, mod, salt=""):
    return int(hashlib.sha256((salt + str(u)).encode()).hexdigest()[:8], 16) % mod


# ---------------------------------------------------------------- fitting the variants

def fit_variants(data: C.Data, decay_sub=True) -> tuple[dict, dict]:
    train = data.rows("train")
    sub = data.rows("train", sub=(4, "decay")) if decay_sub else train
    ev_tr = data.events(train)
    ev_dec = data.events(sub)
    log(f"TRAIN rows {train.sum():,}; decay-grid rows {sub.sum():,}")
    E0 = E.engine_params(data.is_mc, data.m)
    V = {"E0": E0}
    info = {}
    asy = C.fit_asymptotes(data, train)
    info["asymptotes"] = asy
    log("asymptotes fitted")
    V["E1"] = C.fit_ab(ev_tr, E0, data.group).replace(name="E1")
    V["E1g"] = fit_ab_global(ev_tr, E0).replace(name="E1g")
    log("E1 fitted")
    V["E2"] = E0.replace(c=asy["c"], name="E2")
    V["E3"] = V["E2"].replace(d=asy["d"], mode="know", eff="post", name="E3")
    V["E3lr"] = V["E3"].replace(eff="lr", name="E3lr")
    d4 = C.fit_decay(ev_dec, E0, read=True)
    info["decay_E4"] = d4
    V["E4"] = E0.replace(v=d4["v"], dd=d4["d"], toward=d4["toward"], read=True, name="E4")
    z = d4["best_by_toward"]["zero"]
    V["E4z"] = E0.replace(v=z["v"], dd=z["d"], toward="zero", read=True, name="E4z")
    pr = d4["best_by_toward"]["prior"]
    V["E4p"] = E0.replace(v=pr["v"], dd=pr["d"], toward="prior", read=True, name="E4p")
    d4n = C.fit_decay(ev_dec, E0, read=False)
    info["decay_E4n"] = d4n
    V["E4n"] = E0.replace(v=d4n["v"], dd=d4n["d"], toward=d4n["toward"], read=False, name="E4n")
    V["E4r"] = E0.replace(read=True, name="E4r")
    log(f"E4 decay: half-life {d4['half_life_days']:.3g} d toward {d4['toward']}; lazy {d4n['half_life_days']:.3g} d")
    d5 = C.fit_decay(ev_dec, V["E3"], read=True)
    info["decay_E5"] = d5
    b5 = V["E3"].replace(v=d5["v"], dd=d5["d"], toward=d5["toward"], read=True)
    V["E5"] = C.fit_ab(ev_tr, b5, data.group).replace(name="E5")
    log(f"E5 fitted: half-life {d5['half_life_days']:.3g} d toward {d5['toward']}")
    V["E5-ab"] = V["E5"].replace(a=np.ones(data.I), b=np.zeros(data.I), name="E5-ab")
    V["E5-c"] = C.fit_ab(ev_tr, b5.replace(c=E0.c), data.group).replace(name="E5-c")
    V["E5-slip"] = C.fit_ab(ev_tr, b5.replace(d=np.ones(data.I), mode="raw"), data.group).replace(name="E5-slip")
    V["E5-decay"] = C.fit_ab(ev_tr, b5.replace(v=E.V0, dd=E.D0, toward="prior", read=False), data.group).replace(name="E5-decay")
    log("leave-one-outs fitted")
    return V, info


def fit_ab_global(ev: E.Events, prm: E.Params) -> E.Params:
    """One a and one b for every item (E1g): calibrate step 3 with all items pooled."""
    wt = 1.0 / np.bincount(ev.attempt, None, ev.natt)[ev.attempt]
    cur = prm.replace(a=np.ones_like(prm.a), b=np.zeros_like(prm.b))
    zero = np.zeros(len(ev.item), np.int64)
    w0 = None
    for _ in range(2):
        th = E.replay(ev, cur)["theta"]
        b, a, _, _, _, w0 = C.fit_ab_once(th, zero, ev.y, wt, prm.c[ev.item], prm.d[ev.item], np.zeros(1, int), 1, w0)
        cur = cur.replace(a=np.full_like(prm.a, a[0]), b=np.full_like(prm.b, b[0]))
    return cur


# ---------------------------------------------------------------- baselines

def baselines(data: C.Data) -> dict:
    """Attempt-level P on TEST for PFA-lite and the running proportion; rows' running proportion."""
    df = data.df
    y = df.y.to_numpy()
    first = np.r_[True, df.pair.to_numpy()[1:] != df.pair.to_numpy()[:-1]]
    cs = np.cumsum(y)
    grp_start = np.maximum.accumulate(np.where(first, np.arange(len(df)), 0))
    base = np.where(grp_start > 0, cs[grp_start - 1], 0.0)
    ps = cs - y - base
    n_prior = np.arange(len(df)) - grp_start
    pf = n_prior - ps
    att = df.attempt.to_numpy()
    na = int(att.max()) + 1
    cnt = np.bincount(att, None, na)
    run = np.bincount(att, (ps + 0.5) / (n_prior + 1), na) / cnt
    K1 = np.bincount(att, np.log1p(ps), na) / cnt
    K2 = np.bincount(att, np.log1p(pf), na) / cnt
    A = df.drop_duplicates("attempt").sort_values("attempt")
    A = A.assign(K1=K1[A.attempt.to_numpy()], K2=K2[A.attempt.to_numpy()])
    A = A.sort_values(["l", "t", "o"], kind="stable")
    ya = A.y.to_numpy()
    l = A.l.to_numpy()
    lstart = np.r_[True, l[1:] != l[:-1]]
    cs = np.cumsum(ya)
    gs = np.maximum.accumulate(np.where(lstart, np.arange(len(A)), 0))
    us = cs - ya - np.where(gs > 0, cs[gs - 1], 0.0)
    uf = (np.arange(len(A)) - gs) - us
    train = ~data.test_l[l]
    off, _, _ = e2e.difficulty(A.i.to_numpy(), ya.astype(np.int64), train)
    X = np.column_stack([off, np.log1p(us), np.log1p(uf), A.K1.to_numpy(), A.K2.to_numpy()]).astype(np.float64)
    beta = e2e.fit_logistic(X[train], ya[train].astype(float))
    p = 1 / (1 + np.exp(-e2e.predict(beta, X)))
    pfa = np.empty(na)
    pfa[A.attempt.to_numpy()] = p
    return {"PFA-lite": pfa, "running": run, "running_rows": (ps + 0.5) / (n_prior + 1), "pfa_beta": beta.tolist()}


# ---------------------------------------------------------------- metrics with learner bootstrap

def unneeded_w(p, y, w, risk):
    """unneeded() under integer learner-resample weights (the expanded sample, without expanding)."""
    wrong = y == 0
    pw, ww = p[wrong], w[wrong]
    o = np.argsort(pw, kind="stable")
    pw, ww = pw[o], ww[o]
    cw = np.cumsum(ww)
    n = cw[-1] if len(cw) else 0
    if n == 0:
        return float("nan")
    k = min(n - 1, int(np.floor((1 - risk) * n)))
    tau = pw[np.searchsorted(cw, k, side="right")]
    right = ~wrong
    return float((w[right] * (p[right] < tau)).sum() / w[right].sum())


class Metrics:
    """Everything for one prediction vector, as per-learner sums so a bootstrap draw is a dot product."""

    def __init__(self, P, y, grp, nl, bins=None):
        self.P = np.clip(P, 1e-9, 1 - 1e-9)
        self.y, self.grp, self.nl = y, grp, nl
        ll = -(y * np.log(self.P) + (1 - y) * np.log1p(-self.P))
        self.ll = np.bincount(grp, ll, nl)
        self.n = np.bincount(grp, None, nl)
        self.auc = e2e.AUC(self.P, y, grp)
        if bins is not None:
            q = np.quantile(self.P, np.linspace(0, 1, 11)[1:-1])
            b = np.searchsorted(q, self.P, side="right")
            self.eP = np.zeros((nl, 10))
            self.eY = np.zeros((nl, 10))
            np.add.at(self.eP, (grp, b), self.P)
            np.add.at(self.eY, (grp, b), y)

    def logloss(self, w):
        return float(w @ self.ll / (w @ self.n))

    def ece(self, w):
        return float(np.abs(w @ self.eP - w @ self.eY).sum() / (w @ self.n))

    def all(self, w, risks=()):
        out = {"logloss": self.logloss(w), "auc": self.auc(w.astype(float))}
        if hasattr(self, "eP"):
            out["ece"] = self.ece(w)
        if risks:
            wr = w[self.grp]
            share = float(wr @ self.y / wr.sum())
            for r in risks:
                out[f"unneeded_{r}"] = self.unneeded(wr, r) * share * 1000
        return out

    def unneeded(self, wr, risk):
        """unneeded_w with the sorts cached (same result; checked in evaluate)."""
        if not hasattr(self, "_wo"):
            wrong = self.y == 0
            self._wo = np.nonzero(wrong)[0][np.argsort(self.P[wrong], kind="stable")]
            self._ro = np.nonzero(~wrong)[0][np.argsort(self.P[~wrong], kind="stable")]
        cw = np.cumsum(wr[self._wo])
        n = cw[-1]
        k = min(n - 1, int(np.floor((1 - risk) * n)))
        tau = self.P[self._wo][np.searchsorted(cw, k, side="right")]
        pr = self.P[self._ro]
        cr = np.cumsum(wr[self._ro])
        j = np.searchsorted(pr, tau, side="left")
        return float((cr[j - 1] if j > 0 else 0.0) / cr[-1])


def sb_from(w, S):
    """Spearman-Brown of Pearson r from per-learner sums S (n, x, y, xx, yy, xy)."""
    n, x, yy_, xx, y2, xy = (w @ S[:, j] for j in range(6))
    cov = xy / n - x / n * yy_ / n
    vx, vy = xx / n - (x / n) ** 2, y2 / n - (yy_ / n) ** 2
    r = cov / np.sqrt(max(vx * vy, 1e-300))
    return float(2 * r / (1 + r)), float(r)


def half_events(ev_test: E.Events):
    """TEST pairs with >= MIN_REL rows split by alternating rank into two sequences (pair' = 2 pair + half)."""
    cnt = np.bincount(ev_test.pair, None, ev_test.npair)
    keep = cnt[ev_test.pair] >= MIN_REL
    idx = np.nonzero(keep)[0]
    old = np.unique(ev_test.pair[idx], return_inverse=True)[1]
    newp = 2 * old + (ev_test.rank[idx] % 2)
    o = np.lexsort((np.arange(len(idx)), newp))
    idx, newp = idx[o], newp[o]
    ev = E.Events(newp, ev_test.item[idx], ev_test.t[idx], ev_test.y[idx], ev_test.att[idx],
                  np.arange(len(idx)), ev_test.learner[idx])
    learner_of_pair = np.zeros(ev.npair, np.int64)
    learner_of_pair[newp] = ev_test.learner[idx]
    return ev, learner_of_pair[0::2]


def evaluate(data: C.Data, V: dict, base: dict) -> dict:
    test = data.rows("test")
    ev = data.events(test)
    att_learner = np.zeros(ev.natt, np.int64)
    att_learner[ev.attempt] = ev.learner
    lt, grp_att = np.unique(att_learner, return_inverse=True)
    nl = len(lt)
    grp_row = np.searchsorted(lt, ev.learner)
    y_att = ev.attempt_mean(ev.y)
    gap = ev.gap
    delayed = {"1d": (~ev.first) & (gap >= 86400), "7d": (~ev.first) & (gap >= 7 * 86400)}
    ev_h, lh = half_events(ev)
    grp_h = np.searchsorted(lt, lh)
    # test attempts -> the global attempt ids used by baselines
    d_test = data.df[test]
    glob_att = np.zeros(ev.natt, np.int64)
    glob_att[pd.factorize(d_test.attempt.to_numpy())[0]] = d_test.attempt.to_numpy()
    preds, rows_P, rel = {}, {}, {}
    for name, prm in V.items():
        o = E.replay(ev, prm)
        rows_P[name] = o["P"]
        preds[name] = ev.attempt_mean(o["P"])
        oh = E.replay(ev_h, prm)
        rel[name] = (oh["A"] / (oh["A"] + oh["B"])).reshape(-1, 2)
    for name in ("PFA-lite", "running"):
        preds[name] = base[name][glob_att]
    rows_P["running"] = base["running_rows"][test]
    rows_P["PFA-lite"] = preds["PFA-lite"][ev.attempt]
    # running proportion on the halves
    yh = ev_h.y
    first = ev_h.first
    cs = np.cumsum(yh)
    gs = np.maximum.accumulate(np.where(first, np.arange(len(yh)), 0))
    s_all = cs - np.where(gs > 0, cs[gs - 1], 0.0)
    n_all = np.arange(len(yh)) - gs + 1
    last = np.r_[first[1:], True]
    run_fin = np.zeros(ev_h.npair)
    run_fin[ev_h.pair[last]] = (s_all[last] + 0.5) / (n_all[last] + 1)
    rel["running"] = run_fin.reshape(-1, 2)
    log(f"TEST: {ev.natt:,} attempts, {nl:,} learners; reliability pairs {len(grp_h):,}")
    M = {k: Metrics(p, y_att, grp_att, nl, bins=True) for k, p in preds.items()}
    Md = {dk: {k: Metrics(p[msk], ev.y[msk], grp_row[msk], nl) for k, p in rows_P.items()} for dk, msk in delayed.items()}
    Srel = {}
    for k, v in rel.items():
        x, yv = v[:, 0], v[:, 1]
        S = np.column_stack([np.bincount(grp_h, None, nl), np.bincount(grp_h, x, nl), np.bincount(grp_h, yv, nl),
                             np.bincount(grp_h, x * x, nl), np.bincount(grp_h, yv * yv, nl), np.bincount(grp_h, x * yv, nl)])
        Srel[k] = S
    ones = np.ones(nl)
    # point estimates; unneeded() from practice_value on the unexpanded sample must equal the weighted form
    chk = np.random.default_rng(1).integers(0, 3, nl).astype(float)
    for k, m in M.items():
        assert abs(unneeded(m.P, m.y.astype(int), 0.2) - unneeded_w(m.P, m.y, np.ones(len(m.y)), 0.2)) < 1e-12
        assert abs(m.unneeded(chk[m.grp], 0.2) - unneeded_w(m.P, m.y, chk[m.grp], 0.2)) < 1e-12
    point = {k: m.all(ones, RISKS) for k, m in M.items()}
    for k in point:
        point[k]["reliability_sb"], point[k]["reliability_r"] = sb_from(ones, Srel[k]) if k in Srel else (None, None)
        for dk in delayed:
            if k in Md[dk]:
                point[k][f"delayed_{dk}_logloss"] = Md[dk][k].logloss(ones)
                point[k][f"delayed_{dk}_auc"] = Md[dk][k].auc(ones)
    rng = np.random.default_rng(SEED)
    draws = {k: [] for k in M}
    for bi in range(BOOT):
        w = np.bincount(rng.integers(0, nl, nl), minlength=nl).astype(float)
        for k, m in M.items():
            r = m.all(w, RISKS)
            if k in Srel:
                r["reliability_sb"] = sb_from(w, Srel[k])[0]
            for dk in delayed:
                if k in Md[dk]:
                    r[f"delayed_{dk}_logloss"] = Md[dk][k].logloss(w)
                    r[f"delayed_{dk}_auc"] = Md[dk][k].auc(w)
            draws[k].append(r)
        if bi % 50 == 49:
            log(f"   bootstrap {bi + 1}/{BOOT}")
    return {"point": point, "draws": draws, "n_test_attempts": int(ev.natt), "n_test_learners": int(nl),
            "n_delayed": {k: int(v.sum()) for k, v in delayed.items()}, "n_reliability_pairs": int(len(grp_h))}


def contrast(ev_out, var, base, key, sign=+1):
    """sign +1: base - var (a gain when lower is better, e.g. log loss)."""
    p = ev_out["point"]
    d = np.array([sign * (dr[base][key] - dr[var][key]) for dr in _transpose(ev_out["draws"])])
    est = sign * (p[base][key] - p[var][key])
    lo, hi = np.percentile(d, [2.5, 97.5])
    return {"est": float(est), "lo": float(lo), "hi": float(hi)}


def _transpose(draws):
    keys = list(draws)
    return [{k: draws[k][i] for k in keys} for i in range(len(draws[keys[0]]))]


def verdict(ev_out, var, base):
    g = contrast(ev_out, var, base, "logloss")
    dece = contrast(ev_out, var, base, "ece", sign=-1)     # ECE(var) - ECE(base)
    cal_worse = dece["lo"] > ECE_MARGIN
    if g["lo"] > 0 and not cal_worse:
        v = "IMPROVES"
    elif g["hi"] < 0 or (cal_worse and g["lo"] <= 0):
        v = "WORSENS"
    else:
        v = "NO GAIN"
    return v, g, dece


COMPONENTS = {"a_b": ("E1", "E0"), "guess_c": ("E2", "E0"), "slip": ("E3", "E2"), "forgetting": ("E4", "E0")}
LOO = {"a_b": "E5-ab", "guess_c": "E5-c", "slip": "E5-slip", "forgetting": "E5-decay"}


def summarise(ev_out) -> dict:
    res = {"point": ev_out["point"], "components": {}, "vs_E0": {}, "loo": {}}
    for comp, (var, base) in COMPONENTS.items():
        v, g, dece = verdict(ev_out, var, base)
        res["components"][comp] = {"contrast": f"{var} vs {base}", "verdict": v, "logloss_gain": g, "ece_change": dece}
    for var in ev_out["point"]:
        if var == "E0":
            continue
        v, g, dece = verdict(ev_out, var, "E0")
        row = {"verdict": v, "logloss_gain": g, "ece_change": dece,
               "auc_gain": contrast(ev_out, var, "E0", "auc", sign=-1)}
        for r in RISKS:
            row[f"items_saved_per_1000_at_risk_{r}"] = contrast(ev_out, var, "E0", f"unneeded_{r}")
        for key in ("delayed_1d_logloss", "delayed_7d_logloss"):
            if key in ev_out["point"][var]:
                row[key + "_gain"] = contrast(ev_out, var, "E0", key)
        for key in ("delayed_1d_auc", "delayed_7d_auc"):
            if key in ev_out["point"][var]:
                row[key + "_gain"] = contrast(ev_out, var, "E0", key, sign=-1)
        if ev_out["point"][var].get("reliability_sb") is not None:
            row["reliability_gain"] = contrast(ev_out, var, "E0", "reliability_sb", sign=-1)
        res["vs_E0"][var] = row
    for comp, var in LOO.items():
        g = contrast(ev_out, "E5", var, "logloss")
        res["loo"][comp] = {"E5_over": var, "logloss_gain": g, "carries": bool(g["lo"] > 0)}
    e5 = res["vs_E0"]["E5"]["verdict"]
    res["E5_verdict"] = e5
    res["improving_components"] = [c for c, r in res["components"].items() if r["verdict"] == "IMPROVES"]
    res["carrying_components"] = [c for c, r in res["loo"].items() if r["carries"]]
    return res


# ---------------------------------------------------------------- parameter summaries (aggregates only)

def dist(v):
    v = np.asarray(v, float)
    if len(v) == 0:
        return {"items": 0}
    q = np.percentile(v, [10, 25, 50, 75, 90])
    return {"items": int(len(v)), "mean": float(v.mean()), "p10": float(q[0]), "p25": float(q[1]),
            "median": float(q[2]), "p75": float(q[3]), "p90": float(q[4])}


def param_summary(data: C.Data, V, info, labels) -> dict:
    asy = info["asymptotes"]
    own_cd = asy["n_first"] >= C.MIN_CD
    out = {"c": {}, "d": {}, "E1_a": {}, "E1_b": {}, "E5_a": {}, "E5_b": {}, "items_by_group": {}}
    for g, lab in enumerate(labels):
        sel = data.group == g
        out["items_by_group"][lab] = {"items": int(sel.sum()), "own_c_d": int((sel & own_cd).sum())}
        out["c"][lab] = dist(asy["c"][sel & own_cd])
        out["d"][lab] = dist(asy["d"][sel & own_cd])
        for vn in ("E1", "E5"):
            own = V[vn].meta["ab"]["n_rows"] >= C.MIN_AB
            out[f"{vn}_a"][lab] = dist(V[vn].a[sel & own])
            out[f"{vn}_b"][lab] = dist(V[vn].b[sel & own])
    out["E1g"] = {"a": float(V["E1g"].a[0]), "b": float(V["E1g"].b[0])}
    out["asymptote_group_centres"] = asy["centres"]
    for k in ("decay_E4", "decay_E4n", "decay_E5"):
        out[k] = info[k]
    out["engine_half_life_days"] = E.half_life_days(E.V0, E.D0)
    return out


# ---------------------------------------------------------------- runs

def run(name, data: C.Data, labels, decay_sub=True):
    log(f"{name}: {len(data.df):,} rows, {data.df.attempt.nunique():,} attempts, {len(data.uid):,} learners, {data.I:,} items")
    V, info = fit_variants(data, decay_sub=decay_sub)
    base = baselines(data)
    ev_out = evaluate(data, V, base)
    res = summarise(ev_out)
    res["parameters"] = param_summary(data, V, info, labels)
    res["data"] = {"rows": int(len(data.df)), "attempts": int(data.df.attempt.nunique()), "learners": int(len(data.uid)),
                   "items": int(data.I), "test_attempts": ev_out["n_test_attempts"], "test_learners": ev_out["n_test_learners"],
                   "delayed_rows": ev_out["n_delayed"], "reliability_pairs": ev_out["n_reliability_pairs"],
                   "base_rate": float(data.df.drop_duplicates("attempt").y.mean())}
    return res


def floor_flags():
    f = OUT / "synthetic.json"
    if not f.exists():
        return {"uncalibrated": True, "slip_detected": False}
    s = json.loads(f.read_text())
    return {"uncalibrated": not s["passes"], "slip_detected": s["slip_detected"]}


def real(name, data, labels):
    res = run(name, data, labels)
    fl = floor_flags()
    if not fl["slip_detected"]:
        res["components"]["slip"]["verdict"] += " (not detected at the floor)"
    if fl["uncalibrated"]:
        for r in res["components"].values():
            r["verdict"] += " (UNCALIBRATED)"
        res["E5_verdict"] += " (UNCALIBRATED)"
    OUT.mkdir(exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
    report(res)


def report(res):
    p = res["point"]
    log("variant      logloss   AUC     ECE     unneeded/1000@.2  delayed7d-LL  reliability")
    for k, r in p.items():
        log(f"  {k:<10} {r['logloss']:.4f}  {r['auc']:.4f}  {r['ece']:.4f}  {r['unneeded_0.2']:7.1f}"
            f"          {r.get('delayed_7d_logloss', float('nan')):.4f}        {r.get('reliability_sb') or float('nan'):.3f}")
    for c, r in res["components"].items():
        g = r["logloss_gain"]
        log(f"  {c:<11} {r['contrast']}: {r['verdict']}  gain {g['est']:+.4f} [{g['lo']:+.4f}, {g['hi']:+.4f}]")
    g = res["vs_E0"]["E5"]["logloss_gain"]
    log(f"  E5 vs E0: {res['E5_verdict']}  gain {g['est']:+.4f} [{g['lo']:+.4f}, {g['hi']:+.4f}]; carrying {res['carrying_components']}")


def synthetic():
    out = {"A": [], "B": []}
    for kind in ("A", "B"):
        for sd in range(3):
            data, truth = C.world(kind, sd)
            res = run(f"world {kind} seed {sd}", data, ["MC4", "MC3", "fill"], decay_sub=False)
            rec = {"components": {c: r["verdict"] for c, r in res["components"].items()},
                   "vs_E0": {k: r["verdict"] for k, r in res["vs_E0"].items()},
                   "E5_gain": res["vs_E0"]["E5"]["logloss_gain"],
                   "gains": {k: r["logloss_gain"] for k, r in res["vs_E0"].items()},
                   "carrying": res["carrying_components"], "half_life_days": {
                       k: res["parameters"][k]["half_life_days"] for k in ("decay_E4", "decay_E4n", "decay_E5")},
                   "planted_half_life_days": truth["half_life_days"],
                   "point": res["point"]}
            out[kind].append(rec)
            report(res)
    A, B = out["A"], out["B"]
    okA = (all(r["vs_E0"]["E5"] == "IMPROVES" for r in A)
           and all(sum(r["vs_E0"][v] == "IMPROVES" for r in A) >= 2 for v in ("E1", "E2", "E4")))
    okB = all(r["vs_E0"][v] != "IMPROVES" for r in B for v in ("E1", "E2", "E3", "E4", "E5"))
    out["slip_detected"] = sum(r["components"]["slip"] == "IMPROVES" for r in A) >= 2
    out["world_A_passes"], out["world_B_passes"] = bool(okA), bool(okB)
    out["passes"] = bool(okA and okB)
    OUT.mkdir(exist_ok=True)
    (OUT / "synthetic.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    log(f"FLOOR {'PASSES' if out['passes'] else 'FAILS'}: world A {okA}, world B {okB}, slip detected {out['slip_detected']}")


# ---------------------------------------------------------------- corpora

def load_xes() -> tuple[C.Data, list]:
    d = data_path("XES_DIR")
    a = pd.read_csv(d / "attempts.tsv", sep="\t", header=None, names=["uid", "q", "kc", "res", "t"],
                    dtype={"uid": "category", "q": "category", "kc": "category", "res": np.int8, "t": np.int64})
    qs = json.loads((d / "XES3G5M/metadata/questions.json").read_text())
    li, uids = a.uid.cat.codes.to_numpy(np.int64), np.asarray(a.uid.cat.categories)
    ii, qids = a.q.cat.codes.to_numpy(np.int64), list(a.q.cat.categories)
    combo, combos = a.kc.cat.codes.to_numpy(np.int64), list(a.kc.cat.categories)
    kc_lists = [c.split("_") for c in combos]
    kc_id, _ = pd.factorize(pd.Series([k for ks in kc_lists for k in ks]))
    lens = np.array([len(ks) for ks in kc_lists])
    starts = np.r_[0, np.cumsum(lens)[:-1]]
    rep = lens[combo]
    row = np.repeat(np.arange(len(a)), rep)
    offs = np.arange(len(row)) - np.repeat(np.cumsum(rep) - rep, rep)
    comp = kc_id[starts[combo][row] + offs]
    fmt = np.array(["MC" if qs.get(q, {}).get("type") == "单选" else "fill" for q in qids])
    m = np.array([len(qs[q]["options"]) if f == "MC" and isinstance(qs[q].get("options"), dict) else 0 for q, f in zip(qids, fmt)])
    is_mc = fmt == "MC"
    labels, group = np.unique([f"{f}|{k}" for f, k in zip(fmt, m)], return_inverse=True)
    y = a.res.to_numpy(float)
    t = a.t.to_numpy() / 1000.0
    del a
    data = C.Data(li[row], ii[row], comp, y[row], t[row], row, is_mc, m, group, np.asarray(uids))
    return data, labels.tolist()


def load_eedi() -> tuple[C.Data, list]:
    from shared.corpus import Eedi
    leaves = Eedi(data_path("EEDI_ANSWERS"), data_path("EEDI_ZIP")).leaves
    parts, keep = [], {}
    for ch in pd.read_csv(data_path("EEDI_ANSWERS"), sep="\t", usecols=["UserId", "QuestionId", "IsCorrect", "DateAnswered"],
                          dtype={"UserId": np.int64, "QuestionId": np.int64, "IsCorrect": np.int8, "DateAnswered": str},
                          chunksize=2_000_000):
        for u in ch.UserId.unique():
            if u not in keep:
                keep[u] = hsh(u, 6, "ec") == 0
        ch = ch[ch.UserId.map(keep).to_numpy(bool)]
        parts.append(ch)
    a = pd.concat(parts, ignore_index=True)
    a["o"] = np.arange(len(a))
    a["t"] = (pd.to_datetime(a.DateAnswered) - pd.Timestamp("1970-01-01")).dt.total_seconds()
    lv = {int(q): v for q, v in leaves.items()}
    a = a[a.QuestionId.isin(lv.keys())]
    li, uids = pd.factorize(a.UserId)
    ii, qids = pd.factorize(a.QuestionId)
    L = [lv[int(q)] for q in qids]
    comp_names = pd.factorize(pd.Series([x for ls in L for x in ls]))
    kc_of = {}
    j = 0
    for q, ls in enumerate(L):
        kc_of[q] = comp_names[0][j:j + len(ls)]
        j += len(ls)
    lens = np.array([len(ls) for ls in L])
    rep = lens[ii]
    row = np.repeat(np.arange(len(a)), rep)
    offs = np.arange(len(row)) - np.repeat(np.cumsum(rep) - rep, rep)
    starts = np.r_[0, np.cumsum(lens)[:-1]]
    comp = comp_names[0][starts[ii][row] + offs]
    I = len(qids)
    data = C.Data(li[row], ii[row], comp, a.IsCorrect.to_numpy(float)[row], a.t.to_numpy()[row], a.o.to_numpy()[row],
                  np.ones(I, bool), np.full(I, 4), np.zeros(I, int), np.asarray(uids))
    return data, ["MC|4"]


def load_assist() -> tuple[C.Data, list]:
    sys.path.insert(0, str(ROOT / "studies/measurement/guessing-gaming"))
    import assist_raw
    a = assist_raw.load(mod=3, keep=0, salt="ec", dedupe=False, with_skill_rows=True, chunksize=500_000)
    a = a[(a.original == 1) & (a.skill_id.notna()) & (a.ts > 0) & (a.ptype >= 0)]
    a = a[a.ptype != assist_raw.PTYPES.index("open_response")]
    a = a.drop_duplicates(["problem_log_id", "skill_id"]).reset_index(drop=True)
    a["y"] = (a.correct == 1).astype(float)
    a["o"] = a.problem_log_id.rank(method="dense").astype(np.int64)
    li, uids = pd.factorize(a.user_id)
    ii, pids = pd.factorize(a.problem_id)
    kk, _ = pd.factorize(a.skill_id)
    pt = a.drop_duplicates("problem_id").set_index("problem_id").ptype.reindex(pids).to_numpy()
    is_mc = pt == assist_raw.PTYPES.index("choose_1")
    labels = assist_raw.PTYPES
    data = C.Data(li, ii, kk, a.y.to_numpy(), a.ts.to_numpy(float), a.o.to_numpy(), is_mc, np.where(is_mc, 4, 0),
                  pt.astype(int), np.asarray(uids))
    return data, list(labels)


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "synthetic":
        synthetic()
    else:
        data, labels = {"xes": load_xes, "eedi": load_eedi, "assist": load_assist}[what]()
        real(what, data, labels)
