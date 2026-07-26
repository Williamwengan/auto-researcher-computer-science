# Release Manifest

生成日期：2026-07-24

## Included

- `researcharena/`
- `focused_workflow/`
- `iad_mvp/scripts/`
- `iad_mvp/data/*.json`
- `iad_mvp/data/*.jsonl`
- `iad_mvp/outputs/tables/` lightweight CSV/Markdown summaries
- `iad_mvp/outputs/tables_3cat/` lightweight CSV/Markdown summaries
- `competition_submission/`
- `sample_outputs/`
- `configs/`
- root files: `README.md`, `LICENSE`, `pyproject.toml`, `Dockerfile`, `Dockerfile.cpu`

## Excluded

- raw datasets
- virtual environments
- full `outputs/` directory
- unreleased experiment caches and private review packs
- API request/response caches
- large feature caches such as `.npz`
- git metadata

## Core Entry Points

- focused workflow:

```bash
python focused_workflow/scripts/retrieve_paper_evidence.py --help
python focused_workflow/scripts/verify_reference_claims.py --help
python focused_workflow/scripts/run_blind_ab_llm_reviewer.py --help
```

- IAD MVP:

```bash
python iad_mvp/scripts/prepare_mvtec_subset.py --help
python iad_mvp/scripts/run_iad_baselines.py --help
python iad_mvp/scripts/evaluate_iad_agent.py --help
```
