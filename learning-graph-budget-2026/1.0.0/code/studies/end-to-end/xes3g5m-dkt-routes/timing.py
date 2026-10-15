"""Cost check for dkt_routes.py: time training epochs of the fused simpleKT and AKT on SYNTHETIC data.

No corpus is read: sequences are random draws in XES3G5M's KC-level shape (33,397 train/valid rows of
200 KC attempts, five folds; 865 KCs; 7,652 questions; 768-dimensional text vectors). One fold's
training set (four folds, about 26,718 rows) and its validation fold (about 6,679 rows) are timed
with the exact model, fusion, batch size and optimiser of the real run. Run on the GPU pod:

    python3 timing.py --epochs 3 > timing.json

The first epoch includes CUDA warm-up; the projection uses the median of the rest.
"""
from __future__ import annotations

import json
import statistics
import sys
import time

import numpy as np
import torch

import fusion

N_ROWS, N_KC, N_Q, DIM = 33_397, 865, 7_652, 768


def synth(rng, n):
    q = torch.from_numpy(rng.integers(0, N_Q, (n, fusion.SEQ_LEN)))
    c = torch.from_numpy(rng.integers(0, N_KC, (n, fusion.SEQ_LEN)))
    r = torch.from_numpy(rng.integers(0, 2, (n, fusion.SEQ_LEN)))
    m = torch.ones(n, fusion.SEQ_LEN - 1, dtype=torch.bool)
    return q, c, r, m


def epoch(model, name, data, opt, dev, train):
    q, c, r, m = data
    model.train(train)
    ys, ts = [], []
    for i in range(0, len(q), fusion.BATCH):
        b = [x[i:i + fusion.BATCH].to(dev) for x in (q, c, r, m)]
        with torch.set_grad_enabled(train):
            y, reg = fusion.predict(model, name, b[0], b[1], b[2])
            t = b[2][:, 1:].float()
            if train:
                loss = torch.nn.functional.binary_cross_entropy(y[b[3]], t[b[3]]) + reg
                opt.zero_grad()
                loss.backward()
                opt.step()
            else:
                ys.append(y[b[3]].float().cpu())
    if dev.type == "cuda":
        torch.cuda.synchronize()


def main(epochs: int) -> None:
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    rng = np.random.default_rng(0)
    n_val = N_ROWS // 5
    tr, va = synth(rng, N_ROWS - n_val), synth(rng, n_val)
    out = {"device": torch.cuda.get_device_name(0) if dev.type == "cuda" else "cpu",
           "torch": torch.__version__, "rows_train": N_ROWS - n_val, "rows_val": n_val, "models": {}}
    for name in ("simplekt", "akt"):
        for arm, width in (("content", DIM), ("route", 2 * DIM)):
            torch.manual_seed(0)
            model = fusion.build(name, N_KC, N_Q, torch.randn(N_KC, width), torch.randn(N_Q, DIM)).to(dev)
            opt = torch.optim.Adam(model.parameters(), lr=fusion.CONFIG[name]["lr"])
            if dev.type == "cuda":
                torch.cuda.reset_peak_memory_stats()
            times = []
            for _ in range(epochs):
                t0 = time.time()
                epoch(model, name, tr, opt, dev, True)
                epoch(model, name, va, opt, dev, False)
                times.append(time.time() - t0)
                print(name, arm, f"{times[-1]:.1f}s", file=sys.stderr, flush=True)
            out["models"][f"{name}/{arm}"] = {
                "epoch_seconds": times, "epoch_seconds_median_after_first": statistics.median(times[1:] or times),
                "peak_gb": torch.cuda.max_memory_allocated() / 1e9 if dev.type == "cuda" else None}
            del model, opt
            if dev.type == "cuda":
                torch.cuda.empty_cache()
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(int(sys.argv[sys.argv.index("--epochs") + 1]) if "--epochs" in sys.argv else 3)
