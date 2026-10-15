"""PRE-REGISTERED: in the XES3G5M authors' own deep models, do the real KC routes beat deranged routes?

QUESTION
    Liu et al. (NeurIPS 2023 Datasets and Benchmarks; Paper II literature review, entry 5.9) added
    text embeddings of XES3G5M's KC routes to simpleKT and AKT by early fusion and found nothing
    gained once question and KC content were in (simpleKT 0.8277 content -> 0.8262 content + routes;
    AKT 0.8292 -> 0.8290). That null has no control. kc_tree.py (studies/end-to-end/
    xes3g5m-kc-tree-control/) supplied one inside a logistic model: tree and family arms equivalent to
    their derangements (V1, V3). Paper II, Section 5.4, says the deep-model question was not run. This
    runs it: the authors' two models, the authors' folds and test set, with the real route text and
    with route text from deranged route trees of the same shape.

WRITTEN 2026-10-12, before any model was trained on XES3G5M responses. The analyst has read the
    authors' published AUCs (above), kc_tree.py's results, the KC-route tree's shape (metadata), the
    counts of the pyKT files (33,397 train/valid KC-level rows of 200 in five folds; 3,613 test
    sequences; 7,652 questions; 865 KCs; 1,175 route nodes) and the format of questions.json's
    kc_routes field. No response column was read. The cost check (timing.py) used synthetic data.

DATA (reads a corpus): XES3G5M (pyKT format, from the authors' release; data/data-sources.json,
    "xes3g5m"): kc_level/train_valid_sequences.csv, kc_level/test_question_window_sequences.csv,
    metadata/kc_routes_map.json, metadata/embeddings/{qid,cid}2content_emb.json, and cid2route.json
    (data/ingest/xes3g5m/flatten.py). Research use, no redistribution. The run happens on a private
    RunPod GPU pod (secure cloud), not in this repository: the maintainer approved this on 2026-10-12
    as local processing on a rented machine, not redistribution ("a local data processor, not
    redistribution, and it won't be leaked, as it might with sending it to an ai api"). The files go
    to the pod over TLS, live only on its container disk (no network volume), and the pod is
    terminated (container and disk deleted) when the run ends. Only the aggregates listed under
    OUTPUT come back; no per-learner prediction, sequence or text leaves the pod. The route names are
    embedded on the pod by a public encoder; no text is sent to any model API.

MODELS AND TRAINING (pyKT, GitHub commit fusion.PYKT_COMMIT; model files loaded unmodified, MD5s in
    fusion.PYKT_MD5)
    simpleKT  d_model 256, 2 blocks, 4 heads, dropout 0.1, final_fc 256/256, Adam lr 1e-4
              (pyKT examples/wandb_simplekt_train.py defaults).
    AKT       d_model 256, 1 block, 8 heads, dropout 0.05, d_ff 256, final_fc 512, Adam lr 1e-5
              (pyKT configs/kt_config.json, "akt").
    Both: KC-level sequences, batch 256, sequence length 200, binary cross-entropy on positions whose
    selectmask is 1 (AKT adds its Rasch L2 term), up to 200 epochs, stop when validation AUC has not
    improved for 10 epochs, keep the best-validation weights (pyKT train_model's rule). Fold f is
    the validation fold; the other four train. Five folds, one model per fold and arm. Seed 42 +
    fold for every arm, so arms differ only in their text input.
    FUSION (fusion.py; the authors' code is not public): KC embedding <- Embedding(KC) +
    Linear(KC text), question difficulty <- Embedding(question) + Linear(question text). KC text is
    the authors' released 768-d KC content embedding, concatenated with a 768-d route embedding in a
    route arm; question text is the authors' released 768-d question content embedding.

ARMS (same models, same folds, same seeds; only the route text changes)
    C      content only (KC text = content embedding alone).
    R      content + real route. Route text of KC k = the names of the route nodes from root to k's
           node, joined with "----" (the authors' questions.json format).
    Rd_j   content + deranged route, j = 0..2: the route tree deranged by kc_tree.derange_route with
           seeds e2e.SEED + 950 + j (the same three trees as kc_tree.py's Fd arms: at every depth
           >= 2 each route node is moved to another parent slot of the depth above, no node keeps its
           parent, every node keeps its depth and out-degree). Route text of k = the names along k's
           new ancestor chain, so every KC keeps its own leaf name and route length.
    ENCODER    every route arm (R and Rd) is embedded with the same public encoder,
           hfl/chinese-roberta-wwm-ext (768-d, Chinese RoBERTa), mean-pooled last layer over
           non-padding tokens, run on the pod. The authors' route embeddings are not released, so R
           is not their route arm; it is matched to its own controls, which is what the contrast needs.
    SIZE   the deranged texts are drawn from the same names, at the same lengths, through the same
           encoder, so the controls perturb the model input as much as R does. Reported, beside it:
           the mean cosine distance between each KC's R and Rd_j route vectors, and between R's
           vectors of two random KCs (the scale a full shuffle would give).

EVALUATION
    Test set: kc_level/test_question_window_sequences.csv (pyKT's question-level window test). For
    each fold model, a question's prediction is the mean of its KC predictions (pyKT "late_mean");
    pyKT's other three fusions (early, late_vote, late_all) are reported, not verdict-bearing.
    Arm AUC = the mean over the five fold models' test AUCs (the authors' reporting). Contrast
    statistics use the five-model ensemble (mean prediction per test response) so that one bootstrap
    covers all folds.
    Bootstrap: paired, over test learners (uid; the unit the authors' split assigned), B = 1,000,
    seed 20261012, the same draws for every arm and model. Rd-bar = the mean of Rd_0..2's AUCs per
    draw.

REPRODUCTION GATE (per model, before any route contrast is read): arm C's mean fold AUC within
    +-0.003 of the authors' content-only value (simpleKT 0.8277, AKT 0.8292). If it fails, that
    model's verdicts below are prefixed "SETUP NOT REPRODUCED:" and are reported as descriptive.

VERDICTS (signed; bar +0.001 on the 95% interval, equivalence margin 0.001, as kc_tree.py V1)
  V1 per model (primary), interval [lo, hi] of AUC(R) - AUC(Rd-bar):
     ROUTES BEAT THEIR DERANGEMENT            lo > +0.001
     ROUTES EQUIVALENT TO THEIR DERANGEMENT   lo > -0.001 and hi < +0.001
     DERANGEMENT BEATS THE ROUTES             hi < -0.001
     ROUTES NOT SHOWN BETTER THAN THEIR DERANGEMENT   otherwise
     UNANSWERABLE (floor fails)               if the floor below fails for that model
  V2 per model (the authors' comparison, now with a control): R - C and Rd-bar - C, each with its
     interval, read with V1's four strings ("ROUTES ADD ..." / "DERANGED ROUTES ADD ..."); reported.
  Both models are reported; neither is pooled with the other.

FLOOR (run first, on the pod, on synthetic responses; no XES3G5M response is read)
    The real question-KC structure, route tree and sequences of questions are replaced by a
    generator of the same shape: 865 KCs on the real route tree, 7,652 questions each on one KC
    drawn in proportion to the real KC frequencies (metadata only), 33,397 sequences of 200 KC
    attempts in five folds and a test set of 3,613 sequences, learners visiting route families in
    turn. Mastery m_k += 0.25 (1 - m_k) per attempt on k. logit P = theta - b_q + 1.5 m_k
    + gamma (mean m over k's route family - 0.5), the family as kc_tree.families.
    Worlds: planted (gamma 2) and null (gamma 0), one each. Arms C, R, Rd_0..2 trained exactly as
    above but on fold 0 only (one model per arm, which is then the ensemble), with the real route
    text and fresh random content vectors; the bootstrap and verdict code is the real run's.
    FLOOR PASSES for a model if V1 reads ROUTES BEAT THEIR DERANGEMENT in the planted world and does
    not in the null world. A floor that fails is reported, and that model's V1 reads UNANSWERABLE.

OUTPUT (out/): floor.json (per world, model and arm: fold AUCs, ensemble AUC, the V1 contrast and its
    interval, epochs to stop); result.json (per model and arm: fold AUCs and their mean, each of the
    four fusions, ensemble AUC, epochs to stop; V1, V2, the gate; the size check); cost.json (GPU,
    hours, dollars). No per-learner row.

WHAT IT CAN SAY  Whether, in the authors' deep models with content fused in, the expert route text
    predicts held-out learners' responses better than route text built from the same names on trees
    of the same shape with every parent link moved.
WHAT IT CANNOT   It does not use the authors' route embeddings or fusion code (neither is public),
    so R is a re-creation, gated by C's reproduction; it does not show that the route is a
    prerequisite structure, and prediction is not learning.

COST CHECK (timing.py on synthetic data, before this commit; out/timing.json): see README.md.

CHANGES (2026-10-12, all made after the cost check and before any model was trained on XES3G5M; the
    run code below is committed before the run starts)
    1. RUN ORDER. One pod per model (simpleKT on RTX 4090s, AKT on L40S; four 4090s on one machine
       were not available on RunPod's secure cloud), so each model's floor, real run and bootstrap
       stay on one machine and no per-learner prediction moves between machines. Each pod runs
       its model's floor first. Its real run starts only if that model's floor passes; a failed
       floor ends the pod's run, and the model is reported as UNANSWERABLE with no real-data
       numbers (the maintainer asked for the run to stop if the floor fails). A time cap per pod
       (DKT_HOURS) bounds the cost; a training cut off by it is reported as missing, not dropped.
    2. Details the docstring left open, fixed here: pyKT's improvement rule is validation AUC above
       the best by more than 0.001 (train_model's "auc > max_auc+1e-3"); pyKT's training loader is
       not shuffled, so neither is this one; fold AUCs use pyKT's late_mean rounded to 4 decimals
       (its own output), the ensemble averages the unrounded fold predictions; a question is a
       (uid, qidx) group of the window file's selected positions. The route encoder's resolved
       Hugging Face revision is recorded in result.json. The trees are checked on the pod against
       fingerprints of kc_tree.py's trees computed here (TREE_MD5).
    3. Floor generator, details: each synthetic question sits on one KC, drawn in proportion to the
       KC's question count in questions.json (leaf names matched to KC ids as flatten.py does);
       theta and b_q are standard normal; a learner works in blocks of 10 attempts, each block on
       a KC k0 drawn uniformly and its family (k0 plus kc_tree.families(k0)), an attempt's KC drawn
       uniformly from that pool and its question uniformly from that KC's questions; the family
       term is 0 when k's family is empty. Content vectors are standard normal, seeded per world.
       World seeds e2e.SEED + 970 (planted) and + 971 (null); rows are assigned to folds in turn.
    4. (2026-10-13, first launch) pyKT's model files put their attention masks on the default "cuda"
       device, so every training on a second GPU failed at its first batch; both pods were deleted
       after their floor's first minutes on synthetic data (no real-data job had started), each
       worker now sees only its own GPU, and the pods were relaunched from scratch.
    5. (2026-10-13, second launch) Eight AKT trainings on four L40S ran an epoch in about 140 s, against
       22 s for one AKT training alone on one L40S: the workers were starved by something shared,
       not by the GPUs. The pods were deleted again during the synthetic floor (no real-data job had
       started); now one training per GPU, four CPU threads per worker, training rows held on the GPU,
       and the download retried (Google Drive dropped one pod's connection).

    python3 dkt_routes.py --pod-package             # build the package a pod runs (no data in it)
    (on the pod) python3 dkt_routes.py --pod MODEL  # prepare, floor, then (if it passes) the real run
    python3 dkt_routes.py --smoke                   # tiny synthetic end-to-end check, CPU, no corpus
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
import random
import subprocess
import sys
import tarfile
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies/end-to-end/xes3g5m-kc-tree-control"))
sys.path.insert(0, str(ROOT / "data/ingest/xes3g5m"))

OUT = HERE / "out"
WORK = Path(os.environ.get("DKT_WORK", "/w"))
ARMS = ("C", "R", "Rd0", "Rd1", "Rd2")
DERANGED = ("Rd0", "Rd1", "Rd2")
MODELS = ("simplekt", "akt")
AUTHORS_C = {"simplekt": 0.8277, "akt": 0.8292}
GATE, BAR, EQUIV = 0.003, 0.001, 0.001
B, BOOT_SEED, FOLDS, SEED0 = 1000, 20261012, 5, 42
N_KC, N_Q, DIM, L = 865, 7_652, 768, 200
SIZES = {"rows": 33_397, "test": 3_613}
ENCODER = "hfl/chinese-roberta-wwm-ext"
GDRIVE, TAR_MD5 = "1eFiIYyh5O2V90RA0brammGH6EpHvPDQe", "cb996e44842420a32967889292b7a6d0"
CID2ROUTE_MD5 = "f381243566f9da16c29ff237b0233557"   # flatten.py's cid2route.json, as kc_tree.py read it
TREE_MD5 = {"R": "77c36026bac1a815d9e2ee27528a3c05", "Rd0": "3a12312f527897873fc189c672bee5a9",
            "Rd1": "e68f239dcded1aec39e446c454d1bcec", "Rd2": "017a15494dec446c2f12e7fd35427c17"}
WORLDS = {"planted": 2.0, "null": 0.0}
BLOCK = 10
V1_BEAT = "ROUTES BEAT THEIR DERANGEMENT"
PIP = ["pandas==2.2.2", "scikit-learn==1.5.2", "transformers==4.44.2", "gdown==5.2.0"]
PKG_FILES = ["studies/end-to-end/xes3g5m-dkt-routes/dkt_routes.py", "studies/end-to-end/xes3g5m-dkt-routes/fusion.py",
             "studies/end-to-end/xes3g5m-kc-tree-control/kc_tree.py", "studies/end-to-end/xes3g5m-build/e2e.py",
             "shared/controls.py", "shared/direction.py", "shared/paths.py", "shared/stats.py",
             "data/ingest/xes3g5m/flatten.py"]


def log(*a):
    (WORK / "out").mkdir(parents=True, exist_ok=True)
    line = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
    print(line, flush=True)
    with open(WORK / "out/log.txt", "a") as fh:
        fh.write(line + "\n")


def dump(name: str, obj) -> None:
    (WORK / "out").mkdir(parents=True, exist_ok=True)
    tmp = WORK / "out" / (name + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, ensure_ascii=False))
    tmp.rename(WORK / "out" / name)


# ---------------------------------------------------------------- route trees and their text

def tree_fp(p: dict) -> str:
    return hashlib.md5(json.dumps(sorted((repr(v), repr(p[v])) for v in p), ensure_ascii=False).encode()).hexdigest()


def route_trees(rt: dict):
    import kc_tree
    parent, depth, kcs_at, kc_node = kc_tree.real_tree(rt)
    trees = {"R": parent}
    for j in range(3):
        trees[f"Rd{j}"] = kc_tree.derange_route(parent, depth, kc_tree.e2e.SEED + 950 + j)
    return trees, kc_node, (parent, kcs_at)


def route_texts(rt: dict, trees: dict, kc_node: dict) -> dict:
    """KC k's route text on a tree: the names of the nodes from the root down to k's node."""
    texts = {}
    for arm, p in trees.items():
        t = []
        for k in range(N_KC):
            v, names = kc_node[str(k)], []
            while v is not None:
                names.append(v[-1])
                v = p[v]
            t.append("----".join(reversed(names)))
        texts[arm] = t
    assert texts["R"] == ["----".join(rt[str(k)]) for k in range(N_KC)], "R text is not the real route"
    for a in DERANGED:
        assert all(x.split("----")[-1] == y.split("----")[-1] and x.count("----") == y.count("----")
                   for x, y in zip(texts[a], texts["R"])), "a deranged route changed a leaf or a length"
    return texts


def encode(texts: list[str], dev):
    import torch
    from transformers import AutoModel, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(ENCODER)
    enc = AutoModel.from_pretrained(ENCODER).to(dev).eval()
    out = []
    for i in range(0, len(texts), 64):
        b = tok(texts[i:i + 64], padding=True, truncation=True, max_length=128, return_tensors="pt").to(dev)
        with torch.no_grad():
            h = enc(**b).last_hidden_state
        m = b["attention_mask"].unsqueeze(-1).float()
        out.append(((h * m).sum(1) / m.sum(1)).float().cpu())
    return torch.cat(out), getattr(enc.config, "_commit_hash", None)


def size_check(emb: dict) -> dict:
    """Mean cosine distance of each KC's R vector to its Rd_j vector, beside R to another KC's R."""
    import torch
    from shared.controls import check_control_scale
    def cosd(a, b):
        return float((1 - torch.nn.functional.cosine_similarity(a, b, dim=1)).mean())
    g = torch.Generator().manual_seed(BOOT_SEED)
    perm = torch.randperm(N_KC, generator=g)
    while bool((perm == torch.arange(N_KC)).any()):
        perm = torch.randperm(N_KC, generator=g)
    sizes = {a: cosd(emb["R"], emb[a]) for a in DERANGED}
    sizes["shuffle"] = cosd(emb["R"], emb["R"][perm])
    rep = check_control_scale({"shuffle": sizes["shuffle"], **{a: sizes[a] for a in DERANGED}}, DERANGED,
                              strict=False)
    return {"cosine_distance": sizes, "check_control_scale": rep}


# ---------------------------------------------------------------- data on the pod

def fetch_and_extract() -> Path:
    root = WORK / "data"
    tgz = root / "XES3G5M.tar.gz"
    root.mkdir(parents=True, exist_ok=True)
    for attempt in range(6):                    # Google Drive drops connections now and then
        if tgz.exists():
            break
        if subprocess.run([sys.executable, "-m", "gdown", GDRIVE, "-O", str(tgz)]).returncode != 0:
            tgz.unlink(missing_ok=True)
            time.sleep(30 * (attempt + 1))
    h = hashlib.md5()
    with open(tgz, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 24), b""):
            h.update(chunk)
    assert h.hexdigest() == TAR_MD5, f"tarball md5 {h.hexdigest()} != {TAR_MD5}"
    if not (root / "XES3G5M/kc_level/test_question_window_sequences.csv").exists():
        subprocess.run(["tar", "xzf", str(tgz), "-C", str(root), "XES3G5M/kc_level", "XES3G5M/metadata/questions.json",
                        "XES3G5M/metadata/kc_routes_map.json", "XES3G5M/metadata/embeddings"], check=True)
    if not (root / "cid2route.json").exists():
        import flatten
        flatten.cid2route(root)
    got = hashlib.md5((root / "cid2route.json").read_bytes()).hexdigest()
    assert got == CID2ROUTE_MD5, f"cid2route.json md5 {got} != {CID2ROUTE_MD5}"
    return root


def kc_question_counts(root: Path) -> np.ndarray:
    """Questions per KC in questions.json, leaf names matched to ids as flatten.cid2route does."""
    from collections import defaultdict
    kcmap = json.load(open(root / "XES3G5M/metadata/kc_routes_map.json", encoding="utf-8"))
    leaf2id = defaultdict(set)
    for cid, name in kcmap.items():
        leaf2id[name.strip()].add(int(cid))
    cnt = np.zeros(N_KC)
    for q in json.load(open(root / "XES3G5M/metadata/questions.json", encoding="utf-8")).values():
        rs = q["kc_routes"]
        if isinstance(rs, str):
            rs = json.loads(rs.replace("'", '"'))
        ks = {i for r in rs for i in leaf2id.get(r.split("----")[-1].strip(), ()) if i < N_KC}
        for k in ks:
            cnt[k] += 1
    return cnt


def parse_seqs(path: Path, cols: list[str], dest: Path) -> dict:
    """pyKT csv -> int32 arrays (rows, 200) per column, plus uid and fold; cached as .npy."""
    import csv
    if all((dest / f"{c}.npy").exists() for c in cols + ["uid", "fold"]):
        return {c: np.load(dest / f"{c}.npy", mmap_mode="r") for c in cols + ["uid", "fold"]}
    csv.field_size_limit(10 ** 9)
    dest.mkdir(parents=True, exist_ok=True)
    parts = {c: [] for c in cols}
    buf = {c: [] for c in cols}
    uid, fold = [], []

    def flush():
        for c in cols:
            if buf[c]:
                a = np.fromstring(",".join(buf[c]), dtype=np.int32, sep=",")
                parts[c].append(a.reshape(-1, L))
                buf[c] = []
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            uid.append(int(row["uid"]))
            fold.append(int(row["fold"]))
            for c in cols:
                buf[c].append(row[c])
            if len(uid) % 20000 == 0:
                flush()
    flush()
    out = {c: np.concatenate(parts[c]) for c in cols}
    out["uid"], out["fold"] = np.array(uid, dtype=np.int64), np.array(fold, dtype=np.int32)
    for c, a in out.items():
        assert len(a) == len(uid), c
        np.save(dest / f"{c}.npy", a)
    return {c: np.load(dest / f"{c}.npy", mmap_mode="r") for c in out}


def load_emb(path: Path, n: int) -> tuple[np.ndarray, int]:
    d = json.load(open(path))
    e = np.zeros((n, DIM), dtype=np.float32)
    hit = 0
    for k, v in d.items():
        if int(k) < n:
            e[int(k)] = np.asarray(v, dtype=np.float32)
            hit += 1
    return e, hit


def prepare(model_name: str, dev) -> dict:
    """Download, check, extract; route trees, texts and vectors; the floor's two worlds."""
    import torch
    root = fetch_and_extract()
    rt = json.load(open(root / "cid2route.json", encoding="utf-8"))
    trees, kc_node, (parent, kcs_at) = route_trees(rt)
    fps = {a: tree_fp(p) for a, p in trees.items()}
    assert fps == TREE_MD5, f"trees differ from kc_tree.py's: {fps}"
    texts = route_texts(rt, trees, kc_node)
    emb, rev = {}, None
    for a in ("R",) + DERANGED:
        emb[a], rev = encode(texts[a], dev)
    torch.save(emb, WORK / "route_emb.pt")
    info = {"model": model_name, "tree_md5": fps, "encoder": ENCODER, "encoder_revision": rev,
            "route_text_chars_mean": {a: float(np.mean([len(t) for t in texts[a]])) for a in texts},
            "size": size_check(emb)}
    qcnt = kc_question_counts(root)
    info["kcs_with_questions"] = int((qcnt > 0).sum())
    import kc_tree
    fam = kc_tree.families(parent, kc_node, kcs_at)
    famlist = [sorted(int(x) for x in fam.get(str(k), ()) if int(x) < N_KC and int(x) != k) for k in range(N_KC)]
    info["family_mean_size"] = float(np.mean([len(f) for f in famlist]))
    for w, gamma in WORLDS.items():
        d = WORK / f"world_{w}"
        if not (d / "responses.npy").exists():
            arrs = synth_world(gamma, (kc_tree.e2e.SEED + 970) if w == "planted" else (kc_tree.e2e.SEED + 971),
                               qcnt, famlist, dev)
            d.mkdir(exist_ok=True)
            for c, a in arrs.items():
                np.save(d / f"{c}.npy", a)
        y = np.load(d / "responses.npy")
        info[f"world_{w}_mean_correct"] = float(y[y >= 0].mean())
    dump(f"prep_{model_name}.json", info)
    return info


# ---------------------------------------------------------------- the floor's synthetic worlds

def synth_world(gamma: float, seed: int, qcnt: np.ndarray, famlist: list, dev) -> dict:
    import torch
    rng = np.random.default_rng(seed)
    n_rows, n_test = SIZES["rows"], SIZES["test"]
    n = n_rows + n_test
    qkc = rng.choice(N_KC, size=N_Q, p=qcnt / qcnt.sum())
    b = rng.standard_normal(N_Q)
    qs_of = [np.flatnonzero(qkc == k) for k in range(N_KC)]
    hasq = np.array([len(x) > 0 for x in qs_of])
    starts = np.flatnonzero(hasq)
    pools = [[k] + [j for j in famlist[k] if hasq[j]] for k in range(N_KC)]
    pad = lambda lists, fill: np.array([x + [fill] * (max(map(len, lists)) - len(x)) for x in lists])
    P, Psz = pad(pools, 0), np.array([len(p) for p in pools])
    Q, Qsz = pad([list(x) or [0] for x in qs_of], 0), np.array([max(len(x), 1) for x in qs_of])
    F, Fsz = pad([f or [N_KC] for f in famlist], N_KC), np.array([len(f) for f in famlist])
    t = lambda a, dt=torch.long: torch.as_tensor(a, dtype=dt, device=dev)
    P, Psz, Q, Qsz, F, Fsz, bq = t(P), t(Psz), t(Q), t(Qsz), t(F), t(Fsz), t(b, torch.float32)
    theta = t(rng.standard_normal(n), torch.float32)
    g = torch.Generator(device=dev).manual_seed(seed)
    m = torch.zeros(n, N_KC + 1, device=dev)       # column N_KC is padding, always 0
    rows = torch.arange(n, device=dev)
    qq, cc, yy = (torch.zeros(n, L, dtype=torch.long, device=dev) for _ in range(3))
    starts_t = t(starts)
    for s in range(L):
        if s % BLOCK == 0:
            k0 = starts_t[torch.randint(len(starts), (n,), generator=g, device=dev)]
        k = P[k0, (torch.rand(n, generator=g, device=dev) * Psz[k0]).long()]
        q = Q[k, (torch.rand(n, generator=g, device=dev) * Qsz[k]).long()]
        fm = torch.where(Fsz[k] > 0, m[rows[:, None], F[k]].sum(1) / Fsz[k].clamp(min=1), torch.full_like(theta, 0.5))
        logit = theta - bq[q] + 1.5 * m[rows, k] + gamma * (fm - 0.5)
        y = (torch.rand(n, generator=g, device=dev) < torch.sigmoid(logit)).long()
        m[rows, k] += 0.25 * (1 - m[rows, k])
        qq[:, s], cc[:, s], yy[:, s] = q, k, y
    fold = np.where(np.arange(n) < n_rows, np.arange(n) % FOLDS, -1).astype(np.int32)
    qidx = np.arange(n * L, dtype=np.int64).reshape(n, L)
    return {"questions": qq.cpu().numpy().astype(np.int32), "concepts": cc.cpu().numpy().astype(np.int32),
            "responses": yy.cpu().numpy().astype(np.int32), "selectmasks": np.ones((n, L), dtype=np.int32),
            "qidxs": qidx, "uid": np.arange(n, dtype=np.int64), "fold": fold}


# ---------------------------------------------------------------- training and scoring (pyKT's rules)

def to_inputs(q, c, r, sm):
    """pyKT KTDataset: pad -1; mask = c[t] and c[t+1] not pad; inputs zeroed outside it; full = cat(x[:, :1], shft)."""
    import torch
    m = (c[:, :-1] != -1) & (c[:, 1:] != -1)

    def full(x):
        x = x.clamp(min=0)
        return torch.cat([x[:, :1] * m[:, :1], x[:, 1:] * m], 1)
    return full(q), full(c), full(r), sm[:, 1:] != -1


SEQ_COLS = ("questions", "concepts", "responses", "selectmasks")


def on_device(arr: dict, dev) -> dict:
    """The training rows, moved to the GPU once (they are small), so batches are not copied per step."""
    import torch
    return {c: torch.as_tensor(np.asarray(arr[c]), device=dev) for c in SEQ_COLS}


def batches(arr: dict, idx: np.ndarray, dev, size: int):
    import torch
    for i in range(0, len(idx), size):
        j = idx[i:i + size]
        if isinstance(arr["questions"], torch.Tensor):
            jt = torch.as_tensor(j, device=dev)
            cols = (arr[c][jt].long() for c in SEQ_COLS)
        else:
            cols = (torch.as_tensor(np.asarray(arr[c][j]), dtype=torch.long, device=dev) for c in SEQ_COLS)
        yield (j,) + to_inputs(*cols)


def forward(model, name: str, q, c, r, qtest: bool = False):
    """P(correct) at positions 1..L-1 (and the hidden state pyKT's early fusion averages)."""
    import fusion
    if not qtest:
        return fusion.predict(model, name, q, c, r)
    if name == "simplekt":
        d = {"qseqs": q[:, :-1], "cseqs": c[:, :-1], "rseqs": r[:, :-1],
             "shft_qseqs": q[:, 1:], "shft_cseqs": c[:, 1:], "shft_rseqs": r[:, 1:]}
        y, h = model(d, qtest=True, train=False)
    else:
        y, _, h = model(c, r, q, True)
    return y[:, 1:], h[:, 1:]


def val_auc(model, name, arr, idx, dev) -> float:
    import torch
    from sklearn.metrics import roc_auc_score
    model.eval()
    ys, ts = [], []
    with torch.no_grad():
        for _, q, c, r, sm in batches(arr, idx, dev, 512):
            y, _ = forward(model, name, q, c, r)
            ys.append(y[sm].float().cpu().numpy())
            ts.append(r[:, 1:][sm].cpu().numpy())
    return float(roc_auc_score(np.concatenate(ts), np.concatenate(ys)))


def train(name, kc_text, q_text, arr, tr, va, seed, dev, deadline, tag):
    import torch
    import fusion
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    model = fusion.build(name, N_KC, N_Q, kc_text, q_text).to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=fusion.CONFIG[name]["lr"])
    best, best_ep, state, hist, t0 = 0.0, -1, None, [], time.time()
    for ep in range(1, fusion.MAX_EPOCHS + 1):
        model.train()
        for _, q, c, r, sm in batches(arr, tr, dev, fusion.BATCH):
            y, reg = forward(model, name, q, c, r)
            loss = torch.nn.functional.binary_cross_entropy(y[sm].double(), r[:, 1:][sm].double()) + reg
            opt.zero_grad()
            loss.backward()
            opt.step()
        auc = val_auc(model, name, arr, va, dev)
        hist.append(round(auc, 5))
        if auc > best + 1e-3:
            best, best_ep = auc, ep
            state = {k: v.detach().clone() for k, v in model.state_dict().items()}
        log(tag, "epoch", ep, "val_auc", round(auc, 4), "best_epoch", best_ep, f"{time.time() - t0:.0f}s")
        if ep - best_ep >= fusion.PATIENCE:
            break
        if time.time() > deadline:
            return None, {"aborted_at_epoch": ep, "val_auc": hist}
    model.load_state_dict(state)
    return model, {"best_val_auc": best, "best_epoch": best_ep, "epochs_run": ep, "val_auc": hist,
                   "seconds": time.time() - t0}


class Groups:
    """Questions of a test set: the (uid, qidx) groups of its selected positions, in batch order."""

    def __init__(self, arr: dict):
        sm = np.asarray(arr["selectmasks"])[:, 1:] != -1
        qidx = np.asarray(arr["qidxs"])[:, 1:][sm].astype(np.int64)
        uid = np.repeat(np.asarray(arr["uid"]), sm.sum(1))
        key = (uid << 32) | qidx
        _, self.gid = np.unique(key, return_inverse=True)
        self.G = int(self.gid.max()) + 1
        resp = np.asarray(arr["responses"])[:, 1:][sm]
        self.y = np.zeros(self.G, dtype=np.int64)
        self.y[self.gid] = resp
        assert (self.y[self.gid] == resp).all(), "a question's KC rows disagree on its response"
        self.n = np.bincount(self.gid, minlength=self.G)
        u = np.zeros(self.G, dtype=np.int64)
        u[self.gid] = uid
        _, self.unit = np.unique(u, return_inverse=True)


def score_test(model, name, arr, groups: Groups, dev) -> dict:
    """pyKT evaluate_question: per question, late_mean / late_vote / late_all over its KC predictions,
    and early fusion (the model's output layer on the mean hidden state)."""
    import torch
    model.eval()
    idx = np.arange(len(arr["uid"]))
    preds, hsum, off = [], None, 0
    gid_t = torch.as_tensor(groups.gid, device=dev)
    with torch.no_grad():
        for _, q, c, r, sm in batches(arr, idx, dev, 512):
            y, h = forward(model, name, q, c, r, qtest=True)
            p = y[sm].float()
            hs = h[sm].float()
            if hsum is None:
                hsum = torch.zeros(groups.G, hs.shape[1], device=dev)
            hsum.index_add_(0, gid_t[off:off + len(p)], hs)
            off += len(p)
            preds.append(p.cpu().numpy())
        assert off == len(groups.gid)
        hmean = hsum / torch.as_tensor(groups.n, device=dev, dtype=torch.float32)[:, None]
        early = torch.cat([torch.sigmoid(model.out(hmean[i:i + 65536]).squeeze(-1)) for i in range(0, groups.G, 65536)])
    p = np.concatenate(preds).astype(np.float64)
    g, n = groups.gid, groups.n
    hi = p >= 0.5
    s_hi = np.bincount(g, weights=p * hi, minlength=groups.G)
    s_lo = np.bincount(g, weights=p * ~hi, minlength=groups.G)
    n_hi = np.bincount(g, weights=hi, minlength=groups.G)
    n_lo = n - n_hi
    mean_hi = np.divide(s_hi, n_hi, out=np.full(groups.G, np.nan), where=n_hi > 0)
    mean_lo = np.divide(s_lo, n_lo, out=np.full(groups.G, np.nan), where=n_lo > 0)
    return {"late_mean": (s_hi + s_lo) / n,
            "late_vote": np.where(n_hi / n >= 0.5, mean_hi, mean_lo),
            "late_all": np.where(n_hi == n, mean_hi, mean_lo),
            "early": early.double().cpu().numpy()}


# ---------------------------------------------------------------- bootstrap and verdicts

def _bins(p):
    u, inv = np.unique(p, return_inverse=True)
    return inv, len(u)


def auc_w(inv, nb, y, w) -> float:
    pos = np.bincount(inv, weights=w * y, minlength=nb)
    neg = np.bincount(inv, weights=w * (1 - y), minlength=nb)
    below = np.cumsum(neg) - neg
    return float((pos * (below + 0.5 * neg)).sum() / (pos.sum() * neg.sum()))


def bootstrap(y: np.ndarray, preds: dict, unit: np.ndarray, n_boot: int = B, seed: int = BOOT_SEED) -> dict:
    """Paired bootstrap over learners: the same draws for every arm. Returns full-sample AUCs and draws."""
    U = int(unit.max()) + 1
    rng = np.random.default_rng(seed)
    y = y.astype(np.float64)
    bins = {a: _bins(p) for a, p in preds.items()}
    full = {a: auc_w(*bins[a], y, np.ones_like(y)) for a in preds}
    draws = {a: np.empty(n_boot) for a in preds}
    for b in range(n_boot):
        w = np.bincount(rng.integers(0, U, U), minlength=U)[unit].astype(np.float64)
        for a in preds:
            draws[a][b] = auc_w(*bins[a], y, w)
    return {"full": full, "draws": draws}


def interval(full: float, draws: np.ndarray) -> dict:
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return {"estimate": full, "lo": float(lo), "hi": float(hi)}


def v1(ci: dict) -> str:
    lo, hi = ci["lo"], ci["hi"]
    if lo > BAR:
        return V1_BEAT
    if lo > -EQUIV and hi < EQUIV:
        return "ROUTES EQUIVALENT TO THEIR DERANGEMENT"
    if hi < -BAR:
        return "DERANGEMENT BEATS THE ROUTES"
    return "ROUTES NOT SHOWN BETTER THAN THEIR DERANGEMENT"


def v2(ci: dict, what: str) -> str:
    lo, hi = ci["lo"], ci["hi"]
    if lo > BAR:
        return f"{what} ADD TO CONTENT"
    if lo > -EQUIV and hi < EQUIV:
        return f"{what} EQUIVALENT TO CONTENT ALONE"
    if hi < -BAR:
        return f"CONTENT ALONE BEATS {what}"
    return f"{what} NOT SHOWN TO ADD TO CONTENT"


def contrasts(y, ens: dict, unit, n_boot=B) -> dict:
    bs = bootstrap(y, ens, unit, n_boot)
    f, d = bs["full"], bs["draws"]
    dbar_f = float(np.mean([f[a] for a in DERANGED]))
    dbar_d = np.mean([d[a] for a in DERANGED], axis=0)
    out = {"ensemble_auc": f, "R_minus_Rdbar": interval(f["R"] - dbar_f, d["R"] - dbar_d)}
    out["V1"] = v1(out["R_minus_Rdbar"])
    if "C" in ens:
        out["R_minus_C"] = interval(f["R"] - f["C"], d["R"] - d["C"])
        out["Rdbar_minus_C"] = interval(dbar_f - f["C"], dbar_d - d["C"])
        out["V2_routes"] = v2(out["R_minus_C"], "ROUTES")
        out["V2_deranged"] = v2(out["Rdbar_minus_C"], "DERANGED ROUTES")
    return out


# ---------------------------------------------------------------- jobs

def kc_text_for(arm: str, content: np.ndarray, route: dict):
    import torch
    c = torch.as_tensor(content)
    return c if arm == "C" else torch.cat([c, route[arm]], 1)


def run_job(job: dict, dev_id: int, deadline: float) -> None:
    import torch
    dev = torch.device(f"cuda:{dev_id}" if torch.cuda.is_available() else "cpu")
    name, kind, arm, fold = job["model"], job["kind"], job["arm"], job["fold"]
    tag = f"{name}/{kind}/{job.get('world', '-')}/{arm}/f{fold}"
    dest = WORK / "jobs" / (tag.replace("/", "_") + ".npz")
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    route = torch.load(WORK / "route_emb.pt", weights_only=True)
    if kind == "floor":
        d = WORK / f"world_{job['world']}"
        arr = {c: np.load(d / f"{c}.npy", mmap_mode="r") for c in
               ("questions", "concepts", "responses", "selectmasks", "qidxs", "uid", "fold")}
        g = torch.Generator().manual_seed(job["world_seed"])
        content = torch.randn(N_KC, DIM, generator=g).numpy()
        q_text = torch.randn(N_Q, DIM, generator=g)
        test = {c: a[np.asarray(arr["fold"]) == -1] for c, a in arr.items()}
    else:
        arr = {c: np.load(WORK / f"arrays/train/{c}.npy", mmap_mode="r") for c in
               ("questions", "concepts", "responses", "selectmasks", "uid", "fold")}
        content, _ = load_emb(WORK / "data/XES3G5M/metadata/embeddings/cid2content_emb.json", N_KC)
        q_text = torch.as_tensor(load_emb(WORK / "data/XES3G5M/metadata/embeddings/qid2content_emb.json", N_Q)[0])
        test = {c: np.load(WORK / f"arrays/test/{c}.npy", mmap_mode="r") for c in
                ("questions", "concepts", "responses", "selectmasks", "qidxs", "uid")}
    folds = np.asarray(arr["fold"])
    tr, va = np.flatnonzero((folds != fold) & (folds >= 0)), np.flatnonzero(folds == fold)
    model, meta = train(name, kc_text_for(arm, content, route), q_text, on_device(arr, dev), tr, va, SEED0 + fold,
                        dev, deadline, tag)
    meta.update(job)
    if model is None:
        meta["aborted"] = True
        (WORK / "jobs" / (dest.stem + ".json")).write_text(json.dumps(meta))
        return
    groups = Groups(test)
    sc = score_test(model, name, test, groups, dev)
    (WORK / "jobs" / (dest.stem + ".json")).write_text(json.dumps(meta))
    np.savez(dest, **sc)
    log(tag, "done", "epochs", meta["epochs_run"], "best", meta["best_epoch"], f"val {meta['best_val_auc']:.4f}")


def worker(dev_id: int, q, deadline: float) -> None:
    # pyKT's model files build their masks on the default "cuda" device, so each worker sees one GPU
    os.environ["CUDA_VISIBLE_DEVICES"] = str(dev_id)
    for v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):   # workers share the CPUs
        os.environ[v] = "4"
    dev_id = 0
    while True:
        try:
            job = q.get_nowait()
        except Exception:
            return
        try:
            run_job(job, dev_id, deadline)
        except Exception as e:  # recorded, the others go on
            import traceback
            log("JOB FAILED", job, repr(e))
            log(traceback.format_exc())


def run_jobs(jobs: list, deadline: float) -> None:
    import multiprocessing as mp
    import torch
    ctx = mp.get_context("spawn")
    q = ctx.Queue()
    for j in jobs:
        q.put(j)
    n_gpu = max(torch.cuda.device_count(), 1)
    per = int(os.environ.get("WORKERS_PER_GPU", "1"))
    ps = [ctx.Process(target=worker, args=(i % n_gpu, q, deadline)) for i in range(n_gpu * per)]
    for p in ps:
        p.start()
        time.sleep(5)
    for p in ps:
        p.join()


def load_job(tag: str):
    f = WORK / "jobs" / (tag.replace("/", "_") + ".npz")
    meta_f = f.with_suffix(".json")
    meta = json.loads(meta_f.read_text()) if meta_f.exists() else None
    return (dict(np.load(f)) if f.exists() else None), meta


def summarise_floor(name: str, n_boot: int = B) -> dict:
    out = {}
    for w in WORLDS:
        d = WORK / f"world_{w}"
        test = {c: np.load(d / f"{c}.npy", mmap_mode="r") for c in ("selectmasks", "qidxs", "uid", "responses", "fold")}
        test = {c: a[np.asarray(test["fold"]) == -1] for c, a in test.items()}
        groups = Groups(test)
        ens, meta = {}, {}
        for a in ARMS:
            sc, mt = load_job(f"{name}/floor/{w}/{a}/f0")
            meta[a] = {k: mt.get(k) for k in ("best_val_auc", "best_epoch", "epochs_run", "aborted")} if mt else None
            if sc is not None:
                ens[a] = sc["late_mean"]
        res = {"jobs": meta}
        if all(a in ens for a in ARMS):
            res.update(contrasts(groups.y, ens, groups.unit, n_boot))
        else:
            res["V1"] = "INCOMPLETE"
        out[w] = res
    out["FLOOR_PASSES"] = out["planted"]["V1"] == V1_BEAT and out["null"]["V1"] != V1_BEAT
    return out


def summarise_real(name: str, n_boot: int = B) -> dict:
    from sklearn.metrics import roc_auc_score
    test = {c: np.load(WORK / f"arrays/test/{c}.npy", mmap_mode="r") for c in ("selectmasks", "qidxs", "uid", "responses")}
    groups = Groups(test)
    arms, ens, missing = {}, {}, []
    for a in ARMS:
        per, lm = [], []
        for f in range(FOLDS):
            sc, mt = load_job(f"{name}/real/-/{a}/f{f}")
            if sc is None:
                missing.append(f"{a}/f{f}")
                continue
            aucs = {k: float(roc_auc_score(groups.y, np.round(sc[k], 4) if k == "late_mean" else sc[k]))
                    for k in ("late_mean", "late_vote", "late_all", "early")}
            per.append({"fold": f, "test_auc": aucs, **{k: mt.get(k) for k in ("best_val_auc", "best_epoch", "epochs_run")}})
            lm.append(sc["late_mean"])
        arms[a] = {"folds": per, "mean_fold_auc": {k: float(np.mean([p["test_auc"][k] for p in per])) for k in
                                                     ("late_mean", "late_vote", "late_all", "early")} if per else None}
        if len(lm) == FOLDS:
            ens[a] = np.mean(lm, axis=0)
    out = {"model": name, "arms": arms, "missing": missing, "n_questions": groups.G,
           "n_learners": int(groups.unit.max()) + 1}
    c = arms["C"]["mean_fold_auc"]
    out["gate"] = {"authors_C": AUTHORS_C[name], "ours_C": c["late_mean"] if c else None,
                   "reproduced": bool(c and abs(c["late_mean"] - AUTHORS_C[name]) <= GATE)}
    if len(ens) == len(ARMS):
        out.update(contrasts(groups.y, ens, groups.unit, n_boot))
        if not out["gate"]["reproduced"]:
            for k in ("V1", "V2_routes", "V2_deranged"):
                out[k] = "SETUP NOT REPRODUCED: " + out[k]
    else:
        out["V1"] = "INCOMPLETE"
    return out


def pod(name: str) -> None:
    import torch
    t0 = time.time()
    deadline = t0 + float(os.environ.get("DKT_HOURS", "15")) * 3600
    dev = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    dump("status.json", {"stage": "prepare", "model": name})
    info = prepare(name, dev)
    log("prepared", json.dumps(info["size"]["cosine_distance"]))
    jobs = [{"model": name, "kind": "floor", "world": w, "arm": a, "fold": 0,
             "world_seed": BOOT_SEED + i} for i, w in enumerate(WORLDS) for a in ARMS]
    order = sorted(jobs, key=lambda j: j["arm"])
    import multiprocessing as mp
    parser = mp.get_context("spawn").Process(target=prepare_real)
    parser.start()
    dump("status.json", {"stage": "floor", "model": name})
    run_jobs(order, deadline)
    fl = summarise_floor(name)
    dump(f"floor_{name}.json", fl)
    log("floor", name, fl["planted"]["V1"], "|", fl["null"]["V1"], "passes" if fl["FLOOR_PASSES"] else "FAILS")
    parser.join()
    if not fl["FLOOR_PASSES"]:
        dump(f"result_{name}.json", {"model": name, "V1": "UNANSWERABLE (floor fails)",
                                     "note": "real run not started (floor failed)"})
    else:
        dump("status.json", {"stage": "real", "model": name})
        jobs = [{"model": name, "kind": "real", "arm": a, "fold": f} for f in range(FOLDS) for a in ARMS]
        run_jobs(jobs, deadline)
        dump(f"result_{name}.json", summarise_real(name))
    dump("status.json", {"stage": "done", "model": name, "hours": (time.time() - t0) / 3600})
    (WORK / "out/status").write_text("done")


def prepare_real() -> None:
    root = WORK / "data/XES3G5M/kc_level"
    parse_seqs(root / "train_valid_sequences.csv", ["questions", "concepts", "responses", "selectmasks"],
               WORK / "arrays/train")
    parse_seqs(root / "test_question_window_sequences.csv",
               ["questions", "concepts", "responses", "selectmasks", "qidxs"], WORK / "arrays/test")
    log("real data parsed")


# ---------------------------------------------------------------- local: package, smoke

def pod_package(dest: Path) -> None:
    import fusion
    src = Path(os.environ.get("PYKT_SRC", "")) / "pykt/models"
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for f in PKG_FILES:
            tf.add(ROOT / f, arcname=f)
        for f, md5 in fusion.PYKT_MD5.items():
            data = (src / f).read_bytes()
            assert hashlib.md5(data).hexdigest() == md5, f"pyKT {f} is not the pinned file"
            ti = tarfile.TarInfo(f"studies/end-to-end/xes3g5m-dkt-routes/kt/{f}")
            ti.size = len(data)
            tf.addfile(ti, io.BytesIO(data))
        ti = tarfile.TarInfo("studies/end-to-end/xes3g5m-dkt-routes/kt/__init__.py")
        tf.addfile(ti, io.BytesIO(b""))
    dest.write_bytes(base64.b64encode(buf.getvalue()))
    print(f"{dest}: {dest.stat().st_size:,} bytes (base64)")


def smoke() -> None:
    """Tiny end-to-end run on CPU with fake data in pyKT's formats: no corpus, no download, no encoder."""
    import tempfile
    import torch
    import fusion
    global WORK
    WORK = Path(tempfile.mkdtemp())
    src = Path(os.environ["PYKT_SRC"]) / "pykt/models"      # the pinned pyKT files, as the package ships them
    (WORK / "kt").mkdir()
    (WORK / "kt/__init__.py").write_text("")
    for f, md5 in fusion.PYKT_MD5.items():
        (WORK / "kt" / f).write_bytes((src / f).read_bytes())
        assert hashlib.md5((WORK / "kt" / f).read_bytes()).hexdigest() == md5
    sys.path.insert(0, str(WORK))
    SIZES.update(rows=60, test=12)
    fusion.MAX_EPOCHS, fusion.PATIENCE = 2, 10
    rng = np.random.default_rng(0)
    torch.save({a: torch.randn(N_KC, DIM) for a in ("R",) + DERANGED}, WORK / "route_emb.pt")
    famlist = [[(k + 1) % N_KC, (k + 2) % N_KC] for k in range(N_KC)]
    for w, gamma in WORLDS.items():
        arrs = synth_world(gamma, 1 if w == "planted" else 2, np.ones(N_KC), famlist, torch.device("cpu"))
        (WORK / f"world_{w}").mkdir()
        for c, a in arrs.items():
            np.save(WORK / f"world_{w}/{c}.npy", a)
    # fake real files: train rows and question windows with two-KC questions
    root = WORK / "data/XES3G5M"
    (root / "kc_level").mkdir(parents=True)
    (root / "metadata/embeddings").mkdir(parents=True)
    hdr = "fold,uid,questions,concepts,responses,timestamps,selectmasks,is_repeat"
    with open(root / "kc_level/train_valid_sequences.csv", "w") as fh:
        fh.write(hdr + "\n")
        for i in range(40):
            n = rng.integers(20, L + 1)
            col = lambda v: '"' + ",".join(map(str, list(v) + [-1] * (L - n))) + '"'
            fh.write(",".join([str(i % 5), str(i), col(rng.integers(0, N_Q, n)), col(rng.integers(0, N_KC, n)),
                               col(rng.integers(0, 2, n)), col([0] * n), col([1] * n), col([0] * n)]) + "\n")
    with open(root / "kc_level/test_question_window_sequences.csv", "w") as fh:
        fh.write(hdr + ",qidxs,rest,orirow\n")
        g = 0
        for u in range(6):
            n = 30
            qs, cs, rs = rng.integers(0, N_Q, n), rng.integers(0, N_KC, n), rng.integers(0, 2, n)
            for t in range(1, n):
                for kc in (cs[t], (cs[t] + 1) % N_KC):          # a two-KC question: one row per KC
                    c_ = list(cs[:t]) + [kc] + [-1] * (L - t - 1)
                    sm = [-1] * t + [1] + [-1] * (L - t - 1)
                    qi = list(range(g, g + t + 1)) + [-1] * (L - t - 1)
                    col = lambda v: '"' + ",".join(map(str, v)) + '"'
                    pad = lambda v: list(v[:t + 1]) + [-1] * (L - t - 1)
                    fh.write(",".join(["-1", str(u), col(pad(qs)), col(c_), col(pad(rs)), col([0] * L), col(sm),
                                       col([0] * L), col(qi), col([0] * L), col([0] * L)]) + "\n")
            g += n
    for f, n in (("cid2content_emb.json", N_KC), ("qid2content_emb.json", N_Q)):
        json.dump({str(i): [0.01] * DIM for i in range(n)}, open(root / "metadata/embeddings" / f, "w"))
    prepare_real()
    deadline = time.time() + 3600
    for name in MODELS:
        for w in WORLDS:
            for a in ARMS:
                run_job({"model": name, "kind": "floor", "world": w, "arm": a, "fold": 0, "world_seed": 7}, 0, deadline)
        fl = summarise_floor(name, n_boot=20)
        print(name, "floor", fl["planted"]["V1"], "|", fl["null"]["V1"], fl["FLOOR_PASSES"])
        for f in range(FOLDS):
            for a in ARMS:
                run_job({"model": name, "kind": "real", "arm": a, "fold": f}, 0, deadline)
        res = summarise_real(name, n_boot=20)
        print(name, "real", res["V1"], res["gate"], res["n_questions"], res["missing"])
    # the weighted AUC is sklearn's at unit weights, ties included
    from sklearn.metrics import roc_auc_score
    y = rng.integers(0, 2, 5000)
    p = np.round(rng.random(5000), 2)
    assert abs(auc_w(*_bins(p), y.astype(float), np.ones(5000)) - roc_auc_score(y, p)) < 1e-12
    print("smoke ok", WORK)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pod", choices=MODELS)
    ap.add_argument("--pod-package", type=Path)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.pod_package:
        pod_package(a.pod_package)
    elif a.smoke:
        smoke()
    elif a.pod:
        pod(a.pod)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
