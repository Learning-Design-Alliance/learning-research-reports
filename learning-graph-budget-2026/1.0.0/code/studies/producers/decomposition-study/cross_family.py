"""PRE-REGISTERED: do different model families, as independent proposers, agree on which capabilities a
domain contains, and does capture-recapture over a cross-family pool estimate completeness correctly?

Written 2026-09-25 before any proposal call of this study was made and before any cross-family text
existed. Phase 1 ran only `--synthetic` (no model call; no real list read) and `--dry-run` (M1-M8
read for item counts, mean length and a prompt sample, nothing matched or scored; two routing probes,
no proposal, no matching). The maintainer commits this file before phase 2.

WHY. Paper 1's completeness section argues that capture-recapture over repeated runs of one model
over-certifies, because the runs are too alike (same-model edge kappa 0.72-0.84, completeness_kappa
TRUE arm +25 to +35 points there; on this domain eight runs of one model named 9 of the 11 reference
capabilities and missed the same two every time, which Chao2 cannot see). Its proposed remedy is
independent contributors. The human version of that remedy (PROTOCOL.md) is waiting for lists. This
study tests the model-only version: proposers from different families. It also inherits
completeness_nodes.py's finding that node-level capture-recapture is MATCHING-LIMITED (5% synonym
misses move Chao2 7-10 points low), so the matcher is calibrated before use and its error is carried
into the estimate as an interval.

INPUTS (all committed; no corpus with redistribution terms is read)
  model-runs/M1-M8.txt      8 runs of google/gemini-3.8-flash, build_graph.FLARE_PROMPT on the topic
                            below, generated 2026-09-24 by analyse.py (temperature 1.0, max_tokens
                            4000, no seed, router-chosen provider not recorded). The within-model pool.
  pipeline/build_graph.py   REFERENCE_STEPS, the 11-capability authored subtraction ladder (validity
                            anchor), and FLARE_PROMPT.
  second-author/out/datasci-cta-{A,B,C}.json and node-overlap-judgements.csv / node-overlap-rejudge.csv
                            the 92 CTA-added capabilities and the 2,811 labelled cross-run pairs
                            (30 SAME, 50 OVERLAPPING, 2,731 DIFFERENT after collapsing the 281 blind
                            repeats, which agree 281/281), plus a 400-row independent re-judge
                            (398/400 agree; 2 first-judge SAME pairs re-judged OVERLAPPING / DIFFERENT).
                            Both judges were Anthropic-family agents: calibration measures agreement
                            with one family's judgements, not truth. The labels' own ceiling is the
                            re-judge kappa 0.965 (SAME vs not).

PROPOSERS    Frozen prompt: build_graph.FLARE_PROMPT with topic compare_models.GOLD_DOMAIN =
             "subtraction of whole numbers in primary mathematics, including borrowing and regrouping",
             byte-identical to the M1-M8 runs (sha256 asserted: PROMPT_SHA256). One user message, no
             system message, parsed with stability.lines (the M runs' parser).
             One run per family, first slug in FAMILIES that answers (slugs chosen 2026-09-25 from
             OpenRouter's public models listing: current, non-deprecated, priced below $2.50/M input
             where the family allows; prices in PRICES):
               google     google/gemini-3.8-flash             (the M1-M8 model)
               openai     openai/gpt-6-sol           > openai/gpt-6-luna
               anthropic  anthropic/claude-sonnet-5  > anthropic/claude-opus-5.5
               meta       meta-llama/llama-4-maverick > meta-llama/llama-3.3-70b-instruct
               mistral    mistralai/mistral-medium-3-5 > mistralai/mistral-small-2603
               qwen       qwen/qwen3.8-max-0902      > qwen/qwen3.7-plus > qwen/qwen3.8-flash
               deepseek   deepseek/deepseek-v4-pro   > deepseek/deepseek-v4.1-flash
               zai        z-ai/glm-5.3               > z-ai/glm-5.2
               moonshot   moonshotai/kimi-k2.6       > moonshotai/kimi-k2.5
               xai        x-ai/grok-4.7              > x-ai/grok-4.3
             A slug "answers" if it returns HTTP 200 and >= 10 parsed items. A 4xx (including the
             account data-policy guardrail's 404 "no endpoints matching your guardrail restrictions")
             moves to the next slug; the guardrail is never routed around (no provider override, no
             other key). Empty or truncated output is retried once at RETRY_MAX_TOKENS, then the next
             slug. A family with no answering slug is BLOCKED/FAILED and RESERVE families (cohere,
             xiaomi, stepfun, in that order, never a judge family) top the pool up to 10. Fewer than 8
             resolved families: POOL TOO SMALL, everything descriptive.
             Plus one repeat for each of REPEAT_FAMILIES = google, deepseek (same slug, next seed,
             pinned to the provider that served the family's first run, fallbacks off) -- within-model
             pairs on exactly the cross-family calls' footing. google is chosen because it bridges to
             M1-M8; deepseek as an open-weights family from a different lab.
             Request: temperature 1.0 (as M1-M8; endpoints that do not take it -- OpenAI gpt-6,
             Anthropic sonnet-5 -- ignore it, and the recorded request says so), seed SEED for first
             runs and SEED + 1 for repeats (honoured only by endpoints that support seed), max_tokens
             PROPOSE_MAX_TOKENS, provider = router's choice under the account guardrail for first runs,
             no reasoning parameter (provider default). Every raw output is written, before anything
             reads it, to cross-family-runs/<run>.json with: requested slug, served model and provider
             as the response names them, generation id, full request parameters, prompt and its sha256,
             UTC timestamp, usage and cost, finish reason, raw text, parsed items, and every failed
             attempt (slug, error). Existing files are never overwritten.

MATCHING     Both matchers are calibrated on the labelled CTA pairs before any subtraction list is
             matched, and the judge is chosen by that calibration alone.
  J (headline) JUDGED, list-vs-list. One call per pair of lists: the judge sees list X and list Y
             (items shuffled, sides swapped at random, both seeded by the pair id) and returns every
             SAME or OVERLAPPING pair as JSON, with two directional flags, x_covers_y and y_covers_x
             ("A covers B" = every task that tests B as stated is also a task of A as stated; a
             prerequisite is NOT covered). The rubric is cta_node_overlap.py's committed rubric,
             extracted verbatim from its docstring (sha256 asserted: RUBRIC_SHA256). Pairs not listed
             are DIFFERENT. The relation label is authoritative; label/flag inconsistencies are
             counted. Splits and lumps: an item linked to >= 2 items on the other list, each of which
             it covers, is a LUMP (the other list SPLITS it); counted per list pair, descriptive.
             Judge: JUDGES[0] = minimax/minimax-m3, a family outside the proposer pool (and outside the
             Anthropic family that wrote the labels); fallback JUDGES[1] =
             nvidia/nemotron-3-ultra-550b-a55b, also outside both. temperature 0, seed SEED,
             max_tokens JUDGE_MAX_TOKENS. The first calibration call goes to the router's choice; every
             later call of that judge is pinned to the provider that served it, so calibration and use
             share a backend. An unparseable reply is retried once at seed + 1; still unparseable, the
             list pair is MISSING (reported, excluded).
             CALIBRATION: the three CTA list pairs A-B, A-C, B-C (33x27, 33x32, 27x32 = 2,811 pairs)
             in exactly this format, rep 0 (primary) and rep 1 (reshuffled, sides re-drawn: test-retest).
             6 calls per judge. Against the first judge's labels (and, as a variant, excluding the 2
             pairs the re-judge disputed): synonym-miss rate = P(J != SAME | label SAME); false-merge
             rate = P(J = SAME | label DIFFERENT); grain promotion P(J = SAME | label OVERLAPPING);
             lenient rates on linked (SAME or OVERLAPPING) vs not; Cohen's kappa strict and lenient;
             retest kappa; the full 3x3 confusion. A judge PASSES if all 3 rep-0 calls parse, kappa
             strict >= 0.40 and kappa lenient >= 0.40. The first passing judge in JUDGES is used; none
             passing -> MATCHER NOT CALIBRATED (all judged numbers descriptive, no verdict). The
             calibration domain (data science, ~22-word statements) is not the target domain
             (subtraction, ~12 words): a stated limit, not corrected.
  E            EMBEDDING, cosine similarity of vectors from the first of EMBEDDERS that the account
             guardrail admits, in order perplexity/pplx-embed-v1-4b, baai/bge-m3 (both outside the
             proposer pool), google/gemini-embedding-2, openai/text-embedding-3-large (inside it; an
             embedding proposes nothing, so family matters less here than for the judge), called
             through shared/llm.embed and pinned to the provider that served its calibration call.
             voyageai/voyage-4, the first choice, was refused by the guardrail at the phase-1 probe and
             is not used. None admitted -> "no embedding matcher callable", said so. Thresholds fixed
             on the calibration pairs: tau_S maximises Cohen's kappa against label SAME, tau_L
             against label linked, over a 0.01 grid; SAME if cos >= tau_S,
             OVERLAPPING if tau_L <= cos < tau_S. Rates for propagation are held out: choose the
             taus on two CTA run pairs, score the third, pool the three held-out confusions. PASSES if
             held-out kappa strict >= 0.40, else descriptive.

ANCHOR       Every list (10 families + 2 repeats + M1-M8 = 20) is matched to the 11 reference
             capabilities with the same matcher (20 list-vs-reference calls). The reference is a
             subset of valid capabilities, not the domain. A list RECOVERS reference item g if at least
             one of its items is SAME as g (strict, headline); lenient = SAME or OVERLAPPING.

ESTIMAND     As the matched-estimand rerun (completeness_kappa TRUE arm, reference as truth): restrict
             each list to its proposals matched to reference items; the incidence of reference item g
             across the k lists of a pool is the set of lists that recover g.
             claimed = S_obs / Chao2 (learner-sim/completeness.chao2, bias-corrected form when q2 = 0);
             actual  = S_obs / 11;   error = claimed - actual (positive = over-certifies).
             Pools: (i) the cross-family pool, all resolved families (k = 10 if all resolve);
             (ii) M1-M8 (k = 8); (iii) every same-size subset of each, k = 3 .. 8: all C(n_fam, k)
             family subsets and all C(8, k) M subsets, mean error per k. The headline comparison is at
             k = 8: mean over the C(n_fam, 8) family subsets vs M1-M8.

MATCHING ERROR PROPAGATION (headline intervals)
             Per draw (DRAWS = 2000): the strict miss rate m ~ Beta(1 + calibration SAME pairs the
             matcher missed, 1 + those it caught) and the false-merge rate f ~ Beta(1 + non-SAME pairs
             judged SAME, 1 + the rest); the matching error is RE-APPLIED to the judged decisions (each
             SAME link dropped with probability m, each other pair merged with probability f) and every
             statistic recomputed. The shift a second application adds is taken as the shift the first
             added to the truth, so the interval is the basic (reflected) bootstrap interval
             [2 x point - q97.5, 2 x point - q2.5]; the mean shift is reported as the estimated matching
             bias, signed. It assumes the matching error's effect is stable when re-applied; S2 below
             checks the coverage that assumption buys. The same machinery runs for E with its held-out
             confusion, and for the k = 8 comparison and the Sorensen difference.
             Design note (phase 1). The first design drew each pair's truth from base-rate-adjusted
             predictive values, pairs independent given their judged class. In S2 it covered the
             perfect-matching error in only 0.30 / 0.13 of CORRELATED worlds (k = 8 / 10): independent
             restoration scatters recovered links over items that every proposer truly missed, erasing
             exactly the shared blind spots that make a pool over-certify. It was replaced before any
             real call; the synthetic output kept is the replacement's.

STATISTICS   - Recall of each run (strict and lenient, of 11); reference items no family names; items
               no M run names (U_M).
             - Pairwise Sorensen per list pair from J (headline independence statistic): (items of X
               SAME to some item of Y + items of Y SAME to some item of X) / (|X| + |Y|). Means over
               the C(n_fam, 2) cross-family pairs, the 28 M pairs, the 2 same-footing repeat pairs,
               and the 16 google-run x M-run pairs (footing bridge, descriptive). Interval on
               cross - within: bootstrap over LISTS (the unit that was sampled; resample families and
               M runs with replacement, pairs of a list with itself skipped), BOOT = 2000.
             - Node kappa: pairwise Cohen's kappa (shared.stats.kappa) on the 11-item reference
               incidence, cross-family vs within-model means. It places each pool approximately on
               completeness_kappa's kappa grid (whose kappa is over a 200-candidate universe; the
               placement is indicative). Kappa over the union of matched clusters has no true negatives
               and is not reported (NODE-OVERLAP.md).
             - Descriptive, no verdict: Chao2 over ALL proposals of each pool (clusters = connected
               components of strict J links, union-find; components > 6 items or with > 2 items from
               one list flagged), whose target has no truth.

PREDICTIONS AND VERDICTS (fixed now; every comparison signed; BAND = 0.15, as PROTOCOL.md section 8C)
  V0 GATES   MATCHER NOT CALIBRATED (no judge passes) or POOL TOO SMALL prefix every verdict and make
             it descriptive.
             If the synthetic detection floor (below) is not cleared, V1's verdict string carries the
             suffix " (BELOW DETECTION FLOOR)" and Paper 1 may not cite it as a test.
  V1 CALIBRATION of the cross-family pool, on the matching interval [lo, hi] of its error:
               CROSS-FAMILY POOL CALIBRATED        -0.15 <= lo and hi <= +0.15
               CROSS-FAMILY POOL STILL OVER-CERTIFIES   lo > +0.15
               CROSS-FAMILY POOL UNDER-CERTIFIES   hi < -0.15
               MATCHING-LIMITED                    otherwise (the interval crosses a band edge; the
                                                   point estimate's side is stated beside it)
             The same bands for M1-M8, strings SAME-MODEL RUNS CALIBRATED / STILL OVER-CERTIFY /
             UNDER-CERTIFY / MATCHING-LIMITED. Predicted: M1-M8 STILL OVER-CERTIFY (the earlier matcher
             put them at +0.18: 9 of 11 found, Chao2 claiming 1.00); the cross-family pool CALIBRATED.
  V2 COMPARISON at k = 8, paired within each matching draw: D = error(M1-M8) - mean error(family
             8-subsets). Predicted D > 0 (the same-model pool over-certifies more).
               PREDICTION CONFIRMED  2.5th percentile of D > 0
               PREDICTION REFUTED    97.5th percentile of D < 0
               INCONCLUSIVE          otherwise
             Beside it, whether |error| is smaller for the cross-family subsets at the point estimate;
             a CONFIRMED D with a larger cross-family |error| is reported as "CONFIRMED IN DIRECTION,
             NOT CLOSER" (the cross-family pool under-certifies instead).
  V3 INDEPENDENCE: d = mean cross-family Sorensen - mean M-pair Sorensen. Predicted d < 0.
               CROSS-FAMILY MORE DIVERSE     list-bootstrap 97.5th percentile of d < 0
               CROSS-FAMILY LESS DIVERSE     2.5th percentile > 0 (prediction refuted)
               NO FAMILY EFFECT DETECTED     otherwise (read against the synthetic MDE)
             FOOTING: if the 2 same-footing repeat pairs' mean Sorensen lies outside the range of the
             28 M pairs, V3 is flagged "FOOTING CONFOUNDED" (M1-M8 were not generated on this study's
             footing) and read on the repeat pairs instead, descriptively.
  V4 BLIND SPOTS: U_M = reference items no M run recovers (strict). Predicted: the cross-family pool
             recovers them (the earlier matcher's U_M was items 8 and 11: "several borrowings ... in
             nonadjacent columns" and "Subtract whole numbers of any size").
               CROSS-FAMILY RECOVERS WHAT ONE MODEL MISSES   every item of U_M named by >= 1 family
               PARTIAL RECOVERY                             some
               SHARED BLIND SPOT                            none
               NO SAME-MODEL BLIND SPOT UNDER THIS MATCHER  U_M empty (items 8 and 11 still reported)
  V5 MATCHERS AGREE / MATCHERS DISAGREE on V1 (E beside J), when E passes its calibration.

FOR PAPER 1 (research/article/limits-of-inferring-prerequisite-structure.md, section 5.3), fixed now:
  CALIBRATED (with V3 MORE DIVERSE): the independent-contributor remedy has a model-only form on this
      domain -- a cross-family pool, restricted to reference-matched items and matched by a calibrated
      judge, reads completeness within 15 points of the outside check. One domain, an 11-item
      reference; stated as an existence result, not a method.
  STILL OVER-CERTIFIES: family diversity does not remove the over-certification. The sentence
      "completeness cannot be estimated from repeated model runs" extends from runs of one model to
      models of different families; if the gap is carried by items no family names, it is stated as a
      shared blind spot of the training distribution, which capture-recapture cannot see by
      construction. The human-contributor study stays the only proposed fix.
  UNDER-CERTIFIES: the cross-family estimate errs toward calling the list incomplete (routes to flare,
      the safe direction); the paper may say so for this domain.
  MATCHING-LIMITED: consistent with completeness_nodes.py; the paper reports the matching interval
      and says a node-level estimate from any pool needs a matcher calibrated tighter than this one
      (a human matcher) before it is read.
  MATCHER NOT CALIBRATED / POOL TOO SMALL: no completeness claim; cited as an attempted check.
  If M1-M8 do NOT over-certify under this matcher, the paper's same-model over-certification figure on
  this domain is stated as matcher-dependent.

SYNTHETIC DETECTION FLOOR (--synthetic; no model call; criteria fixed before it was first run)
  S1 Chao2 on 11 items, perfect matching, 2000 worlds per cell, k = 8 and 10, per-run recall ~7/11:
     INDEPENDENT (p_i ~ U(0.25, 1.0), independent), CORRELATED (completeness.propose's shared-latent
     model, corr 0.85, 7 of 11 per run), BLIND SPOT (2 items p = 0, others U(0.35, 1.0)). FLOOR
     CLEARED if at k = 8 INDEPENDENT reads within the band in >= 0.80 of worlds and CORRELATED reads
     above it in >= 0.80; otherwise V1 carries the suffix.
  S2 Propagation coverage: planted judges NOISY (SAME pairs judged S/O/D 0.70/0.25/0.05, others
     0.002/0.02/0.978) and GOOD (0.90/0.08/0.02; 0.0005/0.01/0.9895), calibration counts drawn at the
     real sizes (30 SAME, 2,781 not), 15 filler proposals per list, 150 worlds per cell; share of
     worlds whose perfect-matching error lies inside the 95% matching interval. PROPAGATION COVERS if
     >= 0.80 in every cell; otherwise V1's interval is labelled "under-covers in synthetic check".
  S3 Sorensen floor: lists of 25 drawn from 120 weighted items (within-model lists share weights;
     families share them with correlation rho), 10 families vs 8 runs; power of V3's list bootstrap
     by planted difference; MDE = the smallest planted |d| with power >= 0.80.
  S4 End to end: an oracle judge answers the real prompt format on synthetic lists; the shuffling,
     side swapping, parsing and aggregation must recover the planted decisions and statistics
     exactly (asserted).

SYNTHETIC RESULTS (phase 1, out/cross-family-synthetic.json). The S1-S4 criteria were fixed before the
  first run; the GOOD planted judge and S2's width and verdict-share columns were added after it, with
  the propagation redesign recorded above.
  S4 recovered exactly (decisions, incidence, Chao2 and Sorensen through the real prompt format, with
     side swaps checked both ways).
  S1 FLOOR CLEARED. Perfect matching, error mean (sd): INDEPENDENT k=8 -0.006 (0.051), within the band
     in 0.98 of worlds; CORRELATED k=8 +0.260 (0.096), above it in 0.87 (node kappa 0.84); BLIND SPOT
     k=8 +0.181 (0.025), above it in 0.94 at node kappa 0.39. k = 10 is the same to 0.01. So on 11
     items Chao2 separates independent from same-model-like pools, and it also over-certifies a
     low-kappa pool whose members share a blind spot: STILL OVER-CERTIFIES does not by itself say the
     cause is dependence -- the items no proposer names say which.
  S2 PROPAGATION COVERS: coverage 0.83-0.91 (NOISY) and 0.91-0.97 (GOOD) in all twelve cells. The
     price is width: NOISY intervals are 0.35-0.56 wide, so a truly calibrated pool is declared
     CALIBRATED in only 0.07 (k=8) / 0.26 (k=10) of worlds and an over-certifying one STILL
     OVER-CERTIFIES in 0.07-0.42; GOOD intervals are 0.13-0.37 wide, CALIBRATED 0.49 / 0.77, STILL
     OVER-CERTIFIES 0.60-0.69. Uncorrected, a NOISY judge's synonym misses pull the point estimate
     0.09-0.14 low in over-certifying pools (masking, as completeness_nodes found). Stated now: unless
     the chosen judge's calibrated miss rate is near 0.10 or below, MATCHING-LIMITED is the expected V1
     verdict, and it is then a measurement of the matcher, not of the pool.
  S3 MDE |d| = 0.12 for V3's list bootstrap (power 0.95 at a planted -0.120, 0.53 at -0.068), so NO
     FAMILY EFFECT DETECTED rules out only differences larger than about 0.12.

BUDGET       Study cap $15 for both phases (BUDGET_USD). Every call's cost (usage.cost when returned,
             else tokens x PRICES) goes to out/cross-family-spend.json; a call whose worst-case cost
             would cross the cap is not made and the run stops. The key endpoint's usage is recorded at
             the start and end as a cross-check (other sessions may share the key). Estimate from the
             listing prices (printed by --dry-run; chars/4 tokens, 5,000 reasoning tokens per proposal
             and 8,000 per judge call expected): 12 proposal calls + 2 retries, 6 calibration calls
             (+6 if the fallback judge is needed), 20 anchor calls, 45 + 28 + 2 + 16 = 91 list-pair
             calls, <= 6 embedding calls: expected $1.9; worst case with every call spending its full
             max_tokens $6.6, and about $11 if the fallback judge has to do all the matching. The
             guard enforces the cap whatever happens.

DRY RUN (phase 1, out/cross-family-dryrun.json). Probe 1, chat: minimax/minimax-m3 answered "ok",
             served model minimax/minimax-m3, provider Parasail (router's choice under the guardrail),
             generation id, request {temperature 0, max_tokens 400, seed}, usage and cost $0.0000909
             all recorded by shared/llm.call's new `meta`. Probe 2, embedding: voyageai/voyage-4
             refused by the account guardrail (HTTP 404 "0 endpoints ... matching your guardrail
             restrictions and data policy"), no charge; shared/llm.embed retried the refusal before this
             phase-1 fix made it stop on 400/403/404. Key usage 11.945047547 -> 11.945138447.

DIRECTION    No arrows enter: the units are capability sets. Every error is claimed minus actual, every
             difference is stated with its sign, and nothing is folded with abs() except the symmetric
             BAND, which is paired with the signed verdicts.

    python3 cross_family.py --synthetic   # detection floor, no model call -> out/cross-family-synthetic.json
    python3 cross_family.py --dry-run     # roster, prompts, cost estimate, <= 2 tiny routing calls
    python3 cross_family.py run           # phase 2: calibrate -> propose -> match -> analyse (resumable)
    python3 cross_family.py analyse       # re-run the analysis on committed outputs, no model call

DIRECTION: symmetric -- the DIRECTION entry above in the form board/direction_audit.py reads
(added 2026-09-26, after the run; no analysis changed).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import sys
import textwrap
import urllib.request
from collections import Counter
from itertools import combinations
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in (ROOT, ROOT / "studies/producers/pipeline", ROOT / "studies/simulation/learner-sim",
          ROOT / "studies/producers/second-author"):
    sys.path.insert(0, str(p))

from shared import llm  # noqa: E402
from shared.stats import kappa  # noqa: E402
from completeness import chao2  # noqa: E402

OUT = HERE / "out"
RUNS_DIR = HERE / "cross-family-runs"
JUDGE_DIR = HERE / "cross-family-judgements"
CACHE = HERE / ".cache-cross-family"
M_DIR = HERE / "model-runs"
CTA_OUT = ROOT / "studies/producers/second-author/out"
LABELS = ROOT / "studies/producers/second-author/node-overlap-judgements.csv"
REJUDGE = ROOT / "studies/producers/second-author/node-overlap-rejudge.csv"
RESULT = OUT / "cross-family-result.json"
SYNTH = OUT / "cross-family-synthetic.json"
DRY = OUT / "cross-family-dryrun.json"
SPEND = OUT / "cross-family-spend.json"

PROMPT_SHA256 = "d63964c7ec19ebce6981118cf56cd24f17cadd0435267b33cc53eeaf9bf8a3b8"
RUBRIC_SHA256 = "712b4387049d939eab40dc14d359237a2370af4a70d0bb330d79a9d836bb8078"
SEED = 20260926
TEMPERATURE = 1.0
PROPOSE_MAX_TOKENS = 16000
RETRY_MAX_TOKENS = 32000
MIN_ITEMS = 10
JUDGE_TEMPERATURE = 0.0
JUDGE_MAX_TOKENS = 32000
BAND = 0.15
BOOT = 2000
DRAWS = 2000
KAPPA_PASS = 0.40
MIN_FAMILIES = 8
BUDGET_USD = 15.0
#: key usage (USD) read at the start of phase 1, before any call of this study
KEY_USAGE_AT_START = 11.945047547

FAMILIES: dict[str, list[str]] = {
    "google": ["google/gemini-3.8-flash"],
    "openai": ["openai/gpt-6-sol", "openai/gpt-6-luna"],
    "anthropic": ["anthropic/claude-sonnet-5", "anthropic/claude-opus-5.5"],
    "meta": ["meta-llama/llama-4-maverick", "meta-llama/llama-3.3-70b-instruct"],
    "mistral": ["mistralai/mistral-medium-3-5", "mistralai/mistral-small-2603"],
    "qwen": ["qwen/qwen3.8-max-0902", "qwen/qwen3.7-plus", "qwen/qwen3.8-flash"],
    "deepseek": ["deepseek/deepseek-v4-pro", "deepseek/deepseek-v4.1-flash"],
    "zai": ["z-ai/glm-5.3", "z-ai/glm-5.2"],
    "moonshot": ["moonshotai/kimi-k2.6", "moonshotai/kimi-k2.5"],
    "xai": ["x-ai/grok-4.7", "x-ai/grok-4.3"],
}
RESERVE: dict[str, list[str]] = {
    "cohere": ["cohere/command-a-plus"],
    "xiaomi": ["xiaomi/mimo-v2.6-pro"],
    "stepfun": ["stepfun/step-3.7-flash"],
}
REPEAT_FAMILIES = ("google", "deepseek")
JUDGES = ["minimax/minimax-m3", "nvidia/nemotron-3-ultra-550b-a55b"]
EMBEDDERS = ["perplexity/pplx-embed-v1-4b", "baai/bge-m3", "google/gemini-embedding-2",
             "openai/text-embedding-3-large"]

#: USD per million tokens (input, output) from OpenRouter's public listing on 2026-09-25, used for the
#: estimate and when a response carries no cost. `--dry-run` re-reads the listing and flags changes.
PRICES: dict[str, tuple[float, float]] = {
    "google/gemini-3.8-flash": (0.75, 3.75),
    "openai/gpt-6-sol": (2.0, 10.0), "openai/gpt-6-luna": (0.10, 0.50),
    "anthropic/claude-sonnet-5": (2.0, 10.0), "anthropic/claude-opus-5.5": (4.0, 20.0),
    "meta-llama/llama-4-maverick": (0.1875, 0.6525), "meta-llama/llama-3.3-70b-instruct": (0.10, 0.32),
    "mistralai/mistral-medium-3-5": (1.5, 7.5), "mistralai/mistral-small-2603": (0.15, 0.60),
    "qwen/qwen3.8-max-0902": (2.0, 6.0), "qwen/qwen3.7-plus": (0.32, 1.28),
    "qwen/qwen3.8-flash": (0.15, 0.47),
    "deepseek/deepseek-v4-pro": (0.52, 1.041), "deepseek/deepseek-v4.1-flash": (0.099, 0.60),
    "z-ai/glm-5.3": (1.4, 4.4), "z-ai/glm-5.2": (0.65, 2.0415),
    "moonshotai/kimi-k2.6": (0.95, 4.0), "moonshotai/kimi-k2.5": (0.45, 2.25),
    "x-ai/grok-4.7": (1.6, 4.8), "x-ai/grok-4.3": (1.25, 2.5),
    "cohere/command-a-plus": (0.30, 1.50), "xiaomi/mimo-v2.6-pro": (0.435, 0.87),
    "stepfun/step-3.7-flash": (0.20, 1.15),
    "minimax/minimax-m3": (0.30, 1.20), "nvidia/nemotron-3-ultra-550b-a55b": (0.60, 2.40),
    "voyageai/voyage-4": (0.06, 0.0), "perplexity/pplx-embed-v1-4b": (0.03, 0.0),
    "baai/bge-m3": (0.01, 0.0), "google/gemini-embedding-2": (0.20, 0.0),
    "openai/text-embedding-3-large": (0.13, 0.0),
}
DEC = {"DIFFERENT": 0, "OVERLAPPING": 1, "SAME": 2}
NAMES = {v: k for k, v in DEC.items()}


# ---------------------------------------------------------------- frozen inputs

def frozen_prompt() -> str:
    import build_graph as bg
    import compare_models as cm
    p = bg.FLARE_PROMPT.format(topic=cm.GOLD_DOMAIN)
    assert hashlib.sha256(p.encode()).hexdigest() == PROMPT_SHA256, \
        "FLARE_PROMPT or GOLD_DOMAIN changed since pre-registration; the M1-M8 comparison is void"
    return p


def reference() -> list[str]:
    import compare_models as cm
    assert len(cm.GOLD) == 11
    return list(cm.GOLD)


def rubric() -> str:
    import cta_node_overlap as cno
    d = cno.__doc__
    r = textwrap.dedent(d[d.index("Rubric, fixed now:") + len("Rubric, fixed now:\n"):
                          d.index("`reason`:")]).strip()
    assert hashlib.sha256(r.encode()).hexdigest() == RUBRIC_SHA256, "the committed CTA rubric changed"
    return r


def parse_items(txt: str) -> list[str]:
    import stability
    return stability.lines(txt)


def m_runs() -> dict[str, list[str]]:
    return {p.stem: [l.strip() for l in p.read_text().splitlines() if l.strip()]
            for p in sorted(M_DIR.glob("M*.txt"), key=lambda q: int(q.stem[1:]))}


def cta_lists() -> dict[str, list[str]]:
    return {r: [n["statement"] for n in json.loads((CTA_OUT / f"datasci-cta-{r}.json").read_text())
                ["new_nodes"]] for r in "ABC"}


def cta_labels() -> tuple[dict[frozenset, int], set[frozenset]]:
    """First judge's decision per unordered pair (repeats collapsed; they agree 281/281, asserted),
    and the pairs the independent re-judge disputed."""
    import csv
    by: dict[frozenset, set] = {}
    with LABELS.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            by.setdefault(frozenset((r["statement_1"], r["statement_2"])), set()).add(r["decision"])
    assert all(len(v) == 1 for v in by.values()), "repeat rows disagree; re-read NODE-OVERLAP.md"
    labels = {k: DEC[next(iter(v))] for k, v in by.items()}
    disputed = set()
    with REJUDGE.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["first_judge"] != r["independent_judge"]:
                disputed.add(frozenset((r["statement_1"], r["statement_2"])))
    return labels, disputed


# ---------------------------------------------------------------- budget

def _ledger() -> dict:
    if SPEND.exists():
        return json.loads(SPEND.read_text())
    return {"budget_usd": BUDGET_USD, "key_usage_at_start": KEY_USAGE_AT_START, "calls": []}


def spent() -> float:
    return sum(c["cost_usd"] for c in _ledger()["calls"])


def cost_of(model: str, meta: dict) -> float:
    u = meta.get("usage") or {}
    if isinstance(u.get("cost"), (int, float)):
        return float(u["cost"])
    pin, pout = PRICES.get(model, (5.0, 25.0))
    return (u.get("prompt_tokens", 0) * pin + u.get("completion_tokens", 0) * pout) / 1e6


def charge(model: str, meta: dict, what: str) -> None:
    if meta.get("from_cache"):
        return
    led = _ledger()
    led["calls"].append({"what": what, "model": model, "provider": meta.get("provider"),
                         "cost_usd": cost_of(model, meta), "usage": meta.get("usage"),
                         "timestamp_utc": meta.get("timestamp_utc")})
    OUT.mkdir(exist_ok=True)
    SPEND.write_text(json.dumps(led, indent=1) + "\n")


def guard(model: str, prompt_chars: int, max_tokens: int) -> None:
    pin, pout = PRICES.get(model, (5.0, 25.0))
    worst = (prompt_chars / 3 * pin + max_tokens * pout) / 1e6
    if spent() + worst > BUDGET_USD:
        raise SystemExit(f"BUDGET: ${spent():.2f} spent; the next call could cost ${worst:.2f} and cross "
                         f"the ${BUDGET_USD:.0f} cap. Stopped before calling.")


def logged_call(model: str, prompt: str, *, seed: int, max_tokens: int, temperature: float,
                provider, what: str, attempts: int = 3) -> tuple[str, dict]:
    guard(model, len(prompt), max_tokens)
    meta: dict = {}
    txt = llm.call(model, prompt, seed, cache=CACHE, max_tokens=max_tokens, temperature=temperature,
                   attempts=attempts, provider=provider, meta=meta)
    charge(model, meta, what)
    return txt, meta


# ---------------------------------------------------------------- proposals

def propose_one(run: str, slugs: list[str], seed: int, provider) -> dict | None:
    """First answering slug's run, written before anything reads it. None if no slug answers."""
    path = RUNS_DIR / f"{run}.json"
    if path.exists():
        return json.loads(path.read_text())
    prompt = frozen_prompt()
    failures = []
    for slug in slugs:
        for mt in (PROPOSE_MAX_TOKENS, RETRY_MAX_TOKENS):
            txt, meta = logged_call(slug, prompt, seed=seed, max_tokens=mt, temperature=TEMPERATURE,
                                    provider=provider, what=f"propose {run}")
            items = parse_items(txt)
            if len(items) >= MIN_ITEMS:
                rec = {"run": run, "family": run.split("#")[0], "requested_slug": slug,
                       "served_model": meta.get("served_model"), "provider": meta.get("provider"),
                       "generation_id": meta.get("generation_id"),
                       "timestamp_utc": meta.get("timestamp_utc"), "request": meta.get("request"),
                       "prompt": prompt, "prompt_sha256": PROMPT_SHA256,
                       "finish_reason": meta.get("finish_reason"), "usage": meta.get("usage"),
                       "from_cache": meta.get("from_cache"), "failed_attempts": failures,
                       "raw_text": txt, "items": items}
                RUNS_DIR.mkdir(exist_ok=True)
                path.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
                print(f"   {run:<12} {slug:<36} via {meta.get('provider')}: {len(items)} items")
                return rec
            err = meta.get("last_error", "")
            failures.append({"slug": slug, "max_tokens": mt, "error": err[:200],
                             "finish_reason": meta.get("finish_reason"), "items": len(items)})
            if err.startswith("HTTP 4"):
                break                        # blocked or unknown: next slug, no token retry
    RUNS_DIR.mkdir(exist_ok=True)
    (RUNS_DIR / f"{run}.FAILED.json").write_text(json.dumps(
        {"run": run, "slugs": slugs, "failed_attempts": failures}, indent=1) + "\n")
    print(f"   {run:<12} FAILED: {failures[-1]['error'][:90] if failures else 'no attempt'}")
    return None


def propose_all() -> dict[str, dict]:
    runs: dict[str, dict] = {}
    for fam, slugs in FAMILIES.items():
        rec = propose_one(fam, slugs, SEED, False)
        if rec:
            runs[fam] = rec
    for fam, slugs in RESERVE.items():
        if len(runs) >= len(FAMILIES):
            break
        rec = propose_one(fam, slugs, SEED, False)
        if rec:
            runs[fam] = rec
    for fam in REPEAT_FAMILIES:
        if fam in runs:
            rec = propose_one(f"{fam}#2", [runs[fam]["requested_slug"]], SEED + 1,
                              runs[fam]["provider"])
            if rec:
                runs[f"{fam}#2"] = rec
    return runs


def load_runs() -> dict[str, dict]:
    return {json.loads(p.read_text())["run"]: json.loads(p.read_text())
            for p in sorted(RUNS_DIR.glob("*.json")) if not p.name.endswith(".FAILED.json")}


# ---------------------------------------------------------------- judged matcher

JUDGE_PROMPT = """You are matching two independently written lists of capabilities (things a learner must be able to do) for the same subject. For every pair of statements, one from each list, decide whether they name the same capability.

Definition. "A covers B" means every task that tests B, as B is stated, is also a task that tests A, as A is stated, so that mastering A as stated means mastering B as stated. It does NOT mean that B is a prerequisite of A: a capability needed on the way to A, whose own tasks are not tasks of A, is not covered by A.

Rubric (apply exactly):
{rubric}

In terms of covering: SAME means each covers the other. OVERLAPPING means exactly one covers the other (a split or a lump), or neither covers the other but they share a core performance. DIFFERENT otherwise.

LIST X
{x}

LIST Y
{y}

Decide every pair (Xi, Yj) on its own. One statement may be SAME or OVERLAPPING with several statements on the other list, or with none.
Reply with JSON only, listing every pair that is SAME or OVERLAPPING and omitting DIFFERENT pairs:
{{"links": [{{"x": 1, "y": 3, "relation": "SAME", "x_covers_y": true, "y_covers_x": true}}]}}
If no pair is SAME or OVERLAPPING, reply {{"links": []}}."""


def judge_prompt(x: list[str], y: list[str]) -> str:
    return JUDGE_PROMPT.format(rubric=rubric(), x="\n".join(f"X{i + 1}. {t}" for i, t in enumerate(x)),
                               y="\n".join(f"Y{j + 1}. {t}" for j, t in enumerate(y)))


def parse_links(txt: str, nx: int, ny: int) -> list[dict] | None:
    """Links in presented numbering (1-based), or None if the reply holds no parseable object."""
    s, e = txt.find("{"), txt.rfind("}")
    if s < 0 or e <= s:
        return None
    try:
        obj = json.loads(txt[s:e + 1])
    except json.JSONDecodeError:
        return None
    links = obj.get("links") if isinstance(obj, dict) else None
    if not isinstance(links, list):
        return None
    out = []
    for l in links:
        try:
            x, y, rel = int(l["x"]), int(l["y"]), str(l["relation"]).strip().upper()
        except (KeyError, TypeError, ValueError):
            continue
        if 1 <= x <= nx and 1 <= y <= ny and rel in ("SAME", "OVERLAPPING"):
            out.append({"x": x, "y": y, "relation": rel, "x_covers_y": bool(l.get("x_covers_y")),
                        "y_covers_x": bool(l.get("y_covers_x"))})
    return out


def presentation(pair_id: str, na: int, nb: int, rep: int = 0) -> tuple[list[int], list[int], bool]:
    rng = random.Random(f"{SEED}|{pair_id}|{rep}")
    pa, pb = list(range(na)), list(range(nb))
    rng.shuffle(pa)
    rng.shuffle(pb)
    return pa, pb, rng.random() < 0.5


def judge_pair(judge: str, pair_id: str, a: list[str], b: list[str], *, rep: int = 0,
               provider=True, caller=None) -> dict | None:
    """Decisions of `judge` on every (a_i, b_j), in the callers' own item order.

    Returns {"dec": int array (|a|, |b|) of DEC codes, "a_covers_b", "b_covers_a": bool arrays,
    "inconsistent": count, "meta": ...}, or None if the reply cannot be parsed after one retry."""
    pa, pb, swap = presentation(pair_id, len(a), len(b), rep)
    xs, ys = ([b[j] for j in pb], [a[i] for i in pa]) if swap else ([a[i] for i in pa], [b[j] for j in pb])
    prompt = judge_prompt(xs, ys)
    links, meta, txt = None, {}, ""
    for s in (SEED, SEED + 1):
        if caller is not None:
            txt, meta = caller(prompt), {"synthetic": True}
        else:
            txt, meta = logged_call(judge, prompt, seed=s, max_tokens=JUDGE_MAX_TOKENS,
                                    temperature=JUDGE_TEMPERATURE, provider=provider,
                                    what=f"judge {pair_id} rep{rep}")
        links = parse_links(txt, len(xs), len(ys))
        if links is not None:
            break
    rec = {"pair_id": pair_id, "rep": rep, "judge": judge, "swap": swap, "order_a": pa, "order_b": pb,
           "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "meta": meta,
           "raw_text": txt, "links": links}
    if caller is None:
        d = JUDGE_DIR / judge.replace("/", "__")
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{pair_id}.rep{rep}.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
    if links is None:
        return None
    dec = np.zeros((len(a), len(b)), int)
    acb = np.zeros((len(a), len(b)), bool)
    bca = np.zeros((len(a), len(b)), bool)
    incons = 0
    for l in links:
        # presented X index -> original index on its own side
        if swap:
            i, j, a_cov, b_cov = pa[l["y"] - 1], pb[l["x"] - 1], l["y_covers_x"], l["x_covers_y"]
        else:
            i, j, a_cov, b_cov = pa[l["x"] - 1], pb[l["y"] - 1], l["x_covers_y"], l["y_covers_x"]
        code = DEC[l["relation"]]
        dec[i, j] = max(dec[i, j], code)
        acb[i, j] |= a_cov
        bca[i, j] |= b_cov
        incons += (code == 2) != (a_cov and b_cov)
    return {"dec": dec, "a_covers_b": acb, "b_covers_a": bca, "inconsistent": int(incons),
            "provider": meta.get("provider")}


def splits_lumps(r: dict) -> dict:
    linked = r["dec"] > 0
    lump_a = int(sum((linked[i] & r["a_covers_b"][i]).sum() >= 2 for i in range(linked.shape[0])))
    lump_b = int(sum((linked[:, j] & r["b_covers_a"][:, j]).sum() >= 2 for j in range(linked.shape[1])))
    return {"lumps_in_a": lump_a, "lumps_in_b": lump_b}


# ---------------------------------------------------------------- calibration

CTA_PAIRS = (("A", "B"), ("A", "C"), ("B", "C"))


def confusion(pred: list[int], lab: list[int]) -> list[list[int]]:
    m = [[0] * 3 for _ in range(3)]
    for p, l in zip(pred, lab):
        m[l][p] += 1
    return m                                            # rows = label, cols = matcher


def rates(conf: list[list[int]]) -> dict:
    c = np.array(conf, float)
    same, over, diff = c[2], c[1], c[0]
    pred_s = lambda row: row[2]                          # noqa: E731
    linked = lambda row: row[1] + row[2]                 # noqa: E731
    ns, no, nd = same.sum(), over.sum(), diff.sum()

    def k2(tp, fn, fp, tn):                              # Cohen's kappa from a collapsed 2x2 table
        n = tp + fn + fp + tn
        po = (tp + tn) / n
        pe = ((tp + fn) * (tp + fp) + (fp + tn) * (fn + tn)) / n ** 2
        return float((po - pe) / (1 - pe)) if pe < 1 else float("nan")
    s_tp, s_fn = pred_s(same), ns - pred_s(same)
    s_fp = pred_s(over) + pred_s(diff)
    s_tn = (no + nd) - s_fp
    l_tp = linked(same) + linked(over)
    l_fn = (ns + no) - l_tp
    l_fp = linked(diff)
    l_tn = nd - l_fp
    return {"n": int(c.sum()), "label_counts": {"SAME": int(ns), "OVERLAPPING": int(no), "DIFFERENT": int(nd)},
            "synonym_miss_rate": float(s_fn / ns) if ns else None,
            "false_merge_rate": float(pred_s(diff) / nd) if nd else None,
            "grain_promotion_rate": float(pred_s(over) / no) if no else None,
            "lenient_miss_rate": float(l_fn / (ns + no)) if ns + no else None,
            "lenient_false_merge_rate": float(l_fp / nd) if nd else None,
            "kappa_strict": k2(s_tp, s_fn, s_fp, s_tn), "kappa_lenient": k2(l_tp, l_fn, l_fp, l_tn),
            "confusion_label_rows_matcher_cols_DOS": conf}


def calibrate_judge(judge: str, caller=None) -> dict:
    lists = cta_lists()
    labels, disputed = cta_labels()
    provider = True
    reps: dict[int, dict] = {}
    parsed_all = True
    for rep in (0, 1):
        pred, lab, keys = [], [], []
        for x, y in CTA_PAIRS:
            r = judge_pair(judge, f"cal-{x}{y}", lists[x], lists[y], rep=rep, provider=provider,
                           caller=caller)
            if r is None:
                parsed_all &= rep != 0
                continue
            if provider is True and r.get("provider"):
                provider = r["provider"]                  # pin every later call to this backend
            for i, s in enumerate(lists[x]):
                for j, t in enumerate(lists[y]):
                    k = frozenset((s, t))
                    pred.append(int(r["dec"][i, j]))
                    lab.append(labels[k])
                    keys.append(k)
        reps[rep] = {"pred": pred, "lab": lab, "keys": keys}
    r0 = reps[0]
    conf = confusion(r0["pred"], r0["lab"])
    keep = [n for n, k in enumerate(r0["keys"]) if k not in disputed]
    conf_c = confusion([r0["pred"][n] for n in keep], [r0["lab"][n] for n in keep])
    retest = None
    if reps[1]["keys"] == r0["keys"]:
        retest = kappa([p == 2 for p in r0["pred"]], [p == 2 for p in reps[1]["pred"]])
    res = {"judge": judge, "provider": provider if provider is not True else None,
           "rep0_all_parsed": parsed_all and len(r0["pred"]) == 2811,
           "rates": rates(conf), "rates_excluding_disputed": rates(conf_c),
           "retest_kappa_strict": retest,
           "label_source": "Anthropic-family agents (first judge; independent re-judge on 400 rows)",
           "label_ceiling_kappa_same": 0.965}
    rr = res["rates"]
    res["passes"] = bool(res["rep0_all_parsed"] and rr["kappa_strict"] >= KAPPA_PASS
                         and rr["kappa_lenient"] >= KAPPA_PASS)
    return res


def choose_judge() -> dict:
    cals = []
    for j in JUDGES:
        c = calibrate_judge(j)
        cals.append(c)
        print(f"   judge {j}: kappa strict {c['rates']['kappa_strict']:.3f}, lenient "
              f"{c['rates']['kappa_lenient']:.3f}, miss {c['rates']['synonym_miss_rate']:.3f}, "
              f"false merge {c['rates']['false_merge_rate']:.4f} -> {'PASS' if c['passes'] else 'fail'}")
        if c["passes"]:
            break
    return {"calibrations": cals, "chosen": next((c for c in cals if c["passes"]), None)}


# ---------------------------------------------------------------- embedding matcher

def cosines(va: np.ndarray, vb: np.ndarray) -> np.ndarray:
    na = va / np.linalg.norm(va, axis=1, keepdims=True)
    nb = vb / np.linalg.norm(vb, axis=1, keepdims=True)
    return na @ nb.T


GRID = np.round(np.arange(0.30, 0.99, 0.01), 2)


def best_tau(cos: np.ndarray, lab: np.ndarray, target) -> float:
    ks = [kappa(cos >= t, target(lab)) for t in GRID]
    ks = [(-1 if math.isnan(k) else k) for k in ks]
    return float(GRID[int(np.argmax(ks))])


def emb_classes(cos: np.ndarray, ts: float, tl: float) -> np.ndarray:
    return np.where(cos >= ts, 2, np.where(cos >= min(tl, ts), 1, 0))


def embed_texts(model: str, texts: list[str], provider=True) -> tuple[np.ndarray | None, dict]:
    vecs, meta = [], {}
    for s in range(0, len(texts), 96):
        chunk = texts[s:s + 96]
        guard(model, sum(map(len, chunk)), 0)
        m: dict = {}
        v = llm.embed(model, chunk, cache=CACHE, provider=provider, meta=m)
        charge(model, m, "embed")
        if v is None:
            return None, m
        vecs += v
        meta = m
    return np.array(vecs, float), meta


def calibrate_embedder(model: str) -> dict:
    lists = cta_lists()
    labels, _ = cta_labels()
    allt = [t for r in "ABC" for t in lists[r]]
    V, meta = embed_texts(model, allt)
    if V is None:
        return {"model": model, "passes": False, "error": meta.get("last_error")}
    off = {"A": 0, "B": len(lists["A"]), "C": len(lists["A"]) + len(lists["B"])}
    per = {}
    for x, y in CTA_PAIRS:
        c = cosines(V[off[x]:off[x] + len(lists[x])], V[off[y]:off[y] + len(lists[y])])
        lab = np.array([[labels[frozenset((s, t))] for t in lists[y]] for s in lists[x]])
        per[(x, y)] = (c.ravel(), lab.ravel())
    cos_all = np.concatenate([v[0] for v in per.values()])
    lab_all = np.concatenate([v[1] for v in per.values()])
    ts, tl = best_tau(cos_all, lab_all, lambda l: l == 2), best_tau(cos_all, lab_all, lambda l: l >= 1)
    held_pred, held_lab = [], []
    for out in CTA_PAIRS:
        tr = [k for k in CTA_PAIRS if k != out]
        c_tr = np.concatenate([per[k][0] for k in tr])
        l_tr = np.concatenate([per[k][1] for k in tr])
        a, b = best_tau(c_tr, l_tr, lambda l: l == 2), best_tau(c_tr, l_tr, lambda l: l >= 1)
        held_pred += list(emb_classes(per[out][0], a, b))
        held_lab += list(per[out][1])
    r = rates(confusion(held_pred, held_lab))
    return {"model": model, "provider": meta.get("provider"), "served_model": meta.get("served_model"),
            "tau_same": ts, "tau_linked": tl, "held_out_rates": r,
            "in_sample_rates": rates(confusion(list(emb_classes(cos_all, ts, tl)), list(lab_all))),
            "passes": bool(r["kappa_strict"] >= KAPPA_PASS)}


# ---------------------------------------------------------------- analysis (pure)

def incidence(ref_dec: dict[str, np.ndarray], names: list[str], strict: bool = True) -> np.ndarray:
    """(11, k) bool: list j recovers reference item g."""
    thr = 2 if strict else 1
    return np.stack([(ref_dec[n] >= thr).any(axis=0) for n in names], axis=1)


def chao_error(inc: np.ndarray) -> dict:
    lists = [set(np.nonzero(inc[:, j])[0].tolist()) for j in range(inc.shape[1])]
    s_obs = int(inc.any(axis=1).sum())
    est = chao2(lists) if s_obs else 0.0
    claimed = s_obs / est if est else float("nan")
    actual = s_obs / inc.shape[0]
    return {"s_obs": s_obs, "chao2": float(est), "claimed": claimed, "actual": actual,
            "error": claimed - actual}


def subset_errors(inc: np.ndarray, k: int) -> list[float]:
    return [chao_error(inc[:, list(c)])["error"] for c in combinations(range(inc.shape[1]), k)]


def sorensen(dec: np.ndarray) -> float:
    s = dec == 2
    return float((s.any(axis=1).sum() + s.any(axis=0).sum()) / (s.shape[0] + s.shape[1]))


def mean_pair(stat: dict, names: list[str]) -> float:
    v = [stat[tuple(sorted((a, b)))] for a, b in combinations(names, 2)
         if tuple(sorted((a, b))) in stat]
    return float(np.mean(v)) if v else float("nan")


def list_bootstrap(stat: dict, fam: list[str], mm: list[str], rng: np.random.Generator,
                   n: int = BOOT) -> list[float]:
    """cross - within, resampling lists (the sampled unit); a list paired with its own copy is skipped."""
    out = []
    for _ in range(n):
        f = [fam[i] for i in rng.integers(0, len(fam), len(fam))]
        m = [mm[i] for i in rng.integers(0, len(mm), len(mm))]
        # Skip pairs the judge's reply could not be parsed for, as mean_pair does (fixed 2026-09-26
        # after the real run raised KeyError on the 2 of 91 unparsed pairs; reported as `missing`).
        cf = [stat[k] for a, b in combinations(f, 2) if a != b and (k := tuple(sorted((a, b)))) in stat]
        wm = [stat[k] for a, b in combinations(m, 2) if a != b and (k := tuple(sorted((a, b)))) in stat]
        if cf and wm:
            out.append(float(np.mean(cf) - np.mean(wm)))
    return out


def all_proposals_chao(runs: dict[str, list[str]], pair_dec: dict, names: list[str]) -> dict:
    """Descriptive: Chao2 over every proposal of a pool, clusters = components of strict links."""
    items = [(n, i) for n in names for i in range(len(runs[n]))]
    parent = {x: x for x in items}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for (a, b), d in pair_dec.items():
        if a in names and b in names:
            for i, j in zip(*np.nonzero(d == 2)):
                ra, rb = find((a, int(i))), find((b, int(j)))
                if ra != rb:
                    parent[ra] = rb
    comp: dict = {}
    for x in items:
        comp.setdefault(find(x), []).append(x)
    ids = {root: k for k, root in enumerate(comp)}
    lists = [{ids[find((n, i))] for i in range(len(runs[n]))} for n in names]
    est = chao2(lists)
    flagged = [len(v) for v in comp.values()
               if len(v) > 6 or max(Counter(n for n, _ in v).values()) > 2]
    return {"clusters": len(comp), "chao2": float(est), "completeness": len(comp) / est if est else None,
            "flagged_component_sizes": flagged}


def mean_kappa(inc: np.ndarray) -> float:
    ks = [kappa(inc[:, a], inc[:, b]) for a, b in combinations(range(inc.shape[1]), 2)]
    ks = [k for k in ks if not math.isnan(k)]
    return float(np.mean(ks)) if ks else float("nan")


def band_verdict(iv: list[float] | None, point: float, strings: tuple[str, str, str]) -> str:
    if iv is None:
        return "NOT ESTIMABLE (the pool recovers no reference item)"
    lo, hi = iv
    cal, over, under = strings
    if lo >= -BAND and hi <= BAND:
        return cal
    if lo > BAND:
        return over
    if hi < -BAND:
        return under
    side = "over" if point > BAND else "under" if point < -BAND else "inside the band"
    return f"MATCHING-LIMITED (point estimate {point:+.3f}, {side})"


def rates_posterior(conf) -> tuple[tuple[float, float], tuple[float, float]]:
    """Beta parameters for the strict miss rate P(not judged SAME | SAME) and the false-merge rate
    P(judged SAME | not SAME), from a label-rows x matcher-cols confusion, uniform prior."""
    c = np.array(conf, float)
    s_hit, s_all = c[2, 2], c[2].sum()
    n_s, n_all = c[0, 2] + c[1, 2], c[0].sum() + c[1].sum()
    return (1 + s_all - s_hit, 1 + s_hit), (1 + n_s, 1 + n_all - n_s)


def perturb(d: np.ndarray, miss: float, fm: float, rng: np.random.Generator) -> np.ndarray:
    """Re-apply matching error to a judged decision matrix: SAME links dropped at the miss rate,
    other pairs merged at the false-merge rate. Returns strict decisions (2 = SAME, 0 = not)."""
    same = d == 2
    keep = same & (rng.random(d.shape) >= miss)
    add = ~same & (rng.random(d.shape) < fm)
    return np.where(keep | add, 2, 0)


def basic_interval(point: float, draws: list[float]) -> list[float] | None:
    """Basic (reflected) bootstrap interval: the shift that matching error adds on re-application is
    taken as the shift it added to the truth, so the interval for the truth is point - (draw - point)."""
    if not draws or point != point:
        return None
    return [float(2 * point - np.percentile(draws, 97.5)), float(2 * point - np.percentile(draws, 2.5))]


def propagate(conf, ref_dec, pools: dict[str, list[str]], pair_dec: dict, fam: list[str],
              mm: list[str], rng: np.random.Generator, draws: int = DRAWS) -> dict:
    """Matching-error intervals for every pool's Chao2 error, the k = 8 comparison and the Sorensen
    difference (forward re-application of the calibrated rates, basic interval)."""
    (ma, mb), (fa, fb) = rates_posterior(conf)
    k8 = min(8, len(fam))
    point = {p: chao_error(incidence(ref_dec, names))["error"] for p, names in pools.items()}
    comp_point = (float(np.mean(subset_errors(incidence(ref_dec, mm), k8))
                        - np.mean(subset_errors(incidence(ref_dec, fam), k8)))
                  if len(mm) >= k8 and k8 >= 3 else None)
    sor_point = (mean_pair({k: sorensen(d) for k, d in pair_dec.items()}, fam)
                 - mean_pair({k: sorensen(d) for k, d in pair_dec.items()}, mm)) if pair_dec else None
    errs = {p: [] for p in pools}
    comp, sor_d = [], []
    for _ in range(draws):
        miss, fm = rng.beta(ma, mb), rng.beta(fa, fb)
        rd = {n: perturb(d, miss, fm, rng) for n, d in ref_dec.items()}
        for p, names in pools.items():
            errs[p].append(chao_error(incidence(rd, names))["error"])
        if comp_point is not None:
            comp.append(float(np.mean(subset_errors(incidence(rd, mm), k8))
                              - np.mean(subset_errors(incidence(rd, fam), k8))))
        if pair_dec:
            st = {k: sorensen(perturb(d, miss, fm, rng)) for k, d in pair_dec.items()}
            sor_d.append(mean_pair(st, fam) - mean_pair(st, mm))
    return {"draws": draws, "method": "forward re-application of calibrated miss / false-merge rates, "
                                      "basic interval",
            "error_interval": {p: basic_interval(point[p], v) for p, v in errs.items()},
            "forward_shift": {p: float(np.mean(v) - point[p]) for p, v in errs.items()},
            "k8_difference_point": comp_point,
            "k8_difference_interval": basic_interval(comp_point, comp) if comp_point is not None else None,
            "sorensen_difference_interval": basic_interval(sor_point, sor_d) if sor_point is not None else None,
            "rate_posteriors": {"miss_beta": [ma, mb], "false_merge_beta": [fa, fb]}}


def analyse(runs: dict[str, list[str]], ref_dec: dict[str, np.ndarray], pair_dec: dict,
            conf, fam: list[str], mm: list[str], ref: list[str], floor_cleared: bool | None,
            covers: bool | None, rng: np.random.Generator, draws: int = DRAWS) -> dict:
    """Everything V1-V4 need, from decision matrices. Shared by phase 2 and the synthetic S4 check."""
    inc_f, inc_m = incidence(ref_dec, fam), incidence(ref_dec, mm)
    res: dict = {"families": fam, "m_runs": mm}
    res["recall_strict"] = {n: int(incidence(ref_dec, [n]).sum()) for n in ref_dec}
    res["recall_lenient"] = {n: int(incidence(ref_dec, [n], strict=False).sum()) for n in ref_dec}
    res["named_by_no_family"] = [ref[g] for g in range(len(ref)) if not inc_f[g].any()]
    u_m = [g for g in range(len(ref)) if not inc_m[g].any()]
    res["named_by_no_m_run"] = [ref[g] for g in u_m]
    res["family_incidence"] = {ref[g]: int(inc_f[g].sum()) for g in range(len(ref))}
    res["m_incidence"] = {ref[g]: int(inc_m[g].sum()) for g in range(len(ref))}
    res["chao2"] = {"cross_family": chao_error(inc_f), "m_runs": chao_error(inc_m)}
    res["subsets"] = {
        "cross_family": {k: float(np.mean(subset_errors(inc_f, k))) for k in range(3, min(8, len(fam)) + 1)},
        "m_runs": {k: float(np.mean(subset_errors(inc_m, k))) for k in range(3, min(8, len(mm)) + 1)}}
    res["node_kappa_reference"] = {"cross_family": mean_kappa(inc_f), "m_runs": mean_kappa(inc_m)}
    res["all_proposals_chao2_descriptive"] = {"cross_family": all_proposals_chao(runs, pair_dec, fam),
                                              "m_runs": all_proposals_chao(runs, pair_dec, mm)}
    sor = {k: sorensen(d) for k, d in pair_dec.items()}
    res["sorensen"] = {"cross_family": mean_pair(sor, fam), "m_runs": mean_pair(sor, mm),
                       "per_pair": {"|".join(k): v for k, v in sor.items()}}
    reps = [k for k in sor if k[0].split("#")[0] == k[1].split("#")[0] and "#2" in "".join(k)]
    res["sorensen"]["same_footing_repeats"] = {"|".join(k): sor[k] for k in reps}
    bridge = [sor[k] for k in sor if ("google" in k or "google#2" in k) and any(x.startswith("M") for x in k)]
    res["sorensen"]["google_x_m_bridge_mean"] = float(np.mean(bridge)) if bridge else None
    pools = {"cross_family": fam, "m_runs": mm}
    prop = propagate(conf, ref_dec, pools, {k: v for k, v in pair_dec.items()
                                            if (k[0] in fam and k[1] in fam) or (k[0] in mm and k[1] in mm)},
                     fam, mm, rng, draws)
    res["propagation"] = prop
    boots = list_bootstrap(sor, fam, mm, rng)
    lo_d, hi_d = (np.percentile(boots, [2.5, 97.5]).tolist() if boots else [float("nan")] * 2)
    res["sorensen"]["difference"] = res["sorensen"]["cross_family"] - res["sorensen"]["m_runs"]
    res["sorensen"]["difference_list_bootstrap_ci"] = [lo_d, hi_d]

    suffix = "" if floor_cleared in (True, None) else " (BELOW DETECTION FLOOR)"
    v1 = band_verdict(prop["error_interval"]["cross_family"], res["chao2"]["cross_family"]["error"],
                      ("CROSS-FAMILY POOL CALIBRATED", "CROSS-FAMILY POOL STILL OVER-CERTIFIES",
                       "CROSS-FAMILY POOL UNDER-CERTIFIES")) + suffix
    v1m = band_verdict(prop["error_interval"]["m_runs"], res["chao2"]["m_runs"]["error"],
                       ("SAME-MODEL RUNS CALIBRATED", "SAME-MODEL RUNS STILL OVER-CERTIFY",
                        "SAME-MODEL RUNS UNDER-CERTIFY")) + suffix
    ci = prop["k8_difference_interval"]
    v2 = ("PREDICTION CONFIRMED" if ci and ci[0] > 0 else "PREDICTION REFUTED" if ci and ci[1] < 0
          else "INCONCLUSIVE")
    k8 = min(8, len(fam))
    f8, m8 = res["subsets"]["cross_family"].get(k8), res["subsets"]["m_runs"].get(k8)
    if v2 == "PREDICTION CONFIRMED" and f8 is not None and abs(f8) >= abs(m8):
        v2 = "CONFIRMED IN DIRECTION, NOT CLOSER"
    v3 = ("CROSS-FAMILY MORE DIVERSE" if hi_d < 0 else "CROSS-FAMILY LESS DIVERSE" if lo_d > 0
          else "NO FAMILY EFFECT DETECTED")
    mvals = [sor[tuple(sorted(p))] for p in combinations(mm, 2) if tuple(sorted(p)) in sor]
    rep_vals = list(res["sorensen"]["same_footing_repeats"].values())
    if mvals and rep_vals and not (min(mvals) <= float(np.mean(rep_vals)) <= max(mvals)):
        v3 += " (FOOTING CONFOUNDED)"
    fam_named = inc_f.any(axis=1)
    if not u_m:
        v4 = "NO SAME-MODEL BLIND SPOT UNDER THIS MATCHER"
    else:
        got = sum(bool(fam_named[g]) for g in u_m)
        v4 = ("CROSS-FAMILY RECOVERS WHAT ONE MODEL MISSES" if got == len(u_m)
              else "PARTIAL RECOVERY" if got else "SHARED BLIND SPOT")
    res["items_8_and_11"] = {ref[g]: {"families": int(inc_f[g].sum()), "m_runs": int(inc_m[g].sum())}
                             for g in (7, 10)}
    res["verdicts"] = {"V1_cross_family": v1, "V1_m_runs": v1m, "V2_comparison_k8": v2,
                       "V3_independence": v3, "V4_blind_spots": v4,
                       "interval_note": None if covers in (True, None) else
                       "matching interval under-covers in synthetic check"}
    return res


# ---------------------------------------------------------------- phase 2

def match_all(judge: str, provider, runs: dict[str, list[str]], fam: list[str], mm: list[str],
              ref: list[str]) -> tuple[dict, dict, dict]:
    ref_dec, pair_dec, extra = {}, {}, {"missing": [], "inconsistent": 0, "splits_lumps": {}}
    for n in list(runs):
        r = judge_pair(judge, f"ref-{n}", runs[n], ref, provider=provider)
        if r is None:
            extra["missing"].append(f"ref-{n}")
            continue
        ref_dec[n] = r["dec"]
        extra["inconsistent"] += r["inconsistent"]
    pairs = list(combinations(fam, 2)) + list(combinations(mm, 2))
    pairs += [(f, f"{f}#2") for f in REPEAT_FAMILIES if f"{f}#2" in runs and f in runs]
    pairs += [(g, m) for g in ("google", "google#2") if g in runs for m in mm]
    for a, b in pairs:
        key = tuple(sorted((a, b)))
        r = judge_pair(judge, f"pair-{key[0]}-{key[1]}", runs[key[0]], runs[key[1]], provider=provider)
        if r is None:
            extra["missing"].append("|".join(key))
            continue
        pair_dec[key] = r["dec"]
        extra["inconsistent"] += r["inconsistent"]
        extra["splits_lumps"]["|".join(key)] = splits_lumps(r)
    return ref_dec, pair_dec, extra


def embedding_decisions(cal: dict, runs: dict[str, list[str]], fam, mm, ref) -> tuple[dict, dict]:
    names = list(runs)
    texts = [t for n in names for t in runs[n]] + ref
    V, _ = embed_texts(cal["model"], texts, provider=cal["provider"] or True)
    if V is None:
        return {}, {}
    idx, s = {}, 0
    for n in names:
        idx[n] = (s, s + len(runs[n]))
        s += len(runs[n])
    R = V[s:]
    cls = lambda c: emb_classes(c, cal["tau_same"], cal["tau_linked"])  # noqa: E731
    ref_dec = {n: cls(cosines(V[idx[n][0]:idx[n][1]], R)) for n in names}
    pair_dec = {}
    for a, b in list(combinations(fam, 2)) + list(combinations(mm, 2)) + \
            [(f, f"{f}#2") for f in REPEAT_FAMILIES if f"{f}#2" in runs]:
        k = tuple(sorted((a, b)))
        pair_dec[k] = cls(cosines(V[idx[k[0]][0]:idx[k[0]][1]], V[idx[k[1]][0]:idx[k[1]][1]]))
    return ref_dec, pair_dec


def run_phase2(analyse_only: bool = False) -> None:
    llm.load_key(quiet=True)
    start = None if analyse_only else llm.key_status()
    ref = reference()
    synth = json.loads(SYNTH.read_text()) if SYNTH.exists() else {}
    floor, covers = synth.get("S1", {}).get("floor_cleared"), synth.get("S2", {}).get("covers")
    calpath = OUT / "cross-family-calibration.json"
    if analyse_only:
        cal = json.loads(calpath.read_text())
    else:
        print("1. calibrate the matchers on the labelled CTA pairs")
        cal = {"judge": choose_judge()}
        emb = None
        for m in EMBEDDERS:
            emb = calibrate_embedder(m)
            if "error" not in emb:
                break
        cal["embedding"] = emb
        OUT.mkdir(exist_ok=True)
        calpath.write_text(json.dumps(cal, indent=1, ensure_ascii=False) + "\n")
        print("2. proposals")
        propose_all()
    recs = load_runs()
    fam = [f for f in list(FAMILIES) + list(RESERVE) if f in recs]
    mm = list(m_runs())
    runs = {n: recs[n]["items"] for n in recs} | m_runs()
    out: dict = {"roster": {n: {k: recs[n].get(k) for k in ("requested_slug", "served_model", "provider",
                                                             "timestamp_utc", "request")} for n in recs},
                 "calibration": cal, "gates": {}}
    if len(fam) < MIN_FAMILIES:
        out["gates"]["pool"] = "POOL TOO SMALL"
    chosen = cal["judge"]["chosen"]
    rng = np.random.default_rng(SEED)
    if chosen is None:
        out["gates"]["matcher"] = "MATCHER NOT CALIBRATED"
    else:
        jpath = OUT / "cross-family-decisions.json"
        if analyse_only:
            dd = json.loads(jpath.read_text())
            ref_dec = {k: np.array(v) for k, v in dd["ref"].items()}
            pair_dec = {tuple(k.split("|")): np.array(v) for k, v in dd["pairs"].items()}
            extra = dd["extra"]
        else:
            print("3. judged matching")
            ref_dec, pair_dec, extra = match_all(chosen["judge"], chosen["provider"] or True, runs, fam, mm, ref)
            jpath.write_text(json.dumps({"ref": {k: v.tolist() for k, v in ref_dec.items()},
                                         "pairs": {"|".join(k): v.tolist() for k, v in pair_dec.items()},
                                         "extra": extra}) + "\n")
        fam_ok = [f for f in fam if f in ref_dec]
        mm_ok = [m for m in mm if m in ref_dec]
        out["judged"] = analyse(runs, ref_dec, pair_dec, chosen["rates"]["confusion_label_rows_matcher_cols_DOS"],
                                fam_ok, mm_ok, ref, floor, covers, rng)
        out["judged"]["matching_extra"] = extra
    emb = cal.get("embedding")
    if emb and "tau_same" in emb:
        epath = OUT / "cross-family-embedding-decisions.json"
        if analyse_only:
            dd = json.loads(epath.read_text())
            ref_e = {k: np.array(v) for k, v in dd["ref"].items()}
            pair_e = {tuple(k.split("|")): np.array(v) for k, v in dd["pairs"].items()}
        else:
            ref_e, pair_e = embedding_decisions(emb, runs, fam, mm, ref)
            epath.write_text(json.dumps({"ref": {k: v.tolist() for k, v in ref_e.items()},
                                         "pairs": {"|".join(k): v.tolist() for k, v in pair_e.items()}}) + "\n")
        if ref_e:
            out["embedding"] = analyse(runs, ref_e, pair_e, emb["held_out_rates"]
                                       ["confusion_label_rows_matcher_cols_DOS"], fam, mm, ref,
                                       floor, covers, rng)
            out["embedding"]["passes_calibration"] = emb["passes"]
            if "judged" in out and emb["passes"]:
                same = (out["judged"]["verdicts"]["V1_cross_family"].split(" (")[0]
                        == out["embedding"]["verdicts"]["V1_cross_family"].split(" (")[0])
                out["V5"] = "MATCHERS AGREE" if same else "MATCHERS DISAGREE"
    for g in ("pool", "matcher"):
        if g in out["gates"]:
            for arm in ("judged", "embedding"):
                if arm in out:
                    out[arm]["verdicts"] = {k: f"{out['gates'][g]} (descriptive: {v})"
                                            for k, v in out[arm]["verdicts"].items() if v}
    end = None if analyse_only else llm.key_status()
    out["spend"] = {"study_ledger_usd": spent(), "key_usage_run_start": (start or {}).get("usage"),
                    "key_usage_run_end": (end or {}).get("usage"), "key_usage_phase1_start": KEY_USAGE_AT_START}
    RESULT.write_text(json.dumps(out, indent=1, ensure_ascii=False, default=float) + "\n")
    print(json.dumps({k: out[k] for k in ("gates", "spend")}, indent=1))
    for arm in ("judged", "embedding"):
        if arm in out:
            print(arm, json.dumps(out[arm]["verdicts"], indent=1))
    print(f"wrote {RESULT}")


# ---------------------------------------------------------------- synthetic (no model call)

def world(kind: str, k: int, rng: random.Random) -> list[set[int]]:
    n = 11
    if kind == "INDEPENDENT":
        p = [rng.uniform(0.25, 1.0) for _ in range(n)]
    elif kind == "BLIND SPOT":
        p = [0.0, 0.0] + [rng.uniform(0.35, 1.0) for _ in range(n - 2)]
    else:                                   # CORRELATED: completeness.propose's shared latent, 7 of 11
        o = [rng.random() for _ in range(n)]
        out = []
        for _ in range(k):
            b = [0.85 * oi + 0.15 * rng.random() for oi in o]
            cut = sorted(b)[n - 7]
            out.append({i for i in range(n) if b[i] >= cut})
        return out
    return [{i for i in range(n) if rng.random() < p[i]} for _ in range(k)]


def to_inc(lists: list[set[int]]) -> np.ndarray:
    inc = np.zeros((11, len(lists)), bool)
    for j, s in enumerate(lists):
        for i in s:
            inc[i, j] = True
    return inc


def s1(rng: random.Random, worlds: int = 2000) -> dict:
    out = {}
    for kind in ("INDEPENDENT", "CORRELATED", "BLIND SPOT"):
        for k in (8, 10):
            errs, ks = [], []
            for _ in range(worlds):
                inc = to_inc(world(kind, k, rng))
                errs.append(chao_error(inc)["error"])
                ks.append(mean_kappa(inc))
            e = np.array(errs)
            out[f"{kind}|k={k}"] = {"mean_error": float(e.mean()), "sd": float(e.std()),
                                    "share_within_band": float(np.mean(np.abs(e) <= BAND)),
                                    "share_over": float(np.mean(e > BAND)),
                                    "share_under": float(np.mean(e < -BAND)),
                                    "mean_node_kappa": float(np.nanmean(ks))}
    out["floor_cleared"] = bool(out["INDEPENDENT|k=8"]["share_within_band"] >= 0.80
                                and out["CORRELATED|k=8"]["share_over"] >= 0.80)
    return out


#: planted judges, rows = label (not SAME, not SAME, SAME), cols = judged (D, O, S)
PLANTS = {
    "NOISY": np.array([[0.978, 0.02, 0.002], [0.978, 0.02, 0.002], [0.05, 0.25, 0.70]]),
    "GOOD": np.array([[0.9895, 0.01, 0.0005], [0.9895, 0.01, 0.0005], [0.02, 0.08, 0.90]]),
}


def planted_ref_dec(lists: list[set[int]], plant: np.ndarray, rng: np.random.Generator,
                    filler: int = 15):
    truth, judged = {}, {}
    for j, s in enumerate(lists):
        items = sorted(s)
        t = np.zeros((len(items) + filler, 11), int)
        for r, g in enumerate(items):
            t[r, g] = 2
        jd = np.where(t == 2, rng.choice(3, size=t.shape, p=plant[2]), rng.choice(3, size=t.shape, p=plant[0]))
        truth[f"L{j}"], judged[f"L{j}"] = t, jd
    return truth, judged


def s2(rng_py: random.Random, rng: np.random.Generator, worlds: int = 150, draws: int = 300) -> dict:
    out = {}
    for pname, plant in PLANTS.items():
        for kind in ("INDEPENDENT", "CORRELATED", "BLIND SPOT"):
            for k in (8, 10):
                hits, bias, widths, inside, above = 0, [], [], 0, 0
                for _ in range(worlds):
                    lists = world(kind, k, rng_py)
                    truth, judged = planted_ref_dec(lists, plant, rng)
                    names = list(truth)
                    true_err = chao_error(incidence(truth, names))["error"]
                    cs = rng.multinomial(30, plant[2])
                    cn = rng.multinomial(2781, plant[0])
                    conf = [[int(x) for x in cn], [0, 0, 0], [int(x) for x in cs]]
                    pr = propagate(conf, judged, {"pool": names}, {}, names, [], rng, draws)
                    lo, hi = pr["error_interval"]["pool"]
                    hits += lo <= true_err <= hi
                    widths.append(hi - lo)
                    inside += lo >= -BAND and hi <= BAND
                    above += lo > BAND
                    bias.append(chao_error(incidence(judged, names))["error"] - true_err)
                out[f"{pname}|{kind}|k={k}"] = {
                    "coverage": hits / worlds, "mean_width": float(np.mean(widths)),
                    "share_interval_inside_band": inside / worlds, "share_interval_above_band": above / worlds,
                    "point_minus_truth_mean": float(np.mean(bias))}
    out["covers"] = bool(all(v["coverage"] >= 0.80 for v in out.values()))
    return out


def s3(rng: np.random.Generator, worlds: int = 150, boots: int = 400) -> dict:
    U, L, sigma = 120, 25, 1.6

    def draw(w):
        p = w / w.sum()
        return set(rng.choice(U, L, replace=False, p=p).tolist())

    out = {}
    for rho in (1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.3):
        diffs, power = [], 0
        for _ in range(worlds):
            z = rng.normal(size=U)
            mm = [draw(np.exp(sigma * z)) for _ in range(8)]
            fam = [draw(np.exp(sigma * (rho * z + math.sqrt(1 - rho ** 2) * rng.normal(size=U))))
                   for _ in range(10)]
            lists = {f"F{i}": s for i, s in enumerate(fam)} | {f"M{i}": s for i, s in enumerate(mm)}
            st = {}
            for a, b in combinations(lists, 2):
                A, B = lists[a], lists[b]
                st[tuple(sorted((a, b)))] = 2 * len(A & B) / (len(A) + len(B))
            fn, mn = [f"F{i}" for i in range(10)], [f"M{i}" for i in range(8)]
            d = mean_pair(st, fn) - mean_pair(st, mn)
            diffs.append(d)
            bs = list_bootstrap(st, fn, mn, rng, boots)
            power += np.percentile(bs, 97.5) < 0
        out[f"rho={rho}"] = {"mean_planted_difference": float(np.mean(diffs)), "power": power / worlds}
    ok = [v["mean_planted_difference"] for v in out.values() if v["power"] >= 0.80]
    out["mde_abs_difference"] = float(min(abs(x) for x in ok)) if ok else None
    return out


def s4() -> dict:
    """Oracle judge on synthetic lists through the real prompt, shuffling and parsing code."""
    rng = random.Random(4)
    caps = [f"capability {c:02d}" for c in range(40)]
    ref = [f"{caps[c]} in reference wording" for c in range(11)]

    def make(tag, ids):
        return [f"{caps[c]} as phrased by {tag}" for c in ids]

    truth_ids = {f"F{i}": rng.sample(range(40), 14) for i in range(10)} | \
                {f"M{i}": rng.sample(range(25), 14) for i in range(8)}
    runs = {n: make(n, ids) for n, ids in truth_ids.items()}
    cap_of = {t: int(re.search(r"capability (\d+)", t).group(1)) for n in runs for t in runs[n]}
    cap_of |= {t: int(re.search(r"capability (\d+)", t).group(1)) for t in ref}

    def oracle(prompt: str) -> str:
        x = re.findall(r"^X(\d+)\. (.*)$", prompt, re.M)
        y = re.findall(r"^Y(\d+)\. (.*)$", prompt, re.M)
        links = [{"x": int(i), "y": int(j), "relation": "SAME", "x_covers_y": True, "y_covers_x": True}
                 for i, s in x for j, t in y if cap_of[s] == cap_of[t]]
        return "Here you go:\n" + json.dumps({"links": links})

    fam, mm = [f"F{i}" for i in range(10)], [f"M{i}" for i in range(8)]
    ref_dec = {n: judge_pair("oracle", f"ref-{n}", runs[n], ref, caller=oracle)["dec"] for n in runs}
    pair_dec = {tuple(sorted(k)): judge_pair("oracle", "p" + "".join(k), runs[k[0]], runs[k[1]],
                                             caller=oracle)["dec"]
                for k in list(combinations(fam, 2)) + list(combinations(mm, 2))}
    for n, ids in truth_ids.items():
        want = np.zeros((len(ids), 11), int)
        for r, c in enumerate(ids):
            if c < 11:
                want[r, c] = 2
        assert (ref_dec[n] == want).all(), f"reference decisions for {n} not recovered"
    for (a, b), d in pair_dec.items():
        want = np.array([[2 if x == y else 0 for y in truth_ids[b]] for x in truth_ids[a]])
        assert (d == want).all(), f"pair decisions {a}-{b} not recovered"
    inc_true = to_inc([{c for c in truth_ids[n] if c < 11} for n in fam])
    assert chao_error(incidence(ref_dec, fam)) == chao_error(inc_true)
    s_true = np.mean([2 * len(set(truth_ids[a]) & set(truth_ids[b])) / 28 for a, b in combinations(fam, 2)])
    s_got = mean_pair({k: sorensen(v) for k, v in pair_dec.items()}, fam)
    assert abs(s_true - s_got) < 1e-12, (s_true, s_got)
    conf = [[2781, 0, 0], [0, 0, 0], [0, 0, 30]]            # a perfect matcher
    res = analyse(runs, ref_dec, pair_dec, conf, fam, mm, ref, True, True, np.random.default_rng(0), 50)
    assert res["propagation"]["error_interval"]["cross_family"] is not None
    # a swapped-side presentation must also map back; check one pair both ways
    d1 = judge_pair("oracle", "swapcheck-1", runs["F0"], runs["F1"], caller=oracle)["dec"]
    d2 = judge_pair("oracle", "swapcheck-2", runs["F1"], runs["F0"], caller=oracle)["dec"]
    assert (d1 == d2.T).all()
    return {"recovered_exactly": True, "sorensen_planted": float(s_true),
            "chao2_error_planted": chao_error(inc_true)["error"], "verdicts_on_oracle_world": res["verdicts"]}


def synthetic() -> None:
    rng_py, rng = random.Random(SEED), np.random.default_rng(SEED)
    out = {"S4": s4()}
    print("S4 end-to-end with an oracle judge: recovered exactly")
    out["S1"] = s1(rng_py)
    for k, v in out["S1"].items():
        if k != "floor_cleared":
            print(f"S1 {k:<20} error {v['mean_error']:+.3f} (sd {v['sd']:.3f})  band {v['share_within_band']:.2f}"
                  f"  over {v['share_over']:.2f}  under {v['share_under']:.2f}  kappa {v['mean_node_kappa']:.2f}")
    print(f"S1 floor cleared: {out['S1']['floor_cleared']}")
    out["S2"] = s2(rng_py, rng)
    for k, v in out["S2"].items():
        if k != "covers":
            print(f"S2 {k:<26} coverage {v['coverage']:.2f}  width {v['mean_width']:.2f}  inside band "
                  f"{v['share_interval_inside_band']:.2f}  above {v['share_interval_above_band']:.2f}  "
                  f"point - truth {v['point_minus_truth_mean']:+.3f}")
    print(f"S2 propagation covers: {out['S2']['covers']}")
    out["S3"] = s3(rng)
    for k, v in out["S3"].items():
        if k != "mde_abs_difference":
            print(f"S3 {k:<8} planted d {v['mean_planted_difference']:+.3f}  power {v['power']:.2f}")
    print(f"S3 MDE |d|: {out['S3']['mde_abs_difference']}")
    OUT.mkdir(exist_ok=True)
    SYNTH.write_text(json.dumps(out, indent=1, default=float) + "\n")
    print(f"wrote {SYNTH}")


# ---------------------------------------------------------------- dry run

def estimate(listing: dict) -> dict:
    prompt = frozen_prompt()
    ref = reference()
    mlen = int(np.mean([len(t) for v in m_runs().values() for t in v]))
    list_chars = 25 * (mlen + 6)
    rub = len(judge_prompt([], []))
    cta = cta_lists()
    rows = []

    def add(what, model, n, in_chars, out_exp, out_max):
        pin, pout = PRICES[model]
        rows.append({"what": what, "model": model, "calls": n,
                     "expected_usd": n * (in_chars / 4 * pin + out_exp * pout) / 1e6,
                     "worst_usd": n * (in_chars / 4 * pin + out_max * pout) / 1e6})

    for fam, slugs in FAMILIES.items():
        reasoning = "reasoning" in listing.get(slugs[0], {}).get("supported_parameters", [])
        n = 2 if fam in REPEAT_FAMILIES else 1
        add(f"propose {fam}", slugs[0], n, len(prompt), 800 + (5000 if reasoning else 0), PROPOSE_MAX_TOKENS)
    j = JUDGES[0]
    cal_chars = rub + sum(len(t) + 6 for r in "ABC" for t in cta[r]) * 2 // 3
    add("calibrate judge (6 calls)", j, 6, cal_chars, 1500 + 8000, JUDGE_MAX_TOKENS)
    add("anchor to reference (20)", j, 20, rub + list_chars + sum(len(t) for t in ref), 600 + 6000,
        JUDGE_MAX_TOKENS)
    add("list pairs (45+28+2+16)", j, 91, rub + 2 * list_chars, 800 + 8000, JUDGE_MAX_TOKENS)
    add("fallback judge calibration, if needed (6)", JUDGES[1], 6, cal_chars, 1500 + 8000, JUDGE_MAX_TOKENS)
    add("embeddings (<= 6 calls)", "google/gemini-embedding-2", 6, 600 * 90 // 6, 0, 0)
    add("retry allowance (2 proposals at 32k)", "openai/gpt-6-sol", 2, len(prompt), 8000, RETRY_MAX_TOKENS)
    return {"rows": rows, "expected_total_usd": sum(r["expected_usd"] for r in rows),
            "worst_total_usd": sum(r["worst_usd"] for r in rows),
            "assumptions": "chars/4 tokens; proposal output 800 visible + 5,000 reasoning tokens for "
                           "reasoning-capable slugs; judge 8,000 reasoning tokens per call; worst = every "
                           "call spends its full max_tokens"}


def dry_run() -> None:
    print("frozen prompt sha256 ok; rubric sha256 ok")
    frozen_prompt()
    ref, mm = reference(), m_runs()
    print(f"M runs: {', '.join(f'{k}:{len(v)}' for k, v in mm.items())} items; reference {len(ref)}")
    labels, disputed = cta_labels()
    print(f"calibration pairs {len(labels)} ({Counter(NAMES[v] for v in labels.values())}); "
          f"re-judge disputed {len(disputed)}")
    listing = {m["id"]: m for m in json.load(urllib.request.urlopen(
        "https://openrouter.ai/api/v1/models", timeout=60))["data"]}
    emb_listing = {m["id"]: m for m in json.load(urllib.request.urlopen(
        "https://openrouter.ai/api/v1/embeddings/models", timeout=60))["data"]}
    flags = []
    for s, (pin, pout) in PRICES.items():
        m = listing.get(s) or emb_listing.get(s)
        if m is None:
            flags.append(f"{s}: NOT LISTED")
            continue
        lp = (float(m["pricing"]["prompt"]) * 1e6, float(m["pricing"].get("completion", 0)) * 1e6)
        if abs(lp[0] - pin) > 0.01 * pin + 1e-9 or abs(lp[1] - pout) > 0.01 * pout + 1e-9:
            flags.append(f"{s}: price now {lp[0]:.3f}/{lp[1]:.3f}")
        if m.get("expiration_date"):
            flags.append(f"{s}: expires {m['expiration_date']}")
    print("listing check:", "; ".join(flags) if flags else "every slug listed at the registered price")
    est = estimate(listing)
    for r in est["rows"]:
        print(f"   {r['what']:<44} {r['model']:<36} ${r['expected_usd']:.3f}  (worst ${r['worst_usd']:.3f})")
    print(f"   expected ${est['expected_total_usd']:.2f}, worst ${est['worst_total_usd']:.2f}, cap ${BUDGET_USD:.0f}")
    jp = judge_prompt(mm["M1"][:3], ref[:2])
    print("judge prompt sample (M1[:3] vs reference[:2]):\n" + textwrap.indent(jp, "   | "))

    llm.load_key(quiet=True)
    before = llm.key_status()
    probes = []
    meta: dict = {}
    txt = llm.call(JUDGES[0], "Reply with the single word: ok", SEED, max_tokens=400, temperature=0.0,
                   attempts=2, provider=False, meta=meta)
    charge(JUDGES[0], meta, "dry-run probe")
    probes.append({"kind": "chat", "text": txt.strip()[:40], **{k: meta.get(k) for k in (
        "requested_model", "served_model", "provider", "generation_id", "timestamp_utc", "request",
        "finish_reason", "usage", "last_error")}})
    emeta: dict = {}
    vec = llm.embed(EMBEDDERS[0], ["Subtract whole numbers of any size", "Regroup a ten as ten ones"],
                    provider=False, meta=emeta)
    charge(EMBEDDERS[0], emeta, "dry-run probe")
    probes.append({"kind": "embedding", "dims": len(vec[0]) if vec else None,
                   **{k: emeta.get(k) for k in ("requested_model", "served_model", "provider",
                                                "timestamp_utc", "usage", "last_error")}})
    after = llm.key_status()
    for p in probes:
        print("probe:", json.dumps(p))
    OUT.mkdir(exist_ok=True)
    DRY.write_text(json.dumps({"probes": probes, "key_usage_before": (before or {}).get("usage"),
                               "key_usage_after": (after or {}).get("usage"),
                               "study_ledger_usd": spent(), "listing_flags": flags,
                               "estimate": est}, indent=1) + "\n")
    print(f"key usage {(before or {}).get('usage')} -> {(after or {}).get('usage')}; "
          f"study ledger ${spent():.6f}; wrote {DRY}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", choices=["run", "analyse"])
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.synthetic:
        synthetic()
    elif a.dry_run:
        dry_run()
    elif a.cmd in ("run", "analyse"):
        run_phase2(analyse_only=a.cmd == "analyse")
    else:
        ap.print_help()
