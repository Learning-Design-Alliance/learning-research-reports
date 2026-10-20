"""Distil the EDM Cup 2023 release into one cell table for the A4 directional study.

EDM Cup (osf.io/7stjh) publishes 9,319,676 ASSISTments assignment logs, 576,894 graded
unit-test responses and CCSS skill codes for 99.4% of 132,738 problems.

THE ONE FACT THAT MAKES THIS STUDY POSSIBLE, AND THE TRAP THAT NEARLY KILLED IT.
`assignment_start_time` on a unit-test assignment is not a time. It is the literal string
REMOVED_FOR_EVALUATION -- the competition redacted the clock on exactly the 53,615 rows whose
scores were the prediction target. Read naively that sentinel parses as one constant value, so
every learner appears to have exactly one timestamp, zero ordered skill pairs exist, and the
corpus looks incapable of supporting any directional test. It is a redaction marker, not a
corpus property: all 9,266,061 NON-test assignments keep real epoch times, and none of the
638,528 in-unit practice assignments is redacted.

So the timeline is rebuilt from the practice side. `assignment_relationships` links each unit
test to the in-unit practice assignments that fed it, already per learner. A unit test is
anchored at the LAST practice start time beneath it -- the moment just before the test. That
anchor uses only practice timing; it never consults the CCSS codes or the curriculum order that
the study is trying to recover, so the timeline is independent of the structure under test.

Data handling: ASSISTments is analysis-only, no redistribution. The raw CSVs stay in the session
scratchpad. This script writes one aggregate cell table, also to the scratchpad; only the study's
JSON summaries are committed.
"""
import csv, collections, os, pathlib, sys

SCRATCH = pathlib.Path(os.environ.get("EDMCUP_DIR", "")).expanduser()
if not SCRATCH.is_dir():
    sys.exit("set EDMCUP_DIR to the scratchpad directory holding the EDM Cup CSVs")
OUT = SCRATCH / "cells.tsv"

def main():
    rel = collections.defaultdict(list)
    with open(SCRATCH / "assignment_relationships.csv") as f:
        r = csv.reader(f); next(r)
        for t, i in r:
            rel[t].append(i)
    print("unit tests with practice links %d" % len(rel))

    test_ids = set()
    with open(SCRATCH / "unit_test_scores.csv") as f:
        r = csv.reader(f); next(r)
        for row in r:
            test_ids.add(row[0])

    # one streaming pass over the 966 MB log: learner + class for tests, start time for practice
    tstu, tcls, itime, istu = {}, {}, {}, {}
    need = test_ids | {i for v in rel.values() for i in v}
    with open(SCRATCH / "assignment_details.csv") as f:
        r = csv.reader(f); next(r)
        for row in r:
            a = row[0]
            if a not in need:
                continue
            if a in test_ids:
                tstu[a] = row[3]; tcls[a] = row[2]
            t = row[7]
            if t != "REMOVED_FOR_EVALUATION" and t:
                itime[a] = float(t); istu[a] = row[3]
    print("tests resolved %d   practice times %d" % (len(tstu), len(itime)))

    anchor, unanchored = {}, 0
    for t, ins in rel.items():
        if t not in tstu:
            continue
        s = tstu[t]
        ts = [itime[i] for i in ins if i in itime and istu[i] == s]
        if ts:
            anchor[t] = max(ts)
        else:
            unanchored += 1
    print("anchored %d   unanchored %d" % (len(anchor), unanchored))

    skill = {}
    for row in csv.DictReader(open(SCRATCH / "problem_details.csv")):
        c = (row.get("problem_skill_code") or "").strip()
        if c:
            skill[row["problem_id"]] = c

    agg = collections.defaultdict(lambda: [0.0, 0])
    with open(SCRATCH / "unit_test_scores.csv") as f:
        r = csv.reader(f); next(r)
        for a, p, sc in r:
            k = skill.get(p)
            if k is None or a not in anchor:
                continue
            cell = agg[(a, k)]
            cell[0] += float(sc); cell[1] += 1

    with open(OUT, "w") as f:
        f.write("student\tclass\tskill\ttime\tmean\tn\n")
        for (a, k), (sm, n) in agg.items():
            f.write("%s\t%s\t%s\t%.3f\t%.6f\t%d\n" % (tstu[a], tcls[a], k, anchor[a], sm / n, n))
    print("wrote %s  (%d cells)" % (OUT, len(agg)))

if __name__ == "__main__":
    main()
