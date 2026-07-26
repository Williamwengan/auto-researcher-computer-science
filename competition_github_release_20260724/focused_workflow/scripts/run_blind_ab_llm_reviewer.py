#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path


DIMENSIONS = [
    "novelty",
    "feasibility",
    "expected_effectiveness",
    "experimental_rigor",
    "baseline_grounding",
    "mechanism_specificity",
    "implementation_readiness",
    "overall",
]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def safe_name(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9_.-]+", "_", value)
    return value.strip("_") or "reviewer"


def render_prompt(review_dir: Path, reviewer_name: str, max_pair_chars: int) -> str:
    sheet = load_json(review_dir / "blind_review_sheet.json")
    if not isinstance(sheet, list):
        raise TypeError("blind_review_sheet.json must be a JSON list")

    pair_chunks = []
    for item in sheet:
        pair_id = item["pair_id"]
        pair_file = review_dir / "pairs" / f"{pair_id}.md"
        if not pair_file.exists():
            raise FileNotFoundError(pair_file)
        text = pair_file.read_text(encoding="utf-8")
        if len(text) > max_pair_chars:
            text = text[:max_pair_chars] + "\n\n[TRUNCATED FOR REVIEW PROMPT]\n"
        pair_chunks.append(f"\n\n===== PAIR {pair_id} =====\n\n{text}")

    output_schema = []
    for item in sheet:
        output_schema.append(
            {
                "pair_id": item["pair_id"],
                "domain": item["domain"],
                "idea_title": item["idea_title"],
                "preferred": "A | B | tie",
                "preference_strength": "1 | 2 | 3",
                "preference_rationale": "",
                "tie_allowed": True,
                "scores": {
                    "A": {dim: "integer 1-10" for dim in DIMENSIONS},
                    "B": {dim: "integer 1-10" for dim in DIMENSIONS},
                },
                "rationales": {
                    "A": "",
                    "B": "",
                },
                "implementation_concerns": {
                    "A": [],
                    "B": [],
                },
            }
        )

    return f"""# Blind A/B Research Idea Review

You are reviewer `{reviewer_name}`.

You are evaluating blinded A/B pairs of research ideas. You must not infer or mention which version is before/after repair. The private answer key is not provided.

## Review Goal

Choose which version is more scientifically useful, focused, implementable, and credible.

Do not reward length by itself. Penalize template-like additions that look detailed but do not improve mechanism, evidence, experimental rigor, or implementability.

## Rubric

Score each version A and B on 1-10:

- novelty: non-trivial research contribution beyond stacking tools
- feasibility: can be implemented by a small team in 1-2 weeks for MVP
- expected_effectiveness: likely to improve target metrics or reveal useful failure modes
- experimental_rigor: baselines, ablations, negative controls, success/failure criteria
- baseline_grounding: concrete relation to direct baselines and their weaknesses
- mechanism_specificity: explicit mechanism, decision rule, objective, verifier, or calibration logic
- implementation_readiness: scripts/data/artifacts are specific enough to start engineering
- overall: your holistic judgment

`preferred` must be exactly one of: `A`, `B`, `tie`.
`preference_strength`: 1 means weak preference, 2 means moderate, 3 means strong.

## Required Output

Return only a JSON list. Do not write markdown.

Each item must follow this schema:

```json
{json.dumps(output_schema, ensure_ascii=False, indent=2)}
```

## A/B Pairs
{''.join(pair_chunks)}
"""


def extract_json_list(text: str):
    text = text.strip()
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
    except Exception:
        pass
    match = re.search(r"\[[\s\S]*\]", text)
    if match:
        data = json.loads(match.group(0))
        if isinstance(data, list):
            return data
    raise ValueError("Could not parse a JSON list from reviewer output")


def run_codex(work_dir: Path, prompt_path: Path, model: str) -> str:
    codex = shutil.which("codex")
    if not codex:
        raise FileNotFoundError("Cannot find codex in PATH")
    env = os.environ.copy()
    env.setdefault("CODEX_HOME", str(Path.home() / ".codex-estelle"))
    if not env.get("ESTELLE_API_KEY"):
        raise RuntimeError("ESTELLE_API_KEY is empty. Run: source ~/.estelle_api_env")

    cmd = [
        codex,
        "exec",
        "--skip-git-repo-check",
        "--dangerously-bypass-approvals-and-sandbox",
        "--model",
        model,
        (
            f"Read {prompt_path.name}. Perform the blind A/B review. "
            "Return only the JSON list and also save it exactly as reviewer_output.json."
        ),
    ]
    proc = subprocess.run(cmd, cwd=work_dir, env=env, text=True, capture_output=True)
    (work_dir / "codex_stdout.txt").write_text(proc.stdout or "", encoding="utf-8")
    (work_dir / "codex_stderr.txt").write_text(proc.stderr or "", encoding="utf-8")
    if proc.returncode != 0:
        raise RuntimeError(f"Codex reviewer failed with code {proc.returncode}; see {work_dir}/codex_stderr.txt")
    output_file = work_dir / "reviewer_output.json"
    if output_file.exists():
        return output_file.read_text(encoding="utf-8")
    return proc.stdout


def run_chat_api(
    work_dir: Path,
    prompt_path: Path,
    model: str,
    api_key_env: str,
    base_url: str,
    timeout: int,
    proxy: str | None,
) -> str:
    api_key = os.environ.get(api_key_env, "")
    if not api_key:
        raise RuntimeError(f"{api_key_env} is empty. Run: source ~/.estelle_api_env")

    prompt_text = prompt_path.read_text(encoding="utf-8")
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": (
                    prompt_text
                    + "\n\nPerform the blind A/B review. "
                    + "Return only the JSON list. Do not write markdown."
                ),
            }
        ],
        "temperature": 0,
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    url = base_url.rstrip("/") + "/chat/completions"
    if proxy:
        request_path = work_dir / "chat_api_request.json"
        response_path = work_dir / "chat_api_response.json"
        request_path.write_bytes(data)
        curl = shutil.which("curl")
        if not curl:
            raise FileNotFoundError("Cannot find curl in PATH")
        cmd = [
            curl,
            "-x",
            proxy,
            "-sS",
            "-L",
            "--max-time",
            str(timeout),
            "-o",
            str(response_path),
            "-w",
            "%{http_code}",
            "-X",
            "POST",
            url,
            "-H",
            f"Authorization: Bearer {api_key}",
            "-H",
            "Content-Type: application/json",
            "--data-binary",
            f"@{request_path}",
        ]
        proc = subprocess.run(cmd, cwd=work_dir, text=True, capture_output=True)
        (work_dir / "curl_api_stderr.txt").write_text(proc.stderr or "", encoding="utf-8")
        http_code = (proc.stdout or "").strip()
        body = response_path.read_text(encoding="utf-8", errors="replace") if response_path.exists() else ""
        if proc.returncode != 0:
            raise RuntimeError(f"curl chat API failed with code {proc.returncode}; see {work_dir}/curl_api_stderr.txt")
        if not http_code.startswith("2"):
            (work_dir / "chat_api_error.json").write_text(body, encoding="utf-8")
            raise RuntimeError(f"chat API failed with HTTP {http_code}; see {work_dir}/chat_api_error.json")
        response = json.loads(body)
        choices = response.get("choices") or []
        if not choices:
            raise RuntimeError("chat API response has no choices")
        message = choices[0].get("message") or {}
        content = message.get("content", "")
        if not content:
            raise RuntimeError("chat API response content is empty")
        (work_dir / "reviewer_output.json").write_text(content, encoding="utf-8")
        return content

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    opener = urllib.request.build_opener()
    if proxy:
        opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({"http": proxy, "https": proxy})
        )

    try:
        with opener.open(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        (work_dir / "chat_api_error.json").write_text(body, encoding="utf-8")
        raise RuntimeError(f"chat API failed with HTTP {exc.code}; see {work_dir}/chat_api_error.json") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"chat API connection failed: {exc}") from exc

    (work_dir / "chat_api_response.json").write_text(body, encoding="utf-8")
    response = json.loads(body)
    choices = response.get("choices") or []
    if not choices:
        raise RuntimeError("chat API response has no choices")
    message = choices[0].get("message") or {}
    content = message.get("content", "")
    if not content:
        raise RuntimeError("chat API response content is empty")
    (work_dir / "reviewer_output.json").write_text(content, encoding="utf-8")
    return content


def validate_review(review: list[dict], expected_pairs: set[str]) -> None:
    seen = set()
    for idx, item in enumerate(review, start=1):
        if not isinstance(item, dict):
            raise TypeError(f"review item {idx} must be object")
        pair_id = item.get("pair_id")
        if pair_id not in expected_pairs:
            raise ValueError(f"review item {idx} unknown pair_id: {pair_id}")
        seen.add(pair_id)
        preferred = item.get("preferred")
        if isinstance(preferred, str):
            preferred_norm = preferred.strip().lower()
        else:
            preferred_norm = ""
        if preferred_norm not in {"a", "b", "tie"}:
            raise ValueError(f"review item {idx} invalid preferred: {preferred}")
        scores = item.get("scores", {})
        for side in ["A", "B"]:
            if side not in scores:
                raise ValueError(f"review item {idx} missing scores.{side}")
            for dim in DIMENSIONS:
                value = scores[side].get(dim)
                if not isinstance(value, int) or not (1 <= value <= 10):
                    raise ValueError(f"review item {idx} scores.{side}.{dim} must be integer 1-10")
    missing = expected_pairs - seen
    if missing:
        raise ValueError(f"missing review pairs: {sorted(missing)}")


def normalize_review(review: list[dict]) -> list[dict]:
    for item in review:
        preferred = item.get("preferred")
        if isinstance(preferred, str):
            normalized = preferred.strip()
            if normalized.lower() == "tie":
                item["preferred"] = "tie"
            elif normalized.upper() in {"A", "B"}:
                item["preferred"] = normalized.upper()
        strength = item.get("preference_strength")
        if isinstance(strength, str) and strength.strip().isdigit():
            item["preference_strength"] = int(strength.strip())
        scores = item.get("scores", {})
        for side in ["A", "B"]:
            side_scores = scores.get(side, {})
            for dim in DIMENSIONS:
                value = side_scores.get(dim)
                if isinstance(value, str) and value.strip().isdigit():
                    side_scores[dim] = int(value.strip())
                elif isinstance(value, float) and value.is_integer():
                    side_scores[dim] = int(value)
    return review


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one LLM reviewer on a blind A/B review package.")
    parser.add_argument("--review-dir", required=True, type=Path)
    parser.add_argument("--model", required=True)
    parser.add_argument("--reviewer-name", default=None)
    parser.add_argument("--output-file", type=Path, default=None)
    parser.add_argument("--max-pair-chars", type=int, default=26000)
    parser.add_argument("--backend", choices=["codex", "chat"], default="codex")
    parser.add_argument("--api-key-env", default="ESTELLE_API_KEY")
    parser.add_argument("--base-url", default="https://estellecode.com/v1")
    parser.add_argument("--proxy", default=None, help="Optional HTTP/HTTPS proxy, e.g. http://127.0.0.1:7890")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    review_dir = args.review_dir.resolve()
    reviewer_name = args.reviewer_name or safe_name(args.model)
    reviewer_safe = safe_name(reviewer_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    work_dir = review_dir / "llm_review_runs" / f"{reviewer_safe}_{timestamp}"
    work_dir.mkdir(parents=True, exist_ok=True)

    prompt = render_prompt(review_dir, reviewer_name, args.max_pair_chars)
    prompt_path = work_dir / "blind_ab_llm_review_prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")

    sheet = load_json(review_dir / "blind_review_sheet.json")
    expected_pairs = {item["pair_id"] for item in sheet}

    print("LLM blind reviewer prepared")
    print("Review dir:", review_dir)
    print("Model:", args.model)
    print("Reviewer:", reviewer_name)
    print("Work dir:", work_dir)
    print("Prompt:", prompt_path)
    print("Prompt length:", len(prompt))
    print("Backend:", args.backend)
    if args.proxy:
        print("Proxy:", args.proxy)

    if args.dry_run:
        print("Dry run only; no external API call made.")
        return

    if args.backend == "chat":
        raw = run_chat_api(
            work_dir,
            prompt_path,
            args.model,
            args.api_key_env,
            args.base_url,
            args.timeout,
            args.proxy,
        )
    else:
        raw = run_codex(work_dir, prompt_path, args.model)
    review = extract_json_list(raw)
    review = normalize_review(review)
    validate_review(review, expected_pairs)

    output_file = args.output_file or (review_dir / f"blind_review_{reviewer_safe}.json")
    output_file.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (work_dir / "parsed_review.json").write_text(
        json.dumps(review, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("Reviewer JSON saved:", output_file)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
