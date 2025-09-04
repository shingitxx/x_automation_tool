#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
selenium切り替え時の残存エラー修正
"""

import os


def main():
    print("=" * 60)
    print(" selenium切り替えの残存エラー修正")
    print("=" * 60)

    # automation_executor.pyの完全修正
    if not os.path.exists("automation_executor.py"):
        print("  ✗ automation_executor.py が見つかりません")
        return

    with open("automation_executor.py", "r", encoding="utf-8") as f:
        content = f.read()

    print("  古いundetected-chromedriver関連コードを検索・修正中...")

    # version_mainパラメータを完全削除
    old_patterns = [
        "version_main=139,",
        "version_main=None,",
        "version_main=139",
        "version_main=None",
        "driver_executable_path=None,",
        "driver_executable_path=None",
    ]

    for pattern in old_patterns:
        if pattern in content:
            content = content.replace(pattern, "")
            print(f"  ✓ 削除: {pattern}")

    # WebDriverの呼び出しを統一
    import re

    # パターン1: 複数行にわたるWebDriver呼び出し
    pattern1 = re.compile(
        r"webdriver\.Chrome\(\s*service=Service\(ChromeDriverManager\(\)\.install\(\)\),\s*options=chrome_options,?\s*\)",
        re.MULTILINE | re.DOTALL,
    )
    content = pattern1.sub(
        "webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)",
        content,
    )

    # パターン2: 残存するversion_mainやdriver_executable_pathを含む呼び出し
    pattern2 = re.compile(
        r"webdriver\.Chrome\([^)]*version_main[^)]*\)", re.MULTILINE | re.DOTALL
    )
    content = pattern2.sub(
        "webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)",
        content,
    )

    # setup_driver_with_proxyメソッドを完全に書き換え
    setup_method_pattern = r"def setup_driver_with_proxy\(self, account_id: int\) -> Optional\[webdriver\.Chrome\]:(.*?)(?=def|\Z)"

    new_setup_method = '''def setup_driver_with_proxy(self, account_id: int) -> Optional[webdriver.Chrome]:
        """プロキシ設定付きドライバー（通常selenium版）"""
        account = self.account_manager.get_account_by_id(account_id)
        if not account:
            return None
        
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        
        # プロキシ設定
        proxy = account.get("proxy", {})
        if proxy and proxy.get("host") and proxy.get("port"):
            proxy_url = f"{proxy['host']}:{proxy['port']}"
            chrome_options.add_argument(f'--proxy-server=http://{proxy_url}')
            print(f"  プロキシ設定: {proxy_url}")

        try:
            # webdriver-managerで自動的に適切なChromeDriverを取得
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.implicitly_wait(10)
            print(f"  ✓ ドライバー起動成功（アカウント: {account['email']}）")
            return driver
        except Exception as e:
            print(f"  ✗ ドライバー起動エラー: {str(e)[:100]}")
            return None

    '''

    match = re.search(setup_method_pattern, content, re.DOTALL)
    if match:
        content = content.replace(match.group(0), new_setup_method.strip())
        print("  ✓ setup_driver_with_proxyメソッドを完全に書き換えました")

    # ファイル保存
    with open("automation_executor.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("  ✓ automation_executor.py修正完了")

    # login_manager.pyも同様に修正
    if os.path.exists("login_manager.py"):
        with open("login_manager.py", "r", encoding="utf-8") as f:
            login_content = f.read()

        # 同じパターンで修正
        for pattern in old_patterns:
            if pattern in login_content:
                login_content = login_content.replace(pattern, "")

        # Chrome起動部分を修正
        old_login_chrome = """                try:
                    # Chromeバージョンを明示的に指定（139対応）
                    driver = webdriver.Chrome(
                        options=chrome_options,
                        version_main=139,  # 現在のChromeバージョンに合わせる
                        driver_executable_path=None
                    )
                    driver.maximize_window()
                    print("  ✓ Chrome起動成功")
                except Exception as e:
                    print(f"  ✗ Chrome起動エラー: {str(e)[:100]}")
                    # バージョン自動検出で再試行
                    try:
                        print("  バージョン自動検出で再試行中...")
                        driver = webdriver.Chrome(
                            options=chrome_options,
                            version_main=None,  # 自動検出
                            driver_executable_path=None
                        )
                        driver.maximize_window()
                        print("  ✓ Chrome起動成功（自動検出）")
                    except Exception as e2:
                        print(f"  ✗ 再試行も失敗: {str(e2)[:100]}")
                        raise e2"""

        new_login_chrome = """                try:
                    # webdriver-managerで自動ChromeDriver管理
                    from webdriver_manager.chrome import ChromeDriverManager
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    driver.maximize_window()
                    print("  ✓ Chrome起動成功")
                except Exception as e:
                    print(f"  ✗ Chrome起動エラー: {str(e)[:100]}")
                    raise e"""

        if old_login_chrome in login_content:
            login_content = login_content.replace(old_login_chrome, new_login_chrome)

        with open("login_manager.py", "w", encoding="utf-8") as f:
            f.write(login_content)

        print("  ✓ login_manager.py修正完了")

    print("\n" + "=" * 60)
    print(" 修正完了")
    print("=" * 60)
    print("\n修正内容:")
    print("✓ version_mainパラメータ完全削除")
    print("✓ driver_executable_pathパラメータ削除")
    print("✓ webdriver-manager統一使用")
    print("✓ 通常seleniumに完全対応")

    print("\n次のテスト:")
    print("py -3.10 cli_interface.py")
    print("メニュー「9. 自動操作実行」でテスト")


if __name__ == "__main__":
    main()
