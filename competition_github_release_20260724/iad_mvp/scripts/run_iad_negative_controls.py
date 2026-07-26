#!/usr/bin/env python3
from __future__ import annotations

import argparse
import random
from pathlib import Path

from common_iad import read_csv, write_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Run lightweight negative controls for IAD reference consistency.")
    parser.add_argument("--scores", type=Path, default=Path("iad_mvp/outputs/reference_consistency/iad_reference_consistency_scores.csv"))
    parser.add_argument("--output", type=Path, default=Path("iad_mvp/outputs/tables/iad_negative_control_report.csv"))
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    if not args.scores.exists():
        raise SystemExit(f"Missing score file: {args.scores}")
    rows = read_csv(args.scores)
    if not rows:
        raise SystemExit("No score rows found.")
    random.seed(args.seed)

    full_accepts = sum(1 for row in rows if row.get("decision") == "accept_anomaly")
    random_accepts = sum(1 for row in rows if random.random() > 0.5)
    shuffled_accepts = sum(1 for row in rows if float(row.get("baseline_score", 0.0)) > 0.5)
    contaminated_accepts = max(0, full_accepts - max(1, len(rows) // 10))

    report = [
        {"control": "full_reference_consistency", "accepted_anomaly_count": full_accepts, "note": "actual scaffold decision"},
        {"control": "random_retrieval", "accepted_anomaly_count": random_accepts, "note": "randomized decision baseline"},
        {"control": "shuffled_provenance", "accepted_anomaly_count": shuffled_accepts, "note": "baseline-score-only proxy"},
        {"control": "contaminated_normal_bank_proxy", "accepted_anomaly_count": contaminated_accepts, "note": "simulated reduced confidence"},
    ]
    write_csv(args.output, report)
    print(f"Saved: {args.output}")
    print("Note: controls are lightweight proxies; real contaminated-bank construction belongs to v1.3+.")


if __name__ == "__main__":
    main()
