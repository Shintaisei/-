#!/usr/bin/env python3
"""
note自動投稿システム - 完全自動実行スクリプト
記事生成 → 校閲 → 投稿まで完全自動化
"""

import sys
import os
import time
from datetime import datetime

# パスを追加
sys.path.append('src')

def print_header(text):
    """ヘッダー表示"""
    print(f"\n{'='*60}")
    print(f"🎬 {text}")
    print(f"{'='*60}\n")

def print_step(text):
    """ステップ表示"""
    print(f"\033[1;33m🎯 {text}\033[0m")
    time.sleep(1)

def print_success(text):
    """成功メッセージ"""
    print(f"\033[1;32m✅ {text}\033[0m")

def print_info(text):
    """情報メッセージ"""
    print(f"\033[1;34mℹ️  {text}\033[0m")

def print_warning(text):
    """警告メッセージ"""
    print(f"\033[1;31m⚠️  {text}\033[0m")

def auto_generate_and_post():
    """完全自動記事生成・投稿"""
    
    print_header("note自動投稿システム - 完全自動実行")
    
    try:
        # モジュールのインポート
        from modules.contents.content_generator import ContentGenerator
        from modules.contents.data_manager import DataManager
        from modules.post.driver_manager import DriverManager
        from modules.post.note_login import NoteLogin
        from modules.post.note_poster import NotePoster
        from modules.config_manager import ConfigManager
        
        print_step("システム初期化中...")
        
        # 各コンポーネントの初期化
        data_manager = DataManager()
        content_generator = ContentGenerator(data_manager)
        config_manager = ConfigManager()
        
        print_success("システム初期化完了")
        
        # ステップ1: 記事生成
        print_step("AI記事生成を実行...")
        
        # 自動テンプレート選択（tech_tutorialを使用）
        template_type = 'tech_tutorial'
        print_info(f"テンプレート: {template_type} を自動選択")
        
        title, content = content_generator.generate_templated_content(template_type)
        
        print_success(f"記事生成完了")
        print_info(f"タイトル: {title}")
        print_info(f"文字数: {len(content)}文字")
        
        # ステップ2: AI校閲・改善
        print_step("AI校閲・改善を実行...")
        
        improvement_result = content_generator.improve_with_fallback(
            title, content, 'comprehensive'
        )
        
        if improvement_result and 'error' not in improvement_result:
            final_content = improvement_result.get('final_content', content)
            editor_used = improvement_result.get('editor', 'Unknown')
            
            print_success(f"AI校閲完了 (使用エディター: {editor_used})")
            print_info(f"改善後文字数: {len(final_content)}文字")
            
            # タイトル改善案から自動選択（最初の案を使用）
            if 'title_suggestions' in improvement_result and improvement_result['title_suggestions']:
                suggestions = improvement_result['title_suggestions']
                if suggestions:
                    # 最初の改善案を選択（番号と説明を除去）
                    new_title = suggestions[0].split(' - ')[0].strip('123456789. ')
                    title = new_title
                    print_success(f"タイトル自動選択: {title}")
            
            content = final_content
        else:
            print_warning("AI校閲をスキップ（元の記事を使用）")
        
        # ステップ3: note用フォーマット調整
        print_step("note用フォーマット調整を実行...")
        
        content = content_generator.format_for_note(content)
        print_success(f"フォーマット調整完了 ({len(content)}文字)")
        
        # ステップ4: 投稿準備
        print_step("note投稿準備...")
        
        # 一時記事データ作成
        temp_article = {
            'id': 999,  # 一時ID
            'title': title,
            'content': content,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'method': 'full_auto'
        }
        
        print_info("投稿内容プレビュー:")
        print("-" * 50)
        print(f"タイトル: {title}")
        print(f"文字数: {len(content)}文字")
        print(f"内容: {content[:200]}...")
        print("-" * 50)
        
        # ステップ5: 実際の投稿実行
        print_step("note自動投稿を実行...")
        
        # WebDriverの初期化
        driver_manager = DriverManager()
        if not driver_manager.setup_driver():
            print_warning("WebDriver初期化に失敗しました")
            return False
        
        # ログイン処理
        note_login = NoteLogin(driver_manager, config_manager)
        print_info("noteログイン中...")
        
        if not note_login.login():
            print_warning("ログインに失敗しました")
            driver_manager.cleanup()
            return False
        
        print_success("ログイン成功")
        
        # 記事投稿処理
        note_poster = NotePoster(driver_manager, temp_article)
        print_info("記事投稿中...")
        
        if note_poster.create_and_publish_article():
            print_success("記事投稿完了！")
            
            # 投稿成功時の処理
            print_info("投稿結果:")
            print(f"✅ タイトル: {title}")
            print(f"✅ 文字数: {len(content)}文字")
            print(f"✅ 投稿時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # データファイルに保存（オプション）
            if data_manager.add_article(title, content, "自動生成", ["AI", "自動投稿"]):
                print_success("記事データを保存しました")
            
            result = True
        else:
            print_warning("記事投稿に失敗しました")
            result = False
        
        # クリーンアップ
        driver_manager.cleanup()
        
        return result
        
    except Exception as e:
        print_warning(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メイン関数"""
    print_header("完全自動note投稿システム")
    
    print_info("このスクリプトは以下を自動実行します:")
    print("1. 📝 AI記事生成（OpenAI GPT-4o）")
    print("2. 🎨 AI校閲・改善（Claude → OpenAI フォールバック）")
    print("3. 📱 note用フォーマット調整")
    print("4. 🚀 note自動投稿")
    
    print_warning("実際のnote投稿が実行されます！")
    
    # 5秒の待機時間
    for i in range(5, 0, -1):
        print(f"開始まで {i} 秒...")
        time.sleep(1)
    
    # 自動実行
    if auto_generate_and_post():
        print_header("🎉 完全自動投稿成功！")
        print_success("記事の生成から投稿まで全て完了しました")
    else:
        print_header("❌ 自動投稿失敗")
        print_warning("エラーが発生しました。ログを確認してください")

if __name__ == "__main__":
    main() 