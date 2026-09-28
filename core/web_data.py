#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道教經典翻譯系統 - 網站書單產生器

掃描 docs/source_texts/<書>/原文/ 與 docs/translations/<書>/，產生網站讀取的
docs/data/books.json。書單原本手寫在 docs/js/script.js，檔名一不一致（例如「滅/灭」）
網站就 404，新爬的書也要記得手動加，因此改為由實際檔案產生。

用法：python tools/build_web_data.py（爬完新書時 translate_book 也會自動執行）
"""

import json
import re
from pathlib import Path
from typing import Dict, List

from .conventions import is_untranslated

DOCS_DIR = Path("docs")

_CHAPTER_FILE = re.compile(r"^(\d+)_(.+)\.txt$")
# 資料夾名稱結尾的書籍編號，例如 _DZ0336、_SBCK109、_PC2471
_BOOK_ID_SUFFIX = re.compile(r"_([A-Za-z]+\d+)$")


def _book_sort_key(folder_name: str):
    match = _BOOK_ID_SUFFIX.search(folder_name)
    book_id = match.group(1) if match else folder_name
    prefix, number = re.match(r"([A-Za-z]*)(\d*)", book_id).groups()
    return (prefix, int(number) if number else 0, folder_name)


def _book_title(folder_name: str) -> str:
    return _BOOK_ID_SUFFIX.sub("", folder_name)


def _chapters(book_dir: Path, translation_dir: Path) -> List[Dict]:
    chapters = []
    for source_file in (book_dir / "原文").glob("*.txt"):
        match = _CHAPTER_FILE.match(source_file.name)
        if not match:
            continue
        number, title = match.groups()
        translation_file = translation_dir / f"{number}_{title}.md"
        translated = (translation_file.exists()
                      and not is_untranslated(translation_file.read_text(encoding="utf-8")))
        chapters.append({"number": number, "title": title, "translated": translated})
    return sorted(chapters, key=lambda c: int(c["number"]))


def build_web_data(docs_dir: Path = DOCS_DIR) -> Dict:
    """掃描原文與翻譯資料夾，回傳網站書單資料"""
    books = []
    source_root = docs_dir / "source_texts"
    for book_dir in sorted(source_root.iterdir(), key=lambda d: _book_sort_key(d.name)):
        if not (book_dir / "原文").is_dir():
            continue
        chapters = _chapters(book_dir, docs_dir / "translations" / book_dir.name)
        if chapters:
            books.append({"id": book_dir.name, "title": _book_title(book_dir.name), "chapters": chapters})

    all_chapters = [c for book in books for c in book["chapters"]]
    return {
        "stats": {
            "books": len(books),
            "chapters": len(all_chapters),
            "translated": sum(c["translated"] for c in all_chapters),
        },
        "books": books,
    }


def write_web_data(docs_dir: Path = DOCS_DIR) -> Dict:
    """產生並寫入 docs/data/books.json，回傳統計"""
    data = build_web_data(docs_dir)
    output = docs_dir / "data" / "books.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data["stats"]
