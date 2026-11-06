"""
Precise boolean checklists against Likert rubrics for an LLM grader: what the reliability gain is
made of, and what it costs in validity (2026-10-28).

WHAT WAS ASKED. Google's "A Scalable Framework for Evaluating Health Language Models" (Mallinar et al.,
npj Digital Medicine 2026; arXiv 2503.23339) splits each Likert criterion into roughly ten times as
many yes/no questions ("Precise Boolean rubrics") and reports a higher inter-rater ICC and about half
the rating time. The maintainer asked whether that reliability costs validity: whether some concepts
cannot be captured as booleans, whether a decomposition can miss critical children, and whether it
works beyond procedural assessment. Three things in the paper make its headline hard to read
(conversation of 2026-10-28, and the paper's own text):
  * ICC is computed per (query, response, question) tuple. Between-question differences in base rate
    enter that ICC and raise it without raters agreeing any better about a given response. The fair
    comparison is the reliability of each response's score.
  * binarised Likert did worse than both, so if anything helped it was precise wording, not yes/no;
  * its validity test (scores fall when biomarkers are removed from the prompt) is close to circular:
    the booleans are templated on the user's data ("does the response mention cholesterol?").
The literature this answers to: OSCE checklists vs global ratings (Regehr et al. 1998; Hodges et al.
1999; Ilgen et al. 2015, Medical Education 49:161), Van der Vleuten et al. 1991 on objectification,
Sadler 2009 on criteria and holistic quality, and for LLM judges Furuhashi et al., EMNLP 2025.

THE DESIGN. One grader, two scoring formats on IDENTICAL inputs: the arms differ only in what the
grader is asked to return.
  LIKERT   the established rubric: one score per criterion on the corpus's own scale.
  BOOLEAN  a checklist of precise yes/no checks per criterion, authored by a model from the same
           criterion text (the paper's construction: one Likert criterion -> many booleans). The
           score is the share of YES, unweighted (the paper averages too).
Every input the Likert arm sees, the boolean arm sees (question, reference answer, rubric definition,
work); the boolean arm replaces the Likert scale and band descriptors with its checks.

THE CORPORA. Chosen to span the procedural / judgement axis the question is about.
  Mohler ASAG (data/data-sources.json `mohler-asag`, CC BY 4.0): data-structures short answers, a
    reference answer per question, two independent human raters (0-5). E01-E10 only (E11-E12 are on
    0-10 per rater; the harness drops them too): 1,721 answers, 62 questions (corrected 2026-10-28 from
    "61", per scope audit 1 note B; the draw was always 62). The construct is
    "contains the right ideas", which a checklist should suit.
  Menagerie (`menagerie-grades`, CC BY 4.0): 272 CS1 Java submissions with code, graded by 3-4
    recruited raters on four dimensions (Correctness, Code Elegance, Readability, Documentation),
    14-level letter scale, with the deposit's six-band marking rubric
    (studies/measurement/grader-eval/harness/menagerie.ts, MENAGERIE_RUBRIC, transcribed there and
    copied here verbatim). Documentation and Readability bands read close to checklists; Code
    Elegance is a judgement of the whole design. Correctness cannot be judged without the
    coursework specification, which neither arm sees (as in every earlier Menagerie run), so its
    results are reported and not predicted.
This script reads both corpora from $MOHLER_DIR and $MENAGERIE_DIR. Raw text, checklists (which
paraphrase the reference answers), perturbed answers and per-case dumps stay in the scratch area
($SCRATCH/grader-boolean); only aggregates and hashes are committed to out/.

THE DRAWS (fixed by stable hashes of item ids, seed SEED below; reproduced by --draw).
  Mohler main: 10 answers per question where available (stable-hash order within question): 620
    answers over 62 questions (realised; --draw).
  Mohler perturbation: HIGH answers (human mean >= 4.5) and LOW answers (<= 2.5), at most 3 per
    question each, stable-hash order, up to 120 each (realised: 120 HIGH over 61 questions, 120 LOW
    over 53).
  Menagerie: every submission with code and >= 3 human grades on every dimension: 272. Code is
    concatenated per submission in file order, original bytes, truncated at 90,000 characters as the
    harness does: 73 of 272 are truncated (mean 77,779 characters), the same for both arms.

THE GRADERS. Two vendors, so "inter-rater" has a machine analogue as well as test-retest:
  gemini-3.5-flash-lite  Google direct, the programme's shipped tier, JSON response mode, no
                         temperature/seed/top-p sent (vendor defaults), thinking left at default.
  gpt-5.4-mini           OpenAI direct, chat completions, json_object response format,
                         reasoning_effort "low" (to bound cost on 25k-token code prompts).
Each item is graded twice per arm per model (rep 0, rep 1), as independent calls. The served model
string is recorded on every call. Checklists and perturbations are authored by a third model,
gpt-5.5 (reasoning_effort "medium"), and the perturbation manipulation check is made by
gemini-3.1-pro-preview, so no grader authors or vets its own instrument (gpt-5.5 is the same vendor
as one grader; stated, not controlled).

CHECKLIST AUTHORING (prompts CHECKLIST_MOHLER and CHECKLIST_MENAGERIE below, fixed before any call).
  Mohler: one checklist per question, 3-8 checks, from the question and the reference answer.
  Menagerie: one checklist per dimension, 5-12 checks, from the definition and the six bands.
The prompt does not ask for, or forbid, a check that the answer contains no incorrect claim. Whether
a checklist has one is coded afterwards by a rule (any check whose text matches NO_ERROR_PATTERN) and
reported, because it decides whether the contradiction test below has a child that could catch it.
Checklists are written once, hashed, and frozen before any grading call (--build writes
out/checklists.json with hashes, counts and the Menagerie checklists in full; the Mohler checklists
stay in scratch because they paraphrase the corpus's reference answers).

PLANTED DEFECTS (Mohler perturbation draw): the missing-child test. A checklist decomposes "correct
and complete" into presence checks. If no child checks that what is present is TRUE, a contradiction
appended to a good answer should cost the checklist less than the Likert score; and terms listed
without understanding should earn the checklist more. For each answer gpt-5.5 writes two sentences
to append (prompt PERTURB_CONTRA or PERTURB_STUFF):
  HIGH answers  CONTRA   a specific false claim in the student's voice contradicting the reference
                         answer's key point;
                NEUTRAL  a true sentence in the same voice that adds no claim about the key ideas.
  LOW answers   STUFF    a sentence naming the reference answer's key terms without stating the
                         correct relationship between them;
                NEUTRAL  as above.
Size rule (CLAUDE.md: a control has to be the size of the thing it controls for): per answer the
neutral sentence is within 0.75-1.33x the treatment's characters (one regeneration allowed, then the
answer is dropped and counted), the mean ratio within +/-10%, and shared/controls.check_control_scale
passes. Manipulation check (gemini-3.1-pro-preview, prompt MANIP below, a MODEL check, not a human
one): CONTRA must contradict the reference (YES) and NEUTRAL must add no claim about the key ideas
(NO); STUFF must mention the key terms (YES) and not state the key idea correctly (NO). The primary
analysis uses answers whose pair passes; all pairs are reported as secondary.
Each answer is graded in both perturbed forms (answer + NEUTRAL, answer + treatment), never the
original, so the contrast is size- and position-matched.

ESTIMANDS. Scores are put on a common 0-1 scale (Likert / scale maximum; boolean share of YES).
Each arm's score for an item is the mean of its two reps unless the estimand is about reps. All
statistics are Pearson r, which no linear rescaling moves, so the boolean arm's coarser scale cannot
buy agreement through spread the way QWK can (findings/log/2026-09-16-the-rubric-was-mostly-scale.md).
Pooled estimates are the mean of the two models' estimates on the same resample.
  V[m,a]   validity: r(score, human mean). Mohler human mean = score_avg; Menagerie = mean of the
           item's raters. Ceiling reported beside it: Mohler r(rater 1, rater 2) on the same draw;
           Menagerie leave-one-rater-out r(one rater, mean of the others), pooled over ratings.
  dV       pooled V[.,BOOLEAN] - V[.,LIKERT], per corpus x dimension.
  R[m,a]   test-retest: r(rep 0, rep 1).        dR = pooled R[.,B] - R[.,L].
  X[a]     cross-model: r(gemini mean, gpt mean).   dX = X[B] - X[L].
  D[m,a]   perturbation effect: mean(score(answer+treatment) - score(answer+neutral)), 0-1 scale.
  C        pooled D[.,B] - D[.,L], separately for CONTRA (HIGH) and STUFF (LOW).
Unit of resampling: the question for Mohler (answers within a question share a checklist and a
reference), the submission for Menagerie. Cluster bootstrap, 4,000 replicates, percentile, by
multinomial cluster weights (the same resample as drawing clusters with replacement). Items with a
failed or unparseable call in any arm of a table are dropped from that table and counted.

PRE-REGISTERED VERDICTS (margins and strings fixed before any call).
  Validity, per corpus x dimension (margin 0.05 r):
    BOOLEAN-MORE-VALID / LIKERT-MORE-VALID   dV's 95% interval excludes 0, signed;
    EQUIVALENT                                dV's 90% interval inside +/-0.05;
    UNRESOLVED                                otherwise ("no difference larger than X").
  Reliability, test-retest and cross-model separately (margin 0.03 r):
    BOOLEAN-MORE-RELIABLE / LIKERT-MORE-RELIABLE / EQUIVALENT / UNRESOLVED, same rule.
  Contradiction (HIGH):
    LIKERT-ALSO-BLIND                  pooled D[.,LIKERT] 95% interval does not lie below 0: the
                                       positive control failed, the contrast is not read;
    CHECKLIST-BLIND-TO-CONTRADICTION   else, C's 95% interval above 0 (the checklist loses less);
    CHECKLIST-MORE-SENSITIVE           else, C's 95% interval below 0;
    NO-DIFFERENCE-RESOLVED             else.
  Stuffing (LOW):
    CHECKLIST-REWARDS-STUFFING         C's 95% interval above 0;
    LIKERT-REWARDS-STUFFING-MORE       C's 95% interval below 0;
    NO-DIFFERENCE-RESOLVED             otherwise.
  Each verdict is also given per model, and CONSISTENT is flagged when the two models' point
  estimates share a sign.

PREDICTIONS, written before the run (a prediction is not a verdict; both are reported):
  P1 reliability: dR > 0 and dX > 0 on Mohler (the paper's direction), but smaller than the per-tuple
     ICC contrast. P1b, descriptive: per-tuple ICC(3,1) between the two models (the paper's unit:
     item x check for BOOLEAN, item x dimension for Menagerie LIKERT) exceeds the response-level
     cross-model r of the same arm.
  P2 validity: Mohler dV >= -0.05 (a checklist suits "contains the right ideas"); Menagerie
     Documentation and Readability dV >= -0.05; Code Elegance dV < 0. Correctness: no prediction.
  P3 contradiction: CHECKLIST-BLIND-TO-CONTRADICTION, attenuated on checklists that carry a
     no-error check (descriptive split, not a verdict).
  P4 stuffing: CHECKLIST-REWARDS-STUFFING.

DESCRIPTIVE ONLY, by decision before the run: incremental validity, partial r(human, LIKERT |
BOOLEAN) and partial r(human, BOOLEAN | LIKERT). It looks like a missing-children test and is not
one. When two scores measure the same construct with independent errors, each carries information
about the construct that the other lacks, so both partials are positive with nothing missing. It is
reported because people will ask for it, with that sentence beside it.

THE FLOOR (--floor), before any grading call. Synthetic graders on the real draws (real human
scores, question clusters, the Menagerie rater structure). A latent true score T correlates with
the human mean at sqrt(its reliability) (Mohler: Spearman-Brown of r(rater 1, rater 2); Menagerie:
of the mean leave-one-out r at its rater count); each model x arm score is lam*T + mu*S + sigma*e,
S a stable item error per model x arm, e the call noise per rep, mapped through the human mean's own
marginal (LIKERT: the corpus's level grid; BOOLEAN: a share of YES on a 6-check grid). The null world
is set to validity 0.65 / retest 0.85 for Mohler and 0.45 / 0.85 for Menagerie, both arms equal.
Worlds, 200 replicates each, the instrument above unchanged (4,000 bootstrap replicates):
  NULL       validity: a signed verdict <= 10%; reliability: a signed verdict <= 10% each.
  V+ / V-    boolean validity +0.08 / -0.08 (Mohler), +0.10 / -0.10 (Menagerie, Code Elegance
             shape): the correctly signed verdict >= 80%, the wrong sign <= 5%.
  R+         boolean retest 0.92 against 0.85, validity held: BOOLEAN-MORE-RELIABLE >= 80%.
  CONTRA     LIKERT D -0.20, BOOLEAN D -0.08 (per-answer SD 0.20, call noise as above):
             CHECKLIST-BLIND-TO-CONTRADICTION >= 80%.
  CONTRA0    both D -0.20: CHECKLIST-BLIND-TO-CONTRADICTION <= 10%.
  BLIND      both D 0: LIKERT-ALSO-BLIND >= 80%.
  STUFF      BOOLEAN D +0.10, LIKERT +0.02: CHECKLIST-REWARDS-STUFFING >= 80%; STUFF0 both +0.02:
             <= 10%.
A world that misses its bar makes the matching verdict unreachable at this sample: it is reported as
an interval only, and the bar it missed is written here before any grading call. The floor is a
smoke check of the instrument's logic on worlds this script was told about, written and scored by
the same session; it is not a validation of any construct.

FLOOR RECORD: REVISION 0 FAILED, REVISION 1 PASSED, BOTH BEFORE ANY MODEL CALL (out/floor-rev0.json,
out/floor.json). Revision 0 failed two checks:
  * Mohler NULL, test-retest: LIKERT-MORE-RELIABLE in 20.5% (bar 10%). The null gave each arm its real
    output grid (LIKERT 11 levels, BOOLEAN a 7-level share), and the coarser grid alone lowers retest
    r: the world was not null. Revision 1 puts both arms of each NULL world on one grid, and adds GRID
    worlds (real grids, everything else equal), reported and not gated. Their result is itself a
    finding about the format: grid alone gives LIKERT-MORE-RELIABLE (retest) in 22.5% (Mohler) and
    23.5% (Menagerie) of replicates, and leaves validity and cross-model verdicts within the null
    bar (signed validity 9.5%, cross-model 6.0%). So A RETEST VERDICT FOR LIKERT IS READ AS POSSIBLY
    GRID ALONE; the boolean grids in the run are 4-13 levels, depending on the checklist's length.
  * Menagerie V+/-0.10: detected in 54.5% / 56% (bar 80%). Revision 1 adds +/-0.15 worlds, which pass
    (87.5% / 83.5%), with the wrong sign at 0% in all four. So on Menagerie a signed validity verdict is
    trustworthy (NULL false rate 7.5%), but UNRESOLVED does not rule out a difference up to about
    0.15 r; differences of 0.10 are detected in 58% / 56% of replicates. Mohler resolves +/-0.08
    (97% / 95%).
Revision 1 results (200 replicates per world): Mohler NULL signed validity 4.0%, retest 7.5%,
cross-model 7.5%; V+ 97%, V- 95%, wrong sign 0%; R+ 97%. Menagerie NULL signed validity 7.5%, retest
8.0%. CONTRA 100%, CONTRA0 2.5%, BLIND (LIKERT-ALSO-BLIND) 96.5%, STUFF 98%, STUFF0 1.5%.

RUN RECORD (2026-10-28, after the floor and the freeze). 10,976 gradings, 0 failed. Unparseable:
46 gpt-5.4-mini Menagerie boolean calls (it answered 12 checks for Readability's 10) and 1 Gemini
Likert call; by the drop rule Menagerie tables keep 226 of 272. Results in out/results.json and the
README. Two post hoc additions, each labelled where it is computed: the "avoid" split (added after
reading the checklists, before any grading call) and the Menagerie all-parsed block (added after
reading the results, because neither grader tracks the raters on most Menagerie dimensions).

COST. Estimated before the run: Mohler (620 + 2 x 240) items x 2 arms x 2 reps x 2 models = 8,800
short calls; Menagerie 272 x 2 x 2 x 2 = 2,176 calls at ~25k input tokens. About $40 in all, most
of it gpt-5.4-mini on Menagerie. Calls are cached on disk by (model, prompt hash, rep).

    python3 boolean.py --draw          print the draws (no calls)
    python3 boolean.py --floor         synthetic worlds -> out/floor.json (no calls)
    python3 boolean.py --build         author checklists (gpt-5.5) -> scratch + out/checklists.json
    python3 boolean.py --perturb       author perturbations + manipulation check -> scratch + out/perturb.json
    python3 boolean.py --run           grading calls -> scratch dumps
    python3 boolean.py --analyse       -> out/results.json
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import hashlib
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from shared.controls import check_control_scale  # noqa: E402
from shared.paths import data_path, scratch_root  # noqa: E402
from shared.seeds import stable_hash  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
SCR = scratch_root() / "grader-boolean"
SEED = 20261028
RELEASE_CASES = REPO / "research/wiki/research/releases/checklist-grading-2026/per-case-model-outputs.jsonl"
BOOT = 4000

GRADERS = {"gemini": ("google", "gemini-3.5-flash-lite"), "gpt": ("openai", "gpt-5.4-mini")}
AUTHOR = ("openai", "gpt-5.5")
CHECKER = ("google", "gemini-3.1-pro-preview")
ARMS = ("likert", "boolean")
REPS = (0, 1)

MARGIN_V, MARGIN_R = 0.05, 0.03
NO_ERROR_PATTERN = re.compile(
    r"\b(no|free of|without|avoid\w*|does not (contain|include|make|state)|doesn't)\b.{0,40}"
    r"\b(incorrect|false|wrong|erroneous|inaccura\w*|misconception\w*|error\w*|mistake\w*|contradict\w*)",
    re.I)
# Post hoc (see analyse): any check phrased as avoiding something, which is how the author wrote its
# targeted misconception checks.
AVOID_PATTERN = re.compile(r"\bavoid", re.I)

# ---------------------------------------------------------------- data

MOHLER_PER_Q = 10
PERTURB_PER_Q, PERTURB_N = 3, 120
MENAGERIE_MAX_CHARS = 90000
MEN_SCALE = ["F", "D-", "D", "D+", "C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+", "A++"]
MEN_DIMS = ["Correctness", "Code Elegance", "Readability", "Documentation"]

# Verbatim from studies/measurement/grader-eval/harness/menagerie.ts (MENAGERIE_DIMENSIONS,
# MENAGERIE_RUBRIC), which quotes and transcribes the deposit; the percentage ranges are dropped there
# for the reason given there.
MEN_DEF = {
    "Correctness": "Correctness covers how well the student met the assignment requirements.",
    "Code Elegance": "Code elegance focuses on writing maintainable code, including correctly using "
                     "functions and classes.",
    "Readability": "Readability covers how readable the source code is, including whether the student "
                   "used meaningful variable and function names and used whitespace to separate code blocks.",
    "Documentation": "Documentation examines if the associated documentation is well written and organised "
                     "and clearly explains what the code is accomplishing.",
}
MEN_RUBRIC = {
    "Correctness": [
        ("A+ to A++", "The application works as described in the assignment; all base tasks are completed; the implementation demonstrates originality, creativity, and technical excellence in the completion of all challenging tasks; the student included documentation describing the challenge tasks that were completed and how; all submission instructions were followed correctly."),
        ("A", "The application works as described in the assignment; all base tasks are completed; the student has completed some of the challenge tasks; the student included documentation describing the challenge tasks that were completed and how; all submission instructions were followed correctly."),
        ("B", "The application works as described in the assignment; all the base tasks are completed, however, no challenge task was attempted; all submission instructions were followed correctly."),
        ("C", "Minor details of a task(s) are violated; the application functions correctly on the majority inputs/actions."),
        ("D", "Some tasks are incomplete; the application functions incorrectly on some inputs/actions."),
        ("F", "Significant details of a task are violated, or the program often exhibits incorrect behaviour; the applications does not open or run in BlueJ; Java files are missing."),
    ],
    "Code Elegance": [
        ("A+ to A++", "Student demonstrates excellent use of classes and functions to produce reusable and maintainable code, where possible, in the base and all of the challenge tasks; the code is efficient without sacrificing readability and understanding."),
        ("A", "All of the base tasks and some of the challenge tasks are implemented in such a way that code can be reused, where possible; the majority of the code is written in such a way that is easy to maintain, i.e., add new or extend features; the code is efficient without sacrificing readability and understanding."),
        ("B", "The application is implemented in such a way that only a few code segments could be rewritten to increase code re-usability; the code is fairly efficient without sacrificing readability and understanding; the student made a poor design choice in a single area."),
        ("C", "The application is implemented in such a way that many code segments (or functions) could be rewritten to increase code re-usability; some of the code is unnecessarily complex or poorly designed."),
        ("D", "The application is unnecessarily complex and/or uses brute force; the application contains many instances where the code could have been written in an easier, faster or better fashion."),
        ("F", "The application is not organised for re-usability, e.g., all the code is in a single class (or function); no effort is made to create reusable code; the application is excessively long and poorly organised."),
    ],
    "Documentation": [
        ("A+ to A++", "The documentation is well written, organised and clearly explains what the code is accomplishing and how; the student documents the contents of each class at the beginning of the file; the student documents the purpose of each function, i.e., the function's parameters and return values at the beginning of each function; the student documents each logical block of code when performing non-obvious operations; Every file includes header information (e.g., student name and k-number)."),
        ("A", "The documentation consists of comments that are useful in understanding the code and/or structure of the program; each file has header information (e.g., student name and k-number)."),
        ("B", "The documentation consists of comments that are somewhat useful in understanding the code; some of the comments state the obvious."),
        ("C", "The documentation is simply comments embedded in the code but does not help the reader understand the code."),
        ("D", "One or more code segments could benefit from comments or the code is overly commented."),
        ("F", "The application has no comments, not even the header with the student's name or k-number."),
    ],
    "Readability": [
        ("A+ to A++", "The application is exceptionally well organised and very easy to understand; the student used indentation appropriately and consistently to delineate code blocks; each function performs a single well defined operation; the student used meaningful identifier names, i.e., good function and variables names; the student used white space between logical code blocks; the student uses consistent spacing around operators and variables; classes are self-contained with private data hidden and methods are public only when necessary."),
        ("A", "The code is clean, understandable and organised; the student used meaningful identifier names, i.e., good function and variables names; the student used white space between logical code blocks."),
        ("B", "The application has minor issues such as inconsistent indentation."),
        ("C", "The application has one or two issues that makes the program difficult to understand such as poorly named identifiers and disorganised code."),
        ("D", "The application has more than two issues that makes the program difficult to understand."),
        ("F", "The code is readable only by someone who knows what it is supposed do; the application has several issues that makes the program difficult to understand."),
    ],
}


def clean(t: str) -> str:
    return re.sub(r"\s+", " ", t.replace("<STOP>", " ")).strip()


def load_mohler() -> list[dict]:
    rows = list(csv.DictReader(open(data_path("MOHLER_DIR") / "mohler_en.csv", encoding="utf-8")))
    out = []
    for r in rows:
        if r["id"][:3] in ("E11", "E12"):
            continue
        out.append(dict(id=r["id"], q=r["id"].rsplit(".", 1)[0], question=clean(r["question"]),
                        ref=clean(r["instructor_answer"]), answer=clean(r["student_answer"]),
                        g1=float(r["score_grader_1"]), g2=float(r["score_grader_2"]),
                        h=float(r["score_avg"])))
    return out


def mohler_draws(rows: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    byq = defaultdict(list)
    for r in rows:
        byq[r["q"]].append(r)
    main, high, low = [], [], []
    for q in sorted(byq):
        items = sorted(byq[q], key=lambda r: stable_hash((SEED, r["id"])))
        main += items[:MOHLER_PER_Q]
        high += [r for r in items if r["h"] >= 4.5][:PERTURB_PER_Q]
        low += [r for r in items if r["h"] <= 2.5][:PERTURB_PER_Q]
    key = lambda r: stable_hash((SEED, "p", r["id"]))
    return main, sorted(high, key=key)[:PERTURB_N], sorted(low, key=key)[:PERTURB_N]


def load_menagerie() -> list[dict]:
    root = data_path("MENAGERIE_DIR")
    grades = defaultdict(dict)
    for r in csv.DictReader(open(root / "grades.csv", encoding="utf-8")):
        if r["grade"] in MEN_SCALE:
            a = re.sub(r"\.0+$", "", r["assignment_number"].strip())
            grades[(a, r["skill"])][r["participant_id"]] = MEN_SCALE.index(r["grade"])
    code = {}
    src = root / "src"
    for year in sorted(p for p in src.iterdir() if p.is_dir()):
        inner = year / year.name if (year / year.name).is_dir() else year
        for sub in sorted(p for p in inner.iterdir() if p.is_dir()):
            m = re.search(r"_Submission_(\d+)$", sub.name)
            if not m:
                continue
            files = sorted(f for f in sub.rglob("*.java") if "__MACOSX" not in f.parts)
            if not files:
                continue
            text = "\n\n".join(f"// ==== {f.name} ====\n" + f.read_text(encoding="utf-8", errors="replace")
                               for f in files)
            code[m.group(1)] = text
    out = []
    for a in sorted(code, key=int):
        rs = {d: grades.get((a, d), {}) for d in MEN_DIMS}
        if all(len(rs[d]) >= 3 for d in MEN_DIMS):
            c = code[a]
            trunc = len(c) > MENAGERIE_MAX_CHARS
            out.append(dict(id=a, q=a, code=c[:MENAGERIE_MAX_CHARS] + ("\n\n// [truncated]" if trunc else ""),
                            truncated=trunc, raters=rs,
                            h={d: float(np.mean(list(rs[d].values()))) for d in MEN_DIMS}))
    return out


# ---------------------------------------------------------------- prompts (fixed before any call)

CHECKLIST_MOHLER = """You are designing a precise grading checklist for short answers to one question from an undergraduate data structures course.

Question: {question}

Reference answer (written by the instructor): {ref}

Write between 3 and 8 yes/no checks that a grader will answer about each student answer to this question. Requirements:
- each check asks about exactly one thing;
- each check can be answered from the student's answer (the grader also sees the question and the reference answer);
- a fully correct and complete answer receives YES on every check;
- the share of YES answers should reflect how good the answer is;
- phrase every check so that YES is the desirable outcome.

Reply with ONLY strict JSON, no prose and no code fence: {{"checks": ["...", "..."]}}"""

CHECKLIST_MENAGERIE = """Below is one dimension of the marking rubric that human graders used for a first-year Java programming coursework, with its definition and its grade bands from best to worst.

Dimension: {dim}
Definition: {definition}

Bands:
{bands}

Rewrite this dimension as a checklist of between 5 and 12 precise yes/no checks that a grader answers about a submission's source code. Requirements:
- each check asks about exactly one observable thing;
- together the checks should cover everything the bands distinguish;
- a submission meriting the top band receives YES on every check;
- the share of YES answers should track the band the submission merits;
- phrase every check so that YES is the desirable outcome.

Reply with ONLY strict JSON, no prose and no code fence: {{"checks": ["...", "..."]}}"""

MOHLER_HEAD = """You are grading a student's short answer to a question from an undergraduate data structures course.

Question: {question}

Reference answer (written by the instructor): {ref}

Student answer: {answer}

"""

MOHLER_LIKERT = MOHLER_HEAD + """Grade the student answer on a scale from 0 to 5 in steps of 0.5, where 5 means fully correct and complete and 0 means entirely wrong or missing.

Reply with ONLY strict JSON, no prose and no code fence: {{"score": <number>}}"""

MOHLER_BOOLEAN = MOHLER_HEAD + """Answer each check below about the student answer with YES or NO.

{checks}

Reply with ONLY strict JSON, no prose and no code fence: {{"answers": ["YES" or "NO", ...]}} with exactly {n} entries, in the order of the checks."""

MEN_HEAD = """You are marking a first-year Java programming coursework submission on four rubric dimensions, each marked separately.

"""

MEN_LIKERT = MEN_HEAD + """{rubric}

For each dimension give one grade on this scale, worst to best: F, D-, D, D+, C-, C, C+, B-, B, B+, A-, A, A+, A++.

Source code:
{code}

Reply with ONLY strict JSON, no prose and no code fence: {{"Correctness": "<grade>", "Code Elegance": "<grade>", "Readability": "<grade>", "Documentation": "<grade>"}}"""

MEN_BOOLEAN = MEN_HEAD + """{rubric}

For each dimension, answer each of its checks about the submission with YES or NO.

Source code:
{code}

Reply with ONLY strict JSON, no prose and no code fence: {{{shape}}} where each list has exactly as many "YES" or "NO" entries as that dimension has checks, in order."""

PERTURB_HEAD = """Here is a question from an undergraduate data structures course, the instructor's reference answer, and a student's answer.

Question: {question}

Reference answer: {ref}

Student answer: {answer}

Write two sentences, each of which will be appended to the end of the student answer (separately, never together).
"""

PERTURB_TAIL = """NEUTRAL: one sentence, in the student's voice and style, that is true but adds no claim about the question's key ideas (for example a remark about context or why the topic matters), so that it neither helps nor hurts the answer.

Both sentences must be between 60 and 160 characters long and within 15% of each other in length.

Reply with ONLY strict JSON, no prose and no code fence: {{"treatment": "...", "neutral": "..."}}"""

PERTURB_CONTRA = PERTURB_HEAD + """TREATMENT: one sentence, in the student's voice and style, that makes a clear, specific factual claim about the topic that is FALSE and directly contradicts the key point of the reference answer.
""" + PERTURB_TAIL

PERTURB_STUFF = PERTURB_HEAD + """TREATMENT: one sentence, in the student's voice and style, that mentions the key technical terms of the reference answer without stating the correct relationship between them or explaining them, so that it looks relevant to a keyword-matching grader but adds no correct understanding. It must not be a correct statement of the reference answer's key idea.
""" + PERTURB_TAIL

MANIP = """A question from an undergraduate data structures course and its reference answer:

Question: {question}

Reference answer: {ref}

Two sentences written about this topic:
T: {treatment}
N: {neutral}

Answer four questions with YES or NO:
1. Does sentence T make a claim that is false and contradicts the reference answer?
2. Does sentence T mention the key technical terms of the reference answer?
3. Does sentence T correctly state the key idea of the reference answer?
4. Does sentence N make any claim, correct or incorrect, about the key ideas of the question?

Reply with ONLY strict JSON, no prose and no code fence: {{"answers": ["YES" or "NO", "YES" or "NO", "YES" or "NO", "YES" or "NO"]}}"""

# Expected manipulation-check answers: CONTRA needs Q1 YES, Q4 NO; STUFF needs Q2 YES, Q3 NO, Q4 NO.
MANIP_EXPECT = {"contra": {0: "YES", 3: "NO"}, "stuff": {1: "YES", 2: "NO", 3: "NO"}}


def men_rubric_likert() -> str:
    out = []
    for d in MEN_DIMS:
        bands = "\n".join(f"  {b}: {t}" for b, t in MEN_RUBRIC[d])
        out.append(f"{d}: {MEN_DEF[d]}\nThe marking rubric for this dimension, best to worst:\n{bands}")
    return "\n\n".join(out)


def men_rubric_boolean(checks: dict[str, list[str]]) -> str:
    out = []
    for d in MEN_DIMS:
        cl = "\n".join(f"  {i + 1}. {c}" for i, c in enumerate(checks[d]))
        out.append(f"{d}: {MEN_DEF[d]}\nChecks:\n{cl}")
    return "\n\n".join(out)


# ---------------------------------------------------------------- statistics (shared by floor and run)

def wcorr(W: np.ndarray, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Pearson r of x and y under each row of item weights W (B x n)."""
    S = W.sum(1)
    mx, my = W @ x / S, W @ y / S
    cxy = W @ (x * y) / S - mx * my
    vx = W @ (x * x) / S - mx * mx
    vy = W @ (y * y) / S - my * my
    with np.errstate(invalid="ignore", divide="ignore"):
        return cxy / np.sqrt(vx * vy)


def wmean(W: np.ndarray, x: np.ndarray) -> np.ndarray:
    return W @ x / W.sum(1)


def weights(groups: np.ndarray, rng: np.random.Generator, B: int = BOOT) -> np.ndarray:
    """Row 0 is the sample itself; rows 1..B are cluster-bootstrap resamples as item weights."""
    _, g = np.unique(groups, return_inverse=True)
    G = g.max() + 1
    cw = rng.multinomial(G, np.full(G, 1 / G), size=B).astype(float)
    return np.vstack([np.ones(len(g)), cw[:, g]])


def summ(v: np.ndarray) -> dict:
    """Point (row 0) and percentile intervals over rows 1.. ."""
    b = v[1:][~np.isnan(v[1:])]
    p = lambda q: float(np.percentile(b, q))
    return dict(est=float(v[0]), ci95=[p(2.5), p(97.5)], ci90=[p(5), p(95)])


def three_way(s: dict, margin: float, pos: str, neg: str) -> str:
    lo, hi = s["ci95"]
    if lo > 0:
        return pos
    if hi < 0:
        return neg
    if margin and -margin < s["ci90"][0] and s["ci90"][1] < margin:
        return "EQUIVALENT"
    return "UNRESOLVED"


def table_stats(W: np.ndarray, h: np.ndarray, x: dict) -> dict:
    """x[model][arm] is (2, n) reps on the 0-1 scale. Returns arrays over W's rows."""
    ms = sorted(x)
    o = {}
    for m in ms:
        for a in ARMS:
            r0, r1 = x[m][a]
            o[f"V.{m}.{a}"] = wcorr(W, (r0 + r1) / 2, h)
            o[f"R.{m}.{a}"] = wcorr(W, r0, r1)
    for a in ARMS:
        o[f"X.{a}"] = wcorr(W, x[ms[0]][a].mean(0), x[ms[1]][a].mean(0))
    o["dV"] = np.mean([o[f"V.{m}.boolean"] - o[f"V.{m}.likert"] for m in ms], 0)
    o["dR"] = np.mean([o[f"R.{m}.boolean"] - o[f"R.{m}.likert"] for m in ms], 0)
    o["dX"] = o["X.boolean"] - o["X.likert"]
    for m in ms:
        o[f"dV.{m}"] = o[f"V.{m}.boolean"] - o[f"V.{m}.likert"]
        o[f"dR.{m}"] = o[f"R.{m}.boolean"] - o[f"R.{m}.likert"]
    return o


def table_verdicts(o: dict) -> dict:
    s = {k: summ(v) for k, v in o.items()}
    ms = sorted({k.split(".")[1] for k in o if k.startswith("V.")})
    v = dict(
        validity=three_way(s["dV"], MARGIN_V, "BOOLEAN-MORE-VALID", "LIKERT-MORE-VALID"),
        retest=three_way(s["dR"], MARGIN_R, "BOOLEAN-MORE-RELIABLE", "LIKERT-MORE-RELIABLE"),
        cross_model=three_way(s["dX"], MARGIN_R, "BOOLEAN-MORE-RELIABLE", "LIKERT-MORE-RELIABLE"),
        validity_by_model={m: three_way(s[f"dV.{m}"], MARGIN_V, "BOOLEAN-MORE-VALID", "LIKERT-MORE-VALID") for m in ms},
        retest_by_model={m: three_way(s[f"dR.{m}"], MARGIN_R, "BOOLEAN-MORE-RELIABLE", "LIKERT-MORE-RELIABLE") for m in ms},
        validity_consistent=bool(len({np.sign(s[f"dV.{m}"]["est"]) for m in ms}) == 1),
    )
    return dict(stats=s, verdicts=v)


def perturb_stats(W: np.ndarray, x: dict) -> dict:
    """x[model][arm] = dict(treat=(2,n), neutral=(2,n)) on the 0-1 scale."""
    ms = sorted(x)
    o = {}
    for m in ms:
        for a in ARMS:
            o[f"D.{m}.{a}"] = wmean(W, x[m][a]["treat"].mean(0) - x[m][a]["neutral"].mean(0))
        o[f"C.{m}"] = o[f"D.{m}.boolean"] - o[f"D.{m}.likert"]
    for a in ARMS:
        o[f"D.{a}"] = np.mean([o[f"D.{m}.{a}"] for m in ms], 0)
    o["C"] = o["D.boolean"] - o["D.likert"]
    return o


def contra_verdict(s: dict, c: str = "C", dl: str = "D.likert") -> str:
    if not s[dl]["ci95"][1] < 0:
        return "LIKERT-ALSO-BLIND"
    if s[c]["ci95"][0] > 0:
        return "CHECKLIST-BLIND-TO-CONTRADICTION"
    if s[c]["ci95"][1] < 0:
        return "CHECKLIST-MORE-SENSITIVE"
    return "NO-DIFFERENCE-RESOLVED"


def stuff_verdict(s: dict, c: str = "C") -> str:
    if s[c]["ci95"][0] > 0:
        return "CHECKLIST-REWARDS-STUFFING"
    if s[c]["ci95"][1] < 0:
        return "LIKERT-REWARDS-STUFFING-MORE"
    return "NO-DIFFERENCE-RESOLVED"


def perturb_verdicts(o: dict, kind: str) -> dict:
    s = {k: summ(v) for k, v in o.items()}
    ms = sorted({k.split(".")[1] for k in o if k.startswith("C.")})
    if kind == "contra":
        v = dict(pooled=contra_verdict(s), by_model={m: contra_verdict(s, f"C.{m}", f"D.{m}.likert") for m in ms})
    else:
        v = dict(pooled=stuff_verdict(s), by_model={m: stuff_verdict(s, f"C.{m}") for m in ms})
    v["consistent"] = bool(len({np.sign(s[f"C.{m}"]["est"]) for m in ms}) == 1)
    return dict(stats=s, verdicts=v)


def partials(h: np.ndarray, L: np.ndarray, Bo: np.ndarray) -> dict:
    """Descriptive only (see the docstring): partial r(h, L | Bo) and r(h, Bo | L)."""
    r = np.corrcoef([h, L, Bo])
    p = lambda a, b, c: (r[a, b] - r[a, c] * r[b, c]) / np.sqrt((1 - r[a, c] ** 2) * (1 - r[b, c] ** 2))
    return dict(likert_given_boolean=float(p(0, 1, 2)), boolean_given_likert=float(p(0, 2, 1)),
                r_likert_boolean=float(r[1, 2]))


def icc31(Y: np.ndarray) -> float:
    """ICC(3,1), consistency, single rater: Y is targets x raters."""
    n, k = Y.shape
    gm = Y.mean()
    ssr = k * ((Y.mean(1) - gm) ** 2).sum()
    ssc = n * ((Y.mean(0) - gm) ** 2).sum()
    sse = ((Y - gm) ** 2).sum() - ssr - ssc
    msr, mse = ssr / (n - 1), sse / ((n - 1) * (k - 1))
    return float((msr - mse) / (msr + (k - 1) * mse))


# ---------------------------------------------------------------- floor

def to_marginal(z: np.ndarray, ref: np.ndarray, levels: np.ndarray) -> np.ndarray:
    """Map z onto the empirical marginal of ref (by rank), then snap to the nearest level."""
    q = (np.argsort(np.argsort(z)) + 0.5) / len(z)
    v = np.quantile(ref, q)
    return levels[np.abs(v[:, None] - levels[None, :]).argmin(1)]


def synth_scores(rng, T, h01, lam, mu, sig, grid):
    levels = np.linspace(0, 1, grid)
    S = rng.standard_normal(len(T))
    reps = []
    for _ in REPS:
        z = lam * T + mu * S + sig * rng.standard_normal(len(T))
        reps.append(to_marginal(z, h01, levels))
    return np.array(reps)


def params(validity: float, retest: float, c: float) -> tuple[float, float, float]:
    """lam, mu, sigma so that r(rep, rep') = retest and r(mean of 2 reps, h) = validity, given
    r(T, h) = c, with lam^2 + mu^2 + sigma^2 = 1."""
    sig2 = 1 - retest
    lam = validity * np.sqrt(retest + sig2 / 2) / c
    mu2 = retest - lam ** 2
    if mu2 < 0:
        raise ValueError(f"validity {validity} unreachable at retest {retest}, c {c}")
    return float(lam), float(np.sqrt(mu2)), float(np.sqrt(sig2))


def floor_tables(rng, groups, h, c, grids, arms_spec, reps=200):
    """arms_spec: dict arm -> (validity, retest); grids: dict arm -> output levels. Verdict shares."""
    out = Counter()
    h01 = (h - h.min()) / (h.max() - h.min())
    for _ in range(reps):
        T = c * (h - h.mean()) / h.std() + np.sqrt(1 - c ** 2) * rng.standard_normal(len(h))
        x = {m: {a: synth_scores(rng, T, h01, *params(*arms_spec[a], c), grids[a]) for a in ARMS} for m in GRADERS}
        W = weights(groups, rng)
        res = table_verdicts(table_stats(W, h, x))["verdicts"]
        out[("validity", res["validity"])] += 1
        out[("retest", res["retest"])] += 1
        out[("cross_model", res["cross_model"])] += 1
    return {f"{k}={v}": n / reps for (k, v), n in sorted(out.items())}


def floor_perturb(rng, groups, dL, dB, kind, reps=200, sd=0.20, noise=0.10):
    out = Counter()
    n = len(groups)
    for _ in range(reps):
        x = {}
        for m in GRADERS:
            x[m] = {}
            for a, d in (("likert", dL), ("boolean", dB)):
                base = rng.uniform(0.3, 0.9, n)
                eff = d + sd * rng.standard_normal(n)
                x[m][a] = dict(neutral=np.array([base + noise * rng.standard_normal(n) for _ in REPS]),
                               treat=np.array([base + eff + noise * rng.standard_normal(n) for _ in REPS]))
        W = weights(groups, rng)
        out[perturb_verdicts(perturb_stats(W, x), kind)["verdicts"]["pooled"]] += 1
    return {k: v / reps for k, v in sorted(out.items())}


def menagerie_ceiling(items: list[dict], dim: str) -> tuple[float, float, float]:
    """Leave-one-rater-out r(one rater, mean of the others), pooled; mean rater count; the
    Spearman-Brown reliability of the full mean implied by it."""
    a, b, k = [], [], []
    for it in items:
        g = it["raters"][dim]
        g = list(g.values()) if isinstance(g, dict) else list(g)
        k.append(len(g))
        for i in range(len(g)):
            a.append(g[i])
            b.append(np.mean(g[:i] + g[i + 1:]))
    r_loo = float(np.corrcoef(a, b)[0, 1])
    kbar = float(np.mean(k))
    # r(one, mean of k-1 others) = sqrt(rho1) * sqrt(rel_{k-1}); solve for single-rater rho1.
    rho1 = _solve_rho1(r_loo, kbar - 1)
    rel = kbar * rho1 / (1 + (kbar - 1) * rho1)
    return r_loo, kbar, float(rel)


def _solve_rho1(r_loo: float, m: float) -> float:
    lo, hi = 1e-6, 1 - 1e-6
    for _ in range(100):
        mid = (lo + hi) / 2
        rel_m = m * mid / (1 + (m - 1) * mid)
        if np.sqrt(mid * rel_m) < r_loo:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


SAME_M, REAL_M = {"likert": 11, "boolean": 11}, {"likert": 11, "boolean": 7}
SAME_N, REAL_N = {"likert": 14, "boolean": 14}, {"likert": 14, "boolean": 7}


def run_floor(cases: Path = RELEASE_CASES) -> None:
    rng = np.random.default_rng(SEED)
    C = load_cases(cases)
    main, high, low = C["main"], C["high"], C["low"]
    g = np.array([r["q"] for r in main])
    h = np.array([r["h"] for r in main])
    r12 = float(np.corrcoef([r["g1"] for r in main], [r["g2"] for r in main])[0, 1])
    c_m = float(np.sqrt(2 * r12 / (1 + r12)))
    men = C["menagerie"]
    gm = np.array([it["id"] for it in men])
    hm = np.array([it["h"]["Code Elegance"] for it in men])
    _, _, rel_m = menagerie_ceiling(men, "Code Elegance")
    c_n = float(np.sqrt(rel_m))
    res = dict(mohler=dict(n=len(main), clusters=len(set(g)), r12=r12, c=c_m),
               menagerie=dict(n=len(men), c=c_n, dim="Code Elegance"))
    t0 = time.time()
    W = dict(
        # Revision 1: the null worlds put both arms on the same output grid (rev 0 gave them their
        # real grids, and the coarser boolean grid alone lowered its retest r, so the "null" was not
        # null); GRID worlds measure that grid-only cost with everything else equal.
        mohler_NULL=floor_tables(rng, g, h, c_m, SAME_M, {"likert": (0.65, 0.85), "boolean": (0.65, 0.85)}),
        mohler_GRID=floor_tables(rng, g, h, c_m, REAL_M, {"likert": (0.65, 0.85), "boolean": (0.65, 0.85)}),
        mohler_Vplus=floor_tables(rng, g, h, c_m, REAL_M, {"likert": (0.65, 0.85), "boolean": (0.73, 0.85)}),
        mohler_Vminus=floor_tables(rng, g, h, c_m, REAL_M, {"likert": (0.65, 0.85), "boolean": (0.57, 0.85)}),
        mohler_Rplus=floor_tables(rng, g, h, c_m, REAL_M, {"likert": (0.65, 0.85), "boolean": (0.65, 0.92)}),
        menagerie_NULL=floor_tables(rng, gm, hm, c_n, SAME_N, {"likert": (0.45, 0.85), "boolean": (0.45, 0.85)}),
        menagerie_GRID=floor_tables(rng, gm, hm, c_n, REAL_N, {"likert": (0.45, 0.85), "boolean": (0.45, 0.85)}),
        menagerie_Vplus=floor_tables(rng, gm, hm, c_n, REAL_N, {"likert": (0.45, 0.85), "boolean": (0.55, 0.85)}),
        menagerie_Vminus=floor_tables(rng, gm, hm, c_n, REAL_N, {"likert": (0.45, 0.85), "boolean": (0.35, 0.85)}),
        menagerie_Vplus15=floor_tables(rng, gm, hm, c_n, REAL_N, {"likert": (0.45, 0.85), "boolean": (0.60, 0.85)}),
        menagerie_Vminus15=floor_tables(rng, gm, hm, c_n, REAL_N, {"likert": (0.45, 0.85), "boolean": (0.30, 0.85)}),
    )
    gh = np.array([r["q"] for r in high])
    gl = np.array([r["q"] for r in low])
    W.update(
        CONTRA=floor_perturb(rng, gh, -0.20, -0.08, "contra"),
        CONTRA0=floor_perturb(rng, gh, -0.20, -0.20, "contra"),
        BLIND=floor_perturb(rng, gh, 0.0, 0.0, "contra"),
        STUFF=floor_perturb(rng, gl, 0.02, 0.10, "stuff"),
        STUFF0=floor_perturb(rng, gl, 0.02, 0.02, "stuff"),
    )
    res["worlds"] = W
    res["perturb_n"] = dict(high=len(high), low=len(low), high_clusters=len(set(gh)), low_clusters=len(set(gl)))
    get = lambda w, k: W[w].get(k, 0.0)
    checks = {
        "mohler NULL validity signed <= 0.10": get("mohler_NULL", "validity=BOOLEAN-MORE-VALID") + get("mohler_NULL", "validity=LIKERT-MORE-VALID") <= 0.10,
        "mohler NULL retest signed <= 0.10": get("mohler_NULL", "retest=BOOLEAN-MORE-RELIABLE") + get("mohler_NULL", "retest=LIKERT-MORE-RELIABLE") <= 0.10,
        "mohler NULL cross-model signed <= 0.10": get("mohler_NULL", "cross_model=BOOLEAN-MORE-RELIABLE") + get("mohler_NULL", "cross_model=LIKERT-MORE-RELIABLE") <= 0.10,
        "mohler V+ >= 0.80": get("mohler_Vplus", "validity=BOOLEAN-MORE-VALID") >= 0.80,
        "mohler V+ wrong sign <= 0.05": get("mohler_Vplus", "validity=LIKERT-MORE-VALID") <= 0.05,
        "mohler V- >= 0.80": get("mohler_Vminus", "validity=LIKERT-MORE-VALID") >= 0.80,
        "mohler V- wrong sign <= 0.05": get("mohler_Vminus", "validity=BOOLEAN-MORE-VALID") <= 0.05,
        "mohler R+ retest >= 0.80": get("mohler_Rplus", "retest=BOOLEAN-MORE-RELIABLE") >= 0.80,
        "menagerie NULL validity signed <= 0.10": get("menagerie_NULL", "validity=BOOLEAN-MORE-VALID") + get("menagerie_NULL", "validity=LIKERT-MORE-VALID") <= 0.10,
        "menagerie NULL retest signed <= 0.10": get("menagerie_NULL", "retest=BOOLEAN-MORE-RELIABLE") + get("menagerie_NULL", "retest=LIKERT-MORE-RELIABLE") <= 0.10,
        "menagerie V+0.15 >= 0.80": get("menagerie_Vplus15", "validity=BOOLEAN-MORE-VALID") >= 0.80,
        "menagerie V-0.15 >= 0.80": get("menagerie_Vminus15", "validity=LIKERT-MORE-VALID") >= 0.80,
        "menagerie wrong sign <= 0.05": max(get(w, "validity=LIKERT-MORE-VALID") for w in ("menagerie_Vplus", "menagerie_Vplus15")) + max(get(w, "validity=BOOLEAN-MORE-VALID") for w in ("menagerie_Vminus", "menagerie_Vminus15")) <= 0.05,
        "CONTRA >= 0.80": get("CONTRA", "CHECKLIST-BLIND-TO-CONTRADICTION") >= 0.80,
        "CONTRA0 <= 0.10": get("CONTRA0", "CHECKLIST-BLIND-TO-CONTRADICTION") <= 0.10,
        "BLIND LIKERT-ALSO-BLIND >= 0.80": get("BLIND", "LIKERT-ALSO-BLIND") >= 0.80,
        "STUFF >= 0.80": get("STUFF", "CHECKLIST-REWARDS-STUFFING") >= 0.80,
        "STUFF0 <= 0.10": get("STUFF0", "CHECKLIST-REWARDS-STUFFING") <= 0.10,
    }
    res["reported_not_gated"] = {
        "menagerie V+0.10 BOOLEAN-MORE-VALID": get("menagerie_Vplus", "validity=BOOLEAN-MORE-VALID"),
        "menagerie V-0.10 LIKERT-MORE-VALID": get("menagerie_Vminus", "validity=LIKERT-MORE-VALID"),
        "mohler GRID retest LIKERT-MORE-RELIABLE": get("mohler_GRID", "retest=LIKERT-MORE-RELIABLE"),
        "menagerie GRID retest LIKERT-MORE-RELIABLE": get("menagerie_GRID", "retest=LIKERT-MORE-RELIABLE"),
    }
    res["revision"] = 1
    res["checks"] = checks
    res["passed"] = all(checks.values())
    res["seconds"] = round(time.time() - t0)
    OUT.mkdir(exist_ok=True)
    (OUT / "floor.json").write_text(json.dumps(res, indent=1))
    for k, v in checks.items():
        print(("PASS " if v else "FAIL ") + k)
    print(json.dumps(W, indent=1))
    print("FLOOR", "PASSED" if res["passed"] else "FAILED")


# ---------------------------------------------------------------- model calls

_lock = threading.Lock()
SPEND = Counter()


def _post(url: str, body: dict, headers: dict, timeout: int = 300) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def call(api: str, model: str, prompt: str, rep: int, *, effort: str = "low") -> dict:
    """One cached call. Returns {"text", "served", "usage"} or {"error"}."""
    key = hashlib.sha256(json.dumps([api, model, prompt, rep, effort]).encode()).hexdigest()
    path = SCR / "cache" / key[:2] / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text())
    last = ""
    for attempt in range(6):
        try:
            if api == "google":
                k = os.environ["GOOGLE_GENERATIVE_AI_API_KEY"]
                d = _post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                          dict(contents=[dict(role="user", parts=[dict(text=prompt)])],
                               generationConfig=dict(responseMimeType="application/json")),
                          {"x-goog-api-key": k})
                cand = d["candidates"][0]
                text = "".join(p.get("text", "") for p in cand["content"]["parts"] if not p.get("thought"))
                out = dict(text=text, served=d.get("modelVersion"), usage=d.get("usageMetadata"))
            else:
                k = os.environ["OPENAI_API_KEY"]
                d = _post("https://api.openai.com/v1/chat/completions",
                          dict(model=model, messages=[dict(role="user", content=prompt)],
                               response_format=dict(type="json_object"), reasoning_effort=effort),
                          {"Authorization": f"Bearer {k}"})
                out = dict(text=d["choices"][0]["message"]["content"], served=d.get("model"), usage=d.get("usage"))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(out))
            with _lock:
                SPEND[(model, "calls")] += 1
                u = out.get("usage") or {}
                SPEND[(model, "in")] += u.get("prompt_tokens", u.get("promptTokenCount", 0)) or 0
                SPEND[(model, "out")] += (u.get("completion_tokens", 0) or 0) + (u.get("candidatesTokenCount", 0) or 0) + (u.get("thoughtsTokenCount", 0) or 0)
            return out
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read()[:300]!r}"
            if e.code in (400, 401, 403, 404):
                break
        except Exception as e:  # noqa: BLE001 -- network faults are retried, then recorded
            last = f"{type(e).__name__}: {e}"
        time.sleep(min(60, 2 ** attempt + np.random.random()))
    return dict(error=last)


def parse_json(text: str) -> dict | None:
    t = re.sub(r"^```(json)?|```$", "", (text or "").strip(), flags=re.M).strip()
    try:
        return json.loads(t)
    except Exception:  # noqa: BLE001
        m = re.search(r"\{.*\}", t, re.S)
        try:
            return json.loads(m.group(0)) if m else None
        except Exception:  # noqa: BLE001
            return None


def pmap(fn, jobs, workers=16):
    with cf.ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(fn, j): j for j in jobs}
        out = {}
        for i, f in enumerate(cf.as_completed(futs), 1):
            out[futs[f]] = f.result()
            if i % 200 == 0:
                print(f"  {i}/{len(jobs)}", flush=True)
    return out


def sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


# ---------------------------------------------------------------- build: checklists

def build() -> None:
    rows = load_mohler()
    main, high, low = mohler_draws(rows)
    qs = {}
    for r in main + high + low:
        qs[r["q"]] = (r["question"], r["ref"])
    jobs = [("mohler", q) for q in sorted(qs)] + [("menagerie", d) for d in MEN_DIMS]

    def author(job):
        kind, k = job
        if kind == "mohler":
            p = CHECKLIST_MOHLER.format(question=qs[k][0], ref=qs[k][1])
            lo, hi = 3, 8
        else:
            bands = "\n".join(f"  {b}: {t}" for b, t in MEN_RUBRIC[k])
            p = CHECKLIST_MENAGERIE.format(dim=k, definition=MEN_DEF[k], bands=bands)
            lo, hi = 5, 12
        for rep in range(3):
            r = call(*AUTHOR, p, rep, effort="medium")
            j = parse_json(r.get("text", ""))
            ch = [c.strip() for c in (j or {}).get("checks", []) if isinstance(c, str) and c.strip()]
            if lo <= len(ch) <= hi:
                return ch
        raise SystemExit(f"checklist for {job} failed after 3 attempts: {r}")

    got = pmap(author, jobs, workers=8)
    mohler = {q: got[("mohler", q)] for q in sorted(qs)}
    men = {d: got[("menagerie", d)] for d in MEN_DIMS}
    SCR.mkdir(parents=True, exist_ok=True)
    frozen = dict(mohler=mohler, menagerie=men)
    (SCR / "checklists.json").write_text(json.dumps(frozen, indent=1))
    n_m = [len(v) for v in mohler.values()]
    noerr = {q: any(NO_ERROR_PATTERN.search(c) for c in v) for q, v in mohler.items()}
    summary = dict(
        author=dict(api=AUTHOR[0], model=AUTHOR[1], reasoning_effort="medium",
                    prompts=dict(mohler=sha(CHECKLIST_MOHLER), menagerie=sha(CHECKLIST_MENAGERIE))),
        sha256=sha(frozen), mohler_sha256=sha(mohler),
        mohler=dict(questions=len(mohler), checks_total=sum(n_m), checks_per_question=dict(Counter(n_m)),
                    with_no_error_check=sum(noerr.values()), no_error_by_question=noerr,
                    note="checklists paraphrase the corpus's reference answers; kept in scratch, hash here"),
        menagerie=dict(checks=men, counts={d: len(v) for d, v in men.items()},
                       with_no_error_check={d: any(NO_ERROR_PATTERN.search(c) for c in v) for d, v in men.items()}),
        spend={f"{m}:{k}": v for (m, k), v in SPEND.items()},
    )
    OUT.mkdir(exist_ok=True)
    (OUT / "checklists.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps({k: v for k, v in summary.items() if k != "menagerie"}, indent=1)[:2000])
    print(json.dumps(men, indent=1))


# ---------------------------------------------------------------- perturbations

def perturb() -> None:
    rows = load_mohler()
    _, high, low = mohler_draws(rows)
    jobs = [("contra", r["id"]) for r in high] + [("stuff", r["id"]) for r in low]
    by = {r["id"]: r for r in high + low}

    def gen(job):
        kind, i = job
        r = by[i]
        tmpl = PERTURB_CONTRA if kind == "contra" else PERTURB_STUFF
        p = tmpl.format(question=r["question"], ref=r["ref"], answer=r["answer"])
        for rep in range(2):
            j = parse_json(call(*AUTHOR, p, rep, effort="medium").get("text", "")) or {}
            t, n = (j.get("treatment") or "").strip(), (j.get("neutral") or "").strip()
            if t and n and 0.75 <= len(n) / len(t) <= 1.33:
                break
        else:
            return dict(ok=False, reason="size or parse", treatment=t, neutral=n)
        m = parse_json(call(*CHECKER, MANIP.format(question=r["question"], ref=r["ref"], treatment=t, neutral=n), 0).get("text", "")) or {}
        ans = [str(a).upper() for a in m.get("answers", [])]
        passed = len(ans) == 4 and all(ans[q] == want for q, want in MANIP_EXPECT[kind].items())
        return dict(ok=True, treatment=t, neutral=n, manip=ans, manip_pass=passed)

    got = pmap(gen, jobs, workers=8)
    pert = {f"{k}:{i}": v for (k, i), v in got.items()}
    (SCR / "perturbations.json").write_text(json.dumps(pert, indent=1))
    summ_ = {}
    for kind in ("contra", "stuff"):
        ok = [v for (k, _), v in got.items() if k == kind and v["ok"]]
        lt = [len(v["treatment"]) for v in ok]
        ln = [len(v["neutral"]) for v in ok]
        sizes = {f"T{i}": a for i, a in enumerate(lt)} | {f"N{i}": b for i, b in enumerate(ln)}
        cs = check_control_scale(sizes, [f"N{i}" for i in range(len(ln))])
        ratio = float(np.mean(ln) / np.mean(lt))
        if abs(ratio - 1) > 0.10:
            raise SystemExit(f"{kind}: mean neutral/treatment length ratio {ratio:.3f} outside +/-10%")
        summ_[kind] = dict(requested=sum(1 for k, _ in got if k == kind), kept=len(ok),
                           dropped_size_or_parse=sum(1 for (k, _), v in got.items() if k == kind and not v["ok"]),
                           manip_pass=sum(v["manip_pass"] for v in ok),
                           manip_answer_rates=[dict(Counter(v["manip"][q] if len(v["manip"]) == 4 else "?" for v in ok)) for q in range(4)],
                           mean_chars_treatment=float(np.mean(lt)), mean_chars_neutral=float(np.mean(ln)),
                           mean_ratio=ratio,
                           control_scale=dict(ok=cs["ok"], median_treatment=cs["median_treatment"],
                                              min_ratio=min(cs["ratios"].values()), max_ratio=max(cs["ratios"].values()),
                                              uncovered=len(cs["uncovered"])))
    summ_["sha256"] = sha(pert)
    summ_["prompts"] = dict(contra=sha(PERTURB_CONTRA), stuff=sha(PERTURB_STUFF), manip=sha(MANIP))
    summ_["checker"] = dict(api=CHECKER[0], model=CHECKER[1])
    summ_["spend"] = {f"{m}:{k}": v for (m, k), v in SPEND.items()}
    (OUT / "perturb.json").write_text(json.dumps(summ_, indent=1))
    print(json.dumps(summ_, indent=1))


# ---------------------------------------------------------------- grading run

def mohler_prompt(arm: str, r: dict, answer: str, checks: list[str]) -> str:
    if arm == "likert":
        return MOHLER_LIKERT.format(question=r["question"], ref=r["ref"], answer=answer)
    cl = "\n".join(f"{i + 1}. {c}" for i, c in enumerate(checks))
    return MOHLER_BOOLEAN.format(question=r["question"], ref=r["ref"], answer=answer, checks=cl, n=len(checks))


def score_mohler(arm: str, res: dict, n_checks: int):
    j = parse_json(res.get("text", "")) if "text" in res else None
    if not isinstance(j, dict):
        return None, None
    if arm == "likert":
        try:
            s = float(j["score"])
        except (KeyError, TypeError, ValueError):
            return None, None
        return (s / 5 if 0 <= s <= 5 else None), None
    a = [str(x).strip().upper() for x in j.get("answers", [])]
    if len(a) != n_checks or any(x not in ("YES", "NO") for x in a):
        return None, None
    v = [x == "YES" for x in a]
    return sum(v) / len(v), v


def score_menagerie(arm: str, res: dict, checks: dict[str, list[str]]):
    j = parse_json(res.get("text", "")) if "text" in res else None
    if not isinstance(j, dict):
        return None
    out = {}
    for d in MEN_DIMS:
        v = j.get(d)
        if arm == "likert":
            if not isinstance(v, str) or v.strip() not in MEN_SCALE:
                return None
            out[d] = (MEN_SCALE.index(v.strip()) / 13, None)
        else:
            a = [str(x).strip().upper() for x in (v or [])] if isinstance(v, list) else []
            if len(a) != len(checks[d]) or any(x not in ("YES", "NO") for x in a):
                return None
            b = [x == "YES" for x in a]
            out[d] = (sum(b) / len(b), b)
    return out


def run(only: str | None = None) -> None:
    rows = load_mohler()
    main, high, low = mohler_draws(rows)
    cl = json.loads((SCR / "checklists.json").read_text())
    frozen = json.loads((OUT / "checklists.json").read_text())
    assert sha(cl) == frozen["sha256"], "checklists changed since they were frozen"
    pert = json.loads((SCR / "perturbations.json").read_text())
    assert sha(pert) == json.loads((OUT / "perturb.json").read_text())["sha256"], "perturbations changed since frozen"
    jobs = []
    if only in (None, "mohler"):
        for r in main:
            for m in GRADERS:
                for a in ARMS:
                    for rep in REPS:
                        jobs.append(("mohler", r["id"], "orig", m, a, rep))
        for kind, rs in (("contra", high), ("stuff", low)):
            for r in rs:
                if not pert[f"{kind}:{r['id']}"]["ok"]:
                    continue
                for form in ("treat", "neutral"):
                    for m in GRADERS:
                        for a in ARMS:
                            for rep in REPS:
                                jobs.append(("mohler", r["id"], f"{kind}-{form}", m, a, rep))
    men = load_menagerie() if only in (None, "menagerie") else []
    for it in men:
        for m in GRADERS:
            for a in ARMS:
                for rep in REPS:
                    jobs.append(("menagerie", it["id"], "orig", m, a, rep))
    by = {r["id"]: r for r in rows}
    menby = {it["id"]: it for it in men}
    rub_l = men_rubric_likert()
    rub_b = men_rubric_boolean(cl["menagerie"])
    shape = ", ".join(f'"{d}": ["YES" or "NO", ...]' for d in MEN_DIMS)

    def do(job):
        corpus, i, form, m, a, rep = job
        if corpus == "mohler":
            r = by[i]
            ans = r["answer"]
            if form != "orig":
                kind, f = form.split("-")
                p_ = pert[f"{kind}:{i}"]
                ans = ans + " " + (p_["treatment"] if f == "treat" else p_["neutral"])
            p = mohler_prompt(a, r, ans, cl["mohler"][r["q"]])
        else:
            it = menby[i]
            p = (MEN_LIKERT.format(rubric=rub_l, code=it["code"]) if a == "likert"
                 else MEN_BOOLEAN.format(rubric=rub_b, code=it["code"], shape=shape))
        return call(*GRADERS[m], p, rep)

    print(f"{len(jobs)} gradings")
    t0 = time.time()
    got = pmap(do, jobs, workers=24)
    dump = []
    for job, res in got.items():
        corpus, i, form, m, a, rep = job
        rec = dict(corpus=corpus, id=i, form=form, model=m, arm=a, rep=rep, served=res.get("served"),
                   error=res.get("error"), usage=res.get("usage"))
        if corpus == "mohler":
            s, v = score_mohler(a, res, len(cl["mohler"][by[i]["q"]]))
            rec.update(score=s, checks=v)
        else:
            sc = score_menagerie(a, res, cl["menagerie"])
            rec.update(scores=None if sc is None else {d: sc[d][0] for d in MEN_DIMS},
                       checks=None if sc is None else {d: sc[d][1] for d in MEN_DIMS})
        dump.append(rec)
    name = f"dump-{only or 'all'}.json"
    (SCR / name).write_text(json.dumps(dump))
    print(f"wrote {SCR / name} in {time.time() - t0:.0f}s; spend {dict(SPEND)}")


# ---------------------------------------------------------------- the published per-case file

def strip(path: Path = RELEASE_CASES) -> None:
    """Write the per-case file the release publishes: ids, human scores, draw membership, checklist
    and perturbation flags, and every grading's scores and per-check YES/NO. No answer, program,
    checklist, perturbation or prompt text. --analyse and --floor run from this file alone."""
    rows = load_mohler()
    main, high, low = mohler_draws(rows)
    cl = json.loads((SCR / "checklists.json").read_text())
    pert = json.loads((SCR / "perturbations.json").read_text())
    men = load_menagerie()
    dump = []
    for f in sorted(SCR.glob("dump-*.json")):
        dump += json.loads(f.read_text())
    draws = defaultdict(list)
    for name, rs in (("main", main), ("high", high), ("low", low)):
        for r in rs:
            draws[r["id"]].append(name)
    lines = [dict(record="study", release="checklist-grading-2026",
                  graders={m: dict(api=a, model=mo) for m, (a, mo) in GRADERS.items()},
                  checklists_sha256=json.loads((OUT / "checklists.json").read_text())["sha256"],
                  perturbations_sha256=json.loads((OUT / "perturb.json").read_text())["sha256"],
                  seed=SEED)]
    for q in sorted(cl["mohler"]):
        lines.append(dict(record="question", corpus="mohler", q=q, n_checks=len(cl["mohler"][q]),
                          no_error_check=any(NO_ERROR_PATTERN.search(c) for c in cl["mohler"][q]),
                          avoid_check=any(AVOID_PATTERN.search(c) for c in cl["mohler"][q]),
                          avoid_by_check=[bool(AVOID_PATTERN.search(c)) for c in cl["mohler"][q]],
                          no_error_by_check=[bool(NO_ERROR_PATTERN.search(c)) for c in cl["mohler"][q]]))
    for d in MEN_DIMS:
        lines.append(dict(record="question", corpus="menagerie", q=d, n_checks=len(cl["menagerie"][d])))
    for r in sorted({r["id"]: r for r in main + high + low}.values(), key=lambda r: r["id"]):
        rec = dict(record="item", corpus="mohler", id=r["id"], q=r["q"], draws=draws[r["id"]],
                   g1=r["g1"], g2=r["g2"], h=r["h"], chars=len(r["answer"]))
        for kind in ("contra", "stuff"):
            p_ = pert.get(f"{kind}:{r['id']}")
            if p_:
                rec[kind] = dict(ok=p_["ok"], manip_pass=p_.get("manip_pass"), manip=p_.get("manip"),
                                 chars_treatment=len(p_["treatment"]), chars_neutral=len(p_["neutral"]))
        lines.append(rec)
    for it in men:
        lines.append(dict(record="item", corpus="menagerie", id=it["id"], q=it["id"], draws=["main"],
                          raters={d: list(it["raters"][d].values()) for d in MEN_DIMS}, h=it["h"],
                          chars=len(it["code"]), truncated=it["truncated"]))
    for d in sorted(dump, key=lambda d: (d["corpus"], d["id"], d["form"], d["model"], d["arm"], d["rep"])):
        u = d.get("usage") or {}
        lines.append(dict(record="grade", corpus=d["corpus"], id=d["id"], form=d["form"], model=d["model"],
                          arm=d["arm"], rep=d["rep"], served=d["served"], error=d["error"],
                          score=d.get("score"), scores=d.get("scores"), checks=d.get("checks"),
                          tokens_in=u.get("prompt_tokens", u.get("promptTokenCount", 0)) or 0,
                          tokens_out=(u.get("completion_tokens", 0) or 0) + (u.get("candidatesTokenCount", 0) or 0)
                          + (u.get("thoughtsTokenCount", 0) or 0)))
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for ln in lines:
            f.write(json.dumps(ln, sort_keys=True, separators=(",", ":")) + "\n")
    print(f"wrote {path}: {len(lines)} lines, sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")


def load_cases(path: Path = RELEASE_CASES) -> dict:
    """Everything --analyse and --floor read, from the published per-case file."""
    C = dict(mohler={}, menagerie=[], qflags={}, dump=[], main=[], high=[], low=[])
    for ln in open(path, encoding="utf-8"):
        r = json.loads(ln)
        if r["record"] == "question" and r["corpus"] == "mohler":
            C["qflags"][r["q"]] = r
        elif r["record"] == "item" and r["corpus"] == "mohler":
            C["mohler"][r["id"]] = r
            for d in r["draws"]:
                C[d].append(r)
        elif r["record"] == "item":
            C["menagerie"].append(r)
        elif r["record"] == "grade":
            C["dump"].append(r)
    key = lambda r: stable_hash((SEED, "p", r["id"]))
    C["main"].sort(key=lambda r: (r["q"], stable_hash((SEED, r["id"]))))
    C["high"].sort(key=key)
    C["low"].sort(key=key)
    C["menagerie"].sort(key=lambda it: int(it["id"]))
    return C


# ---------------------------------------------------------------- analysis

def analyse(cases: Path = RELEASE_CASES) -> None:
    rng = np.random.default_rng(SEED + 1)
    C = load_cases(cases)
    main, high, low = C["main"], C["high"], C["low"]
    by = C["mohler"]
    dump = C["dump"]
    idx = {(d["corpus"], d["id"], d["form"], d["model"], d["arm"], d["rep"]): d for d in dump}
    res = dict(calls=len(dump), failed=sum(1 for d in dump if d.get("error")),
               unparsed=sum(1 for d in dump if not d.get("error") and d.get("score") is None and d.get("scores") is None),
               served=dict(Counter(f"{d['model']}={d['served']}" for d in dump)))
    tok = Counter()
    for d in dump:
        tok[(d["model"], "in")] += d["tokens_in"]
        tok[(d["model"], "out")] += d["tokens_out"]
    res["tokens"] = {f"{m}:{k}": v for (m, k), v in tok.items()}

    def get(corpus, i, form, m, a, rep, dim=None):
        d = idx.get((corpus, i, form, m, a, rep))
        if d is None:
            return None
        return d.get("score") if dim is None else (d.get("scores") or {}).get(dim)

    # --- Mohler main
    ids = [r["id"] for r in main if all(get("mohler", r["id"], "orig", m, a, k) is not None
                                        for m in GRADERS for a in ARMS for k in REPS)]
    h = np.array([by[i]["h"] for i in ids])
    g = np.array([by[i]["q"] for i in ids])
    x = {m: {a: np.array([[get("mohler", i, "orig", m, a, k) for i in ids] for k in REPS]) for a in ARMS} for m in GRADERS}
    W = weights(g, rng)
    t = table_verdicts(table_stats(W, h, x))
    g1 = np.array([by[i]["g1"] for i in ids]); g2 = np.array([by[i]["g2"] for i in ids])
    t["ceiling"] = dict(r_rater1_rater2=summ(wcorr(W, g1, g2)),
                        r_model_vs_one_rater={f"{m}.{a}": dict(rater1=float(np.corrcoef(x[m][a].mean(0), g1)[0, 1]),
                                                               rater2=float(np.corrcoef(x[m][a].mean(0), g2)[0, 1]))
                                              for m in GRADERS for a in ARMS})
    t["n"] = len(ids); t["dropped"] = len(main) - len(ids); t["clusters"] = len(set(g))
    t["descriptive_partials"] = {m: partials(h, x[m]["likert"].mean(0), x[m]["boolean"].mean(0)) for m in GRADERS}
    t["descriptive_partials_note"] = ("Not a missing-children test: two scores of one construct with independent "
                                      "errors each add to the other, so both partials are positive with nothing missing.")
    # P1b: per-tuple ICC, the paper's unit, between the two models
    tuples = []
    for i in ids:
        for k in REPS:
            vg = idx[("mohler", i, "orig", "gemini", "boolean", k)]["checks"]
            vo = idx[("mohler", i, "orig", "gpt", "boolean", k)]["checks"]
            tuples += [(float(a_), float(b_)) for a_, b_ in zip(vg, vo)]
    t["per_tuple_icc"] = dict(
        boolean_item_x_check=icc31(np.array(tuples)),
        boolean_response_level=icc31(np.array([[x["gemini"]["boolean"][k][j], x["gpt"]["boolean"][k][j]] for k in REPS for j in range(len(ids))])),
        likert_response_level=icc31(np.array([[x["gemini"]["likert"][k][j], x["gpt"]["likert"][k][j]] for k in REPS for j in range(len(ids))])),
        note="ICC(3,1) between the two models, pooled over reps; the boolean per-tuple unit is the paper's.")
    # check-level base rates: how much of the per-tuple ICC is between-check variance
    by_check = defaultdict(list)
    for i in ids:
        q = by[i]["q"]
        for m in GRADERS:
            for k in REPS:
                for c, v in enumerate(idx[("mohler", i, "orig", m, "boolean", k)]["checks"]):
                    by_check[(q, c)].append(v)
    rates = np.array([np.mean(v) for v in by_check.values()])
    t["check_base_rates"] = dict(n_checks=len(rates), share_yes_ge_0_9=float(np.mean(rates >= 0.9)),
                                 share_yes_le_0_1=float(np.mean(rates <= 0.1)), mean=float(rates.mean()))
    res["mohler"] = t

    # --- perturbations
    for kind, rs in (("contra", high), ("stuff", low)):
        for subset in ("manip_pass", "all"):
            ids = [r["id"] for r in rs if r[kind]["ok"]
                   and (subset == "all" or r[kind]["manip_pass"])
                   and all(get("mohler", r["id"], f"{kind}-{f}", m, a, k) is not None
                           for f in ("treat", "neutral") for m in GRADERS for a in ARMS for k in REPS)]
            gg = np.array([by[i]["q"] for i in ids])
            xx = {m: {a: {f: np.array([[get("mohler", i, f"{kind}-{f}", m, a, k) for i in ids] for k in REPS])
                          for f in ("treat", "neutral")} for a in ARMS} for m in GRADERS}
            Wp = weights(gg, rng)
            pv = perturb_verdicts(perturb_stats(Wp, xx), kind)
            pv["n"] = len(ids); pv["clusters"] = len(set(gg))
            # descriptive split by whether the question's checklist carries a no-error check
            ne = np.array([C["qflags"][by[i]["q"]]["no_error_check"] for i in ids])
            split = {}
            for lab, mask in (("with_no_error_check", ne), ("without", ~ne)):
                if mask.sum() >= 5:
                    split[lab] = dict(n=int(mask.sum()), **{f"D.{a}": float(np.mean([(xx[m][a]["treat"].mean(0) - xx[m][a]["neutral"].mean(0))[mask].mean() for m in GRADERS])) for a in ARMS})
            pv["split_by_no_error_check"] = split
            # POST HOC, added after reading the checklists and before any grading call: the author
            # wrote many targeted misconception checks ("avoid describing the removal order as
            # first-in-first-out") that NO_ERROR_PATTERN, written for generic ones, does not count.
            av = np.array([C["qflags"][by[i]["q"]]["avoid_check"] for i in ids])
            split = {}
            for lab, mask in (("with_avoid_check", av), ("without", ~av)):
                if mask.sum() >= 5:
                    split[lab] = dict(n=int(mask.sum()), **{f"D.{a}": float(np.mean([(xx[m][a]["treat"].mean(0) - xx[m][a]["neutral"].mean(0))[mask].mean() for m in GRADERS])) for a in ARMS})
            pv["post_hoc_split_by_avoid_check"] = split
            res[f"{kind}_{subset}"] = pv

    # --- Menagerie
    men = C["menagerie"]
    res["menagerie"] = {"truncated": sum(it["truncated"] for it in men)}
    ok = [it for it in men if all(get("menagerie", it["id"], "orig", m, a, k, MEN_DIMS[0]) is not None
                                  for m in GRADERS for a in ARMS for k in REPS)]
    gm = np.array([it["id"] for it in ok])
    Wm = weights(gm, rng)
    for d in MEN_DIMS:
        hm = np.array([it["h"][d] for it in ok])
        xm = {m: {a: np.array([[get("menagerie", it["id"], "orig", m, a, k, d) for it in ok] for k in REPS]) for a in ARMS} for m in GRADERS}
        td = table_verdicts(table_stats(Wm, hm, xm))
        r_loo, kbar, rel = menagerie_ceiling(ok, d)
        td["ceiling"] = dict(r_one_rater_vs_mean_of_others=r_loo, mean_raters=kbar, reliability_of_mean=rel)
        td["n"] = len(ok); td["dropped"] = len(men) - len(ok)
        td["descriptive_partials"] = {m: partials(hm, xm[m]["likert"].mean(0), xm[m]["boolean"].mean(0)) for m in GRADERS}
        res["menagerie"][d] = td
    # POST HOC, added after reading the results: on Menagerie neither grader tracks the raters on most
    # dimensions (gpt-5.4-mini negatively, in both arms), so the format contrast there is between two
    # instruments that do not see the construct. Recorded: each arm's validity on every submission
    # it parsed (the drop rule removes 46: 45 for one model's boolean miscounts, 1 for an unparseable Likert call), its correlation with
    # code length beside the raters', and its mean score (a mean near 1 is a checklist answering YES
    # to everything).
    clen = {it["id"]: it["chars"] for it in men}
    ph = {}
    for m in GRADERS:
        for a in ARMS:
            for d in MEN_DIMS:
                ids = [it["id"] for it in men if all(get("menagerie", it["id"], "orig", m, a, k, d) is not None for k in REPS)]
                s = np.array([np.mean([get("menagerie", i, "orig", m, a, k, d) for k in REPS]) for i in ids])
                hh = np.array([next(it for it in men if it["id"] == i)["h"][d] for i in ids])
                L = np.array([clen[i] for i in ids])
                ph[f"{m}.{a}.{d}"] = dict(n=len(ids), r_human=float(np.corrcoef(s, hh)[0, 1]),
                                          r_score_length=float(np.corrcoef(s, L)[0, 1]),
                                          r_human_length=float(np.corrcoef(hh, L)[0, 1]),
                                          mean_score=float(s.mean()), sd_score=float(s.std()))
    res["menagerie"]["post_hoc_all_parsed"] = ph
    # per-tuple ICC on Menagerie: Likert item x dimension, the paper's unit for a multi-criterion Likert
    lk = [[get("menagerie", it["id"], "orig", m, "likert", k, d) for m in GRADERS] for it in ok for d in MEN_DIMS for k in REPS]
    res["menagerie"]["per_tuple_icc_likert_item_x_dimension"] = icc31(np.array(lk))
    res["menagerie"]["within_dimension_cross_model_r"] = {d: res["menagerie"][d]["stats"]["X.likert"]["est"] for d in MEN_DIMS}

    # --- predictions
    mv = lambda d: res["menagerie"][d]["stats"]["dV"]["est"]
    res["predictions"] = {
        "P1 Mohler dR > 0": res["mohler"]["stats"]["dR"]["est"] > 0,
        "P1 Mohler dX > 0": res["mohler"]["stats"]["dX"]["est"] > 0,
        "P1b per-tuple boolean ICC > response-level boolean ICC": t["per_tuple_icc"]["boolean_item_x_check"] > t["per_tuple_icc"]["boolean_response_level"],
        "P2 Mohler dV >= -0.05": res["mohler"]["stats"]["dV"]["est"] >= -0.05,
        "P2 Documentation dV >= -0.05": mv("Documentation") >= -0.05,
        "P2 Readability dV >= -0.05": mv("Readability") >= -0.05,
        "P2 Code Elegance dV < 0": mv("Code Elegance") < 0,
        "P3 CHECKLIST-BLIND-TO-CONTRADICTION": res["contra_manip_pass"]["verdicts"]["pooled"] == "CHECKLIST-BLIND-TO-CONTRADICTION",
        "P4 CHECKLIST-REWARDS-STUFFING": res["stuff_manip_pass"]["verdicts"]["pooled"] == "CHECKLIST-REWARDS-STUFFING",
    }
    res["paper_rows"] = paper_rows(res)
    (OUT / "results.json").write_text(json.dumps(res, indent=1))
    show(res)


def paper_rows(res: dict) -> dict:
    """The values the article's tables print, row by row and column by column (estimate, then the 95%
    interval's ends), so the report build can recompute every table cell from this output."""
    ci = lambda s: [s["est"], s["ci95"][0], s["ci95"][1]]
    tabs = [("mohler", res["mohler"])] + [(d, res["menagerie"][d]) for d in MEN_DIMS]
    rel, val = {}, {}
    for key, t in tabs:
        s = t["stats"]
        rel[key] = {"1": [s["R.gemini.likert"]["est"], s["R.gemini.boolean"]["est"]],
                    "2": [s["R.gpt.likert"]["est"], s["R.gpt.boolean"]["est"]],
                    "3": ci(s["dR"]), "5": [s["X.likert"]["est"], s["X.boolean"]["est"]], "6": ci(s["dX"])}
        c = t["ceiling"]
        val[key] = {"2": [s["V.gemini.likert"]["est"], s["V.gemini.boolean"]["est"]],
                    "3": [s["V.gpt.likert"]["est"], s["V.gpt.boolean"]["est"]], "4": ci(s["dV"]),
                    "6": [c["r_rater1_rater2"]["est"] if "r_rater1_rater2" in c else c["r_one_rater_vs_mean_of_others"]]}
    defects = {k: {"2": ci(res[k]["stats"]["D.likert"]), "3": ci(res[k]["stats"]["D.boolean"]),
                   "4": ci(res[k]["stats"]["C"])} for k in ("contra_manip_pass", "stuff_manip_pass")}
    return {"reliability": rel, "validity": val, "defects": defects}


def show(res: dict) -> None:
    f = lambda s: f"{s['est']:+.3f} [{s['ci95'][0]:+.3f}, {s['ci95'][1]:+.3f}]"
    print(f"calls {res['calls']}, failed {res['failed']}, unparsed {res['unparsed']}")
    for name, t in [("Mohler", res["mohler"])] + [(f"Menagerie {d}", res["menagerie"][d]) for d in MEN_DIMS]:
        s = t["stats"]
        print(f"\n{name} (n={t['n']}): {t['verdicts']}")
        for m in GRADERS:
            print(f"  {m}: V likert {s[f'V.{m}.likert']['est']:.3f} boolean {s[f'V.{m}.boolean']['est']:.3f} | "
                  f"R likert {s[f'R.{m}.likert']['est']:.3f} boolean {s[f'R.{m}.boolean']['est']:.3f}")
        print(f"  X likert {s['X.likert']['est']:.3f} boolean {s['X.boolean']['est']:.3f}")
        print(f"  dV {f(s['dV'])}  dR {f(s['dR'])}  dX {f(s['dX'])}")
        print(f"  ceiling {t['ceiling'] if 'ceiling' in t else ''}")
    for k in ("contra_manip_pass", "contra_all", "stuff_manip_pass", "stuff_all"):
        p = res[k]
        s = p["stats"]
        print(f"\n{k} (n={p['n']}): {p['verdicts']}  D.likert {f(s['D.likert'])}  D.boolean {f(s['D.boolean'])}  C {f(s['C'])}")
        print(f"  split {p['split_by_no_error_check']}")
    print("\nper-tuple ICC", res["mohler"]["per_tuple_icc"], res["mohler"]["check_base_rates"])
    print("predictions", json.dumps(res["predictions"], indent=1))


def show_draw() -> None:
    rows = load_mohler()
    main, high, low = mohler_draws(rows)
    men = load_menagerie()
    print(f"Mohler: {len(rows)} answers, main {len(main)} over {len({r['q'] for r in main})} questions; "
          f"high {len(high)} over {len({r['q'] for r in high})}; low {len(low)} over {len({r['q'] for r in low})}")
    print(f"Menagerie: {len(men)} submissions, truncated {sum(it['truncated'] for it in men)}, "
          f"mean chars {np.mean([len(it['code']) for it in men]):.0f}")
    for d in MEN_DIMS:
        print(f"  {d}: ceiling {menagerie_ceiling(men, d)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for f in ("draw", "floor", "build", "perturb", "strip", "analyse"):
        ap.add_argument(f"--{f}", action="store_true")
    ap.add_argument("--cases", type=Path, default=RELEASE_CASES,
                    help="the published per-case file (--strip writes it; --floor and --analyse read it)")
    ap.add_argument("--run", nargs="?", const="all")
    a = ap.parse_args()
    if a.draw:
        show_draw()
    if a.strip:
        strip(a.cases)
    if a.floor:
        run_floor(a.cases)
    if a.build:
        build()
    if a.perturb:
        perturb()
    if a.run:
        run(None if a.run == "all" else a.run)
    if a.analyse:
        analyse(a.cases)
