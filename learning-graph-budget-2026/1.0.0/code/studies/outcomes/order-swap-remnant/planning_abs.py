"""Planning values for a randomized edge-release trial at the effect the positivity atlas tests for.

Derived, not a new analysis: reads two committed outputs and applies their own formulas at a second
effect size. No corpus is read and nothing is fitted.

Why it exists. `remnant.py` sizes a trial for differences of 0.05, 0.10 and 0.30 standard deviations
(`out/power.json`, `sample_sizes`). Paper II's Table 16 also needs the effect the atlas tests for, an
absolute drop of 0.10 in first-attempt accuracy, which `power.json` converts to standard deviations at
accuracies 0.5 to 0.8 (`lt_trials_comparison.abs_0.10_in_sd_at_p`: 0.202 to 0.232 SD). This script
evaluates the same expressions at those two ends:

  per learner      n = ceil(2 Z^2 / d^2 * eta_W)                         (remnant.py)
  per class        J = ceil(2 Z^2 / d^2 * [rho eta_B + (1 - rho) eta_W / m]) (remnant.py; lt-trials/icc.py)
  per encounter    E = ceil(4 Z^2 / d^2 * (1 - rho_learner)), a total over both arms; learners = ceil(E / K)

with Z, the intraclass correlations, eta_W (the remnant covariate's variance ratio) and the
length-trial rho read from `out/power.json` and `studies/outcomes/lt-trials/out/icc-power.json`.

Control. Before writing, it recomputes every 0.10 SD value it reports from the same expressions and
asserts equality with the stored one, so the second column cannot drift from the first by a different
formula. The 0.10 SD and absolute-0.10 columns differ only in d.

Output: `out/planning-abs.json`. Run: python3 studies/outcomes/order-swap-remnant/planning_abs.py
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
pw = json.loads((HERE / "out/power.json").read_text())
ip = json.loads((ROOT / "studies/outcomes/lt-trials/out/icc-power.json").read_text())
Z = pw["Z"]
assert abs(Z - ip["Z"]) < 1e-12
eta_ptm = None
remnant = json.loads((HERE / "out/remnant-result.json").read_text())
eta_ptm = remnant["problems_to_mastery"]["pairs"]["T1-T3"]["variance_ratio"]
rho_cls = pw["icc"]["problems_to_mastery_class"]["icc"]
rho_l = pw["icc"]["encounter_correct_learner"]["icc"]
rho_lt = ip["rho_used"]["length_trial_icc_point"]


def rows(d):
    base = 2 * Z ** 2 / d ** 2
    ne = 4 * Z ** 2 / d ** 2 * (1 - rho_l)
    return {
        "learner_n_per_arm": math.ceil(base),
        "learner_with_remnant_n_per_arm": math.ceil(base * eta_ptm),
        "class_m13_icc_experiment": math.ceil(base * (rho_cls + (1 - rho_cls) / 13)),
        "class_m20_icc_experiment": math.ceil(base * (rho_cls + (1 - rho_cls) / 20)),
        "class_m13_icc_length_trial": math.ceil(base * (rho_lt + (1 - rho_lt) / 13)),
        "encounters_total": math.ceil(ne),
        "encounter_learners_K5": math.ceil(ne / 5),
    }


ref = rows(0.10)
s = pw["sample_sizes"]["0.1"]
stored = {
    "learner_n_per_arm": s["per_learner_n_per_arm"]["none"],
    "learner_with_remnant_n_per_arm": s["per_learner_n_per_arm"]["remnant_ptm"],
    "class_m13_icc_experiment": s["per_class"]["this_experiment_ptm_rho"]["m=13"]["classes_per_arm"],
    "class_m20_icc_experiment": s["per_class"]["this_experiment_ptm_rho"]["m=20"]["classes_per_arm"],
    "class_m13_icc_length_trial": ip["classes_per_arm"]["0.1"]["length_trial_icc_point"]["m=13"],
    "encounters_total": s["per_encounter"]["total_encounters"],
    "encounter_learners_K5": s["per_encounter"]["learners_K=5"],
}
assert ref == stored, (ref, stored)

conv = pw["lt_trials_comparison"]["abs_0.10_in_sd_at_p"]
d_lo, d_hi = conv["0.5"], conv["0.8"]   # 0.202 SD at accuracy 0.5, 0.232 SD at 0.8
out = {
    "source": ["out/power.json", "out/remnant-result.json", "studies/outcomes/lt-trials/out/icc-power.json"],
    "check_0.10_sd_reproduces_stored": True,
    "sd_0.10": ref,
    "abs_0.10": {"d_sd_at_accuracy_0.5": d_lo, "d_sd_at_accuracy_0.8": d_hi,
                 "at_accuracy_0.5": rows(d_lo), "at_accuracy_0.8": rows(d_hi)},
    "note": "encounters_total and encounter_learners_K5 are totals over both arms; the rest are per arm",
}
(HERE / "out/planning-abs.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out["abs_0.10"], indent=1))
