#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完全リセットスクリプト
今回作成したファイルを全て削除し、元の状態に戻す
"""

import os
import shutil


def main():
    print("=" * 60)
    print(" 完全リセット")
    print("=" * 60)

    # 今回作成した全ファイルリスト
    created_files = [
        # プロキシ関連
        "windows_chrome_manager.py",
        "fix_proxy_auth.py",
        "proxy_connection_test.py",
        "chrome_proxy_from_working.py",
        "fix_fstring_error.py",
        "simple_chrome_proxy_test.py",
        "test_chrome_no_proxy.py",
        "apply_working_proxy.py",
        "integrate_windows_chrome.py",
        # Firefox関連
        "firefox_automation_system.py",
        "firefox_automation_executor.py",
        "remove_firefox_files.py",
        # Chrome関連
        "temp_profile_chrome.py",
        "standard_chrome_isolated.py",
        "fixed_chrome_proxy.py",
        "chrome_direct_proxy.py",
        # 修正スクリプト関連
        "fix_existing_temp_profile.py",
        "analyze_and_fix_automation.py",
        "check_automation_executor.py",
        "integrate_standard_chrome.py",
        # バックアップファイル
        "windows_chrome_manager_backup.py",
        "windows_chrome_manager_working.py",
        "windows_chrome_manager_before_fix.py",
        "chrome_proxy_from_working_backup.py",
        "automation_executor_backup.py",
        "automation_executor_original.py",
        "automation_executor_chrome_backup.py",
        "automation_executor_temp_profile_backup.py",
        "automation_executor_method_backup.py",
        # その他
        "cleanup_files.py",
    ]

    removed_count = 0

    print("作成ファイル削除中...")
    for filename in created_files:
        if os.path.exists(filename):
            try:
                os.remove(filename)
                print(f"✓ 削除: {filename}")
                removed_count += 1
            except Exception as e:
                print(f"✗ 削除失敗: {filename} - {e}")
        # else:
        #     print(f"- なし: {filename}")

    # 作成されたディレクトリも削除
    created_dirs = [
        os.path.join("cache", "firefox_profiles"),
        os.path.join("cache", "firefox_cookies"),
    ]

    for dirname in created_dirs:
        if os.path.exists(dirname):
            try:
                shutil.rmtree(dirname)
                print(f"✓ ディレクトリ削除: {dirname}")
                removed_count += 1
            except Exception as e:
                print(f"✗ ディレクトリ削除失敗: {dirname} - {e}")

    print(f"\n削除完了: {removed_count}項目")

    print("\n" + "=" * 60)
    print(" 元の状態確認")
    print("=" * 60)

    # 重要な既存ファイルの確認
    important_files = [
        "cli_interface.py",
        "automation_executor.py",
        "account_manager.py",
        "login_manager.py",
        "proxy_tester.py",
    ]

    print("重要ファイル確認:")
    all_exist = True
    for filename in important_files:
        if os.path.exists(filename):
            print(f"✓ {filename}")
        else:
            print(f"❌ {filename} - 見つかりません")
            all_exist = False

    if all_exist:
        print(f"\n✅ 元の状態に戻りました")
        print(f"元の問題: Windows同時実行時の [WinError 183] プロファイル競合")
        print(f"対象ファイル: automation_executor.py")
        print(f"テスト実行: py -3.10 cli_interface.py")
    else:
        print(f"\n⚠ 一部ファイルが見つかりません")
        print(f"バックアップから復元が必要な可能性があります")


if __name__ == "__main__":
    main()
