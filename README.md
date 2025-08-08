# 道教經典翻譯專案

## 專案概述

這個專案旨在建立一個線上平台，用於展示道教經典的原文及其現代中文白話（繁體）翻譯。透過將原文與譯文並排顯示，方便讀者對照學習和理解。

專案採用靜態網站技術，可輕鬆部署到 GitHub Pages，實現免費且便捷的線上分享。

## 主要功能

*   **原文與譯文並排顯示：** 提供清晰的閱讀體驗，方便對照。
*   **經文選擇：** 透過下拉選單快速切換不同的經文。
*   **自動化經文管理：** 透過 Python 腳本自動更新網頁上的經文列表，無需手動修改 JavaScript 程式碼。
*   **Markdown 格式翻譯：** 翻譯內容使用 Markdown 格式編寫，易於閱讀和編輯。

## 專案結構

```
.
├── source_texts/             # 存放原始道教經典文本（例如：.txt, .html）
├── translations/           # 存放翻譯後的現代中文白話文本（.md 格式）
├── docs/                   # 存放網頁相關檔案（HTML, CSS, JavaScript）
│   ├── css/                # 網頁樣式表
│   │   └── style.css
│   ├── js/                 # 網頁 JavaScript 邏輯
│   │   └── script.js       # 包含自動生成的經文列表
│   └── index.html          # 網站首頁
├── generate_scriptures_js.py # 自動生成 script.js 中經文列表的 Python 腳本
├── .git/                   # Git 版本控制相關檔案
├── .vscode/                # VS Code 編輯器設定
├── GIT.txt                 # 其他 Git 相關筆記
├── README.md               # 本專案說明文件
└── ...                     # 其他原始經文檔案
```

## 如何開始 (本地設定)

1.  **克隆專案：**
    如果您尚未克隆本專案，請使用以下命令：
    ```bash
    git clone <您的GitHub儲存庫URL>
    cd Taoism
    ```

2.  **安裝 Python：**
    請確保您的系統已安裝 Python 3。您可以從 [Python 官方網站](https://www.python.org/downloads/) 下載並安裝。

## 工作流程

### 步驟一：新增與翻譯經文

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

### 步驟四：部署到 GitHub Pages

1.  **建立 GitHub 儲存庫：**
    如果您尚未將專案上傳到 GitHub，請在 GitHub 上建立一個新的儲存庫，並將本地專案推送到該儲存庫。

2.  **設定 GitHub Pages：**
    *   前往您的 GitHub 儲存庫頁面。
    *   點擊頂部的 **Settings** (設定)。
    *   在左側選單中，點擊 **Pages**。
    *   在 "Build and deployment" 部分，將 "Source" 設定為 **Deploy from a branch**。
    *   在 "Branch" 部分，選擇 `main` (或您的主要分支)，並將資料夾設定為 `/docs`。
    *   點擊 **Save** (儲存)。

    GitHub Pages 會自動部署您的網站。通常在幾分鐘內，您就可以透過 `https://<您的GitHub使用者名稱>.github.io/<您的儲存庫名稱>/` 訪問您的網站。

### 步驟五：管理翻譯進度

*   **判斷翻譯狀態：** 您可以透過檢查 `translations/` 資料夾中是否存在對應的 `.md` 檔案來判斷一篇經文是否已經有翻譯。如果存在，就表示有翻譯；如果不存在，就表示還沒有翻譯。
*   **`generate_scriptures_js.py` 的作用：** 該腳本會自動檢查 `translations/` 資料夾中是否存在對應的 `.md` 檔案。如果存在，它會將翻譯檔案的路徑包含在 `scriptures` 物件中；如果不存在，則翻譯路徑會留空，網頁會顯示載入失敗的訊息，提示該經文尚未翻譯。

---