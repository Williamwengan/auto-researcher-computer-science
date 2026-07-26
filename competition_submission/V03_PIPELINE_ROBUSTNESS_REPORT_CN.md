# V0.3 Pipeline 鲁棒性验证报告（技术路线草案）

生成时间：2026-07-11

定位：这是面向挑战杯/AI4Sci 比赛的 **设计文档草案与技术路线验证报告**，不是最终版智能体详细设计文档。当前目标是验证 v0.3 idea pipeline 是否在多个 CV 方向上稳定生成更细、更可执行、更可评估的科研 idea。

## 1. 为什么现在不写最终版设计文档

- 最终提交需要智能体详细设计文档、Docker 镜像部署包或远程调用接口、三分钟演示视频。
- 目前 v0.3 已经把 idea 从结构化 proposal 推进到可实现雏形，但还没有完成最终 MVP baseline 实验。
- 因此现在应先证明 pipeline 改进有效，再选择最终 MVP 方向，最后写正式智能体设计文档。

## 2. V0.3 做了什么改进

- 在 idea 生成阶段强制要求 `minimal_new_module`：必须写清楚最小新增模块、输入、输出、算法步骤、训练/推理目标，以及为什么 baseline 做不到。
- 在 idea 生成阶段强制要求 `mvp_artifacts`：必须列出 1-2 周 MVP 所需脚本、数据文件、表格、图和成功阈值。
- 加入更严格的质量评估：baseline grounding、failure mode、mechanism、metric alignment、experiment executability、falsifiability、implementation readiness 等维度。
- 保留旧输出目录，所有 v0.3 结果均写入新的 timestamp 目录，没有覆盖旧 idea。

## 3. 三个方向 V0.2 vs V0.3 量化对比

| 方向 | v0.2 平均分 | v0.3 平均分 | 提升 | v0.2 最高分 | v0.3 最高分 | v0.2 新模块/产物覆盖 | v0.3 新模块/产物覆盖 | 粒度 penalty 变化 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 物理属性预测 | 84.7 | 87.0 | +2.3 | 87.5 | 89.0 | 0/3, 0/3 | 3/3, 3/3 | 11.3 -> 6.0 |
| Human Motion 生成 | 89.2 | 91.5 | +2.3 | 91.5 | 94.0 | 0/3, 0/3 | 3/3, 3/3 | 8.7 -> 2.7 |
| IAD + Agent 工作流 | 86.0 | 90.5 | +4.5 | 90.5 | 95.0 | 0/3, 0/3 | 3/3, 3/3 | 8.7 -> 2.7 |

结论：三个方向 v0.3 平均分都提升，新模块和 MVP 产物覆盖都从 0/3 提升到 3/3；粒度 penalty 全部下降。这说明 v0.3 不是单纯把文本写长，而是稳定提升了 implementation readiness。

## 4. 各方向结果解读

### 物理属性预测
- v0.2 top idea：Conformal Property Calibration from Synthetic-to-Real Material Evidence（87.5/100）
- v0.3 top idea：Evidence-Weighted Material Mixture Intervals for Object Physical Properties（89.0/100）
- v0.3 分数列表：[89.0, 87.0, 85.0]
- v0.3 粒度 penalty：[2.0, 8.0, 8.0]
- 判断：v0.3 从“材料/属性 proposal”推进到可执行模块，例如 mask_material_mixture_intervalizer、retrieval_consistency_gate、weak_label_conformal_property_calibrator；适合作为长期研究方向，但短期比赛风险是物理属性真值稀缺。
- v0.3 输出目录：`outputs/benchmark_cv_runs_20260711_150309/01_physical_property_prediction`

### Human Motion 生成
- v0.2 top idea：Uncertainty-Calibrated Keyframe Control for Text-to-Motion Diffusion（91.5/100）
- v0.3 top idea：Contact-Calibrated Diffusion Guidance for Text-to-Motion（94.0/100）
- v0.3 分数列表：[94.0, 87.0, 93.5]
- v0.3 粒度 penalty：[0.0, 8.0, 0.0]
- 判断：v0.3 的 Contact-Calibrated Diffusion Guidance 已经有脚本名、数据文件、图表和成功阈值，演示直观；主要风险是 MDM/HumanML3D 环境和指标复现实装成本。
- v0.3 输出目录：`outputs/benchmark_cv_runs_20260711_143630/02_human_motion_generation`

### IAD + Agent 工作流
- v0.2 top idea：Reference-Consistency Inspection Agent for Shifted and Contaminated Normal Banks（90.5/100）
- v0.3 top idea：Reference-Consistency Agent for Shift-Resistant PatchCore Inspection（95.0/100）
- v0.3 分数列表：[95.0, 87.5, 89.0]
- v0.3 粒度 penalty：[0.0, 4.0, 4.0]
- 判断：v0.3 从“检测+报告”升级为具备 reference consistency、disagreement escalation、claim grounding 的 agent 工作流；MVTec AD/PatchCore 路线短期最容易跑通，也最容易做三分钟演示。
- v0.3 输出目录：`outputs/benchmark_cv_runs_20260711_150957/05_iad_agent_workflow`

## 5. 是否已经足够鲁棒

当前可以说：v0.3 pipeline 已经从“结构化 idea 生成”提升到“可实现 idea 生成雏形”。证据是三个不同 CV 方向都稳定输出了最小新增模块、MVP 脚本、数据文件、表格/图和成功阈值。
但还不能说最终足够鲁棒，因为还缺两件事：
- 生成后 critic/repair 闭环：目前评估器能打分，但还没有自动要求低分 idea 重写。
- MVP 实验验证：还没有选定一个方向，把 baseline 跑通并生成真实可展示结果。

## 6. 比赛 MVP 方向建议

| 候选方向 | 推荐度 | 原因 | 主要风险 |
|---|---|---|---|
| IAD + Agent Idea 1：Reference-Consistency Agent | 最高 | PatchCore + MVTec AD 容易跑通；有异常图、正常参考、证据链、人工升级，三分钟视频很好展示；agent 感最强 | 需要实现 reference consistency 与报告证据链接，但工程量可控 |
| Human Motion Idea 1：Contact-Calibrated Diffusion Guidance | 高 | 视觉演示直观，指标明确，如 foot sliding、FID、R-precision | MDM/HumanML3D 环境可能耗时；不一定体现完整 agent 闭环 |
| Physical Property Idea 1：Material Mixture Intervals | 中 | 贴合研究兴趣，科研问题有价值 | 真实物理属性标签难，短期容易停在 proxy label 和不确定性方案 |

当前建议：**优先把 IAD + Agent Idea 1 作为比赛 MVP 候选路线**，Human Motion Idea 1 作为备选。物理属性预测更适合作为长期科研方向，不建议作为短期比赛主线。

## 7. 与比赛提交物的关系

### 7.1 智能体详细设计文档
现在先写技术路线草案，不写最终版。等 IAD MVP 跑通后，正式文档可以围绕“Reference-Consistency Inspection Agent”展开，包含：工具列表、状态机、检索记忆、验证循环、置信度校准、人工升级策略、结构化报告 schema。

### 7.2 Docker 镜像部署包或远程调用接口
IAD 路线最容易封装：输入一张工业检测图 + 产品类别；输出 anomaly_score、anomaly_mask、normal_reference_used、evidence、confidence、recommended_action、failure_warning。Docker 内可预置 PatchCore/特征缓存/轻量 agent API。

### 7.3 三分钟演示视频
IAD 路线视频结构最清楚：上传产品图 -> PatchCore 生成异常热力图 -> agent 检索正常参考 -> consistency auditor 判断是否误报/异常 -> 输出结构化报告和人工升级理由 -> 展示量化表格。

## 8. 下一步路线

1. 人工审查 v0.3 的 IAD 三个 idea，重点看 Idea 1 是否能 1-2 周实现。
2. 选择 IAD Idea 1 后，先做最小 MVP：PatchCore baseline + reference consistency auditor + structured report。
3. 跑 MVTec AD 3-5 个类别，先产出 image/pixel AUROC、false alarm reduction、evidence grounding 的小表。
4. 做 critic/repair 闭环：如果 idea 缺少脚本、指标、负对照或成功阈值，自动要求生成器重写。
5. MVP 跑通后，再写最终版智能体详细设计文档、Docker/接口说明和三分钟视频脚本。

## 9. 附：关键输出文件

- 物理属性 v0.3 中文审查：`outputs/benchmark_cv_runs_20260711_150309/01_physical_property_prediction/review_ready_ideas/IDEAS_MANUAL_REVIEW_CN.md`
- Human Motion v0.3 中文审查：`outputs/benchmark_cv_runs_20260711_143630/02_human_motion_generation/review_ready_ideas/IDEAS_MANUAL_REVIEW_CN.md`
- IAD v0.3 中文审查：`outputs/benchmark_cv_runs_20260711_150957/05_iad_agent_workflow/review_ready_ideas/IDEAS_MANUAL_REVIEW_CN.md`
- IAD v0.3 自动评分：`outputs/benchmark_cv_runs_20260711_150957/05_iad_agent_workflow/idea_quality_report_CN.md`
- Human Motion v0.2/v0.3 对比：`outputs/benchmark_cv_runs_20260711_143630/02_human_motion_generation/HUMAN_MOTION_V02_V03_QUALITY_COMPARISON_CN.md`