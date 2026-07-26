#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def find_review_file(run_dir: Path, idx: int) -> Path:
    path = run_dir / "review_ready_ideas" / f"idea_{idx:02d}.md"
    if path.exists():
        return path
    raise FileNotFoundError(path)


def title_list(run_dir: Path) -> list[str]:
    ideas = load_json(run_dir / "focused_ideas.json")
    if not isinstance(ideas, list):
        raise TypeError(f"{run_dir}/focused_ideas.json must be a JSON list")
    return [idea.get("title", f"idea_{idx}") for idx, idea in enumerate(ideas, start=1)]


def make_review_item(pair_id: str, domain: str, title: str, a_path: Path, b_path: Path) -> dict:
    sheet = {
        "pair_id": pair_id,
        "domain": domain,
        "idea_title": title,
        "preferred": None,
        "preference_strength": None,
        "preference_rationale": "",
        "tie_allowed": True,
        "scores": {
            "A": {dim: None for dim in DIMENSIONS},
            "B": {dim: None for dim in DIMENSIONS},
        },
        "rationales": {
            "A": "",
            "B": "",
        },
        "implementation_concerns": {
            "A": [],
            "B": [],
        },
        "review_files": {
            "A": str(a_path),
            "B": str(b_path),
        },
    }
    return sheet


def write_pair_markdown(path: Path, pair_id: str, domain: str, title: str, a_text: str, b_text: str) -> None:
    content = f"""# Blind A/B Review Pair {pair_id}

Domain: {domain}

Idea title: {title}

Instructions:

- Do not guess which version is before or after repair.
- Judge which version is more scientifically useful and implementation-ready.
- Prefer the version that has a clearer mechanism, stronger experiment design, stronger evidence use, and more realistic failure criteria.
- Do not reward length by itself.
- If both are equally useful, choose `tie`.

## Version A

{a_text}

---

## Version B

{b_text}
"""
    path.write_text(content, encoding="utf-8")


def write_instructions(path: Path, output_dir: Path) -> None:
    content = f"""# v0.6 匿名 A/B 盲评说明

本目录用于评估 v0.5 repair 是否真的提升 idea 质量，而不是只提高规则评分。

## 审查原则

请 reviewer 不要尝试判断哪个版本是修复前或修复后。

每个 pair 中包含：

```text
Version A
Version B
```

请从科研 idea 质量角度判断哪个更值得进入 MVP 或后续实验。

重点看：

1. 是否有真实、非模板化的机制；
2. 是否明确基于 baseline 的具体缺陷；
3. 实验计划是否可执行；
4. 指标和阈值是否合理，而不是为了好看硬凑；
5. negative control 是否能真正排除伪提升；
6. evidence 是否服务于 claim，而不是只堆引用；
7. 是否存在过度工程拼接、换名、空泛描述。

## 评分维度

每个版本 A/B 都按 1-10 分填写：

```text
novelty
feasibility
expected_effectiveness
experimental_rigor
baseline_grounding
mechanism_specificity
implementation_readiness
overall
```

同时填写：

```text
preferred: A / B / tie
preference_strength: 1-3
preference_rationale
```

## 需要填写的文件

复制下面文件作为 reviewer 版本：

```text
{output_dir / "blind_review_sheet.json"}
```

例如：

```bash
cp {output_dir / "blind_review_sheet.json"} {output_dir / "blind_review_reviewer01.json"}
nano {output_dir / "blind_review_reviewer01.json"}
```

注意：`answer_key_private.json` 不要给 reviewer 看。
"""
    path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create blinded A/B review package for before/after idea comparison.")
    parser.add_argument("--before-run", required=True, type=Path)
    parser.add_argument("--after-run", required=True, type=Path)
    parser.add_argument("--domain", required=True)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=20260712)
    args = parser.parse_args()

    before_run = args.before_run.resolve()
    after_run = args.after_run.resolve()
    if args.output_dir:
        output_dir = args.output_dir.resolve()
    else:
        tag = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("outputs") / f"v06_blind_ab_review_{args.domain}_{tag}"
        output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    pair_dir = output_dir / "pairs"
    pair_dir.mkdir(parents=True, exist_ok=True)

    before_titles = title_list(before_run)
    after_titles = title_list(after_run)
    if len(before_titles) != len(after_titles):
        raise ValueError("Before and after runs must have the same number of ideas")

    rng = random.Random(args.seed)
    review_items = []
    answer_key = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "domain": args.domain,
        "seed": args.seed,
        "before_run": str(before_run),
        "after_run": str(after_run),
        "pairs": [],
    }

    for idx, title in enumerate(before_titles, start=1):
        pair_id = f"{args.domain}_pair_{idx:02d}"
        before_text = read_text(find_review_file(before_run, idx))
        after_text = read_text(find_review_file(after_run, idx))
        assignments = ["before", "after"]
        rng.shuffle(assignments)
        a_label, b_label = assignments
        a_text = before_text if a_label == "before" else after_text
        b_text = before_text if b_label == "before" else after_text

        pair_path = pair_dir / f"{pair_id}.md"
        write_pair_markdown(pair_path, pair_id, args.domain, title, a_text, b_text)
        review_items.append(make_review_item(pair_id, args.domain, title, pair_path, pair_path))
        answer_key["pairs"].append(
            {
                "pair_id": pair_id,
                "idea_index": idx,
                "idea_title": title,
                "A": a_label,
                "B": b_label,
                "before_file": str(find_review_file(before_run, idx)),
                "after_file": str(find_review_file(after_run, idx)),
                "pair_file": str(pair_path),
            }
        )

    (output_dir / "blind_review_sheet.json").write_text(
        json.dumps(review_items, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "answer_key_private.json").write_text(
        json.dumps(answer_key, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_instructions(output_dir / "README_REVIEW_CN.md", output_dir)

    print("Blind A/B review package created")
    print("Output dir:", output_dir)
    print("Pairs:", len(review_items))
    print("Review sheet:", output_dir / "blind_review_sheet.json")
    print("Private answer key:", output_dir / "answer_key_private.json")


if __name__ == "__main__":
    main()
