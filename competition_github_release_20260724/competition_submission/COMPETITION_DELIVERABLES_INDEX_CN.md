# 比赛交付物目录（按 Workflow 环节整理）

生成时间：2026-07-14 21:21:57

生成脚本：`focused_workflow/scripts/build_competition_deliverables_index.py`

## 使用说明

这份目录不是新的实验报告，而是给比赛提交/答辩使用的索引。它把报告、脚本、输出表和中间产物按 workflow 环节整理，避免材料多而散。

优先阅读顺序：

1. `FINAL_WORKFLOW_END_TO_END_CLOSING_REPORT_CN.md`
2. `V09_IDEA_GENERATION_CORE_BENCHMARK_REPORT_CN.md`
3. `V10_FINAL_RESEARCH_PLAN_PACKAGE_CN.md`
4. `V18_IAD_EXECUTION_FEEDBACK_REPAIR_CASE_CN.md`
5. `SI2024_BENCHMARK_EVALUATION_REPORT_CN.md` 和 `V07_REFERENCE_CLAIM_VERIFICATION_FINAL_SUMMARY_CN.md`

## 总览统计

| metric | value |
| --- | --- |
| indexed_items | 103 |
| core_items | 83 |
| support_items | 20 |
| missing_items | 0 |
| docx_available | yes |

## 分环节交付物目录

### 00 最终入口与总收束

| kind | priority | status | path | role |
| --- | --- | --- | --- | --- |
| report | core | exists | competition_submission/FINAL_WORKFLOW_END_TO_END_CLOSING_REPORT_CN.md | 最终主线报告：说明 workflow 已经从 idea generation 走到真实执行反馈。 |
| json | core | exists | competition_submission/FINAL_WORKFLOW_END_TO_END_CLOSING_REPORT.json | 最终主线报告结构化摘要。 |
| script | core | exists | focused_workflow/scripts/build_final_workflow_closing_report.py | 生成最终端到端收束报告。 |
| report | support | exists | competition_submission/FINAL_STORYLINE_FOR_COMPETITION_CN.md | 比赛叙事主线材料。 |
| report | support | exists | competition_submission/AI_RESEARCH_WORKFLOW_FULL_PROGRESS_REPORT_CN.md | 完整阶段性进展报告。 |
| docx | support | exists | competition_submission/AI_RESEARCH_WORKFLOW_FULL_PROGRESS_REPORT_CN.docx | 完整进展报告 DOCX 版本。 |

### 01 任务输入与结构化 idea generation

| kind | priority | status | path | role |
| --- | --- | --- | --- | --- |
| script | support | exists | focused_workflow/scripts/run_focused_workflow_v0_2.sh | 运行 v0.2 focused workflow。 |
| script | support | exists | focused_workflow/scripts/render_prompt.py | 根据 task_spec 渲染 prompt。 |
| script | support | exists | focused_workflow/scripts/validate_outputs.py | 检查 baseline_cards/focused_ideas/experiment_plan 输出结构。 |
| report | support | exists | competition_submission/V03_PIPELINE_ROBUSTNESS_REPORT_CN.md | v0.3 pipeline 鲁棒性阶段报告。 |
| report | support | exists | competition_submission/V04_IDEA_WORKFLOW_FINAL_EVALUATION_REPORT_CN.md | v0.4 idea workflow 评价报告。 |
| report | core | exists | competition_submission/IDEA_GENERATION_MODULE_CARD_CN.md | idea generation 模块卡片，可作为答辩简介。 |

### 02 论文证据检索与 evidence-grounded ideation

| kind | priority | status | path | role |
| --- | --- | --- | --- | --- |
| script | core | exists | focused_workflow/scripts/retrieve_paper_evidence.py | 检索/整理 paper evidence。 |
| script | support | exists | focused_workflow/scripts/validate_paper_evidence.py | 检查 paper evidence 文件。 |
| script | support | exists | focused_workflow/scripts/validate_evidence_grounding.py | 检查 idea 是否绑定 evidence。 |
| script | core | exists | focused_workflow/scripts/repair_v05_evidence_grounded_ideas.py | v0.5 evidence-grounded idea 修复。 |
| script | core | exists | focused_workflow/scripts/seed_indoor_scene_evidence.py | 为 Indoor3D 构造 seeded evidence bank；最终必须透明披露。 |
| report | core | exists | competition_submission/V05_PAPER_RETRIEVAL_EVIDENCE_BINDING_REPORT_CN.md | paper retrieval 与 evidence binding 报告。 |
| report | core | exists | competition_submission/V05_EVIDENCE_GROUNDED_IDEA_RESULT_ANALYSIS_CN.md | evidence-grounded idea 结果分析。 |
| report | core | exists | competition_submission/V05_TARGETED_REPAIR_BEFORE_AFTER_REPORT_CN.md | targeted repair 前后对比报告。 |

### 03 idea repair、质量评分与机制一致性修复

| kind | priority | status | path | role |
| --- | --- | --- | --- | --- |
| script | core | exists | focused_workflow/scripts/evaluate_idea_quality.py | 自动 idea quality scoring。 |
| script | support | exists | focused_workflow/scripts/repair_low_quality_ideas.py | 低质量 idea 修复。 |
| script | core | exists | focused_workflow/scripts/apply_physical_property_v2_repair.py | 物理属性 v2 二次修复核心脚本。 |
| script | core | exists | focused_workflow/scripts/repair_physical_v2_evidence_cards.py | 物理属性 v2 evidence cards 修复。 |
| script | core | exists | focused_workflow/scripts/repair_indoor3d_evidence_cards.py | Indoor3D evidence cards 修复。 |
| report | core | exists | competition_submission/V07_PHYSICAL_V2_CLAIM_REPAIR_SUMMARY_CN.md | 物理属性 claim repair 总结。 |
| report | core | exists | competition_submission/V07_PHYSICAL_V2_EVIDENCE_CARD_REPAIR_SUMMARY_CN.md | 物理属性 evidence-card repair 总结。 |
| report | core | exists | competition_submission/V07_INDOOR3D_CLAIM_FORMAT_REPAIR_SUMMARY_CN.md | Indoor3D claim format repair 总结。 |
| report | core | exists | competition_submission/V07_INDOOR3D_EVIDENCE_CARD_REPAIR_SUMMARY_CN.md | Indoor3D evidence-card repair 总结。 |

### 04 多模型匿名盲评与 Si et al.-style benchmark

| kind | priority | status | path | role |
| --- | --- | --- | --- | --- |
| script | core | exists | focused_workflow/scripts/create_blind_ab_review_pack.py | 生成 blind A/B review pack。 |
| script | core | exists | focused_workflow/scripts/run_blind_ab_llm_reviewer.py | 运行 multi-LLM blind reviewer。 |
| script | core | exists | focused_workflow/scripts/summarize_blind_ab_reviews.py | 汇总 blind A/B 评审结果。 |
| script | core | exists | focused_workflow/scripts/run_si2024_blind_ab_reviewer.py | 运行 Si et al.-style blind reviewer。 |
| script | support | exists | focused_workflow/scripts/multi_llm_judge.py | multi-LLM judge 通用脚本。 |
| report | core | exists | competition_submission/V06_MULTI_LLM_BLIND_AB_EVALUATION_REPORT_V2_CN.md | v0.6 multi-LLM blind A/B 评价报告。 |
| report | core | exists | competition_submission/SI2024_BENCHMARK_EVALUATION_REPORT_CN.md | 正式 Si et al.-style benchmark 报告。 |
| report | core | exists | outputs/si2024_three_task_benchmark_summary/SI2024_THREE_TASK_BENCHMARK_SUMMARY_CN.md | 三任务 Si-style benchmark 总表。 |

### 05 Reference claim verification

| kind | priority | status | path | role |
| --- | --- | --- | --- | --- |
| script | core | exists | focused_workflow/scripts/verify_reference_claims.py | 检查 claim 是否绑定真实 paper id 且被 title/abstract/card 支撑。 |
| report | core | exists | competition_submission/V07_REFERENCE_CLAIM_VERIFICATION_FINAL_SUMMARY_CN.md | v0.7 reference claim verification 最终汇总。 |
| report | support | exists | competition_submission/V07_REFERENCE_CLAIM_VERIFICATION_SUMMARY_V2_CN.md | v0.7 reference claim verification 中间汇总。 |

### 06 核心 benchmark 收束与最终研究方案

| kind | priority | status | path | role |
| --- | --- | --- | --- | --- |
| script | support | exists | focused_workflow/scripts/select_final_candidates_v0_8.py | v0.8 benchmark robustness / candidate selector 历史脚本。 |
| script | core | exists | focused_workflow/scripts/build_v09_idea_generation_core_benchmark_report.py | 生成 V09 idea generation core benchmark 报告。 |
| script | core | exists | focused_workflow/scripts/build_v10_final_research_plan_package.py | 生成 V10 final research plan package。 |
| report | core | exists | competition_submission/V09_IDEA_GENERATION_CORE_BENCHMARK_REPORT_CN.md | 核心 idea generation benchmark 报告。 |
| json | core | exists | competition_submission/V09_IDEA_GENERATION_CORE_BENCHMARK_SUMMARY.json | V09 结构化摘要。 |
| report | core | exists | competition_submission/V10_FINAL_RESEARCH_PLAN_PACKAGE_CN.md | 最终研究方案包。 |
| json | core | exists | competition_submission/V10_FINAL_RESEARCH_PLAN_PACKAGE.json | 最终研究方案包结构化数据。 |
| schema | core | exists | competition_submission/FINAL_RESEARCH_PLAN_SCHEMA.json | 最终研究方案 schema。 |

### 07 实验执行规划与 IAD scaffold

| kind | priority | status | path | role |
| --- | --- | --- | --- | --- |
| script | core | exists | focused_workflow/scripts/build_v11_experiment_execution_plan.py | 生成 V11 experiment execution plan。 |
| script | core | exists | focused_workflow/scripts/build_v12_iad_mvp_scaffold.py | 生成 V12 IAD MVP 脚本骨架。 |
| report | core | exists | competition_submission/V11_EXPERIMENT_EXECUTION_PLAN_CN.md | 实验执行规划报告。 |
| json | core | exists | competition_submission/V11_EXPERIMENT_EXECUTION_PLAN.json | 实验执行规划结构化数据。 |
| schema | core | exists | competition_submission/EXPERIMENT_EXECUTION_PLAN_SCHEMA.json | 实验执行计划 schema。 |
| report | core | exists | competition_submission/V12_IAD_MVP_SCRIPT_SCAFFOLD_CN.md | IAD MVP scaffold 说明。 |
| json | core | exists | competition_submission/V12_IAD_MVP_SCRIPT_SCAFFOLD.json | IAD MVP scaffold 文件清单。 |
| script | core | exists | iad_mvp/scripts/check_env.py | 检查 IAD 环境和 MVTec 数据结构。 |
| script | core | exists | iad_mvp/scripts/prepare_mvtec_subset.py | 准备 MVTec split。 |
| script | core | exists | iad_mvp/scripts/prepare_iad_reference_manifest.py | 生成 IAD manifest。 |
| script | core | exists | iad_mvp/scripts/build_reference_bank.py | 构建 normal reference bank。 |
| script | core | exists | iad_mvp/scripts/run_iad_baselines.py | 运行 lightweight nearest-reference baseline。 |
| script | core | exists | iad_mvp/scripts/score_reference_consistency.py | 生成 reference consistency 决策。 |
| script | core | exists | iad_mvp/scripts/run_iad_negative_controls.py | 运行轻量负控制。 |
| script | core | exists | iad_mvp/scripts/evaluate_iad_agent.py | 生成 IAD execution metrics。 |

### 08 IAD 真实数据执行反馈与自动修复案例

| kind | priority | status | path | role |
| --- | --- | --- | --- | --- |
| script | core | exists | focused_workflow/scripts/build_v13_iad_smoke_test_report.py | 生成 V13 IAD data readiness + smoke test 报告。 |
| script | core | exists | focused_workflow/scripts/build_v14_iad_threshold_calibration.py | 生成 V14 阈值校准报告。 |
| script | core | exists | focused_workflow/scripts/build_v15_iad_multicategory_smoke_test_report.py | 生成 V15 三类别迁移 smoke test 报告。 |
| script | core | exists | focused_workflow/scripts/build_v16_iad_per_category_threshold_calibration.py | 生成 V16 类别感知阈值校准报告。 |
| script | core | exists | focused_workflow/scripts/build_v17_iad_category_constrained_retrieval_report.py | 生成 V17 类别约束检索/归一化报告。 |
| script | core | exists | focused_workflow/scripts/build_v18_iad_execution_feedback_repair_case.py | 生成 V18 execution-feedback repair case 总结。 |
| report | core | exists | competition_submission/V13_IAD_DATA_READINESS_AND_SMOKE_TEST_CN.md | MVTec bottle 单类别 smoke test。 |
| report | core | exists | competition_submission/V14_IAD_THRESHOLD_CALIBRATION_CN.md | bottle 阈值校准：accepted anomaly 0→51。 |
| report | core | exists | competition_submission/V15_IAD_MULTICATEGORY_SMOKE_TEST_CN.md | 三类别迁移发现全局阈值不鲁棒。 |
| report | core | exists | competition_submission/V16_IAD_PER_CATEGORY_THRESHOLD_CALIBRATION_CN.md | 类别感知阈值将 FPR 0.574257→0.009901。 |
| report | core | exists | competition_submission/V17_IAD_CATEGORY_CONSTRAINED_RETRIEVAL_CN.md | 类别约束检索与类别内归一化，小幅提升并暴露 feature 瓶颈。 |
| report | core | exists | competition_submission/V18_IAD_EXECUTION_FEEDBACK_REPAIR_CASE_CN.md | IAD execution-feedback repair case 总结。 |
| json | core | exists | competition_submission/V18_IAD_EXECUTION_FEEDBACK_REPAIR_CASE.json | V18 结构化摘要。 |

### 09 IAD 输出表与中间产物

| kind | priority | status | path | role |
| --- | --- | --- | --- | --- |
| data | core | exists | iad_mvp/data/mvtec_split.json | bottle split。 |
| data | core | exists | iad_mvp/data/mvtec_split_3cat.json | bottle/cable/capsule 三类别 split。 |
| data | core | exists | iad_mvp/data/iad_reference_manifest.jsonl | bottle IAD manifest。 |
| data | core | exists | iad_mvp/data/iad_reference_manifest_3cat.jsonl | 三类别 IAD manifest。 |
| output | core | exists | iad_mvp/outputs/patchcore_baseline/iad_baseline_scores.csv | bottle lightweight baseline scores。 |
| output | core | exists | iad_mvp/outputs/reference_consistency/iad_reference_consistency_scores.csv | bottle reference consistency scores。 |
| table | core | exists | iad_mvp/outputs/tables/iad_agent_execution_metrics.csv | bottle execution metrics。 |
| table | core | exists | iad_mvp/outputs/tables/iad_negative_control_report.csv | bottle negative control report。 |
| table | core | exists | iad_mvp/outputs/tables/iad_threshold_sweep.csv | V14 threshold sweep。 |
| table | core | exists | iad_mvp/outputs/tables/iad_threshold_recommended_decisions.csv | V14 recommended decisions。 |
| output | core | exists | iad_mvp/outputs/patchcore_baseline_3cat/iad_baseline_scores.csv | 三类别 global baseline scores。 |
| output | core | exists | iad_mvp/outputs/reference_consistency_3cat/iad_reference_consistency_scores_calibrated.csv | 三类别 global threshold calibrated scores。 |
| table | core | exists | iad_mvp/outputs/tables_3cat/iad_agent_execution_metrics.csv | 三类别 global threshold metrics。 |
| table | core | exists | iad_mvp/outputs/tables_3cat/iad_negative_control_report_3cat.csv | 三类别 negative control report。 |
| table | core | exists | iad_mvp/outputs/tables_3cat/iad_per_category_threshold_recommendations.csv | V16 per-category threshold recommendations。 |
| table | core | exists | iad_mvp/outputs/tables_3cat/iad_per_category_calibrated_metrics.csv | V16 global vs per-category metrics。 |
| output | core | exists | iad_mvp/outputs/reference_consistency_3cat/iad_reference_consistency_scores_per_category_calibrated.csv | V16 per-category calibrated decisions。 |
| table | core | exists | iad_mvp/outputs/tables_3cat/iad_v17_category_constrained_metrics.csv | V17 category-constrained metrics。 |
| table | core | exists | iad_mvp/outputs/tables_3cat/iad_v17_category_constrained_threshold_recommendations.csv | V17 category-constrained threshold recommendations。 |
| output | core | exists | iad_mvp/outputs/reference_consistency_3cat_category_constrained/iad_reference_consistency_scores.csv | V17 category-constrained consistency scores。 |

### 10 原始 benchmark 输出与 held-out 样本

| kind | priority | status | path | role |
| --- | --- | --- | --- | --- |
| output-dir | core | exists | outputs/si2024_three_task_benchmark_summary | Si-style 三任务 benchmark 总目录。 |
| output-dir | support | exists | outputs/v06_blind_ab_review_iad_20260712_105111 | IAD blind A/B review 原始输出目录。 |
| output-dir | support | exists | outputs/v06_blind_ab_review_physical_property_20260712_105111 | Physical Property blind A/B review 原始输出目录。 |
| output-dir | support | exists | outputs/v06_blind_ab_review_physical_property_v2_20260712_163934 | Physical Property v2 blind A/B review 原始输出目录。 |
| output-dir | support | exists | outputs/v06_blind_ab_review_indoor_scene_generation_20260712_130427 | Indoor3D blind A/B review 原始输出目录。 |
| note | support | exists | focused_workflow/tasks/benchmark_cv/02_human_motion_generation.yaml | 02 Human Motion 当前作为 held-out sample，不作为完整闭环主证据。 |
| note | support | exists | focused_workflow/tasks/benchmark_cv/04_3d_reconstruction.yaml | 04 3D Reconstruction 当前作为 held-out sample，不作为完整闭环主证据。 |

## 边界提醒

- 这份目录替代早期偏 Human Motion demo 的旧 tracker；旧 tracker 可作为历史记录，不建议作为当前主目录。
- 当前主线是跨任务 AI 科研自动化 workflow，不是单个 IAD/CV 算法。
- IAD V1.3–V1.8 是真实执行反馈案例；当前 IAD 结果仍是 lightweight scaffold，不是 PatchCore/anomalib 正式 benchmark。
- Indoor3D 使用 seeded evidence bank，最终材料必须透明披露。
- 02 Human Motion 和 04 3D Reconstruction 当前作为 held-out samples，不作为完整闭环主证据。
