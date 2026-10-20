"""
Does following a learning trajectory's ORDER cause more learning than the same activities reversed?

The first randomised manipulation of instructional SEQUENCE on this board. Every C2 anchor so far
randomises some other intervention (interleaving, hints, practice schedules); this one holds the
activities and the dose fixed and reverses only their order, which is the causal question the
observational assay can only approach sideways.

Sarama, Clements, Baroody, Kutaka, Chernyavskiy, Shi & Cong (AERA Open), ICPSR 151741. 187
kindergartners in 16 classrooms, randomised within class to LT (trajectory order, n = 71), REV (the
same ten 12-minute activities in reverse order, n = 59) or BAU (n = 57). Outcome is a Rasch posttest
theta on a 26-item length assessment whose items are tagged to the trajectory's seven levels.

    python3 length_order.py --data <C6 Analysis File.xlsx>

FLOOR: reproduce the authors' own model (their C6 Analysis Syntax.R, Table 9, frequentist lme4
arm): Theta_post ~ Condition + scale(PreTheta) + Gender + Private + (1|Class). Nothing downstream
is read until that matches the abstract's direction and significance.

ROBUSTNESS, because the LT arm's posttest SD is 1.24 against 0.72-0.75 in the others:
    class fixed effects        the contrast inside classrooms only
    within-class permutation   re-randomises arm labels INSIDE each class, the unit and the way the
                               design randomised -- the inference the design licenses
    class-cluster bootstrap    classes resampled whole
    median regression, ranks   the contrast without the tail's leverage
    drop the top 5%            how much of the effect sits in a handful of children

PRIVACY: the analysis file this reads carries no race, language or admin columns. Gender is kept
only because the authors' model conditions on it.

Terms: AERA/ICPSR open data -- statistical analysis only, no re-identification. The data stay in the
scratchpad; out/length_order.json holds aggregates.
"""
from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd
import statsmodels.formula.api as smf

warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent
SEED = 20260924
DRAWS = 2000


def load(path: Path) -> pd.DataFrame:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = list(wb["Analysis File"].iter_rows(values_only=True))
    hdr = [str(h).strip() if h else f"c{i}" for i, h in enumerate(rows[0])]
    d = pd.DataFrame(rows[1:], columns=hdr).dropna(subset=["Student ID Number"])
    for c in ("PreTheta_1pl", "Theta_post_1pl"):
        d[c] = d[c].astype(float)
    d["Private"] = d["Private"].astype(int)
    return d


def authors_model(d: pd.DataFrame, ref: str) -> dict:
    d = d.dropna(subset=["Theta_post_1pl", "PreTheta_1pl", "Gender"]).copy()
    d["pre"] = (d.PreTheta_1pl - d.PreTheta_1pl.mean()) / d.PreTheta_1pl.std()
    m = smf.mixedlm(f"Theta_post_1pl ~ C(Condition, Treatment('{ref}')) + pre + Gender + C(Private)",
                    d, groups="Class").fit(reml=True)
    ci = m.conf_int()
    return {k.split("[T.")[1].rstrip("]"): {"coef": float(m.params[k]), "lo": float(ci.loc[k, 0]),
                                           "hi": float(ci.loc[k, 1])}
            for k in m.params.index if "Condition" in k}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="C6 Analysis File.xlsx from ICPSR 151741")
    a = ap.parse_args()
    D = load(Path(a.data))
    print(f"{len(D)} children, arms {D.Condition.value_counts().to_dict()}, {D.Class.nunique()} classes\n")

    out = {"n": len(D), "arms": D.Condition.value_counts().to_dict(),
           "post_sd_by_arm": D.groupby("Condition").Theta_post_1pl.std().round(3).to_dict()}
    out["authors_model"] = {"vs_BAU": authors_model(D, "BAU"), "vs_REV": authors_model(D, "REV")}
    lt_rev = out["authors_model"]["vs_REV"]["LT"]
    print("FLOOR -- the authors' model reproduced (posttest theta, logits)")
    for ref, cs in out["authors_model"].items():
        for arm, v in cs.items():
            print(f"   {arm:>3} {ref.replace('vs_', '- '):6s} {v['coef']:+.3f}  [{v['lo']:+.3f}, {v['hi']:+.3f}]")

    L = D[D.Condition.isin(["LT", "REV"])].dropna(subset=["Theta_post_1pl", "PreTheta_1pl"]).copy()
    L["arm"] = (L.Condition == "LT").astype(int)
    fit = lambda d: smf.ols("Theta_post_1pl ~ arm + PreTheta_1pl + C(Class)", d).fit().params["arm"]  # noqa: E731
    est = fit(L)
    rng = np.random.default_rng(SEED)
    perm = []
    for _ in range(DRAWS):
        d = L.copy()
        d["arm"] = d.groupby("Class")["arm"].transform(lambda s: rng.permutation(s.values))
        perm.append(fit(d))
    p_perm = float((np.abs(perm) >= abs(est)).mean())
    classes, bs = sorted(L.Class.unique()), []
    for _ in range(DRAWS):
        pick = rng.choice(classes, len(classes), replace=True)
        d = pd.concat([L[L.Class == c].assign(Class=f"{c}_{i}") for i, c in enumerate(pick)])
        if d.arm.nunique() == 2:
            bs.append(fit(d))
    L["rk"] = L.Theta_post_1pl.rank() / len(L)
    q = smf.quantreg("Theta_post_1pl ~ arm + PreTheta_1pl", L).fit(q=0.5)
    top = L.Theta_post_1pl.quantile(0.95)
    hi = L[L.Theta_post_1pl >= top]
    out["lt_vs_rev"] = {
        "class_fixed_effects": float(est),
        "per_pooled_sd": float(est / L.Theta_post_1pl.std()),
        "within_class_permutation_p": p_perm,
        "cluster_bootstrap_95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
        "median_regression": [float(q.params["arm"]), float(q.conf_int().loc["arm", 0]),
                              float(q.conf_int().loc["arm", 1])],
        "rank_outcome": float(smf.ols("rk ~ arm + PreTheta_1pl + C(Class)", L).fit().params["arm"]),
        "drop_top_5pct": {"estimate": float(fit(L[L.Theta_post_1pl < top])), "n_dropped": len(hi),
                          "n_dropped_lt": int(hi.arm.sum())},
    }
    r = out["lt_vs_rev"]
    print("\nROBUSTNESS -- LT minus REV, same activities, reversed order")
    print(f"   class fixed effects        {r['class_fixed_effects']:+.3f}  ({r['per_pooled_sd']:+.2f} pooled SD)")
    print(f"   within-class permutation   p = {p_perm:.4f}")
    print(f"   class-cluster bootstrap    [{r['cluster_bootstrap_95'][0]:+.3f}, {r['cluster_bootstrap_95'][1]:+.3f}]")
    mr = r["median_regression"]
    print(f"   median regression          {mr[0]:+.3f}  [{mr[1]:+.3f}, {mr[2]:+.3f}]")
    print(f"   rank outcome               {r['rank_outcome']:+.3f} of the distribution")
    dt = r["drop_top_5pct"]
    print(f"   drop top 5% of posttests   {dt['estimate']:+.3f}  ({dt['n_dropped']} children, "
          f"{dt['n_dropped_lt']} of them LT)")

    ok = lt_rev["lo"] > 0 and p_perm < 0.05
    fragile = r["cluster_bootstrap_95"][0] <= 0 or dt["estimate"] < 0.75 * est
    out["verdict"] = ("ORDER MATTERS, FRAGILELY" if ok and fragile else
                      "ORDER MATTERS" if ok else "NOT SHOWN")
    print(f"\nVERDICT: {out['verdict']}")
    (HERE / "out" / "length_order.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
