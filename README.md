# X自動化ツール

## 概要
複数のXアカウントを効率的に管理・運用するための自動化ツールです。

## 機能
- 複数アカウントの一元管理
- プロキシ設定（IPRoyal対応）
- CSVによる一括インポート
- 暗号化されたパスワード管理
- 対話式CLIインターフェース

## セットアップ

### 1. 必要なライブラリのインストール
```bash
pip install -r requirements.txt
```

### 2. プログラムの起動
```bash
python cli_interface.py
```

## 使い方

### アカウントの追加

#### CSVファイルから一括インポート
1. `config/accounts.csv`にアカウント情報を記載
2. メニューから「3. CSVインポート」を選択

#### CSV形式
```csv
アカウントID,パスワード,プロキシホスト,プロキシポート,プロキシユーザー,プロキシパスワード
user1@example.com,password123,iproyalfast.hellworld.io,12321,username,password
```

### アカウント管理
- メニューから「1. アカウント管理」を選択
- 単一選択、複数選択、範囲指定が可能

## ファイル構造
```
x_automation_tool/
├── config/              # 設定ファイル
│   └── accounts.csv    # アカウント情報
├── cache/              # キャッシュデータ
│   ├── encryption.key  # 暗号化キー
│   └── cookies/        # Cookie保存
├── data/               # データファイル
│   └── account_status.json  # アカウントステータス
├── logs/               # ログファイル
├── account_manager.py  # アカウント管理モジュール
├── cli_interface.py    # CLIインターフェース
├── requirements.txt    # 依存ライブラリ
└── README.md          # このファイル
```

## セキュリティ
- パスワードは暗号化して保存
- 暗号化キーは`cache/encryption.key`に保存
- Cookieも暗号化保存（今後実装）

## 注意事項
- 利用規約を遵守してご使用ください
- プロキシ設定は必須です
- 初回ログイン機能は今後実装予定
