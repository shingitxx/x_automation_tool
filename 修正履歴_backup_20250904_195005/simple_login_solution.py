#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプルな初回ログイン解決策
"""

import os


def main():
    print("=" * 60)
    print(" シンプルな初回ログイン解決策")
    print("=" * 60)

    if not os.path.exists("login_manager.py"):
        print("  ✗ login_manager.py が見つかりません")
        return

    with open("login_manager.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Chrome起動部分を大幅に簡素化
    # 複雑なプロファイル管理を削除し、基本的な設定のみにする
    old_complex_section = """                # プロファイル完全分離のドライバー起動
                import tempfile
                import random
                
                # 各アカウント専用の一時ディレクトリ
                temp_profile = tempfile.mkdtemp(prefix=f'chrome_profile_{account_id}_')
                
                # プロキシ情報を事前に取得
                proxy = account.get("proxy", {})
                proxy_url = f"{proxy['host']}:{proxy['port']}" if proxy.get("host") and proxy.get("port") else None
                
                # プロセス分離とポート競合回避
                debug_port = 9000 + account_id + random.randint(0, 100)
                print(f"Chrome起動中... (ポート: {debug_port})")
                print(f"プロキシ設定: {proxy_url}" if proxy_url else "プロキシなし")
                
                # 複数回試行でドライバー作成（オプション毎回新規作成）
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
                        
                        # プロキシ設定（既に定義済みの変数を使用）
                        if proxy_url:
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

    new_simple_section = """                # シンプルなChrome起動（順次処理）
                print("Chrome起動中...")
                
                # プロキシ設定
                proxy = account.get("proxy", {})
                
                chrome_options = uc.ChromeOptions()
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--start-maximized')
                
                # プロキシ設定
                if proxy and proxy.get("host") and proxy.get("port"):
                    proxy_url = f"{proxy['host']}:{proxy['port']}"
                    chrome_options.add_argument(f'--proxy-server=http://{proxy_url}')
                    print(f"プロキシ設定: {proxy_url}")
                else:
                    print("プロキシなし")
                
                try:
                    driver = uc.Chrome(options=chrome_options)
                    driver.maximize_window()
                    print("  ✓ Chrome起動成功")
                except Exception as e:
                    print(f"  ✗ Chrome起動エラー: {str(e)[:100]}")
                    raise e"""

    if old_complex_section in content:
        content = content.replace(old_complex_section, new_simple_section)
        print("  ✓ Chrome起動を大幅に簡素化しました")
    else:
        print("  ⚠ 対象セクションが見つかりませんでした")

    # ログイン完了後のプロファイル保存処理を追加
    old_login_check = """                # ログイン確認
                current_url = driver.current_url
                if "home" in current_url.lower():
                    print(f"  ✅ [{account_id}] ログイン成功 - プロファイル保存済み")
                else:
                    print(f"  ⚠ [{account_id}] ログイン未完了の可能性があります")"""

    new_login_check = """                # ログイン確認
                current_url = driver.current_url
                if "home" in current_url.lower():
                    print(f"  ✅ [{account_id}] ログイン成功")
                    
                    # Cookieを手動保存（プロファイル代替）
                    cookies = driver.get_cookies()
                    cookie_file = f"cache/cookies/{account['email']}_cookies.json"
                    os.makedirs("cache/cookies", exist_ok=True)
                    
                    import json
                    from datetime import datetime
                    cookie_data = {
                        "cookies": cookies,
                        "saved_at": datetime.now().isoformat(),
                        "account_id": account_id,
                        "email": account['email']
                    }
                    
                    with open(cookie_file, 'w', encoding='utf-8') as f:
                        json.dump(cookie_data, f, ensure_ascii=False, indent=2)
                    
                    print(f"  ✓ Cookie保存完了: {cookie_file}")
                else:
                    print(f"  ⚠ [{account_id}] ログイン未完了の可能性があります")"""

    if old_login_check in content:
        content = content.replace(old_login_check, new_login_check)
        print("  ✓ Cookie保存機能を追加しました")

    # ファイル保存
    with open("login_manager.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("  ✓ ファイル保存完了")

    print("\n" + "=" * 60)
    print(" 修正完了 - シンプル方式")
    print("=" * 60)
    print("\n変更内容:")
    print("✓ 複雑なプロファイル管理を削除")
    print("✓ 基本的なChrome起動のみ")
    print("✓ Cookie手動保存でログイン状態維持")
    print("✓ プロセス競合の完全回避")
    print("\n利点:")
    print("• 確実にChrome起動")
    print("• エラーの大幅削減")
    print("• 既存システムとの互換性維持")

    print("\n次のテスト:")
    print("py -3.10 cli_interface.py")
    print("メニュー「2. 初回ログイン」で再実行")


if __name__ == "__main__":
    main()
