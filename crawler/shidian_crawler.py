#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
十典古籍網專用爬蟲

學習重點：
1. 如何分析特定網站的結構
2. 如何處理動態載入的內容
3. 如何提取特定格式的文本
4. 如何處理複雜的網頁結構
"""

import re
import time
from urllib.parse import urljoin, urlparse
from base_crawler import BaseCrawler

class ShidianCrawler(BaseCrawler):
    """十典古籍網專用爬蟲"""
    
    def __init__(self):
        super().__init__(delay_range=(3, 5))  # 較長延遲避免被封
        self.base_url = "https://www.shidianguji.com"
        
    def analyze_page_structure(self, url):
        """
        分析頁面結構
        
        學習重點：如何分析網頁的DOM結構
        """
        print(f"🔍 分析頁面結構: {url}")
        
        response = self.make_request(url)
        if not response:
            return None
            
        soup = self.parse_html(response.text)
        
        # 分析頁面的主要元素
        analysis = {
            'title': None,
            'content_containers': [],
            'text_elements': [],
            'scripts': [],
            'meta_info': {}
        }
        
        # 提取標題
        title_selectors = ['title', 'h1', 'h2', '.title', '#title']
        for selector in title_selectors:
            elements = soup.select(selector)
            if elements:
                analysis['title'] = elements[0].get_text().strip()
                break
                
        # 尋找可能的內容容器
        content_selectors = [
            '.content', '.article', '.text', '.chapter',
            '#content', '#article', '#text', '#chapter',
            '[class*="content"]', '[class*="text"]', '[class*="chapter"]'
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                for elem in elements:
                    text = elem.get_text().strip()
                    if len(text) > 50:  # 只記錄有意義的內容
                        analysis['content_containers'].append({
                            'selector': selector,
                            'text_length': len(text),
                            'text_preview': text[:100] + '...' if len(text) > 100 else text
                        })
        
        # 檢查是否有JavaScript動態載入
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and ('ajax' in script.string.lower() or 'fetch' in script.string.lower()):
                analysis['scripts'].append('可能有動態載入')
                
        return analysis
        
    def extract_shidian_content(self, url):
        """
        提取十典古籍網的內容
        
        學習重點：針對特定網站的內容提取策略
        """
        print(f"📖 開始提取內容: {url}")
        
        response = self.make_request(url)
        if not response:
            return None
            
        soup = self.parse_html(response.text)
        
        # 十典古籍網的特定選擇器（需要根據實際頁面調整）
        content_selectors = [
            '.chapter-content',
            '.book-content', 
            '.text-content',
            '#chapter-text',
            '.content-text',
            'article',
            '.main-content'
        ]
        
        content = ""
        
        # 嘗試不同的選擇器
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                for elem in elements:
                    text = elem.get_text()
                    if len(text) > content.__len__():
                        content = text
                        print(f"✅ 找到內容 (選擇器: {selector}, 長度: {len(text)})")
                        
        # 如果沒找到特定容器，嘗試提取所有段落
        if len(content) < 100:
            paragraphs = soup.find_all(['p', 'div'])
            all_text = []
            for p in paragraphs:
                text = p.get_text().strip()
                if len(text) > 20 and not any(skip in text.lower() for skip in ['copyright', '版權', '導航', 'nav']):
                    all_text.append(text)
            content = '\n'.join(all_text)
            print(f"📝 提取段落內容，總長度: {len(content)}")
            
        return self.clean_text(content) if content else None
        
    def get_book_info(self, url):
        """
        提取書籍資訊
        
        學習重點：如何從URL和頁面提取結構化資訊
        """
        # 從URL分析書籍資訊
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.split('/')
        
        book_info = {
            'book_id': None,
            'chapter_id': None,
            'title': None,
            'chapter_title': None
        }
        
        # 分析URL結構
        for i, part in enumerate(path_parts):
            if part.startswith('SBCK'):
                book_info['book_id'] = part
            elif 'chapter' in parsed_url.path and i < len(path_parts) - 1:
                book_info['chapter_id'] = path_parts[i + 1]
                
        return book_info
        
    def crawl_shidian_page(self, url, custom_title=None):
        """
        爬取十典古籍網的單一頁面
        
        Args:
            url: 目標網址
            custom_title: 自定義標題
            
        Returns:
            是否成功爬取
        """
        print(f"🕷️ 開始爬取十典古籍頁面")
        print(f"網址: {url}")
        print("-" * 50)
        
        # 先分析頁面結構
        analysis = self.analyze_page_structure(url)
        if analysis:
            print("📊 頁面分析結果:")
            print(f"標題: {analysis['title']}")
            print(f"找到 {len(analysis['content_containers'])} 個內容容器")
            for container in analysis['content_containers'][:3]:  # 只顯示前3個
                print(f"  - {container['selector']}: {container['text_length']} 字符")
                print(f"    預覽: {container['text_preview']}")
            print()
        
        # 提取內容
        content = self.extract_shidian_content(url)
        
        if not content or len(content) < 100:
            print("❌ 未能提取到有效內容")
            return False
            
        # 確定標題
        if custom_title:
            title = custom_title
        elif analysis and analysis['title']:
            title = analysis['title']
        else:
            book_info = self.get_book_info(url)
            title = f"{book_info['book_id']}_{book_info['chapter_id']}" if book_info['book_id'] else "十典古籍_未知"
            
        # 儲存內容
        filename = f"{title}.txt"
        self.save_text(content, filename, "../docs/source_texts")
        
        print(f"✅ 成功爬取: {title}")
        print(f"內容長度: {len(content)} 字符")
        print(f"已儲存為: {filename}")
        
        return True

# 示例使用
if __name__ == "__main__":
    crawler = ShidianCrawler()
    
    # 測試網址
    test_url = "https://www.shidianguji.com/book/SBCK109/chapter/1j70ybwytkcak_1?page_from=home_page&version=19"
    
    success = crawler.crawl_shidian_page(test_url, "道德經_第一章_十典古籍版")
    
    if success:
        print("\n🎉 爬取成功！")
    else:
        print("\n❌ 爬取失敗，可能需要調整策略")