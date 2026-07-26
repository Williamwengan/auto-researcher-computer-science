# 比赛提交物清单与当前工作路线

更新时间：2026-07-11 14:52:17

## 必须时刻记住的比赛提交内容

1. **智能体详细设计文档**
   - 智能体目标、输入输出、模块架构、工具调用流程、状态记忆、决策策略、失败处理、人机交互。
   - 当前建议主线：基于 Idea 1 的 Contact-Calibrated Motion Agent。

2. **Docker 镜像部署包或远程调用接口**
   - 至少要有一种可运行交付形式。
   - 建议先做远程调用接口，后续再封装 Docker。
   - 接口建议：`POST /generate_motion`，输入 text prompt，输出 motion 文件、物理评分、failure_warning、可视化路径。

3. **三分钟以内演示视频**
   - 必须完整展示智能体功能及运行全过程。
   - 建议视频流程：输入文本 prompt -> baseline 生成 -> contact verifier 检查脚滑/接触错误 -> guidance 修复 -> 输出评分表和可视化对比。

## 当前推荐主线

优先选择：**Idea 1: Contact-Calibrated Diffusion Guidance for Text-to-Motion**

原因：

- 最容易做 MVP。
- 指标明确：foot_sliding_rate、ground_contact_error、FID、R-precision。
- 演示直观：能展示修复前后动作稳定性差异。
- 适合包装成智能体：生成、检查、修复、报告、失败警告。

## 下一步执行顺序

### Step 1：写智能体详细设计文档

输出文件建议：

`competition_submission/AGENT_DESIGN_DOC_CN.md`

必须包含：

- Agent 名称：Contact-Calibrated Motion Agent
- 输入：text prompt / action label / optional floor height
- 输出：motion sequence、physical plausibility score、failure_warning、可视化图/视频
- 模块：baseline generator、contact verifier、contact guidance energy、failure warning、report writer
- 状态：candidate motions、contact intervals、energy scores、failed frames、selected output
- 决策策略：accept / repair / resample / warn

### Step 2：确定接口形式

输出文件建议：

`competition_submission/API_DEPLOYMENT_GUIDE_CN.md`

建议接口：

```text
POST /generate_motion
```

输入 JSON：

```json
{
  "prompt": "a person walks forward and turns left",
  "num_candidates": 4,
  "enable_contact_guidance": true
}
```

输出 JSON：

```json
{
  "motion_file": "outputs/demo/motion_001.npz",
  "visualization": "outputs/demo/motion_001.mp4",
  "condition_alignment_score": 0.0,
  "physical_plausibility_score": 0.0,
  "foot_sliding_rate": 0.0,
  "ground_contact_error": 0.0,
  "failure_warning": ""
}
```

### Step 3：规划三分钟演示视频

输出文件建议：

`competition_submission/DEMO_VIDEO_SCRIPT_CN.md`

视频结构：

1. 0:00-0:20 展示输入 prompt 和智能体界面/命令。
2. 0:20-0:55 展示 baseline motion 生成。
3. 0:55-1:30 展示 contact verifier 检测 foot sliding / contact error。
4. 1:30-2:15 展示 contact-guided sampling 或修复后结果。
5. 2:15-2:45 展示指标表和前后对比图。
6. 2:45-3:00 总结智能体能力：生成、验证、修复、报告。

## 当前已有支撑材料

- 最新 v0.3 idea 输出：`/data1/huangyuling/-A_HYL/AI4S/ResearchArena-main/outputs/benchmark_cv_runs_20260711_143630/02_human_motion_generation`
- 中文合并版：`/data1/huangyuling/-A_HYL/AI4S/ResearchArena-main/outputs/benchmark_cv_runs_20260711_143630/02_human_motion_generation/review_ready_ideas/IDEAS_MANUAL_REVIEW_CN.md`
- 自动质量评分：`/data1/huangyuling/-A_HYL/AI4S/ResearchArena-main/outputs/benchmark_cv_runs_20260711_143630/02_human_motion_generation/idea_quality_report_CN.md`
- 人工 reviewer 审查：`/data1/huangyuling/-A_HYL/AI4S/ResearchArena-main/outputs/benchmark_cv_runs_20260711_143630/02_human_motion_generation/si2025_human_reviewer01_summary_CN.md`

## 重要原则

从现在开始，所有后续 idea、MVP、代码和文档都必须服务于三件提交物：

```text
智能体设计文档 + 可部署接口/镜像 + 三分钟演示视频
```
