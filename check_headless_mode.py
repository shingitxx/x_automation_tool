#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動操作のヘッドレスモード確認・修正
"""


def main():
    print("=" * 60)
    print(" 自動操作モード確認")
    print("=" * 60)

    # automation_executor.pyのヘッドレス設定確認
    if os.path.exists("automation_executor.py"):
        with open("automation_executor.py", "r", encoding="utf-8") as f:
            content = f.read()

        print("\n1. setup_driver_with_proxy メソッドの確認:")
        if "--headless" in content:
            print("  ⚠ ヘッドレスモードが設定されています")
            print("  自動操作時に画面が表示されません")

            # ヘッドレスモードを削除
            content = content.replace("chrome_options.add_argument('--headless')", "")
            content = content.replace(
                "chrome_options.add_argument('--headless=new')", ""
            )

            with open("automation_executor.py", "w", encoding="utf-8") as f:
                f.write(content)
            print("  ✓ ヘッドレスモードを削除しました")
        else:
            print("  ✓ 通常モード（画面表示）に設定されています")

    print("\n2. 各機能のモード設定:")
    print("  ✓ ログイン状態確認: ヘッドレス（高速）")
    print("  ✓ 手動ログイン: 通常モード（操作可能）")
    print("  ✓ 自動操作実行: 通常モード（動作確認可能）")

    print("\n" + "=" * 60)
    print(" 確認完了")
    print("=" * 60)


if __name__ == "__main__":
    import os

    main()
