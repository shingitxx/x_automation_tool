#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromeOptions再利用エラー修正
"""

import os


def main():
    print("=" * 60)
    print(" ChromeOptions再利用エラー修正")
    print("=" * 60)

    if not os.path.exists("login_manager.py"):
        print("  ✗ login_manager.py が見つかりません")
        return

    with open("login_manager.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Chrome起動部分の修正（オプションを毎回新規作成）
    old_chrome_section = """                # 複数回試行でドライバー作成
                driver = None
                for attempt in range(3):
                    try:
                        driver = uc.Chrome(
                            options=chrome_options,
                            version_main=None,
                            driver_executable_path=None
                        )
                        driver.maximize_window()
                        print(f"  ✓ Chrome起動成功（試行{attempt+1}回目）")
                        break
                    except Exception as e:
                        print(f"  試行{attempt+1}失敗: {str(e)[:50]}")
                        if attempt < 2:  # 最後の試行でなければ待機
                            import time
                            time.sleep(2)
                            debug_port += 1  # ポートを変更してリトライ
                            chrome_options.add_argument(f'--remote-debugging-port={debug_port}')
                        else:
                            raise Exception(f"Chrome起動に3回失敗: {str(e)}")"""

    new_chrome_section = """                # 複数回試行でドライバー作成（オプション毎回新規作成）
                driver = None
                for attempt in range(3):
                    try:
                        # 試行ごとに新しいChromeOptionsを作成
                        retry_options = uc.ChromeOptions()
                        retry_options.add_argument(f'--user-data-dir={temp_profile}')
                        retry_options.add_argument(f'--profile-directory=Profile_{account_id}')
                        retry_options.add_argument(f'--remote-debugging-port={debug_port}')
                        
                        # Chrome安定化オプション
                        retry_options.add_argument('--no-sandbox')
                        retry_options.add_argument('--disable-dev-shm-usage')
                        retry_options.add_argument('--disable-gpu')
                        retry_options.add_argument('--disable-extensions')
                        retry_options.add_argument('--no-first-run')
                        retry_options.add_argument('--disable-default-apps')
                        retry_options.add_argument('--disable-background-timer-throttling')
                        retry_options.add_argument('--disable-backgrounding-occluded-windows')
                        retry_options.add_argument('--disable-renderer-backgrounding')
                        retry_options.add_argument('--disable-hang-monitor')
                        retry_options.add_argument('--disable-prompt-on-repost')
                        retry_options.add_argument('--start-maximized')
                        retry_options.add_argument('--force-device-scale-factor=1')
                        
                        # プロキシ設定
                        proxy = account.get("proxy", {})
                        if proxy and proxy.get("host") and proxy.get("port"):
                            proxy_url = f"{proxy['host']}:{proxy['port']}"
                            retry_options.add_argument(f'--proxy-server=http://{proxy_url}')
                        
                        driver = uc.Chrome(
                            options=retry_options,
                            version_main=None,
                            driver_executable_path=None
                        )
                        driver.maximize_window()
                        print(f"  ✓ Chrome起動成功（試行{attempt+1}回目）")
                        break
                    except Exception as e:
                        print(f"  試行{attempt+1}失敗: {str(e)[:50]}")
                        if attempt < 2:  # 最後の試行でなければ待機
                            import time
                            time.sleep(3)
                            debug_port += 1  # ポートを変更してリトライ
                        else:
                            raise Exception(f"Chrome起動に3回失敗: {str(e)}")"""

    if old_chrome_section in content:
        content = content.replace(old_chrome_section, new_chrome_section)
        print("  ✓ ChromeOptions再利用エラーを修正しました")
    else:
        print("  ⚠ 対象セクションが見つかりませんでした")

    # 不要になった最初のchrome_options設定部分を削除
    old_options_setup = """                chrome_options = uc.ChromeOptions()
                chrome_options.add_argument(f'--user-data-dir={temp_profile}')
                chrome_options.add_argument(f'--profile-directory=Profile_{account_id}')
                
                # プロセス分離とポート競合回避
                debug_port = 9000 + account_id + random.randint(0, 100)
                chrome_options.add_argument(f'--remote-debugging-port={debug_port}')
                
                # Chrome安定化オプション
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--disable-extensions')
                chrome_options.add_argument('--no-first-run')
                chrome_options.add_argument('--disable-default-apps')
                chrome_options.add_argument('--disable-background-timer-throttling')
                chrome_options.add_argument('--disable-backgrounding-occluded-windows')
                chrome_options.add_argument('--disable-renderer-backgrounding')
                chrome_options.add_argument('--disable-hang-monitor')
                chrome_options.add_argument('--disable-prompt-on-repost')
                chrome_options.add_argument('--start-maximized')
                chrome_options.add_argument('--force-device-scale-factor=1')
                
                # プロキシ設定
                proxy = account.get("proxy", {})
                if proxy and proxy.get("host") and proxy.get("port"):
                    proxy_url = f"{proxy['host']}:{proxy['port']}"
                    chrome_options.add_argument(f'--proxy-server=http://{proxy_url}')
                    print(f"プロキシ設定: {proxy_url}")

                print(f"Chrome起動中... (ポート: {debug_port})")"""

    new_options_setup = """                # プロセス分離とポート競合回避
                debug_port = 9000 + account_id + random.randint(0, 100)
                print(f"Chrome起動中... (ポート: {debug_port})")
                print(f"プロキシ設定: {proxy_url}" if proxy.get("host") else "プロキシなし")"""

    if old_options_setup in content:
        content = content.replace(old_options_setup, new_options_setup)
        print("  ✓ 重複するオプション設定を削除しました")

    # ファイル保存
    with open("login_manager.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("  ✓ ファイル保存完了")

    print("\n" + "=" * 60)
    print(" 修正完了")
    print("=" * 60)
    print("\n修正内容:")
    print("✓ ChromeOptions毎回新規作成")
    print("✓ オブジェクト再利用エラー解決")
    print("✓ 試行間隔を3秒に延長")
    print("✓ 重複コードの削除")

    print("\n次のテスト:")
    print("py -3.10 cli_interface.py")
    print("メニュー「2. 初回ログイン」で再実行")


if __name__ == "__main__":
    main()
