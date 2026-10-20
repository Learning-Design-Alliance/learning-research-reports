"""
Junyi's human relationship ratings, oriented. The only place `relationship_annotation_*.csv` is parsed.

Chang, Hsu & Chen (EDM 2015, p. 533) asked raters "to choose the 1-9 score" for three questions about
each exercise pair (A, B), held verbatim in `QUESTIONS`:

    Similarity    "How similar is the knowledge required for answering these two exercises?"
    Difficulty    "How much more difficult is exercise B compared to exercise A, where a higher score
                  means B is more difficult than A and a score of 5 indicates that they have the same
                  difficulty?"
    Prerequisite  "After students learned to correctly answer exercise B, how appropriate is utilizing
                  exercise A to deepen the students' knowledge on the topic step by step?"

A model prompt that mirrors the human question is built from `QUESTIONS` and `SCALE`, never retyped,
so model and humans are asked the same thing about the same (A, B) by construction.

Their Figure 2: a high (a, b) value means "bth exercise is more likely to be a prerequisite of ath".
So a high Prerequisite rating on row (Exercise_A, Exercise_B) asserts B -> A: **Exercise_B is the
prerequisite, Exercise_A the dependent.** The data agree: on the 231 authored pairs among the 316
rated in both orders, rating(A=dependent, B=prereq) exceeds rating(A=prereq, B=dependent) by +1.09.

A dozen scripts here once read the column as A -> B. The loader exists so the
orientation is decided once: records carry `prereq` and `dependent`, never A/B, and
`Ratings.prerequisite(prereq, dependent)` returns only the correctly oriented row -- None when that
ordered pair was not rated. It never falls back to the reversed row, which answers the opposite
question. `shared/check_idioms.py` fails any other file that opens the CSVs or reads the
Prerequisite columns.

1,954 rows over 1,638 unordered pairs (316 rated in both orders). Rows keep file order (training then
testing), which seeded analyses depend on.

    from shared.junyi_ratings import load
    ratings = load()                               # $JUNYI_DIR, else the session scratchpad
    ratings.prerequisite("addition_1", "addition_2")
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

try:
    from shared.paths import data_path
except ImportError:                       # imported with shared/ itself on sys.path
    from paths import data_path

FILES = ("relationship_annotation_training.csv", "relationship_annotation_testing.csv")

#: verbatim from Chang, Hsu & Chen (EDM 2015), section 2.1
QUESTIONS = {
    "Similarity": "How similar is the knowledge required for answering these two exercises?",
    "Difficulty": ("How much more difficult is exercise B compared to exercise A, where a higher "
                   "score means B is more difficult than A and a score of 5 indicates that they "
                   "have the same difficulty?"),
    "Prerequisite": ("After students learned to correctly answer exercise B, how appropriate is "
                     "utilizing exercise A to deepen the students' knowledge on the topic step by "
                     "step?"),
}
#: "we ask the workers to choose the 1-9 score for the following questions"
SCALE = "Choose a score from 1 to 9."
#: $JUNYI_DIR, else its data/data-sources.json default
DEFAULT_DIR = data_path("JUNYI_DIR", must_exist=False)


@dataclass(frozen=True)
class Rating:
    """One rated row. `prereq` is Exercise_B, `dependent` is Exercise_A."""
    prereq: str
    dependent: str
    #: Prerequisite_avg / _raw: how strongly `prereq` -> `dependent` holds
    prerequisite: float
    prerequisite_raw: tuple[int, ...]
    #: symmetric
    similarity: float
    similarity_raw: tuple[int, ...]
    #: Difficulty_avg / _raw: higher = `prereq` (column B) harder than `dependent`; 5 = equal
    prereq_harder: float
    prereq_harder_raw: tuple[int, ...]

    @property
    def pair(self) -> tuple[str, str]:
        """(prereq, dependent) -- the edge this row's prerequisite rating is about."""
        return self.prereq, self.dependent


class Ratings:
    def __init__(self, rows: list[Rating]):
        self.rows = rows
        self._by_edge = {r.pair: r for r in rows}

    def __iter__(self) -> Iterator[Rating]:
        return iter(self.rows)

    def __len__(self) -> int:
        return len(self.rows)

    def get(self, prereq: str, dependent: str) -> Rating | None:
        """The row rating prereq -> dependent, or None. Never the reversed row."""
        return self._by_edge.get((prereq, dependent))

    def prerequisite(self, prereq: str, dependent: str) -> float | None:
        """Mean rating that `prereq` is a prerequisite of `dependent`; None if not rated that way."""
        r = self._by_edge.get((prereq, dependent))
        return None if r is None else r.prerequisite

    def rated_either_way(self, x: str, y: str) -> bool:
        """For symmetric uses only (is this unordered pair in the rating sample at all)."""
        return (x, y) in self._by_edge or (y, x) in self._by_edge


def _ints(s: str) -> tuple[int, ...]:
    return tuple(int(v) for v in s.split("_") if v)


def parse(rows: list[dict]) -> Ratings:
    """Build from already-read CSV dicts (the fixture path for tests)."""
    return Ratings([Rating(prereq=r["Exercise_B"], dependent=r["Exercise_A"],
                           prerequisite=float(r["Prerequisite_avg"]),
                           prerequisite_raw=_ints(r["Prerequisite_raw"]),
                           similarity=float(r["Similarity_avg"]),
                           similarity_raw=_ints(r["Similarity_raw"]),
                           prereq_harder=float(r["Difficulty_avg"]),
                           prereq_harder_raw=_ints(r["Difficulty_raw"]))
                    for r in rows])


def load(directory: str | Path | None = None) -> Ratings:
    """All rated rows. `directory` overrides $JUNYI_DIR, which overrides the scratchpad default."""
    d = Path(directory or os.environ.get("JUNYI_DIR") or DEFAULT_DIR)
    rows: list[dict] = []
    for f in FILES:
        p = d / f
        if not p.exists():
            raise SystemExit(f"{p} not found. Set JUNYI_DIR to the directory holding {FILES}; "
                             "see data/data-sources.json (junyi2015-authored).")
        with p.open(newline="", encoding="utf-8-sig") as fh:
            rows += list(csv.DictReader(fh))
    return parse(rows)
