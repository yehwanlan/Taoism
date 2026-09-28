#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道教經典翻譯系統 - 核心翻譯器

整合原有的 auto_translator.py 功能，提供統一的翻譯介面
"""

import requests
import re
import json
import time
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Optional

from .conventions import TRANSLATION_PLACEHOLDER, chapter_stem
from .tracker import ClassicTracker
from .file_monitor import FileMonitor

# 確保safe_print在所有地方都可用
try:
    from .unicode_handler import safe_print
except ImportError:
    def safe_print(*args, **kwargs):
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


class TranslationEngine:
    """翻譯引擎核心類"""
    
    def __init__(self, config: Dict = None):
        """初始化翻譯引擎"""
        self.config = config or self._load_default_config()
        self.session = self._create_session()
        self.tracker = ClassicTracker()
        self.file_monitor = FileMonitor()
        
        # 初始化狀態
        self.current_book = None
        self._chapter_titles = set()  # 本書所有章節標題，用來判斷內容邊界
        self.project_root = None
        self.source_dir = None
        self.translation_dir = None
        
    def _load_default_config(self) -> Dict:
        """載入預設配置"""
        return {
            "base_url": "https://www.shidianguji.com",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "request_delay": 2,
            "max_retries": 3,
            "timeout": 10
        }
        
    def _create_session(self) -> requests.Session:
        """創建HTTP會話"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': self.config["user_agent"]
        })
        return session
        
    def extract_book_id(self, url: str) -> Optional[str]:
        """從URL提取書籍ID"""
        match = re.search(r'/book/([^/?]+)', url)
        return match.group(1) if match else None
        
    def get_book_info(self, book_url: str) -> Dict:
        """獲取書籍基本資訊"""
        try:
            response = self.session.get(book_url, timeout=self.config["timeout"])
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            book_id = self.extract_book_id(book_url)
            
            # 提取書籍標題
            book_title = self._extract_title(soup, book_id)
            
            # 提取作者資訊
            author = self._extract_author(soup)
            
            return {
                'id': book_id,
                'title': book_title,
                'author': author,
                'url': book_url
            }
            
        except Exception as e:
            safe_print(f"⚠️  獲取書籍資訊失敗: {e}")
            return {
                'id': self.extract_book_id(book_url),
                'title': self.extract_book_id(book_url),
                'author': "未知作者",
                'url': book_url
            }     
       
    def _extract_title(self, soup: BeautifulSoup, book_id: str) -> str:
        """提取書籍標題"""
        title_selectors = [
            'h1.Goq6DYSE',
            'h1',
            '.book-title h1',
            '.title',
            'title'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title_text = title_elem.get_text().strip()
                # 清理標題
                title_text = re.sub(r'[-–—]\s*識典古籍.*', '', title_text)
                title_text = re.sub(r'\s*\|\s*.*', '', title_text)
                if len(title_text) > 2 and title_text != book_id:
                    return title_text
                    
        return book_id
        
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """提取作者資訊"""
        author_selectors = [
            '.book-title-author',
            '.author',
            '[class*="author"]'
        ]
        
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                author_text = author_elem.get_text().strip()
                if author_text and len(author_text) > 1:
                    return author_text
                    
        # 嘗試從文本中搜尋
        text_content = soup.get_text()
        author_patterns = [
            r'[\[【\(（]([^】\]）\)]*(?:撰|著|編|輯))[\]】\)）]',
            r'([^，。；：\s]{2,6})\s*(?:撰|著|編|輯)',
        ]
        for pattern in author_patterns:
            match = re.search(pattern, text_content)
            if match:
                return match.group(1)
                
        return "未知作者"
        
    def setup_project_structure(self, book_info: Dict) -> None:
        """設定專案結構"""
        # 清理書名，移除不適合作為資料夾名稱的字符
        clean_title = re.sub(r'[<>:"/\\|?*]', '_', book_info['title'])
        clean_title = re.sub(r'\s+', '_', clean_title)
        folder_name = f"{clean_title}_{book_info['id']}"
        
        self.project_root = Path(f"docs/source_texts/{folder_name}")
        self.source_dir = self.project_root / "原文"
        self.translation_dir = Path(f"docs/translations/{folder_name}")
        
        # 建立目錄
        self.source_dir.mkdir(parents=True, exist_ok=True)
        self.translation_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_book = book_info
        
    def get_chapter_list(self, book_url: str) -> List[Dict]:
        """獲取章節列表（支持層級結構和動態發現）"""
        safe_print(f"🔍 正在獲取章節列表...")
        
        try:
            response = self.session.get(book_url, timeout=self.config["timeout"])
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. 從HTML結構中解析可見的章節
            visible_chapters = self._parse_hierarchical_chapters(soup)
            
            if visible_chapters:
                safe_print(f"📋 從HTML獲取 {len(visible_chapters)} 個可見章節")
                
                # 2. 動態發現隱藏的章節
                all_chapters = self._discover_hidden_chapters(visible_chapters)
                
                safe_print(f"✅ 總共發現 {len(all_chapters)} 個章節（包含隱藏章節）")
                return all_chapters
            else:
                safe_print("⚠️  未找到章節，嘗試傳統方式...")
                return self._get_chapters_traditional(soup)
                
        except Exception as e:
            safe_print(f"❌ 獲取章節列表失敗: {e}")
            return []
    
    def _parse_hierarchical_chapters(self, soup: BeautifulSoup) -> List[Dict]:
        """解析層級章節結構"""
        # 尋找目錄樹結構
        catalog_selectors = [
            '.reader-catalog-tree',
            '.semi-tree-option-list',
            '.catalog-tree',
            '.chapter-list'
        ]
        
        for selector in catalog_selectors:
            catalog = soup.select_one(selector)
            if catalog:
                safe_print(f"🌳 找到目錄結構: {selector}")
                return self._extract_chapters_from_catalog(catalog)
        
        return []
    
    def _extract_chapters_from_catalog(self, catalog_element) -> List[Dict]:
        """從目錄元素中提取章節"""
        chapters = []
        chapter_number = 1
        # 上層章節在目錄中會出現兩次（展開節點 + 自身連結），依章節ID去重
        seen_ids = set()
        
        # 尋找所有章節項目
        items = catalog_element.find_all(['div', 'li'], class_=re.compile(r'tree-option|chapter-item'))
        
        safe_print(f"🔍 在目錄中找到 {len(items)} 個項目")
        
        for item in items:
            # 提取層級信息
            level_classes = item.get('class', [])
            level = 1
            
            for cls in level_classes:
                level_match = re.search(r'level-(\d+)', cls)
                if level_match:
                    level = int(level_match.group(1))
                    break
            
            # 提取鏈接和標題
            link = item.find('a')
            if link:
                href = link.get('href', '')
                title = link.get_text().strip()
                
                if href and title and len(title) > 2:
                    chapter_id = self._extract_chapter_id(href)
                    if chapter_id and chapter_id not in seen_ids:
                        seen_ids.add(chapter_id)
                        full_url = self.config["base_url"] + href if href.startswith('/') else href

                        # 更智能的章節類型判斷
                        is_volume = self._is_volume_title(title, level)
                        is_chapter = self._is_chapter_title(title, level)
                        
                        chapters.append({
                            'number': chapter_number,
                            'title': title,
                            'url': full_url,
                            'chapter_id': chapter_id,
                            'level': level,
                            'is_volume': is_volume,
                            'is_chapter': is_chapter
                        })
                        
                        level_prefix = "  " * (level - 1)
                        safe_print(f"{level_prefix}📄 {chapter_number}. {title} (Level {level}, ID: {chapter_id})")
                        
                        chapter_number += 1
        
        return chapters

    def _get_chapters_traditional(self, soup: BeautifulSoup) -> List[Dict]:
        """傳統方式獲取章節（備用）"""
        chapters = []
        chapter_links = soup.find_all('a', href=re.compile(r'/chapter/'))
        
        for idx, link in enumerate(chapter_links, 1):
            href = link.get('href')
            title = link.get_text().strip()
            
            if href and title and len(title) > 2:
                full_url = self.config["base_url"] + href if href.startswith('/') else href
                chapters.append({
                    'number': idx,
                    'title': title,
                    'url': full_url,
                    'chapter_id': self._extract_chapter_id(href),
                    'level': 1,
                    'is_volume': '卷' in title,
                    'is_chapter': '品' in title or '章' in title
                })
                
        return chapters
    
    def _discover_hidden_chapters(self, visible_chapters: List[Dict]) -> List[Dict]:
        """動態發現隱藏的章節"""
        safe_print("🔍 開始動態發現隱藏章節...")
        
        all_chapters = visible_chapters.copy()
        
        # 檢查章節ID類型
        chapter_id_type = self._detect_chapter_id_type(visible_chapters)
        
        if chapter_id_type == "numeric":
            # 數字型ID，使用原有的數字遞增方式
            return self._discover_numeric_chapters(all_chapters, visible_chapters)
        elif chapter_id_type == "random":
            # 隨機字符串ID，使用不同的策略
            safe_print("🎲 檢測到隨機字符串章節ID，使用替代發現策略")
            return self._discover_random_chapters(all_chapters, visible_chapters)
        else:
            safe_print("⚠️  無法識別章節ID模式，跳過動態發現")
            return all_chapters
    
    def _detect_chapter_id_type(self, visible_chapters: List[Dict]) -> str:
        """檢測章節ID的類型"""
        numeric_count = 0
        random_count = 0
        
        for chapter in visible_chapters:
            if chapter.get('chapter_id'):
                chapter_id = chapter['chapter_id']
                
                # 檢查是否為數字型 (如 DZ0336_1, DZ0336_33)
                if re.search(r'_(\d+)$', chapter_id):
                    numeric_count += 1
                # 檢查是否為隨機字符串型 (如 1k1r7oqmxh8uz)
                elif re.search(r'[a-z0-9]{8,}', chapter_id):
                    random_count += 1
        
        if numeric_count > random_count:
            return "numeric"
        elif random_count > 0:
            return "random"
        else:
            return "unknown"
    
    def _discover_numeric_chapters(self, all_chapters: List[Dict], visible_chapters: List[Dict]) -> List[Dict]:
        """發現數字型章節ID的隱藏章節"""
        # 提取已知的章節ID
        known_ids = set()
        for chapter in visible_chapters:
            if chapter.get('chapter_id'):
                # 提取數字ID
                match = re.search(r'_(\d+)$', chapter['chapter_id'])
                if match:
                    known_ids.add(int(match.group(1)))
        
        if not known_ids:
            return all_chapters
        
        # 確定搜索範圍
        min_id = min(known_ids)
        max_id = max(known_ids)
        
        # 擴展搜索範圍
        search_start = max(1, min_id - 5)
        search_end = min(50, max_id + 10)  # 限制最大搜索範圍
        
        safe_print(f"🎯 數字搜索範圍: {search_start} 到 {search_end}")
        
        # 系統性地探測缺失的章節
        missing_ids = []
        for chapter_id in range(search_start, search_end + 1):
            if chapter_id not in known_ids:
                missing_ids.append(chapter_id)
        
        if missing_ids:
            safe_print(f"🔎 探測 {len(missing_ids)} 個可能的缺失章節...")
            discovered_chapters = self._probe_chapter_ids(missing_ids)
            
            if discovered_chapters:
                safe_print(f"✅ 發現 {len(discovered_chapters)} 個隱藏章節")
                all_chapters.extend(discovered_chapters)
                
                # 重新排序章節
                all_chapters.sort(key=lambda x: self._extract_chapter_number(x.get('chapter_id', '')))
                
                # 重新編號
                for i, chapter in enumerate(all_chapters, 1):
                    chapter['number'] = i
        
        return all_chapters
    
    def _discover_random_chapters(self, all_chapters: List[Dict], visible_chapters: List[Dict]) -> List[Dict]:
        """發現隨機字符串章節ID的隱藏章節"""
        safe_print("🔍 對於隨機ID，使用多種策略發現隱藏章節...")
        
        try:
            # 策略1: 從書籍頁面的JavaScript數據中提取
            book_url = f"{self.config['base_url']}/book/{self.current_book['id']}"
            response = self.session.get(book_url, timeout=self.config["timeout"])
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 嘗試從JavaScript數據中提取完整章節列表
                additional_chapters = self._extract_chapters_from_scripts(soup)
                
                if additional_chapters:
                    safe_print(f"📋 從JavaScript數據中發現 {len(additional_chapters)} 個額外章節")
                    
                    # 過濾掉已知章節
                    known_chapter_ids = {ch.get('chapter_id') for ch in visible_chapters}
                    new_chapters = [ch for ch in additional_chapters 
                                  if ch.get('chapter_id') not in known_chapter_ids]
                    
                    if new_chapters:
                        safe_print(f"✅ 發現 {len(new_chapters)} 個新的隱藏章節")
                        all_chapters.extend(new_chapters)
                        
                        # 重新編號
                        for i, chapter in enumerate(all_chapters, 1):
                            chapter['number'] = i
                        
                        return all_chapters
                
                # 策略2: 深度搜索HTML中的所有章節鏈接
                safe_print("🔍 策略2: 深度搜索HTML中的所有章節鏈接...")
                deep_search_chapters = self._deep_search_chapter_links(soup)
                
                if deep_search_chapters:
                    known_chapter_ids = {ch.get('chapter_id') for ch in all_chapters}
                    new_chapters = [ch for ch in deep_search_chapters 
                                  if ch.get('chapter_id') not in known_chapter_ids]
                    
                    if new_chapters:
                        safe_print(f"✅ 深度搜索發現 {len(new_chapters)} 個新章節")
                        all_chapters.extend(new_chapters)
                        
                        # 重新編號
                        for i, chapter in enumerate(all_chapters, 1):
                            chapter['number'] = i
                        
                        return all_chapters
                
                # 策略3: 嘗試API端點探測
                safe_print("🔍 策略3: 嘗試API端點探測...")
                api_chapters = self._probe_api_endpoints()
                
                if api_chapters:
                    known_chapter_ids = {ch.get('chapter_id') for ch in all_chapters}
                    new_chapters = [ch for ch in api_chapters 
                                  if ch.get('chapter_id') not in known_chapter_ids]
                    
                    if new_chapters:
                        safe_print(f"✅ API探測發現 {len(new_chapters)} 個新章節")
                        all_chapters.extend(new_chapters)
                        
                        # 重新編號
                        for i, chapter in enumerate(all_chapters, 1):
                            chapter['number'] = i
                
                safe_print("⚠️  所有策略都未能發現額外章節")
            
        except Exception as e:
            safe_print(f"❌ 嘗試獲取額外章節時出錯: {e}")
        
        return all_chapters
    
    def _deep_search_chapter_links(self, soup: BeautifulSoup) -> List[Dict]:
        """深度搜索HTML中的所有章節鏈接"""
        chapters = []
        
        # 搜索所有可能的章節鏈接
        all_links = soup.find_all('a', href=True)
        
        chapter_pattern = re.compile(r'/book/' + re.escape(self.current_book['id']) + r'/chapter/([^/?]+)')
        
        found_ids = set()
        
        for link in all_links:
            href = link.get('href', '')
            match = chapter_pattern.search(href)
            
            if match:
                chapter_id = match.group(1)
                if chapter_id not in found_ids:
                    found_ids.add(chapter_id)
                    
                    title = link.get_text().strip()
                    if not title:
                        title = f"章節_{chapter_id}"
                    
                    full_url = self.config["base_url"] + href if href.startswith('/') else href
                    
                    # 嘗試推斷層級
                    level = 1
                    if any(indicator in title for indicator in ['外篇', '內篇', '雜篇', '品第']):
                        level = 2
                    
                    chapters.append({
                        'number': len(chapters) + 1,
                        'title': title,
                        'url': full_url,
                        'chapter_id': chapter_id,
                        'level': level,
                        'is_volume': self._is_volume_title(title, level),
                        'is_chapter': self._is_chapter_title(title, level),
                        'discovered': True,
                        'discovery_method': 'deep_search'
                    })
        
        return chapters
    
    def _probe_api_endpoints(self) -> List[Dict]:
        """探測可能的API端點"""
        chapters = []
        
        # 嘗試一些常見的API端點
        api_endpoints = [
            f"/api/book/{self.current_book['id']}/chapters",
            f"/api/book/{self.current_book['id']}/contents",
            f"/api/book/{self.current_book['id']}/toc",
            f"/api/books/{self.current_book['id']}/chapters",
        ]
        
        for endpoint in api_endpoints:
            try:
                api_url = self.config["base_url"] + endpoint
                response = self.session.get(api_url, timeout=5)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, dict) and 'chapters' in data:
                            api_chapters = self._process_api_chapters(data['chapters'])
                            if api_chapters:
                                safe_print(f"✅ API端點 {endpoint} 返回 {len(api_chapters)} 個章節")
                                chapters.extend(api_chapters)
                                break
                        elif isinstance(data, list):
                            api_chapters = self._process_api_chapters(data)
                            if api_chapters:
                                safe_print(f"✅ API端點 {endpoint} 返回 {len(api_chapters)} 個章節")
                                chapters.extend(api_chapters)
                                break
                    except json.JSONDecodeError:
                        continue
                        
            except Exception:
                continue
        
        return chapters
    
    def _process_api_chapters(self, data) -> List[Dict]:
        """處理API返回的章節數據"""
        chapters = []
        
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    title = item.get('title') or item.get('name') or item.get('chapterName', '')
                    chapter_id = item.get('id') or item.get('chapterId') or item.get('key', '')
                    
                    if title and chapter_id:
                        level = 1
                        if any(indicator in title for indicator in ['外篇', '內篇', '雜篇', '品第']):
                            level = 2
                        
                        chapters.append({
                            'number': len(chapters) + 1,
                            'title': title,
                            'url': f"{self.config['base_url']}/book/{self.current_book['id']}/chapter/{chapter_id}",
                            'chapter_id': chapter_id,
                            'level': level,
                            'is_volume': self._is_volume_title(title, level),
                            'is_chapter': self._is_chapter_title(title, level),
                            'discovered': True,
                            'discovery_method': 'api'
                        })
        
        return chapters
    
    def _extract_chapters_from_scripts(self, soup: BeautifulSoup) -> List[Dict]:
        """從JavaScript數據中提取章節信息"""
        chapters = []
        
        # 尋找包含章節數據的JavaScript
        scripts = soup.find_all('script')
        
        for script in scripts:
            if script.string:
                script_content = script.string
                
                # 尋找章節數據的模式
                patterns = [
                    r'chapters["\']?\s*:\s*(\[.*?\])',
                    r'chapterList["\']?\s*:\s*(\[.*?\])',
                    r'contents["\']?\s*:\s*(\[.*?\])',
                    r'"chapters":\s*(\[.*?\])',
                    r'"chapterList":\s*(\[.*?\])',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, script_content, re.DOTALL)
                    for match in matches:
                        try:
                            chapter_data = json.loads(match)
                            if isinstance(chapter_data, list):
                                for item in chapter_data:
                                    if isinstance(item, dict):
                                        title = item.get('title') or item.get('name') or item.get('chapterName', '')
                                        chapter_id = item.get('id') or item.get('chapterId') or item.get('key', '')
                                        
                                        if title and chapter_id:
                                            chapters.append({
                                                'number': len(chapters) + 1,
                                                'title': title,
                                                'url': f"{self.config['base_url']}/book/{self.current_book['id']}/chapter/{chapter_id}",
                                                'chapter_id': chapter_id,
                                                'level': 2 if '品' in title else 1,
                                                'is_volume': '卷' in title,
                                                'is_chapter': '品' in title or '章' in title,
                                                'discovered': True
                                            })
                        except json.JSONDecodeError:
                            continue
                
                if chapters:
                    break
        
        return chapters
    
    def _probe_chapter_ids(self, chapter_ids: List[int]) -> List[Dict]:
        """探測指定的數字章節ID"""
        discovered = []
        
        for chapter_id in chapter_ids:
            chapter_key = f"{self.current_book['id']}_{chapter_id}"
            test_url = f"{self.config['base_url']}/book/{self.current_book['id']}/chapter/{chapter_key}"
            
            try:
                response = self.session.get(test_url, timeout=5)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 嘗試提取標題
                    title_elem = soup.find('h1', class_='Goq6DYSE')
                    if title_elem:
                        title = title_elem.get_text().strip()
                        
                        # 嘗試從內容中提取實際的品名
                        content = self._extract_content_from_html(soup, title)
                        if content and content.get('content'):
                            actual_title = self._extract_actual_title_from_content(
                                content['content'], title
                            )
                            
                            discovered.append({
                                'number': len(discovered) + 1,  # 臨時編號
                                'title': actual_title,
                                'original_title': title,
                                'url': test_url,
                                'chapter_id': chapter_key,
                                'level': 2 if '品' in actual_title else 1,
                                'is_volume': '卷' in actual_title,
                                'is_chapter': '品' in actual_title or '章' in actual_title,
                                'discovered': True  # 標記為動態發現的章節
                            })
                            
                            safe_print(f"  ✅ 發現: {actual_title} ({chapter_key})")
                        else:
                            safe_print(f"  ⚠️  {chapter_key}: 無有效內容")
                    else:
                        safe_print(f"  ❌ {chapter_key}: 無標題")
                else:
                    safe_print(f"  ❌ {chapter_key}: HTTP {response.status_code}")
                    
            except Exception as e:
                safe_print(f"  ❌ {chapter_key}: {e}")
            
            # 添加延遲避免被封鎖
            time.sleep(1)
        
        return discovered
    
    def _extract_chapter_number(self, chapter_id: str) -> int:
        """從章節ID中提取數字"""
        match = re.search(r'_(\d+)$', chapter_id)
        return int(match.group(1)) if match else 0
            
    def _extract_chapter_id(self, href: str) -> Optional[str]:
        """從href提取章節ID"""
        match = re.search(r'/chapter/([^/?]+)', href)
        return match.group(1) if match else None
        
    def crawl_chapter(self, chapter_info: Dict) -> Optional[Dict]:
        """爬取單一章節（支持層級結構和內容去重）"""
        from .unicode_handler import safe_print
        level_prefix = "  " * (chapter_info.get('level', 1) - 1)
        safe_print(f"📖 {level_prefix}爬取: {chapter_info['title']} (Level {chapter_info.get('level', 1)})")
        
        try:
            # 嘗試API端點
            api_url = f"{self.config['base_url']}/api/book/{self.current_book['id']}/chapter/{chapter_info['chapter_id']}"
            
            response = self.session.get(api_url, timeout=self.config["timeout"])
            if response.status_code == 200:
                try:
                    data = response.json()
                    content = self._extract_content_from_api_response(data)
                    if content:
                        # 從內容中提取實際的品名
                        actual_title = self._extract_actual_title_from_content(content, chapter_info['title'])
                        
                        content_data = {
                            'title': actual_title,
                            'original_title': chapter_info['title'],
                            'content': content,
                            'level': chapter_info.get('level', 1),
                            'is_volume': chapter_info.get('is_volume', False),
                            'is_chapter': chapter_info.get('is_chapter', False),
                            'chapter_id': chapter_info['chapter_id']
                        }
                        
                        # 檢查內容重複並處理
                        processed_content = self._process_content_duplication(content_data, chapter_info)
                        if processed_content:
                            self._save_source_text(processed_content, chapter_info['number'])
                            return processed_content
                        else:
                            safe_print(f"  ⚠️  跳過重複內容: {actual_title}")
                            return None
                            
                except json.JSONDecodeError:
                    pass
            
            # 如果API失敗，嘗試直接訪問頁面
            response = self.session.get(chapter_info['url'], timeout=self.config["timeout"])
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                content_data = self._extract_content_from_html(soup, chapter_info['title'])
                
                if content_data:
                    content_data['level'] = chapter_info.get('level', 1)
                    content_data['is_volume'] = chapter_info.get('is_volume', False)
                    content_data['is_chapter'] = chapter_info.get('is_chapter', False)
                    content_data['chapter_id'] = chapter_info['chapter_id']
                    
                    # 檢查內容重複並處理
                    processed_content = self._process_content_duplication(content_data, chapter_info)
                    if processed_content:
                        self._save_source_text(processed_content, chapter_info['number'])
                        return processed_content
                    else:
                        safe_print(f"  ⚠️  跳過重複內容: {content_data['title']}")
                        return None
            
            safe_print(f"❌ 無法提取章節內容: {chapter_info['title']}")
            return None
                
        except Exception as e:
            safe_print(f"❌ 爬取章節失敗: {e}")
            return None
            
    def _extract_content_from_html(self, soup: BeautifulSoup, title: str) -> Optional[Dict]:
        """從HTML中提取內容

        上層章節的頁面會連同底下的子章節一起顯示，遇到其他章節的標題就停止，
        避免子章節內容被重複存進上層章節。
        """
        other_titles = self._chapter_titles - {title}

        try:
            main_content = soup.find('main', class_='read-layout-main')
            if main_content:
                article = main_content.find('article', class_='chapter-reader')
                if article:
                    content_parts = []

                    for element in article.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
                        text = element.get_text().strip()
                        if element.name != 'p' and content_parts and text in other_titles:
                            break
                        if text and len(text) > 3:
                            content_parts.append(text)
                    
                    if content_parts:
                        return {
                            'title': title,
                            'content': '\n\n'.join(content_parts)
                        }
                        
        except Exception as e:
            safe_print(f"⚠️  HTML解析錯誤: {e}")
            
        return None
    
    def _extract_content_from_api_response(self, data) -> Optional[str]:
        """從API響應中提取內容"""
        content_parts = []
        
        def extract_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in ['content', 'text', 'body', 'html'] and isinstance(value, str):
                        text = value.strip()
                        if len(text) > 20 and re.search(r'[\u4e00-\u9fff]', text):
                            # 清理HTML標籤
                            clean_text = re.sub(r'<[^>]+>', '', text)
                            if clean_text.strip():
                                content_parts.append(clean_text.strip())
                    else:
                        extract_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item)
        
        extract_recursive(data)
        
        if content_parts:
            return '\n\n'.join(content_parts)
        return None
    
    def _extract_actual_title_from_content(self, content: str, fallback_title: str) -> str:
        """從內容中提取實際的品名"""
        lines = content.split('\n')
        
        for line in lines[:10]:  # 檢查前10行
            line = line.strip()
            
            # 尋找品名模式
            if '品第' in line and len(line) < 30:
                return line
            
            # 尋找其他可能的章節標題
            if line and len(line) < 50 and not line.startswith('#'):
                # 檢查是否包含品、章、卷等關鍵字
                if any(keyword in line for keyword in ['品', '章', '卷']):
                    if '太上洞玄' not in line:  # 排除書名
                        return line
        
        return fallback_title
    
    def _analyze_chapter_id_patterns(self, chapters: List[Dict]) -> Dict:
        """分析章節ID模式並推薦策略"""
        if not chapters:
            return {'pattern_type': 'unknown', 'strategy': 'default', 'confidence': 0.0}
        
        chapter_ids = [ch.get('chapter_id', '') for ch in chapters if ch.get('chapter_id')]
        
        if not chapter_ids:
            return {'pattern_type': 'unknown', 'strategy': 'default', 'confidence': 0.0}
        
        safe_print(f"📊 分析 {len(chapter_ids)} 個章節ID模式...")
        
        # 簡化的模式分析
        patterns = {
            'numeric': 0,
            'random_string': 0,
            'mixed': 0
        }
        
        for chapter_id in chapter_ids:
            if chapter_id.isdigit():
                patterns['numeric'] += 1
            elif len(chapter_id) >= 8 and re.match(r'^[a-zA-Z0-9]+$', chapter_id):
                patterns['random_string'] += 1
            else:
                patterns['mixed'] += 1
        
        # 確定主要模式
        total = len(chapter_ids)
        dominant_pattern = max(patterns.items(), key=lambda x: x[1])
        confidence = dominant_pattern[1] / total
        
        safe_print(f"🎯 ID模式分析:")
        safe_print(f"   數字序列: {patterns['numeric']} 個 ({patterns['numeric']/total*100:.1f}%)")
        safe_print(f"   隨機字符串: {patterns['random_string']} 個 ({patterns['random_string']/total*100:.1f}%)")
        safe_print(f"   混合模式: {patterns['mixed']} 個 ({patterns['mixed']/total*100:.1f}%)")
        safe_print(f"   主要模式: {dominant_pattern[0]} (信心度: {confidence:.2f})")
        
        # 推薦策略
        if dominant_pattern[0] == 'numeric' and confidence > 0.8:
            strategy = 'numeric_sequence_strategy'
            safe_print(f"💡 推薦策略: 數字序列探測 + 結構分析")
        elif dominant_pattern[0] == 'random_string' and confidence > 0.7:
            strategy = 'structure_based_strategy'
            safe_print(f"💡 推薦策略: 結構化分析（當前使用的方法）")
        else:
            strategy = 'hybrid_strategy'
            safe_print(f"💡 推薦策略: 混合策略")
        
        return {
            'pattern_type': dominant_pattern[0],
            'strategy': strategy,
            'confidence': confidence,
            'patterns': patterns
        }
    
    def _smart_discover_sub_chapters(self, soup: BeautifulSoup, parent_chapter: Dict) -> List[Dict]:
        """智能發現子章節 - 基於目錄結構分析"""
        sub_chapters = []
        
        try:
            # 尋找目錄結構
            catalog = soup.select_one('.reader-catalog-tree')
            if not catalog:
                # 備用選擇器
                for selector in ['.semi-tree-option-list', '.catalog-tree', '.chapter-list']:
                    catalog = soup.select_one(selector)
                    if catalog:
                        break
            
            if catalog:
                items = catalog.find_all(['div', 'li'], class_=re.compile(r'tree-option|chapter-item'))
                parent_level = parent_chapter.get('level', 1)
                parent_chapter_id = parent_chapter['chapter_id']
                
                # 尋找當前章節在目錄中的位置
                current_index = -1
                for i, item in enumerate(items):
                    link = item.find('a')
                    if link:
                        href = link.get('href', '')
                        title = link.get_text().strip()
                        
                        # 檢查是否是當前章節 - 使用更精確的匹配
                        if parent_chapter_id in href:
                            current_index = i
                            break
                
                # 如果找到當前章節，檢查後續項目
                if current_index >= 0:
                    for i in range(current_index + 1, len(items)):
                        item = items[i]
                        link = item.find('a')
                        
                        if not link:
                            continue
                        
                        href = link.get('href', '')
                        title = link.get_text().strip()
                        item_level = self._extract_level_from_item(item)
                        
                        # 如果層級比父章節高，說明是子章節
                        if item_level > parent_level:
                            chapter_id = self._extract_chapter_id(href)
                            if chapter_id and title and len(title) > 2:
                                from urllib.parse import urljoin
                                full_url = urljoin(self.config["base_url"], href)
                                
                                sub_chapters.append({
                                    'title': title,
                                    'url': full_url,
                                    'chapter_id': chapter_id,
                                    'level': item_level,
                                    'parent_id': parent_chapter['chapter_id'],
                                    'parent_title': parent_chapter['title'],
                                    'is_volume': self._is_volume_title(title, item_level),
                                    'is_chapter': self._is_chapter_title(title, item_level),
                                    'discovered': True,
                                    'discovery_method': 'smart_structure_analysis'
                                })
                        
                        # 如果層級等於或小於父章節，停止搜索
                        elif item_level <= parent_level:
                            break
            
        except Exception as e:
            safe_print(f"      ⚠️  智能發現錯誤: {e}")
        
        return sub_chapters
    
    def _extract_level_from_item(self, item) -> int:
        """從HTML項目中提取層級"""
        # 方法1: 檢查CSS類中的層級信息
        level_classes = item.get('class', [])
        for cls in level_classes:
            level_match = re.search(r'level-(\d+)', cls)
            if level_match:
                return int(level_match.group(1))
        
        # 方法2: 檢查樣式中的padding-left
        style = item.get('style', '')
        if 'padding-left' in style:
            padding_match = re.search(r'padding-left:\s*(\d+)px', style)
            if padding_match:
                padding = int(padding_match.group(1))
                # 假設每層級縮進28px
                level = (padding // 28) + 1
                return level
        
        return 1
    
    def _is_volume_title(self, title: str, level: int) -> bool:
        """判斷是否為卷標題"""
        volume_patterns = [r'卷之\w+', r'第\w+卷', r'卷\w+']
        return any(re.search(pattern, title) for pattern in volume_patterns)
    
    def _is_chapter_title(self, title: str, level: int) -> bool:
        """判斷是否為章節標題"""
        chapter_patterns = [r'第\w+章', r'章\w+', r'\w+篇', r'\w+品']
        return any(re.search(pattern, title) for pattern in chapter_patterns)
    
    def _process_content_duplication(self, content_data: Dict, chapter_info: Dict) -> Optional[Dict]:
        """處理內容重複問題"""
        is_volume = content_data.get('is_volume', False)
        is_chapter = content_data.get('is_chapter', False)
        
        # 如果是卷（Level 1），檢查是否與品的內容重複
        if is_volume and content_data.get('level', 1) == 1:
            return self._handle_volume_content(content_data, chapter_info)
        
        # 如果是品（Level 2），直接保存
        elif is_chapter and content_data.get('level', 1) == 2:
            return content_data
        
        # 其他情況，直接保存
        else:
            return content_data
    
    def _handle_volume_content(self, content_data: Dict, chapter_info: Dict) -> Optional[Dict]:
        """處理卷的內容，避免與品重複"""
        content = content_data['content']
        
        # 檢查內容是否包含具體的品
        if self._content_contains_specific_chapter(content):
            # 如果卷的內容包含具體品的內容，則提取卷的概述部分
            volume_summary = self._extract_volume_summary(content, content_data['title'])
            
            if volume_summary and len(volume_summary) > 100:
                content_data['content'] = volume_summary
                content_data['content_type'] = 'volume_summary'
                safe_print(f"  📝 提取卷概述: {len(volume_summary)} 字符")
                return content_data
            else:
                # 如果無法提取有意義的概述，跳過這個卷
                safe_print(f"  ⚠️  卷內容與品重複，跳過")
                return None
        else:
            # 如果卷的內容不包含具體品，直接保存
            return content_data
    
    def _content_contains_specific_chapter(self, content: str) -> bool:
        """檢查內容是否包含具體的品"""
        # 檢查是否包含品的標題模式
        chapter_patterns = [
            r'品第[一二三四五六七八九十]+',
            r'第[一二三四五六七八九十]+品',
            r'品第\d+',
            r'第\d+品'
        ]
        
        for pattern in chapter_patterns:
            if re.search(pattern, content):
                return True
        
        return False
    
    def _extract_volume_summary(self, content: str, volume_title: str) -> str:
        """從卷的內容中提取概述部分"""
        lines = content.split('\n')
        summary_lines = []
        
        # 添加卷標題
        summary_lines.append(volume_title)
        summary_lines.append('')
        
        # 查找卷的介紹或概述部分
        in_summary = False

        for line in lines:
            line = line.strip()
            
            # 如果遇到品的標題，停止提取
            if re.search(r'品第[一二三四五六七八九十]+', line) or re.search(r'第[一二三四五六七八九十]+品', line):
                break
            
            # 如果是卷標題行，開始提取
            if volume_title in line or '卷之' in line:
                in_summary = True
                continue
            
            # 提取概述內容
            if in_summary and line and len(line) > 10:
                summary_lines.append(line)
                
                # 如果已經有足夠的概述內容，停止
                if len('\n'.join(summary_lines)) > 500:
                    break
        
        # 如果沒有找到有意義的概述，返回空
        if len(summary_lines) <= 3:
            return ""
        
        # 添加說明
        summary_lines.append('')
        summary_lines.append('---')
        summary_lines.append('注：本卷包含多個品，具體品的內容請參考對應的品文件。')
        
        return '\n'.join(summary_lines)
        
    def _save_source_text(self, content_data: Dict, chapter_number: int) -> None:
        """儲存原文（支持層級結構）"""
        # 使用實際提取的標題
        title = content_data.get('title', content_data.get('original_title', f'章節{chapter_number}'))
        level = content_data.get('level', 1)
        
        # 根據層級調整文件名格式
        level_prefix = "  " * (level - 1) if level > 1 else ""

        filename = f"{chapter_stem(chapter_number, title)}.txt"
        file_path = self.source_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            
            # 根據內容類型添加說明
            content_type = content_data.get('content_type', 'full_content')
            if content_type == 'volume_summary':
                f.write("**說明：** 本文件為卷的概述，具體品的內容請參考對應的品文件。\n\n")
            
            f.write(content_data['content'])
            
        # 記錄檔案操作
        self.file_monitor.track_file_write(file_path, "source_text", {
            "chapter_number": chapter_number,
            "title": title,
            "original_title": content_data.get('original_title', title),
            "level": level,
            "is_volume": content_data.get('is_volume', False),
            "is_chapter": content_data.get('is_chapter', False),
            "content_length": len(content_data['content'])
        })
        
        level_indicator = f" (Level {level})" if level > 1 else ""
        safe_print(f"✅ {level_prefix}已儲存: {filename}{level_indicator}")
        
    def generate_translation_template(self, content_data: Dict, chapter_number: int) -> None:
        """生成翻譯模板（支持層級結構）"""
        title = content_data.get('title', content_data.get('original_title', f'章節{chapter_number}'))
        level = content_data.get('level', 1)
        level_prefix = "  " * (level - 1) if level > 1 else ""
        
        safe_print(f"🤖 {level_prefix}生成翻譯模板: {title}")
        
        filename = f"{chapter_stem(chapter_number, title)}.md"
        file_path = self.translation_dir / filename
        
        # 根據層級和類型調整模板內容
        structure_info = ""
        if content_data.get('is_volume'):
            structure_info = f"\n**結構層級：** 卷 (Level {level})"
        elif content_data.get('is_chapter'):
            structure_info = f"\n**結構層級：** 品/章 (Level {level})"
        
        markdown_content = f"""# {title}

## 原文

{content_data['content']}

## 翻譯

{TRANSLATION_PLACEHOLDER}

原文字數：{len(content_data['content'])} 字{structure_info}
建議：請使用AI翻譯工具或人工翻譯此段落。

翻譯要點：
1. 保持原文意思
2. 使用現代中文表達
3. 保留重要的古代術語
4. 添加必要的註解說明

## 註解

**重要詞彙：**
- [待補充]

**文化背景：**
- [待補充]

**翻譯要點：**
- [待補充]

## 結構信息

**層級：** Level {level}
**類型：** {'卷' if content_data.get('is_volume') else '品/章' if content_data.get('is_chapter') else '章節'}
**原始標題：** {content_data.get('original_title', title)}

---
*翻譯時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*翻譯方式：自動生成模板（支持層級結構）*
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
            
        # 記錄檔案操作
        self.file_monitor.track_file_write(file_path, "translation_template", {
            "chapter_number": chapter_number,
            "title": title,
            "original_title": content_data.get('original_title', title),
            "level": level,
            "is_volume": content_data.get('is_volume', False),
            "is_chapter": content_data.get('is_chapter', False),
            "template_type": "hierarchical_auto_generated"
        })
        
        level_indicator = f" (Level {level})" if level > 1 else ""
        safe_print(f"✅ {level_prefix}已生成翻譯模板: {filename}{level_indicator}")
        
    def create_project_readme(self, chapters: List[Dict]) -> None:
        """建立專案說明檔案"""
        book_info = self.current_book
        
        readme_content = f"""# {book_info['title']}

## 書籍資訊

- **書名**：{book_info['title']}
- **作者**：{book_info['author']}
- **書籍ID**：{book_info['id']}
- **原始網址**：{book_info['url']}

## 專案說明

本專案使用道教經典翻譯系統生成，包含：
1. 自動爬取的古文原文
2. 自動生成的翻譯模板
3. 完整的專案結構

## 章節列表

總共 {len(chapters)} 個章節：

"""
        
        for chapter in chapters:
            readme_content += f"- {chapter['number']:02d}. {chapter['title']}\n"
            
        readme_content += f"""

## 使用說明

1. **原文檔案**：位於 `原文/` 目錄
2. **翻譯檔案**：位於 `../translations/{book_info['id']}/` 目錄
3. **翻譯模板**：已自動生成，可直接編輯

## 翻譯進度

- [x] 原文爬取完成
- [x] 翻譯模板生成完成
- [ ] 人工翻譯待完成

---
*專案建立時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*使用工具：道教經典翻譯系統 v2.0*
"""
        
        readme_path = self.project_root / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
            
        # 記錄檔案操作
        self.file_monitor.track_file_write(readme_path, "project_readme", {
            "book_id": book_info['id'],
            "book_title": book_info['title'],
            "chapter_count": len(chapters)
        })
            
        safe_print(f"✅ 已建立專案說明: {readme_path}")
        
    def translate_book(self, book_url: str) -> bool:
        """翻譯整本書籍的主要流程"""
        safe_print("🚀 啟動道教經典翻譯系統 v2.0")
        safe_print("=" * 50)
        
        try:
            # 1. 獲取書籍資訊
            book_info = self.get_book_info(book_url)
            safe_print(f"📚 書籍：{book_info['title']}")
            safe_print(f"👤 作者：{book_info['author']}")
            
            # 2. 設定專案結構
            self.setup_project_structure(book_info)
            
            # 3. 設置當前書籍（用於動態發現章節）
            self.current_book = book_info
            
            # 4. 獲取章節列表（包含動態發現）
            chapters = self.get_chapter_list(book_url)
            if not chapters:
                safe_print("❌ 無法獲取章節列表，程序終止")
                return False
                
            safe_print(f"📋 找到 {len(chapters)} 個初始章節")
            
            # 5. 智能章節ID分析
            safe_print("\n🔍 開始智能章節ID分析...")
            id_pattern = self._analyze_chapter_id_patterns(chapters)
            
            # 6. 智能子章節發現階段
            safe_print(f"\n🔍 開始智能子章節發現階段...")
            safe_print(f"📊 使用策略: {id_pattern['strategy']}")
            all_chapters = chapters.copy()
            discovered_sub_chapters = []
            
            for chapter in chapters:
                if chapter.get('level', 1) == 1:  # 只檢查頂級章節
                    level_prefix = "  " * (chapter.get('level', 1) - 1)
                    safe_print(f"{level_prefix}🔍 檢查章節: {chapter['title']}")
                    
                    try:
                        # 訪問章節頁面進行智能分析
                        response = self.session.get(chapter['url'], timeout=self.config["timeout"])
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            
                            # 智能發現子章節（目錄中已經有的章節不重複加入）
                            known_ids = {c['chapter_id'] for c in all_chapters}
                            sub_chapters = [
                                sub for sub in self._smart_discover_sub_chapters(soup, chapter)
                                if sub['chapter_id'] not in known_ids
                            ]

                            if sub_chapters:
                                safe_print(f"{level_prefix}   ✅ 發現 {len(sub_chapters)} 個子章節")
                                
                                # 為子章節分配編號並添加到總列表
                                for sub_chapter in sub_chapters:
                                    sub_chapter['number'] = len(all_chapters) + 1
                                    all_chapters.append(sub_chapter)
                                    discovered_sub_chapters.append(sub_chapter)
                                    
                                    sub_level_prefix = "  " * (sub_chapter.get('level', 2) - 1)
                                    safe_print(f"{sub_level_prefix}     📄 {sub_chapter['title']} (Level {sub_chapter['level']})")
                            else:
                                safe_print(f"{level_prefix}   ⚠️  未發現子章節")
                        else:
                            safe_print(f"{level_prefix}   ❌ 無法訪問頁面: HTTP {response.status_code}")
                            
                    except Exception as e:
                        safe_print(f"{level_prefix}   ❌ 檢查子章節時出錯: {e}")
                    
                    # 添加延遲避免請求過快
                    time.sleep(1)
            
            safe_print(f"\n📊 智能發現結果:")
            safe_print(f"   初始章節: {len(chapters)}")
            safe_print(f"   發現子章節: {len(discovered_sub_chapters)}")
            safe_print(f"   總章節數: {len(all_chapters)}")
            
            if discovered_sub_chapters:
                safe_print(f"\n🤖 智能發現的子章節:")
                for sub_chapter in discovered_sub_chapters:
                    sub_level_prefix = "  " * (sub_chapter.get('level', 2) - 1)
                    safe_print(f"{sub_level_prefix}- {sub_chapter['title']} (父章節: {sub_chapter.get('parent_title', '未知')})")
            
            # 使用包含子章節的完整列表
            chapters = all_chapters
            
            # 重新編號所有章節
            for i, chapter in enumerate(chapters, 1):
                chapter['number'] = i
                
            safe_print(f"\n📋 最終章節總數: {len(chapters)}")
            
            # 7. 批量爬取和翻譯
            self._chapter_titles = {chapter['title'] for chapter in chapters}
            # 記錄實際存檔用的編號與標題（標題可能已被改成內容中的品名），供追蹤系統找檔案
            processed_chapters = []
            for chapter in chapters:
                safe_print(f"\n🔄 處理第 {chapter['number']} 章...")

                # 爬取原文
                content_data = self.crawl_chapter(chapter)
                if content_data:
                    # 生成翻譯模板
                    self.generate_translation_template(content_data, chapter['number'])
                    processed_chapters.append({
                        'number': chapter['number'],
                        'title': content_data['title'],
                        'url': chapter.get('url', '')
                    })
                    
                # 添加延遲避免被封鎖
                time.sleep(self.config["request_delay"])
                
            # 8. 建立專案文檔
            self.create_project_readme(chapters)
            
            # 9. 追蹤新經典到系統
            success_count = len(processed_chapters)
            if success_count > 0:
                safe_print("\n📊 更新經典追蹤系統...")
                try:
                    self.tracker.track_new_classic(
                        book_info=book_info,
                        chapters=processed_chapters,
                        source_dir=self.project_root,
                        translation_dir=self.translation_dir
                    )
                    
                    safe_print("✅ 經典追蹤系統已更新")
                    
                except Exception as e:
                    safe_print(f"⚠️  追蹤系統更新失敗: {e}")
            
            # 10. 生成總結報告
            safe_print(f"\n🎉 翻譯完成！")
            safe_print(f"✅ 成功處理：{success_count}/{len(chapters)} 章")
            safe_print(f"📁 專案位置：{self.project_root}")
            safe_print(f"📝 翻譯檔案：{self.translation_dir}")
            
            return success_count > 0
            
        except Exception as e:
            safe_print(f"❌ 翻譯過程發生錯誤: {e}")
            return False