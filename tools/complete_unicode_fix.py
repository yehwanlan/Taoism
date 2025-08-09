#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的Unicode修復腳本
自動修復所有Python文件中的Unicode顯示問題
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

class UnicodeFixTool:
    """Unicode修復工具"""
    
    def __init__(self):
        self.fixed_files = []
        self.skipped_files = []
        self.error_files = []
    
    def fix_file(self, file_path: Path) -> bool:
        """修復單個文件"""
        try:
            # 讀取文件內容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 1. 添加Unicode處理器導入（如果需要）
            content = self._add_unicode_import(content, file_path)
            
            # 2. 替換print語句
            content = self._replace_print_statements(content)
            
            # 3. 檢查是否有變化
            if content != original_content:
                # 寫回文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.fixed_files.append(file_path)
                return True
            else:
                self.skipped_files.append(file_path)
                return False
                
        except Exception as e:
            self.error_files.append((file_path, str(e)))
            return False
    
    def _add_unicode_import(self, content: str, file_path: Path) -> str:
        """添加Unicode處理器導入"""
        # 檢查是否已經導入
        if 'from core.unicode_handler import safe_print' in content:
            return content
        
        # 檢查是否有print語句需要修復
        if not re.search(r'(?<!safe_)print\(', content):
            return content
        
        # 檢查是否是核心模組文件
        if 'core/' in str(file_path):
            import_line = 'from .unicode_handler import safe_print'
        else:
            import_line = 'from core.unicode_handler import safe_print'
        
        # 尋找合適的位置插入導入語句
        lines = content.split('\n')
        insert_index = 0
        
        # 跳過文件頭部註釋和編碼聲明
        for i, line in enumerate(lines):
            if line.strip().startswith('"""') and '"""' in line[3:]:
                insert_index = i + 1
                break
            elif line.strip().endswith('"""'):
                insert_index = i + 1
                break
            elif line.strip().startswith('import ') or line.strip().startswith('from '):
                insert_index = i
                break
        
        # 插入導入語句
        if insert_index < len(lines):
            # 檢查是否已經有其他導入語句
            has_imports = any(line.strip().startswith(('import ', 'from ')) for line in lines[insert_index:insert_index+10])
            
            if has_imports:
                # 找到最後一個導入語句的位置
                for i in range(insert_index, min(len(lines), insert_index + 20)):
                    if lines[i].strip().startswith(('import ', 'from ')):
                        insert_index = i + 1
                    elif lines[i].strip() == '':
                        continue
                    else:
                        break
            
            lines.insert(insert_index, import_line)
            content = '\n'.join(lines)
        
        return content
    
    def _replace_print_statements(self, content: str) -> str:
        """替換print語句為safe_print"""
        # 匹配 print( 但不匹配 safe_print(
        pattern = r'(?<!safe_)print\('
        replacement = 'safe_print('
        
        return re.sub(pattern, replacement, content)
    
    def fix_directory(self, directory: Path, recursive: bool = True) -> None:
        """修復目錄中的所有Python文件"""
        if recursive:
            python_files = directory.rglob('*.py')
        else:
            python_files = directory.glob('*.py')
        
        for file_path in python_files:
            # 跳過一些特殊文件
            if self._should_skip_file(file_path):
                continue
            
            print(f"處理: {file_path}")
            self.fix_file(file_path)
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """判斷是否應該跳過文件"""
        skip_patterns = [
            '__pycache__',
            '.git',
            'venv',
            'env',
            'test_unicode_fix.py',
            'complete_unicode_fix.py',
            'unicode_handler.py'
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)
    
    def print_summary(self) -> None:
        """打印修復摘要"""
        print("\n" + "=" * 60)
        print("Unicode修復摘要")
        print("=" * 60)
        
        print(f"✅ 修復的文件: {len(self.fixed_files)}")
        for file_path in self.fixed_files:
            print(f"   - {file_path}")
        
        print(f"\n⚠️  跳過的文件: {len(self.skipped_files)}")
        for file_path in self.skipped_files[:5]:  # 只顯示前5個
            print(f"   - {file_path}")
        if len(self.skipped_files) > 5:
            print(f"   ... 還有 {len(self.skipped_files) - 5} 個文件")
        
        if self.error_files:
            print(f"\n❌ 錯誤的文件: {len(self.error_files)}")
            for file_path, error in self.error_files:
                print(f"   - {file_path}: {error}")
        
        print(f"\n📊 總計: {len(self.fixed_files + self.skipped_files + [f[0] for f in self.error_files])} 個文件處理完成")

def main():
    """主函數"""
    print("🔧 完整Unicode修復工具")
    print("=" * 50)
    
    fixer = UnicodeFixTool()
    
    # 修復主要目錄
    directories_to_fix = [
        Path("core"),
        Path("tools"),
    ]
    
    for directory in directories_to_fix:
        if directory.exists():
            print(f"\n📁 處理目錄: {directory}")
            fixer.fix_directory(directory, recursive=False)
        else:
            print(f"⚠️  目錄不存在: {directory}")
    
    # 修復主文件
    main_files = [
        Path("main.py"),
        Path("check_dependencies.py"),
        Path("update_web_data.py"),
    ]
    
    print(f"\n📄 處理主要文件:")
    for file_path in main_files:
        if file_path.exists():
            print(f"處理: {file_path}")
            fixer.fix_file(file_path)
        else:
            print(f"⚠️  文件不存在: {file_path}")
    
    # 打印摘要
    fixer.print_summary()
    
    print("\n💡 修復完成！建議運行 python test_unicode_fix.py 測試效果")

if __name__ == "__main__":
    main()