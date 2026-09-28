#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道教經典翻譯系統 - 簡易命令列介面

整合原有的 easy_translator.py 功能，提供統一的CLI介面
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# 添加父目錄到路徑以便導入核心模組
sys.path.append(str(Path(__file__).parent.parent))

from core import TranslationEngine
from core.conventions import TRANSLATION_PLACEHOLDER
from core.unicode_handler import safe_print


class EasyCLI:
    """簡易命令列介面"""
    
    def __init__(self):
        """初始化CLI"""
        self.config_file = Path("config/settings.json")
        self.config = self._load_config()
        self.engine = TranslationEngine(self.config.get("translation", {}))
        # 與翻譯引擎共用同一份追蹤資料；各自持有時，引擎剛記錄的新書會被這裡的舊資料存檔蓋掉
        self.tracker = self.engine.tracker
        
    def _load_config(self) -> Dict:
        """載入配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
                
        # 返回預設配置
        return self._create_default_config()
        
    def _create_default_config(self) -> Dict:
        """創建預設配置"""
        return {
            "translation": {
                "base_url": "https://www.shidianguji.com",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "request_delay": 2,
                "max_retries": 3,
                "timeout": 10
            },
            "ai": {
                "api_key": "YOUR_AI_API_KEY_HERE"
            },
            "books": [],
            "output": {
                "create_readme": True,
                "generate_progress_report": True,
                "backup_original": True
            }
        }
        
    def _save_config(self) -> None:
        """儲存配置"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
            
    def add_book(self, url: str, name: str = None) -> None:
        """添加新書籍到配置"""
        # 如果沒有提供名稱，嘗試從URL自動獲取
        if not name:
            safe_print("🔍 正在獲取書籍資訊...")
            name = self._get_book_title_from_url(url)
            
        new_book = {
            "name": name,
            "url": url,
            "enabled": True,
            "translation_style": "classical",
            "notes": ""
        }
        
        self.config["books"].append(new_book)
        self._save_config()
        
        safe_print(f"✅ 已添加書籍: {name}")
        safe_print(f"📖 URL: {url}")
        
        # 不再重複詢問，因為在互動模式中已經處理了

    def list_books(self) -> None:
        """列出所有書籍"""
        books = self.config.get("books", [])
        
        if not books:
            safe_print("\n📚 尚未添加任何書籍")
            safe_print("💡 選擇選項 2 添加新書籍")
            return
            
        safe_print("\n📚 已配置的書籍列表:")
        safe_print("=" * 60)
        
        for i, book in enumerate(books, 1):
            status_icon = "✅" if book.get("enabled", True) else "❌"
            status_text = "啟用" if book.get("enabled", True) else "停用"
            
            safe_print(f"{i}. {status_icon} {book['name']}")
            safe_print(f"   🔗 {book['url']}")
            if book.get('notes'):
                safe_print(f"   📝 {book['notes']}")
            safe_print(f"   📊 狀態: {status_text}")
            safe_print()
            
    def translate_book(self, url: str) -> bool:
        """翻譯單本書籍"""
        safe_print("🚀 啟動道教經典翻譯系統")
        safe_print("=" * 50)
        
        try:
            success = self.engine.translate_book(url)
            
            if success:
                safe_print("\n🎉 翻譯完成！")
                safe_print("📊 正在生成追蹤報告...")
                
                # 生成追蹤報告
                self.tracker.check_translation_progress()
                report_file = self.tracker.save_report()
                
                safe_print(f"📋 追蹤報告: {report_file}")
                
            return success
            
        except Exception as e:
            safe_print(f"❌ 翻譯過程發生錯誤: {e}")
            return False
            
    def batch_translate(self) -> None:
        """批量翻譯所有啟用的書籍"""
        books = [book for book in self.config.get("books", []) if book.get("enabled", True)]
        
        if not books:
            safe_print("📚 沒有啟用的書籍可供翻譯")
            safe_print("💡 請先使用 --book 添加書籍或使用 --list 查看現有書籍")
            return
            
        safe_print(f"🚀 開始批量翻譯 {len(books)} 本書籍")
        safe_print("=" * 60)
        
        success_count = 0
        
        for i, book in enumerate(books, 1):
            safe_print(f"\n📖 處理第 {i}/{len(books)} 本: {book['name']}")
            safe_print("-" * 40)
            
            try:
                success = self.translate_book(book['url'])
                if success:
                    success_count += 1
                    safe_print(f"✅ 第 {i} 本書處理完成")
                else:
                    safe_print(f"❌ 第 {i} 本書處理失敗")
                    
            except Exception as e:
                safe_print(f"❌ 處理第 {i} 本書時發生錯誤: {e}")
                
            safe_print("-" * 40)
            
        safe_print(f"\n🎊 批量翻譯完成！")
        safe_print(f"✅ 成功: {success_count}/{len(books)} 本")
        safe_print("💡 提示：翻譯模板已生成，您可以直接編輯翻譯內容")
        
    def show_status(self) -> None:
        """顯示系統狀態"""
        safe_print("📊 道教經典翻譯系統狀態")
        safe_print("=" * 50)
        
        # 追蹤系統統計
        stats = self.tracker.get_statistics()
        safe_print(f"📚 經典總數: {stats.get('total_classics', 0)}")
        safe_print(f"📖 章節總數: {stats.get('total_chapters', 0)}")
        safe_print(f"📝 總字數: {stats.get('total_characters', 0):,}")
        safe_print(f"🕒 最後更新: {stats.get('last_updated', 'N/A')[:19].replace('T', ' ')}")
        
        # 配置統計
        books = self.config.get("books", [])
        enabled_books = [book for book in books if book.get("enabled", True)]
        
        safe_print(f"\n📋 配置統計:")
        safe_print(f"📚 已配置書籍: {len(books)}")
        safe_print(f"✅ 啟用書籍: {len(enabled_books)}")
        
    def interactive_mode(self) -> None:
        """互動模式"""
        safe_print("🌟 歡迎使用道教經典翻譯系統 v2.0")
        safe_print("=" * 50)
        
        while True:
            try:
                safe_print("\n請選擇操作：")
                safe_print("1. 📚 查看書籍列表")
                safe_print("2. ➕ 添加新書籍")
                safe_print("3. 📖 翻譯指定書籍")
                safe_print("4. 🚀 批量翻譯所有書籍")
                safe_print("5. 📊 查看系統狀態")
                safe_print("6. 🔍 監控儀表板")
                safe_print("7. 📋 生成報告")
                safe_print("8. 📝 生成翻譯模板")
                safe_print("9. 🤖 AI智能翻譯")
                safe_print("10. ❓ 幫助說明")
                safe_print("11. 👋 退出程式")
                
                choice = input("\n請輸入選項 (1-11): ").strip()
                
                if choice == "1":
                    self.list_books()
                    
                elif choice == "2":
                    url = input("請輸入書籍URL: ").strip()
                    if url:
                        # 自動獲取書名並添加書籍
                        safe_print("🔍 正在獲取書籍資訊...")
                        auto_book_name = self._get_book_title_from_url(url)
                        
                        # 如果自動獲取的名稱只是ID，讓用戶手動輸入
                        if auto_book_name.startswith('DZ') or len(auto_book_name) < 4:
                            safe_print(f"⚠️  自動獲取的書名: {auto_book_name}")
                            manual_name = input("請輸入正確的書籍名稱 (直接按Enter使用自動獲取的名稱): ").strip()
                            book_name = manual_name if manual_name else auto_book_name
                        else:
                            book_name = auto_book_name
                        
                        self.add_book(url, book_name)
                        safe_print(f"✅ 已添加書籍: {book_name}")
                        safe_print(f"📖 URL: {url}")
                        
                        # 詢問是否建立翻譯模板
                        safe_print(f"\n📝 發現新書籍: {book_name}")
                        create_template = input("是否立即建立翻譯模板？(Y/n): ").strip().lower()
                        
                        if create_template in ['', 'y', 'yes', '是']:
                            safe_print("📝 開始建立翻譯模板...")
                            self._create_translation_templates_for_book(url, book_name)
                        else:
                            safe_print("📋 已跳過翻譯模板建立，您可以稍後使用選項 8 手動建立")
                    else:
                        safe_print("❌ URL不能為空")
                        
                elif choice == "3":
                    safe_print("\n選擇翻譯方式：")
                    safe_print("a. 從配置列表中選擇")
                    safe_print("b. 直接輸入新的URL")
                    
                    sub_choice = input("請選擇 (a/b): ").strip().lower()
                    
                    if sub_choice == "a":
                        self.list_books()
                        books = self.config.get("books", [])
                        if books:
                            try:
                                index = int(input("請選擇書籍編號: ")) - 1
                                if 0 <= index < len(books):
                                    book = books[index]
                                    safe_print(f"🚀 開始翻譯: {book['name']}")
                                    self.translate_book(book["url"])
                                else:
                                    safe_print("❌ 無效的編號")
                            except ValueError:
                                safe_print("❌ 請輸入有效的數字")
                    elif sub_choice == "b":
                        url = input("請直接貼上書籍URL: ").strip()
                        if url:
                            self.translate_book(url)
                        else:
                            safe_print("❌ URL不能為空")
                    else:
                        safe_print("❌ 無效的選項")
                        
                elif choice == "4":
                    confirm = input("確定要批量翻譯所有啟用的書籍嗎？(y/N): ").strip().lower()
                    if confirm == 'y':
                        self.batch_translate()
                    else:
                        safe_print("❌ 已取消批量翻譯")
                        
                elif choice == "5":
                    self.show_status()
                    
                elif choice == "6":
                    safe_print("🔍 啟動監控儀表板...")
                    from .monitor_cli import MonitorCLI
                    monitor = MonitorCLI()
                    monitor.generate_dashboard()
                    
                elif choice == "7":
                    safe_print("📋 正在生成報告...")
                    from .monitor_cli import MonitorCLI
                    monitor = MonitorCLI()
                    monitor.generate_reports()
                    
                elif choice == "8":
                    safe_print("📝 啟動翻譯模板生成器...")
                    self._generate_translation_templates()
                    
                elif choice == "9":
                    self._ai_translation_interface()
                    
                elif choice == "10":
                    self._show_interactive_help()
                    
                elif choice == "11":
                    safe_print("👋 感謝使用道教經典翻譯系統！")
                    break
                    
                else:
                    safe_print("❌ 無效的選項，請輸入 1-11 之間的數字")
                    
            except KeyboardInterrupt:
                safe_print("\n👋 再見！")
                break
            except Exception as e:
                safe_print(f"❌ 發生錯誤: {e}")
                safe_print("💡 請重新選擇操作")

    def _show_interactive_help(self) -> None:
        """顯示互動模式幫助"""
        safe_print("""
📖 道教經典翻譯系統 v2.0 - 使用說明

🎯 主要功能:
  1. 📚 書籍管理 - 查看、添加、管理書籍配置
  2. 🤖 自動翻譯 - 一鍵完成爬取和翻譯模板生成
  3. 📊 進度追蹤 - 實時監控翻譯進度和統計
  4. 📋 報告生成 - 詳細的統計報告和分析
  5. 🤖 AI智能翻譯 - 使用生成式AI進行專業經文翻譯

🚀 快速開始:
  • 選擇選項 2 添加新書籍URL（自動獲取書名）
  • 選擇選項 3 開始翻譯（可直接貼上URL）
  • 選擇選項 6 查看監控儀表板
  • 選擇選項 9 使用AI智能翻譯

💡 小貼士:
  • 支援十典古籍網 (shidianguji.com) 的書籍URL
  • 系統會自動獲取書籍名稱，無需手動輸入
  • 添加書籍後會詢問是否立即建立翻譯模板
  • 使用選項 8 可為現有經典批量生成翻譯模板
  • 使用選項 9 可進行AI智能翻譯，支援單檔和批量模式

🤖 AI翻譯功能:
  • 基於專業道教翻譯規範進行翻譯
  • 自動保持術語一致性和專業性
  • 提供翻譯品質評估和改進建議
  • 支援進度追蹤和批量處理
  • 需要安裝 Gemini CLI 工具

📞 需要幫助？
  • 查看 docs/system/ 目錄的詳細文檔
  • 使用 python main.py --help 查看命令列選項
""")
            
    def _generate_translation_templates(self) -> None:
        """生成翻譯模板"""
        safe_print("📝 翻譯模板生成器")
        safe_print("=" * 40)
        
        from pathlib import Path
        
        # 查找所有原文目錄
        docs_dir = Path("docs/source_texts")
        if not docs_dir.exists():
            safe_print("❌ 沒有找到原文目錄")
            safe_print("💡 請先使用選項 2 或 3 爬取一些書籍")
            return
        
        book_dirs = [d for d in docs_dir.iterdir() if d.is_dir() and (d / "原文").exists()]
        
        if not book_dirs:
            safe_print("❌ 沒有找到包含原文的書籍目錄")
            safe_print("💡 請先使用選項 2 或 3 爬取一些書籍")
            return
        
        safe_print(f"📚 找到 {len(book_dirs)} 本書籍：")
        for i, book_dir in enumerate(book_dirs, 1):
            source_files = list((book_dir / "原文").glob("*.txt"))
            safe_print(f"{i}. {book_dir.name} ({len(source_files)} 個原文檔案)")
        
        safe_print("\n請選擇操作：")
        safe_print("1. 為所有書籍生成翻譯模板")
        safe_print("2. 為指定書籍生成翻譯模板")
        safe_print("3. 返回主選單")
        
        choice = input("\n請輸入選項 (1-3): ").strip()
        
        if choice == "1":
            safe_print("🚀 開始為所有書籍生成翻譯模板...")
            total_generated = 0
            
            for book_dir in book_dirs:
                safe_print(f"\n📖 處理: {book_dir.name}")
                generated = self._generate_templates_for_book_dir(book_dir)
                total_generated += generated
                safe_print(f"✅ 已生成 {generated} 個翻譯模板")
            
            safe_print(f"\n🎉 全部完成！總共生成 {total_generated} 個翻譯模板")
            
        elif choice == "2":
            try:
                book_index = int(input("請選擇書籍編號: ")) - 1
                if 0 <= book_index < len(book_dirs):
                    book_dir = book_dirs[book_index]
                    safe_print(f"🚀 開始為 {book_dir.name} 生成翻譯模板...")
                    generated = self._generate_templates_for_book_dir(book_dir)
                    safe_print(f"🎉 完成！生成了 {generated} 個翻譯模板")
                else:
                    safe_print("❌ 無效的書籍編號")
            except ValueError:
                safe_print("❌ 請輸入有效的數字")
        
        elif choice == "3":
            return
        else:
            safe_print("❌ 無效選項")
    
    def _generate_templates_for_book_dir(self, book_dir) -> int:
        """為指定書籍目錄生成翻譯模板"""
        from pathlib import Path
        
        source_dir = book_dir / "原文"
        translation_dir = Path("docs/translations") / book_dir.name
        translation_dir.mkdir(parents=True, exist_ok=True)
        
        source_files = list(source_dir.glob("*.txt"))
        generated_count = 0
        
        for source_file in source_files:
            translation_filename = f"{source_file.stem}.md"
            translation_file_path = translation_dir / translation_filename
            
            # 如果翻譯模板已存在，跳過
            if translation_file_path.exists():
                safe_print(f"  ⏭️  跳過已存在的模板: {translation_filename}")
                continue
            
            if self._create_single_translation_template(source_file, translation_dir):
                safe_print(f"  ✅ 已生成: {translation_filename}")
                generated_count += 1
        
        return generated_count
            
    def _create_translation_templates_for_book(self, url: str, book_name: str) -> None:
        """為指定書籍建立翻譯模板"""
        try:
            # 使用現有的翻譯系統來下載原文並生成模板
            safe_print("📥 正在下載書籍原文並生成翻譯模板...")
            success = self.translate_book(url)
            
            if success:
                # 翻譯完成後，自動生成翻譯模板
                safe_print("📝 正在生成翻譯模板...")
                self._generate_templates_for_existing_sources()
                safe_print("✅ 翻譯模板建立完成！")
                safe_print("💡 您現在可以在 docs/translations/ 目錄中找到翻譯模板")
            else:
                safe_print("❌ 原文下載失敗")
                safe_print("💡 您可以稍後使用選項 8 手動建立翻譯模板")
                
        except Exception as e:
            safe_print(f"❌ 建立翻譯模板失敗: {e}")
            # 即使翻譯引擎失敗，也嘗試為現有原文生成模板
            safe_print("🔄 嘗試為現有原文生成翻譯模板...")
            try:
                self._generate_templates_for_existing_sources()
                safe_print("✅ 翻譯模板生成完成！")
            except Exception as e2:
                safe_print(f"❌ 翻譯模板生成也失敗: {e2}")
                safe_print("💡 您可以稍後使用選項 8 手動建立翻譯模板")
    
    def _generate_templates_for_existing_sources(self) -> None:
        """為現有的原文檔案生成翻譯模板"""
        from pathlib import Path

        # 查找所有原文目錄
        docs_dir = Path("docs/source_texts")
        if not docs_dir.exists():
            safe_print("❌ 沒有找到原文目錄")
            return
        
        for book_dir in docs_dir.iterdir():
            if book_dir.is_dir():
                source_dir = book_dir / "原文"
                if source_dir.exists():
                    # 建立對應的翻譯目錄
                    translation_dir = Path("docs/translations") / book_dir.name
                    translation_dir.mkdir(parents=True, exist_ok=True)
                    
                    # 為每個原文檔案生成翻譯模板
                    source_files = list(source_dir.glob("*.txt"))
                    for source_file in source_files:
                        self._create_single_translation_template(source_file, translation_dir)
    
    def _get_book_title_from_url(self, url: str) -> str:
        """從URL獲取書籍標題"""
        try:
            # 嘗試轉換URL格式以獲取更好的結果
            corrected_url = self._correct_book_url(url)
            
            # 使用翻譯引擎獲取書籍資訊
            book_info = self.engine.get_book_info(corrected_url)
            title = book_info.get('title', self._extract_book_id_from_url(url))
            
            # 如果標題就是ID，嘗試原始URL
            if title == self._extract_book_id_from_url(url):
                book_info = self.engine.get_book_info(url)
                title = book_info.get('title', title)
            
            return title
        except Exception as e:
            safe_print(f"⚠️  無法獲取書籍標題: {e}")
            return self._extract_book_id_from_url(url)
    
    def _correct_book_url(self, url: str) -> str:
        """修正書籍URL格式以獲得更好的標題提取效果"""
        import re
        
        # 提取書籍ID
        book_id_match = re.search(r'/book/([^/?]+)', url)
        if not book_id_match:
            return url
        
        book_id = book_id_match.group(1)
        
        # 如果URL格式是 /chapter/start 或類似格式，嘗試轉換為章節格式
        if '/chapter/start' in url or 'mode=book' in url:
            # 轉換為第一章的URL格式
            base_url = "https://www.shidianguji.com/zh/book"
            corrected_url = f"{base_url}/{book_id}/chapter/{book_id}_1"
            return corrected_url
        
        return url
    
    def _extract_book_id_from_url(self, url: str) -> str:
        """從URL提取書籍ID作為備用名稱"""
        import re
        match = re.search(r'/book/([^/?]+)', url)
        return match.group(1) if match else "未知書籍"

    def _create_single_translation_template(self, source_file_path, translation_dir) -> bool:
        """為單個原文檔案生成翻譯模板，有實際寫入檔案時回傳 True"""
        try:
            # 讀取原文
            with open(source_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取標題
            lines = content.split('\n')
            title = lines[0].replace('# ', '').strip() if lines else "未知標題"
            
            # 生成翻譯檔案名
            source_filename = Path(source_file_path).stem
            translation_filename = f"{source_filename}.md"
            translation_file_path = translation_dir / translation_filename
            
            # 如果翻譯模板已存在，跳過
            if translation_file_path.exists():
                return False

            # 生成翻譯模板內容
            template_content = f"""# {title}

## 原文

{content}

## 翻譯

{TRANSLATION_PLACEHOLDER}

---

**翻譯說明：**
- 原文字數：{len(content)} 字
- 建議使用AI翻譯工具或人工翻譯
- 保持原文意思，使用現代中文表達
- 保留重要的古代術語，必要時添加註解

**重要詞彙：**
- [待補充重要詞彙解釋]

**文化背景：**
- [待補充相關文化背景]

**翻譯要點：**
- [待補充翻譯注意事項]

---
*翻譯模板生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*原文檔案：{source_filename}.txt*
"""
            
            # 保存翻譯模板
            with open(translation_file_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            return True

        except Exception as e:
            safe_print(f"❌ 生成翻譯模板失敗 {source_file_path}: {e}")
            return False
            
    def _ai_translation_interface(self) -> None:
        """AI翻譯介面"""
        try:
            import sys
            from pathlib import Path
            sys.path.append(str(Path(__file__).parent))
            from ai_translator import AITranslator, TranslationProgressTracker
            
            safe_print("🤖 AI智能翻譯系統")
            safe_print("=" * 40)
            safe_print("💡 支援使用Gemini CLI進行專業道教經文翻譯")
            safe_print()
            
            translator = AITranslator()
            tracker = TranslationProgressTracker()
            translator.set_progress_callback(tracker.update_progress)
            
            while True:
                safe_print("請選擇翻譯模式：")
                safe_print("1. 📄 翻譯單個檔案")
                safe_print("2. 📁 批量翻譯目錄")
                safe_print("3. 🔍 掃描待翻譯檔案")
                safe_print("4. 📊 翻譯品質評估")
                safe_print("5. 🔙 返回主選單")
                
                ai_choice = input("\n請輸入選項 (1-5): ").strip()
                
                if ai_choice == "1":
                    self._translate_single_file(translator)
                elif ai_choice == "2":
                    self._batch_translate_directory(translator, tracker)
                elif ai_choice == "3":
                    self._scan_untranslated_files()
                elif ai_choice == "4":
                    self._evaluate_translation_quality()
                elif ai_choice == "5":
                    break
                else:
                    safe_print("❌ 無效選項")
                    
        except ImportError:
            safe_print("❌ 無法載入AI翻譯器")
            safe_print("💡 請確認ai_translator.py檔案存在")
        except Exception as e:
            safe_print(f"❌ AI翻譯介面錯誤: {e}")
            
    def _translate_single_file(self, translator) -> None:
        """翻譯單個檔案"""
        safe_print("\n📄 單檔翻譯模式")
        safe_print("-" * 30)
        
        file_path = input("請輸入翻譯檔案路徑: ").strip()
        
        if not file_path:
            safe_print("❌ 檔案路徑不能為空")
            return
            
        file_path = Path(file_path)
        
        if not file_path.exists():
            safe_print(f"❌ 檔案不存在: {file_path}")
            return
            
        safe_print(f"🚀 開始翻譯: {file_path.name}")
        success = translator.translate_file(str(file_path))
        
        if success:
            safe_print("✅ 翻譯完成！")
            
            # 詢問是否進行品質評估
            evaluate = input("是否進行翻譯品質評估？(Y/n): ").strip().lower()
            if evaluate in ['', 'y', 'yes', '是']:
                self._evaluate_file(str(file_path))
        else:
            safe_print("❌ 翻譯失敗")
            
    def _batch_translate_directory(self, translator, tracker) -> None:
        """批量翻譯目錄"""
        safe_print("\n📁 批量翻譯模式")
        safe_print("-" * 30)
        
        directory = input("請輸入翻譯目錄路徑: ").strip()
        
        if not directory:
            safe_print("❌ 目錄路徑不能為空")
            return
            
        directory = Path(directory)
        
        if not directory.exists():
            safe_print(f"❌ 目錄不存在: {directory}")
            return
            
        pattern = input("檔案匹配模式 (預設: *.md): ").strip() or "*.md"
        
        # 預覽要翻譯的檔案
        files = list(directory.glob(pattern))
        
        if not files:
            safe_print(f"❌ 未找到符合條件的檔案: {directory}/{pattern}")
            return
            
        safe_print(f"\n🔍 找到 {len(files)} 個檔案:")
        for i, file in enumerate(files[:10], 1):  # 只顯示前10個
            safe_print(f"  {i}. {file.name}")
        if len(files) > 10:
            safe_print(f"  ... 還有 {len(files) - 10} 個檔案")
            
        confirm = input(f"\n確認翻譯這 {len(files)} 個檔案？(Y/n): ").strip().lower()
        
        if confirm not in ['', 'y', 'yes', '是']:
            safe_print("❌ 已取消批量翻譯")
            return
            
        safe_print(f"\n🚀 開始批量翻譯...")
        tracker.start_tracking(len(files))
        
        results = translator.batch_translate_directory(str(directory), pattern)
        
        safe_print(f"\n🎉 批量翻譯完成!")
        safe_print(f"✅ 成功: {results['success']} 個")
        safe_print(f"❌ 失敗: {results['failed']} 個")
        
        if results['success'] > 0:
            evaluate = input("是否對成功翻譯的檔案進行品質評估？(Y/n): ").strip().lower()
            if evaluate in ['', 'y', 'yes', '是']:
                self._batch_evaluate_translations(results['files'])
                
    def _scan_untranslated_files(self) -> None:
        """掃描待翻譯檔案"""
        safe_print("\n🔍 掃描待翻譯檔案")
        safe_print("-" * 30)
        
        translations_dir = Path("docs/translations")
        
        if not translations_dir.exists():
            safe_print("❌ 翻譯目錄不存在")
            return
            
        untranslated_files = []
        
        for book_dir in translations_dir.iterdir():
            if not book_dir.is_dir():
                continue
                
            for file in book_dir.glob("*.md"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # 檢查是否已翻譯
                    if "🔄 待翻譯" in content or "[請在此處填入翻譯內容]" in content:
                        untranslated_files.append(file)
                        
                except Exception:
                    continue
                    
        if not untranslated_files:
            safe_print("✅ 所有檔案都已翻譯完成")
            return
            
        safe_print(f"📋 找到 {len(untranslated_files)} 個待翻譯檔案:")
        
        for i, file in enumerate(untranslated_files, 1):
            book_name = file.parent.name.split('_')[0]
            safe_print(f"  {i}. {book_name} - {file.name}")
            
        translate_all = input(f"\n是否翻譯所有待翻譯檔案？(Y/n): ").strip().lower()
        
        if translate_all in ['', 'y', 'yes', '是']:
            from ai_translator import AITranslator, TranslationProgressTracker
            
            translator = AITranslator()
            tracker = TranslationProgressTracker()
            translator.set_progress_callback(tracker.update_progress)
            
            tracker.start_tracking(len(untranslated_files))
            
            success_count = 0
            for i, file in enumerate(untranslated_files, 1):
                safe_print(f"\n📝 進度: {i}/{len(untranslated_files)} - {file.name}")
                tracker.update_progress(i, len(untranslated_files), file.name)
                
                if translator.translate_file(str(file)):
                    success_count += 1
                    
            safe_print(f"\n🎉 批量翻譯完成!")
            safe_print(f"✅ 成功: {success_count}/{len(untranslated_files)} 個")
            
    def _evaluate_translation_quality(self) -> None:
        """翻譯品質評估"""
        safe_print("\n📊 翻譯品質評估")
        safe_print("-" * 30)
        
        file_path = input("請輸入要評估的翻譯檔案路徑: ").strip()
        
        if not file_path:
            safe_print("❌ 檔案路徑不能為空")
            return
            
        self._evaluate_file(file_path)
        
    def _evaluate_file(self, file_path: str) -> None:
        """評估單個檔案"""
        try:
            from ai_translation_evaluator import evaluate_translation_file
            evaluate_translation_file(file_path)
        except ImportError:
            safe_print("❌ 無法載入翻譯評估器")
        except Exception as e:
            safe_print(f"❌ 評估失敗: {e}")
            
    def _batch_evaluate_translations(self, file_results: List[Dict]) -> None:
        """批量評估翻譯品質"""
        safe_print("\n📊 開始批量品質評估...")
        
        success_files = [f for f in file_results if f['status'] == 'success']
        
        for i, file_info in enumerate(success_files, 1):
            safe_print(f"\n📊 評估進度: {i}/{len(success_files)} - {Path(file_info['file']).name}")
            self._evaluate_file(file_info['file'])
            
        safe_print(f"\n🎉 批量評估完成! 共評估 {len(success_files)} 個檔案")


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description="道教經典翻譯系統 v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例用法:
  python easy_cli.py --book "https://www.shidianguji.com/book/DZ0001"
  python easy_cli.py --list
  python easy_cli.py --batch
  python easy_cli.py --interactive
        """
    )
    
    parser.add_argument('--book', '-b', help='翻譯指定書籍URL')
    parser.add_argument('--list', '-l', action='store_true', help='列出所有書籍')
    parser.add_argument('--batch', action='store_true', help='批量翻譯所有啟用的書籍')
    parser.add_argument('--status', '-s', action='store_true', help='顯示系統狀態')
    parser.add_argument('--interactive', '-i', action='store_true', help='啟動互動模式')
    
    args = parser.parse_args()
    
    cli = EasyCLI()
    
    if args.book:
        cli.translate_book(args.book)
    elif args.list:
        cli.list_books()
    elif args.batch:
        cli.batch_translate()
    elif args.status:
        cli.show_status()
    elif args.interactive:
        cli.interactive_mode()
    else:
        # 預設啟動互動模式
        cli.interactive_mode()


if __name__ == "__main__":
    main()
