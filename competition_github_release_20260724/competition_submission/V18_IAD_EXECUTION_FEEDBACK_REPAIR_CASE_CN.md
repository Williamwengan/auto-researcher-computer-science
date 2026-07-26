# V1.8 IAD Execution-Feedback Repair Case 总结

生成时间：2026-07-14 21:06:48

生成脚本：`focused_workflow/scripts/build_v18_iad_execution_feedback_repair_case.py`

## 1. 这一阶段到底完成了什么

V1.3–V1.7 不是为了把 IAD 做成一个独立 SOTA 算法，而是为了验证我们的科研自动化 workflow 是否能从“生成研究方案”继续走到“真实数据执行反馈”，并在执行失败时自动诊断和修复。

这组实验形成了一个完整闭环：

```text
最终研究方案
→ 接入真实 MVTec AD 数据
→ 运行 lightweight scaffold
→ 发现执行层失败
→ 自动阈值/类别校准
→ 再次评估
→ 输出结构化修复证据
```

## 2. V1.3–V1.7 时间线

| version | stage | input | finding | key_metric | repair_or_next |
| --- | --- | --- | --- | --- | --- |
| V1.3 | 真实数据接入与单类别 smoke test | MVTec AD bottle | 链路可以跑通，但 reference-consistency 决策没有接受任何异常。 | AUC=0.945238; accepted_anomaly=0 | 进入阈值校准，而不是继续跑更多模型。 |
| V1.4 | 单类别阈值校准 | bottle scores | 默认 consistency_threshold=0.55 明显过低，导致异常被过度 suppress。 | accepted_anomaly 0→51; recall 0.000000→0.809524; FPR=0.000000 | 用自动 threshold sweep 选择低误报 operating point。 |
| V1.5 | 三类别迁移 smoke test | bottle/cable/capsule | bottle 阈值不能直接作为跨类别全局阈值。 | overall_auc=0.490512; overall_recall=0.496212; overall_fpr=0.574257 | 定位为全局阈值不鲁棒，进入类别感知校准。 |
| V1.6 | 类别感知阈值校准 | three-category scores | per-category threshold 显著降低误报。 | FPR 0.574257→0.009901; score -0.078045→0.419451 | 保留低误报，同时暴露 capsule 需要更强特征。 |
| V1.7 | 类别约束检索与类别内归一化 | three-category manifest/reference bank | 修正跨类别 retrieval 和全局归一化后有小幅提升，但瓶颈转向 feature/baseline。 | score 0.419451→0.425705; FPR 0.009901→0.009901; recall=0.435606 | 停止继续调轻量阈值，下一步可接 patch-level/PatchCore 或收束为案例。 |

## 3. 对 workflow 能力的证明

| workflow_capability | evidence |
| --- | --- |
| 研究方案可执行性验证 | V1.3 接入 MVTec AD 并生成 split/manifest/reference bank/baseline/metrics。 |
| 执行反馈诊断 | V1.3 发现 accept_anomaly=0；V1.5 发现全局阈值跨类别失败。 |
| 自动修复策略生成 | V1.4 自动 threshold sweep；V1.6 自动 per-category threshold calibration。 |
| 修复效果量化 | V1.6 将 overall FPR 从 0.574257 降到 0.009901，balanced score 从 -0.078045 提升到 0.419451。 |
| 诚实边界识别 | V1.7 显示类别约束检索只有小幅提升，说明瓶颈进入 lightweight feature 层。 |

## 4. 关键指标摘要

- V1.3 单类别 bottle lightweight AUC：0.945238
- V1.4 bottle accepted anomaly：0 → 51
- V1.5 全局阈值三类别 FPR：0.574257
- V1.6 类别感知阈值三类别 FPR：0.009901
- V1.6 balanced score：-0.078045 → 0.419451
- V1.7 score / recall / FPR：0.425705 / 0.435606 / 0.009901

最重要的结果不是某个 IAD 分数，而是这个修复链：

```text
V1.5 global FPR = 0.574257
V1.6 per-category FPR = 0.009901
```

说明 workflow 能把“跨类别阈值不鲁棒”定位出来，并通过类别感知校准显著降低误报。

## 5. 这应该如何写进比赛材料

建议表述：

> We use IAD as an execution-feedback case study, not as a standalone algorithmic endpoint. After the generated research plan was connected to real MVTec AD data, the initial scaffold exposed two failures: overly conservative anomaly acceptance and poor cross-category threshold transfer. The workflow then produced threshold calibration, per-category calibration, and category-constrained retrieval repairs, turning execution feedback into structured workflow-level improvements.

中文表述：

> 我们不是把 IAD 当成唯一比赛方向，而是把它作为自动科研 workflow 的真实执行反馈案例。系统先生成研究方案，再接入 MVTec AD 数据执行，随后自动发现异常接受率为 0、全局阈值跨类别失败等问题，并进一步生成阈值校准、类别感知校准和类别约束检索等修复策略，最终形成可量化的执行反馈闭环。

## 6. 边界与诚实声明

必须保留以下边界：

1. 当前 IAD 实验是 lightweight scaffold，不是完整 PatchCore/anomalib benchmark。
2. 当前结果不能写成 IAD SOTA。
3. V1.7 只有小幅提升，说明下一层瓶颈已经进入 feature/baseline，而不是继续调阈值。
4. 该案例的核心价值是 workflow 能力证明：生成、执行、失败诊断、修复、再评估。

## 7. 下一步建议

现在有两条路：

### 推荐路线：收束总报告

把 V1.8 写入最终 workflow 报告，作为“真实执行反馈闭环案例”。这条最符合你当前项目主线，因为你的主线是 AI 科研自动化工作流，不是单点 IAD 算法。

### 工程增强路线：继续做 V1.9

如果还想增强 IAD 证据，再做：

```text
V1.9：PatchCore/anomalib or patch-level feature integration
```

但这会把工作重心推向 IAD 算法工程，容易偏离“通用科研 workflow”的主线。

我的建议：先做总报告收束，不要继续陷进 IAD。
