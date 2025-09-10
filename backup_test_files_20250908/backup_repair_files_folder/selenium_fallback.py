#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通常selenium版への緊急切り替え
"""

import os


def main():
    print("=" * 60)
    print(" 緊急切り替え: 通常seleniumでの動作確認")
    print("=" * 60)

    print("undetected-chromedriverの問題により、一時的に通常のseleniumに切り替えます。")
    print("これにより動作確認が可能になります。")

    print("\n1. 必要なパッケージをインストール:")
    print("   py -m pip uninstall undetected-chromedriver -y")
    print("   py -m pip install selenium webdriver-manager")

    print("\n2. automation_executor.pyを修正します...")

    if not os.path.exists("automation_executor.py"):
        print("  ✗ automation_executor.py が見つかりません")
        return

    with open("automation_executor.py", "r", encoding="utf-8") as f:
        content = f.read()

    # undetected_chromedriverを通常のseleniumに置換
    old_imports = """import undetected_chromedriver as uc"""
    new_imports = """from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager"""

    if old_imports in content:
        content = content.replace(old_imports, new_imports)
        print("  ✓ インポートを通常seleniumに変更")

    # Chrome起動部分を修正
    old_chrome_setup = """        chrome_options = uc.ChromeOptions()"""
    new_chrome_setup = """        chrome_options = webdriver.ChromeOptions()"""

    content = content.replace(old_chrome_setup, new_chrome_setup)

    # ドライバー起動を修正
    old_driver_creation = """            driver = uc.Chrome(
                options=chrome_options, 
                version_main=139,  # バージョン明示
                driver_executable_path=None
            )"""

    new_driver_creation = """            # 自動的に適切なChromeDriverをダウンロード・使用
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)"""

    if old_driver_creation in content:
        content = content.replace(old_driver_creation, new_driver_creation)
        print("  ✓ Chrome起動方法を通常seleniumに変更")

    # より汎用的な置換
    content = content.replace(
        "uc.Chrome(",
        "webdriver.Chrome(service=Service(ChromeDriverManager().install()), ",
    )
    content = content.replace("uc.ChromeOptions()", "webdriver.ChromeOptions()")

    with open("automation_executor.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("  ✓ automation_executor.py修正完了")

    # login_manager.pyも修正
    if os.path.exists("login_manager.py"):
        with open("login_manager.py", "r", encoding="utf-8") as f:
            login_content = f.read()

        login_content = login_content.replace(old_imports, new_imports)
        login_content = login_content.replace(
            "uc.ChromeOptions()", "webdriver.ChromeOptions()"
        )
        login_content = login_content.replace(
            "uc.Chrome(",
            "webdriver.Chrome(service=Service(ChromeDriverManager().install()), ",
        )

        with open("login_manager.py", "w", encoding="utf-8") as f:
            f.write(login_content)

        print("  ✓ login_manager.py修正完了")

    print("\n" + "=" * 60)
    print(" 修正完了")
    print("=" * 60)
    print("\n変更内容:")
    print("✓ undetected-chromedriver → selenium")
    print("✓ webdriver-managerで自動ChromeDriver管理")
    print("✓ Chrome139との互換性問題回避")
    print("✓ プロファイル選択画面問題の解決")

    print("\n次の手順:")
    print("1. 上記のpipコマンドを実行")
    print("2. py -3.10 cli_interface.py")
    print("3. メニュー「9. 自動操作実行」でテスト")
    print("\n注意: 通常seleniumのため検出されやすい可能性があります")
    print("動作確認後、必要に応じてundetected版に戻すことができます")


if __name__ == "__main__":
    main()
