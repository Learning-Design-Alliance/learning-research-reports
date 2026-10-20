"""A4 POSITIVE CONTROL: is an independently-known curricular structure recovered in real human
responses, DIRECTION INCLUDED?

CORPUS. EDM Cup 2023 (osf.io/7stjh), an ASSISTments release: 34,580 learners with graded unit-test
responses, 192,971 (learner, skill, time) cells, CCSS skill codes on 99.4% of 132,738 problems.
Analysis only, no redistribution; raw CSVs stay in the scratchpad and only the aggregates below are
committed. See prep.py for how the learner timeline is rebuilt -- and for the REMOVED_FOR_EVALUATION
sentinel that makes the corpus look, on a naive read, as though it has no timeline at all.

WHAT MAKES THIS A POSITIVE CONTROL. The structure is not induced from the responses. It is read off
two published documents that existed before any of these learners sat down:
   S1  CCSS GRADE, parsed from the code itself (5.NBT.A.1 is grade 5, 6.RP.A.2 is grade 6).
   S2  CURRICULUM MODULE ORDER, from the publisher's own scope and sequence (Kendall Hunt
       Illustrative Mathematics, EngageNY/Eureka). Within one course, module 3 is taught after
       module 2. This supplies direction WITHIN a grade, where S1 is silent.
   S3  CURRICULUM LESSON ORDER, the same document read at the grain it is written in.
S3 was added after S1 and S2 came back underpowered. It is a finer reading of the same published
document, not a different hypothesis; the bar and the verdict rule were not touched.
If the assay cannot recover an order this well established, the fault is the assay's.

The statistic, the controls and the verdict rule all live in shared/direction_contrast.py, because
studies/measurement/assist2012-direction/ runs the same ones and a rule that lives in one copy is a rule the next caller
does not have. Read that module's docstring first.

PRE-REGISTERED BEFORE THE RUN. bar delta_excess > 0.02 on the 0-1 score scale; 95% cluster bootstrap
over CLASS must exclude 0; >= 10 learners in each of a pair's four cells; fewer than 20 surviving
pairs -> UNANSWERABLE. Verdicts RECOVERED / NOT RECOVERED / UNANSWERABLE / FLOOR FAILURE, plus
UNDERPOWERED AT THE BAR where the bar falls below the instrument's own noise.

DIRECTION: a -> b means a comes first: S1 a lower CCSS grade, per problem_skill_code ("The Common Core
State Standards for Mathematics skill code most related to solving the problem", EDM Cup codebook;
the grade is the code's leading field); S2/S3 a lower Module/Unit (then Topic, Lesson) number within
one course of sequence_details.csv's folder path, per the publisher's own numbering -- the codebook
documents the columns, not an ordering, so "module 2 is taught before module 3" is the folder names'
convention, not a documented field.

Reversed-arrow control added 2026-09-24. Each structure's delta (ability-residualised, on the pairs
that survive direction and positivity) is recomputed with every order reversed. The within-pair
contrast is antisymmetric, so the reverse is exactly minus the claim and the control reads the sign
of the published order's result; reported, not gated, since the registered verdicts are not
RECOVERED.
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
SCRATCH = pathlib.Path(os.environ.get("EDMCUP_DIR", ""))

PASS = 0.5
CFG = Config(min_cell=10, min_pairs=20, bar=0.02, reps=400, plant=0.15)

MODULE = re.compile(r"\b(?:Module|Unit)\s*(\d+)", re.I)
LESSON = re.compile(r"\bLesson\s*(\d+)", re.I)
TOPIC = re.compile(r"\bTopic\s+([A-Z])\b")


# ---------------------------------------------------------------- structures

def _skill_map():
    skill = {}
    for row in csv.DictReader(open(SCRATCH / "problem_details.csv")):
        c = (row.get("problem_skill_code") or "").strip()
        if c:
            skill[row["problem_id"]] = c
    return skill


def curriculum_positions():
    """skill -> (publisher, course, module). Read from the publisher's scope and sequence alone:
    which sequence a problem sits in, and what that sequence's folder path says. No learner response
    is consulted."""
    skill = _skill_map()
    votes = collections.defaultdict(collections.Counter)
    for row in csv.DictReader(open(SCRATCH / "sequence_details.csv")):
        m = MODULE.search(row["sequence_folder_path_level_3"] or "")
        if not m:
            continue
        pos = (row["sequence_folder_path_level_1"], row["sequence_folder_path_level_2"],
               int(m.group(1)))
        for pid in (row["sequence_problem_ids"] or "").strip("[]").split(","):
            k = skill.get(pid.strip())
            if k:
                votes[k][pos] += 1
    return {k: v.most_common(1)[0][0] for k, v in votes.items()}


def fine_positions():
    """skill -> (publisher, course, median (module, topic, lesson)). The same published document as
    S2, read at the grain it is actually written in: module 1 topic B lesson 4 comes before lesson 5.
    This is what gives direction to the same-module pairs S2 has to discard. 82.7% of sequences carry
    a lesson or topic; the rest (unit assessments) fall back to lesson 0 and order by module alone.
    The median, not the mode, because a skill is practised across several lessons and the middle of
    that run locates it better than its single commonest lesson."""
    skill = _skill_map()
    votes = collections.defaultdict(list)
    for row in csv.DictReader(open(SCRATCH / "sequence_details.csv")):
        m = MODULE.search(row["sequence_folder_path_level_3"] or "")
        if not m:
            continue
        l4 = row["sequence_folder_path_level_4"] or ""
        les = LESSON.search(l4) or LESSON.search(row["sequence_name"] or "")
        top = TOPIC.search(l4)
        key = (int(m.group(1)), ord(top.group(1)) - 65 if top else 0,
               int(les.group(1)) if les else 0)
        course = (row["sequence_folder_path_level_1"], row["sequence_folder_path_level_2"])
        for pid in (row["sequence_problem_ids"] or "").strip("[]").split(","):
            k = skill.get(pid.strip())
            if k:
                votes[k].append((course, key))
    out = {}
    for k, vs in votes.items():
        course = collections.Counter(c for c, _ in vs).most_common(1)[0][0]
        keys = sorted(key for c, key in vs if c == course)
        out[k] = (course[0], course[1], keys[len(keys) // 2])
    return out


# ---------------------------------------------------------------- corpus

def corpus():
    """The corpus, through the loader contract. This is now the ONLY corpus-specific line."""
    from shared.corpus import EdmCup
    return EdmCup(SCRATCH)


def main():
    if not SCRATCH.is_dir():
        sys.exit("set EDMCUP_DIR to the scratchpad directory holding the EDM Cup CSVs")
    OUT.mkdir(exist_ok=True)
    lines = []

    def log(s=""):
        print(s)
        lines.append(s)

    c = corpus()
    # A unit-test cell is one sitting, so the first event IS the encounter: first/first.
    obs = build_observations(c, pass_threshold=PASS, pass_on="first", outcome="first")
    per = collections.defaultdict(list)
    for (learner, unit), (t, mean, _n) in cells(c).items():
        per[learner].append((t, unit, mean))
    cls = {learner: c.cohort(learner) for learner in per}
    log("A4 POSITIVE CONTROL -- IS A PUBLISHED CURRICULAR ORDER RECOVERED, DIRECTION INCLUDED?")
    log("")
    log("  learners %d   classes %d   ordered skill pairs %d"
        % (len(per), len(set(cls.values())), len(obs)))
    both = sum(1 for (a, b) in obs if (b, a) in obs) // 2
    log("  pairs observed in BOTH orders %d   <- the only pairs the contrast can use" % both)

    # S1's position IS the contract's: EdmCup.position() parses the grade off the CCSS code, which
    # is what this study used to do for itself. S2 and S3 keep their own position builders because
    # the publisher's scope and sequence is corpus-specific ENRICHMENT with no analogue elsewhere --
    # but they order through the same shared function, so none of the three carries its own copy of
    # "order by an external scale" any more. That was O1's last piece of per-dataset plumbing here.
    grade = positions_for(c, {u for pair in obs for u in pair})
    mod, fine = curriculum_positions(), fine_positions()
    STRUCTURES = [
        ("S1  CCSS GRADE", "5.NBT before 6.RP, from the code itself",
         by_position(grade), position_strata(grade, "grade gap")),
        ("S2  CURRICULUM MODULE ORDER", "module 2 before module 3, from the publisher's sequence",
         by_position(mod), position_strata(mod, "module gap")),
        ("S3  CURRICULUM LESSON ORDER",
         "module 1 lesson 4 before lesson 5, same document read finer",
         by_position(fine), position_strata(fine, "module gap")),
    ]
    res = [run_structure(nm, bl, obs, fn, cls, log, CFG, strata=st)
           for nm, bl, fn, st in STRUCTURES]

    # reversed-arrow control on each structure's surviving pairs
    def signed_delta(edges):
        return delta(obs, [(e, (e[1], e[0])) for e in sorted(edges)], 2)

    log("")
    for r, (nm, _bl, fn, _st) in zip(res, STRUCTURES):
        pairs, _ = select(obs, fn, CFG.min_cell)
        if not pairs:
            continue
        r["reversed_arrow"] = reversed_arrow(signed_delta, {f for f, _b in pairs})
        f = r["reversed_arrow"]
        log("  REVERSED-ARROW CONTROL  %-34s delta claimed %+.4f  reversed %+.4f -> %s"
            % (nm, f["claimed"], f["reversed"], f["verdict"]))

    # The positivity floor trades pairs against cell noise, and which way that trade falls is not
    # knowable in advance, so the whole sweep is reported -- every setting, not the kind one.
    log("")
    log("=" * 78)
    log("POSITIVITY-FLOOR SWEEP  (every setting reported, pre-registered floor is %d)"
        % CFG.min_cell)
    log("=" * 78)
    sweep = []
    for nm, bl, fn, _ in STRUCTURES:
        for mc in (5, 10, 20, 30):
            r = run_structure(nm, bl, obs, fn, cls, lambda *_: None, CFG, min_cell=mc)
            sweep.append(r)
            log("  %-28s cells>=%-3d pairs %4d  excess %s  noise %s  %s"
                % (nm, mc, r["pairs"],
                   ("%+.4f" % r["excess"]) if "excess" in r else "    --  ",
                   ("%.4f" % r["noise_2sd"]) if "noise_2sd" in r else "  --  ",
                   r["verdict"]))

    priced = price(sweep, CFG.bar, log, len(per), both)
    log("")
    log("  The scarce thing is not learners but learners who meet a LATER skill BEFORE an earlier")
    log("  one. A corpus recruits that cell by containing learners on DIFFERENT curricular")
    log("  sequences, not by containing more of the same ones.")

    log("")
    log("=" * 78)
    log("A4")
    log("=" * 78)
    for r in res:
        log("  %-30s %s" % (r["structure"], r["verdict"]))
    (OUT / "direction.json").write_text(json.dumps(
        {"pass_threshold": PASS, "min_cell": CFG.min_cell, "min_pairs": CFG.min_pairs,
         "bar": CFG.bar, "learners": len(per), "both_order_pairs": both,
         "structures": res, "positivity_sweep": sweep, "pricing": priced}, indent=2))
    (OUT / "direction.log").write_text("\n".join(lines) + "\n")
    log("")
    log("wrote out/direction.json")


if __name__ == "__main__":
    main()
