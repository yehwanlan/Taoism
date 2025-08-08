#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium動態網頁爬蟲

學習重點：
1. 如何使用Selenium處理動態載入的內容
2. 如何等待頁面載入完成
3. 如何模擬真實瀏覽器行為
4. 如何處理JavaScript渲染的內容

注意：需要先安裝 selenium 和瀏覽器驅動
pip install selenium
"""

import time
import os
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium未安裝，請執行: pip install selenium")

from base_crawler import BaseCrawler

class SeleniumCrawler(BaseCrawler):
    """使用Selenium的動態網頁爬蟲"""
    
    def __init__(self, headless=True):
        super().__init__()
        self.headless = headless
        self.driver = None
        
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium未安裝，請先安裝: pip install selenium")
            
    def setup_driver(self):
        """設定瀏覽器驅動"""
        print("🔧 設定瀏覽器驅動...")
        
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')  # 無頭模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # 設定用戶代理
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)  # 隱式等待
            print("✅ Chrome驅動設定成功")
            return True
        except Exception as e:
            print(f"❌ Chrome驅動設定失敗: {e}")
            print("💡 請確保已安裝ChromeDriver或使用webdriver-manager")
            return False
            
    def wait_for_content(self, timeout=15):
        """等待頁面內容載入"""
        print("⏳ 等待頁面載入...")
        
        # 等待頁面基本載入完成
        WebDriverWait(self.driver, timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        
        # 額外等待JavaScript執行
        time.sleep(3)
        
        print("✅ 頁面載入完成")
        
    def extract_dynamic_content(self, url):
        """提取動態載入的內容"""
        print(f"🌐 開始載入動態頁面: {url}")
        
        if not self.driver:
            if not self.setup_driver():
                return None
                
        try:
            # 載入頁面
            self.driver.get(url)
            self.wait_for_content()
            
            # 嘗試多種內容選擇器
            content_selectors = [
                "//div[contains(@class, 'content')]",
                "//div[contains(@class, 'text')]", 
                "//div[contains(@class, 'chapter')]",
                "//article",
                "//main",
                "//div[contains(@class, 'book')]",
                "//p[string-length(text()) > 50]"  # 長度超過50的段落
            ]
            
            content_found = False
            all_content = []
            
            for selector in content_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        print(f"✅ 找到內容 (選擇器: {selector}, 元素數: {len(elements)})")
                        for elem in elements:
                            text = elem.text.strip()
                            if len(text) > 50:  # 只收集有意義的內容
                                all_content.append(text)
                                content_found = True
                except Exception as e:
                    continue
                    
            if content_found:
                # 去重並合併內容
                unique_content = []
                seen = set()
                for content in all_content:
                    if content not in seen and len(content) > 20:
                        unique_content.append(content)
                        seen.add(content)
                        
                final_content = '\n\n'.join(unique_content)
                print(f"📝 提取到內容，總長度: {len(final_content)} 字符")
                return final_content
            else:
                print("❌ 未找到有效內容")
                return None
                
        except TimeoutException:
            print("⏰ 頁面載入超時")
            return None
        except Exception as e:
            print(f"❌ 提取內容時發生錯誤: {e}")
            return None
            
    def crawl_dynamic_page(self, url, title=None):
        """爬取動態頁面"""
        print(f"🕷️ 開始爬取動態頁面")
        print(f"網址: {url}")
        print("-" * 50)
        
        content = self.extract_dynamic_content(url)
        
        if not content:
            return False
            
        # 確定標題
        if not title:
            try:
                page_title = self.driver.title
                title = page_title.split('-')[0].strip() if '-' in page_title else page_title
            except:
                title = "動態爬取_未知標題"
                
        # 清理內容
        cleaned_content = self.clean_text(content)
        
        # 儲存內容
        filename = f"{title}.txt"
        self.save_text(cleaned_content, filename, "../docs/source_texts")
        
        print(f"✅ 成功爬取: {title}")
        print(f"內容長度: {len(cleaned_content)} 字符")
        
        return True
        
    def close(self):
        """關閉瀏覽器"""
        if self.driver:
            self.driver.quit()
            print("🔒 瀏覽器已關閉")

# 使用示例
def crawl_shidian_with_selenium():
    """使用Selenium爬取十典古籍"""
    
    if not SELENIUM_AVAILABLE:
        print("❌ Selenium未安裝，無法使用動態爬蟲")
        print("請執行: pip install selenium")
        print("並下載ChromeDriver: https://chromedriver.chromium.org/")
        return
        
    crawler = SeleniumCrawler(headless=True)  # 設為False可以看到瀏覽器操作
    
    try:
        url = "https://www.shidianguji.com/book/SBCK109/chapter/1j70ybwytkcak_1?page_from=home_page&version=19"
        
        success = crawler.crawl_dynamic_page(url, "抱朴子_第一章_十典古籍")
        
        if success:
            print("\n🎉 動態爬取成功！")
        else:
            print("\n❌ 動態爬取失敗")
            
    finally:
        crawler.close()

if __name__ == "__main__":
    crawl_shidian_with_selenium()