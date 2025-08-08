#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道教經典專用爬蟲

學習重點：
1. 繼承和多型
2. 正規表達式處理文本
3. 資料清理和格式化
4. 結構化資料儲存
"""

import re
from pathlib import Path
from base_crawler import BaseCrawler

class TaoismCrawler(BaseCrawler):
    """道教經典爬蟲"""
    
    def __init__(self):
        super().__init__(delay_range=(2, 4))  # 較長的延遲時間
        self.output_dir = Path("../docs/source_texts")
        self.output_dir.mkdir(exist_ok=True)
        
    def clean_text(self, text):
        """
        清理文本內容
        
        學習重點：正規表達式的使用
        """
        # 移除多餘的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除 HTML 標籤殘留
        text = re.sub(r'<[^>]+>', '', text)
        
        # 移除特殊字符但保留中文標點
        text = re.sub(r'[^\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\s]', '', text)
        
        # 整理段落
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
        
    def extract_scripture_content(self, soup, title):
        """
        從網頁中提取經典內容
        
        Args:
            soup: BeautifulSoup 物件
            title: 經典標題
            
        Returns:
            清理後的文本內容
        """
        # 常見的內容容器選擇器
        content_selectors = [
            '.content',
            '.article-content',
            '.post-content',
            '#content',
            '.main-content',
            'article',
            '.text-content'
        ]
        
        content = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content = elements[0].get_text()
                break
                
        if not content:
            # 如果沒有找到特定容器，嘗試提取所有段落
            paragraphs = soup.find_all('p')
            content = '\n'.join([p.get_text() for p in paragraphs])
            
        return self.clean_text(content)
        
    def crawl_scripture(self, url, title):
        """
        爬取單一經典
        
        Args:
            url: 經典網址
            title: 經典標題
            
        Returns:
            是否成功爬取
        """
        self.logger.info(f"開始爬取: {title}")
        
        response = self.make_request(url)
        if not response:
            return False
            
        soup = self.parse_html(response.text)
        content = self.extract_scripture_content(soup, title)
        
        if content and len(content) > 100:  # 確保內容有意義
            filename = f"{title}.txt"
            self.save_text(content, filename, self.output_dir)
            self.logger.info(f"成功爬取: {title} ({len(content)} 字符)")
            return True
        else:
            self.logger.warning(f"內容太短或為空: {title}")
            return False
            
    def crawl_multiple_scriptures(self, scripture_urls):
        """
        批量爬取多個經典
        
        Args:
            scripture_urls: 字典，格式為 {標題: 網址}
        """
        success_count = 0
        total_count = len(scripture_urls)
        
        for title, url in scripture_urls.items():
            try:
                if self.crawl_scripture(url, title):
                    success_count += 1
                self.delay()  # 延遲避免被封鎖
            except Exception as e:
                self.logger.error(f"爬取 {title} 時發生錯誤: {e}")
                
        self.logger.info(f"爬取完成: {success_count}/{total_count} 成功")
        return success_count

# 示例使用方法
if __name__ == "__main__":
    crawler = TaoismCrawler()
    
    # 示例網址（請替換為實際的道教經典網站）
    sample_urls = {
        "道德經": "https://example.com/daodejing",
        "莊子": "https://example.com/zhuangzi",
        # 添加更多經典...
    }
    
    # 開始爬取
    # crawler.crawl_multiple_scriptures(sample_urls)