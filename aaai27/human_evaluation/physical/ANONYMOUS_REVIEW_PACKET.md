# 物理属性预测：匿名科研 Idea A/B 评审包

评审者代码：`physical_property_expert`

条目数：20

请先完整阅读上一级目录的 `HUMAN_BLIND_REVIEW_INSTRUCTIONS_CN.md`。不要查看任何 private answer key，也不要使用大模型代评。

## Item 1: HUM-1dd69f586c

类型：`single_idea`

### Candidate A

Title:
Material-Conditioned Interval Property Lookup for Segmented Indoor Objects

Core proposal:
Add a lightweight mapper that converts localized top-k material predictions and object-category priors into interval-valued physical-property estimates rather than overconfident point predictions. For each detected object mask, the method combines calibrated material probabilities, object category, and normalized material-property tables to output median estimates, lower/upper intervals, confidence scores, source identifiers, and failure warnings when the material posterior is diffuse or the object is visually underdetermined.

Motivation or baseline weakness:
GroundingDINO with SAM/SAM2 can localize visible indoor objects, but the resulting masks do not by themselves support calibrated physical-property estimates. CLIP/OpenSurfaces/MINC-style material recognition can be ambiguous at the object level, and single RGB images often cannot determine exact density, stiffness, hardness, or friction, especially for painted, coated, or composite objects.

Mechanism or approach:
A frozen-backbone material posterior calibrator plus deterministic property-table aggregator. Temperature-scaled material logits from masked object crops are mapped to property intervals using normalized engineering material tables and ObjectFolder/ObjectFolder2.0 priors, requiring only small validation data for calibration rather than large-scale end-to-end training.
Optimize calibrated interval prediction by minimizing interval negative log likelihood and log-space absolute error for density and Young's modulus under available weak or proxy labels, while targeting nominal prediction-interval coverage for all reported physical properties.

Experiment and implementation plan:
GroundingDINO; SAM; SAM2; CLIP; OpenSurfaces; MINC; ObjectFolder; ObjectFolder2.0; engineering_material_property_tables
Indoor RGB images with object masks or boxes from ScanNet, Matterport3D, or OpenRooms; Object category labels aligned to detected masks; Material labels or proxy material labels from OpenSurfaces/MINC-style categories; Engineering material property tables with density, Young's modulus, Poisson's ratio, hardness, and friction coefficient ranges; ObjectFolder/ObjectFolder2.0 object-material-property metadata where available; Small validation subset with human-checked materials for calibration and failure-mode analysis
run_detection_segmentation.py to produce object_id, category, mask_or_box using GroundingDINO with SAM/SAM2; extract_masked_object_crops.py to create masked object crops and optional local context crops; predict_material_topk.py to obtain material posteriors from frozen CLIP/OpenSurfaces/MINC-style models; calibrate_material_posteriors.py to fit temperature scaling and reliability estimates on a validation split; build_property_table_index.py to normalize material names, units, and property ranges across table sources; aggregate_property_intervals.py to produce structured object-level physical-property JSON; evaluate_interval_properties.py to compute material metrics, property errors, coverage, calibration error, and selective risk
object_recall; mask_iou; material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Remove object-category priors and use only the material posterior; Use most-likely-material point estimates instead of interval aggregation; Use uncalibrated material logits instead of temperature-scaled probabilities; Use masked object crop only versus masked crop plus surrounding context; Replace engineering table intervals with ObjectFolder/ObjectFolder2.0-only priors; Use category-only priors without visual material predictions
Shuffle material labels across object crops before property lookup; Assign generic category-level property intervals without localized material evidence; Use whole-image material prediction instead of object-mask-localized prediction; Evaluate categories absent from the property table to verify failure_warning activation; Inject unit-mismatched property-table entries to test table normalization checks
Improve material_top3_accuracy over a frozen CLIP-only object-crop baseline by at least 5 percentage points; Reduce density_log_mae and youngs_modulus_log_mae by at least 10% relative to most-likely-material table lookup; Achieve prediction_interval_coverage within 5 percentage points of the nominal 90% interval target; Reduce selective_risk at 70% retained predictions relative to an uncalibrated material-posterior baseline; Failure if nominal 90% interval coverage falls below 75% or property errors do not improve over generic category priors

Evidence paper IDs:
openalex:W4402427278; openalex:W4402500749; openalex:W4411238954; openalex:W2798280964; openalex:W3012463097; openalex:W2895238724; openalex:W3200689778; openalex:W4312347618

Risks, controls, or fallback:
Risk: visible appearance may not reveal hidden composition, such as veneer, painted metal, foam-filled furniture, or layered composites. Fallback: widen intervals, emit low-observability failure warnings, and report category-level priors instead of unsupported precise values.

### Candidate B

Title:
Material-Conditioned Interval Property Lookup for Segmented Indoor Objects

Core proposal:
Add a lightweight material-to-property interval mapper that converts top-k localized material predictions and object category priors into interval-valued physical-property predictions rather than overconfident point estimates. For each object mask, the module fuses calibrated visual material probabilities with category-conditioned priors from curated material-property tables and ObjectFolder/ObjectFolder2.0 metadata where available. It emits median estimates, lower/upper intervals, confidence, source tags, and failure warnings when the material posterior is diffuse, the object category conflicts with the material hypothesis, or the lookup table lacks adequate support.

Motivation or baseline weakness:
GroundingDINO with SAM/SAM2 can localize visible objects, but the pipeline has no calibrated bridge from object-localized material cues to physical-property ranges. CLIP/OpenSurfaces/MINC-style material recognition can be prompt-sensitive or ambiguous, and single RGB images often cannot support exact density, modulus, hardness, or friction estimates for hidden or composite materials.

Mechanism or approach:
A frozen-backbone material posterior calibrator plus deterministic property-table aggregator: temperature-scaled material logits from masked object crops are mapped to normalized material names and then to property intervals using curated material-property tables and ObjectFolder/ObjectFolder2.0 priors, with no large-scale end-to-end training.
Minimize interval-aware negative log likelihood and log-space absolute error for density and Young's modulus under weak or proxy labels, while enforcing target prediction-interval coverage for all physical-property outputs through calibration on a held-out validation split.

Experiment and implementation plan:
GroundingDINO; SAM; SAM2; CLIP; OpenSurfaces; MINC; ObjectFolder; ObjectFolder2.0
Indoor images with object masks or boxes from an indoor-scene source such as ScanNet, Matterport3D, or OpenRooms; Material labels or proxy labels aligned to object crops using OpenSurfaces/MINC-style material categories; Object category labels aligned to detected masks; Curated material-property tables containing density, Young's modulus, Poisson's ratio, hardness, and friction coefficient ranges with normalized units; ObjectFolder/ObjectFolder2.0 object-material-property metadata where available; Held-out validation split for material-logit temperature scaling and interval calibration
run_detection_segmentation.py to produce object_id, category, mask_or_box using GroundingDINO plus SAM/SAM2; extract_masked_object_crops.py to create masked object crops and optional local context crops; predict_material_topk.py to obtain calibrated material posteriors from frozen CLIP/OpenSurfaces/MINC-style material models; build_property_table_index.py to normalize material names, aliases, property units, and source tags; aggregate_property_intervals.py to combine material posteriors, object-category priors, and table ranges into structured JSON predictions; evaluate_interval_properties.py to compute material metrics, property errors, interval coverage, calibration error, abstention rate, and selective risk
object_recall; mask_iou; material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Remove object-category prior and use material posterior only; Use point estimates from the most likely material instead of posterior-weighted interval aggregation; Use uncalibrated CLIP/OpenSurfaces/MINC logits instead of temperature-scaled material probabilities; Use mask crop only versus mask crop plus surrounding scene context; Replace curated table intervals with ObjectFolder/ObjectFolder2.0-only priors where metadata exists; Disable low-observability and table-missing failure warnings
Shuffle material labels across object crops before property lookup; Assign generic category-level property intervals without visual material evidence; Use whole-image material prediction instead of object-mask-localized prediction; Evaluate categories or materials absent from the property table to verify failure_warning activation; Randomize material-property table rows while preserving material label frequencies
Improve material_top3_accuracy over a frozen CLIP-only object-crop baseline by at least 5 percentage points after calibration; Reduce density_log_mae and youngs_modulus_log_mae by at least 10% relative to most-likely-material table lookup; Achieve prediction_interval_coverage within 5 percentage points of the nominal 90% interval target; Reduce selective_risk at 70% retained predictions relative to an uncalibrated material-posterior baseline; Failure if nominal 90% interval coverage is below 75% or property errors do not beat generic category priors

Evidence paper IDs:
openalex:W4402427278; openalex:W4402500749; openalex:W4411238954; openalex:W2798280964; openalex:W3012463097; openalex:W2895238724; openalex:W3200689778; openalex:W4312347618

Risks, controls, or fallback:
Risk: visible texture may not identify hidden composition, for example veneer, painted metal, foam-filled furniture, or composite objects. Fallback: widen intervals, mark low-observability or table-missing failure_warning fields, and report category-level priors rather than unsupported precise values.

---

## Item 2: HUM-c8a31f7adc

类型：`single_idea`

### Candidate A

Title:
Property-Interval Conformal Calibration for Single-Image Physical Estimates

Core proposal:
Wrap any frozen detection, segmentation, material-recognition, and property-estimation pipeline with split conformal calibration. The calibrator receives baseline point estimates or raw intervals and computes nonconformity scores on a calibration split with proxy or audited property intervals. Scores are conditioned by material family, object category, material confidence, visible texture strength, mask quality, and disagreement between property sources. At inference, the module outputs calibrated per-property intervals and an uncertainty tag, using broader fallback groups when a fine material/category group has insufficient calibration examples.

Motivation or baseline weakness:
Direct material-to-property lookup and VLM-generated numeric estimates can produce precise-looking point values even when the visible image supports only a material family or proxy label. This makes density, modulus, hardness, friction, and related estimates poorly calibrated, especially for hidden materials, rare materials, and object categories with large within-class variation.

Mechanism or approach:
A post-hoc grouped conformal interval calibrator that does not retrain the vision backbone and can wrap GroundingDINO/SAM2/Mask2Former-style masks, CLIP/MINC-style material recognizers, or VLM JSON predictors.
For each physical property, minimize interval width subject to empirical target coverage on a held-out calibration split. Use grouped conformal quantiles when group sample counts are sufficient, back off to material-family or global quantiles when sparse, and report unsupported-group warnings rather than extrapolating narrow intervals.

Experiment and implementation plan:
GroundingDINO + SAM2 + CLIP-style material prediction + material-property table point estimate; Mask2Former + MINC-style material classifier + uncalibrated material-property interval estimate; Qwen-VL direct property JSON prediction without residual-based conformal calibration
Calibration split with object masks or boxes, material labels or proxy material intervals, and audited examples where available; Physical-property ranges from ObjectFolder/ObjectFolder2.0-style physical-property sources and curated material-property tables; Indoor evaluation images with object-level detections or masks and material/category metadata sufficient for grouped calibration; A held-out test split separated by scene and object instance to avoid calibrating and testing on near-duplicate objects
collect_baseline_property_predictions.py; construct_proxy_interval_labels.py; fit_grouped_conformal_calibrator.py; apply_property_interval_calibration.py; evaluate_coverage_width_selective_risk.py
prediction_interval_coverage; calibration_error; selective_risk; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; material_top3_accuracy
Global conformal calibration without material or category grouping; Group only by material family; Group only by object category; Use VLM self-reported confidence instead of calibration residuals; Use uncalibrated source-table intervals; Disable sparse-group backoff and force fine-grained group quantiles
Calibrate on shuffled property labels while preserving material/category frequencies; Calibrate on one set of material families and test on held-out unrelated material families without fallback grouping; Use a constant-width interval for every property and object; Remove source-table disagreement features from the grouping and nonconformity model; Tune conformal quantiles on the test split to detect leakage-sensitive gains
Reach at least 90 percent empirical coverage for nominal 90 percent intervals on density and Young's modulus; Reduce calibration_error by at least 25 percent versus uncalibrated baseline intervals; Maintain median interval width no more than 1.5 times the strongest uncalibrated table-interval baseline at matched coverage; Improve selective_risk by at least 10 percent at 80 percent retained-object coverage; Maintain coverage within 7 percentage points of nominal for the largest material-family groups

Evidence paper IDs:
openalex:W4416850904; openalex:W4403323960; openalex:W4385327621; openalex:W4391722892; openalex:W4327630646; openalex:W4312347618

Risks, controls, or fallback:
Risk: proxy labels and material-property tables may be noisy, and conformal guarantees can degrade under distribution shift or sparse rare-material groups such as composites, coated metal, laminated wood, and foam. Fallback: back off from fine groups to broader material-family or global calibration, widen intervals using source-table disagreement, and set failure_warning when an object falls outside calibrated material/category support.

### Candidate B

Title:
Property-Interval Conformal Calibration for Single-Image Physical Estimates

Core proposal:
Convert all physical-property predictions into calibrated prediction intervals using split conformal calibration over proxy-labeled material/object groups. The module learns residual distributions conditioned on material confidence, object category, visible texture strength, and source table disagreement, then outputs per-property intervals and an uncertainty tag in the required JSON.

Motivation or baseline weakness:
A direct material-to-property lookup or VLM-generated numeric estimate produces point values that appear precise despite missing exact physical ground truth and hidden material composition. This makes density, modulus, hardness, and friction predictions poorly calibrated.

Mechanism or approach:
A post-hoc conformal interval calibrator that wraps any frozen detector, segmenter, material recognizer, and property table without retraining the vision backbone.
Given baseline point or interval estimates, produce the narrowest valid prediction intervals satisfying target empirical coverage for each physical property under grouped calibration by material family and object category.

Experiment and implementation plan:
GroundingDINO + SAM2 + CLIP + engineering table point estimate; Mask2Former + MINC + engineering table interval estimate; Qwen-VL direct property JSON prediction
Calibration split with material labels or interval proxy labels from OpenSurfaces, MINC, and manually audited indoor images; Physical-property ranges from ObjectFolder, ObjectFolder2.0, and engineering tables; Indoor evaluation images from ScanNet, Matterport3D, or OpenRooms with object-level masks/boxes
collect_baseline_property_predictions.py; construct_proxy_interval_labels.py; fit_grouped_conformal_calibrator.py; apply_property_interval_calibration.py; evaluate_coverage_width_selective_risk.py
prediction_interval_coverage; calibration_error; selective_risk; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; material_top3_accuracy
Global conformal calibration without grouping; Group only by material family; Group only by object category; Use VLM self-reported confidence instead of residual-based calibration; Use uncalibrated engineering-table intervals
Calibrate on shuffled property labels; Calibrate on unrelated material families and test on held-out indoor objects; Use a constant-width interval for every property and object; Remove source-table disagreement features
Reach at least 90 percent empirical coverage for nominal 90 percent intervals on density and Young's modulus; Reduce calibration_error by at least 25 percent versus uncalibrated baseline intervals; Maintain median interval width no more than 1.5 times the strongest uncalibrated table interval baseline; Improve selective_risk by at least 10 percent at 80 percent retained coverage

Evidence paper IDs:
openalex:W4416850904; openalex:W4403323960; openalex:W4385327621; openalex:W4391722892; openalex:W4327630646; openalex:W4312347618

Risks, controls, or fallback:
Risk: proxy labels may be noisy and calibration may not transfer to rare materials such as composites, laminated wood, coated metal, or foam. Fallback: use broader material-family calibration, report source-table disagreement as evidence, and trigger failure_warning when the test object falls outside calibrated material/category support.

---

## Item 3: HUM-dec8306816

类型：`single_idea`

### Candidate A

Title:
Conformal Property Calibration from Proxy Labels and Object Similarity

Core proposal:
Add a conformal calibration layer that operates on proxy labels and object-similarity groups: it converts material/property predictions into per-object prediction intervals with guaranteed empirical coverage on calibration splits stratified by object category, material ambiguity, and mask quality.

Motivation or baseline weakness:
A plug-and-play pipeline using GroundingDINO/SAM-style masks plus material lookup can output physical-property values, but exact ground truth is often unavailable and uncertainty is poorly calibrated, especially for visually ambiguous indoor objects.

Mechanism or approach:
A post-hoc conformal interval calibrator that consumes predicted material posterior, property-table distribution, mask quality score, object category, and scene-context embedding, then returns calibrated intervals and selective abstention thresholds.
Minimize interval width subject to validation-set coverage constraints for each physical property and stratified subgroup; optimize abstention thresholds to reduce selective risk under a target retained-object fraction.

Experiment and implementation plan:
GroundingDINO + SAM + material lookup with uncalibrated confidence; GroundingDINO + SAM2 + CLIP/OpenSurfaces property intervals without conformal correction; Mask2Former + MINC property lookup with global uncertainty
Indoor RGB images and object masks or boxes from ScanNet, Matterport3D, or OpenRooms; Material proxy labels from OpenSurfaces and MINC; Physical-property proxy intervals from ObjectFolder, ObjectFolder2.0, and engineering material-property tables; Calibration and test splits grouped by object category, material class, and mask quality
generate_baseline_property_predictions.py; estimate_mask_quality_features.py; fit_conformal_property_intervals.py; evaluate_calibration_by_subgroup.py; export_calibrated_object_json.py
prediction_interval_coverage; calibration_error; selective_risk; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; object_recall; mask_iou
Global conformal calibration instead of subgroup calibration; Remove mask quality features; Remove material posterior entropy; Use category-only calibration groups; Use fixed engineering-table ranges without learned residual calibration
Calibrate on randomly permuted property labels; Use calibration objects from disjoint categories without subgroup adjustment; Apply calibration scores from high-quality masks to low-quality masks; Replace material posterior entropy with random confidence
Achieve 90 percent nominal interval coverage within plus or minus 5 percentage points overall; Achieve subgroup coverage no lower than 80 percent for major material and object-category groups; Reduce calibration_error by at least 25 percent relative to uncalibrated lookup confidence; Reduce selective_risk by at least 15 percent at 70 percent retained objects without increasing median interval width by more than 20 percent

Evidence paper IDs:
openalex:W4402500749; openalex:W4416850904; openalex:W4403323960; openalex:W2798280964; openalex:W3200689778; openalex:W4312347618

Risks, controls, or fallback:
Risk: proxy labels and table-derived intervals may not reflect true object-specific properties, so conformal guarantees may only hold for the proxy target. Fallback: report the calibrated target explicitly as visible-material property interval, add failure_warning for hidden structure and coatings, and evaluate separate calibration curves for proxy labels versus any available measured ObjectFolder-style properties.

### Candidate B

Title:
Conformal Property Calibration from Proxy Labels and Object Similarity

Core proposal:
Add a post-hoc conformal calibration layer that operates on proxy labels and object-similarity groups. It converts material/property predictions into per-object prediction intervals with empirical coverage measured on held-out calibration splits stratified by object category, material ambiguity, and mask quality. The method explicitly claims coverage for the proxy visible-material target rather than for hidden true bulk composition.

Motivation or baseline weakness:
A plug-and-play pipeline using GroundingDINO/SAM-style masks plus material lookup can output physical-property values, but exact ground truth is often unavailable and uncertainty is poorly calibrated, especially for visually ambiguous indoor objects and low-quality masks.

Mechanism or approach:
A post-hoc conformal interval calibrator that consumes predicted material posterior, table-derived property distribution, mask quality score, object category, and scene-context embedding, then returns calibrated property intervals, confidence metadata, and abstention thresholds for unreliable objects.
Minimize calibrated interval width subject to validation-set coverage constraints for each physical property and for predefined subgroups. Fit nonconformity scores from residuals between predicted intervals and proxy labels, then tune abstention thresholds to reduce error among retained objects at a target retained-object fraction.

Experiment and implementation plan:
GroundingDINO + SAM + material lookup with uncalibrated confidence; GroundingDINO + SAM2 + CLIP/OpenSurfaces property intervals without conformal correction; Mask2Former + MINC property lookup with global uncertainty
Indoor RGB images and object masks or boxes produced by GroundingDINO, SAM, SAM2, or Mask2Former; Material proxy labels aligned to OpenSurfaces and MINC categories; Physical-property proxy intervals from ObjectFolder, ObjectFolder2.0, and normalized material-property tables; Calibration and test splits grouped by object category, material class, material posterior entropy, and mask quality; Optional measured ObjectFolder-style properties where category/object overlap permits separate evaluation from proxy table labels
generate_baseline_property_predictions.py; estimate_mask_quality_features.py; fit_conformal_property_intervals.py; evaluate_calibration_by_subgroup.py; export_calibrated_object_json.py
prediction_interval_coverage; calibration_error; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; object_recall; mask_iou
Global conformal calibration instead of subgroup calibration; Remove mask quality features; Remove material posterior entropy; Use category-only calibration groups; Use fixed engineering-table ranges without learned residual calibration
Calibrate on randomly permuted property labels; Use calibration objects from disjoint categories without subgroup adjustment; Apply calibration scores from high-quality masks to low-quality masks; Replace material posterior entropy with random confidence; Evaluate calibration after shuffling object masks across images
Achieve 90 percent nominal interval coverage within plus or minus 5 percentage points overall on proxy targets; Achieve subgroup coverage no lower than 80 percent for major material and object-category groups; Reduce calibration_error by at least 25 percent relative to uncalibrated lookup confidence; Do not increase median interval width by more than 20 percent relative to uncalibrated table intervals after calibration; Negative controls should show degraded coverage or inflated interval width, confirming dependence on valid labels, masks, and confidence features

Evidence paper IDs:
openalex:W4402500749; openalex:W4416850904; openalex:W4403323960; openalex:W2798280964; openalex:W3200689778; openalex:W4312347618

Risks, controls, or fallback:
Risk: proxy labels and table-derived intervals may not reflect true object-specific properties, so conformal guarantees may only hold for the proxy visible-material target. Fallback: report the calibrated target explicitly as a visible-material property interval, add failure_warning for hidden structure and coatings, and evaluate separate calibration curves for proxy labels versus any available measured ObjectFolder-style properties.

---

## Item 4: HUM-0415b0073a

类型：`single_idea`

### Candidate A

Title:
Mask-Conditioned Material Mixtures for Calibrated Property Intervals

Core proposal:
For each detected object mask, estimate a calibrated probability distribution over visible surface materials from frozen CLIP/OpenSurfaces/MINC-style material classifiers applied to masked crops and local texture patches. Combine the material mixture with the object category to query ObjectFolder/ObjectFolder2.0 and normalized engineering material tables. The output is an object-level JSON record containing top-k materials, category-conditioned candidate materials, and interval-valued physical properties whose width increases with material ambiguity and table disagreement.

Motivation or baseline weakness:
Open-vocabulary detection and segmentation pipelines such as GroundingDINO plus SAM can localize visible indoor objects, but direct category-to-property lookup treats each object as if it had a single known material. This is brittle for composite, coated, upholstered, laminated, or partially occluded objects, where single RGB images expose only surface cues and can lead to overconfident estimates of density, Young's modulus, hardness, friction, and related properties.

Mechanism or approach:
A lightweight material-mixture calibrator: temperature scaling or isotonic calibration over frozen material logits, followed by a deterministic category-conditioned interval aggregator with unit normalization and table provenance fields.
Minimize calibrated material classification loss and interval scoring loss. Use material cross-entropy or NLL where labels are available, plus an interval objective that rewards high coverage of proxy table-derived targets while penalizing unnecessarily wide intervals.

Experiment and implementation plan:
GroundingDINO; SAM; CLIP; OpenSurfaces; MINC; ObjectFolder; ObjectFolder2.0; engineering_material_property_tables
Indoor RGB images from ScanNet, Matterport3D, or OpenRooms with object masks, boxes, or generated masks; Material labels or proxy material labels mapped from OpenSurfaces/MINC taxonomies to indoor object regions; Object-category to candidate-material mappings for common indoor objects; Physical property ranges from ObjectFolder, ObjectFolder2.0, and normalized engineering material property tables; A validation split with manually checked object categories, masks, material labels, and acceptable property intervals for calibration
run_detection_segmentation.py to produce GroundingDINO detections and SAM masks; extract_masked_material_logits.py to compute material logits from masked crops, texture patches, and optional context crops; build_material_property_table.py to align taxonomies, normalize units, and store property ranges with provenance; train_calibrator.py to fit temperature scaling, isotonic calibration, or a small linear calibration layer; aggregate_property_intervals.py to combine calibrated material mixtures with category-conditioned property tables; evaluate_object_property_json.py to score object-level JSON outputs, calibration, and interval quality
object_recall; mask_iou; material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Replace calibrated material mixture with top-1 material only; Remove object-category conditioning from property aggregation; Use uncalibrated CLIP/OpenSurfaces/MINC logits instead of calibrated material probabilities; Use bounding boxes instead of masks for material evidence; Use category-only property lookup with no visual material model; Return point estimates instead of calibrated intervals
Randomly permute material labels before property lookup; Use object category only with no masked visual crop; Use full-image material predictions instead of object-specific masks; Evaluate on blank or eroded masks to measure context leakage; Shuffle property tables across material names while preserving category frequencies
Improve material_macro_f1 by at least 5 percentage points over a frozen masked-crop CLIP baseline; Reduce density_log_mae and youngs_modulus_log_mae by at least 10% relative to category-only property lookup; Achieve prediction_interval_coverage within 5 percentage points of nominal 90% coverage; Keep average interval width lower than a category-only conservative interval at matched coverage; Maintain mask_iou within 2 percentage points of the GroundingDINO plus SAM pipeline

Evidence paper IDs:
openalex:W4402500749; openalex:W4411238954; openalex:W2798280964; openalex:W2895238724; openalex:W4391722892; openalex:W4312347618

Risks, controls, or fallback:
Risk: visible surface material may not reveal internal composition, especially for painted, laminated, upholstered, reflective, transparent, or low-resolution objects. Fallback: emit broader category-conditioned intervals, include failure_warning tags for hidden-core or low-evidence cases, and report performance separately for visibly homogeneous versus likely composite objects.

### Candidate B

Title:
Mask-Conditioned Material Mixture to Property Intervals

Core proposal:
For each detected object mask, estimate a calibrated distribution over visible surface-material classes using frozen masked-crop material classifiers aligned to OpenSurfaces/MINC-style taxonomies. Combine the top-k material probabilities with the detected object category to retrieve candidate physical-property intervals from ObjectFolder/ObjectFolder2.0-derived object/material property records and normalized in-dataset property proxies. The mechanism outputs interval-valued properties; intervals are widened when material entropy is high, when category-material compatibility is weak, or when the mask covers too little visible surface.

Motivation or baseline weakness:
Open-vocabulary detectors and promptable segmenters such as GroundingDINO plus SAM can localize visible objects, but direct category-to-property lookup ignores material mixtures and the fact that single RGB exposes mainly surface appearance. This can make density, elastic modulus, hardness, friction, and Poisson-ratio estimates overconfident, especially for coated, upholstered, laminated, transparent, or low-resolution objects.

Mechanism or approach:
A lightweight material-mixture-to-property calibrator consisting of temperature scaling or isotonic calibration over frozen material logits, a category-material compatibility matrix estimated from training data, and a deterministic interval aggregator that unions or probability-weights ObjectFolder/ObjectFolder2.0 property ranges.
Minimize calibrated material cross-entropy plus an interval scoring objective for physical properties. The interval term rewards containing proxy property labels from ObjectFolder/ObjectFolder2.0 mappings while penalizing unnecessarily wide intervals, with a separate calibration penalty for nominal interval coverage.

Experiment and implementation plan:
GroundingDINO; SAM; CLIP; OpenSurfaces; MINC; ObjectFolder; ObjectFolder2.0
Indoor RGB images with object boxes or masks and object categories; Masked object crops produced by GroundingDINO plus SAM or available ground-truth masks; Visible-surface material labels or proxy labels mapped to an OpenSurfaces/MINC-style taxonomy; Object-category to candidate-material mappings estimated from training annotations; Physical-property proxy intervals derived only from ObjectFolder and ObjectFolder2.0 records after unit normalization
run_detection_segmentation.py for GroundingDINO plus SAM masks; extract_masked_material_logits.py for masked crops and visible-region material logits; build_objectfolder_property_table.py for taxonomy alignment and unit normalization; train_material_calibrator.py for temperature scaling or isotonic calibration; aggregate_property_intervals.py for category-conditioned interval construction; evaluate_object_property_json.py for object-level JSON outputs and supported metrics
object_recall; mask_iou; material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error
Replace material mixture with single top-1 material; Remove object-category conditioning from property aggregation; Use uncalibrated material logits instead of calibrated material probabilities; Use boxes instead of masks for material evidence; Return median point estimates instead of intervals; Disable entropy-based interval widening
Randomly permute material labels before property aggregation; Use object category only with no masked visual crop; Use full-image material predictions instead of object masks; Evaluate on empty or synthetic blank masks to test context leakage; Shuffle ObjectFolder/ObjectFolder2.0 property records across material classes
Improve material_macro_f1 by at least 5 percentage points over the frozen masked-crop material baseline; Reduce density_log_mae and youngs_modulus_log_mae by at least 10% relative to category-only ObjectFolder/ObjectFolder2.0 lookup; Achieve prediction_interval_coverage within 5 percentage points of nominal 90% coverage; Keep mask_iou within 2 percentage points of the GroundingDINO plus SAM mask pipeline when using predicted masks; Reduce calibration_error relative to uncalibrated material-probability aggregation

Evidence paper IDs:
openalex:W4402500749; openalex:W4411238954; openalex:W2798280964; openalex:W2895238724; openalex:W4391722892; openalex:W4312347618

Risks, controls, or fallback:
Risk: visible surface material may not reveal internal composition, and ObjectFolder/ObjectFolder2.0 proxy intervals may not cover all indoor categories. Fallback: emit broader category-conditioned intervals, mark hidden-core/coated/reflective/transparent/low-resolution objects with failure_warning tags, and report results separately for categories with and without reliable property proxies.

---

## Item 5: HUM-1b8a6a088f

类型：`portfolio`

### Candidate A

Idea 1
Title:
Context-Constrained Material Mixture Adapter for Object-Level Property Intervals

Core proposal:
Add a lightweight material-mixture adapter that fuses frozen visual material logits with object-category and room-context priors. The adapter estimates p(material | visual_crop, object_category, room_context) and maps the resulting top-k material mixture to physical-property intervals using a canonical material-property table. The priors are used as soft constraints rather than hard overrides: a learned or temperature-scaled gate downweights category/context priors when visual material evidence is confident and upweights them when visual evidence is ambiguous.

Motivation or baseline weakness:
A CLIP- or VLM-based material classifier can assign visually plausible but physically inconsistent materials to indoor objects because it relies heavily on local appearance cues. This causes large property errors for ambiguous surfaces such as painted wood, plastic laminate, metal-coated fixtures, upholstered furniture, and glossy composite objects.

Mechanism or approach:
A probabilistic fusion module that takes frozen object-crop material logits, object category, room type/context label, mask-derived appearance statistics, and detector confidence as input. It outputs a calibrated top-k material distribution, mixture-weighted property intervals, and an ambiguity flag when the posterior remains multimodal or when visual and contextual cues conflict.
Train the adapter with material supervision where available and table-derived property intervals as proxy targets. Use L = CE(material) + lambda * interval_score(properties) + beta * calibration_penalty + gamma * prior_overconfidence_penalty. Property predictions are mixture-weighted intervals rather than single deterministic constants, and the prior_overconfidence_penalty discourages confident context-only predictions when visual logits disagree.

Experiment and implementation plan:
GroundingDINO + SAM/SAM2 + CLIP material classifier + top-1 engineering material-property lookup; Mask2Former + MINC/OpenSurfaces-style material classifier + top-1 engineering material-property lookup; VLM prompted to infer object material and physical properties directly; Uniform material prior fused with frozen visual material logits
Indoor scene images from ScanNet, Matterport3D, OpenRooms, or a comparable indoor RGB/RGB-D source; Object masks or boxes from annotations or from a frozen detector/segmenter; Object categories from dataset annotations or detector labels; Room-context labels from dataset metadata, scene classifier output, or manually defined indoor room categories; Material labels or proxy material labels where available; Canonical engineering material-property tables converted into material-level value ranges or distributions
run_detection_segmentation.py for object boxes, masks, categories, and detector confidence; extract_object_crops_and_context.py for crop features, mask statistics, category labels, and room-context labels; build_material_property_table.py for canonical material names and property interval mappings; train_material_context_adapter.py for probabilistic fusion, calibration, and gating; evaluate_object_property_json.py for object-level JSON output, material metrics, property metrics, and interval metrics
material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; expected_calibration_error; selective_risk
Remove object-category prior and use only visual material logits plus room context; Remove room-context prior and use only visual material logits plus object category; Use hard top-1 material lookup instead of material-mixture propagation; Replace learned/calibrated priors with a uniform material prior; Remove confidence-based gating so category/context priors always have fixed weight; Predict point properties directly from VLM text output instead of table-grounded intervals
Randomly permute object categories before fusion while preserving visual logits and room labels; Randomly permute room-context labels while preserving visual logits and object categories; Use a deliberately mismatched material-property table with material names preserved but property values reassigned; Train the adapter with category labels replaced by coarse random bins of the same cardinality
Improve material_top3_accuracy over the frozen visual material baseline by at least 5 percentage points on held-out indoor objects; Reduce density_log_mae and youngs_modulus_log_mae by at least 10 percent relative to top-1 material lookup; Achieve prediction_interval_coverage within 5 percentage points of the nominal interval level for density and Young's modulus; Maintain object_recall and mask_iou within 1 percent of the unchanged detector/segmenter pipeline; Show that category and room-context permutation negative controls remove most of the observed gain

Risks, controls, or fallback:
Risk: category and scene priors may overrule valid visual evidence for unusual, decorative, or repaired objects. Fallback: use confidence-gated prior fusion, widen intervals when visual and contextual cues disagree, and emit an ambiguity flag instead of forcing a narrow property estimate.

---

Idea 2
Title:
Visibility-Aware Property Uncertainty from Single-View Object Evidence

Core proposal:
Add a visibility-aware uncertainty estimator that decides, for each object and property, whether to return a narrow interval, a broad interval, or an abstention warning. The estimator uses observable difficulty signals including visible mask area, truncation, occlusion, crop resolution, detector confidence, material posterior entropy, top-k material property spread, category-level hidden-structure ambiguity, and disagreement among frozen predictors. The module targets calibrated uncertainty and selective reliability rather than improving the underlying material classifier.

Motivation or baseline weakness:
A single RGB view often cannot reveal hidden material structure, coatings, hollow interiors, internal reinforcement, or load-bearing composition. Direct VLM or lookup-table baselines therefore tend to output overconfident point estimates even when the visible evidence is insufficient for reliable physical-property prediction.

Mechanism or approach:
A lightweight uncertainty head or conformal calibration layer that consumes per-object difficulty features and a base table-grounded property prediction. It outputs property-specific calibrated intervals, an abstention score, and failure_warning labels for properties that are not visually identifiable from the current view.
Use a held-out calibration split to fit property-specific interval widths or conformal residual quantiles around a base material-table predictor. Optimize for minimum interval width subject to target empirical coverage, with an abstention objective that ranks high-error or high-residual objects above low-error objects. A possible loss is L = interval_width + alpha * coverage_violation + beta * abstention_ranking_loss, evaluated separately for each property.

Experiment and implementation plan:
GroundingDINO + SAM/SAM2 + CLIP material classifier + point-valued property table; VLM direct property prompting with parsed confidence text; Material top-k lookup with uncalibrated min-max property intervals; Conformal intervals using only material class and no visibility or object-quality features
Indoor scene images with detected or annotated visible objects; Object masks or boxes, detector confidences, crop resolution, and boundary-truncation indicators; Material predictions or material posteriors from frozen classifiers; Object categories for category-level hidden-structure ambiguity features; Proxy physical-property labels or interval labels derived from material annotations and canonical property tables; A training/tuning split and a strictly held-out calibration split
compute_visibility_features.py for visible area, truncation, occlusion proxies, crop resolution, and mask quality; run_predictor_ensemble.py for material-posterior entropy, top-k property spread, and predictor disagreement; fit_conformal_property_intervals.py for property-specific calibrated intervals; train_abstention_ranker.py for failure-warning and selective-risk ranking; evaluate_uncertainty_and_selective_risk.py for coverage, interval width, calibration, abstention, and risk curves
prediction_interval_coverage; mean_interval_width_normalized; expected_calibration_error; selective_risk; density_log_mae_at_fixed_coverage; youngs_modulus_log_mae_at_fixed_coverage; friction_coefficient_mae_at_fixed_coverage; failure_warning_precision; failure_warning_recall; abstention_auroc_for_high_error_objects
Use conformal calibration without visibility or object-quality features; Use visibility features without material-posterior entropy or top-k property spread; Use material entropy only and remove detector, mask, and crop-quality features; Use fixed-width intervals per material instead of object-specific calibrated intervals; Remove predictor-disagreement features; Remove category-level hidden-structure ambiguity features
Shuffle visibility and object-quality features across objects while preserving material predictions; Assign random uncertainty scores with the same marginal distribution as the learned scores; Evaluate separately on large unoccluded objects to verify that gains concentrate on difficult visibility cases; Replace detector confidence with random confidence values drawn from the same marginal distribution
Achieve empirical prediction_interval_coverage within 5 percentage points of the target level for at least four of five property types; Reduce selective_risk by at least 15 percent at 70 percent retained coverage compared with uncalibrated material-table intervals; Produce lower average normalized interval width than naive material min-max intervals while maintaining target coverage; Rank high-error objects with at least 20 percent higher failure_warning precision than random ranking at the same warning rate; Show that shuffling visibility features measurably degrades selective-risk or interval-width performance

Risks, controls, or fallback:
Risk: proxy property labels derived from material tables may make uncertainty appear calibrated while true object properties remain affected by unobserved internal structure. Fallback: report calibration against both material-derived proxy labels and broad engineering intervals, widen intervals for high hidden-structure categories, and abstain when a property depends primarily on unobservable internal composition.

---

Idea 3
Title:
Property-Consistent Object JSON Repair Layer for Plug-and-Play Vision Pipelines

Core proposal:
Add a deterministic validation and lightweight candidate-ranking layer after the frozen perception modules. The layer canonicalizes material names, validates schema fields and units, rejects physically impossible values, and selects one coherent material-property bundle from upstream candidates. It does not invent new object detections or new material classes; it repairs only by choosing among candidates, clipping to declared feasible bounds, widening uncertainty intervals, or abstaining when no candidate satisfies the constraints.

Motivation or baseline weakness:
A modular detector/segmenter, material classifier, VLM, and property-table pipeline can produce invalid or inconsistent structured JSON. Typical failures include impossible Poisson's ratios, negative or unit-mismatched values, density and modulus copied from different material rows, missing uncertainty fields, unsupported material names, and contradictions between the selected material and its assigned properties.

Mechanism or approach:
A schema-and-physics consistency validator plus a small ranking model for candidate material-property bundles. Inputs are raw object JSON records, candidate material names and scores, object category, detector confidence, and canonical material-property table entries. Outputs are validated object-level JSON records with standardized units, coherent material-property intervals, confidence_or_uncertainty fields, repair_status, and failure_warning fields when any correction, clipping, widening, or abstention occurs.
Maximize valid structured outputs while minimizing material and property error under a constrained candidate-selection objective. For each object, select bundle b from candidate set B using score(b) = visual_material_score(b) + category_prior_score(b) - constraint_violation_penalty(b) - uncertainty_width_penalty(b). Hard constraints enforce schema validity, allowed units, feasible property ranges, and single-bundle consistency; if no candidate passes hard constraints, the layer emits abstain_or_unknown rather than a confident repaired value.

Experiment and implementation plan:
GroundingDINO + SAM/SAM2 + CLIP + raw engineering table lookup JSON; SAM2 or Mask2Former + VLM-prompted structured JSON without post-hoc validation; Material classifier top-1 property lookup with no schema repair or constraint checking; Rule-only range clipping without candidate reranking or bundle consistency
Indoor images from ScanNet, Matterport3D, OpenRooms, or a comparable indoor source; Detected object masks or boxes and object categories; Raw candidate material predictions from frozen classifiers and VLM prompts; Canonical material-property tables with standardized units, aliases, and feasible ranges; Generated raw pipeline JSON outputs for validation and repair testing; Material labels or proxy labels where available for evaluating candidate ranking
generate_raw_object_json.py for baseline unvalidated object records; canonicalize_material_names.py for mapping raw material strings and aliases to table entries; validate_physical_property_ranges.py for density, modulus, Poisson ratio, hardness, and friction constraints; repair_and_rank_property_bundles.py for constrained candidate selection, clipping, widening, and abstention; evaluate_json_validity_and_property_metrics.py for schema validity, consistency rate, property errors, and warning behavior
structured_json_validity_rate; schema_field_completeness; unit_consistency_rate; material_accuracy; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; failure_warning_rate_on_repaired_cases; abstention_rate
Only schema validation without physical-property constraints; Only range clipping without material-bundle consistency; Use top-1 material lookup without candidate reranking; Remove category prior from bundle ranking; Remove uncertainty widening after repair; Remove failure_warning generation for repaired or low-confidence outputs
Apply the repair layer to randomly generated material candidates to verify it cannot create high material accuracy without plausible upstream candidates; Disable canonical material-name mapping to test dependence on correct table alignment; Use intentionally corrupted property tables and require the validator to flag table-level inconsistency rather than silently producing confident outputs; Randomly permute candidate material scores before reranking while preserving the candidate set
Increase structured_json_validity_rate to at least 98 percent without reducing object_recall; Reduce impossible, out-of-range, or unit-inconsistent property values to below 1 percent of object outputs; Reduce density_log_mae or youngs_modulus_log_mae by at least 8 percent relative to raw top-1 lookup when multiple material candidates are available; Flag at least 90 percent of repaired records with repair_status or failure_warning; Show that corrupted-table and randomized-candidate negative controls prevent false claims of property improvement

Risks, controls, or fallback:
Risk: a repair layer may hide upstream perception errors by producing physically valid but semantically wrong outputs. Fallback: preserve raw candidates in separate raw_prediction fields, mark all repaired predictions explicitly, evaluate repaired and unrepaired metrics separately, and abstain rather than force a confident value when all candidate material-property bundles have low visual support.

### Candidate B

Idea 1
Title:
Object-Material Interval Lookup With Evidence-Gated Mixture Predictions

Core proposal:
For each detected object mask, estimate a posterior over visible material families from masked-crop evidence using frozen material recognizers and prompt-based material scoring. Combine this posterior with an object-category compatibility prior and a scene-context compatibility prior, then map each retained material family to engineering-property intervals. The output is a calibrated mixture distribution per property, represented by mean, central interval, confidence, top contributing material hypotheses, and explicit warnings when the visible material is insufficient to infer bulk composition. Candidate materials are retained only if they pass three gates: localized mask evidence above a validation-tuned threshold, compatibility with the predicted object category, and no contradiction with coarse scene context such as floor, wall, furniture, appliance, or container role.

Motivation or baseline weakness:
CLIP/OpenSurfaces/MINC-style material recognition can provide plausible visible-material labels, but a single RGB crop often cannot identify hidden composition, coatings, laminates, or exact material grade. Direct point estimates for density, Young's modulus, hardness, Poisson's ratio, and friction therefore become overconfident when the visual evidence supports only a broad material family.

Mechanism or approach:
A lightweight property-interval resolver: a table-backed probabilistic mapper that normalizes material names, combines material posterior, object-category prior, and engineering material-property ranges, and emits per-property mean, prediction interval, confidence, evidence strings, and failure_warning fields.
Train only calibration and mixture weights while keeping detectors, segmenters, and frozen material recognizers fixed. Minimize interval-aware negative log likelihood plus log-space absolute error on proxy-labeled object-property data, with a penalty for intervals narrower than their empirical validation coverage supports: objective = property_log_mae + lambda * calibration_error + beta * undercoverage_penalty + rho * unsupported_narrow_interval_penalty. Interval width is not minimized directly unless nominal coverage is satisfied on validation objects.

Experiment and implementation plan:
GroundingDINO + SAM + CLIP point-property lookup; GroundingDINO + SAM + OpenSurfaces material lookup; GroundingDINO + SAM + MINC material lookup; LLaVA prompted JSON property prediction
Indoor RGB images with object boxes or masks, evaluated only at object level; Material labels or proxy material labels mapped to OpenSurfaces and MINC-compatible classes; Object-category to plausible-visible-material mappings for indoor objects; Engineering material-property tables with intervals for density, Young's modulus, Poisson's ratio, hardness, and friction coefficient, normalized to shared material-family names; Optional ObjectFolder/ObjectFolder2.0 objects with known or proxy physical properties for validation of the property-table mapping rather than scene-level training
run_detection_segmentation.py to produce object_id, category, mask_or_box, detection_score, and mask_quality_score using GroundingDINO plus SAM or SAM2; extract_masked_material_scores.py to score masked crops, box crops, and full images with CLIP/OpenSurfaces/MINC-compatible material labels; build_property_interval_table.py to normalize material aliases, units, and property ranges and to flag material families with grade-dependent ranges; resolve_property_mixture.py to combine material posteriors and property intervals into structured JSON with top contributors and failure_warning values; evaluate_property_intervals.py to compute log MAE, interval coverage, calibration error, material metrics, and selective risk on the same detected objects
object_recall; mask_iou; material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Remove object-category prior and use material visual posterior only; Remove scene-context compatibility prior; Use top-1 material only instead of mixture over top-k materials; Use table medians as point estimates instead of calibrated intervals; Replace SAM masks with boxes to test sensitivity to localized material evidence
Shuffle material-property table rows while keeping material labels fixed; property metrics should degrade while material metrics remain similar; Use full-image CLIP scores instead of masked object crops; locality-sensitive material classes should degrade; Assign category-frequency material priors without visual evidence; confidence should be lower and selective risk should worsen on visually atypical objects; Force all objects to a generic plastic/wood/metal prior depending only on superclass; improvements over this control must come from localized evidence; Evaluate with masks shifted to nearby background regions; material support and confidence should drop
Improve density_log_mae by at least 10% over top-1 CLIP property lookup on the same detected objects; Improve youngs_modulus_log_mae by at least 10% over top-1 material lookup on the same detected objects; Achieve prediction_interval_coverage within 5 percentage points of the nominal 90% interval target; Reduce calibration_error by at least 15% relative to LLaVA prompted point estimates with self-reported confidence; Do not reduce material_top3_accuracy by more than 2 percentage points compared with the best frozen material recognizer on the same masks

Evidence paper IDs:
openalex:W4402427278; openalex:W4402500749; openalex:W2798280964; openalex:W3012463097; openalex:W3046559354; openalex:W3200689778; openalex:W4312347618

Risks, controls, or fallback:
Risk: proxy property intervals may be too broad to show useful metric gains, and visual cues may not distinguish laminates, coatings, composites, or hidden internal materials. Fallback: report conservative intervals with explicit failure_warning values for ambiguous or hidden-composition cases, evaluate selective prediction by abstaining when material posterior entropy or table range width exceeds a threshold, and separately report visible-material accuracy so property errors are not mistaken for segmentation failures.

---

Idea 2
Title:
Mask-Conditioned Material Evidence Verification for VLM Property JSON

Core proposal:
Insert a verifier between segmentation and final property output. A VLM first proposes object category, material hypotheses, property intervals, and natural-language evidence. Each proposed material is then checked against masked-crop evidence using frozen CLIP/material classifiers and counterfactual material prompts. The verifier accepts, widens, or flags the VLM output according to three tests: the proposed material must score higher on the masked crop than on unrelated background or full-image context, it must be plausible for the object category without being category-only, and it must exceed visually confusable counterfactual materials by a validation-calibrated margin. Unsupported claims are not replaced by a new point estimate; they are converted to wider property intervals with failure_warning fields.

Motivation or baseline weakness:
Vision-language models such as LLaVA, BLIP-2, and Qwen-VL can produce plausible object-level physical-property JSON, but their material and property claims may be unsupported by localized visual evidence, sensitive to prompt wording, and influenced by object-category priors rather than the pixels inside the target mask.

Mechanism or approach:
A material-evidence verifier that computes per-object support scores from masked-crop similarity, mask-versus-full-image leakage contrast, category plausibility, and counterfactual material margins, then rescales property confidence and interval width without fine-tuning the VLM.
Fit verifier thresholds and calibration parameters on validation proxy labels while keeping VLMs and visual encoders frozen. Optimize material support and calibrated acceptance: objective = material_cross_entropy_proxy + alpha * counterfactual_margin_loss + gamma * confidence_calibration_loss + tau * unsupported_acceptance_penalty, with low-support predictions handled by abstention or interval widening rather than forced relabeling.

Experiment and implementation plan:
LLaVA prompted structured JSON prediction; BLIP-2 prompted structured JSON prediction; Qwen-VL prompted structured JSON prediction; GroundingDINO + SAM + CLIP material-to-property lookup
Indoor RGB images evaluated at object level; Object masks or boxes generated by GroundingDINO plus SAM/SAM2 or Mask2Former; Material class labels or proxy labels mapped to OpenSurfaces and MINC-compatible classes; Engineering material-property intervals linked to material classes; Prompt templates for VLM object category, material hypotheses, localized evidence, uncertainty, and property JSON
prompt_vlm_property_json.py to collect baseline VLM object-level predictions with multiple prompt paraphrases and self-reported confidence; score_local_material_evidence.py to compare masked crop, box crop, background crop, and full-image material scores; run_counterfactual_material_prompts.py to score visually confusable alternatives such as wood veneer versus plastic laminate, metal versus painted plastic, leather versus vinyl, and ceramic versus stone; calibrate_verifier.py to fit support thresholds, confidence scaling, and widening rules on validation proxy labels; evaluate_verified_json.py to compare accepted, widened, rejected, and raw VLM predictions under identical detected objects
material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Verifier without counterfactual material prompts; Verifier without full-image leakage contrast; Verifier using box crops instead of masks; No interval widening for unsupported VLM claims; Use VLM self-confidence only instead of verifier confidence
Verify each object using another random object's mask crop; accepted support should decrease; Use full-scene material scores as if they were object-local evidence; locality-sensitive calibration should degrade; Swap object categories while keeping masks fixed; category-plausibility-only acceptance should be exposed; Use adversarially broad prompts that list all common indoor materials as evidence; verifier should not accept all listed materials; Randomize the VLM material string before verification; acceptance and property accuracy should drop
Reduce calibration_error by at least 20% relative to raw VLM self-confidence; Reduce selective_risk by at least 15% at 70% object coverage relative to raw VLM predictions; Improve material_macro_f1 by at least 5 points over raw VLM material labels on proxy-labeled objects; Maintain or improve density_log_mae and youngs_modulus_log_mae on accepted predictions compared with CLIP top-1 lookup on the same objects; At least 80% of emitted failure_warning cases must correspond to high material ambiguity, mask error, visible-surface versus bulk-material mismatch, or category-property mismatch under manual audit

Evidence paper IDs:
openalex:W4399597788; openalex:W4392222076; openalex:W4402155831; openalex:W4385327621; openalex:W4402500749; openalex:W2798280964; openalex:W2895238724

Risks, controls, or fallback:
Risk: the verifier may reject too many objects because material datasets do not align with indoor object appearances, or because VLM predictions are correct at the object-category level but not visually verifiable from the crop. Fallback: use verifier scores for uncertainty calibration and interval widening rather than hard rejection, report selective-risk curves across acceptance thresholds, and keep a separate category-prior-only baseline to show whether gains come from localized evidence rather than semantic priors.

---

Idea 3
Title:
Segmentation-Property Sensitivity Calibration via Mask Perturbation Ensembles

Core proposal:
Generate a compact ensemble of plausible masks per detected object using alternative segmentation backbones, prompt perturbations, score-threshold variants, and controlled mask erosions/dilations. Run the same frozen material-to-property resolver on every mask sample. Estimate mask-induced epistemic uncertainty from dispersion in material posteriors and property intervals, then widen final intervals and add failure_warning tags when predictions are sensitive to mask choice. The method attributes uncertainty specifically to segmentation by comparing perturbations around the same detection and by separating mask-induced dispersion from material-posterior entropy.

Motivation or baseline weakness:
GroundingDINO/SAM/SAM2/Mask2Former pipelines can produce useful object masks, but small mask errors can include background, shadows, or adjacent objects, or exclude material-discriminative regions. Downstream material and physical-property estimates can therefore be unstable even when object recall and average mask IoU appear acceptable.

Mechanism or approach:
A mask-sensitivity calibrator that creates low-cost mask perturbation ensembles, measures property dispersion and material-posterior disagreement across masks, and converts that dispersion into calibrated uncertainty intervals and object-level failure_warning tags.
Fit only the dispersion-to-uncertainty calibration layer while keeping segmentation models and material/property resolver fixed. Minimize property error and uncertainty miscalibration under mask perturbations: objective = mean property_log_mae across mask samples + eta * interval_coverage_loss + zeta * high_confidence_high_variance_penalty + kappa * mask_quality_monotonicity_loss, where confidence should decrease as mask-induced variance or mask-quality disagreement increases.

Experiment and implementation plan:
GroundingDINO + SAM single-mask pipeline; GroundingDINO + SAM2 single-mask pipeline; Mask2Former single-mask pipeline; GroundingDINO + SAM + CLIP/OpenSurfaces material lookup without uncertainty propagation
Indoor scene images evaluated at object level; Available ground-truth or pseudo object masks for mask_iou evaluation and for stratifying results by mask quality; Proxy material labels from OpenSurfaces/MINC-compatible mappings; Engineering property tables for material-to-property intervals; Optional ObjectFolder/ObjectFolder2.0 rendered or photographed objects with property annotations or proxy labels to test whether mask-induced uncertainty transfers to isolated-object settings
generate_mask_ensemble.py to run SAM, SAM2, Mask2Former, prompt perturbations, threshold variants, and morphological mask variants while preserving object_id alignment; run_property_resolver_on_masks.py to compute material posterior, property interval, and evidence fields for each mask sample; fit_mask_sensitivity_calibrator.py to map ensemble dispersion, mask IoU proxies, and material entropy to calibrated confidence intervals; evaluate_mask_property_sensitivity.py to correlate mask_iou, material error, property error, interval coverage, and uncertainty; export_object_property_json.py to produce final structured JSON with selected mask, ensemble summary, evidence, and warnings
object_recall; mask_iou; material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Use only one segmentation model instead of multi-source mask ensemble; Use morphological perturbations only without SAM/SAM2/Mask2Former diversity; Use ensemble mean without uncertainty calibration; Remove mask-sensitivity failure warnings; Replace masks with bounding boxes for all property predictions
Randomly perturb masks outside the object region to test whether sensitivity is merely noise-driven; Use identical duplicated masks as an ensemble, which should not improve calibration; Shuffle ensemble property predictions across objects before calibration; any calibration gain should disappear; Calibrate uncertainty from object category frequency rather than mask-induced dispersion; Apply perturbations to background-only masks; material confidence should remain low and warnings should increase
Improve prediction_interval_coverage to within 5 percentage points of nominal 90% while keeping intervals narrower than a category-only prior baseline; Reduce calibration_error by at least 15% compared with single-mask CLIP/OpenSurfaces lookup; Reduce selective_risk by at least 10% at fixed 80% object coverage; Identify high-risk mask-sensitive objects with at least 70% precision in manual audit; Do not reduce object_recall by more than 1 percentage point relative to the best single-mask pipeline because calibration should operate after detection rather than filtering detections by default

Evidence paper IDs:
openalex:W4402500749; openalex:W7148178853; openalex:W4416850904; openalex:W4403323960; openalex:W4411238954; openalex:W4385327621; openalex:W2798280964

Risks, controls, or fallback:
Risk: mask perturbation may overestimate uncertainty for highly textured objects, underestimate uncertainty when all segmenters share the same systematic error, or conflate segmentation uncertainty with intrinsic material ambiguity. Fallback: report separate components for mask-induced dispersion, material-posterior entropy, and category-property prior width; if all masks agree but visual evidence conflicts with category priors, emit a persistent evidence_conflict failure_warning rather than a confident property prediction.

---

## Item 6: HUM-15f39d9f19

类型：`single_idea`

### Candidate A

Title:
Selective Uncertainty Head for Hidden-Material Failure Cases

Core proposal:
Add a selective uncertainty head that predicts object-level observability and hidden-material risk from mask quality, crop resolution, material entropy, specularity/texture cues, object category, and disagreement among CLIP, OpenSurfaces/MINC, and VLM material predictions. The head decides whether to output narrow intervals, broad intervals, or abstention-style failure warnings.

Motivation or baseline weakness:
Detection, material recognition, and table lookup pipelines can produce reasonable average property estimates, but they usually do not know when to abstain on objects whose physical properties are unknowable from single RGB, such as coated wood, fabric-covered foam, glossy plastic, or metal-painted surfaces.

Mechanism or approach:
A small gradient-boosted tree, logistic regression, or two-layer MLP trained on frozen pipeline features to estimate risk of property error exceeding a threshold for each object-property pair.
Optimize selective prediction: minimize property error on accepted predictions subject to target coverage, using binary labels derived from whether proxy table-derived ground truth falls inside predicted intervals or whether log error exceeds a threshold.

Experiment and implementation plan:
Mask2Former; SAM; CLIP; OpenSurfaces; MINC; LLaVA; ObjectFolder; engineering_material_property_tables
Indoor object crops and masks from ScanNet, Matterport3D, or OpenRooms; Proxy physical-property labels or intervals from material/category table mappings; Frozen material logits from CLIP/OpenSurfaces/MINC-style models; VLM material and ambiguity descriptions from LLaVA or BLIP-2; Mask quality features from SAM or Mask2Former outputs
extract_pipeline_features.py for entropy, disagreement, mask area, boundary quality, and category priors; make_proxy_error_labels.py for per-property high-error labels; train_selective_uncertainty_head.py for lightweight risk modeling; apply_abstention_policy.py for interval widening and failure_warning generation; evaluate_selective_risk.py for coverage-risk curves
density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk; material_macro_f1
Use material entropy only; Use model disagreement only; Remove mask-quality features; Remove object-category prior; Single global uncertainty score instead of per-property uncertainty; Always output broad intervals with no learned selector
Train the uncertainty head on randomly shuffled error labels; Use only object mask area as the risk predictor; Evaluate calibration after permuting material logits across objects; Force acceptance of all predictions to recover the non-selective baseline
At 70% accepted-object coverage, reduce selective_risk by at least 20% relative to non-selective property lookup; Improve calibration_error by at least 25% relative to uncalibrated interval outputs; Flag at least 60% of high-error hidden-material cases while keeping false warning rate below 30%; Do not degrade accepted-set material_macro_f1 relative to the frozen material baseline

Evidence paper IDs:
openalex:W4416850904; openalex:W4403323960; openalex:W4385327621; openalex:W2798280964; openalex:W3046559354; openalex:W4391722892

Risks, controls, or fallback:
Risk: proxy error labels may encode table bias rather than true physical uncertainty. Fallback: evaluate the head primarily as an abstention and calibration module, report sensitivity to multiple property tables, and use conservative interval widening when risk estimates disagree across tables.

### Candidate B

Title:
Selective Uncertainty Head for Hidden-Material Failure Cases

Core proposal:
Add a selective uncertainty head that predicts object-level observability and hidden-material risk from frozen pipeline features: mask quality, crop resolution, visible area, material entropy, disagreement among CLIP/OpenSurfaces/MINC-style material predictions, optional VLM ambiguity descriptions, object category, and texture/specularity cues. For each object-property pair, the head chooses narrow interval, widened interval, or abstention-style failure warning without changing the underlying detector, segmenter, or material classifier.

Motivation or baseline weakness:
Detection, material recognition, and table-lookup pipelines can produce reasonable average property estimates, but they often do not know when to abstain on objects whose physical properties are underdetermined from single RGB, such as coated wood, fabric-covered foam, glossy plastic, painted metal, glass, or laminated surfaces.

Mechanism or approach:
A small gradient-boosted tree, logistic regression model, or two-layer MLP trained on frozen pipeline features to estimate the probability that each property estimate will exceed a predefined error threshold or miss its nominal interval.
Optimize selective calibration using validation labels derived from held-out proxy property intervals. The head minimizes accepted-set property error and calibration_error while maintaining a target accepted-object coverage, with binary supervision indicating whether the base interval missed the proxy label or exceeded a per-property log-error threshold.

Experiment and implementation plan:
Mask2Former; SAM; CLIP; OpenSurfaces; MINC; LLaVA; ObjectFolder
Indoor object crops and masks from RGB scene images; Proxy physical-property labels or intervals derived from ObjectFolder-linked material/category mappings; Frozen material logits from CLIP/OpenSurfaces/MINC-style models; Optional VLM material and ambiguity descriptions from LLaVA or BLIP-2 used only as frozen features; Mask quality features from SAM or Mask2Former outputs; Held-out validation categories containing coated, upholstered, reflective, transparent, or visually ambiguous objects
extract_pipeline_features.py for entropy, disagreement, mask area, boundary quality, texture cues, and category priors; make_proxy_error_labels.py for per-property high-error and interval-miss labels; train_selective_uncertainty_head.py for lightweight risk modeling; apply_abstention_policy.py for interval widening and failure_warning generation; evaluate_calibrated_acceptance.py for accepted-coverage, property error, interval coverage, and calibration
density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; material_macro_f1
Use material entropy only; Use model disagreement only; Remove mask-quality features; Remove object-category prior; Use one global uncertainty score instead of per-property uncertainty; Always output broad intervals with no learned selector; Use VLM ambiguity text only, without visual/material features
Train the uncertainty head on randomly shuffled error labels; Use only object mask area as the risk predictor; Evaluate calibration after permuting material logits across objects; Force acceptance of all predictions to recover the non-selective baseline; Randomly assign failure warnings at the same abstention rate as the learned head
At 70% accepted-object coverage, reduce accepted-set density_log_mae and youngs_modulus_log_mae by at least 20% relative to non-selective property lookup; Improve calibration_error by at least 25% relative to uncalibrated interval outputs; Flag at least 60% of high-error hidden-material cases while keeping false warning rate below 30%; Do not degrade accepted-set material_macro_f1 relative to the frozen material baseline; Maintain prediction_interval_coverage within 5 percentage points of the target nominal coverage after interval widening

Evidence paper IDs:
openalex:W4416850904; openalex:W4403323960; openalex:W4385327621; openalex:W2798280964; openalex:W3046559354; openalex:W4391722892

Risks, controls, or fallback:
Risk: proxy error labels may encode ObjectFolder/material-table bias rather than true physical uncertainty, and hidden-material cases may be rare in validation data. Fallback: report sensitivity across multiple proxy-label construction rules, evaluate the head primarily as an abstention and calibration module, and default to conservative interval widening when feature-based risk estimates are unstable.

---

## Item 7: HUM-df4895517c

类型：`single_idea`

### Candidate A

Title:
Segmentation-Property Sensitivity Calibration via Mask Perturbation Ensembles

Core proposal:
Generate a compact ensemble of plausible masks per detected object using alternative segmentation backbones, prompt perturbations, score-threshold variants, and controlled mask erosions/dilations. Run the same frozen material-to-property resolver on every mask sample. Estimate mask-induced epistemic uncertainty from dispersion in material posteriors and property intervals, then widen final intervals and add failure_warning tags when predictions are sensitive to mask choice. The method attributes uncertainty specifically to segmentation by comparing perturbations around the same detection and by separating mask-induced dispersion from material-posterior entropy.

Motivation or baseline weakness:
GroundingDINO/SAM/SAM2/Mask2Former pipelines can produce useful object masks, but small mask errors can include background, shadows, or adjacent objects, or exclude material-discriminative regions. Downstream material and physical-property estimates can therefore be unstable even when object recall and average mask IoU appear acceptable.

Mechanism or approach:
A mask-sensitivity calibrator that creates low-cost mask perturbation ensembles, measures property dispersion and material-posterior disagreement across masks, and converts that dispersion into calibrated uncertainty intervals and object-level failure_warning tags.
Fit only the dispersion-to-uncertainty calibration layer while keeping segmentation models and material/property resolver fixed. Minimize property error and uncertainty miscalibration under mask perturbations: objective = mean property_log_mae across mask samples + eta * interval_coverage_loss + zeta * high_confidence_high_variance_penalty + kappa * mask_quality_monotonicity_loss, where confidence should decrease as mask-induced variance or mask-quality disagreement increases.

Experiment and implementation plan:
GroundingDINO + SAM single-mask pipeline; GroundingDINO + SAM2 single-mask pipeline; Mask2Former single-mask pipeline; GroundingDINO + SAM + CLIP/OpenSurfaces material lookup without uncertainty propagation
Indoor scene images evaluated at object level; Available ground-truth or pseudo object masks for mask_iou evaluation and for stratifying results by mask quality; Proxy material labels from OpenSurfaces/MINC-compatible mappings; Engineering property tables for material-to-property intervals; Optional ObjectFolder/ObjectFolder2.0 rendered or photographed objects with property annotations or proxy labels to test whether mask-induced uncertainty transfers to isolated-object settings
generate_mask_ensemble.py to run SAM, SAM2, Mask2Former, prompt perturbations, threshold variants, and morphological mask variants while preserving object_id alignment; run_property_resolver_on_masks.py to compute material posterior, property interval, and evidence fields for each mask sample; fit_mask_sensitivity_calibrator.py to map ensemble dispersion, mask IoU proxies, and material entropy to calibrated confidence intervals; evaluate_mask_property_sensitivity.py to correlate mask_iou, material error, property error, interval coverage, and uncertainty; export_object_property_json.py to produce final structured JSON with selected mask, ensemble summary, evidence, and warnings
object_recall; mask_iou; material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Use only one segmentation model instead of multi-source mask ensemble; Use morphological perturbations only without SAM/SAM2/Mask2Former diversity; Use ensemble mean without uncertainty calibration; Remove mask-sensitivity failure warnings; Replace masks with bounding boxes for all property predictions
Randomly perturb masks outside the object region to test whether sensitivity is merely noise-driven; Use identical duplicated masks as an ensemble, which should not improve calibration; Shuffle ensemble property predictions across objects before calibration; any calibration gain should disappear; Calibrate uncertainty from object category frequency rather than mask-induced dispersion; Apply perturbations to background-only masks; material confidence should remain low and warnings should increase
Improve prediction_interval_coverage to within 5 percentage points of nominal 90% while keeping intervals narrower than a category-only prior baseline; Reduce calibration_error by at least 15% compared with single-mask CLIP/OpenSurfaces lookup; Reduce selective_risk by at least 10% at fixed 80% object coverage; Identify high-risk mask-sensitive objects with at least 70% precision in manual audit; Do not reduce object_recall by more than 1 percentage point relative to the best single-mask pipeline because calibration should operate after detection rather than filtering detections by default

Evidence paper IDs:
openalex:W4402500749; openalex:W7148178853; openalex:W4416850904; openalex:W4403323960; openalex:W4411238954; openalex:W4385327621; openalex:W2798280964

Risks, controls, or fallback:
Risk: mask perturbation may overestimate uncertainty for highly textured objects, underestimate uncertainty when all segmenters share the same systematic error, or conflate segmentation uncertainty with intrinsic material ambiguity. Fallback: report separate components for mask-induced dispersion, material-posterior entropy, and category-property prior width; if all masks agree but visual evidence conflicts with category priors, emit a persistent evidence_conflict failure_warning rather than a confident property prediction.

### Candidate B

Title:
Segmentation-Property Sensitivity Calibration via Mask Perturbation Ensembles

Core proposal:
For each detected object, generate a compact ensemble of plausible masks using alternative segmentation backbones, prompt perturbations, and simple erosions/dilations. Run the same frozen material-to-property resolver on every mask sample. Use dispersion across material posteriors and property estimates to estimate mask-induced uncertainty, widen prediction intervals, and attach failure_warning tags when a property estimate is highly sensitive to the chosen mask.

Motivation or baseline weakness:
GroundingDINO/SAM/SAM2/Mask2Former pipelines can provide strong object masks, but small segmentation errors may include background texture, miss material-discriminative regions, or split an object into inconsistent parts. Downstream material and physical-property predictions can then change substantially while the system still reports a single confident value.

Mechanism or approach:
A mask-sensitivity calibrator that builds low-cost mask perturbation ensembles, summarizes material and property dispersion, and maps that dispersion into calibrated uncertainty intervals and object-level failure_warning tags.
Tune the calibrator to reduce property error and uncertainty miscalibration under plausible mask variation. Optimize mean property log MAE across mask samples, interval coverage loss, and a sensitivity-consistency loss that penalizes high-confidence outputs when mask-induced variance is high.

Experiment and implementation plan:
GroundingDINO + SAM single-mask pipeline; GroundingDINO + SAM2 single-mask pipeline; Mask2Former single-mask pipeline; GroundingDINO + SAM + CLIP/OpenSurfaces material lookup without uncertainty propagation
Indoor scene images from ScanNet, Matterport3D, or OpenRooms; Available ground-truth or pseudo object masks for mask_iou evaluation; Proxy material labels from OpenSurfaces/MINC-compatible mappings; Engineering property tables for material-to-property intervals; Optional ObjectFolder/ObjectFolder2.0 rendered or photographed objects with property annotations or proxy labels
generate_mask_ensemble.py to run SAM, SAM2, Mask2Former, prompt perturbations, and morphological mask variants; run_property_resolver_on_masks.py to compute material and property predictions for each mask sample; fit_mask_sensitivity_calibrator.py to map ensemble dispersion to confidence intervals; evaluate_mask_property_sensitivity.py to correlate mask_iou, material error, property error, and uncertainty; export_object_property_json.py to produce final structured JSON with evidence and warnings
object_recall; mask_iou; material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Use only one segmentation model instead of a multi-source mask ensemble; Use morphological perturbations only without SAM/SAM2/Mask2Former diversity; Use ensemble mean predictions without uncertainty calibration; Remove mask-sensitivity failure warnings; Replace masks with bounding boxes for all property predictions
Perturb masks mostly outside the object region to test whether gains come from meaningful object-boundary variation; Use identical duplicated masks as an ensemble, which should not improve calibration; Shuffle ensemble property predictions across objects before calibration; Calibrate uncertainty from object category frequency rather than mask-induced dispersion
Improve prediction_interval_coverage to within 5 percentage points of nominal 90% while keeping intervals narrower than a category-only prior baseline; Reduce calibration_error by at least 15% compared with single-mask CLIP/OpenSurfaces lookup; Reduce selective_risk by at least 10% at fixed 80% object coverage; Identify high-risk mask-sensitive objects with at least 70% precision in manual audit; Do not reduce object_recall by more than 1 percentage point relative to the best single-mask pipeline

Evidence paper IDs:
openalex:W4402500749; openalex:W7148178853; openalex:W4416850904; openalex:W4403323960; openalex:W4411238954; openalex:W4385327621; openalex:W2798280964

Risks, controls, or fallback:
Risk: mask perturbations may overestimate uncertainty for highly textured objects or underestimate it when all segmenters make the same systematic error. Fallback: combine mask-induced dispersion with material-posterior entropy and category-property prior width, and flag persistent disagreement between visual material evidence and object-category expectations instead of emitting a confident narrow interval.

---

## Item 8: HUM-cb06516dab

类型：`portfolio`

### Candidate A

Idea 1
Title:
Evidence-Gated Material-to-Property Retrieval for Masked Indoor Objects

Core proposal:
For each object, first obtain a box or mask with GroundingDINO/SAM-style segmentation, then compute material evidence only inside the mask using masked image crops and material-recognition prompts or classifiers. A calibrated evidence gate combines masked material scores, object category, mask area, texture/edge statistics, and agreement between multiple material prompts. Materials below the gate are not treated as observed facts; instead they contribute to a broader material-family distribution. Physical-property intervals are retrieved from ObjectFolder/ObjectFolder2.0-style physical-property sources and material-property tables only through the gated material distribution. If no material has sufficient localized evidence, the output interval is widened and tagged as visually underdetermined rather than returning an overconfident point estimate.

Motivation or baseline weakness:
Open-vocabulary VLM or CLIP-style material predictions can be driven by object semantics rather than localized surface evidence. This is risky for indoor categories such as chairs, cabinets, cushions, doors, and tabletops where the same category can be wood, metal, plastic, glass, fabric, or composites, and where single RGB images may not reveal hidden material composition.

Mechanism or approach:
A lightweight evidence-gating calibrator that takes masked material logits, category prior logits, prompt-agreement scores, mask quality features, and optional source-table disagreement features, and returns a calibrated distribution over material labels plus per-property interval weights.
Train the gate with material cross-entropy or soft-label KL divergence and interval negative log likelihood for density, Young's modulus, Poisson's ratio, hardness, and friction coefficient. Add a calibration penalty that increases loss when high-confidence material predictions disagree with masked visual evidence, and optimize interval coverage/width tradeoff on a held-out calibration split.

Experiment and implementation plan:
GroundingDINO + SAM + CLIP material prompt + material-property table lookup; GroundingDINO + SAM + OpenSurfaces/MINC-style material classifier + material-property table lookup; LLaVA or Qwen-VL direct JSON material and property prediction without localized evidence gating
Indoor RGB images with object boxes or masks, either annotated or produced by GroundingDINO/SAM-style models; Object-level material labels, weak material labels, or manually audited proxy labels compatible with OpenSurfaces/MINC-style material categories; Physical-property ranges aligned to material families using ObjectFolder/ObjectFolder2.0-style sources and curated material-property tables; Held-out manually audited indoor objects with visible-material labels, property intervals, and flags for hidden, composite, or visually ambiguous materials
run_detection_segmentation.py; extract_masked_material_scores.py; build_material_property_table.py; train_evidence_gate.py; predict_object_property_json.py; evaluate_material_and_property_intervals.py
object_recall; mask_iou; material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Remove masked visual evidence and use object-category prior only; Remove object-category prior and use masked material scores only; Replace the calibrated evidence gate with uncalibrated top-1 masked material prediction; Use point estimates instead of property intervals; Disable low-evidence widening and failure warnings
Randomly permute material-property table rows while preserving material frequencies; Use a same-size background crop instead of the object mask for material scoring; Evaluate on blank or texture-erased object crops with category labels retained; Force all objects of the same category to share one material prediction; Replace the true object mask with a shifted mask that has low IoU with the object
Improve material_macro_f1 by at least 5 percentage points over the masked CLIP prompt baseline on audited objects; Reduce density_log_mae and youngs_modulus_log_mae by at least 10 percent versus top-1 material table lookup; Achieve prediction_interval_coverage within 5 percentage points of the target coverage level on audited intervals; Lower selective_risk by at least 15 percent when abstaining or widening intervals on the lowest-confidence 20 percent of objects

Evidence paper IDs:
openalex:W4402427278; openalex:W4402500749; openalex:W3047386722; openalex:W2798280964; openalex:W3200689778; openalex:W4312347618

Risks, controls, or fallback:
Risk: single RGB views may not reveal internal structure, coatings, laminates, or composite construction, so localized visual evidence can still support the wrong physical material. Fallback: report conservative material-family mixtures and wider property intervals, expose material-evidence disagreement in the JSON evidence field, and set failure_warning to hidden_material_or_composite_uncertain when the gate rejects all specific materials.

---

Idea 2
Title:
Property-Interval Conformal Calibration for Single-Image Physical Estimates

Core proposal:
Wrap any frozen detection, segmentation, material-recognition, and property-estimation pipeline with split conformal calibration. The calibrator receives baseline point estimates or raw intervals and computes nonconformity scores on a calibration split with proxy or audited property intervals. Scores are conditioned by material family, object category, material confidence, visible texture strength, mask quality, and disagreement between property sources. At inference, the module outputs calibrated per-property intervals and an uncertainty tag, using broader fallback groups when a fine material/category group has insufficient calibration examples.

Motivation or baseline weakness:
Direct material-to-property lookup and VLM-generated numeric estimates can produce precise-looking point values even when the visible image supports only a material family or proxy label. This makes density, modulus, hardness, friction, and related estimates poorly calibrated, especially for hidden materials, rare materials, and object categories with large within-class variation.

Mechanism or approach:
A post-hoc grouped conformal interval calibrator that does not retrain the vision backbone and can wrap GroundingDINO/SAM2/Mask2Former-style masks, CLIP/MINC-style material recognizers, or VLM JSON predictors.
For each physical property, minimize interval width subject to empirical target coverage on a held-out calibration split. Use grouped conformal quantiles when group sample counts are sufficient, back off to material-family or global quantiles when sparse, and report unsupported-group warnings rather than extrapolating narrow intervals.

Experiment and implementation plan:
GroundingDINO + SAM2 + CLIP-style material prediction + material-property table point estimate; Mask2Former + MINC-style material classifier + uncalibrated material-property interval estimate; Qwen-VL direct property JSON prediction without residual-based conformal calibration
Calibration split with object masks or boxes, material labels or proxy material intervals, and audited examples where available; Physical-property ranges from ObjectFolder/ObjectFolder2.0-style physical-property sources and curated material-property tables; Indoor evaluation images with object-level detections or masks and material/category metadata sufficient for grouped calibration; A held-out test split separated by scene and object instance to avoid calibrating and testing on near-duplicate objects
collect_baseline_property_predictions.py; construct_proxy_interval_labels.py; fit_grouped_conformal_calibrator.py; apply_property_interval_calibration.py; evaluate_coverage_width_selective_risk.py
prediction_interval_coverage; calibration_error; selective_risk; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; material_top3_accuracy
Global conformal calibration without material or category grouping; Group only by material family; Group only by object category; Use VLM self-reported confidence instead of calibration residuals; Use uncalibrated source-table intervals; Disable sparse-group backoff and force fine-grained group quantiles
Calibrate on shuffled property labels while preserving material/category frequencies; Calibrate on one set of material families and test on held-out unrelated material families without fallback grouping; Use a constant-width interval for every property and object; Remove source-table disagreement features from the grouping and nonconformity model; Tune conformal quantiles on the test split to detect leakage-sensitive gains
Reach at least 90 percent empirical coverage for nominal 90 percent intervals on density and Young's modulus; Reduce calibration_error by at least 25 percent versus uncalibrated baseline intervals; Maintain median interval width no more than 1.5 times the strongest uncalibrated table-interval baseline at matched coverage; Improve selective_risk by at least 10 percent at 80 percent retained-object coverage; Maintain coverage within 7 percentage points of nominal for the largest material-family groups

Evidence paper IDs:
openalex:W4416850904; openalex:W4403323960; openalex:W4385327621; openalex:W4391722892; openalex:W4327630646; openalex:W4312347618

Risks, controls, or fallback:
Risk: proxy labels and material-property tables may be noisy, and conformal guarantees can degrade under distribution shift or sparse rare-material groups such as composites, coated metal, laminated wood, and foam. Fallback: back off from fine groups to broader material-family or global calibration, widen intervals using source-table disagreement, and set failure_warning when an object falls outside calibrated material/category support.

---

Idea 3
Title:
Mask-Consistency Self-Check for Object-Level Property JSON Reliability

Core proposal:
Before property prediction, generate multiple plausible spatial supports for each detected object: the original mask, alternative promptable masks, box crops, eroded/dilated masks, boundary-trimmed masks, and visible part crops. Run the same material and property estimator on each support. A mask-consistency scorer measures agreement of material distributions, property intervals, mask IoU, mask area change, and part-to-whole consistency. Objects with stable predictions pass through with normal calibrated intervals; unstable objects receive wider intervals and failure_warning set to mixed_material_or_mask_uncertain. The self-check is applied before JSON aggregation so downstream consumers know whether the object-level estimate is mask-sensitive.

Motivation or baseline weakness:
Promptable or open-vocabulary segmentation with GroundingDINO, SAM, SAM2, or Mask2Former can return masks that include background, merge neighboring objects, omit parts, or isolate a salient subpart rather than the full object. Material and physical-property estimates derived from one mask can therefore be unstable while the final JSON still appears complete and object-level.

Mechanism or approach:
A mask-consistency scorer that aggregates material logits, property intervals, mask IoU/area features, and perturbation metadata across candidate masks and crops, then outputs a reliability score and interval-widening factor.
Learn or tune a reliability score that predicts downstream material/property error from perturbation instability. Penalize high material entropy, large property-interval variance, low agreement between whole-object and part-crop predictions, and low IoU among high-confidence masks, while avoiding penalties for benign boundary perturbations that do not change predictions.

Experiment and implementation plan:
GroundingDINO + SAM single-mask property pipeline; GroundingDINO + SAM2 single-mask property pipeline; Mask2Former single-mask property pipeline
Indoor RGB images with object boxes or masks produced by GroundingDINO, SAM, SAM2, or Mask2Former-style systems; Material labels, proxy labels, or manually audited material annotations for evaluating whether mask instability corresponds to material errors; Property ranges from ObjectFolder/ObjectFolder2.0-style sources and curated material-property tables; A manually audited subset labeling mask failure types such as background inclusion, merged objects, missing parts, and mixed visible materials
generate_candidate_masks.py; perturb_masks_and_boxes.py; predict_materials_per_mask_variant.py; compute_mask_consistency_score.py; aggregate_property_json_with_warnings.py; evaluate_stability_and_downstream_error.py
object_recall; mask_iou; material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Use only the highest-confidence mask; Use box crop instead of mask crop; Remove erosion and dilation perturbations; Remove part-crop consistency check; Use consistency score only for warning without widening intervals; Aggregate all mask variants by simple averaging without reliability scoring
Apply the perturbation pipeline to background regions rather than object masks; Randomly choose one candidate mask without consistency scoring; Force all candidate masks to share the same material label before aggregation; Evaluate on intentionally merged neighboring-object masks; Use duplicate copies of the same mask as variants to confirm that apparent gains require real perturbation diversity
Reduce material prediction variance across mask variants by at least 20 percent versus the single-mask baseline on objects with ambiguous boundaries; Improve density_log_mae and friction_coefficient_mae by at least 8 percent on audited objects with multiple visible materials or cluttered boundaries; Achieve lower selective_risk than confidence-only filtering at the same retained-object rate; Increase failure_warning precision for mask-related errors by at least 15 percentage points on manually audited cases; Maintain material_macro_f1 within 2 percentage points of the single-mask baseline on audited uniform-material objects

Evidence paper IDs:
openalex:W4402500749; openalex:W7148178853; openalex:W4416850904; openalex:W4411238954; openalex:W4385327621; openalex:W2798280964

Risks, controls, or fallback:
Risk: generating and evaluating multiple mask variants increases compute and may over-flag uniform objects with weak texture or reflective surfaces. Fallback: run the self-check only for low-confidence masks, small objects, reflective objects, masks with unusual area changes, and categories with common multi-material construction; otherwise pass through the single-mask baseline with normal calibrated intervals.

### Candidate B

Idea 1
Title:
Material Interval Retrieval Head for Object-Level Property Prediction

Core proposal:
Add a retrieval-and-interval head that treats each object as a distribution over candidate material-table entries rather than a single material class. For each detected object, the module scores table entries using masked crop appearance, object category, predicted material logits, and optional scene context. It then aggregates the retrieved entries into per-property predictive distributions by weighting each entry's tabulated range and subtype prior. The output is a structured object record containing top-k materials, mixture weights, point estimates, prediction intervals, and a low-evidence flag when the visual signal is insufficient to narrow the mixture.

Motivation or baseline weakness:
Detection/segmentation plus CLIP-style material recognition can assign a single coarse material label, but physical properties depend on material subtypes, coatings, composites, and manufacturing variation that are often not identifiable from a single RGB view. Mapping one predicted label to one table median therefore produces overconfident and brittle property estimates.

Mechanism or approach:
A frozen-encoder adapter with a small MLP or cross-attention scorer over candidate material-table entries. Inputs are object crop embedding, masked texture/color embedding, object category embedding, material-recognizer logits, and optional room-context embedding; outputs are candidate scores and per-property interval parameters.
Train the adapter with a joint ranking and interval objective. Use cross-entropy or pairwise ranking loss for proxy material labels, negative log likelihood or pinball loss for interval-valued property targets, and a calibration penalty for under-covered intervals. Property targets are represented in log space for positive scale-sensitive quantities such as density and Young's modulus, and in bounded or ordinal parameterizations for coefficients or hardness when appropriate.

Experiment and implementation plan:
GroundingDINO+SAM+CLIP material label mapped to median property table values; Mask2Former+MINC material classifier mapped to median property table values; Object category prior mapped to median property table values; LLaVA or Qwen-VL prompted to output object material and property estimates
Indoor images with object masks or boxes from ScanNet, Matterport3D, or OpenRooms; Object category labels from detector outputs or dataset annotations; Proxy material labels aligned to OpenSurfaces or MINC-style categories; Engineering material property tables with density, Young's modulus, Poisson's ratio, hardness, and friction coefficient ranges; A hand-built taxonomy mapping coarse visual material labels to one or more table entries; Optional synthetic or scanned object exemplars with known material labels for object-crop augmentation
run_object_detection_and_segmentation.py; extract_masked_object_embeddings.py; build_material_property_index.py; align_visual_material_taxonomy_to_tables.py; train_material_interval_retriever.py; calibrate_prediction_intervals.py; evaluate_object_property_json.py
material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; mean_interval_width; calibration_error; selective_risk; json_schema_validity
Remove object category embedding and use only masked crop appearance; Remove material-recognizer logits and retrieve directly from image embeddings; Remove scene-context embedding; Use single top-1 material instead of top-k mixture aggregation; Replace learned retriever with CLIP nearest-neighbor retrieval; Train with point-valued targets only instead of interval-valued targets; Use table ranges without learned calibration
Randomly shuffle property ranges across material-table entries while preserving material names; Randomly shuffle material labels during retriever training; Use only object category priors with no image crop or mask evidence; Use bounding-box crops without masks to test background leakage; Evaluate the same property head on deliberately irrelevant targets such as random numeric labels to check that it cannot manufacture apparent physical-property signal
Improve material_top3_accuracy over CLIP-to-table baseline by at least 5 absolute percentage points; Reduce density_log_mae by at least 10 percent relative to category-prior median baseline; Reduce youngs_modulus_log_mae by at least 10 percent relative to CLIP top-1 material mapping; Achieve prediction_interval_coverage within 5 percentage points of nominal 90 percent intervals; Keep mean interval width at matched coverage lower than the unconditioned material-table range baseline; Maintain object-level JSON schema validity above 98 percent on the evaluation split

Risks, controls, or fallback:
Risk: proxy material supervision and table mappings may be too coarse to support accurate point-property prediction from RGB. Fallback: emphasize calibrated retrieval, top-k material mixtures, selective prediction, and interval coverage. If point errors do not improve, report the system as an uncertainty-aware material-to-property indexer rather than a precise estimator.

---

Idea 2
Title:
Scene-Context Constrained Material Disambiguation for Similar-Looking Objects

Core proposal:
Introduce a context-consistency graph that re-ranks, but does not replace, per-object visual material candidates. Each object node starts with unary material scores from a frozen visual recognizer. Learned factors use object category, room type, support/contact relations, surface location, and neighboring object categories to adjust only the relative scores among plausible candidates. A gating term limits the context update when visual confidence is high or when context features are missing, preventing the graph from forcing a stereotyped material assignment.

Motivation or baseline weakness:
Object crops alone confuse visually similar materials such as laminated wood, painted metal, plastic, ceramic, and stone. Independent per-object classification ignores room type, object function, support relations, and co-occurring objects that can help disambiguate materials, but unconstrained context use can also hallucinate common materials when visual evidence disagrees.

Mechanism or approach:
A lightweight factor graph or graph neural adapter with frozen visual unary scores, learned context factors, and a confidence gate. The module outputs adjusted material distributions and downstream property intervals derived from the adjusted material mixture.
Train the graph with material classification loss on proxy labels, property regression or interval loss after material-to-property mapping, and a conservatism regularizer that penalizes large context-driven score changes when visual evidence is confident. Context factors are learned from training scenes but evaluated with held-out rooms and shuffled-context controls to separate genuine contextual disambiguation from dataset priors.

Experiment and implementation plan:
GroundingDINO+SAM with independent CLIP material classification per object; Mask2Former with independent MINC/OpenSurfaces material classifier per object; Object category and room-type prior without image evidence; VLM prompt baseline that predicts each object's material and properties without explicit context graph
Indoor scene images with object annotations from ScanNet, Matterport3D, or OpenRooms; Object masks or boxes and categories from GroundingDINO+SAM, SAM2, or Mask2Former; Proxy material labels aligned to a fixed visual-material taxonomy; Room type, support/contact relations, surface location, and object co-occurrence metadata when available; Engineering property tables aligned to material categories; A split design that holds out scenes or room instances to test context generalization
infer_objects_and_masks.py; compute_object_context_features.py; construct_scene_context_graphs.py; train_context_material_graph.py; map_materials_to_property_intervals.py; evaluate_context_vs_independent.py; export_structured_object_json.py
object_recall; mask_iou; material_accuracy; material_macro_f1; material_top3_accuracy; ambiguous_group_macro_f1; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; selective_risk
Unary visual material scores only with no context factors; Category-context factors only, excluding co-occurrence and relation factors; Room-type factors only; Support-relation and surface-location factors only; Graph inference with learned factors versus hand-coded priors; Remove the confidence gate and allow unrestricted context re-ranking; Oracle masks versus predicted masks to separate segmentation errors from material reasoning errors
Randomly permute room labels across images; Randomly permute object co-occurrence edges while preserving graph size; Randomly permute support/contact relations while preserving object categories; Apply the context graph to cropped single-object images where relational context should not help; Evaluate on visually distinctive material classes where context should make little or no change; Train context factors with image evidence removed to quantify how much gain comes from dataset priors alone
Improve material_macro_f1 for predefined ambiguous material groups by at least 5 absolute percentage points over independent object classification; Reduce youngs_modulus_log_mae by at least 8 percent on objects whose top-2 visual material candidates have strongly different stiffness; Do not reduce overall material_accuracy by more than 1 percentage point on visually distinctive materials; Show that shuffled-context negative controls lose at least half of the observed ambiguous-group gain; Maintain or improve selective_risk at 70 percent prediction coverage relative to the independent baseline; Keep context-induced label changes below a preset rate for high-confidence visual predictions unless they improve validation likelihood

Risks, controls, or fallback:
Risk: context priors may overfit dataset-specific room layouts and amplify stereotyped material assignments. Fallback: use the graph only as a calibrated re-ranking term behind a confidence gate; when visual and contextual evidence disagree, output a broader material mixture and higher uncertainty rather than forcing a single context-preferred material.

---

Idea 3
Title:
Visibility-Aware Uncertainty Calibration for Hidden Physical Properties

Core proposal:
Add a visibility-aware uncertainty calibrator on top of an existing object material-to-property pipeline. The calibrator estimates per-object and per-property uncertainty from segmentation quality, occlusion, visible area, viewpoint, blur, texture evidence strength, material-distribution entropy, top-k material disagreement, object category variability, and distance from the training feature distribution. It converts raw point predictions into calibrated intervals and emits failure-warning or abstention flags when the interval would be too wide for useful prediction.

Motivation or baseline weakness:
Standard material-to-property pipelines output overconfident point estimates even though single-view RGB cannot reveal internal structure, coatings, composites, moisture, wear, or exact manufacturing material. This is especially problematic when masks are poor, objects are occluded, surfaces are glossy or textureless, or the predicted material distribution is multi-modal.

Mechanism or approach:
A small multi-property uncertainty head trained on frozen pipeline features, followed by a split-calibration wrapper that converts uncertainty scores into calibrated prediction intervals. The module does not change the base material or property predictor; it only calibrates and flags predictions.
Train the uncertainty head to predict absolute residuals, quantile residuals, or normalized interval widths for each physical property using a held-out training split. Apply split calibration on a separate calibration split to set per-property interval thresholds. Optimize selective risk by ranking predictions according to calibrated uncertainty and abstaining or warning when expected error is high. Use log residuals for positive-valued properties and bounded residual transforms for coefficients where needed.

Experiment and implementation plan:
GroundingDINO+SAM+CLIP material-to-property point estimates with fixed global uncertainty; Mask2Former+MINC material-to-property point estimates with fixed intervals per material; Material-entropy-only uncertainty score without visibility features; VLM prompted confidence scores without recalibration
Indoor images with predicted and/or ground-truth object masks from ScanNet, Matterport3D, or OpenRooms; Material proxy labels aligned to a fixed material taxonomy; Engineering material property tables with ranges and variability statistics; Base model predictions, residuals, material logits, and object-level visibility features; Held-out calibration split with proxy material-property targets; Optional synthetic occlusion, blur, crop truncation, and mask-corruption augmentations for stress testing
generate_base_property_predictions.py; extract_visibility_and_ambiguity_features.py; train_uncertainty_head.py; run_split_calibration.py; evaluate_calibration_and_selective_risk.py; stress_test_visibility_corruptions.py; generate_failure_warning_json.py
prediction_interval_coverage; mean_interval_width; calibration_error; selective_risk; failure_warning_precision; failure_warning_recall; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; material_top3_accuracy; object_recall; mask_iou
Fixed global interval width instead of object-specific uncertainty; Material-entropy-only uncertainty without visibility features; Visibility-features-only uncertainty without material ambiguity; No split-calibration wrapper; Separate uncertainty heads per property versus shared multi-property uncertainty head; Remove out-of-distribution feature distance; Calibration using predicted masks versus oracle masks; Train without synthetic visibility corruptions and test on corrupted inputs
Randomly shuffle residual targets during uncertainty-head training; Use object_id hashes, image filenames, or dataset indices as uncertainty features to check for leakage; Evaluate calibration after artificially corrupting masks without exposing corruption indicators to the uncertainty head; Randomly permute uncertainty scores before selective-risk evaluation; Compare against prompted VLM confidence scores without recalibration; Train the uncertainty head on one property's residuals and evaluate it on an unrelated property's residuals to test whether it learned meaningful uncertainty rather than generic difficulty
Achieve empirical 90 percent prediction_interval_coverage between 85 and 95 percent for at least four of five physical properties; Reduce calibration_error by at least 20 percent relative to fixed material-range intervals; Reduce selective_risk by at least 15 percent at 70 percent prediction coverage; Failure_warning precision for high-error cases exceeds the uncalibrated confidence baseline by at least 10 absolute percentage points; Do not increase mean interval width by more than 25 percent relative to fixed material-range intervals at matched coverage; Under mask or occlusion corruption, increase warning rate and interval width monotonically with corruption severity

Risks, controls, or fallback:
Risk: intervals calibrated on proxy labels may not transfer to real physical ground truth, and visibility features may correlate with dataset artifacts rather than true uncertainty. Fallback: report calibration separately for clean, ambiguous, and corrupted subsets; if calibrated intervals become too wide, prioritize abstention and explicit failure warnings over narrow but misleading physical-property estimates.

---

## Item 9: HUM-6b77d8b144

类型：`single_idea`

### Candidate A

Title:
Mask-Localized Material Mixture Retrieval for Property Intervals

Core proposal:
Add a lightweight mask-localized material-mixture retriever that samples multiple masked visual patches per detected object, predicts a calibrated distribution over visible material components, and maps the posterior mixture to table-backed physical-property intervals. ObjectFolder/ObjectFolder2.0 are used only as object/category and multisensory property priors where available, while OpenSurfaces/MINC-style labels supervise visible material recognition; outputs are explicitly labeled as visible-surface-informed property intervals, not exact bulk measurements.

Motivation or baseline weakness:
CLIP/OpenSurfaces/MINC-style material recognition can assign a single semantic material to an object crop even when the visible evidence is localized, mixed, or surface-only; this propagates overconfident point estimates for density, Young's modulus, Poisson's ratio, hardness, and friction coefficient from 2D indoor images where hidden composition is often unobservable.

Mechanism or approach:
A frozen-encoder adapter with four components: masked patch sampler, material-mixture softmax head, property-interval aggregator over material/property tables and object priors, and JSON uncertainty formatter that emits interval bounds, posterior entropy, and failure_warning flags.
Minimize weak-label multiple-instance material loss over masked patches plus interval negative log likelihood for proxy physical-property intervals. Add a coverage-aware width regularizer that penalizes intervals that are too narrow on validation proxy labels while avoiding unbounded intervals through a validation-tuned maximum-width penalty.

Experiment and implementation plan:
GroundingDINO + SAM + CLIP single-material lookup; GroundingDINO + SAM2 + OpenSurfaces classifier + property-table lookup; Mask2Former + MINC classifier + property-table lookup
Indoor RGB images with object masks or boxes produced by GroundingDINO, SAM, SAM2, or Mask2Former; Object-level or region-level visible material labels or weak material tags aligned to OpenSurfaces and MINC categories; Object-category to material/property priors derived from ObjectFolder and ObjectFolder2.0 where category overlap exists; A versioned material-property table converted into density, Young's modulus, Poisson's ratio, hardness, and friction-coefficient intervals with source identifiers and unit normalization; Held-out validation objects with proxy material/property intervals for calibration and negative-control evaluation
run_detection_segmentation.py; extract_masked_object_patches.py; train_material_mixture_adapter.py; build_property_interval_table.py; evaluate_object_property_json.py
material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error
Replace mixture distribution with top-1 material lookup; Use whole-object crop instead of masked patch sampling; Remove object-category prior from the property aggregator; Use point estimates instead of intervals; Train with only visual features and no table-derived property constraints
Shuffle material-property table rows before aggregation; Evaluate on background masks treated as objects; Use random masks with correct object category labels; Use object category only without visible material cues; Replace masked patch features with patches from another object of the same category
Improve material_macro_f1 by at least 5 percentage points over top-1 CLIP/OpenSurfaces/MINC lookup on held-out indoor objects; Reduce density_log_mae and youngs_modulus_log_mae by at least 10 percent relative to single-material lookup on proxy interval midpoints; Achieve prediction_interval_coverage between 85 percent and 95 percent for nominal 90 percent proxy intervals; Reduce calibration_error by at least 20 percent relative to uncalibrated single-material lookup; Fail negative controls by showing coverage or accuracy drops when table rows, masks, or patch evidence are randomized

Evidence paper IDs:
openalex:W4402500749; openalex:W2798280964; openalex:W3012463097; openalex:W3200689778; openalex:W4312347618

Risks, controls, or fallback:
Risk: RGB-visible surfaces may not reveal bulk composition, so mixture estimates may still be wrong for veneered, painted, coated, hollow, or composite objects. Fallback: explicitly output wider visible-surface-informed intervals and a failure_warning when visible material evidence conflicts with object-category priors, when the material posterior entropy exceeds a validation-tuned threshold, or when the object category has no reliable overlap with ObjectFolder/ObjectFolder2.0 priors.

### Candidate B

Title:
Mask-Localized Material Mixture Retrieval for Property Intervals

Core proposal:
Use object masks to sample multiple localized visual patches per object, retrieve visually similar material examples, and estimate a calibrated distribution over visible material components. Convert this material-mixture posterior into physical-property intervals using ObjectFolder/ObjectFolder2.0 category-material priors and engineering material-property tables, rather than emitting a single material-to-property lookup.

Motivation or baseline weakness:
CLIP/OpenSurfaces/MINC-style material recognition often collapses an object crop to one semantic material even when the visible evidence is localized, mixed, textured, coated, or only surface-level. This single-material decision can produce overconfident point estimates for density, Young's modulus, Poisson's ratio, hardness, and friction coefficient.

Mechanism or approach:
A frozen-encoder adapter with four parts: masked patch sampler, material-mixture prediction head, table-based property interval aggregator, and structured JSON uncertainty formatter.
Train the adapter with material cross-entropy when labels are available and weak multiple-instance material loss when only image- or object-level tags are available. Add interval negative log likelihood or quantile loss for proxy physical-property intervals, plus a coverage penalty for intervals that are too narrow on validation proxy labels.

Experiment and implementation plan:
GroundingDINO + SAM + CLIP single-material lookup; GroundingDINO + SAM2 + OpenSurfaces classifier + property-table lookup; Mask2Former + MINC classifier + property-table lookup
Indoor RGB images with object masks or boxes from ScanNet, Matterport3D, or OpenRooms; Material labels or weak material tags from OpenSurfaces and MINC; Object-category to material priors from ObjectFolder and ObjectFolder2.0; Engineering material-property tables normalized to density, Young's modulus, Poisson's ratio, hardness, and friction-coefficient intervals
run_detection_segmentation.py; extract_masked_object_patches.py; train_material_mixture_adapter.py; build_property_interval_table.py; evaluate_object_property_json.py
material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error
Replace the material-mixture posterior with a top-1 material lookup; Use the whole-object crop instead of localized masked patch sampling; Remove object-category priors from the property interval aggregator; Emit point estimates instead of calibrated intervals; Train only on visual material labels without table-derived property constraints
Shuffle material-property table rows before aggregation; Evaluate background masks as if they were objects; Use random masks while keeping the correct object category label; Use object category only without visible material features
Improve material_macro_f1 by at least 5 percentage points over the best top-1 CLIP/OpenSurfaces/MINC lookup baseline on held-out indoor objects; Reduce density_log_mae and youngs_modulus_log_mae by at least 10 percent relative to single-material lookup; Achieve prediction_interval_coverage between 85 percent and 95 percent for nominal 90 percent intervals; Lower selective_risk relative to the direct baseline at 70 percent retained predictions

Evidence paper IDs:
openalex:W4402500749; openalex:W2798280964; openalex:W3012463097; openalex:W3200689778; openalex:W4312347618

Risks, controls, or fallback:
Risk: RGB-visible surfaces may not reveal bulk composition, especially for painted, veneered, coated, laminated, hollow, or composite objects. Fallback: widen intervals and emit a failure_warning when visible material evidence conflicts with object-category priors, the material posterior has high entropy, or the mask covers only a small or low-texture region of the object.

---

## Item 10: HUM-b977c57de7

类型：`portfolio`

### Candidate A

Idea 1
Title:
Material-Conditioned Interval Property Lookup for Segmented Indoor Objects

Core proposal:
Add a lightweight material-to-property interval mapper that converts top-k localized material predictions and object category priors into interval-valued physical-property predictions rather than overconfident point estimates. For each object mask, the module fuses calibrated visual material probabilities with category-conditioned priors from curated material-property tables and ObjectFolder/ObjectFolder2.0 metadata where available. It emits median estimates, lower/upper intervals, confidence, source tags, and failure warnings when the material posterior is diffuse, the object category conflicts with the material hypothesis, or the lookup table lacks adequate support.

Motivation or baseline weakness:
GroundingDINO with SAM/SAM2 can localize visible objects, but the pipeline has no calibrated bridge from object-localized material cues to physical-property ranges. CLIP/OpenSurfaces/MINC-style material recognition can be prompt-sensitive or ambiguous, and single RGB images often cannot support exact density, modulus, hardness, or friction estimates for hidden or composite materials.

Mechanism or approach:
A frozen-backbone material posterior calibrator plus deterministic property-table aggregator: temperature-scaled material logits from masked object crops are mapped to normalized material names and then to property intervals using curated material-property tables and ObjectFolder/ObjectFolder2.0 priors, with no large-scale end-to-end training.
Minimize interval-aware negative log likelihood and log-space absolute error for density and Young's modulus under weak or proxy labels, while enforcing target prediction-interval coverage for all physical-property outputs through calibration on a held-out validation split.

Experiment and implementation plan:
GroundingDINO; SAM; SAM2; CLIP; OpenSurfaces; MINC; ObjectFolder; ObjectFolder2.0
Indoor images with object masks or boxes from an indoor-scene source such as ScanNet, Matterport3D, or OpenRooms; Material labels or proxy labels aligned to object crops using OpenSurfaces/MINC-style material categories; Object category labels aligned to detected masks; Curated material-property tables containing density, Young's modulus, Poisson's ratio, hardness, and friction coefficient ranges with normalized units; ObjectFolder/ObjectFolder2.0 object-material-property metadata where available; Held-out validation split for material-logit temperature scaling and interval calibration
run_detection_segmentation.py to produce object_id, category, mask_or_box using GroundingDINO plus SAM/SAM2; extract_masked_object_crops.py to create masked object crops and optional local context crops; predict_material_topk.py to obtain calibrated material posteriors from frozen CLIP/OpenSurfaces/MINC-style material models; build_property_table_index.py to normalize material names, aliases, property units, and source tags; aggregate_property_intervals.py to combine material posteriors, object-category priors, and table ranges into structured JSON predictions; evaluate_interval_properties.py to compute material metrics, property errors, interval coverage, calibration error, abstention rate, and selective risk
object_recall; mask_iou; material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Remove object-category prior and use material posterior only; Use point estimates from the most likely material instead of posterior-weighted interval aggregation; Use uncalibrated CLIP/OpenSurfaces/MINC logits instead of temperature-scaled material probabilities; Use mask crop only versus mask crop plus surrounding scene context; Replace curated table intervals with ObjectFolder/ObjectFolder2.0-only priors where metadata exists; Disable low-observability and table-missing failure warnings
Shuffle material labels across object crops before property lookup; Assign generic category-level property intervals without visual material evidence; Use whole-image material prediction instead of object-mask-localized prediction; Evaluate categories or materials absent from the property table to verify failure_warning activation; Randomize material-property table rows while preserving material label frequencies
Improve material_top3_accuracy over a frozen CLIP-only object-crop baseline by at least 5 percentage points after calibration; Reduce density_log_mae and youngs_modulus_log_mae by at least 10% relative to most-likely-material table lookup; Achieve prediction_interval_coverage within 5 percentage points of the nominal 90% interval target; Reduce selective_risk at 70% retained predictions relative to an uncalibrated material-posterior baseline; Failure if nominal 90% interval coverage is below 75% or property errors do not beat generic category priors

Evidence paper IDs:
openalex:W4402427278; openalex:W4402500749; openalex:W4411238954; openalex:W2798280964; openalex:W3012463097; openalex:W2895238724; openalex:W3200689778; openalex:W4312347618

Risks, controls, or fallback:
Risk: visible texture may not identify hidden composition, for example veneer, painted metal, foam-filled furniture, or composite objects. Fallback: widen intervals, mark low-observability or table-missing failure_warning fields, and report category-level priors rather than unsupported precise values.

---

Idea 2
Title:
Evidence-Gated VLM Verification for Object Material and Property JSON

Core proposal:
Introduce an evidence-gating layer that requires every accepted material/property prediction to be backed by object-localized evidence: masked crop appearance, nearby context, object category, material candidate, and property-source tag. The VLM is used only as a verifier or reranker over candidate material-property hypotheses generated by a frozen detector, segmenter, material model, and table lookup; it is not allowed to invent numeric property values. Predictions are rejected or downweighted when the verifier cannot select a candidate using localized visual cues or when prompt-consistency checks disagree.

Motivation or baseline weakness:
Vision-language models such as LLaVA, BLIP-2, and Qwen-VL can provide contextual reasoning, but their material and physical-property claims may be unsupported by localized visual evidence and sensitive to prompts. This can produce plausible but unverified JSON outputs, especially when asked to infer numerical properties directly from a single RGB image.

Mechanism or approach:
A constrained hypothesis verifier that scores candidate JSON rows using masked object crops, context panels, explicit candidate lists, and property-source tags. The verifier outputs a candidate rank, evidence cue labels, and an abstention score; numeric property intervals are copied only from the candidate table row and never generated free-form by the VLM.
Maximize material reranking accuracy and minimize selective physical-property risk subject to an acceptance constraint: each retained prediction must include at least one localized visual cue and one property-source cue. Calibrate the evidence-score threshold on a validation split to abstain when verifier confidence or prompt consistency is low.

Experiment and implementation plan:
GroundingDINO; SAM; Mask2Former; CLIP; OpenSurfaces; MINC; BLIP-2; LLaVA; Qwen-VL; ObjectFolder; ObjectFolder2.0
Indoor scene images from a source such as ScanNet, Matterport3D, or OpenRooms; Object masks or boxes from GroundingDINO plus SAM/SAM2 or Mask2Former; Candidate material labels from CLIP/OpenSurfaces/MINC-style material models; Candidate physical-property intervals from curated material-property tables and ObjectFolder/ObjectFolder2.0 metadata where available; A validation split with human-checked material labels or proxy labels for verifier calibration; A small audit subset with human judgments of whether cited evidence is actually localized to the target object
generate_candidate_json.py to create top-k material and property hypotheses per object without VLM-generated numeric values; render_evidence_panels.py to create object crop, masked image, context crop, mask overlay, and candidate list for VLM verification; vlm_verify_candidates.py to query BLIP-2/LLaVA/Qwen-VL with constrained evidence prompts and fixed output schema; check_prompt_consistency.py to run prompt variants and measure candidate-rank agreement; calibrate_acceptance_threshold.py to tune evidence-score and consistency thresholds on validation data; evaluate_verified_json.py to score accepted, rejected, and all predictions, including human-audited unsupported-evidence errors
material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Use VLM free-form prediction instead of candidate verification; Remove localized mask crop and give only full-image context; Remove property-source text from the verifier prompt; Use a single prompt versus prompt ensemble with consistency voting; Use verifier score without calibration versus calibrated abstention; Allow VLM-generated numeric properties versus table-copied property intervals only
Give the VLM candidates from a different object mask in the same image; Randomize candidate material-property pairings while keeping object category fixed; Ask the VLM to output numerical properties without table candidates and verify that these are not accepted; Use a background crop instead of the object crop to test evidence leakage; Swap the property-source tags across candidate rows to test whether the verifier over-trusts source text
Improve material_top1_accuracy or material_macro_f1 by at least 5 percentage points over CLIP/OpenSurfaces/MINC candidate ranking alone; Reduce selective_risk at 60% retained objects by at least 15% compared with no VLM evidence gate; Maintain prediction_interval_coverage within 5 percentage points of target coverage after abstention; Decrease unsupported-evidence errors in a human audit by at least 30% relative to free-form VLM JSON; Failure if VLM verification improves fluency but not material accuracy, calibration error, selective risk, or audited evidence support

Evidence paper IDs:
openalex:W4399597788; openalex:W4402155831; openalex:W4385327621; openalex:W4392222076; openalex:W4402427278; openalex:W4402500749; openalex:W4411238954; openalex:W3200689778; openalex:W4312347618

Risks, controls, or fallback:
Risk: the VLM may rationalize incorrect candidates, rely on object-category stereotypes, or follow misleading source text rather than visual cues. Fallback: restrict VLM output to reranking and abstention, log evidence text separately from numeric property values, reject prompt-inconsistent cases, and default to calibrated material-model plus table intervals when verifier consistency is low.

---

Idea 3
Title:
Segmentation-Uncertainty Propagation for Physical Property Confidence

Core proposal:
Sample multiple plausible masks or boxes per detected object using detector proposals, SAM/SAM2 prompt variants, and Mask2Former alternatives, then propagate the resulting variation through material classification and property lookup. The final object JSON reports material distributions, property intervals, mask-instability scores, evidence diversity, and a failure warning when predictions are unstable across masks or when alternative masks imply incompatible materials.

Motivation or baseline weakness:
Promptable segmentation with SAM/SAM2 or detection-driven masks can vary with prompts, occlusions, and object boundaries. Downstream material and physical-property estimates often ignore this mask uncertainty, producing overconfident predictions for partially visible, small, reflective, or poorly segmented objects.

Mechanism or approach:
A mask-ensemble uncertainty propagator that perturbs points and boxes, collects alternative masks, computes material/property predictions for each mask, filters degenerate masks, and aggregates the resulting predictions into calibrated confidence intervals and instability scores.
Estimate predictive uncertainty by marginalizing over segmentation hypotheses and calibrate object-level property intervals so that objects with unstable masks have wider intervals and higher abstention probability, while stable masks retain narrow intervals when material predictions agree.

Experiment and implementation plan:
GroundingDINO; SAM; SAM2; Mask2Former; CLIP; OpenSurfaces; MINC; ObjectFolder; ObjectFolder2.0
Indoor RGB images with visible objects from a source such as ScanNet, Matterport3D, or OpenRooms; Reference object masks where available for mask_iou evaluation; Object category annotations or detector-generated categories; Material proxy labels from OpenSurfaces/MINC-style datasets or a manually validated subset; Physical-property proxy intervals from ObjectFolder/ObjectFolder2.0 metadata and curated material-property tables; Validation split for calibrating the relationship between mask instability, material disagreement, and interval width
generate_mask_ensemble.py to create box-, point-, and mask-prompt variants from GroundingDINO/SAM/SAM2/Mask2Former outputs; filter_degenerate_masks.py to remove empty masks, near-duplicates, and masks dominated by background; score_mask_quality.py to compute mask_iou where reference masks exist and mask stability otherwise; predict_properties_per_mask.py to run material prediction and property lookup for each retained mask sample; aggregate_uncertainty.py to combine material and property distributions across masks using posterior-weighted intervals and instability features; evaluate_uncertainty_propagation.py to compute accuracy, property error, coverage, calibration error, abstention rate, and selective risk
object_recall; mask_iou; material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Single best SAM mask versus mask ensemble; SAM-only ensemble versus GroundingDINO plus SAM/SAM2 plus Mask2Former ensemble; Aggregate by mean material posterior versus worst-case interval union; Remove mask-instability feature from confidence calibration; Use object crop bounding box instead of precise mask crops; Disable degenerate-mask filtering before uncertainty aggregation
Randomly jitter masks far outside the object to verify uncertainty increases and confidence decreases; Use duplicate identical masks to confirm no artificial uncertainty gain; Swap mask ensembles between objects of the same category; Evaluate fully visible large objects separately from small or occluded objects to check whether uncertainty is selectively useful; Randomly permute per-mask material predictions before aggregation to verify calibration detects incoherent evidence
Improve prediction_interval_coverage by at least 10 percentage points over single-mask property prediction at similar average interval width; Reduce calibration_error by at least 15% compared with single-best-mask confidence; Maintain material_accuracy within 2 percentage points of the single-mask baseline while improving selective_risk; Show higher uncertainty for low-mask_iou or high-occlusion objects than for stable high-mask_iou objects; Failure if mask ensembling only widens all intervals uniformly without improving coverage, calibration error, or selective risk

Evidence paper IDs:
openalex:W4402500749; openalex:W7148178853; openalex:W4416850904; openalex:W4403323960; openalex:W4411238954; openalex:W3022851742; openalex:W4391809438; openalex:W3200689778; openalex:W4312347618

Risks, controls, or fallback:
Risk: mask ensembles may be computationally expensive and may degrade material recognition by including background or neighboring objects. Fallback: cap the ensemble to a small diverse set of masks, skip ensembling for high-stability easy objects, filter degenerate masks, and widen intervals only when material or property predictions actually vary across plausible masks.

### Candidate B

Idea 1
Title:
Context-Conditioned Material Interval Mapper for Object Physical Properties

Core proposal:
Add a probabilistic mapper that converts object category, room context, visible texture features, and top-k material probabilities into property-specific mixture distributions over material-property interval entries. The mapper should output a calibrated interval per physical property, an interval midpoint, and a mixture explanation showing which material/property entries contributed. It should treat surface-observed properties such as friction and hardness separately from bulk-sensitive properties such as density and Young's modulus, so the model can express broader uncertainty when RGB evidence is insufficient.

Motivation or baseline weakness:
A detection/segmentation plus material classifier pipeline can often identify a visible surface material, but it usually maps each object to one material label and one point-valued set of physical constants. This ignores ambiguity from object category, room context, coatings, upholstery, laminates, and hidden internal structure, especially for chairs, cabinets, tables, sofas, appliances, and composite furniture where the visible surface may not determine bulk density or stiffness.

Mechanism or approach:
A small tabular/MLP calibration head attached after frozen detection, segmentation, and material-recognition components. Inputs are object category embedding, room type embedding, normalized box/mask features, crop texture embedding, material top-k probabilities, and material entropy. Outputs are property-specific mixture weights over a material-property interval table plus lower/median/upper estimates for density, Young's modulus, Poisson's ratio, hardness, and friction coefficient.
Train the mapper with a property-specific interval objective: quantile pinball loss for lower and upper bounds, midpoint log-MAE for positive-valued properties, and MAE or ordinal loss for bounded or ordinal properties. Add a weak regularizer that keeps mixture mass compatible with the frozen material probabilities without forcing identical weights across all properties. Calibrate the final intervals on a held-out split to target nominal coverage while reporting interval width and selective risk.

Experiment and implementation plan:
GroundingDINO+SAM+CLIP material top-1 mapped to engineering material property table median; Mask2Former+MINC material classifier mapped to table median; Qwen-VL object/material prompt mapped to table median; Top-k material probability weighted average over material table medians without context conditioning
Indoor images with object masks or boxes from ScanNet, Matterport3D, or OpenRooms; Object category labels or detector-generated categories; Room or scene-type labels, either annotated or inferred from image metadata; Material labels or proxy material labels from OpenSurfaces/MINC-style categories; Engineering material property tables with intervals for density, Young's modulus, Poisson's ratio, hardness, and friction coefficient; A small validation set with manually audited object category, visible material, and plausible property interval annotations
run_detection_segmentation.py; extract_object_crops_and_context.py; predict_material_topk.py; build_material_property_interval_table.py; create_proxy_property_targets.py; train_interval_mapper.py; calibrate_prediction_intervals.py; evaluate_object_property_predictions.py
material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; mean_prediction_interval_width; calibration_error; selective_risk
Remove scene context features and use only object crop material probabilities; Remove object category conditioning; Use top-1 material table median instead of top-k mixture; Replace learned interval mapper with hand-coded material lookup; Train with midpoint-only point loss instead of interval/quantile loss; Share one mixture distribution across all properties instead of property-specific mixture weights; Vary property interval width assumptions in the material table
Randomly permute material labels before property mapping while keeping object categories fixed; Randomly permute object categories while keeping material predictions fixed; Use room context alone without object crop, object category, or material cues; Map every object in a coarse visual-material group to identical constants regardless of category; Train on shuffled property intervals that preserve the marginal distribution but break object-material-property alignment
Reduce density_log_mae by at least 10% relative to the top-1 material table median baseline on the audited validation set; Reduce youngs_modulus_log_mae by at least 10% relative to the same baseline; Achieve 80-90% empirical coverage for nominal 90% intervals without more than 2x the baseline interval width; Improve selective_risk at 70% object coverage relative to the deterministic lookup baseline; Maintain material_top3_accuracy within 2 percentage points of the frozen material classifier because the mapper should not degrade recognition outputs

Risks, controls, or fallback:
Risk: proxy property intervals may be noisy, overly broad, or dominated by hidden construction that cannot be inferred from one RGB image. Fallback: restrict the MVP to categories with plausible visual-material linkage, report ordinal or interval metrics in addition to exact regression, use property-specific conservative intervals for bulk-sensitive quantities, and emit a failure_warning field whenever predicted intervals span multiple incompatible material families.

---

Idea 2
Title:
Object-Part Surface Evidence Aggregation for Multi-Material Indoor Objects

Core proposal:
Add an object-part evidence aggregator that subdivides each object mask into visually coherent regions, predicts a material distribution for each region, and combines region evidence into an object-level material mixture using category-specific but simple part relevance rules. The aggregation should distinguish visible surface composition from inferred bulk relevance: a large visible cushion region may dominate friction or hardness, while a smaller frame region may be more relevant for stiffness or density. The output is a property-specific material mixture, not a single shared mixture for all properties.

Motivation or baseline weakness:
Whole-object material classification treats each detected object as having one dominant material, but many indoor objects expose multiple visible parts with different materials, such as metal chair legs with fabric seats, wooden tables with glass tops, or plastic appliances with rubber seals. A single crop-level material prediction can therefore produce incorrect material mixtures and physical-property estimates when the object contains spatially distinct surfaces.

Mechanism or approach:
A lightweight region graph aggregator over submasks or superpixels inside each object instance mask. Each node stores region area, location, shape, crop embedding, material probabilities, and boundary adjacency. A small scoring head or rule-based scorer assigns property-specific region relevance weights using visible area, normalized part location, material confidence, and object category.
Estimate property-specific object material mixtures by minimizing material multi-label loss when part/material labels are available and interval property loss when only object-level property targets are available. Add sparsity and entropy regularization so the top contributing regions are interpretable, while preventing collapse to the largest region for every property. Train and evaluate single-material and multi-material categories separately.

Experiment and implementation plan:
GroundingDINO+SAM whole-object crop with CLIP material classifier; SAM2 object mask with average pooled object embedding mapped to material table; Mask2Former instance mask with single material prediction from MINC/OpenSurfaces classifier; Area-weighted average of region material probabilities without category or property-specific relevance
Indoor RGB images with instance masks from ScanNet, Matterport3D, or OpenRooms; Submasks, superpixels, or segment proposals inside each detected object mask; Material classification data from OpenSurfaces or MINC for region-level supervision or pseudo-labeling; Engineering material property tables for mapping material mixtures to property intervals; A manually checked subset of multi-material objects with visible part/material annotations; A manually checked subset of mostly single-material objects for regression testing against false over-segmentation
generate_object_and_subpart_masks.py; extract_region_material_scores.py; build_region_graph_features.py; create_part_material_audit_split.py; train_part_evidence_aggregator.py; compose_material_mixture_properties.py; evaluate_multimaterial_objects.py; visualize_region_contributions.py
material_macro_f1; material_top3_accuracy; visible_material_mixture_l1; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; mask_iou; calibration_error; region_contribution_sparsity
Whole-object crop only versus region aggregation; Area-weighted region aggregation versus learned region weighting; Remove category-specific part priors; Remove property-specific region relevance and use one shared region weighting; Use only largest submask material prediction; Use ground-truth instance masks versus detector-generated masks; Evaluate single-material and multi-material categories separately
Randomly shuffle region material scores within an object while preserving region geometry; Use submasks from neighboring objects as evidence for the target object; Aggregate regions with uniform random weights at the same number of regions; Disable visual material scores and use category priors only; Randomly rotate or mirror normalized region locations before applying category-specific part priors
Improve material_macro_f1 by at least 5 percentage points on audited multi-material objects compared with whole-object material classification; Reduce density_log_mae by at least 8% on multi-material categories relative to whole-object lookup; Reduce youngs_modulus_log_mae by at least 8% on multi-material categories relative to whole-object lookup; Limit degradation on mostly single-material categories to no more than 3 percentage points in material_macro_f1; Produce an interpretable top-region evidence list for at least 90% of evaluated objects; Show that shuffled-region and neighboring-object negative controls perform worse than the proposed aggregator

Risks, controls, or fallback:
Risk: automatically generated submasks may not correspond to semantic parts, and visible area may be a poor proxy for bulk composition. Fallback: limit aggregation to categories with reliable part layouts, use conservative material mixtures when region evidence conflicts, fall back to whole-object classification for fragmented masks, and emit failure_warning when the object is heavily occluded, over-segmented, or dominated by visually ambiguous regions.

---

Idea 3
Title:
Failure-Aware Conformal Property Prediction for Single-Image Object Physics

Core proposal:
Add a post-hoc conformal calibration and failure-warning layer around an existing object/material/property pipeline. The layer computes uncertainty features from detector confidence, mask quality proxies, material entropy, disagreement among material predictors, object size, occlusion cues, and property-table spread. It then produces property-specific calibrated intervals and a selective prediction decision: return a prediction, return a wide interval with warning, or abstain when the expected error is too high.

Motivation or baseline weakness:
A plug-and-play pipeline that combines detectors, material classifiers, vision-language prompts, and property tables can output precise-looking physical properties even when the object is occluded, material evidence is weak, segmentation is poor, or the property is intrinsically unobservable from RGB. This creates overconfident predictions instead of useful uncertainty estimates, abstentions, or failure warnings.

Mechanism or approach:
A calibration wrapper with three components: a feature extractor for uncertainty signals, a property-specific nonconformity scorer, and a selective prediction policy. The wrapper does not retrain the frozen detector, segmenter, material classifier, or prompt model; it only learns calibration thresholds and optional shallow scoring functions on a calibration split.
Fit property-specific nonconformity scores on a calibration split so prediction intervals achieve target empirical coverage. Optimize abstention thresholds to minimize selective risk at fixed object coverage levels. Train the warning classifier or threshold rule to enrich high-error cases while controlling warning frequency, using only calibration-set residuals and uncertainty features.

Experiment and implementation plan:
GroundingDINO+SAM+CLIP material lookup with uncalibrated confidence; SAM2+Qwen-VL material/property prompt with raw model confidence; Mask2Former+MINC material classifier with fixed property intervals; Fixed-width property intervals from material table spread without image-conditioned calibration
Calibration and test splits from ScanNet, Matterport3D, or OpenRooms with object detections and masks; Proxy or audited material/property interval labels; Detector confidence scores, mask stability or mask quality proxies, material probability distributions, and prompt-based material outputs; Engineering property tables with material-level variance or intervals; Human-audited difficult cases including occlusion, transparent objects, reflective objects, very small objects, and ambiguous materials
run_base_property_pipeline.py; compute_uncertainty_features.py; fit_conformal_calibrator.py; fit_selective_prediction_policy.py; evaluate_interval_coverage.py; evaluate_selective_prediction.py; generate_failure_warnings.py; audit_warning_cases.py
prediction_interval_coverage; mean_prediction_interval_width; calibration_error; selective_risk; abstention_rate; warning_precision_for_high_error_cases; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; object_recall
Use material entropy only for calibration; Use property-table spread only for calibration; Remove detector and mask quality features; Remove material-predictor disagreement features; Global conformal intervals versus category-conditioned conformal intervals; Property-specific conformal intervals versus one shared threshold for all properties; No abstention versus selective prediction with failure warnings
Calibrate on randomly shuffled property labels while preserving the marginal property distribution; Use random uncertainty scores with the same abstention rate; Use detector confidence alone as the uncertainty estimate; Apply calibration thresholds learned for one property to all properties without property-specific fitting; Randomly assign failure warnings at the same warning frequency
Achieve at least 85% empirical coverage for nominal 90% prediction intervals on density and Young's modulus; Reduce calibration_error by at least 25% relative to raw model confidence or fixed table intervals; At 70% object coverage, reduce selective_risk by at least 15% relative to non-selective prediction; Failure warnings should be enriched among high-error cases, with warned objects having at least 1.5x the error rate of non-warned objects; Do not increase median interval width by more than 50% over the fixed-interval baseline at comparable coverage; Random-warning and random-uncertainty negative controls should not match the proposed warning enrichment or selective-risk reduction

Risks, controls, or fallback:
Risk: calibration splits may not represent deployment scenes, and proxy labels may conflate true uncertainty with annotation noise. Fallback: use category-conditional and property-conditional calibrators where enough data exists, otherwise default to conservative global intervals and explicit failure_warning messages for transparent, reflective, heavily occluded, tiny, or visually textureless objects.

---

## Item 11: HUM-bc3c559211

类型：`portfolio`

### Candidate A

Idea 1
Title:
Material-Conditioned Interval Property Lookup for Segmented Indoor Objects

Core proposal:
Add a lightweight material-to-property interval mapper that converts top-k localized material predictions and object category priors into interval-valued physical-property predictions rather than overconfident point estimates. For each object mask, the module fuses calibrated visual material probabilities with category-conditioned priors from curated material-property tables and ObjectFolder/ObjectFolder2.0 metadata where available. It emits median estimates, lower/upper intervals, confidence, source tags, and failure warnings when the material posterior is diffuse, the object category conflicts with the material hypothesis, or the lookup table lacks adequate support.

Motivation or baseline weakness:
GroundingDINO with SAM/SAM2 can localize visible objects, but the pipeline has no calibrated bridge from object-localized material cues to physical-property ranges. CLIP/OpenSurfaces/MINC-style material recognition can be prompt-sensitive or ambiguous, and single RGB images often cannot support exact density, modulus, hardness, or friction estimates for hidden or composite materials.

Mechanism or approach:
A frozen-backbone material posterior calibrator plus deterministic property-table aggregator: temperature-scaled material logits from masked object crops are mapped to normalized material names and then to property intervals using curated material-property tables and ObjectFolder/ObjectFolder2.0 priors, with no large-scale end-to-end training.
Minimize interval-aware negative log likelihood and log-space absolute error for density and Young's modulus under weak or proxy labels, while enforcing target prediction-interval coverage for all physical-property outputs through calibration on a held-out validation split.

Experiment and implementation plan:
GroundingDINO; SAM; SAM2; CLIP; OpenSurfaces; MINC; ObjectFolder; ObjectFolder2.0
Indoor images with object masks or boxes from an indoor-scene source such as ScanNet, Matterport3D, or OpenRooms; Material labels or proxy labels aligned to object crops using OpenSurfaces/MINC-style material categories; Object category labels aligned to detected masks; Curated material-property tables containing density, Young's modulus, Poisson's ratio, hardness, and friction coefficient ranges with normalized units; ObjectFolder/ObjectFolder2.0 object-material-property metadata where available; Held-out validation split for material-logit temperature scaling and interval calibration
run_detection_segmentation.py to produce object_id, category, mask_or_box using GroundingDINO plus SAM/SAM2; extract_masked_object_crops.py to create masked object crops and optional local context crops; predict_material_topk.py to obtain calibrated material posteriors from frozen CLIP/OpenSurfaces/MINC-style material models; build_property_table_index.py to normalize material names, aliases, property units, and source tags; aggregate_property_intervals.py to combine material posteriors, object-category priors, and table ranges into structured JSON predictions; evaluate_interval_properties.py to compute material metrics, property errors, interval coverage, calibration error, abstention rate, and selective risk
object_recall; mask_iou; material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Remove object-category prior and use material posterior only; Use point estimates from the most likely material instead of posterior-weighted interval aggregation; Use uncalibrated CLIP/OpenSurfaces/MINC logits instead of temperature-scaled material probabilities; Use mask crop only versus mask crop plus surrounding scene context; Replace curated table intervals with ObjectFolder/ObjectFolder2.0-only priors where metadata exists; Disable low-observability and table-missing failure warnings
Shuffle material labels across object crops before property lookup; Assign generic category-level property intervals without visual material evidence; Use whole-image material prediction instead of object-mask-localized prediction; Evaluate categories or materials absent from the property table to verify failure_warning activation; Randomize material-property table rows while preserving material label frequencies
Improve material_top3_accuracy over a frozen CLIP-only object-crop baseline by at least 5 percentage points after calibration; Reduce density_log_mae and youngs_modulus_log_mae by at least 10% relative to most-likely-material table lookup; Achieve prediction_interval_coverage within 5 percentage points of the nominal 90% interval target; Reduce selective_risk at 70% retained predictions relative to an uncalibrated material-posterior baseline; Failure if nominal 90% interval coverage is below 75% or property errors do not beat generic category priors

Evidence paper IDs:
openalex:W4402427278; openalex:W4402500749; openalex:W4411238954; openalex:W2798280964; openalex:W3012463097; openalex:W2895238724; openalex:W3200689778; openalex:W4312347618

Risks, controls, or fallback:
Risk: visible texture may not identify hidden composition, for example veneer, painted metal, foam-filled furniture, or composite objects. Fallback: widen intervals, mark low-observability or table-missing failure_warning fields, and report category-level priors rather than unsupported precise values.

---

Idea 2
Title:
Evidence-Gated VLM Verification for Object Material and Property JSON

Core proposal:
Introduce an evidence-gating layer that requires every accepted material/property prediction to be backed by object-localized evidence: masked crop appearance, nearby context, object category, material candidate, and property-source tag. The VLM is used only as a verifier or reranker over candidate material-property hypotheses generated by a frozen detector, segmenter, material model, and table lookup; it is not allowed to invent numeric property values. Predictions are rejected or downweighted when the verifier cannot select a candidate using localized visual cues or when prompt-consistency checks disagree.

Motivation or baseline weakness:
Vision-language models such as LLaVA, BLIP-2, and Qwen-VL can provide contextual reasoning, but their material and physical-property claims may be unsupported by localized visual evidence and sensitive to prompts. This can produce plausible but unverified JSON outputs, especially when asked to infer numerical properties directly from a single RGB image.

Mechanism or approach:
A constrained hypothesis verifier that scores candidate JSON rows using masked object crops, context panels, explicit candidate lists, and property-source tags. The verifier outputs a candidate rank, evidence cue labels, and an abstention score; numeric property intervals are copied only from the candidate table row and never generated free-form by the VLM.
Maximize material reranking accuracy and minimize selective physical-property risk subject to an acceptance constraint: each retained prediction must include at least one localized visual cue and one property-source cue. Calibrate the evidence-score threshold on a validation split to abstain when verifier confidence or prompt consistency is low.

Experiment and implementation plan:
GroundingDINO; SAM; Mask2Former; CLIP; OpenSurfaces; MINC; BLIP-2; LLaVA; Qwen-VL; ObjectFolder; ObjectFolder2.0
Indoor scene images from a source such as ScanNet, Matterport3D, or OpenRooms; Object masks or boxes from GroundingDINO plus SAM/SAM2 or Mask2Former; Candidate material labels from CLIP/OpenSurfaces/MINC-style material models; Candidate physical-property intervals from curated material-property tables and ObjectFolder/ObjectFolder2.0 metadata where available; A validation split with human-checked material labels or proxy labels for verifier calibration; A small audit subset with human judgments of whether cited evidence is actually localized to the target object
generate_candidate_json.py to create top-k material and property hypotheses per object without VLM-generated numeric values; render_evidence_panels.py to create object crop, masked image, context crop, mask overlay, and candidate list for VLM verification; vlm_verify_candidates.py to query BLIP-2/LLaVA/Qwen-VL with constrained evidence prompts and fixed output schema; check_prompt_consistency.py to run prompt variants and measure candidate-rank agreement; calibrate_acceptance_threshold.py to tune evidence-score and consistency thresholds on validation data; evaluate_verified_json.py to score accepted, rejected, and all predictions, including human-audited unsupported-evidence errors
material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Use VLM free-form prediction instead of candidate verification; Remove localized mask crop and give only full-image context; Remove property-source text from the verifier prompt; Use a single prompt versus prompt ensemble with consistency voting; Use verifier score without calibration versus calibrated abstention; Allow VLM-generated numeric properties versus table-copied property intervals only
Give the VLM candidates from a different object mask in the same image; Randomize candidate material-property pairings while keeping object category fixed; Ask the VLM to output numerical properties without table candidates and verify that these are not accepted; Use a background crop instead of the object crop to test evidence leakage; Swap the property-source tags across candidate rows to test whether the verifier over-trusts source text
Improve material_top1_accuracy or material_macro_f1 by at least 5 percentage points over CLIP/OpenSurfaces/MINC candidate ranking alone; Reduce selective_risk at 60% retained objects by at least 15% compared with no VLM evidence gate; Maintain prediction_interval_coverage within 5 percentage points of target coverage after abstention; Decrease unsupported-evidence errors in a human audit by at least 30% relative to free-form VLM JSON; Failure if VLM verification improves fluency but not material accuracy, calibration error, selective risk, or audited evidence support

Evidence paper IDs:
openalex:W4399597788; openalex:W4402155831; openalex:W4385327621; openalex:W4392222076; openalex:W4402427278; openalex:W4402500749; openalex:W4411238954; openalex:W3200689778; openalex:W4312347618

Risks, controls, or fallback:
Risk: the VLM may rationalize incorrect candidates, rely on object-category stereotypes, or follow misleading source text rather than visual cues. Fallback: restrict VLM output to reranking and abstention, log evidence text separately from numeric property values, reject prompt-inconsistent cases, and default to calibrated material-model plus table intervals when verifier consistency is low.

---

Idea 3
Title:
Segmentation-Uncertainty Propagation for Physical Property Confidence

Core proposal:
Sample multiple plausible masks or boxes per detected object using detector proposals, SAM/SAM2 prompt variants, and Mask2Former alternatives, then propagate the resulting variation through material classification and property lookup. The final object JSON reports material distributions, property intervals, mask-instability scores, evidence diversity, and a failure warning when predictions are unstable across masks or when alternative masks imply incompatible materials.

Motivation or baseline weakness:
Promptable segmentation with SAM/SAM2 or detection-driven masks can vary with prompts, occlusions, and object boundaries. Downstream material and physical-property estimates often ignore this mask uncertainty, producing overconfident predictions for partially visible, small, reflective, or poorly segmented objects.

Mechanism or approach:
A mask-ensemble uncertainty propagator that perturbs points and boxes, collects alternative masks, computes material/property predictions for each mask, filters degenerate masks, and aggregates the resulting predictions into calibrated confidence intervals and instability scores.
Estimate predictive uncertainty by marginalizing over segmentation hypotheses and calibrate object-level property intervals so that objects with unstable masks have wider intervals and higher abstention probability, while stable masks retain narrow intervals when material predictions agree.

Experiment and implementation plan:
GroundingDINO; SAM; SAM2; Mask2Former; CLIP; OpenSurfaces; MINC; ObjectFolder; ObjectFolder2.0
Indoor RGB images with visible objects from a source such as ScanNet, Matterport3D, or OpenRooms; Reference object masks where available for mask_iou evaluation; Object category annotations or detector-generated categories; Material proxy labels from OpenSurfaces/MINC-style datasets or a manually validated subset; Physical-property proxy intervals from ObjectFolder/ObjectFolder2.0 metadata and curated material-property tables; Validation split for calibrating the relationship between mask instability, material disagreement, and interval width
generate_mask_ensemble.py to create box-, point-, and mask-prompt variants from GroundingDINO/SAM/SAM2/Mask2Former outputs; filter_degenerate_masks.py to remove empty masks, near-duplicates, and masks dominated by background; score_mask_quality.py to compute mask_iou where reference masks exist and mask stability otherwise; predict_properties_per_mask.py to run material prediction and property lookup for each retained mask sample; aggregate_uncertainty.py to combine material and property distributions across masks using posterior-weighted intervals and instability features; evaluate_uncertainty_propagation.py to compute accuracy, property error, coverage, calibration error, abstention rate, and selective risk
object_recall; mask_iou; material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Single best SAM mask versus mask ensemble; SAM-only ensemble versus GroundingDINO plus SAM/SAM2 plus Mask2Former ensemble; Aggregate by mean material posterior versus worst-case interval union; Remove mask-instability feature from confidence calibration; Use object crop bounding box instead of precise mask crops; Disable degenerate-mask filtering before uncertainty aggregation
Randomly jitter masks far outside the object to verify uncertainty increases and confidence decreases; Use duplicate identical masks to confirm no artificial uncertainty gain; Swap mask ensembles between objects of the same category; Evaluate fully visible large objects separately from small or occluded objects to check whether uncertainty is selectively useful; Randomly permute per-mask material predictions before aggregation to verify calibration detects incoherent evidence
Improve prediction_interval_coverage by at least 10 percentage points over single-mask property prediction at similar average interval width; Reduce calibration_error by at least 15% compared with single-best-mask confidence; Maintain material_accuracy within 2 percentage points of the single-mask baseline while improving selective_risk; Show higher uncertainty for low-mask_iou or high-occlusion objects than for stable high-mask_iou objects; Failure if mask ensembling only widens all intervals uniformly without improving coverage, calibration error, or selective risk

Evidence paper IDs:
openalex:W4402500749; openalex:W7148178853; openalex:W4416850904; openalex:W4403323960; openalex:W4411238954; openalex:W3022851742; openalex:W4391809438; openalex:W3200689778; openalex:W4312347618

Risks, controls, or fallback:
Risk: mask ensembles may be computationally expensive and may degrade material recognition by including background or neighboring objects. Fallback: cap the ensemble to a small diverse set of masks, skip ensembling for high-stability easy objects, filter degenerate masks, and widen intervals only when material or property predictions actually vary across plausible masks.

### Candidate B

Idea 1
Title:
Uncertainty-Aware Material-to-Property Retrieval for Segmented Indoor Objects

Core proposal:
Build a plug-and-play workflow that combines frozen open-vocabulary object detection, promptable segmentation, material recognition, and table-based physical-property retrieval. For each visible object, GroundingDINO or Mask2Former proposes object boxes, SAM or SAM2 refines masks, CLIP/OpenSurfaces/MINC-style material classifiers estimate a top-k material distribution from masked crops, and a lightweight retrieval/calibration module maps material hypotheses to intervals for density, Young's modulus, Poisson's ratio, hardness, and friction coefficient. The final output is an object-level structured JSON containing object_id, category, mask_or_box, predicted_materials, physical-property intervals or point estimates, uncertainty, localized evidence, and a failure warning when the property is underdetermined from RGB.

Motivation or baseline weakness:
The main bottleneck is not detecting visible indoor objects, but avoiding overconfident physical-property predictions when a single RGB image only reveals surface appearance. A publishable incremental contribution is to treat physical-property prediction as evidence-grounded retrieval over material-property tables rather than direct regression. This is baseline-grounded, lightweight, and directly addresses the constraint that exact ground truth may be unavailable while proxy or interval labels are allowed.

Mechanism or approach:
Direct baselines: GroundingDINO, SAM/SAM2, Mask2Former, CLIP, OpenSurfaces, MINC, ObjectFolder/ObjectFolder2.0, and engineering material property tables. Transfer baselines: VLM prompting with BLIP-2, LLaVA, or Qwen-VL to infer object category and likely material from scene context. Borrowed components: open-vocabulary object detection, promptable mask refinement, material-category classifiers, and material-property lookup tables. New component: a Material-Property Interval Retriever that stores distributions over physical properties per material and object category, then fuses visual material probabilities, object category priors, and scene context into calibrated prediction intervals. Minimal new module: a small probabilistic fusion layer, implemented as temperature-scaled Bayesian model averaging or conformalized quantile lookup, without training large vision backbones. Ablations: boxes only versus masks; CLIP-only versus OpenSurfaces/MINC supervised material classifier; no scene context versus VLM context; point estimates versus interval retrieval; category-only priors versus material-plus-category priors. Risks: property tables may disagree by source, material labels may be too coarse, visible surface material may differ from bulk material, and VLM context may hallucinate. Failure criteria: less than 5% relative improvement over category-only property priors on density_log_mae and youngs_modulus_log_mae; prediction_interval_coverage below nominal by more than 10 percentage points; material_macro_f1 not exceeding CLIP-only prompt baseline; or frequent unsupported evidence strings in qualitative audit. MVP artifacts: inference script, material-property database, JSON schema validator, calibration plots, and benchmark report. Implementation plan: assemble indoor images from ScanNet, Matterport3D, and OpenRooms; run frozen detection/segmentation; collect or derive material proxy labels from OpenSurfaces/MINC-compatible categories; map material labels to ObjectFolder/ObjectFolder2.0 and engineering tables; evaluate object_recall, mask_iou, material_accuracy, material_macro_f1, material_top3_accuracy, density_log_mae, youngs_modulus_log_mae, poisson_ratio_mae, hardness_mae_or_ordinal_error, friction_coefficient_mae, prediction_interval_coverage, calibration_error, and selective_risk.

Experiment and implementation plan:
Create a benchmark split with indoor images from ScanNet, Matterport3D, and OpenRooms. Use available object categories and masks where present, otherwise generate pseudo-labels with detection plus SAM/SAM2 and manually audit a small validation subset. Evaluate against category-only lookup, CLIP material prompt lookup, and VLM direct prompting baselines. Main metrics are object_recall, mask_iou, material_macro_f1, material_top3_accuracy, density_log_mae, youngs_modulus_log_mae, poisson_ratio_mae, hardness_mae_or_ordinal_error, friction_coefficient_mae, prediction_interval_coverage, calibration_error, and selective_risk. Report failure-warning precision by auditing cases where the system flags hidden structure, reflective/transparent surfaces, tiny objects, or uncertain material.

Evidence paper IDs:
openalex:W4402427278; openalex:W4402500749; openalex:W4411238954; openalex:W3022851742; openalex:W4391809438; openalex:W4367665525; openalex:W4385327621; openalex:W3200689778; openalex:W4312347618

---

Idea 2
Title:
Evidence-Gated Vision-Language Physical Property Prediction

Core proposal:
Develop an object-level physical-property predictor that uses a vision-language model only when its material and property claims are supported by localized visual evidence from the detected object mask. The pipeline first segments objects, extracts masked crops and local texture/color/reflectance cues, asks a VLM to produce candidate material-property explanations, and then applies a lightweight evidence gate that accepts, downweights, or rejects claims based on agreement with localized material classifiers and retrieval priors. The output JSON includes explicit evidence such as material cues, object-category priors, context cues, and a failure_warning when the VLM relies on unsupported semantics.

Motivation or baseline weakness:
VLMs can reason about indoor context, object affordances, and likely materials, but they may hallucinate precise physical properties from category names. A publishable metric-improvement idea is to preserve the useful context reasoning of BLIP-2/LLaVA/Qwen-VL while adding localized evidence verification and uncertainty calibration. This targets the known limitation that semantic predictions may be unsupported by visual evidence.

Mechanism or approach:
Direct baselines: LLaVA, BLIP-2, Qwen-VL direct prompting for JSON physical-property output; CLIP material prompts; GroundingDINO plus SAM/SAM2 for object localization. Transfer baselines: SceneGPT-style scene reasoning ideas for context priors, adapted only as prompt-based 2D scene context rather than requiring 3D training. Borrowed components: VLM captioning/question answering, object grounding, mask-based crop extraction, and CLIP/OpenSurfaces/MINC material scoring. New component: an Evidence-Gated Property Decoding module that compares VLM-generated materials and property ranges against three evidence channels: masked visual material probability, object-category-to-material prior, and table-derived feasible physical-property ranges. The gate produces calibrated confidence, abstention, and failure warnings. Minimal new module: a small verifier trained or calibrated on proxy labels, using features such as VLM log-probability or self-consistency score, CLIP material similarity, classifier entropy, table-range consistency, and mask quality. Ablations: ungated VLM prompting; VLM plus table lookup without visual evidence; evidence gate without scene context; CLIP-only material verifier; self-consistency sampling versus single VLM response; hard rejection versus soft reweighting. Risks: VLM APIs or checkpoints may vary, evidence scores may penalize uncommon but correct materials, and object crops may omit discriminative details. Failure criteria: no reduction in selective_risk relative to ungated VLM at the same coverage; calibration_error not improved by at least 15%; material_top3_accuracy worse than CLIP-only baseline; or qualitative audit showing accepted VLM claims without localized evidence. MVP artifacts: prompt library, object-crop generator, evidence-gate model, uncertainty report, structured JSON examples, and an error taxonomy for hallucinated material/property claims. Implementation plan: run GroundingDINO/SAM2 to obtain objects; query VLMs with full image plus masked crop; parse candidate material and property estimates; retrieve feasible ranges from material-property tables; train or tune the evidence gate on validation proxy labels; evaluate on held-out indoor scenes and report both accuracy and abstention behavior.

Experiment and implementation plan:
Compare four systems: direct VLM JSON prompting, detector-plus-VLM crop prompting, detector-plus-material-retrieval, and the proposed evidence-gated VLM. Datasets include ScanNet, Matterport3D, OpenRooms, OpenSurfaces/MINC material labels, and ObjectFolder/ObjectFolder2.0 or engineering material tables for property intervals. Metrics include material_accuracy, material_macro_f1, material_top3_accuracy, density_log_mae, youngs_modulus_log_mae, poisson_ratio_mae, hardness_mae_or_ordinal_error, friction_coefficient_mae, prediction_interval_coverage, calibration_error, and selective_risk. Conduct a human audit of 100 accepted and 100 rejected object predictions to measure whether evidence fields correspond to localized visual cues rather than generic category knowledge.

Evidence paper IDs:
openalex:W4399597788; openalex:W4392222076; openalex:W4402155831; openalex:W4414857074; openalex:W4402427278; openalex:W4385327621; openalex:W3047386722; openalex:W2798280964; openalex:W2895238724

---

Idea 3
Title:
Conformal Cascaded Property Prediction with Object-Level Failure Warnings

Core proposal:
Design a cascaded inference workflow that explicitly separates easy, visually supported physical-property predictions from ambiguous or impossible single-image cases. The cascade starts with frozen detection and segmentation, then estimates material distributions, then predicts physical-property intervals using conformal calibration. A selective prediction controller decides whether to emit a narrow interval, a broad interval, or a failure_warning such as hidden core material, transparent/reflective surface, low mask confidence, small object, or category-material conflict.

Motivation or baseline weakness:
For deployment, the most important engineering integration challenge is not always reducing average error, but knowing when the workflow should abstain or broaden uncertainty. Existing baselines provide detection, segmentation, material recognition, and property sources, but they do not define an object-level selective-risk protocol for physical-property JSON outputs. This idea is publishable as an uncertainty-calibrated integration method and benchmark protocol.

Mechanism or approach:
Direct baselines: Mask2Former or GroundingDINO for object proposals, SAM/SAM2 for mask refinement, CLIP/OpenSurfaces/MINC for material probabilities, ObjectFolder/ObjectFolder2.0 and engineering tables for physical-property intervals. Transfer baselines: uncertainty-aware segmentation and efficient SAM adaptation concepts, used only to motivate lightweight calibration and mask-quality estimation. Borrowed components: frozen vision backbones, promptable masks, material classifiers, tabular property retrieval, and conformal prediction. New component: a Cascaded Conformal Selector that takes mask confidence, detector score, material entropy, top-1/top-2 material margin, object-category prior agreement, table-range width, and VLM context consistency as inputs, then outputs calibrated property intervals plus a failure_warning type. Minimal new module: a calibration layer fitted on a validation set, such as split conformal quantile calibration plus a small logistic/selective-risk model. Ablations: no conformal calibration; global conformal intervals versus material-conditioned intervals; no mask-quality feature; no category-material conflict feature; direct regression surrogate versus table interval prediction; single failure warning versus typed warnings. Risks: conformal validity may break under dataset shift, proxy labels may be noisy, broad intervals may be uninformative, and object-level physical properties may be multi-material rather than single-material. Failure criteria: prediction_interval_coverage below target coverage on held-out indoor scenes; selective_risk curve not better than confidence-thresholded CLIP baseline; average interval width too broad to be useful, for example exceeding a predefined full-table prior width on most objects; or typed failure warnings not correlated with actual high-error cases. MVP artifacts: calibration split definition, conformal interval code, typed warning taxonomy, JSON output validator, risk-coverage plots, and benchmark leaderboard script. Implementation plan: collect pseudo-ground-truth property intervals by linking material labels from OpenSurfaces/MINC-style categories to property tables; generate object masks on ScanNet/Matterport3D/OpenRooms; fit conformal calibration on validation scenes; evaluate on disjoint scenes and cross-dataset transfer; produce examples showing narrow high-confidence predictions for visually obvious materials such as metal or glass and broad/abstained predictions for upholstered, painted, laminated, or composite objects.

Experiment and implementation plan:
Construct a cascaded benchmark with object-level outputs and typed failure warnings. Use detection_segmentation metrics object_recall and mask_iou; material metrics material_accuracy, material_macro_f1, and material_top3_accuracy; physical-property metrics density_log_mae, youngs_modulus_log_mae, poisson_ratio_mae, hardness_mae_or_ordinal_error, and friction_coefficient_mae; uncertainty metrics prediction_interval_coverage, calibration_error, and selective_risk. Compare against direct table lookup from object category, CLIP material lookup, VLM direct property prompting, and non-conformal interval baselines. Stress-test cross-dataset transfer by calibrating on one indoor source and evaluating on another, then report when failure warnings successfully identify high-error or underdetermined objects.

Evidence paper IDs:
openalex:W4402500749; openalex:W7148178853; openalex:W4416850904; openalex:W4403323960; openalex:W4411238954; openalex:W2798280964; openalex:W3012463097; openalex:W3200689778; openalex:W4312347618

---

## Item 12: HUM-c85f8d38f4

类型：`portfolio`

### Candidate A

Idea 1
Title:
Mask-Localized Material Mixture Retrieval for Property Intervals

Core proposal:
Add a lightweight mask-localized material-mixture retriever that samples multiple masked visual patches per detected object, predicts a calibrated distribution over visible material components, and maps the posterior mixture to table-backed physical-property intervals. ObjectFolder/ObjectFolder2.0 are used only as object/category and multisensory property priors where available, while OpenSurfaces/MINC-style labels supervise visible material recognition; outputs are explicitly labeled as visible-surface-informed property intervals, not exact bulk measurements.

Motivation or baseline weakness:
CLIP/OpenSurfaces/MINC-style material recognition can assign a single semantic material to an object crop even when the visible evidence is localized, mixed, or surface-only; this propagates overconfident point estimates for density, Young's modulus, Poisson's ratio, hardness, and friction coefficient from 2D indoor images where hidden composition is often unobservable.

Mechanism or approach:
A frozen-encoder adapter with four components: masked patch sampler, material-mixture softmax head, property-interval aggregator over material/property tables and object priors, and JSON uncertainty formatter that emits interval bounds, posterior entropy, and failure_warning flags.
Minimize weak-label multiple-instance material loss over masked patches plus interval negative log likelihood for proxy physical-property intervals. Add a coverage-aware width regularizer that penalizes intervals that are too narrow on validation proxy labels while avoiding unbounded intervals through a validation-tuned maximum-width penalty.

Experiment and implementation plan:
GroundingDINO + SAM + CLIP single-material lookup; GroundingDINO + SAM2 + OpenSurfaces classifier + property-table lookup; Mask2Former + MINC classifier + property-table lookup
Indoor RGB images with object masks or boxes produced by GroundingDINO, SAM, SAM2, or Mask2Former; Object-level or region-level visible material labels or weak material tags aligned to OpenSurfaces and MINC categories; Object-category to material/property priors derived from ObjectFolder and ObjectFolder2.0 where category overlap exists; A versioned material-property table converted into density, Young's modulus, Poisson's ratio, hardness, and friction-coefficient intervals with source identifiers and unit normalization; Held-out validation objects with proxy material/property intervals for calibration and negative-control evaluation
run_detection_segmentation.py; extract_masked_object_patches.py; train_material_mixture_adapter.py; build_property_interval_table.py; evaluate_object_property_json.py
material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error
Replace mixture distribution with top-1 material lookup; Use whole-object crop instead of masked patch sampling; Remove object-category prior from the property aggregator; Use point estimates instead of intervals; Train with only visual features and no table-derived property constraints
Shuffle material-property table rows before aggregation; Evaluate on background masks treated as objects; Use random masks with correct object category labels; Use object category only without visible material cues; Replace masked patch features with patches from another object of the same category
Improve material_macro_f1 by at least 5 percentage points over top-1 CLIP/OpenSurfaces/MINC lookup on held-out indoor objects; Reduce density_log_mae and youngs_modulus_log_mae by at least 10 percent relative to single-material lookup on proxy interval midpoints; Achieve prediction_interval_coverage between 85 percent and 95 percent for nominal 90 percent proxy intervals; Reduce calibration_error by at least 20 percent relative to uncalibrated single-material lookup; Fail negative controls by showing coverage or accuracy drops when table rows, masks, or patch evidence are randomized

Evidence paper IDs:
openalex:W4402500749; openalex:W2798280964; openalex:W3012463097; openalex:W3200689778; openalex:W4312347618

Risks, controls, or fallback:
Risk: RGB-visible surfaces may not reveal bulk composition, so mixture estimates may still be wrong for veneered, painted, coated, hollow, or composite objects. Fallback: explicitly output wider visible-surface-informed intervals and a failure_warning when visible material evidence conflicts with object-category priors, when the material posterior entropy exceeds a validation-tuned threshold, or when the object category has no reliable overlap with ObjectFolder/ObjectFolder2.0 priors.

---

Idea 2
Title:
Evidence-Gated VLM Property Reasoning for Hallucination-Resistant JSON Outputs

Core proposal:
Introduce an evidence gate between frozen detection/segmentation and a frozen VLM. The VLM first emits candidate object-level JSON. For each material or physical-property claim, the gate checks whether the claim is supported by the object mask crop, material-retrieval neighbors, object-category priors, and table-backed property ranges. Unsupported or overprecise claims are replaced with calibrated intervals and explicit failure_warning fields rather than free-form corrections.

Motivation or baseline weakness:
VLMs such as LLaVA, BLIP-2, and Qwen-VL can produce plausible physical-property explanations from scene context, but their material and property claims may be unsupported by localized object evidence, sensitive to prompt wording, and overprecise relative to what a single 2D indoor image can justify.

Mechanism or approach:
A small evidence verifier that scores each VLM-generated material/property claim as supported, ambiguous, contradicted, or uncheckable using masked crop retrieval, object-category priors, and table-backed ranges; a deterministic JSON editor then rewrites material labels, property intervals, confidence values, and warnings according to the verifier state.
Maximize agreement between generated JSON claims and retrieval/table evidence while minimizing unsupported claims. Train or tune the verifier with supervised or rule-derived labels for supported, ambiguous, contradicted, and uncheckable claim states; calibrate verifier scores so abstention and warning decisions match validation-set reliability.

Experiment and implementation plan:
GroundingDINO + SAM + LLaVA prompted to emit object-level property JSON; GroundingDINO + SAM2 + BLIP-2 prompted to emit material and property estimates; Mask2Former + Qwen-VL prompted with object boxes and scene context
Indoor scene RGB images with object masks or boxes from GroundingDINO, SAM, SAM2, or Mask2Former; Raw VLM object-level JSON outputs from LLaVA, BLIP-2, and Qwen-VL under fixed prompt templates; Material labels or weak material tags aligned to OpenSurfaces and MINC categories; Physical-property proxy intervals from ObjectFolder, ObjectFolder2.0, and normalized material-property tables; A validation set of object-level JSON claims annotated or rule-labeled as supported, ambiguous, contradicted, or uncheckable by visible evidence and table ranges
prompt_vlm_object_json.py; retrieve_material_evidence.py; score_claim_support.py; calibrate_evidence_gate.py; evaluate_json_faithfulness_and_properties.py
material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error
Remove evidence gate and use raw VLM JSON; Use VLM confidence only without retrieval evidence; Use retrieval evidence only without scene context; Allow point estimates without table-backed intervals; Disable failure_warning generation; Use object category priors without masked crop evidence
Prompt the VLM with mismatched masks from another image; Swap retrieved material neighbors across object categories; Ask for impossible precision in physical-property point values; Evaluate with blank or blurred object crops while preserving category text; Replace property-table ranges with ranges from randomly selected materials
Reduce unsupported material/property claims by at least 30 percent relative to raw VLM prompting on the annotated validation set; Maintain or improve material_top3_accuracy relative to raw VLM prompting; Improve prediction_interval_coverage for nominal 90 percent proxy intervals to at least 85 percent; Reduce calibration_error by at least 20 percent relative to raw VLM confidence or self-reported certainty; Negative controls should trigger higher warning rates and lower verifier support scores than matched valid inputs

Evidence paper IDs:
openalex:W4399597788; openalex:W4392222076; openalex:W4402155831; openalex:W4385327621; openalex:W4402427278

Risks, controls, or fallback:
Risk: the verifier may reject correct but visually subtle VLM inferences or over-rely on incomplete material tables. Fallback: use a four-way decision policy that preserves the VLM category/context hypothesis but marks physical properties as broad intervals with low confidence when evidence is ambiguous or uncheckable, rather than forcing a hard correction.

---

Idea 3
Title:
Conformal Property Calibration from Proxy Labels and Object Similarity

Core proposal:
Add a post-hoc conformal calibration layer that operates on proxy labels and object-similarity groups. It converts material/property predictions into per-object prediction intervals with empirical coverage measured on held-out calibration splits stratified by object category, material ambiguity, and mask quality. The method explicitly claims coverage for the proxy visible-material target rather than for hidden true bulk composition.

Motivation or baseline weakness:
A plug-and-play pipeline using GroundingDINO/SAM-style masks plus material lookup can output physical-property values, but exact ground truth is often unavailable and uncertainty is poorly calibrated, especially for visually ambiguous indoor objects and low-quality masks.

Mechanism or approach:
A post-hoc conformal interval calibrator that consumes predicted material posterior, table-derived property distribution, mask quality score, object category, and scene-context embedding, then returns calibrated property intervals, confidence metadata, and abstention thresholds for unreliable objects.
Minimize calibrated interval width subject to validation-set coverage constraints for each physical property and for predefined subgroups. Fit nonconformity scores from residuals between predicted intervals and proxy labels, then tune abstention thresholds to reduce error among retained objects at a target retained-object fraction.

Experiment and implementation plan:
GroundingDINO + SAM + material lookup with uncalibrated confidence; GroundingDINO + SAM2 + CLIP/OpenSurfaces property intervals without conformal correction; Mask2Former + MINC property lookup with global uncertainty
Indoor RGB images and object masks or boxes produced by GroundingDINO, SAM, SAM2, or Mask2Former; Material proxy labels aligned to OpenSurfaces and MINC categories; Physical-property proxy intervals from ObjectFolder, ObjectFolder2.0, and normalized material-property tables; Calibration and test splits grouped by object category, material class, material posterior entropy, and mask quality; Optional measured ObjectFolder-style properties where category/object overlap permits separate evaluation from proxy table labels
generate_baseline_property_predictions.py; estimate_mask_quality_features.py; fit_conformal_property_intervals.py; evaluate_calibration_by_subgroup.py; export_calibrated_object_json.py
prediction_interval_coverage; calibration_error; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; object_recall; mask_iou
Global conformal calibration instead of subgroup calibration; Remove mask quality features; Remove material posterior entropy; Use category-only calibration groups; Use fixed engineering-table ranges without learned residual calibration
Calibrate on randomly permuted property labels; Use calibration objects from disjoint categories without subgroup adjustment; Apply calibration scores from high-quality masks to low-quality masks; Replace material posterior entropy with random confidence; Evaluate calibration after shuffling object masks across images
Achieve 90 percent nominal interval coverage within plus or minus 5 percentage points overall on proxy targets; Achieve subgroup coverage no lower than 80 percent for major material and object-category groups; Reduce calibration_error by at least 25 percent relative to uncalibrated lookup confidence; Do not increase median interval width by more than 20 percent relative to uncalibrated table intervals after calibration; Negative controls should show degraded coverage or inflated interval width, confirming dependence on valid labels, masks, and confidence features

Evidence paper IDs:
openalex:W4402500749; openalex:W4416850904; openalex:W4403323960; openalex:W2798280964; openalex:W3200689778; openalex:W4312347618

Risks, controls, or fallback:
Risk: proxy labels and table-derived intervals may not reflect true object-specific properties, so conformal guarantees may only hold for the proxy visible-material target. Fallback: report the calibrated target explicitly as a visible-material property interval, add failure_warning for hidden structure and coatings, and evaluate separate calibration curves for proxy labels versus any available measured ObjectFolder-style properties.

### Candidate B

Idea 1
Title:
Evidence-Grounded Material Interval Retrieval for Object-Level Physical Property Prediction

Core proposal:
A plug-and-play workflow that combines open-vocabulary object detection/segmentation with localized material recognition and a physical-property interval retriever. For each visible object, GroundingDINO or Mask2Former proposes objects, SAM/SAM2 refines masks, CLIP/OpenSurfaces/MINC-style material classifiers estimate top-k visible materials, and a lightweight retrieval module maps object category plus material candidates to density, Young's modulus, Poisson's ratio, hardness, and friction coefficient intervals from ObjectFolder/ObjectFolder2.0 and engineering material tables. The output is structured JSON with object_id, object_category, mask_or_box, predicted_materials, numeric property estimates, uncertainty intervals, evidence strings describing visual/material/context cues, and failure_warning flags when the property is underdetermined from RGB.

Motivation or baseline weakness:
Single RGB images rarely reveal exact composition, coatings, internal structure, or manufacturing process, so point estimates for physical properties are often overconfident. A publishable incremental improvement is to treat physical-property prediction as evidence-grounded interval retrieval rather than direct hallucinated regression. This directly addresses the benchmark constraints: frozen foundation models, proxy or interval labels, hidden material ambiguity, and object-level structured output.

Mechanism or approach:
Direct baselines: GroundingDINO, SAM/SAM2, Mask2Former, CLIP, OpenSurfaces, MINC, ObjectFolder, ObjectFolder2.0, and engineering material property tables. Transfer baselines: BLIP-2/LLaVA/Qwen-VL prompted to produce object-material-property JSON from masked crops. Borrowed components: open-vocabulary detection, promptable segmentation, material recognition, and multisensory/object property repositories. New component: a Material-Property Interval Retriever that conditions on object category, scene context, visible material cues, and top-k material probabilities to retrieve candidate material families and convert them into calibrated property intervals. Minimal new module: a small learned ranker or logistic calibration layer over frozen visual/material embeddings and table-derived material candidates. Ablations: no scene context, no object category, no mask crop, CLIP-only material recognition, OpenSurfaces/MINC-only recognition, top-1 material versus top-k material mixture, point regression versus interval retrieval, and with/without VLM evidence rationales. MVP artifacts: JSON schema, object-mask-to-material pipeline, material-property table normalization, retrieval/ranking module, uncertainty interval generator, and evaluation scripts. Implementation plan: build a canonical material taxonomy, align ObjectFolder/ObjectFolder2.0 and engineering tables to the taxonomy, run detection/segmentation on ScanNet/Matterport3D/OpenRooms images, crop masked objects, score material candidates, retrieve property distributions, output medians plus intervals, and benchmark against VLM-only and table-lookup baselines. Risks: material taxonomy mismatch, visually identical materials with different properties, bias toward common object-material pairs, and unreliable exact labels. Failure criteria: no improvement over category-only table lookup in density_log_mae or youngs_modulus_log_mae, prediction_interval_coverage below target at acceptable interval width, or material_top3_accuracy fails to exceed CLIP-only baseline.

Experiment and implementation plan:
Datasets: ScanNet, Matterport3D, and OpenRooms for indoor RGB scenes; OpenSurfaces and MINC for material supervision; ObjectFolder/ObjectFolder2.0 and engineering material tables for property priors and interval labels. Metrics: object_recall, mask_iou, material_accuracy, material_macro_f1, material_top3_accuracy, density_log_mae, youngs_modulus_log_mae, poisson_ratio_mae, hardness_mae_or_ordinal_error, friction_coefficient_mae, prediction_interval_coverage, calibration_error, and selective_risk. Compare against category-only lookup, material-only lookup, CLIP-to-table lookup, and VLM-prompted property JSON. Test whether top-k material mixture and interval calibration improve log-MAE and coverage. Report failure_warning precision by manually auditing cases with transparent, painted, composite, fabric-covered, or occluded objects.

Evidence paper IDs:
openalex:W4402427278; openalex:W4402500749; openalex:W4411238954; openalex:W7148178853; openalex:W4403323960; openalex:W2798280964; openalex:W3012463097; openalex:W3200689778; openalex:W4312347618

---

Idea 2
Title:
Counterfactual Mask-Crop Consensus for Calibrated Material and Property Uncertainty

Core proposal:
A metric-improvement and uncertainty-calibration proposal that estimates object-level physical properties by querying multiple visual views derived from the same 2D image: full scene, masked object crop, background-suppressed crop, boundary-eroded crop, texture patch crops, and object-context crop. Frozen material/VLM models score each view, and a lightweight consensus-calibration module converts disagreement into uncertainty and failure_warning fields. The final JSON reports property distributions rather than unqualified point estimates, with evidence indicating which crop types supported the prediction.

Motivation or baseline weakness:
Current plug-and-play pipelines can produce plausible but poorly grounded property estimates because material predictions depend heavily on crop choice, background context, and prompt wording. Disagreement across counterfactual crops is a cheap uncertainty signal available from a single RGB image. This idea is publishable because it targets selective risk and calibration without large-scale training, and it turns known limitations of SAM/CLIP/VLM workflows into measurable uncertainty signals.

Mechanism or approach:
Direct baselines: GroundingDINO plus SAM/SAM2 for object masks, CLIP/OpenSurfaces/MINC for material scoring, and BLIP-2/LLaVA/Qwen-VL for textual evidence and property guesses. Transfer baselines: uncertainty-aware segmentation ideas from SAM adaptation surveys and prompt-based VLM consistency checking. Borrowed components: promptable segmentation, masked crop generation, visual-language prompting, and material-property lookup tables. New component: Counterfactual Crop Consensus Calibration, a small module that aggregates material and property predictions across controlled image perturbations and calibrates prediction intervals using conformal or temperature-scaling-style validation on proxy labels. Minimal new module: a consensus scorer using features such as entropy, top-k variance, crop disagreement, prompt disagreement, mask stability, and context dependence. Ablations: single crop versus multi-crop consensus, no VLM rationale, no mask erosion/dilation, no context crop, CLIP-only versus CLIP plus VLM, uncalibrated entropy versus calibrated conformal intervals, and segmentation confidence versus material disagreement. MVP artifacts: crop generator, prompt set, frozen-model inference wrapper, consensus feature extractor, interval calibrator, JSON exporter, and selective-risk evaluator. Risks: crop perturbations may create artifacts, VLM rationales may be post-hoc, validation proxy labels may not transfer, and consensus may penalize genuinely ambiguous but correct context-dependent predictions. Failure criteria: calibration_error does not improve over raw model confidence, selective_risk is not reduced when abstaining on high-uncertainty objects, or prediction_interval_coverage improves only by producing unusably wide intervals.

Experiment and implementation plan:
Datasets: OpenRooms, ScanNet, and Matterport3D images with generated or existing masks; OpenSurfaces/MINC for material labels; ObjectFolder/ObjectFolder2.0 and engineering tables for physical-property proxy intervals. Metrics: material_accuracy, material_macro_f1, material_top3_accuracy, density_log_mae, youngs_modulus_log_mae, poisson_ratio_mae, hardness_mae_or_ordinal_error, friction_coefficient_mae, prediction_interval_coverage, calibration_error, and selective_risk. Run frozen baselines on standardized crop variants, learn a lightweight calibrator on a held-out validation split, and evaluate whether uncertainty predicts material/property errors. Report curves for risk versus coverage, interval width versus coverage, and failure_warning precision on cases with occlusion, specular surfaces, transparent materials, fabric coverings, and small objects.

Evidence paper IDs:
openalex:W3022851742; openalex:W4391809438; openalex:W4367665525; openalex:W4416850904; openalex:W4385327621; openalex:W4399597788; openalex:W4402155831; openalex:W2798280964; openalex:W4312347618

---

Idea 3
Title:
Object-Scene Material Graph Priors for Property Prediction in Indoor Images

Core proposal:
An engineering-integration proposal that builds a lightweight object-scene material graph from a single indoor RGB image and uses it to regularize object-level physical-property predictions. Nodes represent detected objects, candidate materials, scene type, support/contact relations inferred from 2D geometry, and property distributions. Edges encode priors such as chair-seat-fabric, table-top-wood/glass, sink-metal/ceramic, floor-wood/tile/carpet, and object co-occurrence constraints. The system remains plug-and-play: frozen detectors, segmenters, material recognizers, and VLMs produce candidates; a small graph inference layer re-ranks materials and property intervals before emitting structured JSON.

Motivation or baseline weakness:
Material and physical-property predictions are not independent across indoor objects. Scene context and object relations can disambiguate visually weak cues: a shiny rectangular surface on a dining table may be glass; a soft-looking sofa region likely maps to fabric/foam; a kitchen counter differs from a wooden desk despite similar color. Existing baselines can detect, segment, and caption objects, but they do not explicitly enforce object-scene consistency in property outputs. A graph prior can improve metric performance with minimal training and provides interpretable evidence.

Mechanism or approach:
Direct baselines: GroundingDINO/SAM or Mask2Former for object masks, CLIP/OpenSurfaces/MINC for material candidates, LLaVA/Qwen-VL/BLIP-2 for scene and relation descriptions, ObjectFolder/ObjectFolder2.0 plus engineering tables for property priors. Transfer baselines: SceneGPT-style scene reasoning and 3D scene graph prompting, adapted to single RGB and 2D object masks rather than requiring 3D training. Borrowed components: open-vocabulary grounding, segmentation, VLM scene parsing, material classifiers, and physical-property tables. New component: Object-Scene Material Graph Inference, a factor graph or graph neural re-ranker with frozen embeddings and small learned weights that combines visual material likelihoods with object-category, room-type, support/contact, and co-occurrence priors. Minimal new module: a graph re-ranking layer trained on proxy material labels and property intervals. Ablations: independent object predictions versus graph priors, scene-type edge removal, contact/support edge removal, VLM relation removal, learned graph weights versus hand-coded priors, and graph over material labels only versus graph over property intervals. MVP artifacts: scene graph extractor, relation heuristics from boxes/masks, material-property node schema, graph inference module, evidence trace generator, and JSON output validator. Risks: priors can reinforce dataset bias, unusual objects may be incorrectly normalized to common materials, 2D spatial relations are noisy, and VLM scene descriptions may hallucinate. Failure criteria: graph priors reduce material_macro_f1 on rare materials, improve common categories while worsening long-tail selective risk, or generate overconfident incorrect intervals for atypical object-material combinations.

Experiment and implementation plan:
Datasets: ScanNet and Matterport3D for indoor object context and room-level co-occurrence; OpenRooms for material-rich indoor renderings; OpenSurfaces/MINC for material supervision; ObjectFolder/ObjectFolder2.0 and engineering tables for property priors. Metrics: object_recall, mask_iou, material_accuracy, material_macro_f1, material_top3_accuracy, density_log_mae, youngs_modulus_log_mae, poisson_ratio_mae, hardness_mae_or_ordinal_error, friction_coefficient_mae, prediction_interval_coverage, calibration_error, and selective_risk. Compare independent per-object prediction, VLM-only JSON prediction, category-scene lookup, and the proposed graph re-ranker. Evaluate by room type and object category, with special analysis on long-tail and atypical material cases. Include human audit of evidence fields to verify that graph-based changes are supported by visible object, material, or scene-context cues rather than unsupported priors.

Evidence paper IDs:
openalex:W4402427278; openalex:W4399597788; openalex:W4385327621; openalex:W4411238954; openalex:W4402500749; openalex:W3047386722; openalex:W2798280964; openalex:W4391722892; openalex:W4327630646

---

## Item 13: HUM-3eba5986cd

类型：`portfolio`

### Candidate A

Idea 1
Title:
Mask-Conditioned Material-to-Property Retrieval With Interval-Valued Engineering Priors

Core proposal:
A plug-and-play workflow that combines open-vocabulary object detection, promptable segmentation, localized material recognition, and a lightweight retrieval layer over material-property tables to predict object-level density, Young's modulus, Poisson's ratio, hardness, and friction coefficient from a single indoor RGB image. The core novelty is not another end-to-end predictor, but a calibrated object-mask-conditioned material-to-property retriever that returns physically plausible intervals and evidence traces instead of overconfident point estimates.

Motivation or baseline weakness:
Directly regressing mechanical properties from a single RGB image is underdetermined because hidden structure, coatings, composites, and manufacturing variation are usually invisible. Existing baselines such as GroundingDINO, SAM/SAM2, CLIP, OpenSurfaces, MINC, and VLMs can identify objects, masks, and material cues, but they do not by themselves enforce physically plausible property ranges or expose evidence. This idea treats property prediction as evidence-grounded retrieval and interval estimation: visible material cues plus object category and scene context constrain a distribution over likely materials, which then maps to property intervals using ObjectFolder/ObjectFolder2.0 and engineering material tables.

Mechanism or approach:
Direct baselines: GroundingDINO plus SAM/SAM2 for object boxes and masks; CLIP, OpenSurfaces, and MINC classifiers for material labels; LLaVA or Qwen-VL prompting for object-context descriptions; ObjectFolder/ObjectFolder2.0 and engineering material tables for property lookup. Transfer baselines: BLIP-2/LLaVA-style image-to-text evidence generation and SceneGPT-style context reasoning, used only as frozen contextual priors. Borrowed components: frozen detector, frozen segmenter, frozen CLIP/material encoders, material-property database, conformal interval calibration. New component: a small Masked Material Property Retriever that takes cropped RGB, mask, object category, local texture features, global scene context, and candidate material names, then outputs a ranked material mixture and property intervals. The module can be implemented as a lightweight adapter or gradient-boosted/ridge regression head over frozen embeddings. For each object, the output JSON includes object_id, category, mask_or_box, predicted_materials, physical-property medians and intervals, confidence_or_uncertainty, visual/textual evidence, and failure_warning. Why it may work: material classes strongly constrain many physical-property ranges even when exact values are unknowable; combining object category with localized mask evidence should reduce semantic hallucination compared with whole-image VLM prompting; interval-valued outputs better match the inherent ambiguity of single-view RGB.

Experiment and implementation plan:
Datasets: ScanNet, Matterport3D, and OpenRooms for indoor RGB scenes and object/mask/category evaluation; OpenSurfaces and MINC for material supervision; ObjectFolder/ObjectFolder2.0 plus engineering material-property tables for density, Young's modulus, Poisson's ratio, hardness, and friction coefficient targets or intervals. Metrics: object_recall and mask_iou for detection/segmentation; material_accuracy, material_macro_f1, and material_top3_accuracy for material prediction; density_log_mae, youngs_modulus_log_mae, poisson_ratio_mae, hardness_mae_or_ordinal_error, and friction_coefficient_mae for property prediction where point or midpoint labels exist; prediction_interval_coverage, calibration_error, and selective_risk for uncertainty. Ablations: box crop versus mask crop; CLIP only versus OpenSurfaces/MINC ensemble; object category removed; scene context removed; point lookup versus interval retrieval; frozen embeddings versus lightweight adapter. Risks: material labels may be too coarse for mechanical properties; tables may disagree across sources; visible surface may not match internal material; friction depends on surface condition and counterpart material. Failure criteria: no improvement over CLIP-plus-table lookup on material_macro_f1 or top3 material accuracy; property interval coverage below the nominal level by more than 10 percentage points; selective risk does not decrease when low-confidence predictions are abstained; evidence fields frequently cite non-localized or irrelevant visual cues. Minimal new module: a mask-conditioned retrieval/calibration head over frozen visual and text embeddings. MVP artifacts: a runnable RGB-to-JSON demo, a material-property database schema, a benchmark split with proxy interval labels, calibration plots, and per-object evidence visualizations. Implementation plan: first build GroundingDINO/SAM object extraction; then attach frozen material recognizers; then normalize material-property tables into common units; then train the lightweight retriever on OpenSurfaces/MINC/ObjectFolder-linked labels; then calibrate intervals on held-out scenes; finally evaluate against CLIP/VLM prompting and table-lookup baselines.

Evidence paper IDs:
openalex:W4402427278; openalex:W4402500749; openalex:W4411238954; openalex:W3022851742; openalex:W4403323960; openalex:W4385327621; openalex:W2798280964; openalex:W3046559354; openalex:W4391722892; openalex:W4312347618

---

Idea 2
Title:
Self-Consistency and Counterfactual Prompting for Calibrated Object Property JSON

Core proposal:
A VLM-centered engineering-integration and uncertainty-calibration proposal that wraps existing object detection, segmentation, material recognition, and VLM baselines in a self-consistency verifier. Instead of trusting one VLM answer, the system asks multiple localized, counterfactual, and evidence-seeking questions for each masked object, reconciles them with material-property tables, and emits calibrated JSON with explicit failure warnings.

Motivation or baseline weakness:
Vision-language models can use object category and scene context to infer likely materials, but their outputs are prompt-sensitive and may be unsupported by localized visual evidence. For physical properties, this is dangerous: a model may confidently assign steel-like stiffness to a painted plastic object or confuse veneer with solid wood. The research opportunity is to turn VLMs into cautious evidence aggregators rather than direct regressors, using self-consistency, contradiction checks, and table-grounded plausibility filters to improve uncertainty calibration and selective risk without large-scale training.

Mechanism or approach:
Direct baselines: LLaVA, Qwen-VL, and BLIP-2 for object- and material-level visual questioning; GroundingDINO plus SAM/SAM2 or Mask2Former for visible object masks; CLIP/OpenSurfaces/MINC for independent material votes; ObjectFolder/ObjectFolder2.0 and engineering material-property tables for physical-property ranges. Transfer baselines: SceneGPT-style prompt decomposition for spatial/context reasoning, and foundation-model prompting approaches that avoid task-specific large-scale training. Borrowed components: frozen VLMs, frozen segmentation, material classifiers, ensemble/self-consistency voting, conformal prediction, and rule-based unit normalization. New component: a Property Consistency Verifier that generates structured prompts per object: visible material evidence, alternative plausible materials, object function, scene context, surface finish, and known ambiguity. It scores agreement among VLM answers, material classifiers, and database ranges, then outputs point estimates only when intervals are sufficiently constrained. Why it may work: VLMs are useful for commonsense object-function priors, while material classifiers provide localized texture evidence and tables enforce physical plausibility. Disagreement is informative and can be converted into calibrated uncertainty and failure warnings.

Experiment and implementation plan:
Datasets: ScanNet, Matterport3D, and OpenRooms for indoor images; OpenSurfaces and MINC for material labels; ObjectFolder/ObjectFolder2.0 and engineering tables for property priors and interval labels. Metrics: material_accuracy, material_macro_f1, material_top3_accuracy, density_log_mae, youngs_modulus_log_mae, poisson_ratio_mae, hardness_mae_or_ordinal_error, friction_coefficient_mae, prediction_interval_coverage, calibration_error, and selective_risk. Detection and segmentation are evaluated with object_recall and mask_iou but are also analyzed as upstream error sources. Ablations: single direct VLM prompt versus decomposed prompts; no counterfactual material alternatives; no independent material-classifier vote; no table plausibility filter; no conformal calibration; masks versus boxes; global image prompt versus object crop plus mask. Risks: VLM responses may be unstable across versions; prompt ensembles increase latency; table-grounded filters can reject correct rare materials; material-property ranges may be too broad to improve point metrics. Failure criteria: self-consistency does not improve calibration_error or selective_risk over a single-prompt VLM baseline; contradiction score is uncorrelated with actual property error; prediction intervals become so wide that they are uninformative; VLM evidence frequently references invisible or hallucinated attributes. Minimal new module: a prompt orchestration and consistency-scoring layer with conformal calibration. MVP artifacts: prompt templates, object-level JSON schema, consistency score implementation, disagreement heatmaps, calibration curves, and a leaderboard comparing single-prompt VLM, material-classifier lookup, and verifier outputs. Implementation plan: assemble object masks from GroundingDINO/SAM; generate object crops and masked images; query frozen VLMs with standardized prompts; collect CLIP/OpenSurfaces/MINC material votes; map candidate materials to property distributions; compute agreement and calibrated intervals; evaluate per object and per material family; release failure-warning taxonomy for hidden core, coating, transparent material, specular ambiguity, occlusion, and low-resolution texture.

Evidence paper IDs:
openalex:W4399597788; openalex:W4402155831; openalex:W4417250113; openalex:W4392222076; openalex:W4385327621; openalex:W4402427278; openalex:W4402500749; openalex:W4411238954; openalex:W2798280964; openalex:W4312347618

---

Idea 3
Title:
Property-Aware Mask Selection and Surface-Evidence Scoring for Indoor Objects

Core proposal:
An incremental but publishable improvement focused on the segmentation-to-property bottleneck: selecting the object mask or visible surface region that best supports material and physical-property inference. The method augments GroundingDINO/SAM/SAM2 or Mask2Former outputs with a lightweight property-aware surface-evidence scorer that ranks masks, suppresses misleading regions, and estimates when a visible surface is insufficient for property prediction.

Motivation or baseline weakness:
Most pipelines assume that if an object is detected and segmented, downstream material and property prediction can proceed. In practice, physical properties are often inferred from small visible surface regions: upholstery texture, wood grain, metal specularity, ceramic glaze, rubber feet, or plastic seams. Generic masks may include shadows, clutter, transparent regions, labels, reflections, or mixed materials. Improving mask/surface selection can raise material accuracy and uncertainty calibration without training a large physical-property model.

Mechanism or approach:
Direct baselines: GroundingDINO for open-vocabulary boxes; SAM/SAM2 and Mask2Former for masks; CLIP, OpenSurfaces, and MINC for material recognition; ObjectFolder/ObjectFolder2.0 and engineering tables for property supervision. Transfer baselines: efficient SAM variants and interactive segmentation ideas suggest lightweight adaptation rather than full retraining; surface-defect and material-texture recognition motivate scoring local regions instead of whole masks. Borrowed components: promptable segmentation, mask proposals, frozen visual embeddings, texture descriptors from material classifiers, and uncertainty-aware calibration. New component: a Property-Aware Surface Evidence Scorer that decomposes each object mask into candidate visible patches, scores each patch for material informativeness, detects mixed-material objects, and passes only high-evidence patches to the material/property retriever. The scorer uses lightweight adapters or classical features over frozen embeddings and can be trained with proxy labels: material-classifier agreement, entropy reduction, table-consistency, and human-labeled evidence regions for a small validation set. Why it may work: property estimates are only as good as the material evidence; suppressing non-informative pixels and identifying mixed surfaces should improve material prediction and prevent overconfident property estimates.

Experiment and implementation plan:
Datasets: ScanNet, Matterport3D, and OpenRooms for indoor object instances; OpenSurfaces and MINC for material patch supervision; ObjectFolder/ObjectFolder2.0 and engineering tables for object/material-to-property proxy labels. Metrics: object_recall and mask_iou for segmentation; material_accuracy, material_macro_f1, and material_top3_accuracy for material classification using selected patches; density_log_mae, youngs_modulus_log_mae, poisson_ratio_mae, hardness_mae_or_ordinal_error, and friction_coefficient_mae for downstream property estimates; prediction_interval_coverage, calibration_error, and selective_risk for uncertainty. Ablations: full object mask versus top-k evidence patches; SAM versus SAM2 versus Mask2Former proposals; no mixed-material detection; no scene-context feature; no entropy/evidence score; patch-level CLIP only versus OpenSurfaces/MINC features; lightweight adapter versus zero-shot scoring. Risks: evidence scoring may discard subtle but useful context; small patches may lack enough pixels; mixed-material annotations are expensive; improvements in material accuracy may not translate to property-error reductions because table ranges dominate. Failure criteria: selected patches do not improve material_macro_f1 over full-mask crops; mask_iou gains do not correlate with property metrics; uncertainty calibration worsens due to overconfident patch selection; the scorer fails on transparent, glossy, or heavily occluded objects. Minimal new module: a patch-level evidence scorer and mask/patch selection policy over frozen segmentation and material features. MVP artifacts: mask proposal cache, patch scorer, visualization overlay of selected evidence regions, object-level JSON output with evidence patches and failure warnings, and an evaluation script linking patch selection to material and property metrics. Implementation plan: generate multiple masks per object from GroundingDINO prompts and SAM/SAM2; split masks into superpixels or fixed patches; extract frozen CLIP/OpenSurfaces/MINC features; train a lightweight scorer using material-label agreement and entropy reduction; add mixed-material and low-evidence flags; feed selected patches to the property retriever; compare against full-mask and box-crop baselines on indoor-scene splits.

Evidence paper IDs:
openalex:W4402500749; openalex:W7148178853; openalex:W4416850904; openalex:W4403323960; openalex:W4411238954; openalex:W4367665525; openalex:W2798280964; openalex:W2895238724; openalex:W3046559354; openalex:W4312347618

### Candidate B

Idea 1
Title:
Object-Material Interval Lookup With Evidence-Gated Mixture Predictions

Core proposal:
For each detected object mask, estimate a posterior over visible material families from masked-crop evidence using frozen material recognizers and prompt-based material scoring. Combine this posterior with an object-category compatibility prior and a scene-context compatibility prior, then map each retained material family to engineering-property intervals. The output is a calibrated mixture distribution per property, represented by mean, central interval, confidence, top contributing material hypotheses, and explicit warnings when the visible material is insufficient to infer bulk composition. Candidate materials are retained only if they pass three gates: localized mask evidence above a validation-tuned threshold, compatibility with the predicted object category, and no contradiction with coarse scene context such as floor, wall, furniture, appliance, or container role.

Motivation or baseline weakness:
CLIP/OpenSurfaces/MINC-style material recognition can provide plausible visible-material labels, but a single RGB crop often cannot identify hidden composition, coatings, laminates, or exact material grade. Direct point estimates for density, Young's modulus, hardness, Poisson's ratio, and friction therefore become overconfident when the visual evidence supports only a broad material family.

Mechanism or approach:
A lightweight property-interval resolver: a table-backed probabilistic mapper that normalizes material names, combines material posterior, object-category prior, and engineering material-property ranges, and emits per-property mean, prediction interval, confidence, evidence strings, and failure_warning fields.
Train only calibration and mixture weights while keeping detectors, segmenters, and frozen material recognizers fixed. Minimize interval-aware negative log likelihood plus log-space absolute error on proxy-labeled object-property data, with a penalty for intervals narrower than their empirical validation coverage supports: objective = property_log_mae + lambda * calibration_error + beta * undercoverage_penalty + rho * unsupported_narrow_interval_penalty. Interval width is not minimized directly unless nominal coverage is satisfied on validation objects.

Experiment and implementation plan:
GroundingDINO + SAM + CLIP point-property lookup; GroundingDINO + SAM + OpenSurfaces material lookup; GroundingDINO + SAM + MINC material lookup; LLaVA prompted JSON property prediction
Indoor RGB images with object boxes or masks, evaluated only at object level; Material labels or proxy material labels mapped to OpenSurfaces and MINC-compatible classes; Object-category to plausible-visible-material mappings for indoor objects; Engineering material-property tables with intervals for density, Young's modulus, Poisson's ratio, hardness, and friction coefficient, normalized to shared material-family names; Optional ObjectFolder/ObjectFolder2.0 objects with known or proxy physical properties for validation of the property-table mapping rather than scene-level training
run_detection_segmentation.py to produce object_id, category, mask_or_box, detection_score, and mask_quality_score using GroundingDINO plus SAM or SAM2; extract_masked_material_scores.py to score masked crops, box crops, and full images with CLIP/OpenSurfaces/MINC-compatible material labels; build_property_interval_table.py to normalize material aliases, units, and property ranges and to flag material families with grade-dependent ranges; resolve_property_mixture.py to combine material posteriors and property intervals into structured JSON with top contributors and failure_warning values; evaluate_property_intervals.py to compute log MAE, interval coverage, calibration error, material metrics, and selective risk on the same detected objects
object_recall; mask_iou; material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Remove object-category prior and use material visual posterior only; Remove scene-context compatibility prior; Use top-1 material only instead of mixture over top-k materials; Use table medians as point estimates instead of calibrated intervals; Replace SAM masks with boxes to test sensitivity to localized material evidence
Shuffle material-property table rows while keeping material labels fixed; property metrics should degrade while material metrics remain similar; Use full-image CLIP scores instead of masked object crops; locality-sensitive material classes should degrade; Assign category-frequency material priors without visual evidence; confidence should be lower and selective risk should worsen on visually atypical objects; Force all objects to a generic plastic/wood/metal prior depending only on superclass; improvements over this control must come from localized evidence; Evaluate with masks shifted to nearby background regions; material support and confidence should drop
Improve density_log_mae by at least 10% over top-1 CLIP property lookup on the same detected objects; Improve youngs_modulus_log_mae by at least 10% over top-1 material lookup on the same detected objects; Achieve prediction_interval_coverage within 5 percentage points of the nominal 90% interval target; Reduce calibration_error by at least 15% relative to LLaVA prompted point estimates with self-reported confidence; Do not reduce material_top3_accuracy by more than 2 percentage points compared with the best frozen material recognizer on the same masks

Evidence paper IDs:
openalex:W4402427278; openalex:W4402500749; openalex:W2798280964; openalex:W3012463097; openalex:W3046559354; openalex:W3200689778; openalex:W4312347618

Risks, controls, or fallback:
Risk: proxy property intervals may be too broad to show useful metric gains, and visual cues may not distinguish laminates, coatings, composites, or hidden internal materials. Fallback: report conservative intervals with explicit failure_warning values for ambiguous or hidden-composition cases, evaluate selective prediction by abstaining when material posterior entropy or table range width exceeds a threshold, and separately report visible-material accuracy so property errors are not mistaken for segmentation failures.

---

Idea 2
Title:
Mask-Conditioned Material Evidence Verification for VLM Property JSON

Core proposal:
Insert a verifier between segmentation and final property output. A VLM first proposes object category, material hypotheses, property intervals, and natural-language evidence. Each proposed material is then checked against masked-crop evidence using frozen CLIP/material classifiers and counterfactual material prompts. The verifier accepts, widens, or flags the VLM output according to three tests: the proposed material must score higher on the masked crop than on unrelated background or full-image context, it must be plausible for the object category without being category-only, and it must exceed visually confusable counterfactual materials by a validation-calibrated margin. Unsupported claims are not replaced by a new point estimate; they are converted to wider property intervals with failure_warning fields.

Motivation or baseline weakness:
Vision-language models such as LLaVA, BLIP-2, and Qwen-VL can produce plausible object-level physical-property JSON, but their material and property claims may be unsupported by localized visual evidence, sensitive to prompt wording, and influenced by object-category priors rather than the pixels inside the target mask.

Mechanism or approach:
A material-evidence verifier that computes per-object support scores from masked-crop similarity, mask-versus-full-image leakage contrast, category plausibility, and counterfactual material margins, then rescales property confidence and interval width without fine-tuning the VLM.
Fit verifier thresholds and calibration parameters on validation proxy labels while keeping VLMs and visual encoders frozen. Optimize material support and calibrated acceptance: objective = material_cross_entropy_proxy + alpha * counterfactual_margin_loss + gamma * confidence_calibration_loss + tau * unsupported_acceptance_penalty, with low-support predictions handled by abstention or interval widening rather than forced relabeling.

Experiment and implementation plan:
LLaVA prompted structured JSON prediction; BLIP-2 prompted structured JSON prediction; Qwen-VL prompted structured JSON prediction; GroundingDINO + SAM + CLIP material-to-property lookup
Indoor RGB images evaluated at object level; Object masks or boxes generated by GroundingDINO plus SAM/SAM2 or Mask2Former; Material class labels or proxy labels mapped to OpenSurfaces and MINC-compatible classes; Engineering material-property intervals linked to material classes; Prompt templates for VLM object category, material hypotheses, localized evidence, uncertainty, and property JSON
prompt_vlm_property_json.py to collect baseline VLM object-level predictions with multiple prompt paraphrases and self-reported confidence; score_local_material_evidence.py to compare masked crop, box crop, background crop, and full-image material scores; run_counterfactual_material_prompts.py to score visually confusable alternatives such as wood veneer versus plastic laminate, metal versus painted plastic, leather versus vinyl, and ceramic versus stone; calibrate_verifier.py to fit support thresholds, confidence scaling, and widening rules on validation proxy labels; evaluate_verified_json.py to compare accepted, widened, rejected, and raw VLM predictions under identical detected objects
material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Verifier without counterfactual material prompts; Verifier without full-image leakage contrast; Verifier using box crops instead of masks; No interval widening for unsupported VLM claims; Use VLM self-confidence only instead of verifier confidence
Verify each object using another random object's mask crop; accepted support should decrease; Use full-scene material scores as if they were object-local evidence; locality-sensitive calibration should degrade; Swap object categories while keeping masks fixed; category-plausibility-only acceptance should be exposed; Use adversarially broad prompts that list all common indoor materials as evidence; verifier should not accept all listed materials; Randomize the VLM material string before verification; acceptance and property accuracy should drop
Reduce calibration_error by at least 20% relative to raw VLM self-confidence; Reduce selective_risk by at least 15% at 70% object coverage relative to raw VLM predictions; Improve material_macro_f1 by at least 5 points over raw VLM material labels on proxy-labeled objects; Maintain or improve density_log_mae and youngs_modulus_log_mae on accepted predictions compared with CLIP top-1 lookup on the same objects; At least 80% of emitted failure_warning cases must correspond to high material ambiguity, mask error, visible-surface versus bulk-material mismatch, or category-property mismatch under manual audit

Evidence paper IDs:
openalex:W4399597788; openalex:W4392222076; openalex:W4402155831; openalex:W4385327621; openalex:W4402500749; openalex:W2798280964; openalex:W2895238724

Risks, controls, or fallback:
Risk: the verifier may reject too many objects because material datasets do not align with indoor object appearances, or because VLM predictions are correct at the object-category level but not visually verifiable from the crop. Fallback: use verifier scores for uncertainty calibration and interval widening rather than hard rejection, report selective-risk curves across acceptance thresholds, and keep a separate category-prior-only baseline to show whether gains come from localized evidence rather than semantic priors.

---

Idea 3
Title:
Segmentation-Property Sensitivity Calibration via Mask Perturbation Ensembles

Core proposal:
Generate a compact ensemble of plausible masks per detected object using alternative segmentation backbones, prompt perturbations, score-threshold variants, and controlled mask erosions/dilations. Run the same frozen material-to-property resolver on every mask sample. Estimate mask-induced epistemic uncertainty from dispersion in material posteriors and property intervals, then widen final intervals and add failure_warning tags when predictions are sensitive to mask choice. The method attributes uncertainty specifically to segmentation by comparing perturbations around the same detection and by separating mask-induced dispersion from material-posterior entropy.

Motivation or baseline weakness:
GroundingDINO/SAM/SAM2/Mask2Former pipelines can produce useful object masks, but small mask errors can include background, shadows, or adjacent objects, or exclude material-discriminative regions. Downstream material and physical-property estimates can therefore be unstable even when object recall and average mask IoU appear acceptable.

Mechanism or approach:
A mask-sensitivity calibrator that creates low-cost mask perturbation ensembles, measures property dispersion and material-posterior disagreement across masks, and converts that dispersion into calibrated uncertainty intervals and object-level failure_warning tags.
Fit only the dispersion-to-uncertainty calibration layer while keeping segmentation models and material/property resolver fixed. Minimize property error and uncertainty miscalibration under mask perturbations: objective = mean property_log_mae across mask samples + eta * interval_coverage_loss + zeta * high_confidence_high_variance_penalty + kappa * mask_quality_monotonicity_loss, where confidence should decrease as mask-induced variance or mask-quality disagreement increases.

Experiment and implementation plan:
GroundingDINO + SAM single-mask pipeline; GroundingDINO + SAM2 single-mask pipeline; Mask2Former single-mask pipeline; GroundingDINO + SAM + CLIP/OpenSurfaces material lookup without uncertainty propagation
Indoor scene images evaluated at object level; Available ground-truth or pseudo object masks for mask_iou evaluation and for stratifying results by mask quality; Proxy material labels from OpenSurfaces/MINC-compatible mappings; Engineering property tables for material-to-property intervals; Optional ObjectFolder/ObjectFolder2.0 rendered or photographed objects with property annotations or proxy labels to test whether mask-induced uncertainty transfers to isolated-object settings
generate_mask_ensemble.py to run SAM, SAM2, Mask2Former, prompt perturbations, threshold variants, and morphological mask variants while preserving object_id alignment; run_property_resolver_on_masks.py to compute material posterior, property interval, and evidence fields for each mask sample; fit_mask_sensitivity_calibrator.py to map ensemble dispersion, mask IoU proxies, and material entropy to calibrated confidence intervals; evaluate_mask_property_sensitivity.py to correlate mask_iou, material error, property error, interval coverage, and uncertainty; export_object_property_json.py to produce final structured JSON with selected mask, ensemble summary, evidence, and warnings
object_recall; mask_iou; material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Use only one segmentation model instead of multi-source mask ensemble; Use morphological perturbations only without SAM/SAM2/Mask2Former diversity; Use ensemble mean without uncertainty calibration; Remove mask-sensitivity failure warnings; Replace masks with bounding boxes for all property predictions
Randomly perturb masks outside the object region to test whether sensitivity is merely noise-driven; Use identical duplicated masks as an ensemble, which should not improve calibration; Shuffle ensemble property predictions across objects before calibration; any calibration gain should disappear; Calibrate uncertainty from object category frequency rather than mask-induced dispersion; Apply perturbations to background-only masks; material confidence should remain low and warnings should increase
Improve prediction_interval_coverage to within 5 percentage points of nominal 90% while keeping intervals narrower than a category-only prior baseline; Reduce calibration_error by at least 15% compared with single-mask CLIP/OpenSurfaces lookup; Reduce selective_risk by at least 10% at fixed 80% object coverage; Identify high-risk mask-sensitive objects with at least 70% precision in manual audit; Do not reduce object_recall by more than 1 percentage point relative to the best single-mask pipeline because calibration should operate after detection rather than filtering detections by default

Evidence paper IDs:
openalex:W4402500749; openalex:W7148178853; openalex:W4416850904; openalex:W4403323960; openalex:W4411238954; openalex:W4385327621; openalex:W2798280964

Risks, controls, or fallback:
Risk: mask perturbation may overestimate uncertainty for highly textured objects, underestimate uncertainty when all segmenters share the same systematic error, or conflate segmentation uncertainty with intrinsic material ambiguity. Fallback: report separate components for mask-induced dispersion, material-posterior entropy, and category-property prior width; if all masks agree but visual evidence conflicts with category priors, emit a persistent evidence_conflict failure_warning rather than a confident property prediction.

---

## Item 14: HUM-c879276618

类型：`portfolio`

### Candidate A

Idea 1
Title:
Uncertainty-Aware Material-to-Property Retrieval for Segmented Indoor Objects

Core proposal:
A plug-and-play workflow that combines open-vocabulary object detection, promptable segmentation, localized material recognition, and retrieval from physical-property tables to produce object-level JSON predictions for density, Young's modulus, Poisson's ratio, hardness, and friction coefficient. The core idea is to avoid direct regression from RGB and instead predict a calibrated distribution over visible materials, retrieve material-property intervals from ObjectFolder/ObjectFolder2.0 and engineering tables, and propagate uncertainty into final property intervals with explicit failure warnings.

Motivation or baseline weakness:
Single RGB indoor images often do not reveal hidden material composition, coatings, hollow structure, or manufacturing process, so point estimates for physical properties are likely overconfident. Existing baselines such as GroundingDINO, SAM/SAM2, CLIP, OpenSurfaces, MINC, LLaVA, Qwen-VL, ObjectFolder, and ObjectFolder2.0 cover detection, segmentation, material recognition, language priors, and property sources, but they do not by themselves provide a calibrated object-level physical-property workflow. This proposal is publishable as a rigorous integration and calibration study: the novelty is not a new foundation model, but a physically grounded probabilistic bridge from visible material evidence to property intervals and failure-aware JSON outputs.

Mechanism or approach:
Direct baselines: GroundingDINO+SAM/SAM2 for object masks, CLIP/OpenSurfaces/MINC for material classification, ObjectFolder/ObjectFolder2.0 plus engineering material-property tables for physical-property lookup. Transfer baselines: LLaVA or Qwen-VL as contextual object/material priors and SceneGPT-style scene reasoning for object-context consistency. Borrowed components: frozen detector, frozen segmenter, frozen material encoders, frozen VLM captioning/context module, and static property tables. New component: a lightweight Material-Property Evidence Graph that maps each object to a posterior over candidate materials and property intervals. The graph combines localized crop evidence, mask-level texture/color features, object category priors, room context, and table-derived property distributions. It outputs structured JSON with object_id, object_category, mask_or_box, predicted_materials, density, youngs_modulus, poisson_ratio, hardness, friction_coefficient, confidence_or_uncertainty, evidence, and failure_warning. Minimal new module: a small calibration-and-fusion layer trained on proxy material labels and interval labels, preferably temperature scaling plus a shallow MLP or logistic calibration model over frozen features. Why it may work: physical properties are often better estimated through material identity and category-conditioned priors than through unconstrained image-to-property regression; interval retrieval also naturally represents ambiguity from single RGB images.

Experiment and implementation plan:
Datasets: ScanNet, Matterport3D, and OpenRooms for indoor scenes; OpenSurfaces and MINC for material supervision; ObjectFolder/ObjectFolder2.0 and engineering tables for property intervals. Metrics: object_recall and mask_iou for detection/segmentation; material_accuracy, material_macro_f1, and material_top3_accuracy for materials; density_log_mae, youngs_modulus_log_mae, poisson_ratio_mae, hardness_mae_or_ordinal_error, and friction_coefficient_mae for physical properties where labels/proxies exist; prediction_interval_coverage, calibration_error, and selective_risk for uncertainty. Ablations: remove scene context, remove object-category priors, replace interval retrieval with direct regression, use boxes instead of masks, use CLIP-only versus OpenSurfaces/MINC material heads, compare SAM versus SAM2, and compare calibrated versus uncalibrated property intervals. MVP artifacts: runnable pipeline, material-property table schema, calibration splits, JSON output validator, evidence visualization overlay, and evaluation notebook. Implementation plan: first build GroundingDINO+SAM/SAM2 object extraction; second compute masked material predictions from frozen material models; third normalize material names into a controlled ontology; fourth attach property distributions from tables/ObjectFolder; fifth calibrate material and property uncertainty on held-out proxy labels; sixth produce object-level JSON and benchmark against direct material-to-table lookup. Risks: material labels may be noisy, property tables may disagree, visible surfaces may not reflect bulk material, and VLM context may hallucinate. Failure criteria: no improvement over CLIP/OpenSurfaces/MINC lookup on material_macro_f1 or material_top3_accuracy; property interval coverage below the nominal target by more than 10 percentage points; selective risk does not improve when abstaining on low-confidence objects; or failure warnings are not correlated with high-error cases.

Evidence paper IDs:
openalex:W4402427278; openalex:W4402500749; openalex:W4411238954; openalex:W3022851742; openalex:W4391809438; openalex:W4385327621; openalex:W4399597788; openalex:W4312347618; openalex:W3200689778

---

Idea 2
Title:
Counterfactual Visual Evidence Checks for Object-Level Physical Property Prediction

Core proposal:
A failure-aware extension to standard detection-segmentation-material pipelines that tests whether predicted materials and physical properties are actually supported by localized visual evidence. The workflow generates counterfactual object crops and prompts, perturbs material cues such as texture/color/reflectance descriptors, and measures prediction stability before emitting physical-property estimates. The method is designed as an uncertainty-calibration and reliability improvement layer that can be attached to GroundingDINO, SAM/SAM2, CLIP, OpenSurfaces, MINC, LLaVA, or Qwen-VL.

Motivation or baseline weakness:
Vision-language and material-recognition baselines may infer plausible materials from category or context rather than from the pixels of the visible object. For physical properties, this is risky: a chair may be wood, plastic, metal, composite, upholstered, hollow, or coated, with very different density and elastic properties. Current baselines provide predictions but not a direct test of whether those predictions depend on object-local visual evidence. A publishable contribution is an evidence-stress-testing module that improves calibration and failure warnings without large-scale training.

Mechanism or approach:
Direct baselines: GroundingDINO+SAM/SAM2 or Mask2Former for object masks, CLIP/OpenSurfaces/MINC for material predictions, LLaVA/Qwen-VL for object-context descriptions, and ObjectFolder/ObjectFolder2.0/property tables for property values. Transfer baselines: SAM uncertainty-aware adaptation ideas and VLM prompt-consistency checks. Borrowed components: frozen segmentation, frozen material/VLM encoders, masked crop extraction, and material-property retrieval. New component: Counterfactual Evidence Consistency Scoring. For each detected object, create a set of evidence-preserving and evidence-destroying views: masked crop, background-only crop, texture-blurred crop, color-jittered crop, grayscale crop, object-category-only prompt, context-only prompt, and mask-eroded/expanded crops. The module scores whether material and property predictions change appropriately. If the model predicts the same material from background-only or category-only views, confidence is reduced and a failure_warning is emitted. Minimal new module: a lightweight consistency-to-uncertainty calibrator that maps perturbation stability patterns to calibrated confidence intervals. Why it may work: physically meaningful predictions should be stable under irrelevant perturbations but sensitive to removal of object-local material evidence; this turns hidden hallucination into measurable uncertainty.

Experiment and implementation plan:
Datasets: ScanNet, Matterport3D, and OpenRooms for indoor object crops; OpenSurfaces and MINC for material labels; ObjectFolder/ObjectFolder2.0 plus engineering tables for property proxies. Metrics: standard object_recall and mask_iou; material_accuracy, material_macro_f1, and material_top3_accuracy; physical-property density_log_mae, youngs_modulus_log_mae, poisson_ratio_mae, hardness_mae_or_ordinal_error, and friction_coefficient_mae; uncertainty metrics prediction_interval_coverage, calibration_error, and selective_risk. Key experiments: compare base pipeline versus base pipeline plus counterfactual consistency calibration; evaluate whether background-only and category-only confidence predicts errors; test abstention policies based on evidence consistency; measure failure-warning precision for high-error cases. Ablations: remove background-only test, remove texture-blur test, remove VLM context-only prompt, use boxes instead of masks, compare SAM versus SAM2 masks, compare CLIP-only versus material-specific heads, and compare consistency-calibrated intervals versus temperature-scaled intervals. MVP artifacts: perturbation library, evidence-consistency score, calibrated uncertainty model, JSON output with evidence and failure_warning, and visualization showing which perturbations changed predictions. Implementation plan: first implement object extraction; second implement perturbation suite; third run frozen material/VLM predictions across perturbations; fourth build consistency features; fifth train/calibrate a small model against held-out material/property proxy errors; sixth evaluate selective risk and interval coverage. Risks: perturbations may introduce artifacts, some true materials are visually ambiguous even under all tests, and a stable prediction can still be wrong if all models share the same bias. Failure criteria: counterfactual module fails to reduce calibration_error or selective_risk relative to base pipeline; failure_warning does not enrich for high-error predictions; material accuracy drops more than acceptable due to over-abstention; or perturbation scores are not reproducible across detectors/segmenters.

Evidence paper IDs:
openalex:W4402500749; openalex:W4416850904; openalex:W4403323960; openalex:W4385327621; openalex:W4399597788; openalex:W4411238954; openalex:W2798280964; openalex:W2895238724; openalex:W4312347618

---

Idea 3
Title:
Category-Conditioned Mixture-of-Materials Property Estimation for Composite Indoor Objects

Core proposal:
A lightweight adapter that predicts not a single material per object but a category-conditioned mixture over visible and latent material components, then converts that mixture into physical-property distributions. The goal is to improve object-level property estimates for common indoor objects that are composites, such as chairs, sofas, cabinets, lamps, appliances, and tables, where the visible surface material alone is insufficient.

Motivation or baseline weakness:
Most material-recognition pipelines treat each object or surface patch as having one dominant material, while physical properties often depend on bulk structure and multiple components. A sofa may include fabric, foam, wood, metal springs, and plastic; a chair may combine metal legs, plastic shell, and rubber feet. Since hidden material structure cannot be fully observed from single RGB, the right output is a category-conditioned mixture with uncertainty and explicit warnings. This proposal is distinct from simple material retrieval because it models object categories as probabilistic assemblies and evaluates whether mixture priors improve physical-property estimates and calibration.

Mechanism or approach:
Direct baselines: GroundingDINO/SAM/SAM2 or Mask2Former for object masks, CLIP/OpenSurfaces/MINC for visible material predictions, BLIP-2/LLaVA/Qwen-VL for object category and context verification, and ObjectFolder/ObjectFolder2.0 plus engineering tables for property distributions. Transfer baselines: SceneGPT-like scene/context reasoning for object affordance and likely construction priors. Borrowed components: frozen object detectors, frozen segmenters, frozen material classifiers, frozen VLMs, and physical-property sources. New component: Category-Conditioned Mixture-of-Materials Adapter. The adapter takes object category, mask/crop features, visible material posterior, and scene context, then predicts a sparse distribution over material components with visible/latent flags. Physical properties are computed using conservative mixture rules and broad intervals rather than overconfident point estimates. Minimal new module: a small adapter trained from weak supervision using object-category-to-material priors mined from ObjectFolder/ObjectFolder2.0 metadata and engineering tables, with optional manual priors for common indoor categories. Why it may work: many errors in property prediction come from treating composite objects as homogeneous; category-conditioned mixtures can encode plausible hidden structure while still using visible evidence to constrain surface materials.

Experiment and implementation plan:
Datasets: ScanNet, Matterport3D, and OpenRooms for indoor scenes and object categories; OpenSurfaces and MINC for visible material labels; ObjectFolder/ObjectFolder2.0 and engineering material-property tables for object/material/property priors. Metrics: object_recall and mask_iou; material_accuracy, material_macro_f1, material_top3_accuracy; density_log_mae, youngs_modulus_log_mae, poisson_ratio_mae, hardness_mae_or_ordinal_error, friction_coefficient_mae; prediction_interval_coverage, calibration_error, and selective_risk. Experiments: compare homogeneous visible-material lookup, object-category-only lookup, VLM-only property prompting, and the proposed mixture adapter. Evaluate separately on likely homogeneous objects, likely composite objects, and ambiguous/coated objects. Ablations: remove latent-material components, remove visible-material posterior, remove category prior, remove scene context, compare hand-coded mixture rules versus learned sparse adapter, compare narrow point estimates versus interval mixture outputs, and test SAM versus Mask2Former masks. MVP artifacts: object-category/material-mixture ontology, prior table, adapter training script, property-mixture calculator, calibrated JSON emitter, and benchmark split for composite-object categories. Implementation plan: first construct a normalized ontology linking categories, materials, and property tables; second run object detection/segmentation and visible material inference; third initialize category-mixture priors from ObjectFolder/ObjectFolder2.0 and engineering knowledge; fourth train a lightweight adapter on weak/proxy labels; fifth compute property intervals using mixture rules; sixth benchmark against homogeneous and VLM-prompting baselines. Risks: weak priors may encode dataset bias, true internal construction is unobservable, mixture rules may be physically simplistic, and property labels may be proxy intervals rather than exact measurements. Failure criteria: no improvement on composite-object density_log_mae or youngs_modulus_log_mae over homogeneous material lookup; prediction_interval_coverage remains poorly calibrated; latent-mixture predictions reduce material interpretability; or gains vanish when evaluated on held-out indoor datasets.

Evidence paper IDs:
openalex:W4402427278; openalex:W4385327621; openalex:W4392222076; openalex:W4399597788; openalex:W4402155831; openalex:W4411238954; openalex:W2798280964; openalex:W3046559354; openalex:W3200689778; openalex:W4312347618

### Candidate B

Idea 1
Title:
Mask-Conditioned Material Mixture to Property Intervals

Core proposal:
For each detected object mask, estimate a calibrated distribution over visible surface-material classes using frozen masked-crop material classifiers aligned to OpenSurfaces/MINC-style taxonomies. Combine the top-k material probabilities with the detected object category to retrieve candidate physical-property intervals from ObjectFolder/ObjectFolder2.0-derived object/material property records and normalized in-dataset property proxies. The mechanism outputs interval-valued properties; intervals are widened when material entropy is high, when category-material compatibility is weak, or when the mask covers too little visible surface.

Motivation or baseline weakness:
Open-vocabulary detectors and promptable segmenters such as GroundingDINO plus SAM can localize visible objects, but direct category-to-property lookup ignores material mixtures and the fact that single RGB exposes mainly surface appearance. This can make density, elastic modulus, hardness, friction, and Poisson-ratio estimates overconfident, especially for coated, upholstered, laminated, transparent, or low-resolution objects.

Mechanism or approach:
A lightweight material-mixture-to-property calibrator consisting of temperature scaling or isotonic calibration over frozen material logits, a category-material compatibility matrix estimated from training data, and a deterministic interval aggregator that unions or probability-weights ObjectFolder/ObjectFolder2.0 property ranges.
Minimize calibrated material cross-entropy plus an interval scoring objective for physical properties. The interval term rewards containing proxy property labels from ObjectFolder/ObjectFolder2.0 mappings while penalizing unnecessarily wide intervals, with a separate calibration penalty for nominal interval coverage.

Experiment and implementation plan:
GroundingDINO; SAM; CLIP; OpenSurfaces; MINC; ObjectFolder; ObjectFolder2.0
Indoor RGB images with object boxes or masks and object categories; Masked object crops produced by GroundingDINO plus SAM or available ground-truth masks; Visible-surface material labels or proxy labels mapped to an OpenSurfaces/MINC-style taxonomy; Object-category to candidate-material mappings estimated from training annotations; Physical-property proxy intervals derived only from ObjectFolder and ObjectFolder2.0 records after unit normalization
run_detection_segmentation.py for GroundingDINO plus SAM masks; extract_masked_material_logits.py for masked crops and visible-region material logits; build_objectfolder_property_table.py for taxonomy alignment and unit normalization; train_material_calibrator.py for temperature scaling or isotonic calibration; aggregate_property_intervals.py for category-conditioned interval construction; evaluate_object_property_json.py for object-level JSON outputs and supported metrics
object_recall; mask_iou; material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error
Replace material mixture with single top-1 material; Remove object-category conditioning from property aggregation; Use uncalibrated material logits instead of calibrated material probabilities; Use boxes instead of masks for material evidence; Return median point estimates instead of intervals; Disable entropy-based interval widening
Randomly permute material labels before property aggregation; Use object category only with no masked visual crop; Use full-image material predictions instead of object masks; Evaluate on empty or synthetic blank masks to test context leakage; Shuffle ObjectFolder/ObjectFolder2.0 property records across material classes
Improve material_macro_f1 by at least 5 percentage points over the frozen masked-crop material baseline; Reduce density_log_mae and youngs_modulus_log_mae by at least 10% relative to category-only ObjectFolder/ObjectFolder2.0 lookup; Achieve prediction_interval_coverage within 5 percentage points of nominal 90% coverage; Keep mask_iou within 2 percentage points of the GroundingDINO plus SAM mask pipeline when using predicted masks; Reduce calibration_error relative to uncalibrated material-probability aggregation

Evidence paper IDs:
openalex:W4402500749; openalex:W4411238954; openalex:W2798280964; openalex:W2895238724; openalex:W4391722892; openalex:W4312347618

Risks, controls, or fallback:
Risk: visible surface material may not reveal internal composition, and ObjectFolder/ObjectFolder2.0 proxy intervals may not cover all indoor categories. Fallback: emit broader category-conditioned intervals, mark hidden-core/coated/reflective/transparent/low-resolution objects with failure_warning tags, and report results separately for categories with and without reliable property proxies.

---

Idea 2
Title:
Evidence-Gated VLM Property Reasoning

Core proposal:
Insert an evidence gate between segmentation/material recognition and VLM reasoning. For each object, build a structured object card containing the mask crop, category, top-k material hypotheses, visible surface cues, mask-quality fields, and ObjectFolder2.0-derived candidate property ranges. The VLM is constrained to choose, widen, or abstain from these ranges and must cite specific object-card fields. A verifier rejects unsupported citations, out-of-card materials, and ranges not traceable to candidate entries, then widens intervals or emits a failure warning.

Motivation or baseline weakness:
VLMs such as LLaVA, Qwen-VL, and BLIP-2 can describe objects and context, but physical-property predictions may be driven by language priors rather than localized visual evidence. This makes numeric or interval estimates prompt-sensitive, weakly calibrated, and difficult to audit.

Mechanism or approach:
A rule-based verifier plus lightweight calibration layer. The verifier checks JSON schema validity, citation presence, material/category consistency, and whether each predicted property interval is supported by a listed candidate range. The calibration layer learns when to widen accepted intervals using validation-set coverage errors from frozen VLM outputs.
Train only the verifier thresholds and interval calibrator while keeping detectors, material models, and VLMs frozen. Optimize valid structured-output rate, calibrated interval coverage, and property interval score, with penalties for unsupported citations, out-of-range numeric values, and failure to abstain when object-card evidence is insufficient.

Experiment and implementation plan:
GroundingDINO; SAM2; LLaVA; Qwen-VL; BLIP-2; CLIP; ObjectFolder2.0
Indoor RGB scene images with visible objects and object categories; Object masks or boxes generated by GroundingDINO plus SAM2 or provided by annotations; Masked object crops and optional local context crops; Material top-k predictions from frozen masked-crop classifiers; ObjectFolder2.0-derived candidate property intervals aligned to object category and material taxonomy; A small validation set with human-checked object cards, evidence citations, and acceptable interval decisions
generate_object_cards.py for masks, categories, material logits, mask quality, and local context cues; prompt_vlm_property_json.py for constrained VLM generation from object cards; verify_evidence_support.py for citation, schema, and range checks; calibrate_vlm_intervals.py for validation-set interval widening; score_structured_outputs.py for JSON validity, supported property metrics, and calibration
material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error
Free-form VLM prediction without object cards; Object cards without material top-k hypotheses; Object cards without ObjectFolder2.0 candidate property ranges; Verifier disabled; Verifier enabled but interval widening disabled; Mask crop removed while category and context are retained; Scene context removed from object cards
Ask the VLM to predict properties from category names only; Shuffle object cards across masks before VLM prompting; Remove the mask crop while keeping scene context to test context-only leakage; Inject false material candidates and measure verifier rejection rate; Replace candidate property ranges with randomly permuted ranges across categories
Reduce unsupported-evidence rate by at least 50% compared with unconstrained VLM prompting; Reach at least 85% prediction_interval_coverage for nominal 90% intervals; Reduce density_log_mae and youngs_modulus_log_mae by at least 10% relative to VLM-only prompting on accepted non-warning outputs; Keep valid structured JSON output rate above 98%; Reduce calibration_error relative to unverified object-card prompting

Evidence paper IDs:
openalex:W4399597788; openalex:W4402155831; openalex:W4385327621; openalex:W4402500749; openalex:W7148178853; openalex:W4312347618

Risks, controls, or fallback:
Risk: the VLM may still infer unsupported properties from memorized priors or ignore range constraints despite structured prompting. Fallback: replace numeric VLM generation with deterministic ObjectFolder2.0 range aggregation, and use the VLM only to produce qualitative visible-cue summaries and failure_warning explanations that are checked by the verifier.

---

Idea 3
Title:
Selective Uncertainty Head for Hidden-Material Failure Cases

Core proposal:
Add a selective uncertainty head that predicts object-level observability and hidden-material risk from frozen pipeline features: mask quality, crop resolution, visible area, material entropy, disagreement among CLIP/OpenSurfaces/MINC-style material predictions, optional VLM ambiguity descriptions, object category, and texture/specularity cues. For each object-property pair, the head chooses narrow interval, widened interval, or abstention-style failure warning without changing the underlying detector, segmenter, or material classifier.

Motivation or baseline weakness:
Detection, material recognition, and table-lookup pipelines can produce reasonable average property estimates, but they often do not know when to abstain on objects whose physical properties are underdetermined from single RGB, such as coated wood, fabric-covered foam, glossy plastic, painted metal, glass, or laminated surfaces.

Mechanism or approach:
A small gradient-boosted tree, logistic regression model, or two-layer MLP trained on frozen pipeline features to estimate the probability that each property estimate will exceed a predefined error threshold or miss its nominal interval.
Optimize selective calibration using validation labels derived from held-out proxy property intervals. The head minimizes accepted-set property error and calibration_error while maintaining a target accepted-object coverage, with binary supervision indicating whether the base interval missed the proxy label or exceeded a per-property log-error threshold.

Experiment and implementation plan:
Mask2Former; SAM; CLIP; OpenSurfaces; MINC; LLaVA; ObjectFolder
Indoor object crops and masks from RGB scene images; Proxy physical-property labels or intervals derived from ObjectFolder-linked material/category mappings; Frozen material logits from CLIP/OpenSurfaces/MINC-style models; Optional VLM material and ambiguity descriptions from LLaVA or BLIP-2 used only as frozen features; Mask quality features from SAM or Mask2Former outputs; Held-out validation categories containing coated, upholstered, reflective, transparent, or visually ambiguous objects
extract_pipeline_features.py for entropy, disagreement, mask area, boundary quality, texture cues, and category priors; make_proxy_error_labels.py for per-property high-error and interval-miss labels; train_selective_uncertainty_head.py for lightweight risk modeling; apply_abstention_policy.py for interval widening and failure_warning generation; evaluate_calibrated_acceptance.py for accepted-coverage, property error, interval coverage, and calibration
density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; material_macro_f1
Use material entropy only; Use model disagreement only; Remove mask-quality features; Remove object-category prior; Use one global uncertainty score instead of per-property uncertainty; Always output broad intervals with no learned selector; Use VLM ambiguity text only, without visual/material features
Train the uncertainty head on randomly shuffled error labels; Use only object mask area as the risk predictor; Evaluate calibration after permuting material logits across objects; Force acceptance of all predictions to recover the non-selective baseline; Randomly assign failure warnings at the same abstention rate as the learned head
At 70% accepted-object coverage, reduce accepted-set density_log_mae and youngs_modulus_log_mae by at least 20% relative to non-selective property lookup; Improve calibration_error by at least 25% relative to uncalibrated interval outputs; Flag at least 60% of high-error hidden-material cases while keeping false warning rate below 30%; Do not degrade accepted-set material_macro_f1 relative to the frozen material baseline; Maintain prediction_interval_coverage within 5 percentage points of the target nominal coverage after interval widening

Evidence paper IDs:
openalex:W4416850904; openalex:W4403323960; openalex:W4385327621; openalex:W2798280964; openalex:W3046559354; openalex:W4391722892

Risks, controls, or fallback:
Risk: proxy error labels may encode ObjectFolder/material-table bias rather than true physical uncertainty, and hidden-material cases may be rare in validation data. Fallback: report sensitivity across multiple proxy-label construction rules, evaluate the head primarily as an abstention and calibration module, and default to conservative interval widening when feature-based risk estimates are unstable.

---

## Item 15: HUM-0e6790e6e4

类型：`portfolio`

### Candidate A

Idea 1
Title:
Evidence-Gated Material-to-Property Retrieval for Masked Indoor Objects

Core proposal:
For each object, first obtain a box or mask with GroundingDINO/SAM-style segmentation, then compute material evidence only inside the mask using masked image crops and material-recognition prompts or classifiers. A calibrated evidence gate combines masked material scores, object category, mask area, texture/edge statistics, and agreement between multiple material prompts. Materials below the gate are not treated as observed facts; instead they contribute to a broader material-family distribution. Physical-property intervals are retrieved from ObjectFolder/ObjectFolder2.0-style physical-property sources and material-property tables only through the gated material distribution. If no material has sufficient localized evidence, the output interval is widened and tagged as visually underdetermined rather than returning an overconfident point estimate.

Motivation or baseline weakness:
Open-vocabulary VLM or CLIP-style material predictions can be driven by object semantics rather than localized surface evidence. This is risky for indoor categories such as chairs, cabinets, cushions, doors, and tabletops where the same category can be wood, metal, plastic, glass, fabric, or composites, and where single RGB images may not reveal hidden material composition.

Mechanism or approach:
A lightweight evidence-gating calibrator that takes masked material logits, category prior logits, prompt-agreement scores, mask quality features, and optional source-table disagreement features, and returns a calibrated distribution over material labels plus per-property interval weights.
Train the gate with material cross-entropy or soft-label KL divergence and interval negative log likelihood for density, Young's modulus, Poisson's ratio, hardness, and friction coefficient. Add a calibration penalty that increases loss when high-confidence material predictions disagree with masked visual evidence, and optimize interval coverage/width tradeoff on a held-out calibration split.

Experiment and implementation plan:
GroundingDINO + SAM + CLIP material prompt + material-property table lookup; GroundingDINO + SAM + OpenSurfaces/MINC-style material classifier + material-property table lookup; LLaVA or Qwen-VL direct JSON material and property prediction without localized evidence gating
Indoor RGB images with object boxes or masks, either annotated or produced by GroundingDINO/SAM-style models; Object-level material labels, weak material labels, or manually audited proxy labels compatible with OpenSurfaces/MINC-style material categories; Physical-property ranges aligned to material families using ObjectFolder/ObjectFolder2.0-style sources and curated material-property tables; Held-out manually audited indoor objects with visible-material labels, property intervals, and flags for hidden, composite, or visually ambiguous materials
run_detection_segmentation.py; extract_masked_material_scores.py; build_material_property_table.py; train_evidence_gate.py; predict_object_property_json.py; evaluate_material_and_property_intervals.py
object_recall; mask_iou; material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Remove masked visual evidence and use object-category prior only; Remove object-category prior and use masked material scores only; Replace the calibrated evidence gate with uncalibrated top-1 masked material prediction; Use point estimates instead of property intervals; Disable low-evidence widening and failure warnings
Randomly permute material-property table rows while preserving material frequencies; Use a same-size background crop instead of the object mask for material scoring; Evaluate on blank or texture-erased object crops with category labels retained; Force all objects of the same category to share one material prediction; Replace the true object mask with a shifted mask that has low IoU with the object
Improve material_macro_f1 by at least 5 percentage points over the masked CLIP prompt baseline on audited objects; Reduce density_log_mae and youngs_modulus_log_mae by at least 10 percent versus top-1 material table lookup; Achieve prediction_interval_coverage within 5 percentage points of the target coverage level on audited intervals; Lower selective_risk by at least 15 percent when abstaining or widening intervals on the lowest-confidence 20 percent of objects

Evidence paper IDs:
openalex:W4402427278; openalex:W4402500749; openalex:W3047386722; openalex:W2798280964; openalex:W3200689778; openalex:W4312347618

Risks, controls, or fallback:
Risk: single RGB views may not reveal internal structure, coatings, laminates, or composite construction, so localized visual evidence can still support the wrong physical material. Fallback: report conservative material-family mixtures and wider property intervals, expose material-evidence disagreement in the JSON evidence field, and set failure_warning to hidden_material_or_composite_uncertain when the gate rejects all specific materials.

---

Idea 2
Title:
Property-Interval Conformal Calibration for Single-Image Physical Estimates

Core proposal:
Wrap any frozen detection, segmentation, material-recognition, and property-estimation pipeline with split conformal calibration. The calibrator receives baseline point estimates or raw intervals and computes nonconformity scores on a calibration split with proxy or audited property intervals. Scores are conditioned by material family, object category, material confidence, visible texture strength, mask quality, and disagreement between property sources. At inference, the module outputs calibrated per-property intervals and an uncertainty tag, using broader fallback groups when a fine material/category group has insufficient calibration examples.

Motivation or baseline weakness:
Direct material-to-property lookup and VLM-generated numeric estimates can produce precise-looking point values even when the visible image supports only a material family or proxy label. This makes density, modulus, hardness, friction, and related estimates poorly calibrated, especially for hidden materials, rare materials, and object categories with large within-class variation.

Mechanism or approach:
A post-hoc grouped conformal interval calibrator that does not retrain the vision backbone and can wrap GroundingDINO/SAM2/Mask2Former-style masks, CLIP/MINC-style material recognizers, or VLM JSON predictors.
For each physical property, minimize interval width subject to empirical target coverage on a held-out calibration split. Use grouped conformal quantiles when group sample counts are sufficient, back off to material-family or global quantiles when sparse, and report unsupported-group warnings rather than extrapolating narrow intervals.

Experiment and implementation plan:
GroundingDINO + SAM2 + CLIP-style material prediction + material-property table point estimate; Mask2Former + MINC-style material classifier + uncalibrated material-property interval estimate; Qwen-VL direct property JSON prediction without residual-based conformal calibration
Calibration split with object masks or boxes, material labels or proxy material intervals, and audited examples where available; Physical-property ranges from ObjectFolder/ObjectFolder2.0-style physical-property sources and curated material-property tables; Indoor evaluation images with object-level detections or masks and material/category metadata sufficient for grouped calibration; A held-out test split separated by scene and object instance to avoid calibrating and testing on near-duplicate objects
collect_baseline_property_predictions.py; construct_proxy_interval_labels.py; fit_grouped_conformal_calibrator.py; apply_property_interval_calibration.py; evaluate_coverage_width_selective_risk.py
prediction_interval_coverage; calibration_error; selective_risk; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; material_top3_accuracy
Global conformal calibration without material or category grouping; Group only by material family; Group only by object category; Use VLM self-reported confidence instead of calibration residuals; Use uncalibrated source-table intervals; Disable sparse-group backoff and force fine-grained group quantiles
Calibrate on shuffled property labels while preserving material/category frequencies; Calibrate on one set of material families and test on held-out unrelated material families without fallback grouping; Use a constant-width interval for every property and object; Remove source-table disagreement features from the grouping and nonconformity model; Tune conformal quantiles on the test split to detect leakage-sensitive gains
Reach at least 90 percent empirical coverage for nominal 90 percent intervals on density and Young's modulus; Reduce calibration_error by at least 25 percent versus uncalibrated baseline intervals; Maintain median interval width no more than 1.5 times the strongest uncalibrated table-interval baseline at matched coverage; Improve selective_risk by at least 10 percent at 80 percent retained-object coverage; Maintain coverage within 7 percentage points of nominal for the largest material-family groups

Evidence paper IDs:
openalex:W4416850904; openalex:W4403323960; openalex:W4385327621; openalex:W4391722892; openalex:W4327630646; openalex:W4312347618

Risks, controls, or fallback:
Risk: proxy labels and material-property tables may be noisy, and conformal guarantees can degrade under distribution shift or sparse rare-material groups such as composites, coated metal, laminated wood, and foam. Fallback: back off from fine groups to broader material-family or global calibration, widen intervals using source-table disagreement, and set failure_warning when an object falls outside calibrated material/category support.

---

Idea 3
Title:
Mask-Consistency Self-Check for Object-Level Property JSON Reliability

Core proposal:
Before property prediction, generate multiple plausible spatial supports for each detected object: the original mask, alternative promptable masks, box crops, eroded/dilated masks, boundary-trimmed masks, and visible part crops. Run the same material and property estimator on each support. A mask-consistency scorer measures agreement of material distributions, property intervals, mask IoU, mask area change, and part-to-whole consistency. Objects with stable predictions pass through with normal calibrated intervals; unstable objects receive wider intervals and failure_warning set to mixed_material_or_mask_uncertain. The self-check is applied before JSON aggregation so downstream consumers know whether the object-level estimate is mask-sensitive.

Motivation or baseline weakness:
Promptable or open-vocabulary segmentation with GroundingDINO, SAM, SAM2, or Mask2Former can return masks that include background, merge neighboring objects, omit parts, or isolate a salient subpart rather than the full object. Material and physical-property estimates derived from one mask can therefore be unstable while the final JSON still appears complete and object-level.

Mechanism or approach:
A mask-consistency scorer that aggregates material logits, property intervals, mask IoU/area features, and perturbation metadata across candidate masks and crops, then outputs a reliability score and interval-widening factor.
Learn or tune a reliability score that predicts downstream material/property error from perturbation instability. Penalize high material entropy, large property-interval variance, low agreement between whole-object and part-crop predictions, and low IoU among high-confidence masks, while avoiding penalties for benign boundary perturbations that do not change predictions.

Experiment and implementation plan:
GroundingDINO + SAM single-mask property pipeline; GroundingDINO + SAM2 single-mask property pipeline; Mask2Former single-mask property pipeline
Indoor RGB images with object boxes or masks produced by GroundingDINO, SAM, SAM2, or Mask2Former-style systems; Material labels, proxy labels, or manually audited material annotations for evaluating whether mask instability corresponds to material errors; Property ranges from ObjectFolder/ObjectFolder2.0-style sources and curated material-property tables; A manually audited subset labeling mask failure types such as background inclusion, merged objects, missing parts, and mixed visible materials
generate_candidate_masks.py; perturb_masks_and_boxes.py; predict_materials_per_mask_variant.py; compute_mask_consistency_score.py; aggregate_property_json_with_warnings.py; evaluate_stability_and_downstream_error.py
object_recall; mask_iou; material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Use only the highest-confidence mask; Use box crop instead of mask crop; Remove erosion and dilation perturbations; Remove part-crop consistency check; Use consistency score only for warning without widening intervals; Aggregate all mask variants by simple averaging without reliability scoring
Apply the perturbation pipeline to background regions rather than object masks; Randomly choose one candidate mask without consistency scoring; Force all candidate masks to share the same material label before aggregation; Evaluate on intentionally merged neighboring-object masks; Use duplicate copies of the same mask as variants to confirm that apparent gains require real perturbation diversity
Reduce material prediction variance across mask variants by at least 20 percent versus the single-mask baseline on objects with ambiguous boundaries; Improve density_log_mae and friction_coefficient_mae by at least 8 percent on audited objects with multiple visible materials or cluttered boundaries; Achieve lower selective_risk than confidence-only filtering at the same retained-object rate; Increase failure_warning precision for mask-related errors by at least 15 percentage points on manually audited cases; Maintain material_macro_f1 within 2 percentage points of the single-mask baseline on audited uniform-material objects

Evidence paper IDs:
openalex:W4402500749; openalex:W7148178853; openalex:W4416850904; openalex:W4411238954; openalex:W4385327621; openalex:W2798280964

Risks, controls, or fallback:
Risk: generating and evaluating multiple mask variants increases compute and may over-flag uniform objects with weak texture or reflective surfaces. Fallback: run the self-check only for low-confidence masks, small objects, reflective objects, masks with unusual area changes, and categories with common multi-material construction; otherwise pass through the single-mask baseline with normal calibrated intervals.

### Candidate B

Idea 1
Title:
Uncertainty-Aware Material-to-Property Retrieval for Every Segmented Indoor Object

Core proposal:
Build a plug-and-play workflow that combines open-vocabulary object detection/segmentation with material recognition and a calibrated material-property retrieval layer. The system takes one RGB indoor image, detects visible objects with GroundingDINO plus SAM or SAM2, classifies each object crop and masked surface regions into a distribution over candidate materials using CLIP/OpenSurfaces/MINC-style material prompts, and maps the resulting material distribution to interval-valued physical properties from ObjectFolder/ObjectFolder2.0 and engineering material tables. The output is object-level JSON containing object_id, category, mask_or_box, predicted_materials, density, Young's modulus, Poisson's ratio, hardness, friction coefficient, confidence intervals, visual evidence, and failure warnings for ambiguous or hidden-material cases.

Motivation or baseline weakness:
A single RGB image usually cannot identify hidden structure or exact composition, but many indoor objects expose enough category, texture, reflectance, and context cues to support useful interval predictions. Existing baselines cover detection, segmentation, material recognition, and physical-property sources separately, but not a calibrated object-level physical-property workflow. The key novelty is not a new large model, but a lightweight probabilistic bridge from visible material evidence to physically meaningful property intervals with explicit warnings when the inference is underdetermined.

Mechanism or approach:
Direct baselines: GroundingDINO, SAM, SAM2, Mask2Former for object localization; CLIP, OpenSurfaces, and MINC for material recognition; ObjectFolder, ObjectFolder2.0, and engineering material tables for property values. Transfer baselines: BLIP-2, LLaVA, and Qwen-VL as object/category/context validators and prompt-based material priors. Borrowed components: promptable segmentation, masked crop classification, material taxonomies, and tabulated physical-property ranges. New component: a Material-Property Evidence Graph that stores material aliases, object-category priors, property intervals, source reliability, and compatibility constraints, plus a conformal calibration wrapper that turns material uncertainty into property prediction intervals. Minimal new module: a frozen-model inference wrapper plus a small calibrator/retriever trained or tuned on proxy labels. Ablations: remove object-category priors, remove scene-context priors, use boxes instead of masks, use CLIP-only vs OpenSurfaces/MINC features, point estimates vs intervals, and calibrated vs uncalibrated uncertainty. Risks: material labels may be visually ambiguous, property tables may disagree, composite objects may mix materials, masks may include background, and VLM priors may hallucinate. Failure criteria: no improvement over a CLIP-to-table baseline in density_log_mae or material_macro_f1; prediction_interval_coverage below target coverage by more than 10 percentage points; selective risk does not improve when abstaining on high-uncertainty objects; failure warnings do not correlate with high error.

Experiment and implementation plan:
Datasets: use ScanNet, Matterport3D, and OpenRooms images for indoor object crops and context; use OpenSurfaces/MINC-style material labels for material evaluation where available; use ObjectFolder/ObjectFolder2.0 and engineering material tables to build proxy or interval property labels. Metrics: object_recall and mask_iou for segmentation; material_accuracy, material_macro_f1, and material_top3_accuracy for material prediction; density_log_mae, youngs_modulus_log_mae, poisson_ratio_mae, hardness_mae_or_ordinal_error, and friction_coefficient_mae for property estimates; prediction_interval_coverage, calibration_error, and selective_risk for uncertainty. MVP artifacts: inference script that ingests one RGB image and emits structured JSON; material-property evidence graph; evaluation harness; calibration report; qualitative failure gallery. Implementation plan: first integrate GroundingDINO plus SAM2 and a Mask2Former baseline; second implement masked crop material scoring with CLIP/OpenSurfaces/MINC prompts; third normalize material names and property tables into intervals; fourth fit a lightweight conformal or isotonic calibrator on held-out proxy labels; fifth run ablations and compare against direct CLIP-to-nearest-material and VLM-only baselines.

Evidence paper IDs:
openalex:W4402427278; openalex:W4402500749; openalex:W4411238954; openalex:W3022851742; openalex:W4391809438; openalex:W4367665525; openalex:W7148178853; openalex:W4416850904; openalex:W4403323960; openalex:W4385327621; openalex:W4391722892; openalex:W4327630646; openalex:W3200689778; openalex:W4312347618

---

Idea 2
Title:
Object-Part Material Mixture Estimation for Composite Indoor Objects

Core proposal:
Develop an object-level physical-property predictor that explicitly models visible objects as mixtures of part-level materials rather than assigning one material per object. The workflow detects objects, segments them, oversegments each object mask into visually coherent material regions, predicts a material distribution for each region, and aggregates region-level property distributions into object-level effective properties with uncertainty. The final JSON reports both predicted_materials and property intervals, with evidence linking each property estimate to visible regions such as metal legs, wooden tabletop, fabric cushion, plastic shell, or glass panel.

Motivation or baseline weakness:
Many indoor objects are composites: a chair may contain fabric, foam, metal, and plastic; a cabinet may combine wood veneer, metal handles, and glass; appliances may expose plastic and metal while hiding internal components. A single-material baseline can be systematically wrong for density, stiffness, hardness, and friction. A mixture-aware method is an incremental but publishable improvement because it targets a concrete failure mode of object-level material recognition while staying compatible with frozen detectors and segmenters.

Mechanism or approach:
Direct baselines: GroundingDINO plus SAM/SAM2 for object masks, Mask2Former for semantic/instance alternatives, CLIP/OpenSurfaces/MINC for region material labels, and ObjectFolder/ObjectFolder2.0 plus engineering tables for property lookup. Transfer baselines: LLaVA or Qwen-VL to propose object parts and likely material compositions from the masked crop and category, used only as a prior. Borrowed components: SAM-style promptable masks, texture/material classification, scene context, and tabulated physical properties. New component: a Part-Material Mixture Aggregator that splits an object mask into superpixels or SAM-generated submasks, assigns region material posteriors, estimates visible area fractions, and computes conservative effective-property ranges using mixture rules and category-specific part priors. Minimal new module: a lightweight region proposal and mixture aggregation layer; all large models remain frozen. Ablations: single object crop vs part regions, visible-area-weighted vs category-prior-weighted mixture, VLM part prior vs no VLM prior, SAM2 submasks vs classical superpixels, and strict interval aggregation vs point-estimate aggregation. Risks: visible area fraction may not match mass fraction, internal structures are hidden, region segmentation may fragment highlights/shadows, and mixture rules for Young's modulus or friction may be physically approximate. Failure criteria: mixture modeling fails to improve material_top3_accuracy or property errors on composite-object subsets; effective-property intervals become so wide that selective_risk is not useful; part evidence cannot be localized; or the method degrades simple single-material objects compared with the baseline.

Experiment and implementation plan:
Datasets: construct composite-object subsets from ScanNet, Matterport3D, and OpenRooms using categories such as chairs, tables, cabinets, sofas, appliances, windows, and doors; annotate a small validation set with visible part-material labels; use OpenSurfaces/MINC labels for region-level material checks; use ObjectFolder/ObjectFolder2.0 and engineering tables for proxy intervals. Metrics: object_recall and mask_iou; material_macro_f1 at region and object levels; material_top3_accuracy for visible materials; density_log_mae, youngs_modulus_log_mae, poisson_ratio_mae, hardness_mae_or_ordinal_error, and friction_coefficient_mae against proxy labels; prediction_interval_coverage and selective_risk on composite categories. MVP artifacts: part-region visualizer, per-object material-mixture JSON schema, benchmark split for composite vs single-material objects, and scripts comparing single-material and mixture-aware predictions. Implementation plan: first run object detection and masks; second generate sub-object regions using SAM2 prompts or mask-constrained superpixels; third score material distributions per region; fourth aggregate properties using material tables and conservative mixture rules; fifth evaluate on composite-object subsets and report failure warnings for hidden structure and low evidence coverage.

Evidence paper IDs:
openalex:W4402500749; openalex:W7148178853; openalex:W4416850904; openalex:W4403323960; openalex:W4411238954; openalex:W4385327621; openalex:W2895238724; openalex:W2798280964; openalex:W3012463097; openalex:W4399597788; openalex:W4402155831; openalex:W4312347618; openalex:W3200689778

---

Idea 3
Title:
Self-Auditing Vision-Language Property Predictor with Evidence-Grounded Failure Warnings

Core proposal:
Create an engineering-integration and uncertainty-calibration workflow where a vision-language model proposes object category, material hypotheses, and physical-property ranges, but every claim must be checked against detector masks, localized material evidence, and a structured property database before it enters the output JSON. The system emits not only property estimates but also evidence strings, confidence scores, and failure_warning fields that distinguish low visual evidence, out-of-database material, composite ambiguity, occlusion, specular confusion, and hidden-structure uncertainty.

Motivation or baseline weakness:
Vision-language models are attractive for plug-and-play deployment because they can use object category and scene context, but they are prompt-sensitive and may hallucinate unsupported material or property claims. A self-auditing layer can convert a brittle VLM-only baseline into an experiment-ready physical-property estimator that is safer, more calibrated, and easier to debug. The novelty is a constrained verification loop that accepts VLM priors only when they agree with localized visual evidence and table-backed physical-property intervals.

Mechanism or approach:
Direct baselines: BLIP-2, LLaVA, and Qwen-VL as VLM-only predictors; GroundingDINO/SAM2 and Mask2Former as localization baselines; CLIP/OpenSurfaces/MINC as visual material verifiers; ObjectFolder/ObjectFolder2.0 and engineering material tables as property sources. Transfer baselines: SceneGPT-style scene reasoning ideas for contextual prompting, adapted only as text-level scene priors without requiring 3D training. Borrowed components: open-vocabulary grounding, promptable segmentation, VLM chain-of-thought-style decomposition without exposing hidden reasoning, and property-table retrieval. New component: an Evidence Consistency Auditor that scores whether each object-level property estimate is supported by the object mask, material classifier, object category, scene context, and property table, then calibrates confidence or abstains. Minimal new module: a rule-plus-learned logistic verifier or small adapter trained on proxy accept/reject labels; large VLMs and vision encoders remain frozen. Ablations: VLM-only property prediction, VLM plus table lookup without audit, audit without localized material verifier, audit without category-context prior, different uncertainty calibrators, and different abstention thresholds. Risks: auditor rules may be too conservative, VLM prompts may vary, material verifiers may inherit dataset bias, property tables may not cover consumer products, and evidence strings may appear reliable even when the underlying mask is wrong. Failure criteria: audited predictions do not reduce calibration_error or selective_risk relative to VLM-only; abstention rate is too high for practical use; accepted predictions have no lower property error than rejected predictions; or evidence/failure warnings fail human inspection on a sampled error set.

Experiment and implementation plan:
Datasets: evaluate on ScanNet, Matterport3D, and OpenRooms indoor images with object masks or generated masks; use material labels from OpenSurfaces/MINC-style sources where possible; create a small audit benchmark with human labels for whether material/property claims are visually supported; use ObjectFolder/ObjectFolder2.0 and engineering tables for interval labels. Metrics: material_accuracy, material_macro_f1, material_top3_accuracy; density_log_mae, youngs_modulus_log_mae, poisson_ratio_mae, hardness_mae_or_ordinal_error, and friction_coefficient_mae; prediction_interval_coverage, calibration_error, selective_risk, abstention rate, and warning precision for known failure modes. MVP artifacts: prompt templates for VLM proposals, detector/segmenter integration, evidence-auditor module, calibrated JSON emitter, audit benchmark, and dashboard of accepted vs rejected predictions. Implementation plan: first implement a VLM-only JSON predictor; second add GroundingDINO/SAM2 object masks and object crops; third score material hypotheses using CLIP/OpenSurfaces/MINC verifiers; fourth retrieve table-backed property intervals; fifth train or tune the auditor on proxy accept/reject examples; sixth evaluate whether auditing improves calibration and selective-risk curves over VLM-only and table-only baselines.

Evidence paper IDs:
openalex:W4392222076; openalex:W4399597788; openalex:W4402155831; openalex:W4414857074; openalex:W4402427278; openalex:W4402500749; openalex:W7148178853; openalex:W4411238954; openalex:W4385327621; openalex:W2798280964; openalex:W3012463097; openalex:W4391722892; openalex:W4327630646

---

## Item 16: HUM-62ced0931c

类型：`single_idea`

### Candidate A

Title:
Material-Conditioned Interval Property Lookup for Segmented Indoor Objects

Core proposal:
Add a lightweight material-to-property interval mapper that converts top-k localized material predictions and object category priors into interval-valued physical properties, rather than single overconfident point estimates. For each object mask, the module fuses visual material probabilities with category-conditioned engineering table priors and emits median, lower/upper interval, confidence, evidence strings, and failure warnings when the material posterior is diffuse.

Motivation or baseline weakness:
GroundingDINO plus SAM/SAM2 can localize visible objects, but the pipeline has no calibrated bridge from localized visual material cues to physical properties; CLIP/OpenSurfaces/MINC-style material recognition can be prompt-sensitive or ambiguous, and exact density/modulus/hardness/friction ground truth is often unavailable from single RGB.

Mechanism or approach:
A frozen-backbone material posterior calibrator plus deterministic property-table aggregator: temperature-scaled material logits from cropped masked objects are mapped to property intervals using engineering material tables and ObjectFolder/ObjectFolder2.0 priors, with no large-scale training.
Minimize interval-aware negative log likelihood and log-space absolute error for density and Young's modulus under weak/proxy labels, while enforcing target prediction-interval coverage for all physical-property outputs.

Experiment and implementation plan:
GroundingDINO; SAM; SAM2; CLIP; OpenSurfaces; MINC; ObjectFolder; ObjectFolder2.0; engineering_material_property_tables
Indoor images with object masks or boxes from ScanNet, Matterport3D, or OpenRooms; Material labels or proxy labels from OpenSurfaces/MINC-style categories; Object category labels aligned to detected masks; Engineering material property tables containing density, Young's modulus, Poisson's ratio, hardness, and friction coefficient ranges; ObjectFolder/ObjectFolder2.0 object-material-property metadata where available
run_detection_segmentation.py to produce object_id, category, mask_or_box using GroundingDINO plus SAM/SAM2; extract_masked_object_crops.py to create localized object crops and masked context crops; predict_material_topk.py to obtain calibrated material posteriors from frozen CLIP/OpenSurfaces/MINC models; build_property_table_index.py to normalize material names and property units; aggregate_property_intervals.py to produce structured JSON object-level physical-property predictions; evaluate_interval_properties.py to compute log MAE, MAE, coverage, calibration error, and selective risk
object_recall; mask_iou; material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Remove object-category prior and use material posterior only; Use point estimates from the most likely material instead of interval aggregation; Use uncalibrated CLIP logits instead of temperature-scaled material probabilities; Use mask crop only versus mask crop plus surrounding scene context; Replace engineering table intervals with ObjectFolder/ObjectFolder2.0-only priors
Shuffle material labels across object crops before property lookup; Assign generic category-level property intervals without visual material evidence; Use whole-image material prediction instead of object-mask-localized prediction; Evaluate on categories absent from the property table to verify failure_warning activation
Improve material_top3_accuracy over frozen CLIP-only object crop baseline by at least 5 percentage points; Reduce density_log_mae and youngs_modulus_log_mae by at least 10% relative to most-likely-material table lookup; Achieve prediction_interval_coverage within 5 percentage points of the nominal 90% interval target; Reduce selective_risk at 70% retained predictions relative to uncalibrated material posterior baseline; Failure if interval coverage is below 75% for nominal 90% intervals or if property errors are not lower than generic category priors

Evidence paper IDs:
openalex:W4402427278; openalex:W4402500749; openalex:W4411238954; openalex:W2798280964; openalex:W3012463097; openalex:W2895238724; openalex:W3200689778; openalex:W4312347618

Risks, controls, or fallback:
Risk: visible texture may not identify hidden composition, for example veneer, painted metal, foam-filled furniture, or composite objects. Fallback: widen intervals, mark low-observability failure_warning, and report category-level priors rather than unsupported precise values.

### Candidate B

Title:
Material-Conditioned Interval Property Lookup for Segmented Indoor Objects

Core proposal:
Add a lightweight material-to-property interval mapper that converts top-k localized material predictions and object category priors into interval-valued physical-property predictions rather than overconfident point estimates. For each object mask, the module fuses calibrated visual material probabilities with category-conditioned priors from curated material-property tables and ObjectFolder/ObjectFolder2.0 metadata where available. It emits median estimates, lower/upper intervals, confidence, source tags, and failure warnings when the material posterior is diffuse, the object category conflicts with the material hypothesis, or the lookup table lacks adequate support.

Motivation or baseline weakness:
GroundingDINO with SAM/SAM2 can localize visible objects, but the pipeline has no calibrated bridge from object-localized material cues to physical-property ranges. CLIP/OpenSurfaces/MINC-style material recognition can be prompt-sensitive or ambiguous, and single RGB images often cannot support exact density, modulus, hardness, or friction estimates for hidden or composite materials.

Mechanism or approach:
A frozen-backbone material posterior calibrator plus deterministic property-table aggregator: temperature-scaled material logits from masked object crops are mapped to normalized material names and then to property intervals using curated material-property tables and ObjectFolder/ObjectFolder2.0 priors, with no large-scale end-to-end training.
Minimize interval-aware negative log likelihood and log-space absolute error for density and Young's modulus under weak or proxy labels, while enforcing target prediction-interval coverage for all physical-property outputs through calibration on a held-out validation split.

Experiment and implementation plan:
GroundingDINO; SAM; SAM2; CLIP; OpenSurfaces; MINC; ObjectFolder; ObjectFolder2.0
Indoor images with object masks or boxes from an indoor-scene source such as ScanNet, Matterport3D, or OpenRooms; Material labels or proxy labels aligned to object crops using OpenSurfaces/MINC-style material categories; Object category labels aligned to detected masks; Curated material-property tables containing density, Young's modulus, Poisson's ratio, hardness, and friction coefficient ranges with normalized units; ObjectFolder/ObjectFolder2.0 object-material-property metadata where available; Held-out validation split for material-logit temperature scaling and interval calibration
run_detection_segmentation.py to produce object_id, category, mask_or_box using GroundingDINO plus SAM/SAM2; extract_masked_object_crops.py to create masked object crops and optional local context crops; predict_material_topk.py to obtain calibrated material posteriors from frozen CLIP/OpenSurfaces/MINC-style material models; build_property_table_index.py to normalize material names, aliases, property units, and source tags; aggregate_property_intervals.py to combine material posteriors, object-category priors, and table ranges into structured JSON predictions; evaluate_interval_properties.py to compute material metrics, property errors, interval coverage, calibration error, abstention rate, and selective risk
object_recall; mask_iou; material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Remove object-category prior and use material posterior only; Use point estimates from the most likely material instead of posterior-weighted interval aggregation; Use uncalibrated CLIP/OpenSurfaces/MINC logits instead of temperature-scaled material probabilities; Use mask crop only versus mask crop plus surrounding scene context; Replace curated table intervals with ObjectFolder/ObjectFolder2.0-only priors where metadata exists; Disable low-observability and table-missing failure warnings
Shuffle material labels across object crops before property lookup; Assign generic category-level property intervals without visual material evidence; Use whole-image material prediction instead of object-mask-localized prediction; Evaluate categories or materials absent from the property table to verify failure_warning activation; Randomize material-property table rows while preserving material label frequencies
Improve material_top3_accuracy over a frozen CLIP-only object-crop baseline by at least 5 percentage points after calibration; Reduce density_log_mae and youngs_modulus_log_mae by at least 10% relative to most-likely-material table lookup; Achieve prediction_interval_coverage within 5 percentage points of the nominal 90% interval target; Reduce selective_risk at 70% retained predictions relative to an uncalibrated material-posterior baseline; Failure if nominal 90% interval coverage is below 75% or property errors do not beat generic category priors

Evidence paper IDs:
openalex:W4402427278; openalex:W4402500749; openalex:W4411238954; openalex:W2798280964; openalex:W3012463097; openalex:W2895238724; openalex:W3200689778; openalex:W4312347618

Risks, controls, or fallback:
Risk: visible texture may not identify hidden composition, for example veneer, painted metal, foam-filled furniture, or composite objects. Fallback: widen intervals, mark low-observability or table-missing failure_warning fields, and report category-level priors rather than unsupported precise values.

---

## Item 17: HUM-73132c909d

类型：`portfolio`

### Candidate A

Idea 1
Title:
Context-Calibrated Material Mixture Retrieval for Object Property Intervals

Core proposal:
Add a material-mixture retrieval and interval aggregation module for each segmented object. The module encodes the object crop, object category, local scene context, and optional caption text, retrieves top-k candidate material entries from a material-label index, and maps them to property-table ranges. It predicts normalized mixture weights over candidate material-property entries, then outputs both a point estimate and calibrated per-property intervals by aggregating candidate ranges under the mixture. The context signal is used only as a prior over plausible materials for the object category and room, not as a replacement for visible material evidence.

Motivation or baseline weakness:
A frozen detector/segmenter plus CLIP-style material classifier can assign a single visually plausible surface material, but object physical properties are often compatible with multiple material mixtures and category-conditioned priors. From one RGB image, similar-looking objects can map to different density, modulus, hardness, and friction ranges because the visible surface may not determine the bulk material.

Mechanism or approach:
A small adapter that maps frozen crop, category, context, and caption embeddings to a probability distribution over material candidates and property-table entries, followed by a calibration layer that converts mixture-weighted residuals into calibrated prediction intervals on a held-out split.
Train the adapter with supervised or proxy material/property targets: L = CE(material_label, mixture_weights) + lambda * log_property_error(y, y_hat) + beta * interval_score(I, y) + gamma * coverage_penalty. Property predictions are computed by mixture-weighted lookup over table ranges, with log-space losses for positive scale-valued properties such as density and Young's modulus.

Experiment and implementation plan:
GroundingDINO + SAM/SAM2 + CLIP material top-1 + engineering material property table lookup; Mask2Former + MINC/OpenSurfaces material classifier + median property per predicted material; LLaVA/Qwen-VL prompted to infer object material and properties from the crop and scene
Indoor RGB images with object masks/boxes from ScanNet, Matterport3D, or OpenRooms; Object categories from detector outputs or dataset annotations; Material labels or proxy labels from OpenSurfaces/MINC/ObjectFolder/ObjectFolder2.0 where available; Engineering material property tables containing density, Young's modulus, Poisson's ratio, hardness, and friction coefficient ranges; Held-out calibration and test splits separated by scene and object instance
run_object_detection_segmentation.py; extract_object_crop_context_embeddings.py; build_material_property_index.py; train_material_mixture_adapter.py; calibrate_property_intervals.py; evaluate_object_property_json.py
material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Remove scene context and use object crop only; Use top-1 material instead of top-k mixture; Use category-only property priors without visual material cues; Use uncalibrated mixture variance instead of calibrated intervals; Vary k in top-k retrieval: 1, 3, 5, 10; Remove caption embeddings while retaining crop, category, and room context
Randomly permute material-property table entries while keeping material labels fixed; Use background crop embeddings instead of object crop embeddings; Predict global dataset median properties for every object; Train with correct material labels but evaluate with shuffled object categories to test context overreliance
Improve material_top3_accuracy over CLIP top-1/table baseline by at least 10 percent relative; Reduce density_log_mae and youngs_modulus_log_mae by at least 8 percent relative versus top-1 material lookup; Achieve 90 percent nominal prediction interval coverage within plus or minus 5 percentage points on held-out objects; Selective risk decreases monotonically when low-confidence predictions are abstained; Calibration remains within the target tolerance on at least four of the five reported property types

Risks, controls, or fallback:
Risk: proxy material labels and engineering tables may be too coarse for object-specific physical properties, especially for composite or layered objects. Fallback: report category-conditioned property ranges with explicit hidden-structure warnings, evaluate interval calibration separately from point accuracy, and restrict point-estimate claims to categories where visible material is a reasonable proxy for bulk properties.

---

Idea 2
Title:
Physics-Aware Consistency Checker for VLM Property JSON Outputs

Core proposal:
Add a post-hoc constrained validation and repair module for object-level VLM JSON. The module parses each predicted material-property tuple, standardizes units, checks values against material- and category-conditioned feasible intervals, and either minimally repairs the numeric fields or flags the object as unreliable. It preserves the original detector masks, raw VLM text, raw predictions, and parsed units so that repair does not erase the source error.

Motivation or baseline weakness:
Prompted vision-language models can produce complete structured JSON, but their numeric physical-property estimates may be internally inconsistent, unit-unstable, or incompatible with the predicted material and object category. They may also mix units, return impossible values, or assign properties that violate broad feasible ranges for the stated material.

Mechanism or approach:
A lightweight property constraint solver that takes candidate materials, raw VLM numeric estimates, parsed units, object category, and optional evidence strings, then emits raw_prediction, repaired_prediction, calibrated interval, confidence, constraint_violation_codes, and failure_warning fields.
Minimize a weighted repair distance from the raw VLM prediction subject to feasible property constraints: min_x sum_j w_j * rho_j(x_j - x_vlm,j) + alpha * material_category_incompatibility + beta * unit_uncertainty_penalty, subject to lower_{m,c,j} <= x_j <= upper_{m,c,j} for each selected material/category candidate. If no feasible candidate has sufficient confidence, return the raw prediction plus a failure_warning instead of forcing a repair.

Experiment and implementation plan:
BLIP-2/LLaVA/Qwen-VL zero-shot JSON prompting for object material and physical properties; GroundingDINO + SAM/SAM2 for object localization followed by VLM crop-level property prediction; CLIP material prediction + direct median table lookup without consistency repair
Indoor images with visible objects and masks/boxes from ScanNet, Matterport3D, or OpenRooms; VLM-generated object captions, material hypotheses, units, and numeric property predictions; Engineering material property tables with feasible property ranges and canonical units; A held-out validation set with proxy material/property labels or interval labels; A small manually checked validation subset for tuning violation-code thresholds and warning precision
prompt_vlm_object_properties.py; parse_and_validate_property_json.py; build_property_constraint_rules.py; repair_property_predictions.py; evaluate_consistency_and_error.py; audit_failure_warnings.py
valid_json_rate; unit_parse_success_rate; physical_feasibility_rate; material_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; failure_warning_precision
Disable numeric feasibility constraints; Disable category-conditioned constraints; Disable unit normalization and unit-consistency checks; Disable evidence-support checks; Use hard rejection only instead of minimal repair; Use table median replacement instead of constrained optimization
Apply constraints using randomly assigned object categories; Apply constraints using randomly shuffled material tables; Repair only formatting errors while leaving physical values unchanged; Run the solver with deliberately incorrect unit conversion factors to verify that unit checks affect feasibility and error
Reduce physically infeasible property tuples by at least 50 percent relative to raw VLM JSON; Maintain or improve density_log_mae and youngs_modulus_log_mae relative to raw VLM estimates; Increase valid_json_rate to at least 98 percent on the evaluation set; Failure warnings identify at least 70 percent of out-of-range, unit-inconsistent, or unsupported predictions at a false-positive rate fixed on validation; Report raw and repaired outputs separately for 100 percent of repaired examples

Risks, controls, or fallback:
Risk: rule-based repair may hide model errors by snapping outputs to broad plausible ranges, and broad constraints may improve feasibility without improving correctness. Fallback: always store raw and repaired predictions, score both, and use the module only as a validation, unit-normalization, and failure-warning layer if point-error does not improve.

---

Idea 3
Title:
Object-Crop Versus Context Disagreement as Uncertainty for Hidden Material Structure

Core proposal:
Add a disagreement-based uncertainty estimator that compares three frozen prediction views for each object: a crop-only material/property estimate from visible appearance, a context-only category prior from object class and scene type, and a crop-plus-context VLM estimate. The module converts disagreement among these views, material entropy, mask quality, occlusion, and visible-area cues into per-property interval widths and hidden-structure warnings. The estimator does not change the detector or the base material predictor; it only calibrates confidence and intervals.

Motivation or baseline weakness:
Single-image pipelines often overconfidently infer physical properties from visible surfaces, even when hidden structure dominates properties, such as veneer over particle board, painted metal, upholstered foam, hollow plastic, or laminated composites. A point prediction can therefore look plausible while missing the true bulk property range.

Mechanism or approach:
A small uncertainty calibrator that consumes disagreement features, object category, material entropy, mask confidence, visible area ratio, truncation/occlusion indicators, and category hidden-structure flags, then outputs per-property interval width multipliers, confidence scores, and failure_warning labels.
Learn calibrated uncertainty from proxy property labels or interval labels by minimizing interval score plus calibration error: L = interval_score(I(y_hat, s), y) + lambda * coverage_penalty + beta * warning_loss. Disagreement features include entropy_material, absolute log differences between crop and context property estimates, absolute log differences between VLM and table estimates, mask_confidence, visible_area_ratio, and occlusion indicators.

Experiment and implementation plan:
GroundingDINO + SAM/SAM2 + CLIP/OpenSurfaces material classifier + property table lookup; Mask2Former object masks with category-conditioned property priors; Qwen-VL/LLaVA prompted with crop plus full image context for property prediction
Indoor RGB images with object boxes/masks and object categories; Object crops, masked crops, and full-scene context crops; Proxy material labels and property intervals from ObjectFolder/ObjectFolder2.0, OpenSurfaces/MINC, and engineering material tables; Validation splits containing difficult categories with hidden or layered materials, such as sofas, chairs, cabinets, doors, appliances, painted objects, and laminated furniture; Held-out scene-level splits for calibration and selective-prediction evaluation
generate_crop_context_views.py; run_three_property_predictors.py; compute_disagreement_features.py; train_uncertainty_calibrator.py; evaluate_selective_prediction.py; export_object_level_json_with_warnings.py
prediction_interval_coverage; calibration_error; selective_risk; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; material_top3_accuracy; mask_iou; hidden_structure_warning_auc
Use material entropy only without crop-context disagreement; Use crop-context disagreement without mask/visibility cues; Use learned uncertainty calibrator versus fixed heuristic interval widening; Remove VLM branch and compare only crop material versus category prior; Evaluate per-category calibration with and without hidden-structure categories; Remove category hidden-structure flags while retaining numeric disagreement features
Use random disagreement features with the same marginal distribution; Shuffle crop predictions across objects within an image; Train calibrator on easy single-material categories and test on hidden-structure categories without adaptation; Replace visible-area and occlusion cues with random mask-quality values
Improve 90 percent prediction_interval_coverage to within plus or minus 5 percentage points while keeping intervals narrower than a category-only prior baseline; Reduce selective_risk by at least 15 percent at 70 percent retained coverage relative to entropy-only uncertainty; Assign higher average uncertainty to hidden-structure categories than to visually homogeneous categories on held-out data; Do not reduce material_top3_accuracy or object_recall relative to the frozen detection/material baseline; Hidden-structure warnings outperform random warning scores on held-out difficult categories

Risks, controls, or fallback:
Risk: disagreement can reflect model noise rather than true ambiguity, and low disagreement can still be confidently wrong when all branches share the same bias. Fallback: combine disagreement with conservative category-level priors, expose a failure_warning whenever the property is likely to depend on unobserved internal composition, and evaluate the method primarily as calibrated uncertainty rather than as a point-estimation improvement.

### Candidate B

Idea 1
Title:
Mask-Conditioned Material Mixture to Property Intervals

Core proposal:
For each detected object mask, estimate a calibrated distribution over visible surface-material classes using frozen masked-crop material classifiers aligned to OpenSurfaces/MINC-style taxonomies. Combine the top-k material probabilities with the detected object category to retrieve candidate physical-property intervals from ObjectFolder/ObjectFolder2.0-derived object/material property records and normalized in-dataset property proxies. The mechanism outputs interval-valued properties; intervals are widened when material entropy is high, when category-material compatibility is weak, or when the mask covers too little visible surface.

Motivation or baseline weakness:
Open-vocabulary detectors and promptable segmenters such as GroundingDINO plus SAM can localize visible objects, but direct category-to-property lookup ignores material mixtures and the fact that single RGB exposes mainly surface appearance. This can make density, elastic modulus, hardness, friction, and Poisson-ratio estimates overconfident, especially for coated, upholstered, laminated, transparent, or low-resolution objects.

Mechanism or approach:
A lightweight material-mixture-to-property calibrator consisting of temperature scaling or isotonic calibration over frozen material logits, a category-material compatibility matrix estimated from training data, and a deterministic interval aggregator that unions or probability-weights ObjectFolder/ObjectFolder2.0 property ranges.
Minimize calibrated material cross-entropy plus an interval scoring objective for physical properties. The interval term rewards containing proxy property labels from ObjectFolder/ObjectFolder2.0 mappings while penalizing unnecessarily wide intervals, with a separate calibration penalty for nominal interval coverage.

Experiment and implementation plan:
GroundingDINO; SAM; CLIP; OpenSurfaces; MINC; ObjectFolder; ObjectFolder2.0
Indoor RGB images with object boxes or masks and object categories; Masked object crops produced by GroundingDINO plus SAM or available ground-truth masks; Visible-surface material labels or proxy labels mapped to an OpenSurfaces/MINC-style taxonomy; Object-category to candidate-material mappings estimated from training annotations; Physical-property proxy intervals derived only from ObjectFolder and ObjectFolder2.0 records after unit normalization
run_detection_segmentation.py for GroundingDINO plus SAM masks; extract_masked_material_logits.py for masked crops and visible-region material logits; build_objectfolder_property_table.py for taxonomy alignment and unit normalization; train_material_calibrator.py for temperature scaling or isotonic calibration; aggregate_property_intervals.py for category-conditioned interval construction; evaluate_object_property_json.py for object-level JSON outputs and supported metrics
object_recall; mask_iou; material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error
Replace material mixture with single top-1 material; Remove object-category conditioning from property aggregation; Use uncalibrated material logits instead of calibrated material probabilities; Use boxes instead of masks for material evidence; Return median point estimates instead of intervals; Disable entropy-based interval widening
Randomly permute material labels before property aggregation; Use object category only with no masked visual crop; Use full-image material predictions instead of object masks; Evaluate on empty or synthetic blank masks to test context leakage; Shuffle ObjectFolder/ObjectFolder2.0 property records across material classes
Improve material_macro_f1 by at least 5 percentage points over the frozen masked-crop material baseline; Reduce density_log_mae and youngs_modulus_log_mae by at least 10% relative to category-only ObjectFolder/ObjectFolder2.0 lookup; Achieve prediction_interval_coverage within 5 percentage points of nominal 90% coverage; Keep mask_iou within 2 percentage points of the GroundingDINO plus SAM mask pipeline when using predicted masks; Reduce calibration_error relative to uncalibrated material-probability aggregation

Evidence paper IDs:
openalex:W4402500749; openalex:W4411238954; openalex:W2798280964; openalex:W2895238724; openalex:W4391722892; openalex:W4312347618

Risks, controls, or fallback:
Risk: visible surface material may not reveal internal composition, and ObjectFolder/ObjectFolder2.0 proxy intervals may not cover all indoor categories. Fallback: emit broader category-conditioned intervals, mark hidden-core/coated/reflective/transparent/low-resolution objects with failure_warning tags, and report results separately for categories with and without reliable property proxies.

---

Idea 2
Title:
Evidence-Gated VLM Property Reasoning

Core proposal:
Insert an evidence gate between segmentation/material recognition and VLM reasoning. For each object, build a structured object card containing the mask crop, category, top-k material hypotheses, visible surface cues, mask-quality fields, and ObjectFolder2.0-derived candidate property ranges. The VLM is constrained to choose, widen, or abstain from these ranges and must cite specific object-card fields. A verifier rejects unsupported citations, out-of-card materials, and ranges not traceable to candidate entries, then widens intervals or emits a failure warning.

Motivation or baseline weakness:
VLMs such as LLaVA, Qwen-VL, and BLIP-2 can describe objects and context, but physical-property predictions may be driven by language priors rather than localized visual evidence. This makes numeric or interval estimates prompt-sensitive, weakly calibrated, and difficult to audit.

Mechanism or approach:
A rule-based verifier plus lightweight calibration layer. The verifier checks JSON schema validity, citation presence, material/category consistency, and whether each predicted property interval is supported by a listed candidate range. The calibration layer learns when to widen accepted intervals using validation-set coverage errors from frozen VLM outputs.
Train only the verifier thresholds and interval calibrator while keeping detectors, material models, and VLMs frozen. Optimize valid structured-output rate, calibrated interval coverage, and property interval score, with penalties for unsupported citations, out-of-range numeric values, and failure to abstain when object-card evidence is insufficient.

Experiment and implementation plan:
GroundingDINO; SAM2; LLaVA; Qwen-VL; BLIP-2; CLIP; ObjectFolder2.0
Indoor RGB scene images with visible objects and object categories; Object masks or boxes generated by GroundingDINO plus SAM2 or provided by annotations; Masked object crops and optional local context crops; Material top-k predictions from frozen masked-crop classifiers; ObjectFolder2.0-derived candidate property intervals aligned to object category and material taxonomy; A small validation set with human-checked object cards, evidence citations, and acceptable interval decisions
generate_object_cards.py for masks, categories, material logits, mask quality, and local context cues; prompt_vlm_property_json.py for constrained VLM generation from object cards; verify_evidence_support.py for citation, schema, and range checks; calibrate_vlm_intervals.py for validation-set interval widening; score_structured_outputs.py for JSON validity, supported property metrics, and calibration
material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error
Free-form VLM prediction without object cards; Object cards without material top-k hypotheses; Object cards without ObjectFolder2.0 candidate property ranges; Verifier disabled; Verifier enabled but interval widening disabled; Mask crop removed while category and context are retained; Scene context removed from object cards
Ask the VLM to predict properties from category names only; Shuffle object cards across masks before VLM prompting; Remove the mask crop while keeping scene context to test context-only leakage; Inject false material candidates and measure verifier rejection rate; Replace candidate property ranges with randomly permuted ranges across categories
Reduce unsupported-evidence rate by at least 50% compared with unconstrained VLM prompting; Reach at least 85% prediction_interval_coverage for nominal 90% intervals; Reduce density_log_mae and youngs_modulus_log_mae by at least 10% relative to VLM-only prompting on accepted non-warning outputs; Keep valid structured JSON output rate above 98%; Reduce calibration_error relative to unverified object-card prompting

Evidence paper IDs:
openalex:W4399597788; openalex:W4402155831; openalex:W4385327621; openalex:W4402500749; openalex:W7148178853; openalex:W4312347618

Risks, controls, or fallback:
Risk: the VLM may still infer unsupported properties from memorized priors or ignore range constraints despite structured prompting. Fallback: replace numeric VLM generation with deterministic ObjectFolder2.0 range aggregation, and use the VLM only to produce qualitative visible-cue summaries and failure_warning explanations that are checked by the verifier.

---

Idea 3
Title:
Selective Uncertainty Head for Hidden-Material Failure Cases

Core proposal:
Add a selective uncertainty head that predicts object-level observability and hidden-material risk from frozen pipeline features: mask quality, crop resolution, visible area, material entropy, disagreement among CLIP/OpenSurfaces/MINC-style material predictions, optional VLM ambiguity descriptions, object category, and texture/specularity cues. For each object-property pair, the head chooses narrow interval, widened interval, or abstention-style failure warning without changing the underlying detector, segmenter, or material classifier.

Motivation or baseline weakness:
Detection, material recognition, and table-lookup pipelines can produce reasonable average property estimates, but they often do not know when to abstain on objects whose physical properties are underdetermined from single RGB, such as coated wood, fabric-covered foam, glossy plastic, painted metal, glass, or laminated surfaces.

Mechanism or approach:
A small gradient-boosted tree, logistic regression model, or two-layer MLP trained on frozen pipeline features to estimate the probability that each property estimate will exceed a predefined error threshold or miss its nominal interval.
Optimize selective calibration using validation labels derived from held-out proxy property intervals. The head minimizes accepted-set property error and calibration_error while maintaining a target accepted-object coverage, with binary supervision indicating whether the base interval missed the proxy label or exceeded a per-property log-error threshold.

Experiment and implementation plan:
Mask2Former; SAM; CLIP; OpenSurfaces; MINC; LLaVA; ObjectFolder
Indoor object crops and masks from RGB scene images; Proxy physical-property labels or intervals derived from ObjectFolder-linked material/category mappings; Frozen material logits from CLIP/OpenSurfaces/MINC-style models; Optional VLM material and ambiguity descriptions from LLaVA or BLIP-2 used only as frozen features; Mask quality features from SAM or Mask2Former outputs; Held-out validation categories containing coated, upholstered, reflective, transparent, or visually ambiguous objects
extract_pipeline_features.py for entropy, disagreement, mask area, boundary quality, texture cues, and category priors; make_proxy_error_labels.py for per-property high-error and interval-miss labels; train_selective_uncertainty_head.py for lightweight risk modeling; apply_abstention_policy.py for interval widening and failure_warning generation; evaluate_calibrated_acceptance.py for accepted-coverage, property error, interval coverage, and calibration
density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; material_macro_f1
Use material entropy only; Use model disagreement only; Remove mask-quality features; Remove object-category prior; Use one global uncertainty score instead of per-property uncertainty; Always output broad intervals with no learned selector; Use VLM ambiguity text only, without visual/material features
Train the uncertainty head on randomly shuffled error labels; Use only object mask area as the risk predictor; Evaluate calibration after permuting material logits across objects; Force acceptance of all predictions to recover the non-selective baseline; Randomly assign failure warnings at the same abstention rate as the learned head
At 70% accepted-object coverage, reduce accepted-set density_log_mae and youngs_modulus_log_mae by at least 20% relative to non-selective property lookup; Improve calibration_error by at least 25% relative to uncalibrated interval outputs; Flag at least 60% of high-error hidden-material cases while keeping false warning rate below 30%; Do not degrade accepted-set material_macro_f1 relative to the frozen material baseline; Maintain prediction_interval_coverage within 5 percentage points of the target nominal coverage after interval widening

Evidence paper IDs:
openalex:W4416850904; openalex:W4403323960; openalex:W4385327621; openalex:W2798280964; openalex:W3046559354; openalex:W4391722892

Risks, controls, or fallback:
Risk: proxy error labels may encode ObjectFolder/material-table bias rather than true physical uncertainty, and hidden-material cases may be rare in validation data. Fallback: report sensitivity across multiple proxy-label construction rules, evaluate the head primarily as an abstention and calibration module, and default to conservative interval widening when feature-based risk estimates are unstable.

---

## Item 18: HUM-4ee458bedd

类型：`single_idea`

### Candidate A

Title:
Mask-Conditioned Material Evidence Verification for VLM Property JSON

Core proposal:
Insert a verifier between segmentation and final property output. A VLM first proposes object category, material hypotheses, property intervals, and natural-language evidence. Each proposed material is then checked against masked-crop evidence using frozen CLIP/material classifiers and counterfactual material prompts. The verifier accepts, widens, or flags the VLM output according to three tests: the proposed material must score higher on the masked crop than on unrelated background or full-image context, it must be plausible for the object category without being category-only, and it must exceed visually confusable counterfactual materials by a validation-calibrated margin. Unsupported claims are not replaced by a new point estimate; they are converted to wider property intervals with failure_warning fields.

Motivation or baseline weakness:
Vision-language models such as LLaVA, BLIP-2, and Qwen-VL can produce plausible object-level physical-property JSON, but their material and property claims may be unsupported by localized visual evidence, sensitive to prompt wording, and influenced by object-category priors rather than the pixels inside the target mask.

Mechanism or approach:
A material-evidence verifier that computes per-object support scores from masked-crop similarity, mask-versus-full-image leakage contrast, category plausibility, and counterfactual material margins, then rescales property confidence and interval width without fine-tuning the VLM.
Fit verifier thresholds and calibration parameters on validation proxy labels while keeping VLMs and visual encoders frozen. Optimize material support and calibrated acceptance: objective = material_cross_entropy_proxy + alpha * counterfactual_margin_loss + gamma * confidence_calibration_loss + tau * unsupported_acceptance_penalty, with low-support predictions handled by abstention or interval widening rather than forced relabeling.

Experiment and implementation plan:
LLaVA prompted structured JSON prediction; BLIP-2 prompted structured JSON prediction; Qwen-VL prompted structured JSON prediction; GroundingDINO + SAM + CLIP material-to-property lookup
Indoor RGB images evaluated at object level; Object masks or boxes generated by GroundingDINO plus SAM/SAM2 or Mask2Former; Material class labels or proxy labels mapped to OpenSurfaces and MINC-compatible classes; Engineering material-property intervals linked to material classes; Prompt templates for VLM object category, material hypotheses, localized evidence, uncertainty, and property JSON
prompt_vlm_property_json.py to collect baseline VLM object-level predictions with multiple prompt paraphrases and self-reported confidence; score_local_material_evidence.py to compare masked crop, box crop, background crop, and full-image material scores; run_counterfactual_material_prompts.py to score visually confusable alternatives such as wood veneer versus plastic laminate, metal versus painted plastic, leather versus vinyl, and ceramic versus stone; calibrate_verifier.py to fit support thresholds, confidence scaling, and widening rules on validation proxy labels; evaluate_verified_json.py to compare accepted, widened, rejected, and raw VLM predictions under identical detected objects
material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Verifier without counterfactual material prompts; Verifier without full-image leakage contrast; Verifier using box crops instead of masks; No interval widening for unsupported VLM claims; Use VLM self-confidence only instead of verifier confidence
Verify each object using another random object's mask crop; accepted support should decrease; Use full-scene material scores as if they were object-local evidence; locality-sensitive calibration should degrade; Swap object categories while keeping masks fixed; category-plausibility-only acceptance should be exposed; Use adversarially broad prompts that list all common indoor materials as evidence; verifier should not accept all listed materials; Randomize the VLM material string before verification; acceptance and property accuracy should drop
Reduce calibration_error by at least 20% relative to raw VLM self-confidence; Reduce selective_risk by at least 15% at 70% object coverage relative to raw VLM predictions; Improve material_macro_f1 by at least 5 points over raw VLM material labels on proxy-labeled objects; Maintain or improve density_log_mae and youngs_modulus_log_mae on accepted predictions compared with CLIP top-1 lookup on the same objects; At least 80% of emitted failure_warning cases must correspond to high material ambiguity, mask error, visible-surface versus bulk-material mismatch, or category-property mismatch under manual audit

Evidence paper IDs:
openalex:W4399597788; openalex:W4392222076; openalex:W4402155831; openalex:W4385327621; openalex:W4402500749; openalex:W2798280964; openalex:W2895238724

Risks, controls, or fallback:
Risk: the verifier may reject too many objects because material datasets do not align with indoor object appearances, or because VLM predictions are correct at the object-category level but not visually verifiable from the crop. Fallback: use verifier scores for uncertainty calibration and interval widening rather than hard rejection, report selective-risk curves across acceptance thresholds, and keep a separate category-prior-only baseline to show whether gains come from localized evidence rather than semantic priors.

### Candidate B

Title:
Mask-Conditioned Material Evidence Verification for VLM Property JSON

Core proposal:
Add a verifier between segmentation and property output: each VLM-proposed material is checked against masked-crop evidence using frozen CLIP/material classifiers and counterfactual prompts. The final property prediction is allowed only when the proposed material passes a locality test, a category-plausibility test, and a counterfactual margin test; otherwise the system widens intervals and emits a failure warning.

Motivation or baseline weakness:
Vision-language models such as LLaVA, BLIP-2, and Qwen-VL can produce plausible object-level physical-property JSON, but their material/property claims may be unsupported by localized visual evidence and sensitive to prompts.

Mechanism or approach:
A material-evidence verifier that computes per-object support scores from masked crop similarity, full-image leakage contrast, and counterfactual material margins, then rescales property confidence and interval width.
Maximize verified material support for accepted predictions while maintaining property interval coverage; objective = material_cross_entropy_proxy + alpha * counterfactual_margin_loss + gamma * confidence_calibration_loss, with abstention/widening for low-support predictions.

Experiment and implementation plan:
LLaVA prompted structured JSON prediction; BLIP-2 prompted structured JSON prediction; Qwen-VL prompted structured JSON prediction; GroundingDINO + SAM + CLIP material-to-property lookup
Indoor RGB images from ScanNet, Matterport3D, or OpenRooms; Object masks or boxes generated by GroundingDINO plus SAM/SAM2 or Mask2Former; Material class labels or proxy labels from OpenSurfaces and MINC; Engineering material-property intervals linked to material classes; Prompt templates for VLM object category, material, evidence, and property JSON
prompt_vlm_property_json.py to collect baseline VLM object-level predictions; score_local_material_evidence.py to compare masked crop, box crop, and full-image material scores; run_counterfactual_material_prompts.py to score visually confusable alternatives such as wood veneer vs plastic laminate or metal vs painted plastic; calibrate_verifier.py to fit confidence scaling on validation proxy labels; evaluate_verified_json.py to compare accepted, widened, and rejected predictions
material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Verifier without counterfactual material prompts; Verifier without full-image leakage contrast; Verifier using box crops instead of masks; No interval widening for unsupported VLM claims; Use VLM self-confidence only instead of verifier confidence
Verify each object using another random object's mask crop; Use full-scene material scores as if they were object-local evidence; Swap object categories while keeping masks fixed; Use adversarially broad prompts that list all common indoor materials as evidence
Reduce calibration_error by at least 20% relative to raw VLM self-confidence; Reduce selective_risk by at least 15% at 70% object coverage relative to raw VLM predictions; Improve material_macro_f1 by at least 5 points over raw VLM material labels on proxy-labeled objects; Maintain or improve density_log_mae and youngs_modulus_log_mae on accepted predictions compared with CLIP top-1 lookup; At least 80% of emitted failure_warning cases must correspond to high material ambiguity, mask error, or category-property mismatch under manual audit

Evidence paper IDs:
openalex:W4399597788; openalex:W4392222076; openalex:W4402155831; openalex:W4385327621; openalex:W4402500749; openalex:W2798280964; openalex:W2895238724

Risks, controls, or fallback:
Risk: the verifier may reject too many objects because material datasets do not align with indoor object appearances. Fallback: use verifier scores only for uncertainty calibration and interval widening, not hard rejection, and report selective-risk curves to expose the coverage-accuracy tradeoff.

---

## Item 19: HUM-bb32f1ba00

类型：`portfolio`

### Candidate A

Idea 1
Title:
Mask-Conditioned Material Mixture Retrieval for Object Physical Property Intervals

Core proposal:
Use object masks from a detector-segmenter to isolate each object, split the masked crop into visible surface regions, estimate a probability distribution over a small set of material components, retrieve compatible engineering material records for each component, and propagate the weighted mixture into calibrated property intervals. The mixture is treated as visible-surface evidence rather than a guaranteed bulk composition, so object-category priors and uncertainty widening handle coated, hollow, or composite cases.

Motivation or baseline weakness:
A direct CLIP or VLM material label per detected object is too coarse for physical property prediction because many indoor object instances contain multiple visible materials, and a single top-1 material can produce large errors in density, modulus, hardness, and friction estimates.

Mechanism or approach:
A lightweight mask-conditioned material-mixture head that takes frozen visual embeddings, mask-pooled color and texture statistics, object category logits, and optional part-region features, then outputs top-k material mixture weights mapped to property-table intervals.
Minimize a combined objective with material multi-label cross-entropy or weak-label ranking loss, mixture-weight regularization, and interval negative log likelihood for physical properties. Each object prediction is computed as a weighted mixture of material-specific property distributions, constrained to remain inside valid table ranges and penalized when predicted intervals are overconfident on ambiguous objects.

Experiment and implementation plan:
GroundingDINO+SAM+CLIP top-1 material lookup; GroundingDINO+SAM+OpenSurfaces material classifier; Mask2Former object masks plus category-level median property lookup
Single RGB indoor images with object masks or boxes from ScanNet, Matterport3D, or OpenRooms; Material category labels, weak material tags, or region-level material annotations from OpenSurfaces and MINC; Engineering material property tables with density, Young's modulus, Poisson's ratio, hardness, and friction coefficient intervals; Object category to likely-material priors from ObjectFolder or ObjectFolder2.0; A small validation split with manually checked object category, visible material components, and plausible property intervals
run_object_detection_and_segmentation.py; extract_masked_object_features.py; train_material_mixture_head.py; map_material_mixtures_to_property_intervals.py; evaluate_object_property_predictions.py
material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error
Replace material mixture with top-1 material lookup; Remove object mask and use bounding-box crop only; Remove object category prior; Use uniform material mixture weights; Predict point properties without interval propagation
Shuffle material-property table rows before lookup; Use scene-level image embedding without object masks; Assign category-only median properties to every instance; Train with randomly reassigned material labels while preserving object categories
Improve material_top3_accuracy by at least 5 percentage points over CLIP top-1/top-k material retrieval on masked objects; Reduce density_log_mae and youngs_modulus_log_mae by at least 10% versus category-level median lookup; Achieve prediction_interval_coverage within 10 percentage points of the nominal interval level; Do not reduce object_recall or mask_iou relative to the frozen detection-segmentation front end

Risks, controls, or fallback:
Risk: visible surface material may not determine bulk physical properties, especially for coated, hollow, or composite objects. Fallback: emit explicit failure_warning fields for likely composite or hidden-core categories, downweight surface-only evidence, and widen uncertainty intervals using category-level priors.

---

Idea 2
Title:
Category-Constrained Property Prior Adapter for VLM Object Descriptions

Core proposal:
Add a retrieval-and-calibration adapter that converts frozen VLM object descriptions into constrained distributions over material-property records. The adapter parses object category, visible material phrases, functional descriptors, and scene context into candidate records, then filters and re-ranks them using category-material compatibility and valid property ranges. It outputs bounded numeric intervals rather than free-form numerical answers.

Motivation or baseline weakness:
General VLMs can describe objects and materials but often produce unconstrained, inconsistent physical property estimates because they are not tied to valid engineering ranges, object-category compatibility, or calibrated uncertainty.

Mechanism or approach:
A property-prior adapter that converts frozen VLM captions, tags, and object-category predictions into candidate material-property records, then learns a small calibration layer over retrieval scores, compatibility features, and range-validity features to output bounded intervals and uncertainty.
Optimize a constrained ranking and calibration objective: rank category-compatible material-property records above incompatible or implausible records, penalize predictions outside allowed table ranges, calibrate interval widths on held-out proxy labels, and add a consistency loss so semantically similar descriptions of the same masked object retrieve similar property intervals.

Experiment and implementation plan:
BLIP-2 or LLaVA object crop caption followed by naive keyword material lookup; Qwen-VL object question answering followed by hand-coded property table lookup; CLIP masked crop retrieval against material names
Object crops and masks from GroundingDINO+SAM, SAM2, or Mask2Former; Indoor scene images from ScanNet, Matterport3D, or OpenRooms; Proxy material labels from OpenSurfaces or MINC; Engineering material property tables with interval-valued properties; A small validation set with manually checked object category, visible material, and plausible property intervals
generate_object_vlm_descriptions.py; retrieve_candidate_property_records.py; train_property_prior_adapter.py; calibrate_property_intervals.py; evaluate_structured_json_outputs.py
material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk; invalid_output_rate
Remove VLM textual descriptions and use only object category; Remove category constraints and rely only on material keywords; Remove range constraints from property tables; Use uncalibrated retrieval scores as confidence; Use point estimates instead of intervals
Prompt the VLM for numerical physical properties directly without table grounding; Randomly permute object categories while keeping captions fixed; Retrieve from material names only with no physical property records; Use a property table with randomly permuted numeric intervals
Reduce invalid or out-of-range property outputs to below 1%; Reduce youngs_modulus_log_mae by at least 10% versus direct VLM numerical prompting; Improve calibration_error by at least 15% versus uncalibrated retrieval confidence; Maintain or improve material_top3_accuracy compared with CLIP masked crop retrieval

Risks, controls, or fallback:
Risk: VLM captions may hallucinate material cues or miss small visible components. Fallback: treat VLM text as one evidence source rather than ground truth, lower its weight when it conflicts with masked visual features or category constraints, and expose disagreement in failure_warning fields.

---

Idea 3
Title:
Selective Abstention and Failure Warnings for Hidden-Structure Physical Properties

Core proposal:
Train a lightweight uncertainty and abstention module that detects when visual evidence is insufficient for physical property prediction. The module uses disagreement among category priors, material classifiers, VLM descriptions, property-table candidates, mask quality, occlusion indicators, and candidate interval spread to either output calibrated wide intervals or flag explicit failure warnings while preserving a structured output for every detected object.

Motivation or baseline weakness:
A single RGB image cannot reliably reveal hidden structure such as hollow interiors, coatings, laminated materials, fasteners, or exact manufacturing process, yet standard pipelines still output overconfident physical properties for every visible object.

Mechanism or approach:
An evidence-disagreement calibrator that consumes detector confidence, mask quality, occlusion score, material top-k entropy, category-material prior entropy, VLM/material agreement, category/property compatibility, and property candidate spread to produce uncertainty, selective prediction decisions, interval widening factors, and failure_warning labels.
Minimize selective risk under a target coverage constraint by learning calibrated uncertainty scores that predict property error or interval miss on proxy-labeled validation objects. The loss combines error-ranking supervision, interval calibration loss, and a coverage penalty, while requiring every object to receive either a prediction with intervals or an explicit abstention-style failure_warning.

Experiment and implementation plan:
GroundingDINO+SAM+CLIP material lookup with softmax confidence; Mask2Former plus category-level property prior confidence; VLM-generated confidence scores for object material and properties
Indoor RGB images with detected objects and masks from ScanNet, Matterport3D, or OpenRooms; Proxy material labels from OpenSurfaces or MINC; Property interval labels from engineering material tables and ObjectFolder or ObjectFolder2.0 priors; A manually audited subset marking ambiguous, composite, reflective, occluded, transparent, coated, or hidden-structure objects
compute_pipeline_evidence_features.py; build_proxy_error_labels.py; train_disagreement_calibrator.py; evaluate_selective_prediction.py; emit_json_with_failure_warnings.py
prediction_interval_coverage; calibration_error; selective_risk; density_log_mae at fixed coverage; youngs_modulus_log_mae at fixed coverage; material_accuracy under non-abstained predictions; failure_warning_precision; failure_warning_recall; object_recall; mask_iou
Use only classifier softmax confidence; Remove property candidate spread features; Remove mask quality and occlusion features; Remove VLM/material disagreement features; Use fixed uncertainty intervals for all objects
Random abstention at the same coverage; Confidence based only on object detector score; Always output narrow intervals without failure warnings; Assign failure warnings to a random subset matched to the same warning rate
At 80% object coverage, reduce selective_risk by at least 20% versus softmax-confidence selection; Achieve prediction_interval_coverage within 5 percentage points of nominal for non-abstained predictions; Correctly flag at least 60% of manually audited hidden-structure or composite failure cases; Keep JSON completeness at 100% by emitting either predictions or explicit failure_warning for every detected object

Risks, controls, or fallback:
Risk: proxy error labels may not reflect true physical property errors, causing the calibrator to learn dataset artifacts. Fallback: evaluate separately on manually audited ambiguous objects, report selective-risk curves across coverage levels, and use conservative interval widening when uncertainty sources disagree.

### Candidate B

Idea 1
Title:
Mask-Localized Material Mixture Retrieval for Property Intervals

Core proposal:
Add a lightweight mask-localized material-mixture retriever that samples multiple masked visual patches per detected object, predicts a calibrated distribution over visible material components, and maps the posterior mixture to table-backed physical-property intervals. ObjectFolder/ObjectFolder2.0 are used only as object/category and multisensory property priors where available, while OpenSurfaces/MINC-style labels supervise visible material recognition; outputs are explicitly labeled as visible-surface-informed property intervals, not exact bulk measurements.

Motivation or baseline weakness:
CLIP/OpenSurfaces/MINC-style material recognition can assign a single semantic material to an object crop even when the visible evidence is localized, mixed, or surface-only; this propagates overconfident point estimates for density, Young's modulus, Poisson's ratio, hardness, and friction coefficient from 2D indoor images where hidden composition is often unobservable.

Mechanism or approach:
A frozen-encoder adapter with four components: masked patch sampler, material-mixture softmax head, property-interval aggregator over material/property tables and object priors, and JSON uncertainty formatter that emits interval bounds, posterior entropy, and failure_warning flags.
Minimize weak-label multiple-instance material loss over masked patches plus interval negative log likelihood for proxy physical-property intervals. Add a coverage-aware width regularizer that penalizes intervals that are too narrow on validation proxy labels while avoiding unbounded intervals through a validation-tuned maximum-width penalty.

Experiment and implementation plan:
GroundingDINO + SAM + CLIP single-material lookup; GroundingDINO + SAM2 + OpenSurfaces classifier + property-table lookup; Mask2Former + MINC classifier + property-table lookup
Indoor RGB images with object masks or boxes produced by GroundingDINO, SAM, SAM2, or Mask2Former; Object-level or region-level visible material labels or weak material tags aligned to OpenSurfaces and MINC categories; Object-category to material/property priors derived from ObjectFolder and ObjectFolder2.0 where category overlap exists; A versioned material-property table converted into density, Young's modulus, Poisson's ratio, hardness, and friction-coefficient intervals with source identifiers and unit normalization; Held-out validation objects with proxy material/property intervals for calibration and negative-control evaluation
run_detection_segmentation.py; extract_masked_object_patches.py; train_material_mixture_adapter.py; build_property_interval_table.py; evaluate_object_property_json.py
material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error
Replace mixture distribution with top-1 material lookup; Use whole-object crop instead of masked patch sampling; Remove object-category prior from the property aggregator; Use point estimates instead of intervals; Train with only visual features and no table-derived property constraints
Shuffle material-property table rows before aggregation; Evaluate on background masks treated as objects; Use random masks with correct object category labels; Use object category only without visible material cues; Replace masked patch features with patches from another object of the same category
Improve material_macro_f1 by at least 5 percentage points over top-1 CLIP/OpenSurfaces/MINC lookup on held-out indoor objects; Reduce density_log_mae and youngs_modulus_log_mae by at least 10 percent relative to single-material lookup on proxy interval midpoints; Achieve prediction_interval_coverage between 85 percent and 95 percent for nominal 90 percent proxy intervals; Reduce calibration_error by at least 20 percent relative to uncalibrated single-material lookup; Fail negative controls by showing coverage or accuracy drops when table rows, masks, or patch evidence are randomized

Evidence paper IDs:
openalex:W4402500749; openalex:W2798280964; openalex:W3012463097; openalex:W3200689778; openalex:W4312347618

Risks, controls, or fallback:
Risk: RGB-visible surfaces may not reveal bulk composition, so mixture estimates may still be wrong for veneered, painted, coated, hollow, or composite objects. Fallback: explicitly output wider visible-surface-informed intervals and a failure_warning when visible material evidence conflicts with object-category priors, when the material posterior entropy exceeds a validation-tuned threshold, or when the object category has no reliable overlap with ObjectFolder/ObjectFolder2.0 priors.

---

Idea 2
Title:
Evidence-Gated VLM Property Reasoning for Hallucination-Resistant JSON Outputs

Core proposal:
Introduce an evidence gate between frozen detection/segmentation and a frozen VLM. The VLM first emits candidate object-level JSON. For each material or physical-property claim, the gate checks whether the claim is supported by the object mask crop, material-retrieval neighbors, object-category priors, and table-backed property ranges. Unsupported or overprecise claims are replaced with calibrated intervals and explicit failure_warning fields rather than free-form corrections.

Motivation or baseline weakness:
VLMs such as LLaVA, BLIP-2, and Qwen-VL can produce plausible physical-property explanations from scene context, but their material and property claims may be unsupported by localized object evidence, sensitive to prompt wording, and overprecise relative to what a single 2D indoor image can justify.

Mechanism or approach:
A small evidence verifier that scores each VLM-generated material/property claim as supported, ambiguous, contradicted, or uncheckable using masked crop retrieval, object-category priors, and table-backed ranges; a deterministic JSON editor then rewrites material labels, property intervals, confidence values, and warnings according to the verifier state.
Maximize agreement between generated JSON claims and retrieval/table evidence while minimizing unsupported claims. Train or tune the verifier with supervised or rule-derived labels for supported, ambiguous, contradicted, and uncheckable claim states; calibrate verifier scores so abstention and warning decisions match validation-set reliability.

Experiment and implementation plan:
GroundingDINO + SAM + LLaVA prompted to emit object-level property JSON; GroundingDINO + SAM2 + BLIP-2 prompted to emit material and property estimates; Mask2Former + Qwen-VL prompted with object boxes and scene context
Indoor scene RGB images with object masks or boxes from GroundingDINO, SAM, SAM2, or Mask2Former; Raw VLM object-level JSON outputs from LLaVA, BLIP-2, and Qwen-VL under fixed prompt templates; Material labels or weak material tags aligned to OpenSurfaces and MINC categories; Physical-property proxy intervals from ObjectFolder, ObjectFolder2.0, and normalized material-property tables; A validation set of object-level JSON claims annotated or rule-labeled as supported, ambiguous, contradicted, or uncheckable by visible evidence and table ranges
prompt_vlm_object_json.py; retrieve_material_evidence.py; score_claim_support.py; calibrate_evidence_gate.py; evaluate_json_faithfulness_and_properties.py
material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error
Remove evidence gate and use raw VLM JSON; Use VLM confidence only without retrieval evidence; Use retrieval evidence only without scene context; Allow point estimates without table-backed intervals; Disable failure_warning generation; Use object category priors without masked crop evidence
Prompt the VLM with mismatched masks from another image; Swap retrieved material neighbors across object categories; Ask for impossible precision in physical-property point values; Evaluate with blank or blurred object crops while preserving category text; Replace property-table ranges with ranges from randomly selected materials
Reduce unsupported material/property claims by at least 30 percent relative to raw VLM prompting on the annotated validation set; Maintain or improve material_top3_accuracy relative to raw VLM prompting; Improve prediction_interval_coverage for nominal 90 percent proxy intervals to at least 85 percent; Reduce calibration_error by at least 20 percent relative to raw VLM confidence or self-reported certainty; Negative controls should trigger higher warning rates and lower verifier support scores than matched valid inputs

Evidence paper IDs:
openalex:W4399597788; openalex:W4392222076; openalex:W4402155831; openalex:W4385327621; openalex:W4402427278

Risks, controls, or fallback:
Risk: the verifier may reject correct but visually subtle VLM inferences or over-rely on incomplete material tables. Fallback: use a four-way decision policy that preserves the VLM category/context hypothesis but marks physical properties as broad intervals with low confidence when evidence is ambiguous or uncheckable, rather than forcing a hard correction.

---

Idea 3
Title:
Conformal Property Calibration from Proxy Labels and Object Similarity

Core proposal:
Add a post-hoc conformal calibration layer that operates on proxy labels and object-similarity groups. It converts material/property predictions into per-object prediction intervals with empirical coverage measured on held-out calibration splits stratified by object category, material ambiguity, and mask quality. The method explicitly claims coverage for the proxy visible-material target rather than for hidden true bulk composition.

Motivation or baseline weakness:
A plug-and-play pipeline using GroundingDINO/SAM-style masks plus material lookup can output physical-property values, but exact ground truth is often unavailable and uncertainty is poorly calibrated, especially for visually ambiguous indoor objects and low-quality masks.

Mechanism or approach:
A post-hoc conformal interval calibrator that consumes predicted material posterior, table-derived property distribution, mask quality score, object category, and scene-context embedding, then returns calibrated property intervals, confidence metadata, and abstention thresholds for unreliable objects.
Minimize calibrated interval width subject to validation-set coverage constraints for each physical property and for predefined subgroups. Fit nonconformity scores from residuals between predicted intervals and proxy labels, then tune abstention thresholds to reduce error among retained objects at a target retained-object fraction.

Experiment and implementation plan:
GroundingDINO + SAM + material lookup with uncalibrated confidence; GroundingDINO + SAM2 + CLIP/OpenSurfaces property intervals without conformal correction; Mask2Former + MINC property lookup with global uncertainty
Indoor RGB images and object masks or boxes produced by GroundingDINO, SAM, SAM2, or Mask2Former; Material proxy labels aligned to OpenSurfaces and MINC categories; Physical-property proxy intervals from ObjectFolder, ObjectFolder2.0, and normalized material-property tables; Calibration and test splits grouped by object category, material class, material posterior entropy, and mask quality; Optional measured ObjectFolder-style properties where category/object overlap permits separate evaluation from proxy table labels
generate_baseline_property_predictions.py; estimate_mask_quality_features.py; fit_conformal_property_intervals.py; evaluate_calibration_by_subgroup.py; export_calibrated_object_json.py
prediction_interval_coverage; calibration_error; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; object_recall; mask_iou
Global conformal calibration instead of subgroup calibration; Remove mask quality features; Remove material posterior entropy; Use category-only calibration groups; Use fixed engineering-table ranges without learned residual calibration
Calibrate on randomly permuted property labels; Use calibration objects from disjoint categories without subgroup adjustment; Apply calibration scores from high-quality masks to low-quality masks; Replace material posterior entropy with random confidence; Evaluate calibration after shuffling object masks across images
Achieve 90 percent nominal interval coverage within plus or minus 5 percentage points overall on proxy targets; Achieve subgroup coverage no lower than 80 percent for major material and object-category groups; Reduce calibration_error by at least 25 percent relative to uncalibrated lookup confidence; Do not increase median interval width by more than 20 percent relative to uncalibrated table intervals after calibration; Negative controls should show degraded coverage or inflated interval width, confirming dependence on valid labels, masks, and confidence features

Evidence paper IDs:
openalex:W4402500749; openalex:W4416850904; openalex:W4403323960; openalex:W2798280964; openalex:W3200689778; openalex:W4312347618

Risks, controls, or fallback:
Risk: proxy labels and table-derived intervals may not reflect true object-specific properties, so conformal guarantees may only hold for the proxy visible-material target. Fallback: report the calibrated target explicitly as a visible-material property interval, add failure_warning for hidden structure and coatings, and evaluate separate calibration curves for proxy labels versus any available measured ObjectFolder-style properties.

---

## Item 20: HUM-0ba295c926

类型：`single_idea`

### Candidate A

Title:
Evidence-Gated Material-to-Property Retrieval for Masked Indoor Objects

Core proposal:
For each object, first obtain a box or mask with GroundingDINO/SAM-style segmentation, then compute material evidence only inside the mask using masked image crops and material-recognition prompts or classifiers. A calibrated evidence gate combines masked material scores, object category, mask area, texture/edge statistics, and agreement between multiple material prompts. Materials below the gate are not treated as observed facts; instead they contribute to a broader material-family distribution. Physical-property intervals are retrieved from ObjectFolder/ObjectFolder2.0-style physical-property sources and material-property tables only through the gated material distribution. If no material has sufficient localized evidence, the output interval is widened and tagged as visually underdetermined rather than returning an overconfident point estimate.

Motivation or baseline weakness:
Open-vocabulary VLM or CLIP-style material predictions can be driven by object semantics rather than localized surface evidence. This is risky for indoor categories such as chairs, cabinets, cushions, doors, and tabletops where the same category can be wood, metal, plastic, glass, fabric, or composites, and where single RGB images may not reveal hidden material composition.

Mechanism or approach:
A lightweight evidence-gating calibrator that takes masked material logits, category prior logits, prompt-agreement scores, mask quality features, and optional source-table disagreement features, and returns a calibrated distribution over material labels plus per-property interval weights.
Train the gate with material cross-entropy or soft-label KL divergence and interval negative log likelihood for density, Young's modulus, Poisson's ratio, hardness, and friction coefficient. Add a calibration penalty that increases loss when high-confidence material predictions disagree with masked visual evidence, and optimize interval coverage/width tradeoff on a held-out calibration split.

Experiment and implementation plan:
GroundingDINO + SAM + CLIP material prompt + material-property table lookup; GroundingDINO + SAM + OpenSurfaces/MINC-style material classifier + material-property table lookup; LLaVA or Qwen-VL direct JSON material and property prediction without localized evidence gating
Indoor RGB images with object boxes or masks, either annotated or produced by GroundingDINO/SAM-style models; Object-level material labels, weak material labels, or manually audited proxy labels compatible with OpenSurfaces/MINC-style material categories; Physical-property ranges aligned to material families using ObjectFolder/ObjectFolder2.0-style sources and curated material-property tables; Held-out manually audited indoor objects with visible-material labels, property intervals, and flags for hidden, composite, or visually ambiguous materials
run_detection_segmentation.py; extract_masked_material_scores.py; build_material_property_table.py; train_evidence_gate.py; predict_object_property_json.py; evaluate_material_and_property_intervals.py
object_recall; mask_iou; material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Remove masked visual evidence and use object-category prior only; Remove object-category prior and use masked material scores only; Replace the calibrated evidence gate with uncalibrated top-1 masked material prediction; Use point estimates instead of property intervals; Disable low-evidence widening and failure warnings
Randomly permute material-property table rows while preserving material frequencies; Use a same-size background crop instead of the object mask for material scoring; Evaluate on blank or texture-erased object crops with category labels retained; Force all objects of the same category to share one material prediction; Replace the true object mask with a shifted mask that has low IoU with the object
Improve material_macro_f1 by at least 5 percentage points over the masked CLIP prompt baseline on audited objects; Reduce density_log_mae and youngs_modulus_log_mae by at least 10 percent versus top-1 material table lookup; Achieve prediction_interval_coverage within 5 percentage points of the target coverage level on audited intervals; Lower selective_risk by at least 15 percent when abstaining or widening intervals on the lowest-confidence 20 percent of objects

Evidence paper IDs:
openalex:W4402427278; openalex:W4402500749; openalex:W3047386722; openalex:W2798280964; openalex:W3200689778; openalex:W4312347618

Risks, controls, or fallback:
Risk: single RGB views may not reveal internal structure, coatings, laminates, or composite construction, so localized visual evidence can still support the wrong physical material. Fallback: report conservative material-family mixtures and wider property intervals, expose material-evidence disagreement in the JSON evidence field, and set failure_warning to hidden_material_or_composite_uncertain when the gate rejects all specific materials.

### Candidate B

Title:
Evidence-Gated Material-to-Property Retrieval for Masked Indoor Objects

Core proposal:
For each detected object, combine three signals: masked visual material evidence, object-category priors, and scene-context prompts. A small calibrated gate determines whether the masked-region evidence is strong enough to support each candidate material. Supported materials retrieve physical-property intervals from ObjectFolder/ObjectFolder2.0 and engineering material tables. If the visual evidence is weak or conflicts with the category prior, the method returns a wider property interval and marks the prediction as visually underdetermined rather than forcing a precise material.

Motivation or baseline weakness:
CLIP, BLIP-2, LLaVA, and Qwen-VL can infer plausible materials from object names and scene context, but these predictions are often weakly tied to the pixels inside the object mask. This is risky for indoor categories such as chairs, cabinets, cushions, doors, and tabletops, where the same object category can be made from wood, metal, plastic, fabric, glass, foam, or composite materials.

Mechanism or approach:
A lightweight evidence-gating calibrator that maps masked CLIP or material-classifier scores, object category, mask area, texture strength, and prompt agreement into calibrated probabilities over material labels and physical-property intervals.
Minimize material classification loss together with interval negative log likelihood for density, Young's modulus, Poisson's ratio, hardness, and friction coefficient, while penalizing overconfident property estimates when masked visual evidence disagrees with object-category priors.

Experiment and implementation plan:
GroundingDINO + SAM + CLIP material prompt + table lookup; GroundingDINO + SAM + OpenSurfaces/MINC classifier + table lookup; LLaVA direct JSON property prediction
Indoor RGB images with object masks or boxes from ScanNet, Matterport3D, or OpenRooms; Object and material labels or proxy labels from OpenSurfaces and MINC; Physical-property ranges from ObjectFolder, ObjectFolder2.0, and engineering material property tables; A held-out manually audited indoor-object set with material labels and acceptable property intervals
run_detection_segmentation.py; extract_masked_material_scores.py; build_material_property_table.py; train_evidence_gate.py; predict_object_property_json.py; evaluate_material_and_property_intervals.py
object_recall; mask_iou; material_accuracy; material_macro_f1; material_top3_accuracy; density_log_mae; youngs_modulus_log_mae; poisson_ratio_mae; hardness_mae_or_ordinal_error; friction_coefficient_mae; prediction_interval_coverage; calibration_error; selective_risk
Remove masked visual evidence and use object-category priors only; Remove object-category priors and use masked material scores only; Replace the evidence gate with uncalibrated top-1 CLIP material prediction; Use point estimates instead of property intervals; Disable low-evidence failure warnings while keeping the same material predictor
Randomly permute material-property table rows while preserving material frequency; Use a background crop instead of the object mask for material scoring; Evaluate on synthetic blank masks with category labels only; Force all objects from the same category to share one material prediction
Improve material_macro_f1 by at least 5 percentage points over the CLIP prompt baseline on audited objects; Reduce density_log_mae and youngs_modulus_log_mae by at least 10 percent versus top-1 material table lookup; Achieve prediction_interval_coverage within 5 percentage points of the target coverage level; Lower selective_risk by at least 15 percent when abstaining on the lowest-confidence 20 percent of objects

Evidence paper IDs:
openalex:W4402427278; openalex:W4402500749; openalex:W3047386722; openalex:W2798280964; openalex:W3200689778; openalex:W4312347618

Risks, controls, or fallback:
Risk: a single RGB image may not reveal internal structure, coatings, laminates, or composite construction, so visually plausible material estimates can still imply incorrect physical properties. Fallback: return conservative property intervals, include the material-evidence disagreement in the output, and set failure_warning to hidden_material_or_composite_uncertain.

---
