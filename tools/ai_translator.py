#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成式AI經文翻譯工具

基於AI翻譯指導規範，使用生成式AI進行道教經文翻譯
支援進度追蹤和品質評估
"""

import re
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Generator
from datetime import datetime
import subprocess
import sys

# 設置標準輸出編碼為 UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)


class AITranslator:
    """生成式AI翻譯器"""
    
    def __init__(self):
        """初始化翻譯器"""
        self.load_translation_guidelines()
        self.load_terminology()
        self.progress_callback = None
        
    def load_translation_guidelines(self):
        """載入AI翻譯指導規範"""
        guidelines_path = Path("docs/system/AI翻譯指導規範.md")
        
        if guidelines_path.exists():
            with open(guidelines_path, 'r', encoding='utf-8') as f:
                self.guidelines = f.read()
        else:
            # 預設指導規範
            self.guidelines = """
# AI翻譯指導規範

## 翻譯原則
1. 忠實原文，準確傳達古文含義
2. 使用現代中文表達，保持典雅風格
3. 道教專業術語保持一致性
4. 尊重傳統文化，避免不當現代化詮釋

## 術語處理
- 保持道教核心概念的原始性
- 統一術語翻譯標準
- 避免使用帶有貶義的現代詞彙

## 格式要求
- 保持原文結構
- 適當添加標點符號
- 必要時提供註解說明
"""
            
    def load_terminology(self):
        """載入術語對照表"""
        self.terminology = {
            # 道教三清
            "元始天尊": "元始天尊",
            "靈寶天尊": "靈寶天尊", 
            "道德天尊": "道德天尊",
            "太上老君": "太上老君",
            
            # 核心概念
            "道": "道",
            "德": "德",
            "無為": "無為",
            "自然": "自然",
            "太上": "太上",
            
            # 修煉術語
            "修真": "修真",
            "煉丹": "煉丹",
            "服氣": "服氣",
            "導引": "導引",
            
            # 宗教術語
            "符籙": "符籙",
            "齋醮": "齋醮",
            "洞天福地": "洞天福地"
        }
        
    def create_translation_prompt(self, original_text: str, context: Dict = None) -> str:
        """創建翻譯提示詞"""
        context = context or {}
        
        prompt = f"""你是一位專業的道教經典翻譯專家。請根據以下指導規範翻譯古文：

{self.guidelines}

## 翻譯任務
請將以下道教經典原文翻譯成現代中文：

### 原文
```
{original_text.strip()}
```

### 上下文資訊
- 經典名稱：{context.get('book_title', '未知')}
- 章節：{context.get('chapter_title', '未知')}
- 作者：{context.get('author', '未知')}

## 翻譯要求
1. 提供準確、流暢的現代中文翻譯
2. 保持道教術語的專業性和一致性
3. 必要時提供重要詞彙的註解
4. 說明翻譯過程中的重點和難點

## 輸出格式
請按以下格式輸出：

### 現代中文翻譯
[翻譯內容]

### 重要詞彙註解
- **[術語1]**: [解釋]
- **[術語2]**: [解釋]

### 翻譯要點
- [翻譯要點1]
- [翻譯要點2]

請開始翻譯："""
        
        return prompt
        
    def translate_with_gemini(self, prompt: str) -> Optional[str]:
        """使用Gemini CLI進行翻譯"""
        try:
            # 使用gemini命令行工具
            cmd = ['gemini', 'chat']
            
            result = subprocess.run(
                cmd,
                input=prompt, # 將 prompt 通過標準輸入傳遞
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=120  # 2分鐘超時
            )
            
            if result.returncode == 0:
                print(f"DEBUG: Gemini CLI Stdout: {result.stdout.strip()}")
                return result.stdout.strip()
            else:
                print(f"DEBUG: Gemini CLI Stderr: {result.stderr.strip()}")
                print(f"❌ Gemini CLI錯誤: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("❌ 翻譯超時")
            return None
        except FileNotFoundError:
            print("❌ 未找到gemini命令，請確認已安裝Gemini CLI")
            return None
        except Exception as e:
            print(f"❌ 翻譯失敗: {e}")
            return None
            
    def translate_with_openai(self, prompt: str) -> Optional[str]:
        """使用OpenAI API進行翻譯（備用方案）"""
        try:
            # 這裡可以添加OpenAI API調用
            # 需要安裝openai庫並設置API密鑰
            print("💡 OpenAI翻譯功能需要額外配置")
            return None
        except Exception as e:
            print(f"❌ OpenAI翻譯失敗: {e}")
            return None
            
    def translate_text(self, original_text: str, context: Dict = None) -> Optional[str]:
        """翻譯文本"""
        prompt = self.create_translation_prompt(original_text, context)
        
        # 首先嘗試Gemini CLI
        result = self.translate_with_gemini(prompt)
        
        # 如果失敗，可以嘗試其他AI服務
        if not result:
            result = self.translate_with_openai(prompt)
            
        return result
        
    def translate_file(self, file_path: str, output_path: str = None) -> bool:
        """翻譯單個檔案"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"❌ 檔案不存在: {file_path}")
            return False
            
        try:
            # 讀取原文
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 解析檔案資訊
            context = self.extract_file_context(file_path, content)
            
            # 提取原文內容
            original_text = self.extract_original_text(content)
            
            if not original_text:
                print(f"❌ 無法提取原文內容: {file_path}")
                return False
                
            print(f"📝 開始翻譯: {file_path.name}")
            print(f"📊 原文字數: {len(original_text)} 字")
            
            # 進行翻譯
            translation_result = self.translate_text(original_text, context)
            
            if not translation_result:
                print(f"❌ 翻譯失敗: {file_path}")
                return False
                
            # 更新翻譯模板
            updated_content = self.update_translation_template(content, translation_result)
            
            # 儲存結果
            if not output_path:
                output_path = file_path
                
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
                
            print(f"✅ 翻譯完成: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ 翻譯檔案失敗: {e}")
            return False
            
    def extract_file_context(self, file_path: Path, content: str) -> Dict:
        """從檔案路徑和內容提取上下文資訊"""
        context = {}
        
        # 從檔案路徑提取資訊
        parts = file_path.stem.split('_')
        if len(parts) >= 2:
            context['chapter_number'] = parts[0]
            context['chapter_title'] = '_'.join(parts[1:])
            
        # 從父目錄提取書籍資訊
        parent_dir = file_path.parent.name
        if '_' in parent_dir:
            book_parts = parent_dir.rsplit('_', 1)
            context['book_title'] = book_parts[0]
            context['book_id'] = book_parts[1] if len(book_parts) > 1 else ''
            
        # 從內容提取資訊
        title_match = re.search(r'^#\s*(.+)', content, re.MULTILINE)
        if title_match:
            context['full_title'] = title_match.group(1).strip()
            
        author_match = re.search(r'\*\*作者\*\*[：:]\s*(.+)', content)
        if author_match:
            context['author'] = author_match.group(1).strip()
            
        return context
        
    def extract_original_text(self, content: str) -> str:
        """從翻譯模板中提取原文"""
        # 尋找原文部分
        original_match = re.search(r'##\s*📜\s*原文\s*\n\s*```\s*\n(.*?)\n\s*```', content, re.DOTALL)
        
        if original_match:
            return original_match.group(1).strip()
            
        # 備用方案：尋找其他格式的原文
        original_match = re.search(r'##\s*原文\s*\n(.*?)(?=##|$)', content, re.DOTALL)
        if original_match:
            text = original_match.group(1).strip()
            # 移除可能的代碼塊標記
            text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
            return text.strip()
            
        return ""
        
    def update_translation_template(self, original_content: str, translation_result: str) -> str:
        """更新翻譯模板"""
        # 解析翻譯結果
        translation_parts = self.parse_translation_result(translation_result)
        
        # 更新翻譯部分
        if translation_parts.get('translation'):
            pattern = r'(##\s*📝\s*現代中文翻譯.*?\n)(.*?)(?=##|\Z)'
            replacement = f"\\1\n{translation_parts['translation']}\n"
            original_content = re.sub(pattern, replacement, original_content, flags=re.DOTALL)
            
        # 更新詞彙註解
        if translation_parts.get('annotations'):
            pattern = r'(##\s*📚\s*重要詞彙註解.*?\n)(.*?)(?=##|\Z)'
            replacement = f"\\1\n{translation_parts['annotations']}\n"
            original_content = re.sub(pattern, replacement, original_content, flags=re.DOTALL)
            
        # 更新翻譯要點
        if translation_parts.get('points'):
            pattern = r'(##\s*💡\s*翻譯要點.*?\n)(.*?)(?=##|\Z)'
            replacement = f"\\1\n{translation_parts['points']}\n"
            original_content = re.sub(pattern, replacement, original_content, flags=re.DOTALL)
            
        # 更新翻譯狀態
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status_pattern = r'(\*\*翻譯狀態\*\*[：:]\s*)🔄 待翻譯'
        original_content = re.sub(status_pattern, f'\\1✅ 已完成 ({now})', original_content)
        
        return original_content
        
    def parse_translation_result(self, result: str) -> Dict:
        """解析翻譯結果"""
        parts = {}
        
        # 提取翻譯內容
        translation_match = re.search(r'###\s*現代中文翻譯\s*\n(.*?)(?=###|\Z)', result, re.DOTALL)
        if translation_match:
            parts['translation'] = translation_match.group(1).strip()
            
        # 提取詞彙註解
        annotations_match = re.search(r'###\s*重要詞彙註解\s*\n(.*?)(?=###|\Z)', result, re.DOTALL)
        if annotations_match:
            parts['annotations'] = annotations_match.group(1).strip()
            
        # 提取翻譯要點
        points_match = re.search(r'###\s*翻譯要點\s*\n(.*?)(?=###|\Z)', result, re.DOTALL)
        if points_match:
            parts['points'] = points_match.group(1).strip()
            
        return parts
        
    def batch_translate_directory(self, directory: str, pattern: str = "*.md") -> Dict:
        """批量翻譯目錄中的檔案"""
        directory = Path(directory)
        
        if not directory.exists():
            print(f"❌ 目錄不存在: {directory}")
            return {"success": 0, "failed": 0, "files": []}
            
        files = list(directory.glob(f"**/{pattern}"))
        
        if not files:
            print(f"❌ 未找到符合條件的檔案: {directory}/{pattern}")
            return {"success": 0, "failed": 0, "files": []}
            
        print(f"🚀 開始批量翻譯: {len(files)} 個檔案")
        
        results = {"success": 0, "failed": 0, "files": []}
        
        for i, file_path in enumerate(files, 1):
            print(f"\n📝 進度: {i}/{len(files)} - {file_path.name}")
            
            if self.progress_callback:
                self.progress_callback(i, len(files), file_path.name)
                
            success = self.translate_file(file_path)
            
            if success:
                results["success"] += 1
                results["files"].append({"file": str(file_path), "status": "success"})
            else:
                results["failed"] += 1
                results["files"].append({"file": str(file_path), "status": "failed"})
                
            # 避免API限制，添加延遲
            time.sleep(2)
            
        print(f"\n🎉 批量翻譯完成!")
        print(f"✅ 成功: {results['success']} 個")
        print(f"❌ 失敗: {results['failed']} 個")
        
        return results
        
    def set_progress_callback(self, callback):
        """設置進度回調函數"""
        self.progress_callback = callback


class TranslationProgressTracker:
    """翻譯進度追蹤器"""
    
    def __init__(self):
        self.start_time = None
        self.current_file = ""
        self.total_files = 0
        self.completed_files = 0
        
    def start_tracking(self, total_files: int):
        """開始追蹤"""
        self.start_time = time.time()
        self.total_files = total_files
        self.completed_files = 0
        
    def update_progress(self, completed: int, total: int, current_file: str):
        """更新進度"""
        self.completed_files = completed
        self.current_file = current_file
        
        if self.start_time:
            elapsed = time.time() - self.start_time
            if completed > 0:
                avg_time = elapsed / completed
                remaining = (total - completed) * avg_time
                eta = time.strftime('%H:%M:%S', time.gmtime(remaining))
            else:
                eta = "計算中..."
                
            progress_percent = (completed / total) * 100
            
            print(f"📊 進度: {completed}/{total} ({progress_percent:.1f}%)")
            print(f"⏱️  已用時間: {time.strftime('%H:%M:%S', time.gmtime(elapsed))}")
            print(f"🕐 預計剩餘: {eta}")
            print(f"📄 當前檔案: {current_file}")
            print("=" * 50)


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="生成式AI經文翻譯工具")
    parser.add_argument("--file", "-f", help="翻譯單個檔案")
    parser.add_argument("--directory", "-d", help="批量翻譯目錄")
    parser.add_argument("--pattern", "-p", default="*.md", help="檔案匹配模式")
    parser.add_argument("--output", "-o", help="輸出檔案路徑")
    
    args = parser.parse_args()
    
    translator = AITranslator()
    tracker = TranslationProgressTracker()
    
    # 設置進度回調
    translator.set_progress_callback(tracker.update_progress)
    
    if args.file:
        # 翻譯單個檔案
        success = translator.translate_file(args.file, args.output)
        return 0 if success else 1
        
    elif args.directory:
        # 批量翻譯
        results = translator.batch_translate_directory(args.directory, args.pattern)
        return 0 if results["failed"] == 0 else 1
        
    else:
        # 互動模式
        print("🤖 生成式AI經文翻譯工具")
        print("=" * 40)
        
        while True:
            print("\n請選擇操作：")
            print("1. 翻譯單個檔案")
            print("2. 批量翻譯目錄")
            print("3. 退出")
            
            choice = input("\n請輸入選項 (1-3): ").strip()
            
            if choice == "1":
                file_path = input("請輸入檔案路徑: ").strip()
                if file_path:
                    translator.translate_file(file_path)
                    
            elif choice == "2":
                directory = input("請輸入目錄路徑: ").strip()
                pattern = input("檔案模式 (預設: *.md): ").strip() or "*.md"
                if directory:
                    translator.batch_translate_directory(directory, pattern)
                    
            elif choice == "3":
                print("👋 再見！")
                break
                
            else:
                print("❌ 無效選項")
                
        return 0


if __name__ == "__main__":
    exit(main())