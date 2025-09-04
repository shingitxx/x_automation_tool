#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手動でseleniumパッケージを削除するガイド
"""


def main():
    print("=" * 60)
    print(" 手動selenium削除ガイド")
    print("=" * 60)

    print("\n現状: pipコマンドでは削除不可能")
    print("解決方法: 手動でフォルダを削除")

    print("\n【手順1】Explorerを開く")
    print("Windows + R → 「ファイル名を指定して実行」")
    print("以下をコピーして貼り付け:")
    print("%LOCALAPPDATA%\\Programs\\Python\\Python310\\Lib\\site-packages")

    print("\n【手順2】削除対象フォルダ")
    print("以下のフォルダとファイルを全て削除:")
    print("- selenium (フォルダ)")
    print("- selenium-4.35.0.dist-info (フォルダ)")
    print("- selenium関連の全てのファイル・フォルダ")

    print("\n【手順3】削除後の確認")
    print("コマンドプロンプトで実行:")
    print('py -c "import selenium"')
    print("→ ImportErrorが表示されればOK")

    print("\n【手順4】undetected-chromedriverの再インストール")
    print("py -m pip install undetected-chromedriver")

    print("\n【手順5】動作確認")
    print("py -c \"import undetected_chromedriver as uc; print('SUCCESS')\"")

    print("\n" + "=" * 60)
    print(" 重要な注意事項")
    print("=" * 60)
    print("- selenium関連のファイルを完全に削除してください")
    print("- 削除後は必ずコマンドプロンプトを再起動してください")
    print("- 他のPythonプロジェクトに影響する可能性があります")

    print("\n削除完了後、以下でテスト:")
    print("py -3.10 cli_interface.py")


if __name__ == "__main__":
    main()
