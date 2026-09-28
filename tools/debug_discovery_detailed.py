#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
詳細調試智能發現問題
"""

import sys
import re
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.translator import TranslationEngine
from bs4 import BeautifulSoup
from core.unicode_handler import safe_print

def debug_smart_discovery_detailed():
    """詳細調試智能發現方法"""
    safe_print("🐛 詳細調試智能發現方法")
    safe_print("=" * 50)
    
    engine = TranslationEngine()
    
    # 測試卷之三十
    chapter = {
        'title': '南华真经口义卷之三十',
        'url': 'https://www.shidianguji.com/book/DZ0735/chapter/1k1ro1v9b6ur7',
        'chapter_id': '1k1ro1v9b6ur7',
        'level': 1
    }
    
    safe_print(f"📋 測試: {chapter['title']}")
    safe_print(f"URL: {chapter['url']}")
    safe_print("-" * 40)
    
    try:
        response = engine.session.get(chapter['url'], timeout=engine.config["timeout"])
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 手動實現智能發現邏輯，添加調試信息
            sub_chapters = []
            
            # 尋找目錄結構
            catalog = soup.select_one('.reader-catalog-tree')
            if catalog:
                safe_print("✅ 找到目錄結構")
                
                items = catalog.find_all(['div', 'li'], class_=re.compile(r'tree-option|chapter-item'))
                parent_level = chapter.get('level', 1)
                parent_chapter_id = chapter['chapter_id']
                
                safe_print(f"📊 目錄項目數: {len(items)}")
                safe_print(f"🎯 尋找章節ID: {parent_chapter_id}")
                safe_print(f"📏 父章節層級: {parent_level}")
                
                # 尋找當前章節在目錄中的位置
                current_index = -1
                for i, item in enumerate(items):
                    link = item.find('a')
                    if link:
                        href = link.get('href', '')
                        title = link.get_text().strip()
                        
                        # 檢查是否是當前章節
                        if (parent_chapter_id in href or 
                            chapter['title'] in title or
                            title in chapter['title']):
                            current_index = i
                            safe_print(f"🎯 找到當前章節: 索引 {i}, {title}")
                            break
                
                # 如果找到當前章節，檢查後續項目
                if current_index >= 0:
                    safe_print(f"🔍 檢查後續項目 (從索引 {current_index + 1} 開始)...")
                    
                    for i in range(current_index + 1, len(items)):
                        item = items[i]
                        link = item.find('a')
                        
                        if not link:
                            safe_print(f"   項目 {i}: 無鏈接，跳過")
                            continue
                        
                        href = link.get('href', '')
                        title = link.get_text().strip()
                        item_level = engine._extract_level_from_item(item)
                        
                        safe_print(f"   項目 {i}: {title} (Level {item_level})")
                        safe_print(f"      href: {href}")
                        
                        # 如果層級比父章節高，說明是子章節
                        if item_level > parent_level:
                            safe_print(f"      ✅ 層級檢查通過: {item_level} > {parent_level}")
                            
                            chapter_id = engine._extract_chapter_id(href)
                            safe_print(f"      章節ID: {chapter_id}")
                            
                            if chapter_id and title and len(title) > 2:
                                safe_print(f"      ✅ 所有檢查通過，添加子章節")
                                
                                from urllib.parse import urljoin
                                full_url = urljoin(engine.config["base_url"], href)
                                
                                sub_chapter = {
                                    'title': title,
                                    'url': full_url,
                                    'chapter_id': chapter_id,
                                    'level': item_level,
                                    'parent_id': chapter['chapter_id'],
                                    'parent_title': chapter['title'],
                                    'is_volume': engine._is_volume_title(title, item_level),
                                    'is_chapter': engine._is_chapter_title(title, item_level),
                                    'discovered': True,
                                    'discovery_method': 'smart_structure_analysis'
                                }
                                
                                sub_chapters.append(sub_chapter)
                                safe_print(f"      📄 已添加: {title}")
                            else:
                                safe_print(f"      ❌ 檢查失敗:")
                                safe_print(f"         chapter_id: {chapter_id}")
                                safe_print(f"         title: '{title}' (長度: {len(title)})")
                        
                        # 如果層級等於或小於父章節，停止搜索
                        elif item_level <= parent_level:
                            safe_print(f"      🛑 到達同級章節 (Level {item_level})，停止搜索")
                            break
                        else:
                            safe_print(f"      ⚠️  層級檢查未通過: {item_level} <= {parent_level}")
                
                safe_print(f"\n📊 最終結果: 發現 {len(sub_chapters)} 個子章節")
                for sub_ch in sub_chapters:
                    safe_print(f"   - {sub_ch['title']} (ID: {sub_ch['chapter_id']})")
            else:
                safe_print("❌ 未找到目錄結構")
                
    except Exception as e:
        safe_print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_smart_discovery_detailed()