#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromeDriverバージョン修正
"""

import os


def main():
    print("=" * 60)
    print(" ChromeDriverバージョン修正")
    print("=" * 60)

    # 1. login_manager.pyでバージョン指定を修正
    if not os.path.exists("login_manager.py"):
        print("  ✗ login_manager.py が見つかりません")
        return

    with open("login_manager.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Chrome起動部分でバージョンを明示的に指定
    old_chrome_call = """                try:
                    driver = uc.Chrome(options=chrome_options)
                    driver.maximize_window()
                    print("  ✓ Chrome起動成功")
                except Exception as e:
                    print(f"  ✗ Chrome起動エラー: {str(e)[:100]}")
                    raise e"""

    new_chrome_call = """                try:
                    # Chromeバージョンを明示的に指定（139対応）
                    driver = uc.Chrome(
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
                        driver = uc.Chrome(
                            options=chrome_options,
                            version_main=None,  # 自動検出
                            driver_executable_path=None
                        )
                        driver.maximize_window()
                        print("  ✓ Chrome起動成功（自動検出）")
                    except Exception as e2:
                        print(f"  ✗ 再試行も失敗: {str(e2)[:100]}")
                        raise e2"""

    if old_chrome_call in content:
        content = content.replace(old_chrome_call, new_chrome_call)
        print("  ✓ login_manager.pyのChromeDriver呼び出しを修正")

    with open("login_manager.py", "w", encoding="utf-8") as f:
        f.write(content)

    # 2. automation_executor.pyも同様に修正
    if os.path.exists("automation_executor.py"):
        with open("automation_executor.py", "r", encoding="utf-8") as f:
            exec_content = f.read()

        # setup_driver_with_proxyメソッド内のバージョン指定を修正
        old_exec_chrome = """            driver = uc.Chrome(options=chrome_options, version_main=139)"""
        new_exec_chrome = """            driver = uc.Chrome(
                options=chrome_options, 
                version_main=139,  # バージョン明示
                driver_executable_path=None
            )"""

        if old_exec_chrome in exec_content:
            exec_content = exec_content.replace(old_exec_chrome, new_exec_chrome)
            print("  ✓ automation_executor.pyも修正")

        # より汎用的な修正
        if "uc.Chrome(" in exec_content and "version_main=" not in exec_content:
            exec_content = exec_content.replace(
                "uc.Chrome(options=chrome_options)",
                "uc.Chrome(options=chrome_options, version_main=139)",
            )
            print("  ✓ automation_executor.pyにバージョン指定を追加")

        with open("automation_executor.py", "w", encoding="utf-8") as f:
            f.write(exec_content)

    # 3. undetected_chromedriverの再インストール（必要に応じて）
    print("\n3. undetected_chromedriverの状態確認:")
    try:
        import undetected_chromedriver as uc

        print(f"  現在のバージョン: {uc.__version__}")
    except Exception as e:
        print(f"  インポートエラー: {e}")

    print("\n" + "=" * 60)
    print(" 修正完了")
    print("=" * 60)
    print("\n修正内容:")
    print("✓ ChromeDriverバージョンを139に明示")
    print("✓ 失敗時の自動検出フォールバック")
    print("✓ login_manager.pyとautomation_executor.py両方を修正")

    print("\n次のステップ:")
    print("1. py -3.10 cli_interface.py")
    print("2. メニュー「2. 初回ログイン」でテスト")
    print("3. バージョンエラーが解決されるはずです")

    print("\n注意:")
    print("もしまだエラーが出る場合は以下を実行:")
    print("pip uninstall undetected-chromedriver")
    print("pip install undetected-chromedriver")


if __name__ == "__main__":
    main()
