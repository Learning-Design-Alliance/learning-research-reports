"""
Do expert prerequisite judgements correspond to anything in learner behaviour?

This is the question the programme exists to answer, and until now nothing had the three pieces at
once: an authored prerequisite graph, expert ratings of individual pairs with the RAW per-annotator
scores, and learner data whose order was not dictated by a scheduler.

Junyi Academy has all three.

  junyi_Exercise_table.csv            835 exercises, 981 authored prerequisite edges (988 listed)
  relationship_annotation_*.csv       1,954 rated rows (1,638 unordered pairs) 1-9 for
                                      Prerequisite, 3-15 raters each, every rater's score kept;
                                      read through shared.junyi_ratings
  DataShop ds1275                     2,063 learners over 631 of those exercises, LEARNER-CHOSEN
                                      order -- 92% of topic pairs met in both directions

Three things, each a precondition for the next.

1. AGREEMENT. Split each pair's raters in half, average each half, correlate across pairs, and
   Spearman-Brown correct. If raters do not agree with each other, their mean rating is noise and
   nothing downstream can be interpreted. Our own corpora put expert agreement on graph structure at
   kappa ~0.31, so this is an independent replication at much larger scale.

2. AUTHORED vs RATED. Do the pairs the knowledge map asserts as prerequisites get higher prerequisite
   ratings than pairs it does not? This checks the map against the raters -- two human sources, no
   learners involved.

3. RATED vs LEARNERS. For each rated edge P -> D, compare learners who met P before D against those
   who met D first, on their first-attempt accuracy at D, adjusting for each learner's overall
   accuracy. Then ask whether that gap tracks the expert rating.

PRE-REGISTERED, written before any number was read:

  H0   Expert prerequisite rating is unrelated to the order effect in learner data. Correlation
       between the adjusted gap and Prerequisite_avg is zero.
  H1   Higher-rated prerequisites show a larger advantage for meeting the prerequisite first.

THE CONFOUND, stated plainly. Learners chose their own order, so this is observational. Someone who
does A before B may differ from someone who does the reverse in ways that also affect performance on
B. Adjusting for overall accuracy removes the crudest version of that and not the subtle version. A
positive result here is evidence that expert judgement tracks SOMETHING real in behaviour; it is not
proof of a causal prerequisite, and the randomised arm is still the only thing that would settle it.

CORRECTION (2026-09-24): rating direction. Sections 2 and 3 read row (Exercise_A, Exercise_B) as
A -> B. Chang et al. asked "after B, how appropriate is A as the next step", so the row rates B -> A.
Section 2 compared ratings on the reverse of the authored arrows: 5.17 vs 4.50 (n 265) is now
6.12 vs 4.21 (n 387), d 0.32 -> 0.96. Section 3 measured the order effect for the wrong prerequisite:
rho -0.059 [-0.382, +0.267] n 50 is now +0.299 [-0.017, +0.571] n 47 -- positive, the H1 direction,
CI touching zero. Section 1 is orientation-free and unchanged.

DIRECTION: a -> b means a is the prerequisite of b, per the release's column description of
`prerequisites` ("Indicate its prerequisite exercise (parent shown in its knowledge map)", codebook
junyi2015-authored) for authored edges (p, name), and per Chang et al. 2015's third question for
rating rows, whose (prereq, dependent) is (Exercise_B, Exercise_A) (quoted in shared/junyi_ratings.py).

Reversed-arrow control added 2026-09-24. Section 2's Cohen's d is re-scored with every authored edge
flipped and must beat its reverse (require_claimed: the section claims the map and the raters agree
on the arrow). Section 3 is re-scored with each rated row's prereq and dependent swapped -- the order
effect of the other exercise, against the same rating -- and reported beside the claimed rho.

Checked 2026-09-24 (ds1275 has two DataShop samples on disk, the same transactions rolled up two
ways): the committed result reproduces exactly from the 'All Data' export, the one
shared.corpus.ds1275_export selects; passing a directory now resolves to it. From 'All Data1' section
3 would read rho +0.340 [+0.034, +0.612], n 49. The authored-edge set was already deduplicated.

    python3 expert_vs_data.py <junyi_dir> <ds1275_dir | ds1275_student_step>
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from shared.corpus import ds1275_export  # noqa: E402
from shared.direction import require_claimed, reversed_arrow  # noqa: E402
from shared.junyi_ratings import load as load_ratings  # noqa: E402

CORRECT = {"CORRECT", "OK"}
KC = "KC (Exercise)"


def spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    def rank(a):
        o = np.argsort(a); r = np.empty(len(a)); r[o] = np.arange(len(a)); return r
    return float(np.corrcoef(rank(x), rank(y))[0, 1])


def main():
    jd, log = Path(sys.argv[1]), sys.argv[2]
    ex = list(csv.DictReader(open(jd / "junyi_Exercise_table.csv", encoding="utf-8-sig")))
    authored = {(p.strip(), r["name"]) for r in ex
                for p in (r["prerequisites"] or "").split(",") if p.strip()}
    ann = load_ratings(jd).rows
    print(f"   {len(ex)} exercises, {len(authored)} authored edges, {len(ann)} rated pairs")

    # ---- 1. do the raters agree with each other? -------------------------
    rng = np.random.default_rng(0)
    a_half, b_half = [], []
    for r in ann:
        v = [float(x) for x in r.prerequisite_raw]
        if len(v) < 6:
            continue
        idx = rng.permutation(len(v))
        h = len(v) // 2
        a_half.append(np.mean([v[i] for i in idx[:h]]))
        b_half.append(np.mean([v[i] for i in idx[h:2 * h]]))
    r_half = spearman(a_half, b_half)
    r_full = 2 * r_half / (1 + r_half)          # Spearman-Brown
    print(f"\n   1. RATER AGREEMENT  split-half {r_half:+.3f}, "
          f"Spearman-Brown corrected {r_full:+.3f}  (n={len(a_half)} pairs)")

    # ---- 2. does the authored map match the raters? ----------------------
    def cohen_d(edges):
        y = [r.prerequisite for r in ann if r.pair in edges]
        n = [r.prerequisite for r in ann if r.pair not in edges]
        sd = np.sqrt(((len(y) - 1) * np.var(y, ddof=1) + (len(n) - 1) * np.var(n, ddof=1))
                     / (len(y) + len(n) - 2))
        return float((np.mean(y) - np.mean(n)) / sd)

    yes = [r.prerequisite for r in ann if r.pair in authored]
    no = [r.prerequisite for r in ann if r.pair not in authored]
    d = cohen_d(authored)
    flip2 = reversed_arrow(cohen_d, authored)
    print(f"\n   2. AUTHORED vs RATED  mean prerequisite rating")
    print(f"      edges the map asserts:     {np.mean(yes):.2f}  (n={len(yes)})")
    print(f"      rows it does not:          {np.mean(no):.2f}  (n={len(no)})")
    print(f"      difference:                {np.mean(yes) - np.mean(no):+.2f} on a 1-9 scale, d = {d:.2f}")
    print(f"      reversed-arrow control:    d claimed {flip2['claimed']:.2f}, reversed "
          f"{flip2['reversed']:.2f} -> {flip2['verdict']}")
    require_claimed(flip2, "authored map vs rater direction")

    # ---- 3. does expert rating track the learner-order effect? -----------
    rows = list(csv.DictReader(open(ds1275_export(log), encoding="utf-8", errors="replace"),
                               delimiter="\t"))
    first, acc = {}, defaultdict(lambda: [0, 0])
    seq = defaultdict(int)
    for r in rows:
        s = r["Anon Student Id"]
        seq[s] += 1
        ok = (r.get("First Attempt") or "").strip().upper() in CORRECT
        for k in (r.get(KC) or "").split("~~"):
            k = k.strip()
            if not k:
                continue
            first.setdefault((s, k), seq[s])
            acc[(s, k)][0] += ok
            acc[(s, k)][1] += 1
    overall = defaultdict(lambda: [0, 0])
    for (s, k), (c, n) in acc.items():
        overall[s][0] += c
        overall[s][1] += n
    ability = {s: c / n for s, (c, n) in overall.items() if n >= 20}

    def order_gap(a, b):
        """Adjusted accuracy on b, a-first minus b-first, or None below 15 learners per order."""
        af, bf = [], []
        for s in ability:
            if (s, a) not in first or (s, b) not in first or (s, b) not in acc:
                continue
            c, n = acc[(s, b)]
            if n < 2:
                continue
            resid = c / n - ability[s]              # accuracy on B, adjusted for the learner
            (af if first[(s, a)] < first[(s, b)] else bf).append(resid)
        if len(af) >= 15 and len(bf) >= 15:
            return float(np.mean(af) - np.mean(bf)), len(af) + len(bf)
        return None

    gaps, ratings, ns = [], [], []
    for r in ann:
        g = order_gap(r.prereq, r.dependent)       # a -> b
        if g is not None:
            gaps.append(g[0])
            ratings.append(r.prerequisite)
            ns.append(g[1])
    print(f"\n   3. RATED vs LEARNERS  {len(gaps)} pairs with >=15 learners in each order")
    if len(gaps) >= 30:
        rho = spearman(ratings, gaps)
        boot = [spearman([ratings[i] for i in idx], [gaps[i] for i in idx])
                for idx in (rng.integers(0, len(gaps), len(gaps)) for _ in range(2000))]
        lo, hi = np.percentile(boot, [2.5, 97.5])
        print(f"      Spearman(expert rating, prereq-first advantage) = {rho:+.3f} "
              f"95% CI [{lo:+.3f}, {hi:+.3f}]")
        print(f"      mean prereq-first advantage: {np.mean(gaps):+.4f} "
              f"(top-quartile rated pairs: {np.mean([g for g, t in zip(gaps, ratings) if t >= np.percentile(ratings, 75)]):+.4f})")

        # Reversed-arrow control. Nodes carry their row index so each edge keeps its own rating
        # when flipped (316 unordered pairs are rated both ways, with different ratings). Row order
        # is kept because this spearman breaks rating ties by position.
        def rho_of(edges):
            g, t = [], []
            for (x, i), (y, _i) in sorted(edges, key=lambda e: e[0][1]):
                got = order_gap(x, y)
                if got is not None:
                    g.append(got[0])
                    t.append(ann[i].prerequisite)
            return spearman(t, g) if len(g) >= 30 else float("nan")

        rated_edges = {((r.prereq, i), (r.dependent, i)) for i, r in enumerate(ann)}
        flip3 = reversed_arrow(rho_of, rated_edges)
        print(f"      reversed-arrow control: rho claimed {flip3['claimed']:+.3f}, reversed "
              f"{flip3['reversed']:+.3f} -> {flip3['verdict']}")
        Path("junyi-expert-vs-data.json").write_text(json.dumps(
            {"rater_split_half": r_half, "rater_spearman_brown": r_full,
             "authored_mean": float(np.mean(yes)), "unauthored_mean": float(np.mean(no)),
             "n_authored": len(yes), "cohen_d": d,
             "n_pairs_learner": len(gaps), "spearman": rho, "ci": [float(lo), float(hi)],
             "reversed_arrow": {"authored_vs_rated_d": flip2, "rated_vs_learners_rho": flip3},
             "acknowledgement": "Junyi Academy dataset; Koedinger et al. (2010), datashop.org"},
            indent=2) + "\n")
        print("      wrote junyi-expert-vs-data.json")


if __name__ == "__main__":
    main()
