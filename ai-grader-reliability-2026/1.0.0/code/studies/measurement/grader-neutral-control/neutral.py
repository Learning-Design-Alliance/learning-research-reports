"""
Does a sentence about the student move the mark just by being there? A size-matched neutral control
for Paper VI's penalty, reward and toward/away readings (2026-10-06).

WHAT WAS ASKED. Paper VI (research/article/attainment-bias-in-llm-grading.md, release
ai-grader-reliability-2026) shows an LLM short-answer grader the sentence "Current attainment for
this learner across this course: x/10, from n prior graded responses." Its main estimand, L (the
mark under a high label minus under a low label on the same answer, swapped-label arm), is immune to a
presence effect: both arms carry a sentence of the same length and template. Two other readings are
not. Both compare the labelled arm with a CONTROL THAT HAS NO ADDED TEXT:
  * the "penalty" (the true low label's drift from control in the low tail) and the "reward" (the
    true high label's drift from control in the high tail);
  * the toward/away reading (grader-attainment-prior revision 3: whether the label moves a tail's
    marks toward or away from the teacher's, from the control's signed error and the label's drift).
Each mixes "a sentence about the student is present" with "what the sentence says". CLAUDE.md: a
control has to be the size of the thing it controls for. On ASAP 2.0 a same-length mid label moved
marks by being present (studies/measurement/grader-attainment-groups/), and Kapetanovic et al. 2026
found the presence of a prior score mattered more than its value. The maintainer: "let's run the
study. simple."

THE DATA. JorGPT (Zenodo 18981627, CC BY 4.0; data/data-sources.json `jorgpt-answers`), read ONLY by
the harness. This script never reads the corpus. It reads per-case dumps (ids, learner ids, tail,
teacher mark, labels, label sentence length, the model's marks), which stay in the session
scratchpad; only aggregates in out/ are committed. For the floor it also reads the two existing
Gemini 3.5 Flash Lite dumps of this draw (grader-attainment-prior's `grader-vi/swap-gemini.json`
and grader-model-breadth's `breadth/swap-lite-rerun.json`, both hashed in
studies/measurement/grader-eval/analyses/per-case-dumps.sha256) for the shape of the grader's marks
and its call-to-call noise. Those numbers are already published; nothing from THIS study's run is
read before the floor passes.

THE DRAW. The 300-answer attainment draw of grader-attainment-prior (Q2), unchanged: `attainmentDraw`
in studies/measurement/grader-eval/harness/stability.ts, 150 answers whose learner's held-out mean
teacher mark is >= 6 (19 learners) and 150 whose is < 4 (14 learners). A dry run of the new arm set
reproduces Q2's rows (id, question, learner, tail, teacher mark, both labels) exactly.

THE ARMS, ALL IN ONE RUN (`--mode attainment-swap --n 300 --arms control,neutral,true,swapped`), so
run-to-run noise (about +/-0.07 on L between two Gemini runs, grader-model-breadth) does not enter
any contrast:
  control   no added text (the shipped configuration; the line the sentence would occupy is empty)
  neutral   NEUTRAL_TEXT below, on the same line of the prompt as the attainment sentence
  true      the learner's own held-out attainment (the paper's arm)
  swapped   the opposite tail's attainment sentence (Q2's arm)
The swapped arm is kept because it is cheap (300 Gemini calls, about $0.30) and buys two things:
the harness's identical-work pairing stays as it is (its assertion that true and swapped are both
present is untouched), and L is re-measured inside this run, so this run can be checked against Q2
(L +0.37) before anything new in it is read.

THE NEUTRAL SENTENCE, fixed here before any call:
  "Current context for this learner across this course: this response was submitted as coursework."
95 characters. The attainment sentence renders at 94-95 characters on this draw (mean 94.99), so the
ratio is 1.000; the rule is +/-10%. Same opening, register and slot as the attainment sentence
("Current ... for this learner across this course: ..."). It carries no number and nothing that
varies by student: it is the same string for every answer, and it is true of every answer. The rule
is asserted twice: in the harness before any call (length within +/-10% of the mean rendered
attainment sentence over the full draw; no digit), and here on the dump (its recorded neutral text
equals NEUTRAL_TEXT; mean of the recorded `labelTrueChars` within +/-10%; no digit). An offline
render with fetch replaced (one answer, four arms; nothing sent) showed the four prompts differ only
on that line, and the request bodies are otherwise identical.

THE MODEL. google:gemini-3.5-flash-lite, the shipped tier, configured exactly as in Q2 and the
breadth re-run: Google direct, the current harness, no temperature, top-p, seed or token limit sent,
thinkingLevel "minimal" (the SDK default the harness leaves alone), responseSchema JSON mode, prompt
pinned to the vendored product prompt (vendor pin 277cd5085). The request body, billed tokens and
served model are taken from the dump's run record, as earlier runs did.

THE UNIT. The label is a learner property and so is anything the grader infers from a sentence about
"this learner". Every interval is a LEARNER-CLUSTER bootstrap within tail (resample learners with
replacement inside each tail, keep all their answers), 4,000 replicates, percentile: Q2's scheme.
Implemented by multinomial learner weights on per-learner sums, which is the same resample.

ESTIMANDS (all signed; per tail k in {high, low}; paired on answers complete in all four arms;
"score" is the grader's mark, h the teacher's):
  P_k      presence effect       mean(neutral - control)
  VN_k     value vs neutral      mean(true - neutral)   (low tail: the PENALTY; high tail: the REWARD)
  VC_k     value vs control      mean(true - control)   (the paper's penalty/reward; VC = VN + P)
  B_arm_k  signed error          mean(arm - h)
  L, L_k   identical-work label effect, as Q2 (reproduction check, not a new claim)
  Toward/away: Q2 revision 3's `tail_direction`, imported unchanged from
  grader-attainment-prior/analyse.py, read twice: with the control as the reference (drift VC_k,
  reference B_control_k) and with the neutral arm as the reference (drift VN_k, reference
  B_neutral_k). FLAT / AWAY / TOWARD / UNRESOLVED per tail; the rule is not modified.

PRE-REGISTERED VERDICTS (written and committed before any model call; see the git log).

  PRESENCE (margin M = 0.10 marks; per-tail tests Bonferroni-corrected over the two tails):
    PRESENCE-EFFECT             some tail's P_k 97.5% interval excludes 0. The sign of each tail is
                                named ("+" raises marks, "-" lowers them, "0" unresolved); opposite
                                signs in the two tails are reported as such, not netted.
    NO-PRESENCE-EFFECT-BOUNDED  no tail resolved, and both tails' P_k 90% intervals lie inside
                                +/-M (TOST at alpha 0.05 per tail; intersection-union, no correction).
    UNRESOLVED                  otherwise; read as "no presence effect larger than X", X the largest
                                absolute 95% bound over the two tails.
    Why 0.10: Gemini's per-tail value effects in Q2 were +0.24 (high) and -0.22 (low); a presence
    effect under 0.10 leaves more than half of each in place, which is what "the readings survive"
    needs. It is also Q4's MAE margin (1% of the scale).

  READINGS:
    For each tail, the value-effect class against each reference: "+" / "-" if its 95% interval lies
    above / below 0, "0" otherwise; and the toward/away call against each reference.
    READINGS-HOLD    in both tails, class(VN_k) == class(VC_k) and direction(neutral reference) ==
                     direction(control reference).
    READINGS-CHANGE  otherwise, naming each change, e.g. "low-tail penalty: - vs control -> 0 vs
                     neutral" or "high-tail direction: UNRESOLVED vs control -> AWAY vs neutral".
    (Revised before any call: revision 1 splits READINGS-CHANGE into CHANGE and FRAGILE; see FLOOR
    RECORD below.)
    Q2's combined verdict (PRIOR / BIAS / MIXED / UNRESOLVED, from both tails and L) is reported
    against each reference too; it changes only if a tail call changes.

THE FLOOR (`--floor`), before any paid call. Synthetic graders on the real draw (real teacher marks,
tails, labels and learner clusters). Each answer's latent mark is the mean of Gemini's two existing
control marks on it plus a uniform jitter of +/-0.25; each arm adds its planted effect and a call
noise e ~ N(0, sigma), and is rounded half-up to Gemini's 0.5-point grid and clipped to 0..10. sigma
is calibrated so two null calls agree as often, and differ by as much, as Gemini's two control runs
on this draw (identical on 76% of answers, SD of the difference 0.35); across runs, so if anything
noisier than within one run. Planted effects carry heterogeneity: presence learner SD 0.10 and answer
SD 0.20 (shared by the three sentence arms, since all three carry a sentence); value learner SD 0.10
and answer SD 0.40 (so the true-minus-control SD per tail matches Gemini's ~0.6). Value effects by
label shown, vs neutral: high label +0.22, low label -0.22 (Gemini's Q2 drifts). Worlds, 200
replicates each, the instrument above unchanged, 4,000 bootstrap replicates:
  NULL     P = 0 in both tails      presence: PRESENCE-EFFECT in <= 10%; READINGS-HOLD in >= 80%;
                                    VN signed and resolved (+ high, - low) in >= 80% per tail.
                                    The rate of NO-PRESENCE-EFFECT-BOUNDED is reported; if it is below
                                    80% that verdict is declared unreachable and an unresolved
                                    presence effect is read only as an interval ("no presence effect
                                    larger than X").
  PRES+    P = +0.20 both tails     PRESENCE-EFFECT with no tail "-" in >= 80%; any tail "-" <= 5%.
  PRES-    P = -0.20 both tails     the mirror.
  CHANGE   P = -0.22 high tail only READINGS-CHANGE in >= 80% (the high-tail reward vs control is
                                    planted at 0 while vs neutral it is +0.22).
A synthetic grader written and scored by the same session is a smoke check of the instrument's logic
on worlds it was told about, not a validation of a construct, and is reported as one.

FLOOR RECORD: REVISION 0 FAILED; REVISION 1 PASSED, BOTH BEFORE ANY MODEL CALL (out/floor-rev0.json,
out/floor.json). Revision 0 failed on one check: under NULL, READINGS-HOLD came back in 73% (< 80%).
The flips were almost all the high tail's toward/away call (AWAY <-> UNRESOLVED): Gemini's control
error in the high tail is +0.20 [-0.02, +0.44] on this draw, on the edge of resolution, so swapping
the reference for one that differs from it by noise flips the call. Its noise model was also off
(one normal: 72% identical marks, SD 0.27, against Gemini's 76% and 0.35). Revision 1, settled on
the synthetic worlds alone:
  * call noise is a two-component mixture (near: N(0, s1); with probability q, far: N(0, s2)),
    calibrated to Gemini's identical-mark rate, SD of the difference and rate of whole-point jumps
    (76% / 0.35 / 8.3%); the fit is (s1, q, s2) = (0.08, 0.08, 0.9), giving 74% / 0.37 / 5.3%;
  * the readings verdict gains a third value. A call that changes in a tail whose presence effect is
    resolved (97.5%) is READINGS-CHANGE; a call that changes while that tail's presence effect is
    unresolved is READINGS-FRAGILE (the reading sits on its own resolution boundary: moving the
    reference by an amount indistinguishable from 0 flips it); otherwise READINGS-HOLD. The NULL
    check becomes READINGS-CHANGE <= 10%, the CHANGE world's READINGS-CHANGE >= 80%.
Revision 1 results (200 replicates per world): NULL false PRESENCE-EFFECT 9.0%, READINGS-CHANGE 4.0%
(FRAGILE 28.5%, HOLD 67.5%), VN signed and resolved 97% (high) / 94% (low); PRES+ and PRES- signed
PRESENCE-EFFECT 100%, no wrong sign; CHANGE world READINGS-CHANGE 97.5%. NO-PRESENCE-EFFECT-BOUNDED
came back in only 23.5% under NULL, so by the pre-registered rule it is UNREACHABLE here: an
unresolved presence effect is read only as "no presence effect larger than X". And FRAGILE is common
under NULL (28.5%), so a FRAGILE result says a reading is boundary-sitting, not that presence moved it.

THE GATE. `--dump` refuses to read a real dump unless out/floor.json exists and passed (or its
shortfall is recorded in the README with a pre-run revision, as Q2 did).

COST. Cap $5. About 1,200 calls; Gemini 3.5 Flash Lite at list price ($0.30 / $2.50 per million in /
out) with Q2's ~980 in / ~300 out tokens per call: about $1.25. The run uses --max-calls 1300 (the
harness's call ceiling; Google reports no spend, so the call cap is the binding guard) and the
harness's 35% failure guard. Spend = billed tokens x list price, from the dump's run record.

Usage:
  python3 neutral.py --floor
  python3 neutral.py --dump <scratch>/neutral/swap-neutral-lite.json
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
SCRATCH = Path("/tmp/claude-0/-home-user-Learning-engineering-research/3e89eb50-bc6b-5ed8-9fc9-e24fd022b13f/scratchpad")

# Q2's revision-3 toward/away rule and its combined verdict, imported unchanged (one copy of the rule).
_spec = importlib.util.spec_from_file_location("q2", HERE.parent / "grader-attainment-prior" / "analyse.py")
q2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(q2)

NEUTRAL_TEXT = "Current context for this learner across this course: this response was submitted as coursework."
REPS = 4000
FLOOR_REPS = 200
MARGIN = 0.10
PRICE = (0.30, 2.50)          # gemini-3.5-flash-lite, USD per million tokens in / out (as grader-model-breadth/spend.py)
CAP_USD = 5.0
TAILS = ("high", "low")
Q2_GEMINI = {"L": 0.368, "drift_high": 0.243, "drift_low": -0.223}   # grader-attainment-prior/out/results.json


def check_neutral(blob: dict) -> dict:
    """The size-matched control's rule, on the dump itself."""
    assert blob.get("neutralText") == NEUTRAL_TEXT, "dump's neutral sentence is not the pre-registered one"
    lens = np.array([r["labelTrueChars"] for r in blob["rows"]], float)
    ratio = len(NEUTRAL_TEXT) / lens.mean()
    assert abs(ratio - 1) <= 0.10, f"neutral length {len(NEUTRAL_TEXT)} outside +/-10% of {lens.mean():.2f}"
    assert not any(ch.isdigit() for ch in NEUTRAL_TEXT), "neutral sentence carries a number"
    return {"neutral_chars": len(NEUTRAL_TEXT), "attainment_chars_mean": float(lens.mean()),
            "attainment_chars_range": [int(lens.min()), int(lens.max())], "ratio": float(ratio)}


# ----------------------------------------------------------------------------- the instrument

COLS = ("P", "VN", "VC", "Bc", "Bn", "Bt", "Bs", "HL")


def case_matrix(h, c, n, t, s, hi) -> np.ndarray:
    hl = np.where(hi, t - s, s - t)          # mark under the high label minus under the low label
    return np.stack([n - c, t - n, t - c, c - h, n - h, t - h, s - h, hl], axis=1)


class Boot:
    """Learner-cluster bootstrap within tail via multinomial learner weights. Every estimand here is a
    per-tail mean, so a resample is (weights @ per-learner sums) / (weights @ per-learner counts)."""

    def __init__(self, learner: np.ndarray, hi: np.ndarray, reps: int, rng: np.random.Generator):
        self.parts = {}
        for k, m in (("high", hi), ("low", ~hi)):
            ids, inv = np.unique(learner[m], return_inverse=True)
            G = np.zeros((len(ids), m.sum()))
            G[inv, np.arange(m.sum())] = 1
            W = rng.multinomial(len(ids), np.full(len(ids), 1 / len(ids)), size=reps).astype(float)
            self.parts[k] = (m, G, W)

    def run(self, X: np.ndarray) -> dict:
        res, tot_s, tot_n, pt_s, pt_n = {}, 0, 0, 0, 0
        for k, (m, G, W) in self.parts.items():
            S, cnt = G @ X[m], G.sum(1)
            draws = (W @ S) / (W @ cnt)[:, None]
            point = X[m].mean(0)
            for j, name in enumerate(COLS):
                res[f"{name}_{k}"] = summarise(point[j], draws[:, j])
            tot_s, tot_n = tot_s + W @ S, tot_n + W @ cnt
            pt_s, pt_n = pt_s + X[m].sum(0), pt_n + m.sum()
        pooled = tot_s / tot_n[:, None]
        for j, name in enumerate(COLS):
            res[name] = summarise(pt_s[j] / pt_n, pooled[:, j])
        return res


def summarise(est: float, d: np.ndarray) -> dict:
    q = np.percentile(d, [1.25, 2.5, 5, 95, 97.5, 98.75])
    return {"est": float(est), "ci95": [float(q[1]), float(q[4])], "ci90": [float(q[2]), float(q[3])],
            "ci975": [float(q[0]), float(q[5])]}


def sign_class(ci: list[float]) -> str:
    return "+" if ci[0] > 0 else "-" if ci[1] < 0 else "0"


def directions(r: dict, ref: str) -> dict:
    """Q2's tail_direction and verdict_q2 with `ref` ("control" or "neutral") as the reference arm."""
    key_drift, key_ref = ("VC", "Bc") if ref == "control" else ("VN", "Bn")
    d = {"L": r["HL"]}
    for k in TAILS:
        d[f"drift_{k}"] = r[f"{key_drift}_{k}"]
        d[f"bias_control_{k}"] = r[f"{key_ref}_{k}"]
        d[f"bias_true_{k}"] = r[f"Bt_{k}"]
    return q2.verdict_q2(d)


def verdicts(r: dict) -> dict:
    tail_sign = {k: sign_class(r[f"P_{k}"]["ci975"]) for k in TAILS}
    if any(v != "0" for v in tail_sign.values()):
        pv = "PRESENCE-EFFECT"
    elif all(-MARGIN < r[f"P_{k}"]["ci90"][0] and r[f"P_{k}"]["ci90"][1] < MARGIN for k in TAILS):
        pv = "NO-PRESENCE-EFFECT-BOUNDED"
    else:
        pv = "UNRESOLVED"
    largest = max(abs(x) for k in TAILS for x in r[f"P_{k}"]["ci95"])
    dir_c, dir_n = directions(r, "control"), directions(r, "neutral")
    changes, changed_tails = [], set()
    for k, what in (("high", "reward"), ("low", "penalty")):
        a, b = sign_class(r[f"VC_{k}"]["ci95"]), sign_class(r[f"VN_{k}"]["ci95"])
        if a != b:
            changes.append(f"{k}-tail {what}: {a} vs control -> {b} vs neutral")
            changed_tails.add(k)
        if dir_c[f"{k}_tail"] != dir_n[f"{k}_tail"]:
            changes.append(f"{k}-tail direction: {dir_c[f'{k}_tail']} vs control -> {dir_n[f'{k}_tail']} vs neutral")
            changed_tails.add(k)
    # REVISION 1 (floor record): a call that flips while that tail's presence effect is unresolved has
    # moved by an amount indistinguishable from 0. It says the reading sits on its own resolution
    # boundary (FRAGILE), not that the presence of a sentence changed it (CHANGE).
    resolved = {k for k in changed_tails if tail_sign[k] != "0"}
    rv = "READINGS-CHANGE" if resolved else "READINGS-FRAGILE" if changes else "READINGS-HOLD"
    return {
        "presence": {"verdict": pv, "tail_sign_975": tail_sign, "margin": MARGIN,
                     "no_presence_effect_larger_than": largest},
        "readings": {"verdict": rv, "changes": changes, "changed_tails_with_resolved_presence": sorted(resolved),
                     "value_class": {k: {"vs_control": sign_class(r[f"VC_{k}"]["ci95"]),
                                         "vs_neutral": sign_class(r[f"VN_{k}"]["ci95"])} for k in TAILS},
                     "toward_away_vs_control": dir_c, "toward_away_vs_neutral": dir_n},
    }


# ----------------------------------------------------------------------------- the floor

def load_rows(p: Path) -> list[dict]:
    return json.loads(p.read_text())["rows"]


def floor_base() -> dict:
    a = load_rows(SCRATCH / "grader-vi/swap-gemini.json")
    b = load_rows(SCRATCH / "breadth/swap-lite-rerun.json")
    assert [r["id"] for r in a] == [r["id"] for r in b]
    c1 = np.array([r["control"] for r in a], float)
    c2 = np.array([r["control"] for r in b], float)
    return {"rows": a, "mu": (c1 + c2) / 2, "p_equal": float(np.mean(c1 == c2)), "sd_diff": float(np.std(c1 - c2)),
            "p_big": float(np.mean(np.abs(c1 - c2) >= 1))}


def grid(x: np.ndarray) -> np.ndarray:
    return np.clip(np.floor(x * 2 + 0.5) / 2, 0, 10)


def noise(n: int, sig: tuple[float, float, float], rng) -> np.ndarray:
    """REVISION 1: a two-component call noise. With probability q a call lands far from the last one
    (N(0, s2)), otherwise near it (N(0, s1)). Revision 0's single normal could not match Gemini's
    shape: it gave 72% identical marks and SD 0.27 against the real 76% and 0.35, because Gemini's
    disagreements are rare but often a whole point."""
    s1, q, s2 = sig
    return np.where(rng.random(n) < q, rng.normal(0, s2, n), rng.normal(0, s1, n))


def calibrate(mu: np.ndarray, target: dict, rng) -> tuple:
    best = None
    for s2 in (0.9, 1.2, 1.5):
        for s1 in np.arange(0.0, 0.21, 0.02):
            for q in np.arange(0.0, 0.21, 0.02):
                eq, sd, big = [], [], []
                for _ in range(10):
                    lat = mu + rng.uniform(-0.25, 0.25, len(mu))
                    d = grid(lat + noise(len(mu), (s1, q, s2), rng)) - grid(lat + noise(len(mu), (s1, q, s2), rng))
                    eq.append(np.mean(d == 0))
                    sd.append(np.std(d))
                    big.append(np.mean(np.abs(d) >= 1))
                m = (float(np.mean(eq)), float(np.mean(sd)), float(np.mean(big)))
                loss = (m[0] - target["p_equal"]) ** 2 + (m[1] - target["sd_diff"]) ** 2 + (m[2] - target["p_big"]) ** 2
                if best is None or loss < best[0]:
                    best = (loss, (float(s1), float(q), float(s2)), m)
    return best


WORLDS = {"NULL": (0.0, 0.0), "PRES+": (0.20, 0.20), "PRES-": (-0.20, -0.20), "CHANGE": (-0.22, 0.0)}
VALUE = {"high": 0.22, "low": -0.22}   # by label shown, vs neutral


def synth(base: dict, sigma: tuple, P: tuple[float, float], rng) -> tuple:
    rows = base["rows"]
    hi = np.array([r["tail"] == "high" for r in rows])
    learner = np.array([str(r["learnerId"]) for r in rows])
    h = np.array([r["human"] for r in rows], float)
    lat = base["mu"] + rng.uniform(-0.25, 0.25, len(rows))
    ids = np.unique(learner)
    lp = dict(zip(ids, rng.normal(0, 0.10, len(ids))))
    lv = dict(zip(ids, rng.normal(0, 0.10, len(ids))))
    pres = np.where(hi, P[0], P[1]) + np.array([lp[x] for x in learner]) + rng.normal(0, 0.20, len(rows))
    vhet = np.array([lv[x] for x in learner]) + rng.normal(0, 0.40, len(rows))
    v_true = np.where(hi, VALUE["high"], VALUE["low"]) + vhet        # true label: own tail's
    v_swap = np.where(hi, VALUE["low"], VALUE["high"]) + vhet        # swapped: the other tail's
    e = lambda: noise(len(rows), sigma, rng)  # noqa: E731
    c = grid(lat + e())
    n = grid(lat + pres + e())
    t = grid(lat + pres + v_true + e())
    s = grid(lat + pres + v_swap + e())
    return h, c, n, t, s, hi, learner


def run_floor() -> dict:
    rng = np.random.default_rng(20261006)
    base = floor_base()
    target = {k: base[k] for k in ("p_equal", "sd_diff", "p_big")}
    loss, sigma, (eq, sd, big) = calibrate(base["mu"], target, rng)
    print(f"  noise: Gemini control-vs-control equal {target['p_equal']:.3f}, sd {target['sd_diff']:.3f}, |d|>=1 {target['p_big']:.3f}; "
          f"calibrated (s1, q, s2) {sigma} gives {eq:.3f}, {sd:.3f}, {big:.3f}")
    report, ok = {}, True
    for world, P in WORLDS.items():
        tally = {"presence": [], "signs": [], "readings": [], "vn_hi": [], "vn_lo": [], "P_est": []}
        for _ in range(FLOOR_REPS):
            h, c, n, t, s, hi, learner = synth(base, sigma, P, rng)
            r = Boot(learner, hi, REPS, rng).run(case_matrix(h, c, n, t, s, hi))
            v = verdicts(r)
            tally["presence"].append(v["presence"]["verdict"])
            tally["signs"].append(tuple(v["presence"]["tail_sign_975"].values()))
            tally["readings"].append(v["readings"]["verdict"])
            tally["vn_hi"].append(sign_class(r["VN_high"]["ci95"]))
            tally["vn_lo"].append(sign_class(r["VN_low"]["ci95"]))
            tally["P_est"].append((r["P_high"]["est"], r["P_low"]["est"]))
        f = lambda xs, x: sum(y == x for y in xs) / len(xs)  # noqa: E731
        pe = f(tally["presence"], "PRESENCE-EFFECT")
        any_neg = sum("-" in sg for sg in tally["signs"]) / FLOOR_REPS
        any_pos = sum("+" in sg for sg in tally["signs"]) / FLOOR_REPS
        hold = f(tally["readings"], "READINGS-HOLD")
        change = f(tally["readings"], "READINGS-CHANGE")
        rec = {"planted_P": {"high": P[0], "low": P[1]}, "planted_value_vs_neutral": VALUE,
               "presence_verdicts": {x: tally["presence"].count(x) for x in sorted(set(tally["presence"]))},
               "presence_effect_rate": pe, "any_tail_minus": any_neg, "any_tail_plus": any_pos,
               "readings_verdicts": {x: tally["readings"].count(x) for x in sorted(set(tally["readings"]))},
               "readings_hold_rate": hold, "readings_change_rate": change,
               "vn_high_plus_rate": f(tally["vn_hi"], "+"), "vn_low_minus_rate": f(tally["vn_lo"], "-"),
               "mean_P_est": [float(np.mean([p[0] for p in tally["P_est"]])), float(np.mean([p[1] for p in tally["P_est"]]))]}
        if world == "NULL":
            rec["bounded_rate"] = f(tally["presence"], "NO-PRESENCE-EFFECT-BOUNDED")
            checks = {"false_presence<=0.10": pe <= 0.10, "false_readings_change<=0.10": change <= 0.10,
                      "vn_high+>=0.80": rec["vn_high_plus_rate"] >= 0.80, "vn_low->=0.80": rec["vn_low_minus_rate"] >= 0.80}
        elif world == "PRES+":
            hit = sum(v == "PRESENCE-EFFECT" and "-" not in sg for v, sg in zip(tally["presence"], tally["signs"])) / FLOOR_REPS
            rec["signed_hit_rate"] = hit
            checks = {"signed_hit>=0.80": hit >= 0.80, "wrong_sign<=0.05": any_neg <= 0.05}
        elif world == "PRES-":
            hit = sum(v == "PRESENCE-EFFECT" and "+" not in sg for v, sg in zip(tally["presence"], tally["signs"])) / FLOOR_REPS
            rec["signed_hit_rate"] = hit
            checks = {"signed_hit>=0.80": hit >= 0.80, "wrong_sign<=0.05": any_pos <= 0.05}
        else:
            checks = {"readings_change>=0.80": change >= 0.80}
        rec["checks"] = checks
        rec["pass"] = all(checks.values())
        ok &= rec["pass"]
        report[world] = rec
        print(f"  {world:7s} presence {rec['presence_verdicts']}  readings {rec['readings_verdicts']}  VN+hi {rec['vn_high_plus_rate']:.2f} "
              f"VN-lo {rec['vn_low_minus_rate']:.2f}  {checks}  {'PASS' if rec['pass'] else 'FAIL'}")
    bounded_reachable = report["NULL"]["bounded_rate"] >= 0.80
    return {"pass": ok, "replicates": FLOOR_REPS, "bootstrap": REPS, "sigma": sigma,
            "noise_target": target, "noise_calibrated": {"p_equal": eq, "sd_diff": sd, "p_big": big},
            "bounded_verdict_reachable": bounded_reachable, "worlds": report,
            "note": "smoke check: synthetic graders written and scored by the same session"}


# ----------------------------------------------------------------------------- the real run

def analyse(path: Path) -> dict:
    raw = path.read_bytes()
    blob = json.loads(raw)
    length = check_neutral(blob)
    arms = ("control", "neutral", "trueLabel", "swappedLabel")
    rows = [r for r in blob["rows"] if all(r[a] is not None for a in arms)]
    h = np.array([r["human"] for r in rows], float)
    c, n, t, s = (np.array([r[a] for r in rows], float) for a in arms)
    hi = np.array([r["tail"] == "high" for r in rows])
    learner = np.array([str(r["learnerId"]) for r in rows])
    r = Boot(learner, hi, REPS, np.random.default_rng(7)).run(case_matrix(h, c, n, t, s, hi))
    run = blob["run"]
    tok = run["tokens"]
    usd = (tok["input"] * PRICE[0] + tok["output"] * PRICE[1]) / 1e6
    return {
        "model": blob["model"], "run": blob.get("runStamp"), "reasoning": blob.get("reasoning"),
        "temperature": blob.get("temperature"), "arms": blob.get("arms"),
        "dump_sha256": hashlib.sha256(raw).hexdigest(),
        "n_rows": len(blob["rows"]), "n_complete": len(rows),
        "complete_by_tail": {"high": int(hi.sum()), "low": int((~hi).sum())},
        "learners_by_tail": {"high": len(set(learner[hi])), "low": len(set(learner[~hi]))},
        "neutral_length_check": length,
        "verdicts": verdicts(r),
        "reproduction_vs_q2": {"L": [r["HL"]["est"], Q2_GEMINI["L"]],
                               "drift_high": [r["VC_high"]["est"], Q2_GEMINI["drift_high"]],
                               "drift_low": [r["VC_low"]["est"], Q2_GEMINI["drift_low"]]},
        "learner_cluster": r,
        "spend": {"calls": run["calls"], "failures": run["failures"], "tokens": tok, "served": run.get("served"),
                  "wire": run.get("wire"), "usd": round(usd, 4), "how": "billed tokens x list price",
                  "price_per_million": PRICE, "cap_usd": CAP_USD},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--floor", action="store_true")
    ap.add_argument("--dump", type=Path)
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    if a.floor:
        res = run_floor()
        (OUT / "floor.json").write_text(json.dumps(res, indent=2) + "\n")
        print("FLOOR", "PASS" if res["pass"] else "FAIL", "| bounded verdict reachable:", res["bounded_verdict_reachable"])
        sys.exit(0 if res["pass"] else 1)
    floor = json.loads((OUT / "floor.json").read_text())
    if not floor["pass"]:
        sys.exit("floor did not pass; no real number is read")
    res = analyse(a.dump)
    res["floor"] = {"pass": floor["pass"], "bounded_verdict_reachable": floor["bounded_verdict_reachable"]}
    if not floor["bounded_verdict_reachable"] and res["verdicts"]["presence"]["verdict"] == "NO-PRESENCE-EFFECT-BOUNDED":
        res["verdicts"]["presence"]["note"] = "the floor found this verdict unreachable under NULL; read it with that limit"
    (OUT / "results.json").write_text(json.dumps(res, indent=2) + "\n")
    R = res["learner_cluster"]
    f = lambda k: f"{R[k]['est']:+.3f} [{R[k]['ci95'][0]:+.3f}, {R[k]['ci95'][1]:+.3f}]"  # noqa: E731
    print(f"{res['model']}  n={res['n_complete']}/{res['n_rows']}  sha256 {res['dump_sha256']}")
    for k in ("HL", "HL_high", "HL_low", "P_high", "P_low", "P", "VN_high", "VN_low", "VC_high", "VC_low",
              "Bc_high", "Bc_low", "Bn_high", "Bn_low", "Bt_high", "Bt_low"):
        print(f"  {k:8s} {f(k)}")
    print(json.dumps(res["verdicts"], indent=1))
    print("spend", res["spend"]["usd"], "tokens", res["spend"]["tokens"], "served", res["spend"]["served"])


if __name__ == "__main__":
    main()
