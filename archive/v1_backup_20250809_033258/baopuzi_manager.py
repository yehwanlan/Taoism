#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抱朴子專案管理工具

用於管理抱朴子的爬取、翻譯和進度追蹤
"""

import os
import json
from pathlib import Path
from datetime import datetime

class BaopuziManager:
    """抱朴子專案管理器"""
    
    def __init__(self):
        self.project_root = Path("docs")
        self.source_dir = self.project_root / "source_texts" / "抱朴子"
        self.translation_dir = self.project_root / "translations" / "抱朴子"
        self.progress_file = self.project_root / "抱朴子_進度.json"
        
        # 確保目錄存在
        self.source_dir.mkdir(parents=True, exist_ok=True)
        self.translation_dir.mkdir(parents=True, exist_ok=True)
        
    def load_progress(self):
        """載入進度資料"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "chapters": {},
            "last_updated": None,
            "total_chapters": 0,
            "completed_translations": 0
        }
        
    def save_progress(self, progress_data):
        """儲存進度資料"""
        progress_data["last_updated"] = datetime.now().isoformat()
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
            
    def scan_chapters(self):
        """掃描已有的章節"""
        progress = self.load_progress()
        
        # 掃描原文
        source_files = list((self.source_dir / "原文").glob("*.txt"))
        
        # 掃描翻譯
        translation_files = list(self.translation_dir.glob("*.md"))
        
        for source_file in source_files:
            chapter_key = source_file.stem
            if chapter_key not in progress["chapters"]:
                progress["chapters"][chapter_key] = {
                    "title": self.extract_title_from_file(source_file),
                    "source_exists": True,
                    "translation_exists": False,
                    "source_file": str(source_file.relative_to(self.project_root)),
                    "translation_file": None,
                    "word_count": self.count_words(source_file)
                }
            else:
                progress["chapters"][chapter_key]["source_exists"] = True
                progress["chapters"][chapter_key]["word_count"] = self.count_words(source_file)
                
        for trans_file in translation_files:
            chapter_key = trans_file.stem
            if chapter_key in progress["chapters"]:
                progress["chapters"][chapter_key]["translation_exists"] = True
                progress["chapters"][chapter_key]["translation_file"] = str(trans_file.relative_to(self.project_root))
                
        # 更新統計
        progress["total_chapters"] = len(progress["chapters"])
        progress["completed_translations"] = sum(1 for ch in progress["chapters"].values() if ch["translation_exists"])
        
        self.save_progress(progress)
        return progress
        
    def extract_title_from_file(self, file_path):
        """從檔案中提取標題"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('#'):
                    return first_line[1:].strip()
                return file_path.stem
        except:
            return file_path.stem
            
    def count_words(self, file_path):
        """計算檔案字數"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 計算中文字符數
                chinese_chars = len([c for c in content if '\u4e00' <= c <= '\u9fff'])
                return chinese_chars
        except:
            return 0
            
    def generate_progress_report(self):
        """生成進度報告"""
        progress = self.scan_chapters()
        
        report = f"""# 抱朴子專案進度報告

**更新時間：** {progress.get('last_updated', '未知')}

## 總體進度

- **總章節數：** {progress['total_chapters']}
- **已完成翻譯：** {progress['completed_translations']}
- **翻譯進度：** {progress['completed_translations']}/{progress['total_chapters']} ({progress['completed_translations']/max(progress['total_chapters'], 1)*100:.1f}%)

## 章節詳情

| 章節 | 標題 | 原文 | 翻譯 | 字數 |
|------|------|------|------|------|
"""
        
        for chapter_key, chapter_info in sorted(progress["chapters"].items()):
            source_status = "✅" if chapter_info["source_exists"] else "❌"
            trans_status = "✅" if chapter_info["translation_exists"] else "⏳"
            
            report += f"| {chapter_key} | {chapter_info['title']} | {source_status} | {trans_status} | {chapter_info['word_count']} |\n"
            
        report += f"""
## 下一步計劃

"""
        
        # 找出還沒翻譯的章節
        untranslated = [ch for ch in progress["chapters"].values() 
                       if ch["source_exists"] and not ch["translation_exists"]]
        
        if untranslated:
            report += "### 待翻譯章節\n\n"
            for chapter in sorted(untranslated, key=lambda x: x["title"]):
                report += f"- {chapter['title']} ({chapter['word_count']} 字)\n"
        else:
            report += "🎉 所有章節翻譯已完成！\n"
            
        return report
        
    def create_translation_template(self, chapter_key):
        """為指定章節建立翻譯模板"""
        progress = self.scan_chapters()
        
        if chapter_key not in progress["chapters"]:
            print(f"❌ 找不到章節: {chapter_key}")
            return False
            
        chapter_info = progress["chapters"][chapter_key]
        
        if chapter_info["translation_exists"]:
            print(f"⚠️  翻譯已存在: {chapter_info['translation_file']}")
            return False
            
        # 讀取原文
        source_file = self.project_root / chapter_info["source_file"]
        with open(source_file, 'r', encoding='utf-8') as f:
            source_content = f.read()
            
        # 建立翻譯模板
        template = f"""# {chapter_info['title']}

## 原文

{source_content.replace('# ' + chapter_info['title'], '').strip()}

## 翻譯

[在此處添加現代中文翻譯]

## 註解

**重要詞彙：**
- 詞彙1：解釋
- 詞彙2：解釋

**文化背景：**
- 相關歷史文化說明

**翻譯要點：**
- 翻譯過程中的重要考量
"""
        
        # 儲存模板
        template_file = self.translation_dir / f"{chapter_key}.md"
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(template)
            
        print(f"✅ 已建立翻譯模板: {template_file}")
        return True

def main():
    """主函數"""
    manager = BaopuziManager()
    
    print("📊 抱朴子專案管理工具")
    print("=" * 40)
    
    # 生成進度報告
    report = manager.generate_progress_report()
    
    # 儲存報告
    report_file = Path("docs/抱朴子_進度報告.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
        
    print(f"✅ 進度報告已生成: {report_file}")
    print("\n" + "="*40)
    print(report)

if __name__ == "__main__":
    main()