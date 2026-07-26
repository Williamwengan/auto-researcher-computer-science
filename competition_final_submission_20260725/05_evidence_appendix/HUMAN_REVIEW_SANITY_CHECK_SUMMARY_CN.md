# 小规模专家辅助评审摘要

说明：该部分只作为 sanity check，不作为主评价依据。

三方向共 60 条 blind review sanity check：

```text
focused_full wins/losses/ties = 39/15/6
tie-half win rate = 70.0%
95% CI = [57.5%, 80.1%]
mean confidence = 3.433
```

分方向：

| task | N | W/L/T | win rate | mean confidence |
| --- | ---: | --- | ---: | ---: |
| IAD | 20 | 15/2/3 | 82.5% | 4.3 |
| indoor3D | 20 | 14/6/0 | 70.0% | 3.0 |
| physical | 20 | 10/7/3 | 57.5% | 3.0 |

边界：

- 每个方向只有一位专家，因此不能建立 inter-rater reliability；
- indoor3D 表含 AI 辅助说明，应作为非正式辅助诊断；
- 主证据仍是自动化 workflow、multi-LLM blind review、reference claim verification 和 IAD execution-feedback case。

