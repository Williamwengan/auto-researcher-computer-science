# Demo 页面打开说明

Demo 页面文件：

```text
competition_final_submission_20260725/03_demo_video/demo_assets/AI4S_RESEARCH_AGENT_DEMO.html
```

如果你是在服务器上跑项目，不能直接把服务器文件路径复制到本地浏览器里打开。推荐用下面方式启动一个本地网页服务。

## 方式一：服务器终端启动

在服务器终端运行：

```bash
cd /data1/huangyuling/-A_HYL/AI4S/ResearchArena-main
python competition_final_submission_20260725/03_demo_video/demo_assets/start_demo_server.py
```

终端看到下面内容说明启动成功：

```text
Demo server running: http://127.0.0.1:8765/AI4S_RESEARCH_AGENT_DEMO.html
```

然后打开浏览器：

```text
http://127.0.0.1:8765/AI4S_RESEARCH_AGENT_DEMO.html
```

## 方式二：VS Code Remote

如果你用 VS Code Remote 连接服务器：

1. 先在服务器终端运行上面的 `python .../start_demo_server.py`。
2. 打开 VS Code 的 `Ports` 面板。
3. 转发远程端口 `8765`。
4. 在本地浏览器打开 VS Code 给出的 forwarded URL，或打开：

```text
http://127.0.0.1:8765/AI4S_RESEARCH_AGENT_DEMO.html
```

## 方式三：SSH 手动端口转发

如果你用 SSH：

```bash
ssh -L 8765:127.0.0.1:8765 huangyuling@你的服务器地址
```

登录后再运行：

```bash
cd /data1/huangyuling/-A_HYL/AI4S/ResearchArena-main
python competition_final_submission_20260725/03_demo_video/demo_assets/start_demo_server.py
```

然后在本地浏览器打开：

```text
http://127.0.0.1:8765/AI4S_RESEARCH_AGENT_DEMO.html
```

## 交互 demo 录屏建议

三分钟视频建议只录这个网页，按交互式软件使用方式展示：

1. 在“研究方向”里输入一个科研方向。
2. 在“具体任务类型”里选择任务，例如“工业异常检测 IAD + Agent”。
3. 点击“启动智能体”。
4. 让系统自动依次展示：
   - baseline cards
   - focused idea
   - 自动评分
   - multi-LLM judge
   - critic repair
   - 最终候选 idea + 实验计划
5. 最后展示“下载本次结果 JSON”按钮，说明系统可以输出结构化结果。

推荐录屏主任务：

```text
研究方向：工业异常检测中的可信科研智能体
具体任务类型：工业异常检测 IAD + Agent
```

如果时间够，可以快速切换一次“物理属性预测”，展示该系统不是只服务一个任务。

视频文件建议命名：

```text
AI4S_ResearchAgent_Demo_3min.mp4
```
