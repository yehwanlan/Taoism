#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單的翻譯模板生成器
讀取原文檔案，生成對應的翻譯模板
"""

import os
from pathlib import Path
from datetime import datetime

def safe_print(*args, **kwargs):
    """安全打印函數"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                safe_args.append(arg.encode('utf-8', errors='replace').decode('utf-8'))
            else:
                safe_args.append(str(arg))
        print(*safe_args, **kwargs)
    except Exception as e:
        print(f"打印錯誤: {e}")

def generate_translation_template(source_file_path, translation_dir):
    """為單個原文檔案生成翻譯模板"""
    
    # 讀取原文
    try:
        with open(source_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        safe_print(f"❌ 讀取原文失敗 {source_file_path}: {e}")
        return False
    
    # 提取標題（第一行通常是標題）
    lines = content.split('\n')
    title = lines[0].replace('# ', '').strip() if lines else "未知標題"
    
    # 生成翻譯檔案名
    source_filename = Path(source_file_path).stem
    translation_filename = f"{source_filename}.md"
    translation_file_path = translation_dir / translation_filename
    
    # 生成翻譯模板內容
    template_content = f"""# {title}

## 原文

{content}

## 翻譯

[此處填入現代中文翻譯]

---

**翻譯說明：**
- 原文字數：{len(content)} 字
- 建議使用AI翻譯工具或人工翻譯
- 保持原文意思，使用現代中文表達
- 保留重要的古代術語，必要時添加註解

**重要詞彙：**
- [待補充重要詞彙解釋]

**文化背景：**
- [待補充相關文化背景]

**翻譯要點：**
- [待補充翻譯注意事項]

---
*翻譯模板生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*原文檔案：{source_filename}.txt*
"""
    
    # 保存翻譯模板
    try:
        with open(translation_file_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        safe_print(f"✅ 已生成翻譯模板: {translation_filename}")
        return True
    except Exception as e:
        safe_print(f"❌ 生成翻譯模板失敗 {translation_filename}: {e}")
        return False

def main():
    """主函數"""
    safe_print("🚀 開始生成翻譯模板...")
    safe_print("=" * 50)
    
    # 設定路徑
    source_dir = Path("docs/source_texts/文始真經（關尹子）_SBCK440/原文")
    translation_dir = Path("docs/translations/文始真經（關尹子）_SBCK440")
    
    # 檢查原文目錄是否存在
    if not source_dir.exists():
        safe_print(f"❌ 原文目錄不存在: {source_dir}")
        return
    
    # 建立翻譯目錄
    translation_dir.mkdir(parents=True, exist_ok=True)
    safe_print(f"📁 翻譯目錄: {translation_dir}")
    
    # 獲取所有原文檔案
    source_files = list(source_dir.glob("*.txt"))
    if not source_files:
        safe_print("❌ 沒有找到原文檔案")
        return
    
    safe_print(f"📚 找到 {len(source_files)} 個原文檔案")
    safe_print()
    
    # 為每個原文檔案生成翻譯模板
    success_count = 0
    for source_file in sorted(source_files):
        if generate_translation_template(source_file, translation_dir):
            success_count += 1
    
    safe_print()
    safe_print("🎉 翻譯模板生成完成！")
    safe_print(f"✅ 成功生成: {success_count}/{len(source_files)} 個模板")
    safe_print(f"📁 翻譯檔案位置: {translation_dir}")
    safe_print()
    safe_print("💡 使用說明：")
    safe_print("1. 打開翻譯目錄中的 .md 檔案")
    safe_print("2. 在「## 翻譯」部分填入現代中文翻譯")
    safe_print("3. 可以使用AI翻譯工具輔助翻譯")
    safe_print("4. 完成後保存檔案即可")

if __name__ == "__main__":
    main()