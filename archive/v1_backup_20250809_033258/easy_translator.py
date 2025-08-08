#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡易古籍翻譯器

使用方法：
1. 直接運行：python easy_translator.py
2. 指定書籍：python easy_translator.py --book "書籍URL"
3. 批量處理：python easy_translator.py --batch
"""

import argparse
import json
from pathlib import Path
from auto_translator import AutoTranslator

class EasyTranslator:
    """簡易翻譯器控制介面"""
    
    def __init__(self):
        self.config_file = Path("config.json")
        self.load_config()
        
    def load_config(self):
        """載入配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {"books": []}
            
    def save_config(self):
        """儲存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
            
    def add_book(self, url, name=None):
        """添加新書籍"""
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
        self.save_config()
        print(f"✅ 已添加書籍: {name}")
        
    def list_books(self):
        """列出所有書籍"""
        if not self.config["books"]:
            print("📚 目前沒有配置任何書籍")
            return
            
        print("📚 已配置的書籍:")
        for i, book in enumerate(self.config["books"], 1):
            status = "✅" if book["enabled"] else "❌"
            print(f"{i}. {status} {book['name']} - {book['url']}")
            
    def translate_single_book(self, book_url):
        """翻譯單一書籍"""
        print(f"🚀 開始處理書籍: {book_url}")
        
        try:
            translator = AutoTranslator(book_url)
            success = translator.run_full_automation()
            
            if success:
                print("🎉 翻譯完成！")
                return True
            else:
                print("❌ 翻譯失敗")
                return False
                
        except Exception as e:
            print(f"❌ 發生錯誤: {e}")
            return False
            
    def translate_all_enabled_books(self):
        """翻譯所有啟用的書籍"""
        enabled_books = [book for book in self.config["books"] if book["enabled"]]
        
        if not enabled_books:
            print("❌ 沒有啟用的書籍")
            return
            
        print(f"🚀 開始批量處理 {len(enabled_books)} 本書籍")
        
        success_count = 0
        for book in enabled_books:
            print(f"\n📖 處理: {book['name']}")
            if self.translate_single_book(book['url']):
                success_count += 1
                
        print(f"\n🎊 批量處理完成！成功: {success_count}/{len(enabled_books)}")
        
    def interactive_mode(self):
        """互動模式"""
        print("🌟 歡迎使用簡易古籍翻譯器")
        print("=" * 40)
        
        while True:
            print("\n請選擇操作：")
            print("1. 查看書籍列表")
            print("2. 添加新書籍")
            print("3. 翻譯單一書籍")
            print("4. 批量翻譯所有書籍")
            print("5. 退出")
            
            choice = input("\n請輸入選項 (1-5): ").strip()
            
            if choice == "1":
                self.list_books()
                
            elif choice == "2":
                url = input("請輸入書籍URL: ").strip()
                name = input("請輸入書籍名稱 (可選): ").strip()
                if url:
                    self.add_book(url, name if name else None)
                    
            elif choice == "3":
                self.list_books()
                try:
                    index = int(input("請選擇書籍編號: ")) - 1
                    if 0 <= index < len(self.config["books"]):
                        book = self.config["books"][index]
                        self.translate_single_book(book["url"])
                    else:
                        print("❌ 無效的編號")
                except ValueError:
                    print("❌ 請輸入有效的數字")
                    
            elif choice == "4":
                self.translate_all_enabled_books()
                
            elif choice == "5":
                print("👋 再見！")
                break
                
            else:
                print("❌ 無效的選項，請重新選擇")

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="簡易古籍翻譯器")
    parser.add_argument("--book", help="指定要翻譯的書籍URL")
    parser.add_argument("--batch", action="store_true", help="批量翻譯所有啟用的書籍")
    parser.add_argument("--add", help="添加新書籍URL到配置")
    parser.add_argument("--list", action="store_true", help="列出所有配置的書籍")
    
    args = parser.parse_args()
    
    translator = EasyTranslator()
    
    if args.book:
        # 翻譯指定書籍
        translator.translate_single_book(args.book)
        
    elif args.batch:
        # 批量翻譯
        translator.translate_all_enabled_books()
        
    elif args.add:
        # 添加書籍
        name = input("請輸入書籍名稱: ").strip()
        translator.add_book(args.add, name if name else None)
        
    elif args.list:
        # 列出書籍
        translator.list_books()
        
    else:
        # 互動模式
        translator.interactive_mode()

if __name__ == "__main__":
    main()