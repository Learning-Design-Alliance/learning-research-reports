"""
Junyi's authored exercise table and prerequisite graph (`junyi_Exercise_table.csv`), read once.

The release README says "each name is unique in the dataset". The file disagrees: 837 rows carry
835 names. `matrix_mul_two` and `matrix_app_fruit_oil` each appear twice, with identical
prerequisites, and each row lists its one prerequisite twice ("matrix_add_sub_3,matrix_add_sub_3"),
so a reader that keeps edges in a list counts those two edges four times each (and `ratio` lists
`writing_proportions` twice): 988 listed prerequisites, 981 distinct edges. `exercises()` keeps
the first row per name; `authored_edges()` returns each (prereq, dependent) once, in file order,
which seeded analyses that sample or permute edges depend on.

DIRECTION: an edge (p, name) means p is a prerequisite OF name, per the column description
"Indicate its prerequisite exercise (parent shown in its knowledge map)" (codebook
junyi2015-authored).

    from shared.junyi_graph import authored_edges, exercises
    rows = exercises()                     # $JUNYI_DIR, else the session scratchpad
    edges = authored_edges(known_only=True)
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

try:
    from shared.paths import data_path
except ImportError:                       # imported with shared/ itself on sys.path
    from paths import data_path

FILE = "junyi_Exercise_table.csv"
#: $JUNYI_DIR, else its data/data-sources.json default
DEFAULT_DIR = data_path("JUNYI_DIR", must_exist=False)


def _dir(directory) -> Path:
    return Path(directory or os.environ.get("JUNYI_DIR") or DEFAULT_DIR)


def exercises(directory: str | Path | None = None) -> list[dict]:
    """One dict per exercise name (first row wins), in file order."""
    p = _dir(directory) / FILE
    if not p.exists():
        raise SystemExit(f"{p} not found. Set JUNYI_DIR; see data/data-sources.json "
                         "(junyi2015-authored).")
    seen, out = set(), []
    with p.open(newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            if r["name"] in seen:
                continue
            seen.add(r["name"])
            out.append(r)
    return out


def authored_edges(directory: str | Path | None = None, known_only: bool = True,
                   rows: list[dict] | None = None) -> list[tuple[str, str]]:
    """Unique (prereq, dependent) edges in file order.

    known_only drops prerequisites that are not themselves exercise names (none are, today)."""
    rows = exercises(directory) if rows is None else rows
    names = {r["name"] for r in rows}
    seen, out = set(), []
    for r in rows:
        for p in (r["prerequisites"] or "").split(","):
            p = p.strip()
            if not p or (known_only and p not in names):
                continue
            e = (p, r["name"])
            if e not in seen:
                seen.add(e)
                out.append(e)
    return out
