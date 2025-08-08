from utils.layout_to_md import split_json_to_markdown
from utils.analyze import analyze_markdown
from utils.overlay import enrich_json_with_bboxes

layout_json_path = './assets/layout.json'
md_pages_dir = './out/output_md_pages'
split_json_to_markdown(layout_json_path, md_pages_dir)

prompt_path = './assets/prompt.md'
model_name = "qwen3:30b-a3b-instruct-2507-q4_K_M"
analysis_dir_json = analyze_markdown(md_pages_dir, prompt_path, model_name)

json_dir = "output_json"
enrich_json_with_bboxes(analysis_dir_json, layout_json_path)