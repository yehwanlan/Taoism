#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
道教經典爬蟲模組

主要爬蟲：
- ShidianCrawler: 師典古籍網站爬蟲（推薦使用）

使用範例：
    from crawler import ShidianCrawler
    
    crawler = ShidianCrawler()
    book = crawler.crawl_book('DZ1422')
"""

from .shidian_crawler import ShidianCrawler
from .base_crawler import BaseCrawler

__version__ = '2.0.0'
__author__ = 'Taoism Translation System'

__all__ = [
    'ShidianCrawler',
    'BaseCrawler',
]

# 便捷函數
def crawl_book(book_id, delay=2, generate_templates=True):
    """
    便捷函數：爬取單本書籍
    
    Args:
        book_id: 書籍編號（如 'DZ1422'）
        delay: 請求間隔時間（秒）
        generate_templates: 是否生成翻譯模板
        
    Returns:
        dict: 書籍資訊
        
    Example:
        >>> from crawler import crawl_book
        >>> book = crawl_book('DZ1422')
    """
    crawler = ShidianCrawler(delay=delay)
    return crawler.crawl_book(book_id, generate_templates=generate_templates)


def batch_crawl(book_ids, delay=3, output_dir='data/crawled'):
    """
    便捷函數：批量爬取多本書籍
    
    Args:
        book_ids: 書籍編號列表
        delay: 請求間隔時間（秒）
        output_dir: 輸出目錄
        
    Returns:
        list: 成功爬取的書籍列表
        
    Example:
        >>> from crawler import batch_crawl
        >>> results = batch_crawl(['DZ1422', 'DZ1439'])
    """
    crawler = ShidianCrawler(delay=delay)
    return crawler.batch_crawl(book_ids, output_dir=output_dir)
