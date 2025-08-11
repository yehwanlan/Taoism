#!/usr/bin/env python3
# -*- coding: utf-8 -*-"""
改進的爬蟲示例

學習重點：
1. 如何處理爬蟲失敗的情況
2. 如何選擇更好的目標網址
3. 如何驗證爬取內容的品質
"""

from taoism_crawler import TaoismCrawler
from url_finder import UrlFinder
from core.unicode_handler import safe_print

def improved_demo():
    """改進的爬蟲示例"""
    safe_print("🔧 改進的道教經典爬蟲示例")
    safe_print("=" * 50)
    
    # 建立工具實例
    crawler = TaoismCrawler()
    finder = UrlFinder()
    
    # 測試多個可能的網址
    test_urls = [
        ("道德經", "https://ctext.org/dao-de-jing"),
        ("道德經全文", "https://ctext.org/dao-de-jing/zh"),
        ("莊子", "https://ctext.org/zhuangzi"),
    ]
    
    safe_print("🔍 正在驗證網址品質...")
    safe_print("-