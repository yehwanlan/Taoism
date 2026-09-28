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


def sanitize_title(title: str) -> str:
    """把標題中不能用在檔名的字元換成底線"""
    return _UNSAFE_FILENAME_CHARS.sub('_', title)


def chapter_stem(number: int, title: str) -> str:
    """章節檔名（不含副檔名），例如 `03_开度品第一`"""
    return f"{number:02d}_{sanitize_title(title)}"


def is_untranslated(content: str) -> bool:
    """翻譯檔是否仍只有模板（尚未填入實際翻譯）"""
    return any(placeholder in content for placeholder in _PLACEHOLDERS)
