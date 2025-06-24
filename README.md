# 📝 note自動投稿システム

AIを活用したnote記事の自動生成・校閲・投稿システムです。OpenAI GPT-4oとClaude 3.5 Sonnetを使用して、高品質な技術記事を自動生成し、noteプラットフォームに投稿します。

## 🌟 主な機能

### 🤖 AI記事生成
- **OpenAI GPT-4o**による高品質な記事生成
- 複数のテンプレート対応（技術チュートリアル、解説記事など）
- カスタマイズ可能な記事構成

### 🎨 AI校閲・改善システム
- **Claude 3.5 Sonnet** + **OpenAI GPT-4o**のフォールバック機能
- 4つの改善タイプ：
  - 📖 **校閲機能**: 文章の読みやすさ・流れ改善、誤字脱字修正
  - ⚡ **バズ要素追加**: 具体的データ・体験談・最新トレンド情報の追加
  - 🎯 **タイトル改善**: SEO効果とクリック魅力を高めるタイトル生成
  - 🚀 **包括的改善**: 上記すべてを統合した総合改善

### 📱 note最適化
- **note用フォーマット自動調整**
- Markdownからnote形式への変換
- 見出し・強調・コードブロックの最適化

### 🔄 自動投稿
- Selenium WebDriverによる自動ログイン・投稿
- エラーハンドリング・リトライ機能
- 投稿状況の詳細ログ

## 🚀 クイックスタート

### 1. 環境セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/Shintaisei/-.git
cd note自動投稿

# 仮想環境作成・有効化
python -m venv venv
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate     # Windows

# 依存関係インストール
pip install -r requirements.txt
```

### 2. 設定ファイル作成

```bash
# 設定ファイルをコピー
cp llm_config_sample.json llm_config.json
cp note_login_config_sample.json note_login_config.json
```

### 3. APIキー設定

`llm_config.json`を編集してAPIキーを設定：

```json
{
  "openai_settings": {
    "api_key": "sk-your-openai-api-key"
  },
  "claude_editor_settings": {
    "api_key": "sk-ant-your-claude-api-key"
  }
}
```

`note_login_config.json`を編集してnoteログイン情報を設定：

```json
{
  "email": "your_note_email@example.com",
  "password": "your_note_password"
}
```

### 4. 実行

```bash
# メインシステム起動
cd src
python note_complete_auto_refactored.py
```

## 📋 使用方法

### インタラクティブモード

メインシステムを起動すると、以下のオプションが表示されます：

1. **📊 設定確認** - 現在の設定とAPI接続状況を確認
2. **📝 LLM記事生成で投稿** - AI記事生成→校閲→投稿
3. **📄 特定の記事で投稿** - 既存記事の校閲・投稿
4. **❌ 終了**

### ワンクリック実行（macOS）

デスクトップに配置されたファイルをダブルクリック：

- `note_quick_post.command` - オプション選択付き実行
- `note_full_auto.command` - 完全自動実行

## 🛠️ システム構成

```
note自動投稿/
├── src/                          # ソースコード
│   ├── modules/
│   │   ├── contents/            # コンテンツ生成・管理
│   │   │   ├── content_generator.py    # AI記事生成
│   │   │   ├── claude_editor.py        # Claude校閲エージェント
│   │   │   ├── openai_editor.py        # OpenAI校閲エージェント
│   │   │   └── data_manager.py         # データ管理
│   │   ├── post/                # 投稿機能
│   │   │   ├── driver_manager.py       # WebDriver管理
│   │   │   ├── note_login.py           # noteログイン
│   │   │   └── note_poster.py          # 記事投稿
│   │   └── config_manager.py    # 設定管理
│   └── note_complete_auto_refactored.py # メインシステム
├── data/                        # データファイル
│   ├── article_templates.txt    # 記事テンプレート
│   └── articles/               # 生成記事保存
├── requirements.txt            # Python依存関係
├── llm_config_sample.json     # LLM設定サンプル
├── note_login_config_sample.json # note設定サンプル
└── README.md                  # このファイル
```

## 🔧 高度な機能

### フォールバック校閲システム

Claude APIが利用できない場合、自動的にOpenAI GPT-4oにフォールバック：

```python
# Claude → OpenAI 自動フォールバック
result = content_generator.improve_with_fallback(
    title, content, 'comprehensive'
)
```

### カスタムテンプレート

`data/article_templates.txt`でテンプレートをカスタマイズ可能：

```
[tech_tutorial]
title_template: {技術名}の実装ガイド：{期間}で習得する{レベル}向け解説
content_template: ## 概要\n{技術概要}\n\n## 実装手順\n{実装内容}...
```

### バッチ処理

複数記事の一括生成・投稿：

```python
# 完全自動バッチ実行
python full_auto_post.py
```

## 🧪 テスト・デバッグ

### 機能テスト

```bash
# フォールバック機能テスト
python test_fallback_system.py

# note フォーマット調整テスト
python test_note_format.py

# Claude編集機能テスト
python test_claude_editor.py
```

### デモモード

投稿を行わない安全なデモ実行：

```bash
# デモ実行（投稿なし）
./auto_demo.zsh
```

## 📦 依存関係

### Python パッケージ

- `openai>=1.0.0` - OpenAI API
- `anthropic>=0.18.0` - Claude API
- `langchain>=0.1.0` - LangChain フレームワーク
- `langchain-anthropic>=0.1.0` - Claude統合
- `selenium>=4.20.0` - Web自動化
- `requests>=2.32.0` - HTTP通信

### システム要件

- Python 3.9+
- Chrome/Chromium ブラウザ
- macOS/Linux/Windows対応

## 🔒 セキュリティ

### 機密情報の管理

- APIキーは`.gitignore`で除外
- 設定ファイルはローカルのみ保存
- サンプルファイルで安全な共有

### WebDriver セキュリティ

- ヘッドレスモード対応
- User-Agent偽装
- レート制限対応

## 🤝 コントリビューション

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 🆘 トラブルシューティング

### よくある問題

**Q: Claude APIエラーが発生する**
A: APIクレジットを確認し、フォールバック機能でOpenAIを使用してください。

**Q: note投稿に失敗する**
A: ログイン情報を確認し、2段階認証が無効になっていることを確認してください。

**Q: WebDriverエラー**
A: Chromeブラウザが最新版であることを確認してください。

### サポート

問題が発生した場合は、[GitHub Issues](https://github.com/Shintaisei/-/issues)で報告してください。

## 🎯 今後の予定

- [ ] GUI インターフェース
- [ ] スケジュール投稿機能
- [ ] 他プラットフォーム対応（Qiita、Zenn等）
- [ ] 画像自動生成・挿入
- [ ] アナリティクス機能

---

**⚡ AI × 自動化で、コンテンツ制作を次のレベルへ！** 