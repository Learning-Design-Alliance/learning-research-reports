"""
Turn raw learner logs into the one object every model in this study consumes: a sparse
learner x item matrix of FIRST-ENCOUNTER correctness, plus the order the learner met the items in.

Why first encounter only. Repeated practice on the same item mixes two things -- what the learner
knew when they arrived, and what the tutor taught them in the meantime. Only the first is evidence
about structure, so each (learner, item) cell keeps the first attempt and nothing else. This also
removes the practice-curve term (AFM's opportunity count) from the comparison entirely: with one
observation per cell there is no curve to fit, and no model can win by capturing learning instead
of structure.

    python3 build_matrix.py junyi|assist|ds1190 <out.npz> [--all-attempts] [--outcome help]

`--outcome help` records whether the learner's FIRST ACTION on the item was to ask for a hint;
`--outcome hinted` whether they used a hint at any point on it. The first is the cleaner reading of
"do I have what this needs", taken before any feedback; the second is two to three times more common
and so carries more signal per cell. Which wins is an empirical question and the answer differs by
dataset.

`--outcome help` records whether the learner's FIRST ACTION on the item was to ask for a hint,
instead of whether they got it right. That is a different measurement of the same moment and a
better one for this question: it is taken before any feedback, so it is the learner's own reading of
whether they have what this item needs, and unlike correctness it has no guessing channel. Guessing
is what destroys the direction of a prerequisite (see recover.py), so an outcome without it is where
direction has a chance.

`--all-attempts` keeps every attempt in time order instead, with each one's prior-attempt count on
that item. That is the shape PSI-KT (ICLR 2024) works in, and its ablation reports the prerequisite
graph is worth 4-7 accuracy points there -- so the structure question has to be asked in that shape
too, against a practice term rather than against a matrix with no time in it.

Raw exports stay outside the repo (DataShop and ASSISTments both forbid redistribution); only the
npz in the scratchpad and the aggregate counts printed here ever leave this script.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from shared.paths import data_path, scratch_root  # noqa: E402

#: the data root, re-exported for the readers that still build paths under it (positivity.py passes
#: it on to studies/identifiability/conjunctive/); corpus paths here come from data_path()
SCRATCH = scratch_root()

#: a cell is kept only if the learner met at least this many items and the item at least this many
#: learners -- singletons carry no information for any model here and destabilise the item params
MIN_ITEMS_PER_LEARNER = 10
MIN_LEARNERS_PER_ITEM = 30

OUTCOME_NOTE = {"help": " -- outcome: asked for a hint before attempting",
                "hinted": " -- outcome: used a hint at any point"}


def _junyi_rows():
    """ds1275: Junyi Academy exercises, learner-chosen order, KC (Exercise) is the item.

    ONE export (shared.corpus.ds1275_export). Until 2026-09-24 this globbed both DataShop samples on
    disk, which hold the same transactions, and yielded every event twice."""
    from shared.corpus import ds1275_export
    with ds1275_export(data_path("DS1275_DIR")).open(newline="", encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            kc = r.get("KC (Exercise)") or ""
            t = r.get("First Transaction Time") or ""
            if not kc or not t:
                continue
            yield (r["Anon Student Id"], kc, r["First Attempt"] == "correct", t,
                   r["First Attempt"] == "hint", int(r.get("Hints") or 0) > 0)


def _ds1190_rows():
    """ds1190: fractions tutor. Tutor steps only -- the pre/post tests are a separate instrument."""
    d = data_path("DATASHOP_DIR") / "ds1190"
    f = next(d.glob("ds1190_student_step_All_Data_*.txt"))
    with f.open(newline="", encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            kc = r.get("KC (Default)") or ""
            h = r.get("Problem Hierarchy") or ""
            if not kc or "Posttest" in h or "Pretest" in h:
                continue
            t = r.get("First Transaction Time") or ""
            if not t:
                continue
            # a capability KC re-met on many different steps: the item is the capability
            yield (r["Anon Student Id"], kc, r["First Attempt"] == "correct", t,
                   r["First Attempt"] == "hint", int(r.get("Hints") or 0) > 0)


def _assist_rows():
    """ASSISTments 2012-13, skill_id as the item. `first_action` 1 means the learner opened a hint
    before attempting anything."""
    with (data_path("ASSIST_DIR") / "assist_rich.csv").open(newline="") as fh:
        for r in csv.DictReader(fh):
            s = r["skill_id"]
            if not s or s == "NA":
                continue
            yield (r["user_id"], s, r["correct"] == "1", r["start_time"],
                   r["first_action"] == "1", int(r["hint_count"] or 0) > 0)


LOADERS = {"junyi": _junyi_rows, "ds1190": _ds1190_rows, "assist": _assist_rows}


def build_sequence(name: str, outcome: str = "correct"):
    """Every attempt, in the learner's own time order, with its prior-attempt count on that item.

    The prior count is what separates a practice effect from a structural one. A model without it
    can win by noticing that the fourth attempt at an item goes better than the first, and call that
    a prerequisite.
    """
    rows = [(learner, item, _pick(outcome, ok, helped, hinted), t)
            for learner, item, ok, t, helped, hinted in LOADERS[name]()]
    rows.sort(key=lambda r: (r[0], r[3]))
    print(f"   {len(rows):,} attempts")

    learners = sorted({r[0] for r in rows})
    items = sorted({r[1] for r in rows})
    li = {u: i for i, u in enumerate(learners)}
    ii = {j: i for i, j in enumerate(items)}

    u = np.fromiter((li[r[0]] for r in rows), np.int32, len(rows))
    j = np.fromiter((ii[r[1]] for r in rows), np.int32, len(rows))
    y = np.fromiter((r[2] for r in rows), np.int8, len(rows))

    keep = _dense_core(u, j, len(learners), len(items))
    u, j, y = u[keep], j[keep], y[keep]
    keep_items = np.array(items, object)[np.unique(j)]
    u, j = _compact(u), _compact(j)

    # rows are already in (learner, time) order, so a running count per (learner, item) is enough
    opp = np.empty(len(u), np.int32)
    seen: dict[tuple[int, int], int] = {}
    pos = np.empty(len(u), np.int32)
    n_seen: dict[int, int] = {}
    for i, (uu, jj) in enumerate(zip(u, j)):
        k = (int(uu), int(jj))
        opp[i] = seen.get(k, 0)
        seen[k] = opp[i] + 1
        pos[i] = n_seen.get(int(uu), 0)
        n_seen[int(uu)] = pos[i] + 1

    return dict(learner=u, item=j, y=y.astype(np.int8), pos=pos, opp=opp,
                item_name=keep_items.astype(str))


def _dense_core(u, j, n_learners, n_items) -> np.ndarray:
    """Drop learners and items too thin to estimate, alternating until both thresholds hold."""
    keep = np.ones(len(u), bool)
    while True:
        # distinct partners, not row counts: an item answered 500 times by four learners is not an
        # item with 500 learners, and W cannot be estimated from four
        cell = np.unique(np.stack([u[keep], j[keep]]), axis=1)
        nl = np.bincount(cell[0], minlength=n_learners)
        ni = np.bincount(cell[1], minlength=n_items)
        bad = keep.copy()
        bad[keep] = (nl[u[keep]] < MIN_ITEMS_PER_LEARNER) | (ni[j[keep]] < MIN_LEARNERS_PER_ITEM)
        if not bad.any():
            return keep
        keep &= ~bad


def build(name: str, outcome: str = "correct"):
    first: dict[tuple[str, str], tuple[str, bool]] = {}
    seen = 0
    for learner, item, ok, t, helped, hinted in LOADERS[name]():
        seen += 1
        k = (learner, item)
        prev = first.get(k)
        if prev is None or t < prev[0]:
            first[k] = (t, _pick(outcome, ok, helped, hinted))
    print(f"   {seen:,} raw rows -> {len(first):,} first-encounter cells")

    learners = sorted({k[0] for k in first})
    items = sorted({k[1] for k in first})
    li = {u: i for i, u in enumerate(learners)}
    ii = {j: i for i, j in enumerate(items)}

    u = np.fromiter((li[k[0]] for k in first), np.int32, len(first))
    j = np.fromiter((ii[k[1]] for k in first), np.int32, len(first))
    y = np.fromiter((v[1] for v in first.values()), np.int8, len(first))
    t = np.array([v[0] for v in first.values()])
    day = _days(t)

    # prune to the dense core, alternating until both thresholds hold
    keep = np.ones(len(u), bool)
    while True:
        nl = np.bincount(u[keep], minlength=len(learners))
        ni = np.bincount(j[keep], minlength=len(items))
        bad = keep & (nl[u] < MIN_ITEMS_PER_LEARNER)
        bad |= keep & (ni[j] < MIN_LEARNERS_PER_ITEM)
        if not bad.any():
            break
        keep &= ~bad
    u, j, y, t, day = u[keep], j[keep], y[keep], t[keep], day[keep]

    # reindex survivors, then give every learner a 0..n-1 position in their own time order
    keep_items = np.array(items, object)[np.unique(j)]
    u = _compact(u)
    j = _compact(j)
    order = np.lexsort((t, u))
    pos = np.empty(len(u), np.int32)
    ranks = np.arange(len(u))
    starts = np.searchsorted(u[order], np.arange(u.max() + 1))
    pos[order] = ranks - starts[u[order]]

    # item names travel with the matrix: the Junyi arm has to line W up against an authored graph
    return dict(learner=u, item=j, y=y.astype(np.int8), pos=pos, day=day,
                item_name=keep_items.astype(str))


def _pick(outcome: str, ok: bool, helped: bool, hinted: bool) -> bool:
    return {"help": helped, "hinted": hinted}.get(outcome, ok)


def _days(t: np.ndarray) -> np.ndarray:
    """Calendar days since the first row, from the export's "YYYY-MM-DD hh:mm:ss" strings.

    Kept so a pair can be asked how far apart a learner met its two items. A structure that lives
    only in items met within a day of each other is an assignment, not a prerequisite.
    """
    d = np.array([x[:10] for x in t])
    uniq, inv = np.unique(d, return_inverse=True)
    epoch = np.array([(np.datetime64(x) - np.datetime64(uniq[0])).astype("timedelta64[D]").astype(int)
                      for x in uniq])
    return epoch[inv].astype(np.float32)


def _compact(a: np.ndarray) -> np.ndarray:
    _, inv = np.unique(a, return_inverse=True)
    return inv.astype(np.int32)


def main() -> None:
    name, out = sys.argv[1], Path(sys.argv[2])
    seq = "--all-attempts" in sys.argv
    outcome = sys.argv[sys.argv.index("--outcome") + 1] if "--outcome" in sys.argv else "correct"
    print(f"{name}{' (every attempt)' if seq else ''}"
          f"{OUTCOME_NOTE.get(outcome, '')}:")
    d = build_sequence(name, outcome) if seq else build(name, outcome)
    np.savez_compressed(out, **d)
    nl, ni, n = d["learner"].max() + 1, d["item"].max() + 1, len(d["y"])
    print(f"   {nl:,} learners x {ni:,} items, {n:,} rows "
          f"({100 * n / (nl * ni):.2f}% of the grid), {d['y'].mean():.3f} positive")
    print(f"   median rows/learner {np.median(np.bincount(d['learner'])):.0f}, "
          f"median rows/item {np.median(np.bincount(d['item'])):.0f}"
          + (f", mean prior attempts {d['opp'].mean():.2f}" if "opp" in d else ""))
    print(f"   -> {out}")


if __name__ == "__main__":
    main()
