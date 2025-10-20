#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DZ1439 洞玄靈寶玉京山步虛經 完整爬蟲
支援爬取書籍資訊、章節列表和章節內容
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import os

class DZ1439Crawler:
    """DZ1439 專用爬蟲"""
    
    def __init__(self):
        self.base_url = "https://www.shidianguji.com"
        self.book_id = "DZ1439"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.shidianguji.com/'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_book_info(self):
        """獲取書籍基本資訊和章節列表"""
        
        url = f"{self.base_url}/book/{self.book_id}?page_from=bookshelf&mode=book"
        
        try:
            print(f"正在獲取書籍資訊: {url}")
            response = self.session.get(url, timeout=15)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"請求失敗，狀態碼: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            book_info = {
                'book_id': self.book_id,
                'url': url,
                'title': '',
                'author': '',
                'dynasty': '',
                'description': '',
                'chapters': []
            }
            
            # 提取書名
            title_tag = soup.find('h1', class_='HbYW1Abi')
            if title_tag:
                book_info['title'] = title_tag.text.strip()
                print(f"✓ 書名: {book_info['title']}")
            
            # 提取作者和朝代
            author_tag = soup.find('span', class_='book-title-author')
            if author_tag:
                author_text = author_tag.text.strip()
                book_info['author'] = author_text
                
                # 分離朝代和作者
                if '[' in author_text and ']' in author_text:
                    dynasty_part = author_text.split(']')[0].replace('[', '').strip()
                    author_part = author_text.split(']')[1].replace('著', '').strip()
                    book_info['dynasty'] = dynasty_part
                    book_info['author'] = author_part
                    print(f"✓ 朝代: {dynasty_part}, 作者: {author_part}")
            
            # 提取摘要
            desc_meta = soup.find('meta', {'name': 'description'})
            if desc_meta and desc_meta.get('content'):
                book_info['description'] = desc_meta['content'].strip()
                print(f"✓ 摘要: {book_info['description'][:80]}...")
            
            # 提取章節目錄
            print("\n正在提取章節目錄...")
            chapter_items = soup.find_all('div', class_='semi-tree-option')
            
            for idx, item in enumerate(chapter_items, 1):
                a_tag = item.find('a')
                if a_tag:
                    chapter_name = a_tag.text.strip()
                    chapter_url = a_tag.get('href', '')
                    
                    if chapter_url and not chapter_url.startswith('http'):
                        chapter_url = self.base_url + chapter_url
                    
                    chapter_info = {
                        'index': idx,
                        'name': chapter_name,
                        'url': chapter_url,
                        'content': ''
                    }
                    
                    book_info['chapters'].append(chapter_info)
                    print(f"  {idx}. {chapter_name}")
            
            print(f"\n✓ 總共找到 {len(book_info['chapters'])} 個章節")
            return book_info
            
        except Exception as e:
            print(f"✗ 獲取書籍資訊失敗: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_chapter_content(self, chapter_url, chapter_name=""):
        """獲取章節內容"""
        
        try:
            if chapter_name:
                print(f"\n正在爬取: {chapter_name}")
            
            response = self.session.get(chapter_url, timeout=15)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"  ✗ 請求失敗，狀態碼: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取章節標題
            title = ""
            title_tag = soup.find('h1')
            if title_tag:
                title = title_tag.text.strip()
            
            # 提取正文內容 - 使用 article 或 main 標籤
            content = ""
            
            # 優先使用 article 標籤
            article_tag = soup.find('article')
            if article_tag:
                # 移除導航和其他非內容元素
                for nav in article_tag.find_all(['nav', 'header', 'footer']):
                    nav.decompose()
                
                content = article_tag.get_text(separator='\n', strip=True)
            
            # 如果沒有 article，嘗試 main 標籤
            if not content:
                main_tag = soup.find('main')
                if main_tag:
                    for nav in main_tag.find_all(['nav', 'header', 'footer']):
                        nav.decompose()
                    content = main_tag.get_text(separator='\n', strip=True)
            
            if content:
                # 清理內容
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                content = '\n'.join(lines)
                print(f"  ✓ 成功，內容長度: {len(content)} 字")
            else:
                print(f"  ✗ 未找到內容")
            
            return {
                'title': title,
                'content': content,
                'url': chapter_url
            }
            
        except Exception as e:
            print(f"  ✗ 爬取失敗: {e}")
            return None
    
    def crawl_all_chapters(self, book_info, delay=2):
        """爬取所有章節內容"""
        
        if not book_info or not book_info.get('chapters'):
            print("沒有章節資訊")
            return book_info
        
        total = len(book_info['chapters'])
        print(f"\n開始爬取 {total} 個章節...")
        print("=" * 60)
        
        for i, chapter in enumerate(book_info['chapters'], 1):
            print(f"\n[{i}/{total}] {chapter['name']}")
            
            chapter_data = self.get_chapter_content(chapter['url'], chapter['name'])
            
            if chapter_data and chapter_data['content']:
                chapter['content'] = chapter_data['content']
            
            # 延遲，避免請求過快
            if i < total:
                time.sleep(delay)
        
        print("\n" + "=" * 60)
        print("✓ 所有章節爬取完成")
        
        return book_info
    
    def save_to_json(self, book_info, filename='dz1439_complete.json'):
        """保存為 JSON 格式"""
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(book_info, f, ensure_ascii=False, indent=2)
            print(f"\n✓ 已保存到: {filename}")
            return True
        except Exception as e:
            print(f"\n✗ 保存失敗: {e}")
            return False
    
    def save_to_text_files(self, book_info, output_dir='dz1439_output'):
        """保存為文字檔案（每章一個檔案）"""
        
        try:
            # 建立輸出目錄
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # 保存書籍資訊
            info_file = os.path.join(output_dir, '00_書籍資訊.txt')
            with open(info_file, 'w', encoding='utf-8') as f:
                f.write(f"書名: {book_info['title']}\n")
                f.write(f"作者: {book_info['author']}\n")
                f.write(f"朝代: {book_info['dynasty']}\n")
                f.write(f"書籍編號: {book_info['book_id']}\n")
                f.write(f"\n摘要:\n{book_info['description']}\n")
                f.write(f"\n總章節數: {len(book_info['chapters'])}\n")
            
            # 保存每個章節
            for chapter in book_info['chapters']:
                filename = f"{chapter['index']:02d}_{chapter['name']}.txt"
                # 移除檔名中的非法字元
                filename = filename.replace('/', '_').replace('\\', '_').replace(':', '_')
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"章節: {chapter['name']}\n")
                    f.write(f"URL: {chapter['url']}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(chapter.get('content', ''))
            
            print(f"\n✓ 文字檔案已保存到: {output_dir}/")
            print(f"  共 {len(book_info['chapters']) + 1} 個檔案")
            return True
            
        except Exception as e:
            print(f"\n✗ 保存文字檔案失敗: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """主程式"""
    
    print("=" * 60)
    print("DZ1439 洞玄靈寶玉京山步虛經 爬蟲")
    print("=" * 60)
    
    crawler = DZ1439Crawler()
    
    # 步驟1: 獲取書籍資訊和章節列表
    print("\n【步驟 1】獲取書籍資訊和章節列表")
    print("-" * 60)
    book_info = crawler.get_book_info()
    
    if not book_info:
        print("\n✗ 無法獲取書籍資訊，程式結束")
        return
    
    # 步驟2: 爬取所有章節內容
    print("\n【步驟 2】爬取所有章節內容")
    print("-" * 60)
    book_info = crawler.crawl_all_chapters(book_info, delay=2)
    
    # 步驟3: 保存結果
    print("\n【步驟 3】保存結果")
    print("-" * 60)
    
    # 保存為 JSON
    crawler.save_to_json(book_info, 'dz1439_complete.json')
    
    # 保存為文字檔案
    crawler.save_to_text_files(book_info, 'dz1439_output')
    
    # 統計資訊
    print("\n" + "=" * 60)
    print("爬取統計")
    print("=" * 60)
    print(f"書名: {book_info['title']}")
    print(f"總章節數: {len(book_info['chapters'])}")
    
    success_count = sum(1 for ch in book_info['chapters'] if ch.get('content'))
    print(f"成功爬取: {success_count} 章")
    print(f"失敗: {len(book_info['chapters']) - success_count} 章")
    
    total_chars = sum(len(ch.get('content', '')) for ch in book_info['chapters'])
    print(f"總字數: {total_chars:,} 字")
    
    print("\n✓ 完成！")

if __name__ == "__main__":
    main()
