# 室内单图 3D 场景生成：匿名科研 Idea A/B 评审包

评审者代码：`indoor3d_expert`

条目数：20

请先完整阅读上一级目录的 `HUMAN_BLIND_REVIEW_INSTRUCTIONS_CN.md`。不要查看任何 private answer key，也不要使用大模型代评。

## Item 1: HUM-86deda094c

类型：`single_idea`

### Candidate A

Title:
Uncertainty-Aware Occluded Room Completion via Layout-Constrained Hypothesis Sets

Core proposal:
Add a lightweight hypothesis sampler that generates K layout and hidden-object scene-graph completions conditioned only on the input RGB-derived visible layout cues, monocular depth, visible object detections, and support relations. Each hypothesis is scored by explicit layout containment, object collision, floor/wall support, visible reprojection, and depth consistency checks; the method returns a ranked hypothesis set with calibrated existence probabilities instead of collapsing ambiguity to one completion.

Motivation or baseline weakness:
Text2Room and SceneScape can extend an indoor scene from one image, but occluded regions are often represented as a single confident continuation. This can create impossible room extents, unsupported hidden furniture, poor containment, and uncalibrated hidden-object predictions.

Mechanism or approach:
A layout-object hypothesis head that outputs K scene-graph completions with per-object existence probability, 3D box mean and covariance, support target, occlusion state, and hypothesis weight. It reuses pretrained depth, layout, detector, and image-to-3D modules as frozen components and trains only the small hypothesis head plus calibration parameters.
Train on synthetic single-view renders by minimizing a mixture objective: visible-mask reprojection loss, visible-depth consistency loss, layout boundary violation, pairwise object collision penalty, unsupported-object penalty, out-of-room penalty, and negative log likelihood of ground-truth hidden layout/object annotations under the K-hypothesis distribution. Calibrate hidden-object existence and room-extent probabilities with a held-out validation split.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; layout_estimation_baselines; monocular_depth_estimation
Structured3D single-view RGB renders with ground-truth layout, camera intrinsics, and depth; 3D-FRONT furnished room renders with 3D boxes, support relations, room boundaries, and occlusion masks; 3D-FUTURE object meshes and textures for proxy geometry attached to sampled boxes; Held-out synthetic stress split with high occlusion, mirrors of layouts, and nonstandard object arrangements
single_view_render_export.py to create RGB, depth, camera intrinsics, visible masks, occlusion masks, and ground-truth scene graphs; run_baselines_text2room_scenescape.py to generate baseline mesh or scene outputs from the same input image and fixed camera intrinsics; fit_layout_depth_objects.py to estimate visible layout planes, object boxes, and monocular depth priors from the single RGB image; sample_occluded_hypotheses.py to produce K weighted scene-graph completions with uncertainty fields; evaluate_geometry_relations_uncertainty.py to compute layout, object, collision, support, occlusion, and calibration metrics
layout_iou; depth_error; object_3d_iou; collision_rate; out_of_room_rate; support_relation_accuracy; object_relation_accuracy; occlusion_consistency; visible_object_recall; confidence_calibration
Remove multi-hypothesis sampling and keep only the maximum-probability completion; Remove collision and support filters while keeping the same sampler; Remove layout containment constraints and allow unconstrained hidden-region expansion; Use monocular depth only without detected object categories and relation cues; Vary K hypotheses in {1,3,5,10} to measure ambiguity coverage versus false-positive hidden objects
Shuffle visible object categories before hypothesis sampling while preserving boxes and masks; Use random room layout priors with the same object sampler and calibration procedure; Evaluate on deliberately inconsistent indoor images with impossible visible depth-layout alignment and require low confidence rather than confident completion; Replace support labels with random floor, wall, and object attachments during validation to test support-relation sensitivity
Reduce collision_rate by at least 25% relative to Text2Room or SceneScape on 3D-FRONT synthetic single-view tests; Improve layout_iou by at least 0.05 over the best direct single-image scene baseline using the same camera intrinsics; Reduce expected calibration error for hidden object existence by at least 15% relative to single-hypothesis completion; Maintain visible_object_recall within 95% of the best direct baseline while improving occlusion_consistency; Assign low calibrated confidence to at least 80% of severe ambiguity or inconsistent-layout cases at a fixed 10% false-alarm rate on valid cases

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: hypothesis sampling may improve uncertainty and relations without improving textured mesh quality. Fallback: output an uncertainty-annotated scene graph plus proxy boxes for occluded regions, and instantiate 3D-FUTURE proxy meshes only for high-confidence objects while leaving low-confidence regions as explicit uncertain volumes.

### Candidate B

Title:
Uncertainty-Aware Occluded Room Completion with Layout-Constrained Hypothesis Sets

Core proposal:
Add a lightweight hypothesis sampler on top of existing single-image scene pipelines. Given visible layout cues, monocular depth, detected objects, and support relations, the sampler proposes K layout-and-object completions for occluded regions. A constraint filter removes completions with severe collisions, room-boundary violations, or unsupported objects, while the final output preserves calibrated uncertainty over room extent, hidden-object existence, and object placement instead of collapsing to one guess.

Motivation or baseline weakness:
Text2Room and SceneScape can expand a room from a single image, but they typically commit to one hidden-region completion. This can make occluded geometry overconfident, produce impossible room extents, add unsupported furniture, and provide little indication when several completions are plausible.

Mechanism or approach:
A layout-object hypothesis head that predicts K scene-graph completions. Each completion contains room-layout parameters, per-object existence probability, 3D box distribution, support target, semantic category, and occlusion status. The module reuses pretrained depth, detection, layout, and image-to-3D components and avoids training a full room-scale 3D generator.
Train on synthetic single-view indoor renders using a loss that combines visible-image reprojection, monocular-depth consistency, layout-boundary violations, object-box likelihood, collision penalties, unsupported-object penalties, and negative log likelihood for hidden-object existence and placement. At evaluation time, score both the best completion and the calibrated top-K distribution over occluded regions.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; layout_estimation_baselines; monocular_depth_estimation
Structured3D single-view RGB renders with ground-truth layout, depth, camera intrinsics, and visible masks; 3D-FRONT furnished room renders with 3D object boxes, support relations, occlusion masks, and full scene graphs; 3D-FUTURE object meshes and textures for proxy geometry when object instances need to be visualized; Optional Matterport3D or ScanNet images for real-image stress testing without hidden-region ground truth
single_view_render_export.py to export RGB images, depth, camera intrinsics, visible masks, occlusion masks, and ground-truth scene graphs; run_baselines_text2room_scenescape.py to run baseline mesh or scene generation from the same single RGB input; fit_layout_depth_objects.py to estimate visible layout, object boxes, depth priors, and support cues; sample_occluded_hypotheses.py to generate K uncertainty-aware room and object completions; evaluate_geometry_relations_uncertainty.py to compute layout, object, collision, support, occlusion, and calibration metrics
layout_iou; depth_error; object_3d_iou; collision_rate; out_of_room_rate; support_relation_accuracy; object_relation_accuracy; occlusion_consistency; visible_object_recall; confidence_calibration; failure_detection_auc
Replace top-K hypothesis sampling with a single maximum-probability completion; Remove collision and support filtering from the hypothesis set; Remove layout constraints and allow unconstrained hidden-room expansion; Use monocular depth only, without object detections or relation cues; Vary K in {1,3,5,10} to measure ambiguity coverage, false positives, and calibration
Shuffle visible object categories before hypothesis sampling to test whether hidden completions depend on semantic evidence; Use random room-layout priors with the same object sampler to test layout dependence; Evaluate on non-indoor or strongly mirrored images and require high failure_warning rather than confident completion
Reduce collision_rate by at least 25% relative to Text2Room or SceneScape on 3D-FRONT synthetic single-view tests; Improve layout_iou by at least 0.05 over the best direct single-image scene baseline under the same camera-intrinsics setting; Reduce expected calibration error for hidden-object existence by at least 15% compared with a single-hypothesis completion; Maintain visible_object_recall within 95% of the best direct baseline while improving occlusion_consistency; Flag at least 80% of severe ambiguity cases at a fixed 10% false-alarm rate using failure_warning

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023

Risks, controls, or fallback:
Risk: hypothesis sampling may improve uncertainty and scene-graph plausibility without improving textured mesh quality. Fallback: expose the output as an uncertainty-annotated scene graph with proxy boxes for occluded regions, and instantiate 3D-FUTURE meshes only for high-confidence objects.

---

## Item 2: HUM-e25b32fdb4

类型：`single_idea`

### Candidate A

Title:
Relation-First Object Proxy Reconstruction for Renderable Indoor Scene Graphs

Core proposal:
Convert the single image into an object-centric scene graph with cuboids or retrieved proxy meshes, then optimize object scale, pose, room containment, and support relations before any texture transfer or inpainting. DUSt3R/MASt3R-style geometry is used only when valid image collections or generated auxiliary views are available; the core single-image path relies on monocular depth, masks, layout, and 3D-FRONT/3D-FUTURE size/support priors.

Motivation or baseline weakness:
Single-image scene generators and image-to-3D baselines can preserve the input-view appearance but often lack object-level 3D proxies that satisfy stable spatial relations such as on, against, inside, left-of, and in-front-of. This limits geometric evaluation, editing, and embodied use even when preview renderings look plausible.

Mechanism or approach:
A differentiable or search-based object proxy optimizer that initializes object cuboids from 2D detections, masks, monocular depth, and layout. It assigns candidate support surfaces, retrieves category-compatible proxy meshes when available, and adjusts 3D positions, scale, and yaw to satisfy relation constraints while preserving visible reprojection alignment.
Minimize a weighted objective combining 2D mask reprojection error, depth consistency, room-layout containment, pairwise collision penalties, support-surface distance, and relation-class penalties. Texture generation or view inpainting is applied only after proxy geometry passes collision, containment, and support checks.

Experiment and implementation plan:
image_to_3d_generation_baselines; Text2Room; WonderJourney; DUSt3R; MASt3R; 3D Gaussian Splatting
3D-FRONT and 3D-FUTURE for object categories, proxy meshes, sizes, and support priors; Structured3D for rendered single-view layout and depth supervision; A held-out rendered single-view split with ground-truth 3D boxes, support relations, and visible masks; Optional real indoor images used only when the same visible-object and relation annotations can be standardized
extract_2d_instances_and_masks.py; estimate_single_view_depth_or_pointmap.py; initialize_object_proxies.py; optimize_scene_graph_relations.py; retrieve_or_fit_proxy_meshes.py; render_scene_preview.py; evaluate_object_relation_metrics.py
object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; visible_object_recall; novel_view_consistency; depth_error; layout_iou
Use direct Text2Room-style mesh fusion without object proxy optimization; Optimize object poses without support-relation terms; Optimize support relations without collision penalties; Use cuboids only versus retrieved 3D-FUTURE proxy meshes; Run texture generation before versus after relation-consistent proxy fitting; Remove room-layout containment while keeping object relation terms
Randomize support-surface assignments while keeping object detections fixed; Use depth estimates with shuffled or incorrect scale to test metric-scale sensitivity; Evaluate on rendered scenes with transparent, reflective, or very thin support surfaces where proxy assumptions should be uncertain; Randomly rotate retrieved proxy meshes within each object category to confirm relation and reprojection metrics detect implausible fits
Improve support_relation_accuracy by at least 15 percentage points over image-to-3D generation baselines; Reduce collision_rate by at least 25% relative to Text2Room or WonderJourney outputs converted to meshes; Improve object_3d_iou by at least 10% on visible major furniture categories in 3D-FRONT renders; Maintain visible_object_recall within 5% of the best direct baseline; Improve novel_view_consistency without increasing out_of_room_rate relative to unconstrained mesh generation

Evidence paper IDs:
seed:text2room_2023; seed:wonderjourney_2023; seed:dust3r_2023; seed:mast3r_2024; seed:3dgs_2023; seed:3dfront_2020; seed:3dfuture_2020; seed:structured3d_2019; seed:midas_2023

Risks, controls, or fallback:
Risk: object detectors and masks may miss heavily occluded or small objects, causing incomplete scene graphs. Fallback: optimize and report major furniture separately from small clutter, keep an uncertain residual occupancy layer for low-confidence regions, and expose low visible_object_recall or mask confidence through confidence_calibration rather than hallucinating precise proxies.

### Candidate B

Title:
Relation-First Object Proxy Reconstruction for Renderable Indoor Scene Graphs

Core proposal:
Convert the single image into an object-centric scene graph with proxy meshes or cuboids, then optimize object scale, pose, and support relations jointly against monocular depth, visible masks, room layout, and collision constraints before texture transfer or inpainting.

Motivation or baseline weakness:
Single-image scene generators and image-to-3D baselines often preserve the input view appearance but fail to produce object-level 3D proxies that satisfy stable spatial relations such as on, against, inside, left-of, and in-front-of, limiting downstream navigation and embodied use.

Mechanism or approach:
A differentiable or search-based object proxy optimizer that initializes object cuboids from 2D detections and depth, assigns candidate support surfaces, and adjusts 3D positions to satisfy relation constraints while preserving reprojection alignment.
Minimize a weighted objective combining 2D mask reprojection error, depth consistency, room-layout containment, pairwise collision penalties, support-surface distance, and relation-class loss; generate textures only after proxy geometry and relations pass consistency checks.

Experiment and implementation plan:
image_to_3d_generation_baselines; Text2Room; WonderJourney; DUSt3R; MASt3R; 3D Gaussian Splatting
3D-FRONT and 3D-FUTURE for object categories, proxy meshes, sizes, and support priors; Structured3D for rendered single-view layout and depth supervision; ScanNet or Matterport3D for real indoor object relation evaluation
extract_2d_instances_and_masks.py; estimate_single_view_depth_or_pointmap.py; initialize_object_proxies.py; optimize_scene_graph_relations.py; retrieve_or_fit_proxy_meshes.py; render_scene_preview.py; evaluate_object_relation_metrics.py
object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; visible_object_recall; object_count_accuracy; novel_view_consistency; navigation_success_rate
Use direct Text2Room-style mesh fusion without object proxy optimization; Optimize object poses without support-relation terms; Optimize support relations without collision penalties; Use cuboids only versus retrieved 3D-FUTURE proxy meshes; Run texture generation before versus after relation-consistent proxy fitting
Randomize support-surface assignments while keeping object detections fixed; Use depth estimates with shuffled scale to test metric-scale sensitivity; Evaluate on scenes with mirrors or transparent tables where proxy assumptions should fail
Improve support_relation_accuracy by at least 15 percentage points over image-to-3D generation baselines; Reduce collision_rate by at least 25% relative to Text2Room or WonderJourney outputs converted to meshes; Improve object_3d_iou by at least 10% on visible major furniture categories in 3D-FRONT renders; Maintain visible_object_recall within 5% of the best direct baseline; Increase navigation_success_rate in a simple collision-aware simulator by at least 10% over unconstrained meshes

Evidence paper IDs:
seed:text2room_2023; seed:wonderjourney_2023; seed:dust3r_2023; seed:mast3r_2024; seed:3dgs_2023; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: object detectors and masks may miss heavily occluded or small objects, causing incomplete scene graphs. Fallback: keep a separate uncertain clutter layer for low-confidence regions and evaluate major furniture separately from small objects, with explicit failure_warning when visible_object_recall or mask confidence is low.

---

## Item 3: HUM-24e9ff2417

类型：`portfolio`

### Candidate A

Idea 1
Title:
Uncertainty-Aware Occlusion Volumes for Single-Image Room Completion

Core proposal:
Add a post-hoc occlusion-volume sampler that takes a single RGB image, monocular depth, visible object masks, and estimated room-layout planes, then samples a small set of hidden 3D occupancy hypotheses. Each hypothesis represents hidden room cells, candidate object categories, object extents, support surfaces, free-space constraints from the visible image, and confidence over alternatives. The final output contains a most-likely proxy scene plus per-cell and per-object uncertainty maps for occluded regions.

Motivation or baseline weakness:
Text2Room, SceneScape, and WonderJourney can generate plausible hidden room regions, but their outputs are usually consumed as a single deterministic completion. This makes them prone to overconfident hidden-object placement, weak ambiguity reporting, and physically inconsistent completions behind visible occluders.

Mechanism or approach:
A probabilistic scene-graph completion module that samples hidden room cells and candidate proxy objects under layout, depth-ordering, visible-free-space, collision, and support-relation constraints. It is used after existing single-image scene generation or reconstruction baselines and does not train a new large 3D generator.
Maximize a constrained posterior over hidden occupancy and object hypotheses: visible evidence likelihood from masks, depth, and layout; priors over room-bounded object placement and support relations; penalties for collision, out-of-room placement, and violation of visible free space; and a calibration term that aligns predicted confidence with empirical correctness on rendered synthetic validation views. Uncertainty is estimated from normalized posterior mass and ensemble disagreement across sampled hidden completions.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; layout_estimation_baselines; monocular_depth_estimation
Single RGB indoor image with optional camera intrinsics; Visible object masks or detections produced from the input image; Monocular depth prediction from the input image; Estimated room-layout planes from the input image; 3D-FRONT or Structured3D rendered single-view inputs with full ground-truth hidden geometry for evaluation; 3D-FUTURE assets when object proxy meshes are needed for evaluating hidden object extents
run_single_image_baselines.py; estimate_layout_and_depth.py; extract_visible_objects.py; sample_occlusion_volume_hypotheses.py; score_constrained_hidden_hypotheses.py; export_scene_graph_and_proxy_meshes.py; evaluate_occlusion_uncertainty.py; render_preview_views.py
depth_error; layout_iou; object_3d_iou; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; occlusion_consistency; visible_object_recall; confidence_calibration
Remove hidden occupancy uncertainty and output only the MAP completion; Remove support-relation constraints; Remove visible-free-space constraints from monocular depth and masks; Use a single deterministic layout instead of sampled layout perturbations; Replace object-category priors with category-agnostic cuboids; Remove posterior calibration and report raw sample frequency as confidence
Sample hidden objects uniformly without conditioning on visible image cues; Place occluded objects using only 2D inpainting-derived prompts without 3D constraints; Report a constant confidence score for all hidden regions; Ignore visible-free-space constraints while keeping the same object count distribution
Reduce collision_rate by at least 20% relative to Text2Room or SceneScape on matched single-view rendered evaluation; Improve occlusion_consistency by at least 15% over deterministic MAP-only completion; Improve confidence_calibration expected calibration error by at least 25% over constant-confidence and MAP-only controls; Keep visible_object_recall within 3 percentage points of the strongest direct baseline; Improve support_relation_accuracy for hidden-object hypotheses by at least 10 percentage points over uniform hidden-object sampling

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: hidden-region ground truth from synthetic rooms may reward common furniture priors rather than image-conditioned reasoning. Fallback: report visible-region metrics separately from hidden-region plausibility, stratify by occlusion amount, and require improvements in collision_rate, support_relation_accuracy, and confidence_calibration rather than calibration alone. Failure criterion: reject the module if it improves confidence_calibration only by assigning high uncertainty everywhere while failing to improve occlusion_consistency or collision_rate.

---

Idea 2
Title:
Physics-Checked Object Proxy Fitting for Renderable Single-Image Scene Graphs

Core proposal:
Add a lightweight object proxy fitting loop that converts visible generated or detected objects into category-aware cuboids or retrieved 3D-FUTURE proxy meshes. Object scale, yaw, translation, and support assignment are optimized against 2D masks, monocular depth, estimated room layout, category scale priors, support constraints, collision penalties, and out-of-room penalties. The output is a renderable proxy scene graph with per-object physical consistency warnings and uncertainty intervals from multi-start fitting.

Motivation or baseline weakness:
Single-image scene generators and monocular reconstruction methods can produce visually acceptable previews while placing objects at implausible 3D scale, support, orientation, or room location. These errors are hidden by image-space quality but harm renderable scene graphs, relation reasoning, and downstream navigation-like checks.

Mechanism or approach:
A constrained 3D object-layout optimizer over object scale, yaw, translation, support surface, and uncertainty intervals, initialized from single-image masks, monocular depth, and room layout. It replaces or augments raw generated geometry with physically checked proxy geometry while preserving the baseline's visible object set whenever possible.
Minimize a weighted objective consisting of 2D mask reprojection error, monocular depth residuals on visible object pixels, layout-boundary violations, support-relation violations, object-object intersections, out-of-room penalties, and category scale-prior penalties. Estimate uncertainty from the spread of feasible low-energy solutions across randomized initializations and layout/depth perturbations.

Experiment and implementation plan:
Text2Room; image_to_3d_generation_baselines; layout_estimation_baselines; monocular_depth_estimation; DUSt3R
Single RGB indoor image; Camera intrinsics if available or an estimated focal length; Object masks and categories inferred from the single image; Monocular depth prediction from the single image; DUSt3R pointmaps only for diagnostic settings where additional views are available and clearly marked non-strict; Estimated room layout planes; 3D-FRONT rendered single-view scenes with ground-truth object poses for evaluation; 3D-FUTURE proxy furniture assets for mesh retrieval and category scale priors
detect_and_segment_objects.py; estimate_depth_or_pointmap.py; fit_room_layout.py; initialize_object_proxies.py; optimize_object_proxy_scene.py; check_physics_and_collisions.py; export_renderable_scene_graph.py; evaluate_scene_graph_geometry.py
object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; visible_object_recall; depth_error; layout_iou; confidence_calibration
Remove collision penalty; Remove support-surface assignment; Use 2D boxes instead of masks; Use fixed category-average object sizes instead of optimized scales; Disable multi-start uncertainty estimation; Use generated mesh geometry directly without proxy fitting; Remove category scale priors
Randomly assign support surfaces while preserving 2D detections; Optimize only image reprojection with no physical terms; Fit all objects on the floor regardless of category; Evaluate with shuffled object categories to test dependence on semantic priors; Shrink every object by a fixed factor to test whether lower collision is achieved by degenerate geometry
Reduce collision_rate by at least 30% versus the raw generated scene representation; Improve support_relation_accuracy by at least 10 percentage points over direct baselines; Improve object_3d_iou by at least 10% on 3D-FRONT rendered single-view evaluation; Keep visible_object_recall within 5 percentage points of the raw baseline; Reduce out_of_room_rate by at least 20% without degrading object_3d_iou or visible_object_recall

Evidence paper IDs:
seed:text2room_2023; seed:3d_scenedreamer_2024; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:dust3r_2023; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: proxy meshes may improve physical metrics while reducing visual fidelity for irregular or partially visible objects. Fallback: keep high-fidelity generated textures or meshes as visual overlays, but use proxy geometry for collisions, support relations, and scene-graph export. Failure criterion: the method fails if physical consistency improves mainly by deleting, shrinking, or flattening objects, measured by drops in visible_object_recall, object_3d_iou, or support_relation_accuracy under the shrinkage negative control.

---

Idea 3
Title:
Single-Image Scene Completion Benchmark with Ambiguity-Stratified Evaluation

Core proposal:
Construct an ambiguity-stratified benchmark from evidence-supported indoor datasets by rendering single RGB views with known camera intrinsics, full 3D ground truth, visible and hidden object labels, layout annotations, and derived sets of physically plausible alternative hidden completions. Evaluate methods with separate visible-region reconstruction scores, hidden-region plausibility scores, physical relation checks, uncertainty calibration, and compliance labels indicating whether each method used only the single RGB input.

Motivation or baseline weakness:
Existing single-image-to-3D room methods are hard to compare because image-level preview quality can hide geometry errors, occluded regions are inherently multi-modal, and some baselines use extra prompts, generated views, camera paths, or iterative exploration that violate a strict single-RGB input protocol.

Mechanism or approach:
A dataset-generation and evaluator layer that labels each test view by occlusion fraction, layout visibility, object truncation, visible-object count, hidden-object count, and physical-constraint difficulty. It also defines a standardized JSON scene-graph schema for method outputs, including camera, layout, objects, support relations, uncertainty fields, and confidence values.
Define an evaluation score that rewards visible-image-grounded geometry and physically valid scene structure while avoiding over-penalization of ambiguous hidden regions. Visible regions are scored against ground truth, while hidden completions are scored using plausibility sets, support and collision validity, calibrated uncertainty, and consistency with visible free space. Scores are always reported by ambiguity stratum and by input-protocol compliance.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; Indoor_NeRF_prior_methods; layout_estimation_baselines; image_to_3d_generation_baselines; monocular_depth_estimation; DUSt3R; MASt3R; NeRF
3D-FRONT furnished rooms with 3D-FUTURE assets; Structured3D scenes with layout and structure annotations; Rendered single RGB images with camera intrinsics; Ground-truth room layouts, object poses, meshes, materials, and visibility masks from rendered scenes; Derived visible/hidden masks, free-space masks, support relations, and collision annotations; Optional method-native diagnostic inputs recorded separately from the strict single-RGB benchmark track
render_single_view_benchmark.py; compute_visible_hidden_masks.py; generate_ambiguity_labels.py; derive_plausible_hidden_completion_sets.py; convert_outputs_to_scene_schema.py; check_input_protocol_compliance.py; evaluate_geometry_consistency.py; evaluate_scene_relations.py; evaluate_uncertainty_calibration.py; baseline_runner_wrappers.py
depth_error; layout_iou; object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; occlusion_consistency; visible_object_recall; novel_view_consistency; confidence_calibration
Score hidden regions deterministically against one ground-truth completion; Remove ambiguity stratification; Remove physics and collision checks from the benchmark score; Evaluate only depth_error and novel_view_consistency; Use no standardized scene-graph schema; Do not separate visible and occluded objects; Ignore input-protocol compliance when comparing methods
Submit ground-truth visible geometry with random hidden objects; Submit visually plausible 2D inpainted views with no valid 3D scene graph; Submit empty-room completions to test whether metrics penalize missing objects; Submit overconfident confidence maps for all hidden regions; Submit a method-native run that uses extra views or prompts and mark it as non-strict to test protocol reporting
Baseline ranking changes when geometry, relation, and uncertainty metrics are added compared with novel_view_consistency-only evaluation; The evaluator penalizes random-hidden-object controls with at least 50% worse occlusion_consistency than compliant direct baselines; Confidence_calibration separates overconfident hidden-region submissions from calibrated uncertainty outputs; Ambiguity-stratified subsets show monotonic degradation in occlusion_consistency and object_3d_iou as occlusion fraction increases; The benchmark runs at least three direct baselines under the same strict single-RGB input protocol and flags non-compliant runs separately

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:nerf_2020; seed:nerfvs_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:dust3r_2023; seed:mast3r_2024; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: benchmark construction may be viewed as dataset engineering rather than a model contribution, and synthetic rendered rooms may not capture all real-image ambiguity. Fallback: keep the MVP focused on 3D-FRONT and Structured3D rendered splits with transparent ambiguity labels, strong negative controls, and strict input-protocol reporting; add real-image diagnostics only as non-primary evaluation if no full 3D ground truth is available. Failure criterion: the benchmark is not useful if simple negative controls score similarly to strong baselines, if rankings are dominated by a single view-consistency metric, or if methods using extra inputs are not clearly separated from strict single-RGB submissions.

### Candidate B

Idea 1
Title:
Uncertainty-Aware Layout-First Scene Completion for Single-Image Indoor 3D

Core proposal:
Add a lightweight probabilistic room-layout and occlusion-hypothesis stage before scene completion. Given one RGB image, estimated camera parameters, monocular depth, object detections, floor-wall cues, and visible free-space evidence, the stage samples a small set of metrically normalized room boxes or room polygons, visible-object anchor constraints, occluded free-space masks, occluded occupied-space masks, and uncertainty maps. The downstream generator, retrieval pipeline, or asset placer is constrained to condition on one sampled hypothesis at a time and must return per-object and per-region confidence tied to the selected hypothesis.

Motivation or baseline weakness:
Single-image indoor 3D scene generation can produce visually plausible completions while placing hidden objects, walls, doors, or room extents inconsistently with the observed perspective. Typical failures include objects outside the room, furniture floating or intersecting, unsupported hidden objects, and confidence estimates that do not distinguish constrained visible regions from ambiguous occluded regions.

Mechanism or approach:
A layout-conditioned occlusion sampler that outputs K candidate room layouts, K occluded free-space and occupied-space masks, visible-object anchor constraints, and uncertainty scores. It reuses pretrained depth, detection, layout, and asset-placement components and does not train a new 3D generator from scratch.
Select or sample scene completions that maximize image-consistent visible geometry and object alignment while minimizing layout violations, object collisions, unsupported objects, out-of-room placements, and confidence miscalibration. The main experiment compares identical scene-completion pipelines with and without the probabilistic occlusion sampler, holding depth estimation, object detection, asset retrieval, and rendering components fixed.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; layout_estimation_baselines; monocular_depth_estimation + image_to_3d_generation_baselines
Single RGB indoor image; camera intrinsics if available or estimated camera parameters; visible object detections; monocular depth estimates; floor-wall and vanishing cues; 3D-FRONT; 3D-FUTURE; Structured3D; Matterport3D; ScanNet; Hypersim
run_object_detection.py; estimate_monocular_depth.py; estimate_layout_candidates.py; sample_occluded_region_hypotheses.py; place_assets_with_constraints.py; render_scene_preview.py; evaluate_geometry_scene_uncertainty.py
layout_iou; depth_error; object_3d_iou; collision_rate; out_of_room_rate; support_relation_accuracy; object_relation_accuracy; occlusion_consistency; visible_object_recall; object_count_accuracy; novel_view_consistency; confidence_calibration; ambiguity_detection; failure_detection_auc
Use one deterministic layout instead of probabilistic layout sampling; Remove occluded-region occupancy uncertainty; Use depth-only constraints without visible-object anchors; Use visible-object anchors without room-layout constraints; Vary the number of sampled layout hypotheses K; Disable collision and support checks during placement; Condition generation on layout samples but remove confidence prediction
Use room layouts sampled from unrelated images; Use uniform random hidden-region occupancy maps; Perturb camera parameters beyond plausible calibration error; Place objects without preserving visible-object 2D projections; Replace confidence scores with constant values; Use a layout mirrored relative to the visible image geometry
Reduce out_of_room_rate by at least 25% relative to the strongest direct single-image indoor 3D baseline; Reduce collision_rate by at least 20% without decreasing visible_object_recall by more than 5%; Improve layout_iou by at least 0.05 absolute over deterministic layout conditioning; Improve expected calibration error for occluded-region confidence by at least 15%; Flag high-ambiguity or likely-failure cases with failure_detection_auc above 0.75

Risks, controls, or fallback:
Risk: layout estimation from cluttered single images may be unstable, and sampled hidden regions may overconstrain valid alternative completions. Fallback: keep multiple hypotheses through placement, use confidence-weighted constraints rather than hard constraints for uncertain walls or occluders, and report whether the module improves failure detection and collision or out-of-room warnings even when exact metric layout does not improve.

---

Idea 2
Title:
Scene-Graph Constraint Repair for Renderable Single-Image 3D Indoor Scenes

Core proposal:
Insert a scene-graph repair layer after an initial renderable 3D scene has been produced. The layer converts the scene into object nodes, room-boundary nodes, and relation candidates; estimates support, containment, adjacency, visibility, and collision constraints from detections, depth, layout, and proxy geometry; then solves a constrained pose-repair problem over object translation, yaw, scale within category-specific limits, and optional room-relative placement. The repair must preserve visible 2D reprojection and depth alignment, and it must leave low-confidence or ambiguous objects unchanged unless a violation is severe.

Motivation or baseline weakness:
Single-image indoor 3D scene generation can reconstruct visible appearance while violating physically meaningful relations such as objects resting on support surfaces, large furniture staying inside room boundaries, monitors standing on desks, beds aligning with walls, and distinct objects not occupying the same volume. These failures reduce usefulness for navigation, simulation, and embodied interaction even when rendered previews appear acceptable.

Mechanism or approach:
A relation-aware mixed discrete-continuous repair optimizer that takes an initial renderable scene graph and outputs adjusted object poses, repaired relation labels, per-relation confidence, and warnings for unresolved constraint conflicts.
Minimize a weighted energy with terms for visible-object 2D reprojection error, monocular-depth consistency, category-compatible scale changes, collision penalties, support-relation violations, room-boundary violations, and confidence-weighted relation priors. The main experiment tests whether repair improves physical and relational metrics over unrepaired initial scenes without materially degrading image alignment or object recall.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; Indoor_NeRF_prior_methods; 3D Gaussian Splatting + object proxy extraction; DUSt3R or MASt3R + asset retrieval; layout_estimation_baselines
Single RGB indoor image; visible object detections and categories; estimated depth or point cloud; initial generated 3D scene or scene graph; object proxy meshes from 3D-FUTURE; room layouts from 3D-FRONT or Structured3D; Matterport3D; ScanNet
generate_initial_scene.py; extract_scene_graph.py; infer_spatial_relations.py; optimize_scene_graph_repair.py; check_physics_collisions.py; render_before_after.py; evaluate_scene_graph_consistency.py
collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; object_3d_iou; chamfer_distance; visible_object_recall; image_reconstruction_lpips; object_count_accuracy; novel_view_consistency; navigation_success_rate; embodied_task_success_rate; failure_detection_auc
Disable support constraints; Disable collision constraints; Disable 2D reprojection preservation; Disable room-boundary constraints; Use category-agnostic relation priors; Use deterministic relation labels instead of confidence-weighted relations; Repair only positions versus positions plus scale and orientation; Repair all objects versus only objects involved in detected violations
Apply relation constraints inferred from a mismatched image; Randomly permute object categories before relation inference; Optimize only for visual reprojection with no physical constraints; Optimize only physical constraints with no image-alignment term; Initialize from random object poses inside the room instead of the generated scene; Use intentionally wrong support-surface labels for common furniture categories
Improve support_relation_accuracy by at least 10 percentage points over unrepaired scenes; Reduce collision_rate by at least 30% while increasing image_reconstruction_lpips by less than 0.03; Reduce out_of_room_rate by at least 25%; Maintain visible_object_recall within 95% of the unrepaired baseline; Improve downstream navigation_success_rate or embodied_task_success_rate by at least 5 percentage points in a simulator-style evaluation

Risks, controls, or fallback:
Risk: relation repair may overfit common spatial priors and move rare but valid configurations into stereotyped placements. Fallback: make repairs confidence-gated, cap pose and scale changes for visible objects, preserve multiple candidate repairs when constraints conflict, and emit unresolved-violation warnings rather than forcing a single implausible solution.

---

Idea 3
Title:
Benchmark and Failure-Aware Metric Suite for Ambiguous Single-Image Indoor Scene Generation

Core proposal:
Construct a benchmark protocol that evaluates each generated scene against visible constraints and a set of acceptable hidden-scene hypotheses rather than a single hidden ground truth. Each input image is paired with camera information when available, visible-object masks, visibility or occlusion labels, room-layout references or acceptable layout variants, physical-consistency checks, and failure annotations. The scorer uses strict penalties for visible-object mismatch, camera misalignment, room-boundary violations, collisions, unsupported objects, and overconfident hidden-region hallucinations, while using best-of-set or tolerance-based matching for genuinely ambiguous occluded regions.

Motivation or baseline weakness:
Single-image indoor 3D generation is inherently ambiguous, but common evaluations can overemphasize visible-view reconstruction or semantic similarity while undermeasuring hidden-region uncertainty, physical impossibility, relation errors, and downstream usability. This makes it difficult to tell whether apparent improvements are genuine scene-level improvements or only better visible-view rendering.

Mechanism or approach:
An evaluation harness with ambiguity-aware scene matching, visibility-aware geometry scoring, occluded-region uncertainty scoring, physical plausibility checks, and failure-warning evaluation. It trains no new large generator and only standardizes outputs from existing methods into a common scene representation.
Define a composite score that rewards visible reconstruction aligned to the input, plausible room-scale geometry, correct object and support relations, calibrated hidden-region uncertainty, and useful failure warnings. The main experiment ranks existing single-image indoor 3D baselines under conventional visible-view metrics and under the new ambiguity-aware score, then measures whether severe occlusion and physical failures change the ranking.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; Indoor_NeRF_prior_methods; monocular_depth_estimation; DUSt3R; MASt3R; 3D Gaussian Splatting; NeRF; layout_estimation_baselines; image_to_3d_generation_baselines
Single RGB indoor images; camera intrinsics if available or estimated camera parameters; ground-truth or pseudo-ground-truth room layouts; visible-object annotations; 3D object annotations where available; visibility masks or occlusion labels; 3D-FRONT; 3D-FUTURE; Matterport3D; ScanNet; Structured3D; Hypersim
prepare_single_view_benchmark.py; compute_visibility_and_occlusion_masks.py; normalize_scene_outputs.py; match_generated_to_reference_scene.py; run_collision_support_checks.py; score_uncertainty_calibration.py; evaluate_failure_warnings.py; generate_metric_report.py
depth_error; layout_iou; object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; occlusion_consistency; visible_object_recall; novel_view_consistency; image_reconstruction_lpips; object_count_accuracy; confidence_calibration; ambiguity_detection; failure_detection_auc; navigation_success_rate
Score with a single reference scene versus multiple acceptable hypotheses; Remove uncertainty calibration from the composite score; Remove physics and collision penalties; Remove the visible-object recall requirement; Evaluate only visible regions versus visible plus occluded regions; Use category-level matching versus instance-level matching; Compare metric ranking with and without downstream navigation checks; Use fixed metric weights versus task-specific metric weights
Evaluate generated scenes after randomly rotating camera alignment; Replace uncertainty maps with constant confidence; Use randomly sampled plausible rooms unrelated to the input image; Score only image-level appearance similarity without geometry checks; Ignore hidden regions entirely; Allow objects outside the room without penalty; Disable all collision and support checks while keeping the same visual metrics
Detect physical or layout failures in at least 20% of visually plausible outputs from direct baselines; Ensure severe collision or out-of-room failures reduce the composite score even when visible-view image_reconstruction_lpips is good; Show uncertainty calibration separates occluded ambiguous regions from visible constrained regions with at least 0.10 AUROC improvement over constant confidence; Show benchmark failure-warning labels can be predicted from generated outputs with failure_detection_auc above 0.75; Provide reproducible baseline rankings for at least three single-image indoor 3D baselines across two indoor datasets

Risks, controls, or fallback:
Risk: automatic evaluation may penalize plausible alternatives not present in the reference set or may inherit errors from detectors, depth estimators, and output normalization. Fallback: use ambiguity-aware best-of-set matching, separate visible-region correctness from hidden-region plausibility, report detector-dependent confidence intervals, include a small human-audited validation subset, and release per-metric scores rather than only a single aggregate number.

---

## Item 4: HUM-73dd2b496f

类型：`single_idea`

### Candidate A

Title:
Geometry-First Scene Graph Repair for Image-to-3D Indoor Generation

Core proposal:
Insert a post-generation geometry repair stage after a Text2Room/SceneScape/WonderJourney-style output. The stage canonicalizes the generated mesh into a typed scene graph containing room planes, visible object proxies, approximate object boxes, support candidates, containment relations, and pairwise spatial relations. It then solves a constrained 3D repair problem over object poses, box dimensions, support contacts, and layout-plane alignment while preserving visible-image projections and retaining the original generated textures where possible. The repair is accepted only if constraint violations are reduced without moving visible evidence beyond a preset reprojection/depth tolerance; otherwise the system emits a failure warning instead of silently changing the scene.

Motivation or baseline weakness:
Image-to-3D room generation baselines can produce visually plausible previews while violating basic 3D constraints: furniture floats, penetrates walls, lacks support surfaces, exits the room boundary, or drifts from the visible object layout because generation is not explicitly repaired against a structured scene graph.

Mechanism or approach:
A differentiable or search-based scene graph repair optimizer over room planes, object 3D boxes, support contacts, containment, and collision constraints. It uses pretrained depth, object-mask or box extraction, and layout modules for perception, and reuses the baseline-generated mesh as the visual asset rather than replacing it with a new generator.
Minimize E = reprojection_error + depth_alignment + layout_plane_error + object_box_prior + collision_penalty + support_penalty + out_of_room_penalty + relation_penalty + texture_anchor_penalty, subject to visible object masks remaining aligned with the input RGB image and repaired proxy geometry remaining physically plausible and renderable. If the minimum feasible solution exceeds a visible-alignment threshold, the method returns an explicit repair failure warning.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; image_to_3d_generation_baselines; layout_estimation_baselines; monocular_depth_estimation; 3D-FRONT
Single RGB indoor images with visible object masks, boxes, or detector outputs; 3D-FRONT/3D-FUTURE scenes for object-size, support, containment, and relation priors; Structured3D rendered views for room layout and depth evaluation; Held-out real single-view indoor images for visible reprojection, depth, and qualitative stress tests where full object ground truth is not available
run_generation_baselines.py to produce initial Text2Room, SceneScape, WonderJourney, or image-to-3D baseline scenes under matched inputs; baseline_scene_to_graph.py to extract layout planes, object proxies, boxes, and approximate meshes from generated scenes; fit_proxy_scene_graph.py to estimate typed object proxies and candidate support or containment relations; repair_scene_geometry.py to optimize object transforms, supports, collisions, and room containment with visible-alignment constraints; render_repaired_scene.py to export repaired mesh, proxy scene graph, and before/after previews; evaluate_scene_graph_geometry.py for relation, collision, layout, depth, and visible-alignment metrics
layout_iou; object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; depth_error; visible_object_recall; novel_view_consistency
Use the visual generation output directly without repair; Optimize collisions only without support relations; Optimize support relations only without room containment; Remove visible reprojection and depth constraints and allow unconstrained 3D repair; Use class-agnostic boxes instead of category-specific size and support priors; Replace the accept/reject failure gate with always-apply repair
Apply the repair optimizer to random object layouts initialized far from the input image to verify visible-alignment constraints reject them; Shuffle object categories while keeping boxes fixed to test whether semantic support priors matter; Disable room layout planes and allow objects outside the room to verify containment penalties are necessary; Run repair on ground-truth synthetic layouts where changes should be minimal; Perturb visible object masks before repair to test whether the optimizer overfits noisy perception rather than stable 3D constraints
Reduce collision_rate by at least 30% compared with the unrepaired baseline output; Reduce out_of_room_rate by at least 30% without decreasing visible_object_recall by more than 3 percentage points; Improve support_relation_accuracy by at least 10% on rendered 3D-FRONT/Structured3D-style test views; Maintain depth_error and layout_iou within 5% of the unrepaired visible reconstruction unless the baseline was already geometrically invalid; Failure criterion: if repairs improve constraints only by moving visible objects away from their input-image projections, the mechanism fails the single-image alignment requirement

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:3d_scenedreamer_2024; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: proxy boxes may oversimplify detailed furniture and improve relation metrics while hurting visual fidelity. Fallback: keep original textured meshes attached to repaired proxy transforms, report proxy-geometry metrics separately from rendered-view metrics, and trigger failure warnings when the repair requires large visible reprojection or depth changes.

### Candidate B

Title:
Geometry-First Scene Graph Repair for Image-to-3D Indoor Generation

Core proposal:
Insert a post-generation geometry repair stage that converts an initial Text2Room/SceneScape/WonderJourney mesh into a typed scene graph with layout, object proxies, supports, containment, and relative relations. The module then solves a constrained 3D optimization over object boxes, proxy meshes, and room layout planes while preserving visible-image projections and textures. The output is a renderable scene graph plus corrected proxy geometry, with failure warnings when constraints cannot be satisfied without moving visible evidence too far.

Motivation or baseline weakness:
Image-to-3D room generation baselines can produce visually plausible previews while violating basic 3D constraints: furniture floats, penetrates walls, lacks support surfaces, or drifts from the visible object layout because generation is not explicitly repaired against a structured scene graph.

Mechanism or approach:
A differentiable-or-search-based scene graph repair optimizer over room planes, object 3D boxes, support contacts, and collision constraints; all perception inputs come from pretrained depth, object detector, and layout modules.
Minimize E = reprojection_error + depth_alignment + layout_plane_error + object_box_prior + collision_penalty + support_penalty + out_of_room_penalty + relation_penalty, subject to visible object masks remaining aligned with the input RGB image and corrected geometry remaining renderable.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; image_to_3d_generation_baselines; layout_estimation_baselines; monocular_depth_estimation
Single RGB indoor images with visible object masks or detector outputs; 3D-FRONT/3D-FUTURE scenes for object-size and support priors; Structured3D for room layout evaluation; ScanNet or Matterport3D for real-world geometry and relation stress tests
baseline_scene_to_graph.py to extract layout planes, object boxes, and meshes from generated scenes; fit_proxy_scene_graph.py to estimate typed object proxies and relations; repair_scene_geometry.py to optimize positions, supports, and collisions; render_repaired_scene.py to export mesh or scene graph previews; evaluate_scene_graph_geometry.py for relation, collision, layout, and visible alignment metrics
layout_iou; object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; depth_error; visible_object_recall; image_reconstruction_lpips; novel_view_consistency; failure_detection_auc
Use visual generation output directly without repair; Optimize collisions only without support relations; Optimize support relations only without room containment; Remove visible reprojection constraints and allow unconstrained 3D repair; Use class-agnostic boxes instead of category-specific size and support priors
Apply the repair optimizer to random object layouts initialized far from the input image; Shuffle object categories while keeping boxes fixed to test whether semantic support priors matter; Disable room layout planes and allow objects outside the room; Run repair on already ground-truth synthetic layouts where changes should be minimal
Reduce collision_rate by at least 30% compared with the unrepaired baseline output; Reduce out_of_room_rate by at least 30% without decreasing visible_object_recall by more than 3 percentage points; Improve support_relation_accuracy by at least 10% on 3D-FRONT/Structured3D rendered views; Keep image_reconstruction_lpips degradation below 0.03 relative to the initial generated scene; Failure criterion: if repairs improve constraints only by moving visible objects away from their input-image projections, the mechanism fails the single-image alignment requirement

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:3d_scenedreamer_2024; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023

Risks, controls, or fallback:
Risk: proxy geometry may oversimplify detailed furniture and improve box metrics while hurting visual quality. Fallback: keep original textured meshes attached to repaired proxy transforms, report proxy and render metrics separately, and trigger failure warnings when the repair requires large visible reprojection changes.

---

## Item 5: HUM-ef372709a7

类型：`portfolio`

### Candidate A

Idea 1
Title:
Uncertainty-Aware Occluded Room Completion via Layout-Constrained Hypothesis Sets

Core proposal:
Add a lightweight hypothesis sampler that generates K layout and hidden-object scene-graph completions conditioned only on the input RGB-derived visible layout cues, monocular depth, visible object detections, and support relations. Each hypothesis is scored by explicit layout containment, object collision, floor/wall support, visible reprojection, and depth consistency checks; the method returns a ranked hypothesis set with calibrated existence probabilities instead of collapsing ambiguity to one completion.

Motivation or baseline weakness:
Text2Room and SceneScape can extend an indoor scene from one image, but occluded regions are often represented as a single confident continuation. This can create impossible room extents, unsupported hidden furniture, poor containment, and uncalibrated hidden-object predictions.

Mechanism or approach:
A layout-object hypothesis head that outputs K scene-graph completions with per-object existence probability, 3D box mean and covariance, support target, occlusion state, and hypothesis weight. It reuses pretrained depth, layout, detector, and image-to-3D modules as frozen components and trains only the small hypothesis head plus calibration parameters.
Train on synthetic single-view renders by minimizing a mixture objective: visible-mask reprojection loss, visible-depth consistency loss, layout boundary violation, pairwise object collision penalty, unsupported-object penalty, out-of-room penalty, and negative log likelihood of ground-truth hidden layout/object annotations under the K-hypothesis distribution. Calibrate hidden-object existence and room-extent probabilities with a held-out validation split.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; layout_estimation_baselines; monocular_depth_estimation
Structured3D single-view RGB renders with ground-truth layout, camera intrinsics, and depth; 3D-FRONT furnished room renders with 3D boxes, support relations, room boundaries, and occlusion masks; 3D-FUTURE object meshes and textures for proxy geometry attached to sampled boxes; Held-out synthetic stress split with high occlusion, mirrors of layouts, and nonstandard object arrangements
single_view_render_export.py to create RGB, depth, camera intrinsics, visible masks, occlusion masks, and ground-truth scene graphs; run_baselines_text2room_scenescape.py to generate baseline mesh or scene outputs from the same input image and fixed camera intrinsics; fit_layout_depth_objects.py to estimate visible layout planes, object boxes, and monocular depth priors from the single RGB image; sample_occluded_hypotheses.py to produce K weighted scene-graph completions with uncertainty fields; evaluate_geometry_relations_uncertainty.py to compute layout, object, collision, support, occlusion, and calibration metrics
layout_iou; depth_error; object_3d_iou; collision_rate; out_of_room_rate; support_relation_accuracy; object_relation_accuracy; occlusion_consistency; visible_object_recall; confidence_calibration
Remove multi-hypothesis sampling and keep only the maximum-probability completion; Remove collision and support filters while keeping the same sampler; Remove layout containment constraints and allow unconstrained hidden-region expansion; Use monocular depth only without detected object categories and relation cues; Vary K hypotheses in {1,3,5,10} to measure ambiguity coverage versus false-positive hidden objects
Shuffle visible object categories before hypothesis sampling while preserving boxes and masks; Use random room layout priors with the same object sampler and calibration procedure; Evaluate on deliberately inconsistent indoor images with impossible visible depth-layout alignment and require low confidence rather than confident completion; Replace support labels with random floor, wall, and object attachments during validation to test support-relation sensitivity
Reduce collision_rate by at least 25% relative to Text2Room or SceneScape on 3D-FRONT synthetic single-view tests; Improve layout_iou by at least 0.05 over the best direct single-image scene baseline using the same camera intrinsics; Reduce expected calibration error for hidden object existence by at least 15% relative to single-hypothesis completion; Maintain visible_object_recall within 95% of the best direct baseline while improving occlusion_consistency; Assign low calibrated confidence to at least 80% of severe ambiguity or inconsistent-layout cases at a fixed 10% false-alarm rate on valid cases

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: hypothesis sampling may improve uncertainty and relations without improving textured mesh quality. Fallback: output an uncertainty-annotated scene graph plus proxy boxes for occluded regions, and instantiate 3D-FUTURE proxy meshes only for high-confidence objects while leaving low-confidence regions as explicit uncertain volumes.

---

Idea 2
Title:
Relation-Verified Object Proxy Insertion for Physically Plausible Single-Image Scenes

Core proposal:
Insert a relation-verification loop after a baseline scene output is produced. The loop detects visible objects, estimates room layout and depth from the input image, retrieves category-compatible proxy meshes, initializes 3D boxes from visible masks and depth, and optimizes object transforms under explicit floor/wall support, inter-object collision, room containment, and visible-mask reprojection constraints. If no low-energy solution exists, the system returns a low-confidence or partial scene rather than a physically inconsistent completion.

Motivation or baseline weakness:
Image-to-3D scene baselines can produce plausible render previews while violating physical relations: furniture floats, penetrates walls, leaves the room volume, or contradicts visible support and adjacency cues. NeRF and 3D Gaussian Splatting are included only as renderable-scene representations when initialized or adapted from the same single-RGB protocol, not as inherently single-image completion methods.

Mechanism or approach:
A scene-graph relation optimizer that adjusts object 3D position, scale, yaw, and support attachment for generated or retrieved proxy meshes while preserving the baseline-generated visible appearance through fixed masks, texture anchors, and reprojection constraints.
Minimize a weighted constrained energy over object transforms and support assignments: 2D mask reprojection error, monocular depth residual inside visible masks, deviation from category-specific 3D box priors, object-object collision volume, wall/floor penetration, room-boundary containment, support-plane distance, and support-relation classification loss. Reject or mark outputs uncertain when optimized energy remains above a validation-calibrated threshold.

Experiment and implementation plan:
Text2Room; SceneScape; image_to_3d_generation_baselines; 3D Gaussian Splatting; NeRF; monocular_depth_estimation
3D-FRONT scenes with object boxes, room layouts, and support relations; 3D-FUTURE meshes and textures for proxy object geometry; Structured3D room layouts, depth annotations, and rendered single RGB images; Synthetic validation splits with controlled collisions, floating objects, wall penetrations, and missing support labels
detect_visible_objects.py to produce masks, classes, and confidence scores from the single RGB input; estimate_depth_layout.py to produce monocular depth and room boundary planes; retrieve_proxy_meshes.py to map detected object categories to approximate 3D-FUTURE meshes and category-size priors; optimize_scene_relations.py to solve object transforms, room containment, and support constraints; render_preview_and_scene_graph.py to export a renderable proxy scene and relation graph; evaluate_physical_consistency.py to compute collision, support, out-of-room, object, depth, and visible-recall metrics
collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; visible_object_recall; object_3d_iou; depth_error; layout_iou; novel_view_consistency; confidence_calibration
No relation optimizer after baseline scene generation; Collision-only optimizer without support constraints; Support-only optimizer without collision constraints; Use category-average boxes instead of retrieved proxy meshes; Disable rejection and always output a scene even when constraint energy is high
Randomize support labels while preserving object detections and room layout; Optimize object transforms against a shuffled depth map from another room; Use an empty-room layout with object detections removed to verify that visible_object_recall depends on image evidence; Swap room boundaries between scenes while keeping object masks fixed to test containment sensitivity
Reduce collision_rate by at least 30% over direct image-to-3D scene baselines on 3D-FRONT single-view renders; Reduce out_of_room_rate by at least 40% without decreasing visible_object_recall by more than 5%; Improve support_relation_accuracy by at least 10 percentage points over the best baseline scene graph extracted from generated geometry; Keep depth_error and layout_iou no worse than the unoptimized baseline by more than 5% relative on visible regions; Improve confidence_calibration for rejected or low-confidence physically inconsistent cases relative to always-output baselines

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:3d_scenedreamer_2024; seed:3dgs_2023; seed:nerf_2020; seed:midas_2023; seed:3dfront_2020; seed:3dfuture_2020; seed:structured3d_2019

Risks, controls, or fallback:
Risk: proxy retrieval may reduce visual realism when CAD assets mismatch the photo or generated texture. Fallback: keep baseline textures as fixed appearance anchors or textured billboards, use proxy meshes only for physics and relations, and evaluate the contribution primarily as a downstream-usable collision-aware scene graph rather than a photorealistic reconstruction.

---

Idea 3
Title:
Single-Image Scene Completion Benchmark with Ambiguity-Aware Failure Scoring

Core proposal:
Construct a controlled benchmark from synthetic indoor rooms rendered from one camera, with ground-truth visible geometry, hidden object annotations, room layout, relations, and ambiguity labels derived from groups of similar room configurations. Standardized adapters convert renderable scenes, meshes, radiance fields, pointmaps, or scene graphs into a common representation so metrics can separately score visible reconstruction, hidden completion, physical validity, uncertainty calibration, and failure awareness.

Motivation or baseline weakness:
Existing single-image scene generation and reconstruction papers are difficult to compare because visual quality, geometry consistency, hidden-region plausibility, physical relations, and failure awareness are often evaluated with different inputs and output formats. Multi-view reconstruction methods such as DUSt3R, MASt3R, NeRF, and NeRFVS must therefore be clearly separated from true single-RGB completion methods or run only under controlled adapter settings.

Mechanism or approach:
A benchmark adapter that converts each method output into a common scene-level representation with layout planes, object boxes or meshes, spatial relations, uncertainty fields when available, render previews, and confidence or failure_warning scores. Methods without uncertainty must expose a deterministic confidence proxy so calibration can be evaluated but not confused with true probabilistic completion.
No large training objective is introduced; the core contribution is standardized measurement. For optional reporting, learn only a lightweight validation-set failure-warning calibrator from method diagnostics such as depth residual, collision count, out-of-room count, layout confidence, and hidden-area fraction, and report calibrated and uncalibrated scores separately.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; Indoor_NeRF_prior_methods; layout_estimation_baselines; DUSt3R; MASt3R; monocular_depth_estimation
3D-FRONT rooms paired with 3D-FUTURE object meshes and textures; Structured3D images with room layout and depth annotations; Rendered single RGB inputs with camera intrinsics, depth, segmentation, visible-object lists, hidden-object lists, room boundaries, and relation graphs; Controlled ambiguity groups formed by matching room type, visible layout, and visible object evidence but varying plausible hidden objects
render_single_view_benchmark.py to generate benchmark images and annotations from fixed camera protocols; standardize_scene_output.py to convert mesh, NeRF-style, Gaussian-style, pointmap, or scene-graph outputs into a common schema; evaluate_layout_geometry.py for layout_iou, depth_error, chamfer_distance, and object_3d_iou; evaluate_relations_physics.py for collision_rate, support_relation_accuracy, object_relation_accuracy, and out_of_room_rate; evaluate_occlusion_uncertainty.py for occlusion_consistency, hidden-object calibration, and confidence calibration; run_negative_controls.py to submit randomized, image-only, overconfident, and empty-room controls through the same adapters
depth_error; layout_iou; object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; occlusion_consistency; visible_object_recall; novel_view_consistency; confidence_calibration
Evaluate with and without supplied camera intrinsics to quantify calibration dependence; Evaluate visible regions separately from occluded regions; Score single best completion versus top-K uncertain hypotheses when a method provides multiple completions; Compare mesh-based, NeRF-based, Gaussian-style, pointmap, and scene-graph-only outputs through the same adapter; Remove physics and relation checks to show whether image and depth metrics alone miss implausible scenes
Submit ground-truth layout with randomized objects to expose relation and collision metric sensitivity; Submit visually plausible 2D inpainted panoramas with no valid 3D geometry to test geometry gates; Submit overconfident hidden-object predictions on ambiguous rooms to test calibration penalties; Submit empty-room completions to test visible_object_recall and object_3d_iou; Submit shuffled camera intrinsics to test whether methods and adapters depend on correct single-view geometry
Benchmark ranks ground-truth scenes best on at least 90% of geometry and relation metrics; Physics and relation metrics assign worse scores to randomized-object negative controls than to valid ground truth in at least 85% of benchmark scenes; Image-only or panorama-only controls must not score highly on depth_error, chamfer_distance, object_3d_iou, or novel_view_consistency without valid 3D geometry; Top-K uncertainty scoring rewards calibrated ambiguous completions over overconfident single completions on hidden regions according to confidence_calibration and occlusion_consistency; At least three direct baselines can be run end-to-end and exported into the common schema under the single-RGB protocol

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:nerfvs_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:dust3r_2023; seed:mast3r_2024; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: automatic evaluation may still miss human notions of plausibility. Fallback: report separate geometry, relation, image-alignment, occlusion, and calibration axes instead of a single leaderboard score, and include curated failure-case subsets for manual review while keeping all quantitative metrics reproducible.

### Candidate B

Idea 1
Title:
Uncertainty-Aware Occluded Floorplan Completion for Single-Image Indoor 3D Scenes

Core proposal:
Add a probabilistic occluded-layout completion module that operates after visible-scene parsing. The module predicts a distribution over hidden wall continuations, floor extents, doorway openings, support surfaces, and potentially hidden objects conditioned on visible layout lines, monocular depth, object detections, masks, and camera intrinsics. It samples a small set of scene-graph hypotheses, then ranks or rejects them using explicit geometric checks for room containment, support, collision, visibility consistency, and agreement with the visible depth and masks.

Motivation or baseline weakness:
Single-image indoor 3D scene methods can align visible objects and walls to the input view but often commit to one hidden-room completion. This causes overconfident hallucinations in occluded regions, out-of-room placements, unsupported objects, and layouts that do not preserve free space implied by the visible image.

Mechanism or approach:
A scene-graph-level hidden-layout sampler plus validator. The sampler outputs distributions over occluded wall segments, floor polygons, support planes, and optional hidden object slots. The validator scores each sampled scene graph with deterministic checks for collision, object support, line-of-sight consistency, out-of-room placement, and visible-view reprojection. It does not require training a full image-to-3D generator from scratch.
Optimize a weighted objective with four terms: visible-view agreement for depth, masks, and layout; physical validity penalties for collisions, unsupported objects, and out-of-room geometry; diversity or coverage regularization across plausible hidden completions; and calibration loss so predicted confidence matches empirical correctness on held-out synthetic or annotated ambiguity cases. At inference, return a ranked hypothesis set plus per-region uncertainty instead of a single hidden completion.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; layout_estimation_baselines; monocular_depth_estimation; DUSt3R; MASt3R
single RGB indoor image; camera intrinsics when available or estimated focal length; visible object detections and instance masks; monocular depth prediction; visible room layout cues such as wall-floor boundaries and vanishing lines; synthetic indoor scenes rendered from single views with known hidden layout and object support relations; real scanned indoor scenes with single-view evaluation splits
single_view_preprocess_depth_detection_layout.py; sample_occluded_scene_hypotheses.py; score_visibility_and_geometry_consistency.py; validate_physics_geometry.py; export_scene_graph_and_proxy_meshes.py; evaluate_layout_object_uncertainty.py; render_preview_views.py
layout_iou; depth_error; object_3d_iou; collision_rate; out_of_room_rate; support_relation_accuracy; object_relation_accuracy; occlusion_consistency; visible_object_recall; confidence_calibration; ambiguity_detection; failure_detection_auc
replace probabilistic hidden-layout sampler with deterministic layout completion; remove physical consistency validator; remove visibility-consistency scoring; remove support-relation constraints; use depth only without object and layout cues; use only the top-1 hypothesis instead of an uncertainty-weighted hypothesis set; calibrate confidence with temperature scaling versus no calibration
sample hidden walls and objects uniformly without conditioning on the visible scene; rank hypotheses only by image-text or image similarity without geometry checks; force a fixed rectangular room prior for all images; report constant confidence for all hidden regions; shuffle visible object detections across images before sampling hidden completions
reduce out_of_room_rate by at least 25% relative to the strongest direct baseline on the same split; reduce collision_rate by at least 20% without lowering visible_object_recall by more than 5%; improve occlusion_consistency by at least 15% on held-out hidden-region annotations; improve failure_detection_auc by at least 0.08 over uncalibrated baseline confidence; maintain or improve layout_iou relative to a deterministic layout completion baseline

Risks, controls, or fallback:
Risk: hidden-region ground truth is inherently ambiguous, and priors learned from synthetic scenes may not transfer to real scans. Fallback: evaluate completions as a set-prediction problem using coverage-versus-plausibility curves, and allow the system to output conservative free-space and support estimates with explicit uncertainty warnings when a confident hidden completion is not justified.

---

Idea 2
Title:
Constraint-Projected Object Proxy Meshes for Geometry-Consistent Renderable Indoor Scenes

Core proposal:
Insert a constraint-projection stage between initial scene estimation and final rendering. Detected objects are initialized as category-conditioned proxy meshes, cuboids, or retrieved assets. Their scale, pose, and support assignments are then optimized against the input masks, monocular depth, estimated room layout, camera intrinsics, category size priors, and explicit scene-graph constraints. The stage outputs adjusted object transforms, support relations, and a renderable proxy scene that can either replace or guide the baseline geometry.

Motivation or baseline weakness:
Image-to-3D indoor scene baselines may produce visually plausible renderings while failing at metric scene consistency. Common errors include floating furniture, object interpenetration, implausible object scale, objects crossing walls, support-relation violations, and disagreement between rendered geometry and the input-view depth or object masks.

Mechanism or approach:
A lightweight pose-scale optimizer over object proxies. It includes differentiable or subdifferentiable penalties for depth reprojection, mask coverage, silhouette alignment, floor or wall support, object-object collision, room-boundary containment, category size plausibility, and relative spatial relations. Object shapes can be simple parametric proxies for all categories, with optional retrieved assets when available.
Minimize a weighted scene energy over object pose, scale, orientation, support plane, and optional asset choice. The energy combines input-view reprojection loss, monocular depth consistency, mask/silhouette loss, category size prior, support-relation penalty, collision penalty, room containment penalty, and a regularizer that keeps transforms near the initialization. Uncertainty is estimated from multi-start variance, local optimizer curvature, or disagreement between similarly scored solutions.

Experiment and implementation plan:
single_image_to_3d_scene_generation_baselines; Text2Room; SceneScape; Indoor_NeRF_prior_methods; 3D Gaussian Splatting; NeRF; monocular_depth_estimation
single RGB indoor image; object detections, masks, and category labels; monocular depth map; estimated room layout with floor and wall planes; camera intrinsics if available or estimated focal length; category proxy meshes, cuboids, or retrieved indoor object assets; indoor datasets with object-level 3D annotations or scene-level mesh annotations for evaluation
detect_objects_and_layout.py; initialize_object_proxies.py; optimize_scene_constraints.py; check_collision_support_room_bounds.py; render_scene_preview.py; evaluate_proxy_scene_geometry.py
depth_error; object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; visible_object_recall; image_reconstruction_lpips; novel_view_consistency; object_count_accuracy; confidence_calibration
remove collision penalty; remove support penalty; remove room containment penalty; remove category size prior; replace category proxy meshes with 3D boxes only; use single initialization instead of multi-start optimization; remove monocular depth term; remove mask reprojection term
randomly place retrieved assets within the estimated room; optimize only perceptual render similarity without geometric constraints; use correct object categories but random object scales; apply the constraint projector to shuffled object detections from another image; disable the room layout estimate and allow objects to optimize in unconstrained 3D space
reduce collision_rate by at least 30% compared with the best direct baseline; improve support_relation_accuracy by at least 15%; improve object_3d_iou by at least 10% on datasets with object-level 3D annotations; keep image_reconstruction_lpips within 5% of the unconstrained rendering baseline; achieve lower out_of_room_rate without reducing visible_object_recall by more than 5%

Risks, controls, or fallback:
Risk: simple proxy meshes may improve physical metrics while reducing visual fidelity for complex furniture and clutter. Fallback: use the optimized proxies for collision checking, planning, and geometric evaluation while preserving baseline-generated textured geometry for final rendering. When proxy-to-image fit is poor, expose an uncertainty flag rather than forcing an apparently precise object pose.

---

Idea 3
Title:
Failure-Calibrated Scene Graph Generation with Explicit Ambiguity Warnings

Core proposal:
Add a failure-calibrated scene-graph head that predicts confidence and warning labels for each layout element, object instance, spatial relation, support relation, material or texture assignment, and occluded-region hypothesis. The head does not generate new geometry. It aggregates disagreement across existing depth, detection, layout, and scene-generation outputs, plus explicit validator residuals such as collision, support violation, room containment violation, mask mismatch, and depth reprojection error.

Motivation or baseline weakness:
Single-image 3D scene generators usually return a complete scene graph or renderable scene even when the input is underconstrained. Downstream systems may therefore treat hallucinated room extents, uncertain object identities, invalid supports, and occluded geometry as reliable, leading to unsafe planning and misleading evaluation.

Mechanism or approach:
A small uncertainty aggregator over existing model outputs. It computes per-field features from model confidence, test-time perturbation variance, cross-model disagreement, object visibility fraction, occlusion status, geometry-validator violations, and render-reprojection residuals. It outputs calibrated per-field confidence, binary warning labels, and optional scene-level risk summaries.
Train the aggregator to predict whether each scene-graph field will pass downstream semantic and geometric checks. Targets are derived from annotated indoor scenes, held-out reconstructed scenes, and synthetic corruptions that introduce controlled failures such as collisions, wrong supports, missing objects, swapped categories, invalid room extents, and impossible hidden regions. Optimize calibration loss, binary failure classification loss, and ranking loss that prioritizes severe failures above minor visual mismatches.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; layout_estimation_baselines; monocular_depth_estimation; DUSt3R; MASt3R; object_detector; scene_graph_evaluator
single RGB indoor images; baseline-generated renderable scenes or scene graphs; multiple depth, layout, object, or scene predictions from independent models or test-time perturbations; ground-truth or pseudo-ground-truth layout, object, and relation annotations from indoor scene datasets; synthetic corruptions for collisions, wrong supports, missing objects, swapped categories, impossible hidden regions, and out-of-room geometry
run_baseline_scene_generators.py; extract_disagreement_and_validator_features.py; generate_scene_graph_failure_labels.py; train_confidence_aggregator.py; evaluate_calibration_and_downstream_use.py; export_warnings_in_scene_format.py
confidence_calibration; failure_detection_auc; ambiguity_detection; occlusion_consistency; visible_object_recall; object_count_accuracy; support_relation_accuracy; object_relation_accuracy; collision_rate; out_of_room_rate; navigation_success_rate; embodied_task_success_rate
use only raw model confidence without geometry-validator features; use only geometry-validator features without model-disagreement features; remove occlusion-specific features; train on real annotations only versus synthetic corruptions plus real annotations; predict scene-level confidence only versus per-field confidence; downstream planner with warnings versus planner ignoring warnings
assign random confidence scores; assign confidence proportional only to object detector score; mark all occluded regions as low confidence regardless of visible evidence; train the failure predictor on shuffled correctness labels; evaluate warnings without allowing downstream scene consumers to avoid or replan around warned fields; use only scene-level pass or fail labels while reporting per-field confidence
improve failure_detection_auc by at least 0.10 over raw baseline confidence; reduce expected calibration error by at least 25%; identify at least 70% of severe collision or out-of-room failures at a 20% warning rate; improve downstream navigation_success_rate or embodied_task_success_rate by at least 5% when uncertain fields are avoided or replanned; preserve visible_object_recall within 3% of the underlying scene generator

Risks, controls, or fallback:
Risk: the confidence predictor may learn dataset-specific artifacts rather than true ambiguity, and downstream gains may be limited if planners cannot use uncertainty. Fallback: report per-error-type calibration, evaluate cross-domain transfer, and expose warnings as conservative masks over unsafe geometry and unreliable occluded regions so downstream systems can ignore or replan around high-risk fields.

---

## Item 6: HUM-8fd147876f

类型：`portfolio`

### Candidate A

Idea 1
Title:
Layout-Anchored Single-Image Scene Completion with Uncertain Hidden Volumes

Core proposal:
Add a layout-anchored probabilistic volumetric scene graph on top of a single-image generated mesh. The module estimates a Manhattan-style room envelope and monocular depth from the input image, anchors visible objects to reprojection and depth evidence, then samples multiple occluded-volume and support-relation hypotheses constrained to remain inside the room and physically plausible.

Motivation or baseline weakness:
Text2Room and SceneScape can produce visually plausible room meshes from image/text-conditioned generation and depth fusion, but hidden furniture, wall continuations, and floor geometry can drift outside a consistent room layout. They also tend to return one completion without calibrated confidence for occluded regions where many completions are plausible.

Mechanism or approach:
A post-generation constraint-and-uncertainty layer that consumes the baseline mesh, monocular depth, visible object detections, and room layout estimate. It represents hidden space as coarse occupancy cells plus object hypotheses, samples candidates for occluded floor/wall regions, and rejects or downweights samples with wall penetration, floor penetration, unsupported objects, excessive inter-object collision, or contradiction with visible depth.
Maximize visible-image consistency through depth and reprojection agreement while minimizing layout violation, object collision, unsupported-object penalties, and relation inconsistency. The output is a calibrated distribution over occluded occupancy and object/layout completions, plus a deterministic MAP scene for standard mesh metrics.

Experiment and implementation plan:
Text2Room; SceneScape; layout_estimation_baselines; monocular_depth_estimation
Structured3D single-view renders with room layout, object instances, depth, and camera metadata; 3D-FRONT rooms rendered to single RGB views with held-out hidden objects and known layout/object annotations; A real-image stress subset using the same standardized annotation fields where available; otherwise use it only for qualitative failure analysis
run_text2room_or_scenescape_single_image_baseline.py; estimate_layout_and_depth.py; detect_visible_objects.py; sample_occluded_scene_graph.py; check_physics_and_layout_constraints.py; evaluate_scene_completion_metrics.py
layout_iou; depth_error; object_3d_iou; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; occlusion_consistency; visible_object_recall; confidence_calibration
Remove room-layout containment and keep only monocular depth fusion; Use a single MAP hidden-scene completion instead of probabilistic hidden-volume hypotheses; Remove support-relation penalties for objects on floors, tables, and shelves; Replace detector-conditioned visible object anchoring with category priors only; Disable collision rejection during occluded object sampling
Evaluate on images with intentionally corrupted camera intrinsics and require confidence_calibration to worsen or uncertainty to increase rather than silently producing confident completions; Use random room boxes with correct object detections to confirm layout anchoring, not object priors alone, drives out_of_room_rate and layout_iou gains; Shuffle object category priors across rooms to test whether support_relation_accuracy and object_relation_accuracy degrade as expected; Replace estimated depth with spatially shuffled depth while keeping the RGB image fixed to verify visible-object anchoring fails gracefully
Reduce out_of_room_rate by at least 30% relative to Text2Room or SceneScape on Structured3D/3D-FRONT renders; Reduce collision_rate by at least 20% without reducing visible_object_recall by more than 5%; Improve support_relation_accuracy by at least 10 percentage points over the unconstrained generated-mesh baseline; Achieve lower expected calibration error for occluded-region occupancy confidence than deterministic or uncalibrated baselines; Maintain layout_iou within 5% of the layout_estimation_baselines when adding hidden-volume hypotheses

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: layout estimation from narrow-FOV RGB images may be unreliable, making hard constraints harmful. Fallback: use confidence-weighted soft wall, floor, and ceiling penalties; when layout confidence is low, widen the posterior over hidden volumes and report low confidence rather than forcing a brittle room box.

---

Idea 2
Title:
Relation-First Object Proxy Reconstruction for Renderable Indoor Scene Graphs

Core proposal:
Convert the single image into an object-centric scene graph with cuboids or retrieved proxy meshes, then optimize object scale, pose, room containment, and support relations before any texture transfer or inpainting. DUSt3R/MASt3R-style geometry is used only when valid image collections or generated auxiliary views are available; the core single-image path relies on monocular depth, masks, layout, and 3D-FRONT/3D-FUTURE size/support priors.

Motivation or baseline weakness:
Single-image scene generators and image-to-3D baselines can preserve the input-view appearance but often lack object-level 3D proxies that satisfy stable spatial relations such as on, against, inside, left-of, and in-front-of. This limits geometric evaluation, editing, and embodied use even when preview renderings look plausible.

Mechanism or approach:
A differentiable or search-based object proxy optimizer that initializes object cuboids from 2D detections, masks, monocular depth, and layout. It assigns candidate support surfaces, retrieves category-compatible proxy meshes when available, and adjusts 3D positions, scale, and yaw to satisfy relation constraints while preserving visible reprojection alignment.
Minimize a weighted objective combining 2D mask reprojection error, depth consistency, room-layout containment, pairwise collision penalties, support-surface distance, and relation-class penalties. Texture generation or view inpainting is applied only after proxy geometry passes collision, containment, and support checks.

Experiment and implementation plan:
image_to_3d_generation_baselines; Text2Room; WonderJourney; DUSt3R; MASt3R; 3D Gaussian Splatting
3D-FRONT and 3D-FUTURE for object categories, proxy meshes, sizes, and support priors; Structured3D for rendered single-view layout and depth supervision; A held-out rendered single-view split with ground-truth 3D boxes, support relations, and visible masks; Optional real indoor images used only when the same visible-object and relation annotations can be standardized
extract_2d_instances_and_masks.py; estimate_single_view_depth_or_pointmap.py; initialize_object_proxies.py; optimize_scene_graph_relations.py; retrieve_or_fit_proxy_meshes.py; render_scene_preview.py; evaluate_object_relation_metrics.py
object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; visible_object_recall; novel_view_consistency; depth_error; layout_iou
Use direct Text2Room-style mesh fusion without object proxy optimization; Optimize object poses without support-relation terms; Optimize support relations without collision penalties; Use cuboids only versus retrieved 3D-FUTURE proxy meshes; Run texture generation before versus after relation-consistent proxy fitting; Remove room-layout containment while keeping object relation terms
Randomize support-surface assignments while keeping object detections fixed; Use depth estimates with shuffled or incorrect scale to test metric-scale sensitivity; Evaluate on rendered scenes with transparent, reflective, or very thin support surfaces where proxy assumptions should be uncertain; Randomly rotate retrieved proxy meshes within each object category to confirm relation and reprojection metrics detect implausible fits
Improve support_relation_accuracy by at least 15 percentage points over image-to-3D generation baselines; Reduce collision_rate by at least 25% relative to Text2Room or WonderJourney outputs converted to meshes; Improve object_3d_iou by at least 10% on visible major furniture categories in 3D-FRONT renders; Maintain visible_object_recall within 5% of the best direct baseline; Improve novel_view_consistency without increasing out_of_room_rate relative to unconstrained mesh generation

Evidence paper IDs:
seed:text2room_2023; seed:wonderjourney_2023; seed:dust3r_2023; seed:mast3r_2024; seed:3dgs_2023; seed:3dfront_2020; seed:3dfuture_2020; seed:structured3d_2019; seed:midas_2023

Risks, controls, or fallback:
Risk: object detectors and masks may miss heavily occluded or small objects, causing incomplete scene graphs. Fallback: optimize and report major furniture separately from small clutter, keep an uncertain residual occupancy layer for low-confidence regions, and expose low visible_object_recall or mask confidence through confidence_calibration rather than hallucinating precise proxies.

---

Idea 3
Title:
Self-Diagnosing Single-Image 3D Scene Benchmark with Ambiguity-Aware Metrics

Core proposal:
Construct a benchmark protocol that renders many single RGB views from known 3D indoor scenes, hides non-visible ground truth during generation, and scores methods with visible-region geometry metrics plus occluded-region calibration and plausibility checks. Methods may submit meshes, radiance fields, Gaussian splats, or scene graphs, but all submissions must be converted to a minimal common format for core evaluation.

Motivation or baseline weakness:
Existing single-image 3D scene generation evaluations often emphasize rendered preview quality or visible depth, but under-measure ambiguity, occluded-region uncertainty, physical plausibility, relation consistency, and whether a generated scene remains valid when converted into a common 3D representation.

Mechanism or approach:
An evaluation harness that computes visible evidence alignment, hidden-region distributional coverage, scene graph relation correctness, collision/layout violations, uncertainty calibration, and novel-view consistency from a submitted renderable scene or scene graph. The harness records confidence maps or hypothesis weights for ambiguous hidden regions instead of forcing all methods into a single deterministic hidden-scene target.
For each input image, evaluate whether the method produces a renderable scene that matches visible depth/layout/object evidence, assigns calibrated confidence to occluded objects and geometry, avoids physically impossible layouts, and maintains consistency under held-out novel-view rendering.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; Indoor_NeRF_prior_methods; layout_estimation_baselines; monocular_depth_estimation; NeRF; 3D Gaussian Splatting
Structured3D single-view benchmark split with ground-truth layout, depth, object instances, and occlusion masks; 3D-FRONT/3D-FUTURE rendered benchmark split with furniture meshes, object categories, layouts, and material annotations; A synthetic domain-shift split rendered from the same supplied indoor assets with altered lighting, clutter, and camera poses; A small manually checked stress split for corrupted intrinsics, extreme occlusion, reflective surfaces, and missing floor-wall boundaries
render_single_view_benchmark_images.py; compute_visibility_and_occlusion_masks.py; standardize_scene_submission_format.py; evaluate_geometry_and_layout.py; evaluate_scene_graph_relations.py; evaluate_uncertainty_calibration.py; run_collision_checks.py; generate_failure_case_report.py
depth_error; layout_iou; object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; occlusion_consistency; visible_object_recall; novel_view_consistency; confidence_calibration
Score only visible-region geometry versus visible plus occluded-region uncertainty; Use preview-only novel_view_consistency versus full geometric and relation metrics; Remove collision and out-of-room checks from the benchmark score; Treat hidden regions as a single ground truth only versus accepting calibrated multiple hypotheses; Evaluate with and without the synthetic domain-shift stress split
Submit ground-truth visible depth with random hidden geometry to verify occlusion_consistency and confidence_calibration catch implausible completions; Submit visually plausible 2D inpainted previews with no valid 3D object positions to verify object_3d_iou, support_relation_accuracy, and collision_rate expose the failure; Submit overconfident deterministic completions for highly ambiguous views to verify confidence_calibration penalties increase; Submit scenes with all objects inside the room but floating to verify support_relation_accuracy catches the error; Submit valid object proxies with randomized textures to confirm core geometry and relation metrics remain separated from appearance-only effects
Benchmark ranking must separate physically invalid but visually plausible outputs from relation-consistent outputs using collision_rate, support_relation_accuracy, and out_of_room_rate; Confidence_calibration must penalize overconfident hidden-region predictions more than calibrated multi-hypothesis predictions; Occlusion_consistency must decrease for random hidden geometry even when visible depth_error is near optimal; At least three direct baselines must run end-to-end and produce comparable standardized scene submissions; Metric reports must include per-category failure cases for layout, object geometry, relations, occlusion, and novel-view consistency

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:nerf_2020; seed:nerfvs_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:3dgs_2023; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: automatic scene plausibility scoring may be noisy and unfair across mesh, NeRF, Gaussian, and scene-graph outputs. Fallback: require conversion to a minimal common format containing layout, object proxies, render previews, occupancy samples, and confidence maps, while reporting representation-specific metrics separately from the core scene-consistency score.

### Candidate B

Idea 1
Title:
Uncertainty-Aware Occluded Room Completion via Multi-Hypothesis Scene Graph Sampling

Core proposal:
Add an occlusion-conditioned probabilistic scene-graph sampler that explicitly separates visible evidence, unobserved free space, and occluded support surfaces. The sampler first builds a visible-room graph from detected objects, estimated layout planes, depth-derived free space, and occlusion masks, then predicts K discrete hidden-scene hypotheses containing object categories, coarse 3D boxes, support relations, room-zone assignments, and confidence weights. Each hypothesis is checked against visibility constraints so predicted hidden objects do not project into clearly visible empty regions, and is instantiated with proxy geometry or retrieved assets only after graph-level sampling.

Motivation or baseline weakness:
Single-image-to-3D-scene baselines can produce one plausible hidden-room completion but often treat occluded regions as deterministic, causing overconfident hallucinations, missed hidden objects, and poor failure signaling when the image is genuinely ambiguous.

Mechanism or approach:
A small probabilistic scene-graph head with three outputs: hidden occupancy over room zones, categorical object proposals with oriented 3D boxes, and hypothesis-level confidence weights. Inputs are visible detections, monocular depth, estimated room layout, camera intrinsics if available, and occlusion masks; outputs are K weighted hidden-scene graphs plus a calibrated abstention score for highly ambiguous cases.
Train the sampler to maximize likelihood of held-out hidden scene graphs under synthetic single-view occlusion splits while preserving consistency with visible evidence. The loss combines hidden-object category and box likelihood, support-relation likelihood, visibility exclusion penalties for objects that would be visible but are not detected, collision and out-of-room penalties, and a calibration term that discourages high confidence when multiple hidden completions are compatible with the same input.

Experiment and implementation plan:
single deterministic hidden-scene completion; dataset-prior hidden-object sampler; monocular depth plus layout plus asset retrieval; single-image renderable scene generation baseline; single-view point-cloud or correspondence initialized scene completion
single RGB indoor image; camera intrinsics if available; visible object detections; monocular depth map; estimated room layout; occlusion masks derived from depth discontinuities and layout visibility; synthetic single-view projections with full 3D scene graph supervision from indoor 3D scene datasets
generate_single_view_occlusion_splits.py; estimate_depth_layout_objects.py; build_visible_room_graph.py; sample_occluded_scene_graphs.py; instantiate_proxy_mesh_scene.py; evaluate_hidden_scene_hypotheses.py; render_novel_view_previews.py
visible_object_recall; hidden_object_recall; hidden_object_false_positive_rate; object_count_accuracy; layout_iou; object_3d_iou_visible; object_3d_iou_hidden; support_relation_accuracy; object_relation_accuracy; collision_rate; out_of_room_rate; visibility_violation_rate; occlusion_consistency; confidence_calibration; ambiguity_detection; failure_detection_auc
single deterministic hidden-scene prediction instead of K hypotheses; remove confidence calibration term; remove visibility exclusion penalty; remove physics and support-relation penalties; condition sampler only on RGB without depth; condition sampler only on layout without visible object graph; vary number of hypotheses K
sample hidden objects from dataset priors without conditioning on the input image; assign uniform confidence to all hypotheses; place occluded objects randomly in estimated hidden free space while preserving object category histogram; predict hidden objects only from room type while ignoring visible object detections and occlusion masks
reduce hidden-object false-positive rate by at least 15 percent at matched hidden-object recall versus deterministic completion; improve expected calibration error for hidden-region confidence by at least 20 percent; reduce visibility_violation_rate by at least 20 percent versus an unconditioned hidden-object sampler; reduce collision_rate and out_of_room_rate by at least 10 percent without lowering visible_object_recall; achieve higher failure_detection_auc than confidence derived from image reconstruction error alone

Risks, controls, or fallback:
Risk: hidden regions may be too ambiguous for reliable category-level prediction. Fallback: predict occupancy, support surfaces, and coarse object groups instead of fine categories when entropy is high, and emit an explicit failure or abstention signal rather than a confident hidden-object claim.

---

Idea 2
Title:
Geometry-Consistent Single-Image Scene Generation with Differentiable Contact and Visibility Repair

Core proposal:
Insert a post-generation differentiable repair stage that adjusts an already generated scene rather than creating new content. The stage converts generated objects and room structure into proxy boxes or coarse meshes, estimates which parts should be visible from the input camera, and optimizes object translation, yaw, scale, and layout plane offsets under contact, collision, containment, visibility, and depth-preservation constraints. Object identity, instance count, and approximate image-plane location are fixed unless a constraint conflict is detected.

Motivation or baseline weakness:
Image-to-3D scene generation baselines may align visually with the input view but produce geometrically invalid scenes, including floating furniture, wall penetrations, object collisions, and objects placed outside the inferred room.

Mechanism or approach:
A scene-constraint optimizer operating on proxy boxes, coarse meshes, layout planes, monocular depth, object masks, camera projection, and the initial generated scene graph. It exposes confidence weights for noisy masks and depth, supports frozen variables for high-confidence objects, and returns both a repaired scene and residual constraint violations.
Minimize a weighted energy with terms for projected mask alignment, visible-region depth agreement, floor or support contact, inter-object collision avoidance, in-room containment, wall clearance, visibility preservation, and relation preservation. The optimization is constrained so repairs cannot improve physical plausibility by deleting difficult objects, changing object categories, or moving visible objects far from their projected masks.

Experiment and implementation plan:
unoptimized generated scene; random-pose repair with matched displacement magnitude; image-reprojection-only pose refinement; monocular depth plus layout plus asset retrieval; single-image renderable scene generation baseline; single-view neural reconstruction baseline
single RGB indoor image; camera intrinsics if available; object masks and detections; monocular depth map; estimated room layout planes; initial generated scene from a baseline; proxy meshes or oriented bounding boxes for object instances; optional full 3D ground truth for evaluation only
run_baseline_scene_generation.py; extract_proxy_scene_graph.py; estimate_visibility_from_camera.py; optimize_contact_visibility_constraints.py; check_physics_collisions.py; render_before_after_previews.py; evaluate_geometry_repair.py
depth_error_visible_regions; layout_iou; object_3d_iou; chamfer_distance_where_ground_truth_exists; collision_rate; out_of_room_rate; floating_object_rate; support_relation_accuracy; object_relation_accuracy; visible_object_recall; mask_projection_iou; image_reconstruction_lpips; novel_view_consistency; constraint_residual_rate
remove contact and support terms; remove collision penalties; remove in-room containment and wall-clearance terms; remove projected mask and depth preservation terms; optimize layout only; optimize objects only; use axis-aligned boxes instead of oriented boxes or proxy meshes; allow object deletion to test whether gains come from invalid simplification
randomly jitter object poses with the same average displacement as the optimizer; apply only global scene scaling and translation; optimize for image reprojection only without physical constraints; run the optimizer with shuffled object masks so object identity and image evidence are mismatched
reduce collision_rate by at least 25 percent relative to the unoptimized generated scene; reduce out_of_room_rate by at least 20 percent; reduce floating_object_rate by at least 20 percent; improve support_relation_accuracy by at least 10 percent; increase image_reconstruction_lpips by no more than 5 percent relative to the original baseline rendering; maintain at least 95 percent of baseline visible_object_recall

Risks, controls, or fallback:
Risk: monocular depth, masks, and layout estimates may be noisy, causing the optimizer to satisfy incorrect constraints. Fallback: use robust losses, confidence-weighted depth and mask terms, limit maximum pose changes for high-confidence visible objects, and emit a failure warning when optimized residuals remain high or constraints conflict.

---

Idea 3
Title:
Benchmark for Single-Image Indoor Scene Completion with Failure-Aware Renderable Outputs

Core proposal:
Construct a controlled benchmark by rendering single-view RGB inputs from complete indoor 3D scenes, hiding ground-truth scene information during prediction, and evaluating submitted renderable scenes through a common intermediate representation. The benchmark converts each output into visible objects, hidden objects, layout geometry, support relations, proxy meshes or boxes, confidence values, and failure flags, then reports separate scores for visible reconstruction, hidden-scene plausibility, physical validity, uncertainty calibration, and downstream task utility.

Motivation or baseline weakness:
Existing evaluations for single-image indoor 3D scene generation can overemphasize image similarity or qualitative plausibility and under-measure scene-level consistency, uncertainty over occluded regions, physical validity, and downstream usability.

Mechanism or approach:
A benchmark harness that standardizes camera sampling, visibility labeling, occlusion severity bins, output normalization to a common scene graph plus proxy geometry format, metric computation, and automatic failure-case tagging. It includes adapters for methods that output meshes, point clouds, neural renderers, object graphs, or multi-hypothesis scenes.
Measure whether a method recovers visible scene content, produces plausible and calibrated hidden-region hypotheses, satisfies physical and spatial constraints, and remains useful for downstream navigation or embodied planning from a single RGB input. The benchmark avoids treating a single hidden ground truth as the only valid answer by separating deterministic visible-region metrics from probabilistic or set-based hidden-region metrics.

Experiment and implementation plan:
ground-truth visible scene with randomized hidden content; correct object categories with randomized 3D positions; render-only output scored with image metrics alone; constant-confidence single-hypothesis output; monocular depth plus layout baseline; single-image renderable scene generation baseline; single-view neural reconstruction baseline
complete indoor 3D scenes with object-level geometry where available; single RGB render per test case; camera intrinsics; held-out full scene geometry; held-out scene graph annotations where available; visibility masks for visible and hidden objects; room layout annotations or derived layout planes; occlusion severity labels
sample_single_view_benchmark_cameras.py; label_visible_hidden_objects.py; normalize_scene_outputs_to_common_format.py; compute_geometry_metrics.py; compute_scene_graph_metrics.py; compute_uncertainty_metrics.py; run_physics_collision_checker.py; run_navigation_proxy_tasks.py; generate_failure_case_report.py
depth_error_visible; layout_iou; object_3d_iou_visible; object_3d_iou_hidden; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; floating_object_rate; visibility_violation_rate; occlusion_consistency; visible_object_recall; novel_view_consistency; image_reconstruction_lpips; object_count_accuracy; confidence_calibration; ambiguity_detection; failure_detection_auc; navigation_success_rate
evaluate with visible-region metrics only versus full benchmark; remove hidden-object and occlusion-consistency scoring; remove physics and collision checks; remove uncertainty calibration metrics; compare category-level proxy geometry scoring versus mesh-level scoring; vary camera viewpoint ambiguity and occlusion severity; disable output normalization adapters and score only native renderings
score ground-truth visible objects with randomized hidden objects; score scenes with correct object categories but randomized 3D positions; score render-only outputs without a scene graph using image metrics alone; score overconfident single-hypothesis predictions as if uncertainty were unavailable; score scenes with shuffled confidence values to test calibration sensitivity
benchmark separates ground-truth scenes from randomized-position controls by at least 30 points on normalized consistency score; hidden-object randomization reduces occlusion_consistency and relation accuracy by at least 20 percent; methods with identical image LPIPS but different collision rates receive measurably different physical plausibility scores; failure_detection_auc improves when models provide calibrated confidence rather than constant confidence; visible-region scores remain stable when hidden-region annotations are withheld from the method

Risks, controls, or fallback:
Risk: automatic metrics may penalize plausible alternatives to the ground truth in genuinely ambiguous hidden regions. Fallback: report visible-region deterministic scores separately from hidden-region probabilistic scores, use occlusion-severity-stratified leaderboards, accept multiple hypotheses where methods provide them, and mark highly ambiguous cases so they do not dominate deterministic hidden-object rankings.

---

## Item 7: HUM-69e55f3a47

类型：`portfolio`

### Candidate A

Idea 1
Title:
Uncertainty-Aware Occluded Room Completion for Single-Image Indoor Scene Generation

Core proposal:
Add an occlusion-aware multi-hypothesis completion layer after monocular depth, layout, object detection, and initial scene lifting. The layer first builds a camera-space visibility map that separates visible free space, visible occupied space, occluded in-frustum space, and out-of-view space. It then samples a small set of hidden layout and object hypotheses only inside feasible occluded or out-of-view regions. Each hypothesis is filtered or reweighted by explicit constraints: consistency with visible depth, room-plane continuation, floor/wall support, object category-size priors, camera frustum visibility, inter-object collision, and room containment. The output is a renderable scene graph containing visible objects, K alternative hidden completions, per-region hypothesis probabilities, and a failure_warning score when the posterior is diffuse or constraints cannot be satisfied.

Motivation or baseline weakness:
Single-image-to-3D-room systems can generate a plausible room from the visible image but usually commit to one hidden completion. This makes them overconfident about unobserved walls, floor regions, and furniture behind occluders, and it weakens failure detection when the input image underconstrains the room.

Mechanism or approach:
A probabilistic occluded-region hypothesis module that takes estimated depth, layout planes, object detections, camera intrinsics, and visible/occluded masks, then returns K physically feasible hidden-room and hidden-object completions with calibrated confidence scores.
Train or tune the module to minimize visible evidence violations while preserving uncertainty over genuinely ambiguous hidden regions. Use an objective of the form L = L_visible_depth + L_layout_boundary + L_visible_object_reprojection + lambda_collision L_collision + lambda_support L_support + lambda_containment L_containment + lambda_cal L_calibration - lambda_div L_valid_diversity. The diversity term is applied only among valid hidden hypotheses, not visible objects. Calibration is computed on synthetic or fully scanned scenes by comparing predicted hidden-region probabilities against held-out 3D occupancy, layout, and object presence labels.

Experiment and implementation plan:
deterministic single-image room reconstruction; single-image scene graph lifting without hidden uncertainty; monocular depth plus layout plus object detector lifting; image-conditioned generative room completion; retrieval-based furniture completion conditioned on visible objects
synthetic furnished indoor scenes with RGB views, camera intrinsics, full room layout, object geometry, and object categories; scanned indoor scenes with RGB-D or reconstructed geometry for real-domain evaluation; single-view train, validation, and test splits with held-out full 3D ground truth; rendered ambiguous views including narrow field-of-view, cropped, occluded, and corner-facing images
single_view_preprocessing.py for depth estimation, layout estimation, object detection, camera normalization, and visibility labeling; occluded_hypothesis_sampler.py for generating constrained hidden layout and object hypotheses; hypothesis_scoring.py for constraint costs, confidence normalization, valid-hypothesis diversity, and failure_warning estimation; scene_graph_exporter.py for exporting visible scene content plus K hidden completions into a common renderable format; evaluate_uncertainty_completion.py for visible alignment, hidden-region calibration, physical plausibility, diversity, and failure detection
visible_depth_error; visible_layout_iou; visible_object_3d_iou; visible_object_recall; hidden_occupancy_brier_score; hidden_object_presence_f1; occlusion_consistency; valid_hypothesis_diversity; collision_rate; out_of_room_rate; support_relation_accuracy; object_relation_accuracy; confidence_calibration; failure_detection_auc; novel_view_consistency
output only the highest-probability hidden completion; sample hidden objects without conditioning on visible objects or layout; remove camera-frustum visibility masks; remove collision constraints; remove support and containment constraints; replace calibrated probabilities with unnormalized constraint scores; vary the number of hidden hypotheses from 1 to 3 to 10
sample hidden objects uniformly from dataset category frequencies while preserving the same object count distribution; assign random confidence scores to otherwise valid hidden hypotheses; assign constant confidence scores to all hidden hypotheses; shuffle occlusion masks across images before hypothesis sampling; use deliberately perturbed camera intrinsics during constraint checking; evaluate hidden completions after randomly permuting room layouts across images
reduce collision_rate by at least 20% relative to the strongest deterministic single-image room baseline; improve occlusion_consistency by at least 15% on held-out synthetic or scanned views; reduce hidden-region expected calibration error by at least 25% relative to deterministic or constant-confidence baselines; maintain visible_object_recall within 5% of the best direct baseline; increase failure_detection_auc by at least 0.10 on deliberately ambiguous or corrupted inputs

Risks, controls, or fallback:
Risk: multiple hidden completions may be plausible even when only one appears in the held-out ground truth, so top-1 hidden 3D overlap may underestimate quality. Fallback: report both top-1 and oracle-over-K metrics, emphasize calibration and valid-hypothesis diversity for hidden regions, and start with room layout plus large furniture before extending to fine object geometry.

---

Idea 2
Title:
Constraint-Projected Scene Graph Lifting for Geometrically Consistent Single-Image 3D Rooms

Core proposal:
Insert a post-generation constraint projector that operates on an initial renderable scene graph rather than replacing the generator. The projector parses room planes, object categories, object proxy geometry, poses, scales, and predicted relations. It then solves a constrained correction problem over object translation, yaw, scale, support assignment, and layout plane offsets. Corrections are bounded so that visible image evidence is preserved: projected objects must remain consistent with 2D detections, visible masks, monocular depth, and estimated layout edges. Physical constraints are implemented as differentiable penalties when possible and as discrete search or sequential repair when object support choices or proxy retrieval are non-continuous.

Motivation or baseline weakness:
Single-image 3D room generation and reconstruction pipelines may align locally with the input image while producing scene-level violations: furniture can float, penetrate walls, collide with other objects, sit outside the room, or contradict basic support and spatial relations.

Mechanism or approach:
A physical-consistency projection module that takes an initial single-image scene graph and returns a corrected scene graph with adjusted poses, scales, support assignments, layout planes, and a projection_failure flag when constraints cannot be satisfied without large visible-evidence violations.
Given an initial scene S0, solve S* = argmin_S E(S), where E(S)=E_2d_reprojection + E_visible_depth + E_layout_alignment + E_relation_consistency + alpha E_collision + beta E_support + gamma E_room_containment + delta E_scale_category + eta E_deviation_from_S0. Variables include object center, yaw, scale, proxy mesh or box dimensions, support relation, and layout plane offsets. The deviation term prevents the projector from inventing a new scene instead of repairing the initial one.

Experiment and implementation plan:
unprojected single-image scene generator; monocular depth plus layout plus object detector lifting; scene graph lifting with heuristic floor placement; image-conditioned room completion without physical projection; optimization using only image reconstruction terms
synthetic furnished room scenes with object geometry, room layout, support relations, and camera views; scanned indoor scenes with reconstructed geometry and RGB images for real-domain testing; 2D annotations or detector outputs for visible objects; camera intrinsics or normalized camera assumptions for reprojection constraints
baseline_scene_generation_runner.py for producing initial scene graphs from single RGB inputs; scene_graph_parser.py for extracting room planes, object proxies, poses, categories, detections, and relations; constraint_projection_optimizer.py for continuous pose-scale-layout optimization plus discrete support assignment; projection_diagnostics.py for reporting violated constraints, correction magnitudes, and projection_failure cases; render_compare.py for visible-view and novel-view rendering checks; evaluate_physical_consistency.py for collision, support, containment, relation, and alignment metrics
collision_rate; collision_volume; out_of_room_rate; support_relation_accuracy; floating_object_rate; object_relation_accuracy; layout_iou; visible_depth_error; object_3d_iou; visible_object_recall; image_reconstruction_lpips; mean_pose_correction; projection_failure_rate; novel_view_consistency; navigation_success_rate
projection with collision constraints only; projection with support constraints only; projection with room containment only; projection without the deviation_from_initial_scene term; projection without visible-view reprojection constraints; projection using estimated layout versus ground-truth layout; axis-aligned box proxies versus retrieved object proxies
apply random object jitter with the same average displacement as the learned or optimized projector; optimize only visible-view reconstruction without physical constraints; enforce support constraints after shuffling object categories; project scenes into deliberately incorrect room layouts; replace collision volumes with randomly scaled proxy boxes; disable the deviation penalty and measure whether the optimizer drifts away from the input evidence
reduce collision_rate by at least 30% compared with the unprojected generated scene; reduce out_of_room_rate by at least 25% without increasing image_reconstruction_lpips by more than 5%; improve support_relation_accuracy by at least 15%; maintain visible_object_recall within 5% of the initial baseline scene; increase navigation_success_rate in a simple simulator by at least 10% on generated scenes; keep projection_failure_rate below 15% on standard test inputs while correctly flagging severe corruptions

Risks, controls, or fallback:
Risk: strong geometric constraints can over-correct scenes when depth, layout, or detections are wrong, reducing agreement with the visible image. Fallback: use confidence-weighted soft constraints, cap maximum pose and scale changes, return a projection_failure warning when no low-energy repair exists, and begin with box proxies before adding detailed mesh optimization.

---

Idea 3
Title:
Single-Image Indoor Scene Benchmark with Ambiguity-Aware Metrics and Failure Warnings

Core proposal:
Build a benchmark protocol for single RGB input to complete renderable indoor scene output. The protocol renders or selects one input view from a complete 3D scene, withholds the full scene from the method, and evaluates outputs after conversion to a common scene graph format. The evaluator separates visible, self-occluded, in-frustum hidden, and out-of-view regions using ground-truth geometry and camera parameters. It reports deterministic metrics for visible evidence, physical and relational metrics for the whole scene, set-valued or distributional metrics for ambiguous hidden regions, and failure-warning metrics on intentionally ambiguous or corrupted inputs. Methods that do not output uncertainty can still be evaluated by treating their output as a single deterministic hypothesis with degenerate confidence.

Motivation or baseline weakness:
Single-image 3D indoor scene evaluation often emphasizes visible-view appearance or isolated geometry while undermeasuring hidden-region ambiguity, physical invalidity, relation errors, and whether a system can warn when the input is too ambiguous or corrupted for reliable 3D completion.

Mechanism or approach:
An ambiguity-aware evaluation harness that labels visibility states, normalizes method outputs into a common renderable scene graph, computes physical and semantic consistency metrics, scores uncertainty over hidden hypotheses when available, and evaluates failure_warning quality.
Define a transparent benchmark score while always reporting component metrics separately. The composite score is Score = w_visible GeometryVisible + w_phys PhysicalConsistency + w_rel RelationCorrectness + w_img ImageAlignment + w_unc UncertaintyCalibration + w_down DownstreamUtility - w_fail UnwarnedFailurePenalty. Hidden-region scoring uses top-1, oracle-over-K, and calibration-aware variants so deterministic and probabilistic methods are compared without forcing a single hidden ground truth to be the only valid completion.

Experiment and implementation plan:
deterministic single-image room reconstruction; single-image scene graph lifting; monocular depth estimation plus layout estimation plus object detection; image-conditioned generative room completion; multi-view-style reconstruction applied to generated or predicted views; retrieval-based room completion
synthetic indoor scenes with complete room layout, furniture geometry, object categories, and camera metadata; photorealistic rendered indoor views with depth and segmentation; real scanned indoor scenes with RGB images, camera poses, reconstructed geometry, and room annotations when available; curated stress-test inputs including cropped, narrow-FOV, cluttered, mirror-like, low-light, and strongly occluded views
render_single_view_benchmark.py for generating RGB inputs and held-out ground truth from complete 3D scenes; visibility_occlusion_labeler.py for labeling visible, self-occluded, in-frustum hidden, and out-of-view regions; baseline_adapter.py for converting method outputs into a common scene graph with geometry, layout, relations, confidence, and failure_warning fields; metric_suite.py for geometry, consistency, image-alignment, uncertainty, and downstream metrics; failure_case_generator.py for producing controlled ambiguous and corrupted inputs; benchmark_report.py for aggregate tables, paired comparisons, and diagnostic failure visualizations
visible_depth_error; visible_layout_iou; visible_object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; occlusion_consistency; visible_object_recall; novel_view_consistency; image_reconstruction_lpips; object_count_accuracy; hidden_occupancy_brier_score; confidence_calibration; ambiguity_detection; failure_detection_auc; navigation_success_rate; embodied_task_success_rate
evaluate only visible regions versus visible plus hidden regions; single ground-truth hidden completion scoring versus top-K and calibration-aware hidden scoring; with and without physical plausibility metrics; with and without relation metrics; with and without downstream navigation evaluation; failure_warning required versus ignored; synthetic-only evaluation versus synthetic-to-real split
score random scene completions matched only to the dataset object category frequency; score ground-truth scenes after shuffling object poses within each room; score ground-truth scenes after swapping room layouts across examples; score render-only billboard or facade geometry to expose appearance-only success; assign constant confidence to all hidden regions and verify calibration metrics penalize overconfidence or underconfidence; assign random failure_warning scores and verify failure_detection_auc falls near chance
benchmark ranks physically invalid but visually plausible outputs lower than physically consistent outputs in at least 80% of paired diagnostic tests; failure_detection_auc separates corrupted or highly ambiguous inputs from normal inputs with at least 0.75 AUC for a calibrated reference method; metric_suite detects shuffled-pose negative controls through at least 30% worse relation or collision scores; baseline_adapter converts at least four baseline families into the common output schema; human spot-check agreement with benchmark pairwise preference reaches at least 70% on a small validation subset; component metrics identify at least three distinct failure modes that are hidden by visible-view image alignment alone

Risks, controls, or fallback:
Risk: a benchmark contribution may be viewed as less algorithmic, and automatic plausibility metrics can be noisy or gameable. Fallback: include a simple reference method that adds uncertainty and failure_warning outputs to deterministic baselines, report all component metrics separately instead of relying only on the composite score, validate metric behavior with negative controls, and use a small human spot-check set for pairwise sanity checks.

### Candidate B

Idea 1
Title:
Uncertainty-Aware Layout-Constrained Scene Completion from a Single RGB View

Core proposal:
Add a lightweight probabilistic room-layout and hidden-region sampler before scene completion. The module uses monocular depth, object masks, and visible wall-floor cues to predict K Manhattan or piecewise-Manhattan room-layout hypotheses and K occluded free-space masks. Each completion from Text2Room-, SceneScape-, or WonderJourney-style generation is constrained to remain inside one sampled layout, and generated objects must attach to plausible support surfaces. The method returns a small set of renderable scene hypotheses with calibrated per-region confidence rather than one deterministic mesh.

Motivation or baseline weakness:
Text2Room and SceneScape can extend a scene from one image, but occluded regions are often completed as a single overconfident hallucination, producing objects outside the room, inconsistent floor-wall support, and weak failure signaling under ambiguous layouts.

Mechanism or approach:
A layout-and-occlusion hypothesis head that takes monocular depth, visible object detections, and layout cues, then emits K room-layout hypotheses, K occluded free-space masks, and per-region uncertainty scores; no large 3D generator is trained from scratch.
Minimize visible-view reprojection and monocular depth consistency while penalizing object-room violations, unsupported objects, inter-object collisions, and overconfident predictions in unobserved regions. The layout head is supervised where Structured3D or 3D-FRONT annotations are available, and uncertainty is trained/evaluated by comparing predicted hidden-region confidence against held-out full-scene geometry. The objective reports layout IoU, visible depth error, support-relation accuracy, collision rate, out-of-room rate, occlusion consistency, and confidence calibration.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; layout_estimation_baselines; monocular_depth_estimation
Structured3D single RGB renders with room layout and depth annotations; 3D-FRONT furnished room scenes rendered as single RGB inputs with object positions and support relations; Held-out Structured3D and 3D-FRONT stress splits with narrow field of view, heavy occlusion, and non-frontal views; Camera intrinsics when available, otherwise estimated focal length with uncertainty propagated into layout hypotheses
run_single_image_baselines.py to generate Text2Room, SceneScape, WonderJourney, layout-estimation, and monocular-depth outputs under the same single-RGB input protocol; infer_depth_layout_objects.py for monocular depth, object masks, visible object list, wall-floor cues, and camera normalization; sample_occlusion_hypotheses.py for K hidden-region and room-layout hypotheses with confidence scores; constrain_scene_completion.py to clip or reject generated geometry that violates sampled room bounds or support surfaces; evaluate_scene_consistency.py for depth error, layout IoU, object 3D IoU, collision rate, support-relation accuracy, out-of-room rate, occlusion consistency, visible object recall, and confidence calibration
depth_error; layout_iou; object_3d_iou; collision_rate; support_relation_accuracy; out_of_room_rate; occlusion_consistency; visible_object_recall; confidence_calibration
Single deterministic layout instead of K layout hypotheses; No occluded-region uncertainty scores; No support-surface constraint; No object-room boundary penalty; Use monocular depth only without object detections; Replace probabilistic layout sampler with the top prediction from layout_estimation_baselines
Shuffle room-layout hypotheses across images and verify layout IoU, out-of-room rate, and collision rate degrade; Force all hidden-region confidence scores to a constant and verify confidence calibration worsens; Disable collision and room-boundary penalties and verify out-of-room rate and collision rate increase; Evaluate on heavily cropped or mirror-like rendered stress cases and verify confidence decreases rather than producing high-confidence completions
Reduce out_of_room_rate by at least 25% relative to Text2Room and SceneScape on Structured3D-derived single-view tests; Reduce collision_rate by at least 20% while maintaining visible_object_recall within 5% of the best direct baseline; Improve layout_iou by at least 0.08 absolute over image-to-3D generation baselines without layout constraints; Improve confidence_calibration for occluded-region predictions by at least 15% over deterministic confidence proxies; On cropped and high-occlusion stress splits, assign lower confidence to incorrect hidden-region completions than to correct completions in at least 75% of paired comparisons

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:3dfront_2020

Risks, controls, or fallback:
Risk: layout hypotheses may be wrong for non-Manhattan rooms or images with little floor-wall evidence. Fallback: expose the uncertainty explicitly, keep multiple low-rank scene hypotheses, and use a conservative low-confidence output when layout posterior entropy is high or when all hypotheses produce high collision or out-of-room penalties.

---

Idea 2
Title:
Object-Centric Proxy Mesh Retrieval with Physical Relation Repair

Core proposal:
Use pretrained single-image depth and object masks to lift visible objects into coarse 3D boxes, retrieve category-compatible proxy meshes from 3D-FUTURE or 3D-FRONT, and run a small relation-repair optimizer that adjusts scale, yaw, support height, and room placement while preserving 2D mask reprojection and depth ordering. Hidden objects are represented only as optional low-confidence placeholders when the room layout and visible support surfaces imply likely occluded space; otherwise the method avoids committed hallucinations.

Motivation or baseline weakness:
Single-image-to-3D scene generators often produce visually plausible previews but weak object-level geometry: furniture may float, intersect, have implausible scale, or fail to preserve visible object counts and spatial relations from the input image.

Mechanism or approach:
A relation-repair optimizer over object boxes and proxy meshes with terms for 2D reprojection, monocular depth ordering, support relations, collision avoidance, room containment, and uncertainty-aware hidden object insertion.
Given detected objects, masks, depth, and estimated room layout, optimize object pose and proxy geometry assignment to maximize visible mask and depth alignment while minimizing collision volume, unsupported-object count, out-of-room placement, and overconfident hidden object creation. Proxy retrieval is scored by category compatibility, aspect-ratio match, visible silhouette agreement, and depth-consistent scale; the repair stage refines only object pose, scale, support height, and mesh choice rather than training a new scene generator.

Experiment and implementation plan:
image_to_3d_generation_baselines; Text2Room; SceneScape; DUSt3R; MASt3R; 3D Gaussian Splatting
3D-FRONT rooms with object categories, 3D positions, layouts, and support relations; 3D-FUTURE furniture meshes and textures for proxy retrieval; Structured3D rendered single RGB images with depth and layout annotations; Held-out 3D-FRONT and Structured3D single-view splits with occluded, truncated, and cluttered furniture for external validation within the supplied evidence base
detect_and_lift_objects.py for object detection, mask extraction, depth-based 3D box initialization, and camera normalization; retrieve_proxy_meshes.py for category, aspect-ratio, and silhouette-based 3D-FUTURE or 3D-FRONT mesh retrieval; optimize_scene_relations.py for physical relation repair and uncertainty-aware hidden object placeholders; render_scene_preview.py for renderable mesh or scene-graph preview generation; evaluate_object_scene_graph.py for object 3D IoU, chamfer distance, support accuracy, object relation accuracy, collision rate, visible object recall, depth error, out-of-room rate, and confidence calibration
object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; visible_object_recall; depth_error; out_of_room_rate; confidence_calibration
No relation-repair optimizer after proxy retrieval; No collision penalty; No support-height snapping; No depth-order preservation term; Use category-average cuboids instead of retrieved proxy meshes; Always insert hidden objects without uncertainty gating
Randomly assign proxy meshes within the correct category and verify chamfer distance and object 3D IoU degrade; Randomize support relations and verify support_relation_accuracy drops; Remove visible mask reprojection terms and verify visible_object_recall and depth_error degrade; Evaluate on rendered scenes with mirrors, large occluders, or truncated furniture and verify confidence decreases when mask-depth evidence is inconsistent
Improve object_3d_iou by at least 10% relative to Text2Room or image_to_3d_generation_baselines on furnished Structured3D or 3D-FRONT renders; Reduce collision_rate by at least 30% relative to unoptimized proxy placement; Improve support_relation_accuracy by at least 15% over direct scene-generation baselines; Keep visible_object_recall at or above 90% of the object-mask detector upper bound; Hidden-object confidence should improve confidence_calibration by at least 15% relative to always-insert and never-insert deterministic proxies

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:dust3r_2023; seed:mast3r_2024; seed:3dgs_2023; seed:3dfront_2020; seed:3dfuture_2020; seed:structured3d_2019; seed:midas_2023

Risks, controls, or fallback:
Risk: retrieved proxy meshes may not match unusual furniture, and detector errors can propagate into 3D placement. Fallback: use category-level proxy cuboids with texture planes when retrieval confidence is low, preserve detector uncertainty in the scene graph, and flag scenes with inconsistent depth ordering or high residual reprojection error as low-confidence outputs.

---

Idea 3
Title:
Single-Image Scene Hypothesis Benchmark with Geometry, Relation, and Failure Calibration

Core proposal:
Construct a benchmark protocol that converts supported synthetic indoor datasets into single-RGB inputs with hidden ground truth, then evaluates each method as either one renderable scene or a distribution over renderable scene hypotheses. The new component is an evaluator, not a large model: it scores visible alignment, full-scene geometry, physical plausibility, relation correctness, occlusion consistency, and confidence calibration under controlled ambiguity levels.

Motivation or baseline weakness:
Existing single-image indoor scene generation results are difficult to compare because image-level previews can look plausible while geometry, support relations, occluded-region uncertainty, and downstream usability remain unmeasured or inconsistently measured.

Mechanism or approach:
A benchmark harness and uncertainty-aware evaluator that accepts meshes, 3D Gaussians, NeRF-style rendered depth views, or scene graphs after conversion to a common object-layout-geometry representation, then computes consistency and calibration scores using the supported metrics.
Define falsifiable evaluation as risk-sensitive scene reconstruction: reward accurate visible geometry and object relations, penalize physically impossible completions, and assign lower loss to multiple calibrated hypotheses when the hidden scene is genuinely ambiguous. The evaluator reports both best-hypothesis quality and confidence-weighted expected quality, while deterministic methods are scored with confidence marked unavailable or with a documented constant-confidence proxy.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; Indoor_NeRF_prior_methods; layout_estimation_baselines; monocular_depth_estimation; DUSt3R; 3D Gaussian Splatting; NeRF
Structured3D with rendered single RGB views, room layouts, depths, and full scene geometry; 3D-FRONT and 3D-FUTURE for furnished rooms and object-level proxy meshes; Generated ambiguity splits from Structured3D and 3D-FRONT with controlled crop, occlusion, field of view, and hidden-room extent; Held-out rendered stress splits with severe occlusion, missing intrinsics, clutter, and non-Manhattan or piecewise-Manhattan layouts where annotations are available
make_single_view_splits.py to render or select one RGB view and hide all other views during inference; convert_outputs_to_common_scene.py to normalize meshes, 3D Gaussian previews, NeRF renders, depth maps, and scene graphs into layout-object-geometry records; score_geometry_relations_uncertainty.py for depth, layout, object, relation, collision, occlusion, and calibration metrics; make_failure_splits.py for extreme clutter, narrow field of view, severe occlusion, missing intrinsics, and non-Manhattan layout stress cases; run_baseline_adapters.py to execute or import outputs from Text2Room, SceneScape, WonderJourney, NeRF-style, 3DGS-style, DUSt3R-style, layout, and monocular-depth baselines under standardized output fields
depth_error; layout_iou; object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; occlusion_consistency; novel_view_consistency; visible_object_recall; confidence_calibration
Evaluate only visible rendered alignment and compare ranking changes against full geometry and relation metrics; Remove occluded-region uncertainty scoring; Remove physical plausibility checks such as collision and support constraints; Use only visible-region metrics and ignore hidden ground truth; Score only top-1 output instead of confidence-weighted multiple hypotheses; Exclude stress splits and compare reported performance inflation
Submit ground-truth visible surfaces with randomized hidden geometry to verify occlusion_consistency and chamfer_distance catch hidden-scene errors; Submit visually aligned but collision-heavy scenes to verify collision_rate and support_relation_accuracy penalties; Submit empty-room completions to verify visible_object_recall and object_3d_iou penalize missing objects; Submit constant confidence for all hidden regions to verify confidence_calibration degrades on ambiguity-controlled splits
Benchmark rankings must show at least one statistically significant disagreement between visible-alignment-only metrics and full geometry-consistency metrics, demonstrating added diagnostic value; Evaluator should assign worse occlusion_consistency or chamfer_distance to randomized hidden geometry than to valid dataset ground truth in at least 95% of paired cases; Confidence_calibration should separate correct from incorrect hidden-region hypotheses better than constant-confidence proxies for methods that emit confidence; Physical plausibility metrics should detect collision-heavy negative controls with at least 90% precision; The benchmark must run all direct baselines on at least one Structured3D split and one 3D-FRONT furnished-room split with standardized output fields

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:nerf_2020; seed:nerfvs_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:dust3r_2023; seed:3dgs_2023; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: different methods output incompatible representations and some baselines may not expose uncertainty. Fallback: require a minimal adapter that renders depth, object masks, and scene bounds from each output; for methods without uncertainty, mark confidence as unavailable or use a documented constant-confidence proxy, and score them separately on deterministic geometry, relation, collision, and occlusion-consistency metrics.

---

## Item 8: HUM-0843f3efcd

类型：`portfolio`

### Candidate A

Idea 1
Title:
Uncertainty-Aware Layout-Object Scene Graph Completion for Single-Image Indoor 3D

Core proposal:
A scene-level single-image 3D generation system that first reconstructs the visible room and objects, then completes hidden regions as a distribution over physically valid scene graphs rather than a single hallucinated mesh. Direct baselines: Text2Room, SceneScape, WonderJourney, layout_estimation_baselines, image_to_3d_generation_baselines. Transfer baselines: monocular_depth_estimation, DUSt3R, MASt3R, NeRFVS-style geometry scaffolds, 3D Gaussian Splatting for preview rendering. Borrowed components: monocular relative depth, room-layout estimation, detector/segmenter outputs for visible objects, object retrieval from 3D-FUTURE/3D-FRONT, mesh fusion or Gaussian preview rendering, and physics/collision checking. New component: a lightweight probabilistic scene-graph completion module that predicts multiple occluded object/layout hypotheses with calibrated confidence, support constraints, out-of-room checks, and explicit failure warnings. Minimal new module: a graph sampler/ranker over object categories, poses, sizes, supports, and occluded-room zones, trained or tuned on synthetic scene graphs from 3D-FRONT/Structured3D without training a large 3D generator from scratch. MVP artifacts: JSON scene graph, proxy meshes, layout cuboid/polygon, retrieved object meshes, material tags, uncertainty heatmap over unseen floor/wall regions, renderable glTF/USD preview, and per-field confidence/failure flags.

Motivation or baseline weakness:
Single-image indoor 3D scene generation is fundamentally ambiguous behind occluders and outside the visible frustum. Existing perpetual-view or text-driven systems can produce plausible visual completions but often lack explicit calibrated uncertainty, physically grounded support relations, and downstream-usable scene graphs. The key hypothesis is that representing hidden content as a small set of ranked scene-graph hypotheses will improve collision rate, support-relation accuracy, out-of-room rate, and failure detection while preserving compatibility with renderable mesh or Gaussian previews.

Mechanism or approach:
Pipeline: estimate intrinsics if unavailable; infer visible depth using MiDaS/DUSt3R-style priors; estimate layout using a HorizonNet/Structured3D-style layout module adapted to perspective crops; detect and segment visible objects; lift objects to approximate 3D boxes using depth, floor contact, and category-size priors; construct a visible scene graph with relations such as on, against-wall, in-front-of, left-of, supported-by, and occludes. The new probabilistic graph completion module divides unobserved space into occlusion volumes and out-of-view room zones, samples candidate hidden objects and extensions conditioned on room type, visible objects, free space, support surfaces, and category co-occurrence, then ranks hypotheses with geometric and physical energy terms. Each hypothesis is converted to proxy boxes or retrieved meshes from 3D-FUTURE/3D-FRONT, textured from visible image patches when possible or assigned material priors otherwise. A differentiable or heuristic consistency pass rejects objects outside the layout, interpenetrating furniture, floating unsupported objects, impossible depth ordering, and completions that contradict visible masks. Render output can be mesh-based or converted to lightweight 3D Gaussian/NeRF-style preview only after the structured scene is fixed. Failure warnings are triggered for mirror/glass scenes, extreme fisheye or unknown intrinsics, severe occlusion, inconsistent depth/layout evidence, detector disagreement, or high entropy over hidden hypotheses.

Experiment and implementation plan:
Datasets: train/tune graph priors on 3D-FRONT, 3D-FUTURE, Structured3D; evaluate on held-out synthetic single-view renderings plus Matterport3D/ScanNet/Hypersim where annotations allow partial 3D checks. Metrics: depth_error, layout_iou, object_3d_iou, chamfer_distance for visible geometry; collision_rate, support_relation_accuracy, object_relation_accuracy, out_of_room_rate, occlusion_consistency for scene consistency; visible_object_recall, object_count_accuracy, image_reconstruction_lpips, novel_view_consistency for image alignment; confidence_calibration, ambiguity_detection, failure_detection_auc for uncertainty; optional navigation_success_rate or embodied_task_success_rate using the exported scene graph. Ablations: no uncertainty and single MAP completion; no physics/collision checker; no support-relation constraints; depth-only lifting versus layout-aware lifting; retrieved meshes versus proxy boxes; graph prior trained on 3D-FRONT only versus Structured3D plus 3D-FRONT; entropy thresholding versus learned failure predictor. Risks: synthetic-to-real gap, weak metric scale from monocular depth, detector misses, overconfident priors hiding rare layouts, and poor material hallucination for occluded regions. Failure criteria: worse collision_rate or out_of_room_rate than Text2Room/SceneScape-style baselines, uncalibrated confidence with high expected calibration error, hidden-object hypotheses that contradict visible masks/depth ordering, or no improvement in downstream navigation/task success over using visible geometry only. Implementation plan: build preprocessing with depth/layout/detection; implement 3D lifting and visible scene graph; mine layout-object relation statistics; implement constrained graph sampler and ranker; add mesh retrieval/proxy geometry and material assignment; export glTF/USD plus JSON uncertainty; run benchmark and ablations against direct baselines.

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:3dfront_2020; seed:3dfuture_2020; seed:midas_2023; seed:dust3r_2023; seed:mast3r_2024; seed:nerf_2020; seed:nerfvs_2023; seed:3dgs_2023

---

Idea 2
Title:
Geometry-Verified Perpetual Indoor Expansion from One RGB Image

Core proposal:
A single-image indoor 3D generation method that adapts perpetual scene expansion systems by inserting a geometry-verification loop after every synthesized view. Direct baselines: Text2Room, SceneScape, WonderJourney, Indoor_NeRF_prior_methods, image_to_3d_generation_baselines. Transfer baselines: monocular_depth_estimation, DUSt3R, MASt3R, 3D Gaussian Splatting, NeRF/NeRFVS. Borrowed components: iterative viewpoint selection and inpainting from Text2Room/SceneScape, scene planning and VLM-style verification from WonderJourney, pretrained depth/pointmap estimation, mesh or Gaussian fusion, and physics/collision checking. New component: a geometry-and-relation verifier that scores each newly generated view against the current 3D scaffold, visible object graph, occlusion map, and physical constraints before fusion. Minimal new module: a verifier/reranker that evaluates candidate inpainted novel views and their lifted geometry using depth consistency, object persistence, support relations, and uncertainty-aware occlusion rules. MVP artifacts: iterative generated camera path, accepted/rejected view candidates, fused proxy mesh or Gaussian scene, per-region uncertainty, object instance table, spatial-relation graph, render preview, and failure report.

Motivation or baseline weakness:
Perpetual indoor generation can fill missing views, but small depth or object drift errors accumulate into distorted room geometry, duplicated furniture, floating objects, and inconsistent occlusions. The idea is to keep the generative power of Text2Room/SceneScape/WonderJourney-style expansion while making each step pass explicit 3D consistency checks before it can alter the scene representation. This should improve novel-view consistency, collision rate, support-relation accuracy, and downstream usability without requiring a new large 3D generative model.

Mechanism or approach:
Starting from a single RGB image, estimate depth, camera intrinsics if absent, room layout, visible object masks, and an initial mesh/point scaffold. Select next-best expansion views that target uncertain or occluded regions but remain near the inferred room envelope. For each target view, generate K candidate images using an image-conditioned inpainting/perpetual-view model; estimate depth or pointmaps for each candidate; align the candidate geometry to the existing scaffold; and evaluate with the new verifier. The verifier penalizes inconsistent wall/floor boundaries, object identity drift, duplicated visible objects, unsupported furniture, objects outside the room, impossible occluder ordering, texture discontinuities across reprojected surfaces, and hallucinated openings that contradict the initial layout. Accepted candidates update the mesh or Gaussian representation; rejected candidates either resample with stronger constraints or mark the region as uncertain. Hidden areas are not forced into a single completion: the system stores alternate candidate completions with confidence scores and exposes uncertainty in the final scene graph. Final output includes estimated room layout, object instances, object positions, geometry/proxy meshes, spatial relations, occluded-region hypotheses, material/texture assignments, render preview, confidence, and failure warnings.

Experiment and implementation plan:
Datasets: use 3D-FRONT/3D-FUTURE/Structured3D for controlled single-view rendering and full 3D ground truth; test real-domain behavior on Matterport3D, ScanNet, and Hypersim single-view inputs. Metrics: depth_error and chamfer_distance for fused geometry; layout_iou and out_of_room_rate for room structure; object_3d_iou, visible_object_recall, object_count_accuracy for instance recovery; collision_rate, support_relation_accuracy, object_relation_accuracy, occlusion_consistency for physical and semantic plausibility; novel_view_consistency and image_reconstruction_lpips for rendering; confidence_calibration and failure_detection_auc for uncertain completions. Ablations: no verifier; verifier with only depth consistency; verifier with depth plus layout; verifier with full layout-object-physics relations; random camera expansion versus uncertainty-targeted next-best views; mesh fusion versus Gaussian preview; single generated candidate versus K-candidate reranking; storing uncertainty alternatives versus forced fusion. Risks: verification may over-reject creative but valid completions, generated candidates may share systematic depth errors, real images may lack reliable intrinsics, and iterative pipelines can be slow. Failure criteria: expansion reduces initial visible-object recall, accepted views increase collision_rate or out_of_room_rate, novel-view consistency fails to improve over SceneScape/Text2Room-style baselines, uncertainty scores do not predict errors, or repeated rejection leaves most occluded regions unresolved. Implementation plan: reproduce a Text2Room/SceneScape-like image-start expansion baseline; add depth/layout/object preprocessing; implement candidate generation and alignment; implement verifier scoring terms; add K-best reranking and uncertainty logging; evaluate against direct baselines and report failure categories such as mirrors, glass, extreme clutter, open doors, non-Manhattan rooms, and severe occlusion.

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:3d_scenedreamer_2024; seed:midas_2023; seed:dust3r_2023; seed:mast3r_2024; seed:nerf_2020; seed:nerfvs_2023; seed:3dgs_2023; seed:3dfront_2020; seed:3dfuture_2020; seed:structured3d_2019

---

Idea 3
Title:
Single-Image Indoor Scene Generation Benchmark with Ambiguity-Aware Ground Truth Sets

Core proposal:
A benchmark construction proposal for evaluating complete 3D indoor scene generation from one RGB image using not only one hidden ground-truth scene, but a set of valid alternatives and uncertainty-aware metrics. Direct baselines: Text2Room, SceneScape, WonderJourney, layout_estimation_baselines, image_to_3d_generation_baselines, Indoor_NeRF_prior_methods. Transfer baselines: monocular_depth_estimation, DUSt3R, MASt3R, NeRF, 3D Gaussian Splatting. Borrowed components: synthetic rendering from 3D-FRONT/3D-FUTURE/Structured3D, real scans from Matterport3D/ScanNet/Hypersim, object detectors, scene-graph evaluators, CLIP-like image alignment, physics/collision checking, and layout/depth evaluation. New component: an ambiguity-aware evaluation protocol that separates visible reconstruction accuracy from hidden-region plausibility and rewards calibrated distributions over occluded scene completions. Minimal new module: a metric suite that converts predicted meshes/scene graphs into comparable layout, object, relation, free-space, support, material, and uncertainty records. MVP artifacts: curated single-image splits, camera/intrinsics metadata, visible masks, hidden-region labels, multiple plausible completion sets for synthetic scenes, standardized JSON scene-graph schema, renderer scripts, baseline wrappers, metric leaderboard, and failure taxonomy.

Motivation or baseline weakness:
A major bottleneck for single-image 3D indoor scene generation is evaluation: hidden regions are ambiguous, image-level previews can look plausible despite broken 3D structure, and full-scene metrics unfairly penalize plausible alternatives that differ from one ground-truth arrangement. A benchmark that explicitly measures visible fidelity, hidden plausibility, physical consistency, and uncertainty calibration would make progress measurable and expose failure cases that current image-centric evaluation misses.

Mechanism or approach:
Construct a benchmark from synthetic and scanned indoor data. For each scene, render single RGB images with known intrinsics, layout, object meshes, material labels, depth, visible masks, and occlusion masks. Partition annotations into visible-required elements and hidden-ambiguous elements. For synthetic rooms, create ambiguity sets by sampling alternative furniture placements and object instances that preserve room type, visible evidence, free-space constraints, support relations, and collision-free layout. For real scans, use partial annotations and human/automatic plausibility labels rather than requiring exact hidden-object recovery. Prediction format is a renderable 3D scene or scene graph with estimated_room_layout, object_instances, object_3d_positions, geometry/proxy meshes, spatial_relations, occluded_region_hypotheses, materials/textures, preview render, confidence/uncertainty, and failure_warning. Evaluation first scores visible geometry and objects against ground truth, then scores hidden regions by best-of-set plausibility, relation validity, free-space consistency, and calibration rather than exact object identity only. The benchmark includes wrappers for Text2Room, SceneScape, WonderJourney-like expansion, monocular-depth-only lifting, layout-only reconstruction, and Gaussian/NeRF-style preview baselines.

Experiment and implementation plan:
Datasets: primary synthetic benchmark from 3D-FRONT, 3D-FUTURE, Structured3D; validation on Hypersim; real-image stress tests from Matterport3D and ScanNet. Metrics: geometry_quality includes depth_error, layout_iou, object_3d_iou, chamfer_distance, collision_rate; scene_consistency includes support_relation_accuracy, object_relation_accuracy, out_of_room_rate, occlusion_consistency; image_alignment includes visible_object_recall, novel_view_consistency, image_reconstruction_lpips, object_count_accuracy; uncertainty includes confidence_calibration, ambiguity_detection, failure_detection_auc; downstream includes navigation_success_rate and embodied_task_success_rate in generated scenes. Ablations: exact hidden-ground-truth scoring versus ambiguity-set scoring; visible-only evaluation versus full-scene evaluation; mesh-based versus scene-graph-based metric extraction; human plausibility labels versus automatic physics/CLIP/object-detector checks; uncertainty ignored versus uncertainty-calibrated scoring. Risks: ambiguity-set generation may encode dataset priors too strongly, automatic plausibility may miss semantic absurdities, real scans may have incomplete annotations, and benchmark incentives could favor conservative empty-room predictions. Failure criteria: metric rankings fail to correlate with human judgments, baselines exploit loopholes by outputting vague geometry or excessive uncertainty, hidden-region scoring is unstable across plausible alternatives, or the benchmark cannot distinguish geometry-consistent systems from visually plausible but physically broken systems. Implementation plan: define schema and converter for renderable scenes/scene graphs; render single-view benchmark splits; compute visible/hidden masks and alternative completion sets; implement metric extraction from meshes/boxes/graphs; wrap Text2Room, SceneScape, WonderJourney-style, depth-only, layout-only, and Gaussian/NeRF-style baselines; run a pilot human study for plausibility correlation; publish leaderboard, baseline outputs, and failure taxonomy covering mirrors, glass, clutter, non-Manhattan layouts, open doors, missing intrinsics, unusual object scales, and severe occlusion.

Evidence paper IDs:
seed:3dfront_2020; seed:3dfuture_2020; seed:structured3d_2019; seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:3d_scenedreamer_2024; seed:horizonnet_2019; seed:midas_2023; seed:dust3r_2023; seed:mast3r_2024; seed:nerf_2020; seed:nerfvs_2023; seed:3dgs_2023

### Candidate B

Idea 1
Title:
Uncertainty-Gated Occlusion Hypothesis Layer for Single-Image Room Completion

Core proposal:
Add a lightweight probabilistic occlusion hypothesis layer on top of a Text2Room-style single-image pipeline. From the input RGB image, estimate visible layout, visible object masks or boxes, and monocular depth; construct occlusion volumes from depth discontinuities, foreground masks, room-boundary rays, and unobserved frustum cells; then sample K scene-graph hypotheses over hidden occupied or empty regions. Each hypothesis is scored by room containment, object-size priors, support feasibility, pairwise collision checks, consistency with visible reprojection, and a confidence head calibrated against whether the hidden-region hypothesis matches held-out synthetic ground truth. Visible surfaces from the baseline reconstruction are kept fixed except for small depth/layout alignment corrections, while occluded regions are represented as weighted alternatives rather than a single mesh completion.

Motivation or baseline weakness:
Text2Room, SceneScape, and WonderJourney can expand a scene from one image, but hidden regions are often filled as a single confident completion, causing unsupported objects, duplicate furniture, out-of-room geometry, and poor calibration under single-image ambiguity.

Mechanism or approach:
A small occlusion-volume-to-scene-graph sampler plus confidence calibration head. It consumes outputs from pretrained monocular depth, layout estimation, object-mask extraction, and an existing Text2Room/SceneScape/WonderJourney-style mesh construction pipeline; it does not train a large 3D generator from scratch.
Optimize hypothesis weights and hidden-object parameters with L = L_visible_reprojection + L_depth_consistency + L_layout + L_relation + L_collision + L_room_containment + L_calibration. The visible losses constrain the reconstruction to the input image, relation/collision/containment losses score physical plausibility in 3D, and the calibration term penalizes high confidence when multiple hidden completions remain compatible with the visible evidence.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; layout_estimation_baselines; monocular_depth_estimation; 3D-FRONT
Single RGB indoor images with camera intrinsics when available; 3D-FRONT/3D-FUTURE rendered single-view rooms with full hidden-object, layout, and relation ground truth; Structured3D rendered views for layout and depth supervision; Held-out real single RGB indoor images used only for qualitative validation and visible-region metrics when full hidden ground truth is unavailable
run_single_image_baselines.py for Text2Room, SceneScape, and WonderJourney comparisons under identical single-image input assumptions; extract_visible_objects_layout_depth.py to produce visible masks or boxes, room-layout planes, and monocular depth maps; build_occlusion_volumes.py to mark unobserved cells from depth discontinuities, visible masks, camera rays, and room layout; sample_uncertain_scene_graphs.py to sample K hidden empty/occupied/object hypotheses with weights; score_and_calibrate_hypotheses.py to compute relation, collision, containment, reprojection, and confidence terms; evaluate_geometry_relations_uncertainty.py for layout, object, collision, occlusion, and calibration metrics
depth_error; layout_iou; object_3d_iou; chamfer_distance; collision_rate; out_of_room_rate; support_relation_accuracy; object_relation_accuracy; occlusion_consistency; visible_object_recall; confidence_calibration
Remove occlusion-volume reasoning and sample hidden objects from global 3D-FRONT category and size priors only; Replace multi-hypothesis output with the top-1 completion while keeping the same sampler; Remove calibration loss while keeping identical geometric scoring; Remove collision and support-relation scoring from hypothesis ranking; Use visible-object evidence only without room-layout containment constraints
Sample hidden objects uniformly from 3D-FRONT category frequencies without conditioning on the input image; Assign uniformly high confidence to every occluded hypothesis regardless of ambiguity; Place hidden objects using 2D image-space proximity only, without 3D room layout or depth constraints; Evaluate on synthetic views with minimal occlusion where calibrated uncertainty should collapse to low entropy; Shuffle occlusion-volume labels before sampling to verify the sampler depends on geometric visibility rather than dataset priors alone
Reduce collision_rate by at least 25% relative to the strongest Text2Room-style single-hypothesis completion at matched visible_object_recall; Improve occlusion_consistency by at least 10% over single-hypothesis SceneScape/WonderJourney outputs on held-out synthetic rooms; Improve confidence_calibration ECE by at least 20% for hidden occupancy and hidden-object placement confidence; Maintain visible_object_recall within 3 percentage points of the best direct baseline; Failure criterion: if uncertainty does not correlate with hidden-region error better than baseline confidence or entropy scores, the occlusion hypothesis mechanism is not supported

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: hidden-object supervision from synthetic rooms may not transfer to real indoor images, and category-level hidden-object prediction may be underdetermined from a single RGB view. Fallback: report synthetic hidden-region results separately from real-image visible-region checks, expose uncertainty over empty versus occupied occlusion volumes even when category labels are unreliable, and treat human or VLM plausibility checks as secondary diagnostics rather than primary evidence.

---

Idea 2
Title:
Geometry-First Scene Graph Repair for Image-to-3D Indoor Generation

Core proposal:
Insert a post-generation geometry repair stage after a Text2Room/SceneScape/WonderJourney-style output. The stage canonicalizes the generated mesh into a typed scene graph containing room planes, visible object proxies, approximate object boxes, support candidates, containment relations, and pairwise spatial relations. It then solves a constrained 3D repair problem over object poses, box dimensions, support contacts, and layout-plane alignment while preserving visible-image projections and retaining the original generated textures where possible. The repair is accepted only if constraint violations are reduced without moving visible evidence beyond a preset reprojection/depth tolerance; otherwise the system emits a failure warning instead of silently changing the scene.

Motivation or baseline weakness:
Image-to-3D room generation baselines can produce visually plausible previews while violating basic 3D constraints: furniture floats, penetrates walls, lacks support surfaces, exits the room boundary, or drifts from the visible object layout because generation is not explicitly repaired against a structured scene graph.

Mechanism or approach:
A differentiable or search-based scene graph repair optimizer over room planes, object 3D boxes, support contacts, containment, and collision constraints. It uses pretrained depth, object-mask or box extraction, and layout modules for perception, and reuses the baseline-generated mesh as the visual asset rather than replacing it with a new generator.
Minimize E = reprojection_error + depth_alignment + layout_plane_error + object_box_prior + collision_penalty + support_penalty + out_of_room_penalty + relation_penalty + texture_anchor_penalty, subject to visible object masks remaining aligned with the input RGB image and repaired proxy geometry remaining physically plausible and renderable. If the minimum feasible solution exceeds a visible-alignment threshold, the method returns an explicit repair failure warning.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; image_to_3d_generation_baselines; layout_estimation_baselines; monocular_depth_estimation; 3D-FRONT
Single RGB indoor images with visible object masks, boxes, or detector outputs; 3D-FRONT/3D-FUTURE scenes for object-size, support, containment, and relation priors; Structured3D rendered views for room layout and depth evaluation; Held-out real single-view indoor images for visible reprojection, depth, and qualitative stress tests where full object ground truth is not available
run_generation_baselines.py to produce initial Text2Room, SceneScape, WonderJourney, or image-to-3D baseline scenes under matched inputs; baseline_scene_to_graph.py to extract layout planes, object proxies, boxes, and approximate meshes from generated scenes; fit_proxy_scene_graph.py to estimate typed object proxies and candidate support or containment relations; repair_scene_geometry.py to optimize object transforms, supports, collisions, and room containment with visible-alignment constraints; render_repaired_scene.py to export repaired mesh, proxy scene graph, and before/after previews; evaluate_scene_graph_geometry.py for relation, collision, layout, depth, and visible-alignment metrics
layout_iou; object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; depth_error; visible_object_recall; novel_view_consistency
Use the visual generation output directly without repair; Optimize collisions only without support relations; Optimize support relations only without room containment; Remove visible reprojection and depth constraints and allow unconstrained 3D repair; Use class-agnostic boxes instead of category-specific size and support priors; Replace the accept/reject failure gate with always-apply repair
Apply the repair optimizer to random object layouts initialized far from the input image to verify visible-alignment constraints reject them; Shuffle object categories while keeping boxes fixed to test whether semantic support priors matter; Disable room layout planes and allow objects outside the room to verify containment penalties are necessary; Run repair on ground-truth synthetic layouts where changes should be minimal; Perturb visible object masks before repair to test whether the optimizer overfits noisy perception rather than stable 3D constraints
Reduce collision_rate by at least 30% compared with the unrepaired baseline output; Reduce out_of_room_rate by at least 30% without decreasing visible_object_recall by more than 3 percentage points; Improve support_relation_accuracy by at least 10% on rendered 3D-FRONT/Structured3D-style test views; Maintain depth_error and layout_iou within 5% of the unrepaired visible reconstruction unless the baseline was already geometrically invalid; Failure criterion: if repairs improve constraints only by moving visible objects away from their input-image projections, the mechanism fails the single-image alignment requirement

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:3d_scenedreamer_2024; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: proxy boxes may oversimplify detailed furniture and improve relation metrics while hurting visual fidelity. Fallback: keep original textured meshes attached to repaired proxy transforms, report proxy-geometry metrics separately from rendered-view metrics, and trigger failure warnings when the repair requires large visible reprojection or depth changes.

---

Idea 3
Title:
Single-Image Indoor Scene Benchmark with Ambiguity-Aware Multi-Hypothesis Evaluation

Core proposal:
Build an ambiguity-aware benchmark protocol from synthetic indoor scenes with complete 3D ground truth and optional real-image validation. Each test case exposes one RGB image, camera metadata when available, and the required output format; full layout, depth, object, relation, and hidden-region annotations remain hidden for evaluation. Methods may submit either one reconstruction or K weighted hypotheses, but all outputs must be canonicalized into a proxy scene graph plus renderable asset. Visible regions are scored deterministically against the input view, while occluded regions are scored with top-K, set-valued, and confidence-calibration criteria. The new component is the evaluator and submission protocol, not a new generator.

Motivation or baseline weakness:
Existing single-image-to-3D scene methods are hard to compare because evaluations often reward one plausible render but under-measure geometric consistency, hidden-region ambiguity, physical constraints, representation-specific artifacts, and explicit failure detection.

Mechanism or approach:
A benchmark evaluator that canonicalizes meshes, Gaussian splats, NeRF-like renderers, and scene-graph outputs into a common proxy representation with layout planes, object boxes or meshes, relations, occlusion hypotheses, confidence values, and failure warnings, then computes deterministic visible metrics and probabilistic hidden-region metrics.
Define a falsifiable benchmark score S = S_visible_geometry + S_layout + S_relations + S_collision + S_novel_view + S_occlusion_topK + S_calibration - S_failure_penalty, with separate leaderboards for top-1 reconstruction, multi-hypothesis hidden-region plausibility, and calibrated failure detection. Scores are also reported by input protocol so true single-image methods are not conflated with methods that require extra views, poses, or optimization data.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; Indoor_NeRF_prior_methods; layout_estimation_baselines; monocular_depth_estimation; DUSt3R; MASt3R; 3D Gaussian Splatting; NeRF; 3D-FRONT
3D-FRONT/3D-FUTURE rendered rooms with full object meshes, materials or textures, layout, and relations; Structured3D rendered images with layout and depth annotations; Single RGB image per test case plus optional camera intrinsics; Optional held-out real single-view indoor images used for visible-region and qualitative validation only when complete hidden-region ground truth is unavailable
render_single_view_benchmark.py to produce RGB, depth, masks, layout, relations, camera metadata, and hidden-region labels from synthetic scenes; canonicalize_scene_outputs.py to convert mesh, Gaussian, NeRF-style, or scene-graph outputs into a common proxy representation; compute_visible_geometry_metrics.py for depth, layout, object, and chamfer metrics; compute_scene_consistency_metrics.py for support, relation, collision, out-of-room, and occlusion-consistency metrics; compute_uncertainty_failure_metrics.py for confidence calibration and failure-warning evaluation; run_baseline_protocols.py to run single-image baselines separately from multi-view or optimization-heavy baselines and label their input assumptions
depth_error; layout_iou; object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; occlusion_consistency; visible_object_recall; novel_view_consistency; confidence_calibration
Evaluate only top-1 scenes instead of top-K hypotheses; Remove occluded-region metrics and score visible regions only; Remove support, collision, and out-of-room checks; Remove confidence and failure-warning requirements; Score rendered previews only through visible depth and novel-view consistency without canonical scene-graph checks; Pool single-image and extra-view methods into one leaderboard to quantify how much protocol mixing changes rankings
Score ground-truth scenes with randomized hidden objects to verify occlusion metrics detect implausible completions; Score visually plausible 2D billboard rooms to verify geometry metrics penalize non-3D solutions; Score outputs with shuffled confidence values to verify calibration metrics degrade; Score scenes with deliberately moved furniture outside room boundaries to verify out_of_room_rate and collision checks respond; Submit ground-truth proxy scene graphs with degraded render textures to verify the benchmark does not collapse to image-preview quality alone
Benchmark must separate ground-truth scenes from randomized hidden-object negative controls by at least 0.25 normalized score; Adding consistency metrics must prevent a known geometry-violating output from outranking a physically valid output solely due to preview quality; Confidence_calibration must worsen measurably when confidence values are shuffled or made uniformly high; At least three direct baselines must be runnable through the canonical evaluator without manual per-scene intervention; Failure criterion: if leaderboard ranking is dominated by preview or visible-only quality while collision, relation, and occlusion errors remain statistically indistinguishable, the benchmark does not meet the research goal

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:nerf_2020; seed:nerfvs_2023; seed:dust3r_2023; seed:mast3r_2024; seed:3dgs_2023; seed:3dfront_2020; seed:3dfuture_2020; seed:structured3d_2019

Risks, controls, or fallback:
Risk: canonicalizing diverse representations such as meshes, NeRFs, Gaussian splats, and scene graphs may introduce evaluator bias, and some listed reconstruction baselines are not true single-image methods. Fallback: require every submission to include a minimal proxy scene graph plus renderable asset, report representation-specific diagnostics separately, split leaderboards by input protocol, and use negative controls to audit whether the evaluator rewards physical 3D structure rather than format artifacts.

---

## Item 9: HUM-d38d202fa3

类型：`single_idea`

### Candidate A

Title:
Relation-First Object Proxy Reconstruction for Renderable Indoor Scene Graphs

Core proposal:
Convert the single image into an object-centric scene graph with cuboids or retrieved proxy meshes, then optimize object scale, pose, room containment, and support relations before any texture transfer or inpainting. DUSt3R/MASt3R-style geometry is used only when valid image collections or generated auxiliary views are available; the core single-image path relies on monocular depth, masks, layout, and 3D-FRONT/3D-FUTURE size/support priors.

Motivation or baseline weakness:
Single-image scene generators and image-to-3D baselines can preserve the input-view appearance but often lack object-level 3D proxies that satisfy stable spatial relations such as on, against, inside, left-of, and in-front-of. This limits geometric evaluation, editing, and embodied use even when preview renderings look plausible.

Mechanism or approach:
A differentiable or search-based object proxy optimizer that initializes object cuboids from 2D detections, masks, monocular depth, and layout. It assigns candidate support surfaces, retrieves category-compatible proxy meshes when available, and adjusts 3D positions, scale, and yaw to satisfy relation constraints while preserving visible reprojection alignment.
Minimize a weighted objective combining 2D mask reprojection error, depth consistency, room-layout containment, pairwise collision penalties, support-surface distance, and relation-class penalties. Texture generation or view inpainting is applied only after proxy geometry passes collision, containment, and support checks.

Experiment and implementation plan:
image_to_3d_generation_baselines; Text2Room; WonderJourney; DUSt3R; MASt3R; 3D Gaussian Splatting
3D-FRONT and 3D-FUTURE for object categories, proxy meshes, sizes, and support priors; Structured3D for rendered single-view layout and depth supervision; A held-out rendered single-view split with ground-truth 3D boxes, support relations, and visible masks; Optional real indoor images used only when the same visible-object and relation annotations can be standardized
extract_2d_instances_and_masks.py; estimate_single_view_depth_or_pointmap.py; initialize_object_proxies.py; optimize_scene_graph_relations.py; retrieve_or_fit_proxy_meshes.py; render_scene_preview.py; evaluate_object_relation_metrics.py
object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; visible_object_recall; novel_view_consistency; depth_error; layout_iou
Use direct Text2Room-style mesh fusion without object proxy optimization; Optimize object poses without support-relation terms; Optimize support relations without collision penalties; Use cuboids only versus retrieved 3D-FUTURE proxy meshes; Run texture generation before versus after relation-consistent proxy fitting; Remove room-layout containment while keeping object relation terms
Randomize support-surface assignments while keeping object detections fixed; Use depth estimates with shuffled or incorrect scale to test metric-scale sensitivity; Evaluate on rendered scenes with transparent, reflective, or very thin support surfaces where proxy assumptions should be uncertain; Randomly rotate retrieved proxy meshes within each object category to confirm relation and reprojection metrics detect implausible fits
Improve support_relation_accuracy by at least 15 percentage points over image-to-3D generation baselines; Reduce collision_rate by at least 25% relative to Text2Room or WonderJourney outputs converted to meshes; Improve object_3d_iou by at least 10% on visible major furniture categories in 3D-FRONT renders; Maintain visible_object_recall within 5% of the best direct baseline; Improve novel_view_consistency without increasing out_of_room_rate relative to unconstrained mesh generation

Evidence paper IDs:
seed:text2room_2023; seed:wonderjourney_2023; seed:dust3r_2023; seed:mast3r_2024; seed:3dgs_2023; seed:3dfront_2020; seed:3dfuture_2020; seed:structured3d_2019; seed:midas_2023

Risks, controls, or fallback:
Risk: object detectors and masks may miss heavily occluded or small objects, causing incomplete scene graphs. Fallback: optimize and report major furniture separately from small clutter, keep an uncertain residual occupancy layer for low-confidence regions, and expose low visible_object_recall or mask confidence through confidence_calibration rather than hallucinating precise proxies.

### Candidate B

Title:
Relation-First Object Proxy Reconstruction for Renderable Indoor Scene Graphs

Core proposal:
Reconstruct the room as an object-centric renderable scene graph before final texture generation. The method initializes object proxies from 2D detections, masks, depth, and layout, then jointly optimizes object scale, pose, support surfaces, and pairwise relations so the scene is geometrically usable as well as visually plausible.

Motivation or baseline weakness:
Single-image scene generators and image-to-3D baselines can preserve the input-view appearance while producing object geometry that is hard to use for downstream tasks. Common failures include furniture floating, intersecting, lacking support surfaces, or violating relations such as on, against, inside, left-of, and in-front-of.

Mechanism or approach:
A differentiable or search-based object proxy optimizer that initializes cuboids or retrieved meshes from 2D instance masks and depth, assigns candidate support surfaces, estimates metric scale, and adjusts 3D object positions to satisfy relations, avoid collisions, and preserve image reprojection alignment.
Minimize a weighted objective over 2D mask reprojection error, depth consistency, room containment, object scale priors, pairwise collision penalties, support-surface distance, and relation-class loss. Texture transfer or image-based inpainting is applied only after the proxy scene graph passes geometry and relation consistency checks.

Experiment and implementation plan:
image_to_3d_generation_baselines; Text2Room; WonderJourney; DUSt3R; MASt3R; 3D Gaussian Splatting
3D-FRONT and 3D-FUTURE for object categories, proxy meshes, object sizes, and support priors; Structured3D for rendered single-view layout, depth, and object supervision; ScanNet or Matterport3D for real indoor object-relation evaluation and domain-shift testing
extract_2d_instances_masks_and_categories.py; estimate_single_view_depth_or_pointmap.py; initialize_object_proxies.py; optimize_scene_graph_relations.py; retrieve_or_fit_proxy_meshes.py; texture_and_render_scene_preview.py; evaluate_object_geometry_and_relations.py
object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; visible_object_recall; object_count_accuracy; novel_view_consistency; navigation_success_rate
Use direct Text2Room-style mesh fusion without object proxy optimization; Optimize object poses without support-relation terms; Optimize support relations without collision penalties; Compare cuboid-only proxies against retrieved 3D-FUTURE proxy meshes; Run texture generation before relation-consistent proxy fitting instead of after it
Randomize support-surface assignments while keeping object detections fixed; Use depth estimates with shuffled or corrupted scale to test metric-scale sensitivity; Evaluate on scenes with mirrors, transparent furniture, and severe occlusion where proxy assumptions should fail
Improve support_relation_accuracy by at least 15 percentage points over image-to-3D generation baselines; Reduce collision_rate by at least 25% relative to Text2Room or WonderJourney outputs converted to meshes; Improve object_3d_iou by at least 10% for visible major furniture categories on 3D-FRONT renders; Maintain visible_object_recall within 5% of the best direct baseline; Increase navigation_success_rate in a simple collision-aware simulator by at least 10% over unconstrained meshes

Evidence paper IDs:
seed:text2room_2023; seed:wonderjourney_2023; seed:dust3r_2023; seed:mast3r_2024; seed:3dgs_2023; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: missed detections, poor masks, and heavy occlusion may produce incomplete object graphs, especially for small objects and clutter. Fallback: evaluate major furniture separately from small clutter, maintain an uncertain residual occupancy layer for low-confidence regions, and emit a failure_warning when mask confidence or visible_object_recall is too low for reliable relation optimization.

---

## Item 10: HUM-4193564153

类型：`portfolio`

### Candidate A

Idea 1
Title:
Uncertainty-Aware Scene Graph Scaffolds for Single-Image Indoor 3D Generation

Core proposal:
Build a single-image-to-3D pipeline that first predicts a metric room-layout scaffold, visible object instances, object support relations, and a distribution over occluded objects or free-space regions, then uses these constraints to guide a renderable mesh or Gaussian-splat scene generator. The output is a scene-level representation containing estimated_room_layout, object_instances, object_3d_positions, proxy meshes or retrieved CAD-like shapes, spatial_relations, occluded_region_hypotheses, materials_or_textures, render_or_preview, confidence_or_uncertainty, and failure_warning. The minimal new module is a lightweight probabilistic scene-graph scaffold that sits between pretrained monocular depth/layout/object modules and existing scene generation systems such as Text2Room, SceneScape, or WonderJourney.

Motivation or baseline weakness:
Text2Room, SceneScape, and WonderJourney can produce room-scale 3D content, but their hidden-region completions are often evaluated mainly through visual plausibility rather than explicit object-level geometry, support, collision, and uncertainty. Single RGB inputs are inherently ambiguous, so a publishable improvement is not to claim a unique hidden scene, but to expose calibrated alternatives and use them to prevent physically implausible completions such as floating objects, furniture outside the room, impossible occlusions, or visible-object mismatches.

Mechanism or approach:
Use monocular_depth_estimation or DUSt3R-style pointmap priors to estimate visible geometry, a layout_estimation_baseline to infer floor/wall/ceiling planes, and an object detector plus segmentation to lift visible objects into approximate 3D boxes. The new component is a probabilistic room scene graph with nodes for visible objects, layout surfaces, empty-space constraints, and occluded-region hypotheses; edges encode support, containment, adjacency, front-behind ordering, and collision exclusions. For hidden areas, sample multiple plausible completions conditioned on visible cues and common indoor priors from 3D-FRONT/3D-FUTURE, then pass the sampled scaffold to a mesh or Gaussian-based renderer. The scaffold constrains Text2Room/SceneScape-style view expansion by rejecting generations that violate layout bounds, visible-object masks, support relations, or depth ordering. Direct baselines are Text2Room, SceneScape, WonderJourney, image_to_3d_generation_baselines, layout_estimation_baselines, and monocular_depth_estimation. Transfer baselines are DUSt3R, MASt3R, 3D Gaussian Splatting, NeRF, and Indoor_NeRF_prior_methods. Borrowed components include monocular relative depth, iterative inpainting/fusion, room-layout estimation, object detection, shape retrieval, and collision checking. The key novelty is calibrated scene-graph uncertainty over occluded regions used as a hard/soft geometric controller rather than only a post-hoc description.

Experiment and implementation plan:
Datasets: Structured3D and Hypersim for layout/depth/rendered indoor images, 3D-FRONT and 3D-FUTURE for object layout and furniture priors, ScanNet or Matterport3D for real-image stress tests. Metrics: depth_error, layout_iou, object_3d_iou, chamfer_distance, collision_rate, support_relation_accuracy, object_relation_accuracy, out_of_room_rate, occlusion_consistency, visible_object_recall, novel_view_consistency, image_reconstruction_lpips, object_count_accuracy, confidence_calibration, ambiguity_detection, and failure_detection_auc. Ablations: remove scene graph constraints, remove support edges, remove collision checking, replace probabilistic occlusion hypotheses with a single deterministic completion, use depth-only geometry, use layout-only geometry, and vary the number of hidden-scene samples. Failure criteria: lower visible_object_recall than direct single-image-to-3D baselines, increased collision_rate or out_of_room_rate, poor calibration on occluded-object existence, inability to flag mirrors/windows/extreme perspective, and no improvement in navigation_success_rate using the generated scene. MVP artifacts: a JSON scene graph schema, a visible-object lifting script, an occluded-region sampler, constraint-based rejection/reranking, renderable mesh or Gaussian preview export, and benchmark scripts comparing against Text2Room, SceneScape, and WonderJourney. Implementation plan: first build the inference scaffold from pretrained depth/layout/object modules; then fit object boxes and room planes; then sample occluded hypotheses from 3D-FRONT priors; then add physics/collision scoring; finally integrate the best-scoring scaffold with a Text2Room/SceneScape-style renderer and evaluate on synthetic and real indoor splits.

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:dust3r_2023; seed:mast3r_2024; seed:horizonnet_2019; seed:structured3d_2019; seed:3dfront_2020; seed:3dfuture_2020

---

Idea 2
Title:
Back-Projection Consistency Benchmark for Single-Image Indoor Scene Completion

Core proposal:
Construct a benchmark and method wrapper that evaluates whether a generated complete 3D indoor scene remains consistent when rendered back into the original input view and into plausible nearby views. The benchmark converts single RGB images into tasks requiring visible-object preservation, layout agreement, depth consistency, support relation correctness, collision avoidance, and calibrated warnings for ambiguous or invalid hidden regions. The minimal new module is an automatic back-projection consistency evaluator plus a lightweight reranker that selects among completions from existing single-image-to-3D baselines.

Motivation or baseline weakness:
Automatic evaluation of single-image 3D indoor generation is difficult because multiple hidden completions may be valid. Existing methods can appear plausible in a preview while changing visible objects, placing furniture outside the room, or inventing geometry inconsistent with the observed depth and layout. A benchmark centered on back-projecting generated 3D content into the original image and evaluating object/layout/depth constraints can separate image-level appeal from scene-level usability.

Mechanism or approach:
Run multiple candidate generators, including Text2Room, SceneScape, WonderJourney, image_to_3d_generation_baselines, and Indoor_NeRF_prior_methods, from the same input image and optional camera intrinsics. For each generated mesh, NeRF, or 3D Gaussian representation, render the input camera view and a small set of nearby camera perturbations. Score alignment to the original image using visible-object masks, monocular/depth priors, layout projections, and object count consistency. Score scene plausibility using support relations, object relations, collision rate, out-of-room rate, and free-space violations. For hidden areas, report uncertainty-aware metrics: do not penalize all alternative completions equally, but require that completions expose confidence_or_uncertainty and failure_warning when multiple plausible hypotheses exist or when geometry is underconstrained. Direct baselines are Text2Room, SceneScape, WonderJourney, layout_estimation_baselines, image_to_3d_generation_baselines, and monocular_depth_estimation. Transfer baselines are DUSt3R, MASt3R, NeRF, and 3D Gaussian Splatting. Borrowed components include object detectors, CLIP-like image-text similarity, scene graph evaluators, physics/collision checkers, and pretrained depth/layout predictors. The new component is a standardized scene-level consistency protocol and reranking objective rather than a new large 3D generative model.

Experiment and implementation plan:
Datasets: Structured3D and Hypersim for controlled ground truth layout/depth, 3D-FRONT/3D-FUTURE for synthetic object-grounded renderings, and ScanNet or Matterport3D for real-image validation. Metrics: image_reconstruction_lpips, visible_object_recall, object_count_accuracy, depth_error, layout_iou, object_3d_iou where ground truth is available, chamfer_distance, collision_rate, support_relation_accuracy, object_relation_accuracy, out_of_room_rate, occlusion_consistency, novel_view_consistency, confidence_calibration, ambiguity_detection, failure_detection_auc, navigation_success_rate, and embodied_task_success_rate. Ablations: evaluate without original-view back-projection, without nearby-view rendering, without physics checks, without scene graph checks, without uncertainty scoring, and with only CLIP/image similarity. Risks: benchmark metrics may favor conservative reconstructions that avoid creative completion; object detectors may miss small or unusual items; synthetic-to-real gaps may bias scores; and hidden-region ground truth is often not uniquely defined. Failure criteria: benchmark rankings disagree with human physical-plausibility judgments, methods can game the score with billboard geometry, uncertainty metrics do not correlate with failure cases, or downstream navigation does not improve when selecting high-scoring scenes. MVP artifacts: dataset splits, input-output schema, renderer adapters for mesh/NeRF/Gaussian outputs, metric code, baseline outputs for Text2Room/SceneScape/WonderJourney, and a leaderboard-style report. Implementation plan: define a common scene export format; implement camera-aligned rendering; add visible-object, layout, depth, and collision evaluators; collect baseline generations; calibrate uncertainty scoring on synthetic occlusion cases; and validate with downstream navigation or embodied-task probes.

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:nerf_2020; seed:nerfvs_2023; seed:3dgs_2023; seed:midas_2023; seed:dust3r_2023; seed:mast3r_2024; seed:structured3d_2019; seed:3dfront_2020; seed:3dfuture_2020

---

Idea 3
Title:
Layout-Locked Gaussian Scene Completion from One Indoor Image

Core proposal:
Develop a lightweight single-image indoor scene generator that initializes a renderable 3D Gaussian or mesh representation from monocular depth and room layout, then locks major layout surfaces and visible objects while completing occluded regions through constrained inpainting and object-proxy insertion. The output is a renderable scene with room layout, visible and hypothesized objects, approximate 3D positions, proxy geometry, spatial relations, material or texture estimates, uncertainty scores, and explicit failure warnings. The minimal new module is a layout-locked optimization and completion controller that prevents generative view expansion from drifting away from the input image geometry.

Motivation or baseline weakness:
Perpetual scene generation systems can drift geometrically as they synthesize new views, while radiance-field and Gaussian representations are powerful but usually require multiple posed images or optimization. A practical middle ground is to use pretrained single-image depth/layout/object priors to create a geometry scaffold, then use a fast renderable representation only for refinement and preview. Locking layout planes and visible-object anchors should improve geometric consistency, collision rates, and downstream usability without training a large 3D generative model from scratch.

Mechanism or approach:
Estimate camera intrinsics if unavailable, predict monocular depth, infer room layout planes, and segment visible objects. Back-project visible pixels into a partial point cloud, initialize 3D Gaussians or a textured mesh for observed surfaces, and fit simple object proxy meshes or retrieved 3D-FUTURE-like shapes to visible object masks. The new component is a constrained completion loop: novel candidate views are generated using Text2Room/SceneScape-style inpainting, but layout planes, visible-object anchors, free-space rays, and support/collision constraints remain fixed. Occluded regions are represented as multiple hypothesis layers with confidence values rather than one deterministic hallucination. Materials and textures are propagated from visible regions and completed with image inpainting only where geometry constraints allow. Direct baselines are Text2Room, SceneScape, WonderJourney, image_to_3d_generation_baselines, monocular_depth_estimation, and layout_estimation_baselines. Transfer baselines are 3D Gaussian Splatting, NeRF, DUSt3R, MASt3R, and Indoor_NeRF_prior_methods. Borrowed components include monocular depth estimation, progressive mesh fusion, inpainting, Gaussian rendering, object retrieval, and physics/collision checking. The novelty is the layout-locked controller and uncertainty-layered hidden completion for single RGB indoor images.

Experiment and implementation plan:
Datasets: Structured3D for layout/depth supervision, 3D-FRONT and 3D-FUTURE for object proxies and room-object priors, Hypersim for photorealistic depth/material stress tests, and ScanNet or Matterport3D for real-world robustness. Metrics: depth_error, layout_iou, object_3d_iou, chamfer_distance, collision_rate, support_relation_accuracy, object_relation_accuracy, out_of_room_rate, occlusion_consistency, visible_object_recall, novel_view_consistency, image_reconstruction_lpips, object_count_accuracy, confidence_calibration, ambiguity_detection, failure_detection_auc, navigation_success_rate, and embodied_task_success_rate. Ablations: unlock layout planes, remove visible-object anchors, replace Gaussian rendering with mesh-only fusion, remove collision/support constraints, use deterministic hidden completion, remove material propagation, and compare depth priors from monocular_depth_estimation versus DUSt3R-style initialization. Risks: single-view Gaussian initialization may create billboard artifacts; intrinsics errors can corrupt metric scale; object proxy retrieval may mismatch unusual furniture; inpainting may introduce texture-object inconsistencies; and strict layout locking can fail for non-Manhattan rooms or reflective surfaces. Failure criteria: worse novel_view_consistency than Text2Room or SceneScape, high collision_rate, poor layout_iou, visible-object deletion in input-view renders, uncalibrated confidence in heavily occluded rooms, or downstream navigation paths intersect generated objects. MVP artifacts: input image to layout/depth/object scaffold code, Gaussian or mesh initialization, constrained novel-view inpainting loop, proxy-object fitter, uncertainty map for occluded regions, render preview, and evaluation scripts. Implementation plan: first implement partial-scene initialization from pretrained depth/layout modules; next add object proxy fitting and support graph extraction; then integrate a constrained inpainting/fusion loop; then add uncertainty layers for hidden geometry; finally benchmark against Text2Room, SceneScape, WonderJourney, NeRF-style scaffold baselines, and Gaussian rendering variants.

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:3dgs_2023; seed:nerf_2020; seed:nerfvs_2023; seed:midas_2023; seed:dust3r_2023; seed:mast3r_2024; seed:horizonnet_2019; seed:structured3d_2019; seed:3dfront_2020; seed:3dfuture_2020

### Candidate B

Idea 1
Title:
Uncertainty-Aware Layout-Constrained Scene Completion from a Single RGB View

Core proposal:
Add a lightweight probabilistic room-layout and hidden-region sampler before scene completion. The module uses monocular depth, object masks, and visible wall-floor cues to predict K Manhattan or piecewise-Manhattan room-layout hypotheses and K occluded free-space masks. Each completion from Text2Room-, SceneScape-, or WonderJourney-style generation is constrained to remain inside one sampled layout, and generated objects must attach to plausible support surfaces. The method returns a small set of renderable scene hypotheses with calibrated per-region confidence rather than one deterministic mesh.

Motivation or baseline weakness:
Text2Room and SceneScape can extend a scene from one image, but occluded regions are often completed as a single overconfident hallucination, producing objects outside the room, inconsistent floor-wall support, and weak failure signaling under ambiguous layouts.

Mechanism or approach:
A layout-and-occlusion hypothesis head that takes monocular depth, visible object detections, and layout cues, then emits K room-layout hypotheses, K occluded free-space masks, and per-region uncertainty scores; no large 3D generator is trained from scratch.
Minimize visible-view reprojection and monocular depth consistency while penalizing object-room violations, unsupported objects, inter-object collisions, and overconfident predictions in unobserved regions. The layout head is supervised where Structured3D or 3D-FRONT annotations are available, and uncertainty is trained/evaluated by comparing predicted hidden-region confidence against held-out full-scene geometry. The objective reports layout IoU, visible depth error, support-relation accuracy, collision rate, out-of-room rate, occlusion consistency, and confidence calibration.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; layout_estimation_baselines; monocular_depth_estimation
Structured3D single RGB renders with room layout and depth annotations; 3D-FRONT furnished room scenes rendered as single RGB inputs with object positions and support relations; Held-out Structured3D and 3D-FRONT stress splits with narrow field of view, heavy occlusion, and non-frontal views; Camera intrinsics when available, otherwise estimated focal length with uncertainty propagated into layout hypotheses
run_single_image_baselines.py to generate Text2Room, SceneScape, WonderJourney, layout-estimation, and monocular-depth outputs under the same single-RGB input protocol; infer_depth_layout_objects.py for monocular depth, object masks, visible object list, wall-floor cues, and camera normalization; sample_occlusion_hypotheses.py for K hidden-region and room-layout hypotheses with confidence scores; constrain_scene_completion.py to clip or reject generated geometry that violates sampled room bounds or support surfaces; evaluate_scene_consistency.py for depth error, layout IoU, object 3D IoU, collision rate, support-relation accuracy, out-of-room rate, occlusion consistency, visible object recall, and confidence calibration
depth_error; layout_iou; object_3d_iou; collision_rate; support_relation_accuracy; out_of_room_rate; occlusion_consistency; visible_object_recall; confidence_calibration
Single deterministic layout instead of K layout hypotheses; No occluded-region uncertainty scores; No support-surface constraint; No object-room boundary penalty; Use monocular depth only without object detections; Replace probabilistic layout sampler with the top prediction from layout_estimation_baselines
Shuffle room-layout hypotheses across images and verify layout IoU, out-of-room rate, and collision rate degrade; Force all hidden-region confidence scores to a constant and verify confidence calibration worsens; Disable collision and room-boundary penalties and verify out-of-room rate and collision rate increase; Evaluate on heavily cropped or mirror-like rendered stress cases and verify confidence decreases rather than producing high-confidence completions
Reduce out_of_room_rate by at least 25% relative to Text2Room and SceneScape on Structured3D-derived single-view tests; Reduce collision_rate by at least 20% while maintaining visible_object_recall within 5% of the best direct baseline; Improve layout_iou by at least 0.08 absolute over image-to-3D generation baselines without layout constraints; Improve confidence_calibration for occluded-region predictions by at least 15% over deterministic confidence proxies; On cropped and high-occlusion stress splits, assign lower confidence to incorrect hidden-region completions than to correct completions in at least 75% of paired comparisons

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:3dfront_2020

Risks, controls, or fallback:
Risk: layout hypotheses may be wrong for non-Manhattan rooms or images with little floor-wall evidence. Fallback: expose the uncertainty explicitly, keep multiple low-rank scene hypotheses, and use a conservative low-confidence output when layout posterior entropy is high or when all hypotheses produce high collision or out-of-room penalties.

---

Idea 2
Title:
Object-Centric Proxy Mesh Retrieval with Physical Relation Repair

Core proposal:
Use pretrained single-image depth and object masks to lift visible objects into coarse 3D boxes, retrieve category-compatible proxy meshes from 3D-FUTURE or 3D-FRONT, and run a small relation-repair optimizer that adjusts scale, yaw, support height, and room placement while preserving 2D mask reprojection and depth ordering. Hidden objects are represented only as optional low-confidence placeholders when the room layout and visible support surfaces imply likely occluded space; otherwise the method avoids committed hallucinations.

Motivation or baseline weakness:
Single-image-to-3D scene generators often produce visually plausible previews but weak object-level geometry: furniture may float, intersect, have implausible scale, or fail to preserve visible object counts and spatial relations from the input image.

Mechanism or approach:
A relation-repair optimizer over object boxes and proxy meshes with terms for 2D reprojection, monocular depth ordering, support relations, collision avoidance, room containment, and uncertainty-aware hidden object insertion.
Given detected objects, masks, depth, and estimated room layout, optimize object pose and proxy geometry assignment to maximize visible mask and depth alignment while minimizing collision volume, unsupported-object count, out-of-room placement, and overconfident hidden object creation. Proxy retrieval is scored by category compatibility, aspect-ratio match, visible silhouette agreement, and depth-consistent scale; the repair stage refines only object pose, scale, support height, and mesh choice rather than training a new scene generator.

Experiment and implementation plan:
image_to_3d_generation_baselines; Text2Room; SceneScape; DUSt3R; MASt3R; 3D Gaussian Splatting
3D-FRONT rooms with object categories, 3D positions, layouts, and support relations; 3D-FUTURE furniture meshes and textures for proxy retrieval; Structured3D rendered single RGB images with depth and layout annotations; Held-out 3D-FRONT and Structured3D single-view splits with occluded, truncated, and cluttered furniture for external validation within the supplied evidence base
detect_and_lift_objects.py for object detection, mask extraction, depth-based 3D box initialization, and camera normalization; retrieve_proxy_meshes.py for category, aspect-ratio, and silhouette-based 3D-FUTURE or 3D-FRONT mesh retrieval; optimize_scene_relations.py for physical relation repair and uncertainty-aware hidden object placeholders; render_scene_preview.py for renderable mesh or scene-graph preview generation; evaluate_object_scene_graph.py for object 3D IoU, chamfer distance, support accuracy, object relation accuracy, collision rate, visible object recall, depth error, out-of-room rate, and confidence calibration
object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; visible_object_recall; depth_error; out_of_room_rate; confidence_calibration
No relation-repair optimizer after proxy retrieval; No collision penalty; No support-height snapping; No depth-order preservation term; Use category-average cuboids instead of retrieved proxy meshes; Always insert hidden objects without uncertainty gating
Randomly assign proxy meshes within the correct category and verify chamfer distance and object 3D IoU degrade; Randomize support relations and verify support_relation_accuracy drops; Remove visible mask reprojection terms and verify visible_object_recall and depth_error degrade; Evaluate on rendered scenes with mirrors, large occluders, or truncated furniture and verify confidence decreases when mask-depth evidence is inconsistent
Improve object_3d_iou by at least 10% relative to Text2Room or image_to_3d_generation_baselines on furnished Structured3D or 3D-FRONT renders; Reduce collision_rate by at least 30% relative to unoptimized proxy placement; Improve support_relation_accuracy by at least 15% over direct scene-generation baselines; Keep visible_object_recall at or above 90% of the object-mask detector upper bound; Hidden-object confidence should improve confidence_calibration by at least 15% relative to always-insert and never-insert deterministic proxies

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:dust3r_2023; seed:mast3r_2024; seed:3dgs_2023; seed:3dfront_2020; seed:3dfuture_2020; seed:structured3d_2019; seed:midas_2023

Risks, controls, or fallback:
Risk: retrieved proxy meshes may not match unusual furniture, and detector errors can propagate into 3D placement. Fallback: use category-level proxy cuboids with texture planes when retrieval confidence is low, preserve detector uncertainty in the scene graph, and flag scenes with inconsistent depth ordering or high residual reprojection error as low-confidence outputs.

---

Idea 3
Title:
Single-Image Scene Hypothesis Benchmark with Geometry, Relation, and Failure Calibration

Core proposal:
Construct a benchmark protocol that converts supported synthetic indoor datasets into single-RGB inputs with hidden ground truth, then evaluates each method as either one renderable scene or a distribution over renderable scene hypotheses. The new component is an evaluator, not a large model: it scores visible alignment, full-scene geometry, physical plausibility, relation correctness, occlusion consistency, and confidence calibration under controlled ambiguity levels.

Motivation or baseline weakness:
Existing single-image indoor scene generation results are difficult to compare because image-level previews can look plausible while geometry, support relations, occluded-region uncertainty, and downstream usability remain unmeasured or inconsistently measured.

Mechanism or approach:
A benchmark harness and uncertainty-aware evaluator that accepts meshes, 3D Gaussians, NeRF-style rendered depth views, or scene graphs after conversion to a common object-layout-geometry representation, then computes consistency and calibration scores using the supported metrics.
Define falsifiable evaluation as risk-sensitive scene reconstruction: reward accurate visible geometry and object relations, penalize physically impossible completions, and assign lower loss to multiple calibrated hypotheses when the hidden scene is genuinely ambiguous. The evaluator reports both best-hypothesis quality and confidence-weighted expected quality, while deterministic methods are scored with confidence marked unavailable or with a documented constant-confidence proxy.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; Indoor_NeRF_prior_methods; layout_estimation_baselines; monocular_depth_estimation; DUSt3R; 3D Gaussian Splatting; NeRF
Structured3D with rendered single RGB views, room layouts, depths, and full scene geometry; 3D-FRONT and 3D-FUTURE for furnished rooms and object-level proxy meshes; Generated ambiguity splits from Structured3D and 3D-FRONT with controlled crop, occlusion, field of view, and hidden-room extent; Held-out rendered stress splits with severe occlusion, missing intrinsics, clutter, and non-Manhattan or piecewise-Manhattan layouts where annotations are available
make_single_view_splits.py to render or select one RGB view and hide all other views during inference; convert_outputs_to_common_scene.py to normalize meshes, 3D Gaussian previews, NeRF renders, depth maps, and scene graphs into layout-object-geometry records; score_geometry_relations_uncertainty.py for depth, layout, object, relation, collision, occlusion, and calibration metrics; make_failure_splits.py for extreme clutter, narrow field of view, severe occlusion, missing intrinsics, and non-Manhattan layout stress cases; run_baseline_adapters.py to execute or import outputs from Text2Room, SceneScape, WonderJourney, NeRF-style, 3DGS-style, DUSt3R-style, layout, and monocular-depth baselines under standardized output fields
depth_error; layout_iou; object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; occlusion_consistency; novel_view_consistency; visible_object_recall; confidence_calibration
Evaluate only visible rendered alignment and compare ranking changes against full geometry and relation metrics; Remove occluded-region uncertainty scoring; Remove physical plausibility checks such as collision and support constraints; Use only visible-region metrics and ignore hidden ground truth; Score only top-1 output instead of confidence-weighted multiple hypotheses; Exclude stress splits and compare reported performance inflation
Submit ground-truth visible surfaces with randomized hidden geometry to verify occlusion_consistency and chamfer_distance catch hidden-scene errors; Submit visually aligned but collision-heavy scenes to verify collision_rate and support_relation_accuracy penalties; Submit empty-room completions to verify visible_object_recall and object_3d_iou penalize missing objects; Submit constant confidence for all hidden regions to verify confidence_calibration degrades on ambiguity-controlled splits
Benchmark rankings must show at least one statistically significant disagreement between visible-alignment-only metrics and full geometry-consistency metrics, demonstrating added diagnostic value; Evaluator should assign worse occlusion_consistency or chamfer_distance to randomized hidden geometry than to valid dataset ground truth in at least 95% of paired cases; Confidence_calibration should separate correct from incorrect hidden-region hypotheses better than constant-confidence proxies for methods that emit confidence; Physical plausibility metrics should detect collision-heavy negative controls with at least 90% precision; The benchmark must run all direct baselines on at least one Structured3D split and one 3D-FRONT furnished-room split with standardized output fields

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:nerf_2020; seed:nerfvs_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:dust3r_2023; seed:3dgs_2023; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: different methods output incompatible representations and some baselines may not expose uncertainty. Fallback: require a minimal adapter that renders depth, object masks, and scene bounds from each output; for methods without uncertainty, mark confidence as unavailable or use a documented constant-confidence proxy, and score them separately on deterministic geometry, relation, collision, and occlusion-consistency metrics.

---

## Item 11: HUM-3c96e00bd8

类型：`single_idea`

### Candidate A

Title:
Uncertainty-Gated Occlusion Hypothesis Layer for Single-Image Room Completion

Core proposal:
Add a lightweight probabilistic occlusion layer to a Text2Room-style single-image pipeline. The system first estimates visible objects, room layout, foreground masks, and monocular depth. It then constructs occlusion volumes behind foreground objects and near room boundaries, and samples K plausible scene-graph completions for hidden occupied and empty space. Each hypothesis is scored using geometric feasibility, support and containment relations, collision checks, visible-image reprojection consistency, and a learned or calibrated confidence estimate. The final output keeps visible regions fixed while representing occluded regions as weighted alternatives instead of one overconfident mesh.

Motivation or baseline weakness:
Text2Room, SceneScape, and WonderJourney can expand a room from one image, but they often commit to a single completion for unobserved space. This can produce unsupported or duplicated furniture, geometry outside the room, and poorly calibrated confidence in regions that are genuinely ambiguous from a single RGB view.

Mechanism or approach:
An occlusion-volume-to-scene-graph sampler with a confidence calibration head. It reuses pretrained depth, detection, layout, and rendering components, avoiding the need to train a large 3D scene generator from scratch.
Optimize visible consistency and plausible hidden completion while discouraging physically invalid or overconfident predictions: L = L_visible_reprojection + L_depth_consistency + L_layout + L_relation + L_collision + L_out_of_room + L_calibration. The calibration term penalizes high confidence when multiple hidden-region hypotheses remain plausible.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; layout_estimation_baselines; monocular_depth_estimation
Single RGB indoor images with camera intrinsics when available; 3D-FRONT/3D-FUTURE rendered single-view rooms with full hidden-object ground truth; Structured3D or Hypersim for layout and depth supervision; ScanNet or Matterport3D single-view crops for real-image validation
run_single_image_baselines.py for Text2Room, SceneScape, and WonderJourney comparisons; extract_visible_objects_layout_depth.py using object detection, room layout estimation, and monocular depth; build_occlusion_volumes.py from depth discontinuities, foreground masks, and room layout planes; sample_uncertain_scene_graphs.py for K hidden-region hypotheses; evaluate_geometry_relations_uncertainty.py for layout, object, collision, occlusion, and calibration metrics
depth_error; layout_iou; object_3d_iou; chamfer_distance; collision_rate; out_of_room_rate; support_relation_accuracy; object_relation_accuracy; occlusion_consistency; visible_object_recall; object_count_accuracy; confidence_calibration; ambiguity_detection; failure_detection_auc
Remove occlusion-volume reasoning and sample hidden objects only from global room priors; Replace the multi-hypothesis output with the single highest-scoring completion; Remove the calibration loss while keeping the same hypothesis sampler; Remove collision and support-relation scoring; Use visible-object detections without room-layout constraints
Sample hidden objects uniformly from 3D-FRONT category frequencies without conditioning on the input image; Assign uniformly high confidence to all occluded hypotheses regardless of ambiguity; Place hidden objects using only 2D image-space proximity without 3D room constraints; Evaluate images with little or no major occlusion, where uncertainty should collapse to low entropy
Reduce collision_rate by at least 25% relative to a Text2Room-style completion at matched visible_object_recall; Improve occlusion_consistency by at least 10% over single-hypothesis SceneScape or WonderJourney outputs on held-out synthetic rooms; Improve confidence_calibration ECE by at least 20% for hidden-object existence and 3D placement; Maintain visible_object_recall within 3 percentage points of the best direct baseline; Failure criterion: if uncertainty does not correlate with hidden-region error better than baseline confidence scores, the mechanism is not supported

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023

Risks, controls, or fallback:
Risk: hidden-object supervision from synthetic data may not transfer cleanly to real indoor images. Fallback: report synthetic and real-image results separately, use real-image human or VLM plausibility checks only as secondary evidence, and, if category prediction is unreliable, restrict the module to calibrated occupied-versus-empty uncertainty over occlusion volumes.

### Candidate B

Title:
Uncertainty-Gated Occlusion Hypothesis Layer for Single-Image Room Completion

Core proposal:
Add a lightweight probabilistic occlusion hypothesis layer on top of a Text2Room-style single-image pipeline. From the input RGB image, estimate visible layout, visible object masks or boxes, and monocular depth; construct occlusion volumes from depth discontinuities, foreground masks, room-boundary rays, and unobserved frustum cells; then sample K scene-graph hypotheses over hidden occupied or empty regions. Each hypothesis is scored by room containment, object-size priors, support feasibility, pairwise collision checks, consistency with visible reprojection, and a confidence head calibrated against whether the hidden-region hypothesis matches held-out synthetic ground truth. Visible surfaces from the baseline reconstruction are kept fixed except for small depth/layout alignment corrections, while occluded regions are represented as weighted alternatives rather than a single mesh completion.

Motivation or baseline weakness:
Text2Room, SceneScape, and WonderJourney can expand a scene from one image, but hidden regions are often filled as a single confident completion, causing unsupported objects, duplicate furniture, out-of-room geometry, and poor calibration under single-image ambiguity.

Mechanism or approach:
A small occlusion-volume-to-scene-graph sampler plus confidence calibration head. It consumes outputs from pretrained monocular depth, layout estimation, object-mask extraction, and an existing Text2Room/SceneScape/WonderJourney-style mesh construction pipeline; it does not train a large 3D generator from scratch.
Optimize hypothesis weights and hidden-object parameters with L = L_visible_reprojection + L_depth_consistency + L_layout + L_relation + L_collision + L_room_containment + L_calibration. The visible losses constrain the reconstruction to the input image, relation/collision/containment losses score physical plausibility in 3D, and the calibration term penalizes high confidence when multiple hidden completions remain compatible with the visible evidence.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; layout_estimation_baselines; monocular_depth_estimation; 3D-FRONT
Single RGB indoor images with camera intrinsics when available; 3D-FRONT/3D-FUTURE rendered single-view rooms with full hidden-object, layout, and relation ground truth; Structured3D rendered views for layout and depth supervision; Held-out real single RGB indoor images used only for qualitative validation and visible-region metrics when full hidden ground truth is unavailable
run_single_image_baselines.py for Text2Room, SceneScape, and WonderJourney comparisons under identical single-image input assumptions; extract_visible_objects_layout_depth.py to produce visible masks or boxes, room-layout planes, and monocular depth maps; build_occlusion_volumes.py to mark unobserved cells from depth discontinuities, visible masks, camera rays, and room layout; sample_uncertain_scene_graphs.py to sample K hidden empty/occupied/object hypotheses with weights; score_and_calibrate_hypotheses.py to compute relation, collision, containment, reprojection, and confidence terms; evaluate_geometry_relations_uncertainty.py for layout, object, collision, occlusion, and calibration metrics
depth_error; layout_iou; object_3d_iou; chamfer_distance; collision_rate; out_of_room_rate; support_relation_accuracy; object_relation_accuracy; occlusion_consistency; visible_object_recall; confidence_calibration
Remove occlusion-volume reasoning and sample hidden objects from global 3D-FRONT category and size priors only; Replace multi-hypothesis output with the top-1 completion while keeping the same sampler; Remove calibration loss while keeping identical geometric scoring; Remove collision and support-relation scoring from hypothesis ranking; Use visible-object evidence only without room-layout containment constraints
Sample hidden objects uniformly from 3D-FRONT category frequencies without conditioning on the input image; Assign uniformly high confidence to every occluded hypothesis regardless of ambiguity; Place hidden objects using 2D image-space proximity only, without 3D room layout or depth constraints; Evaluate on synthetic views with minimal occlusion where calibrated uncertainty should collapse to low entropy; Shuffle occlusion-volume labels before sampling to verify the sampler depends on geometric visibility rather than dataset priors alone
Reduce collision_rate by at least 25% relative to the strongest Text2Room-style single-hypothesis completion at matched visible_object_recall; Improve occlusion_consistency by at least 10% over single-hypothesis SceneScape/WonderJourney outputs on held-out synthetic rooms; Improve confidence_calibration ECE by at least 20% for hidden occupancy and hidden-object placement confidence; Maintain visible_object_recall within 3 percentage points of the best direct baseline; Failure criterion: if uncertainty does not correlate with hidden-region error better than baseline confidence or entropy scores, the occlusion hypothesis mechanism is not supported

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: hidden-object supervision from synthetic rooms may not transfer to real indoor images, and category-level hidden-object prediction may be underdetermined from a single RGB view. Fallback: report synthetic hidden-region results separately from real-image visible-region checks, expose uncertainty over empty versus occupied occlusion volumes even when category labels are unreliable, and treat human or VLM plausibility checks as secondary diagnostics rather than primary evidence.

---

## Item 12: HUM-85c40087d9

类型：`portfolio`

### Candidate A

Idea 1
Title:
Uncertainty-Aware Layout-to-Object Scene Graph Completion for Single-Image Indoor 3D Generation

Core proposal:
A scene-level pipeline that converts one RGB image into a renderable 3D indoor scene by first estimating visible geometry and room layout, then completing a probabilistic 3D scene graph with explicit hypotheses for occluded regions. Task type: generative_modeling, single_image_3d_generation, geometry_consistency. Direct baselines: Text2Room, SceneScape, WonderJourney, image_to_3d_generation_baselines, layout_estimation_baselines. Transfer baselines: monocular_depth_estimation, DUSt3R, MASt3R, NeRFVS-style geometry scaffolds. Borrowed components: pretrained monocular depth, object detector/segmenter, room layout estimator, 3D-FRONT/3D-FUTURE object priors, physics or collision checker, CLIP/image alignment scoring. New component: a lightweight probabilistic scene-graph completion module that predicts distributions over hidden objects, support relations, object poses, and room-zone occupancy, rather than a single deterministic completion.

Motivation or baseline weakness:
Single-image indoor 3D reconstruction is fundamentally ambiguous behind visible furniture, around corners, and under occlusion. Existing perpetual generation methods can produce plausible textured scenes but often lack calibrated uncertainty, explicit object-level support relations, and failure warnings. The key novelty is to make hidden scene completion a constrained probabilistic inference problem over a room-layout-conditioned object graph, producing multiple physically checked hypotheses with confidence scores instead of one overconfident mesh.

Mechanism or approach:
Implementation plan: (1) estimate camera intrinsics if missing, monocular depth, visible object masks, and a room layout cuboid or Manhattan layout; (2) lift visible masks into approximate 3D object boxes/proxy meshes using depth and category priors; (3) construct a partial scene graph with nodes for walls, floor, ceiling, visible objects, and uncertain occluded zones; (4) use a lightweight graph diffusion or autoregressive graph sampler trained/fine-tuned on 3D-FRONT, Structured3D, ScanNet, Matterport3D, and Hypersim metadata to propose hidden objects and relations; (5) retrieve category-matched CAD/proxy meshes from 3D-FUTURE or generate simple box/superquadric proxies; (6) optimize object poses under floor support, wall containment, collision, visibility, and observed-mask reprojection constraints; (7) assign textures from the RGB image for visible surfaces and plausible material priors for hidden surfaces; (8) export a renderable scene graph plus mesh/3D Gaussian preview with per-object uncertainty and failure warnings. Minimal new module: the probabilistic graph completion and calibration head; all perception and rendering components can use pretrained or off-the-shelf models. MVP artifacts: a JSON scene graph schema, Blender/USD/glTF export, preview renderer, uncertainty heatmap over hidden room cells, and a benchmark script. Ablations: no hidden-object uncertainty, deterministic graph completion, no physics constraints, no layout conditioning, no visible-mask reprojection loss, CAD retrieval versus box proxies, one hypothesis versus top-k hypotheses. Risks: room layout errors can propagate, CAD retrieval may mismatch real furniture, uncertainty may be poorly calibrated under domain shift, and hidden objects may be evaluated unfairly when many completions are plausible. Failure criteria: high visible-object miss rate, collision_rate above baseline, out_of_room_rate not improved, confidence_calibration worse than deterministic baselines, or failure_detection_auc near random.

Experiment and implementation plan:
Datasets: train/validate graph priors on 3D-FRONT/3D-FUTURE and Structured3D; evaluate on held-out Structured3D, Hypersim, ScanNet, and Matterport3D single-view renders. Metrics: depth_error, layout_iou, object_3d_iou for visible objects, chamfer_distance for geometry, collision_rate, support_relation_accuracy, object_relation_accuracy, out_of_room_rate, occlusion_consistency, visible_object_recall, object_count_accuracy, novel_view_consistency, image_reconstruction_lpips, confidence_calibration, ambiguity_detection, failure_detection_auc, and downstream navigation_success_rate in simulated scenes. Compare against Text2Room, SceneScape, WonderJourney, layout_estimation_baselines plus monocular_depth_estimation, DUSt3R/MASt3R geometry, and a deterministic scene-graph completion baseline. Main claims are supported if the method improves collision_rate, support_relation_accuracy, out_of_room_rate, visible_object_recall, and uncertainty calibration while preserving comparable image alignment.

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:dust3r_2023; seed:mast3r_2024; seed:3dfront_2020; seed:3dfuture_2020

---

Idea 2
Title:
Self-Checking Perpetual View Expansion with Differentiable Scene-Consistency Gates

Core proposal:
A single-image-to-3D indoor scene generator that wraps perpetual view generation with differentiable and symbolic consistency gates before fusing each newly hallucinated view into the 3D scene. Task type: single_image_3d_generation, geometry_consistency, metric_improvement. Direct baselines: Text2Room, SceneScape, WonderJourney, Indoor_NeRF_prior_methods, image_to_3d_generation_baselines. Transfer baselines: monocular_depth_estimation, DUSt3R, MASt3R, 3D Gaussian Splatting, NeRF. Borrowed components: pretrained image inpainting/generation, depth estimation, view selection, mesh or Gaussian fusion, CLIP/VLM verification, object detection, and physics/collision checking. New component: a scene-consistency gate that scores each proposed novel view for geometric compatibility, object persistence, support plausibility, layout containment, and uncertainty expansion before accepting it into the global scene representation.

Motivation or baseline weakness:
Perpetual room generation can expand a single image into a complete scene, but errors introduced early are often fused permanently, causing warped layouts, duplicated furniture, inconsistent object identities, and physically impossible placements. The novelty is not another large 3D generator, but a lightweight accept/reject/refine controller that treats generation as sequential hypothesis testing under explicit 3D scene constraints.

Mechanism or approach:
Implementation plan: (1) initialize a partial 3D mesh or Gaussian scene from the input RGB image using monocular depth and estimated layout; (2) choose next camera views that expose high-uncertainty or occluded regions while staying inside the estimated room; (3) generate or inpaint each target view using a Text2Room/SceneScape/WonderJourney-like module conditioned on the current render, depth, object labels, and scene graph memory; (4) estimate depth and object masks for the generated view; (5) evaluate consistency gates: reprojection agreement with already fused surfaces, object identity persistence, floor/wall support, no severe collision, no out-of-room geometry, plausible occlusion ordering, and material continuity; (6) accept, locally refine, or resample the view; (7) fuse accepted views into a mesh or 3D Gaussian representation with confidence weights; (8) export a renderable scene plus failure warnings for regions with repeated gate rejection. Minimal new module: the gate controller and confidence-weighted fusion rules; no large 3D generative model needs to be trained from scratch. MVP artifacts: a wrapper around an existing perpetual generation baseline, gate logs, accepted/rejected view visualizations, renderable mesh/3DGS preview, and per-region uncertainty map. Ablations: all gates disabled, geometry-only gate, object-only gate, physics-only gate, no uncertainty-guided viewpoint selection, mesh fusion versus 3D Gaussian fusion, single sample versus resampling on gate failure. Risks: gates may over-reject creative but valid completions, pretrained depth may be unreliable on generated views, VLM/CLIP checks may miss geometry errors, and repeated resampling may increase runtime. Failure criteria: lower novel_view_consistency than the wrapped baseline, no reduction in collision_rate or out_of_room_rate, degraded visible_object_recall, excessive rejected-view rate, or uncalibrated confidence in hidden regions.

Experiment and implementation plan:
Datasets: use single-view starts from Structured3D, Matterport3D, ScanNet, and Hypersim with held-out ground-truth geometry and novel views where available; use 3D-FRONT/3D-FUTURE synthetic rooms for controlled object-level relation evaluation. Metrics: depth_error on visible and generated views, layout_iou, chamfer_distance, object_3d_iou, collision_rate, support_relation_accuracy, object_relation_accuracy, out_of_room_rate, occlusion_consistency, visible_object_recall, object_count_accuracy, novel_view_consistency, image_reconstruction_lpips, confidence_calibration, failure_detection_auc, and downstream navigation_success_rate. Compare: original Text2Room/SceneScape/WonderJourney-style generation, the same generator with random view expansion, generator plus CLIP-only verification, generator plus geometry-only checking, and the full gate controller. A publishable result would show that consistency-gated fusion reduces geometric and relational failures without sacrificing photorealistic previews.

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:3d_scenedreamer_2024; seed:nerf_2020; seed:nerfvs_2023; seed:midas_2023; seed:dust3r_2023; seed:mast3r_2024; seed:3dgs_2023

---

Idea 3
Title:
Ambiguity-Bench: A Benchmark and Metric Suite for Single-Image 3D Indoor Scene Completion

Core proposal:
A benchmark construction proposal focused on evaluating complete 3D indoor scene generation from one RGB image under hidden-region ambiguity. Task type: benchmark_construction, metric_improvement, geometry_consistency. Direct baselines: Text2Room, SceneScape, WonderJourney, layout_estimation_baselines, image_to_3d_generation_baselines. Transfer baselines: monocular_depth_estimation, DUSt3R, MASt3R, NeRF, 3D Gaussian Splatting. Borrowed components: synthetic single-view rendering from 3D-FRONT, Structured3D, and Hypersim; real scans from ScanNet and Matterport3D; object detectors; scene graph evaluators; physics/collision checkers; CLIP/image alignment tools. New component: an ambiguity-aware evaluation protocol that scores both deterministic outputs and distributions of plausible hidden completions using visible-region fidelity, constraint satisfaction, calibrated uncertainty, and downstream usability.

Motivation or baseline weakness:
Current evaluations often overemphasize image-level quality or novel-view appearance while undermeasuring object-level 3D placement, support relations, occlusion consistency, and calibrated failure warnings. For single-image scenes, hidden regions may have many valid completions, so a benchmark should not penalize plausible alternatives as harshly as visible-region mistakes. The novelty is a benchmark that separates observable correctness from hidden-region plausibility and explicitly evaluates uncertainty.

Mechanism or approach:
Implementation plan: (1) render many single RGB images from indoor datasets with full 3D ground truth, visible masks, object identities, camera intrinsics, room layouts, and depth; (2) annotate each sample with ambiguity factors such as visible floor area, occlusion ratio, mirror/window presence, narrow field of view, object truncation, and layout uncertainty; (3) define required output schema with estimated_room_layout, object_instances, object_3d_positions, object_geometry_or_proxy_meshes, spatial_relations, occluded_region_hypotheses, materials_or_textures, render_or_preview, confidence_or_uncertainty, and failure_warning; (4) add validators for geometry, scene graph, physical plausibility, and renderability; (5) support top-k or distributional submissions so hidden-region hypotheses can be scored by best-of-k plausibility plus calibration; (6) create baseline wrappers for Text2Room, SceneScape, WonderJourney, monocular-depth lifting, DUSt3R/MASt3R-assisted pseudo-geometry, and layout-only reconstruction; (7) release leaderboard slices by room type, occlusion level, layout ambiguity, and downstream task. Minimal new module: dataset conversion, output validator, metric suite, and ambiguity stratification labels. MVP artifacts: benchmark dataset subset, evaluation server/local evaluator, baseline outputs, scene schema, and a paper analyzing failure modes. Ablations: visible-only metrics versus full-scene metrics, deterministic versus top-k scoring, no ambiguity stratification, no physics metrics, no uncertainty calibration metrics, synthetic-only versus real-scan evaluation. Risks: ground truth hidden regions are only one possible completion, real scans may lack clean materials or complete meshes, baseline wrappers may require non-identical assumptions, and automatic plausibility metrics can be gamed. Failure criteria: metrics fail to distinguish obvious collisions or missing visible objects, rankings are dominated by dataset bias, uncertainty scores do not correlate with actual error, or downstream navigation success does not correlate with proposed scene metrics.

Experiment and implementation plan:
Datasets: construct benchmark splits from 3D-FRONT/3D-FUTURE, Structured3D, Hypersim, ScanNet, and Matterport3D. Metrics: geometry_quality includes depth_error, layout_iou, object_3d_iou, chamfer_distance, and collision_rate; scene_consistency includes support_relation_accuracy, object_relation_accuracy, out_of_room_rate, and occlusion_consistency; image_alignment includes visible_object_recall, object_count_accuracy, novel_view_consistency, and image_reconstruction_lpips; uncertainty includes confidence_calibration, ambiguity_detection, and failure_detection_auc; downstream includes navigation_success_rate and embodied_task_success_rate. Baselines: Text2Room, SceneScape, WonderJourney, layout_estimation_baselines, image_to_3d_generation_baselines, monocular_depth_estimation plus object lifting, DUSt3R/MASt3R pseudo-geometry, and simple 3D-FRONT retrieval by detected room/object categories. Main experiment: report baseline rankings by visible fidelity, hidden plausibility, physics consistency, uncertainty calibration, and downstream usefulness; analyze failure cases such as mirrors, heavy occlusion, non-Manhattan layouts, unusual furniture, missing intrinsics, and object truncation.

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:dust3r_2023; seed:mast3r_2024; seed:nerf_2020; seed:3dgs_2023; seed:3dfront_2020; seed:3dfuture_2020

### Candidate B

Idea 1
Title:
Uncertainty-Aware Occluded Room Completion via Layout-Constrained Hypothesis Sets

Core proposal:
Add a lightweight hypothesis sampler that generates K layout and hidden-object scene-graph completions conditioned only on the input RGB-derived visible layout cues, monocular depth, visible object detections, and support relations. Each hypothesis is scored by explicit layout containment, object collision, floor/wall support, visible reprojection, and depth consistency checks; the method returns a ranked hypothesis set with calibrated existence probabilities instead of collapsing ambiguity to one completion.

Motivation or baseline weakness:
Text2Room and SceneScape can extend an indoor scene from one image, but occluded regions are often represented as a single confident continuation. This can create impossible room extents, unsupported hidden furniture, poor containment, and uncalibrated hidden-object predictions.

Mechanism or approach:
A layout-object hypothesis head that outputs K scene-graph completions with per-object existence probability, 3D box mean and covariance, support target, occlusion state, and hypothesis weight. It reuses pretrained depth, layout, detector, and image-to-3D modules as frozen components and trains only the small hypothesis head plus calibration parameters.
Train on synthetic single-view renders by minimizing a mixture objective: visible-mask reprojection loss, visible-depth consistency loss, layout boundary violation, pairwise object collision penalty, unsupported-object penalty, out-of-room penalty, and negative log likelihood of ground-truth hidden layout/object annotations under the K-hypothesis distribution. Calibrate hidden-object existence and room-extent probabilities with a held-out validation split.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; layout_estimation_baselines; monocular_depth_estimation
Structured3D single-view RGB renders with ground-truth layout, camera intrinsics, and depth; 3D-FRONT furnished room renders with 3D boxes, support relations, room boundaries, and occlusion masks; 3D-FUTURE object meshes and textures for proxy geometry attached to sampled boxes; Held-out synthetic stress split with high occlusion, mirrors of layouts, and nonstandard object arrangements
single_view_render_export.py to create RGB, depth, camera intrinsics, visible masks, occlusion masks, and ground-truth scene graphs; run_baselines_text2room_scenescape.py to generate baseline mesh or scene outputs from the same input image and fixed camera intrinsics; fit_layout_depth_objects.py to estimate visible layout planes, object boxes, and monocular depth priors from the single RGB image; sample_occluded_hypotheses.py to produce K weighted scene-graph completions with uncertainty fields; evaluate_geometry_relations_uncertainty.py to compute layout, object, collision, support, occlusion, and calibration metrics
layout_iou; depth_error; object_3d_iou; collision_rate; out_of_room_rate; support_relation_accuracy; object_relation_accuracy; occlusion_consistency; visible_object_recall; confidence_calibration
Remove multi-hypothesis sampling and keep only the maximum-probability completion; Remove collision and support filters while keeping the same sampler; Remove layout containment constraints and allow unconstrained hidden-region expansion; Use monocular depth only without detected object categories and relation cues; Vary K hypotheses in {1,3,5,10} to measure ambiguity coverage versus false-positive hidden objects
Shuffle visible object categories before hypothesis sampling while preserving boxes and masks; Use random room layout priors with the same object sampler and calibration procedure; Evaluate on deliberately inconsistent indoor images with impossible visible depth-layout alignment and require low confidence rather than confident completion; Replace support labels with random floor, wall, and object attachments during validation to test support-relation sensitivity
Reduce collision_rate by at least 25% relative to Text2Room or SceneScape on 3D-FRONT synthetic single-view tests; Improve layout_iou by at least 0.05 over the best direct single-image scene baseline using the same camera intrinsics; Reduce expected calibration error for hidden object existence by at least 15% relative to single-hypothesis completion; Maintain visible_object_recall within 95% of the best direct baseline while improving occlusion_consistency; Assign low calibrated confidence to at least 80% of severe ambiguity or inconsistent-layout cases at a fixed 10% false-alarm rate on valid cases

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: hypothesis sampling may improve uncertainty and relations without improving textured mesh quality. Fallback: output an uncertainty-annotated scene graph plus proxy boxes for occluded regions, and instantiate 3D-FUTURE proxy meshes only for high-confidence objects while leaving low-confidence regions as explicit uncertain volumes.

---

Idea 2
Title:
Relation-Verified Object Proxy Insertion for Physically Plausible Single-Image Scenes

Core proposal:
Insert a relation-verification loop after a baseline scene output is produced. The loop detects visible objects, estimates room layout and depth from the input image, retrieves category-compatible proxy meshes, initializes 3D boxes from visible masks and depth, and optimizes object transforms under explicit floor/wall support, inter-object collision, room containment, and visible-mask reprojection constraints. If no low-energy solution exists, the system returns a low-confidence or partial scene rather than a physically inconsistent completion.

Motivation or baseline weakness:
Image-to-3D scene baselines can produce plausible render previews while violating physical relations: furniture floats, penetrates walls, leaves the room volume, or contradicts visible support and adjacency cues. NeRF and 3D Gaussian Splatting are included only as renderable-scene representations when initialized or adapted from the same single-RGB protocol, not as inherently single-image completion methods.

Mechanism or approach:
A scene-graph relation optimizer that adjusts object 3D position, scale, yaw, and support attachment for generated or retrieved proxy meshes while preserving the baseline-generated visible appearance through fixed masks, texture anchors, and reprojection constraints.
Minimize a weighted constrained energy over object transforms and support assignments: 2D mask reprojection error, monocular depth residual inside visible masks, deviation from category-specific 3D box priors, object-object collision volume, wall/floor penetration, room-boundary containment, support-plane distance, and support-relation classification loss. Reject or mark outputs uncertain when optimized energy remains above a validation-calibrated threshold.

Experiment and implementation plan:
Text2Room; SceneScape; image_to_3d_generation_baselines; 3D Gaussian Splatting; NeRF; monocular_depth_estimation
3D-FRONT scenes with object boxes, room layouts, and support relations; 3D-FUTURE meshes and textures for proxy object geometry; Structured3D room layouts, depth annotations, and rendered single RGB images; Synthetic validation splits with controlled collisions, floating objects, wall penetrations, and missing support labels
detect_visible_objects.py to produce masks, classes, and confidence scores from the single RGB input; estimate_depth_layout.py to produce monocular depth and room boundary planes; retrieve_proxy_meshes.py to map detected object categories to approximate 3D-FUTURE meshes and category-size priors; optimize_scene_relations.py to solve object transforms, room containment, and support constraints; render_preview_and_scene_graph.py to export a renderable proxy scene and relation graph; evaluate_physical_consistency.py to compute collision, support, out-of-room, object, depth, and visible-recall metrics
collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; visible_object_recall; object_3d_iou; depth_error; layout_iou; novel_view_consistency; confidence_calibration
No relation optimizer after baseline scene generation; Collision-only optimizer without support constraints; Support-only optimizer without collision constraints; Use category-average boxes instead of retrieved proxy meshes; Disable rejection and always output a scene even when constraint energy is high
Randomize support labels while preserving object detections and room layout; Optimize object transforms against a shuffled depth map from another room; Use an empty-room layout with object detections removed to verify that visible_object_recall depends on image evidence; Swap room boundaries between scenes while keeping object masks fixed to test containment sensitivity
Reduce collision_rate by at least 30% over direct image-to-3D scene baselines on 3D-FRONT single-view renders; Reduce out_of_room_rate by at least 40% without decreasing visible_object_recall by more than 5%; Improve support_relation_accuracy by at least 10 percentage points over the best baseline scene graph extracted from generated geometry; Keep depth_error and layout_iou no worse than the unoptimized baseline by more than 5% relative on visible regions; Improve confidence_calibration for rejected or low-confidence physically inconsistent cases relative to always-output baselines

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:3d_scenedreamer_2024; seed:3dgs_2023; seed:nerf_2020; seed:midas_2023; seed:3dfront_2020; seed:3dfuture_2020; seed:structured3d_2019

Risks, controls, or fallback:
Risk: proxy retrieval may reduce visual realism when CAD assets mismatch the photo or generated texture. Fallback: keep baseline textures as fixed appearance anchors or textured billboards, use proxy meshes only for physics and relations, and evaluate the contribution primarily as a downstream-usable collision-aware scene graph rather than a photorealistic reconstruction.

---

Idea 3
Title:
Single-Image Scene Completion Benchmark with Ambiguity-Aware Failure Scoring

Core proposal:
Construct a controlled benchmark from synthetic indoor rooms rendered from one camera, with ground-truth visible geometry, hidden object annotations, room layout, relations, and ambiguity labels derived from groups of similar room configurations. Standardized adapters convert renderable scenes, meshes, radiance fields, pointmaps, or scene graphs into a common representation so metrics can separately score visible reconstruction, hidden completion, physical validity, uncertainty calibration, and failure awareness.

Motivation or baseline weakness:
Existing single-image scene generation and reconstruction papers are difficult to compare because visual quality, geometry consistency, hidden-region plausibility, physical relations, and failure awareness are often evaluated with different inputs and output formats. Multi-view reconstruction methods such as DUSt3R, MASt3R, NeRF, and NeRFVS must therefore be clearly separated from true single-RGB completion methods or run only under controlled adapter settings.

Mechanism or approach:
A benchmark adapter that converts each method output into a common scene-level representation with layout planes, object boxes or meshes, spatial relations, uncertainty fields when available, render previews, and confidence or failure_warning scores. Methods without uncertainty must expose a deterministic confidence proxy so calibration can be evaluated but not confused with true probabilistic completion.
No large training objective is introduced; the core contribution is standardized measurement. For optional reporting, learn only a lightweight validation-set failure-warning calibrator from method diagnostics such as depth residual, collision count, out-of-room count, layout confidence, and hidden-area fraction, and report calibrated and uncalibrated scores separately.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; Indoor_NeRF_prior_methods; layout_estimation_baselines; DUSt3R; MASt3R; monocular_depth_estimation
3D-FRONT rooms paired with 3D-FUTURE object meshes and textures; Structured3D images with room layout and depth annotations; Rendered single RGB inputs with camera intrinsics, depth, segmentation, visible-object lists, hidden-object lists, room boundaries, and relation graphs; Controlled ambiguity groups formed by matching room type, visible layout, and visible object evidence but varying plausible hidden objects
render_single_view_benchmark.py to generate benchmark images and annotations from fixed camera protocols; standardize_scene_output.py to convert mesh, NeRF-style, Gaussian-style, pointmap, or scene-graph outputs into a common schema; evaluate_layout_geometry.py for layout_iou, depth_error, chamfer_distance, and object_3d_iou; evaluate_relations_physics.py for collision_rate, support_relation_accuracy, object_relation_accuracy, and out_of_room_rate; evaluate_occlusion_uncertainty.py for occlusion_consistency, hidden-object calibration, and confidence calibration; run_negative_controls.py to submit randomized, image-only, overconfident, and empty-room controls through the same adapters
depth_error; layout_iou; object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; occlusion_consistency; visible_object_recall; novel_view_consistency; confidence_calibration
Evaluate with and without supplied camera intrinsics to quantify calibration dependence; Evaluate visible regions separately from occluded regions; Score single best completion versus top-K uncertain hypotheses when a method provides multiple completions; Compare mesh-based, NeRF-based, Gaussian-style, pointmap, and scene-graph-only outputs through the same adapter; Remove physics and relation checks to show whether image and depth metrics alone miss implausible scenes
Submit ground-truth layout with randomized objects to expose relation and collision metric sensitivity; Submit visually plausible 2D inpainted panoramas with no valid 3D geometry to test geometry gates; Submit overconfident hidden-object predictions on ambiguous rooms to test calibration penalties; Submit empty-room completions to test visible_object_recall and object_3d_iou; Submit shuffled camera intrinsics to test whether methods and adapters depend on correct single-view geometry
Benchmark ranks ground-truth scenes best on at least 90% of geometry and relation metrics; Physics and relation metrics assign worse scores to randomized-object negative controls than to valid ground truth in at least 85% of benchmark scenes; Image-only or panorama-only controls must not score highly on depth_error, chamfer_distance, object_3d_iou, or novel_view_consistency without valid 3D geometry; Top-K uncertainty scoring rewards calibrated ambiguous completions over overconfident single completions on hidden regions according to confidence_calibration and occlusion_consistency; At least three direct baselines can be run end-to-end and exported into the common schema under the single-RGB protocol

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:nerfvs_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:dust3r_2023; seed:mast3r_2024; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: automatic evaluation may still miss human notions of plausibility. Fallback: report separate geometry, relation, image-alignment, occlusion, and calibration axes instead of a single leaderboard score, and include curated failure-case subsets for manual review while keeping all quantitative metrics reproducible.

---

## Item 13: HUM-0da5f298a0

类型：`single_idea`

### Candidate A

Title:
Single-Image Scene Completion Benchmark with Ambiguity-Stratified Evaluation

Core proposal:
Construct an ambiguity-stratified benchmark from evidence-supported indoor datasets by rendering single RGB views with known camera intrinsics, full 3D ground truth, visible and hidden object labels, layout annotations, and derived sets of physically plausible alternative hidden completions. Evaluate methods with separate visible-region reconstruction scores, hidden-region plausibility scores, physical relation checks, uncertainty calibration, and compliance labels indicating whether each method used only the single RGB input.

Motivation or baseline weakness:
Existing single-image-to-3D room methods are hard to compare because image-level preview quality can hide geometry errors, occluded regions are inherently multi-modal, and some baselines use extra prompts, generated views, camera paths, or iterative exploration that violate a strict single-RGB input protocol.

Mechanism or approach:
A dataset-generation and evaluator layer that labels each test view by occlusion fraction, layout visibility, object truncation, visible-object count, hidden-object count, and physical-constraint difficulty. It also defines a standardized JSON scene-graph schema for method outputs, including camera, layout, objects, support relations, uncertainty fields, and confidence values.
Define an evaluation score that rewards visible-image-grounded geometry and physically valid scene structure while avoiding over-penalization of ambiguous hidden regions. Visible regions are scored against ground truth, while hidden completions are scored using plausibility sets, support and collision validity, calibrated uncertainty, and consistency with visible free space. Scores are always reported by ambiguity stratum and by input-protocol compliance.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; Indoor_NeRF_prior_methods; layout_estimation_baselines; image_to_3d_generation_baselines; monocular_depth_estimation; DUSt3R; MASt3R; NeRF
3D-FRONT furnished rooms with 3D-FUTURE assets; Structured3D scenes with layout and structure annotations; Rendered single RGB images with camera intrinsics; Ground-truth room layouts, object poses, meshes, materials, and visibility masks from rendered scenes; Derived visible/hidden masks, free-space masks, support relations, and collision annotations; Optional method-native diagnostic inputs recorded separately from the strict single-RGB benchmark track
render_single_view_benchmark.py; compute_visible_hidden_masks.py; generate_ambiguity_labels.py; derive_plausible_hidden_completion_sets.py; convert_outputs_to_scene_schema.py; check_input_protocol_compliance.py; evaluate_geometry_consistency.py; evaluate_scene_relations.py; evaluate_uncertainty_calibration.py; baseline_runner_wrappers.py
depth_error; layout_iou; object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; occlusion_consistency; visible_object_recall; novel_view_consistency; confidence_calibration
Score hidden regions deterministically against one ground-truth completion; Remove ambiguity stratification; Remove physics and collision checks from the benchmark score; Evaluate only depth_error and novel_view_consistency; Use no standardized scene-graph schema; Do not separate visible and occluded objects; Ignore input-protocol compliance when comparing methods
Submit ground-truth visible geometry with random hidden objects; Submit visually plausible 2D inpainted views with no valid 3D scene graph; Submit empty-room completions to test whether metrics penalize missing objects; Submit overconfident confidence maps for all hidden regions; Submit a method-native run that uses extra views or prompts and mark it as non-strict to test protocol reporting
Baseline ranking changes when geometry, relation, and uncertainty metrics are added compared with novel_view_consistency-only evaluation; The evaluator penalizes random-hidden-object controls with at least 50% worse occlusion_consistency than compliant direct baselines; Confidence_calibration separates overconfident hidden-region submissions from calibrated uncertainty outputs; Ambiguity-stratified subsets show monotonic degradation in occlusion_consistency and object_3d_iou as occlusion fraction increases; The benchmark runs at least three direct baselines under the same strict single-RGB input protocol and flags non-compliant runs separately

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:nerf_2020; seed:nerfvs_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:dust3r_2023; seed:mast3r_2024; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: benchmark construction may be viewed as dataset engineering rather than a model contribution, and synthetic rendered rooms may not capture all real-image ambiguity. Fallback: keep the MVP focused on 3D-FRONT and Structured3D rendered splits with transparent ambiguity labels, strong negative controls, and strict input-protocol reporting; add real-image diagnostics only as non-primary evaluation if no full 3D ground truth is available. Failure criterion: the benchmark is not useful if simple negative controls score similarly to strong baselines, if rankings are dominated by a single view-consistency metric, or if methods using extra inputs are not clearly separated from strict single-RGB submissions.

### Candidate B

Title:
Single-Image Scene Completion Benchmark with Ambiguity-Stratified Evaluation

Core proposal:
Construct an ambiguity-stratified benchmark from existing indoor datasets by rendering single RGB views with known camera intrinsics, full 3D ground truth, visible/hidden object labels, layout annotations, and physically valid alternative completions. Evaluate methods with separate scores for visible reconstruction, hidden-region plausibility, uncertainty calibration, and explicit failure warnings.

Motivation or baseline weakness:
Existing single-image-to-3D room methods are difficult to compare because image-level preview quality hides geometric errors, occluded regions are inherently multi-modal, and many baselines assume extra prompts, view synthesis, or iterative exploration rather than a strict single-RGB input.

Mechanism or approach:
A dataset-generation and evaluator layer that labels each test view by ambiguity level, occlusion fraction, layout visibility, object truncation, and physical constraint difficulty, plus a standardized JSON scene-graph schema for outputs.
Define a benchmark score that rewards visible-image fidelity and geometric consistency while treating hidden regions probabilistically: visible errors are scored against ground truth, hidden completions are scored by plausibility sets, relation validity, calibrated uncertainty, and failure-warning accuracy.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; Indoor_NeRF_prior_methods; layout_estimation_baselines; image_to_3d_generation_baselines; monocular_depth_estimation; DUSt3R; MASt3R; NeRF
3D-FRONT furnished rooms with 3D-FUTURE assets; Structured3D scenes with layout and structure annotations; Hypersim or Matterport3D/ScanNet-style real indoor images for domain-shift splits; Rendered single RGB images with camera intrinsics; Ground-truth room layouts, object poses, meshes, materials, and visibility masks
render_single_view_benchmark.py; compute_visible_hidden_masks.py; generate_ambiguity_labels.py; convert_outputs_to_scene_schema.py; evaluate_geometry_consistency.py; evaluate_scene_relations.py; evaluate_uncertainty_and_failures.py; baseline_runner_wrappers.py
depth_error; layout_iou; object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; occlusion_consistency; visible_object_recall; novel_view_consistency; image_reconstruction_lpips; object_count_accuracy; confidence_calibration; ambiguity_detection; failure_detection_auc; embodied_task_success_rate
Score hidden regions deterministically against one ground-truth completion; Remove ambiguity stratification; Remove physics and collision checks from the benchmark score; Evaluate only image reconstruction LPIPS and novel-view consistency; Use no standardized scene-graph schema; Do not separate visible and occluded objects
Submit ground-truth visible geometry with random hidden objects; Submit visually plausible 2D inpainted views with no valid 3D scene graph; Submit empty-room completions to test whether metrics penalize missing objects; Submit overconfident confidence maps for all hidden regions
Baseline ranking changes meaningfully when geometry and uncertainty metrics are added compared with LPIPS-only evaluation; The evaluator penalizes random-hidden-object controls with at least 50% worse occlusion_consistency than real baselines; Failure warnings correlate with high-error cases with failure_detection_auc above 0.8 for at least one calibrated method; Ambiguity-stratified subsets reveal monotonic degradation as occlusion fraction increases; The benchmark can run at least three direct baselines under the same single-image input protocol

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:nerf_2020; seed:nerfvs_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:dust3r_2023; seed:mast3r_2024; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: benchmark construction may become a dataset engineering contribution rather than a model contribution, and synthetic layouts may not reflect real-image ambiguity. Fallback: keep the MVP small with rendered 3D-FRONT/Structured3D splits, then add a real-image diagnostic split scored by visible geometry, relation consistency, and human-reviewed failure warnings. Failure criterion: the benchmark is not useful if simple negative controls score similarly to strong baselines or if metric rankings are dominated by one image-similarity metric rather than geometry, relations, and uncertainty.

---

## Item 14: HUM-f75f44fda2

类型：`single_idea`

### Candidate A

Title:
Object-Centric Proxy Mesh Retrieval with Physical Relation Repair

Core proposal:
Use pretrained single-image depth and object masks to lift visible objects into coarse 3D boxes, retrieve category-compatible proxy meshes from 3D-FUTURE or 3D-FRONT, and run a small relation-repair optimizer that adjusts scale, yaw, support height, and room placement while preserving 2D mask reprojection and depth ordering. Hidden objects are represented only as optional low-confidence placeholders when the room layout and visible support surfaces imply likely occluded space; otherwise the method avoids committed hallucinations.

Motivation or baseline weakness:
Single-image-to-3D scene generators often produce visually plausible previews but weak object-level geometry: furniture may float, intersect, have implausible scale, or fail to preserve visible object counts and spatial relations from the input image.

Mechanism or approach:
A relation-repair optimizer over object boxes and proxy meshes with terms for 2D reprojection, monocular depth ordering, support relations, collision avoidance, room containment, and uncertainty-aware hidden object insertion.
Given detected objects, masks, depth, and estimated room layout, optimize object pose and proxy geometry assignment to maximize visible mask and depth alignment while minimizing collision volume, unsupported-object count, out-of-room placement, and overconfident hidden object creation. Proxy retrieval is scored by category compatibility, aspect-ratio match, visible silhouette agreement, and depth-consistent scale; the repair stage refines only object pose, scale, support height, and mesh choice rather than training a new scene generator.

Experiment and implementation plan:
image_to_3d_generation_baselines; Text2Room; SceneScape; DUSt3R; MASt3R; 3D Gaussian Splatting
3D-FRONT rooms with object categories, 3D positions, layouts, and support relations; 3D-FUTURE furniture meshes and textures for proxy retrieval; Structured3D rendered single RGB images with depth and layout annotations; Held-out 3D-FRONT and Structured3D single-view splits with occluded, truncated, and cluttered furniture for external validation within the supplied evidence base
detect_and_lift_objects.py for object detection, mask extraction, depth-based 3D box initialization, and camera normalization; retrieve_proxy_meshes.py for category, aspect-ratio, and silhouette-based 3D-FUTURE or 3D-FRONT mesh retrieval; optimize_scene_relations.py for physical relation repair and uncertainty-aware hidden object placeholders; render_scene_preview.py for renderable mesh or scene-graph preview generation; evaluate_object_scene_graph.py for object 3D IoU, chamfer distance, support accuracy, object relation accuracy, collision rate, visible object recall, depth error, out-of-room rate, and confidence calibration
object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; visible_object_recall; depth_error; out_of_room_rate; confidence_calibration
No relation-repair optimizer after proxy retrieval; No collision penalty; No support-height snapping; No depth-order preservation term; Use category-average cuboids instead of retrieved proxy meshes; Always insert hidden objects without uncertainty gating
Randomly assign proxy meshes within the correct category and verify chamfer distance and object 3D IoU degrade; Randomize support relations and verify support_relation_accuracy drops; Remove visible mask reprojection terms and verify visible_object_recall and depth_error degrade; Evaluate on rendered scenes with mirrors, large occluders, or truncated furniture and verify confidence decreases when mask-depth evidence is inconsistent
Improve object_3d_iou by at least 10% relative to Text2Room or image_to_3d_generation_baselines on furnished Structured3D or 3D-FRONT renders; Reduce collision_rate by at least 30% relative to unoptimized proxy placement; Improve support_relation_accuracy by at least 15% over direct scene-generation baselines; Keep visible_object_recall at or above 90% of the object-mask detector upper bound; Hidden-object confidence should improve confidence_calibration by at least 15% relative to always-insert and never-insert deterministic proxies

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:dust3r_2023; seed:mast3r_2024; seed:3dgs_2023; seed:3dfront_2020; seed:3dfuture_2020; seed:structured3d_2019; seed:midas_2023

Risks, controls, or fallback:
Risk: retrieved proxy meshes may not match unusual furniture, and detector errors can propagate into 3D placement. Fallback: use category-level proxy cuboids with texture planes when retrieval confidence is low, preserve detector uncertainty in the scene graph, and flag scenes with inconsistent depth ordering or high residual reprojection error as low-confidence outputs.

### Candidate B

Title:
Object-Centric Proxy Mesh Retrieval with Physical Relation Repair

Core proposal:
Use pretrained single-image depth and object detection to lift visible objects into coarse 3D boxes, retrieve category-compatible proxy meshes from 3D-FUTURE or 3D-FRONT, and run a small differentiable relation-repair optimizer that adjusts scale, yaw, support height, and room placement while preserving 2D mask reprojection and depth ordering. Hidden objects are represented as optional low-confidence placeholders instead of committed hallucinations.

Motivation or baseline weakness:
Single-image-to-3D scene generators often produce visually plausible previews but weak object-level geometry: furniture may float, intersect, have implausible scale, or fail to preserve visible object counts and spatial relations from the input image.

Mechanism or approach:
A relation-repair optimizer over object boxes and proxy meshes with terms for 2D reprojection, monocular depth ordering, support relations, collision avoidance, room containment, and uncertainty-aware hidden object insertion.
Given detected objects, masks, depth, and estimated room layout, optimize object pose and proxy geometry assignment to maximize visible mask/depth alignment and scene-graph relation likelihood while minimizing collision volume, unsupported-object count, out-of-room placement, and overconfident hidden object creation.

Experiment and implementation plan:
image_to_3d_generation_baselines; Text2Room; SceneScape; DUSt3R; MASt3R; 3D Gaussian Splatting
3D-FRONT rooms with object categories, 3D positions, layouts, and support relations; 3D-FUTURE furniture meshes and textures for proxy retrieval; Structured3D rendered single RGB images with depth and layout annotations; ScanNet or Matterport3D real RGB frames with available 3D annotations for external validation
detect_and_lift_objects.py for object detection, mask extraction, depth-based 3D box initialization, and camera normalization; retrieve_proxy_meshes.py for category and aspect-ratio based 3D-FUTURE or 3D-FRONT mesh retrieval; optimize_scene_relations.py for physical relation repair and uncertainty-aware hidden object placeholders; render_scene_preview.py for renderable mesh or scene-graph preview generation; evaluate_object_scene_graph.py for object 3D IoU, chamfer distance, support accuracy, relation accuracy, collision rate, and object count accuracy
object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; object_count_accuracy; visible_object_recall; depth_error; out_of_room_rate; confidence_calibration
No relation-repair optimizer after proxy retrieval; No collision penalty; No support-height snapping; No depth-order preservation term; Use category-average cuboids instead of retrieved proxy meshes; Always insert hidden objects without uncertainty gating
Randomly assign proxy meshes within the correct category and verify chamfer/object IoU degrade; Randomize support relations and verify support_relation_accuracy drops; Remove visible mask reprojection terms and verify visible_object_recall and object_count_accuracy degrade; Evaluate on scenes with mirrors, large occluders, or truncated furniture and verify low confidence or failure warnings
Improve object_3d_iou by at least 10% relative to Text2Room or image_to_3d_generation_baselines on furnished Structured3D or 3D-FRONT renders; Reduce collision_rate by at least 30% relative to unoptimized proxy placement; Improve support_relation_accuracy by at least 15% over direct scene-generation baselines; Keep visible_object_recall at or above 90% of the detector upper bound; Hidden-object confidence should be calibrated with expected calibration error below the deterministic baseline by at least 15%

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:dust3r_2023; seed:mast3r_2024; seed:3dgs_2023; seed:3dfront_2020; seed:3dfuture_2020; seed:structured3d_2019

Risks, controls, or fallback:
Risk: retrieved proxy meshes may not match unusual furniture, and detector errors can propagate into 3D placement. Fallback: use category-level proxy cuboids with texture planes when retrieval confidence is low, preserve detector uncertainty in the scene graph, and flag scenes with inconsistent depth-order or high residual reprojection error as failures.

---

## Item 15: HUM-15d27b36c7

类型：`single_idea`

### Candidate A

Title:
Uncertainty-Aware Layout-Constrained Scene Completion from a Single RGB View

Core proposal:
Introduce a lightweight probabilistic layout-and-occlusion module before scene generation. From monocular depth, object masks, and visible wall-floor cues, the module samples K plausible Manhattan or near-Manhattan room layouts and corresponding hidden free-space volumes. Each downstream completion is constrained to remain inside one sampled layout, place objects on plausible support surfaces, and retain a confidence score. The method outputs a small set of renderable scene hypotheses rather than a single deterministic mesh.

Motivation or baseline weakness:
Text2Room and SceneScape can extrapolate a 3D room from one image, but they often commit to a single hidden-scene completion even when the occluded layout is ambiguous. This can yield objects outside the room, unsupported furniture, floor-wall inconsistencies, collisions, and little indication that the result is unreliable.

Mechanism or approach:
A layout-and-occlusion hypothesis head that consumes monocular depth, visible object detections, and room-layout cues, then predicts K room-layout hypotheses, K occluded free-space masks, and per-region uncertainty scores. It reuses existing depth, detection, and scene-generation components and does not require training a large 3D generator from scratch.
Train and select hypotheses using visible-view reprojection and depth consistency, while penalizing object-room violations, unsupported objects, inter-object collisions, and overconfident predictions in unobserved regions. Evaluate with layout IoU, visible depth error, support-relation accuracy, collision rate, out-of-room rate, occlusion consistency, and calibration of hidden-region confidence.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; layout_estimation_baselines; monocular_depth_estimation
Structured3D single RGB renders with room layout and depth annotations; 3D-FRONT furnished room scenes rendered as single RGB inputs with object positions and support relations; Matterport3D or ScanNet held-out real images for robustness testing; Camera intrinsics when available, otherwise estimated focal length
run_single_image_baselines.py to generate Text2Room, SceneScape, WonderJourney, and layout baseline outputs; infer_depth_layout_objects.py to estimate monocular depth, object masks, visible objects, and layout cues; sample_occlusion_hypotheses.py to produce K hidden-region and room-layout hypotheses; evaluate_scene_consistency.py to compute layout IoU, object 3D IoU, collision rate, support-relation accuracy, out-of-room rate, and occlusion consistency; calibrate_uncertainty.py to compute confidence calibration, ambiguity detection, and failure detection AUC
depth_error; layout_iou; object_3d_iou; collision_rate; support_relation_accuracy; out_of_room_rate; occlusion_consistency; visible_object_recall; confidence_calibration; failure_detection_auc
Use a single deterministic layout instead of K layout hypotheses; Remove occluded-region uncertainty scores; Remove the support-surface constraint; Remove the object-room boundary penalty; Use monocular depth only without object detections; Replace the probabilistic layout sampler with the top prediction from layout_estimation_baselines
Shuffle room-layout hypotheses across images and verify that consistency metrics degrade; Force all hidden-region confidence scores to a constant and verify that calibration worsens; Disable collision and room-boundary penalties and verify that out-of-room rate and collision rate increase; Evaluate on impossible or heavily cropped images and verify that failure warnings trigger instead of confident completions
Reduce out_of_room_rate by at least 25% relative to Text2Room and SceneScape on Structured3D-derived single-view tests; Reduce collision_rate by at least 20% while keeping visible_object_recall within 5% of the best direct baseline; Improve layout_iou by at least 0.08 absolute over image-to-3D generation baselines without layout constraints; Improve expected calibration error for occluded-region confidence by at least 15% over deterministic confidence proxies; Achieve failure_detection_auc above 0.75 on ambiguous, cropped, or mirror-heavy failure cases

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023

Risks, controls, or fallback:
Risk: layout hypotheses may be unreliable for non-Manhattan rooms, cluttered views, or images with little visible floor-wall evidence. Fallback: expose posterior uncertainty, keep multiple low-rank scene hypotheses, and issue a conservative failure warning when layout entropy is high or all hypotheses have high collision or out-of-room penalties.

### Candidate B

Title:
Uncertainty-Aware Layout-Constrained Scene Completion from a Single RGB View

Core proposal:
Add a lightweight probabilistic room-layout and hidden-region sampler before scene completion. The module uses monocular depth, object masks, and visible wall-floor cues to predict K Manhattan or piecewise-Manhattan room-layout hypotheses and K occluded free-space masks. Each completion from Text2Room-, SceneScape-, or WonderJourney-style generation is constrained to remain inside one sampled layout, and generated objects must attach to plausible support surfaces. The method returns a small set of renderable scene hypotheses with calibrated per-region confidence rather than one deterministic mesh.

Motivation or baseline weakness:
Text2Room and SceneScape can extend a scene from one image, but occluded regions are often completed as a single overconfident hallucination, producing objects outside the room, inconsistent floor-wall support, and weak failure signaling under ambiguous layouts.

Mechanism or approach:
A layout-and-occlusion hypothesis head that takes monocular depth, visible object detections, and layout cues, then emits K room-layout hypotheses, K occluded free-space masks, and per-region uncertainty scores; no large 3D generator is trained from scratch.
Minimize visible-view reprojection and monocular depth consistency while penalizing object-room violations, unsupported objects, inter-object collisions, and overconfident predictions in unobserved regions. The layout head is supervised where Structured3D or 3D-FRONT annotations are available, and uncertainty is trained/evaluated by comparing predicted hidden-region confidence against held-out full-scene geometry. The objective reports layout IoU, visible depth error, support-relation accuracy, collision rate, out-of-room rate, occlusion consistency, and confidence calibration.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; layout_estimation_baselines; monocular_depth_estimation
Structured3D single RGB renders with room layout and depth annotations; 3D-FRONT furnished room scenes rendered as single RGB inputs with object positions and support relations; Held-out Structured3D and 3D-FRONT stress splits with narrow field of view, heavy occlusion, and non-frontal views; Camera intrinsics when available, otherwise estimated focal length with uncertainty propagated into layout hypotheses
run_single_image_baselines.py to generate Text2Room, SceneScape, WonderJourney, layout-estimation, and monocular-depth outputs under the same single-RGB input protocol; infer_depth_layout_objects.py for monocular depth, object masks, visible object list, wall-floor cues, and camera normalization; sample_occlusion_hypotheses.py for K hidden-region and room-layout hypotheses with confidence scores; constrain_scene_completion.py to clip or reject generated geometry that violates sampled room bounds or support surfaces; evaluate_scene_consistency.py for depth error, layout IoU, object 3D IoU, collision rate, support-relation accuracy, out-of-room rate, occlusion consistency, visible object recall, and confidence calibration
depth_error; layout_iou; object_3d_iou; collision_rate; support_relation_accuracy; out_of_room_rate; occlusion_consistency; visible_object_recall; confidence_calibration
Single deterministic layout instead of K layout hypotheses; No occluded-region uncertainty scores; No support-surface constraint; No object-room boundary penalty; Use monocular depth only without object detections; Replace probabilistic layout sampler with the top prediction from layout_estimation_baselines
Shuffle room-layout hypotheses across images and verify layout IoU, out-of-room rate, and collision rate degrade; Force all hidden-region confidence scores to a constant and verify confidence calibration worsens; Disable collision and room-boundary penalties and verify out-of-room rate and collision rate increase; Evaluate on heavily cropped or mirror-like rendered stress cases and verify confidence decreases rather than producing high-confidence completions
Reduce out_of_room_rate by at least 25% relative to Text2Room and SceneScape on Structured3D-derived single-view tests; Reduce collision_rate by at least 20% while maintaining visible_object_recall within 5% of the best direct baseline; Improve layout_iou by at least 0.08 absolute over image-to-3D generation baselines without layout constraints; Improve confidence_calibration for occluded-region predictions by at least 15% over deterministic confidence proxies; On cropped and high-occlusion stress splits, assign lower confidence to incorrect hidden-region completions than to correct completions in at least 75% of paired comparisons

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:3dfront_2020

Risks, controls, or fallback:
Risk: layout hypotheses may be wrong for non-Manhattan rooms or images with little floor-wall evidence. Fallback: expose the uncertainty explicitly, keep multiple low-rank scene hypotheses, and use a conservative low-confidence output when layout posterior entropy is high or when all hypotheses produce high collision or out-of-room penalties.

---

## Item 16: HUM-52eb3f805b

类型：`portfolio`

### Candidate A

Idea 1
Title:
Layout-Conditioned Object Lifting With Uncertainty-Aware Occluded Footprints

Core proposal:
Add a lightweight probabilistic floorplan-and-footprint layer on top of a pretrained single-image scene generator. The layer first estimates a Manhattan-style room envelope, visible free space, support planes, and visible object 2D masks or boxes. It then lifts visible objects to coarse 3D footprints using monocular depth and camera geometry, and samples occluded footprints only in regions not contradicted by visible evidence. Each sampled footprint has category, size, height, support-surface, and existence probability, and is rejected or downweighted when it crosses room boundaries, collides with higher-confidence objects, lacks support, blocks visible free space, or violates category-specific size ranges. The downstream generator is conditioned on the sampled footprint scene graph and returns multiple renderable scenes plus per-object uncertainty for hidden regions.

Motivation or baseline weakness:
Single-image-to-3D-scene baselines can place plausible visible objects but often hallucinate hidden object extents or positions that violate the inferred room layout, causing out-of-room objects, floating furniture, and unsupported occluded regions.

Mechanism or approach:
A floorplan occupancy sampler that represents each object as a 2D ground-plane footprint with category-conditioned size and height priors, maintains occupancy probabilities for occluded regions, and performs rejection sampling or differentiable relaxation against room-boundary, free-space, support, and collision constraints.
Maximize visible-image, detected-object, and monocular-depth consistency while minimizing room-boundary violations, unsupported placements, footprint collisions, visible-free-space intrusions, and overconfident hidden-object predictions. The falsifiable experiment is whether adding the footprint sampler improves geometric consistency and hidden-region calibration over the same generator with no footprint layer.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; layout_estimation_baselines; monocular_depth_estimation; image_to_3d_generation_baselines
3D-FRONT; 3D-FUTURE; Structured3D; Matterport3D; ScanNet; single RGB image with optional camera intrinsics; visible object detections or segmentation masks; estimated monocular depth; estimated room layout cues; occlusion masks derived from depth, visibility, and object ordering
run_single_image_scene_baselines.py; estimate_layout_depth_objects.py; sample_uncertain_floorplan_footprints.py; generate_scene_from_constrained_scene_graph.py; evaluate_geometry_scene_consistency_uncertainty.py; render_novel_views_and_previews.py
layout_iou; object_3d_iou; depth_error; collision_rate; out_of_room_rate; support_relation_accuracy; object_relation_accuracy; occlusion_consistency; visible_object_recall; object_count_accuracy; confidence_calibration; failure_detection_auc; navigation_success_rate
remove room-layout boundary constraints; remove visible-free-space constraints; remove object-support constraints; remove collision rejection; replace probabilistic occluded footprints with deterministic mean footprints; condition generator on visible objects only; use ground-truth layout to estimate upper bound; use ground-truth visible object boxes to separate detector error from lifting error
sample occluded footprints uniformly in the room without physical constraints; shuffle detected object categories before footprint sampling while keeping boxes fixed; use an incorrectly scaled room layout while keeping visible detections fixed; force all occluded regions to be empty; place occluded footprints preferentially inside visible free-space regions
reduce out_of_room_rate by at least 30% relative to the unconstrained single-image scene generator; reduce collision_rate by at least 25% without decreasing visible_object_recall by more than 5%; improve layout_iou or maintain it while improving object_3d_iou by at least 10%; improve confidence_calibration for occluded object presence compared with deterministic generation; increase failure_detection_auc for impossible layouts or severe occlusions by at least 0.05

Risks, controls, or fallback:
Risk: the footprint prior may over-regularize scenes and suppress unusual but valid furniture arrangements. Fallback: expose a diversity weight, allow soft constraint penalties for low-confidence layout estimates, and report uncertainty instead of committing to one layout. Failure criteria: no measurable reduction in collision_rate or out_of_room_rate, or improved consistency comes only by deleting difficult objects and lowering visible_object_recall.

---

Idea 2
Title:
Render-Check-and-Repair Loop for Single-Image Indoor Scene Generation

Core proposal:
Wrap existing single-image-to-scene baselines with a lightweight render-check-and-repair loop. After an initial scene is generated, render the input camera and a small set of nearby virtual cameras. Compare the input render against the RGB image, monocular depth, visible object masks, and estimated segmentation, and check every rendered scene for collisions, room-boundary violations, unsupported objects, implausible object scale, and inconsistent depth ordering. Repair is restricted to scene-graph parameters: object translation, yaw, scale within category bounds, support assignment, proxy mesh choice from a fixed candidate set, and material or texture projection confidence. The underlying generator remains frozen, and repairs are accepted only if they improve a held-out consistency score without violating hard physical constraints.

Motivation or baseline weakness:
Single-image 3D scene generators may produce renderable scenes that look plausible from the input view but fail under novel views because object geometry, depth ordering, support relations, and textures are not jointly checked after generation.

Mechanism or approach:
A scene-graph repair optimizer that alternates continuous edits for object transforms and scales with discrete edits for support edges and proxy geometry selection, using differentiable rendering losses for visible evidence and explicit penalties or hard filters for collisions, room bounds, support, and excessive deviation from the initial scene.
Minimize a combined consistency energy with input-view photometric or perceptual reconstruction, mask coverage, depth-order agreement, visible-object coverage, collision penalty, room-boundary penalty, support violation penalty, scale prior penalty, and low-evidence-surface uncertainty penalty. The falsifiable experiment is whether post-generation repair improves novel-view and physics metrics over the same initial scene without retraining the large generator.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; Indoor_NeRF_prior_methods; 3D Gaussian Splatting; NeRF; DUSt3R; MASt3R
Matterport3D; ScanNet; Hypersim; Structured3D; single RGB image; optional camera intrinsics; pretrained monocular depth predictions; object detector or segmentation outputs; initial renderable scene from a single-image baseline
generate_initial_scene_baseline.py; render_candidate_views.py; compute_input_view_alignment_losses.py; check_physics_collisions_supports.py; repair_scene_graph_parameters.py; evaluate_repaired_scene.py
image_reconstruction_lpips; novel_view_consistency; depth_error; visible_object_recall; object_count_accuracy; collision_rate; out_of_room_rate; support_relation_accuracy; object_relation_accuracy; chamfer_distance; confidence_calibration; failure_detection_auc
repair object poses only; repair geometry proxies only; repair support relations only; repair materials and textures only; remove novel-view render checks; remove physical collision and support checks; remove maximum-displacement constraints from the initial scene; replace optimization with one-shot heuristic snapping; use ground-truth depth as an oracle upper bound
optimize against a horizontally flipped input image; optimize only image_reconstruction_lpips without geometry or physics penalties; randomly perturb object poses for the same number of repair iterations; accept all repairs even when input-view alignment worsens; disable hard room-boundary checks while keeping the same optimizer budget
reduce collision_rate by at least 20% relative to the unrepaired baseline; improve novel_view_consistency by at least 10% while not degrading image_reconstruction_lpips by more than 3%; improve support_relation_accuracy by at least 10%; reduce depth_error in visible regions by at least 5%; flag failed repair cases with failure_detection_auc at least 0.75

Risks, controls, or fallback:
Risk: the optimizer may exploit image losses by moving objects into visually aligned but physically implausible positions or by overfitting to the input view. Fallback: enforce hard constraints for room bounds, support, and maximum pose displacement; validate each repair on nearby views; and reject edits that improve RGB alignment while worsening geometry checks. Failure criteria: gains occur only in input-view LPIPS while novel_view_consistency, collision_rate, or support_relation_accuracy worsens.

---

Idea 3
Title:
Ambiguity-Calibrated Scene Sets Instead of One Deterministic Indoor Reconstruction

Core proposal:
Generate a compact set of diverse, physically valid scene hypotheses rather than one scene. A pretrained single-image generator proposes candidate scenes from multiple seeds, prompts, or latent samples. A lightweight ambiguity estimator labels image regions and scene-graph elements as directly visible, inferred by support or layout cues, or unobserved. A hypothesis selector then keeps K scenes that match visible evidence, satisfy physical constraints, and differ primarily in unobserved footprints, hidden objects, and back-facing geometry. Object, occupancy, and relation confidences are computed as marginals over the retained set, while visible objects are forced to remain consistent with the input unless the detector confidence is low.

Motivation or baseline weakness:
A single RGB image cannot determine hidden room regions, back-facing geometry, or occluded objects, but many baselines output one confident scene, making downstream navigation or embodied planning brittle when the hidden scene is wrong.

Mechanism or approach:
A hypothesis-set selector that scores candidate scenes by visible evidence consistency, physical plausibility, and pairwise diversity restricted to occluded or unobserved regions, then outputs a renderable scene ensemble and a marginal scene graph with calibrated object, occupancy, support, and relation probabilities.
Select K scene hypotheses that maximize visible-view consistency and physical validity while maximizing diversity only in image-unobserved regions and maintaining compactness of the retained set. The falsifiable experiment is whether downstream agents or evaluators perform better with calibrated scene sets than with the top-1 generated scene under the same candidate generation budget.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; image_to_3d_generation_baselines; monocular_depth_estimation; DUSt3R; MASt3R; scene_graph_evaluator
3D-FRONT; 3D-FUTURE; Matterport3D; ScanNet; Structured3D; single RGB image; camera intrinsics if available; object detections; estimated depth and occlusion maps; held-out ground-truth scene annotations where available
sample_multiple_scene_hypotheses.py; estimate_visible_and_occluded_regions.py; score_scene_hypotheses.py; select_diverse_physical_scene_set.py; compute_marginal_scene_graph_confidence.py; evaluate_top1_vs_scene_set.py; run_downstream_navigation_or_query_tasks.py
occlusion_consistency; confidence_calibration; ambiguity_detection_auc; failure_detection_auc; visible_object_recall; object_count_accuracy; object_3d_iou; layout_iou; collision_rate; support_relation_accuracy; navigation_success_rate; embodied_task_success_rate
K equals 1 deterministic output; diversity over all regions instead of occluded regions only; remove confidence calibration; remove physical plausibility score; remove visible-evidence consistency score; select hypotheses randomly from the same generator samples; use only generator likelihood or score for selection; oracle K selection using ground-truth hidden scene to estimate upper bound
encourage diversity in visible object identities even when contradicted by the input image; calibrate confidence from generator score only without cross-hypothesis agreement; select the K most visually different renderings without checking geometry; evaluate only top-1 while ignoring uncertainty outputs; select hypotheses that intentionally violate visible depth ordering to increase diversity
improve confidence_calibration for occluded object presence by at least 15% relative error reduction; increase ambiguity_detection_auc by at least 0.08 over deterministic confidence baselines; maintain visible_object_recall within 5% of the best top-1 baseline; reduce overconfident false hidden-object predictions by at least 20%; improve navigation_success_rate or embodied_task_success_rate under hidden-obstacle uncertainty by at least 5%

Risks, controls, or fallback:
Risk: generating many hypotheses may increase compute and produce redundant samples. Fallback: use a small K, cluster hypotheses by occluded-region occupancy before selection, and cache shared visible geometry. Failure criteria: the ensemble improves uncertainty metrics only by becoming uniformly uncertain, increases diversity by corrupting visible evidence, or fails to improve downstream performance over a deterministic top-1 scene.

### Candidate B

Idea 1
Title:
Uncertainty-Gated Occlusion Hypothesis Layer for Single-Image Room Completion

Core proposal:
Add a lightweight probabilistic occlusion hypothesis layer on top of a Text2Room-style single-image pipeline. From the input RGB image, estimate visible layout, visible object masks or boxes, and monocular depth; construct occlusion volumes from depth discontinuities, foreground masks, room-boundary rays, and unobserved frustum cells; then sample K scene-graph hypotheses over hidden occupied or empty regions. Each hypothesis is scored by room containment, object-size priors, support feasibility, pairwise collision checks, consistency with visible reprojection, and a confidence head calibrated against whether the hidden-region hypothesis matches held-out synthetic ground truth. Visible surfaces from the baseline reconstruction are kept fixed except for small depth/layout alignment corrections, while occluded regions are represented as weighted alternatives rather than a single mesh completion.

Motivation or baseline weakness:
Text2Room, SceneScape, and WonderJourney can expand a scene from one image, but hidden regions are often filled as a single confident completion, causing unsupported objects, duplicate furniture, out-of-room geometry, and poor calibration under single-image ambiguity.

Mechanism or approach:
A small occlusion-volume-to-scene-graph sampler plus confidence calibration head. It consumes outputs from pretrained monocular depth, layout estimation, object-mask extraction, and an existing Text2Room/SceneScape/WonderJourney-style mesh construction pipeline; it does not train a large 3D generator from scratch.
Optimize hypothesis weights and hidden-object parameters with L = L_visible_reprojection + L_depth_consistency + L_layout + L_relation + L_collision + L_room_containment + L_calibration. The visible losses constrain the reconstruction to the input image, relation/collision/containment losses score physical plausibility in 3D, and the calibration term penalizes high confidence when multiple hidden completions remain compatible with the visible evidence.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; layout_estimation_baselines; monocular_depth_estimation; 3D-FRONT
Single RGB indoor images with camera intrinsics when available; 3D-FRONT/3D-FUTURE rendered single-view rooms with full hidden-object, layout, and relation ground truth; Structured3D rendered views for layout and depth supervision; Held-out real single RGB indoor images used only for qualitative validation and visible-region metrics when full hidden ground truth is unavailable
run_single_image_baselines.py for Text2Room, SceneScape, and WonderJourney comparisons under identical single-image input assumptions; extract_visible_objects_layout_depth.py to produce visible masks or boxes, room-layout planes, and monocular depth maps; build_occlusion_volumes.py to mark unobserved cells from depth discontinuities, visible masks, camera rays, and room layout; sample_uncertain_scene_graphs.py to sample K hidden empty/occupied/object hypotheses with weights; score_and_calibrate_hypotheses.py to compute relation, collision, containment, reprojection, and confidence terms; evaluate_geometry_relations_uncertainty.py for layout, object, collision, occlusion, and calibration metrics
depth_error; layout_iou; object_3d_iou; chamfer_distance; collision_rate; out_of_room_rate; support_relation_accuracy; object_relation_accuracy; occlusion_consistency; visible_object_recall; confidence_calibration
Remove occlusion-volume reasoning and sample hidden objects from global 3D-FRONT category and size priors only; Replace multi-hypothesis output with the top-1 completion while keeping the same sampler; Remove calibration loss while keeping identical geometric scoring; Remove collision and support-relation scoring from hypothesis ranking; Use visible-object evidence only without room-layout containment constraints
Sample hidden objects uniformly from 3D-FRONT category frequencies without conditioning on the input image; Assign uniformly high confidence to every occluded hypothesis regardless of ambiguity; Place hidden objects using 2D image-space proximity only, without 3D room layout or depth constraints; Evaluate on synthetic views with minimal occlusion where calibrated uncertainty should collapse to low entropy; Shuffle occlusion-volume labels before sampling to verify the sampler depends on geometric visibility rather than dataset priors alone
Reduce collision_rate by at least 25% relative to the strongest Text2Room-style single-hypothesis completion at matched visible_object_recall; Improve occlusion_consistency by at least 10% over single-hypothesis SceneScape/WonderJourney outputs on held-out synthetic rooms; Improve confidence_calibration ECE by at least 20% for hidden occupancy and hidden-object placement confidence; Maintain visible_object_recall within 3 percentage points of the best direct baseline; Failure criterion: if uncertainty does not correlate with hidden-region error better than baseline confidence or entropy scores, the occlusion hypothesis mechanism is not supported

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: hidden-object supervision from synthetic rooms may not transfer to real indoor images, and category-level hidden-object prediction may be underdetermined from a single RGB view. Fallback: report synthetic hidden-region results separately from real-image visible-region checks, expose uncertainty over empty versus occupied occlusion volumes even when category labels are unreliable, and treat human or VLM plausibility checks as secondary diagnostics rather than primary evidence.

---

Idea 2
Title:
Geometry-First Scene Graph Repair for Image-to-3D Indoor Generation

Core proposal:
Insert a post-generation geometry repair stage after a Text2Room/SceneScape/WonderJourney-style output. The stage canonicalizes the generated mesh into a typed scene graph containing room planes, visible object proxies, approximate object boxes, support candidates, containment relations, and pairwise spatial relations. It then solves a constrained 3D repair problem over object poses, box dimensions, support contacts, and layout-plane alignment while preserving visible-image projections and retaining the original generated textures where possible. The repair is accepted only if constraint violations are reduced without moving visible evidence beyond a preset reprojection/depth tolerance; otherwise the system emits a failure warning instead of silently changing the scene.

Motivation or baseline weakness:
Image-to-3D room generation baselines can produce visually plausible previews while violating basic 3D constraints: furniture floats, penetrates walls, lacks support surfaces, exits the room boundary, or drifts from the visible object layout because generation is not explicitly repaired against a structured scene graph.

Mechanism or approach:
A differentiable or search-based scene graph repair optimizer over room planes, object 3D boxes, support contacts, containment, and collision constraints. It uses pretrained depth, object-mask or box extraction, and layout modules for perception, and reuses the baseline-generated mesh as the visual asset rather than replacing it with a new generator.
Minimize E = reprojection_error + depth_alignment + layout_plane_error + object_box_prior + collision_penalty + support_penalty + out_of_room_penalty + relation_penalty + texture_anchor_penalty, subject to visible object masks remaining aligned with the input RGB image and repaired proxy geometry remaining physically plausible and renderable. If the minimum feasible solution exceeds a visible-alignment threshold, the method returns an explicit repair failure warning.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; image_to_3d_generation_baselines; layout_estimation_baselines; monocular_depth_estimation; 3D-FRONT
Single RGB indoor images with visible object masks, boxes, or detector outputs; 3D-FRONT/3D-FUTURE scenes for object-size, support, containment, and relation priors; Structured3D rendered views for room layout and depth evaluation; Held-out real single-view indoor images for visible reprojection, depth, and qualitative stress tests where full object ground truth is not available
run_generation_baselines.py to produce initial Text2Room, SceneScape, WonderJourney, or image-to-3D baseline scenes under matched inputs; baseline_scene_to_graph.py to extract layout planes, object proxies, boxes, and approximate meshes from generated scenes; fit_proxy_scene_graph.py to estimate typed object proxies and candidate support or containment relations; repair_scene_geometry.py to optimize object transforms, supports, collisions, and room containment with visible-alignment constraints; render_repaired_scene.py to export repaired mesh, proxy scene graph, and before/after previews; evaluate_scene_graph_geometry.py for relation, collision, layout, depth, and visible-alignment metrics
layout_iou; object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; depth_error; visible_object_recall; novel_view_consistency
Use the visual generation output directly without repair; Optimize collisions only without support relations; Optimize support relations only without room containment; Remove visible reprojection and depth constraints and allow unconstrained 3D repair; Use class-agnostic boxes instead of category-specific size and support priors; Replace the accept/reject failure gate with always-apply repair
Apply the repair optimizer to random object layouts initialized far from the input image to verify visible-alignment constraints reject them; Shuffle object categories while keeping boxes fixed to test whether semantic support priors matter; Disable room layout planes and allow objects outside the room to verify containment penalties are necessary; Run repair on ground-truth synthetic layouts where changes should be minimal; Perturb visible object masks before repair to test whether the optimizer overfits noisy perception rather than stable 3D constraints
Reduce collision_rate by at least 30% compared with the unrepaired baseline output; Reduce out_of_room_rate by at least 30% without decreasing visible_object_recall by more than 3 percentage points; Improve support_relation_accuracy by at least 10% on rendered 3D-FRONT/Structured3D-style test views; Maintain depth_error and layout_iou within 5% of the unrepaired visible reconstruction unless the baseline was already geometrically invalid; Failure criterion: if repairs improve constraints only by moving visible objects away from their input-image projections, the mechanism fails the single-image alignment requirement

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:3d_scenedreamer_2024; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: proxy boxes may oversimplify detailed furniture and improve relation metrics while hurting visual fidelity. Fallback: keep original textured meshes attached to repaired proxy transforms, report proxy-geometry metrics separately from rendered-view metrics, and trigger failure warnings when the repair requires large visible reprojection or depth changes.

---

Idea 3
Title:
Single-Image Indoor Scene Benchmark with Ambiguity-Aware Multi-Hypothesis Evaluation

Core proposal:
Build an ambiguity-aware benchmark protocol from synthetic indoor scenes with complete 3D ground truth and optional real-image validation. Each test case exposes one RGB image, camera metadata when available, and the required output format; full layout, depth, object, relation, and hidden-region annotations remain hidden for evaluation. Methods may submit either one reconstruction or K weighted hypotheses, but all outputs must be canonicalized into a proxy scene graph plus renderable asset. Visible regions are scored deterministically against the input view, while occluded regions are scored with top-K, set-valued, and confidence-calibration criteria. The new component is the evaluator and submission protocol, not a new generator.

Motivation or baseline weakness:
Existing single-image-to-3D scene methods are hard to compare because evaluations often reward one plausible render but under-measure geometric consistency, hidden-region ambiguity, physical constraints, representation-specific artifacts, and explicit failure detection.

Mechanism or approach:
A benchmark evaluator that canonicalizes meshes, Gaussian splats, NeRF-like renderers, and scene-graph outputs into a common proxy representation with layout planes, object boxes or meshes, relations, occlusion hypotheses, confidence values, and failure warnings, then computes deterministic visible metrics and probabilistic hidden-region metrics.
Define a falsifiable benchmark score S = S_visible_geometry + S_layout + S_relations + S_collision + S_novel_view + S_occlusion_topK + S_calibration - S_failure_penalty, with separate leaderboards for top-1 reconstruction, multi-hypothesis hidden-region plausibility, and calibrated failure detection. Scores are also reported by input protocol so true single-image methods are not conflated with methods that require extra views, poses, or optimization data.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; Indoor_NeRF_prior_methods; layout_estimation_baselines; monocular_depth_estimation; DUSt3R; MASt3R; 3D Gaussian Splatting; NeRF; 3D-FRONT
3D-FRONT/3D-FUTURE rendered rooms with full object meshes, materials or textures, layout, and relations; Structured3D rendered images with layout and depth annotations; Single RGB image per test case plus optional camera intrinsics; Optional held-out real single-view indoor images used for visible-region and qualitative validation only when complete hidden-region ground truth is unavailable
render_single_view_benchmark.py to produce RGB, depth, masks, layout, relations, camera metadata, and hidden-region labels from synthetic scenes; canonicalize_scene_outputs.py to convert mesh, Gaussian, NeRF-style, or scene-graph outputs into a common proxy representation; compute_visible_geometry_metrics.py for depth, layout, object, and chamfer metrics; compute_scene_consistency_metrics.py for support, relation, collision, out-of-room, and occlusion-consistency metrics; compute_uncertainty_failure_metrics.py for confidence calibration and failure-warning evaluation; run_baseline_protocols.py to run single-image baselines separately from multi-view or optimization-heavy baselines and label their input assumptions
depth_error; layout_iou; object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; occlusion_consistency; visible_object_recall; novel_view_consistency; confidence_calibration
Evaluate only top-1 scenes instead of top-K hypotheses; Remove occluded-region metrics and score visible regions only; Remove support, collision, and out-of-room checks; Remove confidence and failure-warning requirements; Score rendered previews only through visible depth and novel-view consistency without canonical scene-graph checks; Pool single-image and extra-view methods into one leaderboard to quantify how much protocol mixing changes rankings
Score ground-truth scenes with randomized hidden objects to verify occlusion metrics detect implausible completions; Score visually plausible 2D billboard rooms to verify geometry metrics penalize non-3D solutions; Score outputs with shuffled confidence values to verify calibration metrics degrade; Score scenes with deliberately moved furniture outside room boundaries to verify out_of_room_rate and collision checks respond; Submit ground-truth proxy scene graphs with degraded render textures to verify the benchmark does not collapse to image-preview quality alone
Benchmark must separate ground-truth scenes from randomized hidden-object negative controls by at least 0.25 normalized score; Adding consistency metrics must prevent a known geometry-violating output from outranking a physically valid output solely due to preview quality; Confidence_calibration must worsen measurably when confidence values are shuffled or made uniformly high; At least three direct baselines must be runnable through the canonical evaluator without manual per-scene intervention; Failure criterion: if leaderboard ranking is dominated by preview or visible-only quality while collision, relation, and occlusion errors remain statistically indistinguishable, the benchmark does not meet the research goal

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:nerf_2020; seed:nerfvs_2023; seed:dust3r_2023; seed:mast3r_2024; seed:3dgs_2023; seed:3dfront_2020; seed:3dfuture_2020; seed:structured3d_2019

Risks, controls, or fallback:
Risk: canonicalizing diverse representations such as meshes, NeRFs, Gaussian splats, and scene graphs may introduce evaluator bias, and some listed reconstruction baselines are not true single-image methods. Fallback: require every submission to include a minimal proxy scene graph plus renderable asset, report representation-specific diagnostics separately, split leaderboards by input protocol, and use negative controls to audit whether the evaluator rewards physical 3D structure rather than format artifacts.

---

## Item 17: HUM-028263467e

类型：`portfolio`

### Candidate A

Idea 1
Title:
Uncertainty-Aware Scene Graph Scaffolds for Single-Image Indoor 3D Scene Completion

Core proposal:
Build a single-image-to-renderable-scene system that first extracts a metric room-layout and object-level scene graph, then completes hidden regions with multiple uncertainty-ranked hypotheses rather than one deterministic hallucination. The output is a renderable hybrid scene: layout planes, object proxy meshes or retrieved CAD-like assets, material tags/textures, spatial relations, occluded-region alternatives, confidence scores, and failure warnings. Task type: generative modeling, single-image 3D generation, geometry consistency, metric improvement. Direct baselines: Text2Room, SceneScape, WonderJourney, layout_estimation_baselines, image_to_3d_generation_baselines. Transfer baselines: monocular_depth_estimation, DUSt3R, MASt3R, 3D Gaussian Splatting, NeRF/Indoor_NeRF_prior_methods. Borrowed components: monocular depth for visible geometry; room-layout estimator for walls/floor/ceiling; object detector/segmenter for visible instances; 3D-FRONT/3D-FUTURE object priors; physics/collision checker; scene-graph evaluator. New component: a lightweight probabilistic scene-graph scaffold that treats unobserved objects, object backsides, support surfaces, and room extents as latent variables, samples several physically feasible completions, and calibrates confidence using visibility, depth residual, relation validity, and collision risk. Minimal new module: a factor-graph or diffusion-lite sampler over object categories, sizes, poses, support relations, and occluded cells, constrained by the input image and layout. MVP artifacts: code pipeline, JSON scene graph schema, Blender/Three.js renderer export, uncertainty visualizer for occluded regions, benchmark scripts, and example scenes with top-k completions.

Motivation or baseline weakness:
Existing single-image room generation systems can produce plausible previews but often conflate visual plausibility with geometric validity. A deterministic completion is especially misleading for occluded areas behind furniture, outside the camera frustum, or under/behind support surfaces. A scene-graph scaffold can make ambiguity explicit while improving downstream usability for navigation, simulation, and embodied tasks: visible objects are anchored to image evidence, hidden regions are represented as hypotheses, and every object has support, collision, room-containment, and confidence metadata. Novelty relative to supplied work: Text2Room, SceneScape, and WonderJourney use 2D generation/depth/perpetual expansion, while this proposal centers uncertainty-calibrated object/layout scaffolds and relation-level validity as first-class outputs rather than only textured mesh growth.

Mechanism or approach:
Pipeline: (1) infer camera intrinsics if absent and estimate monocular depth/pointmap for the visible image; (2) estimate room layout and vanishing geometry; (3) detect and segment visible objects, infer amodal masks where possible, and lift them to 3D boxes/proxy meshes using depth and category priors; (4) construct a visible scene graph with relations such as on, against, inside-room, left-of, occludes, and supports; (5) discretize unseen room regions into uncertainty cells; (6) sample top-k completions conditioned on object-category co-occurrence, support constraints, free-space constraints, image-consistent occlusion, and layout boundaries; (7) retrieve or generate simple proxy meshes and material labels/textures for each object; (8) run a collision/support/out-of-room checker and confidence calibrator; (9) output a renderable scene plus failure warnings. Datasets: Structured3D and 3D-FRONT/3D-FUTURE for synthetic controlled supervision/evaluation; ScanNet, Matterport3D, and Hypersim for real/sim-to-real testing. Metrics: depth_error, layout_iou, object_3d_iou, chamfer_distance for visible geometry; collision_rate, support_relation_accuracy, object_relation_accuracy, out_of_room_rate, occlusion_consistency for scene consistency; visible_object_recall, object_count_accuracy, novel_view_consistency, image_reconstruction_lpips for image alignment; confidence_calibration, ambiguity_detection, failure_detection_auc for uncertainty; navigation_success_rate or embodied_task_success_rate for downstream utility. Ablations: no uncertainty sampling; no relation constraints; no physics/collision checker; deterministic maximum-likelihood hidden completion; depth-only lifting; layout-only scaffold; no amodal completion; no confidence calibration; different numbers of hypotheses. Risks: object detectors miss small or reflective objects; monocular depth scale errors propagate to object placement; priors from 3D-FRONT may bias toward clean furniture layouts; uncertainty may be well-calibrated but not visually compelling. Failure criteria: worse collision_rate or out_of_room_rate than Text2Room/SceneScape at matched visible-object recall; poor confidence calibration on held-out occlusion tests; high rate of unsupported floating objects; inability to export a valid renderable scene graph for more than 10% of benchmark images.

Experiment and implementation plan:
Construct a benchmark from Structured3D and 3D-FRONT by rendering single RGB views with known full 3D scenes, then hiding the ground truth during inference. Add ScanNet/Matterport3D/Hypersim subsets for realistic imagery and partial 3D annotations. Compare against Text2Room, SceneScape, WonderJourney, layout estimation plus depth lifting, and image-to-3D generation baselines. Evaluate visible-region reconstruction separately from occluded-region plausibility. Report top-1 and top-k metrics: top-1 for deterministic usability and oracle/top-k for ambiguity coverage. Include human or VLM-assisted plausibility only as secondary evidence; primary metrics are layout_iou, object_3d_iou, collision_rate, support_relation_accuracy, out_of_room_rate, occlusion_consistency, visible_object_recall, novel_view_consistency, confidence_calibration, and failure_detection_auc. Implementation plan: month 1 assemble data/rendering/evaluation; month 2 implement visible layout/object/depth scaffold; month 3 add probabilistic occluded-region sampler; month 4 add mesh/material retrieval and renderer export; month 5 run baselines/ablations; month 6 downstream navigation sanity tests and paper figures.

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:dust3r_2023; seed:mast3r_2024; seed:3dfront_2020; seed:3dfuture_2020

---

Idea 2
Title:
Self-Checking View-Expansion for Single-Image Indoor Scene Generation

Core proposal:
Develop a single-image indoor scene generator that expands beyond the input view only through a loop of propose-render-check-repair. Instead of trusting generated novel views, the system repeatedly checks whether newly hallucinated geometry remains consistent with the initial image, inferred layout, depth, object count, support relations, and physical constraints. The final output is a textured mesh or Gaussian/mesh hybrid plus a scene graph with explicit confidence and failure warnings. Task type: single-image 3D generation, geometry consistency, generative modeling, metric improvement. Direct baselines: Text2Room, SceneScape, WonderJourney, Indoor_NeRF_prior_methods, image_to_3d_generation_baselines. Transfer baselines: monocular_depth_estimation, DUSt3R/MASt3R for geometry anchors, 3D Gaussian Splatting or NeRF for renderable representation. Borrowed components: iterative view generation/inpainting from Text2Room/SceneScape-style systems, depth priors, pointmap reconstruction, VLM or detector-based verification, collision checker, scene graph evaluator. New component: a geometric self-check controller that decides whether to accept, reject, or repair each generated novel view and its fused geometry based on multi-metric consistency constraints. Minimal new module: a lightweight controller with differentiable or rule-based scores for reprojection error, depth continuity, object identity preservation, layout containment, support validity, and uncertainty growth. MVP artifacts: reproducible expansion loop, checker dashboard, exported mesh/3DGS preview, logs of rejected generations, and benchmark scripts.

Motivation or baseline weakness:
Perpetual scene generation methods can extend a room from a single image, but small errors in depth, scale, or object identity can accumulate over successive views. Indoor scenes are particularly sensitive because walls, floors, furniture supports, and occlusions impose strong geometric constraints. A self-checking controller may improve reliability without training a large 3D generative model: use strong pretrained generation/reconstruction components, but gate their outputs with task-specific geometric and semantic tests. Novelty relative to supplied work: Text2Room and SceneScape already combine generation, depth, and fusion; WonderJourney includes modular planning and verification. This proposal makes metric-driven geometric rejection/repair the central research contribution and directly optimizes for scene-level consistency, uncertainty, and downstream usability.

Mechanism or approach:
Pipeline: (1) initialize a camera, depth map, layout, visible object graph, and uncertainty map from the single RGB image; (2) select candidate next viewpoints that reveal high-uncertainty but high-utility regions while avoiding unsupported extrapolation; (3) generate or inpaint the novel view using an image-generation component conditioned on the current render, layout, and object graph; (4) estimate depth/pointmap for the generated view and align it to the accumulated scaffold; (5) compute self-check scores: depth agreement in overlapping regions, object identity consistency, room-boundary consistency, support/collision validity, texture continuity, and uncertainty inflation; (6) accept high-scoring regions, repair local failures through constrained regeneration, or stop expansion with a failure warning; (7) fuse accepted geometry into a renderable mesh or Gaussian representation; (8) output top-level scene graph, occluded-region hypotheses, materials/textures, confidence, and a preview. Datasets: Structured3D and Hypersim for controlled ground truth; Matterport3D and ScanNet for real-world evaluation; 3D-FRONT/3D-FUTURE for object priors and retrieval. Metrics: depth_error, chamfer_distance, layout_iou, object_3d_iou; collision_rate, support_relation_accuracy, object_relation_accuracy, out_of_room_rate; novel_view_consistency, image_reconstruction_lpips, visible_object_recall, object_count_accuracy; occlusion_consistency; confidence_calibration and failure_detection_auc; optional navigation_success_rate in generated scenes. Ablations: no self-check controller; accept-all generation; random viewpoint selection; no repair loop; depth-only checks; semantic-only checks; no uncertainty map; mesh fusion versus 3D Gaussian rendering; controller thresholds tuned for quality versus coverage. Risks: strict checks may reject too many views and produce incomplete rooms; generated images may satisfy 2D semantic checks but still hide impossible 3D geometry; alignment from synthetic generated views may be unstable; runtime may grow with repeated repair. Failure criteria: expansion produces higher collision_rate or worse novel_view_consistency than Text2Room/SceneScape; controller rejection rate exceeds 50% on ordinary indoor images; visible input objects drift or disappear in generated views; failure warnings do not correlate with actual metric failures.

Experiment and implementation plan:
Use the same single input view for all methods, then ask each system to generate a fixed set of held-out viewpoints and a full scene representation. For synthetic scenes, compare generated geometry and rendered views to ground truth. For real scenes, evaluate visible-object preservation, overlap consistency, collision/support checks, and human/VLM-assisted plausibility as secondary analysis. Main comparisons: Text2Room, SceneScape, WonderJourney, an accept-all variant of the proposed method, and depth/layout-only reconstruction. Primary metrics: novel_view_consistency, image_reconstruction_lpips, depth_error in overlapping regions, layout_iou, object_3d_iou where annotated, collision_rate, support_relation_accuracy, out_of_room_rate, occlusion_consistency, confidence_calibration, and failure_detection_auc. Implementation plan: first wrap a Text2Room/SceneScape-like expansion baseline; then add initialization with depth/layout/object graph; implement viewpoint scoring; implement self-check metrics and accept/reject logging; add constrained repair; export final mesh or 3DGS preview; run ablations and qualitative failure taxonomy.

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:3d_scenedreamer_2024; seed:nerf_2020; seed:nerfvs_2023; seed:3dgs_2023; seed:midas_2023; seed:dust3r_2023; seed:mast3r_2024; seed:structured3d_2019; seed:3dfront_2020

---

Idea 3
Title:
Ambiguity-Centered Benchmark for Single-Image 3D Indoor Scene Completion

Core proposal:
Create a benchmark and reference method that evaluate not only one reconstructed room but a distribution of plausible complete 3D indoor scenes from a single RGB image. The benchmark renders controlled single-view observations from full 3D scenes, labels visible versus occluded regions, and scores systems on geometry, relations, uncertainty calibration, and downstream usability. The accompanying lightweight baseline outputs multiple renderable scene graphs with proxy meshes, object poses, materials, occlusion hypotheses, confidence, and failure warnings. Task type: benchmark construction, metric improvement, geometry consistency, single-image 3D generation. Direct baselines: Text2Room, SceneScape, WonderJourney, layout_estimation_baselines, image_to_3d_generation_baselines. Transfer baselines: monocular_depth_estimation, DUSt3R, MASt3R, NeRF, 3D Gaussian Splatting. Borrowed components: 3D-FRONT/3D-FUTURE/Structured3D ground-truth scenes, Matterport3D/ScanNet/Hypersim imagery, object detector, CLIP-like image alignment, scene graph evaluator, physics/collision checker. New component: ambiguity-aware evaluation protocol with visible-region fidelity, occluded-region coverage, top-k plausibility, confidence calibration, and failure-warning metrics. Minimal new module: benchmark generator plus scorer that separates visible, amodal, and fully hidden regions and evaluates both deterministic and multi-hypothesis predictions. MVP artifacts: dataset split definitions, rendering scripts, ground-truth scene graph conversion, metric package, baseline wrappers, leaderboard-style report, and failure case taxonomy.

Motivation or baseline weakness:
Progress in single-image 3D indoor scene generation is limited by ambiguous hidden regions and inconsistent evaluation. A method can appear visually strong while placing objects outside the room, violating support relations, inventing visible objects, or overclaiming hidden geometry. Existing metrics such as depth error or LPIPS are insufficient alone because they do not measure room-level physical plausibility, relation correctness, uncertainty, or downstream use. Novelty relative to supplied work: the cited generation and reconstruction methods are primarily algorithms; this proposal contributes an evaluation benchmark explicitly designed for single-image ambiguity, top-k occluded completions, physical consistency, and failure detection.

Mechanism or approach:
Benchmark design: (1) render single RGB images from 3D-FRONT/Structured3D/Hypersim scenes with known camera intrinsics, layout, object meshes, materials, and full scene graphs; (2) compute visibility masks for surfaces and objects to label visible, partially occluded, and fully hidden components; (3) create ambiguity groups by selecting alternative ground-truth-compatible completions from similar rooms or by perturbing hidden objects within physically valid constraints; (4) define required prediction format: estimated_room_layout, object_instances, object_3d_positions, object_geometry_or_proxy_meshes, spatial_relations, occluded_region_hypotheses, materials_or_textures, render_or_preview, confidence_or_uncertainty, and failure_warning; (5) implement scorers for geometry, relations, image alignment, uncertainty, and downstream simulation readiness; (6) provide a lightweight reference method using monocular depth, layout estimation, object lifting, CAD/proxy retrieval, and stochastic hidden-object placement. Datasets: 3D-FRONT, 3D-FUTURE, Structured3D, Hypersim for controlled benchmark; ScanNet and Matterport3D for external validation where annotations allow. Metrics: depth_error, layout_iou, object_3d_iou, chamfer_distance, collision_rate, support_relation_accuracy, object_relation_accuracy, out_of_room_rate, occlusion_consistency, visible_object_recall, novel_view_consistency, image_reconstruction_lpips, object_count_accuracy, confidence_calibration, ambiguity_detection, failure_detection_auc, navigation_success_rate, embodied_task_success_rate. Ablations: score visible-only versus full-scene; top-1 versus top-k; geometry-only versus geometry-plus-relations; with/without physics checker; with/without uncertainty calibration; synthetic-only versus real validation; CAD-mesh versus primitive-proxy scoring. Risks: synthetic rooms may not reflect real clutter; ground-truth hidden regions are only one valid completion; automatic plausibility metrics may still miss semantic absurdities; downstream evaluation may be expensive. Failure criteria: benchmark ranks obviously colliding/out-of-room scenes highly; uncertainty metrics do not reward calibrated ambiguity; baseline wrappers cannot ingest/export common scene formats; human inspection disagrees strongly with automated rankings.

Experiment and implementation plan:
Release a benchmark with three tiers: Tier 1 visible geometry/layout from a single view; Tier 2 full-scene object/layout completion with top-k hidden hypotheses; Tier 3 downstream usability in simple navigation or embodied interaction tasks. Evaluate baseline systems by adapting outputs to a common scene graph and renderable format. Report per-region metrics: visible pixels/surfaces, partially occluded object parts, and fully hidden regions. Compare Text2Room, SceneScape, WonderJourney, layout-plus-depth baselines, and the provided stochastic scene-graph reference baseline. Include calibration plots showing whether predicted uncertainty rises in truly ambiguous/occluded regions. Implementation plan: month 1 build scene conversion and renderer; month 2 implement visibility/occlusion labeling; month 3 implement metrics and common schema; month 4 wrap baselines and reference method; month 5 run evaluations and human sanity checks; month 6 package benchmark and write benchmark paper. The key publishable claim is that ambiguity-aware metrics expose failure modes not captured by image-level preview or depth metrics alone.

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:3d_scenedreamer_2024; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:dust3r_2023; seed:mast3r_2024; seed:nerf_2020; seed:nerfvs_2023; seed:3dgs_2023; seed:3dfront_2020; seed:3dfuture_2020

### Candidate B

Idea 1
Title:
Layout-Anchored Single-Image Scene Completion with Uncertain Hidden Volumes

Core proposal:
Add a layout-anchored probabilistic volumetric scene graph on top of a single-image generated mesh. The module estimates a Manhattan-style room envelope and monocular depth from the input image, anchors visible objects to reprojection and depth evidence, then samples multiple occluded-volume and support-relation hypotheses constrained to remain inside the room and physically plausible.

Motivation or baseline weakness:
Text2Room and SceneScape can produce visually plausible room meshes from image/text-conditioned generation and depth fusion, but hidden furniture, wall continuations, and floor geometry can drift outside a consistent room layout. They also tend to return one completion without calibrated confidence for occluded regions where many completions are plausible.

Mechanism or approach:
A post-generation constraint-and-uncertainty layer that consumes the baseline mesh, monocular depth, visible object detections, and room layout estimate. It represents hidden space as coarse occupancy cells plus object hypotheses, samples candidates for occluded floor/wall regions, and rejects or downweights samples with wall penetration, floor penetration, unsupported objects, excessive inter-object collision, or contradiction with visible depth.
Maximize visible-image consistency through depth and reprojection agreement while minimizing layout violation, object collision, unsupported-object penalties, and relation inconsistency. The output is a calibrated distribution over occluded occupancy and object/layout completions, plus a deterministic MAP scene for standard mesh metrics.

Experiment and implementation plan:
Text2Room; SceneScape; layout_estimation_baselines; monocular_depth_estimation
Structured3D single-view renders with room layout, object instances, depth, and camera metadata; 3D-FRONT rooms rendered to single RGB views with held-out hidden objects and known layout/object annotations; A real-image stress subset using the same standardized annotation fields where available; otherwise use it only for qualitative failure analysis
run_text2room_or_scenescape_single_image_baseline.py; estimate_layout_and_depth.py; detect_visible_objects.py; sample_occluded_scene_graph.py; check_physics_and_layout_constraints.py; evaluate_scene_completion_metrics.py
layout_iou; depth_error; object_3d_iou; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; occlusion_consistency; visible_object_recall; confidence_calibration
Remove room-layout containment and keep only monocular depth fusion; Use a single MAP hidden-scene completion instead of probabilistic hidden-volume hypotheses; Remove support-relation penalties for objects on floors, tables, and shelves; Replace detector-conditioned visible object anchoring with category priors only; Disable collision rejection during occluded object sampling
Evaluate on images with intentionally corrupted camera intrinsics and require confidence_calibration to worsen or uncertainty to increase rather than silently producing confident completions; Use random room boxes with correct object detections to confirm layout anchoring, not object priors alone, drives out_of_room_rate and layout_iou gains; Shuffle object category priors across rooms to test whether support_relation_accuracy and object_relation_accuracy degrade as expected; Replace estimated depth with spatially shuffled depth while keeping the RGB image fixed to verify visible-object anchoring fails gracefully
Reduce out_of_room_rate by at least 30% relative to Text2Room or SceneScape on Structured3D/3D-FRONT renders; Reduce collision_rate by at least 20% without reducing visible_object_recall by more than 5%; Improve support_relation_accuracy by at least 10 percentage points over the unconstrained generated-mesh baseline; Achieve lower expected calibration error for occluded-region occupancy confidence than deterministic or uncalibrated baselines; Maintain layout_iou within 5% of the layout_estimation_baselines when adding hidden-volume hypotheses

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: layout estimation from narrow-FOV RGB images may be unreliable, making hard constraints harmful. Fallback: use confidence-weighted soft wall, floor, and ceiling penalties; when layout confidence is low, widen the posterior over hidden volumes and report low confidence rather than forcing a brittle room box.

---

Idea 2
Title:
Relation-First Object Proxy Reconstruction for Renderable Indoor Scene Graphs

Core proposal:
Convert the single image into an object-centric scene graph with cuboids or retrieved proxy meshes, then optimize object scale, pose, room containment, and support relations before any texture transfer or inpainting. DUSt3R/MASt3R-style geometry is used only when valid image collections or generated auxiliary views are available; the core single-image path relies on monocular depth, masks, layout, and 3D-FRONT/3D-FUTURE size/support priors.

Motivation or baseline weakness:
Single-image scene generators and image-to-3D baselines can preserve the input-view appearance but often lack object-level 3D proxies that satisfy stable spatial relations such as on, against, inside, left-of, and in-front-of. This limits geometric evaluation, editing, and embodied use even when preview renderings look plausible.

Mechanism or approach:
A differentiable or search-based object proxy optimizer that initializes object cuboids from 2D detections, masks, monocular depth, and layout. It assigns candidate support surfaces, retrieves category-compatible proxy meshes when available, and adjusts 3D positions, scale, and yaw to satisfy relation constraints while preserving visible reprojection alignment.
Minimize a weighted objective combining 2D mask reprojection error, depth consistency, room-layout containment, pairwise collision penalties, support-surface distance, and relation-class penalties. Texture generation or view inpainting is applied only after proxy geometry passes collision, containment, and support checks.

Experiment and implementation plan:
image_to_3d_generation_baselines; Text2Room; WonderJourney; DUSt3R; MASt3R; 3D Gaussian Splatting
3D-FRONT and 3D-FUTURE for object categories, proxy meshes, sizes, and support priors; Structured3D for rendered single-view layout and depth supervision; A held-out rendered single-view split with ground-truth 3D boxes, support relations, and visible masks; Optional real indoor images used only when the same visible-object and relation annotations can be standardized
extract_2d_instances_and_masks.py; estimate_single_view_depth_or_pointmap.py; initialize_object_proxies.py; optimize_scene_graph_relations.py; retrieve_or_fit_proxy_meshes.py; render_scene_preview.py; evaluate_object_relation_metrics.py
object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; visible_object_recall; novel_view_consistency; depth_error; layout_iou
Use direct Text2Room-style mesh fusion without object proxy optimization; Optimize object poses without support-relation terms; Optimize support relations without collision penalties; Use cuboids only versus retrieved 3D-FUTURE proxy meshes; Run texture generation before versus after relation-consistent proxy fitting; Remove room-layout containment while keeping object relation terms
Randomize support-surface assignments while keeping object detections fixed; Use depth estimates with shuffled or incorrect scale to test metric-scale sensitivity; Evaluate on rendered scenes with transparent, reflective, or very thin support surfaces where proxy assumptions should be uncertain; Randomly rotate retrieved proxy meshes within each object category to confirm relation and reprojection metrics detect implausible fits
Improve support_relation_accuracy by at least 15 percentage points over image-to-3D generation baselines; Reduce collision_rate by at least 25% relative to Text2Room or WonderJourney outputs converted to meshes; Improve object_3d_iou by at least 10% on visible major furniture categories in 3D-FRONT renders; Maintain visible_object_recall within 5% of the best direct baseline; Improve novel_view_consistency without increasing out_of_room_rate relative to unconstrained mesh generation

Evidence paper IDs:
seed:text2room_2023; seed:wonderjourney_2023; seed:dust3r_2023; seed:mast3r_2024; seed:3dgs_2023; seed:3dfront_2020; seed:3dfuture_2020; seed:structured3d_2019; seed:midas_2023

Risks, controls, or fallback:
Risk: object detectors and masks may miss heavily occluded or small objects, causing incomplete scene graphs. Fallback: optimize and report major furniture separately from small clutter, keep an uncertain residual occupancy layer for low-confidence regions, and expose low visible_object_recall or mask confidence through confidence_calibration rather than hallucinating precise proxies.

---

Idea 3
Title:
Self-Diagnosing Single-Image 3D Scene Benchmark with Ambiguity-Aware Metrics

Core proposal:
Construct a benchmark protocol that renders many single RGB views from known 3D indoor scenes, hides non-visible ground truth during generation, and scores methods with visible-region geometry metrics plus occluded-region calibration and plausibility checks. Methods may submit meshes, radiance fields, Gaussian splats, or scene graphs, but all submissions must be converted to a minimal common format for core evaluation.

Motivation or baseline weakness:
Existing single-image 3D scene generation evaluations often emphasize rendered preview quality or visible depth, but under-measure ambiguity, occluded-region uncertainty, physical plausibility, relation consistency, and whether a generated scene remains valid when converted into a common 3D representation.

Mechanism or approach:
An evaluation harness that computes visible evidence alignment, hidden-region distributional coverage, scene graph relation correctness, collision/layout violations, uncertainty calibration, and novel-view consistency from a submitted renderable scene or scene graph. The harness records confidence maps or hypothesis weights for ambiguous hidden regions instead of forcing all methods into a single deterministic hidden-scene target.
For each input image, evaluate whether the method produces a renderable scene that matches visible depth/layout/object evidence, assigns calibrated confidence to occluded objects and geometry, avoids physically impossible layouts, and maintains consistency under held-out novel-view rendering.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; Indoor_NeRF_prior_methods; layout_estimation_baselines; monocular_depth_estimation; NeRF; 3D Gaussian Splatting
Structured3D single-view benchmark split with ground-truth layout, depth, object instances, and occlusion masks; 3D-FRONT/3D-FUTURE rendered benchmark split with furniture meshes, object categories, layouts, and material annotations; A synthetic domain-shift split rendered from the same supplied indoor assets with altered lighting, clutter, and camera poses; A small manually checked stress split for corrupted intrinsics, extreme occlusion, reflective surfaces, and missing floor-wall boundaries
render_single_view_benchmark_images.py; compute_visibility_and_occlusion_masks.py; standardize_scene_submission_format.py; evaluate_geometry_and_layout.py; evaluate_scene_graph_relations.py; evaluate_uncertainty_calibration.py; run_collision_checks.py; generate_failure_case_report.py
depth_error; layout_iou; object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; occlusion_consistency; visible_object_recall; novel_view_consistency; confidence_calibration
Score only visible-region geometry versus visible plus occluded-region uncertainty; Use preview-only novel_view_consistency versus full geometric and relation metrics; Remove collision and out-of-room checks from the benchmark score; Treat hidden regions as a single ground truth only versus accepting calibrated multiple hypotheses; Evaluate with and without the synthetic domain-shift stress split
Submit ground-truth visible depth with random hidden geometry to verify occlusion_consistency and confidence_calibration catch implausible completions; Submit visually plausible 2D inpainted previews with no valid 3D object positions to verify object_3d_iou, support_relation_accuracy, and collision_rate expose the failure; Submit overconfident deterministic completions for highly ambiguous views to verify confidence_calibration penalties increase; Submit scenes with all objects inside the room but floating to verify support_relation_accuracy catches the error; Submit valid object proxies with randomized textures to confirm core geometry and relation metrics remain separated from appearance-only effects
Benchmark ranking must separate physically invalid but visually plausible outputs from relation-consistent outputs using collision_rate, support_relation_accuracy, and out_of_room_rate; Confidence_calibration must penalize overconfident hidden-region predictions more than calibrated multi-hypothesis predictions; Occlusion_consistency must decrease for random hidden geometry even when visible depth_error is near optimal; At least three direct baselines must run end-to-end and produce comparable standardized scene submissions; Metric reports must include per-category failure cases for layout, object geometry, relations, occlusion, and novel-view consistency

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:nerf_2020; seed:nerfvs_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:3dgs_2023; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: automatic scene plausibility scoring may be noisy and unfair across mesh, NeRF, Gaussian, and scene-graph outputs. Fallback: require conversion to a minimal common format containing layout, object proxies, render previews, occupancy samples, and confidence maps, while reporting representation-specific metrics separately from the core scene-consistency score.

---

## Item 18: HUM-b8761e7e81

类型：`single_idea`

### Candidate A

Title:
Uncertainty-Aware Occlusion Volumes for Single-Image Room Completion

Core proposal:
Add a post-hoc occlusion-volume sampler that takes a single RGB image, monocular depth, visible object masks, and estimated room-layout planes, then samples a small set of hidden 3D occupancy hypotheses. Each hypothesis represents hidden room cells, candidate object categories, object extents, support surfaces, free-space constraints from the visible image, and confidence over alternatives. The final output contains a most-likely proxy scene plus per-cell and per-object uncertainty maps for occluded regions.

Motivation or baseline weakness:
Text2Room, SceneScape, and WonderJourney can generate plausible hidden room regions, but their outputs are usually consumed as a single deterministic completion. This makes them prone to overconfident hidden-object placement, weak ambiguity reporting, and physically inconsistent completions behind visible occluders.

Mechanism or approach:
A probabilistic scene-graph completion module that samples hidden room cells and candidate proxy objects under layout, depth-ordering, visible-free-space, collision, and support-relation constraints. It is used after existing single-image scene generation or reconstruction baselines and does not train a new large 3D generator.
Maximize a constrained posterior over hidden occupancy and object hypotheses: visible evidence likelihood from masks, depth, and layout; priors over room-bounded object placement and support relations; penalties for collision, out-of-room placement, and violation of visible free space; and a calibration term that aligns predicted confidence with empirical correctness on rendered synthetic validation views. Uncertainty is estimated from normalized posterior mass and ensemble disagreement across sampled hidden completions.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; layout_estimation_baselines; monocular_depth_estimation
Single RGB indoor image with optional camera intrinsics; Visible object masks or detections produced from the input image; Monocular depth prediction from the input image; Estimated room-layout planes from the input image; 3D-FRONT or Structured3D rendered single-view inputs with full ground-truth hidden geometry for evaluation; 3D-FUTURE assets when object proxy meshes are needed for evaluating hidden object extents
run_single_image_baselines.py; estimate_layout_and_depth.py; extract_visible_objects.py; sample_occlusion_volume_hypotheses.py; score_constrained_hidden_hypotheses.py; export_scene_graph_and_proxy_meshes.py; evaluate_occlusion_uncertainty.py; render_preview_views.py
depth_error; layout_iou; object_3d_iou; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; occlusion_consistency; visible_object_recall; confidence_calibration
Remove hidden occupancy uncertainty and output only the MAP completion; Remove support-relation constraints; Remove visible-free-space constraints from monocular depth and masks; Use a single deterministic layout instead of sampled layout perturbations; Replace object-category priors with category-agnostic cuboids; Remove posterior calibration and report raw sample frequency as confidence
Sample hidden objects uniformly without conditioning on visible image cues; Place occluded objects using only 2D inpainting-derived prompts without 3D constraints; Report a constant confidence score for all hidden regions; Ignore visible-free-space constraints while keeping the same object count distribution
Reduce collision_rate by at least 20% relative to Text2Room or SceneScape on matched single-view rendered evaluation; Improve occlusion_consistency by at least 15% over deterministic MAP-only completion; Improve confidence_calibration expected calibration error by at least 25% over constant-confidence and MAP-only controls; Keep visible_object_recall within 3 percentage points of the strongest direct baseline; Improve support_relation_accuracy for hidden-object hypotheses by at least 10 percentage points over uniform hidden-object sampling

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: hidden-region ground truth from synthetic rooms may reward common furniture priors rather than image-conditioned reasoning. Fallback: report visible-region metrics separately from hidden-region plausibility, stratify by occlusion amount, and require improvements in collision_rate, support_relation_accuracy, and confidence_calibration rather than calibration alone. Failure criterion: reject the module if it improves confidence_calibration only by assigning high uncertainty everywhere while failing to improve occlusion_consistency or collision_rate.

### Candidate B

Title:
Uncertainty-Aware Occlusion Volumes for Single-Image Room Completion

Core proposal:
Add a lightweight occlusion-volume sampler that converts monocular depth, visible object masks, and estimated room-layout planes into a compact distribution over hidden occupancy. Each sampled hypothesis contains hidden-room cells, candidate object categories, object-presence probabilities, support constraints, and visible free-space exclusions. The final output includes a most-likely renderable scene plus per-region uncertainty maps and failure flags for ambiguous or inconsistent occluded regions.

Motivation or baseline weakness:
Text2Room, SceneScape, and WonderJourney can generate plausible unseen room regions, but they usually expose a single deterministic completion. This makes hidden object placements appear overconfident, especially behind large occluders or outside the visible frustum, and gives users weak warnings when several completions are equally plausible.

Mechanism or approach:
A post-hoc probabilistic scene-graph completion module that samples hidden room cells and candidate objects under layout, depth-ordering, visible-free-space, collision, and support-relation constraints. It reuses existing single-image generators, depth estimators, and layout estimators rather than training a large 3D generator from scratch.
Maximize a constrained posterior score combining visible-image alignment, room-layout consistency, category-conditioned object priors, and support plausibility, while penalizing collisions, out-of-room geometry, visible-free-space violations, and depth-ordering contradictions. Calibrate hidden-region confidence from disagreement across sampled completions and layout perturbations.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; layout_estimation_baselines; monocular_depth_estimation
Single RGB indoor image with optional camera intrinsics; Visible object detections or masks; Monocular depth prediction; Estimated room layout planes; Rendered 3D-FRONT or Structured3D single-view inputs with full hidden-geometry ground truth for evaluation
run_single_image_baselines.py; estimate_layout_and_depth.py; extract_visible_objects.py; sample_occlusion_volume_hypotheses.py; export_scene_graph_and_proxy_meshes.py; evaluate_occlusion_uncertainty.py; render_preview_views.py
depth_error; layout_iou; object_3d_iou; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; occlusion_consistency; visible_object_recall; confidence_calibration; failure_detection_auc
Output only the maximum-posterior completion without hidden occupancy uncertainty; Remove support-relation constraints; Remove visible-free-space constraints from monocular depth; Use one deterministic layout instead of sampled layout perturbations; Replace object-category priors with category-agnostic cuboids
Sample hidden objects uniformly without conditioning on visible image cues; Place occluded objects using only 2D inpainting prompts without 3D constraints; Report a constant confidence score for all hidden regions
Reduce collision_rate by at least 20% relative to Text2Room or SceneScape under a matched single-view protocol; Improve occlusion_consistency by at least 15% over deterministic completion; Improve confidence_calibration ECE by at least 25% over constant-confidence and MAP-only controls; Keep visible_object_recall within 3 percentage points of the strongest direct baseline; Reach failure_detection_auc above 0.75 for high-ambiguity or severe-layout-failure cases

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023

Risks, controls, or fallback:
Risk: hidden-region ground truth in synthetic datasets may reward common furniture priors more than image-conditioned reasoning. Fallback: report separate results on 3D-FRONT/Structured3D with full ground truth and on real ScanNet or Matterport3D-style images using visible-view consistency, collision checks, and human-rated plausibility. Failure criterion: reject the module if calibration improves only by assigning high entropy everywhere while occlusion_consistency and collision_rate do not improve.

---

## Item 19: HUM-04599c386c

类型：`single_idea`

### Candidate A

Title:
Single-Image Scene Completion Benchmark with Ambiguity-Aware Failure Scoring

Core proposal:
Construct a benchmark from synthetic indoor rooms rendered from one camera, with ground-truth visible geometry, hidden object annotations, multiple plausible completions grouped by room type, and standardized scripts that evaluate renderable scenes or scene graphs for geometry, relations, occlusion uncertainty, and downstream navigation usability.

Motivation or baseline weakness:
Existing single-image scene generation papers can be difficult to compare because visual quality, geometry consistency, hidden-region plausibility, and failure awareness are not evaluated under one controlled single-RGB protocol.

Mechanism or approach:
A benchmark adapter that converts each method output into a common scene-level representation with layout planes, object boxes or meshes, materials, spatial relations, uncertainty fields, render previews, and failure_warning scores.
No large training objective; the experimental objective is standardized measurement. For optional calibration baselines, learn only a lightweight failure-warning calibrator from method diagnostics such as depth residual, collision count, layout confidence, and hidden-area fraction.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; Indoor_NeRF_prior_methods; layout_estimation_baselines; DUSt3R; MASt3R; monocular_depth_estimation
3D-FRONT rooms paired with 3D-FUTURE object meshes and textures; Structured3D images with room layout and depth annotations; Hypersim or ScanNet-style indoor images for out-of-domain qualitative and diagnostic evaluation; Rendered single RGB inputs with camera intrinsics, depth, segmentation, visible-object lists, hidden-object lists, and relation graphs
render_single_view_benchmark.py to generate benchmark images and annotations; standardize_scene_output.py to convert mesh, Gaussian, NeRF, or scene-graph outputs into a common schema; evaluate_layout_geometry.py for layout_iou, depth_error, chamfer_distance, and object_3d_iou; evaluate_relations_physics.py for collision, support, object relation, and out-of-room metrics; evaluate_occlusion_uncertainty.py for hidden-object ambiguity, calibration, and failure detection; evaluate_downstream_navigation.py for simple collision-free navigation and embodied task probes
depth_error; layout_iou; object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; occlusion_consistency; visible_object_recall; novel_view_consistency; image_reconstruction_lpips; object_count_accuracy; confidence_calibration; ambiguity_detection; failure_detection_auc; navigation_success_rate; embodied_task_success_rate
Evaluate with and without camera intrinsics to quantify calibration dependence; Evaluate visible-only regions separately from occluded regions; Score single best completion versus top-K uncertain hypotheses; Compare mesh-based, NeRF-based, Gaussian, and scene-graph-only outputs through the same adapter; Remove physics checks to show whether image metrics alone miss implausible scenes
Submit ground-truth layout with randomized objects to expose relation metric sensitivity; Submit visually plausible 2D inpainted panoramas with no valid 3D geometry to test geometry gates; Submit overconfident hidden-object predictions on ambiguous rooms to test calibration penalties; Submit empty-room completions to test visible_object_recall and object_count_accuracy
Benchmark ranks ground-truth scenes best on at least 90% of geometry and relation metrics; Physics metrics detect randomized-object negative controls with at least 0.85 failure_detection_auc; Image-only baselines should not score high on downstream navigation unless they provide valid 3D geometry, verifying metric separation; Top-K uncertainty scoring should reward calibrated ambiguous completions over overconfident single completions on hidden regions; At least three direct baselines can be run end-to-end and exported into the common schema

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:nerfvs_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:dust3r_2023; seed:mast3r_2024; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: automatic evaluation may still miss human notions of plausibility. Fallback: make the benchmark explicitly multi-axis, report separate geometry, relation, image-alignment, uncertainty, and downstream scores, and include curated failure-case subsets for manual review rather than collapsing quality into one metric.

### Candidate B

Title:
Single-Image Scene Completion Benchmark with Ambiguity-Aware Failure Scoring

Core proposal:
Construct a controlled benchmark from synthetic indoor rooms rendered from one camera, with ground-truth visible geometry, hidden object annotations, room layout, relations, and ambiguity labels derived from groups of similar room configurations. Standardized adapters convert renderable scenes, meshes, radiance fields, pointmaps, or scene graphs into a common representation so metrics can separately score visible reconstruction, hidden completion, physical validity, uncertainty calibration, and failure awareness.

Motivation or baseline weakness:
Existing single-image scene generation and reconstruction papers are difficult to compare because visual quality, geometry consistency, hidden-region plausibility, physical relations, and failure awareness are often evaluated with different inputs and output formats. Multi-view reconstruction methods such as DUSt3R, MASt3R, NeRF, and NeRFVS must therefore be clearly separated from true single-RGB completion methods or run only under controlled adapter settings.

Mechanism or approach:
A benchmark adapter that converts each method output into a common scene-level representation with layout planes, object boxes or meshes, spatial relations, uncertainty fields when available, render previews, and confidence or failure_warning scores. Methods without uncertainty must expose a deterministic confidence proxy so calibration can be evaluated but not confused with true probabilistic completion.
No large training objective is introduced; the core contribution is standardized measurement. For optional reporting, learn only a lightweight validation-set failure-warning calibrator from method diagnostics such as depth residual, collision count, out-of-room count, layout confidence, and hidden-area fraction, and report calibrated and uncalibrated scores separately.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; Indoor_NeRF_prior_methods; layout_estimation_baselines; DUSt3R; MASt3R; monocular_depth_estimation
3D-FRONT rooms paired with 3D-FUTURE object meshes and textures; Structured3D images with room layout and depth annotations; Rendered single RGB inputs with camera intrinsics, depth, segmentation, visible-object lists, hidden-object lists, room boundaries, and relation graphs; Controlled ambiguity groups formed by matching room type, visible layout, and visible object evidence but varying plausible hidden objects
render_single_view_benchmark.py to generate benchmark images and annotations from fixed camera protocols; standardize_scene_output.py to convert mesh, NeRF-style, Gaussian-style, pointmap, or scene-graph outputs into a common schema; evaluate_layout_geometry.py for layout_iou, depth_error, chamfer_distance, and object_3d_iou; evaluate_relations_physics.py for collision_rate, support_relation_accuracy, object_relation_accuracy, and out_of_room_rate; evaluate_occlusion_uncertainty.py for occlusion_consistency, hidden-object calibration, and confidence calibration; run_negative_controls.py to submit randomized, image-only, overconfident, and empty-room controls through the same adapters
depth_error; layout_iou; object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; occlusion_consistency; visible_object_recall; novel_view_consistency; confidence_calibration
Evaluate with and without supplied camera intrinsics to quantify calibration dependence; Evaluate visible regions separately from occluded regions; Score single best completion versus top-K uncertain hypotheses when a method provides multiple completions; Compare mesh-based, NeRF-based, Gaussian-style, pointmap, and scene-graph-only outputs through the same adapter; Remove physics and relation checks to show whether image and depth metrics alone miss implausible scenes
Submit ground-truth layout with randomized objects to expose relation and collision metric sensitivity; Submit visually plausible 2D inpainted panoramas with no valid 3D geometry to test geometry gates; Submit overconfident hidden-object predictions on ambiguous rooms to test calibration penalties; Submit empty-room completions to test visible_object_recall and object_3d_iou; Submit shuffled camera intrinsics to test whether methods and adapters depend on correct single-view geometry
Benchmark ranks ground-truth scenes best on at least 90% of geometry and relation metrics; Physics and relation metrics assign worse scores to randomized-object negative controls than to valid ground truth in at least 85% of benchmark scenes; Image-only or panorama-only controls must not score highly on depth_error, chamfer_distance, object_3d_iou, or novel_view_consistency without valid 3D geometry; Top-K uncertainty scoring rewards calibrated ambiguous completions over overconfident single completions on hidden regions according to confidence_calibration and occlusion_consistency; At least three direct baselines can be run end-to-end and exported into the common schema under the single-RGB protocol

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:nerfvs_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:dust3r_2023; seed:mast3r_2024; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: automatic evaluation may still miss human notions of plausibility. Fallback: report separate geometry, relation, image-alignment, occlusion, and calibration axes instead of a single leaderboard score, and include curated failure-case subsets for manual review while keeping all quantitative metrics reproducible.

---

## Item 20: HUM-59fd7be1b0

类型：`portfolio`

### Candidate A

Idea 1
Title:
Uncertainty-Aware Room Scaffold and Object Proxy Completion from a Single Indoor Image

Core proposal:
Build a scene-level generator that first creates a metric room scaffold and object-centric 3D proxy scene graph from the visible RGB evidence, then samples multiple plausible completions for occluded regions with calibrated uncertainty. Task type: single_image_3d_generation, geometry_consistency, generative_modeling. Direct baselines: Text2Room, SceneScape, WonderJourney, layout_estimation_baselines, image_to_3d_generation_baselines. Transfer baselines: monocular_depth_estimation, DUSt3R, MASt3R, NeRFVS-style geometry scaffold priors. Borrowed components: monocular relative depth, single-image layout estimation, object detector/segmenter, object category-size priors from 3D-FRONT/3D-FUTURE, mesh fusion from Text2Room/SceneScape, and VLM-style consistency verification from WonderJourney. New component: a lightweight probabilistic scaffold module that represents the room as walls/floor/ceiling plus object proxy meshes with distributions over hidden extents, support surfaces, and occluded object hypotheses. Minimal new module: a scene-graph factor optimizer with uncertainty variables for layout scale, object depth, object size, support relation, and hidden object slots. MVP artifacts: JSON scene graph, proxy mesh scene in glTF/OBJ, rendered preview, per-object confidence, occlusion hypothesis list, and failure warning flags.

Motivation or baseline weakness:
Single-image room generation is inherently ambiguous: an image may show only a corner, partial furniture, or strong occlusions. Existing perpetual generation systems can make visually plausible 3D scenes, but they often under-report ambiguity and may place objects with collisions, unsupported geometry, or inconsistent hidden extents. This idea targets downstream usability by producing a conservative renderable scene with explicit uncertainty rather than a single overconfident hallucination.

Mechanism or approach:
Estimate camera intrinsics if absent, predict monocular depth, infer dominant room layout, detect visible objects, and lift visible masks into approximate 3D using depth and layout constraints. Construct a factor graph whose variables include room planes, object 3D boxes, category-conditioned proxy meshes, support/contact relations, and hidden-region slots. Factors encode reprojection consistency to the RGB image, depth agreement, Manhattan-world or room-layout constraints, no-collision constraints, support plausibility, category-size priors, and occlusion ordering. For hidden regions, sample K completions instead of one deterministic scene; each completion contains object hypotheses with confidence intervals and a failure warning if posterior entropy or constraint violation exceeds thresholds. Materials and textures are assigned by projecting visible pixels where available and retrieving category/style-compatible textures for hidden surfaces. Render output can be a proxy mesh preview or optional Gaussian/NeRF refinement initialized from the scaffold. Novelty is not a new large 3D generator; it is the calibrated object-layout-scaffold layer that wraps pretrained single-image and generation components and exposes uncertainty for occluded parts.

Experiment and implementation plan:
Datasets: Structured3D and 3D-FRONT/3D-FUTURE for synthetic ground-truth layout, object boxes, meshes, support relations, and rendered single-image inputs; ScanNet, Matterport3D, or Hypersim for real-image stress tests where available. Metrics: depth_error, layout_iou, object_3d_iou, chamfer_distance for proxy geometry, collision_rate, support_relation_accuracy, object_relation_accuracy, out_of_room_rate, occlusion_consistency, visible_object_recall, object_count_accuracy, novel_view_consistency, image_reconstruction_lpips, confidence_calibration, ambiguity_detection, failure_detection_auc, and downstream navigation_success_rate in a simulator. Ablations: remove uncertainty sampling, remove support/collision factors, replace room scaffold with raw depth lifting, remove category-size priors, use deterministic hidden completion, disable failure warnings, and compare mesh-only versus proxy-plus-renderer outputs. Failure criteria: higher collision_rate or out_of_room_rate than Text2Room/SceneScape-style baselines, poorly calibrated confidence under occlusion, visible object recall below detector baseline, or hidden hypotheses that improve image preview but degrade support_relation_accuracy. Implementation plan: integrate pretrained depth and object/layout predictors; create a canonical scene graph schema; implement factor optimization and sampling; retrieve proxy meshes/materials; render previews; run synthetic evaluation; then test real images and publish benchmark scripts.

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:dust3r_2023; seed:mast3r_2024; seed:nerfvs_2023

---

Idea 2
Title:
Counterfactual Occlusion Benchmark for Single-Image 3D Indoor Scene Completion

Core proposal:
Create a benchmark that evaluates whether single-image 3D indoor scene generators produce geometrically consistent, physically plausible, and uncertainty-aware completions when visible evidence is systematically reduced by synthetic occlusion and camera cropping. Task type: benchmark_construction, metric_improvement, geometry_consistency. Direct baselines: Text2Room, SceneScape, WonderJourney, image_to_3d_generation_baselines, layout_estimation_baselines. Transfer baselines: monocular_depth_estimation, DUSt3R, MASt3R, NeRF, 3D Gaussian Splatting. Borrowed components: rendered single-view images from 3D-FRONT/Structured3D/Hypersim, ground-truth layout and object annotations, object detectors, CLIP/image alignment checks, scene graph evaluators, and physics/collision checkers. New component: a counterfactual occlusion protocol that generates paired images of the same room with controlled visibility masks, making hidden-scene uncertainty measurable rather than purely subjective. Minimal new module: benchmark generator plus evaluator that outputs image, visible mask, hidden mask, ground-truth scene graph, ambiguity class, and metric report. MVP artifacts: dataset split, evaluation server script, baseline wrappers, metric dashboard, and example failure taxonomy.

Motivation or baseline weakness:
Automatic evaluation is a bottleneck for this field. Single-image 3D completion is ambiguous, so scoring only against one full ground-truth room can unfairly penalize plausible alternatives, while image-level preview metrics miss collisions, unsupported objects, and inconsistent occluded geometry. A counterfactual benchmark can separate visible-evidence fidelity from hidden-region plausibility and measure whether uncertainty increases when the image hides crucial evidence.

Mechanism or approach:
Render multiple controlled single-view observations from the same annotated 3D room. For each scene, create counterfactual variants: full-view image, cropped image, object-occluded image, doorway-only view, low-baseline corner view, and heavy furniture occlusion. Run candidate single-image-to-3D systems on each variant. Evaluate visible evidence using reprojection, object recall, depth and layout accuracy. Evaluate hidden completion with tolerance sets: exact-match scores when the hidden region is visible in a paired reference view, category/size/relation plausibility when many completions are acceptable, and calibration scores that reward methods for high uncertainty under high ambiguity. Add physical checks for collisions, object support, out-of-room placement, and navigability. Novelty lies in treating occlusion as a controlled independent variable and explicitly evaluating uncertainty/failure warnings, instead of ranking systems only by visual novelty or one-shot reconstruction error.

Experiment and implementation plan:
Datasets: 3D-FRONT/3D-FUTURE for furnished object-level ground truth, Structured3D for layout-rich scenes, Hypersim for photorealistic rendering, and optional ScanNet/Matterport3D real-image subsets for external validation. Metrics: layout_iou, depth_error, object_3d_iou, chamfer_distance, visible_object_recall, object_count_accuracy, support_relation_accuracy, object_relation_accuracy, collision_rate, out_of_room_rate, occlusion_consistency, novel_view_consistency, image_reconstruction_lpips, confidence_calibration, ambiguity_detection, failure_detection_auc, and downstream navigation_success_rate. Ablations: benchmark with and without controlled occluders, exact ground-truth scoring versus plausibility-set scoring, visible-only metrics versus full-scene metrics, physics metrics versus image-alignment metrics, and calibration-aware ranking versus deterministic ranking. Failure criteria: benchmark fails if rankings are dominated by detector artifacts, if uncertainty metrics do not correlate with occlusion severity, if physically invalid scenes score well, or if baseline wrappers require multi-view inputs inconsistent with the single-image setting. Implementation plan: select annotated rooms, render canonical views and counterfactual occlusion variants, export ground-truth scene graphs and hidden masks, implement metric calculators and failure taxonomy, run Text2Room/SceneScape/WonderJourney-style baselines and depth/layout baselines, release leaderboard splits and reproducible scripts.

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:3d_scenedreamer_2024; seed:structured3d_2019; seed:3dfront_2020; seed:3dfuture_2020; seed:midas_2023; seed:dust3r_2023; seed:mast3r_2024; seed:nerf_2020; seed:3dgs_2023

---

Idea 3
Title:
Scene-Graph-Constrained Gaussian Room Composer for Single-Image Indoor Reconstruction

Core proposal:
Generate a renderable indoor scene by composing object-level proxy meshes and lightweight 3D Gaussian appearance layers under a constrained scene graph inferred from one RGB image. Task type: generative_modeling, single_image_3d_generation, geometry_consistency, metric_improvement. Direct baselines: Text2Room, SceneScape, WonderJourney, Indoor_NeRF_prior_methods, image_to_3d_generation_baselines. Transfer baselines: 3D Gaussian Splatting, NeRF, DUSt3R, MASt3R, monocular_depth_estimation, layout_estimation_baselines. Borrowed components: 3DGS real-time rendering representation, NeRF/NeRFVS geometry scaffold idea, Text2Room/SceneScape-style inpainting and mesh fusion, DUSt3R/MASt3R depth and matching priors where pseudo-views are generated, and 3D-FUTURE object geometry/texture assets. New component: a constrained object-scene composer that binds Gaussians to semantic object proxies and room planes, preventing free-floating radiance artifacts and enabling scene-graph queries. Minimal new module: object-anchored Gaussian initializer and optimizer with collision/support penalties and uncertainty tags for hallucinated regions. MVP artifacts: renderable 3D Gaussian scene, object-level proxy scene graph, editable object transforms, preview video, confidence heatmap, and warnings for unsupported or high-ambiguity regions.

Motivation or baseline weakness:
Radiance-field and Gaussian representations render well, but single-image indoor generation needs editability, object identity, physical constraints, and warning signals. Mesh-only perpetual generation can drift geometrically, while unconstrained Gaussian optimization from one image or pseudo-views can invent inconsistent geometry. Anchoring appearance primitives to a structured scene graph can preserve render quality while maintaining object-level usability.

Mechanism or approach:
From the input image, predict layout planes, monocular depth, visible object masks, category labels, and approximate 3D boxes. Retrieve or generate category-compatible proxy meshes for visible and likely hidden objects. Initialize room-plane Gaussians for walls, floor, and ceiling, and object-bound Gaussians attached to proxy surfaces. Generate a small set of pseudo-views using a Text2Room/SceneScape-like inpainting loop, but accept pseudo-view content only if it is consistent with the current scene graph, depth ordering, and support/collision constraints. Optimize Gaussian colors/opacities/positions with losses for source-view reconstruction, pseudo-view consistency, depth alignment, object-mask reprojection, support relations, and collision avoidance. Each Gaussian or object carries a provenance label: directly visible, extrapolated, or hallucinated; hallucinated objects receive uncertainty scores and can be disabled for conservative downstream use. Novelty is the object-anchored, scene-graph-constrained Gaussian composer for single-image indoor completion, bridging renderable representations with physical and semantic consistency.

Experiment and implementation plan:
Datasets: 3D-FRONT/3D-FUTURE for object geometry and furnished-room supervision, Structured3D for layout evaluation, Hypersim for photorealistic appearance, and ScanNet/Matterport3D for real-world qualitative and partial quantitative tests. Metrics: image_reconstruction_lpips on the input view, novel_view_consistency on held-out rendered views for synthetic scenes, depth_error, layout_iou, object_3d_iou, chamfer_distance, visible_object_recall, object_count_accuracy, support_relation_accuracy, object_relation_accuracy, collision_rate, out_of_room_rate, occlusion_consistency, confidence_calibration, failure_detection_auc, and downstream embodied_task_success_rate or navigation_success_rate using conservative versus full hallucinated scenes. Ablations: free 3DGS without object anchoring, mesh-only Text2Room-style fusion, no pseudo-view verification, no collision/support penalties, no provenance uncertainty labels, proxy meshes only without Gaussian appearance, and Gaussians only without proxy meshes. Failure criteria: Gaussian floaters increase collision/out-of-room rates, pseudo-views override visible image evidence, hidden objects receive high confidence despite ambiguity, novel views look good but object_3d_iou/support accuracy collapses, or runtime exceeds lightweight module constraints. Implementation plan: implement scene graph extraction; retrieve proxy geometry; initialize room/object Gaussians; integrate inpainting-based pseudo-view generation; add graph-constrained Gaussian optimization; export glTF plus Gaussian representation; evaluate against direct single-image-to-3D baselines and reconstruction/rendering transfer baselines.

Evidence paper IDs:
seed:3dgs_2023; seed:nerf_2020; seed:nerfvs_2023; seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:dust3r_2023; seed:mast3r_2024; seed:midas_2023; seed:structured3d_2019; seed:3dfront_2020; seed:3dfuture_2020

### Candidate B

Idea 1
Title:
Uncertainty-Aware Occlusion Volumes for Single-Image Room Completion

Core proposal:
Add a post-hoc occlusion-volume sampler that takes a single RGB image, monocular depth, visible object masks, and estimated room-layout planes, then samples a small set of hidden 3D occupancy hypotheses. Each hypothesis represents hidden room cells, candidate object categories, object extents, support surfaces, free-space constraints from the visible image, and confidence over alternatives. The final output contains a most-likely proxy scene plus per-cell and per-object uncertainty maps for occluded regions.

Motivation or baseline weakness:
Text2Room, SceneScape, and WonderJourney can generate plausible hidden room regions, but their outputs are usually consumed as a single deterministic completion. This makes them prone to overconfident hidden-object placement, weak ambiguity reporting, and physically inconsistent completions behind visible occluders.

Mechanism or approach:
A probabilistic scene-graph completion module that samples hidden room cells and candidate proxy objects under layout, depth-ordering, visible-free-space, collision, and support-relation constraints. It is used after existing single-image scene generation or reconstruction baselines and does not train a new large 3D generator.
Maximize a constrained posterior over hidden occupancy and object hypotheses: visible evidence likelihood from masks, depth, and layout; priors over room-bounded object placement and support relations; penalties for collision, out-of-room placement, and violation of visible free space; and a calibration term that aligns predicted confidence with empirical correctness on rendered synthetic validation views. Uncertainty is estimated from normalized posterior mass and ensemble disagreement across sampled hidden completions.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; layout_estimation_baselines; monocular_depth_estimation
Single RGB indoor image with optional camera intrinsics; Visible object masks or detections produced from the input image; Monocular depth prediction from the input image; Estimated room-layout planes from the input image; 3D-FRONT or Structured3D rendered single-view inputs with full ground-truth hidden geometry for evaluation; 3D-FUTURE assets when object proxy meshes are needed for evaluating hidden object extents
run_single_image_baselines.py; estimate_layout_and_depth.py; extract_visible_objects.py; sample_occlusion_volume_hypotheses.py; score_constrained_hidden_hypotheses.py; export_scene_graph_and_proxy_meshes.py; evaluate_occlusion_uncertainty.py; render_preview_views.py
depth_error; layout_iou; object_3d_iou; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; occlusion_consistency; visible_object_recall; confidence_calibration
Remove hidden occupancy uncertainty and output only the MAP completion; Remove support-relation constraints; Remove visible-free-space constraints from monocular depth and masks; Use a single deterministic layout instead of sampled layout perturbations; Replace object-category priors with category-agnostic cuboids; Remove posterior calibration and report raw sample frequency as confidence
Sample hidden objects uniformly without conditioning on visible image cues; Place occluded objects using only 2D inpainting-derived prompts without 3D constraints; Report a constant confidence score for all hidden regions; Ignore visible-free-space constraints while keeping the same object count distribution
Reduce collision_rate by at least 20% relative to Text2Room or SceneScape on matched single-view rendered evaluation; Improve occlusion_consistency by at least 15% over deterministic MAP-only completion; Improve confidence_calibration expected calibration error by at least 25% over constant-confidence and MAP-only controls; Keep visible_object_recall within 3 percentage points of the strongest direct baseline; Improve support_relation_accuracy for hidden-object hypotheses by at least 10 percentage points over uniform hidden-object sampling

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: hidden-region ground truth from synthetic rooms may reward common furniture priors rather than image-conditioned reasoning. Fallback: report visible-region metrics separately from hidden-region plausibility, stratify by occlusion amount, and require improvements in collision_rate, support_relation_accuracy, and confidence_calibration rather than calibration alone. Failure criterion: reject the module if it improves confidence_calibration only by assigning high uncertainty everywhere while failing to improve occlusion_consistency or collision_rate.

---

Idea 2
Title:
Physics-Checked Object Proxy Fitting for Renderable Single-Image Scene Graphs

Core proposal:
Add a lightweight object proxy fitting loop that converts visible generated or detected objects into category-aware cuboids or retrieved 3D-FUTURE proxy meshes. Object scale, yaw, translation, and support assignment are optimized against 2D masks, monocular depth, estimated room layout, category scale priors, support constraints, collision penalties, and out-of-room penalties. The output is a renderable proxy scene graph with per-object physical consistency warnings and uncertainty intervals from multi-start fitting.

Motivation or baseline weakness:
Single-image scene generators and monocular reconstruction methods can produce visually acceptable previews while placing objects at implausible 3D scale, support, orientation, or room location. These errors are hidden by image-space quality but harm renderable scene graphs, relation reasoning, and downstream navigation-like checks.

Mechanism or approach:
A constrained 3D object-layout optimizer over object scale, yaw, translation, support surface, and uncertainty intervals, initialized from single-image masks, monocular depth, and room layout. It replaces or augments raw generated geometry with physically checked proxy geometry while preserving the baseline's visible object set whenever possible.
Minimize a weighted objective consisting of 2D mask reprojection error, monocular depth residuals on visible object pixels, layout-boundary violations, support-relation violations, object-object intersections, out-of-room penalties, and category scale-prior penalties. Estimate uncertainty from the spread of feasible low-energy solutions across randomized initializations and layout/depth perturbations.

Experiment and implementation plan:
Text2Room; image_to_3d_generation_baselines; layout_estimation_baselines; monocular_depth_estimation; DUSt3R
Single RGB indoor image; Camera intrinsics if available or an estimated focal length; Object masks and categories inferred from the single image; Monocular depth prediction from the single image; DUSt3R pointmaps only for diagnostic settings where additional views are available and clearly marked non-strict; Estimated room layout planes; 3D-FRONT rendered single-view scenes with ground-truth object poses for evaluation; 3D-FUTURE proxy furniture assets for mesh retrieval and category scale priors
detect_and_segment_objects.py; estimate_depth_or_pointmap.py; fit_room_layout.py; initialize_object_proxies.py; optimize_object_proxy_scene.py; check_physics_and_collisions.py; export_renderable_scene_graph.py; evaluate_scene_graph_geometry.py
object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; visible_object_recall; depth_error; layout_iou; confidence_calibration
Remove collision penalty; Remove support-surface assignment; Use 2D boxes instead of masks; Use fixed category-average object sizes instead of optimized scales; Disable multi-start uncertainty estimation; Use generated mesh geometry directly without proxy fitting; Remove category scale priors
Randomly assign support surfaces while preserving 2D detections; Optimize only image reprojection with no physical terms; Fit all objects on the floor regardless of category; Evaluate with shuffled object categories to test dependence on semantic priors; Shrink every object by a fixed factor to test whether lower collision is achieved by degenerate geometry
Reduce collision_rate by at least 30% versus the raw generated scene representation; Improve support_relation_accuracy by at least 10 percentage points over direct baselines; Improve object_3d_iou by at least 10% on 3D-FRONT rendered single-view evaluation; Keep visible_object_recall within 5 percentage points of the raw baseline; Reduce out_of_room_rate by at least 20% without degrading object_3d_iou or visible_object_recall

Evidence paper IDs:
seed:text2room_2023; seed:3d_scenedreamer_2024; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:dust3r_2023; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: proxy meshes may improve physical metrics while reducing visual fidelity for irregular or partially visible objects. Fallback: keep high-fidelity generated textures or meshes as visual overlays, but use proxy geometry for collisions, support relations, and scene-graph export. Failure criterion: the method fails if physical consistency improves mainly by deleting, shrinking, or flattening objects, measured by drops in visible_object_recall, object_3d_iou, or support_relation_accuracy under the shrinkage negative control.

---

Idea 3
Title:
Single-Image Scene Completion Benchmark with Ambiguity-Stratified Evaluation

Core proposal:
Construct an ambiguity-stratified benchmark from evidence-supported indoor datasets by rendering single RGB views with known camera intrinsics, full 3D ground truth, visible and hidden object labels, layout annotations, and derived sets of physically plausible alternative hidden completions. Evaluate methods with separate visible-region reconstruction scores, hidden-region plausibility scores, physical relation checks, uncertainty calibration, and compliance labels indicating whether each method used only the single RGB input.

Motivation or baseline weakness:
Existing single-image-to-3D room methods are hard to compare because image-level preview quality can hide geometry errors, occluded regions are inherently multi-modal, and some baselines use extra prompts, generated views, camera paths, or iterative exploration that violate a strict single-RGB input protocol.

Mechanism or approach:
A dataset-generation and evaluator layer that labels each test view by occlusion fraction, layout visibility, object truncation, visible-object count, hidden-object count, and physical-constraint difficulty. It also defines a standardized JSON scene-graph schema for method outputs, including camera, layout, objects, support relations, uncertainty fields, and confidence values.
Define an evaluation score that rewards visible-image-grounded geometry and physically valid scene structure while avoiding over-penalization of ambiguous hidden regions. Visible regions are scored against ground truth, while hidden completions are scored using plausibility sets, support and collision validity, calibrated uncertainty, and consistency with visible free space. Scores are always reported by ambiguity stratum and by input-protocol compliance.

Experiment and implementation plan:
Text2Room; SceneScape; WonderJourney; Indoor_NeRF_prior_methods; layout_estimation_baselines; image_to_3d_generation_baselines; monocular_depth_estimation; DUSt3R; MASt3R; NeRF
3D-FRONT furnished rooms with 3D-FUTURE assets; Structured3D scenes with layout and structure annotations; Rendered single RGB images with camera intrinsics; Ground-truth room layouts, object poses, meshes, materials, and visibility masks from rendered scenes; Derived visible/hidden masks, free-space masks, support relations, and collision annotations; Optional method-native diagnostic inputs recorded separately from the strict single-RGB benchmark track
render_single_view_benchmark.py; compute_visible_hidden_masks.py; generate_ambiguity_labels.py; derive_plausible_hidden_completion_sets.py; convert_outputs_to_scene_schema.py; check_input_protocol_compliance.py; evaluate_geometry_consistency.py; evaluate_scene_relations.py; evaluate_uncertainty_calibration.py; baseline_runner_wrappers.py
depth_error; layout_iou; object_3d_iou; chamfer_distance; collision_rate; support_relation_accuracy; object_relation_accuracy; out_of_room_rate; occlusion_consistency; visible_object_recall; novel_view_consistency; confidence_calibration
Score hidden regions deterministically against one ground-truth completion; Remove ambiguity stratification; Remove physics and collision checks from the benchmark score; Evaluate only depth_error and novel_view_consistency; Use no standardized scene-graph schema; Do not separate visible and occluded objects; Ignore input-protocol compliance when comparing methods
Submit ground-truth visible geometry with random hidden objects; Submit visually plausible 2D inpainted views with no valid 3D scene graph; Submit empty-room completions to test whether metrics penalize missing objects; Submit overconfident confidence maps for all hidden regions; Submit a method-native run that uses extra views or prompts and mark it as non-strict to test protocol reporting
Baseline ranking changes when geometry, relation, and uncertainty metrics are added compared with novel_view_consistency-only evaluation; The evaluator penalizes random-hidden-object controls with at least 50% worse occlusion_consistency than compliant direct baselines; Confidence_calibration separates overconfident hidden-region submissions from calibrated uncertainty outputs; Ambiguity-stratified subsets show monotonic degradation in occlusion_consistency and object_3d_iou as occlusion fraction increases; The benchmark runs at least three direct baselines under the same strict single-RGB input protocol and flags non-compliant runs separately

Evidence paper IDs:
seed:text2room_2023; seed:scenescape_2023; seed:wonderjourney_2023; seed:nerf_2020; seed:nerfvs_2023; seed:horizonnet_2019; seed:structured3d_2019; seed:midas_2023; seed:dust3r_2023; seed:mast3r_2024; seed:3dfront_2020; seed:3dfuture_2020

Risks, controls, or fallback:
Risk: benchmark construction may be viewed as dataset engineering rather than a model contribution, and synthetic rendered rooms may not capture all real-image ambiguity. Fallback: keep the MVP focused on 3D-FRONT and Structured3D rendered splits with transparent ambiguity labels, strong negative controls, and strict input-protocol reporting; add real-image diagnostics only as non-primary evaluation if no full 3D ground truth is available. Failure criterion: the benchmark is not useful if simple negative controls score similarly to strong baselines, if rankings are dominated by a single view-consistency metric, or if methods using extra inputs are not clearly separated from strict single-RGB submissions.

---
