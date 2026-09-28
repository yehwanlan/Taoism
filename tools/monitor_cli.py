#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道教經典翻譯系統 - 監控命令列介面

整合原有的 tracking_monitor.py 功能，提供統一的監控介面
"""

import json
import time
import sys
from datetime import datetime
from pathlib import Path

# 添加父目錄到路徑以便導入核心模組
sys.path.append(str(Path(__file__).parent.parent))

from core import get_tracker, get_file_monitor
from core.unicode_handler import safe_print


class MonitorCLI:
    """監控命令列介面"""
    
    def __init__(self):
        """初始化監控CLI"""
        self.tracker = get_tracker()
        self.file_monitor = get_file_monitor()
        
    def show_status(self) -> None:
        """顯示當前狀態"""
        safe_print("📊 經典追蹤系統狀態")
        safe_print("=" * 50)
        
        # 經典追蹤統計
        stats = self.tracker.get_statistics()
        safe_print(f"📚 經典總數: {stats.get('total_classics', 0)}")
        safe_print(f"📖 章節總數: {stats.get('total_chapters', 0)}")
        safe_print(f"📝 總字數: {stats.get('total_characters', 0):,}")
        safe_print(f"🕒 最後更新: {stats.get('last_updated', 'N/A')[:19].replace('T', ' ')}")
        
        safe_print("\n" + "-" * 30)
        
        # 檔案操作統計
        file_stats = self.file_monitor.get_statistics()
        safe_print(f"📁 檔案操作總數: {file_stats['total_operations']}")
        
        if file_stats['file_types']:
            safe_print("📂 檔案類型分佈:")
            for file_type, count in file_stats['file_types'].items():
                safe_print(f"   {file_type}: {count}")
                
    def show_recent_activity(self, limit: int = 5) -> None:
        """顯示最近活動"""
        safe_print(f"\n🕒 最近 {limit} 項活動")
        safe_print("-" * 30)
        
        recent_ops = self.file_monitor.get_recent_operations(limit)
        
        if not recent_ops:
            safe_print("暫無活動記錄")
            return
            
        for op in reversed(recent_ops):
            timestamp = op['timestamp'][:19].replace('T', ' ')
            operation = op['operation']
            file_name = op['file_name']
            
            # 根據操作類型選擇圖示
            icon = "📝" if operation == "create" else "🔄"
            
            safe_print(f"{icon} {timestamp} - {operation}: {file_name}")
            
            # 顯示詳細資訊
            if op.get('details'):
                details = op['details']
                if 'title' in details:
                    safe_print(f"   📖 標題: {details['title']}")
                if 'chapter_number' in details:
                    safe_print(f"   📄 章節: 第{details['chapter_number']}章")
                    
    def show_translation_progress(self) -> None:
        """顯示翻譯進度"""
        safe_print("\n📈 翻譯進度概覽")
        safe_print("-" * 30)
        
        classics = self.tracker.get_all_classics()
        
        if not classics:
            safe_print("暫無經典記錄")
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
            progress_bar = self._create_progress_bar(percentage)
            
            safe_print(f"📚 {book_title}")
            safe_print(f"   {progress_bar} {completed}/{chapter_count} ({percentage}%)")
            
        # 總體進度
        overall_percentage = (completed_chapters / total_chapters * 100) if total_chapters > 0 else 0
        overall_progress_bar = self._create_progress_bar(overall_percentage)
        
        safe_print(f"\n🎯 總體進度:")
        safe_print(f"   {overall_progress_bar} {completed_chapters}/{total_chapters} ({overall_percentage:.1f}%)")
        
    def _create_progress_bar(self, percentage: float, width: int = 20) -> str:
        """創建進度條"""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
        
    def show_category_breakdown(self) -> None:
        """顯示分類統計"""
        safe_print("\n📊 分類統計")
        safe_print("-" * 30)
        
        classics = self.tracker.get_all_classics()
        categories = {}
        
        for classic in classics.values():
            category = classic.get('category', '未分類')
            if category not in categories:
                categories[category] = {'count': 0, 'chapters': 0}
            categories[category]['count'] += 1
            categories[category]['chapters'] += classic.get('chapter_count', 0)
            
        for category, stats in categories.items():
            safe_print(f"📂 {category}: {stats['count']} 部, {stats['chapters']} 章")
            
    def generate_dashboard(self) -> None:
        """生成完整儀表板"""
        safe_print("\n" + "=" * 60)
        safe_print("🎛️  經典追蹤系統儀表板 v2.0")
        safe_print("=" * 60)
        
        self.show_status()
        self.show_recent_activity()
        self.show_translation_progress()
        self.show_category_breakdown()
        
        safe_print("\n" + "=" * 60)
        safe_print(f"📅 報告生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        safe_print("=" * 60)
        
    def watch_mode(self, interval: int = 30) -> None:
        """監控模式 - 定期更新顯示"""
        safe_print("👁️  啟動監控模式 v2.0 (按 Ctrl+C 退出)")
        safe_print(f"🔄 更新間隔: {interval} 秒")
        
        try:
            while True:
                # 清屏（在支援的終端中）
                import os
                os.system('cls' if os.name == 'nt' else 'clear')
                
                self.generate_dashboard()
                
                safe_print(f"\n⏰ 下次更新: {interval} 秒後...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            safe_print("\n👋 監控模式已退出")
            
    def export_status_json(self) -> Path:
        """匯出狀態為JSON"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "version": "2.0",
            "classic_tracker": {
                "statistics": self.tracker.get_statistics(),
                "classics_count": len(self.tracker.get_all_classics())
            },
            "file_monitor": {
                "statistics": self.file_monitor.get_statistics(),
                "recent_operations": self.file_monitor.get_recent_operations(10)
            }
        }
        
        status_file = Path("data/tracking/system_status.json")
        status_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, ensure_ascii=False, indent=2)
            
        safe_print(f"📄 狀態已匯出: {status_file}")
        return status_file
        
    def generate_reports(self) -> None:
        """生成所有報告"""
        safe_print("📊 正在生成報告...")
        
        # 更新翻譯進度
        self.tracker.check_translation_progress()
        
        # 生成追蹤報告
        tracking_report = self.tracker.save_report("tracking_report.md")
        
        # 生成活動報告
        activity_report = self.file_monitor.save_activity_report("activity_report.md")
        
        # 匯出狀態
        status_file = self.export_status_json()
        
        safe_print("✅ 報告生成完成:")
        safe_print(f"   📋 追蹤報告: {tracking_report}")
        safe_print(f"   📊 活動報告: {activity_report}")
        safe_print(f"   📄 狀態檔案: {status_file}")


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="道教經典翻譯系統監控工具 v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例用法:
  python monitor_cli.py status
  python monitor_cli.py dashboard
  python monitor_cli.py watch 10
  python monitor_cli.py activity 20
        """
    )
    
    parser.add_argument('command', nargs='?', default='dashboard',
                       choices=['status', 'dashboard', 'progress', 'activity', 'watch', 'export', 'reports'],
                       help='要執行的命令')
    parser.add_argument('param', nargs='?', type=int, help='命令參數（如活動數量或監控間隔）')
    
    args = parser.parse_args()
    
    monitor = MonitorCLI()
    
    if args.command == 'status':
        monitor.show_status()
    elif args.command == 'dashboard':
        monitor.generate_dashboard()
    elif args.command == 'progress':
        monitor.show_translation_progress()
    elif args.command == 'activity':
        limit = args.param or 10
        monitor.show_recent_activity(limit)
    elif args.command == 'watch':
        interval = args.param or 30
        monitor.watch_mode(interval)
    elif args.command == 'export':
        monitor.export_status_json()
    elif args.command == 'reports':
        monitor.generate_reports()
    else:
        monitor.generate_dashboard()


if __name__ == "__main__":
    main()