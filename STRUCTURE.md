# 📁 專案結構總覽

## 🏗️ 整理後的目錄結構

```
Taoism/
├── 📁 .git/                    # Git 版本控制
├── 📁 .github/                 # GitHub 配置
│   └── workflows/              # GitHub Actions
├── 📁 .history/                # 歷史記錄
├── 📁 .vscode/                 # VS Code 配置
├── 📁 archive/                 # 歸檔檔案
│   └── v1_backup_20250809_033258/  # v1.x 版本備份
├── 📁 backup/                  # 備份檔案
├── 📁 config/                  # 配置管理
│   ├── templates/              # 模板檔案
│   ├── ai_translation_guidelines.md
│   ├── hidden_chapters.json
│   ├── settings.example.json
│   └── settings.json
├── 📁 core/                    # 核心系統模組
│   ├── __init__.py
│   ├── ai_engine.py           # AI 翻譯引擎
│   ├── file_monitor.py        # 檔案監控系統
│   ├── tracker.py             # 經典追蹤系統
│   ├── translator.py          # 翻譯引擎核心
│   └── unicode_handler.py     # Unicode 處理
├── 📁 crawler/                 # 爬蟲工具集
│   ├── 21個專業爬蟲工具
│   └── 詳細說明文檔
├── 📁 data/                    # 資料儲存
│   ├── logs/                  # 日誌檔案
│   │   ├── activity_report.md
│   │   ├── file_operations.json
│   │   └── file_operations_tools_backup.json
│   ├── tracking/              # 追蹤資料
│   │   ├── classics.json      # 經典資料庫
│   │   ├── system_status.json # 系統狀態
│   │   └── tracking_report.md # 追蹤報告
│   └── books.json             # 書籍配置
├── 📁 docs/                    # 文檔和輸出
│   ├── css/                   # 網頁樣式
│   ├── js/                    # 網頁腳本
│   ├── olddocs/               # 舊版文檔
│   ├── source_texts/          # 原文檔案（23部經典）
│   ├── system/                # 系統文檔
│   │   ├── AI翻譯使用指南.md
│   │   ├── AI翻譯工作流程.md
│   │   ├── AI翻譯指導規範.md
│   │   ├── README.md
│   │   ├── UPGRADE_SUMMARY.md
│   │   ├── 使用示例.md
│   │   ├── 工具使用指南.md
│   │   ├── 環境設定指南.md
│   │   ├── 網頁使用說明.md
│   │   ├── 資料流程說明.md
│   │   ├── 追蹤系統說明.md
│   │   ├── 升級規劃_中期.md
│   │   ├── 升級規劃_短期.md
│   │   └── 升級規劃_長期.md
│   ├── translations/          # 翻譯檔案（188個章節）
│   ├── index.html             # 主要網頁介面
│   └── web_data_report.md
├── 📁 tools/                   # 命令列工具集
│   ├── temp/                  # 臨時工具檔案（已整理）
│   │   ├── check_dependencies.py
│   │   ├── check_translation_progress.py
│   │   ├── clear_cache_and_test.py
│   │   ├── emergency_fix.py
│   │   ├── fix_all_imports.py
│   │   ├── generate_templates.py
│   │   ├── quick_fix.py
│   │   ├── simple_translator.py
│   │   ├── temp_test_encoding.py
│   │   ├── test_*.py (多個測試檔案)
│   │   └── update_web_data.py
│   ├── ai_taoismRule.md
│   ├── ai_translation_evaluator.py
│   ├── ai_translator.py
│   ├── easy_cli.py            # 簡易翻譯介面
│   ├── monitor_cli.py         # 監控介面
│   └── 其他專業工具...
├── .gitignore                 # Git 忽略規則
├── LICENSE                    # 授權條款
├── main.py                    # 🚀 主要入口點
├── PROJECT_OVERVIEW.md        # 專案概述
├── README.md                  # 詳細說明
├── requirements.txt           # Python 依賴
└── setup.py                   # 安裝配置
```

## 🎯 核心檔案說明

### 主要入口
- `main.py` - 統一的命令列介面
- `docs/index.html` - 網頁閱讀介面

### 核心模組
- `core/translator.py` - 翻譯引擎
- `core/tracker.py` - 追蹤系統
- `core/ai_engine.py` - AI 翻譯引擎

### 工具集
- `tools/easy_cli.py` - 簡易翻譯工具
- `tools/monitor_cli.py` - 監控工具
- `crawler/` - 21個專業爬蟲工具

### 資料管理
- `data/tracking/classics.json` - 經典資料庫
- `config/settings.json` - 系統配置
- `docs/source_texts/` - 原文檔案
- `docs/translations/` - 翻譯檔案

## 📊 統計資訊

- **經典總數**: 23部
- **章節總數**: 188章
- **核心模組**: 5個
- **工具檔案**: 30+個
- **爬蟲工具**: 21個
- **系統文檔**: 15個

## 🧹 整理完成項目

✅ **根目錄清理** - 移除15個臨時檔案
✅ **目錄結構優化** - 合併重複的資料目錄
✅ **檔案分類** - 按功能分類到對應目錄
✅ **備份保護** - 重要檔案已備份
✅ **文檔整理** - 升級規劃移至系統文檔
✅ **Git 配置更新** - 更新忽略規則

## 🎯 使用建議

1. **開發時** - 使用 `main.py` 作為統一入口
2. **網頁閱讀** - 開啟 `docs/index.html`
3. **工具開發** - 在 `tools/` 目錄下工作
4. **臨時測試** - 使用 `tools/temp/` 目錄
5. **文檔查閱** - 參考 `docs/system/` 目錄

---
*整理完成時間: 2025-08-18*