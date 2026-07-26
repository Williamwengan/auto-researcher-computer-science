# Focused Workflow v0.3 升级说明

## 升级目标

本次升级的目标是解决 idea 仍然偏空泛的问题：过去的 idea 虽然包含 baseline、metrics、ablation 和 failure criteria，但经常缺少可以直接开工的实现粒度，例如：

- 最小新增模块到底是什么？
- 模块输入和输出是什么？
- 算法步骤是什么？
- 训练或推理目标是什么？
- baseline 为什么不能直接做到？
- 1-2 周 MVP 需要哪些脚本、数据文件、表格、图和成功阈值？

因此 v0.3 强制每个 idea 额外输出两个字段：

```json
"minimal_new_module": {
  "name": "",
  "input": "",
  "output": "",
  "algorithm_steps": [],
  "training_or_inference_objective": "",
  "why_baseline_cannot_do_this": ""
}
```

```json
"mvp_artifacts": {
  "required_scripts": [],
  "required_data_files": [],
  "expected_tables": [],
  "expected_figures": [],
  "success_threshold": ""
}
```

## 修改文件

- `focused_workflow/prompts/focused_ideation_prompt.md`
  - 新增 Anti-Shallow 要求：Minimal new module 和 MVP artifacts。
  - 新增 focused_ideas.json 必填字段示例。

- `focused_workflow/schemas/focused_idea.schema.json`
  - 新增 `minimal_new_module` 和 `mvp_artifacts` 的 schema 校验。

- `focused_workflow/scripts/validate_outputs.py`
  - 新增嵌套字段校验。
  - 保留 legacy 兼容：旧 run 的 task_spec.yaml 没有新字段时，仍按旧 schema 校验，不会破坏已生成结果。

- `focused_workflow/scripts/format_ideas_for_review.py`
  - review-ready markdown 中新增 “Minimal New Module” 和 “MVP Artifacts” 两节。

- `focused_workflow/scripts/evaluate_idea_quality.py`
  - 质量评分纳入新字段。
  - 新字段存在时降低粒度惩罚。

- `focused_workflow/tasks/benchmark_cv/*.yaml`
  - 五个 CV benchmark task spec 均加入 `minimal_new_module` 和 `mvp_artifacts`。

## 不覆盖旧结果

本次升级不会修改已有 benchmark 输出目录中的：

- `focused_ideas.json`
- `experiment_plan.json`
- `baseline_cards.jsonl`
- `review_ready_ideas/idea_*.md`

旧结果仍可查看和校验。只有未来重新运行 benchmark 时，才会按 v0.3 schema 生成更细粒度 idea。

## 已完成验证

- `focused_idea.schema.json` 通过 JSON 解析。
- `validate_outputs.py`、`format_ideas_for_review.py`、`evaluate_idea_quality.py` 通过 Python 语法检查。
- 旧 human motion benchmark 在 legacy 兼容模式下仍然 `PASSED`。
- 新渲染 prompt 已包含 `minimal_new_module`、`mvp_artifacts`、`required_scripts` 和 `success_threshold`。

## 下一步建议

选择一个方向重新跑一次，建议先跑最能代表问题的 human motion 或 physical property：

```bash
bash focused_workflow/scripts/run_benchmark_cv_tasks.sh   --only 02_human_motion_generation.yaml
```

为了不覆盖旧结果，脚本会生成新的时间戳目录。跑完后再执行：

```bash
python focused_workflow/scripts/evaluate_idea_quality.py <new_run_dir>
```

然后比较旧版和 v0.3 新版的：

- `idea_quality_score`
- `granularity_penalty`
- `mvp_artifacts_not_precise` 是否消失
- 人工审查是否更容易直接分工实现
