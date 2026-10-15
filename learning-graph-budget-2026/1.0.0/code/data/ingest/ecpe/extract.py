"""Extract the ECPE responses and Q-matrix from the CDM package's source archive.

ECPE (Examination for the Certificate of Proficiency in English, University of Michigan; now Michigan
Language Assessment): 2,922 examinees, 28 dichotomous grammar items, a 3-skill Q-matrix (morphosyntactic,
cohesive, lexical rules). Used by Templin & Hoffman (2013, EMIP 32, 37-50) and Templin & Bradshaw (2014,
Psychometrika 79, 317-339), who report a hierarchy among the three skills. CDM ships it as
data/data.ecpe.rda, downloaded by its author from Templin's 2012 NCME workshop page (now offline).

No data licence is stated anywhere found (checked 2026-10-07): CDM's GPL covers the package code, not
the data. The maintainer approved use (2026-10-07) under the programme's strictest terms: research use,
no redistribution, aggregates only in the repository; cite Templin & Hoffman (2013) and CDM.

    python3 data/ingest/ecpe/extract.py $SCRATCH/ecpe/CDM_8.3-14.tar.gz $SCRATCH/ecpe

Writes ecpe_responses.csv (id, E1..E28) and ecpe_qmatrix.csv (item, skill1..skill3). Needs the pure-Python
`rdata` package (and xarray), e.g. `pip install --target <dir> --no-deps rdata xarray` then PYTHONPATH=<dir>;
pyreadr cannot read the R list the data are stored as.
"""
import sys
import tarfile
import tempfile
from pathlib import Path

import rdata


def main() -> None:
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    with tarfile.open(src) as t, tempfile.TemporaryDirectory() as tmp:
        member = t.getmember("CDM/data/data.ecpe.rda")
        f = Path(tmp) / "data.ecpe.rda"
        f.write_bytes(t.extractfile(member).read())
        e = rdata.read_rda(str(f))["data.ecpe"]
    data, qm = e["data"], e["q.matrix"].copy()
    assert data.shape == (2922, 29) and qm.shape == (28, 3), (data.shape, qm.shape)
    data.to_csv(out / "ecpe_responses.csv", index=False)
    qm.insert(0, "item", [f"E{i}" for i in range(1, len(qm) + 1)])
    qm.to_csv(out / "ecpe_qmatrix.csv", index=False)
    print(f"responses {data.shape}, q-matrix {qm.shape} -> {out}")


if __name__ == "__main__":
    main()
