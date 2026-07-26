# Gap Map

- PatchCore/PaDiM/WinCLIP 等 IAD baseline 对 reference shift、texture/lighting variation 和 contaminated normal bank 敏感。
- VLM 生成的 defect description 可能没有绑定具体区域或 normal reference evidence。
- 异常标签稀缺，pixel-level labels 更稀缺，需要 negative controls 和 selective prediction。
- 普通 agent 报告容易成为文本生成器，缺少 tool success、evidence grounding 和 escalation metrics。
