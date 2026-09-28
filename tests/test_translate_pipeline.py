#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻譯流程回歸測試（不連網，用假的網站回應）

涵蓋過去被 try/except 吞掉而沒人發現的問題：
- tracker / file_monitor 沒有真正 import safe_print，導致每一章都「爬取失敗」
- 中間有章節失敗時，追蹤系統記錄的章節與實際檔案對不上
- 兩種模板佔位文字導致翻譯進度誤判
"""

import json

import pytest

from core import translator as translator_module
from core.conventions import TRANSLATION_PLACEHOLDER, chapter_stem, is_untranslated
from core.translator import TranslationEngine


class FakeResponse:
    def __init__(self, status_code, data=None):
        self.status_code = status_code
        self._data = data
        self.text = ""

    def json(self):
        if self._data is None:
            raise json.JSONDecodeError("no json", "", 0)
        return self._data


# 章節內容的第一行是品名，translator 會用它取代目錄上的標題來命名檔案
FAKE_CHAPTERS = {
    "TEST01_1": "开度品第一\n\n" + "道言善哉善哉，汝等諦聽。" * 5,
    "TEST01_3": "善对品第二\n\n" + "天尊告曰，善惡之報如影隨形。" * 5,
}


def fake_get(url, timeout=None):
    for chapter_id, content in FAKE_CHAPTERS.items():
        if url.endswith(f"/chapter/{chapter_id}"):
            return FakeResponse(200, {"content": content})
    return FakeResponse(404)


@pytest.fixture
def engine(tmp_path, monkeypatch):
    # translator / tracker / file_monitor 目前都以工作目錄為基準寫檔
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(translator_module.time, "sleep", lambda *_: None)

    eng = TranslationEngine()
    monkeypatch.setattr(eng.session, "get", fake_get)
    monkeypatch.setattr(eng, "get_book_info", lambda url: {
        "id": "TEST01", "title": "測試經", "author": "佚名", "url": url,
    })
    # 第 2 章在網站上不存在（404），模擬中間有章節失敗
    monkeypatch.setattr(eng, "get_chapter_list", lambda url: [
        {"number": n, "title": f"卷{n}", "chapter_id": f"TEST01_{n}", "level": 2,
         "url": f"https://example.invalid/book/TEST01/chapter/TEST01_{n}"}
        for n in (1, 2, 3)
    ])
    return eng


def test_translate_book_saves_and_tracks_successful_chapters(engine, tmp_path):
    assert engine.translate_book("https://example.invalid/book/TEST01") is True

    source_dir = tmp_path / "docs/source_texts/測試經_TEST01/原文"
    translation_dir = tmp_path / "docs/translations/測試經_TEST01"
    assert sorted(p.name for p in source_dir.glob("*.txt")) == [
        "01_开度品第一.txt", "03_善对品第二.txt"]
    assert sorted(p.name for p in translation_dir.glob("*.md")) == [
        "01_开度品第一.md", "03_善对品第二.md"]

    # 追蹤系統記錄的章節必須是實際成功的第 1、3 章，而且找得到檔案（字數 > 0）
    classics = json.loads((tmp_path / "data/tracking/classics.json").read_text(encoding="utf-8"))
    chapters = classics["classics"]["TEST01"]["chapters"]
    assert [(c["number"], c["title"]) for c in chapters] == [(1, "开度品第一"), (3, "善对品第二")]
    assert all(c["char_count"] > 0 for c in chapters)

    # 檔案操作有被記錄（過去在這一步 NameError）
    log = json.loads((tmp_path / "data/logs/file_operations.json").read_text(encoding="utf-8"))
    assert log["metadata"]["total_operations"] >= 4


def test_new_templates_count_as_untranslated(engine, tmp_path):
    engine.translate_book("https://example.invalid/book/TEST01")
    engine.tracker.check_translation_progress()

    status = engine.tracker.get_classic_by_id("TEST01")["translation_status"]
    assert status["completed_chapters"] == 0
    assert status["total_chapters"] == 2


def test_recrawl_keeps_existing_translation(engine, tmp_path):
    translation = tmp_path / "docs/translations/測試經_TEST01/01_开度品第一.md"
    translation.parent.mkdir(parents=True)
    translation.write_text("# 开度品第一\n\n## 翻譯\n\n天尊說：善哉。\n", encoding="utf-8")

    engine.translate_book("https://example.invalid/book/TEST01")

    assert "天尊說：善哉。" in translation.read_text(encoding="utf-8")
    # 沒有翻譯的章節照常產生模板
    other = tmp_path / "docs/translations/測試經_TEST01/03_善对品第二.md"
    assert is_untranslated(other.read_text(encoding="utf-8"))


def test_placeholder_detection_covers_legacy_templates():
    assert is_untranslated(f"## 翻譯\n\n{TRANSLATION_PLACEHOLDER}\n")
    assert is_untranslated("## 翻譯\n\n[此處填入現代中文翻譯]\n")
    assert not is_untranslated("## 翻譯\n\n天尊說：善哉。\n")


def test_chapter_stem_sanitizes_unsafe_characters():
    assert chapter_stem(3, "卷上/卷下?") == "03_卷上_卷下_"
