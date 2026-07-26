# AAAI-27 科研 Idea 人类匿名盲评操作说明

## 1. 评审目的

本评审用于比较两份匿名科研 idea 或三-idea portfolio 的科学质量。候选来源已隐藏，A/B 位置已随机且平衡。评审者只根据展示内容判断，不需要猜测生成方法。

三位评审者按领域独立填写：

- `physical_property_expert`：物理属性预测；
- `indoor3d_expert`：室内单图 3D 场景生成；
- `iad_expert`：工业异常检测 IAD + Agent。

每位评审者填写自己领域目录中的 20 条，预计 60–90 分钟。可以分两次完成，但同一 item 的 A/B 必须在同一次阅读中比较。

## 2. 盲评纪律

1. 独立完成，不与其他评审者讨论具体条目。
2. 不查看代码仓库、生成日志、方法名、private answer key 或已有 LLM 评审结果。
3. 不使用 ChatGPT、Claude、Gemini 等模型代评或润色理由。
4. 不按篇幅长短直接判胜；更长不代表更好。模板化细节、无关脚本列表和不可信阈值应扣分。
5. 不要求联网检索论文。若候选的证据声明看起来不可信，可以在 concerns 中指出，但不要据此猜方法身份。
6. `tie` 是合法选项：两者科学价值确实相当时应选 tie，不必强行二选一。

## 3. 文件与填写方法

评审者主要使用以下两个中文文件：

```text
匿名评审材料_中文版.md
评审答题表_中文版.xlsx
```

建议用 VS Code/Typora 阅读 Markdown，用 Excel/WPS/LibreOffice 填写 XLSX。Excel 内含“评分表”“候选内容”“评分说明”三个工作表，可以在同一条目 ID 下对照 A/B。不要改变评审者代码和条目 ID，不要增删或排序行。评分必须是整数 1–5。

每读完一个 item，立即填写对应 CSV 行，避免最后凭记忆集中填写。

## 4. 九项评分标准

所有维度分别给 Candidate A 和 Candidate B 打 1–5 分：

| 维度 | 关注问题 |
| --- | --- |
| novelty | 核心机制是否真正区别于直接 baseline 拼接，而不是换名或堆工具？ |
| excitement | 若结果成立，是否值得研究社区关注？ |
| feasibility | 数据、监督、算力和时间是否现实？是否存在无法获得的标签？ |
| expected_effectiveness | 所提机制是否有合理路径改善目标指标？ |
| overall | 综合科学价值，而非写作质量。 |
| baseline_grounding | 是否明确指出具体 baseline 的能力边界，并让新机制直接针对该缺陷？ |
| experimental_rigor | 是否包含合适 baseline、消融、negative control、指标和可证伪条件？ |
| mechanism_specificity | 输入、输出、算法步骤、目标函数或决策规则是否明确且内部一致？ |
| implementation_readiness | 是否能据此开始实现；所需数据、脚本和产物是否合理？ |

统一分数含义：

```text
1 = 明显不足或存在致命问题
2 = 较弱，关键环节缺失
3 = 基本合理，但仍有明显不确定性
4 = 较强，少量问题不影响执行
5 = 非常强、具体、可信且可执行
```

## 5. 总体偏好与置信度

`preference_A_B_tie` 只能填写：

```text
A
B
tie
```

总体偏好应综合九个维度，但重点考虑：核心机制是否成立、实验能否证伪、是否可实现。不要简单对九项分数机械求和。

`confidence_1_5`：

```text
1 = 非常不确定
2 = 较不确定
3 = 中等
4 = 较有把握
5 = 非常有把握
```

`domain_familiarity_1_5` 表示你对该 item 具体子问题的熟悉程度，不是个人能力评价。

## 6. 理由要求

`rationale_required` 每条至少写 1–3 句，必须指出决定偏好的内容依据，例如：

- 某候选的机制和 baseline weakness 是否一致；
- 某损失或模块是否被错误套用；
- negative control 是否真正检验核心假设；
- 数据标签或实验资源是否现实；
- 两者为何应判 tie。

不要只写“更详细”“更完整”“感觉更好”。

`concerns_optional` 可记录共同缺陷、证据疑问、不可实现标签、潜在泄漏或模板化内容。

`minutes_spent` 填该条大致用时，可用小数。

## 7. 提交前自检

提交前确认：

- 20 行均已填写；
- 所有 A/B 九维评分均为 1–5 整数；
- preference 仅为 A/B/tie；
- confidence 和 familiarity 均为 1–5；
- 每条都有实质性 rationale；
- 未修改 item_id，未排序或删除行；
- 文件仍保存为 XLSX，不要另存为 PDF、图片或合并单元格版本。

将完成的文件改名为：

```text
评审答题表_已完成_<reviewer_code>.xlsx
```

评审者只需返还完成后的 XLSX，不需要返还或修改 Markdown packet。旧版 `RESPONSE_SHEET.csv` 仅作为兼容备份，不建议两份同时填写。

## 8. 研究边界

评审结果会以匿名汇总形式用于研究论文，报告样本数、领域分布、偏好胜率和置信区间。该设计每个领域目前只有一位领域评审者，因此可以支持“领域专家盲评”结果，但不能声称测得领域内 inter-rater agreement。若需要该指标，后续必须增加第二位同领域独立评审者或设置共同复评子集。
