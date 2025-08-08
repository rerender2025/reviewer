import os
import json

def load_layout(layout_path):
    with open(layout_path, "r", encoding="utf-8") as f:
        return json.load(f)

def find_matching_bboxes(page_json, ref_texts):
    bboxes = []
    for block in page_json.get("para_blocks", []):
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                content = span.get("content", "")
                for ref in ref_texts:
                    if ref.strip() and ref in content:
                        bboxes.append(span.get("bbox"))
    return bboxes

def enrich_json_with_bboxes(json_dir, layout_json_path):
    layout = load_layout(layout_json_path)
    os.makedirs(json_dir, exist_ok=True)

    pdf_pages = layout.get("pdf_info", [])

    for filename in sorted(os.listdir(json_dir)):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(json_dir, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"❌ 跳过非法JSON: {filename}")
                continue

        page_idx = data.get("page_index")
        ref_texts = data.get("ref", [])

        if not isinstance(ref_texts, list) or page_idx is None:
            print(f"⚠️ 缺少必要字段：{filename}")
            continue

        # ✅ 通过字段匹配找到对应 page
        page_json = next(
            (page for page in pdf_pages if str(page.get("page_idx")) == str(page_idx)),
            None
        )

        if not page_json:
            print(f"⚠️ 未找到匹配页：{filename} (page_idx={page_idx})")
            continue

        matched_bboxes = find_matching_bboxes(page_json, ref_texts)
        data["bbox"] = matched_bboxes

        # 保存更新后的 JSON
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ 已更新 bbox：{filename}")
