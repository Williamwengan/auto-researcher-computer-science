from pathlib import Path

task_path = Path("focused_workflow/tasks/task_spec.yaml")
prompt_path = Path("focused_workflow/prompts/focused_ideation_prompt.md")
output_path = Path("focused_workflow/prompts/rendered_focused_ideation_prompt.md")

task_yaml = task_path.read_text()
prompt_template = prompt_path.read_text()

rendered_prompt = prompt_template.replace("{{TASK_SPEC_YAML}}", task_yaml)

output_path.write_text(rendered_prompt)

print("Rendered prompt saved to:", output_path)
print("Prompt length:", len(rendered_prompt))