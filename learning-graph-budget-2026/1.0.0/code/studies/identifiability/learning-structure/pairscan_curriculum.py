"""PRE-REGISTERED: are the pairs iita_pairscan flagged skills the XES3G5M curriculum links?

iita_pairscan.py (IITA-PAIRSCAN.md, out/iita-pairscan.json, committed at 1dfb78c) found PAIRWISE LOCAL
DEPENDENCE BEYOND ONE TRAIT on XES3G5M: 8 of 15 fifteen-skill sets carry an isolated significant pair,
20 ordered pairs that are 12 unordered skill pairs. That statistic cannot orient a pair and cannot
tell a prerequisite from a second trait shared by exactly two skills. XES3G5M ships an expert KC
taxonomy (kc_routes: every KC's route from a root to itself). This asks whether the flagged pairs are
skills the taxonomy links, more often than the unflagged pairs of the same sets are.

Reads, through shared.paths.data_path("XES_DIR"): cid2route.json (KC id -> route, root first; written
by the committed generator data/ingest/xes3g5m/flatten.py, md5 checked against data/data-sources.json)
and attempts.tsv (through surmise_graphs' loader and mastery table, for the co-attempt covariate
only). Reads out/iita-pairscan.json (sha256 checked against the 1dfb78c commit) for the sets, their
fitted 2PL parameters and the flagged pairs. Raw exports stay outside the repo; only per-set counts,
test statistics and p-values are written. --validate never stores which pairs were flagged.

Seen while this was written, not chosen from (no statistic joining flagged pairs to the taxonomy
has been computed): the structure of out/iita-pairscan.json and its per-set counts (12 flagged
unordered pairs, per set 2, 1, 3, 0, 1, 0, 0, 1, 2, 0, 1, 0, 1, 0, 0; set 14 holds one CLUSTERED
significant pair). Label-blind, over all eligible pairs of each set: route coverage (every skill
resolves), compound skills (0-9 a set), each set's count of R1 and R2 pairs and its distance
summary, and the Spearman correlation of distance with each covariate (|rho| <= 0.29 for |db|,
<= 0.41 for n_both, <= 0.43 for expected discordance). One consequence of the positivity count
is unavoidable and stated here: no set holding a flagged pair holds any R2 pair, so no flagged pair
can be R2 and R2 is unreadable (POSITIVITY below). Set 14's R2 count fell from 3 to 2 when its
one unscanned pair and its clustered pair were dropped; neither is a flagged pair. The R1 counts of
the flag-bearing sets (1-5 of 105 each) do not reveal the R1 status of any flagged pair.

PRE-REGISTRATION (written before the comparison; CHANGE 1 was forced by the synthetic run, also before)

UNITS        Unordered skill pairs {i, j} within the 15 scored XES3G5M sets of iita_pairscan (all
             converged). A pair is ELIGIBLE if either orientation was scanned. The scan mask is not in
             the committed output, so it is rebuilt from the committed fitted parameters by the same
             rule (model-expected counterexample count >= 5; the committed rule uses the bootstrap
             mean, whose expectation this is). The rebuild matches the committed scanned count in 13
             of 15 sets and is off by 3 and 1 ordered pairs in sets 12 and 14; at the unordered level
             every pair of every flag-bearing set is eligible either way (105 of 105), so the choice
             cannot move any test (a set with no flagged pair is inert under within-set permutation).
FLAGGED      An eligible pair with an ISOLATED significant ordered pair in either orientation (12).
             A pair whose significant orientations are all CLUSTERED is dropped from both groups
             (one pair, set 14). COMPARISON = every other eligible pair of the same sets.
TAXONOMY     A KC's route is its cid2route list (root -> KC). A compound skill ('a_b', questions
             tagged with several KCs) stands for each KC it names; a pair relation holds if it holds
             for some component pair. The file's structure is a containment tree with no sibling
             order and nine roots (parallel schemes: 拓展思维, 知识点, 课内知识点, ...).
  R1  ADJACENT (unordered): some component pair is the same KC, has the same route, is siblings
      (routes equal but for the last element) or parent-child (one route is the other minus its
      last element).
  R2  ROUTED BEFORE (ordered): some component pair is ancestor-descendant, one route a proper prefix
      of the other; the ancestor comes first along the descendant's route. This is the only order
      the files carry: a route is a containment path, not a teaching sequence, and siblings are
      unordered. Orientation = ancestor -> descendant, 0 if component pairs disagree.
  R3  DISTANCE: tree path length len(ra) + len(rb) - 2 lcp(ra, rb), minimised over component pairs,
      0 for a shared KC, roots joined at a virtual super-root. Tested as its within-set normalised
      mid-rank u = (rank - 0.5) / N (shared.stats.rank), whose mean over a set is 0.5.
STATISTIC    For R1 / R2: the count of relation-positive flagged pairs; for R3: the sum of their u.
             Equivalent to comparing the flagged rate (or mean rank) with the comparison pairs' at
             fixed set composition. effect = flagged mean minus its permutation mean (a rate
             difference for R1 / R2, a rank shift for R3).
NULL         Within-set permutation: the flagged label is permuted among the eligible pairs of each
             set, the count per set held fixed, N_PERM = 10,000 draws. One-sided and signed:
             enrichment is MORE R1 / R2 (upper tail) or SMALLER distance rank (lower tail); a
             depletion is never read as a link. p = (1 + #{null at least as extreme}) / (N_PERM + 1).
             This permutation is the null distribution of an exact conditional test, not a control
             arm, so it is not deranged: the observed labelling is one draw of it under H0, and a
             derangement would push the null away from the data. The unit permuted is the unit the
             flag was assigned to (a pair within a set).
POSITIVITY   A relation is READABLE only if its best case (every set's flags on its most extreme
             pairs) reaches p < 0.05 / 3. Label-blind count: R2 has 0 positive pairs in the 8
             flag-bearing sets (2 in set 14, which has no flag), best-case p = 1: R2 is UNREADABLE
             and its enrichment and orientation analyses report "no flagged R2 pair". R1 has 21
             positive pairs there and R3 is graded; both are readable (best case p = 1e-4).
FAMILY       Holm at familywise 0.05 over the readable relations: R1 and R3. The brief named R1 or R2
             as verdict-bearing and R3 as a rank comparison; R3 enters the verdict family because R2
             fails positivity, which leaves R1 alone with 21 positive pairs. The maintainer may strike
             R3 back to reported-only before committing, in which case R1 is tested alone at 0.05.
CONTROL      The confound: taxonomically near skills may be of similar difficulty, or practised by the
             same learners, and either could raise pairwise dependence without a curricular link.
             Stratifiers, not regression covariates: the permutation runs within set x STRATUM, the
             flagged count per stratum held fixed, so the flagged pairs are compared only with pairs
             of the same difficulty gap and co-attempt level.
               |db|    |b_i - b_j|, fitted 2PL difficulties from out/iita-pairscan.json
               n_both  learners with a mastery state on both skills, corpus-wide (surmise_graphs'
                       mastery table: the pool the sets were drawn from)
             The complete-responder count is the set's learner count, the same for every pair of a
             set, so the within-set permutation already holds it fixed exactly; n_both is its
             pair-level analogue. VERDICT-BEARING: within set x |db| within-set quintile x n_both
             within-set half (10 strata of ~10 pairs; CHANGE 1). Reported, never verdict-bearing:
             terciles of |db| alone, of n_both alone, and of the expected discordant count E_ij + E_ji
             from the fitted model (the scan's own power: flagged pairs can only be pairs it could
             see), and the flagged and comparison medians of all three.
ORIENTATION  For every flagged R2 pair (none can exist; POSITIVITY), never verdict-bearing:
             z orientation = the ordered pair with the more negative z (iita_pairscan's prereq ->
             dependant); curricular = ancestor -> descendant; difficulty = easier (lower b) ->
             harder. Agreement of z with the curriculum is scored with shared.direction.reversed_arrow.
             iita_pairscan's DIRECTION note applies: studentisation gives the rarer cell the larger z,
             so the z orientation tends to run easier -> harder, and agreement with the curriculum may
             be difficulty order. Control: the same agreement for difficulty vs curriculum on the
             flagged pairs and on every eligible R2 pair of the 15 sets (the baseline), and the count
             of flagged pairs where z and difficulty disagree with curriculum siding with z. Only
             agreement in that discordant subset would be orientation beyond difficulty.
MDE          By simulation on the real sets' structure (real relations, covariates and flagged
             counts), 1000 replicates a point, 80% power, CONTROL permutation, at the Holm first-step
             level 0.025 (--validate, out/pairscan-curriculum-synthetic.json):
               R1  +0.32 rate difference (flagged adjacency rate ~0.34 against a within-set
                   expectation of 0.024; 0.29 of 12 flagged pairs expected adjacent). Significance
                   needs 3 adjacent flagged pairs at 0.025, 2 at 0.05.
               R3  -0.26 rank shift (flagged pairs' mean distance rank ~0.24 against 0.50);
                   significance needs a mean rank <= 0.34 at 0.025, <= 0.37 at 0.05.
             At 0.05 (if R3 is struck): R1 +0.31 under CONTROL, +0.22 unstratified.
MEANINGFUL   The smallest enrichment worth a reading, fixed here: +0.10 for R1 (about 5x the
             within-set expectation; below it at most one extra adjacent pair among 12) and a -0.10
             rank shift for R3 (flagged pairs at the 40th distance percentile). Both MDEs exceed
             these, so SAID NOW: this comparison cannot return NOT CURRICULUM-LINKED. A null will read
             UNDERPOWERED. Only a large link (3 or more of the 12 flagged pairs adjacent, or a mean
             distance rank of the flagged pairs at or below the 34th percentile) can produce a reading.
VERDICTS     exactly one of:
               CURRICULUM-LINKED       a readable relation passes Holm (familywise 0.05) both under
                                       the within-set permutation AND under CONTROL, in the enriched
                                       direction.
               NOT CURRICULUM-LINKED   none passes, and some readable relation's CONTROL MDE at the
                                       Holm first-step level is <= its MEANINGFUL enrichment (it
                                       could have seen one). Not reachable here (MDE above).
               UNDERPOWERED            none passes and no readable relation is powered for a
                                       meaningful enrichment.
             An enrichment passing only the unstratified test is reported in `reason` and reads as
             UNDERPOWERED here: the difficulty or co-practice explanation is not excluded.
FOR PAPER 1  fixed now:
               CURRICULUM-LINKED       the pairs may be called "prerequisite-like candidates
                                       consistent with expert curriculum": they are skills the
                                       expert taxonomy places together, beyond what difficulty gap
                                       and co-practice explain. Still not edges: neither the pair
                                       statistic nor containment orients a pair (taxonomy-order
                                       found the taxonomy INERT for order), and a trait shared by
                                       two taxonomically adjacent skills fits too.
               NOT CURRICULUM-LINKED   leans toward the shared-trait reading: the pairs are not where
                                       the curriculum puts related skills. (Not reachable here.)
               UNDERPOWERED            no reading: Paper 1 may not cite the taxonomy for or against
                                       the pairs, and keeps IITA-PAIRSCAN's wording.
             R2 unreadable is reported in every case: the taxonomy offers no route order among these
             sets' skills, so the brief's "routed before" relation cannot be asked here.

DIRECTION: iita_pairscan's (i, j) means i is the prerequisite of j (b_ij counts learners who mastered
j but not i); the curricular orientation is ancestor -> descendant along a kc_route ("general before
specific", per XES3G5M's kc_routes, routes run root -> leaf, codebook xes3g5m and taxonomy.py). The
verdict is symmetric in each pair; only the ORIENTATION block reads direction, through
shared.direction.reversed_arrow, and it is never verdict-bearing.

CHANGES FORCED BY THE SYNTHETIC RUN (before any comparison)
  1. CONTROL strata |db| half x n_both half -> |db| quintile x n_both half. In a synthetic confound
     world (flags chosen for small difficulty gap, the gap tied to hierarchy distance: u + N(0,
     0.15), no planted link) of strength kappa = 4, which makes the unstratified R3 test fire in 95%
     of replicates (the size of the MDE effect), the 2 x 2 strata still fired in 37%, residual
     confounding from coarse bins. Exploratory comparison, 500 replicates (R3 at kappa 2 / 4 / 8;
     random-label R1 / R3 rate; power R1 x = 0.3 / R3 kappa = 3):
       |db| 2 x n_both 2   0.15 / 0.34 / 0.75   0.018 / 0.056   0.86 / 0.83
       |db| 3 x n_both 2   0.08 / 0.17 / 0.36   0.015 / 0.056   0.82 / 0.84
       |db| 5 x n_both 2   0.06 / 0.10 / 0.18   0.011 / 0.053   0.81 / 0.81   (kept)
       |db| 4 x n_both 3   0.07 / 0.14 / 0.25   0.011 / 0.052   0.77 / 0.81
       |db| 5 alone        0.06 / 0.10 / 0.19   0.017 / 0.052   0.83 / 0.85
       |db| 7 alone        0.05 / 0.08 / 0.11   0.012 / 0.069   0.83 / 0.84
     Quintiles cost ~5 points of power and keep n_both in the control; seven bins alone drift above
     nominal on random labels (~7 pairs a stratum).

SYNTHETIC RESULTS (--validate; synthetic flagged labels on the real sets' structure; real flags not
read). Final design.
  random labels   2000 replicates, each set's real flagged count: rejection at 0.05, unstratified /
                  CONTROL: R1 0.026 / 0.010 (conservative: a count with expectation 0.29 is
                  discrete), R3 0.053 / 0.051; |db|, n_both and expected-discordance terciles 0.017-
                  0.054. Mean effect R1 -0.001, R3 +0.006.
  planted link    flags on adjacent pairs with probability x (R1) or drawn with weight exp(-kappa u)
                  (R3), power unstratified / CONTROL at 0.05:
                    R1 x = 0.10 +0.08 0.35 / 0.21   x = 0.20 +0.17 0.70 / 0.54   x = 0.30 +0.27 0.91 / 0.80
                       x = 0.40 +0.36 0.98 / 0.95
                    R3 kappa 1 -0.08 0.26 / 0.22   kappa 2 -0.15 0.62 / 0.57   kappa 3 -0.21 0.87 / 0.82
                       kappa 4 -0.26 0.98 / 0.96
                  every flag adjacent where the set allows: R1 and R3 detected in 1000 of 1000.
  confound        flags chosen by the REAL |db| (kappa 2 / 4 / 8): unstratified R3 0.065 / 0.066 /
                  0.052, R1 0.015-0.025. In these sets distance is nearly independent of difficulty
                  gap (|rho| <= 0.29), so a difficulty-driven flag cannot fake a link here.
                  Synthetic gap tied to distance (kappa 2 / 4 / 8): unstratified R3 0.55 / 0.95 /
                  1.00, CONTROL 0.055 / 0.091 / 0.18; R1 0.09 / 0.20 / 0.44, CONTROL 0.02 / 0.03 /
                  0.08. Against a confound the size of the MDE the control leaves ~9% where 5% is
                  nominal; it is a strong confound (rho ~0.9) the real sets do not carry.

ORDER        load (hash checks) -> positivity -> [--validate: critical values, synthetic labels,
             MDE -> out/pairscan-curriculum-synthetic.json] -> committed by the maintainer -> the
             comparison reads the flags, the MDE from the committed synthetic file, and writes
             out/pairscan-curriculum.json with the verdict.

    python3 pairscan_curriculum.py --validate   # phase 1: out/pairscan-curriculum-synthetic.json (~1.5 min)
    python3 pairscan_curriculum.py              # phase 2: out/pairscan-curriculum.json, the verdict
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
import time
import zlib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
import iita_dense as dense  # noqa: E402  (surmise_graphs' loader and mastery table)
import iita_pairscan as ps  # noqa: E402  (the committed scan rule and expected counts)
from shared.direction import reversed_arrow  # noqa: E402
from shared.paths import data_path  # noqa: E402
from shared.stats import rank, spearman  # noqa: E402

SEED = 20260927
PAIRSCAN = HERE / "out" / "iita-pairscan.json"
PAIRSCAN_SHA256 = "8bcaa5cfb168651c53680fbf90c0248930e10876b8833e92ecce0d7153da139c"   # as committed at 1dfb78c
ROUTES_MD5 = "f381243566f9da16c29ff237b0233557"                                         # data/data-sources.json
OUT = HERE / "out" / "pairscan-curriculum.json"
OUT_SYN = HERE / "out" / "pairscan-curriculum-synthetic.json"

N_PERM = 10_000             # within-set permutations per test
ALPHA = 0.05                # familywise, Holm over the readable relations
POWER = 0.8                 # power at which the MDE is read
MEANINGFUL = {"R1": 0.10, "R2": 0.10, "R3": 0.10}   # smallest enrichment worth a reading (docstring)
N_FPR = 2000                # random-label replicates in the validation
N_SIM = 1000                # replicates per point of a power curve
R_GRID = (0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.60)
KAPPA_GRID = (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0)

RELATIONS = ("R1", "R2", "R3")
TAIL = {"R1": "upper", "R2": "upper", "R3": "lower"}     # enrichment = more adjacent / closer
CONTROL = "control"                                       # verdict-bearing: set x |db| quintile x n_both half
SCHEMES = ("set", CONTROL, "db3", "nb3", "ed3")
LINKED, NOT_LINKED, UNDERPOWERED = "CURRICULUM-LINKED", "NOT CURRICULUM-LINKED", "UNDERPOWERED"


# ----------------------------------------------------------------------------- inputs

def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_routes() -> dict[str, tuple[str, ...]]:
    p = data_path("XES_DIR") / "cid2route.json"
    if hashlib.md5(p.read_bytes()).hexdigest() != ROUTES_MD5:
        raise SystemExit(f"{p} is not the registered cid2route.json (md5 {ROUTES_MD5})")
    return {k: tuple(v) for k, v in json.loads(p.read_text(encoding="utf-8")).items()}


def lcp(a: tuple, b: tuple) -> int:
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


def relate(x: str, y: str, routes) -> tuple[bool, bool, int, float]:
    """(R1, R2, R2 orientation, R3) for skills x, y; a compound skill 'a_b' is every KC it names.

    R1  some component pair is the same KC, the same route, siblings (same parent) or parent-child.
    R2  some component pair is ancestor-descendant (one route a proper prefix of the other).
        Orientation +1 if x holds the ancestor, -1 if y does, 0 if the component pairs disagree.
    R3  the smallest tree path length over component pairs: len(ra) + len(rb) - 2 lcp(ra, rb), roots
        joined at a virtual super-root; nan if no component pair has two routes.
    """
    r1 = r2 = False
    ori, d = set(), np.inf
    for p in x.split("_"):
        for q in y.split("_"):
            if p not in routes or q not in routes:
                continue
            ra, rb = routes[p], routes[q]
            n = lcp(ra, rb)
            d = min(d, 0 if p == q else len(ra) + len(rb) - 2 * n)
            if p == q or ra == rb or ra[:-1] == rb[:-1] or ra == rb[:-1] or rb == ra[:-1]:
                r1 = True
            if len(ra) < len(rb) and n == len(ra):
                r2 = True
                ori.add(1)
            elif len(rb) < len(ra) and n == len(rb):
                r2 = True
                ori.add(-1)
    return r1, r2, (ori.pop() if len(ori) == 1 else 0), (float(d) if np.isfinite(d) else np.nan)


def co_attempts(skill_sets: list[list[str]]) -> list[dict]:
    """n_both per unordered pair: learners with a mastery state on both skills, corpus-wide."""
    state = dense.sg.mastery(dense.sg.xes3g5m())
    out = []
    for sk in skill_sets:
        users = {c: set(state[c]) for c in sk}
        out.append({(i, j): len(users[sk[i]] & users[sk[j]]) for i, j in itertools.combinations(range(len(sk)), 2)})
    return out


def within_rank(x: np.ndarray) -> np.ndarray:
    """Normalised mid-rank in (0, 1) within a set; its mean over the set is exactly 0.5."""
    return (rank(x) - 0.5) / len(x)


def load_sets(routes, read_labels: bool) -> tuple[list[dict], dict]:
    """The scored XES3G5M sets as units: eligible unordered pairs, relations, covariates, flags.

    With read_labels False (the validation) a set carries only its COUNT of flagged pairs; which
    pairs they are is never stored. Significant pairs are read by identity only to count unordered
    pairs and drop CLUSTERED ones, never related to the hierarchy.
    """
    if sha256(PAIRSCAN) != PAIRSCAN_SHA256:
        raise SystemExit(f"{PAIRSCAN} differs from the output committed at 1dfb78c")
    run = json.loads(PAIRSCAN.read_text())
    corpus = next(c for c in run["corpora"] if c["corpus"] == "xes3g5m")
    rows = [r for r in corpus["sets"] if r["fit_converged"] and "pairs" in r]
    if len(rows) != corpus["scored"]:
        raise SystemExit("scored-set count does not match the committed run")
    nb_all = co_attempts([r["skills"] for r in rows])
    sets, audit = [], []
    for r, nb in zip(rows, nb_all):
        sk, a, b = r["skills"], np.array(r["a"]), np.array(r["b"])
        th = (a, -a * b, r["g"], r["l"])
        E = ps.expected(th, r["learners"])
        scan = ps.OFF & (E >= ps.MIN_EXPECTED)
        pos = {s: k for k, s in enumerate(sk)}
        sig = {}
        for p in r["pairs"]:
            key = tuple(sorted((pos[p["prereq"]], pos[p["dependant"]])))
            sig.setdefault(key, []).append(p)
        flagged = {k for k, ps_ in sig.items() if any(p["isolated"] for p in ps_)}
        clustered = set(sig) - flagged
        units = [(i, j) for i, j in itertools.combinations(range(len(sk)), 2)
                 if (scan[i, j] or scan[j, i]) and (i, j) not in clustered]
        rel = [relate(sk[i], sk[j], routes) for i, j in units]
        dist = np.array([t[3] for t in rel])
        if np.isnan(dist).any():
            raise SystemExit(f"set {r['set']}: a pair has no route; the pre-registration has no rule for it")
        db = np.array([abs(b[i] - b[j]) for i, j in units])
        nboth = np.array([nb[u] for u in units], dtype=float)
        edisc = np.array([E[i, j] + E[j, i] for i, j in units])
        s = dict(set=r["set"], skills=sk, b=b, units=units, learners=r["learners"],
                 r1=np.array([t[0] for t in rel], float), r2=np.array([t[1] for t in rel], float),
                 r2dir=np.array([t[2] for t in rel]), dist=dist, u3=within_rank(dist),
                 db=db, nboth=nboth, edisc=edisc, n_flag=len(flagged))
        s["strata"] = strata(s)
        if read_labels:
            s["flagged"] = np.array([u in flagged for u in units])
            s["sig"] = {u: sig[u] for u in flagged}
        sets.append(s)
        audit.append(dict(set=r["set"], learners=r["learners"], eligible=len(units),
                          unordered_total=len(sk) * (len(sk) - 1) // 2,
                          scanned_committed=r["scanned"], scanned_reconstructed=int(scan.sum()),
                          clustered_dropped=len(clustered), flagged=len(flagged),
                          compound_skills=sum("_" in k for k in sk),
                          r1=int(s["r1"].sum()), r2=int(s["r2"].sum()),
                          dist_median=float(np.median(dist)), dist_min=float(dist.min()),
                          rho_dist_db=round(spearman(dist, db), 3),
                          rho_dist_nboth=round(spearman(dist, nboth), 3),
                          rho_dist_edisc=round(spearman(dist, edisc), 3)))
    return sets, dict(pairscan_sha256=PAIRSCAN_SHA256, routes_md5=ROUTES_MD5, per_set=audit)


def strata(s: dict) -> dict[str, np.ndarray]:
    """Within-set strata for each permutation scheme: equal-count bins of within-set mid-ranks.

    CONTROL is |db| quintile x n_both half (10 strata of ~10 pairs; CHANGE 1).
    """
    def bins(x, k):
        return np.minimum((k * within_rank(x)).astype(int), k - 1)
    n = len(s["units"])
    return {"set": np.zeros(n, int), CONTROL: 2 * bins(s["db"], 5) + bins(s["nboth"], 2),
            "db3": bins(s["db"], 3), "nb3": bins(s["nboth"], 3), "ed3": bins(s["edisc"], 3)}


# ----------------------------------------------------------------------------- the permutation test

class Null:
    """Within-set (x stratum) permutation null of a sum over flagged units, cached by composition.

    The flagged count in every set x stratum is held fixed; each component is the sum of f units
    drawn without replacement from that stratum, N_PERM times. Components are cached, so the
    validation's replicates share null draws; the real run computes each once from its own seed.
    """

    def __init__(self, n_perm: int = N_PERM):
        self.n_perm, self.comp, self.total = n_perm, {}, {}

    def component(self, key: tuple, values: np.ndarray, f: int) -> np.ndarray:
        k = key + (f,)
        if k not in self.comp:
            rng = np.random.default_rng([SEED, zlib.crc32(repr(k).encode())])
            idx = rng.random((self.n_perm, len(values))).argsort(axis=1)[:, :f]
            self.comp[k] = values[idx].sum(1)
        return self.comp[k]

    def dist(self, sets, rel: str, scheme: str, flags: list[np.ndarray]) -> np.ndarray:
        comp = []
        for s, fl in zip(sets, flags):
            st = s["strata"][scheme]
            for g in np.unique(st[fl]):
                comp.append((s["set"], g, int((fl & (st == g)).sum())))
        key = (rel, scheme, tuple(comp))
        if key not in self.total:
            tot = np.zeros(self.n_perm)
            byset = {s["set"]: s for s in sets}
            for sid, g, f in comp:
                s = byset[sid]
                st = s["strata"][scheme]
                tot += self.component((rel, scheme, sid, int(g)), values(s, rel)[st == g], f)
            self.total[key] = tot
        return self.total[key]


def values(s: dict, rel: str) -> np.ndarray:
    return {"R1": s["r1"], "R2": s["r2"], "R3": s["u3"]}[rel]


def test(sets, rel: str, scheme: str, flags: list[np.ndarray], null: Null) -> dict:
    """One-sided within-set permutation test of relation `rel` among flagged pairs.

    Statistic: the sum over flagged pairs of R1 / R2 (a count) or of R3's within-set distance rank.
    Enrichment is signed: more R1 / R2 (upper tail) or smaller distance rank (lower tail).
    effect = flagged mean minus the permutation mean of the same (a rate difference for R1 / R2, a
    rank shift for R3; positive = enriched for R1 / R2, negative = closer for R3).
    """
    F = int(sum(f.sum() for f in flags))
    obs = float(sum(values(s, rel)[f].sum() for s, f in zip(sets, flags)))
    d = null.dist(sets, rel, scheme, flags)
    tol = 1e-9
    k = (d >= obs - tol).sum() if TAIL[rel] == "upper" else (d <= obs + tol).sum()
    return dict(flagged=F, observed=obs / F, expected=float(d.mean()) / F, effect=(obs - d.mean()) / F,
                p=float((1 + k) / (len(d) + 1)))


def holm(ps_: dict[str, float], alpha: float = ALPHA) -> dict[str, bool]:
    out, m = {}, len(ps_)
    for step, (rel, p) in enumerate(sorted(ps_.items(), key=lambda t: t[1])):
        if p >= alpha / (m - step):
            out.update({r: False for r in ps_ if r not in out})
            break
        out[rel] = True
    return out


def best_case_p(sets, rel: str, null: Null) -> float:
    """Positivity: p if every set's flags sat on its most extreme pairs for `rel`."""
    flags = []
    for s in sets:
        v = values(s, rel)
        order = np.argsort(-v if TAIL[rel] == "upper" else v, kind="mergesort")
        f = np.zeros(len(v), bool)
        f[order[:s["n_flag"]]] = True
        flags.append(f)
    return test(sets, rel, "set", flags, null)["p"]


# ----------------------------------------------------------------------------- synthetic labels

def gumbel_top(rng, logw: np.ndarray, f: int) -> np.ndarray:
    """f units without replacement, P proportional to exp(logw) at each draw (Gumbel top-k)."""
    m = np.zeros(len(logw), bool)
    if f:
        m[np.argsort(-(logw + rng.gumbel(size=len(logw))), kind="mergesort")[:f]] = True
    return m


def plant(rng, sets, kind: str, x: float = 0.0, cov: str = "db") -> list[np.ndarray]:
    """Synthetic flagged labels with each set's real flagged count.

    random     uniform: the null is true.
    r1         each flag is an R1 pair with probability x (while R1 pairs remain), else a non-R1 pair.
    r3         flags drawn with weight exp(-x * distance rank): planted closeness.
    confound   flags drawn with weight exp(-x * rank of cov) with cov a covariate: 'db' (similar
               difficulty), or 'syn', a synthetic difficulty gap tied to hierarchy distance
               (u3 + N(0, 0.15)), so the confound is as strong as the relation.
    """
    out = []
    for s in sets:
        n, f = len(s["units"]), s["n_flag"]
        if kind == "random":
            out.append(gumbel_top(rng, np.zeros(n), f))
        elif kind == "r1":
            pos, neg = np.flatnonzero(s["r1"] == 1), np.flatnonzero(s["r1"] == 0)
            k = min(rng.binomial(f, x), len(pos))
            m = np.zeros(n, bool)
            m[rng.choice(pos, k, replace=False)] = True
            m[rng.choice(neg, f - k, replace=False)] = True
            out.append(m)
        elif kind == "r3":
            out.append(gumbel_top(rng, -x * s["u3"], f))
        elif kind == "confound":
            c = s["db"] if cov == "db" else s["syn"]
            out.append(gumbel_top(rng, -x * within_rank(c), f))
    return out


def with_synthetic_gap(sets, rng) -> list[dict]:
    """Copies of the sets whose |db| is replaced by a gap tied to distance, strata rebuilt."""
    out = []
    for s in sets:
        t = dict(s)
        t["syn"] = t["db"] = s["u3"] + rng.normal(0, 0.15, len(s["u3"]))
        t["strata"] = strata(t)
        out.append(t)
    return out


def reject_rate(sets, kind, x, rels, schemes, null, reps, seed_key, cov="db", level=ALPHA) -> dict:
    rng = np.random.default_rng([SEED, *seed_key])
    hits = {(r, sc): 0 for r in rels for sc in schemes}
    eff = {r: [] for r in rels}
    for _ in range(reps):
        flags = plant(rng, sets, kind, x, cov)
        for r in rels:
            for sc in schemes:
                t = test(sets, r, sc, flags, null)
                hits[(r, sc)] += t["p"] < level
                if sc == "set":
                    eff[r].append(t["effect"])
    return {f"{r}/{sc}": hits[(r, sc)] / reps for r, sc in hits} | \
           {f"{r}/effect": float(np.mean(eff[r])) for r in rels if eff[r]}


def power_curve(sets, rel, grid, null, level, reps=N_SIM) -> list[dict]:
    kind = "r1" if rel == "R1" else "r3"
    rows = []
    for x in grid:
        rr = reject_rate(sets, kind, x, [rel], ["set", CONTROL], null, reps, (1, zlib.crc32(f"{rel}{x}{level}".encode())),
                         level=level)
        rows.append(dict(x=x, effect=round(rr[f"{rel}/effect"], 4), power=rr[f"{rel}/set"],
                         power_control=rr[f"{rel}/{CONTROL}"]))
    return rows


def mde(rows, key: str) -> float | None:
    """The smallest planted effect whose power reaches POWER; None if no grid point does."""
    hit = [abs(r["effect"]) for r in rows if r[key] >= POWER]
    return round(min(hit), 4) if hit else None


def critical_values(sets, readable, null) -> dict:
    """The flagged-pair statistic each readable relation needs, at ALPHA and at the Holm first level.

    R1: the smallest count of adjacent flagged pairs with p below the level; R3: the largest mean
    within-set distance rank of the flagged pairs with p below it. Primary (within-set) null.
    """
    rng = np.random.default_rng([SEED, 6])
    flags = plant(rng, sets, "random")                  # only the per-set counts matter to this null
    F = sum(s["n_flag"] for s in sets)
    out = {}
    for rel in readable:
        d = null.dist(sets, rel, "set", flags)
        for name, lv in (("alpha", ALPHA), ("holm_first", ALPHA / max(len(readable), 1))):
            if rel == "R1":
                k = next((k for k in range(F + 1) if (1 + (d >= k - 1e-9).sum()) / (len(d) + 1) < lv), None)
                out[f"{rel}@{name}"] = dict(count=k, of=F, expected=round(float(d.mean()), 3))
            else:
                v = np.sort(d)
                i = int(np.floor(lv * (len(d) + 1))) - 2
                out[f"{rel}@{name}"] = dict(mean_rank=round(float(v[max(i, 0)]) / F, 4), expected=round(float(d.mean()) / F, 4))
    return out


def validate(sets, readable: list[str], log) -> dict:
    null = Null()
    m = max(len(readable), 1)
    out = dict(readable=readable, holm_first_level=ALPHA / m)
    t0 = time.time()
    out["random_labels"] = reject_rate(sets, "random", 0, readable, SCHEMES, null, N_FPR, (0,))
    out["random_labels_at_holm_first"] = reject_rate(sets, "random", 0, readable, ["set", CONTROL], null, N_FPR, (0,),
                                                     level=ALPHA / m)
    out["critical"] = critical_values(sets, readable, null)
    log(f"critical values: {out['critical']}")
    log(f"random labels ({N_FPR} replicates): {out['random_labels']}  [{time.time() - t0:.0f}s]")
    out["power"], out["mde"] = {}, {}
    for rel in readable:
        grid = R_GRID if rel == "R1" else KAPPA_GRID
        for lv_name, lv in (("alpha", ALPHA), ("holm_first", ALPHA / m)):
            rows = power_curve(sets, rel, grid, null, lv)
            out["power"][f"{rel}@{lv_name}"] = rows
            out["mde"][f"{rel}@{lv_name}"] = dict(primary=mde(rows, "power"), control=mde(rows, "power_control"))
            log(f"{rel} power at {lv:.3f}: " + "; ".join(f"x={r['x']} eff={r['effect']:+.3f} "
                                                          f"pw={r['power']:.2f}/{r['power_control']:.2f}" for r in rows))
    # all flags on curriculum-adjacent pairs where the set has enough of them
    out["all_adjacent"] = reject_rate(sets, "r1", 1.0, readable, ["set", CONTROL], null, N_SIM, (2,))
    log(f"all flags R1 where possible: {out['all_adjacent']}")
    # confound worlds: flags chosen by covariate, no planted relation
    out["confound_real_db"] = {str(k): reject_rate(sets, "confound", k, readable, ["set", CONTROL, "db3"], null, N_SIM,
                                                   (3, int(10 * k))) for k in (2.0, 4.0, 8.0)}
    log(f"confound (real |db|): {out['confound_real_db']}")
    syn = with_synthetic_gap(sets, np.random.default_rng([SEED, 4]))
    null_syn = Null()
    out["confound_synthetic_gap"] = {str(k): reject_rate(syn, "confound", k, readable, ["set", CONTROL, "db3"], null_syn,
                                                         N_SIM, (5, int(10 * k)), cov="syn") for k in (2.0, 4.0, 8.0)}
    log(f"confound (gap tied to distance): {out['confound_synthetic_gap']}")
    out["seconds"] = round(time.time() - t0, 1)
    return out


# ----------------------------------------------------------------------------- the real comparison

def orientation(sets) -> dict:
    """R2 pairs: curricular order (ancestor -> descendant) against the z orientation and difficulty.

    z orientation: the ordered pair (i, j) with the more negative z (i the claimed prerequisite, per
    iita_pairscan). Difficulty order: easier (lower fitted b) -> harder. Baseline: curriculum against
    difficulty over every eligible R2 pair in the 15 sets, flagged or not.
    """
    flagged, base = [], []
    for s in sets:
        for k, (i, j) in enumerate(s["units"]):
            if not s["r2"][k] or s["r2dir"][k] == 0:
                continue
            cur = (i, j) if s["r2dir"][k] == 1 else (j, i)
            easy = (i, j) if s["b"][i] < s["b"][j] else (j, i)
            base.append((cur, easy))
            if s["flagged"][k]:
                recs = s["sig"][(i, j)]
                r = min(recs, key=lambda p: min(p["z"], p["z_reverse"]))
                pi, pj = s["skills"].index(r["prereq"]), s["skills"].index(r["dependant"])
                zo = (pi, pj) if r["z"] <= r["z_reverse"] else (pj, pi)
                flagged.append((cur, zo, easy))

    def agree(pairs):
        return lambda edges: (float(np.mean([p in edges for p in pairs])) if pairs else float("nan"))

    cur_f = [c for c, _, _ in flagged]
    res = dict(n_flagged_r2=len(flagged), n_all_r2=len(base))
    res["z_vs_curriculum"] = reversed_arrow(agree([z for _, z, _ in flagged]), cur_f)
    res["difficulty_vs_curriculum_flagged"] = reversed_arrow(agree([e for _, _, e in flagged]), cur_f)
    res["z_vs_difficulty_flagged"] = float(np.mean([z == e for _, z, e in flagged])) if flagged else None
    res["difficulty_vs_curriculum_all"] = reversed_arrow(agree([e for _, e in base]), [c for c, _ in base])
    disc = [(c, z) for c, z, e in flagged if z != e]
    res["discordant_z_vs_difficulty"] = dict(n=len(disc), curriculum_agrees_with_z=sum(c == z for c, z in disc))
    return res


def compare(sets, readable: list[str], mdes: dict, log) -> dict:
    null = Null()
    flags = [s["flagged"] for s in sets]
    tests = {f"{r}/{sc}": test(sets, r, sc, flags, null) for r in RELATIONS for sc in SCHEMES}
    for k, v in tests.items():
        log(f"  {k:12s} observed {v['observed']:.3f} expected {v['expected']:.3f} effect {v['effect']:+.3f} p {v['p']:.4f}")
    prim = holm({r: tests[f"{r}/set"]["p"] for r in readable}) if readable else {}
    ctrl = holm({r: tests[f"{r}/{CONTROL}"]["p"] for r in readable}) if readable else {}
    passes = [r for r in readable if prim.get(r) and ctrl.get(r)]
    powered = [r for r in readable if mdes.get(r) is not None and mdes[r] <= MEANINGFUL[r]]
    if passes:
        verdict, reason = LINKED, f"{', '.join(passes)} enriched, surviving the {CONTROL} stratification"
    elif powered:
        verdict, reason = NOT_LINKED, (f"no readable relation passes; {', '.join(powered)} could see the "
                                       f"meaningful enrichment")
    else:
        verdict, reason = UNDERPOWERED, "no readable relation passes and none is powered for a meaningful enrichment"
    if not passes and any(prim.values()):
        reason += f"; primary-only pass (not surviving the control): {[r for r in prim if prim[r]]}"
    desc = {}
    for cov in ("db", "nboth", "edisc"):
        fl = np.concatenate([s[cov][s["flagged"]] for s in sets])
        co = np.concatenate([s[cov][~s["flagged"]] for s in sets if s["n_flag"]])
        desc[cov] = dict(flagged_median=float(np.median(fl)), comparison_median=float(np.median(co)))
    comp_rates = {r: float(np.concatenate([values(s, r)[~s["flagged"]] for s in sets if s["n_flag"]]).mean())
                  for r in ("R1", "R2")}
    return dict(tests=tests, holm_primary=prim, holm_control=ctrl, readable=readable, powered=powered,
                verdict=verdict, reason=reason, comparison_rates_in_flag_sets=comp_rates,
                covariates=desc, orientation=orientation(sets))


# ----------------------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true",
                    help="positivity, MDE and synthetic-label validation; never reads which pairs were flagged")
    a = ap.parse_args()
    log = lambda m: print(m, flush=True)                                          # noqa: E731
    routes = load_routes()
    t0 = time.time()
    sets, audit = load_sets(routes, read_labels=not a.validate)
    log(f"{len(sets)} sets, {sum(s['n_flag'] for s in sets)} flagged pairs in "
        f"{sum(s['n_flag'] > 0 for s in sets)} sets; loaded in {time.time() - t0:.0f}s")
    for row in audit["per_set"]:
        log("  " + " ".join(f"{k}={v}" for k, v in row.items()))
    positivity_null = Null()
    best = {r: best_case_p(sets, r, positivity_null) for r in RELATIONS}
    n_pos = {r: int(sum(values(s, r)[:].sum() for s in sets if s["n_flag"])) for r in ("R1", "R2")}
    readable = [r for r in RELATIONS if best[r] < ALPHA / len(RELATIONS)]
    log(f"positivity: best-case p {best}; relation-positive pairs in flag sets {n_pos}; readable {readable}")
    head = dict(n_perm=N_PERM, alpha=ALPHA, power=POWER, meaningful=MEANINGFUL, seed=SEED, audit=audit,
                best_case_p=best, relation_positive_in_flag_sets=n_pos, readable=readable,
                flagged_per_set=[s["n_flag"] for s in sets])
    if a.validate:
        res = head | dict(validation=validate(sets, readable, log))
        OUT_SYN.write_text(json.dumps(res, indent=1, default=float))
        log(f"wrote {OUT_SYN}")
        return
    syn = json.loads(OUT_SYN.read_text())
    lv = "holm_first" if len(readable) > 1 else "alpha"
    mdes = {r: syn["validation"]["mde"][f"{r}@{lv}"]["control"] for r in readable}
    res = head | dict(mde_used=mdes, result=compare(sets, readable, mdes, log))
    log(f"VERDICT: {res['result']['verdict']} ({res['result']['reason']})")
    OUT.write_text(json.dumps(res, indent=1, default=float))
    log(f"wrote {OUT}")


if __name__ == "__main__":
    main()
