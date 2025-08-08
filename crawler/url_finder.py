#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道教經典網址搜尋工具

學習重點：
1. 搜尋引擎 API 使用
2. 網址驗證和過濾
3. 資料持久化
"""

import json
import re
from urllib.parse import urljoin, urlparse
from base_crawler import BaseCrawler

class UrlFinder(BaseCrawler):
    """網址搜尋和驗證工具"""
    
    def __init__(self):
        super().__init__()
        self.taoism_keywords = [
            "道德經", "莊子", "列子", "文子", "鬼谷子",
            "太上感應篇", "陰符經", "參同契", "悟真篇",
            "雲笈七籤", "道藏", "正統道藏"
        ]
        
    def find_taoism_sites(self, base_url):
        """
        從基礎網站尋找道教相關連結
        
        Args:
            base_url: 基礎網站網址
            
        Returns:
            找到的相關連結列表
        """
        response = self.make_request(base_url)
        if not response:
            return []
            
        soup = self.parse_html(response.text)
        links = []
        
        # 尋找所有連結
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text().strip()
            
            # 檢查是否包含道教關鍵字
            if any(keyword in text for keyword in self.taoism_keywords):
                full_url = urljoin(base_url, href)
                links.append({
                    'title': text,
                    'url': full_url,
                    'keywords': [kw for kw in self.taoism_keywords if kw in text]
                })
                
        return links
        
    def validate_scripture_url(self, url):
        """
        驗證網址是否包含有效的經典內容
        
        Args:
            url: 要驗證的網址
            
        Returns:
            驗證結果字典
        """
        response = self.make_request(url)
        if not response:
            return {'valid': False, 'reason': '無法訪問'}
            
        soup = self.parse_html(response.text)
        text = soup.get_text()
        
        # 檢查內容長度
        if len(text) < 500:
            return {'valid': False, 'reason': '內容太短'}
            
        # 檢查是否包含道教相關內容
        taoism_indicators = ['道', '德', '無為', '自然', '玄', '虛', '靜']
        indicator_count = sum(1 for indicator in taoism_indicators if indicator in text)
        
        if indicator_count < 3:
            return {'valid': False, 'reason': '道教相關內容不足'}
            
        return {
            'valid': True,
            'content_length': len(text),
            'taoism_indicators': indicator_count
        }
        
    def save_urls(self, urls, filename="found_urls.json"):
        """儲存找到的網址"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(urls, f, ensure_ascii=False, indent=2)
        self.logger.info(f"已儲存 {len(urls)} 個網址到 {filename}")

# 常用的道教網站列表
TAOISM_WEBSITES = [
    "https://ctext.org/",  # 中國哲學書電子化計劃
    "https://www.daozang.org/",  # 道藏網
    # 可以添加更多網站...
]