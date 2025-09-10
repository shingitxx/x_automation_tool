#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
強制パッケージクリーンアップ
"""


def main():
    print("=" * 60)
    print(" 強制パッケージクリーンアップ")
    print("=" * 60)

    print("\n現在の問題:")
    print("- seleniumのMETADATAファイルが破損")
    print("- パッケージの依存関係が不整合")
    print("- 通常のアンインストールが不可能")

    print("\n解決方法:")
    print("以下のコマンドを順番に実行してください:")

    print("\n1. 強制再インストール:")
    print("   py -m pip install --force-reinstall --no-deps selenium==4.35.0")

    print("\n2. 正常なアンインストール:")
    print("   py -m pip uninstall selenium webdriver-manager -y")

    print("\n3. undetected-chromedriverのクリーンインストール:")
    print("   py -m pip uninstall undetected-chromedriver -y")
    print("   py -m pip install undetected-chromedriver")

    print("\n4. 動作確認:")
    print("   py -c \"import undetected_chromedriver as uc; print('SUCCESS')\"")

    print("\n代替方法（上記で解決しない場合）:")
    print("   手動でseleniumフォルダを削除:")
    print(
        "   C:\\Users\\nextS\\AppData\\Local\\Programs\\Python\\Python310\\Lib\\site-packages\\selenium*"
    )
    print("   （Explorerで直接削除）")

    print("\n" + "=" * 60)
    print(" パッケージ環境の修復")
    print("=" * 60)


if __name__ == "__main__":
    main()
