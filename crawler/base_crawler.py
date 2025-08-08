#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道教經典爬蟲基礎類別

學習重點：
1. 物件導向程式設計
2. 網路請求處理
3. 錯誤處理和重試機制
4. 中文編碼處理
"""

import requests
import time
import random
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from pathlib import Path
import logging

class BaseCrawler:
    """爬蟲基礎類別"""
    
    def __init__(self, delay_range=(1, 3)):
        """
        初始化爬蟲
        
        Args:
            delay_range: 請求間隔時間範圍（秒）
        """
        self.session = requests.Session()
        self.ua = UserAgent()
        self.delay_range = delay_range
        self.setup_logging()
        
    def setup_logging(self):
        """設定日誌記錄"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('crawler.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def get_random_headers(self):
        """產生隨機請求標頭"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
    def make_request(self, url, max_retries=3):
        """
        發送 HTTP 請求
        
        Args:
            url: 目標網址
            max_retries: 最大重試次數
            
        Returns:
            Response 物件或 None
        """
        for attempt in range(max_retries):
            try:
                headers = self.get_random_headers()
                response = self.session.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                # 處理中文編碼
                if response.encoding == 'ISO-8859-1':
                    response.encoding = 'utf-8'
                    
                self.logger.info(f"成功請求: {url}")
                return response
                
            except requests.RequestException as e:
                self.logger.warning(f"請求失敗 (嘗試 {attempt + 1}/{max_retries}): {url} - {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(2, 5))
                    
        self.logger.error(f"所有重試都失敗: {url}")
        return None
        
    def parse_html(self, html_content):
        """
        解析 HTML 內容
        
        Args:
            html_content: HTML 字串
            
        Returns:
            BeautifulSoup 物件
        """
        return BeautifulSoup(html_content, 'lxml')
        
    def delay(self):
        """隨機延遲，避免被封鎖"""
        delay_time = random.uniform(*self.delay_range)
        time.sleep(delay_time)
        
    def save_text(self, content, filename, directory="scraped_texts"):
        """
        儲存文本內容
        
        Args:
            content: 文本內容
            filename: 檔案名稱
            directory: 儲存目錄
        """
        save_dir = Path(directory)
        save_dir.mkdir(exist_ok=True)
        
        file_path = save_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        self.logger.info(f"已儲存: {file_path}")