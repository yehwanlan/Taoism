#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料夾重命名工具

將使用書籍ID的資料夾重命名為有意義的書名
"""

import os
import shutil
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import re

class FolderRenamer:
    """資料夾重命名工具"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_book_title_from_id(self, book_id):
        """從書籍ID獲取書名"""
        try:
            url = f"https://www.shidianguji.com/book/{book_id}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 嘗試多種方式提取標題
            title_selectors = [
                'h1.Goq6DYSE',
                'h1',
                '.book-title h1',
                '.title'
            ]
            
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title_text = title_elem.get_text().strip()
                    # 清理標題
                    title_text = re.sub(r'[-–—]\s*識典古籍.*$', '', title_text)
                    title_text = re.sub(r'\s*\|\s*.*$', '', title_text)
                    if len(title_text) > 2 and title_text != book_id:
                        return title_text
                        
            return None
            
        except Exception as e:
            print(f"⚠️  獲取書名失敗: {e}")
            return None
            
    def clean_folder_name(self, title, book_id):
        """清理資料夾名稱"""
        # 移除不適合作為資料夾名稱的字符
        clean_title = re.sub(r'[<>:"/\\|?*]', '_', title)
        clean_title = re.sub(r'\s+', '_', clean_title)
        clean_title = clean_title.strip('_')
        
        # 限制長度
        if len(clean_title) > 50:
            clean_title = clean_title[:50]
            
        return f"{clean_title}_{book_id}"
        
    def rename_folder(self, old_path, new_name):
        """重命名資料夾"""
        old_path = Path(old_path)
        new_path = old_path.parent / new_name
        
        if old_path.exists() and not new_path.exists():
            try:
                shutil.move(str(old_path), str(new_path))
                print(f"✅ 重命名成功: {old_path.name} → {new_name}")
                return True
            except Exception as e:
                print(f"❌ 重命名失敗: {e}")
                return False
        else:
            if not old_path.exists():
                print(f"⚠️  原資料夾不存在: {old_path}")
            if new_path.exists():
                print(f"⚠️  目標資料夾已存在: {new_path}")
            return False
            
    def scan_and_rename(self):
        """掃描並重命名所有需要的資料夾"""
        print("🔍 掃描需要重命名的資料夾...")
        
        # 掃描 source_texts 目錄
        source_dir = Path("docs/source_texts")
        translation_dir = Path("docs/translations")
        
        renamed_count = 0
        
        for folder_path in source_dir.iterdir():
            if folder_path.is_dir():
                folder_name = folder_path.name
                
                # 檢查是否是書籍ID格式（如 SBCK109, DZ0046）
                if re.match(r'^[A-Z]+\d+$', folder_name):
                    print(f"\n📖 處理資料夾: {folder_name}")
                    
                    # 獲取書名
                    book_title = self.get_book_title_from_id(folder_name)
                    
                    if book_title:
                        new_name = self.clean_folder_name(book_title, folder_name)
                        print(f"📚 書名: {book_title}")
                        print(f"📁 新名稱: {new_name}")
                        
                        # 重命名 source_texts 中的資料夾
                        if self.rename_folder(folder_path, new_name):
                            renamed_count += 1
                            
                            # 同時重命名 translations 中的對應資料夾
                            trans_folder = translation_dir / folder_name
                            if trans_folder.exists():
                                self.rename_folder(trans_folder, new_name)
                                
                    else:
                        print(f"❌ 無法獲取書名: {folder_name}")
                        
        print(f"\n🎉 重命名完成！成功重命名 {renamed_count} 個資料夾")
        
    def preview_changes(self):
        """預覽將要進行的更改"""
        print("👀 預覽重命名更改...")
        
        source_dir = Path("docs/source_texts")
        changes = []
        
        for folder_path in source_dir.iterdir():
            if folder_path.is_dir():
                folder_name = folder_path.name
                
                if re.match(r'^[A-Z]+\d+$', folder_name):
                    book_title = self.get_book_title_from_id(folder_name)
                    
                    if book_title:
                        new_name = self.clean_folder_name(book_title, folder_name)
                        changes.append({
                            'old': folder_name,
                            'new': new_name,
                            'title': book_title
                        })
                        
        if changes:
            print("\n📋 將要進行的更改:")
            print("=" * 60)
            for change in changes:
                print(f"📁 {change['old']}")
                print(f"   → {change['new']}")
                print(f"   📚 {change['title']}")
                print()
        else:
            print("✅ 沒有需要重命名的資料夾")
            
        return changes

def main():
    """主函數"""
    renamer = FolderRenamer()
    
    print("🏷️  資料夾重命名工具")
    print("=" * 40)
    
    # 先預覽更改
    changes = renamer.preview_changes()
    
    if changes:
        confirm = input(f"\n確定要重命名 {len(changes)} 個資料夾嗎？(y/N): ").strip().lower()
        
        if confirm == 'y':
            renamer.scan_and_rename()
        else:
            print("❌ 取消重命名操作")
    else:
        print("✅ 沒有需要處理的資料夾")

if __name__ == "__main__":
    main()