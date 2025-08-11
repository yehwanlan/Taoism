#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單翻譯器 - 穩定版本
直接輸入URL，自動完成爬取和模板生成
"""

import asyncio
import aiohttp
import re
import json
import time
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

def safe_print(*args, **kwargs):
    """安全打印函數"""
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

class SimpleTranslator:
    """簡單翻譯器"""
    
    def __init__(self):
        self.base_url = "https://www.shidianguji.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def translate_book(self, book_url: str):
        """翻譯書籍的完整流程"""
        safe_print("🚀 簡單翻譯器啟動")
        safe_print("=" * 50)
        
        try:
            # 1. 獲取書籍資訊
            book_info = await self.get_book_info(book_url)
            safe_print(f"📚 書籍：{book_info['title']}")
            safe_print(f"👤 作者：{book_info['author']}")
            
            # 2. 設定專案結構
            self.setup_project_structure(book_info)
            
            # 3. 獲取章節列表
            chapters = await self.get_chapter_list(book_url)
            if not chapters:
                safe_print("❌ 無法獲取章節列表")
                return False
            
            safe_print(f"📋 找到 {len(chapters)} 個章節")
            
            # 4. 爬取章節內容（添加去重功能）
            success_count = 0
            content_hashes = set()  # 用於檢測重複內容
            actual_chapter_number = 1
            
            for i, chapter in enumerate(chapters, 1):
                safe_print(f"\n🔄 處理第 {i} 章: {chapter['title']}")
                
                content = await self.crawl_chapter(chapter)
                if content:
                    # 檢查內容是否重複
                    content_hash = hash(content['content'])
                    if content_hash in content_hashes:
                        safe_print(f"⏭️  跳過重複內容")
                        continue
                    
                    content_hashes.add(content_hash)
                    
                    # 保存原文
                    self.save_source_text(content, actual_chapter_number)
                    # 生成翻譯模板
                    self.generate_translation_template(content, actual_chapter_number)
                    success_count += 1
                    actual_chapter_number += 1
                    safe_print(f"✅ 完成")
                else:
                    safe_print(f"❌ 失敗")
                
                # 延遲避免被封鎖
                await asyncio.sleep(1)
            
            safe_print(f"\n🎉 處理完成！")
            safe_print(f"✅ 成功處理：{success_count}/{len(chapters)} 章")
            safe_print(f"📁 原文位置：{self.source_dir}")
            safe_print(f"📝 翻譯位置：{self.translation_dir}")
            
            return success_count > 0
            
        except Exception as e:
            safe_print(f"❌ 處理失敗: {e}")
            return False
    
    async def get_book_info(self, book_url: str):
        """獲取書籍資訊"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(book_url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # 提取書籍ID
                book_id = re.search(r'/book/([^/?]+)', book_url)
                book_id = book_id.group(1) if book_id else "unknown"
                
                # 提取標題
                title_selectors = ['h1', '.book-title', 'title']
                title = book_id
                
                for selector in title_selectors:
                    title_elem = soup.select_one(selector)
                    if title_elem:
                        title_text = title_elem.get_text().strip()
                        title_text = re.sub(r'[-–—]\s*識典古籍.*', '', title_text)
                        if len(title_text) > 2 and title_text != book_id:
                            title = title_text
                            break
                
                # 提取作者
                author = "未知作者"
                author_selectors = ['.author', '[class*="author"]']
                for selector in author_selectors:
                    author_elem = soup.select_one(selector)
                    if author_elem:
                        author_text = author_elem.get_text().strip()
                        if author_text and len(author_text) > 1:
                            author = author_text
                            break
                
                return {
                    'id': book_id,
                    'title': title,
                    'author': author,
                    'url': book_url
                }
    
    def setup_project_structure(self, book_info):
        """設定專案結構"""
        clean_title = re.sub(r'[<>:"/\\|?*]', '_', book_info['title'])
        clean_title = re.sub(r'\s+', '_', clean_title)
        folder_name = f"{clean_title}_{book_info['id']}"
        
        self.project_root = Path(f"docs/source_texts/{folder_name}")
        self.source_dir = self.project_root / "原文"
        self.translation_dir = Path(f"docs/translations/{folder_name}")
        
        self.source_dir.mkdir(parents=True, exist_ok=True)
        self.translation_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_book = book_info
    
    async def get_chapter_list(self, book_url: str):
        """獲取章節列表"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(book_url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                chapters = []
                
                # 尋找目錄結構
                catalog_selectors = [
                    '.reader-catalog-tree',
                    '.semi-tree-option-list',
                    '.catalog-tree'
                ]
                
                for selector in catalog_selectors:
                    catalog = soup.select_one(selector)
                    if catalog:
                        items = catalog.find_all(['div', 'li'])
                        chapter_number = 1
                        
                        for item in items:
                            link = item.find('a')
                            if link:
                                href = link.get('href', '')
                                title = link.get_text().strip()
                                
                                if href and title and len(title) > 2:
                                    chapter_id = re.search(r'/chapter/([^/?]+)', href)
                                    if chapter_id:
                                        full_url = self.base_url + href if href.startswith('/') else href
                                        
                                        chapters.append({
                                            'number': chapter_number,
                                            'title': title,
                                            'url': full_url,
                                            'chapter_id': chapter_id.group(1)
                                        })
                                        chapter_number += 1
                        
                        if chapters:
                            break
                
                return chapters
    
    async def crawl_chapter(self, chapter_info):
        """爬取章節內容"""
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(chapter_info['url']) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # 提取內容
                    content_selectors = [
                        'main .chapter-reader',
                        '.chapter-content',
                        '.content',
                        'article'
                    ]
                    
                    content_parts = []
                    
                    for selector in content_selectors:
                        content_elem = soup.select_one(selector)
                        if content_elem:
                            for element in content_elem.find_all(['h1', 'h2', 'h3', 'p']):
                                text = element.get_text().strip()
                                if text and len(text) > 3:
                                    content_parts.append(text)
                            break
                    
                    if content_parts:
                        return {
                            'title': chapter_info['title'],
                            'content': '\n\n'.join(content_parts),
                            'chapter_id': chapter_info['chapter_id']
                        }
                    
                    return None
                    
        except Exception as e:
            safe_print(f"  ❌ 爬取錯誤: {e}")
            return None
    
    def save_source_text(self, content_data, chapter_number):
        """保存原文"""
        clean_title = re.sub(r'[<>:"/\\|?*]', '_', content_data['title'])
        filename = f"{chapter_number:02d}_{clean_title}.txt"
        file_path = self.source_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {content_data['title']}\n\n")
                f.write(content_data['content'])
            
            safe_print(f"  📄 已保存原文: {filename}")
            
        except Exception as e:
            safe_print(f"  ❌ 保存原文失敗: {e}")
    
    def generate_translation_template(self, content_data, chapter_number):
        """生成翻譯模板"""
        clean_title = re.sub(r'[<>:"/\\|?*]', '_', content_data['title'])
        filename = f"{chapter_number:02d}_{clean_title}.md"
        file_path = self.translation_dir / filename
        
        template_content = f"""# {content_data['title']}

## 原文

# {content_data['title']}

{content_data['content']}

## 翻譯

[此處填入現代中文翻譯]

---

**翻譯說明：**
- 原文字數：{len(content_data['content'])} 字
- 建議使用AI翻譯工具或人工翻譯
- 保持原文意思，使用現代中文表達
- 保留重要的古代術語，必要時添加註解

**重要詞彙：**
- [待補充重要詞彙解釋]

**文化背景：**
- [待補充相關文化背景]

**翻譯要點：**
- [待補充翻譯注意事項]

---
*翻譯模板生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*原文檔案：{clean_title}.txt*
"""
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            safe_print(f"  📝 已生成翻譯模板: {filename}")
            
        except Exception as e:
            safe_print(f"  ❌ 生成翻譯模板失敗: {e}")

async def main():
    """主函數"""
    translator = SimpleTranslator()
    
    safe_print("🌟 簡單翻譯器")
    safe_print("=" * 30)
    
    while True:
        url = input("\n請輸入書籍URL (或輸入 'quit' 退出): ").strip()
        
        if url.lower() in ['quit', 'exit', 'q']:
            safe_print("👋 再見！")
            break
        
        if not url:
            safe_print("❌ URL不能為空")
            continue
        
        if not url.startswith('http'):
            safe_print("❌ 請輸入完整的URL")
            continue
        
        success = await translator.translate_book(url)
        
        if success:
            safe_print("\n🎉 翻譯任務完成！")
        else:
            safe_print("\n❌ 翻譯任務失敗")
        
        continue_choice = input("\n是否繼續添加其他書籍？(Y/n): ").strip().lower()
        if continue_choice in ['n', 'no', '否']:
            safe_print("👋 再見！")
            break

if __name__ == "__main__":
    asyncio.run(main())