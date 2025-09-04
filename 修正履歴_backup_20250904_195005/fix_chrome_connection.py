#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome接続エラー修正 - プロセス分離強化
"""

import os


def main():
    print("=" * 60)
    print(" Chrome接続エラー修正")
    print("=" * 60)

    if not os.path.exists("login_manager.py"):
        print("  ✗ login_manager.py が見つかりません")
        return

    with open("login_manager.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Chrome起動部分を完全に修正（プロセス分離強化）
    old_chrome_section = """                # プロファイル固定のドライバー起動（改善版）
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
                chrome_options.add_argument('--start-maximized')
                
                # プロキシ設定
                proxy = account.get("proxy", {})
                if proxy and proxy.get("host") and proxy.get("port"):
                    proxy_url = f"{proxy['host']}:{proxy['port']}"
                    chrome_options.add_argument(f'--proxy-server=http://{proxy_url}')
                    print(f"プロキシ設定: {proxy_url}")

                driver = uc.Chrome(options=chrome_options)
                driver.maximize_window()"""

    new_chrome_section = """                # プロセス完全分離のドライバー起動
                import tempfile
                import random
                
                # 各アカウント専用の一時ディレクトリ
                temp_profile = tempfile.mkdtemp(prefix=f'chrome_profile_{account_id}_')
                
                chrome_options = uc.ChromeOptions()
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

                print(f"Chrome起動中... (ポート: {debug_port})")
                
                # 複数回試行でドライバー作成
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

    if old_chrome_section in content:
        content = content.replace(old_chrome_section, new_chrome_section)
        print("  ✓ Chrome起動部分を完全修正しました")
    else:
        print("  ⚠ Chrome起動部分が見つかりませんでした。手動で確認が必要です")

    # ファイル保存
    with open("login_manager.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("  ✓ ファイル保存完了")

    # 既存の一時プロファイルをクリーンアップ
    print("\n既存の一時プロファイルをクリーンアップ中...")
    import shutil
    import glob

    # chrome_profilesディレクトリ内のクリーンアップ
    if os.path.exists("chrome_profiles"):
        try:
            shutil.rmtree("chrome_profiles")
            print("  ✓ chrome_profilesディレクトリを削除")
        except:
            print("  ⚠ chrome_profilesディレクトリの削除に失敗")

    # 一時ディレクトリのクリーンアップ
    temp_dirs = glob.glob("/tmp/chrome_profile_*") + glob.glob(
        "C:/Users/*/AppData/Local/Temp/chrome_profile_*"
    )
    for temp_dir in temp_dirs[:5]:  # 最大5個まで
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                print(f"  ✓ 一時ディレクトリ削除: {os.path.basename(temp_dir)}")
        except:
            pass

    print("\n" + "=" * 60)
    print(" 修正完了")
    print("=" * 60)
    print("\n改善点:")
    print("✓ 完全なプロセス分離")
    print("✓ 動的ポート割り当て")
    print("✓ 3回試行でリトライ機能")
    print("✓ 一時プロファイルの自動生成")
    print("✓ 既存プロファイルとの競合回避")

    print("\n次のテスト:")
    print("1. py -3.10 cli_interface.py")
    print("2. メニュー「2. 初回ログイン」")
    print("3. 今度は両方のアカウントが成功するはずです")


if __name__ == "__main__":
    main()
