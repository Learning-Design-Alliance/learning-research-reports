"""Spend record for grader-model-breadth: OpenRouter-reported cost where the router reports it,
billed tokens x list price (per million, OpenRouter's listing on 2026-10-05) for direct OpenAI and
Google calls. Pricing probes (10 calls each) are entered from their logs.

    python3 spend.py <scratch>/breadth
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRICE = {"openai:gpt-5-mini": (0.25, 2.0), "google:gemini-3.5-flash-lite": (0.30, 2.50)}
PROBES = {"opus55": 0.28, "gpt5mini-minimal": 0.02, "gpt5mini-high": 0.11, "gpt5mini-default": 0.03, "gpt41mini": 0.01,
          "lite-high": 0.05, "lite-default": 0.01, "llama4": 0.01, "gemini31pro": 0.21}


def main() -> None:
    s = Path(sys.argv[1])
    runs = {}
    for f in ["opus55", "llama4", "lite-rerun", "lite-high", "g5m-min", "g5m-high"]:
        b = json.loads((s / f"swap-{f}.json").read_text())
        r, t = b["run"], b["run"]["tokens"]
        if r["reportedSpendUsd"] > 0:
            usd, how = r["reportedSpendUsd"], "OpenRouter-reported"
        else:
            pi, po = PRICE[b["model"]]
            usd, how = (t["input"] * pi + t["output"] * po) / 1e6, "tokens x list price"
        runs[f] = {"model": b["model"], "reasoning": b["reasoning"], "calls": r["calls"], "failures": r["failures"],
                   "tokens": t, "usd": round(usd, 2), "how": how}
    total = sum(v["usd"] for v in runs.values()) + sum(PROBES.values())
    out = {"cap_usd": 60, "runs": runs, "pricing_probes_usd": PROBES, "total_usd": round(total, 2),
           "skipped_by_cap": {"google:gemini-3.1-pro-preview": "projected $19; spend + 1.3 x projection > $60",
                              "anthropic/claude-fable-5.1": "projected ~$60 alone", "openai:gpt-5.5": "projected ~$50"}}
    (HERE / "out/spend.json").write_text(json.dumps(out, indent=2) + "\n")
    print({k: v["usd"] for k, v in runs.items()}, "total", round(total, 2))


if __name__ == "__main__":
    main()
