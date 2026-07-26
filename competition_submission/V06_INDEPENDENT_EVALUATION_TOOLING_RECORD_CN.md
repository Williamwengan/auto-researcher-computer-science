# v0.6 Independent Evaluation Tooling 阶段记录

## 1. 为什么进入 v0.6

v0.5 targeted repair 后，规则评分显著提升：

```text
IAD: 78.3 -> 89.5
Physical Property: 78.3 -> 94.7
```

但这不能直接证明 idea 真的变强，因为本地 repair 脚本和规则评分器可能共享偏好：

```text
数字阈值
MVP 字段
negative control
implementation files
```

因此 v0.6 的目标不是继续写比赛文档，而是建立独立评估工具，验证 repair 后 idea 是否在盲评中真的胜出。

## 2. 新增工具

### 2.1 匿名 A/B 盲评包生成

```text
focused_workflow/scripts/create_blind_ab_review_pack.py
```

功能：

- 输入 before run 和 after run；
- 随机把 before/after 分配为 Version A / Version B；
- 生成 reviewer 可看的 pair markdown；
- 生成 reviewer 填写用的 `blind_review_sheet.json`；
- 生成私有答案文件 `answer_key_private.json`；
- 不在 reviewer 文件中暴露 before/after 标签。

### 2.2 匿名 A/B 盲评统计

```text
focused_workflow/scripts/summarize_blind_ab_reviews.py
```

功能：

- 读取 reviewer 填好的 JSON；
- 读取私有 answer key；
- 统计 after win rate、before win rate、tie rate；
- 统计各维度 after-before 平均差；
- 统计 pair-level reviewer agreement；
- 输出 `blind_ab_summary_CN.md` 和 `blind_ab_summary.json`。

## 3. 已生成的盲评包

### 3.1 IAD

```text
outputs/v06_blind_ab_review_iad_20260712_105111
```

包含：

```text
README_REVIEW_CN.md
blind_review_sheet.json
answer_key_private.json
pairs/iad_pair_01.md
pairs/iad_pair_02.md
pairs/iad_pair_03.md
```

注意：

```text
answer_key_private.json 不给 reviewer 看。
```

### 3.2 Physical Property

```text
outputs/v06_blind_ab_review_physical_property_20260712_105111
```

包含：

```text
README_REVIEW_CN.md
blind_review_sheet.json
answer_key_private.json
pairs/physical_property_pair_01.md
pairs/physical_property_pair_02.md
pairs/physical_property_pair_03.md
```

## 4. Reviewer 需要做什么

复制 review sheet：

```bash
cp outputs/v06_blind_ab_review_iad_20260712_105111/blind_review_sheet.json \
   outputs/v06_blind_ab_review_iad_20260712_105111/blind_review_reviewer01.json

cp outputs/v06_blind_ab_review_physical_property_20260712_105111/blind_review_sheet.json \
   outputs/v06_blind_ab_review_physical_property_20260712_105111/blind_review_reviewer01.json
```

然后 reviewer 阅读 `pairs/*.md`，填写：

```text
preferred: A / B / tie
preference_strength: 1-3
preference_rationale
scores.A / scores.B
implementation_concerns
```

评分维度：

```text
novelty
feasibility
expected_effectiveness
experimental_rigor
baseline_grounding
mechanism_specificity
implementation_readiness
overall
```

## 5. 汇总命令

IAD：

```bash
python focused_workflow/scripts/summarize_blind_ab_reviews.py \
  --answer-key outputs/v06_blind_ab_review_iad_20260712_105111/answer_key_private.json \
  --reviews outputs/v06_blind_ab_review_iad_20260712_105111/blind_review_reviewer01.json
```

Physical Property：

```bash
python focused_workflow/scripts/summarize_blind_ab_reviews.py \
  --answer-key outputs/v06_blind_ab_review_physical_property_20260712_105111/answer_key_private.json \
  --reviews outputs/v06_blind_ab_review_physical_property_20260712_105111/blind_review_reviewer01.json
```

如果有多个 reviewer：

```bash
python focused_workflow/scripts/summarize_blind_ab_reviews.py \
  --answer-key outputs/v06_blind_ab_review_iad_20260712_105111/answer_key_private.json \
  --reviews \
    outputs/v06_blind_ab_review_iad_20260712_105111/blind_review_reviewer01.json \
    outputs/v06_blind_ab_review_iad_20260712_105111/blind_review_reviewer02.json \
    outputs/v06_blind_ab_review_iad_20260712_105111/blind_review_reviewer03.json
```

## 6. 下一步

下一步应该做真实盲评，而不是继续写最终文档。

建议顺序：

```text
1. 人工 reviewer 至少 2-3 人盲评 IAD 和 Physical Property
2. Claude/GPT judge 也可作为额外 reviewer，但不能看 answer_key_private.json
3. 汇总 after win rate、tie rate、dimension delta、reviewer agreement
4. 如果 after 在盲评中不稳定胜出，就回到 repair 逻辑继续改
5. 如果 after 稳定胜出，再进入 evidence claim verification 和多次运行稳定性实验
```

当前阶段只证明：

```text
我们已经具备独立盲评工具。
```

还没有证明：

```text
修复后的 idea 在独立盲评中稳定优于修复前。
```
