#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新追蹤系統工具

用於手動更新現有經典的追蹤記錄
"""

from pathlib import Path
from classic_tracker import ClassicTracker, track_new_classic
import re

def scan_existing_classics():
    """掃描現有的經典並添加到追蹤系統"""
    print("🔍 掃描現有經典...")
    
    source_dir = Path("docs/source_texts")
    tracker = ClassicTracker()
    
    added_count = 0
    
    for folder in source_dir.iterdir():
        if folder.is_dir() and '_' in folder.name:
            print(f"\n📚 處理: {folder.name}")
            
            # 從資料夾名稱提取資訊
            parts = folder.name.rsplit('_', 1)
            if len(parts) == 2:
                book_title, book_id = parts
                
                # 檢查README檔案獲取更多資訊
                readme_file = folder / "README.md"
                author = "未知作者"
                
                if readme_file.exists():
                    try:
                        with open(readme_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # 嘗試從README中提取作者資訊
                            author_match = re.search(r'\*\*作者\*\*：(.+)', content)
                            if author_match:
                                author = author_match.group(1).strip()
                    except:
                        pass
                
                # 建立書籍資訊
                book_info = {
                    'id': book_id,
                    'title': book_title,
                    'author': author,
                    'url': f"https://www.shidianguji.com/book/{book_id}"
                }
                
                # 掃描章節
                chapters = []
                source_files = folder / "原文"
                if source_files.exists():
                    for file in sorted(source_files.glob("*.txt")):
                        # 從檔案名稱提取章節資訊
                        match = re.match(r'(\d+)_(.+)\.txt', file.name)
                        if match:
                            chapter_num = int(match.group(1))
                            chapter_title = match.group(2)
                            chapters.append({
                                'number': chapter_num,
                                'title': chapter_title,
                                'url': ''
                            })
                
                if chapters:
                    # 添加到追蹤系統
                    translation_dir = Path(f"docs/translations/{folder.name}")
                    
                    track_new_classic(
                        book_info=book_info,
                        chapters=chapters,
                        source_dir=folder,
                        translation_dir=translation_dir
                    )
                    
                    added_count += 1
                    print(f"✅ 已添加: {book_title} ({len(chapters)} 章)")
                else:
                    print(f"⚠️  未找到章節: {folder.name}")
    
    print(f"\n🎉 掃描完成！添加了 {added_count} 部經典")
    
    # 生成報告
    from classic_tracker import generate_tracking_report
    generate_tracking_report()
    print("📊 追蹤報告已更新")

if __name__ == "__main__":
    scan_existing_classics()