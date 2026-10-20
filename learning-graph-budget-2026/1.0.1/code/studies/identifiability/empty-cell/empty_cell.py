"""PRE-REGISTERED: what empties the identifying cell in each corpus, measured from its records?

QUESTION
    Paper II's first headline sorts corpora by how their order is set ("the platform sets the order"
    against "learners meet skills in varying orders") and reads Table 1 through that split. The label
    comes from each platform's documentation, and the scope audit of 2026-10-13 (F1) showed the
    records do not follow it: EDM Cup and Eedi are both teacher-assigned and decide 0.015% and 25.36%
    of their pairs; Junyi ds1275 is learner-chosen (92% of topic pairs met in both directions,
    studies/identifiability/junyi/) and decides none. This study replaces the documented label with
    measured ones.

THE DECOMPOSITION (an identity, not a model)
    For an ordered pair (a, b), the atlas's identifying cell is the learners who attempted a before
    their first attempt at b and had not passed a by then (positivity.classify, cell "failed"). Among
    the learners who attempted both a and b at some time, write
        N   the number of them                                  (coverage)
        O   the share whose first attempt at a came strictly before their first attempt at b   (order)
        F   among those, the share who had not passed a when they reached b                 (pass-through)
    Then  identifying cell = N x O x F  exactly. The cell is empty when too few learners meet both
    skills, when almost nobody meets a first, or when almost everyone who meets a first passes it
    before b (mastery gating, or an easy a). The documented label speaks only to the second.

DATA (reads corpora): exactly the corpora and pair samples of Table 1, read through the atlas's own
    readers so the pairs are the atlas's pairs: overlap/atlas.py audit() inputs (READERS, discover(),
    corpus_rng; max 20,000 ordered pairs per corpus) for EDM Cup, EdNet KT1, XES3G5M, Eedi and the
    DataShop exports; overlap/positivity.py's ASSISTments 2012-13 loader with the 40,000-pair sample
    of out/positivity-assist.json; overlap/slam_atlas.py's three SLAM courses at the construct grain.
    Same MIN_CELL (5), same first-touch and first-pass definitions (positivity.states). Licences and
    locations: data/data-sources.json. Only the aggregates below are committed.

WHAT THE ANALYST HAS SEEN (written 2026-10-13, before this script reads any corpus): Table 1 and
    every field of atlas.json, positivity-assist.json and atlas-slam.json (median identifying cell,
    readable and decided shares, drops); the Junyi order figure above; random_order.json on
    ASSISTments. No N, O or F has been computed for any corpus. The analyst has not read
    order-variation-estimator/out/ (a different question: whether order variation orients an edge),
    which may hold order counts for some corpora.

DIRECTION. For each sampled ordered pair (a, b), call it FORWARD if more of the learners who met both
    met a first (O > 0.5; at O = 0.5, the pair whose a sorts first by id), and BACKWARD otherwise. A
    curriculum's own direction is forward; its reverse is backward. Where order never varies, every
    backward cell is empty by order alone, while a forward cell can still fill: learners who fail a
    and are sent on to b anyway. Whether they are sent on is pass-through, not order.

MEASURES (per corpus, over its sampled ordered pairs)
    coverage      median N over sampled pairs
    two-way share W = among unordered pairs {a, b} with N >= 2 x MIN_CELL, the share met in both
                  orders by at least MIN_CELL learners each (each unordered pair counted once)
    minority share median over those unordered pairs of min(n_ab, n_ba) / (n_ab + n_ba), learners
                  whose first attempts at a and b share an instant excluded
    pass-through  median F over forward pairs with N x O >= MIN_CELL
    binding factor of each ordered pair whose cell is below MIN_CELL, checked in this order:
                  COVERAGE if N < MIN_CELL; else ORDER if N x O < MIN_CELL; else PASS-THROUGH.
    The decided share is the atlas's, unchanged.

LABELS (per corpus and direction; strings fixed here)
    CELL FILLS            fewer than half of that direction's pairs have a cell below MIN_CELL
    COVERAGE-LIMITED      otherwise, and COVERAGE binds at least half of the empty pairs
    ORDER-LIMITED         otherwise, and ORDER binds at least half
    PASS-THROUGH-LIMITED  otherwise, and PASS-THROUGH binds at least half
    MIXED                 otherwise; the three shares are printed with every label
    A corpus reads as two labels, forward / backward, printed with W and the shares.

PREDICTIONS FROM THE DOCUMENTATION (written now, to be scored, not used to choose anything)
    ASSISTments 2012-13   forward PASS-THROUGH-LIMITED (skill builders), backward ORDER-LIMITED
    EDM Cup 2023          backward ORDER-LIMITED (teacher problem sets)
    Junyi ds1275          COVERAGE-LIMITED both ways
    Duolingo SLAM         backward ORDER-LIMITED (fixed skill tree)
    DataShop tutors       forward PASS-THROUGH-LIMITED (mastery-gated curricula)
    EdNet KT1, Eedi       CELL FILLS both ways
    XES3G5M               no prediction (assignment rule not documented)
    V2  DOCUMENTATION AGREES if every predicted label is observed, else DOCUMENTATION DISAGREES ON
        <corpus: predicted -> observed, ...>.

THE CLAIMS IT TESTS FOR THE PAPER (Table 1's split: decided at most 0.22% of pairs, or more)
    C1  ORDER VARIATION SEPARATES THE CORPORA if the largest W among the corpora deciding at most
        0.22% is below the smallest W among those deciding more; otherwise ORDER VARIATION DOES NOT
        SEPARATE THE CORPORA, and the corpora on the wrong side are named.
    C2  the same test over the corpora whose forward label is not COVERAGE-LIMITED (those with enough
        learners per pair for order to matter), with the same two strings prefixed "WITH COVERAGE:".
    C3  for each corpus deciding at most 0.22%, its forward / backward labels, which the paper prints
        as the measured reason in place of the documented one.

FLOOR (run first; synthetic learners only; no corpus read)
    Five worlds of 3,000 learners and 40 skills, each one mechanism, through the real code path
    (all ordered pairs, MIN_CELL 5). A learner attempts 25 skills unless stated; an attempt passes with
    probability 0.6; a learner makes up to 3 attempts at a skill before moving on, except where gated.
      fixed      one global order for every learner; no gating
                 expect forward CELL FILLS, backward ORDER-LIMITED
      gated      a random order per learner; the learner moves on only after passing (unbounded retries)
                 expect PASS-THROUGH-LIMITED both ways
      curriculum one global order and gated as above (a mastery-gated fixed curriculum)
                 expect forward PASS-THROUGH-LIMITED, backward ORDER-LIMITED
      sparse     a random order per learner, no gating, 3 skills per learner
                 expect COVERAGE-LIMITED both ways
      free       a random order per learner, no gating
                 expect CELL FILLS both ways
    Also checked on every pair of every world: N x O x F equals the atlas's identifying cell
    (positivity.classify), to the learner. FLOOR PASSES if all ten labels are as expected and the
    identity holds; C1 and C2 are run on the five worlds as a smoke check of the code only (the worlds
    have no decided share; W must order them fixed and curriculum below free). A failed floor makes
    every real label UNANSWERABLE.

OUTPUT (out/): floor.json; result.json (per corpus: N, W, minority share, pass-through, per direction
    the share of empty pairs, the three binding shares and the label; the atlas's decided share; V2,
    C1, C2, C3). No per-learner or per-pair row.

WHAT IT CAN SAY  Which of three measured factors leaves each corpus without an identifying cell, in the
    curriculum's direction and against it, whether a measured order statistic sorts Table 1's corpora,
    and whether the documented way order is set predicts the factors.
WHAT IT CANNOT   Why a corpus's order is uniform (curriculum, platform or teacher), or whether a
    larger sample of the same platform would fill the cell; the factors are measured on the atlas's
    pair samples, not on every pair.

CHANGES (2026-10-13, before the floor or any corpus was run)
    1. PASS-THROUGH IS SPLIT IN TWO (maintainer). "Passed" is the atlas's: a first correct answer on a
       (positivity.states). Among learners who met a first, write
           P1  the share whose first attempt at a was wrong                         (ease)
           P2  among those, the share still without a correct answer on a when they reached b  (retry)
       so F = P1 x P2 and  cell = N x O x P1 x P2  exactly. The binding factor of an empty pair is now
       checked in the order COVERAGE (N < MIN_CELL), ORDER (N x O < MIN_CELL), EASE (N x O x P1 <
       MIN_CELL, too few even missed a first), else RETRY (enough missed a first, but answered it
       correctly before reaching b: mastery gating, or several questions on a before moving on).
       PASS-THROUGH-LIMITED is replaced by EASE-LIMITED and RETRY-LIMITED, with the same half rule;
       the predictions' PASS-THROUGH-LIMITED (ASSISTments forward, DataShop tutors forward) read
       RETRY-LIMITED. Medians of P1 and P2 are reported beside F.
    2. FLOOR, corrected before it ran. gated and curriculum now expect RETRY-LIMITED where they
       expected PASS-THROUGH-LIMITED. sparse gives each learner 2 skills, not 3: at 3, a pair's
       expected N is 11.5 (3,000 x 3/40 x 2/39), above MIN_CELL, so the world would not plant a
       coverage limit; at 2 it is 3.8. A sixth world, easy, is added: a random order per learner, no
       gating, one attempt per skill, pass probability 0.995 (expected learners who meet a first and
       miss it about 2.9 per pair); expect EASE-LIMITED both ways. FLOOR PASSES if all twelve labels
       are as expected and the identity holds on every pair. (That floor ran and passed under
       CHANGES 1-2; its record is out/floor-changes2.json.)
    3. A COUNT IS NOT EVIDENCE OF ORDER OR EASE (maintainer, after that floor). Under CHANGES 1-2 a pair
       with 5 to 9 learners and an even order usually has fewer than 5 who met a first, and was called
       ORDER; in the sparse world a quarter of the empty pairs were. The bias runs toward ORDER, the
       label the paper's headline is about. Now, for an empty pair with N >= MIN_CELL:
         ORDER     if fewer than MIN_CELL met a first AND an exact one-sided binomial test of the a-first
                   count against an even split, over the learners who met the two in a strict order,
                   gives p < 0.05;
         EASE      else, if fewer than MIN_CELL of the a-first learners missed a first AND an exact
                   one-sided binomial test of that count against the corpus's reference miss rate
                   (the median P1 over forward pairs with at least MIN_CELL a-first learners) gives
                   p < 0.05;
         RETRY     else, if at least MIN_CELL missed a first;
         COVERAGE  otherwise ("too few learners to tell"), and always when N < MIN_CELL.
       COVERAGE-LIMITED now reads "too few learners to tell". About 5% of balanced, under-covered pairs
       can be called ORDER by chance; the bands below show where. Labels are also reported per
       coverage band (N under 5, 5-19, 20-99, 100 and over), per direction, beside the overall label.
       FLOOR, two worlds added: marginal (a random order, no gating, 3 skills per learner, expected N
       11.5 per pair): COVERAGE-LIMITED both ways; modest (one global order, no gating, 5 skills per
       learner, expected N 38, one attempt per skill): forward CELL FILLS, backward ORDER-LIMITED. The
       other six worlds keep their expectations. FLOOR PASSES if all sixteen labels are as expected,
       COVERAGE binds at least 90% of the empty pairs in both directions of sparse and marginal, and the
       identity holds on every pair.
       DIFFICULTY, descriptive only (no verdict). For every sampled pair, three readings of how hard a
       is: P1 (among the a-first learners); a's first-attempt miss rate over all learners who attempted
       it; and an ability-adjusted difficulty, the mean over a's attempters of (first-attempt miss on a)
       minus (that learner's mean first-attempt miss over the other skills they attempted). Reported
       as medians for EASE-LIMITED pairs against all other pairs, per direction, so the readout says
       whether easy means easy for everyone or easy for those who met a first. On ASSISTments 2012-13
       and EDM Cup, the Spearman correlation over skills between a's Common Core grade
       (assist2012-direction/out/skill_ccss_map.json; EDM Cup's skill code) and its all-learner miss
       rate.
    RECORD. Commit 925159d's message says it adds CHANGES 3; it holds only the rename of the first
       floor's record, because the edit adding CHANGES 3 failed and the commit went ahead. The floor
       that ran after it was the CHANGES 1-2 code again (same result) and is not kept. CHANGES 3 is
       in the commit after 925159d, before the second floor.
    4. THE SECOND FLOOR FAILED (out/floor-changes3.json), in two worlds, before any corpus was read.
       easy read COVERAGE-LIMITED: the ease test's reference was the corpus's own median miss rate,
       which in a world of easy skills is itself 0.5%, so no skill was easier than usual. A corpus where
       most skills are easy would hide ease the same way. marginal had COVERAGE at 83% of the empty
       forward pairs: its learners had 3 attempts per skill, so retrying was really present (14%), and
       the world was not the pure coverage world it was meant to be. Changes (maintainer):
         EASE now tests against a fixed standard: fewer than MIN_CELL of the a-first learners missed a
         first AND an exact one-sided binomial test of that count against a miss rate of 1 in 5 gives
         p < 0.05 (a is answered correctly on first contact by significantly more than 80%). Labels at
         1 in 10 and 3 in 10 are printed beside it as a sensitivity check, without a verdict.
         marginal gives one attempt per skill.
       Same pass rule: sixteen labels as expected, COVERAGE at least 90% in sparse and marginal, identity.
       The third floor passed (out/floor.json).
    5. THE REAL READING, as coded (written after the third floor, before any corpus was read). Corpora:
       every row of atlas.json that the atlas did not skip, through atlas.discover() and its readers,
       pairs drawn exactly as atlas.audit draws them (corpus_rng(name), 20,000); ASSISTments 2012-13
       through positivity's loader with its 40,000-pair draw (default_rng(0)); the three SLAM courses at
       the construct grain through slam_atlas's reader and atlas.audit's draw (name
       slam-<course>-construct). Every sampled pair is kept, including pairs no learner reached
       (N = 0, COVERAGE). The identity is checked on every real pair too, and any mismatch is printed
       and fails the corpus. Decided shares come from the committed atlas files (ASSISTments: 87 of
       40,000 sampled pairs). EDM Cup records one sitting per learner and skill, so its first attempt
       is its only attempt and RETRY cannot occur there. C1 and C2 are computed over every corpus read,
       and, descriptively, over the seven rows of Table 1 (ASSISTments, EDM Cup, ds1275, SLAM en_es
       constructs, EdNet, XES3G5M, Eedi). For the predictions, "DataShop tutors" means every DataShop
       export but ds1275. Grades: ASSISTments through assist2012-direction/out/skill_ccss_map.json
       (skill id -> CCSS code); EDM Cup's units are CCSS codes; the grade is the code's leading number,
       K = 0, and codes with no grade (high school) are left out.
    6. THE VERDICT FUNNEL (maintainer, after the real reading of CHANGES 5, before this part was run).
       The real reading showed several corpora whose forward cells fill and that decide nothing, and
       three that decide many pairs, nearly all SUPPORTED. A cell of 5 learners is not a verdict. Each
       sampled pair is now followed through every condition shared/edge_state.classify_edge sets:
         COVERAGE     N >= MIN_CELL
         CELL         identifying cell >= MIN_CELL
         READABILITY  positivity.mde is defined (both cells >= MIN_CELL, control arm not within 0.01
                      of 0 or 1)
         POWER        mde <= 0.10 (CLAIMED_EFFECT)
         GATE         the powered pairs all get a verdict before the reachability gate (SUPPORTED if
                      the drop reaches the MDE, else a would-be CONTRADICTED); the gate then withdraws
                      would-be contradictions. Post-gate counts are the atlas's (atlas.json,
                      atlas-slam.json, positivity-assist.json); for the atlas corpora the pre-gate
                      SUPPORTED and would-be CONTRADICTED counts must equal the atlas's supported and
                      contradicted_before_reachability, or the corpus fails.
       Each stage's pass rate is the share of the pairs reaching it that pass it. BINDING STAGE = the
       stage with the lowest pass rate among those below one half; NONE BINDS if none is below half.
       SIZE: among readable pairs, the median identifying cell and the median control-arm accuracy,
       beside the per-group size two equal groups would need for an MDE of 0.10 at that accuracy.
       ABILITY: for each SUPPORTED pair, the drop recomputed on residuals: a learner's first-attempt
       outcome on b minus their mean first-attempt correctness over every other skill they attempted
       except a and b (learners with no other skill left out). The pair survives if the adjusted drop
       still reaches its MDE. Per corpus with at least 20 SUPPORTED pairs: VERDICTS SURVIVE ABILITY
       ADJUSTMENT if at least half survive, else VERDICTS ARE MOSTLY ABILITY; with fewer, NOT
       TESTABLE (TOO FEW VERDICTS).
       FLOOR, two worlds added; the eight above keep their expectations. Both have 5,000 learners,
       20 skills, every learner attempting every skill once in a random order:
         prereq   no ability spread (ability 0 for all); skill k depends on k-1 and k-2 (37 edges):
                  a learner who has not passed a dependency before reaching k has the logit of
                  success on k lowered by 1.5. Expect VERDICTS SURVIVE ABILITY ADJUSTMENT.
         ability  ability ~ N(0, 1.5), no dependency. Expect VERDICTS ARE MOSTLY ABILITY.
       Skill difficulties ~ N(-1.5, 0.5) in both (see below). FLOOR PASSES if all earlier conditions hold and these
       two ability verdicts are as expected.
       That floor ran and FAILED (out/floor-changes6a.json): prereq gave 14 SUPPORTED pairs, under the
       20 the check needs, because the code lowered the logit by 1.5 once if any dependency was
       unpassed, so a learner missing the other dependency was penalised either way and each edge's
       own drop was diluted. The world now lowers the logit by 1.5 for EACH unpassed dependency (the
       reading of "a dependency" above), and the floor is rerun; the rule is unchanged.
       That rerun FAILED too (out/floor-changes6b.json): 17 SUPPORTED. With difficulties centred at 0
       and penalties that stack, success fell to about 5% on most skills, so the group that had passed a
       held about 100 learners and most planted edges fell just short of power (planted drops 0.10 to
       0.22 against MDEs 0.05 to 0.12). Skill difficulty in both worlds is now N(-1.5, 0.5), so a
       skill with no unpassed dependency is answered correctly about 82% of the time; nothing else
       changes. The third run passed (out/floor.json).
       Run on the real corpora as `--funnel`, which reads each corpus and its pair sample exactly as
       CHANGES 5 does and adds a "funnel" entry per corpus to out/result.json, leaving the rest of that
       file as it was.
    7. JUNYI AT THE EXERCISE GRAIN (maintainer, 2026-10-13, after the funnel; nothing at this grain had
       been computed). atlas.datashop_rows reads ds1275's first KC column, KC (Area): 8 areas, 56
       ordered pairs, which is the grain of Table 1's Junyi row and of the readings above. Junyi's
       learners choose among exercises, so ds1275 is re-read at KC (Exercise) with the same filters
       (studies/measurement/difficulty-validation's datashop_rows_at). The pair sample is atlas.audit's
       draw under the name "datashop/ds1275-exercise" (corpus_rng of that name, 20,000 pairs). Three
       things are computed on it, all with the code above unchanged: atlas.audit itself (a new Table 1
       row, decided share included, written to out/junyi-exercise-atlas.json), measure(), and
       funnel() with the atlas row's post-gate counts. Written to out/junyi-exercise.json; result.json
       is not changed. No new verdict strings: the labels, binding stage and ability verdict above.

    python3 empty_cell.py --floor     # first
    python3 empty_cell.py             # every corpus on disk
"""
from __future__ import annotations

import json
import math
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "studies/identifiability/overlap"))
sys.path.insert(0, str(ROOT))
from positivity import MIN_CELL, at_item, classify, states, timelines  # noqa: E402

OUT = HERE / "out"
SEED = 20261013
FACTORS = ("COVERAGE", "ORDER", "EASE", "RETRY")
LABEL = {"COVERAGE": "COVERAGE-LIMITED", "ORDER": "ORDER-LIMITED", "EASE": "EASE-LIMITED",
         "RETRY": "RETRY-LIMITED"}


def pair_counts(a, b, first_touch, first_pass, outcome_at_touch, by_item):
    """N, a-first, b-first, missed-a-first, cell for one ordered pair (a, b)."""
    la, lb = by_item.get(a, set()), by_item.get(b, set())
    both = la & lb
    n = a_first = b_first = miss = cell = 0
    for learner in both:
        ta, tb = first_touch[learner][a], first_touch[learner][b]
        n += 1
        if ta < tb:
            a_first += 1
            if not outcome_at_touch[learner][a]:
                miss += 1
                pa = first_pass[learner].get(a)
                if pa is None or pa >= tb:
                    cell += 1
        elif tb < ta:
            b_first += 1
    return n, a_first, b_first, miss, cell


ALPHA = 0.05
BANDS = (("N<5", 0, 5), ("N5-19", 5, 20), ("N20-99", 20, 100), ("N100+", 100, 10 ** 12))


def binom_cdf(k: int, n: int, p: float) -> float:
    """P(X <= k), X ~ Binomial(n, p), exact."""
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


EASE_REF = 0.2                     # CHANGES 4: a fixed standard; 0.1 and 0.3 printed as a check
EASE_SENS = (0.1, 0.3)


def binding(n, a_first, b_first, miss, p1_ref=EASE_REF):
    """CHANGES 3-4: order or ease is blamed only when the count is improbably low, not merely below 5."""
    if n < MIN_CELL:
        return "COVERAGE"
    if a_first < MIN_CELL:
        strict = a_first + b_first
        return "ORDER" if strict and binom_cdf(a_first, strict, 0.5) < ALPHA else "COVERAGE"
    if miss < MIN_CELL:
        return "EASE" if p1_ref and binom_cdf(miss, a_first, p1_ref) < ALPHA else "COVERAGE"
    return "RETRY"


def label_of(rows, bands=True) -> dict:
    """rows: (cell, factor or None, N). The pre-registered half rule, overall and per coverage band."""
    if not rows:
        return {"label": "NO PAIRS", "pairs": 0}
    empty = [r[1] for r in rows if r[0] < MIN_CELL]
    e = len(empty) / len(rows)
    shares = {f: (empty.count(f) / len(empty) if empty else 0.0) for f in FACTORS}
    if e < 0.5:
        lab = "CELL FILLS"
    else:
        top = [f for f in FACTORS if shares[f] >= 0.5]
        lab = LABEL[top[0]] if top else "MIXED"
    out = {"label": lab, "pairs": len(rows), "empty_share": e, "binding_shares": shares}
    if bands:
        out["bands"] = {name: label_of([r for r in rows if lo <= r[2] < hi], bands=False)
                        for name, lo, hi in BANDS}
    return out


def measure(by_learner, pairs, check_identity=False) -> dict:
    first_touch, first_pass, outcome_at_touch = states(by_learner)
    by_item: dict[str, set] = {}
    for learner, ft in first_touch.items():
        for it in ft:
            by_item.setdefault(it, set()).add(learner)
    idx = at_item(first_touch, outcome_at_touch) if check_identity else None
    rows = {"forward": [], "backward": []}
    ns, Fs, P1s, P2s = [], [], [], []
    unordered = {}
    mismatches = 0
    counted = []
    for a, b in pairs:
        n, af, bf, miss, cell = pair_counts(a, b, first_touch, first_pass, outcome_at_touch, by_item)
        if check_identity:
            mismatches += len(classify((a, b), first_touch, first_pass, outcome_at_touch, idx)["failed"]) != cell
        ns.append(n)
        o = af / n if n else 0.0
        fwd = o > 0.5 or (o == 0.5 and str(a) < str(b))
        counted.append((n, af, bf, miss, cell, fwd))
        if fwd and af >= MIN_CELL:
            Fs.append(cell / af)
            P1s.append(miss / af)
            if miss:
                P2s.append(cell / miss)
        key = tuple(sorted((str(a), str(b))))
        if key not in unordered and n >= 2 * MIN_CELL:
            unordered[key] = (af, bf) if str(a) <= str(b) else (bf, af)
    sens = {r: {"forward": [], "backward": []} for r in EASE_SENS}
    for n, af, bf, miss, cell, fwd in counted:
        d = "forward" if fwd else "backward"
        rows[d].append((cell, binding(n, af, bf, miss) if cell < MIN_CELL else None, n))
        for r in EASE_SENS:
            sens[r][d].append((cell, binding(n, af, bf, miss, r) if cell < MIN_CELL else None, n))
    two_way = [min(x, y) >= MIN_CELL for x, y in unordered.values()]
    minority = [min(x, y) / (x + y) for x, y in unordered.values() if x + y]
    med = lambda v: statistics.median(v) if v else None
    out = {"learners": len(by_learner), "pairs": len(pairs), "coverage_median_N": med(ns),
           "W_two_way_share": (sum(two_way) / len(two_way)) if two_way else None,
           "unordered_pairs_for_W": len(two_way), "minority_share_median": med(minority),
           "pass_through_median_F": med(Fs), "ease_median_P1": med(P1s), "retry_median_P2": med(P2s),
           "forward": label_of(rows["forward"]), "backward": label_of(rows["backward"]),
           "ease_sensitivity": {str(r): {d: label_of(sens[r][d], bands=False)["label"] for d in sens[r]}
                                for r in EASE_SENS}}
    if check_identity:
        out["identity_mismatches"] = mismatches
    return out


# ---------------------------------------------------------------- the verdict funnel (CHANGES 6)

STAGES = ("COVERAGE", "CELL", "READABILITY", "POWER", "GATE")


def required_n(p: float, d: float = 0.10) -> int:
    """Per-group size two equal groups need for positivity.mde <= d at control accuracy p."""
    from positivity import mde as _mde
    lo, hi = MIN_CELL, 200000
    while lo < hi:
        mid = (lo + hi) // 2
        v = _mde(mid, mid, p)
        if v is not None and v <= d:
            hi = mid
        else:
            lo = mid + 1
    return lo


def funnel(by_learner, pairs, post_gate=None) -> dict:
    """Follow every pair through classify_edge's conditions; the ABILITY check on SUPPORTED pairs."""
    from positivity import mde as _mde
    from shared.edge_state import CLAIMED_EFFECT, SUPPORTED, classify_edge
    first_touch, first_pass, outcome_at_touch = states(by_learner)
    idx = at_item(first_touch, outcome_at_touch)
    by_item = {}
    for learner, ft in first_touch.items():
        for it in ft:
            by_item.setdefault(it, set()).add(learner)
    tot = {u: (sum(1 for ok in oat.values() if ok), len(oat)) for u, oat in outcome_at_touch.items()}
    reach = dict.fromkeys(STAGES, 0)
    passed = dict.fromkeys(STAGES, 0)
    supported = would_contra = survive = 0
    cells, ctrl_p = [], []
    for a, b in pairs:
        n = len(by_item.get(a, set()) & by_item.get(b, set()))
        reach["COVERAGE"] += 1
        if n < MIN_CELL:
            continue
        passed["COVERAGE"] += 1
        m, f = [], []
        for learner, tb, y in idx.get(b, []):
            ta = first_touch[learner].get(a)
            if ta is None or ta >= tb:
                continue
            pa = first_pass[learner].get(a)
            (m if pa is not None and pa < tb else f).append((learner, y))
        reach["CELL"] += 1
        if len(f) < MIN_CELL:
            continue
        passed["CELL"] += 1
        reach["READABILITY"] += 1
        p_m = sum(y for _, y in m) / len(m) if m else None
        v = _mde(len(m), len(f), p_m) if m else None
        if v is None:
            continue
        passed["READABILITY"] += 1
        cells.append(len(f))
        ctrl_p.append(p_m)
        reach["POWER"] += 1
        if v > CLAIMED_EFFECT:
            continue
        passed["POWER"] += 1
        obs = p_m - sum(y for _, y in f) / len(f)
        st = classify_edge(v, obs)[0]
        if st == SUPPORTED:
            supported += 1
            def resid(lst):
                out = []
                for u, y in lst:
                    c, k = tot[u]
                    oat = outcome_at_touch[u]
                    for x in (a, b):
                        if x in oat:
                            c -= 1 if oat[x] else 0
                            k -= 1
                    if k > 0:
                        out.append((1 if y else 0) - c / k)
                return out
            rm, rf = resid(m), resid(f)
            if rm and rf and (sum(rm) / len(rm) - sum(rf) / len(rf)) >= v:
                survive += 1
        else:
            would_contra += 1
    reach["GATE"] = supported + would_contra
    if post_gate is not None:
        passed["GATE"] = post_gate["supported"] + post_gate["contradicted"]
    else:
        passed["GATE"] = reach["GATE"]
    rates = {s_: (passed[s_] / reach[s_] if reach[s_] else None) for s_ in STAGES}
    below = [s_ for s_ in STAGES if rates[s_] is not None and rates[s_] < 0.5]
    binding = min(below, key=lambda s_: rates[s_]) if below else "NONE BINDS"
    med = lambda v_: statistics.median(v_) if v_ else None
    p_med = med(ctrl_p)
    if supported >= 20:
        abil = ("VERDICTS SURVIVE ABILITY ADJUSTMENT" if survive / supported >= 0.5
                else "VERDICTS ARE MOSTLY ABILITY")
    else:
        abil = "NOT TESTABLE (TOO FEW VERDICTS)"
    return {"reached": reach, "passed": passed, "pass_rates": rates, "binding_stage": binding,
            "pre_gate": {"supported": supported, "would_be_contradicted": would_contra},
            "size": {"median_identifying_cell_readable": med(cells), "median_control_accuracy": p_med,
                     "per_group_n_for_mde_0.10": required_n(p_med) if p_med and 0.01 < p_med < 0.99 else None},
            "ability": {"supported": supported, "survive": survive,
                        "share_survive": (survive / supported) if supported else None, "verdict": abil}}


def ability_world(kind, seed):
    rng = random.Random(seed)
    K, n = 20, 5000
    b = [rng.gauss(-1.5, 0.5) for _ in range(K)]
    rows = []
    for u in range(n):
        th = 0.0 if kind == "prereq" else rng.gauss(0, 1.5)
        order = rng.sample(range(K), K)
        passed_ = set()
        for t, k in enumerate(order):
            lg = th - b[k]
            if kind == "prereq":
                lg -= 1.5 * sum(1 for d in (k - 1, k - 2) if d >= 0 and d not in passed_)
            ok = rng.random() < 1 / (1 + math.exp(-lg))
            if ok:
                passed_.add(k)
            rows.append((f"u{u}", f"s{k:02d}", ok, t, False, False))
    return rows


# ---------------------------------------------------------------- floor

WORLDS = {  # name: (global order, gated, skills per learner, attempts, pass prob), expected fwd / bwd
    "fixed": ((True, False, 25, 3, 0.6), ("CELL FILLS", "ORDER-LIMITED")),
    "gated": ((False, True, 25, None, 0.6), ("RETRY-LIMITED", "RETRY-LIMITED")),
    "curriculum": ((True, True, 25, None, 0.6), ("RETRY-LIMITED", "ORDER-LIMITED")),
    "sparse": ((False, False, 2, 3, 0.6), ("COVERAGE-LIMITED", "COVERAGE-LIMITED")),
    "free": ((False, False, 25, 3, 0.6), ("CELL FILLS", "CELL FILLS")),
    "easy": ((False, False, 25, 1, 0.995), ("EASE-LIMITED", "EASE-LIMITED")),
    "marginal": ((False, False, 3, 1, 0.6), ("COVERAGE-LIMITED", "COVERAGE-LIMITED")),
    "modest": ((True, False, 5, 1, 0.6), ("CELL FILLS", "ORDER-LIMITED")),
}
COVERAGE_WORLDS = ("sparse", "marginal")
N_LEARNERS, N_SKILLS = 3000, 40


def world_rows(spec, seed):
    glob, gated, k, attempts, p = spec
    rng = random.Random(seed)
    order = list(range(N_SKILLS))
    rng.shuffle(order)
    rows = []
    for u in range(N_LEARNERS):
        chosen = set(rng.sample(range(N_SKILLS), k))
        seq = [s for s in order if s in chosen] if glob else rng.sample(sorted(chosen), k)
        t = 0
        for s in seq:
            tries = 0
            while True:
                ok = rng.random() < p
                rows.append((f"u{u}", f"s{s:02d}", ok, t, False, False))
                t += 1
                tries += 1
                if ok or (not gated and tries >= attempts):
                    break
    return rows


def floor() -> dict:
    pairs = [(f"s{a:02d}", f"s{b:02d}") for a in range(N_SKILLS) for b in range(N_SKILLS) if a != b]
    res, ok = {}, True
    for i, (name, (spec, expect)) in enumerate(WORLDS.items()):
        m = measure(timelines(world_rows(spec, SEED + i)), pairs, check_identity=True)
        got = (m["forward"]["label"], m["backward"]["label"])
        m["expected"], m["passes"] = list(expect), got == expect and m["identity_mismatches"] == 0
        if name in COVERAGE_WORLDS:
            cov = [m[d]["binding_shares"]["COVERAGE"] for d in ("forward", "backward")]
            m["coverage_binds"] = cov
            m["passes"] = m["passes"] and min(cov) >= 0.9
        ok &= m["passes"]
        res[name] = m
        print(f"{name:11s} W={m['W_two_way_share']}  fwd {got[0]:22s} bwd {got[1]:22s} "
              f"identity mismatches {m['identity_mismatches']}  coverage binds {m.get('coverage_binds', '')}  "
              f"{'ok' if m['passes'] else 'FAIL'}", flush=True)
    pairs20 = [(f"s{a:02d}", f"s{b:02d}") for a in range(20) for b in range(20) if a != b]
    for j, (kind, expect) in enumerate((("prereq", "VERDICTS SURVIVE ABILITY ADJUSTMENT"),
                                         ("ability", "VERDICTS ARE MOSTLY ABILITY"))):
        fu = funnel(timelines(ability_world(kind, SEED + 100 + j)), pairs20)
        fu["expected"], fu["passes"] = expect, fu["ability"]["verdict"] == expect
        ok &= fu["passes"]
        res[f"ability_{kind}"] = fu
        print(f"{kind:11s} supported {fu['ability']['supported']}, survive {fu['ability']['survive']} -> "
              f"{fu['ability']['verdict']}  binding {fu['binding_stage']}  {'ok' if fu['passes'] else 'FAIL'}",
              flush=True)
    w = {k: v["W_two_way_share"] for k, v in res.items() if k in WORLDS}
    res["smoke_W_order"] = bool(w["fixed"] < w["free"] and w["curriculum"] < w["free"])
    res["FLOOR_PASSES"] = bool(ok)
    print("FLOOR PASSES" if ok else "FLOOR FAILS", "| W orders fixed, curriculum below free:", res["smoke_W_order"])
    return res


# ---------------------------------------------------------------- real corpora (CHANGES 5)

PREDICT = {  # corpus -> {direction: allowed labels}
    "assist": {"forward": {"RETRY-LIMITED"}, "backward": {"ORDER-LIMITED"}},
    "edmcup": {"backward": {"ORDER-LIMITED"}},
    "datashop/ds1275": {"forward": {"COVERAGE-LIMITED"}, "backward": {"COVERAGE-LIMITED"}},
    "slam": {"backward": {"ORDER-LIMITED"}},
    "datashop": {"forward": {"RETRY-LIMITED"}},
    "ednet": {"forward": {"CELL FILLS"}, "backward": {"CELL FILLS"}},
    "eedi": {"forward": {"CELL FILLS"}, "backward": {"CELL FILLS"}},
}
TABLE1 = ("assist", "edmcup", "datashop/ds1275", "slam-en_es-construct", "ednet", "xes3g5m", "eedi")
LOW = 0.0022


def prediction_for(name):
    if name in PREDICT:
        return PREDICT[name]
    if name.startswith("slam-"):
        return PREDICT["slam"]
    if name.startswith("datashop/"):
        return PREDICT["datashop"]
    return None


def grade_of(code: str):
    head = str(code).split(".")[0].strip().upper()
    if head == "K":
        return 0
    return int(head) if head.isdigit() else None


def spearman(x, y):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2
            i = j + 1
        return r
    rx, ry = ranks(x), ranks(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else None


def difficulty(by_learner, pairs, m_rows):
    """CHANGES 3 descriptive readout: three readings of how hard a is, EASE pairs against the rest."""
    first_touch, _fp, outcome_at_touch = states(by_learner)
    miss_by_item, learner_mean = {}, {}
    for u, oat in outcome_at_touch.items():
        misses = [0 if ok else 1 for ok in oat.values()]
        learner_mean[u] = (sum(misses), len(misses))
        for it, ok in oat.items():
            miss_by_item.setdefault(it, []).append((u, 0 if ok else 1))
    all_miss, adj = {}, {}
    for it, lst in miss_by_item.items():
        all_miss[it] = sum(m for _, m in lst) / len(lst)
        d = [m - (learner_mean[u][0] - m) / (learner_mean[u][1] - 1) for u, m in lst if learner_mean[u][1] > 1]
        adj[it] = sum(d) / len(d) if d else None
    out = {}
    for direc, rows in m_rows.items():
        groups = {"EASE": [], "other": []}
        for (a, b), (cell, factor, n, p1) in rows:
            groups["EASE" if factor == "EASE" else "other"].append((p1, all_miss.get(a), adj.get(a)))
        med = lambda v: statistics.median(v) if v else None
        out[direc] = {g: {"pairs": len(v), "P1_median": med([x for x, _, _ in v if x is not None]),
                          "all_learner_miss_median": med([y for _, y, _ in v if y is not None]),
                          "ability_adjusted_median": med([z for _, _, z in v if z is not None])}
                      for g, v in groups.items()}
    return out, all_miss


def read_corpus(name, by_learner, pairs):
    m = measure(by_learner, pairs, check_identity=True)
    # per-pair rows again for the difficulty readout (aggregated, never written)
    first_touch, first_pass, outcome_at_touch = states(by_learner)
    by_item = {}
    for learner, ft in first_touch.items():
        for it in ft:
            by_item.setdefault(it, set()).add(learner)
    rows = {"forward": [], "backward": []}
    for a, b in pairs:
        n, af, bf, miss, cell = pair_counts(a, b, first_touch, first_pass, outcome_at_touch, by_item)
        o = af / n if n else 0.0
        fwd = o > 0.5 or (o == 0.5 and str(a) < str(b))
        f = binding(n, af, bf, miss) if cell < MIN_CELL else None
        rows["forward" if fwd else "backward"].append(((a, b), (cell, f, n, miss / af if af else None)))
    m["difficulty"], all_miss = difficulty(by_learner, pairs, rows)
    return m, all_miss


def real() -> dict:
    sys.path.insert(0, str(ROOT / "studies/identifiability/overlap"))
    import numpy as np
    import atlas
    from positivity import LOADERS, candidate_pairs
    ov = ROOT / "studies/identifiability/overlap/out"
    decided = {r["dataset"]: r["decided_frac"] for r in json.loads((ov / "atlas.json").read_text())
               if "skipped" not in r}
    for r in json.loads((ov / "atlas-slam.json").read_text())["rows"]:
        decided[r["dataset"]] = r["decided_frac"]
    pa = json.loads((ov / "positivity-assist.json").read_text())["summary"]
    decided["assist"] = (pa["edge_state"]["supported"] + pa["edge_state"]["contradicted"]) / pa["edges"]

    def atlas_pairs(name, by_learner, max_pairs=20000):
        fts, _, oat = states(by_learner)
        items = sorted(at_item(fts, oat))
        pairs = candidate_pairs(name, items, "all")
        if len(pairs) > max_pairs:
            rng = atlas.corpus_rng(name)
            pairs = [pairs[i] for i in rng.choice(len(pairs), max_pairs, replace=False)]
        return pairs

    jobs = []
    for name, f in atlas.discover().items():
        if name not in decided:
            continue
        jobs.append((name, (lambda f=f: atlas.READERS[f[0]](f[1])) if isinstance(f, tuple)
                     else (lambda f=f: atlas.datashop_rows(f)), "atlas"))
    jobs.append(("assist", lambda: LOADERS["assist"](), "assist"))
    try:
        from shared.corpus import Slam
        from shared.paths import data_path
        root = str(data_path("SLAM_DIR"))
        for course in ("en_es", "es_en", "fr_en"):
            jobs.append((f"slam-{course}-construct",
                         (lambda c=course: ((u, unit, o >= 0.5, t, False, False)
                                            for u, unit, t, o in Slam(root, c, "construct").events())), "atlas"))
    except Exception as e:  # noqa: BLE001
        print("SLAM not read:", e)
    corpora, grades = {}, {}
    for name, rows_fn, how in jobs:
        try:
            by_learner = timelines(rows_fn())
            if how == "assist":
                fts, _, oat = states(by_learner)
                items = sorted(at_item(fts, oat))
                pairs = candidate_pairs("assist", items, "all")
                if len(pairs) > 40000:
                    rng = np.random.default_rng(0)
                    pairs = [pairs[i] for i in rng.choice(len(pairs), 40000, replace=False)]
            else:
                pairs = atlas_pairs(name, by_learner)
            m, all_miss = read_corpus(name, by_learner, pairs)
            if m["identity_mismatches"]:
                raise AssertionError(f"identity fails on {m['identity_mismatches']} pairs")
            m["decided_share"] = decided[name]
            corpora[name] = m
            if name in ("assist", "edmcup"):
                cmap = (json.loads((ROOT / "studies/measurement/assist2012-direction/out/skill_ccss_map.json")
                                   .read_text()) if name == "assist" else None)
                xs, ys = [], []
                for it, miss in all_miss.items():
                    code = (cmap.get(str(it), {}).get("ccss") if cmap else it)
                    g = grade_of(code) if code else None
                    if g is not None:
                        xs.append(g)
                        ys.append(miss)
                grades[name] = {"skills": len(xs), "spearman_grade_vs_all_learner_miss": spearman(xs, ys)
                                if len(xs) > 2 else None}
            print(f"{name:24s} N~{m['coverage_median_N']}  W={m['W_two_way_share']}  "
                  f"fwd {m['forward']['label']:22s} bwd {m['backward']['label']:22s} "
                  f"decided {m['decided_share']:.4%}", flush=True)
        except Exception as e:  # noqa: BLE001
            corpora[name] = {"skipped": f"{type(e).__name__}: {e}"}
            print(f"{name:24s} skipped: {corpora[name]['skipped']}", flush=True)
    read = {k: v for k, v in corpora.items() if "skipped" not in v}

    def c1(names, prefix=""):
        names = [n for n in names if n in read and read[n]["W_two_way_share"] is not None]
        low = [n for n in names if read[n]["decided_share"] <= LOW]
        high = [n for n in names if read[n]["decided_share"] > LOW]
        if not low or not high:
            return {"verdict": prefix + "NOT TESTABLE", "low": low, "high": high}
        maxlow = max(read[n]["W_two_way_share"] for n in low)
        minhigh = min(read[n]["W_two_way_share"] for n in high)
        wrong = sorted([n for n in low if read[n]["W_two_way_share"] >= minhigh] +
                       [n for n in high if read[n]["W_two_way_share"] <= maxlow])
        v = ("ORDER VARIATION SEPARATES THE CORPORA" if maxlow < minhigh
             else "ORDER VARIATION DOES NOT SEPARATE THE CORPORA")
        return {"verdict": prefix + v, "max_W_low": maxlow, "min_W_high": minhigh, "wrong_side": wrong,
                "low": low, "high": high}

    covered = [n for n in read if read[n]["forward"]["label"] != "COVERAGE-LIMITED"]
    disagree = []
    for n, m in read.items():
        pred = prediction_for(n)
        for d, allowed in (pred or {}).items():
            if m[d]["label"] not in allowed:
                disagree.append(f"{n} {d}: {'/'.join(sorted(allowed))} -> {m[d]['label']}")
    return {"corpora": corpora, "grades": grades,
            "V2": "DOCUMENTATION AGREES" if not disagree else "DOCUMENTATION DISAGREES ON " + "; ".join(disagree),
            "C1": c1(list(read)), "C2": c1(covered, "WITH COVERAGE: "),
            "C1_table1": c1([n for n in TABLE1 if n in read]),
            "C2_table1": c1([n for n in TABLE1 if n in covered], "WITH COVERAGE: "),
            "C3": {n: f"{m['forward']['label']} / {m['backward']['label']}" for n, m in read.items()
                   if m["decided_share"] <= LOW}}


def real_funnel(res: dict) -> dict:
    """CHANGES 6 on the real corpora: the same corpora and pair draws as real()."""
    sys.path.insert(0, str(ROOT / "studies/identifiability/overlap"))
    import numpy as np
    import atlas
    from positivity import LOADERS, candidate_pairs
    ov = ROOT / "studies/identifiability/overlap/out"
    post, pre = {}, {}
    for r in json.loads((ov / "atlas.json").read_text()):
        if "skipped" not in r:
            post[r["dataset"]] = r
            pre[r["dataset"]] = r
    for r in json.loads((ov / "atlas-slam.json").read_text())["rows"]:
        post[r["dataset"]] = r
        pre[r["dataset"]] = r
    pa = json.loads((ov / "positivity-assist.json").read_text())["summary"]["edge_state"]
    post["assist"] = {"supported": pa["supported"], "contradicted": pa["contradicted"]}

    def sample(name, by_learner, k, rng):
        fts, _, oat = states(by_learner)
        items = sorted(at_item(fts, oat))
        pairs = candidate_pairs(name, items, "all")
        if len(pairs) > k:
            pairs = [pairs[i] for i in rng.choice(len(pairs), k, replace=False)]
        return pairs

    jobs = []
    for name, f in atlas.discover().items():
        if name in post and name in res["corpora"] and "skipped" not in res["corpora"][name]:
            jobs.append((name, (lambda f=f: atlas.READERS[f[0]](f[1])) if isinstance(f, tuple)
                         else (lambda f=f: atlas.datashop_rows(f))))
    jobs.append(("assist", lambda: LOADERS["assist"]()))
    from shared.corpus import Slam
    from shared.paths import data_path
    root = str(data_path("SLAM_DIR"))
    for course in ("en_es", "es_en", "fr_en"):
        jobs.append((f"slam-{course}-construct",
                     (lambda c=course: ((u, unit, o >= 0.5, t, False, False)
                                        for u, unit, t, o in Slam(root, c, "construct").events()))))
    for name, fn in jobs:
        try:
            bl = timelines(fn())
            if name == "assist":
                pairs = sample("assist", bl, 40000, np.random.default_rng(0))
            else:
                pairs = sample(name, bl, 20000, atlas.corpus_rng(name))
            fu = funnel(bl, pairs, post_gate=post[name])
            if name in pre and "contradicted_before_reachability" in pre[name]:
                want = (pre[name]["supported"], pre[name]["contradicted_before_reachability"])
                got = (fu["pre_gate"]["supported"], fu["pre_gate"]["would_be_contradicted"])
                fu["matches_atlas"] = want == got
                if want != got:
                    raise AssertionError(f"pre-gate counts {got} differ from the atlas's {want}")
            res["corpora"][name]["funnel"] = fu
            print(f"{name:24s} binding {fu['binding_stage']:12s} rates "
                  f"{ {k: (round(v, 3) if v is not None else None) for k, v in fu['pass_rates'].items()} } "
                  f"cell {fu['size']['median_identifying_cell_readable']} need {fu['size']['per_group_n_for_mde_0.10']}  "
                  f"{fu['ability']['verdict']} ({fu['ability']['survive']}/{fu['ability']['supported']})", flush=True)
        except Exception as e:  # noqa: BLE001
            res["corpora"].setdefault(name, {})["funnel"] = {"skipped": f"{type(e).__name__}: {e}"}
            print(f"{name:24s} funnel skipped: {type(e).__name__}: {e}", flush=True)
    return res


def junyi_exercise() -> dict:
    """CHANGES 7: ds1275 at KC (Exercise), through atlas.audit, measure() and funnel()."""
    sys.path.insert(0, str(ROOT / "studies/identifiability/overlap"))
    sys.path.insert(0, str(ROOT / "studies/measurement/difficulty-validation"))
    import atlas
    from difficulty_validation import datashop_rows_at
    from shared.corpus import ds1275_export
    from shared.paths import data_path
    name = "datashop/ds1275-exercise"
    f = ds1275_export(data_path("DS1275_DIR"))
    rows = list(datashop_rows_at(f, "KC (Exercise)"))
    arow = atlas.audit(name, iter(rows), 20000)
    arow["kc_model"] = "KC (Exercise)"
    (OUT / "junyi-exercise-atlas.json").write_text(json.dumps(arow, indent=1, default=str))
    bl = timelines(iter(rows))
    fts, _, oat = states(bl)
    items = sorted(at_item(fts, oat))
    from positivity import candidate_pairs
    pairs = candidate_pairs(name, items, "all")
    if len(pairs) > 20000:
        rng = atlas.corpus_rng(name)
        pairs = [pairs[i] for i in rng.choice(len(pairs), 20000, replace=False)]
    m, _ = read_corpus(name, bl, pairs)
    if m["identity_mismatches"]:
        raise AssertionError("identity fails")
    m["decided_share"] = arow["decided_frac"]
    fu = funnel(bl, pairs, post_gate={"supported": arow["supported"], "contradicted": arow["contradicted"]})
    want = (arow["supported"], arow["contradicted_before_reachability"])
    got = (fu["pre_gate"]["supported"], fu["pre_gate"]["would_be_contradicted"])
    fu["matches_atlas"] = want == got
    if want != got:
        raise AssertionError(f"pre-gate counts {got} differ from the atlas's {want}")
    m["funnel"] = fu
    return {"atlas_row": arow, "reading": m}


def main() -> None:
    OUT.mkdir(exist_ok=True)
    if "--junyi-exercise" in sys.argv:
        r = junyi_exercise()
        (OUT / "junyi-exercise.json").write_text(json.dumps(r, indent=1, default=str))
        a, m = r["atlas_row"], r["reading"]
        print(f"atlas: {a['learners']} learners, {a['items']} exercises, {a['edges']} pairs scored, median cell "
              f"{a['median_identifying']}, readable {a['readable_frac']:.3f}, supported {a['supported']}, "
              f"contradicted {a['contradicted']}, decided {a['decided_frac']:.4%}, background {a['drop_median']}")
        print(f"labels: fwd {m['forward']['label']}, bwd {m['backward']['label']}, N~{m['coverage_median_N']}, "
              f"W {m['W_two_way_share']}")
        fu = m["funnel"]
        print("funnel", fu["reached"], fu["passed"], fu["binding_stage"], fu["size"], fu["ability"])
        return
    if "--funnel" in sys.argv:
        path = OUT / "result.json"
        res = real_funnel(json.loads(path.read_text()))
        path.write_text(json.dumps(res, indent=1, default=str))
        return
    if "--floor" in sys.argv:
        r = floor()
        (OUT / "floor.json").write_text(json.dumps(r, indent=1))
    else:
        r = real()
        (OUT / "result.json").write_text(json.dumps(r, indent=1, default=str))
        for k in ("V2", "C1", "C2", "C1_table1", "C2_table1"):
            print(k, r[k] if isinstance(r[k], str) else r[k]["verdict"], "" if isinstance(r[k], str) else r[k].get("wrong_side", ""))


if __name__ == "__main__":
    main()
