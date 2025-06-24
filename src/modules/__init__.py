#!/usr/bin/env python3
"""
note自動投稿システム モジュールパッケージ（リファクタリング版）

構造:
- post/: 投稿機能（ログイン、WebDriver、投稿処理）
- contents/: コンテンツ生成機能（記事生成、データ管理、LLM）
- 共通: 設定管理、ユーティリティ
"""

# 投稿機能モジュール
from .post.driver_manager import DriverManager
from .post.note_login import NoteLogin
from .post.note_poster import NotePoster

# コンテンツ生成機能モジュール
from .contents.content_generator import ContentGenerator
from .contents.article_manager import ArticleManager
from .contents.data_manager import DataManager

# 共通モジュール
from .config_manager import ConfigManager
from .utils import InputUtils, ValidationUtils, TimeUtils

__all__ = [
    # 投稿機能
    'DriverManager',
    'NoteLogin',
    'NotePoster',
    
    # コンテンツ生成機能
    'ContentGenerator',
    'ArticleManager',
    'DataManager',
    
    # 共通機能
    'ConfigManager',
    'InputUtils',
    'ValidationUtils',
    'TimeUtils'
] 