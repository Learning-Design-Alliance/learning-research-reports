"""Stream MOOCCubeX's user-problem.json and keep the attempts on concept-linked problems.

Builds the attempts.tsv that item-tree inference reads (studies/identifiability/learning-structure/
mooccubex_iita.py, mooccubex_concept_iita.py, reanalyse_lower_tail.py). The 22 GB source is read from
a pipe and never stored; only matching rows are written, one per line:

    user_id <TAB> problem_id <TAB> is_correct <TAB> attempts

A problem is kept when it is the second column of any line of concept-problem.txt. Rows keep the
order of the source file. This is the filter first run on 2026-09-12 as the scratch `stream_filter.py`
(133,384,333 rows read, 69,546 kept), with its two hard-coded file names made arguments.

    curl -sSL https://lfs.aminer.cn/misc/moocdata/data/mooccube2/relations/user-problem.json \\
      | python3 data/ingest/mooccubex/stream_attempts.py $MOOCCUBEX_DIR/concept-problem.txt \\
          $MOOCCUBEX_DIR/attempts.tsv

MOOCCubeX: research use, no redistribution. The output stays outside the repository.
"""
import json
import sys
import time


def main() -> None:
    concept_problem, out_path = sys.argv[1], sys.argv[2]
    keep = set()
    for line in open(concept_problem, encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if len(p) >= 2:
            keep.add(p[1])
    sys.stderr.write(f"target problems: {len(keep):,}\n")

    n = kept = 0
    t0 = time.time()
    with open(out_path, "w", encoding="utf-8") as out:
        for line in sys.stdin:
            n += 1
            if n % 5_000_000 == 0:
                sys.stderr.write(f"  {n:,} rows read, {kept:,} kept, {time.time() - t0:.0f}s\n")
                sys.stderr.flush()
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            pid = r.get("problem_id")
            if pid in keep:
                kept += 1
                out.write(f"{r.get('user_id')}\t{pid}\t{r.get('is_correct')}\t{r.get('attempts')}\n")
    sys.stderr.write(f"DONE {n:,} rows read, {kept:,} kept, {time.time() - t0:.0f}s\n")


if __name__ == "__main__":
    main()
