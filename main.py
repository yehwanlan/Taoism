#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道教經典翻譯系統 v2.0 - 主要入口點

統一的系統入口，提供所有功能的存取介面
"""

import argparse
import sys
from pathlib import Path

# 添加當前目錄到路徑
sys.path.append(str(Path(__file__).parent))

from tools.easy_cli import EasyCLI
from tools.monitor_cli import MonitorCLI
from core import TranslationEngine, get_tracker, get_file_monitor


def show_system_info():
    """顯示系統資訊"""
    print("""
🏛️  道教經典翻譯系統 v2.0
================================

📚 功能模組:
  翻譯引擎    - 自動爬取和翻譯古籍
  追蹤系統    - 記錄和統計經典資訊
  檔案監控    - 追蹤檔案操作歷史
  CLI工具     - 命令列操作介面

🎯 主要功能:
  ✅ 全自動古籍翻譯
  ✅ 智能進度追蹤
  ✅ 實時檔案監控
  ✅ 統計報告生成
  ✅ 批量處理支援

📖 使用方法:
  python main.py translate --book "書籍URL"
  python main.py monitor dashboard
  python main.py --help

🔗 專案網址: https://github.com/your-repo/taoism-translation
""")


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description="道教經典翻譯系統 v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
子命令說明:
  translate    - 翻譯功能 (原 easy_translator.py)
  monitor      - 監控功能 (原 tracking_monitor.py)
  info         - 顯示系統資訊

範例用法:
  python main.py translate --book "https://www.shidianguji.com/book/DZ0001"
  python main.py translate --interactive
  python main.py monitor dashboard
  python main.py monitor watch 30
  python main.py info
        """
    )
    
    # 添加子命令
    subparsers = parser.add_subparsers(dest='command', help='可用的子命令')
    
    # 翻譯子命令
    translate_parser = subparsers.add_parser('translate', help='翻譯功能')
    translate_parser.add_argument('--book', '-b', help='翻譯指定書籍URL')
    translate_parser.add_argument('--list', '-l', action='store_true', help='列出所有書籍')
    translate_parser.add_argument('--batch', action='store_true', help='批量翻譯')
    translate_parser.add_argument('--status', '-s', action='store_true', help='顯示狀態')
    translate_parser.add_argument('--interactive', '-i', action='store_true', help='互動模式')
    
    # 監控子命令
    monitor_parser = subparsers.add_parser('monitor', help='監控功能')
    monitor_parser.add_argument('action', nargs='?', default='dashboard',
                               choices=['status', 'dashboard', 'progress', 'activity', 'watch', 'export', 'reports'],
                               help='監控動作')
    monitor_parser.add_argument('param', nargs='?', type=int, help='參數（數量或間隔）')
    
    # 資訊子命令
    info_parser = subparsers.add_parser('info', help='顯示系統資訊')
    
    args = parser.parse_args()
    
    # 如果沒有提供子命令，直接進入翻譯互動模式
    if not args.command:
        print("🏛️  道教經典翻譯系統 v2.0")
        print("=" * 40)
        print("💡 未指定命令，啟動互動模式...")
        print("   使用 'python main.py --help' 查看所有命令")
        
        cli = EasyCLI()
        cli.interactive_mode()
        return
    
    # 執行對應的子命令
    if args.command == 'translate':
        cli = EasyCLI()
        
        if args.book:
            cli.translate_book(args.book)
        elif args.list:
            cli.list_books()
        elif args.batch:
            cli.batch_translate()
        elif args.status:
            cli.show_status()
        elif args.interactive:
            cli.interactive_mode()
        else:
            cli.interactive_mode()
            
    elif args.command == 'monitor':
        monitor = MonitorCLI()
        
        if args.action == 'status':
            monitor.show_status()
        elif args.action == 'dashboard':
            monitor.generate_dashboard()
        elif args.action == 'progress':
            monitor.show_translation_progress()
        elif args.action == 'activity':
            limit = args.param or 10
            monitor.show_recent_activity(limit)
        elif args.action == 'watch':
            interval = args.param or 30
            monitor.watch_mode(interval)
        elif args.action == 'export':
            monitor.export_status_json()
        elif args.action == 'reports':
            monitor.generate_reports()
        else:
            monitor.generate_dashboard()
            
    elif args.command == 'info':
        show_system_info()
        
        # 顯示系統狀態
        print("\n📊 當前系統狀態:")
        print("-" * 30)
        
        tracker = get_tracker()
        stats = tracker.get_statistics()
        
        print(f"📚 經典總數: {stats.get('total_classics', 0)}")
        print(f"📖 章節總數: {stats.get('total_chapters', 0)}")
        print(f"📝 總字數: {stats.get('total_characters', 0):,}")
        
        file_monitor = get_file_monitor()
        file_stats = file_monitor.get_statistics()
        print(f"📁 檔案操作: {file_stats['total_operations']}")


if __name__ == "__main__":
    main()