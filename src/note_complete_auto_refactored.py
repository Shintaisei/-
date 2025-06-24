#!/usr/bin/env python3
"""
note完全自動投稿システム（リファクタリング版）
元のnote_complete_auto.pyの全機能を完全再現し、モジュール化で整理
"""

from datetime import datetime
from modules import (
    ConfigManager,
    DriverManager,
    NoteLogin,
    ArticleManager,
    ContentGenerator,
    NotePoster,
    DataManager,
    TimeUtils
)

class NoteCompleteAutoRefactored:
    """
    note完全自動投稿システム（リファクタリング版）
    元のnote_complete_auto.pyの全機能を完全再現
    """
    
    def __init__(self, config_file="note_login_config.json"):
        """初期化"""
        self.config_file = config_file
        
        # 各モジュールの初期化
        self.config_manager = ConfigManager(config_file)
        self.data_manager = DataManager()
        self.driver_manager = None
        self.note_login = None
        self.article_manager = None
        self.content_generator = None
        self.note_poster = None
        
        print("🤖 note完全自動投稿システム（リファクタリング版）を初期化しました")

    def setup_system(self):
        """システム全体のセットアップ"""
        try:
            print("⚙️ システムをセットアップ中...")
            
            # WebDriverの初期化
            self.driver_manager = DriverManager(self.config_manager)
            if not self.driver_manager.setup_driver():
                print("❌ WebDriverのセットアップに失敗しました")
                return False
            
            # 各モジュールの初期化（依存性注入）
            self.note_login = NoteLogin(self.driver_manager, self.config_manager)
            self.article_manager = ArticleManager(self.data_manager)
            self.content_generator = ContentGenerator(self.data_manager)
            self.note_poster = NotePoster(self.driver_manager, self.article_manager)
            
            print("✅ システムのセットアップが完了しました")
            return True
            
        except Exception as e:
            print(f"❌ システムセットアップエラー: {e}")
            return False

    def run_auto_posting(self):
        """自動投稿実行（元のrun_auto_postingメソッドを完全再現）"""
        try:
            print("🤖 note完全自動投稿システムを開始します...")
            
            # システムセットアップ
            if not self.setup_system():
                return False
            
            # ログイン実行
            print("🔐 ログイン処理を開始します...")
            if not self.note_login.login():
                print("❌ ログインに失敗しました")
                return False
            
            # 記事作成・投稿実行
            print("📝 記事作成・投稿処理を開始します...")
            if not self.note_poster.create_and_publish_article():
                print("❌ 記事作成・投稿に失敗しました")
                return False
            
            print("✅ 全ての処理が正常に完了しました！")
            return True
            
        except Exception as e:
            print(f"❌ 自動投稿中にエラーが発生しました: {e}")
            return False
        finally:
            # クリーンアップ
            self.cleanup()

    def cleanup(self):
        """システムクリーンアップ"""
        if self.driver_manager and self.driver_manager.get_driver():
            print("🔄 ブラウザを終了しています...")
            TimeUtils.random_delay(3, 3)  # 元のコードと同じ3秒待機
            self.driver_manager.quit_driver()

    def show_menu(self):
        """メニュー表示（記事管理・LLM生成機能を追加）"""
        print("\n" + "="*50)
        print("🤖 note完全自動投稿システム")
        print("="*50)
        print("1. 自動実行（ランダム記事で投稿）")
        print("2. LLM記事生成で投稿")
        print("3. 記事一覧を表示")
        print("4. 特定の記事で投稿")
        print("5. 新しい記事を追加")
        print("6. 設定確認")
        print("7. 終了")
        print("="*50)

    def run_llm_generated_posting(self):
        """LLM記事生成で投稿実行（テンプレート+テーマ選択対応）"""
        try:
            print("\n🤖 LLM記事生成機能")
            print("=" * 40)
            
            # ContentGeneratorの初期化確認
            if not hasattr(self, 'content_generator') or not self.content_generator:
                self.content_generator = ContentGenerator(self.data_manager)
            
            # LLM利用可能性確認
            if self.content_generator.is_llm_available():
                print("✅ LLM機能が利用可能です")
                method = "llm"
            else:
                print("⚠️ LLM機能は現在無効です。テンプレート生成を使用します。")
                method = "template"
            
            # 生成方法選択
            print("\n生成方法を選択してください:")
            print("1. 自動生成（ランダムテンプレート）")
            print("2. テンプレート指定のみ")
            print("3. テンプレート + テーマ指定")
            if method == "llm":
                print("4. フリートピック指定")
            
            choice = input("選択 (1-4): ").strip()
            
            generation_kwargs = {}
            
            if choice in ["2", "3"]:
                # テンプレート選択
                template_types = self.content_generator.list_template_types()
                print("\n📋 利用可能なテンプレート:")
                for i, template_type in enumerate(template_types, 1):
                    template_info = self.content_generator.get_template_info(template_type)
                    print(f"{i}. {template_type}")
                    print(f"   スタイル: {template_info['style']}")
                    print(f"   文字数: {template_info.get('length', '標準')}")
                    print()
                
                try:
                    template_idx = int(input("テンプレート番号を選択: ").strip()) - 1
                    if 0 <= template_idx < len(template_types):
                        selected_template = template_types[template_idx]
                        generation_kwargs["template_type"] = selected_template
                        print(f"✅ テンプレート '{selected_template}' を選択しました")
                        
                        # テーマ選択（choice == "3"の場合）
                        if choice == "3":
                            theme = self._select_theme_for_template(selected_template)
                            if theme:
                                generation_kwargs["topic"] = theme
                                print(f"✅ テーマ '{theme}' を選択しました")
                        
                        method = "llm" if self.content_generator.is_llm_available() else "template"
                    else:
                        print("無効な選択です。自動生成を使用します。")
                except ValueError:
                    print("無効な入力です。自動生成を使用します。")
                    
            elif choice == "4" and method == "llm":
                # フリートピック指定
                topic = input("記事のトピックを自由に入力してください: ").strip()
                if topic:
                    generation_kwargs["topic"] = topic
                    print(f"✅ トピック '{topic}' を設定しました")
                method = "llm"
            
            # 記事生成
            print(f"\n🎯 記事を生成中... (方法: {method})")
            title, content = self.content_generator.generate_content(method, **generation_kwargs)
            
            # 生成結果確認
            print(f"\n📝 生成された記事:")
            print(f"タイトル: {title}")
            print(f"文字数: {len(content)}文字")
            print(f"内容: {content[:150]}...")
            
            # Claude編集オプション
            if self.content_generator.is_claude_available():
                claude_confirm = input("\n🤖 Claude AIで記事を改善しますか？（校閲・バズ要素・タイトル改善） (y/N): ").strip().lower()
                if claude_confirm == 'y':
                    print("\nClaude改善オプション:")
                    print("1. 包括的改善（校閲 + バズ要素 + タイトル改善）")
                    print("2. 校閲のみ")
                    print("3. バズ要素追加のみ")
                    print("4. タイトル改善のみ")
                    
                    claude_choice = input("選択 (1-4): ").strip()
                    improvement_type = {
                        "1": "comprehensive",
                        "2": "proofread", 
                        "3": "buzz",
                        "4": "title"
                    }.get(claude_choice, "comprehensive")
                    
                    improvement_result = self.content_generator.improve_with_fallback(title, content, improvement_type)
                    
                    if improvement_result and "error" not in improvement_result:
                        if improvement_type == "comprehensive":
                            print(f"\n{self.content_generator.claude_editor.get_improvement_summary(improvement_result)}")
                            
                            # タイトル選択
                            if "title_suggestions" in improvement_result:
                                print("\n💡 タイトル改善案:")
                                for i, suggestion in enumerate(improvement_result["title_suggestions"], 1):
                                    print(f"{i}. {suggestion}")
                                
                                title_choice = input(f"\nタイトルを選択 (1-{len(improvement_result['title_suggestions'])}, 0で元のまま): ").strip()
                                try:
                                    choice_idx = int(title_choice) - 1
                                    if 0 <= choice_idx < len(improvement_result["title_suggestions"]):
                                        selected_title = improvement_result["title_suggestions"][choice_idx].split(" - ")[0].strip("123456789. ")
                                        title = selected_title
                                        print(f"✅ 新しいタイトル: {title}")
                                except ValueError:
                                    print("元のタイトルを使用します")
                            
                            # 改善された内容を使用
                            content = improvement_result.get("final_content", content)
                            print(f"✅ 改善された記事を使用します（{len(content)}文字）")
                        
                        elif improvement_type == "proofread":
                            content = improvement_result.get("proofread_content", content)
                            print(f"✅ 校閲完了（{len(content)}文字）")
                        
                        elif improvement_type == "buzz":
                            content = improvement_result.get("buzz_content", content)
                            print(f"✅ バズ要素追加完了（{len(content)}文字）")
                        
                        elif improvement_type == "title":
                            if "suggestions" in improvement_result:
                                print("\n💡 タイトル改善案:")
                                for i, suggestion in enumerate(improvement_result["suggestions"], 1):
                                    print(f"{i}. {suggestion}")
                                
                                title_choice = input(f"\nタイトルを選択 (1-{len(improvement_result['suggestions'])}, 0で元のまま): ").strip()
                                try:
                                    choice_idx = int(title_choice) - 1
                                    if 0 <= choice_idx < len(improvement_result["suggestions"]):
                                        selected_title = improvement_result["suggestions"][choice_idx].split(" - ")[0].strip("123456789. ")
                                        title = selected_title
                                        print(f"✅ 新しいタイトル: {title}")
                                except ValueError:
                                    print("元のタイトルを使用します")
                    else:
                        print("❌ Claude改善に失敗しました。元の記事を使用します。")
            
            # note用フォーマット調整オプション
            format_confirm = input("\n📱 note用にフォーマットを調整しますか？（コードブロック、見出しを調整） (Y/n): ").strip().lower()
            if format_confirm != 'n':
                print("🔄 note用フォーマット調整中...")
                content = self.content_generator.format_for_note(content)
                print(f"✅ フォーマット調整完了（調整後文字数: {len(content)}文字）")
                print(f"調整後プレビュー: {content[:200]}...")
            
            confirm = input("\nこの記事で投稿しますか？ (y/N): ").strip().lower()
            if confirm != 'y':
                print("投稿をキャンセルしました。")
                return False
            
            # システムセットアップ
            if not self.setup_system():
                return False
            
            # 生成された記事を一時的に設定
            temp_article = {
                "id": 0,
                "title": title,
                "content": content,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "method": method
            }
            self.article_manager.selected_article = temp_article
            
            # ログイン実行
            print("🔐 ログイン処理を開始します...")
            if not self.note_login.login():
                print("❌ ログインに失敗しました")
                return False
            
            # 記事投稿実行
            print("📝 記事投稿処理を開始します...")
            if not self.note_poster.create_and_publish_article():
                print("❌ 記事投稿に失敗しました")
                return False
            
            print("✅ LLM生成記事の投稿が完了しました！")
            
            # 投稿成功した記事をデータファイルに保存するか確認
            save_confirm = input("\n📚 この記事をデータファイルに保存しますか？ (y/N): ").strip().lower()
            if save_confirm == 'y':
                category = input("カテゴリを入力（空白でデフォルト）: ").strip()
                tags_input = input("タグを入力（カンマ区切り、空白でスキップ）: ").strip()
                
                tags = []
                if tags_input:
                    tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
                
                if self.data_manager.add_article(title, content, category, tags):
                    print("✅ 記事をデータファイルに保存しました")
                else:
                    print("❌ 記事の保存に失敗しました")
            
            return True
            
        except Exception as e:
            print(f"❌ LLM記事生成投稿中にエラーが発生しました: {e}")
            return False
        finally:
            self.cleanup()

    def run_specific_article_posting(self):
        """特定の記事で投稿実行"""
        try:
            # 記事一覧を表示
            self.data_manager.list_articles()
            
            # 記事IDを入力
            try:
                article_id = int(input("\n投稿する記事のIDを入力してください: ").strip())
            except ValueError:
                print("❌ 無効なIDです。数字を入力してください。")
                return False
            
            # 記事を取得
            article = self.data_manager.get_article_by_id(article_id)
            if not article:
                return False
            
            # 記事内容を確認
            title, content = self.data_manager.format_article_content(article)
            print(f"\n📝 選択された記事:")
            print(f"タイトル: {title}")
            print(f"文字数: {len(content)}文字")
            print(f"内容: {content[:100]}...")
            
            # ContentGeneratorの初期化
            if not hasattr(self, 'content_generator') or not self.content_generator:
                from .modules.contents import ContentGenerator
                self.content_generator = ContentGenerator(self.data_manager)
            
            # Claude改善オプション
            if (self.content_generator.is_claude_available() or 
                self.content_generator.is_openai_editor_available()):
                
                claude_confirm = input("\n🎨 記事を改善しますか？（Claude/OpenAI編集機能） (y/N): ").strip().lower()
                if claude_confirm == 'y':
                    print("\n🎯 改善タイプを選択してください:")
                    print("1. 包括的改善（校閲 + バズ要素 + タイトル改善）")
                    print("2. 校閲のみ")
                    print("3. バズ要素追加のみ")
                    print("4. タイトル改善のみ")
                    
                    claude_choice = input("選択 (1-4): ").strip()
                    improvement_type = {
                        "1": "comprehensive",
                        "2": "proofread", 
                        "3": "buzz",
                        "4": "title"
                    }.get(claude_choice, "comprehensive")
                    
                    improvement_result = self.content_generator.improve_with_fallback(title, content, improvement_type)
                    
                    if improvement_result and "error" not in improvement_result:
                        if improvement_type == "comprehensive":
                            print(f"\n改善サマリー:")
                            editor_name = improvement_result.get("editor", "AI")
                            print(f"使用エディター: {editor_name}")
                            
                            # タイトル選択
                            if "title_suggestions" in improvement_result:
                                print("\n💡 タイトル改善案:")
                                for i, suggestion in enumerate(improvement_result["title_suggestions"], 1):
                                    print(f"{i}. {suggestion}")
                                
                                title_choice = input(f"\nタイトルを選択 (1-{len(improvement_result['title_suggestions'])}, 0で元のまま): ").strip()
                                try:
                                    choice_idx = int(title_choice) - 1
                                    if 0 <= choice_idx < len(improvement_result["title_suggestions"]):
                                        selected_title = improvement_result["title_suggestions"][choice_idx].split(" - ")[0].strip("123456789. ")
                                        title = selected_title
                                        print(f"✅ 新しいタイトル: {title}")
                                except ValueError:
                                    print("元のタイトルを使用します")
                            
                            # 改善された内容を使用
                            content = improvement_result.get("final_content", content)
                            print(f"✅ 改善された記事を使用します（{len(content)}文字）")
                        
                        elif improvement_type == "proofread":
                            content = improvement_result.get("proofread_content", content)
                            print(f"✅ 校閲完了（{len(content)}文字）")
                        
                        elif improvement_type == "buzz":
                            content = improvement_result.get("buzz_content", content)
                            print(f"✅ バズ要素追加完了（{len(content)}文字）")
                        
                        elif improvement_type == "title":
                            if "suggestions" in improvement_result:
                                print("\n💡 タイトル改善案:")
                                for i, suggestion in enumerate(improvement_result["suggestions"], 1):
                                    print(f"{i}. {suggestion}")
                                
                                title_choice = input(f"\nタイトルを選択 (1-{len(improvement_result['suggestions'])}, 0で元のまま): ").strip()
                                try:
                                    choice_idx = int(title_choice) - 1
                                    if 0 <= choice_idx < len(improvement_result["suggestions"]):
                                        selected_title = improvement_result["suggestions"][choice_idx].split(" - ")[0].strip("123456789. ")
                                        title = selected_title
                                        print(f"✅ 新しいタイトル: {title}")
                                except ValueError:
                                    print("元のタイトルを使用します")
                        
                        # 記事を更新
                        article['title'] = title
                        article['content'] = content
                    else:
                        print("❌ 記事改善に失敗しました。元の記事を使用します。")
            
            # note用フォーマット調整オプション
            format_confirm = input("\n📱 note用にフォーマットを調整しますか？（コードブロック、見出しを調整） (Y/n): ").strip().lower()
            if format_confirm != 'n':
                print("🔄 note用フォーマット調整中...")
                content = self.content_generator.format_for_note(content)
                print(f"✅ フォーマット調整完了（調整後文字数: {len(content)}文字）")
                print(f"調整後プレビュー: {content[:200]}...")
                
                # 調整後の内容で記事を更新
                article['content'] = content
            
            confirm = input("\nこの記事で投稿しますか？ (y/N): ").strip().lower()
            if confirm != 'y':
                print("投稿をキャンセルしました。")
                return False
            
            # システムセットアップ
            if not self.setup_system():
                return False
            
            # 記事管理器に特定記事を設定
            self.article_manager.selected_article = article
            
            # ログイン実行
            print("🔐 ログイン処理を開始します...")
            if not self.note_login.login():
                print("❌ ログインに失敗しました")
                return False
            
            # 記事投稿実行
            print("📝 記事投稿処理を開始します...")
            if not self.note_poster.create_and_publish_article():
                print("❌ 記事投稿に失敗しました")
                return False
            
            print("✅ 指定された記事の投稿が完了しました！")
            return True
            
        except Exception as e:
            print(f"❌ 特定記事投稿中にエラーが発生しました: {e}")
            return False
        finally:
            self.cleanup()

    def add_new_article(self):
        """新しい記事を追加"""
        try:
            print("\n📝 新しい記事を追加します")
            print("=" * 40)
            
            title = input("タイトルを入力してください: ").strip()
            if not title:
                print("❌ タイトルが入力されていません")
                return False
            
            print("\n本文を入力してください（改行は \\n で入力）:")
            print("入力完了後、空行でEnterを押してください")
            
            content_lines = []
            while True:
                line = input()
                if line == "":
                    break
                content_lines.append(line)
            
            content = "\n".join(content_lines).replace("\\n", "\n")
            
            if not content:
                print("❌ 本文が入力されていません")
                return False
            
            # カテゴリとタグの入力（オプション）
            category = input("\nカテゴリを入力してください（空白でデフォルト）: ").strip()
            tags_input = input("タグを入力してください（カンマ区切り、空白でスキップ）: ").strip()
            
            tags = []
            if tags_input:
                tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
            
            # 記事を追加
            if self.data_manager.add_article(title, content, category, tags):
                print("✅ 記事が正常に追加されました！")
                return True
            else:
                print("❌ 記事の追加に失敗しました")
                return False
                
        except Exception as e:
            print(f"❌ 記事追加中にエラーが発生しました: {e}")
            return False

    def show_settings(self):
        """設定確認表示（LLM設定情報を追加）"""
        config = self.config_manager.get_config()
        print(f"\n📋 現在の設定:")
        print("=" * 50)
        print("🔐 ログイン設定:")
        print(f"  Email: {config.get('email', '未設定')}")
        print(f"  Password: {'設定済み' if config.get('password') else '未設定'}")
        
        print("\n📚 記事データ設定:")
        print(f"  データファイル: {self.data_manager.data_file_path}")
        print(f"  利用可能記事数: {len(self.data_manager.get_active_articles())}件")
        
        print("\n🤖 LLM設定:")
        if hasattr(self, 'content_generator') and self.content_generator:
            llm_config = self.content_generator.llm_config
            print(f"  プロバイダー: {llm_config.get('provider', '未設定')}")
            print(f"  モデル: {llm_config.get('model', '未設定')}")
            print(f"  APIキー: {'設定済み' if llm_config.get('api_key') else '未設定'}")
            print(f"  LLM機能: {'✅ 有効' if llm_config.get('enabled', False) else '❌ 無効'}")
            print(f"  最大トークン数: {llm_config.get('max_tokens', 'デフォルト')}")
            print(f"  Temperature: {llm_config.get('temperature', 'デフォルト')}")
        else:
            print("  LLMモジュール: 未初期化")
        
        print("\n🎨 記事編集機能:")
        if hasattr(self, 'content_generator') and self.content_generator:
            # Claude編集機能
            claude_available = self.content_generator.is_claude_available()
            print(f"  Claude API: {'✅ 利用可能' if claude_available else '❌ 利用不可'}")
            if claude_available and hasattr(self.content_generator, 'claude_editor'):
                claude_config = self.content_generator.claude_editor.config
                print(f"    モデル: {claude_config.get('model', 'claude-3-5-sonnet-20241022')}")
                print(f"    Temperature: {claude_config.get('temperature', 0.7)}")
                print(f"    最大トークン数: {claude_config.get('max_tokens', 4000)}")
            
            # OpenAI編集機能
            openai_available = self.content_generator.is_openai_editor_available()
            print(f"  OpenAI編集 API: {'✅ 利用可能' if openai_available else '❌ 利用不可'}")
            if openai_available and hasattr(self.content_generator, 'openai_editor'):
                openai_config = self.content_generator.openai_editor.config
                print(f"    モデル: {openai_config.get('model', 'gpt-4o')}")
                print(f"    Temperature: {openai_config.get('temperature', 0.7)}")
                print(f"    最大トークン数: {openai_config.get('max_tokens', 3500)}")
            
            # フォールバック機能
            if claude_available or openai_available:
                print(f"  フォールバック機能: ✅ 有効")
                print(f"    優先順位: Claude → OpenAI")
                print(f"    機能: 校閲・バズ要素追加・タイトル改善・包括改善")
            else:
                print("  ※ llm_config.jsonで編集機能の設定確認が必要です")
        else:
            print("  編集モジュール: 未初期化")
        
        print("\n🎯 利用可能なテンプレート:")
        if hasattr(self, 'content_generator') and self.content_generator:
            template_types = self.content_generator.list_template_types()
            for template_type in template_types:
                template_info = self.content_generator.get_template_info(template_type)
                print(f"  - {template_type}: {template_info['style']}")
        
        print("=" * 50)
        input("\nEnterキーで戻る...")
    
    def _select_theme_for_template(self, template_type: str) -> str:
        """テンプレートタイプに応じたテーマ選択"""
        theme_options = {
            "tech_tutorial": [
                "Python基礎プログラミング",
                "Docker入門とコンテナ化",
                "Git/GitHub実践活用",
                "React.js開発入門",
                "Node.js API開発",
                "データベース設計基礎",
                "AWS クラウド入門",
                "Linux コマンド活用",
                "VS Code 効率化設定",
                "テスト駆動開発(TDD)"
            ],
            "tech_deep_dive": [
                "JavaScriptエンジンの仕組み",
                "HTTP/HTTPSプロトコルの詳細",
                "データベースインデックスの最適化",
                "メモリ管理とガベージコレクション",
                "認証・認可システムの設計",
                "マイクロサービスアーキテクチャ",
                "キャッシュ戦略と実装",
                "非同期処理とイベントループ",
                "セキュリティ脆弱性と対策",
                "パフォーマンス最適化手法"
            ],
            "dev_experience": [
                "大規模リファクタリング体験談",
                "チーム開発での失敗と学び",
                "技術選定の判断プロセス",
                "パフォーマンス問題の解決",
                "レガシーコードとの向き合い方",
                "新技術導入の挑戦",
                "バグ調査・デバッグ体験",
                "プロジェクト炎上からの復活",
                "コードレビュー文化の構築",
                "個人開発から学んだこと"
            ],
            "tech_comparison": [
                "React vs Vue.js vs Angular",
                "MySQL vs PostgreSQL vs MongoDB",
                "Docker vs Kubernetes vs Serverless",
                "REST API vs GraphQL vs gRPC",
                "TypeScript vs JavaScript",
                "AWS vs Azure vs GCP",
                "Redux vs Context API vs Zustand",
                "Jest vs Vitest vs Cypress",
                "Nginx vs Apache vs Caddy",
                "npm vs yarn vs pnpm"
            ],
            "programming_tips": [
                "効率的なデバッグ手法",
                "可読性の高いコードの書き方",
                "エラーハンドリングのベストプラクティス",
                "コードレビューのコツ",
                "リファクタリングの進め方",
                "命名規則とコメント活用",
                "パフォーマンス向上のテクニック",
                "セキュアコーディング実践",
                "テストコード設計のポイント",
                "開発環境の効率化"
            ],
            "tech_trends": [
                "AI・機械学習の最新動向",
                "Web3・ブロックチェーン技術",
                "エッジコンピューティングの進化",
                "ローコード・ノーコード開発",
                "量子コンピューティング",
                "WebAssembly(WASM)の可能性",
                "5G技術とアプリケーション",
                "サーバーレスアーキテクチャ",
                "DevOps・GitOpsの発展",
                "プライバシー保護技術"
            ],
            "learning_share": [
                "オンライン学習プラットフォーム活用",
                "技術書の効果的な読み方",
                "プログラミング言語の学習順序",
                "実践的なポートフォリオ作成",
                "OSS貢献の始め方",
                "技術コミュニティ参加のメリット",
                "資格取得の価値と活用",
                "メンターとの関わり方",
                "継続的学習の習慣化",
                "スキルアップのロードマップ"
            ],
            "problem_solving": [
                "メモリリークの特定と解決",
                "パフォーマンス劣化の原因調査",
                "セキュリティ脆弱性の修正",
                "データベースクエリ最適化",
                "API レスポンス速度改善",
                "フロントエンド描画最適化",
                "サーバー負荷分散対策",
                "バックアップ・復旧戦略",
                "モニタリング・アラート設定",
                "障害対応とポストモーテム"
            ]
        }
        
        themes = theme_options.get(template_type, [
            "プログラミング基礎",
            "Web開発",
            "データベース",
            "クラウド技術",
            "開発手法"
        ])
        
        print(f"\n🎯 '{template_type}' テンプレート用のテーマを選択してください:")
        for i, theme in enumerate(themes, 1):
            print(f"{i}. {theme}")
        
        print(f"{len(themes) + 1}. カスタムテーマ（自分で入力）")
        
        try:
            choice = int(input("テーマ番号を選択: ").strip())
            if 1 <= choice <= len(themes):
                return themes[choice - 1]
            elif choice == len(themes) + 1:
                custom_theme = input("カスタムテーマを入力してください: ").strip()
                return custom_theme if custom_theme else None
            else:
                print("無効な選択です。")
                return None
        except ValueError:
            print("無効な入力です。")
            return None

def main():
    """メイン関数（記事管理・LLM生成機能を追加）"""
    auto_poster = NoteCompleteAutoRefactored()
    
    while True:
        auto_poster.show_menu()
        choice = input("選択してください (1-7): ").strip()
        
        if choice == "1":
            print("\n🚀 自動投稿を開始します...")
            auto_poster.run_auto_posting()
            break
        elif choice == "2":
            print("\n🤖 LLM記事生成で投稿します...")
            auto_poster.run_llm_generated_posting()
            break
        elif choice == "3":
            print("\n📚 記事一覧を表示します...")
            auto_poster.data_manager.list_articles()
            input("\nEnterキーで戻る...")
        elif choice == "4":
            print("\n📝 特定の記事で投稿します...")
            auto_poster.run_specific_article_posting()
            break
        elif choice == "5":
            print("\n➕ 新しい記事を追加します...")
            auto_poster.add_new_article()
        elif choice == "6":
            auto_poster.show_settings()
        elif choice == "7":
            print("👋 システムを終了します。")
            break
        else:
            print("❌ 無効な選択です。1-7の数字を入力してください。")

if __name__ == "__main__":
    main() 