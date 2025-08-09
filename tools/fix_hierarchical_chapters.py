#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
from core.unicode_handler import safe_print
修復層級章節工具

專門處理有層級結構的經典，如每卷包含多個品的情況
"""

import requests
import re
import json
import time
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class HierarchicalChapterFixer:
    """層級章節修復器"""
    
    def __init__(self):
        self.base_url = "https://www.shidianguji.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def analyze_hierarchical_structure(self, book_id):
        """分析層級結構"""
        safe_print(f"🔍 分析層級結構: {book_id}")
        
        book_url = f"{self.base_url}/book/{book_id}"
        
        try:
            response = self.session.get(book_url, timeout=10)
            response.raise_for_status()
            
            # 從JavaScript中提取完整的章節樹結構
            script_data = self._extract_chapter_tree_from_scripts(response.text)
            
            if script_data:
                return script_data
            
            # 如果JavaScript方法失敗，嘗試HTML解析
            return self._parse_html_structure(response.text)
            
        except Exception as e:
            safe_print(f"❌ 分析結構失敗: {e}")
            return None
    
    def _extract_chapter_tree_from_scripts(self, html_content):
        """從JavaScript中提取章節樹結構"""
        safe_print("🌳 從JavaScript提取章節樹...")
        
        # 尋找包含章節數據的JavaScript變量
        patterns = [
            r'window\._ROUTER_DATA\s*=\s*({.*?});',
            r'window\._SSR_DATA\s*=\s*({.*?});',
            r'__MODERN_SERVER_DATA__[^>]*>([^<]+)',
        ]
        
        for pattern in patterns:
            matches = re.search(pattern, html_content, re.DOTALL)
            if matches:
                try:
                    data_str = matches.group(1)
                    data = json.loads(data_str)
                    
                    # 遞歸搜尋章節結構
                    chapter_tree = self._find_chapter_tree_in_data(data)
                    if chapter_tree:
                        safe_print(f"✅ 從JavaScript找到章節樹結構")
                        return chapter_tree
                        
                except json.JSONDecodeError as e:
                    safe_print(f"⚠️  JSON解析失敗: {e}")
                    continue
        
        return None
    
    def _find_chapter_tree_in_data(self, data):
        """在數據中遞歸尋找章節樹"""
        if isinstance(data, dict):
            # 檢查是否包含章節樹的關鍵字段
            for key in ['chapterTree', 'chapters', 'contents', 'catalog', 'toc']:
                if key in data:
                    tree_data = data[key]
                    if isinstance(tree_data, (list, dict)):
                        return self._parse_tree_structure(tree_data)
            
            # 遞歸搜索
            for value in data.values():
                result = self._find_chapter_tree_in_data(value)
                if result:
                    return result
        
        elif isinstance(data, list):
            for item in data:
                result = self._find_chapter_tree_in_data(item)
                if result:
                    return result
        
        return None
    
    def _parse_tree_structure(self, tree_data):
        """解析樹結構"""
        chapters = []
        
        def parse_node(node, level=1, parent_title=""):
            if isinstance(node, dict):
                # 提取節點信息
                title = node.get('title') or node.get('name') or node.get('chapterName', '')
                chapter_id = node.get('id') or node.get('chapterId') or node.get('key', '')
                
                if title and chapter_id:
                    chapter_info = {
                        'title': title,
                        'chapter_id': chapter_id,
                        'level': level,
                        'parent_title': parent_title,
                        'url': f"{self.base_url}/book/DZ0336/chapter/{chapter_id}",
                        'children': []
                    }
                    
                    # 處理子節點
                    children_key = None
                    for key in ['children', 'subChapters', 'items']:
                        if key in node and isinstance(node[key], list):
                            children_key = key
                            break
                    
                    if children_key:
                        for child in node[children_key]:
                            child_chapters = parse_node(child, level + 1, title)
                            chapter_info['children'].extend(child_chapters)
                    
                    chapters.append(chapter_info)
                    return [chapter_info]
            
            elif isinstance(node, list):
                all_chapters = []
                for item in node:
                    item_chapters = parse_node(item, level, parent_title)
                    all_chapters.extend(item_chapters)
                return all_chapters
            
            return []
        
        if isinstance(tree_data, list):
            for item in tree_data:
                parse_node(item)
        else:
            parse_node(tree_data)
        
        return chapters
    
    def _parse_html_structure(self, html_content):
        """從HTML解析結構（備用方法）"""
        safe_print("📄 從HTML解析結構...")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 尋找目錄結構
        catalog_selectors = [
            '.reader-catalog-tree',
            '.catalog-tree',
            '.chapter-list',
            '.toc'
        ]
        
        for selector in catalog_selectors:
            catalog = soup.select_one(selector)
            if catalog:
                return self._parse_catalog_html(catalog)
        
        return None
    
    def _parse_catalog_html(self, catalog_element):
        """解析目錄HTML元素"""
        chapters = []
        
        # 尋找所有章節項目
        items = catalog_element.find_all(['div', 'li'], class_=re.compile(r'tree-option|chapter-item'))
        
        for item in items:
            # 提取層級信息
            level_match = re.search(r'level-(\d+)', item.get('class', [''])[0] if item.get('class') else '')
            level = int(level_match.group(1)) if level_match else 1
            
            # 提取鏈接和標題
            link = item.find('a')
            if link:
                href = link.get('href', '')
                title = link.get_text().strip()
                
                chapter_id_match = re.search(r'/chapter/([^/?]+)', href)
                if chapter_id_match:
                    chapter_id = chapter_id_match.group(1)
                    
                    chapters.append({
                        'title': title,
                        'chapter_id': chapter_id,
                        'level': level,
                        'url': urljoin(self.base_url, href),
                        'children': []
                    })
        
        return chapters
    
    def get_missing_chapters(self, all_chapters, existing_files):
        """找出缺失的章節"""
        existing_titles = set()
        
        for file_path in existing_files:
            filename = file_path.stem
            # 移除編號前綴，提取標題
            title_part = re.sub(r'^\d+_', '', filename)
            existing_titles.add(title_part)
        
        missing_chapters = []
        
        def check_chapter(chapter):
            clean_title = re.sub(r'[<>:"/\\|?*]', '_', chapter['title'])
            if clean_title not in existing_titles:
                missing_chapters.append(chapter)
            
            # 檢查子章節
            for child in chapter.get('children', []):
                check_chapter(child)
        
        for chapter in all_chapters:
            check_chapter(chapter)
        
        return missing_chapters
    
    def crawl_chapter_content(self, chapter_info):
        """爬取章節內容"""
        safe_print(f"📖 爬取: {chapter_info['title']} (Level {chapter_info['level']})")
        
        try:
            # 嘗試多種API端點
            api_urls = [
                f"{self.base_url}/api/book/DZ0336/chapter/{chapter_info['chapter_id']}",
                f"{self.base_url}/api/ancientlib/volume/{chapter_info['chapter_id']}/content",
                chapter_info['url']
            ]
            
            for api_url in api_urls:
                safe_print(f"  嘗試: {api_url}")
                content = self._extract_content_from_url(api_url)
                if content and len(content) > 100:  # 確保內容有意義
                    return {
                        'title': chapter_info['title'],
                        'content': content,
                        'chapter_id': chapter_info['chapter_id'],
                        'level': chapter_info['level']
                    }
                time.sleep(1)
            
            safe_print(f"❌ 無法獲取內容: {chapter_info['title']}")
            return None
            
        except Exception as e:
            safe_print(f"❌ 爬取失敗: {e}")
            return None
    
    def _extract_content_from_url(self, url):
        """從URL提取內容"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # 檢查響應類型
            content_type = response.headers.get('content-type', '')
            
            if 'application/json' in content_type:
                # JSON響應
                data = response.json()
                return self._extract_text_from_json(data)
            else:
                # HTML響應
                soup = BeautifulSoup(response.text, 'html.parser')
                return self._extract_text_from_html(soup)
                
        except Exception as e:
            safe_print(f"  ⚠️  提取失敗: {e}")
            return None
    
    def _extract_text_from_json(self, data):
        """從JSON提取文本"""
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
    
    def _extract_text_from_html(self, soup):
        """從HTML提取文本"""
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
                for element in elements[0].find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div']):
                    text = element.get_text().strip()
                    if text and len(text) > 5:
                        content_parts.append(text)
                
                if content_parts:
                    return '\n\n'.join(content_parts)
        
        return None
    
    def save_hierarchical_chapter(self, book_folder, chapter_data, chapter_number):
        """保存層級章節"""
        # 根據層級調整文件名
        level_prefix = "  " * (chapter_data['level'] - 1)  # 縮進表示層級
        clean_title = re.sub(r'[<>:"/\\|?*]', '_', chapter_data['title'])
        
        filename = f"{chapter_number:02d}_{clean_title}.txt"
        file_path = book_folder / "原文" / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# {chapter_data['title']}\n\n")
            f.write(chapter_data['content'])
        
        safe_print(f"✅ 已保存: {filename} (Level {chapter_data['level']})")
        return filename
    
    def fix_hierarchical_structure(self, book_id, book_folder_name):
        """修復層級結構"""
        safe_print(f"🔧 開始修復層級結構: {book_id}")
        safe_print("=" * 60)
        
        # 1. 分析層級結構
        chapter_tree = self.analyze_hierarchical_structure(book_id)
        if not chapter_tree:
            safe_print("❌ 無法獲取章節樹結構")
            return False
        
        safe_print(f"🌳 找到章節樹，共 {len(chapter_tree)} 個頂級章節")
        
        # 打印結構預覽
        def print_tree(chapters, indent=0):
            for chapter in chapters:
                prefix = "  " * indent
                safe_print(f"{prefix}- {chapter['title']} (Level {chapter['level']})")
                if chapter.get('children'):
                    print_tree(chapter['children'], indent + 1)
        
        safe_print("\n📋 章節結構預覽:")
        print_tree(chapter_tree)
        
        # 2. 檢查現有文件
        book_folder = Path(f"../docs/source_texts/{book_folder_name}")
        source_folder = book_folder / "原文"
        
        if not source_folder.exists():
            safe_print(f"❌ 找不到源文件夾: {source_folder}")
            return False
        
        existing_files = list(source_folder.glob("*.txt"))
        safe_print(f"\n📁 現有文件: {len(existing_files)} 個")
        
        # 3. 找出缺失的章節
        missing_chapters = self.get_missing_chapters(chapter_tree, existing_files)
        
        safe_print(f"❌ 缺失章節: {len(missing_chapters)} 個")
        for chapter in missing_chapters:
            level_prefix = "  " * (chapter['level'] - 1)
            safe_print(f"  {level_prefix}- {chapter['title']} (Level {chapter['level']})")
        
        if not missing_chapters:
            safe_print("✅ 沒有缺失的章節")
            return True
        
        # 4. 爬取缺失的章節
        success_count = 0
        for i, chapter in enumerate(missing_chapters, 1):
            safe_print(f"\n📖 處理缺失章節 {i}/{len(missing_chapters)}")
            
            chapter_data = self.crawl_chapter_content(chapter)
            if chapter_data:
                # 確定章節編號
                chapter_number = len(existing_files) + success_count + 1
                
                # 保存章節
                filename = self.save_hierarchical_chapter(book_folder, chapter_data, chapter_number)
                success_count += 1
                
                # 更新README
                self._update_readme_with_hierarchy(book_folder, chapter_data, chapter_number)
            
            time.sleep(2)  # 避免請求過快
        
        safe_print(f"\n🎉 修復完成！成功添加 {success_count}/{len(missing_chapters)} 個章節")
        return success_count > 0
    
    def _update_readme_with_hierarchy(self, book_folder, chapter_data, chapter_number):
        """更新README，包含層級信息"""
        readme_path = book_folder / "README.md"
        if readme_path.exists():
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 根據層級添加縮進
                level_prefix = "  " * (chapter_data['level'] - 1)
                new_line = f"{level_prefix}- {chapter_number:02d}. {chapter_data['title']}"
                
                # 在章節列表中添加新章節
                if "## 章節列表" in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.startswith("## 章節列表"):
                            # 找到列表結束位置
                            j = i + 1
                            while j < len(lines) and (lines[j].startswith('- ') or lines[j].startswith('  ') or lines[j].strip() == ''):
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
    fixer = HierarchicalChapterFixer()
    
    # 修復 太上洞玄灵宝业报因缘经_DZ0336
    book_id = "DZ0336"
    book_folder_name = "太上洞玄灵宝业报因缘经_DZ0336"
    
    success = fixer.fix_hierarchical_structure(book_id, book_folder_name)
    
    if success:
        safe_print("\n🎊 層級結構修復成功！")
        safe_print("💡 建議：檢查新添加的章節內容和層級結構")
    else:
        safe_print("\n❌ 層級結構修復失敗")
        safe_print("💡 建議：檢查網絡連接和調試信息")


if __name__ == "__main__":
    main()