"""The loader contract: what a corpus must supply so every study downstream runs unchanged.

O1 asks for "a new dataset runs end to end from a loader plus a config, with no per-dataset code",
and has sat at 2/3 because each study kept needing its own build_observations. Three studies built
on 2026-09-23 -- edmcup-direction, assist2012-direction, conjunctive-reachability -- made the missing
piece obvious: they differ ONLY in how raw files become (learner, unit, time, outcome) rows. Every
statistic after that point is shared.

So the contract is four columns.

    EVENT = (learner, unit, time, outcome)

        learner  an opaque id. Never a name, never anything identifying.
        unit     the thing being learned -- a skill, a KC, an exercise. The corpus's own vocabulary.
        time     anything sortable. Epoch seconds, an ISO string, an index. Only ORDER is used, so
                 a corpus with sequence numbers but no clock is admissible.
        outcome  a float in [0,1]. Binary correctness, or a mean over attempts.

and three optional extras, each of which unlocks specific studies rather than being decoration:

        cohort(learner)    a class or class PROXY. Without it, intervals cannot cluster and must say
                           so; a proxy is admissible and must be named as one in the adapter.
        position(unit)     an EXTERNAL curricular position, for direction and for left-censoring
                           depth. Returning None is the honest answer for a corpus whose only scale
                           is its own taxonomy -- and studies/identifiability/window-depth/ showed five of seven corpora are
                           in exactly that state, so None is a first-class value, not a gap.
        licence            a string, printed by every runner. A corpus whose terms forbid
                           redistribution says so here and the runner carries it into the output.

WHAT THIS DELIBERATELY DOES NOT DO. It does not wrap the statistics, schedule work, or define a
workflow graph. LearnSphere's Tigris does all of that with an info.xml and an XSD per component, and
that machinery is not what O1 needs -- the interface discipline is. This is the smallest surface that
makes a corpus interchangeable.

Adapters live at the bottom. Adding a corpus is writing ONE class, which is the gate O1 states.
"""
import collections
import csv
import os
import pathlib
import re


class Corpus:
    """Subclass, set `name` and `licence`, implement `events()`. Everything else is optional."""

    name = "unnamed"
    licence = "UNSTATED -- state it before using this corpus"

    def events(self):
        """Yield (learner, unit, time, outcome). Order does not matter; the consumer sorts."""
        raise NotImplementedError

    def cohort(self, learner):
        """Class or class proxy for clustering, or None if the corpus has none."""
        return None

    def position(self, unit):
        """External curricular position, or None. None is a real answer, not a gap."""
        return None


# ---------------------------------------------------------------- shared derivations
# Every study on this board consumes one of these three. None of them knows which corpus it has.

def cells(corpus):
    """(learner, unit) -> (first_time, mean_outcome, n). The universal intermediate."""
    agg = collections.defaultdict(lambda: [None, 0.0, 0])
    for learner, unit, time, outcome in corpus.events():
        c = agg[(learner, unit)]
        if c[0] is None or time < c[0]:
            c[0] = time
        c[1] += float(outcome)
        c[2] += 1
    return {k: (v[0], v[1] / v[2], v[2]) for k, v in agg.items()}


def timelines(corpus, pass_threshold=0.5):
    """learner -> {unit: (first_time, passed)} -- what reachability and positivity consume."""
    out = collections.defaultdict(dict)
    for (learner, unit), (t, mean, _n) in cells(corpus).items():
        out[learner][unit] = (t, mean >= pass_threshold)
    return out


def summary(corpus):
    """The line every runner prints, so a corpus's terms travel with its numbers."""
    c = cells(corpus)
    learners = {k[0] for k in c}
    units = {k[1] for k in c}
    per = collections.Counter(k[0] for k in c)
    n = sorted(per.values())
    positioned = sum(1 for u in units if corpus.position(u) is not None)
    return {"corpus": corpus.name, "licence": corpus.licence,
            "learners": len(learners), "units": len(units), "cells": len(c),
            "units_per_learner_median": n[len(n) // 2] if n else 0,
            "units_with_external_position": positioned,
            "has_cohorts": corpus.cohort(next(iter(learners))) is not None if learners else False}


def sequences(corpus):
    """learner -> unit -> sorted [(time, outcome)]. Keeps individual events, which cells() discards.

    build_observations needs this because "passed A BEFORE reaching B" has to be decided on the
    A-events that precede B, not on A's whole record -- on a practice corpus a learner's A attempts
    routinely straddle B, and letting the later ones count leaks the future into the conditioning
    variable."""
    out = collections.defaultdict(lambda: collections.defaultdict(list))
    for learner, unit, time, outcome in corpus.events():
        out[learner][unit].append((time, float(outcome)))
    for d in out.values():
        for v in d.values():
            # SORT BY TIME ONLY, and rely on Python's stable sort to keep input order within ties.
            # A plain v.sort() would order ties by OUTCOME, which is not a time order at all. It
            # matters on EDM Cup, where every problem in a unit test carries the assignment's
            # timestamp, so a learner's cells for one skill routinely tie -- and picking the lowest
            # outcome instead of the first flips passed_A for some of them.
            v.sort(key=lambda e: e[0])
    return out


def build_observations(corpus, pass_threshold=0.5, pass_on="prior", outcome="all"):
    """pair -> [(learner, passed_A, residual_outcome_B, raw_outcome_B)] -- the direction contrast's
    input, for any corpus.

    TWO POLICIES, DECLARED RATHER THAN BURIED. The two direction studies were written independently
    and made different choices, which only became visible when they were put behind one function:

        pass_on  "prior"  passed_A is decided on the A-events PRECEDING the first B-event. Right for
                          a practice corpus, where a learner's A attempts routinely straddle B and
                          letting later ones count leaks the future into the conditioning variable.
                 "first"  passed_A is the FIRST A-event alone. Right where an event is already an
                          aggregate of one sitting, as in a unit test.
        outcome  "all"    outcome at B is the mean over all B-events.
                 "first"  outcome at B is the first B-event alone -- "how did they do when they
                          first got there", which is what a unit-test corpus means.

    On a corpus whose adapter yields one event per cell the two collapse, so this is a real choice
    only where events repeat. Each study states its own in one line; neither is a default worth
    hiding, and the pair of them is the entire difference between the two studies' inputs.

    The residual is an attempt-weighted mean over the learner's OTHER units, and it is a PROXY FOR
    UNOBSERVED UPSTREAM PREREQUISITES, not an ability control -- see docs/specs/ESTIMAND.md section 4.
    edmcup-direction was cell-weighted and assist2012-direction attempt-weighted, which looks like a
    third conflict and is not: EDM Cup's adapter yields one event per cell, so attempt-weighting over
    its events IS cell-weighting. That difference lives in the adapter, where it belongs.
    """
    import bisect
    if pass_on not in ("prior", "first") or outcome not in ("all", "first"):
        raise ValueError("pass_on must be prior|first and outcome must be all|first")
    obs = collections.defaultdict(list)
    for learner, d in sequences(corpus).items():
        firsts = {u: v[0][0] for u, v in d.items()}
        tot = sum(o for v in d.values() for _t, o in v)
        cnt = sum(len(v) for v in d.values())
        sums = {u: sum(o for _t, o in v) for u, v in d.items()}
        lens = {u: len(v) for u, v in d.items()}
        times = {u: [t for t, _o in v] for u, v in d.items()}
        for b, tb in firsts.items():
            mb = d[b][0][1] if outcome == "first" else sums[b] / lens[b]
            for a in d:
                if a == b or firsts[a] >= tb:
                    continue
                rest_n = cnt - lens[a] - lens[b]
                if rest_n <= 0:
                    continue
                if pass_on == "first":
                    ma = d[a][0][1]
                else:
                    cut = bisect.bisect_left(times[a], tb)
                    if cut == 0:
                        continue
                    prior = d[a][:cut]
                    ma = sum(o for _t, o in prior) / len(prior)
                distal_proxy = (tot - sums[a] - sums[b]) / rest_n
                obs[(a, b)].append((learner, ma >= pass_threshold, mb - distal_proxy, mb))
    return obs


# ---------------------------------------------------------------- adapters
# One class per corpus. This is the whole cost of adding a dataset.

class EdmCup(Corpus):
    name = "EDM Cup 2023"
    licence = "ASSISTments Data Terms of Use (2020) -- non-commercial, no redistribution, open outcomes"

    def __init__(self, root):
        self.root = pathlib.Path(root)
        self._cls = {}

    def events(self):
        with open(self.root / "cells.tsv") as f:
            r = csv.reader(f, delimiter="\t")
            next(r)
            for learner, cls, unit, t, mean, n in r:
                self._cls[learner] = cls
                yield learner, unit, float(t), float(mean)

    def cohort(self, learner):
        return self._cls.get(learner)

    def position(self, unit):
        m = re.match(r"^(K|\d+)\.", unit or "")
        return None if not m else (0 if m.group(1) == "K" else int(m.group(1)))


class Junyi2020(Corpus):
    """Junyi Academy 2018-19 problem log ("Junyi 2020"), unit = hashed content id `ucid`.

    THE CLOCK IS QUARTER-HOURLY (recorded 2026-09-24). Every `timestamp_TW` is 'YYYY-MM-DD HH:MM:00
    UTC' on a 15-minute grid, 98.9% of attempts share a (learner, timestamp) with another, and file
    order within a learner is not chronological (876,859 of 1,819,187 consecutive within-learner rows
    go backwards, per the codebook check). So order inside a 15-minute slot is NOT in the data. Time
    is yielded as the raw string, which sorts correctly; consumers must treat equal times as
    UNORDERED -- compare strictly, never break ties by file order or by outcome. sequences() and
    build_observations() keep file order within ties, which is meaningless here, so neither may be
    used on this corpus without first dropping tied pairs. Anything that needs order within a slot
    is unanswerable on this corpus at that grain. (any_corpus.py's reachability is tie-safe: a merge
    node counts only if strictly later than both parents.)
    """

    name = "Junyi Academy 2020"
    licence = "CC BY-NC-SA 4.0 -- non-commercial, share-alike, attribution"

    STAGE = {"elementary": 0, "junior": 6, "senior": 9}

    def __init__(self, root, limit=None):
        self.root = pathlib.Path(root)
        self.limit = limit
        self._pos = {}
        for r in csv.DictReader(open(self.root / "Info_Content.csv", encoding="utf-8-sig")):
            # learning_stage is the Taiwanese school stage -- EXTERNAL to the corpus, unlike the
            # hashed level1..4 tree, so it is the only field here that can float a depth figure.
            self._pos[r["ucid"]] = self.STAGE.get((r.get("learning_stage") or "").strip())

    def events(self):
        with open(self.root / "Log_Problem.csv", encoding="utf-8-sig") as f:
            for i, r in enumerate(csv.DictReader(f)):
                if self.limit and i >= self.limit:
                    break
                ok = (r.get("is_correct") or "").strip().lower()
                if ok not in ("true", "false"):
                    continue
                yield (r["uuid"], r["ucid"], r["timestamp_TW"], 1.0 if ok == "true" else 0.0)

    def position(self, unit):
        return self._pos.get(unit)


class Xes3g5m(Corpus):
    name = "XES3G5M"
    licence = "repo MIT; data licence unstated -- treat as non-redistributable"

    def __init__(self, root):
        self.root = pathlib.Path(root)

    def events(self):
        import json
        known = {int(k) for k in json.loads((self.root / "cid2route.json").read_text())}
        with open(self.root / "attempts.tsv") as f:
            for line in f:
                uid, _q, c, res, t = line.rstrip("\n").split("\t")
                for part in c.split("_"):
                    if part.isdigit() and int(part) in known:
                        yield uid, "k%s" % part, float(t), 1.0 if res == "1" else 0.0

    # position() stays None by inheritance: the route tree is INTERNAL, so it cannot say what sits
    # beneath the corpus. studies/identifiability/window-depth/ records that as the finding rather than a shortcoming.


#: How many KT1 members ednet/RESTORE-KT1.sh extracts. The dense EdNet studies read this many.
KT1_RESTORED = 60308


def kt1_members(zip_path, n=None):
    """The reproducible EdNet learner set: the first n KT1 CSV members in the zip's namelist order.

    Every EdNet reader goes through this, directly or via EdNet.events, so a learner set is a
    function of the archive and a number and never of what happens to be extracted on disk. Returns
    the open ZipFile (the caller reads members from it) and the member names.
    """
    import zipfile
    z = zipfile.ZipFile(zip_path)
    names = [m for m in z.namelist() if m.startswith("KT1/") and m.endswith(".csv")]
    return z, (names[:n] if n else names)


#: EdNet's undocumented "no tag" sentinel. 797 of 13,169 questions carry `-1` and nothing else (no
#: question mixes it with real tags); the README documents tags only as expert-annotated integers.
#: Until 2026-09-24 three readers made it a KC (unit `t-1` / `-1`) and two dropped it.
EDNET_NO_TAG = "-1"


def ednet_questions(contents):
    """question_id -> (answer key, [KC tags]) from contents/questions.csv, the one parse of it.

    Tags keep file order (callers taking the leading tag depend on it). `-1` is dropped, so a
    question carrying only `-1` has no KC and yields no evidence on any unit."""
    out = {}
    with open(pathlib.Path(contents) / "questions.csv", newline="", encoding="utf-8",
              errors="replace") as fh:
        for r in csv.DictReader(fh):
            tags = [t.strip() for t in (r.get("tags") or "").split(";")
                    if t.strip() and t.strip() != EDNET_NO_TAG]
            out[r["question_id"]] = ((r.get("correct_answer") or "").strip(), tags)
    return out


class EdNet(Corpus):
    """EdNet KT1, STREAMED FROM THE ZIP AND NEVER EXTRACTED.

    Its own restore note says why: 784,309 files hold 3.1 GB of data but allocate about 31 GB,
    because the mean file is a few KB against a much larger block. Streaming is not an optimisation
    here, it is the only way the corpus fits. That the contract accommodates a zip member as
    naturally as a CSV is the point of having a contract.

    Unit is the KC tag. A question carrying several tags is evidence on each, which is how EdNet's
    own tag files are built. Correctness needs the answer key from contents/questions.csv. The
    `-1` sentinel is not a KC (ednet_questions), so its 797 questions contribute no events.

    `tags` picks the KC MODEL, and it is a parameter because two callers legitimately want
    different ones. "all" (the default) treats a multi-tagged question as evidence on each tag and
    yields 189 units; "first" takes only the leading tag and yields 142, which is the model
    studies/identifiability/overlap/atlas.py's numbers were computed under. Neither is the true one and the difference is
    not small, so it is named in the output rather than left to whichever caller ran last.

    WHICH LEARNERS, AND WHY IT IS A PREFIX RATHER THAN A SAMPLE. `learners` takes the first N
    members of the zip's namelist. That order is not id order -- the archive interleaves
    (u246317, u51472, u213653, ...) -- so a prefix is already an arbitrary slice of the population,
    and unlike a random draw it is REGENERABLE FROM THE ARCHIVE ALONE. studies/identifiability/a7-readjudication/ is why
    that matters: the atlas's EdNet row was computed over an extracted subset that was later
    deleted, and it cannot now be re-derived.
    """

    name = "EdNet KT1"
    licence = "CC BY-NC 4.0 -- non-commercial, no model training"

    def __init__(self, zip_path, contents, learners=None, tags="all"):
        if tags not in ("all", "first"):
            raise ValueError("tags must be 'all' or 'first', not %r" % (tags,))
        self.zip_path = pathlib.Path(zip_path)
        self.learners = learners          # cap the number of KT1 members read
        self.tag_model = tags
        q = ednet_questions(contents)
        self.key = {k: v[0] for k, v in q.items()}
        self.tags = {k: v[1] for k, v in q.items()}

    def events(self):
        import io
        z, members = kt1_members(self.zip_path, self.learners)
        with z:
            for m in members:
                learner = m.rsplit("/", 1)[-1][:-4]
                with z.open(m) as fh:
                    for r in csv.DictReader(io.TextIOWrapper(fh)):
                        q = r.get("question_id")
                        ans = self.key.get(q)
                        if not ans:
                            continue
                        ok = 1.0 if (r.get("user_answer") or "").strip() == ans else 0.0
                        ts = self.tags.get(q, ())
                        for t in (ts[:1] if self.tag_model == "first" else ts):
                            yield learner, "t%s" % t.strip(), float(r["timestamp"]), ok

    # position() stays None: EdNet's tags carry no level scale, so depth is UNKNOWN by construction.


class Duolingo(Corpus):
    """Duolingo spaced-repetition traces (Settles & Meeder, ACL 2016), one learning language at a time.

    CC BY-NC 4.0 -- non-commercial, attribution -- taken from Duolingo's own Harvard Dataverse release
    (doi:10.7910/DVN/N8XJME), not from a third-party mirror, and checked against its published MD5.

    EVERY ROW IS A REVIEW. The release covers 11.9 days and not one of its 12,854,226 rows has
    history_seen == 0: every word was introduced BEFORE the window opens. So the order in which a
    learner first MET two words -- the order every positivity and direction argument in this
    programme runs on -- is entirely off the record, and what is observable is review order chosen by
    a spaced-repetition scheduler. Any caller treating first-observed-in-window as first-exposure is
    reading a retention signal as a learning-order one. This is left-censoring at 100%, the extreme
    case of studies/identifiability/window-depth/.

    Unit is the lemma, taken from lexeme_string (`surface/lemma<tags>`), within one language; lexeme
    ids distinguish every inflected form and would split one word into dozens. Outcome is p_recall,
    the share of the session's exercises recalled correctly.
    """

    name = "Duolingo spaced repetition"
    licence = "CC BY-NC 4.0 -- non-commercial, attribution (Settles & Meeder 2016)"
    left_censored_share = 1.0      # measured: 0 of 12,854,226 rows are first exposures

    def __init__(self, path, language):
        self.path = pathlib.Path(path)
        self.language = language
        self.name = "Duolingo (%s)" % language

    @staticmethod
    def lemma(lexeme_string):
        head = (lexeme_string or "").split("<")[0]
        return head.split("/", 1)[1] if "/" in head else head

    def events(self):
        import gzip
        with gzip.open(self.path, "rt", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r["learning_language"] != self.language:
                    continue
                yield (r["user_id"], self.lemma(r["lexeme_string"]),
                       float(r["timestamp"]), float(r["p_recall"]))


class Eedi(Corpus):
    """Eedi NeurIPS 2020 Education Challenge, tasks 1-2: diagnostic maths questions, UK, 2018-2020.

    Terms confirmed with Eedi as research use (2026-09-24); no redistribution. Reads the slim TSV
    that data/ingest/eedi/slim.py writes from the release zip, plus two small metadata files read straight
    from that zip. student_metadata is never opened here: demographics live in a side file
    (data/ingest/eedi/demographics.py) that only studies naming a use for them read.

    Unit is the LEVEL-3 subject -- the leaf of Eedi's own four-level maths tree (308 leaves, e.g.
    "Expanding Double Brackets"). 91% of questions carry exactly one leaf; a question tagged with
    several is evidence on each, as XES3G5M's kc_level files are built. Questions with no leaf
    (90 of 27,613) are dropped rather than promoted to a coarser level, which would mix grains.

    cohort() is GroupId, the teacher's class the quiz was set to. A learner who moved class is
    assigned the group of their first answer in a real class. GroupId 2580 is NOT a class: it holds
    61,930 learners platform-wide and is the first group of 12.5% of learners (H-INNOV,
    studies/measurement/innovation-audit/, 2026-10-08), so it is skipped (PLATFORM_GROUPS). A learner
    seen only there has no cohort.
    position() is None: the subject tree carries no year or key stage.

    TIME IS THE LATEST ANSWER, NOT THE FIRST (limitation recorded 2026-09-24, unrepairable). The
    release keeps one row per (learner, question): "when a student has multiple answer records to the
    same question, we keep the latest answer record" (Wang et al. 2020, s2.1). So `time` is
    DateAnswered of the LAST attempt, and IsCorrect is that attempt's outcome. Earlier attempts and
    the moment a learner first met a question are not in the data, and nothing here can restore
    them. Any consumer reading first touch, "met A before B", outcome at first touch or first-pass
    time is reading last-answer order: a question re-answered later moves later and carries its
    re-answer outcome, which biases toward correct. DateAnswered is also minute-resolution and 63.9%
    of answers share a (learner, minute) with another, so order inside a minute is file order.
    A study that reads Eedi order must say so beside its number.
    """

    name = "Eedi NeurIPS 2020"
    licence = "Eedi: research use confirmed with the provider (2026-09-24); no redistribution"

    #: GroupIds that are platform-wide pools, not classes. Never assigned as a cohort.
    PLATFORM_GROUPS = frozenset({"2580"})

    def __init__(self, answers_tsv, zip_path, with_cohorts=False):
        import ast
        import io
        import zipfile
        self.answers = pathlib.Path(answers_tsv)
        z = zipfile.ZipFile(zip_path)
        level = {}
        with z.open("data/metadata/subject_metadata.csv") as f:
            for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig")):
                level[int(r["SubjectId"])] = int(r["Level"])
        self.leaves = {}
        with z.open("data/metadata/question_metadata_task_1_2.csv") as f:
            for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8")):
                tags = [t for t in ast.literal_eval(r["SubjectId"]) if level.get(t) == 3]
                if tags:
                    self.leaves[r["QuestionId"]] = ["s%d" % t for t in tags]
        self._cohort = {} if with_cohorts else None

    def events(self):
        with open(self.answers, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                if (self._cohort is not None and r["UserId"] not in self._cohort
                        and r["GroupId"] and r["GroupId"] not in self.PLATFORM_GROUPS):
                    self._cohort[r["UserId"]] = r["GroupId"]
                for unit in self.leaves.get(r["QuestionId"], ()):
                    yield r["UserId"], unit, r["DateAnswered"], float(r["IsCorrect"])

    def cohort(self, learner):
        return (self._cohort or {}).get(learner)


class Slam(Corpus):
    """Duolingo SLAM 2018 shared task (Settles et al. 2018): every learner's FIRST 30 DAYS, token-scored.

    CC BY-NC 4.0, Harvard Dataverse doi:10.7910/DVN/8SWHNO, behind a guestbook (name, email,
    institution). One course at a time: en_es, es_en or fr_en.

    Unlike the half-life release (shared/corpus.Duolingo, 0% first exposures), this one opens at a
    learner's first session, so the order in which words and constructions were MET is on the record.
    The challenge split each learner's timeline chronologically into train / dev / test, with dev and
    test labels in separate .key files; all three are read, or every timeline would stop at day ~20.

    Two grains, because the right unit for a language is not obvious:
        word       the lowercased token as the learner had to produce or recognise it
        construct  UD part of speech + its morphological bundle, e.g. VERB|Mood=Ind|Person=3|Tense=Past
                   -- nearer a grammar skill, and far fewer units, so denser coverage
    Outcome is 1 - label (the release marks a MISTAKE as 1). Time is `days` since the learner's first
    session. `countries` is on every exercise header and is never kept.
    """

    name = "Duolingo SLAM 2018"
    licence = "CC BY-NC 4.0 -- non-commercial, attribution (Settles et al. 2018)"

    def __init__(self, root, course, grain="construct"):
        assert grain in ("word", "construct")
        self.root = pathlib.Path(root)
        self.course, self.grain = course, grain
        self.name = "Duolingo SLAM %s (%s)" % (course, grain)

    def _unit(self, token, pos, morph):
        if self.grain == "word":
            return token.lower()
        feats = [f for f in morph.split("|") if f and not f.startswith("fPOS=")]
        return "|".join([pos] + sorted(feats))

    def events(self):
        for split in ("train", "dev", "test"):
            path = next(self.root.glob("%s.slam.*.%s" % (self.course, split)))
            key = {}
            if split != "train":
                with open(str(path) + ".key", encoding="utf-8") as f:
                    for line in f:
                        tid, lab = line.split()
                        key[tid] = int(lab)
            user = days = None
            with open(path, encoding="utf-8") as f:
                for line in f:
                    if line.startswith("# user:"):
                        meta = dict(kv.split(":", 1) for kv in line[2:].split())
                        user, days = meta["user"], float(meta["days"])
                        continue
                    if not line.strip() or line.startswith("#"):
                        continue
                    cols = line.split()
                    lab = int(cols[6]) if split == "train" else key.get(cols[0])
                    if lab is None:
                        continue
                    yield user, self._unit(cols[1], cols[2], cols[3]), days, float(1 - lab)


class MoocCubeX(Corpus):
    """MOOCCubeX at CONCEPT grain, from the filtered problem log.

    Only 33,856 records survived filtering from 133,384,333 raw rows, which this repo already
    recorded when the course-grain work was done. That thinness is the corpus's defining feature at
    this grain and the runner will show it rather than hide it.

    Ingest discipline, unchanged from the original pass: name, gender, year_of_birth and school are
    discarded at the door; only a pseudonymous id, the concept and the timestamp are read.
    """

    name = "MOOCCubeX (concept grain)"
    licence = "research use; no redistribution"

    def __init__(self, root):
        self.root = pathlib.Path(root)
        self._concept = {}
        with open(self.root / "concept-problem.txt", encoding="utf-8") as f:
            for line in f:
                parts = line.rstrip("\n").split("\t")
                if len(parts) >= 2:
                    self._concept.setdefault(parts[1].strip(), parts[0].strip())

    def events(self):
        import json as _json
        with open(self.root / "user-problem-filtered.jsonl", encoding="utf-8") as f:
            for line in f:
                try:
                    d = _json.loads(line)
                except ValueError:
                    continue
                unit = self._concept.get(d.get("p"))
                if not unit or not d.get("t"):
                    continue
                yield d["u"], unit, d["t"], float(d.get("ok") or 0)


class Assistments2012(Corpus):
    """ASSISTments 2012-13 skill builders, with CCSS grade as the external position.

    The grade comes from the derived skill-to-CCSS map built in studies/measurement/assist2012-direction/, which is
    itself a name match against EDM Cup's published code/description pairs. That map's exact-name
    half was the only part that survived scrutiny there, so grade is used here only for
    LEFT-CENSORING DEPTH -- a coarse, robust reading -- and never to orient an edge.

    cohort() is available but OFF by default: the assignment_id proxy lives in assist_rich.csv,
    475 MB, and a window run has no use for it. Pass with_cohorts=True when clustering is needed.
    """

    name = "ASSISTments 2012-13"
    licence = "ASSISTments data terms (WPI IRB-approved) -- research use, no redistribution, cite Feng et al. 2009"

    def __init__(self, root, ccss_map=None, with_cohorts=False):
        self.root = pathlib.Path(root)
        self._pos = {}
        if ccss_map and pathlib.Path(ccss_map).exists():
            import json as _json
            for skill, rec in _json.loads(pathlib.Path(ccss_map).read_text()).items():
                m = re.match(r"^(K|\d+)\.", rec.get("ccss") or "")
                if m:
                    self._pos[skill] = 0 if m.group(1) == "K" else int(m.group(1))
        self._cohort = {}
        if with_cohorts:
            with open(self.root / "assist_rich.csv") as f:
                for r in csv.DictReader(f):
                    u, a, t = r.get("user_id"), r.get("assignment_id"), r.get("start_time")
                    if u and a and t and (u not in self._cohort or t < self._cohort[u][1]):
                        self._cohort[u] = (a, t)

    def events(self):
        """`correct` is 1, 0 or a partial-credit decimal in (0, 1) (211 rows of assist_slim.csv).
        Scored as the release recommends for a dependent variable -- "1 = correct, <1 = Incorrect"
        -- so partial credit is 0. Until 2026-09-24 int() raised on the decimals and they were
        dropped, which removed exactly the attempts that needed hints or retries."""
        with open(self.root / "assist_slim.csv") as f:
            for r in csv.DictReader(f):
                s, t = r.get("skill_id"), r.get("start_time")
                if not s or not t:
                    continue
                try:
                    c = float(r["correct"])
                except (ValueError, TypeError, KeyError):
                    continue
                yield r["user_id"], s, t, 1.0 if c == 1.0 else 0.0

    def cohort(self, learner):
        rec = self._cohort.get(learner)
        return rec[0] if rec else None

    def position(self, unit):
        return self._pos.get(unit)


#: The DataShop sample every reader uses: DataShop's default, which holds the whole dataset.
DATASHOP_SAMPLE = "All Data"


def datashop_export(root, sample=DATASHOP_SAMPLE, dsid=None):
    """The one DataShop student-step export to read under `root`: the file whose sample is `sample`.

    A DataShop download holds one export per sample, and samples are not parts of a whole: 'All Data'
    is the dataset, while others are subsets (ds1190's '2016 data' is one term) or the same
    transactions rolled up differently (ds1275's 'All Data1'). Reading whichever file sorts first
    picked a subset for ds1190 and ds649 and the re-rolled copy for ds1275 until 2026-09-25, so every
    DataShop reader goes through here. The sample is matched on the file name DataShop writes
    (`<ds>_student_step_<Sample>_<n>_<stamp>.txt`) and confirmed against the file's `Sample` column.
    `dsid` narrows a directory that holds several datasets' exports to one of them.
    """
    root = pathlib.Path(root)
    if root.is_file():
        return root
    token = "_student_step_%s_" % sample.replace(" ", "_")
    hits = []
    for path in sorted(root.glob("%s_student_step*.txt" % (dsid or "*"))):
        rest = path.name.split(token, 1)
        if len(rest) != 2 or not re.match(r"\d+_", rest[1]):
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            head = f.readline().rstrip("\n").split("\t")
            first = f.readline().rstrip("\n").split("\t")
        if "Sample" in head and len(first) > head.index("Sample") and first[head.index("Sample")] == sample:
            hits.append(path)
    if len(hits) != 1:
        raise SystemExit("expected exactly one DataShop student-step export with Sample == %r under %s, "
                         "found %d; see data/data-sources.json (datashop)" % (sample, root / (dsid or ""), len(hits)))
    return hits[0]


def datashop_is_qa(root):
    """True when an export came from DataShop's QA server (its TERMS.html points at qa.datashop.org).

    QA-server datasets are not public, and their ids collide with different production datasets, so
    no reported result may rest on them (maintainer, 2026-09-25)."""
    terms = pathlib.Path(root) / "TERMS.html"
    return terms.exists() and "qa.datashop.org" in terms.read_text(encoding="utf-8", errors="replace")


def datashop_exports(*roots):
    """{dataset id: its 'All Data' export} for every public export directory under `roots`.

    A root may be a directory of export directories or an export directory itself, and an export
    directory may hold several datasets' files side by side. QA-server exports are skipped
    (datashop_is_qa). The first directory seen for a dataset wins; duplicate downloads of one dataset
    are byte-identical."""
    out = {}
    for root in roots:
        root = pathlib.Path(root)
        if not root.is_dir():
            continue
        dirs = [root] if any(root.glob("*student_step*.txt")) else sorted(p for p in root.iterdir() if p.is_dir())
        for d in dirs:
            if datashop_is_qa(d) or not any(d.glob("*student_step*.txt")):
                continue
            for ds in sorted({p.name.split("_student_step")[0] for p in d.glob("*student_step*.txt")}):
                if ds not in out:
                    out[ds] = datashop_export(d, dsid=ds)
    return out


#: The one ds1275 DataShop sample every reader uses. See ds1275_export.
DS1275_SAMPLE = DATASHOP_SAMPLE


def ds1275_export(root):
    """The single ds1275 student-step export to read: the file whose `Sample` column is DS1275_SAMPLE.

    ds1275 is on disk as TWO exports of the same dataset, samples 'All Data' and 'All Data1'. They are
    not two halves: both hold the same 2,063 learners, the same 359,804 transactions (the README's
    count), the same 19,960 (learner, KC) cells and identical first times per cell. They differ only
    in how transactions were rolled up into steps -- 'All Data1' splits a run of hints into one row
    per hint, so it has 319,249 rows to 'All Data''s 303,720 -- and so no event key deduplicates
    them: matching on (learner, KC, step start, first attempt) leaves 33,939 + 49,468 rows that are
    the same transactions rolled up differently. The only correct dedup is to read one sample.

    'All Data' is kept: DataShop's default sample, the only one with its KC-model Opportunity and
    Predicted Error Rate columns populated, the export whose md5 data/data-sources.json records, and
    the file expert_vs_data.py's committed result reproduces from. Until 2026-09-24 three readers
    globbed both and counted every transaction twice (codebook, datashop 'Sample').
    """
    return datashop_export(root, DS1275_SAMPLE)


class Junyi2015(Corpus):
    """Junyi 2015 via the DataShop ds1275 student-step export (one sample: see ds1275_export).

    Unit is `KC (Exercise)`, which is the same 837-exercise vocabulary the authored prerequisite
    graph uses -- so this corpus and that graph join exactly, which the 2020 release does NOT
    (its content ids are hashed and only 34 of 837 names survive a match).

    position() stays None deliberately. Junyi ships an AUTHORED graph, not a levelled curriculum,
    and that graph is what the programme puts under test -- using its own depth as an external
    scale would be circular.
    """

    name = "Junyi 2015 (ds1275)"
    licence = "DataShop: research use, no redistribution"

    def __init__(self, root):
        self.root = pathlib.Path(root)

    def events(self):
        with open(ds1275_export(self.root), encoding="utf-8", errors="replace") as f:
            head = f.readline().rstrip("\n").split("\t")
            ix = {name: i for i, name in enumerate(head)}
            for line in f:
                c = line.rstrip("\n").split("\t")
                if len(c) <= ix["First Attempt"]:
                    continue
                kc = c[ix["KC (Exercise)"]].strip()
                t = c[ix["Step Start Time"]].strip()
                if not kc or not t:
                    continue
                yield (c[ix["Anon Student Id"]], kc, t,
                       1.0 if c[ix["First Attempt"]].strip().lower() == "correct" else 0.0)


ADAPTERS = {
    "edmcup": lambda: EdmCup(os.environ["EDMCUP_DIR"]),
    "junyi2020": lambda: Junyi2020(os.environ["JUNYI2020_DIR"], limit=int(os.environ.get("LIMIT", 0)) or None),
    "xes3g5m": lambda: Xes3g5m(os.environ["XES_DIR"]),
    "ednet": lambda: EdNet(os.environ["EDNET_ZIP"], os.environ["EDNET_CONTENTS"],
                           learners=int(os.environ.get("LIMIT", 0)) or None),
    "mooccubex": lambda: MoocCubeX(os.environ["MOOCCUBEX_DIR"]),
    "assistments2012": lambda: Assistments2012(
        os.environ["ASSIST_DIR"], ccss_map=os.environ.get("ASSIST_CCSS_MAP")),
    "junyi2015": lambda: Junyi2015(os.environ["DS1275_DIR"]),
    "duolingo": lambda: Duolingo(os.environ["DUOLINGO_GZ"], os.environ.get("DUOLINGO_LANG", "it")),
    "eedi": lambda: Eedi(os.environ["EEDI_ANSWERS"], os.environ["EEDI_ZIP"]),
    "slam": lambda: Slam(os.environ["SLAM_DIR"], os.environ.get("SLAM_COURSE", "en_es"),
                         os.environ.get("SLAM_GRAIN", "construct")),
}
