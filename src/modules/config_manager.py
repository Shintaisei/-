#!/usr/bin/env python3
"""
設定管理モジュール
note自動投稿システムの設定ファイル管理
"""

import json
import os

class ConfigManager:
    def __init__(self, config_file="note_login_config.json"):
        """初期化"""
        self.config_file = config_file
        self.config = {}
        self.load_config()

    def load_config(self):
        """設定ファイルを読み込み"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"設定ファイル {self.config_file} が見つかりません。デフォルト設定を作成します。")
            self.create_default_config()

    def create_default_config(self):
        """デフォルト設定を作成"""
        self.config = {
            "email": "",
            "password": "",
            "chrome_options": {
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "window_size": "1920,1080",
                "disable_blink_features": ["AutomationControlled"],
                "exclude_switches": ["enable-automation"],
                "use_automation_extension": False,
                "disable_dev_shm_usage": True,
                "no_sandbox": True
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        
        print(f"デフォルト設定ファイル {self.config_file} を作成しました。")
        print("メールアドレスとパスワードを設定してください。")

    def get_email(self):
        """メールアドレスを取得"""
        return self.config.get('email', '')

    def get_password(self):
        """パスワードを取得"""
        return self.config.get('password', '')

    def get_chrome_options(self):
        """Chrome設定を取得"""
        return self.config.get('chrome_options', {})

    def get_config(self):
        """設定全体を取得"""
        return self.config

    def validate_credentials(self):
        """認証情報の検証"""
        email = self.get_email()
        password = self.get_password()
        
        if not email or not password:
            print("❌ メールアドレスまたはパスワードが設定されていません")
            print("note_login_config.json ファイルを確認してください")
            return False
        
        return True 