#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
リプライ機能の単純テスト
"""

import time
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from account_manager import AccountManager
from automation_executor import AutomationExecutor
import json
import os


def test_reply_simple():
    print("=" * 60)
    print(" リプライ機能シンプルテスト")
    print("=" * 60)

    # 1. リプライテキストの確認
    executor = AutomationExecutor()
    csv_path = "config/reply_texts.csv"

    print("\n1. リプライテキスト読み込みテスト")
    if os.path.exists(csv_path):
        success = executor.load_reply_texts(csv_path)
        print(f"   読み込み結果: {success}")
        print(f"   テキスト数: {len(executor.reply_texts)}")
        if executor.reply_texts:
            print(f"   サンプル: {executor.reply_texts[0]}")
    else:
        print(f"   ✗ ファイルが存在しません: {csv_path}")
        return

    # 2. ランダムテキスト取得テスト
    print("\n2. ランダムテキスト取得テスト")
    text = executor.get_random_reply()
    print(f"   取得結果: {text}")

    if not text:
        print("   ✗ テキストが取得できません")
        return

    # 3. ブラウザでリプライテスト
    print("\n3. ブラウザでリプライ実行テスト")

    manager = AccountManager()
    account = manager.get_account_by_id(1)

    if not account:
        print("   ✗ アカウントが見つかりません")
        return

    # ドライバー起動
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(options=options, version_main=139)

    try:
        # Cookie読み込み
        cookie_file = os.path.join("cache/cookies", f"{account['email']}_cookies.json")
        if os.path.exists(cookie_file):
            with open(cookie_file, "r", encoding="utf-8") as f:
                cookie_data = json.load(f)

            driver.get("https://x.com")
            time.sleep(3)

            for cookie in cookie_data.get("cookies", []):
                try:
                    driver.add_cookie(cookie)
                except:
                    pass

            driver.refresh()
            time.sleep(3)
            print("   ✓ ログイン完了")

        # テストURL
        test_url = input("\nテストするツイートURLを入力: ")

        # リプライ実行
        print(f"\n   リプライテキスト: {text}")
        result = executor.execute_reply(driver, test_url, text)
        print(f"   実行結果: {result}")

        if result:
            print("\n   ✅ リプライ成功！")
        else:
            print("\n   ❌ リプライ失敗")

        input("\nEnterキーを押してブラウザを閉じる...")

    finally:
        driver.quit()


if __name__ == "__main__":
    test_reply_simple()
