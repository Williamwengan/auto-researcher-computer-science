# 7月25日最终收尾清单

截止时间：2026年7月26日。

今天不再新增大实验，目标是把作品打磨成可提交、可演示、可解释的智能体系统。

## 必做 1：确认提交包

```bash
cd /data1/huangyuling/-A_HYL/AI4S/ResearchArena-main
find competition_final_submission_20260725 -maxdepth 3 -type f | sort
```

必须包含：

```text
01_design_doc/AI4S_AGENT_DETAILED_DESIGN_CN.docx
02_deployment/DEPLOYMENT_AND_API_GUIDE_CN.docx
03_demo_video/THREE_MINUTE_DEMO_SCRIPT_CN.docx
03_demo_video/demo_assets/AI4S_RESEARCH_AGENT_DEMO.html
04_code_package/competition_github_release_20260724.tar.gz
05_evidence_appendix/V24_AUTHORIZED_EXPERIMENT_EXECUTOR_CN.docx
06_execution_runs/v24_authorized_iad_executor/EXPERIMENT_AUTHORIZATION_REQUEST.md
```

## 必做 2：打开 demo 页面录屏

如果在本地电脑录屏，建议用浏览器打开：

```text
competition_final_submission_20260725/03_demo_video/demo_assets/AI4S_RESEARCH_AGENT_DEMO.html
```

录屏顺序：

1. demo 首页：讲项目一句话定位和四个评分维度对齐；
2. 展示 `V20_COMPETITION_SCORECARD_AND_DEMO_CN.md`；
3. 展示 `V10_FINAL_RESEARCH_PLAN_PACKAGE_CN.md`；
4. 展示 `V24_AUTHORIZED_EXPERIMENT_EXECUTOR_CN.md`，强调“人工授权后才执行实验”；
5. 展示 `V18_IAD_EXECUTION_FEEDBACK_REPAIR_CASE_CN.md`；
6. 回到 demo 首页总结。

## 必做 3：视频放入提交包

```bash
cp /你的路径/AI4S_ResearchAgent_Demo_3min.mp4 \
  competition_final_submission_20260725/03_demo_video/AI4S_ResearchAgent_Demo_3min.mp4
```

检查：

```bash
ls -lh competition_final_submission_20260725/03_demo_video/AI4S_ResearchAgent_Demo_3min.mp4
```

如果有 `ffprobe`：

```bash
ffprobe -v error \
  -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 \
  competition_final_submission_20260725/03_demo_video/AI4S_ResearchAgent_Demo_3min.mp4
```

## 必做 4：安全扫描

提交前请检查压缩包内不要包含私有答案、密钥、原始数据集、大型缓存或不希望公开的项目记录。当前我已经对现有提交包做过扫描，未发现这些内容。

## 必做 5：最终打包

```bash
tar -czf competition_final_submission_20260725_FINAL.tar.gz \
  competition_final_submission_20260725

ls -lh competition_final_submission_20260725_FINAL.tar.gz
sha256sum competition_final_submission_20260725_FINAL.tar.gz
```

## 提交邮件建议

主题：

```text
2026深圳大学AI4S智能体创新大赛作品提交 - ResearchArena-Focused AI Research Agent
```

正文：

```text
老师您好，

附件为我们的参赛作品提交包：ResearchArena-Focused AI Research Agent。

作品面向 AI for Science 科研发现场景，构建了从科研任务输入、论文证据检索、baseline缺陷分析、细粒度idea生成、实验计划、多模型盲评、targeted repair、reference claim verification 到 IAD真实数据执行反馈的自动化智能体工作流。

提交包内包含：
1. 智能体详细设计文档；
2. Docker/本地部署及调用说明；
3. 三分钟演示视频；
4. 代码包；
5. 证据附录。

谢谢！
```
