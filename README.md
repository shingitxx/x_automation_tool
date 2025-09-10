# X自動化ツール v2.1

## 概要
X（旧Twitter）の自動操作を行うPythonツール。Chromeプロファイルベースの管理により、複数アカウントの安定した並列運用を実現。

## 主要機能

### 1. アカウント管理
- CSV形式での一括アカウント管理
- プロキシ認証対応（ユーザー名/パスワード認証）
- 二段階認証（TOTP）の自動化
- アカウントステータスの追跡と管理

### 2. プロファイル管理
- Chromeプロファイルによるセッション永続化
- Cookie保存によるログイン状態の維持
- プロファイル単位での独立したブラウザ環境
- プロファイルのロック管理と自動クリーンアップ

### 3. Cloudflare対策（v2.1で強化）
- **手動解除待機機能**
  - Enterキー待機方式で確実な解除確認
  - 初回ログイン時の対応
  - プロファイル起動時の対応
  - 明確な解除指示の表示
- **自動検出タイミング**
  - ログインページアクセス時
  - ホームページアクセス時
  - 各操作実行前

### 4. セッション管理
- セッション切れの自動検出
- 自動再ログイン機能
- ログイン状態の確実な検証（URL判定方式）
- 二段階認証の自動処理

### 5. 自動操作機能
- いいね、ブックマーク、リツイート、リプライ
- 操作後の状態変化検証（誤判定防止）
- ランダム待機時間による人間的な動作
- 並列/逐次実行の選択可能（最大同時実行数設定可）

## システム要件
- Windows 10/11
- Python 3.10以上
- Chrome 139以上
- 8GB以上のRAM推奨

## インストール

```bash
# リポジトリのクローン
git clone https://github.com/shingitxx/x_automation_tool.git
cd x_automation_tool

# ブランチ切り替え
git checkout feature/clean-automation

# 依存関係のインストール
pip install -r requirements.txt
初期設定
1. アカウント情報の準備
config/accounts.csvを作成：
csvemail,password,proxy_url,secret_key
user1@example.com,password123,http://user:pass@proxy.com:8080,TOTP_SECRET_KEY
2. リプライテキストの設定（オプション）
config/reply_texts.csvを作成：
csvリプライテキスト
素晴らしい投稿ですね！
参考になりました
使用方法
1. メインメニューの起動
bashpython cli_automation.py
2. 初回ログイン（プロファイル作成）

メニュー「2. 初回ログイン（プロファイル作成）」
Cloudflareが表示された場合は手動で解除
Enterキーで処理継続

3. 自動操作の実行

メニュー「8. 自動操作実行（プロファイル版）」
プロファイル起動時にCloudflareが出ても自動対応

Cloudflare対応フロー
初回ログイン時

ログインページでCloudflare検出
「Cloudflareが検出されました」メッセージ表示
手動で解除
Enterキー押下で継続

プロファイル使用時

プロファイル起動時に自動検出
必要に応じて手動解除待機
解除後、自動操作継続

トラブルシューティング
Cloudflareが表示される場合

ターミナルに指示が表示されるまで待つ
ブラウザで「私は人間です」をクリック
認証完了を確認
Enterキーを押して継続

ログイン失敗する場合

プロファイルを削除して再作成
プロキシの接続を確認
二段階認証のシークレットキーを確認

ファイル構成
x_automation_tool/
├── config/                      # 設定ファイル
├── data/                        # データファイル
├── profiles/                    # Chromeプロファイル
├── logs/                        # 実行ログ
├── cli_automation.py            # メインプログラム
├── automation_executor.py       # 自動操作エンジン
├── login_manager.py            # ログイン管理
├── profile_manager.py          # プロファイル管理
├── cloudflare_handler.py       # Cloudflare対策
└── README.md                   # このファイル
更新履歴

v2.1.0 (2024-09-10): プロファイル起動時のCloudflare対策、手動解除待機改善
v2.0.0 (2024-09-10): Cloudflare手動解除、セッション切れ自動再ログイン実装
v1.0.0: 初回リリース

ライセンス
MIT License

## 引き継ぎテンプレート

```markdown
# X自動化ツール開発の継続

## プロジェクト情報
- GitHub: https://github.com/shingitxx/x_automation_tool
- ブランチ: feature/clean-automation
- 最終更新: 2024-09-10 夜
- 動作環境: Windows 11, Python 3.10, Chrome 139

## 本日の実装内容（2024-09-10）
✅ 完了：
1. Cloudflare手動解除をEnterキー待機方式に変更
2. 初回ログイン時のCloudflare対応実装
3. プロファイル起動時のCloudflare検出機能追加
4. _execute_tasksメソッドの最初でCloudflareチェック

## 重要な変更ファイル
- cloudflare_handler.py: input()待機方式に変更
- login_manager.py: _perform_login_with_profileにCloudflare対応追加  
- automation_executor.py: _execute_tasksの最初にCloudflareチェック追加

## 動作確認状況
- 初回ログイン: Cloudflare手動解除OK
- プロファイル起動: Cloudflare検出OK
- 自動操作: 正常動作確認済み

## 次回の課題
- 特になし（現時点で正常動作）

## 質問/依頼
[具体的な内容を記載]