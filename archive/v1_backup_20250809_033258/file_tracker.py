#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檔案追蹤系統

功能：
1. 監控檔案寫入操作
2. 自動記錄新增的經典檔案
3. 實時更新追蹤系統
4. 提供檔案變更歷史
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from classic_tracker import get_tracker, track_new_classic, generate_tracking_report

class FileTracker:
    """檔案追蹤器"""
    
    def __init__(self):
        self.tracker_log = Path("檔案追蹤日誌.json")
        self.load_log()
        
    def load_log(self):
        """載入追蹤日誌"""
        if self.tracker_log.exists():
            with open(self.tracker_log, 'r', encoding='utf-8') as f:
                self.log_data = json.load(f)
        else:
            self.log_data = {
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "total_operations": 0
                },
                "operations": []
            }
            
    def save_log(self):
        """儲存追蹤日誌"""
        self.log_data["metadata"]["last_updated"] = datetime.now().isoformat()
        
        with open(self.tracker_log, 'w', encoding='utf-8') as f:
            json.dump(self.log_data, f, ensure_ascii=False, indent=2)
            
    def calculate_file_hash(self, file_path):
        """計算檔案雜湊值"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None         
   
    def log_file_operation(self, operation_type, file_path, details=None):
        """記錄檔案操作"""
        file_path = Path(file_path)
        
        operation = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation_type,
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size": file_path.stat().st_size if file_path.exists() else 0,
            "file_hash": self.calculate_file_hash(file_path) if file_path.exists() else None,
            "details": details or {}
        }
        
        self.log_data["operations"].append(operation)
        self.log_data["metadata"]["total_operations"] += 1
        
        # 保持日誌大小合理（最多保留1000條記錄）
        if len(self.log_data["operations"]) > 1000:
            self.log_data["operations"] = self.log_data["operations"][-1000:]
            
        self.save_log()
        
        print(f"📝 記錄檔案操作: {operation_type} - {file_path.name}")
        
    def track_new_file(self, file_path, file_type="unknown"):
        """追蹤新檔案"""
        file_path = Path(file_path)
        
        # 記錄檔案操作
        self.log_file_operation("create", file_path, {
            "file_type": file_type,
            "parent_dir": str(file_path.parent)
        })
        
        # 如果是經典相關檔案，嘗試自動分析
        if self.is_classic_file(file_path):
            self.analyze_classic_file(file_path)
            
    def is_classic_file(self, file_path):
        """判斷是否為經典相關檔案"""
        file_path = Path(file_path)
        
        # 檢查路徑是否包含經典相關目錄
        path_parts = file_path.parts
        classic_indicators = ['source_texts', 'translations', '原文', '翻譯']
        
        return any(indicator in path_parts for indicator in classic_indicators)
        
    def analyze_classic_file(self, file_path):
        """分析經典檔案並更新追蹤系統"""
        file_path = Path(file_path)
        
        try:
            # 從路徑分析經典資訊
            if 'source_texts' in file_path.parts:
                # 這是原文檔案
                self.handle_source_file(file_path)
            elif 'translations' in file_path.parts:
                # 這是翻譯檔案
                self.handle_translation_file(file_path)
                
        except Exception as e:
            print(f"⚠️  分析經典檔案失敗: {e}")
            
    def handle_source_file(self, file_path):
        """處理原文檔案"""
        # 從路徑提取經典資訊
        path_parts = file_path.parts
        source_texts_idx = path_parts.index('source_texts')
        
        if source_texts_idx + 1 < len(path_parts):
            classic_folder = path_parts[source_texts_idx + 1]
            
            print(f"🔍 檢測到新的原文檔案: {classic_folder}")
            
            # 觸發追蹤系統更新
            self.trigger_tracking_update(classic_folder)
            
    def handle_translation_file(self, file_path):
        """處理翻譯檔案"""
        print(f"📖 檢測到翻譯檔案更新: {file_path.name}")
        
        # 更新翻譯進度
        self.update_translation_progress()
        
    def trigger_tracking_update(self, classic_folder):
        """觸發追蹤系統更新"""
        try:
            # 重新生成追蹤報告
            generate_tracking_report()
            print("✅ 追蹤系統已自動更新")
            
        except Exception as e:
            print(f"⚠️  自動更新追蹤系統失敗: {e}")
            
    def update_translation_progress(self):
        """更新翻譯進度"""
        try:
            tracker = get_tracker()
            tracker.check_translation_progress()
            print("📊 翻譯進度已更新")
            
        except Exception as e:
            print(f"⚠️  更新翻譯進度失敗: {e}")
            
    def get_recent_operations(self, limit=10):
        """獲取最近的操作記錄"""
        operations = self.log_data["operations"]
        return operations[-limit:] if operations else []
        
    def generate_activity_report(self):
        """生成活動報告"""
        operations = self.log_data["operations"]
        
        if not operations:
            return "📋 暫無檔案操作記錄"
            
        # 統計資訊
        total_ops = len(operations)
        create_ops = len([op for op in operations if op["operation"] == "create"])
        modify_ops = len([op for op in operations if op["operation"] == "modify"])
        
        # 最近活動
        recent_ops = self.get_recent_operations(5)
        
        report = f"""# 📊 檔案追蹤活動報告

**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📈 統計摘要

- **總操作數**: {total_ops}
- **新建檔案**: {create_ops}
- **修改檔案**: {modify_ops}
- **最後更新**: {self.log_data['metadata']['last_updated'][:19].replace('T', ' ')}

## 🕒 最近活動

"""
        
        for op in reversed(recent_ops):
            timestamp = op['timestamp'][:19].replace('T', ' ')
            report += f"- **{timestamp}**: {op['operation']} - `{op['file_name']}`\n"
            
        return report

# 全域檔案追蹤器
_file_tracker = None

def get_file_tracker():
    """獲取全域檔案追蹤器實例"""
    global _file_tracker
    if _file_tracker is None:
        _file_tracker = FileTracker()
    return _file_tracker

def track_file_write(file_path, file_type="unknown"):
    """追蹤檔案寫入（供其他模組調用）"""
    tracker = get_file_tracker()
    tracker.track_new_file(file_path, file_type)

def log_operation(operation_type, file_path, details=None):
    """記錄操作（供其他模組調用）"""
    tracker = get_file_tracker()
    tracker.log_file_operation(operation_type, file_path, details)

if __name__ == "__main__":
    # 命令列使用
    tracker = FileTracker()
    report = tracker.generate_activity_report()
    print(report)