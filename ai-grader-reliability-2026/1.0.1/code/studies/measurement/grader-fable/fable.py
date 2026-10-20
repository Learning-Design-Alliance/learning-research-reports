"""
Does Paper VI's label effect persist on Claude Fable 5.1? A low-cost two-arm test (2026-10-06).

WHAT WAS ASKED. studies/measurement/grader-model-breadth/ ran Claude Opus 5.5 as Anthropic's frontier
model and skipped Fable 5.1 (the top Anthropic tier) for cost; the maintainer then decided the top tiers
stay unrun. The maintainer has since approved one low-cost test of whether the identical-work label
effect (L, Q2's estimand) persists on Fable. HARD CAP $30 TOTAL, pricing probe included.

DATA. JorGPT (Zenodo 18981627, CC BY 4.0; data/data-sources.json `jorgpt-answers`), read only by the
harness (studies/measurement/grader-eval/harness/stability.ts). THIS SCRIPT NEVER READS THE CORPUS: it
reads the harness's dry-run draw and per-case dumps (answer id, question id, hashed learner id, tail,
teacher mark, the two labels, the two scores), which stay in the session scratchpad. Only aggregates
in out/ are committed. The outcome is a grader's mark on fixed work (outcome-timing tag
`not-a-learner-outcome`).

DRAW (reproducible, seed fixed). The Q2 attainment-swap draw (`--mode attainment-swap --n 300
--dry-run`: 150 answers from learners whose held-out mean is >= 6, then 150 from < 4, in the harness's
order; the swap pairs high case k with low case k, k = 0..149, and shows each the other's held-out
mean). Byte-identical to the draw the Q2 and Opus 5.5 runs used (checked: the fresh dry run equals
scratch grader-vi/draw.json and the ids and swapped labels of the Opus dump). Rule: 50 PAIR indices
k = sorted(numpy.random.default_rng(20261006).choice(150, 50, replace=False)); the subset is high case
k and low case k for each chosen k: 100 answers, 50 per tail. Sampling pairs rather than answers keeps
the label set closed: the 50 high labels and 50 low labels shown are the same set in both tails. The
harness computes labels and pairing on the full draw first (`--ids`), so every subset answer sees
exactly the labels it saw in the 300-answer runs.

ARMS. Two only, on identical answers: the true label and the swapped (opposite tail's) label, so each
answer is graded once under a high label and once under a low label (`--arms true,swapped`). NO CONTROL
ARM: the per-tail drift from an unlabelled grading, and therefore Q2's TOWARD / AWAY (prior vs bias)
reading, is NOT AVAILABLE FOR FABLE. Only the label's effect on the same work is measured.

CONFIGURATION (what is sent; recorded from the live request body in the dump's `run.wire`). The same
prompt (vendor pin 277cd5085, one user message), harness and output-schema handling as Opus 5.5:
OpenRouter `/api/v1/responses`, model `anthropic/claude-fable-5.1`, `text.format = json_object` with
the schema in a prepended system message (provider.ts `relaxStrictSchema`, the zero-retention route),
`reasoning: {exclude: true}` (the harness's OpenRouter default: the model may reason, the trace is not
returned), `max_tokens: 16384` (OpenRouter's required cap), `usage: {include: true}`, host pinned to
Amazon Bedrock with `allow_fallbacks: false` (OPENROUTER_PROVIDER, as Opus 5.5). No temperature, top_p
or seed is sent (Fable's endpoints do not list temperature as a supported parameter in any case).
Fable 5.1's OpenRouter hosts on 2026-10-06: Azure, Anthropic, Amazon Bedrock, Google Vertex (global),
all at $10 / $50 per million input / output tokens.

ESTIMAND. d_i = mark under the high label - mark under the low label on answer i (for a high-tail
answer, true - swapped; for a low-tail answer, swapped - true), out of 10. L = mean d_i over answers
complete in both arms. 95% interval: paired bootstrap resampling whole learners within tail (Q2's
`analyse.cluster_index`), 4,000 replicates, seed 20261006. Also L per tail (high-tail answers / low-tail
answers), with the same intervals. An answer with either arm failed is dropped (complete pairs only);
the count is reported.

PRE-REGISTERED VERDICT (signed: positive = higher under the high label)
  PERSISTS                 the 95% interval lies above 0
  PERSISTS-REVERSED        the 95% interval lies below 0 (a label effect, in the other direction)
  NOT-DETECTED-BOUNDED     not the above, and the 95% interval lies inside (-0.10, +0.10)
  UNRESOLVED               otherwise
Consequence for the model-breadth frontier verdict (`PERSISTS-AT-FRONTIER` needs every frontier model's
95% interval above 0): PERSISTS keeps `PERSISTS-AT-FRONTIER` (now Opus 5.5 and Fable 5.1); any other
Fable verdict makes it `MIXED-AT-FRONTIER`. Reported beside, not as, verdicts: L per tail; the mark
under each label against the teacher's per tail; Opus 5.5's L on the SAME 100 answers from its existing
dump (no new call) and the paired Fable - Opus difference in d.

FLOOR (`--floor`, before any paid call). The Q2 / breadth floor was built at n = 300 answers with a
control arm and does not transfer to n = 100 pairs, so a synthetic floor is run on the real 100-answer
subset (its learners, tails and questions), 400 replicates per world, 1,000 bootstrap draws each:
  shape Q2  Q2's corpus-shaped synthetic grader (analyse.BASE_C/BASE_G, learner sd 0.33, case sd 1.4,
            per-call sd 0.6, integer marks): conservative, d SD about 0.9.
  shape OPUS  d resampled from Opus 5.5's own per-answer d on the 300-answer run, centred, plus the
            planted L (d SD 0.37, half-point marks): the noise of the closest model run.
  worlds    L = 0 (null), +0.28 (Opus 5.5's effect, the smallest observed), -0.28 (direction check),
            +0.10 (the bound).
PASS requires, in BOTH shapes: under L = 0 a PERSISTS / PERSISTS-REVERSED call in <= 10%; at +0.28
PERSISTS in >= 80% and PERSISTS-REVERSED in 0%; at -0.28 PERSISTS-REVERSED in >= 80%. The power of
NOT-DETECTED-BOUNDED under L = 0 is reported (the equivalence power at +/-0.10); it is not required,
so a null result may well read UNRESOLVED, and the README says so. Written and scored by the same
session: a smoke check, reported as one. If the floor fails, no paid call is made.

FLOOR RESULT AND DEVIATION 1 (2026-10-06, recorded and committed BEFORE any paid call; no Fable
number existed). The floor FAILED as pre-registered, narrowly, in the conservative shape only: Q2 shape
PERSISTS at +0.28 in 79.5% (needed >= 80%; Monte Carlo SE about 2%) and PERSISTS-REVERSED at -0.28 in
79.5%; signed calls under L = 0 in 7.2%. The OPUS shape passed every check (power 100% at +/-0.28;
signed calls under L = 0 in 6.5%; equivalence power 60%; PERSISTS at +0.10 in 80%). The pre-registered
consequence was "no paid call". DEVIATION: the run proceeds, for these reasons and with this rule fixed
now. The check that protects a positive (or reversed) verdict, the false signed-call rate under L = 0,
passes in both shapes (<= 7.2%), so a PERSISTS or PERSISTS-REVERSED verdict is not affected by the
failure. What fails is power for a null, in a noise shape (d SD about 0.9) 2.4 times noisier than the
closest model actually run (Opus 5.5, d SD 0.37). RULE: if the verdict is UNRESOLVED, the result is
reported as "no Opus-sized effect excluded" and, if Fable's observed d SD exceeds 0.6 (between the two
shapes), additionally as "the instrument was underpowered at the noise Fable showed" (`underpowered`
in out/fable.json); NOT-DETECTED-BOUNDED is reported with its 60% power in the Opus shape. The floor's
`pass` stays false in out/floor.json; the deviation is recorded beside it, not instead of it.

COST GATE. A 10-answer pricing probe (`--mode schema-probe --n 10`, the seed-7 stratified sample, the
same as every breadth probe; only schema compliance, tokens and OpenRouter-reported cost are read, no
scores). Projection for the run = probe cost / 10 x 200. Proceed only if probe + 1.3 x projection <=
$30; otherwise stop and report. The run uses `--max-calls 220` and `--max-spend` = $30 - probe cost
(the harness aborts, not skips, at either ceiling; 35% failure-rate guard after 30 calls). Spend is
OpenRouter's reported cost.

RESULT (2026-10-06): BLOCKED, no verdict, $0 spent. The pricing probe failed 10/10 at OpenRouter's
routing step ("Filter by Guardrails", reason `zdr-violation-by-account`): all four Fable 5.1 hosts
(Azure, Anthropic, Amazon Bedrock, Google Vertex) are excluded by the account's zero-data-retention
setting, which was not relaxed. One 16-token request per pinned host and one unpinned: the same 404,
before any model ran. Projected cost per grade from Opus 5.5's measured tokens at Fable's list price:
$0.069. Record in out/block.json and the README.

AMENDMENT 1: FABLE VIA CLAUDE CODE SUBAGENTS (2026-10-06; committed BEFORE any agent grading, no Fable
grade existed). Why: the API route above is blocked by the zero-data-retention setting, which stays.
The maintainer approved a different route: the orchestrating Claude Code session spawns subagents
running on Fable, each grading one batch of the prompts the harness would have sent. Preparation in
agent_prepare.py, analysis in agent_analyse.py; the README carries the same text with the check numbers.
  ROUTE. The 200 (answer, arm) request bodies are rendered by the unmodified harness with the
  pre-registered API command (model anthropic/claude-fable-5.1, Bedrock pin) under renderhook.mjs
  (fetch replaced, nothing sent). Identity with the Opus 5.5 API run, by the harness's own input hash:
  200/200 Fable inputs equal the Opus 5.5 inputs for the same (answer, arm) re-rendered on the current
  harness; 900/900 current-harness inputs equal those of the harness committed with the breadth results
  (6265e5a); the Opus 5.5 live dump's recorded wire input (sha256 639d2116c9c9f0b5) is one of them
  (answer 57, control arm: the only body that run recorded); every Fable body's non-input fields equal
  the Opus live body's except `model`; true and swapped bodies of each answer differ only in the
  attainment line. The prompts are packed into 20 batches of 10 (seed 20261007): 5 true-arm and 5
  swapped-arm items per batch, 5 high and 5 low labels shown per batch, never both arms of one answer
  in a batch, random order, opaque item ids; each batch file is a fixed one-sentence preamble, the items
  (messages verbatim, delimited, plus the output schema) and a fixed closing line asking for a JSON
  array of {item_id, score, evaluation}. Nothing in the wrapper names the study, the label, arms or other
  items. sha256 of every batch, the key and every prompt: out/agent-manifest.json, committed with this
  amendment. One fresh subagent per batch, handed the batch text and nothing else; its final message is
  saved verbatim to <scratch>/fable-agent/results/batch_NN.json. A batch whose agent returns no final
  message at all (an infrastructure failure) may be re-run ONCE with a fresh agent; any returned
  message, parseable or not, is final. A batch whose agent read anything under <scratch>/fable-agent/
  (the key or prompts would reveal case and arm) is excluded: its items are missing.
  DIFFERENCES FROM THE API CONDITION (none removable on this route): (1) the agent harness's own system
  prompt, tool definitions and environment context precede the item and are not controlled; the API run
  sent only the schema system message and the user message. (2) The two messages arrive as delimited
  text inside one user turn, not as API roles. (3) Ten items share one context: within-batch order and
  carry-over (including the other items' labels) are possible; balanced across arms and labels by design,
  not removed. (4) Structured output by instruction only: no json_object mode, and the closing line asks
  for {item_id, score, evaluation}, not the item schema's object (whose required xapiStatements the API
  model generated). (5) No sampling or reasoning settings are known or recorded (the API run sent no
  temperature/top_p/seed either, but did send reasoning exclude and max_tokens 16384). (6) The model is
  whatever the session's "fable" alias serves, with no host pin; the orchestrator records it from the
  session metadata (e.g. last_served_model) and passes it as --model-served; if it cannot be determined
  the result says so. (7) No token or cost accounting. (8) Missingness is correlated within a batch.
  UNCHANGED. Draw, arms, estimand L, the paired bootstrap clustered by learner within tail (4,000
  replicates, seed 20261006), per-tail L, the verdict strings and thresholds (PERSISTS /
  PERSISTS-REVERSED / NOT-DETECTED-BOUNDED inside +/-0.10 / UNRESOLVED).
  ADDED RULES. The result is reported as "Fable 5.1 as an agent", never pooled with the API runs, and is
  reported beside, not inside, the model-breadth frontier verdict (which stays on Opus 5.5 via the API).
  PARSE: an item whose output does not parse or does not meet the schema's score (a number in [0, 10])
  and evaluation (a string) is missing; one enclosing code fence around the array is tolerated and
  counted; the pair is dropped; counts reported; MORE THAN 20 OF THE 100 ANSWERS WITHOUT A COMPLETE PAIR
  -> UNRESOLVED regardless of the interval. FLOOR: the floor fell just short (79.5% vs 80% at Q2-shaped
  noise), so a NOT-DETECTED-BOUNDED or UNRESOLVED result is reported as underpowered. Opus 5.5's L on
  the same answers is reported beside, labelled as API vs agent.

RESULT (Amendment 1, 2026-10-06): PERSISTS. Fable 5.1 as an agent, L = +0.31 [+0.19, +0.45] on 99 of
  100 pairs (one item not returned, batch 13); high tail +0.44 [+0.31, +0.57], low +0.19 [-0.06, +0.43];
  Opus 5.5 via the API on the same answers +0.34 [+0.26, +0.43]. All 20 agents were served
  claude-fable-5-1 (their transcripts), and each read only its own batch, so none is excluded.
  Deviation 2 (after the run): each agent read a byte-identical copy of its batch from an isolated
  directory with its file tool, rather than receiving it inline. Detail in README.md.

Usage:
  python3 fable.py --draw <scratch>/fable/draw300.json --ids-out <scratch>/fable/ids.json
  python3 fable.py --floor --draw <scratch>/fable/draw300.json --opus <scratch>/breadth/swap-opus55.json
  python3 fable.py --analyse <scratch>/fable/swap-fable.json --opus <scratch>/breadth/swap-opus55.json \
      --probe-cost <usd>
  Amendment 1:
  python3 agent_prepare.py --render <scratch>; python3 agent_prepare.py --batches <scratch>
  python3 agent_analyse.py --scratch <scratch> --selftest
  python3 agent_analyse.py --scratch <scratch> --model-served "<model>" --opus <scratch>/breadth/swap-opus55.json
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
BREADTH = HERE.parent / "grader-model-breadth"
sys.path.insert(0, str(Q2))
sys.path.insert(0, str(BREADTH))
import analyse as q2  # noqa: E402  (Q2's cluster bootstrap and synthetic base, unchanged)
import breadth  # noqa: E402  (its corpus-shaped synthetic grader, unchanged)

SEED = 20261006
N_PAIRS = 50
MARGIN = 0.10
REPS = 4000
FLOOR_REPS = 400
FLOOR_BOOT = 1000
CAP_USD = 30.0
RUN_CALLS = 200
OPUS_L = 0.28
# Deviation 1 (docstring): the floor failed narrowly in the Q2 shape; recorded before any paid call.
DEVIATION_1 = ("floor FAILED narrowly in the Q2 shape (power 0.795 at +/-0.28, needed 0.80); passed in the OPUS shape; "
               "false signed calls <= 7.2% in both; run proceeds by recorded deviation 1, made before any paid call")
UNDERPOWERED_SD = 0.6


def d_of(rows: list[dict]) -> np.ndarray:
    """High-label mark minus low-label mark on the same answer (breadth.hl, Q2's L at case level)."""
    return breadth.hl(rows)


def draw(draw300: Path, ids_out: Path) -> dict:
    rows = json.loads(Path(draw300).read_text())["rows"]
    hi = [r for r in rows if r["tail"] == "high"]
    lo = [r for r in rows if r["tail"] == "low"]
    assert len(hi) == len(lo) == 150 and rows[:150] == hi, "not the Q2 draw's 150/150 order"
    k = sorted(int(x) for x in np.random.default_rng(SEED).choice(150, N_PAIRS, replace=False))
    sub = [hi[i] for i in k] + [lo[i] for i in k]
    for i in k:  # the pairing the harness uses: each shows the other's held-out mean
        assert hi[i]["labelSwapped"] == lo[i]["labelTrue"] and lo[i]["labelSwapped"] == hi[i]["labelTrue"]
    ids = [str(r["id"]) for r in sub]
    Path(ids_out).write_text(json.dumps({"ids": ids}) + "\n")
    rec = {
        "rule": f"pair indices k = sorted(numpy.random.default_rng({SEED}).choice(150, {N_PAIRS}, replace=False)); "
                "subset = high case k and low case k of the Q2 attainment-swap draw (--n 300 --dry-run)",
        "seed": SEED, "pair_indices": k, "answer_ids": ids,
        "n_answers": len(sub),
        "learners": {"high": len({r["learnerId"] for r in sub if r["tail"] == "high"}),
                     "low": len({r["learnerId"] for r in sub if r["tail"] == "low"})},
        "learners_in_full_draw": {"high": len({r["learnerId"] for r in hi}), "low": len({r["learnerId"] for r in lo})},
        "questions": len({r["questionId"] for r in sub}),
        "label_gap_mean": float(np.mean([r["labelTrue"] - r["labelSwapped"] for r in sub if r["tail"] == "high"])),
    }
    return rec


# ----------------------------------------------------------------------------- estimand

def cluster_stats(rows: list[dict], rng: np.random.Generator, reps: int = REPS) -> dict:
    d = d_of(rows)
    hi = np.array([r["tail"] == "high" for r in rows])
    learner = np.array([str(r["learnerId"]) for r in rows])
    h = np.array([r["human"] for r in rows], float)
    hl_mark = np.array([r["trueLabel"] if r["tail"] == "high" else r["swappedLabel"] for r in rows], float)
    ll_mark = np.array([r["swappedLabel"] if r["tail"] == "high" else r["trueLabel"] for r in rows], float)

    def st(idx: np.ndarray) -> dict[str, float]:
        out = {"L": d[idx].mean()}
        for k, m in (("high", hi[idx]), ("low", ~hi[idx])):
            out[f"L_{k}"] = d[idx][m].mean()
            out[f"err_highlabel_{k}"] = (hl_mark - h)[idx][m].mean()
            out[f"err_lowlabel_{k}"] = (ll_mark - h)[idx][m].mean()
        return {k: float(v) for k, v in out.items()}

    point = st(np.arange(len(d)))
    draws = {k: [] for k in point}
    for _ in range(reps):
        for k, v in st(q2.cluster_index(learner, hi, rng)).items():
            draws[k].append(v)
    res = {k: {"est": v, "ci95": [float(np.percentile(draws[k], 2.5)), float(np.percentile(draws[k], 97.5))]}
           for k, v in point.items()}
    res["n_pairs"] = len(d)
    res["n_learners"] = int(len(set(learner)))
    res["d_sd"] = float(d.std(ddof=1))
    res["d_values"] = {str(v): int(c) for v, c in zip(*np.unique(d, return_counts=True))}
    return res


def verdict(ci: list[float]) -> str:
    lo, hi = ci
    if lo > 0:
        return "PERSISTS"
    if hi < 0:
        return "PERSISTS-REVERSED"
    if -MARGIN < lo and hi < MARGIN:
        return "NOT-DETECTED-BOUNDED"
    return "UNRESOLVED"


def quick_ci(d: np.ndarray, learner: np.ndarray, hi: np.ndarray, rng: np.random.Generator, reps: int) -> list[float]:
    # Precompute cluster membership once: the floor runs this 400 x 8 times.
    strata = []
    for t in (True, False):
        ids = np.unique(learner[hi == t])
        strata.append([np.flatnonzero((learner == g) & (hi == t)) for g in ids])
    sums = [np.array([d[m].sum() for m in s]) for s in strata]
    cnts = [np.array([len(m) for m in s]) for s in strata]
    est = np.empty(reps)
    for b in range(reps):
        tot = n = 0.0
        for s, c in zip(sums, cnts):
            pick = rng.integers(0, len(s), len(s))
            tot += s[pick].sum()
            n += c[pick].sum()
        est[b] = tot / n
    return [float(np.percentile(est, 2.5)), float(np.percentile(est, 97.5))]


# ----------------------------------------------------------------------------- floor

def floor(draw300: Path, opus: Path) -> dict:
    rows = json.loads(Path(draw300).read_text())["rows"]
    ids = set(json.loads((OUT / "draw.json").read_text())["answer_ids"])
    sub = [r for r in rows if str(r["id"]) in ids]
    assert len(sub) == 100
    learner = np.array([str(r["learnerId"]) for r in sub])
    hi = np.array([r["tail"] == "high" for r in sub])
    o = [r for r in json.loads(Path(opus).read_text())["rows"] if None not in (r["trueLabel"], r["swappedLabel"])]
    e_opus = d_of(o) - d_of(o).mean()
    rng = np.random.default_rng(SEED + 1)
    worlds = {"null": 0.0, "opus_effect": OPUS_L, "reversed": -OPUS_L, "bound": MARGIN}
    rep: dict = {"n_answers": len(sub), "replicates": FLOOR_REPS, "bootstrap": FLOOR_BOOT, "shapes": {}}
    ok = True
    for shape in ("Q2", "OPUS"):
        rep["shapes"][shape] = {}
        for w, L in worlds.items():
            got = []
            for _ in range(FLOOR_REPS):
                if shape == "Q2":
                    syn, _ = breadth.synth_pair(sub, rng, L, L)
                    d = d_of(syn)
                else:
                    d = L + rng.choice(e_opus, len(sub), replace=True)
                got.append(verdict(quick_ci(d, learner, hi, rng, FLOOR_BOOT)))
            rates = {v: got.count(v) / len(got) for v in ("PERSISTS", "PERSISTS-REVERSED", "NOT-DETECTED-BOUNDED", "UNRESOLVED")}
            rep["shapes"][shape][w] = {"L": L, "rates": rates}
            print(f"  {shape:4s} {w:12s} L {L:+.2f}  " + "  ".join(f"{k} {v:.3f}" for k, v in rates.items()))
        s = rep["shapes"][shape]
        checks = {
            "null_false_signed_le_0.10": s["null"]["rates"]["PERSISTS"] + s["null"]["rates"]["PERSISTS-REVERSED"] <= 0.10,
            "opus_effect_persists_ge_0.80": s["opus_effect"]["rates"]["PERSISTS"] >= 0.80,
            "opus_effect_no_wrong_sign": s["opus_effect"]["rates"]["PERSISTS-REVERSED"] == 0.0,
            "reversed_called_ge_0.80": s["reversed"]["rates"]["PERSISTS-REVERSED"] >= 0.80,
        }
        s["checks"] = checks
        s["power_at_0.28"] = s["opus_effect"]["rates"]["PERSISTS"]
        s["equivalence_power_at_0.10_under_null"] = s["null"]["rates"]["NOT-DETECTED-BOUNDED"]
        ok &= all(checks.values())
    rep["opus_d_sd"] = float(d_of(o).std(ddof=1))
    rep["pass"] = bool(ok)
    rep["note"] = "smoke check: synthetic graders written and scored by the same session"
    return rep


# ----------------------------------------------------------------------------- analysis

def analyse(dump: Path, opus: Path, probe_cost: float | None) -> dict:
    blob = json.loads(Path(dump).read_text())
    ids = json.loads((OUT / "draw.json").read_text())["answer_ids"]
    assert sorted(str(r["id"]) for r in blob["rows"]) == sorted(ids), "dump is not the pre-registered subset"
    rows = [r for r in blob["rows"] if r["trueLabel"] is not None and r["swappedLabel"] is not None]
    rng = np.random.default_rng(SEED)
    res = cluster_stats(rows, rng)
    v = verdict(res["L"]["ci95"])
    tails = {k: verdict(res[f"L_{k}"]["ci95"]) for k in ("high", "low")}
    # Opus 5.5 on the same answers, from its existing dump (no new call). Reported only.
    op_all = {str(r["id"]): r for r in json.loads(Path(opus).read_text())["rows"]}
    op_rows = [op_all[str(r["id"])] for r in rows]
    opus_res = cluster_stats(op_rows, np.random.default_rng(SEED))
    diff_rows = [{**f, "trueLabel": f["trueLabel"] - o["trueLabel"], "swappedLabel": f["swappedLabel"] - o["swappedLabel"]}
                 for f, o in zip(rows, op_rows)]
    diff = cluster_stats(diff_rows, np.random.default_rng(SEED))
    run = blob.get("run") or {}
    spend = run.get("reportedSpendUsd")
    graded = run.get("tokens", {}).get("withUsage") or 0
    out = {
        "model": blob.get("model"), "runStamp": blob.get("runStamp"), "arms": blob.get("arms"),
        "temperature": blob.get("temperature"), "reasoning": blob.get("reasoning"),
        "n_answers_asked": len(blob["rows"]), "n_complete_pairs": len(rows),
        "verdict": v, "verdict_rule": {"PERSISTS": "95% CI > 0", "PERSISTS-REVERSED": "95% CI < 0",
                                       "NOT-DETECTED-BOUNDED": f"95% CI inside (-{MARGIN}, +{MARGIN})", "UNRESOLVED": "otherwise"},
        "tail_readings_reported_only": tails,
        "fable": res,
        "opus55_same_answers_reported_only": {k: opus_res[k] for k in ("L", "L_high", "L_low", "n_pairs", "d_sd")},
        "fable_minus_opus55_dL_reported_only": {k: diff[k] for k in ("L", "L_high", "L_low")},
        "floor": {"pass": json.loads((OUT / "floor.json").read_text())["pass"], "deviation_1": DEVIATION_1},
        "underpowered": bool(v == "UNRESOLVED" and res["d_sd"] > UNDERPOWERED_SD),
        "frontier_verdict_with_fable": "PERSISTS-AT-FRONTIER" if v == "PERSISTS" else "MIXED-AT-FRONTIER",
        "run": {"calls": run.get("calls"), "failures": run.get("failures"), "tokens": run.get("tokens"),
                "served": run.get("served"), "wire": run.get("wire")},
        "cost": {"run_openrouter_reported_usd": spend, "probe_openrouter_reported_usd": probe_cost,
                 "total_usd": None if spend is None else round(spend + (probe_cost or 0), 4),
                 "gradings": graded, "cost_per_grade_usd": None if not (spend and graded) else spend / graded,
                 "per_8000_grades_usd": None if not (spend and graded) else 8000 * spend / graded,
                 "cap_usd": CAP_USD},
    }
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--draw", type=Path)
    ap.add_argument("--ids-out", type=Path)
    ap.add_argument("--floor", action="store_true")
    ap.add_argument("--opus", type=Path)
    ap.add_argument("--analyse", type=Path)
    ap.add_argument("--probe-cost", type=float)
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    if a.floor:
        rep = floor(a.draw, a.opus)
        (OUT / "floor.json").write_text(json.dumps(rep, indent=2) + "\n")
        print("FLOOR", "PASS" if rep["pass"] else "FAIL")
        sys.exit(0 if rep["pass"] else 1)
    if a.analyse:
        fl = json.loads((OUT / "floor.json").read_text())
        if not (fl["pass"] or DEVIATION_1):
            sys.exit("floor did not pass; no real number is read")
        res = analyse(a.analyse, a.opus, a.probe_cost)
        (OUT / "fable.json").write_text(json.dumps(res, indent=2) + "\n")
        f = res["fable"]
        g = lambda k, R=f: f"{R[k]['est']:+.2f} [{R[k]['ci95'][0]:+.2f}, {R[k]['ci95'][1]:+.2f}]"  # noqa: E731
        print(f"Fable n={res['n_complete_pairs']} L {g('L')}  high {g('L_high')}  low {g('L_low')}  -> {res['verdict']}")
        o = res["opus55_same_answers_reported_only"]
        print(f"Opus 5.5 same answers L {g('L', o)} high {g('L_high', o)} low {g('L_low', o)}")
        print(f"Fable - Opus dL {g('L', res['fable_minus_opus55_dL_reported_only'])}")
        print("cost", res["cost"])
        return
    if a.draw:
        rec = draw(a.draw, a.ids_out)
        (OUT / "draw.json").write_text(json.dumps(rec, indent=2) + "\n")
        print({k: v for k, v in rec.items() if k not in ("answer_ids", "pair_indices")})


if __name__ == "__main__":
    main()
