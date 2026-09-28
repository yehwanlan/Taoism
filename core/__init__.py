#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道教經典翻譯系統 - 核心模組

提供翻譯、追蹤、監控等核心功能
"""

from .tracker import ClassicTracker, get_tracker
from .file_monitor import FileMonitor, get_file_monitor


def __getattr__(name):
    # 翻譯引擎延後載入：只用到 core.web_data 等模組時（例如部署時產生網站書單），
    # 不需要安裝爬蟲用的 requests、beautifulsoup4
    if name == "TranslationEngine":
        from .translator import TranslationEngine
        return TranslationEngine
    raise AttributeError(f"module 'core' has no attribute {name!r}")

__version__ = "2.0.0"
__author__ = "道教經典翻譯專案"

__all__ = [
    "TranslationEngine",
    "ClassicTracker", 
    "get_tracker",
    "FileMonitor",
    "get_file_monitor"
]