#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
師典古籍網 Selenium 爬蟲 - 處理動態載入內容
"""

import time
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent))

def safe_print(*args, **kwargs):
    """安全的打印函數"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                safe_args.append(arg.encode('utf-8', errors='replace').decode('utf-8'))
            else:
                safe_args.append(str(arg))
        print(*safe_args, **kwargs)

# 檢查 Selenium 依賴
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError as e:
    safe_print(f"❌ Selenium 未安裝: {e}")
    safe_print("請執行: pip install selenium")
    SELENIUM_AVAILABLE = False

# 檢查 webdriver-manager
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False
    safe_print("💡 建議安裝 webdriver-manager: pip install webdriver-manager")

class ShidianSeleniumCrawler:
    """師典古籍網 Selenium 爬蟲"""
    
    def __init__(self, headless=True, wait_timeout=30):
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium 未安裝，請執行: pip install selenium")
        
        self.headless = headless
        self.wait_timeout = wait_timeout
        self.driver = None
        
    def setup_driver(self):
        """設置 Chrome WebDriver"""
        safe_print("🔧 正在設置 Chrome WebDriver...")
        
        # Chrome 選項
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless=new')
            safe_print("👻 使用無頭模式")
        
        # 其他選項
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 設置 User-Agent
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            if WEBDRIVER_MANAGER_AVAILABLE:
                # 使用 webdriver-manager 自動管理 ChromeDriver
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                safe_print("✅ 使用 webdriver-manager 初始化成功")
            else:
                # 嘗試使用系統中的 ChromeDriver
                self.driver = webdriver.Chrome(options=chrome_options)
                safe_print("✅ 使用系統 ChromeDriver 初始化成功")
                
        except Exception as e:
            safe_print(f"❌ ChromeDriver 初始化失敗: {e}")
            safe_print("💡 解決方案:")
            safe_print("   1. 安裝 webdriver-manager: pip install webdriver-manager")
            safe_print("   2. 或手動下載 ChromeDriver: https://chromedriver.chromium.org/")
            safe_print("   3. 確保 Chrome 瀏覽器已安裝")
            raise
        
        # 執行反檢測腳本
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def wait_for_content(self, url):
        """等待頁面內容載入"""
        safe_print(f"⏳ 等待頁面載入: {url}")
        
        try:
            # 訪問頁面
            self.driver.get(url)
            safe_print("📄 頁面已載入，等待內容...")
            
            # 等待頁面基本結構載入
            WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 等待可能的載入動畫消失
            time.sleep(5)
            
            # 嘗試等待內容區域
            content_selectors = [
                "#canvas-reader",
                ".chapter-reader-content", 
                ".text-container",
                ".content",
                "main"
            ]
            
            content_element = None
            for selector in content_selectors:
                try:
                    content_element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    safe_print(f"✅ 找到內容區域: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not content_element:
                safe_print("⚠️  未找到特定內容區域，使用整個頁面")
            
            # 額外等待動態內容載入
            safe_print("⏳ 等待動態內容載入...")
            time.sleep(10)
            
            return True
            
        except TimeoutException:
            safe_print(f"❌ 頁面載入超時 ({self.wait_timeout}秒)")
            return False
        except Exception as e:
            safe_print(f"❌ 頁面載入失敗: {e}")
            return False
    
    def extract_content(self):
        """提取頁面內容"""
        safe_print("📖 開始提取內容...")
        
        try:
            # 嘗試多種內容提取策略
            content_strategies = [
                # 策略1: 特定內容區域
                {
                    'name': '內容區域',
                    'selectors': ['#canvas-reader', '.chapter-reader-content', '.text-container']
                },
                # 策略2: 主要內容
                {
                    'name': '主要內容',
                    'selectors': ['main', 'article', '.content', '.main-content']
                },
                # 策略3: 文本段落
                {
                    'name': '文本段落',
                    'selectors': ['p', '.text', '.paragraph']
                }
            ]
            
            best_content = ""
            best_strategy = None
            
            for strategy in content_strategies:
                safe_print(f"🔍 嘗試策略: {strategy['name']}")
                
                for selector in strategy['selectors']:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        if elements:
                            # 提取所有匹配元素的文本
                            texts = []
                            for element in elements:
                                text = element.text.strip()
                                if text and len(text) > 10:  # 過濾太短的文本
                                    texts.append(text)
                            
                            combined_text = '\n'.join(texts)
                            
                            if len(combined_text) > len(best_content):
                                best_content = combined_text
                                best_strategy = f"{strategy['name']} - {selector}"
                                safe_print(f"✅ 找到更好的內容: {len(combined_text)} 字符")
                    
                    except Exception as e:
                        safe_print(f"⚠️  選擇器 {selector} 失敗: {e}")
                        continue
            
            # 如果沒有找到好的內容，嘗試提取所有可見文本
            if len(best_content) < 100:
                safe_print("🔍 嘗試提取所有可見文本...")
                try:
                    body_element = self.driver.find_element(By.TAG_NAME, "body")
                    all_text = body_element.text
                    
                    if len(all_text) > len(best_content):
                        best_content = all_text
                        best_strategy = "整個頁面"
                        safe_print(f"✅ 提取整頁內容: {len(all_text)} 字符")
                
                except Exception as e:
                    safe_print(f"❌ 提取整頁內容失敗: {e}")
            
            if best_content:
                safe_print(f"🎉 內容提取成功!")
                safe_print(f"📊 使用策略: {best_strategy}")
                safe_print(f"📊 內容長度: {len(best_content)} 字符")
                
                # 顯示內容預覽
                preview_lines = best_content.split('\n')[:5]
                safe_print("📝 內容預覽:")
                for i, line in enumerate(preview_lines, 1):
                    if line.strip():
                        preview = line[:80] + '...' if len(line) > 80 else line
                        safe_print(f"   {i}. {preview}")
                
                return self.clean_content(best_content)
            else:
                safe_print("❌ 未能提取到有效內容")
                return None
                
        except Exception as e:
            safe_print(f"❌ 內容提取失敗: {e}")
            return None
    
    def clean_content(self, content):
        """清理提取的內容"""
        if not content:
            return ""
        
        lines = []
        for line in content.split('\n'):
            line = line.strip()
            
            # 過濾條件
            if (line and 
                len(line) > 2 and
                not self.is_navigation_text(line) and
                not self.is_metadata_text(line)):
                lines.append(line)
        
        return '\n'.join(lines)
    
    def is_navigation_text(self, text):
        """判斷是否為導航文字"""
        nav_keywords = [
            '首頁', '登錄', '註冊', '搜索', '菜單', '導航', '书库',
            'home', 'login', 'register', 'search', 'menu', 'nav',
            '上一頁', '下一頁', '返回', '目錄', '章節',
            '版權', 'copyright', '聯繫', 'contact'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in nav_keywords)
    
    def is_metadata_text(self, text):
        """判斷是否為元數據文字"""
        return (text.isdigit() or 
                len(text) < 5 or
                text in ['登录后阅读更方便', '书库登录后阅读更方便'])
    
    def save_content(self, content, filename, directory="docs/source_texts"):
        """儲存內容到檔案"""
        try:
            save_dir = Path(directory)
            save_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = save_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            safe_print(f"✅ 已儲存: {file_path}")
            safe_print(f"📊 檔案大小: {file_path.stat().st_size} 字節")
            
            return True
        except Exception as e:
            safe_print(f"❌ 儲存失敗: {e}")
            return False
    
    def crawl_page(self, url, custom_title=None):
        """爬取單個頁面"""
        safe_print("🕷️ 開始 Selenium 爬蟲")
        safe_print(f"🌐 目標URL: {url}")
        safe_print("-" * 60)
        
        try:
            # 設置 WebDriver
            self.setup_driver()
            
            # 等待頁面載入
            if not self.wait_for_content(url):
                return False
            
            # 提取內容
            content = self.extract_content()
            
            if not content or len(content) < 50:
                safe_print("❌ 未能提取到有效內容")
                
                # 嘗試截圖用於調試
                try:
                    screenshot_path = Path("crawler") / "debug_screenshot.png"
                    self.driver.save_screenshot(str(screenshot_path))
                    safe_print(f"📸 已儲存調試截圖: {screenshot_path}")
                except:
                    pass
                
                return False
            
            # 確定檔案名
            if custom_title:
                filename = f"{custom_title}.txt"
            else:
                filename = "師典古籍_Selenium版.txt"
            
            # 儲存內容
            success = self.save_content(content, filename)
            
            if success:
                safe_print("🎉 Selenium 爬蟲成功完成！")
            
            return success
            
        except Exception as e:
            safe_print(f"❌ 爬蟲過程發生錯誤: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            self.close()
    
    def close(self):
        """關閉 WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                safe_print("✅ WebDriver 已關閉")
            except:
                pass

def main():
    """主函數"""
    if not SELENIUM_AVAILABLE:
        safe_print("❌ 無法運行 Selenium 爬蟲")
        safe_print("請安裝必要依賴:")
        safe_print("   pip install selenium webdriver-manager")
        return
    
    # 丹陽真人直言
    target_url = "https://www.shidianguji.com/book/DZ1234/chapter/start?page_from=bookshelf&mode=book"
    
    safe_print("🚀 師典古籍網 Selenium 爬蟲")
    safe_print("=" * 60)
    safe_print("💡 此爬蟲使用 Selenium 處理動態載入的內容")
    safe_print("⏳ 請耐心等待，載入可能需要較長時間...")
    safe_print("")
    
    # 詢問是否使用有頭模式（用於調試）
    try:
        debug_mode = input("是否使用調試模式（顯示瀏覽器窗口）？[y/N]: ").strip().lower()
        headless = debug_mode not in ['y', 'yes', '是']
    except (EOFError, KeyboardInterrupt):
        headless = True
    
    crawler = ShidianSeleniumCrawler(headless=headless, wait_timeout=30)
    
    success = crawler.crawl_page(target_url, "丹陽真人直言_DZ1234")
    
    if success:
        safe_print("\n" + "🎉" * 20)
        safe_print("Selenium 爬蟲成功完成！")
        safe_print("🎉" * 20)
        safe_print("📁 檔案已儲存到 docs/source_texts/ 目錄")
        safe_print("💡 如果內容不完整，可能需要登錄帳號")
    else:
        safe_print("\n" + "❌" * 20)
        safe_print("Selenium 爬蟲失敗")
        safe_print("❌" * 20)
        safe_print("💡 可能的原因:")
        safe_print("   1. 網站需要登錄才能查看內容")
        safe_print("   2. 網站有反爬蟲機制")
        safe_print("   3. 網路連接問題")
        safe_print("   4. ChromeDriver 配置問題")

if __name__ == "__main__":
    main()
