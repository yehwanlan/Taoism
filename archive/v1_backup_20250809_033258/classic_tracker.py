#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
經典追蹤系統

功能：
1. 自動記錄新增的經典
2. 追蹤翻譯進度
3. 生成統計報告
4. 維護經典資料庫
"""

import json
import os
from datetime import datetime
from pathlib import Path
import hashlib

class ClassicTracker:
    """經典追蹤器"""
    
    def __init__(self):
        self.tracker_file = Path("經典追蹤記錄.json")
        self.load_tracker_data()
        
    def load_tracker_data(self):
        """載入追蹤資料"""
        if self.tracker_file.exists():
            with open(self.tracker_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "total_classics": 0,
                    "total_chapters": 0
                },
                "classics": {}
            }
            
    def save_tracker_data(self):
        """儲存追蹤資料"""
        self.data["metadata"]["last_updated"] = datetime.now().isoformat()
        
        with open(self.tracker_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
            
    def generate_file_hash(self, file_path):
        """生成檔案雜湊值用於檢測變更"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None
            
    def add_classic(self, book_info, chapters, source_dir, translation_dir):
        """添加新經典到追蹤系統"""
        classic_id = book_info['id']
        folder_name = Path(source_dir).name
        
        # 計算章節資訊
        chapter_details = []
        total_chars = 0
        
        for chapter in chapters:
            chapter_file = Path(source_dir) / "原文" / f"{chapter['number']:02d}_{chapter['title']}.txt"
            if chapter_file.exists():
                file_size = chapter_file.stat().st_size
                file_hash = self.generate_file_hash(chapter_file)
                
                # 計算字數
                try:
                    with open(chapter_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        char_count = len([c for c in content if '\u4e00' <= c <= '\u9fff'])
                        total_chars += char_count
                except:
                    char_count = 0
                    
                chapter_details.append({
                    "number": chapter['number'],
                    "title": chapter['title'],
                    "file_size": file_size,
                    "char_count": char_count,
                    "file_hash": file_hash,
                    "added_time": datetime.now().isoformat()
                })
        
        # 建立經典記錄
        classic_record = {
            "book_info": book_info,
            "folder_name": folder_name,
            "source_dir": str(source_dir),
            "translation_dir": str(translation_dir),
            "added_time": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "chapter_count": len(chapters),
            "total_characters": total_chars,
            "chapters": chapter_details,
            "translation_status": {
                "completed_chapters": 0,
                "total_chapters": len(chapters),
                "completion_percentage": 0.0,
                "last_translation_update": None
            },
            "tags": self.generate_tags(book_info),
            "category": self.classify_classic(book_info)
        }
        
        # 如果是新經典或有更新，記錄變更
        if classic_id not in self.data["classics"]:
            print(f"📚 新增經典: {book_info['title']}")
            classic_record["status"] = "新增"
        else:
            print(f"🔄 更新經典: {book_info['title']}")
            classic_record["status"] = "更新"
            # 保留舊的添加時間
            classic_record["added_time"] = self.data["classics"][classic_id].get("added_time", classic_record["added_time"])
        
        self.data["classics"][classic_id] = classic_record
        
        # 更新統計
        self.update_statistics()
        self.save_tracker_data()
        
        return classic_record
        
    def generate_tags(self, book_info):
        """根據書籍資訊生成標籤"""
        tags = []
        
        title = book_info['title'].lower()
        author = book_info.get('author', '').lower()
        
        # 根據書名生成標籤
        if '道德經' in title or '老子' in title:
            tags.extend(['道德經', '老子', '道家經典'])
        elif '抱朴子' in title:
            tags.extend(['抱朴子', '葛洪', '道教煉丹'])
        elif '太上' in title:
            tags.extend(['太上', '道教經典'])
        elif '元始' in title:
            tags.extend(['元始天尊', '道教神話'])
        elif '真經' in title or '經' in title:
            tags.extend(['道教經典', '經文'])
            
        # 根據作者生成標籤
        if '葛洪' in author:
            tags.extend(['東晉', '葛洪'])
        elif '佚名' in author or '未知' in author:
            tags.append('佚名')
            
        # 根據朝代生成標籤
        if '唐' in author:
            tags.append('唐代')
        elif '晉' in author:
            tags.append('晉代')
        elif '宋' in author:
            tags.append('宋代')
            
        return list(set(tags))  # 去重
        
    def classify_classic(self, book_info):
        """分類經典"""
        title = book_info['title'].lower()
        
        if '道德經' in title or '老子' in title:
            return '道家經典'
        elif '抱朴子' in title:
            return '道教理論'
        elif '太上' in title or '元始' in title:
            return '道教經文'
        elif '保命' in title or '長生' in title:
            return '養生修煉'
        elif '度人' in title:
            return '度化經典'
        else:
            return '其他道教文獻'
            
    def update_statistics(self):
        """更新統計資訊"""
        total_classics = len(self.data["classics"])
        total_chapters = sum(classic["chapter_count"] for classic in self.data["classics"].values())
        total_characters = sum(classic["total_characters"] for classic in self.data["classics"].values())
        
        self.data["metadata"].update({
            "total_classics": total_classics,
            "total_chapters": total_chapters,
            "total_characters": total_characters
        })
        
    def check_translation_progress(self):
        """檢查翻譯進度"""
        print("🔍 檢查翻譯進度...")
        
        for classic_id, classic in self.data["classics"].items():
            translation_dir = Path(classic["translation_dir"])
            completed = 0
            
            if translation_dir.exists():
                for chapter in classic["chapters"]:
                    trans_file = translation_dir / f"{chapter['number']:02d}_{chapter['title']}.md"
                    if trans_file.exists():
                        # 檢查是否有實際翻譯內容（不只是模板）
                        try:
                            with open(trans_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if '[此處應為現代中文翻譯]' not in content and len(content) > 1000:
                                    completed += 1
                        except:
                            pass
            
            # 更新翻譯狀態
            total = classic["chapter_count"]
            percentage = (completed / total * 100) if total > 0 else 0
            
            classic["translation_status"].update({
                "completed_chapters": completed,
                "completion_percentage": round(percentage, 1),
                "last_translation_update": datetime.now().isoformat()
            })
            
        self.save_tracker_data()
        
    def generate_report(self):
        """生成詳細報告"""
        report = f"""# 📊 道教經典追蹤報告

**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📈 總體統計

- **經典總數**: {self.data['metadata']['total_classics']} 部
- **章節總數**: {self.data['metadata']['total_chapters']} 章
- **總字數**: {self.data['metadata']['total_characters']:,} 字
- **最後更新**: {self.data['metadata']['last_updated'][:19].replace('T', ' ')}

## 📚 經典列表

"""
        
        # 按添加時間排序
        sorted_classics = sorted(
            self.data["classics"].items(),
            key=lambda x: x[1]["added_time"],
            reverse=True
        )
        
        for classic_id, classic in sorted_classics:
            book_info = classic["book_info"]
            trans_status = classic["translation_status"]
            
            report += f"""### {book_info['title']}

- **書籍ID**: {classic_id}
- **作者**: {book_info['author']}
- **分類**: {classic['category']}
- **章節數**: {classic['chapter_count']} 章
- **字數**: {classic['total_characters']:,} 字
- **添加時間**: {classic['added_time'][:19].replace('T', ' ')}
- **翻譯進度**: {trans_status['completed_chapters']}/{trans_status['total_chapters']} ({trans_status['completion_percentage']}%)
- **標籤**: {', '.join(classic['tags'])}
- **資料夾**: `{classic['folder_name']}`

"""
        
        # 按分類統計
        categories = {}
        for classic in self.data["classics"].values():
            category = classic["category"]
            if category not in categories:
                categories[category] = {"count": 0, "chapters": 0, "characters": 0}
            categories[category]["count"] += 1
            categories[category]["chapters"] += classic["chapter_count"]
            categories[category]["characters"] += classic["total_characters"]
            
        report += "## 📊 分類統計\n\n"
        for category, stats in categories.items():
            report += f"- **{category}**: {stats['count']} 部, {stats['chapters']} 章, {stats['characters']:,} 字\n"
            
        # 翻譯進度統計
        total_chapters = sum(c["chapter_count"] for c in self.data["classics"].values())
        completed_chapters = sum(c["translation_status"]["completed_chapters"] for c in self.data["classics"].values())
        overall_progress = (completed_chapters / total_chapters * 100) if total_chapters > 0 else 0
        
        report += f"""
## 🎯 翻譯進度總覽

- **總章節**: {total_chapters} 章
- **已完成**: {completed_chapters} 章
- **整體進度**: {overall_progress:.1f}%

---
*本報告由經典追蹤系統自動生成*
"""
        
        return report
        
    def save_report(self):
        """儲存報告到檔案"""
        report = self.generate_report()
        report_file = Path("經典追蹤報告.md")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
            
        print(f"📋 報告已儲存: {report_file}")
        return report_file

# 全域追蹤器實例
_tracker = None

def get_tracker():
    """獲取全域追蹤器實例"""
    global _tracker
    if _tracker is None:
        _tracker = ClassicTracker()
    return _tracker

def track_new_classic(book_info, chapters, source_dir, translation_dir):
    """追蹤新經典（供其他模組調用）"""
    tracker = get_tracker()
    return tracker.add_classic(book_info, chapters, source_dir, translation_dir)

def generate_tracking_report():
    """生成追蹤報告（供其他模組調用）"""
    tracker = get_tracker()
    tracker.check_translation_progress()
    return tracker.save_report()

if __name__ == "__main__":
    # 命令列使用
    tracker = ClassicTracker()
    tracker.check_translation_progress()
    report_file = tracker.save_report()
    print(f"\n📊 追蹤報告已生成: {report_file}")