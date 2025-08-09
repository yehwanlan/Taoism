#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道教經典翻譯系統 v2.0 - 安裝腳本
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """檢查 Python 版本"""
    if sys.version_info < (3, 7):
        print("❌ 需要 Python 3.7 或更高版本")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def install_dependencies():
    """安裝依賴套件"""
    print("📦 安裝依賴套件...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依賴套件安裝完成")
        return True
    except subprocess.CalledProcessError:
        print("❌ 依賴套件安裝失敗")
        return False

def setup_config():
    """設置配置檔案"""
    config_dir = Path("config")
    settings_file = config_dir / "settings.json"
    example_file = config_dir / "settings.example.json"
    
    if not settings_file.exists() and example_file.exists():
        print("⚙️ 複製配置檔案...")
        import shutil
        shutil.copy(example_file, settings_file)
        print("✅ 配置檔案設置完成")
    else:
        print("✅ 配置檔案已存在")

def main():
    """主安裝流程"""
    print("🏛️ 道教經典翻譯系統 v2.0 - 安裝程序")
    print("=" * 50)
    
    # 檢查 Python 版本
    if not check_python_version():
        return 1
    
    # 安裝依賴
    if not install_dependencies():
        return 1
    
    # 設置配置
    setup_config()
    
    print("\n🎉 安裝完成！")
    print("\n💡 下一步:")
    print("   python main.py info          # 查看系統資訊")
    print("   python main.py               # 啟動互動模式")
    
    return 0

if __name__ == "__main__":
    exit(main())