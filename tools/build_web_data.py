#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新產生網站書單 docs/data/books.json

手動新增、刪除或翻譯經文檔案後執行一次；GitHub Actions 部署前也會自動執行。
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from core.unicode_handler import safe_print  # noqa: E402
from core.web_data import write_web_data  # noqa: E402

if __name__ == "__main__":
    stats = write_web_data()
    safe_print(f"已產生 docs/data/books.json：{stats['books']} 部經典、"
               f"{stats['chapters']} 章，已翻譯 {stats['translated']} 章")
