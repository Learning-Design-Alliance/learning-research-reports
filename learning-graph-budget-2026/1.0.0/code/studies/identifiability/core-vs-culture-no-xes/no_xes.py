"""PRE-REGISTERED: does the core-versus-culture result survive without XES3G5M?

WHY. invariance.py (studies/identifiability/core-vs-culture/) found CORE AND CULTURAL on four corpora:
pooled b_other +0.12488 [+0.09098, +0.15834], pooled b_prox +0.36290 [+0.32627, +0.40110], null 97.5th
for b_other +0.02232. Its unit of analysis is a Common Core K-8 cluster, assigned to every unit by a
language model from the unit's name (out/unit-map.json; openai/gpt-6-sol primary, deepseek/deepseek-v4-pro
second). The blind human check of that map (human_codes.py; coder human:david-porcaro, blind to both
models, 87 coded items) returned MAP VALIDATED narrowly: kappa 0.606 [0.493, 0.709] against the bar 0.60.
By corpus it was weakest on XES3G5M (0.464, 18 items). The coder said XES3G5M units often span several
standards, so they have no single right cluster. The two models agree with each other most there (0.825),
which is what correlated errors would also produce. The maintainer asked (2026-10-07) whether the
headline depends on the leg the map handles worst. Literature: research/readiness/learning-graph-budget-2026/
literature.md, strand 6: 6.18 Herman, Webb & Zuniga (2007) and Webb, Herman & Webb (2007) for what
human aligners reach (kappa 0.55-0.58 at 57 topics), and the synthesis row 15 (report against those
figures, do not move the bar); 6.13 Oliveri & von Davier (2014) and 6.14 Robitzsch & Ludtke (2023) for
the split being relative to the linking, of which the corpus set is one part. Written 2026-10-07.

WHAT HAS ALREADY BEEN SEEN, AND WHAT IS NEW. The brief required reading invariance-result.json before
this design. Each of its 12 per-corpus-pair OLS coefficients depends only on the two corpora in that
pair, so the six that do not involve XES3G5M are already printed there, and the reduced design's
pooled points are their means. That mean has not been computed here, but it is not blind. What is new
and not yet computed: the joint bootstrap interval and the permutation null over the reduced union of
cluster pairs (both change when XES3G5M leaves the union and the null), hence the verdict; the floor at
the reduced design; the second map's reduced run; the leave-one-corpus-out comparison; and the
human-confirmation shares. The shared-pair counts of the three remaining corpus pairs (760, 768, 1,134)
are also already printed.

CONSTRUCT. Unchanged: the primary map (gpt-6-sol) is the verdict-bearing map, coded by a model from
names, with human agreement kappa 0.606 overall (ASSISTments 0.620, Eedi 0.668, Junyi 0.525) against one
blind human coder. A second human coder (the human-human ceiling) has not been run.

DATA. This script reads no corpus. It reads committed aggregates only:
  - ../core-vs-culture/out/invariance-pairs.json: per corpus, per cluster pair, n, D, P, O under the
    primary map. core-vs-culture-linking (linking.py, check R0) recomputed these from the raw corpora
    (ASSISTments 2012-13, Eedi NeurIPS 2020, Junyi 2020 streamed from its zip, XES3G5M) and matched them
    (same pairs, same n and P, D within 8.4e-14). Pair statistics are computed per corpus, so removing
    XES3G5M changes no other corpus's statistics; re-reading the raw data would reproduce the same
    numbers at the cost of a multi-hour stream on a shared machine. That is the reuse of linking's
    reproduction the brief asks for: its check is what licenses using the committed file.
  - ../core-vs-culture-linking/out/linking-pairs.json, key "deepseek/deepseek-v4-pro | cluster": the
    same statistics under the second map (descriptive only).
  - ../core-vs-culture/out/unit-map.json, human-codes.json: unit -> cluster, and the human's 87 codes
    (corpus, unit id, code; no names).
Imported, not modified: invariance.py (cross, CORPORA, SEED, MAPPER, MAPPER2, MIN_SHARED) and linking.py
(cross_multi, which consumes the random stream as invariance.cross does and was shown equal to it; used
for the floor's faster draws and for the ratio interval).

PRE-REGISTRATION

(1) PRIMARY. Corpora: ASSISTments 2012-13, Eedi, Junyi 2020 (XES3G5M removed). Same pair statistics,
  same rule for a qualifying ordered corpus pair (>= 30 shared cluster pairs), same OLS on standardized
  D_c, D_c', P_c, pooled by the mean over qualifying ordered pairs (6 here, 12 before). Same scheme as
  invariance.py CHANGE 1: 2,000 joint bootstraps (one draw of cluster pairs from the union of the
  reduced design's shared pairs serves every corpus pair) and 2,000 joint permutations (each corpus's D
  shuffled once per draw over all its own pairs, for every regression it enters), seed invariance.SEED.
  Run by calling invariance.cross itself on the three corpora.
  Same verdict strings and thresholds (signed, never on abs()):
    CORE: pooled b_other lower 95% bound > 0 and pooled b_other > the null's 97.5th percentile.
    CULTURAL: pooled b_prox lower 95% bound > 0 and CORE not reached.
    CORE AND CULTURAL: both.  NEITHER: neither.  UNANSWERABLE: no ordered pair shares >= 30.
    NEITHER reads "NEITHER (UNDERPOWERED)" under rule (3).
    If the floor below fails, the verdict is UNANSWERABLE (the read it would have been is recorded).
  WHAT EACH OUTCOME MEANS FOR PAPER II (fixed now):
    CORE AND CULTURAL: the headline does not depend on the leg the map handles worst. The paper states
      the four-corpus result as before and adds that it holds without XES3G5M, with this run's numbers.
    CULTURAL (core lost): the core rested on XES3G5M, the corpus the human check supports least, and
      the paper says so: F6's "partly carries across curricula" is stated as dependent on XES3G5M and
      cannot be a headline; the local layer stands.
    CORE (local layer lost): the local layer rested on XES3G5M and the paper says so; the core stands.
    NEITHER: both parts rested on XES3G5M; the core-and-culture split is not a headline. If it reads
      NEITHER (UNDERPOWERED), the paper says the three-corpus design cannot answer, not that the
      effect is absent.
    UNANSWERABLE: the question cannot be answered without XES3G5M; the paper says so.
  Reported beside the verdict (descriptive): per ordered pair b_other, b_prox, n shared; the ratio
  R = b_other / b_prox with its interval on the same draws (linking.cross_multi); the order-discordance
  Spearmans; the change from the four-corpus estimate (unpaired: the unions differ, so no paired
  interval is claimed).

(2) SECONDARY (descriptive; cannot be a verdict). Only the 87 coded sample units have human codes, too
  few to re-run invariance on human-confirmed units. A cluster is CONFIRMED if at least one coded unit,
  in any corpus, has a human code equal to its primary-map code and that code is not NONE; it is
  CONFIRMED-IN-CORPUS for corpus c if such a unit is from c. For each corpus, over its shared cluster
  pairs (the union of the keys of every qualifying regression with c as the dependent corpus; reduced
  design for ASSISTments, Eedi and Junyi; the four-corpus design for XES3G5M, for reference), report:
  the share of pairs with both clusters confirmed, with at least one confirmed, and the same for
  confirmed-in-corpus; and how many of the distinct clusters in those pairs are confirmed. No
  re-weighting, no threshold, no verdict. A cluster no human confirmed is unchecked, not wrong: the
  sample is 25 units a corpus, drawn uniformly over units, so most clusters were never shown.

(3) DESIGN SIZE AND POWER. Report the qualifying ordered corpus pairs and the shared-pair count of each,
  their median, and the union size, for the reduced design. The power table is re-run at three corpora
  (invariance.py CHANGE 2's grid: 60, 150 and 300 shared pairs; core effects 0.3 and 0.5; culture 0.5;
  20 worlds per cell rather than CHANGE 2's 10, for a less noisy table). The smallest grid count with
  power >= 0.8 at effect 0.3 is the bar; if no grid count reaches 0.8, the bar is "none" and any NEITHER
  reads UNDERPOWERED. NEITHER reads "NEITHER (UNDERPOWERED)" when the median shared-pair count is below
  the bar (invariance.py CHANGE 2). Also reported: power at effect 0.3 in worlds built on the reduced
  design's real key structure, and the bar from the committed four-corpus table (300) for comparison.
  A lost CORE (verdict CULTURAL) is not relabelled by this rule; its power is stated beside it.

FLOOR (--synthetic; no corpus values. It reads only which cluster-pair keys each corpus holds and
  whether P is defined for each, from invariance-pairs.json, so the synthetic worlds have the reduced
  design's exact pair overlap; no D, P or n value is read.)
  F0: linking.cross_multi with OLS equals invariance.cross on one synthetic three-corpus world (point
      exactly, intervals and null to 1e-9), so the faster floor instrument is the verdict instrument.
  F1 CALIBRATION (governs): worlds on the real key structure of the three corpora: truth ~ N(0,1) per
      cluster pair in the union, per corpus P ~ N(0,1), D = core * truth + culture * P + N(0,1); P left
      undefined where the real P is undefined. 20 worlds each of core+culture (0.5, 0.5), culture only
      (0, 0.5), core only (0.5, 0) and neither. FLOOR PASSES if a core is claimed (verdict contains
      CORE) in <= 4 of the 40 core-free worlds (invariance.py CHANGE 2's bar). Planted-core hits and
      false culture are reported.
  F2 POWER: the table under (3), on generic three-corpus worlds with every pair shared (invariance.py's
      world() with three corpora), plus 20 real-structure worlds at core 0.3, culture 0.5.
  Floor draws: 500 bootstrap and permutation draws per world (not 2,000), because the floor runs about
  200 worlds; linking.py made the same choice. The real run uses 2,000.

DESCRIPTIVE (not verdict-bearing): the same reduced run under the second map; leave-one-corpus-out
  for each of the four corpora under the primary map (is dropping XES3G5M different from dropping any
  corpus?), each with its verdict string and median shared count.

WHAT IT CAN AND CANNOT SAY. It says whether the four-corpus verdict needs XES3G5M, the corpus whose
units the human check supports least. It cannot say the remaining three corpora are mapped correctly
(their kappas are 0.53-0.67 against one human coder, and Junyi's is also below the bar); it cannot
separate a cognitive core from a shared mathematics-education culture (invariance.py's limit); and with
three corpora the pooled estimate rests on three corpus pairs, so one corpus can carry more weight.

RUN RECORD (2026-10-07, after the design commit 9cc4075; no design change, nothing tuned). The floor
ran first and passed (F0 true; false core 1/40); the power bar came out at 300 shared pairs. Then
`analyse` ran once. Results: README.md and out/no-xes-result.json.

    python3 no_xes.py --synthetic   # floor -> out/no-xes-synthetic.json
    python3 no_xes.py analyse       # needs the floor; -> out/no-xes-result.json
"""

from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies" / "identifiability" / "core-vs-culture"))
sys.path.insert(0, str(ROOT / "studies" / "identifiability" / "core-vs-culture-linking"))
import invariance as inv  # noqa: E402
import linking  # noqa: E402

OUT = HERE / "out"
INV_OUT = ROOT / "studies" / "identifiability" / "core-vs-culture" / "out"
LINK_OUT = ROOT / "studies" / "identifiability" / "core-vs-culture-linking" / "out"
REDUCED = ["assistments2012", "eedi", "junyi2020"]
DROPPED = "xes3g5m"
FLOOR_DRAWS = 500
FLOOR_WORLDS = 20
GRID = (60, 150, 300)
COMMITTED_BAR_4CORPORA = 300   # invariance-synthetic.json: power 0.9 at 300, 0.6 at 150 (effect 0.3)


def strip(d):
    if isinstance(d, dict):
        return {k: strip(v) for k, v in d.items() if not k.startswith("_")}
    return d


def primary_stats():
    return json.loads((INV_OUT / "invariance-pairs.json").read_text())


def second_stats():
    return json.loads((LINK_OUT / "linking-pairs.json").read_text())[f"{inv.MAPPER2} | cluster"]


def design(stats, corpora):
    per = linking._regressions({c: stats[c] for c in corpora})
    counts = {k: len(v) for k, v in per.items()}
    return {"ordered_pairs": len(per), "n_shared": counts,
            "median_shared": float(np.median(list(counts.values()))) if counts else None,
            "union": len(set().union(*per.values())) if per else 0}, per


# ---------------------------------------------------------------- floor

def key_structure():
    """Which cluster-pair keys each reduced corpus holds, and whether P is defined. No values."""
    st = primary_stats()
    return {c: {k: (v["P"] is not None) for k, v in st[c].items()} for c in REDUCED}


def real_world(rng, ks, core, culture):
    union = sorted(set().union(*[set(v) for v in ks.values()]))
    truth = dict(zip(union, rng.normal(size=len(union))))
    stats = {}
    for c, keys in ks.items():
        names = sorted(keys)
        P = rng.normal(size=len(names))
        e = rng.normal(size=len(names))
        stats[c] = {k: {"n": 500, "D": float(core * truth[k] + culture * P[i] + e[i]),
                        "P": float(P[i]) if keys[k] else None, "O": 0.5} for i, k in enumerate(names)}
    return stats


def generic_world(rng, core, culture, npairs, ncorp=3):
    truth = rng.normal(size=npairs)
    stats = {}
    for j in range(ncorp):
        P = rng.normal(size=npairs)
        D = core * truth + culture * P + rng.normal(size=npairs)
        stats[f"c{j}"] = {f"p{i}": {"n": 500, "D": float(D[i]), "P": float(P[i]), "O": 0.5} for i in range(npairs)}
    return stats


def run(stats, rng, draws=FLOOR_DRAWS):
    return linking.cross_multi(stats, rng, ests=("ols",), draws=draws)["estimators"]["ols"]["verdict"]


def synthetic():
    rng = np.random.default_rng(inv.SEED + 31)
    out = {"draws_per_world": FLOOR_DRAWS, "worlds_per_cell": FLOOR_WORLDS}
    t0 = time.time()
    # F0: the faster instrument is the verdict instrument (2,000 draws each, as invariance.cross is fixed).
    w = generic_world(rng, 0.3, 0.5, 80)
    a = inv.cross(w, np.random.default_rng(11))
    b = linking.cross_multi(w, np.random.default_rng(11), ests=("ols",))["estimators"]["ols"]
    f0 = (abs(a["pooled_b_other"] - b["pooled_b_other"]) < 1e-12 and
          max(abs(x - y) for x, y in zip(a["b_other_ci"] + a["b_prox_ci"], b["b_other_ci"] + b["b_prox_ci"])) < 1e-9
          and abs(a["null_b_other_975"] - b["null_b_other_975"]) < 1e-9 and a["verdict"] == b["verdict"])
    out["F0_cross_multi_equals_invariance_cross"] = bool(f0)
    print("F0:", f0, f"({time.time() - t0:.0f}s)", flush=True)
    # F1: calibration on the reduced design's real key structure.
    ks = key_structure()
    dsg, _ = design({c: {k: {"P": (0.0 if v else None)} for k, v in ks[c].items()} for c in REDUCED}, REDUCED)
    out["structure"] = dsg
    tally = {}
    for name, core, culture in (("core+culture", 0.5, 0.5), ("culture only", 0.0, 0.5),
                                ("core only", 0.5, 0.0), ("neither", 0.0, 0.0)):
        vs = Counter(run(real_world(rng, ks, core, culture), np.random.default_rng(rng.integers(1 << 30)))
                     for _ in range(FLOOR_WORLDS))
        tally[name] = dict(vs)
        print(f"  F1 {name:<14} {dict(vs)} ({time.time() - t0:.0f}s)", flush=True)
    false_core = sum(v for w_ in ("culture only", "neither") for k, v in tally[w_].items() if "CORE" in k)
    hits = sum(v for w_ in ("core+culture", "core only") for k, v in tally[w_].items() if "CORE" in k)
    false_cult = sum(v for w_ in ("core only", "neither") for k, v in tally[w_].items() if "CULTURAL" in k)
    out["F1"] = {"worlds": tally, "false_core_of_40": false_core, "core_found_of_40": hits,
                 "false_culture_of_40": false_cult, "passes": false_core <= 4}
    print(f"F1 {'PASSES' if false_core <= 4 else 'FAILS'}: false core {false_core}/40; core found {hits}/40; "
          f"false culture {false_cult}/40", flush=True)
    # F2: power.
    power = {}
    for core in (0.3, 0.5):
        for npairs in GRID:
            h = sum("CORE" in run(generic_world(rng, core, 0.5, npairs), np.random.default_rng(rng.integers(1 << 30)))
                    for _ in range(FLOOR_WORLDS))
            power[f"core {core}, {npairs} pairs"] = h / FLOOR_WORLDS
            print(f"  F2 power core {core} at {npairs} pairs (3 corpora): {h}/{FLOOR_WORLDS} ({time.time() - t0:.0f}s)", flush=True)
    h = sum("CORE" in run(real_world(rng, ks, 0.3, 0.5), np.random.default_rng(rng.integers(1 << 30)))
            for _ in range(FLOOR_WORLDS))
    power["core 0.3, real key structure"] = h / FLOOR_WORLDS
    print(f"  F2 power core 0.3 on the real key structure: {h}/{FLOOR_WORLDS}", flush=True)
    bar = next((n for n in GRID if power[f"core 0.3, {n} pairs"] >= 0.8), None)
    out["F2"] = {"power": power, "bar_smallest_count_power_ge_0.8_at_0.3": bar,
                 "committed_bar_4_corpora": COMMITTED_BAR_4CORPORA}
    out["passes"] = bool(f0 and out["F1"]["passes"])
    OUT.mkdir(exist_ok=True)
    (OUT / "no-xes-synthetic.json").write_text(json.dumps(out, indent=1) + "\n")
    print("FLOOR:", "PASSES" if out["passes"] else "FAILS", f"({time.time() - t0:.0f}s)")


# ---------------------------------------------------------------- real run

def confirmation(stats_full):
    umap = json.loads((INV_OUT / "unit-map.json").read_text())["maps"][inv.MAPPER]
    codes = json.loads((INV_OUT / "human-codes.json").read_text())
    coded = [r for r in codes["codes"] if r.get("code")]
    agree = [r for r in coded if r["code"] == umap.get(r["corpus"], {}).get(r["unit"]) and r["code"] != "NONE"]
    conf_any = {r["code"] for r in agree}
    conf_in = {c: {r["code"] for r in agree if r["corpus"] == c} for c in inv.CORPORA}
    out = {"coder": codes["coder"], "coded_items": len(coded), "agreeing_non_none_items": len(agree),
           "agreeing_by_corpus": dict(Counter(r["corpus"] for r in agree)),
           "confirmed_clusters_any_corpus": len(conf_any),
           "confirmed_clusters_in_corpus": {c: len(v) for c, v in conf_in.items()}, "per_corpus": {}}
    for c in inv.CORPORA:
        corp = REDUCED if c in REDUCED else inv.CORPORA
        _, per = design(stats_full, corp)
        keys = sorted(set().union(*[set(v) for k, v in per.items() if k.startswith(c + "<-")]))
        pairs = [k.split("|") for k in keys]
        cl = sorted({x for p in pairs for x in p})

        def share(cset, rule):
            return float(np.mean([rule(a in cset, b in cset) for a, b in pairs])) if pairs else None
        out["per_corpus"][c] = {
            "design": "reduced (3 corpora)" if c in REDUCED else "four-corpus (reference)",
            "shared_cluster_pairs": len(pairs), "distinct_clusters": len(cl),
            "clusters_confirmed_any": sum(x in conf_any for x in cl),
            "clusters_confirmed_in_corpus": sum(x in conf_in[c] for x in cl),
            "share_pairs_both_confirmed_any": share(conf_any, lambda a, b: a and b),
            "share_pairs_at_least_one_confirmed_any": share(conf_any, lambda a, b: a or b),
            "share_pairs_both_confirmed_in_corpus": share(conf_in[c], lambda a, b: a and b),
            "share_pairs_at_least_one_confirmed_in_corpus": share(conf_in[c], lambda a, b: a or b)}
    return out


def underpowered(verdict, median, bar):
    if verdict == "NEITHER" and (bar is None or median < bar):
        return "NEITHER (UNDERPOWERED)"
    return verdict


def analyse():
    fpath = OUT / "no-xes-synthetic.json"
    if not fpath.exists():
        raise SystemExit("run --synthetic first: the floor governs the verdict")
    floor = json.loads(fpath.read_text())
    bar = floor["F2"]["bar_smallest_count_power_ge_0.8_at_0.3"]
    st = primary_stats()
    committed = json.loads((INV_OUT / "invariance-result.json").read_text())[inv.MAPPER]["cross"]
    res = {"floor_passes": floor["passes"], "power_bar": bar, "corpora": REDUCED, "dropped": DROPPED}

    # (1) primary, with invariance.cross itself.
    dsg, _ = design(st, REDUCED)
    res["design"] = dsg
    t0 = time.time()
    cr = inv.cross({c: st[c] for c in REDUCED}, np.random.default_rng(inv.SEED))
    print(f"invariance.cross on three corpora ({time.time() - t0:.0f}s)", flush=True)
    cm = linking.cross_multi({c: st[c] for c in REDUCED}, np.random.default_rng(inv.SEED), ests=("ols",))["estimators"]["ols"]
    same = (abs(cr["pooled_b_other"] - cm["pooled_b_other"]) < 1e-12 and
            abs(cr["b_other_ci"][0] - cm["b_other_ci"][0]) < 1e-9 and abs(cr["null_b_other_975"] - cm["null_b_other_975"]) < 1e-9)
    v = underpowered(cr["verdict"], dsg["median_shared"], bar)
    read = v
    if not floor["passes"]:
        v = f"UNANSWERABLE (floor failed; read would have been: {read})"
    res["primary"] = {**strip(cr), "verdict_rule_output": cr["verdict"], "verdict": v,
                      "ratio": cm["ratio"], "ratio_ci": cm["ratio_ci"], "cross_multi_agrees": bool(same)}
    res["four_corpus_committed"] = {k: committed[k] for k in ("verdict", "pooled_b_other", "b_other_ci", "pooled_b_prox",
                                                              "b_prox_ci", "null_b_other_975")}
    res["change_from_four_corpus_unpaired"] = {"b_other": cr["pooled_b_other"] - committed["pooled_b_other"],
                                               "b_prox": cr["pooled_b_prox"] - committed["pooled_b_prox"]}
    print("PRIMARY:", v, json.dumps({k: res["primary"][k] for k in ("pooled_b_other", "b_other_ci", "pooled_b_prox",
                                                                     "b_prox_ci", "null_b_other_975", "ratio", "ratio_ci")}), flush=True)

    # (3) power reading.
    cult_lost_core = cr["verdict"] == "CULTURAL"
    res["power"] = {"median_shared": dsg["median_shared"], "bar_3_corpora": bar,
                    "bar_4_corpora_committed": COMMITTED_BAR_4CORPORA,
                    "powered": bool(bar is not None and dsg["median_shared"] >= bar),
                    "power_table_3_corpora": floor["F2"]["power"],
                    "note": ("CORE not reached; power at effect 0.3 on the real key structure is "
                             f"{floor['F2']['power']['core 0.3, real key structure']}") if cult_lost_core else None}

    # (2) secondary.
    res["human_confirmation"] = confirmation(st)

    # descriptive: second map, leave-one-corpus-out.
    st2 = second_stats()
    d2, _ = design(st2, REDUCED)
    c2 = linking.cross_multi({c: st2[c] for c in REDUCED}, np.random.default_rng(inv.SEED), ests=("ols",))["estimators"]["ols"]
    res["second_map_reduced"] = {"design": d2, **{k: c2[k] for k in ("verdict", "pooled_b_other", "b_other_ci", "pooled_b_prox",
                                                                    "b_prox_ci", "null_b_other_975", "ratio", "ratio_ci", "per_pair")}}
    loo = {}
    for drop in inv.CORPORA:
        keep = [c for c in inv.CORPORA if c != drop]
        dd, _ = design(st, keep)
        r = linking.cross_multi({c: st[c] for c in keep}, np.random.default_rng(inv.SEED), ests=("ols",))["estimators"]["ols"]
        loo[f"without {drop}"] = {"median_shared": dd["median_shared"], "ordered_pairs": dd["ordered_pairs"],
                                  **{k: r[k] for k in ("verdict", "pooled_b_other", "b_other_ci", "pooled_b_prox",
                                                       "b_prox_ci", "null_b_other_975", "ratio", "ratio_ci")}}
        print(f"  LOO without {drop}: {r['verdict']} b_other {r['pooled_b_other']:+.4f} {r['b_other_ci']}", flush=True)
    res["leave_one_corpus_out"] = loo
    res["map_status"] = ("model-coded from names (openai/gpt-6-sol primary); blind human check MAP VALIDATED "
                         "narrowly, kappa 0.606 [0.493, 0.709], 87 items, coder human:david-porcaro")
    OUT.mkdir(exist_ok=True)
    (OUT / "no-xes-result.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
    print("VERDICT:", v)


if __name__ == "__main__":
    {"--synthetic": synthetic, "analyse": analyse}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
