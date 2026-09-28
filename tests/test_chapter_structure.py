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
PARENT_TEXT = "總序正文，道生一，一生二，二生三，三生萬物，萬物負陰而抱陽，沖氣以為和。"
CHILD_TEXT = "開度品正文，天尊告曰，善惡之報如影隨形，修善者福至，為惡者禍來，不可不慎。"


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


def test_book_url_resolves_to_first_chapter(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    eng = TranslationEngine()
    base = "https://www.shidianguji.com"
    # 書籍首頁不含目錄，改用第一章
    assert eng._resolve_start_url(f"{base}/book/DZ1422") == f"{base}/book/DZ1422/chapter/DZ1422_1"
    # 已經是章節網址（含亂碼章節 ID）就維持原樣
    chapter_url = f"{base}/book/SBCK440/chapter/1j6lo3zzeqt6n_1?page_from=bookshelf"
    assert eng._resolve_start_url(chapter_url) == chapter_url


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


# ---- 只有標題的分組章節、單章經典、子章節順序 ----

def _item(chapter_id, title, level):
    return (f'<div class="semi-tree-option semi-tree-option-level-{level}">'
            f'<a href="/book/T03/chapter/{chapter_id}">{title}</a></div>')


def _page(catalog_items, body):
    catalog = f'<div class="reader-catalog-tree">{"".join(catalog_items)}</div>' if catalog_items else ""
    return (f'<html><body>{catalog}<main class="read-layout-main">'
            f'<article class="chapter-reader">{body}</article></main></body></html>')


def _engine_for_pages(tmp_path, monkeypatch, pages):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(translator_module.time, "sleep", lambda *_: None)

    def fake_get(url, timeout=None):
        if "/api/" not in url:
            for chapter_id, html in pages.items():
                if url.split("?")[0].endswith(f"/chapter/{chapter_id}"):
                    return FakeResponse(200, html)
        return FakeResponse(404)

    eng = TranslationEngine()
    monkeypatch.setattr(eng.session, "get", fake_get)
    monkeypatch.setattr(eng, "get_book_info", lambda url: {
        "id": "T03", "title": "文始經", "author": "佚名", "url": url,
    })
    return eng


def _saved(tmp_path):
    return sorted(p.name for p in (tmp_path / "docs/source_texts/文始經_T03/原文").glob("*.txt"))


def test_sub_chapters_follow_parent_and_title_only_volume_is_skipped(tmp_path, monkeypatch):
    # 書的目錄只列出分卷；分卷頁的目錄才展開底下的篇（章節 ID 為亂碼，與網站相同）
    book_catalog = [_item("volaaaaaaaa1", "文始經上卷", 1), _item("noteaaaaaaa1", "校勘記", 1)]
    volume_catalog = [_item("volaaaaaaaa1", "文始經上卷", 1),
                      _item("pianaaaaaaa1", "一宇篇", 2), _item("pianaaaaaaa2", "二柱篇", 2),
                      _item("noteaaaaaaa1", "校勘記", 1)]
    pages = {
        "volaaaaaaaa1": _page(volume_catalog, "<h2>文始經上卷</h2><h3>一宇篇</h3><p>一宇篇正文，非有道不可言，不可言即道，非有道不可思，不可思即道。</p>"),
        "pianaaaaaaa1": _page(volume_catalog, "<h3>一宇篇</h3><p>一宇篇正文，非有道不可言，不可言即道，非有道不可思，不可思即道。</p>"),
        "pianaaaaaaa2": _page(volume_catalog, "<h3>二柱篇</h3><p>二柱篇正文，若碗若盂若瓶若壺若甕，皆能建天地，兆於一氣。</p>"),
        "noteaaaaaaa1": _page(book_catalog, "<h2>校勘記</h2><p>校勘記正文，據明正統道藏本校訂，並參照四部叢刊本與諸家舊注。</p>"),
    }
    eng = _engine_for_pages(tmp_path, monkeypatch, pages)
    assert eng.translate_book("https://example.invalid/book/T03/chapter/volaaaaaaaa1") is True

    # 上卷只有標題不另存；篇緊接在上卷之後、校勘記之前
    assert _saved(tmp_path) == ["02_一宇篇.txt", "03_二柱篇.txt", "04_校勘記.txt"]


def test_single_chapter_book_without_catalog(tmp_path, monkeypatch):
    pages = {"onlyaaaaaaa1": _page([], "<h2>清靜經注</h2><p>老君曰：大道無形，生育天地；大道無情，運行日月；大道無名，長養萬物。</p>")}
    eng = _engine_for_pages(tmp_path, monkeypatch, pages)
    assert eng.translate_book("https://example.invalid/book/T03/chapter/onlyaaaaaaa1") is True
    assert _saved(tmp_path) == ["01_清靜經注.txt"]


def test_volume_with_only_author_is_skipped_and_inline_section_is_retitled(tmp_path, monkeypatch):
    # 仿南華真經口義：卷之二只有卷名與撰者；卷之三的內容其實是「内篇齐物论下」（篇名以段落出現）
    catalog = [_item("juanaaaaaa02", "南华真经口义卷之二", 1), _item("pianaaaaaa21", "内篇齐物论上", 2),
               _item("juanaaaaaa03", "南华真经口义卷之三", 1)]
    qiwu = "齐物论下正文，大知闲闲，小知间间，大言炎炎，小言詹詹，其寐也魂交，其觉也形开。"
    pages = {
        "juanaaaaaa02": _page(catalog, "<h2>南华真经口义卷之二</h2><p>鬳斋林希逸</p><h3>内篇齐物论上</h3>"),
        "pianaaaaaa21": _page(catalog, "<h3>内篇齐物论上</h3><p>齐物论上正文，南郭子綦隐机而坐，仰天而嘘，荅焉似丧其耦。</p>"),
        "juanaaaaaa03": _page(catalog, f"<h2>南华真经口义卷之三</h2><p>鬳斋林希逸</p><p>内篇齐物论下</p><p>{qiwu}</p>"),
    }
    eng = _engine_for_pages(tmp_path, monkeypatch, pages)
    assert eng.translate_book("https://example.invalid/book/T03/chapter/juanaaaaaa02") is True
    assert _saved(tmp_path) == ["02_内篇齐物论上.txt", "03_内篇齐物论下.txt"]
    assert qiwu in (tmp_path / "docs/source_texts/文始經_T03/原文/03_内篇齐物论下.txt").read_text(encoding="utf-8")
