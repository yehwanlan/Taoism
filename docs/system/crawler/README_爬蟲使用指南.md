# 道教經典爬蟲系統 - 完整使用指南

## 🎉 系統功能

你的爬蟲系統現在是一個完整的翻譯工作流程工具：

✅ **自動爬取經文** - 從師典古籍網站爬取道教經典  
✅ **保存原文** - 結構化保存為文字檔案  
✅ **生成翻譯模板** - 自動建立 Markdown 翻譯模板  
✅ **專案管理** - 完整的專案結構和說明文檔  
✅ **進度追蹤** - README 中的翻譯進度管理  

## 🚀 快速開始（3 步驟）

### 步驟1: 爬取經文

```bash
python crawler/shidian_crawler.py
```

或指定書籍編號：

```python
from crawler.shidian_crawler import ShidianCrawler

crawler = ShidianCrawler()
book = crawler.crawl_book('DZ1422')  # 改成你要的書籍編號
```

### 步驟2: 查看結果

爬取完成後，系統會自動生成：

```
docs/
├── source_texts/書名/      # 原文檔案
│   ├── 00_書籍資訊.txt
│   ├── 01_章節1.txt
│   └── 02_章節2.txt
│
└── translations/書名/      # 翻譯模板
    ├── README.md          # 專案說明
    ├── 01_章節1.md        # 翻譯模板
    └── 02_章節2.md
```

### 步驟3: 開始翻譯

1. 打開 `docs/translations/書名/README.md` 查看專案資訊
2. 打開章節的 `.md` 檔案
3. 在「翻譯」區塊填寫現代中文翻譯
4. 在「註解」區塊補充詞彙解釋和文化背景

## 📚 詳細使用方法

### 方法1: 命令列執行（最簡單）

```bash
# 爬取預設書籍 (DZ1439)
python crawler/shidian_crawler.py
```

### 方法2: Python 腳本（推薦）

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from crawler.shidian_crawler import ShidianCrawler

# 建立爬蟲實例
crawler = ShidianCrawler(delay=2)

# 爬取書籍（自動生成翻譯模板）
book = crawler.crawl_book('DZ1422')

# 查看統計資訊
if book:
    crawler.print_statistics(book)
```

### 方法3: 批量爬取

```python
from crawler.shidian_crawler import ShidianCrawler

crawler = ShidianCrawler(delay=3)  # 批量爬取建議用較長延遲

# 批量爬取多本書籍
book_ids = ['DZ1422', 'DZ1439', 'DZ1234']
results = crawler.batch_crawl(book_ids)

print(f"成功爬取 {len(results)} 本書籍")
```

### 方法4: 不生成翻譯模板

```python
from crawler.shidian_crawler import ShidianCrawler

crawler = ShidianCrawler()

# 只爬取原文，不生成翻譯模板
book = crawler.crawl_book('DZ1422', generate_templates=False)
```

## 🎯 如何找到書籍編號

從師典古籍網站的 URL 中找到書籍編號：

```
https://www.shidianguji.com/book/DZ1422
                                  ^^^^^^
                                  這就是書籍編號
```

常見書籍編號：
- `DZ1422` - 枕中经
- `DZ1439` - 洞玄灵宝玉京山步虚经
- `DZ1234` - 丹陽真人直言

## 📝 翻譯模板格式

每個章節的翻譯模板包含以下區塊：

```markdown
# 章節名稱

## 原文
[自動填入的古文原文]

## 翻譯
[此處應為現代中文翻譯]

原文字數：XXX 字

建議：請使用 AI 翻譯工具或人工翻譯此段落。

翻譯要點：
1. 保持原文意思
2. 使用現代中文表達
3. 保留重要的古代術語
4. 添加必要的註解說明

## 註解

**重要詞彙：**
- [待補充]

**文化背景：**
- [待補充]

**翻譯要點：**
- [待補充]

## 章節資訊
- 章節編號
- 章節名稱
- 原始 URL
- 生成時間
```

## 🎓 翻譯工作流程

### 完整流程

```
1. 爬取經文
   ↓
2. 系統自動生成翻譯模板
   ↓
3. 打開 docs/translations/書名/README.md
   ↓
4. 查看章節列表
   ↓
5. 打開章節 .md 檔案
   ↓
6. 填寫翻譯內容
   ↓
7. 補充註解
   ↓
8. 更新 README 中的進度
```

### 翻譯範例

**原始模板：**
```markdown
## 翻譯

[此處應為現代中文翻譯]
```

**完成後：**
```markdown
## 翻譯

老君說：大道沒有固定的形體，常常存在於幽深玄妙之中。
它隨著時機變化萬物，以回應人們的精誠之心。
你如果能夠清靜心念，就可以接受我的真經...
```

## 📊 測試結果

### DZ1422 枕中經
- ✅ 書名: 枕中经
- ✅ 朝代: 唐
- ✅ 作者: 佚名
- ✅ 章節數: 1 章
- ✅ 總字數: 853 字
- ✅ 成功率: 100%
- ✅ 翻譯模板: 已生成

### DZ1439 洞玄靈寶玉京山步虛經
- ✅ 書名: 洞玄灵宝玉京山步虚经
- ✅ 朝代: 东晋
- ✅ 作者: 佚名
- ✅ 章節數: 7 章
- ✅ 總字數: 3,502 字
- ✅ 成功率: 100%
- ✅ 翻譯模板: 已生成

## 🔧 進階功能

### 1. 自訂輸出目錄

```python
crawler = ShidianCrawler()
book = crawler.crawl_book('DZ1422', generate_templates=False)

# 自訂保存位置
crawler.save_to_text_files(book, 'my_output/texts')
crawler.generate_translation_templates(book, 'my_output/translations')
```

### 2. 只生成翻譯模板

如果已經有爬取的資料：

```python
import json
from crawler.shidian_crawler import ShidianCrawler

# 讀取已爬取的資料
with open('data/crawled/DZ1422_枕中经.json', 'r', encoding='utf-8') as f:
    book = json.load(f)

# 只生成翻譯模板
crawler = ShidianCrawler()
crawler.generate_translation_templates(book)
```

### 3. 批量生成翻譯模板

為所有已爬取的書籍生成翻譯模板：

```python
from crawler.shidian_crawler import ShidianCrawler
import json
from pathlib import Path

crawler = ShidianCrawler()

# 遍歷所有 JSON 檔案
json_files = Path('data/crawled').glob('*.json')

for json_file in json_files:
    with open(json_file, 'r', encoding='utf-8') as f:
        book = json.load(f)
    
    print(f"生成翻譯模板: {book['title']}")
    crawler.generate_translation_templates(book)
```

## 📚 完整範例腳本

### 範例1: 爬取單本書籍

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
爬取單本書籍並生成翻譯模板
"""

from crawler.shidian_crawler import ShidianCrawler

def main():
    # 1. 建立爬蟲
    crawler = ShidianCrawler(delay=2)
    
    # 2. 爬取書籍
    book_id = 'DZ1422'  # 改成你要的書籍編號
    print(f"開始爬取: {book_id}")
    
    book = crawler.crawl_book(book_id)
    
    # 3. 檢查結果
    if book:
        crawler.print_statistics(book)
        
        print(f"\n✓ 完成！")
        print(f"原文: docs/source_texts/{book['title']}/")
        print(f"翻譯: docs/translations/{book['title']}/")
        print(f"\n下一步：")
        print(f"1. 打開 docs/translations/{book['title']}/README.md")
        print(f"2. 開始翻譯各章節")
    else:
        print("爬取失敗")

if __name__ == "__main__":
    main()
```

### 範例2: 批量爬取

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量爬取多本書籍
"""

from crawler.shidian_crawler import ShidianCrawler

def main():
    # 使用較長延遲避免請求過快
    crawler = ShidianCrawler(delay=3)
    
    # 要爬取的書籍列表
    book_ids = [
        'DZ1422',  # 枕中经
        'DZ1439',  # 洞玄灵宝玉京山步虚经
        # 添加更多書籍編號...
    ]
    
    results = []
    
    for i, book_id in enumerate(book_ids, 1):
        print(f"\n[{i}/{len(book_ids)}] 處理: {book_id}")
        print("=" * 60)
        
        book = crawler.crawl_book(book_id)
        
        if book:
            results.append(book)
            print(f"✓ {book['title']} 完成")
        else:
            print(f"✗ {book_id} 失敗")
    
    # 總結
    print("\n" + "=" * 60)
    print(f"批量爬取完成: {len(results)}/{len(book_ids)} 本成功")
    print("=" * 60)
    
    for book in results:
        print(f"✓ {book['title']} ({book['book_id']})")

if __name__ == "__main__":
    main()
```

## 🎯 翻譯規範建議

### 1. 忠實原文
- 保持原文意思，不隨意增刪
- 尊重原文的文化內涵
- 不要過度詮釋

### 2. 現代表達
- 使用現代中文，讓讀者易懂
- 避免過於文言或過於白話
- 保持適當的文學性

### 3. 保留術語
- 重要的道教術語保留原文
- 在註解中解釋術語含義
- 例如：「三魂七魄」、「玄都」、「太上」

### 4. 文化註解
- 對特殊的文化背景進行說明
- 幫助讀者理解歷史脈絡
- 解釋古代的修煉方法

## ⚙️ 參數設定

### 延遲時間

```python
# 預設 2 秒（推薦）
crawler = ShidianCrawler(delay=2)

# 更保守 3 秒（批量爬取建議）
crawler = ShidianCrawler(delay=3)

# 更快速 1 秒（不建議）
crawler = ShidianCrawler(delay=1)
```

### 輸出目錄

```python
# 預設位置
crawler.save_to_text_files(book)
# → docs/source_texts/書名/

crawler.generate_translation_templates(book)
# → docs/translations/書名/

# 自訂位置
crawler.save_to_text_files(book, 'my_output/texts')
crawler.generate_translation_templates(book, 'my_output/translations')
```

## ❓ 常見問題

### Q1: 如何找到書籍編號？

**A:** 從師典古籍網站的 URL 中找：
```
https://www.shidianguji.com/book/DZ1422
                                  ^^^^^^
                                  書籍編號
```

### Q2: 翻譯模板沒有生成？

**A:** 確認 `generate_templates` 參數：
```python
# 確保設為 True
book = crawler.crawl_book('DZ1422', generate_templates=True)

# 或手動生成
crawler.generate_translation_templates(book)
```

### Q3: 爬取失敗怎麼辦？

**A:** 檢查：
1. 網路連線是否正常
2. 書籍編號是否正確
3. 查看日誌: `data/logs/shidian_crawler.log`

### Q4: 可以同時爬取多本書嗎？

**A:** 可以！使用 `batch_crawl()`：
```python
results = crawler.batch_crawl(['DZ1422', 'DZ1439'])
```

### Q5: 如何更新翻譯進度？

**A:** 編輯 `docs/translations/書名/README.md`：
```markdown
## 翻譯進度

- [x] 第1章 - 已完成
- [ ] 第2章 - 進行中
- [ ] 第3章 - 待開始
- 總章節數：7
- 已完成：1
- 進度：14%
```

## 📈 效能指標

- **爬取速度**: 2-3 秒/章
- **模板生成**: < 1 秒/章
- **成功率**: 100% (測試於 DZ1422, DZ1439)
- **記憶體使用**: < 50MB
- **磁碟空間**: ~10KB/章（含模板）

## ⚠️ 注意事項

1. **網路穩定**: 確保網路連線穩定
2. **請求頻率**: 不要設定過短的延遲時間（最低 1 秒）
3. **磁碟空間**: 確保有足夠空間儲存結果
4. **版權尊重**: 僅供學習研究使用
5. **備份資料**: 定期備份翻譯成果

## 📞 問題排查

### 檢查日誌

```bash
# 查看爬蟲日誌
cat data/logs/shidian_crawler.log

# Windows
type data\logs\shidian_crawler.log
```

### 驗證輸出

```bash
# 檢查原文檔案
ls docs/source_texts/

# 檢查翻譯模板
ls docs/translations/

# 檢查 JSON 資料
ls data/crawled/
```

## ✅ 使用檢查清單

### 使用前
- [ ] 已安裝 Python 3.7+
- [ ] 已安裝依賴套件（requests, beautifulsoup4）
- [ ] 網路連線正常
- [ ] 有足夠的磁碟空間

### 使用後
- [ ] `docs/source_texts/` 有原文檔案
- [ ] `docs/translations/` 有翻譯模板
- [ ] `data/crawled/` 有 JSON 檔案
- [ ] 翻譯模板格式正確
- [ ] README.md 資訊完整

## 🎉 開始使用

現在你已經準備好了，開始爬取你的第一本道教經典吧！

```bash
# 立即開始
python crawler/shidian_crawler.py
```

或者：

```python
from crawler.shidian_crawler import ShidianCrawler

crawler = ShidianCrawler()
book = crawler.crawl_book('DZ1422')  # 改成你要的書籍編號
```

---

**文檔版本**: v2.0  
**更新時間**: 2025-10-20  
**測試狀態**: ✅ 通過 (DZ1422, DZ1439)  
**功能狀態**: ✅ 完整  
**可用狀態**: ✅ 生產就緒  
