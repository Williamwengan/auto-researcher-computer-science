# IAD + Agent MVP 选择与最小实现计划（草案）

生成时间：2026-07-11

定位：本文件是比赛 MVP 方向选择与最小实现计划，不是最终版智能体详细设计文档。最终设计文档应在 MVP baseline 跑通后再写。

## 1. 审查对象

- 输入目录：`outputs/benchmark_cv_runs_20260711_150957/05_iad_agent_workflow`
- 中文 idea 汇总：`outputs/benchmark_cv_runs_20260711_150957/05_iad_agent_workflow/review_ready_ideas/IDEAS_MANUAL_REVIEW_CN.md`
- 自动质量评分：`outputs/benchmark_cv_runs_20260711_150957/05_iad_agent_workflow/idea_quality_report_CN.md`
- 人工 reviewer 评分：`outputs/benchmark_cv_runs_20260711_150957/05_iad_agent_workflow/si2025_review_reviewer01.json`

## 2. 人工 Reviewer 评分结论

| 排名 | Idea | Novelty | Feasibility | Expected Effectiveness | Excitement | Overall | 判断 |
|---:|---|---:|---:|---:|---:|---:|---|
| 1 | Reference-Consistency Agent for Shift-Resistant PatchCore Inspection | 8 | 9 | 9 | 9 | 9 | 推荐作为第一阶段 MVP 主线 |
| 2 | Claim-Grounded Defect Report Agent with Region-Reference Evidence Checking | 8 | 8 | 8 | 9 | 8 | 适合作为展示增强模块 |
| 3 | Disagreement-Calibrated Inspection Agent for Selective Human Escalation | 8 | 7 | 8 | 8 | 8 | 适合作为第二阶段增强 |

## 3. 最终 MVP 选择

建议选择：**Idea 1：Reference-Consistency Agent for Shift-Resistant PatchCore Inspection**。

选择理由：
- 最容易跑通：PatchCore + MVTec AD 是成熟 IAD baseline，数据、指标和可视化都比较完整。
- 最像智能体：它包含检索正常参考、审计参考库、验证异常区域、置信度校准、接受/抑制/升级决策和结构化报告。
- 最适合视频：可以展示异常热力图、top-k 正常参考 patch、一致性分数、失败警告和人工升级理由。
- 最容易封装接口：输入工业图像和产品类别，输出 anomaly score、mask、evidence、normal reference、confidence、recommended action。

不建议第一阶段直接选择 Idea 2，因为它需要多模型统一运行，工程链条更长；不建议单独选择 Idea 3，因为它更偏报告可信度，检测 baseline 仍需要 Idea 1 支撑。

## 4. 第一阶段最小 MVP 范围

第一阶段只做一个能跑、能评估、能展示的最小闭环：

```text
输入：测试图像 + 产品类别 + 正常参考库
工具 1：PatchCore baseline，输出 anomaly score 与 anomaly heatmap
工具 2：region_reference_consistency_auditor，检索正常参考 patch 并计算一致性
工具 3：structured_report_writer，输出结构化 inspection report
输出：anomaly_mask_or_region + normal_reference_used + confidence + recommended_action + failure_warning
```

第一阶段暂时不强制做：
- 多模型 disagreement controller。
- 完整 VLM claim checker。
- 大规模多数据集泛化。
- 复杂 Docker UI。

## 5. 最小实现模块拆分

| 模块 | 作用 | 第一阶段要求 |
|---|---|---|
| PatchCore baseline | 生成 image-level score 和 pixel-level heatmap | 跑通 MVTec AD 3-5 个类别 |
| normal reference memory | 保存正常 patch 特征和索引 | 支持 top-k normal patch retrieval |
| region_reference_consistency_auditor | 新增核心模块 | 输出 consistency_score、reference_purity、shift_warning、decision |
| structured report writer | 结构化报告 | 输出 JSON，不追求复杂自然语言 |
| evaluator | 量化评估 | 输出 AUROC、PRO、false_alarm_reduction、evidence_grounding_score |

## 6. 推荐脚本结构

```text
iad_mvp/
  data/
    mvtec_split.json
  scripts/
    build_patchcore_memory.py
    run_patchcore_baseline.py
    score_reference_consistency.py
    run_reference_consistency_agent.py
    evaluate_iad_agent.py
  outputs/
    patchcore_baseline/
    reference_consistency/
    reports/
    tables/
    figures/
```

## 7. 第一阶段评价指标

| 指标 | 用途 | 成功阈值 |
|---|---|---|
| image_level_auroc | 判断图像级异常检测是否没有崩 | 不明显低于 PatchCore baseline |
| pixel_level_auroc / pro_score | 判断定位是否保持 | 相比 PatchCore 下降不超过 1.5-2 点 |
| defect_region_recall | 保证不要漏检 | 与 PatchCore matched recall 对齐 |
| false_alarm_reduction | 证明 agent 有用 | 在 matched recall 下减少至少 10% false alarm |
| evidence_grounding_score | 证明报告证据可靠 | 50 个样本人工/规则审查达到 0.8 左右 |
| tool_success_rate | 证明工作流稳定 | 大于 95% |

## 8. 1-2 周实施节奏

| 阶段 | 时间 | 目标 | 产物 |
|---|---|---|---|
| Day 1-2 | baseline | 跑通 PatchCore/MVTec AD，保存 heatmap 和 score | baseline 表格、可视化图 |
| Day 3-4 | reference consistency | 实现 normal patch retrieval 和 consistency score | `reference_consistency/*.jsonl` |
| Day 5 | agent report | 实现 accept/suppress/escalate 决策与结构化报告 | `reports/*_agent_reports.jsonl` |
| Day 6-7 | evaluation | 比较 PatchCore vs agent，做消融 | 指标表、案例图 |
| Week 2 | packaging | 轻量 API/Docker/演示视频材料 | 接口说明、视频脚本、设计文档草案 |

## 9. 与比赛三项提交物的对应关系

### 9.1 智能体详细设计文档
MVP 跑通后，正式文档围绕以下结构写：工具列表、状态机、normal reference memory、reference consistency auditor、决策策略、失败处理、评估指标、实验结果。

### 9.2 Docker 镜像部署包或远程调用接口
建议先做远程调用接口或 FastAPI 本地服务，接口最小形式：
```text
POST /inspect
input: image, product_category
output: anomaly_score, anomaly_region, normal_reference_used, confidence, recommended_action, failure_warning
```

### 9.3 三分钟演示视频
推荐视频脚本：
1. 展示输入工业图像和产品类别。
2. 展示 PatchCore heatmap。
3. 展示 agent 检索到的正常参考 patch。
4. 展示 consistency score 和是否抑制误报/确认异常/升级人工。
5. 展示结构化报告和量化指标表。

## 10. Go / No-Go 判断

如果第一阶段满足以下条件，就进入最终智能体设计文档和 Docker/API 包装：
- PatchCore baseline 能稳定跑通至少 3 个 MVTec AD 类别。
- agent 输出的结构化报告字段完整。
- matched recall 下 false_alarm_reduction 有提升趋势。
- 可视化案例能清楚展示正常参考证据链。

如果不满足，则降级方案：保留 PatchCore baseline + Idea 3 的 claim-grounded report checker，主打“证据约束报告智能体”，减少对 false alarm reduction 的硬性要求。
