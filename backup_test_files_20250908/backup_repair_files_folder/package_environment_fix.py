#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
パッケージ環境の修正
"""


def main():
    print("=" * 60)
    print(" パッケージ環境修正")
    print("=" * 60)

    print("\nエラー状況:")
    print("- seleniumパッケージが見つからない")
    print("- login_manager.pyでselenium.webdriverをインポートできない")
    print("- 混在したパッケージ環境")

    print("\n修正手順:")
    print("以下のコマンドを順番に実行してください:")

    print("\n1. 全てのWebDriverパッケージをアンインストール:")
    print(
        "   py -m pip uninstall selenium webdriver-manager undetected-chromedriver -y"
    )

    print("\n2. undetected-chromedriverのみ再インストール:")
    print("   py -m pip install undetected-chromedriver")

    print("\n3. 必要に応じて追加パッケージ:")
    print("   py -m pip install cryptography")

    print("\n4. インストール確認:")
    print("   py -c \"import undetected_chromedriver as uc; print('OK')\"")

    print("\n" + "=" * 60)
    print(" 実行後にテストしてください")
    print("=" * 60)
    print("\n上記コマンド実行後:")
    print("py -3.10 cli_interface.py")

    print("\n重要:")
    print("undetected-chromedriverにはseleniumが含まれているため")
    print("通常のseleniumは不要です")


if __name__ == "__main__":
    main()
