import os
import json

def generate_scriptures_js():
    project_root = os.path.dirname(os.path.abspath(__file__))
    source_texts_dir = os.path.join(project_root, "source_texts")
    translations_dir = os.path.join(project_root, "translations")
    script_js_path = os.path.join(project_root, "docs", "js", "script.js")

    scriptures_data = {}

    # Scan source_texts directory
    for filename in os.listdir(source_texts_dir):
        name, ext = os.path.splitext(filename)
        # Remove .txt or .text extension for display name
        display_name = name.replace(".text", "").replace(".txt", "").replace(".html", "")
        
        # Check if a translation file exists for this source text
        translation_file_path = os.path.join(translations_dir, f"{display_name}.md")
        
        scriptures_data[display_name] = {
            "original": f"source_texts/{filename}",
            "translation": f"translations/{display_name}.md" if os.path.exists(translation_file_path) else ""
        }

    # Generate the JavaScript object string
    scriptures_lines = []
    for key, value in scriptures_data.items():
        scriptures_lines.append(f"        \"{key}\": {{ original: \"{value['original']}\", translation: \"{value['translation']}\" }}")
    
    # Use an f-string for the entire block, escaping curly braces for literal output
    scriptures_js_content = f"""
    const scriptures = {{
{ "\n".join(scriptures_lines) }
    }};
"""

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