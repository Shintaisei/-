#!/usr/bin/env python3
"""
WebDriver管理モジュール
Chrome WebDriverの設定と管理
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

class DriverManager:
    def __init__(self, config_manager):
        """初期化"""
        self.config_manager = config_manager
        self.driver = None
        self.wait = None

    def setup_driver(self):
        """Chrome WebDriverを設定"""
        options = Options()
        
        # 設定から値を取得（フォールバック付き）
        chrome_opts = self.config_manager.get_chrome_options()
        user_agent = chrome_opts.get('user_agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        window_size = chrome_opts.get('window_size', '1920,1080')
        
        # 基本設定
        options.add_argument(f"--user-agent={user_agent}")
        options.add_argument(f"--window-size={window_size}")
        
        # 検出回避設定
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        
        # その他の設定
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-features=VizDisplayCompositor")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 15)
            
            # WebDriverプロパティを隠蔽
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ Chrome WebDriverが正常に起動しました")
            return True
            
        except Exception as e:
            print(f"❌ WebDriverの起動に失敗しました: {e}")
            return False

    def get_driver(self):
        """WebDriverインスタンスを取得"""
        return self.driver

    def get_wait(self):
        """WebDriverWaitインスタンスを取得"""
        return self.wait

    def quit_driver(self):
        """WebDriverを終了"""
        if self.driver:
            try:
                self.driver.quit()
                print("🔄 ブラウザを終了しています...")
            except Exception as e:
                print(f"⚠️ ブラウザ終了時にエラー: {e}")
            finally:
                self.driver = None
                self.wait = None 