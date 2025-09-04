#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromeDriver接続エラー修正
バージョン指定を削除して自動検出に変更
"""

import os
import shutil


def main():
    print("=" * 60)
    print(" ChromeDriver接続エラー修正")
    print("=" * 60)

    if not os.path.exists("automation_executor.py"):
        print("❌ automation_executor.py が見つかりません")
        return

    # バックアップ作成
    shutil.copy("automation_executor.py", "automation_executor_before_chrome_fix.py")
    print("✓ バックアップ作成: automation_executor_before_chrome_fix.py")

    # ファイル読み込み
    with open("automation_executor.py", "r", encoding="utf-8") as f:
        content = f.read()

    # version_main=139の指定を削除
    old_chrome_call = "driver = uc.Chrome(options=chrome_options, version_main=139)"
    new_chrome_call = "driver = uc.Chrome(options=chrome_options)"

    if old_chrome_call in content:
        content = content.replace(old_chrome_call, new_chrome_call)
        print("✓ ChromeDriverのバージョン指定を削除（自動検出に変更）")
    else:
        print("- version_main指定は見つかりませんでした")

    # さらに安全なドライバー作成オプションを追加
    setup_method_pattern = """        try:
            driver = uc.Chrome(options=chrome_options)
            driver.implicitly_wait(10)
            print(f"  ✓ ドライバーを起動（アカウント: {account['email']}）")
            return driver
        except Exception as e:
            print(f"  ✗ ドライバー起動エラー: {str(e)[:100]}")
            return None"""

    new_setup_method = """        try:
            # より安全なドライバー起動
            driver = uc.Chrome(options=chrome_options)
            driver.implicitly_wait(10)
            print(f"  ✓ ドライバーを起動（アカウント: {account['email']}）")
            return driver
        except Exception as e:
            print(f"  ✗ ドライバー起動エラー: {str(e)[:100]}")
            print("  リトライを試行します...")
            
            # リトライ（オプションを簡素化）
            try:
                simple_options = uc.ChromeOptions()
                simple_options.add_argument('--no-sandbox')
                simple_options.add_argument('--disable-dev-shm-usage')
                
                driver = uc.Chrome(options=simple_options)
                driver.implicitly_wait(10)
                print(f"  ✓ リトライでドライバー起動成功")
                return driver
            except Exception as e2:
                print(f"  ✗ リトライも失敗: {str(e2)[:100]}")
                return None"""

    if setup_method_pattern in content:
        content = content.replace(setup_method_pattern, new_setup_method)
        print("✓ ドライバー起動にリトライロジックを追加")

    # ファイル更新
    with open("automation_executor.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("\n" + "=" * 60)
    print(" 修正完了")
    print("=" * 60)
    print("\n修正内容:")
    print("1. ChromeDriverのバージョン指定を削除")
    print("2. 自動バージョン検出に変更")
    print("3. 失敗時のリトライロジック追加")
    print("4. シンプルなオプションでのフォールバック")
    print("\nテスト実行:")
    print("py -3.10 cli_interface.py")
    print("メニュー「9. 自動操作実行」で再テスト")

    print("\n注意:")
    print("- Chromeブラウザが最新版であることを確認してください")
    print("- それでも接続エラーが出る場合は、Chromeを再起動してください")


if __name__ == "__main__":
    main()
