# Si et al. 2025 Style LLM Reviewer Prompt

You are acting as a careful research-idea reviewer.

Your task is to review the research ideas below using the adapted Si et al. 2025 rubric.

## Rubric

```yaml
{{RUBRIC_YAML}}
```

## Review Rules

1. Review the idea itself, not the writing style.
2. Use the same standard for every idea.
3. Scores must be integers from 1 to 10.
4. Give concise but specific rationales.
5. Do not reward an idea only because it is detailed; reward clear novelty, feasibility, expected effectiveness, and excitement.
6. Penalize ideas that lack concrete baselines, metrics, implementation steps, or failure conditions.
7. Be conservative: a score of 8 or above should mean the idea is genuinely strong on that dimension.

## Required Output

Write exactly one JSON file named:

```text
{{OUTPUT_FILE}}
```

The file must contain a JSON list. Each item must have this schema:

```json
{
  "idea_file": "",
  "title": "",
  "novelty_score": 1,
  "novelty_rationale": "",
  "feasibility_score": 1,
  "feasibility_rationale": "",
  "expected_effectiveness_score": 1,
  "expected_effectiveness_rationale": "",
  "excitement_score": 1,
  "excitement_rationale": "",
  "overall_score": 1,
  "overall_rationale": "",
  "reviewer": "llm_reviewer",
  "review_protocol": "Si et al. 2025 adapted rubric"
}
```

Do not write markdown.
Do not include comments.
Do not include extra text outside the JSON file.

## Ideas To Review

{{IDEA_BLOCKS}}
