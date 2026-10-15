"""NOT PRE-REGISTERED. Why the registered ds1190 re-analysis (patel_order.py part 3) fails on the data.

Written 2026-10-08, AFTER the registered run of patel_order.py on the ds1190 export. That run
completed (exit 0) and printed verdicts, but its outputs did not mean what they say: the "problem"
scoring sat near 0.01-0.04, the "final step" scoring near 0.05-0.16, the "step" scoring near 0.85, and
every "days after last practice" was negative or zero. This script records what each logged value
actually is, so the failure is documented from the data and not asserted. It computes NO order
contrast on any outcome: every accuracy below is pooled over both arms, and the only per-arm figures
are logging variables (how many steps of each kind were logged), which are what the registered
scorings mix into their outcome.

Checks:
  1. STEP ANATOMY. For every test-form problem (items named "T ...") in the five test sets, the
     first-attempt outcome and logged duration of each step kind, pooled over both arms.
     A step that is correct 100% of the time with a 0 s duration is a given (pre-filled) field of
     the problem statement, not a response. A step that is "incorrect" 100% of the time is
     ungraded.
  2. LOGGING BY ARM. Per test set and arm, the mean share of a learner's test steps that are given
     fields, answer fields, and confidence ratings. If these differ between arms, any scoring that
     mixes them has an arm difference that is not performance.
  3. DELAY. The registered delay takes a learner's latest non-"T" row as "last practice". The
     test sets also hold non-"T" items (ComDen, Equiv), so that row is often inside the delayed test
     itself. Reported: the registered definition, and the time from the learner's last row in a
     practice set ("Fraction Arithmetic Blocked 1/2") to the first row of each test.
  4. PROVENANCE. The registered script reads the per-sample exports S2_AM_Blocked and
     S2_MA_Blocked, which data/data-sources.json does not checksum (it records the All Data file).
     This counts the same learners' rows in the registered All Data file, by assignment, so the
     per-sample files are tied to the checksummed export. MD5s of all three files are recorded.

Data: DataShop ds1190 (research use, no redistribution). Reads scratch_root()/ds1190 only; writes
aggregates to out/patel_artefacts.json.

    python3 patel_artefacts.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from shared.paths import scratch_root  # noqa: E402

OUT = HERE / "out"
TESTS = ("Pretest", "Midtest A", "Midtest B", "Posttest", "DPosttest")
GIVEN = {"num1", "den1", "operation1", "num2", "den2"}
ANSWER = {"num3", "den3"}
CONF = {"ConfidenceRating"}


def pset(h):
    m = re.search(r"ProblemSet (.+?)\s*$", h or "")
    return m.group(1) if m else ""


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def ts(s):
    return datetime.fromisoformat(s[:19])


def main() -> None:
    src = scratch_root() / "ds1190"
    files = {tag: next(p for p in src.iterdir() if f"S2_{tag}_Blocked" in p.name) for tag in ("AM", "MA")}
    anatomy = defaultdict(Counter)
    durs = defaultdict(list)
    share = defaultdict(lambda: defaultdict(lambda: defaultdict(Counter)))   # test -> arm -> sid -> kind
    last_nonT, last_practice, first_test = {}, {}, defaultdict(dict)
    rows_per_sid = Counter()
    arm_of = {}
    for tag, f in files.items():
        with open(f, encoding="utf-8", errors="replace") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                sid, s, t = r["Anon Student Id"], pset(r["Problem Hierarchy"]), r["Step Start Time"]
                arm_of[sid] = tag
                rows_per_sid[sid] += 1
                isT = r["Problem Name"].strip().upper().startswith("T ")
                if not isT and t and (sid not in last_nonT or t > last_nonT[sid]):
                    last_nonT[sid] = t
                if s.startswith("Fraction Arithmetic Blocked") and t and (sid not in last_practice or t > last_practice[sid]):
                    last_practice[sid] = t
                if s in TESTS and t and (s not in first_test[sid] or t < first_test[sid][s]):
                    first_test[sid][s] = t
                if s in TESTS and isT:
                    step = r["Step Name"].split(" ")[0]
                    anatomy[step][r["First Attempt"]] += 1
                    try:
                        durs[step].append(float(r["Step Duration (sec)"]))
                    except ValueError:
                        pass
                    kind = "given" if step in GIVEN else "answer" if step in ANSWER else \
                        "confidence" if step in CONF else "other"
                    share[s][tag][sid][kind] += 1

    res = {"note": "NOT PRE-REGISTERED; written after the registered patel_order.py run to document "
                   "why its part 3 fails on the data. No outcome contrast between arms is computed."}
    res["step_anatomy_pooled"] = {
        k: dict(n=sum(c.values()), correct=c["correct"] / sum(c.values()),
                incorrect=c["incorrect"] / sum(c.values()), hint=c["hint"] / sum(c.values()),
                median_duration_s=float(np.median(durs[k])) if durs[k] else None)
        for k, c in anatomy.items()}

    res["logging_share_by_arm"] = {}
    for s in TESTS:
        res["logging_share_by_arm"][s] = {}
        for tag in ("AM", "MA"):
            per = share[s][tag]
            sh = {kind: float(np.mean([c[kind] / sum(c.values()) for c in per.values()]))
                  for kind in ("given", "answer", "confidence", "other")}
            sh["learners"] = len(per)
            sh["learners_with_any_confidence_step"] = sum(1 for c in per.values() if c["confidence"])
            res["logging_share_by_arm"][s][tag] = sh

    delay = {}
    for s in TESTS:
        reg, prac = [], []
        for sid, ft in first_test.items():
            if s not in ft:
                continue
            if sid in last_nonT:
                reg.append((ts(ft[s]) - ts(last_nonT[sid])).total_seconds() / 86400)
            if sid in last_practice:
                prac.append((ts(ft[s]) - ts(last_practice[sid])).total_seconds() / 86400)
        delay[s] = dict(registered_definition_median_days=float(np.median(reg)),
                        from_last_practice_set_row=dict(median=float(np.median(prac)),
                                                        min=float(np.min(prac)), max=float(np.max(prac)),
                                                        n=len(prac)))
    res["delay_days"] = delay

    # provenance: the same learners in the registered All Data file
    alld = next(p for p in src.iterdir() if "All_Data" in p.name)
    in_all = Counter()
    hier = Counter()
    with open(alld, encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            sid = r["Anon Student Id"]
            if sid in arm_of:
                in_all[sid] += 1
                hier[r["Problem Hierarchy"].split(",")[0]] += 1
    res["provenance"] = dict(
        md5={alld.name: md5(alld), **{f.name: md5(f) for f in files.values()}},
        learners=dict(AM=sum(v == "AM" for v in arm_of.values()), MA=sum(v == "MA" for v in arm_of.values())),
        rows_in_samples=sum(rows_per_sid.values()), rows_same_learners_in_all_data=sum(in_all.values()),
        learners_whose_row_counts_match=sum(in_all[s] == rows_per_sid[s] for s in arm_of),
        all_data_assignments_for_these_learners=dict(hier))
    OUT.mkdir(exist_ok=True)
    (OUT / "patel_artefacts.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
