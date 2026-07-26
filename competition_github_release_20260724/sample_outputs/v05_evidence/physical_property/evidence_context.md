# Evidence-Grounded Baseline Context

Focus area: object-level physical property prediction from 2D indoor scene images

## Baseline Evidence Cards

### GroundingDINO (strong)
- Type: detection_and_segmentation
- Claimed task: object-level physical property prediction from 2D indoor scene images
- Evidence papers:
  - `openalex:W4402427278` SceneGPT: A Language Model for 3D Scene Understanding (2024) https://doi.org/10.48550/arxiv.2408.06926
  - `openalex:W4402500749` Segment Anything for Videos: A Systematic Survey (2024) https://doi.org/10.48550/arxiv.2408.08315
  - `openalex:W4411238954` Comprehensive review of recent developments in visual object detection based on deep learning (2025) https://doi.org/10.1007/s10462-025-11284-w
- Known limitations:
  - Single RGB images may not reveal hidden material composition.
  - Exact physical-property labels may require proxy, interval, or uncertainty-aware supervision.

### SAM (strong)
- Type: detection_and_segmentation
- Claimed task: object-level physical property prediction from 2D indoor scene images
- Evidence papers:
  - `openalex:W3022851742` Investigations of Object Detection in Images/Videos Using Various Deep Learning Techniques and Embedded Platforms—A Comprehensive Review (2020) https://doi.org/10.3390/app10093280
  - `openalex:W4391809438` A Review of Sensing Technologies for Indoor Autonomous Mobile Robots (2024) https://doi.org/10.3390/s24041222
  - `openalex:W4367665525` Deep Learning for Automatic Vision-Based Recognition of Industrial Surface Defects: A Survey (2023) https://doi.org/10.1109/access.2023.3271748
- Known limitations:
  - Promptable masks may segment salient regions rather than task-specific failure regions.
  - Mask refinement needs a selection policy and negative controls.

### SAM2 (strong)
- Type: detection_and_segmentation
- Claimed task: object-level physical property prediction from 2D indoor scene images
- Evidence papers:
  - `openalex:W7148178853` Live Interactive Training for Video Segmentation (2026) https://openalex.org/W7148178853
  - `openalex:W4416850904` A Review of Deep Learning Approaches Based on Segment Anything Model for Medical Image Segmentation (2025) https://doi.org/10.3390/bioengineering12121312
  - `openalex:W4403323960` On Efficient Variants of Segment Anything Model: A Survey (2024) https://doi.org/10.48550/arxiv.2410.04960
- Known limitations:
  - Promptable masks may segment salient regions rather than task-specific failure regions.
  - Mask refinement needs a selection policy and negative controls.

### Mask2Former (strong)
- Type: detection_and_segmentation
- Claimed task: object-level physical property prediction from 2D indoor scene images
- Evidence papers:
  - `openalex:W4411238954` Comprehensive review of recent developments in visual object detection based on deep learning (2025) https://doi.org/10.1007/s10462-025-11284-w
  - `openalex:W4385327621` Foundational Models Defining a New Era in Vision: A Survey and Outlook (2023) https://doi.org/10.48550/arxiv.2307.13721
  - `openalex:W7155417107` AI-enabled digital twin framework for reconfigurable robotic palletizing of irregularly shaped products (2026) https://doi.org/10.1007/s00170-026-18109-2
- Known limitations:
  - Single RGB images may not reveal hidden material composition.
  - Exact physical-property labels may require proxy, interval, or uncertainty-aware supervision.

### CLIP (strong)
- Type: material_recognition
- Claimed task: object-level physical property prediction from 2D indoor scene images
- Evidence papers:
  - `openalex:W3047386722` A Survey of Computer Vision Methods for 2D Object Detection from Unmanned Aerial Vehicles (2020) https://doi.org/10.3390/jimaging6080078
  - `openalex:W2963557767` Stereo magnification (2018) https://doi.org/10.1145/3197517.3201323
  - `openalex:W2461758788` Local Background Enclosure for RGB-D Salient Object Detection (2016) https://doi.org/10.1109/cvpr.2016.257
- Known limitations:
  - Semantic predictions may be unsupported by localized visual evidence.
  - Prompt-sensitive predictions require calibration or verification.

### OpenSurfaces (strong)
- Type: material_recognition
- Claimed task: object-level physical property prediction from 2D indoor scene images
- Evidence papers:
  - `openalex:W2798280964` Gaussian material synthesis (2018) https://doi.org/10.1145/3197517.3201307
  - `openalex:W3012463097` Terrain Segmentation and Roughness Estimation using RGB Data: Path Planning Application on the CENTAURO Robot (2019) https://doi.org/10.1109/humanoids43949.2019.9035009
  - `openalex:W2895238724` From BoW to CNN: Two Decades of Texture Representation for Texture Classification (2018) https://doi.org/10.1007/s11263-018-1125-z
- Known limitations:
  - Single RGB images may not reveal hidden material composition.
  - Exact physical-property labels may require proxy, interval, or uncertainty-aware supervision.

### MINC (strong)
- Type: material_recognition
- Claimed task: object-level physical property prediction from 2D indoor scene images
- Evidence papers:
  - `openalex:W3046559354` An application independent review of multimodal 3D registration methods (2020) https://doi.org/10.1016/j.cag.2020.07.012
  - `openalex:W4362553764` On the Analyses of Medical Images Using Traditional Machine Learning Techniques and Convolutional Neural Networks (2023) https://doi.org/10.1007/s11831-023-09899-9
  - `openalex:W2895238724` From BoW to CNN: Two Decades of Texture Representation for Texture Classification (2018) https://doi.org/10.1007/s11263-018-1125-z
- Known limitations:
  - Single RGB images may not reveal hidden material composition.
  - Exact physical-property labels may require proxy, interval, or uncertainty-aware supervision.

### BLIP-2 (strong)
- Type: vision_language_models
- Claimed task: object-level physical property prediction from 2D indoor scene images
- Evidence papers:
  - `openalex:W4392222076` MoodCapture: Depression Detection using In-the-Wild Smartphone Images (2024) https://doi.org/10.1145/3613904.3642680
  - `openalex:W4385327621` Foundational Models Defining a New Era in Vision: A Survey and Outlook (2023) https://doi.org/10.48550/arxiv.2307.13721
  - `openalex:W4406938298` Advances in diffusion models for image data augmentation: a review of methods, models, evaluation metrics and future research directions (2025) https://doi.org/10.1007/s10462-025-11116-x
- Known limitations:
  - Single RGB images may not reveal hidden material composition.
  - Exact physical-property labels may require proxy, interval, or uncertainty-aware supervision.

### LLaVA (strong)
- Type: vision_language_models
- Claimed task: object-level physical property prediction from 2D indoor scene images
- Evidence papers:
  - `openalex:W4399597788` Beyond Bare Queries: Open-Vocabulary Object Grounding with 3D Scene Graph (2024) https://doi.org/10.48550/arxiv.2406.07113
  - `openalex:W4402155831` Multimodal Large Language Models in Health Care: Applications, Challenges, and Future Outlook (2024) https://doi.org/10.2196/59505
  - `openalex:W4385327621` Foundational Models Defining a New Era in Vision: A Survey and Outlook (2023) https://doi.org/10.48550/arxiv.2307.13721
- Known limitations:
  - Semantic predictions may be unsupported by localized visual evidence.
  - Prompt-sensitive predictions require calibration or verification.

### Qwen-VL (strong)
- Type: vision_language_models
- Claimed task: object-level physical property prediction from 2D indoor scene images
- Evidence papers:
  - `openalex:W4402155831` Multimodal Large Language Models in Health Care: Applications, Challenges, and Future Outlook (2024) https://doi.org/10.2196/59505
  - `openalex:W4414857074` Embodied AI: From LLMs to World Models (2025) https://doi.org/10.36227/techrxiv.175977432.27129012/v1
  - `openalex:W4417250113` Kimi-VL Technical Report (2025) https://doi.org/10.48550/arxiv.2504.07491
- Known limitations:
  - Semantic predictions may be unsupported by localized visual evidence.
  - Prompt-sensitive predictions require calibration or verification.

### ObjectFolder (strong)
- Type: physical_property_sources
- Claimed task: object-level physical property prediction from 2D indoor scene images
- Evidence papers:
  - `openalex:W4391722892` Physical scene understanding (2024)
  - `openalex:W4327630646` Visuo-haptic object perception for robots: an overview (2023) https://doi.org/10.1007/s10514-023-10091-y
  - `openalex:W3200689778` ObjectFolder: A Dataset of Objects with Implicit Visual, Auditory, and\n Tactile Representations (2021) https://doi.org/10.48550/arxiv.2109.07991
- Known limitations:
  - Single RGB images may not reveal hidden material composition.
  - Exact physical-property labels may require proxy, interval, or uncertainty-aware supervision.

### ObjectFolder2.0 (strong)
- Type: physical_property_sources
- Claimed task: object-level physical property prediction from 2D indoor scene images
- Evidence papers:
  - `openalex:W4327630646` Visuo-haptic object perception for robots: an overview (2023) https://doi.org/10.1007/s10514-023-10091-y
  - `openalex:W4385430564` Rotating without Seeing: Towards In-hand Dexterity through Touch (2023) https://doi.org/10.15607/rss.2023.xix.036
  - `openalex:W4312347618` ObjectFolder 2.0: A Multisensory Object Dataset for Sim2Real Transfer (2022) https://doi.org/10.1109/cvpr52688.2022.01034
- Known limitations:
  - Single RGB images may not reveal hidden material composition.
  - Exact physical-property labels may require proxy, interval, or uncertainty-aware supervision.

## Top Retrieved Papers

- `openalex:W7148178853` Live Interactive Training for Video Segmentation (2026) score=12.0 url=https://openalex.org/W7148178853
- `openalex:W4399597788` Beyond Bare Queries: Open-Vocabulary Object Grounding with 3D Scene Graph (2024) score=10.833 url=https://doi.org/10.48550/arxiv.2406.07113
- `openalex:W2798280964` Gaussian material synthesis (2018) score=8.333 url=https://doi.org/10.1145/3197517.3201307
- `openalex:W4416850904` A Review of Deep Learning Approaches Based on Segment Anything Model for Medical Image Segmentation (2025) score=6.917 url=https://doi.org/10.3390/bioengineering12121312
- `openalex:W4402427278` SceneGPT: A Language Model for 3D Scene Understanding (2024) score=6.833 url=https://doi.org/10.48550/arxiv.2408.06926
- `openalex:W4402500749` Segment Anything for Videos: A Systematic Survey (2024) score=6.833 url=https://doi.org/10.48550/arxiv.2408.08315
- `openalex:W4392222076` MoodCapture: Depression Detection using In-the-Wild Smartphone Images (2024) score=6.833 url=https://doi.org/10.1145/3613904.3642680
- `openalex:W4391722892` Physical scene understanding (2024) score=6.833
- `openalex:W3046559354` An application independent review of multimodal 3D registration methods (2020) score=6.5 url=https://doi.org/10.1016/j.cag.2020.07.012
- `openalex:W3012463097` Terrain Segmentation and Roughness Estimation using RGB Data: Path Planning Application on the CENTAURO Robot (2019) score=6.417 url=https://doi.org/10.1109/humanoids43949.2019.9035009
- `openalex:W4403323960` On Efficient Variants of Segment Anything Model: A Survey (2024) score=5.833 url=https://doi.org/10.48550/arxiv.2410.04960
- `openalex:W4380551232` A Survey on Segment Anything Model (SAM): Vision Foundation Model Meets Prompt Engineering (2023) score=5.75 url=https://doi.org/10.48550/arxiv.2306.06211
- `openalex:W4362553764` On the Analyses of Medical Images Using Traditional Machine Learning Techniques and Convolutional Neural Networks (2023) score=5.75 url=https://doi.org/10.1007/s11831-023-09899-9
- `openalex:W3022851742` Investigations of Object Detection in Images/Videos Using Various Deep Learning Techniques and Embedded Platforms—A Comprehensive Review (2020) score=5.5 url=https://doi.org/10.3390/app10093280
- `openalex:W3047386722` A Survey of Computer Vision Methods for 2D Object Detection from Unmanned Aerial Vehicles (2020) score=5.5 url=https://doi.org/10.3390/jimaging6080078
- `openalex:W2963557767` Stereo magnification (2018) score=5.333 url=https://doi.org/10.1145/3197517.3201323
- `openalex:W2461758788` Local Background Enclosure for RGB-D Salient Object Detection (2016) score=5.167 url=https://doi.org/10.1109/cvpr.2016.257
- `openalex:W4411238954` Comprehensive review of recent developments in visual object detection based on deep learning (2025) score=4.917 url=https://doi.org/10.1007/s10462-025-11284-w
- `openalex:W4402155831` Multimodal Large Language Models in Health Care: Applications, Challenges, and Future Outlook (2024) score=4.833 url=https://doi.org/10.2196/59505
- `openalex:W4385327621` Foundational Models Defining a New Era in Vision: A Survey and Outlook (2023) score=4.75 url=https://doi.org/10.48550/arxiv.2307.13721
- `openalex:W4327630646` Visuo-haptic object perception for robots: an overview (2023) score=4.75 url=https://doi.org/10.1007/s10514-023-10091-y
- `openalex:W4385430564` Rotating without Seeing: Towards In-hand Dexterity through Touch (2023) score=4.75 url=https://doi.org/10.15607/rss.2023.xix.036
- `openalex:W4295689624` In Pursuit of Many: A Review of Modern Multiple Object Tracking Systems (2022) score=4.667 url=https://doi.org/10.48550/arxiv.2209.04796
- `openalex:W4312347618` ObjectFolder 2.0: A Multisensory Object Dataset for Sim2Real Transfer (2022) score=4.667 url=https://doi.org/10.1109/cvpr52688.2022.01034
- `openalex:W4226166186` ObjectFolder 2.0: A Multisensory Object Dataset for Sim2Real Transfer (2022) score=4.667 url=https://doi.org/10.48550/arxiv.2204.02389
- `openalex:W3200689778` ObjectFolder: A Dataset of Objects with Implicit Visual, Auditory, and\n Tactile Representations (2021) score=4.583 url=https://doi.org/10.48550/arxiv.2109.07991
- `openalex:W4406122761` Visual Large Language Models for Generalized and Specialized Applications (2025) score=3.917 url=https://doi.org/10.48550/arxiv.2501.02765
- `openalex:W4406938298` Advances in diffusion models for image data augmentation: a review of methods, models, evaluation metrics and future research directions (2025) score=3.917 url=https://doi.org/10.1007/s10462-025-11116-x
- `openalex:W4414857074` Embodied AI: From LLMs to World Models (2025) score=3.917 url=https://doi.org/10.36227/techrxiv.175977432.27129012/v1
- `openalex:W4391809438` A Review of Sensing Technologies for Indoor Autonomous Mobile Robots (2024) score=3.833 url=https://doi.org/10.3390/s24041222
