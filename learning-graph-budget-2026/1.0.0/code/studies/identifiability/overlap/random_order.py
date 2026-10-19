"""
Does ASSISTments 2012-13's random-order configuration randomise the order of SKILLS?

It would be the one configuration in these corpora where the order between two capabilities was
assigned rather than chosen, and so the one place an existence test needs no positivity argument.
It does not randomise it. Problem sets of type `RandomChildOrderSection` shuffle problems, and the
skills inside them still arrive in one order for almost everyone.

For each (sequence, student) unit, each skill's FIRST problem position is kept, from rows carrying a
skill tag, a position and a 0/1 `correct`. For every pair of skills co-seen inside one sequence, the
students holding both are split into those who met a first and the rest (b first, or both at one
position). The largest minority arm across all pairs is the number that decides whether an order
contrast could be read; the recorded run needs 15 per arm (`MIN_ARM`).

This is the scratch diagnostic behind the counts data/DATASETS.md and Paper 1 quote (17,502 units,
3,838 pairs, largest minority arm 15, top pairs 0/490 and 4/475), committed with its output. A pair is
counted once per sequence it is co-seen in, and its (a, b) is in sorted skill-id order.

    python3 random_order.py [--zip $ASSIST_DIR/assist2012.zip] [--out out/random_order.json]

ASSISTments terms: analysis only, no redistribution. Only the counts below are written.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from shared.paths import data_path  # noqa: E402

HERE = Path(__file__).resolve().parent
SECTION = "RandomChildOrderSection"
MIN_ARM = 15
TOP = 10


def first_positions(zip_path: Path):
    """(sequence, student) -> skill -> first position, over the random-order sections."""
    first: dict[tuple[str, str], dict[str, float]] = defaultdict(dict)
    rows = 0
    csv.field_size_limit(10_000_000)
    with zipfile.ZipFile(zip_path) as z:
        (name,) = z.namelist()
        with z.open(name) as raw:
            for row in csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8", errors="replace")):
                rows += 1
                if (row.get("type") or "").strip() != SECTION:
                    continue
                sk = (row.get("skill_id") or "").strip()
                pos = (row.get("position") or "").strip()
                cor = (row.get("correct") or "").strip()
                if not (sk and pos and cor in ("0", "1")):
                    continue
                k = ((row.get("sequence_id") or "").strip(), (row.get("user_id") or "").strip())
                if sk not in first[k] or float(pos) < first[k][sk]:
                    first[k][sk] = float(pos)
    return first, rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", type=Path, default=None, help="default $ASSIST_DIR/assist2012.zip")
    ap.add_argument("--out", type=Path, default=HERE / "out" / "random_order.json")
    a = ap.parse_args()
    first, rows = first_positions(a.zip or data_path("ASSIST_DIR") / "assist2012.zip")

    per_unit = Counter(len(d) for d in first.values())
    by_seq: dict[str, dict[str, dict[str, float]]] = defaultdict(dict)
    for (seq, user), d in first.items():
        by_seq[seq][user] = d
    pairs = []                              # (students with both, a first, b first or tied)
    for users in by_seq.values():
        sk = sorted({x for d in users.values() for x in d})
        for i, s1 in enumerate(sk):
            for s2 in sk[i + 1:]:
                both = [d for d in users.values() if s1 in d and s2 in d]
                if both:
                    af = sum(1 for d in both if d[s1] < d[s2])
                    pairs.append((len(both), af, len(both) - af))
    pairs.sort(reverse=True)
    minority = [min(af, bf) for _, af, bf in pairs]
    res = dict(
        rows_scanned=rows, section=SECTION,
        units=len(first), units_one_skill=per_unit.get(1, 0),
        units_two_or_more_skills=sum(v for k, v in per_unit.items() if k >= 2),
        pairs_co_seen=len(pairs),
        largest_minority_arm=max(minority) if minority else None,
        pairs_with_both_arms_at_least=dict(threshold=MIN_ARM,
                                           pairs=sum(1 for m in minority if m >= MIN_ARM)),
        top_pairs=[dict(students=n, a_first=af, b_first_or_tied=bf) for n, af, bf in pairs[:TOP]])
    print(f"rows scanned {rows:,}; {SECTION} (sequence, student) units with a skill: {len(first):,} "
          f"({res['units_one_skill']:,} see one skill)")
    print(f"skill pairs co-seen by at least one student: {len(pairs):,}")
    print(f"largest minority arm: {res['largest_minority_arm']}; pairs with both arms >= {MIN_ARM}: "
          f"{res['pairs_with_both_arms_at_least']['pairs']}")
    for n, af, bf in pairs[:TOP]:
        print(f"   both={n:<5} a_first={af:<5} b_first={bf}")
    a.out.parent.mkdir(exist_ok=True)
    a.out.write_text(json.dumps(res, indent=1) + "\n")
    print(f"-> {a.out}")


if __name__ == "__main__":
    main()
