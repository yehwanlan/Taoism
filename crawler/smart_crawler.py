#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能爬蟲 - 針對十典古籍網的優化版本

學習重點：
1. 如何分析網頁的實際HTML結構
2. 如何找到隱藏在複雜結構中的內容
3. 如何處理特殊的網站架構
4. 如何提取純文本內容
"""

import re
import json
from base_crawler import BaseCrawler

class SmartCrawler(BaseCrawler):
    """智能爬蟲"""
    
    def __init__(self):
        super().__init__(delay_range=(2, 4))
        
    def extract_raw_html(self, url):
        """提取原始HTML並分析"""
        print(f"🔍 提取原始HTML: {url}")
        
        response = self.make_request(url)
        if not response:
            return None
            
        # 儲存原始HTML以供分析
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("💾 原始HTML已儲存為 debug_page.html")
        
        return response.text
        
    def find_content_in_html(self, html_content):
        """在HTML中尋找實際內容"""
        print("🔎 在HTML中搜尋內容...")
        
        soup = self.parse_html(html_content)
        
        # 方法1: 尋找所有文本節點
        all_text = soup.get_text()
        print(f"總文本長度: {len(all_text)} 字符")
        
        # 方法2: 尋找包含中文的長段落
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
        paragraphs = []
        
        for element in soup.find_all(['p', 'div', 'span', 'td']):
            text = element.get_text().strip()
            if len(text) > 30 and chinese_pattern.search(text):
                paragraphs.append({
                    'text': text,
                    'length': len(text),
                    'tag': element.name,
                    'class': element.get('class', []),
                    'id': element.get('id', '')
                })
        
        # 按長度排序
        paragraphs.sort(key=lambda x: x['length'], reverse=True)
        
        print(f"找到 {len(paragraphs)} 個中文段落")
        
        # 顯示最長的幾個段落
        for i, para in enumerate(paragraphs[:5]):
            print(f"段落 {i+1}: {para['length']} 字符")
            print(f"  標籤: {para['tag']}")
            if para['class']:
                print(f"  類別: {' '.join(para['class'])}")
            if para['id']:
                print(f"  ID: {para['id']}")
            print(f"  預覽: {para['text'][:100]}...")
            print()
            
        return paragraphs
        
    def extract_book_content(self, paragraphs):
        """從段落中提取書籍內容"""
        print("📖 提取書籍內容...")
        
        # 過濾掉導航、版權等無關內容
        filter_keywords = [
            '版權', '導航', '菜單', '登錄', '註冊', '搜索', 
            '首頁', '關於', '聯繫', '友情鏈接', 'copyright',
            '网站', '平台', '服务', '用户', '隐私', '条款'
        ]
        
        content_paragraphs = []
        for para in paragraphs:
            text = para['text']
            # 檢查是否包含過濾關鍵字
            if not any(keyword in text for keyword in filter_keywords):
                # 檢查是否是實際的書籍內容（包含古文特徵）
                if self.is_classical_text(text):
                    content_paragraphs.append(para)
                    
        print(f"過濾後剩餘 {len(content_paragraphs)} 個內容段落")
        
        if content_paragraphs:
            # 合併內容
            final_content = '\n\n'.join([para['text'] for para in content_paragraphs])
            return self.clean_text(final_content)
        
        return None
        
    def is_classical_text(self, text):
        """判斷是否為古典文本"""
        # 古文特徵檢查
        classical_indicators = [
            '之', '者', '也', '矣', '焉', '乎', '哉', '耳',
            '曰', '云', '謂', '故', '是以', '然則', '夫',
            '蓋', '且', '若', '則', '而', '以', '於'
        ]
        
        # 計算古文指標出現次數
        indicator_count = sum(1 for indicator in classical_indicators if indicator in text)
        
        # 如果古文指標足夠多，且文本長度合理，則認為是古典文本
        return indicator_count >= 3 and len(text) > 50
        
    def crawl_shidian_smart(self, url, title=None):
        """智能爬取十典古籍"""
        print(f"🧠 智能爬取開始")
        print(f"網址: {url}")
        print("=" * 50)
        
        # 1. 提取原始HTML
        html_content = self.extract_raw_html(url)
        if not html_content:
            return False
            
        # 2. 分析HTML結構
        paragraphs = self.find_content_in_html(html_content)
        if not paragraphs:
            return False
            
        # 3. 提取書籍內容
        content = self.extract_book_content(paragraphs)
        if not content:
            print("❌ 未能提取到有效的書籍內容")
            return False
            
        # 4. 確定標題
        if not title:
            soup = self.parse_html(html_content)
            page_title = soup.find('title')
            if page_title:
                title = page_title.get_text().split('-')[0].strip()
            else:
                title = "十典古籍_智能爬取"
                
        # 5. 儲存內容
        filename = f"{title}.txt"
        self.save_text(content, filename, "../docs/source_texts")
        
        print(f"✅ 智能爬取成功: {title}")
        print(f"內容長度: {len(content)} 字符")
        print(f"已儲存為: {filename}")
        
        return True

# 使用示例
def test_smart_crawler():
    """測試智能爬蟲"""
    crawler = SmartCrawler()
    
    url = "https://www.shidianguji.com/book/DZ0095/chapter/DZ0095_1?page_from=bookshelf&version=2"
    
    success = crawler.crawl_shidian_smart(url, "DZ0095_智能爬取")
    
    if success:
        print("\n🎉 智能爬取完成！")
        print("💡 提示：檢查 debug_page.html 可以看到完整的網頁結構")
    else:
        print("\n❌ 智能爬取失敗")

if __name__ == "__main__":
    test_smart_crawler()