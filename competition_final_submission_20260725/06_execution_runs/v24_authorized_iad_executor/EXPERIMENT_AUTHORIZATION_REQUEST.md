# V24 授权实验执行请求

生成时间：2026-07-25T11:27:44

## 目的

把当前 ResearchArena workflow 生成的 IAD 研究方案，接入 Auto-claude-style 的实验执行层：先复现 lightweight baseline，再运行 reference-consistency agent，再汇总实验指标。

## 为什么需要人工授权

实验执行会读取数据集、生成中间文件并覆盖同名 scaffold 输出。为了避免自动系统在未经确认时消耗资源或改写结果，V24 默认只生成预览；只有显式 `--approve` 才会真正运行。

## 将要执行的命令

| step | phase | artifact |
| ---: | --- | --- |
| 1 | `prepare_reference_manifest` | `iad_mvp/data/iad_reference_manifest.jsonl` |
| 2 | `build_reference_bank` | `iad_mvp/data/iad_reference_bank.npz` |
| 3 | `reproduce_lightweight_baseline` | `iad_mvp/outputs/patchcore_baseline/iad_baseline_scores.csv` |
| 4 | `run_reference_consistency_agent` | `iad_mvp/outputs/reference_consistency/iad_reference_consistency_scores.csv` |
| 5 | `evaluate_execution_metrics` | `iad_mvp/outputs/tables/iad_agent_execution_metrics.csv` |

详细命令见：`commands_preview.sh`

## 授权执行命令

```bash
python focused_workflow/scripts/run_v24_authorized_experiment_executor.py \
  --approve \
  --approval-note "I approve running the local IAD scaffold execution chain."
```

如果要指定 MVTec 数据和类别：

```bash
python focused_workflow/scripts/run_v24_authorized_experiment_executor.py \
  --mvtec-root Datasets/01_IAD/mvtec_anomaly_detection/mvtec_anomaly_detection \
  --categories bottle cable capsule \
  --approve \
  --approval-note "I approve running the local IAD scaffold execution chain on bottle/cable/capsule."
```

## 边界

- 当前执行器只接 IAD scaffold，不声称完整 PatchCore/anomalib benchmark。
- 当前执行器不做远程 GPU 调度，不自动下载数据，不删除文件。
- 后续可把 Auto-claude 的 experiment queue / watchdog / paper writing loop 继续接入。
