# Main Protocol v3 Generation Audit

日期：2026-07-15

协议：`aaai27_focused_workflow_v3_paired_refinement`

模型：`gpt-5.5`，Estelle OpenAI-compatible chat completions

## 覆盖范围

| axis | values |
| --- | --- |
| tasks | Physical Property, Indoor3D, IAD |
| methods | direct prompt, ResearchArena-style, focused no repair, generic refinement, targeted repair |
| replicates | 11, 23, 37, 53, 71 |
| total runs | 75 |

## 完整性检查

- 成功运行：75/75。
- 失败运行：0。
- 缺失运行：0。
- provider retry count：0。
- 每个 run 输出 3 个 ideas。
- Indoor3D 保持 `seeded_disclosed` evidence mode。

## 配对检查

所有 15 个 task-replicate 组合均满足：

```text
focused_generic_refine.paired_initial_ideas_sha256
==
focused_full.paired_initial_ideas_sha256
```

这说明 generic refinement 与 targeted repair 的比较共享相同初始 focused ideas，不受初始抽样差异混杂。

## 已生成匿名评审包

输出目录：

```text
aaai27/experiments/results/derived/review_pack_main_v3_all_v1/
```

文件：

- `anonymous_review_items.jsonl`：120 个 public blind review items。
- `anonymous_review_pack.md`：可读版 public blind review pack。
- `private_answer_key.jsonl`：私有方法映射，不给 reviewer。
- `candidate_length_stats.csv`：私有长度统计，不给 reviewer。
- `review_pack_summary.md`：评审包摘要。

公开文件已检查，不包含 `focused_full`、`focused_no_repair`、`focused_generic_refine`、`researcharena`、`direct_prompt` 等方法名。

## 结论

AAAI-27 主生成实验已完成。下一步进入 full anonymous review：先运行一个 reviewer 覆盖 120 个 items，确认全量评审流程稳定后，再扩展到多 reviewer。
