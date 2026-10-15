"""PRE-REGISTERED: do the empty-cell study's two difficulty readings agree with labelled difficulty?

QUESTION
    studies/identifiability/empty-cell/ reads how hard a skill is in two ways, as a descriptive check
    on its EASE label (CHANGES 3): RAW, the skill's first-attempt miss rate over every learner who
    attempted it, and ADJ, the ability-adjusted difficulty, the mean over its attempters of (miss on
    the skill's first attempt) minus (that learner's mean first-attempt miss over the other skills
    they attempted). Both come from the same answers they describe. This study asks whether they
    agree with difficulty labelled from outside those answers. Asked by the maintainer, 2026-10-13.

REFERENCES (each read where it is on disk; one that is absent is reported NOT RUN)
    R1 DBE-KT22 (ADA Dataverse; data/data-sources.json "dbe-kt22"): the course instructors' difficulty
       for every question, 1 easy, 2 medium, 3 hard (Questions.difficulty). Learner answers from its
       Transaction file; the unit is the question. Primary reference: labelled by instructors, not
       estimated from the answers.
    R2 Junyi 2015 raters (junyi2015-authored; shared.junyi_ratings): for rated exercise pairs, the
       mean 1-9 judgement of how much harder the row's prereq exercise is than its dependent (5 =
       equal; Rating.prereq_harder). Learner answers: DataShop ds1275 through
       overlap/atlas.datashop_rows, the unit being the exercise (the atlas's KC). The statistic is
       pairwise: the reading's difference, d(prereq) - d(dependent), against prereq_harder - 5.
       Ceiling: the raters' own split-half agreement on prereq_harder, from each row's raw ratings
       split at random into two halves (rows with at least 2 raters), Spearman over rows,
       Spearman-Brown corrected, reported beside the result.
    R3 PISA 2022 (pisa2022 STU_COG, pisa2022-annex-a): each mathematics item's IRT difficulty from
       the main-survey scaling against RAW and ADJ from the scored item responses (one response per
       student and item). Estimated from responses, but from the full survey with a calibrated model:
       a calibration check, not an independent label. Run only when disk allows (the cognitive file
       expands to several GB); reported NOT RUN otherwise.

READINGS: exactly the empty-cell formulas (first touch, first-attempt outcome, positivity.states),
    reimplemented here as item_difficulty(); before any real reading the script asserts that it
    reproduces empty_cell.difficulty's RAW on a synthetic world to the last digit. An item enters a
    statistic only with at least 20 first attempts.

STATISTICS (signed: a larger reading means harder)
    R1, R3  Spearman rho between the reading and the reference over items.
    R2      Spearman rho between the reading's difference and prereq_harder - 5 over rated pairs whose
            two exercises both qualify; a row rated in both orders counts once per row.
    95% percentile intervals from 1,000 bootstrap draws, seed 20261013, over the unit the label was
    given to: questions (R1), items (R3), rated rows (R2). ADJ minus RAW is a paired difference over
    the same draws.

VERDICTS (per reference and reading; strings fixed here)
    AGREES                 lower bound of rho above +0.3
    WEAKLY AGREES          lower bound above 0, not above +0.3
    DISAGREES              upper bound below 0
    NOT SHOWN TO AGREE     otherwise
    ADJUSTMENT HELPS       lower bound of rho(ADJ) - rho(RAW) above 0; ADJUSTMENT HURTS if the upper
                           bound is below 0; else ADJUSTMENT NOT SHOWN TO DIFFER.

FLOOR (run first; synthetic learners only)
    3,000 learners, ability ~ N(0, 1); 60 items, difficulty b ~ N(0, 1); P(correct) = logistic(ability
    - b); one attempt per item attempted. Labels from the true b: three levels at its tertiles (as R1),
    and 300 random rated pairs, rating 5 + 1.5 (b_B - b_A) + N(0, 1) clipped to 1-9 (as R2).
      random    each learner attempts a random 30 items
                expect RAW and ADJ to AGREE with both labels
      selected  a learner attempts an item with probability logistic(2 x ability x b), so abler learners
                take the harder items and RAW understates their difficulty
                expect ADJ to AGREE with both labels and ADJUSTMENT HELPS on the levels
      null      as random, but the labels are shuffled across items and pairs
                expect ADJ NOT SHOWN TO AGREE with both
    FLOOR PASSES if all ten expectations hold. If ADJ fails in selected, the floor fails and the empty-
    cell study's ability-adjusted reading is reported as not validated, whatever the references say.

OUTPUT (out/): floor.json; result.json (per reference: items or rows used, rho and interval per reading,
    the ADJ - RAW difference, the verdicts, R2's ceiling). No per-learner row.

WHAT IT CAN SAY  Whether two cheap difficulty readings, computed from the answers alone, rank items as
    instructors (R1) and raters (R2) do, and track a calibrated IRT scale (R3).
WHAT IT CANNOT   Whether the readings are right on the seven corpora of the empty-cell study, which have
    no labels; R2's raters are crowd-sourced and their own agreement is the ceiling.

WHAT THE ANALYST HAS SEEN: the registry's codebook entries for the three references; the Junyi
    ratings' use elsewhere in Paper II (raters follow taxonomy distance). No reading has been computed
    on DBE-KT22, ds1275 or PISA for this purpose.

CHANGES (2026-10-13)
    1. SEEN AFTER THIS PRE-REGISTRATION WAS COMMITTED (25d3128), before any reading here: the earlier
       DBE-KT22 study (studies/end-to-end/dbe-kt22-build/README.md) reports Spearman(instructor
       difficulty, training error rate) +0.223 on that corpus, with the error rates' split-half
       reliability 0.991. That is close to R1's RAW statistic (here over all learners, with the 20-
       attempt rule), so R1 RAW is likely to read WEAKLY AGREES. The 0.3 threshold was written before
       that number was read and is not changed.
    2. R2's UNIT (found when R2 first ran and matched no rated pair; no statistic was computed).
       overlap/atlas.datashop_rows reads the first KC column of an export, which for ds1275 is
       KC (Area): 8 subject areas, not exercises (so Table 1's Junyi row is at the area grain, 56
       ordered pairs). The ratings are on exercises, the unit this pre-registration names, so R2 reads
       ds1275's KC (Exercise) column, with datashop_rows's filters otherwise unchanged
       (datashop_rows_at below), as studies/identifiability/junyi/expert_vs_data.py does.
       RECORD: commit ae3d9e1's message says it adds this change; it holds only the NOT RUN result of
       that first attempt, because the edit adding it failed and the commit went ahead. The change is
       in the commit after it.
    3. R1 AND R3 NOT RUN, by decision (maintainer, 2026-10-13, after R2). The difficulty readings are
       descriptive in the empty-cell study, and its real reading found EASE binding at most 16% of empty
       pairs in any corpus (XES3G5M, forward), so validating them further does not bear on the paper's
       claims. R1 (DBE-KT22) and R3 (PISA) are left NOT RUN; they are to be run if a later reading makes
       ease a deciding factor.

    python3 difficulty_validation.py --floor
    python3 difficulty_validation.py [--only R1|R2|R3]
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
sys.path.insert(0, str(ROOT / "studies/identifiability/empty-cell"))
sys.path.insert(0, str(ROOT))
from positivity import states, timelines  # noqa: E402

OUT = HERE / "out"
SEED, B, MIN_ATTEMPTS = 20261013, 1000, 20


def item_difficulty(by_learner):
    """RAW and ADJ per item, the empty-cell formulas (empty_cell.difficulty), with first-attempt counts."""
    _ft, _fp, outcome_at_touch = states(by_learner)
    miss_by_item, learner = {}, {}
    for u, oat in outcome_at_touch.items():
        ms = [0 if ok else 1 for ok in oat.values()]
        learner[u] = (sum(ms), len(ms))
        for it, ok in oat.items():
            miss_by_item.setdefault(it, []).append((u, 0 if ok else 1))
    out = {}
    for it, lst in miss_by_item.items():
        raw = sum(m for _, m in lst) / len(lst)
        d = [m - (learner[u][0] - m) / (learner[u][1] - 1) for u, m in lst if learner[u][1] > 1]
        out[it] = {"n": len(lst), "raw": raw, "adj": (sum(d) / len(d)) if d else None}
    return out


def rho(x, y):
    import empty_cell
    return empty_cell.spearman(list(x), list(y))


def boot_rho(units, f_ref, f_reads, seed=SEED):
    """units: list; f_ref(u) -> reference; f_reads[name](u) -> reading. Resample units."""
    rng = random.Random(seed)
    full = {k: rho([g(u) for u in units], [f_ref(u) for u in units]) for k, g in f_reads.items()}
    draws = {k: [] for k in f_reads}
    for _ in range(B):
        s = [units[rng.randrange(len(units))] for _ in units]
        refs = [f_ref(u) for u in s]
        for k, g in f_reads.items():
            r = rho([g(u) for u in s], refs)
            draws[k].append(r if r is not None else float("nan"))
    def iv(v):
        v = sorted(x for x in v if x == x)
        return v[int(0.025 * len(v))], v[min(len(v) - 1, int(0.975 * len(v)))]
    res = {k: {"rho": full[k], "lo": iv(draws[k])[0], "hi": iv(draws[k])[1]} for k in f_reads}
    if "ADJ" in draws and "RAW" in draws:
        diff = [a - b for a, b in zip(draws["ADJ"], draws["RAW"])]
        lo, hi = iv(diff)
        res["ADJ_minus_RAW"] = {"diff": full["ADJ"] - full["RAW"], "lo": lo, "hi": hi,
                                "verdict": ("ADJUSTMENT HELPS" if lo > 0 else "ADJUSTMENT HURTS" if hi < 0
                                            else "ADJUSTMENT NOT SHOWN TO DIFFER")}
    for k in f_reads:
        r = res[k]
        r["verdict"] = ("AGREES" if r["lo"] > 0.3 else "WEAKLY AGREES" if r["lo"] > 0 else
                        "DISAGREES" if r["hi"] < 0 else "NOT SHOWN TO AGREE")
    res["units"] = len(units)
    return res


def levels_test(d, level):
    items = [i for i in d if d[i]["n"] >= MIN_ATTEMPTS and d[i]["adj"] is not None and i in level]
    return boot_rho(items, lambda i: level[i], {"RAW": lambda i: d[i]["raw"], "ADJ": lambda i: d[i]["adj"]})


def pairs_test(d, rated):
    """rated: list of (harder_candidate, other, rating - 5); reading difference d(harder) - d(other)."""
    ok = lambda i: i in d and d[i]["n"] >= MIN_ATTEMPTS and d[i]["adj"] is not None
    rows = [r for r in rated if ok(r[0]) and ok(r[1])]
    return boot_rho(rows, lambda r: r[2], {"RAW": lambda r: d[r[0]]["raw"] - d[r[1]]["raw"],
                                          "ADJ": lambda r: d[r[0]]["adj"] - d[r[1]]["adj"]})


# ---------------------------------------------------------------- floor

def world(kind, seed):
    rng = random.Random(seed)
    th = [rng.gauss(0, 1) for _ in range(3000)]
    b = {f"i{j:02d}": rng.gauss(0, 1) for j in range(60)}
    items = sorted(b)
    rows, t = [], 0
    for u, a in enumerate(th):
        if kind == "selected":
            chosen = [i for i in items if rng.random() < 1 / (1 + math.exp(-2 * a * b[i]))]
        else:
            chosen = rng.sample(items, 30)
        rng.shuffle(chosen)
        for i in chosen:
            rows.append((f"u{u}", i, rng.random() < 1 / (1 + math.exp(-(a - b[i]))), t, False, False))
            t += 1
    cut = sorted(b.values())
    t1, t2 = cut[20], cut[40]
    level = {i: (1 if v < t1 else 2 if v < t2 else 3) for i, v in b.items()}
    rated = []
    for _ in range(300):
        x, y = rng.sample(items, 2)
        r = min(9, max(1, 5 + 1.5 * (b[x] - b[y]) + rng.gauss(0, 1)))
        rated.append((x, y, r - 5))
    if kind == "null":
        vals = list(level.values())
        rng.shuffle(vals)
        level = dict(zip(level, vals))
        rs = [r[2] for r in rated]
        rng.shuffle(rs)
        rated = [(x, y, r) for (x, y, _), r in zip(rated, rs)]
    return rows, level, rated


EXPECT = {"random": {("levels", "RAW"): {"AGREES"}, ("levels", "ADJ"): {"AGREES"},
                     ("pairs", "RAW"): {"AGREES"}, ("pairs", "ADJ"): {"AGREES"}},
          "selected": {("levels", "ADJ"): {"AGREES"}, ("pairs", "ADJ"): {"AGREES"},
                       ("levels", "ADJ_minus_RAW"): {"ADJUSTMENT HELPS"}},
          "null": {("levels", "ADJ"): {"NOT SHOWN TO AGREE"}, ("pairs", "ADJ"): {"NOT SHOWN TO AGREE"}}}


def floor():
    import empty_cell
    res, ok = {}, True
    for i, kind in enumerate(("random", "selected", "null")):
        rows, level, rated = world(kind, SEED + i)
        bl = timelines(rows)
        d = item_difficulty(bl)
        _, all_miss = empty_cell.difficulty(bl, [], {"forward": [], "backward": []})
        assert all(abs(all_miss[k] - d[k]["raw"]) == 0 for k in d), "RAW differs from empty_cell's"
        r = {"levels": levels_test(d, level), "pairs": pairs_test(d, rated)}
        checks = {}
        for (test, reading), allowed in EXPECT[kind].items():
            got = r[test][reading]["verdict"]
            checks[f"{test}/{reading}"] = {"got": got, "ok": got in allowed}
            ok &= got in allowed
        r["checks"] = checks
        res[kind] = r
        print(kind, {k: (v["got"], "ok" if v["ok"] else "FAIL") for k, v in checks.items()},
              {t: {k: round(r[t][k]["rho"], 3) for k in ("RAW", "ADJ")} for t in ("levels", "pairs")}, flush=True)
    res["FLOOR_PASSES"] = bool(ok)
    print("FLOOR PASSES" if ok else "FLOOR FAILS")
    return res


# ---------------------------------------------------------------- real references

def datashop_rows_at(path: Path, kc_col: str):
    """overlap/atlas.datashop_rows with the KC column named instead of taken first (CHANGES 2)."""
    import csv
    with path.open(newline="", encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            kc = r.get(kc_col) or ""
            t = r.get("First Transaction Time") or ""
            h = r.get("Problem Hierarchy") or ""
            if not kc or not t or "Posttest" in h or "Pretest" in h:
                continue
            first = r.get("First Attempt") or ""
            yield (r["Anon Student Id"], kc, first == "correct", t,
                   first == "hint", int(r.get("Hints") or 0) > 0)


def r2_junyi():
    import atlas
    from shared.corpus import ds1275_export
    from shared.junyi_ratings import load
    from shared.paths import data_path
    ratings = load()
    bl = timelines(datashop_rows_at(ds1275_export(data_path("DS1275_DIR")), "KC (Exercise)"))
    d = item_difficulty(bl)
    rated = [(r.prereq, r.dependent, r.prereq_harder - 5) for r in ratings]
    res = pairs_test(d, rated)
    # ceiling: split-half of the raters' own prereq_harder, rows with at least 2 raters
    rng = random.Random(SEED)
    h1, h2 = [], []
    for r in ratings:
        raw = list(r.prereq_harder_raw)
        if len(raw) < 2:
            continue
        rng.shuffle(raw)
        k = len(raw) // 2
        h1.append(sum(raw[:k]) / k)
        h2.append(sum(raw[k:]) / (len(raw) - k))
    sh = rho(h1, h2)
    res["ceiling"] = {"rows": len(h1), "split_half_spearman": sh,
                      "spearman_brown": (2 * sh / (1 + sh)) if sh is not None else None}
    res["learners"], res["items_qualifying"] = len(bl), sum(1 for v in d.values() if v["n"] >= MIN_ATTEMPTS)
    res["rated_rows"] = len(rated)
    return res


def r1_dbe():
    sys.path.insert(0, str(ROOT / "studies/end-to-end/dbe-kt22-build"))
    import dbe
    data = dbe.load()
    rows = [(str(u), str(q), ok, t, False, False) for u, t, _id, q, ok in data["rows"]]
    d = item_difficulty(timelines(rows))
    res = levels_test(d, {str(k): v for k, v in data["difficulty"].items()})
    return res


def main():
    OUT.mkdir(exist_ok=True)
    if "--floor" in sys.argv:
        (OUT / "floor.json").write_text(json.dumps(floor(), indent=1))
        return
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    path = OUT / "result.json"
    res = json.loads(path.read_text()) if path.exists() else {}
    for key, fn in (("R1", r1_dbe), ("R2", r2_junyi)):
        if only and only != key:
            continue
        try:
            res[key] = fn()
            print(key, {k: (v["rho"], v["lo"], v["hi"], v["verdict"]) for k, v in res[key].items()
                        if isinstance(v, dict) and "rho" in v}, res[key].get("ADJ_minus_RAW", {}).get("verdict"))
        except Exception as e:  # noqa: BLE001
            res[key] = {"verdict": "NOT RUN", "why": f"{type(e).__name__}: {e}"}
            print(key, "NOT RUN:", res[key]["why"])
    res.setdefault("R3", {"verdict": "NOT RUN", "why": "PISA 2022 cognitive file not on disk (space)"})
    path.write_text(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
