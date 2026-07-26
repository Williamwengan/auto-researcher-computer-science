#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "for",
    "from",
    "has",
    "have",
    "in",
    "into",
    "is",
    "it",
    "may",
    "of",
    "on",
    "or",
    "over",
    "than",
    "that",
    "the",
    "their",
    "this",
    "to",
    "with",
    "without",
    "需要",
    "可能",
    "方法",
    "模型",
}


MANUAL_MARKERS = {
    "needs_manual_verification",
    "manual verification",
    "require manual verification",
    "requires manual verification",
    "manual check",
    "not directly supported",
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
        if isinstance(item, dict):
            rows.append(item)
    return rows


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_pid(item: Any) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return item.get("paper_id") or item.get("evidence_paper_id") or item.get("id") or ""
    return ""


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def textify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(textify(v) for v in value)
    if isinstance(value, dict):
        return " ".join(f"{k} {textify(v)}" for k, v in value.items())
    return str(value)


def tokens(text: str) -> set[str]:
    raw = re.findall(r"[A-Za-z][A-Za-z0-9_\-]{2,}|[\u4e00-\u9fff]{2,}", text.lower())
    out = set()
    for tok in raw:
        if tok in STOPWORDS:
            continue
        if len(tok) < 3 and not re.search(r"[\u4e00-\u9fff]", tok):
            continue
        out.add(tok)
    return out


def contains_manual_marker(text: str) -> bool:
    low = text.lower()
    return any(marker in low for marker in MANUAL_MARKERS)


def paper_text(paper: dict[str, Any]) -> str:
    return " ".join(
        [
            str(paper.get("title", "")),
            str(paper.get("abstract", "")),
            textify(paper.get("baseline_tags", [])),
            textify(paper.get("matched_terms", [])),
        ]
    )


def card_text(card: dict[str, Any]) -> str:
    return " ".join(
        [
            str(card.get("baseline_name", "")),
            str(card.get("baseline_type", "")),
            str(card.get("claimed_task", "")),
            textify(card.get("known_limitations", [])),
            textify(card.get("supported_metrics", [])),
            textify(card.get("reusable_components", [])),
            textify(card.get("unsupported_claims", [])),
        ]
    )


def evidence_ids_from_claim(item: Any) -> list[str]:
    if isinstance(item, str):
        return [item] if (":" in item or item.startswith("needs_")) else []
    if not isinstance(item, dict):
        return []
    keys = [
        "evidence_ids",
        "paper_ids",
        "evidence_paper_ids",
        "paper_id",
        "evidence",
    ]
    ids: list[str] = []
    for key in keys:
        value = item.get(key)
        if value is None:
            continue
        for entry in as_list(value):
            pid = normalize_pid(entry)
            if pid:
                ids.append(pid)
    return ids


def claim_text_from_item(item: Any) -> str:
    if isinstance(item, str):
        return ""
    if not isinstance(item, dict):
        return textify(item)
    fields = [
        "baseline",
        "weakness",
        "claim",
        "limitation",
        "improvement",
        "why_relevant",
        "evidence",
    ]
    return " ".join(str(item.get(field, "")) for field in fields if item.get(field))


def extract_claims(idea: dict[str, Any], idea_index: int) -> list[dict[str, Any]]:
    title = idea.get("title", f"idea_{idea_index}")
    claims: list[dict[str, Any]] = []

    for idx, item in enumerate(as_list(idea.get("baseline_weakness_evidence")), start=1):
        claim_text = claim_text_from_item(item)
        evidence_ids = evidence_ids_from_claim(item)
        baseline = item.get("baseline", "") if isinstance(item, dict) else ""
        if isinstance(item, str) and item:
            claims.append(
                {
                    "idea_index": idea_index,
                    "idea_title": title,
                    "claim_type": "paper_reference_without_claim_text",
                    "claim_index": idx,
                    "baseline": baseline,
                    "claim_text": "",
                    "evidence_ids": evidence_ids,
                    "raw_claim": item,
                }
            )
        else:
            claims.append(
                {
                    "idea_index": idea_index,
                    "idea_title": title,
                    "claim_type": "baseline_weakness",
                    "claim_index": idx,
                    "baseline": baseline,
                    "claim_text": claim_text,
                    "evidence_ids": evidence_ids,
                    "raw_claim": item,
                }
            )

    proposed_text = " ".join(
        [
            str(idea.get("new_component", "")),
            str(idea.get("algorithmic_objective", "")),
            textify(idea.get("minimal_new_module", {}).get("why_baseline_cannot_do_this", ""))
            if isinstance(idea.get("minimal_new_module"), dict)
            else "",
        ]
    ).strip()
    if proposed_text:
        claims.append(
            {
                "idea_index": idea_index,
                "idea_title": title,
                "claim_type": "proposed_mechanism_context",
                "claim_index": 1,
                "baseline": "",
                "claim_text": proposed_text,
                "evidence_ids": [normalize_pid(x) for x in as_list(idea.get("evidence_paper_ids")) if normalize_pid(x)],
                "raw_claim": proposed_text,
            }
        )

    for idx, item in enumerate(as_list(idea.get("unsupported_or_weak_claims")), start=1):
        claim_text = textify(item)
        claims.append(
            {
                "idea_index": idea_index,
                "idea_title": title,
                "claim_type": "declared_unsupported_or_weak",
                "claim_index": idx,
                "baseline": "",
                "claim_text": claim_text,
                "evidence_ids": evidence_ids_from_claim(item),
                "raw_claim": item,
            }
        )
    return claims


def nearest_card_text(baseline: str, cards: list[dict[str, Any]]) -> str:
    if not baseline:
        return ""
    low = baseline.lower()
    matched = []
    for card in cards:
        name = str(card.get("baseline_name", "")).lower()
        if low == name or low in name or name in low:
            matched.append(card_text(card))
    return " ".join(matched)


def verify_claim(
    claim: dict[str, Any],
    paper_by_id: dict[str, dict[str, Any]],
    cards: list[dict[str, Any]],
    min_overlap: int,
) -> dict[str, Any]:
    claim_text = claim.get("claim_text", "")
    evidence_ids = [pid for pid in claim.get("evidence_ids", []) if pid]
    valid_ids = [pid for pid in evidence_ids if pid in paper_by_id]
    unknown_ids = [pid for pid in evidence_ids if pid not in paper_by_id and not pid.startswith("needs_")]
    manual_ids = [pid for pid in evidence_ids if pid.startswith("needs_")]
    claim_tokens = tokens(claim_text)
    baseline = claim.get("baseline", "")
    baseline_tokens = tokens(baseline)
    support_details = []
    evidence_overlap = set()

    for pid in valid_ids:
        paper = paper_by_id[pid]
        p_text = paper_text(paper)
        p_tokens = tokens(p_text)
        overlap = sorted(claim_tokens & p_tokens)
        evidence_overlap.update(overlap)
        support_details.append(
            {
                "paper_id": pid,
                "title": paper.get("title", ""),
                "year": paper.get("year", ""),
                "url": paper.get("url", ""),
                "overlap_terms": overlap[:20],
                "overlap_count": len(overlap),
                "has_abstract": bool(paper.get("abstract")),
            }
        )

    card_support_text = nearest_card_text(baseline, cards)
    card_overlap = sorted(claim_tokens & tokens(card_support_text))
    baseline_seen_in_evidence = False
    if baseline_tokens:
        for pid in valid_ids:
            if baseline_tokens & tokens(paper_text(paper_by_id[pid])):
                baseline_seen_in_evidence = True
                break
        if baseline_tokens & tokens(card_support_text):
            baseline_seen_in_evidence = True

    reasons = []
    status = "needs_manual_check"

    if claim["claim_type"] == "declared_unsupported_or_weak":
        status = "declared_unsupported"
        reasons.append("The idea already declares this as unsupported or weak; it should not be treated as verified evidence.")
    elif claim["claim_type"] == "paper_reference_without_claim_text":
        status = "needs_manual_check"
        reasons.append("The field contains paper ids but no explicit weakness/claim text to verify.")
    elif not claim_text.strip():
        status = "needs_manual_check"
        reasons.append("Claim text is empty.")
    elif contains_manual_marker(claim_text) or manual_ids:
        status = "needs_manual_check"
        reasons.append("Claim or evidence id explicitly requests manual verification.")
    elif not evidence_ids:
        status = "unsupported"
        reasons.append("No evidence paper ids are attached to this claim.")
    elif unknown_ids:
        status = "unsupported"
        reasons.append(f"Unknown evidence ids: {unknown_ids}")
    elif not valid_ids:
        status = "unsupported"
        reasons.append("No valid evidence paper ids are available.")
    else:
        overlap_count = len(evidence_overlap)
        card_overlap_count = len(card_overlap)
        if claim["claim_type"] == "proposed_mechanism_context":
            if overlap_count >= min_overlap or card_overlap_count >= min_overlap:
                status = "weakly_supported"
                reasons.append(
                    "Evidence supports related components/context, but a new proposed mechanism is not expected to be directly proven by prior papers."
                )
            else:
                status = "needs_manual_check"
                reasons.append("Proposed mechanism has valid papers but limited term overlap; manual check is needed.")
        elif overlap_count >= min_overlap and (not baseline or baseline_seen_in_evidence):
            status = "supported"
            reasons.append("Attached evidence overlaps with the claim text and baseline context.")
        elif overlap_count >= min_overlap or card_overlap_count >= min_overlap:
            status = "weakly_supported"
            reasons.append("Attached evidence has partial textual support, but baseline-specific support is incomplete.")
        else:
            status = "needs_manual_check"
            reasons.append("Evidence ids exist, but title/abstract/card text has weak overlap with the claim.")

    return {
        **claim,
        "status": status,
        "valid_evidence_ids": valid_ids,
        "unknown_evidence_ids": unknown_ids,
        "manual_evidence_ids": manual_ids,
        "claim_terms": sorted(claim_tokens)[:40],
        "evidence_overlap_terms": sorted(evidence_overlap)[:40],
        "card_overlap_terms": card_overlap[:40],
        "baseline_seen_in_evidence": baseline_seen_in_evidence,
        "support_details": support_details,
        "reasons": reasons,
    }


def write_cn_report(path: Path, summary: dict[str, Any], results: list[dict[str, Any]]) -> None:
    counts = summary["status_counts"]
    lines = [
        "# v0.7 Reference Claim Verification 报告",
        "",
        f"- Run dir: `{summary['run_dir']}`",
        f"- 生成时间: {summary['generated_at']}",
        f"- Idea 数: {summary['ideas']}",
        f"- 论文证据数: {summary['papers']}",
        f"- Baseline card 数: {summary['baseline_cards']}",
        f"- Claim 总数: {summary['claims']}",
        f"- supported: {counts.get('supported', 0)}",
        f"- weakly_supported: {counts.get('weakly_supported', 0)}",
        f"- needs_manual_check: {counts.get('needs_manual_check', 0)}",
        f"- unsupported: {counts.get('unsupported', 0)}",
        f"- declared_unsupported: {counts.get('declared_unsupported', 0)}",
        f"- verification pass rate: {summary['verification_pass_rate']}",
        "",
        "## 说明",
        "",
        "本脚本做的是自动证据一致性检查，不等同于专家审稿。它主要检查：",
        "",
        "1. claim 是否绑定了真实存在的 paper id；",
        "2. claim 文本是否和论文标题/摘要/baseline card 中的限制或任务文本有词面支持；",
        "3. 显式标记 `needs_manual_verification` 或 unsupported 的 claim 是否被保留为人工复核项；",
        "4. proposed mechanism 是否至少有相关组件级证据，而不是伪装成已被前人证明。",
        "",
        "## 按 Idea 汇总",
        "",
    ]
    by_idea: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in results:
        by_idea[item["idea_title"]].append(item)
    for title, items in by_idea.items():
        c = Counter(item["status"] for item in items)
        lines.append(f"### {title}")
        lines.append(
            f"- claims={len(items)}, supported={c.get('supported', 0)}, "
            f"weakly_supported={c.get('weakly_supported', 0)}, "
            f"needs_manual_check={c.get('needs_manual_check', 0)}, "
            f"unsupported={c.get('unsupported', 0)}, declared_unsupported={c.get('declared_unsupported', 0)}"
        )
        for item in items:
            if item["status"] in {"unsupported", "needs_manual_check", "declared_unsupported"}:
                claim = item.get("claim_text") or str(item.get("raw_claim", ""))
                claim = claim.replace("\n", " ")[:240]
                lines.append(f"  - `{item['status']}` [{item['claim_type']}]: {claim}")
                if item.get("reasons"):
                    lines.append(f"    - reason: {item['reasons'][0]}")
        lines.append("")

    lines.extend(
        [
            "## 高风险 Claim 明细",
            "",
        ]
    )
    high_risk = [item for item in results if item["status"] in {"unsupported", "needs_manual_check"}]
    if not high_risk:
        lines.append("- 无。")
    else:
        for item in high_risk:
            claim = item.get("claim_text") or str(item.get("raw_claim", ""))
            claim = claim.replace("\n", " ")[:360]
            lines.append(f"### {item['idea_title']} / {item['claim_type']}")
            lines.append(f"- Status: `{item['status']}`")
            lines.append(f"- Claim: {claim if claim else '(no explicit claim text)'}")
            lines.append(f"- Evidence ids: {item.get('evidence_ids', [])}")
            lines.append(f"- Valid evidence ids: {item.get('valid_evidence_ids', [])}")
            if item.get("unknown_evidence_ids"):
                lines.append(f"- Unknown evidence ids: {item['unknown_evidence_ids']}")
            if item.get("evidence_overlap_terms"):
                lines.append(f"- Overlap terms: {item['evidence_overlap_terms'][:20]}")
            if item.get("reasons"):
                lines.append(f"- Reason: {item['reasons'][0]}")
            lines.append("")

    lines.extend(
        [
            "## 使用建议",
            "",
            "- `supported`：可以作为自动证据绑定结果使用。",
            "- `weakly_supported`：可以保留，但报告中应写成“相关证据支持”，不要写成已严格证明。",
            "- `needs_manual_check`：进入人工复核或下一轮检索。",
            "- `unsupported`：不应进入最终 idea，除非补充证据或改写 claim。",
            "- `declared_unsupported`：说明系统正确保留了不确定性，不应被当成失败；但最终报告要如实说明。",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def verify_run(run_dir: Path, min_overlap: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    ideas_path = run_dir / "focused_ideas.json"
    papers_path = run_dir / "papers.jsonl"
    cards_path = run_dir / "evidence_baseline_cards.jsonl"
    if not ideas_path.exists():
        raise FileNotFoundError(ideas_path)
    ideas = read_json(ideas_path)
    if not isinstance(ideas, list):
        raise TypeError(f"{ideas_path} must be a JSON list")
    papers = read_jsonl(papers_path)
    cards = read_jsonl(cards_path)
    paper_by_id = {p.get("paper_id"): p for p in papers if p.get("paper_id")}

    results = []
    for idx, idea in enumerate(ideas, start=1):
        for claim in extract_claims(idea, idx):
            results.append(verify_claim(claim, paper_by_id, cards, min_overlap=min_overlap))

    counts = Counter(item["status"] for item in results)
    pass_count = counts.get("supported", 0) + counts.get("weakly_supported", 0) + counts.get("declared_unsupported", 0)
    summary = {
        "run_dir": str(run_dir),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "ideas": len(ideas),
        "papers": len(papers),
        "baseline_cards": len(cards),
        "claims": len(results),
        "status_counts": dict(counts),
        "verification_pass_rate": round(pass_count / len(results), 3) if results else 0.0,
        "min_overlap": min_overlap,
    }
    return summary, results


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify whether idea claims are supported by attached paper evidence.")
    parser.add_argument("run_dirs", type=Path, nargs="+", help="One or more evidence-grounded idea run directories.")
    parser.add_argument("--min-overlap", type=int, default=2, help="Minimum claim/evidence token overlap for support.")
    parser.add_argument("--summary-output", type=Path, default=None, help="Optional aggregate CN markdown report.")
    parser.add_argument("--fail-on-unsupported", action="store_true")
    args = parser.parse_args()

    aggregate = []
    unsupported_total = 0
    for run_dir in args.run_dirs:
        run_dir = run_dir.resolve()
        summary, results = verify_run(run_dir, min_overlap=args.min_overlap)
        write_json(run_dir / "claim_verification_report.json", {"summary": summary, "claims": results})
        write_cn_report(run_dir / "claim_verification_report_CN.md", summary, results)
        aggregate.append(summary)
        unsupported_total += summary["status_counts"].get("unsupported", 0)
        print("Reference claim verification complete")
        print("Run dir:", run_dir)
        print("Claims:", summary["claims"])
        print("Status counts:", summary["status_counts"])
        print("Pass rate:", summary["verification_pass_rate"])
        print("Report:", run_dir / "claim_verification_report_CN.md")

    if args.summary_output:
        lines = [
            "# v0.7 Reference Claim Verification 汇总报告",
            "",
            "| Run | Ideas | Papers | Claims | Supported | Weak | Manual | Unsupported | Declared Unsupported | Pass Rate |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for s in aggregate:
            c = s["status_counts"]
            lines.append(
                f"| `{s['run_dir']}` | {s['ideas']} | {s['papers']} | {s['claims']} | "
                f"{c.get('supported', 0)} | {c.get('weakly_supported', 0)} | "
                f"{c.get('needs_manual_check', 0)} | {c.get('unsupported', 0)} | "
                f"{c.get('declared_unsupported', 0)} | {s['verification_pass_rate']} |"
            )
        lines.extend(
            [
                "",
                "## 解释",
                "",
                "- Pass rate 将 `supported`、`weakly_supported`、`declared_unsupported` 计为通过。",
                "- `needs_manual_check` 不直接判失败，但代表需要人工读论文或补检索。",
                "- `unsupported` 代表自动检查下缺少有效证据，不应直接进入最终报告。",
            ]
        )
        args.summary_output.parent.mkdir(parents=True, exist_ok=True)
        args.summary_output.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("Aggregate report:", args.summary_output)

    if args.fail_on_unsupported and unsupported_total:
        sys.exit(1)


if __name__ == "__main__":
    main()
