#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抱朴子專用爬蟲

專門用於爬取抱朴子各章節內容
"""

import requests
import re
from pathlib import Path
from bs4 import BeautifulSoup

class BaopuziCrawler:
    """抱朴子專用爬蟲"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = "https://www.shidianguji.com"
        
    def extract_ids_from_url(self, url):
        """從URL提取書籍和章節ID"""
        book_match = re.search(r'/book/([^/]+)', url)
        chapter_match = re.search(r'/chapter/([^/?]+)', url)
        
        if book_match and chapter_match:
            return book_match.group(1), chapter_match.group(1)
        return None, None
        
    def get_chapter_content(self, url):
        """獲取章節內容"""
        book_id, chapter_id = self.extract_ids_from_url(url)
        if not book_id or not chapter_id:
            print("❌ 無法從URL提取ID")
            return None, None
            
        # 使用API端點
        api_url = f"{self.base_url}/api/book/{book_id}/chapter/{chapter_id}"
        
        try:
            response = self.session.get(api_url, timeout=10)
            if response.status_code == 200:
                return self.extract_text_from_html(response.text), chapter_id
        except Exception as e:
            print(f"❌ 請求失敗: {e}")
            
        return None, None
        
    def extract_text_from_html(self, html_content):
        """從HTML中提取文本內容"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 尋找主要內容區域
            main_content = soup.find('main', class_='read-layout-main')
            if main_content:
                article = main_content.find('article', class_='chapter-reader')
                if article:
                    # 提取標題和內容
                    result = {
                        'title': '',
                        'content': []
                    }
                    
                    for element in article.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
                        text = element.get_text().strip()
                        if text and len(text) > 3:
                            if element.name.startswith('h'):
                                result['title'] = text
                            else:
                                result['content'].append(text)
                    
                    return result
                    
        except Exception as e:
            print(f"⚠️  HTML解析錯誤: {e}")
            
        return None
        
    def save_chapter(self, content_data, chapter_id, chapter_number=None):
        """儲存章節內容"""
        if not content_data:
            return False
            
        # 建立檔案名稱
        if chapter_number:
            filename = f"{chapter_number:02d}_{content_data['title']}.txt"
        else:
            filename = f"{content_data['title']}.txt"
            
        # 清理檔案名稱中的特殊字符
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # 建立完整內容
        full_content = f"# {content_data['title']}\n\n"
        full_content += '\n\n'.join(content_data['content'])
        
        # 儲存到抱朴子資料夾
        output_path = Path("../docs/source_texts/抱朴子/原文") / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
            
        print(f"✅ 已儲存: {filename}")
        print(f"   標題: {content_data['title']}")
        print(f"   內容長度: {len(full_content)} 字符")
        
        return True
        
    def crawl_chapter(self, url, chapter_number=None):
        """爬取單一章節"""
        print(f"🕷️ 爬取章節: {url}")
        
        content_data, chapter_id = self.get_chapter_content(url)
        
        if content_data:
            return self.save_chapter(content_data, chapter_id, chapter_number)
        else:
            print("❌ 無法獲取章節內容")
            return False

def main():
    """主函數"""
    crawler = BaopuziCrawler()
    
    # 抱朴子章節列表
    chapters = [
        {
            'number': 2,
            'title': '抱朴子序',
            'url': 'https://www.shidianguji.com/book/SBCK109/chapter/1j70ybwyyqgje_2?page_from=home_page&version=19'
        },
        # 可以添加更多章節...
    ]
    
    print("🏗️ 開始建立抱朴子專案")
    print("=" * 50)
    
    success_count = 0
    for chapter in chapters:
        print(f"\n📖 處理第 {chapter['number']} 章: {chapter['title']}")
        
        if crawler.crawl_chapter(chapter['url'], chapter['number']):
            success_count += 1
        else:
            print(f"❌ 第 {chapter['number']} 章爬取失敗")
            
    print(f"\n🎉 完成！成功爬取 {success_count}/{len(chapters)} 章")

if __name__ == "__main__":
    main()