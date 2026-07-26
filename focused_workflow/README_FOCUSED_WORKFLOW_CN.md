# Focused Workflow v0.2 中文说明

## 1. 这个 workflow 是什么

Focused Workflow v0.2 是在 ResearchArena baseline 之外新增的一套科研 idea 生成流程。它的目标不是替代完整 ResearchArena，而是专门改进 **idea generation** 阶段，让输出更聚焦、更细粒度、更容易评价。

原始 ResearchArena 通常输入一个宽泛 seed，例如：

```text
computer vision
```

Focused Workflow 改成结构化输入：

```text
方向 + 具体任务 + 任务类型 + baseline + 约束 + 评价指标
```

当前默认任务是：

```text
2D 室内场景图像中的物体级物理属性预测
```

目标属性包括：

```text
density
Young's modulus
Poisson's ratio
hardness
friction coefficient
```

## 2. 输入和输出

### 输入

核心输入文件：

```text
focused_workflow/tasks/task_spec.yaml
```

它定义：

```text
研究方向
具体任务
候选 baseline
目标属性
评价指标
计算和数据约束
idea 输出要求
```

Prompt 模板：

```text
focused_workflow/prompts/focused_ideation_prompt.md
```

最终渲染后的 prompt：

```text
focused_workflow/prompts/rendered_focused_ideation_prompt.md
```

### 输出

每次运行会创建一个新的输出目录，例如：

```text
outputs/focused_workflow_v0_2_20260710_103708
```

其中核心文件是：

```text
baseline_cards.jsonl
focused_ideas.json
experiment_plan.json
prompt.md
task_spec.yaml
```

含义如下：

| 文件 | 含义 |
|---|---|
| `baseline_cards.jsonl` | 每一行是一个 baseline card，记录 baseline 任务、输入输出、指标、局限和可复用部分 |
| `focused_ideas.json` | 结构化候选 idea 列表 |
| `experiment_plan.json` | 每个 idea 对应的实验计划 |
| `prompt.md` | 本次实际交给 Codex 执行的 prompt |
| `task_spec.yaml` | 本次使用的任务配置副本 |

## 3. 一键运行

先进入 ResearchArena 项目：

```bash
cd /data1/huangyuling/-A_HYL/ResearchArena-main
```

确认 Estelle/Codex 环境可用：

```bash
source ~/.estelle_api_env
echo ${#ESTELLE_API_KEY}
echo $CODEX_HOME
which codex
```

运行：

```bash
bash focused_workflow/scripts/run_focused_workflow_v0_2.sh
```

脚本会自动完成：

```text
1. 渲染 prompt
2. 创建新的 RUN_DIR
3. 复制 prompt 和 task_spec
4. 调用 Codex 生成 baseline_cards.jsonl、focused_ideas.json、experiment_plan.json
5. 检查 JSON 是否可解析
6. 转成 Si et al. 风格 review-ready idea
7. 生成 si2025_manual_review_sheet.json
```

运行结束后，终端会打印本次输出目录。

## 4. Si et al. 2025 风格 benchmark

我们参考论文：

```text
Si et al., 2025, Can LLMs Generate Novel Research Ideas?
```

评价维度包括：

```text
Novelty
Feasibility
Expected Effectiveness
Excitement
Overall
```

评分标准文件：

```text
focused_workflow/evaluation/si2025_review_rubric.yaml
```

评审说明：

```text
focused_workflow/evaluation/si2025_reviewer_instruction.md
```

一键脚本会生成：

```text
review_ready_ideas/idea_01.md
review_ready_ideas/idea_02.md
review_ready_ideas/idea_03.md
si2025_manual_review_sheet.json
```

其中 `review_ready_ideas/*.md` 是统一格式的 proposal，便于人工或 LLM reviewer 评审。

## 5. 人工评审与汇总

复制一份人工评审文件：

```bash
cp "$RUN_DIR/si2025_manual_review_sheet.json" "$RUN_DIR/si2025_review_reviewer01.json"
nano "$RUN_DIR/si2025_review_reviewer01.json"
```

填写每个 idea 的：

```text
novelty_score
feasibility_score
expected_effectiveness_score
excitement_score
overall_score
```

以及对应 rationale。

填写完成后汇总：

```bash
python focused_workflow/scripts/summarize_si2025_reviews.py "$RUN_DIR"
```

会生成：

```text
si2025_review_summary.json
si2025_review_summary.md
```

## 6. LLM-as-a-judge 自动预评分

除了人工评审，也可以用 LLM 做快速预评分。这个结果不能完全替代专家评审，但适合快速筛选 idea。

先生成 reviewer prompt，不调用 API：

```bash
python focused_workflow/scripts/score_ideas_si2025_llm.py "$RUN_DIR" --dry-run
```

会生成：

```text
si2025_llm_reviewer_prompt.rendered.md
si2025_llm_reviewer_ideas.json
```

确认 prompt 没问题后，调用 Codex/Estelle 自动评分：

```bash
source ~/.estelle_api_env
python focused_workflow/scripts/score_ideas_si2025_llm.py "$RUN_DIR"
```

输出：

```text
si2025_review_llm_reviewer01.json
```

然后可以和人工评审一样汇总：

```bash
python focused_workflow/scripts/summarize_si2025_reviews.py "$RUN_DIR"
```

## 7. 和 ResearchArena baseline 对比

原始 ResearchArena 同方向 baseline 输出目录示例：

```text
outputs/researcharena_baseline_physical_property_20260710_085650/idea_01
```

将 baseline 转成同一评审格式：

```bash
BASELINE_DIR=/data1/huangyuling/-A_HYL/ResearchArena-main/outputs/researcharena_baseline_physical_property_20260710_085650/idea_01
COMPARE_DIR=/data1/huangyuling/-A_HYL/ResearchArena-main/outputs/si2025_comparison_physical_property_20260710

mkdir -p "$COMPARE_DIR/review_ready_baseline"

python focused_workflow/scripts/format_researcharena_baseline_for_review.py \
  "$BASELINE_DIR" \
  "$COMPARE_DIR/review_ready_baseline"
```

这样可以把 ResearchArena baseline 和 Focused Workflow 的 idea 放到同一个 Si et al. rubric 下比较。

当前已有对比结果示例：

```text
outputs/si2025_comparison_physical_property_20260710/si2025_comparison_summary.md
```

## 8. 小型 CV benchmark 批量运行

当前已经准备了 5 个 CV benchmark task spec：

```text
focused_workflow/tasks/benchmark_cv/
```

先 dry-run 检查将要运行哪些任务，不调用 API：

```bash
bash focused_workflow/scripts/run_benchmark_cv_tasks.sh --dry-run
```

只运行其中一个任务：

```bash
bash focused_workflow/scripts/run_benchmark_cv_tasks.sh \
  --only 02_open_vocabulary_segmentation.yaml
```

真正批量运行 5 个任务：

```bash
source ~/.estelle_api_env
bash focused_workflow/scripts/run_benchmark_cv_tasks.sh
```

注意：真正批量运行会调用 5 次 Codex/Estelle API，可能消耗较多 token。

批量运行完成后汇总：

```bash
python focused_workflow/scripts/summarize_benchmark_cv_runs.py \
  outputs/benchmark_cv_runs_YYYYMMDD_HHMMSS
```

会生成：

```text
benchmark_summary.json
benchmark_summary.md
```

## 9. 当前结论

目前一次测试中的结论是：

```text
ResearchArena baseline 能生成强单点 idea，但输出形态偏长 proposal。
Focused Workflow 的优势不是保证最高分单 idea 一定超过 baseline，
而是把 idea generation 改造成结构化、多候选、baseline-grounded、可评审、可排序的流程。
```

更适合比赛展示的表述：

```text
我们基于 ResearchArena 的科研自动化思想，在 idea generation 阶段加入结构化 task spec、baseline cards、固定输出 schema、Si et al. 风格评审和排序机制，使科研 idea 生成更聚焦、更细粒度、更鲁棒、更便于团队筛选与分工。
```

## 10. 下一步

建议优先做：

```text
1. 选择 1-2 个 benchmark task 真实运行，避免一次性消耗太多 API
2. 汇总不同任务的输出成功率、idea 数量、baseline 数量、schema pass 情况
3. 做前端检索页面，支持按 baseline、任务类型、指标、风险和评分筛选 idea
4. 准备比赛展示材料：ResearchArena baseline vs Focused Workflow v0.2
```
