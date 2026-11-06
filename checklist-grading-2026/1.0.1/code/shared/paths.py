"""Resolve data locations without hard-coding one machine's filesystem.

Several analyses here read corpora that cannot be committed - a session scratchpad, a sibling repo,
a licence-restricted download. Those paths were written as absolute literals, which meant the
scripts ran exactly once, on one machine, and thereafter died at import with a FileNotFoundError
naming a directory nobody else has.

Helpers, all of which fail loudly and usefully instead:

    HERE(__file__)        this script's own directory - for anything inside the repo, which should
                          never have been absolute in the first place
    data_path(VAR)        a registered corpus: $VAR, else the default data/data-sources.json records
                          for it under scratch_root(), fetched there first if it is missing and has
                          an unattended route (shared/fetch.py); raises naming VAR when neither exists
    scratch_root()        the root `$SCRATCH` stands for in the registry
    external(...)         an unregistered location outside the repo: takes an environment variable
                          and an optional CLI override, and raises with the variable name and what
                          the data is when neither is set
"""

from __future__ import annotations

import os
from pathlib import Path


def HERE(file: str) -> Path:
    """The directory containing `file`. Use for repo-internal paths."""
    return Path(file).resolve().parent


def external(env_var: str, what: str, override: str | None = None,
             *, must_exist: bool = True) -> Path:
    """A corpus that lives outside this repo.

    `override` is a value from argparse if the script offers one. Otherwise the environment
    variable is read. Raising here - with the variable name and a description of the data - is the
    point: a script that cannot find its corpus should say which corpus and how to point it at one.
    """
    raw = override or os.environ.get(env_var)
    if not raw:
        raise SystemExit(
            f"{what} not found.\n"
            f"  Set {env_var} to its directory, or pass the corresponding command-line override.\n"
            f"  This data is not committed to the repository, by licence or by size.")
    p = Path(raw).expanduser()
    if must_exist and not p.exists():
        raise SystemExit(f"{env_var}={p} does not exist.\n  Expected: {what}")
    return p


# --------------------------------------------------------------------------- corpus locations
#
# THE ONE PLACE A CORPUS PATH IS RESOLVED. Every corpus has an environment variable, documented with
# its default in data/data-sources.json (`env`). data_path(VAR) returns $VAR if it is set; otherwise
# that default, with $SCRATCH replaced by scratch_root(). A path that does not exist fails with the
# variable's name, so a reader on another machine is told what to set rather than shown this one's
# filesystem.
#
# scratch_root() is LDA_SCRATCH_DIR if set; else the session scratchpad these analyses were run in,
# if this machine still has it; else ./external, the registry's own default. The session path is
# written here and nowhere else (shared/check_idioms.py enforces it).

REPO = Path(__file__).resolve().parents[1]
REGISTRY = REPO / "data" / "data-sources.json"
SESSION_SCRATCH = ("/tmp/claude-0/-home-user-learning-engine-ai-frontend/"
                   "95e45190-f913-5b1d-89d5-0a9410ca02ad/scratchpad")


def scratch_root() -> Path:
    """The root that `$SCRATCH` in data/data-sources.json stands for."""
    raw = os.environ.get("LDA_SCRATCH_DIR")
    if raw:
        return Path(raw).expanduser()
    if Path(SESSION_SCRATCH).is_dir():
        return Path(SESSION_SCRATCH)
    return REPO / "external"


_DEFAULTS: dict[str, str] | None = None


def registry_default(env_var: str) -> str:
    """The default data/data-sources.json records for `env_var`, $SCRATCH unexpanded."""
    global _DEFAULTS
    if _DEFAULTS is None:
        import json
        if not REGISTRY.is_file():           # e.g. a release's code package, which ships no registry
            raise SystemExit(f"{env_var} is not set, and there is no data/data-sources.json here to "
                             f"supply its default. Set {env_var} to the corpus location.")
        _DEFAULTS = {}
        for s in json.loads(REGISTRY.read_text(encoding="utf-8"))["sources"]:
            _DEFAULTS.update(s.get("env") or {})
    if env_var not in _DEFAULTS:
        raise KeyError(f"{env_var} has no entry in data/data-sources.json; add one (`env`) before "
                       f"reading it")
    return _DEFAULTS[env_var]


def data_path(env_var: str, *, must_exist: bool = True) -> Path:
    """Where the corpus behind `env_var` lives: $env_var, else its registry default.

    With must_exist=False the path is returned unchecked, for module constants resolved at import
    and for callers that test existence themselves."""
    raw = os.environ.get(env_var)
    if raw:
        p = Path(raw).expanduser()
        if must_exist and not p.exists():
            raise SystemExit(f"{env_var}={p} does not exist.")
        return p
    default = registry_default(env_var)
    p = Path(default.replace("$SCRATCH", str(scratch_root())))
    if must_exist and not p.exists() and "$SCRATCH" in default:
        from shared import fetch                   # corpora that can come back unattended do (shared/fetch.py)
        if fetch.autofetch_enabled():
            fetch.ensure(env_var)
    if must_exist and p.exists():
        from shared import fetch
        fetch.touch_env(env_var)
    if must_exist and not p.exists():
        rel = default.replace("$SCRATCH", "").lstrip("/")
        alt = (f", or LDA_SCRATCH_DIR to the directory holding {rel!r}" if rel else
               ", or LDA_SCRATCH_DIR to that directory") if "$SCRATCH" in default else ""
        raise SystemExit(
            f"{p} not found.\n"
            f"  Set {env_var} to its location{alt}.\n"
            f"  data/data-sources.json says where the data comes from; it is not committed.")
    return p
