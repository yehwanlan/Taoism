#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
章節結構回歸測試（不連網，HTML 仿照識典古籍 2026 年的頁面結構）

識典古籍的目錄裡，上層章節會出現兩次（展開節點 + 自身連結），
上層章節的頁面也會連同子章節內容一起顯示。過去因此產生重複章節，
例如南華真經口義 01 = 02、文始真經 02 = 08。
"""

import pytest

from core import translator as translator_module
from core.translator import TranslationEngine

BOOK = "T02"
PARENT_TEXT = "總序正文，道生一，一生二，二生三，三生萬物。"
CHILD_TEXT = "開度品正文，天尊告曰，善惡之報如影隨形。"


class FakeResponse:
    def __init__(self, status_code, text=""):
        self.status_code = status_code
        self.text = text

    def json(self):
        raise ValueError("not json")

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def catalog_html(parent_twice: bool) -> str:
    parent = (f'<div class="semi-tree-option semi-tree-option-level-1">'
              f'<a href="/book/{BOOK}/chapter/{BOOK}_1">上卷總序</a></div>')
    child = (f'<div class="semi-tree-option semi-tree-option-level-2">'
             f'<a href="/book/{BOOK}/chapter/{BOOK}_2">開度品第一</a></div>')
    items = parent * (2 if parent_twice else 1) + child
    return f'<div class="reader-catalog-tree">{items}</div>'


def chapter_page(catalog: str, sections) -> str:
    body = "".join(f"<h2>{heading}</h2><p>{text}</p>" for heading, text in sections)
    return (f'<html><body>{catalog}<main class="read-layout-main">'
            f'<article class="chapter-reader">{body}</article></main></body></html>')


def make_engine(tmp_path, monkeypatch, parent_twice):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(translator_module.time, "sleep", lambda *_: None)
    catalog = catalog_html(parent_twice)
    pages = {
        # 上層章節頁面會把子章節一起顯示
        f"{BOOK}_1": chapter_page(catalog, [("上卷總序", PARENT_TEXT), ("開度品第一", CHILD_TEXT)]),
        f"{BOOK}_2": chapter_page(catalog, [("開度品第一", CHILD_TEXT)]),
    }

    def fake_get(url, timeout=None):
        if "/api/" in url:
            return FakeResponse(404)
        for chapter_id, html in pages.items():
            if url.split("?")[0].endswith(f"/chapter/{chapter_id}"):
                return FakeResponse(200, html)
        return FakeResponse(404)

    eng = TranslationEngine()
    monkeypatch.setattr(eng.session, "get", fake_get)
    monkeypatch.setattr(eng, "get_book_info", lambda url: {
        "id": BOOK, "title": "測試經", "author": "佚名", "url": url,
    })
    return eng


@pytest.mark.parametrize("parent_twice", [True, False], ids=["目錄重複上層章節", "目錄只列一次"])
def test_each_chapter_saved_once_without_child_content(tmp_path, monkeypatch, parent_twice):
    eng = make_engine(tmp_path, monkeypatch, parent_twice)
    assert eng.translate_book(f"https://example.invalid/book/{BOOK}/chapter/{BOOK}_1") is True

    source_dir = tmp_path / f"docs/source_texts/測試經_{BOOK}/原文"
    files = sorted(p.name for p in source_dir.glob("*.txt"))
    assert files == ["01_上卷總序.txt", "02_開度品第一.txt"]

    parent = (source_dir / "01_上卷總序.txt").read_text(encoding="utf-8")
    child = (source_dir / "02_開度品第一.txt").read_text(encoding="utf-8")
    assert PARENT_TEXT in parent
    assert CHILD_TEXT not in parent, "上層章節不應包含子章節內容"
    assert CHILD_TEXT in child
