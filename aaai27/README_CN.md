# AAAI-27 工作区

本目录只服务 AAAI-27 投稿，不替代 `competition_submission/`，也不修改 `competition_archive/` 的冻结比赛材料。

工作顺序：

1. 冻结并检查 `experiments/experiment_protocol.yaml`。
2. 使用 manifest 运行公平 baseline 与消融。
3. 将原始结果写入 `experiments/results/raw/`，统计表写入 `experiments/results/derived/`。
4. 论文只引用可由 manifest 和脚本复现的 derived 表格。
5. 提交前使用 AAAI-27 官方 Author Kit 替换 `paper/` 中的模板占位文件。

禁止事项：不要手工修改生成后的主结果数字；不要在最终 test labels 上选择阈值；不要把 LLM judge 当作唯一的人类质量证据。
