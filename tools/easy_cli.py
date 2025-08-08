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


class EasyCLI:
    """簡易命令列介面"""
    
    def __init__(self):
        """初始化CLI"""
        self.config_file = Path("config/settings.json")
        self.config = self._load_config()
        self.engine = TranslationEngine(self.config.get("translation", {}))
        self.tracker = get_tracker()
        
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
        if not name:
            name = f"書籍_{len(self.config['books']) + 1}"
            
        new_book = {
            "name": name,
            "url": url,
            "enabled": True,
            "translation_style": "classical",
            "notes": ""
        }
        
        self.config["books"].append(new_book)
        self._save_config()
        
        print(f"✅ 已添加書籍: {name}")
        print(f"📖 URL: {url}")
        
    def list_books(self) -> None:
        """列出所有書籍"""
        books = self.config.get("books", [])
        
        if not books:
            print("\n📚 尚未添加任何書籍")
            print("💡 選擇選項 2 添加新書籍")
            return
            
        print("\n📚 已配置的書籍列表:")
        print("=" * 60)
        
        for i, book in enumerate(books, 1):
            status_icon = "✅" if book.get("enabled", True) else "❌"
            status_text = "啟用" if book.get("enabled", True) else "停用"
            
            print(f"{i}. {status_icon} {book['name']}")
            print(f"   🔗 {book['url']}")
            if book.get('notes'):
                print(f"   📝 {book['notes']}")
            print(f"   📊 狀態: {status_text}")
            print()
            
    def translate_book(self, url: str) -> bool:
        """翻譯單本書籍"""
        print("🚀 啟動道教經典翻譯系統")
        print("=" * 50)
        
        try:
            success = self.engine.translate_book(url)
            
            if success:
                print("\n🎉 翻譯完成！")
                print("📊 正在生成追蹤報告...")
                
                # 生成追蹤報告
                self.tracker.check_translation_progress()
                report_file = self.tracker.save_report()
                
                print(f"📋 追蹤報告: {report_file}")
                
            return success
            
        except Exception as e:
            print(f"❌ 翻譯過程發生錯誤: {e}")
            return False
            
    def batch_translate(self) -> None:
        """批量翻譯所有啟用的書籍"""
        books = [book for book in self.config.get("books", []) if book.get("enabled", True)]
        
        if not books:
            print("📚 沒有啟用的書籍可供翻譯")
            print("💡 請先使用 --book 添加書籍或使用 --list 查看現有書籍")
            return
            
        print(f"🚀 開始批量翻譯 {len(books)} 本書籍")
        print("=" * 60)
        
        success_count = 0
        
        for i, book in enumerate(books, 1):
            print(f"\n📖 處理第 {i}/{len(books)} 本: {book['name']}")
            print("-" * 40)
            
            try:
                success = self.translate_book(book['url'])
                if success:
                    success_count += 1
                    print(f"✅ 第 {i} 本書處理完成")
                else:
                    print(f"❌ 第 {i} 本書處理失敗")
                    
            except Exception as e:
                print(f"❌ 處理第 {i} 本書時發生錯誤: {e}")
                
            print("-" * 40)
            
        print(f"\n🎊 批量翻譯完成！")
        print(f"✅ 成功: {success_count}/{len(books)} 本")
        print("💡 提示：翻譯模板已生成，您可以直接編輯翻譯內容")
        
    def show_status(self) -> None:
        """顯示系統狀態"""
        print("📊 道教經典翻譯系統狀態")
        print("=" * 50)
        
        # 追蹤系統統計
        stats = self.tracker.get_statistics()
        print(f"📚 經典總數: {stats.get('total_classics', 0)}")
        print(f"📖 章節總數: {stats.get('total_chapters', 0)}")
        print(f"📝 總字數: {stats.get('total_characters', 0):,}")
        print(f"🕒 最後更新: {stats.get('last_updated', 'N/A')[:19].replace('T', ' ')}")
        
        # 配置統計
        books = self.config.get("books", [])
        enabled_books = [book for book in books if book.get("enabled", True)]
        
        print(f"\n📋 配置統計:")
        print(f"📚 已配置書籍: {len(books)}")
        print(f"✅ 啟用書籍: {len(enabled_books)}")
        
    def interactive_mode(self) -> None:
        """互動模式"""
        print("🌟 歡迎使用道教經典翻譯系統 v2.0")
        print("=" * 50)
        
        while True:
            try:
                print("\n請選擇操作：")
                print("1. 📚 查看書籍列表")
                print("2. ➕ 添加新書籍")
                print("3. 📖 翻譯指定書籍")
                print("4. 🚀 批量翻譯所有書籍")
                print("5. 📊 查看系統狀態")
                print("6. 🔍 監控儀表板")
                print("7. 📋 生成報告")
                print("8. ❓ 幫助說明")
                print("9. 👋 退出程式")
                
                choice = input("\n請輸入選項 (1-9): ").strip()
                
                if choice == "1":
                    self.list_books()
                    
                elif choice == "2":
                    url = input("請輸入書籍URL: ").strip()
                    if url:
                        name = input("請輸入書籍名稱 (可選，按Enter跳過): ").strip()
                        self.add_book(url, name if name else None)
                    else:
                        print("❌ URL不能為空")
                        
                elif choice == "3":
                    print("\n選擇翻譯方式：")
                    print("a. 從配置列表中選擇")
                    print("b. 直接輸入新的URL")
                    
                    sub_choice = input("請選擇 (a/b): ").strip().lower()
                    
                    if sub_choice == "a":
                        self.list_books()
                        books = self.config.get("books", [])
                        if books:
                            try:
                                index = int(input("請選擇書籍編號: ")) - 1
                                if 0 <= index < len(books):
                                    book = books[index]
                                    print(f"🚀 開始翻譯: {book['name']}")
                                    self.translate_book(book["url"])
                                else:
                                    print("❌ 無效的編號")
                            except ValueError:
                                print("❌ 請輸入有效的數字")
                    elif sub_choice == "b":
                        url = input("請直接貼上書籍URL: ").strip()
                        if url:
                            self.translate_book(url)
                        else:
                            print("❌ URL不能為空")
                    else:
                        print("❌ 無效的選項")
                        
                elif choice == "4":
                    confirm = input("確定要批量翻譯所有啟用的書籍嗎？(y/N): ").strip().lower()
                    if confirm == 'y':
                        self.batch_translate()
                    else:
                        print("❌ 已取消批量翻譯")
                        
                elif choice == "5":
                    self.show_status()
                    
                elif choice == "6":
                    print("🔍 啟動監控儀表板...")
                    from .monitor_cli import MonitorCLI
                    monitor = MonitorCLI()
                    monitor.generate_dashboard()
                    
                elif choice == "7":
                    print("📋 正在生成報告...")
                    from .monitor_cli import MonitorCLI
                    monitor = MonitorCLI()
                    monitor.generate_reports()
                    
                elif choice == "8":
                    self._show_interactive_help()
                    
                elif choice == "9":
                    print("👋 感謝使用道教經典翻譯系統！")
                    break
                    
                else:
                    print("❌ 無效的選項，請輸入 1-9 之間的數字")
                    
            except KeyboardInterrupt:
                print("\n👋 再見！")
                break
            except Exception as e:
                print(f"❌ 發生錯誤: {e}")
                print("💡 請重新選擇操作")
                
    def _show_interactive_help(self) -> None:
        """顯示互動模式幫助"""
        print("""
📖 道教經典翻譯系統 v2.0 - 使用說明

🎯 主要功能:
  1. 📚 書籍管理 - 查看、添加、管理書籍配置
  2. 🤖 自動翻譯 - 一鍵完成爬取和翻譯模板生成
  3. 📊 進度追蹤 - 實時監控翻譯進度和統計
  4. 📋 報告生成 - 詳細的統計報告和分析

🚀 快速開始:
  • 選擇選項 2 添加新書籍URL
  • 選擇選項 3 開始翻譯（可直接貼上URL）
  • 選擇選項 6 查看監控儀表板

💡 小貼士:
  • 支援十典古籍網 (shidianguji.com) 的書籍URL
  • 翻譯完成後會自動生成模板，可直接編輯
  • 使用選項 5 隨時查看系統狀態

📞 需要幫助？
  • 查看 docs/system/ 目錄的詳細文檔
  • 使用 python main.py --help 查看命令列選項
""")


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