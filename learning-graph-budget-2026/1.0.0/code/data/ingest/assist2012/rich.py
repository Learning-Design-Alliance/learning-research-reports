"""Stream the ASSISTments 2012-13 export down to the fourteen columns assist_rich.csv holds.

assist_rich.csv is what the mastery-release analysis (studies/identifiability/rdd/mastery_exit.py)
and the ASSISTments reader in studies/identifiability/latent-shape/build_matrix.py read. Every row of
the export is kept, in export order: untagged, scaffolding (`original` 0) and open-response rows
included. That is how the file was first built on 2026-09-14, and the readers drop untagged rows
themselves; assist_slim.csv (studies/simulation/validate/extract_assist.py) is the filtered extract.

    python3 data/ingest/assist2012/rich.py $ASSIST_DIR/assist2012.zip $ASSIST_DIR/assist_rich.csv

On the export with MD5 049675fdba1f887fa7917c051e0e6c46 this writes 6,123,270 rows with MD5
c0f706edc41df4135be4456fc1f10854. ASSISTments terms: analysis only, no redistribution; the extract
stays outside the repository.
"""
import csv
import io
import sys
import zipfile

KEEP = ["user_id", "skill_id", "skill", "problem_id", "assignment_id", "sequence_id",
        "start_time", "correct", "hint_count", "bottom_hint", "attempt_count",
        "first_action", "tutor_mode", "position"]


def main() -> None:
    src, dst = sys.argv[1], sys.argv[2]
    csv.field_size_limit(10_000_000)
    with zipfile.ZipFile(src) as z:
        (name,) = z.namelist()
        # universal newlines, as the first build read the export from `unzip -p` on stdin
        with z.open(name) as raw, open(dst, "w", newline="") as fh:
            out = csv.writer(fh)
            out.writerow(KEEP)
            n = 0
            for row in csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8")):
                out.writerow([row.get(k, "") for k in KEEP])
                n += 1
                if n % 1_000_000 == 0:
                    print(f"  {n:,}", file=sys.stderr, flush=True)
    print(f"{n:,} rows -> {dst}")


if __name__ == "__main__":
    main()
