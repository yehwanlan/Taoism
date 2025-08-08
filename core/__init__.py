#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道教經典翻譯系統 - 核心模組

提供翻譯、追蹤、監控等核心功能
"""

from .translator import TranslationEngine
from .tracker import ClassicTracker, get_tracker
from .file_monitor import FileMonitor, get_file_monitor

__version__ = "2.0.0"
__author__ = "道教經典翻譯專案"

__all__ = [
    "TranslationEngine",
    "ClassicTracker", 
    "get_tracker",
    "FileMonitor",
    "get_file_monitor"
]