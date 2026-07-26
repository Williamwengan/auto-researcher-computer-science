# seed=11 主实验 Smoke Test 操作指南

## 第 0 步：理解当前配置

默认使用 Estelle OpenAI-compatible API 与 `gpt-5.5`。这是基于项目此前已经成功使用的通道做的 smoke 配置，不代表最终论文必须用该模型。五种方法共用相同 task、evidence 裁剪、temperature 和每次调用 token 上限。Baseline 保留其原生 proposal schema，Focused 方法使用结构化 schema；匿名评审阶段只做确定性排版，不用 LLM 给 baseline 补写字段。

`focused_no_repair` 先生成一份共享初始 ideas；`focused_generic_refine` 和 `focused_full` 从这份完全相同的初始结果分叉，分别做通用润色和 targeted repair。metadata 保存 source run ID 与 SHA-256，并将共享 generation 成本计入两条 pipeline，以隔离额外计算预算和 targeted repair 本身的收益。

Provider retry policy：429、500、502、503、504 以及 Cloudflare 520--524 视为临时基础设施错误，最多按 10/20/40/60 秒退避重试。重试会写入 metadata，不计为模型内容失败。

## 第 1 步：加载 API 环境

```bash
cd /data1/huangyuling/-A_HYL/AI4S/ResearchArena-main
source ~/.estelle_api_env
python -c 'import os; print("ESTELLE_API_KEY loaded:", bool(os.getenv("ESTELLE_API_KEY")))'
```

只检查布尔值，不打印 key。

## 第 2 步：语法检查与离线 dry-run

```bash
python -m py_compile aaai27/experiments/scripts/run_generation_smoke_test.py
python aaai27/experiments/scripts/run_generation_smoke_test.py --dry-run
```

预期看到 `Planned smoke runs: 15`，随后 15 行 `DRY ...`。这一步不调用 API。

## 第 3 步：只调用一个最便宜的探针

```bash
python aaai27/experiments/scripts/run_generation_smoke_test.py \
  --run-id physical_direct_prompt_s11
```

检查：

```bash
sed -n '1,200p' aaai27/experiments/results/raw/smoke_seed11/physical_direct_prompt_s11/metadata.json
python -m json.tool aaai27/experiments/results/raw/smoke_seed11/physical_direct_prompt_s11/ideas.json | sed -n '1,100p'
```

必须满足：`status=success`、正好 3 个 ideas、usage 非空或明确记录 provider 没返回 usage、没有越界 paper_id、没有 API key 写入文件。

## 第 4 步：跑同一任务五方法

```bash
python aaai27/experiments/scripts/run_generation_smoke_test.py \
  --run-id physical_direct_prompt_s11 \
  --run-id physical_researcharena_s11 \
  --run-id physical_focused_no_repair_s11 \
  --run-id physical_focused_generic_refine_s11 \
  --run-id physical_focused_full_s11
```

如果某个 run 目录已存在，脚本默认显示 `SKIP`，防止重复付费和覆盖证据。需要正式重跑时请更换 `--output-dir`；只有明确需要替换错误运行时才使用 `--overwrite`。不要把重复调用当独立 seed。

## 第 5 步：跑完整 15-run smoke test

建议使用新的输出目录：

```bash
python aaai27/experiments/scripts/run_generation_smoke_test.py \
  --output-dir aaai27/experiments/results/raw/smoke_seed11_v1
```

完成后统计：

```bash
grep -R '"status": "success"' aaai27/experiments/results/raw/smoke_seed11_v1/*/metadata.json | wc -l
grep -R '"status": "failed"' aaai27/experiments/results/raw/smoke_seed11_v1/*/metadata.json
```

目标是 15 个 success、0 个 failed。若失败，不要立即跑其余 60 runs；先把终端输出和失败目录的 `metadata.json` 发给 Codex 诊断。

## 第 6 步：人工检查公平性

对 15 个 `prompt.txt` 检查：同任务 evidence 内容相同；baseline 与 focused schema 按协议不同；没有方法名称泄漏到最终 review formatter。对 metadata 检查 prompt 长度、输出 token、调用次数和耗时。

注意：当前 `researcharena` 是在统一 API/证据/输出约束下复现其 ideation instruction 的 controlled prompt baseline，不是原始 ResearchArena 完整 agent 的等价运行。论文中必须称为 `ResearchArena-style controlled ideation baseline`；原始 ResearchArena end-to-end 结果应另作 external-system comparison。

## 第 7 步：决定是否冻结

15 runs 全部通过后，再将 `experiment_protocol.yaml` 中 `model/provider` 从 `TO_BE_FROZEN` 正式改为实际配置，并记录模型访问日期。之后才能扩展到剩余 seeds。
