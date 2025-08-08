import json
import os

def extract_text_from_page(page):
    """提取一页中的所有文本内容"""
    texts = []
    for block in page.get("para_blocks", []):
        for line in block.get("lines", []):
            span_texts = []
            for span in line.get("spans", []):
                if span.get("type") == "text":
                    span_texts.append(span.get("content", "").strip())
                elif span.get("type") == "inline_equation":
                    equation = '$' + span.get("content", "").strip() + '$'
                    span_texts.append(equation)
            texts.append("".join(span_texts))
    return "\n\n".join(texts)  # 段落间保留空行

def save_page_to_markdown(page_idx, text, output_dir):
    filename = os.path.join(output_dir, f"page_{page_idx:03d}.md")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

def split_json_to_markdown(json_path, output_dir):
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 加载 JSON 数据
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 遍历每一页
    for page in data.get("pdf_info", []):
        page_idx = page.get("page_idx", 0)
        page_text = extract_text_from_page(page)
        save_page_to_markdown(page_idx, page_text, output_dir)
        print(f"✅ 已保存：page_{page_idx:03d}.md")