"""PRE-REGISTERED: build a skill graph blind on XES3G5M, then check every stage against the data.

The north-star process (docs/specs/NORTH-STAR-PROCESS.md) says how a skill graph with levels should
be built where no curriculum exists to check it: nodes from several model families grounded in
source material, a tacit-skill probe, a calibrated merge, levels per node, edges from a panel with a
critic, then checks the platform generates itself. Every stage has been studied alone. This runs the
whole process once, on a domain where each stage can be checked: XES3G5M has an expert KC taxonomy,
question text, and 5.49M timed responses from 18,066 third graders.

The builders see only the SCOPE record below and random samples of question text (with answers and
worked solutions). They never see the KC taxonomy, the KC tags, or any learner response. The build is
frozen and committed (build/) before any learner response is read. The analyst is NOT blind: earlier
studies in this repo read XES3G5M's taxonomy and learner data (taxonomy-order, iita_pairscan,
pairscan_curriculum, the positivity atlas), and the SCOPE record was written by someone who had seen
the taxonomy. Nothing in SCOPE names a KC or a module.

Reads, through shared.paths.data_path("XES_DIR"): XES3G5M/metadata/questions.json (question text;
kc_routes stripped before any prompt is built, asserted), attempts.tsv (uid, question, KC ids,
response, start time in ms; written by the ingest in data/ingest/xes3g5m), cid2route.json (KC id ->
route). Raw data and every prompt holding question text stay outside the repo (the LLM cache lives
under shared.paths.scratch_root()). The repo gets generated node texts, question id -> node id tags,
aggregate statistics, and the model replies that hold no question text.

DIRECTION: "a -> b" means a is a direct prerequisite of b (must be mastered before b can be learned),
per the edge prompt below; the reversed-arrow control is M4r (features from successors instead of
prerequisites), scored through shared.direction.reversed_arrow and reported, never verdict-bearing.

PRE-REGISTRATION (written 2026-09-26, before any build call and before any statistic of this design
was computed on XES3G5M; every change forced by the synthetic run is listed under CHANGES, also
before any real call)

SCOPE        The SCOPE constant. It is the only description of the course the builders get. Every
             build prompt reads it (proposal, attributes, edges, tagging).

STAGE 1      NODES.
  proposers  One proposal from each of six families (PROPOSERS; RESERVE fills a refused family), on
             PROPOSE_PROMPT: SCOPE, a sample of SAMPLE_N = 120 questions drawn without replacement
             (seeded; disjoint across families, so the pool sees 720 of 7,652 questions), the probe
             (PROBE: the frozen subtraction probes of studies/producers/pipeline/probe_transfer.py,
             verbatim, plus one tacit-skill line), and an explicit terminal flag per capability.
             Fewer than 5 families answering: BUILD FAILED, nothing downstream runs.
  merge      Every pair of proposal lists is judged by the calibrated judged matcher of
             studies/producers/decomposition-study/cross_family.py (judge minimax/minimax-m3; prompt
             and rubric imported, not copied; calibrated there on 2,811 labelled pairs: kappa 0.856,
             synonym-miss 0.20, false merge 0.00). Lists longer than CHUNK = 40 are judged in chunks;
             every item pair lies in exactly one chunk pair. Items linked SAME are joined
             (union-find). Each cluster is one node; its text is the member from the first family in
             PROPOSERS order that has a member. A node is terminal if any member was flagged.
  reported   node count; cluster sizes; accumulation (distinct nodes against families added, mean
             over all orders); terminal present.

STAGE 2      NODE ATTRIBUTES, from ATTR_MODELS (two families) on ATTR_PROMPT, batches of 20 nodes:
             three performance levels as observable criteria (from the first model), knowledge type
             (first model), load 1-5 (element interactivity for a typical learner meeting it) and
             minutes to reach level 2 (both averaged over the two models).

STAGE 3      EDGES. Two proposer families (EDGE_MODELS) each name every node's direct prerequisites
             among the nodes (batches of 25 targets, all nodes listed). The union goes to a critic
             from a third family (CRITIC), batches of 40, which keeps or rejects each. Kept edges are
             added in order (proposer count desc, then id) skipping any that closes a cycle, then
             transitively reduced.

TAGGING      Every question with text is tagged by TAGGER with 1-3 built nodes (first = primary) and
             the level (1-3) it demands of its primary node, batches of 20, the full node list with
             levels in the prompt. A batch that fails to parse is retried in batches of 5; a question
             still unparsed is untagged (counted).

FREEZE       build/ (nodes, attributes, edges, tags, proposal replies) is committed before the
             analysis step reads attempts.tsv. analyse refuses to run if build/ has uncommitted
             changes.

SPLIT        Learners by sha256(uid): first 8 hex digits mod 5 == 0 is TEST (about 20%), else TRAIN.
             Every data-derived quantity (question difficulty, model coefficients, error rates used
             as baselines) comes from TRAIN; every verdict is scored on TEST.

B11 (primary) IS THE BUILT GRAPH USEFUL ON HELD-OUT LEARNERS?
  features   For each attempt, from the same learner's earlier attempts only:
             off = logit of the question's TRAIN success rate, shrunk: (c + 5 g) / (n + 5), g the
             global TRAIN rate; U = log1p(prior successes), log1p(prior failures), all questions;
             K[Q] = mean over the question's nodes under Q-matrix Q of log1p(prior successes on the
             node), log1p(prior failures on it), and an indicator for a question with no node;
             P[E] = the same over the direct prerequisites under edge set E of the question's nodes
             (excluding its own nodes), with its indicator.
  models     logistic regression (IRLS, numpy), fitted on TRAIN, scored on TEST:
               M0 difficulty      off
               M1 no graph        off + U
               M2 expert          off + U + K[expert leaf KCs]
               M3 built nodes     off + U + K[built]
               M4 built graph     off + U + K[built] + P[built edges]
               M4s shuffled edges off + U + K[built] + P[built edges under a random relabelling of
                                  the nodes] (same graph shape, semantics destroyed; seeded)
               M4r reversed       off + U + K[built] + P[built edges reversed]
             Secondary: M2c expert at depth 3 (off + U + K[route prefix of length <= 3]).
  statistic  AUC on TEST attempts. Differences by paired learner bootstrap, B = 200.
             "X beats Y": the 95% interval of AUC(X) - AUC(Y) has its lower bound above +0.001.
  verdict    USEFUL, NOT WORSE THAN THE EXPERT TAXONOMY: M4 beats M0 and M1, and the lower bound of
               AUC(M4) - AUC(M2) is above -0.005.
             USEFUL BUT WORSE THAN THE EXPERT TAXONOMY: M4 beats M0 and M1; that bound fails.
             NOT USEFUL: M4 does not beat M1.
  edges      EDGES CARRY SPECIFIC SIGNAL: M4 beats M4s and M4 beats M3.
             EDGES ADD SIGNAL, NOT SPECIFIC: M4 beats M3, not M4s.
             EDGES ADD NOTHING: M4 does not beat M3.
             Unanswerable if the synthetic floor fails (below).
  direction  M4 vs M4r through reversed_arrow; reported, not verdict-bearing (prerequisites are
             practised earlier, so parent history is more often present than child history).

B3  NODE COVERAGE against XES3G5M's taxonomy, at depth 3 (route prefixes of length <= 3; 172 nodes).
  judged     built node texts vs reference prefixes (joined " > "), same judge and chunking.
             Covered-lenient: some built node SAME or OVERLAPPING; covered-strict: SAME.
  questions  a reference node R with >= 10 questions is covered if the built nodes "inside" R
             (>= 0.5 of the questions tagged with the node carry a KC under R) jointly tag >= 0.5 of
             R's questions. Also at leaf level (866 KCs), same rule.
  met        lenient recall >= 0.80 and question-overlap recall >= 0.80 and a terminal node present.

B4  LEVELS ORDERED. Questions with >= 30 TRAIN attempts. Nodes with >= 10 such primary-tagged
    questions spanning >= 2 levels: Spearman(level, TRAIN error rate) per node. Pooled = mean
    weighted by questions; interval by bootstrap over nodes (2000).
    LEVELS ORDERED: pooled lower bound > 0 and share of nodes with rho > 0 >= 0.80.
    LEVELS PARTLY ORDERED: pooled lower bound > 0, share < 0.80. LEVELS NOT ORDERED otherwise.

B7  TIME. Duration of an attempt = next start - this start, same learner, kept if 0 < d <= 600 s.
    Per node, on TEST: each learner's total duration on questions primary-tagged to it (learners
    with >= 3 attempts on it), median over learners; nodes with >= 50 such learners.
    rho_panel = Spearman(panel minutes, observed); rho_diff = Spearman(TRAIN error rate of the
    node's questions, observed); interval of rho_panel - rho_diff by bootstrap over nodes (2000).
    TIME PREDICTED: rho_panel >= 0.50 and the difference's lower bound > 0.
    TIME PARTLY PREDICTED: rho_panel lower bound > 0, not the above. TIME NOT PREDICTED otherwise.
    Observed time is exposure, which the platform's assignment shapes; this is stated with it.
    Secondary: median per-attempt duration.

B8  LOAD x PRIOR KNOWLEDGE. TEST attempts with >= 5 prior attempts; low = the learner's prior
    accuracy below the median of that quantity over TRAIN attempts with >= 5 prior. Logistic
    regression: correct ~ off + load_z + low + load_z x low (load of the primary node, z-scored over
    nodes). Interval of the interaction by learner bootstrap (200).
    LOAD HURTS LOW-PRIOR LEARNERS MORE: upper bound < 0. REVERSED: lower bound > 0.
    NO INTERACTION DETECTED otherwise.

DESCRIPTIVE  Edge order: per built edge a -> b with both tagged, among TEST learners who attempted
             both, the share whose first attempt on a precedes their first on b; the same for M4s's
             edges. Platform order is a curriculum's order, not proof of a prerequisite.
             Untagged questions, tag counts per question, nodes with no tagged question.

NOT TESTED   B1 (no scope manipulation), B2 (no human typing), B6 (no grain rule fixed in advance),
             B9 (no support variation in XES3G5M), B10 (no revise loop).

SYNTHETIC FLOOR (--synthetic, no corpus, no model call). The feature, fit and bootstrap code above
    runs on simulated learners: 30 nodes, a random DAG (parent probability 0.12 among earlier nodes),
    5 questions per node (difficulty N(0, 0.7)), 3,000 learners (theta N(0, 1)) visiting nodes in a
    noisy topological order (index + N(0, 6)), 4-6 attempts per node; mastery m += 0.25 (1 - m) per
    attempt; logit P(correct) = theta - b + 1.5 m + gamma (mean parent mastery - 0.5), no parents
    counting as 0.5. Worlds: gamma = 2 (planted, 5 worlds), gamma = 0 (null, 10 worlds).
    FLOOR PASSES if M4 beats M4s in >= 4 of 5 planted worlds, in <= 1 of 10 null worlds, and M3
    beats M1 in every planted world. If it fails, the edge verdicts are UNANSWERABLE; B11's primary
    verdict does not depend on it.

BUDGET       $30 cap over the study's own ledger (out/spend.json); a call that could cross it is not
             made.

RESULTS (synthetic, before any real call): FLOOR PASSES. M4 beats M4s in 5 of 5 planted worlds
             (M4 - M4s +0.0072 to +0.0101) and in 0 of 10 null worlds (all intervals within
             [-0.0002, +0.0003]); M3 beats M1 in every planted world (+0.012 to +0.014).
             out/synthetic.json. The analysis path was then exercised end to end on fake data
             (--smoke; fake corpus and build, no judge call); no design change followed.

CHANGES      1. Operational, 2026-09-26, before any model answer: the first `build` never loaded the
             repo key (shared.llm.load_key), so its first two proposal calls went out on the
             sandbox's unfunded ambient key and were refused (HTTP 402, $0, no answer received, no
             run file written). build and analyse now load the repo key first. No design change.
             2. Operational, during the merge: judge chunks run four at a time (same prompts and
             seeds; cached answers reused), and a family that failed is recorded (runs/*.FAILED.json)
             and not retried on a restart, so the reserve that replaced it stands. z-ai failed on
             the first real pass (two replies without 20 parseable capabilities; no error returned)
             and Mistral replaced it; the z-ai record was written by hand from that log.
             3. Operational, during the edge stage: critic batches run four at a time (same prompts
             and seeds; cached answers reused). No design change.
             4. Operational, disclosed: judge requests that fail at the HTTP level return no text
             and are not cached. On the first pass six merge chunks failed that way on their first
             seed (two on both seeds, recorded unparsed; four answered on the second seed). The
             restart for change 3 re-requested them and all six answered on the first seed, so the
             node set of record is 401, not the 405 printed by the aborted pass. All replies of both
             passes stay in the cache, so a rerun reproduces 401. Attributes and edges were
             recomputed for the 401-node set; attribute and edge batches now also run four at a
             time. No design change.
             5. Implementation fix, before tagging finished and before any learner data was read:
             reply caps were too low for reasoning models. Every z-ai edge reply stopped at the
             16,000-token cap (34 of 34; no z-ai edge was parsed, so all 831 candidates came from one
             proposer), 33 of 38 critic replies stopped at 8,000 (631 of 831 candidates unjudged and
             so dropped), and tag replies stopped at 6,000 (5,881 reasoning tokens). Caps raised to
             64,000 (edges), 32,000 (critic) and 32,000 (tagging); the stages rerun. Truncated
             replies are cached under the old caps and are not reused, since the cap is part of the
             cache key.
             6. Design substitution, before any learner data was read: at the 64,000-token cap
             z-ai/glm-5.3 still ran to the cap on 19 of 21 edge replies (about $0.28 each), so it
             cannot return an edge list. It is replaced as the second edge proposer by
             mistralai/mistral-medium-3-5, following stage 1's rule that a reserve family fills a
             family that cannot answer (Mistral is stage 1's reserve and answered there). The
             critic stays moonshotai/kimi-k2.6.
             7. Operational: tagging runs sixteen batches at a time (the tagger reasons for
             minutes per batch). Same prompts; cached batches reused. No design change.
             8. Build of record, disclosed: requests that fail at the HTTP level are not cached, so
             a replay re-asks them. Replaying the finished build re-asked 5 critic batches (edges
             807/638 kept/final -> 802/636) and 4 tagging batches (53 questions' tags changed). A
             second replay made no new call and reproduced every build file byte for byte; that
             state is the frozen build. No build file holds question text (no 16-character overlap
             with any question). Build spend $20.12.
             9. Structural, 2026-10-08, after the analysis of record (maintainer): the B3 coverage
             judge moved out of `analyse` into its own step, `judge`, which writes its decisions to
             build/coverage-judge.json; `analyse` reads that file and calls no model. The judge sees
             only the 187 depth-3 route names and the built nodes' texts, never a learner record, and
             this makes the step that calls a model separate from the step that reads learner data.
             Same judge model, prompts, chunking and seeds. The original judge responses were cached
             on a machine that no longer exists, so `judge` was run afresh (with zero data retention
             requested on every call); its B3 figures replace the first run's, and the README
             records both.

    python3 e2e.py --synthetic      # the floor; no corpus, no model call
    python3 e2e.py build            # stages 1-3 and tagging; writes build/
    python3 e2e.py judge            # B3 coverage judge on route names and node texts; writes
                                    # build/coverage-judge.json; no learner data
    python3 e2e.py analyse          # after build/ is committed; reads learner data; no model call
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import random
import re
import subprocess
import sys
import threading
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies/producers/decomposition-study"))
sys.path.insert(0, str(ROOT / "studies/producers/second-author"))
os.environ.setdefault("LLM_MIN_INTERVAL", "1.0")

from shared.direction import reversed_arrow  # noqa: E402
from shared.paths import data_path, scratch_root  # noqa: E402
from shared.stats import spearman  # noqa: E402

OUT = HERE / "out"
BUILD = HERE / "build"
SPEND = OUT / "spend.json"
SEED = 20260927
BUDGET_USD = 30.0
SAMPLE_N = 120
CHUNK = 40
BOOT = 200
NODE_BOOT = 2000
BEATS = 0.001
NONINF = -0.005
_LEDGER_LOCK = threading.Lock()

PROPOSERS = {"google": "google/gemini-3.8-flash", "openai": "openai/gpt-6-sol",
             "anthropic": "anthropic/claude-sonnet-5", "deepseek": "deepseek/deepseek-v4-pro",
             "moonshot": "moonshotai/kimi-k2.6", "zai": "z-ai/glm-5.3"}
RESERVE = {"mistral": "mistralai/mistral-medium-3-5", "xiaomi": "xiaomi/mimo-v2.6-pro",
           "cohere": "cohere/command-a-plus"}
JUDGE = "minimax/minimax-m3"
ATTR_MODELS = ["anthropic/claude-sonnet-5", "deepseek/deepseek-v4-pro"]
EDGE_MODELS = ["openai/gpt-6-sol", "mistralai/mistral-medium-3-5"]
CRITIC = "moonshotai/kimi-k2.6"
TAGGER = "deepseek/deepseek-v4.1-flash"
PRICES = {"google/gemini-3.8-flash": (0.75, 3.75), "openai/gpt-6-sol": (2.0, 10.0),
          "anthropic/claude-sonnet-5": (2.0, 10.0), "deepseek/deepseek-v4-pro": (0.52, 1.041),
          "moonshotai/kimi-k2.6": (0.95, 4.0), "z-ai/glm-5.3": (1.4, 4.4),
          "mistralai/mistral-medium-3-5": (1.5, 7.5), "xiaomi/mimo-v2.6-pro": (0.435, 0.87),
          "cohere/command-a-plus": (0.30, 1.50), "minimax/minimax-m3": (0.30, 1.20),
          "deepseek/deepseek-v4.1-flash": (0.099, 0.60)}

SCOPE = """Learners: third-grade students (about 8-9 years old) using a Chinese online after-school mathematics platform, with a wide spread of prior knowledge.
Target performance: solve the kinds of mathematics problems this platform teaches in its third-grade course.
Setting: self-paced practice on the platform after its own lessons; no teacher adjusts the sequence for an individual learner.
Time budget: one school year.
Knowledge to expect: calculation procedures, concepts, and problem-solving strategies (recognising a problem type and choosing a method)."""

#: studies/producers/pipeline/probe_transfer.py PROBE_FROM_SUBTRACTION, verbatim, then one tacit-skill line
PROBE = """
Before you answer, make sure your list covers these kinds of capability, which decompositions
routinely omit:

- The LAST capability: the one whose presence means the learner has the whole skill, not a component
  of it.
- DIFFICULTY RUNGS: places where the same operation becomes harder in a way that needs separate
  teaching and separate practice, rather than being one capability applied to a bigger case. Name
  each rung separately.
- The capability of RECOGNISING which case you are in, where more than one method applies.
- ENABLING capabilities that experts perform automatically and so leave out: the recognitions,
  checks, representations and small procedures a novice has to be taught explicitly.
"""

PROPOSE_PROMPT = """You are designing the skill map for a mathematics course.

SCOPE
{scope}

SOURCE MATERIAL
Below are {n} questions from the course's question bank, with answers and worked solutions, sampled at random. They show the kind and level of mathematics the course teaches. Do not quote them.

{questions}

TASK
List the capabilities a learner must acquire in this course: every distinct thing a learner must be able to do, at the grain a teacher would teach and assess as one skill in one or two lessons. Cover the whole course the sample is drawn from, not only the sampled questions.
{probe}
Reply with JSON only, no other text:
{{"capabilities": [{{"name": "English name", "name_zh": "Chinese name", "description": "one sentence: what the learner can do", "terminal": false}}]}}
Set "terminal": true on capabilities whose presence means the learner has a whole major strand of the course, not a component of it. Aim for 60 to 150 capabilities."""

ATTR_PROMPT = """You are describing the capabilities of a mathematics course.

SCOPE
{scope}

CAPABILITIES
{nodes}

For each capability give:
- "levels": three performance levels as observable criteria a rater could score from a learner's work: level 1 (beginning), level 2 (secure, the course's expectation), level 3 (extended). One sentence each.
- "type": one of procedural, conceptual, factual, strategic.
- "load": 1 to 5, how many new elements a typical learner in this population must hold and coordinate at once when first meeting it (1 very few, 5 very many).
- "minutes": minutes of instruction and practice a typical learner in this population needs to reach level 2, starting from its prerequisites mastered and this capability not known.

Reply with JSON only: {{"attributes": {{"<id>": {{"levels": ["...", "...", "..."], "type": "...", "load": 3, "minutes": 60}}}}}}"""

EDGE_PROMPT = """You are building the prerequisite map of a mathematics course.

SCOPE
{scope}

ALL CAPABILITIES
{nodes}

For each TARGET capability below, list its DIRECT prerequisites among the capabilities above: those a learner must have mastered before the target can be learned, and that are not already implied by another listed prerequisite. A target may have none.

TARGETS
{targets}

Reply with JSON only: {{"prerequisites": {{"<target id>": ["<id>", "..."]}}}}"""

CRITIC_PROMPT = """You are checking proposed prerequisite links in the capability map of a mathematics course.

SCOPE
{scope}

A link "A -> B" claims A must be mastered before B can be learned, for this population.

LINKS
{links}

For each link decide keep or reject. Reject a link that is backwards, merely topical, or not needed before B can be learned.
Reply with JSON only: {{"decisions": {{"<link number>": "keep"}}}}"""

TAG_PROMPT = """You are tagging mathematics questions with the capabilities they assess.

CAPABILITIES (id | name | levels 1/2/3)
{nodes}

QUESTIONS
{questions}

For each question give 1 to 3 capability ids it assesses, the main one first, and the level (1, 2 or 3) it demands of the main capability.
Reply with JSON only: {{"tags": [{{"q": 1, "nodes": ["n001"], "level": 2}}]}}"""


# ---------------------------------------------------------------- ledger and calls

def _ledger() -> dict:
    return json.loads(SPEND.read_text()) if SPEND.exists() else {"budget_usd": BUDGET_USD, "calls": []}


def spent() -> float:
    return sum(c["cost_usd"] for c in _ledger()["calls"])


def cost_of(model: str, meta: dict) -> float:
    u = meta.get("usage") or {}
    if isinstance(u.get("cost"), (int, float)):
        return float(u["cost"])
    pin, pout = PRICES.get(model, (5.0, 25.0))
    return (u.get("prompt_tokens", 0) * pin + u.get("completion_tokens", 0) * pout) / 1e6


def call(model: str, prompt: str, *, what: str, max_tokens: int, temperature: float,
         seed: int = SEED) -> tuple[str, dict]:
    from shared import llm
    pin, pout = PRICES.get(model, (5.0, 25.0))
    if spent() + (len(prompt) / 3 * pin + max_tokens * pout) / 1e6 > BUDGET_USD:
        raise SystemExit(f"BUDGET: ${spent():.2f} spent; the next call could cross ${BUDGET_USD:.0f}.")
    meta: dict = {}
    txt = llm.call(model, prompt, seed, cache=scratch_root() / "e2e-xes3g5m-cache", max_tokens=max_tokens,
                   temperature=temperature, attempts=3, provider=False, meta=meta)
    if not meta.get("from_cache"):
        with _LEDGER_LOCK:
            led = _ledger()
            led["calls"].append({"what": what, "model": model, "provider": meta.get("provider"),
                                 "served_model": meta.get("served_model"), "cost_usd": cost_of(model, meta),
                                 "usage": meta.get("usage"), "timestamp_utc": meta.get("timestamp_utc")})
            OUT.mkdir(exist_ok=True)
            SPEND.write_text(json.dumps(led, indent=1) + "\n")
    return txt, meta


def parse_json(txt: str):
    s, e = txt.find("{"), txt.rfind("}")
    if s < 0 or e <= s:
        return None
    try:
        return json.loads(txt[s:e + 1])
    except json.JSONDecodeError:
        return None


# ---------------------------------------------------------------- source material

def questions() -> dict[str, dict]:
    """Question id -> {content, answer, analysis}; kc_routes never leaves this function."""
    raw = json.loads((data_path("XES_DIR") / "XES3G5M/metadata/questions.json").read_text())
    out = {}
    for k, v in raw.items():
        out[k] = {f: v.get(f, "") for f in ("content", "answer", "analysis", "type", "options")}
    assert all("kc_routes" not in v for v in out.values())
    return out


def clean(s, n: int) -> str:
    s = re.sub(r"\s+", " ", str(s)).strip()
    return s if len(s) <= n else s[:n] + "..."


def show_question(q: dict, n_content=300, n_analysis=200) -> str:
    opts = "" if q["options"] in ("{}", "", None) else f" Options: {clean(q['options'], 150)}"
    ana = f" Solution: {clean(q['analysis'], n_analysis)}" if n_analysis else ""
    return f"{clean(q['content'], n_content)}{opts} Answer: {clean(q['answer'], 60)}{ana}"


def samples(qs: dict, families: list[str]) -> dict[str, list[str]]:
    ids = sorted(qs, key=int)
    random.Random(SEED).shuffle(ids)
    return {f: ids[i * SAMPLE_N:(i + 1) * SAMPLE_N] for i, f in enumerate(families)}


# ---------------------------------------------------------------- stage 1: nodes

def propose(fam: str, slug: str, sample: list[str], qs: dict) -> dict | None:
    path = BUILD / "runs" / f"{fam}.json"
    if path.exists():
        return json.loads(path.read_text())
    if path.with_suffix(".FAILED.json").exists():
        return None
    block = "\n".join(f"Q{i + 1}. {show_question(qs[q])}" for i, q in enumerate(sample))
    prompt = PROPOSE_PROMPT.format(scope=SCOPE, n=len(sample), questions=block, probe=PROBE)
    for mt in (16000, 32000):
        txt, meta = call(slug, prompt, what=f"propose {fam}", max_tokens=mt, temperature=1.0)
        obj = parse_json(txt)
        caps = obj.get("capabilities") if isinstance(obj, dict) else None
        caps = [c for c in (caps or []) if isinstance(c, dict) and str(c.get("name", "")).strip()]
        if len(caps) >= 20:
            rec = {"family": fam, "requested_slug": slug, "served_model": meta.get("served_model"),
                   "provider": meta.get("provider"), "timestamp_utc": meta.get("timestamp_utc"),
                   "usage": meta.get("usage"), "sample_question_ids": sample,
                   "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                   "capabilities": [{"name": str(c.get("name")).strip(),
                                     "name_zh": str(c.get("name_zh", "")).strip(),
                                     "description": str(c.get("description", "")).strip(),
                                     "terminal": bool(c.get("terminal"))} for c in caps]}
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
            print(f"   {fam:<10} {slug:<34} {len(caps)} capabilities")
            return rec
        if (meta.get("last_error") or "").startswith("HTTP 4"):
            break
    print(f"   {fam:<10} {slug:<34} FAILED {(meta.get('last_error') or '')[:80]}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.with_suffix(".FAILED.json").write_text(json.dumps(
        {"family": fam, "requested_slug": slug, "error": (meta.get("last_error") or "")[:300],
         "finish_reason": meta.get("finish_reason"), "reply_chars": len(txt)}, indent=1) + "\n")
    return None


def cap_text(c: dict) -> str:
    zh = f" ({c['name_zh']})" if c.get("name_zh") else ""
    return f"{c['name']}{zh}: {c['description']}"


def judge_lists(tag: str, a: list[str], b: list[str]) -> np.ndarray:
    """Relation codes (0 different, 1 overlapping, 2 same) for every (a_i, b_j), chunked."""
    import cross_family as cf
    dec = np.zeros((len(a), len(b)), int)

    def one(ij):
        ia, ib = ij
        xa, xb = a[ia:ia + CHUNK], b[ib:ib + CHUNK]
        prompt = cf.judge_prompt(xa, xb)
        for s in (SEED, SEED + 1):
            txt, _ = call(JUDGE, prompt, what=f"judge {tag} {ia}/{ib}", max_tokens=32000,
                          temperature=0.0, seed=s)
            links = cf.parse_links(txt, len(xa), len(xb))
            if links is not None:
                return ia, ib, links
        return ia, ib, None
    chunks = [(ia, ib) for ia in range(0, len(a), CHUNK) for ib in range(0, len(b), CHUNK)]
    with ThreadPoolExecutor(4) as ex:
        for ia, ib, links in ex.map(one, chunks):
            if links is None:
                print(f"   judge {tag} chunk {ia}/{ib}: unparsed, counted as no links")
                continue
            for l in links:
                i, j = ia + l["x"] - 1, ib + l["y"] - 1
                dec[i, j] = max(dec[i, j], 2 if l["relation"] == "SAME" else 1)
    return dec


def merge(runs: dict[str, dict]) -> dict:
    fams = [f for f in list(PROPOSERS) + list(RESERVE) if f in runs]
    items = [(f, i) for f in fams for i in range(len(runs[f]["capabilities"]))]
    idx = {it: k for k, it in enumerate(items)}
    parent = list(range(len(items)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    pairs = {}
    for fa, fb in itertools.combinations(fams, 2):
        ta = [cap_text(c) for c in runs[fa]["capabilities"]]
        tb = [cap_text(c) for c in runs[fb]["capabilities"]]
        dec = judge_lists(f"{fa}-{fb}", ta, tb)
        pairs[f"{fa}-{fb}"] = {"same": int((dec == 2).sum()), "overlapping": int((dec == 1).sum())}
        for i, j in zip(*np.nonzero(dec == 2)):
            ra, rb = find(idx[(fa, int(i))]), find(idx[(fb, int(j))])
            if ra != rb:
                parent[rb] = ra
    clusters = defaultdict(list)
    for k, it in enumerate(items):
        clusters[find(k)].append(it)
    nodes = []
    order = {f: n for n, f in enumerate(fams)}
    for members in sorted(clusters.values(), key=lambda m: min((order[f], i) for f, i in m)):
        f0, i0 = min(members, key=lambda m: (order[m[0]], m[1]))
        c = runs[f0]["capabilities"][i0]
        nodes.append({"id": f"n{len(nodes) + 1:03d}", "name": c["name"], "name_zh": c["name_zh"],
                      "description": c["description"],
                      "terminal": any(runs[f]["capabilities"][i]["terminal"] for f, i in members),
                      "families": sorted({f for f, _ in members}), "members": [[f, i] for f, i in members]})
    # accumulation: distinct nodes against families added, mean over all orders
    fam_nodes = {f: {n["id"] for n in nodes if f in n["families"]} for f in fams}
    acc = np.zeros(len(fams))
    perms = list(itertools.permutations(fams))
    for p in perms:
        seen = set()
        for k, f in enumerate(p):
            seen |= fam_nodes[f]
            acc[k] += len(seen)
    return {"families": fams, "nodes": nodes, "judged_pairs": pairs,
            "accumulation": [round(float(x), 2) for x in acc / len(perms)],
            "cluster_sizes": dict(Counter(len(n["members"]) for n in nodes))}


# ---------------------------------------------------------------- stages 2, 3 and tagging

def node_line(n: dict) -> str:
    return f"{n['id']} | {n['name']} ({n['name_zh']}): {n['description']}"


def attributes(nodes: list[dict]) -> dict:
    per_model = {}

    def attr_batch(job):
        m, s = job
        batch = nodes[s:s + 20]
        prompt = ATTR_PROMPT.format(scope=SCOPE, nodes="\n".join(node_line(n) for n in batch))
        for seed in (SEED, SEED + 1):
            txt, _ = call(m, prompt, what=f"attributes {m} {s}", max_tokens=16000, temperature=0.0,
                          seed=seed)
            obj = parse_json(txt)
            att = obj.get("attributes") if isinstance(obj, dict) else None
            if isinstance(att, dict) and any(n["id"] in att for n in batch):
                return m, {k: v for k, v in att.items() if isinstance(v, dict)}
        return m, {}
    jobs = [(m, s) for m in ATTR_MODELS for s in range(0, len(nodes), 20)]
    for m in ATTR_MODELS:
        per_model[m] = {}
    with ThreadPoolExecutor(4) as ex:
        for m, got in ex.map(attr_batch, jobs):
            per_model[m].update(got)
    out = {}
    for n in nodes:
        rows = [per_model[m].get(n["id"]) for m in ATTR_MODELS]
        first = rows[0] or {}

        def num(r, k):
            try:
                return float(r[k])
            except (KeyError, TypeError, ValueError):
                return None
        loads = [x for x in (num(r, "load") for r in rows if r) if x is not None]
        mins = [x for x in (num(r, "minutes") for r in rows if r) if x is not None]
        lv = first.get("levels") if isinstance(first.get("levels"), list) else []
        out[n["id"]] = {"levels": [str(x) for x in lv[:3]], "type": str(first.get("type", "")),
                        "load": float(np.mean(loads)) if loads else None,
                        "minutes": float(np.mean(mins)) if mins else None,
                        "per_model": {m: r for m, r in zip(ATTR_MODELS, rows)}}
    return out


def edges(nodes: list[dict]) -> dict:
    ids = {n["id"] for n in nodes}
    listing = "\n".join(node_line(n) for n in nodes)
    proposed = defaultdict(set)

    def edge_batch(job):
        m, s = job
        batch = nodes[s:s + 25]
        prompt = EDGE_PROMPT.format(scope=SCOPE, nodes=listing,
                                    targets="\n".join(f"{n['id']} | {n['name']}" for n in batch))
        for seed in (SEED, SEED + 1):
            txt, _ = call(m, prompt, what=f"edges {m} {s}", max_tokens=64000, temperature=0.0, seed=seed)
            obj = parse_json(txt)
            pre = obj.get("prerequisites") if isinstance(obj, dict) else None
            if isinstance(pre, dict):
                return m, pre
        return m, {}
    jobs = [(m, s) for m in EDGE_MODELS for s in range(0, len(nodes), 25)]
    with ThreadPoolExecutor(4) as ex:
        for m, pre in ex.map(edge_batch, jobs):
            for tgt, ps in pre.items():
                if tgt in ids and isinstance(ps, list):
                    for q in ps:
                        if q in ids and q != tgt:
                            proposed[(q, tgt)].add(m)
    cand = sorted(proposed, key=lambda e: (-len(proposed[e]), e))
    name = {n["id"]: n["name"] for n in nodes}
    kept = {}

    def judge_batch(s):
        batch = cand[s:s + 40]
        links = "\n".join(f"{k + 1}. {a} {name[a]} -> {b} {name[b]}" for k, (a, b) in enumerate(batch))
        for seed in (SEED, SEED + 1):
            txt, _ = call(CRITIC, CRITIC_PROMPT.format(scope=SCOPE, links=links), what=f"critic {s}",
                          max_tokens=32000, temperature=0.0, seed=seed)
            obj = parse_json(txt)
            dec = obj.get("decisions") if isinstance(obj, dict) else None
            if isinstance(dec, dict):
                return {e: str(dec.get(str(k + 1), "")).strip().lower() == "keep" for k, e in enumerate(batch)}
        return {}
    with ThreadPoolExecutor(4) as ex:
        for got in ex.map(judge_batch, range(0, len(cand), 40)):
            kept.update(got)
    # acyclic by insertion order, then transitive reduction
    adj = defaultdict(set)

    def reaches(a, b):
        stack, seen = [a], set()
        while stack:
            x = stack.pop()
            if x == b:
                return True
            if x not in seen:
                seen.add(x)
                stack.extend(adj[x])
        return False
    dropped_cycle = []
    for e in cand:
        if not kept.get(e):
            continue
        a, b = e
        if reaches(b, a):
            dropped_cycle.append(e)
            continue
        adj[a].add(b)
    final = set()
    for a in list(adj):
        for b in adj[a]:
            adj[a].discard(b)
            if not reaches(a, b):
                final.add((a, b))
            adj[a].add(b)
    return {"proposed": [[a, b, sorted(proposed[(a, b)])] for a, b in cand],
            "critic_kept": [[a, b] for a, b in cand if kept.get((a, b))],
            "critic_unjudged": [[a, b] for a, b in cand if (a, b) not in kept],
            "dropped_for_cycle": [list(e) for e in dropped_cycle],
            "edges": sorted([a, b] for a, b in final)}


def tag_batch(qids: list[str], qs: dict, listing: str, ids: set) -> dict:
    block = "\n".join(f"Q{i + 1}. {show_question(qs[q], 400, 0)}" for i, q in enumerate(qids))
    txt, _ = call(TAGGER, TAG_PROMPT.format(nodes=listing, questions=block),
                  what=f"tag {qids[0]}", max_tokens=32000, temperature=0.0)
    obj = parse_json(txt)
    out = {}
    for t in (obj.get("tags") if isinstance(obj, dict) else None) or []:
        try:
            k = int(t["q"]) - 1
            ns = [n for n in t["nodes"] if n in ids][:3]
            lv = int(t.get("level", 0))
        except (KeyError, TypeError, ValueError):
            continue
        if 0 <= k < len(qids) and ns:
            out[qids[k]] = {"nodes": ns, "level": lv if lv in (1, 2, 3) else None}
    return out


def tag_all(nodes: list[dict], att: dict, qs: dict) -> dict:
    ids = {n["id"] for n in nodes}
    listing = "\n".join(f"{n['id']} | {n['name']} ({n['name_zh']}) | "
                        + " / ".join(att[n["id"]]["levels"]) for n in nodes)
    qids = sorted(qs, key=int)
    batches = [qids[s:s + 20] for s in range(0, len(qids), 20)]
    tags: dict = {}
    with ThreadPoolExecutor(16) as ex:
        for got in ex.map(lambda b: tag_batch(b, qs, listing, ids), batches):
            tags.update(got)
    missing = [q for q in qids if q not in tags]
    retry = [missing[s:s + 5] for s in range(0, len(missing), 5)]
    with ThreadPoolExecutor(16) as ex:
        for got in ex.map(lambda b: tag_batch(b, qs, listing, ids), retry):
            tags.update(got)
    return {"tags": tags, "untagged": [q for q in qids if q not in tags]}


def build() -> None:
    from shared import llm
    if not llm.load_key():
        raise SystemExit("no OPENROUTER_API_KEY in the repo .env or the environment")
    qs = questions()
    fams = list(PROPOSERS)
    smp = samples(qs, fams + list(RESERVE))
    print("1. proposals")
    runs = {}
    for f in fams:
        r = propose(f, PROPOSERS[f], smp[f], qs)
        if r:
            runs[f] = r
    for f, slug in RESERVE.items():
        if len(runs) >= len(PROPOSERS):
            break
        r = propose(f, slug, smp[f], qs)
        if r:
            runs[f] = r
    if len(runs) < 5:
        raise SystemExit(f"BUILD FAILED: {len(runs)} families answered")
    print("2. merge")
    mg = merge(runs)
    nodes = mg["nodes"]
    print(f"   {len(nodes)} nodes; accumulation {mg['accumulation']}; terminal "
          f"{sum(n['terminal'] for n in nodes)}")
    (BUILD / "nodes.json").write_text(json.dumps(mg, indent=1, ensure_ascii=False) + "\n")
    print("3. attributes")
    att = attributes(nodes)
    (BUILD / "attributes.json").write_text(json.dumps(att, indent=1, ensure_ascii=False) + "\n")
    print(f"   levels for {sum(len(a['levels']) == 3 for a in att.values())} of {len(nodes)}")
    print("4. edges")
    ed = edges(nodes)
    (BUILD / "edges.json").write_text(json.dumps(ed, indent=1, ensure_ascii=False) + "\n")
    print(f"   proposed {len(ed['proposed'])}, kept {len(ed['critic_kept'])}, final {len(ed['edges'])}")
    print("5. tagging")
    tg = tag_all(nodes, att, qs)
    (BUILD / "tags.json").write_text(json.dumps(tg, indent=1) + "\n")
    print(f"   tagged {len(tg['tags'])} of {len(qs)}; spend ${spent():.2f}")


# ---------------------------------------------------------------- knowledge tracing core

def logit(p):
    return np.log(p / (1 - p))


def fit_logistic(X: np.ndarray, y: np.ndarray, w: np.ndarray | None = None, iters: int = 30) -> np.ndarray:
    """IRLS with an intercept column prepended; tiny ridge for stability."""
    X1 = np.column_stack([np.ones(len(X)), X])
    beta = np.zeros(X1.shape[1])
    w = np.ones(len(y)) if w is None else w
    for _ in range(iters):
        eta = np.clip(X1 @ beta, -30, 30)
        p = 1 / (1 + np.exp(-eta))
        W = w * p * (1 - p)
        H = (X1 * W[:, None]).T @ X1 + 1e-6 * np.eye(X1.shape[1])
        g = X1.T @ (w * (y - p))
        step = np.linalg.solve(H, g)
        beta += step
        if np.max(np.abs(step)) < 1e-7:
            break
    return beta


def predict(beta, X):
    return np.column_stack([np.ones(len(X)), X]) @ beta


class AUC:
    """Weighted AUC with ties, fast under learner-bootstrap weights."""

    def __init__(self, score: np.ndarray, y: np.ndarray, grp: np.ndarray):
        order = np.argsort(score, kind="stable")
        s = score[order]
        self.gid = np.empty(len(s), int)
        self.gid[order] = np.concatenate([[0], np.cumsum(s[1:] != s[:-1])])
        self.ng = int(self.gid.max()) + 1
        self.y, self.grp = y.astype(bool), grp

    def __call__(self, lw: np.ndarray) -> float:
        w = lw[self.grp]
        pos = np.bincount(self.gid[self.y], w[self.y], self.ng)
        neg = np.bincount(self.gid[~self.y], w[~self.y], self.ng)
        below = np.cumsum(neg) - neg
        P, N = pos.sum(), neg.sum()
        return float((pos * (below + 0.5 * neg)).sum() / (P * N)) if P and N else float("nan")


def features(seq, qnodes: dict[str, dict], parent_sets: dict[str, dict]):
    """seq: list of (learner, question, correct) in each learner's time order, learners contiguous.

    qnodes: Q-matrix name -> {question: [node, ...]}. parent_sets: edge-set name -> (Q-matrix name,
    {node: set of predecessor nodes}). Returns name -> float32 array of columns."""
    n = len(seq)
    out = {"U": np.zeros((n, 2), np.float32)}
    for q in qnodes:
        out[f"K:{q}"] = np.zeros((n, 3), np.float32)
    for e in parent_sets:
        out[f"P:{e}"] = np.zeros((n, 3), np.float32)
    L = math.log1p
    last = None
    for r, (u, q, c) in enumerate(seq):
        if u != last:
            last, ts, tf = u, 0, 0
            st = {name: defaultdict(lambda: [0, 0]) for name in qnodes}
        out["U"][r] = (L(ts), L(tf))
        for name, qm in qnodes.items():
            ns = qm.get(q, ())
            if ns:
                s_ = st[name]
                out[f"K:{name}"][r] = (sum(L(s_[k][0]) for k in ns) / len(ns),
                                       sum(L(s_[k][1]) for k in ns) / len(ns), 0)
            else:
                out[f"K:{name}"][r, 2] = 1
        for ename, (qname, pre) in parent_sets.items():
            ns = qnodes[qname].get(q, ())
            ps = set().union(*(pre.get(k, set()) for k in ns)) - set(ns) if ns else set()
            if ps:
                s_ = st[qname]
                out[f"P:{ename}"][r] = (sum(L(s_[k][0]) for k in ps) / len(ps),
                                        sum(L(s_[k][1]) for k in ps) / len(ps), 0)
            else:
                out[f"P:{ename}"][r, 2] = 1
        for name, qm in qnodes.items():
            for k in qm.get(q, ()):
                st[name][k][0 if c else 1] += 1
        if c:
            ts += 1
        else:
            tf += 1
    return out


def difficulty(qs_arr, y, train):
    g = y[train].mean()
    n = np.bincount(qs_arr[train], minlength=qs_arr.max() + 1)
    c = np.bincount(qs_arr[train], y[train], minlength=qs_arr.max() + 1)
    p = (c + 5 * g) / (n + 5)
    return logit(p)[qs_arr].astype(np.float32), n, c


def preds(edge_list):
    pre = defaultdict(set)
    for a, b in edge_list:
        pre[b].add(a)
    return pre


def kt_compare(seq, y, learner, train, qidx, qnodes, specs, extra=()):
    """specs: model name -> list of feature-block names (plus 'off'). Returns AUCs and differences."""
    off, _, _ = difficulty(qidx, y, train)
    blocks = {"off": off[:, None]}
    blocks.update(features(seq, qnodes, extra and extra[0] or {}))
    test = ~train
    lw_idx = np.unique(learner[test], return_inverse=True)[1]
    nl = lw_idx.max() + 1
    scores, betas = {}, {}
    for m, bl in specs.items():
        X = np.column_stack([blocks[b] for b in bl]).astype(np.float64)
        beta = fit_logistic(X[train], y[train].astype(float))
        betas[m] = beta.tolist()
        scores[m] = AUC(predict(beta, X[test]), y[test], lw_idx)
    rng = np.random.default_rng(SEED)
    ones = np.ones(nl)
    point = {m: a(ones) for m, a in scores.items()}
    draws = {m: [] for m in scores}
    for _ in range(BOOT):
        lw = np.bincount(rng.integers(0, nl, nl), minlength=nl).astype(float)
        for m, a in scores.items():
            draws[m].append(a(lw))
    draws = {m: np.array(v) for m, v in draws.items()}
    return point, draws, betas


def diff(point, draws, a, b):
    d = draws[a] - draws[b]
    return {"diff": point[a] - point[b], "lo": float(np.percentile(d, 2.5)), "hi": float(np.percentile(d, 97.5))}


def beats(point, draws, a, b):
    return diff(point, draws, a, b)["lo"] > BEATS


EDGE_SPECS = {"M1": ["off", "U"], "M3": ["off", "U", "K:built"],
              "M4": ["off", "U", "K:built", "P:built"], "M4s": ["off", "U", "K:built", "P:shuffled"]}


def relabel(edge_list, nodes, seed):
    perm = list(nodes)
    random.Random(seed).shuffle(perm)
    m = dict(zip(nodes, perm))
    return [(m[a], m[b]) for a, b in edge_list]


# ---------------------------------------------------------------- synthetic floor

def sim_world(gamma: float, seed: int):
    rng = np.random.default_rng(seed)
    K = 30
    par = {j: [i for i in range(j) if rng.random() < 0.12] for j in range(K)}
    qnode = {f"q{j}_{k}": j for j in range(K) for k in range(5)}
    b = {q: rng.normal(0, 0.7) for q in qnode}
    seq, y, learner = [], [], []
    for u in range(3000):
        th = rng.normal()
        m = np.zeros(K)
        order = np.argsort(np.arange(K) + rng.normal(0, 6, K))
        for j in order:
            gbar = np.mean([m[p] for p in par[j]]) if par[j] else 0.5
            for _ in range(rng.integers(4, 7)):
                q = f"q{j}_{rng.integers(5)}"
                eta = th - b[q] + 1.5 * m[j] + gamma * (gbar - 0.5)
                c = int(rng.random() < 1 / (1 + math.exp(-eta)))
                seq.append((u, q, c))
                y.append(c)
                learner.append(u)
                m[j] += 0.25 * (1 - m[j])
    edges_true = [(p, j) for j in par for p in par[j]]
    return seq, np.array(y), np.array(learner), {q: [j] for q, j in qnode.items()}, edges_true, list(range(K))


def synthetic() -> dict:
    res = {"planted": [], "null": []}
    for kind, gamma, worlds in (("planted", 2.0, 5), ("null", 0.0, 10)):
        for w in range(worlds):
            seq, y, learner, qn, et, nodes = sim_world(gamma, SEED + 100 * w + int(gamma))
            train = np.array([int(hashlib.sha256(str(u).encode()).hexdigest()[:8], 16) % 5 != 0
                              for u in learner])
            qlist = sorted(qn)
            qi = {q: i for i, q in enumerate(qlist)}
            qidx = np.array([qi[q] for _, q, _ in seq])
            parent_sets = {"built": ("built", preds(et)),
                           "shuffled": ("built", preds(relabel(et, nodes, SEED + w)))}
            point, draws, _ = kt_compare(seq, y, learner, train, qidx, {"built": qn}, EDGE_SPECS,
                                         (parent_sets,))
            row = {"world": w, "gamma": gamma, "edges": len(et),
                   "auc": {m: round(v, 4) for m, v in point.items()},
                   "M4-M4s": diff(point, draws, "M4", "M4s"), "M4-M3": diff(point, draws, "M4", "M3"),
                   "M3-M1": diff(point, draws, "M3", "M1"),
                   "M4 beats M4s": beats(point, draws, "M4", "M4s"),
                   "M3 beats M1": beats(point, draws, "M3", "M1")}
            res[kind].append(row)
            print(f"  {kind:<8} world {w}: M4-M4s {row['M4-M4s']['diff']:+.4f} "
                  f"[{row['M4-M4s']['lo']:+.4f}, {row['M4-M4s']['hi']:+.4f}]  "
                  f"M3-M1 {row['M3-M1']['diff']:+.4f}")
    hit = sum(r["M4 beats M4s"] for r in res["planted"])
    fp = sum(r["M4 beats M4s"] for r in res["null"])
    q_ok = all(r["M3 beats M1"] for r in res["planted"])
    res["floor"] = {"planted_detected": hit, "null_false_positives": fp, "qmatrix_detected_all": q_ok,
                    "passes": hit >= 4 and fp <= 1 and q_ok}
    print(f"FLOOR {'PASSES' if res['floor']['passes'] else 'FAILS'}: planted {hit}/5, "
          f"null false positives {fp}/10, Q-matrix detected in every planted world: {q_ok}")
    OUT.mkdir(exist_ok=True)
    (OUT / "synthetic.json").write_text(json.dumps(res, indent=1) + "\n")
    return res


# ---------------------------------------------------------------- analysis (after the freeze)

def load_attempts():
    rows = []
    with open(data_path("XES_DIR") / "attempts.tsv") as f:
        for k, line in enumerate(f):
            uid, q, c, res, t = line.rstrip("\n").split("\t")
            rows.append((uid, int(t), k, q, c, res == "1"))
    rows.sort(key=lambda r: (r[0], r[1], r[2]))
    return rows


def routes():
    r = json.loads((data_path("XES_DIR") / "cid2route.json").read_text())
    return {k: (v.split("----") if isinstance(v, str) else list(v)) for k, v in r.items()}


def coverage_inputs(BUILD: Path) -> tuple[list[str], list[str]]:
    """The B3 judge's two lists: depth-3 route names and the built nodes' texts. No learner data."""
    mg = json.loads((BUILD / "nodes.json").read_text())
    d3_names = sorted({" > ".join(v[:3]) for v in routes().values()})
    node_txt = [f"{n['name']} ({n['name_zh']}): {n['description']}" for n in mg["nodes"]]
    return d3_names, node_txt


def _digest(xs: list[str]) -> str:
    return hashlib.sha256("\n".join(xs).encode()).hexdigest()


def judge() -> None:
    """B3 coverage judge (CHANGES 9): writes build/coverage-judge.json. Reads no learner record."""
    from shared import llm
    llm.load_key()
    d3_names, node_txt = coverage_inputs(HERE / "build")
    dec = judge_lists("coverage", d3_names, node_txt)
    rec = {"judge": JUDGE, "chunk": CHUNK, "seeds": [SEED, SEED + 1],
           "d3_names_sha256": _digest(d3_names), "node_txt_sha256": _digest(node_txt),
           "n_d3": len(d3_names), "n_nodes": len(node_txt), "decisions": dec.tolist()}
    (HERE / "build" / "coverage-judge.json").write_text(json.dumps(rec) + "\n")
    print(f"coverage judge: {len(d3_names)} x {len(node_txt)} decisions written")


def analyse(smoke: Path | None = None) -> None:
    """smoke: a directory holding a fake build/ (with XES_DIR pointed at fake data) to exercise this
    code without real data; the judge is skipped and nothing is written to out/."""
    BUILD = smoke / "build" if smoke else HERE / "build"
    dirty = "" if smoke else subprocess.run(["git", "status", "--porcelain", str(BUILD)],
                                            capture_output=True, text=True, cwd=ROOT).stdout.strip()
    if dirty or not (BUILD / "tags.json").exists():
        raise SystemExit("build/ is missing or has uncommitted changes; commit the frozen build first")
    syn = json.loads((OUT / "synthetic.json").read_text())
    floor_ok = syn["floor"]["passes"]
    mg = json.loads((BUILD / "nodes.json").read_text())
    att = json.loads((BUILD / "attributes.json").read_text())
    ed = json.loads((BUILD / "edges.json").read_text())
    tg = json.loads((BUILD / "tags.json").read_text())
    nodes = [n["id"] for n in mg["nodes"]]
    built_q = {q: t["nodes"] for q, t in tg["tags"].items()}
    primary = {q: t["nodes"][0] for q, t in tg["tags"].items()}
    qlevel = {q: t["level"] for q, t in tg["tags"].items()}
    rt = routes()

    print("reading attempts")
    rows = load_attempts()
    uids = [r[0] for r in rows]
    y = np.array([r[5] for r in rows], np.int8)
    ul = {u: i for i, u in enumerate(dict.fromkeys(uids))}
    learner = np.array([ul[u] for u in uids])
    train = np.array([int(hashlib.sha256(u.encode()).hexdigest()[:8], 16) % 5 != 0 for u in uids])
    qlist = sorted({r[3] for r in rows}, key=int)
    qi = {q: i for i, q in enumerate(qlist)}
    qidx = np.array([qi[r[3]] for r in rows])
    expert_q, d3_q = {}, {}
    for r in rows:
        if r[3] not in expert_q:
            ks = [k for k in r[4].split("_") if k in rt]
            expert_q[r[3]] = ks
            d3_q[r[3]] = sorted({" > ".join(rt[k][:3]) for k in ks})
    seq = [(r[0], r[3], r[5]) for r in rows]
    E = [tuple(e) for e in ed["edges"]]
    parent_sets = {"built": ("built", preds(E)),
                   "shuffled": ("built", preds(relabel(E, nodes, SEED))),
                   "reversed": ("built", preds([(b, a) for a, b in E]))}
    specs = {"M0": ["off"], "M1": ["off", "U"], "M2": ["off", "U", "K:expert"],
             "M2c": ["off", "U", "K:depth3"], "M3": ["off", "U", "K:built"],
             "M4": ["off", "U", "K:built", "P:built"], "M4s": ["off", "U", "K:built", "P:shuffled"],
             "M4r": ["off", "U", "K:built", "P:reversed"]}
    print("fitting")
    point, draws, betas = kt_compare(seq, y, learner, train, qidx,
                                     {"expert": expert_q, "depth3": d3_q, "built": built_q}, specs,
                                     (parent_sets,))
    D = {f"{a}-{b}": diff(point, draws, a, b) for a, b in
         [("M4", "M0"), ("M4", "M1"), ("M4", "M2"), ("M4", "M3"), ("M4", "M4s"), ("M4", "M4r"),
          ("M3", "M2"), ("M2", "M1"), ("M3", "M1"), ("M2c", "M1")]}
    if beats(point, draws, "M4", "M0") and beats(point, draws, "M4", "M1"):
        b11 = ("USEFUL, NOT WORSE THAN THE EXPERT TAXONOMY" if D["M4-M2"]["lo"] > NONINF
               else "USEFUL BUT WORSE THAN THE EXPERT TAXONOMY")
    else:
        b11 = "NOT USEFUL"
    if not floor_ok:
        ev = "UNANSWERABLE (synthetic floor fails)"
    elif beats(point, draws, "M4", "M3"):
        ev = ("EDGES CARRY SPECIFIC SIGNAL" if beats(point, draws, "M4", "M4s")
              else "EDGES ADD SIGNAL, NOT SPECIFIC")
    else:
        ev = "EDGES ADD NOTHING"
    direction = reversed_arrow(lambda es: point["M4"] if es == set(E) else point["M4r"], E)

    # ---- B3 coverage (the judge's decisions come from build/coverage-judge.json; CHANGES 9)
    d3_names, node_txt = coverage_inputs(BUILD)
    if smoke:
        dec = np.zeros((len(d3_names), len(node_txt)), int)
    else:
        cj = json.loads((BUILD / "coverage-judge.json").read_text())
        assert cj["d3_names_sha256"] == _digest(d3_names) and cj["node_txt_sha256"] == _digest(node_txt), \
            "build/coverage-judge.json was judged on different lists; rerun `e2e.py judge`"
        dec = np.array(cj["decisions"], int)
    cov_len = float((dec.max(1) >= 1).mean())
    cov_str = float((dec.max(1) == 2).mean())

    def overlap_cov(ref_of_q: dict[str, list[str]]):
        refq = defaultdict(set)
        for q, rs in ref_of_q.items():
            for r_ in rs:
                refq[r_].add(q)
        nodeq = defaultdict(set)
        for q, ns in built_q.items():
            for n in ns:
                nodeq[n].add(q)
        eligible = [r_ for r_, qq in refq.items() if len(qq) >= 10]
        covered = 0
        for r_ in eligible:
            inside = [n for n, qq in nodeq.items() if len(qq & refq[r_]) >= 0.5 * len(qq)]
            union = set().union(*(nodeq[n] for n in inside)) if inside else set()
            covered += len(union & refq[r_]) >= 0.5 * len(refq[r_])
        return {"eligible": len(eligible), "covered": covered,
                "recall": covered / len(eligible) if eligible else float("nan")}
    ov3 = overlap_cov(d3_q)
    ovl = overlap_cov(expert_q)
    terminal = any(n["terminal"] for n in mg["nodes"])
    b3_met = cov_len >= 0.80 and ov3["recall"] >= 0.80 and terminal

    # ---- per-question train difficulty
    nq = np.bincount(qidx[train], minlength=len(qlist))
    cq = np.bincount(qidx[train], y[train], minlength=len(qlist))
    err = {q: 1 - cq[i] / nq[i] for q, i in qi.items() if nq[i] >= 30}

    # ---- B4 levels
    per_node = defaultdict(list)
    for q, e in err.items():
        if q in primary and qlevel.get(q):
            per_node[primary[q]].append((qlevel[q], e))
    lv_rows = []
    for n, v in per_node.items():
        if len(v) >= 10 and len({a for a, _ in v}) >= 2:
            lv_rows.append((n, len(v), spearman([a for a, _ in v], [e for _, e in v])))
    rng = np.random.default_rng(SEED)
    if lv_rows:
        wts = np.array([r[1] for r in lv_rows], float)
        rhos = np.array([r[2] for r in lv_rows])
        ok = ~np.isnan(rhos)
        pooled = float(np.average(rhos[ok], weights=wts[ok]))
        bs = []
        for _ in range(NODE_BOOT):
            i = rng.integers(0, ok.sum(), ok.sum())
            bs.append(np.average(rhos[ok][i], weights=wts[ok][i]))
        lo4 = float(np.percentile(bs, 2.5))
        share = float((rhos[ok] > 0).mean())
        b4 = ("LEVELS ORDERED" if lo4 > 0 and share >= 0.80 else
              "LEVELS PARTLY ORDERED" if lo4 > 0 else "LEVELS NOT ORDERED")
        b4d = {"nodes": int(ok.sum()), "pooled_rho": pooled, "lo": lo4,
               "hi": float(np.percentile(bs, 97.5)), "share_positive": share, "verdict": b4}
    else:
        b4d = {"nodes": 0, "verdict": "LEVELS NOT ORDERED (no eligible node)"}

    # ---- B7 time
    dur = np.full(len(rows), np.nan)
    for r in range(len(rows) - 1):
        if rows[r][0] == rows[r + 1][0]:
            d = (rows[r + 1][1] - rows[r][1]) / 1000
            if 0 < d <= 600:
                dur[r] = d
    tot = defaultdict(lambda: defaultdict(lambda: [0.0, 0]))
    per_att = defaultdict(list)
    for r in np.nonzero(~train)[0]:
        n = primary.get(rows[r][3])
        if n is None:
            continue
        cell = tot[n][rows[r][0]]
        cell[1] += 1
        if not np.isnan(dur[r]):
            cell[0] += dur[r]
            per_att[n].append(dur[r])
    node_err = defaultdict(list)
    for q, e in err.items():
        if q in primary:
            node_err[primary[q]].append(e)
    t_rows = []
    for n, by_l in tot.items():
        vals = [s for s, k in by_l.values() if k >= 3]
        if len(vals) >= 50 and att.get(n, {}).get("minutes") and node_err.get(n):
            t_rows.append((n, att[n]["minutes"], float(np.median(vals)), float(np.mean(node_err[n])),
                           float(np.median(per_att[n])) if per_att[n] else float("nan")))
    if len(t_rows) >= 5:
        pm = np.array([r[1] for r in t_rows]); ob = np.array([r[2] for r in t_rows])
        de = np.array([r[3] for r in t_rows]); pa = np.array([r[4] for r in t_rows])
        rp, rd = spearman(pm, ob), spearman(de, ob)
        bsd, bsp = [], []
        for _ in range(NODE_BOOT):
            i = rng.integers(0, len(t_rows), len(t_rows))
            a_, b_ = spearman(pm[i], ob[i]), spearman(de[i], ob[i])
            bsp.append(a_)
            bsd.append(a_ - b_)
        lo_d, lo_p = float(np.nanpercentile(bsd, 2.5)), float(np.nanpercentile(bsp, 2.5))
        b7 = ("TIME PREDICTED" if rp >= 0.50 and lo_d > 0 else
              "TIME PARTLY PREDICTED" if lo_p > 0 else "TIME NOT PREDICTED")
        b7d = {"nodes": len(t_rows), "rho_panel": rp, "rho_panel_lo": lo_p, "rho_difficulty": rd,
               "diff_lo": lo_d, "diff_hi": float(np.nanpercentile(bsd, 97.5)),
               "rho_panel_per_attempt": spearman(pm, pa), "verdict": b7}
    else:
        b7d = {"nodes": len(t_rows), "verdict": "TIME NOT PREDICTED (too few nodes)"}

    # ---- B8 load x prior
    loads = {n: att[n]["load"] for n in nodes if att.get(n, {}).get("load") is not None}
    lz_mu, lz_sd = np.mean(list(loads.values())), np.std(list(loads.values()))
    feats = features(seq, {}, {})["U"]
    prior_n = np.expm1(feats[:, 0]) + np.expm1(feats[:, 1])
    prior_acc = np.where(prior_n > 0, np.expm1(feats[:, 0]) / np.maximum(prior_n, 1), np.nan)
    off, _, _ = difficulty(qidx, y, train)
    med = np.nanmedian(prior_acc[train & (prior_n >= 5)])
    sel = np.array([(not train[r]) and prior_n[r] >= 5 and primary.get(rows[r][3]) in loads
                    for r in range(len(rows))])
    lz = np.array([(loads[primary[rows[r][3]]] - lz_mu) / lz_sd for r in np.nonzero(sel)[0]])
    low = (prior_acc[sel] < med).astype(float)
    X8 = np.column_stack([off[sel], lz, low, lz * low])
    y8 = y[sel].astype(float)
    b8_beta = fit_logistic(X8, y8)
    gl = np.unique(learner[sel], return_inverse=True)[1]
    ng = gl.max() + 1
    inter = []
    for _ in range(BOOT):
        lw = np.bincount(rng.integers(0, ng, ng), minlength=ng).astype(float)
        inter.append(fit_logistic(X8, y8, lw[gl], iters=15)[4])
    lo8, hi8 = float(np.percentile(inter, 2.5)), float(np.percentile(inter, 97.5))
    b8 = ("LOAD HURTS LOW-PRIOR LEARNERS MORE" if hi8 < 0 else "REVERSED" if lo8 > 0
          else "NO INTERACTION DETECTED")

    # ---- descriptive: edge order on TEST
    first = defaultdict(dict)
    for r in np.nonzero(~train)[0]:
        for n in built_q.get(rows[r][3], ()):
            first[rows[r][0]].setdefault(n, rows[r][1])

    def order_share(es):
        shares = []
        for a, b in es:
            both = [(f[a], f[b]) for f in first.values() if a in f and b in f]
            if len(both) >= 30:
                shares.append(sum(x < z for x, z in both) / len(both))
        return {"edges_scored": len(shares), "median_share_a_first": float(np.median(shares)) if shares else None,
                "share_of_edges_above_half": float(np.mean([s > 0.5 for s in shares])) if shares else None}

    res = {
        "build": {"families": mg["families"], "nodes": len(nodes), "terminal_nodes": sum(n["terminal"] for n in mg["nodes"]),
                  "accumulation": mg["accumulation"], "edges": len(E), "tagged_questions": len(built_q),
                  "untagged": len(tg["untagged"]),
                  "nodes_with_no_question": len(set(nodes) - {n for ns in built_q.values() for n in ns}),
                  "tags_per_question": dict(Counter(len(v) for v in built_q.values()))},
        "split": {"train_attempts": int(train.sum()), "test_attempts": int((~train).sum()),
                  "test_learners": int(len(set(learner[~train])))},
        "B11": {"auc": point, "differences": D, "betas": betas, "verdict": b11, "edges_verdict": ev,
                "floor_passes": floor_ok, "direction_control": direction},
        "B3": {"judged_recall_lenient": cov_len, "judged_recall_strict": cov_str, "reference_depth3": len(d3_names),
               "overlap_depth3": ov3, "overlap_leaf": ovl, "terminal_present": terminal, "met": b3_met},
        "B4": b4d, "B7": b7d,
        "B8": {"beta": dict(zip(["intercept", "off", "load_z", "low", "load_z_x_low"], b8_beta.tolist())),
               "interaction_lo": lo8, "interaction_hi": hi8, "attempts": int(sel.sum()), "verdict": b8},
        "edge_order": {"built": order_share(E), "shuffled": order_share(relabel(E, nodes, SEED))},
        "spend_usd": spent(),
    }
    (smoke or OUT).joinpath("result.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({k: res[k] for k in ("build", "split")}, indent=1))
    print("AUC", {m: round(v, 4) for m, v in point.items()})
    for k, v in D.items():
        print(f"  {k:<8} {v['diff']:+.4f} [{v['lo']:+.4f}, {v['hi']:+.4f}]")
    print("B11:", b11, "|", ev, "| direction", direction["verdict"])
    print(f"B3: judged lenient {cov_len:.3f} strict {cov_str:.3f}; overlap depth3 {ov3}; leaf {ovl}; "
          f"terminal {terminal}; met {b3_met}")
    print("B4:", b4d)
    print("B7:", b7d)
    print("B8:", res["B8"])
    print("edge order:", res["edge_order"])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", choices=["build", "judge", "analyse"])
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--smoke", type=Path, help="fake-data directory for analyse (see analyse)")
    a = ap.parse_args()
    if a.synthetic:
        synthetic()
    elif a.cmd == "build":
        BUILD.mkdir(exist_ok=True)
        build()
    elif a.cmd == "judge":
        judge()
    elif a.cmd == "analyse":
        analyse(a.smoke)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
