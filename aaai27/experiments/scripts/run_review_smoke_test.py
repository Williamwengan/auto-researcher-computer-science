#!/usr/bin/env python3
"""Run a small blind-review smoke test on an anonymous review pack."""

from __future__ import annotations

import argparse
import http.client
import json
import os
import re
import socket
import ssl
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]

DIMENSIONS = [
    "novelty",
    "excitement",
    "feasibility",
    "expected_effectiveness",
    "overall",
    "baseline_grounding",
    "experimental_rigor",
    "mechanism_specificity",
    "implementation_readiness",
]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def extract_json(text: str) -> dict:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.S)
        if match:
            return json.loads(match.group(0))
        raise


def normalize_review(review: dict) -> dict:
    """Normalize harmless provider-specific JSON scalar variations."""
    preference = review.get("preference")
    if isinstance(preference, str):
        normalized = preference.strip()
        review["preference"] = normalized.upper() if normalized.lower() in {"a", "b"} else normalized.lower()
    scores = review.get("scores", {})
    if isinstance(scores, dict):
        for pair in scores.values():
            if not isinstance(pair, dict):
                continue
            for side in ("A", "B"):
                value = pair.get(side)
                if isinstance(value, str) and value.strip().isdigit():
                    pair[side] = int(value.strip())
                elif isinstance(value, float) and value.is_integer():
                    pair[side] = int(value)
    return review


def select_items(rows: list[dict], max_items: int) -> list[dict]:
    selected = []
    seen = set()
    for row in rows:
        comparison = row["comparison"]
        if comparison not in seen:
            selected.append(row)
            seen.add(comparison)
        if len(selected) >= max_items:
            return selected
    for row in rows:
        if row not in selected:
            selected.append(row)
        if len(selected) >= max_items:
            break
    return selected


def build_prompt(item: dict) -> str:
    score_shape = {dim: {"A": "integer 1-5", "B": "integer 1-5"} for dim in DIMENSIONS}
    output_shape = {
        "item_id": item["item_id"],
        "scores": score_shape,
        "preference": "A | B | tie",
        "overall_rationale": "brief rationale grounded in the candidates",
        "strengths_A": ["..."],
        "strengths_B": ["..."],
        "concerns_A": ["..."],
        "concerns_B": ["..."],
    }
    return (
        "You are an anonymous research-idea reviewer. You must not infer method identity from formatting.\n"
        "Compare Candidate A and Candidate B only on the content shown below.\n"
        "Use integer scores from 1 to 5, where 5 is best. Prefer tie only when genuinely indistinguishable.\n"
        "Return valid JSON only with this exact top-level shape:\n"
        + json.dumps(output_shape, ensure_ascii=False, indent=2)
        + "\n\nREVIEW ITEM:\n"
        + json.dumps(item, ensure_ascii=False, indent=2)
    )


def call_model(base_url: str, model: str, api_key: str, prompt: str, timeout: int, max_attempts: int,
               max_output_tokens: int) -> tuple[str, dict, list[dict]]:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a careful blind reviewer. Return JSON only."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": max_output_tokens,
    }
    request = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ResearchArena-AAAI27/1.0",
        },
        method="POST",
    )
    retryable = {429, 500, 502, 503, 504, 520, 521, 522, 523, 524}
    retry_events = []
    for attempt in range(1, max_attempts + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"], data.get("usage", {}), retry_events
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:2000]
            # Some OpenAI-compatible gateways report permanent routing errors
            # (for example, a Claude model requested with a GPT-group key) as
            # HTTP 503. Retrying those responses only wastes time.
            permanent_markers = ("model_not_found", "No available channel for model")
            if any(marker in body for marker in permanent_markers):
                raise RuntimeError(
                    f"Permanent provider routing error (HTTP {exc.code}); check model name and API-key group: {body}"
                ) from exc
            if exc.code in retryable and attempt < max_attempts:
                delay = min(10 * (2 ** (attempt - 1)), 60)
                retry_events.append({"attempt": attempt, "http_code": exc.code, "body": body, "delay_seconds": delay})
                print(f"  RETRY HTTP {exc.code}: attempt {attempt}/{max_attempts}, wait {delay:g}s")
                time.sleep(delay)
                continue
            raise RuntimeError(f"HTTP {exc.code} from provider after {attempt} attempt(s): {body}") from exc
        except (urllib.error.URLError, TimeoutError, socket.timeout, ssl.SSLError, ConnectionResetError, http.client.RemoteDisconnected) as exc:
            if attempt < max_attempts:
                delay = min(10 * (2 ** (attempt - 1)), 60)
                retry_events.append(
                    {
                        "attempt": attempt,
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                        "delay_seconds": delay,
                    }
                )
                print(f"  RETRY {type(exc).__name__}: attempt {attempt}/{max_attempts}, wait {delay:g}s")
                time.sleep(delay)
                continue
            raise RuntimeError(f"{type(exc).__name__} from provider after {attempt} attempt(s): {exc}") from exc
    raise RuntimeError("Provider call exhausted retry loop")


def validate_review(item_id: str, review: dict) -> None:
    if review.get("item_id") != item_id:
        raise ValueError(f"Review item_id mismatch: expected {item_id}, got {review.get('item_id')}")
    if review.get("preference") not in {"A", "B", "tie"}:
        raise ValueError(f"{item_id} invalid preference: {review.get('preference')}")
    scores = review.get("scores")
    if not isinstance(scores, dict):
        raise ValueError(f"{item_id} missing scores dict")
    for dim in DIMENSIONS:
        pair = scores.get(dim)
        if not isinstance(pair, dict):
            raise ValueError(f"{item_id} missing score dimension: {dim}")
        for side in ("A", "B"):
            value = pair.get(side)
            if not isinstance(value, int) or value < 1 or value > 5:
                raise ValueError(f"{item_id} invalid {dim}.{side}: {value}")


def write_summary(path: Path, rows: list[dict], reviewer_id: str) -> None:
    pref_counts = {"A": 0, "B": 0, "tie": 0}
    for row in rows:
        pref_counts[row["review"]["preference"]] += 1
    lines = [
        "# Blind Review Smoke Summary",
        "",
        f"Reviewer: `{reviewer_id}`",
        f"Items: {len(rows)}",
        "",
        "| preference | count |",
        "| --- | ---: |",
    ]
    for pref, count in pref_counts.items():
        lines.append(f"| {pref} | {count} |")
    lines.extend([
        "",
        "This smoke test validates reviewer JSON format and public-pack usability only. It is not a paper result.",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def ordered_unique_results(rows: list[dict], ordered_item_ids: list[str]) -> list[dict]:
    by_id = {}
    for row in rows:
        if row.get("status") == "success" and row.get("item_id"):
            by_id[row["item_id"]] = row
    return [by_id[item_id] for item_id in ordered_item_ids if item_id in by_id]


def make_result(
    item: dict,
    review: dict,
    reviewer_id: str,
    model: str,
    usage: dict | None,
    retry_events: list[dict] | None,
    wall_time_seconds: float,
    recovered_from_raw: bool,
) -> dict:
    return {
        "item_id": item["item_id"],
        "task": item["task"],
        "comparison": item["comparison"],
        "replicate_id": item.get("replicate_id"),
        "reviewer_id": reviewer_id,
        "model": model,
        "status": "success",
        "usage": usage or {},
        "retry_events": retry_events or [],
        "wall_time_seconds": wall_time_seconds,
        "recovered_from_raw": recovered_from_raw,
        "review": review,
        "finished_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review-pack", default="aaai27/experiments/results/derived/review_pack_seed11_v1/anonymous_review_items.jsonl")
    parser.add_argument("--output-dir", default="aaai27/experiments/results/derived/review_smoke_seed11_v1")
    parser.add_argument("--reviewer-id", default="gpt55_review_smoke")
    parser.add_argument("--model", default="gpt-5.5")
    parser.add_argument("--base-url", default="https://estellecode.com/v1")
    parser.add_argument(
        "--api-key-env",
        default="ESTELLE_API_KEY",
        help="Name of the environment variable containing the API key.",
    )
    parser.add_argument("--max-items", type=int, default=4)
    parser.add_argument("--timeout-seconds", type=int, default=180)
    parser.add_argument("--max-attempts", type=int, default=5)
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=2200,
        help="Maximum reviewer completion tokens; use a larger value for verbose providers.",
    )
    parser.add_argument(
        "--max-new-api-calls",
        type=int,
        default=0,
        help="Stop gracefully after this many new API calls; 0 means no limit.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    pack_path = ROOT / args.review_pack
    out_dir = ROOT / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = out_dir / "raw_reviews"
    raw_dir.mkdir(parents=True, exist_ok=True)
    items = select_items(read_jsonl(pack_path), args.max_items)
    ordered_item_ids = [item["item_id"] for item in items]
    prompts = [(item, build_prompt(item)) for item in items]

    if args.dry_run:
        print(f"Planned review smoke items: {len(prompts)}")
        for item, prompt in prompts:
            print(f"DRY {item['item_id']}: comparison={item['comparison']} prompt_chars={len(prompt)}")
        return

    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise RuntimeError(f"{args.api_key_env} is not loaded")
    try:
        api_key.encode("ascii")
    except UnicodeEncodeError as exc:
        raise RuntimeError(
            f"{args.api_key_env} contains non-ASCII characters. Replace placeholder/Chinese text "
            "with the actual provider API key, then source the env file again."
        ) from exc
    if any(marker in api_key.lower() for marker in ("your_api", "replace_me", "placeholder")):
        raise RuntimeError(f"{args.api_key_env} still appears to contain a placeholder value")

    results_path = out_dir / "review_results.jsonl"
    results = []
    completed_ids = set()
    if results_path.exists():
        results = ordered_unique_results(read_jsonl(results_path), ordered_item_ids)
        completed_ids = {row["item_id"] for row in results}
        write_jsonl(results_path, results)
        write_summary(out_dir / "review_smoke_summary.md", results, args.reviewer_id)
    new_api_calls = 0
    for item, prompt in prompts:
        if item["item_id"] in completed_ids:
            print(f"SKIP {item['item_id']}: already in review_results.jsonl")
            continue
        started = time.time()
        raw_path = raw_dir / f"{item['item_id']}.txt"
        if raw_path.exists():
            raw = raw_path.read_text(encoding="utf-8")
            try:
                review = normalize_review(extract_json(raw))
                validate_review(item["item_id"], review)
            except json.JSONDecodeError as exc:
                invalid_dir = out_dir / "invalid_raw_reviews"
                invalid_dir.mkdir(parents=True, exist_ok=True)
                suffix = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                invalid_path = invalid_dir / f"{item['item_id']}.{suffix}.txt"
                raw_path.replace(invalid_path)
                print(f"QUARANTINED {item['item_id']}: malformed/truncated JSON -> {invalid_path.name}: {exc}")
            else:
                result = make_result(
                    item,
                    review,
                    args.reviewer_id,
                    args.model,
                    usage={},
                    retry_events=[],
                    wall_time_seconds=0.0,
                    recovered_from_raw=True,
                )
                results.append(result)
                results = ordered_unique_results(results, ordered_item_ids)
                completed_ids.add(item["item_id"])
                write_jsonl(results_path, results)
                write_summary(out_dir / "review_smoke_summary.md", results, args.reviewer_id)
                print(f"RECOVERED {item['item_id']} preference={review['preference']}: no API call ({len(results)}/{len(items)})")
                continue
        if args.max_new_api_calls and new_api_calls >= args.max_new_api_calls:
            print(f"STOP after {new_api_calls} new API calls: progress {len(results)}/{len(items)}")
            break
        raw, usage, retry_events = call_model(
            args.base_url,
            args.model,
            api_key,
            prompt,
            args.timeout_seconds,
            args.max_attempts,
            args.max_output_tokens,
        )
        raw_path.write_text(raw, encoding="utf-8")
        review = normalize_review(extract_json(raw))
        validate_review(item["item_id"], review)
        elapsed = round(time.time() - started, 3)
        results.append(
            make_result(
                item,
                review,
                args.reviewer_id,
                args.model,
                usage,
                retry_events,
                elapsed,
                recovered_from_raw=False,
            )
        )
        results = ordered_unique_results(results, ordered_item_ids)
        completed_ids.add(item["item_id"])
        new_api_calls += 1
        write_jsonl(results_path, results)
        write_summary(out_dir / "review_smoke_summary.md", results, args.reviewer_id)
        print(f"OK  {item['item_id']} preference={review['preference']} ({len(results)}/{len(items)})")

    write_jsonl(results_path, results)
    write_summary(out_dir / "review_smoke_summary.md", results, args.reviewer_id)
    print(f"Wrote {out_dir / 'review_results.jsonl'}")
    print(f"Wrote {out_dir / 'review_smoke_summary.md'}")


if __name__ == "__main__":
    main()
