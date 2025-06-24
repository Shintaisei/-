#!/usr/bin/env python3
"""
note自動投稿システム - srcパッケージ
リファクタリング版のメインパッケージ
"""

from .note_complete_auto import NoteCompleteAuto

__version__ = "2.0.0"
__author__ = "note自動投稿システム"
__description__ = "noteの自動ログインと記事投稿を行うシステム（リファクタリング版）"

__all__ = ['NoteCompleteAuto'] 