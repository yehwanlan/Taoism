#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬蟲示例演示

學習重點：實際使用爬蟲工具
"""

from taoism_crawler import TaoismCrawler

def demo_crawl():
    """示例爬取功能"""
    print("🕷️ 道教經典爬蟲示例")
    print("=" * 50)
    
    # 建立爬蟲實例
    crawler = TaoismCrawler()
    
    # 示例：爬取道德經的一小部分
    test_url = "https://ctext.org/dao-de-jing/1"
    title = "道德經第一章"
    
    print(f"正在爬取: {title}")
    print(f"網址: {test_url}")
    print("-" * 30)
    
    success = crawler.crawl_scripture(test_url, title)
    
    if success:
        print("✅ 爬取成功！")
        print("檔案已儲存到 ../docs/source_texts/")
    else:
        print("❌ 爬取失敗")
        
    print("\n📚 學習重點：")
    print("1. 觀察爬蟲的請求過程")
    print("2. 查看生成的日誌檔案 crawler.log")
    print("3. 檢查儲存的文本檔案")
    print("4. 了解延遲機制的重要性")

if __name__ == "__main__":
    demo_crawl()