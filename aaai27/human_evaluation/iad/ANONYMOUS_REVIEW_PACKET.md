# 工业异常检测 IAD + Agent：匿名科研 Idea A/B 评审包

评审者代码：`iad_expert`

条目数：20

请先完整阅读上一级目录的 `HUMAN_BLIND_REVIEW_INSTRUCTIONS_CN.md`。不要查看任何 private answer key，也不要使用大模型代评。

## Item 1: HUM-7d26d56c23

类型：`single_idea`

### Candidate A

Title:
Reference-Consistency Agent for Shifted or Contaminated Normal Memory Banks

Core proposal:
Add a retrieval-audit agent around a frozen IAD model. For each suspicious test region, the agent retrieves top-k normal reference patches, scores how consistently those references support the anomaly decision, identifies suspicious reference-bank entries through nearest-neighbor graph outlierness and leave-one-reference sensitivity, recomputes region scores after excluding suspect references, and reports whether the decision is stable. The final output links each defect region to the retrieved normal evidence, marks low-trust references, and escalates cases whose anomaly score depends strongly on unstable or contaminated references.

Motivation or baseline weakness:
PatchCore-style nearest-neighbor IAD methods can become unstable when the normal memory bank contains mislabeled anomalous patches or when reference images come from a shifted factory condition. The resulting heatmap does not indicate whether a high anomaly score is supported by trustworthy normal references or driven by unreliable neighbors.

Mechanism or approach:
A lightweight reference-bank auditor using frozen PatchCore, DINO, or CLIP patch embeddings to estimate per-reference contamination likelihood and per-region retrieval_consistency_score, combined with a rule-based agent state machine for retrieval, verification, reporting, and escalation.
Compute an audited region score that combines the base IAD anomaly score, dissimilarity to trusted normal references, and a reference_instability penalty. Calibrate selective prediction so the system reduces false alarms under contaminated or shifted reference banks while preserving recall. Flag references whose removal changes many region scores or whose neighborhood structure is unusually isolated relative to other normal-bank entries.

Experiment and implementation plan:
PatchCore; PaDiM; FastFlow; RD4AD; WinCLIP
MVTec_AD train/test normal and anomaly images with masks; VisA train/test normal and anomaly images with masks; Synthetic contaminated memory banks created by injecting anomalous test patches or shifted normal images into the reference set; Optional factory-shift proxy splits using product category, lighting augmentation, camera perturbation, or acquisition-condition changes
build_patch_memory_bank.py; inject_reference_contamination.py; run_baseline_iad_heatmaps.py; retrieve_topk_normal_patches.py; audit_reference_bank.py; agent_verify_and_report.py; evaluate_detection_localization_agent.py; calibrate_selective_policy.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; f1_score; mask_iou; defect_region_precision; defect_region_recall; tool_success_rate; evidence_grounding_score; false_alarm_reduction; human_escalation_precision; calibration_error; selective_risk; out_of_distribution_detection
Remove reference-bank audit while keeping nearest-reference retrieval; Use random normal references instead of nearest retrieved references; Use the base PatchCore heatmap without retrieval consistency scoring; Disable score-stability verification after suspect reference removal; Replace calibrated escalation with a fixed anomaly threshold; Vary contamination rate and factory-shift severity
Non-agent PatchCore with a templated report but no retrieval audit, verification loop, or escalation policy; Reference retrieval with shuffled region-reference links to test whether evidence grounding depends on correct visual correspondences
At matched anomaly recall, reduce false_alarm_rate by at least 10% over PatchCore in contaminated or shifted reference settings; Improve or preserve pixel_level_auroc and pro_score within 1 point of PatchCore on clean MVTec_AD or VisA while improving robustness under contaminated banks; Achieve evidence_grounding_score of at least 0.75 for reports that link each defect claim to a region and trusted reference patches; Improve human_escalation_precision by at least 10% over fixed-threshold escalation; Failure if agent workflow metrics do not improve over the non-agent baseline or if clean-data localization drops by more than 2 points

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W4404704036

Risks, controls, or fallback:
Risk: synthetic contamination or proxy shifts may not fully represent real factory drift. Fallback: evaluate several controlled contamination and shift regimes, report sensitivity curves, and frame claims specifically as reference-bank robustness rather than general domain adaptation.

### Candidate B

Title:
Reference-Consistency Agent for Shifted or Contaminated Normal Memory Banks

Core proposal:
Add a retrieval-audit agent around a frozen nearest-neighbor IAD pipeline. The workflow is: compute the baseline anomaly heatmap; convert high-score connected components into suspicious regions; retrieve top-k normal patches for each region from the memory bank; compute retrieval_consistency_score from the agreement among retrieved neighbors, their distance margin to the test region, and their own cross-neighbor normality; identify suspicious reference patches using leave-one-reference or leave-one-cluster influence on region scores; recompute the region anomaly score after excluding suspect references; compare pre- and post-audit score stability; emit a structured report linking each anomaly claim to the test region, trusted references, removed references if any, and an escalation decision. The agent escalates rather than suppresses a defect when the region remains anomalous but the trusted reference evidence is insufficient.

Motivation or baseline weakness:
PatchCore-style nearest-neighbor industrial anomaly detectors can become unstable when the normal memory bank is shifted across acquisition conditions or contains contaminated normal examples. Their heatmaps also do not indicate whether a high anomaly score was caused by trustworthy normal references, outlier reference patches, or reference-bank instability.

Mechanism or approach:
A lightweight reference-bank auditor over frozen PatchCore-style patch embeddings, optionally DINO or CLIP embeddings for cross-checking. It outputs per-reference contamination_likelihood, per-region retrieval_consistency_score, score_instability_after_reference_removal, and a rule-based agent state for verify, accept, refuse, or escalate.
For each region r, compute audited_score(r)=base_iad_score(r)+lambda_instability*score_instability(r)-lambda_trust*trusted_normal_support(r), where trusted_normal_support is estimated only from references with low contamination_likelihood. Calibrate a selective decision rule so that reports are emitted when audited confidence exceeds tau and otherwise escalated. Reference contamination_likelihood is estimated from nearest-neighbor graph outlierness, disagreement with local normal clusters, and influence on many test-region scores under leave-one-reference or leave-one-cluster removal.

Experiment and implementation plan:
PatchCore; PaDiM; FastFlow; RD4AD; WinCLIP
MVTec_AD train/test normal and anomaly images with masks; VisA train/test normal and anomaly images with masks; Synthetic contaminated memory banks created by injecting a controlled percentage of anomalous test patches, shifted normal images, or nuisance-perturbed normal images into the reference set; Factory-shift proxy splits by product category, lighting augmentation, camera perturbation, or acquisition-condition perturbation
build_patch_memory_bank.py; inject_reference_contamination.py; run_baseline_iad_heatmaps.py; retrieve_topk_normal_patches.py; audit_reference_bank.py; agent_verify_and_report.py; evaluate_detection_localization_agent.py; calibrate_selective_policy.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; f1_score; mask_iou; defect_region_precision; defect_region_recall; tool_success_rate; evidence_grounding_score; false_alarm_reduction; human_escalation_precision; calibration_error; selective_risk; out_of_distribution_detection
Remove reference-bank audit but keep nearest-neighbor retrieval; Use random normal references instead of top-k retrieved references; Use the base PatchCore heatmap without retrieval_consistency_score; Disable score-stability verification after suspect-reference removal; Replace calibrated escalation with a fixed anomaly-score threshold; Vary contamination rate and shift severity independently; Use only PatchCore embeddings versus adding DINO or CLIP embedding cross-checks
Non-agent PatchCore plus a templated report with no retrieval audit, no score-stability verification, and no escalation policy; Reference retrieval with shuffled region-reference links to test whether evidence grounding depends on the true retrieved patches; Clean normal-bank setting with no injected contamination to verify that the auditor does not invent contamination or degrade clean-data localization; Injected contamination labels hidden during calibration to prevent tuning directly on synthetic contamination identities
At matched anomaly recall, reduce false_alarm_rate by at least 10% over PatchCore on contaminated or shifted reference settings; Preserve pixel_level_auroc and pro_score within 1 point of PatchCore on clean MVTec_AD or VisA while improving contaminated-bank robustness; Achieve evidence_grounding_score of at least 0.75 for reports linking each defect claim to a region and trusted reference patches; Improve human_escalation_precision by at least 10% over fixed-threshold escalation; Failure if agent workflow metrics do not improve over the non-agent retrieval baseline or if localization drops by more than 2 points on clean data

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W4404704036

Risks, controls, or fallback:
Risk: synthetic contamination and proxy shifts may not represent real factory drift. Fallback: report sensitivity curves across multiple contamination types and shift severities, separate clean-bank and contaminated-bank results, and restrict claims to reference-bank robustness rather than broad domain adaptation.

---

## Item 2: HUM-24479ba8f8

类型：`single_idea`

### Candidate A

Title:
Evidence-Grounded Report Checker with Selective Human Escalation for VLM-Based IAD

Core proposal:
Build a lightweight agent workflow in which WinCLIP, AnomalyCLIP, CLIP, and PatchCore provide image-level anomaly scores and candidate regions. A VLM-style report generator drafts a structured report with fields for defect presence, region, visual evidence, normal-reference contrast, and uncertainty. A claim-to-evidence checker parses the report into atomic claims and verifies each claim against candidate region crops, anomaly masks or heatmaps, retrieved same-category normal references, and an optional allowed defect taxonomy. Unsupported claims are revised to generic localized-anomaly language, refused, or escalated to human review. The selective decision policy is calibrated on validation data to reduce false alarms at matched image-level recall rather than improving report fluency alone.

Motivation or baseline weakness:
WinCLIP, AnomalyCLIP, CLIP, and VLM-style inspection workflows can produce plausible semantic defect descriptions that are unsupported by localized visual evidence, especially when defect taxonomies are sparse, candidate regions are weak, or normal references shift.

Mechanism or approach:
A claim-to-evidence verifier that parses structured reports into atomic claims, links each claim to localized anomaly evidence and retrieved normal references, scores grounding support and taxonomy validity, and outputs calibrated confidence with accept, revise, refuse, or escalate decisions.
Optimize selective report correctness by maximizing report_correctness and evidence_grounding_score while maintaining image-level anomaly recall and reducing false alarms under a bounded automated-coverage target.

Experiment and implementation plan:
WinCLIP; AnomalyCLIP; CLIP; PatchCore
MVTec_AD and VisA images with product categories, anomaly masks, and defect labels where available; normal_reference_images for same-category retrieval-grounded comparison; optional defect_taxonomy converted to an allowed report vocabulary; human-review proxy labels derived from ground-truth anomaly presence, class labels where available, and mask overlap with claimed regions; normal-image subsets and masked-region variants for refusal and confidence-drop tests
run_winclip_anomalyclip_clip_patchcore_candidates.py; retrieve_normal_references_for_region.py; generate_structured_vlm_style_report.py; parse_report_into_atomic_claims.py; verify_claim_region_reference_grounding.py; calibrate_selective_escalation_policy.py; evaluate_report_and_agent_metrics.py
image_level_auroc; pixel_level_auroc; aupr; mask_iou; defect_region_precision; defect_region_recall; report_correctness; evidence_grounding_score; false_alarm_reduction; tool_success_rate; f1_score
remove evidence-grounded report checker and keep the original VLM-style report; remove retrieval of same-category normal references; allow free-form defect descriptions instead of taxonomy-constrained claims; use uncalibrated report confidence only; escalate based on anomaly score only without claim verification; replace region-linked evidence with whole-image captions; disable revision and allow only accept-or-reject decisions
Ask the report generator to describe defects on known normal images and require unsupported claims to be refused or escalated; Provide mismatched normal references from a different product category and require the checker to flag the evidence as invalid; Mask out the candidate defect region before report generation and require grounding confidence to drop; Shuffle candidate regions across images and require claim-to-region links to be rejected; Use a defect taxonomy with labels absent from the product category and require taxonomy-invalid claims to be revised or refused
Improve report_correctness by at least 20% over structured VLM-style reports without the checker; Improve evidence_grounding_score by at least 25% over retrieval-augmented reporting without claim verification; Reduce false alarms by at least 15% at matched image-level recall relative to WinCLIP or AnomalyCLIP report decisions; Keep defect_region_recall within 5% of the strongest candidate-region baseline while improving unsupported-claim refusal on normal images; Failure if detection or localization metrics improve but report_correctness and evidence_grounding_score do not exceed the non-checker baseline

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W7153328271; openalex:W7138099583; openalex:W7154655652

Risks, controls, or fallback:
Risk: the checker may be too strict when ground-truth defect labels are coarse or when the anomaly is visually real but semantically hard to name, lowering automated coverage. Fallback: output a generic localized anomaly with explicit uncertainty and escalate fine-grained defect naming to human review rather than hallucinating a specific defect type.

### Candidate B

Title:
Evidence-Grounded Report Checker with Selective Human Escalation for VLM-Based IAD

Core proposal:
Build a lightweight agent workflow in which IAD models first localize candidate regions, a VLM drafts a structured defect report, and an evidence-grounded checker verifies every claim against region crops, anomaly masks, retrieved normal references, and optional taxonomy entries. Claims without region-reference support are revised, refused, or escalated to a human reviewer using a calibrated selective prediction policy optimized for false-alarm reduction at matched recall.

Motivation or baseline weakness:
WinCLIP, AnomalyCLIP, CLIP, and multimodal VLM-style inspection can assign plausible semantic defect descriptions that are unsupported by localized visual evidence, especially when defect taxonomy is sparse or product references shift.

Mechanism or approach:
A claim-to-evidence verifier that parses the structured report into atomic claims, links each claim to anomaly regions and retrieved normal references, scores grounding support, and outputs calibrated confidence plus escalation decision.
Optimize selective report correctness: maximize evidence-grounded report accuracy and false-alarm reduction subject to maintaining image-level anomaly recall and bounded human-escalation rate.

Experiment and implementation plan:
WinCLIP; AnomalyCLIP; CLIP; PatchCore; Qwen-VL; LLaVA; tool_using_agent; retrieval_augmented_generation
MVTec_AD and VisA images with product categories, anomaly masks, and defect labels where available; optional defect_taxonomy converted to allowed report vocabulary; normal_reference_images for retrieval-grounded comparison; human-review proxy labels from ground-truth anomaly class and mask overlap
run_winclip_anomalyclip_patchcore_candidates.py; retrieve_normal_references_for_region.py; vlm_generate_structured_report.py; verify_claim_region_reference_grounding.py; calibrate_selective_escalation_policy.py; evaluate_report_and_human_review_metrics.py
image_level_auroc; pixel_level_auroc; aupr; mask_iou; defect_region_precision; defect_region_recall; report_correctness; evidence_grounding_score; false_alarm_reduction; human_escalation_precision; tool_success_rate; calibration_error; selective_risk; out_of_distribution_detection
remove evidence-grounded report checker and keep VLM report; remove retrieval of normal references; allow free-form defect descriptions instead of taxonomy-constrained claims; use uncalibrated confidence from VLM only; escalate based on anomaly score only without claim verification; replace region-linked evidence with whole-image captions
Ask the VLM to describe defects on normal images and verify that unsupported claims are refused or escalated; Provide mismatched normal references from a different product category and require the checker to flag invalid evidence; Mask out the candidate defect region before report generation and require confidence to drop
Improve report_correctness by at least 20% over VLM report without checker; Improve evidence_grounding_score by at least 25% over retrieval-augmented generation without claim verification; Reduce false alarms by at least 15% at matched image-level recall relative to WinCLIP or AnomalyCLIP; Achieve human_escalation_precision above 0.75 for ambiguous or unsupported cases; Failure if detection/localization metrics improve but report and grounding metrics do not exceed the non-agent baseline

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W7153328271; openalex:W7138099583; openalex:W7154655652

Risks, controls, or fallback:
Risk: the checker may be too strict when ground-truth defect labels are coarse, lowering automated coverage. Fallback: report a generic localized anomaly with explicit uncertainty and escalate taxonomy-level defect naming to human review rather than hallucinating a specific defect type.

---

## Item 3: HUM-30f3f8ee4e

类型：`single_idea`

### Candidate A

Title:
Evidence-Grounded Report Checker with Selective Human Escalation

Core proposal:
Add a report-verification agent that links every defect claim to an anomaly region, retrieved normal reference patches, and model scores; unsupported claims are removed or marked as failure_warning, and a selective prediction policy decides accept, reject, or human_review.

Motivation or baseline weakness:
WinCLIP, AnomalyCLIP, and VLM-style inspection agents may generate plausible defect descriptions that are not supported by localized visual evidence; conventional IAD baselines output scores and heatmaps but lack calibrated report confidence and escalation behavior.

Mechanism or approach:
A structured report checker that validates claim-region-reference triples and calibrates confidence using cross-model agreement, retrieval consistency, and validation-set conformal thresholds; it outputs anomaly_score, anomaly_mask_or_region, defect_type, evidence, normal_reference_used, confidence, recommended_action, and failure_warning.
Optimize selective reporting: minimize report_error and unsupported_claim_rate under a target human_review_budget, while preserving image_level_auroc, pixel_level_auroc, and defect_region_recall relative to IAD baselines.

Experiment and implementation plan:
WinCLIP; AnomalyCLIP; PatchCore; PaDiM; LLaVA; Qwen-VL; tool_using_agent
MVTec_AD or VisA images; product_category labels; normal reference images; optional defect taxonomy; optional mask or bounding-box labels for region grounding evaluation; inspection_goal text such as reject/repair/reinspect
run_iad_baselines.py; retrieve_reference_evidence.py; draft_vlm_report.py; check_claim_region_reference_links.py; calibrate_confidence_and_selective_policy.py; route_human_escalation.py; score_report_correctness_and_grounding.py; export_structured_inspection_report.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; report_correctness; evidence_grounding_score; human_escalation_precision; false_alarm_reduction; calibration_error; selective_risk; out_of_distribution_detection
VLM report without evidence checker; evidence checker without retrieved normal references; confidence calibration without cross-model agreement; escalation based only on anomaly_score; remove failure_warning field; replace structured schema with free-form report; use report checker on random regions
Generate a VLM or template report from the same anomaly score and mask but remove claim-region-reference verification and selective escalation; compare report correctness, unsupported claims, and human escalation precision.
Improve evidence_grounding_score by at least 20% versus unchecked VLM/template reports; Reduce unsupported defect descriptions by at least 30% without reducing defect_region_recall by more than 2 points; Achieve lower calibration_error than raw IAD confidence by at least 10% relative; At a fixed human review budget, improve selective_risk or false_alarm_reduction over anomaly-score-only escalation; Failure if report_correctness or evidence_grounding_score does not improve over the non-agent negative control

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W7154655652; openalex:W7153328271; openalex:W7138099583

Risks, controls, or fallback:
Risk: automatic report correctness labels may be noisy because public IAD datasets have limited defect taxonomies. Fallback: evaluate claim grounding objectively through region-reference links and use a small human audit subset only for report semantics, while keeping the detection and localization experiments fully reproducible on MVTec_AD or VisA.

### Candidate B

Title:
Evidence-Grounded Report Checker with Selective Human Escalation

Core proposal:
Add a report-verification agent that converts detector outputs and optional VLM drafts into structured claims, then verifies each claim against an anomaly region, same-class normal reference evidence, and calibrated model scores. Unsupported claims are removed, downgraded to failure_warning, or routed to human_review. The report is accepted only when claim-region-reference links pass grounding and confidence checks.

Motivation or baseline weakness:
WinCLIP, AnomalyCLIP, and VLM-style inspection agents can generate plausible defect descriptions that are not supported by localized visual evidence. Conventional IAD baselines output scores and heatmaps but lack calibrated report confidence, claim-level evidence checks, and selective human escalation behavior.

Mechanism or approach:
A structured report checker that validates claim-region-reference triples and calibrates report confidence using validation-set conformal or quantile thresholds over detector confidence, region overlap consistency, and reference-evidence contrast. It outputs anomaly_score, anomaly_mask_or_region, defect_type when supported, evidence, normal_reference_used, confidence, recommended_action, and failure_warning. If defect_type is not supported by dataset labels or grounded visual evidence, the field is set to unknown_defect rather than hallucinated.
Optimize selective reporting by minimizing report_error and unsupported_claim_rate under a fixed human_review_budget, while preserving image_level_auroc, pixel_level_auroc, and defect_region_recall relative to the underlying IAD baselines. The selective policy chooses accept_normal, reject_defective, or human_review using calibrated confidence and claim-grounding validity rather than free-form language confidence.

Experiment and implementation plan:
WinCLIP; AnomalyCLIP; PatchCore; PaDiM; CLIP-style prompt report baseline; unchecked VLM or template report baseline; anomaly-score-only escalation baseline
MVTec_AD or VisA images; product_category labels; normal reference images; optional defect taxonomy; optional mask or bounding-box labels for region grounding evaluation; inspection_goal text such as reject, repair, or reinspect; human-audited subset for report semantics when public labels do not specify defect descriptions
run_iad_baselines.py; retrieve_reference_evidence.py; draft_vlm_report.py; check_claim_region_reference_links.py; calibrate_confidence_and_selective_policy.py; route_human_escalation.py; score_report_correctness_and_grounding.py; export_structured_inspection_report.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; report_correctness; evidence_grounding_score; human_escalation_precision; false_alarm_reduction; calibration_error; selective_risk; out_of_distribution_detection
VLM or template report without evidence checker; evidence checker without retrieved normal references; confidence calibration using anomaly_score only; escalation based only on anomaly_score; remove failure_warning field; replace structured schema with free-form report; use report checker on random regions; force every case to be accepted with no human_review option
Generate a VLM or template report from the same anomaly score and mask but remove claim-region-reference verification and selective escalation; compare report correctness, unsupported claims, and human escalation precision.; Shuffle normal reference patches across product categories before report checking; grounding and confidence should degrade rather than remain unchanged.; Attach defect claims to random low-score regions; the checker should reject or mark the claims as unsupported.
Improve evidence_grounding_score by at least 20% versus unchecked VLM or template reports generated from the same detector outputs.; Reduce unsupported defect descriptions by at least 30% without reducing defect_region_recall by more than 2 points.; Achieve at least 10% relative lower calibration_error than raw IAD confidence or anomaly-score-only report confidence.; At a fixed human review budget, improve selective_risk or false_alarm_reduction over anomaly-score-only escalation.; Failure if report_correctness or evidence_grounding_score does not improve over the non-agent negative control, or if shuffled-reference and random-region controls pass verification at the same rate as true evidence links.

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W7154655652; openalex:W7153328271; openalex:W7138099583

Risks, controls, or fallback:
Risk: automatic report correctness labels may be noisy because public IAD datasets have limited defect taxonomies, and generic VLM drafts may over-specify defect types not present in labels. Fallback: evaluate claim grounding objectively through region-reference links, force unsupported defect categories to unknown_defect, use a small human audit subset only for report semantics, and keep detection and localization experiments fully reproducible on MVTec_AD or VisA.

---

## Item 4: HUM-c050632885

类型：`single_idea`

### Candidate A

Title:
Reference-Consistency Agent for Shift-Resilient PatchCore Inspection

Core proposal:
Wrap a frozen PatchCore detector with an agentic reference retrieval and audit loop. For each high-scoring test region, the agent retrieves the top-k normal reference patches and computes a reference-consistency score from PatchCore feature distance, local texture similarity, spatial/category metadata when available, and optional CLIP or WinCLIP semantic agreement. It then compares agreement across multiple references, flags memory-bank items that repeatedly act as poor or outlier explanations, and decides whether to accept, downweight, or escalate the region. The final decision is based on the original anomaly score, reference consistency, cross-reference agreement, memory-bank audit status, and calibrated uncertainty.

Motivation or baseline weakness:
PatchCore's nearest-neighbor normal memory bank can become unreliable when normal references are shifted, incomplete, or contaminated. In those cases, visually plausible but invalid neighbors may inflate false anomaly heatmaps or make inspection decisions difficult to justify with grounded reference evidence.

Mechanism or approach:
A lightweight reference-consistency scorer and memory-bank audit layer around frozen PatchCore features, with optional frozen CLIP/WinCLIP embeddings. It requires no defect-label training beyond calibration on held-out normal validation images and optional synthetic contamination experiments.
Reduce false positives caused by shifted or contaminated normal references while preserving PatchCore localization. For a candidate region r, use score(r)=PatchCoreScore(r)-lambda*ReferenceConsistency(r)+gamma*ReferenceRisk(r), where ReferenceRisk increases when retrieved neighbors are unstable, cross-category, or repeatedly implicated by the memory-bank audit. Escalate rather than suppress when calibrated confidence is below a chosen operating threshold.

Experiment and implementation plan:
PatchCore; PaDiM; FastFlow; WinCLIP; non-agent PatchCore plus static normal memory
MVTec_AD normal training images and test images with masks for evaluation; VisA normal training images and test images with masks for evaluation; synthetic memory-bank contamination created by injecting a controlled fraction of anomalous test images into the normal bank; synthetic reference shift created by mixing visually similar but nonmatching normal categories or cross-dataset normal references; held-out normal validation images for calibration of consistency and escalation thresholds
build_patchcore_memory_bank.py; retrieve_reference_patches.py; compute_retrieval_consistency.py; audit_reference_bank.py; calibrate_selective_policy.py; run_agent_inspection_loop.py; evaluate_detection_localization_agent_metrics.py; generate_structured_report.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; f1_score; mask_iou; defect_region_precision; defect_region_recall; false_alarm_reduction; tool_success_rate; evidence_grounding_score; human_escalation_precision; calibration_error; selective_risk
use PatchCore score only without reference consistency; keep retrieval evidence but remove memory-bank audit updates; replace nearest retrieved references with random normal references; use only PatchCore feature consistency without CLIP/WinCLIP semantic agreement; use only CLIP/WinCLIP semantic agreement without PatchCore feature consistency; vary injected contamination rate in the normal memory bank; vary selective escalation threshold at matched anomaly recall
allow the agent to retrieve references and write a report, but prevent reference consistency from changing anomaly scores or escalation decisions; shuffle the memory bank across product categories to test whether the agent flags invalid references instead of treating them as valid evidence; run the audit on clean normal validation images to estimate whether it incorrectly marks normal references as contaminated
at matched image-level recall, reduce false positive rate by at least 10 percent relative to PatchCore on MVTec_AD or VisA; maintain pixel_level_auroc and pro_score within 1 point of PatchCore while improving defect_region_precision by at least 5 percent; detect injected contaminated reference images with AUROC above 0.75; improve evidence_grounding_score and tool_success_rate over the retrieval-only negative control; fail if the agent improves reporting metrics only by excessive escalation or if localization drops by more than 2 pro_score points

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W4404704036

Risks, controls, or fallback:
Risk: strong reference-consistency penalties may suppress subtle true defects that remain close to normal texture. Fallback: use consistency mainly for selective escalation in low-margin cases, reporting the suspicious region together with its closest normal references instead of forcing an automatic normal/anomalous decision.

### Candidate B

Title:
Reference-Consistency Agent for Shift-Resilient PatchCore Inspection

Core proposal:
Wrap frozen PatchCore with an agentic retrieval-and-audit loop. For each connected high-score region in the PatchCore heatmap, retrieve top-k normal patches from the memory bank and compute a reference-consistency score from PatchCore feature distance dispersion, local texture-statistic similarity, spatial/category metadata validity, and optional WinCLIP/CLIP semantic agreement when a VLM embedding is available. The agent audits the memory bank by accumulating per-reference reliability statistics: references are downweighted if they repeatedly appear as nearest neighbors for regions later judged anomalous, have outlier distances to other normal references, or fail category/metadata checks. Candidate regions are accepted, downweighted, or escalated using anomaly score, cross-reference agreement, calibrated uncertainty, and an explicit evidence bundle containing the region, nearest references, and audit status.

Motivation or baseline weakness:
PatchCore relies on a nearest-neighbor normal memory bank, so normal-reference shift or contaminated normal references can create false anomaly heatmaps and unsupported inspection decisions; the heatmap alone also does not explain why retrieved normal evidence is valid.

Mechanism or approach:
A lightweight reference-consistency and memory-bank audit wrapper around frozen PatchCore features, with optional frozen CLIP/WinCLIP embeddings for semantic consistency; no defect-label training is required beyond threshold calibration on normal validation images and injected-contamination validation splits.
Use a calibrated regional decision score: adjusted_score(region)=PatchCoreScore(region)-lambda*ReferenceConsistency(region)+gamma*ReferenceUnreliability(region). ReferenceConsistency is high when multiple valid normal references agree with the test patch, while ReferenceUnreliability is high when the retrieved references are audit outliers or suspected contaminants. Optimize thresholds to reduce false positives at matched image-level recall, with abstention/escalation when uncertainty or reference unreliability exceeds a calibrated bound.

Experiment and implementation plan:
PatchCore; PaDiM; WinCLIP; non-agent PatchCore plus static normal memory; PatchCore with random reference retrieval report only
MVTec_AD normal train/test images with masks for evaluation; VisA normal train/test images with masks for evaluation; synthetic reference-bank contamination created by injecting a fixed fraction of anomalous test images into the normal bank without using their labels for scoring; synthetic reference-shift splits created by replacing part of the normal bank with visually similar but category-mismatched normal images; normal-only validation images for calibration of consistency, audit, and escalation thresholds
build_patchcore_memory_bank.py; retrieve_reference_patches.py; compute_retrieval_consistency.py; audit_reference_bank.py; calibrate_selective_policy.py; run_agent_inspection_loop.py; evaluate_detection_localization_agent_metrics.py; generate_structured_report.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; f1_score; mask_iou; defect_region_precision; defect_region_recall; false_alarm_reduction; tool_success_rate; evidence_grounding_score; human_escalation_precision; calibration_error; selective_risk
remove retrieval consistency score and use PatchCore score only; remove memory-bank audit while keeping retrieved-reference evidence; use random normal references instead of nearest normal patches; use only feature-distance consistency without texture or semantic consistency; use only optional CLIP/WinCLIP semantic consistency without PatchCore feature consistency; vary injected contamination rate in the normal memory bank; vary selective escalation threshold at matched image-level recall
agent retrieves references and writes a report but the retrieval consistency and audit scores are not allowed to change anomaly scores or escalation decisions; memory bank is deliberately shuffled across product categories to test whether the agent detects invalid references rather than treating them as valid evidence; normal validation images are passed through the full agent loop and should not produce defect reports except as calibrated abstentions
at matched image-level recall, reduce false positive rate by at least 10 percent relative to PatchCore on MVTec_AD or VisA; maintain pixel_level_auroc and pro_score within 1 point of PatchCore while improving defect_region_precision by at least 5 percent; detect injected contaminated reference images with AUROC above 0.75; improve evidence_grounding_score and tool_success_rate over the retrieval-report-only negative control; failure if localization drops by more than 2 pro_score points or if false_alarm_reduction is achieved mainly by excessive escalation above a predeclared coverage floor

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W4404704036

Risks, controls, or fallback:
Risk: retrieval consistency may suppress true subtle defects that resemble normal texture, especially when the normal bank is broad or partly contaminated. Fallback: do not force suppression for low-margin regions; instead use selective prediction, report both the suspicious region and closest normal references, and escalate cases with high anomaly score but high reference consistency.

---

## Item 5: HUM-c8e7b27925

类型：`portfolio`

### Candidate A

Idea 1
Title:
Reference-Bank Audit Agent for Shift-Robust Industrial Anomaly Detection

Core proposal:
Develop an agentic inspection workflow that treats the normal reference bank as an inspectable, fallible memory rather than a fixed clean training set. The agent retrieves normal patches for each suspicious test region, estimates retrieval consistency, audits the reference bank for factory shift or contamination, and only then commits to an anomaly mask, score, and structured report. The core research question is whether explicit reference-bank auditing reduces false positives from normal-reference shift and false negatives caused by contaminated memory banks while preserving strong localization performance.

Motivation or baseline weakness:
PatchCore, PaDiM, FastFlow, and related memory-based industrial anomaly detectors can be strong on MVTec AD and VisA, but their nearest-neighbor evidence is fragile when the normal bank contains shifted lighting, new fixtures, or rare contaminated examples. Existing agentic or VLM-based approaches improve semantic flexibility, but they often do not verify whether retrieved normal evidence is trustworthy. This proposal targets the gap between retrieval-augmented inspection and reliable manufacturing deployment: the agent must know when its own normal references are invalid and escalate instead of producing unsupported defect descriptions.

Mechanism or approach:
Use a frozen IAD ensemble consisting of PatchCore, PaDiM, and WinCLIP or AnomalyCLIP as direct detectors. The agent exposes tools for anomaly heatmap generation, patch retrieval, normal-bank clustering, candidate mask generation with SAM or SAM2, region-level cross-model scoring, VLM report drafting, and report verification. For every candidate anomalous region, the agent stores a retrieval state containing top-k normal patches, source image ids, embedding distances, lighting/color statistics, category metadata, and whether the retrieved patches are themselves suspicious under leave-one-out scoring. The new component is a contaminated-reference and shift audit module that computes: retrieval consistency between the test region and top-k normal patches, normal-bank internal outlierness, agreement between memory-based and CLIP-based anomaly scores, and a bank-shift score estimated from category-level embedding distribution drift. The verification loop first removes or downweights suspicious reference patches, recomputes anomaly scores, asks whether the predicted mask is stable under audited versus unaudited memory, and checks that each report claim links to a region and at least one clean normal reference. The confidence calibration module maps anomaly score, mask stability, retrieval consistency, and cross-model disagreement into calibrated confidence and selective-risk estimates. The escalation policy refuses final defect typing and routes to human review when reference contamination, reference shift, or detector disagreement exceeds learned thresholds. The structured report schema includes anomaly_score, anomaly_mask_or_region, defect_type, evidence, normal_reference_used, confidence, recommended_action, and failure_warning.

Experiment and implementation plan:
Datasets: start with MVTec AD and VisA; optionally test transfer on MVTec LOCO, BTAD, and MPDD. Construct controlled reference-bank corruption by injecting a small percentage of anomalous training images or shifted normal images into the normal bank, and construct factory-shift proxies using illumination, color temperature, blur, camera crop, and background perturbations applied only to subsets of normal references. Direct baselines: PatchCore, PaDiM, FastFlow, WinCLIP, and AnomalyCLIP. Transfer baselines: SAM or SAM2 for segmentation proposals, CLIP or Qwen-VL/LLaVA for report drafting. Negative controls: same IAD ensemble without the agent audit, same retrieval without contamination detection, same SAM refinement without evidence-based mask selection, and same report generator without grounded claim checking. Metrics: image-level AUROC, pixel-level AUROC, AUPR, PRO score, F1, mask IoU, defect-region precision, defect-region recall, calibration error, selective risk, out-of-distribution detection of shifted references, false-alarm reduction at matched recall, tool success rate, report correctness, evidence-grounding score, and human-escalation precision. Ablations: top-k retrieval size, reference-bank audit thresholds, cross-model disagreement features, use of leave-one-out normal outlierness, selective prediction threshold, VLM report checker on/off, and human-escalation policy on/off. MVP artifacts: audited memory-bank builder, retrieval-state logger, region scorer, report checker, calibration notebook, and benchmark scripts for clean, shifted, and contaminated banks. Failure criteria: the method fails if agent workflow metrics do not improve over the non-agent ensemble, if false-alarm reduction at matched recall is not improved under reference shift, if contaminated-reference detection is near random, or if localization metrics drop materially relative to PatchCore under clean-bank conditions. Implementation plan: first reproduce PatchCore and PaDiM on MVTec AD and VisA; second add retrieval-state logging and leave-one-out reference scoring; third implement the audit module and recompute heatmaps with downweighted references; fourth add SAM/SAM2 candidate masks selected by audited heatmap overlap and negative-control rejection; fifth add the structured report generator and evidence-grounded checker; sixth fit calibration and escalation thresholds on validation categories; seventh evaluate clean, shifted, and contaminated-bank regimes.

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W4404704036; openalex:W7154655652; openalex:W4380551232

---

Idea 2
Title:
Disagreement-Guided Mask Verification Agent for Weakly Labeled IAD

Core proposal:
Create an agentic anomaly localization system for settings with weak or missing pixel-level defect labels. Instead of assuming that a heatmap or SAM mask is correct, the agent proposes multiple candidate regions, scores each with cross-model disagreement and normal-reference consistency, rejects masks that also explain normal negative controls, and produces a calibrated anomaly mask plus evidence-grounded report. The main novelty is a mask selection and verification policy that turns frozen IAD models and promptable segmentation into a self-checking region inspector.

Motivation or baseline weakness:
Industrial datasets often have image-level labels but sparse or noisy masks, making it difficult to train supervised segmenters such as Mask2Former or evaluate VLM region descriptions. Heatmap-based IAD models can highlight texture or lighting variation rather than true defects, while SAM/SAM2 may segment salient object parts rather than defect regions. A publishable gap is to study whether an agent can improve region selection and reporting reliability without large-scale defect annotation by using negative controls, model disagreement, and retrieval-grounded evidence.

Mechanism or approach:
Run frozen PatchCore, RD4AD, DRAEM, and AnomalyCLIP or WinCLIP to produce complementary anomaly maps and semantic anomaly scores. Generate candidate regions using thresholded IAD heatmaps, connected components, SAM/SAM2 prompts from high-score points, and optional GroundingDINO prompts derived from a defect taxonomy. The agent maintains memory over candidate masks, associated detector scores, retrieved normal patches, candidate-mask provenance, negative-control scores on visually similar normal images, and report claims. The new component is a disagreement-guided mask verification policy: a candidate mask is accepted only if it has high anomaly evidence, stable support across at least one texture-sensitive and one semantic detector, low activation on retrieved normal negative controls, and better explanation quality than object-part masks proposed by SAM/SAM2. Cross-model disagreement is not treated as failure by default; high disagreement triggers either extra retrieval, alternative mask prompts, or human escalation. The VLM report module can describe the defect only after a checker verifies that each textual claim is grounded in accepted regions and retrieved normal references. Confidence calibration uses detector agreement, negative-control rejection margin, mask stability under prompt perturbation, and evidence-grounding score. The escalation policy sends cases to human review when mask candidates are unstable, when semantic defect labels are unsupported by the region evidence, or when the best mask also fires on normal controls.

Experiment and implementation plan:
Datasets: MVTec AD and VisA first, using full masks only for evaluation while training/tuning with image-level labels or sparse point/bbox labels; extend to MVTec LOCO for logical anomalies and MPDD or BTAD for manufacturing variation. Direct baselines: PatchCore, RD4AD, DRAEM, WinCLIP, AnomalyCLIP, SAM/SAM2 refinement without verification, and Mask2Former trained where masks are available. Transfer baselines: CLIP, GroundingDINO, Qwen-VL or LLaVA report generation without grounded checking. Negative controls: remove the agentic verification loop, remove normal negative-control testing, use SAM2 refinement without mask selection, use single-model heatmaps only, and allow VLM defect descriptions without evidence checking. Metrics: image-level AUROC, pixel-level AUROC, AUPR, PRO score, F1, mask IoU, defect-region precision, defect-region recall, false-alarm reduction, tool success rate, report correctness, evidence-grounding score, human-escalation precision, calibration error, and selective risk. Ablations: detector ensemble composition, disagreement threshold, number of retrieved normal controls, SAM prompt perturbation count, candidate-ranking features, taxonomy-guided versus taxonomy-free defect typing, and calibration method. MVP artifacts: candidate-mask generator, mask provenance table, negative-control evaluator, disagreement scorer, region-grounded report checker, selective escalation module, and evaluation scripts for weak-label regimes. Failure criteria: the idea fails if mask IoU or PRO does not improve over the best non-agent heatmap baseline, if negative-control testing does not reduce false-positive texture/lighting heatmaps, if report grounding is not better than direct VLM reporting, or if human-escalation precision is worse than a simple uncertainty threshold. Implementation plan: first run frozen IAD baselines and produce heatmaps; second implement candidate generation from heatmaps and SAM/SAM2 point prompts; third retrieve visually similar normal references and compute negative-control activations; fourth rank masks with the disagreement-guided policy; fifth add structured report generation constrained to accepted masks; sixth add a verifier that links claims to mask ids and normal references; seventh calibrate selective prediction and evaluate weak-label and full-label settings separately.

Evidence paper IDs:
openalex:W7153670799; openalex:W7154655652; openalex:W7162893906; openalex:W4415239807; openalex:W4380551232; openalex:W7153328271

---

Idea 3
Title:
Selective Inspection Agent for False-Alarm Reduction and Human Escalation

Core proposal:
Design a selective prediction agent for manufacturing inspection that optimizes when to accept, reject, or escalate an anomaly decision under fixed recall requirements. The agent coordinates frozen IAD detectors, retrieval of normal references, region verification, uncertainty calibration, report checking, and human-in-the-loop escalation. The contribution is not another anomaly score, but an inspection policy that reduces false alarms and unsupported reports while preserving detection recall and providing auditable escalation decisions.

Motivation or baseline weakness:
Many IAD methods report AUROC and pixel localization, but production systems also need calibrated confidence, selective risk, and clear escalation. A detector that produces many false alarms from benign texture, lighting, or reference shift can be unusable even with high AUROC. VLM-based reports add another risk: plausible but unsupported defect descriptions. This idea targets the deployment gap by evaluating the full agent workflow using tool success rate, evidence grounding, report correctness, false-alarm reduction, and human-escalation precision, rather than claiming agent improvement from detection metrics alone.

Mechanism or approach:
Use PatchCore, FastFlow, PaDiM, and AnomalyCLIP or WinCLIP as frozen anomaly detectors. The agent has tools for detector inference, normal-reference retrieval, candidate-region extraction, optional SAM/SAM2 mask proposal with evidence-based selection, defect-taxonomy lookup, VLM report drafting, report verification, calibration, and escalation. The memory state stores the inspection trace: input product category, inspection goal, detector heatmaps, candidate regions, retrieved references, cross-model disagreement, reference-shift indicators, claim-to-region links, confidence estimates, and final action. The new component is a selective inspection policy optimized for false-alarm reduction at matched recall. It learns or tunes thresholds over calibrated features including anomaly score, region size, retrieval consistency, detector disagreement, report-grounding score, normal-reference shift score, and mask stability. The verification loop has three gates: visual evidence gate, reference consistency gate, and report support gate. If any gate fails, the agent either requests another tool pass or escalates with a failure_warning rather than inventing a defect type. Recommended actions are constrained to pass, reject, re-image, clean lens/lighting check, process hold, or human review. This directly addresses when to escalate to a human and when to refuse unsupported VLM descriptions.

Experiment and implementation plan:
Datasets: MVTec AD and VisA as the minimum viable benchmark; add MVTec LOCO to test logical anomalies and optional video or multiview only if proxy construction is explicit, such as treating repeated captures or synthetic viewpoint/illumination perturbations as inspection passes and validating that they preserve labels. Direct baselines: PatchCore, PaDiM, FastFlow, WinCLIP, AnomalyCLIP, and a non-agent ensemble with score averaging. Transfer baselines: CLIP-based report generation, Qwen-VL or LLaVA report generation, SAM/SAM2 region proposal, and retrieval-augmented generation without verification. Negative controls: no selective policy, uncertainty threshold using anomaly score only, agent without report checker, agent without retrieval consistency, and agent with random escalation at the same escalation budget. Metrics: image-level AUROC, pixel-level AUROC, AUPR, PRO score, F1, mask IoU, defect-region precision, defect-region recall, false-alarm reduction at matched recall, calibration error, selective risk, out-of-distribution detection for shifted inputs, tool success rate, report correctness, evidence-grounding score, and human-escalation precision. Ablations: matched-recall target, escalation budget, calibration features, detector disagreement feature, retrieval consistency feature, report checker on/off, allowed action set, and category-specific versus shared thresholds. MVP artifacts: frozen-detector ensemble runner, inspection-trace JSON schema, calibrated selective-policy module, report verifier, human-escalation simulator using labels as oracle, and dashboards for false alarms versus recall. Failure criteria: the method fails if it does not reduce false alarms over the non-agent ensemble at the same recall, if selective risk is not lower than anomaly-score thresholding, if report correctness or evidence-grounding does not improve over direct VLM reports, or if escalation precision is no better than random escalation under the same review budget. Implementation plan: first establish detector and report-generation baselines on MVTec AD and VisA; second build the inspection trace and structured report schema; third compute calibration features from retrieval, disagreement, and mask stability; fourth train or tune the selective policy on validation categories; fifth implement refusal and escalation logic with explicit failure_warning outputs; sixth evaluate under clean, lighting-shifted, and reference-shifted settings; seventh run ablations and negative controls to isolate the agentic contribution.

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W4404704036; openalex:W7153328271; openalex:W7138099583; openalex:W4380551232; openalex:W7154655652

### Candidate B

Idea 1
Title:
Reference-Consistency Agent for Shift-Resilient PatchCore Inspection

Core proposal:
Wrap frozen PatchCore with an agentic retrieval-and-audit loop. For each connected high-score region in the PatchCore heatmap, retrieve top-k normal patches from the memory bank and compute a reference-consistency score from PatchCore feature distance dispersion, local texture-statistic similarity, spatial/category metadata validity, and optional WinCLIP/CLIP semantic agreement when a VLM embedding is available. The agent audits the memory bank by accumulating per-reference reliability statistics: references are downweighted if they repeatedly appear as nearest neighbors for regions later judged anomalous, have outlier distances to other normal references, or fail category/metadata checks. Candidate regions are accepted, downweighted, or escalated using anomaly score, cross-reference agreement, calibrated uncertainty, and an explicit evidence bundle containing the region, nearest references, and audit status.

Motivation or baseline weakness:
PatchCore relies on a nearest-neighbor normal memory bank, so normal-reference shift or contaminated normal references can create false anomaly heatmaps and unsupported inspection decisions; the heatmap alone also does not explain why retrieved normal evidence is valid.

Mechanism or approach:
A lightweight reference-consistency and memory-bank audit wrapper around frozen PatchCore features, with optional frozen CLIP/WinCLIP embeddings for semantic consistency; no defect-label training is required beyond threshold calibration on normal validation images and injected-contamination validation splits.
Use a calibrated regional decision score: adjusted_score(region)=PatchCoreScore(region)-lambda*ReferenceConsistency(region)+gamma*ReferenceUnreliability(region). ReferenceConsistency is high when multiple valid normal references agree with the test patch, while ReferenceUnreliability is high when the retrieved references are audit outliers or suspected contaminants. Optimize thresholds to reduce false positives at matched image-level recall, with abstention/escalation when uncertainty or reference unreliability exceeds a calibrated bound.

Experiment and implementation plan:
PatchCore; PaDiM; WinCLIP; non-agent PatchCore plus static normal memory; PatchCore with random reference retrieval report only
MVTec_AD normal train/test images with masks for evaluation; VisA normal train/test images with masks for evaluation; synthetic reference-bank contamination created by injecting a fixed fraction of anomalous test images into the normal bank without using their labels for scoring; synthetic reference-shift splits created by replacing part of the normal bank with visually similar but category-mismatched normal images; normal-only validation images for calibration of consistency, audit, and escalation thresholds
build_patchcore_memory_bank.py; retrieve_reference_patches.py; compute_retrieval_consistency.py; audit_reference_bank.py; calibrate_selective_policy.py; run_agent_inspection_loop.py; evaluate_detection_localization_agent_metrics.py; generate_structured_report.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; f1_score; mask_iou; defect_region_precision; defect_region_recall; false_alarm_reduction; tool_success_rate; evidence_grounding_score; human_escalation_precision; calibration_error; selective_risk
remove retrieval consistency score and use PatchCore score only; remove memory-bank audit while keeping retrieved-reference evidence; use random normal references instead of nearest normal patches; use only feature-distance consistency without texture or semantic consistency; use only optional CLIP/WinCLIP semantic consistency without PatchCore feature consistency; vary injected contamination rate in the normal memory bank; vary selective escalation threshold at matched image-level recall
agent retrieves references and writes a report but the retrieval consistency and audit scores are not allowed to change anomaly scores or escalation decisions; memory bank is deliberately shuffled across product categories to test whether the agent detects invalid references rather than treating them as valid evidence; normal validation images are passed through the full agent loop and should not produce defect reports except as calibrated abstentions
at matched image-level recall, reduce false positive rate by at least 10 percent relative to PatchCore on MVTec_AD or VisA; maintain pixel_level_auroc and pro_score within 1 point of PatchCore while improving defect_region_precision by at least 5 percent; detect injected contaminated reference images with AUROC above 0.75; improve evidence_grounding_score and tool_success_rate over the retrieval-report-only negative control; failure if localization drops by more than 2 pro_score points or if false_alarm_reduction is achieved mainly by excessive escalation above a predeclared coverage floor

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W4404704036

Risks, controls, or fallback:
Risk: retrieval consistency may suppress true subtle defects that resemble normal texture, especially when the normal bank is broad or partly contaminated. Fallback: do not force suppression for low-margin regions; instead use selective prediction, report both the suspicious region and closest normal references, and escalate cases with high anomaly score but high reference consistency.

---

Idea 2
Title:
Disagreement-Guided Mask Selection Agent for Weak-Label Anomaly Localization

Core proposal:
Use an agent to turn anomaly heatmaps and text/box/point prompts into multiple SAM/SAM2 candidate masks, then select or abstain using explicit evidence tests. The agent keeps a candidate mask only if it overlaps high-confidence anomaly evidence from at least one frozen IAD model, is not similarly activated on retrieved normal reference regions, passes a normal-region negative prompt test, and has sufficient support under cross-model comparison. Cross-model disagreement is used as an uncertainty signal rather than as a direct defect label: strong disagreement triggers escalation unless one candidate has a calibrated margin over alternatives. The final output is a selected mask, confidence, evidence links to heatmaps/references, or a refusal on normal images.

Motivation or baseline weakness:
SAM or SAM2 can produce salient object masks that do not correspond to actual defect regions, while industrial anomaly heatmaps from PatchCore, RD4AD, AnomalyCLIP, or WinCLIP can be noisy under texture, lighting, and prompt variation, especially when pixel-level labels are sparse or unavailable for calibration.

Mechanism or approach:
A mask-selection and abstention policy that ranks frozen SAM/SAM2 candidate masks using heatmap overlap, retrieved-normal contradiction, cross-model support, negative-control activation, and calibrated margin; segmentation backbones and IAD models remain frozen.
Select mask m maximizing S(m)=alpha*IADHeatmapOverlap(m)+beta*CrossModelSupport(m)-delta*NormalReferenceSupport(m)-eta*NegativeControlActivation(m)-rho*MaskInstability(m). Abstain or escalate when the best-vs-second-best score margin is below a calibrated threshold or when normal-image negative controls activate strongly. Calibrate all thresholds with image-level labels or a small validation mask subset, and reserve test masks only for evaluation.

Experiment and implementation plan:
SAM; SAM2; PatchCore; RD4AD; AnomalyCLIP; WinCLIP; heatmap-threshold baseline without SAM; SAM/SAM2 largest-mask baseline
MVTec_AD images with pixel masks for evaluation; VisA images with pixel masks for evaluation; normal reference images from each product category; weak-label calibration split using only image-level anomaly labels unless a small mask-calibration setting is explicitly tested; optional defect taxonomy for report labels when available, not required for mask scoring
run_iad_heatmaps.py; generate_sam_candidates_from_heatmap_prompts.py; retrieve_normal_reference_regions.py; score_candidate_masks.py; run_negative_control_prompts.py; calibrate_mask_abstention.py; evaluate_mask_and_agent_metrics.py; render_region_grounded_report.py
pixel_level_auroc; pro_score; mask_iou; defect_region_precision; defect_region_recall; image_level_auroc; aupr; f1_score; tool_success_rate; evidence_grounding_score; report_correctness; human_escalation_precision; selective_risk
replace calibrated mask selection with largest SAM/SAM2 mask; remove negative-control normal-region prompt test; remove retrieved-normal contradiction term; remove cross-model disagreement and use one IAD heatmap only; compare SAM versus SAM2 using the identical selection policy; calibrate with image-level labels only versus a small labeled-mask subset; remove abstention and force a mask for every image
SAM/SAM2 refinement with no mask-selection policy, using the largest or highest-stability mask; random heatmap peak prompts matched for number of SAM/SAM2 calls; normal-image prompts where the agent should refuse to output a defect mask; permuted heatmaps paired with correct images to verify that selected masks depend on anomaly evidence rather than salient-object bias
improve mask_iou or pro_score by at least 5 percent over heatmap-threshold PatchCore or RD4AD on at least two MVTec_AD or VisA categories; reduce false defect masks on normal images by at least 10 percent at matched defect_region_recall; achieve higher evidence_grounding_score than SAM/SAM2 without a selection policy; maintain or improve image_level_auroc relative to the underlying heatmap model used for prompting; failure if SAM/SAM2 improves localization metrics only by increasing normal-image false alarms, or if tool_success_rate is not better than negative controls

Evidence paper IDs:
openalex:W4380551232; openalex:W7154655652; openalex:W7162893906; openalex:W7153328271

Risks, controls, or fallback:
Risk: cross-model disagreement can be high for small true defects, causing over-escalation or rejection of valid masks. Fallback: use a two-tier policy where small high-contrast regions are reported as low-confidence suspected defects with mandatory human review, while the system preserves the candidate mask and evidence bundle instead of suppressing it.

---

Idea 3
Title:
Evidence-Grounded Report Checker with Selective Human Escalation

Core proposal:
Add a report-checking agent after frozen IAD/VLM prediction. The checker parses each structured report into claims such as anomaly_present, defect_region, defect_type, severity, and recommended_action, then verifies each claim against region masks, anomaly heatmaps, retrieved normal references, and an optional category-specific defect taxonomy. Each claim is labeled grounded, contradicted, unsupported, or out-of-taxonomy. Unsupported defect_type, severity, or recommended_action fields are not emitted as confident facts; they trigger refusal, unknown-defect wording, or human escalation. The checker returns a structured report only when visual grounding, normal-reference contrast, and calibrated confidence satisfy predeclared thresholds.

Motivation or baseline weakness:
WinCLIP, AnomalyCLIP, CLIP-style scoring, and VLM-based inspection agents can assign semantic defect descriptions that are prompt-sensitive and not supported by localized visual evidence, leading to confident but unsupported manufacturing reports.

Mechanism or approach:
A claim-to-evidence verifier that links structured report fields to image regions and retrieved references, plus a calibration layer for confidence and escalation decisions; it uses frozen IAD/VLM outputs with deterministic rules or a small validation-fitted verifier trained only on report-grounding labels.
Minimize expected selective risk over structured reports. Accept a report only if anomaly confidence, localization evidence, normal-reference contrast, taxonomy validity, and claim-grounding scores exceed calibrated thresholds; otherwise escalate with an evidence bundle instead of producing unsupported defect descriptions. Optimize at a fixed coverage target so gains cannot come only from refusing most cases.

Experiment and implementation plan:
WinCLIP; AnomalyCLIP; CLIP; PatchCore; tool_using_agent; retrieval_augmented_generation; VLM report generator without verification; anomaly-score-only escalation
MVTec_AD or VisA images with anomaly labels and masks for grounding evaluation; normal reference images for visual contrast evidence; optional defect taxonomy converted to an allowed defect_type vocabulary per category; human or template-generated structured report labels for a small validation subset; synthetic unsupported-claim reports created by swapping defect types, regions, severities, or recommended actions; held-out normal images for refusal and false-report evaluation
run_iad_and_vlm_predictions.py; retrieve_normal_evidence.py; generate_structured_inspection_report.py; verify_claim_region_links.py; score_evidence_grounding.py; calibrate_escalation_policy.py; evaluate_report_and_detection_metrics.py; create_unsupported_claim_negative_set.py
image_level_auroc; pixel_level_auroc; aupr; f1_score; mask_iou; defect_region_precision; defect_region_recall; report_correctness; evidence_grounding_score; false_alarm_reduction; human_escalation_precision; calibration_error; selective_risk; tool_success_rate
remove claim-level evidence checker; remove normal-reference retrieval from the checker; remove defect-taxonomy constraint and allow free-form defect descriptions; use anomaly score confidence without calibration; escalate by fixed anomaly-score threshold instead of selective risk optimization; compare region-grounded report generation versus image-only VLM report generation; disable claim-type-specific decisions and use one global report confidence score
VLM generates a fluent report from the image and anomaly score but cannot inspect masks or references; checker receives randomly permuted region masks to test whether grounding scores fall; defect taxonomy is intentionally mismatched across categories to test refusal behavior; synthetic swapped-claim reports are evaluated without access to the original correct claim to prevent leakage
increase evidence_grounding_score by at least 15 percent over a VLM report generator without verification; reduce unsupported defect_type claims by at least 20 percent on synthetic swapped-claim tests; maintain image_level_auroc within 1 point of the strongest IAD baseline used for anomaly scoring while improving human_escalation_precision; achieve lower selective_risk than anomaly-score-only escalation at matched recall and at a predeclared coverage point such as 70 percent; failure if report_correctness improves only by refusing most cases, or if localization-grounded claims do not outperform the image-only VLM negative control

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W7154655652; openalex:W7153328271; openalex:W7138099583

Risks, controls, or fallback:
Risk: report verification may depend on imperfect masks and overly conservative taxonomy constraints. Fallback: separate visual grounding confidence from semantic defect-typing confidence, allowing the system to localize and escalate an unknown defect rather than forcing a specific defect_type or recommended_action.

---

## Item 6: HUM-fa1f6cdf8b

类型：`single_idea`

### Candidate A

Title:
Evidence-Grounded Report Checker with Selective Human Escalation

Core proposal:
Introduce an evidence-grounded report checker that validates every report claim before release. The checker receives candidate anomaly regions from IAD tools, retrieved same-category normal references, a restricted defect taxonomy when available, and cross-model heatmap or semantic agreement scores. It drafts or receives a structured inspection report, decomposes it into atomic claims, checks whether each claim is supported by a linked anomaly region and a normal-reference contrast, and then accepts, revises unsupported claims to a weaker evidence-supported form, or escalates/refuses. Agent steps: run IAD and VLM-style tools, retrieve normal references, draft a structured report, verify each claim-to-region/reference link, calibrate confidence, and apply selective escalation optimized for false-alarm reduction at matched anomaly recall.

Motivation or baseline weakness:
WinCLIP, AnomalyCLIP, and VLM-style inspection agents may generate plausible defect descriptions that are unsupported by localized visual evidence. This can produce misleading inspection reports and poor human escalation decisions even when image-level anomaly scores are reasonable.

Mechanism or approach:
A Claim-Region-Reference Verifier that parses the report schema into atomic claims {defect_type, location, visual_evidence, normal_reference_used, severity, recommended_action}, checks whether each claim has localized region support, normal-reference contrast, and taxonomy compatibility, and returns unsupported_claim_flags plus calibrated release, revise, or escalation decisions.
Minimize unsupported report claims and selective risk by optimizing a release policy over anomaly score, localization confidence, cross-model disagreement, and claim-verification score. The policy is constrained to maintain target anomaly recall, improve human_escalation_precision, and reduce false releases of reports whose defect type, location, or evidence link is contradicted by the available region evidence.

Experiment and implementation plan:
WinCLIP; AnomalyCLIP; PatchCore; Unverified VLM inspection report agent; IAD heatmap plus template report; Retrieval-augmented report generation without claim verification
MVTec_AD and VisA image-level and pixel-level anomaly data; Optional defect taxonomy converted into allowed report labels for each product category; Normal reference images for region-to-reference contrast; Human- or rule-constructed report correctness labels for a small validation subset; Automatically generated counterfactual reports with wrong defect type, wrong region, missing evidence, swapped normal references, or unsupported severity/action claims for checker training and evaluation
run_iad_and_vlm_baselines.py; retrieve_normal_references.py; draft_structured_reports.py; create_counterfactual_report_claims.py; verify_claim_region_reference_links.py; calibrate_escalation_policy.py; evaluate_report_correctness_grounding.py; evaluate_selective_detection.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; mask_iou; report_correctness; evidence_grounding_score; false_alarm_reduction; human_escalation_precision; tool_success_rate; calibration_error; selective_risk; defect_region_precision; defect_region_recall
Remove claim-region-reference verifier; Remove retrieved normal references from verification; Use VLM self-critique without access to anomaly masks or heatmaps; Use cross-model disagreement only without report checking; Use fixed confidence threshold instead of calibrated selective policy; Disable refusal and escalation and force a report for every sample; Allow free-form defect labels instead of the restricted taxonomy or unknown-anomaly fallback
Feed reports with deliberately swapped defect locations and require the checker to reject or revise them; Feed reports with correct anomaly score but unsupported defect type and require revision or escalation; Generate reports from normal images with no anomaly evidence and measure false release rate; Swap normal references across product categories and require the checker to flag unsupported reference contrast; Provide reports with correct region but exaggerated severity or unsupported recommended action and require claim-level rejection
Improve report_correctness by at least 15% over VLM-style report generation without evidence checking; Achieve evidence_grounding_score of at least 0.85 on accepted reports; Reduce false alarms by at least 10% at matched image-level recall compared with the strongest direct IAD baseline plus unverified report; Improve human_escalation_precision by at least 10% while keeping selective_risk no worse than the non-agent baseline; If evidence_grounding_score and tool_success_rate do not improve over the negative-control unverified agent, the idea fails

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W7154655652; openalex:W7153328271; openalex:W7138099583

Risks, controls, or fallback:
Risk: automatic report labels may be noisy, VLM descriptions may not match dataset taxonomies, and checker training on synthetic counterfactuals may miss real human-report errors. Fallback: restrict output to a small allowed defect taxonomy plus an 'unknown anomaly' class, prioritize region/reference evidence over free-form semantic naming, and escalate whenever defect type or recommended action is not directly supported by localized evidence.

### Candidate B

Title:
Evidence-Grounded Report Checker with Selective Human Escalation

Core proposal:
Introduce an evidence-grounded report checker that validates each structured report claim against linked anomaly regions, retrieved normal references, allowed defect labels, and cross-model localization evidence before release. The agent drafts or receives a report, decomposes it into atomic claims, verifies whether each claim is supported by visual evidence and reference contrast, then accepts, revises, or escalates with calibrated confidence.

Motivation or baseline weakness:
WinCLIP, AnomalyCLIP, and VLM-style inspection agents can produce plausible defect descriptions that are not supported by localized visual evidence. This can mislead downstream users even when the underlying anomaly score or heatmap is useful, especially if escalation decisions depend on the generated report.

Mechanism or approach:
A Claim-Region-Reference Verifier that parses reports into atomic claims {defect_type, location, visual_evidence, normal_reference_used, recommended_action}, checks each claim for localized region support and normal-reference contrast, and returns unsupported_claim_flags plus calibrated release, revision, or escalation decisions.
Minimize unsupported report claims and selective risk by learning a release policy over anomaly score, localization confidence, cross-model disagreement, and claim-verification score, subject to maintaining a target anomaly recall and improving human escalation precision.

Experiment and implementation plan:
WinCLIP; AnomalyCLIP; PatchCore; LLaVA; Qwen-VL; tool_using_agent; retrieval_augmented_generation
MVTec_AD and VisA image-level and pixel-level anomaly data; Optional defect taxonomy converted into allowed report labels; Normal reference images for region-to-reference contrast; Small validation subset with human- or rule-constructed report correctness labels; Counterfactual reports with wrong defect type, wrong region, missing evidence, or unsupported action recommendation for checker evaluation
run_iad_and_vlm_baselines.py; retrieve_normal_references.py; draft_structured_reports.py; create_counterfactual_report_claims.py; verify_claim_region_reference_links.py; calibrate_escalation_policy.py; evaluate_report_correctness_grounding.py; evaluate_selective_detection.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; mask_iou; report_correctness; evidence_grounding_score; false_alarm_reduction; human_escalation_precision; tool_success_rate; confidence; calibration_error; selective_risk
Remove the claim-region-reference verifier; Remove retrieved normal references from verification; Use VLM self-critique without anomaly masks or linked regions; Use cross-model disagreement without report-level checking; Use a fixed confidence threshold instead of a calibrated selective policy; Disable refusal and escalation so every sample receives a released report
Feed reports with deliberately swapped defect locations and require the checker to reject or revise them; Feed reports with correct anomaly scores but unsupported defect types and require revision or escalation; Generate reports from normal images with no anomaly evidence and measure false release rate
Improve report_correctness by at least 15% over VLM report generation without evidence checking; Achieve evidence_grounding_score of at least 0.85 on accepted reports; Reduce false alarms by at least 10% at matched image-level recall compared with the best direct IAD baseline plus unverified report; Improve human_escalation_precision by at least 10% while keeping selective_risk no worse than the non-agent baseline; If evidence_grounding_score and tool_success_rate do not improve over the unverified agent, treat the idea as unsuccessful

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W7154655652; openalex:W7153328271; openalex:W7138099583

Risks, controls, or fallback:
Risk: automatically generated report labels can be noisy, and free-form VLM descriptions may not align with dataset taxonomies. Fallback: restrict outputs to a compact allowed defect taxonomy plus an unknown-anomaly class, and prioritize region/reference evidence over semantic naming when confidence is low.

---

## Item 7: HUM-86495bbbe7

类型：`single_idea`

### Candidate A

Title:
Disagreement-Guided Mask Selection Agent for Weak-Label Anomaly Localization

Core proposal:
Use an agent to turn anomaly heatmaps and text/box/point prompts into multiple SAM/SAM2 candidate masks, then select or abstain using explicit evidence tests. The agent keeps a candidate mask only if it overlaps high-confidence anomaly evidence from at least one frozen IAD model, is not similarly activated on retrieved normal reference regions, passes a normal-region negative prompt test, and has sufficient support under cross-model comparison. Cross-model disagreement is used as an uncertainty signal rather than as a direct defect label: strong disagreement triggers escalation unless one candidate has a calibrated margin over alternatives. The final output is a selected mask, confidence, evidence links to heatmaps/references, or a refusal on normal images.

Motivation or baseline weakness:
SAM or SAM2 can produce salient object masks that do not correspond to actual defect regions, while industrial anomaly heatmaps from PatchCore, RD4AD, AnomalyCLIP, or WinCLIP can be noisy under texture, lighting, and prompt variation, especially when pixel-level labels are sparse or unavailable for calibration.

Mechanism or approach:
A mask-selection and abstention policy that ranks frozen SAM/SAM2 candidate masks using heatmap overlap, retrieved-normal contradiction, cross-model support, negative-control activation, and calibrated margin; segmentation backbones and IAD models remain frozen.
Select mask m maximizing S(m)=alpha*IADHeatmapOverlap(m)+beta*CrossModelSupport(m)-delta*NormalReferenceSupport(m)-eta*NegativeControlActivation(m)-rho*MaskInstability(m). Abstain or escalate when the best-vs-second-best score margin is below a calibrated threshold or when normal-image negative controls activate strongly. Calibrate all thresholds with image-level labels or a small validation mask subset, and reserve test masks only for evaluation.

Experiment and implementation plan:
SAM; SAM2; PatchCore; RD4AD; AnomalyCLIP; WinCLIP; heatmap-threshold baseline without SAM; SAM/SAM2 largest-mask baseline
MVTec_AD images with pixel masks for evaluation; VisA images with pixel masks for evaluation; normal reference images from each product category; weak-label calibration split using only image-level anomaly labels unless a small mask-calibration setting is explicitly tested; optional defect taxonomy for report labels when available, not required for mask scoring
run_iad_heatmaps.py; generate_sam_candidates_from_heatmap_prompts.py; retrieve_normal_reference_regions.py; score_candidate_masks.py; run_negative_control_prompts.py; calibrate_mask_abstention.py; evaluate_mask_and_agent_metrics.py; render_region_grounded_report.py
pixel_level_auroc; pro_score; mask_iou; defect_region_precision; defect_region_recall; image_level_auroc; aupr; f1_score; tool_success_rate; evidence_grounding_score; report_correctness; human_escalation_precision; selective_risk
replace calibrated mask selection with largest SAM/SAM2 mask; remove negative-control normal-region prompt test; remove retrieved-normal contradiction term; remove cross-model disagreement and use one IAD heatmap only; compare SAM versus SAM2 using the identical selection policy; calibrate with image-level labels only versus a small labeled-mask subset; remove abstention and force a mask for every image
SAM/SAM2 refinement with no mask-selection policy, using the largest or highest-stability mask; random heatmap peak prompts matched for number of SAM/SAM2 calls; normal-image prompts where the agent should refuse to output a defect mask; permuted heatmaps paired with correct images to verify that selected masks depend on anomaly evidence rather than salient-object bias
improve mask_iou or pro_score by at least 5 percent over heatmap-threshold PatchCore or RD4AD on at least two MVTec_AD or VisA categories; reduce false defect masks on normal images by at least 10 percent at matched defect_region_recall; achieve higher evidence_grounding_score than SAM/SAM2 without a selection policy; maintain or improve image_level_auroc relative to the underlying heatmap model used for prompting; failure if SAM/SAM2 improves localization metrics only by increasing normal-image false alarms, or if tool_success_rate is not better than negative controls

Evidence paper IDs:
openalex:W4380551232; openalex:W7154655652; openalex:W7162893906; openalex:W7153328271

Risks, controls, or fallback:
Risk: cross-model disagreement can be high for small true defects, causing over-escalation or rejection of valid masks. Fallback: use a two-tier policy where small high-contrast regions are reported as low-confidence suspected defects with mandatory human review, while the system preserves the candidate mask and evidence bundle instead of suppressing it.

### Candidate B

Title:
Disagreement-Guided Mask Selection Agent for Weak-Label Anomaly Localization

Core proposal:
Use an agent to generate multiple candidate masks from heatmap peaks, boxes, and negative prompts, then select masks using cross-model disagreement and negative-control checks. Candidate masks are retained only when they overlap high-confidence anomaly evidence from at least one IAD model, are not equally supported by retrieved normal references, and fail a normal-region negative prompt test. The agent then reports the selected mask with linked evidence and escalates if candidate masks disagree strongly.

Motivation or baseline weakness:
SAM or SAM2 can produce salient object masks that do not correspond to actual defect regions, while IAD heatmaps from PatchCore, RD4AD, or AnomalyCLIP can be noisy under texture and lighting variation, especially when pixel-level labels are sparse or missing.

Mechanism or approach:
A mask selection policy that ranks SAM/SAM2 candidate masks using heatmap agreement, retrieved-normal contradiction, cross-model disagreement, and negative-control scores; the segmentation backbones and IAD models remain frozen.
Select mask m maximizing S(m)=alpha*IADHeatmapOverlap(m)+beta*CrossModelSupport(m)-delta*NormalReferenceSupport(m)-eta*NegativeControlActivation(m), and abstain/escalate when top-2 masks have small margin or disagreement exceeds a calibrated threshold.

Experiment and implementation plan:
SAM; SAM2; PatchCore; RD4AD; AnomalyCLIP; WinCLIP; heatmap-threshold baseline without SAM
MVTec_AD images with pixel masks for first evaluation; VisA images with pixel masks for first evaluation; normal reference images from each product category; weak-label setting using only image-level anomaly labels for calibration and reserving masks only for evaluation; optional defect taxonomy for report labels when available
run_iad_heatmaps.py; generate_sam_candidates_from_heatmap_prompts.py; retrieve_normal_reference_regions.py; score_candidate_masks.py; run_negative_control_prompts.py; calibrate_mask_abstention.py; evaluate_mask_and_agent_metrics.py; render_region_grounded_report.py
pixel_level_auroc; pro_score; mask_iou; defect_region_precision; defect_region_recall; image_level_auroc; aupr; f1_score; tool_success_rate; evidence_grounding_score; report_correctness; human_escalation_precision; selective_risk
replace learned/calibrated mask selection with largest SAM mask; remove negative-control normal-region prompt test; remove retrieved-normal contradiction term; remove cross-model disagreement and use one IAD heatmap only; compare SAM versus SAM2 using identical selection policy; calibrate with image-level labels only versus small labeled-mask subset
SAM/SAM2 refinement with no mask selection policy, using the largest or highest-stability mask; random heatmap peak prompts matched for number of SAM calls; normal-image prompts where the agent should refuse to output a defect mask
improve mask_iou or pro_score by at least 5 percent over heatmap-threshold PatchCore or RD4AD on at least two MVTec_AD or VisA categories; reduce false defect masks on normal images by at least 10 percent at matched defect_region_recall; achieve higher evidence_grounding_score than SAM/SAM2 without selection policy; failure if SAM/SAM2 increases localization metrics but normal-image false alarms also increase, or if tool_success_rate is not better than the negative control

Evidence paper IDs:
openalex:W4380551232; openalex:W7154655652; openalex:W7162893906; openalex:W7153328271

Risks, controls, or fallback:
Risk: cross-model disagreement can be high for small true defects, causing over-escalation. Fallback: use a two-tier policy where small high-contrast regions are reported as low-confidence suspected defects with mandatory human review rather than being suppressed.

---

## Item 8: HUM-c141c05031

类型：`single_idea`

### Candidate A

Title:
Retrieval-Consistency Agent for Shifted or Contaminated Normal Reference Banks

Core proposal:
Add a lightweight inspection agent that audits the normal-reference evidence behind each suspicious region. For each high-score region, the agent retrieves top-k normal patches, measures whether the retrieved evidence is stable and visually consistent, estimates whether retrieved references may themselves be contaminated, and either accepts the anomaly decision, lowers confidence, or escalates the case for human review when the decision depends on unstable evidence.

Motivation or baseline weakness:
PatchCore-style nearest-neighbor industrial anomaly detectors can be brittle when the normal memory bank is shifted across acquisition conditions, product subtypes, or factories, or when it contains subtle anomalous examples. Their heatmaps also indicate abnormal regions without showing which retrieved normal references support or undermine the decision.

Mechanism or approach:
A frozen-embedding retrieval audit module built on PatchCore-style memory features, optionally using DINO or CLIP embeddings for secondary consistency checks. The final region score combines the original anomaly score, a retrieval-inconsistency term between the test region and its top-k references, and a contamination-risk term for the retrieved references.
Improve reliability under reference shift and memory contamination while preserving the detector's core localization quality. Tune thresholds on a validation split to reduce false alarms and selective risk at matched defect-region recall, with constraints that pixel-level AUROC and PRO do not fall below the strongest non-agent IAD baseline by more than a small tolerance.

Experiment and implementation plan:
PatchCore; PaDiM; RD4AD; WinCLIP; non-agent PatchCore with the same memory bank
MVTec_AD or VisA images; product-category labels; normal reference images per class; pixel masks or bounding boxes for evaluation where available; reference-shift splits created by mixing normal images across acquisition conditions, product subtypes, or factories where metadata permits; contaminated-memory splits created by injecting a controlled fraction of anomalous images into the normal bank
build_patchcore_memory_bank.py; retrieve_topk_normal_patches.py; score_retrieval_consistency.py; audit_reference_bank_contamination.py; run_agent_inspection_loop.py; evaluate_detection_localization_agent_metrics.py; generate_structured_report_json.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; false_alarm_reduction; tool_success_rate; evidence_grounding_score; human_escalation_precision; calibration_error; selective_risk
remove reference-bank audit while keeping top-k retrieval; replace retrieval-consistency scoring with raw nearest-neighbor distance; use random normal references instead of top-k retrieved references; disable the escalation policy; vary the contamination rate in the normal memory bank; vary reference-shift severity through cross-subset memory construction
Run the same PatchCore heatmap and report template without retrieval audit, contamination scoring, or escalation, using identical anomaly scores and comparable thresholds wherever possible.
At matched defect_region_recall, reduce false positive decisions by at least 10% versus non-agent PatchCore on MVTec_AD or VisA; Improve evidence_grounding_score by at least 15% over a non-agent report generated from the same heatmap; Detect injected contaminated reference images with AUROC above 0.75 on synthetic contamination splits; Keep pixel_level_auroc and pro_score within 1 percentage point of the strongest direct IAD baseline; Failure if tool_success_rate is below 90% or if agent-level reliability metrics do not improve over the non-agent baseline

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W4404704036

Risks, controls, or fallback:
Risk: synthetic reference shift and contamination may not match real factory drift. Fallback: report natural category shifts, acquisition-condition shifts, and injected contamination separately, and position the module as a reference-bank diagnostic if it improves evidence quality and escalation precision without consistently improving AUROC.

### Candidate B

Title:
Retrieval-Consistency Agent for Shifted or Contaminated Normal Reference Banks

Core proposal:
Add an agentic retrieval-audit loop around a frozen PatchCore-style memory bank. For each connected suspicious heatmap region, retrieve top-k normal patches, compute whether the retrieved references are mutually consistent and visually close to the test region, flag references that repeatedly behave as outliers among normal samples, and either accept the anomaly decision, down-weight unstable evidence, or escalate the case for human review.

Motivation or baseline weakness:
PatchCore-style nearest-neighbor industrial anomaly detectors can be brittle when the normal memory bank is shifted across acquisition conditions or mildly contaminated by anomalous samples. Their heatmaps also do not identify which normal references support a rejection decision, limiting evidence grounding in agentic inspection workflows.

Mechanism or approach:
A lightweight reference-bank audit and retrieval-consistency scorer using frozen PatchCore features, with optional DINO or CLIP embeddings only for secondary evidence reporting. For region r with base anomaly score A(r), top-k references N_k(r), and per-reference contamination scores C(n), compute S(r)=A(r)+lambda*median_distance(r,N_k(r))+gamma*mean(C(n) for n in N_k(r))+eta*topk_instability(r). Contamination scores are estimated by leave-one-out nearest-neighbor normality within the memory bank, not by using test labels.
Tune lambda, gamma, eta, k, anomaly thresholds, and escalation thresholds on a validation split to reduce false alarms and unsupported escalations at matched defect_region_recall. The constrained objective is to minimize selective_risk and false_alarm_reduction error subject to pixel_level_auroc, pro_score, and defect_region_recall not dropping by more than the pre-specified tolerance relative to the strongest non-agent IAD baseline on the same split.

Experiment and implementation plan:
PatchCore; PaDiM; RD4AD; WinCLIP; non-agent PatchCore with the same memory bank and identical threshold-search protocol
MVTec_AD or VisA test images; product_category labels; normal reference images per class; pixel masks or bounding boxes when available for localization evaluation; synthetic reference-shift splits created by separating normal images by acquisition condition, product subtype, or controlled cross-category mismatch; synthetic contaminated-memory splits created only from training-time anomalous or held-out defect images injected into the normal bank at known rates
build_patchcore_memory_bank.py; retrieve_topk_normal_patches.py; score_retrieval_consistency.py; audit_reference_bank_contamination.py; run_agent_inspection_loop.py; evaluate_detection_localization_agent_metrics.py; generate_structured_report_json.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; false_alarm_reduction; tool_success_rate; evidence_grounding_score; human_escalation_precision; calibration_error; selective_risk
remove reference-bank audit while keeping top-k retrieval evidence; set gamma=0 so contaminated-reference risk cannot affect the score; replace retrieval_consistency_score with raw nearest-neighbor distance only; use random same-class normal references instead of top-k retrieved references; disable escalation policy and force every case to accept or reject; vary contamination rate in the normal memory bank; vary factory-shift severity by cross-subset memory construction
Run non-agent PatchCore with the same memory bank, same base heatmaps, same validation thresholds, and the same report template but without retrieval audit, contamination scoring, or escalation.; Run the retrieval-audit loop with shuffled test-region to reference-region pairings; improvements should disappear if gains come from valid evidence links rather than threshold changes.; Inject visually normal held-out images into the memory bank as a placebo contamination condition; the audit should not flag them at the same rate as injected anomalous references.
At matched defect_region_recall, reduce false positive regions or false positive images by at least 10% versus non-agent PatchCore on MVTec_AD or VisA shifted or contaminated splits.; Improve evidence_grounding_score by at least 15% over a non-agent report generated from the same heatmap and threshold.; Detect injected contaminated reference images with AUROC above 0.75 on synthetic contamination splits while keeping placebo normal-injection false positive rate below the selected operating point.; Do not reduce pixel_level_auroc or pro_score by more than 1 percentage point versus the strongest direct IAD baseline on the same evaluation split.; Failure if tool_success_rate is below 90%, if shuffled-reference negative control matches the full method, or if gains are explained only by a lower operating threshold.

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W4404704036

Risks, controls, or fallback:
Risk: synthetic shift and contamination may not reflect real factory drift, and reference-bank outlier scores may confuse rare but valid normal appearances with contamination. Fallback: report results separately for natural category-level shifts, acquisition-condition shifts, placebo normal injections, and injected contamination, and position the module as a reference-bank diagnostic and escalation aid rather than a universal detector if detection AUROC does not improve.

---

## Item 9: HUM-aa54b53ab9

类型：`portfolio`

### Candidate A

Idea 1
Title:
Reference-Consistency Agent for Shifted or Contaminated Normal Memory Banks

Core proposal:
Add an agentic reference-audit workflow around a frozen base IAD scorer. For each test image, the agent identifies high-score regions, retrieves top-k nearest normal patches from the reference bank, computes test-to-reference consistency, computes reference-to-reference consistency among the retrieved neighbors, and assigns each retrieved exemplar a reliability weight. References that are internally inconsistent, unusually close to known suspicious regions, or drawn from a mismatched product/domain subset are downweighted rather than deleted globally. The final anomaly score fuses the base IAD score with a local reference-reliability penalty and a domain-shift uncertainty term. The agent reports the anomaly region, the reference patches used, references downweighted for that decision, confidence, and whether the case should be escalated because the reference evidence is unstable.

Motivation or baseline weakness:
Memory-bank and distribution-estimation IAD methods can fail when the normal reference set is not actually representative of deployment normals. Cross-factory shift can make harmless variants look anomalous, while contaminated reference images can make true defects appear normal because their nearest neighbors include defective or mismatched exemplars.

Mechanism or approach:
A Reference Bank Auditor that stores retrieval provenance, computes patch-level test-reference consistency and retrieved-set self-consistency, produces per-reference reliability weights, and exposes calibrated confidence plus escalation triggers to the inspection agent.
For each image or patch, minimize selective detection risk under clean, shifted, and contaminated reference banks by combining the base anomaly score with a learned or validation-tuned reference reliability term. The operating point is selected to reduce false positives at matched recall while preserving localization quality and improving calibration under reference contamination.

Experiment and implementation plan:
PatchCore; PaDiM; FastFlow; RD4AD; non-agent PatchCore with the same reference bank; retrieval-only nearest-normal explanation without audit
MVTec_AD or VisA test images; product category labels; normal training/reference images; synthetically contaminated normal banks by injecting a controlled fraction of anomalous images into the reference set; synthetically shifted normal banks using cross-category, cross-domain, or held-out normal variants where applicable; optional pixel masks for localization evaluation; inspection goal specifying acceptable false-alarm rate or target recall
build_reference_bank.py: construct clean, shifted, and contaminated normal memory banks with stored source labels; run_iad_baselines.py: run PatchCore, PaDiM, FastFlow, and RD4AD image-level and pixel-level scoring; agent_reference_audit.py: retrieve normal patches, compute test-reference and reference-reference consistency, assign reliability weights, and rerun scoring; calibrate_reference_scores.py: fit score-fusion and escalation thresholds on a validation split; generate_grounded_report.py: output anomaly_score, anomaly_mask_or_region, defect_type, evidence, normal_reference_used, confidence, recommended_action, and failure_warning; evaluate_detection_localization_agent.py: compute AUROC, AUPR, PRO, IoU, calibration error, tool_success_rate, evidence_grounding_score, false_alarm_reduction, and human_escalation_precision
image_level_auroc; pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; calibration_error; selective_risk; tool_success_rate; evidence_grounding_score; false_alarm_reduction; human_escalation_precision
remove reference-bank audit but keep retrieval evidence in the report; use random normal references instead of top-k retrieved references; use base IAD score only without retrieval-consistency fusion; disable contaminated-reference downweighting while retaining shift uncertainty; disable domain-shift uncertainty while retaining contamination downweighting; replace calibrated escalation policy with a fixed anomaly-score threshold; vary contamination rate and factory-shift severity
Non-agent PatchCore, PaDiM, FastFlow, or RD4AD using the same contaminated or shifted memory bank and producing no verification loop; Agent report generator that sees the final heatmap and retrieved references but cannot change scores, weights, or escalation decisions; Reference retrieval evidence shown to the report module but excluded from anomaly scoring, calibration, and escalation; Auditor applied to a deliberately shuffled reference bank where product-category labels are mismatched, to verify that the workflow refuses or escalates instead of producing confident normality
At matched image-level recall, reduce false positives by at least 10% relative to the strongest non-agent IAD baseline under contaminated or shifted reference banks; Improve or maintain pixel-level AUROC and PRO relative to the strongest direct baseline under clean references, and improve them under contaminated references; Reduce expected calibration error relative to the base anomaly score by at least 10%; Achieve evidence_grounding_score above 0.8 by linking each defect claim to a region and at least one retained or downweighted normal reference; Human_escalation_precision must exceed the fixed-threshold baseline at matched recall; Failure criterion: if tool_success_rate, evidence_grounding_score, or false_alarm_reduction do not improve over the non-agent baseline under reference stress, the mechanism is not supported

Risks, controls, or fallback:
Risk: the auditor may downweight rare but valid normal variants and increase false alarms. Fallback: restrict downweighting to decision-local reliability weights rather than permanent reference deletion, add a small factory-specific calibration split when available, and return an uncertainty or escalation decision when the retrieved normal set is internally inconsistent.

---

Idea 2
Title:
Disagreement-Gated Localization Agent for Weakly Labeled Industrial Defects

Core proposal:
Use an agent that separates candidate-mask generation from evidence-based mask acceptance. The agent first obtains frozen IAD heatmaps from complementary detectors, proposes candidate masks from high-score connected components and prompted segmentation, and computes a mask evidence vector for each candidate. The evidence vector includes anomaly intensity inside the mask, contrast against the surrounding region, cross-model agreement, consistency with retrieved normal patches from the same product category, mask shape plausibility, and response under task-preserving negative-control transformations such as brightness or contrast changes. The agent selects a mask only if the evidence satisfies a validation-tuned acceptance rule; otherwise it returns a coarse region or escalates rather than forcing a precise localization.

Motivation or baseline weakness:
Unsupervised IAD heatmaps can produce noisy localization when pixel labels are sparse or absent. Segmentation refinement can sharpen these errors into confident but false defect masks, especially for lighting changes, repetitive texture, reflections, or background edges that are not real defects.

Mechanism or approach:
A Disagreement-Gated Mask Selector that ranks candidate masks using base anomaly intensity, cross-model agreement, retrieval consistency against normal patches, mask compactness, boundary alignment, and negative-control response to brightness or texture-preserving perturbations.
Select anomaly masks that maximize defect-region precision at a fixed defect-region recall. The selector penalizes masks that are supported by only one unstable heatmap, match normal-reference texture, or remain highly anomalous under perturbations intended to preserve the true defect label while exposing lighting or texture artifacts.

Experiment and implementation plan:
PatchCore heatmap thresholding; RD4AD heatmap thresholding; DRAEM segmentation output; WinCLIP zero-shot anomaly map; SAM or SAM2 prompted by top heatmap points without mask-selection policy; Mask2Former if category labels and suitable training labels are available
MVTec_AD or VisA images with image labels and available masks for evaluation only; normal reference images per product category; optional sparse bounding-box or point labels to simulate weak annotation; synthetic lighting, contrast, blur, and texture-preserving perturbation views for negative controls; inspection goal specifying precision-recall operating point
run_multi_iad_heatmaps.py: generate PatchCore, RD4AD, DRAEM, and WinCLIP anomaly maps; propose_candidate_masks.py: produce connected-component masks and prompted SAM or SAM2 masks from high-score regions; compute_mask_evidence.py: calculate anomaly intensity, cross-model agreement, normal-reference consistency, shape features, and negative-control stability; agent_mask_selection.py: choose a supported mask, return a coarse uncertain region, reject unsupported masks, or escalate; report_region_evidence.py: produce structured report with region, score, defect_type, evidence, confidence, recommended_action, and failure_warning; evaluate_localization_workflow.py: compute localization, calibration, selective-risk, and agent metrics
pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; f1_score; tool_success_rate; evidence_grounding_score; false_alarm_reduction; human_escalation_precision; selective_risk
remove cross-model agreement score; remove retrieval-consistency check against normal patches; remove perturbation-based negative control; remove mask shape and boundary plausibility terms; use SAM or SAM2 masks selected by largest area or highest heatmap overlap only; disable escalation and force a mask for every image; evaluate with only one IAD model to test dependence on ensemble diversity
SAM or SAM2 refinement directly applied to PatchCore top points with no verification loop; Agent report generation after fixed-threshold heatmap localization without ability to reject, rerank, or abstain on masks; Randomly selected candidate mask among SAM or SAM2 proposals matched for area distribution; Mask selector evaluated on normal images with synthetic lighting perturbations, where a valid mechanism should reject most candidate masks rather than sharpen artifacts
Improve defect_region_precision by at least 10% at matched defect_region_recall relative to the best heatmap-threshold baseline; Improve mask_iou or PRO on MVTec_AD or VisA without reducing image-level anomaly detection performance by more than 1 percentage point; Reduce false positive regions caused by lighting or texture perturbations relative to direct SAM or SAM2 refinement; Achieve tool_success_rate above 0.9 for heatmap generation, mask proposal, evidence scoring, and report generation; Human_escalation_precision must exceed a fixed-score escalation baseline when the selector abstains; Failure criterion: if the selector does not beat simple heatmap thresholding and the negative-control segmentation baseline, the mask-selection mechanism is not justified

Risks, controls, or fallback:
Risk: true subtle defects may create high model disagreement and be escalated too often or localized only coarsely. Fallback: tune the operating point for high recall, permit coarse region outputs when fine mask evidence is insufficient, and separate defect detection from fine-grained mask acceptance so that uncertain localization does not suppress true anomaly detection.

---

Idea 3
Title:
Evidence-Grounded Reporting and Escalation Agent for Unsupported VLM Defect Claims

Core proposal:
Introduce an evidence-grounded report checker and selective escalation policy. The agent runs frozen detection, localization, retrieval, and optional VLM description tools, then converts any candidate report into a constrained structured form. Each defect claim must be tied to a specific anomalous region, detector scores for that region, normal-reference contrasts, and an allowed defect taxonomy label or a taxonomy-unknown label. Claims that lack region support, contradict normal-reference evidence, or rely only on free-form visual description are rewritten as uncertainty, removed, or escalated. The final action is chosen by a calibrated selective policy that uses anomaly score, localization confidence, cross-tool disagreement, retrieval consistency, and claim-support score.

Motivation or baseline weakness:
VLM-based inspection reports can produce plausible defect descriptions that are not supported by the anomaly evidence. Conversely, non-agent IAD systems may output scores or heatmaps without a principled rule for when the evidence is too weak, ambiguous, or poorly calibrated and should be escalated to human review.

Mechanism or approach:
A Claim-to-Evidence Verifier that maps every report field to region-level evidence, normal references, detector scores, and taxonomy constraints, then applies a calibrated selective prediction policy for accept, reject-as-normal, or escalate decisions.
Minimize unsupported report claims and unnecessary human review under a selective-risk objective. The optimization balances anomaly recall, false-alarm reduction, report correctness, evidence grounding, calibration error, and escalation precision, using validation-tuned thresholds rather than unconstrained free-form report confidence.

Experiment and implementation plan:
WinCLIP; AnomalyCLIP; PatchCore plus template report; LLaVA or Qwen-VL report from image and heatmap only; tool-using agent without evidence-grounded report checker; fixed-threshold human escalation based only on anomaly score
MVTec_AD or VisA images; product category labels; normal reference images; optional defect taxonomy for mapping free-form descriptions to allowed defect types; available masks or bounding boxes for evaluating claim-region grounding; validation split for calibration and selective escalation thresholding; human-review labels simulated from ground-truth anomaly status and predefined uncertainty conditions
run_detection_tools.py: execute PatchCore, WinCLIP, AnomalyCLIP, and optional RD4AD; retrieve_region_references.py: find normal patches corresponding to suspicious regions; generate_candidate_report.py: create initial structured report with anomaly_score, anomaly_mask_or_region, defect_type, evidence, normal_reference_used, confidence, recommended_action, and failure_warning; verify_report_claims.py: check claim-region-reference consistency, enforce taxonomy constraints, and remove or rewrite unsupported descriptions; calibrate_and_escalate.py: fit calibration and selective prediction thresholds for accept, reject, and escalate actions; evaluate_reports_and_escalation.py: score report_correctness, evidence_grounding_score, calibration_error, selective_risk, false_alarm_reduction, and human_escalation_precision
image_level_auroc; pixel_level_auroc; aupr; mask_iou; defect_region_precision; defect_region_recall; report_correctness; evidence_grounding_score; calibration_error; selective_risk; false_alarm_reduction; human_escalation_precision; tool_success_rate
remove claim-to-region grounding requirement; remove normal-reference contrast from the verifier; remove cross-tool disagreement from confidence calibration; replace selective escalation policy with fixed anomaly-score threshold; allow free-form VLM defect descriptions without taxonomy or evidence checking; disable refusal and force a recommended_action for every sample; verify only the final text while ignoring detector and retrieval evidence
VLM report generated from the image and anomaly heatmap without verification; PatchCore plus deterministic template report with no human-escalation policy; Agent workflow with all tools available but no evidence-grounded report checker; Verifier given shuffled region-evidence links, where supported-claim scores should decrease rather than remain high; Normal-image reports with injected generic defect text, where the verifier should remove or escalate unsupported claims
Increase report_correctness and evidence_grounding_score by at least 15% relative to the unverified VLM-report baseline; Reduce unsupported defect_type claims by at least 20% while maintaining image-level recall within 2 percentage points of the strongest IAD baseline; Improve human_escalation_precision over fixed anomaly-score escalation at matched anomaly recall; Reduce calibration_error relative to raw IAD or VLM confidence scores; Maintain tool_success_rate above 0.9 for detection, retrieval, verification, and report generation; Failure criterion: if the verifier improves fluency or formatting but not evidence_grounding_score, false_alarm_reduction, or human_escalation_precision, the agentic component is considered ineffective

Risks, controls, or fallback:
Risk: strict verification may under-report novel defect types or over-escalate rare but real anomalies. Fallback: separate defect presence from defect naming, allow taxonomy-unknown labels, and escalate with region evidence when localization is strong but semantic classification is weak.

### Candidate B

Idea 1
Title:
Reference-Consistency Agent for Auditing Shifted or Contaminated Normal Memory Banks

Core proposal:
Add an agent-managed reference audit loop around a frozen PatchCore-style memory bank. For each high-score test region, retrieve the top-k normal patches, compute local feature-distance statistics, neighbor-to-neighbor compactness, product-category consistency, and disagreement between the test patch and its retrieved references. The auditor flags reference clusters as potentially contaminated when they are both close to anomalous test regions and inconsistent with the clean validation distribution. Scoring is rerun after excluding flagged references, and the agent reports a defect only when anomaly evidence remains stable after the audit. If the anomaly score collapses or retrieved references are invalid, the agent outputs an explicit reference-shift or ambiguous-normal-variation escalation rather than a defect claim.

Motivation or baseline weakness:
PatchCore and other normal-reference IAD methods can produce unstable anomaly scores when the normal memory bank is shifted across factories or contaminated by subtle defective samples. Patch-level heatmaps alone do not indicate whether the nearest normal references are trustworthy evidence, and evidence-grounded inspection reports remain weak without an explicit reference audit.

Mechanism or approach:
A frozen-feature reference-bank auditor that records top-k retrievals, estimates patch-level reference consistency and contamination likelihood from validation-calibrated distance distributions, excludes suspicious references for a second scoring pass, and exposes accept, refuse, or escalate decisions to the inspection agent.
Optimize a calibrated selective decision rule that reduces false positives from shifted or contaminated reference banks while preserving defect recall: accept an automated defect decision only when the audited anomaly score remains high, retrieved normal evidence is category-valid, consistency to clean references is low for the test region, and estimated contamination probability of the supporting references is below a threshold.

Experiment and implementation plan:
PatchCore; PaDiM; RD4AD; WinCLIP
MVTec_AD normal training images and anomalous test images with masks; VisA normal training images and anomalous test images with masks; synthetic contaminated memory banks created by injecting 1%, 5%, and 10% anomalous images or shifted normal images into reference sets; factory-shift or proxy-shift splits created with product-category-preserving lighting, background, acquisition, or texture changes; product_category metadata and normal_reference_images for retrieval validation
build_patchcore_or_padim_memory_bank.py; inject_reference_contamination_and_factory_shift.py; retrieve_topk_reference_patches.py; compute_retrieval_consistency_and_bank_audit.py; rerun_scoring_after_reference_exclusion.py; agent_inspection_loop_with_audit_and_escalation.py; evaluate_detection_localization_agent_metrics.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; f1_score; mask_iou; defect_region_precision; defect_region_recall; false_alarm_reduction; tool_success_rate; evidence_grounding_score; report_correctness
remove reference-bank audit and use raw PatchCore scores; retrieve random same-category normal patches instead of nearest references; disable contaminated-reference exclusion but keep the reporting agent; replace patch-level retrieval consistency with global image similarity only; vary contamination rates and factory-shift severity; calibrate thresholds on clean validation only versus shifted validation; use PaDiM or RD4AD features for retrieval while keeping the same audit policy
Generate a structured report from the raw PatchCore heatmap without reference audit or retrieval consistency checking; Run the audit with randomly permuted product categories where retrieved references should be rejected as invalid evidence; Inject only clean same-category normal references and verify that the auditor does not remove a large fraction of valid memory-bank patches; Apply the exclusion step to low-score normal test images and require no new defect reports to be introduced
At matched defect_region_recall, reduce false alarms by at least 15% relative to PatchCore on contaminated or shifted reference banks; Maintain image_level_auroc within 2 percentage points of PatchCore on clean memory banks; Improve evidence_grounding_score by at least 20% over the non-auditing report baseline; Achieve tool_success_rate above 90% for retrieval, audit, reranking, and report-generation calls; Failure if the audit improves clean-bank metrics only by discarding difficult cases, or if false_alarm_reduction comes with more than a 5% absolute drop in defect_region_recall

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W4404704036

Risks, controls, or fallback:
Risk: the consistency score may reject legitimate rare normal variants and increase escalations. Fallback: use category-specific validation calibration, cap the allowed fraction of excluded references, and introduce a conservative abstention band so uncertain reference-shift cases are escalated instead of converted into unsupported defect calls.

---

Idea 2
Title:
Disagreement-Gated Mask Selection Agent for Weakly Labeled Defect Localization

Core proposal:
Use an inspection agent that first obtains frozen IAD heatmaps from DRAEM, RD4AD, and optionally FastFlow as a weaker stress-test baseline. Candidate points and boxes are generated from high-confidence heatmap regions and passed to SAM or SAM2. Each candidate mask is accepted only when it has strong support from at least one reliable IAD heatmap, low spatial disagreement among the stronger IAD sources inside the proposed defect region, limited overlap with known normal structures, and a negative response when the same prompting and scoring procedure is applied to retrieved same-category normal-reference regions. Masks that also appear on matched normal patches or depend on shuffled heatmaps are rejected or escalated. The final report links the selected mask to heatmap evidence and normal-reference counterexamples.

Motivation or baseline weakness:
SAM or SAM2 can segment visually salient regions that are not true defects, while IAD heatmaps from DRAEM, FastFlow, or RD4AD can be noisy under texture and lighting variation. Without a mask selection policy, normal-reference negative controls, and shuffled-evidence controls, promptable segmentation can falsely appear to improve defect localization.

Mechanism or approach:
A disagreement-gated mask selection policy that scores each candidate mask by heatmap support, cross-model spatial agreement, normal-reference negative-control response, prompt stability, and calibrated uncertainty, then returns accept, reject, or escalate decisions.
Maximize defect_region_precision and mask_iou under full-mask or sparse-box supervision by selecting a candidate mask only when it improves agreement-weighted anomaly evidence over raw heatmap thresholding and does not reproduce on retrieved normal-reference regions.

Experiment and implementation plan:
DRAEM; FastFlow; RD4AD; SAM; SAM2; GroundingDINO
MVTec_AD images with pixel masks; VisA images with pixel masks; weak-label variants created from image-level anomaly tags, sparse boxes, or sparse point prompts; normal_reference_images for each product category; lighting and texture perturbation splits for false-positive stress tests; known-normal test images for refusal evaluation
run_iad_heatmap_ensemble.py; generate_prompt_points_and_boxes_from_heatmaps.py; generate_sam_or_sam2_candidate_masks.py; retrieve_normal_counterfactual_regions.py; score_cross_model_disagreement_and_negative_controls.py; agent_mask_selection_and_report.py; evaluate_sparse_label_localization.py
pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; f1_score; tool_success_rate; report_correctness; evidence_grounding_score; false_alarm_reduction
use SAM or SAM2 refinement without disagreement-gated mask selection; use single IAD model support instead of cross-model disagreement; remove normal-reference negative-control mask checking; use GroundingDINO text boxes only without IAD heatmap evidence; train or tune thresholds with full masks versus sparse boxes only; disable calibration and use fixed anomaly thresholds; remove prompt-stability scoring across point and box prompts
Prompt SAM or SAM2 with high-saliency but low-anomaly regions and require the selected masks to be rejected; Run the mask-selection agent on known normal images and require refusal or no-defect reports; Shuffle heatmaps across images before mask selection to verify that accepted masks depend on real localized evidence; Retrieve normal-reference patches from mismatched product categories and require the agent to flag the negative-control evidence as invalid rather than using it; Use blank or uniform heatmaps with SAM or SAM2 prompts and require no claimed localization improvement
Improve mask_iou by at least 10% over the best raw IAD heatmap thresholding baseline on MVTec_AD or VisA; Improve defect_region_precision by at least 15% under lighting or texture perturbations while keeping defect_region_recall within 5% of the strongest IAD baseline; Reduce unsupported selected masks on normal-reference negative controls by at least 25% compared with SAM or SAM2 refinement without the policy; Achieve evidence_grounding_score above 0.8 for claims linked to selected regions and references; Failure if SAM or SAM2 refinement without the policy matches performance, if shuffled-heatmap controls are still accepted, or if tool_success_rate falls below 90%

Evidence paper IDs:
openalex:W7153670799; openalex:W7154655652; openalex:W4380551232

Risks, controls, or fallback:
Risk: cross-model disagreement can be high for very small or low-contrast true defects, causing over-rejection. Fallback: add a small-defect escalation mode where high local anomaly density, stable prompt response, and valid same-category normal-reference rejection permit a low-confidence localized anomaly report without forcing a specific defect label.

---

Idea 3
Title:
Evidence-Grounded Report Checker with Selective Human Escalation for VLM-Based IAD

Core proposal:
Build a lightweight agent workflow in which WinCLIP, AnomalyCLIP, CLIP, and PatchCore provide image-level anomaly scores and candidate regions. A VLM-style report generator drafts a structured report with fields for defect presence, region, visual evidence, normal-reference contrast, and uncertainty. A claim-to-evidence checker parses the report into atomic claims and verifies each claim against candidate region crops, anomaly masks or heatmaps, retrieved same-category normal references, and an optional allowed defect taxonomy. Unsupported claims are revised to generic localized-anomaly language, refused, or escalated to human review. The selective decision policy is calibrated on validation data to reduce false alarms at matched image-level recall rather than improving report fluency alone.

Motivation or baseline weakness:
WinCLIP, AnomalyCLIP, CLIP, and VLM-style inspection workflows can produce plausible semantic defect descriptions that are unsupported by localized visual evidence, especially when defect taxonomies are sparse, candidate regions are weak, or normal references shift.

Mechanism or approach:
A claim-to-evidence verifier that parses structured reports into atomic claims, links each claim to localized anomaly evidence and retrieved normal references, scores grounding support and taxonomy validity, and outputs calibrated confidence with accept, revise, refuse, or escalate decisions.
Optimize selective report correctness by maximizing report_correctness and evidence_grounding_score while maintaining image-level anomaly recall and reducing false alarms under a bounded automated-coverage target.

Experiment and implementation plan:
WinCLIP; AnomalyCLIP; CLIP; PatchCore
MVTec_AD and VisA images with product categories, anomaly masks, and defect labels where available; normal_reference_images for same-category retrieval-grounded comparison; optional defect_taxonomy converted to an allowed report vocabulary; human-review proxy labels derived from ground-truth anomaly presence, class labels where available, and mask overlap with claimed regions; normal-image subsets and masked-region variants for refusal and confidence-drop tests
run_winclip_anomalyclip_clip_patchcore_candidates.py; retrieve_normal_references_for_region.py; generate_structured_vlm_style_report.py; parse_report_into_atomic_claims.py; verify_claim_region_reference_grounding.py; calibrate_selective_escalation_policy.py; evaluate_report_and_agent_metrics.py
image_level_auroc; pixel_level_auroc; aupr; mask_iou; defect_region_precision; defect_region_recall; report_correctness; evidence_grounding_score; false_alarm_reduction; tool_success_rate; f1_score
remove evidence-grounded report checker and keep the original VLM-style report; remove retrieval of same-category normal references; allow free-form defect descriptions instead of taxonomy-constrained claims; use uncalibrated report confidence only; escalate based on anomaly score only without claim verification; replace region-linked evidence with whole-image captions; disable revision and allow only accept-or-reject decisions
Ask the report generator to describe defects on known normal images and require unsupported claims to be refused or escalated; Provide mismatched normal references from a different product category and require the checker to flag the evidence as invalid; Mask out the candidate defect region before report generation and require grounding confidence to drop; Shuffle candidate regions across images and require claim-to-region links to be rejected; Use a defect taxonomy with labels absent from the product category and require taxonomy-invalid claims to be revised or refused
Improve report_correctness by at least 20% over structured VLM-style reports without the checker; Improve evidence_grounding_score by at least 25% over retrieval-augmented reporting without claim verification; Reduce false alarms by at least 15% at matched image-level recall relative to WinCLIP or AnomalyCLIP report decisions; Keep defect_region_recall within 5% of the strongest candidate-region baseline while improving unsupported-claim refusal on normal images; Failure if detection or localization metrics improve but report_correctness and evidence_grounding_score do not exceed the non-checker baseline

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W7153328271; openalex:W7138099583; openalex:W7154655652

Risks, controls, or fallback:
Risk: the checker may be too strict when ground-truth defect labels are coarse or when the anomaly is visually real but semantically hard to name, lowering automated coverage. Fallback: output a generic localized anomaly with explicit uncertainty and escalate fine-grained defect naming to human review rather than hallucinating a specific defect type.

---

## Item 10: HUM-d65d1dfcee

类型：`portfolio`

### Candidate A

Idea 1
Title:
Reference-Consistency Agent for Shift-Robust Industrial Anomaly Inspection

Core proposal:
An inspection agent runs a frozen industrial anomaly detector to produce a heatmap, extracts connected high-score candidate regions, retrieves category-matched normal patches for each region, audits the retrieved references, and accepts a defect claim only when detector evidence and reference-consistency evidence agree. For each candidate region, the agent stores the heatmap score, region mask, retrieved reference IDs, region-to-reference feature distances, distance dispersion, reference outlier flags, contamination probability, and final accept/escalate decision. The structured report links each accepted defect to its region, the normal references used for contrast, confidence, recommended action, and a failure warning when the decision is escalated or reference reliability is low.

Motivation or baseline weakness:
PatchCore, PaDiM, FastFlow, and RD4AD can over-score benign texture, illumination, or factory-specific normal-reference shifts because their memory banks assume clean and stable normal references. A non-agent baseline typically returns a heatmap without checking whether a suspicious region is inconsistent with retrieved normal neighbors or whether the reference bank itself contains shifted or contaminated examples.

Mechanism or approach:
A frozen-feature reference-consistency and memory-bank-audit module. Inputs are a candidate anomaly region, its feature vector, and k category-matched normal patch embeddings. Outputs are: nearest-reference distance, distance dispersion across the k references, mean visual similarity to retrieved references, reference-bank outlier score computed from each retrieved reference's distance to normal-bank prototypes, and a contamination flag. The module does not train a new detector; it only calibrates whether an existing detector's candidate region is supported by clean normal-reference contrast.
Optimize a selective decision rule for false-alarm reduction at matched recall. Accept a region as a defect when the base IAD score exceeds a calibrated threshold, the region-to-reference inconsistency score exceeds a calibrated threshold, and the retrieved-reference contamination probability is below a calibrated threshold. Escalate rather than accept when the IAD score is high but reference evidence is unreliable. Calibrate thresholds on normal validation images and a held-out anomalous calibration split when available, minimizing selective risk and calibration error while preserving a target image-level recall.

Experiment and implementation plan:
PatchCore; PaDiM; FastFlow; RD4AD; WinCLIP; non-agent PatchCore plus static threshold; retrieval-only nearest-normal comparison without agent verification
MVTec_AD test images with product categories and normal train images; VisA normal and anomalous images; optional mask labels for pixel-level evaluation only; synthetic reference shift splits created by holding out normal subdomains or applying lighting, color, or texture perturbations to normal references; synthetic contaminated memory banks created by injecting a controlled percentage of anomalous images into normal references
build_iad_memory_bank.py; retrieve_normal_references.py; compute_candidate_regions_from_heatmap.py; audit_reference_bank.py; run_agent_verification_loop.py; calibrate_selective_thresholds.py; generate_structured_inspection_report.py; evaluate_detection_localization_agent_metrics.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; false_alarm_reduction; tool_success_rate; evidence_grounding_score; human_escalation_precision; calibration_error; selective_risk; out_of_distribution_detection
remove reference-consistency score and use raw PatchCore heatmap only; remove contaminated-reference audit while keeping retrieval; use random normal references instead of nearest references; replace calibrated selective policy with fixed anomaly threshold; vary injected contamination rates in the reference bank; vary factory-shift severity using held-out normal subdomains or appearance perturbations; compare CLIP features versus IAD-backbone features for reference retrieval
agent writes a report from the same PatchCore heatmap without retrieval verification; retrieval module uses shuffled product-category references while all other thresholds are unchanged; reference audit is run and logged but its flags are ignored in the final decision; candidate anomaly regions are paired with normal references from a different image after retrieval, testing whether the consistency score depends on the correct evidence link
at matched image-level recall within 1 percentage point of PatchCore or RD4AD, reduce false positives by at least 15 percent on shifted-normal validation splits; improve defect_region_precision by at least 5 absolute points without decreasing defect_region_recall by more than 2 absolute points; achieve evidence_grounding_score at least 0.80 for accepted defect reports; detect contaminated reference banks with auroc at least 0.75 under 1-10 percent anomaly injection; failure if tool_success_rate and evidence_grounding_score do not improve over the non-agent heatmap-and-report baseline

Risks, controls, or fallback:
Risk: reference retrieval may fail for highly repetitive textures or categories with few normal images, causing unnecessary escalation. Fallback: use category-level prototype references and conservative refusal rather than unsupported defect naming. If the reference-bank audit is unstable, restrict the mechanism to confidence calibration and human escalation while reporting normal_reference_used as low reliability.

---

Idea 2
Title:
Disagreement-Guided Mask Selection Agent for Weak-Label Defect Localization

Core proposal:
An agent first runs multiple frozen IAD models to generate heatmaps, converts high-score heatmap peaks and connected components into prompts, queries SAM or SAM2 for candidate masks, and then selects or refuses masks using a verifier. The verifier scores each candidate mask by overlap with high-anomaly regions, agreement across detectors, boundary alignment with local image gradients, inconsistency against retrieved normal patches from the same product category, and stability under benign negative-control augmentations. The agent rejects masks that are supported by only one detector, disappear under benign augmentations, or lack normal-reference contrast. The final report includes the selected mask, confidence, detector agreement summary, normal-reference contrast, defect type only if supported by an allowed taxonomy, and an escalation reason when mask evidence is ambiguous.

Motivation or baseline weakness:
SAM or SAM2 can produce plausible masks but does not know which mask corresponds to a real defect, while IAD heatmaps from PatchCore, DRAEM, RD4AD, or AnomalyCLIP can produce diffuse false positives from texture and lighting. In a weak-label setting with hidden or missing pixel labels, naive heatmap-to-mask conversion lacks a principled mask selection policy, uncertainty handling, and negative controls that distinguish real defect evidence from segmentation artifacts.

Mechanism or approach:
A mask-selection verifier that ranks SAM/SAM2 candidate masks using a calibrated weighted score. The score combines normalized overlap with top anomaly heatmap regions, agreement across at least two IAD models, boundary alignment between the mask boundary and local image edges, feature contrast between the masked region and retrieved normal patches, and an instability penalty computed from brightness, blur, and crop-preserving augmentations. The module selects the highest-scoring mask only if the score exceeds a calibrated threshold; otherwise it refuses localization and escalates.
Maximize localization precision under weak supervision while constraining recall loss. Tune only a small calibration layer or scalar weights using image-level labels, normal validation data, and optionally a small held-out mask calibration subset. Thresholds are optimized for defect_region_precision subject to a minimum defect_region_recall constraint, and the selective refusal policy is calibrated so low-agreement cases are escalated instead of converted into unsupported masks.

Experiment and implementation plan:
PatchCore heatmap thresholding; DRAEM segmentation output; RD4AD heatmap thresholding; AnomalyCLIP region scoring; SAM/SAM2 prompted by top heatmap point without mask verification; Mask2Former if category masks are available
MVTec_AD images with image-level labels and available pixel masks for evaluation only; VisA images with sparse or held-out pixel masks; optional defect taxonomy for mapping selected regions to defect types; normal reference images for each product category; weak-label setting where mask labels are hidden during method tuning except for an explicitly declared small calibration subset if used
run_multiple_iad_detectors.py; generate_sam_candidate_masks.py; retrieve_patch_references_for_masks.py; score_cross_model_disagreement.py; run_negative_control_augmentations.py; select_or_refuse_masks.py; calibrate_mask_confidence.py; render_region_grounded_report.py; evaluate_localization_and_agent_metrics.py
pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; f1_score; tool_success_rate; evidence_grounding_score; report_correctness; human_escalation_precision; calibration_error; selective_risk
remove cross-model disagreement and rank masks only by the primary heatmap; remove retrieval-consistency term; remove negative-control augmentation stability check; use SAM/SAM2 top-1 mask without verifier; replace selective refusal with always-report policy; tune with full pixel masks versus weak-label calibration to measure label efficiency; compare two-detector and three-detector disagreement ensembles
SAM/SAM2 masks selected from random points inside the product region; mask verifier receives shuffled detector scores from other images; agent generates reports from selected masks but without evidence-link checking; negative-control augmentations are computed and logged but not used in selection; normal-reference retrieval uses references from the wrong product category while detector heatmaps and masks remain unchanged
improve mask_iou by at least 5 absolute points over primary IAD heatmap thresholding on MVTec_AD or VisA; increase defect_region_precision by at least 10 percent relative while keeping defect_region_recall within 3 absolute points of the strongest direct baseline; achieve at least 90 percent tool_success_rate for mask proposal and scoring calls; achieve evidence_grounding_score at least 0.80 for accepted masks; failure if SAM/SAM2 mask selection does not beat the top-heatmap-prompt baseline or if agent metrics do not improve over the non-agent baseline

Risks, controls, or fallback:
Risk: cross-model agreement may reject subtle true defects that only one detector catches. Fallback: route low-agreement high-score regions to human review instead of suppressing them, and report failure_warning as low localization confidence. If SAM/SAM2 oversegments reflective products, fall back to connected components from calibrated heatmaps and mark the mask source explicitly.

---

Idea 3
Title:
Evidence-Checked Reporting and Escalation Agent for Unsupported VLM Defect Claims

Core proposal:
An agent separates visual detection from report generation. Frozen IAD models propose anomaly regions, retrieval tools gather category-matched normal references, a VLM drafts a defect report using a constrained output schema and optional defect taxonomy, and an evidence checker verifies every atomic claim against region masks, anomaly scores, detector agreement, and retrieved-reference contrast. The escalation policy refuses unsupported defect type claims, escalates high-risk low-confidence cases, and outputs a structured report containing anomaly_score, anomaly_mask_or_region, defect_type, evidence, normal_reference_used, confidence, recommended_action, and failure_warning. The VLM is not allowed to introduce a defect type or causal explanation unless the checker can link it to allowed taxonomy entries and visual evidence fields.

Motivation or baseline weakness:
VLM-based inspection with LLaVA, Qwen-VL, WinCLIP, or AnomalyCLIP can generate plausible but unsupported defect descriptions. Standard IAD baselines output scores and heatmaps without a calibrated policy for when to report, refuse, or escalate to a human reviewer, and without checking that each textual claim is tied to a region, score, and normal-reference contrast.

Mechanism or approach:
A claim-to-evidence verifier plus selective escalation calibrator. The verifier parses each generated report into atomic claims such as defect presence, defect type, location, severity, and recommended action. Each claim must link to a region ID, an IAD score or detector-agreement statistic, and at least one normal-reference contrast. Unsupported claims receive a zero support score and are removed, downgraded to unknown_anomaly, or escalated. The calibrator maps anomaly confidence, support score, taxonomy validity, and cross-model disagreement into accept, escalate, or refuse decisions.
Minimize unsupported report claims and selective risk while preserving detection performance. The decision rule accepts a report only when required fields are grounded, the anomaly confidence is calibrated, the defect type is taxonomy-valid or explicitly unknown, and the support score exceeds a threshold. Otherwise the system escalates to human review or emits a refusal warning. Thresholds are calibrated to reduce false alarms and unsupported claims while maintaining image-level recall close to the strongest detector used for region proposals.

Experiment and implementation plan:
WinCLIP; AnomalyCLIP; PatchCore plus template report; LLaVA or Qwen-VL direct defect description; tool_using_agent without evidence checker; retrieval_augmented_generation without region-level grounding
MVTec_AD or VisA images with product categories and normal references; optional defect taxonomy per category; available masks or bounding boxes for evaluation of region grounding; human-readable synthetic report labels derived from dataset class and mask metadata for report correctness evaluation; held-out normal images and anomalous images for calibration of escalation thresholds
run_iad_region_proposals.py; retrieve_normal_evidence.py; draft_vlm_report.py; parse_report_claims.py; verify_claim_region_reference_links.py; calibrate_accept_escalate_refuse_policy.py; simulate_human_review_queue.py; evaluate_report_grounding_and_detection.py
image_level_auroc; pixel_level_auroc; aupr; mask_iou; defect_region_precision; defect_region_recall; report_correctness; evidence_grounding_score; false_alarm_reduction; human_escalation_precision; tool_success_rate; calibration_error; selective_risk; out_of_distribution_detection
remove evidence-grounded report checker; remove normal-reference retrieval from claim verification; remove defect taxonomy constraint and allow free-form VLM descriptions; replace calibrated escalation with fixed confidence threshold; remove cross-model disagreement from confidence estimate; evaluate with and without optional mask labels during calibration; compare template reports versus VLM-drafted reports under the same checker
VLM generates defect descriptions directly from the image without anomaly regions; report checker receives mismatched regions from another image; retrieved normal references are shuffled across product categories; agent always accepts reports and never escalates; claim parser receives reports with location and defect-type fields swapped to test whether verification depends on structured evidence rather than text fluency
reduce unsupported defect descriptions by at least 30 percent compared with direct VLM reporting; achieve evidence_grounding_score at least 0.85 for accepted reports; maintain image_level_auroc within 1 absolute point of the strongest IAD detector used for proposals; achieve human_escalation_precision at least 0.70 on low-confidence or disagreement cases; failure if report_correctness or evidence_grounding_score does not improve over PatchCore plus template report and direct VLM baselines

Risks, controls, or fallback:
Risk: constrained reporting may be overly conservative and escalate too many cases, reducing automation value. Fallback: tune the selective policy to a user-specified inspection_goal such as safety-first or throughput-first, and output defect_type as unknown_anomaly when visual evidence is strong but taxonomy support is weak. If VLM report drafting is unstable, replace it with a deterministic template while keeping the same evidence checker and escalation policy.

### Candidate B

Idea 1
Title:
Reference-Consistency Agent for Shift-Resilient PatchCore Inspection

Core proposal:
Wrap frozen PatchCore with an agentic retrieval-and-audit loop. For each connected high-score region in the PatchCore heatmap, retrieve top-k normal patches from the memory bank and compute a reference-consistency score from PatchCore feature distance dispersion, local texture-statistic similarity, spatial/category metadata validity, and optional WinCLIP/CLIP semantic agreement when a VLM embedding is available. The agent audits the memory bank by accumulating per-reference reliability statistics: references are downweighted if they repeatedly appear as nearest neighbors for regions later judged anomalous, have outlier distances to other normal references, or fail category/metadata checks. Candidate regions are accepted, downweighted, or escalated using anomaly score, cross-reference agreement, calibrated uncertainty, and an explicit evidence bundle containing the region, nearest references, and audit status.

Motivation or baseline weakness:
PatchCore relies on a nearest-neighbor normal memory bank, so normal-reference shift or contaminated normal references can create false anomaly heatmaps and unsupported inspection decisions; the heatmap alone also does not explain why retrieved normal evidence is valid.

Mechanism or approach:
A lightweight reference-consistency and memory-bank audit wrapper around frozen PatchCore features, with optional frozen CLIP/WinCLIP embeddings for semantic consistency; no defect-label training is required beyond threshold calibration on normal validation images and injected-contamination validation splits.
Use a calibrated regional decision score: adjusted_score(region)=PatchCoreScore(region)-lambda*ReferenceConsistency(region)+gamma*ReferenceUnreliability(region). ReferenceConsistency is high when multiple valid normal references agree with the test patch, while ReferenceUnreliability is high when the retrieved references are audit outliers or suspected contaminants. Optimize thresholds to reduce false positives at matched image-level recall, with abstention/escalation when uncertainty or reference unreliability exceeds a calibrated bound.

Experiment and implementation plan:
PatchCore; PaDiM; WinCLIP; non-agent PatchCore plus static normal memory; PatchCore with random reference retrieval report only
MVTec_AD normal train/test images with masks for evaluation; VisA normal train/test images with masks for evaluation; synthetic reference-bank contamination created by injecting a fixed fraction of anomalous test images into the normal bank without using their labels for scoring; synthetic reference-shift splits created by replacing part of the normal bank with visually similar but category-mismatched normal images; normal-only validation images for calibration of consistency, audit, and escalation thresholds
build_patchcore_memory_bank.py; retrieve_reference_patches.py; compute_retrieval_consistency.py; audit_reference_bank.py; calibrate_selective_policy.py; run_agent_inspection_loop.py; evaluate_detection_localization_agent_metrics.py; generate_structured_report.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; f1_score; mask_iou; defect_region_precision; defect_region_recall; false_alarm_reduction; tool_success_rate; evidence_grounding_score; human_escalation_precision; calibration_error; selective_risk
remove retrieval consistency score and use PatchCore score only; remove memory-bank audit while keeping retrieved-reference evidence; use random normal references instead of nearest normal patches; use only feature-distance consistency without texture or semantic consistency; use only optional CLIP/WinCLIP semantic consistency without PatchCore feature consistency; vary injected contamination rate in the normal memory bank; vary selective escalation threshold at matched image-level recall
agent retrieves references and writes a report but the retrieval consistency and audit scores are not allowed to change anomaly scores or escalation decisions; memory bank is deliberately shuffled across product categories to test whether the agent detects invalid references rather than treating them as valid evidence; normal validation images are passed through the full agent loop and should not produce defect reports except as calibrated abstentions
at matched image-level recall, reduce false positive rate by at least 10 percent relative to PatchCore on MVTec_AD or VisA; maintain pixel_level_auroc and pro_score within 1 point of PatchCore while improving defect_region_precision by at least 5 percent; detect injected contaminated reference images with AUROC above 0.75; improve evidence_grounding_score and tool_success_rate over the retrieval-report-only negative control; failure if localization drops by more than 2 pro_score points or if false_alarm_reduction is achieved mainly by excessive escalation above a predeclared coverage floor

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W4404704036

Risks, controls, or fallback:
Risk: retrieval consistency may suppress true subtle defects that resemble normal texture, especially when the normal bank is broad or partly contaminated. Fallback: do not force suppression for low-margin regions; instead use selective prediction, report both the suspicious region and closest normal references, and escalate cases with high anomaly score but high reference consistency.

---

Idea 2
Title:
Disagreement-Guided Mask Selection Agent for Weak-Label Anomaly Localization

Core proposal:
Use an agent to turn anomaly heatmaps and text/box/point prompts into multiple SAM/SAM2 candidate masks, then select or abstain using explicit evidence tests. The agent keeps a candidate mask only if it overlaps high-confidence anomaly evidence from at least one frozen IAD model, is not similarly activated on retrieved normal reference regions, passes a normal-region negative prompt test, and has sufficient support under cross-model comparison. Cross-model disagreement is used as an uncertainty signal rather than as a direct defect label: strong disagreement triggers escalation unless one candidate has a calibrated margin over alternatives. The final output is a selected mask, confidence, evidence links to heatmaps/references, or a refusal on normal images.

Motivation or baseline weakness:
SAM or SAM2 can produce salient object masks that do not correspond to actual defect regions, while industrial anomaly heatmaps from PatchCore, RD4AD, AnomalyCLIP, or WinCLIP can be noisy under texture, lighting, and prompt variation, especially when pixel-level labels are sparse or unavailable for calibration.

Mechanism or approach:
A mask-selection and abstention policy that ranks frozen SAM/SAM2 candidate masks using heatmap overlap, retrieved-normal contradiction, cross-model support, negative-control activation, and calibrated margin; segmentation backbones and IAD models remain frozen.
Select mask m maximizing S(m)=alpha*IADHeatmapOverlap(m)+beta*CrossModelSupport(m)-delta*NormalReferenceSupport(m)-eta*NegativeControlActivation(m)-rho*MaskInstability(m). Abstain or escalate when the best-vs-second-best score margin is below a calibrated threshold or when normal-image negative controls activate strongly. Calibrate all thresholds with image-level labels or a small validation mask subset, and reserve test masks only for evaluation.

Experiment and implementation plan:
SAM; SAM2; PatchCore; RD4AD; AnomalyCLIP; WinCLIP; heatmap-threshold baseline without SAM; SAM/SAM2 largest-mask baseline
MVTec_AD images with pixel masks for evaluation; VisA images with pixel masks for evaluation; normal reference images from each product category; weak-label calibration split using only image-level anomaly labels unless a small mask-calibration setting is explicitly tested; optional defect taxonomy for report labels when available, not required for mask scoring
run_iad_heatmaps.py; generate_sam_candidates_from_heatmap_prompts.py; retrieve_normal_reference_regions.py; score_candidate_masks.py; run_negative_control_prompts.py; calibrate_mask_abstention.py; evaluate_mask_and_agent_metrics.py; render_region_grounded_report.py
pixel_level_auroc; pro_score; mask_iou; defect_region_precision; defect_region_recall; image_level_auroc; aupr; f1_score; tool_success_rate; evidence_grounding_score; report_correctness; human_escalation_precision; selective_risk
replace calibrated mask selection with largest SAM/SAM2 mask; remove negative-control normal-region prompt test; remove retrieved-normal contradiction term; remove cross-model disagreement and use one IAD heatmap only; compare SAM versus SAM2 using the identical selection policy; calibrate with image-level labels only versus a small labeled-mask subset; remove abstention and force a mask for every image
SAM/SAM2 refinement with no mask-selection policy, using the largest or highest-stability mask; random heatmap peak prompts matched for number of SAM/SAM2 calls; normal-image prompts where the agent should refuse to output a defect mask; permuted heatmaps paired with correct images to verify that selected masks depend on anomaly evidence rather than salient-object bias
improve mask_iou or pro_score by at least 5 percent over heatmap-threshold PatchCore or RD4AD on at least two MVTec_AD or VisA categories; reduce false defect masks on normal images by at least 10 percent at matched defect_region_recall; achieve higher evidence_grounding_score than SAM/SAM2 without a selection policy; maintain or improve image_level_auroc relative to the underlying heatmap model used for prompting; failure if SAM/SAM2 improves localization metrics only by increasing normal-image false alarms, or if tool_success_rate is not better than negative controls

Evidence paper IDs:
openalex:W4380551232; openalex:W7154655652; openalex:W7162893906; openalex:W7153328271

Risks, controls, or fallback:
Risk: cross-model disagreement can be high for small true defects, causing over-escalation or rejection of valid masks. Fallback: use a two-tier policy where small high-contrast regions are reported as low-confidence suspected defects with mandatory human review, while the system preserves the candidate mask and evidence bundle instead of suppressing it.

---

Idea 3
Title:
Evidence-Grounded Report Checker with Selective Human Escalation

Core proposal:
Add a report-checking agent after frozen IAD/VLM prediction. The checker parses each structured report into claims such as anomaly_present, defect_region, defect_type, severity, and recommended_action, then verifies each claim against region masks, anomaly heatmaps, retrieved normal references, and an optional category-specific defect taxonomy. Each claim is labeled grounded, contradicted, unsupported, or out-of-taxonomy. Unsupported defect_type, severity, or recommended_action fields are not emitted as confident facts; they trigger refusal, unknown-defect wording, or human escalation. The checker returns a structured report only when visual grounding, normal-reference contrast, and calibrated confidence satisfy predeclared thresholds.

Motivation or baseline weakness:
WinCLIP, AnomalyCLIP, CLIP-style scoring, and VLM-based inspection agents can assign semantic defect descriptions that are prompt-sensitive and not supported by localized visual evidence, leading to confident but unsupported manufacturing reports.

Mechanism or approach:
A claim-to-evidence verifier that links structured report fields to image regions and retrieved references, plus a calibration layer for confidence and escalation decisions; it uses frozen IAD/VLM outputs with deterministic rules or a small validation-fitted verifier trained only on report-grounding labels.
Minimize expected selective risk over structured reports. Accept a report only if anomaly confidence, localization evidence, normal-reference contrast, taxonomy validity, and claim-grounding scores exceed calibrated thresholds; otherwise escalate with an evidence bundle instead of producing unsupported defect descriptions. Optimize at a fixed coverage target so gains cannot come only from refusing most cases.

Experiment and implementation plan:
WinCLIP; AnomalyCLIP; CLIP; PatchCore; tool_using_agent; retrieval_augmented_generation; VLM report generator without verification; anomaly-score-only escalation
MVTec_AD or VisA images with anomaly labels and masks for grounding evaluation; normal reference images for visual contrast evidence; optional defect taxonomy converted to an allowed defect_type vocabulary per category; human or template-generated structured report labels for a small validation subset; synthetic unsupported-claim reports created by swapping defect types, regions, severities, or recommended actions; held-out normal images for refusal and false-report evaluation
run_iad_and_vlm_predictions.py; retrieve_normal_evidence.py; generate_structured_inspection_report.py; verify_claim_region_links.py; score_evidence_grounding.py; calibrate_escalation_policy.py; evaluate_report_and_detection_metrics.py; create_unsupported_claim_negative_set.py
image_level_auroc; pixel_level_auroc; aupr; f1_score; mask_iou; defect_region_precision; defect_region_recall; report_correctness; evidence_grounding_score; false_alarm_reduction; human_escalation_precision; calibration_error; selective_risk; tool_success_rate
remove claim-level evidence checker; remove normal-reference retrieval from the checker; remove defect-taxonomy constraint and allow free-form defect descriptions; use anomaly score confidence without calibration; escalate by fixed anomaly-score threshold instead of selective risk optimization; compare region-grounded report generation versus image-only VLM report generation; disable claim-type-specific decisions and use one global report confidence score
VLM generates a fluent report from the image and anomaly score but cannot inspect masks or references; checker receives randomly permuted region masks to test whether grounding scores fall; defect taxonomy is intentionally mismatched across categories to test refusal behavior; synthetic swapped-claim reports are evaluated without access to the original correct claim to prevent leakage
increase evidence_grounding_score by at least 15 percent over a VLM report generator without verification; reduce unsupported defect_type claims by at least 20 percent on synthetic swapped-claim tests; maintain image_level_auroc within 1 point of the strongest IAD baseline used for anomaly scoring while improving human_escalation_precision; achieve lower selective_risk than anomaly-score-only escalation at matched recall and at a predeclared coverage point such as 70 percent; failure if report_correctness improves only by refusing most cases, or if localization-grounded claims do not outperform the image-only VLM negative control

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W7154655652; openalex:W7153328271; openalex:W7138099583

Risks, controls, or fallback:
Risk: report verification may depend on imperfect masks and overly conservative taxonomy constraints. Fallback: separate visual grounding confidence from semantic defect-typing confidence, allowing the system to localize and escalate an unknown defect rather than forcing a specific defect_type or recommended_action.

---

## Item 11: HUM-f89e17a8c9

类型：`portfolio`

### Candidate A

Idea 1
Title:
Retrieval-Consistency Agent for Shifted or Contaminated Normal Reference Banks

Core proposal:
Add an agentic retrieval-audit loop around a frozen PatchCore-style memory bank. For each connected suspicious heatmap region, retrieve top-k normal patches, compute whether the retrieved references are mutually consistent and visually close to the test region, flag references that repeatedly behave as outliers among normal samples, and either accept the anomaly decision, down-weight unstable evidence, or escalate the case for human review.

Motivation or baseline weakness:
PatchCore-style nearest-neighbor industrial anomaly detectors can be brittle when the normal memory bank is shifted across acquisition conditions or mildly contaminated by anomalous samples. Their heatmaps also do not identify which normal references support a rejection decision, limiting evidence grounding in agentic inspection workflows.

Mechanism or approach:
A lightweight reference-bank audit and retrieval-consistency scorer using frozen PatchCore features, with optional DINO or CLIP embeddings only for secondary evidence reporting. For region r with base anomaly score A(r), top-k references N_k(r), and per-reference contamination scores C(n), compute S(r)=A(r)+lambda*median_distance(r,N_k(r))+gamma*mean(C(n) for n in N_k(r))+eta*topk_instability(r). Contamination scores are estimated by leave-one-out nearest-neighbor normality within the memory bank, not by using test labels.
Tune lambda, gamma, eta, k, anomaly thresholds, and escalation thresholds on a validation split to reduce false alarms and unsupported escalations at matched defect_region_recall. The constrained objective is to minimize selective_risk and false_alarm_reduction error subject to pixel_level_auroc, pro_score, and defect_region_recall not dropping by more than the pre-specified tolerance relative to the strongest non-agent IAD baseline on the same split.

Experiment and implementation plan:
PatchCore; PaDiM; RD4AD; WinCLIP; non-agent PatchCore with the same memory bank and identical threshold-search protocol
MVTec_AD or VisA test images; product_category labels; normal reference images per class; pixel masks or bounding boxes when available for localization evaluation; synthetic reference-shift splits created by separating normal images by acquisition condition, product subtype, or controlled cross-category mismatch; synthetic contaminated-memory splits created only from training-time anomalous or held-out defect images injected into the normal bank at known rates
build_patchcore_memory_bank.py; retrieve_topk_normal_patches.py; score_retrieval_consistency.py; audit_reference_bank_contamination.py; run_agent_inspection_loop.py; evaluate_detection_localization_agent_metrics.py; generate_structured_report_json.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; false_alarm_reduction; tool_success_rate; evidence_grounding_score; human_escalation_precision; calibration_error; selective_risk
remove reference-bank audit while keeping top-k retrieval evidence; set gamma=0 so contaminated-reference risk cannot affect the score; replace retrieval_consistency_score with raw nearest-neighbor distance only; use random same-class normal references instead of top-k retrieved references; disable escalation policy and force every case to accept or reject; vary contamination rate in the normal memory bank; vary factory-shift severity by cross-subset memory construction
Run non-agent PatchCore with the same memory bank, same base heatmaps, same validation thresholds, and the same report template but without retrieval audit, contamination scoring, or escalation.; Run the retrieval-audit loop with shuffled test-region to reference-region pairings; improvements should disappear if gains come from valid evidence links rather than threshold changes.; Inject visually normal held-out images into the memory bank as a placebo contamination condition; the audit should not flag them at the same rate as injected anomalous references.
At matched defect_region_recall, reduce false positive regions or false positive images by at least 10% versus non-agent PatchCore on MVTec_AD or VisA shifted or contaminated splits.; Improve evidence_grounding_score by at least 15% over a non-agent report generated from the same heatmap and threshold.; Detect injected contaminated reference images with AUROC above 0.75 on synthetic contamination splits while keeping placebo normal-injection false positive rate below the selected operating point.; Do not reduce pixel_level_auroc or pro_score by more than 1 percentage point versus the strongest direct IAD baseline on the same evaluation split.; Failure if tool_success_rate is below 90%, if shuffled-reference negative control matches the full method, or if gains are explained only by a lower operating threshold.

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W4404704036

Risks, controls, or fallback:
Risk: synthetic shift and contamination may not reflect real factory drift, and reference-bank outlier scores may confuse rare but valid normal appearances with contamination. Fallback: report results separately for natural category-level shifts, acquisition-condition shifts, placebo normal injections, and injected contamination, and position the module as a reference-bank diagnostic and escalation aid rather than a universal detector if detection AUROC does not improve.

---

Idea 2
Title:
Disagreement-Gated Mask Selection Agent for Weakly Labeled Defect Localization

Core proposal:
Use an inspection agent that converts IAD heatmap peaks into prompts, obtains candidate masks from SAM or SAM2, optionally obtains text-conditioned boxes from GroundingDINO when a defect taxonomy is available, and accepts a mask only if it is supported by anomaly heatmaps and remains stable under negative-control transformations. The agent refuses or escalates masks that mostly follow object borders, illumination changes, or normal texture regions.

Motivation or baseline weakness:
SAM/SAM2 can segment salient object parts rather than true defects, while IAD heatmaps from PatchCore, DRAEM, FastFlow, or AnomalyCLIP can produce noisy regions under texture, lighting, or boundary variation. With weak or missing pixel labels, selecting a trustworthy defect mask requires checks that distinguish localized defect evidence from generic saliency.

Mechanism or approach:
A mask-selection policy that scores each candidate mask m by U(m)=w1*heatmap_overlap(m)+w2*semantic_anomaly_support(m)+w3*normal_contrast(m)-w4*negative_control_instability(m)-w5*border_saliency_penalty(m)-w6*area_prior_penalty(m). heatmap_overlap is computed from frozen IAD heatmaps, semantic_anomaly_support from AnomalyCLIP or CLIP-style prompts when available, normal_contrast from same-class normal reference patches, and negative_control_instability from brightness, color, blur, crop, and normal-image placebo tests.
Select the smallest evidence-supported region that maximizes defect_region_precision and mask_iou while constraining missed defects. Tune mask thresholds and refusal thresholds on validation data to maximize calibrated mask utility under a minimum defect_region_recall constraint and an explicit human_review_budget.

Experiment and implementation plan:
PatchCore; DRAEM; FastFlow; AnomalyCLIP; SAM; SAM2; GroundingDINO; thresholded strongest IAD heatmap
MVTec_AD or VisA images; pixel masks where available for evaluation only; product_category labels; optional defect taxonomy for text prompts; normal reference images for same-class negative contrast; image augmentations for lighting, blur, color, crop, border, and texture negative controls; normal-only images used as placebo prompts to estimate false mask acceptance
generate_iad_heatmaps.py; prompt_sam_from_heatmaps.py; generate_groundingdino_candidates.py; compute_cross_model_disagreement.py; run_negative_control_augmentations.py; select_or_refuse_mask.py; evaluate_mask_and_region_metrics.py; emit_region_grounded_report.py
pixel_level_auroc; pro_score; mask_iou; defect_region_precision; defect_region_recall; f1_score; tool_success_rate; report_correctness; evidence_grounding_score; false_alarm_reduction; human_escalation_precision; selective_risk
SAM/SAM2 refinement without the mask-selection policy; mask-selection policy without negative-control augmentations; single IAD heatmap support instead of cross-model agreement or disagreement checks; no retrieved normal-patch contrast; always accept the top SAM or SAM2 mask; always accept the thresholded heatmap mask; disable escalation for low-agreement masks; remove border_saliency_penalty and area_prior_penalty
Use SAM2 refinement directly on IAD heatmap prompts without disagreement scoring, negative-control tests, or refusal; this tests whether segmentation alone is responsible for any gain.; Run the full mask-selection policy on normal-only images and on masks prompted from low-score heatmap locations; accepted-mask rate should remain low.; Apply brightness and color jitter that should not create a physical defect; accepted defect masks should be stable or refused rather than moving to illumination artifacts.
Improve mask_iou by at least 5 absolute points or defect_region_precision by at least 10% versus the thresholded strongest IAD heatmap on MVTec_AD or VisA.; Reduce false positive regions from lighting, texture, or border perturbations by at least 10% at matched defect_region_recall.; Maintain image_level_auroc within 1 point of the strongest IAD baseline when mask selection is used only for localization and reporting.; Improve evidence_grounding_score over the non-agent mask-report baseline by at least 15%.; Failure if SAM/SAM2-only negative control matches the full agent on localization and agent workflow metrics, or if normal-only placebo acceptance is not lower than anomalous-image acceptance.

Evidence paper IDs:
openalex:W4380551232; openalex:W7154655652; openalex:W7162893906; openalex:W7153670799

Risks, controls, or fallback:
Risk: candidate masks may be dominated by object boundaries instead of defects, especially for small scratches or low-contrast defects, and GroundingDINO text prompts may be unreliable when the defect taxonomy is incomplete. Fallback: restrict the module to region proposal verification, keep the original IAD heatmap as the primary localization output, disable text-prompted boxes when no defect vocabulary is available, and escalate small high-score regions when mask agreement is unreliable.

---

Idea 3
Title:
Evidence-Grounded Report Checker with Selective Human Escalation

Core proposal:
Add a report-verification agent that converts detector outputs and optional VLM drafts into structured claims, then verifies each claim against an anomaly region, same-class normal reference evidence, and calibrated model scores. Unsupported claims are removed, downgraded to failure_warning, or routed to human_review. The report is accepted only when claim-region-reference links pass grounding and confidence checks.

Motivation or baseline weakness:
WinCLIP, AnomalyCLIP, and VLM-style inspection agents can generate plausible defect descriptions that are not supported by localized visual evidence. Conventional IAD baselines output scores and heatmaps but lack calibrated report confidence, claim-level evidence checks, and selective human escalation behavior.

Mechanism or approach:
A structured report checker that validates claim-region-reference triples and calibrates report confidence using validation-set conformal or quantile thresholds over detector confidence, region overlap consistency, and reference-evidence contrast. It outputs anomaly_score, anomaly_mask_or_region, defect_type when supported, evidence, normal_reference_used, confidence, recommended_action, and failure_warning. If defect_type is not supported by dataset labels or grounded visual evidence, the field is set to unknown_defect rather than hallucinated.
Optimize selective reporting by minimizing report_error and unsupported_claim_rate under a fixed human_review_budget, while preserving image_level_auroc, pixel_level_auroc, and defect_region_recall relative to the underlying IAD baselines. The selective policy chooses accept_normal, reject_defective, or human_review using calibrated confidence and claim-grounding validity rather than free-form language confidence.

Experiment and implementation plan:
WinCLIP; AnomalyCLIP; PatchCore; PaDiM; CLIP-style prompt report baseline; unchecked VLM or template report baseline; anomaly-score-only escalation baseline
MVTec_AD or VisA images; product_category labels; normal reference images; optional defect taxonomy; optional mask or bounding-box labels for region grounding evaluation; inspection_goal text such as reject, repair, or reinspect; human-audited subset for report semantics when public labels do not specify defect descriptions
run_iad_baselines.py; retrieve_reference_evidence.py; draft_vlm_report.py; check_claim_region_reference_links.py; calibrate_confidence_and_selective_policy.py; route_human_escalation.py; score_report_correctness_and_grounding.py; export_structured_inspection_report.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; report_correctness; evidence_grounding_score; human_escalation_precision; false_alarm_reduction; calibration_error; selective_risk; out_of_distribution_detection
VLM or template report without evidence checker; evidence checker without retrieved normal references; confidence calibration using anomaly_score only; escalation based only on anomaly_score; remove failure_warning field; replace structured schema with free-form report; use report checker on random regions; force every case to be accepted with no human_review option
Generate a VLM or template report from the same anomaly score and mask but remove claim-region-reference verification and selective escalation; compare report correctness, unsupported claims, and human escalation precision.; Shuffle normal reference patches across product categories before report checking; grounding and confidence should degrade rather than remain unchanged.; Attach defect claims to random low-score regions; the checker should reject or mark the claims as unsupported.
Improve evidence_grounding_score by at least 20% versus unchecked VLM or template reports generated from the same detector outputs.; Reduce unsupported defect descriptions by at least 30% without reducing defect_region_recall by more than 2 points.; Achieve at least 10% relative lower calibration_error than raw IAD confidence or anomaly-score-only report confidence.; At a fixed human review budget, improve selective_risk or false_alarm_reduction over anomaly-score-only escalation.; Failure if report_correctness or evidence_grounding_score does not improve over the non-agent negative control, or if shuffled-reference and random-region controls pass verification at the same rate as true evidence links.

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W7154655652; openalex:W7153328271; openalex:W7138099583

Risks, controls, or fallback:
Risk: automatic report correctness labels may be noisy because public IAD datasets have limited defect taxonomies, and generic VLM drafts may over-specify defect types not present in labels. Fallback: evaluate claim grounding objectively through region-reference links, force unsupported defect categories to unknown_defect, use a small human audit subset only for report semantics, and keep detection and localization experiments fully reproducible on MVTec_AD or VisA.

### Candidate B

Idea 1
Title:
Reference-Consistency Inspection Agent for Shifted or Contaminated Normal Memory Banks

Core proposal:
Add a reference-consistency inspection loop around an existing industrial anomaly detector. For each high-scoring test region, the system retrieves top-k normal reference patches, computes test-to-reference similarity, reference-to-reference cohesion, prototype compatibility, and bank-split stability, then decides whether to accept the base anomaly score, suppress a likely benign shift, or escalate because the retrieved evidence is unstable. The module never changes the detector backbone; it only calibrates or refuses decisions whose anomaly score depends on unreliable references.

Motivation or baseline weakness:
PatchCore, PaDiM, FastFlow, and RD4AD depend on a normal reference distribution that is assumed to be clean and deployment-compatible. When the normal memory bank contains shifted samples, mislabeled defects, or factory-specific appearance changes, these methods can over-score benign regions or under-score true defects without any explicit mechanism to audit the reference neighborhood that drives the decision.

Mechanism or approach:
Reference Consistency and Bank Audit module. Inputs are a candidate region, its anomaly score, top-k retrieved normal patches, held-out clean normal patches, and category prototypes. Outputs are retrieval_consistency_score, reference_cohesion_score, prototype_compatibility_score, contamination_flag, and decision_modifier. The core score is sim(test_region, top_k_normals) normalized by the cohesion of top_k_normals against held-out normals, with a separate flag when retrieved references are mutually inconsistent or inconsistent with category-level prototypes.
For each candidate region r, compute calibrated score s_prime(r)=base_iad_score(r)*g(retrieval_consistency_score, reference_cohesion_score, prototype_compatibility_score, contamination_flag). Learn g and selective escalation thresholds on validation splits to reduce false alarms at matched defect recall while forcing human_review when the bank audit indicates unreliable evidence rather than automatically passing the sample.

Experiment and implementation plan:
PatchCore; PaDiM; FastFlow; RD4AD; non-agent PatchCore with static memory bank; retrieval-only inspection without bank audit
MVTec_AD test images with product category and optional masks; VisA test images with product category and optional masks; normal reference images split into clean bank, shifted bank, and synthetically contaminated bank; validation normals for calibration and bank audit thresholds; optional defect taxonomy for report labels; inspection goal specifying reject, review, or pass decision
build_reference_bank.py to create clean, shifted, and contaminated normal banks; run_iad_baselines.py for PatchCore, PaDiM, FastFlow, and RD4AD anomaly maps; retrieve_region_references.py for patch-level top-k normal retrieval; audit_reference_bank.py for reference cohesion, prototype compatibility, and contamination scoring; calibrate_reference_policy.py for score modifier and selective escalation thresholds; agent_inspection_loop.py with tools: iad_detector, region_proposer, reference_retriever, bank_auditor, calibration_tool, report_generator, escalation_policy; evaluate_detection_localization_agent.py for AUROC, AUPR, PRO, IoU, tool success, grounding, false-alarm reduction, and escalation precision
image_level_auroc; pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; false_alarm_reduction at matched recall; reference_contamination_auroc; tool_success_rate for retrieval and bank audit calls; evidence_grounding_score linking anomalous regions to retrieved normal references; human_escalation_precision; calibration_error; selective_risk
remove reference bank audit while keeping retrieval; use unnormalized test-to-normal similarity without reference-to-reference consistency; remove prototype compatibility while keeping top-k cohesion; replace calibrated selective policy with fixed anomaly threshold; vary contamination rate in normal memory bank; vary number of retrieved references k; evaluate clean-bank, shifted-bank, and contaminated-bank settings separately; allow low-consistency regions to be passed instead of escalated
non-agent PatchCore or RD4AD with identical anomaly maps and no retrieval verification; random normal-reference retrieval with the same report template and same number of retrieved patches; agent report generation using retrieved images but without retrieval_consistency_score or bank audit outputs; bank audit run after the final decision and not allowed to change prediction, calibration, or escalation; shuffled category prototypes used for audit to test whether gains come from valid category compatibility
At matched image-level recall, reduce false positives by at least 15% versus the strongest direct IAD baseline on MVTec_AD or VisA; Improve or preserve pixel_level_auroc within 1 percentage point while improving PRO score on shifted-bank evaluation; Detect contaminated reference banks with AUROC above 0.80 in synthetic contamination experiments; Improve evidence_grounding_score by at least 20% over retrieval-only report generation; Human escalation precision must exceed the non-agent uncertainty-threshold baseline by at least 10% at the same review budget; Failure if gains appear only under contaminated-bank settings and disappear on clean-bank and shifted-bank settings

Risks, controls, or fallback:
Risk: synthetic bank contamination or proxy factory shift may not reflect real deployment shift, making the audit overfit to artificial artifacts. Fallback: construct multiple proxy shifts using lighting, color, camera blur, compression, and cross-dataset normal-bank swaps, and report success only when improvements hold across at least two shift types. Risk: reference-consistency suppression may hide subtle real defects. Fallback: low-consistency cases become human_review rather than automatic pass decisions, and thresholds are optimized under matched recall constraints.

---

Idea 2
Title:
Disagreement-Gated Mask Selection Agent for Weakly Labeled Defect Localization

Core proposal:
Use a self-verifying mask selection agent that proposes candidate masks from high-anomaly heatmap regions and negative-control masks from low-anomaly regions. Each candidate is scored by heatmap support, boundary plausibility, normal-reference contrast, defect-text compatibility constrained to an allowed taxonomy, and cross-model agreement. The agent emits a mask only when positive evidence is stronger than matched negative-control evidence; otherwise it returns a coarse region or human_review instead of a precise unsupported mask.

Motivation or baseline weakness:
SAM or SAM2 can produce many plausible masks around texture edges, shadows, specular highlights, and object boundaries. IAD heatmaps from RD4AD, DRAEM, WinCLIP, or AnomalyCLIP can be spatially noisy, especially when only image-level or sparse labels are available. Naive SAM refinement usually selects masks by heatmap overlap alone and lacks explicit checks that the selected mask is defect-supported rather than a normal structure.

Mechanism or approach:
Cross-Model Disagreement Mask Selector. Inputs are IAD heatmaps, SAM or SAM2 candidate masks, retrieved normal patches for each candidate, low-anomaly negative-control masks, optional text labels, and category metadata. Outputs are selected_mask, mask_confidence, disagreement_score, negative_control_margin, and refusal_reason. The selector penalizes masks whose evidence resembles low-anomaly masks or whose support is concentrated only on normal boundaries.
Maximize calibrated region utility U(m)=alpha*IAD_support(m)+beta*normal_contrast(m)+gamma*taxonomy_text_score(m)+eta*boundary_quality(m)-lambda*negative_control_score(m)-delta*cross_model_disagreement(m). Select the highest-utility mask only if its confidence and negative-control margin exceed validation-calibrated thresholds; otherwise output a coarse heatmap region or refuse under a selective-risk constraint. Optimize for higher mask IoU and defect-region precision while maintaining at least the baseline heatmap recall.

Experiment and implementation plan:
RD4AD; DRAEM; WinCLIP; AnomalyCLIP; SAM; SAM2; GroundingDINO plus SAM; heatmap thresholding without mask proposal; SAM refinement without mask selection policy
MVTec_AD images with product category and pixel masks where available; VisA images with product category and pixel masks where available; normal images for low-anomaly negative-control mask sampling; normal reference images for retrieved-normal contrast; optional sparse bbox or image-level labels converted to weak localization targets; optional defect taxonomy for constrained text prompts and report labels; validation split for calibrating selection and refusal thresholds
run_iad_heatmaps.py for RD4AD, DRAEM, WinCLIP, and AnomalyCLIP maps; propose_candidate_masks.py using SAM or SAM2 from heatmap prompts and low-anomaly negative-control prompts; retrieve_normal_patches_for_masks.py; score_mask_disagreement.py for heatmap support, boundary quality, retrieval contrast, text compatibility, and negative-control margin; calibrate_mask_selector.py for utility weights and selective thresholds; agent_mask_verification_loop.py with tools: iad_detector, mask_proposer, normal_retriever, disagreement_scorer, calibration_tool, report_checker, escalation_policy; evaluate_mask_selection.py for IoU, PRO, precision, recall, grounding, and selective risk
pixel_level_auroc; pro_score; mask_iou; defect_region_precision; defect_region_recall; f1_score; false_positive_mask_rate_on_normals; negative_control_margin; tool_success_rate for mask proposal and verification; evidence_grounding_score linking selected masks to heatmaps and references; report_correctness; human_escalation_precision; calibration_error; selective_risk
remove negative-control masks from low-anomaly regions; remove retrieved-normal contrast term; remove cross-model disagreement penalty; remove boundary quality term; use only SAM mask with maximum heatmap overlap; use only VLM or CLIP text compatibility for mask selection; evaluate with full masks versus sparse bbox-derived weak labels; vary selective refusal threshold and measure risk-coverage tradeoff; force a precise mask even when the selector would output a coarse region or refuse
SAM2 refinement driven by IAD heatmap prompts without selection policy; randomly selected SAM candidate among top heatmap-prompted masks; mask selector trained or calibrated with negative-control masks treated as positives to test leakage; mask selector using shuffled heatmaps while keeping the same candidate masks; report generator that describes selected mask without evidence-grounded checking
Improve mask_iou by at least 5 absolute points over heatmap thresholding on MVTec_AD or VisA categories with masks; Improve defect_region_precision by at least 10% while maintaining at least 95% of baseline defect_region_recall; Reduce false positive masks on low-anomaly normal images by at least 20% versus SAM refinement without negative controls; Achieve higher evidence_grounding_score than VLM-only report generation by at least 15%; Tool_success_rate for mask proposal and verification must remain at or above 90% on standard images; Failure if localization improves only through lower recall, if negative controls do not reduce false masks, or if gains vanish when text compatibility is disabled

Risks, controls, or fallback:
Risk: segmentation candidates may be poor for tiny, transparent, or low-contrast defects, limiting the selector regardless of scoring. Fallback: allow heatmap-only boxes or coarse regions as valid outputs when all masks fail verification, and evaluate mask quality separately from region quality. Risk: text compatibility may hallucinate defect types. Fallback: constrain labels to the optional taxonomy and require evidence-grounded checking before emitting a defect_type; otherwise output unknown_defect and escalate.

---

Idea 3
Title:
Evidence-Grounded Selective Reporting Agent for Human-in-the-Loop Quality Control

Core proposal:
Build a selective reporting agent that converts anomaly scores, heatmaps, retrieved normal references, candidate regions or masks, and defect-taxonomy constraints into a structured quality-control report. Before any reject decision, a claim-level evidence checker validates each proposed defect statement against the cited image region, anomaly support, normal-reference contrast, and model agreement. Unsupported claims are removed, downgraded to unknown_defect, or converted into human_review with a failure_warning.

Motivation or baseline weakness:
VLM-based inspection reports can describe unsupported defects, while IAD models such as PatchCore, RD4AD, WinCLIP, and AnomalyCLIP produce scores and heatmaps without deciding whether evidence is sufficient for autonomous pass or reject. Simple uncertainty thresholds do not verify claim-level grounding and can send either easy positives or noisy false alarms to human review.

Mechanism or approach:
Claim-Region-Reference Evidence Checker plus Selective Escalation Policy. The checker parses each report claim into defect_type, region_or_mask, evidence_links, normal_reference_ids, confidence, and recommended_action. It validates that the cited region has sufficient anomaly support, that retrieved normal references differ in the claimed way, and that the claim uses an allowed taxonomy label. The escalation policy then chooses pass, reject, or human_review using calibrated claim confidence and operational costs.
Minimize expected cost C=c_false_pass*FN+c_false_reject*FP+c_review*Review+c_unsupported*UnsupportedClaim subject to minimum defect recall and minimum evidence-grounding constraints. Calibrate confidence and action thresholds on validation normals and rare anomalies, then evaluate selective risk, report grounding, false-alarm reduction, and escalation precision on held-out categories or held-out product splits.

Experiment and implementation plan:
PatchCore; RD4AD; WinCLIP; AnomalyCLIP; LLaVA or Qwen-VL report generation without evidence checker; uncertainty-threshold escalation without claim verification; RAG report generation using normal references without selective policy
MVTec_AD images and masks or image-level labels; VisA images and masks or image-level labels; normal reference images per product category; optional defect taxonomy mapping visual defects to allowed report labels; held-out validation split for calibration with rare anomalies; inspection goal defining cost of pass, reject, and review; human-review budget for matched-budget selective evaluation
run_iad_and_vlm_baselines.py for anomaly maps, scores, candidate regions, and draft reports; build_normal_reference_index.py; generate_structured_report.py with schema fields anomaly_score, anomaly_mask_or_region, defect_type, evidence, normal_reference_used, confidence, recommended_action, failure_warning; check_report_evidence.py for claim-region-reference validation; calibrate_selective_policy.py for confidence calibration, action costs, and risk-coverage tuning; agent_quality_control_loop.py with tools: iad_detector, region_localizer, normal_retriever, report_generator, evidence_checker, calibrator, human_escalation_policy; evaluate_reporting_and_escalation.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; f1_score; mask_iou; report_correctness; unsupported_claim_rate; evidence_grounding_score; false_alarm_reduction at matched recall; human_escalation_precision; review_rate; tool_success_rate; calibration_error; selective_risk; out_of_distribution_detection
remove claim-region-reference evidence checker; remove normal-reference retrieval from report evidence; replace selective escalation policy with fixed anomaly-score threshold; allow open-ended VLM defect labels instead of taxonomy-constrained labels; remove cross-model disagreement from confidence calibration; compare report-level refusal versus forced defect_type output; evaluate with sparse labels only versus available pixel masks; keep evidence checking but prevent it from changing pass, reject, or human_review decisions
VLM generates structured report from the test image and anomaly score only; RAG report includes normal references but does not verify region-level evidence; selective policy trained on shuffled evidence links; human_review assigned randomly at the same review rate as the proposed policy; evidence checker receives shuffled region masks while report text is unchanged
At matched defect recall, reduce false reject or false alarm rate by at least 15% compared with the best non-agent IAD baseline; Improve evidence_grounding_score by at least 25% over VLM report generation without evidence checking; Unsupported defect descriptions must decrease by at least 30% under taxonomy-constrained reporting; Human escalation precision must improve by at least 10% over anomaly-score uncertainty thresholding at the same review budget; Calibration error must not worsen relative to the strongest calibrated non-agent baseline; Failure if report metrics improve without detection or localization parity, if escalation mostly captures easy positives rather than ambiguous cases, or if the evidence checker rejects correct claims too often

Risks, controls, or fallback:
Risk: structured report evaluation may be noisy if defect taxonomies are incomplete or labels are sparse. Fallback: evaluate both strict taxonomy correctness and evidence-grounded region correctness, and permit unknown_defect when the region is well supported but the label is uncertain. Risk: the selective policy may over-escalate to improve apparent accuracy. Fallback: report risk-coverage curves, fixed review-budget results, and escalation precision at matched review rates.

---

## Item 12: HUM-690d58f500

类型：`portfolio`

### Candidate A

Idea 1
Title:
Reference-Bank Auditing Agent for Shift- and Contamination-Robust Industrial Anomaly Detection

Core proposal:
Build an agentic IAD workflow that treats the normal-reference memory bank as an inspectable object rather than a fixed resource. The agent retrieves nearest normal patches for each suspicious test region, estimates whether those references are factory-shifted or contaminated, prunes unreliable references, recomputes anomaly evidence, and emits a structured report with calibrated confidence and escalation decisions. The output is an anomaly score, region mask, defect type hypothesis, retrieved normal evidence, confidence, recommended action, and failure warning when reference quality is insufficient.

Motivation or baseline weakness:
PatchCore-style nearest-neighbor memory is strong for MVTec AD and VisA, but it can fail when the normal bank contains subtle defects or when lighting, texture, or supplier changes shift the normal distribution. Existing VLM or agentic IAD work motivates tool use and semantic reporting, but a publishable gap remains: agents rarely verify whether their retrieved normal evidence is trustworthy before using it to justify a defect report. This idea directly targets normal-reference shift, contaminated memory banks, false-positive texture heatmaps, and when to escalate to human review.

Mechanism or approach:
Direct baselines: PatchCore, PaDiM, RD4AD, WinCLIP, AnomalyCLIP. Transfer baselines: CLIP retrieval, SAM/SAM2 promptable masks, tool-using agent, retrieval-augmented generation. Borrowed components: frozen PatchCore or PaDiM heatmaps for candidate regions, CLIP/DINO-style embeddings for reference retrieval, SAM or SAM2 only for mask proposal refinement, and a lightweight VLM for report drafting. New component: a Reference Integrity Agent with three scores: retrieval-consistency score between the test region and top-k normal patches, reference-bank contamination score computed by leave-one-reference-out anomaly ranking inside the normal bank, and factory-shift score based on distributional mismatch between current test normals and stored references. Agent steps: (1) run IAD heatmap tools; (2) propose suspicious regions; (3) retrieve normal reference patches and metadata; (4) audit retrieved references for contamination and shift; (5) discard or downweight suspicious references; (6) recompute anomaly score and mask; (7) run cross-model verification with PatchCore versus WinCLIP/AnomalyCLIP; (8) calibrate confidence with temperature scaling or conformal selective prediction on normal validation data; (9) generate a structured report schema containing anomaly_score, anomaly_mask_or_region, defect_type, evidence, normal_reference_used, confidence, recommended_action, and failure_warning; (10) escalate if reference integrity is low, model disagreement is high, or calibrated confidence is below threshold. Minimal new module: reference audit scorer plus policy rules for pruning and escalation. Negative control: same IAD and report generator using unverified top-k references with no audit or pruning.

Experiment and implementation plan:
Datasets: start with MVTec AD and VisA; optionally add BTAD and MPDD for cross-factory robustness. Construct proxy reference shift by splitting normal images by lighting/background/product pose when available, or by applying controlled brightness, blur, color-temperature, and texture augmentations to normal banks. Construct contamination by injecting 1%, 5%, and 10% anomalous training images or masked anomalous patches into the normal memory. Metrics: image_level_auroc, pixel_level_auroc, aupr, pro_score, f1_score, mask_iou, defect_region_precision, defect_region_recall, calibration_error, selective_risk, out_of_distribution_detection, tool_success_rate, report_correctness, evidence_grounding_score, false_alarm_reduction, and human_escalation_precision. Ablations: no reference audit, no contamination detection, no shift score, no cross-model disagreement, no calibration, no SAM/SAM2 refinement, fixed versus learned/pruned reference weighting, and report without evidence links. Mask-selection policy: accept SAM/SAM2 masks only if they overlap high-IAD-score connected components, improve boundary compactness, and do not also appear anomalous on retrieved normal references; negative control prompts SAM/SAM2 on normal images and requires low anomaly acceptance. Failure criteria: reject the idea if agent metrics do not improve over the non-agent PatchCore or PaDiM pipeline, if evidence_grounding_score does not improve, if false_alarm_reduction is achieved only by lowering recall, or if the audit reduces pixel-level localization by more than a predefined tolerance at matched image-level recall. MVP artifacts: reference-audited memory bank, candidate-region viewer, JSON report generator, calibration curves, contamination benchmark scripts, and human-escalation dashboard.

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W7154655652; openalex:W4404704036; openalex:W4380551232

---

Idea 2
Title:
Disagreement-Guided Inspection Agent with Evidence-Grounded Report Checking

Core proposal:
Develop an agent that uses cross-model disagreement as a self-verification signal before producing industrial defect descriptions. The system compares heatmaps and semantic labels from complementary IAD models, retrieves normal references for the disputed region, requests segmentation masks only when the region is stable under verification, and runs an evidence-grounded report checker that rejects unsupported VLM claims. The final output includes localized anomaly evidence and a report that explicitly links each defect claim to image regions and normal references.

Motivation or baseline weakness:
Industrial reports from VLM-style anomaly systems can sound plausible while being unsupported by localized visual evidence. Conversely, classical IAD heatmaps can overreact to benign texture or illumination changes. A promising research gap is not simply adding a VLM report to PatchCore, but making the agent verify whether the visual, retrieval, and textual evidence agree. Cross-model disagreement can identify fragile detections and drive selective prediction or human escalation.

Mechanism or approach:
Direct baselines: PatchCore, FastFlow, DRAEM, RD4AD, WinCLIP, AnomalyCLIP. Transfer baselines: CLIP image-text scoring, Qwen-VL or LLaVA-style report drafting, SAM/SAM2 for mask candidates, GroundingDINO for optional phrase-to-region checks, retrieval-augmented generation. Borrowed components: frozen IAD models for anomaly maps, frozen VLM for defect-type hypotheses, segmentation tools for region proposals, and retrieval over normal images. New component: a Disagreement-Guided Verification Loop with an Evidence-Grounded Report Checker. Agent tool list: IAD scorer, candidate connected-component extractor, normal-reference retriever, SAM/SAM2 mask proposer, CLIP/VLM defect-label proposer, cross-model heatmap comparer, report checker, calibration module, and escalation policy. Memory/retrieval state stores retrieved normal patches, model heatmaps, proposed masks, defect-label candidates, and rejected claims. Verification loop: (1) compute anomaly maps from at least two heterogeneous IAD models; (2) form candidate regions where at least one model is high; (3) calculate cross-model disagreement from region rank changes, heatmap IoU, and semantic label entropy; (4) retrieve normal references for each candidate; (5) ask the VLM to generate only region-conditioned defect hypotheses; (6) checker verifies each claim by requiring a link to a candidate mask, a contrast with retrieved normal references, and consistency with at least one IAD heatmap; (7) unsupported claims are removed or converted into failure_warning; (8) calibrated confidence combines anomaly magnitude, retrieval consistency, and disagreement; (9) escalation triggers when disagreement is high, report claims are unsupported, or the defect taxonomy is missing. Minimal new module: evidence graph plus claim-to-region/reference verifier. Negative control: same models with a single-pass VLM report and no disagreement loop or claim checker.

Experiment and implementation plan:
Datasets: MVTec AD and VisA first, with MVTec LOCO for logical anomalies where model disagreement may be especially informative. Use provided defect masks where available; when pixel labels are sparse, evaluate pseudo-region stability and image-level correctness while reserving labeled subsets for mask_iou and pro_score. Metrics: image_level_auroc, pixel_level_auroc, aupr, pro_score, f1_score, mask_iou, defect_region_precision, defect_region_recall, tool_success_rate, report_correctness, evidence_grounding_score, false_alarm_reduction, human_escalation_precision, calibration_error, and selective_risk. Report evaluation: each generated defect claim must cite a region ID and one or more normal-reference IDs; human or rule-assisted grading checks whether the claim is visually supported. Ablations: remove cross-model disagreement, remove normal retrieval, remove report checker, remove calibration, use one IAD model only, allow free-form VLM descriptions, and replace selective escalation with fixed thresholding. Mask-selection policy: choose SAM/SAM2 masks only if they maximize agreement with connected high-score anomaly components while minimizing overlap with normal-reference saliency maps; negative control runs the same mask selection on known-normal test images and requires low accepted-defect rate. Failure criteria: the proposal fails if evidence_grounding_score and report_correctness do not improve over the non-agent report baseline, if tool_success_rate is low enough to break production usability, or if selective prediction reduces false alarms only by escalating most samples. MVP artifacts: disagreement heatmap visualizer, evidence graph JSON, structured report checker, defect-claim audit interface, and matched-recall false-alarm benchmark.

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W7154655652; openalex:W7153328271; openalex:W7138099583; openalex:W4380551232

---

Idea 3
Title:
Selective Human-Escalation Agent for Weakly Labeled Industrial Defect Localization

Core proposal:
Create an inspection agent optimized for sparse pixel labels and production triage. The agent combines frozen IAD heatmaps, retrieval consistency, segmentation mask selection, and calibrated selective prediction to decide among accept, reject, or escalate-to-human. Unlike a pure anomaly detector, the method explicitly optimizes false-alarm reduction at matched recall and measures whether escalations are precise, evidence-rich, and useful to human reviewers.

Motivation or baseline weakness:
Many factories have image-level pass/fail logs or occasional bounding boxes but lack dense defect masks. In this setting, anomaly maps are noisy, VLM descriptions may be unsupported, and the most valuable system behavior may be knowing when not to decide. The research gap is an agent workflow that converts weak localization evidence into calibrated triage decisions and structured reports, while proving improvement with agent-specific metrics rather than only AUROC.

Mechanism or approach:
Direct baselines: PatchCore, PaDiM, FastFlow, DRAEM, WinCLIP, AnomalyCLIP. Transfer baselines: SAM/SAM2 for candidate masks, Mask2Former when supervised masks are available for an upper-bound segmentation baseline, CLIP/VLM models for taxonomy alignment, and retrieval-augmented inspection. Borrowed components: frozen anomaly heatmaps, promptable segmentation, normal-reference retrieval, and lightweight VLM report generation. New component: a Selective Escalation Policy trained or tuned with weak labels to minimize false alarms under matched defect recall. Agent components: tool list includes IAD scorer, region proposal extractor, normal-reference retriever, mask selector, defect-taxonomy matcher, confidence calibrator, report generator, and escalation/refusal policy. Memory/retrieval state tracks region candidates, normal references, uncertainty features, calibration history, and human feedback outcomes. Verification loop: (1) generate candidate anomaly regions from IAD heatmaps; (2) retrieve normal patches and compute retrieval-consistency contrast; (3) propose SAM/SAM2 masks and select masks using anomaly-map overlap, normal-reference negative control, shape plausibility, and stability under augmentations; (4) infer defect type only if the taxonomy match is grounded in the selected region; (5) calibrate confidence using validation normals and sparse labels; (6) choose accept/reject/escalate based on selective risk; (7) generate structured report with failure_warning if labels, references, or confidence are insufficient; (8) incorporate optional human feedback to update thresholds, not backbone weights. Minimal new module: selective triage head over uncertainty, disagreement, and retrieval-consistency features. Negative control: identical IAD detector with fixed threshold and no agentic escalation or verification.

Experiment and implementation plan:
Datasets: MVTec AD and VisA first; use full masks for evaluation but simulate weak supervision by hiding most pixel labels during threshold and policy development. Add MVTec LOCO for logical anomalies and BTAD or MPDD for industrial transfer if time allows. Weak-label protocol: tune the selective policy using image-level labels plus 5% or 10% mask/bbox labels, and test on held-out dense masks. Metrics: image_level_auroc, pixel_level_auroc, aupr, pro_score, f1_score, mask_iou, defect_region_precision, defect_region_recall, false_alarm_reduction at matched recall, human_escalation_precision, report_correctness, evidence_grounding_score, calibration_error, selective_risk, and out_of_distribution_detection. Ablations: no selective policy, no retrieval consistency, no SAM/SAM2 mask selection, no negative control, no taxonomy grounding, no human-feedback threshold update, and dense-label upper bound with Mask2Former. Proxy human-review experiment: sampled escalations are scored for whether the report contains sufficient region, normal-reference, and confidence evidence for a quality engineer to decide quickly. Failure criteria: fail if the selective agent does not reduce false alarms at fixed recall compared with PatchCore or PaDiM, if human_escalation_precision is not higher than random/high-score escalation, if evidence_grounding_score does not exceed the non-agent report baseline, or if mask selection improves IoU only on labeled classes while increasing false positives on normal images. MVP artifacts: weak-label split generator, triage policy evaluator, escalation queue UI mock, structured report schema, calibration and selective-risk plots, and a reproducible MVTec AD/VisA benchmark script.

Evidence paper IDs:
openalex:W4404704036; openalex:W7162893906; openalex:W7154655652; openalex:W4380551232; openalex:W7153670799; openalex:W7153328271

### Candidate B

Idea 1
Title:
Reference-Consistency Agent for Shifted or Contaminated Normal Memory Banks

Core proposal:
Add an agentic retrieval-audit loop for memory-based industrial anomaly detection. The loop first runs a PatchCore or PaDiM heatmap tool, extracts suspicious connected regions, retrieves top-k normal reference patches from the same product category and comparable spatial neighborhood, computes whether the retrieved references are internally consistent and visually compatible with the test region, audits the normal bank for likely contamination using cross-reference anomaly scores, and escalates when the base anomaly score is high but the reference evidence is ambiguous. Agent steps: run IAD heatmap tool, retrieve normal references, audit retrieved references for contamination and category/position mismatch, verify suspicious regions with a second IAD or CLIP-style semantic anomaly tool, calibrate confidence, then emit a structured report linking each decision to test-region crops and reference patches.

Motivation or baseline weakness:
PatchCore and PaDiM depend on normal-reference feature memories or distribution estimates, so factory shift or contaminated normal reference images can make abnormal regions appear normal or shifted normal regions look defective. Patch-level heatmaps alone also do not verify whether a retrieved normal patch is a valid counterexample for the suspicious test region.

Mechanism or approach:
A lightweight Reference Consistency and Bank Audit module that stores retrieval state as {test_region_id, product_category, spatial_bin, top_k_reference_ids, patch_distances, reference_anomaly_scores, consistency_score, bank_disagreement_score, audit_flag} and outputs calibrated anomaly confidence plus accept, escalate, or refuse decisions.
Optimize selective anomaly prediction under reference shift by combining base anomaly score A(x), normal-reference consistency C(x,R), and contamination penalty B(R) into S = A(x) * (1 - C(x,R)) + lambda * B(R), where C is high only when same-category retrieved references are mutually consistent and visually compatible with the test region. Choose thresholds on held-out shifted-normal and contaminated-bank validation splits to reduce false alarms at matched recall and minimize calibration error relative to anomaly-score-only calibration.

Experiment and implementation plan:
PatchCore; PaDiM; RD4AD; PatchCore plus non-agent top-k retrieval report; PaDiM plus fixed anomaly threshold
MVTec_AD train-normal and test anomaly images; VisA train-normal and test anomaly images; Constructed shifted-normal split using category-specific brightness, texture, viewpoint, compression, or factory-batch augmentations applied only to normal test images; Constructed contaminated-memory split by injecting 1%, 5%, and 10% anomalous patches or images into the normal bank while keeping clean-bank metadata for evaluation; Pixel masks or bounding boxes where available for region-level verification and grounding evaluation
build_patch_memory_bank.py; inject_contaminated_references.py; simulate_normal_reference_shift.py; run_iad_heatmaps.py; retrieve_region_references.py; audit_reference_bank.py; calibrate_selective_policy.py; generate_structured_inspection_report.py; evaluate_detection_localization_agent_metrics.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; false_alarm_reduction; tool_success_rate; evidence_grounding_score; human_escalation_precision; calibration_error; selective_risk; out_of_distribution_detection
Remove reference-bank audit while keeping nearest-neighbor retrieval; Use random same-category normal references instead of nearest retrieved references; Use anomaly score only without retrieval consistency; Use single IAD model verification instead of cross-model disagreement; Vary contamination rate and shift severity independently; Replace calibrated selective policy with a fixed anomaly threshold; Disable category and spatial-bin constraints during reference retrieval
Generate the same report schema from the PatchCore or PaDiM heatmap only, without retrieval audit or verification; Shuffle retrieved references across product categories while keeping report generation enabled; Allow the agent to cite reference identifiers but hide reference patches from the verifier; Inject clean normal patches labeled as contaminated and require the audit module not to over-escalate them; Use shifted normal images with no injected defects and measure whether the agent reduces, rather than increases, false alarms
On MVTec_AD or VisA, maintain at least 95% of the strongest direct baseline image_level_auroc while improving false_alarm_reduction by at least 15% on shifted-normal splits; Improve pixel_level_auroc or pro_score by at least 2 points over PatchCore or PaDiM on contaminated-bank splits; Reduce calibration_error by at least 10% relative to anomaly-score-only calibration; Achieve evidence_grounding_score of at least 0.80 for reports that cite normal references; Human_escalation_precision must exceed the non-agent heatmap-plus-report baseline by at least 10%; otherwise the agentic component is considered failed

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W4404704036; openalex:W7154655652

Risks, controls, or fallback:
Risk: reference consistency may reject legitimate rare normal variants or fail under severe domain shift, and contaminated-bank labels may be hard to infer without ground truth. Fallback: use category-specific conformal calibration, treat high internal reference disagreement as an escalation condition rather than an automatic anomaly decision, and report 'insufficient normal-reference support' instead of forcing a defect label.

---

Idea 2
Title:
Disagreement-Guided Mask Selection Agent for Weakly Labeled Defect Localization

Core proposal:
Use a mask-selection agent that treats SAM or SAM2 masks as candidates rather than final defect predictions. The agent detects suspicious peaks from IAD heatmaps, prompts SAM or SAM2 with points, boxes, and local crops around those peaks, scores each candidate mask using heatmap coverage, CLIP-style anomaly prompt support, same-category normal-reference contrast, and cross-model disagreement, then rejects masks that also activate on normal negative-control images. Agent steps: detect suspicious heatmap peaks, generate candidate masks, retrieve same-category normal region neighbors for each candidate, compute evidence and disagreement terms, run normal negative-control scoring, calibrate mask confidence, and generate a region-grounded report only for accepted masks.

Motivation or baseline weakness:
SAM and SAM2 can segment salient object parts rather than true defect regions, while WinCLIP and AnomalyCLIP can provide semantic anomaly cues without precise masks. This creates a task-domain mismatch when generic promptable masks are used as defect masks under sparse or missing pixel-level labels.

Mechanism or approach:
A Mask Evidence Selection Policy that ranks candidate masks by E(mask) = heatmap_coverage + semantic_anomaly_support + reference_mismatch - normal_negative_control_activation - cross_model_disagreement - saliency_only_penalty, with a refusal threshold when evidence is insufficient or when the selected mask mostly covers normal object structure rather than a localized defect.
Maximize defect_region_precision at fixed defect_region_recall using weak supervision from image labels and a small calibration subset of sparse masks. The selected mask must be jointly supported by IAD heatmaps, VLM anomaly prompts, and retrieved normal-reference contrast, while masks that activate on normal negative controls or disagree strongly across tools are penalized. Full pixel masks are used for evaluation, not for training the main selection policy except in the declared calibration subset.

Experiment and implementation plan:
SAM; SAM2; PatchCore; RD4AD; WinCLIP; AnomalyCLIP; SAM2 refinement without mask selection policy; Heatmap thresholding without SAM or SAM2 refinement
MVTec_AD images with pixel masks reserved for evaluation and limited calibration only; VisA images with image-level labels and available sparse masks or pixel masks reserved for evaluation; Optional defect taxonomy for text prompts, restricted to dataset-supported product and defect labels; Normal reference images for negative-control mask scoring; Synthetic sparse-label setting using 5%, 10%, and 20% of available masks for calibration only
run_patchcore_rd4ad_heatmaps.py; generate_sam_candidate_masks.py; prompt_clip_anomaly_scores.py; retrieve_normal_region_neighbors.py; score_mask_evidence.py; run_normal_negative_controls.py; calibrate_mask_confidence.py; generate_region_grounded_report.py; evaluate_mask_and_agent_metrics.py
pixel_level_auroc; pro_score; mask_iou; defect_region_precision; defect_region_recall; aupr; f1_score; tool_success_rate; evidence_grounding_score; report_correctness; human_escalation_precision; calibration_error; selective_risk; false_alarm_reduction
Remove negative-control normal scoring; Remove cross-model disagreement term; Use SAM or SAM2 largest mask only; Use the mask with highest heatmap overlap only; Use CLIP-style semantic score only without IAD heatmap support; Use no normal-reference retrieval; Use all masks without calibrated refusal; Remove the saliency-only penalty for large object-part masks
Run SAM2 refinement on random heatmap peaks from normal images and require the policy to reject them; Use shuffled defect-type prompts unrelated to the product category; Replace retrieved normal references with same-image background patches; Prompt SAM or SAM2 with boxes covering normal salient object parts and require rejection unless anomaly evidence is present; Evaluate on normal images with synthetic prompt points but no defects and measure false positive mask rate
Improve mask_iou by at least 5 points over heatmap-thresholded PatchCore or RD4AD on MVTec_AD or VisA; Improve defect_region_precision by at least 10% at matched defect_region_recall relative to SAM2 without the selection policy; Keep false positive mask rate on normal negative controls below 5% at the selected operating point; Achieve evidence_grounding_score of at least 0.80 for accepted reports; If tool_success_rate or evidence_grounding_score does not exceed the non-agent SAM2-plus-report baseline, declare the agent component unsuccessful

Evidence paper IDs:
openalex:W4380551232; openalex:W7162893906; openalex:W7154655652; openalex:W4415239807; openalex:W7153328271

Risks, controls, or fallback:
Risk: cross-model agreement can reinforce the same texture, lighting, or object-saliency false positives, and sparse mask calibration can overfit to product categories. Fallback: require normal negative-control rejection, restrict prompts to dataset-supported product and defect terms, and use conservative escalation when semantic support, heatmap evidence, and reference mismatch disagree.

---

Idea 3
Title:
Evidence-Grounded Report Checker with Selective Human Escalation

Core proposal:
Introduce an evidence-grounded report checker that validates every report claim before release. The checker receives candidate anomaly regions from IAD tools, retrieved same-category normal references, a restricted defect taxonomy when available, and cross-model heatmap or semantic agreement scores. It drafts or receives a structured inspection report, decomposes it into atomic claims, checks whether each claim is supported by a linked anomaly region and a normal-reference contrast, and then accepts, revises unsupported claims to a weaker evidence-supported form, or escalates/refuses. Agent steps: run IAD and VLM-style tools, retrieve normal references, draft a structured report, verify each claim-to-region/reference link, calibrate confidence, and apply selective escalation optimized for false-alarm reduction at matched anomaly recall.

Motivation or baseline weakness:
WinCLIP, AnomalyCLIP, and VLM-style inspection agents may generate plausible defect descriptions that are unsupported by localized visual evidence. This can produce misleading inspection reports and poor human escalation decisions even when image-level anomaly scores are reasonable.

Mechanism or approach:
A Claim-Region-Reference Verifier that parses the report schema into atomic claims {defect_type, location, visual_evidence, normal_reference_used, severity, recommended_action}, checks whether each claim has localized region support, normal-reference contrast, and taxonomy compatibility, and returns unsupported_claim_flags plus calibrated release, revise, or escalation decisions.
Minimize unsupported report claims and selective risk by optimizing a release policy over anomaly score, localization confidence, cross-model disagreement, and claim-verification score. The policy is constrained to maintain target anomaly recall, improve human_escalation_precision, and reduce false releases of reports whose defect type, location, or evidence link is contradicted by the available region evidence.

Experiment and implementation plan:
WinCLIP; AnomalyCLIP; PatchCore; Unverified VLM inspection report agent; IAD heatmap plus template report; Retrieval-augmented report generation without claim verification
MVTec_AD and VisA image-level and pixel-level anomaly data; Optional defect taxonomy converted into allowed report labels for each product category; Normal reference images for region-to-reference contrast; Human- or rule-constructed report correctness labels for a small validation subset; Automatically generated counterfactual reports with wrong defect type, wrong region, missing evidence, swapped normal references, or unsupported severity/action claims for checker training and evaluation
run_iad_and_vlm_baselines.py; retrieve_normal_references.py; draft_structured_reports.py; create_counterfactual_report_claims.py; verify_claim_region_reference_links.py; calibrate_escalation_policy.py; evaluate_report_correctness_grounding.py; evaluate_selective_detection.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; mask_iou; report_correctness; evidence_grounding_score; false_alarm_reduction; human_escalation_precision; tool_success_rate; calibration_error; selective_risk; defect_region_precision; defect_region_recall
Remove claim-region-reference verifier; Remove retrieved normal references from verification; Use VLM self-critique without access to anomaly masks or heatmaps; Use cross-model disagreement only without report checking; Use fixed confidence threshold instead of calibrated selective policy; Disable refusal and escalation and force a report for every sample; Allow free-form defect labels instead of the restricted taxonomy or unknown-anomaly fallback
Feed reports with deliberately swapped defect locations and require the checker to reject or revise them; Feed reports with correct anomaly score but unsupported defect type and require revision or escalation; Generate reports from normal images with no anomaly evidence and measure false release rate; Swap normal references across product categories and require the checker to flag unsupported reference contrast; Provide reports with correct region but exaggerated severity or unsupported recommended action and require claim-level rejection
Improve report_correctness by at least 15% over VLM-style report generation without evidence checking; Achieve evidence_grounding_score of at least 0.85 on accepted reports; Reduce false alarms by at least 10% at matched image-level recall compared with the strongest direct IAD baseline plus unverified report; Improve human_escalation_precision by at least 10% while keeping selective_risk no worse than the non-agent baseline; If evidence_grounding_score and tool_success_rate do not improve over the negative-control unverified agent, the idea fails

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W7154655652; openalex:W7153328271; openalex:W7138099583

Risks, controls, or fallback:
Risk: automatic report labels may be noisy, VLM descriptions may not match dataset taxonomies, and checker training on synthetic counterfactuals may miss real human-report errors. Fallback: restrict output to a small allowed defect taxonomy plus an 'unknown anomaly' class, prioritize region/reference evidence over free-form semantic naming, and escalate whenever defect type or recommended action is not directly supported by localized evidence.

---

## Item 13: HUM-a24a9a1add

类型：`portfolio`

### Candidate A

Idea 1
Title:
Reference-Consistency Agent for Shifted or Contaminated Normal Memory Banks

Core proposal:
Add a retrieval-audit agent around a frozen nearest-neighbor IAD pipeline. The workflow is: compute the baseline anomaly heatmap; convert high-score connected components into suspicious regions; retrieve top-k normal patches for each region from the memory bank; compute retrieval_consistency_score from the agreement among retrieved neighbors, their distance margin to the test region, and their own cross-neighbor normality; identify suspicious reference patches using leave-one-reference or leave-one-cluster influence on region scores; recompute the region anomaly score after excluding suspect references; compare pre- and post-audit score stability; emit a structured report linking each anomaly claim to the test region, trusted references, removed references if any, and an escalation decision. The agent escalates rather than suppresses a defect when the region remains anomalous but the trusted reference evidence is insufficient.

Motivation or baseline weakness:
PatchCore-style nearest-neighbor industrial anomaly detectors can become unstable when the normal memory bank is shifted across acquisition conditions or contains contaminated normal examples. Their heatmaps also do not indicate whether a high anomaly score was caused by trustworthy normal references, outlier reference patches, or reference-bank instability.

Mechanism or approach:
A lightweight reference-bank auditor over frozen PatchCore-style patch embeddings, optionally DINO or CLIP embeddings for cross-checking. It outputs per-reference contamination_likelihood, per-region retrieval_consistency_score, score_instability_after_reference_removal, and a rule-based agent state for verify, accept, refuse, or escalate.
For each region r, compute audited_score(r)=base_iad_score(r)+lambda_instability*score_instability(r)-lambda_trust*trusted_normal_support(r), where trusted_normal_support is estimated only from references with low contamination_likelihood. Calibrate a selective decision rule so that reports are emitted when audited confidence exceeds tau and otherwise escalated. Reference contamination_likelihood is estimated from nearest-neighbor graph outlierness, disagreement with local normal clusters, and influence on many test-region scores under leave-one-reference or leave-one-cluster removal.

Experiment and implementation plan:
PatchCore; PaDiM; FastFlow; RD4AD; WinCLIP
MVTec_AD train/test normal and anomaly images with masks; VisA train/test normal and anomaly images with masks; Synthetic contaminated memory banks created by injecting a controlled percentage of anomalous test patches, shifted normal images, or nuisance-perturbed normal images into the reference set; Factory-shift proxy splits by product category, lighting augmentation, camera perturbation, or acquisition-condition perturbation
build_patch_memory_bank.py; inject_reference_contamination.py; run_baseline_iad_heatmaps.py; retrieve_topk_normal_patches.py; audit_reference_bank.py; agent_verify_and_report.py; evaluate_detection_localization_agent.py; calibrate_selective_policy.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; f1_score; mask_iou; defect_region_precision; defect_region_recall; tool_success_rate; evidence_grounding_score; false_alarm_reduction; human_escalation_precision; calibration_error; selective_risk; out_of_distribution_detection
Remove reference-bank audit but keep nearest-neighbor retrieval; Use random normal references instead of top-k retrieved references; Use the base PatchCore heatmap without retrieval_consistency_score; Disable score-stability verification after suspect-reference removal; Replace calibrated escalation with a fixed anomaly-score threshold; Vary contamination rate and shift severity independently; Use only PatchCore embeddings versus adding DINO or CLIP embedding cross-checks
Non-agent PatchCore plus a templated report with no retrieval audit, no score-stability verification, and no escalation policy; Reference retrieval with shuffled region-reference links to test whether evidence grounding depends on the true retrieved patches; Clean normal-bank setting with no injected contamination to verify that the auditor does not invent contamination or degrade clean-data localization; Injected contamination labels hidden during calibration to prevent tuning directly on synthetic contamination identities
At matched anomaly recall, reduce false_alarm_rate by at least 10% over PatchCore on contaminated or shifted reference settings; Preserve pixel_level_auroc and pro_score within 1 point of PatchCore on clean MVTec_AD or VisA while improving contaminated-bank robustness; Achieve evidence_grounding_score of at least 0.75 for reports linking each defect claim to a region and trusted reference patches; Improve human_escalation_precision by at least 10% over fixed-threshold escalation; Failure if agent workflow metrics do not improve over the non-agent retrieval baseline or if localization drops by more than 2 points on clean data

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W4404704036

Risks, controls, or fallback:
Risk: synthetic contamination and proxy shifts may not represent real factory drift. Fallback: report sensitivity curves across multiple contamination types and shift severities, separate clean-bank and contaminated-bank results, and restrict claims to reference-bank robustness rather than broad domain adaptation.

---

Idea 2
Title:
Disagreement-Gated Mask Agent for Suppressing Texture and Lighting False Positives

Core proposal:
Create a mask-verification agent that treats each candidate mask as a hypothesis. The workflow is: run multiple frozen detectors; convert detector heatmaps into candidate boxes and points; prompt SAM or SAM2 to generate candidate masks; score each mask using heatmap support, normal-reference inconsistency, CLIP or AnomalyCLIP semantic defect compatibility, prompt stability, and similarity to nuisance negative controls; use cross-model disagreement as uncertainty rather than direct evidence of a defect; reject or abstain on masks dominated by lighting, shadow, blur, specular highlight, or texture-preserving color perturbation signatures; emit a localized defect report only when the accepted mask is supported by localized anomaly evidence and stable enough under detector and prompt perturbations.

Motivation or baseline weakness:
IAD heatmaps from PatchCore, PaDiM, FastFlow, or CLIP-based zero-shot detectors can confuse texture, reflections, shadows, and illumination changes with physical defects. SAM and SAM2 can refine candidate masks, but promptable segmentation can select salient non-defect regions unless mask selection is constrained by defect evidence and nuisance negative controls.

Mechanism or approach:
A frozen-model mask selection and rejection policy that ranks SAM or SAM2 masks using heatmap_support, reference_inconsistency, semantic_defect_support, nuisance_similarity, and model_disagreement_uncertainty. The module requires no detector fine-tuning and only calibrates thresholds or a shallow scoring function on validation normals and held-out labeled masks when available.
Select mask m maximizing S(m)=alpha*heatmap_support(m)+beta*reference_inconsistency(m)+gamma*semantic_defect_support(m)-delta*nuisance_similarity(m)-eta*model_disagreement_uncertainty(m)-rho*prompt_instability(m). Accept the highest-scoring mask only if calibrated confidence exceeds tau; otherwise escalate. Cross-model disagreement increases uncertainty unless the disagreement is resolved by high localized support, low nuisance similarity, and stable SAM/SAM2 prompts.

Experiment and implementation plan:
PatchCore; PaDiM; FastFlow; WinCLIP; AnomalyCLIP; SAM; SAM2
MVTec_AD images and pixel masks; VisA images and pixel masks; Normal-reference images from train splits; Nuisance negative controls generated from normal images using brightness, contrast, shadow, blur, specular highlight, compression, and texture-preserving color perturbations; Optional sparse-mask setting using image labels for calibration and held-out masks only for final evaluation
run_multi_detector_heatmaps.py; generate_sam_candidate_masks.py; make_lighting_texture_negative_controls.py; score_mask_hypotheses.py; calibrate_abstention_policy.py; agent_region_verification.py; generate_structured_region_report.py; evaluate_mask_and_agent_metrics.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; f1_score; tool_success_rate; evidence_grounding_score; false_alarm_reduction; report_correctness; human_escalation_precision; calibration_error; selective_risk
Remove SAM/SAM2 mask selection and use thresholded heatmap masks; Use SAM/SAM2 refinement without nuisance-negative-control rejection; Remove model_disagreement_uncertainty from the mask score; Remove normal-reference inconsistency from the mask score; Remove semantic defect compatibility from WinCLIP or AnomalyCLIP; Remove prompt-stability scoring across SAM/SAM2 prompts; Replace calibrated abstention with always-report behavior
SAM/SAM2 prompted by heatmap boxes but selecting the largest or highest-confidence SAM mask without the proposed policy; Agent report generated from accepted masks after randomizing mask-to-evidence links; Nuisance-only normal images treated as test anomalies to measure false-positive suppression; Random boxes or points used as SAM/SAM2 prompts to estimate how much improvement comes from promptable segmentation alone; Detector-score-only mask acceptance without nuisance controls or prompt-stability checks
Improve defect_region_precision by at least 10% at matched defect_region_recall versus thresholded PatchCore or PaDiM heatmaps; Reduce false positives on nuisance negative controls by at least 15% versus SAM/SAM2 heatmap refinement without the selection policy; Maintain pixel_level_auroc and pro_score within 1 point of the strongest frozen IAD baseline on MVTec_AD or VisA; Achieve tool_success_rate of at least 0.9 for detector, retrieval, SAM/SAM2, calibration, and report tools; Failure if SAM/SAM2 refinement improves mask_iou but evidence_grounding_score or false_alarm_reduction does not improve over the non-agent mask-refinement baseline

Evidence paper IDs:
openalex:W4380551232; openalex:W7162893906; openalex:W4415239807; openalex:W7154655652

Risks, controls, or fallback:
Risk: high model disagreement may occur on subtle true defects, causing excessive abstention. Fallback: treat disagreement as an escalation signal rather than a rejection signal, calibrate thresholds primarily on validation normals and nuisance controls, and report coverage-risk curves so gains are not hidden by over-abstention.

---

Idea 3
Title:
Evidence-Grounded Report Checker with Selective Human Escalation

Core proposal:
Add a report-checking agent that requires every defect_type, evidence sentence, severity statement, and recommended_action to be linked to a specific anomaly region, detector score, and retrieved normal reference. The workflow is: run a frozen IAD detector or zero-shot anomaly model; generate suspicious regions from heatmaps or detector outputs; retrieve normal references for each region; optionally refine boundaries using a segmentation proposal tool; draft a schema-constrained report; parse the report into atomic claims; verify each claim against region masks, anomaly scores, normal-reference contrasts, and an allowed defect taxonomy; compute calibrated report confidence from detector confidence, retrieval consistency, region quality, and checker pass rate; allow one revision for unsupported claims; then emit the report, refuse unsupported semantic descriptions, or escalate to human review.

Motivation or baseline weakness:
WinCLIP, AnomalyCLIP, and VLM-style IAD agents can produce semantic defect descriptions that are not grounded in localized visual evidence. Classical IAD models provide anomaly scores or masks but do not produce verified structured reports or principled human-review triggers.

Mechanism or approach:
A claim-to-evidence verifier that parses structured reports into atomic claims and validates required links to region identifiers, masks, anomaly scores, retrieved normal references, and allowed defect taxonomy entries. It uses frozen CLIP/VLM embeddings only for semantic compatibility checks and deterministic schema checks for grounding, missing links, confidence fields, and unsupported recommended actions.
Maximize report_correctness and evidence_grounding_score under a selective-risk constraint. Emit a report only if calibrated confidence q(report|regions,references,checker_pass_rate) exceeds tau; otherwise escalate. Penalize unsupported defect labels, missing region links, missing normal-reference comparisons, claims outside the defect taxonomy, and recommended actions that are not justified by the verified region evidence.

Experiment and implementation plan:
WinCLIP; AnomalyCLIP; PatchCore; RD4AD; SAM; GroundingDINO
MVTec_AD or VisA images with image labels and pixel masks; Optional defect taxonomy mapped from dataset defect names; Normal reference images from training splits; Small human- or rule-created report templates with required fields: anomaly_score, anomaly_mask_or_region, defect_type, evidence, normal_reference_used, confidence, recommended_action, and failure_warning; Optional sparse labels to simulate weak pixel supervision
run_iad_and_region_proposals.py; retrieve_region_references.py; draft_structured_report.py; check_report_claim_grounding.py; revise_or_refuse_report.py; calibrate_report_confidence.py; simulate_human_escalation.py; evaluate_reports_and_localization.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; report_correctness; evidence_grounding_score; tool_success_rate; false_alarm_reduction; human_escalation_precision; calibration_error; selective_risk
Remove evidence-grounded report checker; Allow one-shot VLM report without region-reference links; Remove retrieval of normal references; Remove calibrated refusal and always generate a report; Remove defect taxonomy constraint; Use masks from IAD heatmaps only versus SAM-assisted region proposals with the same checker; Disable the one-revision step and compare direct refusal against revision-then-refusal
PatchCore or WinCLIP plus a templated report that copies the top anomaly score but does not verify claims; Report checker run with randomized normal references and randomized region identifiers; Human escalation triggered by anomaly_score threshold alone rather than calibrated report confidence; Reports with deliberately injected unsupported defect labels or swapped defect regions to test checker sensitivity; Normal images with no defect region where the system must either report normality or refuse defect descriptions
Improve evidence_grounding_score by at least 20% over one-shot report generation at comparable report coverage; Maintain image_level_auroc and pixel_level_auroc within 1 point of the underlying IAD baseline because reporting should not degrade detection; Reduce unsupported defect descriptions by at least 30% relative to WinCLIP or AnomalyCLIP report prompts; Improve human_escalation_precision by at least 10% over anomaly-score-only escalation; Failure if report_correctness or evidence_grounding_score does not improve over the non-agent report baseline, even if detection metrics are unchanged

Evidence paper IDs:
openalex:W7162893906; openalex:W7154655652; openalex:W7153328271; openalex:W7138099583

Risks, controls, or fallback:
Risk: automatic report-correctness evaluation can be noisy and may reward overly conservative reports. Fallback: report factual grounding separately from usefulness, include refusal-rate and coverage-risk curves, and audit a small stratified human-evaluation set for report correctness, usefulness, and escalation quality.

### Candidate B

Idea 1
Title:
Reference-Consistency Inspection Agent for Shifted and Contaminated Normal Banks

Core proposal:
A retrieval-augmented industrial anomaly detection agent that audits the normal reference bank before making a defect decision, then uses reference-consistency evidence to produce an anomaly mask, score, defect hypothesis, confidence, and escalation recommendation. The core research question is whether an agent that explicitly checks reference quality and cross-reference consistency can reduce false alarms from factory shift and prevent missed defects caused by contaminated normal memories.

Motivation or baseline weakness:
PatchCore, PaDiM, FastFlow, RD4AD, WinCLIP, and AnomalyCLIP provide strong image-level and pixel-level anomaly signals, but nearest-neighbor memory banks and prompt-based semantic models can fail when normal references shift across factories or contain hidden defects. Existing agentic anomaly systems emphasize reasoning and tool use, but a publishable gap remains in making reference retrieval itself auditable: which normal references were used, whether they are trustworthy, and whether the localized anomaly is consistent across multiple retrieved references. This targets the required gaps of normal-reference shift, contaminated memory banks, false-positive heatmaps from texture or lighting variation, unsupported VLM descriptions, and human escalation.

Mechanism or approach:
The agent uses the following tools: image preprocessor, product-category router, PatchCore or PaDiM heatmap generator, WinCLIP or AnomalyCLIP semantic scorer, CLIP/DINO-style normal-patch retriever, SAM or SAM2 candidate-mask generator, reference-bank auditor, cross-model disagreement checker, report generator, evidence-grounded report checker, and escalation policy. The memory state stores product category, retrieved normal images, patch-level nearest neighbors, reference provenance, suspected contaminated references, mask candidates, model scores, calibration statistics, and final report claims. The new component is a Reference-Consistency and Bank-Audit Module: for each candidate anomalous region, it retrieves top-k normal patches from multiple reference images, computes a retrieval consistency score between the test region and normal patches, flags references whose patches are repeatedly closer to anomalous regions than clean normal regions, and downweights or excludes them. The verification loop reruns localization after excluding suspicious references, compares PatchCore/PaDiM heatmaps with WinCLIP/AnomalyCLIP semantic anomaly maps, asks SAM/SAM2 for masks only from high-consensus seed points, rejects masks that also appear on retrieved normal references as a negative control, and sends low-consistency or high-disagreement cases to human review. Confidence calibration uses validation normal data plus synthetic held-out contamination to learn selective thresholds for anomaly_score, retrieval_consistency_score, cross_model_disagreement_score, and reference_audit_score. The structured report schema contains anomaly_score, anomaly_mask_or_region, defect_type, evidence, normal_reference_used, confidence, recommended_action, and failure_warning.

Experiment and implementation plan:
Datasets: MVTec_AD and VisA first, with optional extension to MVTec_LOCO, BTAD, and MPDD. Construct reference-shift splits by mixing normal references across product subdomains, illumination conditions, or factories when metadata permits; construct contaminated-bank splits by injecting a controlled percentage of anomalous training/test-normal references into the normal memory. Direct baselines: PatchCore, PaDiM, RD4AD, WinCLIP, AnomalyCLIP, and a non-agent retrieval baseline using the same frozen features without auditing or verification. Transfer baselines: CLIP retrieval, SAM/SAM2 mask refinement, and tool-using RAG inspection. Metrics: image_level_auroc, pixel_level_auroc, aupr, pro_score, f1_score, mask_iou, defect_region_precision, defect_region_recall, calibration_error, selective_risk, out_of_distribution_detection, tool_success_rate, report_correctness, evidence_grounding_score, false_alarm_reduction, and human_escalation_precision. Ablations: remove reference-bank audit, remove retrieval-consistency score, remove cross-model disagreement, use SAM/SAM2 masks without negative control, remove report checker, remove calibration, and replace the agent with a fixed pipeline. Minimal new module: reference-consistency scorer plus bank-audit state update. MVP artifacts: Python inspection pipeline, reference-bank contamination benchmark script, JSON report schema, mask/evidence visualizer, and evaluation dashboard. Implementation plan: implement frozen-feature patch retrieval; wrap PatchCore/PaDiM and WinCLIP/AnomalyCLIP outputs as tools; add reference audit and consistency scoring; prompt SAM/SAM2 from consensus heatmap seeds; calibrate selective thresholds on validation normals; generate reports; run negative-control and contaminated-bank evaluations. Risks: reference-shift proxies may not fully match real factory shifts, CLIP/DINO patch features may over-index texture, and bank audit may remove rare but valid normal modes. Failure criteria: the method fails if agent workflow metrics do not improve over the non-agent baseline, if false_alarm_reduction is not achieved at matched recall, if evidence_grounding_score does not improve, or if localization metrics drop substantially relative to the best direct IAD baseline.

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W4404704036; openalex:W7154655652; openalex:W4380551232

---

Idea 2
Title:
Disagreement-Guided Mask Verification Agent for Weakly Labeled Anomaly Localization

Core proposal:
A localization-focused inspection agent that converts noisy IAD heatmaps into verified defect regions under weak or missing pixel labels. It coordinates multiple frozen anomaly models, promptable segmentation, negative controls, and evidence-grounded report checking to decide which proposed mask is a true defect region and when uncertainty requires human review.

Motivation or baseline weakness:
Industrial anomaly datasets often provide sparse or incomplete pixel-level masks, while heatmap-based methods such as PatchCore, PaDiM, FastFlow, DRAEM, and RD4AD can produce diffuse false-positive regions from texture, lighting, or structural variation. SAM and SAM2 can refine masks but may segment salient normal parts unless there is a principled mask selection policy and negative control. VLMs such as WinCLIP, AnomalyCLIP, LLaVA, or Qwen-VL can describe defects, but descriptions can be unsupported by localized evidence. The gap is an experiment-ready agentic verification loop that makes mask selection measurable through cross-model disagreement, normal-reference counterfactuals, and report-region grounding.

Mechanism or approach:
The agent has tools for IAD heatmap generation, semantic anomaly scoring, candidate box extraction, SAM/SAM2 mask proposal, GroundingDINO text-conditioned region proposal when a defect taxonomy is provided, normal-reference retrieval, local image normalization/illumination check, mask scoring, VLM report drafting, report-claim grounding, and human escalation. The memory state stores heatmaps, candidate masks, retrieved normal patches, model-specific anomaly scores, disagreement maps, illumination/texture warnings, report claims, and final calibrated confidence. The new component is a Disagreement-Guided Mask Selection Policy: candidate masks are retained only if they cover high anomaly evidence from at least one strong IAD model, are not equally activated on retrieved normal references, have bounded disagreement rather than arbitrary saliency, and support a defect-type claim through localized visual evidence. Cross-model disagreement is used in two ways: moderate disagreement triggers extra verification and mask refinement, while extreme disagreement lowers confidence and escalates. The verification loop tests each candidate mask against negative controls: random normal patch prompts, retrieved normal-image prompts, shuffled defect-taxonomy prompts, and SAM/SAM2 masks proposed from low-anomaly regions. The report checker accepts only claims linked to selected regions and normal references; unsupported defect descriptions are converted to failure_warning or escalated as unknown anomaly.

Experiment and implementation plan:
Datasets: MVTec_AD and VisA for the main MVP, with weak-label settings created by hiding pixel masks during method development and using them only for evaluation; optional extension to BTAD and MPDD. Direct baselines: PatchCore, PaDiM, FastFlow, DRAEM, RD4AD, WinCLIP, AnomalyCLIP, SAM/SAM2 prompted from raw heatmap peaks, and a non-agent ensemble average. Transfer baselines: GroundingDINO for taxonomy-conditioned boxes, Mask2Former trained on available masks where labels exist, CLIP retrieval, and a generic tool-using agent without verification. Metrics: image_level_auroc, pixel_level_auroc, aupr, pro_score, f1_score, mask_iou, defect_region_precision, defect_region_recall, tool_success_rate, report_correctness, evidence_grounding_score, false_alarm_reduction, human_escalation_precision, calibration_error, and selective_risk. Ablations: remove cross-model disagreement, remove normal-reference negative control, remove SAM/SAM2 mask selection policy, remove report checker, remove illumination/texture warning, use a single IAD model, and replace escalation with forced prediction. Minimal new module: candidate-mask verifier that combines heatmap support, reference counterfactual score, disagreement score, and report-grounding score. MVP artifacts: weak-label split generator, mask-verification agent, SAM/SAM2 prompt policy, JSON reports with linked evidence regions, and evaluation scripts. Implementation plan: compute heatmaps from PatchCore/PaDiM/RD4AD and semantic maps from WinCLIP/AnomalyCLIP; extract seed regions; generate candidate masks with SAM/SAM2; retrieve normal reference patches for each candidate; score heatmap support and negative-control activation; calibrate confidence; draft and check structured reports; evaluate against held-out masks and report annotations. Risks: disagreement may correlate with model weakness rather than useful uncertainty, SAM/SAM2 may miss tiny defects, and defect-taxonomy prompts may bias reports. Failure criteria: the idea fails if mask_iou, pro_score, or defect_region_precision do not improve over heatmap-threshold baselines, if SAM/SAM2 negative controls do not reduce false positives, if evidence_grounding_score is not higher than unverified VLM reporting, or if escalation precision is poor.

Evidence paper IDs:
openalex:W7154655652; openalex:W7162893906; openalex:W7138099583; openalex:W4380551232; openalex:W7153328271

---

Idea 3
Title:
Selective Inspection Agent for Calibrated Reject-or-Review Decisions in Manufacturing QC

Core proposal:
A reliability-centered agentic workflow that optimizes when to accept, reject, or escalate an inspected product. Instead of only improving raw AUROC, the method studies selective prediction for industrial anomaly detection: maintain defect recall, reduce false alarms, calibrate confidence, ground each report in visual evidence, and escalate uncertain or unsupported cases to a human inspector.

Motivation or baseline weakness:
Manufacturing deployment requires reliable actions, not just anomaly heatmaps. Strong IAD baselines can overreact to benign texture changes or understate uncertainty under product-category shift, while VLM-based reports may confidently describe defects without sufficient visual grounding. Prior agentic anomaly work motivates multi-step reasoning and tool use, but the open research gap is a calibrated decision policy that jointly evaluates detection, localization, report correctness, evidence grounding, and human escalation precision under rare anomalies and sparse labels. This proposal directly addresses when to escalate to human review and how to measure whether the agent improves quality-control decisions over a non-agent baseline.

Mechanism or approach:
The agent uses tools for product-category validation, IAD model inference, normal-reference retrieval, candidate-region localization, cross-model self-verification, report generation, report-claim grounding, confidence calibration, and action selection. The memory state stores product metadata, inspection goal, optional defect taxonomy, retrieved references, anomaly masks, image-level scores, region-level evidence links, model disagreement, OOD indicators, calibrated confidence, and action history. The new component is a Selective Action Policy optimized for false_alarm_reduction at matched recall: it learns thresholds over anomaly_score, retrieval_consistency_score, cross_model_disagreement_score, evidence_grounding_score, and OOD score to output one of pass, reject, re-image/reinspect, or human_review. The verification loop first compares PatchCore or RD4AD with WinCLIP or AnomalyCLIP, retrieves normal references for the top anomalous regions, checks whether the defect description is supported by region-reference contrast, and refuses to name a defect type when the evidence is insufficient. Confidence calibration uses temperature/isotonic calibration on validation normals and scarce labeled anomalies, plus conformal or selective-risk tuning to control the risk of automatic decisions. The structured report includes anomaly_score, anomaly_mask_or_region, defect_type or unknown, evidence, normal_reference_used, confidence, recommended_action, and failure_warning.

Experiment and implementation plan:
Datasets: MVTec_AD and VisA first; optional MVTec_LOCO for logical anomalies and MPDD or BTAD for additional manufacturing variation. Create deployment-style evaluation queues with class imbalance, mixed product categories, withheld defect taxonomy for some classes, normal-reference shift, and a small human-review budget simulated from labels. Direct baselines: best single IAD baseline among PatchCore, PaDiM, RD4AD, FastFlow, DRAEM, WinCLIP, and AnomalyCLIP; score-threshold-only selective baseline; uncalibrated VLM report agent; and non-agent ensemble. Transfer baselines: CLIP retrieval, RAG report generation, and tool-using agent without calibrated escalation. Metrics: image_level_auroc, pixel_level_auroc, aupr, pro_score, f1_score, mask_iou, defect_region_precision, defect_region_recall, calibration_error, selective_risk, out_of_distribution_detection, tool_success_rate, report_correctness, evidence_grounding_score, false_alarm_reduction, and human_escalation_precision. Ablations: remove calibration, remove selective policy, remove human-review action, remove evidence-grounded report checker, remove retrieval consistency, remove cross-model disagreement, and force every case into pass/reject. Minimal new module: calibrated selective action head over frozen-tool outputs and evidence-grounding features. MVP artifacts: deployment-queue generator, selective-risk evaluator, calibrated action-policy module, report schema, human-review simulator, and reliability dashboard. Implementation plan: wrap IAD baselines as tools; compute region evidence and normal-reference retrieval; generate initial reports; score claim-region-reference grounding; fit calibration and selective thresholds on validation split; evaluate automatic pass/reject decisions under matched recall and limited review budget; compare against non-agent and uncalibrated agent variants. Risks: simulated human-review budgets may not fully capture real inspector behavior, calibration may be unstable with very few anomalies, and report-correctness labels may require manual annotation. Failure criteria: the proposal fails if selective_risk or calibration_error does not improve over threshold-only baselines, if false_alarm_reduction at matched recall is negligible, if human_escalation_precision is not better than score-based uncertainty, or if evidence_grounding_score and report_correctness do not improve over an unverified report agent.

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W7153328271; openalex:W7138099583; openalex:W4404704036

---

## Item 14: HUM-fc34d6a0f0

类型：`single_idea`

### Candidate A

Title:
Disagreement-Gated Mask Selection Agent for Weakly Labeled Defect Localization

Core proposal:
Use an inspection agent to combine frozen IAD heatmaps with promptable segmentation. The agent proposes candidate regions from one or more IAD heatmaps, prompts SAM or SAM2 with points and boxes from high-confidence regions, and selects a mask only when it is supported by localized anomaly evidence and does not reproduce on matched normal-reference regions. The final report links each accepted mask to heatmap support and normal-reference comparisons; unsupported masks are rejected or escalated.

Motivation or baseline weakness:
SAM and SAM2 can produce precise masks for visually salient regions that are not defects, while IAD heatmaps from DRAEM, FastFlow, or RD4AD can be noisy under texture, illumination, or surface-pattern variation. Without an explicit mask selection policy and normal-image checks, promptable segmentation may appear to improve localization while actually amplifying false positives.

Mechanism or approach:
A disagreement-gated mask selection policy that scores each candidate mask using IAD heatmap support, agreement among available anomaly maps, response on matched normal-reference regions, and calibrated uncertainty.
Improve defect localization from weak or sparse labels by selecting a candidate mask only when it increases agreement-weighted anomaly evidence over raw heatmap thresholding and remains absent from retrieved normal-reference patches.

Experiment and implementation plan:
DRAEM; FastFlow; RD4AD; SAM; SAM2; GroundingDINO
MVTec_AD images with pixel masks; VisA images with pixel masks; optional weak labels derived from image-level anomaly tags and sparse boxes; normal_reference_images for each product category; lighting and texture perturbation splits for false-positive stress testing
run_iad_heatmap_ensemble.py; generate_sam_or_sam2_candidate_masks.py; retrieve_normal_counterfactual_regions.py; score_cross_model_disagreement_and_negative_controls.py; agent_mask_selection_and_report.py; evaluate_sparse_label_localization.py
pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; f1_score; tool_success_rate; report_correctness; evidence_grounding_score; false_alarm_reduction; calibration_error
use SAM2 refinement without disagreement-gated mask selection; use a single IAD heatmap instead of multi-model or multi-view support; remove the normal-reference negative-control check; use GroundingDINO text boxes without IAD heatmap evidence; train or tune with full masks versus sparse boxes only; disable calibration and use fixed anomaly thresholds
Prompt SAM2 with high-saliency but low-anomaly regions and require the policy to reject the masks; Run the mask-selection agent on known normal images and require no-defect reports or escalation; Shuffle heatmaps across images before mask selection to test whether accepted masks depend on real localized anomaly evidence; Use normal-reference regions from the same category and verify that masks recurring on normal regions are rejected
Improve mask_iou by at least 10% over the best raw IAD heatmap thresholding baseline on MVTec_AD or VisA; Improve defect_region_precision by at least 15% under lighting or texture perturbations while keeping defect_region_recall within 5% of the strongest baseline; Reduce unsupported selected masks on normal-reference negative controls by at least 25% compared with SAM2 refinement without the policy; Achieve evidence_grounding_score above 0.8 for claims linked to selected regions and references; Treat the method as unsuccessful if SAM2 refinement without the policy matches performance or if agent tool_success_rate falls below 90%

Evidence paper IDs:
openalex:W7153670799; openalex:W7154655652; openalex:W4380551232

Risks, controls, or fallback:
Risk: small or low-contrast true defects may produce high disagreement and be over-escalated. Fallback: allow a small-defect mode in which high local anomaly density plus stable reference inconsistency yields a low-confidence localized anomaly report instead of outright rejection.

### Candidate B

Title:
Disagreement-Gated Mask Selection Agent for Weakly Labeled Defect Localization

Core proposal:
Use an inspection agent that first obtains frozen IAD heatmaps from DRAEM, RD4AD, and optionally FastFlow as a weaker stress-test baseline. Candidate points and boxes are generated from high-confidence heatmap regions and passed to SAM or SAM2. Each candidate mask is accepted only when it has strong support from at least one reliable IAD heatmap, low spatial disagreement among the stronger IAD sources inside the proposed defect region, limited overlap with known normal structures, and a negative response when the same prompting and scoring procedure is applied to retrieved same-category normal-reference regions. Masks that also appear on matched normal patches or depend on shuffled heatmaps are rejected or escalated. The final report links the selected mask to heatmap evidence and normal-reference counterexamples.

Motivation or baseline weakness:
SAM or SAM2 can segment visually salient regions that are not true defects, while IAD heatmaps from DRAEM, FastFlow, or RD4AD can be noisy under texture and lighting variation. Without a mask selection policy, normal-reference negative controls, and shuffled-evidence controls, promptable segmentation can falsely appear to improve defect localization.

Mechanism or approach:
A disagreement-gated mask selection policy that scores each candidate mask by heatmap support, cross-model spatial agreement, normal-reference negative-control response, prompt stability, and calibrated uncertainty, then returns accept, reject, or escalate decisions.
Maximize defect_region_precision and mask_iou under full-mask or sparse-box supervision by selecting a candidate mask only when it improves agreement-weighted anomaly evidence over raw heatmap thresholding and does not reproduce on retrieved normal-reference regions.

Experiment and implementation plan:
DRAEM; FastFlow; RD4AD; SAM; SAM2; GroundingDINO
MVTec_AD images with pixel masks; VisA images with pixel masks; weak-label variants created from image-level anomaly tags, sparse boxes, or sparse point prompts; normal_reference_images for each product category; lighting and texture perturbation splits for false-positive stress tests; known-normal test images for refusal evaluation
run_iad_heatmap_ensemble.py; generate_prompt_points_and_boxes_from_heatmaps.py; generate_sam_or_sam2_candidate_masks.py; retrieve_normal_counterfactual_regions.py; score_cross_model_disagreement_and_negative_controls.py; agent_mask_selection_and_report.py; evaluate_sparse_label_localization.py
pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; f1_score; tool_success_rate; report_correctness; evidence_grounding_score; false_alarm_reduction
use SAM or SAM2 refinement without disagreement-gated mask selection; use single IAD model support instead of cross-model disagreement; remove normal-reference negative-control mask checking; use GroundingDINO text boxes only without IAD heatmap evidence; train or tune thresholds with full masks versus sparse boxes only; disable calibration and use fixed anomaly thresholds; remove prompt-stability scoring across point and box prompts
Prompt SAM or SAM2 with high-saliency but low-anomaly regions and require the selected masks to be rejected; Run the mask-selection agent on known normal images and require refusal or no-defect reports; Shuffle heatmaps across images before mask selection to verify that accepted masks depend on real localized evidence; Retrieve normal-reference patches from mismatched product categories and require the agent to flag the negative-control evidence as invalid rather than using it; Use blank or uniform heatmaps with SAM or SAM2 prompts and require no claimed localization improvement
Improve mask_iou by at least 10% over the best raw IAD heatmap thresholding baseline on MVTec_AD or VisA; Improve defect_region_precision by at least 15% under lighting or texture perturbations while keeping defect_region_recall within 5% of the strongest IAD baseline; Reduce unsupported selected masks on normal-reference negative controls by at least 25% compared with SAM or SAM2 refinement without the policy; Achieve evidence_grounding_score above 0.8 for claims linked to selected regions and references; Failure if SAM or SAM2 refinement without the policy matches performance, if shuffled-heatmap controls are still accepted, or if tool_success_rate falls below 90%

Evidence paper IDs:
openalex:W7153670799; openalex:W7154655652; openalex:W4380551232

Risks, controls, or fallback:
Risk: cross-model disagreement can be high for very small or low-contrast true defects, causing over-rejection. Fallback: add a small-defect escalation mode where high local anomaly density, stable prompt response, and valid same-category normal-reference rejection permit a low-confidence localized anomaly report without forcing a specific defect label.

---

## Item 15: HUM-8b0669455a

类型：`portfolio`

### Candidate A

Idea 1
Title:
Retrieval-Consistency Agent for Shifted or Contaminated Normal Reference Banks

Core proposal:
Add an agentic retrieval-audit loop around a frozen PatchCore-style memory bank. For each connected suspicious heatmap region, retrieve top-k normal patches, compute whether the retrieved references are mutually consistent and visually close to the test region, flag references that repeatedly behave as outliers among normal samples, and either accept the anomaly decision, down-weight unstable evidence, or escalate the case for human review.

Motivation or baseline weakness:
PatchCore-style nearest-neighbor industrial anomaly detectors can be brittle when the normal memory bank is shifted across acquisition conditions or mildly contaminated by anomalous samples. Their heatmaps also do not identify which normal references support a rejection decision, limiting evidence grounding in agentic inspection workflows.

Mechanism or approach:
A lightweight reference-bank audit and retrieval-consistency scorer using frozen PatchCore features, with optional DINO or CLIP embeddings only for secondary evidence reporting. For region r with base anomaly score A(r), top-k references N_k(r), and per-reference contamination scores C(n), compute S(r)=A(r)+lambda*median_distance(r,N_k(r))+gamma*mean(C(n) for n in N_k(r))+eta*topk_instability(r). Contamination scores are estimated by leave-one-out nearest-neighbor normality within the memory bank, not by using test labels.
Tune lambda, gamma, eta, k, anomaly thresholds, and escalation thresholds on a validation split to reduce false alarms and unsupported escalations at matched defect_region_recall. The constrained objective is to minimize selective_risk and false_alarm_reduction error subject to pixel_level_auroc, pro_score, and defect_region_recall not dropping by more than the pre-specified tolerance relative to the strongest non-agent IAD baseline on the same split.

Experiment and implementation plan:
PatchCore; PaDiM; RD4AD; WinCLIP; non-agent PatchCore with the same memory bank and identical threshold-search protocol
MVTec_AD or VisA test images; product_category labels; normal reference images per class; pixel masks or bounding boxes when available for localization evaluation; synthetic reference-shift splits created by separating normal images by acquisition condition, product subtype, or controlled cross-category mismatch; synthetic contaminated-memory splits created only from training-time anomalous or held-out defect images injected into the normal bank at known rates
build_patchcore_memory_bank.py; retrieve_topk_normal_patches.py; score_retrieval_consistency.py; audit_reference_bank_contamination.py; run_agent_inspection_loop.py; evaluate_detection_localization_agent_metrics.py; generate_structured_report_json.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; false_alarm_reduction; tool_success_rate; evidence_grounding_score; human_escalation_precision; calibration_error; selective_risk
remove reference-bank audit while keeping top-k retrieval evidence; set gamma=0 so contaminated-reference risk cannot affect the score; replace retrieval_consistency_score with raw nearest-neighbor distance only; use random same-class normal references instead of top-k retrieved references; disable escalation policy and force every case to accept or reject; vary contamination rate in the normal memory bank; vary factory-shift severity by cross-subset memory construction
Run non-agent PatchCore with the same memory bank, same base heatmaps, same validation thresholds, and the same report template but without retrieval audit, contamination scoring, or escalation.; Run the retrieval-audit loop with shuffled test-region to reference-region pairings; improvements should disappear if gains come from valid evidence links rather than threshold changes.; Inject visually normal held-out images into the memory bank as a placebo contamination condition; the audit should not flag them at the same rate as injected anomalous references.
At matched defect_region_recall, reduce false positive regions or false positive images by at least 10% versus non-agent PatchCore on MVTec_AD or VisA shifted or contaminated splits.; Improve evidence_grounding_score by at least 15% over a non-agent report generated from the same heatmap and threshold.; Detect injected contaminated reference images with AUROC above 0.75 on synthetic contamination splits while keeping placebo normal-injection false positive rate below the selected operating point.; Do not reduce pixel_level_auroc or pro_score by more than 1 percentage point versus the strongest direct IAD baseline on the same evaluation split.; Failure if tool_success_rate is below 90%, if shuffled-reference negative control matches the full method, or if gains are explained only by a lower operating threshold.

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W4404704036

Risks, controls, or fallback:
Risk: synthetic shift and contamination may not reflect real factory drift, and reference-bank outlier scores may confuse rare but valid normal appearances with contamination. Fallback: report results separately for natural category-level shifts, acquisition-condition shifts, placebo normal injections, and injected contamination, and position the module as a reference-bank diagnostic and escalation aid rather than a universal detector if detection AUROC does not improve.

---

Idea 2
Title:
Disagreement-Gated Mask Selection Agent for Weakly Labeled Defect Localization

Core proposal:
Use an inspection agent that converts IAD heatmap peaks into prompts, obtains candidate masks from SAM or SAM2, optionally obtains text-conditioned boxes from GroundingDINO when a defect taxonomy is available, and accepts a mask only if it is supported by anomaly heatmaps and remains stable under negative-control transformations. The agent refuses or escalates masks that mostly follow object borders, illumination changes, or normal texture regions.

Motivation or baseline weakness:
SAM/SAM2 can segment salient object parts rather than true defects, while IAD heatmaps from PatchCore, DRAEM, FastFlow, or AnomalyCLIP can produce noisy regions under texture, lighting, or boundary variation. With weak or missing pixel labels, selecting a trustworthy defect mask requires checks that distinguish localized defect evidence from generic saliency.

Mechanism or approach:
A mask-selection policy that scores each candidate mask m by U(m)=w1*heatmap_overlap(m)+w2*semantic_anomaly_support(m)+w3*normal_contrast(m)-w4*negative_control_instability(m)-w5*border_saliency_penalty(m)-w6*area_prior_penalty(m). heatmap_overlap is computed from frozen IAD heatmaps, semantic_anomaly_support from AnomalyCLIP or CLIP-style prompts when available, normal_contrast from same-class normal reference patches, and negative_control_instability from brightness, color, blur, crop, and normal-image placebo tests.
Select the smallest evidence-supported region that maximizes defect_region_precision and mask_iou while constraining missed defects. Tune mask thresholds and refusal thresholds on validation data to maximize calibrated mask utility under a minimum defect_region_recall constraint and an explicit human_review_budget.

Experiment and implementation plan:
PatchCore; DRAEM; FastFlow; AnomalyCLIP; SAM; SAM2; GroundingDINO; thresholded strongest IAD heatmap
MVTec_AD or VisA images; pixel masks where available for evaluation only; product_category labels; optional defect taxonomy for text prompts; normal reference images for same-class negative contrast; image augmentations for lighting, blur, color, crop, border, and texture negative controls; normal-only images used as placebo prompts to estimate false mask acceptance
generate_iad_heatmaps.py; prompt_sam_from_heatmaps.py; generate_groundingdino_candidates.py; compute_cross_model_disagreement.py; run_negative_control_augmentations.py; select_or_refuse_mask.py; evaluate_mask_and_region_metrics.py; emit_region_grounded_report.py
pixel_level_auroc; pro_score; mask_iou; defect_region_precision; defect_region_recall; f1_score; tool_success_rate; report_correctness; evidence_grounding_score; false_alarm_reduction; human_escalation_precision; selective_risk
SAM/SAM2 refinement without the mask-selection policy; mask-selection policy without negative-control augmentations; single IAD heatmap support instead of cross-model agreement or disagreement checks; no retrieved normal-patch contrast; always accept the top SAM or SAM2 mask; always accept the thresholded heatmap mask; disable escalation for low-agreement masks; remove border_saliency_penalty and area_prior_penalty
Use SAM2 refinement directly on IAD heatmap prompts without disagreement scoring, negative-control tests, or refusal; this tests whether segmentation alone is responsible for any gain.; Run the full mask-selection policy on normal-only images and on masks prompted from low-score heatmap locations; accepted-mask rate should remain low.; Apply brightness and color jitter that should not create a physical defect; accepted defect masks should be stable or refused rather than moving to illumination artifacts.
Improve mask_iou by at least 5 absolute points or defect_region_precision by at least 10% versus the thresholded strongest IAD heatmap on MVTec_AD or VisA.; Reduce false positive regions from lighting, texture, or border perturbations by at least 10% at matched defect_region_recall.; Maintain image_level_auroc within 1 point of the strongest IAD baseline when mask selection is used only for localization and reporting.; Improve evidence_grounding_score over the non-agent mask-report baseline by at least 15%.; Failure if SAM/SAM2-only negative control matches the full agent on localization and agent workflow metrics, or if normal-only placebo acceptance is not lower than anomalous-image acceptance.

Evidence paper IDs:
openalex:W4380551232; openalex:W7154655652; openalex:W7162893906; openalex:W7153670799

Risks, controls, or fallback:
Risk: candidate masks may be dominated by object boundaries instead of defects, especially for small scratches or low-contrast defects, and GroundingDINO text prompts may be unreliable when the defect taxonomy is incomplete. Fallback: restrict the module to region proposal verification, keep the original IAD heatmap as the primary localization output, disable text-prompted boxes when no defect vocabulary is available, and escalate small high-score regions when mask agreement is unreliable.

---

Idea 3
Title:
Evidence-Grounded Report Checker with Selective Human Escalation

Core proposal:
Add a report-verification agent that converts detector outputs and optional VLM drafts into structured claims, then verifies each claim against an anomaly region, same-class normal reference evidence, and calibrated model scores. Unsupported claims are removed, downgraded to failure_warning, or routed to human_review. The report is accepted only when claim-region-reference links pass grounding and confidence checks.

Motivation or baseline weakness:
WinCLIP, AnomalyCLIP, and VLM-style inspection agents can generate plausible defect descriptions that are not supported by localized visual evidence. Conventional IAD baselines output scores and heatmaps but lack calibrated report confidence, claim-level evidence checks, and selective human escalation behavior.

Mechanism or approach:
A structured report checker that validates claim-region-reference triples and calibrates report confidence using validation-set conformal or quantile thresholds over detector confidence, region overlap consistency, and reference-evidence contrast. It outputs anomaly_score, anomaly_mask_or_region, defect_type when supported, evidence, normal_reference_used, confidence, recommended_action, and failure_warning. If defect_type is not supported by dataset labels or grounded visual evidence, the field is set to unknown_defect rather than hallucinated.
Optimize selective reporting by minimizing report_error and unsupported_claim_rate under a fixed human_review_budget, while preserving image_level_auroc, pixel_level_auroc, and defect_region_recall relative to the underlying IAD baselines. The selective policy chooses accept_normal, reject_defective, or human_review using calibrated confidence and claim-grounding validity rather than free-form language confidence.

Experiment and implementation plan:
WinCLIP; AnomalyCLIP; PatchCore; PaDiM; CLIP-style prompt report baseline; unchecked VLM or template report baseline; anomaly-score-only escalation baseline
MVTec_AD or VisA images; product_category labels; normal reference images; optional defect taxonomy; optional mask or bounding-box labels for region grounding evaluation; inspection_goal text such as reject, repair, or reinspect; human-audited subset for report semantics when public labels do not specify defect descriptions
run_iad_baselines.py; retrieve_reference_evidence.py; draft_vlm_report.py; check_claim_region_reference_links.py; calibrate_confidence_and_selective_policy.py; route_human_escalation.py; score_report_correctness_and_grounding.py; export_structured_inspection_report.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; report_correctness; evidence_grounding_score; human_escalation_precision; false_alarm_reduction; calibration_error; selective_risk; out_of_distribution_detection
VLM or template report without evidence checker; evidence checker without retrieved normal references; confidence calibration using anomaly_score only; escalation based only on anomaly_score; remove failure_warning field; replace structured schema with free-form report; use report checker on random regions; force every case to be accepted with no human_review option
Generate a VLM or template report from the same anomaly score and mask but remove claim-region-reference verification and selective escalation; compare report correctness, unsupported claims, and human escalation precision.; Shuffle normal reference patches across product categories before report checking; grounding and confidence should degrade rather than remain unchanged.; Attach defect claims to random low-score regions; the checker should reject or mark the claims as unsupported.
Improve evidence_grounding_score by at least 20% versus unchecked VLM or template reports generated from the same detector outputs.; Reduce unsupported defect descriptions by at least 30% without reducing defect_region_recall by more than 2 points.; Achieve at least 10% relative lower calibration_error than raw IAD confidence or anomaly-score-only report confidence.; At a fixed human review budget, improve selective_risk or false_alarm_reduction over anomaly-score-only escalation.; Failure if report_correctness or evidence_grounding_score does not improve over the non-agent negative control, or if shuffled-reference and random-region controls pass verification at the same rate as true evidence links.

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W7154655652; openalex:W7153328271; openalex:W7138099583

Risks, controls, or fallback:
Risk: automatic report correctness labels may be noisy because public IAD datasets have limited defect taxonomies, and generic VLM drafts may over-specify defect types not present in labels. Fallback: evaluate claim grounding objectively through region-reference links, force unsupported defect categories to unknown_defect, use a small human audit subset only for report semantics, and keep detection and localization experiments fully reproducible on MVTec_AD or VisA.

### Candidate B

Idea 1
Title:
Reference-Auditing Agent for Shift-Robust Industrial Anomaly Detection

Core proposal:
Build an agentic IAD workflow that explicitly audits and reweights the normal reference memory before using it for retrieval-augmented anomaly scoring. The agent coordinates tools for product-category routing, normal-patch retrieval, PatchCore or PaDiM scoring, reference-bank contamination checks, SAM/SAM2 candidate region extraction with a mask-selection policy, cross-model verification, calibrated confidence estimation, structured report generation, and human escalation. The central new component is a reference-consistency auditor that estimates whether retrieved normal patches are factory-shifted, contaminated by subtle defects, or visually inconsistent with the test region before they are allowed to support a final decision.

Motivation or baseline weakness:
Nearest-neighbor IAD methods such as PatchCore are strong but can fail when the normal memory bank shifts across factories or contains contaminated normal images. Agentic frameworks and VLM-based IAD can produce reports, but reports are unsafe if the underlying references are unverified. This idea targets the required gaps of normal-reference shift, contaminated memory banks, false-positive heatmaps from lighting or texture variation, unsupported VLM descriptions, and deciding when to escalate to a human. The hypothesis is that an explicit audit-and-verification loop can reduce false alarms at matched recall while improving evidence-grounded reporting over a non-agent baseline.

Mechanism or approach:
The workflow uses the following tools: image preprocessor, product-category router, normal-reference retriever, PatchCore scorer, PaDiM scorer, optional WinCLIP or AnomalyCLIP semantic scorer, SAM/SAM2 region proposer, reference-bank auditor, calibration module, report checker, and human-escalation module. The memory state stores normal patch embeddings, source factory or batch metadata when available, retrieval neighbors, audit scores, and rejected reference examples. For each test image, the agent retrieves top-k normal patches for each suspicious region and computes a retrieval-consistency score comparing the test region to same-category normal references under feature, color-normalized, and local-geometry views. The reference-bank auditor flags candidate normal references as shifted or contaminated if they are repeatedly retrieved for high-anomaly regions, have high disagreement with other normal references, or are close to known defect-like patterns from optional taxonomy prompts. The anomaly mask is produced by combining PatchCore or PaDiM heatmaps with a SAM/SAM2 mask-selection policy: candidate masks are accepted only if they overlap high-score heatmap regions, are not similarly activated in negative-control normal images, and are supported by clean retrieved references. Cross-model disagreement between PatchCore, PaDiM, and optionally WinCLIP/AnomalyCLIP drives a verification loop: high disagreement triggers additional retrieval, reference audit, and possible escalation. Confidence is calibrated using validation normal images and sparse anomaly masks when available, optimizing a selective-prediction policy for false-alarm reduction at matched recall. The structured report schema includes anomaly_score, anomaly_mask_or_region, defect_type, evidence, normal_reference_used, confidence, recommended_action, and failure_warning. A report checker rejects claims whose defect type or severity cannot be linked to a region and to specific normal-reference contrasts.

Experiment and implementation plan:
Datasets: first evaluate on MVTec_AD and VisA, then test reference-shift stress on MVTec_LOCO, BTAD, or MPDD by mixing normal banks across product categories, acquisition conditions, or artificially contaminated normal samples. Direct baselines: PatchCore, PaDiM, FastFlow, RD4AD, WinCLIP, and AnomalyCLIP where applicable. Transfer baselines: CLIP retrieval, SAM/SAM2 mask proposals, and a tool-using RAG inspection agent without reference auditing. Metrics: image_level_auroc, pixel_level_auroc, aupr, pro_score, f1_score, mask_iou, defect_region_precision, defect_region_recall, calibration_error, selective_risk, out_of_distribution_detection, tool_success_rate, report_correctness, evidence_grounding_score, false_alarm_reduction, and human_escalation_precision. Ablations: remove the reference auditor, remove retrieval-consistency scoring, remove cross-model disagreement, use SAM/SAM2 without mask-selection policy, use contaminated memory without audit, remove the report checker, and replace the agent with a fixed PatchCore-plus-report pipeline. Negative control: a non-agent PatchCore or PaDiM system with the same retrieved references but no audit, verification loop, or escalation. Minimal new module: the reference-consistency auditor plus a lightweight policy that reweights or rejects retrieved references. MVP artifacts: reference-bank audit logs, anomaly masks, calibrated scores, JSON reports, human-escalation decisions, and a dashboard showing accepted versus rejected references. Failure criteria: the idea fails if detection/localization metrics do not match or exceed the strongest IAD baseline, or if agent metrics such as evidence_grounding_score, tool_success_rate, false_alarm_reduction, and human_escalation_precision do not improve over the non-agent negative control under shifted or contaminated references. Main risks: audit thresholds may over-reject valid references, sparse labels may weaken calibration, and synthetic contamination may not fully represent real factory drift.

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W4404704036; openalex:W7154655652; openalex:W4380551232

---

Idea 2
Title:
Disagreement-Guided Mask Selection Agent for Weakly Labeled Defect Localization

Core proposal:
Develop an inspection agent that converts weak image-level anomaly evidence into reliable region-level masks by using cross-model disagreement as an active self-verification signal. The agent uses frozen IAD models and promptable segmentation tools, but the novelty is not SAM/SAM2 refinement alone; it is a mask-selection and rejection policy that requires agreement among anomaly heatmaps, retrieved normal references, negative-control masks, and region-grounded report claims. The output is a calibrated anomaly mask, defect type, evidence links, confidence, recommended action, and failure warning.

Motivation or baseline weakness:
Industrial datasets often have few or no pixel-level defect labels, making supervised segmentation difficult. Promptable segmentation can generate plausible masks, but these masks may capture salient texture, object parts, shadows, or lighting changes rather than defects. Existing VLM-style reports can also hallucinate defect descriptions. This idea targets weak or missing pixel labels, false-positive heatmaps from texture or lighting variation, and unsupported defect descriptions by treating localization as an agentic verification problem: a region is accepted only if multiple tools provide compatible evidence and if the same policy rejects matched normal controls.

Mechanism or approach:
The agent tool list includes PatchCore, DRAEM, RD4AD, optional FastFlow, WinCLIP or AnomalyCLIP, CLIP normal-reference retrieval, SAM/SAM2, optional GroundingDINO for taxonomy-conditioned prompts, calibration, report generation, report checking, and human escalation. The memory state contains image-level scores, pixel heatmaps, candidate SAM/SAM2 masks, negative-control masks generated on normal validation images, retrieved normal patches, defect taxonomy prompts, and verification outcomes. The new component is a disagreement-guided mask selector. It first proposes candidate regions from the union of high-response heatmaps and SAM/SAM2 masks prompted by points, boxes, or taxonomy-conditioned phrases. For each candidate region, it computes: heatmap support from multiple IAD models, retrieval-consistency gap against normal patches, semantic compatibility with optional defect taxonomy, boundary plausibility, and negative-control activation frequency on visually similar normal images. The verification loop asks whether the same candidate mask would be selected on normal references or under benign image perturbations such as brightness and color normalization; masks that are unstable or common on normal controls are rejected. Defect type is assigned only if a VLM or CLIP-style semantic tool can link the label to the selected region and retrieved references; otherwise the report uses an abstaining defect_type such as unknown_surface_anomaly and raises a failure_warning. Confidence calibration maps model agreement, retrieval consistency, and negative-control rarity into a selective risk score. Escalation occurs when localization is high but semantic type is uncertain, when models disagree strongly, or when confidence falls below a product-specific threshold.

Experiment and implementation plan:
Datasets: MVTec_AD and VisA for the first MVP, using full masks for evaluation but hiding pixel labels during method development; extend to MVTec_LOCO for logical anomalies and false-positive stress. Direct baselines: PatchCore, DRAEM, RD4AD, PaDiM, FastFlow, WinCLIP, and AnomalyCLIP. Transfer baselines: SAM/SAM2 prompted by raw heatmap boxes, GroundingDINO taxonomy prompts, CLIP retrieval, and a simple VLM report agent. Metrics: image_level_auroc, pixel_level_auroc, aupr, pro_score, f1_score, mask_iou, defect_region_precision, defect_region_recall, calibration_error, selective_risk, tool_success_rate, report_correctness, evidence_grounding_score, false_alarm_reduction, and human_escalation_precision. Ablations: remove negative-control mask rejection, remove retrieval-consistency scoring, remove cross-model disagreement, remove semantic claim checking, use SAM/SAM2 heatmap boxes without selection policy, train thresholds with sparse masks versus no masks, and disable escalation. Negative control: PatchCore plus SAM/SAM2 refinement plus VLM report without verification or negative controls. Minimal new module: the disagreement-guided mask selector with negative-control rejection and calibrated abstention. MVP artifacts: selected masks, rejected masks with reasons, model-disagreement maps, reference patches, region-linked report JSON, and escalation logs. Failure criteria: the idea fails if mask_iou, pro_score, or defect_region_precision do not improve over heatmap-only and SAM/SAM2-without-policy baselines, or if evidence_grounding_score and false_alarm_reduction do not improve over the non-agent control. Risks: candidate masks may miss tiny defects, negative controls may be too conservative for subtle texture defects, and taxonomy-conditioned prompts may bias the agent toward known defects while rare unknown defects require escalation.

Evidence paper IDs:
openalex:W7153670799; openalex:W7154655652; openalex:W7162893906; openalex:W4380551232; openalex:W7138099583

---

Idea 3
Title:
Selective Evidence-Grounded Inspection Agent with Human Escalation Optimization

Core proposal:
Create an agentic quality-control system that optimizes not only anomaly detection but also when to issue a final automated report versus when to escalate to a human inspector. The agent combines frozen IAD scores, retrieved normal evidence, region-level verification, VLM report drafting, and a report checker that links every claim to image regions and reference patches. The main new component is a selective prediction and escalation policy trained or tuned to reduce false alarms at matched recall while preserving report correctness and evidence grounding.

Motivation or baseline weakness:
Manufacturing inspection needs actionable decisions, not only anomaly scores. Overconfident automated reports can create unnecessary scrap, missed defects, or unsupported defect descriptions. Existing IAD and VLM methods often report image or pixel metrics but may not measure tool success, evidence grounding, false-alarm reduction, or human-escalation precision. This idea targets the research gaps of unsupported VLM defect descriptions, false-positive heatmaps, weak localization evidence, and deciding when to escalate. The key claim is that a calibrated selective agent can outperform a non-agent pipeline in operational quality-control metrics even when using the same frozen IAD models.

Mechanism or approach:
The agent uses tools for image preprocessing, product-category recognition, normal-reference retrieval, PatchCore/PaDiM/FastFlow/RD4AD scoring, WinCLIP or AnomalyCLIP semantic scoring, SAM/SAM2 candidate localization with the policy from negative controls, report drafting by a VLM such as LLaVA or Qwen-VL, evidence-grounded report checking, confidence calibration, and escalation. The memory or retrieval state stores normal references, top-k matched patches, anomaly regions, model scores, calibration bins, previous failure warnings, and human-review outcomes when available. The new component is a selective inspection policy that takes features from anomaly score, mask stability, cross-model disagreement, retrieval-consistency score, report-checker pass rate, semantic-label uncertainty, and OOD/reference-shift signals. It chooses one of three actions: accept as normal, accept as anomalous with structured report, or escalate/refuse due to insufficient evidence. The verification loop runs before final reporting: it checks whether each report claim has a corresponding selected region, whether that region differs from retrieved normal references, whether the claimed defect type is supported by taxonomy or visual evidence, and whether any model strongly contradicts the decision. If verification fails, the agent either downgrades defect_type to unknown, adds failure_warning, or escalates. Confidence calibration is evaluated with expected calibration error and selective risk, with thresholds selected on validation data to reduce false alarms at matched defect recall. Human-in-the-loop escalation is simulated using ground-truth labels in benchmark experiments and can be logged for real deployment.

Experiment and implementation plan:
Datasets: MVTec_AD and VisA for initial image and region evaluation; MVTec_LOCO for logical anomaly and report stress; BTAD or MPDD for external validation. Direct baselines: PatchCore, PaDiM, FastFlow, RD4AD, DRAEM, WinCLIP, and AnomalyCLIP. Transfer baselines: CLIP retrieval, LLaVA or Qwen-VL report generation, SAM/SAM2 region proposals, and a generic tool-using agent without selective calibration. Metrics: image_level_auroc, pixel_level_auroc, aupr, pro_score, f1_score, mask_iou, defect_region_precision, defect_region_recall, report_correctness, evidence_grounding_score, tool_success_rate, false_alarm_reduction, human_escalation_precision, calibration_error, selective_risk, and out_of_distribution_detection. Ablations: remove escalation, use fixed anomaly-score thresholds, remove report checker, remove retrieval evidence, remove cross-model disagreement, remove calibration, remove SAM/SAM2 mask-selection negative controls, and replace the selective policy with a VLM-only decision. Negative control: a non-agent IAD baseline that outputs anomaly score and mask, followed by an unverified VLM-generated report. Minimal new module: the selective evidence-grounded escalation policy plus report-claim checker. MVP artifacts: calibrated decision thresholds, action logs, report JSON files, evidence links to regions and references, human-escalation queues, and evaluation scripts for workflow metrics. Failure criteria: the idea fails if selective risk or calibration_error does not improve over score-threshold baselines, if human_escalation_precision is poor, or if evidence_grounding_score and report_correctness do not improve over the unverified report control while maintaining detection and localization performance. Risks: benchmark ground truth may not perfectly proxy human review cost, report correctness scoring may require careful annotation, and overly conservative escalation could reduce automation benefits.

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W7153328271; openalex:W7138099583; openalex:W4404704036

---

## Item 16: HUM-61bc1d0f2a

类型：`portfolio`

### Candidate A

Idea 1
Title:
Reference-Consistency Agent for Auditing Shifted or Contaminated Normal Memory Banks

Core proposal:
Add an agent-managed reference audit loop around a frozen PatchCore-style memory bank. For each high-score test region, retrieve the top-k normal patches, compute local feature-distance statistics, neighbor-to-neighbor compactness, product-category consistency, and disagreement between the test patch and its retrieved references. The auditor flags reference clusters as potentially contaminated when they are both close to anomalous test regions and inconsistent with the clean validation distribution. Scoring is rerun after excluding flagged references, and the agent reports a defect only when anomaly evidence remains stable after the audit. If the anomaly score collapses or retrieved references are invalid, the agent outputs an explicit reference-shift or ambiguous-normal-variation escalation rather than a defect claim.

Motivation or baseline weakness:
PatchCore and other normal-reference IAD methods can produce unstable anomaly scores when the normal memory bank is shifted across factories or contaminated by subtle defective samples. Patch-level heatmaps alone do not indicate whether the nearest normal references are trustworthy evidence, and evidence-grounded inspection reports remain weak without an explicit reference audit.

Mechanism or approach:
A frozen-feature reference-bank auditor that records top-k retrievals, estimates patch-level reference consistency and contamination likelihood from validation-calibrated distance distributions, excludes suspicious references for a second scoring pass, and exposes accept, refuse, or escalate decisions to the inspection agent.
Optimize a calibrated selective decision rule that reduces false positives from shifted or contaminated reference banks while preserving defect recall: accept an automated defect decision only when the audited anomaly score remains high, retrieved normal evidence is category-valid, consistency to clean references is low for the test region, and estimated contamination probability of the supporting references is below a threshold.

Experiment and implementation plan:
PatchCore; PaDiM; RD4AD; WinCLIP
MVTec_AD normal training images and anomalous test images with masks; VisA normal training images and anomalous test images with masks; synthetic contaminated memory banks created by injecting 1%, 5%, and 10% anomalous images or shifted normal images into reference sets; factory-shift or proxy-shift splits created with product-category-preserving lighting, background, acquisition, or texture changes; product_category metadata and normal_reference_images for retrieval validation
build_patchcore_or_padim_memory_bank.py; inject_reference_contamination_and_factory_shift.py; retrieve_topk_reference_patches.py; compute_retrieval_consistency_and_bank_audit.py; rerun_scoring_after_reference_exclusion.py; agent_inspection_loop_with_audit_and_escalation.py; evaluate_detection_localization_agent_metrics.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; f1_score; mask_iou; defect_region_precision; defect_region_recall; false_alarm_reduction; tool_success_rate; evidence_grounding_score; report_correctness
remove reference-bank audit and use raw PatchCore scores; retrieve random same-category normal patches instead of nearest references; disable contaminated-reference exclusion but keep the reporting agent; replace patch-level retrieval consistency with global image similarity only; vary contamination rates and factory-shift severity; calibrate thresholds on clean validation only versus shifted validation; use PaDiM or RD4AD features for retrieval while keeping the same audit policy
Generate a structured report from the raw PatchCore heatmap without reference audit or retrieval consistency checking; Run the audit with randomly permuted product categories where retrieved references should be rejected as invalid evidence; Inject only clean same-category normal references and verify that the auditor does not remove a large fraction of valid memory-bank patches; Apply the exclusion step to low-score normal test images and require no new defect reports to be introduced
At matched defect_region_recall, reduce false alarms by at least 15% relative to PatchCore on contaminated or shifted reference banks; Maintain image_level_auroc within 2 percentage points of PatchCore on clean memory banks; Improve evidence_grounding_score by at least 20% over the non-auditing report baseline; Achieve tool_success_rate above 90% for retrieval, audit, reranking, and report-generation calls; Failure if the audit improves clean-bank metrics only by discarding difficult cases, or if false_alarm_reduction comes with more than a 5% absolute drop in defect_region_recall

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W4404704036

Risks, controls, or fallback:
Risk: the consistency score may reject legitimate rare normal variants and increase escalations. Fallback: use category-specific validation calibration, cap the allowed fraction of excluded references, and introduce a conservative abstention band so uncertain reference-shift cases are escalated instead of converted into unsupported defect calls.

---

Idea 2
Title:
Disagreement-Gated Mask Selection Agent for Weakly Labeled Defect Localization

Core proposal:
Use an inspection agent that first obtains frozen IAD heatmaps from DRAEM, RD4AD, and optionally FastFlow as a weaker stress-test baseline. Candidate points and boxes are generated from high-confidence heatmap regions and passed to SAM or SAM2. Each candidate mask is accepted only when it has strong support from at least one reliable IAD heatmap, low spatial disagreement among the stronger IAD sources inside the proposed defect region, limited overlap with known normal structures, and a negative response when the same prompting and scoring procedure is applied to retrieved same-category normal-reference regions. Masks that also appear on matched normal patches or depend on shuffled heatmaps are rejected or escalated. The final report links the selected mask to heatmap evidence and normal-reference counterexamples.

Motivation or baseline weakness:
SAM or SAM2 can segment visually salient regions that are not true defects, while IAD heatmaps from DRAEM, FastFlow, or RD4AD can be noisy under texture and lighting variation. Without a mask selection policy, normal-reference negative controls, and shuffled-evidence controls, promptable segmentation can falsely appear to improve defect localization.

Mechanism or approach:
A disagreement-gated mask selection policy that scores each candidate mask by heatmap support, cross-model spatial agreement, normal-reference negative-control response, prompt stability, and calibrated uncertainty, then returns accept, reject, or escalate decisions.
Maximize defect_region_precision and mask_iou under full-mask or sparse-box supervision by selecting a candidate mask only when it improves agreement-weighted anomaly evidence over raw heatmap thresholding and does not reproduce on retrieved normal-reference regions.

Experiment and implementation plan:
DRAEM; FastFlow; RD4AD; SAM; SAM2; GroundingDINO
MVTec_AD images with pixel masks; VisA images with pixel masks; weak-label variants created from image-level anomaly tags, sparse boxes, or sparse point prompts; normal_reference_images for each product category; lighting and texture perturbation splits for false-positive stress tests; known-normal test images for refusal evaluation
run_iad_heatmap_ensemble.py; generate_prompt_points_and_boxes_from_heatmaps.py; generate_sam_or_sam2_candidate_masks.py; retrieve_normal_counterfactual_regions.py; score_cross_model_disagreement_and_negative_controls.py; agent_mask_selection_and_report.py; evaluate_sparse_label_localization.py
pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; f1_score; tool_success_rate; report_correctness; evidence_grounding_score; false_alarm_reduction
use SAM or SAM2 refinement without disagreement-gated mask selection; use single IAD model support instead of cross-model disagreement; remove normal-reference negative-control mask checking; use GroundingDINO text boxes only without IAD heatmap evidence; train or tune thresholds with full masks versus sparse boxes only; disable calibration and use fixed anomaly thresholds; remove prompt-stability scoring across point and box prompts
Prompt SAM or SAM2 with high-saliency but low-anomaly regions and require the selected masks to be rejected; Run the mask-selection agent on known normal images and require refusal or no-defect reports; Shuffle heatmaps across images before mask selection to verify that accepted masks depend on real localized evidence; Retrieve normal-reference patches from mismatched product categories and require the agent to flag the negative-control evidence as invalid rather than using it; Use blank or uniform heatmaps with SAM or SAM2 prompts and require no claimed localization improvement
Improve mask_iou by at least 10% over the best raw IAD heatmap thresholding baseline on MVTec_AD or VisA; Improve defect_region_precision by at least 15% under lighting or texture perturbations while keeping defect_region_recall within 5% of the strongest IAD baseline; Reduce unsupported selected masks on normal-reference negative controls by at least 25% compared with SAM or SAM2 refinement without the policy; Achieve evidence_grounding_score above 0.8 for claims linked to selected regions and references; Failure if SAM or SAM2 refinement without the policy matches performance, if shuffled-heatmap controls are still accepted, or if tool_success_rate falls below 90%

Evidence paper IDs:
openalex:W7153670799; openalex:W7154655652; openalex:W4380551232

Risks, controls, or fallback:
Risk: cross-model disagreement can be high for very small or low-contrast true defects, causing over-rejection. Fallback: add a small-defect escalation mode where high local anomaly density, stable prompt response, and valid same-category normal-reference rejection permit a low-confidence localized anomaly report without forcing a specific defect label.

---

Idea 3
Title:
Evidence-Grounded Report Checker with Selective Human Escalation for VLM-Based IAD

Core proposal:
Build a lightweight agent workflow in which WinCLIP, AnomalyCLIP, CLIP, and PatchCore provide image-level anomaly scores and candidate regions. A VLM-style report generator drafts a structured report with fields for defect presence, region, visual evidence, normal-reference contrast, and uncertainty. A claim-to-evidence checker parses the report into atomic claims and verifies each claim against candidate region crops, anomaly masks or heatmaps, retrieved same-category normal references, and an optional allowed defect taxonomy. Unsupported claims are revised to generic localized-anomaly language, refused, or escalated to human review. The selective decision policy is calibrated on validation data to reduce false alarms at matched image-level recall rather than improving report fluency alone.

Motivation or baseline weakness:
WinCLIP, AnomalyCLIP, CLIP, and VLM-style inspection workflows can produce plausible semantic defect descriptions that are unsupported by localized visual evidence, especially when defect taxonomies are sparse, candidate regions are weak, or normal references shift.

Mechanism or approach:
A claim-to-evidence verifier that parses structured reports into atomic claims, links each claim to localized anomaly evidence and retrieved normal references, scores grounding support and taxonomy validity, and outputs calibrated confidence with accept, revise, refuse, or escalate decisions.
Optimize selective report correctness by maximizing report_correctness and evidence_grounding_score while maintaining image-level anomaly recall and reducing false alarms under a bounded automated-coverage target.

Experiment and implementation plan:
WinCLIP; AnomalyCLIP; CLIP; PatchCore
MVTec_AD and VisA images with product categories, anomaly masks, and defect labels where available; normal_reference_images for same-category retrieval-grounded comparison; optional defect_taxonomy converted to an allowed report vocabulary; human-review proxy labels derived from ground-truth anomaly presence, class labels where available, and mask overlap with claimed regions; normal-image subsets and masked-region variants for refusal and confidence-drop tests
run_winclip_anomalyclip_clip_patchcore_candidates.py; retrieve_normal_references_for_region.py; generate_structured_vlm_style_report.py; parse_report_into_atomic_claims.py; verify_claim_region_reference_grounding.py; calibrate_selective_escalation_policy.py; evaluate_report_and_agent_metrics.py
image_level_auroc; pixel_level_auroc; aupr; mask_iou; defect_region_precision; defect_region_recall; report_correctness; evidence_grounding_score; false_alarm_reduction; tool_success_rate; f1_score
remove evidence-grounded report checker and keep the original VLM-style report; remove retrieval of same-category normal references; allow free-form defect descriptions instead of taxonomy-constrained claims; use uncalibrated report confidence only; escalate based on anomaly score only without claim verification; replace region-linked evidence with whole-image captions; disable revision and allow only accept-or-reject decisions
Ask the report generator to describe defects on known normal images and require unsupported claims to be refused or escalated; Provide mismatched normal references from a different product category and require the checker to flag the evidence as invalid; Mask out the candidate defect region before report generation and require grounding confidence to drop; Shuffle candidate regions across images and require claim-to-region links to be rejected; Use a defect taxonomy with labels absent from the product category and require taxonomy-invalid claims to be revised or refused
Improve report_correctness by at least 20% over structured VLM-style reports without the checker; Improve evidence_grounding_score by at least 25% over retrieval-augmented reporting without claim verification; Reduce false alarms by at least 15% at matched image-level recall relative to WinCLIP or AnomalyCLIP report decisions; Keep defect_region_recall within 5% of the strongest candidate-region baseline while improving unsupported-claim refusal on normal images; Failure if detection or localization metrics improve but report_correctness and evidence_grounding_score do not exceed the non-checker baseline

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W7153328271; openalex:W7138099583; openalex:W7154655652

Risks, controls, or fallback:
Risk: the checker may be too strict when ground-truth defect labels are coarse or when the anomaly is visually real but semantically hard to name, lowering automated coverage. Fallback: output a generic localized anomaly with explicit uncertainty and escalate fine-grained defect naming to human review rather than hallucinating a specific defect type.

### Candidate B

Idea 1
Title:
Reference-Bank Audit Agent for Shift- and Contamination-Robust Industrial Anomaly Detection

Core proposal:
Develop an agentic inspection workflow that treats the normal reference set as an uncertain, auditable memory rather than a fixed clean bank. The agent retrieves normal patches, estimates whether the reference bank is shifted or contaminated, runs a strong IAD model, verifies the anomaly against multiple reference neighborhoods, and emits an anomaly mask, score, evidence links, confidence, recommended action, and escalation warning. The core new component is a contaminated-reference audit module that combines retrieval consistency, reference-neighborhood disagreement, and leave-one-cluster-out anomaly scoring to decide whether the reference memory is trustworthy for the current product category.

Motivation or baseline weakness:
PatchCore-style memory banks are strong for MVTec AD and VisA-style inspection, but they can fail when the normal bank contains subtle defects or when normal appearance shifts across factories, lighting, tooling, or suppliers. Existing heatmap-only pipelines usually assume clean references and do not tell the operator whether the evidence itself is unreliable. This proposal targets the required gaps of normal reference shift, contaminated memory banks, false-positive heatmaps from texture or lighting variation, and when to escalate to human review.

Mechanism or approach:
Agent workflow: (1) input parser reads test image or video frame, product category, inspection goal, optional normal references, defect taxonomy, and optional masks; (2) retrieval tool builds or queries a frozen DINOv2/CLIP/PatchCore patch index over normal references; (3) IAD tool runs PatchCore and optionally PaDiM or FastFlow to produce image-level anomaly score and pixel heatmap; (4) reference audit tool clusters normal patches and computes leave-one-cluster-out stability, cross-factory metadata shift if available, and a contaminated-reference likelihood; (5) retrieval-consistency verifier compares each candidate anomalous region with top-k normal patches and with nearest reference patches from different clusters, producing a score that penalizes anomalies explainable by a consistent normal neighborhood; (6) mask tool uses SAM only after heatmap-derived prompts and applies a mask selection policy based on anomaly energy inside mask, boundary compactness, overlap with retrieved inconsistent patches, and negative-control prompts on normal references; (7) calibration tool maps IAD score, retrieval consistency, and audit score to confidence using validation normals plus synthetic/held-out anomalies; (8) escalation policy refuses or escalates if confidence is low, reference audit is failed, cross-model disagreement is high, or the defect description lacks region-grounded evidence; (9) report generator outputs a structured schema with anomaly_score, anomaly_mask_or_region, defect_type, evidence, normal_reference_used, confidence, recommended_action, and failure_warning. Direct baselines: PatchCore, PaDiM, FastFlow, WinCLIP. Transfer baselines/components: CLIP retrieval, SAM mask proposal, tool_using_agent, retrieval_augmented_generation. Minimal new module: reference-bank audit plus retrieval-consistency scoring and a small calibration layer; all vision encoders remain frozen.

Experiment and implementation plan:
Datasets: start with MVTec_AD and VisA; add MVTec_LOCO for logical anomalies and reference-shift stress tests; optionally BTAD or MPDD for cross-dataset transfer. Construct proxy contamination by injecting a controlled fraction of anomalous training images or high-score normal outliers into the reference bank; construct reference shift by training memory on one subset of product instances/lighting and testing on another, or by cross-category/near-category normal references where valid. Metrics: image_level_auroc, pixel_level_auroc, aupr, pro_score, f1_score, mask_iou, defect_region_precision, defect_region_recall, calibration_error, selective_risk, out_of_distribution_detection, tool_success_rate, report_correctness, evidence_grounding_score, false_alarm_reduction, and human_escalation_precision. Ablations: remove reference audit; remove retrieval-consistency score; use PatchCore heatmap only; use SAM without mask selection; remove calibration; remove escalation; vary contamination rate and reference shift severity; replace PatchCore with PaDiM or FastFlow. Negative control: non-agent PatchCore plus static threshold and template report, with no memory audit or verification loop. MVP artifacts: reference-bank index, contamination simulator, audit dashboard, region evidence viewer, structured JSON report writer, calibration/evaluation scripts. Implementation plan: implement PatchCore/PaDiM baselines; build frozen feature index; add audit scoring; add region verifier and SAM mask selector; calibrate confidence; run contamination/shift sweeps; evaluate agent metrics and failure warnings. Failure criteria: reject the idea if the agent fails to improve evidence_grounding_score and tool_success_rate over the non-agent baseline, if false_alarm_reduction at matched recall is not improved, or if memory audit cannot detect contaminated banks above a predefined OOD AUROC threshold.

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W4404704036; openalex:W7154655652; openalex:W4380551232

---

Idea 2
Title:
Disagreement-Guided Self-Verifying Inspection Agent for Weakly Labeled Defect Localization

Core proposal:
Create an agent that localizes defects under sparse or missing pixel labels by forcing candidate anomaly regions to survive cross-model disagreement checks, retrieval-based normality tests, and region-grounded report validation. The central novelty is a self-verification loop that converts disagreement among PatchCore, RD4AD, DRAEM, WinCLIP/AnomalyCLIP, and SAM-derived masks into calibrated decisions about accept, refine, reject, or escalate. The goal is not just better heatmaps, but reliable mask-and-report outputs whose claims are linked to image regions and retrieved normal references.

Motivation or baseline weakness:
Industrial datasets often have image-level labels but limited masks, so methods can overfit to texture, illumination, or object boundaries and still produce plausible-looking heatmaps. VLMs can add semantic labels, but their defect descriptions may be unsupported by visual evidence. This proposal targets weak pixel supervision, false-positive heatmaps, unsupported VLM descriptions, and human escalation under uncertainty.

Mechanism or approach:
Agent workflow: (1) initial detector tool runs PatchCore, RD4AD, and either DRAEM or PaDiM to produce independent anomaly maps; (2) semantic tool runs WinCLIP or AnomalyCLIP with product-specific normal/defect prompts from the optional defect taxonomy; (3) proposal tool converts heatmap peaks and text-conditioned boxes into candidate regions and prompts SAM, using a mask selection policy based on cross-model anomaly overlap, region compactness, normal-reference dissimilarity, and rejection of masks that also appear on normal images; (4) retrieval tool fetches top-k visually similar normal patches and top-k category prototypes for each candidate region; (5) cross-model disagreement module computes region-level disagreement among detectors, VLM score, and retrieval consistency, separating likely true defects from lighting/texture artifacts; (6) self-checking loop asks whether each report claim has a linked region, score source, and normal-reference contrast; unsupported claims are removed or marked as unknown; (7) confidence calibration estimates selective risk from model agreement, retrieval consistency, mask stability, and product-category prior; (8) escalation policy sends cases to human review when high anomaly score conflicts with low evidence grounding, models disagree strongly, or mask stability is poor. Direct baselines: PatchCore, RD4AD, DRAEM, PaDiM, WinCLIP, AnomalyCLIP. Transfer baselines/components: SAM, GroundingDINO for optional text-conditioned boxes, CLIP retrieval, LLaVA or Qwen-VL as report verbalizer only after evidence checking. Borrowed components: heatmap ensembling, promptable segmentation, retrieval augmented generation, selective prediction. Minimal new module: region-level disagreement verifier plus evidence-grounded report checker.

Experiment and implementation plan:
Datasets: MVTec_AD and VisA first, using full masks for evaluation but training/calibration with image labels only or a small mask subset; extend to BTAD and MPDD for category transfer. Weak-label protocol: use 0%, 1%, 5%, and 10% pixel masks for calibration/mask selection; keep test masks hidden for evaluation. Metrics: image_level_auroc, pixel_level_auroc, aupr, pro_score, f1_score, mask_iou, defect_region_precision, defect_region_recall, calibration_error, selective_risk, tool_success_rate, report_correctness, evidence_grounding_score, false_alarm_reduction, and human_escalation_precision. Ablations: remove disagreement score; remove retrieval verifier; remove report checker; use SAM masks without selection; use VLM report without grounding; single-detector PatchCore; detector ensemble without agent decisions; calibration without escalation. Negative control: PatchCore or RD4AD plus SAM refinement and a VLM-generated report, with no verification loop or evidence checker. MVP artifacts: detector wrapper, candidate-region store, normal-reference retrieval viewer, disagreement matrix, evidence-grounded report checker, escalation logs. Implementation plan: run baseline detectors; normalize heatmaps; create candidate regions; implement SAM selection with normal-image negative controls; compute disagreement and retrieval features; train lightweight calibration head; implement JSON report checker; evaluate under weak-label protocols. Failure criteria: the idea fails if mask_iou/pro_score do not improve over the best non-agent IAD baseline under matched image-level recall, if evidence_grounding_score does not exceed the unverified VLM report baseline, or if selective prediction does not reduce false alarms at matched recall.

Evidence paper IDs:
openalex:W7154655652; openalex:W7162893906; openalex:W7153328271; openalex:W7138099583; openalex:W4380551232; openalex:W7153670799

---

Idea 3
Title:
Selective Human-Escalation Agent for False-Alarm Reduction at Matched Defect Recall

Core proposal:
Design a production-oriented inspection agent whose main research objective is selective prediction: automatically accept clear normal/defect cases, generate evidence-grounded defect reports for confident anomalies, and escalate ambiguous cases to human inspectors. The new component is a policy optimized for false-alarm reduction at matched defect recall using calibrated anomaly score, retrieval consistency, cross-model disagreement, report-grounding validity, and reference-bank trustworthiness. Unlike simple detector-plus-report pipelines, the agent is evaluated by both detection/localization metrics and workflow metrics that measure tool success, grounded evidence, and escalation precision.

Motivation or baseline weakness:
In manufacturing, a small gain in AUROC may not translate into operational value if false alarms overwhelm operators or if the model silently gives unsupported defect explanations. Human review should be triggered by measurable uncertainty sources: detector disagreement, OOD product/reference shift, weak evidence, or unreliable references. This proposal targets false-positive heatmaps, unsupported descriptions, calibration, and when to escalate to human review.

Mechanism or approach:
Agent workflow: (1) triage tool computes image-level and pixel-level anomaly outputs from PatchCore plus one complementary baseline such as PaDiM, FastFlow, or RD4AD; (2) retrieval tool fetches normal references and records memory state, including product category, reference clusters, nearest normal patches, and shift/audit flags; (3) localization tool proposes regions from heatmaps and optionally SAM/SAM2, but accepts masks only if a policy verifies anomaly concentration, stability under prompt perturbation, and absence of equivalent masks on normal references; (4) semantic labeling tool maps verified regions to optional defect taxonomy using WinCLIP/AnomalyCLIP or a frozen VLM, but labels are downgraded to unknown if not grounded; (5) report checker validates each defect_type and evidence sentence by requiring links to region coordinates, detector outputs, and retrieved normal contrasts; (6) calibration module estimates confidence and selective risk with conformal or temperature-calibrated scores on validation normals and synthetic/held-out anomalies; (7) escalation/refusal policy optimizes action thresholds for automatic pass, automatic reject/rework, or human review, with a constraint that defect recall matches the strongest detector baseline; (8) final report includes anomaly_score, anomaly_mask_or_region, defect_type, evidence, normal_reference_used, confidence, recommended_action, and failure_warning. Direct baselines: PatchCore, PaDiM, FastFlow, RD4AD, WinCLIP, AnomalyCLIP. Transfer baselines/components: SAM2 only with explicit mask selection and negative control, CLIP retrieval, LLaVA/Qwen-VL for structured report drafting after checker approval, tool_using_agent orchestration. Minimal new module: selective escalation policy jointly trained/evaluated on calibrated detector, retrieval, disagreement, and report-grounding features.

Experiment and implementation plan:
Datasets: MVTec_AD and VisA first; MVTec_LOCO for logical anomalies and false-positive stress; optional BTAD/MPDD for additional factory-like variation. Data construction: simulate operator workload by setting target recall levels from the best direct baseline and measuring false alarms and escalations under shifts, contaminated references, and sparse defect taxonomy. Video or multiview extension is optional only if frames/views are treated as repeated inspections with proxy validity defined by consistency of anomaly regions across views or time; otherwise the MVP is image-based. Metrics: image_level_auroc, pixel_level_auroc, aupr, pro_score, f1_score, mask_iou, defect_region_precision, defect_region_recall, calibration_error, selective_risk, out_of_distribution_detection, tool_success_rate, report_correctness, evidence_grounding_score, false_alarm_reduction, and human_escalation_precision. Ablations: no selective policy; score-only escalation; no report-grounding feature; no retrieval consistency; no cross-model disagreement; no reference audit; SAM2 without negative control; human escalation at random but same rate. Negative control: best IAD baseline with a fixed threshold and automatic VLM report, without tool-state memory, verification, or calibrated escalation. MVP artifacts: calibrated threshold optimizer, escalation simulator, structured report schema, report-grounding evaluator, dashboard showing accepted/rejected/escalated cases, and scripts for matched-recall false-alarm curves. Implementation plan: benchmark baselines; build feature table per image/region from detector scores, localization quality proxies, retrieval consistency, disagreement, and report-check status; fit selective policy on validation split; evaluate matched-recall false-alarm reduction and escalation precision; run stress tests for shift and contamination; audit reports manually or with region-claim matching. Failure criteria: the proposal fails if false_alarm_reduction at matched recall is not better than score-only thresholding, if human_escalation_precision is not above random/same-rate escalation, if report_correctness or evidence_grounding_score fails to improve over unverified VLM reporting, or if calibration_error/selective_risk worsens enough to make automatic decisions unsafe.

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W7154655652; openalex:W7153328271; openalex:W4380551232

---

## Item 17: HUM-a81c563b16

类型：`single_idea`

### Candidate A

Title:
Reference-Consistency Agent for Shifted or Contaminated Normal Memory Banks

Core proposal:
Add an agentic retrieval-audit loop for memory-based industrial anomaly detection. The loop first runs a PatchCore or PaDiM heatmap tool, extracts suspicious connected regions, retrieves top-k normal reference patches from the same product category and comparable spatial neighborhood, computes whether the retrieved references are internally consistent and visually compatible with the test region, audits the normal bank for likely contamination using cross-reference anomaly scores, and escalates when the base anomaly score is high but the reference evidence is ambiguous. Agent steps: run IAD heatmap tool, retrieve normal references, audit retrieved references for contamination and category/position mismatch, verify suspicious regions with a second IAD or CLIP-style semantic anomaly tool, calibrate confidence, then emit a structured report linking each decision to test-region crops and reference patches.

Motivation or baseline weakness:
PatchCore and PaDiM depend on normal-reference feature memories or distribution estimates, so factory shift or contaminated normal reference images can make abnormal regions appear normal or shifted normal regions look defective. Patch-level heatmaps alone also do not verify whether a retrieved normal patch is a valid counterexample for the suspicious test region.

Mechanism or approach:
A lightweight Reference Consistency and Bank Audit module that stores retrieval state as {test_region_id, product_category, spatial_bin, top_k_reference_ids, patch_distances, reference_anomaly_scores, consistency_score, bank_disagreement_score, audit_flag} and outputs calibrated anomaly confidence plus accept, escalate, or refuse decisions.
Optimize selective anomaly prediction under reference shift by combining base anomaly score A(x), normal-reference consistency C(x,R), and contamination penalty B(R) into S = A(x) * (1 - C(x,R)) + lambda * B(R), where C is high only when same-category retrieved references are mutually consistent and visually compatible with the test region. Choose thresholds on held-out shifted-normal and contaminated-bank validation splits to reduce false alarms at matched recall and minimize calibration error relative to anomaly-score-only calibration.

Experiment and implementation plan:
PatchCore; PaDiM; RD4AD; PatchCore plus non-agent top-k retrieval report; PaDiM plus fixed anomaly threshold
MVTec_AD train-normal and test anomaly images; VisA train-normal and test anomaly images; Constructed shifted-normal split using category-specific brightness, texture, viewpoint, compression, or factory-batch augmentations applied only to normal test images; Constructed contaminated-memory split by injecting 1%, 5%, and 10% anomalous patches or images into the normal bank while keeping clean-bank metadata for evaluation; Pixel masks or bounding boxes where available for region-level verification and grounding evaluation
build_patch_memory_bank.py; inject_contaminated_references.py; simulate_normal_reference_shift.py; run_iad_heatmaps.py; retrieve_region_references.py; audit_reference_bank.py; calibrate_selective_policy.py; generate_structured_inspection_report.py; evaluate_detection_localization_agent_metrics.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; false_alarm_reduction; tool_success_rate; evidence_grounding_score; human_escalation_precision; calibration_error; selective_risk; out_of_distribution_detection
Remove reference-bank audit while keeping nearest-neighbor retrieval; Use random same-category normal references instead of nearest retrieved references; Use anomaly score only without retrieval consistency; Use single IAD model verification instead of cross-model disagreement; Vary contamination rate and shift severity independently; Replace calibrated selective policy with a fixed anomaly threshold; Disable category and spatial-bin constraints during reference retrieval
Generate the same report schema from the PatchCore or PaDiM heatmap only, without retrieval audit or verification; Shuffle retrieved references across product categories while keeping report generation enabled; Allow the agent to cite reference identifiers but hide reference patches from the verifier; Inject clean normal patches labeled as contaminated and require the audit module not to over-escalate them; Use shifted normal images with no injected defects and measure whether the agent reduces, rather than increases, false alarms
On MVTec_AD or VisA, maintain at least 95% of the strongest direct baseline image_level_auroc while improving false_alarm_reduction by at least 15% on shifted-normal splits; Improve pixel_level_auroc or pro_score by at least 2 points over PatchCore or PaDiM on contaminated-bank splits; Reduce calibration_error by at least 10% relative to anomaly-score-only calibration; Achieve evidence_grounding_score of at least 0.80 for reports that cite normal references; Human_escalation_precision must exceed the non-agent heatmap-plus-report baseline by at least 10%; otherwise the agentic component is considered failed

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W4404704036; openalex:W7154655652

Risks, controls, or fallback:
Risk: reference consistency may reject legitimate rare normal variants or fail under severe domain shift, and contaminated-bank labels may be hard to infer without ground truth. Fallback: use category-specific conformal calibration, treat high internal reference disagreement as an escalation condition rather than an automatic anomaly decision, and report 'insufficient normal-reference support' instead of forcing a defect label.

### Candidate B

Title:
Reference-Consistency Agent for Shifted or Contaminated Normal Memory Banks

Core proposal:
Add an agentic retrieval-audit loop that retrieves top-k normal patches, computes a retrieval consistency score between each suspicious test region and normal references, audits the normal bank for contamination using cross-reference disagreement, and escalates when the anomaly score is high but reference consistency is ambiguous. Agent steps: run IAD heatmap tool, retrieve normal references, audit retrieved patches, verify with a second IAD/CLIP semantic tool, calibrate confidence, then emit a structured report with linked test region and reference patches.

Motivation or baseline weakness:
PatchCore and PaDiM depend on nearest-neighbor normal memories, so factory shift or contaminated normal reference images can make abnormal regions appear normal or make shifted normal regions look defective; their heatmaps also do not verify whether retrieved evidence is a valid normal counterexample.

Mechanism or approach:
A lightweight Reference Consistency and Bank Audit module that stores retrieval state as {test_region_id, top_k_reference_ids, patch_distances, reference_anomaly_scores, consistency_score, audit_flag} and outputs calibrated confidence plus escalation/refusal decisions.
Optimize selective anomaly prediction under reference shift by combining base anomaly score A(x), retrieval consistency C(x,R), and contamination penalty B(R) into S=A*(1-C)+lambda*B, with thresholds chosen to reduce false alarms at matched recall and to minimize calibration error on held-out normal-shift validation splits.

Experiment and implementation plan:
PatchCore; PaDiM; RD4AD; PatchCore plus non-agent top-k retrieval report
MVTec_AD train normal and test anomaly images; VisA train normal and test anomaly images; Constructed shifted-normal split using category-specific brightness, texture, viewpoint, or factory-batch augmentations; Constructed contaminated-memory split by injecting 1%, 5%, and 10% anomalous patches into the normal bank; Optional sparse masks or bounding boxes for region-level verification
build_patch_memory_bank.py; inject_contaminated_references.py; simulate_normal_reference_shift.py; run_iad_heatmaps.py; retrieve_region_references.py; audit_reference_bank.py; calibrate_selective_policy.py; generate_structured_inspection_report.py; evaluate_detection_localization_agent_metrics.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; false_alarm_reduction; tool_success_rate; evidence_grounding_score; human_escalation_precision; calibration_error; selective_risk; out_of_distribution_detection
Remove reference-bank audit while keeping retrieval; Use random normal references instead of nearest retrieved references; Use anomaly score only without retrieval consistency; Use single IAD model verification instead of cross-model disagreement; Vary contamination rate and shift severity; Replace calibrated selective policy with fixed anomaly threshold
Agent produces the same report schema from PatchCore heatmap only without retrieval audit or verification; Shuffle retrieved references across product categories while keeping report generation enabled; Allow the agent to cite references but hide reference patches from the checker
On MVTec_AD or VisA, maintain at least 95% of PatchCore image-level AUROC while improving false_alarm_reduction by at least 15% on shifted-normal splits; Improve pixel_level_auroc or pro_score by at least 2 points over PatchCore on contaminated-bank splits; Reduce calibration_error by at least 10% relative to anomaly-score-only calibration; Achieve evidence_grounding_score at least 0.80 for reports that cite normal references; Human_escalation_precision must exceed the non-agent baseline by at least 10%; otherwise the agentic component is considered failed

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W4404704036; openalex:W7154655652

Risks, controls, or fallback:
Risk: reference consistency may reject legitimate rare normal variants or fail under severe domain shift. Fallback: use category-specific conformal calibration and escalate instead of auto-rejecting when the retrieved reference set has high internal disagreement.

---

## Item 18: HUM-c02a218f47

类型：`portfolio`

### Candidate A

Idea 1
Title:
Reference-Consistency Agent for Auditing Shifted or Contaminated Normal Memory Banks

Core proposal:
Add a retrieval-verification loop around a frozen IAD backbone. For each image, the agent first computes a baseline anomaly heatmap and extracts candidate regions from connected components above a validation-set threshold. For each candidate region, it retrieves top-k normal patches from the memory bank using the same frozen feature space as the baseline, then computes four explicit reliability features: median top-k feature distance, top-k distance variance, low-level appearance mismatch between test and references, and reference-neighborhood impurity estimated by whether retrieved references are repeatedly retrieved by known anomalous validation patches or shifted-normal probes. The agent assigns each candidate one of three actions: accept baseline evidence, rerank with references whose reliability score exceeds a threshold, or escalate without changing the mask. Memory-bank entries are not permanently deleted during evaluation; they are only down-weighted per query to avoid conflating audit performance with data curation.

Motivation or baseline weakness:
PatchCore, PaDiM, and RD4AD rely on normal-reference statistics or memory banks. If those references contain shifted operating conditions, duplicate near-test samples, mislabeled anomalies, or missing normal modes, nearest-neighbor evidence can suppress true defects or create false positives from benign appearance changes. Standard non-agent pipelines usually output a heatmap without checking whether the retrieved normal evidence is trustworthy for the queried region.

Mechanism or approach:
A query-time reference-bank audit module over frozen IAD features, plus a deterministic inspection state machine with fields tool_list, candidate_regions, retrieved_reference_ids, retrieval_state, reference_reliability_scores, verification_status, calibrated_confidence, escalation_decision, final_mask, and report_schema.
Learn a calibrated selective scoring function on a validation split. The final anomaly score for region r is s_final(r)=alpha*s_heatmap(r)+beta*s_reference_contrast(r)-gamma*s_reference_unreliability(r), with alpha, beta, gamma and abstention thresholds selected to minimize validation selective risk at a fixed target recall. Image-level scores are the maximum accepted region score. The policy escalates when the top region has high heatmap score but unreliable or high-variance reference evidence.

Experiment and implementation plan:
PatchCore; PaDiM; RD4AD; FastFlow; WinCLIP; non-agent PatchCore with the same fixed memory bank; retrieval-only PatchCore using top-k neighbors without reliability audit
MVTec_AD train/test with normal memory banks; VisA train/test with normal references; synthetic contaminated memory banks created by injecting 1%, 5%, and 10% anomalous training or validation images into the normal bank; synthetic shifted banks created by applying lighting, color, blur, background, or camera-noise perturbations to a controlled fraction of normal references; held-out clean normal images to measure whether the audit falsely rejects valid normal modes; pixel masks or bounding boxes for localization evaluation where available
build_memory_bank.py to construct clean, shifted, and contaminated normal banks with saved reference IDs; run_iad_baselines.py for PatchCore, PaDiM, RD4AD, FastFlow, and WinCLIP heatmaps; retrieve_reference_patches.py for top-k reference retrieval per candidate region; audit_reference_bank.py for per-query reference reliability and bank-level contamination summaries; agent_inspection_loop.py for inspect-retrieve-verify-rerank-report-escalate workflow; calibrate_reference_policy.py for score weights and abstention thresholds; evaluate_detection_localization.py for image AUROC, pixel AUROC, AUPR, PRO, F1, mask IoU, precision, and recall; evaluate_agent_metrics.py for evidence grounding, false alarm reduction, calibration error, selective risk, escalation precision, and reference rejection accuracy
image_level_auroc; pixel_level_auroc; aupr; pro_score; f1_score; mask_iou; defect_region_precision; defect_region_recall; reference_rejection_precision; reference_rejection_recall; evidence_grounding_score; report_correctness; false_alarm_reduction_at_matched_recall; human_escalation_precision; calibration_error; selective_risk; out_of_distribution_detection_auroc
remove reference-bank audit while keeping top-k retrieval; use random normal references instead of nearest references; use top-1 retrieval instead of top-k distance variance; disable per-query reranking after unreliable-reference detection; replace calibrated selective policy with a fixed anomaly-score threshold; remove appearance-mismatch features and use feature distance only; remove structured evidence links from the report; evaluate clean bank versus contaminated bank versus shifted bank
non-agent PatchCore or RD4AD using the same memory bank and no verification loop; agent report generated after the baseline prediction but not allowed to change score, mask, confidence, or escalation; retrieval reliability computed from shuffled query-reference region pairs; memory bank with benign duplicate normal images injected instead of anomalous or shifted references, where the audit should not report high contamination; candidate regions sampled from low-anomaly background, where reference unreliability alone should not create positive anomaly predictions
On MVTec_AD or VisA, maintain at least 98% of the best direct baseline image-level AUROC on clean memory banks; Under 5% contaminated memory-bank injection, improve pixel-level AUROC or PRO by at least 2 percentage points over the same baseline without audit; Under shifted or contaminated banks, improve false_alarm_reduction_at_matched_recall by at least 10% over the strongest non-agent baseline; Achieve reference_rejection_precision at least 0.70 on synthetically contaminated references while keeping false rejection of clean references below 10%; Achieve evidence_grounding_score at least 0.80 for reported defect claims on sampled reports; Reduce calibration_error by at least 15% relative to the strongest non-agent IAD baseline; Human_escalation_precision must exceed escalation by raw anomaly-score uncertainty at the same escalation rate; Failure if localization degrades by more than 2 percentage points on clean memory banks or if audit decisions improve only on shuffled-reference controls

Risks, controls, or fallback:
Risk: synthetic contamination and shift may not capture real factory drift, and per-query reference down-weighting could remove rare but valid normal modes. Fallback: report clean-bank and corrupted-bank results separately, cap the fraction of references that can be down-weighted per query, use conservative escalation instead of automatic defect calls when rare-mode uncertainty is high, and include held-out clean normal modes as a guardrail.

---

Idea 2
Title:
Disagreement-Guided Mask Selection Agent for Weak-Label Anomaly Localization

Core proposal:
Introduce an agent that treats localization as candidate-mask selection rather than free-form segmentation. It first runs multiple frozen anomaly scorers and converts each heatmap into candidate seeds using thresholded connected components and local maxima. It then prompts a segmentation proposal tool with those seeds and also keeps simple heatmap components as fallback candidates. Each candidate mask receives explicit scores: mean anomaly inside the mask, anomaly contrast against a surrounding ring, agreement across frozen IAD models, contrast to retrieved normal patches for the same spatial/object region, boundary plausibility measured by edge alignment and mask compactness, and stability under benign photometric perturbations. The agent selects the highest calibrated mask, rejects all masks if scores are below threshold, or escalates when the top two masks have similar evidence but inconsistent locations.

Motivation or baseline weakness:
Image-level IAD models such as FastFlow, RD4AD, PatchCore, and WinCLIP often produce noisy heatmaps, while generic segmentation proposal tools can oversegment texture, shadows, specular highlights, or object boundaries. In weak-label settings, image labels identify whether a defect exists but do not identify which candidate mask is the defect, so naive refinement of heatmap peaks can amplify false positives.

Mechanism or approach:
A mask-selection policy that ranks candidate regions by cross-model agreement, retrieval contrast, boundary plausibility, and benign-perturbation stability, plus a schema-based report checker that requires every defect_type claim to reference one selected region, its score components, and at least one normal reference.
Given candidate masks M={m_i}, choose m*=argmax_i f(m_i), where f combines normalized intra-mask anomaly, local contrast, inter-model agreement, reference contrast, boundary plausibility, and perturbation stability. The calibration objective minimizes validation mask error and selective risk under an abstention budget. If no candidate exceeds the calibrated acceptance threshold, the output is normal or escalated depending on image-level anomaly confidence.

Experiment and implementation plan:
FastFlow; RD4AD; PatchCore; DRAEM; WinCLIP; SAM; SAM2; Mask2Former; heatmap thresholding without segmentation proposals; segmentation refinement from heatmap prompts without mask-selection policy
MVTec_AD with pixel masks reserved for evaluation and limited validation masks for calibration; VisA with segmentation annotations where available; BTAD or MPDD for additional industrial categories; weak-label training setting using image-level labels for thresholding and calibration while withholding most pixel masks from policy fitting; normal validation images for benign-perturbation and false-positive controls; optional defect taxonomy for constrained report labels
run_multi_iad_heatmaps.py for FastFlow, RD4AD, PatchCore, DRAEM, and WinCLIP outputs; generate_segmentation_proposals.py for candidate masks from heatmap prompts and connected components; retrieve_normal_evidence.py for reference patches matched to each candidate mask; score_mask_candidates.py for agreement, retrieval contrast, local contrast, boundary plausibility, and perturbation stability; calibrate_mask_policy.py for score normalization, ranking weights, and reject/escalate thresholds; agent_mask_selection.py for select-reject-escalate decisions; report_checker.py for region-grounded defect descriptions and unsupported-claim detection; evaluate_masks_and_reports.py for localization, selective localization, and workflow metrics
pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; image_level_auroc; f1_score; candidate_recall; selected_mask_precision; tool_success_rate; evidence_grounding_score; report_correctness; unsupported_claim_rate; false_alarm_reduction; calibration_error; selective_risk; human_escalation_precision
remove cross-model disagreement score; remove normal-reference retrieval contrast; remove benign-perturbation stability test; remove boundary plausibility and compactness features; use raw largest segmentation proposal instead of calibrated mask ranking; use heatmap thresholding only; disable report checker and allow free-form defect descriptions; train thresholds on one product category and test on another to measure category transfer
segmentation refinement driven by baseline heatmap prompts but with no mask-selection policy; mask candidates generated from randomly shifted heatmap peaks; normal images with only lighting, color, or mild blur perturbations, where selected defect masks should be rejected or remain stable without new defect claims; report-only VLM agent that cannot alter masks, scores, or escalation; candidate masks sampled from object boundaries on normal images, where boundary plausibility alone should not produce defect predictions; mask ranking with shuffled normal references, where retrieval-contrast benefits should disappear
Improve mask_iou or PRO by at least 3 percentage points over the best single IAD heatmap-thresholding baseline on MVTec_AD or VisA; Reduce false positive defect regions from texture, boundary, or lighting variation by at least 10% at matched defect-region recall; Maintain candidate_recall of at least 0.95 for defects larger than the minimum evaluable mask area before final selection; Evidence_grounding_score for reports must be at least 0.80, with unsupported_claim_rate below 5% on audited samples; Selective risk must decrease relative to raw anomaly-score thresholding when the agent abstains on no more than 20% of cases; Failure if segmentation proposals improve apparent mask shape but selected_mask_precision, evidence_grounding_score, or perturbation stability does not improve over non-agent baselines

Risks, controls, or fallback:
Risk: multiple anomaly models may share correlated errors, and segmentation proposals may miss small scratches, transparent defects, or low-contrast defects. Fallback: always include connected-component heatmap masks as candidates, tune candidate generation for high recall before ranking, mark small high-disagreement regions for human review, and report performance separately by defect size and texture complexity.

---

Idea 3
Title:
Selective Inspection Agent for Calibrated Human Escalation and Evidence-Grounded Reports

Core proposal:
Build a selective inspection agent that separates defect detection, report generation, report verification, and escalation. The agent runs one or more frozen IAD baselines, extracts candidate regions, retrieves normal references for those regions, and computes uncertainty features: raw anomaly score, score margin to threshold, heatmap entropy, region compactness, region size, top-k retrieval consistency, cross-model disagreement, and report-evidence mismatch. A constrained report generator may only fill fields from a fixed schema. A verifier then checks whether each field is supported by a selected region and retrieved references. The final policy outputs one of three actions: accept as defect with grounded report, reject as normal with confidence, or escalate with an explicit failure_warning and missing-evidence reason.

Motivation or baseline weakness:
Strong IAD baselines can rank anomalous images but often do not know when their heatmaps are unreliable, when a generated defect description is unsupported, or when a human inspector should review the case. This causes overconfident false alarms from lighting or texture changes and ungrounded report fields such as defect type, affected region, severity, and recommended action.

Mechanism or approach:
A selective calibration and escalation policy trained on lightweight validation data, plus a structured report verifier that maps anomaly_score, anomaly_mask_or_region, defect_type, evidence, normal_reference_used, confidence, recommended_action, and failure_warning to explicit visual evidence and rejects unsupported fields.
Minimize selective risk at a fixed target anomaly recall and capped escalation rate. Train a calibration model on validation uncertainty features to estimate P(correct automatic decision | features). Accept automatic decisions only when calibrated confidence exceeds class-specific thresholds; otherwise escalate. Report fields are optimized separately by minimizing unsupported-claim rate subject to preserving required operational fields for accepted defect cases.

Experiment and implementation plan:
PatchCore; FastFlow; RD4AD; WinCLIP; AnomalyCLIP; Qwen-VL or LLaVA report generation without verification; fixed-threshold IAD classifier; uncertainty by raw anomaly score margin only
MVTec_AD and VisA for primary evaluation; MVTec_LOCO for logical anomaly stress testing; optional BTAD or MPDD for transfer validation; validation split with image-level labels and limited pixel masks for calibration; normal-only validation subset for false-alarm calibration; small human-audit subset or simulated audit labels from ground truth for escalation precision evaluation
run_iad_and_vlm_tools.py for baseline anomaly scores, heatmaps, candidate regions, and constrained candidate reports; extract_uncertainty_features.py for score margin, heatmap entropy, compactness, region size, retrieval consistency, disagreement, and report-evidence mismatch; calibrate_selective_policy.py for temperature scaling, isotonic calibration, or lightweight logistic calibration and abstention thresholds; verify_report_grounding.py for claim-region-reference checks; agent_selective_inspection.py for accept-reject-escalate workflow; evaluate_selective_iad.py for AUROC, F1, selective risk, calibration error, coverage, and escalation precision; evaluate_report_quality.py for report correctness, evidence grounding, unsupported claim rate, and recommended-action accuracy
image_level_auroc; pixel_level_auroc; aupr; pro_score; f1_score; mask_iou; defect_region_precision; defect_region_recall; calibration_error; selective_risk; coverage; escalation_rate; out_of_distribution_detection_auroc; human_escalation_precision; tool_success_rate; report_correctness; evidence_grounding_score; unsupported_claim_rate; false_alarm_reduction
remove retrieval-consistency uncertainty feature; remove cross-model disagreement feature; remove heatmap entropy and compactness features; remove report-grounding verifier; replace selective policy with fixed anomaly threshold; replace calibrated confidence with raw IAD score; allow free-form VLM defect descriptions instead of schema-constrained reports; train escalation thresholds on MVTec_AD and test transfer to VisA or MVTec_LOCO
non-agent IAD baseline with the same anomaly score and no abstention; VLM report generation from image and heatmap only, with no grounding verifier and no ability to refuse; random escalation at the same escalation rate; escalation by raw anomaly score uncertainty only; report checker using shuffled masks or shuffled normal references; normal images with benign lighting or color perturbations, where the agent should not increase defect acceptance solely because the report text is confident; schema-filled reports with deliberately unsupported defect_type or recommended_action fields, which the verifier should reject
At matched anomaly recall, reduce false alarms by at least 10% compared with the strongest fixed-threshold IAD baseline on MVTec_AD or VisA; Lower calibration_error by at least 15% compared with raw baseline anomaly scores; Achieve human_escalation_precision at least 10 percentage points above raw-score uncertainty escalation at the same escalation rate; Keep pixel-level AUROC or PRO within 2 percentage points of the best direct localization baseline while improving selective_risk; Report evidence_grounding_score must exceed 0.80 and unsupported_claim_rate must remain below 5% on audited accepted reports; Maintain coverage of at least 80% unless a lower-coverage operating point is explicitly reported on the risk-coverage curve; Failure if report or escalation metrics do not improve over non-agent baselines, even if AUROC is unchanged or slightly improved

Risks, controls, or fallback:
Risk: selective policies may over-abstain and appear better by avoiding difficult cases, and calibration learned on one category may not transfer to another. Fallback: report risk-coverage curves, cap escalation rates in the main comparison, evaluate category-held-out transfer, separately score automatic-pass, automatic-fail, and human-review decisions, and use conservative schema defaults when report evidence is incomplete.

### Candidate B

Idea 1
Title:
Reference-Consistency Agent for Shifted or Contaminated Normal Memory Banks

Core proposal:
Add an agentic retrieval-audit loop for memory-based industrial anomaly detection. The loop first runs a PatchCore or PaDiM heatmap tool, extracts suspicious connected regions, retrieves top-k normal reference patches from the same product category and comparable spatial neighborhood, computes whether the retrieved references are internally consistent and visually compatible with the test region, audits the normal bank for likely contamination using cross-reference anomaly scores, and escalates when the base anomaly score is high but the reference evidence is ambiguous. Agent steps: run IAD heatmap tool, retrieve normal references, audit retrieved references for contamination and category/position mismatch, verify suspicious regions with a second IAD or CLIP-style semantic anomaly tool, calibrate confidence, then emit a structured report linking each decision to test-region crops and reference patches.

Motivation or baseline weakness:
PatchCore and PaDiM depend on normal-reference feature memories or distribution estimates, so factory shift or contaminated normal reference images can make abnormal regions appear normal or shifted normal regions look defective. Patch-level heatmaps alone also do not verify whether a retrieved normal patch is a valid counterexample for the suspicious test region.

Mechanism or approach:
A lightweight Reference Consistency and Bank Audit module that stores retrieval state as {test_region_id, product_category, spatial_bin, top_k_reference_ids, patch_distances, reference_anomaly_scores, consistency_score, bank_disagreement_score, audit_flag} and outputs calibrated anomaly confidence plus accept, escalate, or refuse decisions.
Optimize selective anomaly prediction under reference shift by combining base anomaly score A(x), normal-reference consistency C(x,R), and contamination penalty B(R) into S = A(x) * (1 - C(x,R)) + lambda * B(R), where C is high only when same-category retrieved references are mutually consistent and visually compatible with the test region. Choose thresholds on held-out shifted-normal and contaminated-bank validation splits to reduce false alarms at matched recall and minimize calibration error relative to anomaly-score-only calibration.

Experiment and implementation plan:
PatchCore; PaDiM; RD4AD; PatchCore plus non-agent top-k retrieval report; PaDiM plus fixed anomaly threshold
MVTec_AD train-normal and test anomaly images; VisA train-normal and test anomaly images; Constructed shifted-normal split using category-specific brightness, texture, viewpoint, compression, or factory-batch augmentations applied only to normal test images; Constructed contaminated-memory split by injecting 1%, 5%, and 10% anomalous patches or images into the normal bank while keeping clean-bank metadata for evaluation; Pixel masks or bounding boxes where available for region-level verification and grounding evaluation
build_patch_memory_bank.py; inject_contaminated_references.py; simulate_normal_reference_shift.py; run_iad_heatmaps.py; retrieve_region_references.py; audit_reference_bank.py; calibrate_selective_policy.py; generate_structured_inspection_report.py; evaluate_detection_localization_agent_metrics.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; false_alarm_reduction; tool_success_rate; evidence_grounding_score; human_escalation_precision; calibration_error; selective_risk; out_of_distribution_detection
Remove reference-bank audit while keeping nearest-neighbor retrieval; Use random same-category normal references instead of nearest retrieved references; Use anomaly score only without retrieval consistency; Use single IAD model verification instead of cross-model disagreement; Vary contamination rate and shift severity independently; Replace calibrated selective policy with a fixed anomaly threshold; Disable category and spatial-bin constraints during reference retrieval
Generate the same report schema from the PatchCore or PaDiM heatmap only, without retrieval audit or verification; Shuffle retrieved references across product categories while keeping report generation enabled; Allow the agent to cite reference identifiers but hide reference patches from the verifier; Inject clean normal patches labeled as contaminated and require the audit module not to over-escalate them; Use shifted normal images with no injected defects and measure whether the agent reduces, rather than increases, false alarms
On MVTec_AD or VisA, maintain at least 95% of the strongest direct baseline image_level_auroc while improving false_alarm_reduction by at least 15% on shifted-normal splits; Improve pixel_level_auroc or pro_score by at least 2 points over PatchCore or PaDiM on contaminated-bank splits; Reduce calibration_error by at least 10% relative to anomaly-score-only calibration; Achieve evidence_grounding_score of at least 0.80 for reports that cite normal references; Human_escalation_precision must exceed the non-agent heatmap-plus-report baseline by at least 10%; otherwise the agentic component is considered failed

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W4404704036; openalex:W7154655652

Risks, controls, or fallback:
Risk: reference consistency may reject legitimate rare normal variants or fail under severe domain shift, and contaminated-bank labels may be hard to infer without ground truth. Fallback: use category-specific conformal calibration, treat high internal reference disagreement as an escalation condition rather than an automatic anomaly decision, and report 'insufficient normal-reference support' instead of forcing a defect label.

---

Idea 2
Title:
Disagreement-Guided Mask Selection Agent for Weakly Labeled Defect Localization

Core proposal:
Use a mask-selection agent that treats SAM or SAM2 masks as candidates rather than final defect predictions. The agent detects suspicious peaks from IAD heatmaps, prompts SAM or SAM2 with points, boxes, and local crops around those peaks, scores each candidate mask using heatmap coverage, CLIP-style anomaly prompt support, same-category normal-reference contrast, and cross-model disagreement, then rejects masks that also activate on normal negative-control images. Agent steps: detect suspicious heatmap peaks, generate candidate masks, retrieve same-category normal region neighbors for each candidate, compute evidence and disagreement terms, run normal negative-control scoring, calibrate mask confidence, and generate a region-grounded report only for accepted masks.

Motivation or baseline weakness:
SAM and SAM2 can segment salient object parts rather than true defect regions, while WinCLIP and AnomalyCLIP can provide semantic anomaly cues without precise masks. This creates a task-domain mismatch when generic promptable masks are used as defect masks under sparse or missing pixel-level labels.

Mechanism or approach:
A Mask Evidence Selection Policy that ranks candidate masks by E(mask) = heatmap_coverage + semantic_anomaly_support + reference_mismatch - normal_negative_control_activation - cross_model_disagreement - saliency_only_penalty, with a refusal threshold when evidence is insufficient or when the selected mask mostly covers normal object structure rather than a localized defect.
Maximize defect_region_precision at fixed defect_region_recall using weak supervision from image labels and a small calibration subset of sparse masks. The selected mask must be jointly supported by IAD heatmaps, VLM anomaly prompts, and retrieved normal-reference contrast, while masks that activate on normal negative controls or disagree strongly across tools are penalized. Full pixel masks are used for evaluation, not for training the main selection policy except in the declared calibration subset.

Experiment and implementation plan:
SAM; SAM2; PatchCore; RD4AD; WinCLIP; AnomalyCLIP; SAM2 refinement without mask selection policy; Heatmap thresholding without SAM or SAM2 refinement
MVTec_AD images with pixel masks reserved for evaluation and limited calibration only; VisA images with image-level labels and available sparse masks or pixel masks reserved for evaluation; Optional defect taxonomy for text prompts, restricted to dataset-supported product and defect labels; Normal reference images for negative-control mask scoring; Synthetic sparse-label setting using 5%, 10%, and 20% of available masks for calibration only
run_patchcore_rd4ad_heatmaps.py; generate_sam_candidate_masks.py; prompt_clip_anomaly_scores.py; retrieve_normal_region_neighbors.py; score_mask_evidence.py; run_normal_negative_controls.py; calibrate_mask_confidence.py; generate_region_grounded_report.py; evaluate_mask_and_agent_metrics.py
pixel_level_auroc; pro_score; mask_iou; defect_region_precision; defect_region_recall; aupr; f1_score; tool_success_rate; evidence_grounding_score; report_correctness; human_escalation_precision; calibration_error; selective_risk; false_alarm_reduction
Remove negative-control normal scoring; Remove cross-model disagreement term; Use SAM or SAM2 largest mask only; Use the mask with highest heatmap overlap only; Use CLIP-style semantic score only without IAD heatmap support; Use no normal-reference retrieval; Use all masks without calibrated refusal; Remove the saliency-only penalty for large object-part masks
Run SAM2 refinement on random heatmap peaks from normal images and require the policy to reject them; Use shuffled defect-type prompts unrelated to the product category; Replace retrieved normal references with same-image background patches; Prompt SAM or SAM2 with boxes covering normal salient object parts and require rejection unless anomaly evidence is present; Evaluate on normal images with synthetic prompt points but no defects and measure false positive mask rate
Improve mask_iou by at least 5 points over heatmap-thresholded PatchCore or RD4AD on MVTec_AD or VisA; Improve defect_region_precision by at least 10% at matched defect_region_recall relative to SAM2 without the selection policy; Keep false positive mask rate on normal negative controls below 5% at the selected operating point; Achieve evidence_grounding_score of at least 0.80 for accepted reports; If tool_success_rate or evidence_grounding_score does not exceed the non-agent SAM2-plus-report baseline, declare the agent component unsuccessful

Evidence paper IDs:
openalex:W4380551232; openalex:W7162893906; openalex:W7154655652; openalex:W4415239807; openalex:W7153328271

Risks, controls, or fallback:
Risk: cross-model agreement can reinforce the same texture, lighting, or object-saliency false positives, and sparse mask calibration can overfit to product categories. Fallback: require normal negative-control rejection, restrict prompts to dataset-supported product and defect terms, and use conservative escalation when semantic support, heatmap evidence, and reference mismatch disagree.

---

Idea 3
Title:
Evidence-Grounded Report Checker with Selective Human Escalation

Core proposal:
Introduce an evidence-grounded report checker that validates every report claim before release. The checker receives candidate anomaly regions from IAD tools, retrieved same-category normal references, a restricted defect taxonomy when available, and cross-model heatmap or semantic agreement scores. It drafts or receives a structured inspection report, decomposes it into atomic claims, checks whether each claim is supported by a linked anomaly region and a normal-reference contrast, and then accepts, revises unsupported claims to a weaker evidence-supported form, or escalates/refuses. Agent steps: run IAD and VLM-style tools, retrieve normal references, draft a structured report, verify each claim-to-region/reference link, calibrate confidence, and apply selective escalation optimized for false-alarm reduction at matched anomaly recall.

Motivation or baseline weakness:
WinCLIP, AnomalyCLIP, and VLM-style inspection agents may generate plausible defect descriptions that are unsupported by localized visual evidence. This can produce misleading inspection reports and poor human escalation decisions even when image-level anomaly scores are reasonable.

Mechanism or approach:
A Claim-Region-Reference Verifier that parses the report schema into atomic claims {defect_type, location, visual_evidence, normal_reference_used, severity, recommended_action}, checks whether each claim has localized region support, normal-reference contrast, and taxonomy compatibility, and returns unsupported_claim_flags plus calibrated release, revise, or escalation decisions.
Minimize unsupported report claims and selective risk by optimizing a release policy over anomaly score, localization confidence, cross-model disagreement, and claim-verification score. The policy is constrained to maintain target anomaly recall, improve human_escalation_precision, and reduce false releases of reports whose defect type, location, or evidence link is contradicted by the available region evidence.

Experiment and implementation plan:
WinCLIP; AnomalyCLIP; PatchCore; Unverified VLM inspection report agent; IAD heatmap plus template report; Retrieval-augmented report generation without claim verification
MVTec_AD and VisA image-level and pixel-level anomaly data; Optional defect taxonomy converted into allowed report labels for each product category; Normal reference images for region-to-reference contrast; Human- or rule-constructed report correctness labels for a small validation subset; Automatically generated counterfactual reports with wrong defect type, wrong region, missing evidence, swapped normal references, or unsupported severity/action claims for checker training and evaluation
run_iad_and_vlm_baselines.py; retrieve_normal_references.py; draft_structured_reports.py; create_counterfactual_report_claims.py; verify_claim_region_reference_links.py; calibrate_escalation_policy.py; evaluate_report_correctness_grounding.py; evaluate_selective_detection.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; mask_iou; report_correctness; evidence_grounding_score; false_alarm_reduction; human_escalation_precision; tool_success_rate; calibration_error; selective_risk; defect_region_precision; defect_region_recall
Remove claim-region-reference verifier; Remove retrieved normal references from verification; Use VLM self-critique without access to anomaly masks or heatmaps; Use cross-model disagreement only without report checking; Use fixed confidence threshold instead of calibrated selective policy; Disable refusal and escalation and force a report for every sample; Allow free-form defect labels instead of the restricted taxonomy or unknown-anomaly fallback
Feed reports with deliberately swapped defect locations and require the checker to reject or revise them; Feed reports with correct anomaly score but unsupported defect type and require revision or escalation; Generate reports from normal images with no anomaly evidence and measure false release rate; Swap normal references across product categories and require the checker to flag unsupported reference contrast; Provide reports with correct region but exaggerated severity or unsupported recommended action and require claim-level rejection
Improve report_correctness by at least 15% over VLM-style report generation without evidence checking; Achieve evidence_grounding_score of at least 0.85 on accepted reports; Reduce false alarms by at least 10% at matched image-level recall compared with the strongest direct IAD baseline plus unverified report; Improve human_escalation_precision by at least 10% while keeping selective_risk no worse than the non-agent baseline; If evidence_grounding_score and tool_success_rate do not improve over the negative-control unverified agent, the idea fails

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W7154655652; openalex:W7153328271; openalex:W7138099583

Risks, controls, or fallback:
Risk: automatic report labels may be noisy, VLM descriptions may not match dataset taxonomies, and checker training on synthetic counterfactuals may miss real human-report errors. Fallback: restrict output to a small allowed defect taxonomy plus an 'unknown anomaly' class, prioritize region/reference evidence over free-form semantic naming, and escalate whenever defect type or recommended action is not directly supported by localized evidence.

---

## Item 19: HUM-531d656c59

类型：`single_idea`

### Candidate A

Title:
Reference-Consistency Agent for Shifted or Contaminated Normal Memory Banks

Core proposal:
Add a retrieval-audit agent around a frozen nearest-neighbor IAD pipeline. The workflow is: compute the baseline anomaly heatmap; convert high-score connected components into suspicious regions; retrieve top-k normal patches for each region from the memory bank; compute retrieval_consistency_score from the agreement among retrieved neighbors, their distance margin to the test region, and their own cross-neighbor normality; identify suspicious reference patches using leave-one-reference or leave-one-cluster influence on region scores; recompute the region anomaly score after excluding suspect references; compare pre- and post-audit score stability; emit a structured report linking each anomaly claim to the test region, trusted references, removed references if any, and an escalation decision. The agent escalates rather than suppresses a defect when the region remains anomalous but the trusted reference evidence is insufficient.

Motivation or baseline weakness:
PatchCore-style nearest-neighbor industrial anomaly detectors can become unstable when the normal memory bank is shifted across acquisition conditions or contains contaminated normal examples. Their heatmaps also do not indicate whether a high anomaly score was caused by trustworthy normal references, outlier reference patches, or reference-bank instability.

Mechanism or approach:
A lightweight reference-bank auditor over frozen PatchCore-style patch embeddings, optionally DINO or CLIP embeddings for cross-checking. It outputs per-reference contamination_likelihood, per-region retrieval_consistency_score, score_instability_after_reference_removal, and a rule-based agent state for verify, accept, refuse, or escalate.
For each region r, compute audited_score(r)=base_iad_score(r)+lambda_instability*score_instability(r)-lambda_trust*trusted_normal_support(r), where trusted_normal_support is estimated only from references with low contamination_likelihood. Calibrate a selective decision rule so that reports are emitted when audited confidence exceeds tau and otherwise escalated. Reference contamination_likelihood is estimated from nearest-neighbor graph outlierness, disagreement with local normal clusters, and influence on many test-region scores under leave-one-reference or leave-one-cluster removal.

Experiment and implementation plan:
PatchCore; PaDiM; FastFlow; RD4AD; WinCLIP
MVTec_AD train/test normal and anomaly images with masks; VisA train/test normal and anomaly images with masks; Synthetic contaminated memory banks created by injecting a controlled percentage of anomalous test patches, shifted normal images, or nuisance-perturbed normal images into the reference set; Factory-shift proxy splits by product category, lighting augmentation, camera perturbation, or acquisition-condition perturbation
build_patch_memory_bank.py; inject_reference_contamination.py; run_baseline_iad_heatmaps.py; retrieve_topk_normal_patches.py; audit_reference_bank.py; agent_verify_and_report.py; evaluate_detection_localization_agent.py; calibrate_selective_policy.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; f1_score; mask_iou; defect_region_precision; defect_region_recall; tool_success_rate; evidence_grounding_score; false_alarm_reduction; human_escalation_precision; calibration_error; selective_risk; out_of_distribution_detection
Remove reference-bank audit but keep nearest-neighbor retrieval; Use random normal references instead of top-k retrieved references; Use the base PatchCore heatmap without retrieval_consistency_score; Disable score-stability verification after suspect-reference removal; Replace calibrated escalation with a fixed anomaly-score threshold; Vary contamination rate and shift severity independently; Use only PatchCore embeddings versus adding DINO or CLIP embedding cross-checks
Non-agent PatchCore plus a templated report with no retrieval audit, no score-stability verification, and no escalation policy; Reference retrieval with shuffled region-reference links to test whether evidence grounding depends on the true retrieved patches; Clean normal-bank setting with no injected contamination to verify that the auditor does not invent contamination or degrade clean-data localization; Injected contamination labels hidden during calibration to prevent tuning directly on synthetic contamination identities
At matched anomaly recall, reduce false_alarm_rate by at least 10% over PatchCore on contaminated or shifted reference settings; Preserve pixel_level_auroc and pro_score within 1 point of PatchCore on clean MVTec_AD or VisA while improving contaminated-bank robustness; Achieve evidence_grounding_score of at least 0.75 for reports linking each defect claim to a region and trusted reference patches; Improve human_escalation_precision by at least 10% over fixed-threshold escalation; Failure if agent workflow metrics do not improve over the non-agent retrieval baseline or if localization drops by more than 2 points on clean data

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W4404704036

Risks, controls, or fallback:
Risk: synthetic contamination and proxy shifts may not represent real factory drift. Fallback: report sensitivity curves across multiple contamination types and shift severities, separate clean-bank and contaminated-bank results, and restrict claims to reference-bank robustness rather than broad domain adaptation.

### Candidate B

Title:
Reference-Consistency Agent for Shifted or Contaminated Normal Memory Banks

Core proposal:
Add an agentic retrieval-audit loop that retrieves top-k normal patches for each suspicious test region, estimates a retrieval_consistency_score between the test region and normal references, audits the normal bank for contaminated exemplars using cross-neighbor outlierness, and refuses or escalates when anomaly evidence depends on low-consistency or suspicious references. The workflow is: run IAD heatmap, propose regions, retrieve normal patches, audit retrieved references, recompute region score after removing suspect references, verify score stability, generate a structured report with linked test region and reference patches, and escalate if the calibrated confidence is low or reference contamination is likely.

Motivation or baseline weakness:
PatchCore and related nearest-neighbor IAD methods can produce unstable heatmaps when the normal reference bank shifts across factories or contains contaminated normal images, and the baseline heatmap alone cannot explain whether the evidence came from trustworthy normal references.

Mechanism or approach:
A lightweight reference-bank auditor that computes per-reference contamination likelihood and per-region retrieval_consistency_score from frozen PatchCore or DINO/CLIP patch embeddings, plus a rule-based agent state machine for retrieval, verification, report generation, and escalation.
Optimize anomaly_score = base_iad_score * (1 - normal_similarity_to_trusted_refs) + lambda * reference_instability, with selective prediction calibrated to reduce false alarms at matched recall; flag references whose leave-one-bank-out removal changes many region scores or whose nearest-neighbor graph has high outlierness.

Experiment and implementation plan:
PatchCore; PaDiM; FastFlow; RD4AD; WinCLIP
MVTec_AD train/test normal and anomaly images with masks; VisA train/test normal and anomaly images with masks; synthetic contaminated memory banks created by injecting a small percentage of anomalous test patches or shifted normal images into the reference set; optional factory-shift proxy splits by product category, lighting augmentation, or acquisition-condition perturbation
build_patch_memory_bank.py; inject_reference_contamination.py; run_baseline_iad_heatmaps.py; retrieve_topk_normal_patches.py; audit_reference_bank.py; agent_verify_and_report.py; evaluate_detection_localization_agent.py; calibrate_selective_policy.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; f1_score; mask_iou; defect_region_precision; defect_region_recall; tool_success_rate; evidence_grounding_score; false_alarm_reduction; human_escalation_precision; calibration_error; selective_risk; out_of_distribution_detection
remove reference-bank audit but keep retrieval; use random normal references instead of nearest retrieved references; use base PatchCore heatmap without retrieval consistency; disable score-stability verification after suspect reference removal; replace calibrated escalation with a fixed anomaly threshold; vary contamination rate and factory-shift severity
Non-agent PatchCore plus a templated VLM-style report without retrieval audit, verification loop, or escalation policy; Reference retrieval with shuffled region-reference links to test whether evidence grounding is genuine
At matched anomaly recall, reduce false_alarm_rate by at least 10% over PatchCore on contaminated or shifted reference settings; Improve or preserve pixel_level_auroc and pro_score within 1 point of PatchCore on clean MVTec_AD or VisA while improving contaminated-bank robustness; Achieve evidence_grounding_score at least 0.75 for reports linking each defect claim to a region and trusted reference patches; Human_escalation_precision improves over fixed-threshold escalation by at least 10%; Failure if agent workflow metrics do not improve over the non-agent baseline or if localization drops by more than 2 points on clean data

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W4404704036

Risks, controls, or fallback:
Risk: synthetic contamination or shift may not reflect real factory drift. Fallback: evaluate multiple proxy shifts, report sensitivity curves, and restrict claims to reference-bank robustness rather than broad domain adaptation.

---

## Item 20: HUM-f2a6b4d4f7

类型：`portfolio`

### Candidate A

Idea 1
Title:
Reference-Consistency Agent for Shifted or Contaminated Normal Memory Banks

Core proposal:
Add a retrieval-audit agent around a frozen nearest-neighbor IAD pipeline. The workflow is: compute the baseline anomaly heatmap; convert high-score connected components into suspicious regions; retrieve top-k normal patches for each region from the memory bank; compute retrieval_consistency_score from the agreement among retrieved neighbors, their distance margin to the test region, and their own cross-neighbor normality; identify suspicious reference patches using leave-one-reference or leave-one-cluster influence on region scores; recompute the region anomaly score after excluding suspect references; compare pre- and post-audit score stability; emit a structured report linking each anomaly claim to the test region, trusted references, removed references if any, and an escalation decision. The agent escalates rather than suppresses a defect when the region remains anomalous but the trusted reference evidence is insufficient.

Motivation or baseline weakness:
PatchCore-style nearest-neighbor industrial anomaly detectors can become unstable when the normal memory bank is shifted across acquisition conditions or contains contaminated normal examples. Their heatmaps also do not indicate whether a high anomaly score was caused by trustworthy normal references, outlier reference patches, or reference-bank instability.

Mechanism or approach:
A lightweight reference-bank auditor over frozen PatchCore-style patch embeddings, optionally DINO or CLIP embeddings for cross-checking. It outputs per-reference contamination_likelihood, per-region retrieval_consistency_score, score_instability_after_reference_removal, and a rule-based agent state for verify, accept, refuse, or escalate.
For each region r, compute audited_score(r)=base_iad_score(r)+lambda_instability*score_instability(r)-lambda_trust*trusted_normal_support(r), where trusted_normal_support is estimated only from references with low contamination_likelihood. Calibrate a selective decision rule so that reports are emitted when audited confidence exceeds tau and otherwise escalated. Reference contamination_likelihood is estimated from nearest-neighbor graph outlierness, disagreement with local normal clusters, and influence on many test-region scores under leave-one-reference or leave-one-cluster removal.

Experiment and implementation plan:
PatchCore; PaDiM; FastFlow; RD4AD; WinCLIP
MVTec_AD train/test normal and anomaly images with masks; VisA train/test normal and anomaly images with masks; Synthetic contaminated memory banks created by injecting a controlled percentage of anomalous test patches, shifted normal images, or nuisance-perturbed normal images into the reference set; Factory-shift proxy splits by product category, lighting augmentation, camera perturbation, or acquisition-condition perturbation
build_patch_memory_bank.py; inject_reference_contamination.py; run_baseline_iad_heatmaps.py; retrieve_topk_normal_patches.py; audit_reference_bank.py; agent_verify_and_report.py; evaluate_detection_localization_agent.py; calibrate_selective_policy.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; f1_score; mask_iou; defect_region_precision; defect_region_recall; tool_success_rate; evidence_grounding_score; false_alarm_reduction; human_escalation_precision; calibration_error; selective_risk; out_of_distribution_detection
Remove reference-bank audit but keep nearest-neighbor retrieval; Use random normal references instead of top-k retrieved references; Use the base PatchCore heatmap without retrieval_consistency_score; Disable score-stability verification after suspect-reference removal; Replace calibrated escalation with a fixed anomaly-score threshold; Vary contamination rate and shift severity independently; Use only PatchCore embeddings versus adding DINO or CLIP embedding cross-checks
Non-agent PatchCore plus a templated report with no retrieval audit, no score-stability verification, and no escalation policy; Reference retrieval with shuffled region-reference links to test whether evidence grounding depends on the true retrieved patches; Clean normal-bank setting with no injected contamination to verify that the auditor does not invent contamination or degrade clean-data localization; Injected contamination labels hidden during calibration to prevent tuning directly on synthetic contamination identities
At matched anomaly recall, reduce false_alarm_rate by at least 10% over PatchCore on contaminated or shifted reference settings; Preserve pixel_level_auroc and pro_score within 1 point of PatchCore on clean MVTec_AD or VisA while improving contaminated-bank robustness; Achieve evidence_grounding_score of at least 0.75 for reports linking each defect claim to a region and trusted reference patches; Improve human_escalation_precision by at least 10% over fixed-threshold escalation; Failure if agent workflow metrics do not improve over the non-agent retrieval baseline or if localization drops by more than 2 points on clean data

Evidence paper IDs:
openalex:W7162893906; openalex:W4415239807; openalex:W4404704036

Risks, controls, or fallback:
Risk: synthetic contamination and proxy shifts may not represent real factory drift. Fallback: report sensitivity curves across multiple contamination types and shift severities, separate clean-bank and contaminated-bank results, and restrict claims to reference-bank robustness rather than broad domain adaptation.

---

Idea 2
Title:
Disagreement-Gated Mask Agent for Suppressing Texture and Lighting False Positives

Core proposal:
Create a mask-verification agent that treats each candidate mask as a hypothesis. The workflow is: run multiple frozen detectors; convert detector heatmaps into candidate boxes and points; prompt SAM or SAM2 to generate candidate masks; score each mask using heatmap support, normal-reference inconsistency, CLIP or AnomalyCLIP semantic defect compatibility, prompt stability, and similarity to nuisance negative controls; use cross-model disagreement as uncertainty rather than direct evidence of a defect; reject or abstain on masks dominated by lighting, shadow, blur, specular highlight, or texture-preserving color perturbation signatures; emit a localized defect report only when the accepted mask is supported by localized anomaly evidence and stable enough under detector and prompt perturbations.

Motivation or baseline weakness:
IAD heatmaps from PatchCore, PaDiM, FastFlow, or CLIP-based zero-shot detectors can confuse texture, reflections, shadows, and illumination changes with physical defects. SAM and SAM2 can refine candidate masks, but promptable segmentation can select salient non-defect regions unless mask selection is constrained by defect evidence and nuisance negative controls.

Mechanism or approach:
A frozen-model mask selection and rejection policy that ranks SAM or SAM2 masks using heatmap_support, reference_inconsistency, semantic_defect_support, nuisance_similarity, and model_disagreement_uncertainty. The module requires no detector fine-tuning and only calibrates thresholds or a shallow scoring function on validation normals and held-out labeled masks when available.
Select mask m maximizing S(m)=alpha*heatmap_support(m)+beta*reference_inconsistency(m)+gamma*semantic_defect_support(m)-delta*nuisance_similarity(m)-eta*model_disagreement_uncertainty(m)-rho*prompt_instability(m). Accept the highest-scoring mask only if calibrated confidence exceeds tau; otherwise escalate. Cross-model disagreement increases uncertainty unless the disagreement is resolved by high localized support, low nuisance similarity, and stable SAM/SAM2 prompts.

Experiment and implementation plan:
PatchCore; PaDiM; FastFlow; WinCLIP; AnomalyCLIP; SAM; SAM2
MVTec_AD images and pixel masks; VisA images and pixel masks; Normal-reference images from train splits; Nuisance negative controls generated from normal images using brightness, contrast, shadow, blur, specular highlight, compression, and texture-preserving color perturbations; Optional sparse-mask setting using image labels for calibration and held-out masks only for final evaluation
run_multi_detector_heatmaps.py; generate_sam_candidate_masks.py; make_lighting_texture_negative_controls.py; score_mask_hypotheses.py; calibrate_abstention_policy.py; agent_region_verification.py; generate_structured_region_report.py; evaluate_mask_and_agent_metrics.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; f1_score; tool_success_rate; evidence_grounding_score; false_alarm_reduction; report_correctness; human_escalation_precision; calibration_error; selective_risk
Remove SAM/SAM2 mask selection and use thresholded heatmap masks; Use SAM/SAM2 refinement without nuisance-negative-control rejection; Remove model_disagreement_uncertainty from the mask score; Remove normal-reference inconsistency from the mask score; Remove semantic defect compatibility from WinCLIP or AnomalyCLIP; Remove prompt-stability scoring across SAM/SAM2 prompts; Replace calibrated abstention with always-report behavior
SAM/SAM2 prompted by heatmap boxes but selecting the largest or highest-confidence SAM mask without the proposed policy; Agent report generated from accepted masks after randomizing mask-to-evidence links; Nuisance-only normal images treated as test anomalies to measure false-positive suppression; Random boxes or points used as SAM/SAM2 prompts to estimate how much improvement comes from promptable segmentation alone; Detector-score-only mask acceptance without nuisance controls or prompt-stability checks
Improve defect_region_precision by at least 10% at matched defect_region_recall versus thresholded PatchCore or PaDiM heatmaps; Reduce false positives on nuisance negative controls by at least 15% versus SAM/SAM2 heatmap refinement without the selection policy; Maintain pixel_level_auroc and pro_score within 1 point of the strongest frozen IAD baseline on MVTec_AD or VisA; Achieve tool_success_rate of at least 0.9 for detector, retrieval, SAM/SAM2, calibration, and report tools; Failure if SAM/SAM2 refinement improves mask_iou but evidence_grounding_score or false_alarm_reduction does not improve over the non-agent mask-refinement baseline

Evidence paper IDs:
openalex:W4380551232; openalex:W7162893906; openalex:W4415239807; openalex:W7154655652

Risks, controls, or fallback:
Risk: high model disagreement may occur on subtle true defects, causing excessive abstention. Fallback: treat disagreement as an escalation signal rather than a rejection signal, calibrate thresholds primarily on validation normals and nuisance controls, and report coverage-risk curves so gains are not hidden by over-abstention.

---

Idea 3
Title:
Evidence-Grounded Report Checker with Selective Human Escalation

Core proposal:
Add a report-checking agent that requires every defect_type, evidence sentence, severity statement, and recommended_action to be linked to a specific anomaly region, detector score, and retrieved normal reference. The workflow is: run a frozen IAD detector or zero-shot anomaly model; generate suspicious regions from heatmaps or detector outputs; retrieve normal references for each region; optionally refine boundaries using a segmentation proposal tool; draft a schema-constrained report; parse the report into atomic claims; verify each claim against region masks, anomaly scores, normal-reference contrasts, and an allowed defect taxonomy; compute calibrated report confidence from detector confidence, retrieval consistency, region quality, and checker pass rate; allow one revision for unsupported claims; then emit the report, refuse unsupported semantic descriptions, or escalate to human review.

Motivation or baseline weakness:
WinCLIP, AnomalyCLIP, and VLM-style IAD agents can produce semantic defect descriptions that are not grounded in localized visual evidence. Classical IAD models provide anomaly scores or masks but do not produce verified structured reports or principled human-review triggers.

Mechanism or approach:
A claim-to-evidence verifier that parses structured reports into atomic claims and validates required links to region identifiers, masks, anomaly scores, retrieved normal references, and allowed defect taxonomy entries. It uses frozen CLIP/VLM embeddings only for semantic compatibility checks and deterministic schema checks for grounding, missing links, confidence fields, and unsupported recommended actions.
Maximize report_correctness and evidence_grounding_score under a selective-risk constraint. Emit a report only if calibrated confidence q(report|regions,references,checker_pass_rate) exceeds tau; otherwise escalate. Penalize unsupported defect labels, missing region links, missing normal-reference comparisons, claims outside the defect taxonomy, and recommended actions that are not justified by the verified region evidence.

Experiment and implementation plan:
WinCLIP; AnomalyCLIP; PatchCore; RD4AD; SAM; GroundingDINO
MVTec_AD or VisA images with image labels and pixel masks; Optional defect taxonomy mapped from dataset defect names; Normal reference images from training splits; Small human- or rule-created report templates with required fields: anomaly_score, anomaly_mask_or_region, defect_type, evidence, normal_reference_used, confidence, recommended_action, and failure_warning; Optional sparse labels to simulate weak pixel supervision
run_iad_and_region_proposals.py; retrieve_region_references.py; draft_structured_report.py; check_report_claim_grounding.py; revise_or_refuse_report.py; calibrate_report_confidence.py; simulate_human_escalation.py; evaluate_reports_and_localization.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; report_correctness; evidence_grounding_score; tool_success_rate; false_alarm_reduction; human_escalation_precision; calibration_error; selective_risk
Remove evidence-grounded report checker; Allow one-shot VLM report without region-reference links; Remove retrieval of normal references; Remove calibrated refusal and always generate a report; Remove defect taxonomy constraint; Use masks from IAD heatmaps only versus SAM-assisted region proposals with the same checker; Disable the one-revision step and compare direct refusal against revision-then-refusal
PatchCore or WinCLIP plus a templated report that copies the top anomaly score but does not verify claims; Report checker run with randomized normal references and randomized region identifiers; Human escalation triggered by anomaly_score threshold alone rather than calibrated report confidence; Reports with deliberately injected unsupported defect labels or swapped defect regions to test checker sensitivity; Normal images with no defect region where the system must either report normality or refuse defect descriptions
Improve evidence_grounding_score by at least 20% over one-shot report generation at comparable report coverage; Maintain image_level_auroc and pixel_level_auroc within 1 point of the underlying IAD baseline because reporting should not degrade detection; Reduce unsupported defect descriptions by at least 30% relative to WinCLIP or AnomalyCLIP report prompts; Improve human_escalation_precision by at least 10% over anomaly-score-only escalation; Failure if report_correctness or evidence_grounding_score does not improve over the non-agent report baseline, even if detection metrics are unchanged

Evidence paper IDs:
openalex:W7162893906; openalex:W7154655652; openalex:W7153328271; openalex:W7138099583

Risks, controls, or fallback:
Risk: automatic report-correctness evaluation can be noisy and may reward overly conservative reports. Fallback: report factual grounding separately from usefulness, include refusal-rate and coverage-risk curves, and audit a small stratified human-evaluation set for report correctness, usefulness, and escalation quality.

### Candidate B

Idea 1
Title:
Reference-Bank Audit Agent for Contaminated and Shifted Normal Memory in Industrial Anomaly Detection

Core proposal:
An audit agent runs before final anomaly scoring. For each product category, it builds a graph over normal-reference patch embeddings, estimates local density and neighbor agreement, and marks reference patches or images as suspicious when they are isolated, inconsistent with nearby references, or repeatedly selected as nearest neighbors for known high-anomaly regions. At test time, the agent scores the image twice: once with the raw memory bank and once with an audited memory bank that downweights suspicious references. It reports the raw score, audited score, changed nearest references, and whether the decision is stable, escalated, or accepted.

Motivation or baseline weakness:
PatchCore, PaDiM, and RD4AD rely on a normal reference memory bank that is assumed to be clean and distribution-matched. In factory transfer or incremental deployment, contaminated references or benign domain shifts can suppress true defects, inflate false positives, or make nearest-neighbor explanations misleading.

Mechanism or approach:
A reference-bank audit module that stores per-reference reliability weights, computes patch-level neighbor consistency, applies soft downweighting rather than automatic deletion by default, reruns the baseline IAD scorer with audited weights, and records which references influenced the final decision.
For each test image x and reference bank B, learn or tune reliability weights w_i in [0,1] for reference entries b_i. The final score is S(x)=S_IAD(x;B,w)+lambda*D_raw_audited(x)+mu*R_test_ref(x), where D_raw_audited measures prediction instability between raw and audited banks and R_test_ref measures inconsistency between anomalous test patches and their nearest reliable references. Optimize validation false-alarm rate at fixed defect recall, with escalation when raw and audited decisions disagree beyond a calibrated threshold.

Experiment and implementation plan:
PatchCore; PaDiM; RD4AD; FastFlow; non-agent PatchCore with full unfiltered memory bank; retrieval-only nearest-neighbor scoring without audit; random reference downweighting with the same downweight budget
MVTec_AD train normals and test anomalies; VisA train normals and test anomalies; synthetic contaminated memory banks created by injecting a controlled percentage of anomalous images or shifted normal images into the normal reference set; product_category metadata; optional defect masks for pixel-level evaluation; held-out clean normal validation images for calibration
build_reference_memory_bank.py; inject_contamination_and_shift.py; run_iad_baselines.py; reference_bank_audit_agent.py; rerun_iad_with_audited_memory.py; calibrate_selective_thresholds.py; generate_structured_report.py; evaluate_detection_localization_agent_metrics.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; f1_score; mask_iou; defect_region_precision; defect_region_recall; calibration_error; selective_risk; false_alarm_reduction; audit_stability_gap; reference_quarantine_precision; human_escalation_precision; report_correctness
remove reference-bank audit but keep retrieval; use raw PatchCore memory without downweighting or quarantine; replace neighbor-consistency weights with random reference weights; use hard removal instead of soft downweighting; disable rescoring after auditing references; disable confidence calibration; vary contamination rates from 0% to 20%; evaluate shift by calibrating on one normal subset and testing on another controlled texture or lighting subset
agent produces a report from the baseline heatmap without changing retrieval weights or memory state; audit module randomly downweights the same number of reference patches as the proposed method; retrieval uses references from the wrong product category; inject clean duplicate normal images instead of anomalous or shifted references to verify that the audit does not remove valid repeated modes; shuffle reliability weights across product categories before rescoring
At matched defect recall, reduce false alarms by at least 10% relative to non-agent PatchCore on contaminated or shifted reference settings; Maintain image_level_auroc within 1 point of the strongest raw-memory baseline on clean memory banks; Improve pixel_level_auroc or pro_score over raw-memory PatchCore under contamination; Reference downweighting should outperform random downweighting at the same downweight budget; Human_escalation_precision should exceed a non-agent uncertainty threshold baseline when raw and audited predictions disagree; Failure if clean-bank performance drops substantially or if improvements disappear against the random-downweighting negative control

Risks, controls, or fallback:
Risk: synthetic contamination may not reflect real factory drift. Fallback: report separate sensitivity curves for contamination, lighting shift, texture shift, and clean-bank settings rather than claiming deployment robustness. Risk: aggressive quarantine may remove rare but valid normal modes. Fallback: use soft downweighting as the default, retain the raw-bank score for comparison, and escalate high-disagreement cases instead of making automatic reject decisions.

---

Idea 2
Title:
Disagreement-Guided Mask Selection Agent for Weakly Labeled Defect Localization

Core proposal:
An inspection agent converts IAD heatmaps into candidate prompts, generates candidate masks with SAM or SAM2, and also includes non-SAM candidates from heatmap thresholding for small or texture-like defects. Each candidate mask is scored using heatmap support, contrast against retrieved normal references from the same product category, boundary agreement with high-anomaly pixels, and comparison to nearby negative-control regions. The agent selects a final mask only if the candidate is both anomalous relative to normal references and spatially supported by the IAD heatmap; otherwise it abstains or returns an image-level defect decision without a precise mask.

Motivation or baseline weakness:
IAD heatmaps from FastFlow, DRAEM, RD4AD, and CLIP-based methods often localize defects coarsely, while SAM or SAM2 can oversegment texture, highlights, shadows, or background if used as a blind refinement step. When only image-level labels or sparse annotations are available, selecting the correct candidate mask is underconstrained.

Mechanism or approach:
A mask verification policy that ranks candidate masks using heatmap overlap, normal-reference contrast, candidate compactness and boundary plausibility, local negative-control activation, and optional taxonomy-constrained text labels. The module outputs the selected mask, a confidence score, and a structured reason for selection or abstention.
Select m* from candidate masks M by maximizing Q(m)=alpha*H(m)+beta*N(m)+delta*B(m)-eta*C_neg(m)-rho*A_bad(m), where H is heatmap support, N is normal-reference inconsistency inside the mask, B is boundary alignment with anomaly gradients, C_neg is activation on nearby normal-looking control regions, and A_bad penalizes implausible area or background coverage. Abstain if max_m Q(m) is below a calibrated threshold or if top candidates disagree strongly.

Experiment and implementation plan:
FastFlow; DRAEM; RD4AD; WinCLIP; AnomalyCLIP; SAM; SAM2; heatmap thresholding without SAM; SAM refinement without mask selection policy; largest SAM mask from high-heatmap prompts; SAM confidence-only selection
MVTec_AD images with available masks; VisA images with available masks; optional sparse bounding boxes or image-level labels to simulate weak labels; normal reference images from the same product category; optional defect taxonomy for constrained report labels; held-out validation split for threshold calibration
run_iad_heatmap_generators.py; generate_sam_candidate_masks.py; generate_heatmap_threshold_candidates.py; retrieve_normal_patches_for_regions.py; mask_selection_agent.py; negative_control_region_sampler.py; calibrate_mask_selection_thresholds.py; structured_region_report_checker.py; evaluate_mask_and_report_metrics.py
pixel_level_auroc; aupr; pro_score; mask_iou; defect_region_precision; defect_region_recall; f1_score; image_level_auroc; calibration_error; selective_risk; abstention_rate; false_alarm_reduction; report_correctness; region_reference_grounding_score
remove retrieval inconsistency from mask ranking; remove negative-control region comparison; use SAM/SAM2 largest mask only; use SAM/SAM2 confidence only; use heatmap thresholding only; disable boundary alignment term; disable abstention and force every anomalous image to produce a defect mask; train thresholds with full masks versus only image-level labels
run SAM/SAM2 on random points sampled outside high-IAD regions; use retrieved references from mismatched product categories; replace mask selection score with mask area alone; replace mask selection score with SAM confidence alone; shuffle heatmaps across images before prompting SAM/SAM2; generate defect descriptions without requiring a selected region and same-category normal reference
Improve mask_iou or pro_score over heatmap thresholding and SAM-only refinement on MVTec_AD or VisA; Reduce defect_region false positives by at least 10% at matched defect_region_recall; Maintain image_level_auroc within 1 point of the strongest direct IAD baseline when mask selection is added; Outperform area-only, SAM-confidence-only, and random-prompt negative controls; Escalate or abstain on at least 70% of deliberately unsupported masks while keeping selective_risk below the forced-decision variant; Failure if masks look visually smoother but do not improve localization metrics or if gains vanish when same-category retrieval is enforced

Risks, controls, or fallback:
Risk: SAM/SAM2 candidate masks may not align with small scratches, faint stains, or subtle texture defects. Fallback: keep heatmap-threshold and connected-component candidates in the candidate pool and allow the policy to select non-SAM masks. Risk: taxonomy-constrained text checks may still overfit superficial visual cues. Fallback: make text labels optional for mask selection and require the quantitative region-reference checks to determine the mask.

---

Idea 3
Title:
Selective Report-and-Escalation Agent for Calibrated Industrial Anomaly Decisions

Core proposal:
A selective inspection agent runs a small set of frozen IAD tools, retrieves same-category normal references for the most suspicious regions, and verifies whether each proposed report claim is tied to a concrete anomaly region and a contrasting normal reference. The final policy chooses one of three actions: accept_normal when anomaly evidence is weak and calibrated confidence is high, flag_defect when region-level evidence and model agreement are sufficient, or escalate when scores, retrieved references, or report claims are inconsistent.

Motivation or baseline weakness:
Strong IAD models can assign high anomaly scores to benign texture, lighting, or viewpoint variation, and multimodal report generators can add unsupported defect descriptions. Standard pipelines often lack a calibrated policy for deciding when to accept normal, flag a defect, or escalate uncertain cases.

Mechanism or approach:
A selective decision and report-checking module that combines calibrated anomaly scores, cross-model disagreement, region-reference contrast, and claim-to-region validation. It does not change the underlying IAD models; it only controls decision, abstention, and structured reporting.
Choose action a in {accept_normal, flag_defect, escalate} by minimizing expected selective risk L(a,x)=false_accept_cost+false_alarm_cost+unsupported_report_cost+escalation_cost under constraints on minimum anomaly recall and maximum escalation rate. Calibrated confidence C is estimated from IAD scores, score margins, model disagreement, retrieval consistency, and report-grounding indicators on a held-out validation split.

Experiment and implementation plan:
PatchCore; FastFlow; RD4AD; WinCLIP; AnomalyCLIP; single-model anomaly-score thresholding; non-agent ensemble averaging; uncertainty thresholding on max anomaly score; VLM report from anomaly heatmap without verification; template report from baseline heatmap
MVTec_AD image-level labels and masks where available; VisA image-level labels and masks where available; optional defect taxonomy mapped to product categories; normal reference images for same-category retrieval; held-out validation split for confidence calibration; predefined escalation targets based on low confidence, model disagreement, or localization inconsistency
run_multi_iad_tools.py; retrieve_region_normal_evidence.py; calibrate_confidence_and_selective_policy.py; evidence_grounded_report_checker.py; define_escalation_targets.py; generate_final_inspection_report.py; evaluate_selective_agent.py
image_level_auroc; pixel_level_auroc; aupr; pro_score; f1_score; mask_iou; defect_region_precision; defect_region_recall; calibration_error; selective_risk; false_alarm_reduction; escalation_rate; human_escalation_precision; report_correctness; claim_region_grounding_score; unsupported_claim_rate
remove cross-model disagreement from confidence; remove evidence-grounded report checker; remove retrieval consistency and use scores only; force the agent to always decide without escalation; replace calibrated selective policy with a fixed anomaly-score threshold; use generated report without claim-to-region validation; evaluate with and without defect taxonomy constraints; limit the workflow to the two strongest tools versus all tools
generate reports after shuffling anomaly masks across images; retrieve normal references from a different product category; allow the report generator to name any defect type without taxonomy or visual evidence; use an agent wrapper that only formats baseline outputs but does not verify or calibrate decisions; shuffle report claims across images before report checking; replace calibrated confidence with a random confidence score matched for escalation rate
Reduce false alarms by at least 10% at matched image-level anomaly recall compared with the strongest single IAD baseline; Lower calibration_error and selective_risk compared with max-score uncertainty thresholding and non-agent ensemble averaging; Reduce unsupported_claim_rate compared with unverified generated reports; Improve human_escalation_precision over entropy or max-score uncertainty baselines at a matched escalation rate; Maintain localization performance within 1 point of the best included IAD heatmap baseline while improving selective decision and report metrics; Failure if report quality improves only linguistically but claim_region_grounding_score, unsupported_claim_rate, and selective_risk do not improve

Risks, controls, or fallback:
Risk: combining several frozen models may add compute and latency without better decisions. Fallback: select the two most complementary tools using validation disagreement and report the latency-accuracy tradeoff. Risk: escalation labels are simulated rather than collected from real inspectors. Fallback: frame escalation as selective prediction or abstention, define the escalation targets deterministically from uncertainty and disagreement, and avoid claiming measured human workflow gains without human data.

---
