# Final Storyline for Competition

生成时间：2026-07-13 08:51:51

## 30 秒开场

我们做的不是某一个 CV 算法，而是一个面向 AI4Sci 的科研自动化 workflow。我们发现，很多自动科研系统最大的问题不是不会写代码，而是第一步 idea generation 就容易空泛：没有明确 baseline、没有最小实验、没有 negative control，也缺少论文证据校验。

## 核心方法

我们基于 ResearchArena baseline，构建了 focused idea generation workflow：

1. 用 task_spec 固定任务输入。
2. 用 baseline cards 约束 idea 必须针对真实 baseline weakness。
3. 用 evidence-grounded ideation 绑定论文证据。
4. 用 targeted repair 修复空泛、机制错配和证据不足。
5. 用 multi-LLM blind A/B judge 检查 repair 后 idea 是否真的更好。
6. 用 reference claim verification 检查 claim 是否被论文证据支持。

## 三个证据样本

物理属性预测：这是最强闭环案例。v1 repair 曾经失败，after win rate 只有 0.556。我们没有掩盖失败，而是用 reviewer rationale 定位问题：Idea 2 和 Idea 3 错误套用了 Idea 1 的 interval-mapper loss。v2 修复后，6 个 judge 共 18 票全部选择 after，证据校验 pass rate 也达到 1.0。

IAD + Agent：这个样本说明我们的 idea 不是空泛文本，而能落成 agent workflow 字段：normal reference retrieval、verification loop、evidence-grounded report checker、negative controls、success thresholds。它的 v0.6 after win rate 是 0.778，v0.7 pass rate 是 0.857，unsupported 为 0。

室内单图 3D：这个样本说明 workflow 可以迁移到复杂生成/重建任务。我们也透明说明：初始检索 evidence bank 为空，因此使用 seeded evidence bank 补齐代表性论文；该方向 9/9 after wins，证据校验 pass rate 1.0。

## 评委可能问的问题

Q：你们是不是只做了 IAD 或某一个任务？

A：不是。IAD、物理属性和室内 3D 都是 benchmark samples，用来测试同一个 idea generation pipeline。我们的贡献是跨任务 workflow，而不是单点算法。

Q：为什么 02 Human Motion 和 04 3D Reconstruction 暂时不跑？

A：它们作为 held-out benchmark 保留。当前阶段先用 01/03/05 三个已完成闭环的样本证明模块能力，避免继续消耗 API 和堆结果。后续会用 02/04 验证进一步泛化。

Q：你们能说 idea generation 已经 SOTA 吗？

A：我们会谨慎表述。当前可以说：在我们的 benchmark 样本和对比设置下，相比 ResearchArena baseline，idea 输出在结构化、可实现性、repair 后质量和证据可校验性上显著增强。全球意义的 SOTA 需要更大规模 benchmark 和人工评审。

Q：室内 3D 的 seeded evidence bank 会不会影响可信度？

A：我们会透明披露。它不作为唯一结论，而是作为复杂任务上的 workflow demonstration。核心证据仍来自生成、修复、盲评和 claim verification 的闭环。

## 收束句

我们的系统把 idea generation 从“生成一段看起来合理的想法”，推进为“可约束、可修复、可盲评、可证据校验的科研工作流模块”。这为后续自动实验规划、代码执行和论文报告生成打下基础。
