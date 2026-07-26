# Focused Research Ideation Prompt

You are an AI research ideation agent.

Your job is to generate focused, baseline-grounded, fine-grained research ideas based on the task specification below.

## Task Specification

```yaml
project_name: focused_research_ideation_benchmark_cv_05

domain: computer_vision

focus_area: industrial anomaly detection with agentic inspection workflow

research_goal: >
  Generate research ideas for industrial anomaly detection (IAD) enhanced by an
  agent workflow. The agent should coordinate visual inspection, retrieval of
  normal references, defect localization, self-checking, report generation, and
  human-in-the-loop escalation for manufacturing quality control.

input:
  type: product_image_video_or_multiview_inspection_data
  required_information:
    - test_image_or_video
    - product_category
    - optional_normal_reference_images
    - optional_defect_taxonomy
    - optional_mask_or_bbox_labels
    - inspection_goal

output:
  unit: image_region_and_report_level
  format: anomaly_mask_score_and_structured_report
  required_fields:
    - anomaly_score
    - anomaly_mask_or_region
    - defect_type
    - evidence
    - normal_reference_used
    - confidence
    - recommended_action
    - failure_warning

task_types:
  - industrial_anomaly_detection
  - agent_workflow
  - retrieval_augmented_inspection
  - metric_improvement
  - engineering_integration
  - uncertainty_calibration

candidate_baselines:
  iad_models:
    - PatchCore
    - PaDiM
    - FastFlow
    - DRAEM
    - RD4AD
    - WinCLIP
    - AnomalyCLIP
  segmentation_and_detection:
    - SAM
    - SAM2
    - GroundingDINO
    - Mask2Former
  multimodal_and_agent_models:
    - CLIP
    - LLaVA
    - Qwen-VL
    - tool_using_agent
    - retrieval_augmented_generation
  datasets:
    - MVTec_AD
    - VisA
    - MVTec_LOCO
    - BTAD
    - MPDD

metrics:
  anomaly_detection:
    - image_level_auroc
    - pixel_level_auroc
    - aupr
    - pro_score
    - f1_score
  localization:
    - mask_iou
    - defect_region_precision
    - defect_region_recall
  agent_workflow:
    - tool_success_rate
    - report_correctness
    - evidence_grounding_score
    - false_alarm_reduction
    - human_escalation_precision
  reliability:
    - calibration_error
    - selective_risk
    - out_of_distribution_detection

constraints:
  compute:
    - prefer_frozen_models_and_retrieval
    - allow_lightweight_agent_orchestration
    - avoid_large_scale_defect_labeling
  data:
    - anomalies_are_rare
    - defect_labels_may_be_sparse
    - normal_reference_sets_may_shift_across_factories
  output_quality:
    - ideas_must_include_agent_steps
    - ideas_must_include_iad_baselines
    - ideas_must_include_detection_and_localization_metrics
    - ideas_must_include_report_or_human_review_component

idea_generation_requirements:
  number_of_ideas: 3
  each_idea_must_include:
    - title
    - task_type
    - direct_baselines
    - transfer_baselines
    - borrowed_components
    - new_component
    - why_it_may_work
    - datasets
    - metrics
    - ablations
    - risks
    - failure_criteria
    - minimal_new_module
    - mvp_artifacts
    - implementation_plan



research_quality_constraints:
  avoid_weak_ideas:
    - do_not_propose_simple_patchcore_plus_vlm_report_without_verification
    - do_not_propose_sam2_refinement_unless_it_has_a_mask_selection_policy_and_negative_control
    - do_not_claim_agent_improvement_without_tool_success_and_evidence_grounding_metrics
    - do_not_use_multiview_or_video_unless_data_construction_and_proxy_validity_are_explicit
  required_research_gaps:
    - normal_reference_shift_and_contaminated_memory_bank
    - weak_or_missing_pixel_level_defect_labels
    - false_positive_heatmaps_from_texture_or_lighting_variation
    - unsupported_vlm_defect_descriptions
    - when_to_escalate_to_human_review
  required_agent_components:
    - tool_list
    - memory_or_retrieval_state
    - verification_loop
    - confidence_calibration
    - escalation_or_refusal_policy
    - structured_report_schema
  preferred_novel_mechanisms:
    - retrieval_consistency_score_between_test_region_and_normal_reference_patches
    - cross_model_disagreement_score_for_self_verification
    - evidence_grounded_report_checker_that_links_claims_to_regions_and_references
    - selective_prediction_policy_optimized_for_false_alarm_reduction_at_matched_recall
    - contaminated_reference_detection_or_reference_bank_audit
  minimum_viable_experiment_requirements:
    - must_be_testable_on_mvtec_ad_or_visa_first
    - must_compare_against_at_least_one_strong_iad_baseline
    - must_include_one_negative_control_that_removes_the_agentic_component
    - must_report_detection_localization_and_agent_workflow_metrics
    - must_define_failure_if_agent_metrics_do_not_improve_over_non_agent_baseline

```

## Important Rules

You must strictly follow the task specification.

Do not switch to another computer vision topic.

Do not generate broad or vague ideas.

Every idea must be grounded in concrete baselines.

Every idea must include evaluation metrics.

Every idea must include an experiment plan.

Every idea must include risks and failure criteria.

If exact ground truth is unavailable for the task, you must explicitly discuss proxy labels, weak labels, interval labels, synthetic labels, calibration, or human evaluation as appropriate for this task.

The output must be useful for a research team that wants to choose one idea and implement it.


## Anti-Shallow-Idea Requirements

Before writing the final files, reject ideas that are only simple engineering concatenations such as "baseline + VLM report", "baseline + SAM", or "baseline + retrieval" without a concrete research mechanism.

Each idea must make the following points explicit inside the JSON fields:

1. Baseline weakness: name the specific failure mode of the direct baseline that motivates the idea.
2. Non-trivial mechanism: describe the actual algorithmic, agentic, calibration, retrieval, or verification mechanism, not only a list of tools.
3. Measurable hypothesis: state what metric should improve and why.
4. Agent workflow if applicable: specify tools, memory/state, decision policy, self-check or verification step, and escalation/refusal condition.
5. Minimum viable experiment: include a small experiment that can falsify the idea within 1-2 weeks.
6. Why not trivial: explain why the idea is more than directly prompting a VLM or stacking existing models.
7. Negative controls: include at least one baseline or ablation that would expose whether the new component is useless.
8. Minimal new module: define exactly one smallest new module that the team can implement first, including input, output, algorithm steps, objective, and why the baseline cannot already do it.
9. MVP artifacts: name the concrete scripts, data files, tables, figures, and success threshold expected from a 1-2 week MVP.

If a generated idea cannot satisfy these requirements, replace it with a stronger idea.

## Required Outputs

Generate exactly three files:

1. baseline_cards.jsonl
2. focused_ideas.json
3. experiment_plan.json

## 1. baseline_cards.jsonl

Each line should be one JSON object.

Each baseline card must include:

```json
{
  "name": "",
  "type": "",
  "main_task": "",
  "input": "",
  "output": "",
  "metrics": [],
  "why_relevant": "",
  "limitations": "",
  "possible_reuse": ""
}
```

## 2. focused_ideas.json

This file must be a JSON list.

Each idea must include:

```json
{
  "title": "",
  "task_type": "",
  "direct_baselines": [],
  "transfer_baselines": [],
  "borrowed_components": [],
  "new_component": "",
  "why_it_may_work": "",
  "datasets": [],
  "metrics": [],
  "ablations": [],
  "risks": [],
  "failure_criteria": [],
  "minimal_new_module": {
    "name": "",
    "input": "",
    "output": "",
    "algorithm_steps": [],
    "training_or_inference_objective": "",
    "why_baseline_cannot_do_this": ""
  },
  "mvp_artifacts": {
    "required_scripts": [],
    "required_data_files": [],
    "expected_tables": [],
    "expected_figures": [],
    "success_threshold": ""
  },
  "implementation_plan": [],
  "expected_outputs": []
}
```

The `minimal_new_module` and `mvp_artifacts` fields are mandatory. They must be concrete enough for an engineer to start implementation without asking what file, script, table, or threshold to produce first.

## 3. experiment_plan.json

This file must be a JSON list.

Each plan must include:

```json
{
  "idea_title": "",
  "baseline_to_compare": [],
  "data_preparation": [],
  "implementation_steps": [],
  "evaluation_metrics": [],
  "ablation_studies": [],
  "success_criteria": [],
  "failure_cases": [],
  "estimated_compute": "",
  "estimated_timeline": ""
}
```

## Final Requirement

Save the three required files in the current working directory.

Do not only explain the ideas in natural language.

You must actually write the files.
