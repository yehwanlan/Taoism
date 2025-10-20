# 師典古籍爬蟲測試總結

## 測試目標
爬取「丹陽真人直言」(DZ1234)
- URL: https://www.shidianguji.com/book/DZ1234/chapter/start?page_from=bookshelf&mode=book

## 測試結果

### ❌ main.py 測試失敗
```bash
python main.py translate --book "https://www.shidianguji.com/book/DZ1234/..."
```

**失敗原因：**
- `TranslationEngine` 使用的是基於 `requests` + `BeautifulSoup` 的靜態爬蟲
- 師典古籍網站使用 JavaScript 動態載入內容
- 靜態爬蟲無法獲取動態渲染的章節列表和內容

**錯誤訊息：**
```
⚠️  未找到章節，嘗試傳統方式...
❌ 無法獲取章節列表，程序終止
```

## 問題分析

### 1. 師典古籍網站特性
- ✅ 使用 JavaScript 動態載入內容
- ✅ 可能需要登錄才能查看完整內容
- ✅ 有反爬蟲機制
- ✅ 內容在 Canvas 或特殊容器中渲染

### 2. 現有爬蟲工具狀態

#### core/translator.py (TranslationEngine)
- **類型**: 靜態爬蟲 (requests + BeautifulSoup)
- **狀態**: ❌ 無法處理師典古籍
- **原因**: 無法執行 JavaScript

#### crawler/shidian_selenium.py
- **類型**: 動態爬蟲 (Selenium)
- **狀態**: ⚠️ 需要安裝依賴
- **依賴**: 
  - selenium
  - webdriver-manager
  - Chrome 瀏覽器

#### crawler/enhanced_shidian_crawler.py
- **類型**: 增強爬蟲管理器
- **狀態**: ⚠️ 依賴 Selenium
- **問題**: 方法名稱不匹配

## 解決方案

### 方案 1: 安裝 Selenium（推薦）

```bash
# 安裝依賴
pip install selenium webdriver-manager

# 使用 Selenium 爬蟲
cd crawler
python shidian_selenium.py
```

### 方案 2: 使用備用資源

師典古籍網站可能需要登錄，可以嘗試其他古籍網站：

1. **中國哲學書電子化計劃** (ctext.org)
   - URL: https://ctext.org/
   - 特點: 開放存取，無需登錄

2. **維基文庫** (zh.wikisource.org)
   - URL: https://zh.wikisource.org/wiki/道教
   - 特點: 開源內容，易於爬取

3. **國學大師** (guoxuedashi.com)
   - URL: http://www.guoxuedashi.com/daojia/
   - 特點: 內容豐富

### 方案 3: 修改 main.py 整合 Selenium

需要修改 `core/translator.py` 的 `TranslationEngine` 類：
- 添加 Selenium 支援
- 檢測網站類型（靜態/動態）
- 自動選擇合適的爬蟲策略

## 建議

### 短期方案
1. 安裝 Selenium 和 webdriver-manager
2. 直接使用 `crawler/shidian_selenium.py`
3. 或註冊師典古籍帳號後手動下載

### 長期方案
1. 重構 `TranslationEngine` 支援多種爬蟲策略
2. 實作自動檢測網站類型
3. 整合 Selenium 到主系統
4. 添加登錄功能支援

## 測試命令

```bash
# 測試 Selenium 爬蟲（需先安裝依賴）
cd crawler
python shidian_selenium.py

# 或使用測試腳本
python test_danyang_selenium.py
```

## 依賴安裝

```bash
# 安裝 Selenium
pip install selenium

# 安裝 webdriver-manager（自動管理 ChromeDriver）
pip install webdriver-manager

# 確保已安裝 Chrome 瀏覽器
```

## 結論

**main.py 目前無法爬取師典古籍網站**，因為：
1. 使用靜態爬蟲，無法處理 JavaScript 動態內容
2. 需要整合 Selenium 或使用專門的動態爬蟲工具
3. 建議先使用 `crawler/` 目錄中的專用工具測試
