"""PRE-REGISTERED: how many different carvings of XES3G5M into skills fit learners equally well?

The end-to-end study (studies/end-to-end/xes3g5m-build/) fitted several Q-matrices to the same
held-out XES3G5M learners and found them close: the blind-built nodes, the expert taxonomy with and
without multi-skill tags, the expert taxonomy at depth 3. If very different carvings fit equally
well, the skill description is not unique (a Rashomon set); if content-free carvings fit as well,
the "skills" carry nothing beyond difficulty. Written 2026-09-27 after those results were read (the
analyst knows the AUCs of E1, E2, E3, M2c and the built graph); no statistic below has been
computed.

Reads the frozen builds (studies/end-to-end/xes3g5m-build/build/tags.json, expert-tags.json) and,
through shared.paths.data_path("XES_DIR"), attempts.tsv and cid2route.json. No model call.

DIRECTION: symmetric -- node sets only; no edge enters any model here.

PRE-REGISTRATION
  Split, features, fit, AUC, learner bootstrap (B = 200) and "X beats Y" (lower 95% bound of the
  paired AUC difference above +0.001) are e2e.py's, imported.
  Carvings, each a Q-matrix over the 7,651 attempted questions:
    C1 expert leaf KCs (original tags)            C2 expert route prefixes of length <= 3
    C3 built nodes, all tags                       C4 built primary node only
    C5 tagger's expert KCs, all                    C6 original expert tags + tagger's extra KCs
    C7 DIFFICULTY BINS: one tag per question, questions cut into K bins by TRAIN error rate
       quantiles, K = the number of distinct primary built nodes. Content-free.
    C8 RANDOM: one tag per question, a seeded random partition with C4's bin sizes. Floor.
  Model per carving: off + U + K[carving] (e2e.py's M3 form).
  Primary partition of a carving: each question's first tag (C2: first route's prefix).
  RASHOMON SET R: content carvings C1-C6 whose AUC is within eps = 0.001 of the best content
  carving (reported also at eps = 0.002).
  Agreement: adjusted Rand index (ARI) between primary partitions, over questions tagged in both.
  VERDICTS
    V1 uniqueness: NON-UNIQUE CARVING if R holds two carvings with ARI < 0.5; UNIQUE UP TO
       RELABELLING if every pair in R has ARI >= 0.8; PARTLY UNIQUE otherwise; ONE CARVING if R
       has a single member (then read at eps = 0.002, reported, not verdict-bearing).
    V2 content: CONTENT MATTERS if every member of R beats both C7 and C8; DIFFICULTY SUFFICES if
       C7 is within eps of the best content carving; otherwise CONTENT PARTLY MATTERS.
  Reported: every carving's AUC and tags per question; ARI for every pair of carvings; the share of
  question pairs co-assigned in every member of R among pairs co-assigned in any (the shared core
  of the carvings).

    python3 rashomon.py
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E2E = ROOT / "studies/end-to-end/xes3g5m-build"
sys.path.insert(0, str(E2E))
import e2e  # noqa: E402

OUT = HERE / "out"
SEED = 20260927
EPS = (0.001, 0.002)


def ari(a: dict, b: dict) -> float:
    qs = [q for q in a if q in b]
    n = len(qs)
    if n < 2:
        return float("nan")
    comb = lambda x: x * (x - 1) / 2
    cont = Counter((a[q], b[q]) for q in qs)
    sa, sb = Counter(a[q] for q in qs), Counter(b[q] for q in qs)
    idx = sum(comb(v) for v in cont.values())
    ea, eb = sum(comb(v) for v in sa.values()), sum(comb(v) for v in sb.values())
    exp = ea * eb / comb(n)
    mx = (ea + eb) / 2
    return float((idx - exp) / (mx - exp)) if mx != exp else float("nan")


def coassigned(p: dict) -> set:
    groups = defaultdict(list)
    for q, g in p.items():
        groups[g].append(q)
    out = set()
    for qs in groups.values():
        qs = sorted(qs, key=int)
        for i in range(len(qs)):
            for j in range(i + 1, len(qs)):
                out.add((qs[i], qs[j]))
    return out


def main() -> None:
    rt = e2e.routes()
    built = {q: t["nodes"] for q, t in json.loads((E2E / "build/tags.json").read_text())["tags"].items()}
    tagger = json.loads((E2E / "build/expert-tags.json").read_text())["tags"]
    print("reading attempts")
    rows = e2e.load_attempts()
    uids = [r[0] for r in rows]
    y = np.array([r[5] for r in rows], np.int8)
    ul = {u: i for i, u in enumerate(dict.fromkeys(uids))}
    learner = np.array([ul[u] for u in uids])
    train = np.array([int(hashlib.sha256(u.encode()).hexdigest()[:8], 16) % 5 != 0 for u in uids])
    qlist = sorted({r[3] for r in rows}, key=int)
    qi = {q: i for i, q in enumerate(qlist)}
    qidx = np.array([qi[r[3]] for r in rows])
    C1, C2 = {}, {}
    for r in rows:
        if r[3] not in C1:
            ks = [k for k in r[4].split("_") if k in rt]
            C1[r[3]] = ks
            C2[r[3]] = list(dict.fromkeys(" > ".join(rt[k][:3]) for k in ks))
    C3 = {q: built.get(q, []) for q in C1}
    C4 = {q: v[:1] for q, v in C3.items()}
    C5 = {q: tagger.get(q, []) for q in C1}
    C6 = {q: C1[q] + [k for k in C5[q] if k not in C1[q]] for q in C1}
    # content-free carvings
    nq = np.bincount(qidx[train], minlength=len(qlist))
    cq = np.bincount(qidx[train], y[train], minlength=len(qlist))
    err = {q: (1 - cq[i] / nq[i]) if nq[i] else 0.5 for q, i in qi.items()}
    K = len({v[0] for v in C4.values() if v})
    order = sorted(C1, key=lambda q: (err[q], int(q)))
    C7 = {q: [f"d{min(K - 1, i * K // len(order))}"] for i, q in enumerate(order)}
    sizes = sorted(Counter(v[0] for v in C4.values() if v).values(), reverse=True)
    qs_shuf = sorted(C1, key=int)
    random.Random(SEED).shuffle(qs_shuf)
    C8, pos = {}, 0
    for gi, s in enumerate(sizes):
        for q in qs_shuf[pos:pos + s]:
            C8[q] = [f"r{gi}"]
        pos += s
    for q in qs_shuf[pos:]:
        C8[q] = [f"r{len(sizes)}"]
    qms = {"C1": C1, "C2": C2, "C3": C3, "C4": C4, "C5": C5, "C6": C6, "C7": C7, "C8": C8}
    seq = [(r[0], r[3], r[5]) for r in rows]
    specs = {c: ["off", "U", f"K:{c}"] for c in qms}
    specs["M1"] = ["off", "U"]
    print("fitting")
    point, draws, _ = e2e.kt_compare(seq, y, learner, train, qidx, qms, specs, ({},))
    content = ["C1", "C2", "C3", "C4", "C5", "C6"]
    best = max(content, key=lambda c: point[c])
    prim = {c: {q: v[0] for q, v in m.items() if v} for c, m in qms.items()}
    aris = {f"{a}-{b}": ari(prim[a], prim[b]) for i, a in enumerate(qms) for b in list(qms)[i + 1:]}
    res = {"auc": point, "best_content": best, "K_bins": K,
           "tags_per_question": {c: sum(len(v) for v in m.values()) / len(m) for c, m in qms.items()},
           "ari": aris, "by_eps": {}}
    for eps in EPS:
        R = [c for c in content if point[c] >= point[best] - eps]
        pair_aris = [ari(prim[a], prim[b]) for i, a in enumerate(R) for b in R[i + 1:]]
        if len(R) < 2:
            v1 = "ONE CARVING"
        elif min(pair_aris) < 0.5:
            v1 = "NON-UNIQUE CARVING"
        elif min(pair_aris) >= 0.8:
            v1 = "UNIQUE UP TO RELABELLING"
        else:
            v1 = "PARTLY UNIQUE"
        beats_all = all(e2e.beats(point, draws, c, "C7") and e2e.beats(point, draws, c, "C8") for c in R)
        v2 = ("DIFFICULTY SUFFICES" if point["C7"] >= point[best] - eps else
              "CONTENT MATTERS" if beats_all else "CONTENT PARTLY MATTERS")
        core = None
        if len(R) >= 2:
            sets = [coassigned(prim[c]) for c in R]
            union = set().union(*sets)
            inter = set.intersection(*sets)
            core = {"pairs_any": len(union), "pairs_all": len(inter),
                    "share": len(inter) / len(union) if union else float("nan")}
        res["by_eps"][str(eps)] = {"R": R, "min_pair_ari": min(pair_aris) if pair_aris else None,
                                   "V1": v1, "V2": v2, "core": core}
    D = {f"{a}-{b}": e2e.diff(point, draws, a, b) for a in content for b in ("C7", "C8")}
    D.update({f"{c}-M1": e2e.diff(point, draws, c, "M1") for c in qms})
    res["differences"] = D
    OUT.mkdir(exist_ok=True)
    (OUT / "rashomon-result.json").write_text(json.dumps(res, indent=1) + "\n")
    print("AUC", {c: round(v, 4) for c, v in point.items()})
    print("ARI", {k: round(v, 3) for k, v in aris.items()})
    for eps, r in res["by_eps"].items():
        print(f"eps {eps}: R={r['R']} min ARI {r['min_pair_ari']} | {r['V1']} | {r['V2']} | core {r['core']}")


if __name__ == "__main__":
    main()
