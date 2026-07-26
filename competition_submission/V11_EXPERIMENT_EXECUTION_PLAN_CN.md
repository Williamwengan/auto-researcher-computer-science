# V1.1 Experiment Execution Planning

生成时间：2026-07-14 10:52:06

生成脚本：`focused_workflow/scripts/build_v11_experiment_execution_plan.py`

## 为什么做 V1.1

V1.0 已经把经过生成、修复、盲评和证据校验的 idea 转换成 final research plans。V1.1 的任务是继续往前推进半步：把 final research plans 拆成可执行实验任务清单。

本阶段仍然不做三件事：

- 不真正写完整算法实现；
- 不运行真实 benchmark；
- 不声称得到实验结果。

它只回答：如果下一步要执行实验，应该准备哪些数据，写哪些脚本，跑哪些命令，产生哪些表格，以及怎样判断执行失败。报告中的命令是模板，不是当前立刻执行的命令；对应脚本需要在 v1.2 才真正实现。

## 总览

| Execution Plan | Source Plan | 任务 | 执行范围 | 建议优先级 |
| --- | --- | --- | --- | --- |
| exec_01_physical_property_proxy_interval_mvp | plan_01_physical_property | 物理属性预测 | Proxy-label calibrated interval prediction MVP, not full physical-property SOTA training. | Medium: scientifically strong, but proxy labels and material tables need careful manual setup. |
| exec_03_indoor3d_scene_graph_verifier_mvp | plan_03_indoor3d | 室内单图 3D 场景生成 | Lightweight scene-graph and geometry-consistency verifier MVP, not full 3D generation training. | Low to Medium: visually valuable, but engineering risk is higher than IAD and physical-property proxy MVP. |
| exec_05_iad_reference_consistency_mvp | plan_05_iad_agent | 工业异常检测 IAD + Agent | Reference-consistency IAD agent MVP with cached or lightweight baseline scores, not a full industrial deployment. | High for first real execution: easiest to make runnable with public datasets and standard metrics. |

注意：这里的“建议优先级”只是工程执行优先级，不是项目方向选择。项目主张仍然是跨任务科研 idea generation workflow。

## Execution Plan Schema

每个 execution plan 必须包含以下字段：

- execution_plan_id
- source_plan_id
- task_name
- execution_scope
- why_this_scope
- data_preparation_tasks
- scripts_to_implement
- commands_to_run
- expected_outputs
- metrics_to_compute
- validation_checks
- failure_checks
- compute_requirements
- manual_decisions_needed
- not_in_scope
- recommended_execution_priority

## 三个执行规划

### exec_01_physical_property_proxy_interval_mvp: 物理属性预测

执行范围：Proxy-label calibrated interval prediction MVP, not full physical-property SOTA training.

为什么这样切：真实物理属性标签难获取，所以 v1.1 先把执行范围限制在 material table + proxy interval labels + calibration evaluation。这样能验证 final plan 是否可执行，同时避免陷入大规模标注。

### 数据准备任务

1. 选择一个小型 indoor image subset，记录 image_id、object_id、category、mask_or_box 和 material candidates。
2. 整理 material_property_table.csv，至少包含 density、Young's modulus、Poisson ratio、hardness、friction 的 interval ranges 和 provenance。
3. 构建 indoor_property_manifest.jsonl，把每个 object 绑定 category、mask、material candidates 和 proxy interval labels。
4. 准备 shuffled material-property table，作为 negative control。

### 待实现脚本

| Script | Purpose | Inputs | Outputs |
| --- | --- | --- | --- |
| scripts/prepare_indoor_property_manifest.py | 从图像/标注/检测结果构建 object-level manifest。 | raw indoor images<br>object masks or boxes<br>material candidates | data/indoor_property_manifest.jsonl |
| scripts/build_material_property_table.py | 整理材料到物理属性区间的映射表。 | raw material property sources | data/material_property_table.csv<br>data/material_property_table_shuffled.csv |
| scripts/predict_property_intervals.py | 根据 object category、material evidence 和属性表输出 calibrated intervals。 | data/indoor_property_manifest.jsonl<br>data/material_property_table.csv | results/physical_property_interval_predictions.csv |
| scripts/evaluate_property_intervals.py | 计算 interval coverage、calibration error、selective risk 和 negative control 差异。 | results/physical_property_interval_predictions.csv<br>proxy labels<br>shuffled-table predictions | results/physical_property_calibration_table.csv<br>results/physical_property_negative_control_report.csv |

### 命令模板

```bash
python scripts/prepare_indoor_property_manifest.py --images DATA_DIR --output data/indoor_property_manifest.jsonl
python scripts/build_material_property_table.py --output data/material_property_table.csv --make_shuffled_control
python scripts/predict_property_intervals.py --manifest data/indoor_property_manifest.jsonl --table data/material_property_table.csv --output results/physical_property_interval_predictions.csv
python scripts/evaluate_property_intervals.py --predictions results/physical_property_interval_predictions.csv --output_dir results
```

### 预期输出

- data/indoor_property_manifest.jsonl
- data/material_property_table.csv
- data/material_property_table_shuffled.csv
- results/physical_property_interval_predictions.csv
- results/physical_property_calibration_table.csv
- results/physical_property_negative_control_report.csv

### 指标

- prediction_interval_coverage
- calibration_error
- selective_risk
- density_log_mae or proxy interval error
- negative_control_gap_vs_shuffled_table

### 验证检查

- manifest row count > 0 and every row has object_id/category/material_candidates
- material table has non-empty interval ranges and provenance
- prediction file has one row per object unless abstained with reason
- coverage and calibration metrics are computed for accepted predictions

### 失败检查

- shuffled table performs within 5% of real table
- 90% nominal intervals have less than 80% empirical coverage
- selective risk does not decrease when confidence threshold increases
- many predictions lack provenance or material evidence

### 资源和人工决策

Compute：CPU is enough for table/interval MVP; single GPU optional if material candidates are produced by a VLM.

需要人工决定：

- Which indoor image subset to use first
- Which material-property source is acceptable for proxy labels
- Whether object masks come from existing labels, SAM2, or manual samples
- Which properties are mandatory in the first MVP

当前不做：

- Full physical-property benchmark training
- Claiming true material property ground truth from RGB alone
- Large-scale dataset construction

执行优先级：Medium: scientifically strong, but proxy labels and material tables need careful manual setup.

### exec_03_indoor3d_scene_graph_verifier_mvp: 室内单图 3D 场景生成

执行范围：Lightweight scene-graph and geometry-consistency verifier MVP, not full 3D generation training.

为什么这样切：完整单图 3D 生成工程太重。v1.1 先规划一个 verifier MVP，验证 idea 中最核心的 support/collision/relation 检查能否产生可度量输出。这样能保留复杂任务泛化证据，又不把项目拖进大型 3D 系统实现。

### 数据准备任务

1. 选择小型 indoor scene subset，准备 input image、visible objects、layout cues 和可用 depth/layout proxy labels。
2. 准备 seeded evidence bank 的披露说明，确保报告中透明标记。
3. 构建 indoor3d_scene_manifest.jsonl，包含 image_id、camera info if available、objects、layout/depth proxy。
4. 准备 random placement 和 shuffled relation negative controls。

### 待实现脚本

| Script | Purpose | Inputs | Outputs |
| --- | --- | --- | --- |
| scripts/prepare_indoor3d_scene_manifest.py | 构建室内单图 3D verifier 的输入 manifest。 | indoor RGB images<br>object detections<br>layout/depth proxy labels | data/indoor3d_scene_manifest.jsonl |
| scripts/build_scene_graph_hypotheses.py | 生成 object relation、support relation 和 occluded region hypotheses。 | data/indoor3d_scene_manifest.jsonl | results/indoor3d_scene_graph_predictions.jsonl |
| scripts/verify_scene_geometry.py | 检查 collision、support、out-of-room 和 relation consistency。 | results/indoor3d_scene_graph_predictions.jsonl | results/indoor3d_geometry_consistency_table.csv |
| scripts/evaluate_indoor3d_negative_controls.py | 对比 random placement 和 shuffled relation negative controls。 | results/indoor3d_scene_graph_predictions.jsonl | results/indoor3d_negative_control_report.csv |

### 命令模板

```bash
python scripts/prepare_indoor3d_scene_manifest.py --images DATA_DIR --output data/indoor3d_scene_manifest.jsonl
python scripts/build_scene_graph_hypotheses.py --manifest data/indoor3d_scene_manifest.jsonl --output results/indoor3d_scene_graph_predictions.jsonl
python scripts/verify_scene_geometry.py --scene_graphs results/indoor3d_scene_graph_predictions.jsonl --output results/indoor3d_geometry_consistency_table.csv
python scripts/evaluate_indoor3d_negative_controls.py --scene_graphs results/indoor3d_scene_graph_predictions.jsonl --output results/indoor3d_negative_control_report.csv
```

### 预期输出

- data/indoor3d_scene_manifest.jsonl
- results/indoor3d_scene_graph_predictions.jsonl
- results/indoor3d_geometry_consistency_table.csv
- results/indoor3d_negative_control_report.csv
- competition_submission/indoor3d_seeded_evidence_disclosure.md

### 指标

- support_relation_accuracy or proxy score
- collision_rate
- out_of_room_rate
- object_count_accuracy
- failure_detection_auc
- negative_control_gap_vs_random_placement

### 验证检查

- seeded evidence disclosure exists
- every scene graph has object nodes and relation edges
- geometry table contains collision/support/out_of_room metrics
- negative controls are generated and compared

### 失败检查

- random placement matches verifier on relation/collision metrics
- uncertainty fields are empty for most scenes
- scene graph verifier improves no metric over depth/layout-only baseline

### 资源和人工决策

Compute：CPU is enough for symbolic verifier; single GPU optional if depth/object detectors are run from scratch.

需要人工决定：

- Which small indoor dataset subset to use
- Whether to use existing detections/depth or generate them locally
- How to define proxy support/collision labels
- How to present seeded evidence disclosure in final materials

当前不做：

- Training a full single-image 3D generation model
- Rendering photorealistic novel views
- Claiming fully automatic paper retrieval for this direction

执行优先级：Low to Medium: visually valuable, but engineering risk is higher than IAD and physical-property proxy MVP.

### exec_05_iad_reference_consistency_mvp: 工业异常检测 IAD + Agent

执行范围：Reference-consistency IAD agent MVP with cached or lightweight baseline scores, not a full industrial deployment.

为什么这样切：IAD 的数据集和指标最标准，reference bank、negative controls、evidence-grounded report checker 也最容易做成一个闭环。因此如果后续要真正执行一个实验，IAD 是最低工程风险候选，但这不代表项目只做 IAD。

### 数据准备任务

1. 选择 MVTec AD 或 VisA 的小型 category subset，准备 train normal、test normal/anomaly split。
2. 构建 iad_reference_manifest.jsonl，记录 product_category、image_id、split、label、mask path 和 provenance。
3. 准备 baseline anomaly scores 和 heatmaps，可先使用已有 baseline/cached features。
4. 准备 contaminated normal bank、random retrieval、shuffled provenance 等 negative controls。

### 待实现脚本

| Script | Purpose | Inputs | Outputs |
| --- | --- | --- | --- |
| scripts/prepare_iad_reference_manifest.py | 构建 IAD reference bank 和 test split manifest。 | MVTec AD or VisA subset | data/iad_reference_manifest.jsonl |
| scripts/build_reference_bank.py | 为 normal references 建立 patch/image embeddings 和 retrieval index。 | data/iad_reference_manifest.jsonl | data/iad_reference_bank.npz<br>data/iad_reference_index.jsonl |
| scripts/run_iad_baselines.py | 运行或读取 PatchCore/PaDiM/WinCLIP 等 baseline anomaly scores。 | data/iad_reference_manifest.jsonl | results/iad_baseline_scores.csv<br>results/iad_region_heatmaps.npz |
| scripts/score_reference_consistency.py | 计算 anomaly/reference/disagreement/evidence 综合分和 accept/abstain 决策。 | results/iad_baseline_scores.csv<br>data/iad_reference_bank.npz<br>results/iad_region_heatmaps.npz | results/iad_reference_consistency_scores.csv |
| scripts/run_iad_negative_controls.py | 运行 random retrieval、shuffled provenance、contaminated normal bank 控制组。 | data/iad_reference_manifest.jsonl<br>results/iad_reference_consistency_scores.csv | results/iad_negative_control_report.csv |

### 命令模板

```bash
python scripts/prepare_iad_reference_manifest.py --dataset DATA_DIR --category bottle --output data/iad_reference_manifest.jsonl
python scripts/build_reference_bank.py --manifest data/iad_reference_manifest.jsonl --output_dir data
python scripts/run_iad_baselines.py --manifest data/iad_reference_manifest.jsonl --output_dir results
python scripts/score_reference_consistency.py --manifest data/iad_reference_manifest.jsonl --baseline results/iad_baseline_scores.csv --reference_bank data/iad_reference_bank.npz --output results/iad_reference_consistency_scores.csv
python scripts/run_iad_negative_controls.py --manifest data/iad_reference_manifest.jsonl --scores results/iad_reference_consistency_scores.csv --output results/iad_negative_control_report.csv
```

### 预期输出

- data/iad_reference_manifest.jsonl
- data/iad_reference_bank.npz
- data/iad_reference_index.jsonl
- results/iad_baseline_scores.csv
- results/iad_region_heatmaps.npz
- results/iad_reference_consistency_scores.csv
- results/iad_negative_control_report.csv
- results/iad_agent_execution_summary.md

### 指标

- image_level_auroc
- pixel_level_auroc or PRO score
- false_alarm_reduction
- evidence_grounding_score
- tool_success_rate
- selective_risk
- negative_control_gap_vs_random_retrieval

### 验证检查

- reference bank contains only allowed normal references
- baseline scores cover all test images
- accepted reports have region/reference/evidence ids
- negative controls use the same test split and metrics
- manual-check claims remain flagged in report text

### 失败检查

- random retrieval reaches within 5% of full agent
- contaminated reference bank does not reduce confidence or trigger warning
- evidence_grounding_score below 85% for accepted reports
- detection/localization metrics degrade while report quality improves

### 资源和人工决策

Compute：Single GPU useful for baselines/embeddings; CPU possible if baseline scores and features are cached.

需要人工决定：

- Which dataset and product category to start with
- Whether to compute baselines now or use cached scores
- Which region mask source to trust for evidence grounding
- How to define contaminated normal bank stress test

当前不做：

- Full industrial deployment
- Human-in-the-loop UI
- Large-scale multi-category benchmark
- Replacing all IAD baselines

执行优先级：High for first real execution: easiest to make runnable with public datasets and standard metrics.


## 当前阶段状态

完成 V1.1 后，项目阶段可以表述为：

```text
已完成 final research plan -> experiment execution plan 的拆解。
尚未进入真实实验代码实现、benchmark 运行和结果表格生成。
```

下一步如果继续推进，应进入 v1.2：选择一个 execution plan，真正实现最小脚本和小规模数据闭环。
