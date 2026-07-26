<!-- ARIS:BEGIN -->
## ARIS Skill Scope

This workspace is generated for Auto-claude/ARIS-style experiment execution.
Use project-local ARIS skills if installed. The intended execution skill is:

- `/experiment-bridge refine-logs/EXPERIMENT_PLAN.md`
- then `/run-experiment` or `/experiment-queue` after human authorization.

<!-- ARIS:END -->

# Project Instructions

## Goal

Run experiments for the focused AI4S research idea:

Mechanism-consistent physical property prediction plan：保留 Idea 1 的 calibrated interval mapper，将 Idea 2 修复为 localized material evidence verifier，将 Idea 3 修复为 proposal uncertainty propagation。

## Safety / Authorization

- Ask the user before running shell commands that download data, install packages, call APIs, or launch GPU jobs.
- If a dataset is missing, ask for a path or upload.
- Keep all outputs under this workspace unless the user authorizes otherwise.
- Save metrics as JSON/CSV and logs as plain text.

## Environment

- gpu: local
- code_sync: local
- wandb: false

## Required Reading Order

1. `RESEARCH_BRIEF.md`
2. `refine-logs/FINAL_PROPOSAL.md`
3. `refine-logs/EXPERIMENT_PLAN.md`
4. `refine-logs/EXPERIMENT_TRACKER.md`

## Non-claims

Do not claim SOTA or full benchmark completion unless the corresponding experiments are actually executed.
