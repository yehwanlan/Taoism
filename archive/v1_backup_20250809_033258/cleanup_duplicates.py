#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理重複資料夾工具

清理只有ID的舊資料夾，保留有書名的新資料夾
"""

import shutil
from pathlib import Path
import re

def cleanup_duplicate_folders():
    """清理重複的資料夾"""
    print("🧹 清理重複資料夾工具")
    print("=" * 40)
    
    source_dir = Path("docs/source_texts")
    translation_dir = Path("docs/translations")
    
    # 找出所有只有ID的資料夾
    id_only_folders = []
    named_folders = []
    
    for folder in source_dir.iterdir():
        if folder.is_dir():
            folder_name = folder.name
            # 檢查是否只是ID格式
            if re.match(r'^[A-Z]+\d+$', folder_name):
                id_only_folders.append(folder)
            else:
                named_folders.append(folder)
    
    print(f"📁 找到 {len(id_only_folders)} 個只有ID的資料夾")
    print(f"📚 找到 {len(named_folders)} 個有書名的資料夾")
    
    if not id_only_folders:
        print("✅ 沒有需要清理的資料夾")
        return
    
    print("\n🗑️  將要刪除的資料夾:")
    for folder in id_only_folders:
        print(f"  - {folder.name}")
    
    confirm = input(f"\n確定要刪除這 {len(id_only_folders)} 個資料夾嗎？(y/N): ").strip().lower()
    
    if confirm == 'y':
        deleted_count = 0
        for folder in id_only_folders:
            try:
                # 刪除 source_texts 中的資料夾
                shutil.rmtree(folder)
                print(f"✅ 已刪除: {folder.name}")
                deleted_count += 1
                
                # 同時刪除 translations 中的對應資料夾
                trans_folder = translation_dir / folder.name
                if trans_folder.exists():
                    shutil.rmtree(trans_folder)
                    print(f"✅ 已刪除翻譯資料夾: {folder.name}")
                    
            except Exception as e:
                print(f"❌ 刪除失敗 {folder.name}: {e}")
        
        print(f"\n🎉 清理完成！成功刪除 {deleted_count} 個資料夾")
    else:
        print("❌ 取消清理操作")

def list_all_folders():
    """列出所有資料夾"""
    print("📋 當前所有資料夾:")
    print("=" * 40)
    
    source_dir = Path("docs/source_texts")
    
    for folder in sorted(source_dir.iterdir()):
        if folder.is_dir():
            folder_type = "🆔 ID格式" if re.match(r'^[A-Z]+\d+$', folder.name) else "📚 有書名"
            print(f"{folder_type}: {folder.name}")

if __name__ == "__main__":
    list_all_folders()
    print()
    cleanup_duplicate_folders()