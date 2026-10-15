"""The within-pair directional contrast, and the controls it is not allowed to run without.

Shared because two corpora now use it (studies/measurement/edmcup-direction/, studies/measurement/assist2012-direction/) and a rule that
lives in one copy is a rule the next caller does not have. Everything corpus-specific -- how the
learner timeline is rebuilt, which published document supplies the direction -- stays in the study.

THE STATISTIC. The repo's drop

    drop(A->B) = mean outcome at B among learners who PASSED A before reaching B
               - mean outcome at B among learners who TOUCHED BUT FAILED A before reaching B

is positive for essentially ANY ordered pair, because learners who pass A are abler; the house
background is about +0.10. A single drop therefore cannot demonstrate direction. The readout is the
WITHIN-PAIR DIRECTIONAL CONTRAST, computed only on pairs seen in BOTH orders:

    delta(A,B) = drop(A->B) - drop(B->A),   A before B in the published structure.

The same two skills carry both terms, so pair difficulty cancels, and general ability cancels to the
extent that it acts equally in both orders. What survives is direction.

An observation row is (learner, passed_A, residual_outcome_B, raw_outcome_B). Index 2 is the
residualised outcome and index 3 the raw one; both are reported so the residualisation can be
audited.

WHAT THE RESIDUAL ACTUALLY IS, because calling it an "ability control" overstates how solved it is.
Subtracting a learner's mean over their OTHER cells is a proxy for UNOBSERVED UPSTREAM
PREREQUISITES -- the fluency taught before the record opens, never assessed, which raises performance
at BOTH ends of every pair and so makes drop(A->B) read as structure while partly being that. It is
the only handle this programme has on that confound and its adequacy is an open question, not a
settled nuisance adjustment. See docs/specs/ESTIMAND.md section 4. The empirical handle is the `strata` argument
below: flat across curricular distance means the residual is doing its job, climbing means it is not.
Printed labels and JSON keys still say "ability-residualised"; they were left alone so artefacts
committed before 2026-09-23 stay comparable.

WHAT THE CONTROLS ARE FOR, each having caught something real:
  floor      A planted gate of known size must be recovered, and an UNPLANTED arm must return ~0.
             Averaged over draws: ONE draw is one sample of a noisy quantity, and a single unplanted
             draw once scored +0.0222 -- over a 0.02 bar, from noise alone.
  deranged   Pass/fail labels deranged within each (pair, direction) stratum -- a derangement, not a
             permutation, since a permutation leaves on average one learner in place. Also averaged
             over draws: a single derangement once moved a headline from -0.0188 to -0.0052.
  shuffled   The direction labels themselves randomised across pairs. This is the null that matters:
             it asks whether the PUBLISHED order does the work, or whether any labelling would score
             as well.
  clustering Learners are nested in classes, so intervals resample whole CLASSES, each drawn copy
             getting its own learner namespace.
The treatment is per learner, so the learner is the unit that gets deranged.

A NULL IS ONLY A FINDING IF THE INSTRUMENT COULD HAVE RESOLVED THE BAR. Where the floor's own
unplanted scatter exceeds the bar, the verdict is UNDERPOWERED AT THE BAR, not NOT RECOVERED.
"""
import collections
import math
import random


class Config:
    def __init__(self, min_cell=10, min_pairs=20, bar=0.02, reps=400, plant=0.15,
                 floor_draws=25, derange_draws=25, seed="20260923"):
        self.min_cell = min_cell
        self.min_pairs = min_pairs
        self.bar = bar
        self.reps = reps
        self.plant = plant
        self.floor_draws = floor_draws
        self.derange_draws = derange_draws
        self.seed = seed


# ------------------------------------------------------- direction from an external position
# THE LAST PIECE OF PER-DATASET PLUMBING IN THE DIRECTION STUDIES (assay-readiness O1). Both
# studies were ordering pairs by an external scale and both had written their own copy of it:
# EDM Cup had grade_of + direction_s1 + make_direction + make_strata, ASSISTments had grade_of +
# make_dir + strata. The two differed only in what supplied the position, and the contract already
# exposes that as corpus.position(). So the ORDERING is shared here and what stays study-side is
# the genuinely corpus-specific part: where a richer position comes from (EDM Cup's publisher scope
# and sequence) and which subset a control restricts to (ASSISTments' exact-name half).
#
# A POSITION IS EITHER AN ORDINAL OR A CONTEXT PLUS AN ORDINAL, and the distinction is the reason
# these are not one line. A CCSS grade is comparable everywhere: grade 5 precedes grade 6 whoever
# published it. A module number is comparable only WITHIN a course -- module 2 of one publisher's
# course says nothing about module 3 of another's -- so a tuple position is read as
# (context..., ordinal) and pairs whose contexts differ are declined rather than ordered wrongly.
# That guard is not decoration: without it the EDM Cup module structure would have ordered pairs
# across publishers, which is a comparison the published documents do not license.

def _split(p):
    """(context, ordinal). A bare value is an ordinal with no context; a tuple's last element is
    the ordinal and everything before it is the context that must match."""
    return (p[:-1], p[-1]) if isinstance(p, tuple) else ((), p)


def positions_for(corpus, units, allowed=None):
    """{unit: position} from corpus.position() over an explicit unit set, Nones dropped.

    None is the contract's real answer for "this corpus has no external scale here", so an
    unpositioned unit is ABSENT rather than carrying a placeholder that would sort somewhere. The
    unit vocabulary comes from the study's own cell set, which it already holds, so this never
    re-reads the corpus. `allowed` restricts to a control's subset."""
    # SORTED, so the returned dict's order does not depend on PYTHONHASHSEED. Nothing downstream
    # currently iterates it, and that is exactly the kind of thing that changes underneath you:
    # cluster_ci in this same module was non-deterministic for precisely this reason until its
    # members were sorted once.
    out = {}
    for u in sorted(units):
        if allowed is not None and u not in allowed:
            continue
        p = corpus.position(u)
        if p is not None:
            out[u] = p
    return out


def by_position(pos):
    """Direction function: order a pair by an external position map, or decline it.

    Declines when either unit is unpositioned, when the contexts differ, or when the ordinals tie --
    a tie is not a direction and ordering it would invent one."""
    def f(a, b):
        pa, pb = pos.get(a), pos.get(b)
        if pa is None or pb is None:
            return None
        ca, oa = _split(pa)
        cb, ob = _split(pb)
        if ca != cb or oa == ob:
            return None
        return (a, b) if oa < ob else (b, a)
    return f


def _gap_key(p):
    """The scalar the gap is measured on. A compound ordinal such as (module, topic, lesson) is
    read at its coarsest level, because that is the grain the distance means something at."""
    _c, o = _split(p)
    return o[0] if isinstance(o, tuple) else o


def position_strata(pos, label, cap=3):
    """Bucket pairs by how far apart the external scale places them.

    DISTAL REACH: if a real dependency can sit further back than the corpus observes, near and far
    pairs should not behave alike, and this is where that would show. It is also the empirical
    handle on the ability residual -- flat across distance means it is doing its job."""
    def f(pair):
        a, b = pair[0]
        pa, pb = pos.get(a), pos.get(b)
        if pa is None or pb is None:
            return "%s unknown" % label
        gap = abs(_gap_key(pa) - _gap_key(pb))
        return "%s %d" % (label, gap) if gap <= cap else "%s %d+" % (label, cap + 1)
    return f


# ---------------------------------------------------------------- estimator

def drop(rows, idx):
    p = [r[idx] for r in rows if r[1]]
    f = [r[idx] for r in rows if not r[1]]
    if not p or not f:
        return None
    return sum(p) / len(p) - sum(f) / len(f)


def cells_ok(rows, min_cell):
    p = sum(1 for r in rows if r[1])
    return p >= min_cell and (len(rows) - p) >= min_cell


def select(obs, direction, min_cell):
    """both-order pairs whose direction the published structure knows, passing positivity."""
    pairs, drops = [], collections.Counter()
    seen = set()
    for (a, b) in obs:
        if (b, a) not in obs or (a, b) in seen or (b, a) in seen:
            continue
        seen.add((a, b))
        d = direction(a, b)
        if d is None:
            drops["no direction"] += 1
            continue
        fwd, bwd = d, (d[1], d[0])
        if not (cells_ok(obs[fwd], min_cell) and cells_ok(obs[bwd], min_cell)):
            drops["positivity"] += 1
            continue
        pairs.append((fwd, bwd))
    return pairs, drops


def delta(obs, pairs, idx, flip=None):
    """weighted mean within-pair contrast. flip[i] reverses pair i's direction label."""
    num = den = 0.0
    for i, (fwd, bwd) in enumerate(pairs):
        f, b = (bwd, fwd) if (flip and flip[i]) else (fwd, bwd)
        df, db = drop(obs[f], idx), drop(obs[b], idx)
        if df is None or db is None:
            continue
        w = min(len(obs[f]), len(obs[b]))
        num += w * (df - db)
        den += w
    return num / den if den else float("nan")


def derange(rows, rng):
    """deranged pass/fail labels: no learner keeps their own. Family-matched -- the derangement
    happens INSIDE one (pair, direction) stratum, so the marginal pass rate and the outcome
    distribution are both preserved exactly and only the learner link is broken."""
    n = len(rows)
    if n < 2:
        return rows
    idx = list(range(n))
    for _ in range(200):
        rng.shuffle(idx)
        if all(i != j for i, j in enumerate(idx)):
            break
    else:
        idx = idx[1:] + idx[:1]
    return [(rows[i][0], rows[idx[i]][1], rows[i][2], rows[i][3]) for i in range(n)]


def deranged_obs(obs, pairs, rng):
    out = {}
    for fwd, bwd in pairs:
        out[fwd] = derange(obs[fwd], rng)
        out[bwd] = derange(obs[bwd], rng)
    return out


def cluster_ci(obs, pairs, cls, idx, rng, reps):
    """resample whole CLASSES. Each drawn copy gets its own learner namespace, or the per-learner
    aggregation silently collapses the duplicates back into one."""
    members = collections.defaultdict(set)
    for (a, b) in pairs:
        for p in (a, b):
            for r in obs[p]:
                members[cls.get(r[0], "?")].add(r[0])
    # Sorted ONCE into lists. Iterating the sets directly leaves the accumulation order of the
    # bootstrap at the mercy of PYTHONHASHSEED, which made two runs of identical code disagree in the
    # last decimal place of every CI endpoint -- harmless in magnitude, but a seeded run that does not
    # reproduce is a provenance problem, and this repo has been bitten by those today already.
    members = {c: sorted(v) for c, v in members.items()}
    classes = sorted(members)
    bystu = collections.defaultdict(lambda: collections.defaultdict(list))
    for (a, b) in pairs:
        for p in (a, b):
            for r in obs[p]:
                bystu[r[0]][p].append(r)
    vals = []
    for _ in range(reps):
        draw = [classes[rng.randrange(len(classes))] for _ in classes]
        rep = collections.defaultdict(list)
        for copy, c in enumerate(draw):
            for s in members[c]:
                tag = "%s#%d" % (s, copy)
                for p, rows in bystu[s].items():
                    for r in rows:
                        rep[p].append((tag,) + r[1:])
        vals.append(delta(rep, pairs, idx))
    vals = [v for v in vals if not math.isnan(v)]
    vals.sort()
    if len(vals) < 20:
        return None, None
    return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals))]


def synthetic(pairs, obs, rng, gate):
    """synthetic learners shaped like the real selection: same pairs, same cell counts, same
    marginal pass rates. A gate of size `gate` is planted on the FORWARD direction only."""
    sim = {}
    for fwd, bwd in pairs:
        for p, planted in ((fwd, gate), (bwd, 0.0)):
            real = obs[p]
            rate = sum(1 for r in real if r[1]) / len(real)
            rows = []
            for j in range(len(real)):
                passed = rng.random() < rate
                base = rng.gauss(0.0, 0.30)
                y = base + (planted if passed else 0.0)
                rows.append(("sim%d" % j, passed, y, y))
            sim[p] = rows
    return sim


# ---------------------------------------------------------------- one structure, end to end

def run_structure(name, blurb, obs, direction, cls, log, cfg, min_cell=None, strata=None):
    """Score one published structure. `strata` optionally maps a (fwd, bwd) pair to a bucket label;
    the contrast is then also reported per bucket, which is how DISTAL PREREQUISITE REACH is
    instrumented -- see the studies' READMEs."""
    min_cell = cfg.min_cell if min_cell is None else min_cell
    # Seeded from the cell's own identity, so a sweep row and the headline run for one setting are
    # the same number, not two draws that happen to share a label.
    rng = random.Random("%s|%d|%s" % (name, min_cell, cfg.seed))
    pairs, drops = select(obs, direction, min_cell)
    log("")
    log("=" * 78)
    log("%s -- %s" % (name, blurb))
    log("  positivity floor              >= %d learners in each of the four cells" % min_cell)
    log("=" * 78)
    log("  both-order pairs offered      %d" % (sum(drops.values()) + len(pairs)))
    log("  dropped, direction unknown    %d" % drops["no direction"])
    log("  dropped, positivity (<%d/cell) %d" % (min_cell, drops["positivity"]))
    log("  pairs surviving               %d" % len(pairs))
    if len(pairs) < cfg.min_pairs:
        log("")
        log("  VERDICT: UNANSWERABLE -- %d surviving pairs, pre-registered floor is %d."
            % (len(pairs), cfg.min_pairs))
        return {"structure": name, "min_cell": min_cell, "pairs": len(pairs),
                "verdict": "UNANSWERABLE", "dropped_no_direction": drops["no direction"],
                "dropped_positivity": drops["positivity"]}
    nobs = sum(len(obs[p]) for pr in pairs for p in pr)
    log("  ordered observations          %d" % nobs)

    log("")
    log("  FLOOR  (%d draws each)" % cfg.floor_draws)
    hits = [delta(synthetic(pairs, obs, rng, cfg.plant), pairs, 2) for _ in range(cfg.floor_draws)]
    nuls = [delta(synthetic(pairs, obs, rng, 0.0), pairs, 2) for _ in range(cfg.floor_draws)]
    hits = [v for v in hits if not math.isnan(v)]
    nuls = [v for v in nuls if not math.isnan(v)]
    f_hit = sum(hits) / len(hits)
    f_nul = sum(nuls) / len(nuls)
    nul_sd = (sum((v - f_nul) ** 2 for v in nuls) / max(1, len(nuls) - 1)) ** 0.5
    hit_sd = (sum((v - f_hit) ** 2 for v in hits) / max(1, len(hits) - 1)) ** 0.5
    log("    planted gate %+.3f          recovered %+.4f +- %.4f" % (cfg.plant, f_hit, hit_sd))
    log("    nothing planted             recovered %+.4f +- %.4f" % (f_nul, nul_sd))
    noise = 2 * nul_sd
    log("    instrument noise (2 sd)     %.4f   <- nothing smaller is claimable" % noise)
    floor_ok = f_hit > cfg.plant * 0.5 and abs(f_nul) < noise
    log("    -> %s" % ("instrument sees the gate, unplanted arm is centred on zero"
                       if floor_ok else "FLOOR FAILURE"))
    if not floor_ok:
        return {"structure": name, "min_cell": min_cell, "pairs": len(pairs),
                "verdict": "FLOOR FAILURE", "floor_planted": f_hit, "floor_null": f_nul,
                "floor_null_sd": nul_sd}

    d_res = delta(obs, pairs, 2)
    d_raw = delta(obs, pairs, 3)
    g_res_d, g_raw_d = [], []
    for _ in range(cfg.derange_draws):
        dr = deranged_obs(obs, pairs, rng)
        v2, v3 = delta(dr, pairs, 2), delta(dr, pairs, 3)
        if not math.isnan(v2):
            g_res_d.append(v2)
        if not math.isnan(v3):
            g_raw_d.append(v3)
    g_res = sum(g_res_d) / len(g_res_d)
    g_raw = sum(g_raw_d) / len(g_raw_d)
    g_sd = (sum((v - g_res) ** 2 for v in g_res_d) / max(1, len(g_res_d) - 1)) ** 0.5
    flips = [[rng.random() < 0.5 for _ in pairs] for _ in range(25)]
    sh = [delta(obs, pairs, 2, f) for f in flips]
    sh = [v for v in sh if not math.isnan(v)]
    sh_mean = sum(sh) / len(sh)
    sh_sd = (sum((v - sh_mean) ** 2 for v in sh) / max(1, len(sh) - 1)) ** 0.5

    lo, hi = cluster_ci(obs, pairs, cls, 2, rng, cfg.reps)
    exc = d_res - g_res

    log("")
    log("  %-28s %9s %9s %9s" % ("", "real", "deranged", "excess"))
    log("  %-28s %+9.4f %+9.4f %+9.4f" % ("delta, ability-residualised", d_res, g_res, exc))
    log("  %-28s %+9.4f %+9.4f %+9.4f" % ("delta, raw outcome", d_raw, g_raw, d_raw - g_raw))
    log("")
    log("  deranged arm spread           +- %.4f over %d derangements" % (g_sd, len(g_res_d)))
    log("  direction labels shuffled     %+.4f +- %.4f over %d draws" % (sh_mean, sh_sd, len(sh)))
    log("  cluster bootstrap 95%% CI      [%+.4f, %+.4f]" % (lo, hi) if lo is not None
        else "  cluster bootstrap 95% CI      unavailable")
    log("  bar                           %+.4f" % cfg.bar)

    strat = {}
    if strata:
        buckets = collections.defaultdict(list)
        for pr in pairs:
            buckets[strata(pr)].append(pr)
        log("")
        log("  BY STRATUM")
        for k in sorted(buckets, key=lambda x: (isinstance(x, str), x)):
            sub = buckets[k]
            if len(sub) < 5:
                log("    %-22s %4d pairs   (too few to score)" % (k, len(sub)))
                strat[str(k)] = {"pairs": len(sub)}
                continue
            dv = delta(obs, sub, 2)
            gv = delta(deranged_obs(obs, sub, rng), sub, 2)
            log("    %-22s %4d pairs   delta %+.4f   deranged %+.4f   excess %+.4f"
                % (k, len(sub), dv, gv, dv - gv))
            strat[str(k)] = {"pairs": len(sub), "delta": dv, "deranged": gv, "excess": dv - gv}

    ci_ok = lo is not None and lo > 0
    if exc > cfg.bar and ci_ok:
        verdict = "RECOVERED"
    elif abs(exc) < noise and cfg.bar < noise:
        verdict = "UNDERPOWERED AT THE BAR"
    else:
        verdict = "NOT RECOVERED"
    log("")
    log("  bar vs instrument noise       bar %+.4f, noise %.4f -> bar is %s"
        % (cfg.bar, noise, "BELOW the noise floor" if cfg.bar < noise else "resolvable"))
    log("  VERDICT: %s" % verdict)
    return {"structure": name, "min_cell": min_cell, "noise_2sd": noise,
            "pairs": len(pairs), "observations": nobs,
            "delta_residualised": d_res, "delta_raw": d_raw,
            "deranged_residualised": g_res, "deranged_raw": g_raw,
            "deranged_sd": g_sd, "excess": exc,
            "shuffled_mean": sh_mean, "shuffled_sd": sh_sd,
            "ci_lo": lo, "ci_hi": hi, "bar": cfg.bar,
            "floor_planted": f_hit, "floor_null": f_nul, "floor_null_sd": nul_sd,
            "dropped_no_direction": drops["no direction"],
            "dropped_positivity": drops["positivity"],
            "strata": strat, "verdict": verdict}


def price(sweep, bar, log, learners, both_order):
    """Instrument noise falls as c/sqrt(pairs); the sweep's points fix c and say what a corpus
    would have to supply. This is the number to quote when asking a data holder for more."""
    pts = [(r["pairs"], r["noise_2sd"]) for r in sweep if r.get("noise_2sd")]
    if not pts:
        return {}
    cs = sorted(n * (k ** 0.5) for k, n in pts)
    c = cs[len(cs) // 2]
    best = max(k for k, _ in pts)
    log("")
    log("=" * 78)
    log("WHAT WOULD SETTLE IT")
    log("=" * 78)
    log("  noise falls as %.3f / sqrt(pairs), fitted on %d sweep points" % (c, len(pts)))
    log("  both-order pairs in hand, best setting   %d" % best)
    for tgt, lbl in ((bar, "to resolve the bar"), (bar / 2, "to resolve half the bar")):
        log("  pairs needed %-24s %d" % (lbl, int(math.ceil((c / tgt) ** 2))))
    log("")
    log("  learners %d   unordered pairs seen in both orders %d" % (learners, both_order))
    return {"noise_constant": c, "pairs_in_hand": best,
            "pairs_for_bar": int(math.ceil((c / bar) ** 2)),
            "pairs_for_half_bar": int(math.ceil((c / (bar / 2)) ** 2))}
