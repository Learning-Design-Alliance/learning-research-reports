"""PRE-REGISTERED: does the dependence between two skills follow the local curriculum, or hold across curricula?

The core-versus-culture reading: a sparse core of dependencies holds whatever the curriculum; a large
layer of grouping and order is chosen locally, and learners learn what they are taught together. If
dependence between skills were purely curricular, skills taught close together locally would look
dependent and the pattern would not carry from one country's platform to another's. If a core exists,
the dependence between two skills on one platform should predict it on another, beyond how close the
two are taught locally. Written 2026-09-27; no statistic of this design has been computed.

Corpora (all through shared.corpus adapters and shared.paths.data_path; raw data stays outside the
repo): XES3G5M (China, third grade), ASSISTments 2012-13 (US, mostly middle school), Eedi (UK, lower
secondary), Junyi 2020 (Taiwan, grades 1-9).

Shared vocabulary: every unit (XES3G5M leaf KC, ASSISTments skill, Eedi level-3 subject, Junyi
exercise) is mapped by a language model, from its name alone, to one Common Core K-8 cluster
(grade.domain.cluster, e.g. 4.NF.B) or NONE. The allowed clusters are the 92 K-8 clusters in EDM Cup's
problem_details.csv, each shown with up to three of its standards' descriptions. MAPPER is primary;
MAPPER2 is a robustness check. The mapping reads names only, never responses; out/unit-map.json holds
unit id -> cluster only.

TIME: XES3G5M and ASSISTments give attempt start times; Eedi gives the LATEST answer per question
(the release keeps only it) at minute resolution; Junyi is on a 15-minute grid. Proximity is read in
days, where both limits are immaterial; order is descriptive only.

DIRECTION: symmetric -- dependence D is a partial correlation, unordered; the order share O is
descriptive and never verdict-bearing.

PRE-REGISTRATION
  Cells: (learner, cluster) with >= 3 attempts on units mapped to the cluster; accuracy = share correct;
  first time = earliest attempt.
  Per corpus, per unordered cluster pair (A, B) with >= 100 learners holding both cells:
    D  partial correlation of accuracy on A and on B, controlling the learner's accuracy on all other
       mapped clusters (learners with < 10 such attempts dropped).
    P  proximity = -log(1 + median over learners of |first time A - first time B| in days); the\n       median is read from a 200-bin histogram of log(1 + days).
    O  share of learners who met A first (ties dropped), descriptive.
  Cross-corpus: for each ordered pair of corpora (c, c') sharing >= 30 cluster pairs, standardise D_c,
  D_c' and P_c over the shared pairs and fit D_c ~ b_other D_c' + b_prox P_c (OLS). Pooled estimate:
  the mean of each coefficient over all qualifying ordered corpus pairs. Interval: 2,000 bootstraps,
  resampling shared cluster pairs within every corpus pair. Null for b_other: 2,000 permutations of
  D_c' across shared pairs.
  VERDICTS
    CORE: pooled b_other lower 95% bound > 0 and above the permutation null's 97.5th percentile.
    CULTURAL: pooled b_prox lower 95% bound > 0 and CORE not reached.
    CORE AND CULTURAL: both reached.  NEITHER: neither.
    UNANSWERABLE: no corpus pair shares >= 30 cluster pairs.
  Reported: per corpus pair b_other, b_prox, n shared; the same with MAPPER2's map; Spearman of D_c
  with D_c' separately on order-discordant pairs (one corpus meets A first for > 60% of learners, the
  other for < 40%) and concordant pairs; mapper agreement.
  WHAT IT CAN AND CANNOT SAY. It separates local-curriculum dependence from dependence that carries
  across four national curricula. It cannot separate a cognitive core from a mathematics-education
  culture the four countries share; order-discordant pairs are the closest it comes. Name-only mapping
  adds noise, which biases b_other toward zero.

SYNTHETIC FLOOR (--synthetic, no corpus, no model call): pair_stats must equal a direct residual
  correlation; cross() on four simulated corpora with 60 shared pairs, 20 worlds each of core+culture,
  culture only, core only and neither. FLOOR PASSES if the planted core is found in >= 36 of 40
  core worlds and falsely claimed in <= 4 of 40 core-free worlds. If it fails, the verdict is
  UNANSWERABLE. (Superseded by change 2 below.)

CHANGES (before any real data was read)
  1. The first synthetic run found the core in 39 of 40 core worlds but claimed it falsely in 3 of
     40, and claimed culture falsely in 6 of 20 core-only worlds; its floor also miscounted core
     worlds that were read CORE AND CULTURAL as misses. Cause: the pooled estimate averages
     regressions that share corpora, but the bootstrap and permutation treated them as independent,
     so intervals were too narrow. Now one bootstrap draw of cluster pairs from their union serves
     every corpus pair, and the null shuffles each corpus's D once per draw across every regression
     it enters. The floor counts a core found whenever the verdict contains CORE.
  2. The corrected test is calibrated (false core 0 of 40) but finds a planted core of 0.5 in 31 of
     40 worlds at 60 shared pairs, under the >= 36 first set. The floor is now calibration only
     (false core <= 4 of 40), with a power table at 60, 150 and 300 shared pairs for core effects of
     0.3 and 0.5 (10 worlds each). A NEITHER verdict is read as UNDERPOWERED when the median shared
     pair count across corpus pairs is below the smallest count with power >= 0.8 at effect 0.3.

BUDGET: its own ledger, out/invariance-spend.json, $10 cap.

    python3 invariance.py --synthetic
    python3 invariance.py map        # model calls: unit names -> CCSS clusters
    python3 invariance.py analyse    # after out/unit-map.json is committed
"""

from __future__ import annotations

import csv
import io
import json
import math
import os
import re
import subprocess
import sys
import threading
import zipfile
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("LLM_MIN_INTERVAL", "1.0")
from shared.paths import data_path, scratch_root  # noqa: E402
from shared.stats import spearman  # noqa: E402

OUT = HERE / "out"
MAP = OUT / "unit-map.json"
SPEND = OUT / "invariance-spend.json"
BUDGET = 10.0
SEED = 20260927
MAPPER = "openai/gpt-6-sol"
MAPPER2 = "deepseek/deepseek-v4-pro"
PRICES = {MAPPER: (2.0, 10.0), MAPPER2: (0.52, 1.041)}
MIN_CELL, MIN_LEARNERS, MIN_REST, MIN_SHARED = 3, 100, 10, 30
CORPORA = ["xes3g5m", "assistments2012", "eedi", "junyi2020"]
_LOCK = threading.Lock()

MAP_PROMPT = """You are aligning skill labels from mathematics learning platforms in different countries to the US Common Core State Standards (grades K-8).

COMMON CORE CLUSTERS (code | example standards in the cluster)
{clusters}

SKILL LABELS (id | label; labels may be Chinese, English or another language, and may be a path from general to specific)
{units}

For each skill label choose the ONE cluster above whose content it best matches. Use NONE if no cluster fits (for example competition-only puzzles, high-school content, or non-mathematical labels).
Reply with JSON only: {{"map": {{"<id>": "4.NF.B"}}}}"""


# ---------------------------------------------------------------- vocabulary

def clusters() -> dict[str, list[str]]:
    out = defaultdict(Counter)
    with open(data_path("EDMCUP_DIR") / "problem_details.csv", newline="") as f:
        for r in csv.DictReader(f):
            m = re.match(r"^(K|[1-8])\.([A-Z]+)\.([A-Z])", r.get("problem_skill_code") or "")
            if m:
                out[".".join(m.groups())][r.get("problem_skill_description") or ""] += 1
    return {k: [d for d, _ in v.most_common(3) if d] for k, v in sorted(out.items())}


def unit_names() -> dict[str, dict[str, str]]:
    names = {}
    xr = json.loads((data_path("XES_DIR") / "cid2route.json").read_text())
    names["xes3g5m"] = {"k%s" % k: " > ".join(v if isinstance(v, list) else v.split("----")) for k, v in xr.items()}
    sk = {}
    with open(data_path("ASSIST_DIR") / "assist_skill_names.csv", newline="") as f:
        for row in csv.reader(f):
            if len(row) >= 2 and row[0].strip():
                sk[row[0].strip()] = row[1].strip()
    names["assistments2012"] = sk
    z = zipfile.ZipFile(data_path("EEDI_ZIP"))
    meta = {r["SubjectId"]: r for r in csv.DictReader(io.TextIOWrapper(
        z.open("data/metadata/subject_metadata.csv"), encoding="utf-8-sig"))}

    def path(sid):
        p = []
        while sid in meta and meta[sid]["Level"] != "0":
            p.append(meta[sid]["Name"])
            sid = meta[sid]["ParentId"]
        return " > ".join(reversed(p))
    names["eedi"] = {"s%s" % s: path(s) for s, r in meta.items() if r["Level"] == "3"}
    with open(data_path("JUNYI2020_DIR") / "Info_Content.csv", encoding="utf-8-sig") as f:
        names["junyi2020"] = {r["ucid"]: r["content_pretty_name"] for r in csv.DictReader(f)}
    return names


def _ledger():
    return json.loads(SPEND.read_text()) if SPEND.exists() else {"budget_usd": BUDGET, "calls": []}


def call(model, prompt, what):
    from shared import llm
    led = _ledger()
    spent = sum(c["cost_usd"] for c in led["calls"])
    pin, pout = PRICES[model]
    if spent + (len(prompt) / 3 * pin + 16000 * pout) / 1e6 > BUDGET:
        raise SystemExit(f"BUDGET: ${spent:.2f} spent")
    meta = {}
    txt = llm.call(model, prompt, SEED, cache=scratch_root() / "core-vs-culture-cache", max_tokens=16000,
                   temperature=0.0, attempts=3, provider=False, meta=meta)
    if not meta.get("from_cache"):
        u = meta.get("usage") or {}
        cost = u.get("cost") if isinstance(u.get("cost"), (int, float)) else \
            (u.get("prompt_tokens", 0) * pin + u.get("completion_tokens", 0) * pout) / 1e6
        with _LOCK:
            led = _ledger()
            led["calls"].append({"what": what, "model": model, "cost_usd": cost, "served_model": meta.get("served_model"),
                                 "provider": meta.get("provider"), "timestamp_utc": meta.get("timestamp_utc")})
            OUT.mkdir(exist_ok=True)
            SPEND.write_text(json.dumps(led, indent=1) + "\n")
    return txt


def map_units() -> None:
    from shared import llm
    if not llm.load_key():
        raise SystemExit("no OPENROUTER_API_KEY")
    cl = clusters()
    block = "\n".join(f"{k} | {'; '.join(v)}" for k, v in cl.items())
    names = unit_names()
    result = {"clusters": sorted(cl), "maps": {}}
    for model in (MAPPER, MAPPER2):
        mp = {}
        jobs = []
        for corpus, nm in names.items():
            ids = sorted(nm)
            for s in range(0, len(ids), 40):
                jobs.append((corpus, ids[s:s + 40]))

        def one(job):
            corpus, ids = job
            units = "\n".join(f"u{i} | {names[corpus][x]}" for i, x in enumerate(ids))
            txt = call(model, MAP_PROMPT.format(clusters=block, units=units), f"map {corpus} {ids[0]}")
            s, e = txt.find("{"), txt.rfind("}")
            try:
                obj = json.loads(txt[s:e + 1])["map"]
            except (ValueError, KeyError, TypeError):
                return corpus, {}
            out = {}
            for k, v in obj.items():
                m = re.match(r"^u(\d+)$", str(k))
                if m and int(m.group(1)) < len(ids):
                    code = str(v).strip()
                    out[ids[int(m.group(1))]] = code if code in cl else "NONE"
            return corpus, out
        with ThreadPoolExecutor(8) as ex:
            for corpus, got in ex.map(one, jobs):
                mp.setdefault(corpus, {}).update(got)
        result["maps"][model] = mp
        cov = {c: (sum(v != "NONE" for v in m.values()), len(names[c])) for c, m in mp.items()}
        print(model, "mapped (non-NONE, total):", cov)
    OUT.mkdir(exist_ok=True)
    MAP.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    a, b = result["maps"][MAPPER], result["maps"][MAPPER2]
    agree = [a[c][u] == b.get(c, {}).get(u) for c in a for u in a[c] if u in b.get(c, {})]
    print(f"mapper agreement {np.mean(agree):.3f} over {len(agree)} units; spend "
          f"${sum(c['cost_usd'] for c in _ledger()['calls']):.2f}")


# ---------------------------------------------------------------- analysis

def to_seconds(t) -> float | None:
    if isinstance(t, (int, float)):
        return float(t) / 1000.0 if t > 1e11 else float(t)
    s = str(t).strip().replace(" UTC", "+00:00")
    try:
        d = datetime.fromisoformat(s)
    except ValueError:
        try:
            return float(s) / 1000.0 if float(s) > 1e11 else float(s)
        except ValueError:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.timestamp()


def cells(corpus: str, umap: dict[str, str]):
    from shared import corpus as C
    env = {"xes3g5m": ("XES_DIR",), "assistments2012": ("ASSIST_DIR",), "eedi": ("EEDI_ANSWERS", "EEDI_ZIP"),
           "junyi2020": ("JUNYI2020_DIR",)}[corpus]
    for v in env:
        os.environ.setdefault(v, str(data_path(v)))
    src = C.ADAPTERS[corpus]()
    agg = defaultdict(lambda: [0, 0.0, math.inf])
    for learner, unit, t, y in src.events():
        cl = umap.get(unit)
        if not cl or cl == "NONE":
            continue
        a = agg[(learner, cl)]
        a[0] += 1
        a[1] += y
        ts = to_seconds(t)
        if ts is not None and ts < a[2]:
            a[2] = ts
    by = defaultdict(dict)
    for (learner, cl), (n, s, t) in agg.items():
        by[learner][cl] = (n, s, t)
    return by


GAP_BINS = np.linspace(0.0, math.log1p(3650.0), 201)


def pair_stats(by) -> dict:
    """Exact partial correlations from running sums; the median gap from a 200-bin histogram of
    log(1 + days), so it is binned to 0.041 in log-days."""
    acc = {}
    for l, cs in by.items():
        N = sum(v[0] for v in cs.values())
        S = sum(v[1] for v in cs.values())
        ok = sorted(c for c, v in cs.items() if v[0] >= MIN_CELL)
        for i in range(len(ok)):
            for j in range(i + 1, len(ok)):
                a, b = ok[i], ok[j]
                na, sa, ta = cs[a]
                nb, sb, tb = cs[b]
                rest = N - na - nb
                if rest < MIN_REST:
                    continue
                xa, xb, z = sa / na, sb / nb, (S - sa - sb) / rest
                r = acc.get((a, b))
                if r is None:
                    r = acc[(a, b)] = {"m": np.zeros(10), "h": np.zeros(len(GAP_BINS) - 1), "first": 0, "later": 0}
                r["m"] += (1, xa, xb, z, xa * xa, xb * xb, z * z, xa * xb, xa * z, xb * z)
                if math.isfinite(ta) and math.isfinite(tb):
                    g = math.log1p(abs(ta - tb) / 86400.0)
                    r["h"][min(len(GAP_BINS) - 2, int(np.searchsorted(GAP_BINS, g, side="right")) - 1)] += 1
                    if ta < tb:
                        r["first"] += 1
                    elif tb < ta:
                        r["later"] += 1
    out = {}
    for (a, b), r in acc.items():
        n, sa, sb, sz, saa, sbb, szz, sab, saz, sbz = r["m"]
        if n < MIN_LEARNERS:
            continue
        caa, cbb, czz = saa - sa * sa / n, sbb - sb * sb / n, szz - sz * sz / n
        cab, caz, cbz = sab - sa * sb / n, saz - sa * sz / n, sbz - sb * sz / n
        if czz <= 0:
            continue
        pa, pb, pab = caa - caz * caz / czz, cbb - cbz * cbz / czz, cab - caz * cbz / czz
        if pa <= 0 or pb <= 0:
            continue
        h = r["h"]
        P = None
        if h.sum():
            k = int(np.searchsorted(np.cumsum(h), h.sum() / 2))
            P = -float((GAP_BINS[k] + GAP_BINS[k + 1]) / 2)
        tot = r["first"] + r["later"]
        out[f"{a}|{b}"] = {"n": int(n), "D": float(pab / math.sqrt(pa * pb)), "P": P,
                           "O": r["first"] / tot if tot else None}
    return out


def zs(v):
    v = np.asarray(v, float)
    sd = v.std()
    return (v - v.mean()) / sd if sd > 0 else v * 0


def cross(stats: dict, rng) -> dict:
    per = {}
    for c in stats:
        for c2 in stats:
            if c == c2:
                continue
            shared = sorted(k for k in stats[c] if k in stats[c2] and stats[c][k]["P"] is not None)
            if len(shared) < MIN_SHARED:
                continue
            per[f"{c}<-{c2}"] = shared
    if not per:
        return {"verdict": "UNANSWERABLE", "per_pair": {}}

    def fit(c, c2, keys, dmap=None):
        d = zs([stats[c][k]["D"] for k in keys])
        src = dmap[c2] if dmap is not None else {k: stats[c2][k]["D"] for k in keys}
        X = np.column_stack([np.ones(len(keys)), zs([src[k] for k in keys]), zs([stats[c][k]["P"] for k in keys])])
        beta = np.linalg.lstsq(X, d, rcond=None)[0]
        return beta[1], beta[2]
    point = {k: fit(*k.split("<-"), keys) for k, keys in per.items()}
    pooled = (float(np.mean([v[0] for v in point.values()])), float(np.mean([v[1] for v in point.values()])))
    # Regressions share corpora, so resampling and permutation are JOINT: one bootstrap draw of cluster
    # pairs from their union serves every corpus pair, and the null shuffles each corpus's D over its
    # own pairs once per draw, for every regression it enters.
    union = sorted(set().union(*per.values()))
    boot_o, boot_p, null = [], [], []
    for _ in range(2000):
        cnt = Counter(union[i] for i in rng.integers(0, len(union), len(union)))
        bo, bp = [], []
        for k, keys in per.items():
            c, c2 = k.split("<-")
            sample = [x for x in keys for _ in range(cnt.get(x, 0))]
            if len(sample) >= 3:
                o, p = fit(c, c2, sample)
                bo.append(o)
                bp.append(p)
        boot_o.append(np.mean(bo))
        boot_p.append(np.mean(bp))
        dmap = {}
        for c in stats:
            ks = list(stats[c])
            vals = [stats[c][x]["D"] for x in ks]
            dmap[c] = dict(zip(ks, rng.permutation(vals)))
        null.append(np.mean([fit(*k.split("<-"), keys, dmap=dmap)[0] for k, keys in per.items()]))
    lo_o, lo_p = float(np.percentile(boot_o, 2.5)), float(np.percentile(boot_p, 2.5))
    core = lo_o > 0 and pooled[0] > float(np.percentile(null, 97.5))
    cult = lo_p > 0
    verdict = ("CORE AND CULTURAL" if core and cult else "CORE" if core else
               "CULTURAL" if cult else "NEITHER")
    disc = {}
    for k, keys in per.items():
        c, c2 = k.split("<-")
        dk = [x for x in keys if stats[c][x]["O"] is not None and stats[c2][x]["O"] is not None and
              ((stats[c][x]["O"] > 0.6 and stats[c2][x]["O"] < 0.4) or (stats[c][x]["O"] < 0.4 and stats[c2][x]["O"] > 0.6))]
        ck = [x for x in keys if x not in dk]
        rho = lambda ks: spearman([stats[c][x]["D"] for x in ks], [stats[c2][x]["D"] for x in ks]) if len(ks) >= 10 else None
        disc[k] = {"discordant_n": len(dk), "discordant_rho": rho(dk), "concordant_n": len(ck), "concordant_rho": rho(ck)}
    return {"verdict": verdict, "pooled_b_other": pooled[0], "pooled_b_prox": pooled[1],
            "_boot_other": [float(x) for x in boot_o], "_boot_prox": [float(x) for x in boot_p],
            "b_other_ci": [lo_o, float(np.percentile(boot_o, 97.5))],
            "b_prox_ci": [lo_p, float(np.percentile(boot_p, 97.5))],
            "null_b_other_975": float(np.percentile(null, 97.5)),
            "per_pair": {k: {"n_shared": len(per[k]), "b_other": float(v[0]), "b_prox": float(v[1])} for k, v in point.items()},
            "order_discordance": disc}


def analyse() -> None:
    dirty = subprocess.run(["git", "status", "--porcelain", str(MAP)], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    if dirty or not MAP.exists():
        raise SystemExit("out/unit-map.json is missing or uncommitted")
    maps = json.loads(MAP.read_text())["maps"]
    res = {}
    for model in (MAPPER, MAPPER2):
        stats = {}
        for corpus in CORPORA:
            print(f"{model}: reading {corpus}")
            by = cells(corpus, maps[model].get(corpus, {}))
            stats[corpus] = pair_stats(by)
            print(f"   {len(by)} learners, {len(stats[corpus])} cluster pairs")
        res[model] = {"pairs_per_corpus": {c: len(s) for c, s in stats.items()},
                      "cross": cross(stats, np.random.default_rng(SEED))}
        if model == MAPPER:
            (OUT / "invariance-pairs.json").write_text(json.dumps(stats, indent=1) + "\n")
        print(model, json.dumps({k: v for k, v in res[model]["cross"].items() if k != "order_discordance"}, indent=1))
    res["verdict"] = res[MAPPER]["cross"]["verdict"]
    (OUT / "invariance-result.json").write_text(json.dumps(res, indent=1) + "\n")
    print("VERDICT:", res["verdict"])


def synthetic() -> None:
    """Floor: pair_stats against a direct residual correlation, and cross() on planted worlds."""
    rng = np.random.default_rng(SEED)
    by = {}
    for l in range(3000):
        g, s = rng.normal(), rng.normal()
        cs = {}
        for c, load in (("A", 1.0), ("B", 1.0), ("C", 0.0), ("D", 0.0), ("E", 0.0)):
            p = 1 / (1 + math.exp(-(g + load * s + rng.normal(0, 0.5))))
            n = 10
            cs[c] = (n, float(rng.binomial(n, p)), float(l + rng.integers(0, 50)) * 86400)
        by[str(l)] = cs
    st = pair_stats(by)
    xa, xb, z = [], [], []
    for cs in by.values():
        N = sum(v[0] for v in cs.values()); S = sum(v[1] for v in cs.values())
        xa.append(cs["A"][1] / cs["A"][0]); xb.append(cs["B"][1] / cs["B"][0])
        z.append((S - cs["A"][1] - cs["B"][1]) / (N - cs["A"][0] - cs["B"][0]))
    Z = np.column_stack([np.ones(len(z)), z])
    ra = np.array(xa) - Z @ np.linalg.lstsq(Z, np.array(xa), rcond=None)[0]
    rb = np.array(xb) - Z @ np.linalg.lstsq(Z, np.array(xb), rcond=None)[0]
    direct = float((ra * rb).sum() / np.sqrt((ra ** 2).sum() * (rb ** 2).sum()))
    print(f"partial r A|B: running sums {st['A|B']['D']:.6f}, direct {direct:.6f}; C|D {st['C|D']['D']:+.3f}")
    assert abs(st["A|B"]["D"] - direct) < 1e-9

    def world(core, culture, npairs=60):
        truth = rng.normal(size=npairs)
        stats = {}
        for c in ("c1", "c2", "c3", "c4"):
            P = rng.normal(size=npairs)
            D = core * truth + culture * P + rng.normal(size=npairs)
            stats[c] = {f"p{i}": {"n": 500, "D": float(D[i]), "P": float(P[i]), "O": 0.5} for i in range(npairs)}
        return stats
    tally = {}
    for name, core, culture in (("core+culture", 0.5, 0.5), ("culture only", 0.0, 0.5),
                                ("core only", 0.5, 0.0), ("neither", 0.0, 0.0)):
        vs = Counter(cross(world(core, culture), np.random.default_rng(rng.integers(1 << 30)))["verdict"] for _ in range(20))
        tally[name] = dict(vs)
        print(f"  {name:<14} {dict(vs)}")
    core_hits = sum(v for w in ("core+culture", "core only") for k, v in tally[w].items() if "CORE" in k)
    false_core = sum(v for w in ("culture only", "neither") for k, v in tally[w].items() if "CORE" in k)
    false_cult = sum(v for w in ("core only", "neither") for k, v in tally[w].items() if "CULTURAL" in k)
    print(f"  false culture {false_cult}/40 (reported)")
    passes = false_core <= 4
    print(f"FLOOR {'PASSES' if passes else 'FAILS'}: false core {false_core}/40 (calibration); "
          f"planted core found {core_hits}/40 at 60 pairs (power, reported)")
    power = {}
    for core in (0.3, 0.5):
        for npairs in (60, 150, 300):
            hits = sum("CORE" in cross(world(core, 0.5, npairs), np.random.default_rng(rng.integers(1 << 30)))["verdict"]
                       for _ in range(10))
            power[f"core {core}, {npairs} pairs"] = hits / 10
            print(f"  power core {core} at {npairs} shared pairs: {hits}/10")
    tally["power"] = power
    OUT.mkdir(exist_ok=True)
    (OUT / "invariance-synthetic.json").write_text(json.dumps({"partial_r_check": [st["A|B"]["D"], direct],
                                                               "worlds": tally, "passes": passes}, indent=1) + "\n")


if __name__ == "__main__":
    {"map": map_units, "analyse": analyse, "--synthetic": synthetic}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
