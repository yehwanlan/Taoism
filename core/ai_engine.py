import os
from pathlib import Path

class AIEngine:
    """AI 翻譯引擎，負責準備翻譯任務並生成指令給 Gemini CLI。"""

    def __init__(self, config=None):
        """初始化 AI 引擎"""
        self.config = config if config else {}
        self.root_dir = Path(__file__).parent.parent
        self.source_texts_dir = self.root_dir / 'docs' / 'source_texts'
        self.translations_dir = self.root_dir / 'docs' / 'translations'
        self.guidelines_path = self.root_dir / 'config' / 'ai_translation_guidelines.md'

    def prepare_translation_task(self, filename):
        """準備翻譯任務，並返回給 Gemini CLI 的指令。"""
        # filename is now a relative path like "Book_ID/原文/Chapter.txt"
        source_path = self.source_texts_dir / filename

        # Extract the book-specific directory from the filename
        # e.g., "Book_ID" from "Book_ID/原文/Chapter.txt"
        try:
            book_dir_name = Path(filename).parts[0]
        except IndexError:
            print(f"錯誤：無法從 '{filename}' 中提取書籍目錄。")
            return None

        # Construct the correct translation path
        translation_sub_dir = self.translations_dir / book_dir_name
        translation_sub_dir.mkdir(parents=True, exist_ok=True) # Ensure the directory exists
        
        translation_filename = source_path.stem + '.md'
        translation_path = translation_sub_dir / translation_filename

        if not source_path.exists():
            print(f"錯誤：找不到原始經文檔案 '{source_path}'")
            return None

        # We don't check for existence of translation_path anymore because
        # the tracker already determined it's untranslated.

        if not self.guidelines_path.exists():
            print(f"錯誤：找不到翻譯準則檔案 '{self.guidelines_path}'")
            return None

        print("\n" + "="*60)
        print("✅ 翻譯任務已準備就緒！")
        print("="*60)
        print("下一步，請複製並執行以下指令來開始翻譯：")
        print("\n" + "-"*60)
        # Use absolute paths in the final command for clarity
        gemini_command = f"翻譯檔案 '{source_path.resolve()}' 至 '{translation_path.resolve()}'，並使用準則 '{self.guidelines_path.resolve()}'"
        print(gemini_command)
        print("-"*60 + "\n")
        
        return gemini_command

