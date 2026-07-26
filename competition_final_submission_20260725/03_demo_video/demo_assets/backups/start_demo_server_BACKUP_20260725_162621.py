#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import http.server
import socket
import socketserver
import subprocess
import sys
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


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


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
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
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
        api_key_present = bool(payload.get("api_key_present"))
        dataset_path = str(payload.get("dataset_path", "")).strip()

        if not approval_note or len(approval_note) < 8:
            self._send_json(400, {
                "ok": False,
                "error": "请先填写明确的授权说明 approval_note。",
            })
            return
        if not api_key_present:
            self._send_json(400, {
                "ok": False,
                "error": "请先在网页端提供 Claude 或其他大模型 API Key。Demo server 不保存密钥，只记录 key_present=true。",
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
                mvtec_root = (PROJECT_ROOT / dataset_path) if dataset_path else PROJECT_ROOT / "Datasets/01_IAD/mvtec_anomaly_detection/mvtec_anomaly_detection"
                if mvtec_root.exists():
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
