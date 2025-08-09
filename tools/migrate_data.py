#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
from core.unicode_handler import safe_print
資料遷移工具

將舊系統的資料遷移到新的模組化結構中
"""

import json
import shutil
from pathlib import Path
from datetime import datetime


class DataMigrator:
    """資料遷移器"""
    
    def __init__(self):
        """初始化遷移器"""
        self.root_dir = Path(".")
        self.old_files = {
            "經典追蹤記錄.json": "data/tracking/classics.json",
            "經典追蹤報告.md": "data/tracking/tracking_report.md",
            "檔案追蹤日誌.json": "data/logs/file_operations.json"
        }
        
    def migrate_tracking_data(self):
        """遷移追蹤資料"""
        safe_print("📊 遷移追蹤資料...")
        
        old_file = self.root_dir / "經典追蹤記錄.json"
        new_file = self.root_dir / "data/tracking/classics.json"
        
        if old_file.exists():
            # 確保目標目錄存在
            new_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 讀取舊資料
            with open(old_file, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
                
            # 清理測試資料
            if "classics" in old_data:
                # 移除測試經典
                old_data["classics"] = {
                    k: v for k, v in old_data["classics"].items()
                    if not k.startswith("TEST") and "測試" not in v.get("book_info", {}).get("title", "")
                }
                
                # 更新統計
                total_classics = len(old_data["classics"])
                total_chapters = sum(classic["chapter_count"] for classic in old_data["classics"].values())
                total_characters = sum(classic["total_characters"] for classic in old_data["classics"].values())
                
                old_data["metadata"].update({
                    "total_classics": total_classics,
                    "total_chapters": total_chapters,
                    "total_characters": total_characters,
                    "migrated_at": datetime.now().isoformat(),
                    "version": "2.0"
                })
                
            # 修復路徑格式（統一使用正斜線）
            for classic in old_data.get("classics", {}).values():
                if "source_dir" in classic:
                    classic["source_dir"] = classic["source_dir"].replace("\\", "/")
                if "translation_dir" in classic:
                    classic["translation_dir"] = classic["translation_dir"].replace("\\", "/")
                    
            # 寫入新檔案
            with open(new_file, 'w', encoding='utf-8') as f:
                json.dump(old_data, f, ensure_ascii=False, indent=2)
                
            safe_print(f"✅ 追蹤資料已遷移: {new_file}")
            
            # 備份舊檔案
            backup_file = self.root_dir / "backup" / f"經典追蹤記錄_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(old_file, backup_file)
            safe_print(f"📦 舊檔案已備份: {backup_file}")
            
        else:
            safe_print("⚠️  未找到舊的追蹤記錄檔案")
            
    def migrate_file_logs(self):
        """遷移檔案日誌"""
        safe_print("📁 遷移檔案日誌...")
        
        old_file = self.root_dir / "檔案追蹤日誌.json"
        new_file = self.root_dir / "data/logs/file_operations.json"
        
        if old_file.exists():
            # 確保目標目錄存在
            new_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 讀取舊資料
            with open(old_file, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
                
            # 清理測試資料和修復路徑
            if "operations" in old_data:
                cleaned_operations = []
                for op in old_data["operations"]:
                    # 跳過測試資料
                    if "測試" not in op.get("file_path", ""):
                        # 修復路徑格式
                        if "file_path" in op:
                            op["file_path"] = op["file_path"].replace("\\", "/")
                        cleaned_operations.append(op)
                        
                old_data["operations"] = cleaned_operations
                old_data["metadata"]["total_operations"] = len(cleaned_operations)
                old_data["metadata"]["migrated_at"] = datetime.now().isoformat()
                old_data["metadata"]["version"] = "2.0"
                
            # 寫入新檔案
            with open(new_file, 'w', encoding='utf-8') as f:
                json.dump(old_data, f, ensure_ascii=False, indent=2)
                
            safe_print(f"✅ 檔案日誌已遷移: {new_file}")
            
            # 備份舊檔案
            backup_file = self.root_dir / "backup" / f"檔案追蹤日誌_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(old_file, backup_file)
            safe_print(f"📦 舊檔案已備份: {backup_file}")
            
        else:
            safe_print("⚠️  未找到舊的檔案日誌")
            
    def migrate_reports(self):
        """遷移報告檔案"""
        safe_print("📋 遷移報告檔案...")
        
        old_files = [
            "經典追蹤報告.md",
            "追蹤狀態.json"
        ]
        
        for old_filename in old_files:
            old_file = self.root_dir / old_filename
            if old_file.exists():
                if old_filename.endswith('.md'):
                    new_file = self.root_dir / "data/tracking/tracking_report.md"
                else:
                    new_file = self.root_dir / "data/tracking/system_status.json"
                    
                # 確保目標目錄存在
                new_file.parent.mkdir(parents=True, exist_ok=True)
                
                # 複製檔案
                shutil.copy2(old_file, new_file)
                safe_print(f"✅ 已遷移: {old_filename} -> {new_file}")
                
                # 備份舊檔案
                backup_file = self.root_dir / "backup" / f"{old_filename}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                backup_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(old_file, backup_file)
                
    def archive_old_files(self):
        """歸檔舊檔案"""
        safe_print("📦 歸檔舊檔案...")
        
        # 要歸檔的檔案
        old_files = [
            "auto_translator.py",
            "easy_translator.py", 
            "classic_tracker.py",
            "file_tracker.py",
            "tracking_monitor.py",
            "update_tracker.py",
            "baopuzi_manager.py",
            "rename_folders.py",
            "cleanup_duplicates.py",
            "config.json",
            "GIT.txt",
            "GEMINI.md",
            "generate_scriptures_js.py",
            "專案狀態總結.md"
        ]
        
        archive_dir = self.root_dir / "archive" / f"v1_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        archived_count = 0
        for filename in old_files:
            old_file = self.root_dir / filename
            if old_file.exists():
                new_file = archive_dir / filename
                shutil.move(str(old_file), str(new_file))
                safe_print(f"📁 已歸檔: {filename}")
                archived_count += 1
                
        safe_print(f"✅ 已歸檔 {archived_count} 個檔案到: {archive_dir}")
        
    def clean_old_data_files(self):
        """清理舊的資料檔案"""
        safe_print("🧹 清理舊資料檔案...")
        
        old_data_files = [
            "經典追蹤記錄.json",
            "經典追蹤報告.md", 
            "檔案追蹤日誌.json",
            "追蹤狀態.json"
        ]
        
        for filename in old_data_files:
            old_file = self.root_dir / filename
            if old_file.exists():
                old_file.unlink()
                safe_print(f"🗑️  已刪除: {filename}")
                
    def run_migration(self):
        """執行完整遷移"""
        safe_print("🚀 開始資料遷移...")
        safe_print("=" * 50)
        
        try:
            # 1. 遷移追蹤資料
            self.migrate_tracking_data()
            
            # 2. 遷移檔案日誌
            self.migrate_file_logs()
            
            # 3. 遷移報告檔案
            self.migrate_reports()
            
            # 4. 歸檔舊檔案
            self.archive_old_files()
            
            # 5. 清理舊資料檔案
            self.clean_old_data_files()
            
            safe_print("\n🎉 遷移完成！")
            safe_print("=" * 50)
            safe_print("✅ 所有資料已成功遷移到新的模組化結構")
            safe_print("📦 舊檔案已備份到 backup/ 和 archive/ 目錄")
            safe_print("🚀 現在可以使用新的 main.py 介面")
            
        except Exception as e:
            safe_print(f"❌ 遷移過程發生錯誤: {e}")
            safe_print("💡 請檢查錯誤並重新執行遷移")


def main():
    """主函數"""
    migrator = DataMigrator()
    
    safe_print("📋 道教經典翻譯系統 - 資料遷移工具")
    safe_print("=" * 50)
    safe_print("此工具將把舊系統的資料遷移到新的模組化結構中")
    safe_print("⚠️  遷移前會自動備份所有舊檔案")
    
    confirm = input("\n確定要開始遷移嗎？(y/N): ").strip().lower()
    
    if confirm == 'y':
        migrator.run_migration()
    else:
        safe_print("❌ 遷移已取消")


if __name__ == "__main__":
    main()