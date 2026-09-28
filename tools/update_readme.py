#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新README文件，正確顯示所有章節
"""

from pathlib import Path
import re
import sys

# 讓 `python tools/xxx.py` 也能找到 core 套件
sys.path.append(str(Path(__file__).parent.parent))
from core.unicode_handler import safe_print


def update_readme():
    """更新README文件"""
    book_folder = Path("../docs/source_texts/太上洞玄灵宝业报因缘经_DZ0336")
    readme_path = book_folder / "README.md"
    source_folder = book_folder / "原文"
    
    # 獲取所有文件並排序
    files = sorted(source_folder.glob("*.txt"))
    
    # 提取章節信息
    chapters = []
    for file_path in files:
        filename = file_path.stem
        # 提取編號和標題
        match = re.match(r'(\d+)_(.+)', filename)
        if match:
            number = int(match.group(1))
            title = match.group(2)
            
            # 讀取文件第一行來獲取實際的品名
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 尋找品名
                    lines = content.split('\n')
                    actual_title = title  # 默認使用文件名中的標題
                    
                    for line in lines[1:10]:  # 檢查前幾行
                        line = line.strip()
                        if '品第' in line and len(line) < 20:
                            actual_title = line
                            break
                        elif line and len(line) < 50 and '太上洞玄' not in line and line != title:
                            # 可能是章節標題
                            if not line.startswith('#'):
                                actual_title = line
                                break
                    
                    chapters.append((number, actual_title))
            except Exception:
                chapters.append((number, title))
    
    # 生成新的README內容
    readme_content = f"""# 太上洞玄灵宝业报因缘经

## 書籍資訊

- **書名**：太上洞玄灵宝业报因缘经
- **作者**：[唐] 佚名 著
- **書籍ID**：DZ0336
- **原始網址**：https://www.shidianguji.com/book/DZ0336?page_from=bookshelf&mode=book

## 專案說明

本專案使用道教經典翻譯系統生成，包含：
1. 自動爬取的古文原文
2. 自動生成的翻譯模板
3. 完整的專案結構

## 章節列表

總共 {len(chapters)} 個章節：

"""
    
    # 添加章節列表
    for number, title in chapters:
        readme_content += f"- {number:02d}. {title}\n"
    
    readme_content += f"""

## 結構說明

根據經典描述，本書結構如下：
- **首為《开度品》** - 第一品
- **次為《善对》《恶报》《受罪》三品** - 第二、三、四品
- **再次為《忏悔》《奉戒》等八品** - 第五、六品等
- **再次《生神》《弘教》等九品** - 後續各品

本次修復成功找回了所有缺失的品（章節），現在包含完整的{len(chapters)}個章節。

## 使用說明

1. **原文檔案**：位於 `原文/` 目錄
2. **翻譯檔案**：位於 `../translations/太上洞玄灵宝业报因缘经_DZ0336/` 目錄
3. **翻譯模板**：已自動生成，可直接編輯

## 翻譯進度

- [x] 原文爬取完成（{len(chapters)}個章節）
- [x] 翻譯模板生成完成
- [ ] 人工翻譯待完成

## 修復記錄

- **2025-08-10**: 發現並修復了缺失章節問題
- **修復前**: 只有11個文件，缺少具體的品的內容
- **修復後**: 完整的{len(chapters)}個章節，包含所有品的詳細內容
- **修復工具**: 使用專門的DZ0336結構修復腳本

---
*專案建立時間：2025-08-10 01:11:22*
*最後更新時間：2025-08-10*
*使用工具：道教經典翻譯系統 v2.0*
"""
    
    # 寫入README
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    safe_print(f"✅ README已更新，包含{len(chapters)}個章節")
    
    # 顯示章節列表預覽
    safe_print("\n📋 章節列表預覽:")
    for number, title in chapters[:10]:  # 只顯示前10個
        safe_print(f"  {number:02d}. {title}")
    if len(chapters) > 10:
        safe_print(f"  ... 還有 {len(chapters) - 10} 個章節")


if __name__ == "__main__":
    update_readme()