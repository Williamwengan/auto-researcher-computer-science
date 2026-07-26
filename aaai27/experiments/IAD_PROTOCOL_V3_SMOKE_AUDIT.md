# IAD Protocol v3 Smoke Audit

日期：2026-07-14

协议：`aaai27_focused_workflow_v3_paired_refinement`

模型：`gpt-5.5`，Estelle OpenAI-compatible chat completions

结果目录：`aaai27/experiments/results/raw/smoke_iad_protocol_v3`

## 工程检查

- 五种方法：5/5 success，0 failed。
- 每种方法输出正好 3 个 ideas。
- 所有 metadata 均标记 `evidence_mode=retrieved`。
- 所有调用内部 retry count 为 0。
- 引用 paper IDs 已由生成脚本约束为必须出现在实际 prompt evidence 中。

## 配对设计检查

`focused_generic_refine` 和 `focused_full` 均从 `iad_focused_no_repair_s11` 分叉。

共享初始 ideas SHA-256：

```text
004abd7b9a3b566817f3da6935445bc848082c41ab572c3152ed6e78d4cf4eef
```

因此 generic self-refinement 与 targeted repair 的比较不受不同初始 idea 抽样混杂。

## 成本检查

| method | pipeline calls | pipeline tokens |
| --- | ---: | ---: |
| direct_prompt | 1 | 12330 |
| researcharena | 1 | 12954 |
| focused_no_repair | 1 | 11773 |
| focused_generic_refine | 2 | 25074 |
| focused_full | 2 | 25913 |

两条 refinement pipeline 相差 839 tokens，约为 generic pipeline 的 3.35%，计算预算可视为近似匹配，但论文仍应报告实际 token 与延迟。

## 内容检查

Focused 三个 idea identity 在 no-repair、generic 和 full 中保持一致：

1. Retrieval-Consistency Agent for Shifted or Contaminated Normal Reference Banks。
2. Disagreement-Gated Mask Selection Agent for Weakly Labeled Defect Localization。
3. Evidence-Grounded Report Checker with Selective Human Escalation。

这与 IAD execution-feedback case 的主线一致：reference consistency、mask/report grounding、selective escalation。Smoke audit 只证明 API、schema、配对、证据标记与成本记录正常，不证明 full 方法质量更高；质量结论必须来自后续匿名评价。

## 结论

IAD replicate-11 验证了 protocol v3 的 API、schema、evidence、pairing 和 cost logging。至此，Physical、Indoor3D、IAD 三个任务的 seed=11 五方法 generation smoke test 已全部通过。下一步应冻结这些 seed=11 输出，构建统一匿名 review pack，再启动盲评验证。
