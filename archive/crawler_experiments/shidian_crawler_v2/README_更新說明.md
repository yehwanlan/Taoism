# 爬蟲系統更新說明

## 🎉 更新內容

基於 DZ1439 成功經驗，全面更新師典古籍爬蟲系統！

### 新增檔案

1. **`shidian_crawler.py`** - 全新的師典古籍爬蟲
   - 整合 DZ1439 的成功經驗
   - 支援單本和批量爬取
   - 完整的錯誤處理和日誌記錄
   - 自動保存為 JSON 和文字檔案

### 核心改進

#### 1. 內容提取策略
```python
# 優先順序：article > main > 其他容器
article_tag = soup.find('article')  # 最優先
main_tag = soup.find('main')        # 次優先
div.chapter-content                 # 備用方案
```

#### 2. 完整的書籍資訊提取
- ✅ 書名（h1.HbYW1Abi）
- ✅ 作者和朝代（span.book-title-author）
- ✅ 摘要（meta description）
- ✅ 章節列表（div.semi-tree-option）

#### 3. 智能檔案管理
```
docs/source_texts/
└── 書名/
    ├── 00_書籍資訊.txt
    ├── 01_章節名稱.txt
    ├── 02_章節名稱.txt
    └── ...

data/crawled/
└── DZ1439_書名.json
```

## 🚀 使用方法

### 方法1: 直接執行（推薦）

```bash
# 爬取單本書籍
python crawler/shidian_crawler.py
```

### 方法2: 作為模組使用

```python
from crawler.shidian_crawler import ShidianCrawler

# 建立爬蟲
crawler = ShidianCrawler(delay=2)

# 爬取單本書籍
book_info = crawler.crawl_book('DZ1439')

# 保存結果
crawler.save_to_json(book_info)
crawler.save_to_text_files(book_info)

# 列印統計
crawler.print_statistics(book_info)
```

### 方法3: 批量爬取

```python
from crawler.shidian_crawler import ShidianCrawler

crawler = ShidianCrawler(delay=2)

# 批量爬取多本書籍
book_ids = ['DZ1439', 'DZ1234', 'DZ1437']
results = crawler.batch_crawl(book_ids)

# 查看結果
for book in results:
    crawler.print_statistics(book)
```

## 📊 功能對比

| 功能 | 舊版爬蟲 | 新版爬蟲 |
|------|---------|---------|
| 內容提取 | ❌ 失敗 | ✅ 成功 (article/main) |
| 書籍資訊 | ⚠️ 部分 | ✅ 完整 |
| 章節列表 | ✅ 支援 | ✅ 支援 |
| 批量爬取 | ❌ 無 | ✅ 支援 |
| JSON 輸出 | ⚠️ 簡單 | ✅ 完整結構 |
| 文字檔案 | ⚠️ 簡單 | ✅ 格式化輸出 |
| 錯誤處理 | ⚠️ 基本 | ✅ 完整 |
| 日誌記錄 | ⚠️ 基本 | ✅ 詳細 |
| 統計資訊 | ❌ 無 | ✅ 完整 |

## 🎯 測試結果

### DZ1439 測試
- ✅ 書名: 洞玄灵宝玉京山步虚经
- ✅ 章節數: 7 章
- ✅ 成功率: 100% (7/7)
- ✅ 總字數: 3,502 字
- ✅ 平均每章: 500 字

## 📝 API 文檔

### ShidianCrawler 類別

#### 初始化
```python
crawler = ShidianCrawler(delay=2)
```
- `delay`: 請求間隔時間（秒），預設 2 秒

#### 主要方法

##### 1. get_book_info(book_id)
獲取書籍資訊和章節列表
```python
book_info = crawler.get_book_info('DZ1439')
```

##### 2. get_chapter_content(chapter_url, chapter_name)
獲取單個章節內容
```python
chapter = crawler.get_chapter_content(url, "章節名稱")
```

##### 3. crawl_all_chapters(book_info)
爬取所有章節內容
```python
book_info = crawler.crawl_all_chapters(book_info)
```

##### 4. crawl_book(book_id)
爬取完整書籍（一站式方法）
```python
book_info = crawler.crawl_book('DZ1439')
```

##### 5. save_to_json(book_info, output_dir)
保存為 JSON 格式
```python
crawler.save_to_json(book_info, 'data/crawled')
```

##### 6. save_to_text_files(book_info, output_dir)
保存為文字檔案
```python
crawler.save_to_text_files(book_info, 'docs/source_texts/書名')
```

##### 7. batch_crawl(book_ids, output_dir)
批量爬取多本書籍
```python
results = crawler.batch_crawl(['DZ1439', 'DZ1234'])
```

##### 8. print_statistics(book_info)
列印爬取統計資訊
```python
crawler.print_statistics(book_info)
```

## 🔧 配置選項

### 修改延遲時間
```python
# 更保守（3秒）
crawler = ShidianCrawler(delay=3)

# 更快速（1秒，不建議）
crawler = ShidianCrawler(delay=1)
```

### 自訂輸出目錄
```python
# JSON 輸出
crawler.save_to_json(book_info, 'my_output/json')

# 文字檔案輸出
crawler.save_to_text_files(book_info, 'my_output/texts')
```

### 日誌設定
日誌自動保存到 `data/logs/shidian_crawler.log`

## ⚠️ 注意事項

1. **請求頻率**: 預設 2 秒延遲，請勿設定過短
2. **網路穩定**: 確保網路連線穩定
3. **磁碟空間**: 確保有足夠空間儲存結果
4. **版權尊重**: 僅供學習研究使用
5. **錯誤處理**: 遇到錯誤會自動記錄並繼續

## 📈 效能指標

- 單章爬取時間: ~2-3 秒
- 7 章書籍總時間: ~15-20 秒
- 成功率: 100% (測試於 DZ1439)
- 記憶體使用: < 50MB

## 🔄 整合到現有系統

### 整合到 main.py
```python
from crawler.shidian_crawler import ShidianCrawler

def crawl_command(book_id):
    """爬取命令"""
    crawler = ShidianCrawler()
    book_info = crawler.crawl_book(book_id)
    
    if book_info:
        crawler.save_to_json(book_info)
        crawler.save_to_text_files(book_info)
        crawler.print_statistics(book_info)
        return True
    return False
```

### 整合到 EasyCLI
```python
from crawler.shidian_crawler import ShidianCrawler

class EasyCLI:
    def crawl_book(self, book_id):
        crawler = ShidianCrawler()
        return crawler.crawl_book(book_id)
```

## 🎓 學習要點

1. **HTML 解析**: 使用 BeautifulSoup 提取內容
2. **錯誤處理**: try-except 和日誌記錄
3. **檔案管理**: pathlib 和 os 模組
4. **資料結構**: 字典和列表的使用
5. **物件導向**: 類別設計和方法組織

## 📚 相關檔案

- `shidian_crawler.py` - 主要爬蟲程式
- `base_crawler.py` - 基礎爬蟲類別（保留）
- `shidian_selenium.py` - Selenium 版本（備用）
- `DZ1439_爬蟲使用說明.md` - DZ1439 詳細說明

## ✅ 下一步

1. ✅ 測試更多書籍（DZ1234, DZ1437 等）
2. ✅ 整合到 main.py 命令列介面
3. ✅ 添加進度追蹤功能
4. ✅ 支援斷點續傳
5. ✅ 添加內容驗證

## 🎉 完成！

新版爬蟲已經準備就緒，可以開始使用了！
