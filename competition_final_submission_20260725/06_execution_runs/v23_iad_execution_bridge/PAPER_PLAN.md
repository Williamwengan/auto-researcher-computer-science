# Paper Plan

## Metadata

- **Title**: Evidence-Grounded Research Agents for AI4S Idea-to-Experiment Automation
- **One-sentence contribution**: We connect evidence-grounded idea generation with execution feedback, using IAD as a real-data smoke-test case.

## Claims-Evidence Matrix

| # | Claim | Evidence | Status |
| --- | --- | --- | --- |
| C1 | Workflow can convert a final research idea into executable experiment artifacts. | V23 execution bridge outputs, run_state, experiment log. | supported for scaffold |
| C2 | IAD reference-consistency idea is ready for full benchmark implementation. | AUC=0.945238, tool_success=1.0; current scaffold only. | partial |
| C3 | Execution feedback can drive repair. | Prior V15→V16 FPR drop case; V23 records path to result-to-claim. | supported as case study |

## Section Plan

### 1. Introduction

Motivate the gap between idea generation and executable AI4S research.

### 2. Method

Describe task input, evidence retrieval, baseline cards, idea generation, judge/repair, claim verification, and execution bridge.

### 3. Execution Layer

Explain ARIS-style run_state, research_wiki experiment nodes, result-to-claim, iteration logs, and watchdog monitoring.

### 4. Experiments

Report three-task idea benchmark and IAD real-data execution smoke test.

### 5. Limitations

State clearly that current IAD result is lightweight scaffold, not full PatchCore/anomalib benchmark.

## Strongest number currently safe to mention

- IAD lightweight AUC: 0.945238
- tool_success_rate: 1.0

## Boundary

Do not claim IAD SOTA. Do not claim full autonomous science yet. Claim a prototype of idea-to-execution workflow with one real-data execution bridge.
