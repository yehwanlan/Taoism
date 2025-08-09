#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
from core.unicode_handler import safe_print
數字序列章節發現器

針對使用數字序列ID的書籍，提供專門的子章節發現策略
"""

import sys
import re
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Dict, List, Optional

sys.path.append(str(Path(__file__).parent.parent))

class NumericSequenceDiscovery:
    """數字序列章節發現器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.base_url = "https://www.shidianguji.com"
    
    def discover_numeric_sub_chapters(self, book_url: str, parent_chapter: Dict) -> List[Dict]:
        """針對數字序列ID發現子章節"""
        safe_print(f"🔢 數字序列發現: {parent_chapter['title']}")
        
        sub_chapters = []
        parent_id = parent_chapter.get('chapter_id', '')
        
        if not parent_id.isdigit():
            safe_print(f"   ⚠️  非數字ID，跳過數字序列發現")
            return []
        
        parent_num = int(parent_id)
        book_id = self._extract_book_id(book_url)
        
        # 策略1: 檢查小數點模式 (如 1.1, 1.2, 1.3)
        decimal_sub_chapters = self._check_decimal_pattern(book_id, parent_num)
        if decimal_sub_chapters:
            sub_chapters.extend(decimal_sub_chapters)
            safe_print(f"   ✅ 小數點模式發現 {len(decimal_sub_chapters)} 個子章節")
        
        # 策略2: 檢查字母後綴模式 (如 1a, 1b, 1c)
        if not sub_chapters:
            letter_sub_chapters = self._check_letter_suffix_pattern(book_id, parent_num)
            if letter_sub_chapters:
                sub_chapters.extend(letter_sub_chapters)
                safe_print(f"   ✅ 字母後綴模式發現 {len(letter_sub_chapters)} 個子章節")
        
        # 策略3: 檢查範圍內的連續數字 (如 101, 102, 103 屬於 1)
        if not sub_chapters:
            range_sub_chapters = self._check_range_pattern(book_id, parent_num)
            if range_sub_chapters:
                sub_chapters.extend(range_sub_chapters)
                safe_print(f"   ✅ 範圍模式發現 {len(range_sub_chapters)} 個子章節")
        
        # 策略4: 結合結構分析作為備用
        if not sub_chapters:
            safe_print(f"   🔄 數字策略無效，使用結構分析備用方案")
            # 這裡可以調用原有的結構分析方法
        
        return sub_chapters
    
    def _extract_book_id(self, book_url: str) -> str:
        """從書籍URL中提取書籍ID"""
        match = re.search(r'/book/([^/?]+)', book_url)
        return match.group(1) if match else ''
    
    def _check_decimal_pattern(self, book_id: str, parent_num: int) -> List[Dict]:
        """檢查小數點模式的子章節"""
        sub_chapters = []
        
        # 嘗試 parent_num.1, parent_num.2, ... parent_num.10
        for i in range(1, 11):
            test_id = f"{parent_num}.{i}"
            chapter_url = f"{self.base_url}/book/{book_id}/chapter/{test_id}"
            
            if self._test_chapter_exists(chapter_url):
                title = self._get_chapter_title(chapter_url)
                if title:
                    sub_chapters.append({
                        'title': title,
                        'url': chapter_url,
                        'chapter_id': test_id,
                        'level': 2,
                        'parent_id': str(parent_num),
                        'discovered': True,
                        'discovery_method': 'numeric_decimal_pattern'
                    })
                    safe_print(f"      📄 找到: {test_id} - {title}")
            else:
                # 如果連續3個不存在，停止搜索
                if i > 3 and len(sub_chapters) == 0:
                    break
                elif i > len(sub_chapters) + 3:
                    break
        
        return sub_chapters
    
    def _check_letter_suffix_pattern(self, book_id: str, parent_num: int) -> List[Dict]:
        """檢查字母後綴模式的子章節"""
        sub_chapters = []
        
        # 嘗試 parent_numa, parent_numb, ... parent_numz
        for i in range(26):  # a-z
            letter = chr(ord('a') + i)
            test_id = f"{parent_num}{letter}"
            chapter_url = f"{self.base_url}/book/{book_id}/chapter/{test_id}"
            
            if self._test_chapter_exists(chapter_url):
                title = self._get_chapter_title(chapter_url)
                if title:
                    sub_chapters.append({
                        'title': title,
                        'url': chapter_url,
                        'chapter_id': test_id,
                        'level': 2,
                        'parent_id': str(parent_num),
                        'discovered': True,
                        'discovery_method': 'numeric_letter_suffix_pattern'
                    })
                    safe_print(f"      📄 找到: {test_id} - {title}")
            else:
                # 如果連續5個不存在，停止搜索
                if i > 5 and len(sub_chapters) == 0:
                    break
                elif i > len(sub_chapters) + 5:
                    break
        
        return sub_chapters
    
    def _check_range_pattern(self, book_id: str, parent_num: int) -> List[Dict]:
        """檢查範圍模式的子章節"""
        sub_chapters = []
        
        # 嘗試範圍模式，如章節1可能包含101-199
        start_range = parent_num * 100 + 1
        end_range = start_range + 20  # 限制搜索範圍
        
        for test_num in range(start_range, end_range):
            test_id = str(test_num)
            chapter_url = f"{self.base_url}/book/{book_id}/chapter/{test_id}"
            
            if self._test_chapter_exists(chapter_url):
                title = self._get_chapter_title(chapter_url)
                if title:
                    sub_chapters.append({
                        'title': title,
                        'url': chapter_url,
                        'chapter_id': test_id,
                        'level': 2,
                        'parent_id': str(parent_num),
                        'discovered': True,
                        'discovery_method': 'numeric_range_pattern'
                    })
                    safe_print(f"      📄 找到: {test_id} - {title}")
            
            # 限制連續失敗次數
            if test_num - start_range > 5 and len(sub_chapters) == 0:
                break
        
        return sub_chapters
    
    def _test_chapter_exists(self, chapter_url: str) -> bool:
        """測試章節URL是否存在"""
        try:
            response = self.session.head(chapter_url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _get_chapter_title(self, chapter_url: str) -> Optional[str]:
        """獲取章節標題"""
        try:
            response = self.session.get(chapter_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 嘗試多種標題選擇器
                title_selectors = [
                    'h1.chapter-title',
                    '.chapter-title',
                    'h1',
                    '.title',
                    '.chapter-name'
                ]
                
                for selector in title_selectors:
                    title_elem = soup.select_one(selector)
                    if title_elem:
                        return title_elem.get_text().strip()
                
                # 備用方案：從頁面標題提取
                title_tag = soup.find('title')
                if title_tag:
                    title = title_tag.get_text().strip()
                    # 清理標題
                    title = re.sub(r'\s*-\s*.*$', '', title)  # 移除網站名稱
                    return title
            
            return None
        except:
            return None

def test_numeric_discovery():
    """測試數字序列發現器"""
    safe_print("🧪 測試數字序列發現器")
    safe_print("=" * 50)
    
    discovery = NumericSequenceDiscovery()
    
    # 模擬測試
    test_chapter = {
        'title': '第一章',
        'chapter_id': '1',
        'level': 1
    }
    
    test_book_url = "https://www.shidianguji.com/book/TEST001"
    
    safe_print(f"📋 測試章節: {test_chapter['title']} (ID: {test_chapter['chapter_id']})")
    safe_print(f"📚 測試書籍: {test_book_url}")
    
    # 這裡只是演示邏輯，實際測試需要真實的數字序列書籍
    safe_print("\n💡 數字序列發現策略:")
    safe_print("   1. 小數點模式: 1.1, 1.2, 1.3, ...")
    safe_print("   2. 字母後綴模式: 1a, 1b, 1c, ...")
    safe_print("   3. 範圍模式: 101, 102, 103, ...")
    safe_print("   4. 結構分析備用")

if __name__ == "__main__":
    test_numeric_discovery()