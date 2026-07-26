# AI 科研自动化 Workflow 端到端收束报告

生成时间：2026-07-14 21:13:20

生成脚本：`focused_workflow/scripts/build_final_workflow_closing_report.py`

## 1. 一句话结论

本项目已经从 ResearchArena baseline 出发，形成了一个跨任务、证据驱动、可修复、可评价的 AI 科研自动化 workflow 雏形。它的核心贡献不是某一个 CV 算法，而是：

```text
输入科研任务
→ 检索和整理论文
→ 分析 baseline 缺陷
→ 生成细粒度 idea
→ 生成实验计划
→ 多模型匿名评审
→ 根据意见修复 idea
→ 再次盲评
→ 核查论文证据
→ 输出最终研究方案
→ 接入真实数据执行反馈
→ 自动诊断和修复执行层问题
```

当前最重要的新增证据是：IAD 方向已经从“生成研究方案”推进到 MVTec AD 真实数据 smoke test，并形成 V1.3–V1.8 的 execution-feedback repair case。

## 2. Workflow 阶段完成情况

| stage | status | evidence |
| --- | --- | --- |
| Task input | done | v0.2 固定 task_spec 输入和 baseline_cards/focused_ideas/experiment_plan 输出格式。 |
| Paper evidence and baseline weakness | done | v0.5 evidence-grounded ideation；v0.7 reference claim verification。 |
| Focused idea generation | done | v0.3–v0.5 约束 minimal_new_module、algorithmic objective、实验字段、negative controls。 |
| Multi-LLM blind review and repair | done | v0.6 multi-LLM anonymous blind A/B judge；物理属性 v1→v2 二次修复。 |
| Reference claim verification | done | v0.7 对 IAD/Physical/Indoor3D claim-evidence alignment 做自动检查。 |
| Final research plan package | done | v1.0 输出 final research plan schema/package。 |
| Experiment execution planning | done | v1.1 将 final plans 拆成数据准备、脚本、指标和失败检查。 |
| Real-data execution feedback | partially done | v1.3–v1.8 IAD 接入 MVTec AD，形成 execution-feedback repair case。 |
| Full benchmark-grade algorithm implementation | not claimed | 当前 IAD 是 lightweight scaffold，不声称 PatchCore/anomalib 正式 benchmark 或 SOTA。 |

## 3. Idea Generation 核心证据

| task | si2024_style_result | core_value |
| --- | --- | --- |
| IAD + Agent | After win rate 60.00% in 5-judge Si-style report; earlier v0.6 repair 7/9 after wins. | agentic workflow、reference retrieval、evidence-grounded report checker、implementation readiness。 |
| Physical Property | Si-style report shows task-dependent repair failure; later v2 repair achieved 18/18 after wins. | 最强 failure → rationale diagnosis → mechanism-consistent v2 repair 案例。 |
| Indoor 3D Scene | After win rate 80.00% in Si-style report; v0.6/v0.7 evidence-card repaired case reached strong results. | 复杂 3D/generation/reconstruction 任务上的 evidence-grounded ideation 泛化；需披露 seeded evidence bank。 |

解释：

- Si et al.-style benchmark 复用的是 blind review protocol 和评分维度，不是复现 100+ NLP researcher human study。
- 结果是任务依赖的，不能写成“全面提升”。
- 物理属性方向的失败和 v2 修复，反而是本 workflow 最有说服力的 failure-diagnosis-repair 案例之一。

## 4. Reference Claim Verification 证据

| task | papers | claims | pass_rate | note |
| --- | --- | --- | --- | --- |
| IAD + Agent | 24 | 21 | 0.857 | unsupported=0, needs_manual_check=3，保留诚实不确定性。 |
| Physical Property v2 | 51 | 15 | 1.0 | evidence-card repair 后 claim verification pass rate 1.0。 |
| Indoor 3D Scene | 18 | 18 | 1.0 | 使用 seeded evidence bank，最终材料必须透明披露。 |

这说明 idea 并不是凭空生成，而是和 paper evidence、baseline weakness、proposed mechanism 建立了可检查的绑定关系。

## 5. Final Research Plan 与真实执行反馈

V1.0 已经把经过生成、修复、盲评和证据校验的 ideas 转换成 final research plans。V1.1–V1.2 将其拆成执行计划和 IAD MVP scaffold。V1.3–V1.8 则进一步证明：至少在 IAD 方向，workflow 可以接入真实 MVTec AD 数据并从执行反馈中自动修复。

| version | stage | input | finding | key_metric | repair_or_next |
| --- | --- | --- | --- | --- | --- |
| V1.3 | 真实数据接入与单类别 smoke test | MVTec AD bottle | 链路可以跑通，但 reference-consistency 决策没有接受任何异常。 | AUC=0.945238; accepted_anomaly=0 | 进入阈值校准，而不是继续跑更多模型。 |
| V1.4 | 单类别阈值校准 | bottle scores | 默认 consistency_threshold=0.55 明显过低，导致异常被过度 suppress。 | accepted_anomaly 0→51; recall 0.000000→0.809524; FPR=0.000000 | 用自动 threshold sweep 选择低误报 operating point。 |
| V1.5 | 三类别迁移 smoke test | bottle/cable/capsule | bottle 阈值不能直接作为跨类别全局阈值。 | overall_auc=0.490512; overall_recall=0.496212; overall_fpr=0.574257 | 定位为全局阈值不鲁棒，进入类别感知校准。 |
| V1.6 | 类别感知阈值校准 | three-category scores | per-category threshold 显著降低误报。 | FPR 0.574257→0.009901; score -0.078045→0.419451 | 保留低误报，同时暴露 capsule 需要更强特征。 |
| V1.7 | 类别约束检索与类别内归一化 | three-category manifest/reference bank | 修正跨类别 retrieval 和全局归一化后有小幅提升，但瓶颈转向 feature/baseline。 | score 0.419451→0.425705; FPR 0.009901→0.009901; recall=0.435606 | 停止继续调轻量阈值，下一步可接 patch-level/PatchCore 或收束为案例。 |

关键指标：

- V1.3 单类别 bottle lightweight AUC：0.945238
- V1.4 bottle accepted anomaly：0 → 51
- V1.5 全局阈值三类别 FPR：0.574257
- V1.6 类别感知阈值三类别 FPR：0.009901
- V1.6 balanced score：-0.078045 → 0.419451
- V1.7 score / recall / FPR：0.425705 / 0.435606 / 0.009901

最值得放进答辩的一句话：

> V1.5 发现全局阈值跨类别迁移失败，FPR 达到 0.574257；V1.6 自动做类别感知阈值校准，将 FPR 降到 0.009901。这证明 workflow 能将真实执行失败转化为自动诊断和修复信号。

## 6. 当前可以主张什么

- 已经完成一个基于 ResearchArena baseline 的跨任务 AI 科研自动化 workflow 雏形。
- 核心贡献不是单点 CV 算法，而是 baseline-grounded、evidence-grounded、可修复、可评价的 idea generation 和 research-plan generation pipeline。
- workflow 已在 IAD、物理属性预测、室内单图 3D 场景三个代表性任务上完成 idea generation + repair + evaluation + evidence verification 闭环。
- IAD 方向进一步接入真实 MVTec AD 数据，形成真实执行反馈与自动修复案例。

## 7. 当前不能主张什么

- 不声称已经完成所有 5 个 benchmark 方向的完整闭环；02 Human Motion 和 04 3D Reconstruction 当前仍是 held-out samples。
- 不声称 idea generation 达到全球意义上的 SOTA；当前是 Si et al.-style protocol + multi-LLM judge + 人工复核近似评估。
- 不声称 IAD 是最终唯一比赛方向；IAD 是 execution-feedback case study。
- 不声称当前 IAD 结果是完整 PatchCore/anomalib benchmark 或 IAD SOTA。
- 不隐瞒室内 3D 使用 seeded evidence bank。

## 8. 推荐最终材料组织方式

建议把最终材料组织成四层：

1. **主线报告**：本报告，说明端到端 workflow 已经闭环。
2. **核心 idea generation 报告**：`V09_IDEA_GENERATION_CORE_BENCHMARK_REPORT_CN.md`。
3. **最终研究方案包**：`V10_FINAL_RESEARCH_PLAN_PACKAGE_CN.md`。
4. **真实执行反馈案例**：`V18_IAD_EXECUTION_FEEDBACK_REPAIR_CASE_CN.md`。

辅助证据包括：

- `SI2024_BENCHMARK_EVALUATION_REPORT_CN.md`
- `V07_REFERENCE_CLAIM_VERIFICATION_FINAL_SUMMARY_CN.md`
- `V13–V17` IAD execution reports
- `V06_MULTI_LLM_BLIND_AB_EVALUATION_REPORT_V2_CN.md`

## 9. 下一步怎么做

| priority | step | why |
| --- | --- | --- |
| High | 把本报告作为最终主线报告，和 V09/V10/V18 一起组成比赛材料核心证据。 | 现在已经形成 end-to-end story，再继续堆 IAD 会偏离通用 workflow 主线。 |
| High | 制作 8–10 页答辩 PPT：问题、系统流程、三任务 benchmark、证据校验、IAD execution-feedback case、边界与展望。 | 比赛评审更需要清楚故事线，而不是阅读所有版本报告。 |
| Medium | 整理一个 deliverables index，标出每个报告/脚本/输出表对应 workflow 哪一环。 | 避免材料多而散，让评审快速找到证据。 |
| Optional | 如果必须增强工程深度，再考虑 PatchCore/anomalib 或 patch-level feature。 | 这会增强 IAD 工程证据，但也会消耗时间并偏向单任务算法。 |

## 10. 最终建议

现在不要继续陷入 IAD 算法工程。最优路线是开始整理比赛交付材料：

```text
Final report
PPT
deliverables index
workflow diagram
关键表格截图/附录
```

如果后续还有时间，再把 PatchCore/anomalib 作为附加工程增强，而不是主线。
