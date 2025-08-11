#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清除Python緩存並測試修復
"""

import os
import shutil
import sys
from pathlib import Path

# Add project root to path to allow importing core modules
sys.path.append(str(Path(__file__).parent))
from core.unicode_handler import safe_print

def clear_python_cache():
    """清除Python緩存文件"""
    safe_print("🧹 清除Python緩存...")
    
    # 清除 __pycache__ 目錄
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                cache_path = os.path.join(root, dir_name)
                safe_print(f"  刪除: {cache_path}")
                shutil.rmtree(cache_path, ignore_errors=True)
    
    # 清除 .pyc 文件
    for root, dirs, files in os.walk('.'):
        for file_name in files:
            if file_name.endswith('.pyc'):
                pyc_path = os.path.join(root, file_name)
                safe_print(f"  刪除: {pyc_path}")
                os.remove(pyc_path)
    
    safe_print("✅ 緩存清除完成")

def test_import():
    """測試導入是否正常"""
    safe_print("\n🔍 測試導入...")
    
    try:
        safe_print("✅ unicode_handler.safe_print 導入成功")
        
        from core.translator import TranslationEngine
        safe_print("✅ TranslationEngine 導入成功")
        
        # 測試 safe_print 功能
        safe_print("✅ safe_print 功能測試成功")
        
        # 創建翻譯引擎實例
        engine = TranslationEngine()
        safe_print("✅ TranslationEngine 實例創建成功")
        
        return True
        
    except Exception as e:
        safe_print(f"❌ 導入測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    safe_print("🔧 Python緩存清除和修復測試工具")
    safe_print("=" * 50)
    
    # 切換到正確的目錄
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # 清除緩存
    clear_python_cache()
    
    # 測試導入
    success = test_import()
    
    if success:
        safe_print("\n🎉 所有測試通過！")
        safe_print("💡 現在可以重新運行翻譯系統:")
        safe_print("   python main.py")
        safe_print("   或")
        safe_print("   python tools/easy_cli.py")
    else:
        safe_print("\n❌ 測試失敗，需要進一步調試")
        
    return success

if __name__ == "__main__":
    main()
