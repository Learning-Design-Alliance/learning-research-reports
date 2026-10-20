"""How much does a constant offset cost quadratic-weighted kappa on Paper VI's own draw?

Paper VI (research/article/attainment-bias-in-llm-grading.md) said "a kappa is insensitive to a
constant offset". That is wrong for QWK. With chance agreement taken from the observed marginals,
QWK on integer levels equals Lin's concordance correlation,

    QWK = 2 s_xy / (s_x^2 + s_y^2 + d^2),      d = mean(x) - mean(y)

(Fleiss & Cohen 1973; Lin 1989), so an offset lowers QWK, but only through d^2 relative to the
two variances. This script puts numbers on that from the paper's own grades, instead of from an
illustrative range of SDs, and also records the human-grade SDs the paper uses to express effects
in SD units.

Reads (no model call):
  - the per-case dump of `--mode pool --n 150 --seed 7 --repeats 9` on Gemini 3.5 Flash Lite
    (studies/measurement/grader-attainment-prior/, run 2026-10-05). It holds, per answer, the
    teacher grade and nine LITE passes. Its 150 answers are the stratified seed-7 draw the attempt
    history and original exemplar arms were run on: the id sets of this dump, the 2026-10-05
    `--mode history` dump and grader-exemplar-marks' dry-run draw of its first 150 were compared
    on 2026-10-05 and are identical. The dump is
    a per-case file and stays in the session scratchpad; pass its path as argv[1].
  - JorGPT (`jorgpt-answers` in data/data-sources.json) via JORGPT_DIR, for the full-corpus SD.

Writes studies/measurement/grader-eval/analyses/out/qwk-offset.json (aggregates only).

Checks, not trusted: the identity is verified against a direct QWK computation on the rounded
first pass, and the two must agree to 1e-9 (they are algebraically equal on integer data).
"""
import csv
import json
import os
import sys
from pathlib import Path


def pvar(v):
    m = sum(v) / len(v)
    return sum((t - m) ** 2 for t in v) / len(v)


def qwk_direct(x, y):
    """QWK with expected disagreement from the product of the observed marginals."""
    n = len(x)
    obs = sum((a - b) ** 2 for a, b in zip(x, y)) / n
    exp = sum((a - b) ** 2 for a in x for b in y) / (n * n)
    return 1 - obs / exp


def main():
    dump = json.load(open(sys.argv[1]))
    rows = dump["rows"]
    human = [float(r["human"]) for r in rows]
    lite = [float(round(r["lite"][0])) for r in rows]          # first pass, integer levels
    n = len(rows)
    mh, ml = sum(human) / n, sum(lite) / n
    sxy = sum((a - mh) * (b - ml) for a, b in zip(human, lite)) / n
    S = pvar(human) + pvar(lite)
    d = ml - mh
    identity = 2 * sxy / (S + d * d)
    direct = qwk_direct(lite, human)
    assert abs(identity - direct) < 1e-9, (identity, direct)

    def kappa_at(offset):
        return 2 * sxy / (S + offset * offset)

    # Offsets the paper discusses: exemplar arm +0.38 -> +0.06, model tier +0.34 -> +0.01,
    # and the low-prior-mark drift of -0.59 applied to an unbiased grader.
    cases = {
        "exemplars_0.38_to_0.06": (0.38, 0.06),
        "tier_0.34_to_0.01": (0.34, 0.01),
        "offset_0.59_vs_0": (0.59, 0.0),
    }
    costs = {k: {"kappa_at_larger": round(kappa_at(a), 4), "kappa_at_smaller": round(kappa_at(b), 4),
                 "difference": round(kappa_at(b) - kappa_at(a), 4)} for k, (a, b) in cases.items()}

    jdir = os.environ.get("JORGPT_DIR")
    full_sd = None
    if jdir:
        g = [float(r["teacher_grade"]) for r in csv.DictReader(open(Path(jdir) / "dataset_en.csv", encoding="utf-8"))
             if r.get("student_answer", "").strip()]
        full_sd = {"n": len(g), "sd": round(pvar(g) ** 0.5, 3), "mean": round(sum(g) / len(g), 3)}

    out = {
        "source_dump": {"model": dump.get("models"), "run": dump.get("runStamp"), "n": n,
                        "first_id": rows[0]["id"]},
        "stratified_150": {"human_mean": round(mh, 3), "human_sd": round(pvar(human) ** 0.5, 3),
                           "lite_pass1_sd": round(pvar(lite) ** 0.5, 3), "lite_pass1_bias": round(d, 3),
                           "qwk_direct": round(direct, 4), "qwk_identity": round(identity, 4)},
        "offset_cost": costs,
        "full_corpus_teacher_grade": full_sd,
        "note": "population SDs; QWK identity exact on integer levels",
    }
    dest = Path(__file__).parent / "out" / "qwk-offset.json"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
