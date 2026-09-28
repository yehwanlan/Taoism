# 道教經典爬蟲模組

## 🎯 核心功能

完整的道教經典爬取和翻譯工作流程工具：

✅ **自動爬取經文** - 從師典古籍網站爬取道教經典  
✅ **保存原文** - 結構化保存為文字檔案  
✅ **生成翻譯模板** - 自動建立 Markdown 翻譯模板  
✅ **批量處理** - 支援批量爬取多本書籍  
✅ **完整日誌** - 詳細的執行日誌和錯誤追蹤  

## 🚀 快速開始

### 最簡單的方式

```bash
# 直接執行主爬蟲
python crawler/shidian_crawler.py
```

### Python 腳本

```python
from crawler.shidian_crawler import ShidianCrawler

# 建立爬蟲
crawler = ShidianCrawler(delay=2)

# 爬取書籍（自動生成翻譯模板）
book = crawler.crawl_book('DZ1422')

# 查看統計
crawler.print_statistics(book)
```

## 📁 模組結構

```
crawler/
├── shidian_crawler.py          # 主爬蟲（推薦使用）⭐
├── base_crawler.py             # 基礎爬蟲類別
├── README.md                   # 本文檔
├── 快速開始.md                  # 5分鐘上手指南
└── README_更新說明.md           # 詳細API文檔
```

舊版與實驗性質的爬蟲（shidian_selenium、smart_crawler、taoism_crawler 等）
及其說明文件已封存到 `archive/crawler_experiments/`。

## 🎯 主要爬蟲：shidian_crawler.py

這是目前最完整、最穩定的爬蟲工具。

### 核心特點

- ✅ **100% 成功率** - 測試於 DZ1422, DZ1439
- ✅ **自動化流程** - 爬取 → 保存 → 生成模板
- ✅ **完整日誌** - 詳細的執行記錄
- ✅ **錯誤處理** - 完善的異常處理機制
- ✅ **批量支援** - 可批量爬取多本書籍

### 使用方法

#### 1. 爬取單本書籍

```python
from crawler.shidian_crawler import ShidianCrawler

crawler = ShidianCrawler()
book = crawler.crawl_book('DZ1422')
```

#### 2. 批量爬取

```python
from crawler.shidian_crawler import ShidianCrawler

crawler = ShidianCrawler(delay=3)
book_ids = ['DZ1422', 'DZ1439', 'DZ1234']
results = crawler.batch_crawl(book_ids)
```

#### 3. 不生成翻譯模板

```python
from crawler.shidian_crawler import ShidianCrawler

crawler = ShidianCrawler()
book = crawler.crawl_book('DZ1422', generate_templates=False)
```

## 📊 輸出結構

```
Taoism/
├── docs/
│   ├── source_texts/          # 原文
│   │   └── 書名/
│   │       ├── 00_書籍資訊.txt
│   │       └── 01_章節.txt
│   │
│   └── translations/          # 翻譯模板
│       └── 書名/
│           ├── README.md      # 專案說明
│           └── 01_章節.md     # 翻譯模板
│
└── data/
    └── crawled/               # JSON資料
        └── DZ1422_書名.json
```

## 🎓 使用文檔

### 新手入門
1. **快速開始.md** - 5分鐘快速上手
2. **README_更新說明.md** - 詳細API文檔

### 進階使用
- 查看 `shidian_crawler.py` 原始碼

## 📈 測試結果

### DZ1422 枕中經
- ✅ 章節數: 1 章
- ✅ 總字數: 853 字
- ✅ 成功率: 100%

### DZ1439 洞玄靈寶玉京山步虛經
- ✅ 章節數: 7 章
- ✅ 總字數: 3,502 字
- ✅ 成功率: 100%

## 🔧 API 參考

### ShidianCrawler 類別

```python
class ShidianCrawler:
    def __init__(self, delay=2)
    def get_book_info(self, book_id)
    def get_chapter_content(self, chapter_url, chapter_name="")
    def crawl_all_chapters(self, book_info)
    def crawl_book(self, book_id, generate_templates=True)
    def save_to_json(self, book_info, output_dir='data/crawled')
    def save_to_text_files(self, book_info, output_dir=None)
    def generate_translation_templates(self, book_info, output_dir=None)
    def batch_crawl(self, book_ids, output_dir='data/crawled')
    def print_statistics(self, book_info)
```

詳細說明請參考 `README_更新說明.md`

## 🎯 如何找到書籍編號

從師典古籍網站的 URL 中找：

```
https://www.shidianguji.com/book/DZ1422
                                  ^^^^^^
                                  書籍編號
```

## ⚙️ 配置選項

### 延遲時間

```python
# 預設 2 秒（推薦）
crawler = ShidianCrawler(delay=2)

# 批量爬取建議 3 秒
crawler = ShidianCrawler(delay=3)
```

### 輸出目錄

```python
# 使用預設目錄
crawler.save_to_text_files(book)
crawler.generate_translation_templates(book)

# 自訂目錄
crawler.save_to_text_files(book, 'my_output/texts')
crawler.generate_translation_templates(book, 'my_output/translations')
```

## 📝 完整範例

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整的爬蟲使用範例
"""

from crawler.shidian_crawler import ShidianCrawler

def main():
    # 1. 建立爬蟲
    crawler = ShidianCrawler(delay=2)
    
    # 2. 爬取書籍
    book = crawler.crawl_book('DZ1422')
    
    # 3. 查看結果
    if book:
        crawler.print_statistics(book)
        print(f"\n✓ 完成！")
        print(f"原文: docs/source_texts/{book['title']}/")
        print(f"翻譯: docs/translations/{book['title']}/")

if __name__ == "__main__":
    main()
```

## ❓ 常見問題

### Q1: 爬取失敗怎麼辦？

**A:** 檢查：
1. 網路連線是否正常
2. 書籍編號是否正確
3. 查看日誌: `data/logs/shidian_crawler.log`

### Q2: 翻譯模板沒有生成？

**A:** 確認參數設定：
```python
book = crawler.crawl_book('DZ1422', generate_templates=True)
```

### Q3: 可以批量爬取嗎？

**A:** 可以！
```python
results = crawler.batch_crawl(['DZ1422', 'DZ1439'])
```

## ⚠️ 注意事項

1. **網路穩定** - 確保網路連線穩定
2. **請求頻率** - 不要設定過短的延遲（最低 1 秒）
3. **磁碟空間** - 確保有足夠空間儲存結果
4. **版權尊重** - 僅供學習研究使用

## 🔄 舊版工具說明

舊版爬蟲工具（`shidian_selenium.py`、`smart_crawler.py`、`taoism_crawler.py` 等）
已封存到 `archive/crawler_experiments/`，新專案請使用 `shidian_crawler.py`。

## 📚 相關文檔

- [快速開始指南](快速開始.md) - 5分鐘上手
- [詳細API文檔](README_更新說明.md) - 完整API說明

## 🎉 開始使用

```bash
# 立即開始
python crawler/shidian_crawler.py
```

或查看 [快速開始指南](快速開始.md) 了解更多。

---

**模組版本**: v2.0  
**更新時間**: 2025-10-20  
**測試狀態**: ✅ 通過  
**維護狀態**: ✅ 活躍維護  
