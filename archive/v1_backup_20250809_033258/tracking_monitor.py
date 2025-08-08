#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
追蹤監控工具

功能：
1. 實時顯示追蹤狀態
2. 監控檔案變更
3. 生成即時報告
4. 提供追蹤統計
"""

import json
import time
from datetime import datetime
from pathlib import Path
from classic_tracker import get_tracker, generate_tracking_report
from file_tracker import get_file_tracker

class TrackingMonitor:
    """追蹤監控器"""
    
    def __init__(self):
        self.classic_tracker = get_tracker()
        self.file_tracker = get_file_tracker()
        
    def show_current_status(self):
        """顯示當前狀態"""
        print("📊 經典追蹤系統狀態")
        print("=" * 50)
        
        # 經典追蹤統計
        metadata = self.classic_tracker.data.get("metadata", {})
        print(f"📚 經典總數: {metadata.get('total_classics', 0)}")
        print(f"📖 章節總數: {metadata.get('total_chapters', 0)}")
        print(f"📝 總字數: {metadata.get('total_characters', 0):,}")
        print(f"🕒 最後更新: {metadata.get('last_updated', 'N/A')[:19].replace('T', ' ')}")
        
        print("\n" + "-" * 30)
        
        # 檔案操作統計
        file_metadata = self.file_tracker.log_data.get("metadata", {})
        print(f"📁 檔案操作總數: {file_metadata.get('total_operations', 0)}")
        print(f"🕒 檔案追蹤更新: {file_metadata.get('last_updated', 'N/A')[:19].replace('T', ' ')}")
        
    def show_recent_activity(self, limit=5):
        """顯示最近活動"""
        print(f"\n🕒 最近 {limit} 項活動")
        print("-" * 30)
        
        recent_ops = self.file_tracker.get_recent_operations(limit)
        
        if not recent_ops:
            print("暫無活動記錄")
            return
            
        for op in reversed(recent_ops):
            timestamp = op['timestamp'][:19].replace('T', ' ')
            operation = op['operation']
            file_name = op['file_name']
            
            # 根據操作類型選擇圖示
            icon = "📝" if operation == "create" else "🔄"
            
            print(f"{icon} {timestamp} - {operation}: {file_name}")
            
            # 顯示詳細資訊
            if op.get('details'):
                details = op['details']
                if 'title' in details:
                    print(f"   📖 標題: {details['title']}")
                if 'chapter_number' in details:
                    print(f"   📄 章節: 第{details['chapter_number']}章")
                    
    def show_translation_progress(self):
        """顯示翻譯進度"""
        print("\n📈 翻譯進度概覽")
        print("-" * 30)
        
        classics = self.classic_tracker.data.get("classics", {})
        
        if not classics:
            print("暫無經典記錄")
            return
            
        total_chapters = 0
        completed_chapters = 0
        
        for classic_id, classic in classics.items():
            book_title = classic['book_info']['title']
            trans_status = classic.get('translation_status', {})
            
            chapter_count = trans_status.get('total_chapters', 0)
            completed = trans_status.get('completed_chapters', 0)
            percentage = trans_status.get('completion_percentage', 0)
            
            total_chapters += chapter_count
            completed_chapters += completed
            
            # 進度條
            progress_bar = self.create_progress_bar(percentage)
            
            print(f"📚 {book_title}")
            print(f"   {progress_bar} {completed}/{chapter_count} ({percentage}%)")
            
        # 總體進度
        overall_percentage = (completed_chapters / total_chapters * 100) if total_chapters > 0 else 0
        overall_progress_bar = self.create_progress_bar(overall_percentage)
        
        print(f"\n🎯 總體進度:")
        print(f"   {overall_progress_bar} {completed_chapters}/{total_chapters} ({overall_percentage:.1f}%)")
        
    def create_progress_bar(self, percentage, width=20):
        """創建進度條"""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
        
    def show_category_breakdown(self):
        """顯示分類統計"""
        print("\n📊 分類統計")
        print("-" * 30)
        
        classics = self.classic_tracker.data.get("classics", {})
        categories = {}
        
        for classic in classics.values():
            category = classic.get('category', '未分類')
            if category not in categories:
                categories[category] = {'count': 0, 'chapters': 0}
            categories[category]['count'] += 1
            categories[category]['chapters'] += classic.get('chapter_count', 0)
            
        for category, stats in categories.items():
            print(f"📂 {category}: {stats['count']} 部, {stats['chapters']} 章")
            
    def generate_dashboard(self):
        """生成完整儀表板"""
        print("\n" + "=" * 60)
        print("🎛️  經典追蹤系統儀表板")
        print("=" * 60)
        
        self.show_current_status()
        self.show_recent_activity()
        self.show_translation_progress()
        self.show_category_breakdown()
        
        print("\n" + "=" * 60)
        print(f"📅 報告生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
    def watch_mode(self, interval=30):
        """監控模式 - 定期更新顯示"""
        print("👁️  啟動監控模式 (按 Ctrl+C 退出)")
        print(f"🔄 更新間隔: {interval} 秒")
        
        try:
            while True:
                # 清屏（在支援的終端中）
                import os
                os.system('cls' if os.name == 'nt' else 'clear')
                
                self.generate_dashboard()
                
                print(f"\n⏰ 下次更新: {interval} 秒後...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n👋 監控模式已退出")
            
    def export_status_json(self):
        """匯出狀態為JSON"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "classic_tracker": {
                "metadata": self.classic_tracker.data.get("metadata", {}),
                "classics_count": len(self.classic_tracker.data.get("classics", {}))
            },
            "file_tracker": {
                "metadata": self.file_tracker.log_data.get("metadata", {}),
                "recent_operations": self.file_tracker.get_recent_operations(10)
            }
        }
        
        status_file = Path("追蹤狀態.json")
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, ensure_ascii=False, indent=2)
            
        print(f"📄 狀態已匯出: {status_file}")
        return status_file

def main():
    """主函數"""
    import sys
    
    monitor = TrackingMonitor()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "status":
            monitor.show_current_status()
        elif command == "activity":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            monitor.show_recent_activity(limit)
        elif command == "progress":
            monitor.show_translation_progress()
        elif command == "dashboard":
            monitor.generate_dashboard()
        elif command == "watch":
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            monitor.watch_mode(interval)
        elif command == "export":
            monitor.export_status_json()
        else:
            print("❌ 未知命令")
            print("可用命令: status, activity, progress, dashboard, watch, export")
    else:
        # 預設顯示儀表板
        monitor.generate_dashboard()

if __name__ == "__main__":
    main()