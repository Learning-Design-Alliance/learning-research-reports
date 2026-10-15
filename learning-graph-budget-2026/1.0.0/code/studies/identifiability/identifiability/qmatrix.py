"""Are our corpora's attributes identifiable AT ALL? The condition stated before estimation.

Every positivity result in this programme was discovered the hard way: run the corpus, find the
identifying cell empty, record that it could not answer. `studies/identifiability/overlap/ATLAS.md` is a catalogue of that.

The cognitive-diagnosis literature does better. It has **necessary and sufficient theorems** for when
a Q-matrix and its attribute profiles are recoverable from responses (Chen/Liu/Xu/Ying, JASA 2015; Gu & Xu,
arXiv:1810.03819; Fang/Liu/Ying, arXiv:1706.01240; Kim, BJMSP, doi 10.1111/bmsp.70020), stated as
conditions on the DESIGN that can be checked before any estimation:

  C1  COMPLETENESS -- Q contains an identity submatrix: every attribute is measured by at least one
                     item that measures ONLY that attribute. Without it an attribute has no item that
                     isolates it and cannot be told apart from the ones it always appears with.
  C2  TWO IDENTITY SUBMATRICES -- every attribute is isolated by at least TWO items. Gu & Xu's
                     necessary condition for strict identifiability under DINA.
  C3  THREE ITEMS -- every attribute is measured by at least three items in total.
  C4  DISTINCT COLUMNS -- no two attributes load on exactly the same set of items. Two attributes
                     with identical patterns are one attribute wearing two names.

WHAT THIS CAN AND CANNOT SAY. These conditions identify the Q-MATRIX AND THE ATTRIBUTE PROFILES, not
the prerequisite relation among attributes. They are therefore **necessary, not sufficient**: if the
attributes themselves are not separable, relations among them certainly are not. A corpus that FAILS
is ruled out; a corpus that PASSES is not certified, and the failure then lies somewhere other than
the measurement model -- which is itself worth knowing, because it localises the problem.

    python3 qmatrix.py [--out out/qmatrix.json]

Raw exports stay in the scratchpad; only the per-corpus row is committed.
"""

from __future__ import annotations

import csv
import glob
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SCRATCH = Path("/tmp/claude-0/-home-user-learning-engine-ai-frontend/"
               "95e45190-f913-5b1d-89d5-0a9410ca02ad/scratchpad")
#: an attribute loading on fewer items than this is reported but cannot satisfy C3
MIN_ITEMS = 3


def qm_xes3g5m():
    """question -> set of KC ids, from the authored kc_routes."""
    root = SCRATCH / "xes3g5m"
    if not (root / "questions.json").exists() and not (root / "cid2route.json").exists():
        return None
    qs = json.loads((root / "XES3G5M/metadata/questions.json").read_text(encoding="utf-8")) \
        if (root / "XES3G5M/metadata/questions.json").exists() else None
    if qs is None:
        # fall back to the flattened export: concepts column carries `_`-joined KC ids
        out = defaultdict(set)
        with (root / "attempts.tsv").open(encoding="utf-8") as fh:
            for line in fh:
                _u, q, c, _r, _t = line.rstrip("\n").split("\t")
                for part in c.split("_"):
                    out[q].add(f"k{part}")
        return out
    kcmap = json.loads((root / "XES3G5M/metadata/kc_routes_map.json").read_text(encoding="utf-8"))
    leaf2id = defaultdict(set)
    for cid, name in kcmap.items():
        leaf2id[name.strip()].add(cid)
    out = defaultdict(set)
    for qid, q in qs.items():
        rs = q["kc_routes"]
        if isinstance(rs, str):
            rs = json.loads(rs.replace("'", '"'))
        for r in rs:
            leaf = [p.strip() for p in r.split("----")][-1]
            for i in leaf2id.get(leaf, ()):
                out[qid].add(f"k{i}")
    return out


def qm_ednet():
    p = SCRATCH / "ednet/contents/questions.csv"
    if not p.exists():
        return None
    out = defaultdict(set)
    with p.open(newline="", encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh):
            tags = (r.get("tags") or "").strip()
            if not tags or tags == "-1":
                continue
            for t in tags.split(";"):
                if t.strip():
                    out[r["question_id"]].add(t.strip())
    return out


def qm_datashop(path):
    """DataShop steps: the KC column may carry several KCs, `~~` separated."""
    out = defaultdict(set)
    with open(path, newline="", encoding="utf-8", errors="replace") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        kc_cols = [c for c in (reader.fieldnames or []) if c.startswith("KC (")]
        if not kc_cols:
            return None
        col = kc_cols[0]
        for r in reader:
            kc = (r.get(col) or "").strip()
            step = f"{r.get('Problem Name','')}|{r.get('Step Name','')}"
            if not kc or not step.strip("|"):
                continue
            for k in kc.split("~~"):
                if k.strip():
                    out[step].add(k.strip())
    return out or None


def check(name, item_to_attrs):
    """The four conditions, plus the counts that make a failure readable."""
    attrs = sorted({a for s in item_to_attrs.values() for a in s})
    idx = {a: i for i, a in enumerate(attrs)}
    items = sorted(item_to_attrs)
    Q = np.zeros((len(items), len(attrs)), dtype=np.int8)
    for r, it in enumerate(items):
        for a in item_to_attrs[it]:
            Q[r, idx[a]] = 1

    loads = Q.sum(0)                                  # items per attribute
    single = Q[Q.sum(1) == 1]                         # items measuring exactly one attribute
    isolated = single.sum(0) if len(single) else np.zeros(len(attrs))

    c1 = int((isolated >= 1).sum())
    c2 = int((isolated >= 2).sum())
    c3 = int((loads >= MIN_ITEMS).sum())
    cols = {}
    for j, a in enumerate(attrs):
        cols.setdefault(tuple(np.flatnonzero(Q[:, j]).tolist()), []).append(a)
    dupes = sum(len(v) - 1 for v in cols.values() if len(v) > 1)
    k = len(attrs)
    row = dict(corpus=name, items=len(items), attributes=k,
               mean_attrs_per_item=float(Q.sum(1).mean()),
               single_attribute_items=int(len(single)),
               C1_complete=c1 == k, C1_attrs_isolated=c1,
               C2_two_identity=c2 == k, C2_attrs_isolated_twice=c2,
               C3_three_items=c3 == k, C3_attrs_with_3plus=c3,
               C4_distinct_columns=dupes == 0, C4_duplicate_attrs=dupes,
               all_hold=bool(c1 == k and c2 == k and c3 == k and dupes == 0))
    print(f"{name:22s} items={len(items):>7,} attrs={k:>5,} "
          f"attrs/item={row['mean_attrs_per_item']:.2f}")
    print(f"{'':22s} C1 isolated>=1: {c1:>5,}/{k:<5,} {'PASS' if c1==k else 'FAIL'}   "
          f"C2 isolated>=2: {c2:>5,}/{k:<5,} {'PASS' if c2==k else 'FAIL'}")
    print(f"{'':22s} C3 items>=3   : {c3:>5,}/{k:<5,} {'PASS' if c3==k else 'FAIL'}   "
          f"C4 duplicate cols: {dupes:>4,}      {'PASS' if dupes==0 else 'FAIL'}")
    print(f"{'':22s} -> {'ALL CONDITIONS HOLD' if row['all_hold'] else 'NOT IDENTIFIABLE as specified'}\n")
    return row


def main() -> None:
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else HERE / "out/qmatrix.json"
    rows = []
    for name, loader in (("xes3g5m", qm_xes3g5m), ("ednet", qm_ednet)):
        q = loader()
        if q:
            rows.append(check(name, q))
    seen = set()
    for pat in ("datashop/prod/*/*student_step*.txt", "ds*/*student_step*.txt"):
        for p in sorted(glob.glob(str(SCRATCH / pat))):
            m = re.search(r"(ds\d+)", p)
            nm = m.group(1) if m else Path(p).parent.name[:10]
            if nm in seen:
                continue
            q = qm_datashop(p)
            if q and len({a for s in q.values() for a in s}) >= 4:
                seen.add(nm)
                rows.append(check(f"datashop/{nm}", q))

    passed = [r for r in rows if r["all_hold"]]
    print(f"{len(passed)} of {len(rows)} corpora satisfy all four conditions.")
    print("A corpus that FAILS is ruled out. A corpus that PASSES is not certified -- these identify")
    print("the Q-matrix and the attribute profiles, NOT the relations among attributes. Passing")
    print("localises the problem away from the measurement model.")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(min_items=MIN_ITEMS, rows=rows), indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
