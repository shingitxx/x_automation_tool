#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根本的なChromeDriver問題解決
"""


def main():
    print("=" * 60)
    print(" 根本的なChromeDriver問題解決")
    print("=" * 60)

    print("\n1. 現在の状況:")
    print("   - ChromeDriver: 140版")
    print("   - Chrome実際: 139版")
    print("   - バージョンミスマッチでセッション作成失敗")

    print("\n2. 解決方法:")
    print("   正しいpipコマンド:")
    print("   py -m pip uninstall undetected-chromedriver")
    print("   py -m pip install undetected-chromedriver")

    print("\n3. 手順:")
    print("   以下のコマンドを順番に実行してください:")
    print("   ")
    print("   py -m pip uninstall undetected-chromedriver -y")
    print("   py -m pip install undetected-chromedriver")
    print("   py -m pip install --upgrade undetected-chromedriver")

    print("\n" + "=" * 60)
    print(" 実行してください")
    print("=" * 60)
    print("\n上記のコマンドを実行後、以下で再テスト:")
    print("py -3.10 cli_interface.py")


if __name__ == "__main__":
    main()
