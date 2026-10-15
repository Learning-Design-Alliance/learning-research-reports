"""Diagnose the binding floor failure (run after it, before any real-data statistic): where does a
planted projection order go?

W_proj is built on the real marginals (as holon.py --floor --shape real) at BETA 0.3 and 1.0 (every
learner enrols in P_red's topological order). D is reported with and without the catalogue
residualization, beside the raw order statistic. Synthetic learners only; reads MOOCCubeX enrolment
marginals through holon.load_real.

    python3 floor_diagnosis.py out/floor-diagnosis.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import holon as H  # noqa: E402

proj = H.build_projection(H.data_path("MOOCCUBEX_DIR"))
cidx = {c: i for i, c in enumerate(proj["courses"])}
R, info, breadth, first, tl, cl = H.load_real(cidx)
M = H.real_marginals(R, breadth, tl, cl)
out = {}
for beta in (0.3, 1.0):
    rng = np.random.default_rng(7)
    S = H.synth_world("W_proj", proj, cidx, M, rng, beta=beta)
    E, raw, _ = H.excess(S, np.arange(S.n), rng)
    En, _, _ = H.excess(S, np.arange(S.n), rng, resid=False)
    idx = H.edge_index(proj["P"]["P_red"], cidx)
    out[str(beta)] = {"D_resid": H.D_of(E, idx)[0], "D_derangement_only": H.D_of(En, idx)[0],
                      "raw_order_D": H.D_of(raw, idx)[0]}
    print(beta, out[str(beta)], flush=True)
out["N"] = M["N"]
json.dump(out, open(sys.argv[1], "w"), indent=1)
