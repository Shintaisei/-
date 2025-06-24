#!/usr/bin/env python3
"""
ユーティリティモジュール
共通機能とヘルパー関数
"""

import time
import random
from selenium.webdriver.common.keys import Keys

class InputUtils:
    @staticmethod
    def js_paste_text(driver, element, text):
        """JavaScript経由で超高速入力"""
        driver.execute_script("arguments[0].value = arguments[1];", element, text)
        # イベントを発火させて入力を認識させる
        driver.execute_script("""
            var event = new Event('input', { bubbles: true });
            arguments[0].dispatchEvent(event);
        """, element)
        time.sleep(0.05)

    @staticmethod
    def paste_text(driver, element, text):
        """コピペで高速入力（clear削除版）"""
        try:
            # まずJavaScript経由を試す（clearしない）
            InputUtils.js_paste_text(driver, element, text)
        except:
            # 失敗したら通常のコピペ（clearしない）
            element.send_keys(text)
            time.sleep(0.1)

    @staticmethod
    def human_type(element, text, min_delay=0.001, max_delay=0.005):
        """人間らしいタイピングを模倣（超高速版）"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(min_delay, max_delay))  # 超高速化

    @staticmethod
    def clear_and_input(element, text):
        """フィールドをクリアして確実に入力"""
        element.click()
        time.sleep(0.3)
        
        # 既存のテキストをクリア（確実な方法）
        element.send_keys(Keys.CONTROL + "a")  # 全選択
        time.sleep(0.1)
        element.send_keys(Keys.DELETE)  # 削除
        time.sleep(0.1)
        
        # テキストを入力
        element.send_keys(text)


class ValidationUtils:
    @staticmethod
    def verify_input(element, expected_text, field_name):
        """入力内容を確認"""
        try:
            # 要素の値を取得
            actual_value = element.get_attribute('value') or element.text or element.get_attribute('textContent')
            
            if actual_value and expected_text in actual_value:
                print(f"✅ {field_name}の入力確認: {actual_value[:50]}...")
                return True
            else:
                print(f"⚠️ {field_name}の入力が不完全: 期待「{expected_text[:30]}...」実際「{actual_value[:30] if actual_value else 'なし'}...」")
                return False
        except Exception as e:
            print(f"❌ {field_name}の入力確認エラー: {e}")
            return False

    @staticmethod
    def confirm_before_click(element, button_name):
        """ボタンクリック前の確認"""
        try:
            # ボタンの状態確認
            is_enabled = element.is_enabled()
            is_displayed = element.is_displayed()
            button_text = element.text or element.get_attribute('aria-label') or element.get_attribute('value')
            
            print(f"🔍 {button_name}ボタン確認:")
            print(f"   - 表示状態: {'✅ 表示中' if is_displayed else '❌ 非表示'}")
            print(f"   - 有効状態: {'✅ 有効' if is_enabled else '❌ 無効'}")
            print(f"   - ボタンテキスト: {button_text}")
            
            if is_displayed and is_enabled:
                print(f"✅ {button_name}ボタンクリック準備完了")
                return True
            else:
                print(f"⚠️ {button_name}ボタンがクリックできない状態です")
                return False
                
        except Exception as e:
            print(f"❌ {button_name}ボタンの確認エラー: {e}")
            return False


class TimeUtils:
    @staticmethod
    def random_delay(min_sec=0.2, max_sec=0.5):
        """ランダムな遅延（高速化）"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

    @staticmethod
    def wait_for_page_load(driver, timeout=10):
        """ページの読み込み完了を待機"""
        try:
            driver.execute_script("return document.readyState") == "complete"
            time.sleep(1)  # 追加の安全マージン
            return True
        except Exception as e:
            print(f"⚠️ ページ読み込み待機エラー: {e}")
            return False 