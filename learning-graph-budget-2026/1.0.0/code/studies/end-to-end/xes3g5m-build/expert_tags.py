"""PRE-REGISTERED: does multi-skill tagging of the EXPERT's own nodes close the gap to the built graph?

primary_tag.py found that the built graph's advantage over XES3G5M's expert taxonomy is mostly
multi-skill tagging: the tagger's secondary nodes beat random ones by +0.0030 AUC, while at one tag
per question built and expert nodes differ by only +0.0008 (under the bar). If tagging carries the
gain, the same tagger applied to the expert's own 866 leaf KCs should recover it. Written after
e2e.py's and primary_tag.py's results were read; no statistic below has been computed.

The tagger (e2e.TAGGER, same batching, retry and reply cap as e2e.py) sees each question's text and
answer and the expert KC list (id | route, root first) and names 1-3 KCs the question assesses, main
first. It never sees a learner response or the original expert tags. The tags are written to
build/expert-tags.json and committed before `analyse` reads learner data. Prompts holding question
text stay in the scratch cache; the repo gets question id -> KC ids only.

DIRECTION: symmetric -- node sets only; no edge enters any model here.

PRE-REGISTRATION
  split, features, fit, AUC, bootstrap and the "beats" rule (lower 95% bound of the paired
  learner-bootstrap AUC difference above +0.001, B = 200) are e2e.py's, imported.
  Q-matrices (all over expert leaf KCs unless named built):
    E1   the original expert tags (e2e.py's M2)
    E2   the tagger's expert KCs, all
    E2p  the tagger's primary expert KC only
    E3   the original expert tags plus the tagger's KCs not already among them
    E3x  the original expert tags plus as many random other expert KCs as E3 added (seeded)
    B    the built nodes, all tags (e2e.py's M3)
  VERDICTS
    V1 multi-skill tagging on expert nodes: TAGGING ADDS CONTENT TO EXPERT NODES if E3 beats E1 and
       E3 beats E3x; ADDS POOLING ONLY if E3 beats E1 but not E3x; ADDS NOTHING otherwise.
    V2 is tagging the whole effect: max(E2, E3) against B. EXPERT NODES WITH MULTI-SKILL TAGS MATCH
       THE BUILT GRAPH if the lower bound of best - B is above -0.001; BUILT NODES STILL AHEAD
       otherwise (B beats best by more than the bar).
  Reported: E2p - E1 (does the tagger's single choice match the experts'), agreement of E2p with the
  original first expert KC, tags per question, every model against M1 (off + U).
  A tagger reply that fails to parse is retried in batches of 5; a question still unparsed keeps no
  tagger KC (E2, E2p empty for it; E3 = E1 for it), counted.

BUDGET  the e2e.py ledger and its $30 cap (spent before this study: $21.88).

TAGGING RUN  7,652 of 7,652 tagged (1: 3,015, 2: 4,238, 3: 399 KCs); $2.17. As in e2e.py (change 8), a
             first cache replay re-asked requests that had failed at the HTTP level and changed some
             tags; a second replay made no new call and reproduced build/expert-tags.json byte for
             byte. That state is frozen.

    python3 expert_tags.py tag       # model calls; writes build/expert-tags.json
    python3 expert_tags.py analyse   # after build/expert-tags.json is committed
"""

from __future__ import annotations

import hashlib
import json
import random
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import e2e  # noqa: E402

SEED = e2e.SEED + 11
TAGS = HERE / "build/expert-tags.json"

EXPERT_TAG_PROMPT = """You are tagging mathematics questions with the knowledge components they assess.

KNOWLEDGE COMPONENTS (id | name)
{nodes}

QUESTIONS
{questions}

For each question give 1 to 3 knowledge component ids it assesses, the main one first.
Reply with JSON only: {{"tags": [{{"q": 1, "nodes": ["k12"]}}]}}"""


def kc_list(rt: dict) -> tuple[str, set]:
    ids = sorted(rt, key=int)
    return "\n".join(f"k{k} | {' > '.join(rt[k])}" for k in ids), {f"k{k}" for k in ids}


def tag_batch(qids, qs, listing, ids):
    block = "\n".join(f"Q{i + 1}. {e2e.show_question(qs[q], 400, 0)}" for i, q in enumerate(qids))
    txt, _ = e2e.call(e2e.TAGGER, EXPERT_TAG_PROMPT.format(nodes=listing, questions=block),
                      what=f"expert-tag {qids[0]}", max_tokens=32000, temperature=0.0)
    obj = e2e.parse_json(txt)
    out = {}
    for t in (obj.get("tags") if isinstance(obj, dict) else None) or []:
        try:
            k = int(t["q"]) - 1
            ns = [n for n in t["nodes"] if n in ids][:3]
        except (KeyError, TypeError, ValueError):
            continue
        if 0 <= k < len(qids) and ns:
            out[qids[k]] = [n[1:] for n in ns]
    return out


def tag() -> None:
    from shared import llm
    if not llm.load_key():
        raise SystemExit("no OPENROUTER_API_KEY")
    qs = e2e.questions()
    listing, ids = kc_list(e2e.routes())
    qids = sorted(qs, key=int)
    tags: dict = {}
    batches = [qids[s:s + 20] for s in range(0, len(qids), 20)]
    with ThreadPoolExecutor(16) as ex:
        for got in ex.map(lambda b: tag_batch(b, qs, listing, ids), batches):
            tags.update(got)
    missing = [q for q in qids if q not in tags]
    with ThreadPoolExecutor(16) as ex:
        for got in ex.map(lambda b: tag_batch(b, qs, listing, ids),
                          [missing[s:s + 5] for s in range(0, len(missing), 5)]):
            tags.update(got)
    TAGS.write_text(json.dumps({"tags": tags, "untagged": [q for q in qids if q not in tags]}, indent=1) + "\n")
    print(f"tagged {len(tags)} of {len(qids)}; spend ${e2e.spent():.2f}")


def analyse() -> None:
    dirty = subprocess.run(["git", "status", "--porcelain", str(TAGS)], capture_output=True, text=True,
                           cwd=e2e.ROOT).stdout.strip()
    if dirty or not TAGS.exists():
        raise SystemExit("build/expert-tags.json is missing or uncommitted")
    tagger = json.loads(TAGS.read_text())["tags"]
    built = {q: t["nodes"] for q, t in json.loads((HERE / "build/tags.json").read_text())["tags"].items()}
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
    E1 = {}
    for r in rows:
        if r[3] not in E1:
            E1[r[3]] = [k for k in r[4].split("_") if k in rt]
    E2 = {q: tagger.get(q, []) for q in E1}
    E2p = {q: v[:1] for q, v in E2.items()}
    E3 = {q: E1[q] + [k for k in E2[q] if k not in E1[q]] for q in E1}
    rng = random.Random(SEED)
    allk = sorted(rt, key=int)
    E3x = {}
    for q in sorted(E1, key=int):
        extra = len(E3[q]) - len(E1[q])
        E3x[q] = E1[q] + rng.sample([k for k in allk if k not in E1[q]], extra)
    seq = [(r[0], r[3], r[5]) for r in rows]
    qms = {"E1": E1, "E2": E2, "E2p": E2p, "E3": E3, "E3x": E3x, "B": built}
    specs = {"M1": ["off", "U"]}
    specs.update({q: ["off", "U", f"K:{q}"] for q in qms})
    print("fitting")
    point, draws, _ = e2e.kt_compare(seq, y, learner, train, qidx, qms, specs, ({},))
    best = "E2" if point["E2"] >= point["E3"] else "E3"
    pairs = [("E3", "E1"), ("E3", "E3x"), ("E2", "B"), ("E3", "B"), ("E2p", "E1"), ("E2", "E1")] + \
            [(q, "M1") for q in qms]
    D = {f"{a}-{b}": e2e.diff(point, draws, a, b) for a, b in pairs}
    bt = lambda a, c: e2e.beats(point, draws, a, c)
    v1 = ("TAGGING ADDS CONTENT TO EXPERT NODES" if bt("E3", "E1") and bt("E3", "E3x") else
          "TAGGING ADDS POOLING ONLY" if bt("E3", "E1") else "TAGGING ADDS NOTHING")
    v2 = ("EXPERT NODES WITH MULTI-SKILL TAGS MATCH THE BUILT GRAPH" if D[f"{best}-B"]["lo"] > -e2e.BEATS
          else "BUILT NODES STILL AHEAD")
    agree = np.mean([bool(E2p[q]) and bool(E1[q]) and E2p[q][0] == E1[q][0] for q in E1])
    tags = {q: sum(len(v) for v in m.values()) / len(m) for q, m in qms.items()}
    res = {"auc": point, "differences": D, "V1": v1, "V2": v2, "best_expert_arm": best,
           "tagger_primary_equals_original_first": float(agree), "mean_tags_per_question": tags,
           "questions_without_tagger_kc": sum(1 for v in E2.values() if not v)}
    (e2e.OUT / "expert-tags-result.json").write_text(json.dumps(res, indent=1) + "\n")
    print("AUC", {m: round(v, 4) for m, v in point.items()})
    print("tags per question", {q: round(v, 2) for q, v in tags.items()})
    for k, v in D.items():
        print(f"  {k:<8} {v['diff']:+.4f} [{v['lo']:+.4f}, {v['hi']:+.4f}]")
    print(f"tagger primary = original first KC: {agree:.3f}")
    print("V1:", v1)
    print("V2:", v2)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    {"tag": tag, "analyse": analyse}.get(cmd, lambda: print(__doc__))()
