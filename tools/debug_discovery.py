#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
from core.unicode_handler import safe_print
調試智能發現問題
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.translator import TranslationEngine

def debug_specific_chapters():
    """調試特定章節的發現問題"""
    safe_print("🐛 調試智能發現問題")
    safe_print("=" * 50)
    
    engine = TranslationEngine()
    
    # 測試章節
    test_chapters = [
        {
            'title': '南华真经口义卷之三十',
            'url': 'https://www.shidianguji.com/book/DZ0735/chapter/1k1ro1v9b6ur7',
            'chapter_id': '1k1ro1v9b6ur7',
            'level': 1
        },
        {
            'title': '南华真经口义卷之三十一', 
            'url': 'https://www.shidianguji.com/book/DZ0735/chapter/1k1ro1wu1qwiu',
            'chapter_id': '1k1ro1wu1qwiu',
            'level': 1
        },
        {
            'title': '南华真经口义卷之三十二',
            'url': 'https://www.shidianguji.com/book/DZ0735/chapter/1k1r7q2hmtcsp', 
            'chapter_id': '1k1r7q2hmtcsp',
            'level': 1
        }
    ]
    
    for chapter in test_chapters:
        safe_print(f"\n📋 調試: {chapter['title']}")
        safe_print(f"URL: {chapter['url']}")
        safe_print("-" * 40)
        
        try:
            # 訪問頁面
            response = engine.session.get(chapter['url'], timeout=engine.config["timeout"])
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 調用智能發現方法
                sub_chapters = engine._smart_discover_sub_chapters(soup, chapter)
                
                if sub_chapters:
                    safe_print(f"✅ 發現 {len(sub_chapters)} 個子章節:")
                    for i, sub_ch in enumerate(sub_chapters, 1):
                        safe_print(f"   {i}. {sub_ch['title']}")
                        safe_print(f"      ID: {sub_ch['chapter_id']}")
                        safe_print(f"      Level: {sub_ch['level']}")
                        safe_print(f"      URL: {sub_ch['url']}")
                        safe_print()
                else:
                    safe_print("❌ 未發現子章節")
                    
                    # 手動調試
                    safe_print("🔍 手動調試...")
                    catalog = soup.select_one('.reader-catalog-tree')
                    if catalog:
                        import re
                        items = catalog.find_all(['div', 'li'], class_=re.compile(r'tree-option|chapter-item'))
                        safe_print(f"   目錄項目數: {len(items)}")
                        
                        # 尋找當前章節
                        for i, item in enumerate(items):
                            link = item.find('a')
                            if link:
                                href = link.get('href', '')
                                title = link.get_text().strip()
                                
                                if chapter['chapter_id'] in href:
                                    safe_print(f"   找到當前章節: 索引 {i}, {title}")
                                    
                                    # 檢查後續項目
                                    for j in range(i+1, min(i+5, len(items))):
                                        next_item = items[j]
                                        next_link = next_item.find('a')
                                        if next_link:
                                            next_title = next_link.get_text().strip()
                                            next_level = engine._extract_level_from_item(next_item)
                                            safe_print(f"      後續項目 {j}: {next_title} (Level {next_level})")
                                    break
                    else:
                        safe_print("   未找到目錄結構")
            else:
                safe_print(f"❌ HTTP {response.status_code}")
                
        except Exception as e:
            safe_print(f"❌ 錯誤: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_specific_chapters()