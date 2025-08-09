#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
from core.unicode_handler import safe_print
依賴檢查腳本

檢查系統依賴和配置是否正確設定
"""

import sys
import importlib
import json
from pathlib import Path


def check_python_version():
    """檢查 Python 版本"""
    safe_print("🐍 檢查 Python 版本...")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        safe_print(f"✅ Python {version.major}.{version.minor}.{version.micro} - 版本符合要求")
        return True
    else:
        safe_print(f"❌ Python {version.major}.{version.minor}.{version.micro} - 需要 Python 3.7+")
        return False


def check_required_packages():
    """檢查必要套件"""
    safe_print("\n📦 檢查必要套件...")
    
    required_packages = [
        ('requests', '網路請求'),
        ('bs4', 'HTML 解析'),
        ('pathlib', '路徑處理'),
        ('json', 'JSON 處理'),
        ('datetime', '時間處理')
    ]
    
    all_ok = True
    
    for package, description in required_packages:
        try:
            importlib.import_module(package)
            safe_print(f"✅ {package} - {description}")
        except ImportError:
            safe_print(f"❌ {package} - {description} (未安裝)")
            all_ok = False
    
    return all_ok


def check_optional_packages():
    """檢查可選套件"""
    safe_print("\n🔧 檢查可選套件...")
    
    optional_packages = [
        ('selenium', 'Selenium 網頁自動化'),
        ('lxml', 'XML/HTML 解析器'),
        ('pytest', '測試框架'),
        ('markdown', 'Markdown 處理')
    ]
    
    for package, description in optional_packages:
        try:
            importlib.import_module(package)
            safe_print(f"✅ {package} - {description}")
        except ImportError:
            safe_print(f"⚠️  {package} - {description} (未安裝，可選)")


def check_config_files():
    """檢查配置檔案"""
    safe_print("\n⚙️ 檢查配置檔案...")
    
    config_files = [
        ('config/settings.json', '主要配置檔案', True),
        ('config/settings.example.json', '範例配置檔案', True),
        ('requirements.txt', '依賴清單', True),
        ('.gitignore', 'Git 忽略檔案', False)
    ]
    
    all_ok = True
    
    for file_path, description, required in config_files:
        path = Path(file_path)
        if path.exists():
            safe_print(f"✅ {file_path} - {description}")
            
            # 檢查 JSON 檔案格式
            if file_path.endswith('.json'):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        json.load(f)
                    safe_print(f"   📄 JSON 格式正確")
                except json.JSONDecodeError as e:
                    safe_print(f"   ❌ JSON 格式錯誤: {e}")
                    all_ok = False
                    
        else:
            if required:
                safe_print(f"❌ {file_path} - {description} (缺少)")
                all_ok = False
            else:
                safe_print(f"⚠️  {file_path} - {description} (建議建立)")
    
    return all_ok


def check_directory_structure():
    """檢查目錄結構"""
    safe_print("\n📁 檢查目錄結構...")
    
    required_dirs = [
        ('core', '核心模組'),
        ('tools', 'CLI 工具'),
        ('config', '配置檔案'),
        ('data', '資料目錄'),
        ('docs', '文檔和輸出'),
        ('crawler', '爬蟲工具')
    ]
    
    all_ok = True
    
    for dir_path, description in required_dirs:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            safe_print(f"✅ {dir_path}/ - {description}")
        else:
            safe_print(f"❌ {dir_path}/ - {description} (缺少)")
            all_ok = False
    
    return all_ok


def check_main_files():
    """檢查主要檔案"""
    safe_print("\n📄 檢查主要檔案...")
    
    main_files = [
        ('main.py', '主要入口點'),
        ('core/__init__.py', '核心模組初始化'),
        ('tools/easy_cli.py', '簡易CLI工具'),
        ('docs/index.html', '網頁介面'),
        ('update_web_data.py', '網頁資料更新腳本')
    ]
    
    all_ok = True
    
    for file_path, description in main_files:
        path = Path(file_path)
        if path.exists():
            safe_print(f"✅ {file_path} - {description}")
        else:
            safe_print(f"❌ {file_path} - {description} (缺少)")
            all_ok = False
    
    return all_ok


def run_basic_tests():
    """執行基本功能測試"""
    safe_print("\n🧪 執行基本功能測試...")
    
    try:
        # 測試核心模組導入
        sys.path.append('.')
        from core import get_tracker, get_file_monitor
        safe_print("✅ 核心模組導入成功")
        
        # 測試追蹤器
        tracker = get_tracker()
        stats = tracker.get_statistics()
        safe_print(f"✅ 追蹤系統正常 (經典數: {stats.get('total_classics', 0)})")
        
        # 測試檔案監控
        monitor = get_file_monitor()
        file_stats = monitor.get_statistics()
        safe_print(f"✅ 檔案監控正常 (操作數: {file_stats.get('total_operations', 0)})")
        
        return True
        
    except Exception as e:
        safe_print(f"❌ 功能測試失敗: {e}")
        return False


def generate_report():
    """生成檢查報告"""
    safe_print("\n" + "=" * 60)
    safe_print("📋 依賴檢查報告")
    safe_print("=" * 60)
    
    checks = [
        ("Python 版本", check_python_version()),
        ("必要套件", check_required_packages()),
        ("配置檔案", check_config_files()),
        ("目錄結構", check_directory_structure()),
        ("主要檔案", check_main_files()),
        ("功能測試", run_basic_tests())
    ]
    
    # 檢查可選套件（不影響總體結果）
    check_optional_packages()
    
    # 統計結果
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    safe_print(f"\n📊 檢查結果: {passed}/{total} 項通過")
    
    if passed == total:
        safe_print("🎉 所有檢查都通過！系統已準備就緒。")
        return True
    else:
        safe_print("⚠️  部分檢查未通過，請根據上述提示進行修復。")
        return False


def main():
    """主函數"""
    safe_print("🔍 道教經典翻譯系統 v2.0 - 依賴檢查")
    safe_print("=" * 60)
    
    success = generate_report()
    
    if success:
        safe_print("\n💡 建議的下一步:")
        safe_print("   1. python main.py info - 查看系統資訊")
        safe_print("   2. python main.py translate --interactive - 啟動互動模式")
        safe_print("   3. python -m http.server 8000 --directory docs - 啟動網頁服務")
    else:
        safe_print("\n🔧 修復建議:")
        safe_print("   1. pip install -r requirements.txt - 安裝依賴套件")
        safe_print("   2. cp config/settings.example.json config/settings.json - 複製配置")
        safe_print("   3. 檢查並修復上述錯誤")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())