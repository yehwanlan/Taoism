#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能翻譯模板生成器

自動檢測現有經典並生成翻譯模板
"""

import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import sys

# 讓 `python tools/xxx.py` 也能找到 core 套件
sys.path.append(str(Path(__file__).parent.parent))
from core.unicode_handler import safe_print


class TemplateGenerator:
    """翻譯模板生成器"""
    
    def __init__(self):
        """初始化生成器"""
        self.source_dir = Path("docs/source_texts")
        self.translation_dir = Path("docs/translations")
        
    def scan_untranslated_classics(self) -> List[Dict]:
        """掃描尚未翻譯的經典"""
        untranslated = []
        
        if not self.source_dir.exists():
            safe_print("❌ 原文目錄不存在")
            return untranslated
            
        for book_folder in self.source_dir.iterdir():
            if not book_folder.is_dir():
                continue
                
            book_id = book_folder.name
            original_dir = book_folder / "原文"
            translation_folder = self.translation_dir / book_id
            
            if not original_dir.exists():
                continue
                
            # 檢查是否已有翻譯
            has_translation = translation_folder.exists() and any(translation_folder.glob("*.md"))
            
            if not has_translation:
                # 獲取書籍資訊
                book_info = self._extract_book_info(book_folder)
                chapters = self._scan_chapters(original_dir)
                
                untranslated.append({
                    "book_id": book_id,
                    "book_info": book_info,
                    "chapters": chapters,
                    "source_dir": book_folder,
                    "translation_dir": translation_folder
                })
                
        return untranslated
        
    def _extract_book_info(self, book_folder: Path) -> Dict:
        """從書籍資料夾提取資訊"""
        book_id = book_folder.name
        
        # 從資料夾名稱提取書名
        if '_' in book_id:
            title_part = book_id.rsplit('_', 1)[0]
            title = title_part.replace('（', '(').replace('）', ')')
        else:
            title = book_id
            
        # 嘗試從README獲取更多資訊
        readme_file = book_folder / "README.md"
        author = "未知作者"
        
        if readme_file.exists():
            try:
                with open(readme_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 提取作者資訊
                    author_match = re.search(r'\*\*作者\*\*：(.+)', content)
                    if author_match:
                        author = author_match.group(1).strip()
            except Exception:
                pass
                
        return {
            "id": book_id,
            "title": title,
            "author": author
        }
        
    def _scan_chapters(self, original_dir: Path) -> List[Dict]:
        """掃描章節檔案"""
        chapters = []
        
        for file in sorted(original_dir.glob("*.txt")):
            # 從檔案名稱提取章節資訊
            match = re.match(r'(\d+)_(.+)\.txt', file.name)
            if match:
                number = match.group(1)
                title = match.group(2)
                
                # 讀取內容獲取字數
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        char_count = len([c for c in content if '\u4e00' <= c <= '\u9fff'])
                except Exception:
                    char_count = 0
                    
                chapters.append({
                    "number": number,
                    "title": title,
                    "file_path": file,
                    "char_count": char_count
                })
                
        return chapters
        
    def generate_translation_template(self, book_data: Dict) -> bool:
        """為指定書籍生成翻譯模板"""
        book_info = book_data["book_info"]
        chapters = book_data["chapters"]
        translation_dir = book_data["translation_dir"]
        
        safe_print(f"📝 為《{book_info['title']}》生成翻譯模板...")
        
        # 建立翻譯目錄
        translation_dir.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        
        for chapter in chapters:
            try:
                # 讀取原文
                with open(chapter["file_path"], 'r', encoding='utf-8') as f:
                    original_content = f.read()
                    
                # 生成翻譯模板
                template_content = self._create_template_content(
                    book_info, chapter, original_content
                )
                
                # 儲存翻譯模板
                template_file = translation_dir / f"{chapter['number']}_{chapter['title']}.md"
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(template_content)
                    
                safe_print(f"  ✅ 第{chapter['number']}章: {chapter['title']}")
                success_count += 1
                
            except Exception as e:
                safe_print(f"  ❌ 第{chapter['number']}章失敗: {e}")
                
        safe_print(f"📊 完成 {success_count}/{len(chapters)} 個翻譯模板")
        return success_count > 0
        
    def _create_template_content(self, book_info: Dict, chapter: Dict, original_content: str) -> str:
        """創建翻譯模板內容"""
        template = f"""# {book_info['title']} - 第{chapter['number']}章

## 📖 章節資訊
- **章節**: 第{chapter['number']}章 - {chapter['title']}
- **經典**: {book_info['title']}
- **作者**: {book_info['author']}
- **字數**: {chapter['char_count']} 字

## 📜 原文

```
{original_content.strip()}
```

## 📝 現代中文翻譯

> **翻譯說明**: 請在此處提供準確、流暢的現代中文翻譯
> 
> **翻譯原則**:
> - 忠實原文，準確傳達古文含義
> - 使用現代中文表達，保持典雅風格
> - 道教專業術語保持一致性
> - 尊重傳統文化，避免不當現代化詮釋

[請在此處填入翻譯內容]

## 📚 重要詞彙註解

> **使用說明**: 請解釋文中的重要術語和概念

- **[術語1]**: [解釋]
- **[術語2]**: [解釋]

## 🏛️ 文化背景

> **背景說明**: 請提供相關的歷史文化背景

- [背景資訊1]
- [背景資訊2]

## 💡 翻譯要點

> **翻譯難點**: 請說明翻譯過程中的重點和難點

- [翻譯要點1]
- [翻譯要點2]

## 📋 翻譯狀態

- **建立時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **翻譯狀態**: 🔄 待翻譯
- **審核狀態**: ⏳ 待審核
- **品質評分**: 📊 待評估

---

> 💡 **AI翻譯提示**: 可參考 [AI翻譯指導規範](../../system/AI翻譯指導規範.md) 進行翻譯
> 
> 🔧 **品質檢查**: 完成翻譯後可使用 `python tools/ai_translation_evaluator.py` 進行品質評估
"""
        return template
        
    def interactive_template_generation(self) -> None:
        """互動式模板生成"""
        safe_print("📝 智能翻譯模板生成器")
        safe_print("=" * 40)
        
        # 掃描尚未翻譯的經典
        untranslated = self.scan_untranslated_classics()
        
        if not untranslated:
            safe_print("✅ 所有經典都已有翻譯模板")
            return
            
        safe_print(f"🔍 發現 {len(untranslated)} 部尚未建立翻譯模板的經典:\n")
        
        # 顯示列表
        for i, book in enumerate(untranslated, 1):
            book_info = book["book_info"]
            chapter_count = len(book["chapters"])
            total_chars = sum(ch["char_count"] for ch in book["chapters"])
            
            safe_print(f"{i}. 📚 {book_info['title']}")
            safe_print(f"   👤 作者: {book_info['author']}")
            safe_print(f"   📖 章節: {chapter_count} 章")
            safe_print(f"   📝 字數: {total_chars:,} 字")
            safe_print()
            
        # 詢問用戶選擇
        while True:
            try:
                choice = input("請選擇要生成模板的經典編號 (輸入 'all' 生成全部，'q' 退出): ").strip()
                
                if choice.lower() == 'q':
                    safe_print("👋 已退出模板生成")
                    break
                elif choice.lower() == 'all':
                    # 生成所有模板
                    safe_print("🚀 開始生成所有翻譯模板...")
                    for book in untranslated:
                        self.generate_translation_template(book)
                    safe_print("🎉 所有翻譯模板生成完成！")
                    break
                else:
                    # 生成指定經典的模板
                    index = int(choice) - 1
                    if 0 <= index < len(untranslated):
                        book = untranslated[index]
                        self.generate_translation_template(book)
                        
                        # 詢問是否繼續
                        continue_choice = input("\n是否繼續生成其他模板？(y/N): ").strip().lower()
                        if continue_choice not in ['y', 'yes', '是']:
                            break
                    else:
                        safe_print("❌ 無效的編號")
                        
            except ValueError:
                safe_print("❌ 請輸入有效的數字")
            except KeyboardInterrupt:
                safe_print("\n👋 已退出模板生成")
                break


def main():
    """主函數"""
    generator = TemplateGenerator()
    generator.interactive_template_generation()


if __name__ == "__main__":
    main()