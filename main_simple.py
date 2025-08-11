#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道教經典翻譯系統 - 簡化版主程式
結合原有智能功能和新的互動式介面
"""

import asyncio
import aiohttp
import re
import json
import time
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from contextlib import asynccontextmanager
import logging

# 配置日誌系統
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('translation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def safe_print(*args, **kwargs):
    """安全的打印函數"""
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

@dataclass
class ChapterInfo:
    """章節信息數據類"""
    number: int
    title: str
    url: str
    chapter_id: str
    level: int = 1
    is_volume: bool = False
    is_chapter: bool = False

@dataclass
class BookInfo:
    """書籍信息數據類"""
    id: str
    title: str
    author: str
    url: str

class SmartTranslationEngine:
    """智能翻譯引擎"""
    
    def __init__(self, config: Dict = None):
        """初始化翻譯引擎"""
        self.config = self._load_config(config)
        self.current_book: Optional[BookInfo] = None
        self.project_root: Optional[Path] = None
        self.source_dir: Optional[Path] = None
        self.translation_dir: Optional[Path] = None
        
        logger.info("智能翻譯引擎初始化完成")
    
    def _load_config(self, config: Dict = None) -> Dict:
        """載入配置"""
        default_config = {
            "base_url": "https://www.shidianguji.com",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "request_delay": 2.0,
            "max_retries": 3,
            "timeout": 10,
            "concurrent_limit": 3
        }
        
        if config:
            default_config.update(config)
        
        return default_config
    
    @asynccontextmanager
    async def session_manager(self):
        """異步會話管理器"""
        connector = aiohttp.TCPConnector(limit=self.config["concurrent_limit"])
        timeout = aiohttp.ClientTimeout(total=self.config["timeout"])
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': self.config["user_agent"]}
        ) as session:
            try:
                yield session
            finally:
                logger.debug("HTTP會話已關閉")
    
    async def get_book_info(self, book_url: str) -> BookInfo:
        """獲取書籍基本資訊"""
        logger.info(f"獲取書籍資訊: {book_url}")
        
        try:
            async with self.session_manager() as session:
                async with session.get(book_url) as response:
                    response.raise_for_status()
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    book_id = self._extract_book_id(book_url)
                    title = self._extract_title(soup, book_id)
                    author = self._extract_author(soup)
                    
                    return BookInfo(
                        id=book_id,
                        title=title,
                        author=author,
                        url=book_url
                    )
        except Exception as e:
            logger.error(f"獲取書籍資訊失敗: {e}")
            book_id = self._extract_book_id(book_url)
            return BookInfo(
                id=book_id,
                title=book_id,
                author="未知作者",
                url=book_url
            )
    
    def _extract_book_id(self, url: str) -> str:
        """從URL提取書籍ID"""
        match = re.search(r'/book/([^/?]+)', url)
        return match.group(1) if match else "unknown"
    
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
        
        return "未知作者"
    
    async def get_chapter_list(self, book_url: str) -> List[ChapterInfo]:
        """獲取章節列表"""
        logger.info("獲取章節列表...")
        
        try:
            async with self.session_manager() as session:
                async with session.get(book_url) as response:
                    response.raise_for_status()
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    chapters = self._parse_chapters_from_html(soup)
                    logger.info(f"獲取到 {len(chapters)} 個章節")
                    return chapters
                    
        except Exception as e:
            logger.error(f"獲取章節列表失敗: {e}")
            return []
    
    def _parse_chapters_from_html(self, soup: BeautifulSoup) -> List[ChapterInfo]:
        """從HTML解析章節信息"""
        chapters = []
        chapter_number = 1
        
        # 尋找目錄結構
        catalog_selectors = [
            '.reader-catalog-tree',
            '.semi-tree-option-list',
            '.catalog-tree',
            '.chapter-list'
        ]
        
        catalog = None
        for selector in catalog_selectors:
            catalog = soup.select_one(selector)
            if catalog:
                logger.debug(f"找到目錄結構: {selector}")
                break
        
        if catalog:
            items = catalog.find_all(['div', 'li'], class_=re.compile(r'tree-option|chapter-item'))
            
            for item in items:
                link = item.find('a')
                if link:
                    href = link.get('href', '')
                    title = link.get_text().strip()
                    
                    if href and title and len(title) > 2:
                        chapter_id = self._extract_chapter_id(href)
                        if chapter_id:
                            level = self._extract_level_from_item(item)
                            full_url = self._build_full_url(href)
                            
                            chapter_info = ChapterInfo(
                                number=chapter_number,
                                title=title,
                                url=full_url,
                                chapter_id=chapter_id,
                                level=level,
                                is_volume=self._is_volume_title(title, level),
                                is_chapter=self._is_chapter_title(title, level)
                            )
                            
                            chapters.append(chapter_info)
                            chapter_number += 1
        
        return chapters
    
    def _extract_chapter_id(self, href: str) -> Optional[str]:
        """從href提取章節ID"""
        match = re.search(r'/chapter/([^/?]+)', href)
        return match.group(1) if match else None
    
    def _extract_level_from_item(self, item) -> int:
        """從HTML項目中提取層級"""
        level_classes = item.get('class', [])
        for cls in level_classes:
            level_match = re.search(r'level-(\d+)', cls)
            if level_match:
                return int(level_match.group(1))
        
        style = item.get('style', '')
        if 'padding-left' in style:
            padding_match = re.search(r'padding-left:\s*(\d+)px', style)
            if padding_match:
                padding = int(padding_match.group(1))
                return (padding // 28) + 1
        
        return 1
    
    def _build_full_url(self, href: str) -> str:
        """構建完整URL"""
        if href.startswith('http'):
            return href
        elif href.startswith('/'):
            return self.config["base_url"] + href
        else:
            return f"{self.config['base_url']}/{href}"
    
    def _is_volume_title(self, title: str, level: int) -> bool:
        """判斷是否為卷標題"""
        volume_patterns = [r'卷之\w+', r'第\w+卷', r'卷\w+']
        return any(re.search(pattern, title) for pattern in volume_patterns)
    
    def _is_chapter_title(self, title: str, level: int) -> bool:
        """判斷是否為章節標題"""
        chapter_patterns = [r'第\w+章', r'章\w+', r'\w+篇', r'\w+品']
        return any(re.search(pattern, title) for pattern in chapter_patterns)
    
    def setup_project_structure(self, book_info: BookInfo) -> None:
        """設定專案結構"""
        logger.info(f"設定專案結構: {book_info.title}")
        
        clean_title = re.sub(r'[<>:"/\\|?*]', '_', book_info.title)
        clean_title = re.sub(r'\s+', '_', clean_title)
        folder_name = f"{clean_title}_{book_info.id}"
        
        self.project_root = Path(f"docs/source_texts/{folder_name}")
        self.source_dir = self.project_root / "原文"
        self.translation_dir = Path(f"docs/translations/{folder_name}")
        
        # 建立目錄
        self.source_dir.mkdir(parents=True, exist_ok=True)
        self.translation_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_book = book_info
        logger.info(f"專案目錄已建立: {self.project_root}")
    
    async def translate_book(self, book_url: str) -> bool:
        """翻譯整本書籍"""
        safe_print("🚀 啟動智能道教經典翻譯系統")
        safe_print("=" * 50)
        
        start_time = time.time()
        
        try:
            # 1. 獲取書籍資訊
            book_info = await self.get_book_info(book_url)
            safe_print(f"📚 書籍：{book_info.title}")
            safe_print(f"👤 作者：{book_info.author}")
            
            # 2. 設定專案結構
            self.setup_project_structure(book_info)
            
            # 3. 獲取章節列表
            chapters = await self.get_chapter_list(book_url)
            if not chapters:
                logger.error("無法獲取章節列表")
                return False
            
            safe_print(f"📋 找到 {len(chapters)} 個章節")
            
            # 顯示章節結構
            safe_print("\n📖 章節結構：")
            for chapter in chapters:
                level_prefix = "  " * (chapter.level - 1)
                type_indicator = ""
                if chapter.is_volume:
                    type_indicator = " [卷]"
                elif chapter.is_chapter:
                    type_indicator = " [品/章]"
                
                safe_print(f"{level_prefix}{chapter.number:02d}. {chapter.title}{type_indicator}")
            
            safe_print(f"\n✅ 翻譯任務準備完成")
            safe_print(f"📁 專案位置：{self.project_root}")
            safe_print(f"📝 翻譯檔案：{self.translation_dir}")
            
            end_time = time.time()
            duration = end_time - start_time
            safe_print(f"⏱️  準備耗時：{duration:.2f} 秒")
            
            return True
            
        except Exception as e:
            logger.error(f"翻譯過程發生錯誤: {e}")
            safe_print(f"❌ 翻譯過程發生錯誤: {e}")
            return False

class InteractiveCLI:
    """互動式命令行介面"""
    
    def __init__(self):
        self.engine = SmartTranslationEngine()
        self.books_data = self._load_books_data()
    
    def _load_books_data(self) -> Dict:
        """載入書籍數據"""
        data_file = Path("data/books.json")
        if data_file.exists():
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"books": []}
    
    def _save_books_data(self):
        """保存書籍數據"""
        data_file = Path("data/books.json")
        data_file.parent.mkdir(exist_ok=True)
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(self.books_data, f, ensure_ascii=False, indent=2)
    
    def show_menu(self):
        """顯示主選單"""
        safe_print("\n🏛️  道教經典翻譯系統 v2.0")
        safe_print("=" * 40)
        safe_print("請選擇操作：")
        safe_print("1. 📚 查看書籍列表")
        safe_print("2. ➕ 添加新書籍")
        safe_print("3. 📖 翻譯指定書籍")
        safe_print("4. 🔍 智能分析書籍結構")
        safe_print("5. 📊 查看系統狀態")
        safe_print("6. ❓ 幫助說明")
        safe_print("7. 👋 退出程式")
    
    def list_books(self):
        """列出所有書籍"""
        books = self.books_data.get("books", [])
        if not books:
            safe_print("📚 目前沒有書籍記錄")
            return
        
        safe_print(f"\n📚 書籍列表 (共 {len(books)} 本)：")
        safe_print("-" * 50)
        for i, book in enumerate(books, 1):
            safe_print(f"{i:2d}. {book['title']}")
            safe_print(f"     作者：{book['author']}")
            safe_print(f"     ID：{book['id']}")
            safe_print(f"     URL：{book['url']}")
            safe_print()
    
    def add_book(self):
        """添加新書籍"""
        safe_print("\n➕ 添加新書籍")
        safe_print("-" * 30)
        
        while True:
            url = input("請輸入書籍URL: ").strip()
            if not url:
                safe_print("❌ URL不能為空")
                continue
            
            if not url.startswith("http"):
                safe_print("❌ 請輸入完整的URL")
                continue
            
            break
        
        safe_print("🔍 正在獲取書籍資訊...")
        
        try:
            # 使用異步方法獲取書籍資訊
            book_info = asyncio.run(self.engine.get_book_info(url))
            
            # 檢查是否已存在
            existing_books = self.books_data.get("books", [])
            for book in existing_books:
                if book["id"] == book_info.id:
                    safe_print(f"⚠️  書籍已存在：{book_info.title}")
                    return
            
            # 添加到列表
            book_dict = {
                "id": book_info.id,
                "title": book_info.title,
                "author": book_info.author,
                "url": book_info.url,
                "added_time": datetime.now().isoformat()
            }
            
            self.books_data.setdefault("books", []).append(book_dict)
            self._save_books_data()
            
            safe_print(f"✅ 已添加書籍: {book_info.title}")
            safe_print(f"📖 URL: {book_info.url}")
            
        except Exception as e:
            safe_print(f"❌ 添加書籍失敗: {e}")
    
    def translate_book(self):
        """翻譯書籍"""
        books = self.books_data.get("books", [])
        if not books:
            safe_print("📚 目前沒有書籍記錄，請先添加書籍")
            return
        
        safe_print("\n📖 選擇要翻譯的書籍：")
        for i, book in enumerate(books, 1):
            safe_print(f"{i}. {book['title']} - {book['author']}")
        
        try:
            choice = int(input("\n請輸入書籍編號: ")) - 1
            if 0 <= choice < len(books):
                book = books[choice]
                safe_print(f"\n🚀 開始翻譯：{book['title']}")
                success = asyncio.run(self.engine.translate_book(book['url']))
                if success:
                    safe_print("✅ 翻譯準備完成")
                else:
                    safe_print("❌ 翻譯失敗")
            else:
                safe_print("❌ 無效的選擇")
        except ValueError:
            safe_print("❌ 請輸入有效的數字")
    
    def analyze_book_structure(self):
        """智能分析書籍結構"""
        safe_print("\n🔍 智能書籍結構分析")
        safe_print("-" * 30)
        
        url = input("請輸入書籍URL: ").strip()
        if not url:
            safe_print("❌ URL不能為空")
            return
        
        safe_print("🔍 正在分析書籍結構...")
        
        try:
            # 獲取書籍資訊和章節列表
            book_info = asyncio.run(self.engine.get_book_info(url))
            chapters = asyncio.run(self.engine.get_chapter_list(url))
            
            safe_print(f"\n📚 書籍：{book_info.title}")
            safe_print(f"👤 作者：{book_info.author}")
            safe_print(f"📋 章節數量：{len(chapters)}")
            
            if chapters:
                safe_print("\n📖 章節結構分析：")
                safe_print("-" * 40)
                
                level_counts = {}
                volume_count = 0
                chapter_count = 0
                
                for chapter in chapters:
                    level_counts[chapter.level] = level_counts.get(chapter.level, 0) + 1
                    if chapter.is_volume:
                        volume_count += 1
                    elif chapter.is_chapter:
                        chapter_count += 1
                    
                    level_prefix = "  " * (chapter.level - 1)
                    type_indicator = ""
                    if chapter.is_volume:
                        type_indicator = " [卷]"
                    elif chapter.is_chapter:
                        type_indicator = " [品/章]"
                    
                    safe_print(f"{level_prefix}{chapter.number:02d}. {chapter.title}{type_indicator}")
                
                safe_print(f"\n📊 結構統計：")
                safe_print(f"   卷數：{volume_count}")
                safe_print(f"   品/章數：{chapter_count}")
                safe_print(f"   其他：{len(chapters) - volume_count - chapter_count}")
                
                for level, count in sorted(level_counts.items()):
                    safe_print(f"   Level {level}：{count} 個")
            
        except Exception as e:
            safe_print(f"❌ 分析失敗: {e}")
    
    def show_status(self):
        """顯示系統狀態"""
        safe_print("\n📊 系統狀態")
        safe_print("-" * 30)
        
        books = self.books_data.get("books", [])
        safe_print(f"📚 書籍總數：{len(books)}")
        
        # 檢查專案目錄
        docs_dir = Path("docs")
        if docs_dir.exists():
            source_dirs = list((docs_dir / "source_texts").glob("*")) if (docs_dir / "source_texts").exists() else []
            translation_dirs = list((docs_dir / "translations").glob("*")) if (docs_dir / "translations").exists() else []
            safe_print(f"📁 原文專案：{len(source_dirs)}")
            safe_print(f"📝 翻譯專案：{len(translation_dirs)}")
        
        # 檢查日誌文件
        log_file = Path("translation.log")
        if log_file.exists():
            safe_print(f"📋 日誌大小：{log_file.stat().st_size / 1024:.1f} KB")
    
    def show_help(self):
        """顯示幫助說明"""
        safe_print("""
🏛️  道教經典翻譯系統 v2.0 - 幫助說明
========================================

📚 主要功能：
1. 書籍管理 - 添加、查看、管理道教經典書籍
2. 智能翻譯 - 自動爬取和分析古籍內容
3. 結構分析 - 智能識別卷、品、章節結構
4. 專案管理 - 自動建立翻譯專案結構

🎯 使用流程：
1. 添加書籍 - 輸入識典古籍網站的書籍URL
2. 分析結構 - 查看書籍的章節組織結構
3. 開始翻譯 - 自動建立翻譯專案和模板

🔗 支援網站：
- 識典古籍 (shidianguji.com)
- 其他古籍網站（實驗性支援）

💡 提示：
- 建議先使用「智能分析」功能查看書籍結構
- 翻譯結果會保存在 docs/ 目錄下
- 查看 translation.log 獲取詳細日誌
""")
    
    def run(self):
        """運行互動式介面"""
        safe_print("🌟 歡迎使用道教經典翻譯系統 v2.0")
        safe_print("=" * 50)
        
        while True:
            try:
                self.show_menu()
                choice = input("\n請輸入選項 (1-7): ").strip()
                
                if choice == '1':
                    self.list_books()
                elif choice == '2':
                    self.add_book()
                elif choice == '3':
                    self.translate_book()
                elif choice == '4':
                    self.analyze_book_structure()
                elif choice == '5':
                    self.show_status()
                elif choice == '6':
                    self.show_help()
                elif choice == '7':
                    safe_print("👋 感謝使用道教經典翻譯系統！")
                    break
                else:
                    safe_print("❌ 無效選項，請輸入 1-7")
                
                input("\n按 Enter 繼續...")
                
            except KeyboardInterrupt:
                safe_print("\n👋 用戶中斷，退出程式")
                break
            except Exception as e:
                safe_print(f"❌ 發生錯誤: {e}")

def main():
    """主函數"""
    cli = InteractiveCLI()
    cli.run()

if __name__ == "__main__":
    main()