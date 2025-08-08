# 道教經典爬蟲工具

## 🎯 學習目標

這個爬蟲工具讓您學習：
- 網路爬蟲基礎概念
- Python 物件導向程式設計
- 網頁內容解析和處理
- 中文文本處理技巧
- 錯誤處理和重試機制

## 📦 安裝步驟

### 1. 安裝必要套件

```bash
# 在 crawler 目錄下執行
pip install -r requirements.txt
```

### 2. 檢查安裝

```bash
python run_crawler.py --help
```

## 🚀 使用方法

### 基本爬取

```bash
# 使用預設配置爬取經典
python run_crawler.py --mode crawl
```

### 驗證網址

```bash
# 驗證單一網址是否適合爬取
python run_crawler.py --mode validate --url "https://example.com/scripture"
```

### 搜尋相關網址

```bash
# 搜尋道教相關網址（開發中）
python run_crawler.py --mode find
```

## ⚙️ 配置檔案

第一次執行會自動建立 `crawler_config.json`：

```json
{
  "target_scriptures": {
    "道德經": "https://ctext.org/dao-de-jing",
    "莊子": "https://ctext.org/zhuangzi",
    "列子": "https://ctext.org/liezi"
  },
  "output_directory": "../docs/source_texts",
  "delay_range": [2, 4],
  "max_retries": 3
}
```

## 📚 學習重點

### 1. 基礎爬蟲概念
- HTTP 請求和回應
- HTML 解析
- 反爬蟲機制應對

### 2. 程式設計技巧
- 物件導向設計
- 錯誤處理
- 日誌記錄

### 3. 中文處理
- 編碼問題解決
- 文本清理
- 正規表達式使用

## ⚠️ 注意事項

1. **遵守網站規則**：檢查 robots.txt 和使用條款
2. **適當延遲**：避免對目標網站造成負擔
3. **內容版權**：注意版權問題，僅用於學習目的
4. **測試先行**：先用小範圍測試再大量爬取

## 🔧 進階功能

### 自定義爬蟲

```python
from taoism_crawler import TaoismCrawler

# 建立自定義爬蟲
crawler = TaoismCrawler()

# 爬取單一經典
success = crawler.crawl_scripture(
    "https://example.com/scripture", 
    "經典名稱"
)
```

### 批量處理

```python
# 批量爬取
urls = {
    "經典1": "https://example.com/1",
    "經典2": "https://example.com/2"
}

success_count = crawler.crawl_multiple_scriptures(urls)
```

## 📈 後續學習方向

1. **進階爬蟲技術**
   - Selenium 動態網頁處理
   - 驗證碼識別
   - 分散式爬蟲

2. **資料處理**
   - 自然語言處理
   - 文本相似度比較
   - 自動分類標記

3. **系統整合**
   - 定時任務
   - 資料庫儲存
   - API 介面開發