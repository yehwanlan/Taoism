#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
from core.unicode_handler import safe_print
調試href匹配問題
"""

import sys
import re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.translator import TranslationEngine
from bs4 import BeautifulSoup

def debug_href_matching():
    """調試href匹配問題"""
    safe_print("🐛 調試href匹配問題")
    safe_print("=" * 50)
    
    engine = TranslationEngine()
    
    # 測試卷之三十
    chapter = {
        'title': '南华真经口义卷之三十',
        'url': 'https://www.shidianguji.com/book/DZ0735/chapter/1k1ro1v9b6ur7',
        'chapter_id': '1k1ro1v9b6ur7',
        'level': 1
    }
    
    safe_print(f"📋 尋找章節ID: {chapter['chapter_id']}")
    
    try:
        response = engine.session.get(chapter['url'], timeout=engine.config["timeout"])
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            catalog = soup.select_one('.reader-catalog-tree')
            if catalog:
                items = catalog.find_all(['div', 'li'], class_=re.compile(r'tree-option|chapter-item'))
                
                safe_print(f"📊 檢查所有 {len(items)} 個項目的href:")
                
                for i, item in enumerate(items):
                    link = item.find('a')
                    if link:
                        href = link.get('href', '')
                        title = link.get_text().strip()
                        
                        safe_print(f"   {i:2d}. {title}")
                        safe_print(f"       href: {href}")
                        
                        if chapter['chapter_id'] in href:
                            safe_print(f"       ✅ 匹配! 這是目標章節")
                        
                        if '三十' in title:
                            safe_print(f"       🎯 包含'三十'的章節")
                            
    except Exception as e:
        safe_print(f"❌ 錯誤: {e}")

if __name__ == "__main__":
    debug_href_matching()