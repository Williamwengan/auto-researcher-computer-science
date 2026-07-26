# Si et al. (2024)-style Benchmark Evaluation Report

生成日期：2026-07-14

项目目录：`/data1/huangyuling/-A_HYL/AI4S/ResearchArena-main`

## 摘要

本报告参考 Si et al. (2024)《Can LLMs Generate Novel Research Ideas? A Large-Scale Human Study with 100+ NLP Researchers》的 research idea blind-review benchmark，对当前 AI 科研自动化 idea-generation workflow 进行了三方向评测。

需要明确的是：本项目没有复现原论文的 100+ NLP researcher human study。我们复用的是其核心评审协议和评分维度，并将其迁移到 CV / AI4Sci 科研自动化 workflow 中。原论文依赖大规模人类专家盲审，而本项目采用 multi-LLM judge、anonymous blind A/B review 和人工复核相结合的近似评估方式。

本次评测的核心问题是：

> v0.6 critic-repair / evidence-grounded refinement 是否真的提升了 research idea 的质量，而不只是让 idea 变长、字段变多？

结论是：提升具有明显任务依赖性。室内单图生成 3D 场景方向提升最强，IAD + Agent 方向有中等提升，物理属性预测方向在本轮 repair 后没有整体胜出，暴露出 task-specific mismatch 和模板化修复风险。这一负结果很重要，因为它说明 multi-LLM blind review 能发现 repair 失败，并推动后续加入更强的 domain constraints、mechanism consistency checker 和二次修复机制。

## 1. 评测对象

评测对象为 v0.6 critic-repair / evidence-grounded refinement 前后的 idea pair。

每个任务方向包含 3 个 idea pair。每个 pair 由 repair 前 idea 和 repair 后 idea 组成，评审时以 A/B 匿名方式呈现，隐藏 before/after 来源，judge 不知道哪一个是 repair 后版本。

评测覆盖 3 个方向：

| ID | 方向 | 任务含义 |
|---|---|---|
| 01 | IAD / 工业异常检测 + Agent workflow | 面向工业异常检测的 agentic inspection、normal reference retrieval、verification loop、report generation |
| 02 | 物理属性预测 | 从 2D 室内场景图像中预测 object-level density、Young's modulus、friction 等物理属性 |
| 03 | 室内单图生成 3D 场景 | 从单张室内 RGB 图像生成 / 重建 3D scene、layout、object relations 和 renderable representation |

## 2. Judge 设置

每个方向使用 5 个 LLM judge：

| Judge family | 调用方式 |
|---|---|
| GPT 系列 | Estelle API |
| Claude 系列 | Estelle API |
| Gemini 系列 | 云雾 API |
| DeepSeek 系列 | 云雾 API |
| Qwen 系列 | 云雾 API |

每个方向 3 个 pair，每个 pair 由 5 个 judge 评审，因此每个方向共 15 行 judge 结果。

正式统计时使用解码后的 before/after 结果。单方向原始表格中的 A/B 只是匿名代号，不直接等价于 repair 前 / repair 后。

## 3. 评分维度

本评测采用 Si et al.-style 核心维度：

- novelty
- excitement
- feasibility
- expected_effectiveness
- overall

同时针对科研自动化 workflow 增加 4 个扩展维度：

- baseline_grounding
- experimental_rigor
- mechanism_specificity
- implementation_readiness

这些扩展维度用于检查 idea 是否真正变得更可执行、更贴近 baseline weakness、更有实验可检验性，而不是只在文本上变得更复杂。

## 4. 三方向总体结果

| Task | Reviewers | Rows | Before Votes | After Votes | Tie | After Win Rate |
|---|---:|---:|---:|---:|---:|---:|
| IAD | 5 | 15 | 6 | 9 | 0 | 60.00% |
| Physical Property | 5 | 15 | 8 | 7 | 0 | 46.67% |
| Indoor Scene Generation | 5 | 15 | 3 | 12 | 0 | 80.00% |

总体上，repair 后 idea 并非在所有任务上稳定胜出：

- strong improvement：Indoor Scene Generation
- moderate improvement：IAD
- no overall improvement / needs repair redesign：Physical Property

这说明当前 workflow 的 repair 模块已经能在部分任务上显著提升 experimental rigor 和 implementation readiness，但还不能简单宣称“全面提升”。正确结论应是：repair 的效果与任务结构、领域约束和机制一致性强相关。

## 5. 分方向分析

### 5.1 IAD / 工业异常检测 + Agent workflow

IAD 方向 repair 后小幅胜出：

| Metric | Result |
|---|---:|
| Reviewers | 5 |
| Rows | 15 |
| Before Votes | 6 |
| After Votes | 9 |
| Tie | 0 |
| After Win Rate | 60.00% |

关键维度变化：

| Dimension | After-Before |
|---|---:|
| novelty | -0.20 |
| excitement | -0.13 |
| feasibility | -0.33 |
| expected_effectiveness | +0.20 |
| overall | +0.00 |
| baseline_grounding | -0.27 |
| experimental_rigor | +1.00 |
| mechanism_specificity | +1.20 |
| implementation_readiness | +1.00 |

解释：

IAD repair 的主要收益不在 novelty 或 excitement，而在 experimental_rigor、mechanism_specificity 和 implementation_readiness。也就是说，repair 后 idea 更像一个可以进入实验设计和工程验证的方案，但并没有显著提升研究新颖性。

这与当前 workflow 的目标一致：v0.6 repair 的首要作用不是凭空制造创新，而是把原始 idea 变得更具体、更可检验、更适合进入科研自动化后续流程。

### 5.2 物理属性预测

物理属性方向 repair 后没有整体胜出：

| Metric | Result |
|---|---:|
| Reviewers | 5 |
| Rows | 15 |
| Before Votes | 8 |
| After Votes | 7 |
| Tie | 0 |
| After Win Rate | 46.67% |

关键维度变化：

| Dimension | After-Before |
|---|---:|
| novelty | -0.40 |
| excitement | -0.47 |
| feasibility | -0.73 |
| expected_effectiveness | -0.67 |
| overall | -0.53 |
| baseline_grounding | -0.40 |
| experimental_rigor | +0.33 |
| mechanism_specificity | -0.33 |
| implementation_readiness | +0.40 |

解释：

物理属性方向出现了典型的 repair failure：experimental_rigor 和 implementation_readiness 略有提升，但 novelty、excitement、feasibility、expected_effectiveness 和 overall 都下降。这说明 repair 增加了实验细节，却没有保持任务机制的一致性，甚至可能引入了不贴合物理属性预测任务的模板化内容。

这个结果不能被包装成成功。它的价值在于暴露了 workflow 的关键风险：

- critic-repair 可能让 idea 更“完整”，但不一定更“正确”；
- 领域任务需要 task-specific repair constraints；
- repair 后必须有 consistency checker，检查新增实验计划是否和 idea mechanism 对齐；
- multi-LLM blind review 能发现这种“表面更细、整体更差”的失败。

因此，物理属性方向在本报告中应被定义为 failure diagnosis case。它说明系统需要从一次性 repair 升级到“repair -> blind review -> rationale diagnosis -> mechanism-consistent repair”的闭环。

### 5.3 室内单图生成 3D 场景

室内单图生成 3D 场景方向 repair 后明显胜出：

| Metric | Result |
|---|---:|
| Reviewers | 5 |
| Rows | 15 |
| Before Votes | 3 |
| After Votes | 12 |
| Tie | 0 |
| After Win Rate | 80.00% |

关键维度变化：

| Dimension | After-Before |
|---|---:|
| novelty | +0.07 |
| excitement | +0.07 |
| feasibility | +0.27 |
| expected_effectiveness | +0.33 |
| overall | +0.93 |
| baseline_grounding | +0.73 |
| experimental_rigor | +3.13 |
| mechanism_specificity | +1.47 |
| implementation_readiness | +3.40 |

解释：

室内单图生成 3D 场景方向是本次 Si et al.-style benchmark 中最强的 positive case。repair 后不仅 after win rate 达到 80.00%，而且 overall、baseline_grounding、experimental_rigor、mechanism_specificity 和 implementation_readiness 都明显提升。

这说明 critic-repair / evidence-grounded refinement 对复杂生成与重建任务特别有效：它能把原本可能较抽象的 3D scene generation idea，转化为更具体的 baseline 对比、geometry consistency metrics、uncertainty handling、failure cases 和 implementation artifacts。

需要同时披露的是：室内 3D 方向后续 evidence bank 使用了 seeded evidence bank。因此在比赛报告中，它适合作为 workflow 在复杂任务上的 evidence-grounded ideation 示例，但不应被描述为完全自动检索闭环的唯一证据。

## 6. 跨任务结论

本次 benchmark 给出三个重要结论。

第一，repair 并不等于全面提升。IAD 和室内 3D 有明显或中等收益，但物理属性方向 repair 后整体下降。这说明多模型盲评是必要的，因为它能发现“字段更完整但 idea 更差”的情况。

第二，repair 最稳定提升的是 experimental_rigor 和 implementation_readiness。IAD 和室内 3D 的提升主要体现在实验严谨性、机制具体性和实现就绪度，而不是 novelty 或 excitement。这符合 focused workflow 的目标：把 idea 从开放式 proposal 变成可执行科研计划。

第三，domain constraints 和 consistency checker 是下一步关键。物理属性方向说明，如果 repair prompt 过于通用，可能会引入 task-specific mismatch。因此后续必须加入：

- task-specific repair constraints；
- mechanism consistency checker；
- domain verifier；
- evidence-to-claim alignment checker；
- repair rationale tracing。

## 7. 对项目主线的意义

本 benchmark 不是为了证明某一个 CV 任务上算法性能更高，而是为了评估 idea-generation workflow 本身：

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
```

Si et al.-style benchmark 对应的是其中的“多模型匿名评审”和“repair 是否有效”两段。它证明：本 workflow 不只是生成想法，还能通过 blind review 检查想法是否真的变好，并暴露 repair 失败案例。

因此，当前项目最稳妥的阶段性定位是：

> 本项目已完成从科研任务输入到 evidence-grounded idea generation、targeted repair、multi-LLM blind evaluation 和 reference claim verification 的核心闭环，能够输出经过多轮评审和证据校验的最终研究方案草案。下一阶段将从“方案生成”推进到“方案执行”，即自动生成实验代码、运行实验、收集结果并形成最终科研报告。

## 8. 比赛报告建议写法

推荐写法：

> Multi-LLM blind review under a Si et al.-style research idea benchmark shows that our critic-repair workflow substantially improves experimental rigor and implementation readiness, especially for indoor scene generation and IAD. However, performance is task-dependent; in physical property prediction, repair sometimes introduces task-specific mismatch, indicating the need for stronger domain constraints and consistency checks.

中文对应表述：

> 基于 Si et al.-style research idea benchmark 的多模型匿名盲评显示，本项目的 critic-repair workflow 能显著提升部分任务中的实验严谨性和实现就绪度，尤其是在室内单图生成 3D 场景和 IAD + Agent 方向上表现明显。但该提升具有任务依赖性：在物理属性预测方向，repair 曾引入 task-specific mismatch，说明后续需要更强的领域约束和机制一致性检查。

不建议写法：

- “我们的 workflow 在所有任务上全面提升 idea 质量。”
- “我们复现了 Si et al. 的 100+ 人类研究者实验。”
- “repair 后 idea 一定优于 repair 前。”
- “multi-LLM judge 等价于人类专家评审。”

## 9. 局限性

本评测仍有以下局限：

1. 没有复现 Si et al. 原论文的 100+ NLP researcher human study。
2. 评审主体是 LLM judge，不是大规模人类领域专家。
3. 每个方向只有 3 个 idea pair，共 15 行 judge 结果，样本规模较小。
4. 该 benchmark 评价的是 idea quality，不是下游实验真实性能。
5. A/B 盲评能降低来源偏见，但不能完全消除 LLM judge 的模型偏好。
6. 室内 3D 方向后续使用 seeded evidence bank，需要在最终材料中透明披露。

## 10. 后续改进方向

基于本次 benchmark，下一步建议如下：

1. 增加 task-specific repair constraints，避免模板化修复。
2. 增加 mechanism consistency checker，检查新增实验计划是否和 idea 机制一致。
3. 增加 domain verifier，保证 repair 不偏离任务领域。
4. 对 physical_property 方向单独设计领域约束和 mechanism-consistent repair。
5. 将 Si et al.-style benchmark 结果写入比赛技术路线中的智能体评估模块。
6. 在后续端到端 workflow 中，把 blind review rationale 自动反馈给 repair prompt，形成可迭代闭环。

## 11. 输出文件索引

三方向总表：

```text
outputs/si2024_three_task_benchmark_summary/SI2024_THREE_TASK_BENCHMARK_SUMMARY_CN.md
outputs/si2024_three_task_benchmark_summary/si2024_three_task_summary.json
```

三个方向单独表格：

```text
outputs/v06_blind_ab_review_iad_20260712_105111/si2024_summary/si2024_iad_summary_CN.md
outputs/v06_blind_ab_review_physical_property_20260712_105111/si2024_summary/si2024_physical_property_summary_CN.md
outputs/v06_blind_ab_review_indoor_scene_generation_20260712_130427/si2024_summary/si2024_indoor_scene_generation_summary_CN.md
```

本正式报告：

```text
competition_submission/SI2024_BENCHMARK_EVALUATION_REPORT_CN.md
```

