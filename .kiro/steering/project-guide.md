# 道教經典翻譯專案開發指南

## 專案概述
這是一個道教經典翻譯專案，旨在建立線上平台展示道教經典原文及現代中文翻譯。

## 開發原則
- 使用繁體中文進行翻譯
- 保持原文與譯文的對照格式
- 採用 Markdown 格式編寫翻譯內容
- 使用 Python 腳本自動化管理經文列表

## 檔案結構說明
- `docs/source_texts/`: 存放原始道教經典文本
- `docs/translations/`: 存放翻譯後的現代中文白話文本（.md 格式）
- `docs/`: 網頁相關檔案
- `generate_scriptures_js.py`: 自動生成經文列表的腳本

## 工作流程
1. 新增原始經文到 `docs/source_texts/`
2. 建立對應的翻譯檔案到 `docs/translations/`
3. 執行 `python generate_scriptures_js.py` 更新網頁
4. 使用 `python -m http.server 8000` 本地預覽

## 程式碼風格
- Python: 遵循 PEP 8 標準
- JavaScript: 使用現代 ES6+ 語法
- HTML/CSS: 保持語義化和可讀性