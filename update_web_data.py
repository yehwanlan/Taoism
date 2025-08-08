#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新網頁資料腳本

自動掃描經典檔案並更新網頁的JavaScript資料結構
"""

import json
import re
from pathlib import Path


def scan_books_data():
    """掃描書籍資料"""
    source_dir = Path("docs/source_texts")
    books_data = {}
    
    if not source_dir.exists():
        print("❌ source_texts 目錄不存在")
        return books_data
    
    for book_folder in source_dir.iterdir():
        if not book_folder.is_dir():
            continue
            
        book_id = book_folder.name
        
        # 從資料夾名稱提取書名
        if '_' in book_id:
            title_part = book_id.rsplit('_', 1)[0]
            # 清理書名
            title = title_part.replace('（', '(').replace('）', ')')
        else:
            title = book_id
            
        # 掃描章節
        chapters = []
        original_dir = book_folder / "原文"
        
        if original_dir.exists():
            for file in sorted(original_dir.glob("*.txt")):
                # 從檔案名稱提取章節資訊
                match = re.match(r'(\d+)_(.+)\.txt', file.name)
                if match:
                    number = match.group(1)
                    chapter_title = match.group(2)
                    chapters.append({
                        "number": number,
                        "title": chapter_title
                    })
        
        if chapters:
            books_data[book_id] = {
                "title": title,
                "chapters": chapters
            }
            print(f"✅ 掃描到: {title} ({len(chapters)} 章)")
    
    return books_data


def update_javascript_file(books_data):
    """更新JavaScript檔案中的書籍資料"""
    js_file = Path("docs/js/script.js")
    
    if not js_file.exists():
        print("❌ JavaScript檔案不存在")
        return False
    
    try:
        # 讀取現有檔案
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 生成新的資料結構
        js_data = "    const booksData = {\n"
        
        for book_id, book_info in books_data.items():
            js_data += f'        "{book_id}": {{\n'
            js_data += f'            title: "{book_info["title"]}",\n'
            js_data += f'            chapters: [\n'
            
            for chapter in book_info["chapters"]:
                js_data += f'                {{ number: "{chapter["number"]}", title: "{chapter["title"]}" }},\n'
            
            js_data += f'            ]\n'
            js_data += f'        }},\n'
        
        js_data += "    };"
        
        # 使用正則表達式替換資料結構
        pattern = r'const booksData = \{.*?\};'
        new_content = re.sub(pattern, js_data, content, flags=re.DOTALL)
        
        # 寫回檔案
        with open(js_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ 已更新 JavaScript 檔案: {js_file}")
        return True
        
    except Exception as e:
        print(f"❌ 更新 JavaScript 檔案失敗: {e}")
        return False


def generate_web_report():
    """生成網頁資料報告"""
    books_data = scan_books_data()
    
    if not books_data:
        print("❌ 沒有找到任何書籍資料")
        return
    
    total_books = len(books_data)
    total_chapters = sum(len(book["chapters"]) for book in books_data.values())
    
    report = f"""# 📊 網頁資料報告

**生成時間**: {Path(__file__).stat().st_mtime}

## 📈 統計資訊

- **書籍總數**: {total_books} 部
- **章節總數**: {total_chapters} 章

## 📚 書籍列表

"""
    
    for book_id, book_info in books_data.items():
        report += f"""### {book_info['title']}

- **資料夾ID**: {book_id}
- **章節數**: {len(book_info['chapters'])} 章
- **章節列表**:
"""
        for chapter in book_info['chapters']:
            report += f"  - 第{chapter['number']}章: {chapter['title']}\n"
        report += "\n"
    
    # 儲存報告
    report_file = Path("docs/web_data_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📋 報告已儲存: {report_file}")
    
    return books_data


def main():
    """主函數"""
    print("🔄 更新網頁資料...")
    print("=" * 40)
    
    # 掃描書籍資料
    books_data = generate_web_report()
    
    if not books_data:
        return
    
    # 更新JavaScript檔案
    if update_javascript_file(books_data):
        print("\n🎉 網頁資料更新完成！")
        print(f"📊 總計: {len(books_data)} 部書籍")
        print("💡 請重新載入網頁查看更新")
    else:
        print("\n❌ 更新失敗")


if __name__ == "__main__":
    main()