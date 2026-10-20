# MOOCCubeX — assessed

[THU-KEG](https://github.com/THU-KEG/MOOCCubeX), GPL-3.0, **direct download, no application**.
4,216 courses, 637,572 concepts, 358,265 exercises, ~296M behavioural records from 3.3M students.

Run: `python3 mooccubex_assess.py --dir <download dir>`

**Verdict: take it, but as an observations source, not a structure source.** Its unique value is a
real Q-matrix attached to real response data, available today with no approval. Its annotated
prerequisite structure is about the size of LectureBank's.

## What is actually annotated

The headline numbers are concepts and behaviour. The prerequisite files are mostly *candidates*:

| domain | rows | annotated | share | positive edges |
| --- | --- | --- | --- | --- |
| math | 331,202 | 1,598 | **0.48%** | 761 |
| psy | 757,771 | 1,745 | **0.23%** | 831 |
| cs | 492,102 | 1,522 | **0.31%** | 725 |

Everything else carries `ground_truth: -1` — a candidate pair nobody judged, with model scores
attached. Counting those as negatives would convert "not annotated" into "annotated absent", which
is the absence-is-not-evidence rule in the place it is easiest to break, since `-1` sits in the same
column as `0` and `1`.

So the human-annotated structure is **~2,300 positive edges across three domains**. Comparable to
LectureBank (208), far short of what 637,572 concepts suggests.

## Structure: not trees, but mostly not real either

| domain | nodes | edges/node | components | shared-neighbour | null p95 | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| math | 294 | 2.59 | 1 | 0.445 | 0.459 | fails |
| psy | 377 | 2.20 | 1 | 0.450 | 0.519 | fails (below its null) |
| cs | 287 | 2.53 | 8 | 0.350 | 0.272 | **survives** |

All three are well above tree density (~1.0), which is rare and would matter — B3 established that
tree edges are unrecoverable by construction, so every corpus that was a tree was dead on arrival.

But **two of three do not survive a degree-preserving null**, so their apparent recoverability is
degree, not structure. Only `cs` clears it, and it still clears restricted to its largest component
(0.354 vs 0.287), so that is not a fragmentation artifact from a rewiring that merges components.

**And the density is probably an artifact of annotation.** 294 annotated nodes out of 637,572
concepts: annotators worked over a small curated set, so the induced subgraph is dense because
attention was concentrated, not because the domain is. What we can say is that *this subgraph* is
not a tree. Whether prerequisite structure over the full concept set is tree-like is not answered
here, and the annotated sample cannot answer it.

## The prediction columns are not independent evidence

Annotated pairs score far higher under the shipped model than unlabelled ones:

| domain | median score, annotated | median, unlabelled | unlabelled scoring >0.9 |
| --- | --- | --- | --- |
| math | 0.446 | 0.023 | 7,540 |
| psy | 0.381 | 0.007 | 20,998 |
| cs | 0.483 | 0.095 | 26,738 |

Two readings the data cannot separate: pairs were **selected** for annotation because a model
flagged them, or the model was **trained** on these labels and scores them high for that reason.
The repo cites a co-training method, which makes the second likely. Either way the prediction
columns cannot be used as independent signal, and the annotated subgraph's representativeness is
unestablished. Separating the two needs the paper's sampling protocol.

## The one thing it has that nothing else does

`relations/concept-problem.txt` — **29,141 links, 13,822 concepts, 19,983 problems**, mean 1.46
concepts per problem. That is a Q-matrix, in our vocabulary a corpus of `evidence_for` constraints.

And `relations/user-problem.json` (21G) is the response data those problems generated.

Together they are exactly what an AHM-style attribute-hierarchy induction, or IITA, needs: a
Q-matrix plus responses. **That makes MOOCCubeX a structure source after all** — not through its
annotations, but by inducing structure from behaviour, which is the provenance class the corpus has
none of. And unlike DataShop it needs no approval and no export queue.

### Correction: the expert-versus-behaviour comparison is NOT available here

An earlier version of this page said the annotated and induced structures would be "two independent
readings of the same concepts — the expert-versus-behaviour comparison, available in one dataset."
**That was wrong**, and the reason is structural rather than a sampling artifact.

The two sides use different concept namespaces — the prerequisite files carry bare names
(`边界路由器`), `concept-problem` carries `K_<name>_<field>` (`K_浊_中国语言文学`) — so the direct
overlap is **zero**. Normalising the prefix away recovers a little, and then the numbers are:

| concepts must have a problem attempted by | attempted concepts | shared with annotated | annotated pairs with BOTH ends usable |
| --- | --- | --- | --- |
| ≥1 learner | 1,694 | 32 | **11** |
| ≥5 learners | 720 | 13 | **0** |
| ≥10 learners | 568 | 11 | **0** |

At any threshold that could support induction, **no annotated prerequisite pair has both endpoints
on a well-attempted concept**. The annotated files cover psychology, mathematics and computer
science; the heavily-attempted problems sit in whatever courses had the most activity — military
history, control engineering, Chinese linguistics. The two halves of the dataset are about different
subjects.

So MOOCCubeX supports induction **or** comparison against its annotations, not both. The induction
is still worth having — it is the first `induced` provenance in the corpus — but the comparison
needs a dataset where the same concepts are both annotated and worked.

*(The 21G file was deliberately not downloaded here — the assessment did not need it, and it should
be pulled straight into whatever runs the induction.)*

## Cross-domain holdout: genuine

| domain | concepts | also appear in another domain |
| --- | --- | --- |
| cs | 702 | 2.1% |
| math | 576 | 2.4% |
| psy | 871 | 0.1% |

This is the best property it has. **ESCO failed the same test at 87–98%** — its "held-out" ISCO
groups reused almost all of the held-out skills, so leave-one-group-out was never a holdout at all.
Here a leave-one-domain-out split is real.

(Concepts are Chinese-language strings; the overlap is exact-match on the label, so it is a floor —
translation-equivalent concepts across domains would not be caught.)

## What to do with it

1. **Pull `concept-problem.txt` + `user-problem.json` and run IITA on a single course's concepts.**
   First real learner data the surmise/IITA pipeline has ever seen — it is validated only on
   simulation. No approval needed, so it de-risks the whole observation story rather than waiting on
   CMU.
2. **Treat the ~2,300 annotated edges as a small `asserted` corpus**, comparable to LectureBank, and
   never pool them with the `-1` rows.
3. **Do not use the model prediction columns** for anything, per above.
4. **Do not plan on comparing induced structure against the annotations here** — see the
   correction above. At any learner threshold that supports induction, no annotated pair has both
   endpoints on a well-attempted concept.

## Provenance, in interchange terms

| part | basis |
| --- | --- |
| `ground_truth` 0/1 | `asserted` (human annotation) — ~2,300 positives across three domains |
| `text_predict` / `graph_predict` | `generated` — and not independent of the annotations |
| `concept-problem` links | `asserted` — extracted, but a real Q-matrix |
| anything induced from `user-problem` | `induced` — the class we have none of |
