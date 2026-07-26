# Bridge Workspace 02: 室内单图 3D 场景生成

这个目录由 `focused_workflow/scripts/run_pipeline_from_focused_ideas.py` 自动生成。

## 已写入文件

- `idea.json`：ResearchArena ideation summary schema
- `plan.json`：ResearchArena experiment plan schema
- `proposal.md`：完整 proposal 文档

## 当前状态

已完成 bridge 初始化；尚未调用 API，尚未跑实验。

## 人工授权后可执行

```bash
python -m researcharena.cli run --config configs/default.yaml --resume outputs/pipeline_bridge_from_focused_ideas_v1/indoor3d_scene/idea_02
```

ResearchArena 会检测到 `idea.json + plan.json + proposal.md` 已存在，因此跳过 ideation，进入 self-review / experiments / paper / review 后续阶段。
