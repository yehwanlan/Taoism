#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unicode處理器 - 解決Windows CMD Unicode顯示問題

主要功能：
1. 自動檢測系統編碼環境
2. 提供安全的Unicode輸出方法
3. 處理emoji和特殊字符的顯示問題
"""

import sys
import os
import locale
from typing import Optional

class UnicodeHandler:
    """Unicode處理器"""
    
    def __init__(self):
        self.system_encoding = self._detect_system_encoding()
        self.is_windows = os.name == 'nt'
        self.supports_unicode = self._check_unicode_support()
        
        # 嘗試設置UTF-8編碼
        self._setup_utf8_environment()
    
    def _detect_system_encoding(self) -> str:
        """檢測系統編碼"""
        try:
            # 嘗試獲取系統編碼
            encoding = locale.getpreferredencoding()
            return encoding
        except:
            return 'utf-8'
    
    def _check_unicode_support(self) -> bool:
        """檢查是否支持Unicode輸出"""
        try:
            # 測試輸出Unicode字符
            test_char = '🔍'
            test_char.encode(sys.stdout.encoding or 'utf-8')
            return True
        except (UnicodeEncodeError, AttributeError):
            return False
    
    def _setup_utf8_environment(self):
        """設置UTF-8環境"""
        if self.is_windows:
            try:
                # 嘗試設置控制台代碼頁為UTF-8
                os.system('chcp 65001 >nul 2>&1')
                
                # 重新配置stdout和stderr
                if hasattr(sys.stdout, 'reconfigure'):
                    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
                    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
                
            except Exception as e:
                pass  # 靜默處理，使用備用方案
    
    def safe_print(self, *args, **kwargs):
        """安全的打印函數，自動處理Unicode問題"""
        try:
            # 處理所有參數
            safe_args = []
            for arg in args:
                safe_args.append(self._make_safe_string(str(arg)))
            
            # 使用處理後的參數打印
            print(*safe_args, **kwargs)
            
        except UnicodeEncodeError:
            # 如果還是失敗，使用ASCII安全模式
            ascii_args = []
            for arg in args:
                ascii_args.append(self._to_ascii_safe(str(arg)))
            print(*ascii_args, **kwargs)
    
    def _make_safe_string(self, text: str) -> str:
        """將字符串轉換為安全輸出格式"""
        if self.supports_unicode:
            return text
        
        # 如果不支持Unicode，替換特殊字符
        replacements = {
            # Emoji替換
            '🔍': '[搜索]',
            '📚': '[書籍]',
            '📖': '[閱讀]',
            '📋': '[列表]',
            '📊': '[統計]',
            '🎯': '[目標]',
            '✅': '[成功]',
            '❌': '[失敗]',
            '⚠️': '[警告]',
            '🔄': '[處理]',
            '🤖': '[智能]',
            '🎉': '[完成]',
            '💡': '[建議]',
            '🚀': '[啟動]',
            '🔧': '[工具]',
            '📁': '[文件夾]',
            '📝': '[記錄]',
            '🧪': '[測試]',
            '🎊': '[慶祝]',
            '🔢': '[數字]',
            '🏛️': '[系統]',
            '🕷️': '[爬蟲]',
            '🔥': '[重要]',
            '🔶': '[中等]',
            '🔵': '[一般]',
            
            # 其他特殊字符
            '→': '->',
            '←': '<-',
            '↑': '^',
            '↓': 'v',
            '✓': 'OK',
            '✗': 'X',
            '●': '*',
            '○': 'o',
            '■': '#',
            '□': '[]',
        }
        
        result = text
        for unicode_char, replacement in replacements.items():
            result = result.replace(unicode_char, replacement)
        
        return result
    
    def _to_ascii_safe(self, text: str) -> str:
        """轉換為ASCII安全字符串"""
        try:
            # 嘗試編碼為ASCII，無法編碼的字符用?替換
            return text.encode('ascii', errors='replace').decode('ascii')
        except:
            # 最後的備用方案
            return ''.join(c if ord(c) < 128 else '?' for c in text)
    
    def get_status_info(self) -> dict:
        """獲取Unicode支持狀態信息"""
        return {
            'system_encoding': self.system_encoding,
            'is_windows': self.is_windows,
            'supports_unicode': self.supports_unicode,
            'stdout_encoding': getattr(sys.stdout, 'encoding', 'unknown'),
            'stderr_encoding': getattr(sys.stderr, 'encoding', 'unknown'),
        }

# 全局Unicode處理器實例
_unicode_handler = None

def get_unicode_handler() -> UnicodeHandler:
    """獲取全局Unicode處理器實例"""
    global _unicode_handler
    if _unicode_handler is None:
        _unicode_handler = UnicodeHandler()
    return _unicode_handler

def safe_print(*args, **kwargs):
    """全局安全打印函數"""
    handler = get_unicode_handler()
    handler.safe_print(*args, **kwargs)

def print_unicode_status():
    """打印Unicode支持狀態"""
    handler = get_unicode_handler()
    status = handler.get_status_info()
    
    safe_print("=" * 50)
    safe_print("Unicode支持狀態檢查")
    safe_print("=" * 50)
    safe_print(f"系統編碼: {status['system_encoding']}")
    safe_print(f"Windows系統: {status['is_windows']}")
    safe_print(f"支持Unicode: {status['supports_unicode']}")
    safe_print(f"stdout編碼: {status['stdout_encoding']}")
    safe_print(f"stderr編碼: {status['stderr_encoding']}")
    safe_print("=" * 50)

if __name__ == "__main__":
    # 測試Unicode處理器
    print_unicode_status()
    
    # 測試各種字符
    test_strings = [
        "🔍 測試搜索功能",
        "📚 書籍：南华真经口义",
        "✅ 成功處理：71/71 章",
        "🎉 翻譯完成！",
        "⚠️ 警告：編碼問題",
        "🤖 智能發現的子章節"
    ]
    
    safe_print("\n測試字符串輸出:")
    safe_print("-" * 30)
    
    for test_str in test_strings:
        safe_print(test_str)