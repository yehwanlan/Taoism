#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
網頁深度分析工具

學習重點：
1. 如何詳細分析網頁結構
2. 如何識別動態載入內容
3. 如何找到隱藏的內容選擇器
4. 如何處理複雜的網站架構
"""

import json
from base_crawler import BaseCrawler
from core.unicode_handler import safe_print

class PageAnalyzer(BaseCrawler):
    """網頁深度分析工具"""
    
    def __init__(self):
        super().__init__()
        
    def deep_analyze(self, url):
        """深度分析網頁結構"""
        safe_print(f"🔬 深度分析網頁: {url}")
        safe_print("=" * 60)
        
        response = self.make_request(url)
        if not response:
            return None
            
        soup = self.parse_html(response.text)
        
        # 1. 基本資訊
        safe_print("📋 基本資訊:")
        safe_print(f"狀態碼: {response.status_code}")
        safe_print(f"內容類型: {response.headers.get('content-type', 'unknown')}")
        safe_print(f"頁面大小: {len(response.text)} 字符")
        safe_print()
        
        # 2. 標題分析
        safe_print("📝 標題分析:")
        title = soup.find('title')
        if title:
            safe_print(f"頁面標題: {title.get_text().strip()}")
        
        for i in range(1, 7):
            headers = soup.find_all(f'h{i}')
            if headers:
                safe_print(f"H{i} 標題 ({len(headers)}個):")
                for h in headers[:3]:  # 只顯示前3個
                    safe_print(f"  - {h.get_text().strip()}")
        safe_print()
        
        # 3. 內容容器分析
        safe_print("📦 內容容器分析:")
        containers = [
            ('div', 'DIV元素'),
            ('article', 'ARTICLE元素'),
            ('section', 'SECTION元素'),
            ('main', 'MAIN元素'),
            ('p', '段落元素')
        ]
        
        for tag, desc in containers:
            elements = soup.find_all(tag)
            if elements:
                safe_print(f"{desc}: {len(elements)}個")
                # 找出最長的內容
                longest = max(elements, key=lambda x: len(x.get_text()))
                text = longest.get_text().strip()
                if len(text) > 50:
                    safe_print(f"  最長內容: {len(text)} 字符")
                    safe_print(f"  預覽: {text[:100]}...")
                    # 顯示這個元素的class和id
                    if longest.get('class'):
                        safe_print(f"  Class: {' '.join(longest.get('class'))}")
                    if longest.get('id'):
                        safe_print(f"  ID: {longest.get('id')}")
        safe_print()
        
        # 4. JavaScript分析
        safe_print("🔧 JavaScript分析:")
        scripts = soup.find_all('script')
        safe_print(f"腳本數量: {len(scripts)}")
        
        js_keywords = ['ajax', 'fetch', 'xhr', 'load', 'content', 'text']
        for script in scripts:
            if script.string:
                script_text = script.string.lower()
                found_keywords = [kw for kw in js_keywords if kw in script_text]
                if found_keywords:
                    safe_print(f"  發現關鍵字: {', '.join(found_keywords)}")
                    if 'src' in script.attrs:
                        safe_print(f"  外部腳本: {script['src']}")
        safe_print()
        
        # 5. CSS類別分析
        safe_print("🎨 CSS類別分析:")
        all_classes = set()
        for elem in soup.find_all(class_=True):
            all_classes.update(elem.get('class'))
        
        # 尋找可能的內容相關類別
        content_related = [cls for cls in all_classes if any(
            keyword in cls.lower() for keyword in 
            ['content', 'text', 'article', 'chapter', 'book', 'page']
        )]
        
        if content_related:
            safe_print("可能的內容相關類別:")
            for cls in sorted(content_related)[:10]:  # 只顯示前10個
                elements = soup.find_all(class_=cls)
                if elements:
                    max_text_len = max(len(elem.get_text()) for elem in elements)
                    safe_print(f"  .{cls}: {len(elements)}個元素, 最大內容長度: {max_text_len}")
        safe_print()
        
        # 6. 表單分析
        safe_print("📋 表單分析:")
        forms = soup.find_all('form')
        if forms:
            safe_print(f"表單數量: {len(forms)}")
            for i, form in enumerate(forms):
                action = form.get('action', '無')
                method = form.get('method', 'GET')
                safe_print(f"  表單{i+1}: {method} -> {action}")
        else:
            safe_print("未發現表單")
        safe_print()
        
        # 7. 特殊元素分析
        safe_print("🔍 特殊元素分析:")
        
        # iframe嵌入
        iframes = soup.find_all('iframe')
        if iframes:
            safe_print(f"iframe嵌入: {len(iframes)}個")
            
        # 數據屬性元素
        data_elements = soup.find_all(attrs=lambda x: x and any(k.startswith('data-') for k in x.keys()))
        if data_elements:
            safe_print(f"數據屬性元素: {len(data_elements)}個")
            
        # 懶載入元素
        lazy_elements = soup.find_all(class_='lazy')
        if lazy_elements:
            safe_print(f"懶載入元素: {len(lazy_elements)}個")
            
        # 隱藏元素
        hidden_elements = soup.find_all(attrs={'style': lambda x: x and 'display:none' in x})
        if hidden_elements:
            safe_print(f"隱藏元素: {len(hidden_elements)}個")
        
        return {
            'url': url,
            'status_code': response.status_code,
            'content_length': len(response.text),
            'title': title.get_text().strip() if title else None,
            'content_classes': content_related,
            'script_count': len(scripts)
        }

def analyze_shidian_page():
    """分析十典古籍頁面"""
    analyzer = PageAnalyzer()
    
    url = "https://www.shidianguji.com/book/SBCK109/chapter/1j70ybwytkcak_1?page_from=home_page&version=19"
    
    result = analyzer.deep_analyze(url)
    
    safe_print("🎯 分析建議:")
    safe_print("1. 檢查是否有動態載入的內容")
    safe_print("2. 嘗試不同的內容選擇器")
    safe_print("3. 可能需要模擬瀏覽器行為")
    safe_print("4. 檢查是否需要特殊的請求標頭")

if __name__ == "__main__":
    analyze_shidian_page()