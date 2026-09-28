#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復缺失章節工具

專門用於修復 太上洞玄灵宝业报因缘经_DZ0336 等經典中缺失的品（章節）
"""

import requests
import re
import json
import time
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys

# 讓 `python tools/xxx.py` 也能找到 core 套件
sys.path.append(str(Path(__file__).parent.parent))
from core.unicode_handler import safe_print


class ChapterFixer:
    """章節修復器"""
    
    def __init__(self):
        self.base_url = "https://www.shidianguji.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def analyze_book_structure(self, book_id):
        """分析書籍結構，找出所有章節"""
        safe_print(f"🔍 分析書籍結構: {book_id}")
        
        book_url = f"{self.base_url}/book/{book_id}"
        
        try:
            response = self.session.get(book_url, timeout=10)
            response.raise_for_status()
            
            # 保存原始HTML用於調試
            debug_file = Path(f"debug_{book_id}_structure.html")
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            safe_print(f"💾 結構調試文件: {debug_file}")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尋找章節列表
            chapters = []
            
            # 方法1: 尋找章節鏈接
            chapter_links = soup.find_all('a', href=re.compile(r'/chapter/'))
            for link in chapter_links:
                href = link.get('href')
                title = link.get_text().strip()
                if href and title and len(title) > 2:
                    chapters.append({
                        'title': title,
                        'url': urljoin(self.base_url, href),
                        'chapter_id': self._extract_chapter_id(href)
                    })
            
            # 方法2: 從JavaScript數據中提取
            script_chapters = self._extract_chapters_from_scripts(response.text)
            if script_chapters:
                chapters.extend(script_chapters)
            
            # 去重
            seen_ids = set()
            unique_chapters = []
            for chapter in chapters:
                if chapter['chapter_id'] not in seen_ids:
                    unique_chapters.append(chapter)
                    seen_ids.add(chapter['chapter_id'])
            
            safe_print(f"✅ 找到 {len(unique_chapters)} 個章節")
            for i, chapter in enumerate(unique_chapters, 1):
                safe_print(f"  {i}. {chapter['title']} ({chapter['chapter_id']})")
            
            return unique_chapters
            
        except Exception as e:
            safe_print(f"❌ 分析書籍結構失敗: {e}")
            return []
    
    def _extract_chapter_id(self, href):
        """從href提取章節ID"""
        match = re.search(r'/chapter/([^/?]+)', href)
        return match.group(1) if match else None
    
    def _extract_chapters_from_scripts(self, html_content):
        """從JavaScript數據中提取章節信息"""
        chapters = []
        
        # 尋找包含章節數據的JavaScript
        patterns = [
            r'window\._ROUTER_DATA\s*=\s*({.*?});',
            r'window\._SSR_DATA\s*=\s*({.*?});',
            r'"chapters":\s*(\[.*?\])',
            r'"chapterList":\s*(\[.*?\])',
        ]
        
        for pattern in patterns:
            matches = re.search(pattern, html_content, re.DOTALL)
            if matches:
                try:
                    data_str = matches.group(1)
                    if data_str.startswith('['):
                        # 直接是章節數組
                        chapter_data = json.loads(data_str)
                    else:
                        # 是完整的數據對象
                        full_data = json.loads(data_str)
                        chapter_data = self._find_chapters_in_data(full_data)
                    
                    if chapter_data:
                        for item in chapter_data:
                            if isinstance(item, dict):
                                title = item.get('title') or item.get('name') or item.get('chapterName')
                                chapter_id = item.get('id') or item.get('chapterId')
                                if title and chapter_id:
                                    chapters.append({
                                        'title': title,
                                        'url': f"{self.base_url}/book/{book_id}/chapter/{chapter_id}",
                                        'chapter_id': chapter_id
                                    })
                        break
                        
                except json.JSONDecodeError:
                    continue
        
        return chapters
    
    def _find_chapters_in_data(self, data):
        """在數據結構中遞歸尋找章節信息"""
        if isinstance(data, dict):
            # 檢查常見的章節字段名
            for key in ['chapters', 'chapterList', 'contents', 'items']:
                if key in data and isinstance(data[key], list):
                    return data[key]
            
            # 遞歸搜索
            for value in data.values():
                result = self._find_chapters_in_data(value)
                if result:
                    return result
        
        elif isinstance(data, list):
            for item in data:
                result = self._find_chapters_in_data(item)
                if result:
                    return result
        
        return None
    
    def crawl_missing_chapter(self, book_id, chapter_info):
        """爬取缺失的章節"""
        safe_print(f"📖 爬取章節: {chapter_info['title']}")
        
        try:
            # 嘗試多種API端點
            api_urls = [
                f"{self.base_url}/api/book/{book_id}/chapter/{chapter_info['chapter_id']}",
                f"{self.base_url}/api/ancientlib/volume/{chapter_info['chapter_id']}/content",
                chapter_info['url']
            ]
            
            content = None
            for api_url in api_urls:
                safe_print(f"  嘗試: {api_url}")
                content = self._try_extract_content(api_url)
                if content:
                    break
                time.sleep(1)  # 避免請求過快
            
            if content:
                return {
                    'title': chapter_info['title'],
                    'content': content,
                    'chapter_id': chapter_info['chapter_id']
                }
            else:
                safe_print(f"❌ 無法獲取章節內容: {chapter_info['title']}")
                return None
                
        except Exception as e:
            safe_print(f"❌ 爬取章節失敗: {e}")
            return None
    
    def _try_extract_content(self, url):
        """嘗試從URL提取內容"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # 如果是JSON響應
            if 'application/json' in response.headers.get('content-type', ''):
                data = response.json()
                return self._extract_text_from_json(data)
            
            # 如果是HTML響應
            else:
                soup = BeautifulSoup(response.text, 'html.parser')
                return self._extract_text_from_html(soup)
                
        except Exception:
            return None
    
    def _extract_text_from_json(self, data):
        """從JSON數據中提取文本"""
        content_parts = []
        
        def extract_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in ['content', 'text', 'body'] and isinstance(value, str):
                        text = value.strip()
                        if len(text) > 10 and re.search(r'[\u4e00-\u9fff]', text):
                            content_parts.append(text)
                    else:
                        extract_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item)
        
        extract_recursive(data)
        
        if content_parts:
            return '\n\n'.join(content_parts)
        return None
    
    def _extract_text_from_html(self, soup):
        """從HTML中提取文本"""
        # 尋找主要內容區域
        content_selectors = [
            'main.read-layout-main article.chapter-reader',
            '.chapter-content',
            '.book-content',
            '.text-content',
            'article',
            '.main-content'
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content_parts = []
                for element in elements[0].find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
                    text = element.get_text().strip()
                    if text and len(text) > 3:
                        content_parts.append(text)
                
                if content_parts:
                    return '\n\n'.join(content_parts)
        
        return None
    
    def save_chapter(self, book_folder, chapter_data, chapter_number):
        """保存章節到文件"""
        # 清理文件名
        clean_title = re.sub(r'[<>:"/\\|?*]', '_', chapter_data['title'])
        filename = f"{chapter_number:02d}_{clean_title}.txt"
        
        file_path = book_folder / "原文" / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# {chapter_data['title']}\n\n")
            f.write(chapter_data['content'])
        
        safe_print(f"✅ 已保存: {filename}")
        return filename
    
    def fix_missing_chapters(self, book_id, book_folder_name):
        """修復缺失的章節"""
        safe_print(f"🔧 開始修復缺失章節: {book_id}")
        safe_print("=" * 60)
        
        # 1. 分析書籍結構
        all_chapters = self.analyze_book_structure(book_id)
        if not all_chapters:
            safe_print("❌ 無法獲取章節列表")
            return False
        
        # 2. 檢查現有文件
        book_folder = Path(f"../docs/source_texts/{book_folder_name}")
        source_folder = book_folder / "原文"
        
        if not source_folder.exists():
            safe_print(f"❌ 找不到源文件夾: {source_folder}")
            return False
        
        existing_files = list(source_folder.glob("*.txt"))
        existing_titles = set()
        
        for file_path in existing_files:
            # 從文件名提取標題
            filename = file_path.stem
            # 移除編號前綴
            title_part = re.sub(r'^\d+_', '', filename)
            existing_titles.add(title_part)
        
        safe_print(f"📁 現有文件: {len(existing_files)} 個")
        
        # 3. 找出缺失的章節
        missing_chapters = []
        for chapter in all_chapters:
            clean_title = re.sub(r'[<>:"/\\|?*]', '_', chapter['title'])
            if clean_title not in existing_titles:
                missing_chapters.append(chapter)
        
        safe_print(f"❌ 缺失章節: {len(missing_chapters)} 個")
        for chapter in missing_chapters:
            safe_print(f"  - {chapter['title']}")
        
        if not missing_chapters:
            safe_print("✅ 沒有缺失的章節")
            return True
        
        # 4. 爬取缺失的章節
        success_count = 0
        for i, chapter in enumerate(missing_chapters, 1):
            safe_print(f"\n📖 處理缺失章節 {i}/{len(missing_chapters)}")
            
            chapter_data = self.crawl_missing_chapter(book_id, chapter)
            if chapter_data:
                # 確定章節編號
                chapter_number = len(existing_files) + success_count + 1
                
                # 保存章節
                filename = self.save_chapter(book_folder, chapter_data, chapter_number)
                success_count += 1
                
                # 更新README
                self._update_readme(book_folder, chapter_data['title'], chapter_number)
            
            time.sleep(2)  # 避免請求過快
        
        safe_print(f"\n🎉 修復完成！成功添加 {success_count}/{len(missing_chapters)} 個章節")
        return success_count > 0
    
    def _update_readme(self, book_folder, chapter_title, chapter_number):
        """更新README文件"""
        readme_path = book_folder / "README.md"
        if readme_path.exists():
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 在章節列表中添加新章節
                new_line = f"- {chapter_number:02d}. {chapter_title}"
                
                # 找到章節列表部分並添加
                if "## 章節列表" in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.startswith("## 章節列表"):
                            # 找到列表結束位置
                            j = i + 1
                            while j < len(lines) and (lines[j].startswith('- ') or lines[j].strip() == ''):
                                j += 1
                            # 插入新章節
                            lines.insert(j, new_line)
                            break
                    
                    with open(readme_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(lines))
                
            except Exception as e:
                safe_print(f"⚠️  更新README失敗: {e}")


def main():
    """主函數"""
    fixer = ChapterFixer()
    
    # 修復 太上洞玄灵宝业报因缘经_DZ0336
    book_id = "DZ0336"
    book_folder_name = "太上洞玄灵宝业报因缘经_DZ0336"
    
    success = fixer.fix_missing_chapters(book_id, book_folder_name)
    
    if success:
        safe_print("\n🎊 修復成功！")
        safe_print("💡 建議：檢查新添加的章節內容是否正確")
    else:
        safe_print("\n❌ 修復失敗")
        safe_print("💡 建議：檢查網絡連接和調試文件")


if __name__ == "__main__":
    main()