"""Stream MOOCCubeX relations/user-problem.json and keep one aggregate per learner.

The general learner factor for holon.py: per learner, how many problem rows they answered and how
many were correct. The 22 GB source is read from a pipe and never stored; the output is one line per
learner (pseudonymous id TAB rows TAB correct), nothing else.

    curl -sSL https://lfs.aminer.cn/misc/moocdata/data/mooccube2/relations/user-problem.json \\
      | python3 ability_ingest.py $LDA_SCRATCH_DIR/derived-holon-projection/ability.tsv

MOOCCubeX: research use, no redistribution. The output stays outside the repository.
"""
import json
import sys
import time
from collections import defaultdict


def main() -> None:
    out_path = sys.argv[1]
    n_rows = defaultdict(int)
    n_ok = defaultdict(int)
    n = bad = 0
    t0 = time.time()
    for line in sys.stdin:
        n += 1
        if n % 10_000_000 == 0:
            sys.stderr.write(f"  {n:,} rows, {len(n_rows):,} learners, {time.time() - t0:.0f}s\n")
            sys.stderr.flush()
        line = line.strip().rstrip(",")
        if not line or line[0] != "{":
            continue
        try:
            r = json.loads(line)
        except Exception:
            bad += 1
            continue
        u = r.get("user_id")
        if u is None:
            bad += 1
            continue
        n_rows[u] += 1
        ok = r.get("is_correct")
        if ok in (1, "1", True, "true"):
            n_ok[u] += 1
    with open(out_path, "w", encoding="utf-8") as out:
        for u, k in n_rows.items():
            out.write(f"{u}\t{k}\t{n_ok.get(u, 0)}\n")
    sys.stderr.write(f"DONE {n:,} rows, {len(n_rows):,} learners, {bad:,} unparsed, "
                     f"{time.time() - t0:.0f}s\n")


if __name__ == "__main__":
    main()
