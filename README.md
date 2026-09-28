# 🏛️ 道教經典翻譯系統 v2.0

## 🎯 專案概述

道教經典翻譯系統是一個全自動化的古籍翻譯和管理平台，專門用於處理道教經典的爬取、翻譯和追蹤。系統採用模組化設計，提供完整的CLI介面和實時監控功能。

### ✨ 核心特色

- 🤖 **全自動翻譯** - 一鍵完成從URL到翻譯模板的完整流程
- 📊 **智能追蹤** - 自動記錄和統計所有經典資訊
- 🔍 **實時監控** - 檔案操作和翻譯進度的即時追蹤
- 🎛️ **統一介面** - 簡潔的命令列介面，支援互動模式
- 📈 **詳細報告** - 自動生成統計報告和進度分析

## 🎯 主要功能

- 🕷️ **智能爬蟲** - 自動識別和爬取古籍網站內容
- 🤖 **自動翻譯** - 生成標準化的翻譯模板
- 📊 **進度追蹤** - 實時監控翻譯進度和統計
- 📁 **檔案管理** - 自動組織原文和翻譯檔案
- 📈 **報告生成** - 詳細的統計報告和分析
- 🎛️ **CLI介面** - 簡潔易用的命令列操作
- 🌐 **網頁介面** - 現代化的網頁閱讀介面，支援書籍和章節選擇
- 🤖 **AI翻譯指導** - 專業的AI翻譯規範和品質評估系統

## 🏗️ 系統架構

```
Taoism/
├── 📁 core/                    # 核心系統模組
│   ├── translator.py           # 翻譯引擎核心
│   ├── tracker.py             # 經典追蹤系統
│   ├── file_monitor.py        # 檔案監控系統
│   └── __init__.py            # 模組初始化
│
├── 📁 tools/                   # 命令列工具集
│   ├── easy_cli.py            # 簡易翻譯介面
│   ├── monitor_cli.py         # 監控介面
│   └── folder_manager.py      # 資料夾管理工具
│
├── 📁 config/                  # 配置管理
│   ├── settings.json          # 系統配置檔案
│   └── templates/             # 模板檔案
│
├── 📁 data/                    # 資料儲存
│   ├── tracking/              # 追蹤資料
│   │   ├── classics.json      # 經典資料庫
│   │   └── tracking_report.md # 追蹤報告
│   └── logs/                  # 日誌檔案
│       ├── file_operations.json # 檔案操作日誌
│       └── activity_report.md   # 活動報告
│
├── 📁 docs/                    # 文檔和輸出
│   ├── source_texts/          # 原文檔案
│   ├── translations/          # 翻譯檔案
│   └── system/                # 系統文檔
│       ├── 工具使用指南.md     # 詳細使用指南
│       ├── 追蹤系統說明.md     # 追蹤系統說明
│       └── UPGRADE_SUMMARY.md # 升級總結報告
│   └── translations/          # 翻譯檔案
│
├── 📁 archive/                 # 封存的舊程式（說明見 archive/README.md）
│
├── main.py                     # 🚀 主要入口點
└── README.md                   # 專案說明
```

## 🚀 快速開始

### 1. 環境準備

```bash
# 確保已安裝 Python 3.7+
python --version

# 建立虛擬環境（推薦）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安裝依賴套件
pip install -r requirements.txt

# 複製配置檔案
cp config/settings.example.json config/settings.json
```

### 2. 基本使用

```bash
# 🌟 推薦：直接啟動互動模式
python main.py

# 或使用命令列模式
python main.py info                                    # 顯示系統資訊
python main.py translate --book "書籍URL"              # 翻譯單本書籍
python main.py monitor dashboard                       # 查看監控儀表板
python main.py monitor watch 30                        # 實時監控模式

# 🌐 網頁介面使用
# 1. 開啟 docs/index.html 在瀏覽器中
# 2. 或使用 Python 啟動本地伺服器
python -m http.server 8000 --directory docs
# 然後訪問 http://localhost:8000
```

### 3. 互動模式特色

- 🎯 **數字選單**: 輸入數字選擇操作，簡單直觀
- 📋 **書籍管理**: 查看、添加、選擇書籍配置
- 🔗 **直接貼上**: 支援直接貼上書籍URL進行翻譯
- 📊 **即時狀態**: 隨時查看系統狀態和進度
- 🎛️ **整合監控**: 內建監控儀表板和報告生成

### 4. 網頁介面功能

- 📚 **智能選擇**: 書籍和章節雙重選擇系統
- 📖 **對照閱讀**: 原文與譯文並排顯示
- 🎛️ **多種模式**: 原文模式、翻譯模式、對照模式
- ⌨️ **快捷鍵**: 支援方向鍵導航和空格鍵切換模式
- 📜 **向後相容**: 保留舊版經典的存取功能

## 📖 詳細使用指南

### 翻譯功能

```bash
# 翻譯單本書籍
python main.py translate --book "https://www.shidianguji.com/book/DZ0001"

# 查看已配置的書籍
python main.py translate --list

# 批量翻譯所有啟用的書籍
python main.py translate --batch

# 查看翻譯系統狀態
python main.py translate --status
```

### 監控功能

```bash
# 查看完整儀表板
python main.py monitor dashboard

# 查看翻譯進度
python main.py monitor progress

# 查看最近活動（預設10項）
python main.py monitor activity 20

# 實時監控模式（每30秒更新）
python main.py monitor watch 30

# 生成所有報告
python main.py monitor reports

# 匯出系統狀態為JSON
python main.py monitor export
```

### 系統資訊

```bash
# 查看系統資訊和當前狀態
python main.py info

# 查看幫助
python main.py --help
python main.py translate --help
python main.py monitor --help
```

## 🔧 配置管理

### 配置檔案設定
```bash
# 1. 複製範例配置
cp config/settings.example.json config/settings.json

# 2. 編輯配置檔案
# 包含：翻譯設定、追蹤設定、輸出設定、書籍清單等
```

### 資料流程概覽
```
網站URL → core/translator.py（爬取 + 產生翻譯模板）→
docs/source_texts/、docs/translations/ → core/tracker.py → data/tracking/ →
docs/js/script.js（網站書單）→ docs/index.html
```

詳細說明請參考：**[資料流程說明](docs/system/資料流程說明.md)**

## 📊 資料結構

### 追蹤資料 (`data/tracking/`)
- `classics.json` - 經典資料庫
- `tracking_report.md` - 追蹤報告
- `system_status.json` - 系統狀態快照

### 日誌資料 (`data/logs/`)
- `file_operations.json` - 檔案操作日誌
- `activity_report.md` - 活動報告

### 輸出資料 (`docs/`)
- `source_texts/` - 爬取的原文檔案
- `translations/` - 生成的翻譯模板

## 🎯 工作流程

### 步驟一：翻譯新經典

```bash
# 方法1: 直接翻譯
python main.py translate --book "https://www.shidianguji.com/book/DZ0001"

# 方法2: 先添加到配置，再批量處理
# 編輯 config/settings.json 添加新書籍
python main.py translate --batch
```

### 步驟二：監控進度

```bash
# 查看翻譯進度
python main.py monitor progress

# 實時監控
python main.py monitor watch
```

### 步驟三：生成報告

```bash
# 生成所有報告
python main.py monitor reports
```

## 🔄 從舊版本升級

v1.x → v2.0 的資料遷移已經完成，遷移工具已封存到 `archive/one_off_tools/migrate_data.py`。

遷移後的變更：
- ✅ 所有舊檔案已備份到 `backup/` 和 `archive/` 目錄
- ✅ 資料已遷移到新的模組化結構
- ✅ 使用新的 `main.py` 統一入口點

## 🛠️ 開發者資訊

### 模組結構

- **core/** - 核心功能模組
  - `translator.py` - 翻譯引擎
  - `tracker.py` - 追蹤系統
  - `file_monitor.py` - 檔案監控
  
- **tools/** - 命令列工具
  - `easy_cli.py` - 翻譯介面
  - `monitor_cli.py` - 監控介面
  - `ai_translator.py` / `ai_translation_evaluator.py` - AI 翻譯與品質評估

- **archive/** - 已不再使用、保留參考的舊程式（說明見 `archive/README.md`）

### 擴展功能

系統採用模組化設計，可輕鬆擴展新功能：

1. 在 `core/` 添加新的核心模組
2. 在 `tools/` 添加新的CLI工具
3. 在 `main.py` 中註冊新的子命令

## 📝 更新日誌

### v2.0.0 (2025-08-09)
- 🎉 **重大重構**: 採用模組化架構
- ✨ **統一入口**: 新增 `main.py` 統一介面
- 📊 **增強追蹤**: 改進的追蹤和監控系統
- 🔧 **配置管理**: 統一的配置檔案系統
- 📦 **自動遷移**: 提供從v1.x的無縫升級

### v1.x (歷史版本)
- 基礎翻譯和追蹤功能
- 多個獨立的工具檔案
- 已歸檔到 `archive/` 目錄

## 🤝 貢獻指南

歡迎提交Issue和Pull Request！

1. Fork 本專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟Pull Request

## 📚 詳細文檔

### 🎯 使用指南
- **[使用示例](docs/system/使用示例.md)** - 實際操作示例和互動模式指南
- **[工具使用指南](docs/system/工具使用指南.md)** - 完整的功能說明和使用方法
- **[網頁使用說明](docs/system/網頁使用說明.md)** - 網頁介面使用指南

### 🔧 技術文檔
- **[環境設定指南](docs/system/環境設定指南.md)** - 完整的環境設定和依賴管理
- **[資料流程說明](docs/system/資料流程說明.md)** - 資料處理流程和目錄關係
- **[追蹤系統說明](docs/system/追蹤系統說明.md)** - 追蹤系統的詳細介紹

### 🤖 AI翻譯指導
- **[AI翻譯指導規範](docs/system/AI翻譯指導規範.md)** - AI翻譯專用指導和規範
- **[AI翻譯工作流程](docs/system/AI翻譯工作流程.md)** - 完整的AI翻譯工作流程

### 📋 參考資料
- **[升級總結報告](docs/system/UPGRADE_SUMMARY.md)** - v2.0重構的完整記錄
- **[封存說明](archive/README.md)** - 舊版爬蟲與一次性工具的封存紀錄

## 📊 當前狀態

- **經典總數**: 23部
- **章節總數**: 188章
- **系統版本**: v2.0.0
- **主要經典**: 南華真經口義(71章)、抱朴子內篇(38章)等

## 🤝 貢獻指南

歡迎提交Issue和Pull Request！

1. Fork 本專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟Pull Request

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 🙏 致謝

感謝所有為道教經典數位化和翻譯工作做出貢獻的朋友們！

---

*道教經典翻譯系統 v2.0 - 讓古籍翻譯更簡單、更智能* 🏛️✨

## 📥 新增經文與更新網站

1. **爬取新書**（產生原文與翻譯模板，並自動更新網站書單）：
   ```bash
   python main.py translate --book "https://www.shidianguji.com/book/DZ0789"
   ```
2. **翻譯**：編輯 `docs/translations/<書名_編號>/<章>.md`，把「[此處應為現代中文翻譯]」換成譯文。
   已經翻譯好的章節，重新爬取同一本書時不會被覆蓋。
3. **更新網站書單**：手動新增、刪除或翻譯檔案後執行一次（推送到 main 時 GitHub Actions 也會自動執行）：
   ```bash
   python tools/build_web_data.py
   ```
4. **本地預覽**：
   ```bash
   python -m http.server 8000 --directory docs
   ```
   然後打開 `http://localhost:8000`。
5. **部署**：推送到 main 分支即自動部署到 https://yehwanlan.github.io/Taoism/

---