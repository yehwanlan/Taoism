#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
緊急修復 safe_print 問題
"""

import re
from pathlib import Path

def fix_translator_file():
    """修復 translator.py 文件中的所有 safe_print 調用"""
    translator_file = Path("core/translator.py")
    
    if not translator_file.exists():
        print("❌ translator.py 文件不存在")
        return False
    
    print("🔧 開始修復 translator.py...")
    
    # 讀取文件內容
    with open(translator_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 定義安全的打印函數
    safe_print_replacement = '''
# 安全的打印函數
def _safe_print(*args, **kwargs):
    """安全的打印函數，處理所有導入問題"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # 處理 Unicode 編碼問題
        safe_args = []
        for arg in args:
            try:
                safe_args.append(str(arg).encode('ascii', 'replace').decode('ascii'))
            except:
                safe_args.append('[無法顯示]')
        print(*safe_args, **kwargs)
    except Exception as e:
        print(f"打印錯誤: {e}")
'''
    
    # 在類定義之前插入安全函數
    class_pattern = r'(class TranslationEngine:)'
    if re.search(class_pattern, content):
        content = re.sub(class_pattern, safe_print_replacement + r'\n\1', content)
        print("✅ 已插入安全打印函數")
    
    # 替換所有 safe_print 調用為 _safe_print
    # 但不替換導入語句和函數定義
    patterns_to_replace = [
        (r'(?<!from .unicode_handler import )(?<!def )safe_print\(', '_safe_print('),
    ]
    
    for pattern, replacement in patterns_to_replace:
        old_content = content
        content = re.sub(pattern, replacement, content)
        if content != old_content:
            count = len(re.findall(pattern, old_content))
            print(f"✅ 替換了 {count} 個 safe_print 調用")
    
    # 移除原有的導入（因為我們不再需要它）
    content = re.sub(r'from \.unicode_handler import safe_print\n', '', content)
    
    # 寫回文件
    with open(translator_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ translator.py 修復完成")
    return True

def main():
    """主函數"""
    print("🚨 緊急修復工具")
    print("=" * 50)
    
    success = fix_translator_file()
    
    if success:
        print("\n🎉 修復完成！")
        print("💡 現在可以重新運行翻譯系統")
        print("   python main.py")
    else:
        print("\n❌ 修復失敗")

if __name__ == "__main__":
    main()