# 三分钟交互 Demo 视频脚本

目标：让评委看到这是一个从“科研任务输入”到“实验复现、结果改进、论文草稿”的完整 AI4S 科研智能体。

Demo 网页：

```text
demo_assets/AI4S_RESEARCH_AGENT_DEMO.html
```

## 0:00-0:20 打开系统

画面：打开交互 demo 首页，展示左侧输入区和右侧竖向 workflow。

解说：

```text
这是我们的 AI4S Research Agent。用户输入具体任务类型和研究方向后，系统会沿着完整科研流程运行：论文证据、baseline 分析、idea 生成、实验计划、自动评审、修复、证据核查、实验复现、结果改进和论文草稿。
```

## 0:20-0:40 输入科研任务

画面：填写：

```text
具体任务类型：工业异常检测 IAD + Agent
研究方向：工业异常检测中的可信科研智能体
```

然后点击：

```text
启动智能体
```

解说：

```text
这里我选择工业异常检测任务。系统会根据任务类型和研究方向生成完整的结构化科研 workflow。
```

## 0:40-1:25 展示 idea generation 前半段

画面：右侧竖向流程依次完成：

```text
1. 论文证据检索
2. 生成 baseline cards
3. 生成 idea
4. 生成实验计划
```

解说：

```text
系统不是直接自由生成 idea，而是先整理论文证据，再分析 baseline 缺陷。例如 IAD 中 PatchCore、PaDiM 等方法对 reference shift、normal bank 污染和报告证据绑定比较敏感。基于这些缺陷，系统生成 focused idea，并进一步生成包含数据集、指标、负对照和成功阈值的实验计划。
```

## 1:25-2:05 展示评审、修复和证据核查

画面：继续显示：

```text
5. 自动评分
6. multi-LLM judge
7. critic repair + 再次盲评
8. 论文证据核查
```

解说：

```text
系统会自动检查方案的机制具体性、实验严谨性、执行就绪度和证据绑定。随后用匿名 multi-LLM judge 判断修复后的方案是否更好。如果发现问题，就进入 critic repair，并再次评审。最后用 reference claim verification 检查 baseline weakness 和 proposed mechanism 是否有论文证据支持。
```

## 2:05-2:45 展示实验复现、结果改进和论文草稿

画面：继续显示：

```text
9. 最终候选 idea + 实验计划
10. 实验复现与运行
11. 根据实验结果诊断与改进
12. 根据实验结果撰写论文草稿
```

解说：

```text
完整 workflow 不停在 idea，而是根据 idea 的方案和计划继续运行实验。以 IAD 为例，系统在三类别 smoke test 中发现全局阈值迁移失败，FPR 达到 0.574257；随后自动做类别感知阈值校准，将 FPR 降到 0.009901。实验结果会反过来驱动方案改进，最后再基于实验结果和证据核查状态生成论文草稿。
```

## 2:45-3:00 收尾

画面：停留在第 12 步论文草稿卡片和“下载完整 workflow JSON”按钮。

解说：

```text
这就是我们的核心贡献：把科研 idea generation 扩展成可评审、可修复、可执行、可写作的 AI4S 科研自动化 workflow。
```

## 启动命令

在服务器终端运行：

```bash
cd /data1/huangyuling/-A_HYL/AI4S/ResearchArena-main
python competition_final_submission_20260725/03_demo_video/demo_assets/start_demo_server.py --port 8899
```

浏览器打开：

```text
http://127.0.0.1:8899/AI4S_RESEARCH_AGENT_DEMO.html
```

如果用 VS Code Remote 或 SSH，需要转发远程端口 `8899`。

## 视频文件要求

```text
时长 <= 3 分钟
格式：mp4
文件名建议：AI4S_ResearchAgent_Demo_3min.mp4
```
