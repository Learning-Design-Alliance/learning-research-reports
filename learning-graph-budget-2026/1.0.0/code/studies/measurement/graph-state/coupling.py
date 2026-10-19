"""PRE-REGISTERED: does holding a learner's state as one coupled posterior over the skill graph forecast
better than an independent belief per skill -- at nodes the learner has not been seen on, further
ahead in time, and with honest uncertainty?

docs/specs/ESTIMAND.md section 8 defines the state estimand as the JOINT mastery posterior over the
graph, coupled by its relations and estimated like weather data assimilation. Lazuli's engine holds an
independent Beta per competency and hands increments to parents; nothing flows back down or sideways.
This study replays both on open corpora and asks what coupling buys. Written 2026-09-28, before any
statistic of this design on real data. Structural counts only were read first (XES3G5M: 6.35M rows,
5.49M attempts, 18,066 learners, 865 KCs, 1-6 KCs per attempt, 181-898 attempts and 67-292 KCs per
learner; peak 2.1 GB to load). The machinery was debugged on synthetic worlds of the floor's shape
before this commit (not the floor runs, which follow it); four things found there are part of the
design below: the Stage-1 scale anchor (joint maximum likelihood drifted), cells linearised at the
learner's ability (the Laplace fit at a weak-prior mode made all-correct cells look like pure noise and
collapsed D), the practice term, and the rank chosen by the filter's own cold-node loss (a cell-density
criterion preferred r = 0 in a world with 15 planted blocks). Open-corpus answers about the formulas,
not about Lazuli's items.

DATA (raw data never enters the repo; out/ holds aggregates only). Loaded through
engine-calibration/variants.py's loaders (imported), with their row definitions: one row per (attempt,
competency); multi-competency attempts have one row per competency.
  XES3G5M (PRIMARY) through data_path("XES_DIR"): competency = leaf KC id. Hierarchy = cid2route.json's
    KC route tree (e2e.routes()). Learners with sha256("gs" + uid)[:8] % 2 == 0 (memory: the 4 GB cap).
  Eedi NeurIPS 2020 through data_path("EEDI_ANSWERS"), data_path("EEDI_ZIP"): competency = level-3
    subject; hierarchy = subject_metadata.csv's ParentId tree (levels 0-3). variants.py's 1-in-6 learner
    subsample. Order is LAST-answer order (Eedi keeps the latest answer only): a "first attempt at a
    skill" is the first in that order.
  ASSISTments 2012-13 streamed from its zip (guessing-gaming/assist_raw.py via variants.load_assist):
    competency = skill_id; NO hierarchy, so C1, C3, C3g and C3c are not applicable. 1-in-3 subsample.
  The KC / subject names are recovered by recording the loaders' own pd.factorize calls (the loaders
  return dense ids only), and checked: the name count equals the competency count; Eedi items' leaves
  match the loader's rows.
  SPLIT: e2e.py's learner hash (sha256(uid)[:8] % 5 == 0 is TEST). Every fitted quantity comes from
  TRAIN learners; every metric is on TEST learners. Rank selection splits TRAIN by
  sha256("gsrank" + uid)[:8] % 4 == 0 (validation) against the rest.
  SKILL CAP: none. The covariance is low-rank plus diagonal (or one factor per group), so its size is
  O(K r). A skill with fewer than 20 TRAIN cells keeps the prior's centre (mean loading, median D).

VARIANTS (per learner, over the skills; gstate.py implements each)
  C0  independent per-skill state: engine-calibration's calibrated engine in its recommended form, E5
      without the fitted decay ("E5-decay": per-item a, b, c, d, slip-aware direction, the engine's lazy
      30-day decay). Fitted with calibrate.py's steps 1 and 3 on TRAIN. E5-decay is within 0.0005 nats
      of E5 on all three corpora and keeps C0's decay identical to C2's, so the contrast isolates
      coupling. The prediction is the engine's own P from the stored state.
  C1  C0 + the engine's parent propagation (generate_parent_assertions): every applied increment,
      after the engine's bound, is handed with weight 1 to each ancestor up the chain, which decays by
      its own elapsed time and adds it. The engine never writes back to a child, so on its own
      propagation leaves a leaf's first forecast at the prior; the product reads parents only where a
      parent is itself assessed (XES3G5M KCs that are ancestors of other KCs). C1 therefore also
      READS THE PARENT: a skill with no evidence of its own is forecast from the nearest ancestor holding
      evidence (the most the engine's hierarchy offers a cold node). C1-engine (propagation, own state
      only) is reported beside it. Multi-KC attempts propagate once per KC (the engine's behaviour).
  C2  Gaussian coupled state. Logit mastery theta (K skills) ~ N(mu, Sigma), Sigma = W W^T + D, W K x r.
      Every C2-family response model: P = c + (d - c) sigmoid(a (theta_eff + beta x - b)), theta_eff =
      the mean of the item's skills' thetas (compensatory), x = the mean over those skills of
      log(1 + the learner's earlier attempts on the skill) (a practice term, so that theta is mastery at
      first encounter; without it a static prior over-predicts first attempts and under-predicts
      practised ones). STAGE 1 (TRAIN): c, d = C0's asymptotes; learner ability theta_l ~ N(0, 2^2)
      (standardised each round: the scale anchor), the global practice slope beta and per-item a, b by
      calibrate's penalised fit (fit_ab_once), alternated 4 rounds; then per (learner, skill) cell a
      Gaussian pseudo-measurement of theta_lk: the cell's likelihood linearised at theta_l (precision J =
      Fisher information, value theta_l + score / J), a row's other skills held at theta_l; cells with
      J < 0.02 dropped. STAGE 2 (TRAIN): mu, W, D by MAP-EM (factor analysis with missing cells and each
      cell's own noise 1 / J), 40 iterations, loadings ~ N(mean loading, 0.5^2), each D_k pulled toward
      the median by 10 pseudo-cells. RANK r in {0, 1, 2, 4, 8, 12, 16, 24}, chosen on TRAIN: EM on the
      non-validation TRAIN learners' cells, then the filter (Stage-1 items) on the validation learners;
      the rank with the lowest cold-attempt (M1) log loss there; then refitted on all TRAIN cells.
      THE FILTER (TEST, per response): evidence on skill k is held as a Gaussian pseudo-measurement of
      theta_k (precision q_k, information s_k); the state is the prior conditioned on all of them (exact
      Gaussian conditioning through the factor form; no approximation beyond the linearisation). Before
      a response: theta_eff's predictive mean m and variance v from the skills' joint predictive; P =
      c + (d - c) sigmoid(a (m + beta x - b) / sqrt(1 + pi a^2 v / 8)) (the logistic-normal integral,
      probit approximation). Update: one Laplace / extended-Kalman step at m -- score g and Fisher
      information J of the response in theta_eff. HYPEREDGE RULE: a response on an nS-skill item is
      spread evenly (compensatory, as difficulty.py's additive-difficulty finding supports): each skill's
      pseudo-measurement gains precision J / nS at value m_k + g / J. A wrong answer is spread the same
      way (credit assignment is open; this is the neutral rule). FORGETTING: before adding, q_k and s_k
      of each touched skill are multiplied by the engine's retention (1 + 0.1 t)^(-0.5) over the days t
      since that skill's last evidence -- drift toward the prior, lazy, as the engine.
      ITEMS, PER VARIANT: starting from Stage 1's, a, b and beta are refitted on TRAIN to that variant's
      own predictive state (m, v) -- two passes of filter then fit, calibrate step 3's penalised
      objective and minimum samples, Fisher scoring (beta in a separate step: it trades off against b)
      -- as calibrate fits E5's a, b to the engine's own scale. c, d = C0's.
  C3  C2 with the covariance restricted to graph neighbours: one factor per SIBLING GROUP (the skills
      sharing an immediate parent: XES3G5M route tree, Eedi level-2 subject), Sigma block-diagonal by
      group, fitted by the same EM restricted to that structure (a group with fewer than 2 fitted skills
      carries no coupling). Tests whether the graph's own edges carry the coupling. An XES3G5M KC that
      is also an ancestor of other KCs sits in its own parent's group, not its children's, so
      parent-child pairs are coupled only in C3c (a limit).
  Controls and secondary (reported; the verdicts below name which enter them)
    C2-diag  C2's mu and marginal variances diag(Sigma), no coupling: the same machinery without
             coupling. A gain of C2 over C0 that C2-diag also has is not a coupling gain.
    C2-shuf  C2's correlations with skill labels DERANGED within deciles of TRAIN cell count (family-
             matched: well-sampled skills take well-sampled skills' correlations), each skill keeping its
             own variance: the same correlation spectrum, so the same size of coupling, at the wrong
             skills. Three derangements; their metrics are averaged in every bootstrap draw.
    C2g      a general factor only (dense r = 1).
    C3g      a general factor plus the sibling-group factors (the engine-implementable hierarchy).
    C3c      one factor per coarse group (XES3G5M route depth 2; Eedi level-1 subject).
    PFA-lite engine-calibration's logistic reference (it pools learner-level counts across skills);
    CLIM     climatology: the item's TRAIN success rate (5 pseudo-answers at the mean); the reference of
             every skill score.

METRICS (TEST learners; an attempt's P for C0 / C1 is the mean over its competency rows, as
engine-calibration; for the C2 family one P per attempt)
  M1 COLD NODE (headline): attempts all of whose skills the learner has never attempted before, and
     that are not the learner's first attempt. Log loss, AUC, ECE, skill score vs CLIM.
  M2 NEXT ATTEMPT: every TEST attempt; log loss, AUC, ECE.
  M3 HORIZON: attempts all of whose skills have earlier evidence, binned by the time since the most
     recent evidence on any of its skills: < 1 day, [1, 7), [7, 30), >= 30 days. Log-loss skill score
     vs CLIM per bin, and the gain over C0. A variant's PREDICTABILITY HORIZON is the last bin of an
     unbroken run from < 1 day whose skill-score lower bound is above 0; its decay is the skill score
     per bin relative to the < 1 day bin.
  M4 CALIBRATION: ECE (10 equal-count bins) on M1 and M2. PREDICTIVE INTERVALS: windows of k = 5
     consecutive single-skill attempts on one skill -- COLD (the pair's rows 0-4) and WARM (rows 3-7);
     the count correct is forecast from the state before the window's first attempt (theta ~ N(m, v)
     held fixed, 20-point Gauss-Hermite, with each attempt's practice term; C0: p ~ Beta(alpha, beta),
     20 quantile points), each attempt Bernoulli under its own item. Randomised PIT; coverage of the central 50 / 80 / 95% intervals.
     CALIBRATED INTERVALS if every coverage is within 0.05 of nominal; OVER-CONFIDENT if any is more
     than 0.05 below; UNDER-CONFIDENT if any is more than 0.05 above (and none below).
  M5 DECISION: practice_value.py's matched-risk metric on every TEST attempt (tau so premature advances
     are 20% of wrong answers; 10%, 30% reported); items saved per 1,000 attempts = C0's unneeded
     practice minus the variant's.
  BOOTSTRAP: B = 200 multinomial resamples of TEST learners, the same draws for every variant and
     metric; 95% percentile intervals of every difference (engine-calibration's Metrics and contrast).

VERDICTS (per corpus; gain = log loss(C0) - log loss(variant), TEST attempts of the metric)
  COUPLING: COUPLING HELPS COLD NODES if C2's M1 gain has its lower bound above 0. Attribution check
    (added by this study): if C2 does not also beat C2-diag on M1 (lower bound > 0), the verdict reads
    "C2 HELPS COLD NODES, NOT BY COUPLING". NO COUPLING GAIN otherwise. If TEST holds fewer than 500
    cold attempts, M1 is UNANSWERABLE.
  GRAPH: retention = M1 gain of C3 / M1 gain of C2 (point estimate; bootstrap interval reported).
    [CHANGE 1: both gains are measured over C2-diag, and the GRAPH verdict needs COUPLING HELPS.]
    GRAPH CARRIES THE COUPLING if retention >= 0.5 and C2's M1 gain is above 0; EMPIRICAL COVARIANCE
    ONLY if retention < 0.5 with C2 > C0; NO COUPLING GAIN otherwise; NOT TESTABLE without a hierarchy.
    Flag: if C3 retains >= 50% in the synthetic GENERAL-FACTOR world (world H, below), the GRAPH verdict
    carries "(not diagnostic: a general factor seen through siblings also passes)"; C3g against C2g is
    then the reading of the graph beyond a general level.
  WHICH SKILLS: C2 vs C2-shuf on M1: WHICH SKILLS CO-VARY MATTERS if the lower bound is above 0;
    GENERAL LEVEL ONLY otherwise.
  GUARD M2: C2 WORSENS NEXT-ATTEMPT if the M2 gain's upper bound is below 0; C2 IMPROVES NEXT-ATTEMPT if
    its lower bound is above 0; C2 DOES NOT WORSEN NEXT-ATTEMPT otherwise.
  C1: PARENT READ HELPS COLD NODES if C1's M1 gain has its lower bound above 0.
  M3, M4, M5 are reported beside the verdicts with their intervals.

SYNTHETIC FLOOR (before any real statistic; `python3 coupling.py synthetic`). Worlds shaped like the
  corpora at small scale: 3,000 learners, 60 skills in 15 sibling groups of 4 (3 coarse groups of 5);
  per skill 8 single-skill items and one two-skill item (half within the group); half MC (c ~ U(0.1,
  0.3)), half fill-in (c ~ U(0.02, 0.08)), slip ~ U(0, 0.04), a ~ logN(0, 0.25), b = skill offset
  N(-0.8, 0.6) + N(0, 0.7); learners meet new skills group by group in a random order, 20-44 sessions
  of 4-8 attempts, 35% of sessions revisiting a seen skill, sessions 1 hour to 40 days apart; practice
  gain +0.15 per attempt decaying on a 3-day half-life; theta ~ N(0, Sigma) with total variance 1.2:
    G  graph coupling: within-group correlation 0.6, none across groups;
    E  empirical coupling off the graph: two random factors, loadings N(0, 0.55^2), D = 0.6;
    I  independent skills: Sigma = 1.2 I;
    H  a general factor only: loadings N(0.85, 0.1^2), D = 0.48 (reported; sets the GRAPH flag).
  Two seeds of G, E and I, one of H. PASS requires, in every seed:
    G  COUPLING HELPS COLD NODES (with C2 > C2-diag), GRAPH CARRIES THE COUPLING, and C2 beats C2-shuf;
    E  COUPLING HELPS COLD NODES and EMPIRICAL COVARIANCE ONLY;
    I  C2 does not beat C0 on M1 (lower bound <= 0) and does not beat C2-diag; [CHANGE 2: the first
       half replaced by "no COUPLING HELPS COLD NODES verdict"]
    all  C2 does not WORSEN NEXT-ATTEMPT.
  If the floor fails, every real verdict carries "(UNCALIBRATED)".

LIMITS stated in advance: open corpora, not Lazuli's items or graphs; the Laplace step linearises one
  response at a time; the hyperedge rule splits evidence evenly and cannot assign blame for a wrong
  answer; Stage 1 is a static calibration, so practice gains within a skill are absorbed by the
  pseudo-measurements, not modelled; items come from TRAIN of the same corpora (different learners);
  Eedi's order is last-answer order; ASSISTments has no hierarchy; the covariance assumes cells are
  missing at random given the model (curricula are not random, so it is a predictive, not a causal,
  covariance); the decay is the engine's lazy curve for both C0 and C2 (engine-calibration: fitting it
  gains at most 0.002 nats); C1's parent read is not in the product; the C2 family carries a practice
  term C0 does not (it is 0 on every M1 attempt; on M2 a C2-C0 difference mixes coupling, machinery and
  practice, which is why C2-diag is the coupling control); learner subsamples as above.

CHANGES (after the first synthetic floor, before any real statistic)
  1. GRAPH retention is (C3 - C2-diag) / (C2 - C2-diag) on M1, not (C0 - C3) / (C0 - C2), and the GRAPH
     verdict is given only under COUPLING HELPS COLD NODES (otherwise NO COUPLING GAIN); the registered
     ratio is reported beside it. Floor 1 failed world E seed 1 on it: the Gaussian machinery alone
     (C2-diag) gains +0.0040 nats over C0 on cold nodes there, C3 matched C2-diag (+0.0042) and so
     "retained" 0.505 of C2's +0.0084 while carrying none of the off-graph coupling. World I read GRAPH
     CARRIES THE COUPLING with no coupling planted, for the same reason. The world-H flag uses the new
     ratio (floor 1: 0.378 registered, 0.33 new; no flag either way).
  2. World I's check "C2 does not beat C0" becomes "no COUPLING HELPS COLD NODES verdict" (C2 not above
     C2-diag). Floor 1: C2 beat C0 by +0.0027 and +0.0060 in the two seeds, and C2-diag by as much
     (+0.0025, +0.0062): a machinery gain at first encounters (C0's cold forecast is the engine at the
     Jeffreys prior; the C2 family's is the item integrated over the population prior), which the
     registered attribution check already names "C2 HELPS COLD NODES, NOT BY COUPLING". The C2-over-C0
     gain in world I is reported. Floor 1's other checks passed: world G both seeds (GRAPH CARRIES,
     C2 over C2-shuf), world E seed 0 (EMPIRICAL COVARIANCE ONLY), no WORSENS anywhere. Its record
     is out/synthetic-floor1.json; out/synthetic.json is floor 2.
  3. Computation only: a real run reads the floor record (the H flag, UNCALIBRATED) after its own fit
     and replay, waiting for the floor to finish, so the XES3G5M run could start while floor 2 ran.
     Its verdict lines were not read until floor 2 had passed.

RESULTS (floor 2, out/synthetic.json): FLOOR PASSES. M1 gains over C0 (nats per cold attempt):
  G  C2 +0.0074 / +0.0096 (C2-diag +0.0013 / +0.0031), C3 +0.0088 / +0.0123, retention 1.23 / 1.42:
     GRAPH CARRIES THE COUPLING; C2-shuf -0.0027 / -0.0024. Ranks 24 and 16 (15 planted blocks).
  E  C2 +0.0039 / +0.0084 (C2-diag +0.0004 / +0.0040), C3 +0.0000 / +0.0042, retention -0.10 / 0.06:
     EMPIRICAL COVARIANCE ONLY. Rank 4.
  I  C2 +0.0027 / +0.0060, C2-diag +0.0025 / +0.0062: C2 HELPS COLD NODES, NOT BY COUPLING.
  H  C2 +0.0234, C2-diag +0.0017, C3 +0.0088 (retention 0.33: no flag), C2-shuf +0.0232 (GENERAL LEVEL
     ONLY: a derangement leaves a general factor in place), C3g +0.0228. Rank 1.
  C2's predictive intervals are CALIBRATED in every world (coverage within 0.04 of nominal). No variant
  WORSENS NEXT-ATTEMPT. C1 (parent read) loses 0.006-0.017 nats on cold nodes in every world.

RESULTS (real runs, code at 66a17bd; README.md has the tables). COUPLING HELPS COLD NODES in all three
  corpora: C2's M1 gain over C0 +0.0457 [+0.0424, +0.0486] (XES3G5M), +0.0473 [+0.0423, +0.0533]
  (ASSISTments), +0.0672 [+0.0634, +0.0711] (Eedi); over C2-diag +0.046, +0.032, +0.066. GRAPH:
  EMPIRICAL COVARIANCE ONLY on XES3G5M (retention 0.141 [0.132, 0.151]) and Eedi (0.348 [0.328,
  0.365]); not testable on ASSISTments. A general factor (C2g) carries 95-99% of the gain; C3g over C2g
  +0.001 / +0.002. WHICH SKILLS CO-VARY MATTERS (C2 over C2-shuf +0.002 to +0.008). C2 IMPROVES
  NEXT-ATTEMPT (+0.036, +0.020, +0.037). Horizon: C0 7-30 days, < 1 day, >= 30 days; C2 >= 30 days
  everywhere. C2's intervals CALIBRATED; C0's UNDER-CONFIDENT at cold windows. Items saved at 20% risk
  +74, +26, +53 per 1,000. C1 (parent read) -0.009 on XES3G5M, +0.025 on Eedi.

DIRECTION: symmetric -- no edge is oriented; the hierarchy enters only as undirected groups (C3) and as
the engine's child-to-parent propagation, whose orientation is the product's and is not tested here.

    python3 coupling.py synthetic | xes | eedi | assist
"""

from __future__ import annotations

import hashlib
import json
import math
import resource
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EC = ROOT / "studies/measurement/engine-calibration"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(EC))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "studies/end-to-end/xes3g5m-build"))
import calibrate as C  # noqa: E402
import engine as E  # noqa: E402
import variants as V  # noqa: E402
import e2e  # noqa: E402
import gstate as S  # noqa: E402
from shared.paths import data_path  # noqa: E402

OUT = HERE / "out"
SEED = 20260928
BOOT = 200
RISKS = (0.20, 0.10, 0.30)
RANKS = (0, 1, 2, 4, 8, 12, 16, 24)
N_SHUF = 3
MIN_COLD = 500
BINS = (("h0", 0, 1), ("h1", 1, 7), ("h7", 7, 30), ("h30", 30, math.inf))
LEVELS = (0.5, 0.8, 0.95)
WIN = 5
T0 = time.time()


def log(*a):
    gb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6
    print(f"[{time.time() - T0:7.0f}s {gb:4.1f}GB]", *a, flush=True)


def hsh(u, mod, salt=""):
    return int(hashlib.sha256((salt + str(u)).encode()).hexdigest()[:8], 16) % mod


# ---------------------------------------------------------------- corpora and hierarchies

class Hier:
    """groups / coarse: per competency; chain (N, depth): ancestors nearest first (C1); None if absent."""

    def __init__(self, groups=None, coarse=None, chain=None):
        self.groups, self.coarse, self.chain = groups, coarse, chain


def _capture(fn):
    """Run a loader, recording its pd.factorize calls (the loaders return dense ids only)."""
    orig = pd.factorize
    got = []

    def spy(*a, **k):
        r = orig(*a, **k)
        got.append(r)
        return r

    pd.factorize = spy
    try:
        out = fn()
    finally:
        pd.factorize = orig
    return out, got


def subsample(data: C.Data, keep_l: np.ndarray) -> C.Data:
    """A calibrate.Data holding only the learners with keep_l (dense learner ids kept per item/comp)."""
    d = data.df[keep_l[data.df.l.to_numpy()]]
    li, uniq = pd.factorize(d.l.to_numpy())
    return C.Data(li, d.i.to_numpy(), d.k.to_numpy(), d.y.to_numpy(), d.t.to_numpy(), d.o.to_numpy(),
                  data.is_mc, data.m, data.group, np.asarray(data.uid)[uniq])


def _tree(K, parents_of, depth_group, depth_coarse):
    """parents_of[j]: list of ancestor keys nearest first (hashable); competencies that are themselves an
    ancestor key are that node. -> Hier."""
    node_of = {}
    own = {}
    for j in range(K):
        own.setdefault(parents_of[j][0], j)
    nxt = K
    rows = []
    for j in range(K):
        ch = []
        for key in parents_of[j][1:]:
            if key in own:
                ch.append(own[key])
            else:
                if key not in node_of:
                    node_of[key] = nxt
                    nxt += 1
                ch.append(node_of[key])
        rows.append(ch)
    depth = max(1, max(len(r) for r in rows))
    chain = np.full((nxt, depth), -1, np.int64)
    for j, r in enumerate(rows):
        chain[j, :len(r)] = r
    groups = pd.factorize(pd.Series([depth_group(parents_of[j]) for j in range(K)]))[0]
    coarse = pd.factorize(pd.Series([depth_coarse(parents_of[j]) for j in range(K)]))[0]
    return Hier(groups.astype(np.int64), coarse.astype(np.int64), chain)


def load_xes():
    (data, labels), got = _capture(V.load_xes)
    names = [str(x) for x in got[0][1]]
    K = int(data.df.k.max()) + 1
    assert len(names) == K, (len(names), K)
    keep = np.array([hsh(u, 2, "gs") == 0 for u in data.uid])
    data = subsample(data, keep)
    rt = e2e.routes()
    miss = sum(n not in rt for n in names)
    assert miss <= 0.01 * K, f"{miss} KCs without a route"
    parents_of = []
    for j, n in enumerate(names):
        r = tuple(rt.get(n, [f"?{n}"]))
        parents_of.append([r[:len(r) - h] for h in range(len(r))])   # self route first, then ancestors
    hier = _tree(K, parents_of, lambda p: p[1] if len(p) > 1 else p[0],
                 lambda p: p[0][:2] if len(p[0]) > 2 else p[0][:1])
    log(f"XES3G5M: KC routes resolved for {K - miss}/{K}; sibling groups {hier.groups.max() + 1}, "
        f"coarse {hier.coarse.max() + 1}, hierarchy nodes {hier.chain.shape[0]}")
    return data, labels, hier


def load_eedi():
    import csv
    import io
    import zipfile
    (data, labels), got = _capture(V.load_eedi)
    qids, comp = got[1][1], [str(x) for x in got[2][1]]
    K = int(data.df.k.max()) + 1
    assert len(comp) == K and len(qids) == data.I, (len(comp), K, len(qids), data.I)
    from shared.corpus import Eedi
    leaves = Eedi(data_path("EEDI_ANSWERS"), data_path("EEDI_ZIP")).leaves
    chk = data.df.drop_duplicates(["i", "k"]).groupby("i").k.apply(lambda s: sorted(comp[x] for x in s))
    bad = sum(chk[i] != sorted(leaves[str(qids[i])]) for i in chk.index[:2000])
    assert bad == 0, f"{bad} Eedi items whose leaves do not match"
    z = zipfile.ZipFile(data_path("EEDI_ZIP"))
    with z.open("data/metadata/subject_metadata.csv") as f:
        meta = {r["SubjectId"]: r for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig"))}
    parents_of = []
    for n in comp:
        sid = n[1:]
        ch = [("s", sid)]
        p = meta[sid]["ParentId"]
        while p and p != "NULL":
            ch.append(("s", p))
            p = meta[p]["ParentId"]
        parents_of.append(ch)
    hier = _tree(K, parents_of, lambda p: p[1] if len(p) > 1 else p[0], lambda p: p[2] if len(p) > 2 else p[-1])
    log(f"Eedi: {K} level-3 subjects; sibling groups {hier.groups.max() + 1}, coarse {hier.coarse.max() + 1}")
    return data, labels, hier


def load_assist():
    data, labels = V.load_assist()
    return data, labels, Hier()


# ---------------------------------------------------------------- fitting

def derange_within(strata, rng):
    """A permutation with no fixed point inside each stratum of size >= 2 (singletons stay)."""
    perm = np.arange(len(strata))
    for s in np.unique(strata):
        idx = np.nonzero(strata == s)[0]
        if len(idx) < 2:
            continue
        while True:
            p = rng.permutation(len(idx))
            if np.all(p != np.arange(len(idx))):
                break
        perm[idx] = idx[p]
    return perm


def shuffled(pr: S.Prior, perm) -> S.Prior:
    """Correlations of pr with labels permuted, each skill keeping its own variance."""
    sd = np.sqrt(pr.diag())
    f = sd / sd[perm]
    return S.Prior("dense", pr.mu, pr.D[perm] * f ** 2, W=pr.W[perm] * f[:, None], name="shuffled")


def cold_ll(P, at):
    p = np.clip(P[at.cold], 1e-9, 1 - 1e-9)
    y = at.y[at.cold]
    return float(-(y * np.log(p) + (1 - y) * np.log1p(-p)).mean())


def fit_all(data: C.Data, hier: Hier):
    K = int(data.df.k.max()) + 1
    train = data.rows("train")
    info = {}
    asy = C.fit_asymptotes(data, train)
    base = E.engine_params(data.is_mc, data.m).replace(c=asy["c"], d=asy["d"], mode="know", eff="post")
    c0 = C.fit_ab(data.events(train), base, data.group).replace(name="C0")
    log("C0 (E5-decay) fitted")
    at_tr = S.Attempts(data, train)
    a, b, th, beta = S.static_items(at_tr, asy["c"], asy["d"], data.group, data.I, log=log)
    items1 = (a, b, asy["c"], asy["d"], beta)
    cl = S.cells(at_tr, th, a, b, asy["c"], asy["d"], K, beta)
    log(f"cells: {cl['n']:,} kept, {cl['dropped']:,} dropped (information < {S.MIN_J}); practice slope {beta:.3f}")
    uid = np.asarray(data.uid)
    val_learner = np.array([hsh(u, 4, "gsrank") == 0 for u in uid])
    vm = val_learner[at_tr.learners][cl["l"]]
    cl_fit = {k_: (v_[~vm] if isinstance(v_, np.ndarray) else v_) for k_, v_ in cl.items()}
    at_val = S.Attempts(data, train & val_learner[data.df.l.to_numpy()])
    score = {}
    for r in RANKS:
        pr, _ = S.fit_dense(cl_fit, r)
        if r == 0:
            pr = S.Prior("dense", pr.mu, pr.D, W=np.zeros((K, 1)))
        score[r] = cold_ll(S.run_gauss(at_val, pr, items1, K)["P"], at_val)
        log(f"   rank {r}: validation cold-attempt log loss {score[r]:.5f} ({int(at_val.cold.sum()):,} attempts)")
    r_star = min(score, key=score.get)
    info["rank_cold_logloss"] = score
    info["rank"] = r_star
    P = {}
    pr2, tr2 = S.fit_dense(cl, r_star, log=log)
    if r_star == 0:
        pr2 = S.Prior("dense", pr2.mu, pr2.D, W=np.zeros((K, 1)), name="C2 (r = 0)")
    P["C2"] = pr2
    info["em_trace_C2"] = [float(x) for x in tr2[::5]] + [float(tr2[-1])]
    P["C2-diag"] = S.Prior("dense", pr2.mu, pr2.diag(), W=np.zeros((K, 1)), name="C2-diag")
    n_k = np.bincount(cl["k"], None, K)
    dec = np.searchsorted(np.quantile(n_k, np.linspace(0, 1, 11)[1:-1]), n_k, side="right")
    rng = np.random.default_rng(SEED + 3)
    for j in range(N_SHUF):
        perm = derange_within(dec, rng)
        P[f"C2-shuf{j}"] = shuffled(pr2, perm)
    P["C2g"] = pr2 if r_star == 1 else S.fit_dense(cl, 1)[0]
    if hier.groups is not None:
        G = int(hier.groups.max()) + 1
        P["C3"], _ = S.fit_arrow(cl, hier.groups, G, general=False, groups=True, name="C3", log=log)
        P["C3g"], _ = S.fit_arrow(cl, hier.groups, G, general=True, groups=True, name="C3g", log=log)
        Gc = int(hier.coarse.max()) + 1
        P["C3c"], _ = S.fit_arrow(cl, hier.coarse, Gc, general=False, groups=True, name="C3c", log=log)
    log("priors fitted: " + ", ".join(P))
    items = {}
    for name, pr in P.items():
        items[name] = S.refit_items(at_tr, pr, items1, K, data.group, data.I)
        log(f"   items refitted for {name}: practice slope {items[name][4]:.3f}")
    info["prior_summary"] = {k_: prior_summary(v_) for k_, v_ in P.items() if not k_.startswith("C2-shuf")}
    info["cells"] = {"kept": cl["n"], "dropped": cl["dropped"], "skills": K,
                     "skills_below_min_cells": int((n_k < S.MIN_CELLS).sum())}
    info["stage1"] = {"median_a": float(np.median(a)), "median_b": float(np.median(b)), "practice_slope": float(beta)}
    info["practice_slope_refit"] = {k_: float(v_[4]) for k_, v_ in items.items()}
    return c0, items, P, info


def prior_summary(pr: S.Prior) -> dict:
    """Aggregates only: variance shares and mean correlations."""
    dg = pr.diag()
    dp = pr.as_dense() if pr.kind == "arrow" and pr.G < 600 else pr
    out = {"mean_var": float(dg.mean()), "mean_unique_share": float((pr.D / dg).mean())}
    if dp.kind == "dense":
        Wn = dp.W / np.sqrt(dg)[:, None]
        Rm = Wn @ Wn.T
        K = len(dg)
        off = ~np.eye(K, dtype=bool)
        out["mean_corr"] = float(Rm[off].mean())
        out["mean_abs_corr"] = float(np.abs(Rm[off]).mean())
        ev = np.linalg.eigvalsh(Rm + np.diag(pr.D / dg))[::-1]
        out["top_eigen_share"] = [float(x) for x in (ev[:5] / ev.sum())]
    return out


# ---------------------------------------------------------------- replay on TEST

def predict(data: C.Data, hier: Hier, c0, items, P):
    K = int(data.df.k.max()) + 1
    test = data.rows("test")
    at = S.Attempts(data, test)
    err = S.beta_check(data, at, c0, test)
    assert err < 1e-9, f"run_beta differs from engine.replay by {err}"
    log(f"TEST: {at.n:,} attempts, {at.nl:,} learners, {int(at.cold.sum()):,} cold; run_beta = engine.replay to {err:.1e}")
    pred, extra = {}, {}
    ob = S.run_beta(at, c0, K, record=True)
    pred["C0"] = ob["P_own"]
    extra["C0"] = (ob["alpha"], ob["beta"])
    if hier.chain is not None:
        o1 = S.run_beta(at, c0, K, chain=hier.chain)
        pred["C1"], pred["C1-engine"] = o1["P_read"], o1["P_own"]
    for name, pr in P.items():
        o = S.run_gauss(at, pr, items[name], K)
        pred[name] = o["P"]
        extra[name] = (o["m"], o["v"])
        log(f"   filter {name} done")
    base = V.baselines(data)
    pred["PFA-lite"] = base["PFA-lite"][at.gid]
    A = data.df.drop_duplicates("attempt").sort_values("attempt")
    tr = ~data.test_l[A.l.to_numpy()]
    lg, _, _ = e2e.difficulty(A.i.to_numpy(), A.y.to_numpy().astype(np.int64), tr)
    clim = np.empty(int(A.attempt.max()) + 1)
    clim[A.attempt.to_numpy()] = 1 / (1 + np.exp(-lg.astype(float)))
    pred["CLIM"] = clim[at.gid]
    return at, pred, extra


# ---------------------------------------------------------------- metrics

def windows(at: S.Attempts):
    """Windows of WIN consecutive single-skill attempts on one skill: cold (rows 0..4), warm (3..7)."""
    single = np.nonzero(at.nS == 1)[0]
    df = pd.DataFrame({"a": single, "l": at.l[single], "k": at.S[single, 0], "r": at.R[single, 0]})
    out = {}
    for name, r0 in (("cold", 0), ("warm", 3)):
        sub = df[(df.r >= r0) & (df.r < r0 + WIN)]
        g = sub.groupby(["l", "k"])
        full = g.r.transform("size") == WIN
        sub = sub[full.to_numpy()].sort_values(["l", "k", "r"])
        idx = sub.a.to_numpy().reshape(-1, WIN)
        out[name] = idx
    return out


def _poibin(Pm):
    """Pm (..., WIN) -> pmf of the count (..., WIN + 1)."""
    f = np.zeros(Pm.shape[:-1] + (WIN + 1,))
    f[..., 0] = 1
    for j in range(WIN):
        p = Pm[..., j:j + 1]
        f = np.concatenate([f[..., :1] * (1 - p), f[..., 1:] * (1 - p) + f[..., :-1] * p], -1)
    return f


def pit(at, win, kind, state, prm_items):
    """Randomised PIT of each window's count under the variant's state at the window start."""
    a, b, c, d, beta = prm_items
    it = at.i[win]
    y = at.y[win].sum(1).astype(int)
    first = win[:, 0]
    ai, bi, ci, di = a[it], b[it], c[it], d[it]
    if kind == "gauss":
        m, v = state[0][first], state[1][first]
        x, w = np.polynomial.hermite_e.hermegauss(20)
        w = w / w.sum()
        th = m[:, None] + np.sqrt(np.maximum(v, 0))[:, None] * x[None]
        off = (beta * at.x[win])[:, None]
        Pm = ci[:, None] + (di - ci)[:, None] * S.sigmoid(ai[:, None] * (th[:, :, None] + off - bi[:, None]))
    else:
        from scipy.stats import beta as betad
        al, be = state[0][first], state[1][first]
        qs = (np.arange(20) + 0.5) / 20
        p = np.clip(betad.ppf(qs[None], al[:, None], be[:, None]), 1e-6, 1 - 1e-6)
        th = np.log(p / (1 - p))
        w = np.full(20, 1 / 20)
        Pm = ci[:, None] + (di - ci)[:, None] * S.sigmoid(ai[:, None] * (th[:, :, None] - bi[:, None]))
    pmf = (_poibin(Pm) * w[None, :, None]).sum(1)
    cdf = np.cumsum(pmf, 1)
    lo = np.where(y > 0, cdf[np.arange(len(y)), np.maximum(y - 1, 0)], 0.0)
    hi = cdf[np.arange(len(y)), y]
    u = np.random.default_rng(SEED + 11).random(len(y))
    return lo + u * (hi - lo)


def evaluate(at: S.Attempts, pred, extra, c0, items):
    nl = at.nl
    y = at.y
    grp = at.l
    subsets = {"all": np.ones(at.n, bool), "cold": at.cold}
    for name, lo, hi in BINS:
        subsets[name] = at.warm & (at.gap_min >= lo * S.DAY) & (at.gap_min < hi * S.DAY)
    counts = {k: int(v.sum()) for k, v in subsets.items()}
    log("subset sizes: " + json.dumps(counts))
    Ms = {}
    for sk, msk in subsets.items():
        for vn, p in pred.items():
            Ms[(sk, vn)] = V.Metrics(p[msk], y[msk], grp[msk], nl, bins=True)
    win = windows(at)
    cov = {}
    for wn, idx in win.items():
        wl = at.l[idx[:, 0]]
        for vn in list(pred):
            if vn == "C0":
                u = pit(at, idx, "beta", extra["C0"], (c0.a, c0.b, c0.c, c0.d, 0.0))
            elif vn in extra:
                u = pit(at, idx, "gauss", extra[vn], items[vn])
            else:
                continue
            cov[(wn, vn)] = np.stack([np.bincount(wl, (np.abs(u - 0.5) <= q / 2).astype(float), nl) for q in LEVELS], 1)
        cov[(wn, "_n")] = np.bincount(wl, None, nl)
    counts.update({f"windows_{k}": int(len(v)) for k, v in win.items()})

    def one(w):
        r = {vn: {} for vn in pred}
        for (sk, vn), m in Ms.items():
            res = m.all(w, RISKS if sk == "all" else ())
            for kk, vv in res.items():
                r[vn][f"{sk}_{kk}"] = vv
        for (wn, vn), c in cov.items():
            if vn == "_n":
                continue
            den = w @ cov[(wn, "_n")]
            for j, q in enumerate(LEVELS):
                r[vn][f"cover_{wn}_{q}"] = float(w @ c[:, j] / den) if den else float("nan")
        for vn in pred:
            for sk in subsets:
                r[vn][f"{sk}_skill"] = 1 - r[vn][f"{sk}_logloss"] / r["CLIM"][f"{sk}_logloss"]
        shuf = [k for k in pred if k.startswith("C2-shuf")]
        if shuf:
            r["C2-shuf"] = {kk: float(np.mean([r[s][kk] for s in shuf])) for kk in r[shuf[0]]}
        return r

    point = one(np.ones(nl))
    rng = np.random.default_rng(SEED)
    draws = {k: [] for k in point}
    for bi in range(BOOT):
        w = np.bincount(rng.integers(0, nl, nl), minlength=nl).astype(float)
        r = one(w)
        for k in point:
            draws[k].append(r[k])
        if bi % 50 == 49:
            log(f"   bootstrap {bi + 1}/{BOOT}")
    return {"point": point, "draws": draws, "counts": counts}


def ci(ev, var, base, key, sign=+1):
    return V.contrast(ev, var, base, key, sign)


def ratio_ci(ev, num, den, base, key):
    """(base - num) / (base - den) on `key`, point and percentile interval."""
    p = ev["point"]
    est = (p[base][key] - p[num][key]) / (p[base][key] - p[den][key])
    dr = V._transpose(ev["draws"])
    vals = np.array([(d[base][key] - d[num][key]) / (d[base][key] - d[den][key]) for d in dr])
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return {"est": float(est), "lo": float(lo), "hi": float(hi)}


def verdicts(ev, has_graph, floor=None) -> dict:
    p = ev["point"]
    res = {"counts": ev["counts"]}
    vs = [v for v in p if v not in ("C0",)]
    res["M1_gain_vs_C0"] = {v: ci(ev, v, "C0", "cold_logloss") for v in vs}
    res["M1_auc_gain_vs_C0"] = {v: ci(ev, v, "C0", "cold_auc", -1) for v in vs}
    res["M2_gain_vs_C0"] = {v: ci(ev, v, "C0", "all_logloss") for v in vs}
    res["M2_auc_gain_vs_C0"] = {v: ci(ev, v, "C0", "all_auc", -1) for v in vs}
    res["M5_items_saved"] = {v: {str(r): ci(ev, v, "C0", f"all_unneeded_{r}") for r in RISKS} for v in vs}
    g2 = res["M1_gain_vs_C0"]["C2"]
    over_diag = ci(ev, "C2", "C2-diag", "cold_logloss")
    over_shuf = ci(ev, "C2", "C2-shuf", "cold_logloss")
    res["C2_over_C2diag_M1"], res["C2_over_C2shuf_M1"] = over_diag, over_shuf
    if ev["counts"]["cold"] < MIN_COLD:
        cp = "UNANSWERABLE (fewer than %d cold attempts)" % MIN_COLD
    elif g2["lo"] > 0:
        cp = "COUPLING HELPS COLD NODES" if over_diag["lo"] > 0 else "C2 HELPS COLD NODES, NOT BY COUPLING"
    else:
        cp = "NO COUPLING GAIN"
    res["coupling"] = cp
    res["which_skills"] = "WHICH SKILLS CO-VARY MATTERS" if over_shuf["lo"] > 0 else "GENERAL LEVEL ONLY"
    if has_graph:
        rt = ratio_ci(ev, "C3", "C2", "C2-diag", "cold_logloss")        # CHANGE 1: the coupling part
        res["graph_retention"] = rt
        res["graph_retention_vs_C0_as_registered"] = ratio_ci(ev, "C3", "C2", "C0", "cold_logloss")
        if cp == "COUPLING HELPS COLD NODES":
            gv = "GRAPH CARRIES THE COUPLING" if rt["est"] >= 0.5 else "EMPIRICAL COVARIANCE ONLY"
        else:
            gv = "NO COUPLING GAIN"
        if floor is not None and floor.get("H_retention", 0) >= 0.5 and gv == "GRAPH CARRIES THE COUPLING":
            gv += " (not diagnostic: a general factor seen through siblings also passes)"
        res["graph"] = gv
        res["C3g_over_C2g_M1"] = ci(ev, "C3g", "C2g", "cold_logloss")
        res["C3_over_C2diag_M1"] = ci(ev, "C3", "C2-diag", "cold_logloss")
        if "C1" in p:
            g1 = res["M1_gain_vs_C0"]["C1"]
            res["C1"] = "PARENT READ HELPS COLD NODES" if g1["lo"] > 0 else "PARENT READ DOES NOT HELP COLD NODES"
    else:
        res["graph"] = "NOT TESTABLE (no hierarchy)"
    m2 = res["M2_gain_vs_C0"]["C2"]
    res["guard_M2"] = ("C2 WORSENS NEXT-ATTEMPT" if m2["hi"] < 0 else
                       "C2 IMPROVES NEXT-ATTEMPT" if m2["lo"] > 0 else "C2 DOES NOT WORSEN NEXT-ATTEMPT")
    # M3 horizon
    hz = {}
    for v in p:
        if v == "CLIM":
            continue
        rows = {}
        run = True
        last = None
        for name, _, _ in BINS:
            key = f"{name}_skill"
            d = np.array([dr[key] for dr in ev["draws"][v]])
            lo_, hi_ = np.percentile(d, [2.5, 97.5])
            rows[name] = {"skill": float(p[v][key]), "lo": float(lo_), "hi": float(hi_),
                          "relative_to_h0": float(p[v][key] / p[v]["h0_skill"]) if p[v]["h0_skill"] else None}
            if run and lo_ > 0:
                last = name
            else:
                run = False
        rows["horizon"] = {"h0": "< 1 day", "h1": "1-7 days", "h7": "7-30 days", "h30": ">= 30 days", None: "none"}[last]
        if v != "C0":
            for name, _, _ in BINS:
                rows[name]["gain_vs_C0"] = ci(ev, v, "C0", f"{name}_logloss")
        hz[v] = rows
    res["M3_horizon"] = hz
    # M4
    cal = {}
    for v in p:
        row = {"ece_cold": p[v]["cold_ece"], "ece_all": p[v]["all_ece"]}
        for wn in ("cold", "warm"):
            key0 = f"cover_{wn}_0.5"
            if key0 in p[v]:
                cv = {str(q): p[v][f"cover_{wn}_{q}"] for q in LEVELS}
                dev = [cv[str(q)] - q for q in LEVELS]
                row[f"coverage_{wn}"] = cv
                row[f"intervals_{wn}"] = ("OVER-CONFIDENT" if min(dev) < -0.05 else "UNDER-CONFIDENT" if max(dev) > 0.05
                                          else "CALIBRATED INTERVALS")
        cal[v] = row
    res["M4_calibration"] = cal
    res["M4_ece_change_vs_C0"] = {v: {"cold": ci(ev, v, "C0", "cold_ece", -1), "all": ci(ev, v, "C0", "all_ece", -1)}
                                  for v in ("C2", "C3") if v in p}
    res["point"] = p
    return res


# ---------------------------------------------------------------- runs

def run(name, data, hier, floor=None):
    log(f"{name}: {len(data.df):,} rows, {data.df.attempt.nunique():,} attempts, {len(data.uid):,} learners, "
        f"{data.I:,} items, {int(data.df.k.max()) + 1} skills")
    c0, items, P, info = fit_all(data, hier)
    at, pred, extra = predict(data, hier, c0, items, P)
    ev = evaluate(at, pred, extra, c0, items)
    res = verdicts(ev, hier.groups is not None, floor)
    res["fit"] = info
    res["data"] = {"rows": int(len(data.df)), "attempts": int(data.df.attempt.nunique()), "learners": int(len(data.uid)),
                   "items": int(data.I), "skills": int(data.df.k.max()) + 1, "test_attempts": int(at.n),
                   "test_learners": int(at.nl)}
    report(name, res)
    return res


def report(name, res):
    log(f"== {name}: {res['coupling']} | {res['graph']} | {res['which_skills']} | {res['guard_M2']} | "
        f"rank {res['fit']['rank']}")
    for v, g in res["M1_gain_vs_C0"].items():
        m2 = res["M2_gain_vs_C0"][v]
        log(f"   {v:<10} M1 {g['est']:+.4f} [{g['lo']:+.4f}, {g['hi']:+.4f}]   M2 {m2['est']:+.4f} [{m2['lo']:+.4f}, {m2['hi']:+.4f}]"
            f"   horizon {res['M3_horizon'].get(v, {}).get('horizon', '-')}")
    if "graph_retention" in res:
        r = res["graph_retention"]
        log(f"   C3 retention {r['est']:.3f} [{r['lo']:.3f}, {r['hi']:.3f}]")


def floor_record():
    f = OUT / "synthetic.json"
    if not f.exists():
        return {"passes": False, "H_retention": 0.0}
    s = json.loads(f.read_text())
    return {"passes": s["passes"], "H_retention": s.get("H_retention", 0.0)}


def floor_complete():
    """The floor's last write: `complete`, or (a run launched before that flag existed) all 7 worlds
    written and the file untouched for a minute (its final write follows the last world's at once)."""
    f = OUT / "synthetic.json"
    if not f.exists():
        return False
    s = json.loads(f.read_text())
    return bool(s.get("complete")) or (len(s.get("worlds", [])) == 7 and time.time() - f.stat().st_mtime > 60)


def real(name):
    loader = {"xes": load_xes, "eedi": load_eedi, "assist": load_assist}[name]
    data, labels, hier = loader()
    res = run(name, data, hier)
    del data
    while not floor_complete():
        log("waiting for the synthetic floor to finish")
        time.sleep(120)
    fl = floor_record()
    if (fl["H_retention"] >= 0.5 and res["graph"] == "GRAPH CARRIES THE COUPLING"):
        res["graph"] += " (not diagnostic: a general factor seen through siblings also passes)"
    if not fl["passes"]:
        for k_ in ("coupling", "graph", "which_skills", "guard_M2"):
            res[k_] += " (UNCALIBRATED)"
    res["floor"] = fl
    OUT.mkdir(exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(res, indent=1, default=float) + "\n")


# ---------------------------------------------------------------- synthetic worlds

def world(kind, seed, L=3000):
    rng = np.random.default_rng(SEED + 1000 * "GEIH".index(kind) + seed)
    K, per_g, G = 60, 4, 15
    grp = np.arange(K) // per_g
    coarse = grp // 5
    same = grp[:, None] == grp[None, :]
    if kind == "G":
        Sig = 0.48 * np.eye(K) + 0.72 * same
    elif kind == "E":
        W = rng.normal(0, 0.55, (K, 2))
        Sig = W @ W.T + 0.6 * np.eye(K)
    elif kind == "H":
        w = rng.normal(0.85, 0.1, K)
        Sig = np.outer(w, w) + 0.48 * np.eye(K)
    else:
        Sig = 1.2 * np.eye(K)
    ch = np.linalg.cholesky(Sig)
    beta_k = rng.normal(-0.8, 0.6, K)
    skills = [[k] for k in range(K) for _ in range(8)]
    for k in range(K):
        o = rng.choice(np.nonzero(same[k] & (np.arange(K) != k))[0]) if rng.random() < 0.5 else rng.choice(np.delete(np.arange(K), k))
        skills.append([k, int(o)])
    I = len(skills)
    b = np.array([beta_k[s].mean() for s in skills]) + rng.normal(0, 0.7, I)
    a = np.exp(rng.normal(0, 0.25, I))
    is_mc = rng.random(I) < 0.5
    m = np.where(is_mc, 4, 0)
    c = np.where(is_mc, rng.uniform(0.1, 0.3, I), rng.uniform(0.02, 0.08, I))
    dd = 1 - rng.uniform(0, 0.04, I)
    items_of = [[] for _ in range(K)]
    multi_of = [[] for _ in range(K)]
    for i, s in enumerate(skills):
        for k in s:
            (items_of if len(s) == 1 else multi_of)[k].append(i)
    rows = ([], [], [], [], [], [])
    aid = 0
    for u in range(L):
        th = ch @ rng.normal(size=K)
        gain = np.zeros(K)
        last = np.full(K, -1.0)
        order = [k for g in rng.permutation(G) for k in rng.permutation(np.nonzero(grp == g)[0])]
        seen, nxt = [], 0
        t = 0.0
        for _ in range(int(rng.integers(20, 45))):
            t += math.exp(rng.uniform(math.log(3600), math.log(40 * 86400)))
            if (seen and rng.random() < 0.35) or nxt >= K:
                k = int(rng.choice(seen))
            else:
                k = int(order[nxt])
                nxt += 1
                seen.append(k)
            for j in range(int(rng.integers(4, 9))):
                tt = t + 60.0 * j
                pool = multi_of[k] if (multi_of[k] and rng.random() < 0.2) else items_of[k]
                i = int(rng.choice(pool))
                sk = skills[i]
                for s_ in sk:
                    if last[s_] >= 0:
                        gain[s_] *= (1 + (tt - last[s_]) / 86400) ** (-0.5)
                te = np.mean([th[s_] + gain[s_] for s_ in sk])
                P = c[i] + (dd[i] - c[i]) / (1 + math.exp(-a[i] * (te - b[i])))
                yv = float(rng.random() < P)
                for s_ in sk:
                    gain[s_] += 0.15
                    last[s_] = tt
                    for arr, val in zip(rows, (u, i, s_, yv, tt, aid)):
                        arr.append(val)
                aid += 1
    li, ii, kk, yy, tt, oo = (np.array(x) for x in rows)
    group = np.where(is_mc, 0, 1)
    data = C.Data(li, ii, kk, yy, tt, oo, is_mc, m, group, np.array([f"gs{kind}{seed}-{u}" for u in range(L)]))
    chain = np.full((K + G + 4, 3), -1, np.int64)
    chain[:K, 0] = K + grp
    chain[:K, 1] = K + G + coarse
    chain[:K, 2] = K + G + 3
    return data, Hier(grp.astype(np.int64), coarse.astype(np.int64), chain)


def synthetic():
    out = {"worlds": [], "passes": True}
    checks_all = []
    for kind, seeds in (("G", 2), ("E", 2), ("I", 2), ("H", 1)):
        for sd in range(seeds):
            data, hier = world(kind, sd)
            res = run(f"world {kind} seed {sd}", data, hier)
            g = res["M1_gain_vs_C0"]["C2"]
            ck = {"not_worse_M2": not res["guard_M2"].startswith("C2 WORSENS")}
            if kind == "G":
                ck.update({"coupling": res["coupling"] == "COUPLING HELPS COLD NODES",
                           "graph": res["graph"].startswith("GRAPH CARRIES"),
                           "beats_shuffled": res["C2_over_C2shuf_M1"]["lo"] > 0})
            elif kind == "E":
                ck.update({"coupling": res["coupling"] == "COUPLING HELPS COLD NODES",
                           "graph": res["graph"] == "EMPIRICAL COVARIANCE ONLY"})
            elif kind == "I":       # CHANGE 2: no false COUPLING verdict; C2's gain over C0 is reported
                ck.update({"no_false_coupling": res["coupling"] != "COUPLING HELPS COLD NODES",
                           "no_false_over_diag": res["C2_over_C2diag_M1"]["lo"] <= 0})
            else:
                out["H_retention"] = res["graph_retention"]["est"]
                ck = {}
            rec = {"world": kind, "seed": sd, "checks": ck, "C2_gain_vs_C0_M1": g, "coupling": res["coupling"], "graph": res["graph"],
                   "which_skills": res["which_skills"], "guard_M2": res["guard_M2"], "rank": res["fit"]["rank"],
                   "M1_gain_vs_C0": res["M1_gain_vs_C0"], "M2_gain_vs_C0": res["M2_gain_vs_C0"],
                   "graph_retention": res.get("graph_retention"), "C2_over_C2diag_M1": res["C2_over_C2diag_M1"],
                   "C2_over_C2shuf_M1": res["C2_over_C2shuf_M1"], "M4_calibration": res["M4_calibration"],
                   "M3_horizon": {v: r["horizon"] for v, r in res["M3_horizon"].items()},
                   "counts": res["counts"], "rank_cold_logloss": res["fit"]["rank_cold_logloss"]}
            out["worlds"].append(rec)
            checks_all += list(ck.values())
            log(f"   checks {ck}")
            OUT.mkdir(exist_ok=True)
            (OUT / "synthetic.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    out["passes"] = bool(all(checks_all))
    out["complete"] = True
    (OUT / "synthetic.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    log(f"FLOOR {'PASSES' if out['passes'] else 'FAILS'}; world H C3 retention {out.get('H_retention')}")


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "synthetic":
        synthetic()
    else:
        real(what)
