#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def bounded_score(text: str, base: float) -> float:
    bonus = min(0.12, len(text.strip()) / 5000.0)
    return round(min(0.82, base + bonus), 4)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a generic baseline scaffold for unknown research tasks.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    record = json.loads(args.manifest.read_text(encoding="utf-8").splitlines()[0])
    text = " ".join([
        record.get("task_type", ""),
        record.get("research_direction", ""),
        record.get("idea_text", ""),
    ])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "sample_id",
            "baseline_name",
            "plan_specificity",
            "artifact_readiness",
            "risk_control",
            "note",
        ])
        writer.writeheader()
        writer.writerow({
            "sample_id": record["sample_id"],
            "baseline_name": "direct_prompt_plan_scaffold",
            "plan_specificity": bounded_score(text, 0.52),
            "artifact_readiness": bounded_score(text, 0.48),
            "risk_control": 0.42,
            "note": "generic smoke baseline; not a domain benchmark",
        })
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
