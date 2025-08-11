#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復所有 safe_print 導入問題的終極解決方案
"""

import os
import re
from pathlib import Path

def fix_safe_print_imports():
    """修復所有文件中的 safe_print 導入問題"""
    print("🔧 修復所有 safe_print 導入問題...")
    
    # 定義安全的 safe_print 函數代碼
    safe_print_code = '''
def safe_print(*args, **kwargs):
    """安全的打印函數，自動處理導入問題"""
    try:
        from core.unicode_handler import safe_print as _safe_print
        _safe_print(*args, **kwargs)
    except ImportError:
        try:
            import sys
            from pathlib import Path
            sys.path.append(str(Path(__file__).parent.parent))
            from core.unicode_handler import safe_print as _safe_print
            _safe_print(*args, **kwargs)
        except ImportError:
            print(*args, **kwargs)
    except Exception:
        print(*args, **kwargs)
'''
    
    # 需要修復的文件列表
    files_to_fix = [
        'core/translator.py',
        'tools/easy_cli.py',
        'crawler/smart_crawler.py',
        'crawler/shidian_simple.py',
        'crawler/shidian_crawler.py'
    ]
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            print(f"  修復: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 在文件開頭添加安全的 safe_print 函數
            if 'def safe_print(' not in content:
                # 找到第一個 import 語句後插入
                lines = content.split('\n')
                insert_index = 0
                
                for i, line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        insert_index = i + 1
                        break
                
                # 插入安全函數
                lines.insert(insert_index, safe_print_code)
                content = '\n'.join(lines)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"    ✅ 已添加安全的 safe_print 函數")
            else:
                print(f"    ⚠️  已存在 safe_print 函數，跳過")
    
    print("✅ 所有文件修復完成")

def main():
    """主函數"""
    print("🛠️  Safe Print 導入修復工具")
    print("=" * 50)
    
    # 切換到正確的目錄
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # 修復導入
    fix_safe_print_imports()
    
    print("\n🎉 修復完成！")
    print("💡 現在可以重新運行翻譯系統")

if __name__ == "__main__":
    main()