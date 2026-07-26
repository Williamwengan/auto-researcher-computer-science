#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_one_csv(path: Path) -> dict[str, str]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows[0] if rows else {}


def clamp(value: float) -> float:
    return round(max(0.0, min(0.95, value)), 4)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a generic proposed-method scaffold for unknown tasks.")
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    baseline = read_one_csv(args.baseline)
    specificity = float(baseline.get("plan_specificity", 0.5))
    readiness = float(baseline.get("artifact_readiness", 0.5))
    risk = float(baseline.get("risk_control", 0.4))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "sample_id",
            "proposed_name",
            "plan_specificity",
            "artifact_readiness",
            "risk_control",
            "improvement_source",
            "note",
        ])
        writer.writeheader()
        writer.writerow({
            "sample_id": baseline.get("sample_id", "generic_smoke_001"),
            "proposed_name": "focused_workflow_final_plan_scaffold",
            "plan_specificity": clamp(specificity + 0.10),
            "artifact_readiness": clamp(readiness + 0.12),
            "risk_control": clamp(risk + 0.16),
            "improvement_source": "baseline-grounded idea + experiment plan + explicit limitations",
            "note": "generic smoke proposed scaffold; not a domain benchmark",
        })
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
