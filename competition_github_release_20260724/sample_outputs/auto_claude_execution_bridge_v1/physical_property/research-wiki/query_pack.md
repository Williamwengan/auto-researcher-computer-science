# Query Pack

Problem: 从单张 2D 室内场景图像中，为每个可见物体预测 density、Young's modulus、Poisson ratio、hardness、friction coefficient 等物理属性，并输出不确定性和失败警告。

Idea: Mechanism-consistent physical property prediction plan：保留 Idea 1 的 calibrated interval mapper，将 Idea 2 修复为 localized material evidence verifier，将 Idea 3 修复为 proposal uncertainty propagation。

Evidence:
- v0.7 evidence-card repair 后：papers 51，claims 15，pass rate 1.0。
- 证据链覆盖 ObjectFolder/ObjectFolder2.0、CLIP、SAM/SAM2、GroundingDINO、VLM material claim evidence 和 proposal uncertainty evidence。
