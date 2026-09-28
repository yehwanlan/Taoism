#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬蟲執行腳本

學習重點：
1. 命令列介面設計
2. 配置檔案使用
3. 進度追蹤和報告
"""

import argparse
import json
from pathlib import Path
from taoism_crawler import TaoismCrawler
from url_finder import UrlFinder
from core.unicode_handler import safe_print

def load_config(config_file="crawler_config.json"):
    """載入爬蟲配置"""
    if Path(config_file).exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # 預設配置
        default_config = {
            "target_scriptures": {
                "道德經": "https://ctext.org/dao-de-jing",
                "莊子": "https://ctext.org/zhuangzi",
                "列子": "https://ctext.org/liezi"
            },
            "output_directory": "../docs/source_texts",
            "delay_range": [2, 4],
            "max_retries": 3
        }
        
        # 儲存預設配置
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
            
        safe_print(f"已建立預設配置檔案: {config_file}")
        safe_print("請編輯配置檔案後重新執行")
        return default_config

def main():
    parser = argparse.ArgumentParser(description="道教經典爬蟲工具")
    parser.add_argument("--mode", choices=["crawl", "find", "validate"], 
                       default="crawl", help="執行模式")
    parser.add_argument("--config", default="crawler_config.json", 
                       help="配置檔案路徑")
    parser.add_argument("--url", help="單一網址（用於驗證模式）")
    
    args = parser.parse_args()
    
    if args.mode == "crawl":
        # 爬取模式
        config = load_config(args.config)
        crawler = TaoismCrawler()
        
        safe_print("開始爬取道教經典...")
        success_count = crawler.crawl_multiple_scriptures(
            config["target_scriptures"]
        )
        safe_print(f"爬取完成！成功: {success_count} 個經典")
        
    elif args.mode == "find":
        # 搜尋模式
        finder = UrlFinder()
        safe_print("搜尋道教相關網址...")
        
        # 這裡可以添加搜尋邏輯
        safe_print("搜尋功能開發中...")
        
    elif args.mode == "validate":
        # 驗證模式
        if not args.url:
            safe_print("驗證模式需要提供 --url 參數")
            return
            
        finder = UrlFinder()
        result = finder.validate_scripture_url(args.url)
        
        if result['valid']:
            safe_print(f"✅ 網址有效: {args.url}")
            safe_print(f"內容長度: {result['content_length']}")
            safe_print(f"道教指標: {result['taoism_indicators']}")
        else:
            safe_print(f"❌ 網址無效: {args.url}")
            safe_print(f"原因: {result['reason']}")

if __name__ == "__main__":
    main()