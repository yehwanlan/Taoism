#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復Unicode打印問題 - 批量替換print語句
"""

import re
import sys
from pathlib import Path

def fix_print_statements(file_path: Path):
    """修復文件中的print語句"""
    if not file_path.exists():
        safe_print(f"文件不存在: {file_path}")
        return False
    
    try:
        # 讀取文件內容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查是否已經導入了safe_print
        if 'from core.unicode_handler import safe_print' not in content:
            safe_print(f"跳過 {file_path}: 未導入safe_print")
            return False
        
        # 替換print語句為safe_print
        # 匹配 safe_print( 但不匹配 safe_print(
        pattern = r'(?<!safe_)print\('
        replacement = 'safe_print('
        
        new_content = re.sub(pattern, replacement, content)
        
        # 檢查是否有變化
        if new_content != content:
            # 寫回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # 統計替換次數
            count = len(re.findall(pattern, content))
            safe_print(f"✅ 修復 {file_path}: 替換了 {count} 個print語句")
            return True
        else:
            safe_print(f"⚠️  {file_path}: 沒有需要替換的print語句")
            return False
            
    except Exception as e:
        safe_print(f"❌ 處理 {file_path} 時出錯: {e}")
        return False

def main():
    """主函數"""
    safe_print("🔧 修復Unicode打印問題")
    safe_print("=" * 50)
    
    # 需要修復的文件列表
    files_to_fix = [
        Path("tools/easy_cli.py"),
        Path("tools/monitor_cli.py"),
        Path("core/translator.py"),
    ]
    
    success_count = 0
    
    for file_path in files_to_fix:
        if fix_print_statements(file_path):
            success_count += 1
    
    safe_print(f"\n📊 修復完成: {success_count}/{len(files_to_fix)} 個文件")
    safe_print("💡 請手動檢查修復結果並測試功能")

if __name__ == "__main__":
    main()