"""
One API caller, with the failure modes this programme actually hit encoded in it.

Three scripts grew their own copy of an OpenRouter call and each learned a different lesson the hard
way. Consolidated here for the reason `CLAUDE.md` gives: a rule that lives in one copy is a rule the
next caller does not have.

**The project's `.env` wins over the ambient environment.** This is the fault that cost most of a
day. `load_key` used to return early when `OPENROUTER_API_KEY` was already set, on the reasonable
assumption that an exported variable is deliberate. It is not: this sandbox injects a key of its own,
belonging to an account with no credit, and after a restart mid-session that key appeared and every
script began sending it. The failure was a 402 reading *"Insufficient credits. This account never
purchased credits. Make sure your key is on the correct account or org."*

That message was **exactly right**, and was repeatedly dismissed as a mislabelled provider outage,
because shell commands reading `.env` directly kept succeeding against the same endpoint in the same
second. The tell was there from the first probe and took a three-way interleave -- bash 5/5, Python
0/5, alternating inside one command -- to become undeniable.

So `.env` is now authoritative when it exists, the ambient variable is a fallback, and the source is
reported (never the value) so a mismatch is visible in the first line of any run.

**The 402 that really is a 402.****The 402 that really is a 402.** `studies/producers/elicitation/protocols.py` found a hard per-request token ceiling that
returned HTTP 402, and correctly concluded that retrying was pointless. That rule was then inherited
by callers where its premise did not hold, and it aborted two runs whose key had $144 and $158
remaining and which succeeded on a single call minutes later. So a 402 now *asks the key endpoint*
whether credit is genuinely exhausted, and only aborts if it is. `_key_exhausted` returns False on
any error of its own, because killing a long run on an ambiguous signal is the failure it exists to
prevent.

**Concurrency is what trips the reservation.** OpenRouter reserves `max_tokens` of credit per
in-flight request, so the reservation is `workers x max_tokens`. Single calls sail through while a
pooled run 402s on every request. The fix is to ask for what the answer needs -- twelve lines of
`N: YES` is about 200 characters -- not to retry harder. Hence a 400-token default rather than the
1400 that failed.

**A run that dies at call 60 of 480 should not repay for the first 60.** Responses are cached on disk
by (model, prompt, seed, max_tokens, provider). Cache directories are gitignored repo-wide.

**A model name is not a model.** `MIN_INTERVAL` already carries the rule that "a model fallback would
be wrong here: an experiment whose arms silently switch model is confounded". The router does the
same thing one level down, and it had been doing it unobserved. `qwen/qwen-2.5-72b-instruct` is
served by DeepInfra at fp8 and by Novita at bf16 -- two different numerical models behind one name --
and OpenRouter picks between them per request. A rate limit on the first silently promotes the
second, so which backend answered depends on how busy the cheap one was when the call went out, and
arms compared against each other can be served by different hardware and different weights.

That is the confound the model-fallback rule exists to prevent, so `provider` is now pinned by
default and `allow_fallbacks` is off: a rate-limited provider returns 429 and is retried, rather
than quietly promoting a different one. The provider that actually answered is counted in `CALLS`
on every call, pinned or not, so a run that did switch says so in its own output.

**Every request asks for zero data retention.** The account the key belongs to enforces zero data
retention by default, but a request that relies on an account setting carries no record of it, and a
key used from another account would not. So every request sets `provider.zdr`, which lets the router
use only endpoints with a zero-data-retention policy; a model with none fails rather than being
served by one that retains prompts (maintainer, 2026-10-08). It is not part of the cache key: it
narrows which endpoints may answer, and the endpoint that answered is recorded in `CALLS`.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import contextlib
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from collections import Counter
from pathlib import Path

# Upstream rate limiting, established by testing four request bodies twice: "minimal" succeeded then
# failed, the full body failed then succeeded. Nothing about a request predicts the outcome, only how
# recently the previous one went out. Retrying harder makes it worse, so requests are PACED instead.
# A model fallback would be wrong here: an experiment whose arms silently switch model is confounded.
MIN_INTERVAL = float(os.environ.get("LLM_MIN_INTERVAL", "4.0"))
_LAST = [0.0]
_GATE = threading.Lock()

ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# Pinned per model, so an arm cannot be served by a different backend than the arm it is compared
# with. `None` for a model not listed here means "router's choice", which is fine for a one-off
# question and NOT fine for anything with arms -- pass `provider=` explicitly there.
PROVIDER: dict[str, str] = {
    # fp8 on DeepInfra, bf16 on Novita. Novita additionally rejects the chat endpoint for this
    # model with a 400, so an unpinned call during a DeepInfra rate limit fails outright.
    "qwen/qwen-2.5-72b-instruct": "DeepInfra",
    # Eleven endpoints across six clouds serve this one, and a study comparing conditions cannot
    # have the router picking a different one per call. Anthropic's own endpoint would be the
    # obvious pin but this key cannot reach it: the routing funnel drops 11 endpoints to 2 at the
    # guardrails filter and pinning to "Anthropic" then leaves 0, returning a 404 that reads like
    # the model does not exist. Bedrock is what the router reaches for unpinned, so pinning there
    # fixes the backend without fighting the funnel.
    "anthropic/claude-opus-5": "Amazon Bedrock",
}
KEY_ENDPOINT = "https://openrouter.ai/api/v1/key"
DEFAULT_MAX_TOKENS = 400
#: Seconds a single call will wait out a pinned provider's rate limit before giving up on it.
#: 300, not 1800. A batch run makes hundreds of calls, so a per-call budget multiplies: at half an
#: hour each, a 200-call run spends 100 hours working through a sustained outage instead of failing
#: and being retried. Waiting belongs in the supervisor loop around the run, where the cache makes
#: a retry nearly free, not inside each call where it is paid over and over.
RATE_LIMIT_BUDGET = float(os.environ.get("LLM_RATE_LIMIT_BUDGET", "300"))
CALLS: Counter = Counter()
LAST_ERROR: list[str] = []


def _key_exhausted() -> bool:
    try:
        req = urllib.request.Request(
            KEY_ENDPOINT, headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.load(r).get("data", {})
        rem = d.get("limit_remaining")
        return rem is not None and float(rem) <= 0
    except Exception:  # noqa: BLE001
        return False


#: The one place a script finds the repo's gitignored secrets file. Before 2026-09-25 callers read
#: the product repo's .env, or one directory above this repo (a restructure off-by-one), and so fell
#: back to the sandbox's unfunded ambient key without saying so. check_idioms bans other .env paths.
REPO_ENV = Path(__file__).resolve().parents[1] / ".env"


def env_value(name: str) -> str | None:
    """`name` from REPO_ENV if it is set there, else the ambient environment. Never printed.

    The file wins for the reason load_key gives: the sandbox injects credentials of its own."""
    if REPO_ENV.exists():
        for line in REPO_ENV.read_text().splitlines():
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return os.environ.get(name)



@contextlib.contextmanager
def _auth_header(key: str):
    """The Authorization header in a private temporary file, for `curl -H @file`.

    Passing it as `-H "Authorization: Bearer …"` put the key in curl's argv, where any process can
    read it; CLAUDE.md forbids credentials as command arguments. The body already occupies stdin."""
    fd, path = tempfile.mkstemp(prefix="hdr-", text=True)
    try:
        os.chmod(path, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(f"Authorization: Bearer {key}\n")
        yield path
    finally:
        os.unlink(path)

def load_key(env_path: str = str(REPO_ENV),
             *, quiet: bool = False) -> bool:
    """Put the project's key in the environment, preferring `.env` over anything already set.

    Deliberately NOT "use whatever is exported". See the module docstring: the sandbox exports a key
    of its own with no credit behind it, and silently preferring it produced a day of 402s that read
    as a provider fault. The key is never printed; only which source supplied it, and a short tail so
    a mismatch is recognisable without exposing the secret."""
    ambient = os.environ.get("OPENROUTER_API_KEY")
    from_file = None
    p = Path(env_path)
    if p.exists():
        for line in p.read_text().splitlines():
            if line.startswith("OPENROUTER_API_KEY="):
                from_file = line.split("=", 1)[1].strip().strip('"').strip("'")
    chosen = from_file or ambient
    if not chosen:
        return False
    os.environ["OPENROUTER_API_KEY"] = chosen
    if not quiet:
        src = ".env" if from_file else "ambient environment"
        note = ""
        if from_file and ambient and from_file != ambient:
            note = f"  (overriding a DIFFERENT ambient key ...{ambient[-6:]})"
        print(f"   key from {src} ...{chosen[-6:]}{note}", flush=True)
    return True


def preflight(model: str, *, provider: str | None | bool = True) -> str:
    """"" if `model` will answer right now, otherwise why it will not.

    A study that starts into a provider outage does not fail, it grinds: every call waits out its
    rate-limit budget and then returns nothing, and hours later there is a log full of empty arms.
    One cheap call first turns that into a sentence. Call it before the arms, not instead of
    checking the arms.

    A rejected key aborts inside `call`, which is right for a run and wrong for a probe, so that is
    caught here and returned as the reason like any other. Callers tell the two apart with
    `is_auth_failure`: capacity is worth retrying later, credentials are not."""
    before = len(LAST_ERROR)
    try:
        # a small rate-limit budget on purpose: the question is "is it answering now", and a
        # preflight that waits half an hour to say no is the grind it exists to prevent
        txt = call(model, "Reply with the single word: ok", seed=0, max_tokens=8, temperature=0.0,
                   attempts=1, provider=provider, rate_limit_budget=45.0)
    except SystemExit as e:
        detail = " ".join(str(e).split())
        return detail[:200] if detail else "key rejected"
    if txt.strip():
        return ""
    return LAST_ERROR[-1][:200] if len(LAST_ERROR) > before else "no response and no error"


def is_auth_failure(reason: str) -> bool:
    """Is this preflight reason about credentials rather than capacity?

    Worth the separate function because the two call for opposite responses. A rate limit means
    wait and retry; an expired key means stop and tell someone, and a supervisor loop that retries
    it just spends twelve hours proving the key is still expired."""
    low = reason.lower()
    return "401" in low or "expired" in low or "invalid_token" in low or "rejected" in low


def call(model: str, prompt: str, seed: int, *, cache: Path | None = None,
         max_tokens: int = DEFAULT_MAX_TOKENS, temperature: float = 0.8,
         attempts: int = 10, provider: str | None | bool = True,
         rate_limit_budget: float | None = None,
         response_format: dict | None = None, system: str | None = None,
         meta: dict | None = None) -> str:
    """The model's text, or "" after `attempts` failures. Aborts only on confirmed exhaustion.

    `provider` is the backend to pin to. `True`, the default, means "whatever `PROVIDER` says for
    this model, and the router's choice if it says nothing". `False` opts out of pinning -- only do
    that for a call whose answer is not compared with another call. A name pins to it explicitly.
    The pin is part of the cache key, so switching provider does not silently reuse the other
    backend's answers.

    `system` is a separate system message rather than text glued onto the prompt, because an
    evaluator whose published contract is a system/user pair is a different request when the two are
    concatenated, and this caller exists partly to run other people's contracts faithfully.

    `response_format` is passed through untouched for structured output. It is part of the cache key
    too: the same prompt constrained to a schema and left free are different requests, and reusing
    one for the other would be the provider confound in miniature.

    `meta`, when given, is filled with who answered and under what request: the slug asked for, the
    model the response names, the provider, generation id, usage (including cost when the router
    reports it), finish reason, the request parameters and a UTC timestamp. The programme twice lost
    the model identity of outputs it kept; a caller that stores a text stores this beside it. With a
    cache the record is kept in a sidecar file and returned on a hit, marked `from_cache`."""
    key = os.environ["OPENROUTER_API_KEY"]
    budget = RATE_LIMIT_BUDGET if rate_limit_budget is None else rate_limit_budget
    if provider is True:
        provider = PROVIDER.get(model)
    elif provider is False:
        provider = None

    ck = None
    if cache is not None:
        cache.mkdir(parents=True, exist_ok=True)
        ck = cache / (hashlib.sha256(
            f"{model}\x00{prompt}\x00{seed}\x00{max_tokens}\x00{provider or ''}"
            f"\x00{json.dumps(response_format, sort_keys=True) if response_format else ''}"
            f"\x00{system or ''}".encode()).hexdigest() + ".txt")
        if ck.exists():
            CALLS["cached"] += 1
            side = ck.with_suffix(".meta.json")
            if meta is not None and side.exists():
                meta.update(json.loads(side.read_text()), from_cache=True)
            return ck.read_text()

    msgs = ([{"role": "system", "content": system}] if system else []) \
        + [{"role": "user", "content": prompt}]
    payload = {"model": model, "messages": msgs,
               "temperature": temperature, "max_tokens": max_tokens, "seed": seed}
    # Zero data retention on every request, pinned or not (see the module docstring).
    payload["provider"] = {"zdr": True}
    if provider:
        # allow_fallbacks off on purpose: a promoted fallback is a silent model change mid-run.
        payload["provider"].update(order=[provider], allow_fallbacks=False)
    if response_format:
        payload["response_format"] = response_format
    body = json.dumps(payload).encode()
    if meta is not None:
        meta.update(requested_model=model, from_cache=False, request={
            k: v for k, v in payload.items() if k not in ("messages", "model")},
            system_message=bool(system))
    # `attempt` is advanced by hand rather than by a for-loop, because a 429 must NOT spend it --
    # see the rate-limit branch below. Its own budget is time, not tries.
    rl_attempt, rl_waited, attempt = 0, 0.0, 0
    while attempt < attempts:
        with _GATE:
            wait = MIN_INTERVAL - (time.monotonic() - _LAST[0])
            if wait > 0:
                time.sleep(wait)
            _LAST[0] = time.monotonic()
        # curl, not urllib. In this sandbox the two disagree: back-to-back tests had curl at 3/3
        # while in-process urllib returned 402 on every call, and the pattern survived every request
        # variant. Rather than keep bisecting a proxy interaction we do not control, use the client
        # that demonstrably works here. The HTTP semantics below are unchanged.
        try:
            with _auth_header(key) as hdr:
              proc = subprocess.run(
                ["curl", "-sS", "-X", "POST", ENDPOINT,
                 "-H", f"@{hdr}",
                 "-H", "Content-Type: application/json",
                 "--data-binary", "@-", "-w", "\n%{http_code}"],
                input=body, capture_output=True, timeout=300)
            raw = proc.stdout.decode("utf-8", "replace")
            status_line, _, _ = raw.rpartition("\n")[2], None, None
            text, _, status = raw.rpartition("\n")
            code = int(status.strip()) if status.strip().isdigit() else 0
            if code != 200:
                detail = f"HTTP {code} | {text[:160]}"
                if meta is not None:
                    meta["last_error"] = detail
                # An expired or revoked key is not capacity, and retrying cannot fix it. Left to
                # the generic retry it burns ten attempts and returns "" -- indistinguishable from
                # a provider outage, and it silently empties whichever arm was running when the
                # key died. That is how both_reversed came back 29 calls short. Stop loudly.
                if code == 401:
                    CALLS["error"] += 1
                    raise SystemExit(
                        f"\nABORT: {detail}\nThe key is rejected, not rate-limited -- retrying "
                        "cannot fix it. Refresh OPENROUTER_API_KEY in the project's .env. Cached "
                        "calls are kept, so the run resumes rather than restarts.")
                if code == 402 and _key_exhausted():
                    CALLS["error"] += 1
                    raise SystemExit(f"\nABORT: {detail}\nThe key endpoint confirms no credit "
                                     "remains. Cached calls are kept; re-run after topping up.")
                # A 429 is the provider being busy, not the request being wrong, and with
                # allow_fallbacks off it is the normal way a pinned provider says "later". It gets
                # its own patient backoff and does NOT spend the attempt budget, because ten
                # attempts of <=20s is about two minutes and an upstream rate limit outlasts that
                # easily -- which is how a 200-call run loses whole arms to a busy afternoon.
                if code == 429:
                    if rl_waited > budget:
                        CALLS["error"] += 1
                        LAST_ERROR.append(f"rate-limited for {rl_waited:.0f}s | {detail}")
                        return ""
                    nap = min(180.0, 10.0 * 2 ** rl_attempt) * (0.5 + random.random())
                    CALLS["retry_429"] += 1
                    rl_attempt += 1
                    rl_waited += nap
                    time.sleep(nap)
                    continue
                if attempt == attempts - 1:
                    CALLS["error"] += 1
                    LAST_ERROR.append(detail)
                    return ""
                CALLS[f"retry_{code}"] += 1
                time.sleep(min(20, 2 ** attempt) * (0.5 + random.random()))
                attempt += 1
                continue
            d = json.loads(text)
            ch = d["choices"][0]
            # counted whether or not the call was pinned, so a study that did switch backends
            # mid-run can be caught by reading its own call counter
            CALLS[f"via_{d.get('provider', 'unknown')}"] += 1
            txt = ch["message"].get("content") or ""
            if meta is not None:
                meta.update(served_model=d.get("model"), provider=d.get("provider"),
                            generation_id=d.get("id"), created=d.get("created"),
                            finish_reason=ch.get("finish_reason"),
                            native_finish_reason=ch.get("native_finish_reason"),
                            usage=d.get("usage"),
                            timestamp_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
            if txt.strip():
                CALLS["ok"] += 1
                if ck is not None:
                    ck.write_text(txt)
                    if meta is not None:
                        ck.with_suffix(".meta.json").write_text(json.dumps(meta, indent=1))
                return txt
            CALLS["truncated" if ch.get("finish_reason") == "length" else "empty"] += 1
            return ""
        except SystemExit:
            raise
        except Exception as e:  # noqa: BLE001
            if attempt == attempts - 1:
                CALLS["error"] += 1
                LAST_ERROR.append(repr(e)[:160])
                return ""
            time.sleep(min(20, 2 ** attempt) * (0.5 + random.random()))
            attempt += 1
    return ""


EMBED_ENDPOINT = "https://openrouter.ai/api/v1/embeddings"


def embed(model: str, texts: list[str], *, cache: Path | None = None,
          provider: str | None | bool = True, attempts: int = 5,
          meta: dict | None = None) -> list[list[float]] | None:
    """One embedding per text, in order, or None after `attempts` failures.

    Same key, pacing, provider pin and cache rules as `call`, for the same reasons: an embedding
    matcher whose vectors come from two backends is two matchers. `meta` records the model the
    response names, the provider, usage and a timestamp."""
    key = os.environ["OPENROUTER_API_KEY"]
    if provider is True:
        provider = PROVIDER.get(model)
    elif provider is False:
        provider = None
    ck = None
    if cache is not None:
        cache.mkdir(parents=True, exist_ok=True)
        ck = cache / (hashlib.sha256(json.dumps([model, texts, provider or ""]).encode())
                      .hexdigest() + ".emb.json")
        if ck.exists():
            CALLS["cached"] += 1
            d = json.loads(ck.read_text())
            if meta is not None:
                meta.update(d["meta"], from_cache=True)
            return d["vectors"]
    payload = {"model": model, "input": texts, "provider": {"zdr": True}}
    if provider:
        payload["provider"].update(order=[provider], allow_fallbacks=False)
    body = json.dumps(payload).encode()
    for attempt in range(attempts):
        with _GATE:
            wait = MIN_INTERVAL - (time.monotonic() - _LAST[0])
            if wait > 0:
                time.sleep(wait)
            _LAST[0] = time.monotonic()
        try:
            with _auth_header(key) as hdr:
              proc = subprocess.run(
                ["curl", "-sS", "-X", "POST", EMBED_ENDPOINT,
                 "-H", f"@{hdr}",
                 "-H", "Content-Type: application/json",
                 "--data-binary", "@-", "-w", "\n%{http_code}"],
                input=body, capture_output=True, timeout=300)
            text, _, status = proc.stdout.decode("utf-8", "replace").rpartition("\n")
            code = int(status.strip()) if status.strip().isdigit() else 0
            if code != 200:
                detail = f"HTTP {code} | {text[:160]}"
                if meta is not None:
                    meta["last_error"] = detail
                if code == 401:
                    raise SystemExit(f"\nABORT: {detail}\nThe key is rejected.")
                if code == 402 and _key_exhausted():
                    raise SystemExit(f"\nABORT: {detail}\nThe key endpoint confirms no credit.")
                LAST_ERROR.append(detail)
                if code in (400, 403, 404):
                    # deterministic refusals (bad request, the account's data-policy guardrail, an
                    # unknown model): retrying cannot change them
                    break
                time.sleep(min(20, 2 ** attempt) * (0.5 + random.random()))
                continue
            d = json.loads(text)
            rows = sorted(d["data"], key=lambda r: r.get("index", 0))
            vecs = [r["embedding"] for r in rows]
            if len(vecs) != len(texts):
                LAST_ERROR.append(f"{len(vecs)} vectors for {len(texts)} texts")
                continue
            CALLS[f"via_{d.get('provider', 'unknown')}"] += 1
            CALLS["ok"] += 1
            info = dict(requested_model=model, served_model=d.get("model"),
                        provider=d.get("provider"), generation_id=d.get("id"),
                        usage=d.get("usage"), n_texts=len(texts),
                        request={"provider": payload.get("provider")},
                        timestamp_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
            if meta is not None:
                meta.update(info, from_cache=False)
            if ck is not None:
                ck.write_text(json.dumps({"meta": info, "vectors": vecs}))
            return vecs
        except SystemExit:
            raise
        except Exception as e:  # noqa: BLE001
            LAST_ERROR.append(repr(e)[:160])
            time.sleep(min(20, 2 ** attempt) * (0.5 + random.random()))
    CALLS["error"] += 1
    return None


def key_status() -> dict | None:
    """The key's spend so far: `usage`, `limit`, `limit_remaining` (USD), or None if unreadable.

    For budget ledgers. Only these three fields are returned, never the key or its label."""
    try:
        req = urllib.request.Request(
            KEY_ENDPOINT, headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.load(r).get("data", {})
        return {k: d.get(k) for k in ("usage", "limit", "limit_remaining")}
    except Exception:  # noqa: BLE001
        return None
