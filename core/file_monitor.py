#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道教經典翻譯系統 - 檔案監控核心

整合原有的 file_tracker.py 功能，提供統一的檔案監控介面
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class FileMonitor:
    """檔案監控器核心類"""
    
    def __init__(self, data_dir: Path = None):
        """初始化檔案監控器"""
        self.data_dir = data_dir or Path("data/logs")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.data_dir / "file_operations.json"
        self.load_log_data()
        
    def load_log_data(self) -> None:
        """載入日誌資料"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    self.log_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.log_data = self._create_empty_log()
        else:
            self.log_data = self._create_empty_log()
            
    def _create_empty_log(self) -> Dict:
        """創建空的日誌資料結構"""
        return {
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "version": "2.0",
                "total_operations": 0
            },
            "operations": []
        }
        
    def save_log_data(self) -> None:
        """儲存日誌資料"""
        self.log_data["metadata"]["last_updated"] = datetime.now().isoformat()
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.log_data, f, ensure_ascii=False, indent=2)
            
    def calculate_file_hash(self, file_path: Path) -> Optional[str]:
        """計算檔案雜湊值"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return None
            
    def track_file_write(self, file_path: Path, file_type: str = "unknown", 
                        details: Dict = None) -> None:
        """追蹤檔案寫入操作"""
        file_path = Path(file_path)
        
        operation = {
            "timestamp": datetime.now().isoformat(),
            "operation": "create",
            "file_path": str(file_path).replace('\\', '/'),  # 統一使用正斜線
            "file_name": file_path.name,
            "file_size": file_path.stat().st_size if file_path.exists() else 0,
            "file_hash": self.calculate_file_hash(file_path) if file_path.exists() else None,
            "file_type": file_type,
            "details": details or {}
        }
        
        self.log_data["operations"].append(operation)
        self.log_data["metadata"]["total_operations"] += 1
        
        # 保持日誌大小合理（最多保留1000條記錄）
        if len(self.log_data["operations"]) > 1000:
            self.log_data["operations"] = self.log_data["operations"][-1000:]
            
        self.save_log_data()
        
        print(f"📝 記錄檔案操作: {operation['operation']} - {file_path.name}")
        
        # 如果是經典相關檔案，觸發自動分析
        if self._is_classic_file(file_path):
            self._analyze_classic_file(file_path)
            
    def _is_classic_file(self, file_path: Path) -> bool:
        """判斷是否為經典相關檔案"""
        path_parts = file_path.parts
        classic_indicators = ['source_texts', 'translations', '原文', '翻譯']
        
        return any(indicator in path_parts for indicator in classic_indicators)
        
    def _analyze_classic_file(self, file_path: Path) -> None:
        """分析經典檔案並觸發相關操作"""
        try:
            if 'source_texts' in file_path.parts:
                self._handle_source_file(file_path)
            elif 'translations' in file_path.parts:
                self._handle_translation_file(file_path)
                
        except Exception as e:
            print(f"⚠️  分析經典檔案失敗: {e}")
            
    def _handle_source_file(self, file_path: Path) -> None:
        """處理原文檔案"""
        path_parts = file_path.parts
        try:
            source_texts_idx = path_parts.index('source_texts')
            
            if source_texts_idx + 1 < len(path_parts):
                classic_folder = path_parts[source_texts_idx + 1]
                print(f"🔍 檢測到新的原文檔案: {classic_folder}")
                
        except ValueError:
            pass
            
    def _handle_translation_file(self, file_path: Path) -> None:
        """處理翻譯檔案"""
        print(f"📖 檢測到翻譯檔案更新: {file_path.name}")
        
    def get_recent_operations(self, limit: int = 10) -> List[Dict]:
        """獲取最近的操作記錄"""
        operations = self.log_data["operations"]
        return operations[-limit:] if operations else []
        
    def get_operations_by_type(self, file_type: str) -> List[Dict]:
        """根據檔案類型獲取操作記錄"""
        return [
            op for op in self.log_data["operations"]
            if op.get("file_type") == file_type
        ]
        
    def get_operations_by_date(self, date_str: str) -> List[Dict]:
        """根據日期獲取操作記錄"""
        return [
            op for op in self.log_data["operations"]
            if op["timestamp"].startswith(date_str)
        ]
        
    def get_statistics(self) -> Dict:
        """獲取統計資訊"""
        operations = self.log_data["operations"]
        
        if not operations:
            return {
                "total_operations": 0,
                "file_types": {},
                "daily_activity": {},
                "recent_activity": []
            }
            
        # 統計檔案類型
        file_types = {}
        daily_activity = {}
        
        for op in operations:
            # 檔案類型統計
            file_type = op.get("file_type", "unknown")
            file_types[file_type] = file_types.get(file_type, 0) + 1
            
            # 日期活動統計
            date = op["timestamp"][:10]
            daily_activity[date] = daily_activity.get(date, 0) + 1
            
        return {
            "total_operations": len(operations),
            "file_types": file_types,
            "daily_activity": daily_activity,
            "recent_activity": self.get_recent_operations(5)
        }
        
    def generate_activity_report(self) -> str:
        """生成活動報告"""
        stats = self.get_statistics()
        metadata = self.log_data.get("metadata", {})
        
        report = f"""# 📊 檔案操作活動報告

**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**系統版本**: {metadata.get('version', '2.0')}

## 📈 統計摘要

- **總操作數**: {stats['total_operations']}
- **最後更新**: {metadata.get('last_updated', 'N/A')[:19].replace('T', ' ')}

## 📁 檔案類型分佈

"""
        
        for file_type, count in stats['file_types'].items():
            report += f"- **{file_type}**: {count} 個檔案\n"
            
        report += "\n## 📅 每日活動統計\n\n"
        
        for date, count in sorted(stats['daily_activity'].items(), reverse=True)[:7]:
            report += f"- **{date}**: {count} 項操作\n"
            
        report += "\n## 🕒 最近活動\n\n"
        
        for op in reversed(stats['recent_activity']):
            timestamp = op['timestamp'][:19].replace('T', ' ')
            report += f"- **{timestamp}**: {op['operation']} - `{op['file_name']}`\n"
            
            # 顯示詳細資訊
            if op.get('details'):
                details = op['details']
                if 'title' in details:
                    report += f"  📖 標題: {details['title']}\n"
                if 'chapter_number' in details:
                    report += f"  📄 章節: 第{details['chapter_number']}章\n"
                    
        report += f"""

---
*本報告由道教經典翻譯系統 v2.0 自動生成*
"""
        
        return report
        
    def save_activity_report(self, filename: str = None) -> Path:
        """儲存活動報告到檔案"""
        if filename is None:
            filename = "activity_report.md"
            
        report = self.generate_activity_report()
        report_file = self.data_dir / filename
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
            
        print(f"📋 活動報告已儲存: {report_file}")
        return report_file


# 全域檔案監控器實例
_monitor_instance = None

def get_file_monitor() -> FileMonitor:
    """獲取全域檔案監控器實例"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = FileMonitor()
    return _monitor_instance