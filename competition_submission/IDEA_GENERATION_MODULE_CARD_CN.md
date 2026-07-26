# Idea Generation Module Card

生成时间：2026-07-13 08:51:51

## 模块名称

Evidence-Grounded Focused Idea Generation

## 模块定位

该模块不是单个 CV 算法，而是 AI 科研自动化 workflow 的 idea generation 核心。它接收不同任务的 task_spec 和 baseline/evidence context，输出结构化、可执行、可评价、可修复的科研 idea。

## 输入

- `task_spec.yaml`：任务目标、输入输出、baseline、metrics、constraints、idea requirements。
- `baseline_cards.jsonl`：从已有 baseline 或论文中抽取的能力、弱点、可借鉴组件。
- `paper evidence / evidence_baseline_cards.jsonl`：论文证据、baseline weakness、支持或不支持的 claim。
- 可选：已有 idea quality score、reviewer rationale、repair history。

## 输出

- `focused_ideas.json`：多个结构化 idea。
- `experiment_plan.json`：可执行实验计划。
- repaired ideas：经过 targeted repair 的改进版本。
- judge summaries：multi-LLM blind A/B 评价结果。
- claim verification summaries：claim 是否被 paper evidence 支持。

## 强制字段

- direct baselines
- transfer baselines
- borrowed components
- minimal_new_module
- algorithmic_objective
- datasets
- metrics
- ablations
- negative controls
- success thresholds
- required scripts
- required data files
- expected tables/figures
- risks and failure criteria

## 评价方式

- rule-based idea quality scoring
- Si et al. 2025 style LLM review rubric
- multi-LLM anonymous blind A/B judge
- reference claim verification
- unsupported/manual-check claim accounting

## 已验证样本

| 任务 | 证明能力 | 关键结果 |
| --- | --- | --- |
| 物理属性预测 | idea generation 模块能发现机制错配，并通过 targeted repair 生成更一致、更可实现的 idea。 | v2: 6 reviewers, 18/18 after wins, win rate 1.0, agreement 1.0；v2 evidence-card repair: papers 51, claims 15, pass rate 1.0 |
| 室内单图 3D 场景生成 | idea generation 模块能迁移到复杂 3D/generation/reconstruction 任务，并用 evidence bank 限制空泛想法。 | 3 reviewers, 9/9 after wins, win rate 1.0, agreement 1.0；evidence-card repair: papers 18, claims 18, pass rate 1.0 |
| 工业异常检测 IAD + Agent | idea generation 模块能处理 agent workflow、retrieval、verification loop、human escalation 和工业指标。 | 3 reviewers, 7/9 after wins, win rate 0.778, agreement 0.778；papers 24, claims 21, pass rate 0.857, unsupported 0, manual 3 |

## 已知边界

- 当前完整闭环集中在 01/03/05 三个样本，02/04 暂作为 held-out benchmark。
- 室内 3D 使用 seeded evidence bank，需透明披露。
- 该模块证明的是 idea generation workflow 的质量提升，不等同于完成所有下游实验。
- “SOTA”需要谨慎表述，应限定在当前 benchmark 和当前对比设置内。
