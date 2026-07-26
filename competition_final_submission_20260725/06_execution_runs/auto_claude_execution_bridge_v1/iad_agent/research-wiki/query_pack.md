# Query Pack

Problem: 为工业异常检测构建 agentic inspection workflow，使系统能协调 normal reference retrieval、defect localization、self-checking、evidence-grounded report 和 human escalation。

Idea: Evidence-Grounded Reference-Consistency IAD Agent：以 normal reference retrieval 为核心，结合 anomaly heatmap、cross-model disagreement、region-reference consistency score、report checker 和 escalation policy。

Evidence:
- v0.7 reference claim verification：papers 24，claims 21，pass rate 0.857，unsupported 0，manual 3。
- 证据状态允许保留 manual-check claims，但最终报告中不能把 manual-check 当成 fully supported。
