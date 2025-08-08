#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終解決方案 - 十典古籍爬蟲

學習重點：
1. 如何從複雜的API回應中提取有用資訊
2. 如何處理嵌套的JSON數據結構
3. 如何建立完整的爬蟲解決方案
4. 如何整合多種爬蟲技術
"""

import json
import re
from urllib.parse import urljoin
from base_crawler import BaseCrawler

class FinalSolution(BaseCrawler):
    """最終解決方案爬蟲"""
    
    def __init__(self):
        super().__init__(delay_range=(2, 4))
        self.base_url = "https://www.shidianguji.com"
        
    def extract_book_info_from_api(self, url):
        """從API中提取書籍資訊"""
        print(f"📚 從API提取書籍資訊: {url}")
        
        response = self.make_request(url)
        if not response:
            return None
            
        # 嘗試從回應中提取JSON數據
        text = response.text
        
        # 尋找 window._ROUTER_DATA 或類似的數據
        patterns = [
            r'window\._ROUTER_DATA\s*=\s*({.*?});',
            r'window\._SSR_DATA\s*=\s*({.*?});',
            r'"bookInfo":\s*({.*?})',
            r'"chapterInfo":\s*({.*?})',
        ]
        
        for pattern in patterns:
            matches = re.search(pattern, text, re.DOTALL)
            if matches:
                try:
                    data = json.loads(matches.group(1))
                    print(f"✅ 找到數據結構: {pattern}")
                    return data
                except json.JSONDecodeError:
                    continue
                    
        return None
        
    def find_content_api_from_book_info(self, book_info, chapter_id):
        """從書籍資訊中找到內容API"""
        print(f"🔍 從書籍資訊中尋找內容API...")
        
        if not book_info:
            return None
            
        # 遞歸搜尋章節資訊
        def find_chapter_info(obj, target_id):
            if isinstance(obj, dict):
                if obj.get('chapterId') == target_id:
                    return obj
                for value in obj.values():
                    result = find_chapter_info(value, target_id)
                    if result:
                        return result
            elif isinstance(obj, list):
                for item in obj:
                    result = find_chapter_info(item, target_id)
                    if result:
                        return result
            return None
            
        chapter_info = find_chapter_info(book_info, chapter_id)
        
        if chapter_info:
            print(f"✅ 找到章節資訊: {chapter_info.get('chapterName', 'Unknown')}")
            
            # 嘗試構建內容API URL
            volume_id = chapter_info.get('volumeId')
            if volume_id:
                content_api = f"/api/ancientlib/volume/{volume_id}/content"
                return content_api
                
        return None
        
    def get_chapter_content(self, content_api_url):
        """獲取章節內容"""
        print(f"📖 獲取章節內容: {content_api_url}")
        
        full_url = urljoin(self.base_url, content_api_url)
        response = self.make_request(full_url)
        
        if not response:
            return None
            
        try:
            data = response.json()
            
            # 從JSON中提取文本內容
            content_parts = []
            
            def extract_text_recursive(obj):
                if isinstance(obj, dict):
                    # 尋找包含文本的字段
                    if 'content' in obj and isinstance(obj['content'], str):
                        text = obj['content'].strip()
                        if len(text) > 10 and re.search(r'[\u4e00-\u9fff]', text):
                            content_parts.append(text)
                    
                    for value in obj.values():
                        extract_text_recursive(value)
                        
                elif isinstance(obj, list):
                    for item in obj:
                        extract_text_recursive(item)
                        
            extract_text_recursive(data)
            
            if content_parts:
                final_content = '\n\n'.join(content_parts)
                print(f"✅ 提取到內容，總長度: {len(final_content)} 字符")
                return final_content
            else:
                print("❌ 未能從JSON中提取文本內容")
                # 儲存原始數據以供調試
                with open("content_debug.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print("💾 原始數據已儲存為 content_debug.json")
                return None
                
        except json.JSONDecodeError:
            print("❌ API回應不是有效的JSON")
            return None
            
    def crawl_shidian_final(self, url, title=None):
        """最終爬取方案"""
        print(f"🎯 最終爬取方案")
        print(f"網址: {url}")
        print("=" * 60)
        
        # 1. 從URL提取ID
        import re
        book_match = re.search(r'/book/([^/]+)', url)
        chapter_match = re.search(r'/chapter/([^/?]+)', url)
        
        if not book_match or not chapter_match:
            print("❌ 無法從URL中提取書籍或章節ID")
            return False
            
        book_id = book_match.group(1)
        chapter_id = chapter_match.group(1)
        
        print(f"書籍ID: {book_id}")
        print(f"章節ID: {chapter_id}")
        
        # 2. 獲取書籍資訊
        book_api = f"/api/book/{book_id}/chapter/{chapter_id}"
        book_info = self.extract_book_info_from_api(urljoin(self.base_url, book_api))
        
        if not book_info:
            print("❌ 無法獲取書籍資訊")
            return False
            
        # 3. 尋找內容API
        content_api = self.find_content_api_from_book_info(book_info, chapter_id)
        
        if not content_api:
            print("❌ 無法找到內容API")
            return False
            
        # 4. 獲取實際內容
        content = self.get_chapter_content(content_api)
        
        if not content:
            print("❌ 無法獲取章節內容")
            return False
            
        # 5. 清理和儲存內容
        cleaned_content = self.clean_content(content)
        
        if not title:
            title = f"{book_id}_{chapter_id}_最終版本"
            
        filename = f"{title}.txt"
        self.save_text(cleaned_content, filename, "../docs/source_texts")
        
        print(f"✅ 最終爬取成功: {title}")
        print(f"內容長度: {len(cleaned_content)} 字符")
        
        return True
        
    def clean_content(self, content):
        """清理內容"""
        # 移除多餘的空白
        content = re.sub(r'\s+', ' ', content)
        # 移除HTML標籤
        content = re.sub(r'<[^>]+>', '', content)
        # 整理段落
        content = re.sub(r'\n\s*\n', '\n\n', content)
        return content.strip()

# 使用示例
def test_final_solution():
    """測試最終解決方案"""
    crawler = FinalSolution()
    
    url = "https://www.shidianguji.com/book/SBCK109/chapter/1j70ybwytkcak_1?page_from=home_page&version=19"
    
    success = crawler.crawl_shidian_final(url, "抱朴子_內篇_最終版本")
    
    if success:
        print("\n🎉 最終爬取完成！")
        print("🔧 現在您已經掌握了完整的爬蟲技術棧：")
        print("   1. 基礎HTTP爬蟲")
        print("   2. API逆向工程")
        print("   3. JSON數據解析")
        print("   4. 動態內容處理")
    else:
        print("\n❌ 最終爬取失敗")
        print("💡 檢查調試文件以了解更多資訊")

if __name__ == "__main__":
    test_final_solution()