# Gap Map

- 检测/分割模型能给出 object mask 或 category，但不能直接给出可靠物理属性。
- CLIP/VLM/material recognition 可提供材料线索，但容易把可见材质和真实材料结构混淆。
- ObjectFolder/ObjectFolder2.0 等物理属性来源和真实室内图像之间存在 domain gap。
- 缺少 calibrated interval prediction，单点数值预测容易产生虚假精确性。
