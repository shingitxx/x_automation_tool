#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手動でseleniumを削除するスクリプト
"""

import os
import shutil
import glob


def main():
    print("=" * 60)
    print(" 手動selenium削除")
    print("=" * 60)

    # パッケージディレクトリ
    packages_dir = (
        r"C:\Users\nextS\AppData\Local\Programs\Python\Python310\Lib\site-packages"
    )

    print(f"パッケージディレクトリ: {packages_dir}")

    if not os.path.exists(packages_dir):
        print("エラー: パッケージディレクトリが見つかりません")
        return

    # 削除対象を探す
    selenium_targets = []

    # seleniumフォルダ
    selenium_dir = os.path.join(packages_dir, "selenium")
    if os.path.exists(selenium_dir):
        selenium_targets.append(selenium_dir)

    # selenium-*.dist-info フォルダ
    selenium_info_pattern = os.path.join(packages_dir, "selenium-*.dist-info")
    selenium_info_dirs = glob.glob(selenium_info_pattern)
    selenium_targets.extend(selenium_info_dirs)

    # その他selenium関連
    selenium_files = glob.glob(os.path.join(packages_dir, "selenium*"))
    for file in selenium_files:
        if file not in selenium_targets:
            selenium_targets.append(file)

    print(f"\n削除対象 ({len(selenium_targets)}個):")
    for target in selenium_targets:
        print(f"  - {os.path.basename(target)}")

    if not selenium_targets:
        print("削除対象が見つかりません")
        return

    # 削除実行
    print(f"\n削除を開始します...")
    deleted_count = 0

    for target in selenium_targets:
        try:
            if os.path.isdir(target):
                shutil.rmtree(target)
                print(f"  ✓ フォルダ削除: {os.path.basename(target)}")
            else:
                os.remove(target)
                print(f"  ✓ ファイル削除: {os.path.basename(target)}")
            deleted_count += 1
        except Exception as e:
            print(f"  ✗ 削除失敗: {os.path.basename(target)} - {e}")

    print(f"\n削除完了: {deleted_count}/{len(selenium_targets)}")

    # 削除確認
    print(f"\n削除確認中...")
    try:
        import selenium

        print("  ✗ まだseleniumが残っています")
    except ImportError:
        print("  ✓ seleniumの削除完了")

    print(f"\n" + "=" * 60)
    print(" 次の手順")
    print("=" * 60)
    print("1. py -m pip install undetected-chromedriver")
    print("2. py -3.10 cli_interface.py")


if __name__ == "__main__":
    main()
