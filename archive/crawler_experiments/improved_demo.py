#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
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
    safe_print("-" * 30)
    
    valid_urls = []
    for title, url in test_urls:
        safe_print(f"驗證: {title} - {url}")
        result = finder.validate_scripture_url(url)
        
        if result['valid']:
            safe_print(f"  ✅ 有效 (長度: {result['content_length']}, 指標: {result['taoism_indicators']})")
            valid_urls.append((title, url))
        else:
            safe_print(f"  ❌ 無效 - {result['reason']}")
    
    safe_print(f"\n📥 開始爬取 {len(valid_urls)} 個有效網址...")
    safe_print("-" * 30)
    
    success_count = 0
    for title, url in valid_urls:
        safe_print(f"爬取: {title}")
        if crawler.crawl_scripture(url, title):
            success_count += 1
            safe_print("  ✅ 成功")
        else:
            safe_print("  ❌ 失敗")
        
        # 延遲避免被封鎖
        crawler.delay()
    
    safe_print(f"\n🎉 爬取完成！成功: {success_count}/{len(valid_urls)}")
    
    safe_print("\n📚 學習重點：")
    safe_print("1. 先驗證網址再爬取，提高成功率")
    safe_print("2. 處理多個網址時要適當延遲")
    safe_print("3. 檢查爬取內容的品質很重要")
    safe_print("4. 失敗是學習過程的一部分")

if __name__ == "__main__":
    improved_demo()
