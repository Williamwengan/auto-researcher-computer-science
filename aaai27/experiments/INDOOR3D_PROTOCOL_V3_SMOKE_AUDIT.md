# Indoor3D Protocol v3 Smoke Audit

日期：2026-07-14

结果目录：`aaai27/experiments/results/raw/smoke_indoor3d_protocol_v3_retry2`

## 结果

- 五种方法 5/5 success，0 failed。
- 每种方法输出 3 个 ideas。
- 所有 metadata 均标记 `evidence_mode=seeded_disclosed`。
- retry2 成功运行内部 retry count 为 0；此前 503 CPU overload 与 524 gateway timeout 保留在原失败目录，归类为 provider outage，不计为模型内容失败。

## 配对与成本

共享 source：`indoor3d_focused_no_repair_s11`

共享初始 ideas SHA-256：

```text
524400130a283770f9fde9dfd6535825e86b213eaa95f65e03b5c4223042af86
```

| method | calls | pipeline tokens |
| --- | ---: | ---: |
| direct_prompt | 1 | 11112 |
| researcharena | 1 | 11626 |
| focused_no_repair | 1 | 10696 |
| focused_generic_refine | 2 | 23429 |
| focused_full | 2 | 24186 |

Generic 与 full 相差 757 tokens，约为 generic pipeline 的 3.23%。两者共享同一初始 ideas，满足配对与近似计算匹配要求。

## 边界

Indoor3D 使用 seeded evidence bank，论文正文、表格注释与补充材料必须披露。Smoke audit 只证明 API、schema、配对、证据标记与成本记录正常，不证明 full 方法质量更高；质量结论必须来自后续匿名评价。
