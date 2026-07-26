# AAAI-27 冻结实验协议 v1

冻结日期：2026-07-14

## 研究假设

- H1：完整 workflow 相比 direct prompting 和 ResearchArena，提高 idea 的 overall preference、mechanism specificity、experimental rigor 与 implementation readiness。
- H2：evidence grounding 降低 unsupported claims，并提高 baseline grounding。
- H3：targeted repair 的收益依赖 mechanism/domain consistency；无该约束的 repair 可能退化。
- H4：LLM judge 与人类专家存在正相关，但存在位置、长度和模型家族偏差，需要单独测量。

## 主任务

- `01_physical_property_prediction`：强 failure-diagnosis-repair 样本。
- `03_indoor_scene_generation`：复杂生成任务；seeded evidence 必须单独标记。
- `05_iad_agent_workflow`：agent/workflow 与执行反馈样本。

02/04 保持 held-out，不出现在主结果中，除非在冻结设置下完整运行且不据其结果修改系统。

## 主实验方法

- `direct_prompt`：直接要求基础模型生成研究 ideas。
- `researcharena`：原始 ResearchArena ideation baseline。
- `focused_no_repair`：结构化、evidence-grounded generation，但无 critic repair。
- `focused_generic_refine`：与完整系统共享完全相同的 `focused_no_repair` 初始 ideas，第二次只做通用自我改写，不使用机制一致性 targeted repair。
- `focused_full`：完整 generation + consistency-aware targeted repair。

## 公平性约束

所有方法在每个 task/seed 上使用：同一生成模型、同一 evidence pool、相同 idea 数、相近最大输出 token、相同匿名化 formatter。检索本身若属于被测模块，应另做 retrieval ablation，而不能悄悄给一个方法更多论文。

默认每个 task × method 使用 5 个独立 stochastic replicates；每次输出 3 个 ideas。11/23/37/53/71 是 replicate IDs，不是 provider 可复现随机种子，API 请求不发送 seed。主实验清单仍表示 3×5×5=75 个方法结果、225 ideas；实际生成时 `focused_no_repair` 的同一初始输出被分叉给 generic refine 和 full repair，避免重复初始抽样。两条 refinement pipeline 都计入共享 initial generation 的成本，用于隔离额外推理预算和 targeted repair 本身的贡献。

## 消融

- `full`
- `no_evidence`
- `no_repair`
- `no_consistency_check`
- `no_claim_verification`

其中 claim verification 主要影响 unsupported-claim rate 和最终方案通过率，不应虚构为直接改善生成分数。

## 评测

LLM 盲评维度：novelty、excitement、feasibility、expected effectiveness、overall、baseline grounding、experimental rigor、mechanism specificity、implementation readiness。

人类盲评：随机 A/B、隐藏来源、交换位置复测子集、记录领域熟悉度与置信度。主要终点为 `focused_full` 对 `researcharena` 的 overall preference win rate。次要终点为各维度配对差。

统计：报告 N、win rate、95% bootstrap CI、配对效应量；多维比较做 Holm 校正。LLM-human 对齐报告 Spearman 相关和一致率。不得只报告胜票数。

## 数据泄漏规则

- prompt、repair 规则和阈值在查看主 test 结果前冻结。
- IAD threshold calibration 与最终 test 分离。
- 失败、重试、解析错误全部保留。
- seeded Indoor3D evidence 与在线检索 evidence 分开标注。

## 成本日志

每个 run 保存 provider、model id、temperature、seed、input/output tokens、estimated cost、wall time、retry count、status 和 artifact paths。API key 不得写入 manifest 或论文仓库。

## Go/No-Go

AAAI 主结果必须至少包含公平 baseline、四项消融、人类或明确降格的人工复核、置信区间、verifier gold-set 验证以及一键表格复现。未满足时降低 claim，不得用比赛材料中的总结性措辞替代实验。
