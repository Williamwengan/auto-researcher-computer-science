# Manifest 说明

`main_experiment_manifest.jsonl` 包含 75 个 planned runs；`ablation_manifest.jsonl` 包含 75 个 planned runs。它们由 `scripts/build_experiment_manifests.py` 确定性生成。

由于 `experiment_protocol.yaml` 中的模型和 provider 仍标记为 `TO_BE_FROZEN`，这些行只能用于规模规划，不能直接触发 API。确认配置后先跑每种方法的 seed=11 smoke test，通过输出 schema、token 预算和匿名化检查后才运行其余 seeds。不要手工复制结果行，也不要把旧版输出直接伪装成冻结协议下的新实验。
