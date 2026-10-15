# learning-research-reports

Published research releases of the Learning Design Alliance's learning-engineering programme. The
research is carried out with AI agents, and each article's AI-use section says how.

A research release is the programme's replacement for a journal article. It is the article together
with everything needed to check it: the release file (data locations and checksums, analyses with
their code paths and commits, the governing protocol, the evidence), the code package, the per-case
outputs, a reproduction script, re-run notebooks, and an HTML report in which every number is linked
to the output it was computed from.

Drafts are not kept here. A release is prepared and audited in the programme's research
repository, which is private. It is copied here only after a person has released it from embargo,
and only after it has passed two gates: a patent check and a publication-readiness check. The
readiness check requires an independent scope audit and reproduction, a disclosure of how AI was
used, and the maintainer's sign-off. The findings themselves are also summarised as claim pages in
[learning-wiki](https://github.com/Learning-Design-Alliance/learning-wiki), which links back to the
releases here.

## Layout

```
<release>/<version>/
  <version>.yaml        the release file
  LIFT.json             who lifted it, when, from which commit, and the SHA-256 of every file here
  article/              the article and the figures it embeds
  report/index.html     the HTML report (open it in a browser), with its executed notebooks
  code/                 the code package; code/SHA256SUMS lists its files
  reproduce.py, REPRODUCE.md
  notebooks/            re-run notebooks, where the release has them
  per-case-*            per-case outputs and their README
  protocol/             the protocol the release follows
  artifacts/            other documents the release cites, at their original paths
```

## Versions

Nothing is versioned until it is published. A version folder is never changed after it is merged.
A correction is a new version folder, and its release file names the version it supersedes. CI
(`scripts/check_releases.py`) refuses a pull request that:

- edits, adds to or deletes from a published version folder;
- adds a folder without a `LIFT.json` signed by a person;
- adds a file that `LIFT.json` does not list, or whose hash differs from the recorded one;
- adds any file that still carries the programme's embargo marker.

The check proves that a folder is complete and unaltered. It cannot prove that the lift happened,
since anyone can write a `LIFT.json`, so pull requests are merged only by the maintainer.

## DOIs

Each version gets one DOI from Zenodo, minted by `scripts/mint_doi.py` and recorded in `DOIS.json`,
because a published version folder never changes. The deposit is the version folder as one zip.

1. **Reserve** (anyone): `python3 scripts/mint_doi.py --release <r> --version <v> --reserve`. This
   creates an unpublished Zenodo deposition holding a reserved DOI, and writes it to `DOIS.json` as
   `reserved`. Commit that through a pull request. An unpublished deposition can still be deleted.
2. **Merge** the release's pull request, so that the version folder is on `main`.
3. **Publish** (the maintainer only): `python3 scripts/mint_doi.py --release <r> --version <v> --publish
   --by human:<name> --yes`. This uploads the zip, publishes the record and marks the entry
   `published`. Commit `DOIS.json` through a pull request. **This cannot be undone.**

The token comes from the environment: `ZENODO_TOKEN`, with the scopes `deposit:write` and
`deposit:actions`. Run the whole flow on the sandbox first: add `--sandbox` and set
`ZENODO_SANDBOX_TOKEN`. Sandbox DOIs never resolve, and `DOIS.json` is not changed for them. Use
`--metadata` to see what would be deposited, offline. CI refuses a `DOIS.json` entry that is
malformed, names a version that does not exist, or changes after it has been published.

## Citing

Cite the release's DOI (in `DOIS.json`) where it has one, or this repository's URL for the version folder, with the
release's title and authors from its release file.

## Licences

- Code (`code/`, `reproduce.py`, `scripts/`): MIT, in [`LICENSE`](LICENSE).
- Text, figures, reports and data outputs: Creative Commons Attribution 4.0 International, in
  [`LICENSE-CONTENT`](LICENSE-CONTENT).

The corpora the analyses read are not included and keep their own terms, which each release file
states. Some of them forbid redistribution or commercial use.
