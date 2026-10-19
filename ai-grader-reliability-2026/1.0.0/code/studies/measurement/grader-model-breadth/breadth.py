"""
Paper VI's model coverage: more models, reasoning on/off, the configuration record, and learners
(maintainer review 1, 2026-10-05).

WHAT WAS ASKED (research/readiness/ai-grader-reliability-2026/maintainer-review-1.md, verbatim):
  "across 3 LLM models from 2 providers" do we want to expand the main findings across more models?
  "why didn't you use something like opus 5.5? or fable" / "what about thinking/reasoning vs non
  reasoning models" / "Each model runs in its own default configuration." what is included in that
  configuration? I'm sure people will ask about temperature or top-p, etc. / You mention "no people
  are assigned" ... Would it make any difference if we compared findings by individual?

THE BASE. studies/measurement/grader-attainment-prior/ (Q2): JorGPT (Zenodo 18981627, CC BY 4.0,
data/data-sources.json `jorgpt-answers`), the original attainment draw (150 answers from learners with
held-out mean >= 6, 150 with < 4; 19 and 14 learners), three arms on identical work: control, the true
attainment label, the opposite tail's label (swapped). Harness mode `--mode attainment-swap --n 300`
(studies/measurement/grader-eval/harness/stability.ts), the shipped grading prompt (vendor pin
277cd5085). Four models there: Gemini 3.5 Flash Lite (thinking minimal), GPT-4.1-mini, GPT-5-mini,
Qwen3-235B-A22B-2507 (OpenRouter, DeepInfra pin). THIS SCRIPT NEVER READS THE CORPUS: it reads the
harness's per-case dumps (entry id, question id, hashed learner id, tail, teacher mark, labels, three
scores), which stay in the session scratchpad; only aggregates in out/ are committed.

PART 1, MODEL BREADTH. New models on the same draw and the same three arms, analysed with Q2's own
code (`analyse.analyse`, imported unchanged), so every row pools into Q2's table: L = score under the
high label minus under the low label on the same answer, learner-cluster bootstrap 95%; per-tail
signed error against the teacher's mark; Q2 revision-3 verdict (PRIOR / BIAS / MIXED / UNRESOLVED /
NO-LABEL-EFFECT / REVERSED). Pre-registered breadth verdict over the FRONTIER models only:
  PERSISTS-AT-FRONTIER  every frontier model's L 95% interval lies above 0
  ABSENT-AT-FRONTIER    every frontier model's L 90% interval lies inside +/-0.15 (equivalence)
  MIXED-AT-FRONTIER     otherwise
and across ALL models (old and new): the shared Q2 verdict, else MIXED-ACROSS-MODELS (as Q2).

PART 2, REASONING CONTRAST. The same model, the same draw, the same prompt and arms, with ONLY the
reasoning setting changed (harness `--reasoning`, provider.ts). dL = L(more reasoning) - L(less), on
the cases complete in both runs, learner-cluster bootstrap resampling learners within tail with the
same learners in both runs (paired). Margin 0.15 marks (about 40% of the smallest Q2 L, 0.37).
  REASONING-RAISES       dL 95% interval above 0
  REASONING-LOWERS       dL 95% interval below 0
  NO-REASONING-EFFECT    not the above and dL 90% interval inside +/-0.15
  INCONCLUSIVE           otherwise
Signed: positive means reasoning makes the grade MORE label-dependent. The same contrast is computed
for the tail-level signed errors (does reasoning change which way the label moves a tail).
Whether the provider honoured the setting is read off the billed reasoning tokens in each dump's
`run.tokens`, not assumed from the request; a contrast whose arms bill the same reasoning tokens is
reported as NOT-A-CONTRAST, whatever dL says.
A RE-RUN NULL. The Gemini lite tier is re-run at its default (thinking minimal) beside its thinking
arm: default-vs-default across runs is the null for a contrast made across runs, and it must come
back NO-REASONING-EFFECT-sized (it is reported with the same statistic as `RERUN`).

PART 3, CONFIGURATION RECORD. For every model configuration Paper VI and its re-tests used, what was
sent on the wire, captured from the real pinned SDK of each tree with `wirehook.mjs` (globalThis.fetch
replaced; nothing sent; prompt text and schema hashed) and, for the runs made here, from the request
bodies and billed usage the harness now records in each dump (`run.wire`, `run.tokens`, `run.served`).
No new model call. Table in out/config.json and the README.

PART 4, PER LEARNER (no new calls; the four Q2 dumps, plus the new models' dumps when they exist).
d_i = score|high label - score|low label for answer i; L_j = mean d_i over learner j's answers.
  Heterogeneity statistic F = between-learner mean square / within-learner mean square of d, one-way
  within tail (so the tail difference L_high - L_low, reported separately, does not count).
  tau = method-of-moments between-learner SD of L_j.
  CONTROL (family-matched, deranged): learner ids re-assigned among answers to the SAME question in
  the SAME tail, as a derangement (no answer keeps its learner where the stratum allows; singletons
  cannot move and are counted). Each learner keeps exactly its questions, so question-level
  differences in label sensitivity cannot pass for learner differences. 2,000 derangements; p =
  (1 + #{F_null >= F_obs}) / 2,001.
  SECOND CONTROL (the maintainer's "permute labels within learner"): within each learner, which of
  the two labelled scores counts as "high" is flipped at random per answer. That is the null L_j = 0
  for every learner, and gives how many learners individually show a label effect beyond chance.
  Verdict per model: HETEROGENEOUS (p < 0.05) or NO-DETECTABLE-HETEROGENEITY, the latter always with
  the floor's minimum detectable tau beside it. Across models: shared verdict, else MIXED. Reported
  only: per-learner L_j spread, the share of learners with L_j < 0 against the deranged null's, the
  correlation of L_j with the learner's held-out attainment within tail, and the agreement of L_j
  across models on the same learners (if label sensitivity were a property of a learner's work, it
  would correlate across models).

FLOOR (`--floor`). Reused: Q2's floor for the per-model verdict (studies/measurement/grader-attainment-
prior/out/floor.json: passed at revision 3 except OVERSHOOT at 0.78, documented there), valid here
because the draw, arms and instrument are identical; it was shaped to Gemini's calibration, and a
harsher grader resolves its references more easily, not less. New: (a) the dL instrument on the real
draw, synthetic graders with Q2's corpus-shaped base: NULL (two runs, same L = 0.45) must come back
NO-REASONING-EFFECT in >= 80% and with a signed call in <= 10%; +0.30 and -0.30 must be called RAISES /
LOWERS in >= 80%. If only the equivalence half fails, NO-REASONING-EFFECT is unreachable and dL is
read as an interval ("no change larger than X"), as Q2 did for Q4. (b) the heterogeneity test:
tau = 0 must give p < 0.05 in <= 10%; tau = 0 with QUESTION-level heterogeneity (sd 0.3) must also
give <= 10% (the family matching's job); detection rate reported at tau = 0.2, 0.3, 0.5, and the
smallest with >= 80% is the stated minimum detectable tau. Synthetic graders written and scored by
the same session: smoke checks, reported as such.

RESULTS (2026-10-05; README has the tables). Floor PASS, dL equivalence unreachable (read as
intervals), minimum detectable tau 0.5. Spend $42.68 of $60; Gemini 3.1 Pro, Fable 5.1, GPT-5.5
skipped by the cap. Part 1: PERSISTS-AT-FRONTIER (Opus 5.5 L +0.28 [+0.23, +0.32], MIXED); Llama 4
Maverick +0.54, PRIOR; all models MIXED-ACROSS-MODELS. Part 2: GPT-5-mini REASONING-LOWERS (minimal ->
high dL -0.51 [-0.62, -0.39]; minimal -> default -0.51; default -> high -0.01 [-0.10, +0.10]); Gemini
lite minimal -> high +0.05 [-0.06, +0.14]; re-run null -0.01 [-0.07, +0.05]. Part 3: no temperature,
top_p, seed or direct-API token cap was ever sent; the OpenAI re-tests sent strict:false where the
originals sent strict:true. Part 4: MIXED, HETEROGENEOUS on GPT-4.1-mini, Llama and GPT-5-mini at
minimal (tau 0.15-0.26), none after Holm; no learner below the sign-flip null on any run. Reported
beside: QWK GAIN from the true label on Opus, Llama and GPT-5-mini minimal (+0.03 to +0.05) with
Pearson r flat on every run.

Usage:
  python3 breadth.py --floor --draw <scratch>/grader-vi/draw.json
  python3 breadth.py --models <dump> ... --frontier <model-id> ...
  python3 breadth.py --reasoning <less.json>:<more.json>:<name> ...
  python3 breadth.py --learners <dump> ...
  python3 breadth.py --config <wire-dir> --dumps <dump> ...
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
Q2 = HERE.parent / "grader-attainment-prior"
sys.path.insert(0, str(Q2))
import analyse as q2  # noqa: E402  (Q2's instrument, unchanged)

MARGIN_L = 0.15
REPS = 4000
PERMS = 2000
FLOOR_REPS = 200


# ----------------------------------------------------------------------------- loading

def load(path: Path) -> dict:
    blob = json.loads(Path(path).read_text())
    rows = [r for r in blob["rows"] if None not in (r["control"], r["trueLabel"], r["swappedLabel"])]
    return {"blob": blob, "rows": rows, "model": blob.get("model"), "reasoning": blob.get("reasoning", "provider default")}


def hl(rows: list[dict]) -> np.ndarray:
    """Score under the high label minus under the low label, per answer (Q2's L, case level)."""
    return np.array([(r["trueLabel"] - r["swappedLabel"]) if r["tail"] == "high" else (r["swappedLabel"] - r["trueLabel"])
                     for r in rows], float)


# ----------------------------------------------------------------------------- part 1

def part1(paths: list[Path], frontier: list[str]) -> dict:
    rng = np.random.default_rng(7)
    per = {}
    for p in paths:
        m = q2.analyse(Path(p), rng)
        tag = m["model"] + ("" if json.loads(Path(p).read_text()).get("reasoning", "provider default") == "provider default"
                            else f" [reasoning {json.loads(Path(p).read_text())['reasoning']}]")
        tag = tag if tag not in per else f"{tag} [re-run, {Path(p).name}]"  # two runs of one configuration must not collide
        per[tag] = m
    verdicts = sorted({m["q2"]["verdict"] for m in per.values()})
    overall = verdicts[0] if len(verdicts) == 1 else "MIXED-ACROSS-MODELS"
    fr = [per[k] for k in per if any(k.startswith(f) or k == f for f in frontier)]
    if fr and all(m["learner_cluster"]["L"]["ci95"][0] > 0 for m in fr):
        fv = "PERSISTS-AT-FRONTIER"
    elif fr and all(-MARGIN_L < m["learner_cluster"]["L"]["ci90"][0] and m["learner_cluster"]["L"]["ci90"][1] < MARGIN_L for m in fr):
        fv = "ABSENT-AT-FRONTIER"
    else:
        fv = "MIXED-AT-FRONTIER" if fr else "NO-FRONTIER-MODEL-RUN"
    return {"overall_q2": overall, "frontier": frontier, "frontier_verdict": fv, "per_model": per}


# ----------------------------------------------------------------------------- part 2

def paired(a: list[dict], b: list[dict]) -> tuple[list[dict], list[dict]]:
    ib = {r["id"]: r for r in b}
    keep = [r for r in a if r["id"] in ib]
    return keep, [ib[r["id"]] for r in keep]


def _arrays(rows: list[dict]) -> dict[str, np.ndarray]:
    return {"d": hl(rows), "hi": np.array([r["tail"] == "high" for r in rows]),
            "h": np.array([r["human"] for r in rows], float), "c": np.array([r["control"] for r in rows], float),
            "t": np.array([r["trueLabel"] for r in rows], float)}


def contrast_stats(A: dict, B: dict, idx: np.ndarray) -> dict[str, float]:
    out = {}
    for name, X in (("less", A), ("more", B)):
        d, hi, h, c, t = (X[k][idx] for k in ("d", "hi", "h", "c", "t"))
        out[f"L_{name}"] = d.mean()
        for k, m in (("high", hi), ("low", ~hi)):
            out[f"L_{name}_{k}"] = d[m].mean()
            out[f"bias_control_{name}_{k}"] = (c - h)[m].mean()
            out[f"drift_{name}_{k}"] = (t - c)[m].mean()
    out["dL"] = out["L_more"] - out["L_less"]
    for k in ("high", "low"):
        out[f"dL_{k}"] = out[f"L_more_{k}"] - out[f"L_less_{k}"]
        out[f"d_bias_control_{k}"] = out[f"bias_control_more_{k}"] - out[f"bias_control_less_{k}"]
        out[f"d_drift_{k}"] = out[f"drift_more_{k}"] - out[f"drift_less_{k}"]
    return {k: float(v) for k, v in out.items()}


def contrast(a: list[dict], b: list[dict], rng: np.random.Generator, reps: int = REPS) -> dict:
    a, b = paired(a, b)
    learner = np.array([str(r["learnerId"]) for r in a])
    tail = np.array([r["tail"] == "high" for r in a])
    A, B = _arrays(a), _arrays(b)
    point = contrast_stats(A, B, np.arange(len(a)))
    draws = {k: [] for k in point}
    for _ in range(reps):
        idx = q2.cluster_index(learner, tail, rng)
        for k, v in contrast_stats(A, B, idx).items():
            draws[k].append(v)
    res = {k: {"est": v, "ci95": [float(np.percentile(draws[k], 2.5)), float(np.percentile(draws[k], 97.5))],
               "ci90": [float(np.percentile(draws[k], 5)), float(np.percentile(draws[k], 95))]} for k, v in point.items()}
    res["n_paired"] = len(a)
    return res


def verdict_dL(r: dict) -> str:
    lo, hi = r["dL"]["ci95"]
    l90, h90 = r["dL"]["ci90"]
    if lo > 0:
        return "REASONING-RAISES"
    if hi < 0:
        return "REASONING-LOWERS"
    if -MARGIN_L < l90 and h90 < MARGIN_L:
        return "NO-REASONING-EFFECT"
    return "INCONCLUSIVE"


def reasoning_tokens(blob: dict) -> dict:
    run = blob.get("run") or {}
    t = run.get("tokens") or {}
    n = max(1, t.get("withUsage", 0))
    return {"reasoning_per_call": t.get("reasoning", 0) / n, "output_per_call": t.get("output", 0) / n,
            "input_per_call": t.get("input", 0) / n, "calls_with_usage": t.get("withUsage", 0)}


def part2(specs: list[str]) -> dict:
    rng = np.random.default_rng(23)
    out = {}
    for spec in specs:
        less, more, name = spec.split(":", 2)
        A, B = load(Path(less)), load(Path(more))
        r = contrast(A["rows"], B["rows"], rng)
        ta, tb = reasoning_tokens(A["blob"]), reasoning_tokens(B["blob"])
        v = verdict_dL(r)
        # Pre-registered fallback: the floor's equivalence half failed (out/floor.json), so
        # NO-REASONING-EFFECT is unreachable and an unsigned result is read only as an interval.
        if v in ("NO-REASONING-EFFECT", "INCONCLUSIVE") and not json.loads((OUT / "floor.json").read_text())["dL_equivalence_reachable"]:
            v = f"NO-SIGNED-EFFECT (no change larger than {max(abs(x) for x in r['dL']['ci95']):.2f})"
        # A contrast whose arms bill the same reasoning is not a contrast. Only checkable where both
        # dumps carry usage (the Q2 dumps predate the usage record).
        if ta["calls_with_usage"] and tb["calls_with_usage"] and not name.startswith("RERUN"):
            if abs(tb["reasoning_per_call"] - ta["reasoning_per_call"]) < 1:
                v = "NOT-A-CONTRAST"
        out[name] = {"less": {"file": Path(less).name, "model": A["model"], "reasoning": A["reasoning"], "tokens": ta},
                     "more": {"file": Path(more).name, "model": B["model"], "reasoning": B["reasoning"], "tokens": tb},
                     "verdict": v, "margin": MARGIN_L, "stats": r}
    return out


# ----------------------------------------------------------------------------- part 4

def strata_derangement(groups: list[np.ndarray], rng: np.random.Generator, n: int) -> np.ndarray:
    """A permutation of 0..n-1 that sends every index to another index of its own stratum (a single
    random cycle through the stratum, which is a derangement); strata of one stay put."""
    perm = np.arange(n)
    for g in groups:
        if len(g) < 2:
            continue
        o = rng.permutation(g)
        perm[o] = np.roll(o, -1)
    return perm


def anova_F(d: np.ndarray, learner: np.ndarray, tail: np.ndarray) -> tuple[float, float]:
    ssb = ssw = 0.0
    dfb = dfw = 0
    n0_num = 0.0
    for t in (True, False):
        m = tail == t
        dd, ll = d[m], learner[m]
        mu = dd.mean()
        ids, inv = np.unique(ll, return_inverse=True)
        nj = np.bincount(inv)
        means = np.bincount(inv, weights=dd) / nj
        ssb += float((nj * (means - mu) ** 2).sum())
        ssw += float(((dd - means[inv]) ** 2).sum())
        dfb += len(ids) - 1
        dfw += len(dd) - len(ids)
        N = len(dd)
        n0_num += N - (nj ** 2).sum() / N
    msb, msw = ssb / dfb, ssw / dfw
    n0 = n0_num / dfb
    tau2 = max(0.0, (msb - msw) / n0)
    return msb / msw, float(np.sqrt(tau2))


def heterogeneity(rows: list[dict], rng: np.random.Generator, perms: int = PERMS) -> dict:
    d = hl(rows)
    learner = np.array([str(r["learnerId"]) for r in rows])
    tail = np.array([r["tail"] == "high" for r in rows])
    q = np.array([str(r["questionId"]) for r in rows])
    key = np.array([f"{t}|{qq}" for t, qq in zip(tail, q)])
    groups = [np.flatnonzero(key == k) for k in np.unique(key)]
    fixed = int(sum(len(g) for g in groups if len(g) < 2))
    F, tau = anova_F(d, learner, tail)
    null = np.empty(perms)
    taus = np.empty(perms)
    for i in range(perms):
        p = strata_derangement(groups, rng, len(d))
        null[i], taus[i] = anova_F(d, learner[p], tail)
    p_val = (1 + (null >= F).sum()) / (1 + perms)
    # Per-learner L_j and the second control (random sign flip within learner: L_j = 0 for all j).
    ids = np.unique(learner)
    Lj = np.array([d[learner == j].mean() for j in ids])
    nj = np.array([(learner == j).sum() for j in ids])
    tj = np.array([tail[learner == j][0] for j in ids])
    labj = np.array([np.mean([r["labelTrue"] for r, l in zip(rows, learner) if l == j]) for j in ids])
    flips = np.empty((perms, len(ids)))
    for i in range(perms):
        s = rng.choice([-1.0, 1.0], len(d))
        dd = d * s
        flips[i] = [dd[learner == j].mean() for j in ids]
    # learners individually beyond the sign-flip null (two-sided 95% per learner, not adjusted)
    lo, hi = np.percentile(flips, 2.5, axis=0), np.percentile(flips, 97.5, axis=0)
    above = int((Lj > hi).sum())
    below = int((Lj < lo).sum())
    # share of learners with L_j < 0 under the deranged (homogeneous) null
    neg_null = []
    for i in range(min(perms, 500)):
        p = strata_derangement(groups, rng, len(d))
        ll = learner[p]
        neg_null.append(np.mean([d[ll == j].mean() < 0 for j in ids]))
    rho = {}
    for name, m in (("high", tj), ("low", ~tj)):
        if m.sum() >= 4:
            rho[name] = float(_spearman(Lj[m], labj[m]))
    return {
        "n_answers": int(len(d)), "n_learners": int(len(ids)),
        "answers_per_learner": {"min": int(nj.min()), "median": float(np.median(nj)), "max": int(nj.max())},
        "fixed_in_derangement": fixed,
        "F": float(F), "tau": tau, "p_deranged": float(p_val),
        "tau_null_95": float(np.percentile(taus, 95)),
        "verdict": "HETEROGENEOUS" if p_val < 0.05 else "NO-DETECTABLE-HETEROGENEITY",
        "L_j": {"min": float(Lj.min()), "q25": float(np.percentile(Lj, 25)), "median": float(np.median(Lj)),
                "q75": float(np.percentile(Lj, 75)), "max": float(Lj.max()), "sd": float(Lj.std(ddof=1))},
        "share_L_j_negative": float((Lj < 0).mean()),
        "share_L_j_negative_null_95": [float(np.percentile(neg_null, 2.5)), float(np.percentile(neg_null, 97.5))],
        "learners_above_signflip_null": above, "learners_below_signflip_null": below,
        "spearman_Lj_vs_attainment_within_tail": rho,
        "per_learner": {j: {"L": float(L), "n": int(n), "tail": "high" if t else "low"} for j, L, n, t in zip(ids, Lj, nj, tj)},
    }


def _spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


def _Lj(d: np.ndarray, learner: np.ndarray, ids: list[str]) -> np.ndarray:
    return np.array([d[learner == j].mean() for j in ids])


def part4(paths: list[Path]) -> dict:
    rng = np.random.default_rng(31)
    per, data = {}, {}
    for p in paths:
        D = load(Path(p))
        tag = D["model"] + ("" if D["reasoning"] == "provider default" else f" [reasoning {D['reasoning']}]")
        tag = tag if tag not in per else f"{tag} [re-run, {Path(p).name}]"
        per[tag] = heterogeneity(D["rows"], rng)
        data[tag] = D["rows"]
    verdicts = sorted({m["verdict"] for m in per.values()})
    overall = verdicts[0] if len(verdicts) == 1 else "MIXED"
    # Holm across models (reported beside the pre-registered per-model p < 0.05, not instead of it).
    order = sorted(per, key=lambda k: per[k]["p_deranged"])
    running = 0.0
    for i, k in enumerate(order):
        running = max(running, min(1.0, (len(order) - i) * per[k]["p_deranged"]))
        per[k]["p_holm"] = running
    # Across models on the same learners (reported only): Spearman of within-tail-centred L_j for
    # each pair, learner ids permuted within tail in one model as the null. (i) as first written, on
    # raw d. That leaves in a confound: learners answered different questions, so a question-level
    # sensitivity shared by both models would make their L_j agree. REVISION (after (i) was first
    # printed, before any write-up): (ii) answers deranged within (tail, question) as the null. Its
    # null came back centred BELOW zero (median -0.20 on one pair): in strata of two or three answers
    # a derangement hands a learner's own deviation to the others, which anti-correlates the deranged
    # L_j with the real one. A biased null, so (ii) was dropped. (iii) is the reading: d residualised
    # on its (tail, question) mean in each model before L_j is formed, with null (i).
    names = list(per)
    cross = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            ra = {r["id"]: r for r in data[names[i]]}
            rows_b = [r for r in data[names[j]] if r["id"] in ra]
            rows_a = [ra[r["id"]] for r in rows_b]
            da, db = hl(rows_a), hl(rows_b)
            learner = np.array([str(r["learnerId"]) for r in rows_a])
            tail = np.array([r["tail"] == "high" for r in rows_a])
            key = np.array([f"{r['tail']}|{r['questionId']}" for r in rows_a])
            groups = [np.flatnonzero(key == k) for k in np.unique(key)]
            ids = sorted(set(learner))
            tl = np.array([tail[learner == k][0] for k in ids])

            def centred(x: np.ndarray) -> np.ndarray:
                x = x.copy()
                for t in (True, False):
                    x[tl == t] -= x[tl == t].mean()
                return x

            def resid(d: np.ndarray) -> np.ndarray:
                out = d.copy()
                for g in groups:
                    out[g] = d[g] - d[g].mean()
                return out

            res = {}
            for name, (u, v) in {"raw": (da, db), "question_residualised": (resid(da), resid(db))}.items():
                x = centred(_Lj(u, learner, ids))
                y = centred(_Lj(v, learner, ids))
                r = _spearman(x, y)
                null = []
                for _ in range(2000):
                    yy = y.copy()
                    for t in (True, False):
                        m = np.flatnonzero(tl == t)
                        yy[m] = y[rng.permutation(m)]
                    null.append(_spearman(x, yy))
                res[name] = {"spearman_within_tail": r, "p_one_sided": float((1 + (np.array(null) >= r).sum()) / 2001)}
            cross[f"{names[i]} ~ {names[j]}"] = {"n_learners": len(ids), **res}
    return {"overall": overall, "per_model": per, "cross_model_learner_agreement": cross}


# ----------------------------------------------------------------------------- floors

def synth_pair(draw: list[dict], rng: np.random.Generator, L_a: float, L_b: float,
               tau: float = 0.0, q_sd: float = 0.0) -> tuple[list[dict], list[dict]]:
    """Two synthetic runs on the real draw with Q2's corpus-shaped base grader (analyse.BASE_C,
    BASE_G, learner sd 0.33, case sd 1.4, per-call sd 0.6). A high label adds +L/2 and a low label
    -L/2, with a learner-specific deviation (sd tau) and a question-specific one (sd q_sd)."""
    learners = sorted({r["learnerId"] for r in draw})
    qs = sorted({r["questionId"] for r in draw})
    lv = dict(zip(learners, rng.normal(0, 0.33, len(learners))))
    lt = dict(zip(learners, rng.normal(0, tau, len(learners))))
    qt = dict(zip(qs, rng.normal(0, q_sd, len(qs))))
    base = {r["id"]: 5 + q2.BASE_C * (r["human"] - 5) + q2.BASE_G + lv[r["learnerId"]] + rng.normal(0, 1.4) for r in draw}

    def run(L):
        out = []
        for r in draw:
            eff = L + lt[r["learnerId"]] + qt[r["questionId"]]

            def arm(label):
                x = base[r["id"]] + rng.normal(0, 0.6)
                if label is not None:
                    x += eff / 2 if label >= 5 else -eff / 2
                return float(np.clip(q2.round_half_up(x), *q2.SCALE))

            out.append({**r, "control": arm(None), "trueLabel": arm(r["labelTrue"]), "swappedLabel": arm(r["labelSwapped"])})
        return out

    return run(L_a), run(L_b)


def floor(draw_path: Path) -> dict:
    draw = json.loads(Path(draw_path).read_text())["rows"]
    rng = np.random.default_rng(20261006)
    rep = {"dL": {}, "heterogeneity": {}}
    ok = True
    for name, (la, lb, want) in {"NULL": (0.45, 0.45, "NO-REASONING-EFFECT"),
                                 "RAISE": (0.45, 0.75, "REASONING-RAISES"),
                                 "LOWER": (0.45, 0.15, "REASONING-LOWERS")}.items():
        got = []
        for _ in range(FLOOR_REPS):
            a, b = synth_pair(draw, rng, la, lb)
            got.append(verdict_dL(contrast(a, b, rng, reps=400)))
        hit = got.count(want) / len(got)
        signed = sum(v in ("REASONING-RAISES", "REASONING-LOWERS") and v != want for v in got) / len(got)
        passed = hit >= 0.8 and signed <= 0.10
        if name == "NULL":
            ok &= signed <= 0.10      # a signed call under NULL is the costly error; equivalence may fail
        else:
            ok &= passed
        rep["dL"][name] = {"expected": want, "hit_rate": hit, "wrong_signed_rate": signed,
                           "verdicts": {v: got.count(v) for v in set(got)}, "pass": passed}
        print(f"  dL floor {name:6s} expect {want:20s} hit {hit:.2f} {rep['dL'][name]['verdicts']}")
    rep["dL_equivalence_reachable"] = rep["dL"]["NULL"]["pass"]
    for name, (tau, qsd) in {"tau0": (0.0, 0.0), "tau0_question0.3": (0.0, 0.3), "tau0.2": (0.2, 0.0),
                             "tau0.3": (0.3, 0.0), "tau0.5": (0.5, 0.0)}.items():
        ps = []
        for _ in range(FLOOR_REPS):
            a, _ = synth_pair(draw, rng, 0.45, 0.45, tau=tau, q_sd=qsd)
            ps.append(heterogeneity_p(a, rng))
        rate = float(np.mean(np.array(ps) < 0.05))
        rep["heterogeneity"][name] = {"tau": tau, "question_sd": qsd, "rate_p_below_0.05": rate}
        print(f"  het floor {name:18s} p<0.05 in {rate:.2f}")
    fp_ok = rep["heterogeneity"]["tau0"]["rate_p_below_0.05"] <= 0.10 and rep["heterogeneity"]["tau0_question0.3"]["rate_p_below_0.05"] <= 0.10
    mdt = next((v["tau"] for k, v in rep["heterogeneity"].items() if v["tau"] > 0 and v["rate_p_below_0.05"] >= 0.8), None)
    rep["minimum_detectable_tau"] = mdt
    rep["heterogeneity_false_positive_ok"] = fp_ok
    ok &= fp_ok
    rep["pass"] = bool(ok)
    rep["note"] = "smoke check: synthetic graders written and scored by the same session"
    return rep


def heterogeneity_p(rows: list[dict], rng: np.random.Generator, perms: int = 200) -> float:
    d = hl(rows)
    learner = np.array([str(r["learnerId"]) for r in rows])
    tail = np.array([r["tail"] == "high" for r in rows])
    key = np.array([f"{r['tail']}|{r['questionId']}" for r in rows])
    groups = [np.flatnonzero(key == k) for k in np.unique(key)]
    F, _ = anova_F(d, learner, tail)
    null = np.array([anova_F(d, learner[strata_derangement(groups, rng, len(d))], tail)[0] for _ in range(perms)])
    return float((1 + (null >= F).sum()) / (1 + perms))


# ----------------------------------------------------------------------------- part 3

def config(wire_dir: Path, dumps: list[Path]) -> dict:
    captured = {}
    for f in sorted(Path(wire_dir).glob("*.jsonl")):
        captured[f.stem] = [json.loads(line) for line in f.read_text().splitlines() if line.strip()]
    runs = {}
    for p in dumps:
        b = json.loads(Path(p).read_text())
        runs[Path(p).name] = {"model": b.get("model"), "temperature": b.get("temperature"), "reasoning": b.get("reasoning"),
                              "run": {k: v for k, v in (b.get("run") or {}).items()}}
    return {"captured_offline": captured, "runs": runs}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--floor", action="store_true")
    ap.add_argument("--draw", type=Path)
    ap.add_argument("--models", type=Path, nargs="*")
    ap.add_argument("--frontier", nargs="*", default=[])
    ap.add_argument("--reasoning", nargs="*")
    ap.add_argument("--learners", type=Path, nargs="*")
    ap.add_argument("--config", type=Path)
    ap.add_argument("--dumps", type=Path, nargs="*", default=[])
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    if a.floor:
        res = floor(a.draw)
        (OUT / "floor.json").write_text(json.dumps(res, indent=2) + "\n")
        print("FLOOR", "PASS" if res["pass"] else "FAIL", "| dL equivalence reachable:", res["dL_equivalence_reachable"],
              "| min detectable tau:", res["minimum_detectable_tau"])
        sys.exit(0 if res["pass"] else 1)
    if a.config:
        res = config(a.config, a.dumps)
        (OUT / "config.json").write_text(json.dumps(res, indent=2) + "\n")
        return
    fl = json.loads((OUT / "floor.json").read_text())
    if not fl["pass"]:
        sys.exit("floor did not pass; no real number is read")
    if a.models:
        res = part1(a.models, a.frontier)
        (OUT / "models.json").write_text(json.dumps(res, indent=2) + "\n")
        for k, m in res["per_model"].items():
            R = m["learner_cluster"]
            f = lambda x: f"{R[x]['est']:+.2f} [{R[x]['ci95'][0]:+.2f}, {R[x]['ci95'][1]:+.2f}]"  # noqa: E731
            print(f"{k:55s} n={m['n_complete']:3d} L {f('L')} Lh {R['L_high']['est']:+.2f} Ll {R['L_low']['est']:+.2f} "
                  f"bc {R['bias_control_high']['est']:+.2f}/{R['bias_control_low']['est']:+.2f} "
                  f"bt {R['bias_true_high']['est']:+.2f}/{R['bias_true_low']['est']:+.2f} dMAElow {f('dMAE_low')} "
                  f"{m['q2']['verdict']} ({m['q2']['high_tail']}, {m['q2']['low_tail']})")
        print("OVERALL", res["overall_q2"], "| FRONTIER", res["frontier_verdict"])
    if a.reasoning:
        res = part2(a.reasoning)
        (OUT / "reasoning.json").write_text(json.dumps(res, indent=2) + "\n")
        for k, v in res.items():
            s = v["stats"]
            f = lambda x: f"{s[x]['est']:+.3f} [{s[x]['ci95'][0]:+.3f}, {s[x]['ci95'][1]:+.3f}]"  # noqa: E731
            print(f"{k:30s} n={s['n_paired']} L {s['L_less']['est']:+.2f} -> {s['L_more']['est']:+.2f}  dL {f('dL')} "
                  f"dL_high {f('dL_high')} dL_low {f('dL_low')}  {v['verdict']}  "
                  f"reasoning tok/call {v['less']['tokens']['reasoning_per_call']:.0f} -> {v['more']['tokens']['reasoning_per_call']:.0f}")
    if a.learners:
        res = part4(a.learners)
        (OUT / "learners.json").write_text(json.dumps(res, indent=2) + "\n")
        for k, v in res["per_model"].items():
            print(f"{k:55s} learners {v['n_learners']} F {v['F']:.2f} tau {v['tau']:.2f} (null95 {v['tau_null_95']:.2f}) "
                  f"p {v['p_deranged']:.4f} {v['verdict']}  L_j {v['L_j']['min']:+.2f}..{v['L_j']['max']:+.2f} "
                  f"neg {v['share_L_j_negative']:.2f} null {v['share_L_j_negative_null_95']} "
                  f"above/below signflip {v['learners_above_signflip_null']}/{v['learners_below_signflip_null']} fixed {v['fixed_in_derangement']} holm {v['p_holm']:.3f}")
        print("OVERALL", res["overall"])
        for k, v in res["cross_model_learner_agreement"].items():
            print(f"  {k}: raw rho {v['raw']['spearman_within_tail']:+.2f} p {v['raw']['p_one_sided']:.3f} | "
                  f"question-residualised rho {v['question_residualised']['spearman_within_tail']:+.2f} p {v['question_residualised']['p_one_sided']:.3f}")


if __name__ == "__main__":
    main()
