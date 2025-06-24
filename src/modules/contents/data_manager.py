#!/usr/bin/env python3
"""
データ管理モジュール
記事データの読み込み、管理、選択機能
"""

import json
import os
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class DataManager:
    def __init__(self, data_file_path: str = "data/articles.json"):
        """
        データマネージャーの初期化
        
        Args:
            data_file_path: 記事データファイルのパス
        """
        self.data_file_path = data_file_path
        self.articles_data = None
        self.load_articles()
    
    def load_articles(self) -> bool:
        """
        記事データをJSONファイルから読み込み
        
        Returns:
            bool: 読み込み成功の可否
        """
        try:
            if not os.path.exists(self.data_file_path):
                print(f"❌ 記事データファイルが見つかりません: {self.data_file_path}")
                return False
            
            with open(self.data_file_path, 'r', encoding='utf-8') as f:
                self.articles_data = json.load(f)
            
            print(f"✅ 記事データを読み込みました: {len(self.articles_data['articles'])}件")
            return True
            
        except Exception as e:
            print(f"❌ 記事データの読み込みエラー: {e}")
            return False
    
    def get_active_articles(self) -> List[Dict]:
        """
        アクティブな記事一覧を取得
        
        Returns:
            List[Dict]: アクティブな記事のリスト
        """
        if not self.articles_data:
            return []
        
        return [article for article in self.articles_data['articles'] 
                if article.get('status', 'active') == 'active']
    
    def get_random_article(self) -> Optional[Dict]:
        """
        ランダムに記事を選択
        
        Returns:
            Optional[Dict]: 選択された記事データ、または None
        """
        active_articles = self.get_active_articles()
        
        if not active_articles:
            print("❌ 利用可能な記事がありません")
            return None
        
        selected_article = random.choice(active_articles)
        print(f"📝 記事を選択しました: ID {selected_article['id']} - {selected_article['title']}")
        
        return selected_article
    
    def get_article_by_id(self, article_id: int) -> Optional[Dict]:
        """
        IDで記事を取得
        
        Args:
            article_id: 記事ID
            
        Returns:
            Optional[Dict]: 記事データ、または None
        """
        active_articles = self.get_active_articles()
        
        for article in active_articles:
            if article['id'] == article_id:
                return article
        
        print(f"❌ ID {article_id} の記事が見つかりません")
        return None
    
    def format_article_content(self, article: Dict) -> Tuple[str, str]:
        """
        記事内容をフォーマット（日付置換など）
        
        Args:
            article: 記事データ
            
        Returns:
            Tuple[str, str]: (フォーマット済みタイトル, フォーマット済み本文)
        """
        if not article:
            return "", ""
        
        # 日付フォーマットを取得
        date_format = self.articles_data.get('settings', {}).get('date_format', '%Y年%m月%d日')
        current_date = datetime.now().strftime(date_format)
        
        # タイトルの日付置換
        title = article['title'].replace('{date}', current_date)
        
        # 本文の日付置換と改行処理
        content = article['content'].replace('{date}', current_date)
        
        return title, content
    
    def list_articles(self) -> None:
        """
        利用可能な記事一覧を表示
        """
        active_articles = self.get_active_articles()
        
        if not active_articles:
            print("❌ 利用可能な記事がありません")
            return
        
        print("\n📚 利用可能な記事一覧:")
        print("=" * 60)
        
        for article in active_articles:
            title, _ = self.format_article_content(article)
            print(f"ID: {article['id']:2d} | {title}")
            print(f"        カテゴリ: {article.get('category', '未分類')}")
            print(f"        タグ: {', '.join(article.get('tags', []))}")
            print("-" * 60)
    
    def add_article(self, title: str, content: str, category: str = "", tags: List[str] = None) -> bool:
        """
        新しい記事を追加
        
        Args:
            title: 記事タイトル
            content: 記事本文
            category: カテゴリ
            tags: タグリスト
            
        Returns:
            bool: 追加成功の可否
        """
        try:
            if not self.articles_data:
                return False
            
            # 新しいIDを生成
            existing_ids = [article['id'] for article in self.articles_data['articles']]
            new_id = max(existing_ids) + 1 if existing_ids else 1
            
            # デフォルト値設定
            if not category:
                category = self.articles_data.get('settings', {}).get('default_category', '日常')
            
            if tags is None:
                tags = []
            
            # 新しい記事データ
            new_article = {
                "id": new_id,
                "title": title,
                "content": content,
                "tags": tags,
                "category": category,
                "created_at": datetime.now().strftime('%Y-%m-%d'),
                "status": "active"
            }
            
            # 記事を追加
            self.articles_data['articles'].append(new_article)
            
            # ファイルに保存
            self.save_articles()
            
            print(f"✅ 新しい記事を追加しました: ID {new_id} - {title}")
            return True
            
        except Exception as e:
            print(f"❌ 記事追加エラー: {e}")
            return False
    
    def save_articles(self) -> bool:
        """
        記事データをファイルに保存
        
        Returns:
            bool: 保存成功の可否
        """
        try:
            with open(self.data_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.articles_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ 記事データの保存エラー: {e}")
            return False
    
    def get_settings(self) -> Dict:
        """
        設定情報を取得
        
        Returns:
            Dict: 設定情報
        """
        if not self.articles_data:
            return {}
        
        return self.articles_data.get('settings', {}) 