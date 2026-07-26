# V1.2 IAD MVP Script Scaffold

生成时间：2026-07-14 11:21:45

生成脚本：`focused_workflow/scripts/build_v12_iad_mvp_scaffold.py`

## 为什么做 V1.2

V1.1 已经把 final research plans 拆成 experiment execution plans。V1.2 开始进入工程，但只做最小脚本骨架，不跑真实 benchmark，不声明实验结果。

本阶段选择 IAD execution plan 作为第一个工程脚手架，原因是它已有 `iad_mvp/` 目录，数据结构和指标最标准，后续最容易用 MVTec AD / VisA 小子集跑通。

注意：这只是执行优先级，不代表项目变成只做 IAD。项目主线仍然是跨任务科研 idea generation workflow。

## 本阶段生成脚本

| 文件 | 作用 |
| --- | --- |
| `iad_mvp/scripts/common_iad.py` | v1.2 scaffold |
| `iad_mvp/scripts/prepare_iad_reference_manifest.py` | v1.2 scaffold |
| `iad_mvp/scripts/build_reference_bank.py` | v1.2 scaffold |
| `iad_mvp/scripts/run_iad_baselines.py` | v1.2 scaffold |
| `iad_mvp/scripts/score_reference_consistency.py` | v1.2 scaffold |
| `iad_mvp/scripts/run_iad_negative_controls.py` | v1.2 scaffold |
| `iad_mvp/scripts/evaluate_iad_agent.py` | v1.2 scaffold |

## 推荐运行顺序

如果你已经有 MVTec AD 数据集：

```bash
python iad_mvp/scripts/check_env.py --mvtec_root /path/to/mvtec_anomaly_detection
python iad_mvp/scripts/prepare_mvtec_subset.py --mvtec_root /path/to/mvtec_anomaly_detection --categories bottle --output iad_mvp/data/mvtec_split.json
python iad_mvp/scripts/prepare_iad_reference_manifest.py --split iad_mvp/data/mvtec_split.json --output iad_mvp/data/iad_reference_manifest.jsonl
python iad_mvp/scripts/build_reference_bank.py --manifest iad_mvp/data/iad_reference_manifest.jsonl --output_dir iad_mvp/data
python iad_mvp/scripts/run_iad_baselines.py --manifest iad_mvp/data/iad_reference_manifest.jsonl --reference_bank iad_mvp/data/iad_reference_bank.npz --output_dir iad_mvp/outputs/patchcore_baseline
python iad_mvp/scripts/score_reference_consistency.py --manifest iad_mvp/data/iad_reference_manifest.jsonl --baseline iad_mvp/outputs/patchcore_baseline/iad_baseline_scores.csv --reference_bank iad_mvp/data/iad_reference_bank.npz --reference_index iad_mvp/data/iad_reference_index.jsonl --output iad_mvp/outputs/reference_consistency/iad_reference_consistency_scores.csv
python iad_mvp/scripts/run_iad_negative_controls.py --scores iad_mvp/outputs/reference_consistency/iad_reference_consistency_scores.csv --output iad_mvp/outputs/tables/iad_negative_control_report.csv
python iad_mvp/scripts/evaluate_iad_agent.py --baseline iad_mvp/outputs/patchcore_baseline/iad_baseline_scores.csv --scores iad_mvp/outputs/reference_consistency/iad_reference_consistency_scores.csv --output_dir iad_mvp/outputs/tables
```

## 当前边界

- `run_iad_baselines.py` 是 lightweight nearest-reference baseline，不是完整 PatchCore 复现。
- 负控制是轻量 proxy，不是完整 contaminated normal bank 实验。
- 如果没有 MVTec AD / VisA 数据，本阶段只能检查 `--help` 和脚本结构。
- 真实 benchmark 结果属于 v1.3 或后续阶段。
