#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道教經典翻譯專案 - 經文列表生成器

這個腳本會自動掃描 source_texts 和 translations 資料夾，
並更新 script.js 中的經文列表，確保網頁能正確載入所有經文。

學習重點：
1. 使用 docstring 說明程式功能
2. 加入適當的註解
3. 使用 pathlib 處理路徑（更現代的方式）
"""

import os
from pathlib import Path

def generate_scriptures_js():
    # 學習重點：使用 pathlib 讓路徑處理更清晰
    project_root = Path(__file__).parent
    source_texts_dir = project_root / "docs" / "source_texts"
    translations_dir = project_root / "docs" / "translations"
    script_js_path = project_root / "docs" / "js" / "script.js"

    scriptures_data = {}

    # Scan source_texts directory
    for filename in os.listdir(source_texts_dir):
        name, ext = os.path.splitext(filename)
        # Remove .txt or .text extension for display name
        # 學習重點：使用更清晰的方式處理檔案名稱
        display_name = name
        
        # Check if a translation file exists for this source text
        translation_file_path = os.path.join(translations_dir, f"{display_name}.md")
        
        scriptures_data[display_name] = {
            "original": f"source_texts/{filename}",
            "translation": f"translations/{display_name}.md" if os.path.exists(translation_file_path) else ""
        }

    # Generate the JavaScript object string explicitly
    js_content_parts = []
    items = list(scriptures_data.items())
    for i, (key, value) in enumerate(items):
        line = f"        \"{key}\": {{ original: \"{value['original']}\", translation: \"{value['translation']}\" }}"
        if i < len(items) - 1:
            line += ","
        js_content_parts.append(line)
    
    scriptures_js_content = "    const scriptures = {\n" + "\n".join(js_content_parts) + "\n    };\n"

    # Read the existing script.js content
    with open(script_js_path, 'r', encoding='utf-8') as f:
        script_js_lines = f.readlines()

    # Find the start and end markers
    start_marker = "    // SCRIPTURES_START\n"
    end_marker = "    // SCRIPTURES_END\n"

    start_index = -1
    end_index = -1

    for i, line in enumerate(script_js_lines):
        if line == start_marker:
            start_index = i
        elif line == end_marker:
            end_index = i

    if start_index != -1 and end_index != -1:
        # Replace the content between markers
        new_script_js_lines = (
            script_js_lines[:start_index + 1] +
            [scriptures_js_content] +
            script_js_lines[end_index:]
        )
        with open(script_js_path, 'w', encoding='utf-8') as f:
            f.writelines(new_script_js_lines)
        print("script.js updated successfully.")
    else:
        print("Error: SCRIPTURES_START or SCRIPTURES_END markers not found in script.js.")

if __name__ == "__main__":
    generate_scriptures_js()