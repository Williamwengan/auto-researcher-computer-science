# Focused Workflow CV Benchmark Tasks

这个目录包含 5 个用于测试 Focused Workflow v0.2 的计算机视觉任务配置。它们的作用是验证：当输入从单一研究方向扩展到多个 CV 子方向时，workflow 是否仍能稳定生成结构化、baseline-grounded、可评审的科研 idea。

## 任务列表

| 文件 | 任务方向 | 主要目标 |
|---|---|---|
| `01_physical_property_prediction.yaml` | 2D 室内场景物体物理属性预测 | 输入单张室内图，输出每个物体的密度、杨氏模量、泊松比、硬度、摩擦系数等 |
| `02_human_motion_generation.yaml` | Human motion 生成 | 从文本、动作、姿态、场景或物体交互条件生成真实、可控、物理合理的人体运动 |
| `03_indoor_scene_generation.yaml` | 单图生成 3D 室内场景 | 从单张室内 RGB 图生成可渲染的 3D 场景、房间布局、物体几何、空间关系和遮挡区域假设 |
| `04_3d_reconstruction.yaml` | 三维重建 | 从单图、稀疏多视角、视频或 RGB-D 中恢复物体/场景 3D 表示 |
| `05_iad_agent_workflow.yaml` | IAD + Agent 流程 | 面向工业异常检测，构建检索、定位、复核、报告和人工升级的 agent 检测流程 |

## 如何运行单个任务

在 ResearchArena 项目根目录运行：

```bash
cd /data1/huangyuling/-A_HYL/ResearchArena-main
source ~/.estelle_api_env

TASK_SPEC=focused_workflow/tasks/benchmark_cv/02_human_motion_generation.yaml \
bash focused_workflow/scripts/run_focused_workflow_v0_2.sh
```

也可以直接使用批量 benchmark 脚本先 dry-run：

```bash
bash focused_workflow/scripts/run_benchmark_cv_tasks.sh --dry-run
```

只运行其中一个方向：

```bash
bash focused_workflow/scripts/run_benchmark_cv_tasks.sh \
  --only 05_iad_agent_workflow.yaml
```

## 每个输出目录应包含

```text
baseline_cards.jsonl
focused_ideas.json
experiment_plan.json
review_ready_ideas/
si2025_manual_review_sheet.json
```

## 评价方式

每个任务都可以接入同一套 Si et al. 2025 风格评价流程：

```bash
python focused_workflow/scripts/score_ideas_si2025_llm.py "$RUN_DIR" --dry-run
python focused_workflow/scripts/summarize_si2025_reviews.py "$RUN_DIR"
```

人工评审时，复制评审表：

```bash
cp "$RUN_DIR/si2025_manual_review_sheet.json" "$RUN_DIR/si2025_review_reviewer01.json"
nano "$RUN_DIR/si2025_review_reviewer01.json"
```

## 比赛展示建议

展示时可以说明：

```text
我们构建了一个小型 CV idea-generation benchmark，不只在单一任务上验证 workflow，而是在物理属性预测、human motion 生成、单图生成 3D 室内场景、三维重建、IAD + Agent 流程五类任务上测试其结构化 idea 生成能力。
```

