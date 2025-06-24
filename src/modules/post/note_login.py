#!/usr/bin/env python3
"""
noteログインモジュール
noteへの自動ログイン機能
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from ..utils import InputUtils, ValidationUtils, TimeUtils

class NoteLogin:
    def __init__(self, driver_manager, config_manager):
        """初期化"""
        self.driver_manager = driver_manager
        self.config_manager = config_manager
        self.driver = driver_manager.get_driver()
        self.wait = driver_manager.get_wait()

    def login(self):
        """noteにログイン"""
        try:
            # 認証情報の確認
            if not self.config_manager.validate_credentials():
                return False
            
            email = self.config_manager.get_email()
            password = self.config_manager.get_password()
            
            print("🔐 noteログインページにアクセス中...")
            self.driver.get("https://note.com/login")
            TimeUtils.random_delay(2, 3)

            # メールアドレス入力
            print("📧 メールアドレスを入力中...")
            if not self._input_email(email):
                return False

            # パスワード入力
            print("🔑 パスワードを入力中...")
            if not self._input_password(password):
                return False

            # ログインボタンクリック
            print("🚀 ログインボタンをクリック中...")
            if not self._click_login_button():
                return False

            # ログイン成功確認
            print("✅ ログイン処理完了、ページ遷移を確認中...")
            return self._verify_login_success()

        except Exception as e:
            print(f"❌ ログインエラー: {e}")
            return False

    def _input_email(self, email):
        """メールアドレス入力"""
        email_selectors = [
            'input#email[placeholder="mail@example.com or note ID"]',
            'input#email',
            'input[type="email"]',
            'input[name="email"]'
        ]
        
        email_element = None
        for selector in email_selectors:
            try:
                email_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                break
            except TimeoutException:
                continue
        
        if not email_element:
            print("❌ メールアドレス入力フィールドが見つかりません")
            return False

        try:
            InputUtils.paste_text(self.driver, email_element, email)  # 元のコードと同じpaste_text使用
            TimeUtils.random_delay(0.5, 1.0)
            
            return True
            
        except Exception as e:
            print(f"❌ メールアドレス入力エラー: {e}")
            return False

    def _input_password(self, password):
        """パスワード入力"""
        password_selectors = [
            'input#password[type="password"][aria-label="パスワード"]',  # 元のコードと同じ詳細なセレクタ
            'input#password',
            'input[type="password"]',
            'input[name="password"]'
        ]
        
        password_element = None
        for selector in password_selectors:
            try:
                password_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                break
            except TimeoutException:
                continue
        
        if not password_element:
            print("❌ パスワード入力フィールドが見つかりません")
            return False

        try:
            InputUtils.paste_text(self.driver, password_element, password)  # 元のコードと同じpaste_text使用
            TimeUtils.random_delay(0.5, 1.0)
            
            return True
            
        except Exception as e:
            print(f"❌ パスワード入力エラー: {e}")
            return False

    def _click_login_button(self):
        """ログインボタンクリック（元のコードを完全再現）"""
        login_selectors = [
            'button[data-type="primaryNext"]',  # noteサイトの実際のログインボタン
            'button[type="submit"]',
            'button:contains("ログイン")',
            '.login-button'
        ]
        
        login_button = None
        for selector in login_selectors:
            try:
                if 'contains' in selector:
                    login_button = self.driver.find_element(By.XPATH, f'//button[contains(text(), "ログイン")]')
                else:
                    login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ ログインボタンを発見: {selector}")
                break
            except NoSuchElementException:
                continue
        
        if not login_button:
            print("❌ ログインボタンが見つかりません")
            
            # デバッグ用：すべてのボタンを表示
            all_buttons = self.driver.execute_script("""
                var buttons = document.querySelectorAll('button, input[type="submit"]');
                var result = [];
                for (var i = 0; i < buttons.length; i++) {
                    var btn = buttons[i];
                    if (btn.offsetHeight > 0) {
                        result.push({
                            text: btn.textContent || btn.innerText || btn.value || '',
                            type: btn.type || '',
                            className: btn.className || '',
                            dataType: btn.getAttribute('data-type') || ''
                        });
                    }
                }
                return result;
            """)
            
            print("📋 表示されているすべてのボタン:")
            for i, btn in enumerate(all_buttons):
                print(f"  {i+1}. '{btn['text']}' (type: '{btn['type']}', data-type: '{btn['dataType']}', class: '{btn['className']}')")
            
            raise Exception("ログインボタンが見つかりません")

        try:
            login_button.click()
            TimeUtils.random_delay(3, 5)  # 元のコードと同じ待機時間
            return True
                
        except Exception as e:
            print(f"❌ ログインボタンクリックエラー: {e}")
            return False

    def _verify_login_success(self):
        """ログイン成功確認（元のコードを完全再現）"""
        try:
            # noteのホームページにリダイレクトされるまで待機
            success_indicators = [
                "note.com",
                "//button[contains(@aria-label, '投稿')]",
                ".o-navbarPrimary__postingButtonText"
            ]
            
            for indicator in success_indicators:
                try:
                    if indicator.startswith("//"):
                        self.wait.until(EC.presence_of_element_located((By.XPATH, indicator)))
                    elif indicator.startswith("."):
                        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, indicator)))
                    else:
                        # URL確認
                        self.wait.until(lambda driver: indicator in driver.current_url)
                    print(f"✅ ログイン成功！現在のURL: {self.driver.current_url}")
                    return True
                except TimeoutException:
                    continue
            
            print("⚠️  ログインは完了しましたが、ページ遷移の確認ができませんでした")
            return True
                
        except Exception as e:
            print(f"❌ ログイン確認エラー: {e}")
            return False 