import os
import json
import requests
import re

def read_markdown_file(filepath: str) -> str:
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def call_ollama(model: str, prompt: str) -> str:
    url = "http://localhost:11434/api/generate"
    headers = { "Content-Type": "application/json" }
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"❌ 网络或响应失败: {e}"

def split_md_jsons(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    md_files = sorted(f for f in os.listdir(input_dir) if f.startswith("page_") and f.endswith(".md"))

    for md_file in md_files:
        input_path = os.path.join(input_dir, md_file)
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 提取 page index
        match = re.match(r"page_(\d+)\.md", md_file)
        if not match:
            print(f"⚠️ 无法识别页码：{md_file}")
            continue
        page_index = int(match.group(1))

        # 尝试逐个解析多个 JSON（假设每段是独立的 JSON 对象）
        json_blocks = re.findall(r"\{[\s\S]*?\}", content)
        for i, block in enumerate(json_blocks):
            try:
                obj = json.loads(block)
                obj["page_index"] = page_index

                output_filename = f"page_{page_index:03d}_item_{i+1:02d}.json"
                output_path = os.path.join(output_dir, output_filename)

                with open(output_path, "w", encoding="utf-8") as f_out:
                    json.dump(obj, f_out, ensure_ascii=False, indent=2)

                print(f"✅ 保存：{output_filename}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败：{md_file} 第{i+1}个对象：{e}")

def analyze_markdown(
    input_md_dir, prompt_file, model_name
):
    analysis_dir = os.path.join(os.path.dirname(input_md_dir), "analysis_results_md")
    os.makedirs(analysis_dir, exist_ok=True)
    user_prompt = read_markdown_file(prompt_file)

    for md_file in sorted(os.listdir(input_md_dir)):
        if not md_file.endswith(".md"):
            continue
        page_idx = int(md_file.replace("page_", "").replace(".md", ""))
        chunk_text = read_markdown_file(os.path.join(input_md_dir, md_file))
        full_prompt = f"{user_prompt.strip()}\n\n---\n\n{chunk_text.strip()}"

        print(f"📄 正在分析第 {page_idx} 页: {md_file}", full_prompt)
        qwen_output = call_ollama(model_name, full_prompt)

        # 保存分析结果到 analysis_results 文件夹
        analysis_output_path = os.path.join(analysis_dir, md_file)
        with open(analysis_output_path, 'w', encoding='utf-8') as f:
            f.write(qwen_output)
        print(f"📝 分析结果保存至：{analysis_output_path}")

    analysis_dir_json = os.path.join(os.path.dirname(input_md_dir), "analysis_results_json")
    split_md_jsons(analysis_dir, analysis_dir_json)
    return analysis_dir_json