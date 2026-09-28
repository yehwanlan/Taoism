#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手動添加隱藏章節工具

用於添加系統無法自動發現的隱藏章節，如DZ0735中的子章節
"""

import sys
import json
from pathlib import Path

# 添加父目錄到路徑
sys.path.append(str(Path(__file__).parent.parent))

from core.translator import TranslationEngine
from core.unicode_handler import safe_print


class HiddenChapterAdder:
    """隱藏章節添加器"""
    
    def __init__(self):
        self.engine = TranslationEngine()
        
    def add_hidden_chapters_to_book(self, book_id: str, hidden_chapters: list):
        """為指定書籍添加隱藏章節"""
        safe_print(f"🔧 為書籍 {book_id} 添加隱藏章節")
        safe_print("=" * 50)
        
        # 設置書籍信息
        book_info = {'id': book_id, 'title': f'書籍_{book_id}', 'author': '未知'}
        self.engine.current_book = book_info
        
        success_count = 0
        
        for chapter_info in hidden_chapters:
            chapter_id = chapter_info['chapter_id']
            expected_title = chapter_info['title']
            level = chapter_info.get('level', 2)
            
            safe_print(f"\n📖 處理隱藏章節: {expected_title}")
            safe_print(f"   ID: {chapter_id}")
            safe_print(f"   層級: Level {level}")
            
            try:
                # 構建URL
                test_url = f"{self.engine.config['base_url']}/book/{book_id}/chapter/{chapter_id}"
                
                # 嘗試爬取內容
                response = self.engine.session.get(test_url, timeout=10)
                if response.status_code == 200:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 提取實際標題
                    title_elem = soup.find('h1', class_='Goq6DYSE')
                    actual_title = title_elem.get_text().strip() if title_elem else expected_title
                    
                    # 提取內容
                    content_data = self.engine._extract_content_from_html(soup, actual_title)
                    
                    if content_data and content_data.get('content'):
                        # 從內容中提取實際的章節名
                        actual_chapter_title = self.engine._extract_actual_title_from_content(
                            content_data['content'], expected_title
                        )
                        
                        # 更新內容數據
                        content_data['title'] = actual_chapter_title
                        content_data['original_title'] = actual_title
                        content_data['level'] = level
                        content_data['is_volume'] = level == 1 and '卷' in actual_chapter_title
                        content_data['is_chapter'] = level == 2 or any(keyword in actual_chapter_title 
                                                                      for keyword in ['品', '篇', '章'])
                        
                        # 保存原文
                        chapter_number = success_count + 1
                        self.engine._save_source_text(content_data, chapter_number)
                        
                        # 生成翻譯模板
                        self.engine.generate_translation_template(content_data, chapter_number)
                        
                        success_count += 1
                        safe_print(f"   ✅ 成功添加: {actual_chapter_title}")
                        
                    else:
                        safe_print(f"   ❌ 無法提取內容")
                else:
                    safe_print(f"   ❌ HTTP {response.status_code}")
                    
            except Exception as e:
                safe_print(f"   ❌ 錯誤: {e}")
        
        safe_print(f"\n🎉 完成！成功添加 {success_count}/{len(hidden_chapters)} 個隱藏章節")
        return success_count > 0


def add_dz0735_hidden_chapters():
    """添加DZ0735的隱藏章節"""
    
    # DZ0735的隱藏章節列表
    hidden_chapters = [
        {
            'chapter_id': '1kd4w8pj6tu7n',
            'title': '外篇刻意',
            'level': 2,
            'parent': '南华真经口义卷之十七'
        },
        {
            'chapter_id': '1kd4w8pj6thkj', 
            'title': '外篇缮性',
            'level': 2,
            'parent': '南华真经口义卷之十七'
        }
    ]
    
    adder = HiddenChapterAdder()
    
    # 設置輸出目錄
    book_folder = Path("../docs/source_texts/南华真经口义_DZ0735")
    translation_folder = Path("../docs/translations/南华真经口义_DZ0735")
    
    # 確保目錄存在
    (book_folder / "原文").mkdir(parents=True, exist_ok=True)
    translation_folder.mkdir(parents=True, exist_ok=True)
    
    # 設置引擎的輸出目錄
    adder.engine.source_dir = book_folder / "原文"
    adder.engine.translation_dir = translation_folder
    
    # 添加隱藏章節
    success = adder.add_hidden_chapters_to_book("DZ0735", hidden_chapters)
    
    if success:
        safe_print("\n📋 建議後續操作:")
        safe_print("1. 檢查新添加的原文文件")
        safe_print("2. 檢查生成的翻譯模板")
        safe_print("3. 更新README.md文件")
        safe_print("4. 考慮重新運行完整的翻譯流程")


def create_hidden_chapters_config():
    """創建隱藏章節配置文件"""
    config = {
        "DZ0735": {
            "book_title": "南华真经口义",
            "hidden_chapters": [
                {
                    "chapter_id": "1kd4w8pj6tu7n",
                    "title": "外篇刻意",
                    "level": 2,
                    "parent": "南华真经口义卷之十七",
                    "description": "卷之十七的子章節"
                },
                {
                    "chapter_id": "1kd4w8pj6thkj",
                    "title": "外篇缮性", 
                    "level": 2,
                    "parent": "南华真经口义卷之十七",
                    "description": "卷之十七的子章節"
                }
            ]
        }
    }
    
    config_file = Path("../config/hidden_chapters.json")
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    safe_print(f"📝 隱藏章節配置已保存到: {config_file}")


if __name__ == "__main__":
    safe_print("🔧 隱藏章節添加工具")
    safe_print("=" * 30)
    
    # 創建配置文件
    create_hidden_chapters_config()
    
    # 添加DZ0735的隱藏章節
    add_dz0735_hidden_chapters()