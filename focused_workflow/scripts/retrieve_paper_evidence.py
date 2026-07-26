#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
import urllib.parse
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
from pathlib import Path

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


OPENALEX_URL = "https://api.openalex.org/works"
ARXIV_URL = "https://export.arxiv.org/api/query"
S2_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
PROXY_URL: str | None = None


SPECIAL_BASELINE_QUERIES = {
    "text2room": [
        "Text2Room extracting textured 3D meshes from 2D text-to-image models",
        "Text2Room textured 3D room generation",
    ],
    "scenescape": [
        "SceneScape text driven consistent scene generation",
        "SceneScape long-term video generation 3D scene",
    ],
    "wonderjourney": [
        "WonderJourney going from anywhere to everywhere 3D scene generation",
        "WonderJourney single image 3D scene generation",
    ],
    "indoor_nerf_prior_methods": [
        "indoor NeRF prior room layout scene reconstruction",
        "NeRF indoor scene reconstruction room layout prior",
    ],
    "layout_estimation_baselines": [
        "single image room layout estimation indoor scene",
        "HorizonNet single image room layout estimation",
    ],
    "image_to_3d_generation_baselines": [
        "single image to 3D scene generation indoor",
        "image conditioned 3D scene generation indoor",
    ],
    "monocular_depth_estimation": [
        "monocular depth estimation indoor scene benchmark",
        "MiDaS monocular depth estimation",
    ],
    "dust3r": [
        "DUSt3R geometric 3D vision from unconstrained image collections",
        "DUSt3R dense stereo 3D reconstruction",
    ],
    "mast3r": [
        "MASt3R matching and stereo 3D reconstruction",
        "MASt3R-SLAM 3D reconstruction",
    ],
    "3d gaussian splatting": [
        "3D Gaussian Splatting for real-time radiance field rendering",
        "Gaussian Splatting 3D scene reconstruction",
    ],
    "nerf": [
        "NeRF neural radiance fields view synthesis",
        "NeRF indoor scene reconstruction",
    ],
    "3d-front": [
        "3D-FRONT 3D furnished rooms with layouts and semantics",
        "3D-FRONT dataset indoor scene synthesis",
    ],
    "3d-future": [
        "3D-FUTURE 3D furniture shape with texture",
        "3D-FUTURE dataset furniture indoor scenes",
    ],
    "objectfolder": [
        "ObjectFolder dataset implicit visual auditory tactile representations",
        "ObjectFolder multisensory object dataset visual auditory tactile representations",
    ],
    "objectfolder2.0": [
        "ObjectFolder 2.0 multisensory object dataset sim2real transfer",
        "ObjectFolder 2.0 visual tactile acoustic household objects",
        "ObjectFolder 2.0 contact localization shape reconstruction object scale estimation",
    ],
    "objectfolder 2.0": [
        "ObjectFolder 2.0 multisensory object dataset sim2real transfer",
        "ObjectFolder 2.0 visual tactile acoustic household objects",
        "ObjectFolder 2.0 contact localization shape reconstruction object scale estimation",
    ],
}


def load_yaml(path: Path) -> dict:
    if yaml is None:
        raise RuntimeError("PyYAML is required to read task specs.")
    return yaml.safe_load(path.read_text())


def normalize_space(text: str | None) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def flatten_baselines(candidate_baselines) -> list[dict]:
    items = []
    if isinstance(candidate_baselines, dict):
        for group, names in candidate_baselines.items():
            if isinstance(names, list):
                for name in names:
                    items.append({"name": str(name), "type": str(group)})
            elif isinstance(names, dict):
                for sub, subnames in names.items():
                    if isinstance(subnames, list):
                        for name in subnames:
                            items.append({"name": str(name), "type": f"{group}.{sub}"})
    return items


def task_terms(task: dict) -> list[str]:
    chunks = [
        task.get("domain", ""),
        task.get("focus_area", ""),
        task.get("research_goal", ""),
    ]
    for value in task.get("task_types", []) or []:
        chunks.append(str(value))
    text = " ".join(chunks).lower()
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_\-]{2,}", text)
    stop = {
        "the", "and", "for", "with", "from", "that", "this", "into", "every",
        "single", "input", "output", "including", "generate", "research",
        "ideas", "workflow", "computer", "vision",
    }
    return sorted({t for t in tokens if t not in stop})[:30]


def build_queries(
    task: dict,
    baselines: list[dict],
    max_baselines: int,
    include_recency_queries: bool = False,
) -> list[dict]:
    focus = normalize_space(task.get("focus_area", ""))
    goal = normalize_space(task.get("research_goal", ""))
    short_focus = " ".join(focus.split()[:10])
    queries = []
    for base in baselines[:max_baselines]:
        name = base["name"]
        special_queries = SPECIAL_BASELINE_QUERIES.get(name.lower(), [])
        for query_text in special_queries:
            queries.append(
                {
                    "baseline_name": name,
                    "baseline_type": base["type"],
                    "query": query_text,
                }
            )
        queries.append(
            {
                "baseline_name": name,
                "baseline_type": base["type"],
                "query": f"{name} {short_focus}",
            }
        )
        queries.append(
            {
                "baseline_name": name,
                "baseline_type": base["type"],
                "query": f"{name} benchmark metrics {goal[:80]}",
            }
        )
        if include_recency_queries:
            queries.append(
                {
                    "baseline_name": name,
                    "baseline_type": base["type"],
                    "query": f"{name} recent advances 2024 2025 2026 {short_focus}",
                }
            )
            queries.append(
                {
                    "baseline_name": name,
                    "baseline_type": base["type"],
                    "query": f"latest {short_focus} methods benchmark 2025 2026",
                }
            )
    return queries


def make_id(source: str, raw_id: str | None, title: str) -> str:
    raw = raw_id or re.sub(r"[^a-zA-Z0-9]+", "-", title.lower()).strip("-")[:80]
    return f"{source}:{raw}"


def paper_record(
    *,
    source: str,
    raw_id: str | None,
    title: str,
    year: int | None,
    authors: list[str],
    venue: str,
    url: str,
    doi: str,
    abstract: str,
    baseline_tags: list[str],
    retrieval_query: str,
) -> dict:
    return {
        "paper_id": make_id(source, raw_id, title),
        "title": normalize_space(title),
        "year": year,
        "authors": authors[:12],
        "venue": normalize_space(venue),
        "source": source,
        "url": url,
        "doi": doi,
        "abstract": normalize_space(abstract),
        "baseline_tags": sorted(set(baseline_tags)),
        "retrieval_query": retrieval_query,
        "matched_terms": [],
        "task_relevance": "",
        "relevance_score": 0.0,
    }


def retry_delay(exc: urllib.error.HTTPError, attempt: int) -> float:
    retry_after = exc.headers.get("Retry-After") if exc.headers else None
    if retry_after and retry_after.isdigit():
        return min(60.0, float(retry_after))
    return min(60.0, 2.0 * (attempt + 1) ** 2)


def build_opener():
    if PROXY_URL:
        return urllib.request.build_opener(
            urllib.request.ProxyHandler({"http": PROXY_URL, "https": PROXY_URL})
        )
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def urlopen_json(url: str, timeout: int = 30, retries: int = 3) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "ResearchArena-v0.5/0.1"})
    opener = build_opener()
    for attempt in range(retries + 1):
        try:
            with opener.open(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt >= retries:
                raise
            time.sleep(retry_delay(exc, attempt))


def urlopen_text(url: str, timeout: int = 30, retries: int = 3) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "ResearchArena-v0.5/0.1"})
    opener = build_opener()
    for attempt in range(retries + 1):
        try:
            with opener.open(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt >= retries:
                raise
            time.sleep(retry_delay(exc, attempt))


def search_openalex(query: dict, per_page: int, min_year: int | None = None) -> list[dict]:
    params = {
        "search": query["query"],
        "per-page": str(per_page),
        "sort": "relevance_score:desc",
    }
    if min_year:
        params["filter"] = f"from_publication_date:{min_year}-01-01"
    url = OPENALEX_URL + "?" + urllib.parse.urlencode(params)
    data = urlopen_json(url)
    records = []
    for item in data.get("results", []):
        authors = []
        for auth in item.get("authorships", []) or []:
            name = ((auth.get("author") or {}).get("display_name")) or ""
            if name:
                authors.append(name)
        records.append(
            paper_record(
                source="openalex",
                raw_id=(item.get("id") or "").rsplit("/", 1)[-1],
                title=item.get("display_name") or "",
                year=item.get("publication_year"),
                authors=authors,
                venue=((item.get("primary_location") or {}).get("source") or {}).get("display_name") or "",
                url=item.get("doi") or item.get("id") or "",
                doi=item.get("doi") or "",
                abstract=invert_openalex_abstract(item.get("abstract_inverted_index")),
                baseline_tags=[query["baseline_name"]],
                retrieval_query=query["query"],
            )
        )
    return records


def invert_openalex_abstract(index) -> str:
    if not isinstance(index, dict):
        return ""
    positions = []
    for word, inds in index.items():
        for pos in inds:
            positions.append((pos, word))
    return " ".join(word for _, word in sorted(positions))


def search_arxiv(query: dict, per_page: int) -> list[dict]:
    params = {
        "search_query": f"all:{query['query']}",
        "start": "0",
        "max_results": str(per_page),
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    xml_text = urlopen_text(ARXIV_URL + "?" + urllib.parse.urlencode(params))
    root = ET.fromstring(xml_text)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    records = []
    for entry in root.findall("a:entry", ns):
        title = entry.findtext("a:title", default="", namespaces=ns)
        summary = entry.findtext("a:summary", default="", namespaces=ns)
        raw_id = entry.findtext("a:id", default="", namespaces=ns).rsplit("/", 1)[-1]
        published = entry.findtext("a:published", default="", namespaces=ns)
        year = int(published[:4]) if published[:4].isdigit() else None
        authors = [a.findtext("a:name", default="", namespaces=ns) for a in entry.findall("a:author", ns)]
        records.append(
            paper_record(
                source="arxiv",
                raw_id=raw_id,
                title=title,
                year=year,
                authors=[a for a in authors if a],
                venue="arXiv",
                url=f"https://arxiv.org/abs/{raw_id}",
                doi="",
                abstract=summary,
                baseline_tags=[query["baseline_name"]],
                retrieval_query=query["query"],
            )
        )
    return records


def search_semantic_scholar(query: dict, per_page: int) -> list[dict]:
    params = {
        "query": query["query"],
        "limit": str(per_page),
        "fields": "title,year,authors,venue,url,abstract,externalIds",
    }
    data = urlopen_json(S2_URL + "?" + urllib.parse.urlencode(params))
    records = []
    for item in data.get("data", []):
        ext = item.get("externalIds") or {}
        records.append(
            paper_record(
                source="semanticscholar",
                raw_id=item.get("paperId"),
                title=item.get("title") or "",
                year=item.get("year"),
                authors=[a.get("name", "") for a in item.get("authors", []) if a.get("name")],
                venue=item.get("venue") or "",
                url=item.get("url") or "",
                doi=ext.get("DOI") or "",
                abstract=item.get("abstract") or "",
                baseline_tags=[query["baseline_name"]],
                retrieval_query=query["query"],
            )
        )
    return records


def dedupe(records: list[dict]) -> list[dict]:
    merged = {}
    for rec in records:
        key = (rec.get("doi") or rec.get("url") or rec.get("title", "").lower()).strip()
        if not key:
            key = rec["paper_id"]
        if key in merged:
            old = merged[key]
            old["baseline_tags"] = sorted(set(old["baseline_tags"]) | set(rec["baseline_tags"]))
            if len(rec.get("abstract", "")) > len(old.get("abstract", "")):
                old["abstract"] = rec["abstract"]
            if not old.get("url") and rec.get("url"):
                old["url"] = rec["url"]
            if not old.get("doi") and rec.get("doi"):
                old["doi"] = rec["doi"]
        else:
            merged[key] = rec
    return list(merged.values())


def filter_records_by_min_year(records: list[dict], min_year: int | None) -> list[dict]:
    if not min_year:
        return records
    return [rec for rec in records if isinstance(rec.get("year"), int) and rec["year"] >= min_year]


def score_records(
    records: list[dict],
    task: dict,
    baselines: list[dict],
    recency_weight: float = 1.0,
    recent_bonus_year: int | None = None,
    recent_bonus: float = 0.0,
) -> list[dict]:
    terms = task_terms(task)
    baseline_names = [b["name"].lower() for b in baselines]
    current_year = datetime.now().year
    for rec in records:
        text = f"{rec.get('title','')} {rec.get('abstract','')}".lower()
        matched = [t for t in terms if t.lower() in text]
        baseline_hits = [b for b in baseline_names if b and b in text]
        year = rec.get("year") or 0
        recency = max(0.0, 1.0 - max(0, current_year - year) / 12.0) if year else 0.0
        score = len(matched) * 1.0 + len(baseline_hits) * 2.0 + recency_weight * recency
        if recent_bonus_year and year and year >= recent_bonus_year:
            score += recent_bonus
        if rec.get("abstract"):
            score += 1.0
        rec["matched_terms"] = matched[:20]
        rec["relevance_score"] = round(score, 3)
        if score >= 6:
            rec["task_relevance"] = "strong"
        elif score >= 3:
            rec["task_relevance"] = "medium"
        else:
            rec["task_relevance"] = "weak"
    return sorted(records, key=lambda x: x["relevance_score"], reverse=True)


def infer_limitations(baseline_name: str, task: dict) -> list[str]:
    name = baseline_name.lower()
    focus = (task.get("focus_area") or "").lower()
    if "patchcore" in name:
        return [
            "Nearest-neighbor normal memory may be sensitive to reference shift or contaminated normal banks.",
            "Patch anomaly heatmaps do not by themselves provide evidence-grounded inspection reports.",
        ]
    if "clip" in name or "vlm" in name or "llava" in name or "qwen" in name:
        return [
            "Semantic predictions may be unsupported by localized visual evidence.",
            "Prompt-sensitive predictions require calibration or verification.",
        ]
    if "sam" in name:
        return [
            "Promptable masks may segment salient regions rather than task-specific failure regions.",
            "Mask refinement needs a selection policy and negative controls.",
        ]
    if "physical" in focus or "property" in focus:
        return [
            "Single RGB images may not reveal hidden material composition.",
            "Exact physical-property labels may require proxy, interval, or uncertainty-aware supervision.",
        ]
    return ["Limitations require manual verification against retrieved evidence."]


def build_evidence_cards(records: list[dict], baselines: list[dict], task: dict, top_k: int) -> list[dict]:
    by_base = defaultdict(list)
    for rec in records:
        for tag in rec.get("baseline_tags", []):
            by_base[tag].append(rec)

    metrics = []
    if isinstance(task.get("metrics"), dict):
        for values in task["metrics"].values():
            if isinstance(values, list):
                metrics.extend(values)

    cards = []
    for base in baselines:
        name = base["name"]
        papers = sorted(by_base.get(name, []), key=lambda x: x.get("relevance_score", 0), reverse=True)[:top_k]
        evidence = [
            {
                "paper_id": p["paper_id"],
                "title": p["title"],
                "year": p.get("year"),
                "url": p.get("url"),
                "task_relevance": p.get("task_relevance"),
                "relevance_score": p.get("relevance_score"),
            }
            for p in papers
        ]
        unsupported = []
        if not evidence:
            unsupported.append("No retrieved paper evidence for this baseline; claims must be manually verified.")
        cards.append(
            {
                "baseline_name": name,
                "baseline_type": base["type"],
                "claimed_task": normalize_space(task.get("focus_area", "")),
                "evidence_papers": evidence,
                "supported_metrics": metrics[:12],
                "known_limitations": infer_limitations(name, task),
                "reusable_components": [
                    f"Use {name} as a direct baseline or reusable module only where evidence supports its task fit."
                ],
                "evidence_strength": "strong" if len(evidence) >= 2 else ("medium" if len(evidence) == 1 else "weak"),
                "unsupported_claims": unsupported,
            }
        )
    return cards


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


def write_context_md(path: Path, task: dict, cards: list[dict], records: list[dict]) -> None:
    lines = []
    lines.append("# Evidence-Grounded Baseline Context\n")
    lines.append(f"Focus area: {task.get('focus_area', '')}\n")
    lines.append("## Baseline Evidence Cards\n")
    for card in cards:
        lines.append(f"### {card['baseline_name']} ({card['evidence_strength']})")
        lines.append(f"- Type: {card['baseline_type']}")
        lines.append(f"- Claimed task: {card['claimed_task']}")
        lines.append("- Evidence papers:")
        if card["evidence_papers"]:
            for paper in card["evidence_papers"]:
                lines.append(
                    f"  - `{paper['paper_id']}` {paper['title']} ({paper.get('year')}) {paper.get('url')}"
                )
        else:
            lines.append("  - No retrieved evidence.")
        lines.append("- Known limitations:")
        for lim in card["known_limitations"]:
            lines.append(f"  - {lim}")
        if card["unsupported_claims"]:
            lines.append("- Unsupported claims:")
            for claim in card["unsupported_claims"]:
                lines.append(f"  - {claim}")
        lines.append("")
    lines.append("## Top Retrieved Papers\n")
    for rec in records[:30]:
        lines.append(f"- `{rec['paper_id']}` {rec['title']} ({rec.get('year')}) score={rec['relevance_score']} url={rec.get('url')}")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_verification_report(path: Path, records: list[dict], cards: list[dict], no_network: bool) -> None:
    total = len(records)
    with_url = sum(1 for r in records if r.get("url"))
    with_abstract = sum(1 for r in records if r.get("abstract"))
    weak_cards = [c for c in cards if c["evidence_strength"] == "weak"]
    lines = [
        "# Paper Evidence Verification Report",
        "",
        f"- Generated at: {datetime.now().isoformat(timespec='seconds')}",
        f"- Network mode: {'disabled' if no_network else 'enabled'}",
        f"- Retrieved papers: {total}",
        f"- Papers with URL: {with_url}",
        f"- Papers with abstract: {with_abstract}",
        f"- Baseline cards: {len(cards)}",
        f"- Weak evidence cards: {len(weak_cards)}",
        "",
        "## Weak Evidence Baselines",
    ]
    for card in weak_cards:
        lines.append(f"- {card['baseline_name']}: {', '.join(card['unsupported_claims'])}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Retrieve papers and bind baseline cards to evidence for v0.5.")
    parser.add_argument("--task-spec", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--sources", default="openalex")
    parser.add_argument("--per-query", type=int, default=3)
    parser.add_argument("--max-baselines", type=int, default=12)
    parser.add_argument("--top-k-per-baseline", type=int, default=3)
    parser.add_argument("--include-recency-queries", action="store_true", help="Add recent/latest paper query variants.")
    parser.add_argument("--min-year", type=int, default=None, help="Filter supported sources to papers from this year onward.")
    parser.add_argument("--recency-weight", type=float, default=1.0, help="Weight of recency in retrieval ranking.")
    parser.add_argument("--recent-bonus-year", type=int, default=None, help="Add a ranking bonus to papers from this year onward.")
    parser.add_argument("--recent-bonus", type=float, default=0.0, help="Ranking bonus for papers at or after --recent-bonus-year.")
    parser.add_argument("--no-network", action="store_true", help="Generate queries and weak cards without API calls.")
    parser.add_argument("--sleep", type=float, default=0.4)
    parser.add_argument("--proxy", default=None, help="Optional HTTP/HTTPS proxy, e.g. http://127.0.0.1:7890")
    args = parser.parse_args()

    global PROXY_URL
    PROXY_URL = args.proxy

    task = load_yaml(args.task_spec)
    baselines = flatten_baselines(task.get("candidate_baselines", {}))
    queries = build_queries(task, baselines, args.max_baselines, args.include_recency_queries)
    sources = {s.strip().lower() for s in args.sources.split(",") if s.strip()}

    out = args.output_dir
    evidence_dir = out / "paper_evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    records = []
    errors = []
    if not args.no_network:
        for query in queries:
            for source in sources:
                try:
                    if source == "openalex":
                        records.extend(search_openalex(query, args.per_query, args.min_year))
                    elif source == "arxiv":
                        records.extend(search_arxiv(query, args.per_query))
                    elif source in {"semanticscholar", "semantic_scholar", "s2"}:
                        records.extend(search_semantic_scholar(query, args.per_query))
                    else:
                        errors.append({"query": query, "source": source, "error": "unknown source"})
                    time.sleep(args.sleep)
                except Exception as exc:
                    errors.append({"query": query, "source": source, "error": str(exc)})

    records = score_records(
        filter_records_by_min_year(dedupe(records), args.min_year),
        task,
        baselines,
        recency_weight=args.recency_weight,
        recent_bonus_year=args.recent_bonus_year,
        recent_bonus=args.recent_bonus,
    )
    cards = build_evidence_cards(records, baselines[: args.max_baselines], task, args.top_k_per_baseline)

    write_jsonl(evidence_dir / "papers.jsonl", records)
    write_jsonl(evidence_dir / "evidence_baseline_cards.jsonl", cards)
    write_jsonl(evidence_dir / "retrieval_queries.jsonl", queries)
    write_jsonl(evidence_dir / "retrieval_errors.jsonl", errors)
    write_context_md(evidence_dir / "evidence_context.md", task, cards, records)
    write_verification_report(evidence_dir / "reference_verification_report.md", records, cards, args.no_network)

    print("Paper evidence module complete")
    print("Task spec:", args.task_spec)
    print("Output dir:", evidence_dir)
    print("Queries:", len(queries))
    print("Papers:", len(records))
    print("Evidence baseline cards:", len(cards))
    print("Errors:", len(errors))
    if args.no_network:
        print("Network disabled: generated weak evidence cards and query plan only.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
