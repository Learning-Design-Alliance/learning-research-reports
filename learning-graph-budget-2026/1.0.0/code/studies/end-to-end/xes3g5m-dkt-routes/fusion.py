"""Early fusion of frozen text embeddings into pyKT's simpleKT and AKT (runs on the GPU pod).

The XES3G5M authors' fusion code is not public. This is the fusion dkt_routes.py pre-registers:
    KC side       q_embed(c) <- Embedding(c) + Linear(T_kc[c]), where T_kc[c] is the frozen KC text
                  vector: the authors' released KC content embedding (768), concatenated with the
                  KC's route-text embedding (768) in a route arm. The response embedding inherits it
                  (pyKT's qa_embed(r) + q_embed(c), separate_qa False).
    question side difficult_param(q) <- Embedding(q) + Linear(T_q[q]), T_q the authors' released
                  question content embedding (768). pyKT zero-initialises the Embedding (its reset());
                  the Linear starts at PyTorch's default.
The model files are pyKT's own (simplekt.py, akt.py, utils.py at the commit PYKT_COMMIT), loaded
unmodified; only the two embedding attributes are replaced after construction.
"""
from __future__ import annotations

import torch
from torch import nn

PYKT_COMMIT = "eec087e0230520e7ae7bbd4f5433d71612df62fb"
PYKT_MD5 = {"simplekt.py": "d2bab37e3ac2eddd03269f5c05268ac8", "akt.py": "8dd4057423a1bd4530024d9b387896eb",
            "utils.py": "609b532863f87b759d6d85e9eaca2d68"}

# pyKT's XES3G5M configurations (configs/kt_config.json and the authors' defaults)
CONFIG = {
    "simplekt": dict(d_model=256, n_blocks=2, dropout=0.1, d_ff=256, num_attn_heads=4, final_fc_dim=256,
                     final_fc_dim2=256, lr=1e-4),
    "akt": dict(d_model=256, n_blocks=1, dropout=0.05, d_ff=256, num_attn_heads=8, final_fc_dim=512, lr=1e-5),
}
BATCH, SEQ_LEN, MAX_EPOCHS, PATIENCE = 256, 200, 200, 10


class Fused(nn.Module):
    def __init__(self, base: nn.Embedding, text: torch.Tensor):
        super().__init__()
        self.base = base
        self.register_buffer("text", text.float())
        self.proj = nn.Linear(text.shape[1], base.embedding_dim)

    def forward(self, idx):
        return self.base(idx) + self.proj(self.text[idx])


def build(name: str, n_kc: int, n_q: int, kc_text: torch.Tensor, q_text: torch.Tensor):
    from kt.akt import AKT
    from kt.simplekt import simpleKT
    c = {k: v for k, v in CONFIG[name].items() if k != "lr"}
    if name == "simplekt":
        m = simpleKT(n_kc, n_q, seq_len=SEQ_LEN, **c)
    else:
        m = AKT(n_kc, n_q, **c)
    m.q_embed = Fused(m.q_embed, kc_text)
    m.difficult_param = Fused(m.difficult_param, torch.cat([q_text, torch.zeros(1, q_text.shape[1])]))
    nn.init.constant_(m.difficult_param.base.weight, 0.0)
    return m


def predict(m, name: str, q, c, r):
    """q, c, r: (B, L) long tensors (padded with 0, masked outside). Returns P(correct) for positions 1..L-1."""
    if name == "simplekt":
        d = {"qseqs": q[:, :-1], "cseqs": c[:, :-1], "rseqs": r[:, :-1],
             "shft_qseqs": q[:, 1:], "shft_cseqs": c[:, 1:], "shft_rseqs": r[:, 1:]}
        y, _, _ = m(d, train=True)
        return y[:, 1:], 0.0
    y, reg = m(c, r, q)
    return y[:, 1:], reg
