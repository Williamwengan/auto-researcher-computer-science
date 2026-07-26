# V0.6 Multi-LLM 匿名 A/B 评估总报告 V2

本报告更新了物理属性预测方向：原 v1 repair 存在机制错配，已通过 v2 mechanism-consistent repair 修复，并用 6 个 LLM judge 重新匿名盲评。

## 1. 总体结果

| 方向 | 版本说明 | Reviewers | Votes | After Wins | Before Wins | Ties | After Win Rate | Agreement | 结论 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 工业异常检测 IAD + Agent | v0.5 repair | 3 | 9 | 7 | 2 | 0 | 0.778 | 0.778 | repair 后较优 |
| 物理属性预测 | v2 mechanism-consistent repair, 6 judge | 6 | 18 | 18 | 0 | 0 | 1.0 | 1.0 | repair 后显著更优 |
| 室内单图 3D 场景生成 | v0.5 repair with seeded evidence bank | 3 | 9 | 9 | 0 | 0 | 1.0 | 1.0 | repair 后显著更优 |

## 2. 物理属性方向 v1 到 v2 的关键修复

物理属性 v1 repair 的问题是：Idea 2 和 Idea 3 被错误套用了 Idea 1 的 interval-mapper loss，导致 localized verifier 和 proposal uncertainty 的机制不一致。
v2 修复将 Idea 2 改为局部视觉证据验证目标，将 Idea 3 改为 proposal uncertainty propagation 目标。
修复后，6 个 judge 在 3 个 pair 上全部选择 after，After win rate 从 0.556 提升到 1.0。

## 3. 各方向维度提升 Top 维度

### 工业异常检测 IAD + Agent

| Dimension | Mean After-Before | Positive | Negative | Tie |
|---|---:|---:|---:|---:|
| implementation_readiness | 2.222 | 6 | 1 | 2 |
| mechanism_specificity | 2.0 | 7 | 2 | 0 |
| experimental_rigor | 1.889 | 7 | 0 | 2 |
| overall | 1.0 | 6 | 2 | 1 |
| expected_effectiveness | 0.333 | 4 | 2 | 3 |

### 物理属性预测

| Dimension | Mean After-Before | Positive | Negative | Tie |
|---|---:|---:|---:|---:|
| mechanism_specificity | 4.611 | 18 | 0 | 0 |
| experimental_rigor | 3.833 | 18 | 0 | 0 |
| implementation_readiness | 3.667 | 18 | 0 | 0 |
| overall | 2.833 | 18 | 0 | 0 |
| expected_effectiveness | 1.722 | 18 | 0 | 0 |

### 室内单图 3D 场景生成

| Dimension | Mean After-Before | Positive | Negative | Tie |
|---|---:|---:|---:|---:|
| implementation_readiness | 3.889 | 9 | 0 | 0 |
| experimental_rigor | 3.667 | 9 | 0 | 0 |
| mechanism_specificity | 2.556 | 9 | 0 | 0 |
| overall | 1.889 | 9 | 0 | 0 |
| baseline_grounding | 1.111 | 7 | 0 | 2 |

## 4. 结论

- v0.6 结果说明：v0.5/v2 repair 不只是提高规则分，也在匿名 multi-LLM judge 下提升 idea 质量。
- 当前提升最明显的是 experimental_rigor、mechanism_specificity、implementation_readiness。
- 物理属性方向提供了一个重要闭环案例：系统能发现 repair 失败、定位机制错配，并通过二次修复显著改善。
- 下一阶段应进入 v0.7 reference claim verification，检查 evidence 是否真的支持 baseline weakness 和 proposed improvement。
