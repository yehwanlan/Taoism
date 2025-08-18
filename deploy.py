#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道教經典翻譯系統 - 一鍵部署腳本
支援多種部署方式：GitHub Pages、Docker、本地服務
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path
from datetime import datetime

class TaoismDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.docs_dir = self.project_root / "docs"
        
    def check_requirements(self):
        """檢查部署需求"""
        print("🔍 檢查部署需求...")
        
        # 檢查 Python 版本
        if sys.version_info < (3, 7):
            print("❌ 需要 Python 3.7+")
            return False
            
        # 檢查必要檔案
        required_files = [
            "main.py", "requirements.txt", "docs/index.html",
            "config/settings.example.json"
        ]
        
        for file in required_files:
            if not (self.project_root / file).exists():
                print(f"❌ 缺少必要檔案: {file}")
                return False
                
        print("✅ 部署需求檢查通過")
        return True
    
    def prepare_deployment(self):
        """準備部署"""
        print("📦 準備部署檔案...")
        
        # 確保配置檔案存在
        settings_file = self.project_root / "config" / "settings.json"
        example_file = self.project_root / "config" / "settings.example.json"
        
        if not settings_file.exists() and example_file.exists():
            shutil.copy(example_file, settings_file)
            print("✅ 複製配置檔案")
            
        # 更新網頁資料
        try:
            subprocess.run([sys.executable, "tools/temp/update_web_data.py"], 
                         cwd=self.project_root, check=True, capture_output=True)
            print("✅ 更新網頁資料")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ 網頁資料更新跳過（檔案不存在）")
            
        return True
    
    def deploy_github_pages(self):
        """部署到 GitHub Pages"""
        print("🚀 部署到 GitHub Pages...")
        
        try:
            # 檢查 Git 狀態
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True)
            
            if result.stdout.strip():
                print("📝 發現未提交的變更，正在提交...")
                subprocess.run(["git", "add", "."], check=True)
                subprocess.run(["git", "commit", "-m", 
                              f"Auto deploy: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"], 
                              check=True)
            
            # 推送到遠端
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("✅ 推送到 GitHub 完成")
            print("🌐 GitHub Pages 將在幾分鐘內更新")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ GitHub 部署失敗: {e}")
            return False
    
    def deploy_docker(self):
        """Docker 部署"""
        print("🐳 Docker 部署...")
        
        try:
            # 檢查 Docker
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            
            # 構建映像
            print("📦 構建 Docker 映像...")
            subprocess.run(["docker", "build", "-t", "taoism-translation:latest", "."], 
                          check=True)
            
            # 啟動服務
            print("🚀 啟動 Docker 服務...")
            subprocess.run(["docker-compose", "up", "-d"], check=True)
            
            print("✅ Docker 部署完成")
            print("🌐 服務運行在: http://localhost:8000")
            
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Docker 部署失敗（請確保已安裝 Docker）")
            return False
    
    def deploy_local(self, port=8000):
        """本地部署"""
        print(f"🏠 啟動本地服務 (端口: {port})...")
        
        try:
            print(f"🌐 服務將運行在: http://localhost:{port}")
            print("按 Ctrl+C 停止服務")
            
            subprocess.run([sys.executable, "-m", "http.server", str(port)], 
                          cwd=self.docs_dir)
            
        except KeyboardInterrupt:
            print("\n✅ 服務已停止")
    
    def create_release_package(self):
        """創建發布包"""
        print("📦 創建發布包...")
        
        release_dir = self.project_root / "release"
        release_dir.mkdir(exist_ok=True)
        
        # 創建時間戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_name = f"taoism-translation-v2.0-{timestamp}"
        package_dir = release_dir / package_name
        
        # 複製必要檔案
        essential_items = [
            "core", "tools", "docs", "config", "data",
            "main.py", "requirements.txt", "README.md", 
            "LICENSE", "pyproject.toml", "setup.py"
        ]
        
        package_dir.mkdir(exist_ok=True)
        
        for item in essential_items:
            src = self.project_root / item
            dst = package_dir / item
            
            if src.is_file():
                shutil.copy2(src, dst)
            elif src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
        
        # 創建壓縮包
        archive_path = release_dir / f"{package_name}.zip"
        shutil.make_archive(str(archive_path.with_suffix('')), 'zip', package_dir)
        
        # 清理臨時目錄
        shutil.rmtree(package_dir)
        
        print(f"✅ 發布包已創建: {archive_path}")
        return archive_path

def main():
    """主函數"""
    deployer = TaoismDeployer()
    
    print("🏛️ 道教經典翻譯系統 - 一鍵部署工具")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python deploy.py github     # 部署到 GitHub Pages")
        print("  python deploy.py docker     # Docker 部署")
        print("  python deploy.py local      # 本地服務")
        print("  python deploy.py package    # 創建發布包")
        print("  python deploy.py all        # 完整部署流程")
        return 1
    
    command = sys.argv[1].lower()
    
    # 檢查需求
    if not deployer.check_requirements():
        return 1
    
    # 準備部署
    if not deployer.prepare_deployment():
        return 1
    
    # 執行部署
    success = False
    
    if command == "github":
        success = deployer.deploy_github_pages()
    elif command == "docker":
        success = deployer.deploy_docker()
    elif command == "local":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
        deployer.deploy_local(port)
        success = True
    elif command == "package":
        deployer.create_release_package()
        success = True
    elif command == "all":
        print("🚀 執行完整部署流程...")
        package_path = deployer.create_release_package()
        github_success = deployer.deploy_github_pages()
        print(f"\n📊 部署結果:")
        print(f"   📦 發布包: {package_path}")
        print(f"   🌐 GitHub Pages: {'✅' if github_success else '❌'}")
        success = True
    else:
        print(f"❌ 未知命令: {command}")
        return 1
    
    if success:
        print("\n🎉 部署完成！")
        return 0
    else:
        print("\n❌ 部署失敗")
        return 1

if __name__ == "__main__":
    exit(main())