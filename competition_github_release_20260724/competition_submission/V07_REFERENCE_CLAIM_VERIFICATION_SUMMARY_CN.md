# v0.7 Reference Claim Verification 汇总报告

| Run | Ideas | Papers | Claims | Supported | Weak | Manual | Unsupported | Declared Unsupported | Pass Rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `/data1/huangyuling/-A_HYL/AI4S/ResearchArena-main/outputs/v05_evidence_grounded_ideation_05_iad_agent_workflow_20260712_101952/repair_runs/local_targeted_repair_20260712_103945/repaired_run` | 3 | 24 | 21 | 8 | 4 | 3 | 0 | 6 | 0.857 |
| `/data1/huangyuling/-A_HYL/AI4S/ResearchArena-main/outputs/v05_evidence_grounded_ideation_01_physical_property_prediction_20260712_102328/repair_runs/physical_v2_mechanism_repair_20260712_163924/repaired_run` | 3 | 51 | 15 | 1 | 3 | 7 | 0 | 4 | 0.533 |
| `/data1/huangyuling/-A_HYL/AI4S/ResearchArena-main/outputs/v05_evidence_grounded_ideation_03_indoor_scene_generation_seeded/repair_runs/local_targeted_repair_20260712_130408/repaired_run` | 3 | 18 | 15 | 0 | 3 | 12 | 0 | 0 | 0.2 |

## 解释

- Pass rate 将 `supported`、`weakly_supported`、`declared_unsupported` 计为通过。
- `needs_manual_check` 不直接判失败，但代表需要人工读论文或补检索。
- `unsupported` 代表自动检查下缺少有效证据，不应直接进入最终报告。
