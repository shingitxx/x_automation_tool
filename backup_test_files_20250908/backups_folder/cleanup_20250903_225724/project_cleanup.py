#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
プロジェクト整理 - 不要ファイル削除
"""

import os
import shutil
from datetime import datetime

print("=" * 60)
print(" プロジェクト整理・不要ファイル削除")
print("=" * 60)

# 現在のファイル一覧を確認
print("現在のファイル構成:")
for item in os.listdir("."):
    if os.path.isfile(item):
        size = os.path.getsize(item)
        print(f"  {item:<30} ({size:,} bytes)")

# 削除対象ファイル（修正・テスト用スクリプト）
cleanup_files = [
    # 今回作成した修正用ファイル
    "add_concurrent_selection.py",
    "complete_restore.py",
    "create_complete_system.py",
    "fix_import_error.py",
    # 以前の修正用ファイル（残っていれば）
    "project_cleanup.py",  # 自分自身も削除対象
    "rebuild_cli_interface.py",
    "rebuild_login_manager.py",
    "debug_auto_login.py",
    "fix_button_detection.py",
    "remove_auto_login.py",
    "simple_form_auto_input.py",
    "fix_indentation_error.py",
    "fix_string_literal.py",
    "fix_syntax_error.py",
    "copy_working_login.py",
    "fix_auto_login_elements.py",
    # デバッグファイル
    "debug_email_fail_2.png",
]

# バックアップディレクトリ作成
backup_dir = f"backups/cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
os.makedirs(backup_dir, exist_ok=True)

print(f"\nバックアップディレクトリ: {backup_dir}")

# ファイル削除実行
deleted_count = 0
not_found_count = 0

print(f"\n削除処理:")
for file in cleanup_files:
    if os.path.exists(file):
        try:
            # 重要そうなファイルは念のためバックアップ
            if file.endswith(".py") and os.path.getsize(file) > 1000:
                shutil.copy(file, os.path.join(backup_dir, file))

            os.remove(file)
            print(f"  ✓ {file} を削除")
            deleted_count += 1
        except Exception as e:
            print(f"  ✗ {file} 削除失敗: {e}")
    else:
        not_found_count += 1

print(f"\n削除完了: {deleted_count}ファイル")
print(f"見つからず: {not_found_count}ファイル")

# __pycache__フォルダも削除
if os.path.exists("__pycache__"):
    try:
        shutil.rmtree("__pycache__")
        print("✓ __pycache__ フォルダを削除")
    except:
        print("✗ __pycache__ フォルダ削除失敗")

print("\n" + "=" * 60)
print(" 整理後のプロジェクト構造")
print("=" * 60)

print(
    """
x_automation_tool/
├── 【メイン実行ファイル】
│   ├── cli_interface.py       # メインプログラム（起動用）
│   ├── account_manager.py     # アカウント管理
│   ├── automation_executor.py # 自動操作エンジン
│   ├── cli_automation.py      # 自動操作CLI
│   ├── login_manager.py       # ログイン管理
│   └── proxy_tester.py        # プロキシテスト
│
├── 【設定・データ】
│   ├── config/
│   │   ├── accounts.csv       # アカウント情報（要作成）
│   │   └── reply_texts.csv    # リプライテキスト
│   ├── data/                  # アカウントステータス保存
│   ├── cache/cookies/         # ログインCookie保存
│   └── logs/                  # 実行ログ
│
├── 【設定ファイル】
│   ├── requirements.txt       # 必要ライブラリ
│   └── README.md             # 使用説明書
│
└── 【バックアップ】
    └── backups/              # 削除ファイルのバックアップ
"""
)

print("=" * 60)
print(" 整理完了")
print("=" * 60)

print("\n✅ 正常動作する機能:")
print("- アカウント管理（CSV一括インポート）")
print("- 初回ログイン（手動、同時実行数選択）")
print("- プロキシテスト")
print("- 自動操作（いいね、ブックマーク、リツイート、リプライ）")
print("- 並列処理（キュー方式）")

print("\n🚀 使用方法:")
print("1. py -3.10 cli_interface.py")
print("2. CSVインポート → アカウント登録")
print("3. 初回ログイン → 手動ログイン")
print("4. 自動操作実行 → 各種操作")

print(f"\n📁 バックアップ: {backup_dir}")
print("※必要に応じてバックアップから復元可能")
