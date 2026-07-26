# AAAI-27 投稿就绪度审计与冲刺计划

审计日期：2026-07-14

目标会议：AAAI-27 Main Technical Track

官方时间（AoE）：摘要截止 2026-07-21，全文截止 2026-07-28，补充材料与代码截止 2026-07-31。

## 1. 结论

当前项目已经具备一篇系统论文的技术原型、研究问题、初步证据和案例材料，但尚未达到可稳妥投稿 AAAI 主会的实验完整度。

本周可以完成：论文定位冻结、实验协议冻结、AAAI LaTeX 初稿、图表骨架、自动评测重跑和人工评审表准备。

本周不宜承诺完成：足量专家评审、全部消融、多随机种子统计、复现清理和最终英文稿润色。若集中投入，可在 2026-07-28 前形成一版可提交稿，但时间非常紧，实验质量必须优先于继续增加 workflow 版本。

## 2. 推荐论文定位

建议标题方向：

> Evidence-Grounded and Repairable Research Ideation: A Cross-Task Workflow with Blind Evaluation and Execution Feedback

核心研究问题：

> 在控制模型、任务、检索证据和生成预算的条件下，结构化证据约束、机制一致性修复和执行反馈，能否稳定提高研究 idea 的具体性、可验证性与实现就绪度？

建议只提出三项主要贡献：

1. 一个结构化、证据驱动、可修复的跨任务科研 idea generation workflow。
2. 一个包含盲评、机制一致性检查和 claim-evidence verification 的评价闭环。
3. 一个展示执行失败如何反馈到方案修复的真实数据案例。

IAD 是 execution-feedback case study，不是论文的唯一任务，也不作为 IAD 算法 SOTA 贡献。

## 3. 当前已有证据

| 论文所需部分 | 当前材料 | 状态 |
| --- | --- | --- |
| 系统定义 | v0.2-v1.2 脚本、schema、prompt | 已有 |
| 跨任务样本 | Physical、Indoor3D、IAD | 初步已有 |
| repair 前后盲评 | v0.6、Si-style benchmark | 已有但样本小 |
| 失败诊断案例 | Physical v1→v2 | 较强 |
| claim-evidence 检查 | v0.7 | 已有自动结果 |
| 执行反馈案例 | IAD v1.3-v1.8 | 已有但为 lightweight scaffold |
| AAAI 英文论文 | 无 `.tex` / `.bib` 稿件 | 缺失 |
| 公平 baseline 主实验 | 当前不同报告口径尚未统一 | 缺失 |
| 系统消融 | 未形成完整矩阵 | 缺失 |
| 人类专家评审 | 没有正式、足量、可统计的人评 | 缺失 |
| 多随机种子/置信区间 | 未系统报告 | 缺失 |
| 可复现发布包 | 代码存在，但未匿名化、清理和一键复现 | 缺失 |

## 4. 投稿前必须补齐的实验

### E1 公平 baseline 比较（最高优先级）

比较至少四种设置：

1. ResearchArena 原始 ideation。
2. 直接 LLM prompting。
3. Focused Workflow，不含 repair。
4. Focused Workflow，完整版本。

必须控制：同一任务输入、同一基础模型、相近 token budget、同一论文证据池、相同 idea 数量和匿名化格式。否则无法把提升归因于 workflow。

最低规模：3 个已完成任务 × 每个任务至少 5 个独立生成 seed × 每个设置 3 个 ideas。理想情况下再加入 02/04 作为真正 held-out 测试，但在时间不足时不可把它们写成已验证结果。

### E2 组件消融

至少比较：

- 完整系统；
- 去掉 evidence grounding；
- 去掉 targeted repair；
- 去掉 mechanism/domain consistency check；
- 去掉 reference claim verification；
- 去掉 execution feedback（只作为系统能力分析，不要求所有任务真实执行）。

主要指标：novelty、feasibility、expected effectiveness、baseline grounding、mechanism specificity、experimental rigor、implementation readiness、overall。

### E3 人类专家盲评

Multi-LLM judge 不能单独证明 idea 质量，因为生成者和评价者都来自 LLM，存在共同偏好、风格偏差和长度偏差。

最低可接受方案：

- 6-10 名有相关研究经验的评审者；
- 每人评 12-20 个匿名 pair；
- A/B 顺序随机，隐藏方法来源；
- 记录领域熟悉度与置信度；
- 报告胜率、均值差、95% bootstrap CI、评审一致性；
- 同时检查长度归一化或提供等长度版本，排除“更长所以更好”。

如果无法完成此项，论文必须降格表述为 preliminary LLM-based evaluation，AAAI 主会说服力会明显不足。

### E4 自动评审可靠性

需要回答 multi-LLM judge 是否可信：

- LLM judge 与人类评审的 Spearman/Kendall 相关；
- 各 judge 的偏好与一致性；
- position bias 测试（交换 A/B）；
- self-family bias 测试；
- 长度、措辞和格式控制；
- 平局规则和解析失败率。

### E5 claim verification 的人工标注验证

当前 pass rate 不是 verifier 准确率。需要人工标注一批 claim-paper pair，形成 gold set，并报告：

- supported / weak / unsupported 分类准确率或 macro-F1；
- unsupported claim 的 precision、recall；
- 至少两名标注者的一致性；
- seeded evidence bank 与在线检索证据分开报告。

### E6 成本、延迟和稳定性

报告每个任务：模型调用次数、输入/输出 token、估算费用、墙钟时间、失败/重试率、各阶段成功率。系统论文需要说明质量提升的成本。

### E7 执行反馈案例边界

保留 IAD V1.5→V1.6（FPR 0.574257→0.009901）作为案例，但必须同时报告 recall，并说明阈值是否在独立 validation split 上选择。不能在 test labels 上调阈值后再把同一 test 结果当泛化性能。

投稿前应将 MVTec 数据切为 calibration/validation/test，或使用 train-good 构造无监督校准协议；最终 test 只评一次。当前 lightweight baseline 不能称为 PatchCore。

## 5. 统计与实验规范

- 预先冻结任务、prompt、模型版本、temperature、seed、token budget 和评审规则。
- 主结果报告样本数、均值、标准差/置信区间，而不仅是 vote count。
- pairwise 胜率使用 bootstrap CI；多维分数使用配对检验并报告 effect size。
- 多重比较时说明校正策略。
- 保存每次生成、失败、重试和解析日志。
- 将 Physical v1 repair failure 作为真实负结果保留，避免只挑成功案例。

## 6. 论文与复现材料

必须建立：

```text
paper/
  main.tex
  references.bib
  sections/
  figures/
  tables/
  appendix.tex
  reproducibility_checklist.tex
reproducibility/
  README.md
  environment.yml 或 requirements-lock.txt
  run_main_experiments.sh
  run_ablations.sh
  build_tables.py
  configs/
```

论文正文建议 7 页技术内容：

1. Introduction（0.8 页）
2. Related Work（0.7 页）
3. Method（1.5 页）
4. Experimental Setup（1.0 页）
5. Results and Analysis（2.0 页）
6. Limitations/Ethics/Conclusion（1.0 页）

主文至少需要：系统流程图、主结果表、消融表、人类/LLM judge 对齐图、failure→repair 案例图。IAD 执行反馈适合放案例图或附录，不应挤占主结果。

## 7. 两周冲刺安排

### 07-14 至 07-15：冻结协议

- 冻结论文 claim、baseline、任务和指标。
- 建立 AAAI LaTeX 工程、标题、摘要、章节骨架。
- 生成统一 experiment manifest，停止修改 prompt。
- 准备并发出人类盲评表。

### 07-16 至 07-18：主实验

- 并行运行 E1 公平 baseline 和 E2 消融。
- 汇总 token、费用、延迟和失败率。
- 人工标注 claim verification gold subset。

### 07-19 至 07-20：统计与第一稿

- 统一解析实验结果，生成表格和 95% CI。
- 完成 Method、Setup、Results 初稿。
- 完成匿名化检查和摘要定稿。

### 07-21：提交摘要

- 摘要必须与最终全文 claim 保持一致。
- 确认所有作者及 OpenReview 账户；截止后作者变更通常受严格限制。

### 07-21 至 07-24：人评与可靠性

- 收回人类盲评。
- 完成 E3/E4、评审一致性和偏差分析。
- 完成 Related Work、Limitations、Ethics。

### 07-25 至 07-26：内部审稿

- 做一次“拒稿理由”审计：新颖性、baseline 公平性、样本量、泄漏、统计、可复现性。
- 压缩到页数限制，修复图表和引用。

### 07-27：冻结全文

- 编译检查、匿名化检查、引用核查、数字一致性检查。
- 不再新增实验，只修正文与明确限制。

### 07-28：提交全文

- 预留至少 12 小时处理 OpenReview、PDF 字体和格式问题。

### 07-29 至 07-31：补充材料与代码

- 清理匿名仓库、运行一键复现、提交 appendix/code/data artifacts。

## 8. Go / No-Go 标准

满足以下条件才建议提交 AAAI-27 Main Track：

- 至少 3 个任务上的公平 baseline 主实验完成；
- 至少 4 个关键组件的消融完成；
- 有独立人类评审，或至少已完成规模明确的人工复核且论文诚实降格 claim；
- 主结果有置信区间和显著性/效应量；
- claim verifier 有人工 gold-set 评测；
- 代码可从干净环境复现主要表格；
- 论文不宣称 idea-generation SOTA、IAD SOTA 或五任务完整验证。

若 07-21 前主实验仍未形成稳定结果，建议保留摘要注册，但在 07-25 做最终 Go/No-Go；不要为了赶截稿提交一篇只有比赛报告和 LLM 自评的稿件。

## 9. 当前最优先动作

现在应立即停止新增版本报告，进入论文实验冻结。第一项任务是建立统一的 `experiment_manifest`，确保 ResearchArena、direct prompting、no-repair 和 full workflow 在相同模型、证据、预算与随机种子下可比较。没有这一步，后续表格即使数字很多也无法形成可信的因果结论。
