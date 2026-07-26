# Physical Property Protocol v3 Smoke Audit

日期：2026-07-14

协议：`aaai27_focused_workflow_v3_paired_refinement`

模型：`gpt-5.5`，Estelle OpenAI-compatible chat completions

结果目录：`aaai27/experiments/results/raw/smoke_physical_protocol_v3`

## 工程检查

- 五种方法：5/5 success，0 failed。
- 每种方法输出正好 3 个 ideas。
- Baseline 使用原生 proposal schema；Focused 使用结构化实验 schema。
- 同一任务的 task/evidence prompt 前缀一致。
- 引用 paper IDs 均出现在实际保存的 prompt evidence 中。

## 配对设计检查

`focused_generic_refine` 和 `focused_full` 均从 `physical_focused_no_repair_s11` 分叉。

共享初始 ideas SHA-256：

```text
662bfa6909a0df543ce1e90cd6a1a9da0ff37fa6442f19eeba89b7fcef704a88
```

因此 generic self-refinement 与 targeted repair 的比较不受不同初始 idea 抽样混杂。

## 成本检查

| method | pipeline calls | pipeline tokens |
| --- | ---: | ---: |
| direct_prompt | 1 | 12400 |
| researcharena | 1 | 13015 |
| focused_no_repair | 1 | 12369 |
| focused_generic_refine | 2 | 27041 |
| focused_full | 2 | 27722 |

两条 refinement pipeline 相差 681 tokens，约为 generic pipeline 的 2.52%，计算预算可视为近似匹配，但论文仍应报告实际 token 与延迟。

## 内容检查

Focused 三个 idea identity 在 no-repair、generic 和 full 中保持一致：

1. Object-material interval lookup / mixture prediction。
2. Mask-conditioned localized material evidence verifier。
3. Segmentation-property sensitivity calibration / uncertainty propagation。

未发现把 Idea 1 的 interval mapping 机制错误复制到 Idea 2/3 的旧版 physical repair failure。最终质量是否提高仍需匿名人类/LLM 评价，不能由本 smoke audit 推断。

## 结论

Physical replicate-11 验证了 protocol v3 的 API、schema、evidence、pairing 和 cost logging。v1/v2 结果保留为协议诊断，不进入主结果。下一步在不修改 prompt 的条件下迁移到 Indoor3D 和 IAD replicate-11。
