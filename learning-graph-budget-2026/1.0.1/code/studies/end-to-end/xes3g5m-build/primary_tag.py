"""PRE-REGISTERED: do the built nodes beat the expert taxonomy because of their boundaries, or
because questions carry more of them?

e2e.py found that a Q-matrix from the blind-built nodes tracks held-out XES3G5M learners better than
the expert taxonomy (M3 0.7989 vs M2 0.7965, +0.0024 [+0.0022, +0.0027]). But 67% of questions carry
two or three built nodes against 13% for the expert tags, so the built Q-matrix pools each learner's
history across more related questions. This separates the two. Written after e2e.py's result was
read (the analyst knows M2, M2c, M3 and M4); no statistic below has been computed.

Reads the frozen build (build/tags.json, committed at af63b35) and, through
shared.paths.data_path("XES_DIR"), attempts.tsv and cid2route.json. No model call.

DIRECTION: symmetric -- node sets only; no edge enters any model here.

PRE-REGISTRATION
  split, features, fit, AUC, bootstrap and the "beats" rule (lower 95% bound of the paired
  learner-bootstrap AUC difference above +0.001, B = 200) are e2e.py's, imported, not copied.
  Q-matrices:
    expert     every expert leaf KC of the question (e2e.py's M2)
    expert_p   the first expert KC listed for the question (the order attempts.tsv gives)
    built      every built node the tagger gave (e2e.py's M3)
    built_p    the tagger's primary (first) built node only
    built_x    the primary built node plus as many secondary nodes as the tagger gave, drawn at
               random from the other built nodes (seeded): same tag count, secondary content destroyed
  Models: off + U + K[Q] for each Q, and M1 = off + U.
  VERDICTS
    V1 boundaries, one tag each: built_p vs expert_p.
       BUILT BOUNDARIES BETTER if built_p beats expert_p; EXPERT BOUNDARIES BETTER if expert_p beats
       built_p; NO DIFFERENCE AT ONE TAG otherwise.
    V2 secondary tags: built vs built_x.
       SECONDARY TAGS CARRY CONTENT if built beats built_x; SECONDARY TAGS ADD POOLING ONLY if not,
       and built_x beats built_p; SECONDARY TAGS ADD NOTHING otherwise.
  Reported, not verdict-bearing: built - built_p, expert - expert_p, every model against M1.
  What each means for e2e.py: V1 BUILT says the gain survives without pooling; V1 EXPERT or NONE
  says e2e.py's advantage came from tag count; V2 says whether the tagger's extra tags are
  meaningful or merely more history.

    python3 primary_tag.py
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import e2e  # noqa: E402

SEED = e2e.SEED + 7


def main() -> None:
    tg = json.loads((HERE / "build/tags.json").read_text())
    nodes = [n["id"] for n in json.loads((HERE / "build/nodes.json").read_text())["nodes"]]
    built = {q: t["nodes"] for q, t in tg["tags"].items()}
    built_p = {q: ns[:1] for q, ns in built.items()}
    rng = random.Random(SEED)
    built_x = {}
    for q in sorted(built, key=int):
        ns = built[q]
        others = [n for n in nodes if n != ns[0]]
        built_x[q] = [ns[0]] + rng.sample(others, len(ns) - 1)
    rt = e2e.routes()
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
    expert, expert_p = {}, {}
    for r in rows:
        if r[3] not in expert:
            ks = [k for k in r[4].split("_") if k in rt]
            expert[r[3]] = ks
            expert_p[r[3]] = ks[:1]
    seq = [(r[0], r[3], r[5]) for r in rows]
    qms = {"expert": expert, "expert_p": expert_p, "built": built, "built_p": built_p, "built_x": built_x}
    specs = {"M1": ["off", "U"]}
    specs.update({q: ["off", "U", f"K:{q}"] for q in qms})
    print("fitting")
    point, draws, _ = e2e.kt_compare(seq, y, learner, train, qidx, qms, specs, ({},))
    pairs = [("built_p", "expert_p"), ("built", "built_x"), ("built_x", "built_p"),
             ("built", "built_p"), ("expert", "expert_p")] + [(q, "M1") for q in qms]
    D = {f"{a}-{b}": e2e.diff(point, draws, a, b) for a, b in pairs}
    b = lambda a, c: e2e.beats(point, draws, a, c)
    v1 = ("BUILT BOUNDARIES BETTER" if b("built_p", "expert_p") else
          "EXPERT BOUNDARIES BETTER" if b("expert_p", "built_p") else "NO DIFFERENCE AT ONE TAG")
    v2 = ("SECONDARY TAGS CARRY CONTENT" if b("built", "built_x") else
          "SECONDARY TAGS ADD POOLING ONLY" if b("built_x", "built_p") else "SECONDARY TAGS ADD NOTHING")
    tags = {q: sum(len(v) for v in m.values()) / len(m) for q, m in qms.items()}
    res = {"auc": point, "differences": D, "V1": v1, "V2": v2, "mean_tags_per_question": tags}
    (e2e.OUT / "primary-tag-result.json").write_text(json.dumps(res, indent=1) + "\n")
    print("AUC", {m: round(v, 4) for m, v in point.items()})
    print("tags per question", {q: round(v, 2) for q, v in tags.items()})
    for k, v in D.items():
        print(f"  {k:<18} {v['diff']:+.4f} [{v['lo']:+.4f}, {v['hi']:+.4f}]")
    print("V1:", v1)
    print("V2:", v2)


if __name__ == "__main__":
    main()
