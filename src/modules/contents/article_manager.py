#!/usr/bin/env python3
"""
記事管理モジュール
既存記事データの管理と選択
データファイルからの記事取得とフォールバック機能
"""

import random
from datetime import datetime
from .data_manager import DataManager

class ArticleManager:
    def __init__(self, data_manager: DataManager = None):
        """
        記事生成器の初期化
        
        Args:
            data_manager: データマネージャーインスタンス
        """
        self.data_manager = data_manager or DataManager()
        self.selected_article = None  # 特定記事投稿用

    def generate_article_content(self):
        """
        記事内容を自動生成
        
        特定記事が設定されている場合はそれを使用、
        そうでなければデータファイルから記事を選択、フォールバック機能付き
        
        Returns:
            tuple: (タイトル, 内容)
        """
        # 特定記事が設定されている場合はそれを使用
        if self.selected_article:
            title, content = self.data_manager.format_article_content(self.selected_article)
            print(f"📝 指定された記事を使用します:")
            print(f"   タイトル: {title}")
            print(f"   内容: {content[:50]}...")
            # 使用後はリセット
            self.selected_article = None
            return title, content
        
        # データファイルから記事を取得を試行
        try:
            article = self.data_manager.get_random_article()
            if article:
                title, content = self.data_manager.format_article_content(article)
                print(f"📝 データファイルから記事を生成しました:")
                print(f"   タイトル: {title}")
                print(f"   内容: {content[:50]}...")
                return title, content
        except Exception as e:
            print(f"⚠️ データファイルからの記事取得エラー: {e}")
        
        # フォールバック: 元のコードの記事生成ロジック
        print("📝 フォールバック記事生成を使用します...")
        return self._generate_fallback_content()

    def _generate_fallback_content(self):
        """フォールバック用の記事生成（元のコードを完全再現）"""
        titles = [
            f"今日の気づき - {datetime.now().strftime('%Y年%m月%d日')}",
            f"日常の小さな発見 - {datetime.now().strftime('%m/%d')}",
            f"学びのメモ - {datetime.now().strftime('%Y.%m.%d')}",
            "最近考えていること",
            "今日の振り返り",
            "小さな成長の記録"
        ]
        
        contents = [
            """今日はいつもより少し早起きして、朝の静けさを味わいました。

忙しい毎日の中で、こうした静かな時間がとても貴重に感じられます。
朝の空気は澄んでいて、一日の始まりに心が整う感覚がありました。

小さなことですが、こういう瞬間を大切にしたいと思います。

皆さんはどんな時間を大切にしていますか？
コメントで教えてください。""",

            """最近読んだ本から学んだことをシェアします。

「小さな習慣の積み重ねが大きな変化を生む」という言葉が印象に残りました。
確かに、毎日のちょっとした行動が、長期的には大きな違いを作るのだと実感します。

今日から始められる小さな習慣を一つ決めて、続けてみようと思います。

読書は本当に素晴らしい学びの機会ですね。
おすすめの本があれば、ぜひ教えてください！""",

            """今日は新しいことにチャレンジしてみました。

最初は不安もありましたが、やってみると意外と楽しくて、
「やらずに後悔するより、やって学ぶ方がいい」と改めて思いました。

失敗を恐れずに、小さなステップから始めることの大切さを実感しています。

みなさんも最近新しく始めたことはありますか？
体験談があれば聞かせてください。"""
        ]
        
        title = random.choice(titles)
        content = random.choice(contents)
        
        print(f"📝 フォールバック記事を生成しました:")
        print(f"   タイトル: {title}")
        print(f"   内容: {content[:50]}...")
        
        return title, content
    
    def get_article_by_id(self, article_id: int):
        """
        IDで記事を取得
        
        Args:
            article_id: 記事ID
            
        Returns:
            tuple: (タイトル, 内容) または None
        """
        try:
            article = self.data_manager.get_article_by_id(article_id)
            if article:
                return self.data_manager.format_article_content(article)
            return None
        except Exception as e:
            print(f"❌ 記事取得エラー: {e}")
            return None
    
    def list_available_articles(self):
        """利用可能な記事一覧を表示"""
        try:
            self.data_manager.list_articles()
        except Exception as e:
            print(f"❌ 記事一覧表示エラー: {e}")

    def generate_article(self):
        """完全な記事（タイトル + 内容）を生成"""
        title, content = self.generate_article_content()
        
        article_info = {
            "title": title,
            "content": content,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return article_info 