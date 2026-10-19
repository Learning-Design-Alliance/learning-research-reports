"""A4 POSITIVE CONTROL on ASSISTments 2012-13: is CCSS grade order recovered in real human
responses, DIRECTION INCLUDED?

WHY THIS CORPUS, AND WHAT UNLOCKED IT. studies/measurement/edmcup-direction/ ran this same contrast on EDM Cup 2023 and
came back UNDERPOWERED AT THE BAR: the readout needs pairs seen in BOTH orders, EDM Cup yielded 128,
and the pre-registered 0.02 bar fell below the instrument's own 0.025-0.031 noise. That study priced
the ask at about 504 both-order pairs and named the mechanism that recruits them -- learners on
DIFFERENT curricular sequences, not more learners on the same one.

ASSISTments 2012-13 is exactly that corpus, and it was already on disk. Skill builders are
TEACHER-ASSIGNED, so different classes meet skills in different orders, and the both-order cell is
abundant rather than scarce: 14,485 both-order pairs, 4,809 of them passing positivity at 10 per
cell, against EDM Cup's 5 at the same floor.

What was missing was the curriculum map, and EDM Cup supplied it. Its problem_details.csv publishes
541 CCSS codes each with a description, which makes it in effect a published ASSISTments skill-name
to CCSS dictionary. Matched against the 245 named 2012 skills it maps 135 of them (67 exact name
matches, 68 strong), 132 carrying a parseable grade spanning grades 1-8.

THE CAVEAT THAT COMES WITH THAT MAP. Name matching is not construct identity: two releases sharing a
label need not share a construct. That is why the match tier is a reported structure of its own --
S1-EXACT uses only the 67 exact-name matches, so if the fuzzy tail is driving anything, the two
disagree. CCSS GRADE is the robust part of the code: minor construct drift rarely moves a skill
across a grade boundary.

CLASS PROXY. assist_slim carries no class_id. assignment_id does group learners, since an ASSISTments
assignment is given to a class, so each learner is clustered by the assignment they were FIRST seen
on. That is a PROXY and is named as one: 6,630 cohorts, 84.6% of learners in cohorts of 5 or more,
6.8% singletons. Intervals resample whole cohorts.

DATA HANDLING. ASSISTments is analysis-only, no redistribution. Raw CSVs stay in the scratchpad. The
committed artefacts are the aggregate JSON and the derived skill-to-CCSS map.

The statistic, the controls and the verdict rule live in shared/direction_contrast.py -- read that
docstring first. In brief: delta(A,B) = drop(A->B) - drop(B->A) on pairs seen both ways, scored as
excess over a family-matched deranged arm, with a planted-gate floor, a direction-label null and a
cluster bootstrap.

PRE-REGISTERED BEFORE THE RUN. bar delta_excess > 0.02; 95% cluster bootstrap over COHORT must
exclude 0; >= 10 learners in each of a pair's four cells; fewer than 20 surviving pairs ->
UNANSWERABLE; a null at the bar where the bar falls under the instrument's noise is UNDERPOWERED AT
THE BAR, not NOT RECOVERED.

DIRECTION: a -> b means skill a's CCSS grade is lower than b's (grade 5 before grade 6), per the
Common Core code's leading grade field (EDM Cup codebook, problem_skill_code: "The Common Core State
Standards for Mathematics skill code most related to solving the problem", e.g. 6.EE.A.2 is grade 6)
reached through this study's name match; that lower grades are taught first is the standard's own
grade designation, not a dataset field.

Reversed-arrow control added 2026-09-24. Each structure's delta (ability-residualised, on the pairs
that survive direction and positivity) is recomputed with every grade order reversed. The within-pair
contrast is antisymmetric, so the reverse is exactly minus the claim and the control reads the sign
of the published order's result; reported, not gated, since the registered verdicts are nulls.
"""
import collections
import csv
import json
import os
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from shared.corpus import build_observations, cells  # noqa: E402
from shared.direction import reversed_arrow  # noqa: E402
from shared.direction_contrast import (Config, by_position, delta, position_strata,  # noqa: E402
                                       positions_for, price, run_structure, select)

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"
SCRATCH = pathlib.Path(os.environ.get("ASSIST_DIR", ""))
EDMCUP = pathlib.Path(os.environ.get("EDMCUP_DIR", ""))

PASS = 0.5
CFG = Config(min_cell=10, min_pairs=20, bar=0.02, reps=400, plant=0.15)
STOP = {"the", "a", "an", "of", "and", "or", "to", "in", "with", "for", "by", "within",
        "using", "use"}


def toks(s):
    return set(w for w in re.sub(r"[^a-z0-9 ]", " ", s.lower()).split() if w not in STOP)


def ccss_map():
    """ASSISTments 2012 skill_id -> (CCSS code, match quality). Built from EDM Cup's published
    (code, description) pairs, which is the only place this programme has found an ASSISTments
    skill vocabulary aligned to Common Core."""
    edm = {}
    for r in csv.DictReader(open(EDMCUP / "problem_details.csv")):
        c = (r.get("problem_skill_code") or "").strip()
        d = (r.get("problem_skill_description") or "").strip()
        if c and d:
            edm[c] = d
    etok = {c: toks(d) for c, d in edm.items()}
    names = {}
    for r in csv.reader(open(SCRATCH / "assist_skill_names.csv")):
        if len(r) >= 2:
            names[r[0]] = r[1]
    out = {}
    for sid, nm in names.items():
        t = toks(nm)
        if not t:
            continue
        best, bs = None, 0.0
        for c, tt in etok.items():
            if tt:
                j = len(t & tt) / len(t | tt)
                if j > bs:
                    bs, best = j, c
        if bs >= 0.5:
            out[sid] = (best, round(bs, 3), nm, edm[best])
    return out, len(names)


def corpus():
    """The corpus, through the loader contract. This is now the ONLY corpus-specific line.

    The CCSS map is written to out/ before the corpus is built, and the adapter reads it back as
    its position(): the grade parse that used to live here as grade_of() is the adapter's, so this
    study no longer carries its own copy of "which grade is this skill". Writing the map first is
    not a detour -- the file is a committed artefact of this study either way, and a position that
    only exists in memory is a position the next caller cannot have."""
    from shared.corpus import Assistments2012
    return Assistments2012(SCRATCH, ccss_map=OUT / "skill_ccss_map.json", with_cohorts=True)


def main():
    if not SCRATCH.is_dir() or not EDMCUP.is_dir():
        sys.exit("set ASSIST_DIR and EDMCUP_DIR")
    OUT.mkdir(exist_ok=True)
    lines = []

    def log(s=""):
        print(s)
        lines.append(s)

    cm, n_named = ccss_map()
    # WRITTEN BEFORE THE CORPUS IS BUILT, because the adapter's position() reads it. See corpus().
    (OUT / "skill_ccss_map.json").write_text(json.dumps(
        {s: {"ccss": c, "jaccard": q, "assistments_name": nm, "edmcup_description": d}
         for s, (c, q, nm, d) in sorted(cm.items())}, indent=2))

    c = corpus()
    # THE GRADE NOW COMES FROM THE CONTRACT, not from a parser in this file. `exact` stays here:
    # restricting to the 67 exact-name matches is a CONTROL on the fuzzy map, which is this study's
    # business, not a property of the corpus.
    gr = positions_for(c, set(cm))
    exact = {s for s, (_, q, _, _) in cm.items() if q >= 0.999 and s in gr}
    keep = set(gr)

    log("A4 POSITIVE CONTROL ON ASSISTMENTS 2012-13 -- IS CCSS GRADE ORDER RECOVERED?")
    log("")
    log("  named skills %d   mapped to CCSS %d   with a grade %d   exact-name subset %d"
        % (n_named, len(cm), len(gr), len(exact)))
    log("  grade spread  %s" % sorted(collections.Counter(gr.values()).items()))

    allcells = {k: v for k, v in cells(c).items() if k[1] in keep}
    per = collections.defaultdict(list)
    for (learner, unit) in allcells:
        per[learner].append(unit)
    cls = {learner: c.cohort(learner) for learner in per}
    log("  learners touching a mapped skill %d   cohorts %d"
        % (len(per), len(set(cls.get(u, "?") for u in per))))
    # Practice attempts straddle B, so passed_A must use only the PRIOR ones; outcome is the
    # learner's whole record at B.
    obs = {k: v for k, v in build_observations(
               c, pass_threshold=PASS, pass_on="prior", outcome="all").items()
           if k[0] in keep and k[1] in keep}
    both = sum(1 for (a, b) in obs if (b, a) in obs) // 2
    log("  ordered skill pairs %d   pairs seen in BOTH orders %d" % (len(obs), both))

    strata = position_strata(gr, "grade gap")
    STRUCTURES = [
        ("S1  CCSS GRADE", "grade 5 skill before grade 6 skill, from the code itself",
         by_position(gr)),
        ("S1E CCSS GRADE, EXACT NAMES ONLY",
         "same, restricted to the %d exact name matches" % len(exact),
         by_position(positions_for(c, set(cm), allowed=exact))),
    ]
    res = [run_structure(nm, bl, obs, fn, cls, log, CFG, strata=strata) for nm, bl, fn in STRUCTURES]

    # reversed-arrow control on each structure's surviving pairs
    def signed_delta(edges):
        return delta(obs, [(e, (e[1], e[0])) for e in sorted(edges)], 2)

    log("")
    for r, (nm, _bl, fn) in zip(res, STRUCTURES):
        pairs, _ = select(obs, fn, CFG.min_cell)
        if not pairs:
            continue
        r["reversed_arrow"] = reversed_arrow(signed_delta, {f for f, _b in pairs})
        f = r["reversed_arrow"]
        log("  REVERSED-ARROW CONTROL  %-34s delta claimed %+.4f  reversed %+.4f -> %s"
            % (nm, f["claimed"], f["reversed"], f["verdict"]))

    log("")
    log("=" * 78)
    log("POSITIVITY-FLOOR SWEEP  (every setting reported, pre-registered floor is %d)"
        % CFG.min_cell)
    log("=" * 78)
    sweep = []
    for nm, bl, fn in STRUCTURES:
        for mc in (5, 10, 20, 30):
            r = run_structure(nm, bl, obs, fn, cls, lambda *_: None, CFG, min_cell=mc)
            sweep.append(r)
            log("  %-34s cells>=%-3d pairs %4d  excess %s  noise %s  %s"
                % (nm, mc, r["pairs"],
                   ("%+.4f" % r["excess"]) if "excess" in r else "    --  ",
                   ("%.4f" % r["noise_2sd"]) if "noise_2sd" in r else "  --  ",
                   r["verdict"]))

    priced = price(sweep, CFG.bar, log, len(per), both)

    log("")
    log("=" * 78)
    log("A4")
    log("=" * 78)
    for r in res:
        log("  %-34s %s" % (r["structure"], r["verdict"]))

    (OUT / "direction.json").write_text(json.dumps(
        {"pass_threshold": PASS, "min_cell": CFG.min_cell, "bar": CFG.bar,
         "named_skills": n_named, "mapped": len(cm), "with_grade": len(gr),
         "exact_names": len(exact), "learners": len(per), "both_order_pairs": both,
         "structures": res, "positivity_sweep": sweep, "pricing": priced}, indent=2))
    (OUT / "direction.log").write_text("\n".join(lines) + "\n")
    log("")
    log("wrote out/direction.json and out/skill_ccss_map.json")


if __name__ == "__main__":
    main()
