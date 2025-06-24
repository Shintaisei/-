#!/usr/bin/env python3
"""
OpenAI記事編集エージェント
OpenAI APIを使用して記事の校閲・改善を行う（Claudeのフォールバック）
"""

import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAIライブラリがインストールされていません")

class OpenAIEditor:
    """OpenAI APIを使った記事編集エージェント"""
    
    def __init__(self, api_key: str = None, config: Dict = None):
        """
        OpenAI編集エージェントの初期化
        
        Args:
            api_key: OpenAI APIキー
            config: OpenAI設定辞書
        """
        self.config = config or {}
        self.api_key = api_key or self.config.get("api_key")
        self.client = None
        self.is_available = False
        
        if not OPENAI_AVAILABLE:
            print("❌ OpenAIライブラリが不足しています")
            return
            
        if not self.api_key:
            print("❌ OpenAI APIキーが設定されていません")
            return
            
        try:
            # 設定から値を取得（デフォルト値付き）
            self.model = self.config.get("model", "gpt-4o")
            self.temperature = self.config.get("temperature", 0.7)
            self.max_tokens = self.config.get("max_tokens", 3500)
            
            # OpenAI クライアントの初期化
            self.client = openai.OpenAI(api_key=self.api_key)
            self.is_available = True
            print("✅ OpenAI編集エージェントが初期化されました")
            print(f"🤖 設定: {self.model}, temp={self.temperature}, tokens={self.max_tokens}")
        except Exception as e:
            print(f"❌ OpenAI編集エージェントの初期化に失敗: {e}")
    
    def proofread_article(self, title: str, content: str) -> Dict[str, str]:
        """
        記事の校閲を行う
        
        Args:
            title: 記事タイトル
            content: 記事内容
            
        Returns:
            Dict[str, str]: 校閲結果
        """
        if not self.is_available:
            return {"error": "OpenAI編集エージェントが利用できません"}
        
        try:
            print("📝 OpenAI GPT で記事校閲中...")
            
            # 校閲用プロンプト
            system_prompt = """あなたは経験豊富な技術系編集者です。以下の技術記事を校閲してください。

校閲の観点：
1. 文章の読みやすさと流れ
2. 技術的な正確性
3. 誤字脱字・文法チェック
4. 論理構成の改善
5. 専門用語の適切な説明
6. 読者にとっての分かりやすさ

改善点があれば具体的に修正し、改善された記事全文を返してください。
大幅な構成変更は避け、元の内容の意図を保ちながら品質を向上させてください。"""
            
            user_prompt = f"タイトル: {title}\n\n記事内容:\n{content}"
            
            # API呼び出し
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            proofread_content = response.choices[0].message.content
            
            print("✅ 校閲完了")
            return {
                "original_content": content,
                "proofread_content": proofread_content,
                "status": "success"
            }
            
        except Exception as e:
            print(f"❌ 校閲エラー: {e}")
            return {"error": str(e)}
    
    def add_buzz_elements(self, title: str, content: str) -> Dict[str, str]:
        """
        記事にバズ要素を追加する
        
        Args:
            title: 記事タイトル
            content: 記事内容
            
        Returns:
            Dict[str, str]: バズ要素追加結果
        """
        if not self.is_available:
            return {"error": "OpenAI編集エージェントが利用できません"}
        
        try:
            print("🚀 OpenAI GPT でバズ要素追加中...")
            
            # バズ要素追加プロンプト
            system_prompt = """あなたは人気技術ブログのコンテンツマーケターです。以下の技術記事にバズ要素を追加してください。

バズ要素の追加方針：
1. 読者の興味を引く具体的な数値やデータ
2. 「知らないと損する」「意外と知られていない」などの好奇心を刺激する表現
3. 実際の開発現場での体験談や失敗談
4. 最新トレンドとの関連性
5. 読者が「シェアしたくなる」ような驚きの事実
6. 具体的なメリット・デメリットの明示
7. 他の開発者との差別化ポイント

注意点：
- 技術的な正確性は保つ
- 過度に煽らない
- 元の記事の品質を損なわない
- 自然な文章の流れを保つ

改善された記事全文を返してください。"""
            
            user_prompt = f"タイトル: {title}\n\n記事内容:\n{content}"
            
            # API呼び出し
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            buzz_content = response.choices[0].message.content
            
            print("✅ バズ要素追加完了")
            return {
                "original_content": content,
                "buzz_content": buzz_content,
                "status": "success"
            }
            
        except Exception as e:
            print(f"❌ バズ要素追加エラー: {e}")
            return {"error": str(e)}
    
    def improve_title(self, title: str, content: str) -> Dict[str, List[str]]:
        """
        タイトルの改善案を生成する
        
        Args:
            title: 現在のタイトル
            content: 記事内容
            
        Returns:
            Dict[str, List[str]]: タイトル改善案
        """
        if not self.is_available:
            return {"error": "OpenAI編集エージェントが利用できません"}
        
        try:
            print("💡 OpenAI GPT でタイトル改善案生成中...")
            
            # タイトル改善プロンプト
            system_prompt = """あなたは技術ブログのタイトル専門家です。以下の記事に対して、より魅力的で効果的なタイトルを5つ提案してください。

タイトル改善の観点：
1. SEO効果の高いキーワードを含む
2. 読者の興味を引く具体性
3. クリックしたくなる魅力
4. 技術レベルの明示（初心者向け、実践的など）
5. 数値や期間の明示（「3分で理解」「5つの方法」など）
6. 問題解決への期待感
7. 最新性やトレンド感

各タイトル案の後に、そのタイトルの狙いと効果を1行で説明してください。

形式：
1. [タイトル案] - [狙いと効果の説明]
2. [タイトル案] - [狙いと効果の説明]
...

元のタイトル: {title}"""
            
            # 記事内容の要約（最初の500文字）
            content_summary = content[:500] + "..." if len(content) > 500 else content
            user_prompt = f"記事内容の概要:\n{content_summary}"
            
            # API呼び出し
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            title_suggestions_raw = response.choices[0].message.content
            
            # 結果をパース
            suggestions = []
            for line in title_suggestions_raw.split('\n'):
                if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith('-')):
                    suggestions.append(line.strip())
            
            print("✅ タイトル改善案生成完了")
            return {
                "original_title": title,
                "suggestions": suggestions,
                "raw_response": title_suggestions_raw,
                "status": "success"
            }
            
        except Exception as e:
            print(f"❌ タイトル改善エラー: {e}")
            return {"error": str(e)}
    
    def comprehensive_improvement(self, title: str, content: str) -> Dict[str, any]:
        """
        記事の包括的改善（校閲 + バズ要素 + タイトル改善）
        
        Args:
            title: 記事タイトル
            content: 記事内容
            
        Returns:
            Dict[str, any]: 包括的改善結果
        """
        if not self.is_available:
            return {"error": "OpenAI編集エージェントが利用できません"}
        
        print("🎯 OpenAI GPT で記事の包括的改善を開始...")
        
        results = {
            "original_title": title,
            "original_content": content,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "editor": "OpenAI GPT"
        }
        
        # 1. 校閲
        print("\n📝 ステップ1: 記事校閲")
        proofreading_result = self.proofread_article(title, content)
        if "error" not in proofreading_result:
            results["proofread_content"] = proofreading_result["proofread_content"]
            improved_content = proofreading_result["proofread_content"]
        else:
            results["proofread_error"] = proofreading_result["error"]
            improved_content = content
        
        # 2. バズ要素追加
        print("\n🚀 ステップ2: バズ要素追加")
        buzz_result = self.add_buzz_elements(title, improved_content)
        if "error" not in buzz_result:
            results["buzz_content"] = buzz_result["buzz_content"]
            final_content = buzz_result["buzz_content"]
        else:
            results["buzz_error"] = buzz_result["error"]
            final_content = improved_content
        
        # 3. タイトル改善
        print("\n💡 ステップ3: タイトル改善")
        title_result = self.improve_title(title, final_content)
        if "error" not in title_result:
            results["title_suggestions"] = title_result["suggestions"]
        else:
            results["title_error"] = title_result["error"]
        
        results["final_content"] = final_content
        results["improvement_completed"] = True
        
        print("\n✅ 包括的改善完了！")
        return results
    
    def get_improvement_summary(self, improvement_result: Dict) -> str:
        """
        改善結果のサマリーを生成
        
        Args:
            improvement_result: comprehensive_improvementの結果
            
        Returns:
            str: 改善サマリー
        """
        if not improvement_result.get("improvement_completed"):
            return "改善処理が完了していません"
        
        summary_lines = []
        editor = improvement_result.get("editor", "OpenAI GPT")
        summary_lines.append(f"=== {editor}記事改善サマリー ===")
        summary_lines.append(f"改善日時: {improvement_result.get('timestamp', 'N/A')}")
        summary_lines.append(f"元タイトル: {improvement_result.get('original_title', 'N/A')}")
        
        # 文字数比較
        original_length = len(improvement_result.get('original_content', ''))
        final_length = len(improvement_result.get('final_content', ''))
        summary_lines.append(f"文字数変化: {original_length}文字 → {final_length}文字 ({final_length - original_length:+d}文字)")
        
        # 実行された処理
        processes = []
        if "proofread_content" in improvement_result:
            processes.append("✅ 校閲")
        if "buzz_content" in improvement_result:
            processes.append("✅ バズ要素追加")
        if "title_suggestions" in improvement_result:
            processes.append("✅ タイトル改善案生成")
        
        summary_lines.append(f"実行処理: {', '.join(processes)}")
        
        # タイトル提案数
        if "title_suggestions" in improvement_result:
            title_count = len(improvement_result["title_suggestions"])
            summary_lines.append(f"タイトル改善案: {title_count}件")
        
        return "\n".join(summary_lines) 