"""
Which public learning corpora can answer a prerequisite question at all?

`positivity.py` establishes the gate on three datasets and finds the identifying cell -- learners
who attempted the dependant having failed the prerequisite -- empty in all three. That is either a
fact about those three, or a fact about the kind of data this field collects. The difference
matters: if it is the second, then a decade of automated-prerequisite results have been computed on
corpora that could not have shown a gate, and the field has no way of knowing because nobody reports
the number.

So this runs the gate over every corpus on disk and prints one row each. It needs no learners, no
new collection and no permissions beyond the ones already held, and it is the yardstick the field
does not have: a published floor per dataset, against which any reported edge-recovery number can be
read.

The claim is deliberately narrow. A dataset failing here is not bad data -- ITS logs are excellent
for the job they were collected for. It cannot support a CAUSAL prerequisite claim, which is a
different thing, and the tutor's own success at sequencing is what makes it so.

    python3 atlas.py [--out result.json] [--max-pairs 20000]

Raw exports stay in the scratchpad under every provider's redistribution terms; only the aggregate
row per dataset is committed.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from positivity import (MIN_CELL, at_item, candidate_pairs, classify,  # noqa: E402
                        mde, retrospective, states, timelines)

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from shared.edge_state import (CLAIMED_EFFECT, CONTRADICTED, SUPPORTED,  # noqa: E402
                               UNKNOWN, classify_edge)
from shared.paths import data_path  # noqa: E402
from shared.reachability import reachability  # noqa: E402

SEED = 20260920


def corpus_rng(name: str):
    """A SEPARATE random stream per corpus, derived from its name.

    The atlas used to draw every corpus's pair sample from ONE rng advanced across corpora in
    discover() order. That made a row depend on what else happened to be on disk that day and in
    what order it was found, so adding a corpus silently moved every later corpus's sample and no
    row could be re-derived on its own. studies/identifiability/a7-readjudication/ hit exactly this wall trying to reproduce
    the EdNet row. A name-keyed stream costs nothing and makes each row independent."""
    h = hashlib.blake2b(name.encode(), digest_size=8).digest()
    return np.random.default_rng([SEED, int.from_bytes(h, "big")])
#: a corpus with fewer learners or items than this cannot be read whatever its overlap, and saying
#: so is more useful than printing a number computed from nothing
MIN_LEARNERS, MIN_ITEMS = 40, 8


def kc_column(path: Path) -> str:
    """Which KC model an export's numbers come from.

    DataShop ships several per dataset and they are different models of the same learning, so the
    answer below depends on the choice. Recorded per dataset rather than left implicit.
    """
    with path.open(newline="", encoding="utf-8", errors="replace") as fh:
        cols = next(csv.reader(fh, delimiter="\t"), [])
    return next((c for c in cols if c.startswith("KC (")), "")


def datashop_rows(path: Path):
    """Any DataShop student-step export. The KC column is named differently in every dataset.

    Test and pretest steps are dropped where the hierarchy names them: they are a separate
    instrument from the tutor and mixing them invents order that the learner never experienced.
    """
    with path.open(newline="", encoding="utf-8", errors="replace") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        kc_cols = [c for c in (reader.fieldnames or []) if c.startswith("KC (")]
        if not kc_cols:
            return
        kc_col = kc_cols[0]
        for r in reader:
            kc = r.get(kc_col) or ""
            t = r.get("First Transaction Time") or ""
            h = r.get("Problem Hierarchy") or ""
            if not kc or not t or "Posttest" in h or "Pretest" in h:
                continue
            first = r.get("First Attempt") or ""
            yield (r["Anon Student Id"], kc, first == "correct", t,
                   first == "hint", int(r.get("Hints") or 0) > 0)


def ednet_rows(root: Path | None = None, limit_learners: int = 6000):
    """EdNet KT1, STREAMED FROM THE ZIP through the loader contract.

    CC BY-NC 4.0: non-commercial, and no model training. Reading it to count cells is neither.

    KT1 has NO `source` column -- its columns are timestamp, solving_id, question_id, user_answer,
    elapsed_time. The sprint / adaptive_offer distinction lives in KT3 and KT4, which we do not
    hold, so recommender-chosen rows CANNOT be conditioned out of this reading.

    THIS READER WAS REWRITTEN ON 2026-09-23 BECAUSE THE ROW IT PRODUCED COULD NOT BE REPRODUCED.
    It used to draw a deterministic random sample from whatever `KT1/*.csv` happened to be
    EXTRACTED ON DISK, guarding against an early-cohort bias that the archive does not actually
    have. The guard was sound and the pool was not: KT1 is 784,309 files allocating ~31 GB, so it
    lives on disk only in whatever partial extraction the last run left, and the extraction behind
    the published row was deleted to reclaim space. studies/identifiability/a7-readjudication/ measured the damage -- same
    6,000 learners and 142 items, but a median identifying cell of 31 against the published 242,
    and 110 CONTRADICTED verdicts against 8,995. The numbers were not wrong; they were not
    CHECKABLE, which by studies/identifiability/latent-shape/power.py's rule is the same problem.

    So the corpus now arrives through shared/corpus.EdNet, which streams members out of the zip and
    takes a documented PREFIX of the namelist. The namelist is not in id order, so a prefix is
    already an arbitrary slice, and unlike a random draw over a mutable directory it is regenerable
    from the archive alone. `tags="first"` keeps the KC model these numbers have always used.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from shared.corpus import EdNet
    # `root` is a directory holding contents/ beside ../ednet-kt1.zip; without it, $EDNET_ZIP and
    # $EDNET_CONTENTS
    if root is None:
        zip_path = data_path("EDNET_ZIP", must_exist=False)
        contents = data_path("EDNET_CONTENTS", must_exist=False)
    else:
        zip_path, contents = root.parent / "ednet-kt1.zip", root / "contents"
    if not zip_path.exists() or not (contents / "questions.csv").exists():
        return
    corpus = EdNet(zip_path, contents, learners=limit_learners, tags="first")
    for learner, unit, t, outcome in corpus.events():
        yield (learner, unit, outcome >= 0.5, t, False, False)


def xes3g5m_rows(root: Path | None = None):
    """XES3G5M at KC grain, from the flattened export. A question tagged with several KCs is
    evidence on each, which is how its own kc_level files are built.

    The first corpus here whose identifying cell is not empty -- learners on a practice platform
    choose what to attempt, so the cell a gated tutor removes survives. See studies/identifiability/taxonomy-order/.
    """
    import json as _json
    root = root or data_path("XES_DIR", must_exist=False)
    attempts, routes = root / "attempts.tsv", root / "cid2route.json"
    if not attempts.exists() or not routes.exists():
        return
    known = {int(k) for k in _json.loads(routes.read_text(encoding="utf-8"))}
    with attempts.open(encoding="utf-8") as fh:
        for line in fh:
            uid, _q, c, r, t = line.rstrip("\n").split("\t")
            ok = r == "1"
            for part in c.split("_"):
                if (k := int(part)) in known:
                    yield (uid, f"k{k}", ok, t, False, False)


def edmcup_rows(root: Path | None = None):
    """EDM Cup 2023 through the loader contract.

    Its cells.tsv is ALREADY one row per (learner, skill) with a mean and an attempt count -- a
    unit-test sitting, not an attempt stream -- so "passed" is that mean at or above 0.5. The cell
    grain is the corpus's own: a learner meets a skill once, in one assignment.

    This corpus has never been in the atlas, which is why the programme had no positivity states
    for it at all, and studies/identifiability/conjunctive-reachability/ put only 5.2% of its pairs inside a merge node.
    ASSISTments terms: analysis only, no redistribution.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from shared.corpus import EdmCup
    root = root or data_path("EDMCUP_DIR", must_exist=False)
    if not (root / "cells.tsv").exists():
        return
    for learner, unit, t, outcome in EdmCup(root).events():
        yield (learner, unit, outcome >= 0.5, t, False, False)


def eedi_rows(root: Path | None = None):
    """Eedi NeurIPS 2020 through the loader contract, at level-3 subject grain.

    Every learner in tasks 1-2, all three answer splits. Research use confirmed with Eedi; no
    redistribution. See shared/corpus.Eedi for the grain and what is never read.

    LIMITATION (2026-09-24): each row is the learner's LATEST answer to a question (the release keeps
    no earlier attempt), so first touch, outcome at touch and first pass here are last-answer states.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from shared.corpus import Eedi
    # `root` holds answers.tsv and data.zip; without it, $EEDI_ANSWERS and $EEDI_ZIP
    if root is None:
        answers = data_path("EEDI_ANSWERS", must_exist=False)
        zip_path = data_path("EEDI_ZIP", must_exist=False)
    else:
        answers, zip_path = root / "answers.tsv", root / "data.zip"
    if not answers.exists():
        return
    for learner, unit, t, outcome in Eedi(answers, zip_path).events():
        yield (learner, unit, outcome >= 0.5, t, False, False)


#: corpora that ship their own reader, keyed by the tag discover() gives them; root None means the
#: reader's environment variables
READERS = {"xes3g5m": lambda root: xes3g5m_rows(root),
           "ednet": lambda root: ednet_rows(root),
           "edmcup": lambda root: edmcup_rows(root),
           "eedi": lambda root: eedi_rows(root)}
#: which KC model each such corpus's numbers come from, recorded rather than left implicit
KC_MODEL = {"xes3g5m": "authored kc_routes leaf (866 KCs)",
            "ednet": "first expert tag on the question (contents/questions.csv)",
            "edmcup": "published CCSS skill code on the problem (problem_details.csv)",
            "eedi": "level-3 leaf of Eedi's subject tree (308 leaves); multi-leaf questions count on each"}
#: how the corpus's learner set is fixed, so a row can be re-derived rather than only re-run
LEARNER_SELECTION = {"ednet": "first 6,000 members of ednet-kt1.zip's namelist (not id order)",
                     "edmcup": "every learner in cells.tsv",
                     "eedi": "every learner in tasks 1-2 (train + public + private test answers)"}


def discover() -> dict[str, object]:
    """Every corpus on disk, as name -> row generator. Locations come from the corpora's
    environment variables (shared.paths.data_path); a corpus that is not there is left out."""
    out: dict[str, object] = {}
    from shared.corpus import datashop_export, datashop_is_qa
    for d in sorted(data_path("DATASHOP_DIR", must_exist=False).glob("*")):
        # QA-server exports are not public and no result may rest on them; every other export is
        # read at its 'All Data' sample (shared.corpus.datashop_export), not the first file in
        # sorted order, which until 2026-09-25 picked ds1190's '2016 data' subset
        if not d.is_dir() or datashop_is_qa(d):
            continue
        f = datashop_export(d)
        # the export directories carry a hash prefix and a timestamp; the dataset id is the
        # only durable part of the name
        m = re.search(r"(ds\d+)", d.name)
        out.setdefault(f"datashop/{m.group(1) if m else d.name}", f)
    for extra in (data_path("DS1275_DIR", must_exist=False), data_path("DS576_DIR", must_exist=False)):
        if extra.is_dir():
            f = datashop_export(extra)
            m = re.search(r"(ds\d+)", extra.name)
            out.setdefault(f"datashop/{m.group(1) if m else extra.name}", f)
    if (data_path("XES_DIR", must_exist=False) / "attempts.tsv").exists():
        out.setdefault("xes3g5m", ("xes3g5m", None))
    # ednet_rows has existed since the atlas was written and was never reachable: discover() only
    # ever returned DataShop exports, so EdNet has never appeared in an atlas run
    # the zip, not an extraction of it: see ednet_rows for why the extracted directory was the
    # wrong thing to key on
    if ((data_path("EDNET_CONTENTS", must_exist=False) / "questions.csv").exists()
            and data_path("EDNET_ZIP", must_exist=False).exists()):
        out.setdefault("ednet", ("ednet", None))
    if (data_path("EDMCUP_DIR", must_exist=False) / "cells.tsv").exists():
        out.setdefault("edmcup", ("edmcup", None))
    if data_path("EEDI_ANSWERS", must_exist=False).exists():
        out.setdefault("eedi", ("eedi", None))
    return out


def audit(name, rows, max_pairs, _rng=None):
    rng = corpus_rng(name)
    by_learner = timelines(rows)
    if len(by_learner) < MIN_LEARNERS:
        return dict(dataset=name, learners=len(by_learner), skipped="too few learners")
    first_touch, first_pass, outcome_at_touch = states(by_learner)
    idx = at_item(first_touch, outcome_at_touch)
    items = sorted(idx)
    if len(items) < MIN_ITEMS:
        return dict(dataset=name, learners=len(by_learner), items=len(items),
                    skipped="too few items")

    pairs = candidate_pairs(name, items, "all")
    if len(pairs) > max_pairs:
        pairs = [pairs[i] for i in rng.choice(len(pairs), max_pairs, replace=False)]

    reach, failed, mdes, retro_mdes, drops = [], [], [], [], []
    candidates = []
    state_counts = {SUPPORTED: 0, CONTRADICTED: 0, UNKNOWN: 0}
    for a, b in pairs:
        c = classify((a, b), first_touch, first_pass, outcome_at_touch, idx)
        n_m, n_f, n_n = len(c["mastered"]), len(c["failed"]), len(c["never"])
        if n_m + n_f + n_n == 0:
            continue
        reach.append(n_m + n_f + n_n)
        failed.append(n_f)
        v, obs = None, None
        if n_m:
            p_m = float(np.mean(c["mastered"]))
            v = mde(n_m, n_f, p_m)
            if v is not None:
                mdes.append(v)
            if n_f:
                obs = p_m - float(np.mean(c["failed"]))
        # what this corpus can actually SAY about the pair, rather than only whether it can read it.
        # The reachability gate is NOT applied here -- see below for why it runs in a second pass.
        st = classify_edge(v, obs)[0]
        state_counts[st] += 1
        if st == CONTRADICTED:
            candidates.append(((a, b), v, obs))
        # THE BACKGROUND. `obs` on an ARBITRARY ordered pair is what a corpus shows with no gate
        # claimed at all, so a real gate has to exceed it before an observational comparison can
        # tell the two apart. studies/outcomes/value-of-information/ measured +0.1016 on ASSISTments against a
        # claimed effect of 0.10 -- the whole thing. This column is how far that generalises.
        if v is not None and obs is not None:
            drops.append(obs)
        held, lacked = retrospective((a, b), first_touch, first_pass, outcome_at_touch, idx)
        if held:
            v = mde(len(held), len(lacked), float(np.mean(held)))
            if v is not None:
                retro_mdes.append(v)

    # THE REACHABILITY GATE, IN A SECOND PASS OVER THE PAIRS THAT COULD BE MOVED BY IT.
    # shared/edge_state.py refuses CONTRADICTED for a pair the corpus could never have falsified,
    # and falsifiability bears on that branch ALONE -- an unfalsifiable pair that shows the drop is
    # still SUPPORTED. So the gate only has to run on the would-be contradictions, which is what
    # makes it affordable: reachability is O(pairs x learners-holding-both x units-per-learner),
    # ruinous over 20,000 pairs and trivial over the few hundred that are live.
    #
    # THE MERGE NODE MUST BE READABLE AND POWERED, which is the same two-part rule classify_edge
    # applies one level down. A7's open question was which cell floor to use, 5 or 10; the honest
    # answer is that a bare floor is the wrong instrument -- five learners per stratum can never
    # resolve a ten-point gate, and no choice of floor turns a readability test into a power test.
    # So MIN_CELL still decides readability and CLAIMED_EFFECT decides power, exactly as they do
    # for a single edge.
    #
    # The verdict is recomputed by classify_edge rather than adjusted in place, so the rule stays in
    # one file. Subtracting from the counters here would be the same rule written twice.
    downgraded = downgraded_unpowered = 0
    if candidates:
        tl = {learner: {u: ((fp[u], True) if u in fp else (t, False))
                        for u, t in first_touch[learner].items()}
              for learner, fp in first_pass.items()}
        r = reachability(tl, [pair for pair, _v, _o in candidates], min_cell=MIN_CELL,
                         claimed=CLAIMED_EFFECT)
        for pair, v, obs in candidates:
            ok = r[pair]["status"] == "FALSIFIABLE"
            st = classify_edge(v, obs, falsifiable=ok)[0]
            if st != CONTRADICTED:
                downgraded += 1
                downgraded_unpowered += r[pair]["readable_nodes"] > 0
                state_counts[CONTRADICTED] -= 1
                state_counts[st] += 1

    reach, failed = np.array(reach, float), np.array(failed, float)
    drops = np.array(drops, float)
    mdes, retro_mdes = np.array(mdes), np.array(retro_mdes)
    n = max(len(reach), 1)
    return dict(dataset=name, learners=len(by_learner), items=len(items),
                edges=len(reach), median_reach=float(np.median(reach)) if len(reach) else 0.0,
                median_identifying=float(np.median(failed)) if len(failed) else 0.0,
                readable=len(mdes), readable_frac=len(mdes) / n,
                mde_median=float(np.median(mdes)) if len(mdes) else None,
                detect_20pt=int((mdes <= 0.20).sum()) if len(mdes) else 0,
                detect_20pt_frac=(float((mdes <= 0.20).mean()) if len(mdes) else 0.0),
                retro_readable=len(retro_mdes),
                retro_mde_median=float(np.median(retro_mdes)) if len(retro_mdes) else None,
                supported=state_counts[SUPPORTED], contradicted=state_counts[CONTRADICTED],
                unknown=state_counts[UNKNOWN],
                # how much of the negative evidence the merge-node gate took back
                contradicted_before_reachability=len(candidates),
                downgraded_unfalsifiable=downgraded,
                downgraded_frac=(downgraded / len(candidates)) if candidates else 0.0,
                # how much of the downgrade is the POWER half rather than readability, so the two
                # halves of the gate can be told apart in the record
                downgraded_readable_but_unpowered=downgraded_unpowered,
                decided_frac=(state_counts[SUPPORTED] + state_counts[CONTRADICTED]) / n,
                # the background an arbitrary pair already shows, and the share of the claimed
                # effect it eats: >= 1.0 means an observational contrast separates nothing
                drop_n=len(drops),
                drop_median=float(np.median(drops)) if len(drops) else None,
                drop_p75=float(np.percentile(drops, 75)) if len(drops) else None,
                background_share=(float(np.median(drops)) / CLAIMED_EFFECT
                                  if len(drops) else None))


def main() -> None:
    argv = sys.argv
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else None
    max_pairs = int(argv[argv.index("--max-pairs") + 1]) if "--max-pairs" in argv else 20000
    found = discover()
    print(f"{len(found)} corpora on disk\n")
    # --only NAME re-runs one corpus and replaces its row in --out, leaving the others as they were.
    # Sound because corpus_rng() keys each corpus's draws by its own name: a row does not depend on
    # which other corpora ran beside it.
    only = argv[argv.index("--only") + 1] if "--only" in argv else None
    kept = []
    if only:
        if not out:
            sys.exit("--only needs --out, the atlas file to merge into")
        found = {k: v for k, v in found.items() if k == only}
        if not found:
            sys.exit(f"no corpus named {only!r} on disk")
        kept = [r for r in json.loads(out.read_text()) if r.get("dataset") != only] if out.exists() else []
    rows = []
    for name, f in found.items():
        try:
            # discover() yields a bare path for a DataShop export, and a (kind, root) pair for a
            # corpus with its own reader (root None: the reader resolves its location)
            if isinstance(f, tuple):
                kind, root = f
                r = audit(name, READERS[kind](root), max_pairs)
                r["kc_model"] = KC_MODEL.get(kind, "")
            else:
                r = audit(name, datashop_rows(f), max_pairs)
                r["kc_model"] = kc_column(f)
        except Exception as e:                                    # noqa: BLE001
            r = dict(dataset=name, skipped=f"{type(e).__name__}: {e}")
        rows.append(r)
        if "skipped" in r:
            print(f"   {name:<22} skipped: {r['skipped']}")
        else:
            print(f"   {name:<22} {r['learners']:>6,} learners  {r['items']:>4} items  "
                  f"identifying cell (median) {r['median_identifying']:.0f}  "
                  f"can see a 20pt gate on {r['detect_20pt_frac']:.1%}", flush=True)

    good = [r for r in rows if "skipped" not in r]
    print(f"\n{'dataset':<22}{'learners':>9}{'items':>7}{'med. cell':>11}"
          f"{'readable':>10}{'MDE':>8}{'20pt':>8}"
          f"{'supp':>7}{'contra':>8}{'-unfals':>8}{'unknown':>9}{'decided':>9}")
    for r in sorted(good, key=lambda x: -x["detect_20pt_frac"]):
        m = f"{r['mde_median']:.3f}" if r["mde_median"] is not None else "--"
        print(f"{r['dataset']:<22}{r['learners']:>9,}{r['items']:>7}"
              f"{r['median_identifying']:>11.0f}{r['readable_frac']:>9.1%}{m:>8}"
              f"{r['detect_20pt_frac']:>8.1%}"
              f"{r['supported']:>7,}{r['contradicted']:>8,}"
              f"{r.get('downgraded_unfalsifiable', 0):>8,}{r['unknown']:>9,}"
              f"{r['decided_frac']:>9.2%}")

    if good:
        empty = sum(1 for r in good if r["median_identifying"] == 0)
        print(f"\n   corpora whose MEDIAN identifying cell is empty: {empty}/{len(good)}")
        best = max(good, key=lambda x: x["detect_20pt_frac"])
        print(f"   best available: {best['dataset']} sees a 20-point gate on "
              f"{best['detect_20pt_frac']:.1%} of its pairs")

    if out:
        out.write_text(json.dumps(kept + rows, indent=1))
        print(f"\n   -> {out}")


if __name__ == "__main__":
    main()
