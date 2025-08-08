#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI翻譯品質評估工具

用於評估AI翻譯的品質和規範符合度
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class TranslationEvaluator:
    """翻譯品質評估器"""
    
    def __init__(self):
        """初始化評估器"""
        self.load_terminology()
        self.load_evaluation_rules()
        
    def load_terminology(self):
        """載入術語對照表"""
        self.terminology = {
            # 道教三清
            "元始天尊": {"category": "三清", "keep_original": True},
            "靈寶天尊": {"category": "三清", "keep_original": True},
            "道德天尊": {"category": "三清", "keep_original": True},
            "太上老君": {"category": "三清", "keep_original": True},
            
            # 重要概念
            "太上": {"category": "尊稱", "keep_original": True},
            "無為": {"category": "哲學", "keep_original": True},
            "自然": {"category": "哲學", "keep_original": True},
            "道": {"category": "核心概念", "keep_original": True},
            "德": {"category": "核心概念", "keep_original": True},
            
            # 修煉術語
            "修真": {"category": "修煉", "alternatives": ["修道", "修煉"]},
            "煉丹": {"category": "修煉", "keep_original": True},
            "服氣": {"category": "修煉", "alternatives": ["服氣", "氣功修煉"]},
            "導引": {"category": "修煉", "alternatives": ["導引", "養生功法"]},
            
            # 宗教術語
            "符籙": {"category": "宗教", "alternatives": ["符籙", "道符"]},
            "齋醮": {"category": "宗教", "alternatives": ["齋醮", "道教儀式"]},
            "洞天福地": {"category": "宗教", "keep_original": True},
            
            # 避免使用的詞彙
            "迷信": {"category": "禁用", "reason": "帶有貶義色彩"},
            "封建": {"category": "禁用", "reason": "政治色彩詞彙"},
            "老子說": {"category": "禁用", "correct": "太上老君說"}
        }
        
    def load_evaluation_rules(self):
        """載入評估規則"""
        self.rules = {
            "format_check": {
                "required_sections": ["原文", "翻譯", "註解"],
                "annotation_subsections": ["重要詞彙", "文化背景", "翻譯要點"]
            },
            "content_check": {
                "min_translation_length": 10,
                "max_length_ratio": 3.0,  # 翻譯長度不應超過原文3倍
                "min_length_ratio": 0.3   # 翻譯長度不應少於原文30%
            },
            "terminology_check": {
                "check_consistency": True,
                "check_forbidden_terms": True,
                "check_preferred_terms": True
            }
        }
        
    def evaluate_translation(self, translation_text: str) -> Dict:
        """評估翻譯品質"""
        results = {
            "overall_score": 0,
            "format_score": 0,
            "content_score": 0,
            "terminology_score": 0,
            "issues": [],
            "suggestions": []
        }
        
        # 解析翻譯文本
        parsed = self.parse_translation(translation_text)
        
        # 格式檢查
        format_result = self.check_format(parsed)
        results["format_score"] = format_result["score"]
        results["issues"].extend(format_result["issues"])
        
        # 內容檢查
        if parsed["original"] and parsed["translation"]:
            content_result = self.check_content(parsed["original"], parsed["translation"])
            results["content_score"] = content_result["score"]
            results["issues"].extend(content_result["issues"])
            
            # 術語檢查
            terminology_result = self.check_terminology(parsed["translation"])
            results["terminology_score"] = terminology_result["score"]
            results["issues"].extend(terminology_result["issues"])
            results["suggestions"].extend(terminology_result["suggestions"])
        
        # 計算總分
        results["overall_score"] = (
            results["format_score"] * 0.3 +
            results["content_score"] * 0.4 +
            results["terminology_score"] * 0.3
        )
        
        return results
        
    def parse_translation(self, text: str) -> Dict:
        """解析翻譯文本結構"""
        sections = {
            "title": "",
            "original": "",
            "translation": "",
            "annotations": ""
        }
        
        # 提取標題
        title_match = re.search(r'^#\s*(.+)', text, re.MULTILINE)
        if title_match:
            sections["title"] = title_match.group(1).strip()
            
        # 提取各個部分
        original_match = re.search(r'##\s*原文\s*\n(.*?)(?=##|$)', text, re.DOTALL)
        if original_match:
            sections["original"] = original_match.group(1).strip()
            
        translation_match = re.search(r'##\s*翻譯\s*\n(.*?)(?=##|$)', text, re.DOTALL)
        if translation_match:
            sections["translation"] = translation_match.group(1).strip()
            
        annotation_match = re.search(r'##\s*註解\s*\n(.*?)(?=##|$)', text, re.DOTALL)
        if annotation_match:
            sections["annotations"] = annotation_match.group(1).strip()
            
        return sections
        
    def check_format(self, parsed: Dict) -> Dict:
        """檢查格式規範"""
        issues = []
        score = 100
        
        # 檢查必要部分
        required_sections = self.rules["format_check"]["required_sections"]
        for section in required_sections:
            section_key = section.lower().replace("註解", "annotations").replace("翻譯", "translation").replace("原文", "original")
            if not parsed.get(section_key):
                issues.append(f"❌ 缺少「{section}」部分")
                score -= 30
                
        # 檢查註解子部分
        if parsed["annotations"]:
            annotation_subsections = self.rules["format_check"]["annotation_subsections"]
            for subsection in annotation_subsections:
                if subsection not in parsed["annotations"]:
                    issues.append(f"⚠️  註解中缺少「{subsection}」子部分")
                    score -= 10
                    
        return {"score": max(0, score), "issues": issues}
        
    def check_content(self, original: str, translation: str) -> Dict:
        """檢查內容品質"""
        issues = []
        score = 100
        
        # 長度檢查
        orig_len = len(original)
        trans_len = len(translation)
        
        if trans_len < self.rules["content_check"]["min_translation_length"]:
            issues.append("❌ 翻譯內容過短")
            score -= 40
            
        if orig_len > 0:
            length_ratio = trans_len / orig_len
            max_ratio = self.rules["content_check"]["max_length_ratio"]
            min_ratio = self.rules["content_check"]["min_length_ratio"]
            
            if length_ratio > max_ratio:
                issues.append(f"⚠️  翻譯過長（比例: {length_ratio:.1f}，建議: <{max_ratio}）")
                score -= 15
            elif length_ratio < min_ratio:
                issues.append(f"⚠️  翻譯過短（比例: {length_ratio:.1f}，建議: >{min_ratio}）")
                score -= 15
                
        # 檢查是否有明顯的翻譯模板痕跡
        template_indicators = ["[此處應為", "[待補充]", "請使用AI翻譯"]
        for indicator in template_indicators:
            if indicator in translation:
                issues.append(f"❌ 翻譯中包含模板標記: {indicator}")
                score -= 30
                
        return {"score": max(0, score), "issues": issues}
        
    def check_terminology(self, translation: str) -> Dict:
        """檢查術語使用"""
        issues = []
        suggestions = []
        score = 100
        
        # 檢查禁用詞彙
        for term, info in self.terminology.items():
            if info.get("category") == "禁用" and term in translation:
                issues.append(f"❌ 使用了不當詞彙: 「{term}」")
                if "correct" in info:
                    suggestions.append(f"💡 建議將「{term}」改為「{info['correct']}」")
                score -= 20
                
        # 檢查術語一致性
        used_terms = {}
        for term, info in self.terminology.items():
            if info.get("category") != "禁用" and term in translation:
                used_terms[term] = info
                
        # 檢查是否有更好的術語選擇
        for term, info in used_terms.items():
            if "alternatives" in info and len(info["alternatives"]) > 1:
                suggestions.append(f"💡 「{term}」可考慮使用: {', '.join(info['alternatives'])}")
                
        return {"score": max(0, score), "issues": issues, "suggestions": suggestions}
        
    def generate_evaluation_report(self, results: Dict) -> str:
        """生成評估報告"""
        score = results["overall_score"]
        
        # 評級
        if score >= 90:
            grade = "優秀 ⭐⭐⭐⭐⭐"
        elif score >= 80:
            grade = "良好 ⭐⭐⭐⭐"
        elif score >= 70:
            grade = "及格 ⭐⭐⭐"
        elif score >= 60:
            grade = "待改進 ⭐⭐"
        else:
            grade = "不及格 ⭐"
            
        report = f"""# 📊 AI翻譯品質評估報告

## 🎯 總體評估
- **總分**: {score:.1f}/100
- **評級**: {grade}

## 📋 詳細評分
- **格式規範**: {results['format_score']:.1f}/100
- **內容品質**: {results['content_score']:.1f}/100  
- **術語使用**: {results['terminology_score']:.1f}/100

"""
        
        # 問題列表
        if results["issues"]:
            report += "## ❌ 發現的問題\n\n"
            for issue in results["issues"]:
                report += f"- {issue}\n"
            report += "\n"
            
        # 建議列表
        if results["suggestions"]:
            report += "## 💡 改進建議\n\n"
            for suggestion in results["suggestions"]:
                report += f"- {suggestion}\n"
            report += "\n"
            
        # 評估標準
        report += """## 📏 評估標準

### 格式規範 (30%)
- 包含必要部分：原文、翻譯、註解
- 註解包含：重要詞彙、文化背景、翻譯要點
- 遵循標準Markdown格式

### 內容品質 (40%)
- 翻譯長度適中（原文30%-300%）
- 無模板標記殘留
- 內容完整準確

### 術語使用 (30%)
- 避免使用不當詞彙
- 道教術語使用正確
- 術語使用一致

---
*評估時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report


def evaluate_translation_file(file_path: str) -> None:
    """評估翻譯檔案"""
    evaluator = TranslationEvaluator()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        results = evaluator.evaluate_translation(content)
        report = evaluator.generate_evaluation_report(results)
        
        # 儲存評估報告
        report_path = Path(file_path).with_suffix('.evaluation.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
            
        print(f"✅ 評估完成: {file_path}")
        print(f"📊 總分: {results['overall_score']:.1f}/100")
        print(f"📋 報告: {report_path}")
        
    except Exception as e:
        print(f"❌ 評估失敗: {e}")


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI翻譯品質評估工具")
    parser.add_argument("file", help="要評估的翻譯檔案路徑")
    
    args = parser.parse_args()
    
    if not Path(args.file).exists():
        print(f"❌ 檔案不存在: {args.file}")
        return 1
        
    evaluate_translation_file(args.file)
    return 0


if __name__ == "__main__":
    exit(main())