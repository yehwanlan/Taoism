#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
丹陽真人直言 API 爬蟲
直接調用師典古籍的 API 獲取內容
"""

import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

# 添加路徑
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent))

from base_crawler import BaseCrawler

def safe_print(*args, **kwargs):
    """安全打印"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # 移除 emoji 和特殊字符
        import re
        safe_args = []
        for arg in args:
            text = str(arg)
            # 移除 emoji
            text = re.sub(r'[^\u0000-\uFFFF]', '', text)
            safe_args.append(text)
        try:
            print(*safe_args, **kwargs)
        except:
            # 最後手段：只保留 ASCII 和基本中文
            ascii_args = [str(arg).encode('ascii', errors='ignore').decode('ascii') for arg in args]
            print(*ascii_args, **kwargs)

class DanyangAPICrawler(BaseCrawler):
    """丹陽真人直言 API 爬蟲"""
    
    def __init__(self):
        super().__init__(delay_range=(2, 4))
        self.base_url = "https://www.shidianguji.com"
        
    def extract_ids_from_url(self, url):
        """從 URL 提取書籍和章節 ID"""
        book_match = re.search(r'/book/([^/]+)', url)
        chapter_match = re.search(r'/chapter/([^/?]+)', url)
        
        book_id = book_match.group(1) if book_match else None
        chapter_id = chapter_match.group(1) if chapter_match else None
        
        return book_id, chapter_id
    
    def try_api_endpoints(self, book_id, chapter_id):
        """嘗試各種可能的 API 端點"""
        safe_print(f"🔌 嘗試 API 端點...")
        safe_print(f"   書籍ID: {book_id}")
        safe_print(f"   章節ID: {chapter_id}")
        safe_print()
        
        # 可能的 API 端點
        api_patterns = [
            f"/api/book/{book_id}",
            f"/api/book/{book_id}/chapters",
            f"/api/book/{book_id}/chapter/{chapter_id}",
            f"/api/chapter/{chapter_id}",
            f"/api/ancientlib/book/{book_id}",
            f"/api/ancientlib/book/{book_id}/chapter/{chapter_id}",
            f"/api/ancientlib/chapter/{chapter_id}",
            f"/api/ancientlib/volume/{chapter_id}/content",
        ]
        
        results = []
        
        for i, pattern in enumerate(api_patterns, 1):
            api_url = urljoin(self.base_url, pattern)
            safe_print(f"[{i}/{len(api_patterns)}] 嘗試: {pattern}")
            
            response = self.make_request(api_url)
            
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    if data:
                        safe_print(f"     ✅ 成功！獲得 JSON 數據")
                        results.append({
                            'url': api_url,
                            'pattern': pattern,
                            'data': data,
                            'type': 'json'
                        })
                        
                        # 顯示數據結構預覽
                        if isinstance(data, dict):
                            keys = list(data.keys())[:5]
                            safe_print(f"     📊 數據鍵: {keys}")
                        
                except json.JSONDecodeError:
                    if len(response.text) > 100:
                        safe_print(f"     ⚠️  成功但非 JSON")
                        
                        # 保存 HTML 用於調試
                        debug_file = Path(f"debug_api_{i}_html.html")
                        with open(debug_file, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        safe_print(f"     已保存: {debug_file}")
                        
                        results.append({
                            'url': api_url,
                            'pattern': pattern,
                            'data': response.text,
                            'type': 'text'
                        })
            else:
                status = response.status_code if response else 'No Response'
                safe_print(f"     ❌ 失敗 (狀態: {status})")
            
            self.delay()
        
        safe_print()
        safe_print(f"📊 總共找到 {len(results)} 個有效端點")
        return results
    
    def extract_content_from_json(self, data, depth=0, max_depth=5):
        """從 JSON 數據中遞歸提取內容"""
        if depth > max_depth:
            return []
        
        contents = []
        
        if isinstance(data, dict):
            # 檢查常見的內容字段
            content_fields = ['content', 'text', 'body', 'data', 'chapterContent', 
                            'originalText', 'contentText', 'fullText']
            
            for field in content_fields:
                if field in data:
                    value = data[field]
                    if isinstance(value, str) and len(value) > 50:
                        # 檢查是否包含中文
                        if re.search(r'[\u4e00-\u9fff]', value):
                            contents.append({
                                'field': field,
                                'content': value,
                                'length': len(value)
                            })
            
            # 遞歸搜索
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    contents.extend(self.extract_content_from_json(value, depth + 1, max_depth))
        
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    contents.extend(self.extract_content_from_json(item, depth + 1, max_depth))
                elif isinstance(item, str) and len(item) > 50:
                    if re.search(r'[\u4e00-\u9fff]', item):
                        contents.append({
                            'field': 'list_item',
                            'content': item,
                            'length': len(item)
                        })
        
        return contents
    
    def crawl_danyang(self, url):
        """爬取丹陽真人直言"""
        safe_print("=" * 80)
        safe_print("🎯 丹陽真人直言 API 爬蟲")
        safe_print("=" * 80)
        safe_print(f"🌐 目標 URL: {url}")
        safe_print()
        
        # 1. 提取 ID
        book_id, chapter_id = self.extract_ids_from_url(url)
        
        if not book_id or not chapter_id:
            safe_print("❌ 無法從 URL 提取 ID")
            return False
        
        # 2. 嘗試 API 端點
        api_results = self.try_api_endpoints(book_id, chapter_id)
        
        if not api_results:
            safe_print("❌ 沒有找到有效的 API 端點")
            return False
        
        # 3. 從每個結果中提取內容
        safe_print("📖 開始提取內容...")
        safe_print()
        
        all_contents = []
        
        for i, result in enumerate(api_results, 1):
            safe_print(f"[{i}/{len(api_results)}] 分析: {result['pattern']}")
            
            if result['type'] == 'json':
                contents = self.extract_content_from_json(result['data'])
                
                if contents:
                    safe_print(f"     ✅ 找到 {len(contents)} 個內容片段")
                    for content in contents:
                        safe_print(f"        - {content['field']}: {content['length']} 字符")
                        all_contents.append(content)
                else:
                    safe_print(f"     ⚠️  未找到內容")
                    
                    # 保存 JSON 用於調試
                    debug_file = Path("crawler") / f"debug_api_{i}.json"
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        json.dump(result['data'], f, ensure_ascii=False, indent=2)
                    safe_print(f"     💾 已保存調試文件: {debug_file}")
            
            safe_print()
        
        # 4. 選擇最佳內容
        if not all_contents:
            safe_print("❌ 未能從任何 API 提取到內容")
            safe_print("💡 請檢查 debug_api_*.json 文件查看原始數據")
            return False
        
        # 按長度排序，選擇最長的
        all_contents.sort(key=lambda x: x['length'], reverse=True)
        best_content = all_contents[0]
        
        safe_print("=" * 80)
        safe_print("📊 內容提取結果")
        safe_print("=" * 80)
        safe_print(f"✅ 最佳內容來源: {best_content['field']}")
        safe_print(f"📏 內容長度: {best_content['length']} 字符")
        safe_print()
        
        # 顯示預覽
        preview = best_content['content'][:200]
        safe_print("📝 內容預覽:")
        safe_print("-" * 80)
        safe_print(preview + "...")
        safe_print("-" * 80)
        safe_print()
        
        # 5. 保存內容
        filename = f"丹陽真人直言_{book_id}_API版.txt"
        save_dir = Path("docs/source_texts")
        save_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = save_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(best_content['content'])
        
        safe_print(f"✅ 已保存: {file_path}")
        safe_print(f"📊 文件大小: {file_path.stat().st_size} 字節")
        safe_print()
        
        return True

def main():
    """主函數"""
    target_url = "https://www.shidianguji.com/book/DZ1234/chapter/start?page_from=bookshelf&mode=book"
    
    crawler = DanyangAPICrawler()
    success = crawler.crawl_danyang(target_url)
    
    safe_print("=" * 80)
    if success:
        safe_print("🎉 API 爬取成功！")
        safe_print("📁 檔案已保存到 docs/source_texts/ 目錄")
    else:
        safe_print("❌ API 爬取失敗")
        safe_print("💡 可能原因:")
        safe_print("   1. API 端點已變更")
        safe_print("   2. 需要登錄才能訪問 API")
        safe_print("   3. 內容結構與預期不同")
        safe_print()
        safe_print("🔧 請檢查 debug_api_*.json 文件了解詳情")
    safe_print("=" * 80)

if __name__ == "__main__":
    main()
