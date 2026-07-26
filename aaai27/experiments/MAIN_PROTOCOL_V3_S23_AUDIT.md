# Main Protocol v3 Replicate 23 Audit

日期：2026-07-15

协议：`aaai27_focused_workflow_v3_paired_refinement`

模型：`gpt-5.5`，Estelle OpenAI-compatible chat completions

结果目录：`aaai27/experiments/results/raw/main_protocol_v3_s23`

## 工程检查

- 计划运行：15。
- 成功运行：15。
- 失败运行：0。
- 所有调用 retry count 均为 0。
- 每个 run 输出 3 个 ideas。
- `focused_generic_refine` 与 `focused_full` 均从同 replicate 的 `focused_no_repair` 分叉。

## 配对 SHA 检查

| task | source run | shared SHA-256 |
| --- | --- | --- |
| Physical Property | `physical_focused_no_repair_s23` | `e2393577c68e72b43c8bb5312c4da76d60ef2d10fecce767bdfebdaf9d561556` |
| Indoor3D | `indoor3d_focused_no_repair_s23` | `95147ec106da9b58a90d63786853f18bee665baf41b59b663b3a8c3bd5e22cfd` |
| IAD | `iad_focused_no_repair_s23` | `92c438fb7b69636b7515e6aab0a7a39113f3db887abc0b439898234e4dc2c514` |

## 成本检查

| task | direct | researcharena | no repair | generic refine | full repair |
| --- | ---: | ---: | ---: | ---: | ---: |
| Physical Property | 12410 | 12777 | 12394 | 27302 | 27647 |
| Indoor3D | 10958 | 11587 | 11023 | 24237 | 24829 |
| IAD | 12251 | 12800 | 12041 | 25668 | 26595 |

Token accounting uses `pipeline_usage_by_call` for two-call refinement methods and `usage_by_call` for one-call methods.

## 内容检查

Focused branches preserve idea identity within each task:

- Physical Property: material-conditioned interval lookup; evidence-gated VLM verification; segmentation-uncertainty propagation.
- Indoor3D: uncertainty-aware layout scene completion; object-centric proxy mesh retrieval; ambiguity/failure-calibrated benchmark.
- IAD: reference-consistency agent; disagreement-guided mask selection; evidence-grounded report checker.

## 结论

Replicate 23 verifies that the frozen protocol generalizes beyond the seed-11 smoke setting. The next step is to run replicates 37, 53, and 71, then build the full anonymous review pack over all successful main generations.
