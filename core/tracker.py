#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
from core.unicode_handler import safe_print
道教經典翻譯系統 - 經典追蹤核心

整合原有的 classic_tracker.py 功能，提供統一的追蹤介面
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class ClassicTracker:
    """經典追蹤器核心類"""
    
    def __init__(self, data_dir: Path = None):
        """初始化追蹤器"""
        self.data_dir = data_dir or Path("data/tracking")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.tracker_file = self.data_dir / "classics.json"
        self.load_tracker_data()
        
    def load_tracker_data(self) -> None:
        """載入追蹤資料"""
        if self.tracker_file.exists():
            try:
                with open(self.tracker_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.data = self._create_empty_data()
        else:
            self.data = self._create_empty_data()
            
    def _create_empty_data(self) -> Dict:
        """創建空的追蹤資料結構"""
        return {
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "version": "2.0",
                "total_classics": 0,
                "total_chapters": 0,
                "total_characters": 0
            },
            "classics": {}
        }
        
    def save_tracker_data(self) -> None:
        """儲存追蹤資料"""
        self.data["metadata"]["last_updated"] = datetime.now().isoformat()
        
        with open(self.tracker_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
            
    def generate_file_hash(self, file_path: Path) -> Optional[str]:
        """生成檔案雜湊值用於檢測變更"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return None
            
    def track_new_classic(self, book_info: Dict, chapters: List[Dict], 
                         source_dir: Path, translation_dir: Path) -> Dict:
        """追蹤新經典"""
        classic_id = book_info['id']
        folder_name = source_dir.name
        
        # 計算章節資訊
        chapter_details = []
        total_chars = 0
        
        for chapter in chapters:
            chapter_file = source_dir / "原文" / f"{chapter['number']:02d}_{chapter['title']}.txt"
            if chapter_file.exists():
                file_size = chapter_file.stat().st_size
                file_hash = self.generate_file_hash(chapter_file)
                
                # 計算字數
                try:
                    with open(chapter_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        char_count = len([c for c in content if '\u4e00' <= c <= '\u9fff'])
                        total_chars += char_count
                except Exception:
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
            "tags": self._generate_tags(book_info),
            "category": self._classify_classic(book_info)
        }
        
        # 記錄狀態
        if classic_id not in self.data["classics"]:
            safe_print(f"📚 新增經典: {book_info['title']}")
            classic_record["status"] = "新增"
        else:
            safe_print(f"🔄 更新經典: {book_info['title']}")
            classic_record["status"] = "更新"
            # 保留舊的添加時間
            old_record = self.data["classics"][classic_id]
            classic_record["added_time"] = old_record.get("added_time", classic_record["added_time"])
        
        self.data["classics"][classic_id] = classic_record
        
        # 更新統計
        self._update_statistics()
        self.save_tracker_data()
        
        return classic_record 
       
    def _generate_tags(self, book_info: Dict) -> List[str]:
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
        
    def _classify_classic(self, book_info: Dict) -> str:
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
            
    def _update_statistics(self) -> None:
        """更新統計資訊"""
        total_classics = len(self.data["classics"])
        total_chapters = sum(classic["chapter_count"] for classic in self.data["classics"].values())
        total_characters = sum(classic["total_characters"] for classic in self.data["classics"].values())
        
        self.data["metadata"].update({
            "total_classics": total_classics,
            "total_chapters": total_chapters,
            "total_characters": total_characters
        })
        
    def check_translation_progress(self) -> None:
        """檢查翻譯進度"""
        safe_print("🔍 檢查翻譯進度...")
        
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
                        except Exception:
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
        
    def get_statistics(self) -> Dict:
        """獲取統計資訊"""
        return self.data.get("metadata", {})
        
    def get_all_classics(self) -> Dict:
        """獲取所有經典"""
        return self.data.get("classics", {})
        
    def get_classic_by_id(self, classic_id: str) -> Optional[Dict]:
        """根據ID獲取經典"""
        return self.data["classics"].get(classic_id)
        
    def get_classics_by_category(self, category: str) -> List[Dict]:
        """根據分類獲取經典"""
        return [
            classic for classic in self.data["classics"].values()
            if classic.get("category") == category
        ]
        
    def get_classics_by_tag(self, tag: str) -> List[Dict]:
        """根據標籤獲取經典"""
        return [
            classic for classic in self.data["classics"].values()
            if tag in classic.get("tags", [])
        ]
        
    def generate_report(self) -> str:
        """生成詳細報告"""
        metadata = self.data.get("metadata", {})
        
        report = f"""# 📊 道教經典追蹤報告

**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**系統版本**: {metadata.get('version', '2.0')}

## 📈 總體統計

- **經典總數**: {metadata.get('total_classics', 0)} 部
- **章節總數**: {metadata.get('total_chapters', 0)} 章
- **總字數**: {metadata.get('total_characters', 0):,} 字
- **最後更新**: {metadata.get('last_updated', 'N/A')[:19].replace('T', ' ')}

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
*本報告由道教經典翻譯系統 v2.0 自動生成*
"""
        
        return report
        
    def save_report(self, filename: str = None) -> Path:
        """儲存報告到檔案"""
        if filename is None:
            filename = "tracking_report.md"
            
        report = self.generate_report()
        report_file = self.data_dir / filename
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
            
        safe_print(f"📋 報告已儲存: {report_file}")
        return report_file

    def get_untranslated_files(self) -> List[str]:
        """獲取所有未翻譯的原文檔名列表，會檢查翻譯檔案內容以確保不是只有模板。"""
        untranslated_files = []
        base_source_path = Path.cwd() / 'docs' / 'source_texts'

        for classic in self.data.get("classics", {}).values():
            source_dir = Path(classic.get("source_dir", ""))
            translation_dir = Path(classic.get("translation_dir", ""))
            
            if not source_dir.is_dir() or not translation_dir.is_dir():
                continue

            for chapter in classic.get("chapters", []):
                original_filename = f"{chapter['number']:02d}_{chapter['title']}.txt"
                translation_filename = f"{chapter['number']:02d}_{chapter['title']}.md"
                
                # Construct the full path to the original file
                original_file_path = source_dir / "原文" / original_filename
                translation_file_path = translation_dir / translation_filename

                is_translated = False
                if translation_file_path.exists():
                    try:
                        with open(translation_file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if '[此處應為現代中文翻譯]' not in content and len(content.strip()) > 500:
                                is_translated = True
                    except Exception:
                        pass

                if original_file_path.exists() and not is_translated:
                    try:
                        # This creates a path relative to the `docs/source_texts` directory
                        relative_path = original_file_path.relative_to(base_source_path)
                        untranslated_files.append(str(relative_path).replace('\\', '/'))
                    except ValueError:
                        # Fallback for cases where the path logic might fail
                        # This part might need adjustment if paths are not consistent
                        folder_name = source_dir.name
                        relative_fallback = f"{folder_name}/原文/{original_filename}"
                        untranslated_files.append(relative_fallback.replace('\\', '/'))

        return untranslated_files


# 全域追蹤器實例
_tracker_instance = None

def get_tracker() -> ClassicTracker:
    """獲取全域追蹤器實例"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = ClassicTracker()
    return _tracker_instance


# 全域追蹤器實例
_tracker_instance = None

def get_tracker() -> ClassicTracker:
    """獲取全域追蹤器實例"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = ClassicTracker()
    return _tracker_instance