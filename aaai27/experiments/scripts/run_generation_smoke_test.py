#!/usr/bin/env python3
"""Render or execute AAAI-27 generation runs.

The runner uses one OpenAI-compatible endpoint, a shared evidence context, a
common output schema, and per-call usage/error logs. `focused_full` performs a
second repair call; this extra cost is retained and must be reported.

By default the runner keeps the original seed-11 smoke behavior. Pass
`--replicate-id` or `--all-replicates` for the main experiment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]


class ProviderRequestError(RuntimeError):
    def __init__(self, message: str, retry_events: list[dict]):
        super().__init__(message)
        self.retry_events = retry_events


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


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


def evidence_context(evidence_dir: Path, max_papers: int, abstract_chars: int) -> tuple[str, set[str]]:
    cards_path = evidence_dir / "evidence_baseline_cards.jsonl"
    papers_path = evidence_dir / "papers.jsonl"
    if not cards_path.exists() or not papers_path.exists():
        raise FileNotFoundError(f"Evidence files missing in {evidence_dir}")
    cards = read_jsonl(cards_path)
    papers = read_jsonl(papers_path)
    paper_by_id = {str(row.get("paper_id")): row for row in papers if row.get("paper_id")}
    referenced_ids = []
    for card in cards:
        for evidence in card.get("evidence_papers", []) or []:
            paper_id = evidence.get("paper_id")
            if paper_id and str(paper_id) not in referenced_ids:
                referenced_ids.append(str(paper_id))
    selected = []
    seen = set()
    # Match the v0.5 renderer: papers explicitly used by baseline cards have
    # priority over generic retrieval order.
    for paper_id in referenced_ids:
        paper = paper_by_id.get(paper_id)
        if paper is not None and paper_id not in seen:
            selected.append(paper)
            seen.add(paper_id)
        if len(selected) >= max_papers:
            break
    for paper in sorted(papers, key=lambda row: row.get("relevance_score", 0), reverse=True):
        paper_id = str(paper.get("paper_id"))
        if len(selected) >= max_papers:
            break
        if paper.get("paper_id") and paper_id not in seen:
            selected.append(paper)
            seen.add(paper_id)
    compact_papers = []
    for paper in selected:
        compact_papers.append(
            {
                "paper_id": paper.get("paper_id"),
                "title": paper.get("title"),
                "year": paper.get("year"),
                "abstract": (paper.get("abstract") or "")[:abstract_chars],
            }
        )
    context = (
        "EVIDENCE BASELINE CARDS (shared across methods):\n"
        + "\n".join(json.dumps(row, ensure_ascii=False) for row in cards)
        + "\n\nPAPERS (shared across methods):\n"
        + "\n".join(json.dumps(row, ensure_ascii=False) for row in compact_papers)
    )
    # Both blocks are explicitly supplied to the model. A citation is not a
    # hallucinated ID if it occurs in either a baseline card or the detailed
    # paper subset; semantic support is assessed later by the claim verifier.
    allowed_ids = {str(row["paper_id"]) for row in compact_papers if row.get("paper_id")}
    allowed_ids.update(referenced_ids)
    return context, allowed_ids


FOCUSED_OUTPUT = r'''
Return valid JSON only with this shape:
{"ideas": [{
  "idea_id": "idea_1",
  "title": "...",
  "baseline_weakness": "...",
  "proposed_mechanism": "...",
  "minimal_new_module": "...",
  "algorithmic_objective": "...",
  "direct_baselines": ["..."],
  "required_data": ["..."],
  "required_scripts": ["..."],
  "metrics": ["..."],
  "ablations": ["..."],
  "negative_controls": ["..."],
  "success_thresholds": ["..."],
  "evidence_paper_ids": ["..."],
  "risk_and_fallback": "..."
}]}
Generate exactly three ideas. Do not cite any paper_id absent from the supplied evidence.
'''

BASELINE_OUTPUT = r'''
Return valid JSON only with this shape:
{"ideas": [{
  "idea_id": "idea_1",
  "title": "...",
  "description": "...",
  "motivation": "...",
  "proposed_approach": "...",
  "related_work": ["..."],
  "experiment_outline": "...",
  "evidence_paper_ids": ["..."]
}]}
Generate exactly three ideas. Do not cite any paper_id absent from the supplied evidence.
Do not add fields merely to imitate another method.
'''


METHOD_INSTRUCTIONS = {
    "direct_prompt": "Generate three novel and feasible research ideas for the task. Use the supplied evidence where relevant.",
    "researcharena": (
        "Act as the ResearchArena ideation stage. Explore distinct publishable proposals, verify novelty against the supplied "
        "related work, and provide a detailed experiment-ready proposal for each idea."
    ),
    "focused_no_repair": (
        "Generate focused evidence-grounded ideas. Each idea must bind one concrete baseline weakness to one minimal new "
        "mechanism and a falsifiable experiment. Avoid tool-stack novelty and mechanism mismatch."
    ),
    "focused_generic_refine": (
        "Generate focused evidence-grounded ideas. Each idea must bind one concrete baseline weakness to one minimal new "
        "mechanism and a falsifiable experiment. This initial generation will receive a generic self-refinement pass."
    ),
    "focused_full": (
        "Generate focused evidence-grounded ideas. Each idea must bind one concrete baseline weakness to one minimal new "
        "mechanism and a falsifiable experiment. This is the initial generation before a separate repair pass."
    ),
}


REPAIR_INSTRUCTION = r'''
You are the consistency-aware repair stage. Inspect the three ideas below. Repair evidence gaps, vague mechanisms,
task-domain mismatch, missing negative controls, and implementation ambiguity. Preserve the identity of each idea and do
not copy a loss/module from one idea into another unless its mechanism logically requires it. Use only supplied paper_ids.
Return the same JSON schema and exactly three repaired ideas. JSON only.
'''

GENERIC_REFINE_INSTRUCTION = r'''
Improve the clarity, coherence, feasibility, and presentation of the three ideas below. Preserve each idea's identity.
Do not apply an explicit mechanism-consistency checklist, evidence critic, domain verifier, or targeted reviewer rationale.
Return the same focused JSON schema and exactly three improved ideas. JSON only.
'''


def build_prompt(method: str, task_text: str, evidence_text: str) -> str:
    output_instruction = BASELINE_OUTPUT if method in {"direct_prompt", "researcharena"} else FOCUSED_OUTPUT
    return (
        "TASK SPECIFICATION:\n" + task_text + "\n\n" + evidence_text + "\n\nMETHOD INSTRUCTION:\n"
        + METHOD_INSTRUCTIONS[method] + "\n\n" + output_instruction
    )


def chat_completion(api: dict, generation: dict, api_key: str, prompt: str) -> tuple[str, dict, list[dict]]:
    payload = {
        "model": api["model"],
        "messages": [
            {"role": "system", "content": "You are a rigorous AI research ideation system. Return JSON only."},
            {"role": "user", "content": prompt},
        ],
        "temperature": generation["temperature"],
        "max_tokens": generation["max_output_tokens"],
    }
    request = urllib.request.Request(
        api["base_url"].rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            # Cloudflare rejects Python urllib's default user agent on this
            # endpoint even though the same authenticated request via curl is
            # accepted. Use a stable, descriptive research client identifier.
            "User-Agent": "ResearchArena-AAAI27/1.0",
        },
        method="POST",
    )
    max_attempts = int(api.get("max_attempts", 1))
    initial_delay = float(api.get("retry_initial_seconds", 10))
    max_delay = float(api.get("retry_max_seconds", 60))
    # 520--524 are Cloudflare gateway/origin failures. They are transient
    # infrastructure errors, not model-output failures, and are safe to retry
    # without changing the frozen request.
    retryable_codes = {429, 500, 502, 503, 504, 520, 521, 522, 523, 524}
    retry_events = []
    for attempt in range(1, max_attempts + 1):
        try:
            with urllib.request.urlopen(request, timeout=int(api["timeout_seconds"])) as response:
                data = json.loads(response.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"], data.get("usage", {}), retry_events
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:2000]
            if exc.code in retryable_codes and attempt < max_attempts:
                delay = min(initial_delay * (2 ** (attempt - 1)), max_delay)
                retry_events.append(
                    {"attempt": attempt, "http_code": exc.code, "body": body, "delay_seconds": delay}
                )
                print(f"  RETRY HTTP {exc.code}: attempt {attempt}/{max_attempts}, wait {delay:g}s")
                time.sleep(delay)
                continue
            raise ProviderRequestError(
                f"HTTP {exc.code} from provider after {attempt} attempt(s): {body}", retry_events
            ) from exc
    raise ProviderRequestError("Provider call exhausted retry loop", retry_events)


def validate_output(parsed: dict, allowed_paper_ids: set[str], method: str) -> None:
    ideas = parsed.get("ideas")
    if not isinstance(ideas, list) or len(ideas) != 3:
        raise ValueError("Expected exactly three ideas in an `ideas` list")
    if method in {"direct_prompt", "researcharena"}:
        required = {"idea_id", "title", "description", "motivation", "proposed_approach", "experiment_outline"}
    else:
        required = {"idea_id", "title", "baseline_weakness", "proposed_mechanism", "minimal_new_module", "metrics"}
    for index, idea in enumerate(ideas, 1):
        missing = sorted(required - set(idea))
        if missing:
            raise ValueError(f"Idea {index} missing fields: {missing}")
        cited = {str(value) for value in idea.get("evidence_paper_ids", []) if value}
        unknown = sorted(cited - allowed_paper_ids)
        if unknown:
            raise ValueError(f"Idea {index} cites paper_ids absent from prompt evidence: {unknown}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="aaai27/experiments/smoke_config.yaml")
    parser.add_argument("--manifest", default="aaai27/experiments/manifests/main_experiment_manifest.jsonl")
    parser.add_argument("--output-dir", default="aaai27/experiments/results/raw/smoke_seed11")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true", help="Explicitly replace an existing run directory")
    parser.add_argument(
        "--replicate-id",
        action="append",
        type=int,
        help="Run selected replicate_id values; repeat this flag as needed. Defaults to 11.",
    )
    parser.add_argument("--all-replicates", action="store_true", help="Run every replicate_id in the manifest")
    parser.add_argument(
        "--recover-existing-raw",
        action="store_true",
        help="Revalidate an existing raw response without another API call",
    )
    parser.add_argument("--run-id", action="append", help="Run only selected run_id; repeat this flag as needed")
    args = parser.parse_args()

    config = yaml.safe_load((ROOT / args.config).read_text(encoding="utf-8"))
    rows = read_jsonl(ROOT / args.manifest)
    if not args.all_replicates:
        selected_replicates = set(args.replicate_id or [11])
        rows = [
            row
            for row in rows
            if row.get("replicate_id", row.get("seed")) in selected_replicates
        ]
    if args.run_id:
        selected = set(args.run_id)
        rows = [row for row in rows if row["run_id"] in selected]
    out_root = ROOT / args.output_dir
    out_root.mkdir(parents=True, exist_ok=True)

    api = config["api"]
    generation = config["generation"]
    api_key = os.environ.get(api["api_key_env"], "")
    if not args.dry_run and not args.recover_existing_raw and not api_key:
        raise RuntimeError(f"Missing environment variable: {api['api_key_env']}")

    print(f"Planned generation runs: {len(rows)}")
    print(f"Model: {api['model']} via {api['base_url']}")
    for row in rows:
        task_cfg = config["tasks"][row["task"]]
        task_text = (ROOT / task_cfg["spec"]).read_text(encoding="utf-8")
        evidence_text, allowed_paper_ids = evidence_context(
            ROOT / task_cfg["evidence_dir"], generation["evidence_papers"], generation["evidence_abstract_chars"]
        )
        prompt = build_prompt(row["method"], task_text, evidence_text)
        run_dir = out_root / row["run_id"]
        if run_dir.exists() and args.recover_existing_raw:
            raw_path = run_dir / (
                "raw_repair.txt"
                if row["method"] in {"focused_generic_refine", "focused_full"}
                else "raw_generation.txt"
            )
            if not raw_path.exists():
                print(f"FAIL {row['run_id']}: no existing raw response to recover")
                continue
            try:
                saved_prompt_path = run_dir / "prompt.txt"
                if not saved_prompt_path.exists():
                    raise FileNotFoundError("saved prompt.txt is required for evidence-faithful recovery")
                saved_prompt = saved_prompt_path.read_text(encoding="utf-8")
                recovery_allowed_ids = set(
                    re.findall(r'"paper_id"\s*:\s*"([^"]+)"', saved_prompt)
                )
                parsed = extract_json(raw_path.read_text(encoding="utf-8"))
                validate_output(parsed, recovery_allowed_ids, row["method"])
                (run_dir / "ideas.json").write_text(
                    json.dumps(parsed, indent=2, ensure_ascii=False), encoding="utf-8"
                )
                metadata_path = run_dir / "metadata.json"
                metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else row.copy()
                previous_error = metadata.get("error")
                metadata.update(
                    {
                        "status": "success",
                        "recovered_from_existing_raw": True,
                        "previous_validation_error": previous_error,
                        "recovery_allowed_paper_ids_from_saved_prompt": len(recovery_allowed_ids),
                        "evidence_selection": "card_references_then_relevance",
                        "usage_missing_due_to_pre_validation_failure": "usage_by_call" not in metadata,
                    }
                )
                metadata.pop("error", None)
                metadata.pop("error_type", None)
                metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"RECOVERED {row['run_id']}: no API call")
            except Exception as exc:
                print(f"FAIL {row['run_id']}: recovery {type(exc).__name__}: {exc}")
            continue
        if run_dir.exists() and not args.dry_run and not args.overwrite:
            print(f"SKIP {row['run_id']}: output exists (use --overwrite or a new --output-dir)")
            continue
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
        metadata = {
            **row,
            "model": api["model"],
            "provider_base_url": api["base_url"],
            "temperature": generation["temperature"],
            "max_output_tokens_per_call": generation["max_output_tokens"],
            "evidence_mode": task_cfg["evidence_mode"],
            "prompt_chars": len(prompt),
            "dry_run": args.dry_run,
        }
        if args.dry_run:
            (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"DRY {row['run_id']}: prompt_chars={len(prompt)}")
            continue

        started = time.monotonic()
        metadata["started_at"] = datetime.now(timezone.utc).isoformat()
        try:
            refine_methods = {"focused_generic_refine", "focused_full"}
            source_metadata = None
            if row["method"] in refine_methods:
                source_run_id = row["run_id"].replace(row["method"], "focused_no_repair")
                source_dir = out_root / source_run_id
                source_ideas_path = source_dir / "ideas.json"
                source_metadata_path = source_dir / "metadata.json"
                if not source_ideas_path.exists() or not source_metadata_path.exists():
                    raise FileNotFoundError(
                        f"Paired refinement requires successful source run first: {source_run_id}"
                    )
                parsed = json.loads(source_ideas_path.read_text(encoding="utf-8"))
                validate_output(parsed, allowed_paper_ids, "focused_no_repair")
                source_metadata = json.loads(source_metadata_path.read_text(encoding="utf-8"))
                if source_metadata.get("status") != "success":
                    raise ValueError(f"Paired source run is not successful: {source_run_id}")
                usages = []
                metadata.update(
                    {
                        "paired_initial_source_run_id": source_run_id,
                        "paired_initial_ideas_sha256": hashlib.sha256(
                            source_ideas_path.read_bytes()
                        ).hexdigest(),
                        "generation_prompt_executed": False,
                        "pairing_design": "same_initial_ideas_forked_to_generic_and_targeted_refinement",
                    }
                )
            else:
                raw, usage1, retries1 = chat_completion(api, generation, api_key, prompt)
                (run_dir / "raw_generation.txt").write_text(raw, encoding="utf-8")
                parsed = extract_json(raw)
                validate_output(parsed, allowed_paper_ids, row["method"])
                usages = [usage1]
                retry_events_by_call = [retries1]
                metadata["generation_prompt_executed"] = True
            if row["method"] in refine_methods:
                refine_instruction = (
                    REPAIR_INSTRUCTION if row["method"] == "focused_full" else GENERIC_REFINE_INSTRUCTION
                )
                repair_prompt = refine_instruction + "\n\n" + evidence_text + "\n\nIDEAS:\n" + json.dumps(parsed, ensure_ascii=False)
                (run_dir / "repair_prompt.txt").write_text(repair_prompt, encoding="utf-8")
                repaired_raw, usage2, retries2 = chat_completion(api, generation, api_key, repair_prompt)
                (run_dir / "raw_repair.txt").write_text(repaired_raw, encoding="utf-8")
                parsed = extract_json(repaired_raw)
                validate_output(parsed, allowed_paper_ids, row["method"])
                usages.append(usage2)
                retry_events_by_call = [retries2]
            (run_dir / "ideas.json").write_text(json.dumps(parsed, indent=2, ensure_ascii=False), encoding="utf-8")
            metadata.update(
                {
                    "status": "success",
                    "usage_by_call": usages,
                    "retry_events_by_call": retry_events_by_call,
                    "retry_count": sum(len(events) for events in retry_events_by_call),
                }
            )
            if source_metadata is not None:
                metadata["pipeline_usage_by_call"] = source_metadata.get("usage_by_call", []) + usages
                metadata["pipeline_retry_events_by_call"] = (
                    source_metadata.get("retry_events_by_call", []) + retry_events_by_call
                )
                metadata["pipeline_wall_time_seconds"] = round(
                    float(source_metadata.get("wall_time_seconds", 0)) + (time.monotonic() - started), 3
                )
            print(f"OK  {row['run_id']}")
        except Exception as exc:
            metadata.update({"status": "failed", "error_type": type(exc).__name__, "error": str(exc)})
            if isinstance(exc, ProviderRequestError):
                metadata["retry_events_before_failure"] = exc.retry_events
                metadata["retry_count"] = len(exc.retry_events)
            print(f"FAIL {row['run_id']}: {type(exc).__name__}: {exc}")
        metadata["wall_time_seconds"] = round(time.monotonic() - started, 3)
        metadata["finished_at"] = datetime.now(timezone.utc).isoformat()
        (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
