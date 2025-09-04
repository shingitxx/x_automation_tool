#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正版復旧スクリプト
f-stringエラーを修正して動作していた状態に復旧
"""

import os


def main():
    print("=" * 60)
    print(" 動作していた状態に復旧")
    print("=" * 60)

    # バックアップファイルの確認
    backup_files = [
        "automation_executor_backup.py",
        "automation_executor_original.py",
        "automation_executor_chrome_backup.py",
        "automation_executor_temp_profile_backup.py",
    ]

    available_backups = []
    for backup in backup_files:
        if os.path.exists(backup):
            available_backups.append(backup)
            print("✓ バックアップ発見: " + backup)

    if not available_backups:
        print("❌ 利用可能なバックアップが見つかりません")
        return

    # 最も適切なバックアップを選択
    if "automation_executor_backup.py" in available_backups:
        restore_from = "automation_executor_backup.py"
    elif "automation_executor_original.py" in available_backups:
        restore_from = "automation_executor_original.py"
    else:
        restore_from = available_backups[0]

    print("\n復旧元: " + restore_from)

    # automation_executor.pyを復旧
    try:
        import shutil

        shutil.copy(restore_from, "automation_executor.py")
        print("✅ automation_executor.py を " + restore_from + " から復旧完了")

        # 復旧後のファイル確認
        with open("automation_executor.py", "r", encoding="utf-8") as f:
            content = f.read()

        print("\n復旧ファイル確認:")
        content_size = str(len(content))
        line_count = str(len(content.split("\n")))
        print("  ファイルサイズ: " + content_size + " 文字")
        print("  行数: " + line_count + " 行")

        # 重要なクラス・メソッドの存在確認
        important_items = [
            "class AutomationExecutor",
            "def setup_driver_with_proxy",
            "def setup_driver_isolated",
            "def process_single_account",
            "def execute_parallel",
            "undetected_chromedriver",
        ]

        found_items = []
        for item in important_items:
            if item in content:
                found_items.append(item)
                print("  ✓ " + item)
            else:
                print("  - " + item)

        found_count = str(len(found_items))
        total_count = str(len(important_items))

        if len(found_items) >= 4:
            print("\n✅ 復旧成功 - 主要機能が確認できました")
            print("テスト実行: py -3.10 cli_interface.py")
        else:
            print("\n⚠ 復旧したファイルに不足があります")
            print("見つかった項目: " + found_count + "/" + total_count)

    except Exception as e:
        print("❌ 復旧失敗: " + str(e))


if __name__ == "__main__":
    main()
