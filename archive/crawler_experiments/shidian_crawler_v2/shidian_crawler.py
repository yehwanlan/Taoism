#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
師典古籍網站爬蟲 - 更新版
基於 DZ1439 成功經驗開發

支援功能：
1. 爬取書籍資訊和章節列表
2. 爬取章節內容（使用 article/main 標籤）
3. 批量爬取多本書籍
4. 保存為 JSON 和文字檔案
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import os
import re
from pathlib import Path
from datetime import datetime
import logging

class ShidianCrawler:
    """師典古籍網站爬蟲"""
    
    def __init__(self, delay=2):
        """
        初始化爬蟲
        
        Args:
            delay: 請求間隔時間（秒）
        """
        self.base_url = "https://www.shidianguji.com"
        self.delay = delay
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.shidianguji.com/'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.setup_logging()
    
    def setup_logging(self):
        """設定日誌記錄"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('data/logs/shidian_crawler.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_book_info(self, book_id):
        """
        獲取書籍基本資訊和章節列表
        
        Args:
            book_id: 書籍編號（如 DZ1439）
            
        Returns:
            dict: 書籍資訊字典，包含章節列表
        """
        url = f"{self.base_url}/book/{book_id}?page_from=bookshelf&mode=book"
        
        try:
            self.logger.info(f"正在獲取書籍資訊: {book_id}")
            response = self.session.get(url, timeout=15)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                self.logger.error(f"請求失敗，狀態碼: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            book_info = {
                'book_id': book_id,
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
                self.logger.info(f"✓ 書名: {book_info['title']}")
            
            # 提取作者和朝代
            author_tag = soup.find('span', class_='book-title-author')
            if author_tag:
                author_text = author_tag.text.strip()
                book_info['author'] = author_text
                
                # 分離朝代和作者
                if '[' in author_text and ']' in author_text:
                    try:
                        dynasty_part = author_text.split(']')[0].replace('[', '').strip()
                        author_part = author_text.split(']')[1].replace('著', '').strip()
                        book_info['dynasty'] = dynasty_part
                        book_info['author'] = author_part
                        self.logger.info(f"✓ 朝代: {dynasty_part}, 作者: {author_part}")
                    except:
                        pass
            
            # 提取摘要
            desc_meta = soup.find('meta', {'name': 'description'})
            if desc_meta and desc_meta.get('content'):
                book_info['description'] = desc_meta['content'].strip()
                self.logger.info(f"✓ 摘要: {book_info['description'][:80]}...")
            
            # 提取章節目錄
            self.logger.info("正在提取章節目錄...")
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
                    self.logger.info(f"  {idx}. {chapter_name}")
            
            self.logger.info(f"✓ 總共找到 {len(book_info['chapters'])} 個章節")
            return book_info
            
        except Exception as e:
            self.logger.error(f"✗ 獲取書籍資訊失敗: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_chapter_content(self, chapter_url, chapter_name=""):
        """
        獲取章節內容
        
        Args:
            chapter_url: 章節 URL
            chapter_name: 章節名稱（用於日誌）
            
        Returns:
            dict: 包含標題和內容的字典
        """
        try:
            if chapter_name:
                self.logger.info(f"正在爬取: {chapter_name}")
            
            response = self.session.get(chapter_url, timeout=15)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                self.logger.warning(f"  ✗ 請求失敗，狀態碼: {response.status_code}")
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
            
            # 如果還是沒有，嘗試其他常見的內容容器
            if not content:
                content_selectors = [
                    ('div', {'class': 'chapter-content'}),
                    ('div', {'class': 'content'}),
                    ('div', {'class': 'article-content'}),
                    ('div', {'class': 'text-content'}),
                ]
                
                for tag_name, attrs in content_selectors:
                    content_tag = soup.find(tag_name, attrs)
                    if content_tag:
                        content = content_tag.get_text(separator='\n', strip=True)
                        break
            
            if content:
                # 清理內容
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                content = '\n'.join(lines)
                self.logger.info(f"  ✓ 成功，內容長度: {len(content)} 字")
            else:
                self.logger.warning(f"  ✗ 未找到內容")
            
            return {
                'title': title,
                'content': content,
                'url': chapter_url
            }
            
        except Exception as e:
            self.logger.error(f"  ✗ 爬取失敗: {e}")
            return None
    
    def crawl_all_chapters(self, book_info):
        """
        爬取所有章節內容
        
        Args:
            book_info: 書籍資訊字典
            
        Returns:
            dict: 更新後的書籍資訊（包含章節內容）
        """
        if not book_info or not book_info.get('chapters'):
            self.logger.warning("沒有章節資訊")
            return book_info
        
        total = len(book_info['chapters'])
        self.logger.info(f"\n開始爬取 {total} 個章節...")
        self.logger.info("=" * 60)
        
        success_count = 0
        
        for i, chapter in enumerate(book_info['chapters'], 1):
            self.logger.info(f"\n[{i}/{total}] {chapter['name']}")
            
            chapter_data = self.get_chapter_content(chapter['url'], chapter['name'])
            
            if chapter_data and chapter_data['content']:
                chapter['content'] = chapter_data['content']
                success_count += 1
            
            # 延遲，避免請求過快
            if i < total:
                time.sleep(self.delay)
        
        self.logger.info("\n" + "=" * 60)
        self.logger.info(f"✓ 爬取完成: {success_count}/{total} 章成功")
        
        return book_info
    
    def crawl_book(self, book_id, generate_templates=True):
        """
        爬取完整書籍（資訊 + 所有章節）
        
        Args:
            book_id: 書籍編號
            generate_templates: 是否自動生成翻譯模板（預設 True）
            
        Returns:
            dict: 完整的書籍資訊
        """
        self.logger.info("=" * 60)
        self.logger.info(f"開始爬取書籍: {book_id}")
        self.logger.info("=" * 60)
        
        # 步驟1: 獲取書籍資訊
        book_info = self.get_book_info(book_id)
        if not book_info:
            return None
        
        # 步驟2: 爬取所有章節
        book_info = self.crawl_all_chapters(book_info)
        
        # 步驟3: 自動保存和生成模板
        if book_info:
            self.logger.info("\n" + "=" * 60)
            self.logger.info("保存結果")
            self.logger.info("=" * 60)
            
            # 保存 JSON
            self.save_to_json(book_info)
            
            # 保存文字檔案
            self.save_to_text_files(book_info)
            
            # 生成翻譯模板
            if generate_templates:
                self.generate_translation_templates(book_info)
        
        return book_info
    
    def save_to_json(self, book_info, output_dir='data/crawled'):
        """
        保存為 JSON 格式
        
        Args:
            book_info: 書籍資訊
            output_dir: 輸出目錄
        """
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            filename = f"{book_info['book_id']}_{book_info['title']}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(book_info, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"✓ JSON 已保存: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"✗ 保存 JSON 失敗: {e}")
            return None
    
    def save_to_text_files(self, book_info, output_dir=None):
        """
        保存為文字檔案（每章一個檔案）
        
        Args:
            book_info: 書籍資訊
            output_dir: 輸出目錄（預設為 docs/source_texts/書名）
        """
        try:
            if output_dir is None:
                output_dir = f"docs/source_texts/{book_info['title']}"
            
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # 保存書籍資訊
            info_file = os.path.join(output_dir, '00_書籍資訊.txt')
            with open(info_file, 'w', encoding='utf-8') as f:
                f.write(f"書名: {book_info['title']}\n")
                f.write(f"作者: {book_info['author']}\n")
                f.write(f"朝代: {book_info['dynasty']}\n")
                f.write(f"書籍編號: {book_info['book_id']}\n")
                f.write(f"URL: {book_info['url']}\n")
                f.write(f"\n摘要:\n{book_info['description']}\n")
                f.write(f"\n總章節數: {len(book_info['chapters'])}\n")
            
            # 保存每個章節
            for chapter in book_info['chapters']:
                filename = f"{chapter['index']:02d}_{chapter['name']}.txt"
                # 移除檔名中的非法字元
                filename = filename.replace('/', '_').replace('\\', '_').replace(':', '_').replace('?', '_').replace('*', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"章節: {chapter['name']}\n")
                    f.write(f"URL: {chapter['url']}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(chapter.get('content', ''))
            
            self.logger.info(f"✓ 文字檔案已保存: {output_dir}/")
            self.logger.info(f"  共 {len(book_info['chapters']) + 1} 個檔案")
            return output_dir
            
        except Exception as e:
            self.logger.error(f"✗ 保存文字檔案失敗: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_translation_templates(self, book_info, output_dir=None):
        """
        生成翻譯模板（每章一個 Markdown 檔案）
        
        Args:
            book_info: 書籍資訊
            output_dir: 輸出目錄（預設為 docs/translations/書名）
        """
        try:
            if output_dir is None:
                output_dir = f"docs/translations/{book_info['title']}"
            
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"\n正在生成翻譯模板...")
            
            # 生成每個章節的翻譯模板
            for chapter in book_info['chapters']:
                filename = f"{chapter['index']:02d}_{chapter['name']}.md"
                # 移除檔名中的非法字元
                clean_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                filepath = os.path.join(output_dir, clean_filename)
                
                # 生成 Markdown 模板
                content = chapter.get('content', '')
                
                markdown_content = f"""# {chapter['name']}

## 原文

{content}

## 翻譯

[此處應為現代中文翻譯]

原文字數：{len(content)} 字

建議：請使用 AI 翻譯工具或人工翻譯此段落。

翻譯要點：
1. 保持原文意思
2. 使用現代中文表達
3. 保留重要的古代術語
4. 添加必要的註解說明

## 註解

**重要詞彙：**
- [待補充]

**文化背景：**
- [待補充]

**翻譯要點：**
- [待補充]

## 章節資訊

**章節編號：** {chapter['index']}
**章節名稱：** {chapter['name']}
**原始 URL：** {chapter['url']}

---
*翻譯模板生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*翻譯方式：自動生成模板*
"""
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                self.logger.info(f"  ✓ {chapter['index']:02d}. {chapter['name']}")
            
            # 生成 README
            readme_path = os.path.join(output_dir, 'README.md')
            readme_content = f"""# {book_info['title']} - 翻譯專案

## 書籍資訊

- **書名**：{book_info['title']}
- **作者**：{book_info['author']}
- **朝代**：{book_info['dynasty']}
- **書籍編號**：{book_info['book_id']}
- **原始網址**：{book_info['url']}

## 專案說明

本專案使用道教經典翻譯系統生成，包含：
1. 自動爬取的古文原文
2. 自動生成的翻譯模板
3. 完整的專案結構

## 章節列表

總共 {len(book_info['chapters'])} 個章節：

"""
            
            for chapter in book_info['chapters']:
                readme_content += f"{chapter['index']}. [{chapter['name']}]({chapter['index']:02d}_{re.sub(r'[<>:\"/\\|?*]', '_', chapter['name'])}.md)\n"
            
            readme_content += f"""
## 翻譯進度

- [ ] 待開始
- 總章節數：{len(book_info['chapters'])}
- 已完成：0
- 進度：0%

## 使用說明

1. 打開對應章節的 `.md` 檔案
2. 在「翻譯」區塊填寫現代中文翻譯
3. 在「註解」區塊補充重要詞彙和文化背景
4. 完成後更新上方的翻譯進度

## 翻譯規範

1. **忠實原文**：保持原文意思，不隨意增刪
2. **現代表達**：使用現代中文，讓讀者易懂
3. **保留術語**：重要的道教術語保留原文，加註解
4. **文化註解**：對特殊的文化背景進行說明

---
*專案建立時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*爬蟲版本：ShidianCrawler v2.0*
"""
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            self.logger.info(f"\n✓ 翻譯模板已生成: {output_dir}/")
            self.logger.info(f"  共 {len(book_info['chapters']) + 1} 個檔案（含 README）")
            return output_dir
            
        except Exception as e:
            self.logger.error(f"✗ 生成翻譯模板失敗: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def batch_crawl(self, book_ids, output_dir='data/crawled'):
        """
        批量爬取多本書籍
        
        Args:
            book_ids: 書籍編號列表
            output_dir: 輸出目錄
            
        Returns:
            list: 成功爬取的書籍資訊列表
        """
        results = []
        total = len(book_ids)
        
        self.logger.info("=" * 60)
        self.logger.info(f"批量爬取 {total} 本書籍")
        self.logger.info("=" * 60)
        
        for i, book_id in enumerate(book_ids, 1):
            self.logger.info(f"\n【{i}/{total}】處理書籍: {book_id}")
            self.logger.info("-" * 60)
            
            book_info = self.crawl_book(book_id)
            
            if book_info:
                # 保存結果
                self.save_to_json(book_info, output_dir)
                self.save_to_text_files(book_info)
                results.append(book_info)
                
                self.logger.info(f"✓ {book_id} 完成")
            else:
                self.logger.error(f"✗ {book_id} 失敗")
            
            # 書籍之間延遲更長時間
            if i < total:
                self.logger.info(f"等待 {self.delay * 2} 秒...")
                time.sleep(self.delay * 2)
        
        self.logger.info("\n" + "=" * 60)
        self.logger.info(f"批量爬取完成: {len(results)}/{total} 本成功")
        self.logger.info("=" * 60)
        
        return results
    
    def print_statistics(self, book_info):
        """
        列印爬取統計資訊
        
        Args:
            book_info: 書籍資訊
        """
        if not book_info:
            return
        
        success_count = sum(1 for ch in book_info['chapters'] if ch.get('content'))
        total_chars = sum(len(ch.get('content', '')) for ch in book_info['chapters'])
        
        print("\n" + "=" * 60)
        print("爬取統計")
        print("=" * 60)
        print(f"書名: {book_info['title']}")
        print(f"作者: {book_info['author']}")
        print(f"朝代: {book_info['dynasty']}")
        print(f"總章節數: {len(book_info['chapters'])}")
        print(f"成功爬取: {success_count} 章")
        print(f"失敗: {len(book_info['chapters']) - success_count} 章")
        print(f"總字數: {total_chars:,} 字")
        if success_count > 0:
            print(f"平均每章: {total_chars // success_count:,} 字")
        print("=" * 60)


def main():
    """主程式 - 示範使用"""
    
    # 建立爬蟲實例
    crawler = ShidianCrawler(delay=2)
    
    # 示範1: 爬取單本書籍（自動生成翻譯模板）
    print("示範1: 爬取單本書籍 (DZ1439) - 含翻譯模板")
    book_info = crawler.crawl_book('DZ1439', generate_templates=True)
    
    if book_info:
        # 列印統計
        crawler.print_statistics(book_info)
    
    # 示範2: 批量爬取（取消註解以使用）
    # book_ids = ['DZ1439', 'DZ1234', 'DZ1437']
    # results = crawler.batch_crawl(book_ids)


if __name__ == "__main__":
    main()
