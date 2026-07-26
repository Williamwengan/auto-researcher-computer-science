# AI4Sci ResearchArena Workflow Competition Release

本目录是从主工程中整理出的比赛 GitHub 上传包。它保留比赛展示所需的核心代码、任务配置、prompt/schema、轻量结果表和中文报告；不包含原始数据集、虚拟环境、API key、额外实验缓存和大体积中间输出。

## 项目定位

本项目不是单独提出一个 CV 算法，而是在 ResearchArena baseline 上构建一个跨任务 AI 科研自动化 workflow：

```text
输入科研任务
-> 检索和整理论文
-> 分析 baseline 缺陷
-> 生成细粒度 idea
-> 生成实验计划
-> 多模型匿名评审
-> 根据意见修复 idea
-> 再次盲评
-> 核查论文证据
-> 输出最终研究方案
-> 接入真实数据执行反馈
```

## 目录说明

| path | content |
| --- | --- |
| `researcharena/` | ResearchArena baseline 代码。 |
| `focused_workflow/` | 本项目主要 workflow：任务规格、prompt、schema、idea generation、repair、judge、claim verification、报告生成脚本。 |
| `iad_mvp/` | IAD + Agent 真实数据 smoke-test scaffold，仅包含脚本、小型 manifest 和轻量结果表。MVTec AD 数据集需自行下载。 |
| `competition_submission/` | 比赛中文报告、阶段总结、最终收束报告和 deliverables index。 |
| `sample_outputs/` | 轻量样例输出，包括 evidence bank、Si-style benchmark 摘要、多模型盲评摘要。 |
| `configs/` | ResearchArena / workflow 运行配置。 |

## 重要边界

- 不声称 idea generation 达到全球意义上的 SOTA。
- 不声称 IAD scaffold 是完整 PatchCore/anomalib benchmark 或 IAD SOTA。
- `02 Human Motion` 和 `04 3D Reconstruction` 在当前比赛材料中是 held-out samples。
- Indoor3D 使用 seeded evidence bank，最终文档和答辩中必须透明披露。
- `sample_outputs/` 只保留轻量证据和摘要，不包含完整 API request/response。

## 快速检查

```bash
python -m py_compile focused_workflow/scripts/*.py iad_mvp/scripts/*.py
```

查看最终主线报告：

```text
competition_submission/FINAL_WORKFLOW_END_TO_END_CLOSING_REPORT_CN.md
```

查看材料索引：

```text
competition_submission/COMPETITION_DELIVERABLES_INDEX_CN.md
```

## IAD 数据说明

如果要复现 IAD smoke test，需要自行下载 MVTec AD，并按主工程中的约定放置。例如：

```text
Datasets/01_IAD/mvtec_anomaly_detection/mvtec_anomaly_detection
```

本 release 不包含 MVTec AD 原始数据，也不包含由图像特征构建出的 `.npz` reference bank。
