# 项目恢复记忆：比赛归档与 AAAI-27 冲刺

更新时间：2026-07-14

## 当前目标切换

当前主目标暂时从“挑战杯比赛材料”切换为“AAAI-27 Main Technical Track 投稿”。

AAAI-27 截止时间（AoE）：

- 摘要：2026-07-21
- 全文：2026-07-28
- 补充材料与代码：2026-07-31

论文暂定标题：

> Evidence-Grounded and Repairable Research Ideation: A Cross-Task Workflow with Blind Evaluation and Execution Feedback

核心研究问题：在控制基础模型、任务、论文证据池和生成预算后，结构化证据约束、机制一致性修复与执行反馈能否稳定提高科研 idea 的具体性、可验证性和实现就绪度？

## 不能遗忘的项目定位

项目不是一个 IAD/CV 单点算法，也不是从五个任务中选择唯一比赛方向。五个方向是 workflow benchmark 样本。当前完整验证三个样本：01 Physical Property、03 Indoor3D、05 IAD；02 Human Motion 和 04 3D Reconstruction 暂为 held-out。

主流程：

```text
task input → paper evidence → baseline weakness → focused ideas
→ experiment plan → blind multi-LLM review → targeted repair
→ re-evaluation → reference claim verification → final research plan
→ real-data execution feedback → execution-layer diagnosis/repair
```

必须诚实披露：

- Si et al.-style 只迁移盲评协议，不是复现 100+ 人类研究者实验。
- Indoor3D 使用 seeded evidence bank。
- IAD 是 lightweight execution-feedback case，不是 PatchCore/anomalib 或 IAD SOTA。
- Physical 的 Si-style repair 曾失败；later v2 才得到 18/18 after wins。
- 不能宣称 idea generation 全球 SOTA，也不能说五任务全部完成。

## 比赛材料恢复点

比赛主线报告位于 `competition_submission/`。核心入口：

- `FINAL_WORKFLOW_END_TO_END_CLOSING_REPORT_CN.md`
- `COMPETITION_DELIVERABLES_INDEX_CN.md`
- `COMPETITION_DELIVERABLES_INDEX_CN.docx`
- `V09_IDEA_GENERATION_CORE_BENCHMARK_REPORT_CN.md`
- `V10_FINAL_RESEARCH_PLAN_PACKAGE_CN.md`
- `V18_IAD_EXECUTION_FEEDBACK_REPAIR_CASE_CN.md`

完整冻结快照位于 `competition_archive/competition_full_snapshot_20260714.tar.gz`，包含比赛报告、脚本、IAD 产物和 `outputs/` 中的原始评审/证据输出；对应 SHA-256 校验文件位于同目录。轻量快照 `competition_snapshot_20260714.tar.gz` 不含顶层 `outputs/`，便于快速传输。AAAI 阶段不要覆盖或改写这些快照。

## AAAI 工作入口

- 投稿差距审计：`competition_submission/AAAI27_SUBMISSION_READINESS_AUDIT_CN.md`
- 实验协议：`aaai27/experiments/EXPERIMENT_PROTOCOL.md`
- 实验配置：`aaai27/experiments/experiment_protocol.yaml`
- 主实验 manifest：`aaai27/experiments/manifests/main_experiment_manifest.jsonl`
- Smoke 操作指南：`aaai27/experiments/SMOKE_TEST_GUIDE_CN.md`
- 统一生成驱动器：`aaai27/experiments/scripts/run_generation_smoke_test.py`
- 论文工程：`aaai27/paper/`

## 最新实验状态（2026-07-14）

- generation protocol 已升级并冻结为 `aaai27_focused_workflow_v3_paired_refinement`。
- 统一模型/provider：`gpt-5.5` via Estelle `/v1/chat/completions`。
- Physical replicate-11 五方法 smoke test：5/5 success、0 failed。
- generic refine 与 targeted repair 共享同一 `focused_no_repair` 初始 ideas，SHA-256 均为 `662bfa6909a0df543ce1e90cd6a1a9da0ff37fa6442f19eeba89b7fcef704a88`。
- Physical pipeline tokens：direct 12400；ResearchArena-style 13015；focused no repair 12369；generic refine 27041；full repair 27722。
- v1/v2 smoke 仅为协议诊断，不进入论文主结果；正式跨任务设置从 v3 开始。
- 下一步：用同一 v3 配对设置依次运行 Indoor3D replicate-11 和 IAD replicate-11，禁止据结果修改 prompt。
- Indoor3D replicate-11 已完成：5/5 success；共享 SHA-256=`524400130a283770f9fde9dfd6535825e86b213eaa95f65e03b5c4223042af86`；generic/full tokens=23429/24186；全部标记 `seeded_disclosed`。先前 503/524 归类为 provider outage。
- IAD replicate-11 已完成：5/5 success；共享 SHA-256=`004abd7b9a3b566817f3da6935445bc848082c41ab572c3152ed6e78d4cf4eef`；generic/full tokens=25074/25913；全部标记 `retrieved`。
- 三任务 seed=11 五方法 generation smoke 已全部通过。
- 已生成 seed=11 统一匿名 review pack：`aaai27/experiments/results/derived/review_pack_seed11_v1/`，共 24 个 review items。public 文件已检查无方法名泄漏；真实方法映射只在 `private_answer_key.jsonl`。
- seed=11 review smoke 已通过：`aaai27/experiments/results/derived/review_smoke_seed11_v1/`，4/4 reviewer JSON 成功落盘。该结果只验证评审格式与盲评包可用性，不作为论文结论。
- `aaai27/experiments/scripts/run_generation_smoke_test.py` 已扩展支持 `--replicate-id` 和 `--all-replicates`；默认仍只跑 seed=11，避免误触发全部主实验。
- Replicate 23 主生成实验已完成：`aaai27/experiments/results/raw/main_protocol_v3_s23/`，15/15 success，0 failed，0 retry。配对 SHA：Physical=`e2393577c68e72b43c8bb5312c4da76d60ef2d10fecce767bdfebdaf9d561556`；Indoor3D=`95147ec106da9b58a90d63786853f18bee665baf41b59b663b3a8c3bd5e22cfd`；IAD=`92c438fb7b69636b7515e6aab0a7a39113f3db887abc0b439898234e4dc2c514`。审计文件：`aaai27/experiments/MAIN_PROTOCOL_V3_S23_AUDIT.md`。
- Replicates 37/53/71 主生成实验已完成。主生成总计 75/75 success，0 failed，0 missing，0 retry；所有 15 个 task-replicate 的 generic/full 配对 SHA 均一致。总审计文件：`aaai27/experiments/MAIN_PROTOCOL_V3_GENERATION_AUDIT.md`。
- 已生成全量匿名 review pack：`aaai27/experiments/results/derived/review_pack_main_v3_all_v1/`，共 120 个 review items、120 条 private answer key、240 条 candidate length stats。public 文件已检查无方法名泄漏。
- 第一个 full reviewer `gpt55_full_reviewer_v1` 曾在 32/120 时遇到 TLS/SSL EOF 网络中断；resume 后已恢复并补到 33/120。当前结果文件：`aaai27/experiments/results/derived/full_review_main_v3_reviewer_gpt55_v1/review_results.jsonl`，raw reviews 在同目录 `raw_reviews/`。这不是内容/格式错误。
- `aaai27/experiments/scripts/run_review_smoke_test.py` 已增加 resume 和连接错误 retry：重跑同一命令会从已有 raw reviews 恢复，不重复调用已完成的 32 个 item；以后每完成一个 item 都会立即刷新 `review_results.jsonl` 和 summary。
- 当前下一步：重跑同一个 full reviewer 命令，继续完成剩余 87 个 review items；脚本会跳过已经在 `review_results.jsonl` 中的 33 个 item。

## 如果新会话丢失上下文

用户可在新会话中说：

> 请完整读取根目录 PROJECT_MEMORY_AAAI27.md，并继续 AAAI-27 投稿冲刺；不要修改 competition_archive 中的比赛快照。

Codex 应先读取本文件，再读取 AAAI 实验协议与投稿审计，之后检查最新实验状态。若当前对话出现明显上下文遗失，请主动告诉用户重新开会话并粘贴上述句子。
