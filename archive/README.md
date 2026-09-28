# archive/ — 封存的舊程式與檔案

這裡的檔案**不會被主程式（`main.py`）或網站使用**，也不會部署到 GitHub Pages，
只是保留參考。需要時可以搬回原位；完整歷史都在 git 裡。

> 注意：搬到這裡之後，檔案裡的相對路徑（例如 `sys.path` 指向專案根目錄）已經不成立，
> 要執行的話請先搬回原本的資料夾。

| 資料夾 | 原位置 | 內容 | 封存原因 |
|---|---|---|---|
| `v1_backup_20250809_033258/` | 專案根目錄 | v1.x 的舊程式（含當年產生網站書單的 `generate_scriptures_js.py`） | 已被 v2.0 取代 |
| `one_off_tools/` | `tools/`、`config/` | `fix_dz0336_structure.py`、`fix_missing_chapters.py`、`migrate_data.py`、`fix_unicode_prints.py` 等，以及只供 `add_hidden_chapters.py` 使用的 `hidden_chapters.json` | 為單一問題或單本書寫的一次性腳本，任務已完成 |
| `crawler_experiments/` | `crawler/` | Selenium 版、智能爬蟲、通用爬蟲、demo 等 14 支實驗性爬蟲與 6 份說明文件 | 沒有被引用 |
| `crawler_experiments/shidian_crawler_v2/` | `crawler/` | `shidian_crawler.py` + `base_crawler.py` 套件與說明文件 | 2026-09 實測 DZ0789：識典古籍改版後，書籍首頁不再輸出目錄、書名 CSS class 也變了，抓到 0 章。現在統一使用 `core/translator.py`（`python main.py translate --book <網址>`） |
| `crawler_experiments/output/` | `crawler/docs/`、`data/crawled/` | 舊爬蟲抓的《丹陽真人直言》(DZ1234)、《枕中经》(DZ1422)、《洞玄灵宝玉京山步虚经》(DZ1439) 的原始輸出 | 格式與網站不相容；需要時用 `main.py translate` 重新抓取即可 |
| `web_test_pages/` | `docs/` | 10 個測試／除錯頁（`test-*.html`、`api-test.html` + `js/fortune-api.js`、`verify-fix.html` 等），以及 `enhanced-calendar.html` + 專用 css/js | 測試頁原本放在 `docs/` 會被公開部署；enhanced-calendar 呼叫不存在的 `checkFortune()`，從建立起就無法使用，萬年曆保留 `calendar.html` |
| `unused_code/` | `core/` | `ai_engine.py` | 主程式建立了物件但從未呼叫；AI 翻譯實際使用 `tools/ai_translator.py` |

封存日期：2026-09-28
