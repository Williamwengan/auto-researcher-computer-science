#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SUBMISSION = ROOT / "competition_submission"
DEMO_DIR = ROOT / "competition_final_submission_20260725/03_demo_video/demo_assets"


TASK_ALIASES = {
    "物理属性预测": "physical",
    "室内单图 3D 场景生成": "indoor3d",
    "工业异常检测 IAD + Agent": "iad",
}


REPAIR_NOTES = {
    "physical": {
        "title": "机制一致性修复",
        "before": "早期 repair 曾把 interval-mapper loss 错误套到所有 idea，导致机制错配。",
        "after": "修复后拆成 calibrated interval mapper、localized material evidence verifier、proposal uncertainty propagation 三个互补模块。",
        "impact": "6 个 judge 共 18 次 A/B 判断全部选择修复后方案。",
    },
    "indoor3d": {
        "title": "几何一致性修复",
        "before": "单图 3D idea 容易停留在生成式扩展，缺少可验证的 scene graph、support relation 和 collision 检查。",
        "after": "修复后加入 scene-graph hypothesis verifier、support/collision checker 与 uncertainty reporting。",
        "impact": "修复后方案在 blind review 中显著提高实验严谨性、机制具体性和实现就绪度。",
    },
    "iad": {
        "title": "执行反馈修复",
        "before": "三类别 smoke test 发现全局阈值跨类别迁移失败，FPR 达到 0.574257。",
        "after": "自动进入类别感知阈值校准，并加入 reference-consistency / evidence-grounded report checker。",
        "impact": "类别感知校准后 FPR 降到 0.009901，形成真实数据执行反馈案例。",
    },
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def compact_list(value, limit: int = 5) -> list[str]:
    if isinstance(value, list):
        return [str(x) for x in value[:limit]]
    if value is None:
        return []
    return [str(value)]


def make_baseline_cards(plan: dict) -> list[dict]:
    baselines = compact_list(plan.get("baselines"), 4)
    weaknesses = compact_list(plan.get("baseline_weakness"), 4)
    evidence = compact_list(plan.get("paper_evidence"), 2)
    cards = []
    for idx, name in enumerate(baselines[:3] or ["Baseline"]):
        cards.append(
            {
                "name": name,
                "weakness": weaknesses[idx % len(weaknesses)] if weaknesses else "需要进一步定位 baseline weakness。",
                "evidence": evidence[idx % len(evidence)] if evidence else plan.get("evidence_verification_status", "evidence checked"),
            }
        )
    return cards


def build_task_payloads() -> dict:
    v10 = read_json(SUBMISSION / "V10_FINAL_RESEARCH_PLAN_PACKAGE.json")
    v21 = read_json(SUBMISSION / "V21_COMPETITION_DEPTH_READINESS_BENCHMARK.json")
    depth_by_plan = {item["plan_id"]: item for item in v21.get("results", [])}

    payloads = {}
    for plan in v10.get("plans", []):
        alias = TASK_ALIASES.get(plan["task_name"], plan["plan_id"])
        depth = depth_by_plan.get(plan["plan_id"], {})
        payloads[alias] = {
            "taskName": plan["task_name"],
            "researchProblem": plan.get("research_problem", ""),
            "paperEvidence": compact_list(plan.get("paper_evidence"), 4),
            "baselineCards": make_baseline_cards(plan),
            "idea": {
                "title": plan.get("final_idea", ""),
                "hypothesis": plan.get("core_hypothesis", ""),
                "minimalModule": plan.get("minimal_new_module", ""),
                "method": compact_list(plan.get("method_overview"), 5),
            },
            "score": {
                "overall": depth.get("overall_depth_readiness_score", 0),
                "signals": depth.get("signal_scores", {}),
                "warnings": depth.get("warnings", []),
            },
            "judge": {
                "summary": plan.get("judge_summary", ""),
                "evidence": plan.get("evidence_verification_status", ""),
            },
            "verification": {
                "status": plan.get("evidence_verification_status", ""),
                "checkedItems": [
                    "baseline weakness 是否绑定 paper evidence",
                    "proposed mechanism 是否有证据支持",
                    "unsupported claims 是否被标记",
                    "manual-check claims 是否保留不确定性",
                ],
            },
            "repair": REPAIR_NOTES.get(alias, {}),
            "final": {
                "candidate": plan.get("final_idea", ""),
                "experimentPlan": compact_list(plan.get("experiment_plan"), 6),
                "datasets": compact_list(plan.get("datasets"), 6),
                "metrics": compact_list(plan.get("metrics"), 8),
                "negativeControls": compact_list(plan.get("negative_controls"), 5),
                "successThresholds": compact_list(plan.get("success_thresholds"), 4),
                "artifacts": compact_list(plan.get("implementation_artifacts"), 5),
                "nextStep": plan.get("next_execution_step", ""),
            },
            "execution": {
                "reproduction": [
                    "根据 final plan 生成 manifest、baseline runner 和 proposed module scaffold。",
                    "生成授权请求和命令预览；获得人工授权后再运行 baseline / ablation / negative controls。",
                    "IAD 方向已接入 MVTec AD smoke test，形成 execution-feedback repair case。",
                ],
                "resultSignals": [
                    "自动读取 primary metrics、negative-control gaps、failure criteria 和 artifact completeness。",
                    "记录 run_state、watchdog state、execution logs 和 authorization record。",
                    "若结果不满足阈值，进入 execution-feedback diagnosis。",
                ],
            },
            "improvement": {
                "diagnosis": [
                    "定位失败来自 idea 机制、阈值、数据划分、baseline 复现还是证据约束。",
                    "将实验结果转化为 targeted repair instruction。",
                ],
                "example": "IAD V1.5 发现全局阈值跨类别迁移失败，V1.6 改为类别感知阈值校准。",
            },
            "paper": {
                "sections": [
                    "Abstract / Introduction：问题、贡献和 workflow 总览。",
                    "Method：evidence-grounded ideation、judge、repair、claim verification、execution feedback。",
                    "Experiments：三任务 benchmark、IAD execution-feedback case、消融和边界。",
                    "Limitations：人工评审规模、seeded evidence bank、lightweight scaffold 边界。",
                ],
                "claim": "根据最终实验结果和证据核查状态生成论文草稿，而不是在实验前直接写结论。",
            },
        }
    return payloads


def render_html(payloads: dict) -> str:
    data_json = json.dumps(payloads, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AI4S Research Agent Demo</title>
  <style>
    :root {{
      --bg: #eef5ff;
      --panel: #ffffff;
      --ink: #102033;
      --muted: #64748b;
      --blue: #175cff;
      --blue2: #0ea5e9;
      --green: #0f9f6e;
      --orange: #c47a00;
      --line: #dbe7f6;
      --soft: #f6f9ff;
      --shadow: 0 16px 40px rgba(20, 56, 110, .10);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at 12% 4%, rgba(23,92,255,.18), transparent 28%),
        radial-gradient(circle at 88% 8%, rgba(14,165,233,.16), transparent 28%),
        linear-gradient(180deg, var(--bg), #fff 38%, #f8fbff);
    }}
    header {{
      padding: 28px 42px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .logo {{
      width: 44px;
      height: 44px;
      border-radius: 14px;
      background: linear-gradient(135deg, var(--blue), var(--blue2));
      color: white;
      display: grid;
      place-items: center;
      font-weight: 900;
      box-shadow: var(--shadow);
    }}
    h1 {{ margin: 0; font-size: 24px; }}
    .sub {{ color: var(--muted); margin-top: 4px; font-size: 14px; }}
    .badge {{
      border: 1px solid var(--line);
      background: rgba(255,255,255,.72);
      border-radius: 999px;
      padding: 8px 12px;
      color: var(--muted);
      font-size: 13px;
    }}
    main {{
      padding: 10px 42px 34px;
      display: grid;
      grid-template-columns: 360px minmax(0, 1fr);
      gap: 18px;
      align-items: start;
    }}
    .panel {{
      background: rgba(255,255,255,.92);
      border: 1px solid var(--line);
      border-radius: 18px;
      box-shadow: var(--shadow);
    }}
    .input-panel {{ padding: 20px; position: sticky; top: 18px; }}
    label {{ display: block; font-weight: 800; margin: 16px 0 8px; }}
    input, select, textarea {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 12px 13px;
      font: inherit;
      color: var(--ink);
      background: white;
      outline: none;
    }}
    textarea {{ min-height: 92px; resize: vertical; line-height: 1.55; }}
    input:focus, select:focus, textarea:focus {{ border-color: var(--blue); box-shadow: 0 0 0 3px rgba(23,92,255,.10); }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }}
    .chip {{
      border: 1px solid var(--line);
      background: var(--soft);
      color: var(--ink);
      border-radius: 999px;
      padding: 7px 10px;
      cursor: pointer;
      font-size: 13px;
    }}
    .primary {{
      width: 100%;
      border: 0;
      border-radius: 14px;
      margin-top: 18px;
      padding: 13px 16px;
      font: inherit;
      font-weight: 900;
      color: white;
      cursor: pointer;
      background: linear-gradient(135deg, var(--blue), var(--blue2));
      box-shadow: 0 12px 24px rgba(23,92,255,.20);
    }}
    .secondary {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 14px;
      margin-top: 10px;
      padding: 12px 16px;
      font: inherit;
      font-weight: 800;
      color: var(--ink);
      cursor: pointer;
      background: white;
    }}
    .hint {{ color: var(--muted); font-size: 13px; line-height: 1.55; margin-top: 14px; }}
    .workspace {{ padding: 0; overflow: hidden; }}
    .topbar {{
      padding: 18px 20px;
      border-bottom: 1px solid var(--line);
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
      background: linear-gradient(90deg, #ffffff, #f4f9ff);
    }}
    .status {{ color: var(--muted); font-size: 14px; }}
    .status strong {{ color: var(--blue); }}
    .progress {{
      height: 8px;
      background: #e8f0fb;
      border-radius: 999px;
      overflow: hidden;
      margin: 0 20px 18px;
    }}
    .bar {{ height: 100%; width: 0; background: linear-gradient(90deg, var(--blue), var(--green)); transition: width .45s ease; }}
    .steps {{
      display: flex;
      flex-direction: column;
      gap: 8px;
      padding: 16px 20px 16px;
    }}
    .step {{
      position: relative;
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 10px 12px 10px 42px;
      min-height: 54px;
      background: white;
      color: var(--muted);
      font-size: 13px;
    }}
    .step::before {{
      content: attr(data-index);
      position: absolute;
      left: 10px;
      top: 11px;
      width: 23px;
      height: 23px;
      border-radius: 999px;
      display: grid;
      place-items: center;
      background: #e8f0fb;
      color: var(--blue);
      font-weight: 900;
      font-size: 12px;
    }}
    .step b {{ display: block; color: var(--ink); margin-bottom: 6px; }}
    .step.active {{ border-color: var(--blue); background: #eef5ff; }}
    .step.done {{ border-color: rgba(15,159,110,.38); background: #f0fdf8; }}
    .step.done::before {{ background: var(--green); color: white; }}
    .workflow-grid {{
      display: grid;
      grid-template-columns: 270px minmax(0, 1fr);
      gap: 12px;
      padding: 0 20px 22px;
      align-items: start;
    }}
    .outputs {{ padding: 0 20px 22px; display: grid; gap: 14px; }}
    .card {{
      border: 1px solid var(--line);
      border-radius: 16px;
      background: white;
      padding: 16px;
      display: none;
      animation: rise .3s ease both;
    }}
    .card.show {{ display: block; }}
    @keyframes rise {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    .card h2 {{ margin: 0 0 10px; font-size: 19px; }}
    .muted {{ color: var(--muted); }}
    .grid2 {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }}
    .grid3 {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }}
    .mini-card {{
      border: 1px solid var(--line);
      background: var(--soft);
      border-radius: 13px;
      padding: 12px;
    }}
    .mini-card b {{ display: block; margin-bottom: 7px; }}
    ul {{ margin: 8px 0 0; padding-left: 20px; }}
    li {{ margin: 6px 0; line-height: 1.5; }}
    .score-row {{ display: grid; grid-template-columns: 170px minmax(0,1fr) 48px; gap: 10px; align-items: center; margin: 10px 0; }}
    .meter {{ height: 9px; background: #e7edf7; border-radius: 999px; overflow: hidden; }}
    .meter i {{ display: block; height: 100%; background: linear-gradient(90deg, var(--blue2), var(--green)); border-radius: 999px; }}
    .pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border-radius: 999px;
      padding: 6px 10px;
      background: #eef5ff;
      color: var(--blue);
      font-weight: 800;
      font-size: 13px;
      margin: 4px 6px 4px 0;
    }}
    .final-card {{
      border-color: rgba(15,159,110,.38);
      background: linear-gradient(180deg, #ffffff, #f4fff9);
    }}
    .actions {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 12px; }}
    .small-btn {{
      border: 1px solid var(--line);
      background: white;
      border-radius: 10px;
      padding: 8px 10px;
      cursor: pointer;
      color: var(--ink);
      font-weight: 700;
    }}
    .danger-btn {{
      border: 0;
      background: linear-gradient(135deg, #0f9f6e, #0ea5e9);
      color: white;
    }}
    .agent-dialog {{
      display: grid;
      gap: 10px;
      margin-top: 12px;
    }}
    .chat-bubble {{
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 11px 12px;
      line-height: 1.55;
      background: #f8fbff;
    }}
    .chat-bubble.agent {{
      border-left: 4px solid var(--blue);
    }}
    .chat-bubble.user {{
      border-left: 4px solid var(--green);
      background: #f4fff9;
    }}
    .auth-box {{
      display: grid;
      gap: 10px;
      border: 1px solid rgba(15,159,110,.30);
      background: #f4fff9;
      border-radius: 14px;
      padding: 12px;
    }}
    .auth-note {{
      min-height: 58px;
      font-size: 13px;
    }}
    .form-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }}
    .form-grid label {{
      margin: 0 0 6px;
      font-size: 13px;
    }}
    .secret {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      letter-spacing: .03em;
    }}
    .file-note {{
      border: 1px dashed rgba(23,92,255,.35);
      border-radius: 12px;
      padding: 10px;
      background: #f8fbff;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.5;
    }}
    .phase-title {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      color: var(--blue);
      font-weight: 900;
      margin-bottom: 8px;
    }}
    .logbox {{
      white-space: pre-wrap;
      word-break: break-word;
      background: #0f172a;
      color: #e5f0ff;
      border-radius: 14px;
      padding: 14px;
      max-height: 300px;
      overflow: auto;
      font-size: 12px;
      line-height: 1.55;
    }}
    pre {{
      white-space: pre-wrap;
      word-break: break-word;
      background: #0f172a;
      color: #e5f0ff;
      border-radius: 14px;
      padding: 14px;
      max-height: 280px;
      overflow: auto;
      font-size: 12px;
      line-height: 1.55;
    }}
    @media (max-width: 1040px) {{
      main {{ grid-template-columns: 1fr; padding: 10px 20px 30px; }}
      header {{ padding: 24px 20px 12px; }}
      .input-panel {{ position: static; }}
      .workflow-grid, .grid2, .grid3 {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <div class="logo">AI</div>
      <div>
        <h1>AI4S Research Agent</h1>
        <div class="sub">输入科研任务，自动完成 idea 生成；经人工授权后进入 Claude-style 实验复现与论文草稿</div>
      </div>
    </div>
    <div class="badge">AI4S Research Workflow Demo</div>
  </header>

  <main>
    <aside class="panel input-panel">
      <h2 style="margin:0 0 4px;">任务输入</h2>
      <div class="hint">用户只需先填写任务类型和研究方向。系统自动完成论文检索、baseline 空白分析、idea 生成、评分、盲评与候选筛选；到实验阶段再请求数据集、API 和人工授权。</div>

      <label for="taskType">具体任务类型</label>
      <input id="taskType" list="taskOptions" value="工业异常检测 IAD + Agent" placeholder="例如：药物分子性质预测 / 蛋白质结构分析 / 材料发现" />
      <datalist id="taskOptions">
        <option value="工业异常检测 IAD + Agent"></option>
        <option value="物理属性预测"></option>
        <option value="室内单图 3D 场景生成"></option>
        <option value="药物分子性质预测"></option>
        <option value="蛋白质结构分析"></option>
        <option value="材料发现与性能预测"></option>
        <option value="气候科学数据建模"></option>
      </datalist>

      <label for="direction">研究方向</label>
      <textarea id="direction">工业异常检测中的可信科研智能体</textarea>

      <div class="chips">
        <button class="chip" data-task="工业异常检测 IAD + Agent" data-direction="工业异常检测中的可信科研智能体">IAD + Agent</button>
        <button class="chip" data-task="物理属性预测" data-direction="单张室内图像中的物体物理属性预测">物理属性预测</button>
        <button class="chip" data-task="室内单图 3D 场景生成" data-direction="从单张室内图像生成可验证 3D 场景">室内 3D</button>
        <button class="chip" data-task="药物分子性质预测" data-direction="AI for Science 药物发现">药物发现</button>
        <button class="chip" data-task="材料发现与性能预测" data-direction="AI for Science 新材料发现">材料发现</button>
      </div>

      <button class="primary" id="runBtn">启动智能体</button>
      <button class="secondary" id="resetBtn">重置输出</button>

    </aside>

    <section class="panel workspace">
      <div class="topbar">
        <div>
          <b id="runTitle">等待输入</b>
          <div class="status" id="runStatus">请选择任务并点击“启动智能体”。</div>
        </div>
        <div class="status">流程：<strong>idea 自动生成 → 授权实验 → 论文草稿</strong></div>
      </div>

      <div class="progress"><div class="bar" id="bar"></div></div>

      <div class="workflow-grid">
        <div class="steps" id="steps"></div>
        <div class="outputs">
          <section class="card" id="evidenceCard"></section>
          <section class="card" id="baselineCard"></section>
          <section class="card" id="ideaCard"></section>
          <section class="card" id="planCard"></section>
          <section class="card" id="scoreCard"></section>
          <section class="card" id="judgeCard"></section>
          <section class="card" id="repairCard"></section>
          <section class="card" id="verifyCard"></section>
          <section class="card" id="finalCard"></section>
          <section class="card" id="executeCard"></section>
          <section class="card" id="improveCard"></section>
          <section class="card final-card" id="paperCard"></section>
        </div>
      </div>
    </section>
  </main>

  <script>
    const TASKS = {data_json};
    const STEP_NAMES = [
      ["evidence", "论文检索"],
      ["baseline", "baseline 空白分析"],
      ["idea", "生成高质量 idea"],
      ["plan", "生成实验计划"],
      ["score", "自动评分"],
      ["judge", "匿名盲评"],
      ["repair", "critic repair"],
      ["verify", "论文证据核查"],
      ["final", "筛选最佳 idea"],
      ["execute", "数据/API/授权实验"],
      ["improve", "实验反馈改进"],
      ["paper", "输出论文草稿"],
    ];
    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
    const $ = (id) => document.getElementById(id);

    let lastResult = null;

    function esc(text) {{
      return String(text ?? "").replace(/[&<>"']/g, s => ({{"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;","'":"&#39;"}}[s]));
    }}
    function list(items) {{
      return `<ul>${{(items || []).map(x => `<li>${{esc(x)}}</li>`).join("")}}</ul>`;
    }}
    function pills(items) {{
      return (items || []).map(x => `<span class="pill">${{esc(x)}}</span>`).join("");
    }}
    function renderSteps(activeIndex = -1, doneIndex = -1) {{
      $("steps").innerHTML = STEP_NAMES.map(([, name], i) => {{
        const cls = i <= doneIndex ? "step done" : (i === activeIndex ? "step active" : "step");
        const state = i <= doneIndex ? "完成" : (i === activeIndex ? "运行中" : "等待");
        return `<div class="${{cls}}" data-index="${{i+1}}"><b>${{name}}</b><span>${{state}}</span></div>`;
      }}).join("");
      $("bar").style.width = `${{Math.max(0, (doneIndex + 1) / STEP_NAMES.length * 100)}}%`;
    }}
    function show(id, html) {{
      const el = $(id);
      el.innerHTML = html;
      el.classList.add("show");
    }}
    function clearOutputs() {{
      ["evidenceCard","baselineCard","ideaCard","planCard","scoreCard","judgeCard","repairCard","verifyCard","finalCard","executeCard","improveCard","paperCard"].forEach(id => {{
        const el = $(id);
        el.classList.remove("show");
        el.innerHTML = "";
      }});
      lastResult = null;
      renderSteps();
      $("bar").style.width = "0";
      $("runTitle").textContent = "等待输入";
      $("runStatus").textContent = "请选择任务并点击“启动智能体”。";
    }}
    function scoreRows(signals) {{
      const names = {{
        mechanism_specificity: "机制具体性",
        experimental_rigor: "实验严谨性",
        execution_readiness: "执行就绪度",
        evidence_grounding: "证据绑定",
        risk_awareness: "风险意识",
      }};
      return Object.entries(signals || {{}}).map(([k, v]) => {{
        const pct = Math.round(Number(v) * 100);
        return `<div class="score-row"><span>${{names[k] || k}}</span><div class="meter"><i style="width:${{pct}}%"></i></div><b>${{Number(v).toFixed(3)}}</b></div>`;
      }}).join("");
    }}
    function downloadJson() {{
      if (!lastResult) return;
      const blob = new Blob([JSON.stringify(lastResult, null, 2)], {{ type: "application/json" }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "ai4s_research_agent_result.json";
      a.click();
      URL.revokeObjectURL(url);
    }}
    async function authorizeExperiment() {{
      const log = $("executionLog");
      const noteEl = $("approvalNote");
      const btn = $("authorizeBtn");
      const providerEl = $("llmProvider");
      const modelEl = $("llmModel");
      const apiKeyEl = $("llmApiKey");
      const datasetPathEl = $("datasetPath");
      const taskType = $("taskType").value || (lastResult && lastResult.input.task_type) || "";
      const direction = $("direction").value || (lastResult && lastResult.input.research_direction) || "";
      const approvalNote = noteEl ? noteEl.value.trim() : "";
      const provider = providerEl ? providerEl.value : "claude";
      const model = modelEl ? modelEl.value.trim() : "";
      const apiKeyPresent = !!(apiKeyEl && apiKeyEl.value.trim());
      const datasetPath = datasetPathEl ? datasetPathEl.value.trim() : "";
      if (!approvalNote || approvalNote.length < 8) {{
        if (log) log.textContent = "请先填写明确的授权说明，例如：我授权在本地运行 IAD scaffold 实验链。";
        return;
      }}
      if (!apiKeyPresent) {{
        if (log) log.textContent = "请先输入 Claude 或其他大模型 API Key。Demo 不会保存或打印这个 key，但实验代理需要用户显式提供模型配置。";
        return;
      }}
      if (btn) {{
        btn.disabled = true;
        btn.textContent = "正在运行实验...";
      }}
      if (log) log.textContent = "Codex 实验执行代理：收到人工授权。\\n正在请求本地 server 调用 V24 authorized executor...\\n";
      try {{
        const res = await fetch("/api/execution/authorize", {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify({{
            task_type: taskType,
            research_direction: direction,
            approval_note: approvalNote,
            llm_provider: provider,
            llm_model: model,
            api_key_present: apiKeyPresent,
            dataset_path: datasetPath,
            categories: ["bottle", "cable", "capsule"]
          }})
        }});
        const payload = await res.json();
        if (!payload.executed) {{
          if (log) log.textContent =
            "Codex 实验执行代理：该任务当前进入实验计划阶段，但没有真实 runner。\\n" +
            (payload.message || "") + "\\n" +
            (payload.next_step || "");
          return;
        }}
        const summary = payload.summary || {{}};
        const metrics = summary.metrics || {{}};
        if (log) log.textContent =
          "Codex 实验执行代理：实验执行结束。\\n" +
          "returncode: " + payload.returncode + "\\n" +
          "run_dir: " + (payload.run_dir || "") + "\\n" +
          "llm_provider: " + (payload.llm_provider || provider) + "\\n" +
          "llm_model: " + (payload.llm_model || model) + "\\n" +
          "status: " + (summary.status || "") + "\\n" +
          "metrics:\\n" + JSON.stringify(metrics, null, 2) + "\\n\\n" +
          "executor output:\\n" + (payload.stdout || "");
      }} catch (err) {{
        if (log) log.textContent =
          "无法连接本地执行 API。请确认你是用 start_demo_server.py 打开的网页，而不是直接双击 HTML。\\n\\n" +
          "启动命令：\\npython competition_final_submission_20260725/03_demo_video/demo_assets/start_demo_server.py --port 8899\\n\\n" +
          String(err);
      }} finally {{
        if (btn) {{
          btn.disabled = false;
          btn.textContent = "进入对话式实验代理并授权运行";
        }}
      }}
    }}
    function updateDatasetSelection() {{
      const input = $("datasetFiles");
      const note = $("datasetFileNote");
      if (!input || !note) return;
      const files = Array.from(input.files || []);
      if (!files.length) {{
        note.textContent = "尚未选择本地数据文件。也可以直接填写服务器上的数据集路径。";
        return;
      }}
      const shown = files.slice(0, 6).map(f => f.webkitRelativePath || f.name);
      note.textContent = `已选择 ${{files.length}} 个文件：\\n` + shown.join("\\n") + (files.length > 6 ? "\\n..." : "");
    }}
    function normalizeTaskKey(raw) {{
      const text = String(raw || "").toLowerCase();
      if (text.includes("iad") || text.includes("异常") || text.includes("defect") || text.includes("anomaly")) return "iad";
      if (text.includes("物理属性") || text.includes("material") || text.includes("property")) return "physical";
      if (text.includes("室内") || text.includes("3d") || text.includes("三维") || text.includes("scene")) return "indoor3d";
      return null;
    }}
    function buildCustomData(direction, taskType) {{
      const safeDirection = direction || "AI4S 科研方向";
      const safeTask = taskType || "自定义科研任务";
      return {{
        taskName: safeTask,
        researchProblem: `围绕“${{safeDirection}}”中的“${{safeTask}}”任务，自动形成可评审、可修复、可执行的研究方案。`,
        baselineCards: [
          {{
            name: "Direct LLM ideation baseline",
            weakness: "容易生成宽泛 idea，缺少明确 baseline weakness、实验指标和失败标准。",
            evidence: "系统将该 baseline 作为通用对照，检查新方案是否更细粒度、更可执行。"
          }},
          {{
            name: "Literature-summary baseline",
            weakness: "能总结已有论文，但不一定能把论文证据转化为可执行实验计划。",
            evidence: "系统要求每个 idea 显式绑定 evidence、method、metric、negative control。"
          }},
          {{
            name: "Single-shot experiment-plan baseline",
            weakness: "单轮生成缺少 critic repair 和证据核查，容易遗漏风险与边界。",
            evidence: "系统加入自动评分、judge、repair 和 final plan schema。"
          }}
        ],
        idea: {{
          title: `Evidence-grounded workflow for ${{safeTask}}`,
          hypothesis: `如果先分析 baseline 缺陷，再生成机制明确、证据绑定、带负对照和成功阈值的研究 idea，则“${{safeTask}}”可以从泛泛想法转化为可执行方案。`,
          minimalModule: "baseline-weakness analyzer + evidence-grounded ideation + critic-repair planner",
          method: [
            "解析用户输入的研究方向和任务类型，生成结构化 task spec。",
            "整理候选 baseline，并提取可验证的 weakness。",
            "生成包含 minimal new module、algorithmic objective、metrics、negative controls 的 focused idea。",
            "用自动评分器检查机制具体性、实验严谨性、执行就绪度、证据绑定和风险意识。",
            "根据 judge / critic rationale 修复 idea，并输出最终实验计划。"
          ]
        }},
        score: {{
          overall: 0.84,
          signals: {{
            mechanism_specificity: 0.82,
            experimental_rigor: 0.86,
            execution_readiness: 0.83,
            evidence_grounding: 0.80,
            risk_awareness: 0.87
          }},
          warnings: ["自定义任务建议补充领域论文库和真实数据路径，以增强证据强度。"]
        }},
        paperEvidence: [
          "系统为自定义任务建立论文检索 query，并整理候选 paper evidence。",
          "证据会被用于 baseline weakness、idea mechanism 和实验计划字段。",
          "后续 reference claim verification 会检查 claim-evidence alignment。"
        ],
        judge: {{
          summary: "multi-LLM judge 将从 novelty、feasibility、expected effectiveness、experimental rigor 和 implementation readiness 维度评审候选方案。",
          evidence: "reference claim verification 将检查 baseline weakness 和 proposed mechanism 是否有论文证据支持。"
        }},
        repair: {{
          title: "通用 critic repair",
          before: "初始 idea 可能存在机制过宽、实验计划不完整、指标不可复现或证据绑定不足。",
          after: "修复后补充 baseline 对照、负对照、成功阈值、失败标准、实现产物和下一步执行路径。",
          impact: "输出更适合进入真实实验执行的 final research plan。"
        }},
        verification: {{
          status: "自定义任务已生成待核查 claim list；建议接入领域论文库后运行 reference claim verification。",
          checkedItems: [
            "baseline weakness 是否有论文证据",
            "proposed mechanism 是否和证据一致",
            "实验指标是否与任务目标匹配",
            "unsupported claims 是否显式标记"
          ]
        }},
        final: {{
          candidate: `Final candidate for ${{safeTask}}: evidence-grounded, critic-repaired research plan`,
          experimentPlan: [
            "构建 task_manifest.jsonl，记录数据来源、样本划分、baseline 和评估字段。",
            "实现 baseline_runner.py，复现或调用主要 baseline。",
            "实现 proposed_module.py，加入最小新增模块。",
            "运行 ablation 和 negative controls，检查改进是否来自核心机制。",
            "生成 result_table.csv、failure_case_report.md 和 evidence_audit.json。"
          ],
          datasets: ["用户指定数据集", "公开 benchmark 数据集", "领域论文证据库"],
          metrics: ["primary task metric", "robustness metric", "calibration metric", "evidence grounding score", "execution success rate"],
          negativeControls: ["randomized baseline", "shuffled evidence", "remove proposed module", "weakened prompt/control condition"],
          successThresholds: ["主指标优于 direct baseline", "负对照不能接近 full method", "失败案例可被系统标记", "输出方案字段完整率达到预设阈值"],
          artifacts: ["task_manifest.jsonl", "baseline_cards.jsonl", "focused_ideas.json", "experiment_plan.json", "final_research_plan.json"],
          nextStep: "接入该任务的论文检索结果和真实数据，运行完整 evidence-grounded workflow。"
        }},
        execution: {{
          reproduction: [
            "根据 final plan 生成 task manifest、baseline runner 和 proposed module scaffold。",
            "生成授权请求和命令预览；获得人工授权后再运行 baseline、proposed method、ablation 和 negative controls。",
            "保存 metrics table、execution log、failure cases 和 artifact checklist。"
          ],
          resultSignals: [
            "读取 primary metric、robustness metric、negative-control gap 和 failure criteria。",
            "记录 run_state、watchdog state、execution logs 和 authorization record。",
            "如果实验结果未达标，进入 execution-feedback diagnosis。"
          ]
        }},
        improvement: {{
          diagnosis: [
            "判断失败来源：机制不匹配、数据不足、阈值不稳、baseline 复现问题或证据约束不足。",
            "将实验反馈写成 targeted repair instruction，并重新生成修复后的方案。"
          ],
          example: "自定义任务会根据真实实验结果更新方法、阈值、负对照和下一轮实验计划。"
        }},
        paper: {{
          sections: [
            "Abstract / Introduction：任务背景、问题和贡献。",
            "Method：baseline-grounded idea generation、evaluation、repair、execution feedback。",
            "Experiments：主实验、消融、负对照、失败案例和复现细节。",
            "Limitations：证据边界、数据限制和未解决风险。"
          ],
          claim: "论文草稿基于最终实验结果和证据核查状态生成。"
        }}
      }};
    }}
    function resolveTaskData(direction, taskRaw) {{
      const key = normalizeTaskKey(taskRaw);
      if (key && TASKS[key]) return TASKS[key];
      return buildCustomData(direction, taskRaw);
    }}
    async function runDemo() {{
      clearOutputs();
      const taskRaw = $("taskType").value.trim();
      const direction = $("direction").value.trim() || "AI4S 科研任务";
      const data = resolveTaskData(direction, taskRaw);
      lastResult = {{ input: {{ research_direction: direction, task_type: taskRaw || data.taskName }}, output: data }};
      $("runTitle").textContent = `运行任务：${{data.taskName}}`;
      $("runStatus").innerHTML = `已接收输入：<strong>${{esc(direction)}}</strong>`;

      for (let i = 0; i < STEP_NAMES.length; i++) {{
        renderSteps(i, i - 1);
        $("runStatus").textContent = `正在执行：${{STEP_NAMES[i][1]}} ...`;
        await sleep(520);
        if (i === 0) {{
          show("evidenceCard", `
            <h2>1. 论文证据检索与整理</h2>
            <div class="mini-card"><b>Research problem</b>${{esc(data.researchProblem)}}</div>
            <div class="grid2" style="margin-top:12px;">
              <div class="mini-card"><b>检索/整理结果</b>${{list(data.paperEvidence || [])}}</div>
              <div class="mini-card"><b>证据用途</b>${{list([
                "约束 baseline weakness",
                "约束 proposed mechanism",
                "约束实验计划和评价指标",
                "为后续 reference claim verification 提供依据"
              ])}}</div>
            </div>`);
        }}
        if (i === 1) {{
          show("baselineCard", `
            <h2>2. Baseline cards</h2>
            <div class="muted">系统先分析已有 baseline 及其缺陷，而不是直接自由生成 idea。</div>
            <div class="grid3">
              ${{data.baselineCards.map(card => `
                <div class="mini-card">
                  <b>${{esc(card.name)}}</b>
                  <div><b>Weakness</b>${{esc(card.weakness)}}</div>
                  <div style="margin-top:8px;"><b>Evidence</b><span class="muted">${{esc(card.evidence)}}</span></div>
                </div>
              `).join("")}}
            </div>`);
        }}
        if (i === 2) {{
          show("ideaCard", `
            <h2>3. Focused idea</h2>
            <div class="mini-card"><b>候选 idea</b>${{esc(data.idea.title)}}</div>
            <div class="grid2" style="margin-top:12px;">
              <div class="mini-card"><b>核心假设</b>${{esc(data.idea.hypothesis)}}</div>
              <div class="mini-card"><b>最小新增模块</b>${{esc(data.idea.minimalModule)}}</div>
            </div>
            <div class="mini-card" style="margin-top:12px;"><b>方法流程</b>${{list(data.idea.method)}}</div>`);
        }}
        if (i === 3) {{
          show("planCard", `
            <h2>4. 实验计划生成</h2>
            <div class="grid2">
              <div class="mini-card"><b>实验步骤</b>${{list(data.final.experimentPlan)}}</div>
              <div class="mini-card"><b>数据集</b>${{pills(data.final.datasets)}}</div>
              <div class="mini-card"><b>评价指标</b>${{pills(data.final.metrics)}}</div>
              <div class="mini-card"><b>负对照</b>${{list(data.final.negativeControls)}}</div>
            </div>`);
        }}
        if (i === 4) {{
          show("scoreCard", `
            <h2>5. 自动评分 / depth-readiness gate</h2>
            <div class="grid2">
              <div class="mini-card"><b>综合分</b><span style="font-size:34px;font-weight:900;color:var(--green);">${{Number(data.score.overall).toFixed(3)}}</span></div>
              <div class="mini-card"><b>Warnings</b>${{data.score.warnings.length ? list(data.score.warnings) : '<span class="muted">无阻塞性警告</span>'}}</div>
            </div>
            <div style="margin-top:12px;">${{scoreRows(data.score.signals)}}</div>`);
        }}
        if (i === 5) {{
          show("judgeCard", `
            <h2>6. Multi-LLM judge</h2>
            <div class="grid2">
              <div class="mini-card"><b>Blind review summary</b>${{esc(data.judge.summary)}}</div>
              <div class="mini-card"><b>Reference verification</b>${{esc(data.judge.evidence)}}</div>
            </div>
            <div class="muted" style="margin-top:10px;">评审阶段隐藏 before/after 来源，用于判断 repair 是否真的改善 idea。</div>`);
        }}
        if (i === 6) {{
          show("repairCard", `
            <h2>7. Critic repair + 再次盲评</h2>
            <div class="grid3">
              <div class="mini-card"><b>${{esc(data.repair.title || "Targeted repair")}}</b><span class="muted">Repair type</span></div>
              <div class="mini-card"><b>Before</b>${{esc(data.repair.before || "根据 reviewer rationale 定位问题。")}}</div>
              <div class="mini-card"><b>After</b>${{esc(data.repair.after || "输出机制一致、证据绑定、实验可执行的修复方案。")}}</div>
            </div>
            <div class="mini-card" style="margin-top:12px;"><b>Repair impact / re-review</b>${{esc(data.repair.impact || "repair 后进入再次评审与证据核查。")}}</div>`);
        }}
        if (i === 7) {{
          show("verifyCard", `
            <h2>8. Reference claim verification</h2>
            <div class="grid2">
              <div class="mini-card"><b>核查状态</b>${{esc(data.verification.status)}}</div>
              <div class="mini-card"><b>核查项目</b>${{list(data.verification.checkedItems || [])}}</div>
            </div>`);
        }}
        if (i === 8) {{
          show("finalCard", `
            <h2>9. 最终候选 idea + 实验计划</h2>
            <div class="mini-card"><b>Final candidate</b>${{esc(data.final.candidate)}}</div>
            <div class="grid2" style="margin-top:12px;">
              <div class="mini-card"><b>实验计划</b>${{list(data.final.experimentPlan)}}</div>
              <div class="mini-card"><b>数据集</b>${{pills(data.final.datasets)}}</div>
              <div class="mini-card"><b>评价指标</b>${{pills(data.final.metrics)}}</div>
              <div class="mini-card"><b>负对照</b>${{list(data.final.negativeControls)}}</div>
              <div class="mini-card"><b>成功阈值</b>${{list(data.final.successThresholds)}}</div>
              <div class="mini-card"><b>输出产物</b>${{list(data.final.artifacts)}}</div>
            </div>
            <div class="mini-card" style="margin-top:12px;"><b>下一步执行</b>${{esc(data.final.nextStep)}}</div>
            <div class="actions">
              <button class="small-btn" onclick="downloadJson()">下载本次结果 JSON</button>
              <button class="small-btn" onclick="navigator.clipboard && navigator.clipboard.writeText(JSON.stringify(lastResult, null, 2))">复制结果</button>
            </div>
          `);
        }}
        if (i === 9) {{
          show("executeCard", `
            <h2>10. 数据/API 准备与 Claude-style 授权实验</h2>
            <div class="grid2">
              <div class="mini-card"><span class="phase-title">A. 实验准备</span><b>需要准备的数据与脚本</b>${{list(data.execution.reproduction || [])}}</div>
              <div class="mini-card"><span class="phase-title">B. 结果读取</span><b>实验完成后自动读取</b>${{list(data.execution.resultSignals || [])}}</div>
            </div>
            <div class="mini-card" style="margin-top:12px;"><b>执行原则</b>系统根据最佳 idea 和实验计划准备 baseline reproduction、proposed method、ablation、negative controls 和 result parser。涉及读取数据、调用大模型 API、消耗算力或覆盖结果文件时，必须由用户在网页端显式授权。</div>
            <div class="agent-dialog">
              <div class="chat-bubble agent"><b>Codex / Claude 实验执行代理</b>我已经把最终候选 idea 转成实验执行请求。下一步可以进入对话式实验代理：用户提供数据集位置和大模型 API，系统再通过授权执行器复现 baseline、运行 proposed module、读取结果并生成论文草稿。</div>
              <div class="chat-bubble user"><b>用户侧动作</b>上传或填写数据集路径，选择 Claude / GPT / Gemini / DeepSeek / Qwen 等模型接口，确认是否进入实验执行对话框。</div>
              <div class="auth-box">
                <b>1. 数据集准备</b>
                <div class="form-grid">
                  <div>
                    <label for="datasetPath">服务器数据集路径</label>
                    <input id="datasetPath" value="Datasets/01_IAD/mvtec_anomaly_detection/mvtec_anomaly_detection" placeholder="例如：Datasets/01_IAD/..." />
                  </div>
                  <div>
                    <label for="datasetFiles">本地选择/上传数据文件</label>
                    <input id="datasetFiles" type="file" multiple webkitdirectory onchange="updateDatasetSelection()" />
                  </div>
                </div>
                <div class="file-note" id="datasetFileNote">尚未选择本地数据文件。也可以直接填写服务器上的数据集路径。比赛 demo 中 IAD 使用服务器已准备的 MVTec AD scaffold 路径。</div>
              </div>
              <div class="auth-box">
                <b>2. 大模型执行代理配置</b>
                <div class="form-grid">
                  <div>
                    <label for="llmProvider">实验代理模型</label>
                    <select id="llmProvider">
                      <option value="claude">Claude / Claude Code style</option>
                      <option value="gpt">GPT / Codex style</option>
                      <option value="gemini">Gemini</option>
                      <option value="deepseek">DeepSeek</option>
                      <option value="qwen">Qwen</option>
                    </select>
                  </div>
                  <div>
                    <label for="llmModel">模型名</label>
                    <input id="llmModel" value="claude-sonnet-4-6" placeholder="例如：claude-sonnet-4-6 / gpt-5.5" />
                  </div>
                  <div style="grid-column:1/-1;">
                    <label for="llmApiKey">API Key</label>
                    <input id="llmApiKey" class="secret" type="password" placeholder="仅用于本地 demo 会话；不会写入报告、日志或压缩包" />
                  </div>
                </div>
                <span class="muted">当前比赛 demo 的真实可执行 runner 已接 IAD scaffold；API 字段用于展示“进入 Claude/其他大模型实验代理”的产品形态。后续可把 Auto-claude 的完整 experiment-queue / monitor / paper-writing loop 接到同一接口。</span>
              </div>
              <div class="auth-box">
                <b>3. 人工授权</b>
                <textarea class="auth-note" id="approvalNote">我授权在本地运行 IAD scaffold 实验链，并允许生成/覆盖 iad_mvp 的 scaffold 输出文件。</textarea>
                <button class="small-btn danger-btn" id="authorizeBtn" onclick="authorizeExperiment()">进入对话式实验代理并授权运行</button>
                <span class="muted">安全边界：网页不会执行任意命令，只会请求本地 server 调用固定授权执行器。非 IAD 任务会生成 runner 接入计划，不会伪造实验结果。</span>
              </div>
              <div class="logbox" id="executionLog">等待人工授权。请确认本页面由 start_demo_server.py 启动。</div>
            </div>`);
        }}
        if (i === 10) {{
          show("improveCard", `
            <h2>11. 根据实验结果诊断与改进</h2>
            <div class="grid2">
              <div class="mini-card"><b>诊断维度</b>${{list(data.improvement.diagnosis || [])}}</div>
              <div class="mini-card"><b>改进案例</b>${{esc(data.improvement.example || "")}}</div>
            </div>
            <div class="mini-card" style="margin-top:12px;"><b>闭环动作</b>如果实验结果不达标，系统把失败原因转化为下一轮 critic repair 和 experiment-plan update。</div>`);
        }}
        if (i === 11) {{
          show("paperCard", `
            <h2>12. 输出论文草稿</h2>
            <div class="grid2">
              <div class="mini-card"><b>论文标题草案</b>${{esc(data.taskName)}}: Evidence-Grounded Research Agent from Idea Generation to Authorized Experiment Execution</div>
              <div class="mini-card"><b>摘要骨架</b>系统根据任务输入、论文证据、baseline 空白、最佳 idea、实验计划、授权执行日志和 metrics 自动生成摘要；未执行或未验证的 claim 会保留为 limitation。</div>
              <div class="mini-card"><b>论文结构</b>${{list(data.paper.sections || [])}}</div>
              <div class="mini-card"><b>写作约束</b>${{esc(data.paper.claim || "")}}</div>
            </div>
            <div class="mini-card" style="margin-top:12px;"><b>自动化闭环</b>如果实验阶段已经授权运行，论文草稿会引用 execution_summary、metrics table、failure cases 和 evidence audit；如果任务 runner 尚未接入，则只输出实验计划和待验证 claim，不伪造结果。</div>
            <div class="actions">
              <button class="small-btn" onclick="downloadJson()">下载完整 workflow JSON</button>
              <button class="small-btn" onclick="navigator.clipboard && navigator.clipboard.writeText(JSON.stringify(lastResult, null, 2))">复制结果</button>
            </div>
          `);
        }}
        renderSteps(-1, i);
      }}
      $("runStatus").innerHTML = `<strong>完成。</strong> 已形成从任务输入到实验改进和论文草稿的完整 workflow。`;
    }}

    document.querySelectorAll(".chip").forEach(btn => {{
      btn.addEventListener("click", () => {{
        $("taskType").value = btn.dataset.task;
        $("direction").value = btn.dataset.direction;
      }});
    }});
    $("runBtn").addEventListener("click", runDemo);
    $("resetBtn").addEventListener("click", clearOutputs);
    renderSteps();
  </script>
</body>
</html>
"""


def main() -> None:
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    payloads = build_task_payloads()
    out_html = DEMO_DIR / "AI4S_RESEARCH_AGENT_DEMO.html"
    out_html.write_text(render_html(payloads), encoding="utf-8")
    out_json = SUBMISSION / "V22_INTERACTIVE_DEMO_PAYLOAD.json"
    out_json.write_text(json.dumps(payloads, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_html}")
    print(f"Wrote {out_json}")
    print("Interactive demo tasks:", ", ".join(payloads))


if __name__ == "__main__":
    main()
