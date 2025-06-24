#!/usr/bin/env python3
"""
コンテンツ生成モジュール
LLMを使用した記事の自動生成
将来的にOpenAI API、Claude API、ローカルLLM等に対応予定
"""

import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from .data_manager import DataManager
from .claude_editor import ClaudeEditor

try:
    from .openai_editor import OpenAIEditor
    OPENAI_EDITOR_AVAILABLE = True
except ImportError:
    OPENAI_EDITOR_AVAILABLE = False
    print("⚠️ OpenAI編集機能が利用できません")

class ContentGenerator:
    def __init__(self, data_manager: DataManager = None):
        """
        コンテンツ生成器の初期化
        
        Args:
            data_manager: データマネージャーインスタンス
        """
        self.data_manager = data_manager or DataManager()
        self.llm_config = self._load_llm_config()
        self.generation_templates = self._load_generation_templates()
        self.claude_editor = None
        self.openai_editor = None
        self._init_claude_editor()
        self._init_openai_editor()
    
    def _load_llm_config(self) -> Dict:
        """LLM設定を読み込み"""
        try:
            import os
            import json
            
            # 設定ファイルのパスを確認
            config_paths = [
                "llm_config.json",
                "../llm_config.json", 
                "../../llm_config.json"
            ]
            
            config_data = None
            for config_path in config_paths:
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    print(f"✅ LLM設定ファイルを読み込みました: {config_path}")
                    break
            
            if config_data and "llm_settings" in config_data:
                llm_config = config_data["llm_settings"]
                print(f"🤖 LLM設定: {llm_config['provider']}/{llm_config['model']} (有効: {llm_config.get('enabled', False)})")
                return llm_config
            else:
                print("⚠️ LLM設定ファイルが見つかりません。デフォルト設定を使用します。")
                return {
                    "provider": "openai",
                    "model": "gpt-3.5-turbo", 
                    "max_tokens": 2000,
                    "temperature": 0.7,
                    "enabled": False
                }
                
        except Exception as e:
            print(f"⚠️ LLM設定読み込みエラー: {e}")
            return {"enabled": False}
    
    def _load_generation_templates(self) -> List[Dict]:
        """記事生成テンプレートを読み込み（テックブログ向けに拡張）"""
        return [
            {
                "type": "tech_tutorial",
                "prompt": "特定の技術やツールの使い方を、実際のコード例や詳細な手順を交えて徹底的に解説してください。初心者から中級者が完全に理解し、実際に実践できるよう、非常に丁寧に説明してください。環境構築から実装、トラブルシューティングまで網羅してください。",
                "style": "技術解説・教育的で非常に詳細な文体",
                "length": "1500-2200文字"
            },
            {
                "type": "tech_deep_dive",
                "prompt": "特定の技術概念や仕組みについて、その背景、歴史、原理を非常に深く掘り下げて解説してください。技術的な正確性を最重視し、具体例、図解的説明、実装例を豊富に用いて、読者が完全に理解できるよう詳細に説明してください。",
                "style": "技術的で分析的、非常に詳細な解説文体",
                "length": "1800-2500文字"
            },
            {
                "type": "dev_experience",
                "prompt": "開発プロジェクトや技術的な課題解決の体験について、時系列での詳細なプロセス、遭遇した問題、試行錯誤の過程、最終的な解決策、学んだ教訓を非常に具体的に共有してください。他の開発者が同じ状況に遭遇した際の完全なガイドとなるような実践的な内容にしてください。",
                "style": "体験談・実践的で非常に具体的な文体",
                "length": "1400-1900文字"
            },
            {
                "type": "tech_comparison",
                "prompt": "複数の技術、ツール、フレームワークを詳細に比較し、それぞれの特徴、メリット・デメリット、パフォーマンス、学習コスト、適用場面、実装例を非常に詳しく分析してください。実際の使用経験に基づいた具体的な選択指針と、各技術の詳細な使用例を提供してください。",
                "style": "比較分析・客観的で非常に詳細な文体",
                "length": "1600-2300文字"
            },
            {
                "type": "programming_tips",
                "prompt": "効率的なプログラミング手法、コーディングのベストプラクティス、開発のコツについて、具体的なコード例、実装パターン、避けるべきアンチパターンを豊富に含めて詳しく解説してください。理論だけでなく、実際のプロジェクトで即座に活用できる実践的な内容を詳細に提供してください。",
                "style": "実践的・教育的で非常に具体的な文体",
                "length": "1300-1800文字"
            },
            {
                "type": "tech_trends",
                "prompt": "最新の技術トレンドや業界動向について、その背景、技術的詳細、現在の採用状況、将来への影響、実際の活用事例を非常に詳しく考察してください。技術者の視点から深い洞察と、実際の導入を検討する際の詳細な指針を提供してください。",
                "style": "分析的・洞察的で非常に専門的な文体",
                "length": "1500-2100文字"
            },
            # 従来のテンプレートも保持（テック向けに大幅拡張）
            {
                "type": "learning_share",
                "prompt": "最近学んだ技術や開発手法について、その詳細な学習過程、使用した学習リソース、実践での具体的な活用方法、遭遇した困難と解決方法を非常に詳しく共有してください。他の開発者にとって完全な学習ガイドとなるような有益な情報と、実践的で具体的なアドバイスを豊富に含めてください。",
                "style": "教育的・共有型で非常に詳細な文体",
                "length": "1400-1900文字"
            },
            {
                "type": "problem_solving",
                "prompt": "開発中に遭遇した技術的な問題とその詳細な解決過程について、問題の発見から原因特定、解決策の検討、実装、検証までの全プロセスを時系列で詳しく解説してください。具体的なデバッグ手順、使用したツール、試行錯誤の詳細を含め、同じ問題に直面する他の開発者が完全に問題を解決できるような包括的な内容にしてください。",
                "style": "問題解決・実践的で非常に詳細な文体",
                "length": "1500-2000文字"
            }
        ]
    
    def generate_with_llm(self, topic: str = None, template_type: str = None) -> Optional[Tuple[str, str]]:
        """
        LLMを使用した記事生成
        
        Args:
            topic: 記事のトピック
            template_type: 生成テンプレートのタイプ
            
        Returns:
            Optional[Tuple[str, str]]: (タイトル, 内容) または None
        """
        if not self.llm_config.get("enabled", False):
            print("⚠️ LLM機能は現在無効です。フォールバック記事生成を使用します。")
            return None
        
        try:
            print("🤖 OpenAI APIで記事生成を実行中...")
            
            # OpenAI APIを使用した記事生成
            if self.llm_config.get("provider") == "openai":
                return self._generate_with_openai(topic, template_type)
            else:
                print(f"⚠️ 未対応のプロバイダー: {self.llm_config.get('provider')}")
                return None
            
        except Exception as e:
            print(f"❌ LLM記事生成エラー: {e}")
            return None
    
    def _generate_with_openai(self, topic: str = None, template_type: str = None) -> Optional[Tuple[str, str]]:
        """OpenAI APIを使用した記事生成"""
        try:
            # OpenAIライブラリのインポート
            try:
                import openai
            except ImportError:
                print("❌ OpenAIライブラリがインストールされていません。")
                print("   pip install openai でインストールしてください。")
                return None
            
            # APIキーの設定
            api_key = self.llm_config.get("api_key")
            if not api_key:
                print("❌ OpenAI APIキーが設定されていません。")
                return None
            
            # OpenAI クライアントの初期化
            client = openai.OpenAI(api_key=api_key)
            
            # プロンプトの構築
            prompt = self._build_prompt(topic, template_type)
            print(f"📝 プロンプト: {prompt[:100]}...")
            
            # API呼び出し
            response = client.chat.completions.create(
                model=self.llm_config.get("model", "gpt-4o"),
                messages=[
                    {
                        "role": "system", 
                        "content": """あなたは10年以上の経験を持つシニアソフトウェアエンジニアで、技術ブログの執筆とテクニカルライティングを専門としています。

専門性と特徴:
- 技術的に正確で実践的、かつ非常に詳細な内容を提供する
- 複雑な技術概念を段階的に分かりやすく説明する高度な能力
- 豊富なコード例、実装パターン、具体的な手順を含めた包括的な解説ができる
- 初心者から上級者まで、読者のレベルに応じて適切な深さで内容を調整する
- 最新の技術トレンドと豊富な実践的経験の両方を持つ
- 実際のプロジェクトでの経験に基づいた具体的なアドバイスを提供できる

記事執筆の品質基準（厳格に遵守）:
- 技術的正確性と検証可能性を最優先する
- 実際に動作し、読者が試せる具体的で詳細な例を豊富に提供する
- 読者が記事を読んだ後、即座に実践できるような詳細なガイドを作成する
- 専門用語は必ず詳細に説明し、初心者から上級者まで理解できるようにする
- 論理的で構造化された、非常に読みやすい文章を書く
- 背景情報、実装手順、ベストプラクティス、トラブルシューティングを包括的に含める
- 文字数制限を意識し、指定された文字数範囲を必ず満たす
- 実践的な価値が高く、読者の技術スキル向上に直接貢献する内容にする

執筆スタイル:
- 詳細で包括的、かつ実践的
- 段階的で論理的な構成
- 具体例とコードを豊富に使用
- 読者との対話を意識した親しみやすさも保持"""
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=self.llm_config.get("max_tokens", 3500),
                temperature=self.llm_config.get("temperature", 0.6)
            )
            
            # レスポンスの解析
            generated_text = response.choices[0].message.content.strip()
            
            # タイトルと本文の分離
            title, content = self._parse_generated_content(generated_text)
            
            if title and content:
                print(f"✅ OpenAI APIで記事生成完了:")
                print(f"   タイトル: {title}")
                print(f"   内容: {content[:50]}...")
                return title, content
            else:
                print("⚠️ 生成されたコンテンツの解析に失敗しました")
                return None
                
        except Exception as e:
            print(f"❌ OpenAI API呼び出しエラー: {e}")
            return None
    
    def _build_prompt(self, topic: str = None, template_type: str = None) -> str:
        """LLM用のプロンプトを構築（テックブログ向けに強化）"""
        from datetime import datetime
        
        # 設定から詳細な要件を取得
        preferences = self.llm_config.get("generation_preferences", {})
        target_length = preferences.get("target_length", "800-1200文字")
        style = preferences.get("default_style", "技術的で詳細、かつ読みやすい解説文体")
        
        # 基本プロンプト（テックブログ向け・大幅拡張）
        base_prompt = f"""
note.comに投稿する非常に詳細で包括的な技術ブログ記事を生成してください。

要件:
- 文字数: {target_length} (必ず下限を満たし、できるだけ上限に近づけてください)
- 文体: {style}
- 対象読者: プログラマー・エンジニア・技術に興味のある人（初心者から上級者まで）
- 構成: 魅力的なタイトル + 非常に詳細で包括的な本文
- 技術的正確性: 正確で実践的、かつ検証可能な情報を提供する
- 可読性: 適切な見出し、改行、段落構成、箇条書きで非常に読みやすくする
- 実用性: 読者が実際に活用できる具体的で詳細な内容を豊富に含める

記事の特徴（必須要素）:
- 豊富な具体的コード例やコマンド例（実際に動作するもの）
- 技術的な背景、歴史、原理の詳細な説明
- 実践的なアドバイス、ベストプラクティス、アンチパターンの詳細
- 段階的な手順説明（ステップバイステップ）
- 初心者から上級者まで理解できるよう、専門用語の詳細な説明
- 実際の使用例、ユースケース、活用場面の具体例
- トラブルシューティング情報（よくある問題と解決法）
- 参考リソースや次のステップの提案
- 最後に読者との交流を促すコメント誘導

記事構成の推奨パターン:
1. 導入・概要
2. 背景・必要性
3. 詳細解説（複数のセクションに分けて）
4. 実践例・ハンズオン
5. ベストプラクティス・注意点
6. まとめ・次のステップ
7. 読者との交流促進

出力形式:
タイトル: [技術的で魅力的、かつ具体的なタイトル]

[非常に詳細で実践的、包括的な本文内容]
"""
        
        # トピック（テーマ）が指定されている場合
        if topic:
            base_prompt += f"\n記事のトピック・テーマ: {topic}\n"
            base_prompt += "このトピックを中心に、具体的で実践的な内容を詳しく解説してください。\n"
        
        # テンプレートタイプが指定されている場合
        if template_type:
            template = self._get_template(template_type)
            if template:
                base_prompt += f"\n記事のスタイル: {template['style']}\n"
                base_prompt += f"推奨文字数: {template['length']}\n"
                base_prompt += f"内容の方向性: {template['prompt']}\n"
                
                # テンプレートタイプ別の追加指示
                if template_type == "tech_tutorial":
                    base_prompt += "\n特別な要求: 手順を明確に番号付きで示し、各ステップで期待される結果を説明してください。\n"
                elif template_type == "tech_deep_dive":
                    base_prompt += "\n特別な要求: 技術的な仕組みを図解的に説明し、なぜそうなるのかの理由も含めてください。\n"
                elif template_type == "dev_experience":
                    base_prompt += "\n特別な要求: 遭遇した問題、試行錯誤のプロセス、最終的な解決策を時系列で説明してください。\n"
                elif template_type == "tech_comparison":
                    base_prompt += "\n特別な要求: 比較表や具体的な使用例を含め、どの場面でどれを選ぶべきかの判断基準を示してください。\n"
        
        # 現在の日付を追加
        current_date = datetime.now().strftime('%Y年%m月%d日')
        base_prompt += f"\n今日の日付: {current_date}\n"
        
        # 追加の指示（厳格な要求事項）
        base_prompt += """
重要な注意事項（必ず遵守）:
- 技術的に正確で検証可能な情報のみを含め、不確実な情報は避けてください
- コード例は必ず実際に動作し、読者が実行できるものを豊富に提供してください
- 専門用語は初回使用時に詳細に説明し、理解を深める追加情報も含めてください
- 明確な見出し、段落構成、箇条書きを活用して非常に読みやすい構造にしてください
- 実践的で読者が実際に試し、スキルアップできる詳細な内容を心がけてください
- 背景説明、実装手順、ベストプラクティス、トラブルシューティングを包括的に含めてください
- 指定された文字数範囲を必ず満たし、内容の薄い記事は避けてください
- 必ずタイトルと本文を明確に分けて出力してください
- 最後に読者からの質問やコメント、体験談の共有を促す文章を含めてください
- 読者が「この記事を読んで本当に良かった」と感じる価値の高い内容にしてください
"""
        
        return base_prompt
    
    def _parse_generated_content(self, generated_text: str) -> Tuple[str, str]:
        """生成されたコンテンツからタイトルと本文を分離"""
        try:
            lines = generated_text.strip().split('\n')
            
            title = ""
            content_lines = []
            content_started = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    if content_started:
                        content_lines.append("")
                    continue
                
                # タイトルの検出
                if line.startswith("タイトル:") or line.startswith("# "):
                    title = line.replace("タイトル:", "").replace("# ", "").strip()
                    content_started = True
                elif not content_started and not title:
                    # 最初の非空行をタイトルとして扱う
                    title = line
                    content_started = True
                else:
                    # 本文として追加
                    content_lines.append(line)
            
            content = "\n".join(content_lines).strip()
            
            # タイトルが空の場合、本文の最初の行をタイトルにする
            if not title and content_lines:
                title = content_lines[0]
                content = "\n".join(content_lines[1:]).strip()
            
            return title, content
            
        except Exception as e:
            print(f"❌ コンテンツ解析エラー: {e}")
            return "", ""
    
    def generate_templated_content(self, template_type: str = None) -> Tuple[str, str]:
        """
        テンプレートベースの記事生成
        
        Args:
            template_type: 生成テンプレートのタイプ
            
        Returns:
            Tuple[str, str]: (タイトル, 内容)
        """
        template = self._get_template(template_type)
        if not template:
            template = random.choice(self.generation_templates)
        
        print(f"📝 テンプレート '{template['type']}' で記事生成中...")
        
        # テンプレートベースの内容生成
        current_date = datetime.now()
        date_str = current_date.strftime('%Y年%m月%d日')
        
        # タイトル生成
        title_templates = {
            "daily_reflection": [
                f"今日の振り返り - {date_str}",
                f"日常の小さな気づき - {current_date.strftime('%m/%d')}",
                "今日という一日を大切に"
            ],
            "learning_share": [
                f"最近学んだこと - {date_str}",
                "読書から得た学び",
                "新しい発見をシェア"
            ],
            "experience_story": [
                "新しいチャレンジの記録",
                f"体験談 - {current_date.strftime('%Y.%m.%d')}",
                "一歩踏み出してみた結果"
            ],
            "life_tips": [
                "日常を豊かにする小さなコツ",
                "生活の質を上げるアイデア",
                "実践してよかったこと"
            ]
        }
        
        # 内容生成
        content_templates = {
            "daily_reflection": [
                f"""今日は{current_date.strftime('%m月%d日')}、いつもとは少し違う視点で一日を振り返ってみました。

忙しい毎日の中で、ふと立ち止まって考える時間はとても貴重です。
今日感じたこと、学んだこと、そして明日への想いを整理してみます。

小さなことかもしれませんが、こうした日々の積み重ねが
人生を豊かにしてくれるのだと思います。

皆さんはどんな一日でしたか？
よろしければコメントで教えてください。""",
                
                """朝の静寂の中で、今日という日について考えていました。

毎日が過ぎていく中で、一つ一つの瞬間に意味があることを
改めて感じています。

今日出会った人、交わした言葉、感じた感情。
すべてが今の自分を形作る大切な要素なのですね。

こうして文章に残すことで、日々の価値を再確認できます。

皆さんも今日の出来事を振り返ってみませんか？"""
            ],
            "learning_share": [
                """最近読んだ本から、興味深い考え方を学びました。

「知識は使ってこそ価値がある」という言葉が印象的で、
学んだことを実際に生活に取り入れてみることの大切さを感じています。

読書は新しい視点を与えてくれる素晴らしい習慣ですが、
そこで得た学びを行動に移すことで、本当の成長につながるのですね。

皆さんも最近学んだことがあれば、ぜひ実践してみてください。
きっと新しい発見があるはずです。""",
                
                """今日は新しいスキルについて学ぶ機会がありました。

最初は難しく感じましたが、基本から丁寧に理解していくことで
少しずつコツが掴めてきました。

学習において大切なのは、完璧を求めすぎず、
小さな進歩を積み重ねることだと実感しています。

継続は力なり、という言葉を改めて噛み締めています。

一緒に学び続けていきましょう！"""
            ],
            "experience_story": [
                """今日は以前から気になっていたことに、ついにチャレンジしてみました。

最初は不安もありましたが、実際にやってみると
想像していたよりもずっと楽しく、充実した時間を過ごせました。

「案ずるより産むが易し」とはよく言ったもので、
行動してみることで見えてくる世界があるのですね。

小さな一歩でも、踏み出すことに意味があると感じています。

皆さんも何かチャレンジしてみたいことはありませんか？""",
                
                """新しい環境に飛び込んでみた体験をシェアします。

緊張もありましたが、そこで出会った人々の温かさに
心から感謝しています。

変化を恐れずに行動することで、
新しい自分に出会えることを実感しました。

コンフォートゾーンから一歩出ることの大切さを
身をもって学んだ一日でした。"""
            ],
            "life_tips": [
                """日常生活で実践している小さな工夫をご紹介します。

些細なことですが、毎日の積み重ねで
生活の質が向上することを実感しています。

特に朝の時間の使い方を少し変えるだけで、
一日全体が充実するようになりました。

皆さんも試してみて、自分に合うものを見つけてください。
小さな変化が大きな違いを生むかもしれません。""",
                
                """効率的で心地よい日常を送るためのアイデアをシェアします。

忙しい毎日でも、ちょっとした工夫で
時間と心に余裕を作ることができます。

大切なのは、自分のライフスタイルに合った方法を
見つけることだと思います。

完璧を目指さず、できることから始めてみましょう。
継続できることが一番大切ですね。"""
            ]
        }
        
        # ランダム選択
        titles = title_templates.get(template["type"], title_templates["daily_reflection"])
        contents = content_templates.get(template["type"], content_templates["daily_reflection"])
        
        title = random.choice(titles)
        content = random.choice(contents)
        
        print(f"✅ テンプレート記事生成完了:")
        print(f"   タイプ: {template['type']}")
        print(f"   タイトル: {title}")
        print(f"   内容: {content[:50]}...")
        
        return title, content
    
    def generate_content(self, method: str = "template", **kwargs) -> Tuple[str, str]:
        """
        記事コンテンツ生成のメインメソッド
        
        Args:
            method: 生成方法 ("llm", "template", "auto")
            **kwargs: 各生成方法に応じた追加パラメータ
            
        Returns:
            Tuple[str, str]: (タイトル, 内容)
        """
        print(f"🎯 記事生成方法: {method}")
        
        if method == "llm":
            # LLM生成を試行
            result = self.generate_with_llm(
                topic=kwargs.get("topic"),
                template_type=kwargs.get("template_type")
            )
            if result:
                return result
            else:
                print("🔄 LLM生成に失敗、テンプレート生成にフォールバック")
                method = "template"
        
        if method == "template":
            return self.generate_templated_content(
                template_type=kwargs.get("template_type")
            )
        
        elif method == "auto":
            # 自動選択（将来的にLLMが利用可能な場合は優先）
            if self.llm_config.get("enabled", False):
                return self.generate_content("llm", **kwargs)
            else:
                return self.generate_content("template", **kwargs)
        
        else:
            print(f"⚠️ 不明な生成方法: {method}、テンプレート生成を使用")
            return self.generate_templated_content()
    
    def _get_template(self, template_type: str = None) -> Optional[Dict]:
        """指定されたタイプのテンプレートを取得"""
        if not template_type:
            return None
        
        for template in self.generation_templates:
            if template["type"] == template_type:
                return template
        
        return None
    
    def list_template_types(self) -> List[str]:
        """利用可能なテンプレートタイプ一覧を取得"""
        return [template["type"] for template in self.generation_templates]
    
    def get_template_info(self, template_type: str) -> Dict:
        """テンプレート情報を取得"""
        template = self._get_template(template_type)
        if template:
            return {
                "type": template["type"],
                "style": template["style"],
                "prompt": template["prompt"]
            }
        return {"type": "unknown", "style": "不明", "prompt": "不明"}
    
    def is_llm_available(self) -> bool:
        """LLM機能が利用可能かチェック"""
        return self.llm_config.get("enabled", False)
    
    def configure_llm(self, provider: str, model: str, api_key: str = None, **config) -> bool:
        """
        LLM設定を更新（将来実装予定）
        
        Args:
            provider: LLMプロバイダー (openai, claude, local等)
            model: モデル名
            api_key: APIキー
            **config: その他の設定
            
        Returns:
            bool: 設定成功の可否
        """
        try:
            self.llm_config.update({
                "provider": provider,
                "model": model,
                "api_key": api_key,
                **config
            })
            
            # 将来的に設定ファイルに保存
            print(f"✅ LLM設定を更新しました: {provider}/{model}")
            return True
            
        except Exception as e:
            print(f"❌ LLM設定更新エラー: {e}")
            return False
    
    def format_for_note(self, content: str) -> str:
        """
        note投稿用にフォーマットを調整
        
        Args:
            content: 元の記事内容
            
        Returns:
            str: note用に調整された記事内容
        """
        try:
            # コードブロックの変換（```を削除し、コードを見やすくフォーマット）
            import re
            
            # コードブロックパターンを検出
            code_block_pattern = r'```(\w+)?\n(.*?)\n```'
            
            def replace_code_block(match):
                language = match.group(1) or ""
                code = match.group(2)
                
                # コードブロックを装飾付きテキストに変換
                if language:
                    return f"【{language}コード例】\n{code}\n"
                else:
                    return f"【コード例】\n{code}\n"
            
            # コードブロックを変換
            formatted_content = re.sub(code_block_pattern, replace_code_block, content, flags=re.DOTALL)
            
            # 見出しの変換（## → ■、### → ◆）
            formatted_content = re.sub(r'^## (.+)$', r'■ \1', formatted_content, flags=re.MULTILINE)
            formatted_content = re.sub(r'^### (.+)$', r'◆ \1', formatted_content, flags=re.MULTILINE)
            formatted_content = re.sub(r'^#### (.+)$', r'◇ \1', formatted_content, flags=re.MULTILINE)
            
            # 強調表記の調整（**太字** → 【太字】）
            formatted_content = re.sub(r'\*\*(.+?)\*\*', r'【\1】', formatted_content)
            
            # リストの調整（- を ・ に変更）
            formatted_content = re.sub(r'^- (.+)$', r'・\1', formatted_content, flags=re.MULTILINE)
            
            # 空行の調整（連続する空行を整理）
            formatted_content = re.sub(r'\n\n\n+', '\n\n', formatted_content)
            
            print("✅ note用フォーマット調整が完了しました")
            return formatted_content.strip()
            
        except Exception as e:
            print(f"⚠️ フォーマット調整エラー: {e}")
            return content
    
    def _init_claude_editor(self):
        """Claude編集エージェントの初期化"""
        try:
            # llm_config.jsonからClaude設定を読み込み
            claude_config = self._load_claude_config()
            
            if claude_config and claude_config.get("enabled", False):
                api_key = claude_config.get("api_key")
                if api_key:
                    self.claude_editor = ClaudeEditor(api_key, claude_config)
                    if self.claude_editor.is_available:
                        print("✅ Claude編集エージェントが利用可能です")
                    else:
                        print("⚠️ Claude編集エージェントの初期化に失敗しました")
                else:
                    print("⚠️ Claude APIキーが設定されていません")
            else:
                print("⚠️ Claude編集機能が無効になっています")
        except Exception as e:
            print(f"⚠️ Claude編集エージェント初期化エラー: {e}")
    
    def _load_claude_config(self) -> Dict:
        """Claude設定を読み込み"""
        try:
            import os
            import json
            
            # 設定ファイルのパスを確認
            config_paths = [
                "llm_config.json",
                "../llm_config.json", 
                "../../llm_config.json"
            ]
            
            for config_path in config_paths:
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    
                    claude_config = config_data.get("claude_editor_settings", {})
                    if claude_config:
                        print(f"✅ Claude設定ファイルを読み込みました: {config_path}")
                        return claude_config
            
            print("⚠️ Claude設定が見つかりません")
            return {}
                
        except Exception as e:
            print(f"⚠️ Claude設定読み込みエラー: {e}")
            return {}
    
    def is_claude_available(self) -> bool:
        """Claude編集機能が利用可能かチェック"""
        return self.claude_editor and self.claude_editor.is_available
    
    def improve_with_claude(self, title: str, content: str, improvement_type: str = "comprehensive") -> Optional[Dict]:
        """
        Claudeを使った記事改善
        
        Args:
            title: 記事タイトル
            content: 記事内容
            improvement_type: 改善タイプ ("proofread", "buzz", "title", "comprehensive")
            
        Returns:
            Optional[Dict]: 改善結果
        """
        if not self.is_claude_available():
            print("❌ Claude編集機能が利用できません")
            return None
        
        try:
            if improvement_type == "proofread":
                return self.claude_editor.proofread_article(title, content)
            elif improvement_type == "buzz":
                return self.claude_editor.add_buzz_elements(title, content)
            elif improvement_type == "title":
                return self.claude_editor.improve_title(title, content)
            elif improvement_type == "comprehensive":
                return self.claude_editor.comprehensive_improvement(title, content)
            else:
                print(f"❌ 不明な改善タイプ: {improvement_type}")
                return None
                
        except Exception as e:
            print(f"❌ Claude改善エラー: {e}")
            return None
    
    def _init_openai_editor(self):
        """OpenAI編集エージェントの初期化"""
        try:
            if not OPENAI_EDITOR_AVAILABLE:
                return
                
            # llm_config.jsonからOpenAI編集設定を読み込み
            openai_config = self._load_openai_editor_config()
            
            if openai_config and openai_config.get("enabled", False):
                api_key = openai_config.get("api_key")
                if api_key:
                    self.openai_editor = OpenAIEditor(api_key, openai_config)
                    if self.openai_editor.is_available:
                        print("✅ OpenAI編集エージェントが利用可能です")
                    else:
                        print("⚠️ OpenAI編集エージェントの初期化に失敗しました")
                else:
                    print("⚠️ OpenAI編集用APIキーが設定されていません")
            else:
                print("⚠️ OpenAI編集機能が無効になっています")
        except Exception as e:
            print(f"⚠️ OpenAI編集エージェント初期化エラー: {e}")
    
    def _load_openai_editor_config(self) -> Dict:
        """OpenAI編集設定を読み込み"""
        try:
            import os
            import json
            
            # 設定ファイルのパスを確認
            config_paths = [
                "llm_config.json",
                "../llm_config.json", 
                "../../llm_config.json"
            ]
            
            for config_path in config_paths:
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    
                    openai_config = config_data.get("openai_editor_settings", {})
                    if openai_config:
                        print(f"✅ OpenAI編集設定ファイルを読み込みました: {config_path}")
                        return openai_config
            
            print("⚠️ OpenAI編集設定が見つかりません")
            return {}
                
        except Exception as e:
            print(f"⚠️ OpenAI編集設定読み込みエラー: {e}")
            return {}
    
    def is_openai_editor_available(self) -> bool:
        """OpenAI編集機能が利用可能かチェック"""
        return self.openai_editor and self.openai_editor.is_available
    
    def improve_with_openai(self, title: str, content: str, improvement_type: str = "comprehensive") -> Optional[Dict]:
        """
        OpenAIを使った記事改善（Claudeのフォールバック）
        
        Args:
            title: 記事タイトル
            content: 記事内容
            improvement_type: 改善タイプ ("proofread", "buzz", "title", "comprehensive")
            
        Returns:
            Optional[Dict]: 改善結果
        """
        if not self.is_openai_editor_available():
            print("❌ OpenAI編集機能が利用できません")
            return None
        
        try:
            if improvement_type == "proofread":
                return self.openai_editor.proofread_article(title, content)
            elif improvement_type == "buzz":
                return self.openai_editor.add_buzz_elements(title, content)
            elif improvement_type == "title":
                return self.openai_editor.improve_title(title, content)
            elif improvement_type == "comprehensive":
                return self.openai_editor.comprehensive_improvement(title, content)
            else:
                print(f"❌ 不明な改善タイプ: {improvement_type}")
                return None
                
        except Exception as e:
            print(f"❌ OpenAI改善エラー: {e}")
            return None
    
    def improve_with_fallback(self, title: str, content: str, improvement_type: str = "comprehensive") -> Optional[Dict]:
        """
        フォールバック機能付き記事改善（Claude → OpenAI）
        
        Args:
            title: 記事タイトル
            content: 記事内容
            improvement_type: 改善タイプ ("proofread", "buzz", "title", "comprehensive")
            
        Returns:
            Optional[Dict]: 改善結果
        """
        print("🎯 フォールバック機能付き記事改善を開始...")
        
        # まずClaudeを試す
        if self.is_claude_available():
            print("🤖 Claude編集エージェントで改善を試行中...")
            claude_result = self.improve_with_claude(title, content, improvement_type)
            
            if claude_result and "error" not in claude_result:
                print("✅ Claude編集エージェントで改善完了")
                return claude_result
            else:
                print("⚠️ Claude編集エージェントでエラーが発生、OpenAIにフォールバック...")
        else:
            print("⚠️ Claude編集エージェントが利用不可、OpenAIを使用...")
        
        # Claudeが失敗した場合、OpenAIを試す
        if self.is_openai_editor_available():
            print("🤖 OpenAI編集エージェントで改善を試行中...")
            openai_result = self.improve_with_openai(title, content, improvement_type)
            
            if openai_result and "error" not in openai_result:
                print("✅ OpenAI編集エージェントで改善完了")
                return openai_result
            else:
                print("❌ OpenAI編集エージェントでもエラーが発生")
        else:
            print("❌ OpenAI編集エージェントも利用不可")
        
        print("❌ 全ての編集エージェントが利用できません")
        return None 