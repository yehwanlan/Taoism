#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全自動古籍翻譯系統

功能：
1. 自動讀取書籍目錄
2. 批量爬取所有章節
3. 自動AI翻譯
4. 生成完整的翻譯專案
"""

import requests
import re
import json
import time
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
from classic_tracker import track_new_classic, generate_tracking_report
from file_tracker import track_file_write, log_operation

class AutoTranslator:
    """全自動古籍翻譯系統"""
    
    def __init__(self, book_url):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 從URL提取書籍資訊
        self.book_url = book_url
        self.book_id = self.extract_book_id(book_url)
        self.base_url = "https://www.shidianguji.com"
        
        # 初始化時不設定專案結構，等獲取書籍資訊後再設定
        self.project_root = None
        self.source_dir = None
        self.translation_dir = None
        self.folder_name = None
        
    def extract_book_id(self, url):
        """從URL提取書籍ID"""
        match = re.search(r'/book/([^/?]+)', url)
        return match.group(1) if match else None
        
    def setup_project_structure(self, book_info=None):
        """設定專案結構"""
        if not self.book_id:
            raise ValueError("無法從URL提取書籍ID")
        
        # 如果提供了書籍資訊，使用書名作為資料夾名稱
        if book_info and book_info['title'] != self.book_id:
            # 清理書名，移除不適合作為資料夾名稱的字符
            clean_title = re.sub(r'[<>:"/\\|?*]', '_', book_info['title'])
            clean_title = re.sub(r'\s+', '_', clean_title)  # 空格替換為下劃線
            folder_name = f"{clean_title}_{self.book_id}"  # 書名_ID格式
        else:
            folder_name = self.book_id
            
        self.project_root = Path(f"docs/source_texts/{folder_name}")
        self.source_dir = self.project_root / "原文"
        self.translation_dir = Path(f"docs/translations/{folder_name}")
        
        # 建立目錄
        self.source_dir.mkdir(parents=True, exist_ok=True)
        self.translation_dir.mkdir(parents=True, exist_ok=True)
        
        # 儲存資料夾名稱供後續使用
        self.folder_name = folder_name
        
    def get_book_info(self):
        """獲取書籍基本資訊"""
        try:
            response = self.session.get(self.book_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取書籍標題 - 改進版本
            book_title = self.book_id  # 預設值
            
            # 嘗試多種方式提取標題
            title_selectors = [
                'h1.Goq6DYSE',  # 十典古籍網的特定類別
                'h1',
                '.book-title h1',
                '.title',
                'title'
            ]
            
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title_text = title_elem.get_text().strip()
                    # 清理標題，移除網站名稱等
                    title_text = re.sub(r'[-–—]\s*識典古籍.*$', '', title_text)
                    title_text = re.sub(r'\s*\|\s*.*$', '', title_text)
                    if len(title_text) > 2 and title_text != self.book_id:
                        book_title = title_text
                        break
            
            # 提取作者資訊 - 改進版本
            author = "未知作者"
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
                        author = author_text
                        break
            
            # 如果還是沒找到作者，嘗試從文本中搜尋
            if author == "未知作者":
                text_content = soup.get_text()
                author_patterns = [
                    r'[\[【\(（]([^】\]）\)]*(?:撰|著|編|輯))[\]】\)）]',
                    r'([^，。；：\s]{2,6})\s*(?:撰|著|編|輯)',
                ]
                for pattern in author_patterns:
                    match = re.search(pattern, text_content)
                    if match:
                        author = match.group(1)
                        break
            
            return {
                'id': self.book_id,
                'title': book_title,
                'author': author,
                'url': self.book_url
            }
            
        except Exception as e:
            print(f"⚠️  獲取書籍資訊失敗: {e}")
            return {
                'id': self.book_id,
                'title': self.book_id,
                'author': "未知作者",
                'url': self.book_url
            }
            
    def get_chapter_list(self):
        """自動獲取完整章節列表"""
        print(f"🔍 正在獲取 {self.book_id} 的章節列表...")
        
        try:
            # 方法1: 嘗試從書籍主頁獲取
            response = self.session.get(self.book_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            chapters = []
            
            # 尋找章節連結
            chapter_links = soup.find_all('a', href=re.compile(r'/chapter/'))
            
            for idx, link in enumerate(chapter_links, 1):
                href = link.get('href')
                title = link.get_text().strip()
                
                if href and title and len(title) > 2:
                    full_url = self.base_url + href if href.startswith('/') else href
                    chapters.append({
                        'number': idx,
                        'title': title,
                        'url': full_url,
                        'chapter_id': self.extract_chapter_id(href)
                    })
                    
            if chapters:
                print(f"✅ 成功獲取 {len(chapters)} 個章節")
                return chapters
                
            # 方法2: 如果主頁沒有找到，嘗試API方式
            print("🔄 嘗試通過API獲取章節列表...")
            return self.get_chapters_via_api()
            
        except Exception as e:
            print(f"❌ 獲取章節列表失敗: {e}")
            return []
            
    def extract_chapter_id(self, href):
        """從href提取章節ID"""
        match = re.search(r'/chapter/([^/?]+)', href)
        return match.group(1) if match else None
        
    def get_chapters_via_api(self):
        """通過API方式獲取章節列表"""
        # 這裡可以實作更複雜的API調用邏輯
        # 暫時返回空列表，實際使用時可以根據具體網站API調整
        return []
        
    def crawl_chapter(self, chapter_info):
        """爬取單一章節"""
        print(f"📖 爬取章節: {chapter_info['title']}")
        
        try:
            # 構建API URL
            api_url = f"{self.base_url}/api/book/{self.book_id}/chapter/{chapter_info['chapter_id']}"
            
            response = self.session.get(api_url, timeout=10)
            if response.status_code != 200:
                print(f"❌ API請求失敗: {response.status_code}")
                return None
                
            # 解析HTML內容
            soup = BeautifulSoup(response.text, 'html.parser')
            content_data = self.extract_content_from_html(soup, chapter_info['title'])
            
            if content_data:
                # 儲存原文
                self.save_source_text(content_data, chapter_info['number'])
                return content_data
            else:
                print(f"❌ 無法提取章節內容: {chapter_info['title']}")
                return None
                
        except Exception as e:
            print(f"❌ 爬取章節失敗: {e}")
            return None
            
    def extract_content_from_html(self, soup, title):
        """從HTML中提取內容"""
        try:
            # 尋找主要內容區域
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
        
    def save_source_text(self, content_data, chapter_number):
        """儲存原文"""
        filename = f"{chapter_number:02d}_{content_data['title']}.txt"
        # 清理檔案名稱
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        file_path = self.source_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# {content_data['title']}\n\n")
            f.write(content_data['content'])
            
        # 追蹤檔案寫入
        track_file_write(file_path, "source_text")
        log_operation("create", file_path, {
            "chapter_number": chapter_number,
            "title": content_data['title'],
            "content_length": len(content_data['content'])
        })
            
        print(f"✅ 已儲存原文: {filename}")
        
    def translate_chapter(self, content_data, chapter_number):
        """翻譯章節（使用AI或規則）"""
        print(f"🤖 正在翻譯: {content_data['title']}")
        
        # 這裡可以整合各種翻譯方法
        translation = self.simple_translate(content_data['content'])
        
        # 生成翻譯檔案
        self.save_translation(content_data, translation, chapter_number)
        
    def simple_translate(self, ancient_text):
        """簡單的翻譯邏輯（可以替換為AI翻譯）"""
        # 這是一個示例，實際使用時可以整合：
        # 1. OpenAI API
        # 2. 本地AI模型
        # 3. 其他翻譯服務
        
        # 暫時返回提示文本
        return f"""[此處應為現代中文翻譯]

原文字數：{len(ancient_text)} 字
建議：請使用AI翻譯工具或人工翻譯此段落。

翻譯要點：
1. 保持原文意思
2. 使用現代中文表達
3. 保留重要的古代術語
4. 添加必要的註解說明
"""
        
    def save_translation(self, content_data, translation, chapter_number):
        """儲存翻譯"""
        filename = f"{chapter_number:02d}_{content_data['title']}.md"
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        file_path = self.translation_dir / filename
        
        markdown_content = f"""# {content_data['title']}

## 原文

{content_data['content']}

## 翻譯

{translation}

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
            
        # 追蹤翻譯檔案寫入
        track_file_write(file_path, "translation_template")
        log_operation("create", file_path, {
            "chapter_number": chapter_number,
            "title": content_data['title'],
            "template_type": "auto_generated"
        })
            
        print(f"✅ 已生成翻譯模板: {filename}")
        
    def create_project_readme(self, book_info, chapters):
        """建立專案說明檔案"""
        readme_content = f"""# {book_info['title']}

## 書籍資訊

- **書名**：{book_info['title']}
- **作者**：{book_info['author']}
- **書籍ID**：{book_info['id']}
- **原始網址**：{book_info['url']}

## 專案說明

本專案使用全自動翻譯系統生成，包含：
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
*使用工具：全自動古籍翻譯系統*
"""
        
        readme_path = self.project_root / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
            
        # 追蹤README檔案
        track_file_write(readme_path, "project_readme")
        log_operation("create", readme_path, {
            "book_id": book_info['id'],
            "book_title": book_info['title'],
            "chapter_count": len(chapters)
        })
            
        print(f"✅ 已建立專案說明: {readme_path}")
        
    def run_full_automation(self):
        """執行完整的自動化流程"""
        print("🚀 啟動全自動古籍翻譯系統")
        print("=" * 50)
        
        # 1. 獲取書籍資訊
        book_info = self.get_book_info()
        print(f"📚 書籍：{book_info['title']}")
        print(f"👤 作者：{book_info['author']}")
        
        # 2. 設定專案結構（使用書名）
        self.setup_project_structure(book_info)
        print(f"📁 專案資料夾：{self.folder_name}")
        
        # 3. 獲取章節列表
        chapters = self.get_chapter_list()
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
                self.translate_chapter(content_data, chapter['number'])
                success_count += 1
                
            # 添加延遲避免被封鎖
            time.sleep(2)
            
        # 5. 建立專案文檔
        self.create_project_readme(book_info, chapters)
        
        # 6. 追蹤新經典到系統
        if success_count > 0:
            print("\n📊 更新經典追蹤系統...")
            try:
                # 準備章節資訊
                processed_chapters = []
                for i, chapter in enumerate(chapters[:success_count], 1):
                    processed_chapters.append({
                        'number': i,
                        'title': chapter.get('title', f'第{i}章'),
                        'url': chapter.get('url', '')
                    })
                
                # 追蹤新經典
                track_new_classic(
                    book_info=book_info,
                    chapters=processed_chapters,
                    source_dir=self.project_root,
                    translation_dir=self.translation_dir
                )
                
                # 生成最新的追蹤報告
                generate_tracking_report()
                print("✅ 經典追蹤系統已更新")
                
            except Exception as e:
                print(f"⚠️  追蹤系統更新失敗: {e}")
        
        # 7. 生成總結報告
        print(f"\n🎉 自動化完成！")
        print(f"✅ 成功處理：{success_count}/{len(chapters)} 章")
        print(f"📁 專案位置：{self.project_root}")
        print(f"📝 翻譯檔案：{self.translation_dir}")
        print(f"📊 追蹤記錄：經典追蹤記錄.json")
        print(f"📋 最新報告：經典追蹤報告.md")
        
        return success_count > 0

def main():
    """主函數 - 支援多書籍處理"""
    
    # 書籍URL列表 - 您可以在這裡添加多本書
    book_urls = [
        "https://www.shidianguji.com/book/SBCK109",  # 抱朴子
        # "https://www.shidianguji.com/book/SBCK001",  # 其他書籍
        # 可以添加更多書籍URL
    ]
    
    print("🌟 全自動古籍翻譯系統")
    print("=" * 60)
    
    for i, book_url in enumerate(book_urls, 1):
        print(f"\n📖 處理第 {i} 本書籍: {book_url}")
        print("-" * 40)
        
        try:
            translator = AutoTranslator(book_url)
            success = translator.run_full_automation()
            
            if success:
                print(f"✅ 第 {i} 本書處理完成")
            else:
                print(f"❌ 第 {i} 本書處理失敗")
                
        except Exception as e:
            print(f"❌ 處理第 {i} 本書時發生錯誤: {e}")
            
        print("-" * 40)
        
    print(f"\n🎊 所有書籍處理完成！")
    print("💡 提示：翻譯模板已生成，您可以直接編輯翻譯內容")

if __name__ == "__main__":
    main()