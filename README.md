# X自動化ツール v2.0

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

### 3. セキュリティ対策
- **Cloudflare対策**
  - 手動解除待機機能（最大5分）
  - 解除後の自動処理継続
  - 明確な解除指示の表示
- **セッション管理**
  - セッション切れの自動検出
  - 自動再ログイン機能
  - ログイン状態の確実な検証（URL判定方式）

### 4. 自動操作機能
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
git clone [repository-url]
cd x_automation_tool

# 依存関係のインストール
pip install -r requirements.txt

必要なライブラリ

undetected-chromedriver
selenium
pyotp（二段階認証用）
その他requirements.txt参照

初期設定
1. アカウント情報の準備
config/accounts.csvを作成：
2. リプライテキストの設定（オプション）
config/reply_texts.csvを作成：
csvリプライテキスト
素晴らしい投稿ですね！
参考になりました
ありがとうございます
使用方法
1. メインメニューの起動
bashpython cli_automation.py
2. 初回ログイン（プロファイル作成）
メニュー「2. 初回ログイン（プロファイル作成）」
→ 特定番号選択 or 範囲指定 or 全アカウント
3. 自動操作の実行
メニュー「8. 自動操作実行（プロファイル版）」
→ アカウント選択
→ 対象URL入力
→ 操作選択（いいね/ブックマーク/リツイート/リプライ）
4. プロキシテスト
メニュー「4. プロキシテスト」
→ アカウント選択でプロキシ接続確認
ファイル構成
x_automation_tool/
├── config/                      # 設定ファイル
│   ├── accounts.csv            # アカウント情報
│   ├── accounts_add.csv        # 追加アカウント用
│   └── reply_texts.csv         # リプライテキスト
├── data/                        # データファイル
│   ├── account_status.json     # アカウントステータス
│   └── profile_index.json      # プロファイルインデックス
├── profiles/                    # Chromeプロファイル保存
├── temp_profiles/               # 一時プロファイル
├── cache/                       # Cookieキャッシュ
├── logs/                        # 実行ログ
├── backup_test_files_20250908/ # バックアップ
│
├── cli_automation.py            # メインプログラム
├── automation_executor.py       # 自動操作エンジン
├── login_manager.py            # ログイン管理
├── profile_manager.py          # プロファイル管理
├── account_manager.py          # アカウント管理
├── cloudflare_handler.py       # Cloudflare対策
├── cli_interface.py            # CLI表示管理
├── proxy_tester.py             # プロキシテスター
├── totp_handler.py             # 二段階認証処理
├── requirements.txt            # 依存関係
├── README.md                   # このファイル
└── .gitignore                  # Git除外設定
トラブルシューティング
Cloudflareが表示される場合

画面の指示に従って手動で解除
「私は人間です」のチェックボックスをクリック
最大5分待機後、自動的に処理継続

セッションが切れた場合

システムが自動的に検出し再ログイン
二段階認証も自動処理（secret_key設定時）

ログイン判定の仕組み

https://x.com/homeにアクセス
URLのリダイレクトを確認

ログイン済み: /homeのまま
未ログイン: /flow/loginにリダイレクト


未ログインの場合は自動ログイン実行

エラー対処法

ドライバー作成失敗: Chromeプロセスを終了して再実行
プロファイルロック: ロックファイルを自動削除して再試行
タイムアウト: ネットワーク接続とプロキシを確認

セキュリティ注意事項

アカウント情報は暗号化されていません
config/accounts.csvは絶対にGitにコミットしない
プロキシの品質が動作に大きく影響します
定期的なプロファイルのバックアップを推奨

制限事項

X利用規約を遵守してください
過度な自動操作はアカウント制限の原因となります
1アカウントあたり適切な待機時間を設定してください

更新履歴

v2.0.0 (2024-09-10): Cloudflare手動解除、セッション切れ自動再ログイン実装
v1.9.0: プロファイルベース管理、並列実行対応
v1.8.0: 二段階認証自動化
v1.0.0: 初回リリース

ライセンス
MIT License
サポート
Issues: [GitHub Issues URL]