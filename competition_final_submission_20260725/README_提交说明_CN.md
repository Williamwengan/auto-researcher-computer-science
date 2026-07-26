# 2026 深圳大学 AI4S 智能体创新大赛提交包

项目名称：

```text
ResearchArena-Focused AI Research Agent
```

一句话简介：

```text
一个面向 AI for Science 科研选题、方案设计与实验执行的自动化智能体：输入科研任务后，自动检索论文、分析 baseline 缺陷、生成细粒度 idea、生成实验计划、多模型盲评、自动修复、核查论文证据，并在 IAD 方向接入真实数据、baseline reproduction 和人工授权实验执行器，形成从 idea 到 execution feedback 的闭环。
```

## 提交材料对应关系

| 比赛要求 | 本提交包路径 |
| --- | --- |
| 智能体详细设计文档 | `01_design_doc/AI4S_AGENT_DETAILED_DESIGN_CN.md` |
| Docker 镜像部署包或远程调用接口说明 | `02_deployment/DEPLOYMENT_AND_API_GUIDE_CN.md` |
| 三分钟以内演示视频 | `03_demo_video/THREE_MINUTE_DEMO_SCRIPT_CN.md` |
| 代码包 | `04_code_package/competition_github_release_20260724.tar.gz` |
| 证据附录 | `05_evidence_appendix/` |

## 评分维度对齐

| 评分维度 | 权重 | 我们的对应亮点 |
| --- | ---: | --- |
| 科学与应用价值 | 30% | 面向科研 idea generation 与实验方案设计，覆盖 IAD、物理属性预测、室内 3D 场景生成三个 AI4S/CV 科研任务。 |
| 技术深度 | 30% | evidence-grounded ideation、targeted repair、multi-LLM blind review、reference claim verification、execution-feedback repair、authorized experiment executor。 |
| 技术落地性 | 20% | 已有可运行脚本、schema、报告生成链路；IAD 接入 MVTec AD smoke test，并支持人工授权后自动复现 baseline / 运行 agent / 汇总指标。 |
| 演示效果 | 20% | 三分钟展示从任务输入到最终研究方案、授权实验执行和 IAD 执行反馈的完整闭环。 |

## 关键能力：网页 workflow + 授权实验执行

为了避免系统只停留在 idea generation，本提交包提供了网页端 workflow 和授权实验执行入口：

```text
03_demo_video/demo_assets/AI4S_RESEARCH_AGENT_DEMO.html
03_demo_video/demo_assets/start_demo_server.py
02_deployment/DEPLOYMENT_AND_API_GUIDE_CN.md
```

网页 demo 支持用户输入“研究方向 + 具体想做的任务 + 任务类型（增量改进 / 指标提升 / 工程拼接 / 评价协议 / 系统优化）”，系统输出详细 idea 解释、相关 baseline、改进点、论文证据和实验方案计划。

进入实验阶段后，页面会要求用户确认数据集路径、模型接口配置和是否授权执行。网页本身不执行用户输入的任意命令，而是请求本地 `start_demo_server.py` 调用固定 allowlist runner；当前真实可执行 runner 已接入 IAD scaffold，陌生方向会生成任务级 runner scaffold 和执行计划，不伪造未运行实验结果。
