"""PRE-REGISTERED: does XES3G5M's own expert KC-route tree beat a deranged tree of the same shape?

QUESTION
    The XES3G5M dataset paper (Liu et al., NeurIPS 2023 Datasets and Benchmarks; literature review
    for Paper II, strand 5, entry 5.9) reports that adding the dataset's "KC routes" (a taxonomy
    tree the authors say "explicitly introduces the prerequisite relations" among KCs) to
    knowledge-tracing models adds nothing, or slightly hurts, once question and KC content are in
    (simpleKT early fusion 0.8277 -> 0.8262; AKT 0.8292 -> 0.8290). That null has no control: it
    cannot say whether the tree carries nothing a random tree of the same shape would not. Paper II's
    F5 (studies/end-to-end/xes3g5m-build/e2e.py, out/result.json) found that LLM-built edges add the
    same as shuffled or reversed ones. This asks the same question of the platform's expert tree:
    within e2e.py's modelling framework, does the real tree beat a deranged tree of the same shape?
    Literature: review ranked analysis 9 and strand-5 "Analyses" item 4 (5.9); the random-graph
    precedent 5.x (Kim et al. 2023, expert minus random 0.0020 AUC, no variance); the item-difficulty
    caveat 5.14 (Effenberger et al. 2020) is met because every arm carries e2e.py's per-question
    difficulty offset.

WRITTEN 2026-10-07, before any statistic of this design was computed on XES3G5M learner data. The
    analyst has read e2e.py's published AUCs (M1 0.7919, M2 0.7965, M4 - M4s +0.00015) and, to design
    the tree arms, the shape of the KC-route tree (metadata only: 866 KCs; route lengths 2-7; 172
    depth-3 prefixes; 555 KCs have a KC ancestor on their route, mean 1.015; 85 KCs have a KC
    descendant; 705 KCs have a non-empty route family, mean 8.1 KCs). No learner response was read.

DATA (reads a corpus): through shared.paths.data_path("XES_DIR") -- attempts.tsv (uid, question,
    KC ids, response, start time in ms; the ingest's reconstruction) and cid2route.json (KC id ->
    route). XES3G5M is research-use; raw data stays in the scratchpad, only aggregates are written
    to out/. No KC names, question text or learner-level rows are written. No model call. No derived
    file is written to disk.

DIRECTION: "a -> b" means a is a direct prerequisite of b; for the tree, a is the nearest KC that
    lies above b on b's KC route (the route's parent link, contracted over route nodes that are not
    KCs), per the XES3G5M authors' reading of the route as prerequisite relations (paper §3, quoted in
    the literature review entry 5.9). The reversed-arrow control is Tr (features from KC children
    instead of KC parents), scored through shared.direction.reversed_arrow, reported, not
    verdict-bearing.

FRAMEWORK (e2e.py's, imported where possible, not modified)
    split      TRAIN/TEST by sha256(uid): first 8 hex digits mod 5 == 0 is TEST (e2e.py SPLIT).
    offset     off = logit of the question's shrunk TRAIN success rate (e2e.difficulty, imported).
    fit        logistic regression by IRLS (e2e.fit_logistic, e2e.predict, imported).
    AUC        weighted AUC with ties under learner-bootstrap weights (e2e.AUC, imported).
    bootstrap  paired learner bootstrap over TEST learners, B = 200, rng seeded with e2e.SEED, the
               draws taken in e2e.kt_compare's order; e2e.diff, e2e.beats, e2e.BEATS = +0.001
               imported. The resampled unit is the TEST learner, the unit the split assigns.
    features   COPIED, not imported, with a note: e2e.features walks every row once per Q-matrix and
               edge set and rebuilds each question's parent set on every row, and load_attempts holds
               5.49M Python tuples; at 15 P blocks that would exceed this run's 3 GB budget and take
               hours on a shared core. features_lean() computes the same U, K and P columns (same
               definitions, float32, same list semantics for repeated tags) with per-question parent
               sets precomputed, and load_lean() returns arrays in e2e.load_attempts' order (uid
               string, start time, line number). Equality with e2e.features is ASSERTED on a
               synthetic world in --synthetic, and the real run asserts that it reproduces e2e.py's
               published M1 and M2 AUCs to within 1e-6 before any tree arm is scored (it stops
               otherwise).
    Q-matrix   K = the expert leaf KCs of each question (e2e.py's M2: the KC ids attempts.tsv gives
               the question on its first row in that order, kept if in cid2route.json).

TREE ARMS (all P blocks on the expert KC Q-matrix, e2e.py's P definition: mean over the set of
    log1p(prior successes), log1p(prior failures), plus an indicator for an empty set; the set is the
    union over the question's KCs, minus the question's own KCs)
    T     REAL TREE. pre(b) = the KC(s) on the nearest route node above b's that holds a KC (the
          tree's parent link contracted to KCs: a forest of 866 KCs, 311 roots).
    Td_i  DERANGED TREE, i = 0..4 (five independent derangements, seeds e2e.SEED + 900 + i). The
          contracted forest's child-parent slots are permuted among children so that every non-root
          KC keeps being a child, every parent keeps its exact number of children, and no KC keeps
          its real parent (asserted; also no self-link and no reversed real link). Family-matched by
          depth: a child is moved only among children with the same route depth whose real parents
          have the same route depth, so every edge keeps its (parent depth, child depth). If a group
          cannot be deranged (e.g. one parent only) keeps its real slots for a moment; those
          children are then repaired by swapping slots with any child of the same route depth, then
          with any child, every swap keeping both sides valid and parent depth < child depth (so the
          result is acyclic). The counts left after each stage and the number of edges whose parent
          depth changed are reported (on the real tree: 17 after stage 1, 3 after stage 2, 0 after
          stage 3; 0-4 of 559 edges change parent depth -- computed from cid2route.json alone,
          before the design commit). Same edge count, same out-degrees, same set of child KCs, so
          the share of questions with a non-empty P set is the same as T's (up to a KC with two
          parents on one shared route node drawing the same new parent twice).
    Tr    REVERSED TREE: every edge of T reversed (pre(a) = a's KC children).
    SECONDARY, the route family (closer to what route text does in the authors' embeddings: pool
    related KCs):
    F     FAMILY. pre(k) = the KCs in the subtree of the parent route node of k's route node, minus
          those in the subtree of k's own route node (siblings and their descendants).
    Fd_j  DERANGED ROUTE TREE, j = 0..2 (seeds e2e.SEED + 950 + j): at every route depth d >= 2 the
          route nodes of depth d are permuted among the parent slots of depth d - 1 so that no route
          node keeps its real parent (asserted) and every route node keeps its out-degree and depth;
          families are recomputed under the new parent links.

MODELS    M1 = off + U; M2 = off + U + K; X = off + U + K + P[X] for X in T, Td_0..4, Tr, F, Fd_0..2.
          Td-bar = the mean AUC of Td_0..4 (per bootstrap draw); Fd-bar likewise over Fd_0..2.

SIZE CHECK (shared.controls.check_control_scale): size of an arm = the share of TEST attempts whose
    P set holds at least one prior attempt. Treatment T, controls Td_0..4 (and Tr reported). If no
    deranged arm reaches 0.5 x T's coverage the control is too small and the primary verdict reads
    "CONTROL TOO SMALL" instead of any comparison. Same for F against Fd.

VERDICTS (signed; the bar is e2e.py's +0.001 on the 95% learner-bootstrap interval)
  V1 (primary) T vs Td-bar, interval [lo, hi] of AUC(T) - AUC(Td-bar):
     TREE BEATS ITS DERANGEMENT            lo > +0.001
     TREE EQUIVALENT TO ITS DERANGEMENT    lo > -0.001 and hi < +0.001  (a controlled null)
     DERANGEMENT BEATS THE TREE            hi < -0.001
     TREE NOT SHOWN BETTER THAN ITS DERANGEMENT   otherwise
     UNANSWERABLE (tree floor fails)       if the synthetic floor below fails
  V2 (e2e.py's edge verdict, for comparability with F5):
     TREE CARRIES SPECIFIC SIGNAL  T beats M2 and T beats Td-bar; TREE ADDS SIGNAL, NOT SPECIFIC
     T beats M2 only; TREE ADDS NOTHING  T does not beat M2. UNANSWERABLE if the floor fails.
  V3 (secondary) F vs Fd-bar with V1's four strings ("FAMILY ..."), gated by the family floor.
  Direction: T vs Tr through reversed_arrow plus the interval of AUC(T) - AUC(Tr); reported only.
  Cold start (descriptive, F5's sibling-group finding is at first attempts on a new skill): every
     AUC and the V1/V3 contrasts recomputed on TEST attempts where the learner has no prior attempt
     on any of the question's KCs, same bootstrap draws.

SYNTHETIC FLOOR (--synthetic; no corpus). e2e.py's sim_world, adapted to a tree: 3 module route nodes
    that hold no KC; 30 KCs, KC j attached to a random module with probability 0.35 (the real share
    of contracted-forest roots is 311/866 = 0.36) else to a random earlier KC; 5 questions per KC,
    difficulty N(0, 0.7); 3,000 learners, theta N(0, 1), visiting KCs in noisy index order
    (index + N(0, 6)), 4-6 attempts each; mastery m += 0.25 (1 - m) per attempt;
    logit P = theta - b + 1.5 m + gamma (g - 0.5).
    Worlds: planted-parent (g = mastery of the KC parent, 0.5 if none; gamma 2; 5 worlds),
    planted-family (g = mean mastery over the route family, 0.5 if empty; gamma 2; 5 worlds),
    null (gamma 0; 10 worlds). A random tree that cannot be deranged under the constraints above
    at all eight seeds (a hub holding most child slots) is redrawn from the same generator, and the
    redraws are counted. The arms, derangements, fits and bootstrap are the real run's code.
    TREE FLOOR PASSES if T beats Td-bar in >= 4 of 5 planted-parent worlds, in <= 1 of 10 null
    worlds, and M2 beats M1 in every planted world. FAMILY FLOOR PASSES if F beats Fd-bar in >= 4 of
    5 planted-family worlds and in <= 1 of 10 null worlds. The lean features are asserted equal to
    e2e.features on the first world.

WHAT IT CAN SAY  Whether the expert tree's parent links (and route families) carry predictive signal,
    for held-out learners' next responses, beyond a tree of the same shape with every real link
    destroyed, in a logistic model with a per-question difficulty offset and the expert Q-matrix.
WHAT IT CANNOT   It does not replicate the authors' early-fusion deep models (simpleKT, AKT with
    question-text and route-text embeddings): those need a GPU-scale PyTorch run, and this machine
    has 4 shared CPU cores and no torch; e2e.py's model is used throughout. A tree that predicts is
    not shown to be a prerequisite structure (platform order makes parent history more often present
    than child history, which is why Tr is not verdict-bearing), and prediction is not learning.

CHANGES      None to the design after the design commit (dfc8545). The floor ran after it.

RESULTS (2026-10-07; out/synthetic.json, out/result.json; README.md has the tables)
    FLOORS PASS. Tree: T beats Td-bar in 5/5 planted-parent worlds (+0.0098 to +0.0137), 0/10 null
    (every null interval inside [-0.0002, +0.0001]); M2 beats M1 in every planted world. Family: 5/5
    planted-family (+0.0043 to +0.0079), 0/10 null. Neither floor is specific to its own mechanism
    (T also beats Td-bar in 5/5 planted-family worlds, F beats Fd-bar in 5/5 planted-parent worlds).
    features_lean equals e2e.features on the first world; the real run reproduces e2e.py's M1 and M2
    AUCs exactly (difference 0.0).
    REAL: V1 TREE EQUIVALENT TO ITS DERANGEMENT, T - Td-bar +0.000037 [+0.000010, +0.000063];
    V2 TREE ADDS NOTHING, T - M2 +0.000051 [+0.000025, +0.000080]; direction CLAIMED by +0.00002
    (T - Tr interval [-0.000005, +0.000055]). V3 FAMILY EQUIVALENT TO ITS DERANGEMENT under the
    pre-registered rule, but signed and above zero: F - Fd-bar +0.000724 [+0.000638, +0.000816];
    at cold start +0.001245 [+0.001118, +0.001372] (descriptive). Peak memory 2.7 GB.

    python3 kc_tree.py --synthetic    # the floor; no corpus
    python3 kc_tree.py                # the real run (after the design commit)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E2E_DIR = ROOT / "studies/end-to-end/xes3g5m-build"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(E2E_DIR))
import e2e  # noqa: E402
from shared.controls import check_control_scale  # noqa: E402
from shared.direction import reversed_arrow  # noqa: E402
from shared.paths import data_path  # noqa: E402

OUT = HERE / "out"
N_DER = 5
N_FDER = 3
EQUIV = 0.001
MIN_COVER = 0.5


# ---------------------------------------------------------------- trees

class Underangeable(Exception):
    pass


def kc_parent_edges(parent: dict, kc_node: dict, kcs_at: dict) -> list[tuple]:
    """Contract the route tree to KCs: a -> b if a sits on the nearest route node above b's that holds a KC."""
    E = []
    for k in sorted(kc_node, key=str):
        v = parent[kc_node[k]]
        while v is not None and v not in kcs_at:
            v = parent[v]
        if v is not None:
            E += [(a, k) for a in kcs_at[v]]
    return E


def families(parent: dict, kc_node: dict, kcs_at: dict) -> dict:
    children = defaultdict(list)
    for v, p in parent.items():
        if p is not None:
            children[p].append(v)
    memo = {}

    def sub(v):
        if v not in memo:
            s = set(kcs_at.get(v, ()))
            for c in children[v]:
                s |= sub(c)
            memo[v] = s
        return memo[v]
    sys.setrecursionlimit(10000)
    fam = {}
    for k, v in kc_node.items():
        p = parent[v]
        fam[k] = (sub(p) - sub(v)) if p is not None else set()
    return fam


def _repair(items: list, slots: list, ok, rng: random.Random, pool=None, iters: int = 200000) -> list:
    """Swap-repair slots in place until ok(item, slot) for every item; pool(i) lists the positions
    item i may swap with (default: all)."""
    n = len(items)
    bad = {i for i in range(n) if not ok(items[i], slots[i])}
    for _ in range(iters):
        if not bad:
            break
        i = rng.choice(sorted(bad))
        cand = pool(i) if pool else range(n)
        j = cand[rng.randrange(len(cand))]
        if ok(items[i], slots[j]) and ok(items[j], slots[i]):
            slots[i], slots[j] = slots[j], slots[i]
            bad.discard(i)
            bad.discard(j)
    return slots


def _derange(items: list, slots: list, ok, rng: random.Random, iters: int = 20000):
    """A permutation of slots over items with ok(item, slot) for all; None if not found."""
    if not items:
        return []
    sl = list(slots)
    rng.shuffle(sl)
    sl = _repair(items, sl, ok, rng, iters=iters)
    return sl if all(ok(i, s_) for i, s_ in zip(items, sl)) else None


def derange_forest(E: list[tuple], depth: dict, seed: int) -> tuple[list[tuple], dict]:
    """Same-shape derangement of a KC forest. depth: KC -> route depth."""
    rng = random.Random(seed)
    real = defaultdict(set)
    for a, b in E:
        real[b].add(a)
    groups = defaultdict(list)
    for a, b in E:
        groups[(depth[b], depth[a])].append((b, a))
    ok = lambda b, a: a not in real[b] and a != b and b not in real.get(a, ()) and depth[a] < depth[b]
    # stage 1: derange within (child depth, parent depth) groups; a group that cannot be deranged
    # keeps its real slots for now (marked bad)
    items, slots = [], []
    for key in sorted(groups, key=str):
        g = groups[key]
        res = _derange([b for b, _ in g], [a for _, a in g], ok, rng)
        items += [b for b, _ in g]
        slots += res if res is not None else [a for _, a in g]
    pooled = {"stage1_bad": sum(not ok(b, a) for b, a in zip(items, slots))}
    # stage 2: repair bad items by swapping with an item of the same child depth; stage 3: any item
    by_cd = defaultdict(list)
    for i, b_ in enumerate(items):
        by_cd[depth[b_]].append(i)
    _repair(items, slots, ok, rng, pool=lambda i: by_cd[depth[items[i]]])
    pooled["stage2_bad"] = sum(not ok(b, a) for b, a in zip(items, slots))
    _repair(items, slots, ok, rng)
    pooled["stage3_bad"] = sum(not ok(b, a) for b, a in zip(items, slots))
    if pooled["stage3_bad"]:
        raise Underangeable(f"derangement impossible for {pooled['stage3_bad']} edges")
    new = list(zip(slots, items))
    realpd = {b: depth[a] for a, b in E}
    pooled["parent_depth_changed"] = sum(depth[a] != realpd[b] for a, b in new)
    Es = set(E)
    assert len(new) == len(E)
    assert not any(e in Es for e in new), "a real link survived"
    assert not any((b, a) in Es for a, b in new), "a reversed real link"
    assert all(a != b and depth[a] < depth[b] for a, b in new)
    assert sorted(Counter_(a for a, _ in new)) == sorted(Counter_(a for a, _ in E)), "out-degrees changed"
    assert sorted({b for _, b in new}, key=str) == sorted({b for _, b in E}, key=str)
    return new, pooled


def derange_route(parent: dict, depth: dict, seed: int) -> dict:
    """At every depth >= 2, permute nodes among parent slots of the depth above; no node keeps its parent."""
    rng = random.Random(seed)
    newp = dict(parent)
    for d in sorted({depth[v] for v in parent}):
        if d < 2:
            continue
        vs = sorted((v for v in parent if depth[v] == d), key=str)
        res = _derange(vs, [parent[v] for v in vs], lambda v, p: p != parent[v], rng)
        if res is None:
            raise Underangeable(f"route derangement impossible at depth {d}")
        newp.update(dict(zip(vs, res)))
    assert all(newp[v] != parent[v] for v in parent if depth[v] >= 2)
    assert sorted(Counter_(newp.values())) == sorted(Counter_(parent.values()))
    return newp


def Counter_(vals):
    c = defaultdict(int)
    for v in vals:
        c[str(v)] += 1
    return list(c.items())


def real_tree(rt: dict) -> tuple[dict, dict, dict, dict]:
    """rt: KC id -> route list. Route nodes are tuples (prefixes)."""
    parent, depth, kcs_at, kc_node = {}, {}, defaultdict(list), {}
    for k, r in rt.items():
        t = tuple(r)
        kc_node[k] = t
        kcs_at[t].append(k)
        for d in range(1, len(t) + 1):
            v = t[:d]
            parent[v] = t[:d - 1] if d > 1 else None
            depth[v] = d
    for v in kcs_at:
        kcs_at[v].sort(key=int)
    return parent, depth, dict(kcs_at), kc_node


def arms(parent, depth, kcs_at, kc_node):
    E = kc_parent_edges(parent, kc_node, kcs_at)
    kdepth = {k: depth[v] for k, v in kc_node.items()}
    pre = {"T": e2e.preds(E), "Tr": e2e.preds([(b, a) for a, b in E])}
    info = {"edges": len(E), "der_pooled": []}
    der = []
    for i in range(N_DER):
        Ed, pooled = derange_forest(E, kdepth, e2e.SEED + 900 + i)
        pre[f"Td{i}"] = e2e.preds(Ed)
        info["der_pooled"].append(pooled)
        der.append(Ed)
    pre["F"] = families(parent, kc_node, kcs_at)
    info["family_mean_size"] = float(np.mean([len(s) for s in pre["F"].values()]))
    info["fam_der_mean_size"] = []
    for j in range(N_FDER):
        pj = derange_route(parent, depth, e2e.SEED + 950 + j)
        pre[f"Fd{j}"] = families(pj, kc_node, kcs_at)
        info["fam_der_mean_size"].append(float(np.mean([len(s) for s in pre[f"Fd{j}"].values()])))
    return E, pre, info


# ---------------------------------------------------------------- lean features (copy of e2e.features)

def per_question_sets(qkc: list[list[int]], pre_idx: dict[int, set]) -> list[tuple]:
    out = []
    for ns in qkc:
        ps = set().union(*(pre_idx.get(k, set()) for k in ns)) - set(ns) if ns else set()
        out.append(tuple(sorted(ps)))
    return out


def features_lean(learner: np.ndarray, qidx: np.ndarray, y: np.ndarray, qkc: list[list[int]],
                  psets: dict[str, list[tuple]], nk: int):
    """Same columns as e2e.features for one Q-matrix (K) and edge sets on it (P:<name>), rows in
    each learner's time order with learners contiguous. Also returns `cold`: the question has KCs and
    the learner has no prior attempt on any of them."""
    n = len(qidx)
    U = np.zeros((n, 2), np.float32)
    K = np.zeros((n, 3), np.float32)
    P = {a: np.zeros((n, 3), np.float32) for a in psets}
    cold = np.zeros(n, bool)
    maxlen = int(np.bincount(learner).max()) + 2
    L = [math.log1p(i) for i in range(maxlen)]
    s = [0] * nk
    f = [0] * nk
    touched = []
    lr, qr, yr = learner.tolist(), qidx.tolist(), y.tolist()
    names = list(psets)
    plist = [psets[a] for a in names]
    pbuf = [P[a] for a in names]
    last = -1
    ts = tf = 0
    for r in range(n):
        u, q, c = lr[r], qr[r], yr[r]
        if u != last:
            for k in touched:
                s[k] = f[k] = 0
            touched = []
            last, ts, tf = u, 0, 0
        U[r, 0] = L[ts]
        U[r, 1] = L[tf]
        ns = qkc[q]
        if ns:
            m = len(ns)
            K[r, 0] = sum(L[s[k]] for k in ns) / m
            K[r, 1] = sum(L[f[k]] for k in ns) / m
            cold[r] = all(s[k] + f[k] == 0 for k in ns)
        else:
            K[r, 2] = 1
        for ps_q, buf in zip(plist, pbuf):
            ps = ps_q[q]
            if ps:
                m = len(ps)
                buf[r, 0] = sum(L[s[k]] for k in ps) / m
                buf[r, 1] = sum(L[f[k]] for k in ps) / m
            else:
                buf[r, 2] = 1
        for k in ns:
            if c:
                s[k] += 1
            else:
                f[k] += 1
            touched.append(k)
        if c:
            ts += 1
        else:
            tf += 1
    out = {"U": U, "K": K}
    out.update({f"P:{a}": v for a, v in P.items()})
    return out, cold


# ---------------------------------------------------------------- comparison (copy of e2e.kt_compare + subset)

def specs_for():
    sp = {"M1": ["off", "U"], "M2": ["off", "U", "K"]}
    for a in ["T", "Tr"] + [f"Td{i}" for i in range(N_DER)] + ["F"] + [f"Fd{j}" for j in range(N_FDER)]:
        sp[a] = ["off", "U", "K", f"P:{a}"]
    return sp


def compare(blocks, y, learner, train, cold):
    """e2e.kt_compare's fit and bootstrap (same seed, same draw order), plus AUCs on the cold-start subset."""
    test = ~train
    lw_idx = np.unique(learner[test], return_inverse=True)[1]
    nl = lw_idx.max() + 1
    ct = cold[test]
    scores, sub, betas = {}, {}, {}
    for m, bl in specs_for().items():
        X = np.column_stack([blocks[b] for b in bl]).astype(np.float64)
        beta = e2e.fit_logistic(X[train], y[train].astype(float))
        betas[m] = beta.tolist()
        sc = e2e.predict(beta, X[test])
        del X
        scores[m] = e2e.AUC(sc, y[test], lw_idx)
        sub[m] = e2e.AUC(sc[ct], y[test][ct], lw_idx[ct])
    rng = np.random.default_rng(e2e.SEED)
    ones = np.ones(nl)
    point = {m: a(ones) for m, a in scores.items()}
    spoint = {m: a(ones) for m, a in sub.items()}
    draws = {m: [] for m in scores}
    sdraws = {m: [] for m in scores}
    for _ in range(e2e.BOOT):
        lw = np.bincount(rng.integers(0, nl, nl), minlength=nl).astype(float)
        for m in scores:
            draws[m].append(scores[m](lw))
            sdraws[m].append(sub[m](lw))
    draws = {m: np.array(v) for m, v in draws.items()}
    sdraws = {m: np.array(v) for m, v in sdraws.items()}
    for P_, D_ in ((point, draws), (spoint, sdraws)):
        P_["Td-bar"] = float(np.mean([P_[f"Td{i}"] for i in range(N_DER)]))
        D_["Td-bar"] = np.mean([D_[f"Td{i}"] for i in range(N_DER)], axis=0)
        P_["Fd-bar"] = float(np.mean([P_[f"Fd{j}"] for j in range(N_FDER)]))
        D_["Fd-bar"] = np.mean([D_[f"Fd{j}"] for j in range(N_FDER)], axis=0)
    return point, draws, spoint, sdraws, betas, int(ct.sum())


def v1(d: dict, what: str) -> str:
    if d["lo"] > e2e.BEATS:
        return f"{what} BEATS ITS DERANGEMENT"
    if d["lo"] > -EQUIV and d["hi"] < EQUIV:
        return f"{what} EQUIVALENT TO ITS DERANGEMENT"
    if d["hi"] < -EQUIV:
        return f"DERANGEMENT BEATS THE {what}"
    return f"{what} NOT SHOWN BETTER THAN ITS DERANGEMENT"


def coverage(blocks, mask, a):
    P = blocks[f"P:{a}"][mask]
    return float(((P[:, 0] + P[:, 1]) > 0).mean())


def score_world(blocks, y, learner, train, cold):
    point, draws, spoint, sdraws, betas, ncold = compare(blocks, y, learner, train, cold)
    D = {f"{a}-{b}": e2e.diff(point, draws, a, b) for a, b in
         [("T", "Td-bar"), ("T", "M2"), ("T", "Tr"), ("Td-bar", "M2"), ("M2", "M1"),
          ("F", "Fd-bar"), ("F", "M2"), ("Fd-bar", "M2")] + [("T", f"Td{i}") for i in range(N_DER)]
         + [("F", f"Fd{j}") for j in range(N_FDER)]}
    SD = {f"{a}-{b}": e2e.diff(spoint, sdraws, a, b) for a, b in
          [("T", "Td-bar"), ("T", "M2"), ("F", "Fd-bar"), ("F", "M2"), ("M2", "M1")]}
    return point, draws, spoint, D, SD, betas, ncold


# ---------------------------------------------------------------- synthetic floor

def sim_tree_world(kind: str, gamma: float, seed: int):
    rng = np.random.default_rng(seed)
    K = 30
    redraws = 0
    while True:                          # redraw a tree that cannot be deranged at every seed
        parent, depth, kcs_at, kc_node = {}, {}, {}, {}
        for mmod in range(3):
            parent[f"m{mmod}"], depth[f"m{mmod}"] = None, 1
        for j in range(K):
            v = f"k{j}"
            if j == 0 or rng.random() < 0.35:
                p = f"m{rng.integers(3)}"
            else:
                p = f"k{rng.integers(j)}"
            parent[v], depth[v] = p, depth[p] + 1
            kcs_at[v], kc_node[j] = [j], v
        try:
            arms(parent, depth, kcs_at, kc_node)
            break
        except Underangeable:
            redraws += 1
    E = kc_parent_edges(parent, kc_node, kcs_at)
    kpar = {b: a for a, b in E}
    fam = families(parent, kc_node, kcs_at)
    qnode = {f"q{j}_{k}": j for j in range(K) for k in range(5)}
    b = {q: rng.normal(0, 0.7) for q in qnode}
    seq, y, learner = [], [], []
    for u in range(3000):
        th = rng.normal()
        m = np.zeros(K)
        order = np.argsort(np.arange(K) + rng.normal(0, 6, K))
        for j in order:
            if kind == "parent":
                g = m[kpar[j]] if j in kpar else 0.5
            elif kind == "family":
                g = float(np.mean([m[x] for x in fam[j]])) if fam[j] else 0.5
            else:
                g = 0.5
            for _ in range(rng.integers(4, 7)):
                q = f"q{j}_{rng.integers(5)}"
                eta = th - b[q] + 1.5 * m[j] + gamma * (g - 0.5)
                c = int(rng.random() < 1 / (1 + math.exp(-eta)))
                seq.append((u, q, c))
                y.append(c)
                learner.append(u)
                m[j] += 0.25 * (1 - m[j])
    return seq, np.array(y), np.array(learner), qnode, (parent, depth, kcs_at, kc_node), redraws


def run_world(seq, y, learner, qnode, tree, check_equal=False):
    parent, depth, kcs_at, kc_node = tree
    E, pre, info = arms(parent, depth, kcs_at, kc_node)
    train = np.array([int(hashlib.sha256(str(u).encode()).hexdigest()[:8], 16) % 5 != 0 for u in learner])
    qlist = sorted(qnode)
    qi = {q: i for i, q in enumerate(qlist)}
    qidx = np.array([qi[q] for _, q, _ in seq])
    nk = len(kc_node)
    qkc = [[qnode[q]] for q in qlist]
    psets = {a: per_question_sets(qkc, p) for a, p in pre.items()}
    blocks, cold = features_lean(learner, qidx, y, qkc, psets, nk)
    if check_equal:
        ref = e2e.features(seq, {"expert": {q: [j] for q, j in qnode.items()}},
                           {a: ("expert", p) for a, p in pre.items()})
        assert np.array_equal(ref["U"], blocks["U"]) and np.array_equal(ref["K:expert"], blocks["K"])
        for a in pre:
            assert np.array_equal(ref[f"P:{a}"], blocks[f"P:{a}"]), a
        print("  features_lean equals e2e.features on this world (U, K and every P block)")
    off, _, _ = e2e.difficulty(qidx, y, train)
    blocks["off"] = off[:, None]
    point, draws, spoint, D, SD, _, ncold = score_world(blocks, y, learner, train, cold)
    test = ~train
    cov = {a: coverage(blocks, test, a) for a in pre}
    return point, draws, D, cov, info


def synthetic() -> dict:
    res = {"planted-parent": [], "planted-family": [], "null": []}
    first = True
    for kind, gamma, worlds in (("parent", 2.0, 5), ("family", 2.0, 5), ("null", 0.0, 10)):
        key = "null" if kind == "null" else f"planted-{kind}"
        for w in range(worlds):
            seed = e2e.SEED + 1000 * (1 + ["parent", "family", "null"].index(kind)) + w
            seq, y, learner, qnode, tree, redraws = sim_tree_world(kind, gamma, seed)
            point, draws, D, cov, info = run_world(seq, y, learner, qnode, tree, check_equal=first)
            first = False
            b = lambda a, c: e2e.beats(point, draws, a, c)
            row = {"world": w, "gamma": gamma, "edges": info["edges"], "tree_redraws": redraws,
                   "der_pooled": info["der_pooled"],
                   "auc": {m: round(v, 4) for m, v in point.items()},
                   "differences": {k: D[k] for k in ("T-Td-bar", "T-M2", "T-Tr", "M2-M1", "F-Fd-bar", "F-M2")},
                   "coverage": {k: round(v, 4) for k, v in cov.items()},
                   "T beats Td-bar": b("T", "Td-bar"), "F beats Fd-bar": b("F", "Fd-bar"),
                   "M2 beats M1": b("M2", "M1")}
            res[key].append(row)
            print(f"  {key:<15} world {w}: T-Td {D['T-Td-bar']['diff']:+.4f} "
                  f"[{D['T-Td-bar']['lo']:+.4f}, {D['T-Td-bar']['hi']:+.4f}]  "
                  f"F-Fd {D['F-Fd-bar']['diff']:+.4f} [{D['F-Fd-bar']['lo']:+.4f}, {D['F-Fd-bar']['hi']:+.4f}]  "
                  f"M2-M1 {D['M2-M1']['diff']:+.4f}", flush=True)
    tp = sum(r["T beats Td-bar"] for r in res["planted-parent"])
    tn = sum(r["T beats Td-bar"] for r in res["null"])
    fp = sum(r["F beats Fd-bar"] for r in res["planted-family"])
    fn = sum(r["F beats Fd-bar"] for r in res["null"])
    q_ok = all(r["M2 beats M1"] for r in res["planted-parent"] + res["planted-family"])
    res["floor"] = {"tree": {"planted_detected": tp, "null_false_positives": tn, "qmatrix_detected_all": q_ok,
                             "passes": tp >= 4 and tn <= 1 and q_ok},
                    "family": {"planted_detected": fp, "null_false_positives": fn,
                               "passes": fp >= 4 and fn <= 1},
                    "also": {"T beats Td-bar in planted-family worlds":
                             sum(r["T beats Td-bar"] for r in res["planted-family"]),
                             "F beats Fd-bar in planted-parent worlds":
                             sum(r["F beats Fd-bar"] for r in res["planted-parent"])}}
    print(f"TREE FLOOR {'PASSES' if res['floor']['tree']['passes'] else 'FAILS'}: planted {tp}/5, null {tn}/10, "
          f"Q-matrix in every planted world: {q_ok}")
    print(f"FAMILY FLOOR {'PASSES' if res['floor']['family']['passes'] else 'FAILS'}: planted {fp}/5, null {fn}/10")
    OUT.mkdir(exist_ok=True)
    (OUT / "synthetic.json").write_text(json.dumps(res, indent=1) + "\n")
    return res


# ---------------------------------------------------------------- real data

def load_lean():
    """attempts.tsv as arrays in e2e.load_attempts' order (uid string, start time, line number)."""
    uid_code, kc_code = {}, {}
    U, Q, KC, Y, T = [], [], [], [], []
    with open(data_path("XES_DIR") / "attempts.tsv") as f:
        for line in f:
            uid, q, c, res, t = line.rstrip("\n").split("\t")
            U.append(uid_code.setdefault(uid, len(uid_code)))
            Q.append(int(q))
            KC.append(kc_code.setdefault(c, len(kc_code)))
            Y.append(res == "1")
            T.append(int(t))
    uids = list(uid_code)
    rank = np.empty(len(uids), np.int64)
    rank[np.argsort(np.array(uids, dtype=object), kind="stable")] = np.arange(len(uids))
    U = rank[np.array(U, np.int64)]
    Q, KC, Y, T = np.array(Q, np.int64), np.array(KC, np.int64), np.array(Y, np.int8), np.array(T, np.int64)
    order = np.lexsort((np.arange(len(U)), T, U))
    sorted_uids = sorted(uids)
    return U[order], Q[order], KC[order], Y[order], sorted_uids, list(kc_code)


def real() -> None:
    syn = json.loads((OUT / "synthetic.json").read_text())
    tree_ok, fam_ok = syn["floor"]["tree"]["passes"], syn["floor"]["family"]["passes"]
    rt = e2e.routes()
    parent, depth, kcs_at, kc_node = real_tree(rt)
    E, pre, info = arms(parent, depth, kcs_at, kc_node)
    print(f"tree: {len(kc_node)} KCs, {info['edges']} contracted parent links; "
          f"derangements pooled {info['der_pooled']}")
    print("reading attempts", flush=True)
    learner, qraw, kcc, y, sorted_uids, kc_strings = load_lean()
    train_l = np.array([int(hashlib.sha256(u.encode()).hexdigest()[:8], 16) % 5 != 0 for u in sorted_uids])
    train = train_l[learner]
    qvals = np.unique(qraw)                       # sorted by int, as e2e's qlist
    qidx = np.searchsorted(qvals, qraw)
    kcs = sorted(rt, key=int)
    ki = {k: i for i, k in enumerate(kcs)}
    first_kc = {}
    for q, c in zip(qidx.tolist(), kcc.tolist()):
        if q not in first_kc:
            first_kc[q] = c
    qkc = [[ki[k] for k in kc_strings[first_kc[q]].split("_") if k in rt] for q in range(len(qvals))]
    pre_idx = {a: {ki[k]: {ki[x] for x in s} for k, s in p.items()} for a, p in pre.items()}
    psets = {a: per_question_sets(qkc, p) for a, p in pre_idx.items()}
    print("features", flush=True)
    blocks, cold = features_lean(learner, qidx, y, qkc, psets, len(kcs))
    off, _, _ = e2e.difficulty(qidx, y, train)
    blocks["off"] = off[:, None]
    test = ~train
    cov = {a: coverage(blocks, test, a) for a in pre}
    size_T = check_control_scale({"T": cov["T"], **{f"Td{i}": cov[f"Td{i}"] for i in range(N_DER)}},
                                 [f"Td{i}" for i in range(N_DER)], min_ratio=MIN_COVER, strict=False)
    size_F = check_control_scale({"F": cov["F"], **{f"Fd{j}": cov[f"Fd{j}"] for j in range(N_FDER)}},
                                 [f"Fd{j}" for j in range(N_FDER)], min_ratio=MIN_COVER, strict=False)
    t_sized = any(cov[f"Td{i}"] >= MIN_COVER * cov["T"] for i in range(N_DER))
    f_sized = any(cov[f"Fd{j}"] >= MIN_COVER * cov["F"] for j in range(N_FDER))
    print("fitting", flush=True)
    point, draws, spoint, D, SD, betas, ncold = score_world(blocks, y, learner, train, cold)
    pub = json.loads((E2E_DIR / "out/result.json").read_text())["B11"]["auc"]
    repro = {"M1": point["M1"] - pub["M1"], "M2": point["M2"] - pub["M2"]}
    if max(abs(v) for v in repro.values()) > 1e-6:
        raise SystemExit(f"framework mismatch: M1/M2 differ from e2e.py's published AUCs by {repro}")
    if not tree_ok:
        V1 = V2 = "UNANSWERABLE (tree floor fails)"
    elif not t_sized:
        V1 = V2 = "CONTROL TOO SMALL"
    else:
        V1 = v1(D["T-Td-bar"], "TREE")
        bm = e2e.beats(point, draws, "T", "M2")
        V2 = ("TREE CARRIES SPECIFIC SIGNAL" if bm and e2e.beats(point, draws, "T", "Td-bar") else
              "TREE ADDS SIGNAL, NOT SPECIFIC" if bm else "TREE ADDS NOTHING")
    V3 = ("UNANSWERABLE (family floor fails)" if not fam_ok else "CONTROL TOO SMALL" if not f_sized
          else v1(D["F-Fd-bar"], "FAMILY"))
    Es = set(E)
    direction = reversed_arrow(lambda es: point["T"] if es == Es else point["Tr"], E)
    res = {"split": {"train_attempts": int(train.sum()), "test_attempts": int(test.sum()),
                     "test_learners": int(len(np.unique(learner[test]))), "cold_start_test_attempts": ncold},
           "reproduces_e2e": {"M1_minus_published": repro["M1"], "M2_minus_published": repro["M2"]},
           "tree": {"kcs": len(kc_node), "route_nodes": len(parent), "contracted_parent_links": info["edges"],
                    "kcs_with_kc_parent": len({b for _, b in E}), "derangement_pooling": info["der_pooled"],
                    "family_mean_size": info["family_mean_size"],
                    "deranged_family_mean_size": info["fam_der_mean_size"]},
           "floor": syn["floor"],
           "coverage_test": cov, "size_check": {"tree": size_T, "family": size_F,
                                                "tree_sized": t_sized, "family_sized": f_sized},
           "auc": point, "differences": D,
           "cold_start": {"auc": spoint, "differences": SD},
           "V1": V1, "V2": V2, "V3": V3,
           "direction": {k: v for k, v in direction.items() if not callable(v)},
           "betas": {m: betas[m] for m in ("M2", "T", "Td0", "Tr", "F", "Fd0")}}
    OUT.mkdir(exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
    print("AUC", {m: round(v, 5) for m, v in point.items()})
    for k, v in D.items():
        print(f"  {k:<12} {v['diff']:+.5f} [{v['lo']:+.5f}, {v['hi']:+.5f}]")
    print("cold start", {k: f"{v['diff']:+.5f} [{v['lo']:+.5f}, {v['hi']:+.5f}]" for k, v in SD.items()})
    print("coverage", {k: round(v, 4) for k, v in cov.items()})
    print("V1:", V1)
    print("V2:", V2)
    print("V3:", V3)
    print("direction:", direction.get("verdict"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthetic", action="store_true")
    a = ap.parse_args()
    synthetic() if a.synthetic else real()


if __name__ == "__main__":
    main()
