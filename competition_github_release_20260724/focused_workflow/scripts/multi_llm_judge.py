#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import re
import shutil
import subprocess
import statistics
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None

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


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_yaml(path: Path) -> dict:
    if yaml is None:
        raise RuntimeError("PyYAML is required. Install pyyaml or run inside the ResearchArena environment.")
    return yaml.safe_load(path.read_text())


def load_json(path: Path):
    return json.loads(path.read_text())


def extract_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    candidates = re.findall(r"(\{.*\}|\[.*\])", text, flags=re.S)
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    raise ValueError("Could not parse JSON from LLM response")


def openai_chat_completion(base_url: str, api_key: str, model: str, messages: list[dict], temperature: float, max_tokens: int, timeout: int) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def ollama_generate_json(judge: dict, prompt_text: str):
    url = judge.get("base_url", "http://127.0.0.1:11434").rstrip("/") + "/api/generate"
    payload = {
        "model": judge["model"],
        "prompt": prompt_text,
        "stream": False,
        "options": {
            "temperature": judge.get("temperature", 0),
            "num_predict": judge.get("max_new_tokens", 2048),
        },
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(req, timeout=int(judge.get("timeout_seconds", 300))) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return extract_json(data.get("response", ""))



def codex_exec_to_json(workdir: Path, model: str, prompt_text: str, prompt_name: str, output_name: str, instruction: str):
    codex = shutil.which("codex")
    if not codex:
        raise FileNotFoundError("Cannot find `codex` in PATH. Source ~/.estelle_api_env and add Codex binary to PATH.")
    env = os.environ.copy()
    env.setdefault("CODEX_HOME", str(Path.home() / ".codex-estelle"))
    if not env.get("ESTELLE_API_KEY"):
        raise RuntimeError("ESTELLE_API_KEY is empty. Run: source ~/.estelle_api_env")
    prompt_path = workdir / prompt_name
    output_path = workdir / output_name
    prompt_path.write_text(prompt_text, encoding="utf-8")
    cmd = [
        codex,
        "exec",
        "--skip-git-repo-check",
        "--dangerously-bypass-approvals-and-sandbox",
        "--model",
        model,
        f"Read {prompt_name}. {instruction} Save the JSON output exactly as {output_name}.",
    ]
    subprocess.run(cmd, cwd=workdir, env=env, check=True)
    if not output_path.exists():
        raise FileNotFoundError(f"Codex did not create expected output: {output_path}")
    return load_json(output_path)


def local_hf_to_json(workdir: Path, judge: dict, prompt_text: str, prompt_name: str, output_name: str):
    """Run a local HuggingFace causal LM in a separate Python interpreter.

    This keeps the main workflow environment light: ResearchArena can run with
    its own Python, while local judges can use an existing model environment.
    """
    python_bin = judge.get("python", sys.executable)
    model_path = judge.get("model_path") or judge.get("model")
    if not model_path:
        raise ValueError(f"local_hf judge {judge.get('name')} requires model_path")

    runner_path = workdir / "local_hf_judge_runner.py"
    prompt_path = workdir / prompt_name
    output_path = workdir / output_name
    prompt_path.write_text(prompt_text, encoding="utf-8")
    runner_path.write_text(
        r'''
import argparse
import json
import re
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def extract_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    candidates = re.findall(r"(\{.*\}|\[.*\])", text, flags=re.S)
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    raise ValueError("Could not parse JSON from local model output: " + text[:500])


parser = argparse.ArgumentParser()
parser.add_argument("--model-path", required=True)
parser.add_argument("--prompt", required=True)
parser.add_argument("--output", required=True)
parser.add_argument("--max-new-tokens", type=int, default=2048)
args = parser.parse_args()

prompt = Path(args.prompt).read_text(encoding="utf-8")
tokenizer = AutoTokenizer.from_pretrained(args.model_path, local_files_only=True, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    args.model_path,
    local_files_only=True,
    trust_remote_code=True,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto",
)
messages = [
    {
        "role": "system",
        "content": "You are a strict research idea judge. Return valid JSON only. No markdown.",
    },
    {"role": "user", "content": prompt},
]
text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer([text], return_tensors="pt").to(model.device)
with torch.no_grad():
    generated = model.generate(
        **inputs,
        max_new_tokens=args.max_new_tokens,
        do_sample=False,
        temperature=None,
        top_p=None,
    )
new_tokens = generated[:, inputs.input_ids.shape[1]:]
raw = tokenizer.decode(new_tokens[0], skip_special_tokens=True)
parsed = extract_json(raw)
Path(args.output).write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
''',
        encoding="utf-8",
    )
    subprocess.run(
        [
            python_bin,
            str(runner_path),
            "--model-path",
            str(model_path),
            "--prompt",
            str(prompt_path),
            "--output",
            str(output_path),
            "--max-new-tokens",
            str(judge.get("max_new_tokens", 2048)),
        ],
        cwd=workdir,
        check=True,
    )
    return load_json(output_path)


def idea_markdown_files(run_dir: Path, review_dir: Path | None) -> list[Path]:
    directory = review_dir or (run_dir / "review_ready_ideas")
    files = sorted(directory.glob("idea_*.md"))
    if not files:
        raise FileNotFoundError(f"No idea_*.md files found in {directory}")
    return files


def build_rubric_prompt() -> str:
    return """You are a strict research idea reviewer. Score each idea from 1 to 10 on these dimensions:
- novelty: meaningful difference from existing work and baselines.
- feasibility: implementable with realistic data, compute, and time.
- expected_effectiveness: likely to improve metrics or produce useful findings.
- experimental_rigor: clear baselines, metrics, ablations, success/failure criteria.
- baseline_grounding: explicitly grounded in concrete baselines and their weaknesses.
- mechanism_specificity: concrete algorithmic/agentic mechanism, not a tool stack.
- implementation_readiness: enough scripts, data, artifacts, and timeline to start implementation.
- overall: overall priority as a research project or competition MVP.

Be conservative. Do not reward length alone. Penalize vague ideas, missing baselines, missing metrics, missing negative controls, and unsupported novelty claims."""


def build_score_prompt(idea_files: list[Path]) -> str:
    blocks = []
    for idx, path in enumerate(idea_files, 1):
        blocks.append(f"## Idea {idx}\nFile: {path}\n\n```markdown\n{path.read_text()}\n```")
    schema = {
        "idea_file": "",
        "title": "",
        "scores": {dim: 1 for dim in DIMENSIONS},
        "rationales": {dim: "" for dim in DIMENSIONS},
        "red_flags": [],
        "recommended_action": "accept|repair|reject",
    }
    return """Review all ideas below using the rubric. Return only a JSON list, one object per idea.
Each object must follow this schema:

```json
%s
```

Ideas:

%s
""" % (json.dumps(schema, ensure_ascii=False, indent=2), "\n\n".join(blocks))


def build_single_score_prompt(idea_path: Path) -> str:
    schema = {
        "idea_file": str(idea_path),
        "title": "",
        "scores": {dim: 1 for dim in DIMENSIONS},
        "rationales": {dim: "" for dim in DIMENSIONS},
        "red_flags": [],
        "recommended_action": "accept|repair|reject",
    }
    return """Review the single idea below using the rubric. Return only one JSON object.
The object must follow this schema:

```json
%s
```

Idea file: %s

```markdown
%s
```
""" % (json.dumps(schema, ensure_ascii=False, indent=2), idea_path, idea_path.read_text())


def build_pairwise_prompt(idea_a: Path, idea_b: Path) -> str:
    schema = {
        "winner": "A|B|tie",
        "confidence": 1,
        "reason": "",
        "mvp_preference": "A|B|tie",
    }
    return """Compare two research ideas. Which is stronger as a focused, baseline-grounded, implementable research idea or competition MVP?
Return only JSON with this schema:

```json
%s
```

# Idea A
File: %s

```markdown
%s
```

# Idea B
File: %s

```markdown
%s
```
""" % (
        json.dumps(schema, ensure_ascii=False, indent=2),
        idea_a,
        idea_a.read_text(),
        idea_b,
        idea_b.read_text(),
    )


def validate_score_rows(rows, expected_count: int, judge_name: str):
    if not isinstance(rows, list):
        raise TypeError(f"{judge_name}: score output must be a JSON list")
    if len(rows) != expected_count:
        raise ValueError(f"{judge_name}: expected {expected_count} score rows, got {len(rows)}")
    for row in rows:
        if not isinstance(row, dict):
            raise TypeError(f"{judge_name}: each score row must be an object")
        scores = row.get("scores")
        if not isinstance(scores, dict):
            raise ValueError(f"{judge_name}: missing scores object")
        for dim in DIMENSIONS:
            val = scores.get(dim)
            if not isinstance(val, int) or val < 1 or val > 10:
                raise ValueError(f"{judge_name}: invalid score for {dim}: {val}")
        row.setdefault("reviewer", judge_name)
    return rows


def mean_std(values: list[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    if len(values) == 1:
        return round(values[0], 3), 0.0
    return round(statistics.mean(values), 3), round(statistics.pstdev(values), 3)


def agreement_label(std: float, consistent_max: float, review_max: float) -> str:
    if std < consistent_max:
        return "consistent"
    if std <= review_max:
        return "needs_human_review"
    return "high_disagreement"


def aggregate_scores(all_reviews: dict[str, list[dict]], thresholds: dict) -> list[dict]:
    by_title: dict[str, list[dict]] = {}
    for judge, rows in all_reviews.items():
        for row in rows:
            key = row.get("title") or row.get("idea_file")
            by_title.setdefault(key, []).append(row)

    consistent_max = thresholds.get("consistent_std_max", 0.8)
    review_max = thresholds.get("review_needed_std_max", 1.5)
    aggregated = []
    for title, rows in by_title.items():
        dim_stats = {}
        for dim in DIMENSIONS:
            vals = [float(row["scores"][dim]) for row in rows]
            m, s = mean_std(vals)
            dim_stats[dim] = {"mean": m, "std": s, "min": min(vals), "max": max(vals)}
        overall_std = dim_stats["overall"]["std"]
        aggregated.append(
            {
                "title": title,
                "idea_file": rows[0].get("idea_file", ""),
                "judge_count": len(rows),
                "dimension_stats": dim_stats,
                "mean_overall": dim_stats["overall"]["mean"],
                "std_overall": overall_std,
                "agreement": agreement_label(overall_std, consistent_max, review_max),
                "recommended_actions": [row.get("recommended_action", "") for row in rows],
            }
        )
    aggregated.sort(key=lambda x: x["mean_overall"], reverse=True)
    return aggregated


def aggregate_pairwise(pairwise: list[dict], idea_files: list[Path]) -> dict:
    wins = {str(path): 0.0 for path in idea_files}
    total = {str(path): 0 for path in idea_files}
    for row in pairwise:
        a = row["idea_a"]
        b = row["idea_b"]
        total[a] += 1
        total[b] += 1
        winner = row.get("winner")
        if winner == "A":
            wins[a] += 1
        elif winner == "B":
            wins[b] += 1
        else:
            wins[a] += 0.5
            wins[b] += 0.5
    ranking = []
    for path in idea_files:
        key = str(path)
        rate = wins[key] / total[key] if total[key] else 0.0
        ranking.append({"idea_file": key, "pairwise_win_rate": round(rate, 3), "wins": wins[key], "comparisons": total[key]})
    ranking.sort(key=lambda x: x["pairwise_win_rate"], reverse=True)
    return {"ranking": ranking, "comparisons": pairwise}


def write_summary(path: Path, run_dir: Path, judges: list[dict], aggregated: list[dict], pairwise_summary: dict | None, dry_run: bool):
    lines = []
    lines.append("# Multi-LLM Judge 评价汇总\n")
    lines.append(f"Run dir: `{run_dir}`\n")
    lines.append(f"Mode: `{'dry-run' if dry_run else 'executed'}`\n")
    lines.append("## Judges\n")
    for judge in judges:
        lines.append(f"- {judge['name']}：`{judge.get('model')}` enabled={judge.get('enabled', True)}")
    lines.append("\n## Rubric Score Aggregation\n")
    if not aggregated:
        lines.append("Dry-run only: no model scores were generated.\n")
    else:
        lines.append("| Rank | Idea | Mean Overall | Std | Agreement | Judge Count |")
        lines.append("|---:|---|---:|---:|---|---:|")
        for idx, row in enumerate(aggregated, 1):
            lines.append(f"| {idx} | {row['title']} | {row['mean_overall']} | {row['std_overall']} | {row['agreement']} | {row['judge_count']} |")
    if pairwise_summary:
        lines.append("\n## Pairwise Ranking\n")
        lines.append("| Rank | Idea File | Win Rate |")
        lines.append("|---:|---|---:|")
        for idx, row in enumerate(pairwise_summary["ranking"], 1):
            lines.append(f"| {idx} | `{row['idea_file']}` | {row['pairwise_win_rate']} |")
    lines.append("\n## How To Interpret\n")
    lines.append("- `std < 0.8`：judge 比较一致。")
    lines.append("- `0.8 <= std <= 1.5`：存在分歧，建议人工复核。")
    lines.append("- `std > 1.5`：高分歧，不建议直接采用自动评分。")
    lines.append("- Pairwise win rate 更适合比较多个候选 idea 的相对优先级。\n")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run multi-LLM judge evaluation for focused research ideas.")
    parser.add_argument("run_dir", help="Focused workflow output directory")
    parser.add_argument("--config", default="focused_workflow/evaluation/judge_config.yaml")
    parser.add_argument("--review-dir", default=None)
    parser.add_argument("--output-dir", default=None, help="Default: <run_dir>/multi_llm_judge")
    parser.add_argument("--dry-run", action="store_true", help="Render prompts and config only; do not call APIs")
    parser.add_argument("--skip-pairwise", action="store_true")
    args = parser.parse_args()

    root = project_root()
    run_dir = Path(args.run_dir).resolve()
    config_path = (root / args.config).resolve() if not Path(args.config).is_absolute() else Path(args.config)
    review_dir = Path(args.review_dir).resolve() if args.review_dir else None
    output_dir = Path(args.output_dir).resolve() if args.output_dir else run_dir / "multi_llm_judge"
    output_dir.mkdir(parents=True, exist_ok=True)

    config = load_yaml(config_path)
    api_cfg = config.get("api", {})
    judges = [j for j in config.get("judges", []) if j.get("enabled", True)]
    if not judges:
        raise ValueError("No enabled judges in config")

    idea_files = idea_markdown_files(run_dir, review_dir)
    prompts_dir = output_dir / "prompts"
    prompts_dir.mkdir(exist_ok=True)

    rubric = build_rubric_prompt()
    score_prompt = build_score_prompt(idea_files)
    (prompts_dir / "score_prompt.md").write_text(rubric + "\n\n" + score_prompt, encoding="utf-8")

    all_reviews = {}
    pairwise_rows = []
    if not args.dry_run:
        mode = api_cfg.get("mode", "codex")
        api_key = os.environ.get(api_cfg.get("env_key", ""), "")
        if mode == "chat_completions" and not api_key:
            raise RuntimeError(f"Missing API key env var: {api_cfg.get('env_key')}")
        for judge in judges:
            judge_mode = judge.get("backend", mode)
            print(f"Scoring with judge: {judge['name']} ({judge['model']}) via {judge_mode}")
            if judge_mode == "codex":
                if judge.get("single_idea_requests", api_cfg.get("single_idea_requests", False)):
                    rows = []
                    for idea_index, idea_path in enumerate(idea_files, 1):
                        row = codex_exec_to_json(
                            output_dir,
                            judge["model"],
                            rubric + "\n\n" + build_single_score_prompt(idea_path),
                            f"score_prompt_{judge['name']}_{idea_index}.md",
                            f"score_{judge['name']}_{idea_index}.json",
                            "Review the single idea using the required rubric. Return only one JSON object.",
                        )
                        rows.append(row)
                        time.sleep(float(judge.get("request_sleep_seconds", api_cfg.get("request_sleep_seconds", 1.0))))
                else:
                    rows = codex_exec_to_json(
                        output_dir,
                        judge["model"],
                        rubric + "\n\n" + score_prompt,
                        f"score_prompt_{judge['name']}.md",
                        f"score_{judge['name']}.json",
                        "Review all ideas using the required rubric. Return only a JSON list.",
                    )
            elif judge_mode == "local_hf":
                rows = []
                for idea_index, idea_path in enumerate(idea_files, 1):
                    row = local_hf_to_json(
                        output_dir,
                        judge,
                        rubric + "\n\n" + build_single_score_prompt(idea_path),
                        f"score_prompt_{judge['name']}_{idea_index}.md",
                        f"score_{judge['name']}_{idea_index}.json",
                    )
                    rows.append(row)
            elif judge_mode == "ollama":
                rows = []
                for idea_path in idea_files:
                    rows.append(ollama_generate_json(judge, rubric + "\n\n" + build_single_score_prompt(idea_path)))
            else:
                content = openai_chat_completion(
                    api_cfg["base_url"],
                    api_key,
                    judge["model"],
                    [
                        {"role": "system", "content": rubric},
                        {"role": "user", "content": score_prompt},
                    ],
                    float(api_cfg.get("temperature", 0.1)),
                    int(api_cfg.get("max_tokens", 4096)),
                    int(api_cfg.get("timeout_seconds", 180)),
                )
                (output_dir / f"raw_score_{judge['name']}.txt").write_text(content, encoding="utf-8")
                rows = extract_json(content)
            rows = validate_score_rows(rows, len(idea_files), judge["name"])
            all_reviews[judge["name"]] = rows

        if not args.skip_pairwise:
            for judge in judges:
                for idx, (idea_a, idea_b) in enumerate(itertools.combinations(idea_files, 2), 1):
                    prompt = build_pairwise_prompt(idea_a, idea_b)
                    (prompts_dir / f"pairwise_{idx}_{idea_a.stem}_vs_{idea_b.stem}.md").write_text(prompt, encoding="utf-8")
                    judge_mode = judge.get("backend", mode)
                    print(f"Pairwise with judge: {judge['name']} {idea_a.name} vs {idea_b.name} via {judge_mode}")
                    if judge_mode == "codex":
                        row = codex_exec_to_json(
                            output_dir,
                            judge["model"],
                            rubric + "\n\n" + prompt,
                            f"pairwise_prompt_{judge['name']}_{idx}.md",
                            f"pairwise_{judge['name']}_{idx}.json",
                            "Compare the two ideas. Return only one JSON object.",
                        )
                    elif judge_mode == "local_hf":
                        row = local_hf_to_json(
                            output_dir,
                            judge,
                            rubric + "\n\n" + prompt,
                            f"pairwise_prompt_{judge['name']}_{idx}.md",
                            f"pairwise_{judge['name']}_{idx}.json",
                        )
                    elif judge_mode == "ollama":
                        row = ollama_generate_json(judge, rubric + "\n\n" + prompt)
                    else:
                        content = openai_chat_completion(
                            api_cfg["base_url"], api_key, judge["model"],
                            [{"role": "system", "content": rubric}, {"role": "user", "content": prompt}],
                            float(api_cfg.get("temperature", 0.1)), int(api_cfg.get("max_tokens", 4096)), int(api_cfg.get("timeout_seconds", 180)),
                        )
                        row = extract_json(content)
                    row["judge"] = judge["name"]
                    row["idea_a"] = str(idea_a)
                    row["idea_b"] = str(idea_b)
                    pairwise_rows.append(row)
                    time.sleep(0.2)

    aggregated = aggregate_scores(all_reviews, config.get("agreement_thresholds", {})) if all_reviews else []
    pairwise_summary = aggregate_pairwise(pairwise_rows, idea_files) if pairwise_rows else None

    result = {
        "run_dir": str(run_dir),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "dry_run": args.dry_run,
        "config": str(config_path),
        "judges": judges,
        "idea_files": [str(p) for p in idea_files],
        "reviews_by_judge": all_reviews,
        "aggregated_scores": aggregated,
    }
    (output_dir / "multi_judge_scores.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    if pairwise_summary:
        (output_dir / "pairwise_judge_results.json").write_text(json.dumps(pairwise_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_summary(output_dir / "multi_judge_summary_CN.md", run_dir, judges, aggregated, pairwise_summary, args.dry_run)

    print("Saved:", output_dir / "multi_judge_scores.json")
    print("Saved:", output_dir / "multi_judge_summary_CN.md")
    if pairwise_summary:
        print("Saved:", output_dir / "pairwise_judge_results.json")
    if args.dry_run:
        print("Dry run only. Prompts saved in:", prompts_dir)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
