#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ARIS_TOOLS = ROOT / "aris_bridge" / "tools"
SUBMISSION = ROOT / "competition_submission"

sys.path.insert(0, str(ARIS_TOOLS))
import run_state as rs  # noqa: E402


RUN_ID = "v24_authorized_iad_executor"
DEFAULT_RUN_DIR = ROOT / "execution_runs" / RUN_ID


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ensure_run_state_schema(run_dir: Path, steps: list[dict[str, Any]]) -> None:
    """Reset only the ARIS phase-state file when the command plan changes.

    run_state.start_run is intentionally idempotent and will not clobber an
    existing resumable run. For this demo executor, however, the step list can
    change when the user passes --mvtec-root/--categories. Without this guard a
    previous 5-phase run_state can block a later 6-phase run that includes
    prepare_mvtec_split. We only remove the tiny phase-state JSON, not metrics,
    logs, datasets, or experiment artifacts.
    """
    state_path = run_dir / ".aris" / "runs" / f"{RUN_ID}.json"
    expected = [step["phase"] for step in steps]
    if not state_path.exists():
        return
    try:
        current = json.loads(state_path.read_text(encoding="utf-8"))
        existing = [phase["phase"] for phase in current.get("phases", [])]
    except Exception:
        existing = []
    if existing != expected:
        state_path.unlink()


def read_metrics(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return {}
    out: dict[str, Any] = {}
    for k, v in rows[0].items():
        if v is None:
            out[k] = v
            continue
        try:
            out[k] = float(v)
        except ValueError:
            out[k] = v
    return out


def shell_join(argv: list[str]) -> str:
    return " ".join(shlex.quote(x) for x in argv)


def build_steps(args: argparse.Namespace) -> list[dict[str, Any]]:
    split = args.split
    manifest = args.manifest
    bank_dir = args.reference_output_dir
    bank = bank_dir / "iad_reference_bank.npz"
    index = bank_dir / "iad_reference_index.jsonl"
    baseline_dir = args.baseline_output_dir
    baseline_csv = baseline_dir / "iad_baseline_scores.csv"
    scores_csv = args.reference_scores_output
    tables_dir = args.tables_output_dir
    metrics_csv = tables_dir / "iad_agent_execution_metrics.csv"

    steps: list[dict[str, Any]] = []
    if args.mvtec_root:
        categories = args.categories or ["bottle"]
        steps.append({
            "phase": "prepare_mvtec_split",
            "description": "根据 MVTec AD 根目录和类别生成 split 文件。",
            "cmd": [
                sys.executable,
                "iad_mvp/scripts/prepare_mvtec_subset.py",
                "--mvtec_root",
                str(args.mvtec_root),
                "--categories",
                *categories,
                "--output",
                str(split),
            ],
            "artifact": split,
        })

    steps.extend([
        {
            "phase": "prepare_reference_manifest",
            "description": "把 split 转成 train/test/reference manifest。",
            "cmd": [
                sys.executable,
                "iad_mvp/scripts/prepare_iad_reference_manifest.py",
                "--split",
                str(split),
                "--output",
                str(manifest),
            ],
            "artifact": manifest,
        },
        {
            "phase": "build_reference_bank",
            "description": "构建 normal reference feature bank。",
            "cmd": [
                sys.executable,
                "iad_mvp/scripts/build_reference_bank.py",
                "--manifest",
                str(manifest),
                "--output_dir",
                str(bank_dir),
            ],
            "artifact": bank,
        },
        {
            "phase": "reproduce_lightweight_baseline",
            "description": "复现 lightweight nearest-reference baseline。",
            "cmd": [
                sys.executable,
                "iad_mvp/scripts/run_iad_baselines.py",
                "--manifest",
                str(manifest),
                "--reference_bank",
                str(bank),
                "--output_dir",
                str(baseline_dir),
            ],
            "artifact": baseline_csv,
        },
        {
            "phase": "run_reference_consistency_agent",
            "description": "运行 reference-consistency scoring / agent decision。",
            "cmd": [
                sys.executable,
                "iad_mvp/scripts/score_reference_consistency.py",
                "--manifest",
                str(manifest),
                "--baseline",
                str(baseline_csv),
                "--reference_bank",
                str(bank),
                "--reference_index",
                str(index),
                "--output",
                str(scores_csv),
                "--anomaly_threshold",
                str(args.anomaly_threshold),
                "--consistency_threshold",
                str(args.consistency_threshold),
            ],
            "artifact": scores_csv,
        },
        {
            "phase": "evaluate_execution_metrics",
            "description": "汇总 IAD execution metrics。",
            "cmd": [
                sys.executable,
                "iad_mvp/scripts/evaluate_iad_agent.py",
                "--baseline",
                str(baseline_csv),
                "--scores",
                str(scores_csv),
                "--output_dir",
                str(tables_dir),
                "--threshold",
                str(args.eval_threshold),
            ],
            "artifact": metrics_csv,
        },
    ])
    return steps


def write_watchdog_state(run_dir: Path, status: str, phase: str | None, completed: int, total: int) -> None:
    write_json(run_dir / "watchdog_loop_state.json", {
        "status": status,
        "current_phase": phase,
        "updated_at": now(),
        "completed_steps": completed,
        "total_steps": total,
        "note": "Watchdog-compatible state file for Auto-claude-style monitoring.",
    })


def write_manifest(run_dir: Path, args: argparse.Namespace, steps: list[dict[str, Any]]) -> None:
    manifest = {
        "version": "v24",
        "run_id": RUN_ID,
        "created_at": now(),
        "purpose": "Authorized local experiment executor connecting ResearchArena final plans to Auto-claude-style execution control.",
        "human_authorization_required": True,
        "approved": bool(args.approve),
        "approval_note": args.approval_note or "",
        "scope": "IAD local scaffold execution only; no remote deployment; no destructive commands.",
        "paths": {
            "split": rel(args.split),
            "manifest": rel(args.manifest),
            "reference_output_dir": rel(args.reference_output_dir),
            "baseline_output_dir": rel(args.baseline_output_dir),
            "reference_scores_output": rel(args.reference_scores_output),
            "tables_output_dir": rel(args.tables_output_dir),
        },
        "steps": [
            {
                "phase": step["phase"],
                "description": step["description"],
                "command": shell_join(step["cmd"]),
                "artifact": rel(step["artifact"]),
            }
            for step in steps
        ],
    }
    write_json(run_dir / "experiment_manifest.json", manifest)


def write_command_preview(run_dir: Path, steps: list[dict[str, Any]]) -> None:
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "# This is a preview generated by V24. The Python executor requires explicit --approve.",
        "",
    ]
    for step in steps:
        lines.append(f"# {step['phase']}: {step['description']}")
        lines.append(shell_join(step["cmd"]))
        lines.append("")
    path = run_dir / "commands_preview.sh"
    path.write_text("\n".join(lines), encoding="utf-8")
    path.chmod(0o755)


def write_authorization_request(run_dir: Path, args: argparse.Namespace, steps: list[dict[str, Any]]) -> None:
    lines = [
        "# V24 授权实验执行请求",
        "",
        f"生成时间：{now()}",
        "",
        "## 目的",
        "",
        "把当前 ResearchArena workflow 生成的 IAD 研究方案，接入 Auto-claude-style 的实验执行层：先复现 lightweight baseline，再运行 reference-consistency agent，再汇总实验指标。",
        "",
        "## 为什么需要人工授权",
        "",
        "实验执行会读取数据集、生成中间文件并覆盖同名 scaffold 输出。为了避免自动系统在未经确认时消耗资源或改写结果，V24 默认只生成预览；只有显式 `--approve` 才会真正运行。",
        "",
        "## 将要执行的命令",
        "",
        "| step | phase | artifact |",
        "| ---: | --- | --- |",
    ]
    for idx, step in enumerate(steps, 1):
        lines.append(f"| {idx} | `{step['phase']}` | `{rel(step['artifact'])}` |")
    lines.extend([
        "",
        "详细命令见：`commands_preview.sh`",
        "",
        "## 授权执行命令",
        "",
        "```bash",
        "python focused_workflow/scripts/run_v24_authorized_experiment_executor.py \\",
        "  --approve \\",
        "  --approval-note \"I approve running the local IAD scaffold execution chain.\"",
        "```",
        "",
        "如果要指定 MVTec 数据和类别：",
        "",
        "```bash",
        "python focused_workflow/scripts/run_v24_authorized_experiment_executor.py \\",
        "  --mvtec-root Datasets/01_IAD/mvtec_anomaly_detection/mvtec_anomaly_detection \\",
        "  --categories bottle cable capsule \\",
        "  --approve \\",
        "  --approval-note \"I approve running the local IAD scaffold execution chain on bottle/cable/capsule.\"",
        "```",
        "",
        "## 边界",
        "",
        "- 当前执行器只接 IAD scaffold，不声称完整 PatchCore/anomalib benchmark。",
        "- 当前执行器不做远程 GPU 调度，不自动下载数据，不删除文件。",
        "- 后续可把 Auto-claude 的 experiment queue / watchdog / paper writing loop 继续接入。",
    ])
    (run_dir / "EXPERIMENT_AUTHORIZATION_REQUEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_report(run_dir: Path, args: argparse.Namespace, steps: list[dict[str, Any]], executed: bool, success: bool) -> None:
    metrics_path = args.tables_output_dir / "iad_agent_execution_metrics.csv"
    metrics = read_metrics(metrics_path)
    status = "已授权并执行完成" if executed and success else "已生成授权请求，尚未执行"
    if executed and not success:
        status = "已授权但执行失败，需查看 logs"

    metric_intro = "授权执行后生成的 metrics" if executed and success else "当前检测到已有 cached metrics；V24 本轮尚未执行时，这些只是历史 scaffold 输出"
    metric_lines = ""
    if metrics:
        metric_lines = "\n".join(f"| {k} | {v} |" for k, v in metrics.items())
    else:
        metric_lines = "| pending | 尚未生成 metrics |"

    md = f"""# V24 Authorized Experiment Executor：人工授权实验执行器

## 一句话结论

V24 将当前 ResearchArena workflow 的后半段扩展为“人工授权后执行实验”的模式：系统先生成实验命令预览和授权请求；获得授权后，自动运行 baseline reproduction、agent scoring 和 metric evaluation，并记录 run_state、日志和结果。

## 当前状态

{status}

## 接入 Auto-claude 的能力点

| Auto-claude capability | 当前接入方式 |
| --- | --- |
| baseline reproduction | 调用 `iad_mvp/scripts/run_iad_baselines.py` 复现 lightweight baseline |
| run experiment | 调用 reference-consistency agent 和 evaluation 脚本 |
| human authorization | 默认 dry-run；只有 `--approve --approval-note` 才执行 |
| resumable run state | 使用 `aris_bridge/tools/run_state.py` 记录 phase 状态 |
| monitoring hook | 输出 `watchdog_loop_state.json`，后续可被 watchdog 监控 |
| execution logs | 每个阶段写入 `logs/<phase>.log` |
| result-to-report | 自动生成本 V24 报告和 `execution_summary.json` |

## 执行阶段

| # | phase | artifact |
| ---: | --- | --- |
"""
    for idx, step in enumerate(steps, 1):
        md += f"| {idx} | `{step['phase']}` | `{rel(step['artifact'])}` |\n"
    md += f"""

## 当前 metrics

{metric_intro}

| metric | value |
| --- | --- |
{metric_lines}

## 关键产物

- 授权请求：`{rel(run_dir / "EXPERIMENT_AUTHORIZATION_REQUEST.md")}`
- 命令预览：`{rel(run_dir / "commands_preview.sh")}`
- 实验 manifest：`{rel(run_dir / "experiment_manifest.json")}`
- run_state：`{rel(run_dir / "run_state.json")}`
- watchdog state：`{rel(run_dir / "watchdog_loop_state.json")}`
- logs：`{rel(run_dir / "logs")}`
- summary：`{rel(run_dir / "execution_summary.json")}`

## Honest boundary

当前 V24 证明的是“从 idea/plan 到授权实验执行”的系统能力，不证明 IAD 算法达到 SOTA。它是把 Auto-claude 的实验执行思想接到 ResearchArena workflow 的第一版工程入口。

## 下一步扩展

1. 将 IAD scaffold 替换或并联到 PatchCore/anomalib 正式 benchmark。
2. 增加 experiment queue，支持多 seed、多 category、多 GPU。
3. 增加 result-to-claim-to-repair：失败指标自动转成 critic repair prompt。
4. 接入 paper writing loop，把 verified claims 自动转成论文实验段落。
"""
    SUBMISSION.mkdir(parents=True, exist_ok=True)
    (SUBMISSION / "V24_AUTHORIZED_EXPERIMENT_EXECUTOR_CN.md").write_text(md, encoding="utf-8")


def run_step(run_dir: Path, step: dict[str, Any], idx: int, total: int) -> tuple[bool, dict[str, Any]]:
    phase = step["phase"]
    logs_dir = run_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / f"{idx:02d}_{phase}.log"

    rs.set_status(str(run_dir), RUN_ID, phase, "running", artifact=rel(step["artifact"]))
    write_watchdog_state(run_dir, "running", phase, idx - 1, total)

    started = now()
    proc = subprocess.run(
        step["cmd"],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=1800,
    )
    ended = now()
    log_path.write_text(proc.stdout, encoding="utf-8")

    record = {
        "phase": phase,
        "command": shell_join(step["cmd"]),
        "returncode": proc.returncode,
        "started_at": started,
        "ended_at": ended,
        "log": rel(log_path),
        "artifact": rel(step["artifact"]),
    }
    if proc.returncode == 0:
        rs.set_status(str(run_dir), RUN_ID, phase, "done", artifact=rel(step["artifact"]))
        rs.accept(str(run_dir), RUN_ID, phase, verdict_id=f"exit0:{rel(log_path)}", reviewer="deterministic:subprocess_exit_code")
        write_watchdog_state(run_dir, "running", phase, idx, total)
        return True, record

    rs.set_status(str(run_dir), RUN_ID, phase, "failed", artifact=rel(log_path))
    write_watchdog_state(run_dir, "failed", phase, idx - 1, total)
    return False, record


def copy_run_state(run_dir: Path) -> None:
    src = run_dir / ".aris" / "runs" / f"{RUN_ID}.json"
    if src.exists():
        (run_dir / "run_state.json").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def execute(args: argparse.Namespace, steps: list[dict[str, Any]]) -> bool:
    if not args.approve:
        return False
    if not args.approval_note or len(args.approval_note.strip()) < 8:
        raise SystemExit("Refuse to run: --approval-note is required and must be specific.")

    run_dir = args.run_dir
    execution_records: list[dict[str, Any]] = []
    total = len(steps)
    for idx, step in enumerate(steps, 1):
        ok, record = run_step(run_dir, step, idx, total)
        execution_records.append(record)
        if not ok:
            write_json(run_dir / "execution_summary.json", {
                "version": "v24",
                "status": "failed",
                "failed_phase": step["phase"],
                "approval_note": args.approval_note,
                "records": execution_records,
                "updated_at": now(),
            })
            copy_run_state(run_dir)
            return False

    write_watchdog_state(run_dir, "complete", None, total, total)
    copy_run_state(run_dir)
    write_json(run_dir / "AUTHORIZATION_RECORD.json", {
        "approved": True,
        "approved_at": now(),
        "approval_note": args.approval_note,
        "executor": "run_v24_authorized_experiment_executor.py",
        "scope": "local IAD scaffold commands listed in experiment_manifest.json",
    })
    write_json(run_dir / "execution_summary.json", {
        "version": "v24",
        "status": "success",
        "approval_note": args.approval_note,
        "metrics": read_metrics(args.tables_output_dir / "iad_agent_execution_metrics.csv"),
        "records": execution_records,
        "updated_at": now(),
    })
    return True


def print_status(run_dir: Path) -> None:
    print(f"run_dir: {run_dir}")
    for path in [
        run_dir / "EXPERIMENT_AUTHORIZATION_REQUEST.md",
        run_dir / "experiment_manifest.json",
        run_dir / "run_state.json",
        run_dir / "watchdog_loop_state.json",
        run_dir / "execution_summary.json",
    ]:
        print(f"{'FOUND' if path.exists() else 'MISS '} {rel(path)}")
    state = run_dir / "run_state.json"
    if state.exists():
        print(state.read_text(encoding="utf-8")[:4000])


def main() -> None:
    parser = argparse.ArgumentParser(description="V24 authorized local experiment executor for the IAD workflow.")
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--mvtec-root", type=Path, default=None)
    parser.add_argument("--categories", nargs="+", default=None)
    parser.add_argument("--split", type=Path, default=Path("iad_mvp/data/mvtec_split.json"))
    parser.add_argument("--manifest", type=Path, default=Path("iad_mvp/data/iad_reference_manifest.jsonl"))
    parser.add_argument("--reference-output-dir", type=Path, default=Path("iad_mvp/data"))
    parser.add_argument("--baseline-output-dir", type=Path, default=Path("iad_mvp/outputs/patchcore_baseline"))
    parser.add_argument("--reference-scores-output", type=Path, default=Path("iad_mvp/outputs/reference_consistency/iad_reference_consistency_scores.csv"))
    parser.add_argument("--tables-output-dir", type=Path, default=Path("iad_mvp/outputs/tables"))
    parser.add_argument("--anomaly-threshold", type=float, default=0.5)
    parser.add_argument("--consistency-threshold", type=float, default=0.55)
    parser.add_argument("--eval-threshold", type=float, default=0.5)
    parser.add_argument("--approve", action="store_true", help="Actually run commands. Without this flag, only writes authorization materials.")
    parser.add_argument("--approval-note", default="", help="Human approval record required when --approve is used.")
    parser.add_argument("--status", action="store_true", help="Print current V24 run status and exit.")
    args = parser.parse_args()

    if args.status:
        print_status(args.run_dir)
        return

    args.run_dir.mkdir(parents=True, exist_ok=True)
    steps = build_steps(args)
    write_manifest(args.run_dir, args, steps)
    write_command_preview(args.run_dir, steps)
    write_authorization_request(args.run_dir, args, steps)
    ensure_run_state_schema(args.run_dir, steps)
    rs.start_run(str(args.run_dir), RUN_ID, [step["phase"] for step in steps])
    write_watchdog_state(args.run_dir, "awaiting_approval" if not args.approve else "starting", None, 0, len(steps))

    success = False
    executed = False
    if args.approve:
        executed = True
        success = execute(args, steps)
    else:
        write_json(args.run_dir / "execution_summary.json", {
            "version": "v24",
            "status": "awaiting_approval",
            "message": "Authorization materials generated. Re-run with --approve and --approval-note to execute.",
            "updated_at": now(),
        })
        copy_run_state(args.run_dir)

    write_report(args.run_dir, args, steps, executed=executed, success=success)
    print(f"Wrote {args.run_dir / 'EXPERIMENT_AUTHORIZATION_REQUEST.md'}")
    print(f"Wrote {args.run_dir / 'commands_preview.sh'}")
    print(f"Wrote {args.run_dir / 'experiment_manifest.json'}")
    print(f"Wrote {args.run_dir / 'execution_summary.json'}")
    print(f"Wrote {SUBMISSION / 'V24_AUTHORIZED_EXPERIMENT_EXECUTOR_CN.md'}")
    if args.approve:
        print(f"Execution status: {'success' if success else 'failed'}")
        if not success:
            raise SystemExit(1)
    else:
        print("Execution status: awaiting human approval")


if __name__ == "__main__":
    main()
