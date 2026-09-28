# archive/ — 封存的舊程式與檔案

這裡的檔案**不會被主程式（`main.py`）或網站使用**，也不會部署到 GitHub Pages，
只是保留參考。需要時可以搬回原位；完整歷史都在 git 裡。

> 注意：搬到這裡之後，檔案裡的相對路徑（例如 `sys.path` 指向專案根目錄）已經不成立，
> 要執行的話請先搬回原本的資料夾。

| 資料夾 | 原位置 | 內容 | 封存原因 |
|---|---|---|---|
| `v1_backup_20250809_033258/` | 專案根目錄 | v1.x 的舊程式（含當年產生網站書單的 `generate_scriptures_js.py`） | 已被 v2.0 取代 |
| `one_off_tools/` | `tools/`、`config/` | `fix_dz0336_structure.py`、`fix_missing_chapters.py`、`migrate_data.py`、`fix_unicode_prints.py` 等，以及只供 `add_hidden_chapters.py` 使用的 `hidden_chapters.json` | 為單一問題或單本書寫的一次性腳本，任務已完成 |
| `crawler_experiments/` | `crawler/` | Selenium 版、智能爬蟲、通用爬蟲、demo 等 14 支實驗性爬蟲與 6 份說明文件 | 目前使用 `crawler/shidian_crawler.py`，其餘沒有被引用 |
| `web_test_pages/` | `docs/` | `test-lunar.html`、`verify-fix.html`、`debug-calculation.html` 等 7 個測試頁 | 首頁點不到，但原本放在 `docs/` 會被公開部署 |
| `unused_code/` | `core/` | `ai_engine.py` | 主程式建立了物件但從未呼叫；AI 翻譯實際使用 `tools/ai_translator.py` |

封存日期：2026-09-28
