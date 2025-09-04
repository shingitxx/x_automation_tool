#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
login_manager.py の webdriver_manager インポートエラー修正
"""

import os


def main():
    print("=" * 60)
    print(" webdriver_manager インポートエラー修正")
    print("=" * 60)

    if not os.path.exists("login_manager.py"):
        print("  ✗ login_manager.py が見つかりません")
        return

    with open("login_manager.py", "r", encoding="utf-8") as f:
        content = f.read()

    # webdriver_manager関連のインポートを削除
    old_imports = """from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager"""

    new_imports = """# undetected_chromedriverのみ使用"""

    if old_imports in content:
        content = content.replace(old_imports, new_imports)
        print("  ✓ webdriver_manager のインポートを削除しました")

    # 他のwebdriver_manager関連も削除
    webdriver_manager_patterns = [
        "from webdriver_manager.chrome import ChromeDriverManager",
        "from selenium.webdriver.chrome.service import Service",
        "service = Service(ChromeDriverManager().install())",
        "service=service,",
    ]

    for pattern in webdriver_manager_patterns:
        if pattern in content:
            content = content.replace(pattern, "")
            print(f"  ✓ 削除: {pattern[:50]}...")

    # Chrome起動部分でwebdriver_managerを使っている箇所を修正
    old_chrome_call = """                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=chrome_options)"""

    new_chrome_call = """                    driver = uc.Chrome(options=chrome_options, version_main=139)"""

    if old_chrome_call in content:
        content = content.replace(old_chrome_call, new_chrome_call)
        print("  ✓ Chrome起動方法をundetected版に修正しました")

    # 別パターンの修正
    patterns_to_fix = [
        (
            "webdriver.Chrome(service=Service(ChromeDriverManager().install()),",
            "uc.Chrome(",
        ),
        ("webdriver.Chrome(service=service,", "uc.Chrome("),
        ("service=Service(ChromeDriverManager().install())", "version_main=139"),
    ]

    for old, new in patterns_to_fix:
        if old in content:
            content = content.replace(old, new)
            print(f"  ✓ 修正: {old[:30]}... → {new}")

    # ファイル保存
    with open("login_manager.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("  ✓ login_manager.py修正完了")

    print("\n" + "=" * 60)
    print(" 修正完了")
    print("=" * 60)
    print("\n修正内容:")
    print("✓ webdriver_manager インポート削除")
    print("✓ Service インポート削除")
    print("✓ undetected_chromedriver のみ使用")
    print("✓ Chrome起動方法を統一")

    print("\n次のテスト:")
    print("py -3.10 cli_interface.py")


if __name__ == "__main__":
    main()
