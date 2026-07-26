#!/usr/bin/env python3
"""Execute the only generation-requiring AAAI-27 ablation: no evidence.

Each manifest row is one paired pipeline with two calls: focused generation
without paper evidence, followed by consistency-aware repair without paper
evidence. Existing successful initial calls are resumed rather than repeated.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

from run_generation_smoke_test import (
    FOCUSED_OUTPUT,
    ROOT,
    chat_completion,
    extract_json,
    read_jsonl,
    validate_output,
)


NO_EVIDENCE_CONTEXT = """NO PAPER EVIDENCE IS PROVIDED IN THIS ABLATION.
Use only the task specification and general research reasoning. Do not invent,
cite, or reconstruct paper IDs. Every idea must set evidence_paper_ids to [].
"""

INITIAL_INSTRUCTION = """Generate focused ideas. Each idea must bind one concrete baseline weakness to one minimal new
mechanism and a falsifiable experiment. Avoid tool-stack novelty and mechanism mismatch. Because this is the no-evidence
ablation, do not rely on supplied papers or claim that a specific paper establishes a weakness.
"""

REPAIR_INSTRUCTION = """You are the consistency-aware repair stage. Repair vague mechanisms, task-domain mismatch,
missing negative controls, and implementation ambiguity. Preserve each idea's identity and do not copy a loss/module
between ideas unless logically required. This is the no-evidence ablation: do not add citations, paper IDs, paper-specific
claims, or evidence-verification language. Keep evidence_paper_ids as empty lists. Return exactly three ideas in the same
JSON schema. JSON only.
"""


def validate_no_evidence(parsed: dict) -> None:
    validate_output(parsed, set(), "focused_full")
    for index, idea in enumerate(parsed["ideas"], 1):
        if idea.get("evidence_paper_ids") not in ([], None):
            raise ValueError(f"Idea {index} must have empty evidence_paper_ids in no-evidence ablation")


def sum_tokens(usages: list[dict]) -> dict:
    return {
        key: sum(int(x.get(key, 0) or 0) for x in usages)
        for key in ("prompt_tokens", "completion_tokens", "total_tokens")
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="aaai27/experiments/smoke_config.yaml")
    parser.add_argument("--manifest", default="aaai27/experiments/manifests/ablation_execution_manifest_v2.jsonl")
    parser.add_argument("--output-dir", default="aaai27/experiments/results/raw/ablation_no_evidence_v2")
    parser.add_argument("--run-id", action="append")
    parser.add_argument("--replicate-id", action="append", type=int)
    parser.add_argument("--all-runs", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config = yaml.safe_load((ROOT / args.config).read_text(encoding="utf-8"))
    rows = read_jsonl(ROOT / args.manifest)
    if args.run_id:
        wanted = set(args.run_id); rows = [x for x in rows if x["run_id"] in wanted]
    elif args.replicate_id:
        wanted = set(args.replicate_id); rows = [x for x in rows if x["replicate_id"] in wanted]
    elif not args.all_runs:
        rows = [x for x in rows if x["run_id"] == "physical_focused_full_no_evidence_s11"]
    if not rows:
        raise ValueError("No ablation rows selected")

    api, generation = config["api"], config["generation"]
    api_key = os.environ.get(api["api_key_env"], "")
    if not args.dry_run and not api_key:
        raise RuntimeError(f"Missing environment variable: {api['api_key_env']}")
    out_root = ROOT / args.output_dir
    out_root.mkdir(parents=True, exist_ok=True)
    print(f"Planned no-evidence pipelines: {len(rows)} (2 calls each unless resumed)")
    print(f"Model: {api['model']} via {api['base_url']}")

    for row in rows:
        task_cfg = config["tasks"][row["task"]]
        task_text = (ROOT / task_cfg["spec"]).read_text(encoding="utf-8")
        initial_prompt = (
            "TASK SPECIFICATION:\n" + task_text + "\n\n" + NO_EVIDENCE_CONTEXT
            + "\nMETHOD INSTRUCTION:\n" + INITIAL_INSTRUCTION + "\n" + FOCUSED_OUTPUT
        )
        # FOCUSED_OUTPUT mentions the generic phrase "supplied evidence" but
        # contains no evidence records. The explicit ablation instruction wins.
        run_dir = out_root / row["run_id"]
        metadata_path = run_dir / "metadata.json"
        if metadata_path.exists():
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            if metadata.get("status") == "success":
                print(f"SKIP {row['run_id']}: successful output exists")
                continue
        if args.dry_run:
            forbidden = ('"paper_id":', "EVIDENCE BASELINE CARDS", "PAPERS (shared across methods)")
            print(
                f"DRY {row['run_id']}: initial_prompt_chars={len(initial_prompt)}, "
                f"forbidden_evidence_markers={sum(initial_prompt.count(x) for x in forbidden)}"
            )
            continue
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "initial_prompt.txt").write_text(initial_prompt, encoding="utf-8")
        started = time.monotonic()
        metadata = {
            **row, "model": api["model"], "provider_base_url": api["base_url"],
            "temperature": generation["temperature"], "max_output_tokens_per_call": generation["max_output_tokens"],
            "evidence_mode": "none_ablation", "paper_evidence_records_in_prompt": 0,
            "expected_calls": 2, "started_at": datetime.now(timezone.utc).isoformat(),
        }
        usages, retry_events = [], []
        try:
            initial_path = run_dir / "initial_ideas.json"
            initial_call_record_path = run_dir / "initial_call_record.json"
            if initial_path.exists():
                initial = json.loads(initial_path.read_text(encoding="utf-8"))
                validate_no_evidence(initial)
                if not initial_call_record_path.exists():
                    raise FileNotFoundError("initial_call_record.json is required to resume with complete cost accounting")
                initial_record = json.loads(initial_call_record_path.read_text(encoding="utf-8"))
                metadata["initial_generation_resumed"] = True
            else:
                raw, usage, retries = chat_completion(api, generation, api_key, initial_prompt)
                (run_dir / "raw_initial.txt").write_text(raw, encoding="utf-8")
                initial = extract_json(raw); validate_no_evidence(initial)
                initial_path.write_text(json.dumps(initial, ensure_ascii=False, indent=2), encoding="utf-8")
                initial_record = {"usage": usage, "retry_events": retries}
                initial_call_record_path.write_text(
                    json.dumps(initial_record, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                usages.append(usage); retry_events.append(retries)
                metadata["initial_generation_resumed"] = False

            initial_sha = hashlib.sha256(initial_path.read_bytes()).hexdigest()
            repair_prompt = REPAIR_INSTRUCTION + "\n\n" + NO_EVIDENCE_CONTEXT + "\nIDEAS:\n" + json.dumps(initial, ensure_ascii=False)
            (run_dir / "repair_prompt.txt").write_text(repair_prompt, encoding="utf-8")
            raw, usage, retries = chat_completion(api, generation, api_key, repair_prompt)
            (run_dir / "raw_repair.txt").write_text(raw, encoding="utf-8")
            repaired = extract_json(raw); validate_no_evidence(repaired)
            (run_dir / "ideas.json").write_text(json.dumps(repaired, ensure_ascii=False, indent=2), encoding="utf-8")
            repair_record = {"usage": usage, "retry_events": retries}
            (run_dir / "repair_call_record.json").write_text(
                json.dumps(repair_record, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            usages.append(usage); retry_events.append(retries)
            pipeline_usages = [initial_record["usage"], repair_record["usage"]]
            pipeline_retries = [initial_record.get("retry_events", []), repair_record.get("retry_events", [])]
            metadata.update({
                "status": "success", "paired_initial_ideas_sha256": initial_sha,
                "usage_by_calls_executed_this_attempt": usages,
                "usage_this_attempt": sum_tokens(usages),
                "retry_events_by_calls_executed_this_attempt": retry_events,
                "pipeline_usage_by_call": pipeline_usages,
                "pipeline_usage": sum_tokens(pipeline_usages),
                "pipeline_retry_events_by_call": pipeline_retries,
                "pipeline_retry_count": sum(len(x) for x in pipeline_retries),
                "repair_used_paper_evidence": False,
            })
            print(f"OK  {row['run_id']}")
        except Exception as exc:
            metadata.update({
                "status": "failed", "error_type": type(exc).__name__, "error": str(exc),
                "usage_by_calls_executed_this_attempt": usages,
                "usage_this_attempt": sum_tokens(usages),
                "retry_events_by_calls_executed_this_attempt": retry_events,
            })
            print(f"FAIL {row['run_id']}: {type(exc).__name__}: {exc}")
        metadata["wall_time_seconds_this_attempt"] = round(time.monotonic() - started, 3)
        metadata["finished_at"] = datetime.now(timezone.utc).isoformat()
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
