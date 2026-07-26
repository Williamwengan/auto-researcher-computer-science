# V25 Focused Ideas → ResearchArena Pipeline Bridge

生成时间：2026-07-25T15:34:11

## 一句话结论

本步骤把 Focused Workflow 已经筛选出的最终研究方案，转换成 ResearchArena 可以 `--resume` 的实验工作区格式，使系统从“生成好 idea 和实验计划”进入“人工授权后自动跑实验、写论文、评审”的阶段。

## 为什么现在发现了 bridge 问题

之前两段流程各自成立，但文件 schema 不一致：

- Focused Workflow 输出的是比赛友好的 `final research plan`，字段更细：baseline weakness、paper evidence、minimal module、metrics、negative controls 等。
- ResearchArena 执行层期待的是每个 idea workspace 中的 `idea.json + plan.json + proposal.md`。
- 因此唯一阻断点不是算法逻辑，而是字段映射和 workspace 初始化。

这个脚本解决的就是：把 V10 final plan 映射成 ResearchArena resume workspace。

## 生成的工作区

| # | task | source plan | workspace | resume command |
| ---: | --- | --- | --- | --- |
| 1 | 物理属性预测 | `plan_01_physical_property` | `outputs/pipeline_bridge_from_focused_ideas_v1/physical_property/idea_01` | `python -m researcharena.cli run --config configs/default.yaml --resume outputs/pipeline_bridge_from_focused_ideas_v1/physical_property/idea_01` |
| 2 | 室内单图 3D 场景生成 | `plan_03_indoor3d` | `outputs/pipeline_bridge_from_focused_ideas_v1/indoor3d_scene/idea_02` | `python -m researcharena.cli run --config configs/default.yaml --resume outputs/pipeline_bridge_from_focused_ideas_v1/indoor3d_scene/idea_02` |
| 3 | 工业异常检测 IAD + Agent | `plan_05_iad_agent` | `outputs/pipeline_bridge_from_focused_ideas_v1/iad_agent/idea_03` | `python -m researcharena.cli run --config configs/default.yaml --resume outputs/pipeline_bridge_from_focused_ideas_v1/iad_agent/idea_03` |

## 当前安全边界

- 本脚本只写本地文件，不调用 API。
- 本脚本不自动运行 Claude/Codex 实验阶段。
- 真正执行 ResearchArena pipeline 时，需要用户显式授权，并配置相应模型/API。

## 推荐下一步

先在网页 demo 里展示 bridge 已经生成的 workspace；若现场需要演示实验执行，则选择一个轻量任务，例如 IAD scaffold，点击授权后再调用后续执行命令。

## 输入与输出

- Source: `competition_submission/V10_FINAL_RESEARCH_PLAN_PACKAGE.json`
- Output dir: `outputs/pipeline_bridge_from_focused_ideas_v1`
