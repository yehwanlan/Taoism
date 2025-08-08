import os

# 定義檔案路徑
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_TEXTS_DIR = os.path.join(ROOT_DIR, 'docs', 'source_texts')
TRANSLATIONS_DIR = os.path.join(ROOT_DIR, 'docs', 'translations')

def check_progress():
    """檢查翻譯進度"""
    try:
        source_files = [f for f in os.listdir(SOURCE_TEXTS_DIR) if os.path.isfile(os.path.join(SOURCE_TEXTS_DIR, f))]
        translated_files_md = [f for f in os.listdir(TRANSLATIONS_DIR) if f.endswith('.md')]
    except FileNotFoundError as e:
        print(f"錯誤：找不到目錄 {e.filename}。請確保 source_texts 和 translations 目錄存在。")
        return

    translated_basenames = {os.path.splitext(f)[0] for f in translated_files_md}

    total_files = len(source_files)
    translated_count = 0
    untranslated_files = []

    for source_file in source_files:
        basename = os.path.splitext(source_file)[0]
        if basename in translated_basenames:
            translated_count += 1
        else:
            untranslated_files.append(source_file)

    if total_files == 0:
        progress_percentage = 0
    else:
        progress_percentage = (translated_count / total_files) * 100

    print("--- 翻譯進度報告 ---")
    print(f"總經文數: {total_files}")
    print(f"已翻譯:   {translated_count}")
    print(f"未翻譯:   {total_files - translated_count}")
    print(f"進度:     {progress_percentage:.2f}%")
    print("----------------------")

    if untranslated_files:
        print("\n尚未翻譯的經文列表:")
        for filename in untranslated_files:
            print(f"- {filename}")

if __name__ == '__main__':
    check_progress()
