#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a generic research-task smoke-test manifest.")
    parser.add_argument("--task-type", required=True)
    parser.add_argument("--research-direction", required=True)
    parser.add_argument("--idea-title", required=True)
    parser.add_argument("--idea-text", default="")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "sample_id": "generic_smoke_001",
        "task_type": args.task_type,
        "research_direction": args.research_direction,
        "idea_title": args.idea_title,
        "idea_text": args.idea_text,
        "evaluation_scope": "workflow execution smoke test; not a domain benchmark",
        "required_artifacts": [
            "baseline_scaffold_scores.csv",
            "proposed_scaffold_scores.csv",
            "generic_execution_metrics.json",
            "result_to_claim.md",
        ],
    }
    args.output.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
