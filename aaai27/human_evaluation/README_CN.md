# 人类评审材料分发说明（项目负责人阅读）

把以下材料分别发给对应同学：

| 评审者 | 发送目录 |
| --- | --- |
| 物理属性预测同学 | `distribution/physical_property_human_review_pack_CN.zip` |
| 室内 3D 同学 | `distribution/indoor3d_human_review_pack_CN.zip` |
| IAD 同学 | `distribution/iad_human_review_pack_CN.zip` |

三人都要同时收到 `HUMAN_BLIND_REVIEW_INSTRUCTIONS_CN.md`。

绝对不要发送：

```text
private_human_answer_key.jsonl
任何 LLM review result
任何 method 名称映射
```

评审过程中不要解释哪个版本是本系统，也不要在某人提交前透露其他人的选择。收回三个已完成 XLSX 后，先原样备份，再运行后续汇总脚本。
