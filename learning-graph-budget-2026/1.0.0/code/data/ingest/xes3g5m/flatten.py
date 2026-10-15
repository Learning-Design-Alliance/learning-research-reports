"""Flatten the XES3G5M release into the two files every XES3G5M reader here takes.

    attempts.tsv     uid <TAB> question <TAB> concepts <TAB> response <TAB> timestamp, one row per
                     answered question, from question_level/train_valid_sequences_quelevel.csv then
                     question_level/test_quelevel.csv. Padding (-1 response or timestamp) is
                     skipped, and a repeated (uid, question, timestamp) is kept once: the
                     train_valid file repeats windows of a long sequence.
    cid2route.json   knowledge-component id -> its route in the KC tree, a list of names from the
                     root to the leaf. A route leaf in metadata/questions.json is matched by name to
                     metadata/kc_routes_map.json; the first route seen for an id wins.

    tar xzf $XES_DIR/XES3G5M.tar.gz -C $XES_DIR
    python3 data/ingest/xes3g5m/flatten.py $XES_DIR

Readers: studies/identifiability/overlap/atlas.py (xes3g5m_rows), lag_bands.py, domains.py,
studies/identifiability/conjunctive/*, studies/measurement/graph-typology/surmise_graphs.py. These
are the snippets that first built both files on 2026-09-21, unchanged. The data licence is unstated,
so it is treated as research use and the output stays outside the repository.
"""
import collections
import csv
import json
import sys
from pathlib import Path


def attempts(root: Path) -> None:
    seen = set()
    n_rows = n_pad = n_dup = 0
    with open(root / "attempts.tsv", "w", encoding="utf-8") as out:
        for p in ("XES3G5M/question_level/train_valid_sequences_quelevel.csv",
                  "XES3G5M/question_level/test_quelevel.csv"):
            with open(root / p, newline="", encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    uid = row["uid"]
                    q, c = row["questions"].split(","), row["concepts"].split(",")
                    r, t = row["responses"].split(","), row["timestamps"].split(",")
                    for i in range(len(q)):
                        if r[i] == "-1" or t[i] == "-1":
                            n_pad += 1
                            continue
                        key = (uid, q[i], t[i])
                        if key in seen:
                            n_dup += 1
                            continue
                        seen.add(key)
                        n_rows += 1
                        out.write(f"{uid}\t{q[i]}\t{c[i]}\t{r[i]}\t{t[i]}\n")
    print(f"attempts.tsv: {n_rows:,} rows, {n_pad:,} padding skipped, {n_dup:,} repeats dropped")


def cid2route(root: Path) -> None:
    kcmap = json.load(open(root / "XES3G5M/metadata/kc_routes_map.json", encoding="utf-8"))
    leaf2id = collections.defaultdict(set)
    for cid, name in kcmap.items():
        leaf2id[name.strip()].add(int(cid))
    qs = json.load(open(root / "XES3G5M/metadata/questions.json", encoding="utf-8"))
    routes = {}
    for q in qs.values():
        rs = q["kc_routes"]
        if isinstance(rs, str):
            rs = json.loads(rs.replace("'", '"'))
        for r in rs:
            parts = [p.strip() for p in r.split("----")]
            for i in leaf2id.get(parts[-1], ()):
                routes.setdefault(i, parts)
    with open(root / "cid2route.json", "w", encoding="utf-8") as fh:
        json.dump({str(k): v for k, v in routes.items()}, fh, ensure_ascii=False)
    print(f"cid2route.json: {len(routes):,} of {len(kcmap):,} KC ids have a route")


def main() -> None:
    root = Path(sys.argv[1])
    csv.field_size_limit(10**9)
    attempts(root)
    cid2route(root)


if __name__ == "__main__":
    main()
