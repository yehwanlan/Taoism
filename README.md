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
├── 📁 crawler/                 # 爬蟲工具集（保留）
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
網站URL → crawler/ → docs/source_texts/ → core/translator.py → 
docs/translations/ → core/tracker.py → data/tracking/ → 
update_web_data.py → docs/index.html
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

如果您使用的是舊版本（v1.x），系統提供了自動遷移工具：

```bash
# 執行資料遷移（已完成）
python tools/migrate_data.py
```

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
  - `migrate_data.py` - 資料遷移工具

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
- **[爬蟲工具文檔](crawler/)** - 21個專業爬蟲工具的說明

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

1.  **新增原始經文：**
    將新的道教經典文本檔案（例如 `.txt` 或 `.html`）放入 `source_texts/` 資料夾。

2.  **新增翻譯：**
    在 `translations/` 資料夾中，為您新增的原始經文建立一個對應的 `.md` 檔案。檔案名稱應與原始經文的名稱（不含副檔名）相同。例如，如果原始經文是 `道德經.txt`，則翻譯檔案應為 `道德經.md`。

    在 `.md` 檔案中，您可以開始編寫經文的現代中文白話翻譯。您可以使用 Markdown 語法來格式化您的翻譯內容。

### 步驟二：更新經文列表

每當您新增或修改了 `source_texts/` 或 `translations/` 資料夾中的檔案後，您需要執行 `generate_scriptures_js.py` 腳本來更新網頁的經文列表。在專案根目錄下執行：
```bash
python generate_scriptures_js.py
```
這個腳本會自動掃描資料夾，並更新 `docs/js/script.js` 中的 `scriptures` 物件，確保網頁能夠正確載入新的經文或更新後的翻譯。

### 步驟三：本地預覽

在專案的根目錄下，您可以啟動一個簡單的 Python 網頁伺服器來預覽網站變更：
```bash
python -m http.server 8000
```
然後在您的瀏覽器中打開 `http://localhost:8000/docs/`。

### 步驟四：一鍵部署

現在支援多種部署方式，推薦使用一鍵部署腳本：

```bash
# 🚀 一鍵部署到 GitHub Pages
python deploy.py github

# 🐳 Docker 部署
python deploy.py docker

# 🏠 本地服務
python deploy.py local

# 📦 創建發布包
python deploy.py package

# 🎯 完整部署流程
python deploy.py all
```

**GitHub Pages 自動部署：**
- 系統已配置 GitHub Actions 自動部署
- 推送到 main 分支會自動觸發部署
- 訪問地址：`https://<您的GitHub使用者名稱>.github.io/<您的儲存庫名稱>/`

詳細安裝和部署說明請參考：**[安裝指南](INSTALL.md)**

### 步驟五：管理翻譯進度

*   **判斷翻譯狀態：** 您可以透過檢查 `translations/` 資料夾中是否存在對應的 `.md` 檔案來判斷一篇經文是否已經有翻譯。如果存在，就表示有翻譯；如果不存在，就表示還沒有翻譯。
*   **`generate_scriptures_js.py` 的作用：** 該腳本會自動檢查 `translations/` 資料夾中是否存在對應的 `.md` 檔案。如果存在，它會將翻譯檔案的路徑包含在 `scriptures` 物件中；如果不存在，則翻譯路徑會留空，網頁會顯示載入失敗的訊息，提示該經文尚未翻譯。

---