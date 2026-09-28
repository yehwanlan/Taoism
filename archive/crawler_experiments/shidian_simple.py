#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
十典古籍網簡化爬蟲

專門針對您的需求設計的簡單實用版本
"""

import requests

def safe_print(*args, **kwargs):
    """安全的打印函數，自動處理導入問題"""
    try:
        from core.unicode_handler import safe_print as _safe_print
        _safe_print(*args, **kwargs)
    except ImportError:
        try:
            import sys
            from pathlib import Path
            sys.path.append(str(Path(__file__).parent.parent))
            from core.unicode_handler import safe_print as _safe_print
            _safe_print(*args, **kwargs)
        except ImportError:
            print(*args, **kwargs)
    except Exception:
        print(*args, **kwargs)

import re
import json
from pathlib import Path
from core.unicode_handler import safe_print

class ShidianSimple:
    """十典古籍網簡化爬蟲"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def extract_ids_from_url(self, url):
        """從URL提取書籍和章節ID"""
        book_match = re.search(r'/book/([^/]+)', url)
        chapter_match = re.search(r'/chapter/([^/?]+)', url)
        
        if book_match and chapter_match:
            return book_match.group(1), chapter_match.group(1)
        return None, None
        
    def try_api_endpoints(self, book_id, chapter_id):
        """嘗試不同的API端點"""
        base_url = "https://www.shidianguji.com"
        
        # 可能的API端點
        endpoints = [
            f"/api/book/{book_id}/chapter/{chapter_id}",
            f"/api/chapter/{chapter_id}",
            f"/api/content/{book_id}/{chapter_id}",
        ]
        
        results = []
        
        for endpoint in endpoints:
            try:
                url = base_url + endpoint
                safe_print(f"嘗試: {url}")
                
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    content = response.text
                    
                    # 檢查是否包含有用的中文內容
                    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
                    
                    if chinese_chars > 100:  # 至少100個中文字符
                        safe_print(f"✅ 成功: {url} (中文字符: {chinese_chars})")
                        results.append({
                            'url': url,
                            'content': content,
                            'chinese_count': chinese_chars
                        })
                    else:
                        safe_print(f"⚠️  回應太短: {url}")
                else:
                    safe_print(f"❌ 失敗: {url} (狀態碼: {response.status_code})")
                    
            except Exception as e:
                safe_print(f"❌ 錯誤: {url} - {e}")
                
        return results
        
    def extract_text_content(self, content):
        """從回應中提取文本內容"""
        
        # 方法1: 尋找JSON中的文本
        try:
            # 嘗試解析為JSON
            data = json.loads(content)
            return self.extract_from_json(data)
        except:
            pass
            
        # 方法2: 從HTML/JavaScript中提取
        return self.extract_from_html_js(content)
        
    def extract_from_json(self, data):
        """從JSON數據中提取文本"""
        texts = []
        
        def search_json(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in ['content', 'text', 'body'] and isinstance(value, str):
                        if len(value) > 20 and re.search(r'[\u4e00-\u9fff]', value):
                            texts.append(value)
                    elif isinstance(value, (dict, list)):
                        search_json(value)
            elif isinstance(obj, list):
                for item in obj:
                    search_json(item)
                    
        search_json(data)
        return '\n\n'.join(texts) if texts else None
        
    def extract_from_html_js(self, content):
        """從HTML/JavaScript中提取文本"""
        
        # 使用BeautifulSoup解析HTML
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # 尋找主要內容區域
            main_content = soup.find('main', class_='read-layout-main')
            if main_content:
                article = main_content.find('article', class_='chapter-reader')
                if article:
                    # 提取所有段落和標題
                    texts = []
                    for element in article.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                        text = element.get_text().strip()
                        if text and len(text) > 5:  # 過濾太短的文本
                            texts.append(text)
                    
                    if texts:
                        return '\n\n'.join(texts)
            
            # 如果沒有找到特定結構，嘗試提取所有有意義的段落
            paragraphs = soup.find_all('p')
            meaningful_texts = []
            for p in paragraphs:
                text = p.get_text().strip()
                if len(text) > 20 and re.search(r'[\u4e00-\u9fff]', text):
                    meaningful_texts.append(text)
                    
            if meaningful_texts:
                return '\n\n'.join(meaningful_texts)
                
        except ImportError:
            safe_print("⚠️  需要安裝 beautifulsoup4: pip install beautifulsoup4")
        except Exception as e:
            safe_print(f"⚠️  HTML解析錯誤: {e}")
        
        # 備用方案：使用正規表達式
        patterns = [
            r'"content":\s*"([^"]+)"',
            r'"text":\s*"([^"]+)"',
            r'content:\s*"([^"]+)"',
            r'text:\s*"([^"]+)"',
        ]
        
        all_matches = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # 解碼Unicode轉義
                try:
                    decoded = match.encode().decode('unicode_escape')
                    if len(decoded) > 20 and re.search(r'[\u4e00-\u9fff]', decoded):
                        all_matches.append(decoded)
                except:
                    if len(match) > 20 and re.search(r'[\u4e00-\u9fff]', match):
                        all_matches.append(match)
                        
        return '\n\n'.join(all_matches) if all_matches else None
        
    def crawl(self, url, output_filename=None):
        """爬取指定URL的內容"""
        safe_print(f"🕷️ 開始爬取: {url}")
        safe_print("=" * 50)
        
        # 提取ID
        book_id, chapter_id = self.extract_ids_from_url(url)
        if not book_id or not chapter_id:
            safe_print("❌ 無法從URL提取ID")
            return False
            
        safe_print(f"書籍ID: {book_id}")
        safe_print(f"章節ID: {chapter_id}")
        
        # 嘗試API端點
        results = self.try_api_endpoints(book_id, chapter_id)
        
        if not results:
            safe_print("❌ 沒有找到有效的API端點")
            return False
            
        # 選擇最佳結果（中文字符最多的）
        best_result = max(results, key=lambda x: x['chinese_count'])
        safe_print(f"\n📖 使用最佳結果: {best_result['url']}")
        
        # 提取文本內容
        text_content = self.extract_text_content(best_result['content'])
        
        if not text_content:
            safe_print("❌ 無法提取文本內容")
            # 儲存原始內容以供調試
            debug_file = f"debug_{book_id}_{chapter_id}.txt"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(best_result['content'])
            safe_print(f"💾 原始內容已儲存為: {debug_file}")
            return False
            
        # 清理文本
        cleaned_text = self.clean_text(text_content)
        
        # 儲存結果
        if not output_filename:
            output_filename = f"{book_id}_{chapter_id}_爬取結果.txt"
            
        output_path = Path("../docs/source_texts") / output_filename
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
            
        safe_print(f"✅ 爬取成功!")
        safe_print(f"文件: {output_path}")
        safe_print(f"內容長度: {len(cleaned_text)} 字符")
        
        return True
        
    def clean_text(self, text):
        """清理文本"""
        # 移除多餘空白
        text = re.sub(r'\s+', ' ', text)
        # 移除HTML標籤
        text = re.sub(r'<[^>]+>', '', text)
        # 移除JavaScript代碼片段
        text = re.sub(r'function\s*\([^)]*\)\s*\{[^}]*\}', '', text)
        text = re.sub(r'var\s+\w+\s*=\s*[^;]+;', '', text)
        # 整理段落
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()

def main():
    """主函數"""
    crawler = ShidianSimple()
    
    # 您提供的URL
    url = "https://www.shidianguji.com/book/SBCK109/chapter/1j70ybwytkcak_1?page_from=home_page&version=19"
    
    success = crawler.crawl(url, "抱朴子_第一章_簡化版.txt")
    
    if success:
        safe_print("\n🎉 爬取完成!")
        safe_print("💡 提示: 如果內容不完整，可以檢查debug文件")
    else:
        safe_print("\n❌ 爬取失敗")
        safe_print("💡 提示: 檢查debug文件了解詳細情況")

if __name__ == "__main__":
    main()
