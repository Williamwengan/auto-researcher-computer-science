# V21 自动深度与执行就绪度检查

生成时间：2026-07-25T09:46:11

## 目的

该实验用于比赛 demo 改进：检查最终研究方案是否具备技术深度、执行路径和证据约束。它不是替代真实科学实验的最终指标，而是智能体内部的自动质量门。

## 总体结果

- 检查方案数：3
- 平均 depth/readiness score：0.905

## 信号均值

| signal | average score |
| --- | ---: |
| mechanism_specificity | 0.76 |
| experimental_rigor | 0.928 |
| execution_readiness | 0.903 |
| evidence_grounding | 0.77 |
| risk_awareness | 0.85 |

## 分任务结果

| task | completion | depth/readiness | warnings |
| --- | ---: | ---: | --- |
| 物理属性预测 | 1.0 | 0.902 | not yet executed as a full benchmark |
| 室内单图 3D 场景生成 | 1.0 | 0.909 | none |
| 工业异常检测 IAD + Agent | 1.0 | 0.905 | none |

## Demo 中怎么讲

The agent does not stop at idea text. It checks whether each research plan has mechanisms, datasets, metrics, negative controls, evidence grounding, failure criteria, and execution artifacts.

中文表达：

```text
我们的系统不止生成 idea 文本，还会自动检查每个研究方案是否包含机制、数据集、指标、负对照、证据绑定、失败标准和执行产物，从而减少表面化 idea。
```
