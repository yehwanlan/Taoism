#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道教經典翻譯系統 - 共用命名與模板約定

原文/翻譯檔名與「尚未翻譯」的判斷原本分散在 translator、tracker、easy_cli 各寫一份，
規則不一致時會找不到檔案或誤判翻譯進度，因此集中在這裡。
"""

import re

# 新產生的翻譯模板一律使用這個佔位文字
TRANSLATION_PLACEHOLDER = "[此處應為現代中文翻譯]"

# 舊版工具曾使用過的佔位文字，判斷進度時仍需辨識
_PLACEHOLDERS = (
    TRANSLATION_PLACEHOLDER,
    "[此處填入現代中文翻譯]",
)

_UNSAFE_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*]')

# 書籍資料夾名稱結尾的書籍編號，例如 _DZ0336、_SBCK109、_PC2471
_BOOK_ID_SUFFIX = re.compile(r"_([A-Za-z]+\d+)$")

# 原文檔名，例如 03_开度品第一.txt
CHAPTER_FILE = re.compile(r"^(\d+)_(.+)\.txt$")


def split_book_folder(folder_name: str) -> tuple:
    """書籍資料夾名稱 → (書名, 書籍編號)，例如 `南华真经口义_DZ0735` → (`南华真经口义`, `DZ0735`)"""
    match = _BOOK_ID_SUFFIX.search(folder_name)
    if not match:
        return folder_name, folder_name
    return folder_name[:match.start()], match.group(1)


def sanitize_title(title: str) -> str:
    """把標題中不能用在檔名的字元換成底線"""
    return _UNSAFE_FILENAME_CHARS.sub('_', title)


def chapter_stem(number: int, title: str) -> str:
    """章節檔名（不含副檔名），例如 `03_开度品第一`"""
    return f"{number:02d}_{sanitize_title(title)}"


def is_untranslated(content: str) -> bool:
    """翻譯檔是否仍只有模板（尚未填入實際翻譯）"""
    return any(placeholder in content for placeholder in _PLACEHOLDERS)
