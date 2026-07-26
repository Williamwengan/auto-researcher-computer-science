# Evidence-Grounded Baseline Context

Focus area: industrial anomaly detection with agentic inspection workflow

## Baseline Evidence Cards

### PatchCore (strong)
- Type: iad_models
- Claimed task: industrial anomaly detection with agentic inspection workflow
- Evidence papers:
  - `openalex:W7162893906` AnomalyAgent: Training-Free Agentic Models for Zero-/Few-Shot Anomaly Detection (2026) https://openalex.org/W7162893906
  - `openalex:W4415239807` PB-IAD: Utilizing multimodal foundation models for semantic industrial anomaly detection in dynamic manufacturing environments (2025) https://doi.org/10.48550/arxiv.2508.14504
  - `openalex:W4404704036` A Comprehensive Investigation of Anomaly Detection Methods in Deep Learning and Machine Learning: 2019–2023 (2024) https://doi.org/10.1049/2024/8821891
- Known limitations:
  - Nearest-neighbor normal memory may be sensitive to reference shift or contaminated normal banks.
  - Patch anomaly heatmaps do not by themselves provide evidence-grounded inspection reports.

### PaDiM (strong)
- Type: iad_models
- Claimed task: industrial anomaly detection with agentic inspection workflow
- Evidence papers:
  - `openalex:W7154655652` IAD-Unify: A Region-Grounded Unified Model for Industrial Anomaly Segmentation, Understanding, and Generation (2026) https://openalex.org/W7154655652
  - `openalex:W7165826198` Applications of Machine Learning: Feature Extraction and 3D Anomaly Detection. (2026) https://openalex.org/W7165826198
  - `openalex:W4404704036` A Comprehensive Investigation of Anomaly Detection Methods in Deep Learning and Machine Learning: 2019–2023 (2024) https://doi.org/10.1049/2024/8821891
- Known limitations:
  - Limitations require manual verification against retrieved evidence.

### FastFlow (strong)
- Type: iad_models
- Claimed task: industrial anomaly detection with agentic inspection workflow
- Evidence papers:
  - `openalex:W7141157128` Proceedings of the Second Workshop on AI in Production (2026) https://doi.org/10.20378/irb-114337
  - `openalex:W2922785603` Why High-Performance Modelling and Simulation for Big Data Applications Matters (2019) https://doi.org/10.1007/978-3-030-16272-6_1
  - `openalex:W3165278286` High-Performance Modelling and Simulation for Big Data Applications (2019) https://doi.org/10.1007/978-3-030-16272-6
- Known limitations:
  - Limitations require manual verification against retrieved evidence.

### DRAEM (strong)
- Type: iad_models
- Claimed task: industrial anomaly detection with agentic inspection workflow
- Evidence papers:
  - `openalex:W7153670799` AnomalyAgent: Agentic Industrial Anomaly Synthesis via Tool-Augmented Reinforcement Learning (2026) https://openalex.org/W7153670799
  - `openalex:W7154655652` IAD-Unify: A Region-Grounded Unified Model for Industrial Anomaly Segmentation, Understanding, and Generation (2026) https://openalex.org/W7154655652
- Known limitations:
  - Limitations require manual verification against retrieved evidence.

### RD4AD (medium)
- Type: iad_models
- Claimed task: industrial anomaly detection with agentic inspection workflow
- Evidence papers:
  - `openalex:W7154655652` IAD-Unify: A Region-Grounded Unified Model for Industrial Anomaly Segmentation, Understanding, and Generation (2026) https://openalex.org/W7154655652
- Known limitations:
  - Limitations require manual verification against retrieved evidence.

### WinCLIP (strong)
- Type: iad_models
- Claimed task: industrial anomaly detection with agentic inspection workflow
- Evidence papers:
  - `openalex:W7162893906` AnomalyAgent: Training-Free Agentic Models for Zero-/Few-Shot Anomaly Detection (2026) https://openalex.org/W7162893906
  - `openalex:W4415239807` PB-IAD: Utilizing multimodal foundation models for semantic industrial anomaly detection in dynamic manufacturing environments (2025) https://doi.org/10.48550/arxiv.2508.14504
  - `openalex:W4380551232` A Survey on Segment Anything Model (SAM): Vision Foundation Model Meets Prompt Engineering (2023) https://doi.org/10.48550/arxiv.2306.06211
- Known limitations:
  - Semantic predictions may be unsupported by localized visual evidence.
  - Prompt-sensitive predictions require calibration or verification.

### AnomalyCLIP (strong)
- Type: iad_models
- Claimed task: industrial anomaly detection with agentic inspection workflow
- Evidence papers:
  - `openalex:W7162893906` AnomalyAgent: Training-Free Agentic Models for Zero-/Few-Shot Anomaly Detection (2026) https://openalex.org/W7162893906
  - `openalex:W7153328271` Agentic and LLM-Based Multimodal Anomaly Detection: Architectures, Challenges, and Prospects (2026) https://doi.org/10.3390/s26082330
  - `openalex:W7138099583` AD-FM: Multimodal LLMs for Anomaly Detection via Multi-Stage Reasoning and Fine-Grained Reward Optimization (2026)
- Known limitations:
  - Semantic predictions may be unsupported by localized visual evidence.
  - Prompt-sensitive predictions require calibration or verification.

### SAM (strong)
- Type: segmentation_and_detection
- Claimed task: industrial anomaly detection with agentic inspection workflow
- Evidence papers:
  - `openalex:W4380551232` A Survey on Segment Anything Model (SAM): Vision Foundation Model Meets Prompt Engineering (2023) https://doi.org/10.48550/arxiv.2306.06211
  - `openalex:W4320559301` Generalized Video Anomaly Event Detection: Systematic Taxonomy and Comparison of Deep Models (2023) https://doi.org/10.48550/arxiv.2302.05087
  - `openalex:W4401273105` A Comprehensive Survey on Advanced Persistent Threat (APT) Detection Techniques (2024) https://doi.org/10.32604/cmc.2024.052447
- Known limitations:
  - Promptable masks may segment salient regions rather than task-specific failure regions.
  - Mask refinement needs a selection policy and negative controls.

### SAM2 (strong)
- Type: segmentation_and_detection
- Claimed task: industrial anomaly detection with agentic inspection workflow
- Evidence papers:
  - `openalex:W7140238255` Synergistic Perception and Generative Recomposition: A Multi-Agent Orchestration for Expert-Level Building Inspection (2026) https://openalex.org/W7140238255
  - `openalex:W7135065747` An Integrated Smart Manufacturing Framework Based on Industrial Monitoring and Artificial Intelligence (2026) https://doi.org/10.23939/mmc2026.01.165
  - `openalex:W4380551232` A Survey on Segment Anything Model (SAM): Vision Foundation Model Meets Prompt Engineering (2023) https://doi.org/10.48550/arxiv.2306.06211
- Known limitations:
  - Promptable masks may segment salient regions rather than task-specific failure regions.
  - Mask refinement needs a selection policy and negative controls.

### GroundingDINO (strong)
- Type: segmentation_and_detection
- Claimed task: industrial anomaly detection with agentic inspection workflow
- Evidence papers:
  - `openalex:W4416423039` Agentic AI for Computer Vision: A Review (2025) https://doi.org/10.31224/5832
  - `openalex:W4388685466` Large Language Models for Robotics: A Survey (2023) https://doi.org/10.48550/arxiv.2311.07226
- Known limitations:
  - Limitations require manual verification against retrieved evidence.

### Mask2Former (strong)
- Type: segmentation_and_detection
- Claimed task: industrial anomaly detection with agentic inspection workflow
- Evidence papers:
  - `openalex:W7131301433` Localizing Perceptual Artifacts in Synthetic Images for Image Quality Assessment via Deep-Learning-Based Anomaly Detection (2026) https://doi.org/10.3390/electronics15050916
  - `openalex:W4414431285` A modified vision transformer framework for image-based land cover segmentation in rural architectural design and planning (2025) https://doi.org/10.1038/s41598-025-19234-w
  - `openalex:W7126038314` A Hybrid Deep Learning Framework for Automated Dental Disorder Diagnosis from X-Ray Images (2026) https://doi.org/10.3390/jcm15031076
- Known limitations:
  - Limitations require manual verification against retrieved evidence.

### CLIP (strong)
- Type: multimodal_and_agent_models
- Claimed task: industrial anomaly detection with agentic inspection workflow
- Evidence papers:
  - `openalex:W4412505619` AI Agents vs. Agentic AI: A Conceptual Taxonomy, Applications and Challenges (2025) https://doi.org/10.70777/si.v2i3.15161
  - `openalex:W4404704036` A Comprehensive Investigation of Anomaly Detection Methods in Deep Learning and Machine Learning: 2019–2023 (2024) https://doi.org/10.1049/2024/8821891
  - `openalex:W3194730353` Deep Learning: A Comprehensive Overview on Techniques, Taxonomy, Applications and Research Directions (2021) https://doi.org/10.1007/s42979-021-00815-1
- Known limitations:
  - Semantic predictions may be unsupported by localized visual evidence.
  - Prompt-sensitive predictions require calibration or verification.

## Top Retrieved Papers

- `openalex:W7153670799` AnomalyAgent: Agentic Industrial Anomaly Synthesis via Tool-Augmented Reinforcement Learning (2026) score=12.0 url=https://openalex.org/W7153670799
- `openalex:W7162893906` AnomalyAgent: Training-Free Agentic Models for Zero-/Few-Shot Anomaly Detection (2026) score=10.0 url=https://openalex.org/W7162893906
- `openalex:W7154655652` IAD-Unify: A Region-Grounded Unified Model for Industrial Anomaly Segmentation, Understanding, and Generation (2026) score=10.0 url=https://openalex.org/W7154655652
- `openalex:W4415239807` PB-IAD: Utilizing multimodal foundation models for semantic industrial anomaly detection in dynamic manufacturing environments (2025) score=9.917 url=https://doi.org/10.48550/arxiv.2508.14504
- `openalex:W7153328271` Agentic and LLM-Based Multimodal Anomaly Detection: Architectures, Challenges, and Prospects (2026) score=9.0 url=https://doi.org/10.3390/s26082330
- `openalex:W7165826198` Applications of Machine Learning: Feature Extraction and 3D Anomaly Detection. (2026) score=8.0 url=https://openalex.org/W7165826198
- `openalex:W7138099583` AD-FM: Multimodal LLMs for Anomaly Detection via Multi-Stage Reasoning and Fine-Grained Reward Optimization (2026) score=8.0
- `openalex:W7131301433` Localizing Perceptual Artifacts in Synthetic Images for Image Quality Assessment via Deep-Learning-Based Anomaly Detection (2026) score=8.0 url=https://doi.org/10.3390/electronics15050916
- `openalex:W7140238255` Synergistic Perception and Generative Recomposition: A Multi-Agent Orchestration for Expert-Level Building Inspection (2026) score=7.0 url=https://openalex.org/W7140238255
- `openalex:W4412505619` AI Agents vs. Agentic AI: A Conceptual Taxonomy, Applications and Challenges (2025) score=6.917 url=https://doi.org/10.70777/si.v2i3.15161
- `openalex:W7135065747` An Integrated Smart Manufacturing Framework Based on Industrial Monitoring and Artificial Intelligence (2026) score=6.0 url=https://doi.org/10.23939/mmc2026.01.165
- `openalex:W4414431285` A modified vision transformer framework for image-based land cover segmentation in rural architectural design and planning (2025) score=5.917 url=https://doi.org/10.1038/s41598-025-19234-w
- `openalex:W4404704036` A Comprehensive Investigation of Anomaly Detection Methods in Deep Learning and Machine Learning: 2019–2023 (2024) score=5.833 url=https://doi.org/10.1049/2024/8821891
- `openalex:W4380551232` A Survey on Segment Anything Model (SAM): Vision Foundation Model Meets Prompt Engineering (2023) score=4.75 url=https://doi.org/10.48550/arxiv.2306.06211
- `openalex:W7141157128` Proceedings of the Second Workshop on AI in Production (2026) score=4.0 url=https://doi.org/10.20378/irb-114337
- `openalex:W7126038314` A Hybrid Deep Learning Framework for Automated Dental Disorder Diagnosis from X-Ray Images (2026) score=4.0 url=https://doi.org/10.3390/jcm15031076
- `openalex:W4416423039` Agentic AI for Computer Vision: A Review (2025) score=3.917 url=https://doi.org/10.31224/5832
- `openalex:W4320559301` Generalized Video Anomaly Event Detection: Systematic Taxonomy and Comparison of Deep Models (2023) score=3.75 url=https://doi.org/10.48550/arxiv.2302.05087
- `openalex:W4401273105` A Comprehensive Survey on Advanced Persistent Threat (APT) Detection Techniques (2024) score=2.833 url=https://doi.org/10.32604/cmc.2024.052447
- `openalex:W4404996726` A novel knowledge distillation framework for enhancing small object detection in blurry environments with unmanned aerial vehicle-assisted images (2024) score=2.833 url=https://doi.org/10.1007/s40747-024-01676-w
- `openalex:W4388685466` Large Language Models for Robotics: A Survey (2023) score=2.75 url=https://doi.org/10.48550/arxiv.2311.07226
- `openalex:W2922785603` Why High-Performance Modelling and Simulation for Big Data Applications Matters (2019) score=1.417 url=https://doi.org/10.1007/978-3-030-16272-6_1
- `openalex:W3165278286` High-Performance Modelling and Simulation for Big Data Applications (2019) score=1.417 url=https://doi.org/10.1007/978-3-030-16272-6
- `openalex:W3194730353` Deep Learning: A Comprehensive Overview on Techniques, Taxonomy, Applications and Research Directions (2021) score=0.583 url=https://doi.org/10.1007/s42979-021-00815-1
