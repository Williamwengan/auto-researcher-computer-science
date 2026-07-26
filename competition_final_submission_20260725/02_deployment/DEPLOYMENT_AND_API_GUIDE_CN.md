# AI4S Research Agent Docker 部署与远程调用说明

生成日期：2026-07-26

本文档对应比赛提交要求：

```text
Docker 镜像部署包或远程调用接口（含部署及调用说明文档）
```

本项目同时提供两种使用方式：

1. 网页交互 Demo；
2. HTTP 远程调用接口。

评委可以任选一种方式测试。网页适合人工演示；HTTP 接口适合程序化调用和复现实验。

## 1. 提交包结构

提交包根目录：

```text
competition_final_submission_20260725/
```

关键文件：

```text
Dockerfile
.dockerignore
README_提交说明_CN.md
01_design_doc/AI4S_AGENT_DETAILED_DESIGN_CN.md
02_deployment/DEPLOYMENT_AND_API_GUIDE_CN.md
03_demo_video/demo_assets/AI4S_RESEARCH_AGENT_DEMO.html
03_demo_video/demo_assets/start_demo_server.py
focused_workflow/scripts/run_live_workflow_backend_v27.py
research_agent_orchestrator/orchestrator.py
iad_mvp/
generic_mvp/
outputs/
execution_runs/
```

## 2. 推荐方式 A：直接访问远程 Demo

如果服务器已启动，评委可直接打开：

```text
http://172.31.233.6:8902/AI4S_RESEARCH_AGENT_DEMO.html
```

如果浏览器缓存旧页面，可访问：

```text
http://172.31.233.6:8902/AI4S_RESEARCH_AGENT_DEMO.html?v=final_submit
```

网页支持：

- 输入研究方向；
- 输入具体想做的任务；
- 选择任务类型；
- 自动生成候选 idea；
- 展示 baseline、论文证据、改进点和实验计划；
- 进入实验执行对话舱；
- 授权运行 IAD scaffold 或当前任务 smoke runner；
- 输出指标摘要和论文草稿。

## 3. 推荐方式 B：本地启动网页服务

进入提交包目录：

```bash
cd competition_final_submission_20260725
```

启动服务：

```bash
python 03_demo_video/demo_assets/start_demo_server.py \
  --host 127.0.0.1 \
  --port 8902 \
  --strict-port
```

浏览器访问：

```text
http://127.0.0.1:8902/AI4S_RESEARCH_AGENT_DEMO.html
```

如果端口已占用，可换端口：

```bash
python 03_demo_video/demo_assets/start_demo_server.py \
  --host 127.0.0.1 \
  --port 8903 \
  --strict-port
```

然后访问：

```text
http://127.0.0.1:8903/AI4S_RESEARCH_AGENT_DEMO.html
```

## 4. Docker 部署

提交包已包含 `Dockerfile`。

### 4.1 构建镜像

```bash
cd competition_final_submission_20260725
docker build -t ai4s-research-agent:competition .
```

### 4.2 运行容器

```bash
docker run --rm \
  -p 8902:8902 \
  ai4s-research-agent:competition
```

访问：

```text
http://127.0.0.1:8902/AI4S_RESEARCH_AGENT_DEMO.html
```

### 4.3 让局域网或服务器外部访问

如果部署在服务器上：

```bash
docker run --rm \
  -p 8902:8902 \
  ai4s-research-agent:competition
```

访问：

```text
http://服务器IP:8902/AI4S_RESEARCH_AGENT_DEMO.html
```

注意：需要服务器安全组、防火墙或校园网策略允许访问 8902 端口。

### 4.4 导出 Docker 镜像包

如需提交离线镜像包：

```bash
docker save ai4s-research-agent:competition \
  -o ai4s-research-agent_competition.tar
```

评委导入：

```bash
docker load -i ai4s-research-agent_competition.tar
docker run --rm -p 8902:8902 ai4s-research-agent:competition
```

说明：如果评委环境无法访问 Docker Hub，建议优先使用已部署远程网页，或随包提供已 `docker save` 的镜像 tar。

## 5. 环境变量与 API Key

网页的 Phase 2 支持两种 API Key 模式：

| 模式 | 说明 |
| --- | --- |
| 使用服务器内置演示 Key | 由部署者在服务器环境变量中配置，评委无需填写 key |
| 手动填写自己的 Key | 评委可在网页中填写；前端不保存 key |

后端会按以下环境变量顺序读取演示 key：

```text
AI4S_DEMO_API_KEY
ESTELLE_CLAUDE_API_KEY
ESTELLE_API_KEY
YUNWU_API_KEY
```

示例：

```bash
export AI4S_DEMO_API_KEY="your_api_key_here"
python 03_demo_video/demo_assets/start_demo_server.py \
  --host 0.0.0.0 \
  --port 8902 \
  --strict-port
```

提交包中不包含任何真实 API Key。

## 6. HTTP API 调用说明

### 6.1 获取 Demo 配置

```bash
curl http://127.0.0.1:8902/api/demo_config
```

返回字段包括：

```text
ok
server_demo_key_available
project_root
```

### 6.2 启动 live workflow

接口：

```text
POST /api/live_workflow/start
```

示例 1：已验证 IAD 方向

```bash
curl -X POST http://127.0.0.1:8902/api/live_workflow/start \
  -H "Content-Type: application/json" \
  -d '{
    "task_key": "iad",
    "task_type": "工业异常检测 IAD + Agent",
    "research_direction": "工业异常检测中的可信科研智能体",
    "task_mode": "system_optimization"
  }'
```

示例 2：陌生方向

```bash
curl -X POST http://127.0.0.1:8902/api/live_workflow/start \
  -H "Content-Type: application/json" \
  -d '{
    "task_key": "custom",
    "task_type": "多时相遥感图像变化检测中的证据驱动解释智能体",
    "research_direction": "遥感变化检测可信解释",
    "task_mode": "incremental_improvement"
  }'
```

返回示例：

```json
{
  "ok": true,
  "job_id": "live_custom_YYYYMMDD_HHMMSS_xxx",
  "status": "started",
  "task_key": "custom",
  "task_mode": "incremental_improvement",
  "message": "Live workflow backend started. Poll /api/live_workflow/status."
}
```

### 6.3 查询 workflow 状态

接口：

```text
GET /api/live_workflow/status?job_id=<job_id>
```

示例：

```bash
curl "http://127.0.0.1:8902/api/live_workflow/status?job_id=live_custom_YYYYMMDD_HHMMSS_xxx"
```

完成后返回的 JSON 中包含：

```text
result.final_plan.idea_title
result.final_plan.final_idea
result.final_plan.baselines
result.final_plan.baseline_weakness
result.final_plan.improvement_points
result.final_plan.experiment_plan
result.final_plan.datasets
result.final_plan.metrics
result.evidence.papers
result.evidence.paper_count
result.evidence.card_count
result.auto_claude_workspace / 实验工作区
```

说明：字段名中保留了部分历史变量名，但网页展示已统一为“实验工作区/实验代理”。

### 6.4 实验对话接口

接口：

```text
POST /api/aris/chat
```

虽然接口路径保留历史命名，用户界面中展示为“实验代理”。该接口负责：

- 接收用户实验指令；
- 判断是否需要授权；
- 返回授权动作；
- 在用户授权后调用固定 runner；
- 读取指标；
- 生成 result-to-claim 和论文草稿。

示例：

```bash
curl -X POST http://127.0.0.1:8902/api/aris/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "请基于当前 idea 准备实验并运行 smoke test",
    "task_type": "工业异常检测 IAD + Agent",
    "research_direction": "工业异常检测中的可信科研智能体",
    "task_mode": "system_optimization",
    "idea_title": "Evidence-Grounded IAD Research Agent",
    "workspace": "outputs/auto_claude_execution_bridge_v1/iad_agent",
    "dataset_path": "Datasets/01_IAD/mvtec_anomaly_detection/mvtec_anomaly_detection",
    "execution_mode": "sanity",
    "llm_model": "claude-sonnet-4-6",
    "llm_base_url": "https://estellecode.com/v1",
    "api_key_present": true
  }'
```

如果需要执行实验，接口会返回：

```json
{
  "ok": true,
  "action_required": true,
  "action": {
    "type": "run_iad_scaffold",
    "label": "授权执行 IAD scaffold"
  }
}
```

网页端会显示授权按钮。用户点击授权后，前端会再次调用该接口并携带 `authorized_action`。

### 6.5 准备实验入口

接口：

```text
POST /api/aris/prepare
```

该接口会根据当前 idea 和实验计划生成实验工作区、配置和接管提示词。它适合用于检查实验准备状态。

### 6.6 固定授权执行接口

接口：

```text
POST /api/execution/authorize
```

该接口只允许固定 IAD scaffold，不执行用户任意命令。

示例：

```bash
curl -X POST http://127.0.0.1:8902/api/execution/authorize \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "工业异常检测 IAD + Agent",
    "research_direction": "工业异常检测中的可信科研智能体",
    "approval_note": "评委授权运行 IAD scaffold smoke test",
    "dataset_path": "Datasets/01_IAD/mvtec_anomaly_detection/mvtec_anomaly_detection",
    "categories": ["bottle"]
  }'
```

## 7. 推荐评测流程

### 7.1 测试已验证方向

网页输入：

```text
研究方向：工业异常检测中的可信科研智能体
具体想做的任务：工业异常检测 IAD + Agent
任务类型：系统优化
```

预期结果：

- 页面展示完整 idea；
- baseline 包含 PatchCore、PaDiM、FastFlow 等；
- evidence summary 非空；
- 可进入实验对话舱；
- 如数据集存在，可运行 IAD scaffold。

### 7.2 测试陌生方向

网页输入：

```text
研究方向：遥感变化检测可信解释
具体想做的任务：多时相遥感图像变化检测中的证据驱动解释智能体
任务类型：增量改进
```

预期结果：

- 系统尝试在线检索论文；
- 生成 baseline cards；
- 生成候选 idea；
- 生成实验计划；
- 生成当前任务 runner scaffold；
- 明确标记 retrieved/unverified 证据。

说明：陌生方向的 runner scaffold 是 workflow smoke test，不等价于该领域完整 benchmark。

## 8. 安全边界

本 demo 的安全设计：

- 不执行用户输入的任意 shell；
- 实验运行通过固定 allowlist runner；
- API Key 不写入日志或报告；
- 下载数据、安装依赖、长时间 GPU 实验需要用户授权；
- 未真实执行的实验不会伪造成结果；
- 陌生方向的检索结果在 verification 前标记为 retrieved/unverified。

## 9. 常见问题

### 9.1 网页打不开

检查服务是否启动：

```bash
curl http://127.0.0.1:8902/AI4S_RESEARCH_AGENT_DEMO.html | head
```

如果端口被占用：

```bash
python 03_demo_video/demo_assets/start_demo_server.py \
  --host 127.0.0.1 \
  --port 8903 \
  --strict-port
```

### 9.2 页面没有变化

使用缓存刷新：

```text
Ctrl + F5
```

或访问：

```text
http://127.0.0.1:8902/AI4S_RESEARCH_AGENT_DEMO.html?v=final_submit
```

### 9.3 Docker 构建失败

如果失败原因是无法访问 Docker Hub 或 pip 源，建议：

- 使用已部署远程 URL；
- 或在有网络环境的机器上构建并 `docker save`；
- 或直接使用本地 Python 启动方式。

### 9.4 陌生方向没有真实实验结果

这是预期行为。陌生方向可以实时生成 workflow 结果和 runner scaffold，但真实 benchmark 需要领域数据、baseline 代码和 metric parser。系统不会伪造这些结果。

## 10. 一句话验收口径

评委可以把本系统理解为：

```text
一个可通过网页和 HTTP API 调用的 AI4S 科研自动化智能体：
它能把用户输入的科研任务转化为 evidence-grounded idea、baseline 对比、实验计划和授权实验入口；
对已验证方向展示完整闭环，对陌生方向生成可继续执行的 workflow scaffold，并诚实标记未验证证据。
```
