#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import http.server
import os
import socket
import socketserver
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


DEFAULT_PORT = 8765
ROOT = Path(__file__).resolve().parent


def find_project_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "focused_workflow").exists() and (candidate / "aris_bridge").exists():
            return candidate
    # Final submission layout: demo_assets lives under competition_final_submission_*/03_demo_video.
    for candidate in [start, *start.parents]:
        maybe = candidate.parent if candidate.name.startswith("competition_final_submission") else candidate
        if (maybe / "focused_workflow").exists() and (maybe / "aris_bridge").exists():
            return maybe
    raise RuntimeError(
        "Cannot locate project root. Please run this server inside ResearchArena-main "
        "or use the packaged competition directory with focused_workflow/ and aris_bridge/ available."
    )


PROJECT_ROOT = find_project_root(ROOT)
V24_SCRIPT = PROJECT_ROOT / "focused_workflow/scripts/run_v24_authorized_experiment_executor.py"
V24_RUN_DIR = PROJECT_ROOT / "execution_runs/v24_authorized_iad_executor"
GENERIC_RUN_DIR = PROJECT_ROOT / "execution_runs/generic_research_smoke_runner"
V27_SCRIPT = PROJECT_ROOT / "focused_workflow/scripts/run_live_workflow_backend_v27.py"
RESEARCH_AGENT_SCRIPT = PROJECT_ROOT / "research_agent_orchestrator/orchestrator.py"
RESEARCH_AGENT_STATUS = PROJECT_ROOT / "execution_runs/research_agent_orchestrator/latest_custom_status.json"
LIVE_RUN_ROOT = PROJECT_ROOT / "execution_runs/live_workflow_backend"
LIVE_JOBS: dict[str, subprocess.Popen] = {}
DEMO_KEY_ENV_VARS = ("AI4S_DEMO_API_KEY", "ESTELLE_CLAUDE_API_KEY", "ESTELLE_API_KEY", "YUNWU_API_KEY")


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def has_server_demo_key() -> bool:
    return any(bool(os.getenv(name)) for name in DEMO_KEY_ENV_VARS)


def get_server_demo_key() -> str:
    for name in DEMO_KEY_ENV_VARS:
        value = os.getenv(name)
        if value:
            value = value.strip().strip("'\"")
            try:
                value.encode("latin-1")
            except UnicodeEncodeError:
                continue
            return value
    return ""


def tail_text(path: Path, limit: int = 12000) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    return text[-limit:]


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def safe_project_path(raw: str, default_rel: str) -> tuple[Path, str]:
    rel = (raw or default_rel).strip() or default_rel
    rel = rel.replace("\\", "/").lstrip("/")
    candidate = (PROJECT_ROOT / rel).resolve()
    root = PROJECT_ROOT.resolve()
    if not str(candidate).startswith(str(root)):
        raise ValueError(f"path escapes project root: {raw}")
    return candidate, str(candidate.relative_to(root))


def infer_bridge_workspace(task_type: str, direction: str) -> str:
    key = safe_task_key(f"{task_type} {direction}")
    if key == "iad":
        return "outputs/auto_claude_execution_bridge_v1/iad_agent"
    if key == "indoor3d":
        return "outputs/auto_claude_execution_bridge_v1/indoor3d_scene"
    if key == "physical":
        return "outputs/auto_claude_execution_bridge_v1/physical_property"
    return "outputs/auto_claude_execution_bridge_v1/custom_task"


def resolve_dataset_path(raw: str) -> Path | None:
    value = (raw or "").strip()
    if not value:
        return None
    path = Path(value)
    candidates = [path] if path.is_absolute() else [
        PROJECT_ROOT / value,
        PROJECT_ROOT.parent / value,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return None


def build_aris_prompt(payload: dict, workspace_rel: str, config_rel: str) -> str:
    task_type = str(payload.get("task_type", "")).strip()
    direction = str(payload.get("research_direction", "")).strip()
    idea_title = str(payload.get("idea_title", "")).strip()
    idea_text = str(payload.get("idea_text", "")).strip()
    module = str(payload.get("module", "")).strip()
    dataset_path = str(payload.get("dataset_path", "")).strip()
    llm_model = str(payload.get("llm_model", "")).strip()
    llm_base_url = str(payload.get("llm_base_url", "")).strip()
    execution_mode = str(payload.get("execution_mode", "plan_only")).strip()
    baselines = payload.get("baselines") or []
    datasets = payload.get("datasets") or []
    metrics = payload.get("metrics") or []

    def bullet(values) -> str:
        if not values:
            return "- 未提供；请从 final plan / EXPERIMENT_PLAN.md 中读取。"
        return "\n".join(f"- {x}" for x in values)

    return f"""# Auto-claude / ARIS 实验代理接管提示词

你现在接管一个已经由 ResearchArena / Focused Workflow 生成并筛选过的科研方案。你的职责不是重新空泛地产生 idea，而是进入实验执行阶段：读方案、查数据、复现 baseline、运行 proposed module、分析结果、把结果映射为可信 claim，并生成论文草稿。

## 0. 项目位置

- ResearchArena 项目根目录：`{PROJECT_ROOT}`
- Auto-claude / ARIS 项目根目录：`/data1/huangyuling/-A_HYL/AI4S/Auto-claude-code-research-in-sleep-main`
- 当前实验 workspace：`{workspace_rel}`
- 本次运行配置：`{config_rel}`

## 1. 当前科研任务

- 具体任务类型：{task_type}
- 研究方向：{direction}
- 执行模式：{execution_mode}
- 数据集路径：`{dataset_path or '用户尚未指定；请先询问或检查 workspace 中的计划。'}`
- 大模型：{llm_model}
- API Base URL：{llm_base_url}

## 2. Focused Workflow 最终 Idea

Title: {idea_title}

核心 idea:
{idea_text}

最小新增模块:
{module or '请从 focused_final_plan.json 或 refine-logs/EXPERIMENT_PLAN.md 中读取。'}

## 3. 已知 baseline / 数据集 / 指标

Baselines:
{bullet(baselines)}

Datasets:
{bullet(datasets)}

Metrics:
{bullet(metrics)}

## 4. 请按 Auto-claude / ARIS 的实验阶段执行

1. 先读取 workspace 内这些文件：
   - `focused_final_plan.json`
   - `RESEARCH_BRIEF.md`
   - `AUTHORIZED_CLAUDE_PROMPT.md`
   - `refine-logs/EXPERIMENT_PLAN.md`
   - `AGENTS.md`
   - `CLAUDE.md`
2. 使用 Auto-claude / ARIS 的实验能力继续：
   - `/experiment-bridge refine-logs/EXPERIMENT_PLAN.md`
   - `/run-experiment`
   - `/analyze-results`
   - `/result-to-claim`
   - 最后生成 `paper_draft.md` 或 `paper.tex`
3. 如果数据集缺失，先停止并向用户请求上传或填写路径。
4. 如果需要下载数据、安装依赖、写入大量文件、调用 API、启动 GPU 或长时间运行实验，必须先向用户明确申请授权。
5. 不允许伪造实验结果；没有真实执行过的结果只能写成 planned / pending。
6. 每次实验后必须保存：
   - `run_state.json`
   - `execution_log.md`
   - `metrics_summary.csv/json`
   - `result_to_claim.md`

## 5. 本轮目标

把最终 idea 转化为可执行实验，而不是继续做静态展示。如果无法完成 full run，至少完成 sanity test、失败诊断和下一步 runner 计划。
"""


def run_iad_scaffold(dataset_path: str, execution_mode: str, approval_note: str) -> dict:
    """Run the fixed allowlisted IAD scaffold; never executes arbitrary user commands."""
    categories = ["bottle"] if execution_mode == "sanity" else ["bottle", "cable", "capsule"]
    mvtec_root = resolve_dataset_path(dataset_path) or resolve_dataset_path("Datasets/01_IAD/mvtec_anomaly_detection/mvtec_anomaly_detection")
    if not mvtec_root or not mvtec_root.exists():
        return {
            "executed": False,
            "status": "missing_dataset",
            "error": "MVTec AD dataset path not found. Please upload dataset or set an absolute dataset_path.",
            "dataset_path": dataset_path,
        }
    cmd = [
        sys.executable,
        str(V24_SCRIPT),
        "--approve",
        "--approval-note",
        approval_note,
        "--mvtec-root",
        str(mvtec_root),
        "--categories",
        *categories,
    ]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=1800,
        )
    except subprocess.TimeoutExpired:
        return {
            "executed": True,
            "status": "timeout",
            "error": "V24 executor timed out after 1800 seconds.",
        }
    return {
        "executed": True,
        "returncode": proc.returncode,
        "run_dir": str(V24_RUN_DIR.relative_to(PROJECT_ROOT)),
        "summary": read_json(V24_RUN_DIR / "execution_summary.json"),
        "watchdog": read_json(V24_RUN_DIR / "watchdog_loop_state.json"),
        "stdout_tail": proc.stdout[-8000:],
    }


def run_generic_scaffold(task_type: str, direction: str, idea_title: str, idea_text: str) -> dict:
    """Run a generic smoke-test runner for unfamiliar research tasks.

    This completes the same execution interface as a real runner but explicitly
    labels outputs as smoke-test artifacts, not domain benchmark evidence.
    """
    run_dir = GENERIC_RUN_DIR
    data_dir = run_dir / "data"
    out_dir = run_dir / "outputs"
    manifest = data_dir / "generic_manifest.jsonl"
    baseline = out_dir / "baseline_scaffold_scores.csv"
    proposed = out_dir / "proposed_scaffold_scores.csv"
    metrics_json = out_dir / "generic_execution_metrics.json"
    metrics_csv = out_dir / "generic_execution_metrics.csv"
    claim = out_dir / "result_to_claim.md"
    steps = [
        [
            sys.executable,
            "generic_mvp/scripts/prepare_generic_manifest.py",
            "--task-type", task_type,
            "--research-direction", direction,
            "--idea-title", idea_title,
            "--idea-text", idea_text,
            "--output", str(manifest),
        ],
        [
            sys.executable,
            "generic_mvp/scripts/run_generic_baseline.py",
            "--manifest", str(manifest),
            "--output", str(baseline),
        ],
        [
            sys.executable,
            "generic_mvp/scripts/run_generic_proposed.py",
            "--baseline", str(baseline),
            "--output", str(proposed),
        ],
        [
            sys.executable,
            "generic_mvp/scripts/evaluate_generic.py",
            "--baseline", str(baseline),
            "--proposed", str(proposed),
            "--output-json", str(metrics_json),
            "--output-csv", str(metrics_csv),
        ],
        [
            sys.executable,
            "generic_mvp/scripts/parse_generic_result_to_claim.py",
            "--metrics", str(metrics_json),
            "--output", str(claim),
        ],
    ]
    run_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for idx, cmd in enumerate(steps, 1):
        started = time.strftime("%Y-%m-%d %H:%M:%S")
        proc = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=180,
        )
        log_path = run_dir / "logs" / f"{idx:02d}_{Path(cmd[1]).stem}.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(proc.stdout or "", encoding="utf-8")
        records.append({
            "step": Path(cmd[1]).stem,
            "command": " ".join(cmd),
            "returncode": proc.returncode,
            "started_at": started,
            "ended_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "log": str(log_path.relative_to(PROJECT_ROOT)),
        })
        if proc.returncode != 0:
            summary = {
                "status": "failed",
                "failed_step": Path(cmd[1]).stem,
                "records": records,
                "scope": "generic smoke test; not a domain benchmark",
            }
            write_json(run_dir / "execution_summary.json", summary)
            return {"executed": True, "returncode": proc.returncode, "run_dir": str(run_dir.relative_to(PROJECT_ROOT)), "summary": summary}
    metrics = read_json(metrics_json)
    summary = {
        "status": "success",
        "scope": "generic smoke test; not a domain benchmark",
        "metrics": metrics,
        "records": records,
        "artifacts": {
            "manifest": str(manifest.relative_to(PROJECT_ROOT)),
            "baseline": str(baseline.relative_to(PROJECT_ROOT)),
            "proposed": str(proposed.relative_to(PROJECT_ROOT)),
            "metrics_json": str(metrics_json.relative_to(PROJECT_ROOT)),
            "metrics_csv": str(metrics_csv.relative_to(PROJECT_ROOT)),
            "result_to_claim": str(claim.relative_to(PROJECT_ROOT)),
        },
    }
    write_json(run_dir / "execution_summary.json", summary)
    return {"executed": True, "returncode": 0, "run_dir": str(run_dir.relative_to(PROJECT_ROOT)), "summary": summary}


def run_research_agent_runner_scaffold(task_type: str, direction: str, task_mode: str) -> dict:
    """Run the task-specific smoke runner generated by ResearchAgentOrchestrator."""
    if not RESEARCH_AGENT_SCRIPT.exists():
        return {
            "executed": False,
            "status": "missing_research_agent",
            "error": f"missing script: {RESEARCH_AGENT_SCRIPT}",
        }

    orch_cmd = [
        sys.executable,
        str(RESEARCH_AGENT_SCRIPT),
        "--task-type", task_type or "自定义科研任务",
        "--research-direction", direction or "用户输入的研究方向",
        "--task-mode", task_mode or "incremental_improvement",
        "--result-json", str(RESEARCH_AGENT_STATUS),
    ]
    try:
        orch = subprocess.run(
            orch_cmd,
            cwd=str(PROJECT_ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=90,
        )
    except subprocess.TimeoutExpired:
        return {
            "executed": False,
            "status": "orchestrator_timeout",
            "error": "ResearchAgentOrchestrator timed out after 90 seconds.",
        }
    if orch.returncode != 0:
        return {
            "executed": False,
            "status": "orchestrator_failed",
            "returncode": orch.returncode,
            "stdout_tail": orch.stdout[-8000:],
        }

    status = read_json(RESEARCH_AGENT_STATUS)
    runner_rel = ((status.get("artifacts") or {}).get("runner_scaffold") or "").strip()
    if not runner_rel:
        return {"executed": False, "status": "missing_runner_scaffold", "agent_status": status}

    runner_dir, runner_rel_safe = safe_project_path(runner_rel, runner_rel)
    if not (runner_dir / "run_all.sh").exists():
        return {
            "executed": False,
            "status": "missing_run_all",
            "runner_dir": runner_rel_safe,
            "agent_status": status,
        }

    try:
        proc = subprocess.run(
            ["bash", "run_all.sh"],
            cwd=str(runner_dir),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return {
            "executed": True,
            "status": "runner_timeout",
            "runner_dir": runner_rel_safe,
            "agent_status": status,
        }

    metrics_path = runner_dir.parent / "outputs/execution_metrics.json"
    claim_path = runner_dir.parent / "outputs/result_to_claim.md"
    metrics_payload = read_json(metrics_path)
    metrics = metrics_payload.get("metrics", metrics_payload)
    return {
        "executed": True,
        "returncode": proc.returncode,
        "status": "success" if proc.returncode == 0 else "failed",
        "run_dir": str(runner_dir.parent.relative_to(PROJECT_ROOT)),
        "runner_dir": runner_rel_safe,
        "agent_status": status,
        "summary": {"status": "success" if proc.returncode == 0 else "failed", "metrics": metrics},
        "metrics": metrics,
        "result_to_claim": str(claim_path.relative_to(PROJECT_ROOT)) if claim_path.exists() else "",
        "stdout_tail": proc.stdout[-8000:],
    }


def metrics_table_text(summary: dict) -> str:
    metrics = summary.get("metrics") or {}
    if not metrics:
        return "暂未发现 metrics。请先授权运行 sanity/full scaffold。"
    lines = ["| metric | value |", "| --- | ---: |"]
    for key, value in metrics.items():
        lines.append(f"| {key} | {value} |")
    return "\n".join(lines)


def write_result_to_claim(workspace: Path, task_type: str, idea_title: str) -> tuple[Path, str]:
    summary = read_json(V24_RUN_DIR / "execution_summary.json")
    status = summary.get("status", "unknown")
    metrics = summary.get("metrics") or {}
    text = f"""# Result-to-Claim Report

Task: {task_type}

Idea: {idea_title}

## Evidence files

- `{V24_RUN_DIR.relative_to(PROJECT_ROOT) / 'execution_summary.json'}`
- `{V24_RUN_DIR.relative_to(PROJECT_ROOT) / 'run_state.json'}`
- `{V24_RUN_DIR.relative_to(PROJECT_ROOT) / 'watchdog_loop_state.json'}`

## Claims

1. **Supported:** The final idea can be connected to a real-data IAD execution scaffold.
   - Evidence: executor status = `{status}`.
   - Tool success rate = `{metrics.get('tool_success_rate', 'N/A')}`.

2. **Supported as scaffold only:** The pipeline can prepare MVTec split, build a normal reference bank, reproduce a lightweight nearest-reference baseline, run reference-consistency scoring, and summarize metrics.
   - Evidence: `execution_summary.json` records phase-level return codes and artifacts.

3. **Not claimed:** This is not a full PatchCore/anomalib SOTA benchmark.
   - Reason: metrics note = `{metrics.get('note', 'N/A')}`.

## Metric snapshot

{metrics_table_text(summary)}
"""
    path = workspace / "result_to_claim.md"
    path.write_text(text, encoding="utf-8")
    return path, text


def write_paper_draft(workspace: Path, task_type: str, direction: str, idea_title: str, idea_text: str) -> tuple[Path, str]:
    summary = read_json(V24_RUN_DIR / "execution_summary.json")
    text = f"""# Paper Draft

## Title

{idea_title}: Evidence-Grounded Idea Generation with Authorized Execution Feedback

## Abstract

We present an AI4S research-agent workflow that connects task-conditioned literature evidence retrieval, baseline weakness analysis, fine-grained idea generation, multi-model review, critic repair, reference-claim verification, and authorized experiment execution. Given a research task, the system produces a focused research idea and translates it into an Auto-claude/ARIS-compatible execution workspace. In the IAD case study, the web agent further runs an allowlisted sanity scaffold on MVTec AD, records phase-level execution state, and maps results back to supportable claims.

## Task

- Task type: {task_type}
- Research direction: {direction}

## Final Idea

{idea_text}

## Execution Evidence

{metrics_table_text(summary)}

## Limitations

The current executable demo supports a fixed allowlisted IAD scaffold. Other tasks are routed to an ARIS execution plan unless a task-specific dataset manifest, baseline runner, proposed-module runner, and metric parser are configured. We do not claim full SOTA benchmark results from the lightweight scaffold.
"""
    path = workspace / "paper_draft.md"
    path.write_text(text, encoding="utf-8")
    return path, text


def call_openai_compatible_chat(
    *,
    base_url: str,
    api_key: str,
    model: str,
    system_prompt: str,
    user_message: str,
    timeout: int = 120,
) -> dict:
    if not api_key:
        return {
            "ok": False,
            "error": "No API key available. Set AI4S_DEMO_API_KEY on the server or input a temporary key in the page.",
        }
    root = (base_url or "https://estellecode.com/v1").rstrip("/")
    url = root if root.endswith("/chat/completions") else f"{root}/chat/completions"
    body = {
        "model": model or "claude-sonnet-4-6",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.2,
        "max_tokens": 1800,
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1200]
        return {"ok": False, "error": f"HTTP {exc.code} from model provider: {detail}"}
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

    try:
        content = data["choices"][0]["message"]["content"]
    except Exception:
        content = json.dumps(data, ensure_ascii=False)[:4000]
    return {
        "ok": True,
        "reply": content,
        "usage": data.get("usage", {}),
        "provider_response_id": data.get("id", ""),
    }


def safe_task_key(raw: str) -> str:
    value = raw.strip().lower()
    aliases = {
        "物理属性预测": "physical",
        "physical": "physical",
        "material": "physical",
        "室内单图 3d 场景生成": "indoor3d",
        "室内3d": "indoor3d",
        "indoor3d": "indoor3d",
        "iad": "iad",
        "工业异常检测 iad + agent": "iad",
        "工业异常检测": "iad",
    }
    if value in aliases:
        return aliases[value]
    if "物理" in value or "material" in value or "property" in value:
        return "physical"
    if "室内" in value or "3d" in value or "scene" in value:
        return "indoor3d"
    if "iad" in value or "异常" in value or "anomaly" in value:
        return "iad"
    if "custom" in value or "自定义" in value:
        return "custom"
    return "custom"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/demo_config":
            self._send_json(200, {
                "ok": True,
                "has_demo_key": has_server_demo_key(),
                "api_key_mode": "server_env" if has_server_demo_key() else "user_input_required",
                "message": "Demo key is stored server-side only and is never returned to the browser.",
            })
            return
        if self.path == "/api/execution/status":
            summary = read_json(V24_RUN_DIR / "execution_summary.json")
            watchdog = read_json(V24_RUN_DIR / "watchdog_loop_state.json")
            run_state = read_json(V24_RUN_DIR / "run_state.json")
            self._send_json(200, {
                "ok": True,
                "summary": summary,
                "watchdog": watchdog,
                "run_state": run_state,
                "run_dir": str(V24_RUN_DIR.relative_to(PROJECT_ROOT)),
            })
            return
        if parsed.path == "/api/live_workflow/status":
            query = urllib.parse.parse_qs(parsed.query)
            job_id = (query.get("job_id") or [""])[0]
            if not job_id or "/" in job_id or ".." in job_id:
                self._send_json(400, {"ok": False, "error": "invalid job_id"})
                return
            run_dir = LIVE_RUN_ROOT / job_id
            proc = LIVE_JOBS.get(job_id)
            returncode = proc.poll() if proc else None
            if proc and returncode is not None:
                LIVE_JOBS.pop(job_id, None)
            result = read_json(run_dir / "LIVE_WORKFLOW_RESULT.json")
            status = "running" if proc and returncode is None else ("finished" if result else "unknown")
            if returncode not in (None, 0):
                status = "failed"
            self._send_json(200, {
                "ok": status in ("running", "finished"),
                "job_id": job_id,
                "status": status,
                "returncode": returncode,
                "run_dir": str(run_dir.relative_to(PROJECT_ROOT)) if run_dir.exists() else "",
                "log_tail": tail_text(run_dir / "workflow_stdout.log"),
                "result": result,
                "result_markdown": tail_text(run_dir / "LIVE_WORKFLOW_RESULT.md", limit=30000),
            })
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/api/aris/chat":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(min(length, 128_000)).decode("utf-8")
                payload = json.loads(raw or "{}")
            except Exception as exc:
                self._send_json(400, {"ok": False, "error": f"invalid JSON: {exc}"})
                return

            task_type = str(payload.get("task_type", "")).strip()
            direction = str(payload.get("research_direction", "")).strip()
            message = str(payload.get("message", "")).strip()
            execution_mode = str(payload.get("execution_mode", "sanity")).strip() or "sanity"
            dataset_path = str(payload.get("dataset_path", "")).strip()
            idea_title = str(payload.get("idea_title", "")).strip() or "Focused Workflow Final Idea"
            idea_text = str(payload.get("idea_text", "")).strip()
            module = str(payload.get("module", "")).strip()
            llm_model = str(payload.get("llm_model", "")).strip() or "claude-sonnet-4-6"
            llm_base_url = str(payload.get("llm_base_url", "")).strip() or "https://estellecode.com/v1"
            workspace_raw = str(payload.get("workspace", "")).strip()
            default_workspace = infer_bridge_workspace(task_type, direction)
            api_key_present = has_server_demo_key()
            authorized_action = payload.get("authorized_action") or {}

            try:
                workspace, workspace_rel = safe_project_path(workspace_raw, default_workspace)
            except ValueError as exc:
                self._send_json(400, {"ok": False, "error": str(exc)})
                return
            workspace.mkdir(parents=True, exist_ok=True)

            is_iad = ("IAD" in task_type) or ("iad" in task_type.lower()) or ("异常" in task_type) or ("异常" in direction)
            lower = message.lower()

            if authorized_action.get("type") == "run_iad_scaffold":
                mode = str(authorized_action.get("execution_mode") or execution_mode or "sanity")
                executor = run_iad_scaffold(
                    dataset_path=dataset_path,
                    execution_mode=mode,
                    approval_note=f"网页 ARIS chat 授权执行 IAD {mode} scaffold；固定 allowlist。",
                )
                summary = executor.get("summary") or {}
                reply = (
                    "已根据网页授权执行 IAD allowlist scaffold。\n\n"
                    f"- execution_mode: {mode}\n"
                    f"- returncode: {executor.get('returncode')}\n"
                    f"- status: {summary.get('status', executor.get('status', 'unknown'))}\n"
                    f"- run_dir: {executor.get('run_dir', '')}\n\n"
                    f"{metrics_table_text(summary)}"
                )
                self._send_json(200, {
                    "ok": True,
                    "reply": reply,
                    "workspace": workspace_rel,
                    "executor": executor,
                })
                return

            if authorized_action.get("type") == "run_generic_scaffold":
                executor = run_research_agent_runner_scaffold(
                    task_type=task_type,
                    direction=direction,
                    task_mode=str(payload.get("task_mode", "")).strip() or "incremental_improvement",
                )
                if not executor.get("executed"):
                    executor = run_generic_scaffold(
                        task_type=task_type,
                        direction=direction,
                        idea_title=idea_title,
                        idea_text=idea_text,
                    )
                summary = executor.get("summary") or {}
                metrics = summary.get("metrics") or {}
                reply = (
                    "已根据网页授权执行陌生方向 task-specific runner scaffold。\n\n"
                    "注意：这是由 ResearchAgentOrchestrator 为当前任务生成的执行链路测试，不是领域真实 benchmark。\n\n"
                    f"- returncode: {executor.get('returncode')}\n"
                    f"- status: {summary.get('status', 'unknown')}\n"
                    f"- run_dir: {executor.get('run_dir', '')}\n\n"
                    f"{metrics_table_text({'metrics': metrics})}"
                )
                self._send_json(200, {
                    "ok": True,
                    "reply": reply,
                    "workspace": workspace_rel,
                    "executor": executor,
                })
                return

            if any(x in lower for x in ["接管", "开始", "continue", "take over", "接入", "实验代理"]):
                config = read_json(workspace / "ARIS_RUN_CONFIG.json")
                prompt_exists = (workspace / "ARIS_EXECUTION_PROMPT.md").exists()
                reply = (
                    "我已进入网页版 ARIS 实验对话模式，并读取当前 workspace 状态。\n\n"
                    f"- workspace: `{workspace_rel}`\n"
                    f"- focused_final_plan.json: `{(workspace / 'focused_final_plan.json').exists()}`\n"
                    f"- refine-logs/EXPERIMENT_PLAN.md: `{(workspace / 'refine-logs/EXPERIMENT_PLAN.md').exists()}`\n"
                    f"- ARIS_RUN_CONFIG.json: `{bool(config)}`\n"
                    f"- ARIS_EXECUTION_PROMPT.md: `{prompt_exists}`\n\n"
                    "我建议下一步先检查数据集；如果是 IAD，可以请求授权运行 sanity scaffold。"
                )
                self._send_json(200, {"ok": True, "reply": reply, "workspace": workspace_rel})
                return

            if any(x in lower for x in ["检查数据", "数据集", "dataset", "环境", "gpu", "检查"]):
                resolved = resolve_dataset_path(dataset_path)
                reply = (
                    "数据与环境检查结果：\n\n"
                    f"- dataset_path: `{dataset_path}`\n"
                    f"- dataset_exists: `{bool(resolved)}`\n"
                    f"- resolved_path: `{resolved or ''}`\n"
                    f"- V24 IAD executor: `{V24_SCRIPT.exists()}`\n"
                    f"- current task runner: `{'IAD allowlist scaffold' if is_iad else 'runner plan only'}`\n\n"
                    "如果 dataset_exists=true 且任务是 IAD，可以继续请求运行 sanity test。"
                )
                self._send_json(200, {"ok": True, "reply": reply, "workspace": workspace_rel})
                return

            if any(x in lower for x in ["sanity", "跑实验", "运行实验", "baseline", "复现", "run", "执行"]):
                if not is_iad:
                    reply = (
                        "该任务不是已完整接入真实 benchmark 的 IAD runner。为了测试陌生方向的端到端执行接口，"
                        "我可以运行 ResearchAgentOrchestrator 为当前任务生成的 task-specific runner scaffold：\n\n"
                        "1. 重新/刷新当前任务的 agent workspace\n"
                        "2. 运行 runner_scaffold/prepare_manifest.py\n"
                        "3. 运行 runner_scaffold/run_baseline.py\n"
                        "4. 运行 runner_scaffold/run_proposed.py\n"
                        "5. 运行 runner_scaffold/evaluate.py\n"
                        "6. 运行 runner_scaffold/parse_result_to_claim.py\n\n"
                        "注意：这验证的是授权执行链路和 claim 边界；真实领域 benchmark 仍需接入该领域数据和 baseline。请点击授权按钮后执行。"
                    )
                    self._send_json(200, {
                        "ok": True,
                        "reply": reply,
                        "workspace": workspace_rel,
                        "action_required": True,
                        "action": {
                            "type": "run_generic_scaffold",
                            "label": "授权执行当前任务 runner scaffold",
                            "execution_mode": "task_specific_sanity",
                        },
                    })
                    return
                reply = (
                    "我判断下一步需要执行 IAD sanity scaffold。该动作会运行固定 allowlist 命令链：\n\n"
                    "1. prepare_mvtec_split\n"
                    "2. prepare_reference_manifest\n"
                    "3. build_reference_bank\n"
                    "4. reproduce_lightweight_baseline\n"
                    "5. run_reference_consistency_agent\n"
                    "6. evaluate_execution_metrics\n\n"
                    "这不是任意 shell 执行；只会调用项目内固定脚本。请点击授权按钮后执行。"
                )
                self._send_json(200, {
                    "ok": True,
                    "reply": reply,
                    "workspace": workspace_rel,
                    "action_required": True,
                    "action": {
                        "type": "run_iad_scaffold",
                        "label": f"授权执行 IAD {execution_mode} scaffold",
                        "execution_mode": execution_mode,
                    },
                })
                return

            if any(x in lower for x in ["指标", "metric", "结果", "summary", "读取"]):
                summary = read_json(V24_RUN_DIR / "execution_summary.json")
                reply = "当前可读取到的执行指标：\n\n" + metrics_table_text(summary)
                self._send_json(200, {"ok": True, "reply": reply, "workspace": workspace_rel, "summary": summary})
                return

            if any(x in lower for x in ["claim", "result-to-claim", "结论", "证据"]):
                generic_claim = GENERIC_RUN_DIR / "outputs" / "result_to_claim.md"
                if not is_iad and generic_claim.exists():
                    text = generic_claim.read_text(encoding="utf-8")
                    self._send_json(200, {
                        "ok": True,
                        "reply": f"已读取陌生方向 generic result-to-claim 文件：`{generic_claim.relative_to(PROJECT_ROOT)}`\n\n{text}",
                        "workspace": workspace_rel,
                        "artifact": str(generic_claim.relative_to(PROJECT_ROOT)),
                    })
                    return
                path, text = write_result_to_claim(workspace, task_type, idea_title)
                self._send_json(200, {
                    "ok": True,
                    "reply": f"已生成 result-to-claim 文件：`{path.relative_to(PROJECT_ROOT)}`\n\n{text}",
                    "workspace": workspace_rel,
                    "artifact": str(path.relative_to(PROJECT_ROOT)),
                })
                return

            if any(x in lower for x in ["论文", "paper", "draft", "草稿", "写作"]):
                if not is_iad:
                    generic_summary = read_json(GENERIC_RUN_DIR / "execution_summary.json")
                    text = f"""# Generic Paper Draft

## Title

{idea_title}: A Generic Execution Smoke Test for an Unfamiliar Research Direction

## Abstract

This draft describes how the AI4S Research Agent handles an unfamiliar research direction. The system first generates a focused research idea and experiment plan. Since no task-specific dataset runner or domain benchmark is configured, the web ARIS adapter runs a generic execution smoke runner to verify the interface from final plan to executable artifacts, metric parsing, result-to-claim, and paper drafting. The output is not claimed as domain benchmark evidence.

## Task

- Task type: {task_type}
- Research direction: {direction}

## Final Idea

{idea_text}

## Generic Smoke-Test Evidence

{metrics_table_text(generic_summary)}

## Claim Boundary

The generic runner validates workflow executability and artifact generation. It does not validate scientific superiority on a real dataset. A real benchmark requires a task-specific manifest, baseline runner, proposed-module runner, metric parser, and result-to-claim parser.
"""
                    path = workspace / "paper_draft_generic.md"
                    path.write_text(text, encoding="utf-8")
                    self._send_json(200, {
                        "ok": True,
                        "reply": f"已生成陌生方向 generic 论文草稿：`{path.relative_to(PROJECT_ROOT)}`\n\n{text}",
                        "workspace": workspace_rel,
                        "artifact": str(path.relative_to(PROJECT_ROOT)),
                    })
                    return
                path, text = write_paper_draft(workspace, task_type, direction, idea_title, idea_text)
                self._send_json(200, {
                    "ok": True,
                    "reply": f"已生成论文草稿：`{path.relative_to(PROJECT_ROOT)}`\n\n{text}",
                    "workspace": workspace_rel,
                    "artifact": str(path.relative_to(PROJECT_ROOT)),
                })
                return

            system_prompt = (
                "你是 AI4S Research Agent 的 Phase 2 网页实验对话舱。"
                "你可以自由回答用户关于当前科研 idea、baseline、实验设计、结果解释和论文写作的问题。"
                "但你不能声称已经执行未执行的实验；如果用户要求真实运行实验、安装依赖、下载数据、启动 GPU 或执行命令，"
                "必须提醒应通过网页授权动作队列执行，而不是直接编造结果。"
                "回答要具体、面向科研实现，避免空泛。"
            )
            context = (
                f"当前任务: {task_type}\n"
                f"研究方向: {direction}\n"
                f"Idea title: {idea_title}\n"
                f"Idea text: {idea_text}\n"
                f"Minimal module: {module}\n"
                f"Workspace: {workspace_rel}\n"
                f"Dataset path: {dataset_path}\n"
                f"已有 IAD execution summary: {json.dumps(read_json(V24_RUN_DIR / 'execution_summary.json'), ensure_ascii=False)[:2500]}\n\n"
                f"用户问题: {message}"
            )
            model_result = call_openai_compatible_chat(
                base_url=llm_base_url,
                api_key=get_server_demo_key(),
                model=llm_model,
                system_prompt=system_prompt,
                user_message=context,
            )
            if model_result.get("ok"):
                self._send_json(200, {
                    "ok": True,
                    "reply": model_result.get("reply", ""),
                    "workspace": workspace_rel,
                    "model": llm_model,
                    "llm_free_chat": True,
                    "usage": model_result.get("usage", {}),
                })
                return

            reply = (
                "模型自由对话暂时不可用。你仍然可以继续使用实验代理的固定能力：\n\n"
                "- 接管当前实验\n"
                "- 检查数据集和环境\n"
                "- 跑 sanity test\n"
                "- 读取指标\n"
                "- 生成 result-to-claim\n"
                "- 生成论文草稿\n\n"
                "如果需要自由问答，请确认服务器已正确设置 AI4S_DEMO_API_KEY。"
            )
            self._send_json(200, {"ok": True, "reply": reply, "workspace": workspace_rel, "llm_free_chat": False})
            return

        if self.path == "/api/aris/prepare":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(min(length, 128_000)).decode("utf-8")
                payload = json.loads(raw or "{}")
            except Exception as exc:
                self._send_json(400, {"ok": False, "error": f"invalid JSON: {exc}"})
                return

            task_type = str(payload.get("task_type", "")).strip()
            direction = str(payload.get("research_direction", "")).strip()
            execution_mode = str(payload.get("execution_mode", "plan_only")).strip() or "plan_only"
            api_key_present = bool(payload.get("api_key_present")) or has_server_demo_key()
            workspace_raw = str(payload.get("workspace", "")).strip()
            default_workspace = infer_bridge_workspace(task_type, direction)

            if not api_key_present:
                self._send_json(400, {
                    "ok": False,
                    "error": "请先在网页端提供 Claude 或其他大模型 API Key。Demo server 不保存密钥，只记录 key_present=true。",
                })
                return

            try:
                workspace, workspace_rel = safe_project_path(workspace_raw, default_workspace)
            except ValueError as exc:
                self._send_json(400, {"ok": False, "error": str(exc)})
                return

            workspace.mkdir(parents=True, exist_ok=True)
            payload_to_save = dict(payload)
            payload_to_save["api_key_present"] = True
            payload_to_save.pop("api_key", None)
            payload_to_save.update({
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "project_root": str(PROJECT_ROOT),
                "auto_claude_root": "/data1/huangyuling/-A_HYL/AI4S/Auto-claude-code-research-in-sleep-main",
                "workspace": workspace_rel,
                "safety_boundary": "This demo writes ARIS handoff files and only runs fixed allowlisted scaffold executors.",
            })
            config_path = workspace / "ARIS_RUN_CONFIG.json"
            prompt_path = workspace / "ARIS_EXECUTION_PROMPT.md"
            write_json(config_path, payload_to_save)
            prompt = build_aris_prompt(payload_to_save, workspace_rel, str(config_path.relative_to(PROJECT_ROOT)))
            prompt_path.write_text(prompt, encoding="utf-8")

            executor_payload = None
            is_iad = ("IAD" in task_type) or ("iad" in task_type.lower()) or ("异常" in task_type) or ("异常" in direction)
            if execution_mode in ("sanity", "full") and is_iad:
                dataset_path = str(payload.get("dataset_path", "")).strip()
                categories = ["bottle"] if execution_mode == "sanity" else ["bottle", "cable", "capsule"]
                cmd = [
                    sys.executable,
                    str(V24_SCRIPT),
                    "--approve",
                    "--approval-note",
                    f"网页端授权 Auto-claude/ARIS {execution_mode} 执行；固定 IAD scaffold allowlist。",
                ]
                mvtec_root = resolve_dataset_path(dataset_path) or resolve_dataset_path("Datasets/01_IAD/mvtec_anomaly_detection/mvtec_anomaly_detection")
                if mvtec_root and mvtec_root.exists():
                    cmd.extend(["--mvtec-root", str(mvtec_root), "--categories", *categories])
                else:
                    executor_payload = {
                        "executed": False,
                        "status": "missing_dataset",
                        "error": "MVTec AD dataset path not found. Please upload dataset or set an absolute dataset_path.",
                        "dataset_path": dataset_path,
                    }
                    self._send_json(200, {
                        "ok": True,
                        "workspace": workspace_rel,
                        "config_path": str(config_path.relative_to(PROJECT_ROOT)),
                        "prompt_path": str(prompt_path.relative_to(PROJECT_ROOT)),
                        "execution_mode": execution_mode,
                        "executed": False,
                        "executor": executor_payload,
                        "prompt_preview": prompt,
                    })
                    return
                try:
                    proc = subprocess.run(
                        cmd,
                        cwd=str(PROJECT_ROOT),
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        timeout=1800,
                    )
                    executor_payload = {
                        "executed": True,
                        "returncode": proc.returncode,
                        "run_dir": str(V24_RUN_DIR.relative_to(PROJECT_ROOT)),
                        "summary": read_json(V24_RUN_DIR / "execution_summary.json"),
                        "watchdog": read_json(V24_RUN_DIR / "watchdog_loop_state.json"),
                        "stdout_tail": proc.stdout[-8000:],
                    }
                except subprocess.TimeoutExpired:
                    executor_payload = {
                        "executed": True,
                        "status": "timeout",
                        "error": "V24 executor timed out after 1800 seconds.",
                    }

            self._send_json(200, {
                "ok": True,
                "workspace": workspace_rel,
                "config_path": str(config_path.relative_to(PROJECT_ROOT)),
                "prompt_path": str(prompt_path.relative_to(PROJECT_ROOT)),
                "execution_mode": execution_mode,
                "executed": bool(executor_payload and executor_payload.get("executed")),
                "executor": executor_payload,
                "prompt_preview": prompt,
            })
            return

        if self.path == "/api/live_workflow/start":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(min(length, 64_000)).decode("utf-8")
                payload = json.loads(raw or "{}")
            except Exception as exc:
                self._send_json(400, {"ok": False, "error": f"invalid JSON: {exc}"})
                return

            task_key = safe_task_key(str(payload.get("task_key") or payload.get("task_type") or "iad"))
            task_type = str(payload.get("task_type", "")).strip()
            direction = str(payload.get("research_direction", "")).strip()
            task_mode = str(payload.get("task_mode", "")).strip()
            authorize_llm = bool(payload.get("authorize_llm"))
            approval_note = str(payload.get("approval_note", "")).strip()
            mode = "authorized_llm" if authorize_llm else "safe_local"
            if authorize_llm and len(approval_note) < 8:
                self._send_json(400, {"ok": False, "error": "LLM/API mode requires explicit approval_note."})
                return
            if not V27_SCRIPT.exists():
                self._send_json(500, {"ok": False, "error": f"missing V27 script: {V27_SCRIPT}"})
                return

            LIVE_RUN_ROOT.mkdir(parents=True, exist_ok=True)
            job_id = f"live_{task_key}_{time.strftime('%Y%m%d_%H%M%S')}_{int((time.time() % 1) * 1000):03d}"
            run_dir = LIVE_RUN_ROOT / job_id
            run_dir.mkdir(parents=True, exist_ok=True)
            cmd = [
                sys.executable,
                str(V27_SCRIPT),
                "--task-key", task_key,
                "--direction", direction,
                "--user-task-type", task_type,
                "--task-mode", task_mode,
                "--run-dir", str(run_dir),
                "--mode", mode,
            ]
            if task_key == "custom":
                completed = subprocess.run(
                    cmd,
                    cwd=str(PROJECT_ROOT),
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    timeout=20,
                )
                (run_dir / "workflow_stdout.log").write_text(completed.stdout or "", encoding="utf-8")
                if completed.returncode != 0:
                    self._send_json(500, {
                        "ok": False,
                        "job_id": job_id,
                        "status": "failed",
                        "task_key": task_key,
                        "task_mode": task_mode,
                        "run_dir": str(run_dir.relative_to(PROJECT_ROOT)),
                        "error": "custom live workflow failed",
                        "log_tail": tail_text(run_dir / "workflow_stdout.log"),
                    })
                    return
                self._send_json(200, {
                    "ok": True,
                    "job_id": job_id,
                    "status": "finished",
                    "task_key": task_key,
                    "task_mode": task_mode,
                    "mode": mode,
                    "run_dir": str(run_dir.relative_to(PROJECT_ROOT)),
                    "message": "Custom live workflow completed. Poll /api/live_workflow/status or read result directly.",
                })
                return

            log_file = open(run_dir / "workflow_stdout.log", "w", encoding="utf-8")
            proc = subprocess.Popen(
                cmd,
                cwd=str(PROJECT_ROOT),
                text=True,
                stdout=log_file,
                stderr=subprocess.STDOUT,
            )
            LIVE_JOBS[job_id] = proc
            self._send_json(200, {
                "ok": True,
                "job_id": job_id,
                "status": "started",
                "task_key": task_key,
                "task_mode": task_mode,
                "mode": mode,
                "run_dir": str(run_dir.relative_to(PROJECT_ROOT)),
                "message": "Live workflow backend started. Poll /api/live_workflow/status.",
            })
            return

        if self.path != "/api/execution/authorize":
            self._send_json(404, {"ok": False, "error": "unknown endpoint"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(min(length, 64_000)).decode("utf-8")
            payload = json.loads(raw or "{}")
        except Exception as exc:
            self._send_json(400, {"ok": False, "error": f"invalid JSON: {exc}"})
            return

        task_type = str(payload.get("task_type", "")).strip()
        direction = str(payload.get("research_direction", "")).strip()
        approval_note = str(payload.get("approval_note", "")).strip()
        categories = payload.get("categories") or []
        llm_provider = str(payload.get("llm_provider", "")).strip() or "claude"
        llm_model = str(payload.get("llm_model", "")).strip() or "claude-sonnet-4-6"
        llm_base_url = str(payload.get("llm_base_url", "")).strip() or "https://estellecode.com/v1"
        api_key_present = bool(payload.get("api_key_present")) or has_server_demo_key()
        dataset_path = str(payload.get("dataset_path", "")).strip()

        if not approval_note or len(approval_note) < 8:
            self._send_json(400, {
                "ok": False,
                "error": "请先填写明确的授权说明 approval_note。",
            })
            return
        # Safety boundary: this demo server never executes arbitrary commands.
        # It only calls the fixed V24 executor, which itself runs a fixed allowlisted IAD scaffold chain.
        is_iad = ("IAD" in task_type) or ("异常" in task_type) or ("异常" in direction)
        if not is_iad:
            self._send_json(200, {
                "ok": True,
                "executed": False,
                "status": "planned_only",
                "message": "当前网页端真实可执行链路已接入 IAD scaffold。该任务已生成实验执行计划，但尚未配置对应任务 runner；不会伪造实验结果。",
                "next_step": "为该任务添加 baseline runner / dataset manifest / metric parser 后，即可复用同一个授权执行接口。",
                "llm_provider": llm_provider,
                "llm_model": llm_model,
                "llm_base_url": llm_base_url,
                "api_key_present": True,
            })
            return

        cmd = [
            sys.executable,
            str(V24_SCRIPT),
            "--approve",
            "--approval-note",
            approval_note,
        ]
        if categories:
            safe_categories = [str(x).strip() for x in categories if str(x).strip()]
            if safe_categories:
                mvtec_root = resolve_dataset_path(dataset_path) or resolve_dataset_path("Datasets/01_IAD/mvtec_anomaly_detection/mvtec_anomaly_detection")
                if mvtec_root and mvtec_root.exists():
                    cmd.extend(["--mvtec-root", str(mvtec_root), "--categories", *safe_categories])

        try:
            proc = subprocess.run(
                cmd,
                cwd=str(PROJECT_ROOT),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=1800,
            )
        except subprocess.TimeoutExpired:
            self._send_json(504, {
                "ok": False,
                "executed": True,
                "status": "timeout",
                "error": "V24 executor timed out after 1800 seconds.",
            })
            return

        summary = read_json(V24_RUN_DIR / "execution_summary.json")
        watchdog = read_json(V24_RUN_DIR / "watchdog_loop_state.json")
        self._send_json(200 if proc.returncode == 0 else 500, {
            "ok": proc.returncode == 0,
            "executed": True,
            "returncode": proc.returncode,
            "stdout": proc.stdout[-8000:],
            "summary": summary,
            "watchdog": watchdog,
            "run_dir": str(V24_RUN_DIR.relative_to(PROJECT_ROOT)),
            "llm_provider": llm_provider,
            "llm_model": llm_model,
            "llm_base_url": llm_base_url,
            "api_key_present": True,
            "dataset_path": dataset_path,
        })


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def find_available_port(host: str, start_port: int, tries: int = 20) -> int:
    for port in range(start_port, start_port + tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((host, port))
            except OSError:
                continue
            return port
    raise OSError(f"No available localhost port found in {start_port}-{start_port + tries - 1}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the AI4S interactive demo page.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind. Use 0.0.0.0 for remote access.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Preferred local port.")
    parser.add_argument("--strict-port", action="store_true", help="Fail instead of trying the next port.")
    args = parser.parse_args()

    port = args.port if args.strict_port else find_available_port(args.host, args.port)
    if port != args.port:
        print(f"Port {args.port} is busy; using {port} instead.")

    with ReusableTCPServer((args.host, port), Handler) as httpd:
        print(f"Demo server running on: http://{args.host}:{port}/AI4S_RESEARCH_AGENT_DEMO.html")
        print(f"Local URL: http://127.0.0.1:{port}/AI4S_RESEARCH_AGENT_DEMO.html")
        print("Press Ctrl+C to stop.")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
