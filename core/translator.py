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
from typing import Dict, List, Optional, Tuple

from .tracker import ClassicTracker
from .file_monitor import FileMonitor


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
            print(f"⚠️  獲取書籍資訊失敗: {e}")
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
        """獲取章節列表"""
        print(f"🔍 正在獲取章節列表...")
        
        try:
            response = self.session.get(book_url, timeout=self.config["timeout"])
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
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
                        'chapter_id': self._extract_chapter_id(href)
                    })
                    
            if chapters:
                print(f"✅ 成功獲取 {len(chapters)} 個章節")
                return chapters
            else:
                print("⚠️  未找到章節，嘗試API方式...")
                return self._get_chapters_via_api()
                
        except Exception as e:
            print(f"❌ 獲取章節列表失敗: {e}")
            return []
            
    def _extract_chapter_id(self, href: str) -> Optional[str]:
        """從href提取章節ID"""
        match = re.search(r'/chapter/([^/?]+)', href)
        return match.group(1) if match else None
        
    def _get_chapters_via_api(self) -> List[Dict]:
        """通過API方式獲取章節列表"""
        # 預留API實現
        return []
        
    def crawl_chapter(self, chapter_info: Dict) -> Optional[Dict]:
        """爬取單一章節"""
        print(f"📖 爬取章節: {chapter_info['title']}")
        
        try:
            api_url = f"{self.config['base_url']}/api/book/{self.current_book['id']}/chapter/{chapter_info['chapter_id']}"
            
            response = self.session.get(api_url, timeout=self.config["timeout"])
            if response.status_code != 200:
                print(f"❌ API請求失敗: {response.status_code}")
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            content_data = self._extract_content_from_html(soup, chapter_info['title'])
            
            if content_data:
                self._save_source_text(content_data, chapter_info['number'])
                return content_data
            else:
                print(f"❌ 無法提取章節內容: {chapter_info['title']}")
                return None
                
        except Exception as e:
            print(f"❌ 爬取章節失敗: {e}")
            return None
            
    def _extract_content_from_html(self, soup: BeautifulSoup, title: str) -> Optional[Dict]:
        """從HTML中提取內容"""
        try:
            main_content = soup.find('main', class_='read-layout-main')
            if main_content:
                article = main_content.find('article', class_='chapter-reader')
                if article:
                    content_parts = []
                    
                    for element in article.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
                        text = element.get_text().strip()
                        if text and len(text) > 3:
                            content_parts.append(text)
                    
                    if content_parts:
                        return {
                            'title': title,
                            'content': '\n\n'.join(content_parts)
                        }
                        
        except Exception as e:
            print(f"⚠️  HTML解析錯誤: {e}")
            
        return None
        
    def _save_source_text(self, content_data: Dict, chapter_number: int) -> None:
        """儲存原文"""
        filename = f"{chapter_number:02d}_{content_data['title']}.txt"
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        file_path = self.source_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# {content_data['title']}\n\n")
            f.write(content_data['content'])
            
        # 記錄檔案操作
        self.file_monitor.track_file_write(file_path, "source_text", {
            "chapter_number": chapter_number,
            "title": content_data['title'],
            "content_length": len(content_data['content'])
        })
            
        print(f"✅ 已儲存原文: {filename}")
        
    def generate_translation_template(self, content_data: Dict, chapter_number: int) -> None:
        """生成翻譯模板"""
        print(f"🤖 正在生成翻譯模板: {content_data['title']}")
        
        filename = f"{chapter_number:02d}_{content_data['title']}.md"
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        file_path = self.translation_dir / filename
        
        markdown_content = f"""# {content_data['title']}

## 原文

{content_data['content']}

## 翻譯

[此處應為現代中文翻譯]

原文字數：{len(content_data['content'])} 字
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

---
*翻譯時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*翻譯方式：自動生成模板*
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
            
        # 記錄檔案操作
        self.file_monitor.track_file_write(file_path, "translation_template", {
            "chapter_number": chapter_number,
            "title": content_data['title'],
            "template_type": "auto_generated"
        })
            
        print(f"✅ 已生成翻譯模板: {filename}")
        
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
            
        print(f"✅ 已建立專案說明: {readme_path}")
        
    def translate_book(self, book_url: str) -> bool:
        """翻譯整本書籍的主要流程"""
        print("🚀 啟動道教經典翻譯系統 v2.0")
        print("=" * 50)
        
        try:
            # 1. 獲取書籍資訊
            book_info = self.get_book_info(book_url)
            print(f"📚 書籍：{book_info['title']}")
            print(f"👤 作者：{book_info['author']}")
            
            # 2. 設定專案結構
            self.setup_project_structure(book_info)
            
            # 3. 獲取章節列表
            chapters = self.get_chapter_list(book_url)
            if not chapters:
                print("❌ 無法獲取章節列表，程序終止")
                return False
                
            print(f"📋 找到 {len(chapters)} 個章節")
            
            # 4. 批量爬取和翻譯
            success_count = 0
            for chapter in chapters:
                print(f"\n🔄 處理第 {chapter['number']} 章...")
                
                # 爬取原文
                content_data = self.crawl_chapter(chapter)
                if content_data:
                    # 生成翻譯模板
                    self.generate_translation_template(content_data, chapter['number'])
                    success_count += 1
                    
                # 添加延遲避免被封鎖
                time.sleep(self.config["request_delay"])
                
            # 5. 建立專案文檔
            self.create_project_readme(chapters)
            
            # 6. 追蹤新經典到系統
            if success_count > 0:
                print("\n📊 更新經典追蹤系統...")
                try:
                    processed_chapters = []
                    for i, chapter in enumerate(chapters[:success_count], 1):
                        processed_chapters.append({
                            'number': i,
                            'title': chapter.get('title', f'第{i}章'),
                            'url': chapter.get('url', '')
                        })
                    
                    self.tracker.track_new_classic(
                        book_info=book_info,
                        chapters=processed_chapters,
                        source_dir=self.project_root,
                        translation_dir=self.translation_dir
                    )
                    
                    print("✅ 經典追蹤系統已更新")
                    
                except Exception as e:
                    print(f"⚠️  追蹤系統更新失敗: {e}")
            
            # 7. 生成總結報告
            print(f"\n🎉 翻譯完成！")
            print(f"✅ 成功處理：{success_count}/{len(chapters)} 章")
            print(f"📁 專案位置：{self.project_root}")
            print(f"📝 翻譯檔案：{self.translation_dir}")
            
            return success_count > 0
            
        except Exception as e:
            print(f"❌ 翻譯過程發生錯誤: {e}")
            return False