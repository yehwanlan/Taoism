#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速修復 - 為現有原文生成翻譯模板
"""

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

def generate_templates_for_all_books():
    """為所有已爬取的書籍生成翻譯模板"""
    safe_print("🚀 開始為所有書籍生成翻譯模板...")
    
    docs_dir = Path("docs/source_texts")
    if not docs_dir.exists():
        safe_print("❌ 沒有找到原文目錄")
        return
    
    total_generated = 0
    
    for book_dir in docs_dir.iterdir():
        if book_dir.is_dir():
            source_dir = book_dir / "原文"
            if source_dir.exists():
                safe_print(f"\n📖 處理: {book_dir.name}")
                
                # 建立翻譯目錄
                translation_dir = Path("docs/translations") / book_dir.name
                translation_dir.mkdir(parents=True, exist_ok=True)
                
                # 為每個原文檔案生成翻譯模板
                source_files = list(source_dir.glob("*.txt"))
                generated_count = 0
                
                for source_file in source_files:
                    translation_filename = f"{source_file.stem}.md"
                    translation_file_path = translation_dir / translation_filename
                    
                    # 如果翻譯模板已存在，跳過
                    if translation_file_path.exists():
                        safe_print(f"  ⏭️  跳過已存在: {translation_filename}")
                        continue
                    
                    # 讀取原文
                    try:
                        with open(source_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 提取標題
                        lines = content.split('\n')
                        title = lines[0].replace('# ', '').strip() if lines else "未知標題"
                        
                        # 生成翻譯模板
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
*原文檔案：{source_file.stem}.txt*
"""
                        
                        # 保存翻譯模板
                        with open(translation_file_path, 'w', encoding='utf-8') as f:
                            f.write(template_content)
                        
                        safe_print(f"  ✅ 已生成: {translation_filename}")
                        generated_count += 1
                        
                    except Exception as e:
                        safe_print(f"  ❌ 生成失敗 {source_file.name}: {e}")
                
                safe_print(f"  📊 本書生成: {generated_count} 個模板")
                total_generated += generated_count
    
    safe_print(f"\n🎉 全部完成！總共生成 {total_generated} 個翻譯模板")
    safe_print("📁 翻譯檔案位置: docs/translations/")

if __name__ == "__main__":
    generate_templates_for_all_books()