#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道教經典翻譯系統 - 簡易命令列介面

整合原有的 easy_translator.py 功能，提供統一的CLI介面
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

# 添加父目錄到路徑以便導入核心模組
sys.path.append(str(Path(__file__).parent.parent))

from core import TranslationEngine, get_tracker
from core.ai_engine import AIEngine
from core.unicode_handler import safe_print, get_unicode_handler


class EasyCLI:
    """簡易命令列介面"""
    
    def __init__(self):
        """初始化CLI"""
        self.config_file = Path("config/settings.json")
        self.config = self._load_config()
        self.engine = TranslationEngine(self.config.get("translation", {}))
        self.tracker = get_tracker()
        self.ai_engine = AIEngine(self.config.get("ai", {}))
        
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
        
    def _get_book_title_from_url(self, url: str) -> str:
        """從URL自動獲取書籍標題"""
        try:
            from core.translator import TranslationEngine
            engine = TranslationEngine()
            book_info = engine.get_book_info(url)
            return book_info.get('title', f"書籍_{len(self.config['books']) + 1}")
        except Exception as e:
            safe_print(f"⚠️  無法自動獲取書名: {e}")
            return f"書籍_{len(self.config['books']) + 1}"
            

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
                        book_name = self._get_book_title_from_url(url)
                        self.add_book(url, book_name)
                        
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

    def _ai_translation_interface(self) -> None:
        """AI 智能翻譯互動介面"""
        safe_print("\n🤖 AI 智能翻譯")
        safe_print("=" * 50)
        
        # 使用 tracker 獲取進度
        # 注意：這裡需要一個方法從 tracker 獲取未翻譯列表
        # 假設 tracker 有一個 get_untranslated_files() 方法
        try:
            untranslated = self.tracker.get_untranslated_files()
        except Exception as e:
            safe_print(f"⚠️  警告: 獲取未翻譯列表時發生錯誤: {e}")
            untranslated = []

        if not untranslated:
            safe_print("🎉 恭喜！所有經文都已翻譯完成。")
            return

        safe_print("以下是尚未翻譯的經文列表：")
        for i, filename in enumerate(untranslated, 1):
            safe_print(f"{i}. {filename}")

        safe_print("\n請選擇要翻譯的經文：")
        safe_print("a. 翻譯所有未翻譯的經文")
        choice = input(f"請輸入編號 (1-{len(untranslated)}) 或 'a' 翻譯全部: ").strip().lower()

        if choice == 'a':
            safe_print("\n🚀 開始批量準備 AI 翻譯任務...")
            for filename in untranslated:
                self.ai_engine.prepare_translation_task(filename)
        else:
            try:
                index = int(choice) - 1
                if 0 <= index < len(untranslated):
                    filename = untranslated[index]
                    self.ai_engine.prepare_translation_task(filename)
                else:
                    safe_print("❌ 無效的編號。")
            except ValueError:
                safe_print("❌ 無效的輸入。")
                
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
        try:
            import sys
            from pathlib import Path
            sys.path.append(str(Path(__file__).parent))
            from template_generator import TemplateGenerator
            generator = TemplateGenerator()
            generator.interactive_template_generation()
        except ImportError:
            safe_print("❌ 無法載入模板生成器")
        except Exception as e:
            safe_print(f"❌ 模板生成失敗: {e}")
            
    def _create_translation_templates_for_book(self, url: str, book_name: str) -> None:
        """為指定書籍建立翻譯模板"""
        try:
            # 使用現有的翻譯系統來下載原文並生成模板
            safe_print("📥 正在下載書籍原文並生成翻譯模板...")
            success = self.translate_book(url)
            
            if success:
                safe_print("✅ 翻譯模板建立完成！")
                safe_print("💡 您現在可以在 docs/translations/ 目錄中找到翻譯模板")
            else:
                safe_print("❌ 翻譯模板建立失敗")
                safe_print("💡 您可以稍後使用選項 8 手動建立翻譯模板")
                
        except Exception as e:
            safe_print(f"❌ 建立翻譯模板失敗: {e}")
            safe_print("💡 您可以稍後使用選項 8 手動建立翻譯模板")
            
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
