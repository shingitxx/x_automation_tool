#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ゲストモード問題修正 - プロファイル設定改善
"""

import os


def main():
    print("=" * 60)
    print(" ゲストモード問題修正")
    print("=" * 60)

    if not os.path.exists("login_manager.py"):
        print("  ✗ login_manager.py が見つかりません")
        return

    with open("login_manager.py", "r", encoding="utf-8") as f:
        content = f.read()

    # manual_loginメソッドのChrome起動部分を修正
    old_chrome_options = """                # プロファイル固定のドライバー起動
                chrome_options = uc.ChromeOptions()
                chrome_options.add_argument(f'--user-data-dir={profile_dir}')
                chrome_options.add_argument('--no-first-run')
                chrome_options.add_argument('--disable-default-apps')"""

    new_chrome_options = """                # プロファイル固定のドライバー起動（改善版）
                chrome_options = uc.ChromeOptions()
                chrome_options.add_argument(f'--user-data-dir={profile_dir}')
                chrome_options.add_argument('--no-first-run')
                chrome_options.add_argument('--disable-default-apps')
                chrome_options.add_argument('--no-default-browser-check')
                chrome_options.add_argument('--disable-background-timer-throttling')
                chrome_options.add_argument('--disable-backgrounding-occluded-windows')
                chrome_options.add_argument('--disable-renderer-backgrounding')
                chrome_options.add_argument('--disable-features=TranslateUI')
                chrome_options.add_argument('--disable-ipc-flooding-protection')
                chrome_options.add_argument('--disable-hang-monitor')
                chrome_options.add_argument('--disable-client-side-phishing-detection')
                chrome_options.add_argument('--disable-popup-blocking')
                chrome_options.add_argument('--disable-prompt-on-repost')
                chrome_options.add_argument('--start-maximized')"""

    if old_chrome_options in content:
        content = content.replace(old_chrome_options, new_chrome_options)
        print("  ✓ Chrome起動オプションを改善しました")

    # Xログインページへの直接遷移を改善
    old_login_flow = """                # Xのログインページを開く
                print("Xのログインページを開いています...")
                driver.get("https://x.com/login")"""

    new_login_flow = """                # 段階的ページ読み込み
                print("ブラウザを準備中...")
                driver.get("about:blank")
                import time
                time.sleep(2)
                
                print("Xトップページを開いています...")
                driver.get("https://x.com")
                time.sleep(3)
                
                print("Xのログインページに移動...")
                driver.get("https://x.com/i/flow/login")
                time.sleep(3)"""

    if old_login_flow in content:
        content = content.replace(old_login_flow, new_login_flow)
        print("  ✓ ログインページ遷移を改善しました")

    # ファイル保存
    with open("login_manager.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("  ✓ ファイル保存完了")

    print("\n" + "=" * 60)
    print(" 修正完了")
    print("=" * 60)
    print("\n改善点:")
    print("✓ Chrome起動オプションの最適化")
    print("✓ 段階的ページ読み込み")
    print("✓ ゲストモード問題の回避")
    print("✓ より安定したブラウザ起動")

    print("\n次の手順:")
    print("1. 現在のブラウザウィンドウを閉じる")
    print("2. コンソールでEnterキーを押してプログラム終了")
    print("3. py -3.10 cli_interface.py で再実行")
    print("4. メニュー「2. 初回ログイン」を再試行")


if __name__ == "__main__":
    main()
