"""Does the short-lived part of the prerequisite drop behave the same way in every domain?

Paper 1 §6.4 question 2 asks which mechanism real prerequisites run on, by domain. Three signatures
were read corpus-wide in §5.2: no load effect on time on task (EdNet only), sparse conjunctive
structure, and a drop that shrinks with lag (`studies/identifiability/overlap/lag_bands.py`: DECAYS
in ASSISTments, Eedi, XES3G5M and EdNet). This study reads the one signature that can be split by
domain on the corpora in hand, the lag decay, separately for each domain those corpora label.

Why only decay. Load needs per-question timing, which only EdNet has, and its corpus-wide effect is
already null (`studies/simulation/validate/load_form.py`). The conjunctive statistic needs about 30
densely co-attempted items per arm and is already UNANSWERABLE on EdNet at full size
(`studies/identifiability/conjunctive/replicate.py`); a domain split can only cut its power
further. Both are stated as out of scope here rather than run underpowered.

DOMAINS (fixed from metadata alone; label counts were read before this was written, outcomes were not)
  XES3G5M   the module under the 拓展思维 ("extended thinking") branch of the KC route: word problems,
            computation, combinatorics, counting, geometry, number theory, travel (563 of 866 KCs).
            KCs on other branches are left out.
  Eedi      the level-1 strand of the subject tree: Number, Algebra, Geometry and Measure, Data and
            Statistics. Leaves under the Advanced and Physics strands are left out.
  EdNet     TOEIC section by the part of the tag's questions: Listening (parts 1-4) or Reading
            (parts 5-7). A tag counts only if at least 90% of its questions sit in one section.
  ASSISTments is not used: its skill-to-CCSS map is fuzzy on half its skills
  (`studies/measurement/assist2012-direction/`).

PRE-REGISTERED (committed before any real corpus is read)

  pairs      ordered pairs with A and B in the same domain; up to 3,000 per domain, drawn with a seed
             fixed by corpus and domain (shared.seeds.arm_seed)
  signature  per domain, lag_bands' contrast D = drop(LATE, 7+ days) - drop(EARLY, under a day) over
             pairs readable in both bands (MIN_CELL 5 per cell); a domain with fewer than 30 such
             pairs is UNANSWERABLE
  spread     R = max - min of the answerable domains' mean D
  null       2,000 permutations of domain labels across the B items of those pairs (sizes kept);
             each pair moves with its B item, so item clustering is preserved
  interval   2,000 bootstrap draws resampling B items within each domain, giving R's 95% interval
  per corpus UNANSWERABLE          fewer than 2 answerable domains
             DIFFERS BY DOMAIN     R above the null's 97.5th percentile AND R >= 0.03
             INVARIANT             R's bootstrap upper bound < 0.03
             UNRESOLVED            otherwise
             (0.03 is half again the ±0.02 FLAT band lag_bands uses for a single corpus.)
  programme  DOMAIN-DEPENDENT if at least two corpora return DIFFERS BY DOMAIN; DOMAIN-INVARIANT if
             every answerable corpus returns INVARIANT; MIXED otherwise
  reported, gating nothing: each domain's own lag_bands verdict (DECAYS / FLAT / ...), its mean
             early and late drop, and its share of readable pairs by band

  FLOOR (run first, on synthetic learners; no real number is read unless it passes). Two domains of
  40 items, each a chain of planted gates, learners meeting items in random order:
    SAME        both domains' gates decay with lag (tau 5 days): DIFFERS BY DOMAIN in 0 of 3 seeds
    DIFFERENT   one domain's gate decays, the other's is constant: DIFFERS BY DOMAIN in 3 of 3 seeds
  The floor reads the gated pairs only, as lag_bands' floor does.

WHAT IT CANNOT SEPARATE. Real pairs are arbitrary within-domain pairs, as in lag_bands, so D measures
how the estimand moves with lag in that domain, whatever the cause. Domains differ in difficulty,
pacing and who studies them, so a domain difference is a difference in the estimand, not proof that
the prerequisite mechanism differs. Eedi keeps only each learner's latest answer to a question, so
its lags run between latest answers (`studies/identifiability/overlap/LAG-BANDS.md`).

DIRECTION: symmetric -- A and B take their roles from each learner's timeline (A attempted before B),
and D is a within-pair contrast of lag bands; no edge orientation is read.

    python3 domains.py floor
    python3 domains.py real [--corpora xes3g5m,eedi,ednet] [--out out/domains.json]
"""

from __future__ import annotations

import csv
import io
import json
import random
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OVERLAP = ROOT / "studies/identifiability/overlap"
sys.path.insert(0, str(OVERLAP))
sys.path.insert(0, str(ROOT / "studies/identifiability/latent-shape"))
sys.path.insert(0, str(ROOT))

import lag_bands as LB  # noqa: E402
from positivity import at_item, states, timelines  # noqa: E402
from shared.paths import data_path  # noqa: E402
from shared.seeds import arm_seed  # noqa: E402

SEED = 20260925
CAP, MIN_BOTH, PERMS, BOOT, BAR = 3000, 30, 2000, 2000, 0.03
EDNET_PURE = 0.90
XES_BRANCH = "拓展思维"
EEDI_STRANDS = ("Number", "Algebra", "Geometry and Measure", "Data and Statistics")


# ------------------------------------------------------------------ the statistic

def pair_d(rows):
    """Pairs readable in both EARLY and LATE, as (B item, D)."""
    return [(r["b"], r["drops"]["LATE"] - r["drops"]["EARLY"]) for r in rows
            if r["drops"]["EARLY"] is not None and r["drops"]["LATE"] is not None]


def spread(by_domain):
    means = [float(np.mean([d for _b, d in v])) for v in by_domain.values()]
    return max(means) - min(means)


def heterogeneity(by_domain, seed):
    """R, its permutation null over B-item labels, and its within-domain B-item bootstrap."""
    doms = {k: v for k, v in by_domain.items() if len(v) >= MIN_BOTH}
    out = dict(answerable=sorted(doms), pairs={k: len(v) for k, v in by_domain.items()})
    if len(doms) < 2:
        out.update(verdict="UNANSWERABLE")
        return out
    r_obs = spread(doms)
    rng = np.random.default_rng(seed)

    b_dom, by_b = {}, defaultdict(list)
    for k, v in doms.items():
        for b, d in v:
            b_dom[b] = k
            by_b[b].append(d)
    items = sorted(by_b)
    labels = np.array([b_dom[b] for b in items])
    null = []
    for _ in range(PERMS):
        perm = rng.permutation(labels)
        g = defaultdict(list)
        for b, lab in zip(items, perm):
            g[lab].extend((b, d) for d in by_b[b])
        null.append(spread(g))

    boots = []
    for _ in range(BOOT):
        g = {}
        for k, v in doms.items():
            bs = sorted({b for b, _ in v})
            pick = rng.choice(len(bs), len(bs), replace=True)
            g[k] = [(bs[i], d) for i in pick for d in by_b[bs[i]]]
        boots.append(spread(g))

    null_hi = float(np.percentile(null, 97.5))
    lo, hi = (float(x) for x in np.percentile(boots, [2.5, 97.5]))
    if r_obs > null_hi and r_obs >= BAR:
        v = "DIFFERS BY DOMAIN"
    elif hi < BAR:
        v = "INVARIANT"
    else:
        v = "UNRESOLVED"
    out.update(R=r_obs, null_975=null_hi, null_mean=float(np.mean(null)), R_ci=[lo, hi], verdict=v,
               domain_mean_D={k: float(np.mean([d for _b, d in vv])) for k, vv in doms.items()})
    return out


# ------------------------------------------------------------------ floor

def synth_two(decay1: bool, decay2: bool, seed: int, learners=3000, per=40, gate=0.25, tau=5.0):
    """lag_bands.synth with two domains: items d0-* and d1-*, each a chain of gates."""
    rnd = random.Random(seed)
    parent = {}
    for dom in (0, 1):
        for k in range(1, per):
            parent[f"d{dom}-{k}"] = f"d{dom}-{k - 1}"
    decays = {0: decay1, 1: decay2}
    rows = []
    items = [f"d{dom}-{k}" for dom in (0, 1) for k in range(per)]
    for u in range(learners):
        ability = rnd.gauss(0, 1)
        t = rnd.uniform(0, 30) * LB.DAY
        seen_pass, first_t = {}, {}
        order = items[:]
        rnd.shuffle(order)
        for it in order:
            for _ in range(rnd.randint(1, 3)):
                t += (rnd.expovariate(1 / 0.01) if rnd.random() < 0.8 else rnd.expovariate(1 / 5.0)) * LB.DAY
                p = 1 / (1 + np.exp(-(0.3 + ability)))
                par = parent.get(it)
                if par is not None and it not in first_t and par in first_t and par not in seen_pass:
                    lag = (t - first_t[par]) / LB.DAY
                    p -= gate * (np.exp(-lag / tau) if decays[int(it[1])] else 1.0)
                ok = rnd.random() < max(0.02, min(0.98, p))
                first_t.setdefault(it, t)
                if ok:
                    seen_pass.setdefault(it, t)
                rows.append((f"u{u}", it, ok, t, False, False))
    return rows, parent


def run_floor():
    worlds = {"SAME": (True, True), "DIFFERENT": (True, False)}
    res = {}
    for name, (d1, d2) in worlds.items():
        verdicts = []
        for s in range(3):
            rows, parent = synth_two(d1, d2, seed=500 + s)
            ft, fp, oat = states(timelines(rows))
            idx = at_item(ft, oat)
            by = defaultdict(list)
            for child, par in parent.items():
                for b, d in pair_d(LB.analyse(ft, fp, idx, [(par, child)])):
                    by[child[:2]].append((b, d))
            h = heterogeneity(by, seed=s)
            verdicts.append(h)
            print(f"   {name:9s} seed {s}: R {h.get('R', float('nan')):+.3f}  null97.5 "
                  f"{h.get('null_975', float('nan')):+.3f}  CI {h.get('R_ci')}  pairs {h['pairs']}  -> {h['verdict']}",
                  flush=True)
        res[name] = verdicts
    ok = (not any(v["verdict"] == "DIFFERS BY DOMAIN" for v in res["SAME"])
          and all(v["verdict"] == "DIFFERS BY DOMAIN" for v in res["DIFFERENT"]))
    print(f"   FLOOR {'PASSES' if ok else 'FAILS'}")
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / "floor.json").write_text(json.dumps(dict(passes=ok, results=res), indent=1) + "\n")
    return ok


# ------------------------------------------------------------------ domains

def xes_domains():
    routes = json.loads((data_path("XES_DIR") / "cid2route.json").read_text(encoding="utf-8"))
    return {f"k{int(c)}": r[1] for c, r in routes.items() if len(r) > 1 and r[0] == XES_BRANCH}


def eedi_domains():
    z = zipfile.ZipFile(data_path("EEDI_ZIP"))
    with z.open("data/metadata/subject_metadata.csv") as f:
        rows = list(csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig")))
    by = {r["SubjectId"]: r for r in rows}

    def strand(sid):
        while by[sid]["Level"] != "1":
            sid = by[sid]["ParentId"]
        return by[sid]["Name"]
    out = {}
    for r in rows:
        if r["Level"] == "3" and (s := strand(r["SubjectId"])) in EEDI_STRANDS:
            out["s" + r["SubjectId"]] = s
    return out


def ednet_domains():
    parts = defaultdict(Counter)
    with open(data_path("EDNET_CONTENTS") / "questions.csv") as f:
        for r in csv.DictReader(f):
            first = r["tags"].split(";")[0].strip()
            parts[first]["Listening" if int(r["part"]) <= 4 else "Reading"] += 1
    out = {}
    for tag, c in parts.items():
        sec, n = c.most_common(1)[0]
        if n / sum(c.values()) >= EDNET_PURE:
            out["t" + tag] = sec
    return out


def loaders():
    import atlas
    return {"xes3g5m": (lambda: atlas.xes3g5m_rows(), xes_domains),
            "eedi": (lambda: atlas.eedi_rows(), eedi_domains),
            "ednet": (lambda: atlas.ednet_rows(), ednet_domains)}


def run_real(names, out):
    floor = json.loads((HERE / "out" / "floor.json").read_text())
    if not floor.get("passes"):
        raise SystemExit("floor has not passed; no real number is read")
    L = loaders()
    res = {}
    for name in names:
        read, domains = L[name]
        dom = domains()
        rows = ((u, i, ok, LB.to_seconds(t), h1, h2) for u, i, ok, t, h1, h2 in read())
        tl = timelines(rows)
        ft, fp, oat = states(tl)
        idx = at_item(ft, oat)
        groups = defaultdict(list)
        for it in sorted(idx):
            if it in dom:
                groups[dom[it]].append(it)
        by, per = {}, {}
        for d, items in sorted(groups.items()):
            pairs = [(a, b) for a in items for b in items if a != b]
            if len(pairs) > CAP:
                rng = np.random.default_rng(arm_seed(SEED, f"{name}:{d}"))
                pairs = [pairs[i] for i in rng.choice(len(pairs), CAP, replace=False)]
            prs = LB.analyse(ft, fp, idx, pairs)
            by[d] = pair_d(prs)
            per[d] = dict(items=len(items), pairs=len(pairs), lag=LB.contrast(prs), bands=LB.band_summary(prs))
            c = per[d]["lag"]
            print(f"  {name:8s} {d:22s} items {len(items):4d}  pairs {len(pairs):5d}  both {c['pairs_both']:5d}  "
                  + (f"early {c['early_mean']:+.3f} late {c['late_mean']:+.3f} D {c['mean_D']:+.4f} "
                     f"[{c['ci'][0]:+.4f}, {c['ci'][1]:+.4f}] " if "mean_D" in c else "")
                  + c["verdict"], flush=True)
        h = heterogeneity(by, seed=arm_seed(SEED, name))
        res[name] = dict(learners=len(tl), labelled_items=len(dom), domains=per, heterogeneity=h)
        print(f"  {name:8s} SPREAD R {h.get('R', float('nan')):+.4f}  null 97.5th {h.get('null_975', float('nan')):+.4f}  "
              f"CI {h.get('R_ci')}  -> {h['verdict']}\n", flush=True)
    vs = [v["heterogeneity"]["verdict"] for v in res.values()]
    answerable = [v for v in vs if v != "UNANSWERABLE"]
    if vs.count("DIFFERS BY DOMAIN") >= 2:
        overall = "DOMAIN-DEPENDENT"
    elif answerable and all(v == "INVARIANT" for v in answerable):
        overall = "DOMAIN-INVARIANT"
    else:
        overall = "MIXED"
    print(f"PROGRAMME VERDICT: {overall}  ({', '.join(f'{k}: {v}' for k, v in zip(res, vs))})")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(seed=SEED, cap=CAP, min_both=MIN_BOTH, bar=BAR, verdict=overall, corpora=res),
                              indent=1, default=str, ensure_ascii=False) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "floor"
    if mode == "floor":
        sys.exit(0 if run_floor() else 1)
    names = (sys.argv[sys.argv.index("--corpora") + 1].split(",") if "--corpora" in sys.argv
             else ["xes3g5m", "eedi", "ednet"])
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else HERE / "out" / "domains.json"
    run_real(names, out)
