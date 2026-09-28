#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API爬蟲 - 針對動態載入內容的解決方案

學習重點：
1. 如何分析網站的API請求
2. 如何直接調用API獲取數據
3. 如何處理JSON格式的回應
4. 如何繞過前端限制直接獲取內容
"""

import json
import re
from urllib.parse import urljoin, urlparse, parse_qs
from base_crawler import BaseCrawler
from core.unicode_handler import safe_print

class APICrawler(BaseCrawler):
    """API爬蟲"""
    
    def __init__(self):
        super().__init__(delay_range=(2, 4))
        self.base_url = "https://www.shidianguji.com"
        
    def analyze_url_structure(self, url):
        """分析URL結構以推測API端點"""
        safe_print(f"🔍 分析URL結構: {url}")
        
        parsed = urlparse(url)
        path_parts = parsed.path.split('/')
        query_params = parse_qs(parsed.query)
        
        analysis = {
            'domain': parsed.netloc,
            'path_parts': path_parts,
            'query_params': query_params,
            'book_id': None,
            'chapter_id': None
        }
        
        # 從URL中提取書籍和章節ID
        for part in path_parts:
            if part.startswith('SBCK'):
                analysis['book_id'] = part
            elif len(part) > 10 and '_' in part:
                analysis['chapter_id'] = part
                
        safe_print(f"書籍ID: {analysis['book_id']}")
        safe_print(f"章節ID: {analysis['chapter_id']}")
        
        return analysis
        
    def try_api_endpoints(self, book_id, chapter_id):
        """嘗試常見的API端點"""
        safe_print(f"🔌 嘗試API端點...")
        
        # 常見的API端點模式
        api_patterns = [
            f"/api/ancientlib/book/{book_id}/chapter/{chapter_id}",
            f"/api/book/{book_id}/chapter/{chapter_id}",
            f"/api/chapter/{chapter_id}",
            f"/api/content/{book_id}/{chapter_id}",
            f"/api/ancientlib/chapter/{chapter_id}",
            f"/api/v1/book/{book_id}/chapter/{chapter_id}",
        ]
        
        successful_responses = []
        
        for pattern in api_patterns:
            api_url = urljoin(self.base_url, pattern)
            safe_print(f"嘗試: {api_url}")
            
            response = self.make_request(api_url)
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    if data and isinstance(data, dict):
                        safe_print(f"✅ 成功: {api_url}")
                        successful_responses.append({
                            'url': api_url,
                            'data': data
                        })
                except:
                    # 可能是HTML或其他格式
                    if len(response.text) > 100:
                        safe_print(f"✅ 成功 (非JSON): {api_url}")
                        successful_responses.append({
                            'url': api_url,
                            'data': response.text
                        })
            else:
                safe_print(f"❌ 失敗: {api_url}")
                
        return successful_responses
        
    def extract_content_from_api_response(self, api_data):
        """從API回應中提取內容"""
        safe_print("📖 從API回應中提取內容...")
        
        if isinstance(api_data, dict):
            # 常見的內容字段名
            content_fields = [
                'content', 'text', 'body', 'data', 
                'chapter_content', 'book_content',
                'original_text', 'content_text'
            ]
            
            for field in content_fields:
                if field in api_data:
                    content = api_data[field]
                    if isinstance(content, str) and len(content) > 50:
                        safe_print(f"✅ 找到內容字段: {field}")
                        return content
                        
            # 如果沒有直接的內容字段，嘗試遞歸搜尋
            def find_content_recursive(obj, depth=0):
                if depth > 3:  # 避免無限遞歸
                    return None
                    
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if isinstance(value, str) and len(value) > 100:
                            # 檢查是否包含中文
                            if re.search(r'[\u4e00-\u9fff]', value):
                                return value
                        elif isinstance(value, (dict, list)):
                            result = find_content_recursive(value, depth + 1)
                            if result:
                                return result
                elif isinstance(obj, list):
                    for item in obj:
                        result = find_content_recursive(item, depth + 1)
                        if result:
                            return result
                return None
                
            recursive_content = find_content_recursive(api_data)
            if recursive_content:
                safe_print("✅ 通過遞歸搜尋找到內容")
                return recursive_content
                
        elif isinstance(api_data, str):
            # 直接是字符串內容
            if len(api_data) > 50 and re.search(r'[\u4e00-\u9fff]', api_data):
                safe_print("✅ 直接字符串內容")
                return api_data
                
        safe_print("❌ 未能從API回應中提取內容")
        return None
        
    def crawl_via_api(self, url, title=None):
        """通過API爬取內容"""
        safe_print(f"🌐 通過API爬取內容")
        safe_print(f"網址: {url}")
        safe_print("=" * 50)
        
        # 1. 分析URL結構
        analysis = self.analyze_url_structure(url)
        
        if not analysis['book_id'] or not analysis['chapter_id']:
            safe_print("❌ 無法從URL中提取書籍或章節ID")
            return False
            
        # 2. 嘗試API端點
        api_responses = self.try_api_endpoints(
            analysis['book_id'], 
            analysis['chapter_id']
        )
        
        if not api_responses:
            safe_print("❌ 沒有找到有效的API端點")
            return False
            
        # 3. 從API回應中提取內容
        content = None
        for response in api_responses:
            content = self.extract_content_from_api_response(response['data'])
            if content:
                safe_print(f"✅ 從 {response['url']} 獲取到內容")
                break
                
        if not content:
            safe_print("❌ 無法從API回應中提取內容")
            # 儲存API回應以供調試
            with open("api_debug.json", "w", encoding="utf-8") as f:
                json.dump(api_responses, f, ensure_ascii=False, indent=2)
            safe_print("💾 API回應已儲存為 api_debug.json")
            return False
            
        # 4. 清理和儲存內容
        # 使用父類的clean_text方法
        import re
        # 移除多餘的空白字符
        content = re.sub(r'\s+', ' ', content)
        # 移除HTML標籤殘留
        content = re.sub(r'<[^>]+>', '', content)
        # 整理段落
        content = re.sub(r'\n\s*\n', '\n\n', content)
        cleaned_content = content.strip()
        
        if not title:
            title = f"{analysis['book_id']}_{analysis['chapter_id']}_API爬取"
            
        filename = f"{title}.txt"
        self.save_text(cleaned_content, filename, "../docs/source_texts")
        
        safe_print(f"✅ API爬取成功: {title}")
        safe_print(f"內容長度: {len(cleaned_content)} 字符")
        
        return True

# 使用示例
def test_api_crawler():
    """測試API爬蟲"""
    crawler = APICrawler()
    
    url = "https://www.shidianguji.com/book/SBCK109/chapter/1j70ybwytkcak_1?page_from=home_page&version=19"
    
    success = crawler.crawl_via_api(url, "抱朴子_內篇_API爬取")
    
    if success:
        safe_print("\n🎉 API爬取完成！")
    else:
        safe_print("\n❌ API爬取失敗")
        safe_print("💡 提示：檢查 api_debug.json 可以看到API回應內容")

if __name__ == "__main__":
    test_api_crawler()
