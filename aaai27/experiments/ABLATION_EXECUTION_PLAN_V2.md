# AAAI-27 Ablation Execution Plan v2

This operational plan corrects the non-executable 75-row planning manifest without changing the frozen hypotheses or inspecting ablation outcomes.

| Frozen ablation | Executable source | New generation calls |
| --- | --- | ---: |
| full | reuse main `focused_full` outputs | 0 |
| no_repair | reuse main `focused_no_repair` outputs | 0 |
| no_consistency_check | reuse compute-matched `focused_generic_refine` outputs | 0 |
| no_claim_verification | offline verifier bypass over the same ideas | 0 |
| no_evidence | `ablation_execution_manifest_v2.jsonl` | 30 expected |

The no-evidence condition keeps the focused schema and consistency-aware repair but removes evidence cards, paper abstracts, paper IDs, evidence criticism, and paper-specific claim verification. It contains 3 tasks × 5 independent replicates = 15 paired pipelines. Each pipeline uses one initial generation call and one repair call.

Smoke-test gate: run only `physical_focused_full_no_evidence_s11`, confirm two successful calls, empty `evidence_paper_ids`, zero evidence-record markers in the saved prompts, and complete usage metadata. Only then run the remaining 14 pipelines.

The original `ablation_manifest.jsonl` remains as the frozen conceptual grid and must not be passed directly to the main generation runner.
